import pytest
from PIL import Image, ImageDraw, ImageFont

from videoqa_win import ocr_rapid


def test_convertir_caja_centrada():
    box = [[100.0, 200.0], [300.0, 200.0], [300.0, 260.0], [100.0, 260.0]]
    assert ocr_rapid.convertir_caja(box, 1000, 1000) == [0.1, 0.2, 0.2, 0.06]


def test_convertir_caja_inclinada_usa_el_rectangulo_que_la_contiene():
    box = [[100.0, 190.0], [300.0, 210.0], [300.0, 270.0], [100.0, 250.0]]
    x, y, w, h = ocr_rapid.convertir_caja(box, 1000, 1000)
    assert (x, y) == (0.1, 0.19)
    assert round(w, 3) == 0.2 and round(h, 3) == 0.08


def test_convertir_caja_recorta_a_cero_uno():
    box = [[-50.0, -20.0], [1100.0, -20.0], [1100.0, 1050.0], [-50.0, 1050.0]]
    assert ocr_rapid.convertir_caja(box, 1000, 1000) == [0.0, 0.0, 1.0, 1.0]


def test_ocr_frame_traduce_la_salida_de_rapidocr(monkeypatch, tmp_path):
    img = tmp_path / "f.jpg"
    Image.new("RGB", (1000, 500), (0, 0, 0)).save(img)

    class MotorFalso:
        def __call__(self, ruta):
            assert ruta == str(img)
            return ([[[[100.0, 200.0], [300.0, 200.0], [300.0, 260.0], [100.0, 260.0]],
                      "No, me lo comi.", 0.9979]], 0.12)

    monkeypatch.setattr(ocr_rapid, "_motor", lambda: MotorFalso())
    out = ocr_rapid.ocr_frame(img)
    assert len(out) == 1
    assert out[0]["text"] == "No, me lo comi."
    assert round(out[0]["conf"], 4) == 0.9979
    assert out[0]["bbox"] == [0.1, 0.4, 0.2, 0.12]


def test_ocr_frame_sin_detecciones(monkeypatch, tmp_path):
    img = tmp_path / "f.jpg"
    Image.new("RGB", (100, 100), (0, 0, 0)).save(img)
    monkeypatch.setattr(ocr_rapid, "_motor", lambda: (lambda ruta: (None, 0.0)))
    assert ocr_rapid.ocr_frame(img) == []


def test_ocr_frame_descarta_confianza_baja(monkeypatch, tmp_path):
    img = tmp_path / "f.jpg"
    Image.new("RGB", (1000, 500), (0, 0, 0)).save(img)
    caja = [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
    monkeypatch.setattr(ocr_rapid, "_motor",
                        lambda: (lambda ruta: ([[caja, "ruido", 0.1], [caja, "bueno", 0.95]], 0.0)))
    textos = [i["text"] for i in ocr_rapid.ocr_frame(img)]
    assert textos == ["bueno"]


def test_ocr_frame_no_lanza_si_el_motor_falla(monkeypatch, tmp_path):
    img = tmp_path / "f.jpg"
    Image.new("RGB", (100, 100), (0, 0, 0)).save(img)

    def explota():
        raise RuntimeError("onnx roto")

    monkeypatch.setattr(ocr_rapid, "_motor", explota)
    assert ocr_rapid.ocr_frame(img) == []


@pytest.mark.lento
def test_ocr_real_lee_un_subtitulo(tmp_path):
    img = tmp_path / "sub.jpg"
    imagen = Image.new("RGB", (1280, 720), (20, 30, 60))
    dibujo = ImageDraw.Draw(imagen)
    fuente = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 56)
    dibujo.text((330, 600), "OFERTA DE VERANO", fill=(255, 255, 255), font=fuente)
    imagen.save(img)
    out = ocr_rapid.ocr_frame(img)
    textos = " ".join(i["text"].upper() for i in out)
    assert "OFERTA" in textos
    x, y, w, h = out[0]["bbox"]
    assert 0.0 <= x <= 1.0 and 0.75 <= y + h <= 1.05
