# Seat N3Fleet — cross-lane append-only audit findings (round 46)

**Verdict: the kama round-45 truncation class recurs across 14/21 sibling lanes (53 mass-deletion events: 31 unrestored, 18 partial, 4 restored at tip); a fleet-level default should keep all five append-only files (present in all 21 lanes), with SCORECARD.md the most-frequent target.**

Full deliverable: `.ufo/waves/round-46/w1/out/N3Fleet/fleet.md` (per-lane table, full event list, recommendations).

## What ran (read-only, HEAD tips)

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py \
  --repo /home/vgpnk/Projects/shokunin/<lane> --to HEAD --json \
  > .ufo/waves/round-46/w1/out/N3Fleet/audit/<lane>.json   # TMPDIR=/fast/scratch/hyaku/kama-r46/N3Fleet
```

21/21 lanes are git repos with all five files at tip. Exit codes: 0 for audio, game-dev-2d, game-dev-3d, lore, mado, revenger, tsukuroi; 1 for the other 14.

Reproduction check: kama at HEAD `96d329186e` reports exactly the frozen C2 baseline events (5 events; `0718b6ab` LOG/QUALITY/README restored by `82b5e9d3`; SCORECARD 2417→2416 partial; `dd9f5dc6` SCORECARD 31→24 partial).

## Findings

1. **Truncation class recurs.** Per-round self-description truncations that are never fully restored are common: kumitate truncated SCORECARD.md in 8 commits (76/61/58/56/51/44/37/24 lines; all unrestored at tip), kaidoku lost 112 lines (5 restored), souji 85→71. 31/53 events are completely unrestored; only 4/53 fully restored. 14 events are from 2026-10-21 or later — the class is active, not historical.
2. **Fleet-level default files:** exactly the five kama files — `SCORECARD.md`, `LOG.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md` — all present in every lane. Event share: SCORECARD 33, corpus/README.md 9, corpus/SOURCES.md 5, corpus/QUALITY.md 4, LOG.md 2 (largest single deletion: LOG.md 2290). Other governance docs (SHONEN/PROVINCE/SKILL/MINT) are per-lane extensions, not universal.
3. **Counter defect (report only, not fixed):** the deletion filter `startswith("-") and not startswith("---")` also drops deleted lines whose content begins with `--` (e.g. kama `0718b6ab` SCORECARD has four `--out .ufo/...` lines; numstat 2421 vs counted 2417). Near the 20-line threshold this can hide a real mass deletion. Fix shape: exclude only the `--- a/` header.

## Evidence

- `audit/<lane>.json` (21 receipts; full commit ids + events + summary).
- Exact-flag spot verification matches each JSON's `deleted`: kake `ab87a485` 24, kumitate `ed991d07` 76, tameshi `b14ff110` 23, kama `0718b6ab` 2417.
- Command used for receipt generation (above) and per-lane exit codes recorded at run time.

Written:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/N3Fleet/fleet.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/N3Fleet.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/N3Fleet/audit/<lane>.json` ×21
