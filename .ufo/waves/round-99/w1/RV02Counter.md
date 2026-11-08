# RV02Counter — adversarial review of C1 (operability): the population guard

Seat: RV02Counter (leaf). Lane: `kama`. Round 99, wave 1.
Base `439fdb3d41b55e5b9e6d7c480d17f2c428bae978`; M1 (graded) `f6e7ccc285e0c1207378f73c394acbfda58bff23`.
Read: `plans/round-99-claims.md` C1, `tools/round99-control-population.py` (145 ln), the control
branch of `tools/round99-router-budget.py`, `tools/round98-router-budget.py` (predecessor).
No tracked file was edited; every mutation lives in scratch copies. Receipts in
`.ufo/waves/round-99/w1/out/RV02Counter/` (`run-*.out`, each holding the full command output).

All commands below were run as written. `L=/home/vgpnk/Projects/shokunin/kama-shokunin`,
`S=/fast/scratch/hyaku/kama-r99/RV02Counter`, counter bytes from `git show f6e7ccc2:tools/round99-router-budget.py`
(sha256 `e76c35b4…d246`, identical to the working-tree file and to `measured/c1.out`).

## Verdict

The claim's core predicate **reproduces exactly** at M1: the grader refuses the frozen one-line
drop and accepts the unmodified complete population.

```
$ python3 tools/round99-control-population.py --repo "$L" --rev f6e7ccc2 --work $S/w-gm1
CONTROL_POP99 counter=tools/round99-router-budget.py drop=W14-900k-nd1 patch_removed=1 selected=6 ran=5 mutant_cells=5 mutant_cells_ok=5 mutant_control_exit=1 mutant_ok=0 refused=1 positive_cells=6 positive_exit=0 positive_ok=1 complete=1 population_shaped=1 met=True counter_sha256=e76c35b449be9a9680af50480a0871317c6ad88a9a87824ec30262c88ad6d246 rev=f6e7ccc285e0c1207378f73c394acbfda58bff23
exit=0
```

The do-nothing arm also reproduces (`run-grader-base.out`, exit 1):

```
$ python3 tools/round99-control-population.py --repo "$L" --rev 439fdb3d --work $S/w-gbase --counter tools/round98-router-budget.py
CONTROL_POP99 counter=tools/round98-router-budget.py drop=W14-900k-nd1 patch_removed=1 selected=- ran=5 mutant_cells=5 mutant_cells_ok=5 mutant_control_exit=0 mutant_ok=1 refused=0 positive_cells=6 positive_exit=0 positive_ok=1 complete=1 population_shaped=1 met=False counter_sha256=83d3226f… rev=439fdb3d41b55e5b9e6d7c480d17f2c428bae978
```

and the counter-level before-arm (`run-r98drop.out`, exit 0): `ROUTER_BUDGET98_CONTROL cells=5
cells_ok=5 … survived=1 ok=1`.

What the claim does **not** hold: the guard is an equality on the *count* of executed cells
(`tools/round99-router-budget.py:676,679` — `want_selected = … len(selected)`;
`population_ok = int(n == want_selected)`), not on cell identity. Three same-count or vacuous
constructions pass with `population_ok=1 ok=1` exit 0 (rows 4, 5, 7, 9, 10 below). The plan's
limit (a) discloses the principle, so no hidden overclaim survives on the *property*; but the
headline sentence ("refuses a selected population it did not run") is wider than what is measured,
and limit (a)'s wording is ungrammatical and does not name the `--cells all` form, which needs no
id rename at all. Two receipt labels overstate: `population_shaped=1` is printed for a counter with
no population check, and `complete=1` means only "exit 0, ok=1", not "ran the 6 selected cells".

## Catch/escape matrix

