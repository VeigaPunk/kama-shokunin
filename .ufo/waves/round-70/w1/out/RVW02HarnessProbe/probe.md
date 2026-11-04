# RVW02HarnessProbe — tip-checkout vs git-less-export probe (round 70, lane kama)

Axes: operability + calibration. This seat: advisory leaf, read-only on the lane, no subagents.
Milestone: "attack C1: bounded probe that a tip checkout reproduces both git-dependent facts".

## Hypothesis (falsifiable, bounded)

"a checkout of the lane at the tip (with `.git`) makes BOTH git-dependent `## Axes` facts
reproduce exactly, while a git-less export cannot."

The two git-dependent facts (per `.ufo/waves/round-70/w1/w1-dispatch.json`, EX01 item; both are
run-facts cited in `SCORECARD.md` `## Axes` at base 6035e952):

1. operability row: `python3 tools/gate-registry-check.py --selftest` → cited `GATE_SELFTEST pass=7 fail=0`
2. calibration row: `python3 tools/round69-newest-closure-counter.py --since-round 63` → cited `NEWEST_CLOSURE … row_current=true`, exit 0

Problem being probed (per the same dispatch): the round-41 harness `evaluate()` builds a git-less
tree export (`git archive | tar -x`) and runs fact commands there; both git-dependent arms fail
there — the gate lane-tip arm cannot resolve a repo, the counter cannot `git ls-tree`.

## Fixtures (scratch: /fast/scratch/hyaku/kama-r70/RVW02HarnessProbe)

Base tip under test: `6035e952c2521999e192d6f236331f265ac98392` (round-70 frozen base; lane HEAD
was `0e14facd0c619f45a6461821d2bd80ddac9855b1` during the probe).

    $ git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive 6035e952 | tar -x -C "$S/export"
    EXPORT_OK files=38743          # exit 0
    $ test ! -e "$S/export/.git" && echo EXPORT_HAS_NO_GIT
    EXPORT_HAS_NO_GIT              # exit 0
    $ git -C "$S/export" rev-parse --show-toplevel; echo "GIT_IN_EXPORT_EXIT=$?"
    fatal: not a git repository (or any parent up to mount point /)
    Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set.)
    GIT_IN_EXPORT_EXIT=128

    $ git clone --quiet --shared --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin "$S/co"
    $ TL=$(git -C "$S/co" rev-parse --show-toplevel) && echo "TOPLEVEL=$TL"   # host-guard assert
    TOPLEVEL=/fast/scratch/hyaku/kama-r70/RVW02HarnessProbe/co
    TOPLEVEL_ASSERT_OK
    $ git -C "$S/co" checkout --quiet --detach 6035e952
    6035e952c2521999e192d6f236331f265ac98392
    DIRTY=0                        # status --porcelain | wc -l
    CO_HAS_DOTGIT

Tool bytes are identical in both fixtures (sha256):

    gate-registry-check.py             SAME ef8d84a25780f5b44c8ba6a7ba2c629ee81fa871458f73b298ed43df5e30e998
    round69-newest-closure-counter.py  SAME edf6c49aa6ed7d7d612e15c4ce058f57fed4ae91399ab6eda3e531f8eab4394d
    pin-watch.py                       SAME 37040977d637fa4e6c8af44b6ed1dacec77a11729813b1be636537cfc27ac1a3

So every output difference below is environment (git presence), not tool bytes.

## Run matrix (each: `cd <fixture> && bash -c '<cmd>'; echo EXIT=$?`)

### 1. gate-registry-check.py --selftest

Export (git-less) — exit **1**:

    PASS valid-row: exit=0 (want 0) line='registered 1 unregistered 0 defective 0' want-line='registered 1 unregistered 0 defective 0'
    PASS thin-row: exit=1 (want 1) line='registered 1 unregistered 0 defective 3' want-line='defective .ufo/waves/round-98/count-selftest.py: thin-row'
    PASS empty-exit-map: exit=1 (want 1) line='registered 1 unregistered 0 defective 1' want-line='defective .ufo/waves/round-98/count-selftest.py: empty-exit-map'
    PASS missing-path: exit=1 (want 1) line='registered 1 unregistered 0 defective 1' want-line='defective .ufo/waves/round-98/count-selftest.py: missing-path:.ufo/waves/round-999/count-c999.py'
    PASS prose-only: exit=1 (want 1) line='registered 0 unregistered 1 defective 0' want-line='unregistered .ufo/waves/round-98/count-selftest.py'
    FAIL lane-tip: cannot resolve master: fatal: not a git repository (or any parent up to mount point /)
    Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set.)
    PASS stale-index-population: index_empty=True exit=1 (want 1) line='registered 0 unregistered 1 defective 0'
    GATE_SELFTEST pass=6 fail=1
    EXIT=1

