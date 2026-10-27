# R57Item09ClaimFalsifier — frozen C1 no-op control and predicate, falsified

Role: sentinel (leaf, no subagent dispatch). Axes: calibration, operability. All
reads are against committed bytes at the frozen tip
`b89bdab2cc114735ec5d331c6c610134258f7864` (worktree HEAD at seat start
`7c873d7b4e3839489a93d6334cdf93fe5d34d19f`). No shared/source edits, no git/jj
mutation, no tool install (strace/python3/coreutils only; pacman untouched).

## Claim-ordering conflict (reported, not resolved)

The seat context labels C1 *calibration, stale canonical capability row count /
`maxN` 46 vs 56* and C2 *operability, canonical-row execution binding*.
`controls/freeze-amendment.txt` labels C1 *operability, the round56-prereg-check
no-op defect* and C2 *calibration, the stale self-description count*, and says it
supersedes the earlier freeze's ordering only. Both orderings are recorded here;
every finding below is keyed to the **receipts and bytes**, not to the C1/C2
labels, so it stands under either ordering.

## Verdict

1. **The frozen C1 no-op control is falsified as a control.** `controls/c1-noop.py`
   is a three-line program that prints the green line; it never reads the target,
   the repository, or its own arguments. Its receipt `controls/noop-c1.out` is the
   program's own stdout. Therefore `noop_C1=met=True exit=0 despite skipping data`
   (freeze.txt) is **not a measurement of the counter** — it is the string the
   counter is supposed to be able to produce. The same holds for
   `controls/noop-c2.out`, whose `canonical_table_reads=0 self_description_reads=0`
   lines have **no committed instrument** behind them anywhere in the lane.
2. **The frozen C1 predicate is falsified at the frozen bytes.** The committed
   `tools/round56-prereg-check.py` at the tip returns `met=True, exit 0` for a
   battery that declares the preregistered `ROSTER` literal and executes none of
   its entries (my fixture A), and `met=True, exit 0` for the genuine battery. The
   predicate's reject half ("the measured checker rejects a no-op") is false at the
   frozen tip, and the two inputs are *indistinguishable* to that checker, which
   only compares an AST literal to the prereg JSON.
3. **The underlying defect survives.** The no-op false green is real and I
   reproduced it independently (fixture A at the tip's committed checker; same
   posture as round-56 `.ufo/waves/round-56/measured/c2-noop-control.out`). The
   frozen *evidence* is invalid; the *target* is not.
