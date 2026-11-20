# DENTACORE v8.0 : SAATLİK DÜŞMAN SİMÜLASYONU, WHATSAPP JÜRİ VE BULGU DEFTERİ

> **Yeni Çalışma Düzeni:** Eski kayıtlar sıfırlandı. Bu saatten itibaren her koşunun **saati, hataları, eksikleri ve bulguları sayfanın en üstünde (en yeni en üstte)** yer alır.

## CANLI SAAT, HATA, EKSİK VE BULGU ZAMAN ÇİZELGESİ (EN YENİ EN ÜSTTE)

| Tarih ve Saat | Tur | Genel Not | Bulgu / Eksik | Yakalanan Hata, Eksik ve Bulgular |
| :--- | :---: | :---: | :---: | :--- |
| `2026-11-20 04:00:01` | **Tur #2** | **98.6/100 (A)** | **2** | [FAZ5-PARITY-01/Orta] 4_SISTEM <-> 5_KALICI Bulut Deposu Güvenlik & Yapılandırma Paritesi; [FOLDER-AUDIT-01/Yüksek] 8 Ana Klasör, 9 Satış Dosyası (MP4/PPTX/XLSX/PDF/DOCX), 19 HTML ve 64 Python Dosyası Bütünlük Testi |
| `2026-11-20 03:47:04` | **Tur #1** | **98.6/100 (A)** | **2** | [FAZ5-PARITY-01/Orta] 4_SISTEM <-> 5_KALICI Bulut Deposu Güvenlik & Yapılandırma Paritesi; [FOLDER-AUDIT-01/Yüksek] 8 Ana Klasör, 9 Satış Dosyası (MP4/PPTX/XLSX/PDF/DOCX), 19 HTML ve 64 Python Dosyası Bütünlük Testi |

<!-- RUNS_START -->

## SAATLİK DENETİM TURU #2 : `RUN-20261120-040001-T02` (2026-11-20 04:00:01)

### 1. Genel Karne ve Önceki Tura Göre Değişim
- **Genel Düşman Denetim Notu:** **`98.6 / 100`** (**Harf Notu: `A`** : *Mükemmel / Üretime Tam Hazır*)
- **Önceki Tura Göre Değişim:** `+0.0 puan` | **Toplam Birikimli Tur Sayısı:** `2`
- **Koşulan Derin Kontrol & Saldırı:** `37` senaryo (`35` tam geçiş, `2` yakalanan eksik/hata)

| Alt Sistem / Denetim Alanı | Puan (100) | Durum Özeti |
| :--- | :---: | :--- |
| **1. Gerçek Müşteri & Hasta Yolculuğu** | **`100.0`** | Lead, hasta kaydı, KVKK anamnez, bekleme listesi ve post-op radar akışları |
| **2. Eşzamanlılık & Yarış (Concurrency Race)** | **`100.0`** | 10 paralel koltuk yarışı, hekim çakışması, 8 paralel stok düşümü, 700+ sürü |
| **3. Red-Team Siber Güvenlik & FAZ 1-5** | **`100.0`** | IDOR, RBAC, CSRF, SQLi/Traversal, ASVS, Docker/Starlette, FAZ 2 AI Kalkanı |
| **4. Düşman İş Mantığı & Bulut Paritesi** | **`91.4`** | Mesai/Pazar kilidi, arşivli hasta, Odontogram, WA Webhook, bulut paritesi |
| **5. WhatsApp Bot Jüri Genel Oylaması** | **`100.0`** | `64` müşteri/düşman sorusu (`64` geçti, `0` puan kırdı) |
| **6. 16 Dil, Yazım Hatası & Çok Turlu Hafıza** | **`100.0`** | Niyet: `100.0` · Tıbbi Güvenlik: `100.0` · 16 Dil: `100.0` · Hafıza: `100.0` · Typo: `100.0` · KVKK: `100.0` |

---

### 2. Yakalanan Hatalar, Eksikler ve Zafiyetler (`2` Bulgu)

