# M3Live — round-53 item: live-tool mutation test of `code_mappings()` and its receipt wiring

Verdict: **13 mutants of `tools/kama-llamacpp-live.py` `code_mappings()` (10) + receipt wiring (2, plus 1 extra hash-loop shape), anchored to the frozen build commit c22602bd8d83ab26349d1087e916ca537ee4f9d1: 8 killed by shipped detectors (3 by `--selftest`, 5 by the frozen C1 counter pipeline), 5 survived BOTH shipped detectors and were killed only by new seam cases — a concrete coverage gap in the round-53 selftest and the C1 counter; pristine baseline and restored-bytes runs both `met=True`; no mutant was left standing.**

## Scope and method

- Baseline: `git show c22602bd…:tools/kama-llamacpp-live.py`, sha256 `82b253e58ae75457b3dc81e6a7450510a50f815e3503bc6a2b61b7d1342b349d`, placed in a scratch lane layout (`tools/` + `registry/endpoint-consumers.tsv`; the selftest derives `LANE` from the script path — a bare copy fails with `SetupError: registry-unreadable`, which is an environment artifact, not a tool defect).
- Stage 1: `--selftest` on each of 12 primary mutants (exit 0 = survived, 1 + `kama-llamacpp-live selftest: AssertionError` = killed). All anchors applied with exact-count assertions (`mutate.py`, manifest in `out/M3Live/mutants/manifest.json`).
- Stage 2: for every stage-1 survivor, a `git clone --shared` fixture at c22602bd, the mutant committed with the fixture identity (`user.name=fx`), and the frozen counter run: `python3 tools/round53-replay-code-audit.py --repo <clone> --tip <mutant tip> --scratch <dir> --out <out>` (~16 s each, exit 0/1).
- Kill-site diagnosis for fixture-killed mutants: the replay `tools/kama-live-replay.py` run directly at the mutant commit (not frozen; diagnosis only — verdicts come from the frozen counter).
- Stage 3 (proposed killing cases): `harness.py` feeds `code_mappings()` fabricated `/proc/<pid>/maps` rows (patched `open` for the maps read only; real files, real `os.open/fstat/read`) — one case per stage-2 survivor.
- Restoration: pristine bytes restored in the fixture clone (commit 8d1d080a…), sha256 re-verified equal to the baseline blob, frozen counter re-run: `met=True`, exit 0.

## Results

Full table: `out/M3Live/verdicts.tsv`. Counter outputs: `out/M3Live/c1-*.out` (12 files). Selftest log: `out/M3Live/results-selftest.tsv`.

| Mutant (target) | selftest | frozen C1 at c22602bd | final |
|---|---|---|---|
| M01 perm filter (`'x' not in f[1]` dropped) | survived | `met=False` | KILLED — `code-mapping:foreign:<work>/download/stories260K.gguf:uid=1000` |
| M02 `/`-prefix check dropped | survived | `met=False` | KILLED — `code-mapping:unopened:[vdso]…`, `[vsyscall]` |
| M03 `/memfd:` skip dropped | survived | `met=False` | KILLED — `code-mapping:unopened:/memfd:llama-server (deleted):mapped-file-deleted` |
| M04 dedupe key `(path,dev,ino)`→`path` | survived | **`met=True` (survivor)** | KILLED only by seam case E |
| M05 `(deleted)` guard dropped | **killed** (AssertionError) | — | KILLED |
| M06 inode compare dropped | survived | **`met=True` (survivor)** | KILLED only by seam case A |
| M07 dev compare dropped for all uids | survived | **`met=True` (survivor)** | KILLED only by seam case B |
| M08 hash loop → `while False` | **killed** (AssertionError) | — | KILLED |
| M09 shrink check `!=0`→`<0` | survived | **`met=True` (survivor)** | KILLED only by seam case C |
| M10 `opened: True` dropped from success entries | **killed** (AssertionError) | — | KILLED |
| M11 wiring: `code_mappings` emptied | survived | `met=False` | KILLED — `own_code {'verified': False, 'members': {}, …}`, per-file "no entry" |
| M12 wiring: key renamed `code_map` | survived | `met=False` | KILLED — same shape (`code-mappings:absent` path) |
| M13 `if not chunk: break` dropped | survived | **`met=True` (survivor)** | KILLED only by seam case D — **hangs (livelock)** |

