# ScoutPM08Wording — routed defect: PM08 static-only wording

VERDICT: Two live SKILL.md lines still carry the older static-only/settled
wording (SKILL.md:870 and SKILL.md:975-976), one historical LOG.md entry does
(LOG.md:1501-1502, append-only), and every other live PM08 statement already
matches "manual, review-only, unexecuted, uncredited". Advice only; no file
was edited.

## Commands and results

1. `grep -rn "PM08" tests tools SKILL.md corpus SCORECARD.md --exclude-dir=__pycache__`
   -> exit 0. Full output: `.ufo/waves/round-25/a2-build/out/ScoutPM08Wording/census.txt`.
2. `grep -rn "static-only" --exclude-dir=.ufo --exclude-dir=__pycache__ --exclude-dir=.jj --exclude-dir=.git .`
   -> exit 0; live hits are SKILL.md:870, LOG.md:1502, the spot-check finding
   itself (corpus/lessons/round-24-verifier-spotcheck.md:84) and an unrelated
   round-18 row (corpus/lessons/round-18.md:285, endpoint-probe caveat).
3. `git --no-optional-locks show 1fc41e346853afd98cbd7010af5db4e54dc877f7:SKILL.md`
   -> exit 0; lines 870 and 975-976 at the lane pin are byte-identical to the
   working tree text quoted below, so the defect exists at the pin, not only
   in a dirty checkout.
4. Inventory shape read from `tests/report-audit/promisor-mutants.py` by
   `exec` of the module top level with `__name__="kama_pm08_probe"` (main is
   guarded at :1783; no grid, pristine, git or mutant ran) -> exit 0:
   11 entries, ten `execution="grid"` with non-empty `expect_rows`, and
   `PM08-no-lazy-fetch-review-only` with `expect_rows=0`, `alternatives=0`.
   Output: `out/ScoutPM08Wording/inventory-shape.txt`.
5. `grep -rn "Promisor mutation experiment"` repo-wide -> only SKILL.md:870
   holds the live registry row; no duplicate row elsewhere.
6. No `lsp` device is mounted in this seat (`read xd://lsp` -> "No such tool:
   xd://lsp. Mounted devices: ast_edit, debug"), so this prose trace is
   text-level; no language-server semantic proof is claimed.

## Table — path:line -> current text -> conflict -> proposed text

| path:line | current text (exact) | conflicts with manual/review-only/unexecuted/uncredited? | proposed text |
|---|---|---|---|
| SKILL.md:870, cell 5 | `11 named mutations with declared target cells; PM08 no-lazy-fetch removal static-only and never executed; original/amended expectation manifest in the grid` | YES, twice. "static-only" is the retired status spelling (canonical status is `review-only`). "PM08 no-lazy-fetch removal" names an edit that does not exist: the live entry has `alternatives=0`, and the review note says no mutant is built. "declared target cells" also implies PM08 has `expect_rows`, but it is `[]`. | `11 named mutations: ten executable with declared target cells; PM08 is a manual review-only note, unexecuted, uncredited, with no assertion of any kind; original/amended expectation manifest in the grid` |
| SKILL.md:975-976 | `executable operators plus one manual PM08 review note: PM08 (removing the` / `` `--no-lazy-fetch` gate) is settled by uncredited manual source inspection —`` | YES. "is settled by" claims a settled result, while corpus/lessons/round-24.md:546-549 says PM08 is "not 'settled' behavioral evidence"; "removing the gate" is the retired operator spelling. The rest of the sentence (never constructed/executed/credited) is already correct. | `executable operators plus one manual PM08 review note: PM08 rests on` / `uncredited manual source inspection of the candidate's repository-reading` / `wrappers — never constructed, never executed, never credited with a kill,` / `and no permanent AST, text or wiring assertion exists for it. Static anchors` |
| LOG.md:1501-1502 | `leaks and uncompiled/unapplied mutants receive no credit. PM08 remains` / `static-only; no new transport/execution payload is required.` | YES on content, but this is an append-only historical W1 entry. LOG.md:1544-1546 ("PM08 is manual/uncredited, not a permanent wiring assertion or executable mutation") and :1600-1601 ("PM08 manual/uncredited status") already say the opposite, so the file is internally inconsistent. | Leave the historical lines; append an erratum (exact block in `out/ScoutPM08Wording/proposed-wording.txt`, following the LOG.md:644 and :1165 erratum precedent). In-place alternative is given there but not recommended. |

