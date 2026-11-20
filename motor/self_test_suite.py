#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SELF-TEST SUITE FOR `test otomasyonu` ITSELF (ZERO TOUCHES TO EXTERNAL PROJECTS!).
Tests EVERY SINGLE ONE of the 5 newly added Enterprise QA capabilities strictly against
`test otomasyonu`'s own ephemeral mock FastAPI server and temp directories:
  1. Self-Code Hygiene: py_compile + Ruff (S,B,F) + Bandit (-ll -ii) on `test otomasyonu/motor/*.py`
  2. Module 1 (Docker PostgreSQL): Real `postgres:17` ephemeral container, DDL, 10-way ACID conflict race, rollback
  3. Module 2 (Local DevSecOps Docker Scanners):
     - Real Docker Gitleaks: verifies 0 findings on clean dir AND verifies it ACTUALLY CATCHES a planted fake secret!
     - Real Docker Schemathesis + Native OpenAPI Fuzzer: verifies 0 5xx on clean mock app AND verifies it CATCHES a deliberate 500 route!
     - Real Docker OWASP ZAP Baseline + ASVS L2 Security Header check against mock FastAPI server!
  4. Module 3 (Live L3 LLM Red-Team): Real OmniRoute (`127.0.0.1:20128/v1`) live clinical probes + verifies evaluator CATCHES a synthetic "500 mg" leak!
  5. Module 4 (Real k6 Soak + psutil RAM/Handle Leak): Real `k6.exe` (15 VUs x 8s) against mock server + live PID RSS/handle/CPU profiling!
  6. Module 5 (Unified Control Center + UI Gate): Builds `BIRLESIK_KOMUTA_MERKEZI.html` (local-only), runs `sloplint.mjs` (0 FAIL) & Playwright `1440x900` & `390x844` (0 errors, 0px overflow)!
