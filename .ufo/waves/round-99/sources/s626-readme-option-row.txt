# S626 candidate (reject) — llama.cpp tools/server/README.md @ tag b12177
url: https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/README.md
accessed: 2026-11-08 (curl HTTP 200, 136429 bytes)
sha256: eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137
line 234:
| `--models-autoload, --no-models-autoload` | for router server, whether to automatically load models (default: enabled)<br/>(env: LLAMA_ARG_MODELS_AUTOLOAD) |
line 2165:
By default, the model will be loaded automatically if it's not loaded. To disable this, add `--no-models-autoload` when starting the server. Additionally, you can include `?autoload=true|false` in the query param to control this behavior per-request.
