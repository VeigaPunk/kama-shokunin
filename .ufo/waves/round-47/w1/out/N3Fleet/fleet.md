# Seat N3Fleet — cross-lane append-only audit, v2 vs v1 (round 47)

**Verdict: v2 (`append-only-audit/v2`) reproduces the round-46 event map on the same 21 lanes — same 53 events, same commits and files — while correcting both documented v1 defects: the `--` undercount (5 events gain 1–4 deleted lines each; every v2 `deleted` is now byte-exact equal to `git diff --numstat`, 53/53) and restoration measured as the window-max multiset (status flips on 6 events; all flips move ground-truth-ward). The five-file fleet default still covers every event.**

## What ran

For each sibling lane (all 21 lanes are git repos; all have the five files at tip — checked with `git ls-tree -r --name-only HEAD`):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py \
  --repo /home/vgpnk/Projects/shokunin/<lane>-shokunin --to <full HEAD sha> \
  --files SCORECARD.md,LOG.md,corpus/QUALITY.md,corpus/README.md,corpus/SOURCES.md --json
  # TMPDIR=/fast/scratch/hyaku/kama-r47/N3Fleet; outputs -> audit/<lane>.json
```

`--to` = `git -C <lane> rev-parse HEAD` (full sha). For every sibling lane this equals the round-46 receipt's `to` exactly — the lane heads have not moved since round 46 — so every v1↔v2 delta below is pure tool mechanics on identical repository state. Exit codes unchanged: 0 for audio, game-dev-2d, game-dev-3d, lore, mado, revenger, tsukuroi; 1 for the other 14.

### Anchor reproducibility (kama, contract mode, frozen C1 baseline)

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
python3 .../tools/append-only-audit.py --repo $S/lane --to 3a09a1d93dcc16799cf6c4b48786e6440af134c4 --json
```

Exit 1; 85 files (contract `registry/append-only-contract.tsv` at that commit); 5 events — exactly the frozen C1 baseline: `dd9f5dc6` SCORECARD.md 31/24 partial; `0718b6ab` LOG.md 2292 restored (by `82b5e9d3`), SCORECARD.md 2421/2420 partial, corpus/QUALITY.md 375 restored, corpus/README.md 663 restored.

## Tabulation: where v2 differs from v1

### (a) `--` undercount — deleted-line counts

v1 filtered deleted lines with `startswith("-") and not startswith("---")`, which dropped any deleted line whose content starts with `--` (rendered `---…` in the diff, mistaken for the `--- a/<file>` header). Every v1→v2 gap equals the count of rendered `---`-prefixed deleted lines in that diff (column `'---'-pfx`).

