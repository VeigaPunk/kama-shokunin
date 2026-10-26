# X1Replica — round 46, independent b11906 live replication (no shared install)

**Verdict: PASS — two independent b11906 runs, both `outcome: pass`, 11/11 checks evaluated and passed, exit 0 each; every behavioural proposition in S041, S046 and S055 reproduces on b11906 (4d71b42fd…), and the b11906 server binary is `c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff`. One freshness caveat, not a behavioural contradiction: the harness's `teardown_graceful` code bindings are pinned at b11755 and their span text no longer exists in `tools/server/server.cpp` at b11906.**

Seat rules honoured: lane tree read-only (only `.ufo/waves/round-46/w1/out/X1Replica/` written), no counter/prereg/control touched, no service started or stopped, no git/jj mutation anywhere, scratch `rm -rf`'d after every cited artifact was copied out. No tool installed or upgraded this wave.

## 1. Artifact provenance (own download, own scratch, no shared install)

| step | evidence |
|---|---|
| release record | `curl -fsSL https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11906` → exit 0. `tag_name b11906`, `target_commitish 4d71b42fd87db24b8b7c808c151b713aa4459cfd`, `published_at 2026-10-26T19:45:36Z`, 36 assets. Excerpt: `source/release-record-b11906-excerpt.json` |
| tarball | `llama-b11906-bin-ubuntu-x64.tar.gz`, 22478121 bytes, release-record `digest` **`sha256:064ade6220799fd9e7b1804b574f5f92c38dde358cc987c6b8283cfaeb1eeef3`**; my download's `sha256sum` = `064ade62…eeef3` → **match** (`source/downloads.sha256`) |
| model | downloaded fresh from `https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf`, 1185376 bytes, `sha256sum` = **`270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`** → match |
| server binary | `bin/llama-b11906/llama-server` `sha256sum` = **`c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff`**; `sha256sum bin/llama-b11906/llama-server` (exit 0) and receipt `server.sha256` agree |
| server self-report | `./bin/llama-b11906/llama-server --version` → exit 0, `version: 0.7.0-dev (build 11906, commit 4d71b42fd)` (`source/llama-server-version.txt`); runtime `/props` `build_info` = `b11906-4d71b42fd` in both receipts |
| install identity (from receipts) | `install_tree_sha256 89fbc38997001c02fe7daae0fcc32c6aa9e7c585f455d8809ddefe42ed7bdf0f`, `install_links_sha256 5cb9f4865c8e1315dbd1baa99310c9bc65ddcf469929488359c66587b6470060`, `server_impl_sha256 682717ba312caefda06be7b2e5a637d8af357ff1f1264f6f5624dc53212a8223`, `install_unpinned []`; `ldd` resolves every DT_NEEDED (own tree + system libs) |

Release-point confirmation from the shared read-only bare clone (never fetched into, never written):
`git -C /fast/scratch/hyaku/kama-r46/L1/llama.git rev-parse b11906^{commit}` → `4d71b42fd87db24b8b7c808c151b713aa4459cfd`; `rev-list --count d854d98bae598388ecea1ed84396587e5edc326d..4d71b42fd…` → **17** — the claim's "b11906 = 4d71b42fd, 17 commits after b11889 = d854d98ba" is confirmed.

## 2. Runs (exact argv, both exit 0)

```
TMPDIR=$S python3 <lane>/tools/kama-llamacpp-live.py \
  --server $S/bin/llama-b11906/llama-server --model $S/stories260K.gguf \
  --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d \
  --alias kama-r46-replica --ctx 256 --threads 1 --out <…>/receipt-N.json
```

