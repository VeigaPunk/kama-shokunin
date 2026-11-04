# EX01ReceiptScope — C1 operability

## Files changed

- `tools/round76-receipt-scope.py`
- `.ufo/waves/round-76/w1/EX01ReceiptScope/{before,after,selftest}.out`
- This report.

## Behavior

Imports round 73 by path and imports the byte-frozen round-72 base through its loader. Reuses round-72 receipt extensions, blob/citation reading, header checks, ancestry checks and delta grading. Calls the append-only audit's own `fence_open` / `fence_close` functions, not an independently redefined fence grammar. Unclosed fences and an empty live population fail closed. The seven required independent fixture arms are implemented on the module's own selftest. Header-less receipts remain named classifications and do not fail the run.

Record-path scope is exactly round-72 defaults plus `PROVINCE.md`, `SKILL.md`, `corpus/**`. No exemption for tools, registry, plans or another round's wave directory was introduced. Stale receipt paths are named `RECEIPT_SCOPE_FINDING stale` and tallied under `unclassified` because no receipt bytes exist to bind; this summary-bucket interpretation is not specified by the frozen target, which has no stale field.

L1 directed the default population to the next round's frozen plan's Base revision, via `--base-rev`, with explicit `--tip` override. The population diagnostic discloses this choice. This is a post-freeze interpretation: the assignment originally described after capture at the worktree tip. The current implementation is executed from the worktree at the receipt revision while reading the disclosed historical population revision. No frozen plan was edited.

## Exact retained evidence

All three receipts begin `# rev=1a85a991fce5b76b60f88a5cab3df98d253b1a4a`; subsequent bytes are captured command stdout followed by stderr. Commands ran with cwd `/home/vgpnk/Projects/shokunin/kama-shokunin` and `PYTHONDONTWRITEBYTECODE=1`.

1. `python3 tools/round74-receipt-claim-binding.py --repo . --round 75`: exit **2**, frozen base wrapper refuses the fenced `.py` citation. Receipt: `EX01ReceiptScope/before.out`.
2. `python3 tools/round76-receipt-scope.py --repo . --round 75`: exit **1**. Receipt: `EX01ReceiptScope/after.out`.

```text
RECEIPT_SCOPE_POP round=75 tip=b06cc612711560c53eef3ec21484c6963601262f source=plan:plans/round-76-claims.md
RECEIPT_SCOPE round=75 fenced_quoted=1 live_citations=11 bound=6 unbound=2 shifted=3 nonreceipt=0 unclassified=0
```

**Does not equal frozen target:** bound is 6, not 9; shifted is 3, not 0. Each of these receipts remains shifted:

- `.ufo/waves/round-75/measured/before/c1-mutants.out`
- `.ufo/waves/round-75/measured/before/c2-mutants.out`
- `.ufo/waves/round-75/measured/before/c3-audit.out`

All three name the actual offending non-record delta: `registry/append-only-contract.tsv touched by b8ed25682958`. Expanding the self-description paths removes a PROVINCE-only reason but cannot remove this registry change. The counter was not tuned to force the target. L1 was notified of the contradiction.

The two named unbound paths are `.ufo/waves/round-75/assimilation/summary.out` and `.ufo/waves/round-75/controls/freeze.txt`, each with `no tip=/rev= header among the first 5 lines`. The sole quoted non-receipt is `.ufo/waves/round-75/controls/build-spec.py`.

3. `python3 tools/round76-receipt-scope.py --selftest --work /fast/scratch/hyaku/kama-r76/EX01ReceiptScope`: exit **0**, `RECEIPT_SCOPE_SELFTEST pass=7 fail=0`. Each required arm reported its expected exit: quoted-skip 0, live-nonreceipt 1, none-live 2, unclosed 2, selfdesc 0, tools 1, unbound-named 0. Receipt: `EX01ReceiptScope/selftest.out`.

## Risks and boundaries

- Frozen target is disproved by the required non-record-path rule at the disclosed base population; claiming C1 green would be false.
- Default historical population selection is an explicit L1 interpretation, disclosed above, not silently presented as the original at-tip wording.
- No build, linter, formatter, whole-repository gate or unrelated check ran. The only executions were the three assigned capture commands.
- No LSP endpoint/tool is exposed in this seat's inventory; symbol discovery used exact source reads rather than claiming an empty LSP search meant absence.
- No installation/update, commit, push, external-state remediation or sibling-file edit was performed. Scratch and fixture repositories were removed after receipt capture.

## Self-evaluation