| lane | commit | file | v1 deleted | v2 deleted | Δ | '---'-pfx | example deleted lines |
|---|---|---|---|---|---|---|---|
| kama | `0718b6abbda6` | LOG.md | 2290 | 2292 | +2 | 2 | `--tip <full-commit>` reads `listed 3 observed 6 missing 3 unsubstantia`; `--rev <full-commit>` reads `registered 10 unregistered 2 defective 0` ` |
| kama | `0718b6abbda6` | SCORECARD.md | 2417 | 2421 | +4 | 4 | `--out .ufo/waves/round-20/runs/0957ce61` ran **21 commands**, all decl`; `--out .ufo/waves/round-20/runs/9add96e4` records measured commit`; `--out .ufo/waves/round-21/runs/b76727f3` on measured commit`; `--out .ufo/waves/round-22/runs/6433390a` measured committed branch tip` |
| kotoba | `6d1fbffd8e57` | SCORECARD.md | 24 | 25 | +1 | 1 | `--self-test` T2/T3); the 40 `SKILL.md` checklist boxes remain lane-att` |
| kotoba | `57f9e38bfc37` | SCORECARD.md | 35 | 36 | +1 | 1 | `--self-test` T2/T3); **33 of the 41 `SKILL.md` checklist boxes remain` |
| souji | `a529c762c812` | SCORECARD.md | 85 | 86 | +1 | 1 | `---` |

Numstat equality: `git diff --numstat --no-renames <c>^1 <c> -- <file>` deletions == v2 `deleted` for all 53 events, 0 mismatches (the round-47 C1 contract's byte-exact criterion).

### (b) Restoration — window-max multiset vs tip-set membership

v1 measured how many deleted lines' texts exist at the audited tip (set membership); v2 maximises `held(x)` over the event's window. Differences (7 events besides the count fixes above):

| lane | commit | file | v1 (del / rest_tip / status) | v2 (del / rest_max / status) | best / by |
|---|---|---|---|---|---|
| chousa | `c2a6e338bb29` | corpus/README.md | 25 / 1 / partial | 25 / 0 / unrestored | `—` / `—` |
| kama | `0718b6abbda6` | LOG.md | 2290 / 2290 / restored | 2292 / 2292 / restored | `82b5e9d33a19` / `82b5e9d33a19` |
| kama | `0718b6abbda6` | SCORECARD.md | 2417 / 2416 / partial | 2421 / 2420 / partial | `82b5e9d33a19` / `—` |
| kotodama | `c53782ab875e` | SCORECARD.md | 41 / 2 / partial | 41 / 41 / restored | `dee308944df6` / `dee308944df6` |
| kotodama | `c53782ab875e` | corpus/README.md | 20 / 0 / unrestored | 20 / 20 / restored | `dee308944df6` / `dee308944df6` |
| kumitate | `c91fe967ff63` | SCORECARD.md | 51 / 1 / partial | 51 / 2 / partial | `23452e7abb42` / `—` |
| kumitate | `c86088720e23` | SCORECARD.md | 58 / 0 / unrestored | 58 / 1 / partial | `1a162a4dac6e` / `—` |
| souji | `a529c762c812` | SCORECARD.md | 85 / 71 / partial | 86 / 72 / partial | `07f83e69979b` / `—` |
| tameshi | `b14ff1100f5b` | LOG.md | 23 / 21 / partial | 23 / 1 / partial | `5f739acf21e8` / `—` |

Direction of every flip (v2 is more accurate):

- **kotodama `c53782ab875e`**: SCORECARD.md 41/41 restored (v1 saw 2) and corpus/README.md 20/20 restored (v1 saw 0) — both fully restored at `dee308944df6`, then re-truncated before tip; window-max sees the repair, tip-membership hid it.
- **kumitate `c86088720e23`**: unrestored → partial (one re-added copy at `1a162a4dac`, cut again at tip). `c91fe967ff63`: 1 → 2 held (best `23452e7abb`).
- **chousa `c2a6e338bb29`** and **tameshi `b14ff1100f5b`**: partial → unrestored / 21 → 1. The surviving line texts existed at tip but pre-existed the event (kept copies, never re-added); multiset cap correctly excludes them. These are overclaim corrections, not undercounts.
- **kama `0718b6ab` SCORECARD.md** and **souji `a529c762c812`**: restored_max keeps pace with the corrected deleted counts (2416→2420 of 2421; 71→72 of 86).

## Per-lane table (v2, 21 lanes, audited at HEAD on 2026-10-26)

| lane | head (12) | commits | events | restored | partial | unrestored | files hit |
|---|---|---|---|---|---|---|---|
| audio-shokunin | 7a2fcd4f0883 | 276 | 0 | 0 | 0 | 0 | — |
| chousa-shokunin | 00f8c7f5272a | 333 | 2 | 0 | 1 | 1 | corpus/README.md:2 |
| game-dev-2d-shokunin | 7753d49b1667 | 290 | 0 | 0 | 0 | 0 | — |
| game-dev-3d-shokunin | 89dd182b7094 | 294 | 0 | 0 | 0 | 0 | — |
| kagi-shokunin | 69b61db46be4 | 108 | 2 | 0 | 1 | 1 | SCORECARD.md:1, corpus/README.md:1 |
| kaidoku-shokunin | e1c83313f33a | 394 | 1 | 0 | 1 | 0 | SCORECARD.md:1 |
| kake-shokunin | 044048597d62 | 341 | 3 | 0 | 0 | 3 | SCORECARD.md:2, corpus/QUALITY.md:1 |
| kama-shokunin | 46a924e027f0 | 304 | 5 | 3 | 2 | 0 | LOG.md:1, SCORECARD.md:2, corpus/QUALITY.md:1, corpus/README.md:1 |
| kasegi-shokunin | 5e985b74075d | 172 | 2 | 0 | 0 | 2 | SCORECARD.md:2 |
| kengaku-shokunin | f9bbee69b711 | 237 | 6 | 0 | 1 | 5 | SCORECARD.md:3, corpus/README.md:2, corpus/SOURCES.md:1 |
| kotoba-shokunin | 65a5c7a66324 | 401 | 7 | 0 | 2 | 5 | SCORECARD.md:7 |
| kotodama-shokunin | f556d1049fe6 | 373 | 8 | 3 | 2 | 3 | SCORECARD.md:4, corpus/README.md:1, corpus/SOURCES.md:3 |
| kumitate-shokunin | 8d557f85312d | 353 | 10 | 0 | 3 | 7 | SCORECARD.md:8, corpus/QUALITY.md:1, corpus/README.md:1 |
| lore-shokunin | 380ef3abc7c7 | 161 | 0 | 0 | 0 | 0 | — |
| mado-shokunin | edc147898e9d | 399 | 0 | 0 | 0 | 0 | — |
| mori-shokunin | aa3af1ec3118 | 482 | 2 | 0 | 1 | 1 | corpus/QUALITY.md:1, corpus/README.md:1 |
| revenger-shokunin | 6da884c6708f | 161 | 0 | 0 | 0 | 0 | — |
| souji-shokunin | 9c76c7222a8a | 269 | 2 | 0 | 1 | 1 | SCORECARD.md:2 |
| tabi-shokunin | a4bfef0f7502 | 228 | 2 | 0 | 1 | 1 | SCORECARD.md:1, corpus/SOURCES.md:1 |
| tameshi-shokunin | 7d3d977f39ac | 375 | 1 | 0 | 1 | 0 | LOG.md:1 |
| tsukuroi-shokunin | 12421a73b281 | 308 | 0 | 0 | 0 | 0 | — |
| **TOTAL** | | | **53** | **6** | **17** | **30** | |

Round-46 v1 totals were 53 events, 4 restored, 18 partial, 31 unrestored; v2 moves +2 to restored (kotodama ×2) and +1 from partial to unrestored (chousa) and −1 unrestored→partial (kumitate c860887): **6 restored / 17 partial / 30 unrestored**.

## Findings (report, never absorb)

1. **v2 is the correct fleet instrument.** 53/53 events byte-exact to numstat; window-max restorations; no event is detected or missed at the threshold=20 boundary in this corpus (deltas 1–4; smallest flagged events are 20+ lines).
2. **The truncation class persists.** 30 of 53 events remain completely unrestored; class-defining cases unchanged under v2: kumitate SCORECARD.md mass-deleted in 8 commits (all unrestored), kaidoku `c265db9bd3c0` SCORECARD 112, souji `a529c762c812` 86→72, kama `0718b6ab` 2421→2420.
3. **Working-copy invisibility remains** (report-only): 19 jj-colocated lanes are audited at git HEAD; unexported jj commits and working-copy truncations are invisible to both v1 and v2. Same limitation as round 46.
4. The five-file fleet default (`SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md`) still covers every event in every lane; no lane needed a custom set.

## Evidence

- `audit/<lane>.json` ×20 — v2 runs (full commit ids, events, summary), one per sibling lane.
- `audit/kama-anchor-3a09a1d9.json` — contract-mode v2 run on the shared clone at the round-47 build commit.
- `audit/combined.json` — machine-readable per-lane table, v1↔v2 diff rows, undercount rows with sample lines.
- Commands, exit codes, and the numstat equality check (53/53) recorded above.
- No tools installed this round (RULES.md read; python3 + git only); lane and fleet repos untouched (read-only), besides the out directory.
