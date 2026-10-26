# X1Doc — documentation drift from the v3 contract format (population census, measurements, verdicts)

Seat X1Doc, round 48 wave 1. Measured point: lane commit
`380bcdff9c8af06997c482f6eb03db926a794a2b` (the build; base `33e005827742b29772b153cda036ec9f27f653be`),
on a private `git clone --shared` of the lane checked out at that commit. Read-only: no lane file was edited.

Instrument at the measured point (`evidence/00-context.txt`):

| item | value |
|---|---|
| `tools/append-only-audit.py` sha256 | `ec9c6d206fccfd9b9b04526b54da34207c48ab9f0768c3285128cd59fcf60f72` (schema `append-only-audit/v3`) |
| `registry/append-only-contract.tsv` sha256 | `ca0618e50fadc4b0d53b0d8a61868b0ea7fbf33b3429c125a0d5643022a77075` |
| contract shape | header `path<TAB>rule<TAB>declared_at<TAB>region<TAB>note`, **nine** rows (five cells each) |
| audited expansion at `380bcdff` | `files=89`, `commits=311` |
| tool selftest | `AOA_SELFTEST pass=27 fail=0` |

Population (as the item names it): `SKILL.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/knowledge/*.md`,
at `380bcdff`. Census method: `git show 380bcdff:<file> | grep -n` over
`append-only-audit|append-only-contract|append-only/v|restored_at_tip|four cells|seven rows|five files|85 files`,
plus a reading of every surviving hit. Lines outside the four surfaces (lessons, SCORECARD round sections, `.ufo/`)
are history or out of population and are not graded here.

## 1. Census: which population lines describe the instrument

