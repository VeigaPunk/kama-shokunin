# RV02BudgetCells — round-97 wave-1 C2 attack (kama)

Seat: reviewer (operability / calibration / depth). Lane `kama-shokunin`, plan `plans/round-97-claims.md`
§C2, counter `tools/round97-router-budget.py`, probe `tools/kama-probe.sh`.

Revision at every run below: `e057166e09ec069725bd0b0433fc50275ecd03ea` (HEAD during the review; the
probe sha256 is `0897ebffc304fe8d487eff4194f39e42210c3dbc2116e5511fbc472237487ca8`, the counter's
sha256 `24e2fad7c4fb58e9f3a4b56d8bbff776beac7ebd4a27fef581fae529fcb6ca2c` — both identical at the
freeze commit `9e605d41`, so K1 holds for the bytes I graded). `e057166e` is round-97 amendment 1
(`--slow-files 72`); it is comment-only relative to the freeze for the probe and does not touch the
counter: `git diff 40763bd2 9e605d41 -- tools/kama-probe.sh` changes the ceiling comment block only
(lines 575-586), and `git show HEAD:tools/round97-router-budget.py | sha256sum` equals the worktree
sha256.

Host: 32 cores, load average during my runs 39 → 118 (sibling wave-1 probes plus 64 self-raised
burners). No LSP server is mounted in this seat (`xd://lsp` absent), so caller/definition checks are
text-level: the counter is a standalone script with no Python importers
(`grep -rn "import.*round97\|from.*round97" --include=*.py .` returns nothing); its only invocations
are command lines in the plans, the wave spec and receipts. That gap is recorded in residual risk.

## 0. Verdict on C2's sentence

C2 as frozen says:

> the budget counter grades four probe forgeries the 13-cell set misses

and, in the predicate paragraph, `prints ROUTER_BUDGET97 cells=17 mismatches=0 positive_mismatches=0
load_cells=17 load_stable=1 budget=work … and exits 0 at M2; and the three control receipts print
survived=1 for the 13 legacy cells and caught=1 for the three new cells, one per mutant`
(`plans/round-97-claims.md:70-77`).

Verdict: **the instrument survives; the sentence does not, in three named places.**

1. **Coverage (true).** The 17 cells do catch the four named arithmetic classes. W15, W16 and W17 are
   each uniquely necessary for their class (my independent shapes below), and the 13 legacy cells are
   green under the shipped mutants (frozen receipts; my own legacy run for `flat6`). The exact step
   arithmetic in the plan recomputes: `5 + nd` with a 4-step preamble and a 5,000,000 cap.
2. **"three new cells" (false).** There are four new cells (W14-W17) and four mutants
   (`CELLS = 17`, `NEW_CELLS` of four, `MUTANTS` of four). The same stale "three" is in the counter
   docstring (`tools/round97-router-budget.py:13`) and in the committed wave spec
   (`.ufo/waves/round-97/w1-spec.json`, which says "16 cells; W14/W15/W16 catch three probe mutants").
   The predicate's receipt clause is therefore ungradable as written, and the seat brief that says
   "16 cells / three mutants" is itself a pre-freeze count, not the artifact. Amendment 2 (untracked
   at my observation, §7) plans to correct the prose.
3. **The fourth control does not implement the named forgery (major).** `nopreamble` charges **zero**
   parser steps on every header fixture (measured), not four fewer steps; a true four-step drop lands
   at 4,999,998 and is caught by W17 only (my shape A). The shipped receipt shows W14/W15/W17 red
   because it removes *all* `need()` charging, which is the `undercharge` class again. The sentence's
   W17 attribution is true, but the frozen control does not witness it.
4. **The predicate's exit-0 clause holds only under amendment 1, and the passing receipt cannot prove
   its own command.** The verbatim frozen command exits 2 (`c2-could-not-evaluate.out`, committed in
   `e057166e`). The amended run (`--slow-files 72`) does print the exact predicate line and exit 0,
   but the receipt records neither `--slow-files` nor the W03 entry count, its W03 line is still
   labelled `x40`, and its `load1_nat=89.53` shows the "natural" leg was already saturated by sibling
   probes (mine included). A 40-file run under that load produces an indistinguishable receipt.

