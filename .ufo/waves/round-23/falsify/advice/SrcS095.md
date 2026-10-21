# SrcS095 — Python bytes.decode strict errors (S095) re-open

Seat: `CloseKama22.SrcS095-2` (leaf, no dispatch). Lane base:
`245a37f69628c2c6bb29bbf17897d8fb5946c857` (`git -C <lane> rev-parse HEAD`,
exit 0). Read-only on tracked files; this report is the only file written.

## Verdict: REJECT the row as registered (narrow)

The quoted sentence is verbatim on the fetched page, the claimed page version
(`Python 3.14.9`) matches, and both `used-by` paths really cite or rely on the
row. The row is still rejected as written because its immutable `teaches` cell
asserts a **text-mode subprocess** mechanism that the anchored page does not
document at all, and the Gate's `Supports F01/F02/F16 mechanism` inherits that
gap for F01. The source is admissible under a narrowed `teaches` (or a separate
row anchoring the subprocess text-mode paragraph plus the io/TextIOWrapper
strict default). This does not falsify C1's observed fault grid; it is a
source-registry support defect, not a false quote.

## 1. URL, page and version claimed

Observed commands and output (2026-10-21):

```
$ curl -sSI https://docs.python.org/3.14/library/stdtypes.html
HTTP/2 301
location: https://docs.python.org/3.14/builtins/stdtypes.html

$ curl -sSL --max-time 60 https://docs.python.org/3.14/library/stdtypes.html \
    -o /tmp/s095.html -w 'http=%{http_code} size=%{size_download} final=%{url_effective}\n'
http=200 size=773977 final=https://docs.python.org/3.14/builtins/stdtypes.html
```

Page title, HTML-entity-decoded: `Built-in Types — Python 3.14.9
documentation`. The docs root `https://docs.python.org/3.14/` returns
`3.14.9 Documentation`. This matches the row's anchor text
(`corpus/SOURCES.md:107` at `245a37f6`) and the Gate's `(3.14.9)`
(`corpus/lessons/round-23.md:49-51`).

Version scope is honest: the row says `a series URL`
(`corpus/SOURCES.md:107`), so `3.14.9` is the opening-time render, not a micro
pin. The host interpreter is 3.14.8 (`python3 --version` → `Python 3.14.8`);
the row does not claim the host, and the quote is a docs claim, so this is not
a version overclaim. Caveat: the registered URL is the `/library/` alias, which
301s to the `/builtins/` page that actually carries the anchor; unlike the S017
Gate precedent this redirect is not recorded in the row. Minor provenance
issue only.

## 2. Quote located verbatim

Fetched page, `bytes.decode(encoding='utf-8', errors='strict')` /
`bytearray.decode(...)` errors paragraph (the shared paragraph after both
signatures):

> If 'strict' (the default), a UnicodeError exception is raised.

Nine whitespace-delimited words, within the Gate's ≤25-word limit. An exact
substring check after HTML tag-stripping and whitespace normalization returns
`True`, once in the section; `id="bytes.decode"` is present at the final URL.
The lesson Gate (`corpus/lessons/round-23.md:49-51`) reproduces the sentence
byte-equal after line unwrapping:

```
- S095 https://docs.python.org/3.14/library/stdtypes.html#bytes.decode
  (3.14.9) — "If 'strict' (the default), a UnicodeError exception is
  raised." Supports F01/F02/F16 mechanism.
```

So the Gate quote itself is exact and does not overreach. The defect is in the
registry row's `teaches`, below.

## 3. Scope / teaches versus the quote — the reject ground

Row (`corpus/SOURCES.md:107`):

- scope: `Python 3.14-series default decode error handler; a series URL`
- teaches: `The default strict handler raises UnicodeError, so text-mode
  subprocess output with invalid bytes raises unless the caller maps the
  error.`

The first clause restates the quote. The second clause names a different API.
On the entire fetched page, case-insensitive counts are zero for `text mode`,
`subprocess` and `TextIOWrapper`; every `UnicodeError` occurrence is the
bytes/bytearray decode paragraph above. The page therefore says nothing about
text-mode subprocess output or its default error handler. The subprocess page
does have the text-mode sentence — “opened in text mode using the specified
encoding and errors or the io.TextIOWrapper default” — but it never states
that the default is `strict` (its only “strict” substring on the page is
inside “restriction”), and the io/TextIOWrapper strict default is on a page
that was not opened by this round. The build-wave scribe's own
`.ufo/waves/round-23/build/advice/SrcPythonDecode.md` listed the
TextIOWrapper default as “not verified” and the io/locale docs as an unopened
lead; the final row nonetheless asserts the composed claim.

The assertion is behaviourally true — on host Python 3.14.8,
`subprocess.run([...], capture_output=True, text=True)` over a `\xff` byte
raises `UnicodeDecodeError` (observed) — but truth is not the admission test
here: the cited section cannot establish it. KQ6/KQ13 require the statement to
be supported by the cited source's actual section; `bytes.decode`'s default
is not documentation of `subprocess` text mode.