| # | construction (scratch copy) | command tail | counter result | exit | caught? |
|---|---|---|---|---|---|
| 1 | exactly the grader's one-line drop | `m_drop.py … --control --cells new --expect survived --mutant none` | `cells=5 cells_ok=5 selected=6 ran=5 population_ok=0 … ok=0` | 1 | **caught** (refused=1, met=True) |
| 2 | duplicate a W15 tuple, no drop | `m_dup.py …` | `cells=6 cells_ok=6 selected=6 ran=6 population_ok=1 … ok=1` (W15 runs twice; `results[cid]` collapses) | 0 | not an escape: all six ids are still executed |
| 3 | drop W14 + duplicate W15 (mask the drop) | `m_dupmask.py …` | `cells=5 cells_ok=5 selected=6 ran=5 population_ok=0 … ok=0` | 1 | **caught** (5 unique ids) |
| 4 | rename id `W14-900k-nd1`→`W14-900k-nd1X` in `NEW_CELLS`, `R97_CELLS`, cells list | `m_rename.py …` | `cells=6 cells_ok=6 selected=6 ran=6 population_ok=1 … ok=1` | 0 | **ESCAPE** — same count, different id |
| 5 | replace W14's `[[exe,"-m",t900k]]` with `[[exe,"-m",mid4]]`, same id, same expectation | `m_swap.py …` | `cells=6 cells_ok=6 selected=6 ran=6 population_ok=1 … ok=1` | 0 | **ESCAPE** — the 900 k-tensor/nd=1 boundary is no longer graded at all |
| 6 | `--cells all`, drop W14 (`--slow-files 8`) | `m_drop.py … --cells all` | `cells=18 cells_ok=18 selected=19 ran=18 population_ok=0 … ok=0` | 1 | **caught** |
| 7 | `--cells all`, drop W14 + inject `("W20-injected", [[exe,"-m",ok]], "MODEL_OK", …)` (19 entries) | `m_drop_inject.py … --cells all` | `cells=19 cells_ok=19 selected=19 ran=19 population_ok=1 … ok=1` | 0 | **ESCAPE** — `selected is None` under `all`, so the guard has no membership set at all |
| 8 | `--cells all`, inject W20 only (20 entries, complete by list) | `m_inject.py … --cells all` | `cells=20 cells_ok=20 selected=19 ran=20 population_ok=0 … ok=0` | 1 | refused; the guard is count *equality*, so an over-full list is refused too |
| 9 | coordinated shrink: drop the W14 tuple **and** its `NEW_CELLS` member | `m_shrink.py …` | `cells=5 cells_ok=5 selected=5 ran=5 population_ok=1 … ok=1` | 0 | **ESCAPE from the counter** (only the printed `selected=5` reveals it). The grader cannot grade this copy at all: its anchor is gone, `patch_drop` → 0 hits → `could-not-evaluate` exit 2 |
| 10 | `NEW_CELLS = set()` | `m_emptyset.py …` | `cells=0 cells_ok=0 selected=0 ran=0 population_ok=1 … ok=1` | 0 | **ESCAPE** — vacuous: nothing selected, nothing run, "complete" |
| 11 | raise after `results[cid] = …` for W15 | `m_raise.py …` | two `ROUTER_BUDGET99_CELL` lines, `RuntimeError: boom-after-append`, **no CONTROL line** | 1 | not an escape: no control line → grader `m_row is None` → `could-not-evaluate` exit 2 (traced by code read; the 0-hit path is demonstrated by row 13) |
| 12 | `--expect-cell W14-900k-nd1` on the dropped copy | `m_drop.py … --expect-cell W14-900k-nd1` | `ROUTER_BUDGET99 could-not-evaluate: --expect-cell W14-900k-nd1 is not in the selected cells`, no CONTROL line | 2 | fail-closed, but a *different* diagnosis: `population_ok` was computed (line 679) and is never printed on this path |
| 13 | whitespace-altered anchor (`( "W14-900k-nd1",`) committed in a `git clone --shared` fixture, through the grader | `round99-control-population.py --repo $D --rev HEAD --counter tools/round99-router-budget.py` | `CONTROL_POP99 could-not-evaluate: cell anchor 'W14-900k-nd1' matched 0 lines (need exactly 1)` | 2 | fail-closed |
| 14 | tab-indented anchor | `patch_drop(m_indent, …)` via import | `patch_removed=1` | — | anchor tolerates any leading whitespace (`lstrip()`, line 60) |
| 15 | duplicate anchor line | `round99-control-population.py`/`patch_drop` | `… matched 2 lines (need exactly 1)` | 2 | fail-closed |
| 16 | `--mutant overcharge` on the new set, `--expect caught` | `counter-r99.py … --expect caught --mutant overcharge` | `cells=6 cells_ok=4 … survived=0 caught=1 … ok=1` (W18, W19 redden) | 0 | **caught as designed**; with `--expect survived` the same run is `ok=0` exit 1 |
| 17 | `--control --expect caught --mutant none` | `counter-r99.py …` | `ROUTER_BUDGET99 usage: --control requires --expect and, for 'caught', a --mutant` | 64 | fail-closed |

