@echo off
chcp 65001 >nul
"C:\Users\onura\anaconda3\python.exe" -X utf8 "%~dp0adversarial_engine.py" --turns 1 >> "%~dp0..\veri\saatlik_gorev.log" 2>&1
