# W07SourcesRowDraft — S517 registry row (Python `sys.setprofile`)

Axes: operability (C1's profile hook needs a first-party source row) and calibration (a row that
claims only what the page says and that the validator can parse). Leaf seat, advisory; the lane tree
is read-only and I wrote nothing under `corpus/`.

## Status — S517 is already in the working tree, so my draft is a competing draft

Working-tree `corpus/SOURCES.md` carries S517 at line 270 (`git diff --stat` = +2) with the same URL;
my scratch copy was taken at base, so appending my draft inside the table now scores
`E03 S517 duplicate id` (`e03-dup.out`, exit 1). The row below is a cell-level replacement only.

Cell delta vs the row in the tree: anchor — tree `§sys.setprofile, Python 3.14 docs page last updated
2026-10-27 16:42 UTC, accessed 2026-10-27`, mine gives the `profilefunc` signature, the
`#sys.setprofile` fragment and no version claim (see finding); teaches — tree paraphrases, mine quotes
verbatim; scope — tree names "profile-hook event semantics", mine enumerates the five events and the
three non-claims; used-by — tree `tools/round58-battery-exec-check.py, corpus/lessons/round-58.md`
(that lesson exists, 5520 bytes, one `setprofile` mention, so E11 resolves), mine lists the checker;
source cell — cosmetic.

## Finding — the integrated anchor names the wrong Python version (attacks cell 6, hence C1's provenance)

`read https://docs.python.org/3/library/sys.html:16-40` returns `title: sys — System-specific
parameters and functions — Python 3.15.2 documentation`, and the same HTML embeds
`docs.python.org/3.15/_images/...`. The URL is the unpinned `/3/` build, so "Python 3.14 docs page" is
false at that address on 2026-10-27 and cannot carry a 2026-10-27 3.14 footer. The quote is verbatim at
`:1455-1520`, the footer at `:2015-2028`. Fix: drop the version label or write 3.15.2.

## Draft row (947 bytes, 12 pipes = 11 cells, NF 13)

| S517 | Python 3 `sys.setprofile` — https://docs.python.org/3/library/sys.html#sys.setprofile | docs | A | which events a Python profile hook receives at a call boundary: `'call'` on function or code-block entry, `'return'` on exit including an exception exit, and `'c_call'`, `'c_return'`, `'c_exception'` for C functions; not per-line tracing, not thread context switches, not proof that any checker ran | §`sys.setprofile(profilefunc)`, anchor `#sys.setprofile`; page footer "Last updated on Oct 27, 2026 (16:42 UTC)", read 2026-10-27 | "it isn't called for each executed line of code (only on call and return, but the return event is reported even when an exception has been set)" — a call-boundary hook sees entered and exited frames without line traffic, and an exception exit still reports a return; it records that a frame ran, never what the frame achieved. | mined | 2026-10-27 | on-release | tools/round58-battery-exec-check.py |

Recheck `on-release` is symbolic: `/3/` rolls per release, so the anchor's footer date is the drift witness (S044 precedent); `overdue` reports it as `cadence`, never overdue.

## Validation receipts (V = /home/vgpnk/Projects/shokunin/scripts/sources-census.sh, --today 2026-10-27)

Lane tree `<tree>/corpus/SOURCES.md` plus symlinks to the real tools, registry, tests,
corpus/knowledge, corpus/lessons, .ufo, SKILL.md, SCORECARD.md so E11 resolves on real files:

1. Row after base line 269: exit 0, `file ok`; delta vs the same tree without the row is only the
   echoed path. Zero S517 findings; 100 W04 + 1 W01 pre-existing.
2. `census`: rows 257→258, tier.A 243→244, status.mined 232→233; other buckets unchanged.
3. Plain blob copy: exit 1 with and without the row; delta is exactly `E11 S517 missing used-by
   tools/round58-battery-exec-check.py`. `--file` sets `dir=realpath(dirname(FILE)/..)`, so no
   used-by path of any base row resolves (561 findings, all E11/W04/W01). Check 1 is authoritative.
4. Row at EOF instead of inside `## Registry`: `E12 S517 row outside Registry section`, exit 1.
5. Literal pipe in the scope cell: `E01 S517 fields=12`, exit 1 — the rule is an NF!=13 error, and the
   draft has none.
6. `overdue`: exit 0, `cadence S517 recheck=on-release opened=2026-10-27`.
7. Current working tree through the same lane tree: exit 0, zero S517 findings (S518 now present; its
   W04 for ld.so.8 is pre-existing, not mine).

## Limits

`grep -c setprofile tools/round58-c1-counter.py` → 0: the counter never touches the hook, so the
checker is the only consumer and the tree's used-by is right only because `round-58.md` now exists.
The row cannot carry the C1 predicate — the page says nothing about `--counter` subprocesses. The 100
W04 and 1 W01 findings predate this row and are untouched. Receipts in `./W07SourcesRowDraft/`;
scratch removed; no tool installs.
