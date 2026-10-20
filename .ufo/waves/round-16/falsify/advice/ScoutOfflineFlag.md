VERDICT: confirm — `--offline` and the LLAMA_ARG_* env path in llama.cpp @704366d76 common/arg.cpp are as described, and the harness env allowlist excludes every env name the installed server registers (151 LLAMA_ARG_* + 3 non-ARG names; intersection with {PATH,HOME,LANG,LC_ALL,TMPDIR} is empty). One provenance gap and one adjacent config-file vector are noted; neither contradicts the claim.

# What I attacked

Claim: llama.cpp @ 704366d76 `common/arg.cpp` defines `--offline` and handles `LLAMA_ARG_*` environment variables such that the harness's 5-name child env allowlist removes every `LLAMA_ARG_*` influence.

Method: fetched the raw file at the pinned commit and the whole commit tarball, compared digests, inspected the installed b11755 binary's help/version and its env-parse behavior (help/parse paths only — no server started), ran the real harness with a fake `--server` under a deliberately polluted environment to observe the actual child env, and re-ran the receipt gate read-only.

# Sources and identities (observed)

- `common/arg.cpp` @704366d76 raw and tarball copies both sha256 `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d` (224650 bytes), fetched from `raw.githubusercontent.com/ggml-org/llama.cpp/704366d76.../common/arg.cpp` (HTTP 200) and `codeload.github.com/.../tar.gz/704366d76...` (tarball object sha256 `c2d31d5f462e899b580327d242c4fa6e61b704bcbd9dbcf6d4e7698ba3700749`).
- `common/download.cpp` @704366d76 sha256 `08374edafb1362be46f4c5abdf65e41d11664f32d3c0c7c209480da172838304` (HTTP 200).
- Pinned lane copy `server-common.cpp` digest matches `sources/pins.json` exactly (`b4f4aae7...`); raw `server.cpp` sha256 `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4` matches SOURCES S037.
- Installed binary `~/.local/opt/llama-b11755/llama-server --version` → exit 0: `version: 0.7.0-dev (build 11755, commit 704366d76)`. Live receipt `/props` `build_info` is `b11755-704366d76`, so the binary under test is the commit being cited.

# Findings

## 1. `--offline` is registered, server-visible, and env-settable

`common/arg.cpp:3972-3978`:
```
{"--offline"},
"Offline mode: forces use of cache, prevents network access",
[](common_params & params) { params.offline = true; }
).set_examples({LLAMA_EXAMPLE_COMMON, LLAMA_EXAMPLE_DOWNLOAD, LLAMA_EXAMPLE_TOKENIZE}).set_env("LLAMA_ARG_OFFLINE"));
```
It is a COMMON option (not a server-only flag); the server parser requests `LLAMA_EXAMPLE_SERVER` (`tools/server/server.cpp:113`, `common_params_parse(..., LLAMA_EXAMPLE_SERVER)`) and every non-DOWNLOAD example inherits COMMON (`arg.cpp:1434-1441`, `inherit_common = ex != LLAMA_EXAMPLE_DOWNLOAD`). `set_env` only appends the help annotation (`arg.cpp:96-99`) and stores the name. Empty `args_neg`, so no `LLAMA_ARG_NO_OFFLINE` compatibility lookup exists for it (`arg.cpp:125-143`).

Observed in the installed binary's help (exit 0), lines 215-216:
```
--offline                               Offline mode: forces use of cache, prevents network access
                                        (env: LLAMA_ARG_OFFLINE)
```
The real L1 run accepted it at runtime: `receipt.json` argv ends `["--no-webui","--offline"]` and the server reached `/health` 200 (all 10 checks true).

Semantics scope (correction to framing, not to the claim): `params.offline` is consumed only as `opts.offline` (`arg.cpp:395`) and as the download-run gate (`arg.cpp:693`); `common/download.cpp:456` routes to the online download path, 466 refuses a missing cache entry "in offline mode", 746 skips `hf_cache::get_repo_files` when offline. Grep of the whole commit tree shows no other `offline` use in `common/` or `tools/server/` except router child setup (`server-models.cpp:501-516`) and the two forced `cached.offline = true` helper paths. So `--offline` suppresses download network access, not arbitrary network calls; in this harness, `-m <local path>` with no `-hf`/`-mu`/`-dr` produces an empty download plan (`arg.cpp:403`, `475-497`; `-m` handler at `3048-3055` only sets `params.model.path`), so the flag is inert-but-harmless belt-and-braces here. [INFERENCE: source reading; no network capture was taken.]

