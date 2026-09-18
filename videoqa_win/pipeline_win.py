"""Punto de entrada de la revisión en Windows.

Reutiliza `videoqa.pipeline.process_video` tal cual; lo único propio es
sustituir el check de ortografía por el tolerante a tildes y elegir el juez.
"""
from __future__ import annotations

import logging
from pathlib import Path

from videoqa.claude_runner import ClaudeError
from videoqa.pipeline import Result

from videoqa_win.checks_win import check_spelling_win
from videoqa_win.setup_win import activar, cargar_config

log = logging.getLogger("videoqa")


def _sin_juez(prompt: str, cwd: Path) -> str:
    raise ClaudeError("no hay juez configurado en esta instalación")


def runner_actual(cfg: dict):
    juez = cfg.get("juez", "ninguno")
    if juez == "ollama":
        from videoqa_win.judge_ollama import runner_ollama

        return runner_ollama
    if juez != "ninguno":
        log.warning("juez '%s' desconocido: se sigue sin juez", juez)
    return _sin_juez


def _preparar():
    """Deja el motor listo con los backends y el check de ortografía de Windows."""
    import videoqa.pipeline as pl

    activar()
    pl.check_spelling = check_spelling_win
    return pl


def revisar(video: Path) -> Result:
    """Revisa un video y devuelve el Result del motor."""
    pl = _preparar()
    settings, reglas = cargar_config()
    from videoqa.sheet import SheetWriter

    sheet = SheetWriter(None, settings.jobs_dir / "sheet_pending.json")
    return pl.process_video(Path(video), settings, reglas, runner_actual(reglas), sheet=sheet)


def revisar_pendientes() -> list[Result]:
    """Revisa todo lo que haya en 01_Entrada, uno por uno."""
    from videoqa.watcher import list_videos

    _preparar()
    settings, _ = cargar_config()
    return [revisar(video) for video in list_videos(settings.entrada)]
