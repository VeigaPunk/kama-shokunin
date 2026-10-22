VERDICT: Amended C2 can clear the learning bar, but only through "admitted knowledge on uncovered ground" (the KV pool versus the per-slot ceiling, fit raising an unset split context, the shared-pool concurrency failure, and what the endpoints cannot show). It cannot clear the bar by supersession alone. On 10 of the 11 configuration cells the per-slot values only replicate the round-20 rule. The current entry draft overclaims in five places, and `count-c2.py` accepts the wrong KV pool for X1, the cell that carries the supersession.

Seat: KamaR25a2.CriticLearningBarA2 (critic, read-only, wave 1). Lane tip `1fc41e346853afd98cbd7010af5db4e54dc877f7` (`git rev-parse HEAD master`, exit 0). Access date for every source: 2026-10-22. No llama-server child was started and no port was opened. Live values below come from sibling attempt-2 outputs under `.ufo/waves/round-25/a2-build/out/` (untracked, `git status` shows `?? .ufo/waves/round-25/a2-build/`). I re-read their raw logs and bodies; I did not re-run any server.

## Axes

- Coverage (C2's axis): does the entry hold ground that the admitted corpus did not hold?
- Calibration: are prediction matches reported as replication, not as learning?
- Provenance: does each claimed value rest on the bytes it cites?
- Single authority: does a second context rule stay beside round-20 without a cutover?

## Which cells produce new knowledge and which only replicate

Command: `python3 .ufo/waves/round-25/a2-build/out/CriticLearningBarA2/r20-vs-observed.py` (exit 0, output in `r20-vs-observed.out`). It imports round-20 `predict()` unchanged and compares it with `ExecRawReplicate/receipt-config-cells.json`. `r20_pool` is the pool implied by the round-20 model. `predict()` itself returns only the per-slot value.

```
cell args r20_slot obs_slot slot_agree r20_pool obs_pool pool_agree
K1 '-c 0' 2048 2048 yes 2048 2048 yes
K2 '-c 2048 -np 2 --no-kv-unified' 1024 1024 yes 2048 2048 yes
K3 '-c 2048 -np 2 --kv-unified' 2048 2048 yes 2048 2048 yes
K4 '-c 1024 -np 1' 1024 1024 yes 1024 1024 yes
K5 '-c 4096 -np 1' 2048 2048 yes 4096 4096 yes
K6 '-c 1000 -np 3 --no-kv-unified' 512 512 yes 1536 1536 yes
K7 '-np 2 --kv-unified-per-slot 512' 512 512 yes 2048 1024 NO
K8 '-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512' 512 512 yes 4096 4096 yes
X1 '-np 4 --no-kv-unified' 512 2048 NO 2048 8192 NO
X2 '-c 8192 -np 4 --no-kv-unified' 2048 2048 yes 8192 8192 yes
X3 '-np 4 --no-kv-unified --fit off' 512 512 yes 2048 2048 yes
```

| Group | Cells | What it adds |
|---|---|---|
| Replication only | K1-K4, X2, plus the per-slot field of every cell except X1 | Round-20 `predict()` already gives these. K1-K3 are also pilot echoes (`pilot.md:12-16`). |
| New on the pool only | K5 (pool 4096, serves 2048), K6 (pool 1536 is above `-c 1000`), K7 (pool equals slots × per-slot, 1024; the round-20 implied pool is 2048), K8 (pool 4096 while 4 × 512 = 2048 is reachable [INFERENCE]) | The pool never appears in the admitted corpus. All of these values were derived from source beforehand (attempt-1 critics), so they confirm the source reading; they are not discoveries. |
| Carries new knowledge | X1, the X1/X3 pair, K1 against X1/X2, L1, L2, L3 | These are covered in the counterexamples below. |
| Confirms round-20 under one flag | X3 | Round-20 is correct when `--fit off` is set. |

## Counterexample 1: X1 is not the lane's first observation of fit raising the context

- The attempt-1 record, committed at `5388b7c` (`git ls-files` lists `.ufo/waves/round-25/build/out/ExecEdgeCells/raw/E09-np2-noc/server.log`), already served `-np 2` with no `-c` as `n_ctx_slot = 2048, kv_unified = 'false'` (`E09-np2-noc/server.log:10`). Round-20 `predict()` gives 1024 for that launch.
- I checked the amendment's honesty note (`preregistration-amendment-2.json:9`) by printing the first 400 characters of every `summary.json` row in three serializations. No head contains `props_n_ctx` or `slots_n_ctx`, so the claim that the author saw no values holds. Even so, the answer to "one of the two is wrong" (`preregistration-amendment-2.json:28`) is already in committed bytes for 2 slots.
- Correction: the entry cites E09 as earlier, unadmitted corroboration. It must not call X1 a discovery or a blind prediction.

## Counterexample 2: `count-c2.py` accepts the fit-probe pool for X1

- X1's server log holds three `llama_context: n_ctx` lines: 2048 at `ExecRawReplicate/X1/server.log:283` (the context fit measures first), then 8192 at `:812` and `:1344` (the served context). The trace line at `:547` reads `context size unset and KV cache not unified -> using 8192 for 4 sequences:`.
- `count-c2.py:55-57` accepts the pool if *any* such line ends with the recorded value.
- Command: `python3 .ufo/waves/round-25/a2-build/out/CriticLearningBarA2/probe-line-counter.py /fast/scratch/hyaku/kama-r25a2/CriticLearningBarA2/receipts` (exit 0, output in `probe-line-counter.out`):

```
X1 recorded kv_pool_n_ctx 8192
genuine exit 0 registered 14 observed 14 bound True missing []
probe exit 0 registered 14 observed 14 bound True missing []
X1 n_ctx lines in order [2048, 8192, 8192] served (last before load_model) 8192
X3 n_ctx lines in order [2048] served (last before load_model) 2048
```

- So a receipt that records X1's pool as 2048, which is exactly the round-20 value, still meets `registered 14 observed 14 bound True`. The counter does not protect the one pool value the supersession rests on.
- Related: `ExecLoadReplicate/load_replicate.py:186-196` keeps the *first* line. That is harmless for the L configurations but wrong if reused for X1. `ExecCapacityTool/kama-context-capacity.py:386` correctly takes the last line (`pool_candidates[-1]`).
- Correction: the entry, the tool and the falsify wave all read the pool from the last `llama_context: n_ctx` line before `srv load_model: initializing`, and quote its log line number. Hardening the counter the same way only makes the target harder, so it is allowed (amendment 1 sets the precedent). That choice belongs to the L1.

## Counterexample 3: supersession aims at a wave artifact, and round-20 is right except in one case

- `nctx-crosscheck.py` lives only under `.ufo/waves/round-20/build/out/`. Outside round 25, `grep` finds it only in `.ufo/waves/round-20/build/advice/SrcServerNctx.md:21-22`. It is not an admitted entry.
- The admitted entry `corpus/knowledge/gguf-declared-identity.md:26-32` is not wrong. It says "Do not divide `ctx` by `total_slots` blindly" (line 31). It cites `SrcServerNctx.md` as a source (line 1), and that source holds the incomplete rule: "n_ctx starts from explicit context size, or training context when zero" (`SrcServerNctx.md:6`). The code version is `nctx-crosscheck.py:41`.
- X3 shows that the round-20 rule is correct under `--fit off`, and the table above shows it correct on 10 of 11 configuration cells.
- Correction: scope the supersession to "default `--fit on`, `-c` unset, split cache". Name `SrcServerNctx.md:6` and `nctx-crosscheck.py:41` as corrected for that case only. Say that `gguf-declared-identity.md` is extended, not refuted. Point its line 31, and `SKILL.md:665-667`, at the new entry so the lane keeps one authority. Without that pointer, the bar credit is "uncovered ground", not "stronger entry superseding a weaker one".
- Not covered by any cell: the same raise should apply to `-c 0` with a split cache, because `common/fit.cpp:198` tests `n_ctx == 0` [INFERENCE]. No split `-c 0` cell was run.

## Counterexample 4: the draft gets the failure order wrong and overstates the L cells

Evidence: `ExecLoadReplicate/runs.md`, `l-cells-receipt.json`, and the raw logs under `/fast/scratch/hyaku/kama-r25a2/ExecLoadReplicate/`.

- **Failure order.** `ScribeEntryDraft/context-capacity.md:84-86` says the server sends the error "then retries with a halved batch". The log shows the opposite order: `retrying with smaller batch size ... n_batch = 1024` down to `n_batch = 1`, then `Context size has been exceeded. off = 0, n_batch = 1`, then `send_error` for both tasks. The same order appears in all three repetitions (`L1-rep1.log:1827-1840`). In source, a unified cache first tries to purge idle slots (`server-context.cpp:4335`, `1810-1813`), then halves the batch. At `n_batch == 1` it fails every processing slot and stops (`:4298-4301`, `:4318-4320`, `:4329`).
- **L1 result.** L1 predicted that "at least one" request fails. In fact both requests got HTTP 500 in 3 of 3 repetitions (6 of 6 requests, `elapsed_s` 0.025-0.044). Both were admitted: `new prompt, n_ctx_slot = 2048 ... task.n_tokens = 1000` (`L1-rep1.log:1245,1249`). Both were cut at `n_tokens = 1025` (`:1831,1837`), that is 1000 + 25 + 25 = 2050, which is above the 2048 pool. A per-slot ceiling is therefore not an admission guarantee.
- **"Fourfold".** The draft says K1 and X2 differ fourfold in full-context concurrency (`context-capacity.md:88`). Only the pool ratio was observed (2048 against 8192). The load actually tested was 2 requests of 1600 tokens each. Four concurrent full-context requests were never run.
- **L3 scope.** L3 sent `cache_prompt: false` (`load_replicate.py:200-201`). The server defaults are `cache_prompt = true` and `cache_idle_slots = true` (`common.h:637-638`), under which idle slots can keep their cache in the shared pool until it is purged under pressure (`server-context.cpp:1810-1830`) [INFERENCE, untested]. The finding "L1's failure is concurrency, not request size" holds only for `cache_prompt: false`.
- **L log provenance.** `load_replicate.py:94` opens each log with `"ab"` (append), and the script ran twice. Each of the 9 L logs holds two server launches (`grep -c 'load_model: initializing'` gives 2 for every file). The receipt's `log_lines` therefore mix two launches, while `requests` comes from one. Correction: one fresh log per launch, or record which launch the lines came from.

## Counterexample 5: "No HTTP field" is a universal claim the evidence does not enumerate

- What is observed: K1 (pool 2048, shared) and X1/X2 (pool 8192, split) return byte-identical `/slots` bodies (sha256 `6939aec1…7d27`, `ExecRawReplicate/summary.md`). Their `/props` bodies differ only in `/media_marker`, and their `/v1/models` bodies only in `/data[0]/created` (my JSON diff of `K1`, `X1` and `X2` `props.json` / `v1_models.json`). The only `/props` key that mentions context is `/default_generation_settings/n_ctx`.
- What was not checked: `/metrics` was not read (it is not enabled at these flags). The HTTP 500 under load is itself an HTTP-visible signal of the limit.
- The draft's line `context-capacity.md:110-113` says the pool *value* appears only at `-v`. In fact the pool value also shows at default verbosity in some launches: the attempt-1 E06 log at `-lv 3` has `rounding down to 1536` (`E06-c1000-np3-nokvu/server.log:9`), and K7 logs `sizing KV pool to ... = 1024` at info level (`ExecRawReplicate/K7/server.log:9`, run with `-v`; default verbosity for that line is [INFERENCE]). What is absent at `-lv 3` is the `llama_context: n_ctx` line.
- The claim that `-v` does not change the served bodies was checked on two cells only, K1 and K6 (`ExecVerbosityControl/body-diff-summary.json`).

## Minimal must-say list for `corpus/knowledge/context-capacity.md`

1. The per-slot values of K1-K8, X2 and X3 replicate the round-20 rule (10 of 11 configuration cells). Prediction matches are calibration evidence only, and K6 is a measurement.
2. Two numbers per launch: the KV pool (the last `llama_context: n_ctx` line before `load_model: initializing`, with its log line number) and the per-slot ceiling. Give a per-cell pool table.
3. Fit raising: with the default `--fit on`, `-c` unset and a split cache, the pool equals `n_ctx_train` × slots. X1 gave pool 8192 with 2048 per slot, and the trace line at `X1/server.log:547` names the cause. With `--fit off`, X3 gives the round-20 value (pool 2048, 512 per slot). Corroborate with the committed E09 (2 slots). The `-c 0` split case is untested.
4. Scoped supersession: correct `SrcServerNctx.md:6` and `nctx-crosscheck.py:41` for that one case only. `gguf-declared-identity.md:26-32` is extended, not wrong. Repoint its line 31 and `SKILL.md:665-667` to the new entry.
5. Shared-pool failure: in L1, two admitted concurrent requests both received HTTP 500 `Context size has been exceeded.` in 3 of 3 repetitions, each at `n_tokens = 1025`. The order is: purge idle slots (unified cache only), halve the batch down to 1, then fail every processing slot.
6. Load scope: 2 concurrent requests × (1000 prompt + 600 generated) tokens, `cache_prompt: false`. The pool ratio is 1:4. No full-context or four-way concurrency was tested, and L3 does not cover the server's default prompt caching.
7. Surfaces: "no field in `/props`, `/slots` or `/v1/models` at these flags", backed by the byte and JSON diffs above. `/metrics` was not read. "Only at `-v`" refers to the `llama_context` line, not to every pool value. The `-v` equivalence was checked on K1 and K6 only.
8. Provenance: X1-X3 and L1-L3 predictions are source-derived (attempt-1 critic seats and the attempt-2 author), and the X1 mechanism was already present in the committed E09 record.
9. Keep the draft's Scope and Does-not-establish blocks (`context-capacity.md:120-153`). Add that on large models, memory decides whether fit raises or lowers the context.

## Defect or tradeoff

- Replication on 10 cells is a tradeoff the judge can accept if it is labelled as replication. Presenting it as learning would be a defect.
- The counter accepting the probe line, the inverted failure order in the draft, "at least one" against the observed both, the unscoped "fourfold" and "no HTTP field", and the appended L logs are all fixable defects.
- None of them requires narrowing the target `registered 14 observed 14 bound True`.

## Sources (pinned to 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, fetched fresh 2026-10-22 with `curl -sS -f`, every fetch exit 0; sha256 values in `sources.sha256`. `server-context.cpp` `dd1de0f2…2329` equals S060. `server-context.cpp`, `server.cpp` and `README.md` are byte-identical to the round-16 snapshot, checked with `cmp`)

- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp L195: "with non-unified kv, we need to take into account n_streams"; L270: "llama_context would use only hp_nct in total for n_ctx == 0, resolve the context before measuring anything else"; L272 `cparams->n_ctx = n_ctx_max;`
- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp L4301: `err = "Context size has been exceeded.";`; L4320: `send_error(slot, err);`; L4329: "stop, do not retry with smaller batch size"; L4335: `if (!try_clear_idle_slots()) {`; L1813: `if (!params_base.kv_unified) {`
- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/common.h L637: "bool cache_prompt = true; // whether to enable prompt caching"; L638: "bool cache_idle_slots = true; // save and clear idle slots upon starting a new task"
- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp L177: "size the KV pool from --kv-unified-per-slot, unless the user pinned it with -c"
- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp L377: `cparams.n_ctx = GGML_PAD(cparams.n_ctx, 256);`; L391: "n_ctx is not divisible by n_seq_max - rounding down to %u"

## Files written

- `.ufo/waves/round-25/a2-build/advice/CriticLearningBarA2.md` (this report)
- `.ufo/waves/round-25/a2-build/out/CriticLearningBarA2/r20-vs-observed.py`, `r20-vs-observed.out`
- `.ufo/waves/round-25/a2-build/out/CriticLearningBarA2/probe-line-counter.py`, `probe-line-counter.out`
- `.ufo/waves/round-25/a2-build/out/CriticLearningBarA2/sources.sha256`
- Scratch: `/fast/scratch/hyaku/kama-r25a2/CriticLearningBarA2/src/*` (pinned raw sources), `/fast/scratch/hyaku/kama-r25a2/CriticLearningBarA2/receipts/{genuine,probe}.json` (synthetic receipts)

Tools installed or updated: none.
