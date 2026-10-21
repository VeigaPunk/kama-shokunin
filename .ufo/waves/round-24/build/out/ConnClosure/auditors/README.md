# Auditor blobs used by ConnClosure (read-only copies, no production edits)

| file | provenance | sha256 (first 16) |
|---|---|---|
| `base.py` | `git show 0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py` (the r23 base the closure ruled on) | `da5041a8191e0e6` |
| `frozen.py` | `git show 4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py` (the r22 arm the closure used as the correct verdict) | `09ecd63bdc3a5be5` |
| `cand.py` | `git show ed1cc3a342bd801fe2d0f54f7ba2eb4ca42d5f05:tools/report-landing-audit.py` (the pinned r24 candidate) | `ea51bc35b71ac09f` |
| `cand_allroots.py` | `cand.py` with `missing_reachable` re-rooted at `--all` (refs only) instead of every present commit/tree/tag — the mutant used to show the root set decides the verdict | `e9790358546a974` |
| `cand_pm07.py` | `cand.py` with the `promisor-mutants.py` PM07 alternative-1 transform applied (`roots.append("--all")`) | — |

`cand_allroots.py` and `cand_pm07.py` are diagnostic mutants written by this
seat in its own scratch; they are not lane production files and are not
proposals for the candidate.
