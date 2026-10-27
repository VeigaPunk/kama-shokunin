# R57Item30AxisFit — distinct case 51: claim separability and axis attribution

Role: simplifier (bounded leaf). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Distinct case 51: the assigned case is tested independently in this file; receipts are in
`R57Item30AxisFit-case51.receipts/`. No shared/source edits by this seat; no commits, no jj/git
mutation outside private fixtures; scratch was `/fast/scratch/hyaku/kama-r57/R57Item30AxisFit`
(fixtures removed after receipts were copied here). No installs.

Frozen base: `b89bdab2cc114735ec5d331c6c610134258f7864`. Live lane tips seen during the seat, in
order: `89dc4f52` (freeze) → `7c873d7b` (pre-data claim correction) → `7b74e2f2` (checker edit) →
`8640e34c` → `16efcf5e` → `77e7f5ee` → `8a7f1976` (last read at write time; the lane is still
moving). The lane moved under the seat; the base did not. All base claims below are anchored at
`b89bdab`.

## 1. Assigned claim text (as dispatched to this seat)

> C1 calibration—repair the stale canonical capability row count, counter currently reports
> maxN=56 instead of expected 46; before output mismatch=1. C2 operability—distinct, actual
> canonical-row execution/content binding; a no-op currently reports met=True exit 0.

This is the pre-correction ordering. It is not what the lane froze before data: commit `7c873d7b`
("round-57: correct frozen claim targets before data") added `controls/freeze-amendment.txt`, which
states C1 = operability (round56-prereg-check no-op) and C2 = calibration (stale count 42, observed
43), and says "C1 and C2 are distinct axes, each measured independently". `SCORECARD.md` §Round 57
and `corpus/lessons/round-57.md` both use that corrected mapping. One of the two conflict statements
is stale; the seat prompt is the stale one. This is reported, not silently resolved.

## 2. Axis attribution matrix

| Source (authority) | C1 axis / target | C2 axis / target |
|---|---|---|
| `shokunin.conf:52` (live lane config; driver SSOT) | operability | calibration |
| `MISSION.md:29` (block marked "Historical example", `MISSION.md:16`) | operability (freshness also assigned) | freshness (calibration absent) |
| `controls/freeze.txt` (committed `89dc4f52`) | calibration, "stale canonical-table count" | operability, "canonical-row execution binding" |
| `controls/freeze-amendment.txt` (committed pre-data `7c873d7b`) | **operability**, prereg-check no-op | **calibration**, stale count 42→43 |
| `SCORECARD.md` §Round 57 (live) | operability 8→8, "bind declared roster to actual battery call sites" | calibration 7→7, "re-anchor the SCORECARD verifier-spotcheck count" |
| `corpus/lessons/round-57.md` §Claims (live) | operability | calibration |
| Seat assignment (this prompt) | **calibration**, "stale canonical capability row count, maxN=56 vs expected 46" | **operability**, "canonical-row execution/content binding" |
| Swarm registry member axes | `["calibration","operability"]` (unordered; no per-claim mapping) | — |

**Verdict A (axis attribution).** The *round* is on the two assigned axes: live config assigns
operability + calibration, and the committed pre-data amendment, SCORECARD §Round 57 and the lesson
all put one claim on each. The **seat prompt's per-claim mapping is inverted** relative to that
pre-data correction, and its C1 numeric target does not exist (see §3). Under the live config the
pair is valid; under `MISSION.md:29` (operability + freshness) the calibration claim would be
out-of-axis. `MISSION.md:50` says shokunin.conf assignments "are initial" and lanes may add/remove
axes on evidence, and `SCORECARD.md:6` records the disagreement verbatim as "an open L0 question
since round 35". Per the wave instruction this is **not resolved here** — flagged for L0. Quotes:
`attribution-quotes.txt`.

## 3. Independent derivation of the C1 number ("maxN=56, expected 46")

Commands and outputs (`derive-base.txt`, `r42-at-base.out`, `r41-at-base.out`):