| Kod | Önem | Alan | Tespit Edilen Eksik / Hata Başlığı | Dosya / Konum | Kanıt (Canlı Simülasyon Çıktısı) | Çözüm Reçetesi |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| `FAZ5-PARITY-01` | **Orta** | Düşman İş Mantığı | 4_SISTEM <-> 5_KALICI Bulut Deposu Güvenlik & Yapılandırma Paritesi | `5_KALICI_GITHUB_VE_BULUT_KURULUMU/*` | 5_KALICI_GITHUB_VE_BULUT_KURULUMU içinde eksik: .dockerignore, litestream.yml.example, pyproject.toml | Eksik dosyalar 4_SISTEM_MOTORU_DOKUNMA/dentacore içinden 5_KALICI köküne bayt bayt kopyalanmalıdır. |
| `FOLDER-AUDIT-01` | **Yüksek** | Tam Klasör & Dosya Denetimi | 8 Ana Klasör, 9 Satış Dosyası (MP4/PPTX/XLSX/PDF/DOCX), 19 HTML ve 64 Python Dosyası Bütünlük Testi | `Kurumsal-Otomasyon-Sistemi/* (8 Klasör)` | Klasörler=8/8, Rehberler=8/8, SatışVarlıkları=9/9, KırıkLink=2, PyCompile=64/64 | 1_Birebir_Tanitim_Sitesi.html -> manifest.webmanifest; 2_Birebir_Yonetim_Paneli.html -> manifest.webmanifest |

---

### 3. WhatsApp Bot Jüri Oylaması (En Zayıf Yanıtlar)

| Soru Kodu | Kategori | Müşteri / Düşman Sorusu | Botun Verdiği Yanıt | Jüri Puanı | Jüri Eleştirisi |
| :--- | :--- | :--- | :--- | :---: | :--- |


---

### 4. GitHub Açık Kaynak Repo Radarı (`LIVE_GITHUB_API`)

