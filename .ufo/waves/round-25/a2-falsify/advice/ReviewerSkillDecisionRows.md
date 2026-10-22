Verdict: defect found (1 high, 5 medium, the rest low), at the pinned commit fa3b62ae6475d111eb466d79af616aeebb08bbb9.

# ReviewerSkillDecisionRows: round-25 SKILL decision rows (wave 2, falsify)

Target: SKILL.md lines 676-689 at the pin: heading 676, scope paragraph 678-682, table header 684, separator 685, rows 686-689. Each row was checked against the committed entry `corpus/knowledge/context-capacity.md` and the committed receipt `.ufo/waves/round-25/final/context-capacity-receipt.json`, and against the raw bodies and logs in `.ufo/waves/round-25/final/raw/`.

No llama-server was started and no port was used. Git was used read-only (rev-parse, show, merge-base, log, diff --stat). No tool was installed or upgraded; python3 and git were already present.

## Summary by severity

High
- Row 1, line 686, First check: it names `/v1/models` `meta.n_ctx_train`. That field is the training context, which is 2048 in all 14 cells. The served per-slot value is `meta.n_ctx`. In cell K2 the raw body reads `"n_ctx":1024,"n_ctx_train":2048`. Following the row would report 2048 for a served value of 1024.

Medium
- Row 2, line 687, Action: "Do not use the round-20 value for this case" covers `--fit off` (cell X3). Under `--fit off` the round-20 value is correct: predicted 512, observed 512.
- Row 3, line 688, Verdict: the first clause says concurrent requests are bounded by the pool total in general. The only overflow test used a unified cache (cell L1). A split cache is held to per-stream limits by the entry's own mechanism.
- Row 3, line 688, Action: it gives a sizing rule that was never tested, and an escalation with no owner.
- Row 4, line 689, Action: it treats launch flags as evidence of the pool. Flags alone do not give the pool value, and the entry's fixture scope does not carry them to other hosts or models.
- Committed entry, line 2 (`verified-at`): it gives the cell observation window as 09:36:51Z to 09:36:59Z. The committed receipt's cells ran 09:42:42Z to 09:42:50Z.

Low
- Row 2, First check: the X1 log has three `llama_context: n_ctx` lines (283 = 2048, the fit probe; 812 and 1344 = 8192). The row should say "last line".
- Row 3, First check: it reads "how large is the pool" from the startup log. At default verbosity the log does not show the pool.
- Row 4, First check: `-lv 4` appears in no receipt cell; all 14 cells used `-v`.
- Row 4, Verdict: it cites S112 (the README) for an absence claim about endpoint output.
- Scope paragraph: "fit never lowers a context on this fixture" rests on one observed run on this host. It should say so, and say CPU only.
- Receipt: no structured `meta.n_ctx` field; only `models_n_ctx_train` is recorded.
- Table style: the Verdict cells are full sentences; the older table in the same file uses short labels such as `DEAD` and `MODEL_MISMATCH`.

## Format check (table at lines 684-689)

- Header line 684 and separator line 685 are identical to the header and separator of the older decision table at lines 127-128 (`| Symptom | First check | Verdict | Action |`). Row lines 686-689 each have five unescaped pipes, which is four cells. Command: `python3 -B row-check.py`, section 1, exit 0.
- Structure matches. Content style differs (Low). The older table's Verdict column is mostly short labels (`DEAD`, `FOREIGN_SERVICE`, `MODEL_MISMATCH`). The older First-check cells are commands ("Run `check`, then ..."). Round-25 First-check cells are noun phrases or questions, and round-25 Verdict cells are sentences.
- Rows do not restate the fixture scope. They rely on the paragraph at lines 678-682. That is acceptable for the fixture, but the fit and split branches need their own scope words (see R2-1 and R3-1).

## Per-row findings

### Row 1 (line 686): served context from `/props`

Checked: for all 14 cells, the five raw body hashes match the receipt (`raw_hashes_ok=True`). `/props` `default_generation_settings.n_ctx`, every `/slots` `n_ctx`, and `/v1/models` `meta.n_ctx` carry one value in each cell (`receipt_fields_agree=True`). `total_slots` equals the number of slot entries in each cell.

