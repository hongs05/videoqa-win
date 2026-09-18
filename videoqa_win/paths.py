"""Rutas del sistema, con variables de entorno para poder aislarlas en tests.

Se separan a propósito dos carpetas: la de **trabajo** (visible, donde el editor
deja los videos) y la de **datos** (modelos, diccionarios, trabajos intermedios y
registro), para que no vea 300 MB de archivos técnicos mezclados con lo suyo.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

CARPETAS_TRABAJO = ("01_Entrada", "02_Con_errores", "03_Aprobado", "_config")


def es_windows() -> bool:
    return sys.platform.startswith("win")


def datos_dir() -> Path:
    """Donde viven modelos, diccionarios y el registro."""
    env = os.environ.get("VIDEOQA_WIN_HOME")
    if env:
        return Path(env).expanduser()
    if es_windows():
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "VideoQA"
    return Path.home() / ".videoqa-win"


def trabajo_dir() -> Path:
    """Carpeta visible donde el editor deja los videos."""
    env = os.environ.get("VIDEOQA_WIN_TRABAJO")
    if env:
        return Path(env).expanduser()
    return Path.home() / "VideoQA"


def modelos_dir() -> Path:
    return datos_dir() / "modelos"


def dicts_dir() -> Path:
    return datos_dir() / "diccionarios"


def log_path() -> Path:
    return datos_dir() / "registro.log"


def crear_carpetas_trabajo() -> Path:
    raiz = trabajo_dir()
    for nombre in CARPETAS_TRABAJO:
        (raiz / nombre).mkdir(parents=True, exist_ok=True)
    return raiz
