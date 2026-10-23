ATTACK C1 counting command and landed-tip receipt: holds

Seat: KamaR26.RerunC1AtTip (round 26, wave 2 FALSIFY). Access date 2026-10-23.
Scratch: /fast/scratch/hyaku/kama-r26w2/RerunC1AtTip/ (tip/ and base/ are `git archive` extracts).

## Findings by severity

No defect found in scope. The frozen counter reproduces the landed receipt at
the landed tip and prints counted 0 at base.

Low-severity observations (no correction required for C1):

1. The landed receipt `final/c1-tip.out` was measured at tree 7e5ff9b5, not at
   the landed tip f4066979. The two commits after it (3550523, f406697) change
   none of the counter's inputs:
   `git diff --stat 7e5ff9b5 f4066979 -- SKILL.md registry corpus .ufo/waves/round-26/sources .ufo/waves/round-26/count-c1.py`
   printed nothing. Its 14 changed files are receipts, wave-1 advice and LOG.md.
   This rerun at f4066979 gives the same result, so the receipt holds for the tip.
2. The frozen counter starts its own servers without `-t 2` (`base_argv`,
   count-c1.py:225-226). That is inside the frozen counter; it is not a C1
   defect and must not be changed after the freeze.

## Exact observations

### Counter identity
- `sha256sum tip/.ufo/waves/round-26/count-c1.py` gave
  `6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588`, equal to
  the `counter_sha256` in preregistration.json. `git cat-file -p f4066979:.ufo/waves/round-26/count-c1.py | sha256sum` gives the same value.
- The counter's sha256 at each commit: a4a159c `eea0cc75…`, a12850c `f800865d…`,
  and a23c0e0, 3550523, f406697 all `6501737c…`.
  The first two values are the freeze and amendment A0. Amendment A1 landed at
  a23c0e0, and the preregistration documents all three.

### Counter history
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --format='%h %cI' -- .ufo/waves/round-26/count-c1.py`, exit 0:
```
a23c0e0 2026-10-23T00:32:54-03:00
a12850c 2026-10-23T00:19:43-03:00
a4a159c 2026-10-23T00:18:51-03:00
```
`git log --format=%h a23c0e0..f4066979 -- .ufo/waves/round-26/count-c1.py | wc -l` printed `0`,
so there is no change to the counter after a23c0e0. With `--all`, the history
also shows jj keep refs (2dc3db4, fa47a08, 8bf1f98, 71dd14f, 985d95e, 9a6d234).
None is an ancestor of f4066979 (`git merge-base --is-ancestor` gave no for each),
and each holds one of the three counter versions above.

### Run at landed tip f4066979
- Extract: `git archive f4066979096e3452ae731c0e09e50155c6d8258a | tar -x -C $S/tip`, with GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE unset.
- Before the run, `ss -ltn` showed nothing listening on 47560-47579, and `pgrep -af llama-server` showed no process.
- Command (cwd $S/tip), from 2026-10-23T03:57:35Z to 03:57:40Z:
  `flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out $S/tip-receipt.json`
- stdout: `registered 17 counted 17 target 12 met True not-counted []`
- stderr: empty. Exit code: **0**.
- Landed `final/c1-tip.out`: `registered 17 counted 17 target 12 met True not-counted []`, `exit=0 tree=7e5ff9b5…`. The stdout line is identical.
- Receipt comparison with `final/c1-tip-receipt.json`:
  - Both have the same top-level keys and the same 17 row ids.
  - All 12 per-row check results (`id_unique` through `g_distinct`) are identical and all true.
  - Every row has `counted` true.
  - The channel hashes of the HTTP rows E26-01..E26-14 are identical.
- Expected differences:
  - `lane` is the scratch path.
  - `baseline_sha256` changes because the baseline includes the server log and generated tokens.
  - The `channel_sha256` of E26-15..E26-17 changes because their stderr channel carries log timestamps and a temporary directory path.
  - After stripping timestamps and the temporary path, the excerpts match. The only exception is one timestamp cut off at the 400-character excerpt boundary in E26-15 and E26-16 (`0.00.005.62` vs `0.00.011.95`; `0.00.005.8` vs `0.00.005.1`).

### Run at base 1560e4d8 (counter copied in)
- Extract: `git archive 1560e4d83f42b04f40336357de6f9637eafa0f4b | tar -x -C $S/base`, then the tip counter was copied to `.ufo/waves/round-26/count-c1.py`. Its sha256 is `6501737c…`.
- Same command under the lock, cwd $S/base, at 2026-10-23T03:57:47Z.
- stdout: `registered 0 counted 0 target 12 met False not-counted []`
- stderr: empty. Exit code: **0**.
- The receipt has `rows: []` and `baseline_sha256 e3b0c442…`, which is the hash of empty text. With no registry the counter skips the baseline server. The server and model sha256 pins and the base SOURCES.md read still passed, because none raised could-not-evaluate. This matches the preregistration's `before` and `unmoved_command`.

### Cleanup
- After both runs, `ss -ltn` showed nothing on 47560-47579.
- The llama-server processes later visible are on ports 47720, 47734 and 47740, pass `-t 2`, and had run for 11-17 s when checked, after my last run ended at 03:57:47Z. They are sibling seats' servers under the shared host process, not mine. The counter uses 47560-47579 and passes no `-t`.
- I started no other server. No tools were installed or updated.

## Residual risk and verification gaps
- I did not re-fetch the source files at 704366d or compare them against the
  lane snapshot. The counter's clause (d) check passed for all 17 rows, so each
  pinned source file still matches its sha256 in the counter. This seat did not
  check the upstream fetch independently.
- Known counter limits F1-F4 (lesson §Mistakes row 3) were not attacked here;
  sibling seats cover individual rows. This seat checks only that the receipt
  reproduces.
- One rerun per tree; repeat-run stability beyond this single reproduction is not measured.

## Files written
- .ufo/waves/round-26/w2-falsify/advice/RerunC1AtTip.md (this report)
- .ufo/waves/round-26/w2-falsify/out/RerunC1AtTip/{tip-receipt.json, tip.stdout, tip.stderr, tip.exit, base-receipt.json, base.stdout, base.stderr, base.exit, counter-history.txt}
- Scratch only: /fast/scratch/hyaku/kama-r26w2/RerunC1AtTip/ (tip/, base/ extracts, receipts, start/end timestamps)
