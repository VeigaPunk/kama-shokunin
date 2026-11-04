# MT01Mutants — round 74 w1 report

Judged axis: operability. Seat: mutation-test the three v2 modules.

## Verdict in one line

24 of 25 mutants KILLED; one survivor — case-sensitive tip binding in the C2
prototype — is a real coverage finding with a named, buildable selftest arm
the C2 module must carry (r73 `blob_reader` seam pattern).

## What ran

1. Read the frozen claims (`plans/round-74-claims.md`), the committed
   builder/scorer (`controls/build-survivors.py`, `score-survivors.py`), and
   the frozen r42/r73/r72 base modules.
2. Rebuilt all eight committed fixtures into this seat's scratch with the
   committed builder; asserted baselines with the same bounded detector used
   for every mutant (fixture arm rc + required finding fragment + module
   selftest where present).
3. Snapshot mid-seat: C1 and C3 executor modules landed while this seat ran;
   their sha256s were recorded before mutation. C2 (`tools/round74-receipt-
   claim-binding.py`) was still absent at final check — C2 mutants therefore
   ran against a PROTOTYPE built from the frozen C2 predicate and labeled
   `prototype` (per seat spec for the not-yet-landed case).
4. Applied 25 distinct behavior-bearing mutants across the required classes:
   comparison flips (invisible=0 forced, != flipped to ==/&, union→
   intersection), exit-code flips (finding → exit 0), scope cuts (paragraph→
   line, first-table-only, newest-block-only, demo-kind-never), header/
   window cuts (demo regex case-sensitivity restored, recorded-at regex
   broken 40→39 hex), and selftest-oracle tampering (assert-True style).
5. Ran each mutant against the fixtures; verified surviving behavior in
   detail; built the missing-fixture-arm analysis for the survivor.

## Results

- C1 live (`round74-selfdesc-canon.py`, sha256
  `2f4e473f5ad9f999042155edcf01995cdf8e05c477dedaafc516657f3608eea7`):
  10/10 mutants KILLED. Baseline kill arm reproduces the frozen kill rule
  (c1_invisible → exit 1, `invisible=4`, names all four; c1_clean → exit 0,
  `total=7 invisible=0`). Selftest green: `SELFDESC_CANON_V2_SELFTEST
  pass=11 fail=0`.
- C3 live (`round74-province-host-drift.py`, sha256
  `118ae079a7f5a18fa40548940eea8d5e8b6fdfbf28c953c997b911f2dba6bad7`):
  6/6 mutants KILLED. Baselines reproduce the kill rule (c3_edited → exit 1
  naming `edited-block`; c3_clean → exit 0, `edited=0`). Selftest green:
  `PROVINCE_HOST_DRIFT_V2_SELFTEST pass=10 fail=0`.
- C2 prototype (executor module absent at final check): 8/9 KILLED. Kill
  arms reproduce the frozen kill rule (c2_wrapped → exit 1 naming
  `wrapped-claim`; c2_offset → exit 1 naming `offset-claim`;
  c2_mixed_honest → exit 0 with `bound_revisions=1`; c2_clean_realizable →
  exit 0).

Full matrix: `.ufo/waves/round-74/w1/MT01Mutants/mutants.md`. Raw harness
output: `harness-live-results.json` and `harness-results.json` beside it.

## Live-defect finding (the one survivor)

`c2_p2l_case_hex` — restoring case-sensitivity to the tip-claim header
comparison — survives all four committed fixtures. The committed fixtures
cannot carry its defect: the only paragraph on which it is load-bearing is a
tip claim whose cited receipt's header equals the tip, and that receipt is a
git hash fixpoint, unbuildable on committed bytes (the round-73 closure's
impossibility result for the old committed-header-equals-tip rule). The r70
rule applies: the check is load-bearing only on a fixture that carries its
defect, and no committable fixture can.

Required selftest arm (name it for the C2 builder): a `blob_reader`-seam arm
in the C2 selftest — the exact pattern the byte-frozen r73 module already
uses (`tools/round73-receipt-claim-binding.py`, `_claim_pass(...,
blob_reader=...)`) — injecting a receipt blob whose header names the tip in
upper-case hex. Pristine binds it (exit 0); a case-sensitive mutant flags it
(exit 1). If the landed C2 module ships without this seam arm, a
case-sensitive regression in the tip-claim branch ships green; that is the
coverage hole this survivor names.

## Live-byte stability

Mid-seat snapshot sha256 (taken the moment C1/C3 landed) equals the post-run
sha256 for both live modules (receipt: `live-module-sha256.txt` in this
directory). The live bytes did not change under this seat; no executor module
was edited; the C2 live path stayed absent throughout. The one live tool
this seat observed being edited by its owner (`tools/round74-seat-count-
check.py`, EX04/SCR02 territory) was not touched.

## Process notes

- Scratch: all work under `/fast/scratch/hyaku/kama-r74/MT01Mutants/`;
  deleted after receipts were copied here. No `/tmp` path is cited as
  evidence; the selftest work roots were created under the scratch dir and
  removed.
- No mutating git/jj command ran anywhere; fixtures were built by the
  committed builder into the seat scratch only, toplevel-asserted by the
  builder itself.
- No tool installs/upgrades were needed (python3 stdlib only); nothing added
  to any PATH directory.
- No peer messages sent; no `agent://all` broadcast.

## Hand-off checks for the L1

1. When `tools/round74-receipt-claim-binding.py` lands, re-run the survivor
   probe: build the case-tip blob_reader arm (or read the module's selftest
   for one); confirm the pristine module binds upper-case header == tip.
2. Re-run `python3 .ufo/waves/round-74/controls/score-survivors.py` after
   all three v2 modules land to certify the kill rules end-to-end.

Report: .ufo/waves/round-74/w1/MT01Mutants/report.md
