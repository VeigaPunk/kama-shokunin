# EX02Registers — C1b/c

Axis: operability. Frozen plan read in full; predicates and fixtures unchanged.

## Delivered

- `append-only-late.tsv`: original header and 113 retained data rows, followed by one new acceptance (114 data rows total).
- `append-only-late-r83-restored.tsv`: original header plus original lines 105–114, copied byte-for-byte. Historical archive only, never re-graded. Filename follows frozen assignment despite the observed status discrepancy below.
- `append-only-disclosures.tsv`: **UNCHANGED reference copy**, not an integration change; the requested new disclosure row is blocked by that ledger's actual semantics.
- `registry.diff`, component diffs, full pre-change debt/audit receipts, base audit receipt, subject receipt, and `receipts.txt` retain commands, outputs and exit codes.

Acceptance event: `96e28374593be13833aebeb70150877f58f4aadc`, `SCORECARD.md`, SHA256 `b2d76c4c24253879407fa21b658c339d75665e729ecb2469ab4c952a98579b21`, count 1, class `in-place-edit`.

Actual subject (git log exit 0):

> round-83: reconcile the self-description (49 capabilities, round-82 closure pointer, round-84 plan), the R82 defect dispositions and the province note

Appended note:

> round-84 accepts round-83 "round-83: reconcile the self-description (49 capabilities, round-82 closure pointer, round-84 plan), the R82 defect dispositions and the province note"; accepted round-83 record edit superseded by the round that followed

Identity: note deletion round = 83 = event subject round; acceptance round 84 > 83. Quoted subject equals actual subject verbatim.

## Observed evidence and frozen-premise discrepancy

At controls tip `eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85`, debt exits 1 with events=76, late=22, pending=0, unaccepted=1, bad_rows=10; ten unknown-event findings name original lines 105–114, plus count-short for the acceptance event above. Saved in `before-debt.out`.

Both controls-tip audit and explicitly base-bound audit exit 1. Event `0d7c7c3ea7d120c4796e9e5119d48038f85fde20` / SCORECARD.md is **ungraded**, not restored: deleted=12, graded=0, ungraded=12, held_at_to=0, restored_max=0, undisclosed=[]. See `before-audit.json` and `base-audit.json`. Thus the rows are outside the debt population, but the frozen restoration rationale is not supported by either actual JSON receipt. Frozen text was not changed.

## Disclosure blocker

The six columns are `commit file line_sha256 count class note`. This is an event-loss ledger, not a free-form rotation log: audit.py lines 15–25, 529–544 and 697–726 require an unheld graded deleted line, a real event/class, positive count and pre-ledger event ancestry. A metadata-only row or row naming the now-ungraded 0d7c7c3e event cannot satisfy those semantics. Appending one would manufacture a bad disclosure and harm the gate. No fake row was supplied. L1 was notified; representation requires L1 resolution rather than an unrequested audit-tool change.

Disclosure narrative ready for the round lesson: R83V3 — move the ten old late-register rows 105–114 to registry/append-only-late-r83-restored.tsv unchanged; keep as ungradeable history, not acceptance population. Frozen plan calls the event restored at aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0; the actual base and tip audits report ungraded instead. Acceptance of the distinct round-83 event is value-bound above.

## Verification boundary and integration

No post-edit debt, selftest, live register verification, build, lint or formatter was run: the leaf developer contract reserves post-integration checks to the parent during the editing wave. No pass is claimed. No scratch commits were made; new late rows must be committed by L1 before committed-history grading.

Parent checks after resolving disclosure and committing integration:

- python3 tools/round81-append-debt.py --repo . --round 84
- python3 tools/round77-append-registers.py --selftest
- python3 tools/round78-append-registers.py --selftest
- python3 tools/round77-append-registers.py --repo .
- python3 tools/round78-append-registers.py --repo .

Both register tools accept --repo (their argument declarations were read). New-row survival under C1 binding is inferred from the explicit identity above, not exercised here. Global configurations, aliases and external substrates unchanged. No installations, network calls or local git mutations. LSP unavailable in mounted inventory; this task edits TSV data, not symbols.

The requested report trailer location outside out/ conflicts with the exclusive-write directory contract. This report stays inside out/EX02Registers/ for L1 to land at `.ufo/waves/round-84/w1/EX02Registers.md`.

## Self-evaluation

Accuracy 4: receipts preserve the observed ungraded status instead of asserting the frozen restored premise. Completeness 3: requested disclosure row cannot be represented honestly in the current ledger, and parent-owned verification remains unrun. Clarity 4: unchanged disclosure copy is explicitly labeled. Actionability 4: two ready-to-land TSV changes, exact diff and parent commands retained; disclosure decision remains. Conciseness 4: full receipts are separate from this report. Overall 3.8/5. Highest-impact improvement: L1 resolve the disclosure contract mismatch, then run committed-history gates. The user should agree this is a scoped implementation with an explicit blocker, not a complete C1 pass.
