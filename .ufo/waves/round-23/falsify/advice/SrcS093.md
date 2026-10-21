# SrcS093 — re-open of source row S093 (git-log encoding and follow)

Seat: `CloseKama22.SrcS093-2` (leaf, no dispatch). Lane base `245a37f69628c2c6bb29bbf17897d8fb5946c857`.
Target: `corpus/SOURCES.md:105` (S093) and its Gate quote at `corpus/lessons/round-23.md:41-44`.

## Verdict

**ADMIT** the row's factual content: both Gate quotes are verbatim on the fetched
page, the claimed page version is correct, and the scope/teaches clauses do not
exceed the `--encoding` paragraph or the `log.follow` entry. Two registry-level
defects were found, neither of which makes the row false (details in Caveats):
the Gate's F18/F19 attribution cites the wrong sentence of the same paragraph,
and the lesson's "log.follow … kept once" rejection note is contradicted by the
final registry (S091 and S093 both register `log.follow`; both Gate lines claim
F07). Verdict on the row alone: admit; caveat 2 needs an L1 correction.

## Evidence

### 1. Page fetch and version claim

Command: `curl -sSL --max-time 60 'https://git-scm.com/docs/git-log' -o /tmp/srcs093/git-log.html`
Observed: exit 0; `status=200 effective=https://git-scm.com/docs/git-log size=375834`;
second fetch with `-w` gave `status=200 … size=375834`. Host `git version 2.56.0` (context only).

Fetched page text: `git-log last updated in 2.56.0`, change list entry
`2.56.0 / 2026-09-28` (latest entry). This matches the row's
`page "last updated in 2.56.0"` (`corpus/SOURCES.md:105`) and the Gate's `(2.56.0)`
(`corpus/lessons/round-23.md:41`). No versioned URL was pinned; the row records the
observed floating-latest state, which is what it says.

### 2. Quote 1 — verbatim

Gate quote (`corpus/lessons/round-23.md:41-42`), 15 words:

> if iconv(3) fails to convert the commit, we will quietly output the original object verbatim.