## 2. LLAMA_ARG_* handling reads only registered names, exact and case-sensitive

Env names are registered per option via `set_env(...)`; the parse loop iterates only the example-filtered `ctx_arg.options` (`arg.cpp:787-810`) and calls `opt.get_value_from_env(value)` (`arg.cpp:125-143`), i.e. `std::getenv(env)` with no prefix scan, suffix scan, or generic `LLAMA_ARG_` sweep. Order: config file first (`arg.cpp:774-775`), then env, then CLI; a CLI flag whose env is also set prints `warn: %s environment variable is set, but will be overwritten by command line argument %s` (`arg.cpp:842-843`).

Observed at the binary level (no listener, `--help` path only):
- `env -i PATH=/usr/bin:/bin LLAMA_ARG_THREADS=blah llama-server --help` → exit 1, `error while handling environment variable "LLAMA_ARG_THREADS": stoi`.
- `env -i PATH=/usr/bin:/bin LLAMA_ARG_THREADS=7 llama-server -t 1 --help` → exit 0, `warn: LLAMA_ARG_THREADS environment variable is set, but will be overwritten by command line argument -t`.
- `env -i PATH=/usr/bin:/bin LLAMA_ARG_OFFLINE=1 llama-server --help` → exit 0. `is_truthy` accepts only `on|enabled|true|1` (`arg.cpp:1337-1339`), and because the handler is `handler_void`, a falsey `LLAMA_ARG_OFFLINE` cannot cancel the CLI `--offline`; there is no way for an env value to turn the flag off.

Env names visible from the installed server: `--help` prints `(env: NAME)` for each registered option. 154 unique names: 151 `LLAMA_ARG_*` plus `HF_TOKEN` (`--hf-token`, arg.cpp:3096), `LLAMA_API_KEY`, `MTMD_BACKEND_DEVICE`. (No `LLAMA_ARG_` name lacks the `LLAMA_ARG_` prefix except those three.)

Outside the registration mechanism, repo-wide grep for `getenv("LLAMA_ARG` in the commit tree returns nothing (tests aside, which use `setenv`), and the direct `getenv`/`common_get_env`/`common_get_path_from_env` literals are `APPDATA`, `HOME`, `PATH`, `PROGRAMDATA`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `LOCALAPPDATA`, `LLAMA_CACHE`, `LLAMA_TRACE`, `LLAMA_SERVER_*`, `LLAMA_APP_CMD`, `LLAMA_MEDIA_MARKER`, `LLAMA_SERVER_DEBUG_FAKE_TIMING`, `GGML_*`, `HF_ENDPOINT`, `MODEL_ENDPOINT`, `AIP_*`, `NO_COLOR`, `TERM`, `HTTP_PROXY`/`HTTPS_PROXY`/`NO_PROXY`, `LLGUIDANCE_LOG_LEVEL`. None begins `LLAMA_ARG_`.

## 3. Harness allowlist removes every LLAMA_ARG_* name (and the 3 sibling names)

Producer `tools/kama-llamacpp-live.py:71-73`:
```
CHILD_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')
```
`:784` builds `child_env = {k: os.environ[k] for k in CHILD_ENV_KEYS if k in os.environ}`; the server `Popen` receives `env=child_env` (`:819,824`) and the probe `subprocess.run(..., env=child_env)` (`:544-545`). No `shell=True` anywhere. Python's `env=` replaces rather than augments the environment; observed directly: a child run with `env={'PATH':...}` while the parent had `LLAMA_ARG_OFFLINE=1`/`LLAMA_API_KEY=k` printed only `PATH=/usr/bin:/bin`.

Set arithmetic: the binary's 154 registered names ∩ allowlist = ∅ (checked in Python; `comm` output was discarded because of locale sort order and re-done exactly). Therefore every `LLAMA_ARG_*` env var — including `LLAMA_ARG_OFFLINE`, `LLAMA_ARG_MODEL`, `LLAMA_ARG_CTX_SIZE`, `LLAMA_ARG_HOST`, `LLAMA_ARG_PORT`, `LLAMA_ARG_METRICS`, and legacy `LLAMA_ARG_NO_*` variants — is absent from the server's environment, as are the three non-ARG registered names `HF_TOKEN`, `LLAMA_API_KEY`, `MTMD_BACKEND_DEVICE`.

