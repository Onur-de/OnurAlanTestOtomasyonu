#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DentaCore Saatlik Düşman Simülasyonu — Canlı Telemetri ve Kontrol Sunucusu (Port 8795)
- GET /                 -> canli_denetim_paneli.html
- GET /veri/dashboard_data.js -> Güncel birikimli veri paketi
- GET /api/status       -> Son tur özeti ve geçmiş turlar
- POST /api/run-now     -> Tarayıcıdan tek tıkla yeni düşman simülasyon turu başlatır ve not defterine ekler
"""
from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUTO_ROOT = HERE.parent
DATA_DIR = AUTO_ROOT / "veri"
HTML_PATH = AUTO_ROOT / "canli_denetim_paneli.html"
JS_PATH = DATA_DIR / "dashboard_data.js"
LEDGER_PATH = AUTO_ROOT / "SAATLIK_NOT_VE_EKSIK_DEFTERI.md"

import sys
sys.path.insert(0, str(HERE))
from adversarial_engine import run_hourly_adversarial_simulation  # noqa: E402

_RUN_LOCK = threading.Lock()


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def _send(self, code: int, body: bytes, ctype: str = "application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/", "/canli_denetim_paneli.html"):
            if HTML_PATH.exists():
                self._send(200, HTML_PATH.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send(404, b"Panel HTML bulunamadi", "text/plain; charset=utf-8")
            return
        if path == "/veri/dashboard_data.js":
            if JS_PATH.exists():
                self._send(200, JS_PATH.read_bytes(), "application/javascript; charset=utf-8")
            else:
                self._send(200, b"window.DENTACORE_SENTINEL_DATA = null;", "application/javascript; charset=utf-8")
            return
        if path == "/SAATLIK_NOT_VE_EKSIK_DEFTERI.md":
            if LEDGER_PATH.exists():
                self._send(200, LEDGER_PATH.read_bytes(), "text/markdown; charset=utf-8")
            else:
                self._send(404, b"Defter bulunamadi", "text/plain; charset=utf-8")
            return
        if path == "/api/status":
            if JS_PATH.exists():
                raw = JS_PATH.read_text(encoding="utf-8")
                prefix = "window.DENTACORE_SENTINEL_DATA = "
                if raw.startswith(prefix):
                    raw = raw[len(prefix):].rstrip().rstrip(";")
                self._send(200, raw.encode("utf-8"))
            else:
                self._send(200, json.dumps({"ok": False}).encode("utf-8"))
            return
        self._send(404, json.dumps({"error": "Bulunamadı"}).encode("utf-8"))

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/run-now":
            if not _RUN_LOCK.acquire(blocking=False):
                self._send(409, json.dumps({"ok": False, "message": "Simülasyon şu an zaten çalışıyor."}).encode("utf-8"))
                return
            try:
                summary = run_hourly_adversarial_simulation()
                self._send(200, json.dumps({"ok": True, "run_id": summary["run_id"], "overall_score": summary["overall_score"], "grade": summary["grade_letter"]}, ensure_ascii=False).encode("utf-8"))
            except Exception as exc:
                self._send(500, json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False).encode("utf-8"))
            finally:
                _RUN_LOCK.release()
            return
        self._send(404, json.dumps({"error": "Bulunamadı"}).encode("utf-8"))


def main():
    port = 8795
    srv = ThreadingHTTPServer(("127.0.0.1", port), DashboardHandler)
    print(f"[*] Canlı Düşman Denetim Paneli Sunucusu çalışıyor: http://127.0.0.1:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    main()