Nothing below changes a frozen predicate; this is a recommendation, not an admission.

## 1. What I ran (exact commands)

All scratch under `/fast/scratch/hyaku/kama-r97/RV02BudgetCells/`; receipts copied to
`.ufo/waves/round-97/w1/out/RV02BudgetCells/`. Every counter invocation used the lane worktree
script and `--rev master` (resolved to `e057166e` at run time).

```
python3 tools/round97-router-budget.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --rev master --work <scratch> --cells new --control --expect survived
# then the same with --mutant flat6|undercharge|maxmeta|nopreamble --expect caught
#   -> out/repro-new-controls.out

python3 tools/round97-router-budget.py ... --cells legacy --control --expect survived --mutant flat6
#   -> out/legacy-flat6.out

# three forgeries built from `git show 9e605d41:tools/kama-probe.sh` with single-anchor patches,
# run through --probe-file:
python3 tools/round97-router-budget.py ... --cells all --control --expect survived \
  --mutant none --probe-file <shape>.sh
#   -> out/shape-all-controls.out (shapes A and C), out/shapeB-fixed-all.out (shape B, corrected)

# exact step counts: extract ROUTER_PY from each probe, print steps[0] at each verdict return,
# call gguf_parse() directly on the counter's own fixtures
#   -> out/step-counts.out
```

Step counts (parser steps at the verdict; `-` means `Unknown`/budget raised):

| fixture | base | undercharge | flat6 | maxmeta | nopreamble | shape A (preamble-4) | shape C (constant 7) |
|---|---|---|---|---|---|---|---|
| t900k.gguf (900k, nd=1) | `-` 5,000,001 | invalid 0 | `-` 5,000,001 | `-` 5,000,001 | invalid 0 | `-` 5,000,001 | `-` 5,000,001 |
| t833333.gguf (833,333, nd=1) | `-` 5,000,001 | invalid 0 | `-` 5,000,001 | `-` 5,000,001 | invalid 0 | invalid 4,999,998 | `-` 5,000,001 |
| mid4.gguf (700k, nd=4) | `-` 5,000,001 | invalid 0 | invalid 4,200,004 | `-` 5,000,001 | invalid 0 | `-` 5,000,001 | invalid 4,900,004 |

The honest call-site costs this confirms: `skip(u64())  # name` is two `need()` calls (the length read
and the skip), `nd = u32()` one, the dims `nd`, `u32(), u64()` two = `5 + nd`; preamble four. The
shipped `flat6` is exactly the claimed constant 6 — measured 4,200,004 on nd=4, identical to the plan's
number — because it collapses the `nd` dim reads into one `rd(8*nd)`. My first static count of 5 was
wrong (it missed the double charge in `skip(u64())`); the measurement refuted it, and I record the
refutation rather than the guess.

## 2. Findings

### F1 [blocker] The frozen C2 predicate says "three new cells" of four; the receipt clause is ungradable

- `plans/round-97-claims.md:77`: "`caught=1` for the **three** new cells, one per mutant".
- `tools/round97-router-budget.py:13`: "Round 97 adds **three cells** past that:" followed by W14, W15,
  W16, W17; `CELLS = 17` (line 142) with `NEW_CELLS` of four (line 146) and `MUTANTS` of four
  (lines 162-177).
- `.ufo/waves/round-97/w1-spec.json` (committed in the freeze): "tools/round97-router-budget.py
  (16 cells; W14/W15/W16 catch three probe mutants that survive the 13 round-96 cells)"; the seat
  brief inherits it. `git ls-tree -r 9e605d41 .ufo/waves/round-97/` shows the file in the freeze.

