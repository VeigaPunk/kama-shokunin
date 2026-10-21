VERDICT: confirm - the silent-exit control killed the weakened classifier; pristine and exact-restored detectors passed.

Axes: C1 calibration (error versus observed rejection), detector specificity, private-copy restoration. No round-wide judgment.
Scope: one mutation of copied current grid bytes under `/tmp/kama-r20-MutGridSilentExit`; no Git/JJ operation or lane-source mutation.
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.

## Mutant and expected detector
- Copied `tests/llamacpp-live/install-tree-grid.py`, adjacent `check-receipt.py`, and pinned `registry/error-injection-fixtures/grid-gate.py` into the private scratch.
- Changed only scratch `install-tree-grid.py:87`: `elif code == 1 and out.startswith("INVALID "):` → `elif code == 1 and (out.startswith("INVALID ") or not (out or err)):`.
- This claims rejection for exit 1 with both streams empty, retaining genuine INVALID handling.
- Existing control: `install-tree-grid.py:268,283-285` requires silent exit 1 to produce grid exit 2, baseline VALID, row error, rejected=0, errors=1; `:293-296` fails the selftest otherwise.
- Pinned oracle: `registry/error-injection-cells.json:3`; frozen/current evidence `error-pair.stdout:24-32` under `.ufo/waves/round-20/runs/0957ce61/` records rejected→error for this named cell.
- Expected kill: the mutated selftest exits 1 naming silent exit 1; the genuine-INVALID positive control remains a rejection.

## Exact bounded commands
The unchanged private detector ran the selftest and both named CLI cells each phase, capturing raw exit/stdout/stderr; each child had a 30-second timeout.
Child environment: PATH=/usr/bin:/bin; HOME=/tmp/kama-r20-MutGridSilentExit; TMPDIR=/tmp/kama-r20-MutGridSilentExit/tmp; LANG=C.UTF-8; PYTHONDONTWRITEBYTECODE=1, plus the indicated CENSUS_GATE_MODE.
```
/usr/bin/python3 -B /tmp/kama-r20-MutGridSilentExit/detector.py pristine
/usr/bin/python3 -B /tmp/kama-r20-MutGridSilentExit/detector.py mutated
/usr/bin/python3 -B /tmp/kama-r20-MutGridSilentExit/detector.py restored
```
Observed detector exits, respectively: **0, 1, 0**. Detector SHA-256: `6cab0103d25a0f06e3d58429e763d2d328664370415c39cc7a1638805a428ce2`.
Exact selftest command in all phases:
`/usr/bin/python3 -B /tmp/kama-r20-MutGridSilentExit/install-tree-grid.py --selftest`
Exact silent cell command in all phases:
`CENSUS_GATE_MODE=silent1 /usr/bin/python3 -B /tmp/kama-r20-MutGridSilentExit/install-tree-grid.py --gate /tmp/kama-r20-MutGridSilentExit/grid-gate.py --receipt /tmp/kama-r20-MutGridSilentExit/receipt.json --model-sha model --server-sha server --impl-sha impl --probe-sha probe --tool-sha tool --members libllama.so.0.7.0 --json`
The positive-control command was exactly the preceding command with `CENSUS_GATE_MODE=invalid` instead of `CENSUS_GATE_MODE=silent1`.

## Actual outputs
| Phase | Selftest exit | Silent cell exit / row / rejected / errors | Positive exit / row / rejected / errors |
|---|---:|---|---|
| Pristine | 0 | 2 / error / 0 / 1 | 0 / rejected / 1 / 0 |
| Mutated | 1 | 0 / rejected / 1 / 0 | 0 / rejected / 1 / 0 |
| Restored | 0 | 2 / error / 0 / 1 | 0 / rejected / 1 / 0 |
All six focused CLI runs reported baseline VALID and members=1. Silent gate rows had gate_exit=1 and empty stdout/stderr in all phases.
Pristine/restored silent grid stderr: `install-tree-grid: 1 member gate run(s) gave no verdict`; row error: `no verdict line for exit 1`. Mutated silent grid stderr was empty.
Mutated selftest stdout was empty; exact stderr: `SELFTEST FAIL silent exit 1: exit=0 baseline='VALID' row='rejected' rejected=1 errors=0`.
Pristine/restored selftest stdout: `selftest: genuine verdicts, absent/bad input, crash, silent exit 1, signal, unknown exit, post-INVALID tracebacks, stderr-only INVALID and timeout passed`; stderr empty.
Positive-control gate stdout in every phase: `INVALID synthetic mutant: 1 problem(s)`; gate_exit=1; both gate/grid stderr empty. This is an offline synthetic verdict control, not receipt authentication.
Mutation verdict: **KILLED**, not inconclusive: both unchanged-byte controls passed, the named silent control failed only after mutation, and the positive control stayed passing.

## Hashes, restoration and cleanup
Grid SHA-256 before / mutated / restored:
- `d9689c0718a6001f808c00c7b5318327e0757713033e9df04994687a422650c5`
- `0fc2eeeb65e58429c1aa192b410183a7299cd65ec46999c2aaf20fed7c44db14`
- `d9689c0718a6001f808c00c7b5318327e0757713033e9df04994687a422650c5`
Restored the original predicate before the restored detector. `cmp -s /tmp/kama-r20-MutGridSilentExit/install-tree-grid.py /tmp/kama-r20-MutGridSilentExit/grid-pristine.py` exited 0; a second cmp of lane grid versus pristine scratch exited 0 (`restored_bytes_equal=1`, `lane_bytes_unchanged=1`). Lane before/after SHA-256 matched the pristine hash above.
Fixture before/after SHA-256: `0e65e584fe9d7bda52af233c7fd189555d4314b1b7ae6267b12cbf1e2d3bbb5f`; synthetic receipt SHA-256: `be5c6161a2739d120d45a5aa90e3122bf94d8d07bbcb30a22f440f3d9b8377ab`.
Cleanup command: `rm -rf -- /tmp/kama-r20-MutGridSilentExit && test ! -e /tmp/kama-r20-MutGridSilentExit && printf 'scratch_removed=1\ncleanup_exit=0\n'` → exit 0; output `scratch_removed=1`, `cleanup_exit=0`.
No production/evidence/registry edits, installs/updates, services, model loads, or network calls. Only this assigned report persists.
Report: .ufo/waves/round-20/falsify/advice/MutGridSilentExit.md
