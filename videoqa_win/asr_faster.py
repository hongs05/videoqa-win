"""Transcripción con faster-whisper (CTranslate2): CPU o GPU NVIDIA, sin PyTorch.

Verificado: el modelo `small` en CPU transcribe un video de 10 s en segundos y
devuelve las tildes y la puntuación correctas.
"""
from __future__ import annotations

import logging
import shutil
import subprocess
from functools import lru_cache

from videoqa.job import Job
from videoqa.stages.transcribe import extract_audio

from videoqa_win.paths import modelos_dir

log = logging.getLogger("videoqa")

VACIO = {"language": "es", "text": "", "segments": []}


def _hay_gpu_nvidia() -> bool:
    if not shutil.which("nvidia-smi"):
        return False
    try:
        return subprocess.run(["nvidia-smi"], capture_output=True, timeout=15).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def elegir_dispositivo() -> tuple[str, str, str]:
    """(device, compute_type, modelo). Con GPU NVIDIA sube a `medium`."""
    if _hay_gpu_nvidia():
        return "cuda", "float16", "medium"
    return "cpu", "int8", "small"


@lru_cache(maxsize=2)
def _cargar_modelo(nombre: str, device: str, compute_type: str):
    from faster_whisper import WhisperModel

    carpeta = modelos_dir()
    carpeta.mkdir(parents=True, exist_ok=True)
    return WhisperModel(nombre, device=device, compute_type=compute_type, download_root=str(carpeta))


def normalizar(segmentos, info) -> dict:
    limpios = []
    for s in segmentos:
        texto = str(s.text).strip()
        if texto:
            limpios.append({"start": round(float(s.start), 2), "end": round(float(s.end), 2),
                            "text": texto})
    return {"language": getattr(info, "language", "es") or "es",
            "text": " ".join(s["text"] for s in limpios),
            "segments": limpios}


def transcribe(job: Job, has_audio: bool, model: str) -> dict:
    """`model` se ignora salvo que sea un nombre de faster-whisper distinto de 'auto'."""
    if not has_audio:
        return {"language": "es", "text": "", "segments": []}
    wav = job.path("audio.wav")
    try:
        extract_audio(job.video, wav)
        device, compute_type, nombre = elegir_dispositivo()
        if model and model != "auto" and "/" not in model:
            nombre = model
        log.info("[%s] transcribiendo con %s en %s", job.name, nombre, device)
        modelo = _cargar_modelo(nombre, device, compute_type)
        segmentos, info = modelo.transcribe(str(wav), language="es", vad_filter=True)
        return normalizar(segmentos, info)
    except Exception as e:  # noqa: BLE001 — sin transcripción se sigue con los checks visuales
        log.warning("[%s] no se pudo transcribir (%s): %s", job.name, type(e).__name__, e)
        return {"language": "es", "text": "", "segments": []}
