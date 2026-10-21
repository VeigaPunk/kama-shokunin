# SrcS090 — git-replace(1) row S090 re-open (falsify wave)

Seat: CloseKama22.SrcS090-2 (leaf). Read-only on the lane; no lane/fleet file
was edited. Lane HEAD verified:
`git -C .../kama-shokunin rev-parse HEAD` → `245a37f69628c2c6bb29bbf17897d8fb5946c857`
(exit 0). `corpus/SOURCES.md` and `corpus/lessons/round-23.md` are unmodified
in the worktree (`git status --porcelain` lists only SKILL.md, QUALITY.md,
README.md, `knowledge/error-is-not-a-verdict.md` plus untracked `.ufo/`), so
the working-tree rows equal the committed rows.

## Verdict: ADMIT (row holds)

The URL is live, the Gate quote is a byte-exact substring of the fetched page
(including its 2.55.0 versioned copy), the version claim is exact, `scope` /
`teaches` stay inside the source sentence, and the one `used-by` path exists
and cites the row. One procedural defect is in the **lesson Gate line, not the
row**: S090's Gate bullet omits the section location that
`SOURCES-CONTRACT-v1` rule 1 requires, and its 16-word quote truncates the
parenthetical that defines "reachability traversal". Both are repairable by an
append-only erratum; neither changes the row's claim, so no `supersedes` row is
warranted.

## 1. Row under test (committed at 245a37f6)

`git show 245a37f6:corpus/SOURCES.md:102` (also `corpus/SOURCES.md:102` in the
worktree):

```
| S090 | git-replace(1) — https://git-scm.com/docs/git-replace | docs | A | default scope of replacement refs | DESCRIPTION paragraph on default use and `--no-replace-objects`; page "last updated in 2.55.0", 2.56.0 no changes, opened 2026-10-21 | Replacement refs apply by default to all commands except reachability traversal, so an audit's log/cat-file/show see the replacement unless disabled. | mined | 2026-10-21 | on-release | corpus/lessons/round-23.md |
```

Gate line, `corpus/lessons/round-23.md:30-32` (committed):

```
- S090 https://git-scm.com/docs/git-replace (2.55.0, 2.56.0 no changes) —
  "Replacement references will be used by default by all Git commands except
  those doing reachability traversal". Supports F03–F05.
```

## 2. URL and version claimed — hold

- `curl -sS --max-time 30 https://git-scm.com/docs/git-replace -o
  /tmp/r23w2-git-replace.html` → exit 0, HTTP 200 (2026-10-21).
- Fetched page header/selector: `git-replace last updated in 2.55.0` and
  version-list entry `2.56.0 no changes` — exactly the row's and Gate's
  labels. Matches the same two strings a second reader fetch returned
  independently at the start of this seat.
- Versioned copy check: `curl -sS -o /tmp/r23w2-git-replace-255.html -w
  "http=%{http_code}" https://git-scm.com/docs/git-replace/2.55.0` →
  `http=200`; the full quote below is present there too, so "2.55.0" is the
  version whose text the quote belongs to.
- Host engine: `git --version` → `git version 2.56.0`, consistent with the
  "2.56.0 no changes" claim.

Caveat (same class the S089 falsify seat recorded): the registered URL is the
unversioned alias, so "2.55.0 / 2.56.0" is an opening-time label, not a pin.
The row records it as a label and sets `recheck = on-release`, which is the
correct cadence; nothing overreaches here.

## 3. Quote verbatim — hold (with truncation note)

Full sentence in the fetched page's DESCRIPTION section (HTML tags stripped,
whitespace normalised; `python3` check printed `quote_present: True` and
`parenthetical: True`):

> "Replacement references will be used by default by all Git commands except
> those doing reachability traversal (prune, pack transfer and fsck)."

21 words, DESCRIPTION. The Gate's 16-word version
("...except those doing reachability traversal") is an exact substring of this
sentence; the row's `anchor` cell names the DESCRIPTION paragraph and the
`--no-replace-objects` paragraph. The same DESCRIPTION also supplies the
disable mechanism: "It is possible to disable the use of replacement
references for any command using the `--no-replace-objects` option just after
*git*." and notes `GIT_NO_REPLACE_OBJECTS` ("env_var: True" in the same check).
Both quotes are ≤25 words and exact.

