"""Juez local opcional con Ollama.

Experimental: un modelo de 3B ve mucho menos que Claude. Sirve para lo evidente
(marca de agua, texto cortado) y se le escapa el matiz. Apagado por defecto.
"""
from __future__ import annotations

import base64
import logging
import re
from pathlib import Path

import requests
from videoqa.claude_runner import ClaudeError

log = logging.getLogger("videoqa")

MODELO = "qwen2.5vl:3b"
URL = "http://127.0.0.1:11434/api/generate"
MAX_FRAMES = 6          # un 3B se pierde con quince imágenes
TIMEOUT = 600

_RUTA_FRAME = re.compile(r"(claude_frames/[\w.\-]+\.jpg)")


def imagenes_del_prompt(prompt: str, cwd: Path) -> list[Path]:
    vistas, salida = set(), []
    for rel in _RUTA_FRAME.findall(prompt):
        if rel in vistas:
            continue
        vistas.add(rel)
        ruta = Path(cwd) / rel
        if ruta.exists():
            salida.append(ruta)
        if len(salida) >= MAX_FRAMES:
            break
    return salida


def runner_ollama(prompt: str, cwd: Path) -> str:
    """Runner compatible con el motor: (prompt, cwd) -> texto de la respuesta."""
    imagenes = [base64.b64encode(p.read_bytes()).decode("ascii")
                for p in imagenes_del_prompt(prompt, cwd)]
    cuerpo = {"model": MODELO, "prompt": prompt, "images": imagenes, "stream": False,
              "options": {"temperature": 0}}
    try:
        respuesta = requests.post(URL, json=cuerpo, timeout=TIMEOUT)
        respuesta.raise_for_status()
        datos = respuesta.json()
    except Exception as e:  # noqa: BLE001 — cualquier fallo se traduce al error del motor
        raise ClaudeError(f"Ollama no respondió ({type(e).__name__}): {e}") from e
    texto = str(datos.get("response", "")).strip()
    if not texto:
        raise ClaudeError("Ollama devolvió una respuesta vacía")
    return texto