Page, OPTIONS `--encoding=<encoding>` paragraph (exact substring after tag-strip and
whitespace normalization; raw page reads "Likewise, if iconv(3) fails\nto convert the
commit, we will quietly output the original\nobject verbatim."):

> Likewise, if iconv(3) fails to convert the commit, we will quietly output the original object verbatim.

Python exact-substring check on the extracted page text: `True`, word count `15`.
The anchor "`--encoding` paragraph" is correct: the sentence sits in the paragraph
beginning `--encoding=<encoding> Commit objects record the character encoding…`.

### 3. Quote 2 — verbatim

Gate quote (`corpus/lessons/round-23.md:42-44`), 19 words:

> If true, git log will act as if the --follow option was used when a single <path> is given.

Page, CONFIGURATION `log.follow` entry: exact substring `True`, word count `19`.
The following sentence ("This has the same limitations as --follow, i.e. it cannot be
used to follow multiple files.") is consistent with the row's "single-path" wording.
The page itself notes the `log.*` block below `i18n.logOutputEncoding` is "the same as
what's found" in git-config[1]; the text is still served on the cited URL, so the
anchor "CONFIGURATION `log.follow`" is accurate for this page.

### 4. Scope/teaches vs the quotes

`corpus/SOURCES.md:105` teaches: "If conversion fails, git outputs the original bytes
verbatim, so log text need not be valid UTF-8; `log.follow` turns a single-path log
into `--follow`."

- "original bytes verbatim" = the quoted "output the original object verbatim" (the
  object's message bytes). No scope extension.
- "log text need not be valid UTF-8" = the page's own adjacent sentence ("invalid
  sequences in the original commit may be copied to the output"), same paragraph.
- "`log.follow` turns a single-path log into `--follow`" = quoted sentence, with the
  single-path condition preserved in both scope and teaches.
- Scope "log output encoding fallback and the `log.follow` single-path rule" matches
  both anchors; nothing about decode policy of the consumer, commit-object validity,
  rename thresholds or multi-path history is asserted.

Empirical confirmation in a fresh `/tmp` repo (`/tmp/srcs093/rawprobe`,
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, identity/dates set per command):

| probe | commit | command | observed stdout (hex tail) | exit |
|---|---|---|---|---|
| A (F18/F19 shape) | raw commit, no `encoding` header, subject `note caf\xe9` | `git log -1 --format=%s "$A"` | `6e 6f 74 65 20 63 61 66 e9 0a` (verbatim) | 0 |
| B (iconv failure) | `encoding UTF-8` header, subject `note caf\xe9` | `git -c i18n.logOutputEncoding=ISO-8859-1 log -1 --format=%s "$B"` | `6e 6f 74 65 20 63 61 66 e9 0a` (verbatim), stderr empty | 0 |
| C (control: conversion succeeds) | `encoding ISO-8859-1` header, subject `note caf\xe9` | `git log -1 --format=%s "$C"` | `6e 6f 74 65 20 63 61 66 c3 a9 0a` | 0 |

B reproduces exactly the quoted iconv-failure passthrough. A shows the mechanism
that F18/F19 actually use (see Caveat 1).

### 5. Used-by: does the cited path rely on S093?

`corpus/SOURCES.md:105` used-by = `corpus/lessons/round-23.md` only. The lesson cites
both quotes and maps them to faults at `corpus/lessons/round-23.md:41-44`
("Supports F18/F19 and F07"). The reliance is real:

- **F07** `tests/report-audit/repo-state-grid.py:548` (`F07-log-follow-cutoff`, expected
  exit 1 + `landed-omitted`); fixture `tests/report-audit/repo-state-grid.py:289-300`
  sets `log.follow=true` and `require`s the first add to move to 1500. The audit reads a
  single path at `tools/report-landing-audit.py:203-205` (`git log --diff-filter=A
  --format=%at -- rel`), neutralizes the key at `:95` (`-c log.follow=false`), and splits
  commits at the cutoff at `:318-319`. Without isolation the cutoff is 1500 (lane commit
  at 2000 becomes post → false clean 0); with it the cutoff is 2500 (commit 2000 is pre
  and uncited → `landed-omitted`, exit 1). The fault depends on the quoted single-path rule.
- **F18/F19** `tests/report-audit/repo-state-grid.py:560-561`, fixture `:423-431`;
  the lane log is decoded with `errors="surrogateescape"` at
  `tools/report-landing-audit.py:183` precisely because log text need not be valid UTF-8.

## Caveats (reported, not reject grounds for the row)

1. **Gate quote selection for F18/F19.** The quoted iconv clause covers probe B (commit
   declares `encoding UTF-8`, output is another encoding, iconv fails). F18/F19's fixture
   does not declare an encoding (`raw_commit(..., headers=b"")`,
   `tests/report-audit/repo-state-grid.py:84-93,427-431`), so git takes the adjacent
   claim-equals-output clause in the same paragraph: "if an object claims to be encoded
   in X and we are outputting in X, we will output the object verbatim; this means that
   invalid sequences in the original commit may be copied to the output." The row's
   teaches stays literally true, but the Gate's "Supports F18/F19" rests on a sentence
   the Gate did not quote. Tighten by quoting the adjacent sentence as well (or instead
   for F18/F19).
2. **"Kept once" is false in the final registry.** `corpus/lessons/round-23.md:54-55`
   says the separate `log.follow` row was rejected as "same claim as S091, kept once".
   But `corpus/SOURCES.md:103` (S091) already names `log.follow` in its anchor, and
   `corpus/SOURCES.md:105` (S093) names it again in scope and teaches; the lesson maps
   F07 to both S091 (`:39`, "Supports F01, F07–F09…") and S093 (`:44`). The claim is
   registered twice and F07 has two supporting rows. Either drop `log.follow` from
   S093's cells or correct the lesson's rejection sentence; the Gate as written
   contradicts the registry it describes.
3. **used-by asymmetry (note only).** S089/S091/S095 list
   `tools/report-landing-audit.py`; S093 (and S092/S094) list only the lesson even though
   the tool implements both S093 facts at `:94-95`. The round has no single convention,
   so this is not scored as a defect, but the cell omits a real consumer.

## Did NOT verify

- Did not run `tests/report-audit/repo-state-grid.py` or `isolation-mutants.py`; the
  F07 flip above is read from the code paths, not observed as an audit exit.
- Did not run F18/F19 end-to-end (fixture construction/exit codes); only the underlying
  git byte output was observed.
- Did not verify page stability over time; the URL serves floating latest (2.56.0 today),
  and the row records that observed state, not a pin.
- Quote identity was checked after HTML tag-stripping and whitespace normalization, and
  the word counts are whitespace-delimited; no claim about raw HTML byte identity.
- Did not re-audit S089–S092, S094, S095, the corpus census, or Git's C source for iconv
  behavior beyond documentation plus the three probes.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/SrcS093.md`
  (this report). No clone edits, no tracked lane files, no commits.
