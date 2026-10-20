VERDICT: confirm — S052's code-5 quote is verbatim, exit 5 is a distinct non-zero empty-collection status versus exit 1 failure, the exit-codes page states no pytest release version, and the lane labels S052 precedent-only (its own 0/1/2 and 0/1/2/3 tables are not attributed to pytest). Four precision limits, no kill.

# ReopenS052 — pytest exit codes: S052, its Gate quote, and lane-number attribution

Target: lane master `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (`git rev-parse HEAD` → same; subject "round-18: retain measured arms and repair counter classification seams").
Work was read-only plus one network GET of the source page. No clone, tool execution, gate run, counter run or mutation was performed (none was named for this item). No tools installed or upgraded.

## 1. Source opened live; retained bytes unchanged

Command and result:

```
curl -sSL -o /tmp/pytest-exit.html -w 'final=%{url_effective} code=%{http_code} bytes=%{size_download}\n' \
  https://docs.pytest.org/en/stable/reference/exit-codes.html
final=https://docs.pytest.org/en/stable/reference/exit-codes.html code=200 bytes=25597
```

Hashes (byte-identical, so the 2026-10-20 opening and this 2026-10-20 reopening see the same document):

```
7a13d907eab973617f3390c39a39ac2887882859f4a11f0e1640e491ac353d4c  /tmp/pytest-exit.html
7a13d907eab973617f3390c39a39ac2887882859f4a11f0e1640e491ac353d4c  .ufo/waves/round-18/sources/raw/docs.pytest.org/en/stable/reference/exit-codes.html
25597 bytes
```

The retained copy is tracked (`git ls-files --error-unmatch …` exit 0) and was last touched by `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`. `pins.json` records HTTP 200, no redirects, `Last-Modified: Sat, 13 Jun 2026 18:57:02 GMT`, ETag `W/"9732fea5b3c240ae044028b7b55b2db1"`, sha256 `7a13d907…`, 25597 bytes for this URL. No drift between the recorded opening and this check.

## 2. Empty versus failed in the page (the precedent S052 claims)

The page's §Exit codes is a single `<section id="exit-codes"><h1>Exit codes</h1>` with a `<dl>` of seven entries. Preamble: "Running `pytest` can result in seven different exit codes:" (rendered markdown and HTML agree).

- Exit code 1: "Tests were collected and run but some of the tests failed"
- Exit code 5: "No tests were collected"
- Exit code 3: "Internal error happened while executing tests"
- Note: "If you would like to customize the exit code in some scenarios, specifically when no tests are collected, consider using the pytest-custom_exit_code plugin."

Programmatic checks over the retained HTML:

```
h.count('No tests were collected') == 1
h.count('Tests were collected and run but some of the tests failed') == 1
len('No tests were collected'.split()) == 4        # Gate quote <= 25 words
regex 'pytest[\s-]+[0-9][0-9.]*' over whole file  -> []
```

So the two facts the claim needs are exact: an empty collection has its own non-zero code (5), distinct from a failure code (1), and code 1 is scoped to runs that did collect and run tests. The plugin note makes code 5 a default convention, not an invariant; "convention precedent only" in the row is the correct strength, and the lane does not rely on the plugin path.

## 3. Page version: absent, but do not read "unknown" as undiscoverable

Version-string inventory of the whole file:

- No `pytest <version>` occurrence; no dotted version token anywhere in `<article>` (`version-like tokens in article: []`).
- Only version-bearing metadata: `<meta name="readthedocs-version-slug" content="stable" />` (a docs channel slug, not a release) and the head comment `Generated with Sphinx 9.1.0 and Furo 2025.12.19` (generator, not pytest).
- The content-negotiated markdown view returned by `read` likewise contains no version.

Therefore `corpus/lessons/round-18.md:48` "The page states no pytest release version" is literally true, and `corpus/SOURCES.md:64` "the `stable` alias, whose pytest version the page does not state" is true about the page.

Limit worth recording: the page references `_static/documentation_options.js` once; that asset says `VERSION: '9.1',` and `.ufo/waves/round-18/sources/pins.json` already records it (`pins.pytest_documentation_version`, `documents.pytest_exit_codes.identity.version == "pytest documentation 9.1"`). So the docs build's series (9.1) is recoverable from the page's own asset even though the page text does not state it. That is a docs-version series, not a pytest patch release; the delivered claim is page-scoped and survives. A future edit should say "not stated on the page; pins locate docs build 9.1", not imply the version is unknowable.

## 4. Lane numbering is not falsely attributed to pytest

Every delivered statement that mentions the precedent draws the boundary:

- `corpus/lessons/round-18.md:19`: "S052 is convention precedent only, never authority for lane numbering."
- `corpus/lessons/round-18.md:48`: decision column "admit S052 as precedent only"; "failure is separately code 1".
- `corpus/SOURCES.md:64`: scope "convention precedent only, not the lane's numbering"; teaches column maps only exit 1 and exit 5.
- `corpus/QUALITY.md:133` (KQ24): "The lane's numbers are its own contract, not pytest's: S052 supplies only the distinct-empty-outcome precedent."
- `corpus/knowledge/llamacpp-loading-lifecycle.md:244`: "S052 supports only keeping an empty observation distinct, not these lane numbers."
- `LOG.md:1061`: "S052 is convention only."

Repo-wide case-insensitive search for `follow(s|ing)? pytest|per pytest|pytest convention|pytest's exit` finds no delivered corpus/code claim; the only two hits are build advice: `ScoutPytestExitCodes.md:83` says the v3 codes are "justified on their own grounds, not as 'following pytest'", and `CritC1HiddenPass.md:33-35` quotes pytest's exit-1 scoping as support for the conventional shape. Neither attributes the lane's numbers to pytest. The lane does not depend on pytest: `pyproject.toml`, `setup.cfg`, `pytest.ini`, `tox.ini`, `conftest.py` are all absent, and `grep -rn "import pytest" tools tests .ufo/waves/round-18/{c1,c2}` returns nothing.

