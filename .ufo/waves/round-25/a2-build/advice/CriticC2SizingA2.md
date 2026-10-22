Verdict: fixable defect, not a reject. Amendment 2 does not narrow anything: its target only gets harder, and the counter still yields one value from one command. But the committed counter (`count-c2.py`, blob `1c78a96b`, commit 5388b7c, unchanged at 1fc41e3) prints `registered 14 observed 14 bound True` for 15 synthetic receipts that it should reject. Two of those undercut the findings C2 exists to produce: the X1 KV pool size can be matched to the `--fit` probe's log line, and nothing checks that L1's requests actually overlapped in time. Register a stricter counter in an amendment 3 before any receipt is committed. The proposed counter below accepts only a subset of what the current one accepts.

Seat: KamaR25a2.CriticC2SizingA2 (critic, read-only, wave 1, attempt 2). Access date for every source: 2026-10-22. I started no llama-server child and opened no port. I ran git-writing work only in my own clone, `/fast/scratch/hyaku/kama-r25a2/CriticC2SizingA2/clone`, checked out at 1fc41e346853afd98cbd7010af5db4e54dc877f7. In the lane I ran only read-only `git log`, `git show`, `git status` and `git ls-files`, and no jj command. I installed no tools.

# 1. Is the target one value that one command re-derives from committed bytes?

Mostly yes. Three defects need wording fixes.

- **Mostly yes.** `count-c2.py` prints a single line. In that line, `registered` is the constant `len(CELLS)` (count-c2.py:21-36, 14 entries). `observed` is the claim value. `bound` is a gate. The control receipt A00 prints `registered 14 observed 14 bound True missing []` (exit 0, `counter-attacks.out`).
- **Defect 1a: the before value is not output that the command prints.** preregistration-amendment-2.json:25 says `receipt absent at efe58e96: count-c2.py exit 2 (cannot read receipt); registered 14, observed 0`. Two things are wrong with it:
  - `count-c2.py` does not exist at efe58e96. `git log -- .ufo/waves/round-25/count-c2.py` lists only 5388b7c.
  - On a missing receipt the command prints no count. At 1fc41e3 in my clone, `python3 .ufo/waves/round-25/count-c2.py` gives exit 2, and stderr shows `cannot read receipt: [Errno 2] No such file or directory: '.ufo/waves/round-25/final/context-capacity-receipt.json'`. Stdout is empty.
  - So `registered 14, observed 0` is an inference, not command output.
- **Defect 1b: the counter's bytes and the receipt are read from the working tree, not from a commit.** `registered 14` is hardcoded in the counter itself. Someone could edit the args of a `CELLS` entry, for example X1's, to match whatever ran, and the line would still print 14 of 14. The receipt path is relative (count-c2.py:18), so the command only works when run from the lane root. Run from the fleet root it gives exit 2.
- **Defect 1c: the target is a prefix of the printed line, not the whole line.** The full output is `registered 14 observed 14 bound True missing []` (count-c2.py:97-98).

# 2. Is any clause universal without enumeration?

Four clauses claim "every" or "always", and the counter does not enforce any of them.

| Clause | Location | Counterexample receipt that still prints 14 of 14 with the committed counter |
|---|---|---|
| "every cell launches `... -v <args>`" | preregistration-amendment-2.json:35 | A18: every cell's argv lacks `-v`. The counter never reads argv. |
| "every /slots n_ctx" | preregistration.json:33 | A10: `total_slots` 4 but `slots_n_ctx` `[7]` |
| "every required field is present with the required type" | count-c2.py:6 | A07: `prompt_tokens` 1000.0 and `n_predict` 600.0 are floats. Lines 67-68 test `==`, not the type. |
| "Exit 0 always when the receipt parses" | count-c2.py:13 | A14: one extra cell `{"id": ["K1"]}` makes `cid not in CELLS` (line 88) raise `TypeError: cannot use 'list' as a dict key`, exit 1 |

The `kv_pool_n_ctx` clause says "for every cell" (preregistration-amendment-2.json:24). That one is properly enumerated, because `CELLS` lists all 14 cells.

