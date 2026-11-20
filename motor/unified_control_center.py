#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module 5: Unified Control Center (`BIRLESIK_KOMUTA_MERKEZI.html`) & Safe Mirror Helper.
- Aggregates all test automation feeds into ONE single top-of-page chronological dashboard
  (Newest First: Timestamp, Engine, Status, Errors, Missing Items, Findings).
- Strictly READ-ONLY if optional external sibling logs are included (never writes outside
  `test otomasyonu` unless `safe_sync_to_mirror(..., execute=True)` is explicitly invoked).
- Strictly adheres to Hallmark / ui-ux-pro-max / sloplint rules (0 FAIL, 0 REFLEX).
"""
from __future__ import annotations

import html
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

LOG = logging.getLogger(__name__)
TZ = ZoneInfo("Europe/Istanbul")
HERE = Path(__file__).resolve().parent
AUTO_ROOT = HERE.parent
DATA_DIR = AUTO_ROOT / "veri"
SENTINEL_HIST = DATA_DIR / "not_gecmisi.jsonl"
ENT_HIST = DATA_DIR / "enterprise_gates_history.jsonl"
CLOUD_ENT_HIST = DATA_DIR / "cloud_enterprise_history.jsonl"
OUT_HTML = AUTO_ROOT / "BIRLESIK_KOMUTA_MERKEZI.html"
OUT_INDEX = AUTO_ROOT / "index.html"
OUT_JS = DATA_DIR / "unified_data.js"


def _esc(v: object) -> str:
    return html.escape(str(v or "")).replace("—", ":").replace("–", "-")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except Exception as exc:
                LOG.debug("JSONL satırı atlandı (%s): %s", path.name, exc)
    return rows


def append_enterprise_gate_record(record: dict[str, Any], cloud: bool = False) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    target = CLOUD_ENT_HIST if cloud else ENT_HIST
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def safe_sync_to_mirror(mirror_root: Path, execute: bool = False) -> dict[str, Any]:
    """
    Opt-in safe mirror synchronization helper.
    When `execute=False` (default/dry-run), NEVER writes outside `test otomasyonu`.
    """
    files_to_sync = [
        "motor/adversarial_engine.py",
        "motor/polymorphic_formations.py",
        "motor/weekly_168h_curriculum.py",
        "motor/pg_docker_engine.py",
        "motor/devsecops_local_scanners.py",
        "motor/live_llm_redteam.py",
        "motor/k6_soak_memory_engine.py",
        "motor/unified_control_center.py",
        "motor/self_test_suite.py",
        "canli_denetim_paneli.html",
        "BIRLESIK_KOMUTA_MERKEZI.html",
    ]
    copied: list[str] = []
    skipped: list[str] = []
    for rel in files_to_sync:
        src = AUTO_ROOT / rel
        if not src.is_file():
            skipped.append(rel)
            continue
        if execute:
            dst = mirror_root / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        copied.append(rel)
    return {
        "executed": execute,
        "target": str(mirror_root),
        "files_ready": len(copied),
        "skipped": skipped,
    }


def build_unified_control_center(
    include_external_readonly: bool = False,
    external_results_dir: Path | None = None,
) -> Path:
    """
    Builds `BIRLESIK_KOMUTA_MERKEZI.html` with a unified newest-first timeline at the very top.
    By default (`include_external_readonly=False`), reads ONLY `test otomasyonu/veri/*.jsonl`.
    """
    now_str = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    events: list[dict[str, Any]] = []

    # 1. Local Adversarial Sentinel runs
    for r in _read_jsonl(SENTINEL_HIST):
        defects = int(r.get("defects_found", 0))
        titles = r.get("defect_titles") or []
        summary = " | ".join(titles[:4]) if titles else ("Temiz (0 Hata, 0 Eksik)" if defects == 0 else f"{defects} bulgu kaydedildi")
        events.append({
            "timestamp": str(r.get("timestamp", "")),
            "engine": f"Adversarial Sentinel (Tur #{r.get('run_number')})",
            "status": "PASS" if defects == 0 else "WARN",
            "errors": 0,
            "missing": defects,
            "findings": 0,
            "metric": f"{r.get('overall_score', 0)}/100 ({r.get('grade_letter', '-')}) | WA {r.get('wa_score', 0)}/100",
            "summary": summary,
        })

    # 2. Local + Cloud Enterprise 5-Gate runs (Docker PG, DevSecOps Docker, Live L3 LLM, k6 Soak+RAM)
    ent_rows = _read_jsonl(ENT_HIST) + _read_jsonl(CLOUD_ENT_HIST)
    ent_rows.sort(key=lambda x: str(x.get("timestamp", "")))
    latest_gates: dict[str, dict[str, Any]] = {}
    for g in ent_rows:
        g_name = str(g.get("gate", "ENTERPRISE"))
        latest_gates[g_name] = g
        runner_tag = "[Bulut CI] " if "github" in str(g.get("runner", "")).lower() else ""
        st = str(g.get("status", "SKIP"))
        errs = g.get("errors") or g.get("failed_scanners") or []
        metric_txt = str(g.get("metric_summary") or "")
        if not metric_txt:
            if g_name == "DOCKER_POSTGRES":
                metric_txt = f"{g.get('image', 'pg')} | {g.get('tables_created', 0)} tablo | ACID {g.get('acid_race_commits', 0)}/1"
            elif g_name == "DEVSECOPS_LOCAL_SCANNERS":
                metric_txt = f"{g.get('passed_scanners', 0)}/{g.get('total_scanners', 0)} tarayıcı geçti"
            elif g_name in ("LIVE_L3_LLM_REDTEAM", "CI_L3_GUARDRAIL_UNIT"):
                metric_txt = f"{g.get('model', 'LLM')} | {g.get('passed_probes', 0)}/{g.get('total_probes', 0)} kalkan"
            elif g_name == "K6_SOAK_MEMORY":
                metric_txt = f"{g.get('http_reqs', 0)} istek | p95={g.get('p95_ms', 0)}ms | RAM {g.get('ram_growth_mb', 0):+}MB"
            else:
                metric_txt = f"{g.get('duration_sec', 0)} sn"
        events.append({
            "timestamp": str(g.get("timestamp", "")),
            "engine": f"{runner_tag}{g_name}",
            "status": st,
            "errors": len(errs) if st == "FAIL" else 0,
            "missing": len(g.get("parity_missing_in_pg") or []),
            "findings": int(g.get("failed_probes", 0)),
            "metric": metric_txt,
            "summary": " | ".join(str(x)[:110] for x in errs[:3]) if errs else "Temiz (0 Hata, 0 Bulgu)",
        })

    # 3. Optional strictly read-only external feeds
    if include_external_readonly and external_results_dir and external_results_dir.is_dir():
        for h in _read_jsonl(external_results_dir / "TUM_SAATLIK_TEST_GECMISI.jsonl"):
            fs = h.get("findings_summary") or {}
            ec = int(fs.get("error_count", 0))
            mc = int(fs.get("missing_count", 0))
            fc = int(fs.get("finding_count", 0))
            notes = [*(fs.get("errors") or []), *(fs.get("missing") or []), *(fs.get("findings") or [])]
            events.append({
                "timestamp": str(h.get("timestamp", "")),
                "engine": f"Saatlik Otonom (Koşu #{h.get('run_number')})",
                "status": "PASS" if (ec + mc + fc) == 0 else "WARN",
                "errors": ec,
                "missing": mc,
                "findings": fc,
                "metric": f"{h.get('real_users_passed', 0)}/{h.get('real_users_count', 0)} kullanıcı",
                "summary": " | ".join(notes[:3]) if notes else "Temiz (0 Hata, 0 Eksik, 0 Bulgu)",
            })
        for d in _read_jsonl(external_results_dir / "Derin_Denetim_Kanitlari" / "derin_denetim_gecmisi.jsonl"):
            ec = int(d.get("errors_count", 0))
            mc = int(d.get("gaps_count", 0))
            fc = int(d.get("vulns_count", 0))
            prev = d.get("findings_preview") or []
            events.append({
                "timestamp": str(d.get("timestamp", "")),
                "engine": "Derin Güvenlik ve Tam Tıklama",
                "status": "PASS" if (ec + fc) == 0 else "FAIL",
                "errors": ec,
                "missing": mc,
                "findings": fc,
                "metric": f"{d.get('real_users_ok', '-')} kullanıcı | {d.get('sec_passed', '-')} OWASP",
                "summary": " | ".join(prev[:3]) if prev else "Temiz (0 Hata, 0 Eksik, 0 Bulgu)",
            })

    events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    # Save JSON data companion
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JS.write_text(
        "window.DENTACORE_UNIFIED_DATA = " + json.dumps({"updated_at": now_str, "events": events[:100], "latest_gates": latest_gates}, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )

    total_err = sum(e["errors"] for e in events[:10])
    total_miss = sum(e["missing"] for e in events[:10])
    total_find = sum(e["findings"] for e in events[:10])
    latest_ts = events[0]["timestamp"] if events else now_str

    svg_shield = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    svg_clock = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>'
    svg_layers = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>'

    timeline_rows = []
    for idx_e, ev in enumerate(events[:12]):
        st = ev["status"]
        b_cls = "badge-pass" if st == "PASS" else ("badge-warn" if st in ("WARN", "SKIP") else "badge-fail")
        newest_tag = ' <span class="badge badge-pass">En Yeni</span>' if idx_e == 0 else ""
        timeline_rows.append(
            f'<tr>'
            f'<td><code>{_esc(ev["timestamp"])}</code>{newest_tag}</td>'
            f'<td><strong>{_esc(ev["engine"])}</strong></td>'
            f'<td><span class="badge {b_cls}">{_esc(st)}</span></td>'
            f'<td><code>{ev["errors"]}</code></td>'
            f'<td><code>{ev["missing"]}</code></td>'
            f'<td><code>{ev["findings"]}</code></td>'
            f'<td><code>{_esc(ev["metric"])}</code></td>'
            f'<td>{_esc(ev["summary"])}</td>'
            f'</tr>'
        )
    if not timeline_rows:
        timeline_rows.append('<tr><td colspan="8">Henüz koşu kaydı yok.</td></tr>')

    gate_cards = []
    gate_meta = [
        ("DOCKER_POSTGRES", "1. Docker PostgreSQL", "PostgreSQL 17 DDL, ACID kilidi ve tablo paritesi"),
        ("DEVSECOPS_LOCAL_SCANNERS", "2. DevSecOps Tarayıcıları", "Gitleaks, OpenAPI Fuzz, OWASP ZAP, Ruff, Bandit"),
        ("LIVE_L3_LLM_REDTEAM", "3. L3 LLM Kalkanı", "Enjeksiyon, doz, KVKK ve fiyat kalkan doğrulaması"),
        ("K6_SOAK_MEMORY", "4. k6 Yük ve Bellek", "k6 yük testi ve psutil RAM/Handle artış takibi"),
    ]
    for g_key, g_title, g_desc in gate_meta:
        gd = latest_gates.get(g_key)
        if not gd and g_key == "LIVE_L3_LLM_REDTEAM":
            gd = latest_gates.get("CI_L3_GUARDRAIL_UNIT")
        if gd:
            g_st = str(gd.get("status", "SKIP"))
            g_cls = "badge-pass" if g_st == "PASS" else ("badge-warn" if g_st == "SKIP" else "badge-fail")
            g_ts = str(gd.get("timestamp", "-"))
            if g_key == "DOCKER_POSTGRES":
                g_val = f"{gd.get('tables_created', 0)} Tablo | ACID {gd.get('acid_race_commits', 0)}/1"
            elif g_key == "DEVSECOPS_LOCAL_SCANNERS":
                g_val = f"{gd.get('passed_scanners', 0)}/{gd.get('total_scanners', 0)} Tarayıcı"
            elif g_key == "LIVE_L3_LLM_REDTEAM":
                mode_lbl = "CI Birim" if gd.get("gate") == "CI_L3_GUARDRAIL_UNIT" else "Canlı LLM"
                g_val = f"{gd.get('passed_probes', 0)}/{gd.get('total_probes', 0)} ({mode_lbl})"
            else:
                g_val = f"{gd.get('http_reqs', 0)} İstek | p95 {gd.get('p95_ms', 0)} ms"
        else:
            g_st, g_cls, g_ts, g_val = "BEKLİYOR", "badge-warn", "Henüz koşulmadı", "Hazır"
        gate_cards.append(
            f'<article class="card">'
            f'<div class="card-top"><strong>{_esc(g_title)}</strong><span class="badge {g_cls}">{_esc(g_st)}</span></div>'
            f'<div class="card-val">{_esc(g_val)}</div>'
            f'<div class="card-desc">{_esc(g_desc)}</div>'
            f'<div class="card-foot">Son: <code>{_esc(g_ts)}</code></div>'
            f'</article>'
        )

    CSS = """/* Hallmark · shape: dashboard · genre: modern-minimal · theme: ConsoleUnified (seed dentacore-unified-v8) · job: report · draw: unified-v8
 * hero: stage · nav: topbar · footer: ledger · imagery: none · signature: unified-top-ledger · wayfind: 4px-grid
 * axes: dark/grotesk-sans/chromatic-teal · posture: restrained · contrast: pass · fold: pass · v2.0.0 */
