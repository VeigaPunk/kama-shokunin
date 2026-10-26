# Round 47 / X2Receipts — three b11909 live receipts audited against the b11906 baseline

**Verdict: all three receipts are internally consistent, independently re-derivable from upstream, and 11/11 checks evaluated and passed; b11906 → b11909 changes binaries only (7 of 51 files), with no observed HTTP surface change.**

Baseline for comparison: round-46 `kama-llamacpp-live/v3` receipts at `.ufo/waves/round-46/c1/live/receipt-1..3.json`
(llama.cpp b11906 = `4d71b42fd87db24b8b7c808c151b713aa4459cfd`).
Under audit: `.ufo/waves/round-47/c2/live/receipt-1..3.json` (`kama-llamacpp-live/v4`, b11909 = `caa8191df159f764fb0160e3d2fc6be008948aee`).

Scratch: `/fast/scratch/hyaku/kama-r47/X2Receipts` (removed after the run; all evidence below is reproduced by the commands shown).

---

## 1. Receipt integrity (schema, outcome, checks, build_info, provenance)

| field | receipt-1 | receipt-2 | receipt-3 | expected |
|---|---|---|---|---|
| `schema` | `kama-llamacpp-live/v4` | same | same | v4 per `SCHEMA = 'kama-llamacpp-live/v4'` (`tools/kama-llamacpp-live.py:54`) |
| `outcome` | `pass` | `pass` | `pass` | pass |
| `checks` | 11, `evaluated=true` 11/11, `passed=true` 11/11 | same | same | 11 |
| `setup_error` / `internal_fault` | `null` / `null` | same | same | null |
| `captures.props.fields.build_info` | `b11909-caa8191df` | same | same | b11909 / caa8191df |
| `provenance.server.asset_url` | `…/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz` | same | same | frozen |
| `provenance.server.asset_sha256` | `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b` | same | same | frozen |
| `provenance.server.member` | `llama-b11909/llama-server` | same | same | frozen |
| `provenance.model.url` / `.sha256` | HF `stories260K.gguf` / `270cba1b…bd256d` | same | same | frozen |
| `server.sha256` | `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` | same | same | archive member digest |
| `server.server_impl_sha256` | `b8f0f203f3c593225710bc2075b404944037b172c021e0136791dbff6f9043c2` | same | same | archive member digest |
| `server.install_tree` / `install_tree_sha256` | 51 files / `9f1198f4e2d64495ea6e6c6dece9f95a34ab2e4e2a11f72fd7debd1024d5542e` | same | same | 51 / canonical digest |
| `server.install_links` / `install_links_sha256` | 10 links / `5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060` | same | same | 10 / canonical digest |
| `server.install_unpinned` | `[]` | `[]` | `[]` | empty |
| `model.sha256` = `model_sha256_post` | `270cba1b…bd256d` | same | same | 270cba1b…bd256d |
| `tool.sha256` | `65301a3c76f925bf3316673d3774269f6d93ca22f4ccdb7c7139e6826b8ae65d` | same | same | `tools/kama-llamacpp-live.py` at lane commit `3a09a1d9` |
| `probe.sha256` | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` | same | same | `tools/kama-probe.sh` at HEAD |
| `port` / `child_pid` | 37903 / 3871869 | 44883 / 3872567 | 39739 / 3873367 | distinct runs |
| `started_utc` → `ended_utc` | 21:16:50.545Z → 21:16:50.722Z | .774Z → .943Z | 21:16:51.030Z → 21:16:51.224Z | three sequential ~0.2 s runs |

`tool.sha256` checked against the build commit, not the working tree:

```
$ git -C kama-shokunin cat-file -p 3a09a1d93dcc16799cf6c4b48786e6440af134c4:tools/kama-llamacpp-live.py | sha256sum
65301a3c76f925bf3316673d3774269f6d93ca22f4ccdb7c7139e6826b8ae65d  -
```

### 1.1 The 11 checks (all three receipts; observed values identical across the three except the loading count)

| # | id | evaluated | passed | observed |
|---|---|---|---|---|
| 0 | `health_ready` | true | true | 200, body `{"status":"ok"}` |
| 1 | `models_alias_id` | true | true | 200, `data_ids=["kama-r47-live"]` |
| 2 | `models_owned_by_llamacpp` | true | true | 200, `owned_by=["llamacpp"]` |
| 3 | `metrics_not_enabled` | true | true | 501 |
| 4 | `props_alias` | true | true | `build_info=b11909-caa8191df`, `model_alias=kama-r47-live`, `n_ctx=256`, `total_slots=4`, `is_sleeping=false` |
| 5 | `probe_model_ok` | true | true | probe exit 0, `MODEL_OK/matched` |
| 6 | `probe_mismatch` | true | true | probe exit 2, `MODEL_MISMATCH/served-id-mismatch` |
| 7 | `teardown_graceful` | true | true | SIGTERM sent, returncode 0, alive at start, ownership `child` |
| 8 | `teardown_port_closed` | true | true | ownership `child`, port refuses |
| 9 | `loading_envelope_graded` | true | true | `loading_observed=true`, `exact=true`, `all_exact=true`, distinct bodies 1, dropped 0; totals 18 / 34 / 29 |
| 10 | `model_unchanged` | true | true | pre == post == `270cba1b…` |

`captures.props.fields` equals `checks[4].observed.fields` in all three receipts (no re-serialisation drift).

## 2. Independent re-derivation of the pinned digests

Commands (scratch dir, exit codes shown):

```
$ curl -fsSL -o llama-b11909.tar.gz https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz   # exit 0
$ sha256sum llama-b11909.tar.gz
bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b  llama-b11909.tar.gz      (22,475,032 bytes)
$ sha256sum llama-b11909/llama-server
35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
$ curl -fsSL -o stories260K.gguf https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf   # exit 0
$ sha256sum stories260K.gguf
270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d                       (1,185,376 bytes)
```

* Archive asset digest == `provenance.server.asset_sha256` == `.ufo/waves/round-47/c2/live/install.txt:1` ==
  `.ufo/waves/round-47/c2/release-b11909.json` asset `llama-b11909-bin-ubuntu-x64.tar.gz` `sha256:bf94332a…`.
* Archive members: 62 total = 1 directory + **51 regular files + 10 symlinks**, which is exactly the
  `install_tree` (51) and `install_links` (10) cardinality in the receipts.
* Re-hashed **every** regular member: 51/51 equal to `server.install_tree` (0 mismatches); 10/10 symlink
  targets equal to `server.install_links`; the canonical tree digest recomputes to
  `9f1198f4…` and the link digest to `5cb9f486…`, matching `install_tree_sha256`/`install_links_sha256`
  in all three receipts.
* `provenance.server.member` (`llama-b11909/llama-server`) hashes to `server.sha256`; `libllama-server-impl.so`
  hashes to `server.server_impl_sha256` (`b8f0f203…`).
* The **live installed tree** `/home/vgpnk/.local/opt/llama-b11909` was hashed read-only: 51 files + 10 links
  hash-identical to the receipts (tree digest `9f1198f4…` equal) — the receipts describe the served install,
  not only the archive.
* Binary self-report from the extracted member (no server start, no listener):
  `./llama-b11909/llama-server --version` → `version: 0.7.0-dev (build 11909, commit caa8191df)`,
  `built with GNU 11.4.0 for Linux x86_64` — equal to `build_info=b11909-caa8191df` and to
  `install.txt:5-6`.
* `source_binding` (5 entries) re-verified against the named commit `704366d7…`: for every entry the
  `file_sha256` equals the file fetched at that commit and `span_text` equals the exact lines
  (`server-context.cpp` 5288-5299, `server-http.cpp` 314-325, `server.cpp` 519-523 / 529-534 / 575-590);
  `span_sha256` recomputes. The binding block is byte-identical to the round-46 receipts.

## 3. Teardown fields

| field | r47-1 | r47-2 | r47-3 | r46-1..3 |
|---|---|---|---|---|
| `alive_at_teardown_start` | true | true | true | true |
| `sigterm_sent` / `sigkill_sent` | true / false | true / false | true / false | true / false |
| `returncode` | 0 | 0 | 0 | 0 |
| `term_wait_ms` | 3 | 3 | 3 | 3 |
| `port_refuses` | true | true | true | true |
| `log_path` | **null** | **null** | **null** | `/fast/scratch/hyaku/kama-r46/X1Live/kama-llamacpp-live-*.log` (all three paths now absent — `ls` exit 1) |
| `log_lines` | 3 (load → model loaded → listening on the receipt's own port) | same, own port | same, own port | 3, own port |

`log_lines[-1]` port equals the receipt `port` in all six receipts (37903/44883/39739; 33179/46073/44923),
so the log tail belongs to the run it is attached to. `log_path: null` is the v4 contract
(`tools/kama-llamacpp-live.py:32-34`): the temp log is always deleted, so a path would be dead evidence —
the round-46 values were exactly that (three dangling `/fast/scratch` paths, verified absent).

Other teardown-adjacent fields: `port_listener_ownership="child"` (proof before teardown),
`port_refusal_set=[8080,34113]`, `port_pick_note` present, `child_env_keys=["HOME","LANG","PATH","TMPDIR"]`
(values never recorded), `pdeathsig={"requested": true, "prctl_ok": "unknown"}` (see F4).

## 4. Check by check: b11906 (round 46) vs b11909 (round 47)

All 11 ids and their `documented_by` strings are identical between the two rounds; `evaluated`/`passed`
are true/true for every check in all six receipts. Only three `observed` blocks differ:

| id | b11906 observed | b11909 observed | nature |
|---|---|---|---|
| `health_ready` | 200 `{"status":"ok"}` | identical | unchanged |
| `models_alias_id` | `["kama-r46-live"]` | `["kama-r47-live"]` | alias by design |
| `models_owned_by_llamacpp` | `["llamacpp"]` | identical | unchanged |
| `metrics_not_enabled` | 501 | 501 | unchanged |
| `props_alias` | `build_info=b11906-4d71b42fd`, alias r46 | `build_info=b11909-caa8191df`, alias r47 | build + alias by design |
| `probe_model_ok` / `probe_mismatch` | exit 0 / exit 2 | identical | unchanged |
| `teardown_graceful` / `teardown_port_closed` | rc 0, child, refuses | identical | unchanged |
| `loading_envelope_graded` | exact, distinct 1, dropped 0, totals 35/24/27 | identical envelope, totals 18/34/29 | body identical; count is rack timing |
| `model_unchanged` | 270cba1b… | 270cba1b… | unchanged |

## 5. Capture by capture

| capture | b11906 (r46) | b11909 (r47) | difference |
|---|---|---|---|
| `/health` | 200, CL 15, body `{"status":"ok"}`, sha `a29ee2b1…` | 200, CL 15, same body, same sha `a29ee2b1…` | **none** |
| `/v1/models` | 200, CL 670, sha `5b63fc47…` (one sha for all 3 runs) | 200, CL 670, sha `d218fe5c…` ×2 and `e9fb75d4…` ×1 | JSON parses to the same tree; only `data[0].created` (epoch seconds) and the alias differ |
| `/props` | 200, CL 2067, shas `fe6aa72e…`/`031b7426…`/`33c7615f…`; fields `build_info=b11906-4d71b42fd, model_alias=kama-r46-live, n_ctx=256, total_slots=4, is_sleeping=false` | 200, CL 2067, shas `fb5e3e82…`/`4afdf3c5…`/`9089951c…`; same fields with b11909/r47 values | recorded fields: build_info + alias only (see F1 for the unrecorded per-run variance) |
| `/slots` | 200, CL 253, sha `6d345b40…`, `element_count=4` | identical sha `6d345b40…`, `element_count=4` | **none** |
| `/metrics` | 501, no body captured | 501, no body captured | **none** |
| loading 503 envelope | body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`, sha `baa09177…`, exact=true, dropped 0, distinct 1 | identical body and sha, exact=true, dropped 0, distinct 1 | **none** |
| transitions | 4 (refused → 503 → 503 → health 200) | 4, same phases | timings only |

