# S01SourcesReopen — S515 re-open, latest-opened-source inspection, case-6 evidence

Seat: `S01SourcesReopen` (scribe, leaf; no subagent dispatch). Round 57, kama-shokunin.
Scope: read-only re-open and inspection. No file in the lane source tree, registry, lesson,
tool, judge, or fleet root was created or modified. Artifacts are new files under
`.ufo/waves/round-57/sources/` only (my wave report path). No commits, no git/jj mutation.

## Reopened source (S515)

- **URL:** https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT
  (same URL as `corpus/SOURCES.md:268` and `corpus/lessons/round-56.md:18`).
- **Access date:** 2026-10-27, HTTP response `date: Tue, 27 Oct 2026 18:07:05 GMT`.
  Command `curl -sS -L --max-time 60 -D headers.txt -o git-config-live.html
  'https://git-scm.com/docs/git-config'` → exit 0, `HTTP/2 200`.
- **Page identity:** 830605 bytes, sha256
  `706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a`.
  `cmp` against the round-56 snapshot (`.ufo/waves/round-56/sources/git-docs-git-config.html`)
  and the round-55 snapshot (`.ufo/waves/round-55/sources/git-docs-git-config.html`) →
  **byte-identical, cmp exit 0 both**. The byte-identical round-57 copy written by a sibling
  seat is `.ufo/waves/round-57/sources/git-config-live-2026-10-27.html` (same sha256); I did
  not duplicate the 830 KB page, this receipt cites that copy plus `sha256.txt`.
- **Source location:** section `ENVIRONMENT`, definition group headed
  `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>`; the anchor
  `id="Documentation/git-config.txt-GITCONFIGCOUNT"` occurs once (and its `href` once), the
  `<dt>` text is exactly `GIT_CONFIG_COUNT`, and the next heading is `EXAMPLES`.
  Anchor byte offset in the fetched HTML: 168372; located quote byte offset: 169031.
- **Located quote (verbatim, 18 words, source glyph U+2019 in “process’s”):**
  > all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process’s runtime configuration
- **Context the quote is cut from:** the same sentence begins
  “If GIT_CONFIG_COUNT is set to a positive number, all environment pairs …”.

Quote length and agreement checks (`run-live.out`, `run-snapshot.out`):
`check=quote_word_count_matches_declared ok=True declared=18 counted=18`;
`check=quote_word_count_under_limit ok=True counted=18 limit=25`;
`check=quote_in_git_config_count_dd ok=True occurrences=1`;
`check=lesson_quote_agrees_with_registry ok=True lesson_words=18`.

Glyph detail (measured, not a content difference): the fetched page uses U+2019, the
round-57 lesson quote is glyph-identical to the source, while `corpus/SOURCES.md:268` and
`corpus/lessons/round-56.md:18` transcribe the same words with ASCII `'`. Word counts are 18
in all four places.

## Revision marker (claimed vs displayed)

S515's anchor cell says “git 2.56.0 (page last updated in 2.56.0)”. The live page displays
`git-config last updated in 2.56.0`, and its version dropdown pairs `2.56.0` with release date
`2026-09-28` (`page-revision-pairs.txt`). Marker claim: **supported**.

Supersession rationale, measured: S511's anchor cell carries no revision marker, and the
round-55 snapshot already contained `git-config last updated in 2.56.0` — so “the revision
marker was available but omitted from S511's anchor” is **supported** at the current bytes.

## Latest opened source context (no edits)

Read-only inspection of `corpus/SOURCES.md` (`registry-cells.txt`, `tier-cells.txt`,
`s516-context.txt`). The registry moved while this seat ran, so both states are recorded:

- At my first read (2026-10-27 ~18:09Z): 256 rows, maximum id `S515` — matching the round-56
  after-census count.
- At deposit time (~18:11Z): 257 rows, maximum id `S516`; the L1 appended an own-work row
  during the wave. **S516 is now the latest opened source**, and its Gate text appears in
  `corpus/lessons/round-57.md`.
- S515 cells (unchanged in both reads): kind `docs`, tier `B`, status `mined`, opened
  `2026-10-27`, recheck `180d`, used-by `corpus/lessons/round-56.md`; scope is the
  *correction* of S511's revision anchor.
- S516 cells: kind `own-work`, tier `A`, status `mined`, opened `2026-10-27`, recheck
  `every round`, used-by `tools/round56-prereg-check.py, corpus/lessons/round-57.md`; anchor
  “`main()` lines 69–83 at lane commit `b89bdab2…`”.
- S511 (superseded) and S510 cells are unchanged; neither was rewritten, consistent with the
  round-56 lesson's append-only statement.
- `corpus/lessons/round-57.md:12,14` now cites S515 (re-open sentence and the source of its
  scope statement), but S515's `used-by` cell does not list `corpus/lessons/round-57.md`.

S516 context, measured against the base blob (`git show b89bdab2:tools/round56-env-leg-battery.py`,
87 lines, sha256 `69b77a6a…b51c5`, identical to the working-tree file): `def main()` is at line
64; the four cited call sites exist at lines 70, 71, 80, 81, and `return 0 if all(results)`
is line 83, so the cited range covers every named call. The located quote is a byte-exact
match to line 70. Advisory only: the Gate declares “(5 words)” for that quote; measured
whitespace tokens are 6 (5 if the standalone `/` operator token is excluded), and the rule
that matters (≤25) is met either way. Recording the measurement, not a verdict.

Advisory only (I am a dispatched lane seat, not the integrator; no verdict is rendered):
the `used-by` gap is the same class the round-56 lesson handled for S512, where a new citing
artifact was added to `used-by` at integration. Recording it here so the L1 can either add the
cell at integration or state why a round-57 Gate citation does not count as use.