Consequence: the predicate sentence's second clause cannot be satisfied by the artifact (there is no
set of "three new cells"), and a reader who trusts the wave spec grades a 16-cell counter that does not
exist. The assertion `cells=17` is consistent with §C2 Cells (17) and the code; the prose is not. In a
round whose thesis is "the disclosures match the bytes", this is the same class of defect as round-96
defect 1, now in the plan and the committed wave spec rather than a probe comment.

### F2 [major] The fourth control is not the preamble-drop forgery; it is an all-`need()`-free probe

The patch is `tools/round97-router-budget.py:174-176`:

```python
"nopreamble": [(b"        def need(n):\n            steps[0] += 1\n",
                b"        def need(n):\n            steps[0] += 0 if steps[0] < 4 else 1\n")],
```

`steps[0]` only ever changes by `0` while `< 4`, so it is a fixed point: the counter stays 0 and every
`need()` is free forever. Measured on the shipped mutant: t900k `invalid` at 0 steps, t833333 `invalid`
at 0 steps, mid4 `invalid` at 0 steps (`out/step-counts.out`). The plan's arithmetic for the named
shape is a *four-step* drop: 5,400,000 at W14 and 5,399,996 at W17 for nd=1, still `-` at W14/W15 and
`invalid` at W17. My shape A (a separate `_calls` counter, bytes in `out/shapes/shapeA-preamble4.sh`)
gives exactly that: t833333 `invalid` at 4,999,998, t900k `-` at 5,000,001, mid4 `-` at 5,000,001, and
in the 17-cell control run only **W17** is red (`out/shape-all-controls.out`, `cells_ok=16`).

The shipped control's own new-cell receipt (frozen, base rev) is red at W14 **and** W15 **and** W17 —
which a four-step drop cannot be. So the `caught=1` receipt proves a stronger, different forgery that
largely duplicates `undercharge`. The sentence's W17 attribution survives on my cognate, but the frozen
control does not establish it; if the plan's control mapping is graded literally, it is false.

### F3 [major] W03's disclosure says 1.5 x 60 s; the code refuses at 1.25 x 60 s

- `tools/round97-router-budget.py:93`: "the counter refuses to claim it unless the natural pass costs
  >= **1.5 x 60 s**".
- `tools/round97-router-budget.py:157`: `MARGIN = 1.25`; line 633: `if not a.allow_clock and w03 <
  MARGIN * BASE_WRAPPER:` → the guard is **75 s**, not 90 s.

The freeze-time receipt `controls/c2-could-not-evaluate.out` (committed in `e057166e`) prints
`W03 natural pass 55.0s < 1.25 x 60s` and exits 2; amendment 1 cites the 75 s guard. This is a comment
stating a constant the code does not use — precisely round-96 routed defect 1 (the constant-6 comment),
now inside a frozen counter. K1 makes the false text permanent for the round; amendment 2's C2 v2 list
does not mention it.

### F4 [major] The amended predicate's receipt cannot prove which command produced it

- `--slow-files` is accepted (line 571) but never echoed: `MARGIN_HELP` (line 158) and the summary line
  (line 674) print `w03_seconds`, not the slow-file count; `grep -c "slow_files\|slow-files"
  .ufo/waves/round-97/measured/c2.out` → 0.
- The W03 cell id is hardcoded `"W03-slow-x40"` (line 487) even when `n_slow = 72`; the amended
  receipt's line 7 reads `W03-slow-x40 … 126.28s / 129.87s` while the process command line was
  `python3 tools/round97-router-budget.py --repo . --rev e057166e… --work /fast/scratch/hyaku/kama-r97/measured2 --slow-files 72`
  (observed with `ps -eo pid,etimes,args`).
- The final predicate line is `… rev=e057166e… w03_seconds=129.9 load1_nat=89.53 burners=64`
  (`measured/c2.out:35`) — no field binds the run to `--slow-files 72`.

A 40-file run under external load passes the 75 s guard just as well: my legacy `flat6` control at
load 71 → 118 measured W03 at 223.95 s. The receipt is therefore not self-describing; the amended
predicate's only pass can be attributed to the amendment only by the ephemeral process command line
and the plan text.