**Canlı GitHub API Keşifleri (`Sorgu: PayloadsAllTheThings OR owasp api security fuzzing python`):**
- **[cirosantilli/china-dictatorship](https://github.com/cirosantilli/china-dictatorship)** (3355 ★ | `HTML`): 反中共政治宣传库。Anti Chinese government propaganda. 住在中国真名用户的网友请别给星星，不然你要被警察请喝茶。常见问答集，新闻集和饭店和音乐建议。卐习万岁卐。冠状病毒审查郝海东新疆改造中心六四事件法轮功 996.ICU709大抓捕巴拿马文件邓家贵低端人口西藏骚乱。Friends who live in China and 
- **[gege-circle/.github](https://github.com/gege-circle/.github)** (2110 ★ | `Multi`): 这里是GitHub的草场，也是戈戈圈爱好者的交流地，主要讨论动漫、游戏、科技、人文、生活等所有话题，欢迎各位小伙伴们在此讨论趣事。This is GitHub grassland, and the community place for Gege circle lovers, mainly discusses anime, games, technology
- **[cirosantilli/china-dictatroship-7](https://github.com/cirosantilli/china-dictatroship-7)** (388 ★ | `HTML`): 反中共政治宣传库。Anti Chinese government propaganda. https://github.com/cirosantilli/china-dictatorship 的备份backup. 住在中国真名用户的网友请别给星星，不然你要被警察请喝茶。常见问答集，新闻集和饭店和音乐建议。卐习万岁卐。冠状病毒审查郝海东新疆改造中心六四事件法轮
- **[zszszszsz/.config](https://github.com/zszszszsz/.config)** (371 ★ | `Shell`): # # Automatically generated file; DO NOT EDIT. # OpenWrt Configuration # CONFIG_MODULES=y CONFIG_HAVE_DOT_CONFIG=y # CONFIG_TARGET_sunxi is not set # CONFIG_TARGET_apm821xx is not 

| Önerilen GitHub Reposu | Hedef DentaCore Dosyası | Kapatacağı Eksik | DentaCore Mimari Reçetesi | Bağlantı |
| :--- | :--- | :--- | :--- | :---: |
| **rapidfuzz/RapidFuzz** (3150 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/router.py & faq.json` | WhatsApp Bot Bulanık Eşleşme (Typo/STT) & Çok Turlu Diyalog Hafızası | `router.py` içindeki `TokenRouter.route()` fonksiyonunda `L1-acil` ve `L1-sss` regex taraması başarısız olduğunda `rapidfuzz.fuzz.token_set_ratio(n, keyword) >= 82` kontrolü ekleyin. Böylece müşteri 'inpilant fyatı nekadr' veya 'kanma durmuyo yuzm sisti' yazdığında 0 LLM tokenı ile L1 katmanında anında yakalanır. | [Repo](https://github.com/rapidfuzz/RapidFuzz) |
| **pytransitions/transitions** (6100 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/router.py & faq.json` | WhatsApp Bot Bulanık Eşleşme (Typo/STT) & Çok Turlu Diyalog Hafızası | `router.py` şu an tamamen durumsuz (stateless) çalışıyor. Her `patient_id` için son 3 mesajın niyetini ve durumunu (`IDLE -> ASKED_TREATMENT -> OFFERED_APPT -> AWAITING_SLOT`) Redis/SQLite üzerinde `transitions` durum makinesiyle tutun. Müşteri 'Olur yarın 15:00 uygun mu?' dediğinde önceki mesajın randevu teklifi olduğunu anlayıp doğrudan randevu akışına bağlayın. | [Repo](https://github.com/pytransitions/transitions) |
| **emcie-co/parlant** (18335 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/router.py & faq.json` | WhatsApp Bot Bulanık Eşleşme (Typo/STT) & Çok Turlu Diyalog Hafızası | `router.py` içindeki `_compose_parlant_concierge_reply()` ile statik şablonları 4-katmanlı VIP Hasta Koordinatörü mimarisine (1. Samimi & Resmi Karşılama, 2. Hastanın Sorduğu Tedavi/Çocuk Yaşı/Ülke/Nakit İsteğini Yansıtma, 3. Kliniğe Özel `ai_custom_rules_json` Politika Enjeksiyonu, 4. Değer Hissettiren Nazik Randevu Daveti) dönüştürün. | [Repo](https://github.com/emcie-co/parlant) |
| **chatwoot/chatwoot** (40115 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/router.py & faq.json` | WhatsApp Bot Bulanık Eşleşme (Typo/STT) & Çok Turlu Diyalog Hafızası | WhatsApp ve Instagram DM kanallarında resmi-samimi hasta koordinatörü ses tonu, şikayet ve ağrı bildirimlerinde empatik yatıştırma ve başhekimlik/uzman hekim devri (`handoff=True`) akışını işletin. | [Repo](https://github.com/chatwoot/chatwoot) |
| **RasaHQ/rasa** (21395 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/router.py & faq.json` | WhatsApp Bot Bulanık Eşleşme (Typo/STT) & Çok Turlu Diyalog Hafızası | Müşteri mesajında zaten verdiği varlıkları (`5 yaşındaki oğlum`, `Almanya'dan geleceğim`, `Allianz sigorta`, `tek diş implant`) slot olarak yakalayıp asla aynı soruyu tekrar sormadan doğrudan o varlığa özel yanıt üretin. | [Repo](https://github.com/RasaHQ/rasa) |
| **OpenDental/opendental** (620 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/run_local.py & api/app/panel.py` | FDI Diş Şeması (Odontogram) Yüzey Bazlı (M/D/O/B/L) Backend Kalıcılığı & FHIR Uyumu | `run_local.py` ve `002_platform.sql` içine `tooth_records (id, clinic_id, patient_id, tooth_fdi INT CHECK(tooth_fdi BETWEEN 11 AND 85), surface TEXT, procedure_code TEXT, status TEXT, doctor_id INT, note TEXT, created_at TEXT)` tablosu ve `GET/POST /app/api/patients/{pid}/odontogram` uç noktası ekleyin. | [Repo](https://github.com/OpenDental/opendental) |
| **CampbellSoftware/open-odontogram** (190 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/run_local.py & api/app/panel.py` | FDI Diş Şeması (Odontogram) Yüzey Bazlı (M/D/O/B/L) Backend Kalıcılığı & FHIR Uyumu | `api/app/web/app.js` içindeki statik diş şemasını 5 yüzeyli (Mesial, Distal, Occlusal, Buccal, Lingual) SVG seçiciye dönüştürüp her tıklamayı `POST /app/api/patients/{pid}/odontogram` uç noktasına ve `charges` (kasa hizmet) tablosuna otomatik bağlayın. | [Repo](https://github.com/AlexCorvis84/odontograma) |
| **calcom/cal.com** (34200 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/run_local.py (create_appt & update_appt)` | Çalışma Saatleri, Pazar Kapalılığı ve Hekim Vardiya Kural Motoru | `run_local.py` satır 1099 `create_appt()` şu an Pazar günü ve gece 03:30 randevularını kabul ediyor (`HTTP 200`). `clinics` tablosuna `working_hours_json` (`{"mon_fri":["09:00","19:00"],"sat":["09:00","15:00"],"sun":null}`) ve işlem arası `buffer_min` (sterilizasyon payı) ekleyip mesai dışı randevuları `HTTP 422` ile reddedin. | [Repo](https://github.com/calcom/cal.com) |
| **schemathesis/schemathesis** (2650 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/security.py & panel.py` | Otomatik OpenAPI Fuzzing, Hız Sınırlama (Rate-Limit) ve İdempotency Koruması | DentaCore test modunda (`DC_ENABLE_OPENAPI=1`) `/openapi.json` şemasını açarak saatlik otomasyona `schemathesis run` adımını bağlayın; tüm Pydantic sınır değerlerini (NaN, negatif kuruş, Unicode taşması) otomatik fuzzing ile tarayın. | [Repo](https://github.com/schemathesis/schemathesis) |
| **laurentS/slowapi** (1950 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/security.py & panel.py` | Otomatik OpenAPI Fuzzing, Hız Sınırlama (Rate-Limit) ve İdempotency Koruması | `/app/api/conversations/simulate`, `/app/api/charges` ve `/app/api/backup/create` uç noktalarında şu an hız sınırı yok. `_LIMITER.hit(f'sim:{u["id"]}', 30, 60)` ekleyerek LLM token tüketimi saldırılarını ve `charges` tablosuna `idempotency_key` ekleyerek çift tıklama mükerrer borçlandırmalarını engelleyin. | [Repo](https://github.com/laurentS/slowapi) |
| **microsoft/playwright** (100517 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Her saatlik turda yönetim panelinin tüm sekmelerini, 52 dişlik 5 yüzeyli SVG Odontogramı, Müşteriye Özel Bot Stüdyosunu ve 8 klasördeki tüm HTML araçlarını gerçek tarayıcıda tıklayarak denetleyin. | [Repo](https://github.com/microsoft/playwright) |
| **swisskyrepo/PayloadsAllTheThings** (82762 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Saatlik rotasyonla hasta arama, dosya yolları, tahsilat ve form uç noktalarına poliglot güvenlik vektörleri gönderip sıfır 500 ve tam izolasyon doğrulayın. | [Repo](https://github.com/swisskyrepo/PayloadsAllTheThings) |
| **minimaxir/big-list-of-naughty-strings** (47721 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Tüm SQL parametrelerinde _clean_sql_args() ve normalize() ile null-byte (\x00) ve Bidi RTL (\u202e) karakterlerini temizleyerek PostgreSQL ve UI bozulmalarını önleyin. | [Repo](https://github.com/minimaxir/big-list-of-naughty-strings) |
| **promptfoo/promptfoo** (27430 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Her saat farklı sistem komutu ezme, fiyat garantisi koparma ve KVKK üçüncü kişi veri sızdırma senaryolarıyla WhatsApp botunu sınayın. | [Repo](https://github.com/promptfoo/promptfoo) |
| **NVIDIA/garak** (10091 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | A​ugmentin ve augment1n 1000 m.g. gibi görünmez karakterli veya leetspeak ilaç sorgularını normalize() aşamasında yakalayıp L1-tibbi katmanında 0 token ile engelleyin. | [Repo](https://github.com/NVIDIA/garak) |
| **HypothesisWorks/hypothesis** (9188 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Her saat farklı anatomik olmayan FDI diş numaralarını (19, 29, 50, 99 -> HTTP 422) ve ters kasa tarih aralıklarını (start > end -> HTTP 422) otomatik üretip sınayın. | [Repo](https://github.com/HypothesisWorks/hypothesis) |
| **PyCQA/bandit** (8395 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Her saatlik turda api/app/*.py ve run_local.py üzerinde Bandit AST taraması koşarak 0 Yüksek/Orta güvenlik uyarısı garantileyin. | [Repo](https://github.com/PyCQA/bandit) |

---


## SAATLİK DENETİM TURU #1 : `RUN-20261120-034704-T01` (2026-11-20 03:47:04)

### 1. Genel Karne ve Önceki Tura Göre Değişim
- **Genel Düşman Denetim Notu:** **`98.6 / 100`** (**Harf Notu: `A`** : *Mükemmel / Üretime Tam Hazır*)
- **Önceki Tura Göre Değişim:** `İlk Baz Ölçüm` | **Toplam Birikimli Tur Sayısı:** `1`
- **Koşulan Derin Kontrol & Saldırı:** `37` senaryo (`35` tam geçiş, `2` yakalanan eksik/hata)

| Alt Sistem / Denetim Alanı | Puan (100) | Durum Özeti |
| :--- | :---: | :--- |
| **1. Gerçek Müşteri & Hasta Yolculuğu** | **`100.0`** | Lead, hasta kaydı, KVKK anamnez, bekleme listesi ve post-op radar akışları |
| **2. Eşzamanlılık & Yarış (Concurrency Race)** | **`100.0`** | 10 paralel koltuk yarışı, hekim çakışması, 8 paralel stok düşümü, 700+ sürü |
| **3. Red-Team Siber Güvenlik & FAZ 1-5** | **`100.0`** | IDOR, RBAC, CSRF, SQLi/Traversal, ASVS, Docker/Starlette, FAZ 2 AI Kalkanı |
| **4. Düşman İş Mantığı & Bulut Paritesi** | **`91.4`** | Mesai/Pazar kilidi, arşivli hasta, Odontogram, WA Webhook, bulut paritesi |
| **5. WhatsApp Bot Jüri Genel Oylaması** | **`100.0`** | `64` müşteri/düşman sorusu (`64` geçti, `0` puan kırdı) |
| **6. 16 Dil, Yazım Hatası & Çok Turlu Hafıza** | **`100.0`** | Niyet: `100.0` · Tıbbi Güvenlik: `100.0` · 16 Dil: `100.0` · Hafıza: `100.0` · Typo: `100.0` · KVKK: `100.0` |

---

### 2. Yakalanan Hatalar, Eksikler ve Zafiyetler (`2` Bulgu)

| Kod | Önem | Alan | Tespit Edilen Eksik / Hata Başlığı | Dosya / Konum | Kanıt (Canlı Simülasyon Çıktısı) | Çözüm Reçetesi |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| `FAZ5-PARITY-01` | **Orta** | Düşman İş Mantığı | 4_SISTEM <-> 5_KALICI Bulut Deposu Güvenlik & Yapılandırma Paritesi | `5_KALICI_GITHUB_VE_BULUT_KURULUMU/*` | 5_KALICI_GITHUB_VE_BULUT_KURULUMU içinde eksik: .dockerignore, litestream.yml.example, pyproject.toml | Eksik dosyalar 4_SISTEM_MOTORU_DOKUNMA/dentacore içinden 5_KALICI köküne bayt bayt kopyalanmalıdır. |
| `FOLDER-AUDIT-01` | **Yüksek** | Tam Klasör & Dosya Denetimi | 8 Ana Klasör, 9 Satış Dosyası (MP4/PPTX/XLSX/PDF/DOCX), 19 HTML ve 64 Python Dosyası Bütünlük Testi | `Kurumsal-Otomasyon-Sistemi/* (8 Klasör)` | Klasörler=8/8, Rehberler=8/8, SatışVarlıkları=9/9, KırıkLink=2, PyCompile=64/64 | 1_Birebir_Tanitim_Sitesi.html -> manifest.webmanifest; 2_Birebir_Yonetim_Paneli.html -> manifest.webmanifest |

---

### 3. WhatsApp Bot Jüri Oylaması (En Zayıf Yanıtlar)

| Soru Kodu | Kategori | Müşteri / Düşman Sorusu | Botun Verdiği Yanıt | Jüri Puanı | Jüri Eleştirisi |
| :--- | :--- | :--- | :--- | :---: | :--- |


---

### 4. GitHub Açık Kaynak Repo Radarı (`LIVE_GITHUB_API`)

**Canlı GitHub API Keşifleri (`Sorgu: schemathesis OR hypothesis property based testing python`):**
- **[HypothesisWorks/hypothesis](https://github.com/HypothesisWorks/hypothesis)** (9193 ★ | `Python`): The property-based testing library for Python
- **[caijiahao/springMvcPlusMongo](https://github.com/caijiahao/springMvcPlusMongo)** (168 ★ | `HTML`): 慕课网 首页 实战 路径 猿问 手记 登录 注册 11.11 Python  手记 \ 史上最全，最详idea搭建springdata+mongoDB+maven+springmvc 史上最全，最详idea搭建springdata+mongoDB+maven+springmvc 原创 2016-10-21 10:54:297759浏览2评论 作为IT届的小弟
- **[KalyanM45/End-to-End-Airbnb-Price-Prediction](https://github.com/KalyanM45/End-to-End-Airbnb-Price-Prediction)** (79 ★ | `Jupyter Notebook`): The purpose of this project is to predict the price of Airbnb rentals based on various features of the properties listed on the platform. The code in this repository is written in 
- **[nanofuzz/nanofuzz](https://github.com/nanofuzz/nanofuzz)** (53 ★ | `TypeScript`): NaNofuzz is a fast and easy-to-use automatic test suite generator for TypeScript, Python, Rust, Go, and Java that runs inside VS Code and supports fuzz, example, and property-based

| Önerilen GitHub Reposu | Hedef DentaCore Dosyası | Kapatacağı Eksik | DentaCore Mimari Reçetesi | Bağlantı |
| :--- | :--- | :--- | :--- | :---: |
| **rapidfuzz/RapidFuzz** (3150 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/router.py & faq.json` | WhatsApp Bot Bulanık Eşleşme (Typo/STT) & Çok Turlu Diyalog Hafızası | `router.py` içindeki `TokenRouter.route()` fonksiyonunda `L1-acil` ve `L1-sss` regex taraması başarısız olduğunda `rapidfuzz.fuzz.token_set_ratio(n, keyword) >= 82` kontrolü ekleyin. Böylece müşteri 'inpilant fyatı nekadr' veya 'kanma durmuyo yuzm sisti' yazdığında 0 LLM tokenı ile L1 katmanında anında yakalanır. | [Repo](https://github.com/rapidfuzz/RapidFuzz) |
| **pytransitions/transitions** (6100 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/router.py & faq.json` | WhatsApp Bot Bulanık Eşleşme (Typo/STT) & Çok Turlu Diyalog Hafızası | `router.py` şu an tamamen durumsuz (stateless) çalışıyor. Her `patient_id` için son 3 mesajın niyetini ve durumunu (`IDLE -> ASKED_TREATMENT -> OFFERED_APPT -> AWAITING_SLOT`) Redis/SQLite üzerinde `transitions` durum makinesiyle tutun. Müşteri 'Olur yarın 15:00 uygun mu?' dediğinde önceki mesajın randevu teklifi olduğunu anlayıp doğrudan randevu akışına bağlayın. | [Repo](https://github.com/pytransitions/transitions) |
| **emcie-co/parlant** (18335 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/router.py & faq.json` | WhatsApp Bot Bulanık Eşleşme (Typo/STT) & Çok Turlu Diyalog Hafızası | `router.py` içindeki `_compose_parlant_concierge_reply()` ile statik şablonları 4-katmanlı VIP Hasta Koordinatörü mimarisine (1. Samimi & Resmi Karşılama, 2. Hastanın Sorduğu Tedavi/Çocuk Yaşı/Ülke/Nakit İsteğini Yansıtma, 3. Kliniğe Özel `ai_custom_rules_json` Politika Enjeksiyonu, 4. Değer Hissettiren Nazik Randevu Daveti) dönüştürün. | [Repo](https://github.com/emcie-co/parlant) |
| **chatwoot/chatwoot** (40115 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/router.py & faq.json` | WhatsApp Bot Bulanık Eşleşme (Typo/STT) & Çok Turlu Diyalog Hafızası | WhatsApp ve Instagram DM kanallarında resmi-samimi hasta koordinatörü ses tonu, şikayet ve ağrı bildirimlerinde empatik yatıştırma ve başhekimlik/uzman hekim devri (`handoff=True`) akışını işletin. | [Repo](https://github.com/chatwoot/chatwoot) |
| **RasaHQ/rasa** (21395 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/router.py & faq.json` | WhatsApp Bot Bulanık Eşleşme (Typo/STT) & Çok Turlu Diyalog Hafızası | Müşteri mesajında zaten verdiği varlıkları (`5 yaşındaki oğlum`, `Almanya'dan geleceğim`, `Allianz sigorta`, `tek diş implant`) slot olarak yakalayıp asla aynı soruyu tekrar sormadan doğrudan o varlığa özel yanıt üretin. | [Repo](https://github.com/RasaHQ/rasa) |
| **OpenDental/opendental** (620 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/run_local.py & api/app/panel.py` | FDI Diş Şeması (Odontogram) Yüzey Bazlı (M/D/O/B/L) Backend Kalıcılığı & FHIR Uyumu | `run_local.py` ve `002_platform.sql` içine `tooth_records (id, clinic_id, patient_id, tooth_fdi INT CHECK(tooth_fdi BETWEEN 11 AND 85), surface TEXT, procedure_code TEXT, status TEXT, doctor_id INT, note TEXT, created_at TEXT)` tablosu ve `GET/POST /app/api/patients/{pid}/odontogram` uç noktası ekleyin. | [Repo](https://github.com/OpenDental/opendental) |
| **CampbellSoftware/open-odontogram** (190 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/run_local.py & api/app/panel.py` | FDI Diş Şeması (Odontogram) Yüzey Bazlı (M/D/O/B/L) Backend Kalıcılığı & FHIR Uyumu | `api/app/web/app.js` içindeki statik diş şemasını 5 yüzeyli (Mesial, Distal, Occlusal, Buccal, Lingual) SVG seçiciye dönüştürüp her tıklamayı `POST /app/api/patients/{pid}/odontogram` uç noktasına ve `charges` (kasa hizmet) tablosuna otomatik bağlayın. | [Repo](https://github.com/AlexCorvis84/odontograma) |
| **calcom/cal.com** (34200 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/run_local.py (create_appt & update_appt)` | Çalışma Saatleri, Pazar Kapalılığı ve Hekim Vardiya Kural Motoru | `run_local.py` satır 1099 `create_appt()` şu an Pazar günü ve gece 03:30 randevularını kabul ediyor (`HTTP 200`). `clinics` tablosuna `working_hours_json` (`{"mon_fri":["09:00","19:00"],"sat":["09:00","15:00"],"sun":null}`) ve işlem arası `buffer_min` (sterilizasyon payı) ekleyip mesai dışı randevuları `HTTP 422` ile reddedin. | [Repo](https://github.com/calcom/cal.com) |
| **schemathesis/schemathesis** (2650 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/security.py & panel.py` | Otomatik OpenAPI Fuzzing, Hız Sınırlama (Rate-Limit) ve İdempotency Koruması | DentaCore test modunda (`DC_ENABLE_OPENAPI=1`) `/openapi.json` şemasını açarak saatlik otomasyona `schemathesis run` adımını bağlayın; tüm Pydantic sınır değerlerini (NaN, negatif kuruş, Unicode taşması) otomatik fuzzing ile tarayın. | [Repo](https://github.com/schemathesis/schemathesis) |
| **laurentS/slowapi** (1950 ★) | `4_SISTEM_MOTORU_DOKUNMA/dentacore/api/app/security.py & panel.py` | Otomatik OpenAPI Fuzzing, Hız Sınırlama (Rate-Limit) ve İdempotency Koruması | `/app/api/conversations/simulate`, `/app/api/charges` ve `/app/api/backup/create` uç noktalarında şu an hız sınırı yok. `_LIMITER.hit(f'sim:{u["id"]}', 30, 60)` ekleyerek LLM token tüketimi saldırılarını ve `charges` tablosuna `idempotency_key` ekleyerek çift tıklama mükerrer borçlandırmalarını engelleyin. | [Repo](https://github.com/laurentS/slowapi) |
| **microsoft/playwright** (100517 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Her saatlik turda yönetim panelinin tüm sekmelerini, 52 dişlik 5 yüzeyli SVG Odontogramı, Müşteriye Özel Bot Stüdyosunu ve 8 klasördeki tüm HTML araçlarını gerçek tarayıcıda tıklayarak denetleyin. | [Repo](https://github.com/microsoft/playwright) |
| **swisskyrepo/PayloadsAllTheThings** (82762 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Saatlik rotasyonla hasta arama, dosya yolları, tahsilat ve form uç noktalarına poliglot güvenlik vektörleri gönderip sıfır 500 ve tam izolasyon doğrulayın. | [Repo](https://github.com/swisskyrepo/PayloadsAllTheThings) |
| **minimaxir/big-list-of-naughty-strings** (47721 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Tüm SQL parametrelerinde _clean_sql_args() ve normalize() ile null-byte (\x00) ve Bidi RTL (\u202e) karakterlerini temizleyerek PostgreSQL ve UI bozulmalarını önleyin. | [Repo](https://github.com/minimaxir/big-list-of-naughty-strings) |
| **promptfoo/promptfoo** (27430 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Her saat farklı sistem komutu ezme, fiyat garantisi koparma ve KVKK üçüncü kişi veri sızdırma senaryolarıyla WhatsApp botunu sınayın. | [Repo](https://github.com/promptfoo/promptfoo) |
| **NVIDIA/garak** (10091 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | A​ugmentin ve augment1n 1000 m.g. gibi görünmez karakterli veya leetspeak ilaç sorgularını normalize() aşamasında yakalayıp L1-tibbi katmanında 0 token ile engelleyin. | [Repo](https://github.com/NVIDIA/garak) |
| **HypothesisWorks/hypothesis** (9188 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Her saat farklı anatomik olmayan FDI diş numaralarını (19, 29, 50, 99 -> HTTP 422) ve ters kasa tarih aralıklarını (start > end -> HTTP 422) otomatik üretip sınayın. | [Repo](https://github.com/HypothesisWorks/hypothesis) |
| **PyCQA/bandit** (8395 ★) | `test otomasyonu/motor/polymorphic_formations.py & adversarial_engine.py` | Saatlik Çoklu Formasyonlu Gerçek Kullanıcı (Playwright), Hypothesis Fuzzing, Garak AI Red-Team ve Bandit SAST | Her saatlik turda api/app/*.py ve run_local.py üzerinde Bandit AST taraması koşarak 0 Yüksek/Orta güvenlik uyarısı garantileyin. | [Repo](https://github.com/PyCQA/bandit) |

---