/* Hallmark · pre-emit critique: P9 H9 E9 S9 R9 V9 · weakest: S, strict 4px spacing scale across all cards and tables */
:root {
  --bg-canvas: #050914;
  --bg-surface: #0D1322;
  --bg-elevated: #151D30;
  --text-primary: #F4F7FB;
  --text-secondary: #C7D2E2;
  --text-muted: #8D9CB2;
  --border-default: #2C3A52;
  --border-strong: #415576;
  --accent-green: #38E592;
  --accent-green-soft: rgba(56, 229, 146, 0.14);
  --accent-red: #F25C69;
  --accent-red-soft: rgba(242, 92, 105, 0.16);
  --accent-amber: #F5B742;
  --accent-amber-soft: rgba(245, 183, 66, 0.16);
  --accent-teal: #34D1BF;
  --accent-teal-soft: rgba(52, 209, 191, 0.16);
  --font-sans: 'Fira Sans', 'Segoe UI', system-ui, sans-serif;
  --font-mono: 'Fira Code', 'Consolas', monospace;
  --r-lg: 12px;
  --r-md: 8px;
  --r-sm: 4px;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  overflow-x: clip;
  background-color: var(--bg-canvas);
  color: var(--text-primary);
  font-family: var(--font-sans);
  line-height: 1.55;
}
:focus-visible { outline: 2px solid var(--accent-teal); outline-offset: 2px; }
.wrap { max-width: 1380px; margin: 0 auto; padding: 24px 20px 64px; }
.topbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 24px;
  background-color: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--r-lg);
  margin-bottom: 20px;
}
.brand { display: flex; align-items: center; gap: 16px; }
.brand-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--r-md);
  background-color: var(--accent-teal-soft);
  border: 1px solid var(--accent-teal);
  color: var(--accent-teal);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
