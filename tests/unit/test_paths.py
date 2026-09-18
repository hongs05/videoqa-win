from videoqa_win import paths


def test_respeta_las_variables_de_entorno(tmp_path, monkeypatch):
    monkeypatch.setenv("VIDEOQA_WIN_HOME", str(tmp_path / "d"))
    monkeypatch.setenv("VIDEOQA_WIN_TRABAJO", str(tmp_path / "t"))
    assert paths.datos_dir() == tmp_path / "d"
    assert paths.trabajo_dir() == tmp_path / "t"


def test_subcarpetas_bajo_datos(tmp_path, monkeypatch):
    monkeypatch.setenv("VIDEOQA_WIN_HOME", str(tmp_path / "d"))
    assert paths.modelos_dir() == tmp_path / "d" / "modelos"
    assert paths.dicts_dir() == tmp_path / "d" / "diccionarios"
    assert paths.log_path() == tmp_path / "d" / "registro.log"


def test_crear_carpetas_de_trabajo(tmp_path, monkeypatch):
    monkeypatch.setenv("VIDEOQA_WIN_TRABAJO", str(tmp_path / "t"))
    creadas = paths.crear_carpetas_trabajo()
    for nombre in ("01_Entrada", "02_Con_errores", "03_Aprobado", "_config"):
        assert (tmp_path / "t" / nombre).is_dir()
    assert creadas == tmp_path / "t"


def test_es_windows_es_booleano():
    assert isinstance(paths.es_windows(), bool)
