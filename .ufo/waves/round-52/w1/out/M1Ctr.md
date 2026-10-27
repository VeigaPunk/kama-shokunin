Survived controls: 8 of 12 requested mutants; four were killed. Targeted one-defect killer cases for the survivors are listed below but were not run; this probe therefore does not establish their killability.

## Evidence

Pristine counter SHA-256 before/after: `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5`; scratch pristine copy has the same hash. Lane counter was not modified. Fixture repo was `/fast/scratch/hyaku/kama-r52/M1Ctr/lane` (verified `rev-parse --show-toplevel`); fixture commit `7a80f9419254629b55d0061c2ae9aff4d8a2ca68` replaces the build's two replay/live tools with their base-tip versions (path-exec style).

Bounded detector commands used the frozen C1 script/copies with `--repo /fast/scratch/hyaku/kama-r52/M1Ctr/lane --tip <tip> --scratch /fast/scratch/hyaku/kama-r52/M1Ctr`. The build-pristine run at `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` exited 0: `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True` (matches frozen `measured/c1-build.out`). J1-style pristine run at `7a80f9419254629b55d0061c2ae9aff4d8a2ca68` exited 1: `bind=1 sealed=0 teardown=1 newrow=1 bound=3/3 sealedruns=0/3 met=False`. Its per-receipt evidence has `F_GET_SEALS ... Invalid argument`, a path link, and nlink 1.

Twelve independent counter mutants were run against the build tip; each complete run covered all three receipts and teardown. Eight reported the same passing build result (survivors of this control):

| Mutant | Change | Build outcome | Status |
|---|---|---|---|
| m01 | Remove running-image `/memfd:` link predicate | met=True | survived |
| m02 | Remove running-image nlink predicate | met=True | survived |
| m03 | Remove running-image seals predicate | met=True | survived |
| m04 | Remove running-image digest predicate | met=True | survived |
| m05 | Weaken `SEALS` from 15 to 1 | met=True | survived |
| m06 | Remove receipt `server_exe` seals predicate | met=True | survived |
| m07 | Remove `own_server` check | met=True | survived |
| m08 | Accept receipt dev/inode mismatch | met=True | survived |
| m09 | Replace `met = bind and sealed and teardown and newrow` with `bind and teardown` | met=True | killed by J1-style tree: exit 0, `bind=1 sealed=0 teardown=1 newrow=1 ... met=True`, differing from pristine J1 `met=False` |
| m10 | Corrupt `MEMFD_URL` by dropping `.2` | `sealed=1 newrow=0 met=False` | killed at build (exit 1; expected `newrow=1 met=True`) |
| m11 | Limit receipt tuple to receipts 1 and 2 | `bound=2/2 sealedruns=2/2 met=True` | equivalent for this measured predicate; counter recalculates denominator from tuple length, so it did not enforce three frozen receipts |
| m12 | Change frozen server SHA final hex digit | `bind=0 sealed=0 ... met=False` | killed at build (exit 1) |

The J1-style tree was additionally run against m09 only; no other J1 mutant runs were made. Total behavioral detector invocations: 15 (2 pristine, 12 build mutants, 1 J1 mutant), below the 25-run cap. Frozen base control `controls/base.c1.out` supplies the separate registered base evidence (`bind=1 sealed=0 teardown=1 newrow=0 met=False`); this seat did not rerun the base tip.

## Survivor killer cases (proposed, not executed)

These are not claimed as observed outcomes. The J1 path-exec control violates several sealed properties together, so it does not isolate these checks. Targeted fixtures that should isolate each mutation:

- m01 `/memfd:`: a running image whose link is non-memfd while nlink, seals, digest, receipt, and own_server predicates all pass. This may be unreachable for Linux sealed memfds; no equivalence conclusion was tested.
- m02 nlink: a running image with nonzero nlink but every other sealed predicate and receipt fact passing; no such fixture was run.
- m03 seals: undersealed memfd plus a receipt that claims seals 15, with replay-side checks adjusted so bind remains true.
- m04 digest: a digest mismatch isolated from the bind-side image-digest witness; no such independent image/read discrepancy was demonstrated.
- m05 weakened mask: memfd sealed only with `F_SEAL_SEAL` (value 1), while receipt says 15 and replay-side checks preserve bind.
- m06 receipt seals: actual image sealed correctly, but receipt `server_exe.seals` deficient; replay-side comparison must not mask the counter's independent receipt check.
- m07 own_server: otherwise-valid receipt/image with replay result `own_server.memfd=false`.
- m08 dev/inode: otherwise-valid memfd with only receipt dev/inode mismatched; replay-side comparison must not make bind fail.

The proposed cases above were not materialized or run; thus survivors remain coverage findings, not detector kills. `m11` is the additional twelfth mutant and demonstrates a robustness gap in the detector's denominator, though it preserves `met=True` on the build rather than being killed.

## Receipts and cleanup

Full raw outputs are in `.ufo/waves/round-52/w1/out/M1Ctr/` (`pristine-build.out`, `pristine-j1.out`, `m01...m12-build.out`, and `m09_drop_conjunction-j1.out`). `pgrep -af llama-server` after the runs returned no output. Scratch `/fast/scratch/hyaku/kama-r52/M1Ctr` was removed before completion. No tools were installed.