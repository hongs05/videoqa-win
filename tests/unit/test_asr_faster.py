from types import SimpleNamespace

import pytest

from videoqa_win import asr_faster


def seg(start, end, text):
    return SimpleNamespace(start=start, end=end, text=text)


def test_normalizar_limpia_y_arma_el_texto():
    info = SimpleNamespace(language="es", duration=10.0)
    segmentos = [seg(0.0, 2.004, "  ¡Oye! ¿Tienes mi sándwich? "), seg(2.0, 4.0, "   "),
                 seg(4.0, 6.0, "¡Era mi almuerzo!")]
    out = asr_faster.normalizar(segmentos, info)
    assert out["language"] == "es"
    assert out["segments"] == [{"start": 0.0, "end": 2.0, "text": "¡Oye! ¿Tienes mi sándwich?"},
                               {"start": 4.0, "end": 6.0, "text": "¡Era mi almuerzo!"}]
    assert out["text"] == "¡Oye! ¿Tienes mi sándwich? ¡Era mi almuerzo!"


def test_normalizar_sin_segmentos():
    info = SimpleNamespace(language="es", duration=0.0)
    assert asr_faster.normalizar([], info) == {"language": "es", "text": "", "segments": []}


def test_elegir_dispositivo_con_gpu(monkeypatch):
    monkeypatch.setattr(asr_faster, "_hay_gpu_nvidia", lambda: True)
    assert asr_faster.elegir_dispositivo() == ("cuda", "float16", "medium")


def test_elegir_dispositivo_sin_gpu(monkeypatch):
    monkeypatch.setattr(asr_faster, "_hay_gpu_nvidia", lambda: False)
    assert asr_faster.elegir_dispositivo() == ("cpu", "int8", "small")


def test_transcribe_usa_el_modelo_y_normaliza(monkeypatch, tmp_path):
    from videoqa.job import Job

    video = tmp_path / "v.mp4"
    video.write_bytes(b"x")
    job = Job(video, tmp_path / "jobs")
    job.path("audio.wav").write_bytes(b"RIFF")

    monkeypatch.setattr(asr_faster, "extract_audio", lambda video, wav: None)
    monkeypatch.setattr(asr_faster, "_hay_gpu_nvidia", lambda: False)

    class ModeloFalso:
        def transcribe(self, ruta, language, vad_filter=True):
            assert language == "es"
            return iter([seg(0.0, 1.0, "hola")]), SimpleNamespace(language="es", duration=1.0)

    def cargar(nombre, device, compute_type):
        assert (nombre, device, compute_type) == ("small", "cpu", "int8")
        return ModeloFalso()

    monkeypatch.setattr(asr_faster, "_cargar_modelo", cargar)
    out = asr_faster.transcribe(job, True, "auto")
    assert out["text"] == "hola" and out["segments"][0]["end"] == 1.0


def test_transcribe_si_falla_devuelve_vacio_y_no_lanza(monkeypatch, tmp_path):
    from videoqa.job import Job

    video = tmp_path / "v.mp4"
    video.write_bytes(b"x")
    job = Job(video, tmp_path / "jobs")
    monkeypatch.setattr(asr_faster, "extract_audio", lambda video, wav: None)
    monkeypatch.setattr(asr_faster, "_hay_gpu_nvidia", lambda: False)

    def explota(*a, **k):
        raise RuntimeError("modelo corrupto")

    monkeypatch.setattr(asr_faster, "_cargar_modelo", explota)
    out = asr_faster.transcribe(job, True, "auto")
    assert out == {"language": "es", "text": "", "segments": []}


def test_transcribe_sin_audio_no_toca_el_modelo(monkeypatch, tmp_path):
    from videoqa.job import Job

    video = tmp_path / "v.mp4"
    video.write_bytes(b"x")
    job = Job(video, tmp_path / "jobs")
    assert asr_faster.transcribe(job, False, "auto") == {"language": "es", "text": "", "segments": []}


@pytest.mark.lento
def test_transcripcion_real_de_un_fixture(tmp_path):
    from pathlib import Path

    from videoqa.job import Job

    fixture = Path.home() / "videoeditorpipeline" / "tests" / "fixtures" / "out" / "clean.mp4"
    if not fixture.exists():
        pytest.skip("fixture del motor no generado")
    job = Job(fixture, tmp_path / "jobs")
    out = asr_faster.transcribe(job, True, "auto")
    assert out["language"] == "es"
    assert "oferta" in out["text"].lower() or "verano" in out["text"].lower()
    assert all(s["end"] >= s["start"] for s in out["segments"])
