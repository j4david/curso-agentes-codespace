# Agentes y automatización con IA: tu equipo en el navegador

Esta plantilla prepara un ordenador en la nube de GitHub (un *codespace*) con todo lo que necesitan los ejemplos 6, 9, 11, 11b y 12: **OpenCode**, **uv** con Python 3.13 y **llama.cpp**. No hay que instalar nada en tu ordenador: solo hace falta el navegador y una cuenta de GitHub.

Todos los datos de los ejemplos son ficticios.

## Crear tu codespace (una vez)

0. **Antes de crearlo**, en https://github.com/settings/codespaces, pon **Default idle timeout** en **60** minutos y pulsa **Save**. Si no, el codespace se para tras 30 minutos sin tocarlo, por ejemplo durante una explicación.
1. Arriba, pulsa **Use this template → Open in a codespace**.
2. Si te pide la clave **GOOGLE_API_KEY**, pega tu clave de Gemini (la de Google AI Studio). Si no la tienes aún, déjala en blanco.
3. Espera a que termine de prepararse (unos minutos la primera vez). Cuando el terminal diga «Listo», abre un terminal nuevo con el **+**.
4. Si VS Code pregunta si confías en los autores de la carpeta, pulsa **Confiar en la carpeta y continuar**.
5. **Tu clave de OpenRouter** (la del campus, para OpenCode): en el terminal, `opencode auth login -p openrouter` y pégala cuando la pida. Solo una vez.
6. **Tu clave de Gemini** (ejemplos 11, 11b y 12), si no la pusiste al crear el codespace: https://github.com/settings/codespaces → **New secret**, nombre `GOOGLE_API_KEY`, y en *Repository access* elige este repositorio. Después, reinicia el codespace. También vale un `.env` en la carpeta de cada ejemplo.

Para volver otro día: https://github.com/codespaces y abre el tuyo.

**Al terminar cada día, páralo:** en https://github.com/codespaces, menú **⋯** del tuyo → **Stop codespace**. Se para solo tras el tiempo de inactividad (60 minutos sin tocar VS Code), y lo que dejes ejecutándose (OpenCode, el modelo local) no lo mantiene encendido; aun así, pararlo a mano evita gastar horas de más. Si no has puesto tarjeta en GitHub, nunca te cobra: al agotar las horas, se bloquea hasta el mes siguiente. Puedes ver lo gastado en https://github.com/settings/billing/usage (despliega cada día con la flecha).

## Equivalencias con los enunciados

Los enunciados están escritos para Windows. Aquí cambia esto:

| En el enunciado | En el codespace |
|---|---|
| Abrir OpenCode en la carpeta del ejemplo | OpenCode ya está encendido. En la pestaña **Puertos** de VS Code, junto a «OpenCode (web)», pulsa el globo: se abre en una pestaña propia, a pantalla completa. Guarda esa dirección. Dentro, **Añadir proyecto**, escribe `/workspaces/curso-agentes-codespace/` y elige la carpeta del ejemplo |
| OpenCode en el terminal (opcional) | `cd ejemplo6` (o el que toque) y `opencode` |
| Descargar llama.cpp y el modelo, y `arrancar_decider.cmd` o `arrancar_modelo_local.cmd` | En un terminal aparte: `./arrancar_modelo.sh` (la primera vez descarga el modelo). Déjalo abierto |
| Copiar `.env.ejemplo` como `.env` y pegar la clave | No hace falta si pusiste la clave al crear el codespace. Si no: `cp .env.ejemplo .env` en la carpeta del ejemplo y edítalo |
| `$env:SOLO_GRABADAS = "1"` (ejemplo 11b) | `export SOLO_GRABADAS=1` |
| `uv sync`, `uv run python …` | Igual |

## Cuidado

- **No hagas público ningún puerto.** El aviso de «Convertir en público» no hace falta: con «Abrir en el navegador» solo entras tú.
- **No subas tu clave** a ningún sitio. El archivo `.env` está excluido para que no se guarde por error.
- El modelo local va más lento aquí que en un portátil: deja la batería de 30 correos corriendo y vuelve después.
- La cuenta gratuita de GitHub incluye 120 horas-núcleo al mes (60 horas con esta máquina) y 15 GB de almacenamiento. Cuando acabe el curso, borra el codespace desde https://github.com/codespaces.
