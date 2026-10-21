# RowC08-cr-only-report — scout verdict

**Holds** as a control row: on a hand-built CR-only report both arms exit 0 with
`defects: []`, and the frozen arm's pass is real (the section was parsed, not
skipped). Two qualifications, both outside the row's stated claim:

- the builder has **no premise gate** of its own (removing the CR transform still
  yields `met: true`), so the row's `met` only means something together with the
  source transform — which I did verify at byte level;
- the same report-bytes→text read path **still gets a sibling shape wrong in the
  current arm**: a UTF-8 BOM before a first-line `## Landed changes` heading makes
  both arms emit a false `landed-section-missing` + `landed-omitted` (exit 1),
  accusing the lane of omitting a commit the report cites.

Fixture built by hand in /tmp; the grid was never imported by the hand fixture
(the grid itself was run once as a cross-check, read-only).

## Setup

- Lane HEAD `245a37f69628c2c6bb29bbf17897d8fb5946c857`; clone at
  `/tmp/kama-r23w2/RowC08CrOnly-2` verified at that SHA.
- `git cat-file blob 4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`
  → sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`
  (frozen arm). Current `tools/report-landing-audit.py` → sha256
  `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`.
- git 2.56.0, python 3.14.8. Fixtures under `/tmp/c08-hand-dmujlfs2`, every git
  call with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` and explicit
  identity/date, no inherited `GIT_*`.
- Fixture = c_cr_only shape (`tests/report-audit/repo-state-grid.py:176-181`):
  lane one commit `kama-shokunin` "round-1: work" @1000; fleet commits
  `.ufo/reports/round-1/kama.md` @2000 whose `git show` bytes are

  ```
  b'# kama round 1\r\r## Landed changes\r\r- db796f8b820bf3825c58832419138cdba23206a7\r'
  ```

  (`\n` absent, 5 × `\r`; blob `06b0e5a855a3bfc994db601d5f13736dc5eda45b`).
- Command per arm:
  `python3 <auditor> --lane-repo lane --fleet-repo fleet --rounds 1 --no-errata --json`

## (1) Premise real and observed in the frozen arm — YES

| arm | rc | summary | result |
|---|---|---|---|
| frozen | 0 | `status: clean, defects: 0, required_commits: 1` | `required: 1, round_commits: 1, defects: []` |
| current | 0 | identical | identical |

The frozen pass is not a silent skip — probed three ways (each hand-built):

- CR-only report + a second lane commit @1500 → both arms rc=1,
  kinds `['landed-omitted']`.
- CR-only report + `## Notes` containing a fake 40-hex → both arms rc=1,
  kinds `['unresolved-full-hash']` (section boundary survives the transform).
- CR-only report + valid errata row → both arms rc=0, kinds `['landed-omitted']`
  (same shape C06 allows).
- Control: the no-Landed CR-only report gives
  `['landed-omitted','landed-section-missing']`, so the clean fixture's
  `defects: []` can only occur if `## Landed changes` and the citation were
  actually matched.

Mechanism confirmed in the frozen blob: line 90 `text=True` (PEP 278 universal
newlines translate lone CR) and line 266 reads the report via
`git show`, matching the builder docstring
(`tests/report-audit/repo-state-grid.py:177` "text-mode reads translated lone CR").
Current reproduces it explicitly at `tools/report-landing-audit.py:127`
`out.replace("\r\n", "\n").replace("\r", "\n")`, fed by `git show` at line 296.

Cross-check through the shipped grid (read-only):
`python3 tests/report-audit/repo-state-grid.py --case C08-cr-only-report --arm both --json`
→ rc 0; current `exit=0 kinds=[] met=True viol=0`; frozen `exit=0 kinds=[] met=True viol=0`;
no traceback.

## (2) Expected outcome is the CORRECT one — YES

- The report is Markdown. CommonMark 0.31.2 (§2.1, spec.txt lines 302-305):
  "A line ending is a line feed (`U+000A`), a carriage return (`U+000D`) not
  followed by a line feed, or a carriage return and a following line feed."
  A CR-only file is therefore an ordinary multi-line document: the heading line
  and the citation line exist, and the citation resolves to lane HEAD.
- The auditor's own declared model is universal newlines
  (`tools/report-landing-audit.py:109` docstring; implementation line 127;
  draft path `read_report` line 213 also text mode), and C01 (LF) / C07 (CRLF)
  already fix the same expectation. Exit 0 is thus internally consistent, not an
  accident of the current implementation.
- No defensible alternative reading makes exit 1 correct here: nothing is missing
  and nothing is ambiguous. Exit 2 ("irregular report") would also be wrong — the
  file is well-formed UTF-8 Markdown under the auditor's text model.

