# MT04ToolIdCreated — C1 falsification: id/created and usage-cached checks

Seat: MT04ToolIdCreated (mutation-tester, leaf). Item: falsify the id/created and
usage cached checks of the C1 operability counter. Judged on: operability.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (freeze amendment 1).
Counter: tools/round63-c1-counter.py (unmutated, run from its clone path).
Evidence: .ufo/waves/round-63/w1/out/MT04ToolIdCreated/ (tally.tsv, one `.line` and
`.err` per row, tool-mutants.patch, counter-mutants.patch, probe-C03-C04.txt,
rerun.sh, score.sh, probe.py). Scratch root
/fast/scratch/hyaku/kama-r63/w/MT04ToolIdCreated removed before yield.
Tools installed: none (git, python3, and the lane's pre-existing ~/.local/bin/llama-server
only). Nothing committed to the lane; every commit is inside my scratch clones.

## Method

- Baseline (unmutated counter, pristine tip, clone `base`): met=True.
- Harness (tool clone, commit 30ce1384 "harness neutral"): a `_MUT` selector dict at
  tool line 198, a body re-sealer (`_mutate_completion`, applied right after the
  completion capture, re-computes body_sha256/body_bytes/content-length), and a
  `check()` wrapper that can lie (`store='lie'`) or invert (`store='invert'`) one stored
  check, plus a `force_ok` verdict override. With every selector at its neutral value
  the counter still prints met=True, so the harness itself is not the cause of any row.
- Each mutant = one selector line changed, committed in the clone, scored by the
  unmutated counter at that commit (`--repo <clone> --tip <commit>`).
- Counter mutants: one clause removed or forced per commit in a separate clone
  (`counter`), scored at the pristine tool tip (or cross-scored against a tool mutant
  commit). Counter file for each row is the committed blob at that commit.
- "lie" = stored `passed` set to True while the resealed body fails the check (verdict
  then REQUEST_OK). "honest" = stored `passed` computed by the tool from the same
  mutated body (verdict FAIL). "invert" = stored passed flipped on an honest body and
  the verdict forced REQUEST_OK.

## Tool-side mutants (unmutated counter, 11 rows)

Every row prints `live_ok=0/1 ... met=False` (controls never run: `controls_targeted=0/0`,
`eval_selftest=0/3`, `errors=1`). They are killed by the live-receipt gate, not by a
targeted control. Fail sets (stderr `error: live: [...]`):

| row | defect (resealed body) | store | tip | live fail set | killed by |
|---|---|---|---|---|---|
| T01 | id="" | honest | 8fb39478 | completion_id_created, verdict | recomputed only |
| T02 | id="" | lie | 446bcc04 | completion_id_created, inconsistent:completion_id_created | recomputed + inconsistent |
| T03 | created=0 | honest | a2cfb2ed | completion_id_created, verdict | recomputed only |
| T04 | created=0 | lie | 2771366b | completion_id_created, inconsistent:completion_id_created | recomputed + inconsistent |
| T05 | created=true | honest | 520f515a | completion_id_created, verdict | recomputed only |
| T06 | created=true | lie | eda3ce08 | completion_id_created, inconsistent:completion_id_created | recomputed + inconsistent |
| T07 | usage.prompt_tokens_details removed | honest | 0a95d77a | completion_usage, verdict | recomputed only |
| T08 | usage.prompt_tokens_details removed | lie | 6894ea76 | completion_usage, inconsistent:completion_usage | recomputed + inconsistent |
| T09 | cached_tokens = prompt_tokens+1 | honest | 409aed52 | completion_usage, verdict | recomputed only |
| T10 | cached_tokens = prompt_tokens+1 | lie | 8d8137a5 | completion_usage, inconsistent:completion_usage | recomputed + inconsistent |
| T11 | body honest; stored id check inverted; verdict forced REQUEST_OK | invert | 109c7409 | inconsistent:completion_id_created ONLY | inconsistent alone |

Verdicts: T01-T11 = KILLED (met=False). Counter one-liner, identical for all 11 rows:

    tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]

Reading: the recomputed check alone catches every honest-store row. The `inconsistent:`
path fires on every lying-store row and is the only catch for T11, where the recomputed
check passes on the honest body. Both paths are live, but neither is exercised by any
targeted control (see below).

## Counter-side mutants (pristine tool tip 03a6a1d8)

