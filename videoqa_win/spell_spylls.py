"""Corrector ortográfico español con spylls (Hunspell en Python puro).

spylls no trae diccionarios: se descargan los de LibreOffice una vez y quedan
en la carpeta de datos.
"""
from __future__ import annotations

import logging
from pathlib import Path

from videoqa_win.acentos import solo_difiere_en_tildes
from videoqa_win.paths import dicts_dir

log = logging.getLogger("videoqa")

_BASE = "https://raw.githubusercontent.com/LibreOffice/dictionaries/master/es/es_ES"
URLS_DICCIONARIO = {"aff": f"{_BASE}.aff", "dic": f"{_BASE}.dic"}
MAX_SUGERENCIAS = 5


def descargar_diccionario(destino: Path | None = None) -> Path:
    """Baja es_ES.aff y es_ES.dic si faltan. Devuelve el prefijo sin extensión."""
    import requests

    carpeta = Path(destino) if destino else dicts_dir()
    carpeta.mkdir(parents=True, exist_ok=True)
    prefijo = carpeta / "es_ES"
    for ext, url in URLS_DICCIONARIO.items():
        archivo = prefijo.with_suffix(f".{ext}")
        if archivo.exists() and archivo.stat().st_size > 1000:
            continue
        log.info("descargando diccionario %s", ext)
        respuesta = requests.get(url, timeout=120)
        respuesta.raise_for_status()
        archivo.write_bytes(respuesta.content)
    return prefijo


class SpyllsChecker:
    """Corrector con la interfaz que espera el motor."""

    def __init__(self, prefijo: Path | None = None, diccionario=None):
        if diccionario is not None:
            self._dic = diccionario
            return
        from spylls.hunspell import Dictionary

        ruta = Path(prefijo) if prefijo else descargar_diccionario()
        self._dic = Dictionary.from_files(str(ruta))

    def is_known(self, word: str) -> bool:
        return bool(self._dic.lookup(word))

    def unknown(self, words) -> set[str]:
        return {w for w in words if not self.is_known(w)}

    def _sugerencias(self, word: str) -> list[str]:
        salida = []
        for s in self._dic.suggest(word):
            salida.append(str(s))
            if len(salida) >= MAX_SUGERENCIAS:
                break
        return salida

    def correction(self, word: str) -> str | None:
        if self.is_known(word):
            return None
        sugerencias = self._sugerencias(word)
        return sugerencias[0] if sugerencias else None

    def tilde_probable(self, word: str) -> str | None:
        """Si la única diferencia con una palabra válida son las tildes, la devuelve.

        Sirve para no acusar de falta de ortografía lo que en realidad es el OCR
        local, que no lee los acentos.
        """
        if self.is_known(word):
            return None
        for s in self._sugerencias(word):
            if solo_difiere_en_tildes(word, s):
                return s
        return None
