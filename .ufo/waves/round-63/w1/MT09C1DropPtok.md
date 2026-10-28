# MT09C1DropPtok — C1 operability mutation probe (live_ptok)

Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (tools/round63-c1-counter.py blob 56c54c84).
Scope: falsify the live_ptok clause of score() in the C1 counter. Leaf seat, no verdict on the claim.
Clone: $SCRATCH/clone (git clone --shared of the lane; every edit and commit inside the clone; top-level asserted each time). Scratch removed after evidence copy.

## Baseline (unmutated, at tip 03a6a1d)

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
exit=0. Baseline is met, so the control credits below are meaningful.

## Mutant 1 — delete the live_ptok clause from score()

Diff (committed in clone as c61ee7ac80e28fc7656df2233bd017a1a09eb6b0, `git diff` vs 03a6a1d): removes the 3-line `'live_ptok': ... and w['usage_prompt_tokens'] == w['tokenize_count'] >= 1,` entry from the `live` dict. Counter run from the clone path, --repo clone --tip c61ee7a…, work dir fresh.

Output (verbatim):
```
tool_present=1 live_ok=1/1 controls_targeted=42/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=1/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=5/6]
error: escape witness expect=live_ptok fails=[]
error: escape fake-inconsistent expect=live_ptok fails=['live_owned', 'live_port']
```
exit=1. Rerun at the same tip: identical line, exit=1 (deterministic).

Verdict: **KILLED** — met flips to False. Two of the 44 controls escape:
- `witness` family, control `live_ptok` (witness usage_prompt_tokens +1): re-score fails=[] — the defect is now invisible to the counter.
- `fake` family, `fake-inconsistent` (canned server usage 5 vs tokenize 3): rejected only by `live_owned` and `live_port` (the fake is a different listener), not by the named `live_ptok`. Under the is_hit rule this is an escape, correctly.

The ptok family on the receipt side (`completion_prompt_tokens`, grade-side) still catches its 2 controls, so the escape is isolated to the witness-side compare.

## Mutant 2 — make the tokenize_count compare vacuous

Diff vs baseline (committed in clone as a1b5a6aa613175182bf8b2ba81292f99a4e46ce3, parent = mutant 1 tree in the diff, but the net content is baseline + one change): the live_ptok clause keeps its is_int checks and the final compare `w['usage_prompt_tokens'] == w['tokenize_count'] >= 1` is replaced by `True`. Diff file: out/MT09C1DropPtok/mutant2-vacuous-tokenize-compare.diff (the 3-line change is shown relative to mutant 1's commit; the mutant 2 tree differs from the baseline only in that single compare line).

Output (verbatim):
```
tool_present=1 live_ok=1/1 controls_targeted=42/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=1/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=5/6]
error: escape witness expect=live_ptok fails=[]
error: escape fake-inconsistent expect=live_ptok fails=['live_owned', 'live_port']
```
exit=1. Verdict: **KILLED** — met=False, the same two escapes as mutant 1 (witness live_ptok, fake-inconsistent). Both defect forms are detected by the same two controls.

## Observations (counter/control-set weaknesses, not verdicts on the claim)

1. **eval_selftest does not detect the deletion.** Planted control (1) is `stale` (nonce 'r60-dead') expected to be refused on `live_ptok`. With the clause deleted the stale receipt is still refused (live_ptok is simply not in its fail set), so the planted check passes and st stays 3/3. The self-test only proves "not credited by the named check"; it does not prove the named check exists or can fire. The defect is caught only by the 44 targeted controls (witness live_ptok and fake-inconsistent). A stronger plant would require the named check to fail on a witness whose only defect is the ptok mismatch — which is exactly what the witness control already does, so the coverage exists but the self-test layer is not an independent detector for this clause.

2. **The fake-inconsistent control is rejected for the wrong reason at the wrong check set.** Its failures under mutant 1 are live_owned and live_port (its canned listener is not the receipt child). This is still an escape under the strict name rule, so the counter is correct to refuse credit; but it means the fake's inconsistency is only observable through live_ptok, and the fake is not discriminating on its own when that check is absent.

3. No SURVIVED mutant: both forms of the defect flip met to False.

## Restoration / hygiene

- Lane untouched: all edits and commits happened in $SCRATCH/clone; lane HEAD, index and working tree not modified by this seat. Lane read-only calls: `git cat-file`, `git ls-tree`, `git clone --shared` (source read).
- No tool installed or upgraded; no pacman; no live port beyond the counter's own launched fixture (unregistered loopback).
- Receipts copied to .ufo/waves/round-63/w1/out/MT09C1DropPtok/: base.out/err, mut1.out/err, mut1b.out/err (rerun), mut2.out/err, mutant1-drop-live_ptok.diff, mutant2-vacuous-tokenize-compare.diff.
- Scratch root /fast/scratch/hyaku/kama-r63/w/MT09C1DropPtok removed before yield.

## Tally (one line)

tool_present=1 live_ok=1/1 controls_targeted=42/44 eval_selftest=3/3 errors=0 met=False families[… fake=1/2 … witness=5/6] — mutant 1 (drop live_ptok) and mutant 2 (vacuous compare) both KILLED; baseline met=True 44/44.