| | run 1 | run 2 |
|---|---|---|
| exit / outcome | 0 / `pass` | 0 / `pass` |
| schema | `kama-llamacpp-live/v3` | same |
| port | 38645 (not in refusal set `[8080, 34113]`, not in `registry/endpoint-consumers.tsv`) | 45335 (same) |
| started→ended UTC | 19:57:20.586 → 19:57:20.747 | 19:57:24.632 → 19:57:24.790 |
| checks | 11/11 `evaluated:true, passed:true` | 11/11 |
| tool pin | `8c0dbb2b60da4d0e89ebe537b2f36b0b59356efedbe5f66c7364bdb6c8f662f3` | identical |
| probe pin | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` | identical |
| model pin / post-run rehash | `270cba1b…256d` / `270cba1b…256d` | identical |
| `internal_fault` / `setup_error` | `null` / `null` | `null` / `null` |

Check ids (identical order in both runs): `health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch, teardown_graceful, teardown_port_closed, loading_envelope_graded, model_unchanged`. Cross-run comparison: `replica-consistency.json` (`pins_identical_across_runs: true`, `all_checks_passed: true`).

## 3. Agreement with the S041 / S046 / S055 statements (corpus/SOURCES.md:53, :58, :67)

All behavioural propositions hold. Row-local metadata that is historical (schema version, tool digest, check count, ports, timestamps) is listed apart and is not a contradiction — those cells describe the original b11755 runs, and the lane has never claimed the tool is frozen at those digests.

### S041 (SOURCES.md:53 — live lifecycle receipt, b11755, v1/10 checks)
| statement | observed on b11906 | evidence |
|---|---|---|
| `/v1/models` answers 503 with the exact loading envelope while loading | 28 consecutive 503s per run, body `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`, sha256 `baa09177700f64520a799fd2628bb3663c1486b25e17e4a507f2e6c81bef957c` — byte-identical to S036's text (SOURCES.md:48) | `receipt-1.json` `.loading_503`, `.transitions[1]`, `.loading_envelope_exact:true` |
| then `/health` 200 | status 200 | `.captures.health.status` |
| `/v1/models` id = alias with `owned_by` `llamacpp` | `data[0].id = "kama-r46-replica"`, `data[0].owned_by = "llamacpp"` | `.captures.models.body`; checks `models_alias_id`, `models_owned_by_llamacpp` |
| `/metrics` 501 | status 501 | `.captures.metrics.status`; check `metrics_not_enabled` |
| probe grades MODEL_OK and MODEL_MISMATCH correctly | `expect kama-r46-replica` → exit 0, `reason=matched`; `expect kama-not-this-model` → exit 2, `reason=served-id-mismatch`, `drift=true` | `.probes[0]/.probes[1]`; checks `probe_model_ok`, `probe_mismatch` |
| — historical, not replicated | v1 receipt, 10 checks, tool sha `b8c5e8d4…`, port 37527. My run is v3, 11 checks, tool `8c0dbb2b…` (same digest the lane pinned for its b11889 runs, S485) | |

### S046 (SOURCES.md:58 — v2 receipt, b11755)
| statement | observed on b11906 |
|---|---|
| ready `/health` body is exactly `{"status":"ok"}` | both runs: body `{"status":"ok"}`, `Content-Length: 15`, sha256 `a29ee2b15c494311c52521766e44af56a3ad2248e7a8ab465e5206463c13d288` — identical to the lane's b11889 receipt body/sha |
| every loading 503 is the exact envelope | 1 distinct 503 body per run, `loading_envelope_exact:true`, `loading_bodies_dropped:0`, check `loading_envelope_graded` passed |
| one harness SIGTERM to a live child: returncode 0 after 3 ms, no SIGKILL, child-owned port refused | both runs `{"alive_at_teardown_start":true,"sigterm_sent":true,"sigkill_sent":false,"returncode":0,"term_wait_ms":3,"port_refuses":true}`, `port_listener_ownership:"child"` |
| — sampling-dependent detail | S046's "(42, 45, 45)" 503 counts are the round-17 cadence; with this 292 800-parameter model the server is ready in ~4.6 ms of wall clock from spawn, so only 28 polls land inside the window (`.teardown.log_lines` shows `model loaded` at 0.00.008.828). Invariant holds, counts are not a constant. |

### S055 (SOURCES.md:67 — v3 receipts, b11755, gate VALID, four byte pins)
| statement | observed |
|---|---|
| all runs evaluated and passed 11 checks | 11/11 in both runs, exit 0, `outcome:"pass"` — check ids identical to the b11889 receipt |
| observed loading 503s | yes, both runs |
| schema floor v3 | `kama-llamacpp-live/v3` |
| four byte pins | server, model, probe and tool sha256 all recorded; model/probe/tool pins identical across the two runs |
| teardown child-owned and graceful | `port_listener_ownership:"child"`, teardown as above |
| — not evaluable from this seat | the round-18 *gate* verdict (`VALID`) lives in `.ufo/waves/round-18/runs/run.py`; I confirm the receipt facts the gate consumes, not the gate's own run. S055 also describes three runs; this item specified two. |
| — historical | S055's tool sha `dc036d7d…`; today's tool is `8c0dbb2b…` |

## 4. Freshness datum: b11889 → b11906 surface is unchanged

Compared my b11906 `receipt-1.json` against the lane's b11889 receipt `.ufo/waves/round-45/c1/live/receipt-1.json` (`source/b11889-vs-b11906-surface.json`):

- **equal**: `/health` status + body + body sha256 + `Content-Length`, `/metrics` 501, loading-503 body + sha256 + `loading_envelope_exact`, `/v1/models` top-level keys, `data[0]` keys, **`data[0].meta` exactly equal**, `models[0].capabilities == ["completion"]`, `models[0].details`, `/props` field-key set, `total_slots 4`, all 11 check ids and pass states, `port_listener_ownership`, schema, probe/tool/model pins.
- **differs**: `build_info` (b11889-d854d98ba → b11906-4d71b42fd), server binary sha (build-specific; S485's `248e790d…` is the b11889 build), alias-derived `data[0].id/aliases` and `created`, and `term_wait_ms` (15 → 3).
- Source side (`git diff --stat` on the shared clone): only `tools/server/server-context.cpp` (+10/−7, `mtmd_helper_cap` capability refactor) and `tools/server/server-models.cpp` (1 line) move between b11889 and b11906; `server.cpp` and `server-http.cpp` are byte-identical. The `mtmd_cap` refactor did **not** change the single-model `/v1/models` document for this text-only model — a b11906 runtime datum the `server-models.cpp` rows can use.

## 5. Risk (freshness of the harness's citations at the run build) — not fixed here

Exact locus: `tools/kama-llamacpp-live.py:1049`, `:1058`, `:1066` build the three `teardown_graceful` bindings from `tools/server/server.cpp` at `LLAMA_COMMIT = 704366d76…` (b11755, `:56`); the receipts embed them as `source_binding[2..4]`.

Command that shows it (read-only, on the shared clone):

```
git -C /fast/scratch/hyaku/kama-r46/L1/llama.git show \
  4d71b42fd87db24b8b7c808c151b713aa4459cfd:tools/server/server.cpp | grep -n \
  "signal_handler\|shutdown_handler\|sigaction\|start_loop\|return 0;"
