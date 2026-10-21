VERDICT: partial - the S057 row is grounded in the opened ld.so(8) page and its DT_RUNPATH quote is verbatim, but the lane's existing word counts are wrong and the requested column shape is not the contract's.

# DraftS057 — S057 SOURCES row from ld.so(8)

## What was executed (all in /tmp/kama-r19-DraftS057; lane not modified)
- `curl -sS -o out/ld.so.8.html https://man7.org/linux/man-pages/man8/ld.so.8.html` → exit 0, HTTP 200, 41398 bytes, sha256 `d9b7737e6c9a38f6c7ce11a4feec834704d6ad5139dc790afa9798faf0379f83`.
- HTML→text extraction (python3, `out/ld.so.8.txt`) and exact substring counts → exit 0.
- `python3 tools/sources-append-only.py --selftest` → exit 0, `42/42 selftest cases passed`.
- `git show HEAD:corpus/SOURCES.md` → exit 0, 56 rows (`out/SOURCES.HEAD.md`).
- Candidate `out/SOURCES.candidate.md` (lane working-tree SOURCES.md with the S057 line replaced by `out/S057-row.md`); `parse_registry` on HEAD and candidate → 56 and 57 rows, header equals the contract's eleven columns; `diff_registries(HEAD, candidate)` → `violations=[]`, `added=['S057']`, exit 0.
- Receipt: `out/receipt.txt`. Page version: man-pages 6.19, page dated 2026-08-03, HTML rendered 2026-09-09.

## Verified quotes (on the opened page)
1. §DESCRIPTION, search step (3): "are searched only to find those objects required by DT_NEEDED" — verbatim, 1 hit, **10 words**. The same paragraph continues "(direct dependencies) entries and do not apply to those objects' children", which supports the scope note "direct dependencies only".
2. §Dynamic string tokens, $ORIGIN: "$ORIGIN (or equivalently ${ORIGIN}) This expands to the directory containing the program or shared object" — verbatim, 1 hit, **15 words**. The bare span "expands to the directory containing the program or shared object" is 10 words.

## Defects in the existing lane text (not edited; for the lane owner)
- `corpus/SOURCES.md:69` (S057 row) says quote 1 is "(11 words)"; it is 10.
- `corpus/SOURCES.md:69` says quote 2 is "(14 words)"; the verbatim span is 15 with the `$ORIGIN` token, 10 without it. Neither is 14.
- `corpus/lessons/round-19.md:28` repeats "(11 words)" for quote 1; `round-19.md:27` says "14 words located" for the $ORIGIN quote, and its ellipsis form "$ORIGIN ... expands ... object" is 11 words.
- `round-19.md:29`: "A tree digest authenticates execution — reject; same page: … identity is not authentication". The page says nothing about digests or authentication; that sentence is [INFERENCE], not sourced to S057.

## Column shape (conflict with the assignment)
The assignment lists `id, source, kind, tier, teaches, Gate, lesson, status, opened, recheck, used-by`. The frozen checker (`tools/sources-append-only.py` lines 59-62, guard at line 191) requires exactly `id, source, kind, tier, scope, anchor, teaches, status, opened, recheck, used-by`. A `Gate` or `lesson` header would fail the guard with exit 2. The draft therefore uses the contract's eleven columns: the Gate quotes sit in `teaches` (the convention of S044 and S035), section locations in `anchor`, and the lesson in `used-by`. [INFERENCE] the assignment's shape is a drafting label, not the frozen contract.

## Draft row (contract v1 shape; file `out/S057-row.md`)
```
| S057 | Linux ld.so(8) — https://man7.org/linux/man-pages/man8/ld.so.8.html | docs | A | how the loader searches DT_RUNPATH and expands $ORIGIN for direct dependencies of an install tree; grounds the install-tree identity boundary, not a claim that any digest authenticates execution | §DESCRIPTION search step (3) DT_RUNPATH; §Dynamic string tokens $ORIGIN; man-pages 6.19 (page dated 2026-08-03, HTML rendered 2026-09-09) | Step (3): "are searched only to find those objects required by DT_NEEDED" (10 words), with "(direct dependencies)" and "do not apply to those objects' children" in the same paragraph. $ORIGIN: "$ORIGIN (or equivalently ${ORIGIN}) This expands to the directory containing the program or shared object" (15 words). | mined | 2026-10-21 | on-release | corpus/lessons/round-19.md, registry/required-citations.json |
```

## Limits
- One fetch of the live page on 2026-10-21; the page is not pinned to a revision (man-pages is versioned by page date, not commit). Recheck cadence `on-release` is inherited from the lane's convention, not verified.
- Only the search-order and $ORIGIN sections were checked; no ld.so behavior was run. Claims about install-tree identity beyond the quotes are [INFERENCE].
- Not checked: whether `registry/required-citations.json` cites S057 by the same id (not inspected this seat).

## Install record
None. No tools installed or updated.
