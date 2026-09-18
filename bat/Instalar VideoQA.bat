@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title Instalar VideoQA

set "VQ=%USERPROFILE%\VideoQA"
set "PY=%VQ%\.venv\Scripts\python.exe"

echo.
echo   VideoQA - instalacion
echo   Esto deja tu PC listo para revisar videos antes de subirlos.
echo   Puede tardar entre 10 y 20 minutos. No cierres la ventana.
echo.

where winget >nul 2>&1
if errorlevel 1 (
  echo   [X] Falta "winget", que es lo que instala programas en Windows.
  echo       Abre la Microsoft Store, busca "Instalador de aplicaciones"
  echo       e instalalo. Despues vuelve a ejecutar este archivo.
  pause
  exit /b 1
)

echo   [1/5] Python 3.12
where python >nul 2>&1
if errorlevel 1 (
  echo         Instalando Python...
  winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements --silent
) else (
  echo         Ya estaba.
)

echo   [2/5] ffmpeg
where ffmpeg >nul 2>&1
if errorlevel 1 (
  echo         Instalando ffmpeg...
  winget install --id Gyan.FFmpeg -e --accept-source-agreements --accept-package-agreements --silent
) else (
  echo         Ya estaba.
)

echo   [3/5] Preparando la carpeta de trabajo
if not exist "%VQ%" mkdir "%VQ%"
if not exist "%PY%" (
  py -3.12 -m venv "%VQ%\.venv" 2>nul || python -m venv "%VQ%\.venv"
)
if not exist "%PY%" (
  echo   [X] No pude preparar Python. Cierra esta ventana, abrela de nuevo
  echo       y vuelve a ejecutar este archivo: Windows necesita reiniciar
  echo       la ventana despues de instalar Python.
  pause
  exit /b 1
)

echo   [4/5] Instalando VideoQA ^(descarga unos 300 MB^)
"%PY%" -m pip install --upgrade pip --quiet
"%PY%" -m pip install --upgrade "videoqa-win @ git+https://github.com/hongs05/videoqa-win@main"
if errorlevel 1 (
  echo   [X] La descarga fallo. Revisa tu internet y vuelve a ejecutar
  echo       este archivo: continua donde se quedo.
  pause
  exit /b 1
)

echo   [5/5] Carpetas y diccionario
"%PY%" -m videoqa_win.cli instalar-datos
if errorlevel 1 (
  echo   [!] No pude bajar el diccionario. Se puede reintentar despues.
)

copy /Y "%~dp0Revisar video.bat" "%USERPROFILE%\Desktop\Revisar video.bat" >nul 2>&1
copy /Y "%~dp0Activar automatico.bat" "%USERPROFILE%\Desktop\Activar automatico.bat" >nul 2>&1
copy /Y "%~dp0Diagnostico.bat" "%USERPROFILE%\Desktop\Diagnostico.bat" >nul 2>&1
copy /Y "%~dp0Actualizar VideoQA.bat" "%USERPROFILE%\Desktop\Actualizar VideoQA.bat" >nul 2>&1

echo.
echo   Listo. En tu Escritorio tienes "Revisar video".
echo.
echo   Como se usa:
echo     - Arrastra un video encima de "Revisar video" y espera.
echo     - O deja los videos en:  %VQ%\01_Entrada
echo       y haz doble clic en "Revisar video".
echo.
echo   La primera revision descarga el modelo de voz ^(unos 250 MB^):
echo   tarda mas solo esa vez.
echo.
start "" "%VQ%"
pause
exit /b 0