- R1-1 (High). First check reads `meta.n_ctx_train`. Fix: read `meta.n_ctx` for the served per-slot value, and name `meta.n_ctx_train` separately as the declared training context. Evidence: `final/raw/K2.models.body`, line 1, `"meta":{...,"n_ctx":1024,"n_ctx_train":2048,...}`; receipt cell K2 has `props_n_ctx` 1024 and `models_n_ctx_train` 2048.
- R1-2 (Low). The receipt has no structured `meta.n_ctx` field, so the claim that the three endpoints agree is checkable only from the raw bodies. Fix in a later round: record `models_n_ctx` in the receipt.
- Verdict and Action: supported. The pool is not a function of the per-slot value: K2 has per-slot 1024 with pool 2048; K5 has per-slot 2048 with pool 4096; X1 has per-slot 2048 with pool 8192.

### Row 2 (line 687): `-c` unset, `-np` given, split cache

Checked: X1 (pool 8192, 2048 per slot) and X3 (pool 2048, 512 per slot) match the receipt. The X1 log supports the verdict's fit-on claim: line 547, "context size unset and KV cache not unified -> using 8192 for 4 sequences"; lines 1075-1078, "will leave 30968 >= 1024 MiB of system memory, no changes needed". The entry's X1 citations are correct: line 283 (probe, 2048), lines 812 and 1344 (8192), line 1610 (load_model, `kv_unified = 'false'`).

Round-20 check. I ran `nctx-crosscheck.py` `predict()` (lines 38-44) on each cell's argv with `-v` and `--fit off` removed:
- X1: predicted 512, observed 2048. Disagree, as the entry says.
- X3: predicted 512, observed 512. Agree.
- The other ten config cells (K1-K8, X2, X3): 10 of 10 agree. This confirms the entry's "other ten" claim.

- R2-1 (Medium). Action: "Do not use the round-20 value for this case; it gives 512 and is superseded." The symptom includes `--fit off`, and under `--fit off` the round-20 value is right (X3). Fix: add "with `--fit on`" to the Action, or add `--fit on` to the Symptom.
- R2-2 (Low). First check: it should say the last `llama_context: n_ctx = N` line. The first such line in X1 (line 283) is the fit probe and reads 2048.
- R2-3 (Low, optional). Add X1 log line 547 as the direct evidence for the fit-on rule. The row currently cites S106, which is the code path, not the observation.

### Row 3 (line 688): several requests at once

Checked (receipt `requests` and logs):

| cell | args | cache | two requests | status | release lines |
|---|---|---|---|---|---|
| L1 | `-c 0` | unified, pool 2048 | concurrent, prompt 1000, n_predict 600 | 500, 500, "Context size has been exceeded." | log 1852 and 1866: `stop processing: n_tokens = 1025` |
| L2 | `-c 8192 -np 4 --no-kv-unified` | split, pool 8192 | concurrent, same size | 200, 200 | none |
| L3 | `-c 0` | unified, pool 2048 | sequential, same size | 200, 200 | none |

The L1 init line (log line 1082) reads `kv_unified = 'true'`. The "1025 tokens each" wording in the row is correct for the two release lines.

- R3-1 (Medium). Verdict, first clause: "Concurrent requests are bounded by the pool total, not by the per-slot number" is not limited to unified caches. The only overflow test was unified (L1). L2 is split and passed. The entry's own mechanism (fixture entry, bullet at lines 65-67, citing S113) says a split cache keeps one stream per sequence, so a split pool is not one shared budget. Fix: start the clause with "On a unified cache (`kv_unified = 'true'`)".
- R3-2 (Low). First check: "how large is the pool" is read from the startup log. The entry itself says the pool line needs `-lv 4` or `-v` (lines 137-141), and `ExecVerbosityControl.md` lines 63-83 show that at `-lv 3` the pool line is absent and at `-lv 4` it appears. Fix: "and, with `-v` or `-lv 4`, the last `llama_context: n_ctx = N` line".
- R3-3 (Medium). Action: "Size concurrent use from the pool and the request sizes" states a sizing rule that was never tested. The only shape tested is two equal 1000-prompt, 600-token requests on a 2048 unified pool. The entry says "No claim is made for other request counts or sizes" (lines 129-130). "Escalate a consumer that assumes more" names no owner or path. Other rows in this table name one (line 133: "Escalate auth handling to kagi"). Fix: state the tested fact (two slots at 1025 cells each, 2 × 1025 > 2048, both requests failed) and remove the unnamed escalation or name its owner.

