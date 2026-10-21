VERDICT: partial - the C1/C2 counts in the round-19 SCORECARD reproduce from the working tree (C1 before exit 1 missing=3, after exit 0 verified=3; C2 no-pin grid 0/3 exit 1, pin 3/3 exit 0), but the official L1 measurement is pending and three evidence pointers need correction before the table is final.

# DraftScorecard — round-19 measured-results skeleton (advice)

Work copy: `/tmp/kama-r19-DraftScorecard` (cp -a of the lane; lane not modified).
Draft: `/tmp/kama-r19-DraftScorecard/out/SCORECARD-r19-draft.md` (table skeleton,
placeholders `⟦PENDING⟧` only for L1 official run/commit/spot-check fields).
Receipts: `/tmp/kama-r19-DraftScorecard/out/` (c1-*.stdout, c2-counting.stdout,
out/before/, out/receipt.sha256). Installs: none. Servers: none.

## Measured (executed in copy)
- `python3 tools/citation-provenance.py` → exit 0, `required=3 found=3 verified=3 missing=0 mismatch=0`.
- `python3 tools/citation-provenance.py --selftest` → exit 0, `selftest: ok (5 cases)`.
- Before-state: base-commit (`1b85a24`) copies of the four default docs → exit 1, `required=3 found=0 verified=0 missing=3 mismatch=0`; `--docs /dev/null` proxy gives the same, exit 1.
- C2 `tests/llamacpp-live/install-tree-grid.py` on `.ufo/waves/round-18/live-recovery/receipt-1.json`: no pin → `baseline=VALID members=3 rejected=0/3 tree_pin=off`, exit 1; `--tree-sha 6c2163…85a2` → `rejected=3/3 tree_pin=on`, exit 0.
- Gate `check-receipt.py … --expect-install-tree-sha256 <tree>` → VALID exit 0; all-zero pin → INVALID exit 1.
- `py_compile` of both new tools → exit 0.

## Defects to route (evidence pointers)
1. **Argv elided.** SCORECARD round-19 C2 row cites `python3 tests/llamacpp-live/install-tree-grid.py … --receipt …` with `…`. The full argv (model/server/impl/probe/tool pins) is in `out/c2-counting.sh`; the scorecard should carry it verbatim.
2. **Receipt-path ambiguity.** The C2 grid uses `live-recovery/receipt-1.json` (sha256 `89728a02…`), while the S055 erratum in `corpus/SOURCES.md` describes `live/receipt-1.json` (sha256 `e616f67e…`, different bytes). Both exist. The round-19 SCORECARD should name which receipt each claim measures.
3. **Checker silent on stale tokens.** `tools/citation-provenance.py` matches a token only when its digest equals the registry digest. A wrong-digest duplicate is ignored, not counted (mutant M1: exit 0, `found=3 verified=3`). `mismatch` is reachable only if doc and registry carry the same stale digest. This is the candidate (a) in `corpus/lessons/round-19.md` and should be mined as a real gap, not a settled one; there is no document-precedence rule.
4. **Before-line wording.** SCORECARD round-19 C1 "before" quotes `required=3 found=0 verified=0 missing=3 exit 1`; the actual line also prints `mismatch=0` and three `missing:` detail rows. Minor; quote exactly.

## Pending (not measured by me)
- Official `.ufo/waves/round-19/runs/run.py` on the measured commit (exits, `commands.json` digest).
- Official C1 after-count on that commit; C1 before via `git show 1b85a24:<doc>` checkout rather than the proxy.
- S057 census (lesson claims rows 56, A 53, C 3); not run here, no census script path confirmed in this copy.
- Outside non-author admit/reject sample; C1 score 7→8 stays self-assessed until it is recorded.

## Calibration note
C2 pin binds observed bytes (receipt's own tree digest); it does not show the grid covers every swap class (`[INFERENCE]`). Keep the S057 identity-boundary disclosure in the official row.
