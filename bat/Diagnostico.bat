@echo off
chcp 65001 >nul
setlocal
title Diagnostico VideoQA

set "VQ=%USERPROFILE%\VideoQA"
set "PY=%VQ%\.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo   VideoQA no esta instalado: no hay nada que revisar.
  echo   Ejecuta "Instalar VideoQA.bat".
  pause
  exit /b 1
)

"%PY%" -m videoqa_win.cli diagnostico
echo.
echo   Se guardo "diagnostico.txt" en tu Escritorio.
echo   Mandalo por chat a quien te paso la herramienta.
echo.
pause
exit /b 0