## (3) Near variant the same channel still gets wrong (current arm): UTF-8 BOM

Same read path (report bytes → text: `read_report` line 213 `encoding="utf-8"`,
`git()` decode line 123), sibling default at the boundary C08 does not pin.

- Fixture: report bytes `b'\xef\xbb\xbf## Landed changes\n\n- <lane HEAD>\n'`
  (also tested CR-only: `b'\xef\xbb\xbf## Landed changes\r\r- <lane HEAD>\r'`).
  Heading first, no title — a shape the auditor already accepts without a BOM
  (`## Landed changes\n\n- <sha>\n` alone → rc=0).
- Correct verdict: heading present, citation resolves → exit 0. A leading
  `EF BB BF` is a BOM, not content: WHATWG Encoding Standard §6, UTF-8 decode —
  "Let buffer be the result of peeking three bytes from ioQueue … If buffer is
  0xEF 0xBB 0xBF, then read three bytes"; Python `utf-8-sig` yields
  `'## Landed changes\n\n- …'` and `landed_match` matches.
- Observed, **both arms** (committed fleet path and `--report 1=PATH` draft path):
  rc=1, kinds `['landed-omitted', 'landed-section-missing']` — the auditor
  asserts the lane omitted a commit the report actually cites. Root cause:
  `landed_match` (`tools/report-landing-audit.py:169`) anchors `^## Landed
  changes` at string offset 0, and the decoded text begins `\ufeff##`.
- Scope: only when the BOM precedes the heading itself; a BOM before
  `# kama round 1` passes, because that `^## ` match is unanchored.
- Status: unclaimed. grep for `BOM|FEFF|utf-8-sig|byte order` over
  `tools/report-landing-audit.py`, `tests/report-audit/`, and
  `corpus/lessons/round-23.md` returns nothing; no grid row covers it. Both arms
  behave alike, so this is a residual, not a round-23 regression.
- Minimal direction (not implemented): decode the report BOM-tolerantly
  (`utf-8-sig`, or strip one leading `\ufeff`) in `read_report` and after the
  `git show` decode; one grid control with a BOM-owned heading would pin it.

### Variants tested with NO finding (both arms identical)

- mixed per-line separators CRLF/CR/LF; CR-only through the `--report` draft path.
- VT `\x0b`, FF `\x0c`, NEL `U+0085`, `U+2028` used as separators: both arms rc=1
  `['landed-omitted','landed-section-missing']`. **Do not "fix" these.** CommonMark's
  line endings are only LF/CR/CRLF; those code points are content, so the auditor's
  behaviour matches its declared text model.
- 30 randomized reports (per-line separator drawn from LF/CRLF/CR, 20 % BOM
  prefix): 0 arm differences.

## Grid-side observation: C08 has no premise gate

`c_cr_only` (`tests/report-audit/repo-state-grid.py:176-181`) contains no
`require(...)`, unlike e.g. `f_replace_report` (line 267 `require(x in
g(fleet,"show",...) , "report replace not effective")`). The module docstring
(lines 4-6) promises that a fixture whose premise never materialized makes the
grid exit 2, not pass. Demonstrated: a copy of the grid in
`/tmp/c08-hand-dmujlfs2/grid-c08-noop.py` with C08's
`.replace(b"\n", b"\r")` removed (fixture then byte-identical to C01-clean)
still reports `C08-cr-only-report exit=0 kinds=[] met=True`. So the row's `met`
is not self-validating; my byte-level check is what makes the pass meaningful.
C07 has the same gap. A `require(b"\n" not in <blob>)` in both builders would
close it.

## Not verified

- Any other grid row or the L1 totals (26/26 faults, 8/8 controls, 24 mutants /
  22 killed, survivors M02/M20) — only C08, plus C07/C01 smoke, were executed.
- Other report-text residuals I noticed but did not pursue: 1-3-space-indented
  ATX heading (`  ## Landed changes`) is also missed by the `^## ` anchor, and a
  BOM before `## Registry` would defeat `census_source_urls` the same way.
- No fix implemented; no tracked lane file touched; no commits.

## Files written

- `.ufo/waves/round-23/falsify/advice/RowC08CrOnly.md` (this report)
- `/tmp/kama-r23w2/RowC08CrOnly-2/` (clone at 245a37f6),
  `/tmp/kama-r23w2/frozen-audit.py`, `/tmp/kama-r23w2/grid-c08.json`,
  `/tmp/kama-r23w2/commonmark-spec.txt`, `/tmp/kama-r23w2/encoding.html`
- `/tmp/c08-hand-dmujlfs2/…` hand-built fixtures and `grid-c08-noop.py`

No tool installs or upgrades were needed.
