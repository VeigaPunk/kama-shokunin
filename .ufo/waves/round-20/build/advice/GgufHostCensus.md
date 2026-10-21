VERDICT: partial - Current census found one GGUF, but cannot prove round-start filesystem state.

# GGUF host census

- `id -un` exited 0; stdout: `vgpnk` (lane user). The final census run was preceded by `date -Is`, exit 0, stdout: `2026-10-21T04:27:15-03:00`.
- Exact census command:
  ```
  find /home/vgpnk -xdev \( -name '*.gguf' -o -path '*/.ollama/models/blobs/*' \) -type f -readable 2>/dev/null
  ```
  Executed immediately after that timestamp; exit 0. Stdout contained exactly `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`.
- `stat -c '%s %n' /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` exited 0; stdout: `1185376 /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`.
- `head -c 4 /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf | xxd -p` exited 0; stdout: `47475546` (bytes `GGUF`). The TSV row therefore has `is_gguf=true`; the census returned one path total.
- `test -d /home/vgpnk/.ollama` exited 1; result: absent. The census returned no Ollama blob paths.
- Population TSV: `.ufo/waves/round-20/build/out/GgufHostCensus/population.tsv` (header plus one row; magic is hex bytes).

## Scope limitation

This is a live host observation, not a historical filesystem snapshot. [INFERENCE] It cannot establish that this was the complete set readable at round start, or that no matching files changed between round start and this scan. Treat the TSV as a current census candidate pending historical-state confirmation.
