import pytest
from videoqa.claude_runner import ClaudeError

from videoqa_win import judge_ollama


def test_recoge_las_imagenes_del_prompt(tmp_path):
    (tmp_path / "claude_frames").mkdir()
    for i in range(8):
        (tmp_path / "claude_frames" / f"{i:02d}_0000.{i}s.jpg").write_bytes(b"jpg")
    prompt = "\n".join(f"- claude_frames/{i:02d}_0000.{i}s.jpg  (t = 0.{i} s)" for i in range(8))
    imagenes = judge_ollama.imagenes_del_prompt(prompt, tmp_path)
    assert len(imagenes) == judge_ollama.MAX_FRAMES
    assert all(p.exists() for p in imagenes)


def test_ignora_rutas_que_no_existen(tmp_path):
    assert judge_ollama.imagenes_del_prompt("- claude_frames/99_0099.0s.jpg", tmp_path) == []


def test_runner_devuelve_el_texto(monkeypatch, tmp_path):
    def fake_post(url, json=None, timeout=None):
        assert "api/generate" in url
        assert json["model"] == judge_ollama.MODELO

        class R:
            @staticmethod
            def raise_for_status():
                pass

            @staticmethod
            def json():
                return {"response": '{"findings": []}'}

        return R

    monkeypatch.setattr(judge_ollama.requests, "post", fake_post)
    assert judge_ollama.runner_ollama("prompt", tmp_path) == '{"findings": []}'


def test_si_ollama_no_responde_lanza_claude_error(monkeypatch, tmp_path):
    def fake_post(url, json=None, timeout=None):
        raise OSError("conexión rechazada")

    monkeypatch.setattr(judge_ollama.requests, "post", fake_post)
    with pytest.raises(ClaudeError):
        judge_ollama.runner_ollama("prompt", tmp_path)


def test_respuesta_vacia_lanza_claude_error(monkeypatch, tmp_path):
    class R:
        @staticmethod
        def raise_for_status():
            pass

        @staticmethod
        def json():
            return {"response": "   "}

    monkeypatch.setattr(judge_ollama.requests, "post", lambda *a, **k: R)
    with pytest.raises(ClaudeError):
        judge_ollama.runner_ollama("prompt", tmp_path)
