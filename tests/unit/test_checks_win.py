from videoqa.config import load_rules

from videoqa_win.checks_win import check_spelling_win


class CorrectorFalso:
    VOCAB = {"comí", "aprovecha", "oferta", "verano"}

    def is_known(self, w):
        return w.lower() in self.VOCAB

    def unknown(self, words):
        return {w for w in words if not self.is_known(w)}

    def correction(self, w):
        return "aprovecha" if w.lower().startswith("aprob") else "comí"

    def tilde_probable(self, w):
        from videoqa_win.acentos import solo_difiere_en_tildes

        for v in self.VOCAB:
            if solo_difiere_en_tildes(w, v):
                return v
        return None


def app(text, t=1.0, conf=1.0):
    return {"text": text, "bbox": [0.1, 0.4, 0.5, 0.1], "t_start": t, "t_end": t + 2,
            "frame": "frames/a.jpg", "frames": [], "conf": conf}


def test_falta_real_sigue_siendo_bloqueante():
    fs = check_spelling_win([app("Aprobecha la oferta")], set(), load_rules(), checker=CorrectorFalso())
    assert len(fs) == 1
    assert fs[0].severity == "blocker" and fs[0].check == "spelling_unknown_word"
    assert "Aprobecha" in fs[0].title


def test_tilde_perdida_por_el_ocr_es_advertencia_explicada():
    fs = check_spelling_win([app("No, me lo comi.")], set(), load_rules(), checker=CorrectorFalso())
    assert len(fs) == 1
    f = fs[0]
    assert f.severity == "warning" and f.check == "spelling_tilde_ocr"
    assert "comi" in f.title and "comí" in f.suggestion
    assert "no distingue" in f.detail
    assert f.t_start == 1.0 and f.frame == "frames/a.jpg"


def test_texto_correcto_no_produce_nada():
    assert check_spelling_win([app("oferta de verano")], set(), load_rules(), checker=CorrectorFalso()) == []


def test_el_glosario_manda():
    assert check_spelling_win([app("Kasa de verano")], {"kasa"}, load_rules(), checker=CorrectorFalso()) == []


def test_confianza_baja_se_ignora():
    assert check_spelling_win([app("Aprobecha", conf=0.2)], set(), load_rules(), checker=CorrectorFalso()) == []


def test_ids_no_se_repiten():
    fs = check_spelling_win([app("Aprobecha", t=1.0), app("comi", t=5.0)], set(), load_rules(),
                            checker=CorrectorFalso())
    assert len({f.id for f in fs}) == len(fs) == 2
