# kama round 81 — the round-80 self-record is graded, and late acceptance becomes a rule with a register

Lane: kama. Round 81 (attempt 1). Base `e7d2fd729cf8204c89c32534303bc9f2a97fcee4` (round-80
non-author closure tip); frozen plan `plans/round-81-claims.md`; sealed revision for C1
`a2af1af59faf6cf66fe854559293c4e4b441aff3` (the round-80 record tip, an ancestor of the base).
Lane tip at drafting `2c1faed0354dbb3cb9f869cb1af4a9302dfcfd4e`.

## Gate

Every candidate below was opened by this seat with
`curl -sSL -o <body> -w '%{http_code} %{size_download} %{url_effective}'` on 2026-11-04. Status,
bytes and sha256 per URL are recorded in `.ufo/waves/round-81/w1/SC02Lesson/curl.txt`, and the
fetched bodies sit beside it; located-quote contexts and word counts are in `quotes.txt`. No quote
or date below is copied from an earlier round.

| Candidate | Source | Accessed | Located quote (≤25 words) | Decision | Reason and flip |
|---|---|---|---|---|---|
| S558 (supersedes S557) — Ollama `docs/api/openai-compatibility.mdx` at v0.40.11 | https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx — HTTP 200, 25472 bytes, sha256 `44071a12…760cd5` | 2026-11-04 | "`owned_by` corresponds to the ollama username, defaulting to `"library"`" — `### /v1/models` (line 290) → `#### Notes`, line 295 (9 words) | **admit** (tier A, docs) | The pinned release's own bytes for the OpenAI-compatible model list the probe reads to decide a model-API listener, at the path that serves the digest S557's row already states (25472 bytes, `44071a12…`), so the supersession changes the URL, not the evidence. Flip: a round that stops reading `/v1/models` as a listener test, or a newer pinned tag whose bytes differ. |
| S559 — `git-merge-base` | https://git-scm.com/docs/git-merge-base — HTTP 200, 41397 bytes, sha256 `46d106b7…b49644` | 2026-11-04 | "Check if the first <commit> is an ancestor of the second <commit>, and exit with status 0 if true, or with status 1 if not." — §OPTIONS → `--is-ancestor` (25 words) | **admit** (tier A, docs) | Grounds C2's strict-ancestry test with the command's own contract: 0 means ancestor, 1 means not, and any other status is an error — so a late row whose introducing commit is not a strict descendant of the event commit is a finding, not a pass. Flip: an acceptance rule that stops binding rows by ancestry. |
| S560 — `git-diff-tree` | https://git-scm.com/docs/git-diff-tree — HTTP 200, 256938 bytes, sha256 `6473d8a3…ef5000` | 2026-11-04 | "When --raw, --numstat, --name-only or --name-status has been given, do not munge pathnames and use NULs as output field terminators." — §OPTIONS → `-z` (20 words) | **admit** (tier A, docs) | Grounds the record shape the frozen audit parses: `--name-status` emits a status-plus-path record, `-z` makes NUL the field and record terminator so a newline inside a path cannot forge a row, and `--no-renames` turns rename detection off so a rename stays visible as its delete plus add. Flip: an audit that stops parsing NUL-terminated `--name-status` records. |
| S561 — vLLM v0.33.0 release notes | https://github.com/vllm-project/vllm/releases/tag/v0.33.0 — HTTP 200, 163538 bytes, sha256 `41b95980…d34bda` | 2026-11-04 | "vLLM v0.33.0" — the release body (`<pre class="commit-desc">`); the release's Atom `<content>` is the same string and nothing else (2 words) | **reject** | The page states no behaviour: its note text is the bare version string, so it grounds nothing this round measures (C1 grades a self-record, C2 an append-only register). The lane's pin is `v0.32.0` and `registry/engine-pin-relations.tsv` records `behind 1` against `v0.33.0`, so the release is a re-pin trigger, not evidence. Warning inventory (R80V4 restated): the W04 duplicate-URL class is pre-existing, no row carries this URL at the tip (`git show 2c1faed0:corpus/SOURCES.md \| grep -c` → 0), and S558's corrected path is not S557's filed path, so this round adds no duplicate-URL row. Flip: a round that re-pins vLLM or grades a v0.33.0 behaviour — then this page is opened again together with the docs or source page that documents the change. |

