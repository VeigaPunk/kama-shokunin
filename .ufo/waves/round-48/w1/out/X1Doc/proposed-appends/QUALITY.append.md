# Proposed append for `corpus/QUALITY.md` (drafted by seat X1Doc; append-only, never in place)

Anchor: end of `corpus/QUALITY.md` at `380bcdff9c8af06997c482f6eb03db926a794a2b` (400 lines; last line is the KQ71
row). Append the block below at EOF as new lines. `corpus/QUALITY.md` is contract row 3 (`A-corr`, region `*`), so an
append is compliant; nothing above is rewritten. The block supersedes the check cells of KQ67 (line 387), KQ70
(line 397) and KQ71 (line 398) and leaves every criterion's predicate unchanged.

---

## Correction — round 48: the KQ67/KQ70/KQ71 check cells under `append-only-audit/v3` (drafted by seat X1Doc at `380bcdff`)

Round 48 replaced `tools/append-only-audit.py` with schema `append-only-audit/v3` (tool sha256
`ec9c6d206fccfd9b9b04526b54da34207c48ab9f0768c3285128cd59fcf60f72`) and `registry/append-only-contract.tsv` with a
nine-row, five-cell file (sha256 `ca0618e50fadc4b0d53b0d8a61868b0ea7fbf33b3429c125a0d5643022a77075`; header
`path<TAB>rule<TAB>declared_at<TAB>region<TAB>note`). The three rows above keep their text; the measured values below
supersede their check cells. All figures were taken on a clone at `380bcdff9c8af06997c482f6eb03db926a794a2b`
(evidence `.ufo/waves/round-48/w1/out/X1Doc/evidence/`); the integration tip carries a tenth row
(`corpus/knowledge/error-is-not-a-verdict.md`, `only=## Round24`) and 90 files, which changes neither the predicates
nor the exit semantics — the C1 counter's required-row set is unchanged and extra rows are tolerated.

**KQ67 (line 387).** The `deleted`/`restored_at_tip` pair no longer exists: v3 prints
`event <commit12> <file> deleted=N graded=G ungraded=U restored_max=K held_at_to=H status=S restored_best=<c12|->
restored_by=<c12|->` and `--json` prints schema `append-only-audit/v3` with `declarations`, `vanished`,
`unmatched_patterns`, `binary_changes` beside `files`, `commits`, `events` and `summary`. Read the pair a KQ67 report
must name as `deleted`/`graded` with `restored_max` (and `held_at_to` for the tip), and do not explain an `ungraded`
line, which sits outside the verdict. The cited command
`python3 tools/append-only-audit.py --repo <clone> --to <tip> --json` now exits 1 on more than a partial or
unrestored event — also on `regressed`, a `vanished` declared path and an unbound declaration
(`tools/append-only-audit.py:469-474`); measured at `3a09a1d9` it exits 1 with `partial=0 unrestored=0 regressed=1`.
The row's worked pair therefore reads, at `380bcdff`:
`0718b6ab SCORECARD.md deleted=2421 graded=2349 ungraded=72 restored_max=2349 held_at_to=2349 status=restored` and
`dd9f5dc6 SCORECARD.md deleted=31 graded=14 ungraded=17 restored_max=14 held_at_to=14 status=restored` — both
`restored`, neither `partial`; the `2416/2417` and `24/31` figures are v1/v2 readings of the same two events. The
row's own point — that a file whose history holds a partial event is not called append-only until that event is
explained — is unchanged; under v3 that condition is read on `graded` lines and an `ungraded` head section is not an
event.

**KQ70 (line 397).** The predicate stands and is met. Its cited check does not: the round-47 counter reads the
contract at `--tip` with a four-cell header and the v2 JSON, so at the v3 build it reports
`selftest=1 contract=0 lane=0 fixture=0 stable=0 files=0 lane_events=0 lane_mismatch=-1 fixture_mismatch=-1 met=False`,
exit 1 — `python3 tools/round47-append-audit-v2-check.py --repo <clone> --tip
380bcdff9c8af06997c482f6eb03db926a794a2b --scratch <dir>`, `detail: contract: header line is not exactly
path<TAB>rule<TAB>declared_at<TAB>note`, `detail: fixture: tool exit=2, stdout is not one JSON object` — while the
same command at its own build tip reads `… met=True`, exit 0. The graded form is now
`python3 tools/round48-append-audit-v3-check.py --repo <clone> --tip <tip> --scratch <dir>`:
`selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89
fixture_fail=0 met=True`, exit 0, at `380bcdff`. The refusal of a hunk count that differs from numstat moved from
`tools/append-only-audit.py:203` (v2) to `:400` (v3, `raise AuditError(f"{c[:12]} {f}: hunk count {len(dl)} !=
numstat {ns[f]}")`).

**KQ71 (line 398).** Three parts of the row are superseded.

1. *The count.* The check
   `python3 tools/append-only-audit.py --repo <clone> --to <tip> --contract registry/append-only-contract.tsv --json`
   prints schema `append-only-audit/v3` and `files` equal to the expansion of the nine-row contract: 89 paths at
   `380bcdff` (`commits=311`, exit 0) and 87 at the cited `3a09a1d9` (`commits=303`, exit 1) — not 85, because the
   round-48 rows add `registry/report-landing-errata.tsv` and `corpus/knowledge/consumer-registry.md`. "Exits 1
   while any event is partial" understates the exit: at `3a09a1d9` it exits 1 with `partial=0 unrestored=0
   regressed=1` (the `0718b6ab` SCORECARD event reads `held_at_to=2348` against `restored_max=2349`; the round-48
   build appends the round-45 and round-46 banners, which is why `380bcdff` reads `regressed=0`, exit 0).
2. *The scoping.* A row's `region` cell now scopes the claim; **KQ72**, added in the round-48 criteria section of
   this file, carries that requirement (the three region forms, the eligibility rule for an `exempt` title, and the
   binding rule for a declaration). KQ71's own shape sentence is read with it: a row has five cells, not four, and a
   `region`-scoped row declares its claim over that region only.
3. *The counterexample cell.* "`corpus/knowledge/consumer-registry.md:30` declares its section append-only and has no
   row" is superseded: row 9 covers it (`A-corr`, `only=## Errata@corpus/knowledge/consumer-registry.md:30`), the
   tool reports that declaration `ok: true`, and the heading census the same cell cites reads
   `headings=17 covered=15 uncovered=2` at `380bcdff` with both uncovered headings the `SKILL.md:1434` and
   `SKILL.md:1444` topic labels the cell already dispositions. `corpus/knowledge/context-capacity.md:245`
   (`## Errata — round 26`) remains uncovered and must still be dispositioned by a round that cites it, because its
   heading does not carry the word.
