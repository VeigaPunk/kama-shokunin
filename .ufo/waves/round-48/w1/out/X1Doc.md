# X1Doc — v3 contract-format documentation drift: eleven drifts in committed docs, one in the uncommitted round-48 row, three false "not audited" claims, and a documented check that is red at the build

**Verdict.** Documentation drift is real and reproducible: at the build commit
`380bcdff9c8af06997c482f6eb03db926a794a2b` **three of the four graded surfaces** describe the instrument as it
was before the build, and **three of the cited commands change their output under v3** — one of them (KQ70's check)
fails outright, one (KQ71's check) returns a different count and exit, and one (the README's `--to 3a09a1d9` command)
no longer runs. Eleven line-anchored drifts in committed text (F1–F11) plus one in the still-uncommitted round-48 row (F12), three appended-correction drafts, one surface
(`corpus/knowledge/`) with zero drift and therefore no draft. Nothing was edited in the lane; no counter, contract
or control was touched.

## Measured point and method

- Clone: my own `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin`, checked out at
  `380bcdff9c8af06997c482f6eb03db926a794a2b` (`git rev-parse HEAD` in the clone = that commit). All lane tools were
  run from that working tree, so the tool is the v3 tool and a contract passed by path is the v3 file.
- Instrument at the build: `tools/append-only-audit.py` sha256
  `ec9c6d206fccfd9b9b04526b54da34207c48ab9f0768c3285128cd59fcf60f72`; `registry/append-only-contract.tsv` sha256
  `ca0618e50fadc4b0d53b0d8a61868b0ea7fbf33b3429c125a0d5643022a77075`, header
  `path<TAB>rule<TAB>declared_at<TAB>region<TAB>note`, **nine** rows; selftest `AOA_SELFTEST pass=27 fail=0`
  (`evidence/00-context.txt`, `evidence/11-selftest.out`).
- Population: `SKILL.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/knowledge/*.md` (36 files) at that commit.
  Census: `git show 380bcdff:<file> | grep -n` over `append-only-audit|append-only-contract|append-only/v|restored_at_tip|four cells|seven rows|five files|85 files`, then every hit read in full. Full census and per-line verdicts:
  `drift-table.md` §1.
- Cited commands, all fifteen, run and recorded (`drift-table.md` §2): `evidence/01`–`evidence/15`. The only run of
  the frozen round-48 counter is `evidence/12` (it is the closure counter, not my claim); no network leg was run
  (this item is C1-only).

## Findings

### F1 — `corpus/QUALITY.md:397` (KQ70): the criterion's cited check exits 1 at the build

The row says "Check: `python3 tools/round47-append-audit-v2-check.py --repo <clone> --tip <tip> --scratch <dir>`
reports `lane=1 fixture=1 stable=1`". The round-47 counter reads the contract **at `--tip`** with a four-cell header
and the v2 JSON, so at the v3 build it refuses both the contract and its own four-cell fixture:

```
$ python3 tools/round47-append-audit-v2-check.py --repo . --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch <dir>
selftest=1 contract=0 lane=0 fixture=0 stable=0 files=0 lane_events=0 lane_mismatch=-1 fixture_mismatch=-1 met=False
detail: contract: header line is not exactly path<TAB>rule<TAB>declared_at<TAB>note
detail: fixture: tool exit=2, stdout is not one JSON object
exit=1
```
(`evidence/05-v2counter-380.out`.) The same command at its own build tip reads `… met=True`, exit 0
(`evidence/06-v2counter-3a09.out`), so this is v3-induced and not environmental. The same row also cites
`tools/append-only-audit.py:203` for the hunk-count refusal; at the build that raise is at **`:400`** and `:203` is a
`git show` subprocess call. Proposed fix: the appended block in
`proposed-appends/QUALITY.append.md` (names `round48-append-audit-v3-check.py`, `selftest=1 contract=1 lane=1
fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`, exit 0,
and `:400`).

### F2 — `corpus/QUALITY.md:398` (KQ71): count, region cell, counterexample and census all superseded

- Count: the cited check now prints `files` = **89** at `380bcdff` (exit 0) and **87** at the cited `3a09a1d9`
  (exit 1, `regressed=1`), not "85 paths" (`evidence/07-kq71-380.json`, `evidence/08-kq71-3a09.json`).
- Exit: "exits 1 while any event is partial" understates it — at `3a09a1d9` `partial=0 unrestored=0` and the exit is
  1 on `regressed=1` (`evidence/08`).
- Shape: the criterion still describes a four-part row ("pattern matches … `declared_at` holds … text that declares
  the rule") and cannot express the `region` cell that now scopes a claim (`*`, `exempt=…@…`, `only=…@…`).
- Counterexample: the row's own cell says `corpus/knowledge/consumer-registry.md:30` "declares its section
  append-only and has no row" — row 9 now covers it and the tool reports `ok: true`
  (`evidence/02-audit380.json`, `declarations[8]`).
- Census: the cited heading census reads `headings=17 covered=15 uncovered=2` at the build (both uncovered are the
  `SKILL.md:1434`/`:1444` topic labels the row already dispositions), not `13/11/2`
  (`evidence/15-heading-census-380.out`).

Proposed fix: `proposed-appends/QUALITY.append.md`, KQ71 item.

### F3 — `corpus/QUALITY.md:387` (KQ67): the required report fields no longer exist

KQ67 requires a report to name each event's "`deleted`/`restored_at_tip` pair". v3 has no `restored_at_tip`: event
keys are `commit, deleted, file, graded, held_at_to, restored_best, restored_by, restored_max, status, ungraded`
(`evidence/02-audit380.json`), and the text line reads `event <c12> <file> deleted=N graded=G ungraded=U
restored_max=K held_at_to=H status=S …` (`evidence/01-audit380-text.out`). Its "exit 1 when any event is partial or
unrestored" is also incomplete (regressed / vanished / unbound declaration,
`tools/append-only-audit.py:469-474`), and its worked pair now reads `2421/2349` (graded) and `31/14`, both
`restored` (a `partial` in v2 becomes a `restored` with `ungraded` head lines). Proposed fix:
`proposed-appends/QUALITY.append.md`, KQ67 item.

### F4 — `SKILL.md:1450`: "four cells per row"

The round-47 C1 registry row states the contract leg as "exact header, **four cells per row**". The header is
`path<TAB>rule<TAB>declared_at<TAB>region<TAB>note` — five cells, nine rows — and the row's own command now reads
`contract=0 … met=False`, exit 1 (`evidence/05`). Proposed fix: `proposed-appends/SKILL.append.md` (row 1450 bullet).

### F5 — `SKILL.md:1453`: cites `append-only-audit/v2` as the current schema

The row prints `{"schema": "append-only-audit/v2", "to", "threshold", "contract", "files", "commits", "events",
"summary"}`. The build prints `append-only-audit/v3` with `declarations`, `vanished`, `unmatched_patterns`,
`binary_changes` beside those keys (`evidence/02`), `files` is the expanded list (89 at the build), the text line
carries `graded`/`ungraded`/`held_at_to`, and the selftest is `pass=27 fail=0`, not `pass=19`
(`evidence/11-selftest.out`). Proposed fix: `proposed-appends/SKILL.append.md` (row 1453 bullet).

### F6 — `SKILL.md:1442`: v1-era tool row, still the only tool row a reader finds first

It documents `restored_at_tip=`, a summary without `files`/`regressed`/`vanished`, `--files` as the only file-set
flag, and "1 at least one event partial or unrestored". All four are superseded by v3 (`evidence/01`, `02`).
Proposed fix: `proposed-appends/SKILL.append.md` (row 1442 bullet).

### F7 — `SKILL.md:1441`: the round-46 counter is red at any v3 tip

Its legs read the graded tool at `--tip`, so `--tip 380bcdff` prints `selftest=1 fixture=0 lane=0 table=1
lane_events=5 lane_unrestored=0 lane_partial=2 met=False`, exit 1 (`detail: fixture full ok=False rc=2`,
`detail: lane rc=0 missing=[… deleted=2290 …]`) — `evidence/13-r46counter-380.out`. Its **pinned** measurement is
still exact: `--tip 4a2a4d55` reproduces the row's `selftest=1 fixture=1 lane=1 table=0 … met=False`
(`evidence/14-r46counter-4a2a4d55.out`), so this is a live-command staleness, not a false record. Proposed fix:
`proposed-appends/SKILL.append.md` (row 1441 bullet).

### F8 — `corpus/README.md:759-761`: "the five files the lane treats as append-only"

The contract declares nine rows / 89 paths at the build. This sentence was already stale in round 47 (seven rows)
and the round-47 lesson (`corpus/lessons/round-47.md:39`) records the disposition, so it is a known item; under v3 it
is stale a second way (and the tool no longer hard-codes any set). Proposed fix:
`proposed-appends/README.append.md`, first paragraph.

### F9 — `corpus/README.md:776, 782-792, 803-806`: v2 schema, seven rows, 85 files, and a command that now exits 2

`python3 tools/append-only-audit.py --repo <clone> --to 3a09a1d9` (README `:790`) is **broken at the build**:

```
could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>region<TAB>note
exit=2
```
(`evidence/03-audit-3a09-defaultcontract.out`) — the default contract is read from `<to>`, which still holds the
four-cell file. With the v3 contract the same tip reads `commits=303 files=87 events=5 restored=5 partial=0
unrestored=0 ungraded=0 ungraded_lines=89 regressed=1`, exit 1 (`evidence/04-audit-3a09-v3contract.out`); at the
build the tool reads `commits=311 files=89 … regressed=0`, exit 0 (`evidence/01`). Proposed fix:
`proposed-appends/README.append.md`, "round-47 figures" and "command at `:790-792`" paragraphs.

### F10 — `corpus/README.md:807-826`: three "not audited" claims are now false, one is narrowed

- `:807-810` "never reads its `rule`, `declared_at` or `note` cell (`tools/append-only-audit.py:184`)": v3 **reads**
  `declared_at` (binding, negation rejected) and `region`; `rule` is validated but not applied; `:184` is now inside
  `row_token()` and not the expansion site.
- `:811-814` "(1) The `SCORECARD.md` carve-out is declared but not applied … the exit 1 is a signal to read the
  contract row, not a verdict": the carve-out **is** applied — `0718b6ab SCORECARD.md deleted=2421 graded=2349
  ungraded=72 status=restored`, `dd9f5dc6 … deleted=31 graded=14 ungraded=17 status=restored`, build exit 0
  (`evidence/01`).
- `:815-821` "(2) … no contract row covers `corpus/knowledge/*.md`": row 9 covers the `## Errata` region
  (`only=## Errata@…:30`, binding `ok: true`); `context-capacity.md:245` remains uncovered by design (its heading
  carries no such word).
- `:821-826` "(3) … 91 events — 12 restored, 8 partial, 71 unrestored — 26 SCORECARD, 20 SOURCES, 13 LOG, 8 README,
  26 across 15 lesson files": at the same tip with the v3 contract it is **96** events — `restored=12 partial=4
  unrestored=63 ungraded=17 ungraded_lines=177`, exit 1; 26/20/13/8, plus 4 `consumer-registry.md`, 2
  `QUALITY.md`, 1 `report-landing-errata.tsv`, and 22 across 14 lesson files (`evidence/10a-th1-3a09.out`). At the
  build: **98** events, `14/4/62`, `ungraded=18`, 28 SCORECARD and the same rest (`evidence/09a-th1-380.out`).

Proposed fix: `proposed-appends/README.append.md`, "What is still not audited" paragraph.

### F11 — `corpus/README.md:895-898`: two of the four listed edges are closed

"region scoping for the two knowledge `## Errata` blocks" and "the `SCORECARD.md` head carve-out that the tool cannot
apply" are both applied by v3; the "91 events at 1" figure is superseded above; **the last clause stands** — "a lane
file declared append-only but missing from the contract is not detected" (v3's `unmatched_patterns` reports the
inverse case, a row matching no path). Proposed fix: `proposed-appends/README.append.md`, last paragraph.

### No drift: `corpus/knowledge/`

All 36 files censused; **zero** lines cite the tool, the contract, the schema or a cell count. The three
`append-only` mentions are correct at the build — `consumer-registry.md:30` is row 9's `declared_at`,
`context-capacity.md:245` makes no claim, `served-identity-crosswalk.md:94` is a `corpus/SOURCES.md` `A-row` claim
guarded by `tools/sources-append-only.py`. No append is drafted for it
(`proposed-appends/knowledge-nochange.md`). The KQ71 counterexample that named `consumer-registry.md:30` lives in
`corpus/QUALITY.md:398` and is superseded there.

### F12 — the in-flight round-48 tool row states an exit map the tool does not implement (uncommitted)

The round-48 registry section the L1 has written into the lane's working tree (`SKILL.md:1473` there, absent at
`380bcdff`) gives the tool exit map as "0 no event partial or unrestored, none regressed, no vanished declared path,
every declaration bound; **1 otherwise**". `exit_code()` (`tools/append-only-audit.py:469-474`) tests only `partial`,
`unrestored`, `regressed`, `vanished` and `bad_declarations`; `unmatched_patterns` and `binary_changes` are reported
and leave the exit at 0. Measured on a copy of the build's contract with one added, bound row (`LOG.md/*` at
`README.md:16`):

```
unmatched-pattern LOG.md/*
summary commits=311 files=89 events=5 restored=5 partial=0 unrestored=0 ungraded=0 ungraded_lines=89 regressed=0 vanished=0 unmatched=1 binary=0 bad_declarations=0
exit=0
```
(`evidence/16-unmatched-exit.out`, contract `evidence/16-contract-extra.tsv`.) The tool's own docstring has the same
defect (`tools/append-only-audit.py:95-96`, "1 otherwise"). Proposed fix: say "1 on a partial or unrestored event, a
regressed event, a vanished declared path or an unbound declaration" — the wording in
`proposed-appends/SKILL.append.md`, last bullet. This is the one drift item whose anchor is uncommitted text, so it can
still be corrected before the integration commit rather than appended to.

## Overlap with corrections that landed after my measurement (coordination, not a finding)

Between my build-tip measurement and this report, sibling seats wrote four uncommitted changes into the lane's
working tree that touch this item's subject. I measured at `380bcdff` as instructed; none of my figures changed, but
three of my drafts lose part of their surface to landed text, so the L1 should read them as deltas:

- `corpus/README.md` gained `## Frontier disposition — round 48` (seat S9Readme) with an "Integration addendum
  (round-48 L1)". It already states schema v3, the region semantics, 89 files at the build / 90 after integration,
  `regressed`, the 98-event threshold-one reading and the edges list — i.e. it supersedes the round-47 block in the
  lane's accepted way (append, not rewrite). **My `README.append.md` is therefore cut to a delta**: a supersession map
  naming the stale lines (`:759-761`, `:776`, `:782-792`, `:803-810`, `:811-821`, `:821-826`, `:895-898`) so a future
  reader does not cite them, plus the one fact the landed block does not state — that the `:790` command exits 2.
- `corpus/QUALITY.md` gained KQ72–KQ75 (seat S9Quality). KQ72 already carries the `region` cell and the binding rule,
  so **my KQ71 draft's scoping item is now a pointer to KQ72**; what remains mine there is the count (89/87 vs 85),
  the exit-on-`regressed`, the retired counterexample and the census figure.
- `registry/append-only-contract.tsv` gained a tenth row (`corpus/knowledge/error-is-not-a-verdict.md`,
  `only=## Round24`, seat K1Contract) and re-anchored the lessons row to `corpus/QUALITY.md:143` (seat K1Binding).
  The C1 counter's required-row set is nine entries (`tools/round48-append-audit-v3-check.py:140-149`) and extra rows
  are tolerated (it checks `len(decl) == len(rows)`), so integration does not break it; my drafts now say so
  explicitly so their "nine rows" statements are not read as a claim about the integrated file.
- `SKILL.md` gained the round-48 registry section — which is what F12 addresses before it is committed.

Nothing in the overlap changes F1–F11: every one of those lines is still present and still stale at the build, and
`corpus/QUALITY.md:397` (KQ70's check) is still red after the landed criteria, because KQ72's check uses the v3 tool
and does not touch KQ70's v2-counter citation.

## Adjacent observation (not acted on, not in my population)

`tools/append-only-audit.py:95-96` states the exit contract as "0 no event partial or unrestored, no regressed
event, no vanished path and every declaration bound; **1 otherwise**", while `exit_code()`
(`tools/append-only-audit.py:469-474`) tests only `partial`, `unrestored`, `regressed`, `vanished`,
`bad_declarations` — `unmatched_patterns` and `binary_changes` do **not** change the exit. This is now promoted to
F12 with a measured counterexample; the tool itself is frozen (I did not touch it) and the fix belongs in the doc
line, not the code.

## Already-known integration items (not re-reported)

Gate-registry-check lists the two round-48 counters unregistered; the round-41/42/43 counters read the spot-check
count 33 vs 34; hexrun-census has one unknown (`d0012618`). I added nothing to those and did not run
`gate-registry-check`.

## Risks / blockers

- **None blocking.** Every cited command ran; the drafts are complete text, not sketches.
- The drafts are **appends**, as the item requires. `SKILL.md` holds no contract row, so an in-place rewrite of rows
  1441/1442/1450/1453 is also permitted by v3's contract — but that would delete recorded round-46/47 measurements
  from a file the KQ71 census then has to re-derive; the appended form is the one I propose and the one that keeps
  the record honest.
- F4/F5 change the registry rows a reader finds by `grep append-only-audit`; if the L1 lands the round-48 registry
  row (`SKILL.md:1471` on the lane's working tree, not present at `380bcdff`) the append must land **after** it so
  the superseding note reads forward.
- Appending to `corpus/QUALITY.md` and `corpus/README.md` grows two contract-declared files; both are `A-corr`
  region `*`, so no delete is introduced and the v3 audit stays green in shape (I did not append, so I cannot
  measure the post-append `regressed` value — that is the L1's post-integration run).
- No tool was installed or upgraded for this seat (nothing needed). Scratch `/fast/scratch/hyaku/kama-r48/X1Doc`
  removed after the evidence copy.
- I did not judge, grade a claim, or touch a counter, preregistration or control. `corpus/QUALITY.md`,
  `corpus/README.md`, `SKILL.md` and `corpus/knowledge/` were only read (via `git show` on the shared clone).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Doc.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Doc/drift-table.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Doc/proposed-appends/SKILL.append.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Doc/proposed-appends/QUALITY.append.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Doc/proposed-appends/README.append.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Doc/proposed-appends/knowledge-nochange.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/X1Doc/evidence/` (18 files: `00-context.txt`,
  `01`–`15` — including the two v3 JSON documents and the two threshold-one runs — plus `16-unmatched-exit.out` and
  `16-contract-extra.tsv`)