| row | counter edit | verdict | one-liner (verbatim) |
|---|---|---|---|
| C01 | drop `cj['id'] != ''` | KILLED: idcr=2/3, escape id='' | `tool_present=1 live_ok=1/1 controls_targeted=43/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=2/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` |
| C02 | drop `cj['created'] > 1_000_000_000` | KILLED: idcr=2/3, escape created=5 | `tool_present=1 live_ok=1/1 controls_targeted=43/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=2/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` |
| C03 | drop `is_int(created)` | **SURVIVED** | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` |
| C04 | drop `isinstance(id, str)` | **SURVIVED** | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` |
| C05 | completion_usage forced True | **SURVIVED** | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` |
| C06 | drop cached_tokens range bound | **SURVIVED** | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` |
| C08 | `inconsistent` comprehension forced empty | **SURVIVED** | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` |

Cross-scoring (counter mutant run against a tool-side mutant receipt):

| row | counter | tool row | met | fail set / note |
|---|---|---|---|---|
| X-C06xT09 | C06 | T09 honest cached>prompt | False | inconsistent:completion_usage, verdict (killed by the stored-vs-recomputed path, not the recompute) |
| X-C06xT10 | C06 | T10 lying cached>prompt, resealed | **True (SURVIVED)** | receipt accepted; `...controls_targeted=44/44 ... met=True` |
| X-C08xT11 | C08 | T11 stored-only, verdict forced OK | **True (SURVIVED)** | receipt accepted |
| X-C08xT02 | C08 | T02 lying id='' | False | completion_id_created only (recompute still catches it) |

## Survivor findings (prominent)

1. **C05 — the whole completion_usage check has zero controls.** Forcing it true leaves
   44/44 standing and met=True. No targeted control names `completion_usage`; the 44
   controls contain `idcr` (3), `ptok` (2) and `tamper` rows but none of them can fail
   usage. The usage grading is therefore unpinned by the control set.
2. **C06 — the cached_tokens bound is unguarded, and a resealed lying receipt passes.**
   With the bound dropped, the tool-side receipt T10 (cached_tokens = prompt_tokens+1,
   stored passed=True, verdict REQUEST_OK) is accepted: met=True. The unmutated counter
   rejects T10 only through this clause. Honest T09 is rejected under C06 only by
   `inconsistent:completion_usage` (the verdict-side stored check), not by the recompute.
3. **C03 — created accepts a non-integer.** Dropping `is_int` on created leaves
   idcr=3/3 and met=True. Probe (probe-C03-C04.txt): created=1900000000.5 is False under
   pristine and True under C03. The integer discipline on created has no control.
4. **C04 — a missing or null id passes.** Dropping `isinstance(id, str)` leaves idcr=3/3
   and met=True. Probe: id missing and id=None are True under C04, False under pristine.
   No control plants a missing/non-string id; the only id controls are id='' (still
   caught by `!= ''`), created=True and created=5.
5. **C08 — the inconsistency comparison is unpinned.** Disabling it leaves met=True, and
   it is the only catch for T11 (stored-only disagreement on an honest body). No control
   names any `inconsistent:` failure.

What the unmutated counter does catch: every tool-side row T01-T11 (KILLED). The live
gate (`live_ok`) rejects them before any control runs, so those kills show the gate
works but grant no control credit. C01 and C02 are KILLED by the existing idcr controls
(id='' and created=5 escape).

## Not run / limits

- Tool-level float created and tool-level missing id were not planted (the harness has
  no kinds for them); C03/C04 are shown by the probe on the genuine receipt body, not by
  a tool-side run.
- C07 (drop the `isinstance(pd, dict)` guard) was not run; prompt_tokens_details-missing
  is covered at tool level (T07/T08) against the unmutated counter.
- The C08 result is shown against two receipts; no other stored-vs-recomputed row was
  tried.
- No verdict on the frozen claims is given here; the L1 scores the frozen kill rule.

## Pointers

- rerun: out/MT04ToolIdCreated/rerun.sh regenerates tally.tsv (24 rows: BASE, NEUTRAL,
  T01-T11, C01-C06, C08, X-C06xT09, X-C06xT10, X-C08xT11, X-C08xT02; ~22 s).
- Tool-mutant commits: tool clone 30ce1384 (neutral) then T01-T11; counter-mutant commits:
  counter clone 240c50a7 (C01), 9f22afe0 (C02), b0378180 (C03), 8cfa3b6e (C04),
  8824f697 (C05), 163263ef (C06), 1278944d (C08). Patches in out/MT04ToolIdCreated/.

Tally (tally.tsv, 24 rows): tool-side T01-T11 KILLED 11/11 (live gate, 0 control credit); counter-side C01,C02 KILLED; C03,C04,C05,C06,C08 SURVIVED (met=True with defect present); cross X-C06xT10 and X-C08xT11 SURVIVED (met=True); base and neutral met=True.
