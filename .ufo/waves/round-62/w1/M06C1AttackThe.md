# M06C1AttackThe — C1 teardown mutation probe

## Setup and baseline

- Frozen tip inspected: `65d7cad0fce90e34de37527cde22e97b63b118bf`.
- Loaded `tools/round62-c1-counter.py` from `git show master:...` into the isolated scratch harness, without importing the mutable worktree version.
- Used the committed live receipt shape copied from `/fast/scratch/hyaku/kama-r62/measure/c1b/receipt.json`; its actual teardown was `child_pre_dead=false`, `port_closed=true`, `returncode=0`, `sigterm_sent=true`. Pinned nonce to its recorded nonce and supplied an equivalent live witness shape to exercise `score()`.
- The receipt as captured has an extra legacy `checks.hold_released` entry; frozen `grade()` conditionally emits `hold_released` only if present in checks, so this extra key causes `unexpected-checks` and the unmodified receipt scores `met=false`. For the teardown-specific evaluation below, removed only this extra check key to align the captured receipt with the frozen counter schema. No other receipt bytes/fields were modified for pristine.

## Mutations and actual score outputs

Verdicts below are from `score()` (`ACCEPTED` iff `met=true`); the requested claim concerns returncode and SIGKILL evidence.

| Receipt | Verdict | `score()` |
|---|---|---|
| pristine normalized receipt, returncode=0 | ACCEPTED | `{'met': True, 'alltrue': True, 'verdict_ok': True, 'live': True, 'inconsistent': []}` |
| returncode=0 | ACCEPTED | `{'met': True, 'alltrue': True, 'verdict_ok': True, 'live': True, 'inconsistent': []}` |
| returncode=-15 | ACCEPTED | `{'met': True, 'alltrue': True, 'verdict_ok': True, 'live': True, 'inconsistent': []}` |
| returncode=-9 | REJECTED | `{'met': False, 'alltrue': False, 'verdict_ok': True, 'live': True, 'inconsistent': ['teardown_clean']}` |
| SIGKILL claim: returncode=-9, `sigterm_sent=false`, `pdeathsig=null` (absent evidence) | REJECTED | `{'met': False, 'alltrue': False, 'verdict_ok': True, 'live': True, 'inconsistent': ['teardown_clean']}` |
| SIGKILL evidence absent but forged returncode=0 | ACCEPTED | `{'met': True, 'alltrue': True, 'verdict_ok': True, 'live': True, 'inconsistent': []}` |

The last case demonstrates the counter does not inspect `sigterm_sent`/`pdeathsig` evidence at all: the teardown predicate accepts returncode 0 regardless of a receipt's claim of SIGKILL or missing pdeathsig evidence. However, the exact requested family mutant `returncode=-9` is rejected by the frozen score function. This is an evidence-insensitivity observation, not a successful `returncode=-9` falsification of the specified teardown outcome.

## Scope / cleanup

No lane source, Git index, lane jj state, fleet repo, or sibling files were modified. No tools installed. Scratch used: `/fast/scratch/hyaku/kama-r62/w/M06C1AttackThe`; receipt was available at the shared measurement location and the copied input was used only within scratch. The scratch directory was removed before reporting.

Counter/tally output: returncode 0 ACCEPTED; -15 ACCEPTED; -9 REJECTED; SIGKILL/-9 with pdeathsig absent REJECTED; SIGKILL evidence absent forged as returncode 0 ACCEPTED.
