import pytest

from videoqa_win.spell_spylls import URLS_DICCIONARIO, SpyllsChecker, descargar_diccionario


def test_urls_del_diccionario():
    assert set(URLS_DICCIONARIO) == {"aff", "dic"}
    for url in URLS_DICCIONARIO.values():
        assert url.startswith("https://raw.githubusercontent.com/LibreOffice/dictionaries/")


class DiccionarioFalso:
    """Imita spylls.hunspell.Dictionary con un vocabulario mínimo."""

    VOCAB = {"comí", "aprovecha", "oferta", "niño", "casa"}

    def lookup(self, palabra):
        return palabra in self.VOCAB or palabra.lower() in self.VOCAB

    def suggest(self, palabra):
        from videoqa_win.acentos import sin_tildes

        for v in sorted(self.VOCAB):
            if sin_tildes(v) == sin_tildes(palabra):
                yield v
        # Sugerencia "por parecido": comparte el final de la palabra.
        # (kasa → casa, igual que haría hunspell con una letra cambiada)
        for v in sorted(self.VOCAB):
            if sin_tildes(v) == sin_tildes(palabra):
                continue
            if sin_tildes(v)[-3:] == sin_tildes(palabra)[-3:]:
                yield v


@pytest.fixture
def checker():
    return SpyllsChecker(diccionario=DiccionarioFalso())


def test_is_known(checker):
    assert checker.is_known("comí") is True
    assert checker.is_known("casa") is True
    assert checker.is_known("kasa") is False


def test_unknown_filtra(checker):
    assert checker.unknown(["casa", "kasa", "oferta"]) == {"kasa"}


def test_correction_devuelve_la_primera_sugerencia(checker):
    assert checker.correction("kasa") == "casa"
    assert checker.correction("comí") is None


def test_tilde_probable_detecta_el_caso_del_ocr(checker):
    # "comi" no está en el diccionario, pero la única diferencia con "comí"
    # son las tildes: es artefacto del OCR, no una falta del editor.
    assert checker.is_known("comi") is False
    assert checker.tilde_probable("comi") == "comí"
    assert checker.tilde_probable("nino") == "niño"
    assert checker.tilde_probable("kasa") is None


@pytest.mark.lento
def test_diccionario_real_de_libreoffice(tmp_path):
    prefijo = descargar_diccionario(tmp_path)
    assert prefijo.with_suffix(".aff").exists() and prefijo.with_suffix(".dic").exists()
    c = SpyllsChecker(prefijo=prefijo)
    assert c.is_known("aprovecha") and c.is_known("sándwich")
    assert not c.is_known("aprobecha")
    assert c.correction("aprobecha") == "aprovecha"
    assert c.tilde_probable("comi") == "comí"
    assert c.tilde_probable("aprobecha") is None
