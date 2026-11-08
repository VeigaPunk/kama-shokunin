# MT01Mutants — mutation test of the two round-100 frozen counters

**Axes**: calibration (C1) + depth (C2). **Method**: single-point mutants of the frozen
counters in scratch copies only; each mutant run against pristine M (`2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6`,
should stay `met=True`) and against the committed control sets. A mutant whose every
control's `(rc, met)` matches pristine is a **survivor** (or **equivalent** where behavior
is provably identical). No tracked lane file was edited; see §Restoration.

## Pristine baselines (reproduced)

- C1 pristine at M: `RECORD_AUDIT100 checks=9 mismatches=0 met=True rev=2e27e6f1…
  …` rc=0 (`logs/pristine-vs-M.txt`, `logs/c1-runs.txt` header).
  At base `6776c667…`: `checks=9 mismatches=9 met=False` rc=1.
- C1 pristine forgery set: `C1_FORGERIES cases=8 wrong=0 met=True`
  (`logs/c1-forgeries-runs.txt` header; matches committed `controls/c1-forgeries.out`).
- C2 pristine at M: `ROUTER_PROPS_STATUS100 cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True …` rc=0.
  At base: `cells=9 mismatches=6 base_mismatches=6 flips=0 stable=9 met=False` rc=1
  (reproduces `measured/c2.out` and `controls/c2-base.out`).
- Blanket control: I did **not** have the frozen blanket probe bytes, so I rebuilt a
  blanket-refusal probe (`work/probe-blanket.sh` = M probe with `return 2` at the top of
  `router_autoload()`, same refusal *behavior* as `controls/c2-mutant-blanket.out`:
  pristine against it prints `mismatches=2 … met=False`, rc=1 with P1+P2 failing) and
  graded every C2 mutant through it with `--probe-file`. The rebuilt probe's sha256
  differs from the frozen blanket's (`ceb9279f…` vs `4e6a4214…` in the receipt) — the
  refusal patch text is not byte-identical, but cell-by-cell verdicts match the receipt.
  This limit is recorded here rather than silently assumed away.
  (`logs/c2-controls.txt`.) Pristine @BLANKET: `… mismatches=2 base_mismatches=6
  flips=8 stable=1 met=False … candidate=yes` rc=1 — same shape as `c2-mutant-blanket.out`.

- Working tree vs M for the three files I used to build custom probes (`SCORECARD.md`,
  `LOG.md`, `.ufo/waves/round-100/r99-measured.json`): byte-identical to M
  (`git show 2e27e6f1:<f>` vs lane working tree), so the probe scaffold (BASE checkout +
  those three files) is a faithful M replica. Custom probe commits are listed in
  `out/MT01Mutants/probes/revs.txt`.

## C1 — tools/round100-record-audit.py (8 mutants)

Pristine sha256 `6fcc628e…4386` (`tools/round100-record-audit.py`); all mutants in
`out/MT01Mutants/mutants_c1/`. Every mutant stayed green at M (except the two that change
the printed DERIVED line, which still print `met=True`): `logs/c1-runs.txt`.

| Mutant (file:line) | Change | @M | vs forgery set (P0+F1–F7) | Verdict |
|---|---|---|---|---|
| C1M1 `round100-record-audit.py:140` | check-5 stray-% loop `PCT_RE.findall(stripped)` → `[]` | green | **KILLED by F1** (`logs/c1-forgeries-runs.txt`: `C1M1` F1 `rc=0 want=1 ok=0`, `C1_FORGERIES … wrong=1`) | killed |
| C1M2 `:154` | `len(bound) >= 3` → `>= 0` (check 7) | green | **SURVIVES F1–F7** (`… wrong=0 met=True`) | **survivor — equivalent under exit-code grading** (see below) |
| C1M3 `:64` | `BOUND_RE` phrase `+"` → `*` (empty phrase allowed) | green | **SURVIVES F1–F7** (`… wrong=0 met=True`). Note F7 uses `" "` (a space), which matches `[^"]+` anyway, so it never exercised `+` vs `*`; its kill comes from check 8's `phrase.strip() != ""` at `:162`. | **survivor** |
| C1M4 `:101` | `frac` renders `N of T` without the `(P%)` part (count-only) | green (DERIVED shows `'4 of 12'`) | **SURVIVES F1–F7** (`… wrong=0`). F5 changes the *count* (`7 of 12`), so it kills pristine via check 3/4 there and M4 via check 5 — both rc=1. | **survivor** |
| C1M5 `:175` | drop `and preds[c][1] == "exit=0"` from check 9 | green | **SURVIVES F1–F7** (`… wrong=0`). F4 edits a predicate *line* (byte-equality kills both). No committed control flips only an `exit=` line. | **survivor** |
| C1M6 `:118` | heading `ln.startswith(HEADING)` → `HEADING in ln` (substring anywhere) | green | **SURVIVES F1–F7** (`… wrong=0`) | **survivor** |
| C1M7 `:151` | check-7 `ANY_PTR_RE.finditer(stripped)` → `[]` (drop unbound scan) | green | **KILLED by F2** (`logs/c1m7-forgeries.txt`: `C1M7` F2 `rc=0 want=1 ok=0 … wrong=1`) | killed |
| C1M8 `:101` | `round(100n/T)` → `int(100n/T)` | green | **SURVIVES F1–F7** (`logs/c1-m8-base.txt`: `… wrong=0 met=True`) | **equivalent mutant** (see below) |