**Finding (lesson Gate, not the row):** the Gate bullet does not name the
section, while `SOURCES-CONTRACT-v1` rule 1 requires the Gate to record "a
≤25-word quote with its location grounding `teaches`". S089's bullet gives
`OPTIONS:`; S090's gives none. The row's `anchor` cell does give
"DESCRIPTION paragraph", so the fact is recorded in the registry but not in
the lesson record. Also, truncating "(prune, pack transfer and fsck)" leaves
"reachability traversal" undefined at the Gate; a reader could read `git log`'s
history walk as reachability traversal and conclude the opposite of the
teaches. The full sentence resolves it, and the behavioural checks below
confirm the teaches. Recommend an append-only lesson erratum quoting the full
sentence with `DESCRIPTION` named; do not rewrite the committed Gate line
(KQ22/KQ26).

## 4. Scope / teaches vs the quote — no overreach

- `scope` "default scope of replacement refs" — the anchored DESCRIPTION
  paragraphs are exactly about the default use and per-invocation disable of
  replace refs. Official git docs are tier-A authority for this scope.
  Narrower than the build draft (`SrcGitReplace.md` §3 scoped the same row to
  "which Git commands honour replace refs by default ...; not replacement
  safety or graft-file policy"), but the row's `teaches` does not claim
  replacement safety, grafts, transfer policy, or the CAVEATS/BUGS text, so no
  current cell exceeds the anchored material. A future claim about replace-ref
  safety would need a new row or an explicit scope edit (which would itself be
  a `supersedes` row under KQ31).
- `teaches` sentence 1 restates the quote: all Git commands use replacement
  refs by default except reachability traversal. Holds.
- `teaches` sentence 2, "an audit's log/cat-file/show see the replacement
  unless disabled", is an application instance, not an extension: log,
  cat-file and show are Git commands and are not in the parenthetical
  exception list (prune, pack transfer, fsck), and "unless disabled" is the
  documented `--no-replace-objects` / `GIT_NO_REPLACE_OBJECTS` path. The three
  named commands are exactly the audit's three readers of repository data:
  `tools/report-landing-audit.py:183,204` (`git log`), `:144-160,256`
  (`cat-file`), `:298,371` (`show`), all through the shared wrapper at
  `:114`, which prepends `GIT_ISOLATION = ("--no-replace-objects", ...)`
  (`:93`). So the sentence grounds a mechanism the code actually relies on.
- Independent behavioural check of the instance (fresh `/tmp` repo,
  `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, explicit identity set
  per command, `git 2.56.0`):
  - `git log -1 --format=%s` → `replacement subject` (real: `real subject`);
  - `git cat-file -p <sha>` → `replacement subject`;
  - `git show -s --format=%s <sha>` → `replacement subject`;
  - `git show HEAD:marker.txt` after replacing HEAD's commit with a decoy tree
    → `marker` (the decoy path resolves);
  - each of the three with `git --no-replace-objects ...` → `real subject` /
    the decoy path does not exist (`fatal: path 'marker.txt' does not exist in
    'HEAD'`).
  This is the F03/F04/F05 premise form and matches the fixtures'
  `require()`s: `tests/report-audit/repo-state-grid.py:239`
  (`log -1 --format=%s`), `:249` (`cat-file -t` on a fabricated 40-hex),
  `:267` (`show HEAD:{rel}`). A fabricated-key check also passed
  (`refs/replace/<absent-40hex>` → `cat-file -t` = `commit`;
  `--no-replace-objects` → `could not get object info`), which is the F04
  fixture (`:248`) mechanism. The row's teaches does not itself claim the
  dangling-key behaviour; it is the fixture's construction, and the doc's
  "no other restriction on the replaced and replacement objects" is in the
  same DESCRIPTION block. No row overreach; tiny attribution nuance only.
- `git fsck` ignoring replacements is the documented exception and is outside
  the row's claim; not asserted. The page's BUGS/CAVEATS text (compare
  replaced-vs-replacement; commit-graph disabled) does not contradict any cell
  and is not claimed.

## 5. Used-by — cites and relies

- `corpus/lessons/round-23.md:30-32` is the only `used-by` path. It cites the
  URL, version and quote, and binds the row to F03–F05 ("Supports F03–F05"),
  whose fixtures are the three `require()`s above. So the row is `mined`
  consistently with the contract's definition ("cited by ≥1 path in
  `used-by`").
- Cross-check: `git grep -n "S090" 245a37f6 -- .` returns only
  `corpus/SOURCES.md:102` and `corpus/lessons/round-23.md:30`; `git grep -n
  "git-replace\|refs/replace" 245a37f6 -- corpus` adds only S094's unrelated
  layout row. No knowledge entry cites S090, so `used-by` is not
  under-declared against the contract's "knowledge entries or lessons"
  definition.
- Observation, not a defect: `tests/report-audit/repo-state-grid.py` F03–F05
  genuinely rely on the documented default behaviour, but under the contract
  `used-by` is limited to knowledge entries/lessons, and the grid does not
  cite the row, so its absence is convention-consistent (S089's cell does list
  `tools/report-landing-audit.py`, an extra-row practice, not the rule).

## 6. Row-shape / append-only checks

- Census over the committed blob: 11 cells (`NF==13`), `malformed: 0`;
  `S090-count: 1`; no duplicate ids; `used-by` path
  `corpus/lessons/round-23.md` exists; `kind=docs`, `tier=A`, `status=mined`
  pass the contract's enum/tier rules; anchor is a section + version, not a
  homepage.
- `python3 tools/sources-append-only.py --from
  4fe9339f8fc3a4a4a479d9c938a850da12f1124d --to
  245a37f69628c2c6bb29bbf17897d8fb5946c857` → prints `added S089 ... added
  S095`, `no append-only violations`, exit 0. `git log --oneline
  4fe9339f..245a37f6 -- corpus/SOURCES.md` shows the single adding commit.
- Commit 245a37f6 touches only `corpus/SOURCES.md` (+7 rows) and
  `corpus/lessons/round-23.md` (+92), consistent with the declared landing.

## 7. What I did NOT verify

- Did not run `tests/report-audit/repo-state-grid.py` or
  `isolation-mutants.py`; the declared C1 counts (26/26 faults, 8/8 controls,
  22/24 mutants) are taken as reported, not re-measured. My behavioural checks
  cover the three commands S090 names, not the audit's end-to-end verdicts.
- Did not exercise the frozen arm (`4fe9339f` blob) for F03–F05.
- Did not fetch or diff a versioned 2.56.0 page (the selector says "no
  changes" and provides no version link); the "2.56.0 no changes" label is
  taken from the live selector plus the host binary version.
- Did not test git < 2.45 (the lesson's floor) or any release other than the
  host's 2.56.0.
- Did not verify git-scm.com page stability beyond the 2026-10-21 fetches.
- Did not audit every `git()` call site in `report-landing-audit.py` for an
  isolation bypass; only the wrapper and the four named readers were checked.
- Did not verify the page's BUGS/CAVEATS implications for any audit path
  beyond noting they are not claimed by the row.

## Files written

- `.ufo/waves/round-23/falsify/advice/SrcS090.md` (this report)
- Scratch only under `/tmp`: `/tmp/r23w2-git-replace.html`,
  `/tmp/r23w2-git-replace-255.html`, `/tmp/r23w2-SOURCES-245a37f6.md`,
  `/tmp/r23w2-src-s090/`, `/tmp/r23w2-src-s090-show/`,
  `/tmp/r23w2-src-s090-dangling/`.

No installs or upgrades performed; no tool records to report.

## Addendum (2026-10-21) — cat-file forms the audit actually uses

Second behavioural pass on the same `git 2.56.0`, fresh `/tmp` repos, global
and system config nulled, identity set per command:

- Blob replacement: `git replace <blob-one> <blob-two>`; `git cat-file blob
  <blob-one>` → `two`; `git --no-replace-objects cat-file blob <blob-one>` →
  `one`. So `cat-file blob` (the form at
  `tools/report-landing-audit.py:256`) honours the replacement.
- `--batch-check` (the form at `tools/report-landing-audit.py:144-160`), with
  a fabricated key backed by `refs/replace/<absent-40hex>` →
  `refs/replace/<absent-40hex> -> real commit`:
  `printf '%s\n' "$FAKE" | git cat-file --batch-check` →
  `abcdefabcdefabcdefabcdefabcdefabcdefabcd commit 151`;
  with `git --no-replace-objects` → `abcdef... missing`. This is exactly the
  F04 fixture mechanism (`repo-state-grid.py:248`) and confirms that S090's
  "cat-file sees the replacement" instance covers the audit's `--batch-check`
  resolver, not only the `-t/-p` forms tested earlier.

No row cell changes; verdict remains ADMIT.
