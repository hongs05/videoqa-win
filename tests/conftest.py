import os

import pytest


def pytest_runtest_setup(item):
    if "lento" in item.keywords and not os.environ.get("VIDEOQA_WIN_LENTO"):
        pytest.skip("test lento: exporta VIDEOQA_WIN_LENTO=1 para correrlo")


@pytest.fixture(autouse=True)
def _aisla_rutas(tmp_path, monkeypatch):
    """Ningún test escribe en las carpetas reales del usuario."""
    monkeypatch.setenv("VIDEOQA_WIN_HOME", str(tmp_path / "datos"))
    monkeypatch.setenv("VIDEOQA_WIN_TRABAJO", str(tmp_path / "VideoQA"))