Normalised `/v1/models` diff (parse JSON, then compare leaf paths) is exactly:

```
.data[0].id            kama-r46-live -> kama-r47-live
.data[0].aliases[0]    kama-r46-live -> kama-r47-live
.data[0].created       1793044659    -> 1793049410
.models[0].name        kama-r46-live -> kama-r47-live
.models[0].model       kama-r46-live -> kama-r47-live
```
No key was added and none removed (`meta`, `architecture`, `capabilities`, `details`, `owned_by`,
`object`, `tags`, `type` all present and equal in both), and `Content-Length` is 670 in both rounds.

## 6. What actually differs between b11906 and b11909

Install trees are key-identical (51 files, same names) and link-identical (same 10 soname links, so the
ABI sonames `libllama.so.0`, `libllama-common.so.0`, `libggml.so.0`, `libggml-base.so.0`, `libmtmd.so.0`
did not move). 44 of 51 files are byte-identical; **7 changed**:

| file | size b11906 → b11909 | sha256 prefix |
|---|---|---|
| `libggml-base.so.0.27.0` | 906,112 → 906,112 | `072e58f7…` → `16527517…` |
| `libllama-common.so.0.7.0` | 6,699,720 → 6,699,720 | `4d05e08d…` → `29feaa27…` |
| `libllama-server-impl.so` | 7,923,736 → 7,923,736 | `682717ba…` → `b8f0f203…` |
| `libllama.so.0.7.0` | 5,275,320 → **5,275,808** | `63f3d1b3…` → `9705244b…` |
| `llama-bench` | 17,864 → 17,864 | `b8b7c466…` → `3d6f9267…` |
| `llama-quantize` | 17,864 → 17,864 | `00674f44…` → `803913ed…` |
| `llama-server` (launcher) | 17,864 → 17,864 | `c949950e…` → `35ac50fb…` |