Checkout (with .git) — exit **0**:

    PASS valid-row: … (identical to export for the five non-git arms)
    PASS lane-tip 0e14facd0c61: exit=0 line='registered 79 unregistered 0 defective 0'
    PASS stale-index-population: index_empty=True exit=1 (want 1) line='registered 0 unregistered 1 defective 0'
    GATE_SELFTEST pass=7 fail=0
    EXIT=0

Last line: export `GATE_SELFTEST pass=6 fail=1` (exit 1); checkout `GATE_SELFTEST pass=7 fail=0`
(exit 0) — exactly the line the base `## Axes` operability row cites.

### 2. round69-newest-closure-counter.py --since-round 63

Export (git-less) — exit **2** (last stdout line):

    COULD_NOT_EVALUATE git ls-tree --name-only failed (rc=128): fatal: not a git repository (or any parent up to mount point /)
    Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set.)
    EXIT=2

Checkout (with .git) — exit **1** (full stdout):

    MEMBER corpus/lessons/round-63-verifier-spotcheck.md date=2026-10-28 source=body
    MEMBER corpus/lessons/round-64-verifier-spotcheck.md date=2026-10-30 source=heading
    MEMBER corpus/lessons/round-65-verifier-spotcheck.md date=2026-11-01 source=heading
    MEMBER corpus/lessons/round-66-verifier-spotcheck.md date=2026-11-01 source=heading
    MEMBER corpus/lessons/round-67-verifier-spotcheck.md date=2026-11-01 source=heading
    MEMBER corpus/lessons/round-68-verifier-spotcheck.md date=2026-11-01 source=heading
    MEMBER corpus/lessons/round-69-verifier-spotcheck.md date=2026-11-01 source=heading
    SCOPE population=rounds>=63 members=7
    NEWEST_CLOSURE newest=corpus/lessons/round-69-verifier-spotcheck.md date=2026-11-01 round=69 row_names=corpus/lessons/round-68-verifier-spotcheck.md row_current=false
    STALE_CALIBRATION row_names=corpus/lessons/round-68-verifier-spotcheck.md newest=corpus/lessons/round-69-verifier-spotcheck.md newest_date=2026-11-01
    EXIT=1

### 3. pin-watch.py selftest (git-independent control)

Export — exit **0**: nine PASS arms, `selftest pass=9 fail=0`.
Checkout — exit **0**: byte-identical output, `selftest pass=9 fail=0`.
The export route changes nothing for a git-independent fact.

## Result table

| `## Axes` fact (base 6035e952 citation) | git-less export | tip checkout (with .git) | checkout vs cited |
|---|---|---|---|
| operability: `gate-registry-check.py --selftest` → `GATE_SELFTEST pass=7 fail=0` | `GATE_SELFTEST pass=6 fail=1`, exit 1 (`FAIL lane-tip: cannot resolve master: fatal: not a git repository`) | `GATE_SELFTEST pass=7 fail=0`, exit 0 | **exact match** |
| calibration: `round69-newest-closure-counter.py --since-round 63` → `NEWEST_CLOSURE … row_current=true`, exit 0 | `COULD_NOT_EVALUATE git ls-tree --name-only failed (rc=128)`, exit 2 | `NEWEST_CLOSURE newest=corpus/lessons/round-69-verifier-spotcheck.md … row_names=…round-68-verifier-spotcheck.md row_current=false` + `STALE_CALIBRATION`, exit 1 | **executes exactly; true base verdict is stale** (see verdict) |
| control: `pin-watch.py selftest` (git-independent) | `selftest pass=9 fail=0`, exit 0 | `selftest pass=9 fail=0`, exit 0 | identical, as predicted |

