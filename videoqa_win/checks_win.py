"""Check de ortografía adaptado al OCR local.

El modelo de RapidOCR no lee las tildes, así que una palabra que solo difiere de
una válida en los acentos no se puede juzgar: sale como advertencia explicada,
no como bloqueante. Las faltas de verdad ("Aprobecha") siguen bloqueando.
"""
from __future__ import annotations

from videoqa.checks.spelling import WORD_RE
from videoqa.findings import Finding

TILDE_CHECK = "spelling_tilde_ocr"


def _palabras(texto: str) -> list[str]:
    return [w for w in WORD_RE.findall(texto) if len(w) >= 3]


def check_spelling_win(appearances: list[dict], glossary: set[str], rules: dict,
                       checker=None) -> list[Finding]:
    if checker is None:
        from videoqa_win.spell_spylls import SpyllsChecker

        checker = SpyllsChecker()

    sev = rules["severities"]
    sev_falta = sev["spelling_unknown_word"]
    sev_tilde = sev.get(TILDE_CHECK, "warning")
    min_conf = float(rules["thresholds"].get("ocr_min_conf", 0.5))

    salida: list[Finding] = []
    for i, a in enumerate(appearances):
        if float(a.get("conf", 1.0)) < min_conf:
            continue
        texto = a["text"]
        faltas, tildes = [], []
        for w in _palabras(texto):
            if w.lower() in glossary or checker.is_known(w):
                continue
            correcta = checker.tilde_probable(w)
            if correcta:
                tildes.append((w, correcta))
            else:
                faltas.append(w)

        if faltas:
            arreglos = ", ".join(f"{w} → {checker.correction(w) or '?'}" for w in faltas)
            salida.append(Finding(
                id=f"spell-{i}", type="ortografia", severity=sev_falta,
                t_start=a["t_start"], t_end=a["t_end"],
                title=f"Posible error ortográfico: {', '.join(faltas)}",
                detail=f'Texto en pantalla: "{texto}".', suggestion=arreglos,
                frame=a.get("frame"), bbox=a.get("bbox"), source="code",
                check="spelling_unknown_word"))

        if tildes:
            palabras = ", ".join(w for w, _ in tildes)
            arreglos = ", ".join(f"{w} → {c}" for w, c in tildes)
            salida.append(Finding(
                id=f"tilde-{i}", type="ortografia", severity=sev_tilde,
                t_start=a["t_start"], t_end=a["t_end"],
                title=f"Revisa las tildes: {palabras}",
                detail=(f'Texto en pantalla: "{texto}". El lector de texto de esta versión '
                        "no distingue las tildes, así que puede que en el video estén bien puestas. "
                        "Compruébalo a ojo en el video."),
                suggestion=arreglos, frame=a.get("frame"), bbox=a.get("bbox"),
                source="code", check=TILDE_CHECK))
    return salida
