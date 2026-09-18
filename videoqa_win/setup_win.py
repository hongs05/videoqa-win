"""Activación de los backends portables y configuración propia de Windows."""
from __future__ import annotations

import copy
import logging

import yaml
from videoqa import backends
from videoqa.config import Settings, load_rules

from videoqa_win.paths import datos_dir, trabajo_dir

log = logging.getLogger("videoqa")

# Ajustes propios de esta pila. No se tocan las reglas del motor: se aplican
# encima al cargar la configuración.
AJUSTES = {
    "salida": {"reporte_html": True},
    # Esto es un pre-chequeo: el criterio lo aporta la revisión oficial en la Mac.
    # Sin esta bandera el motor marcaría "error" en todos los videos y nunca
    # habría un 🟢.
    "juez_requerido": False,
    # La confianza de RapidOCR no es la de Apple Vision (ver videoqa_win/ocr_rapid.py).
    "thresholds": {"ocr_min_conf": 0.4},
    "severities": {"spelling_tilde_ocr": "warning"},
}


def activar() -> None:
    """Registra OCR, transcripción y corrector portables en el motor."""
    from videoqa_win.asr_faster import transcribe
    from videoqa_win.ocr_rapid import ocr_frame
    from videoqa_win.spell_spylls import SpyllsChecker

    backends.register_ocr(ocr_frame)
    backends.register_transcriber(transcribe)
    backends.register_speller(SpyllsChecker)


def _config_yaml() -> dict:
    ruta = datos_dir() / "config.yaml"
    if not ruta.exists():
        return {}
    try:
        return yaml.safe_load(ruta.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        log.warning("config.yaml ilegible (%s): se usan los valores por defecto", type(e).__name__)
        return {}


def cargar_config() -> tuple[Settings, dict]:
    reglas = copy.deepcopy(load_rules())
    for seccion, valores in AJUSTES.items():
        if isinstance(valores, dict):
            reglas.setdefault(seccion, {}).update(valores)
        else:
            reglas[seccion] = valores

    propia = _config_yaml()
    reglas["juez"] = str(propia.get("juez", "ninguno"))
    if propia.get("whisper_model"):
        reglas.setdefault("asr", {})["model"] = str(propia["whisper_model"])

    settings = Settings(drive_root=trabajo_dir(), jobs_dir=datos_dir() / "jobs")
    return settings, reglas
