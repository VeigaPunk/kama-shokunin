# ExecEmbeddingsInput — advice report (round 26 wave 1, C1 data seat)

Verdict: 5 faults confirmed live with verbatim pinned-source signatures; frozen counter in a scratch extract prints `registered 5 counted 5 target 12 met False not-counted []`; no blockers.

## Fault family covered

Embeddings enabled (`--embeddings`) with malformed `/v1/embeddings` requests on the lane-owned fixture (llama-server b11755, commit 704366d, sha256 b6a31a8e…cd804; stories260K.gguf sha256 270cba1b…256d). All 5 entries are HTTP-channel (status 400), model "fixture", `occupy_port` false.

## Candidate rows (all counted by the frozen counter)

| id | signature (verbatim) | source file:line | trigger | bytes |
|---|---|---|---|---|
| KAMA-R26-E001 | Pooling type 'none' is not OAI compatible. Please use a different pooling type | server-context.cpp:6137 | args `["--embeddings"]`; POST /v1/embeddings `{"input":"hello world"}` | 78 |
| KAMA-R26-E002 | `\"input\" or \"content\" must be provided` (backslash-quote form) | server-context.cpp:6151 | args `["--embeddings","--pooling","mean"]`; POST /v1/embeddings `{"model":"stories260K"}` | 37 |
| KAMA-R26-E003 | `\"input\" must not be empty` (backslash-quote form) | server-context.cpp:6183 | args `["--embeddings","--pooling","mean"]`; POST /v1/embeddings `{"input":[]}` | 25 |
| KAMA-R26-E004 | The format to return the embeddings in. Can be either float or base64 | server-context.cpp:6161 | args `["--embeddings","--pooling","mean"]`; POST /v1/embeddings `{"input":"hello","encoding_format":"binary"}` | 69 |
| KAMA-R26-E005 | Input content cannot be empty | server-context.cpp:6190 | args `["--embeddings","--pooling","mean"]`; POST /v1/embeddings `{"input":[[]]}` | 29 |

Source: `tools/server/server-context.cpp` at commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad:
`https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6137` (and #L6151, #L6161, #L6183, #L6190), accessed 2026-10-23. Pinned sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`; the lane snapshot `sources/llama.cpp-704366d/server-context.cpp` is byte-identical (same sha256). Quote (line 6137, ≤25 words): `"Pooling type 'none' is not OAI compatible. Please use a different pooling type"`.

## Live reproduction evidence (twice per fault, one child at a time)

Pooled route (args `--embeddings --pooling mean`): probe2 (port 47621), probe3 (port 47622), probe4 (port 47620). In every launch `/v1/embeddings` returned status 400 with the bodies in `probe{2,3,4}_*_req_emb_*.body`; responses are byte-identical across launches. Healthy control `{"input":"hello world"}` returned 200; `{"input":""}` returned 200 (empty string tokenizes to BOS only — not a fault).

Default-NONE route (args `--embeddings`): probe3 (port 47623) and probe4 (port 47621). Every `/v1/embeddings` request returns 400 `Pooling type 'none' is not OAI compatible. Please use a different pooling type` (see `probe3_defaultnone_req_emb_missing_input.body`, `probe4_defaultnone_req_emb_missing_input.body`). The fixture model resolves pooling to NONE (llama-context.cpp:302-308: UNSPECIFIED → hparams UNSPECIFIED → NONE), so no `--pooling none` argument is needed; the counter's args stay minimal.

Probe 1 (port 47620, `--embeddings` only) hit a real segfault: the server died (SIGSEGV, coredumpctl pid 3310053, 2026-10-23 00:36:17 -03) while serving a `/completion` request — server log ends `timeout: the monitored command dumped core`. This crash path is NOT a candidate: it yields no HTTP status, and the counter requires status ≥ 400 from a live server. It is recorded for completeness in RUNS.txt.

## Frozen counter (scratch extract of frozen tip a23c0e042114016a909eb15173aa6df74b5b7eb0)

Extract: `git -C <lane> archive a23c0e042114016a909eb15173aa6df74b5b7eb0 | tar -x` into `/fast/scratch/hyaku/kama-r26/ExecEmbeddingsInput/scratch-archive/` (GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE unset). Registry `registry/error-signatures-r26.json` = candidates.json (id → KAMA-R26-E001..E005, source.row → S901..S905). Scratch-only placeholders: SKILL.md `## Round-26 live error signatures` table and corpus/SOURCES.md rows S901-S905 (source row names server-context.cpp + commit 704366d).

Run under the host-wide lock:
```
$ flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py \
    --out /fast/scratch/hyaku/kama-r26/ExecEmbeddingsInput/counter-receipt.json
registered 5 counted 5 target 12 met False not-counted []
counter_exit=0
```
Receipt (`counter-receipt.json`): all 5 rows `counted: true`; every check true (`a_skill_row`, `b_new_at_base`, `c_source_row`, `d_source_pinned`, `d_in_source`, `e_error_shown`, `e_signature_seen`, `e_not_echoed`, `f_absent_from_baseline`, `g_distinct`); observed status 400 for each; `baseline_sha256 bcd899fe74ac4d55d6116ca72d604c43a53c0b8ff56b5e94aa28ab09f89dd991`. Base absence verified separately: `git grep -F -q -e <sig> 1560e4d8 -- SKILL.md corpus` → exit 1 for all five.

### Important byte-exactness note (E002/E003)

The counter requires the signature bytes to occur verbatim in the pinned source file. The C++ source and the live JSON error body both carry escaped quotes (`\"input\" or \"content\" must be provided`), so the registry signature must be that exact backslash-quote form — not the human-readable unescaped message. A first counter run with the unescaped form failed exactly on `d_in_source` for these two rows; re-registering the byte-exact form passed. Keep this form when the L1 opens real S9xx rows.

## Files written by this seat

- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsInput/candidates.json` — registry per counter schema (5 entries, id/row placeholders resolved to KAMA-R26-E001..E005 / S901..S905 for the scratch run).
- `.ufo/waves/round-26/w1-build/out/ExecEmbeddingsInput/RUNS.txt` — every command, output, exit code, teardown check.
- `.ufo/waves/round-26/w1-build/advice/ExecEmbeddingsInput.md` — this report.
- Scratch evidence under `/fast/scratch/hyaku/kama-r26/ExecEmbeddingsInput/`: probe scripts, server logs (`server_probe{1,2,3,4}_*.log`), response bodies (`probe*_*.body`), request files (`req_emb_*.json`), counter receipt, scratch archive.

No tools were installed this seat. Ports 47620-47623 verified free before launch and closed after teardown; no llama-server from this seat remains (`pgrep -af llama-server` shows only other seats' children on 47605/47624/47572, none in my block). No primary keyboard files were modified (scratch and w1-build/out only).

Risks/notes for the L1: (1) the `.completion` segfault under `--embeddings`-only is a reproducible b11755 defect (core dumped) — keep it out of counted rows because it has no HTTP status; (2) keep the E002/E003 backslash-quote byte form in the landed registry and SKILL.md rows; (3) all five entries satisfy clause (g) distinctness (none a substring/superstring of another, no trigger repeats).
