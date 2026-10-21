# Row C04-landed-section-missing — falsification report

Seat: `CloseKama22.RowC04LandedSection-2` (leaf). Clone:
`/tmp/kama-r23w2/CloseKama22.RowC04LandedSection-2`, `git rev-parse HEAD` =
`245a37f69628c2c6bb29bbf17897d8fb5946c857`. No lane tracked file, index or
`.jj` was written; no commit/push/jj; no installs; no REA.

Axes: A1 premise reality, A2 expectation correctness against the contract,
A3 same-channel variant soundness, A4 live-population impact. Only moves that
added directly observed evidence on A1–A4 were kept.

## Verdict

- **HOLDS** for the scored claim (grid row C04, kind `control`): the premise is
  real, the frozen arm produces the claimed ordinary verdict, and the expected
  verdict is the contract-correct one — not merely what the code does.
- **Same-channel defect found, unclaimed and latent:** text that is not a
  rendered section (fenced code block, HTML comment) satisfies `landed_match`,
  and a fenced/comment `## ` line truncates a real Landed section. Both arms
  behave identically; no committed fleet report triggers it today.
- This is **not** a falsification of C1 axis 7: the defect is report text, not
  repository-local git state. It is also **not** a round-23 regression — the
  `landed_match` function and the 15-line section/omission block are
  byte-identical in the frozen blob and the committed auditor.

## Q1 — premise real, and observed in the frozen arm?

Yes. Builder `tests/report-audit/repo-state-grid.py:146-150` creates a lane
commit author `kama-shokunin`, author time 1000, subject `round-1: work`, and a
fleet report whose committed bytes are exactly `# kama round 1\n\nno section\n`.
The row at `tests/report-audit/repo-state-grid.py:532-533` expects exit 1 and
kinds exactly `["landed-omitted", "landed-section-missing"]`; grading is at
`:600-635` (exact sorted kind set at `:627-630`). C04 is a control row, so the
claim is that both arms keep this ordinary verdict, not that either arm changes.

Independently rebuilt by hand in `/tmp` (no import of the grid;
`.ufo/waves/round-23/falsify/out/CloseKama22.RowC04LandedSection-2/repro.py`):

```
$ python3 repro.py --clone /tmp/kama-r23w2/CloseKama22.RowC04LandedSection-2
## C04-hand-no-section  lane=db796f8b820b  heading_in_report=False
  frozen : exit=1 kinds=['landed-omitted', 'landed-section-missing']
           defects=[('landed-section-missing','-',None),
                    ('landed-omitted','db796f8b820b',False)]
  current: exit=1 kinds=['landed-omitted', 'landed-section-missing']
           defects=[('landed-section-missing','-',None),
                    ('landed-omitted','db796f8b820b',False)]
```

