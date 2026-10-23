#!/usr/bin/env bash
# E4b: fake HOME whose .local/opt/llama-b11755 is a symlink to the real install
set -e
FH=/tmp/kama-r27-noreader/fakehome_real
rm -rf "$FH"; mkdir -p "$FH/.local/opt" "$FH/.cache/kama-shokunin/models"
ln -sfn "$HOME/.local/opt/llama-b11755" "$FH/.local/opt/llama-b11755"
ln -sf "$HOME/.cache/kama-shokunin/models/stories260K.gguf" "$FH/.cache/kama-shokunin/models/stories260K.gguf"
python3 /tmp/kama-r27-noreader/gen.py /tmp/kama-r27-noreader/spec_real.json "$1"