Tier observation, advisory only: the correction pairs differ in tier — S510 `B` → S514 `A`
(git(1)), S511 `B` → S515 `B` (git-config(1)), both from the same vendor manual family, and
neither row states a tier rationale. `SOURCES.md` records no A/B legend beyond
“Tiers are scoped to scope, never global” (`corpus/SOURCES.md:5`) and `corpus/QUALITY.md`
KQ6's “a `C` row never supports an entry alone”. Not a defect claim; flagged for calibration
if the L1 wants the asymmetry explained.

## Admit/reject decisions spot check (advisory; non-author)

Decision sampled: **S515 — ADMIT, tier B, mined** (`corpus/lessons/round-56.md:18`).
Evidence for the decision, independently re-opened this round: the located quote exists
verbatim at the named section, is 18 words (≤25), names exactly the environment-pair
mechanism the row's scope claims, the revision marker is displayed, and the anchor resolves
to a unique id. The supersession relation to S511 holds (S511 anchor lacks the revision
marker that its own snapshot displayed). Advisory: the admission is supportable on this
evidence; I do not adjudicate it, and no registry cell was changed.

## Distinct case 6

Tested independently. Separate evidence file (required by the seat spec):
`.ufo/waves/round-57/sources/S01SourcesReopen-case6.md`; script and raw outputs in
`.ufo/waves/round-57/sources/S01SourcesReopen/`.

## Commands and exits

| # | Command (cwd = scratch `/fast/scratch/hyaku/kama-r57/S01SourcesReopen`) | Exit | Output |
|---|---|---|---|
| 1 | `curl -sS -L --max-time 60 -D headers.txt -o git-config-live.html 'https://git-scm.com/docs/git-config'` | 0 | `HTTP/2 200`, `date: Tue, 27 Oct 2026 18:07:05 GMT`, 830605 bytes |
| 2 | `sha256sum git-config-live.html` | 0 | `706b1566…bcd3d5a` (matches both prior snapshots) |
| 3 | `cmp -s git-config-live.html .ufo/waves/round-56/sources/git-docs-git-config.html` | 0 | byte-identical |
| 4 | `cmp -s git-config-live.html .ufo/waves/round-55/sources/git-docs-git-config.html` | 0 | byte-identical |
| 5 | `python3 s515_reopen_check.py --html git-config-live.html --label live-2026-10-27` | 0 | 8/8 base checks True; 4/4 mutants rejected; 26-word limit control red; `met=True` |
| 6 | `python3 s515_reopen_check.py --html <lane>/.ufo/waves/round-56/sources/git-docs-git-config.html --label round56-snapshot` | 0 | same 8 checks True; 4/4 mutants rejected |
| 7 | `python3 s515_reopen_check.py --html <lane>/.ufo/waves/round-56/sources/git-docs-git.html --label wrong-source-git1` | 1 | `met=False`; anchor/dt/quote/revision red — a different page cannot satisfy the binding |

`met=True` in rows 5–6 is *this seat's* verifier result over the cited evidence; it is not a
re-measurement or endorsement of the round's C1/C2 counter claims, which belong to other seats.

## Calibration of this seat's own check (red-before, honest record)

The first revision of `s515_reopen_check.py` printed, in one run:

```
check=url_matches_expected_anchor ok=False detail=https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT
mutant_reorder_clause rejected=False failed_checks=none
met=False
exit=1
```

Two self-inflicted defects, both found by the tool itself and fixed before the receipts above:
(a) the lesson URL was captured with a trailing comma, so the URL equality failed; (b) the
clause-reorder mutant did not apply (the source stores the apostrophe as `&#8217;`), so the
mutant silently became a no-op. The fixed script asserts `applied=` per mutant, because an
unapplied mutant is indistinguishable from a passing check — the exact failure class recorded
for round 56 C2. Post-fix receipts are `run-live.out` and `run-snapshot.out`.

## Round-56 outside defects

Not re-judged here (this wave is a build/attack wave, not judgment). Mapping observed while
reading: the round-56 non-author spot-check records C2 as unprovable on a no-op control
(`corpus/lessons/round-56-verifier-spotcheck.md`, §Claims re-check, C2), and the round-57
lesson records that class in its Mistakes table (`corpus/lessons/round-57.md`, rows
`calibration-staleness` and `no-op-counter`). My case-6 verifier is built so a no-op,
doctored, or wrong-page input is red (4 mutants + 26-word control + wrong-source run), and it
does not read any self-description as evidence.

## Tooling

No install or update was needed or performed; pacman transactions remained paused. Versions
used: `curl 8.23.0`, `Python 3.14.8`, `Linux 7.2.11-arch1-1` (`env.txt`). Scratch:
`/fast/scratch/hyaku/kama-r57/S01SourcesReopen/` (never `/tmp`).

## Artifacts

- `.ufo/waves/round-57/sources/S01SourcesReopen.md` (this report)
- `.ufo/waves/round-57/sources/S01SourcesReopen-case6.md` (distinct case 6, separate evidence)
- `.ufo/waves/round-57/sources/S01SourcesReopen/` — `commands.txt`, `env.txt`, `headers.txt`,
  `sha256.txt`, `section.txt`, `registry-cells.txt`, `tier-cells.txt`,
  `page-revision-pairs.txt`, `s516-context.txt`, `s515_reopen_check.py`, `run-live.out`,
  `run-snapshot.out`, `run-wrong-source.out`
- Live page bytes (not duplicated by this seat):
  `.ufo/waves/round-57/sources/git-config-live-2026-10-27.html` (sha256 matches row 2 above)

Out of scope for this seat and untouched: counter repair (C1/C2), registry/lesson edits,
round lesson Gate cells, commits/pushes, and any judgment of round-57 claims.
