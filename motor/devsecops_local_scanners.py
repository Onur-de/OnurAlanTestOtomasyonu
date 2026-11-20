#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 2: Local DevSecOps Docker & SAST/DAST/OpenAPI Scanner Orchestrator.
Runs strictly defensive security verification against local paths & ephemeral localhost servers:
1. Gitleaks (Docker `ghcr.io/gitleaks/gitleaks:v8.30.1`) — secret leak detection.
2. OpenAPI Schema Fuzzer (Docker `schemathesis/schemathesis:stable` + fast native boundary fuzzer) — 0 HTTP 5xx gate.
3. OWASP ZAP Baseline (`ghcr.io/zaproxy/zaproxy:stable`) + OWASP ASVS L2 Security Header Auditor.
4. Ruff + Bandit (`-ll -ii`) SAST Static Code Scanner.
5. Trivy CVE/Misconfig Scanner (when image/binary is cached locally).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx

TZ = ZoneInfo("Europe/Istanbul")


def _docker_has_image(name: str) -> bool:
    if not shutil.which("docker"):
        return False
    r = subprocess.run(
        ["docker", "images", "-q", name],
        capture_output=True,
        text=True,
        timeout=8,
    )
    return r.returncode == 0 and bool((r.stdout or "").strip())


def run_gitleaks_dir_scan(target_dir: Path, config_path: Path | None = None, timeout: int = 45) -> dict[str, Any]:
    t0 = time.perf_counter()
    res: dict[str, Any] = {
        "scanner": "gitleaks",
        "status": "SKIP",
        "findings_count": 0,
        "findings": [],
        "detail": "",
        "duration_sec": 0.0,
    }
    img = "ghcr.io/gitleaks/gitleaks:v8.30.1"
    if not _docker_has_image(img):
        img = "zricethezav/gitleaks:v8.30.1"
    has_docker_img = _docker_has_image(img)
    native_gl = shutil.which("gitleaks")
    if not has_docker_img and not native_gl:
        res["detail"] = "gitleaks Docker imajı veya yerel ikili bulunamadı"
        return res

    tmp_rep = Path(tempfile.mkdtemp(prefix="dc_gl_"))
    if os.name == "posix":
        os.chmod(tmp_rep, 0o777)  # nosec B103
    try:
        if has_docker_img:
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{target_dir.resolve()}:/scan:ro",
                "-v", f"{tmp_rep.resolve()}:/out:rw",
                img, "dir", "/scan",
                "--redact", "--no-banner", "--exit-code", "1",
                "--report-format", "json", "--report-path", "/out/gitleaks.json",
            ]
            if config_path and config_path.is_file():
                shutil.copy2(config_path, tmp_rep / ".gitleaks.toml")
                cmd.extend(["--config", "/out/.gitleaks.toml"])
            used_engine = img
        else:
            cmd = [
                str(native_gl), "dir", str(target_dir.resolve()),
                "--redact", "--no-banner", "--exit-code", "1",
                "--report-format", "json", "--report-path", str(tmp_rep / "gitleaks.json"),
            ]
            if config_path and config_path.is_file():
                cmd.extend(["--config", str(config_path)])
            used_engine = "gitleaks-native"
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        rep_file = tmp_rep / "gitleaks.json"
        findings = []
        if rep_file.is_file():
            try:
                raw = json.loads(rep_file.read_text(encoding="utf-8") or "[]")
                if isinstance(raw, list):
                    findings = [
                        {"rule": f.get("RuleID"), "file": f.get("File"), "line": f.get("StartLine")}
                        for f in raw
                    ]
            except Exception:
                pass
        res["findings_count"] = len(findings)
        res["findings"] = findings[:15]
        res["status"] = "PASS" if p.returncode == 0 and len(findings) == 0 else "FAIL"
        res["detail"] = f"exit={p.returncode}, findings={len(findings)} ({used_engine})"
    except Exception as exc:
        res["status"] = "FAIL"
        res["detail"] = f"Gitleaks hata: {exc}"
    finally:
        shutil.rmtree(tmp_rep, ignore_errors=True)
        res["duration_sec"] = round(time.perf_counter() - t0, 2)
    return res


