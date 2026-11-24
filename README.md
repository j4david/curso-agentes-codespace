# Agentes y automatización con IA: tu equipo en el navegador

Esta plantilla prepara un ordenador en la nube de GitHub (un *codespace*) con todo lo que necesitan los ejemplos 6, 9, 11, 11b y 12: **OpenCode**, **uv** con Python 3.13 y **llama.cpp**. No hay que instalar nada en tu ordenador: solo hace falta el navegador y una cuenta de GitHub.

Todos los datos de los ejemplos son ficticios.

## Crear tu codespace (una vez)

1. Arriba, pulsa **Use this template → Open in a codespace**.
2. Si te pide la clave **GOOGLE_API_KEY**, pega tu clave de Gemini (la de Google AI Studio). Si no la tienes aún, déjala en blanco.
3. Espera a que termine de prepararse (unos minutos la primera vez). Cuando el terminal diga «Listo», abre un terminal nuevo con el **+**.
4. Si VS Code pregunta si confías en los autores de la carpeta, pulsa **Confiar en la carpeta y continuar**.

Para volver otro día: https://github.com/codespaces y abre el tuyo. Se para solo si no lo usas.

## Equivalencias con los enunciados

Los enunciados están escritos para Windows. Aquí cambia esto:

| En el enunciado | En el codespace |
|---|---|
| Abrir OpenCode en la carpeta del ejemplo | En el terminal: `cd ejemplo6` (o el que toque) y `opencode` |
| La ventana de OpenCode | `opencode web --port 4096`, y en el aviso pulsa **Abrir en el navegador** |
| Descargar llama.cpp y el modelo, y `arrancar_decider.cmd` o `arrancar_modelo_local.cmd` | En un terminal aparte: `./arrancar_modelo.sh` (la primera vez descarga el modelo). Déjalo abierto |
| Copiar `.env.ejemplo` como `.env` y pegar la clave | No hace falta si pusiste la clave al crear el codespace. Si no: `cp .env.ejemplo .env` en la carpeta del ejemplo y edítalo |
| `$env:SOLO_GRABADAS = "1"` (ejemplo 11b) | `export SOLO_GRABADAS=1` |
| `uv sync`, `uv run python …` | Igual |

## Cuidado

- **No hagas público ningún puerto.** El aviso de «Convertir en público» no hace falta: con «Abrir en el navegador» solo entras tú.
- **No subas tu clave** a ningún sitio. El archivo `.env` está excluido para que no se guarde por error.
- El modelo local va más lento aquí que en un portátil: deja la batería de 30 correos corriendo y vuelve después.
- La cuenta gratuita de GitHub incluye 120 horas-núcleo al mes (60 horas con esta máquina) y 15 GB de almacenamiento. Cuando acabe el curso, borra el codespace desde https://github.com/codespaces.
