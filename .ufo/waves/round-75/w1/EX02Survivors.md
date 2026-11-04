# EX02Survivors — C2 implementation

Axes: operability (executable per-mutant evidence), calibration (no unrun success claims), non-regression (production grading untouched).

## Files changed

- `tools/round74-receipt-claim-binding.py`: only two appended selftest arms. `conflicting-headers` builds a committed receipt with different revision headers, requires audit exit 1, the inherited `unbound` finding and count, and the v2 parser's conflicting-header rejection. The parser assertion prevents the unchanged frozen base leg from masking a surviving v2 conflict-off mutant. `header-window-fifth-line` requires audit exit 0 and one explicit-revision binding for a header on line 5. Existing grading and existing arms are unchanged.
- `tools/round75-survivor-probe.py`: frozen C2 predicate constant; exact five source replacement pairs copied from the freeze control; one shared clone of committed lane bytes; pristine and mutant module selftests; parsed arm/count/exit consistency; required existing arms; exact five-name catalogue; expected failing arm per mutant; text receipts, optional JSON, retained-work option, and explicit could-not-evaluate handling. Work is deleted by default. Its selftest exercises the count-only/empty-list cheat, pristine-red, green-mutant and wrong-arm rejections.
- This exclusive report. No other report/receipt files were created.

Decision: the existing `same-line-stale-claim` arm remains the same-line inherited-kind fixture. `kind-boundary` targets that existing arm; no new fixture for that class was added.

## Retained evidence

Read the entire frozen plan, the module implementation/selftest, and `controls/mutation-control.py` C2_MUTANTS. The existing receipt `.ufo/waves/round-75/measured/before/control.out` line 4 says exactly:

```
CONTROL_C2 killed=3 escaped=2 c2_case_hex=killed c2_kind_boundary=killed c2_paragraph_scope=killed c2_conflict_off=escaped c2_header_window=escaped
```

That is prior evidence, not a rerun by this seat. No baseline claim is upgraded to a measured after-result.

Actual command executed, exit 0, empty output:

```
mkdir -p /fast/scratch/hyaku/kama-r75/EX02Survivors && rmdir /fast/scratch/hyaku/kama-r75/EX02Survivors
```

The exclusive scratch root was removed; no clone was created. No tools were installed or updated. LSP tooling is unavailable in this seat's mounted inventory; symbol definitions were read through the file tools instead.

## Verification ownership and risks

Builds, tests, linters, formatters, and smoke runs were **not run**: the higher-priority fleet executor instructions explicitly reserve all verification for the parent after integration. Thus the assignment's requested module/probe/selftest exits are unobserved, not passed. There are no fabricated after-receipts.

Parent commands after integration (set `TMPDIR` explicitly; capture stdout/stderr and exit codes into owned receipts, then remove the scratch root):

```
TMPDIR=/fast/scratch/hyaku/kama-r75/EX02Survivors python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round74-receipt-claim-binding.py --selftest --work /fast/scratch/hyaku/kama-r75/EX02Survivors
TMPDIR=/fast/scratch/hyaku/kama-r75/EX02Survivors python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round75-survivor-probe.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --work /fast/scratch/hyaku/kama-r75/EX02Survivors --json
TMPDIR=/fast/scratch/hyaku/kama-r75/EX02Survivors python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round75-survivor-probe.py --selftest
```

The survivor probe deliberately grades **committed** bytes, not this working tree. The parent must include the two new module arms in its committed integration snapshot before expecting five kills. Before that, the original committed module can still expose the two documented escapes. The decoder accepts the original nine-arm receipt so the same probe can report those escapes rather than misclassifying the baseline as unevaluable.

Expected, not measured: module green with the two new arms; `conflict-off` fails `conflicting-headers`; `header-window` fails `header-window-fifth-line`; all five expected failures produce `SURVIVORS2 mutants=5 killed=5 escaped=0` and exit 0.

Implementation dead end: one line-number patch to the new probe briefly targeted the parser instead of REQUIRED_ARMS. The edit tool reported a syntax error; a focused reread and corrective edit restored the intended parser statements and narrowed REQUIRED_ARMS to the original nine. No check was run in response.

No disagreement with the frozen C2 rule. Delivery is scoped implementation, not a scored claim or acceptance verdict. Remaining blocker to measured acceptance is parent-owned post-integration execution.

## Addendum — arms fixed after L1 verification

L1 reported `header-window-fifth-line FAIL exit=1 bound_revisions=1` and `RECEIPT_CLAIM_V2_SELFTEST pass=10 fail=1`. This is L1 evidence, not a check executed by this seat; the process exit code was not supplied in that message.

Diagnosis: the fixture created `plans/round-74-claims.md` in the record commit **after** the revision named by the receipt. The frozen base `_evaluate` rejects any intervening commit touching a non-record path (`round72-receipt-tip-binding.py:441-444`), and `plans/` is explicitly not a record path (module documentation lines 77-78). Thus the v2 explicit revision bound while the base leg reported shifted. The paragraph itself has no tip claim.

Fix: create the fixture plan before its seed commit, so every change after the named revision is a receipt or self-record. Keep the strict `exit == 0 and bound_revisions == 1` assertion unchanged. No production grading was altered.

No reruns were performed: the higher-priority leaf executor instructions still reserve checks for the parent. Neither a green module exit nor a five-kill probe exit is claimed here. Parent must verify the repaired working-tree module, then the committed integration snapshot with the probe. A probe over the old committed module will correctly continue reporting the two escapes; this cannot be fixed by changing fixture behavior in an uncommitted working tree. No git/jj mutation or scratch writes occurred in this correction.
