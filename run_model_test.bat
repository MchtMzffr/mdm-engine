@echo off
REM Tek test: Dashboard senaryolari rasgele sirada; model dogru calisiyor mu?
set PYEXE=C:\Users\tsgal\AppData\Local\Programs\Python\Python312\python.exe
if not exist "%PYEXE%" (
  echo Python bulunamadi. PYEXE yolunu duzenleyin.
  pause
  exit /b 1
)
cd /d "%~dp0"
echo Tek test: Dashboard senaryolari (rasgele sirada)...
"%PYEXE%" tests/test_dashboard_scenarios.py
if errorlevel 1 (
  echo TEST BASARISIZ.
  pause
  exit /b 1
)
echo.
echo Model dogru calisiyor.
pause
