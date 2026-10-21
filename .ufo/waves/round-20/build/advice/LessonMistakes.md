VERDICT: partial - all five round-19 outside findings reproduce; the scratch/process premise is wrong on timing (run 24:31 total, 13:02 past completion, not "24 min after the round") and the 30ed378 rewrite changed the mechanism sentence, not only wording.

Scope: draft `## Mistakes` rows for `corpus/lessons/round-20.md` (lane not modified; rows below are for L1 to write). Lane HEAD `37bd4c5b`. [INFERENCE] = unexecuted reasoning.

## Draft rows (class | evidence pointer | captured-by | criterion that should have caught it | fix, shown able to fail)

| ID | Class | Evidence pointer | Captured-by | Criterion that should have caught it | Fix / shown able to fail |
|---|---|---|---|---|---|
| R1 | filed lesson row rewritten in place | `git show 30ed378 -- corpus/lessons/round-18.md` (line 42; `git blame -L 42,42` = 30ed378). Old `server-queue.cpp:279` resets `running = false;` at 134 → new "`start_loop()` overwrites `terminate()`'s `running = false` (134) with `running = true` at `server-queue.cpp:279`" | outside spot-check `round-19-verifier-spotcheck.md` item 4 | PROTOCOL.md:135-137 ("never a rewrite of the filed bytes, labelled or silent"); QUALITY KQ22 (QUALITY.md:123) guards `corpus/SOURCES.md` only, so no lesson-level guard exists (`tools/sources-append-only.py` default `--path corpus/SOURCES.md`) | Append a named erratum to round-18.md quoting the original line 42. Add a removed-line check over `corpus/lessons/` per commit pair. Shown able to fail: that check must flag 30ed378 on round-18.md (1 removed line). [INFERENCE: check not built] |
| R2 | stale counts after registry grew 3→4 | Registry rows: 3 at 7229fa9 and f1790e2; 4 at 028235e (`json` len, exits 0). Stale text: `SCORECARD.md:823-824` (blame 7229fa9: `required=3 … selftest 5 cases`), `SCORECARD.md:846` ("three registry-row digests", blame f1790e2), `LOG.md:1146`, `round-19.md:12`. Tip (scratch clone at 37bd4c5): `tools/citation-provenance.py` → `required=4 found=4 verified=4 missing=0 mismatch=0`, exit 0; `--selftest` → `ok (15 cases)`, exit 0 | outside spot-check item 2 | Round-19 measured 4 rows at 028235e (`evidence/c1-counting.txt` line 1 `measured_commit=028235e6…`, `required=4`), but SCORECARD/LOG were not swept after the registry change. No check compares hand-typed `required=N` text against HEAD output. Note: the `missing=3` "before" figures were true for the 3-row registry; the stale part is the post-state. | Append an erratum correcting 823-824 and 846 to the tip values. Add a sweep: every `required=N` in SCORECARD/LOG/lessons must match the tool's HEAD line. Shown able to fail: a `required=3` line against the 4-row tip → mismatch exit. [INFERENCE: sweep not built] |
| R3 | wave label "falsify-wave refutation" on build-wave seats | `.ufo/waves/round-19/falsify/refused-attempt-1.json` (`seats 66, refused 66, spawned 0`, "Background job limit reached (100)"); `corpus/lessons/round-19.md:79`; `SCORECARD.md:844`. `CritC1Inflation` is in `build/dispatch.json` (True), absent from `falsify/dispatch.json` (False). `falsify/` has no `validation.json` (`ls \| grep -c validation` → 0) | outside spot-check item 3 | Round-16 routed defect 1(a) and round-17 M4: `.ufo/waves/round-17/dispatch-provenance.py` (`--selftest` 28/28, exit 0) requires a per-wave `validation.json` with policy and spawned count. `grep -n validation.json SKILL.md corpus/QUALITY.md PROTOCOL.md` → no hits: the requirement is not in any governing doc | Take a wave label only from `dispatch.json` (`wave`, `counts.spawn`); a heading naming a wave requires `validation.json` with spawned > 0. Shown able to fail: relabel a build-seat fixture as falsify; the validator must reject (spawned 0 vs 1). [INFERENCE: validator not run on this case] |
| R4 | selftest receipt measured on a dirty tree, count not reproducible | `.ufo/waves/round-19/evidence/final-selftests.txt` line 1 `measured_tree=working-tree-on-5b108c1a…` (no commit; `c1-counting.txt` line 1 has `measured_commit=`); gate line `77 mutations`; committed C2 advice at 7229fa9, `build/advice/C2ConsistentSwap.md:26`, says `76 mutations`. Difference unexplained | outside spot-check item 5 | `SKILL.md:577,598`: `worktree_not_at_measured_revision` (could-not-evaluate, exit 4) exists for the round-13 live gate only; not applied to manually run selftest receipts | Every receipt header states `measured_commit` and clean `git status --porcelain`; dirty tree → could-not-evaluate. Shown able to fail: run the gate selftest on a dirty copy, expect exit 4. [INFERENCE: not run] |
| R5 | seat process left running and 5.9 GiB /tmp scratch | `.ufo/waves/round-20/evidence/r19-scratch-removal.txt` line 3: pgid 562220 `strace -f … survivors.py --json`, elapsed 24:31, children 4; lines 4-70: 67 `/tmp/kama-r19-*` dirs, `5.9G total`; `ScorecardErratum` 1048 MB. Spot-check item 8 and "675 MB strace written 04:02" | outside spot-check item 8 (scratch found, not removed); L1 at 04:12:16 stopped the process and removed scratch | `round-19/build/spec.json` and `falsify/spec.json`: 0 matches each for kill, "delete your", scratch. Spot-check's process check pattern `llama\|ollama\|vllm\|ggml` does not cover `strace`/`survivors`. Round-20 bounds add both clauses | Round-closure sweep recorded with exit: `ps -eo pgid,etimes,args \| grep -E 'strace\|survivors'` and `ls -d /tmp/kama-r<N>-*` empty before closure; every build/falsify spec carries "kill every process you start; delete your scratch". Shown able to fail: a fixture `sleep` left running must be flagged. [INFERENCE: sweep not built] |

