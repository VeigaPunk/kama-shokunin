# R2Rerun2 — round-50 C2 independent re-measurement

**Verdict: PASS — reproduces the C2 claim exactly.** `fixture=1 lane=1 scenarios=12/12 met=True` at build tip `97c864bead3ee4a2f629574e77263d33834ec98a` on both independent runs (exit 0, byte-identical receipts); `fixture=0 lane=1 scenarios=9/12 met=False` at base `26ecba64ad6fb571d09074b07202d1618a46ecd1` (exit 1). Counter bytes match the preregistered `counter_sha256`. No run-to-run difference. No defect found.

## Method

```
S=/fast/scratch/hyaku/kama-r50/R2Rerun2; export TMPDIR=$S
git clone /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane   # full clone, HEAD 3b79eaddf38246c637cc7ba1a94ab363422876b6
sha256sum $S/lane/tools/round50-append-audit-v5-check.py
# 925f07a48a02ad54a9c89230aac7e54c8dafee4ba2e8a823dcb851b9cf48ca46
# == preregistration.json C2 counter_sha256  (MATCH)

git -C $S/lane cat-file -t 97c864bead3ee4a2f629574e77263d33834ec98a  # commit
git -C $S/lane cat-file -t 26ecba64ad6fb571d09074b07202d1618a46ecd1  # commit
```

Runs (sequential, shared `--scratch $S`; counter removes fixture trees on exit — verified `find $S -mindepth 1` shows only `lane/` afterward):

```
python3 $S/lane/tools/round50-append-audit-v5-check.py --repo $S/lane \
  --tip 97c864bead3ee4a2f629574e77263d33834ec98a --scratch $S \
  --out .../w1/out/R2Rerun2/c2-build.out        # RUN1 exit 0; RUN2 exit 0
python3 $S/lane/tools/round50-append-audit-v5-check.py --repo $S/lane \
  --tip 26ecba64ad6fb571d09074b07202d1618a46ecd1 --scratch $S \
  --out .../w1/out/R2Rerun2/c2-base.out         # RUN3 exit 1
```

Environment: `Python 3.14.8`, host linux 7.2.11-arch1-1, xfs scratch.

## Receipt lines — RUN1 and RUN2 at `97c864be…` (identical, `diff` = IDENTICAL)

```
tip=97c864bead3ee4a2f629574e77263d33834ec98a
fixture=1 lane=1 scenarios=12/12 met=True
detail: scenario launder: ok exit 1 (want 1) event {'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'} = want
detail: scenario native-head: ok exit 0 (want 0) event {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'} = want
detail: scenario dated-loss: ok exit 1 (want 1) event {'deleted': 25, 'graded': 25, 'status': 'unrestored'} = want
detail: scenario substring: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario word-token: ok exit 0 (want 0) bad_declarations 0 want 0
detail: scenario negated: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario wildcard-self: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario wildcard-named: ok exit 0 (want 0) bad_declarations 0 want 0
detail: scenario order-a: ok exit 0 (want 0) event {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'} = want
detail: scenario order-b: ok exit 0 (want 0) event {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'} = want
detail: scenario fence: ok exit 1 (want 1) event {'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'} = want
detail: scenario crlf-launder: ok exit 1 (want 1) event {'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'} = want
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= v5 natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 72 <= v5 natively exempt 72
```

Receipt copies: `c2-build-run1.out`, `c2-build-run2.out` (= `c2-build.out`).

## Receipt lines — RUN3 at base `26ecba64…`

```
tip=26ecba64ad6fb571d09074b07202d1618a46ecd1
fixture=0 lane=1 scenarios=9/12 met=False
detail: scenario order-b: FAIL exit 1 (want 0)
detail: scenario fence: FAIL exit 0 (want 1)
detail: scenario crlf-launder: FAIL exit 1 (want 1) event {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'} want {'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'}
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 82
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= v5 natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 65 <= v5 natively exempt 72
```

(Receipt `c2-base.out`; other 9 scenarios all `ok`.)

## Observations

- **Determinism**: both tip runs produced byte-identical receipts and identical stdout; receipts carry no timestamp/nonce fields.
- **Base failures isolate exactly the v5 fixes**: `order-b` fails while `order-a` passes at base — the asymmetric sibling-order flip the F3 fix removes (v4 first-in-rev-list origin happens to coincide with the union in order-a, diverges in order-b). `fence` fails open (exit 0 want 1; F4) and `crlf-launder` ungrades instead of grading (F5). Consistent with the counter docstring's scenario design (`tools/round50-append-audit-v5-check.py:36-55`).
- **Lane leg at base still passes** (`lane=1`, 82 ≤ bounds): the lane leg is an upper bound on ungrading, so the v4 defects are caught only by the fixture leg — as the preregistered limit states (binder still v4, seat V2Ctr). The +7 in `ungraded_lines` (82→89) and `0718b6abbda6` ungraded 65→72 match the announced F6 resolution (`## Capabilities` mirror rows gaining a head birth under v5). Both `<= v5 natively exempt` inequalities hold at both commits.
- **Counter integrity**: sha256 of the executed counter equals `counter_sha256` in `preregistration.json` (`925f07a4…ca46`); counter ran read-only on the clone and cleaned its fixture trees on exit.
- No `llama-server` processes of mine exist (`pgrep -f llama-server` shows only seat X11ModelSwap's processes, untouched). No leftover scratch besides the removed clone (deleted after the run).

## Defects

None observed in the counter or the measured behavior. Known integration gaps (instrument registry, SCORECARD/LOG/lesson/QUALITY/README round-50 entries, S496/S497/S498 used-by rows) are out of my scope per the assignment.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R2Rerun2.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R2Rerun2/c2-build.out` (RUN2 receipt at tip)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R2Rerun2/c2-build-run1.out` (RUN1 receipt at tip)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R2Rerun2/c2-build-run2.out` (RUN2 receipt copy)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/R2Rerun2/c2-base.out` (base receipt)
