#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Playwright 1440x900 Masaüstü + 390x844 Mobil Görsel ve Fonksiyonel Doğrulama Kapısı."""
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML_FILE = Path(r"C:\Users\onura\OneDrive\Masaüstü\test otomasyonu\canli_denetim_paneli.html")
SHOT_DIR = Path(r"C:\Users\onura\OneDrive\Masaüstü\test otomasyonu\veri")


def main():
    url = HTML_FILE.as_uri()
    console_errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, w, h in [("desktop_1440x900", 1440, 900), ("mobile_390x844", 390, 844)]:
            ctx = browser.new_context(viewport={"width": w, "height": h})
            page = ctx.new_page()
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda err: console_errors.append(str(err)))
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(400)

            overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
            score_txt = page.locator("#kpi-score").inner_text()
            runs_txt = page.locator("#kpi-runs").inner_text()
            defects_rows = page.locator("#checks-tbody tr").count()
            wa_rows = page.locator("#wa-tbody tr").count()
            repo_cards = page.locator("#repo-grid .card").count()
            hist_rows = page.locator("#history-tbody tr").count()

            page.screenshot(path=str(SHOT_DIR / f"verify_{name}.png"), full_page=False)
            print(f"[{name}] overflow={overflow} | score='{score_txt}' | runs='{runs_txt}' | "
                  f"checks={defects_rows} | wa_questions={wa_rows} | github_repos={repo_cards} | history_turns={hist_rows}")
            assert not overflow, f"Yatay taşma tespit edildi: {name}"
            assert "100" in score_txt and ".." not in score_txt, f"Veri yüklenmedi: {score_txt}"
            assert defects_rows >= 20, f"Kontrol tablosu eksik: {defects_rows}"
            assert wa_rows >= 30, f"WhatsApp jüri tablosu eksik: {wa_rows}"
            assert repo_cards >= 7, f"GitHub repo kartları eksik: {repo_cards}"
            assert hist_rows >= 2, f"Birikimli geçmiş turları eksik: {hist_rows}"
            ctx.close()
        browser.close()
    assert not console_errors, f"Console hataları: {console_errors}"
    print("[PASS] Playwright 1440x900 + 390x844 doğrulaması sıfır hata ve sıfır taşma ile geçti!")


if __name__ == "__main__":
    main()