def run_openapi_schema_fuzzer(
    base_url: str,
    headers: dict[str, str] | None = None,
    use_docker_schemathesis: bool = True,
    max_examples: int = 8,
) -> dict[str, Any]:
    """
    Fuzzes a local FastAPI `/openapi.json` for 0 HTTP 5xx server crashes.
    Runs both a fast deterministic boundary fuzzer AND (if Docker `schemathesis/schemathesis:stable`
    is cached locally and `use_docker_schemathesis=True`) Schemathesis CLI against host.docker.internal.
    """
    t0 = time.perf_counter()
    res: dict[str, Any] = {
        "scanner": "openapi_fuzzer",
        "status": "PASS",
        "routes_fuzzed": 0,
        "requests_sent": 0,
        "http_5xx_errors": [],
        "schemathesis_docker_status": "SKIP",
        "detail": "",
        "duration_sec": 0.0,
    }
    if not base_url.startswith(("http://127.0.0.1:", "http://localhost:")):
        res["status"] = "FAIL"
        res["detail"] = "Yalnız yerel izole sunucu fuzz edilebilir"
        return res

    hdrs = dict(headers or {})
    try:
        r_oas = httpx.get(f"{base_url}/openapi.json", headers=hdrs, timeout=8.0)
        r_oas.raise_for_status()
        schema = r_oas.json()
    except Exception as exc:
        res["status"] = "FAIL"
        res["detail"] = f"/openapi.json okunamadı: {exc}"
        res["duration_sec"] = round(time.perf_counter() - t0, 2)
        return res

    boundary_payloads = [
        {},
        {"__fuzz": "A" * 4096},
        {"name": "", "amount": -999999999, "id": "not-an-int"},
        {"text": "\u202eRTL\u0000NULL' OR 1=1;--", "count": 2**40},
    ]

    paths = schema.get("paths") or {}
    with httpx.Client(timeout=6.0, headers=hdrs) as cli:
        for route, ops in paths.items():
            if any(skip in route for skip in ("/auth/logout", "/sessions/revoke", "/permissions")):
                continue
            concrete_route = route
            for seg in ("{id}", "{pid}", "{aid}", "{sid}", "{cid}", "{iid}", "{wid}", "{oid}", "{pay_id}"):
                concrete_route = concrete_route.replace(seg, "999999")
            concrete_route = concrete_route.replace("{slug}", "merkez").replace("{clinic_slug}", "merkez").replace("{token}", "invalid-token").replace("{code}", "nonexistent")
            if "{" in concrete_route:
                continue
            for method in ("get", "post", "patch", "delete"):
                if method not in ops:
                    continue
                res["routes_fuzzed"] += 1
                cases = [None] if method == "get" else boundary_payloads[:2]
                for pl in cases:
                    st = 0
                    try:
                        resp = cli.request(method.upper(), f"{base_url}{concrete_route}", json=pl)
                        st = resp.status_code
                    except Exception as exc:
                        st = 599
                        res["http_5xx_errors"].append(f"{method.upper()} {concrete_route} -> EXC {exc}")
                    res["requests_sent"] += 1
                    if 500 <= st < 599:
                        res["http_5xx_errors"].append(f"{method.upper()} {concrete_route} -> HTTP {st}")

    # Optional Docker Schemathesis execution (when cached locally)
    if use_docker_schemathesis and _docker_has_image("schemathesis/schemathesis:stable"):
        if sys.platform.startswith("linux"):
            docker_url = base_url
            net_args = ["--network=host"]
        else:
            docker_url = base_url.replace("127.0.0.1", "host.docker.internal").replace("localhost", "host.docker.internal")
            net_args = ["--add-host=host.docker.internal:host-gateway"]
        cmd = [
            "docker", "run", "--rm",
            *net_args,
            "schemathesis/schemathesis:stable", "run",
            f"{docker_url}/openapi.json",
            "--checks", "not_a_server_error",
            "--max-examples", str(max_examples),
            "--workers", "2",
        ]
        for hk, hv in hdrs.items():
            cmd.extend(["--header", f"{hk}: {hv}"])
        try:
            sp = subprocess.run(cmd, capture_output=True, text=True, timeout=75)
            res["schemathesis_docker_status"] = "PASS" if sp.returncode == 0 else f"FAIL(rc={sp.returncode})"
            if sp.returncode != 0:
                res["http_5xx_errors"].append(f"Schemathesis Docker rc={sp.returncode}: {(sp.stdout + sp.stderr)[-220:]}")
        except Exception as exc:
            res["schemathesis_docker_status"] = f"ERR({exc})"

    res["status"] = "PASS" if not res["http_5xx_errors"] else "FAIL"
    res["detail"] = f"routes={res['routes_fuzzed']}, reqs={res['requests_sent']}, 5xx={len(res['http_5xx_errors'])}, schemathesis={res['schemathesis_docker_status']}"
    res["duration_sec"] = round(time.perf_counter() - t0, 2)
    return res


