#!/usr/bin/env bash
# E4a: fake HOME whose .local/opt/llama-b11755/llama-server is the fake script
set -e
FH=/tmp/kama-r27-noreader/fakehome_fake
rm -rf "$FH"; mkdir -p "$FH/.local/opt/llama-b11755" "$FH/.cache/kama-shokunin/models"
cp /tmp/kama-r27-noreader/fake-llama-server.py "$FH/.local/opt/llama-b11755/llama-server"
chmod +x "$FH/.local/opt/llama-b11755/llama-server"
ln -sf "$HOME/.local/opt/llama-b11755/libllama-server-impl.so" "$FH/.local/opt/llama-b11755/libllama-server-impl.so"
ln -sf "$HOME/.cache/kama-shokunin/models/stories260K.gguf" "$FH/.cache/kama-shokunin/models/stories260K.gguf"
python3 /tmp/kama-r27-noreader/gen.py /tmp/kama-r27-noreader/spec_real.json "$1"
