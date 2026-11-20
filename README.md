# OnurAlanTestOtomasyonu

Bağımsız, 7/24 çalışan kurumsal test ve güvenlik otomasyonu motoru. Diğer tüm projelerden ayrı olarak kendi deposunda çalışır; bilgisayar kapalıyken bile GitHub Actions üzerinde saat başı çalışarak sonuçları canlı Komuta Merkezi panelinde yayınlar.

## Canlı Komuta Merkezi (GitHub Pages)
- **Canlı Panel:** https://onur-de.github.io/OnurAlanTestOtomasyonu/
- **Birleşik Komuta Merkezi:** [BIRLESIK_KOMUTA_MERKEZI.html](BIRLESIK_KOMUTA_MERKEZI.html)
- **Düşman Simülasyon Paneli:** [canli_denetim_paneli.html](canli_denetim_paneli.html)

## 5 Kurumsal Otomasyon Kapısı
1. **Canlı Docker PostgreSQL 17 (`motor/pg_docker_engine.py`):** Geçici konteynerde DDL, 10 paralel ACID çakışma kilidi (`1 commit / 9 conflict`), ROLLBACK atomikliği ve tablo paritesi.
2. **DevSecOps Tarayıcıları (`motor/devsecops_local_scanners.py`):** Docker Gitleaks (temiz repo + sahte sır yakalama kanıtı), OpenAPI Fuzzing & Schemathesis (kasıtlı 500 yakalama kanıtı), OWASP ASVS L2 başlık + Docker OWASP ZAP Baseline, Ruff ve Bandit SAST.
3. **Klinik L3 LLM Red-Team (`motor/live_llm_redteam.py`):** Yerelde OmniRoute üzerinden canlı LLM taraması, bulutta 10 maddelik deterministik doz/enjeksiyon/KVKK/fiyat sızıntısı yakalama kalkanı.
4. **Gerçek `k6` Yük/Soak & `psutil` Bellek Sızıntısı (`motor/k6_soak_memory_engine.py`):** Eşzamanlı VU yük testi (`RPS`, `p50/p95/p99`) + sunucu PID RAM/FD/CPU artış eğimi.
5. **Birleşik Komuta Merkezi (`motor/unified_control_center.py`):** En üstte en yeni tarih/saat + hata/eksik/bulgu akışı, sıfır çakışmalı yerel/bulut log birleştirme ve Playwright masaüstü (`1440x900`) & mobil (`390x844`) görsel doğrulama.

## Hızlı Çalıştırma
```bash
# Yerel tam öz-test (12/12 doğrulama)
python motor/adversarial_engine.py --self-test

# Bulut CI hızlı mod (GitHub Actions saatlik koşu)
python motor/adversarial_engine.py --ci-fast
```
