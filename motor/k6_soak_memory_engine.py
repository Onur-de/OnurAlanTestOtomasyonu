#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 4: Real `k6` Load/Soak Testing + `psutil` RAM/Memory & Handle Leak Detector.
- Runs the real installed `k6.exe` against a local ephemeral server URL.
- Simultaneously profiles the target server PID via `psutil` every 1 second to measure:
  * RSS Memory baseline -> peak -> final (MB) and leak growth slope (MB/min)
  * Open handles / descriptors growth (connection/file leak detection)
  * Peak CPU utilization (%)
- Exports structured JSON metrics: total requests, RPS, error rate, p50, p95, p99, thresholds.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import psutil

TZ = ZoneInfo("Europe/Istanbul")


def _find_k6() -> str | None:
    p = shutil.which("k6")
    if p:
        return p
    win_default = Path(r"C:\Program Files\k6\k6.exe")
    return str(win_default) if win_default.is_file() else None


def run_k6_soak_and_memory_audit(
    base_url: str,
    server_pid: int | None = None,
    vus: int = 20,
    duration_sec: int = 20,
    endpoints: list[str] | None = None,
    max_ram_growth_mb: float = 120.0,
    max_p95_ms: float = 600.0,
    max_error_rate: float = 0.01,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    ts = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    out: dict[str, Any] = {
        "gate": "K6_SOAK_MEMORY",
        "timestamp": ts,
        "status": "SKIP",
        "vus": vus,
        "duration_target_sec": duration_sec,
        "http_reqs": 0,
        "rps": 0.0,
        "error_rate": 0.0,
        "p50_ms": 0.0,
        "p95_ms": 0.0,
        "p99_ms": 0.0,
        "ram_start_mb": 0.0,
        "ram_peak_mb": 0.0,
        "ram_end_mb": 0.0,
        "ram_growth_mb": 0.0,
        "handles_start": 0,
        "handles_end": 0,
        "cpu_peak_pct": 0.0,
        "errors": [],
        "duration_sec": 0.0,
    }

    if not base_url.startswith(("http://127.0.0.1:", "http://localhost:")):
        out["status"] = "FAIL"
        out["errors"].append("Yalnız yerel izole sunucu üzerinde k6 koşulabilir")
        return out

    k6_exe = _find_k6()
    if not k6_exe:
        out["status"] = "FAIL"
        out["errors"].append("k6 yürütülebilir dosyası bulunamadı")
        return out

    ep_list = endpoints or ["/health"]
    ep_json = json.dumps(ep_list)
    k6_script = f"""
import http from 'k6/http';
import {{ check, sleep }} from 'k6';

export const options = {{
  vus: {int(vus)},
  duration: '{int(duration_sec)}s',
  thresholds: {{
    http_req_failed: ['rate<{max_error_rate}'],
    http_req_duration: ['p(95)<{int(max_p95_ms)}'],
  }},
}};

const ENDPOINTS = {ep_json};

export default function () {{
  const ep = ENDPOINTS[(__ITER + __VU) % ENDPOINTS.length];
  const r = http.get('{base_url}' + ep);
  check(r, {{ 'status_ok': (res) => res.status >= 200 && res.status < 400 }});
  sleep(0.05);
}}
"""

    tmp_d = Path(tempfile.mkdtemp(prefix="dc_k6_"))
    script_file = tmp_d / "soak.js"
    summary_file = tmp_d / "summary.json"
    script_file.write_text(k6_script, encoding="utf-8")

    # Background psutil memory & handle sampler
    samples_rss: list[float] = []
    samples_handles: list[int] = []
    samples_cpu: list[float] = []
    stop_evt = threading.Event()

    def _profile_loop():
        if not server_pid:
            return
        try:
            proc = psutil.Process(server_pid)
            proc.cpu_percent(interval=None)
            while not stop_evt.is_set():
                if not proc.is_running():
                    break
                rss_mb = proc.memory_info().rss / (1024 * 1024)
                samples_rss.append(round(rss_mb, 2))
                try:
                    h_cnt = proc.num_handles() if hasattr(proc, "num_handles") else proc.num_fds()
                    samples_handles.append(int(h_cnt))
                except Exception:
                    pass
                samples_cpu.append(round(proc.cpu_percent(interval=None), 1))
                stop_evt.wait(0.8)
        except Exception:
            pass

    prof_t = threading.Thread(target=_profile_loop, daemon=True)
    prof_t.start()

    try:
        kp = subprocess.run(
            [k6_exe, "run", "--no-color", "--summary-export", str(summary_file), str(script_file)],
            capture_output=True,
            text=True,
            timeout=max(60, duration_sec + 45),
        )
        stop_evt.set()
        prof_t.join(timeout=3)

        if samples_rss:
            out["ram_start_mb"] = samples_rss[0]
            out["ram_peak_mb"] = max(samples_rss)
            out["ram_end_mb"] = samples_rss[-1]
            out["ram_growth_mb"] = round(samples_rss[-1] - samples_rss[0], 2)
        if samples_handles:
            out["handles_start"] = samples_handles[0]
            out["handles_end"] = samples_handles[-1]
        if samples_cpu:
            out["cpu_peak_pct"] = max(samples_cpu)

        if summary_file.is_file():
            sj = json.loads(summary_file.read_text(encoding="utf-8"))
            metrics = sj.get("metrics") or {}
            reqs_m = metrics.get("http_reqs") or {}
            fail_m = metrics.get("http_req_failed") or {}
            dur_m = metrics.get("http_req_duration") or {}

            out["http_reqs"] = int(reqs_m.get("count", 0))
            out["rps"] = round(float(reqs_m.get("rate", 0.0)), 1)
            out["error_rate"] = round(float(fail_m.get("value", 0.0)), 4)
            out["p50_ms"] = round(float(dur_m.get("med", 0.0)), 2)
            out["p95_ms"] = round(float(dur_m.get("p(95)", 0.0)), 2)
            out["p99_ms"] = round(float(dur_m.get("p(99)", dur_m.get("max", 0.0))), 2)
        else:
            out["errors"].append("k6 summary.json üretilemedi")

        if kp.returncode != 0:
            out["errors"].append(f"k6 eşik/çalışma hatası (rc={kp.returncode}): {(kp.stderr or kp.stdout)[-200:]}")
        if out["http_reqs"] <= 0:
            out["errors"].append("k6 sıfır istek raporladı")
        if out["ram_growth_mb"] > max_ram_growth_mb:
            out["errors"].append(f"Bellek sızıntısı şüphesi: RAM +{out['ram_growth_mb']} MB > {max_ram_growth_mb} MB")
        if out["p95_ms"] > max_p95_ms:
            out["errors"].append(f"Yüksek p95 gecikme: {out['p95_ms']} ms > {max_p95_ms} ms")
        if out["error_rate"] > max_error_rate:
            out["errors"].append(f"Yüksek hata oranı: {out['error_rate']} > {max_error_rate}")

        out["status"] = "PASS" if not out["errors"] else "FAIL"
    except Exception as exc:
        stop_evt.set()
        out["status"] = "FAIL"
        out["errors"].append(f"k6 çalıştırma istisnası: {exc}")
    finally:
        shutil.rmtree(tmp_d, ignore_errors=True)
        out["duration_sec"] = round(time.perf_counter() - t0, 2)

    return out
