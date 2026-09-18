from pathlib import Path

import pytest

BAT = Path(__file__).resolve().parents[2] / "bat"
NOMBRES = ["Instalar VideoQA.bat", "Revisar video.bat", "Activar automatico.bat",
           "Diagnostico.bat", "Actualizar VideoQA.bat"]


@pytest.mark.parametrize("nombre", NOMBRES)
def test_existe_y_tiene_la_cabecera(nombre):
    ruta = BAT / nombre
    assert ruta.exists(), f"falta {nombre}"
    texto = ruta.read_text(encoding="utf-8")
    assert texto.startswith("@echo off"), nombre
    assert "chcp 65001" in texto, nombre
    assert "setlocal" in texto, nombre


@pytest.mark.parametrize("nombre", NOMBRES)
def test_saltos_de_linea_de_windows(nombre):
    crudo = (BAT / nombre).read_bytes()
    assert b"\r\n" in crudo, f"{nombre} necesita saltos CRLF"
    assert b"\n" not in crudo.replace(b"\r\n", b""), f"{nombre} mezcla saltos"


@pytest.mark.parametrize("nombre", NOMBRES)
def test_las_rutas_van_entre_comillas(nombre):
    texto = (BAT / nombre).read_text(encoding="utf-8")
    for linea in texto.splitlines():
        if linea.strip().lower().startswith(("echo", ">>", ">")):
            continue  # texto que se le muestra al editor, no una ruta de comando
        if "%VQ%\\" in linea or "%PY%" in linea:
            assert '"' in linea, f"{nombre}: ruta sin comillas -> {linea}"


@pytest.mark.parametrize("nombre", NOMBRES)
def test_comprueban_que_esta_instalado(nombre):
    if nombre == "Instalar VideoQA.bat":
        pytest.skip("el instalador es el que lo crea")
    texto = (BAT / nombre).read_text(encoding="utf-8")
    assert 'if not exist "%PY%"' in texto, f"{nombre} tiene que avisar si falta la instalación"


def test_el_instalador_usa_winget_y_el_repo_correcto():
    texto = (BAT / "Instalar VideoQA.bat").read_text(encoding="utf-8")
    assert "winget" in texto
    assert "github.com/hongs05/videoqa-win" in texto
    assert "instalar-datos" in texto


def test_revisar_acepta_argumentos_arrastrados():
    texto = (BAT / "Revisar video.bat").read_text(encoding="utf-8")
    assert "%*" in texto


def test_activar_automatico_usa_la_carpeta_de_inicio():
    texto = (BAT / "Activar automatico.bat").read_text(encoding="utf-8")
    assert "Startup" in texto
    assert "watch" in texto
    assert "del " in texto, "tiene que poder apagarse también"
