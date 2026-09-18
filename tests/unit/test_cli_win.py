from videoqa.pipeline import Result

from videoqa_win import cli


def test_revisar_un_archivo(monkeypatch, tmp_path, capsys):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"x")
    dest = tmp_path / "02_Con_errores" / "v"
    dest.mkdir(parents=True)
    (dest / "reporte.html").write_text("<html></html>", encoding="utf-8")

    monkeypatch.setattr(cli, "revisar", lambda p: Result("rejected", [], dest))
    abiertos = []
    monkeypatch.setattr(cli, "abrir", abiertos.append)

    assert cli.main(["revisar", str(video)]) == 0
    assert "NO APROBADO" in capsys.readouterr().out
    assert abiertos == [dest / "reporte.html"]


def test_revisar_sin_argumentos_usa_los_pendientes(monkeypatch, capsys):
    monkeypatch.setattr(cli, "revisar_pendientes", lambda: [])
    assert cli.main(["revisar"]) == 0
    assert "no hay videos" in capsys.readouterr().out.lower()


def test_revisar_devuelve_1_si_hay_error(monkeypatch, tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"x")
    monkeypatch.setattr(cli, "revisar", lambda p: Result("error", [], None, "algo falló"))
    assert cli.main(["revisar", str(video)]) == 1


def test_instalar_datos_crea_carpetas(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "descargar_diccionario", lambda: tmp_path / "es_ES")
    assert cli.main(["instalar-datos"]) == 0
    from videoqa_win.paths import trabajo_dir

    for nombre in ("01_Entrada", "02_Con_errores", "03_Aprobado", "_config"):
        assert (trabajo_dir() / nombre).is_dir()


def test_instalar_datos_avisa_si_falla_el_diccionario(monkeypatch, capsys):
    def explota():
        raise OSError("sin internet")

    monkeypatch.setattr(cli, "descargar_diccionario", explota)
    assert cli.main(["instalar-datos"]) == 1
    assert "internet" in capsys.readouterr().out.lower()


def test_diagnostico_escribe_informe(tmp_path, capsys):
    destino = tmp_path / "diagnostico.txt"
    assert cli.main(["diagnostico", "--salida", str(destino)]) == 0
    texto = destino.read_text(encoding="utf-8")
    assert "Python" in texto and "ffmpeg" in texto and "Carpeta de trabajo" in texto