# 3. Are the added cells and the kv_pool requirement non-narrowing relative to amendment 1?

Yes. I found no narrowing.

- **N02, args unchanged.** The K1-K8 args in `count-c2.py` equal preregistration.json:37-44 byte for byte. The X1-X3 and L1-L3 args equal preregistration-amendment-2.json:28-33. All K kinds are `config`. Output: `N02-args: ... equal count-c2 args: True; amendment-2 cells_added (6) equal: True`.
- **N01, the stricter rule implies the amendment-1 rule.** I wrote the amendment-1 counting rule (preregistration-amendment-1.json:17-18) as a predicate. Over 20000 randomly mutated K cells, the number that `count-c2` accepts but the amendment-1 rule rejects is `0`.
- **Conclusion.** 14 of 14 implies 8 of 8 under amendment 1, and the new `bound` gate and `kv_pool_n_ctx` field only add requirements. The after-value moved from `observed 8 of 8` (preregistration-amendment-1.json:27) to 14 of 14, which is strictly harder.

# 4. Does the counter accept something it should not?

Yes. Command: `python3 .ufo/waves/round-25/a2-build/out/CriticC2SizingA2/counter-attacks.py <clone> <scratch>/receipts`, exit 0, output in `counter-attacks.out`. The harness runs the counter bytes from `git show 5388b7c:.ufo/waves/round-25/count-c2.py`. Every case printed `registered 14 observed 14 bound True missing []` unless the table says otherwise.

| Case | What the bad receipt does | Committed counter | Proposed counter |
|---|---|---|---|
| A01 | K1 `kv_pool_n_ctx` 48 against the log line `n_ctx = 2048` (line 55 uses string `endswith`) | 14 of 14 | 13 of 14 |
| A02 | X2 `kv_pool_n_ctx` 192 against `= 8192` | 14 of 14 | 13 of 14 |
| **A03** | X1 log holds the fit-probe line `= 2048`, then `= 8192` twice. The receipt claims pool 2048. | **14 of 14** | 13 of 14 (`missing ['X1']`) |
| A05 | K6 with only the warning `n_ctx is not divisible ... rounding down to 1536`, which is not the info line `-v` was added to capture | 14 of 14 | 13 of 14 |
| A06 | L1 request status 0 and -1 (no HTTP response at all) | 14 of 14 | 13 of 14 |
| A07 | float `prompt_tokens` and `n_predict` | 14 of 14 | 13 of 14 |
| A08 | L1 with 5 requests (the amendment says two) | 14 of 14 | 13 of 14 |
| **A09** | L1 labelled `concurrent`, but its two requests never overlap (this is really an L3 run) | **14 of 14** | 13 of 14 |
| A09b | L1 with no request timing at all | 14 of 14 | 13 of 14 |
| A10 | `slots_n_ctx` length 1 against `total_slots` 4 | 14 of 14 | 13 of 14 |
| A11 | `props_n_ctx` -1, `total_slots` -5, `n_ctx_train` 0 | 14 of 14 | 13 of 14 |
| A12 | `server_version` `build 117559` passes the substring test at line 95 | bound True | bound False |
| A13 | every cell carries its own `server_version` `build 9999` and a zero sha; only the receipt-level fields are checked | bound True | bound False |
| A14 | an unhashable extra id | exit 1 (traceback) | exit 0, extra cell ignored, 14 of 14 |
| A18 | `-v` missing from every argv | 14 of 14 | 0 of 14 |
| A17 | two cells carry the same pasted log lines | 14 of 14 | 14 of 14 (residual risk; see section 6) |
| A04 (control) | the A03 log with the final pool 8192 | 14 of 14 | 14 of 14 |
| A16 (record) | the attempt-1 tool receipt `build/out/ExecCapacityTool/context-capacity-receipt.json` | 0 of 14, bound False | 0 of 14, bound False |

## Why A03 matters: the X1 KV pool can be satisfied by the fit probe's value

The fit step builds its own throwaway llama_context before the real one, and that probe prints its own `llama_context: n_ctx` line.