End-to-end observation (fake server; no llama-server started): ran the real harness with `--server /tmp/.../fake/llama-server` (a two-line `#!/bin/sh` that dumps `env`) under `LLAMA_ARG_OFFLINE=1 LLAMA_ARG_CTX_SIZE=99999 LLAMA_ARG_METRICS=1 LLAMA_ARG_API_KEY=sekret HF_TOKEN=tok MTMD_BACKEND_DEVICE=cuda0 LLAMA_CACHE=/tmp/x LLAMA_TRACE=1 HTTP_PROXY=http://127.0.0.1:1 KAMA_TEST=1`. Harness exit 2 with `setup_error server-exited-early-rc0` (expected). The fake child's env contained only `PWD`, `HOME`, `LANG`, `SHLVL`, `PATH`, `_` — the latter three are shell additions from the `sh` fake itself, not harness-passed; grep for the polluted names returned 0 matches. Receipt `child_env_keys` was `["HOME","LANG","PATH"]`, argv tail `["--no-webui","--offline"]`, port 42485 (ephemeral, not 8080/34113), `pgrep -x llama-server` = 0.

Gate: `tests/llamacpp-live/check-receipt.py` duplicates the allowlist as `CHILD_ENV_ALLOWLIST` (`:49`), enforces `child_env_keys ⊆ allowlist` and sorted-unique (`:301-314`), and requires the argv tail (`:333-334`). Imported both modules: `set(gate.CHILD_ENV_ALLOWLIST) == set(harness.CHILD_ENV_KEYS)` → True. Re-ran read-only on the live receipt:
```
$ python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json
VALID .ufo/waves/round-16/live/receipt.json
gate_exit=0
```
(An earlier invocation with `--receipt` was a usage error, exit 2; the CLI takes a positional path.) The live receipt itself records `child_env_keys ["HOME","LANG","PATH"]` and all 10 checks true.

# Limitations / residual gaps

- The gate sees only declared key names, never values or the kernel-observed environment; it is claim-checking, not strace. The producer code plus the fake-server observation are what establish the actual env. [INFERENCE, mitigated by observation above]
- `HOME` is allowlisted, and llama.cpp loads config files unconditionally: `/etc/llama.cpp/config.ini` and `${XDG_CONFIG_HOME:-~/.config}/llama.cpp/config.ini` (`arg.cpp:723-771`, `common.cpp:1017-1024`; `XDG_CONFIG_HOME` is stripped, so `$HOME/.config` applies). Neither file exists on this host (`ls` → ENOENT), so the L1 run was unaffected; on a different host a config file could set parameters the harness never passes. This is config-file influence, not `LLAMA_ARG_*` env influence, and does not refute the claim — but "the child env allowlist isolates the child" is not full launch isolation. [INFERENCE for the hypothetical host]
- `PATH` is allowlisted and is read by llama.cpp only to locate `llama-connect` for the connect feature (`tools/server/server-connect.cpp:147`); `HOME` drives config/cache location. Neither is `LLAMA_ARG_*`. The Hugging Face cache directory selection reads `LLAMA_CACHE`, `HF_HUB_CACHE`, `HUGGINGFACE_HUB_CACHE`, `HF_HOME`, `XDG_CACHE_HOME`, `HOME` (`common/hf-cache.cpp:33-46`); all but `HOME` are stripped and none is `LLAMA_ARG_*`. With a local `-m` path no HF cache lookup occurs. [INFERENCE from source]
- The lane's pinned source set does not include `common/arg.cpp`: `sources/pins.json` lists README.md, server-common.cpp, server-common.h, server-http.cpp only (server.cpp is present in the directory with the SOURCES S037 digest but absent from the pins map). The `--offline`/`LLAMA_ARG_*` statement therefore rests on an unpinned file. I verified the raw file against the commit tarball (same sha256) and against the installed binary's help/version, but for reproducibility L1 should add `common/arg.cpp` (and `common/download.cpp` if the offline semantics are cited) to the pin manifest with sha256 `bf4c58c1...` / `08374eda...`.
- The vendor help wording "prevents network access" overstates the implementation, which gates only download paths; with `-m` local no download task is even built. No lane artifact claims more than `--offline` presence, so no lane statement is falsified.
- The knowledge doc line "Child environment: `HOME`, `LANG`, `PATH` only" matches the observed run; the allowlist itself is 5 names and `LC_ALL`/`TMPDIR` were simply absent from the operator env. Accurate, and worth keeping that distinction.

Installs/updates: none (no pacman, uv, npm, or binary installs were performed).

Scratch `/tmp/kama-r16-ScoutOfflineFlag/` held the fetched sources, tarball, fake server, help/version captures and polluted-env receipts; removed after this report.
