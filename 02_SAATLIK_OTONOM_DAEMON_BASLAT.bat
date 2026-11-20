@echo off
chcp 65001 >nul
title DentaCore - Saatlik Otonom Dusman Simulasyon Daemon ve Canli Sunucu
echo ===============================================================================
echo [DENTACORE ADVERSARIAL SENTINEL] SAATLIK OTONOM DAEMON + CANLI PANEL (8795)
echo Her 60 dakikada bir Kurumsal-Otomasyon-Sistemi'ni derinden test eder,
echo WhatsApp botunu oylar, GitHub repolarini tarar ve not defterine ekler.
echo ===============================================================================
start "DentaCore Canli Denetim Sunucusu" /min "C:\Users\onura\anaconda3\python.exe" -X utf8 "%~dp0motor\dashboard_server.py"
start "" "http://127.0.0.1:8795"
"C:\Users\onura\anaconda3\python.exe" -X utf8 "%~dp0motor\adversarial_engine.py" --daemon --interval-min 60
