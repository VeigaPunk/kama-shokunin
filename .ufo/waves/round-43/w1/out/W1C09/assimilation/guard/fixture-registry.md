# Scratch guard fixture — NOT the lane registry

Purpose: prove the 0-3-space row pattern (`^ {0,3}\|[[:space:]]*S[0-9]{3,}`) catches an
indented registry row that the column-zero-only pattern (`^\|[[:space:]]*S[0-9]{3,}`) misses.
S330 is a real entry in `/fast/scratch/kama-r43/clone/.ufo/waves/round-42/assimilation/collisions`
(and in this round's `../collisions`), so it is a collided id; here it appears only indented.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S001 | column-zero control — https://example.invalid/control | docs | B | guard control | §1 | a column-zero row that both patterns must find | mined | 2026-10-19 | 90d | corpus/knowledge/control.md |
  | S330 | indented collision fixture — https://example.invalid/indented | docs | B | guard control | §1 | an indented row that only the 0-3-space pattern must find | mined | 2026-10-19 | 90d | corpus/knowledge/control.md |
