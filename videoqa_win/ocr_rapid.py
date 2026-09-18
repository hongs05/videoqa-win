"""OCR con RapidOCR (onnxruntime), sin PaddlePaddle ni PyTorch.

RapidOCR devuelve, por cada detección, cuatro puntos en píxeles, el texto y la
confianza. El motor espera la caja normalizada 0-1 con origen arriba-izquierda,
así que aquí se convierte al rectángulo que contiene los cuatro puntos.

Aviso conocido: el modelo de reconocimiento incluido no trae los caracteres
acentuados del español ("comí" se lee "comi"). Eso NO se corrige aquí: se trata
en el check de ortografía (ver videoqa_win/checks_win.py).
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from PIL import Image

log = logging.getLogger("videoqa")

# La confianza de RapidOCR no es comparable con la de Apple Vision: en la
# prueba real un subtítulo nítido dio 0.998 y el ruido de fondo, 0.1-0.3.
MIN_CONF = 0.4


@lru_cache(maxsize=1)
def _motor():
    from rapidocr_onnxruntime import RapidOCR

    return RapidOCR()


def convertir_caja(box, ancho: int, alto: int) -> list[float]:
    xs = [float(p[0]) for p in box]
    ys = [float(p[1]) for p in box]
    x0 = max(0.0, min(xs) / ancho)
    y0 = max(0.0, min(ys) / alto)
    x1 = min(1.0, max(xs) / ancho)
    y1 = min(1.0, max(ys) / alto)
    return [round(x0, 4), round(y0, 4), round(max(0.0, x1 - x0), 4), round(max(0.0, y1 - y0), 4)]


def ocr_frame(path: Path) -> list[dict]:
    path = Path(path)
    with Image.open(path) as img:
        ancho, alto = img.size
    try:
        resultado, _ = _motor()(str(path))
    except Exception as e:  # noqa: BLE001 — el OCR no debe tumbar la revisión
        log.warning("OCR falló en %s: %s", path.name, type(e).__name__)
        return []
    salida = []
    for deteccion in resultado or []:
        box, texto, conf = deteccion[0], str(deteccion[1]).strip(), float(deteccion[2])
        if not texto or conf < MIN_CONF:
            continue
        salida.append({"text": texto, "conf": conf, "bbox": convertir_caja(box, ancho, alto)})
    return salida
