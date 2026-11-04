# gate block — round 70 (SCR02SourceRow)

Lesson row for `corpus/lessons/round-70.md` §Gate. Same column shape as round-69's Gate table
(`| Row / candidate | Located quote (≤25 words) | Verdict |`). No cell contains a pipe.

## Table row (paste as the S542 row of §Gate)

```
| S542 `https://docs.pytest.org/en/stable/reference/exit-codes.html` | "Exit code 5: No tests were collected" and "Exit code 0: All tests were collected and passed successfully" (7 + 10 = 17 words; §Exit codes, anchor `#exit-codes`; verified verbatim in the retained fetched bytes sha256 `a403306a1d763fc8123749544905dd64e8e0cfa5ed46a416679001c3142e3977` at `.ufo/waves/round-70/w1/out/SCR02SourceRow/source/pytest-exit-codes.html`, accessed 2026-11-03) | admit — tier A: the pytest project's own reference page for a fixed, enumerated process interface, which the page itself calls public API ("They are represented by the pytest.ExitCode enum. The exit codes being a part of the public API", 17 words, same bytes); scope sentence: pytest's exit contract makes "nothing was collected" a nonzero status of its own (5) and reserves 0 for "all tests were collected and passed", so a runner that executed nothing cannot exit 0 — the outside rule C2's census verdict must obey when it derives its exit from the not-evaluated count; recheck on-release |
```

## If the L1 lands Option A instead (no new row)

Replace the id cell with `S052 (re-opened, used-by extended)`. The quote, retained path and
sha256 are identical — S052 cites the same URL — but S052's row has no sha256 of its own, so the
`anchor`/`teaches` cells of S052 stay untouched and the freshness evidence lives in this Gate
block and in `sources-row.md` §4.

## Evidence the row is byte-exact, not paraphrased

Raw HTML at the located section (Sphinx `field` list; the colon is a styled span):

```
Exit code 5<span class="colon">:</span></dt>
<dd class="field-even"><p>No tests were collected</p>
```

Extraction rule used (tags removed, whitespace collapsed), reproducible:

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-70/w1/out/SCR02SourceRow
$ python3 verify-quote.py; echo EXIT=$?
PATH /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-70/w1/out/SCR02SourceRow/source/pytest-exit-codes.html
SHA256 a403306a1d763fc8123749544905dd64e8e0cfa5ed46a416679001c3142e3977
MATCH 7 words: Exit code 5: No tests were collected
MATCH 10 words: Exit code 0: All tests were collected and passed successfully
MATCH 10 words: The exit codes being a part of the public API
EXIT=0
```

Negative arm (same script, tampered bytes, expected hash swapped so the quote matcher runs):
`MISS  7 words: Exit code 5: No tests were collected`, `MISS_ARM_EXIT 1`. A plain hash-mismatch
arm also exits 1 (`SHA256_MISMATCH`). Both arms were run this session; the quote matcher is not
vacuous.

## Access facts recorded with the row

- URL fetched `2026-11-03T23:48:53Z` (`curl -sSL --max-time 30`, HTTP 200, 25787 bytes, exit 0).
- `last-modified: Tue, 27 Oct 2026 21:36:00 GMT`; `etag: W/"dcccfb52d0fbf192adbde399f77ff99c"`;
  `x-amz-meta-mtime: 1793136756.032975742`; `cf-cache-status: HIT` — the served bytes may be a
  CDN copy of that 2026-10-27 build; the sha256 pins what was actually read.
- No pytest version string appears on the page (`grep -o -i 'pytest [0-9][^<]\{0,12\}'` → empty),
  so the row records `on-release` rather than a version pin.