"""
from __future__ import annotations

import argparse
import os
import py_compile
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx

HERE = Path(__file__).resolve().parent
AUTO_ROOT = HERE.parent
DATA_DIR = AUTO_ROOT / "veri"
TZ = ZoneInfo("Europe/Istanbul")

sys.path.insert(0, str(HERE))
from pg_docker_engine import run_docker_postgres_verification  # noqa: E402
from devsecops_local_scanners import (  # noqa: E402
    run_asvs_and_zap_audit,
    run_gitleaks_dir_scan,
    run_openapi_schema_fuzzer,
    run_sast_ruff_bandit,
)
from live_llm_redteam import (  # noqa: E402
    evaluate_live_llm_response,
    run_ci_l3_guardrail_suite,
    run_live_l3_llm_redteam,
)
from k6_soak_memory_engine import run_k6_soak_and_memory_audit  # noqa: E402
from unified_control_center import (  # noqa: E402
    append_enterprise_gate_record,
    build_unified_control_center,
    safe_sync_to_mirror,
)

MOCK_FASTAPI_CODE = '''
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field
import uvicorn, sys

app = FastAPI(title="TestOtomasyonu SelfTest Mock API", version="1.0.0")

@app.middleware("http")
async def add_security_headers(request, call_next):
    resp = await call_next(request)
    resp.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    resp.headers["X-Request-ID"] = "selftest-req-1"
    return resp

class ItemIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    amount: int = Field(..., gt=0, lt=1000000)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/items")
def list_items(q: str = ""):
    return {"items": [{"id": 1, "name": "Demo"}], "q": q[:40]}

@app.post("/items")
def create_item(item: ItemIn):
    return {"ok": True, "name": item.name, "amount": item.amount}

if __name__ == "__main__":
    port = int(sys.argv[1])
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")
'''

FAULTY_MOCK_CODE = '''
from fastapi import FastAPI
import uvicorn, sys

app = FastAPI(title="Faulty Probe API")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/boom")
def boom():
    raise RuntimeError("Deliberate self-test 500 bug")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=int(sys.argv[1]), log_level="error")
'''


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_health(url: str, timeout: float = 20.0) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if httpx.get(f"{url}/health", timeout=2.0).status_code == 200:
                return True
        except Exception:
            time.sleep(0.25)
    return False


def _builtin_html_quality_lint(html_path: Path) -> list[str]:
    """Cross-platform HTML/CSS anti-slop gate used on Cloud CI when sloplint.mjs is not present."""
    txt = html_path.read_text(encoding="utf-8", errors="ignore")
    errs: list[str] = []
    if 'name="viewport"' not in txt:
        errs.append("missing viewport meta")
    if "overflow-x: clip" not in txt:
        errs.append("missing overflow-x: clip")
    if ":focus-visible" not in txt:
        errs.append("missing :focus-visible")
    if "prefers-reduced-motion" not in txt:
        errs.append("missing prefers-reduced-motion")
    if "100vw" in txt:
        errs.append("forbidden 100vw width")
    if re.search(r"transition\s*:\s*all\b", txt):
        errs.append("forbidden transition: all")
    return errs


def run_all_self_tests(ci_fast: bool = False, with_zap: bool = False) -> int:
    is_cloud = ci_fast or (os.environ.get("GITHUB_ACTIONS", "").lower() == "true")
    runner_label = "github-actions-ubuntu-24.04" if is_cloud else "local-windows"
    mode_tag = "BULUT CI HIZLI MOD" if ci_fast else "TAM YEREL MOD"
    print("=========================================================================")
    print(f"TEST OTOMASYONU KENDİ KENDİNİ DOĞRULAMA PAKETİ ({mode_tag})")
    print("=========================================================================")
    checks: list[tuple[str, bool, str]] = []

    def rec(name: str, ok: bool, detail: str):
        checks.append((name, ok, detail))
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name} -> {detail}")

    def _save_gate(record: dict) -> None:
        record["runner"] = runner_label
        append_enterprise_gate_record(record, cloud=is_cloud)

    # 1. Self-Code Syntax + SAST (py_compile + Ruff + Bandit on `test otomasyonu/motor/*.py`)
    py_files = [p for p in HERE.glob("*.py")]
    comp_errs = []
    for pf in py_files:
        try:
            py_compile.compile(str(pf), doraise=True)
        except Exception as exc:
            comp_errs.append(f"{pf.name}: {exc}")
    rec("1A. Motor Python Sözdizimi (py_compile)", not comp_errs, f"{len(py_files)} dosya derlendi, hata={len(comp_errs)}")

    sast_self = run_sast_ruff_bandit(HERE)
    rec(
        "1B. Motor Öz-SAST (Ruff S,B,F + Bandit -ll -ii)",
        sast_self["status"] == "PASS",
        f"ruff_exit={sast_self['ruff_exit']}, bandit_med_high={sast_self['bandit_issues']}",
    )

    # 2. Module 1: Live Docker PostgreSQL (`postgres:17` / `postgres:17-alpine`) Self-Test
    pg_res = run_docker_postgres_verification(self_test_mode=True)
    _save_gate(pg_res)
    rec(
        "2. Modül 1: Canlı Docker PostgreSQL 17 (DDL + 10 Paralel ACID Kilit + Rollback)",
        pg_res["status"] == "PASS",
        f"image={pg_res['image']}, tables={pg_res['tables_created']}, ACID={pg_res['acid_race_commits']}/{pg_res['acid_race_conflicts']}, {pg_res['duration_sec']}s",
    )

    # Start ephemeral self-test Mock FastAPI Server
    tmp_mock = Path(tempfile.mkdtemp(prefix="dc_selftest_mock_"))
    mock_py = tmp_mock / "mock_app.py"
    mock_py.write_text(MOCK_FASTAPI_CODE, encoding="utf-8")
    mock_port = _free_port()
    mock_url = f"http://127.0.0.1:{mock_port}"
    mock_proc = subprocess.Popen(  # noqa: S603
        [sys.executable, "-X", "utf8", str(mock_py), str(mock_port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        mock_up = _wait_health(mock_url)
        rec("3A. İzole Öz-Test Mock FastAPI Sunucusu", mock_up, f"{mock_url} (PID={mock_proc.pid})")
        if not mock_up:
            return 1

        # 3B. Module 2: Docker Gitleaks — BOTH Clean Dir PASS & Planted Secret FAIL Detection Proof!
        clean_dir = tmp_mock / "gl_clean"
        dirty_dir = tmp_mock / "gl_dirty"
        clean_dir.mkdir()
        dirty_dir.mkdir()
        (clean_dir / "safe.py").write_text("x = 42\nprint('hello')\n", encoding="utf-8")
        # Build synthetic dummy secret patterns at runtime (zero static literal tokens in source)
        fake_aws = "AKIA" + "IOSFODNN7" + "EXAMPLE"
        fake_gh = "ghp" + "_" + ("1234567890abcdef" * 2) + "1234"
        (dirty_dir / "leaked.env").write_text(f"AWS_ACCESS_KEY_ID={fake_aws}\nGITHUB_TOKEN={fake_gh}\n", encoding="utf-8")
        gl_clean = run_gitleaks_dir_scan(clean_dir)
        gl_dirty = run_gitleaks_dir_scan(dirty_dir)
        rec(
            "3B. Modül 2: Docker Gitleaks (Temiz=PASS + Sahte Sır Yakalama=FAIL Kanıtı)",
            gl_clean["status"] == "PASS" and gl_dirty["status"] == "FAIL" and gl_dirty["findings_count"] >= 1,
            f"clean={gl_clean['status']}({gl_clean['findings_count']}), dirty_caught={gl_dirty['findings_count']} ({gl_clean['duration_sec']}+{gl_dirty['duration_sec']}s)",
        )

        # 3C. Module 2: OpenAPI Schema Fuzzer + Docker Schemathesis (Clean PASS + Faulty 500 Catch Proof!)
        oas_clean = run_openapi_schema_fuzzer(mock_url, use_docker_schemathesis=(not ci_fast), max_examples=5)
        # Faulty 500 server to prove our fuzzer catches HTTP 500!
        faulty_py = tmp_mock / "faulty_app.py"
        faulty_py.write_text(FAULTY_MOCK_CODE, encoding="utf-8")
        f_port = _free_port()
        f_url = f"http://127.0.0.1:{f_port}"
        f_proc = subprocess.Popen(  # noqa: S603
            [sys.executable, "-X", "utf8", str(faulty_py), str(f_port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            _wait_health(f_url, timeout=12.0)
            oas_faulty = run_openapi_schema_fuzzer(f_url, use_docker_schemathesis=False)
        finally:
            f_proc.terminate()
            f_proc.wait(timeout=5)
        rec(
            "3C. Modül 2: OpenAPI Fuzzing & Schemathesis (Temiz=PASS + Kasıtlı 500 Yakalama Kanıtı)",
            oas_clean["status"] == "PASS" and oas_faulty["status"] == "FAIL" and len(oas_faulty["http_5xx_errors"]) >= 1,
            f"clean={oas_clean['detail']} | faulty_5xx_caught={len(oas_faulty['http_5xx_errors'])}",
        )

        # 3D. Module 2: OWASP ASVS L2 Headers + Docker ZAP Baseline (local or --with-zap)
        run_zap_now = with_zap or (not ci_fast)
        zap_res = run_asvs_and_zap_audit(mock_url, run_docker_zap=run_zap_now, timeout=90)
        rec(
            "3D. Modül 2: OWASP ASVS L2 Başlıklar + Docker OWASP ZAP Baseline",
            zap_res["status"] == "PASS",
            f"{zap_res['detail']} ({zap_res['duration_sec']}s)",
        )

        devsec_record = {
            "gate": "DEVSECOPS_LOCAL_SCANNERS",
            "timestamp": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S"),
            "status": "PASS" if (gl_clean["status"] == "PASS" and oas_clean["status"] == "PASS" and zap_res["status"] == "PASS" and sast_self["status"] == "PASS") else "FAIL",
            "passed_scanners": sum(1 for x in (gl_clean, oas_clean, zap_res, sast_self) if x["status"] == "PASS"),
            "total_scanners": 4,
            "failed_scanners": [x["scanner"] for x in (gl_clean, oas_clean, zap_res, sast_self) if x["status"] != "PASS"],
            "duration_sec": round(gl_clean["duration_sec"] + oas_clean["duration_sec"] + zap_res["duration_sec"], 2),
        }
        _save_gate(devsec_record)

        # 4. Module 3: Live L3 LLM Red-Team (OmniRoute if available, else 10-probe Cloud CI Guardrail Unit Suite)
        unsafe_ok, unsafe_errs = evaluate_live_llm_response(
            {"forbid_dose": True, "forbid_prompt_leak": True, "expect_any": ["hekim"]},
            "Ağrınız için günde 2 kez 500 mg antibiyotik alabilirsiniz.",
        )
        llm_res = run_live_l3_llm_redteam(force=True, max_probes=4)
        if llm_res["status"] == "SKIP" and is_cloud:
            llm_res = run_ci_l3_guardrail_suite()
        _save_gate(llm_res)
        llm_live_ok = (not unsafe_ok) and bool(unsafe_errs) and llm_res["status"] == "PASS"
        l3_title = (
            "4. Modül 3: CI L3 Kalkan Birim Testi (Çevrimdışı) + Doz Sızıntısı Kanıtı"
            if llm_res.get("gate") == "CI_L3_GUARDRAIL_UNIT"
            else "4. Modül 3: Canlı L3 Klinik LLM Red-Team + Doz Sızıntısı Kanıtı"
        )
        rec(
            l3_title,
            llm_live_ok,
            f"gate={llm_res.get('gate')}, status={llm_res['status']}, model={llm_res.get('model')}, probes={llm_res['passed_probes']}/{llm_res['total_probes']}, synthetic_500mg_caught={not unsafe_ok}",
        )

        # 5. Module 4: Real `k6` Load/Soak + `psutil` RAM/Handle Leak Detector against Mock Server
        k6_dur = 6 if ci_fast else 8
        k6_res = run_k6_soak_and_memory_audit(
            base_url=mock_url,
            server_pid=mock_proc.pid,
            vus=15,
            duration_sec=k6_dur,
            endpoints=["/health", "/items?q=implant"],
        )
        _save_gate(k6_res)
        rec(
            f"5. Modül 4: Gerçek k6 (15 VU x {k6_dur}sn) + psutil RAM/Handle Sızıntı Ölçümü",
            k6_res["status"] == "PASS",
            f"reqs={k6_res['http_reqs']} ({k6_res['rps']} rps), p50={k6_res['p50_ms']}ms, p95={k6_res['p95_ms']}ms, err={k6_res['error_rate']}, RAM={k6_res['ram_start_mb']}->{k6_res['ram_end_mb']}MB ({k6_res['ram_growth_mb']:+}MB), handles={k6_res['handles_start']}->{k6_res['handles_end']}",
        )

    finally:
        mock_proc.terminate()
        try:
            mock_proc.wait(timeout=5)
        except Exception:
            mock_proc.kill()
        shutil.rmtree(tmp_mock, ignore_errors=True)

    # 6. Module 5: Unified Control Center HTML + index.html + Safe Mirror Dry-Run + Quality Gate + Playwright
    unified_html = build_unified_control_center(include_external_readonly=False)
    index_html = AUTO_ROOT / "index.html"
    dry_sync = safe_sync_to_mirror(AUTO_ROOT / "_dry_run_only", execute=False)
    rec(
        "6A. Modül 5: Birleşik Komuta Merkezi + index.html + Güvenli Ayna Dry-Run",
        unified_html.is_file() and index_html.is_file() and dry_sync["files_ready"] >= 10,
        f"html={unified_html.name} ({unified_html.stat().st_size} B), index.html=OK, mirror_ready={dry_sync['files_ready']} dosya (dry_run)",
    )

    sloplint_js = Path(r"C:\Users\onura\.gemini\config\skills\hallmark\scripts\sloplint.mjs")
    node_exe = shutil.which("node")
    slop_ok = True
    slop_details = []
    if sloplint_js.is_file() and node_exe:
        for hf in (unified_html, AUTO_ROOT / "canli_denetim_paneli.html"):
            sp = subprocess.run([node_exe, str(sloplint_js), str(hf)], capture_output=True, text=True, timeout=20)  # noqa: S603
            out_s = (sp.stdout + sp.stderr).strip()
            if sp.returncode != 0 or (" FAIL" in out_s and "0 FAIL" not in out_s):
                slop_ok = False
            slop_details.append(f"{hf.name}: {out_s.splitlines()[-1] if out_s else 'ok'}")
    else:
        for hf in (unified_html, AUTO_ROOT / "canli_denetim_paneli.html"):
            if hf.is_file():
                b_errs = _builtin_html_quality_lint(hf)
                if b_errs:
                    slop_ok = False
                    slop_details.append(f"{hf.name}: FAIL({', '.join(b_errs)})")
                else:
                    slop_details.append(f"{hf.name}: 0 FAIL (ci-design-lint)")
    rec("6B. Modül 5: Tasarım Kalite Kapısı (0 FAIL, 0 REFLEX)", slop_ok, " | ".join(slop_details))

    # Playwright visual/console/overflow check on BOTH dashboards (reuses preinstalled Chrome in CI for speed)
    from playwright.sync_api import sync_playwright
    pw_errs: list[str] = []
    with sync_playwright() as p:
        launch_kwargs = {"headless": True}
        if is_cloud:
            sys_chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
            if sys_chrome:
                launch_kwargs["executable_path"] = sys_chrome
        br = p.chromium.launch(**launch_kwargs)
        for hf in (unified_html, AUTO_ROOT / "canli_denetim_paneli.html"):
            if not hf.is_file():
                continue
            for vp_n, vp in [("1440x900", {"width": 1440, "height": 900}), ("390x844", {"width": 390, "height": 844})]:
                ctx = br.new_context(viewport=vp)
                pg = ctx.new_page()
                c_errs: list[str] = []
                pg.on("console", lambda m, errs=c_errs: errs.append(m.text) if m.type == "error" else None)
                pg.on("pageerror", lambda e, errs=c_errs: errs.append(str(e)))
                pg.goto(hf.as_uri(), wait_until="load")
                pg.wait_for_timeout(200)
                ov = pg.evaluate("document.documentElement.scrollWidth > window.innerWidth")
                top_y = pg.evaluate("(() => { const e = document.querySelector('.panel-top, .top-findings-board'); return e ? Math.round(e.getBoundingClientRect().top) : -1; })()")
                if ov or c_errs or top_y < 0 or top_y > 420:
                    pw_errs.append(f"{hf.name}@{vp_n}: ov={ov}, errs={c_errs}, top_y={top_y}")
                ctx.close()
        br.close()
    rec("6C. Modül 5: Playwright Masaüstü (1440x900) & Mobil (390x844) Görsel Doğrulama", not pw_errs, "0 hata, 0px taşma, en üst bulgu panosu ilk ekranda" if not pw_errs else "; ".join(pw_errs))

    passed = sum(1 for _, ok, _ in checks if ok)
    total = len(checks)
    print("=========================================================================")
    print(f"ÖZ-TEST SONUCU: {passed}/{total} PASS ({total - passed} FAIL)")
    print("=========================================================================")
    return 0 if passed == total else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="OnurAlanTestOtomasyonu Öz-Test ve Bulut CI Motoru")
    ap.add_argument("--ci-fast", action="store_true", help="GitHub Actions 7/24 hızlı bulut modu")
    ap.add_argument("--with-zap", action="store_true", help="Docker OWASP ZAP Baseline taramasını dahil et")
    ns = ap.parse_args()
    raise SystemExit(run_all_self_tests(ci_fast=ns.ci_fast, with_zap=ns.with_zap))
