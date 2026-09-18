"""Interfaz de línea de comandos. La usan los .bat; el editor no la ve."""
from __future__ import annotations

import argparse
import logging
import logging.handlers
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from videoqa_win.paths import (crear_carpetas_trabajo, datos_dir, log_path, modelos_dir,
                               trabajo_dir)
from videoqa_win.pipeline_win import revisar, revisar_pendientes
from videoqa_win.spell_spylls import descargar_diccionario

ESTADOS = {"approved": "🟢 APROBADO", "rejected": "🔴 NO APROBADO — hay que corregir",
           "error": "❌ No se pudo revisar del todo"}


def preparar_log() -> None:
    datos_dir().mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    raiz = logging.getLogger("videoqa")
    raiz.setLevel(logging.INFO)
    for h in list(raiz.handlers):
        h.close()
        raiz.removeHandler(h)
    fh = logging.handlers.RotatingFileHandler(log_path(), maxBytes=2_000_000, backupCount=2,
                                              encoding="utf-8")
    fh.setFormatter(fmt)
    raiz.addHandler(fh)


def abrir(ruta: Path) -> None:
    """Abre un archivo con el programa por defecto del sistema."""
    try:
        if sys.platform.startswith("win"):
            import os

            os.startfile(str(ruta))  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", str(ruta)], check=False)
        else:
            subprocess.run(["xdg-open", str(ruta)], check=False)
    except Exception as e:  # noqa: BLE001
        print(f"    (no pude abrir {ruta.name}: {type(e).__name__})")


def _informar(res) -> None:
    print(f"\n  {ESTADOS.get(res.status, res.status)}")
    if res.status == "error" and res.dest is None:
        print(f"    Motivo: {res.error}")
        print("    El video sigue en 01_Entrada; se puede volver a intentar.")
        return
    bloq = sum(1 for f in res.findings if f.severity == "blocker")
    avisos = sum(1 for f in res.findings if f.severity == "warning")
    print(f"    {bloq} cosas que corregir · {avisos} avisos")
    for f in sorted((f for f in res.findings if f.severity == "blocker"), key=lambda f: f.t_start):
        seg = int(f.t_start)
        print(f"      · [{seg // 60}:{seg % 60:02d}] {f.title}")
    if res.dest:
        print(f"    Detalle completo: {res.dest / 'reporte.html'}")


def _abrir_reporte(res) -> None:
    if res.dest:
        html = res.dest / "reporte.html"
        if html.exists():
            abrir(html)


def cmd_revisar(args) -> int:
    if args.archivos:
        codigos = []
        for ruta in args.archivos:
            res = revisar(Path(ruta))
            _informar(res)
            _abrir_reporte(res)
            codigos.append(0 if res.status in ("approved", "rejected") else 1)
        return max(codigos)

    resultados = revisar_pendientes()
    if not resultados:
        print("\n  No hay videos esperando en 01_Entrada.")
        return 0
    for res in resultados:
        _informar(res)
    _abrir_reporte(resultados[-1])
    return 0 if all(r.status in ("approved", "rejected") for r in resultados) else 1


def cmd_watch(args) -> int:
    from videoqa.watcher import watch

    from videoqa_win.pipeline_win import runner_actual
    from videoqa_win.setup_win import activar, cargar_config

    activar()
    settings, reglas = cargar_config()

    def procesar(video, settings, rules, runner, sheet=None):
        return revisar(video)

    print(f"  Vigilando {settings.entrada}")
    watch(settings, reglas, runner_actual(reglas), once=args.once, process=procesar)
    return 0


def cmd_instalar_datos(args) -> int:
    raiz = crear_carpetas_trabajo()
    modelos_dir().mkdir(parents=True, exist_ok=True)
    print(f"  Carpetas listas en {raiz}")
    try:
        descargar_diccionario()
        print("  Diccionario de español listo.")
    except Exception as e:  # noqa: BLE001
        print(f"  No pude bajar el diccionario ({type(e).__name__}).")
        print("  Revisa tu internet y vuelve a ejecutar el instalador.")
        return 1
    return 0


def cmd_diagnostico(args) -> int:
    lineas = ["INFORME DE DIAGNÓSTICO — VideoQA para Windows", ""]
    lineas.append(f"Sistema: {platform.platform()}")
    lineas.append(f"Python: {sys.version.split()[0]} ({sys.executable})")
    lineas.append(f"ffmpeg: {shutil.which('ffmpeg') or 'NO ENCONTRADO'}")
    lineas.append(f"ffprobe: {shutil.which('ffprobe') or 'NO ENCONTRADO'}")
    lineas.append(f"nvidia-smi: {shutil.which('nvidia-smi') or 'no hay GPU NVIDIA visible'}")
    lineas.append("")
    lineas.append(f"Carpeta de trabajo: {trabajo_dir()} (existe: {trabajo_dir().exists()})")
    lineas.append(f"Carpeta de datos: {datos_dir()} (existe: {datos_dir().exists()})")
    lineas.append(f"Modelos: {modelos_dir()} (existe: {modelos_dir().exists()})")
    for nombre, modulo in (("rapidocr", "rapidocr_onnxruntime"), ("faster-whisper", "faster_whisper"),
                           ("spylls", "spylls"), ("motor videoqa", "videoqa")):
        try:
            __import__(modulo)
            lineas.append(f"{nombre}: OK")
        except Exception as e:  # noqa: BLE001
            lineas.append(f"{nombre}: FALLA ({type(e).__name__}: {e})")
    lineas.append("")
    registro = log_path()
    if registro.exists():
        lineas.append("Últimas líneas del registro:")
        lineas += registro.read_text(encoding="utf-8", errors="replace").splitlines()[-20:]
    texto = "\n".join(lineas) + "\n"
    destino = Path(args.salida) if args.salida else Path.home() / "Desktop" / "diagnostico.txt"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")
    print(texto)
    print(f"  Guardado en {destino}")
    return 0


def main(argv: list[str] | None = None) -> int:
    preparar_log()
    ap = argparse.ArgumentParser(prog="videoqa-win",
                                 description="Pre-chequeo local de videos antes de subirlos")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("instalar-datos", help="crear carpetas y bajar el diccionario")
    p.set_defaults(fn=cmd_instalar_datos)

    p = sub.add_parser("revisar", help="revisar archivos concretos o lo pendiente en 01_Entrada")
    p.add_argument("archivos", nargs="*")
    p.set_defaults(fn=cmd_revisar)

    p = sub.add_parser("watch", help="vigilar 01_Entrada")
    p.add_argument("--once", action="store_true")
    p.set_defaults(fn=cmd_watch)

    p = sub.add_parser("diagnostico", help="informe para soporte")
    p.add_argument("--salida")
    p.set_defaults(fn=cmd_diagnostico)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
