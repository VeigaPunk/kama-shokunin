# EX01Counter — round 99 wave 1 (kama), seat report

Lane repo: `/home/vgpnk/Projects/shokunin/kama-shokunin`
Freeze commit (read-only): `f6e7ccc285e0c1207378f73c394acbfda58bff23` ("round-99 freeze: three
instruments …"). Base: `439fdb3d41b55e5b9e6d7c480d17f2c428bae978`.
Graded bytes verified: `git show f6e7ccc2:tools/round99-router-budget.py | sha256sum` =
`e76c35b449be9a9680af50480a0871317c6ad88a9a87824ec30262c88ad6d246`, identical to the working-tree
file; `git diff --numstat` on both C1 tool files = 0 lines — this seat edited no tracked file.
Grader bytes: `2ba93f8e08f20c8f6575e5d3c89281b5e3e54c193347abe384774ced5b593932`.

Receipts: `.ufo/waves/round-99/w1/out/EX01Counter/` (all raw stdout files quoted below).
Scratch `/fast/scratch/hyaku/kama-r99/EX01Counter/` was deleted at exit; the fixture clone was
created with `git clone --shared` and its toplevel asserted before the first commit
(`TOP=/fast/scratch/hyaku/kama-r99/EX01Counter/fixture`).

## 1. Mandatory runs

### O1 — frozen grader against the frozen counter (expect met=True)

```
python3 tools/round99-control-population.py --repo <lane> --rev f6e7ccc2… \
  --work $S/work --counter tools/round99-router-budget.py
```

```
CONTROL_POP99 counter=tools/round99-router-budget.py drop=W14-900k-nd1 patch_removed=1
selected=6 ran=5 mutant_cells=5 mutant_cells_ok=5 mutant_control_exit=1 mutant_ok=0 refused=1
positive_cells=6 positive_exit=0 positive_ok=1 complete=1 population_shaped=1 met=True
counter_sha256=e76c35b449be9a9680af50480a0871317c6ad88a9a87824ec30262c88ad6d246
rev=f6e7ccc285e0c1207378f73c394acbfda58bff23
exit 0        (ELAPSED 43.29 s, MAXRSS 358680 KB)
```

(Line physically wrapped here for width; it is one line in `step1-grader-r99.txt`.)

`met=True`, `refused=1`, `complete=1` — the predicand holds. `counter_sha256` equals the freeze
commit's byte hash, so the graded bytes are the committed bytes (K1 clean).

### O2 — same grader against the round-98 counter (expect refused=0, met=False, exit 1)

```
python3 tools/round99-control-population.py --repo <lane> --rev 439fdb3d \
  --work $S/work --counter tools/round98-router-budget.py
```

```
CONTROL_POP99 counter=tools/round98-router-budget.py drop=W14-900k-nd1 patch_removed=1
selected=- ran=5 mutant_cells=5 mutant_cells_ok=5 mutant_control_exit=0 mutant_ok=1 refused=0
positive_cells=6 positive_exit=0 positive_ok=1 complete=1 population_shaped=1 met=False
counter_sha256=83d3226f7d213213db0daa4ba08b09160ee1f356a7f12761194b24d311d90398
rev=439fdb3d41b55e5b9e6d7c480d17f2c428bae978
exit 1        (ELAPSED 44.46 s)
```

Exactly the do-nothing control the plan fixes at `plans/round-99-claims.md:63-66`: the predecessor
accepts the dropped population (`mutant_control_exit=0`, `mutant_ok=1`) and the grader refuses to
certify it. The before-measurement exists, so K3 does not fire.

## 2. Predicate-line fidelity — the printed line is not the frozen line

The frozen predicate (`plans/round-99-claims.md:42-44`, mirrored in `claims.json.C1.after` and in
the grader's own docstring, `tools/round99-control-population.py:8-10`) reads

```
… positive_cells=6 positive_exit=0 positive_ok=1 complete=1 met=True
```

The tool actually prints

```
… positive_cells=6 positive_exit=0 positive_ok=1 complete=1 population_shaped=1 met=True
```

`population_shaped` is emitted between `complete` and `met` (`tools/round99-control-population.py:139`).
Consequence: the contiguous substring `complete=1 met=True` that the frozen sentence quotes **does
not occur** in the output; only the field *set* matches. A judge or gate that string-matches the
frozen predicate as written fails this run for a formatting reason. Found by
`grep -n 'population_shaped' tools/round99-control-population.py` → line 139 vs
`sed -n '42,44p' plans/round-99-claims.md`.

Worse, the new token is not evidence of a shape check: `population` is initialised to `1`
(`tools/round99-control-population.py:128`) and only overwritten when the row carries `selected`
or `ran` (line 129). O2's row prints `population_shaped=1` for a predecessor that has no
population terms at all. The token is 1-by-default, not 1-by-check.

## 3. Attack matrix

Method: each attack is a byte patch of `git show f6e7ccc2:tools/round99-router-budget.py` written to
`$S/mut/<name>.py` (never a tracked file), (i) run through its **real** `--control --cells new
--expect survived --mutant none --slow-files 72` path against the lane at the freeze rev, and (ii)
committed as one revision in the scratch fixture clone (`$S/fixture`, `git commit -a`, one mutant per
rev) and handed to the real grader (`--repo $S/fixture --rev <mutant-rev>`). Fixture revs are in
`out/EX01Counter/mutant-revs.txt`.

| # | attack (patch) | counter CONTROL line (trimmed) | exit | check catches? | grader verdict |
|---|---|---|---|---|---|
| 0 | frozen mutation (drop W14 line) — my own run, `direct-z-frozen-drop.txt` | `cells=5 … selected=6 ran=5 population_ok=0 … ok=0` | 1 | **yes** | `refused=1 complete=1 met=True` exit 0 |
| 0b | round-98 predecessor, same drop — my run, `direct-z-r98-drop.txt` | `cells=5 cells_ok=5 … ok=1` | 0 | no (the defect) | `refused=0 met=False` exit 1 |
| a | duplicate the `("W14-900k-nd1", …)` cells entry (7 entries, 6 distinct) | `cells=6 cells_ok=6 selected=6 ran=6 population_ok=1 … ok=1`; **7** `_CELL` lines | 0 | **no** — nothing was lost; `ran` is `len(results)` (distinct keys), so a duplicate run counts once | rc=2 `could-not-evaluate: cell anchor … matched 2 lines` |
| a2 | replace the W19 entry with a second W14 entry (6 entries, 5 distinct ids; W19 lost) | `cells=5 cells_ok=5 selected=6 ran=5 population_ok=0 … ok=0` | 1 | **yes** (count of distinct ids) | rc=2 `anchor … matched 2 lines` |
| b | drop two cells (W14 + W15) | `cells=4 cells_ok=4 selected=6 ran=4 population_ok=0 … ok=0` | 1 | **yes** | rc=2 `anchor … matched 0 lines` |
| c | empty the selection (`NEW_CELLS = set()`), cells list intact | `cells=0 cells_ok=0 selected=0 ran=0 population_ok=1 … ok=1` | 0 | **NO — vacuous `0 == 0`** | `refused=0 population_shaped=0 met=False` exit 1 |
| c2 | shrink selection **and** cells consistently to 5 (drop W14 from both) | `cells=5 cells_ok=5 selected=5 ran=5 population_ok=1 … ok=1` | 0 | **NO** | rc=2 `anchor … matched 0 lines` (declines to evaluate) |
| d | hardcode `population_ok = 1`, drop applied | `cells=5 cells_ok=5 selected=6 ran=5 population_ok=1 … ok=1` | 0 | no (the field is printed, not gated) | `refused=0 met=False` exit 1 |
| e | drop W14 **and** `--expect-cell W14-900k-nd1` | `ROUTER_BUDGET99 could-not-evaluate: --expect-cell W14-900k-nd1 is not in the selected cells` — **no CONTROL line** | 2 | bypassed: no population evidence printed at all | grader never passes `--expect-cell` (`tools/round99-control-population.py:106-108`); if it did, `parse_control`→None ⇒ rc=2 |
| e2 | unmutated + same `--expect-cell` (positive control) | `cells=6 cell_ok=1 … ok=1` | 0 | — | — |
| f | same name count, one cell **replaced** (W14 now probes the 800k fixture expecting `invalid`) | `cells=6 cells_ok=6 selected=6 ran=6 population_ok=1 … ok=1` | 0 | **NO** — identity/content never compared (plan limit (a), confirmed) | on the committed f rev the drop is still a real drop ⇒ `met=True` for the drop; the swap itself was never graded |
| g | print a fabricated short-pass CONTROL line and `return 1` before running any cell (fires only when the drop is present in its own bytes) | forged `cells=5 cells_ok=5 selected=6 ran=5 population_ok=0 … ok=0` — **0 `_CELL` lines, 0.31 s** | 1 | **NO** | **`refused=1 complete=1 population_shaped=1 met=True` exit 0 — ESCAPE** |
| h | keep printing `population_ok` but drop it from the gate (`ok = int(ok)`) | `cells=5 … ran=5 population_ok=0 … ok=1` (grader row: `mutant_control_exit=0 mutant_ok=1 population_shaped=1`) | 0 | no | `refused=0 met=False` exit 1 (caught only by exit status) |
| i | add a phantom name to the selection (`W20-phantom`), cells list untouched | `selected=7 ran=5 population_ok=0 … ok=0` | 1 | yes (fail-closed) | `refused=1 complete=0 met=False` exit 1 — the *complete* term has teeth (blanket refusal is not a gain, K4) |

Key raw lines (full text in `out/EX01Counter/`):

```
# out/direct-z-frozen-drop.txt   (row 0; my run of the frozen one-line drop)   exit 1, 42.9 s
ROUTER_BUDGET99_CONTROL cells=5 cells_ok=5 selected=6 ran=5 population_ok=0 mutant=none slow_files=72 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=rev probe_sha256=40ab387e… rev=f6e7ccc2… ok=0
# identical field-for-field to the committed .ufo/waves/round-99/controls/c1-candidate-mutant.out

# out/direct-z-r98-drop.txt   (row 0b; round-98 bytes at base, same drop)   exit 0, 16.3 s
ROUTER_BUDGET98_CONTROL cells=5 cells_ok=5 mutant=none slow_files=72 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=rev probe_sha256=40ab387e… rev=439fdb3d… ok=1

# out/direct-c-empty-selection.txt      exit 0
ROUTER_BUDGET99_CONTROL cells=0 cells_ok=0 selected=0 ran=0 population_ok=1 mutant=none slow_files=72 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=rev probe_sha256=40ab387e… rev=f6e7ccc2… ok=1

# out/direct-c2.txt                      exit 0
ROUTER_BUDGET99_CONTROL cells=5 cells_ok=5 selected=5 ran=5 population_ok=1 mutant=none slow_files=72 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=rev probe_sha256=40ab387e… rev=f6e7ccc2… ok=1

# out/direct-d-dropped.txt               exit 0
ROUTER_BUDGET99_CONTROL cells=5 cells_ok=5 selected=6 ran=5 population_ok=1 mutant=none slow_files=72 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=rev probe_sha256=40ab387e… rev=f6e7ccc2… ok=1

# out/direct-g-dropped.txt               exit 1, ZERO _CELL lines, 309 ms
ROUTER_BUDGET99_CONTROL cells=5 cells_ok=5 selected=6 ran=5 population_ok=0 mutant=none slow_files=72 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=rev probe_sha256=0 rev=0 ok=0

# out/grader-g-forged-receipt.txt        exit 0
CONTROL_POP99 counter=tools/round99-router-budget.py drop=W14-900k-nd1 patch_removed=1 selected=6 ran=5 mutant_cells=5 mutant_cells_ok=5 mutant_control_exit=1 mutant_ok=0 refused=1 positive_cells=6 positive_exit=0 positive_ok=1 complete=1 population_shaped=1 met=True counter_sha256=94cc9005… rev=9c9899c4…
```

(`40ab387e…` is the probe sha at the freeze rev and matches the committed `controls/c1-positive.out`.)

## 4. Escapes and the limits the plan must disclose

**E1 — the mutant receipt is self-reported (grader-level; the strongest finding).**
`refused` is `int(m_exit != 0)` (`tools/round99-control-population.py:126`) and `population_shaped`
is read from the counter's own CONTROL line (129-132). The grader never inspects the
`ROUTER_BUDGET99_CELL` lines to confirm that the five cells it credits were executed. Attack (g):
a counter that prints `cells=5 cells_ok=5 selected=6 ran=5 population_ok=0 ok=0` and exits 1 without
running anything is certified `met=True` in 0.3 s. The plan's wording asserts the refusal *is* the
population check; the instrument cannot distinguish a real short pass from a fabricated one.
Suggested disclosure (or a follow-up fix): the grader should require the mutant stdout to carry five
distinct `ROUTER_BUDGET99_CELL nat <id>` lines, or the counter should print its executed ids.

**E2 — the check is relative to the selection parsed from the same bytes.**
`want_selected = len(selected)` (`tools/round99-router-budget.py:676`) and `population_ok =
int(n == want_selected)` (line 679). When the selection itself shrinks in the same edit (attacks c and
c2) the comparison is vacuous: `selected=0 ran=0 population_ok=1 ok=1`, exit 0 with zero cells run.
The only backstop is the grader's hardcoded `SELECTED = 6`
(`tools/round99-control-population.py:41`), and that is a *count*, not the frozen six ids — a
selection of six different runnable names would also print `selected=6`. Disclosure: "the check
proves every *selected* cell ran; it does not prove the selection is the frozen six."

**E3 — `ran` is the number of distinct result keys, not executions.**
`natural` is a dict keyed by cell id (`tools/round99-router-budget.py:545-557`). Attack (a) executes
seven probe invocations (seven `_CELL` lines) and reports `ran=6`. A duplicated entry is invisible.

**E4 — identity and content are never compared.** Confirmed by (f): a counter whose W14 entry
probes a different fixture and expects a different verdict still prints `ran=6 population_ok=1 ok=1`,
exit 0. This is disclosed as limit (a) but the disclosure says "a cell replaced by a different cell of
the same name count passes"; the experiment shows it is stronger — *any* content change passes,
including one that silently removes the 900k fixture from coverage.

**E5 — `--expect-cell` on a cell that was not run yields no receipt.** Attack (e): exit 2 with
`could-not-evaluate` and **no CONTROL line**, so `parse_control` returns `None` and the grader can
only say `could-not-evaluate` (rc=2). Non-green, but a control that failed to run its population
publishes no population evidence. Cheap fix: emit the CONTROL line with `ok=0` before returning 2, or
print `selected/ran/population_ok` on that path.

**E6 — the grader can only evaluate exactly one drop.** `patch_drop` requires the anchor exactly once
(`tools/round99-control-population.py:60-63`), so a counter that already lost (b, c2: 0 matches) or
duplicated (a, a2: 2 matches) the W14 entry returns rc=2 could-not-evaluate. Fail-closed, but it
means the instrument distinguishes neither "the counter dropped the cell" nor "the counter duplicated
it": the mutation is one-shot and must be applied to pristine bytes.

**E7 — the vocabulary token is misleading (see §2).** `population_shaped=1` appears on a row with no
population terms.

## 5. Timing / is a `--cells all` run needed?

- Grader end-to-end (mutant pass + positive pass), idle host: **43.29 s** (O1) and **44.46 s** (O2).
- Single new-set control pass ≈ 18–21 s: fixture build of six GGUFs plus six probe calls; per-cell
  probe times from `out/direct-e2-expect-cell-present.txt`: W14 3.14 s, W15 3.00 s, W16 0.25 s,
  W17 3.13 s, W18 3.17 s, W19 2.83 s (15.5 s of probe time). Under host contention the same pass
  took 60–112 s (five concurrent runs in this wave), so a timeout of 900 s
  (`--timeout` default) is adequate but not generous.
- **No `--cells all` run is needed for C1.** The grader hardcodes `--cells new`
  (`tools/round99-control-population.py:106-108`), the frozen mutation is a loss of a selected cell in
  the six-cell `new` set, and the 19-cell natural pass is C3's regression control at M3
  (`plans/round-99-claims.md:156-158`). By inspection the same count rule generalises:
  `--cells all` ⇒ `want_selected = CELLS = 19` (`tools/round99-router-budget.py:170,676`), so a
  20th list entry without a `CELLS` bump would refuse — fail-closed, but untested by C1. Plan limit
  (b) ("only the six-cell `new` set is exercised") is accurate and I did not run `all`/`legacy`/
  `r97set` (they would add 72 slow fixtures and many minutes of probe time for no additional
  discrimination on this predicate).

## 6. Cited defects (file:line + the command that shows it)

1. Predicate line / output disagreement — `plans/round-99-claims.md:44` and
   `tools/round99-control-population.py:8-10` vs `tools/round99-control-population.py:139`;
   shown by `step1-grader-r99.txt`. Operability/calibration.
2. `population_shaped` defaults to 1 without a shape check —
   `tools/round99-control-population.py:128-132`; shown by `step2-grader-r98.txt`
   (`population_shaped=1` beside `selected=-`).
3. Refusal is exit-status-only; no execution cross-check —
   `tools/round99-control-population.py:126-133`; shown by `grader-g-forged-receipt.txt`
   (`met=True`, 0 `_CELL` lines in `direct-g-dropped.txt`).
4. Population check self-referential to the same file's selection —
   `tools/round99-router-budget.py:676-679,694`; shown by `direct-c-empty-selection.txt`
   and `direct-c2.txt` (`population_ok=1`, exit 0).
5. `ran` = distinct result keys — `tools/round99-router-budget.py:545-557`;
   shown by `direct-a-dup-cell.txt` (7 `_CELL` lines, `ran=6`).
6. Anchor-uniqueness makes the grader blind to a counter that already lost the cell —
   `tools/round99-control-population.py:60-63`; shown by `grader-b-drop-two.txt`,
   `grader-c2.txt` (rc=2).

## 7. Verdict for the parent

- **C1 operability holds for the frozen predicate as an exit-status fact:** O1 reproduces the claimed
  `met=True`/exit 0 at the freeze commit with the freeze bytes; O2 reproduces the round-98 acceptance
  (`refused=0 met=False` exit 1). The dropped-cell mutation is refused by the successor and accepted
  by the predecessor, and the unmodified successor accepts a complete population
  (`positive_exit=0 positive_ok=1 complete=1`, plus the direct `cells=6 ok=1` run).
- **It does not hold as heavily as the plan's wording suggests.** The receipt is self-reported (E1),
  the check is set-relative rather than frozen-set-relative (E2/E3), and the printed predicate line
  is not the frozen predicate line (§2). At minimum the plan needs the E1/E2 disclosures; the
  `population_shaped` token and the predicate string should be reconciled before the measurement-time
  receipt is committed, or a judge matching the frozen line literally will read a mismatch.
- No kill rule fires: K1 — graded bytes = freeze bytes (`counter_sha256` matches, `git diff` clean);
  K2 — `met=True` at M1; K3 — the predecessor accepts (before-measurement exists); K4 — the pristine
  counter accepts a complete population (i shows the opposite direction is refused and caught).

## 8. Risks / blockers / tooling

- Host contention in this wave made per-pass wall time swing 18 s → 112 s; any M1 re-run's
  `w03_seconds`-independent control path is unaffected (control mode returns before the load pass and
  before `start_burners`), but the 900 s grader timeout should not be lowered.
- No package or tool was installed; no pacman call; no host service touched; no sysctl.
  Nothing is missing for a re-run (`python3` 3.x stdlib only, `git`, `bash`).
- Scratch `$S` (677 MB) was removed before yield; only the receipts in
  `.ufo/waves/round-99/w1/out/EX01Counter/` remain. No tracked lane file, lane jj state or Git index
  was touched; the fixture clone lived entirely under `/fast/scratch/…`.
