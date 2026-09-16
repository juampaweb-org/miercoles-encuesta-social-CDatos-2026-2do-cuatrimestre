# miercoles-encuesta-social-CDatos-2026-2do-cuatrimestre
Resultados de Encuesta Social de Miércoles de C Datos de ISTEA 2026 - 2do cuatrimestre

## Cómo generar los gráficos y la web

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python analizar_encuesta.py
```

`source .venv/bin/activate` activa el entorno virtual (en Windows es
`.venv\Scripts\activate`): mientras esté activo, `pip` y `python` usan la
copia del entorno virtual en vez de la instalación global. Para salir del
entorno virtual alcanza con ejecutar `deactivate`.

Esto genera la carpeta `output/` con los gráficos (`output/graficos/*.png`) y
`output/index.html`, que se puede abrir directamente en el navegador (no
necesita servidor).

El código fuente está en `analizar_encuesta.py`, pensado para poder leerse
de punta a punta (solo usa la librería estándar de Python + matplotlib).