Anchor uniqueness check (both counter files, `lstrip().startswith('("W14-900k-nd1",')`):
`tools/round99-router-budget.py:517` — 1 hit; `tools/round98-router-budget.py:499` — 1 hit.
The grader reads committed bytes only: `src = git("show", f"{rev}:{a.counter}")` at
`tools/round99-control-population.py:88`; there is no `--tree`/worktree alternative (unlike C2).

Which arms the claim requires: `complete` requires **only** the unmodified counter with
`--control --cells new --expect survived --mutant none`, one run (`runs=1`), exit 0 and `ok=1`
(grader `:127`). It does not require any mutant arm, and `--mutant overcharge` is not part of the
predicate. `refused` requires only `m_exit != 0` (`:126`) plus, when the mutant row carries the
tokens, `selected=6 ran=5 population_ok=0` (`:128-132`).

## Findings by severity

### F1 (medium) — the frozen predicate line is not a literal substring of the receipt

`plans/round-99-claims.md` C1 prints (one line, wrapped across three)

```
CONTROL_POP99 counter=tools/round99-router-budget.py drop=W14-900k-nd1 patch_removed=1 selected=6
ran=5 mutant_cells=5 mutant_cells_ok=5 mutant_control_exit=1 mutant_ok=0 refused=1 positive_cells=6
positive_exit=0 positive_ok=1 complete=1 met=True
```

but `measured/c1.out` (and a live run, `run-grader-m1.out`) reads `… complete=1 population_shaped=1
met=True counter_sha256=… rev=…`. Checked mechanically: `plan in receipt → False`; the plan's 15
`k=v` tokens are all present with the same values in the same order (subsequence holds); 3 extra
tokens are interleaved/trailing (`population_shaped=1`, `counter_sha256=…`, `rev=…`). The grader's
docstring (`tools/round99-control-population.py:7-10`) is a *third* text: it omits
`mutant_cells=…`, `mutant_cells_ok=…` and `positive_cells=…` that the plan carries, so the plan's
"same in the grader's docstring and in the receipt label" is false as text (true token-wise).
Consequence: a verifier doing `grep -F '<predicate line>'` on the receipt gets a miss on a claim
that is in fact met.

Since the predicate is frozen and cannot be edited this wave, the round record/report must add:

> Predicate matching is token-wise: every `k=v` in the predicate line appears in the printed line,
> in the same order, with the same value; the printed line may carry additional tokens
> (`population_shaped`, `counter_sha256`, `rev`), and the grader docstring omits
> `mutant_cells`/`mutant_cells_ok`/`positive_cells`.

### F2 (medium) — a same-count substitution passes: the guard counts, it does not bind identity

Limit (a) says "The check compares counts, not cell identity: a cell replaced by a different cell of
the same name count passes." Both halves are now constructed:

* `m_swap.py` — W14 keeps its id, expectation and position but grades `mid4` instead of `t900k`
  (`tools/round99-router-budget.py:517`): `cells=6 cells_ok=6 selected=6 ran=6 population_ok=1 ok=1`,
  exit 0. The 900 k-tensor / nd=1 cell the round added is silently no longer exercised, and every
  printed number says the population is complete.
* `m_rename.py` — id renamed in `NEW_CELLS`, `R97_CELLS` and the list: green, exit 0.
* `m_drop_inject.py` under `--cells all` — W14 dropped, `W20-injected` added: `cells=19 cells_ok=19
  selected=19 ran=19 population_ok=1 ok=1`, exit 0. Under `all`, `selected is None` so there is no
  membership set anywhere; the only anchor is the constant `CELLS = 19`
  (`tools/round99-router-budget.py:170,676`). This form is *not* covered by the plan's restriction
  of C1 to the `new` set in a way a reader would notice, because limit (b) only says the 17-cell
  set keeps "the same count rule".

