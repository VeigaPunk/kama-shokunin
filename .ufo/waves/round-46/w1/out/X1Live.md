# X1Live — live lifecycle run at b11906 (freshness frontier for S041/S046/S055/S485, r45 closure D3)

**Verdict:** PASS — b11906 (4d71b42fd) installed from the official asset with the release digest verified, stories260K re-fetched at the pinned sha256, and three independent kama-llamacpp-live/v3 runs each returned outcome `pass` with 11/11 checks evaluated and true, `build_info b11906-4d71b42fd`, ready `/health` body exactly `{"status":"ok"}`, `/metrics` 501, teardown SIGTERM-only returncode 0 in 3 ms, `sigkill_sent=false`, port closed after teardown.

## 1. Install identity (item step 1)

Release JSON (`gh api repos/ggml-org/llama.cpp/releases/tags/b11906`, exit 0) at `.ufo/waves/round-46/w1/out/X1Live/release-b11906.json`:

- asset `llama-b11906-bin-ubuntu-x64.tar.gz`, 22478121 bytes, digest `sha256:064ade6220799fd9e7b1804b574f5f92c38dde358cc987c6b8283cfaeb1eeef3` — **equals the digest frozen in the item**.
- `target_commitish` = `4d71b42fd87db24b8b7c808c151b713aa4459cfd`, published 2026-10-26T19:45:36Z.
- Downloaded with `curl -fL --retry 3` (exit 0); `sha256sum` of the downloaded tarball re-computed and equal to the release digest (checked twice, after download and after extraction).
- Extracted to a single top directory `llama-b11906/`; installed with `cp -a` at **`/home/vgpnk/.local/opt/llama-b11906/`** (official release binary; round-45 precedent `llama-b11889`; `/home/vgpnk/.local/opt` is not a PATH directory).
- `llama-server` sha256 `c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff`; `libllama-server-impl.so` sha256 `682717ba312caefda06be7b2e5a637d8af357ff1f1264f6f5624dc53212a8223`.
- `llama-server --version` (exit 0): `version: 0.7.0-dev (build 11906, commit 4d71b42fd)` / `built with GNU 11.4.0 for Linux x86_64` — the commit prefix matches b11906 `4d71b42f`.
- Recorded in `.ufo/waves/round-46/c1/live/install.txt` (asset, release digest, target commit, install path, both sha256 lines, `--version`, plus `install_tree_sha256 89fbc38997001c02fe7daae0fcc32c6aa9e7c585f455d8809ddefe42ed7bdf0f` and `install_links_sha256 5cb9f486…` with no unpinned links).
- Harness instrument: `tools/kama-llamacpp-live.py` sha256 `8c0dbb2b60da4d0e89ebe537b2f36b0b59356efedbe5f66c7364bdb6c8f662f3` — unchanged from the round-45 S485 row, so this is the same instrument applied to a new build, not a new instrument.

## 2. Model (item step 2, closes r45 D3)

`/home/vgpnk/.cache/kama-shokunin/models/` did not exist (`ls` exit 2 on that path) — the round-44/45 copy was gone, confirming the D3 premise. Re-created and fetched:

- URL: `https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf` (`curl -fL --retry 3`, exit 0)
- path `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`, **1185376 bytes**
- sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` — **equals the expected digest**, so the run proceeded. The harness re-hashed the model after each run (`model_unchanged` true, pre = post = `270cba1b…256d`).
- Recorded in `.ufo/waves/round-46/c1/live/model-fetch.txt` (url, path, size, sha256, `fetched_utc 2026-10-26T19:57:36Z`, curl exit 0).

## 3. Live runs (item step 3)

Command (identical for N = 1, 2, 3; `TMPDIR=/fast/scratch/hyaku/kama-r46/X1Live`):

```
python3 tools/kama-llamacpp-live.py \
  --server /home/vgpnk/.local/opt/llama-b11906/llama-server \
  --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf \
  --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --alias kama-r46-live --ctx 256 --threads 1 \
  --out .ufo/waves/round-46/c1/live/receipt-N.json
