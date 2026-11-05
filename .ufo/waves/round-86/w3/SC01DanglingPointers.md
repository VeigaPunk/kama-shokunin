# SC01DanglingPointers — round-86 per-surface recon (w3)

Target: the terminal record at `bafae7afb41843564ac2468d28beb8e0bb98e8e6` (ancestor of lane HEAD
`84e6f4573c2a0120def1cb8a37821a8c000686bb`). Full findings with commands and output lines:
`.ufo/waves/round-86/w3/out/SC01DanglingPointers/findings.md`.

## Verdict per item

| # | Item | Verdict |
|---|---|---|
| V1 | Cited paths exist at the tip | PASS — 86/86 lane-relative paths resolve (`git cat-file -e bafae7a…:<path>`); the plan's `scripts/sources-census.sh` is an absolute fleet path that exists on disk |
| V2 | Cited revisions resolve | PASS — 12 distinct revisions, all `git rev-parse --verify` OK; base is an ancestor of the freeze |
| V3 | Frozen counters at base reproduce the frozen before receipts | PASS — c1 `mismatches=3 … newest_gate=85 newest_closure=85` (exit 1), c2 `killed=3 escaped=2 arms=unknown owners=3/5` (exit 1), c3 `could-not-evaluate: no tools/round86-pin-origin.py at 3ff23da3…` (exit 2) — byte-identical to `measured/before/*.out` |
| V4 | Counters at the tip reproduce the after receipts | PARTIAL — c1 identical; c3 identical and live-verified today (`PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0`); **c2 differs on the PRISTINE line** → F1. All three selftest receipts reproduce byte-for-byte (17/0, 13/0, 7/0) |
| V5 | Committed mutant driver re-runs | PASS — `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0` |
| V6 | Three capability rows in the canonical table | PASS — `SELFDESC_CANON_V2 canon_round=86 canon_rows=52 invisible=0`; the three names appear in both the canonical table (5355–5357) and the mirror (176–178), sets and order identical |
| V7 | Three capability rows in the PROVINCE.md surface list | PARTIAL — all three tools named in PROVINCE.md (408/411/415) but not in the "Owns (surfaces)" table cell → F9 |
| V8 | Coverage row's surface hash / count re-derive | PASS — `c7589cc881cd21fb814be2ee9f4e0f7668deff2e192ca5103b0212b56826f95b`, 419 lines, knowledge count 57 — at `bafae7a` and at HEAD |
| V9 | Registry rows / counts | PASS — 317→319 rows, A 302→304, mined 284→286, S576 `used-by` extended, S578 §4.5 / S579 §4.4 mined, `kama ok …/corpus/SOURCES.md` exit 0 with the disclosed W04s |
| V10 | CommonMark quotes verbatim | PASS — all three quotes FOUND in the committed spec copy; section numbers confirmed (atx 4.2, indented **4.4**, fenced **4.5**) |
| V11 | Frozen predicate == instruments' `PREDICATE` | PASS — C1 (after joining the plan's 3-line blockquote), C2, C3 all byte-equal |
| V12 | Append-only acceptance rows | PASS — exactly 15 "round-86 accepts" rows over the four cited commits |
| V13 | R84V5 erratum's own claim | PASS — `round-84/measured/before/red-selfrecord.out` really is MISSING; `round-84/measured/after/c2-red.out` exists with the exact header the erratum describes |
| V14 | Lesson M1's round-85 evidence | PASS — the fenced-shadow fixture and CR01Cheats receipts exist and match the description |

## Findings — the record's own numbers against committed bytes

- **F1 (HIGH)** `.ufo/waves/round-86/measured/after/c2.out` line 7 reads
  `DEBT_MUTANT_OWNERS_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34`; the committed tree produces
  `pass=34 fail=0` (round-81 shape, `tools/round81-append-debt.py:689`). The receipt is the pre-EX02GateArms
  shape and does not reproduce at `bafae7a` **or** at its own commit `c5d71b7a`. Headline claim line unaffected.
- **F2 (HIGH)** `corpus/lessons/round-86.md:59` quotes `RENDERED_CELLS_MUTANTS mutants=7 killed=7 escaped=0`
  from `.ufo/waves/round-86/measured/after/c1-mutants.out`; that receipt says `mutants=10 killed=10`. The
  quoted token is absent from the cited file; SCORECARD/LOG say 10/10. Still stale at HEAD.
- **F3 (HIGH)** Lesson M6 claims `classify()` "requires exactly one ARMS line (a summary with no declared
  population cannot reconcile)" and names an arm `no-arms-line`. The code enforces **at most** one
  (`arms_lines > 1`), skips every clause when the ARMS line is absent, and the real arm is
  `no-arms-line-disclosed-limit` expecting `escaped`. Probe:
  `classify("APPEND_DEBT_SELFTEST pass=0 fail=0\n","",0,"summary-cardinality") -> ('escaped', …, 'green summary')`;
  source mutation (ARMS print removed + summary forged) exits **0** green. The plan says "at most one" — the
  lesson is the outlier, and the plan's kill rule "a cardinality clause that a forged summary can satisfy"
  meets an undisclosed survivor.
- **F4 (HIGH)** The banner couples the round-85 gate receipt to `948dec78…`, where that receipt does not
  exist (`git cat-file -e 948dec78…:.ufo/waves/round-85/measured/after/gate.out` → fatal; introduced at
  `6abaf0a8`). `gate_fact` accepts *any* ancestor revision in the paragraph, and `6abaf0a8` is also in the
  paragraph, so `gate=1` is green through an incidental revision — contradicting lesson M5 / SCORECARD
  ("the receipt is read at the revision the banner names"). Fixed later by re-pointing the banner
  (`239a8f39`, `84e6f457`).
- **F5 (MEDIUM)** `SCORECARD.md:5271-5273` at the tip still carries the literal placeholders
  `--rev <measured> --work <scratch>` — the record's own counting command is not runnable as written
  (pinned only at `84e6f457`).
- **F6 (MEDIUM)** round-86 `measured/**` receipts carry no `# rev=`/`# cmd=` header (round-85's do), so
  `round72-receipt-tip-binding.py --round 86` and `round74-receipt-claim-binding.py --round 86` both exit 2
  (`RECEIPT_TIP_BINDING_UNREADABLE … .ufo/waves/round-86/count.py (SCORECARD.md:5262)`). Round 85 fails the
  same way, so the class is pre-existing, but round 86's receipts are tip-unbindable.
- **F7 (MEDIUM)** the frozen plan says "ONE v1 wave `w1`, 12 seats"; two 12-seat waves (`w1`, `w2`) ran and
  `w3` is dispatched, with the frozen plan unamended.
- **F8 (LOW)** the plan's "(§4.4/§4.5 fenced and indented code)" pairs the section numbers the wrong way
  round (spec: §4.4 indented, §4.5 fenced); the landed `S578`/`S579` rows and the lesson are correct.
- **F9 (LOW)** the three round-86 tools are named in PROVINCE.md's Round-86 note but not in its surface-table
  cell (no `tools/round8*` there — lane-wide convention, also true of rounds 80–83).
- **F10 (LOW)** `SCORECARD.md:182` still says the latest repertoire entries are round-83's, while the same
  line lists round 86 and the round adds three entries.

## Tools installed

None. Everything used was preinstalled (`git`, `python3`, `diff`, `grep`, `sha256sum`, `wc`); the pacman
pause was therefore not touched. Scratch `/fast/scratch/hyaku/kama-r86/SC01DanglingPointers/` removed before
yield; nothing under `/tmp` exceeded a few KB.
