# Round 87 — frozen claims

Base revision `362b0d4a241520c9bc79b204c042d9fcefbb06ea` (master, pushed; `jj-lane.sh state` at round start:
`local=362b0d4a remote=362b0d4a ahead=0 behind=0`). Freeze commit: the commit that adds this file and
`.ufo/waves/round-87/controls/` (its hash is printed by the helper as `landed`; recorded in the report).
Freeze date 2026-11-05.

**Fresh-start round.** Operator run-15 amendment 27 ("Authorize all", 2026-11-05) moved kama's quality pause
to `blocked/.kama.run15-20261105-N`; history is retained and not repaired. The last three rejected closures
were read before declaring anything: `corpus/lessons/round-84-verifier-spotcheck.md` (rejected-honest-stop),
`round-85-verifier-spotcheck.md` (rejected-honest-stop), and `round-86-verifier-spotcheck.md`
(verdict `rejected-honest-stop`; its C1 was falsified by two reproduced false greens, P-A and P-B below).
Its roster item R86V1 (three lane-authored round-86 files left untracked) is resolved in this round's freeze
commit: the three files are committed as they stand, not rewritten.

Assigned axes: operability 8, calibration 7 (`shokunin.conf`). Calibration is the lowest assigned axis, below
the saturation line 8, so claim C1 works it; no stagnation waiver is taken.

Two claims, distinct axes, causally separable (C1 touches `tools/round87-rendered-cells.py`, the SCORECARD
calibration cell, and `controls/c1-probes.py`; C2 touches `tools/pre-report-gate.py` and
`tools/round87-gate-arm-faults.py`; neither needs the other to verify). No exploratory claim.

## Do-nothing controls (executed and committed before this freeze)

| Control | Command | Receipt | Result |
|---|---|---|---|
| C1 live cells, no work | `python3 tools/round86-rendered-cells.py --repo . --rev 362b0d4a…` | `controls/c1-live-before.out` | `mismatches=2` (closure round-85, disposition), exit 1 |
| C1 probe battery, no work | `python3 controls/c1-probes.py tools/round86-rendered-cells.py` | `controls/c1-probes-before.out` | `escapes=3 control=red`, exit 1 |
| C2 gate, no work | `python3 tools/pre-report-gate.py --repo . --round 87 --tip master` | `controls/c2-gate-before.out` | `arms=13 failed=4`; `round86-instruments` count 0 |

The C1 do-nothing control is red on its own predicate. The C2 do-nothing control is red on its own predicate
(no arm). The probe battery's control (stale live cell, no shadow text) is red for the frozen selector, so a
selector that blanket-refuses everything would still fail on escapes only if it also passes the control;
the control is kept as a positive check.

## C1 — calibration: the rendered-cell selector repaired and the live self-assessment cell made true

Axis move: calibration (7). Self-assessment cells vs rendered identity, measured as mismatches and escapes.

Before (measured at `362b0d4a`): live mismatches `2`; probe escapes `3/3`.

After — two frozen predicates, both must hold at the measured revision `R` (the freeze-or-later commit that
carries the SCORECARD cell and the successor selector):

1. `python3 tools/round87-rendered-cells.py --repo . --rev R` prints exactly
   `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=86 newest_closure=86`
   and exits 0. The calibration row of SCORECARD.md names `corpus/lessons/round-86-verifier-spotcheck.md`
   and the disposition token `round86 rejected-honest-stop` (the verdict token of that closure; the cell is
   corrected to observed state, not to a verdict the closure does not state).
2. `python3 .ufo/waves/round-87/controls/c1-probes.py tools/round87-rendered-cells.py` prints
   `C1_PROBES probes=3 escapes=0 control=red` and exits 0.

Successor selector rules (frozen; the successor is a new file, `tools/round86-rendered-cells.py` is not edited):
- R1 fence: a fence closer is a line of at most three leading spaces, then the fence characters of the opener
  (same character, at least as long), then only spaces or tabs. A list-marker or blockquote-marked line
  (`- ```…`, `> ```…`) is content, never a closer (CommonMark 0.31.2 §4.5, S578).
- R2 disposition: the disposition is the single token written after `verdict ` in the closure's own verdict
  line (`verdict \`<token>\``). A word elsewhere in the body is not the disposition. Missing or ambiguous verdict
  line → mismatch.
- R3 fixture API preserved: `fixture`, `grade`, `render`, `A`, `B`, `GOOD_CMD`, `GOOD_TOKEN`, `GOOD_RECEIPT`,
  `GOOD_ROW`, `CouldNotEvaluate` keep their round-86 names and meanings, so `controls/c1-probes.py` loads it
  unchanged.
- R4 population unchanged: the three facts (gate, closure, disposition) and their coupling as frozen in
  `tools/round86-rendered-cells.py`'s docstring. Any other change is a new claim.