Cross-checked against the b11906 archive itself (downloaded, sha256 `064ade62…` = round-46
`install.txt:1`; member `llama-server` `c949950e…` = round-46 `server.sha256`; `libllama-server-impl.so`
`682717ba…` = round-46 `install.txt`): the round-46 `install_tree`/`install_links` equal that archive
member for member, so the "7 changed files" is upstream, not local drift.

Source level: `tools/server/{server-context.cpp, server-http.cpp, server.cpp, README.md}` are
**byte-identical** between `4d71b42fd` (b11906) and `caa8191df` (b11909) — same size and `cmp` equal.
The 7 binary changes therefore come from the rest of the tree plus the embedded build string (the
17864-byte launchers changed hash at constant size, and `build_info` is compiled in), which matches the
observation that no HTTP surface changed. [INFERENCE for the launcher cause: the launcher's only
difference visible in evidence is the embedded `b11909-caa8191df` build string.]

Timeline (one `gh api releases` request): b11909 published `2026-10-26T21:00:58Z`; the receipts ran
`21:16:50Z`–`21:16:51Z`; b11910 published `21:20:07Z` (commit `63b4b303…`). So b11909 **was** the newest
build when measured and was superseded 3.2 minutes after the run; the receipts remain replayable because
they pin the asset and model by digest, not by "latest".