```

All three invocations exited **0**; receipts at `.ufo/waves/round-46/c1/live/receipt-{1,2,3}.json` (schema `kama-llamacpp-live/v3`):

| receipt | outcome | checks passed/evaluated | build_info | ready /health | /metrics | teardown rc | term_wait_ms | sigkill_sent | port | loading 503s (distinct bodies) |
|---|---|---|---|---|---|---|---|---|---|---|
| receipt-1 | pass | 11/11 (0 not-evaluated) | `b11906-4d71b42fd` | 200 `{"status":"ok"}` | 501 | 0 | 3 | false | 33179 | 35 (1) |
| receipt-2 | pass | 11/11 (0 not-evaluated) | `b11906-4d71b42fd` | 200 `{"status":"ok"}` | 501 | 0 | 3 | false | 46073 | 24 (1) |
| receipt-3 | pass | 11/11 (0 not-evaluated) | `b11906-4d71b42fd` | 200 `{"status":"ok"}` | 501 | 0 | 3 | false | 44923 | 27 (1) |

Per-receipt fields (all three byte-level equal apart from port/timing; `sha256` of the receipt files themselves in `summary.json`):

- `setup_error` null, `internal_fault` null, `outcome pass`; wall time 157/159/160 ms (`started_utc`→`ended_utc`, e.g. receipt-1 `2026-10-26T19:57:39.317Z`→`…39.474Z`).
- Checks (`checks[].passed`): `health_ready`, `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`, `probe_mismatch`, `teardown_graceful`, `teardown_port_closed`, `loading_envelope_graded`, `model_unchanged` — all true, none not-evaluated.
- `captures.props.fields.build_info` = `b11906-4d71b42fd`; `n_ctx` 256; `model_alias` `kama-r46-live`; `total_slots` 4.
- `captures.health` = 200, body verbatim `{"status":"ok"}`, sha256 `a29ee2b1…c13d288`, `Server: llama.cpp`.
- `captures.metrics` = **501** (metrics endpoint not enabled — the documented b11755-and-later behaviour).
- `captures.models` data id `kama-r46-live`, `owned_by llamacpp`.
- `teardown`: `sigterm_sent true`, `sigkill_sent false`, `returncode 0`, `term_wait_ms 3`, `alive_at_teardown_start true`, `port_refuses true`; `port_listener_ownership child` (the child, not a stranger, owned the LISTEN socket).
- `loading_envelope_graded`: `loading_observed true`, `all_exact true`, every distinct 503 body = `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` (body sha256 `baa09177700f64520a799fd2628bb3663c1486b25e17e4a507f2e6c81bef957c`).
- Probe pair per run: `probe_model_ok` exit 0 verdict `MODEL_OK`; `probe_mismatch` exit 2 verdict `MODEL_MISMATCH` (served-id-mismatch) — the fail-capable side still fails on a wrong expected alias.
- Ports 33179/46073/44923 are all absent from `port_refusal_set` (`port_in_refusal_set false`), i.e. no registered consumer port was used.
- `child_env_keys` = `[HOME, LANG, PATH, TMPDIR]` (names only), `pdeathsig.requested true`.

## 4. Cross-build observation (frontier value for S041/S046/S055/S485)

Against the round-45 b11889 receipts (same tool sha256, same model sha256):

| | b11889 (round-45 receipt-1) | b11906 (round-46 receipt-1) |
|---|---|---|
| build_info | `b11889-d854d98ba` | `b11906-4d71b42fd` |
| checks | 11/11 | 11/11 |
| ready /health | `{"status":"ok"}` | `{"status":"ok"}` |
| /metrics | 501 | 501 |
| loading-503 body sha256 | `baa09177…bef957c` | `baa09177…bef957c` (identical across all three runs) |
| teardown rc / term_wait_ms / sigkill | 0 / 15 / false | 0 / 3 / false |
| 503 count | 25 | 35 |

So the three lifecycle propositions the live rows assert (exact ready health body, exact loading envelope, SIGTERM-only teardown with no SIGKILL) hold unchanged 17 commits later at b11906; only timing numbers differ, which those rows' scope already excludes ("sampled instants; not … general timing"). The 503 count varies with poll phase, not build.

## 5. Hygiene

- `pgrep -af llama-server` → no match (exit 1): no server left behind.
- Loopback connects to 33179/46073/44923 all refused after teardown (matches each receipt's `teardown.port_refuses true`).
- Lane working tree unchanged by this seat: `git status --porcelain` shows only the wave's own untracked paths (`?? .ufo/waves/round-46/c1/`, `…/w1.ready*`, `…/w1/out/`); no tracked file touched, no jj/git mutation.
- Scratch `/fast/scratch/hyaku/kama-r46/X1Live` removed after copying evidence; no `/tmp` path is cited anywhere.
- No pacman, no package manager: only an official release tarball extracted under `/home/vgpnk/.local/opt/llama-b11906/` (allowed by the item) and a pinned model file in the operator cache. Nothing written to a PATH directory, the fleet root, or a sibling lane.

## 6. Defects

None found in the harness or in the frozen contracts. Observations, not defects:

1. `captures` in the receipt is keyed `health`/`metrics`/`models`/`props`/`slots`, while the same entries carry `path: "/health"` etc. A reader grepping for `captures["/health"]` gets `None`; read `captures.health`. It is internally consistent and documented only by the data, so a future reader-facing note could name the key shape (`tools/kama-llamacpp-live.py`, receipt assembly in `ready_captures`).
2. The round-45 receipt JSON files are mode 600; these new ones are too. Fine for local evidence, worth knowing before a reader tries to read them as another account.

## 7. Proposed SOURCES landing (not applied — L1's call)

The existing rows cover v1 (S041), v2 (S046), v3 (S055) and the b11889 receipts (S485). This run is the same instrument at a new build, so the honest landing is one new own-work row at b11906 rather than an edit of a frozen row. Proposed content (full text for L1 to adapt; paths relative to the lane):

> `| S486 | kama live llama.cpp lifecycle receipts at b11906 — python3 tools/kama-llamacpp-live.py (raw receipts .ufo/waves/round-46/c1/live/receipt-1.json, -2.json, -3.json; install identity .ufo/waves/round-46/c1/live/install.txt; model .ufo/waves/round-46/c1/live/model-fetch.txt) | own-work | A | three lane-owned b11906 runs on unregistered loopback ports at sampled instants; not registered-consumer health, model quality, other builds or general timing | receipts kama-llamacpp-live/v3 2026-10-26T19:57:39.317Z–19:57:39.905Z, ports 33179, 46073, 44923; server sha256 c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff from release asset sha256 064ade62…eeef3 (build_info b11906-4d71b42fd); model stories260K.gguf sha256 270cba1b…256d; tool sha256 8c0dbb2b…f662f3; each run 11/11 checks | At b11906 the ready /health body is exactly {"status":"ok"}, every loading 503 is the exact envelope (24–35 per run, one distinct body, sha256 baa09177…bef957c — identical to b11889), /metrics answers 501, /v1/models reports the alias with owned_by llamacpp, the probe grades MODEL_OK and MODEL_MISMATCH, and one SIGTERM to a live child ends in returncode 0 after 3 ms with no SIGKILL and the port closed | mined | 2026-10-26 | every round | corpus/knowledge/llamacpp-loading-lifecycle.md |`

## 8. Exact retained evidence

- `.ufo/waves/round-46/c1/live/install.txt` — asset + release digest + target commit + install path + `llama-server`/impl/tree/links sha256 + `--version` + tool sha256.
- `.ufo/waves/round-46/c1/live/model-fetch.txt` — URL, path, 1185376 bytes, sha256, fetch time.
- `.ufo/waves/round-46/c1/live/receipt-1.json` (sha256 `9ad6ad36…977e26`), `receipt-2.json` (`09f049cf…c262562a`), `receipt-3.json` (`33f1dd57…ae46632`).
- `.ufo/waves/round-46/w1/out/X1Live/summary.json` — machine-readable per-receipt field table.
- `.ufo/waves/round-46/w1/out/X1Live/commands.json` — every command with exit code and observed value.
- `.ufo/waves/round-46/w1/out/X1Live/release-b11906.json`, `download.log`, `model-dl.log`, `run-{1,2,3}.{stdout,stderr}`.
