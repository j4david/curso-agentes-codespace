# Ejemplo 11b · Una segunda opinión

Dos modelos clasifican el mismo correo **a la vez**: Gemini, en la nube, y un modelo pequeño (decider-0.8b) en tu ordenador. El **código** compara: si coinciden, el correo sigue solo; si no, va a una persona con las dos opiniones.

**No hace falta haber hecho los ejemplos anteriores.** Si no tienes la clave de Gemini o el modelo local no está encendido, ese modelo usa su **opinión grabada** (la que dio en nuestras pruebas, en `grabadas/`). Al empezar, el programa dice cuál va en directo y cuál grabada.

## Empezar

```text
uv sync
uv run python probar_sin_clave.py
uv run python correo.py 14
uv run python bateria.py
```

Opcional:
- **Nube en directo:** copia `.env.ejemplo` como `.env` y pega tu clave de Gemini.
- **Local en directo:** pon llama.cpp en la carpeta `llama` y `decider-0.8b.Q8_0.gguf` en la carpeta `modelo` (enlaces en el enunciado), y haz doble clic en `arrancar_modelo_local.cmd`.
- **Forzar las grabadas** aunque tengas las dos cosas: en PowerShell, `$env:SOLO_GRABADAS = "1"` antes de lanzar las órdenes.

## Archivos

| Archivo | Qué es |
|---|---|
| `grafo.py` | El grafo: dos opiniones a la vez, comparar y decidir. La regla está en `elegir_camino` y el umbral en `UMBRAL_LOCAL` |
| `local.py` | Cómo se pregunta al modelo local |
| `correo.py` | Un correo, paso a paso |
| `bateria.py` | Los correos (todos o los que digas) y la cuenta de aciertos |
| `probar_sin_clave.py` | Pruebas de la regla, sin modelos |
| `dibujar.py` | El dibujo del grafo (`dibujo.md` y `dibujo.png`) |
| `correos.json`, `bateria.csv` | Los 30 correos ficticios y su categoría correcta |
| `preguntas_local.json` | La pregunta y las opciones que ve el modelo local |
| `grabadas/` | Las opiniones de los dos modelos en nuestras pruebas |

Todo es ficticio y simulado: no se envía ni se archiva nada.