## 7. Findings

None of these invalidates a check; every check is evaluated and passed in all three receipts.

**F1 — `/props` body is not captured, and its recorded digest is per-run variable (limitation, localizable
only by changing the harness).** `tools/kama-llamacpp-live.py:771` calls
`_capture(port, '/props', keep_body=False)`, so the receipt keeps `body_sha256` plus 5 selected fields.
In round 47 the three `/props` body digests are all different (`fb5e3e82…`, `4afdf3c5…`, `9089951c…`);
in round 46 likewise (`fe6aa72e…`, `031b7426…`, `33c7615f…`). `Content-Length` is 2067 in all six and the
five recorded fields are identical within a round, so an unrecorded field varies per process and the
receipt cannot localise it. Proposed fix (not applied): `keep_body=True` for `/props` — 2,067 B is far
below `CAPTURE_BODY_CAP = 65536` (`tools/kama-llamacpp-live.py:81`) — or record every key of the parsed
props document. Evidence:
`jq -r '.captures.props.body_sha256' .ufo/waves/round-47/c2/live/receipt-*.json`.

**F2 — `/v1/models` body digest is unstable across runs because of `data[0].created`.** r47-3 reports
`created=1793049411`, r47-1/2 report `1793049410`; that single leaf flips the body sha
(`d218fe5c…` ×2 vs `e9fb75d4…` ×1) at constant `Content-Length` 670. Any future tooling that compares
captured body digests across runs or rounds will report false drift. Proposed fix: record `created`
next to the sha (or normalise it), so a body-sha comparison means "surface unchanged".
Cross-round body-sha inequality (`5b63fc47…` → `d218fe5c…`) is **not** evidence of a surface change — the
parsed diff is alias + `created` only (§5).

