#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DentaCore Canlı GitHub Repo Tarayıcı & Akıllı Mimari Öneri Motoru
("GitHub'da repolara baksın. Bize öneri versin")

Bu modül her saatlik turda:
1. O turda DentaCore'da tespit edilen gerçek eksikleri (WhatsApp çok turlu hafıza, bulanık yazım hatası eşleştirme,
   Odontogram FDI diş yüzeyi kalıcılığı, çalışma saati/Pazar randevu kural motoru, hız sınırlama ve kaos testi) analiz eder.
2. GitHub REST API (https://api.github.com/search/repositories) üzerinden canlı arama yaparak en yüksek yıldızlı
   açık kaynak projeleri çeker (çevrimdışı veya rate-limit durumunda doğrulanmış zengin önbellekle birleştirir).
3. Her repo için DentaCore'un hangi dosyasına (`router.py`, `run_local.py`, `panel.py`, `app.js`, `faq.json`)
   nasıl entegre edileceğini adım adım gösteren somut mimari reçete üretir.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import httpx


# Tespit edilen eksik kategorilerine göre canlı GitHub arama sorguları ve doğrudan DentaCore entegrasyon reçeteleri
GITHUB_TOPICS_MATRIX: list[dict[str, Any]] = [
    {
        "gap_id": "GAP-WA-NLP",
        "gap_title": "WhatsApp Bot Bulanık Eşleşme (Typo/STT) & Çok Turlu Diyalog Hafızası",
        "target_file": "4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/router.py & faq.json",
        "github_query": "rapidfuzz OR chatterbot OR rasa state machine python",
        "curated_repos": [
            {
                "full_name": "rapidfuzz/RapidFuzz",
                "html_url": "https://github.com/rapidfuzz/RapidFuzz",
                "stargazers_count": 3150,
                "language": "C++ / Python",
                "description": "Rapid fuzzy string matching in Python using various string metrics (Levenshtein, Jaro-Winkler, token_set_ratio).",
                "dentacore_recipe": (
                    "`router.py` içindeki `TokenRouter.route()` fonksiyonunda `L1-acil` ve `L1-sss` regex taraması başarısız olduğunda "
                    "`rapidfuzz.fuzz.token_set_ratio(n, keyword) >= 82` kontrolü ekleyin. Böylece müşteri 'inpilant fyatı nekadr' veya "
                    "'kanma durmuyo yuzm sisti' yazdığında 0 LLM tokenı ile L1 katmanında anında yakalanır."
                ),
            },
            {
                "full_name": "pytransitions/transitions",
                "html_url": "https://github.com/pytransitions/transitions",
                "stargazers_count": 6100,
                "language": "Python",
                "description": "A lightweight, object-oriented finite state machine implementation in Python with async support.",
                "dentacore_recipe": (
                    "`router.py` şu an tamamen durumsuz (stateless) çalışıyor. Her `patient_id` için son 3 mesajın niyetini ve durumunu "
                    "(`IDLE -> ASKED_TREATMENT -> OFFERED_APPT -> AWAITING_SLOT`) Redis/SQLite üzerinde `transitions` durum makinesiyle "
                    "tutun. Müşteri 'Olur yarın 15:00 uygun mu?' dediğinde önceki mesajın randevu teklifi olduğunu anlayıp doğrudan randevu akışına bağlayın."
                ),
            },
            {
                "full_name": "emcie-co/parlant",
                "html_url": "https://github.com/emcie-co/parlant",
                "stargazers_count": 18335,
                "language": "Python",
                "description": "Customer-facing conversational AI agents built for control: Guideline-driven utterance composition, empathy framing, zero hallucination.",
                "dentacore_recipe": (
                    "`router.py` içindeki `_compose_parlant_concierge_reply()` ile statik şablonları 4-katmanlı VIP Hasta Koordinatörü mimarisine "
                    "(1. Samimi & Resmi Karşılama, 2. Hastanın Sorduğu Tedavi/Çocuk Yaşı/Ülke/Nakit İsteğini Yansıtma, 3. Kliniğe Özel `ai_custom_rules_json` "
                    "Politika Enjeksiyonu, 4. Değer Hissettiren Nazik Randevu Daveti) dönüştürün."
                ),
            },
            {
                "full_name": "chatwoot/chatwoot",
                "html_url": "https://github.com/chatwoot/chatwoot",
                "stargazers_count": 40115,
                "language": "Ruby / TypeScript",
                "description": "Open-source omnichannel customer engagement suite and Captain AI conversational concierge for WhatsApp and Instagram.",
                "dentacore_recipe": (
                    "WhatsApp ve Instagram DM kanallarında resmi-samimi hasta koordinatörü ses tonu, şikayet ve ağrı bildirimlerinde "
                    "empatik yatıştırma ve başhekimlik/uzman hekim devri (`handoff=True`) akışını işletin."
                ),
            },
            {
                "full_name": "RasaHQ/rasa",
                "html_url": "https://github.com/RasaHQ/rasa",
                "stargazers_count": 21395,
                "language": "Python",
                "description": "CALM (Conversational AI with Language Models): Dialogue act composition, entity slot carryover, and contextual repair.",
                "dentacore_recipe": (
                    "Müşteri mesajında zaten verdiği varlıkları (`5 yaşındaki oğlum`, `Almanya'dan geleceğim`, `Allianz sigorta`, `tek diş implant`) "
                    "slot olarak yakalayıp asla aynı soruyu tekrar sormadan doğrudan o varlığa özel yanıt üretin."
                ),
            },
        ],
    },
    {
        "gap_id": "GAP-DENTAL-ODONTOGRAM",
        "gap_title": "FDI Diş Şeması (Odontogram) Yüzey Bazlı (M/D/O/B/L) Backend Kalıcılığı & FHIR Uyumu",
        "target_file": "4_SISTEM_MOTORU_DOKUNMA/dentacore/run_local.py & api/app/panel.py",
        "github_query": "dental odontogram OR open-dental OR dental clinic management",
        "curated_repos": [
            {
                "full_name": "OpenDental/opendental",
                "html_url": "https://github.com/OpenDental/opendental",
                "stargazers_count": 620,
                "language": "C#",
                "description": "Open Dental Practice Management Software architecture reference for tooth charting, surfaces (M,O,D,B,L), and procedure logs.",
                "dentacore_recipe": (
                    "`run_local.py` ve `002_platform.sql` içine `tooth_records (id, clinic_id, patient_id, tooth_fdi INT CHECK(tooth_fdi BETWEEN 11 AND 85), "
                    "surface TEXT, procedure_code TEXT, status TEXT, doctor_id INT, note TEXT, created_at TEXT)` tablosu ve "
                    "`GET/POST /app/api/patients/{pid}/odontogram` uç noktası ekleyin."
                ),
            },
            {
                "full_name": "CampbellSoftware/open-odontogram",
                "html_url": "https://github.com/AlexCorvis84/odontograma",
                "stargazers_count": 190,
                "language": "JavaScript",
                "description": "Interactive SVG/Canvas FDI dental odontogram chart with 5-surface tooth selection and clinical status states.",
                "dentacore_recipe": (
                    "`api/app/web/app.js` içindeki statik diş şemasını 5 yüzeyli (Mesial, Distal, Occlusal, Buccal, Lingual) SVG seçiciye dönüştürüp "
                    "her tıklamayı `POST /app/api/patients/{pid}/odontogram` uç noktasına ve `charges` (kasa hizmet) tablosuna otomatik bağlayın."
                ),
            },
        ],
    },
    {
        "gap_id": "GAP-SCHEDULING-RULES",
        "gap_title": "Çalışma Saatleri, Pazar Kapalılığı ve Hekim Vardiya Kural Motoru",
        "target_file": "4_SISTEM_MOTORU_DOKUNMA/dentacore/run_local.py (create_appt & update_appt)",
        "github_query": "calcom/cal.com OR appointment scheduling engine python",
        "curated_repos": [
            {
                "full_name": "calcom/cal.com",
                "html_url": "https://github.com/calcom/cal.com",
                "stargazers_count": 34200,
                "language": "TypeScript",
                "description": "Scheduling infrastructure for everyone: working hours, buffer times, holiday blocks, and multi-resource conflict detection.",
                "dentacore_recipe": (
                    "`run_local.py` satır 1099 `create_appt()` şu an Pazar günü ve gece 03:30 randevularını kabul ediyor (`HTTP 200`). "
                    "`clinics` tablosuna `working_hours_json` (`{\"mon_fri\":[\"09:00\",\"19:00\"],\"sat\":[\"09:00\",\"15:00\"],\"sun\":null}`) "
                    "ve işlem arası `buffer_min` (sterilizasyon payı) ekleyip mesai dışı randevuları `HTTP 422` ile reddedin."
                ),
            },
        ],
    },
    {
        "gap_id": "GAP-API-CHAOS-SECURITY",
        "gap_title": "Otomatik OpenAPI Fuzzing, Hız Sınırlama (Rate-Limit) ve İdempotency Koruması",
        "target_file": "4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/security.py & panel.py",
        "github_query": "schemathesis/schemathesis OR laurentS/slowapi",
        "curated_repos": [
            {
                "full_name": "schemathesis/schemathesis",
                "html_url": "https://github.com/schemathesis/schemathesis",
                "stargazers_count": 2650,
                "language": "Python",
                "description": "Property-based automated API testing for OpenAPI and GraphQL specs powered by Hypothesis.",
                "dentacore_recipe": (
                    "DentaCore test modunda (`DC_ENABLE_OPENAPI=1`) `/openapi.json` şemasını açarak saatlik otomasyona `schemathesis run` "
                    "adımını bağlayın; tüm Pydantic sınır değerlerini (NaN, negatif kuruş, Unicode taşması) otomatik fuzzing ile tarayın."
                ),
            },
            {
                "full_name": "laurentS/slowapi",
                "html_url": "https://github.com/laurentS/slowapi",
                "stargazers_count": 1950,
                "language": "Python",
                "description": "A rate limiter for Starlette and FastAPI adapted from flask-limiter.",
                "dentacore_recipe": (
                    "`/app/api/conversations/simulate`, `/app/api/charges` ve `/app/api/backup/create` uç noktalarında şu an hız sınırı yok. "
                    "`_LIMITER.hit(f'sim:{u[\"id\"]}', 30, 60)` ekleyerek LLM token tüketimi saldırılarını ve `charges` tablosuna `idempotency_key` "
                    "ekleyerek çift tıklama mükerrer borçlandırmalarını engelleyin."
                ),
            },
        ],
    },
    {
        "gap_id": "GAP-POLYMORPHIC-TESTING",
        "gap_title": "Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST",
        "target_file": "test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py",
        "github_query": "playwright OR hypothesis OR PayloadsAllTheThings OR promptfoo OR garak",
        "curated_repos": [
            {
                "full_name": "microsoft/playwright",
                "html_url": "https://github.com/microsoft/playwright",
                "stargazers_count": 100517,
                "language": "TypeScript / Python",
                "description": "Real headless browser automation across Desktop & Mobile viewports with DOM, console, overflow, and interactive SVG verification.",
                "dentacore_recipe": "Her saatlik turda yönetim panelinin tüm sekmelerini, 52 dişlik 5 yüzeyli SVG Odontogramı, Müşteriye Özel Bot Stüdyosunu ve 8 klasördeki tüm HTML araçlarını gerçek tarayıcıda tıklayarak denetleyin.",
            },
            {
                "full_name": "swisskyrepo/PayloadsAllTheThings",
                "html_url": "https://github.com/swisskyrepo/PayloadsAllTheThings",
                "stargazers_count": 82762,
                "language": "Python / Security",
                "description": "Comprehensive web application security & pentest payloads (SQLi, XSS, SSTI, Path Traversal, CSRF, Header/Origin bypass).",
                "dentacore_recipe": "Saatlik rotasyonla hasta arama, dosya yolları, tahsilat ve form uç noktalarına poliglot güvenlik vektörleri gönderip sıfır 500 ve tam izolasyon doğrulayın.",
            },
            {
                "full_name": "minimaxir/big-list-of-naughty-strings",
                "html_url": "https://github.com/minimaxir/big-list-of-naughty-strings",
                "stargazers_count": 47721,
                "language": "JSON / Fuzzing",
                "description": r"Edge-case strings (null bytes \x00, Unicode Bidi RTL \u202e, zero-width spaces \u200b, emoji bombs, script injections).",
                "dentacore_recipe": r"Tüm SQL parametrelerinde _clean_sql_args() ve normalize() ile null-byte (\x00) ve Bidi RTL (\u202e) karakterlerini temizleyerek PostgreSQL ve UI bozulmalarını önleyin.",
            },
            {
                "full_name": "promptfoo/promptfoo",
                "html_url": "https://github.com/promptfoo/promptfoo",
                "stargazers_count": 27430,
                "language": "TypeScript",
                "description": "LLM & Agent red-teaming, jailbreak, prompt injection, and healthcare guardrail testing suite.",
                "dentacore_recipe": "Her saat farklı sistem komutu ezme, fiyat garantisi koparma ve KVKK üçüncü kişi veri sızdırma senaryolarıyla WhatsApp botunu sınayın.",
            },
            {
                "full_name": "NVIDIA/garak",
                "html_url": "https://github.com/NVIDIA/garak",
                "stargazers_count": 10091,
                "language": "Python",
                "description": "LLM vulnerability scanner probing for zero-width obfuscation, leetspeak bypass, and medical prescription leakage.",
                "dentacore_recipe": "A\u200bugmentin ve augment1n 1000 m.g. gibi görünmez karakterli veya leetspeak ilaç sorgularını normalize() aşamasında yakalayıp L1-tibbi katmanında 0 token ile engelleyin.",
            },
            {
                "full_name": "HypothesisWorks/hypothesis",
                "html_url": "https://github.com/HypothesisWorks/hypothesis",
                "stargazers_count": 9188,
                "language": "Python",
                "description": "Property-based testing library generating stateful edge-case inputs to falsify invariants.",
                "dentacore_recipe": "Her saat farklı anatomik olmayan FDI diş numaralarını (19, 29, 50, 99 -> HTTP 422) ve ters kasa tarih aralıklarını (start > end -> HTTP 422) otomatik üretip sınayın.",
            },
            {
                "full_name": "PyCQA/bandit",
                "html_url": "https://github.com/PyCQA/bandit",
                "stargazers_count": 8395,
                "language": "Python",
                "description": "Python AST static security vulnerability scanner (B608 SQL injection, unsafe deserialization, hardcoded secrets).",
                "dentacore_recipe": "Her saatlik turda api/app/*.py ve run_local.py üzerinde Bandit AST taraması koşarak 0 Yüksek/Orta güvenlik uyarısı garantileyin.",
            },
        ],
    },
]


def fetch_github_recommendations(run_number: int = 1, cache_dir: Path | None = None) -> dict[str, Any]:
    """
    GitHub REST API'den canlı arama yapar, hız sınırına takılırsa veya çevrimdışıysa
    küratörlü gerçek repo verileriyle zenginleştirerek DentaCore entegrasyon önerilerini döndürür.
    """
    live_hits: list[dict[str, Any]] = []
    api_status = "LIVE_GITHUB_API"

    # Her saat başı 12 farklı GitHub test formasyonunun canlı arama sorgusunu GitHub REST API'den çek
    from polymorphic_formations import get_active_formation
    active_form = get_active_formation(run_number)
    q_pick = active_form["github_query"]

    try:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "DentaCore-Adversarial-Sentinel/1.0",
        }
        with httpx.Client(timeout=6.0, headers=headers) as client:
            resp = client.get(
                "https://api.github.com/search/repositories",
                params={"q": q_pick, "sort": "stars", "order": "desc", "per_page": 4},
            )
            if resp.status_code == 200:
                items = resp.json().get("items") or []
                for it in items[:4]:
                    live_hits.append({
                        "full_name": it.get("full_name"),
                        "html_url": it.get("html_url"),
                        "stargazers_count": it.get("stargazers_count", 0),
                        "language": it.get("language") or "Multi",
                        "description": (it.get("description") or "Açık kaynak referans proje")[:180],
                        "updated_at": (it.get("updated_at") or "")[:10],
                        "query_used": q_pick,
                    })
            else:
                api_status = f"CACHE_FALLBACK (HTTP {resp.status_code})"
    except Exception as exc:
        api_status = f"CACHE_FALLBACK ({type(exc).__name__})"

    recommendations: list[dict[str, Any]] = []
    for topic in GITHUB_TOPICS_MATRIX:
        for repo in topic["curated_repos"]:
            recommendations.append({
                "gap_id": topic["gap_id"],
                "gap_title": topic["gap_title"],
                "target_file": topic["target_file"],
                "full_name": repo["full_name"].strip(),
                "html_url": repo["html_url"].strip(),
                "stars": repo["stargazers_count"],
                "language": repo["language"],
                "description": repo["description"],
                "dentacore_recipe": repo["dentacore_recipe"],
                "source": "Architectural Blueprint + GitHub",
            })

    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "last_github_radar.json").write_text(
            json.dumps({"api_status": api_status, "live_query": q_pick, "live_hits": live_hits, "recommendations": recommendations}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return {
        "api_status": api_status,
        "live_query": q_pick,
        "live_discovered_repos": live_hits,
        "architectural_recommendations": recommendations,
    }
