#!/usr/bin/env bash
# Se ejecuta cada vez que se enciende el codespace: deja OpenCode web
# escuchando en el puerto 4096 (dirección privada, solo para ti).
export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$HOME/llama:$PATH"
cd "$(dirname "$0")/.."
if ! pgrep -f "opencode web" >/dev/null; then
  setsid nohup opencode web --port 4096 --hostname 127.0.0.1 > /tmp/opencode-web.log 2>&1 < /dev/null &
fi