Kill rule: any probe escaping (exit 0 on P-A, P-B or P-C), a green control, or any `mismatches` > 0 at `R`
makes C1 not verified. The result is then reported as an honest stop; no predicate, probe or cell is edited
after data to clear it.

Probes (frozen; the same sentences are the probe comments in `controls/c1-probes.py`):
- P-A `list-marker-closes-fence`: `"```markdown\n- ```\n"` shadow carrying a stale-live fixture. Before: escape.
- P-B `wrong-disposition-word-in-row`: closure body with `rejected-harmed` before its verdict; calibration row
  names `round85 rejected-harmed`. Before: escape.
- P-C `extra-revision-without-receipt`: gate cell naming a second revision carrying the same receipt token.
  Before: escape.

Counting command for the report: `python3 .ufo/waves/round-87/controls/c1-probes.py tools/round87-rendered-cells.py`
and `python3 tools/round87-rendered-cells.py --repo . --rev R`.

## C2 — operability: the round-86 instruments composed as gate arm `round86-instruments`

Axis move: operability (8). Capability: `gate-round86-instruments` (new row in the SCORECARD capabilities table
at first-working round 87, only if demonstrated).

Before (measured at `362b0d4a`, `controls/c2-gate-before.out`): `PRE_REPORT round=87 arms=13 failed=4`;
`round86-instruments` absent.

After — two frozen predicates at revision `R`:
1. `python3 tools/pre-report-gate.py --repo . --round 87 --tip master` prints a line
   `PRE_REPORT_ARM round86-instruments exit=0 ok …` and the verdict line carries `arms=14`.
   The arm runs the `--selftest` of `round86-rendered-cells.py`, `round86-mutant-owners.py` and
   `round86-pin-origin.py` (offline fixtures, no network) and requires each summary to be
   `<prefix> pass=<n> fail=0`. The arm is appended after `round83-instruments` in `ARM_ORDER`.
2. `python3 tools/round87-gate-arm-faults.py --repo .` prints `ARM14_FAULTS faults=3 killed=3 escaped=0`
   and exits 0. The harness seeds one fault per round-86 instrument (its `--selftest` replaced by a stub that
   exits 0 with a failing summary) in a scratch tools tree, runs the gate's `evaluate()` with that tools dir, and
   counts a fault killed when the arm `round86-instruments` is not ok. A missing arm counts as escaped.

Harm rule: every `PRE_REPORT_ARM` line that is `ok` at `362b0d4a` on the same tree stays `ok` at `R`; the
gate's ARM_ORDER prefix is unchanged. Arms that were red at base may turn green (selfdesc, newest-closure,
round-scope, round75-instruments depend on the C1 cell and this plan file).

Kill rule: arm absent or not ok at `R`; any fault leaving the arm ok; any base-ok arm turning red.

Counting commands for the report: the two predicates above, pasted with exit codes.

## Frontier step (within the two-claim cap)

- `corpus/SOURCES.md` census before (round start, `validate --root /home/vgpnk/Projects/shokunin kama`):
  exit 0, `FLEET rows 319 tier.A 304 tier.B 11 tier.C 4 status.mined 286 status.queued 8 status.rejected 25`.
  Census at round end is required to exit 0.
- A row is written only after its source is opened this round. C1 rests on CommonMark 0.31.2 §4.5 (fence
  closer rule, S578) and §5.2 (list items, the container that makes `- ```` content). Both are re-opened this
  round and the gate records the access date and a ≤25-word located quote; a new row is written only when the
  quote is located.
- Mined mistakes into `corpus/lessons/round-87.md` `## Mistakes`: R86V1 (untracked round-86 strays; the
  gate's round-clean arm is round-scoped, so round-86 strays were out of its view), R86V2 (C1 false greens: a
  list-marker closer and a first-fixed-order-word disposition oracle, both reproduced by `controls/`).
- One `considerthese/` proposal (from the 2026-10-26 file's "proposals only … not implemented" list) is
  mined: grounded through the lane's bar, lands as a lesson line, a QUALITY.md criterion or a SOURCES row citing
  `considerthese/2026-10-26.md`; if it is not grounded, the report says so.
- Assimilation: none (no `merge/kama/` package is adopted this round; the report says `Assimilation: none`).

## Scope and bounds

Writes only under `/home/vgpnk/Projects/shokunin/kama-shokunin`, plus the fleet-repo report and `l0-questions.md`
appends. No edits to MANIFEST.json, templates/, scripts/, .ufo/state/, the watchdog log, sibling repos or
`/home/vgpnk/Projects/shokuknow`. `considerthese/` is read-only. Seats never commit, never push, and never run a
mutating git or jj command.
