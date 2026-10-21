VERDICT: partial - the two S057 Gate quotes are located verbatim in the opened ld.so(8) page and are 11 and 10 words, but no declared claim cites S057 by ID and S057's `used-by` names a registry that never mentions it.

Scope: S057 claim linkage, Gate quote location and length; read `corpus/lessons/round-19.md`, `tools/citation-provenance.py`, `tools/sources-append-only.py`, `registry/required-citations.json`, `corpus/SOURCES.md:69`, `SCORECARD.md:821-835`. Receipts: `/tmp/kama-r19-CritSourced/out/RECEIPTS.md` (commands, exits, sha256). The lane changed repeatedly during this review; findings are against the final snapshot: lesson `cd99a767…`, tool `9632e4a9…`, SOURCES `93247553…`, SCORECARD `2347d84c…`, registry `bb47511d…`.

## Counterexamples

1. **No declared claim cites S057 by ID.** C1 (lesson lines 5-12) and C2 (13-18) never name S057. Gate row 1 ("admit (grounds C2)", line 27) links it by URL only; the ID appears in prose at lines 31-32. The only ID-level claim citation is SCORECARD 825-826, under C1: "S057's admission of the identity-boundary limit". C1 is the citation checker; the identity boundary is C2's concern (Gate row 1). Mis-attached.
2. **`used-by` is a false back-link.** Lesson 31-32 and SOURCES line 69 say S057 is used by `registry/required-citations.json`. The registry has three rows (`s055-commands`, `gate-live-1`, `c2-official-stdout`), each bound to `corpus/lessons/round-18.md`; none mentions S057. `sources-append-only.py --selftest` passes 42/42, including "only `used-by` changes" → exit 0, so the contract guard does not catch it.
3. **C1 coverage is narrower than the claim.** `citation-provenance.py` checks registry rows only (`required=3`). S057 is a web page, not a git blob, and has no row, so this round's only new material citation is never machine-checked. The 7→8 credit rests on the three round-18 pointers.

## Gate quotes: pass

- G1 "This expands to the directory containing the program or shared object": verbatim at man7 lines 154-155 under `<b>Dynamic string tokens</b>` (line 134); also in local man-pages 6.19. 11 words, stated 11.
- G2 "are searched only to find those objects required by DT_NEEDED": verbatim at line 115 (step (3), line 113). 10 words, stated 10.
- Both ≤25 words. The locator fails on a one-word mutant (DT_NEEDLED → exit 1), so it can fail.
- Fixed since the 03:29 copy: stated counts (were 14 and 11), "Lawful interception" row removed, reject row marked `[INFERENCE]` (page has 0 hits for digest/authenticat/checksum/lane).

## Smaller defects

- G2 stops before "(direct dependencies) entries", which carries the scope note. Extended quote through "entries" is 13 words, verbatim (receipts 9-10).
- Gate row 1's clause "so a launcher's bytes do not identify the libraries it loads" is not in the page; mark `[INFERENCE]`.
- Source version not recorded: page is Linux man-pages 6.19 (footer 2026-08-03).
- No round-19 search-log entry for S057's open in SOURCES.
- Lesson M1 says "14 total" selftest cases; the current selftest reports 15.

## Impacted axes

- **calibration** (lowest axis, C1 7→8): overstated coverage (3), mis-attached S057 (1), false back-link (2).
- **operability** (C2): the identity-boundary grounding sits under C1 in SCORECARD.

## Smallest safe correction (not applied; lane owner decides)

a. Lesson C2 (13-14): add "Grounded by S057 (Gate rows 1-2)".
b. SCORECARD 825-826: move "S057's admission of the identity-boundary limit" from C1 evidence to C2 evidence (828-835).
c. Lesson 31-32 and SOURCES line 69: `used-by` → `corpus/lessons/round-19.md, SCORECARD.md`. Do not add an S057 registry row; it is not a git blob.
d. Lesson C1 (7-8): "per material citation" → "per registry row (three round-18 pointers); S057 quotes are checked by hand (receipts)".
e. Gate row 2: quote "are searched only to find those objects required by DT_NEEDED (direct dependencies) entries" (13 words).
f. Gate row 1: mark the "so a launcher's bytes…" clause `[INFERENCE]`.
g. Optional: record "Linux man-pages 6.19 (2026-08-03)" in the Gate source; add a round-19 SOURCES search-log line for S057; change "14 total" to 15.

[INFERENCE] The S057-to-C1 placement looks like a drafting slip, since Gate row 1 says "grounds C2". The author has not confirmed it.

## Commands and exits (all exercised in /tmp/kama-r19-CritSourced)

- `curl -fsSL … ld.so.8.html` → 0 (sha256 `d9b7737e…`, fetched 2026-10-21T06:30Z)
- `man -P cat 8 ld.so` → 0 (local rendering sha256 `b1d98a59…`)
- `gate_check_current.py` man7 / local → 0 / 0 (RESULT=pass)
- `gate_check_extended.py` man7 / local → 0 / 0 (13/13)
- `gate_check.py out/negative-control.txt` → 1 (G2 located=no)
- `python3 tools/citation-provenance.py` → 0 (`required=3 found=3 verified=3 missing=0 mismatch=0`)
- `… --selftest` → 0 (`selftest: ok (15 cases)`)
- `… --docs out/negative-control.txt` → 1 (`missing=3`, the before-tokens state)
- `python3 tools/sources-append-only.py --selftest` → 0 (42/42)

## Limits and writes

- Not checked: C2 grid and receipt pin, the frontier census (rows 56), the official harness.
- No installs or updates; none to record.
- Lane: no edits. This report is the only lane write, at the Report trailer path. Re-run the S057 checks on the final commit, since the lane moved during review.
