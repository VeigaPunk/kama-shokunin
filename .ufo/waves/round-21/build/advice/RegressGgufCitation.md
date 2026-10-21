VERDICT: confirm - all result summaries match R20; only clone-root paths differ

## Axes
- Result stability: fixture/citation counts, statuses, and selftest case totals.
- Path portability: absolute paths embedded in JSON and the selftest diagnostic.

## Run context
- Isolated clone HEAD: `a29bb84abbb8b4d328f5970a89e448330a3a42ac` (confirmed by `git rev-parse HEAD`, exit 0).
- Baseline: `.ufo/waves/round-20/runs/9add96e4/`; `commands.json` names measured commit `9add96e462e62dc5141cd02730b7a699268b3513`.

## Requested commands
- `python3 .ufo/waves/round-20/c2/measure.py --json` — exit 0; `status=pass`; `base_revision=37bd4c5bd456a2f8a54d3312c28495c321715856`; 23/23 fixtures passed, 0 mismatched, 0 snapshot-tampered, 0 unavailable; model observed; oracle and receipt evidence validated; receipt status `engine-agreement`. Baseline has the same summary and base revision.
- `python3 tools/gguf-identity.py --selftest` — exit 0; 30/30 passed, no failures, status `passed`. Baseline stdout is identical.
- `python3 tools/citation-provenance.py --json` — exit 0; required/found/verified `17/17/17`; docs unreadable 0, missing 0, mismatch 0, off-ref 0. Baseline counts and record digests/statuses match.
- `python3 tools/citation-provenance.py --selftest` — exit 0; `selftest: ok (24 cases)`. Baseline stdout is identical.

## Differences against retained R20 runs
- `gguf-measure.stdout` comparison: diff exit 1; the 11 changed JSON path values point to the isolated clone instead of `/home/vgpnk/Projects/shokunin/kama-shokunin`; all measured values and statuses match.
- `citation-count.stdout` comparison: diff exit 1; all 17 changed `documents[]` paths point to the isolated clone; counts, digests, statuses, and other fields match.
- GGUF and citation selftest stdout comparisons: diff exit 0 (identical).
- Citation selftest stderr still reports the deliberate-looking missing `absent.md` path, but its generated temp directory differs (`fu99gs4l` in R20 vs `f30pilkm` now); both runs exit 0 and pass all 24 cases.

## Risks / blockers
- [INFERENCE] Bytewise comparisons of these path-bearing outputs need repository-root normalization to distinguish checkout relocation from result changes.
- No blocker. No lane code files changed and no tools installed.