| surface:line | what it says | verdict at `380bcdff` |
|---|---|---|
| `SKILL.md:1441` | round-46 C2 counter row; event format `restored_at_tip=` | **stale command** (F7): the counter's legs read the tool at `--tip`, which is now v3 |
| `SKILL.md:1442` | round-46 tool row; `restored_at_tip`, `--files` only, exit map | **stale** (F6): v3 output fields, exit map, `--contract` |
| `SKILL.md:1450` | round-47 C1 counter row; "**four cells per row**" | **stale** (F4): five cells; cited counter reads `contract=0 met=False` |
| `SKILL.md:1453` | round-47 tool row; `"schema": "append-only-audit/v2"`, `pass=19` | **stale** (F5): schema v3, `pass=27`, new JSON keys |
| `corpus/QUALITY.md:387` (KQ67) | requires the `deleted`/`restored_at_tip` pair; "exit 1 when any event is partial or unrestored" | **stale** (F3): no `restored_at_tip`; exit also on regressed/vanished/bad declarations |
| `corpus/QUALITY.md:397` (KQ70) | "Check: `round47-append-audit-v2-check.py …` reports `lane=1 fixture=1 stable=1`"; `tools/append-only-audit.py:203` | **stale check** (F1): measured `met=False`, exit 1; the raise moved to `:400` |
| `corpus/QUALITY.md:398` (KQ71) | check prints `files` = expansion "85 paths at `3a09a1d9`"; "exits 1 while any event is partial"; counterexample "`consumer-registry.md:30` … has no row"; `headings=13 covered=11 uncovered=2` | **stale** (F2): 89/87 paths, region cell absent from the criterion, the row now exists, census reads 17/15/2 |
| `corpus/README.md:759-761` | "the five files the lane treats as append-only" | **stale** (F8): nine rows, 89 paths (also already stale in round 47, disclosed) |
| `corpus/README.md:776` | "append-only-audit v2 with a declared contract" | **stale** (F9) |
| `corpus/README.md:782-783` | "schema `append-only-audit/v2` … whose seven rows" | **stale** (F9) |
| `corpus/README.md:788` | "At `3a09a1d9` that contract expands to 85 files" | **stale** (F9): 87 with the v3 contract |
| `corpus/README.md:790-792` | `python3 tools/append-only-audit.py --repo <clone> --to 3a09a1d9` reports `files=85 … partial=2`, exit 1 | **stale command** (F9): measured exit 2, `could-not-evaluate: contract header …` |
| `corpus/README.md:803-806` | round-47 counter reads `selftest=1 contract=1 … files=85 … met=True` | **stale** (F9): true only at its own build tip; `met=False` at the build |
| `corpus/README.md:807-810` | "the tool … never reads its `rule`, `declared_at` or `note` cell (`tools/append-only-audit.py:184`)" | **stale** (F10a): v3 reads `declared_at` and `region`; `:184` is `row_token()` now |
| `corpus/README.md:811-814` | "(1) The `SCORECARD.md` carve-out is declared but not applied" | **superseded** (F10b): graded 2349/72 and 14/17, both `restored`, exit 0 |
| `corpus/README.md:815-821` | "(2) … no contract row covers `corpus/knowledge/*.md`" | **superseded** (F10c): row 9, `only=## Errata@…:30` |
| `corpus/README.md:821-826` | "(3) … at `--threshold 1` the same tip reports 91 events — 12 restored, 8 partial, 71 unrestored …" | **stale numbers** (F10d): 96 events at `3a09a1d9`, 98 at `380bcdff` |
| `corpus/README.md:895-898` | "The instrument's edges: region scoping … the `SCORECARD.md` head carve-out that the tool cannot apply, the 20-line threshold (91 events at 1), and … a lane file declared append-only but missing from the contract is not detected" | **partly superseded** (F11): the first two edges are applied; the count is stale; the last clause still holds |
| `corpus/knowledge/consumer-registry.md:30` | `## Errata — 2026-10-14 re-census (append-only; rows below keep their round-1 text)` | **current, no drift**: it is row 9's `declared_at`; the tool reports `ok: true` |
| `corpus/knowledge/context-capacity.md:245` | `## Errata — round 26` (no "append-only" wording) | **current, no drift**: no row, and it makes no claim; a round citing it must disposition it under KQ71 |
| `corpus/knowledge/served-identity-crosswalk.md:94` | "registry cells are append-only" | **current, no drift**: a `corpus/SOURCES.md` A-row claim (`SKILL.md:578`), not this instrument |
| `corpus/knowledge/instrument-run-agreement.md:20` | `tools/sources-append-only.py` receipt | **current, no drift**: a different tool |

`corpus/knowledge/` carries **no** line citing `append-only-audit`, the schema string or a cell count — the whole
surface is drift-free for this item; nothing is proposed for it beyond the counterexample wording that lives in
`corpus/QUALITY.md:398` and `corpus/README.md:815-821`.

## 2. Cited commands, run at `380bcdff`

All commands were run with the clone's working tree at `380bcdff`, so the contract read from a path argument is the
v3 file, and the tool used is the v3 tool. Exit codes are recorded in each evidence file.

