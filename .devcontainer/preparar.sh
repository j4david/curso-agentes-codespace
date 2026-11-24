#!/usr/bin/env bash
# Se ejecuta una sola vez, al crear el codespace: instala OpenCode, uv y llama.cpp
# y prepara los entornos de Python de los ejemplos 11, 11b y 12.
set -e
cd "$(dirname "$0")/.."

echo "== OpenCode"
curl -fsSL https://opencode.ai/install | bash

echo "== uv"
curl -LsSf https://astral.sh/uv/install.sh | sh

echo "== llama.cpp (versión b12359, la del ejemplo 9)"
mkdir -p "$HOME/llama"
curl -fsSL https://github.com/ggml-org/llama.cpp/releases/download/b12359/llama-b12359-bin-ubuntu-x64.tar.gz \
  | tar xz -C "$HOME/llama" --strip-components=1

grep -q 'curso-agentes' "$HOME/.bashrc" || cat >> "$HOME/.bashrc" <<'EOF'
# curso-agentes
export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$HOME/llama:$PATH"
EOF
export PATH="$HOME/.opencode/bin:$HOME/.local/bin:$HOME/llama:$PATH"

echo "== Entornos de Python de los ejemplos 11, 11b y 12"
for d in ejemplo11 ejemplo11b ejemplo12; do
  (cd "$d" && uv sync -q)
done

chmod +x arrancar_modelo.sh
echo "== Listo. Abre un terminal nuevo para empezar."