### Row 4 (line 689): the pool size

Checked: the K1 `props`, `slots` and `models` bodies contain no key naming kv, unified, pool or layout (script section 3). K1 and X2 differ only in `props.media_marker` (random per launch) and `models.data[0].created` (a timestamp). The slot bodies are identical. So "K1 and X2 report identical values" is accurate for the capacity fields.

- R4-1 (Medium). Action: "Require the verbose log line or the launch flags as evidence; without them the pool is unknown." Launch flags do not give the pool value by themselves. They give it only through the row-2 rule, and only where fit cannot lower the context. The entry itself says large models differ (lines 158-159). Environment variables `LLAMA_ARG_*` can also change those inputs, and the round-20 checker refuses such receipts (`nctx-crosscheck.py` lines 47-50). "Unknown" should read "unknown from these three endpoints", because `/metrics` was not read (line 136). Fix: "Require the last `llama_context: n_ctx = N` line from the verbose log. Launch flags are not evidence of the pool by themselves; without that line the pool is unknown from these three endpoints."
- R4-2 (Low). `-lv 4` is not in the receipt; all 14 cells used `-v`. The `-lv 4` threshold comes from `ExecVerbosityControl.md` lines 63-83, a sweep on the K6 arguments. Say so, or cite that file.
- R4-3 (Low). S112 (the README, SOURCES row at line 124) is cited for an absence claim about endpoint output. A README cannot show what an endpoint omits. The raw bodies do. Fix: cite `final/raw/K1.*.body` and `final/raw/X2.*.body`, and keep S112 for "the docs promise nothing about it".

### Scope paragraph (lines 678-682)