Round state observed in both runs: `round_commits=1`, `required=1`, cutoff 2000
(the fleet report's author time), required commit `db796f8b…`, stderr empty,
no traceback, no timeout. The report blob really has no `## Landed changes`
line (`heading_in_report=False`), so the premise is established from committed
bytes, not just by construction.

Cross-check of the actual row (fresh temp fixture, not my hand fixture):

```
$ python3 tests/report-audit/repo-state-grid.py \
    --case C04-landed-section-missing --arm both --json
exit=0
# each arm: "met": true, "kinds": ["landed-omitted","landed-section-missing"],
#           "traceback": false, "executed": false, "timed_out": false
```

Auditor blobs used: frozen `4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/
report-landing-audit.py`, sha256 `09ecd63b…b3b3f`; current working file equals
`HEAD:tools/report-landing-audit.py`, sha256 `f228f174…6928a7`.

Note: `c_no_landed` has no `require()` premise guard (unlike e.g.
`c_shared_clone`), so the row's premise is only established by construction;
I re-derived it above.

## Q2 — is the expected outcome the correct one?

Yes. The kind pair is entailed by the auditor's own finite definitions, and it
matches the external contract:

- `tools/report-landing-audit.py:26`: "landed-section-missing  the report has
  no `## Landed changes` section".
- `tools/report-landing-audit.py:20-24`: `landed-omitted` is a lane commit by
  `<lane>-shokunin` with a `round-N:`/`checkpoint(rN)` subject, authored no
  later than the report's first fleet commit, "not cited in `## Landed
  changes`". With no section, nothing is cited, so every required commit is
  omitted.
- The implementation follows that definition literally: `:320-322` appends
  `landed-section-missing` and sets `section = ""`; `:323` extracts no
  citations; `:332-334` appends one `landed-omitted` per pre-cutoff commit.
- `corpus/QUALITY.md:151` (KQ28): "A round report's `## Landed changes` names
  every lane commit of the round ... by hash"; `.ufo/prompts/kama-round-23.md:107`
  lists "Landed changes" as a required section.
- The build wave's own controls note,
  `.ufo/waves/round-23/build/advice/RevControls.md:56` (K15), declares
  "`landed-section-missing` + 5× `landed-omitted` (grid C04 covers)" for a
  missing heading.
- Exit 1 is the docstring's "failed" code (`tools/report-landing-audit.py:42`),
  not a could-not-evaluate.

Both blobs carry `landed-section-missing` in `KINDS`
(`tools/report-landing-audit.py:78-79`), and the 15-line section/omission block
(`section = None …` through `cited_anywhere = …`) compares byte-identical
between the frozen blob and the committed file. The frozen arm emits exactly
this pair too, so the control is descriptive of both arms *and* independently
required by the definitions.

Why both kinds rather than only `landed-section-missing`: the kinds are
separate contract violations, and only `landed-omitted` is errata-resolvable
(`RESOLVABLE`, `tools/report-landing-audit.py:80-81`, excludes
`landed-section-missing`), so suppressing the omission would make the missing
commit identity uncorrectable and would hide which commits are missing. The
double report is redundant but correct.

## Q3 — near variant of the same channel that current still gets wrong?

Yes, in both directions. All fixtures below are hand-built the same way (one
lane commit `db796f8b…`, one fleet report committed at author time 2000,
`--rounds 1 --no-errata`). Frozen and current outputs were identical for every
row (full transcript:
`.ufo/waves/round-23/falsify/out/CloseKama22.RowC04LandedSection-2/results.txt`).

| fixture (report body after `# kama round 1`) | frozen | current | judgment |
|---|---|---|---|
| `V1-fenced-template-with-citation`: no real section; a fenced block contains `## Landed changes` and `- <sha> work` | exit 0, no defects | exit 0, no defects | **false clean**: no rendered Landed section exists, yet the report passes |
| `V4-html-comment-with-citation`: heading + citation inside `<!-- … -->` | exit 0, no defects | exit 0, no defects | **false clean** |
| `V9-unterminated-fence-example`: open ``` then heading + citation | exit 0, no defects | exit 0, no defects | **false clean** |
| `V5-fenced-heading-no-citation`: exactly the C04 fixture plus a fenced `## Landed changes` line | exit 1, kinds `['landed-omitted']` | same | `landed-section-missing` **disappears**; the C04 expectation is no longer met by a fixture whose rendered form still has no section |
| `V2-fenced-h2-inside-section`: real section, fenced `## notes`, citation after the fence | exit 1, `landed-omitted`, `cited_elsewhere=True` | same | **false defect**: the commit is cited in the rendered section |
| `V11-comment-h2-inside-section`: real section, `<!--\n## notes\n-->`, citation after | exit 1, `landed-omitted`, `cited_elsewhere=True` | same | **false defect** |
| `V10-fenced-template-before-real-section`: fenced template quote of the heading, then the real section citing the commit | exit 1, `landed-omitted`, `cited_elsewhere=True` | same | **false defect on a compliant report** (arguable overlap with the declared "only the first section is read" open item) |
| `V3-indented-heading`: `  ## Landed changes` + citation | exit 1, missing + omitted | same | false defect: valid H2, citation ignored |
| `V6-two-spaces-after-hashes`: `##  Landed changes` + citation | exit 1, missing + omitted | same | same |
| `V8-tab-after-hashes`: `##\tLanded changes` + citation | exit 1, missing + omitted | same | same |
| `V7-setext-h2`: `Landed changes` + `--------------` + citation | exit 1, missing + omitted | same | same |

Root cause is one regex, identical in both blobs:
`tools/report-landing-audit.py:168-170`

```python
def landed_match(text):
    return re.search(r"^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)", text,
                     re.S | re.M)
```

It neither tracks code fences/HTML blocks nor accepts CommonMark's permitted
heading spellings, and it cuts the section at the first `^## ` line regardless
of context. The self-test at `tools/report-landing-audit.py:643-645` pins only
the mid-line prefix case (`prefix ## Landed changes` is not a heading); the
same anchoring principle is not applied to fences, comments, or indentation.

Why the false-clean rows are wrong, not just parser pedantry: reports are
Markdown, and the required element is a rendered section (prompt
`.ufo/prompts/kama-round-23.md:107`, KQ28 `corpus/QUALITY.md:151`). In
CommonMark 0.31.2 a fenced block's content is literal — "A code fence is a
sequence of at least three consecutive backtick characters"
(<https://spec.commonmark.org/0.31.2/#fenced-code-blocks>) — and an HTML block
"is a group of lines that is treated as raw HTML"
(<https://spec.commonmark.org/0.31.2/#html-blocks>). Quoting the template in a
fence therefore satisfies the check without producing the section; a
non-compliant report exits 0. Conversely, `landed_match` misses valid H2
spellings: "The opening `#` character may be preceded by up to three spaces of
indentation" and "must be followed by spaces or tabs"
(<https://spec.commonmark.org/0.31.2/#atx-headings>). The indented/setext rows
are the weaker finding (the format may intend the literal line), but they show
the same recognizer is spelling-sensitive.

Impact on the current population: a textual scan of all 20 committed fleet
reports (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-*/kama.md`) found
0 headings inside fences or HTML comments and 0 indented/spaced heading
variants, although 9 of the 20 reports contain line-start code fences
(rounds 1, 2, 11–16, 22). So no current
verdict is wrong; the hole is latent (e.g. a future report that quotes the
template would pass). Rounds 1–2, which have no canonical Landed heading, are
outside the audited 10–22 range, consistent with RevControls' "synthetic only;
zero real cases".

## What I did NOT verify

- I ran only the C04 row of `repo-state-grid.py`, not the other 33 rows; I did
  not rerun the 50/50 selftest, the rounds 10–22 ledger, or L1's 26/26 and 8/8
  claims beyond this row.
- Variants were not cross-checked with a real Markdown renderer; CommonMark
  0.31.2 spec text was the authority.
- I did not test fixes, `--report N=PATH` drafts, errata paths, other rounds,
  or other defect kinds. No repo-local git-state variant of the Landed channel
  was constructed in this slice.
- The frozen blob's identity was verified by object id/sha256 only, not by its
  own provenance history.
- The population scan is my own fence/comment state machine, not a Markdown
  parser; it establishes absence of those constructs in the 20 reports only.

## Files written

- `.ufo/waves/round-23/falsify/advice/RowC04LandedSection.md` (this report)
- `.ufo/waves/round-23/falsify/out/CloseKama22.RowC04LandedSection-2/repro.py`
- `.ufo/waves/round-23/falsify/out/CloseKama22.RowC04LandedSection-2/results.txt`
- `/tmp/kama-r23w2/CloseKama22.RowC04LandedSection-2/` (clone)
- `/tmp/rowc04-fixture/` (transient frozen blob + hand fixtures)
- `/tmp/commonmark-spec.txt` (spec text for the quotes)

Tool installs: none.
