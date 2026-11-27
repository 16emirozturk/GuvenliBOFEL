@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Guvenli Okul - Yonetici ve Kurucu Secrets olusturucu
echo Parolalar ekranda gorunmez ve dosyaya kaydedilmez.
echo.
py olustur_secrets.py
if errorlevel 1 (
  echo.
  echo Python Launcher bulunamadi; python komutu deneniyor...
  python olustur_secrets.py
)
echo.
pause
