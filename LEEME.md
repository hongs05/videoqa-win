# VideoQA — revisa tus videos antes de subirlos

Esta herramienta revisa un video en tu PC y te dice qué corregir **antes** de que lo subas a
Drive. Así evitas que te lo devuelvan por cosas como una palabra mal escrita o un color que no es
de la marca.

No reemplaza la revisión oficial: esa sigue haciéndose después. Esto es para que llegues limpio.

## Instalar (una sola vez, ~15 minutos)

1. Descomprime el archivo que te pasaron.
2. Haz doble clic en **`Instalar VideoQA.bat`**. Si Windows avisa que es de un origen desconocido,
   elige **Más información → Ejecutar de todas formas**.
3. Espera. Cuando termine, en tu Escritorio aparecen cuatro accesos: **Revisar video**,
   **Activar automatico**, **Diagnostico** y **Actualizar VideoQA**.

## Usar

**La forma rápida:** arrastra el video encima de **Revisar video** y espera. Al terminar se abre
el reporte en el navegador.

**La otra forma:** deja los videos en `C:\Users\<tu usuario>\VideoQA\01_Entrada` y haz doble clic
en **Revisar video**.

**Para que lo haga solo:** doble clic en **Activar automatico**. Desde entonces, todo lo que dejes
en `01_Entrada` se revisa sin que hagas nada. Para apagarlo, doble clic otra vez.

## Qué te va a decir

Cada video acaba en una de dos carpetas, con su reporte al lado:

- **`03_Aprobado`** 🟢 — no encontró nada que corregir. Súbelo.
- **`02_Con_errores`** 🔴 — hay cosas que arreglar. Abre **`reporte.html`**: cada problema viene
  con el segundo exacto y una foto del momento.

También te deja `guion_real.md`, que es la transcripción de lo que realmente se dice en el video.

## Cosas que conviene saber

- **La primera revisión tarda mucho más** (descarga un modelo de voz de unos 250 MB). Solo pasa
  una vez.
- **Las tildes**: esta versión lee el texto del video pero no distingue los acentos, así que
  cuando te avise de una tilde, compruébalo a ojo — puede estar bien puesta.
- **Palabras que marca mal**: si marca como error un nombre de marca o una palabra que usan
  ustedes, añádela al archivo `VideoQA\_config\glosario.txt`, una por línea.
- **Lo que esta versión no ve**: bloopers, incoherencias entre lo que se dice y lo que se escribe,
  y el tono. Eso lo revisa la revisión oficial después.
- **Si algo falla**: doble clic en **Diagnostico**, y manda por chat el `diagnostico.txt` que deja
  en el Escritorio.