### F5 [major] The passing measurement's "natural" leg was load-saturated (honest-saturation claim)

`measured/c2.out:35` records `load1_nat=89.53` and `burners=64`. The natural pass ran while many
wave-1 seats were probing the same 32-core host: my own new-cell controls ran 08:26:39-08:28:38
(load 39.30 → 53.09), my legacy `flat6` control 08:30:47-08:38:06 (load 71.15 → 117.93), and the
three-shape control run 08:29:29-08:49:30. Other seats' counters were also active (`ps` showed
`MT01Forgeries` legacy runs and `RV03Intent`). The natural W03 (126.28/129.87 s) is therefore not a
natural-host measurement; the loaded leg (357.30/321.94 s) is loaded-vs-more-loaded. The verdict
stability under extreme load is a real result (all 17 cells matched), but the margin guard's purpose —
"the round-94 60 s wrapper would truncate this listing **on this host**" — was satisfied by contention,
not by host speed. The amendment's 72 x ~1.37 s ≈ 99 s figure is not evidenced by this receipt, and
the reviewer seat's own probes contributed to the load.

### F6 [major] Control receipts were produced on the base probe, not the probe under claim

`controls/c2-legacy-mutants.out` and `controls/c2-new-mutants.out` print
`rev=40763bd2… probe_sha256=11e5b01b…` (the round-96 probe) for the `none` and all four mutants, with
mutated shas `14efbe6f`, `2e31ff3b`, `6b5f6db4`, `9035b55e`. The probe under claim at the freeze is
`0897ebff…`; the same four mutants on it are `cae7b367`, `3a709856`, `22c311f1`, `b27dc8bf`
(my runs, `out/repro-new-controls.out`, at `rev=e057166e`). The base→freeze diff is comment-only
(verified), so the verdicts transfer, and my runs reproduce every new-cell catch and the legacy
`flat6` survival. But the frozen receipts do not by themselves show "byte patches of the probe under
claim" (plan:91); a reader must diff the probe to know the transfer is legitimate.

### F7 [minor] `KILL = 1200` is below the probe's derived pass limit for the amended W03 fixture

`tools/round97-router-budget.py:148` sets a 1200 s per-check `subprocess.run` kill. The probe derives
`20 + 25 * npaths` (probe:873); with `--slow-files 72` that is 1820 s. On a host roughly 12x slower
than this one the counter kills the probe at 1200 s and reports W03 red (`mismatches>0`, exit 1),
which would be a counter-side timeout, not a probe verdict. Current receipts peak at 357 s for the
load pass, so this is latent, not observed.

### F8 [minor] Amendment-1 wording overstates what it changed

`plans/round-97-amendment-1.md:3` says "before any C2 cell scored", but the exit-2 run printed all 17
natural cells (`ok=1` each) before stopping at the guard; "no cell scored" means no predicate verdict.
Line 23 says "same 17 cells", but the W03 cell is now 72 entries while its id still says `x40` and the
receipt does not state the count (F4). Line 3-4's "the frozen C2 predicate … was run verbatim" is
accurate and the refusal is honestly disclosed — this part is good practice, unlike the unlisted
receipt before it was committed.

### F9 [minor] "three control receipts" (plan:77) does not exist

There are two control files (`c2-legacy-mutants.out`, `c2-new-mutants.out`) with nine sections
(one real-probe section plus four legacy and four new mutant sections). Another stale "three".

### Non-findings (checked, clean)

- `flat6` is a genuine constant-6 probe (4,200,004 on nd=4, exact); W15 is the unique catcher of a
  constant per-header charge in the 6-7 range. My shape C (constant 7, 4,900,004) is caught by W15
  alone (`out/shape-all-controls.out`), and a constant 8 would be caught by W11 at nd=1.
- W16 is the unique catcher of the 100 MiB `MAX_META` lowering (frozen receipt: only W16 red).
- W17 is the unique catcher of a true four-step preamble drop (shape A: only W17 red). W14/W15/W16 and
  all 13 legacy cells stay green under shape A.
