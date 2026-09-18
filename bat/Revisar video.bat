@echo off
chcp 65001 >nul
setlocal
title Revisar video

set "VQ=%USERPROFILE%\VideoQA"
set "PY=%VQ%\.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo   [X] VideoQA no esta instalado todavia.
  echo       Ejecuta primero "Instalar VideoQA.bat".
  pause
  exit /b 1
)

if "%~1"=="" (
  echo   Revisando lo que haya en "%VQ%\01_Entrada" ...
  "%PY%" -m videoqa_win.cli revisar
) else (
  echo   Revisando los archivos que arrastraste...
  "%PY%" -m videoqa_win.cli revisar %*
)

echo.
pause
exit /b 0