Exact whole-row replacement for SKILL.md:870 (still 7 cells, 8 pipes, matching
the table header) is in
`out/ScoutPM08Wording/proposed-wording.txt`. The proposed cells keep the
canonical vocabulary used by tests/report-audit/promisor-mutants.py:419-437,
corpus/lessons/round-24.md:318-327 and SKILL.md:1032, and introduce no new
claim.

## Live lines already correct — no change

- SKILL.md:1032-1035: "PM08 stays filed/manual/unexecuted/uncredited, with no
  permanent AST/text/ wiring assertion." Matches canonical. It is the direct
  internal contradiction of SKILL.md:870 in the same file.
- SCORECARD.md:1229: "PM08 is manual/unexecuted/uncredited".
- corpus/lessons/round-24.md:318-327: heading "PM08 carries no assertion";
  "the static/AST/source-text/wiring assertion proposal is **declined, not
  repinned**. PM08 remains a manual review-only note: no alternatives, no
  assertion of any kind, no construction, no execution, no kill credit".
  Describes the declined proposal, does not assert PM08 is static-only.
- corpus/lessons/round-24.md:521 ("manual PM08 earns no behavioral credit"),
  :546-549 ("merely a FILED, manual, unexecuted, uncredited note, not
  'settled' behavioral evidence").
- corpus/lessons/round-24-verifier-spotcheck.md:83-85 (the finding itself) and
  :151-152 (routing instruction).
- tests/report-audit/promisor-mutants.py:57-63 (module docstring: "review-only
  and uncredited ... not a proof about every git call"), :419-437 (the entry),
  :771-779 (`--anchors` skips review-only), :893-900 (runner status
  `review-only`, `executions=0`), :1420-1429 (selftest refuses a grid call or
  kill credit for PM08).
- No test or tool asserts the strings "static-only", "PM08 no-lazy-fetch
  removal" or "Promisor mutation experiment": `grep -rn "static-only\|PM08"
  tests --include=*.py` hits only promisor-mutants.py lines 57/424/1424/1427,
  and no test reads SKILL.md. [INFERENCE] A wording edit therefore cannot
  break a literal-match check; unverified that no external consumer copies
  the row.

## Frozen round-24 wave files — do not edit

These carry the older static-only vocabulary but are immutable evidence or
superseded proposals, not live statements:

- `.ufo/waves/round-24/build/out/MutationOracle/mutation-inventory.md:9,20`
  ("PM08 is static-only and is never executed against the grid") — superseded
  build-wave inventory.
- `.ufo/waves/round-24/fixes/MutationEvidence/inventory-v2.json:485` and
  `promisor-mutants.py:69,421` (`execution": "static-only"`) — v1/v2
  proposals; V3 onward replaced them (`MutationEvidenceV3/inventory-v3.json:3`:
  "PM08 is a historical review-only note: never applied, never executed,
  never credited with a kill. No source assertion ... is made for it").
- `.ufo/waves/round-24/fixes/MutationEvidence/rationale.md:148` — describes
  the v2 runner's status string.
- `.ufo/waves/round-24/falsify/advice/DocSkill.md:156` verified the then-live
  row as true against the then-live `static-only` inventory; that is why the
  row went stale when review-only landed.
- `.ufo/waves/round-24/postfix/advice/FinalPM08.md:17` is the earlier record
  of this same debt (it already names LOG.md:1501-1502 and SKILL.md:975-976);
  it is a finding, not a live statement.

## Confidence and remaining unknowns

- High confidence that SKILL.md:870 is "the live registry's older static-only
  wording": it is the only live registry row (grep 5), it says "static-only",
  and it contradicts SKILL.md:1032 and SCORECARD.md:1229 in the same tree.
- High confidence on SKILL.md:975-976 being a second, adjacent residual:
  corpus/lessons/round-24.md:546-549 explicitly rejects "settled", and
  FinalPM08.md:17 recorded the same line.
- Medium confidence on whether L1 wants LOG.md corrected in place; the lane's
  own erratum precedent (LOG.md:644, :1165) argues for append.
- Unverified: whether any downstream copy of the SKILL.md registry row exists
  outside this lane. The lane-wide `find -name SKILL.md` returned only
  `./SKILL.md`.
- Unverified: whether a generator regenerates SKILL.md rows; no generator
  reference to SKILL.md was found in tools/ or tests/, but I did not trace a
  writer.

## Files written

- `.ufo/waves/round-25/a2-build/advice/ScoutPM08Wording.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/ScoutPM08Wording/census.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/ScoutPM08Wording/proposed-wording.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/ScoutPM08Wording/inventory-shape.txt`

No production file was edited. No llama-server child was started and no
registered consumer was probed. No tool was installed or upgraded.

Report: .ufo/waves/round-25/a2-build/advice/ScoutPM08Wording.md
