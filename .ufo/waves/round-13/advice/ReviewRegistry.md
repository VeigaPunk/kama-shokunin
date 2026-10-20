# ReviewRegistry — round 13 review of S033 and immutable old cells

Reviewer: KamaR13.ReviewRegistry (leaf, read-only except this report).
State reviewed: `corpus/SOURCES.md` HEAD `941bb32` plus working-tree S033 insertion
(first observed 2026-10-20 ~01:55 UTC, when `corpus/lessons/round-13.md` landed).
If the row or lesson changes again, this review is stale and must be re-read.

## Verdict

S033 is accurate against the primary source: exact quotes, correct revision, valid
tier for cat-file output semantics, `used-by` path exists. Old rows S001–S032 are
unchanged against HEAD. One contract-compliance gap (F1) and four wording or record
items (F2–F5) should be fixed before closure. No blocking defect.

## Findings (by severity)

**F1 — Medium-low: lesson Gate does not carry the quote that grounds half of `teaches`.**
Contract `SOURCES-CONTRACT-v1` rule 1 requires the round lesson's `## Gate` to record,
for each new row, a ≤25-word quote with location grounding `teaches`. S033 `teaches`
has two clauses. The lesson's Gate/Source-access section (`corpus/lessons/round-13.md`
lines 36–44) quotes only OUTPUT. The `--textconv`/`--filters` transform clause is
grounded only in `SOURCES.md` line 74 and `advice/Sources.md`.
Fix: add the two OPTIONS quotes to the lesson with location (OPTIONS `--textconv`,
OPTIONS `--filters`), each ≤25 words (6 and 11 words; see Verified).
Owner: lesson writer; outside this seat's write set.

**F2 — Low: method wording overreaches the source.**
- S033 `scope` reads "Direct object-content comparison for kama evidence". The manual
  never mentions comparison. Its text is about output semantics for an explicit `<type>`.
- S033 `teaches`: "…so exact byte comparison must avoid both." This is kama's inference
  from the two OPTIONS entries. It is not tagged `[INFERENCE]`. The lesson's
  "method support only" caveat partly mitigates this.
Suggested: scope "explicit-type raw output semantics of cat-file, not endpoint truth";
teaches "…; a byte comparison that avoids both is [INFERENCE] from these options."
S033 was created this round, so amending it before closure is, in this seat's reading,
not a rule-2 violation. That reading is an assumption; the owner should confirm it.

**F3 — Low: record drift between `advice/Sources.md` and the landed row.**
`advice/Sources.md` "S033 row as landed" gives scope "direct object-content comparison
mechanics…" and teaches "byte comparison must avoid both; the page documents mechanics
only…". The actual row reads "Direct object-content comparison for kama evidence:
explicit-type raw output, not endpoint truth" and "exact byte comparison must avoid both.
Page semantics alone do not prove an independent comparison ran." Re-sync the advice file
to the row after F2 is settled.

**F4 — Low: row change not logged in the lesson.**
Round 12 logged the new row in its lesson ("Row changes: S032 absent → mined",
`corpus/lessons/round-12.md:114`). Round-13 lesson does not contain an "S033 absent →
mined" line; it defers to `advice/Sources.md`. Add the same line to the lesson.

**F5 — Low: immutable S032 cells carry untagged inference; correction not appended.**
- S032 `anchor` names only "DESCRIPTION, plain blobs". The scope "Byte-preserving…"
  rests on the git-show DISCUSSION sentence "The contents of the blob objects are
  uninterpreted sequences of bytes" (verified below). That section is not named in the
  anchor cell.
- S032 `teaches` "…allowing exact historical source bytes to be compared independently of
  a snapshot manifest": the manual says nothing about snapshot manifests or independent
  comparison. This is kama's inference, not tagged.
Because the cell is immutable, the fix is an appended dated correction paragraph in
`SOURCES.md` (the round-12 pattern), not an in-place edit. None exists yet.

**F6 — Info: line-number shift of later registry lines.**
S033 is inserted at line 45, so Paths, Search log, Leads and appended prose move +1
(prior: `@@ -44,0 +45 @@`). Round 12 accepted the same shift for S032 (its lesson,
`round-12.md` §Gate, argued it is not an append-only violation because no row cell or
established anchor changed). Grep found no corpus-internal `SOURCES.md:N` reference with
N ≥ 45. The round-12 advice files (e.g. `round-12/advice/CorrectionsConnection.md`) cite
prose at lines 63–65 and 64–66; those historical advice citations now point one line off.
Non-corpus, noted only.