Pristine sanity: selftest exit 0 (`selftest: ok`); frozen counter `bind=1 sealed=1 code=1 teardown=1 newrow=1 met=True`, 8 archive libraries byte-equal in `/proc/<pid>/mem`, 13 root-owned host files — matches the lane's `measured/c1-build.out` shape.

## Findings (coverage, not contract changes)

1. **F1 (livelock, defect class, propose fix next round):** M13 — dropping the EOF break in the `code_mappings()` hash loop hangs the launcher forever when a mapped file shrinks between `fstat` and `read` (e.g. package upgrade mid-receipt). Neither the selftest nor the frozen counter reaches a shrink, so the mutant ships green. Killing case D (`harness.py`) reproduces the hang in <1 s on pristine-guarded code, 20 s-timeout on the mutant. Proposal: give the selftest a short-read seam (e.g. factor the loop into `_hash_fd(fd, size)` or patch `os.read` in-test) and assert `file-shrank-while-hashed`.
2. **F2 (coverage):** M06/M07 — the inode-match and dev-match (uid-0-scoped) guards are dead weight on any honest run; only an adversarial path/inode/dev mismatch exercises them, and nothing in selftest or C1 does. Killing cases A and B (fabricated maps rows) kill both in milliseconds. Proposal: upstream cases A/B as selftest seam tests (a `_rows` parameter or patchable maps read in `code_mappings()`).
3. **F3 (coverage):** M04 — C1's receipt check is an `any()` over entries plus digest equality, and the replay's `verify_code` re-derives membership independently, so weakened dedupe semantics are invisible whenever the honest pipeline never emits two same-path-different-inode rows. Killing case E (two such rows, bad one first: the `opened: True` entry for the real inode is silently lost) shows the behavioral difference.
4. **F4 (lane observation, not mine to fix):** the lane worktree at HEAD bc8e6e7f1c53… is **dirty**: ` M tools/kama-llamacpp-live.py` (uncommitted change that records anonymous `/memfd:` mappings as `opened: False, reason: anonymous-memfd`; the worktree replay correspondingly gains `malformed`/`foreign-memfd` branches). My first read of the tool matched c22602bd; the worktree moved mid-wave. Under the in-flight version M03's kill site moves to the `foreign-memfd` branch and M02's to `malformed` — this sweep must be re-run after L1 commits. File:line today: `tools/kama-llamacpp-live.py:793-803` (filter + memfd branch, worktree) vs `:793-795` (frozen blob).
5. The selftest is genuinely load-bearing for the deleted-guard, hash-loop and opened-flag contracts (M05/M08/M10 killed at stage 1) — no action.

## Proposed killing cases (delivered, not applied)

`out/M3Live/harness.py <tool.py> <case>` — cases A-inode-mismatch, B-dev-mismatch-user, C-shrink, D-chunk-break-hang, E-dedupe-two-inodes. Pristine passes all five (`ok: true`, recorded in `out/M3Live/seam-results.tsv`); each survivor mutant fails its case (M13 by hang). Upstreaming them needs the small seam noted in F1/F2; no lane file was edited.

## Evidence and integrity

- Commands and exit codes are quoted above; per-mutant tips in `out/M3Live/commits.txt`; mutant corpus + manifest in `out/M3Live/mutants/`; replay kill-token proof in `out/M3Live/diag/m0{1,2,3}-result.json`.
- Before hash (pristine blob at c22602bd): `82b253e58ae75457b3dc81e6a7450510a50f815e3503bc6a2b61b7d1342b349d`. After restore (commit 8d1d080a8aa4…, file in fixture clone): same sha256; counter rerun `met=True` (`out/M3Live/c1-restored.out`). Mutant hashes in `mutants/manifest.json`.
- No llama-server leftovers at start, between stages, or at end (`pgrep -af llama-server` → none). Counters, preregistration, controls untouched; lane written only under `.ufo/waves/round-53/w1/out/`. No tools installed (no pacman, no uv, no downloads beyond the counters' own pinned assets); scratch `/fast/scratch/hyaku/kama-r53/M3Live` removed at the end.

Report path (Report trailer): `.ufo/waves/round-53/w1/out/M3Live.md`