Gate result: 3 admits (S558, S559, S560), 1 reject (S561); four candidates, four decided.

### Gate erratum — S557

S557's filed URL
`https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api-openai-compatibility.mdx`
was opened on 2026-11-04 and answered HTTP **404** with a 14-byte body (`404: Not Found`). The
corrected URL `https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx`
answers HTTP **200**, 25472 bytes, sha256
`44071a1277796b5ad28e51e561afd94ac75f6f76cd75c4b8d9d80b9dff760cd5` — exactly the digest and size
S557's own row states, so the row's bytes were right and only the path was wrong. Access date
2026-11-04. Located quote (≤25 words), from `### /v1/models` (line 290) → `#### Notes`, line 295:
"`owned_by` corresponds to the ollama username, defaulting to `"library"`" (9 words).

The same row's anchor is one line short: it cites "response notes lines 293-294", while the notes
are lines 294-295 (`created` at 294, `owned_by` at 295), under `### /v1/models` at 290 and
`#### Notes` at 292. The corrected path is filed as S558 (R80V2); the dead path stays in S557's row
byte-intact, since the registry is append-only. This subsection is the Gate record routed defect
R80V3 requires. Receipts: `curl.txt`, `body-ollama-openai-compatibility.mdx`,
`s557-filed-404.txt`, `quotes.txt`.

## Corrections

The round-80 record is graded by `tools/round81-selfrecord-round80.py`. The counter is on disk but
uncommitted at the lane tip `f6cb5303` (sha256 `ddeacbbe…8471db`; an executor seat lands it), so
this seat read its parser and called its `derive()` read-only rather than treating it as frozen. It
returns exactly the six declared→observed pairs below, all six stale, over `git show <rev>:<path>`
reads and never the worktree. The plan's enumeration control fixes the same state as
`SELFRECORD_R80_ENUM claims=6 stale=6 corrected=0`, exit 1. Each fact is answered by exactly one
block below; the six parse with the counter's own `CORRECTION` regex over the section as the
counter reads it, and `old`, `new`, `at` and `date` bind for all six.

`corrected F1 old=c1-selftest=pass=9 new=c1-selftest=pass=11 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

`corrected F2 old=c3-selftest=pass=6 new=c3-selftest=pass=12 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

`corrected F3 old=calibration-row-selftest=pass=9 new=calibration-row-selftest=pass=11 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

`corrected F4 old=log-c1-selftest=pass=9 new=log-c1-selftest=pass=11 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

`corrected F5 old=coverage-last-change=round-79 new=coverage-last-change=round-80 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

`corrected F6 old=newest-closure=round-79-verifier-spotcheck.md new=newest-closure=round-80-verifier-spotcheck.md at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

**F1 — `c1-selftest`.** `SCORECARD.md:4781` at the sealed revision writes
`verified`; selftest `pass=9 fail=0` (`measured/after/c1-selftest.out`). The receipt that row
cites, `.ufo/waves/round-80/measured/after/c1-selftest.out`, prints
`SELFRECORD_R79_SELFTEST pass=11 fail=0` and `EXIT=0`, at the sealed revision and unchanged at the
tip. The record claims nine selftest arms; its own receipt prints eleven.

**F2 — `c3-selftest`.** `SCORECARD.md:4783` writes
selftest `pass=6 fail=0` (`measured/after/c3-selftest.out`); that receipt prints
`OLLAMA_CENSUS_SELFTEST pass=12 fail=0` and `EXIT=0` at both revisions. The record claims six;
its own receipt prints twelve.

**F3 — `calibration-row-selftest`.** The `## Axes` calibration row (`SCORECARD.md:18`) writes
"`--selftest` → `pass=9 fail=0`" for the same counter, so the stale tally was also the axis
argument. The same `c1-selftest.out` prints `pass=11`.

**F4 — `log-c1-selftest`.** The append-only `LOG.md` §Round 80 C1 bullet (`LOG.md:3288`) writes
"selftest `pass=9 fail=0`"; the same receipt prints `pass=11`. The filed LOG bytes are not
rewritten — the correction is the appended `LOG-CORRECTION round=80` entry naming the superseded
selftest tallies.

