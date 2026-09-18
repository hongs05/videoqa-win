import shutil
from pathlib import Path

import pytest

from videoqa_win import pipeline_win

FIXTURES = Path.home() / "videoeditorpipeline" / "tests" / "fixtures"


def _entorno(tmp_path, monkeypatch, nombre):
    monkeypatch.setenv("VIDEOQA_WIN_HOME", str(tmp_path / "datos"))
    monkeypatch.setenv("VIDEOQA_WIN_TRABAJO", str(tmp_path / "T"))
    from videoqa_win.paths import crear_carpetas_trabajo

    raiz = crear_carpetas_trabajo()
    shutil.copy(FIXTURES / "brand.json", raiz / "_config" / "brand.json")
    shutil.copy(FIXTURES / "glosario.txt", raiz / "_config" / "glosario.txt")
    origen = FIXTURES / "out" / f"{nombre}.mp4"
    if not origen.exists():
        pytest.skip("fixtures del motor no generados")
    destino = raiz / "01_Entrada" / f"{nombre}.mp4"
    shutil.copy(origen, destino)
    return raiz, destino


@pytest.mark.lento
def test_el_fixture_con_errores_sale_rechazado(tmp_path, monkeypatch):
    raiz, video = _entorno(tmp_path, monkeypatch, "spelling_color")
    res = pipeline_win.revisar(video)
    assert res.status == "rejected"
    checks = {f.check for f in res.findings}
    assert "brand_color" in checks
    assert res.dest == raiz / "02_Con_errores" / "spelling_color"
    assert (res.dest / "reporte.html").exists()
    assert (res.dest / "reporte.md").exists()
    # El aviso de "sin criterio" está, pero como información: no bloquea.
    juez = [f for f in res.findings if f.check == "judge_unavailable"]
    assert len(juez) == 1 and juez[0].severity == "info"


@pytest.mark.lento
def test_el_fixture_limpio_se_aprueba(tmp_path, monkeypatch):
    raiz, video = _entorno(tmp_path, monkeypatch, "clean")
    res = pipeline_win.revisar(video)
    bloqueantes = [f.title for f in res.findings if f.severity == "blocker"]
    assert bloqueantes == [], bloqueantes
    assert res.status == "approved"
    assert res.dest == raiz / "03_Aprobado" / "clean"


@pytest.mark.lento
def test_video_sin_audio_no_rompe(tmp_path, monkeypatch):
    raiz, video = _entorno(tmp_path, monkeypatch, "no_audio")
    res = pipeline_win.revisar(video)
    # "sin audio" es un aviso, no un bloqueante: el video se aprueba con la nota.
    assert res.status == "approved"
    avisos = {f.check for f in res.findings if f.severity == "warning"}
    assert "no_audio" in avisos
