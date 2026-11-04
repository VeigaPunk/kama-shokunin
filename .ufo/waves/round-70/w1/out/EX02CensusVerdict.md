# EX02CensusVerdict — scoped findings (round 70, lane kama, C2 operability)

Claim C2 repaired in candidate bytes: a census member that did not run is no
longer a pass. Full evidence in
`.ufo/waves/round-70/w1/out/EX02CensusVerdict/` (`report.md`, `demo.md`,
`round65-host-census.py`, `diff.patch`).

- Frozen control on candidate bytes: `REFUSED_MEMBER_CONTROL
  refused_fixture_exit=1 allpass_fixture_exit=0`, control exit 0 (base bytes
  scored (0, 0), fail-open). Refused fixture verdict carries `not_evaluated=1`.
- Real census on this host with candidate bytes, C1 still red:
  `HOST_CENSUS pass=21 fail=1 not_evaluated=0 waived=0 total=22
  tierA_fail=1 tierB_fail=0`, exit 1 — the reconciler arm ran and failed, so
  it stays `fail`; waivers cannot cover it (stderr warning names it).
- Waiver path: exact-name `--waive` on a refused member keeps its reason on
  its own line with `[waived]`, verdict shows `not_evaluated=1 waived=1`,
  exit 0 only then.
- Kill rule: an always-exit-1 shim scores `allpass_fixture_exit=1` → control
  exits 1 (rejected); the counter is the pair (refused=1, allpass=0).
- Member list, markers, tiers, budget byte-identical to base
  (sha256 base `463899182af0…` → candidate `a82cad11d777aa4b…`; diff hunks
  touch only docstring + `main()`; `git apply` on pristine base reproduces
  the candidate bytes exactly).
- L1 lands `round65-host-census.py` → `tools/round65-host-census.py` (or
  `git apply diff.patch` at lane root); then re-run the control on the landed
  path. Not verifiable by this seat: the landed-path invocation (lane
  read-only; demo used the control's own LANE-substitution move) and the C2
  green census line (blocked on C1; separability note in freeze.txt applies).
- Hygiene: no tool installs; no git mutations; scratch
  `/fast/scratch/hyaku/kama-r70/EX02CensusVerdict/` deleted before yield;
  only wave-tree writes are this file and the seat out dir.