- **The probe creates a real llama_context.** In fit.cpp the probe context is created with `llama_context * ctx = llama_init_from_model(model, *cparams);` (fit.cpp:66). Its log lines are demoted to debug level (fit.cpp:52), and debug lines print at `-v`.
- **The probe runs first with the user's context, then again with the fitted one.** The first probe runs with the initial parameters (fit.cpp:264). With the context unset and a split cache, `n_streams = ... std::max<uint32_t>(1, cparams->n_seq_max)` (fit.cpp:197) and `cparams->n_ctx = n_ctx_max;` (fit.cpp:272). The probe is then re-run for more than one stream (fit.cpp:274-276).
- **An unset context resolves to the training context.** llama-context.cpp:219 resolves `n_ctx == 0` to `hparams.n_ctx_train`, and line 396 prints `n_ctx                 = %u`.
- **The pilot log already shows two such lines for one launch.** The amendment-2 pilot log `/fast/scratch/hyaku/kama25-a2/pilot-v.log` (K6 args, `-v`) prints `llama_context: n_ctx                 = 1536` twice, at lines 284 and 820. There are also two `print_info: n_ctx_train` blocks, at lines 56 and 591. So the probe context logs a pool line at `-v`.
- **[INFERENCE, unrun] What this predicts for X1.** An X1 log at `-v` would carry `n_ctx = 2048` from the first probe and `8192` from the second probe and the final context. The committed `any(...)` check (count-c2.py:55-57) accepts either value.
- **Why that defeats the cell.** 2048 is exactly the value that would make round-20's `nctx-crosscheck.py` look right (preregistration-amendment-2.json:28, 30). The cell meant to settle "fit raises an unset split context" cannot settle it under this counter.

## Why A09 matters: nothing shows L1 was concurrent

L1 and L3 have the same args, `-c 0`, and differ only in a free-text `request_mode` label (count-c2.py:59-61). The claim "the failure in L1 is concurrency, not request size" (preregistration-amendment-2.json:33) needs request timing that the counter never asks for.

# 5. Provenance defect, the same class as amendment 1's first correction

- preregistration-amendment-2.json:6 says `"written_utc": "2026-10-22T09:30Z ..."`.
- The file's mtime is 06:28:17 -0300, which is 09:28:17Z.
- Commit 5388b7c carries `cI=2026-10-22T06:28:44-03:00`, which is 09:28:44Z.
- So the typed stamp is later than the commit that carries the file. The hedge "the commit ... is the authoritative order" does not make the stamp true.

# 6. Smallest safe correction (each item only makes the target harder)

1. **Register the stricter counter in an amendment 3, committed before any receipt.** The proposal is `out/CriticC2SizingA2/count-c2-proposed.py`. It is the 5388b7c bytes plus these changes:
   - The pool value comes from the last line matching `llama_context: n_ctx +=  ?(\d+)\s*$`, compared as an integer. The last line is the final context after the fit probes [INFERENCE from the source order above]. Record every pool line in order, so that X1's probe value is reported as a finding rather than accepted as the pool.
   - Require at least one line matching `n_slots = N, n_ctx_slot = N, kv_unified = '(true|false)'`. This was the original measure at preregistration.json:33.
   - Require `len(slots_n_ctx) == total_slots`, and all four integers greater than 0.
   - Require `argv` to end with the registered args and to contain `--host 127.0.0.1 --no-webui --offline -v`. This enforces launch_rule.
   - For load cells:
     - exactly 2 requests;
     - integer status between 100 and 599;
     - integer `prompt_tokens` 1000 and `n_predict` 600;
     - numeric `t_start` < `t_end` on each request;
     - the requests overlap if and only if the mode is `concurrent`.
   - Bind to `\(build 11755, commit 704366d76\)` and the model sha. Any per-cell `server_version` or `model_sha256` must equal the receipt-level value.
   - Skip ids that are not strings, instead of crashing.
   - **Evidence that this only tightens.** N03: over 20000 mutated cells across all 14 ids, the number the proposal accepts but the committed counter rejects is `0` (`counter-attacks-proposed.out`). The target string stays `registered 14 observed 14 bound True`.