The escape is real at counter level and disclosed in principle. What the report must add (repairing
limit (a), which the freeze forbids editing in place):

> The population guard is a count guard: it refuses a control run that executes fewer cells than the
> selected set, and does not bind cell identity — a same-count substitution (a renamed id, a swapped
> fixture under the same id, or, under `--cells all`, a drop compensated by an injected 20th cell)
> passes with `population_ok=1`, and a coordinated two-line shrink of both the cells list and
> `NEW_CELLS` reads `selected=5 ran=5 population_ok=1 ok=1` and exits 0, which only the grader's
> frozen `selected=6` catches.

A one-line hardening for a future round: `population_ok = int(set(natural) == (set(selected) if
selected is not None else set(c for c, *_ in cells_list)))`, i.e. compare id sets, and refuse
`want_selected == 0`.

### F3 (low-medium) — `population_shaped=1` is printed for a counter with no population check

`tools/round99-control-population.py:128` initialises `population = 1` and only *overwrites* it
when the mutant row carries `selected=`/`ran=` (`:129-132`). The base arm therefore prints
`selected=- ran=5 … population_shaped=1 met=False` (`run-grader-base.out`): the label asserts a
shape the round-98 counter does not have. `met` stays False only because `refused=0`. This is the
plan's own named failure class (a property narrower than the label) in miniature, on the grader's
side. Hardening (post-freeze): default `population = 0`, or rename the token to
`population_tokens=0|1` and derive a separate `population_bound`. The verdicts do not change:
base `met=False` either way.

### F4 (low) — a vacuous selection is "complete"

`NEW_CELLS = set()` → `cells=0 cells_ok=0 selected=0 ran=0 population_ok=1 survived=1 ok=1`, exit 0
(`run-emptyset.out`). Nothing was selected, nothing ran, and the counter calls it complete. The
grader's `complete=1` (`:127`) would also report 1 for such a positive (it checks only exit 0 and
`ok=1`), i.e. `complete` does not witness "ran the 6 selected cells". The claim is not defeated at
M1 because the frozen bytes print `positive_cells=6`, but the criterion is narrower than the word.
Hardening: `complete` should require `p_row.get("selected") == "6" and p_row.get("ran") == "6"`, and
the counter should refuse `want_selected == 0`.

### F5 (low) — `refused` is exit-only and the grader trusts a default

`refused = int(m_exit != 0)` (`:126`): any nonzero exit counts, including exit 2 from a counter that
cannot evaluate. With the frozen one-line drop the mutant always either prints the count line
(population_ok=0) or no line at all (→ `could-not-evaluate`, exit 2, not met), so no escape exists
against the graded bytes. But `met` would accept a counter that prints a tokenless control line and
exits nonzero for a reason unrelated to the population. Hardening: `refused = int(m_exit != 0 and
m_row is not None and (m_row.get("ok") == "0"))`.

### F6 (low) — a receipt that cannot fasten its own grader bytes

`measured/c1.out` pins the counter (`counter_sha256=e76c35b4…`, equal to
`git show f6e7ccc2:tools/round99-router-budget.py`), but nothing in the printed line identifies the
grader that produced it. K1's "the graded grader bytes change after the freeze commit" is checkable
only by resolving M1 out-of-band. A `grader_sha256=` token (or a command echo) would make the
receipt self-fastening.

### F7 (info) — `--expect-cell` on a dropped cell reports the wrong arm

`tools/round99-router-budget.py:684-689`: the absence check runs *after* `population_ok` is computed
(`:679`) and returns 2 without printing the control line, so a population-short run asked to grade a
specific cell reports only "not in the selected cells". Fail-closed and correct diagnosis for
`--expect-cell`; recorded because the grader would also report `could-not-evaluate` (2) rather than
`refused=1` for that invocation.

## What I could not make fail (and why that matters)

* No false red of the **unmodified** counter: 6/6 green in 19.8 s wall, per cell dt 0.14 s (W16) to
  2.80 s (W15), `maxrss` 350 MB (`run-pos.out`). The positive arm is a single run (`runs=1`,
  no retry).
