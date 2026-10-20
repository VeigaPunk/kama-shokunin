## Ephemeral lane-owned llama.cpp runtime (round 16, C2 capability)

**What it is.** A short-lived `llama-server` process that the lane's live harness
(`tools/kama-llamacpp-live.py`, planned, not yet present at 2026-10-20) launches for one
receipt run, probes with `tools/kama-probe.sh`, and then tears down with a recorded
teardown proof. Its inputs are fixed and digest-pinned:

- **Server binary:** official llama.cpp release `b11755` (commit `704366d76`), extracted to
  `~/.local/opt/llama-b11755/`, reached through the symlink `~/.local/bin/llama-server`. The
  release asset `llama-b11755-bin-ubuntu-x64.tar.gz` has SHA-256
  `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`, which matches the GitHub
  release API digest and the local tarball at `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`.
  The local binary reports `version: 0.7.0-dev (build 11755, commit 704366d76)`.
- **Model:** a tiny pinned GGUF, `~/.cache/kama-shokunin/models/stories260K.gguf`, SHA-256
  `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`. The harness must verify
  this digest before launch.
- **Listener:** a free loopback port chosen by the harness. It must not be a registered
  consumer port (see below). The upstream default for `--port` is `9931` and for `--host` is
  `127.0.0.1`; the harness is expected to pass both explicitly.

**What it is for.** It lets the lane observe the documented lifecycle surfaces of a real
llama.cpp server on this host: the `503 Loading model` state, then ready `/health`,
`/v1/models`, and `/slots`. It also gives `kama-probe` a live target whose verdict
(`MODEL_LOADING` vs `MODEL_OK` vs `FOREIGN_SERVICE`) can be checked against a known model.

**What it is not.**

- It is **not service restoration.** Nothing here re-creates, enables, starts, or repoints a
  unit. The formerly pinned `~/.config/systemd/user/qwen-coder.service` is absent: `ls` reports
  "No such file or directory" on 2026-10-20.
- It does **not** change the registered consumers. `registry/endpoint-consumers.tsv` rows
  `omp-llama-cpp-default` (`8080`) and `ufo-fsd-thetick` / `ufo-fsd-local-helper` (`34113`)
  stay `DEAD` in the lane's sample. On 2026-10-20 `ss -ltn` shows no listener on either
  port. The live runtime never binds them.
- It writes **nothing** to `~/.config`, `~/.omp`, or systemd. The lane's hard write boundary
  is unchanged.
- It is **not evidence about performance, model quality, or real-deployment readiness.** The
  model is a 260K-parameter test fixture. A passing receipt establishes only the serving
  surfaces and the probe verdict mapping for that process.
- It is **not a standing service.** Its lifetime is one harness run; teardown is required on
  every exit path.

**Sources (accessed 2026-10-20).**

- llama.cpp release `b11755`, API JSON, `https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11755`: asset `llama-b11755-bin-ubuntu-x64.tar.gz` carries `"digest": "sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226"` and `"prerelease": true` (flag on the release object). Also `"target_commitish": "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"`.
- `tools/server/server-http.cpp` at b11755, `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/server-http.cpp:307-325` (`middleware_server_state`): the "Loading model" 503 body is returned for non-frontend paths while the server is not ready, quoted at `:312`: "no endpoints are allowed to be accessed when the server is not ready".
- `tools/server/README.md` at b11755, `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md:479-487` (`GET /health`): the 503 body is `"Loading model"`, explained as "the model is still being loaded."; defaults for `--host` (`127.0.0.1`) and `--port` (`9931`) appear at README lines 193-194.
- Local host: `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` SHA-256 `753bfa73…a6e226`; `~/.cache/kama-shokunin/models/stories260K.gguf` SHA-256 `270cba18…d256d`; `~/.local/opt/llama-b11755/llama-server --version` prints `version: 0.7.0-dev (build 11755, commit 704366d76)`.
- Lane `PROVINCE.md:45`: "kama never writes to `~/.config`, `~/.omp`, or systemd units."
- Lane `registry/endpoint-consumers.tsv:35-37`: registered consumers pin `127.0.0.1:8080` and `127.0.0.1:34113`.
- Lane `corpus/QUALITY.md:13` (KQ5): a training admission "requires enabling services, repointing consumers, installing timers" is rejected.

**Unknown or unverified in this note.**

- The upstream provenance of `stories260K.gguf` (Hugging Face repo, redirect, license) was not checked here. Only the local SHA-256 was observed. A separate scout item covers that.
- The `tools/kama-llamacpp-live.py` harness, its teardown proof, and any live receipt do not exist yet. Nothing in this note is observed behavior of that harness.
- The exact line where the llama.cpp server releases the 503 state after model load was not traced in source. The note relies only on the middleware's `is_ready` check.
- Whether the release `prerelease` flag affects anything the lane should rely on was not investigated.
