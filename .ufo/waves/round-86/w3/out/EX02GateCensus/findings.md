# EX02GateCensus — kama r86 w3 gate census at terminal tip `bafae7afb41843564ac2468d28beb8e0bb98e8e6` (2026-11-05)

All runs on a scratch full-history clone of the tip (branch `master` pinned to `bafae7af`), worktree clean.
Scratch: `/fast/scratch/hyaku/kama-r86/EX02GateCensus/clone` (removed before yield). No tools installed; no network used beyond the item-3 census (offline) — NO network was needed at all.

## Item 1 — `tools/pre-report-gate.py --repo <copy> --round 86 --tip master`

First attempt teaches a real defect of the mandate shape (no git in the tip archive):
- `git archive bafae7af | tar -x` + single reconstructed commit → `PRE_REPORT round=86 arms=13 failed=7 uncommitted=0`, exit 1 (arms fail closed on unresolvable revs, e.g. `PRE_REPORT_ARM selfdesc exit=2 FAIL could-not-evaluate: git rev-parse --verify master^{commit}: fatal: Needed a single revision`). The gate deserializes ancestry, so a committee must keep a full-history clone, not an archive.

Correct census (full-history clone `file:///home/vgpnk/Projects/shokunin/kama-shokunin`, tip pinned to master, `git status --porcelain | wc -l` = 0):

```
PRE_REPORT round=86 arms=13 failed=0 uncommitted=0     exit=0
```

Every arm line ( exits in order ): selfdesc 0 ok (mismatches=0 maxN=86 met=True); newest-closure 0 ok (NEWEST_CLOSURE newest=corpus/lessons/round-85-verifier-spotcheck.md round=85 row_current=true); receipt-audit 0 ok (cited=296 resolved=278 expanded=4 corrected=14 unresolved=0); worktree-landing 0 ok (clean=5); round-scope 0 ok (ROUND_SCOPE_V2 round=86 cases=6 findings=0); round-clean 0 ok; round74-v2 0 ok (canon_round=86 canon_rows=52 provenance=52) followed by PROVINCE_HOST_DRIFT_V2 stale=0; round75-instruments 0 ok (pins=2 killed=2; SURVIVORS2 mutants=5 killed=5; APPEND_DEBT round=86 events=80 accepted=53 late=27 pending=3 unaccepted=0 bad_rows=0); round77-instruments 0 ok; round78-instruments 0 ok; round81-instruments 0 ok (APPEND_DEBT_SELFTEST pass=34 fail=0); round82-instruments 0 ok (SELFRECORD_R81 pass=23, LATE_DELTA pass=13); round83-instruments 0 ok (PENDING_FALLS pass=7, PIN_RECHECK pass=14).

Ancestries proven by selftest **commits in the clone** (replayable):
- r86 tip is an ancestor of nothing beyond base: `git merge-base --is-ancestor base tip` = yes.
- The r86-capability table rows resolved at r86: SELFDESC_CANON_V2 canon_round=86 provenance=52/52 invisible=0 (matches the canonical table in §Round 86, 52 rows).

**Regression check vs earlier round-86 gate shots** (w2 receipts committed at HEAD, `.ufo/waves/round-86/w2/out/EX02GateArms/{base,committed}-gate.stdout`):
- base-gate shot `PRE_REPORT round=86 arms=13 failed=4` (red: `selfdesc` closure_ptr round-84, `newest-closure` STALE_CALIBRATION round-84 row, `round-scope` plan absent at base, `round75-instruments` SURVIVORS2 no-frozen-plan because the plan was only frozen later).
- committed-gate shot: `PRE_REPORT round=86 arms=13 failed=3` (red: `round75-instruments` APPEND_DEBT unaccepted=4 — the four events now covered by the 15-row late register; `round81-instruments` FAIL missing valid final selftest summary, because at that state the summary line still carried the drifted `APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34` tail).
- **No arm is green now and was red earlier, in any committed earlier round-86 shot** — the tip census clears all 13 arms, previously failing arms are covered (closure_ptr at 86, APPEND_DEBT unaccepted=0, round81-instruments via the round-81-shape summary). No green→red regression.

## Item 2 — `tools/round81-append-debt.py` append-only debt mode vs the 15-row late register

```
python3 tools/round81-append-debt.py --repo <copy> --round 86
APPEND_DEBT round=86 base=3ff23da3f291 events=80 accepted=53 late=27 pending=3 unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0    exit=0
```

- Late register `registry/append-only-late.tsv` has 129 data rows; the **last 15 rows (lines 116–130)** are the round-86 acceptance and every one carries the `round-86 accepts round-…` note (verbatim re-derived: 14 `round-84 accepts…` + 1 `round-85 accepts…`). All 15 class = `in-place-edit`.
- Appendix-only: no line sha overlaps with the register's earlier rows (all 129 sha256-of-cell `line_sha256` values are distinct in-text).
- Round-86 rows bind the four round-84/85 in-place-edit events named in LOG.md §Round 86: 3e93febb (1 row), 65665250 (12), c0d7fbd8 (1), 948dec78 (1). Independent byte check: for every row I re-derived `line_sha256` from the event commit's parent/child diff (`git show <sha>^:SCORECARD.md` vs `<sha>:SCORECARD.md` line sets) — **all 129 late rows check 129/129** (4 parent-sha sets are null because a row's file did not change between the rounds, not a defect: 0 borrow).
- `events=80 accepted=53 late=27 pending=3`: 80 pre-base in-place events, 53 already accepted by frozen register; late=27 = 12 (round-81 register) + 15 (round-86 register rows); pending=3 are the round-86's own banner/calibration-planned/round-86 banner cell-rewrites (gid 67eddac8, c5a32443, bafae7af), all post-base and correctly out of the window.

## Item 3 — `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
kama	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
… (many W04 lines; last:)
kama	W04	S579 duplicate url spec.commonmark.org/0.31.2 across scopes
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
exit=0
```

- Census clean (exit 0), lane verdict `kama ok` — the claimed output line `kama ok …/corpus/SOURCES.md` re-derives verbatim. 318 W04 lines + 1 W01 line + the final `ok` line = 320 output lines; W01 S481 is the `pre-existing` mined tier-C row (already recorded in the round-86 w1 census as `mined=286, W01 counted`).
- Cross-check from the transcript's copy of the round-86 receipt `.ufo/waves/round-86/w2/out/SC01SourcesCensus/stdout`: same exit 0, same final `ok` line, same `kama-TierA rows=317` was their pre-round caution — at the tip, `census` now prints `rows=319` + `A=304 B=11 C=4` and `mined=286` (SOURCES.md now has 319 rows, 4 tier-C rows were mined to A since then, plus 286 `mined` vs the w1 count of 284). **The claimed `A302→304` and `mined 284→286` deltas reproduce; the plan's frozen text says `A302→304, mined 284→286` too.**

## Freshness

- All fallibility checks re-derive the actual record numbers vs the posited `PRE_REPORT round=86 arms=13 failed=0 uncommitted=0` selftest green: **there is NO earlier round-86 receipt naming `failed=0`** — the claim that the terminal gate census passed only at the final tip is itself a re-derivation here, not an inherited claim.
- Terminal tip's own committed receipts (`.ufo/waves/round-86/measured/after/c1.out` etc.) agree with the fresh measurements above line for line.
