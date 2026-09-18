@echo off
chcp 65001 >nul
setlocal
title Revision automatica

set "VQ=%USERPROFILE%\VideoQA"
set "PY=%VQ%\.venv\Scripts\python.exe"
set "INICIO=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "TAREA=%INICIO%\VideoQA automatico.bat"

if not exist "%PY%" (
  echo   [X] VideoQA no esta instalado todavia.
  echo       Ejecuta primero "Instalar VideoQA.bat".
  pause
  exit /b 1
)

if exist "%TAREA%" (
  del "%TAREA%"
  echo   Revision automatica APAGADA.
  echo   Los videos ya no se revisan solos: usa "Revisar video".
) else (
  >"%TAREA%" echo @echo off
  >>"%TAREA%" echo chcp 65001 ^>nul
  >>"%TAREA%" echo start "" /min "%PY%" -m videoqa_win.cli watch
  echo   Revision automatica ENCENDIDA.
  echo   Desde ahora, todo lo que dejes en "%VQ%\01_Entrada"
  echo   se revisa solo. Arranca cada vez que enciendes el PC.
  start "" /min "%PY%" -m videoqa_win.cli watch
)

echo.
pause
exit /b 0
