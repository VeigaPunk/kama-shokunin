VERDICT: confirm - crash and silent exit-one check stubs are not detections.

Axes: calibration (7) and operability (8). Tested calibration's error-versus-verdict rule.
Revision: `37bd4c5bd456a2f8a54d3312c28495c321715856`.

| `--check` stub | Stub exit / observation | F0 and suite result | F1-F17 |
|---|---|---|---|
| Traceback (`raise RuntimeError`) | exit 1; uncaught traceback on stderr | F0 not detected; suite INVALID, exit 2 | Not run / not classified |
| Silent `sys.exit(1)` | exit 1; no output | F0 not detected; suite INVALID, exit 2 | Not run / not classified |

Observed harness diagnostic for both runs: `fault-controls: suite INVALID — positive control F0 failed: check exited 1 (wanted 0); stdout[:120]=''`. The command wrappers used to print the child status exited 0; the harness's observed exit was 2. There were no ordinary per-fault DETECTED/ACCEPTED rows because the F0 gate returned before running F1-F17. F0's `detected=false` means the honest positive control did not pass (the doc calls a failed F0 “accepted”; it is not a detected fault).

Commands and observed exits:
- `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r20-FaultControlsCrash/lane && git -C /tmp/kama-r20-FaultControlsCrash/lane checkout -q 37bd4c5bd456a2f8a54d3312c28495c321715856 && git -C /tmp/kama-r20-FaultControlsCrash/lane rev-parse HEAD` — printed the revision above; exit 0.
- `python3 /tmp/kama-r20-FaultControlsCrash/crash-check.py` — printed the uncaught `RuntimeError` traceback; stub exit 1 (capture shell exit 0).
- `python3 /tmp/kama-r20-FaultControlsCrash/silent-check.py` — no output; stub exit 1 (capture shell exit 0).
- `python3 /tmp/kama-r20-FaultControlsCrash/lane/tests/probe-verdicts/fault-controls.py --check /tmp/kama-r20-FaultControlsCrash/crash-check.py` — observed F0 diagnostic above; harness exit 2 (capture shell exit 0).
- `python3 /tmp/kama-r20-FaultControlsCrash/lane/tests/probe-verdicts/fault-controls.py --check /tmp/kama-r20-FaultControlsCrash/silent-check.py` — observed F0 diagnostic above; harness exit 2 (capture shell exit 0).

Rule and evidence at the pinned revision (`tests/probe-verdicts/fault-controls.py`): lines 16-23 define DETECTED as exit 1 plus parseable JSON, all faulted rows `passed: false`, and the target conjunct; they define ACCEPTED to include a traceback/non-JSON stdout. Lines 701-709 reject the wrong exit and non-JSON stdout. Lines 975-980 make a failed positive-control F0 return suite code 2 before ordinary faults run. Thus no crash counts as detection: exit 1 alone is insufficient, and these crashes never reach fault grading.