The lane's own tables are documented as lane-owned, and they differ from pytest's:

- `tools/kama-llamacpp-live.py:16-19`: `0` pass; `1` fail; `2` not-evaluated or setup-error.
- `tests/llamacpp-live/check-receipt.py:32-33`: `0` VALID; `1` INVALID; `2` unreadable/not JSON; `3` NOT-EVALUATED.
- pytest instead assigns 2 = user interrupt and 3 = internal error. The collision is explicitly disclaimed by KQ24 and the rows above; nothing in the delivered text borrows pytest's meaning.

## 5. Empty-versus-failed is actually implemented, with fail dominating null

- `tools/kama-llamacpp-live.py:873-885` `_outcome_exit`: setup-error → `('setup-error', 2)`; then **any `passed is False` → `('fail', 1)` before** any `None` → `('not-evaluated', 2)`; all True → `('pass', 0)`.
- `tests/llamacpp-live/check-receipt.py:1348-1366` re-derives the v3 outcome in the same dominance order (setup-error/internal first, then False, then None) and adds a `bad(...)` problem when the declared `outcome` disagrees. A receipt that declares `not-evaluated` while a check is `false` therefore becomes INVALID.
- `tests/llamacpp-live/check-receipt.py:2101-2111`: any problem → exit 1; only a problem-free v3 receipt with `outcome == "not-evaluated"` → exit 3; otherwise VALID exit 0.
- `tests/llamacpp-live/controls.py:41-46` classifies not-evaluated only when tool exit 2, gate exit 3, receipt outcome `not-evaluated`, `setup_error` null, **no false check**, and the null set exactly the contract's nullable check. So the counter does not treat every non-zero as one class, which is KQ24's reject clause.

The Gate table quote itself: `corpus/lessons/round-18.md:48` contains `"No tests were collected"` exactly once in the page and four words (≤25). "failure is separately code 1" matches the verbatim exit-1 entry. Quote accurate.

## 6. Findings (precision limits, not kills)

1. **Gate location label is one notch coarse.** `round-18.md:48` writes `§Exit code 5`; the page has no such section — only `<section id="exit-codes"><h1>Exit codes</h1>`, with `Exit code 5` as a `<dt>` entry. `SOURCES.md:64` labels it correctly ("§Exit codes, entries …"). If the lesson is edited for another reason, align the Gate cell to the row's wording. No semantic error.
2. **Version wording.** The page does not state a pytest release version (true), but the lane's own pins recover docs `VERSION: '9.1'` from the page's referenced `documentation_options.js`, so "version unknown" should be read as "not stated on the page", not "undiscoverable". No delivered sentence claims otherwise.
3. **`tool 2 = NOT-EVALUATED` is a one-way compression.** `round-18.md:14` and `knowledge/llamacpp-loading-lifecycle.md:241` pair "tool 2 / gate 3" with NOT-EVALUATED, but tool exit 2 also covers setup-error/internal faults (`tools/kama-llamacpp-live.py:19`, `_outcome_exit` lines 875-876). The receipt's `outcome` field and gate exit 3 disambiguate, and `controls.py:42` requires `setup_error` null for the not-evaluated bucket. The separation from failure (1) remains exact. This is internal precision, not a pytest attribution.
4. **Adjacent boundary for C1 owners (outside this item's conclusion).** Both derivations check setup-error/internal before `False` (`tools/kama-llamacpp-live.py:875-880`; `check-receipt.py:1358-1361`). A false check concurrent with an internal fault is therefore reported as `setup-error`, exit 2, not `fail`, exit 1. KQ24's dominance sentence is about a missing observation (null), not a setup-error, so this does not falsify KQ24 as written; it is a wording boundary worth stating if anyone claims "fail always dominates" without the null qualifier.

## 7. Limits, cleanup, residual unknowns

- No runtime/gate/counter experiment was assigned or run; all conclusions are from the live document, byte-identical retained bytes, and committed code. Targeted mutation is n/a for this item.
- No clone was created; `/tmp/pytest-exit.html` was the only scratch file and is removed. No listener was opened; ports 8080/34113 and all registered consumer ports were untouched. No installs.
- Residual unknowns: the exact pytest patch release behind docs series 9.1 (page and asset state only the series; irrelevant to the claim); whether `/en/stable/` bytes change later (pinned hash + `on-release` recheck cover it); the Scout's `pytest 9.1.1` changelog statement was not reopened by me and is not needed here.

Artifact: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/falsify/advice/ReopenS052.md`.