Premise correction for R5: process start = 04:12:16 − 24:31 = 03:47:45 (`-03:00`). Completion was 03:59:14 (`round-19-verifier-spotcheck.md`, driver digest). It therefore outlived completion by 13:02, not 24 minutes.

## Executed commands and exits

| Command (cwd) | Exit | Observed |
|---|---|---|
| `python3 -c` registry len at 7229fa9 / f1790e2 / 028235e (`git show … \| json`) | 0 | 3 / 3 / 4 |
| `git blame -L 820,846 SCORECARD.md`; `git blame -L 42,42 corpus/lessons/round-18.md` | 0 | 7229fa9 / f1790e2 / 30ed378 |
| `git show 30ed378^:corpus/lessons/round-18.md \| sed -n 42p` vs current | 0 | sentence changed as in R1 |
| `grep -rn "required=3…" SCORECARD.md LOG.md corpus/lessons` | 0 | stale strings listed in R2 |
| `python3 -c` on `falsify/refused-attempt-1.json` read | 0 | seats 66, refused 66, spawned 0 |
| `python3 -c` `CritC1Inflation` in build vs falsify `dispatch.json` | 0 | True / False |
| `ls falsify/ build/ \| grep -c validation` | 1 | 0 matches |
| `grep -n validation.json SKILL.md corpus/QUALITY.md PROTOCOL.md` | 0 | no hits (via pipeline) |
| `python3 .ufo/waves/round-17/dispatch-provenance.py --selftest` (scratch cwd) | 0 | `selftest: 28/28 checks passed` |
| `grep -c` kill/delete/scratch in round-19 build and falsify specs | 0 | 0 / 0 / 0 each |
| `ps -eo … \| grep strace\|survivors` | 1 | none running now |
| `ls -d /tmp/kama-r19-*` | 0 | 0 remain (67 listed in removal file) |
| `git clone` lane → scratch; `checkout 37bd4c5` | 0 | clean tree (0 porcelain lines) |
| `python3 tools/citation-provenance.py` at 37bd4c5 (scratch clone) | 0 | `required=4 found=4 verified=4 missing=0 mismatch=0` |
| `python3 tools/citation-provenance.py --selftest` (scratch clone) | 0 | `ok (15 cases)` |
| `python3 -c` time arithmetic | 0 | start 03:47:45; overlap after completion 0:13:02 |

Not executed: the proposed sweeps and guards (marked [INFERENCE]); no gate re-run on any dirty tree.

## Tools, processes, cleanup

- Tools installed or updated: none. Used git, python3 stdlib, ps, grep.
- Processes started: none (the dispatch selftest and citation checker ran to completion).
- Scratch: `/tmp/kama-r20-LessonMistakes-2` (lane clone) removed at end. Out dir `.ufo/waves/round-20/build/out/LessonMistakes-2/` holds `receipts.txt` only.
- Lane: no writes (`git status --porcelain` shows only the untracked `.ufo/waves/round-20/` from the fleet).
