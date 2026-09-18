from videoqa_win.acentos import sin_tildes, solo_difiere_en_tildes


def test_sin_tildes():
    assert sin_tildes("comí") == "comi"
    assert sin_tildes("TRAICIÓN") == "traicion"
    assert sin_tildes("sándwich") == "sandwich"
    assert sin_tildes("niño") == "nino"
    assert sin_tildes("hola") == "hola"


def test_solo_difiere_en_tildes():
    assert solo_difiere_en_tildes("comi", "comí") is True
    assert solo_difiere_en_tildes("TRAICION", "traición") is True
    assert solo_difiere_en_tildes("nino", "niño") is True
    assert solo_difiere_en_tildes("comi", "como") is False
    assert solo_difiere_en_tildes("aprobecha", "aprovecha") is False
    assert solo_difiere_en_tildes("", "") is True
