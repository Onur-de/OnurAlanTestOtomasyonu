@echo off
chcp 65001 >nul
title DentaCore - Hemen Dusman Simulasyonu Calistir ve Not Ekle
echo ===============================================================================
echo [DENTACORE ADVERSARIAL SENTINEL] DERIN DUSMAN SIMULASYONU BASLATILIYOR...
echo Hedef: C:\Users\onura\OneDrive\Masaüstü\Gerçek kurumsal otomasyon
echo ===============================================================================
"C:\Users\onura\anaconda3\python.exe" -X utf8 "%~dp0motor\adversarial_engine.py" --turns 1
echo.
echo [OK] Yeni saatlik karne SAATLIK_NOT_VE_EKSIK_DEFTERI.md dosyasina eklendi!
start "" "%~dp0canli_denetim_paneli.html"
pause
