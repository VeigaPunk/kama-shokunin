# RVW02HarnessProbe — report (round 70, lane kama, axes operability + calibration)

Seat: advisory leaf reviewer/probe. Read-only on the lane; scratch
`/fast/scratch/hyaku/kama-r70/RVW02HarnessProbe/` created and deleted (see Cleanup). No subagents
dispatched. No tools installed (python3 3.14.8, git 2.56.0, tar present; the tooling directive was
not used — nothing to record).

## What I did

Hypothesis under test: "a checkout of the lane at the tip (with `.git`) makes BOTH git-dependent
`## Axes` facts reproduce exactly, while a git-less export cannot."

1. Built two fixtures of frozen base `6035e952c2521999e192d6f236331f265ac98392`:
   - `export/` — git-less: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive 6035e952 | tar -x -C export` → 38,743 files, no `.git`, `git rev-parse --show-toplevel` → `fatal: not a git repository`, exit 128.
   - `co/` — `git clone --quiet --shared --no-checkout <lane> co && git -C co checkout --quiet --detach 6035e952`; host-guard assert `git rev-parse --show-toplevel` = the co dir (passed); worktree clean (`status --porcelain` = 0); `.git` present with `objects/info/alternates` → lane `.git/objects`. Wall time 1.36 s; worktree ≈506 MB.
   - Tool bytes identical in both (`sha256sum`): gate-registry-check `ef8d84a2…`, round69-newest-closure-counter `edf6c49a…`, pin-watch `37040977…`.
2. Ran, with `bash -c`, in each fixture (cwd = fixture root; full transcripts in `probe.md`):
   - `python3 tools/gate-registry-check.py --selftest`
   - `python3 tools/round69-newest-closure-counter.py --since-round 63`
   - `python3 tools/pin-watch.py selftest` (git-independent control)
3. Read base `## Axes` citations from `git show 6035e952:SCORECARD.md` (scratch copy, 509,708 bytes) to pin what "reproduce exactly" means.

## Results (last stdout line + exit)

| Fact | export (git-less) | checkout (with .git) |
|---|---|---|
| operability: `gate-registry-check.py --selftest` | `GATE_SELFTEST pass=6 fail=1`, exit 1 — `FAIL lane-tip: cannot resolve master: fatal: not a git repository` | `GATE_SELFTEST pass=7 fail=0`, exit 0 — `PASS lane-tip 0e14facd0c61: exit=0 line='registered 79 unregistered 0 defective 0'` |
| calibration: `round69-newest-closure-counter.py --since-round 63` | `COULD_NOT_EVALUATE git ls-tree --name-only failed (rc=128): fatal: not a git repository`, exit 2 | `NEWEST_CLOSURE newest=corpus/lessons/round-69-verifier-spotcheck.md date=2026-11-01 round=69 row_names=corpus/lessons/round-68-verifier-spotcheck.md row_current=false` + `STALE_CALIBRATION`, exit 1 (population `rounds>=63 members=7`) |
| control: `pin-watch.py selftest` | `selftest pass=9 fail=0`, exit 0 | byte-identical, exit 0 |

## Verdict

**SUPPORTED.** The checkout executes both git-dependent facts; the export cannot (both fail
closed: exit 1 and exit 2, never 0 — no fail-open). Precision for C1 judgment:

- The operability fact reproduces its cited `## Axes` value exactly in the checkout:
  `GATE_SELFTEST pass=7 fail=0`, exit 0.
- The calibration fact reproduces the tree's true base verdict exactly: `row_current=false`,
  exit 1, `STALE_CALIBRATION`. The base row's citation (`row_current=true`, exit 0) is stale at
  base — the frozen C1-before condition, independently corroborated by
  `.ufo/waves/round-70/measured/before/reconciler-at-base.out` ("no stdout line ==
  'NEWEST_CLOSURE … row_current=true' (exit 2)" via the export route; "closure_ptr: calibration
  row latest outside closure is round-68; newest at tip is round-69"). The checkout turns that
  base red from could-not-evaluate (exit 2) into an honest measured verdict (exit 1) — exactly
  what a harness moved to a tip checkout gains.
- Fragility for the harness author: the gate selftest's `lane-tip` arm follows the branch ref —
  in the checkout detached at 6035e952 it measured live master `0e14facd0c61` (registered 79).
  Branch-dereferencing arms measure the moving lane tip, not the frozen base; pin git access to
  the checked-out rev (`HEAD`/`--rev`). The counter did so (population from `git ls-tree HEAD`
  at 6035e952). Also: `--shared` alternates break if the lane is relocated/gc'd — fine for a
  probe, use a full clone for anything long-lived. Cost: clone 1.36 s, ~500 MB / 38,743 files of
  worktree per fixture.

## What I could NOT verify

- A lane-native run of the two commands at 6035e952: the lane worktree had moved to
  `0e14facd0c619f45a6461821d2bd80ddac9855b1` with in-flight wave edits (` M PROVINCE.md`,
  ` M SCORECARD.md`, plus round-70 untracked files — present before my first command, unchanged
  in composition after). No lane-native base run exists to diff against; corroboration is the
  committed reconciler receipt above.
- The untruncated EX01 dispatch item string (display-truncated JSON); the truncated calibration
  sentence is inferred from measured behavior [INFERENCE].
- `gate-registry-check.py --rev 6035e952` base registry counts (out of milestone scope).

## Bytes/paths for the L1

No lane file changes are proposed — this seat returns evidence only. Receipts to land (already
written by this seat, no L1 action needed beyond awareness):

- `.ufo/waves/round-70/w1/out/RVW02HarnessProbe/probe.md` — protocol, full command outputs, verdict, cost/fragility.
- `.ufo/waves/round-70/w1/out/RVW02HarnessProbe/report.md` — this report.
- `.ufo/waves/round-70/w1/out/RVW02HarnessProbe.md` — trailer-path copy of this report.

Pasteable one-line reproduction of the headline result:

    D=$(mktemp -d /fast/scratch/hyaku/kama-r70/rvw02-repro.XXXX) && git -C /home/vgpnk/Projects/shokunin/kama-shokunin clone -q --shared --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin "$D/co" && git -C "$D/co" checkout -q --detach 6035e952 && (cd "$D/co" && bash -c 'python3 tools/gate-registry-check.py --selftest'; echo "gate_exit=$?"; bash -c 'python3 tools/round69-newest-closure-counter.py --since-round 63'; echo "counter_exit=$?"); rm -rf "$D"

Expected: `GATE_SELFTEST pass=7 fail=0` / `gate_exit=0`; `NEWEST_CLOSURE … row_current=false` +
`STALE_CALIBRATION` / `counter_exit=1`.

## Cleanup

`/fast/scratch/hyaku/kama-r70/RVW02HarnessProbe/` (export 501 MB, co 506 MB, SCORECARD copy)
deleted after the last command; nothing under /tmp was written.