- K1: the counter bytes are unchanged at freeze, HEAD and worktree (`24e2fad7…`); the probe bytes at
  HEAD equal the freeze (`0897ebff…`).
- `undercharge` removes header charging (0 steps on all three header fixtures) while still charging
  large skips (n >= 32); that is why W16 is unaffected and W14/W15/W17 red — the claimed class, with
  a wider scope than "per-header".

## 3. Mutant/shape matrix (17 cells, `--control`, natural pass only)

| probe | W14 | W15 | W16 | W17 | legacy 13 | receipt |
|---|---|---|---|---|---|---|
| real probe | ok | ok | ok | ok | all ok | `out/repro-new-controls.out` (survived=1) |
| undercharge | **red** | **red** | ok | **red** | all ok (frozen) | cells_ok=1, caught=1 |
| flat6 (constant 6) | ok | **red** | ok | ok | all ok (my run) | cells_ok=3, caught=1 |
| maxmeta (100 MiB) | ok | ok | **red** | ok | all ok (frozen) | cells_ok=3, caught=1 |
| nopreamble (shipped; 0 steps) | **red** | **red** | ok | **red** | all ok | cells_ok=1, caught=1 |
| shape A: true 4-step drop | ok | ok | ok | **red** | all ok | cells_ok=16, exit 1 |
| shape B: 5+nd with persistent step memo, no ctime | ok | ok | ok | ok | **W02, W03, W08, W10 red** | cells_ok=13, exit 1 |
| shape C: constant 7 | ok | **red** | ok | ok | all ok | cells_ok=16, exit 1 |

My legacy `flat6` run: `out/legacy-flat6.out`, `cells=13 cells_ok=13 … survived=1 caught=0`,
`probe_sha256=cae7b367…`, `rev=e057166e`.

### Why each legacy cell stays green under a cheaper header charge

The shell's refine rule is: if **any** matching autoload candidate is `missing`/`invalid`, it counts it,
but only if *all* candidates are bad does it report `MODEL_UNLOADED`; one undecidable (`-`) candidate
sets `unloaded=1` (`tools/kama-probe.sh:939`, `if [ "$nbad" -lt "$ncand" ]; then unloaded=1; fi`). The
legacy fixtures are designed so that the cheaper parse reaches the same class they expect:

- W01/W02/W03/W05/W08 (slow_*.gguf, 600k nd=1, no data) and W11 (mid.gguf, 700k nd=1): a complete
  parse (3,600,004 / 4,200,004 steps, under the cap even honestly) ends at the offset/size check and
  returns `invalid`, the designed class. Flat6 changes 6/header to 6/header at nd=1, so nothing moves.
- W09: 1,200,000 headers > `MAX_TENSORS` → `-` before the tensor loop; header accounting is irrelevant.
- W12/W13: the 6,000,000-element string array charges in the array loop (`steps[0] += 1`,
  probe:703), not through `need()`; the budget still trips → `-`.
- W04/W05: ok.gguf/ok2.gguf are one/two tensors; W06 missing paths; W07 non-GGUF magic; W10 the same
  three states as the base probe (slow invalid → valid → invalid), all far under the cap.

That is exactly why the old set "cannot see" a header-accounting change: every legacy fixture's
complete parse is also its designed class, and the two budget-sensitive fixtures charge elsewhere.
The same argument holds for `undercharge` and the shipped `nopreamble` (the array loop still caps).
For `maxmeta`, no legacy fixture has a header position near 100 MiB.

## 4. Shape B detail (the memo shape the brief asked for)

A probe that keeps `5 + nd` but memoizes the step count `(dev, ino, size, mtime_ns)` across
invocations (no ctime) is caught by the legacy cells, not by W14-W17:

```
out/shapeB-fixed-all.out:
  W02-slow-x8     ok=0 run1=MODEL_OK/router-unloaded-autoload
  W03-slow-x40    ok=0 run1=MODEL_OK/router-unloaded-autoload
  W08-hardlink-x8 ok=0 run1=MODEL_OK/router-unloaded-autoload
  W10-rewrite     ok=0 v1=MODEL_OK v2=MODEL_OK v3=MODEL_OK
  W14..W17        ok=1
  cells=17 cells_ok=13 survived=0 caught=1
```

