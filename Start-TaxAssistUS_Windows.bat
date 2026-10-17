@echo off
rem Tax Assist US launcher for Windows. Double-click it.
cd /d "%~dp0"
rem Double-click: open the page.  "Start-TaxAssistUS_Windows.bat serve": serve at http://127.0.0.1:8765
set "TA_ARGS=%*"
if "%~1"=="" set "TA_ARGS=start"
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 tools\taxassist.py %TA_ARGS%
  if not errorlevel 1 goto done
)
python -c "import sys; sys.exit(sys.version_info < (3, 8))" >nul 2>nul
if %errorlevel%==0 (
  python tools\taxassist.py %TA_ARGS%
  goto done
)
echo Python 3.8 or newer wasn't found, so folder views and the inbox count won't show.
echo Install it from https://www.python.org/downloads/ (tick "Add python.exe to PATH")
echo   or run:  winget install Python.Python.3.13
echo Then double-click this again.
echo Opening the page anyway: profile, estimate and CSV loading still work.
start "" "%~dp0TaxAssistUS.html"
pause
exit /b
:done
timeout /t 3 >nul