Consequence for the Gate. `round-23.md:51` says the row `Supports
F01/F02/F16 mechanism`. That is accurate for F02/F16: both are committed
git-output blobs read by `git show`, and the auditor's `git()` calls
`proc.stdout.decode("utf-8", errors)` with `errors="strict"` by default
(`tools/report-landing-audit.py:108,123-126` at `245a37f6`); the grid pins
the refusal reason `output is not UTF-8` for F02/F16
(`tests/report-audit/repo-state-grid.py:580,586`), with fixtures that commit a
non-UTF-8 report/errata blob (`:226-230`, `:398-402`). It is not accurate for
F01's frozen arm: the frozen auditor used `text=True` and caught only
`OSError` (`4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py:87-97`),
so F01's traceback mechanism is the TextIOWrapper default, not
`bytes.decode`. The current arm passes F01 by explicitly mapping errors with
`errors="surrogateescape"` (`tools/report-landing-audit.py:180-184`; grid
F01 expects exit 0 at `:539`). S095's anchor explains why that mapping is
needed, but not the frozen text-mode failure the Gate attributes to it.

The lesson's rejected-candidate rationale (`round-23.md:53-56`: “S044/S064
already register the page; no new anchor needed”) conflates page registration
with anchor registration: S044 and S064 register the subprocess page for
`Popen.returncode` / `CompletedProcess.returncode` (`corpus/SOURCES.md:56,76`),
not for the text-mode paragraph. The text-mode claim has no anchor, and S095's
`teaches` smuggles it in. Under KQ22/KQ31 the cell cannot be edited in place;
a correction needs a superseding row (or a new row for the text-mode/io
anchors), not a prose-only disclosure.

## 4. Used-by paths

Both listed paths are real; neither is merely decorative:

- `corpus/lessons/round-23.md:49-51` cites S095 and its quote, and maps it to
  F01/F02/F16 (accuracy caveat above).
- `tools/report-landing-audit.py:108-126` relies on the default: the `git()`
  signature defaults `errors="strict"`, the docstring says “Strict by default:
  undecodable output is an EvalError, never a traceback verdict”, and the call
  is `proc.stdout.decode("utf-8", errors)` with `except UnicodeDecodeError`.
  F02/F16 exercise exactly that path through `git show`
  (`tools/report-landing-audit.py:290-299,365-372`).
- Observation only, not a pin defect: the working tree currently has an
  uncommitted round-23 section in `corpus/knowledge/error-is-not-a-verdict.md`
  that cites `S095` (`git status` shows ` M`; `git show
  HEAD:corpus/knowledge/error-is-not-a-verdict.md` contains no `S095`). At
  `245a37f6` it is not a consumer, so the `used-by` cell is correct for the
  audited commit. If that addition lands, `used-by` must gain the path
  (a mutable cell).

## 5. What I did NOT verify

- Did not run `tests/report-audit/repo-state-grid.py` or
  `isolation-mutants.py`; F01/F02/F16 routes and the frozen-arm mechanism are
  read from the committed code at `245a37f6` and the frozen blob, not observed
  as grid exits. L1's 26/26, 8/8 and 0-traceback counts are taken as reported,
  not re-measured.
- Did not fetch the 3.14.8 docs render; only the 3.14.9 render was fetched
  today. The text-mode behaviour probe ran on host Python 3.14.8.
- Did not fetch `io`/`locale` docs to anchor the TextIOWrapper strict default,
  or the codecs “Error Handlers” section; those are the missing authorities for
  the row's second clause.
- Did not verify long-term stability of the `/library/` 301 or the floating
  3.14 page; this is a single 2026-10-21 fetch.
- Did not re-audit S089–S094 or the corpus census beyond the cross-references
  named above.

## Files written

- `.ufo/waves/round-23/falsify/advice/SrcS095.md` (this report)

No clone edits, no tracked lane files, no commits, no installs or upgrades.

## Correction appended by the same seat (append-only)

Section 3's sentence “every `UnicodeError` occurrence is the bytes/bytearray
decode paragraph above” is imprecise. The fetched page contains the same
sentence twice: once in the `str.encode` paragraph (“errors controls how
encoding errors are handled …”) and once in the shared `bytes.decode` /
`bytearray.decode` paragraph (“errors controls how decoding errors are
handled …”). The row's anchor names the `bytes.decode` paragraph, where the
quote is exact; the `str.encode` duplicate is a different section and does not
change the finding.

What remains true and is the reject ground: the page's case-insensitive
counts are zero for `text mode`, `subprocess` and `TextIOWrapper`; neither
occurrence of the sentence documents text-mode subprocess decoding. The
verdict stands: reject the row as registered, narrow, because the immutable
`teaches` cell asserts the text-mode mechanism that its anchor does not
document. The quote, version claim and used-by reliance still hold.

## Transient fetch artifacts (not project files)

- `/tmp/s095.html` — fetched Python 3.14 stdtypes page used for the quote and
  absence counts.
- `/tmp/subp.html` — fetched Python 3.14 subprocess page used to check the
  text-mode sentence.

No tracked lane file, clone, index or config was written.

## Fix note (append-only clarification)

The verdict paragraph's “or a separate row” is not an alternative repair for
S095's own cell. A separate row anchoring the subprocess text-mode paragraph
(plus the io/TextIOWrapper strict default) would document the text-mode claim,
but S095's `teaches` would still be supported only by S095's `bytes.decode`
anchor. Because `scope`/`anchor`/`teaches` are immutable in place
(KQ22/KQ31), S095 needs a superseding row with a narrowed `teaches` (or a
`supersedes S095 —` replacement that cites both anchors); a new text-mode row
is needed only if the text-mode proposition is kept. The two fixes are not
interchangeable.
