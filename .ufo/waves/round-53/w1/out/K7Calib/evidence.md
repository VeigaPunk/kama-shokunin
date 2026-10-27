# K7Calib evidence — round 53 C2 framing checks

## 1. Independent counter rerun at the build tip (third run, fleet HEAD moved between runs)

$ python3 tools/round53-cited-path-check.py --repo $S/lane --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 --scratch $S/c2runb
tip=c22602bd8d83ab26349d1087e916ca537ee4f9d1 fleet=33540c6e4587735e67a393736bd97f1126515d5c
fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
exit=0   (wall 1.97 s)

L1 measured receipt (.ufo/waves/round-53/measured/c2-build.out) reads identically except fleet=ee9f7341...; my two runs saw fleet=71256a5... and 33540c6... — the fleet advanced twice between runs and every count is unchanged.

## 2. Base vs build on C2 surfaces (git diff 4229ea1b... c22602bd...)

- SCORECARD.md: +4 lines only — appended "### Evidence-pointer corrections (round 53)" section (file end, lines 3027–3029 of 3029).
- SKILL.md: two 1-line in-place corrections (line 113 scripts/local-helper.mjs -> ~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs; line 895 tests/report-audit/… -> tests/report-audit/). No other SKILL.md change.
- registry/cited-path-corrections.tsv: new file, 27 lines = 9 comment lines + 14 data rows (10 SCORECARD.md, 4 SKILL.md).
- Nothing else in the build touches SHONEN.md (verified: grep cited-path-corrections|round53-cited-path on SHONEN.md -> no match).

## 3. Sentence-level inspection of the 16 base misses (build tree)

Self-disclosing sentences (claim and absence in the same sentence):
- SCORECARD.md:491  "Use absent `.ufo/waves/round-14/frozen/before/tools/kama-ollama-evidence.py`"
- SCORECARD.md:1732 "cites `.ufo/waves/round-31/c2/c2-tip.json`, which does not exist; ..."
- SCORECARD.md:1741 "`...utils.hpp` was a committed `404: Not Found` body" (deleted 9874e455)
- SCORECARD.md:1844/1901  round-999/count-c999.py — deliberately dangling missing-path control
- SCORECARD.md:2228 "N3: ... `c2/base.out` was never written ... The row stays as filed."
- SCORECARD.md:1503 ConfirmM01..11 range notation; `.ufo/waves/round-29/w1/out/ConfirmM01..11/` literal never existed but ConfirmM01..ConfirmM11 each exist (ls-tree verified).

Existence-claiming sentences over dead paths (NOT self-disclosing):
- SCORECARD.md:2136 "wave-1 fetches returned HTTP 200, 6243 and 2820 bytes, receipts in `.ufo/waves/round-38/w1/out/FetchS352/` and `.../FetchS353/`" — git ls-tree -r at the build tip: no path matching FetchS35* or ExecTagInventory exists anywhere in the tree.
- SCORECARD.md:2136 "... it returned HTTP 403 with "API rate limit exceeded" (`.ufo/waves/round-38/w1/out/ExecTagInventory/api-status.txt`, `api-body.json`)" — same dead directory; only api-status.txt is a parsed citation (full path), api-body.json is a short-form span.
Ledger rows for both: class never, note "no seat report of that name was committed in round 38" (FetchS352 row does not name line 2136; neither note quotes the sentence).

## 4. Ledger reachability at the build commit

- SCORECARD.md names the ledger exactly once, in the appended end section (line 3029). Lines 491/1503/1732/1741/1844/1901/2136/2228/2904 carry no local pointer.
- SKILL.md at the build: grep -n 'round53-cited-path|cited-path-corrections|Evidence-pointer' SKILL.md -> no match. The four tools/server/*.cpp upstream rows and the fixed row are discoverable from SKILL.md only by guessing the ledger filename. (SKILL round-53 instrument registry entry is a known pending integration item, not in the build.)
- SHONEN.md: no unresolved citations at base or build (counter output detail lines name only SCORECARD.md and SKILL.md tokens).

## 5. Three-round framing comparison (counter docstrings)

- round51-append-audit-v6-check.py: "does the lane's append-only self-description hold for every deletion its history holds ... every graded line that is gone ... either restored or disclosed by name" (165 lost lines disclosed).
- round52-append-restore-check.py: measured corr_lost 151 -> 0, disclosed 10 (SCORECARD round-52 measured results).
- round53-cited-path-check.py: unresolved 16 -> 0 undisclosed, 14 disclosed.
All three: closure of a registered miss ledger, score 7 -> 7 each time.

## 6. Frozen constraints that force the disclosure-only disposition for SCORECARD

- Counter lane leg: "every token SCORECARD.md cites at --base is still cited there (dropped=0 ...)" — removal or in-place correction of a cited token trips the kill.
- C2 docstring: "the file is append-only outside its head tables".
- Round-52 lesson Mistakes #4 fix precedent: "the sentence is amended at integration (SKILL.md is not an append-only file)" — repair where allowed, disclose where not; the build does exactly this.
