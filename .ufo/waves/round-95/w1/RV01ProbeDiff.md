# RV01ProbeDiff — round-95 w1, C1 probe diff review (operability)

Lane `kama-shokunin`; reviewed `git diff 2011161d -- tools/kama-probe.sh` (base `2011161d5e5612fa953708cf54084b7f10ce99b1` → M1 `f6325660`, 7 hunks, +34/−23; M1 also adds `.ufo/waves/round-95/measured/c1-override.out`). Read-only in the lane; no tracked file touched. Everything below re-derived by extracting `ROUTER_PY` from both revs and calling it directly, and by re-running the extracted `router_file_states` with a PATH shim that logs the real `timeout` argv[1].

## Scope and fixtures
Diff rows enumerated exhaustively; required checks (a) clock grep, (b) three hostile files (900 000-tensor header, 49 000 000-element KV array, 200 MB file) plus base comparison, (c) `20 + 15*ncand` for ncand 1/8/40/2048, (d) undisclosed semantic changes. Fixtures built in scratch: 900 000-tensor GGUF (28.8 MB, state `-`); 392 MB GGUF whose one KV declares 49 000 000 zero-length strings then one tensor with a bad offset (state `invalid`); 200 MB version of the same (state `invalid`); plain 200 MB non-GGUF (`invalid`, 1 step); 192 B non-GGUF; 600 000-tensor invalid (the counter's slow class); valid 192 B GGUF; one candidate naming three distinct 200 MB files (`-m`, `--mmproj`, `-md`); three candidates naming three distinct 49M files.

## Diff: row → old (base) → new → effect
| # hunk (new lines) | old | new | effect |
|---|---|---|---|
| 1 543–555 header doc | "parse budget or deadline exceeded" | "step/byte budget exhausted" + r95 paragraph | doc only |
| 2 560–579 constants | `import ... time`; `PER_FILE_SECONDS=15.0`; `DEADLINE=...` | import without `time`; both deleted; `MAX_STEP_BYTES = MAX_STEPS` | no clock in ROUTER_PY; new constant never read (NOTE-4) |
| 3 609–612 `gguf_parse` | `global DEADLINE; DEADLINE = monotonic()+15` | deleted | a single path has no wall cutoff at all |
| 4 635–641 `need()` | `steps>MAX_STEPS or (steps&0xFFF)==0 and monotonic()>DEADLINE` | `steps>MAX_STEPS` | (a) satisfied for the read path |
| 5 686–695 `skip_strings` refill | `if monotonic()>DEADLINE: raise Unknown` | `steps+=1; if steps>MAX_STEPS: raise Unknown` | per-chunk clock gone; chunk refills now charge 1 step (base charged none) |
| 6 815–836 `router_file_states` | `$1 body, $2... idx`; `timeout 60` | `$1 body, $2 ncand, $3... idx`; `limit=$((20+15*ncand))`; `timeout "$limit"` | pass ceiling now derived from candidate entries |
| 7 891–895 caller | `router_file_states "$body" "${cand[@]}"` | `... "$ncand" "${cand[@]}"` | ncand = number of `unloaded`, not-failed entries |

Unchanged, no hunk: `gguf_state` memo key `(dev,ino,size,mtime_ns,ctime_ns)`; `file_state` return vocabulary (`missing|invalid|-`; a valid parse is mapped `ok`→`-`); `router_entries`; `router_autoload`/`/props`. So neither a repeated `/props` nor an `entries` path changed; a slow `/props` still decides the verdict (carried, r94 SC02 F4, undisclosed changes: none).

## Commands and outputs (exit codes)
- `git diff 2011161d -- tools/kama-probe.sh` → 7 hunks, `34 23 tools/kama-probe.sh` (exit 0).
- `grep -n 'time\.\|DEADLINE\|PER_FILE' new-router.py` → **no match, exit 1**. Same grep over the whole probe → exit 1; only the wrapper's `timeout` (:831) remains.
- PATH-shim log of the argument actually passed, ncand = 1, 8, 40, 2048 → `limit=35`, `limit=140`, `limit=620`, `limit=30740` (exit 0), i.e. exactly `20+15*ncand`.
- Direct calls, `python3 -c "$ROUTER_PY" <body> files 0` (exit 0 every row; new parser): 900k tensors → `-`, **4 000 001 steps**, 1.92–2.20 s user, 9.1–19.6 s wall; 49M-element array → `invalid`, **766 014 steps**, 7.89–8.41 s user, 24.7–35.1 s wall; 200 MB/25M-element array → `invalid`, **390 831 steps**, 4.02 s user, 8.5–15.2 s wall; plain 200 MB → `invalid`, 1 step, 0.03 s; 192 B non-GGUF → `invalid`, 1 step; valid 192 B GGUF → `ok` internally (=`-` through `files`), 10 steps.
- Base parser, same fixtures: 900k → `-` (11.2 s wall); 49M → `-` after 15.08–15.09 s (per-file clock); 200 MB array → `0 invalid` at 14.06 s wall but `0 -` at 15.15 s (the clock race the claim targets; host load varies).
- Wrapper, same bytes and same command, repeated: `./new-run.sh body_1arr.json 1 0` (1 candidate, 49M array, true state `invalid`) → load1 155–158: 28.5 s `0 invalid`; **35.1 s no line**; **35.0 s no line**; 33.0 s `0 invalid`; load1 90–97: 9.2 s and 9.0 s `0 invalid`. Base: 15.1 s `0 -`. Full log: `out/RV01ProbeDiff/wrapper-flips.txt`.

## Findings
**BLOCKER-1 — the verdict is still a wall-clock function at the pass level, and the fallback is a false green.** For one candidate naming one 49M-element KV file the bytes decide `invalid` at 766 014 steps (8.4 s user CPU), but the wrapper's `timeout 35` decides whether that line exists. Observed both outcomes for identical bytes and identical command at load1 155–158: `0 invalid` (→ `nbad=1 == ncand` → `MODEL_UNLOADED router-model-invalid`) and *no line* (→ `nbad=0 < ncand` → `MODEL_OK router-unloaded-autoload`, tools/kama-probe.sh:889–899). At load1 90–97 the same command completed in 9 s. That is exactly the round-94 defect (same bytes → `invalid` idle / `-` under load) relocated from `ROUTER_PY` to the wrapper. The plan's disclosed limit (d) excuses "a listing of very many distinct slow files"; this is `ncand=1`. The frozen 10-cell counter was not run by this seat, but its slow fixture is 600 000 tensors (1.71 s user, 8.06 s wall at load1 147), i.e. ~4–8× cheaper in wall than the file class above, so the cells can pass while C1's sentence ("the verdict is a function of the file's bytes") is false.

**DEFECT-2 — `MAX_STEPS` does not count the parser's work; the 15 s/candidate derivation is unsound.** `skip_strings` charges `steps += n // 64` after iterating n elements (tools/kama-probe.sh:702) and 1 step per 1 MiB chunk (:689); the per-element `unpack_from` is uncharged. Measured: 766 014 steps = 7.9–8.4 s user CPU, while 4 000 001 steps = 1.9–2.2 s user CPU — 4× more CPU for ⅕ the steps. The source comment pricing "MAX_STEPS work, measured ~4 s … ~12 s under heavy load" (:824–827) is contradicted: MAX_STEPS work measured 1.9–2.2 s user / 9–20 s wall, and one 49M-element file (below MAX_STEPS and below MAX_META) measured 7.9–8.4 s user / 24.7–35.1 s wall at load1 155. `MAX_META` bounds elements (≤64M) but not their wall cost, so "a hostile file ends `-` after a fixed amount of work whatever the CPU contention" is false for this class: it ends `invalid` after a load-dependent wall time, or gets truncated.

**DEFECT-3 — ncand counts entries, the work is per path; the small-ncand ceiling is below the old constant (reproduced regression against base).** `file_state` parses every occurrence of `-m/--model/-mm/--mmproj/-md/--model-draft`, so one candidate can own ≥3 distinct parses, but the allowance is 15 s per candidate entry. The source claim "Repeated paths share one memo entry, so ncand over-estimates the work and never under-estimates" (:828) is false for distinct paths. Reproduced back-to-back at load1 142–148: candidate with three distinct 200 MB `invalid` paths → BASE `timeout 60` + 15 s/file: 30.4 s, `0 invalid` (`MODEL_UNLOADED`); NEW `timeout 35`: 35.0 s, **no line** (`MODEL_OK`). Base-green → new-red, i.e. removal of the per-file clock plus the smaller pass ceiling lost a protection the clock provided. Also undisclosed: for ncand=1/2 the derived ceiling (35 s/50 s) is *below* the round-94 constant 60 s, while the per-file 15 s cap (base's real budget unit for a 3-path candidate = 45 s) is gone.

**NOTE-4 — dead constant:** `MAX_STEP_BYTES = MAX_STEPS` (tools/kama-probe.sh:576) is defined and never read.

**NOTE-5 — behaviour change vs base:** `skip_strings` chunk refills now consume step budget (base did not); bounded by ≤512 extra steps at `MAX_META`, no verdict change observed, but it narrows the budget for vocab-heavy files by up to 512 of 4 000 000 steps.

**NOTE-6 — plan/frozen-counter numbers disagree (calibration-adjacent, C3 cannot see prose):** `plans/round-95-claims.md:46` says "W03 twenty distinct slow" and :65–66 "~50 s of CPU at 20 distinct slow files"; the frozen counter has `SLOW_FILES = 40` (tools/round95-router-budget.py:88) and its docstring says "40 × ~2.0 s = ~82 s". The C1 cell list and disclosed limit (b) do not match the counter's committed bytes.

**NOTE-7 — residual risk in C1's own counter (not run here):** measured wall inflation at load1 155–158 was 4–9× (2.16 s user → 19.6 s wall for the 900k fixture; 600k slow fixture 1.71 s user → 8.06 s wall at load1 147). W03's derived limit is 620 s; 40 × 15.5 s = 620 s, so at sustained load1 ≥160 the counter's own discriminator can truncate and redden `mismatches`/`load_stable`. A green run at low load would not prove the 15 s/candidate bound holds at the load the plan says it claims under.

**NOTE-8 — checks that came back clean:** (i) no slow-but-valid file is graded `invalid`/`ok` where base graded `-`: `file_state` maps `ok`→`-`, so both revs return `-` for a valid 192 B GGUF and for a valid 49M-string-array header; (ii) `router_entries` and `router_autoload` (`/props`) have no diff hunk, so repeated `/props` and `entries` behaviour is unchanged; (iii) `MAX_META` is still enforced at `need()` (:641) and in `skip_strings` (:700); (iv) where the pass survives, the change is a real improvement: base `-` (clock) vs new `invalid` for the 49M and 200 MB files at low load.

## Deliverables
- `.ufo/waves/round-95/w1/out/RV01ProbeDiff/wrapper-flips.txt` — every wrapper run above with load1 before/after, wall, raw output.
- `.ufo/waves/round-95/w1/out/RV01ProbeDiff/final-receipt.txt` — clock grep, timeout argv log, direct-call state/steps/CPU for both revs.
- `.ufo/waves/round-95/w1/out/RV01ProbeDiff/timeout-args.log` — shim capture (`limit=35/140/620/30740`).
- `.ufo/waves/round-95/w1/out/RV01ProbeDiff/` — `build_fixtures.py`, `call_one.py`, extracted `new-router.py`/`base-router.py`, `new-funcs.sh`/`base-funcs.sh`, `wraprun.sh`, `new-run.sh`, `base-run.sh` (reproduction harness).
Scratch `/fast/scratch/hyaku/kama-r95/RV01ProbeDiff` removed after copying the receipts.

VERDICT: falsified — C1's sentence "the verdict is a function of the file's bytes" fails at the pass level (49M-element KV file: `invalid`/MODEL_UNLOADED at load1 90–106, truncation→`-`/MODEL_OK in 2/4 runs at load1 155–158; three-path candidate: base invalid, new MODEL_OK back-to-back), and MAX_STEPS under-counts the string-array work the 15 s/candidate budget is priced against.
