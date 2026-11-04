# SCR02SourceRow — round 70 w1 findings (kama, advisory leaf)

Tip measured: `0e14facd0c619f45a6461821d2bd80ddac9855b1`. Lane untouched (read-only); all detail
files live in `.ufo/waves/round-70/w1/out/SCR02SourceRow/`. This trailer file is the only write
outside that directory, because the seat's `Report:` path names it.

## Headline finding — the pytest exit-codes URL is already registered as S052

`corpus/SOURCES.md` line 64 (exit 0):

```
| S052 | pytest exit codes — https://docs.pytest.org/en/stable/reference/exit-codes.html | docs | A | … "nothing was collected" distinct from "collected and failed" … | §Exit codes, entries "Exit code 1" and "Exit code 5" | Exit 1 means tests were collected and run and some failed; exit 5 means no tests were collected: an empty observation has its own non-zero status, distinct from failure. | mined | 2026-10-20 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md |
```

S052 teaches the C2 rule already, but carries no retained bytes and no sha256.

## Two contract-legal landings (L1 decides)

- **Option B (recommended; matches the freeze's one-row frontier step):** new row **S542**, scope
  narrowed to the completeness rule, `used-by SCORECARD.md,corpus/lessons/round-70.md`. Bytes:
  `evidence/row-s542.txt`. Insert as new **line 294** of `corpus/SOURCES.md`, directly after the
  S541 row (line 293), inside `## Registry` (lines 9–297). Row count 281 → 282. Never at EOF (E12).
  Validator (fleet `scripts/sources-census.sh`, `--today 2026-11-03`): with the lesson present
  `file ok`, **exit 0**, one new `W04` (same URL as S052, different scope; `E04` does not fire,
  measured). Without the lesson: **exit 1**, single `E11 S542 missing used-by corpus/lessons/round-70.md`.
- **Option A (no new row):** extend only S052's `used-by` to `…, corpus/lessons/round-70.md`
  (precedent: round-14). Bytes: `evidence/row-s052-extended.txt`. Validator: `file ok`, exit 0,
  **no new warning** (W04 stays 104).

Do not land both.

## Source facts

- `curl -sSL --max-time 30` → HTTP 200, 25787 bytes, exit 0, fetched 2026-11-03T23:48:53Z.
- Retained: `source/pytest-exit-codes.html`, sha256
  `a403306a1d763fc8123749544905dd64e8e0cfa5ed46a416679001c3142e3977`. Stripped derivative
  `source/pytest-exit-codes.txt`, sha256 `61978456441037deafad7f99593e3f3cd3efa2036c8624eacce7139bb4c4b572`.
- `last-modified 2026-10-27T21:36:00Z`; `etag W/"dcccfb52d0fbf192adbde399f77ff99c"`; `cf-cache-status HIT`.
- Page states no pytest version → `recheck on-release` is a cadence, not a pin.

## Byte-exact quote (tag-stripped, ≤25 words)

"Exit code 5: No tests were collected" (7 words) and
"Exit code 0: All tests were collected and passed successfully" (10 words) — 17 words total;
anchor `#exit-codes`. Supplementary tier-A sentence in the same bytes:
"The exit codes being a part of the public API" (10 words).

`python3 verify-quote.py` prints three `MATCH` lines and exit 0; a tampered-bytes arm prints
`MISS` and exits 1.

## Not verified

- No landed state, no commit, no census against the real tip.
- E11 depends on `corpus/lessons/round-70.md` existing at the same tip.
- No pytest version is stated by the page; none was inferred.

Full command log with outputs and exit codes: `report.md`. Row + insertion proof: `sources-row.md`.
Lesson Gate row: `gate-block.md`. Validator receipts: `evidence/validate-*.out`.
