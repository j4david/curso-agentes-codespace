#!/usr/bin/env bash
# Se ejecuta al encender el codespace y al abrirlo: deja OpenCode web
# escuchando en el puerto 4096 (dirección privada, solo para ti).
# Registro en ~/opencode-web.log.
export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$HOME/llama:$PATH"
cd "$(dirname "$0")/.."
if pgrep -f "opencode web --port 4096" >/dev/null; then
  exit 0
fi
nohup setsid bash -c 'exec opencode web --port 4096 --hostname 127.0.0.1' \
  > "$HOME/opencode-web.log" 2>&1 < /dev/null &
disown
sleep 3