## Verified (evidence)

Immutable old cells (read-only commands; no census, validate or gate run):
- `git diff --numstat HEAD -- corpus/SOURCES.md` → 4 insertions, 0 deletions. Hunks:
  `@@ -44,0 +45 @@` (S033 row), `@@ -59,0 +61 @@` (search-log entry),
  `@@ -70,0 +73,2 @@` (correction paragraph).
- Per-row awk comparison, HEAD (941bb32) vs working tree, keyed on column 2 ID:
  output `S033: NEW row` only. Zero rows CHANGED for S001–S032.
- Against the round-10 baseline `1e41928`, the only in-place cell changes are the
  logged ones: S011, S012, S016 `status` queued→mined; `used-by` additions on S001, S010,
  S011, S012, S016. These are logged in `corpus/lessons/round-11.md` lines 55–62 (old→new
  table). S031 and S032 are new rows. Rule 2 is satisfied for these.
- Static used-by existence (`test -e` on every mined row's `used-by` path, 23 mined rows
  after S033): all present, including `corpus/lessons/round-13.md` (now exists, 87 lines).
  Census E11 would pass on this point.
- Pipe-field parse of the S033 row returns `used-by` at field 12 as a single path, so the
  row has the 11-cell shape the contract requires (no stray `|`).

S033 quotes against the primary source (manual fetched 2026-10-20):
- OUTPUT, git-cat-file 2.56.0: "If *<type>* is specified, the raw (though uncompressed)
  contents of the *<object>* will be returned." Matches the row and lesson exactly
  (markdown asterisks removed). 15 words. Location: artifact 4432 (fetch of
  `https://git-scm.com/docs/git-cat-file`), OUTPUT section.
- OPTIONS `--textconv`: "Show the content as transformed by a textconv filter." Quoted
  fragment "as transformed by a textconv filter" = 6 words. Fetch log line 287.
- OPTIONS `--filters`: "Show the content as converted by the filters configured in the
  current working tree…" Quoted fragment "as converted by the filters configured in the
  current working tree" = 11 words. Fetch log line 292.
- OPTIONS `<type>`: "asking for a type that can trivially be dereferenced… is also permitted."
  Matches the row's statement that this clause is not raw-output support.
- Revision: page header "git-cat-file last updated in 2.56.0", "2.56.0 … *2026-09-28*".
  Matches the anchor.
- Cross-check page `https://git-scm.com/docs/git-cat-file/2.55.0`: same OUTPUT sentence at
  fetch log `4655.read.log:493`. The page is labelled "last updated in 2.56.0" and the
  version selector shows 2.55.0; that establishes doc-text identity, nothing about binary
  behaviour.
- Host binary: `git --version` → `git version 2.55.0`, `/usr/bin/git`.
- `opened` 2026-10-20 matches the fetch session date.

S032 (immutable, re-checked):
- DESCRIPTION "For plain blobs, it shows the plain contents." (8 words) present on the
  git-show page; revision header 2.56.0 / 2026-09-28 matches the anchor.
- DISCUSSION "The contents of the blob objects are uninterpreted sequences of bytes.
  There is no encoding translation at the core level." (20 words) present; fetch log
  `4389.read.log` lines 2197–2198.

## Limits

- Static reading only. No `sources-census.sh`, validator, gate, build or test was run by
  this seat; the `test -e` loop is an existence check, not a census.
- `git --version` was the only tool-state query. Git's behaviour on this host was not
  exercised; no `cat-file` was executed on repository objects.
- Verified that the manual text exists and matches. Did not verify any repository
  comparison, receipt or round-12 measurement; those belong to other seats.
- Did not review `corpus/QUALITY.md` KQ16, `SCORECARD.md`, `LOG.md` (all modified in the
  working tree) — outside this assignment.
- Access timestamps are taken from the session log names; no independent clock check.

## Tools

Installed or updated: **none**. Required tools were already present (`git` 2.55.0).