```

At b11906 the signal path is `server_install_signal_handlers()` at `server.cpp:318-326`, `shutdown_handler` at `:525`, `start_loop()` at `:671`, `return 0;` at `:684`. Re-deriving each embedded span (`source/binding-freshness.json`): pin text present at the pin commit and pin `file_sha256` re-derived OK for all five bindings; **at b11906 `health_ready` (server-context.cpp L5288-5299) and `loading_envelope_graded` (server-http.cpp L314-325) spans are still present, and all three `teardown_graceful` spans are absent.**

So a b11906 live receipt grades the SIGTERM/exit-0 behaviour from observed runtime (which passed) but cites code that no longer exists at the build it ran — the `documented_by` strings are accurate *for b11755*, and the receipt never claims otherwise, so this is a citation-freshness gap, not a false check. Consequence for this wave: a b11906 row built from this receipt must not inherit a "shutdown code path" claim without either (a) citing the b11906 anchors above, or (b) carrying a note that the binding commit is b11755 while `build_info` is b11906-4d71b42fd. Proposed fix for the owning tool (out of scope for a frozen-counter wave, so **not** applied): make `source_bindings()` take the run's build commit and assert each span is present at that commit, or record a per-binding `"binding_commit"` plus a `"span_present_at_build"` boolean in the receipt so a later recheck can fail loudly.

No other defect found: the two receipts are internally consistent (all four byte pins identical across runs, no internal fault, no setup error, teardown proven).

## 6. Artifacts written (all under the lane's w1 out)

- `X1Replica.md` — this report
- `X1Replica/receipt-1.json` (`sha256 92f790f2d25c6383170063adc6668598c52fbb271e188abda80fd840940f68a2`), `X1Replica/receipt-2.json` (`sha256 cc0365dd427933dacc923fd6ddcf10ad1a4b045345694e7430a3e9a4a1b14510`, `cmp`-distinct from run 1) — raw `kama-llamacpp-live/v3` receipts (ports 38645, 45335). Their `argv`, `server.arg`, `model.arg` and `teardown.log_path` name scratch paths deleted per the operator scratch directive; the digests inside them identify the artifacts.
- `X1Replica/run-1.stdout.json`, `run-1.stderr.txt`, `run-2.stdout.json`, `run-2.stderr.txt` — empty (0 bytes) because `--out` carries the JSON; kept only to show no stray stdout/stderr.
- `X1Replica/replica-consistency.json` — cross-run pins, check table, teardown, probe evidence
- `X1Replica/source/downloads.sha256` — tarball/model/server sha256
- `X1Replica/source/release-record-b11906-excerpt.json` — tag, target commit, published_at, asset digest
- `X1Replica/source/llama-server-version.txt` — `--version` output
- `X1Replica/source/binding-freshness.json` — pin vs b11906 presence per source binding
- `X1Replica/source/b11889-vs-b11906-surface.json` — cross-release surface equality
- `X1Replica/source/commands.txt` — every command with exit code

Absolute paths:
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Replica.md`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Replica/receipt-1.json`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Replica/receipt-2.json`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Replica/replica-consistency.json`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Replica/source/downloads.sha256`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Replica/source/release-record-b11906-excerpt.json`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Replica/source/llama-server-version.txt`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Replica/source/binding-freshness.json`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Replica/source/b11889-vs-b11906-surface.json`
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/X1Replica/source/commands.txt`