Accuracy 4/5: measured red result preserved; the frozen summary omits a stale bucket, requiring a disclosed interpretation. Completeness 4/5: all required arms and receipts delivered, but the requested green target conflicts with measured registry drift. Clarity 4/5: default population differs from original wording and is explicitly separated. Actionability 4/5: L1 must disposition the frozen target disagreement rather than accept a fabricated green claim. Conciseness 4/5: report retains necessary command and interpretation detail. Overall 4.0/5. Highest-impact improvement is a later, newly frozen claim with a justified target; do not change this plan after scoring.

## L1-requested full-delta diagnostic

L1 accepted the measured miss and requested `--all-findings` without widening scope. Added that mode: it lists every non-record path/commit pair for each shifted receipt, preserving the ordinary verdict and exit map. `python3 tools/round76-receipt-scope.py --repo . --round 75 --all-findings` exited **1**; full byte capture is `EX01ReceiptScope/all-findings.out` (same revision header). Its complete non-record delta list follows:

```text
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c1-mutants.out :: registry/append-only-contract.tsv touched by b8ed256829589a13a0ba2249a8ae9e2b8800fb5a
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c1-mutants.out :: registry/append-only-declarations.md touched by b8ed256829589a13a0ba2249a8ae9e2b8800fb5a
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c1-mutants.out :: registry/append-only-accepted.tsv touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c1-mutants.out :: registry/append-only-contract.tsv touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c1-mutants.out :: registry/append-only-declarations.md touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c1-mutants.out :: tools/pre-report-gate.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c1-mutants.out :: tools/round74-receipt-claim-binding.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c1-mutants.out :: tools/round75-append-accepted.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c1-mutants.out :: tools/round75-interpretation-pins.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c1-mutants.out :: tools/round75-survivor-probe.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c1-mutants.out :: plans/round-75-claims.md touched by 0908bab5cbf0ab6b435144fc525a3e18443dc08f
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c2-mutants.out :: registry/append-only-contract.tsv touched by b8ed256829589a13a0ba2249a8ae9e2b8800fb5a
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c2-mutants.out :: registry/append-only-declarations.md touched by b8ed256829589a13a0ba2249a8ae9e2b8800fb5a
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c2-mutants.out :: registry/append-only-accepted.tsv touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c2-mutants.out :: registry/append-only-contract.tsv touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c2-mutants.out :: registry/append-only-declarations.md touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c2-mutants.out :: tools/pre-report-gate.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c2-mutants.out :: tools/round74-receipt-claim-binding.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c2-mutants.out :: tools/round75-append-accepted.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c2-mutants.out :: tools/round75-interpretation-pins.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c2-mutants.out :: tools/round75-survivor-probe.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c2-mutants.out :: plans/round-75-claims.md touched by 0908bab5cbf0ab6b435144fc525a3e18443dc08f
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c3-audit.out :: registry/append-only-contract.tsv touched by b8ed256829589a13a0ba2249a8ae9e2b8800fb5a
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c3-audit.out :: registry/append-only-declarations.md touched by b8ed256829589a13a0ba2249a8ae9e2b8800fb5a
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c3-audit.out :: registry/append-only-accepted.tsv touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c3-audit.out :: registry/append-only-contract.tsv touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c3-audit.out :: registry/append-only-declarations.md touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c3-audit.out :: tools/pre-report-gate.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c3-audit.out :: tools/round74-receipt-claim-binding.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c3-audit.out :: tools/round75-append-accepted.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c3-audit.out :: tools/round75-interpretation-pins.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c3-audit.out :: tools/round75-survivor-probe.py touched by 10f37171fb696c542586cbee96ea4a509ab74afc
RECEIPT_SCOPE_DELTA .ufo/waves/round-75/measured/before/c3-audit.out :: plans/round-75-claims.md touched by 0908bab5cbf0ab6b435144fc525a3e18443dc08f
```

This measurement disproves the frozen clause requiring `bound=9` and `shifted=0`: the three before receipts cross registry, tools and plan changes, not merely PROVINCE self-description edits. The original control exposed only the first disallowed path, under-sampling the remaining delta. The implementation retains registry/tools/plan shifting and reports `bound=6 shifted=3`; it does not claim C1 green. The full-delta mode makes the hidden paths visible for a future freeze.

Additional changed file: `.ufo/waves/round-76/w1/EX01ReceiptScope/all-findings.out`. The earlier statement of only three executions applies to the initial capture; this explicitly requested diagnostic is the fourth command. Selftest tally was measured before the additive diagnostic mode; parent should rerun the module selftest after integration.
