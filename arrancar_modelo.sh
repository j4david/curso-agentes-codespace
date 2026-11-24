#!/usr/bin/env bash
# Arranca el modelo local de los ejemplos 9 y 11b (http://127.0.0.1:8092).
# La primera vez descarga el modelo (812 MB, unos segundos).
# Deja este terminal abierto mientras lo uses; para pararlo, Ctrl+C.
set -e
MODELO="$HOME/modelos/decider-0.8b.Q8_0.gguf"
if [ ! -f "$MODELO" ]; then
  mkdir -p "$HOME/modelos"
  echo "Descargando el modelo (812 MB)..."
  curl -fL -o "$MODELO" https://huggingface.co/mradermacher/decider-0.8b-GGUF/resolve/main/decider-0.8b.Q8_0.gguf
fi
exec "$HOME/llama/llama-server" -m "$MODELO" --host 127.0.0.1 --port 8092 \
  -c 8192 -b 4096 -ub 2048 --parallel 1