## Verdict

**SUPPORTED**, with one precision the L1 should carry into C1 judgment:

- The checkout executes both git-dependent facts to completion; the export cannot execute either
  (gate lane-tip arm exit 1; counter exit 2 COULD_NOT_EVALUATE). Both tools fail CLOSED in the
  git-less export — no fail-open observed in either instrument.
- The gate fact reproduces its cited `## Axes` value exactly in the checkout:
  `GATE_SELFTEST pass=7 fail=0`, exit 0.
- The calibration fact reproduces the **true base-tree verdict** exactly — `row_current=false`,
  exit 1, `STALE_CALIBRATION` — which is precisely the frozen C1-before state: the base
  `## Axes` calibration row cites `row_current=true, exit 0`, and
  `.ufo/waves/round-70/measured/before/reconciler-at-base.out` independently records the same
  mismatch two ways ("no stdout line == 'NEWEST_CLOSURE … row_current=true' (exit 2)" in the
  export route, and "closure_ptr: calibration row latest outside closure is round-68; newest at
  tip is round-69"). My checkout run is the first executable re-derivation of that base fact:
  red for substance (stale row), not red for a broken harness (could-not-evaluate). "Reproduce
  exactly" therefore holds for the facts-as-executable; it cannot hold for the calibration row's
  cited value, because that citation is itself stale at base — which is what C1 repairs.
- The git-independent control behaves identically in both fixtures, confirming the export route
  only breaks git-dependent arms.

## Cost and fragility of the checkout route

- Cost: `git clone --shared --no-checkout` + detach checkout took **1.36 s** wall (shared
  alternates, no object copy). Worktree materialization is the real cost: **38,743 files,
  ~501 MB** (co measured 506 MB including the tiny shared `.git`; the export is also ~501 MB /
  38,743 files). Cleanup is a plain `rm -rf` of the scratch tree (~1 GB total here).
- Shared-object dependence: `co/.git/objects/info/alternates` points at
  `/home/vgpnk/Projects/shokunin/kama-shokunin/.git/objects`. The checkout breaks if the lane
  repo is relocated or garbage-collects; fine for a probe (scratch lifetime), wrong for anything
  long-lived — use a full clone there.
- Branch-ref fragility (precision note): the gate selftest's `lane-tip` arm follows the repo's
  `master` ref, not the checked-out commit — in the checkout detached at 6035e952 it measured the
  lane's live master `0e14facd0c61` (`registered 79 unregistered 0 defective 0`). Any fact command
  that dereferences a branch measures the moving lane tip, not the frozen base, inside a shared
  clone. The newest-closure counter was correctly pinned (population from the checkout's
  `git ls-tree HEAD` at 6035e952; members end at round-69). A frozen-base harness should pin
  every git access to the checked-out rev (`HEAD`/`--rev`), never to a branch name.
- Fixtures stayed clean through all runs: `CO_DIRTY=0` after; export file count unchanged at
  38,743; the lane gained nothing from this seat (status composition unchanged; the two modified
  tracked files, PROVINCE.md/SCORECARD.md, are the wave's own in-flight edits, present before my
  first command).

## What this probe did NOT verify

- A lane-native run of the two commands at 6035e952 (the lane worktree has moved to 0e14facd with
  in-flight edits, so no lane-native base run exists to diff against). Corroboration for the
  base values is the committed receipt `measured/before/reconciler-at-base.out`, which agrees
  with the checkout outputs on every overlap.
- The full untruncated EX01 dispatch item text (its trailing sentence about the calibration fact
  was cut in display; the measured export behavior — exit 2 on `git ls-tree` rc=128 — is
  [INFERENCE]-consistent with the truncated remainder).
- `gate-registry-check.py --rev 6035e952` registry counts at base (out of milestone scope; the
  selftest arm measured master).

No tool installs (python3 3.14.8, git 2.56.0 already present; tooling directive unused). No lane
bytes proposed for landing — this seat returns evidence only; receipts: `probe.md`, `report.md`,
and the trailer copy `.ufo/waves/round-70/w1/out/RVW02HarnessProbe.md`.