4. **The numeric framing in the seat context does not survive.** The canonical
   capability table at the tip has **11 data rows** (round-49 list, text: "Eleven
   capabilities"); the counter's `maxN` is a round-**heading** maximum and is 56,
   which equals SCORECARD's own head line `Latest measured round: 56`. The only
   stale number at the tip is the SCORECARD calibration `run ... → 42` fact while
   `corpus/lessons/*verifier-spotcheck.md` has **43** blobs. `46` is a *historical
   round-46 receipt value* (`SCORECARD.md:2676`) that was copied into the control's
   literal print.

## Evidence

Commands, exits and byte hashes: `ClaimFalsifier/09/commands.json`,
`ClaimFalsifier/09/sha256s.txt`. Scratch:
`/fast/scratch/hyaku/kama-r57/R57Item09ClaimFalsifier`.

### A. The control has zero dependency on the target

```
$ python3 .ufo/waves/round-57/controls/c1-noop.py
mismatches=0 maxN=46 met=True                       exit=0   (control-echo.out)
$ python3 .ufo/waves/round-57/controls/c1-noop.py --repo /nonexistent --tip deadbeef   # cwd=empty dir
mismatches=0 maxN=46 met=True                       exit=0   (control-bogus-argv.out)
$ python3 .ufo/waves/round-57/controls/c1-noop.py --counter /nonexistent/checker.py     # target absent
mismatches=0 maxN=46 met=True                       exit=0   (control-target-absent.out)
```

All three files hash to
`bffba21626ad79816e36b1be6f0a244d64f06e692aff6a9162f6cddcf39cd407` — one output,
three inputs, including an invalid target and an absent target. The control is
byte-identical to the receipt body (`noop-c1.out:3`).

Syscall audit (`control-syscall-audit.txt`, strace `openat,execve`): 36 trace
lines, **0** opens of any target surface (`SCORECARD`, `round42-selfdesc`,
`round56-prereg`, `preregistration`, `round56-env-leg`), 2 opens of the control
file itself. The control reads nothing it purports to grade.

Consequence: the control cannot distinguish a counter that rejects no-ops from
one that accepts them. The sibling worktree patch (see C) flips the target's own
run `met=True → met=False`, while this control's output stays byte-identical.

### B. The predicate is false at the frozen tip

Fixture A: an isolated git repo (root verified as the fixture dir) carrying the
tip's `preregistration.json` and a battery whose `ROSTER` literal is the
preregistered dict with `main(): return 0` and no entry execution.

```
$ python3 <tip bytes of tools/round56-prereg-check.py> --repo fixtureA --tip 5f7e1f5d...
present=1 roster_match=1 kills=1 controls=2 met=True     exit=0   (fixtureA-noop-frozen-checker.out)
$ python3 tools/round56-prereg-check.py --repo LANE --tip b89bdab2...   # genuine battery
present=1 roster_match=1 kills=1 controls=2 met=True     exit=0   (genuine-battery-at-tip.out)
```

The checker's only subprocess is `git` (line 25); it never imports or runs the
battery, so `EXECUTED`/`idle` never appears in its output. No input can make the
frozen checker accept the genuine roster and reject a no-op that carries the same
literal, because that literal is the whole input. The predicate as frozen is not
a function of what the instrument measures.

### C. The sibling repair is bypassable in one line of dead code

An uncommitted worktree edit to `tools/round56-prereg-check.py` (present at seat
start; **not mine**, not committed) adds an `executed` test: `ast.walk` over calls
to `run`/`assert_mutant_breaks_detection` with a string first argument.

```
$ <patched checker> --repo fixtureA --tip 5f7e...   met=False  exit=1   (plain no-op: rejected)
$ <patched checker> --repo fixtureB --tip fb15...   met=True   exit=0   (same no-op + dead calls)
```

Fixture B is fixture A plus:

```python
if False:  # unreachable: no roster entry runs, no counter is ever invoked
    run("base-old-counter", None, "missed", None)
    run("round56-counter", None, "detected", None)
    run("m-drop-ldaudit", None, "missed", None)
```

Fixture B's frozen-checker output and patched-checker output hash identically
(`c4c0cc8d9c42684cb22fb7a42606f70f68ac111b62c376a99657058ed460d509`): the patch
buys nothing against a battery that only *names* the calls. Call presence in the
AST is a declaration, not an execution.

Smallest remediation that the fixtures support: bind to execution evidence, not
syntax — have the checker run the battery and require a per-entry run receipt
(entry label, counter path, exit code, expected/observed field) that the checker
re-reads, and add fixture B to the controls. Any test satisfied by a literal
print or an unreachable call is not a control.

### D. `noop-c2.out` is unreproducible

`control=no-op instrument / canonical_table_reads=0 / self_description_reads=0`
occurs nowhere except that receipt and reports quoting it; no committed script
prints it (`grep -rn 'no-op instrument'` over the lane). The staged fixtures
`controls/canonical-noop/` and `controls/no-canonical/` have **zero consumers**
(no `tools/` or `tests/` reference). These are staged apparatus with no
instrument, so neither `noop-c1.out` nor `noop-c2.out` can be re-derived, and
`base_counter=1` is the only part of the frozen control pair that re-derives.

## Numbers re-derived at the tip (canon-derivation.txt)

| Quantity | Value | Derivation |
|---|---|---|
| canonical-list heading | round 49 | highest `canonical list as of round N` |
| canonical table data rows | **11** | table after that heading; text says "Eleven capabilities" |
| `## Round N` headings | 57 (min 6, max 56) | `^## Round (\d+)` |
| counter `maxN` | **56** | `max(rounds)`; matches SCORECARD head `Latest measured round: 56` |
| counter mismatches at tip | 1 | `r41` fact `42` vs tree count |
| `corpus/lessons/*verifier-spotcheck.md` at tip | **43** | `git ls-tree` at tip |
| SCORECARD calibration RUN fact at tip | `42` | stale by one (round-56 lesson) |
| control literal `maxN` | 46 | historical round-46 receipt, `SCORECARD.md:2676` |

`46` is therefore neither the canonical row count (11) nor the current round
heading maximum (56); it is a past measured value reused as an expectation.
Repairing the *counter* toward `46` would make it disagree with the SCORECARD
head it is supposed to reconcile; the stale number that should move is the
SCORECARD `42 → 43` fact (already present uncommitted in the worktree).

## What survives

- C1's *substance*: a no-op that declares the matching roster and executes none
  is accepted at the frozen tip (`met=True exit=0`), reproduced with a fresh
  isolated fixture and consistent with round-56's `c2-noop-control.out`.
- The base receipt `base-c2-frozen.out` (`mismatches=1 maxN=56 met=False`,
  exit 1) is genuine: I reproduced it exactly from the tip bytes.
- The frozen *control* and the *46 / canonical-row-count* framing do not survive.

## Limits

- Read-only; no repair implemented (executor seats own that). The worktree was
  already modified by other seats (`SCORECARD.md` calibration `43`,
  `tools/round56-prereg-check.py` patch); I read committed tip bytes for all
  frozen-claim evidence and only *probed* the worktree patch, without editing it.
- Fixtures A/B are synthetic minimal copies of `preregistration.json` + battery;
  they prove the checker's input surface, not any real battery run.
- No axis score or verdict is claimed; this is a falsification seat.
- Advisory only (this is a lane-author seat, not the non-author spot-check):
  the S515 re-open with a located ≤25-word quote and the admit/reject spot check
  are owed by the source seats (`SourcesReopen/06`, `SourcesReopen/26`,
  `SourceAudit/13`, `SourceAudit/33`); this seat did not widen scope to them.

Report: .ufo/waves/round-57/w1/out/R57Item09ClaimFalsifier.md