Mechanism: W03's parse of `slow_1` stores 3,600,004; W10's first invocation then starts that file at
the cached count and trips the cap (`-`), so the rewrite's third invocation, which must see the
original invalid bytes, returns loadable (`MODEL_OK`). In the other cells one poisoned candidate is
enough: `nbad < ncand` → `MODEL_OK` (probe:939). A first memo variant that cached only the `ok`/
exception paths passed all 17 cells; it was discarded because the slow fixture returns `invalid` from
the offset loop, not through `except Bad` — the corrected variant caches that path too. The cell
receipt is `shapeB-fixed-all.out`; the unit-level three-invocation trace is not copied, but the memo
file ended at `{…: 5000001}` and run3 changed from `invalid` (base) to `-` (memo).

Consequence for the claim: this shape is **not** a counter defect; W10 is the designed discriminator
and it works. It does mean the new four cells are blind to it, so C2's list must stay closed ("four
named arithmetic classes"), not "any accounting forgery". The brief's conditional ("if none catch it,
narrow the wording") does not fire: a legacy cell catches it. The wording still needs the other
corrections in F1/F2.

## 5. The predicate, amendment 1, and the measured receipt

- Verbatim frozen command at freeze (`--rev 9e605d41`, no `--slow-files`): all 17 natural cells
  `ok=1`, then `could-not-evaluate: W03 natural pass 55.0s < 1.25 x 60s`, exit **2**. Committed as
  `controls/c2-could-not-evaluate.out` and (at that commit) `measured/c2.out`, commit `e057166e`.
- Amendment 1 (`plans/round-97-amendment-1.md`, commit `e057166e`, 08:22:12) adds `--slow-files 72`
  (72 x ~1.37 s ≈ 99 s > 75 s guard) and says "nothing else changes … same 17 cells, same two host
  loads, same four mutants". It is honest about the refusal and is the right process move; its
  arithmetic is not evidenced on an idle host (F5) and its receipt is not self-describing (F4).
- Amended run (`ps` command line `--slow-files 72`, work `/fast/scratch/hyaku/kama-r97/measured2`,
  started ~08:25, finished 08:48:40) prints exactly:
  `ROUTER_BUDGET97 cells=17 mismatches=0 positive_mismatches=0 load_cells=17 load_stable=1
  budget=work probe=rev mutant=none probe_sha256=0897ebff… base_sha256=27065a5c… rev=e057166e…
  w03_seconds=129.9 load1_nat=89.53 burners=64`, exit 0.
  W03 natural 126.28/129.87 s, W03 load 357.30/321.94 s. At my observation the file is a **modified
  but uncommitted** worktree file (`git status --porcelain .ufo/waves/round-97/measured/c2.out` → `M`);
  the committed version at `e057166e` is the exit-2 receipt.
- Consequence: K2 is not triggered by this receipt (`mismatches=0`, `cells=17`, `load_stable=1`), and
  the predicate string is satisfied in the letter under the amended command. The load and provenance
  caveats above are the residual risk; a strict reading of "exits 0 at M2" against the frozen command
  remains false (exit 2), which is why amendment 1 is load-bearing.

## 6. Fixes I recommend (L1 owns the edits; I do not edit)

1. Restate the plan/counter "three" sentences to four (amendment 2 A/D already plans this) and name
   the wave-spec "16 cells" as a pre-freeze count in the report; do not silently rewrite the dispatch.
2. Replace the `nopreamble` patch with a call-count patch (`_calls = [0]`, first four `need()` calls
   free) or rename it and stop attributing W17 to it. My `out/shapes/shapeA-preamble4.sh` is the
   measured cognate (W17 only, 4,999,998). Re-run the four controls after the replacement; the
   `--expect-cell` restatement in amendment 2 D is necessary but not sufficient if the patch still
   charges zero.
