from videoqa import backends

from videoqa_win import setup_win


def test_activar_registra_los_tres():
    backends.reset()
    setup_win.activar()
    from videoqa_win.asr_faster import transcribe
    from videoqa_win.ocr_rapid import ocr_frame
    from videoqa_win.spell_spylls import SpyllsChecker

    assert backends.get_ocr() is ocr_frame
    assert backends.get_transcriber() is transcribe
    assert backends.get_speller() is SpyllsChecker
    backends.reset()


def test_activar_es_idempotente():
    backends.reset()
    setup_win.activar()
    primero = backends.get_ocr()
    setup_win.activar()
    assert backends.get_ocr() is primero
    backends.reset()


def test_config_apunta_a_la_carpeta_de_trabajo(tmp_path, monkeypatch):
    monkeypatch.setenv("VIDEOQA_WIN_TRABAJO", str(tmp_path / "T"))
    settings, rules = setup_win.cargar_config()
    assert settings.drive_root == tmp_path / "T"
    assert settings.entrada == tmp_path / "T" / "01_Entrada"
    assert rules["salida"]["reporte_html"] is True
    assert rules["thresholds"]["ocr_min_conf"] == 0.4
    assert rules["severities"]["spelling_tilde_ocr"] == "warning"
    # Sin esto, cada video saldría como "error" y nunca habría un 🟢.
    assert rules["juez_requerido"] is False


def test_config_lee_el_juez_del_yaml(tmp_path, monkeypatch):
    monkeypatch.setenv("VIDEOQA_WIN_HOME", str(tmp_path / "d"))
    monkeypatch.setenv("VIDEOQA_WIN_TRABAJO", str(tmp_path / "T"))
    (tmp_path / "d").mkdir(parents=True)
    (tmp_path / "d" / "config.yaml").write_text("juez: ollama\n", encoding="utf-8")
    _, rules = setup_win.cargar_config()
    assert rules["juez"] == "ollama"


def test_config_sin_yaml_usa_juez_ninguno(tmp_path, monkeypatch):
    monkeypatch.setenv("VIDEOQA_WIN_HOME", str(tmp_path / "d"))
    monkeypatch.setenv("VIDEOQA_WIN_TRABAJO", str(tmp_path / "T"))
    _, rules = setup_win.cargar_config()
    assert rules["juez"] == "ninguno"


def test_config_no_modifica_las_reglas_del_motor(tmp_path, monkeypatch):
    from videoqa.config import load_rules

    monkeypatch.setenv("VIDEOQA_WIN_TRABAJO", str(tmp_path / "T"))
    setup_win.cargar_config()
    assert load_rules().get("salida", {}).get("reporte_html") is not True
