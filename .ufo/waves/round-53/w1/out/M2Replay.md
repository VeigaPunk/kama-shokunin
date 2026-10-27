Verdict: 10 mutants killed by selftest; no mutant killed by C1; 6 survived both detectors; 3 were equivalent on the frozen build input.

## Evidence

Mutation base was the exact build-commit blob `c22602bd8d83ab26349d1087e916ca537ee4f9d1:tools/kama-live-replay.py`, SHA-256 `6c0bfbdfa586e0beb47a8ba1f1c617b9db295dfe4f7357299493e04989e98102` (881 lines). This differs from the later lane worktree file (`b89b95e...`; 929 lines), so all tests and fixtures used the pinned build blob.

Pristine detector controls:
- `python3 pristine.py --selftest --scratch .../selftest-pristine`: `KLR_SELFTEST pass=43 fail=0`, exit 0. Full output: `out/M2Replay/selftest-pristine.out`.
- Frozen C1 counter at the base tip: `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True`, exit 0. It verified 8 archive executable ranges and 13 root-owned host files per run; teardown succeeded. Output: `out/M2Replay/counter-pristine.out`.

## Mutant results

Each mutant was a one-point change; each ran `--selftest --scratch` separately. Per-mutant output is in `out/M2Replay/selftest-mNN.out`; full mutation inventory is `out/M2Replay/mutations.json`.

Killed by selftest (10):
- m01 name membership inverted — failures: `match`, `v5-match`, `code-own-members`, `witness-passthrough`.
- m02 regular-file gate inverted — same four failures.
- m06 relpath removed — same four failures.
- m07 digest comparison inverted — `match`, `v5-match`, `code-digest-differs`, `code-own-members`, `witness-passthrough`.
- m08 uid test inverted — `match`, `v5-match`, `code-foreign`, `code-own-members`, `witness-passthrough`.
- m09 opened test inverted — `match`, `v5-match`, `code-own-members`, `witness-passthrough`.
- m10 opened requirement removed — `code-unopened`.
- m13 read gate inverted — `match`, `v5-match`, `code-own-members`, `witness-passthrough`.
- m14 code mismatches not extended — `code-absent`, `code-digest-differs`, `code-foreign`, `code-not-a-member`, `code-unopened`, `code-no-archive-library`.
- m17 empty digest substituted — `match`, `v5-match`, `code-own-members`, `witness-passthrough`.

Selftest survivors run through the frozen C1 counter in a fixture clone at the base commit (all exit 0, `met=True`): m03, m04, m05, m11, m12, m15, m16, m18, m19. Their counter outputs are `out/M2Replay/counter-mNN.out`; the counter output was `met=True` for all nine. The pristine counter also passed, so results are conclusive for the bounded detector.

Equivalent on the exercised frozen archive and consumers (3):
- m03 drops the name filter: the verifier only looks up names derived from the under-tree mappings, so hashing additional regular archive members does not change looked-up digests or results.
- m12 includes outside-tree paths in `want`: for this archive, their `../...` names do not name archive members; none is subsequently looked up as an under-tree mapping.
- m18 records `e["sha256"]` instead of the archive digest only in the branch that has already established equality, so returned member values are identical.

Survived (6), each with a distinguishing proposed selftest case executed against pristine and mutant function bytes by `out/M2Replay/killcases.py`:
- m04, root prefix without `os.sep`: mapped archive library under tree plus root-owned host mapping named `<tree>-evil/libhost.so`. Pristine returns verified with host entry; mutant flags `not-a-member`.
- m05, root without `realpath`: symlink tree path and a mapping using the resolved path. Pristine verifies the archive member; mutant treats it as foreign and fails.
- m11, no-archive-library check disabled: only a root-owned host mapping. Pristine reports `code-mapping:no-archive-library`; mutant returns verified.
- m15, `own_code.verified` forced true: a mapping with a wrong digest. Pristine returns verified false; mutant true while retaining digest mismatch problems.
- m16, malformed/absent mapping branch forced verified true: pass absent `code_mappings`; pristine returns false, mutant true.
- m19, host sorting removed: two root-owned host entries in reverse lexical order. `own_code.host` order differs between pristine and mutant.

These are function-level distinguishing cases, not additions to the frozen selftest suite. Exact outputs: `out/M2Replay/killcases.py` can be rerun while scratch exists; outputs were captured in this report. No C1 counter killed a mutant because its healthy replay inputs do not exercise those exceptional inputs/order conditions.

Restoration: the lane was never edited. The fixture clone is disposable and scratch was removed. Before cleanup, the pinned pristine copy remained SHA-256 `6c0bfbdfa586e0beb47a8ba1f1c617b9db295dfe4f7357299493e04989e98102`; the lane worktree remained `b89b95eeb826cdba7d3e65fc2e034593cda5b38ae508faff5f163128674e1291`. No `llama-server` process started by this seat remained.

Written artifacts:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/M2Replay.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/M2Replay/`
