# R08 case 16 — C2 canonical-row binding mutation evidence

Frozen base: `b89bdab2cc114735ec5d331c6c610134258f7864`. Fixture is a scratch Git clone of the frozen base; every git mutation was preceded by `git rev-parse --show-toplevel` equality check for `/fast/scratch/hyaku/kama-r57/R08SelftestMutation/fixture`.
Detector: import/run the frozen round42 counter against `--repo <scratch-fixture> --tip HEAD`, intercepting `git cat-file -p <tip>:SCORECARD.md` requests; the no-op uses the same wrapper. Each data mutant was committed only in the scratch fixture, then the exact pristine SCORECARD bytes were restored in a new scratch commit and re-tested.
Pristine hashes: SCORECARD `9a8d594b18db8d7b31675ef3a31ff3e70e364ca66816e2489bc8b3c35d29dd35`; gate `9736923ec3086c6e56512cd67fa7c00a22cbb8ac63022bef45a676f2200f9ef0`.

## Observations
### pristine — reference baseline
- exit: `1`; SCORECARD cat-file reads: `2`
- summary: `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`
### missing-row — killed iff new mismatch relative to baseline
- exit: `1`; SCORECARD cat-file reads: `2`
- summary: `r41=1 banner=0 planned=0 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=0 rel=0 mismatches=4 maxN=56 met=False`
### extra-row — killed iff new mismatch relative to baseline
- exit: `1`; SCORECARD cat-file reads: `2`
- summary: `r41=1 banner=0 planned=0 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=5 maxN=56 met=False`
### renamed-canonical-row — killed iff new mismatch relative to baseline
- exit: `1`; SCORECARD cat-file reads: `2`
- summary: `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=1 receipts=0 readme=0 province=0 rel=0 mismatches=2 maxN=56 met=False`
### noop-pristine — no-op control
- exit: `0`; SCORECARD cat-file reads: `0`
- summary: `mismatches=0 maxN=46 met=True`
### noop-mutated — no-op differential binding
- exit: `0`; SCORECARD cat-file reads: `0`
- summary: `mismatches=0 maxN=46 met=True`
### noop-restored — restoration check
- exit: `0`; SCORECARD cat-file reads: `0`
- summary: `mismatches=0 maxN=46 met=True`
### caps-check-ablated — name-check ablation
- exit: `1`; SCORECARD cat-file reads: `2`
- summary: `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`
### caps-check-restored — same renamed data after restoring gate
- exit: `1`; SCORECARD cat-file reads: `2`
- summary: `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=1 receipts=0 readme=0 province=0 rel=0 mismatches=2 maxN=56 met=False`
### consistent-rename — self-consistent rename coverage probe
- exit: `1`; SCORECARD cat-file reads: `2`
- summary: `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`
### final-restored — exact final byte restoration
- exit: `1`; SCORECARD cat-file reads: `2`
- summary: `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`

## Verdicts and minimal controls
- Missing, extra, and canonical-only renamed rows are killed when the actual round42 counter adds mismatches relative to pristine `1`; inspect their per-run outputs in the sibling `.out` receipts.
- The caps name-set equality check is load-bearing: with only `if sorted(hn) != sorted(names)` ablated, the canonical-only rename no longer adds a mismatch; restoring that exact gate byte makes the same rename add a mismatch again.
- A consistent rename in both the head mirror and canonical table is a surviving coverage mutant if the summary adds no mismatch beyond the frozen baseline: the current gate checks internal consistency, not an independent canonical-name authority. This is a finding, not a contract change.
- The no-op says `met=True` with zero SCORECARD cat-file reads and identical output on pristine/mutated/restored bytes. Minimal robust acceptance control: require a positive SCORECARD content-read witness and a differential self-test where each canonical-row mutation changes the appropriate mismatch/result; do not accept its self-reported `met=True` alone.
- Restore evidence: final SCORECARD and gate hashes must equal the pristine hashes above; final summary is recorded in `final-restored.out`. Scratch receipt files were copied to the lane wave path before the shell cleanup trap ran.

## Receipt hashes
- `caps-ablation-data-restored.out` sha256 `0c727281055588f73eba62fec051bce9679002dd8c9bfe614b1f93462cab20cb`
- `caps-check-ablated.out` sha256 `2ab75a348421f3a27796b2d3df93b32ba84aa396f85ea5e2d6439955df4c6183`
- `caps-check-restored.out` sha256 `57b6ccfefe3554044056c19eb8f3a25c2c49511b127a9c376c08355ba85beb60`
- `consistent-rename.out` sha256 `8980f1644700dee172716d2c5790481bddb8928ab8fd2250e90d0188a2febbb8`
- `extra-row.mutated.out` sha256 `c61b66c092610e94fd88a51627708f6932ed31f70315dcf077b426b194688021`
- `extra-row.restored.out` sha256 `2acb371a08209f282f509d89b4618c46f848513bbe173958a0d391604395de98`
- `final-restored.out` sha256 `6df57cd6697f3c55aa9f3fde8885f81e9f6844a95b80b45e38d48fca843f9ce6`
- `missing-row.mutated.out` sha256 `250e1c87513b0de6501564e35c727d5d8f06458245456bfa3f14fa6656dd5787`
- `missing-row.restored.out` sha256 `c4317f683456519c1b980330366c3e6af26c48d3c9fdcf3356ead706bc9001f9`
- `noop-mutated.out` sha256 `cb216ad89724e29eff66e3f0ebdde8e491e3026800fcb6a2fccef906368f25e4`
- `noop-pristine.out` sha256 `170e1da8b65812c1248a372b3e848917a72902d6d8dec22eb0a4d84da7e17ed5`
- `noop-restored.out` sha256 `c49cde786fc49eb8f9d59c92232152358fccf2da7574338ca21deb2491f1b12d`
- `pristine.out` sha256 `d8fa0c9f9d803b266354536423dab772885fb4dff5850fae9018ff0bc808afd2`
- `renamed-canonical-row.mutated.out` sha256 `47eeb5a03b5fd35fdb871dd442067d0f96720415e1cbd9c9b113d89e18616f9a`
- `renamed-canonical-row.restored.out` sha256 `6b7c151ccab9c00bda48983470dc678a4fd05859d3ef571fd696c30b36d815f4`