* The overcharge mutant is caught, never "complete": W18 and W19 flip to `MODEL_OK` → `cells_ok=4
  survived=0 caught=1`; `--expect caught` prints `ok=1` exit 0, `--expect survived` prints `ok=0`
  exit 1.
* The anchor is unique in both counters and every non-exact form is fail-closed (rows 13–15).

## Residual risk and verification gaps

1. **Host-load timing path (the `complete` arm's only soft spot).** The three `MODEL_UNLOADED` cells
   (W16/W18/W19) depend on the probe's pass not being truncated: `tools/kama-probe.sh` (M1) sets
   `limit=$((20 + 25 * npaths))` (≈45 s for one path) at `:874`; a truncation leaves the candidate
   `-` → loadable → `MODEL_OK` → cell red → `survived=0` → `complete=0` → `met=False`. Measured
   headroom is ~19× (2.3 s vs 45 s), so only a severe host stall can flip it. **I did not run a
   load test** (deliberate: a CPU burner would disturb the sibling seats' timed runs); this is the
   one arm I can only bound analytically.
2. **Disk/large fixtures.** Each control run builds a 160 MiB `maxmeta` file plus 900 k / 833 k
   tensor fixtures (`MAXMETA_BYTES = 160 * 1024 ** 2`); ~350 MB RSS. A full `/fast` or ENOSPC makes
   the positive arm exit nonzero with no control line → `could-not-evaluate` (2), not a false red,
   but the claim becomes unmeasurable.
3. **Grader timeout vs counter kill.** Grader `--timeout 900` per invocation vs counter `KILL = 3600`;
   a slow cell sequence is graded `could-not-evaluate` (2) rather than by the population criterion.
4. **Not re-run (declared limits).** The `--cells all` natural 19-cell pass (limit e) and the
   17-cell `r97set` arm (limit b; its count derives as 16 list entries + the separately-handled
   `W10-rewrite` = 17, read from `:561-590`, not executed). The 2-line-shrink copy's grader outcome
   is code-derived (anchor 0 hits → exit 2); that path is demonstrated by row 13.
5. **Environment.** `pty` was unavailable in this seat's shell; every command ran non-interactive
   with the same argv as the advertised predicates. Fixture repo: `git clone --shared` under scratch,
   `git rev-parse --show-toplevel` asserted equal to the fixture before the one commit
   (`791d3f24`, whitespace-altered anchor).

## Appendix — byte-exact recipes for the escape rows

All applied to `git show f6e7ccc2:tools/round99-router-budget.py` (sha256 `e76c35b4…d246`) in
scratch; none to a tracked file. Invocation for every row: `python3 <copy> --repo "$L" --rev
f6e7ccc2 --work <fresh> --slow-files 72 --control --cells new --expect survived --mutant none`
(`--slow-files 8 --cells all` for rows 6–8).

* row 4, rename: replace the 3 occurrences of `"W14-900k-nd1"` (lines 174 `NEW_CELLS`, 176
  `R97_CELLS`, 517 cells list) with `"W14-900k-nd1X"`.
* row 5, swap: line 517 `[[exe, "-m", t900k]]` → `[[exe, "-m", mid4]]` (id, expectation, position
  unchanged).
* row 7, `all` drop+inject: delete line 517; insert after line 522
  `        ("W20-injected", [[exe, "-m", ok]], "MODEL_OK", "router-unloaded-autoload"),`.
* row 9, shrink: delete line 517; in `NEW_CELLS` (line 174) remove `"W14-900k-nd1", ` so
  `R97_CELLS` alone keeps the id.
* row 10, vacuous: replace the `NEW_CELLS = {…}` statement (lines 174–175) with `NEW_CELLS = set()`.
* row 11, raise: after line 558 `        results[cid] = (good, verdicts, wv, wr)` insert
  `        if cid == "W15-700k-nd4":` / `            raise RuntimeError("boom-after-append")`.

## Tooling and scratch

No tool was installed or upgraded. Scratch `/fast/scratch/hyaku/kama-r99/RV02Counter/` was created
for this seat; receipts were copied to
`.ufo/waves/round-99/w1/out/RV02Counter/` (`run-*.out`, 20 files, 80 KB) and the scratch tree was
removed before yield. No tracked lane file, lane Git index, jj state, fleet file, sysctl, host
service or non-owned process was touched.