2. **Pin the closure command to the committed bytes:** `git show <amendment-3 commit>:.ufo/waves/round-25/count-c2.py | python3 - .ufo/waves/round-25/final/context-capacity-receipt.json`, run from the lane root at the receipt commit. I tested this form with the 5388b7c bytes on receipt A00; it prints the expected line with exit 0.
3. **Correct the before value** at preregistration-amendment-2.json:25 to: `no receipt at 1fc41e3: count-c2.py (added in 5388b7c) exit 2, stderr "cannot read receipt"; no count printed; observed 0 [INFERENCE] from the absent file`.
4. **Write the target as the full printed line:** `registered 14 observed 14 bound True missing []`.
5. **Correct `written_utc`** to `2026-10-22T09:28:17Z (file mtime); committed 09:28:44Z in 5388b7c`.
6. **Tell the tool executor that the counter's schema governs, not the other way round.** The attempt-1 tool emits the field names `props_default_generation_settings_n_ctx` and `props_total_slots`, plus a nested `server.version` and `log_lines` as objects. Its receipt scores 0 of 14 (A16). Changing the counter to fit that tool would loosen it.
7. **Residual risk (A17) that no counter fixes.** Pasted or fabricated log lines pass any field check. Commit each cell's raw server log and its raw `/props`, `/slots` and `/v1/models` bytes, and record their sha256 values in the receipt. The falsify wave can then recompute them.

**Impacted axes:**

- coverage: the honesty of the claim value `observed 14`;
- calibration: the X1 against X3 discrimination, and L1 against L3;
- provenance: the before value and `written_utc`.

**Judgement against a reject.** Nothing here forces a reject if amendment 3 lands before the receipt. If the receipt lands under the committed counter, `observed 14` stands only as a count. It must not be read as having established the X1 fit finding or the L1 concurrency finding.

# Sources

All are pinned to commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, fetched fresh on 2026-10-22 with curl (exit 0), and stored with sha256 in `/fast/scratch/hyaku/kama-r25a2/CriticC2SizingA2/sources.sha256`. The fresh `tools/server/server-context.cpp` is byte-identical to the round-16 snapshot (`diff -q`, exit 0). The snapshot has no `fit.cpp` or `llama-context.cpp` to compare.

- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/fit.cpp#L52 — "const ggml_log_level level_eff = level >= ud->min_level ? level : GGML_LOG_LEVEL_DEBUG;" (L52)
- same file #L66 — "llama_context * ctx = llama_init_from_model(model, *cparams);" (L66)
- same file #L197 — "const uint32_t n_streams  = cparams->kv_unified ? 1 : std::max<uint32_t>(1, cparams->n_seq_max);" (L197)
- same file #L270-L276 — "llama_context would use only hp_nct in total for n_ctx == 0, resolve the context before measuring anything else" (L270); "cparams->n_ctx = n_ctx_max;" (L272)
- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp#L219 — "cparams.n_ctx            = params.n_ctx           == 0    ? hparams.n_ctx_train           : params.n_ctx;" (L219)
- same file #L391 and #L396 — "n_ctx is not divisible by n_seq_max - rounding down to %u" (L391); "%s: n_ctx                 = %u\n" (L396)
- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L4301 — "err = \"Context size has been exceeded.\";" (L4301)

# Files written

- `.ufo/waves/round-25/a2-build/advice/CriticC2SizingA2.md` (this report)
- `.ufo/waves/round-25/a2-build/out/CriticC2SizingA2/counter-attacks.py`, sha256 17f467da…75dd: the harness. With a third argument it tests an alternative counter.
- `.ufo/waves/round-25/a2-build/out/CriticC2SizingA2/counter-attacks.out`: the committed counter, exit 0.
- `.ufo/waves/round-25/a2-build/out/CriticC2SizingA2/count-c2-proposed.py`: the proposal, not registered.
- `.ufo/waves/round-25/a2-build/out/CriticC2SizingA2/counter-attacks-proposed.out`: the proposed counter, exit 0, including N03.
- Scratch: `/fast/scratch/hyaku/kama-r25a2/CriticC2SizingA2/`, holding the clone, `src/` (pinned source copies), `sources.sha256`, and `receipts/` and `receipts-proposed/` (synthetic receipts).
