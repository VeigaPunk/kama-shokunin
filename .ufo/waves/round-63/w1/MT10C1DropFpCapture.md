# MT10C1DropFpCapture — C1 mutant: drop the `live_fp_capture` clause

Seat: MT10C1DropFpCapture (mutation-tester, leaf, advisory). Judged on operability. Milestone: falsify C1 counter.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (lane HEAD, verified).

## Verdict

**KILLED.** Deleting the `live_fp_capture` clause flips the C1 counter from `met=True` to `met=False`.
The escape lands in the **witness** family (5/6, was 6/6). The **fake** family does not escape (2/2).
Nothing was SURVIVED.

## Mutation

- Target: `tools/round63-c1-counter.py`, `score()`, lines 302-303:
  `'live_fp_capture': isinstance(cfp, str) and w.get('fingerprint') == cfp,`
- Only delta: those two lines deleted (`git diff --stat`: 1 file, 2 deletions). Evidence: `out/MT10C1DropFpCapture/mutant-c1-drop-live_fp_capture.diff`.
- Clone: `git clone -q --shared` of the lane at 03a6; toplevel asserted equal to the clone dir before every mutation; edit and commit made only inside the clone (`seat` identity, scratch fixture). Mutant commit `da2d6c2ee5b29c4336b2feacb65ca19d6ea3e4d6`.
- Scored by running the mutated counter from the clone path: `cd $D/tools && python3 round63-c1-counter.py --repo $D --tip da2d6c2e… --work $S/work-mut`. The tool under test (`tools/kama-completion-live.py`) is byte-identical in the mutant commit and at 03a6 (blob sha256 `35af5c98…d8143dd1f341280a74d9d0a4ebe45dbcd` in both).
- Unmutated pair: the same counter at the clone's 03a6 commit, `--tip 03a6…`, `--work work-base`.

## Results (verbatim counter output)

Unmutated (exit 0):
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
Mutant, `live_fp_capture` clause deleted (exit 1), stderr: `error: escape witness expect=live_fp_capture fails=[]`:
```
tool_present=1 live_ok=1/1 controls_targeted=43/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=5/6]
```

## Why it flips (mechanism)

- The only control that exercises the clause is `add('witness', receipt, 'live_fp_capture', wm(fingerprint='b1-aaaaaaaaa'))` (line 621). The receipt's captured fingerprint is `b11755-704366d76` (`out/…/receipt-base.json`), so the forged witness differs from the capture.
- Baseline: the forged witness fails `live_fp_capture` alone. `b1-aaaaaaaaa` still matches `FP_RE` (`live_fp_shape` passes), so no other check fails, and `is_hit` credits the control.
- Mutant: with the clause gone the witness fingerprint is checked by nothing. `fails=[]`, `met=True`, `is_hit` is False, and the control escapes. The base and mutant failure sets for that control differ by exactly `{live_fp_capture}`, which is the removed clause.
- The genuine live receipt never violates the clause (`live_ok=1/1` in both runs), so the defect is visible only through the control set, as intended.
- Escape is structural, not stochastic: with the clause deleted, the control's failure set cannot contain `live_fp_capture`. One run per side is conclusive; no repeat was made.

## Family analysis

- **witness (5/6, escapes):** the forged-fingerprint control escapes. This is the family that catches the defect.
- **fake (2/2, does not escape):** `make_fake` is fed `fp` = the receipt's own `system_fingerprint` (lines 696-697), so both canned servers report the same fingerprint as the capture. `fake-inconsistent` expects `live_ptok` and `fake-foreign` expects `live_pid`; neither depends on the clause. The fake family therefore cannot reveal the defect by construction.
- **eval_selftest (3/3, unchanged):** the three planted wrong-reason controls do not involve the fingerprint clause, so the evaluator self-test is blind to it.

## Observations (code reading; not measured beyond the two runs)

1. **Single guard.** `live_fp_capture` has exactly one control behind it. The kill is real, but one control is a thin guard for a clause that is part of the frozen C1 predicate ("whose fingerprint equals the receipt's captured one"). A fake server reporting a divergent `system_fingerprint`, expecting `live_fp_capture`, would give an independent second guard. Not built here: out of the assigned probe.
2. **Dead variable after the mutation.** `cfp` (line 291) is used only by the deleted clause, so the mutant leaves it unused. Harmless to the verdict; noted as a tell only.

## Host, lane and tool integrity

- Live runs: two counter invocations, each spawning its own `kama-completion-live.py` child on a free unregistered loopback port. `pgrep` after both runs found no counter or child process left behind. Foreign llama-servers on ports 1234 and 45669, plus a 37323 server and an ollama runner belonging to other lanes, were listed and left untouched.
- Lane untouched: HEAD still `03a6a1d850902a66a13dfad33f89cf3a8b759a09`; `tools/round63-c1-counter.py` worktree sha256 `35af5c98…d8143dd1f341280a74d9d0a4ebe45dbcd` equals the 03a6 blob; `git status` clean for both tools. No lane write other than this report and its out dir.
- Clone restore: not needed; the clone is disposable scratch under the recipe, and the lane file was never written. Mutant blob sha256 `d0c5e528674afc27622d9067459641a096dff18836eba62b34c03fce22e669e6`.
- Tools installed or upgraded: none. Pacman not touched.

## Evidence (out/MT10C1DropFpCapture/)

- `base.out`, `base.err` (empty): unmutated counter, exit 0.
- `mut.out`, `mut.err`: mutated counter, exit 1, escape line.
- `mutant-tip.txt`: mutant commit `da2d6c2e…`.
- `mutant-c1-drop-live_fp_capture.diff`: the 2-line deletion.
- `receipt-base.json`, `receipt-mutant.json`: the live receipts both counters re-scored (schema `kama-completion-live/v2`, verdict `REQUEST_OK`).

Scratch `/fast/scratch/hyaku/kama-r63/w/MT10C1DropFpCapture/` removed after receipts were copied.

## Tally

tool_present=1 live_ok=1/1 controls_targeted=43/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=5/6]