3. Change the W03 docstring "1.5 x 60 s" to `MARGIN = 1.25` (or raise MARGIN to 1.5 and re-run). This
   is a frozen-counter byte change; it needs a recorded amendment, as F3 cannot be fixed by prose
   outside the counter without hiding the inconsistency.
4. Echo `slow_files=<n>` and the actual W03 entry count in the porcelain/summary line, and stop
   labelling a 72-entry fixture "x40" (derive the id or add the count). Without this, no receipt can
   prove the amended command.
5. Re-take the amended measurement with no sibling probes and no reviewer-seat counters running, and
   record `load1_nat`; the current passing receipt's natural leg at load 89.53 cannot support the
   host-speed argument. If a shared host makes this impossible, disclose the contention and grade the
   load clause as "verdict stability under two loads", not "natural vs synthetic".
6. Raise `KILL` above the probe's derived pass limit for the amended fixture, or derive it, so a slow
   host cannot produce a counter-side red cell.

## 7. Interaction with amendment 2 (observed untracked at 08:51, unapplied)

`plans/round-97-amendment-2.md` (6119 bytes, untracked, mtime 08:51) plans C2 v2: docstring counts to
four, `--expect-cell <id>` (caught = named cell red), restated control/predicate sentences, receipts
re-produced at the amendment commit. It would fix F1 and the ∃-red attribution weakness (which I
independently observed: undercharge red at W14/W15/W17, nopreamble at W14/W15/W17). It does **not**
mention F2's patch replacement, F3's 1.5/1.25 text, F4's `slow_files` echo/W03 label, F5's load
confound, or F7's KILL. Those four remain to be checked when v2 bytes land; amendment 2 also restates
K1 to bind the counter bytes, which needs a new declared baseline or the byte-identity cross-check
loses its referent. I graded the landed v1 bytes; the v2 plan is not evidence that v2 behaves.

## 8. Residual risk and verification gaps

- No LSP device in this seat; caller/definition conclusions are text-level (no Python importers; the
  counter is invoked only as a script). Semantic cross-file effects are limited to the probe bytes it
  reads with `git show`.
- The passing measured receipt is uncommitted at my observation; I graded the bytes present at
  08:48:40. If L1 commits a different receipt, F4/F5 must be re-checked against it.
- Legacy survival for `undercharge`, `maxmeta`, `nopreamble` is taken from the frozen base-rev
  receipts plus the comment-only base→freeze probe diff; I ran the legacy set myself only for `flat6`
  (`survived=1`). The transfer argument is sound but not independently re-run for the other three.
- Shape B's predicate-mode amplification (W11's second run under the memo, `[INFERENCE]`) was not
  exercised; the natural-pass control receipt is the evidence.
- My own seat's counters ran concurrently with the lane's authoritative measurement and contributed
  to its `load1_nat=89.53`; the measured run's "natural" leg is therefore not independent of this
  review.
- No host packages were installed; no sysctl, jj, or git mutation was performed; the scratch dir
  `/fast/scratch/hyaku/kama-r97/RV02BudgetCells/` is deleted before yield. Fixtures were built only
  in scratch; no tracked lane file was edited.

## 9. Receipt index (out dir)

- `out/RV02BudgetCells/repro-new-controls.out` — new cells, real probe + four shipped mutants, rev
  `e057166e`.
- `out/RV02BudgetCells/legacy-flat6.out` — 13 legacy cells, `flat6`, `survived=1`.
- `out/RV02BudgetCells/shape-all-controls.out` — shapes A and C across all 17 cells.
- `out/RV02BudgetCells/shapeB-fixed-all.out` — corrected memo shape across all 17 cells.
- `out/RV02BudgetCells/step-counts.out` — exact parser steps per probe/fixture.
- `out/RV02BudgetCells/shapes/shapeA-preamble4.sh`, `shapeB-stepmemo.sh`,
  `shapeC-constant7.sh` — the forged probes (single-anchor patches of `git show
  9e605d41:tools/kama-probe.sh`).
