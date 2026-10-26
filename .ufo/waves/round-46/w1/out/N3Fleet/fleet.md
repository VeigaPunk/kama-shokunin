# Cross-lane append-only audit — round 46, seat N3Fleet

Verdict: **the kama round-45 truncation class recurs across 14 of 21 sibling lanes — 53 mass-deletion events (31 unrestored, 18 partial, 4 restored) — and a fleet-level default should watch all five append-only files, which exist in every lane; SCORECARD.md is the most-frequent target (33/53 events).**

## Method

For every sibling lane repo `/home/vgpnk/Projects/shokunin/*-shokunin` (21 lanes, all git repos, all with the five files at tip):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py \
  --repo /home/vgpnk/Projects/shokunin/<lane> --to HEAD --json \
  > .../w1/out/N3Fleet/audit/<lane>.json        # TMPDIR=/fast/scratch/hyaku/kama-r46/N3Fleet
```

- `--to HEAD` = `git -C <lane> rev-parse HEAD`, the tip of the checked-out branch (18 lanes are jj-colocated with detached HEAD at `@`; game-dev-3d-shokunin and lore-shokunin are on `main`). Read-only; no repo was written, fetched or mutated.
- Tool run: `append-only-audit.py` at kama commit `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` (landed, as the seat spec states, after the round-46 freeze; the audit tool is the C2 counter's instrument, run read-only).
- Receipts: `audit/<lane>.json` (full commit ids, events, summary) + `audit/<lane>.err` (empty for all 21 runs).
- Exit codes: 0 for lanes with no partial/unrestored event, 1 otherwise (tool `exit_code`).

**Reproduction check against the frozen C2 baseline** (kama at `0163fea2` reports 5 events; our run at current kama HEAD `96d329186e` reports the same 5 events, same files, same statuses):

| event commit | file | deleted | restored_at_tip | status | restored_by |
|---|---|---|---|---|---|
| `dd9f5dc6` | SCORECARD.md | 31 | 24 | partial | — |
| `0718b6ab` | SCORECARD.md | 2417 | 2416 | partial | — |
| `0718b6ab` | LOG.md | 2290 | 2290 | restored | `82b5e9d3` |
| `0718b6ab` | corpus/QUALITY.md | 375 | 375 | restored | `82b5e9d3` |
| `0718b6ab` | corpus/README.md | 663 | 663 | restored | `82b5e9d3` |

## Per-lane tabulation (audited at HEAD on 2026-10-26)

| lane | head (12) | commits | events | restored | partial | unrestored | files hit |
|---|---|---|---|---|---|---|---|
| audio-shokunin | 7a2fcd4f0883 | 276 | 0 | 0 | 0 | 0 | — |
| chousa-shokunin | 00f8c7f5272a | 333 | 2 | 0 | 2 | 0 | corpus/README.md:2 |
| game-dev-2d-shokunin | 7753d49b1667 | 290 | 0 | 0 | 0 | 0 | — |
| game-dev-3d-shokunin | 89dd182b7094 | 294 | 0 | 0 | 0 | 0 | — |
| kagi-shokunin | 69b61db46be4 | 108 | 2 | 0 | 1 | 1 | SCORECARD.md:1, corpus/README.md:1 |
| kaidoku-shokunin | c4895cf1f0fc | 383 | 1 | 0 | 1 | 0 | SCORECARD.md:1 |
| kake-shokunin | 044048597d62 | 341 | 3 | 0 | 0 | 3 | SCORECARD.md:2, corpus/QUALITY.md:1 |
| kama-shokunin | 96d329186e77 | 295 | 5 | 3 | 2 | 0 | LOG/SCORECARD/QUALITY/README |
| kasegi-shokunin | 57ea9ea5a3cb | 163 | 2 | 0 | 0 | 2 | SCORECARD.md:2 |
| kengaku-shokunin | d69452cfa4ea | 229 | 6 | 0 | 1 | 5 | SCORECARD.md:3, corpus/README.md:2, corpus/SOURCES.md:1 |
| kotoba-shokunin | 65a5c7a66324 | 401 | 7 | 0 | 2 | 5 | SCORECARD.md:7 |
| kotodama-shokunin | f556d1049fe6 | 373 | 8 | 1 | 3 | 4 | SCORECARD.md:4, corpus/README.md:1, corpus/SOURCES.md:3 |
| kumitate-shokunin | 8d557f85312d | 353 | 10 | 0 | 2 | 8 | SCORECARD.md:8, corpus/QUALITY.md:1, corpus/README.md:1 |
| lore-shokunin | 380ef3abc7c7 | 161 | 0 | 0 | 0 | 0 | — |
| mado-shokunin | 4d22eeb66c28 | 390 | 0 | 0 | 0 | 0 | — |
| mori-shokunin | aa3af1ec3118 | 482 | 2 | 0 | 1 | 1 | corpus/QUALITY.md:1, corpus/README.md:1 |
| revenger-shokunin | 6da884c6708f | 161 | 0 | 0 | 0 | 0 | — |
| souji-shokunin | 9c76c7222a8a | 269 | 2 | 0 | 1 | 1 | SCORECARD.md:2 |
| tabi-shokunin | 59f1b47aae27 | 223 | 2 | 0 | 1 | 1 | SCORECARD.md:1, corpus/SOURCES.md:1 |
| tameshi-shokunin | 8ca67421111f | 363 | 1 | 0 | 1 | 0 | LOG.md:1 |
| tsukuroi-shokunin | 87c4f7c627e3 | 303 | 0 | 0 | 0 | 0 | — |
| **TOTAL** | | | **53** | **4** | **18** | **31** | |

Clean lanes (exit 0): audio, game-dev-2d, game-dev-3d, lore, mado, revenger, tsukuroi.

## Does the truncation class recur?

Yes — and it is not ancient history; 14 of 53 events are dated 2026-10-21 or later. Full event list (date, lane, commit, file, deleted → restored, status, subject) is in the receipts; the class-defining cases:

- **Recurring per-round truncation, never restored** — kumitate: SCORECARD.md mass-deleted in at least 8 commits (rounds 9–17; 76, 61, 58, 56, 51, 44, 37, 24 lines), all `unrestored` at tip except two 1-line partials. This is the closest match to the kama round-45 pattern (a commit rewriting a whole section of the self-description and dropping the old text).
- **Largest single-file deletion beside kama's** — kaidoku `c265db9bd3c0` (round-1 reconcile): SCORECARD.md 112 lines deleted, 5 restored (partial).
- **README truncations at mint** — chousa `02a615a93a3c` and mori `27acf40c418b` (same timestamp, 2026-10-14 21:18): `corpus/README.md` 22 deleted → 8/9 restored; souji `a529c762c812` SCORECARD.md 85 → 71 restored (partial, 2026-10-25).
- **Still-moving targets** — kama `dd9f5dc6` (SCORECARD 31 → 24, 2026-10-25), kumitate `f874353902d0` (QUALITY 20 unrestored, 2026-10-25), tabi `38891ca0bd28` (SOURCES 23 unrestored, 2026-10-26), tameshi `b14ff1100f5b` (LOG 23 → 21, 2026-10-25), kotodama `cb2f8cafa76e` (SOURCES 63 unrestored, 2026-10-24).
- Only 4 of 53 events are fully restored at tip (kama LOG/QUALITY/README by `82b5e9d3`; kotodama SOURCES 48/48 by `d45985b2`). 31 events remain **completely unrestored** — the deleted text exists nowhere in the file at tip.

## Which files would a fleet-level default need?

All five append-only files exist in all 21 lanes at tip, so the fleet default can be the same set the kama counter uses:

`SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md`

Event frequency across the fleet argues for keeping all five — dropping any one loses events:

| file | events | share | largest single deletion |
|---|---|---|---|
| SCORECARD.md | 33 | 62% | 2417 (kama), 112 (kaidoku), 85 (souji) |
| corpus/README.md | 9 | 17% | 663 (kama, restored), 126 (kagi) |
| corpus/SOURCES.md | 5 | 9% | 63 (kotodama, unrestored) |
| corpus/QUALITY.md | 4 | 8% | 375 (kama, restored), 40 (kake, unrestored) |
| LOG.md | 2 | 4% | 2290 (kama, restored) |

If a fleet default wants a wider net, the other lane-governance docs are not universal (SHONEN.md/PROVINCE.md/SKILL.md exist in most lanes, MINT.md in ~half, README.md/AGENTS.md in most, REGIMEN.md/MANPAGE.md/EXAMPLE.kama.md in one each), so they belong in a per-lane extension list, not the default.

## Findings on the counter (report, never absorb)

1. **Counting edge case — `---`-prefixed deleted lines are dropped.** The tool's deletion filter is `x.startswith("-") and not x.startswith("---")`; this excludes the single diff header `--- a/<file>` but *also* any deleted line whose content itself starts with `--`. On kama `0718b6ab` SCORECARD.md this undercounts by 4 (git numstat `9 2421` vs counter `2417`; the four lines are `--out .ufo/waves/round-{20,21,22}/runs/...`). Small undercounts exist elsewhere (kake 24 vs numstat 25, kumitate 76 vs 77, tameshi 23 vs numstat 29-ish range). Near the 20-line threshold this can hide a real event (a 21-line deletion with ≥2 such lines reads as 19). Fix shape: exclude only the `--- a/` header, or count `-` lines from `--numstat`-style per-file hunks.
2. **Working-copy state is invisible.** In the 18 jj-colocated lanes the audit reads git history to HEAD; uncommitted truncations (jj working copy) are not seen.
3. All 21 lanes ran with the default five-file set; no lane needed a custom set (the tool tolerates absent files, but none were absent).

## Evidence

- `audit/<lane>.json` — full per-lane event JSONs (21 files), incl. `to`/threshold/files/commits/events/summary.
- Per-lane exit codes captured at run time: 0 for the seven clean lanes, 1 for the fourteen with events.
- Spot verification with the tool's exact diff flags (`git diff --no-renames --no-color --no-ext-diff -U0 <c>^1 <c> -- <file>`, count `-` lines excluding `---`): kake `ab87a485` SCORECARD 24 ✓, kumitate `ed991d07` SCORECARD 76 ✓, tameshi `b14ff110` LOG 23 ✓, kama `0718b6ab` SCORECARD 2417 ✓ (matches the JSON's `deleted`).
- Tool: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py` (docstring = C2 contract; read at `4a2a4d55`). No tools installed this round (RULES.md read; python3 + git only).