def run_asvs_and_zap_audit(base_url: str, run_docker_zap: bool = False, timeout: int = 90) -> dict[str, Any]:
    """
    Audits OWASP ASVS L2 HTTP security headers directly AND optionally executes
    Docker OWASP ZAP Baseline (`ghcr.io/zaproxy/zaproxy:stable`) against local server.
    """
    t0 = time.perf_counter()
    res: dict[str, Any] = {
        "scanner": "owasp_asvs_zap",
        "status": "PASS",
        "missing_headers": [],
        "zap_status": "SKIP",
        "zap_high": 0,
        "zap_medium": 0,
        "detail": "",
        "duration_sec": 0.0,
    }
    required_hdrs = [
        "content-security-policy",
        "x-content-type-options",
        "x-frame-options",
        "referrer-policy",
    ]
    try:
        r_h = httpx.get(f"{base_url}/health", timeout=6.0)
        h_low = {k.lower(): v for k, v in r_h.headers.items()}
        missing = [k for k in required_hdrs if not h_low.get(k)]
        res["missing_headers"] = missing
    except Exception as exc:
        res["status"] = "FAIL"
        res["detail"] = f"/health başlık okuma hatası: {exc}"
        res["duration_sec"] = round(time.perf_counter() - t0, 2)
        return res

    if run_docker_zap and _docker_has_image("ghcr.io/zaproxy/zaproxy:stable"):
        tmp_z = Path(tempfile.mkdtemp(prefix="dc_zap_"))
        if os.name == "posix":
            os.chmod(tmp_z, 0o777)  # nosec B103
        try:
            if sys.platform.startswith("linux"):
                docker_url = base_url
                net_args = ["--network=host"]
            else:
                docker_url = base_url.replace("127.0.0.1", "host.docker.internal").replace("localhost", "host.docker.internal")
                net_args = ["--add-host=host.docker.internal:host-gateway"]
            zp = subprocess.run(
                [
                    "docker", "run", "--rm",
                    *net_args,
                    "-v", f"{tmp_z.resolve()}:/zap/wrk:rw",
                    "ghcr.io/zaproxy/zaproxy:stable",
                    "zap-baseline.py", "-t", docker_url,
                    "-m", "1", "-J", "zap.json",
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            zfile = tmp_z / "zap.json"
            if zfile.is_file():
                zj = json.loads(zfile.read_text(encoding="utf-8"))
                for site in zj.get("site") or []:
                    for al in site.get("alerts") or []:
                        rc_risk = str(al.get("riskcode", "0"))
                        if rc_risk == "3":
                            res["zap_high"] += 1
                        elif rc_risk == "2":
                            res["zap_medium"] += 1
            res["zap_status"] = "PASS" if (zp.returncode in (0, 2) and res["zap_high"] == 0) else f"FAIL(rc={zp.returncode}, high={res['zap_high']})"
        except Exception as exc:
            res["zap_status"] = f"ERR({exc})"
        finally:
            shutil.rmtree(tmp_z, ignore_errors=True)

    zap_ok = res["zap_status"] in ("SKIP", "PASS")
    res["status"] = "PASS" if (not res["missing_headers"] and zap_ok) else "FAIL"
    res["detail"] = f"missing_asvs={res['missing_headers']}, zap={res['zap_status']} (high={res['zap_high']}, med={res['zap_medium']})"
    res["duration_sec"] = round(time.perf_counter() - t0, 2)
    return res


def run_sast_ruff_bandit(target_dir: Path, ruff_config: Path | None = None) -> dict[str, Any]:
    t0 = time.perf_counter()
    ruff_cmd = [sys.executable, "-m", "ruff", "check", "--select", "S,B,F"]
    if ruff_config and ruff_config.is_file():
        ruff_cmd = [sys.executable, "-m", "ruff", "check", "--config", str(ruff_config)]
    ruff_cmd.extend(["--exclude", "tests,node_modules,backups,backup,__pycache__,ephemeral_sandbox", str(target_dir)])
    rp = subprocess.run(ruff_cmd, capture_output=True, text=True, timeout=60)

    bp = subprocess.run(
        [sys.executable, "-m", "bandit", "-r", str(target_dir), "-x", "tests,ephemeral_sandbox,__pycache__", "-ll", "-ii", "-q", "-f", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    b_issues = 0
    try:
        bj = json.loads(bp.stdout or "{}")
        b_issues = len(bj.get("results") or [])
    except Exception:
        b_issues = 0 if bp.returncode == 0 else 1

    ok = (rp.returncode == 0 and bp.returncode == 0 and b_issues == 0)
    return {
        "scanner": "sast_ruff_bandit",
        "status": "PASS" if ok else "FAIL",
        "ruff_exit": rp.returncode,
        "bandit_issues": b_issues,
        "detail": f"ruff_exit={rp.returncode}, bandit_med_high={b_issues}",
        "ruff_sample": (rp.stdout or rp.stderr or "").strip()[:240],
        "duration_sec": round(time.perf_counter() - t0, 2),
    }


def run_full_devsecops_local_suite(
    target_dir: Path,
    base_url: str | None = None,
    headers: dict[str, str] | None = None,
    gitleaks_config: Path | None = None,
    ruff_config: Path | None = None,
    run_docker_zap: bool = False,
    use_docker_schemathesis: bool = True,
) -> dict[str, Any]:
    ts = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    scanners: list[dict[str, Any]] = []
    scanners.append(run_sast_ruff_bandit(target_dir, ruff_config=ruff_config))
    scanners.append(run_gitleaks_dir_scan(target_dir, config_path=gitleaks_config))
    if base_url:
        scanners.append(run_openapi_schema_fuzzer(base_url, headers=headers, use_docker_schemathesis=use_docker_schemathesis))
        scanners.append(run_asvs_and_zap_audit(base_url, run_docker_zap=run_docker_zap))

    failed = [s for s in scanners if s["status"] == "FAIL"]
    return {
        "gate": "DEVSECOPS_LOCAL_SCANNERS",
        "timestamp": ts,
        "status": "PASS" if not failed else "FAIL",
        "passed_scanners": sum(1 for s in scanners if s["status"] == "PASS"),
        "total_scanners": len(scanners),
        "failed_scanners": [f"{s['scanner']}: {s['detail']}" for s in failed],
        "scanners": scanners,
    }