Full per-case verdicts: `logs/c1-forgeries-runs.txt` (pristine, C1M1–C1M6),
`logs/c1-m8-base.txt` (C1M8), `logs/c1m7-forgeries.txt` (C1M7 re-run to completion).
The first C1 batch hit the 300 s tool timeout mid-C1M7 (F6); C1M7 was re-run in full
(the re-run line above is complete: `cases=8 wrong=1 met=False`).

### Custom isolation probes for the C1 survivors (scratch commits; revs in `out/MT01Mutants/probes/revs.txt`)

Each probe applies one forgery to the M replica and runs pristine vs all 8 mutants:

- **G2/G3 — bound < 3** (keep 2 / 0 bound pointers, everything else clean):
  pristine `rc=1 check7,check8`; C1M2 `rc=1 check8` only. So check 8's
  `len(bound) >= 3 and resolved == len(bound)` (`:167`) already enforces the ≥3 floor;
  the `>= 3` inside check 7 is **dead logic** — **C1M2 is a verdict-equivalent mutant**.
  It is only distinguishable by pinning *which* checks fire (a control asserting check 7
  must be listed). No exit-code control can kill it.
- **P-empty — `("")` true-empty phrase** (what F7 should have used):
  pristine `rc=1 check7` (an empty phrase doesn't match `BOUND_RE`, so `ANY_PTR_RE` counts
  it unbound); C1M3 `rc=1 check8` (it counts as bound, then fails resolution). Same exit
  code — **C1M3 is exit-code-equivalent**; a control keyed on the *mismatch set* (check 7
  must fire for a `("")` forgery) kills it. **The control that would kill it is F7 with
  `("")` instead of `(" ")`.**
- **G5c — only the `exit=0` line → `exit=1`, predicate lines byte-intact** (the control
  F4 was meant to be): pristine `rc=1 check9`; **C1M5 `rc=0` — killed.** Control that
  kills C1M5: a forgery flipping only an exit line. (Two earlier attempts, G5/G5b, also
  corrupted a predicate line via the `positive_exit=` token — those first two lines
  document the probe bug and its fix; G5c is the clean run.)
- **G6 — decoy `See also ## Round 100 correction …` line inside the block:**
  pristine `rc=0`; **C1M6 `rc=1 check1,check3,check5,check6,check7` — killed.** Control
  that kills C1M6: a block containing the heading text as a mid-line substring.
