# VideoQA para Windows

Pre-chequeo local de videos antes de subirlos a Drive. Corre en el PC del editor, sin cuenta de
ninguna IA en la nube: revisa ortografía, colores de marca, zona segura, pantallas negras,
silencios y transcribe lo que se dice.

**No sustituye la revisión oficial.** El gate de publicación sigue en la Mac de la revisora, con
el motor [`videoqa`](https://github.com/hongs05/videoqa) y el plugin `aura`. Esto es para llegar
limpio a esa revisión.

- **Si eres el editor** → lee [`LEEME.md`](LEEME.md): instalar y usar, sin tecnicismos.
- **Si vas a desarrollar** → sigue leyendo.

## Cómo funciona

Usa el motor `videoqa` como librería y le registra tres implementaciones que no dependen de macOS:

| Pieza | Aquí | En la Mac |
|---|---|---|
| Texto en pantalla | RapidOCR (onnxruntime) | Apple Vision |
| Transcripción | faster-whisper (CTranslate2) | Whisper en MLX |
| Ortografía | spylls + diccionario de LibreOffice | corrector de macOS |
| Criterio | Ollama (opcional, apagado) | Claude |

Todo lo demás —checks de color y tiempos, reporte, carpetas, watcher— viene del motor, así que
"revisar" significa lo mismo en las dos máquinas.

## Desarrollo

```bash
uv sync
uv run pytest -q                      # rápido: sin modelos
VIDEOQA_WIN_LENTO=1 uv run pytest -q  # incluye los que descargan modelos
```

Los `.bat`, `winget` y el arranque automático **solo se pueden validar en un Windows real**: aquí
se comprueba su forma (cabecera, saltos CRLF, rutas citadas) con `tests/unit/test_bat.py`.
