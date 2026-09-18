"""Tildes: el OCR local no las distingue, así que hay que compararlas aparte.

El modelo de reconocimiento que trae RapidOCR no incluye los caracteres
acentuados del español: lee "comí" como "comi". Sin esto, cada palabra con
tilde sería un error de ortografía inventado.
"""
from __future__ import annotations

import unicodedata


def sin_tildes(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFD", texto)
    plano = "".join(c for c in descompuesto if unicodedata.category(c) != "Mn")
    return unicodedata.normalize("NFC", plano).lower()


def solo_difiere_en_tildes(a: str, b: str) -> bool:
    """True si las dos palabras son la misma salvo diacríticos y mayúsculas."""
    return sin_tildes(a) == sin_tildes(b)
