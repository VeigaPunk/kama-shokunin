# EX02 — independent re-derivation of C2's population and row ancestry (executor)

Seat `EX02LatePopulation`. Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` read-only: no production
file edited, no commit made. Scratch `/fast/scratch/hyaku/kama-r82/EX02LatePopulation` deleted on exit.
No tools installed or upgraded (none needed).

Pin: audited tip `384ef1d5bcbf737183571398ecb0955ea5074609` (the audit's `to`; lane master at every
receipt run), base `aaf974dbd3b6adb2ef914dc7293cda92b4e05551`. Master advanced
`bacae072 -> 4beb4f2b -> 384ef1d5` while the seat ran (L1 record commits; after `bacae072` only
`SCORECARD.md` and `PROVINCE.md` bytes changed, `registry/` untouched). Receipts pinned at `384ef1d5`.

## Findings

1. **Enumeration (audit events with `undisclosed` lines, `status != restored`, commit ancestral to the
   base): 68 events / 492 undisclosed line entries** (68 `(commit,file)` pairs, 56 distinct commits;
   all `unrestored`; count column sums to 566). Largest events: `5785cdff`/`registry/append-only-accepted.tsv` 38,
   `9100605d`/`corpus/lessons/round-79.md` 16, `b5743975`/`SCORECARD.md` 12,
   `cf28c470`/`SCORECARD.md` 9, `4af44f78` (SCORECARD.md 6 + round-79.md 2).
2. **Register split at the tip** (`registry/append-only-late.tsv`: 88 data rows at base -> 103;
   `registry/append-only-late-r82.tsv` is byte-identical): the register carries **15 pairs / 14 commits
   / 103 line entries (count 103, all count=1)** — exactly the 103 undeclared lines outside the frozen register. All 103 rows
   are unique `(commit,file,hash)` triples matching an audit line (0 unmatched, 0 count/class
   mismatch). The other **53 pairs / 42 commits / 389 line entries (count 463)** are *not* carried, and all 389 are
   covered by `registry/append-only-accepted.tsv` (0 by disclosures, 0 uncovered, 0 overlap between
   the late and frozen pair sets). Population = 492 − 389 = **103**; no gap and no extra row.
3. **Population rows at the tip: 103 = 88 carried + 15 new, 0 removed.** The 88 carried rows are
   byte-identical to their base-revision bytes; the 15 new rows are `9+1+3+1+1` over the five round-81
   events `cf28c470`, `37484391`, `50c711ec`, `93cdfd60`, `017c34ca`; 9 carried events
   (`1cda0456` 4, `223c881a` 2, `28debbcf` 1, `4af44f78` 8, `5785cdff` 38, `5fcef757` 1,
   `9100605d` 16, `b5743975` 12, `f4a35f6c` 6).
4. **Row ancestry** (`git blame -l <tip> -- registry/append-only-late.tsv`): introducers are 88 rows
   `f6cb5303` (register first add) and 15 rows `b0064016` (round-82). **Strict-descendant violations
   = 0/103.** The register's first-add alone is **not** sufficient: it yields **15 violations**,
   exactly the five round-81 events above, because `f6cb5303` is their ancestor (it predates them).
   This independently confirms the disclosed round-82 row-level (blame) repair.
5. **Note / subject rule: 103/103 pass.** Each subject's `round-N` equals the row note's deletion
   round and the accepting round is greater. The 15 new rows read `round-82 accepts round-81 "…"` over
   subjects `round-81: …` (9+1+3+1+1 undeclared lines, all accepting 82 > deletion 81); the 88 carried
   rows read `round-81 accepts round-79|80 "…"`.
6. **Cross-check after the numbers were fixed** (the tools were not the source of the numbers):
   `python3 tools/round82-late-delta.py --repo <lane> --round 82` -> exit 0,
   `LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0`.
   `python3 tools/round81-append-debt.py --repo <lane> --round 82` -> exit 0,
   `APPEND_DEBT round=82 base=aaf974dbd3b6 events=68 accepted=53 late=15 pending=2 unaccepted=0
   bad_rows=0 bad_declarations=0 out_of_population=0`. Buckets reconcile: 53 frozen + 15 late = 68;
   `pending=2` is the round's own two post-base record commits (`4f156ecf`, `4beb4f2b`), by design.
   The frozen `round81-late-rows.py --check --round 82` -> exit 1, `missing=88 extra=88`: it
   regenerates the 88 carried notes at round 82 (keys equal, cells[:5] equal, 88 note-only diffs; the
   15 new rows byte-identical), a carried-bytes artifact of that generator, not a register defect.

## Receipts (absolute path — command — exit)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/EX02LatePopulation/receipts/audit.json`
  — `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --json` — exit 1
  (repo-wide audit verdict: 70 unrestored events; not the C2 claim).
- `.../receipts/blame.txt` — `git -C /home/vgpnk/Projects/shokunin/kama-shokunin blame -l 384ef1d5bcbf737183571398ecb0955ea5074609 -- registry/append-only-late.tsv` — exit 0.
- `.../receipts/first-add.txt` — `git -C ... log --diff-filter=A --format=%H 384ef1d5bcbf737183571398ecb0955ea5074609 -- registry/append-only-late.tsv` — exit 0.
- `.../receipts/row-ancestry.txt`, `.../receipts/ancestry-summary.txt` — blame + `merge-base --is-ancestor`
  per row (103 rows, 0 violations; first-add alone 15 violations).
- `.../receipts/delta.out` — `python3 .../tools/round82-late-delta.py --repo <lane> --round 82` — exit 0.
- `.../receipts/debt.out` — `python3 .../tools/round81-append-debt.py --repo <lane> --round 82` — exit 0.
- `.../receipts/generator-check.out` — `python3 .../tools/round81-late-rows.py --repo <lane> --round 82 --audit-json <pinned> --check` — exit 1 (see finding 6).
- `.../receipts/generated-late.tsv`, `.../receipts/generated-vs-committed.txt` — generator rows, exit 0.
- `.../receipts/tip.txt` — tip pins around every receipt run.

Seat artifacts: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/EX02LatePopulation/population.tsv`
(103 rows), `.../EX02.json`, `.../EX02.md` (33 lines), `.../receipts/`.

## Risks / notes

- The frozen generator's own `--check` mode is red at round 82 by construction (it regenerates carried
  notes at the new round). The round-82 delta checker is the compatible gate; a seat grading on the
  generator check alone would report a false red.
- The lane tip moves (L1 commits). All receipts are pinned at `384ef1d5`; the two `registry/` files
  did not change after `bacae072`, so later record commits do not move these numbers.
- No blockers; no production paths written; scratch tree deleted.
