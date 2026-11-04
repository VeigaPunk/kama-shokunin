# MT01Mutation — kama r79 w1 mutation-test report

Seat item: mutation-test the new class (C3) and the new gate arm (C2 arm 10); five assigned
mutants, each must be caught by the shipped counter/selftest of its owner. Judged on:
operability. Lane bounds respected: leaf seat, no subagents, no lane writes, no scored gate
run (selftest mode only), no commits.

## Verdict: 5 built / 5 KILLED / 0 survived / 0 inconclusive — counters hold

Full per-mutant diffs, killer commands, output lines and restoration hashes:
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/MT01Mutation/mutants.md`.
Raw receipts: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/MT01Mutation/logs/`
(`pristine-*.log`, `mut*-*.diff`, `mut*-*.log`, `census-midflight.diff`).

| Mutant | Point (scratch clone only) | Killer command (cwd scratch clone) | Exit | Killing output line |
|---|---|---|---|---|
| A: `registered=yes` for every model listener | `kama-probe.sh` `classify_registration` | `TMPDIR=$S python3 tools/round79-unregistered-census.py --repo .` | 1 | `UNREGISTERED_CENSUS port=38257 unregistered=0 governed=0 class_missing=0 rows=1` (+ live `governed=8 unregistered=0 ports=-`) |
| B: summary keys present, column omitted | `kama-probe.sh` `cmd_listeners` | same | 1 | `UNREGISTERED_CENSUS port=51381 unregistered=0 governed=0 class_missing=1 rows=1` |
| C: registry port extraction reads column 3 not 4 | `kama-probe.sh` `read_registry_ports` | same | 1 | `UNREGISTERED_CENSUS port=48297 unregistered=0 governed=0 class_missing=0 rows=1` |
| 4: arm 10 runs only the first instrument | `pre-report-gate.py` `_round78_instruments` | `TMPDIR=$S python3 tools/pre-report-gate.py --selftest` | 1 | `PRE_REPORT_SELFTEST pass=23 fail=3` + `PRE_REPORT_SELFTEST_FAILED round78-instruments-red,round78-instruments-green,round78-instruments-malformed` |
| 5: arm 10 treats nonzero exit as pass | `pre-report-gate.py` `_round78_instruments` | same | 1 | `PRE_REPORT_SELFTEST pass=5 fail=21` + `…round78-instruments-green` among 21 failed labels |

Pristine baselines (pre-mutation, detectors must pass):
- `python3 tools/pre-report-gate.py --selftest` → `PRE_REPORT_SELFTEST pass=26 fail=0`, exit 0
  (`logs/pristine-gate-selftest.log`).
- `python3 tools/round79-unregistered-census.py --repo .` →
  `UNREGISTERED_CENSUS port=59865 unregistered=1 governed=1 class_missing=0 rows=1`, exit 0
  (`logs/pristine-census.log`).
- After the last restore, the restored clone re-ran both detectors green
  (`logs/pristine-final-gate-selftest.log` → `pass=26 fail=0`;
  `logs/pristine-final-census.log` → `port=39033 unregistered=1 governed=1 class_missing=0 rows=1`),
  and every per-mutant restore was verified by sha256 against the pristine snapshot.

## Environment and provenance notes

- Scratch root `/fast/scratch/hyaku/kama-r79/MT01Mutation` (created, `TMPDIR` pointed at it,
  deleted at yield). Mutants applied only inside `$S/clone` =
  `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin` (clone HEAD
  `f7442dea53bd8f474293a2252437b5d869801f49`); `git -C "$D" rev-parse --show-toplevel` ==
  `$D` verified at creation. The lane repo was never mutated (read-only git only).
- All five mutant targets were absent at seat start (base gate = 9 arms, probe without the
  class, no census counter). Polled the lane per the attack-seat rule (`sleep 30`); both
  build modules landed ~6 min in, as uncommitted working-tree bytes. Synced byte-exact into
  the clone and graded on hash-settled snapshots:
  probe `0943fb461d02…`, census `25daa98937ee…`, gate `9b2ff3b453e2…`.
- One mid-flight edit of `tools/round79-unregistered-census.py` was observed one second
  after the first sync (`a193b0bc…` → `25daa989…`: added `--port` restriction to the two
  fixture legs; `logs/census-midflight.diff`); grading was redone on the settled bytes.
  L1 subsequently committed exactly the graded bytes:
  `5ac1a8dd94b151548b5d5a6256938da381366e20` (lane master `f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f`
  at report time; `git status --porcelain -- tools/` clean).
- No tools installed or upgraded (none needed; python3/bash/git only).
- Scored gate mode was NOT run (L1-only, per seat rules); gate mutants were killed by the
  selftest's own scored fixtures as assigned.

## Coverage finding

None — no surviving mutant, so no coverage hole to report against the frozen C2/C3
predicates. The kill quality is meaningful, not nominal: mutants A–C were each caught by a
different assertion leg of the C3 counter (negative registry leg, class-presence leg, and
positive registry leg respectively), and mutants 4–5 were caught by distinct arm-10 wiring
cases (red/green/malformed composition vs exit-code polarity), including fleet-wide
detection via `evaluate()` composing all ten arms (mutant 5: `pass=5 fail=21`).
