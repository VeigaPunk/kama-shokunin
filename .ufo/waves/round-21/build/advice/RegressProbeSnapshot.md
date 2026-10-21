VERDICT: confirm - all requested probes pass identically on the draft and round-start baseline.

Axes:
- Operability: the snapshot fixture suite reports 30 passes and no failures on both revisions.
- Calibration: outputs and exits for the selected probes match between draft `a29bb84abbb8b4d328f5970a89e448330a3a42ac` and baseline `7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d`.

Executed in isolated scratch worktrees at those exact revisions; each command's observed exit was printed as `OBSERVED_EXIT`:

| Command | Baseline stdout evidence / exit | Draft stdout evidence / exit |
|---|---|---|
| `bash tools/test-snapshot.sh` | `RESULT pass=30 fail=0`; 0 | `RESULT pass=30 fail=0`; 0 |
| `python3 tools/sources-append-only.py --help` | Usage/options printed, including `--selftest`; 0 | Same usage/options; 0 |
| `python3 tools/sources-append-only.py --selftest` | `42/42 selftest cases passed`; 0 | `42/42 selftest cases passed`; 0 |
| `python3 tools/kama-ollama-evidence.py --selftest` | JSON: schema `kama-ollama-evidence-selftest/v1`, `finding_id=clean`, `readiness=unknown`, scope `offline-captures-not-runtime`, `passed=51`, `failed=0`, `total=51`; 0 | Same JSON summary; 0 |

Cross-revision source comparison: `git diff --name-status 7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d a29bb84abbb8b4d328f5970a89e448330a3a42ac -- tools/test-snapshot.sh tools/sources-append-only.py tools/kama-ollama-evidence.py tools/kama-probe.sh tests/ollama-evidence` produced no stdout and exited 0.

Risk/limit: these are hermetic fixture and offline-capture checks; the Ollama evidence selftest explicitly reports readiness `unknown` and scope `offline-captures-not-runtime`. No live endpoint health was measured. No tools were installed. Scratch checkout removed (`scratch_removed=yes`). No lane source files were changed; this advisory report is the scoped deliverable.
