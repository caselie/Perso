@echo off
REM Demarre la borne sous Windows : serveur local + navigateur plein ecran.
setlocal
set RACINE=%~dp0..
set PORT=8080
cd /d "%RACINE%"

if not exist .venv (
  echo Creation de l'environnement Python...
  python -m venv .venv
  .venv\Scripts\pip install --quiet --upgrade pip
  .venv\Scripts\pip install --quiet -r requirements.txt
)

start "Borne flechettes" /min .venv\Scripts\python -m app.server --port %PORT%
timeout /t 3 /nobreak >nul

set NAV=
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set NAV=%ProgramFiles%\Google\Chrome\Application\chrome.exe
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set NAV=%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" if "%NAV%"=="" set NAV=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe

if "%NAV%"=="" (
  echo Aucun navigateur trouve. Ouvrez http://127.0.0.1:%PORT% manuellement.
  pause
) else (
  "%NAV%" --kiosk --noerrdialogs --disable-infobars --user-data-dir="%RACINE%\data\navigateur" http://127.0.0.1:%PORT%
)
endlocal