- **G9 — `4 of 12` without the `(33%)` part** (count right, percentage absent — the exact
  ambiguity the claim wording covers but F5 doesn't):
  pristine `rc=1 check4`; **C1M4 `rc=0` — killed.** Control that kills C1M4: a
  percentage-less count forgery. (G8 `(57%)` also separates the *check-5* path but both
  mutants still exit 1 there, so G9 is the clean killer.)
- **C1M8 — `round()` → `int()`:** equivalent on this data: `round(100·4/12)=33=int(…)`
  and `round(100·6/12)=50=int(…)` (verified analytically in §Build notes). No control on
  4/12, 6/12 can kill it.
  **The control that would kill it:** a spec/results pair whose percentage lands on a
  `.5` boundary, e.g. total `T=8`, `n=3` → `37.5`: `round→38`, `int→37`. Nothing in the
  committed set has such a denominator, so this is a coverage gap in the *data* the check
  is derived from, not in the forgery edits.

## C2 — tools/round100-props-status.py (8 mutants)

Pristine sha256 `ce2f0641…05e2` (`tools/round100-props-status.py`); all mutants in
`out/MT01Mutants/mutants_c2/`; logs `logs/c2-runs.txt` (@M), `logs/c2-mutant-controls.txt`
(@BASE + @BLANKET `logs/c2-controls.txt`). Note `met = (mismatches == 0)` at `:211` —
`cells`, `base_mismatches`, `flips`, `stable` are printed but never gated, so output-text
differences alone don't change `met`/exit.

| Mutant (file:line) | Change | @M | @BASE / @BLANKET | Verdict |
|---|---|---|---|---|
| C2M1 `:74` | drop S1-401-router-off cell | `cells=8 mismatches=0 met=True` rc=0 | BASE `cells=8 … met=False` rc=1; BLANKET `cells=8 mismatches=2 … met=False` rc=1 | **survivor of committed controls** on `(rc,met)` (`cells=9` never gated). Killed only by a control pinning `cells=9` in the printed line — the claim's predicate sentence states `cells=9`, the counter's `met` does not. |
| C2M2 `:74` | S1 want `UNREAD` → `OFF` | `mismatches=1 met=False` rc=1 | rc=1 / rc=1 | killed by M itself |
| C2M3 `:200` | ignore exit in comparison (`got = …[:2]+(2,)`) | `mismatches=1 met=False` (P2) rc=1 | BASE `mismatches=7` rc=1; BLANKET `mismatches=2` rc=1 | killed by M itself (P2 wants exit 0) |
| C2M4 `:201` | compare verdict only (`got[0] != want[0]`) | **green** `cells=9 mismatches=0 met=True` rc=0 | BASE `mismatches=4 met=False` rc=1; BLANKET `mismatches=1 met=False` rc=1 | killed by the BASE control (then `mismatches=4`) and by BLANKET (`mismatches=1`) — both in committed sets; no custom probe needed |
| C2M5 `:64` | `P2_WANT = UNREAD` | `mismatches=1 met=False` rc=1 | rc=1 / rc=1 | killed by M itself |
| C2M6 `:200` | skip base pass (`bgot = tip[cid]`) | `base_mismatches=0 flips=0 stable=9 met=True` rc=0 | BASE `mismatches=6 met=False` rc=1; BLANKET `mismatches=2 met=False` rc=1 | **survivor of committed controls** on `(rc,met)`; only the printed `flips=6` betrays it. Killed only by a control pinning `flips=6`/`base_mismatches=6` in the printed line (both printed but ungated). |
| C2M7 `:81` | P1 want `OFF` → `UNREAD` | `mismatches=1 met=False` rc=1 | rc=1 / rc=1 | killed by M itself |
| C2M8 `:201` | force exit to match (`got=(…,want[2])`, insert) | **green** `mismatches=0 met=True` rc=0 | BASE `mismatches=6 flips=4 stable=5 met=False` rc=1; BLANKET `mismatches=2` rc=1 | killed by BASE only on the printed `flips` number; on `(rc,met)` it **survives all three** — a real exit-code-ignoring mutant the committed predicates cannot see at M. Control that would kill it: a cell (probe-level) whose (verdict, reason) match but whose *exit* differs and is graded — e.g. a blanket-refusal tip graded at M (P2-by-blanket wants exit 0, gets 2), or already at M: the blanket control distinguishes it from pristine only after gating flips. |

Knock-on note: C2M3 (ignore-exit by hardcoding 2) and C2M8 (force-to-want) are *not*
equivalent mutants — M kills M3 (because P2 wants 0 ≠ forced 2) but not M8 (because M8
copies the want, not a constant). Both halves of "ignore the exit code in the comparison"
are therefore covered, with different killers; the honest survivor is M8.

## Build notes

- `round()` vs `int()` (C1M8): `round(100·4/12) = round(33.33…) = 33 = int(…)` and
  `round(100·6/12) = 50 = int(…)`. Python banker's rounding would differ only at exact
  `*.5` (e.g. `round(37.5)=38` vs `int=37`); the committed data (12 seats, 4 and 6
  attacks) has no `.5`, hence equivalence. The lane HEAD is `6d0e3abc…` (not M
  `2e27e6f1…`) — the three files copied for probes were byte-checked equal to M first.
- C1M4 is written as the single-line `frac` change (count-only rendering) rather than the
  two-line checks-3/4 rewrite — same mutant class, strictly one mutated line.
- The C1 forgery harness copies lane working-tree files and commits them, so `--counter`
  being absolute vs lane-relative made no difference (it resolves and runs the given file).
- C2 controls: `@BASE` = `mutant --rev 6776c667…`; `@BLANKET` = same with
  `--probe-file work/probe-blanket.sh` (see blanket-SHA note above). All C2 logs are in
  `out/MT01Mutants/logs/`.

## Restoration

- No tracked lane file was modified. Post-run verification (this report's `hashes.txt`):
  `tools/round100-record-audit.py` still sha256 `6fcc628e…4386` and
  `tools/round100-props-status.py` still `ce2f0641…05e2`, both equal to
  `git show 2e27e6f1:<path>` bytes.
- Every mutant lived only in scratch (`/fast/scratch/hyaku/kama-r100/MT01Mutants/mutants_*`)
  and was copied into `out/MT01Mutants/` as receipts. Scratch was deleted before yield.

## VERDICT section (Amendment-59 pre-file gate vocabulary)

- The question is whether a frozen counter goes green on a property **narrower** than the
  claim's stated wording. The findings above are about missing controls for the checks as
  worded, not about the wording itself overclaiming. No case shows the claim's wording
  claiming more than the counter checks, and every number in every receipt re-derived
  byte-equal to the committed receipts. The survivors are pigs in the control set (some
  are exit-code-equivalent mutants; C1M3/C1M5/C1M6/C1M4 and C2M1/C2M6/C2M8 survive only
  because no committed control pins the check-number set or the printed counts), not a
  falsification of the claims' stated wording or of any number.

VERDICT C1 neutral mutant-vs-control coverage gaps only; wording and numbers falsify neither
VERDICT C2 neutral mutant-vs-control coverage gaps only; wording and numbers falsify neither
