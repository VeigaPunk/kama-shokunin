# X10CensusStartEnd — census validate vs round-58 start snapshot

Leaf advisory seat. Registry not edited. Attacks: `census/start.{out,exit}` as an operability/calibration
anchor; not C1/C2 predicate text.

## Verdict: exact reproduction, exit 0, 102 rows — from the frozen registry blob
```
$ TMPDIR=/fast/scratch/hyaku/kama-r58/X10CensusStartEnd \
  /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
EXIT=0   stdout=102 lines   stderr=0 bytes
sha256(now.out)=bece1e9e7f4f3dbaaeedb6ead7dab7fa0ead8105dcf1254074a86f428d3c04a9 = sha256(start.out); cmp identical
```
`start.exit` = `0` → matches live exit. Rows, all `lane=kama`: **100×W04** cross-scope duplicate URL,
**1×W01** (S481 tier C mined, 6 used-by paths), **1×`kama ok <abs>/corpus/SOURCES.md`** trailer.
No E-codes ⇒ exit 0 by contract.

## Independent count (own parse, not the checker's totals)
`rows=257  distinct_ids=257  rows_NF_ne_13=0  max_opened=2026-10-27` (ids S001..S516, sparse).
243 rows carry a URL, 14 do not, 139 distinct, 104 repeats ⇒ 100 cross-scope (equals emitted W04) +
4 same-scope exempt by `supersedes S###` (S099,S138,S139,S474) ⇒ 0 E04. Self-consistent.

## Frozen-blob replay (isolates tree drift)
`git show dcd69473:corpus/SOURCES.md` (sha256 2363f5d4…) into a scratch lane with symlinked siblings →
`validate --today 2026-10-27 <scratch>/kama`: **exit 0, 102 lines, first 101 lines byte-identical** to the
snapshot; only the trailer path differs (it echoes the given dir).

## Live-tree drift inside this seat's window (`drift.txt`)
16:53 reg 257 rows/2363f5d4… → 102 lines exit 0 == start.out · 16:54:45 reg 259 rows/2d42728d…
(+S517 sys.setprofile, +S518 ld.so) → **104 lines exit 1**, two E11 for missing `corpus/lessons/round-58.md`
· 16:55 that file appears → E11 clears · 16:56 **103 lines exit 0**, diff vs snapshot exactly one added line:
`kama W04 S518 duplicate url man7.org/linux/man-pages/man8/ld.so.8.html across scopes` (S518 declares
`supersedes S513`; W04 keys on URL+scope only). Snapshot is stale by one W04 line vs the live tree — content,
not counter drift.

## Reproduction limits (report-only; no predicate change proposed)
1. **Date window, one-sided.** Frozen blob identical only for `--today` ≥ 2026-10-27 (= `max_opened`):
   10-27/10-28/11-30 → 102 lines exit 0; 2026-10-26 → 122 lines, 21×E08, exit 1; 2026-10-19 → 328 lines,
   227×E08, exit 1. `start.exit=0` encodes a lower date bound, so an earlier replay reddens on E08 alone.
2. **`--root` form is observable.** `--root .` puts `./kama-shokunin/corpus/SOURCES.md` in the trailer
   (else identical, exit 0); byte identity needs the absolute-root form the seat names.
3. **Ordering is registry file order.** Two id inversions (S352 after S363 line 223; S473 after S474 line 227)
   emit nothing today, so byte identity hides them; a future table reorder would move snapshot bytes with
   zero change in findings.

## Invariance, script health, tools
All exit 0 and byte-identical to `now.out`: TZ=America/Sao_Paulo, TZ=Pacific/Kiritimati (script uses
`date -u`), LC_ALL=C, rerun, cwd=`/` with absolute root. `sha256(scripts/sources-census.sh)=3fb72615…a64e30`,
mtime 2026-10-19 21:22 (pre-freeze). Supplementary `… selftest` → exit 0, **96 killed / 0 SURVIVED**,
"selftest ok", gawk 5.4.1 — the match is not a stale-binary artifact. Tools installed: none (pacman untouched).

## Risks
- `start.out` is replay-dated, not date-pinned: a later gate re-run changes bytes for reasons unrelated to
  drift, and already differs by one W04 line at the current live registry rev.
- S517/S518 drift is reported here for the L1 (this report is the channel); no registry edit made. Blockers: none.

## Receipts (`…/w1/out/X10CensusStartEnd/`)
`now.out` (== snapshot), `now2.out`, `now.err` (empty), `tz.out`, `lc.out`, `relroot.out`, `today-1019.out`,
`today-2027.out`, `d-2026-10-26.out`, `d-2026-11-30.out`, `frozen.out`, `live-late.out`, `live-final.out`,
`date-probes.txt`, `drift.txt`, `selftest.out`; scratch `/fast/scratch/hyaku/kama-r58/X10CensusStartEnd` removed.