Checked:
- Build 11755 (704366d76): the receipt's `server_version` reads "version: 0.7.0-dev (build 11755, commit 704366d76)". Verified.
- Fixture `stories260K.gguf`, sha256 `270cba1b…256d`: the file at `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` hashes to `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, size 1185376 bytes. This matches the receipt. Verified.
- Training context 2048: GGUF `llama.context_length` = 2048; the logs print `n_ctx_train = 2048`. Verified.
- No sliding-window or rope-scaling keys: the GGUF header has 19 key-value pairs, none containing "sliding", and none with "rope" plus "scal" or "yarn". Verified.
- "Fit never lowers a context on this fixture": observed once on this host (X1 log lines 1075-1078, "no changes needed", 30968 MiB host memory). The general statement rests on source reasoning (entry lines 155-157, citing S106 `fit.cpp` 393-394), which I did not verify line by line. [INFERENCE for other hosts]

- S-1 (Low). Make the paragraph say "on this host" and add "CPU only" (entry line 154; the L1 log's system line lists CPU features only). The condition is memory-dependent (entry lines 158-159).

### Committed entry (pinned bytes)

- E-1 (Medium). Line 2 reads "14 fixture cells observed 2026-10-22T09:36:51Z to 09:36:59Z". The committed receipt says: cell starts 09:42:42.481Z to 09:42:49.702Z; cell stops 09:42:42.985Z to 09:42:50.463Z; top-level 09:42:42.438Z to 09:42:50.502Z. The committed line also has no receipt commit reference. Fix: "09:42:42Z to 09:42:50Z (receipt commit 5c95c8f111a981e316cd4933e38fc363e51f8604)". The working-tree entry already carries this text, uncommitted.
- E-2 (Low). See R1-2 (no structured `meta.n_ctx` in the receipt).

## Receipt cross-check (14 cells)

From `row-check.out` section 2 and section 5. `per-slot` is the `/props` value (equal to every slot value and to `meta.n_ctx`). `pool` is the last `llama_context: n_ctx` line in the cell's server log. `kv_unified` is from the startup line.

| cell | args | per-slot | total_slots | pool | kv_unified | meta.n_ctx_train | round-20 predict | agree |
|---|---|---|---|---|---|---|---|---|
| K1 | `-c 0` | 2048 | 4 | 2048 | true | 2048 | 2048 | yes |
| K2 | `-c 2048 -np 2 --no-kv-unified` | 1024 | 2 | 2048 | false | 2048 | 1024 | yes |
| K3 | `-c 2048 -np 2 --kv-unified` | 2048 | 2 | 2048 | true | 2048 | 2048 | yes |
| K4 | `-c 1024 -np 1` | 1024 | 1 | 1024 | false | 2048 | 1024 | yes |
| K5 | `-c 4096 -np 1` | 2048 | 1 | 4096 | false | 2048 | 2048 | yes |
| K6 | `-c 1000 -np 3 --no-kv-unified` | 512 | 3 | 1536 | false | 2048 | 512 | yes |
| K7 | `-np 2 --kv-unified-per-slot 512` | 512 | 2 | 1024 | false | 2048 | 512 | yes |
| K8 | `-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512` | 512 | 4 | 4096 | true | 2048 | 512 | yes |
| X1 | `-np 4 --no-kv-unified` | 2048 | 4 | 8192 | false | 2048 | 512 | NO (observed 2048) |
| X2 | `-c 8192 -np 4 --no-kv-unified` | 2048 | 4 | 8192 | false | 2048 | 2048 | yes |
| X3 | `-np 4 --no-kv-unified --fit off` | 512 | 4 | 2048 | false | 2048 | 512 | yes |
| L1 | `-c 0` | 2048 | 4 | 2048 | true | 2048 | 2048 | yes |
| L2 | `-c 8192 -np 4 --no-kv-unified` | 2048 | 4 | 8192 | false | 2048 | 2048 | yes |
| L3 | `-c 0` | 2048 | 4 | 2048 | true | 2048 | 2048 | yes |

Every cell's raw hashes match the receipt, every cell has `observed: true`, and `error` is null. Ports used were 47400-47413, inside the receipt's `port_range` [47400, 47419] and outside `port_refusal_set` [8080, 34113]. All teardown records report the port closed.

## Working tree (not the pin; a snapshot, not my target)

The working tree changed during this review and carries uncommitted edits. Snapshot values:
- SKILL.md: working tree sha256 `e1de48c7d6744c63` (95074 bytes) against the pin's `036ca4554e1fee67` (94578 bytes).
- Entry: working tree `864c0f2acf93753c` (16434 bytes; an earlier read gave `cea0f422…`, 16153 bytes) against the pin's `0959b2342c74b23e` (12358 bytes).
- Receipt: identical to the pin (`78c51385991b1261`).

What the working-tree rows do, checked against the same evidence:
- Row 1 now reads `meta.n_ctx` and labels `meta.n_ctx_train` separately. R1-1 is fixed.
- Row 2 now says "for the fit-on case". R2-1 is fixed. Its Symptom now adds "(or `-c 0`)", but its Verdict says "`-c 0` not run" and the entry marks `-c 0` split as [INFERENCE]. That is a new untested extension.
- Row 3's Verdict now says "On a shared (unified) pool". R3-1 is fixed. But it adds shared-pool results at 2048, 3072, 4096 and 8192 that are not in the receipt. They come from `.ufo/waves/round-25/a2-falsify/advice/ExecSharedPool8192.md` and `ExecBoundaryPool.md`, which I did not read. The Action still says "Escalate a consumer that assumes more" (R3-3 partly open), and "On a split cache, from the per-slot value" rests on INFERENCE.
- Row 3's First check still reads the pool size from the startup log (R3-2 open).
- Row 4's Action now requires the verbose log and qualifies launch flags. R4-1 is mostly fixed. The wording "Launch flags count only together with the `LLAMA_ARG_*` environment" is hard to parse; "Launch flags count only if no `LLAMA_ARG_*` variable is set, and fit cannot lower the context" would be clearer.
- The working-tree scope paragraph (lines 679-683) is unchanged, so S-1 is still open.
- The working-tree entry's line 2 now reads 09:42:42Z to 09:42:50Z, so E-1 is fixed.

## Smallest corrections, in order

1. Row 1 First check: `meta.n_ctx`, with `meta.n_ctx_train` named separately.
2. Row 2 Action: add "with `--fit on`".
3. Row 3 Verdict: put "On a unified cache" at the start of the first clause. First check: the pool comes from the `-v` or `-lv 4` log. Action: state the tested fact, and remove or name the escalation owner.
4. Row 4 Action: the pool comes from the last `llama_context: n_ctx` line; launch flags alone do not establish it; "unknown from these three endpoints". Cite the raw bodies rather than S112.
5. Entry line 2: `09:42:42Z to 09:42:50Z (receipt commit 5c95c8f111a981e316cd4933e38fc363e51f8604)`.
6. Scope paragraph: "on this host", "CPU only".
7. Row 2 First check: "last" log line.

## Residual risk and verification gaps

- No live server was run, by instruction. The `-lv 4` threshold, the `-c 0` split case and split-cache concurrency are unobserved in this seat.
- Source checks: I fetched `tools/server/server-context.cpp` at commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (access date 2026-10-22), requesting lines 5186-5188; the reader showed the nearby `/v1/models` `meta` object, which contains `{"n_ctx", meta.slot_n_ctx}`. I fetched `common/fit.cpp` at the same commit, requesting lines 393-394; the reader showed the memory-target reduction message around lines 392-398. I did not verify the `--fit-ctx` 4096 condition line by line.
- The falsify-wave advice files cited by the working tree (`ExecSharedPool8192.md`, `ExecBoundaryPool.md`) were not read.
- Lane master is 46be41cf, a descendant of the pin. `git diff --stat fa3b62ae 46be41cf -- SKILL.md corpus/knowledge/context-capacity.md .ufo/waves/round-25/final/context-capacity-receipt.json` printed nothing (exit 0), so the target files are identical there and the findings apply to master too.
- The working tree is still changing. Re-check the landed rows, not the snapshot.

## Commands run and exit codes

- `python3 -B row-check.py`: exit 0 (recorded at the end of `row-check.out`).
- `git rev-parse --verify fa3b…^{commit}`, `git rev-parse --verify master`, `git merge-base --is-ancestor fa3b master`, `git merge-base --is-ancestor 5c95c8f… fa3b`, `git show fa3b:<path>` for nine paths, `git log --oneline fa3b..master` (one commit, 46be41c), `git diff --stat fa3b master -- …` (empty): all exited 0 within the session.
- Python checks (hashing, JSON, GGUF header, the round-20 `predict()` import with bytecode writing disabled) ran without error. A `__pycache__` entry under `.ufo/waves/round-20/build/out/SrcServerNctx/` pre-dates this session (08:28Z), so I did not create it.

## Files written

- `.ufo/waves/round-25/a2-falsify/advice/ReviewerSkillDecisionRows.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/ReviewerSkillDecisionRows/row-check.py` (read-only check script; exit 0)
- `.ufo/waves/round-25/a2-falsify/out/ReviewerSkillDecisionRows/row-check.out` (captured output, exit 0)
- Scratch copies of pinned bytes, outside the lane: `/fast/scratch/hyaku/kama-r25a2w2/ReviewerSkillDecisionRows/` (SKILL.md.fa3b, corpus__knowledge__context-capacity.md.fa3b, .ufo__waves__round-25__final__context-capacity-receipt.json.fa3b, corpus__SOURCES.md.fa3b, tools__kama-context-capacity.py.fa3b, .ufo__waves__round-25__count-c2.py.fa3b, corpus__lessons__round-25.md.fa3b, .ufo__waves__round-25__preregistration.json.fa3b, .ufo__waves__round-25__errata-attempt-2.json.fa3b)