| # | command (as cited) | result at `380bcdff` | exit | evidence |
|---|---|---|---|---|
| 1 | `append-only-audit.py --repo . --to 380bcdff` (KQ67 form, text) | `summary commits=311 files=89 events=5 restored=5 partial=0 unrestored=0 ungraded=0 ungraded_lines=89 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0` | 0 | `evidence/01-audit380-text.out` |
| 2 | `append-only-audit.py --repo . --to 380bcdff --json` (KQ67's check) | schema `append-only-audit/v3`; keys `binary_changes, commits, contract, declarations, events, files, schema, summary, threshold, to, unmatched_patterns, vanished`; event keys `commit, deleted, file, graded, held_at_to, restored_best, restored_by, restored_max, status, ungraded` — **no `restored_at_tip`** | 0 | `evidence/02-audit380.json` |
| 3 | `append-only-audit.py --repo . --to 3a09a1d9` (README `:790`, default contract at `<to>`) | `could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>region<TAB>note` | **2** | `evidence/03-audit-3a09-defaultcontract.out` |
| 4 | `append-only-audit.py --repo . --to 3a09a1d9 --contract registry/append-only-contract.tsv` | `commits=303 files=87 events=5 restored=5 partial=0 unrestored=0 ungraded=0 ungraded_lines=89 regressed=1 vanished=0 unmatched=0 binary=0 bad_declarations=0` | **1** | `evidence/04-audit-3a09-v3contract.out` |
| 5 | `round47-append-audit-v2-check.py --repo . --tip 380bcdff --scratch <dir>` (KQ70's check) | `selftest=1 contract=0 lane=0 fixture=0 stable=0 files=0 lane_events=0 lane_mismatch=-1 fixture_mismatch=-1 met=False`; `detail: contract: header line is not exactly path<TAB>rule<TAB>declared_at<TAB>note`; `detail: fixture: tool exit=2, stdout is not one JSON object` | **1** | `evidence/05-v2counter-380.out` |
| 6 | same, `--tip 3a09a1d9` (its own build tip) | `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True` | 0 | `evidence/06-v2counter-3a09.out` |
| 7 | `append-only-audit.py --repo . --to 380bcdff --contract registry/append-only-contract.tsv --json` (KQ71's check) | schema v3, `files` = 89 paths, `restored=5 partial=0 regressed=0 ungraded_lines=89` | 0 | `evidence/07-kq71-380.json` |
| 8 | same at `3a09a1d9` (KQ71's cited tip) | schema v3, `files` = **87** paths (not 85), `partial=0 unrestored=0 regressed=1` | **1** | `evidence/08-kq71-3a09.json` |
| 9 | `append-only-audit.py --repo . --to 380bcdff --threshold 1` (README `:822`) | `events=98 restored=14 partial=4 unrestored=62 ungraded=18 ungraded_lines=186` | 1 | `evidence/09a-th1-380.out` |
| 10 | same at `3a09a1d9` with the v3 contract (README's own tip) | `events=96 restored=12 partial=4 unrestored=63 ungraded=17 ungraded_lines=177` — README says 91 / 12 / 8 / 71 | 1 | `evidence/10a-th1-3a09.out` |
| 11 | `append-only-audit.py --selftest` (SKILL `:1453`) | `AOA_SELFTEST pass=27 fail=0` — row says `pass=19` after the round-47 wave | 0 | `evidence/11-selftest.out` |
| 12 | `round48-append-audit-v3-check.py --repo . --tip 380bcdff --scratch <dir>` (the round-48 counter) | `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True` | 0 | `evidence/12-v3counter-380.out` |
| 13 | `round46-append-audit-check.py --repo . --tip 380bcdff` (SKILL `:1441`) | `selftest=1 fixture=0 lane=0 table=1 lane_events=5 lane_unrestored=0 lane_partial=2 met=False`; `detail: fixture full ok=False rc=2`; `detail: lane rc=0 missing=[… deleted=2290 …]` | **1** | `evidence/13-r46counter-380.out` |
| 14 | same at its documented tip `4a2a4d55` | `selftest=1 fixture=1 lane=1 table=0 lane_events=5 lane_unrestored=0 lane_partial=2 met=False` — reproduces the row's pinned `table=0 … met=False` | 1 | `evidence/14-r46counter-4a2a4d55.out` |
| 15 | `heading-census.py --repo . --head 380bcdff` (KQ71's cell) | `headings=17 covered=15 uncovered=2`; the two uncovered are `SKILL.md:1434` and `SKILL.md:1444` (topic labels) — `corpus/knowledge/consumer-registry.md:30` is now **covered=yes** | 0 | `evidence/15-heading-census-380.out` |

| 16 | `append-only-audit.py --to 380bcdff --contract <v3 contract + one bound bogus row LOG.md/*>` (exit-map check for F12) | `unmatched-pattern LOG.md/*`, `summary … unmatched=1 …`, exit **0** | 0 | `evidence/16-unmatched-exit.out`, `evidence/16-contract-extra.tsv` |

Threshold-1 per-file breakdown at `380bcdff` (98 events): 28 `SCORECARD.md`, 20 `corpus/SOURCES.md`, 13 `LOG.md`,
8 `corpus/README.md`, 4 `corpus/knowledge/consumer-registry.md`, 2 `corpus/QUALITY.md`,
1 `registry/report-landing-errata.tsv`, 22 across 14 `corpus/lessons/*.md`.
At `3a09a1d9` with the v3 contract (96 events): 26 `SCORECARD.md`, 20 `corpus/SOURCES.md`, 13 `LOG.md`,
8 `corpus/README.md`, 4 `consumer-registry.md`, 2 `corpus/QUALITY.md`, 1 `report-landing-errata.tsv`,
22 across 14 lesson files. README `:823-826` prints 26/20/13/8 and "26 across 15 lesson files".

## 3. Findings index

| id | anchor | severity | proposed append |
|---|---|---|---|
| F1 | `corpus/QUALITY.md:397` (KQ70 check fails; `:203` stale) | high — a documented check is red at the build | `proposed-appends/QUALITY.append.md` |
| F2 | `corpus/QUALITY.md:398` (KQ71 count, region cell, counterexample, census) | high — the criterion cannot express a region-scoped row | same |
| F3 | `corpus/QUALITY.md:387` (KQ67 `restored_at_tip`, exit map) | medium | same |
| F4 | `SKILL.md:1450` (`four cells`) | high — format statement is wrong | `proposed-appends/SKILL.append.md` |
| F5 | `SKILL.md:1453` (`append-only-audit/v2` as current, `pass=19`) | high | same |
| F6 | `SKILL.md:1442` (v1-era tool row) | medium | same |
| F7 | `SKILL.md:1441` (round-46 counter leg) | medium — live command red, pinned measurement still true | same |
| F8 | `corpus/README.md:759-761` (five files) | medium (already disclosed in round 47) | `proposed-appends/README.append.md` |
| F9 | `corpus/README.md:776, 782-792, 803-806` (v2 schema/seven rows/85 files/command) | high | same |
| F10 | `corpus/README.md:807-826` (a/b/c/d) | high — three "not audited" claims are now false | same |
| F11 | `corpus/README.md:895-898` (edges) | medium | same |
| F12 | round-48 tool row in the **uncommitted** working-tree `SKILL.md` (`:1473` there): exit map "1 otherwise" | medium — false for `unmatched_patterns`/`binary_changes` (measured `unmatched=1`, exit 0) | correct before the integration commit; wording in `proposed-appends/SKILL.append.md` |

No correction is proposed for `corpus/knowledge/` (drift-free, §1) or for the `corpus/README.md:898` clause
"a lane file declared append-only but missing from the contract is not detected", which v3 leaves true
(`unmatched_patterns` reports the inverse case, a row matching no path).

## 4. Post-measurement integration state (read before applying the drafts)

After my build-tip measurement, four uncommitted changes appeared in the lane's working tree:
`corpus/README.md` `## Frontier disposition — round 48` (S9Readme + L1 addendum: schema v3, regions, 89/90 files,
98 events at threshold 1, edges), `corpus/QUALITY.md` KQ72–KQ75 (S9Quality; KQ72 carries the `region` cell),
`registry/append-only-contract.tsv` tenth row `corpus/knowledge/error-is-not-a-verdict.md` + lessons-row re-anchor to
`corpus/QUALITY.md:143` (K1Contract, K1Binding), and the `SKILL.md` round-48 registry section. Consequences for the
drafts: `README.append.md` is cut to a delta (supersession map + the `:790` exit-2 fact); the `QUALITY.append.md`
KQ71 scoping item points at KQ72; the "nine rows" statements are labelled as the build's file (the counter's
required set is nine entries, extra rows tolerated — `tools/round48-append-audit-v3-check.py:140-149`, `:709`); and
F12 targets the uncommitted row rather than appending to it. My measurements remain at `380bcdff` and none of them
changes.