```
$ git show b89bdab:SCORECARD.md > evidence/SCORECARD.at-base.md
$ python3 -c '<heading/canonical parse over that blob>'    # actual script in commands.txt §A
round headings=57  max ## Round N = 56          # includes the out-of-order "## Round 30" heading
canonical list as of round 49, 11 data rows
calibration row run fact: glob(corpus/lessons/*verifier-spotcheck.md) -> `42`
$ git ls-tree -r --name-only b89bdab -- corpus/lessons | grep -c 'verifier-spotcheck\.md$'
43
$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip b89bdab
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
```

* The counter's own definition is `maxN = greatest N over SCORECARD lines matching ^## Round (\d+)`
  (module docstring, and `evaluate()` builds `rounds` from exactly those lines). At the frozen base
  the greatest heading is 56, so **maxN=56 is correct, not stale**. At the round-57 tip the counter
  reports `maxN=57` (`measured/c2-committed-tip.out`); at `7b74e2f2` it reported `maxN=56`.
* The canonical capability table holds **11** rows (round-49 list), not 46.
* `46` is the correct `maxN` of **round 46** (`.ufo/waves/round-46/measured/r42-final.out`:
  `mismatches=0 maxN=46 met=True`); the literal `46` does not occur in the counter source.
  The round-57 no-op controls simply print the round-46 value.
* The real stale item at the base is the **SCORECARD calibration run fact `42` vs 43 committed
  `*verifier-spotcheck.md` blobs** — that is exactly the `r41=1` detail, and repairing that one
  number moves the counter to `mismatches=0 met=True` with `maxN=56` unchanged (§5, S2).

**Verdict B (calibration claim, i.e. committed C2).** The live calibration predicate is supported:
base is red on the count, the corrected count is green, and maxN is untouched. The seat prompt's
version of the claim ("maxN 56 → 46") is **unsupported and unsatisfiable without breaking the
counter's own banner/planned predicates**: at the base head, `Latest measured round: 46` is absent
and `### Planned (round 47)` is absent from the `## Planned` section, so a forced maxN=46 adds the
banner and planned failures (`maxn-target-selfconsistency.txt`; candidate 56 scores `True/True`,
candidate 46 scores `False/False`). That is a claim-identity defect, not a counter defect.

## 4. Execution/content binding test (committed C1 / prompt C2)