**F3 — `documented_by` / `source_binding` are pinned to b11755 (`704366d7…`) while the measurement is
b11909 (`caa8191df…`), four releases later; the line references have moved.** Verified drift at
`caa8191df`: `get_health` is at `server-context.cpp:5609-5620` (cited 5288-5299, **+321**);
the 503 loading block is `server-http.cpp:313-327` (`res.status = 503` at 315; cited 314-325);
`server.cpp` moved the signal installation into `server_install_signal_handlers()` at
`server.cpp:318-330` (cited 529-534), the `shutdown_handler` that calls `ctx_server.terminate()` to
`server.cpp:645-649` (cited 519-523), and `start_loop` / `return 0` to `server.cpp:671` / `684`
(cited 575-590). The predicates themselves still hold at b11909 — I read the spans — so the receipts'
sourcing is correct, only dated. Proposed fix: re-anchor `LLAMA_COMMIT`/`_LLAMA_RAW`
(`tools/kama-llamacpp-live.py:61-63`) to the measured release commit, or record
`provenance.cited_commit` and `provenance.measured_commit` separately so a reader knows the doc anchor is
not the binary under test.

**F4 — `pdeathsig.prctl_ok` is `"unknown"` in all six receipts** (`tools/kama-llamacpp-live.py:461-468`
returns `unknown` honestly). The parent-death guarantee is therefore requested but unverified, and no
check grades it; teardown is proven instead by `port_listener_ownership == "child"` +
`port_refuses` + `returncode 0`.

**F5 — round-46 (v3) receipts carry dangling `teardown.log_path` values** under
`/fast/scratch/hyaku/kama-r46/X1Live/` (all three absent now, `ls` exit 1). The v4 behaviour
(`log_path: null`) is the correct fix and is consistently applied in all three round-47 receipts; no
action needed on round 47.

## 8. Reproduction

```
S=/fast/scratch/hyaku/kama-r47/X2Receipts; mkdir -p "$S"; export TMPDIR="$S"; cd "$S"
curl -fsSL -o llama-b11909.tar.gz https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz
sha256sum llama-b11909.tar.gz          # bf94332a…695b
tar xzf llama-b11909.tar.gz && sha256sum llama-b11909/llama-server   # 35ac50fb…7ff0
./llama-b11909/llama-server --version   # 0.7.0-dev (build 11909, commit caa8191df)
curl -fsSL -o stories260K.gguf https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf
sha256sum stories260K.gguf              # 270cba1b…256d
# per-file comparison of install_tree/install_links and the props/models capture diffs: inline python in the report
```