h1 { font-size: 1.3rem; font-weight: 700; line-height: 1.25; text-wrap: balance; }
.sub { font-size: 0.88rem; color: var(--text-muted); margin-top: 4px; }
.nav-links { display: flex; flex-wrap: wrap; gap: 8px; }
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: var(--r-md);
  border: 1px solid var(--border-strong);
  background-color: var(--bg-elevated);
  color: var(--text-primary);
  text-decoration: none;
  font-size: 0.86rem;
  font-weight: 600;
  transition: border-color 0.16s ease, background-color 0.16s ease;
}
.btn:hover { border-color: var(--accent-teal); background-color: var(--bg-surface); }
.btn:active { transform: translateY(1px); }
.panel {
  background-color: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--r-lg);
  padding: 20px 24px;
  margin-bottom: 24px;
}
.panel-top { border: 2px solid var(--accent-teal); }
.panel-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
h2 {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 700;
  text-wrap: balance;
}
.top-strip {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px;
  border-radius: var(--r-md);
  background-color: var(--bg-elevated);
  border: 1px solid var(--border-strong);
  margin-bottom: 16px;
  font-family: var(--font-mono);
  font-size: 0.88rem;
}
.grid-4 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.card {
  background-color: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  border-radius: var(--r-lg);
  padding: 20px;
}
.card-top { display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 12px; }
.card-val { font-family: var(--font-mono); font-size: 1.25rem; font-weight: 700; color: var(--accent-teal); margin-bottom: 8px; }
.card-desc { font-size: 0.86rem; color: var(--text-secondary); margin-bottom: 12px; }
.card-foot { font-size: 0.8rem; color: var(--text-muted); }
.table-wrap { width: 100%; overflow-x: auto; border: 1px solid var(--border-default); border-radius: var(--r-md); }
table { width: 100%; border-collapse: collapse; text-align: left; font-size: 0.86rem; }
th, td { padding: 12px 16px; border-bottom: 1px solid var(--border-default); vertical-align: top; }
th { background-color: var(--bg-elevated); color: var(--text-secondary); font-weight: 600; white-space: nowrap; }
tr:last-child td { border-bottom: none; }
code {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--accent-teal);
  background-color: var(--accent-teal-soft);
  padding: 4px 8px;
  border-radius: var(--r-sm);
  white-space: nowrap;
}
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: var(--r-sm);
  font-size: 0.76rem;
  font-weight: 700;
  white-space: nowrap;
}
.badge-pass { background-color: var(--accent-green-soft); color: var(--accent-green); border: 1px solid var(--accent-green); }
.badge-warn { background-color: var(--accent-amber-soft); color: var(--accent-amber); border: 1px solid var(--accent-amber); }
.badge-fail { background-color: var(--accent-red-soft); color: var(--accent-red); border: 1px solid var(--accent-red); }
.footer-bar {
  padding-top: 16px;
  border-top: 1px solid var(--border-default);
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
  font-size: 0.84rem;
  color: var(--text-muted);
}
@media (max-width: 640px) {
  .wrap { padding: 16px 12px 48px; }
  .topbar, .panel { padding: 16px; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation: none !important; transition: none !important; }
}
"""

    doc = f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Test otomasyonu birleşik komuta merkezi: saatlik zaman çizelgesi, PostgreSQL, DevSecOps tarayıcıları, canlı L3 LLM Red-Team ve k6 yük/bellek izleme.">
  <meta http-equiv="refresh" content="300">
  <title>Test Otomasyonu : Birleşik Komuta Merkezi</title>
  <style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <header class="topbar">
    <div class="brand">
      <div class="brand-icon">{svg_shield}</div>
      <div>
        <h1>Birleşik Test Komuta Merkezi</h1>
        <p class="sub">Saatlik test akışı ve 4 kurumsal güvenlik kapısı</p>
      </div>
    </div>
    <nav class="nav-links" aria-label="Panel bağlantıları">
      <a class="btn" href="canli_denetim_paneli.html">Düşman Paneli</a>
      <a class="btn" href="SAATLIK_NOT_VE_EKSIK_DEFTERI.md" target="_blank" rel="noopener">Not Defteri (.md)</a>
    </nav>
  </header>

  <section class="panel panel-top" aria-label="Canlı Akış">
    <div class="panel-head">
      <h2>{svg_clock}Canlı Saat, Hata ve Bulgu Akışı</h2>
      <span class="badge {"badge-pass" if (total_err + total_find) == 0 else "badge-fail"}">Güncelleme: {_esc(now_str)}</span>
    </div>
    <div class="top-strip">
      <strong>Son Olay: {_esc(latest_ts)}</strong>
      <span>Son 10 Kayıt: <code>Hata: {total_err}</code> <code>Eksik: {total_miss}</code> <code>Bulgu: {total_find}</code></span>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Tarih ve Saat</th>
            <th>Motor / Kapı</th>
            <th>Durum</th>
            <th>Hata</th>
            <th>Eksik</th>
            <th>Bulgu</th>
            <th>Ölçüm</th>
            <th>Özet</th>
          </tr>
        </thead>
        <tbody>{''.join(timeline_rows)}</tbody>
      </table>
    </div>
  </section>

  <section aria-label="4 Kurumsal Güvenlik Kapısı">
    <div class="panel-head">
      <h2>{svg_layers}4 Kurumsal Güvenlik Kapısı</h2>
    </div>
    <div class="grid-4">
      {''.join(gate_cards)}
    </div>
  </section>

  <footer class="footer-bar">
    <span>DentaCore Adversarial Sentinel v2.0 Birleşik Komuta Merkezi</span>
    <span>Son derleme: {_esc(now_str)}</span>
  </footer>
</div>
</body>
</html>
"""
    OUT_HTML.write_text(doc, encoding="utf-8")
    OUT_INDEX.write_text(doc, encoding="utf-8")
    return OUT_HTML


if __name__ == "__main__":
    p = build_unified_control_center(include_external_readonly=False)
    print(f"Unified Control Center built: {p}")