Instrument identity: frozen base checker `tools/round56-prereg-check.py` sha256
`c7b0d787…f1489853` (equals the prereg's `counter_sha256`); live checker sha256
`dee6f922…2e90ced` — the round-57 edit (`+12/−1` in `7b74e2f2`) adds an AST call-site inventory
(`invoked`/`expected`/`executed`) by walking every `run(...)` /
`assert_mutant_breaks_detection(...)` call with a string constant first argument
(`instruments-sha256.txt`).

Three independent fixtures, each with the genuine prereg and a battery variant carrying the exact
`ROSTER` literal (`variant-matrix.out`):

| battery variant | base checker | live checker | execution probe (`exec_bind.py`) |
|---|---|---|---|
| `no-calls` (`main(): return 0`, no call sites) | `met=True` exit 0 | **`met=False` exit 1** | `met=False` exit 1 |
| `unreachable-calls` (call sites after `return`) | `met=True` exit 0 | **`met=True` exit 0** | `met=False` exit 1 |
| `genuine` (labels emitted at run time) | `met=True` exit 0 | `met=True` exit 0 | `met=True` exit 0 |

`exec_bind.py` binds the same roster to runtime evidence: it runs the battery and requires every
control/positive-control/kill label to be written by the process, not merely mentioned in source.

**Verdict C.** The landed round-57 repair binds **call-site textual inventory**, not execution. It
kills the exact round-56 no-op (`main(): return 0`) but a no-op whose roster calls sit in unreachable
code still returns `met=True`/exit 0. `SCORECARD.md` §Round 57 discloses this honestly ("C1 does not
assert that every runtime effect of a battery call was executed"), but `corpus/lessons/round-57.md`
overstates it ("so a no-op harness cannot satisfy the counter"), and the claim table's after-state
("matching-roster no-op: `met=True` → `met=False`") holds only for the call-free variant. The seat
prompt's wording "actual … execution/content binding" is therefore true for **content**, false for
**execution**.

## 5. Claim separability test (2×2, one fixture, one variable per step)

Fixture: `git clone --shared` of the lane at `b89bdab`, toplevel asserted before every commit; three
states (S0 = `b89bdab`; S1 = fixture commit `858107a1`; S2 = fixture commit `c4571e86`). No lane
object or file was touched. Mapping: prompt-C1 = committed C2 (calibration counter); prompt-C2 =
committed C1 (operability prereg checker).

| state | calibration counter `round41`/`round42` | operability checker frozen | operability checker live | execution probe |
|---|---|---|---|---|
| S0 = base | `r41=1 mismatches=1 met=False` | `met=True` exit 0 | `met=True` exit 0 | not run (genuine battery writes to the lane by absolute path) |
| S1 = S0 + unreachable-call no-op battery | `r41=1 mismatches=1` (unchanged) | `met=True` (unchanged) | `met=True` (unchanged) | `expected=3 ran=0 met=False` |
| S2 = S1 + calibration count `42`→`43` only | **`r41=0 mismatches=0 met=True`**; full counter `mismatches=0 maxN=56 met=True` | `met=True` (unchanged) | `met=True` (unchanged) | `met=False` (unchanged) |

Readings:

* The calibration predicate moves **only** with the SCORECARD count edit (S1→S2) and is unchanged
  by the operational battery variant (S0→S1).
* The operational/execution predicate is unchanged by the count edit (S1→S2) and moves **only**
  with the battery variant (variant matrix above).
* The instruments are disjoint: `round56-prereg-check.py` reads only the prereg + battery bytes;
  `round42-selfdesc-reconcile.py` imports `round41-scorecard-reconcile.py` and reads SCORECARD /
  SOURCES / README / PROVINCE; neither imports the other.

**Verdict D (mechanism separability).** **PASS** — each claim is verifiable without the other
landing, on distinct axes, with a distinct instrument and a distinct before→after.

**Verdict E (frozen-receipt separability).** **FAIL.** The pre-data control set does not carry that
separation:

* `controls/base-c1.out` and `controls/base-c2-frozen.out` are the **same** round-42 counter output
  at `b89bdab`; the only difference is the appended `base_c1_exit=1` line (333 vs 318 bytes;
  `base-receipts-diff.txt`, `base-receipts-identity.txt`). Under the corrected mapping only C2 may
  use that instrument; C1's frozen base control is the calibration counter's output.
* `controls/noop-c1.out` is `controls/c1-noop.py` printing `mismatches=0 maxN=46 met=True` — a
  round-42-counter summary forgery. `controls/noop-c2.out` is the same counter instrument
  (`canonical_table_reads=0 self_description_reads=0 summary=mismatches=0 maxN=46 met=True`). Neither
  receipt runs `tools/round56-prereg-check.py`.
* `controls/canonical-noop/` and `controls/no-canonical/` are reduced trees (`SCORECARD`,
  `SKILL`, `PROVINCE`, `README`, `corpus/`) for the round-42 counter's canonical-table selection —
  calibration fixtures, cited as such by seats R57Item04/R57Item19.
* The only receipts using the prereg checker are post-data: `measured/noop-c1.out`
  (`checker=tools/round56-prereg-check.py … met=False exit=1`) and `measured/c1-committed-tip.out`
  (`met=True`, genuine roster). The no-op fixture tip `8caa23a2` is not in the lane object store
  (`git cat-file -t` → fatal), so that receipt is not re-derivable from the lane.

Cause is the amendment's own scope: it "supersedes … claim ordering only, not its base/control
evidence", and the controls were not re-bound after the swap. Net: two claims that are separable in
code and measurement are **not separable in their frozen pre-data receipts**; C1's pre-data base
reads the C2 instrument. Repair belongs to the planner/executor seats; this seat did not edit.

## 6. Round-56 outside defects vs the round-57 lesson

| Round-56 routed defect | Round-57 lesson status |
|---|---|
| Axis-authority conflict (MISSION vs conf/SCORECARD/prompt) | **not lesson-addressed**; only the SCORECARD banner keeps it open |
| Strengthen no-op gates to bind executed entries | addressed but overstated (see §4) |
| S513 rejection rationale disagreement | addressed (`Mistakes` row `discernment-disagreement`), preserved, not resolved |
| Inherited append-only audit exit 1 / invalid `declared_at`-SCORECARD bindings | **not lesson-addressed** in `corpus/lessons/round-57.md` |

Advise: add rows (or explicit deferrals with receipts) for the two unaddressed defects; the
axis-authority row should at minimum cite `MISSION.md:29` and `SCORECARD.md:6` so the conflict is
carried forward instead of disappearing from the lesson.

## 7. Advisories (lane-author seat; advice only)

* An independent **non-author** admit/reject spot-check is still required before admission; this
  seat is a dispatched lane author and cannot supply it. S515's quote/location is already recorded
  in the round-57 lesson (Git config, `GIT_CONFIG_COUNT` section, 18 words); the non-author seat
  should re-open the live URL and locate it independently rather than rely on this note.
* Do not admit the round on the current C1 after-state alone: the after-state is defeated by an
  unreachable-call no-op (§4). Either narrow the claim wording to call-site inventory (SCORECARD
  already does) with the receipt saying so, or bind execution for real.
* Do not carry the prompt's `maxN=46` target into any repair: it is the round-46 value and would
  break the counter's banner/planned predicates (§3).
* `considerthese/2026-10-26.md` proposal 3 (counter-shortcut tally) is opened by the lesson but not
  implemented ("does not implement a multi-round tally"); leave the tally itself to the proposal-audit
  seat, and do not count it as an assimilation.

## 8. Receipts (relative to this file)

`seat-assignment-vs-amendment.txt`; `attribution-quotes.txt`; `derive-base.txt`; `r42-at-base.out`;
`r42-at-head.out` (tip `7b74e2f2`); `r41-at-base.out`; `S0-r41.out`; `S0-precheck-at-base.py.out`;
`S0-precheck-at-head.py.out`; `S1-r41.out`; `S1-precheck-at-base.py.out`;
`S1-precheck-at-head.py.out`; `S1-exec-probe.out`; `S2-r41.out`; `S2-r42.out`;
`S2-precheck-at-base.py.out`; `S2-precheck-at-head.py.out`; `S2-exec-probe.out`;
`variant-matrix.out`; `base-receipts-diff.txt`; `base-receipts-identity.txt`;
`instruments-sha256.txt`; `maxn-target-selfconsistency.txt`; `commands.txt`; method source
`exec_bind.py`, `batteries.py`, `build_variants.py`; committed control blobs
`committed-at-8a7f1976-{c1-noop.py,noop-c1.out,noop-c2.out,base-c1.out,base-c2-frozen.out,freeze.txt,freeze-amendment.txt}`.

## 9. Shared-tree movement observed during the seat (not by this seat)

The lane's HEAD advanced under the seat (`89dc4f52` … `8a7f1976`). At the last read,
`git -C kama-shokunin status --porcelain .ufo/waves/round-57/controls` showed **worktree deletions**
of `controls/c1-noop.py`, `controls/noop-c1.out`, `controls/noop-c2.out` plus an untracked
`controls/noop-fixture/`; this seat did not delete or create any of them (its only lane writes are
this report and `R57Item30AxisFit-case51.receipts/`). All seven control/freeze blobs cited above
were therefore captured from `HEAD:8a7f1976` into `committed-at-8a7f1976-*` so the evidence here
does not depend on the worktree state. The tracked-file diff outside this reports/ directory was
empty at every measurement this seat took; the three deletions appeared after the report's
measurements were complete.

Report path: `.ufo/waves/round-57/reports/R57Item30AxisFit-case51.md` (this file).
