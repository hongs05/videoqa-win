@echo off
chcp 65001 >nul
setlocal
title Actualizar VideoQA

set "VQ=%USERPROFILE%\VideoQA"
set "PY=%VQ%\.venv\Scripts\python.exe"

if not exist "%PY%" (
  echo   [X] VideoQA no esta instalado todavia.
  pause
  exit /b 1
)

echo   Buscando novedades...
"%PY%" -m pip install --upgrade "videoqa-win @ git+https://github.com/hongs05/videoqa-win@main"
if errorlevel 1 (
  echo   [X] No pude actualizar. Revisa tu internet y vuelve a intentarlo.
  pause
  exit /b 1
)
echo   Listo, ya tienes la ultima version.
echo.
pause
exit /b 0