**F5 — `coverage-last-change`.** The `## Axes` coverage row (`SCORECARD.md:17`) carries, in its
last-change cell, `score round 10; evidence re-anchored round 79`, while the same row's evidence
cell opens "round 80: one admitted entry (`unregistered-class-second-engine`, source S554) …". No
receipt file prints this value; the witness is the row's own evidence cell, which names round 80,
and the correction's new value is read from that cell rather than guessed.

**F6 — `newest-closure`.** The calibration row (`SCORECARD.md:18`) says "the newest non-author
closure is `corpus/lessons/round-79-verifier-spotcheck.md`". The sealed tree lists
`*-verifier-spotcheck.md` files only through round 79; at the tip
`corpus/lessons/round-80-verifier-spotcheck.md` exists and is the newest such file. No receipt
prints this value; the witness is the tree listing at the tip. The claimed path is one round stale.

The corrections bind two append-only record fixes, filed by the L1 and not by this seat.
`SCORECARD.md` gains an appended `#### round-81 correction` block whose body carries the five
superseded cells in the counter's own marker forms — `C1-selftest pass=9 -> pass=11`,
`C3-selftest pass=6 -> pass=12`, `calibration-row pass=9 -> pass=11`,
`coverage-last-change round 79 -> round 80`,
`newest-closure round-79-verifier-spotcheck.md -> round-80-verifier-spotcheck.md` — because the
counter reads the block from that heading to the next heading and looks for each marker inside it,
so a block that names a cell in other words leaves its fact `unbacked`. `LOG.md` gains a
`LOG-CORRECTION round=80` entry carrying `selftest tallies pass=9/pass=6 -> pass=11/pass=12` (the
F4 marker is looked for in the whole LOG, not in a marked block). The filed §Round 80 and LOG
bytes are not rewritten.

## Mistakes

| Class | Evidence pointer | Captured-by | Fix |
|---|---|---|---|
| `post-hardening-claim-on-pre-hardening-tally` | At `a2af1af5`, `SCORECARD.md:4781` (C1 row) states `selftest pass=9 fail=0`, `SCORECARD.md:4783` (C3 row) states `selftest pass=6 fail=0`, `SCORECARD.md:18` (calibration row) states `--selftest` → `pass=9 fail=0`, and `LOG.md:3288` (C1 bullet) states `selftest pass=9 fail=0`; the receipts those cells cite, `.ufo/waves/round-80/measured/after/c1-selftest.out` and `c3-selftest.out`, print `SELFRECORD_R79_SELFTEST pass=11 fail=0` and `OLLAMA_CENSUS_SELFTEST pass=12 fail=0`. `SCORECARD.md:4796` then asserts "The C1/C2/C3 tallies above are the post-hardening measurements", while the same record's own erratum at `LOG.md:3338` names the same two tallies as pre-hardening: `SELFRECORD_R79_SELFTEST pass=11 fail=0` (was 9) and `OLLAMA_CENSUS_SELFTEST pass=12 fail=0` (was 6). So the erratum certifies a property of cells it did not update. | the F1–F4 facts of `tools/round81-selfrecord-round80.py` (round 81; F1 `c1-selftest`, F2 `c3-selftest`, F3 `calibration-row-selftest`, F4 `log-c1-selftest`) — the counter grades each declared tally against the line its own receipt prints and requires one value-bound correction per stale fact, so the four cells cannot stay at the pre-hardening number while the erratum stands. | `tools/round81-selfrecord-round80.py` (this round's C1 counter) plus `corpus/QUALITY.md` KQ133: a hardening note may certify only the cells it names and updates, so an erratum sentence such as "the tallies above are post-hardening" is admissible only when each tally it covers equals its receipt's printed line at the same revision. |

## Freeze divergences

None. Read against the tree before drafting: the six fact locations and value strings, the two
witness receipt paths (`measured/after/{c1,c3}-selftest.out`), the revision order (sealed
`a2af1af5` → base `e7d2fd72` → freeze tip `2c1faed0`), the S557 URL defect (reproduced, 404) and
the two record files the corrections bind (`SCORECARD.md`, `LOG.md`) all match the plan. The
sealed record's three defects — the stale tallies, the dead S557 path and the missing S557 Gate
record — are answered by this round's corrections and erratum; they are record defects, not
divergences between the plan and the tree.
