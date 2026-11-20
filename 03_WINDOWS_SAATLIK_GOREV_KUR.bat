@echo off
chcp 65001 >nul
title DentaCore - Windows Saatlik Otomatik Gorev Zamanlayici Kurulumu
echo ===============================================================================
echo Windows Gorev Zamanlayici'ya (Task Scheduler) saat basi otomatik calisacak
echo "DentaCore_Saatlik_Dusman_Test_Otomasyonu" gorevi kaydediliyor...
echo ===============================================================================
schtasks /Create /F /SC HOURLY /MO 1 /TN "DentaCore_Saatlik_Dusman_Test_Otomasyonu" /TR "\"%~dp0motor\saatlik_gorev.bat\""
echo.
echo [OK] Gorev basariyla kuruldu! Bilgisayar acik oldugu surece her saat basi
echo arka planda otomatik calisip SAATLIK_NOT_VE_EKSIK_DEFTERI.md dosyasina not ekleyecek.
pause
