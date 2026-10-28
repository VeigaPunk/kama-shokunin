# EX04ExistingTests — harm regression of existing gates at tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09

Method: `git clone -q --shared` of the lane into `/fast/scratch/hyaku/kama-r63/w/EX04ExistingTests/clone` (HEAD verified = tip; toplevel asserted), TMPDIR pointed at seat scratch, each gate run in the clone, exit code captured. Clone `git status --short` stayed empty after test-snapshot.sh (0 lines). No tools installed. Receipts: `.ufo/waves/round-63/w1/out/EX04ExistingTests/<gate>.{out,rc}` (large outputs tail-60, long lines cut to 2000 chars).

| gate | exit | tail line | SCORECARD claim | diff |
|---|---|---|---|---|
| `bash tools/test-snapshot.sh` | 0 | `RESULT pass=30 fail=0` (30 PASS lines, 0 FAIL) | `RESULT pass=30 fail=0` (head row 14) | none |
| `python3 tools/pin-watch.py selftest` | 0 | `selftest pass=9 fail=0` | `selftest pass=9 fail=0` | none |
| `python3 tools/report-landing-audit.py --selftest` | 0 | `selftest cases=79 failed=0` | `selftest cases=79 failed=0` | none |
| `python3 tools/sources-append-only.py --selftest` | 0 | `45/45 selftest cases passed` | `45/45 selftest cases passed` | none |
| `python3 tools/capability-repertoire-audit.py --selftest` | 0 | `CAP_SELFTEST pass=2 fail=0` | `CAP_SELFTEST pass=2 fail=0` (row 18) | none |
| `python3 tools/kama-ollama-evidence.py --selftest` | 0 | JSON `"passed": 51, "failed": 0, "total": 51` | 51 passed / 0 failed (§Round-14, line ~507) | none |
| `python3 tools/gguf-identity.py --selftest` | 0 | JSON `"failed": [], "passed": 30, "status": "passed"` (schema gguf-identity-selftest/v2) | GGUF selftest 30/30 (§ ~line 960) | none |
| `python3 tools/instrument-agreement.py --selftest` | 0 | `IA_SELFTEST pass=4 fail=0` | `IA_SELFTEST pass=4 fail=0` (row 18) | none |

Finding: no difference between measured output and any SCORECARD head claim; no harm regression from the round-63 freeze/amendment commits on these eight gates. Limit: the live-endpoint rows in SCORECARD are not exercised here (no live runs); ollama/gguf counts compared against body-section claims, since the head rows carry no count for them.

Tally: `gates=8 exit0=8 nonzero=0 scorecard_diffs=0`
