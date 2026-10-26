# Seat N3Fleet — round-47 cross-lane v2 audit (fleet findings)

**Verdict: v2 fixes exactly the two v1 defects round 46 documented — 5 events regain 1–4 `--`-prefixed deleted lines (all 53 events now byte-exact to `git diff --numstat`), and 6 events' restoration status changes under the window-max measure (kotodama `c53782ab875e` SCORECARD/README flip to restored; chousa `c2a6e338bb29` and tameshi `b14ff1100f5b` overclaims corrected). Same 21 lanes, same 53 events, same five-file default; truncation class persists (30 unrestored).**

## What ran (read-only, v2 tool: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py`, schema `append-only-audit/v2`)

```
python3 .../tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/<lane>-shokunin \
  --to <full HEAD sha> --files SCORECARD.md,LOG.md,corpus/QUALITY.md,corpus/README.md,corpus/SOURCES.md --json
  # TMPDIR=/fast/scratch/hyaku/kama-r47/N3Fleet; per-lane exit codes captured at run time
```

21/21 lanes have all five files at tip; sibling HEAD shas are identical to the round-46 receipts' `to` (no lane moved), so all deltas are tool mechanics. Exit 0: audio, game-dev-2d, game-dev-3d, lore, mado, revenger, tsukuroi; exit 1: the other 14. Anchor: v2 on the shared clone at kama `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (contract, 85 files) reproduces the frozen C1 baseline exactly — 5 events, exit 1 (LOG 2292 restored; SCORECARD 2421/2420 partial; QUALITY 375 restored; README 663 restored; `dd9f5dc6` 31/24 partial).

## v2 differs from v1 in two places (full tabulation in `fleet.md`)

1. **`--` undercount (deleted counts)** — v1 dropped deleted lines whose content starts with `--` (rendered `---…`, mistaken for the `--- a/<file>` header). Affected events (v1 → v2 deleted): kama `0718b6ab` LOG 2290→2292, SCORECARD 2417→2421 (the four `--out .ufo/waves/round-20/21/22/runs/...` lines); kotoba `6d1fbffd8e57` 24→25, `57f9e38bfc37` 35→36 (`--self-test` lines); souji `a529c762c812` 85→86 (a lone `--` line). Showing command: `git diff --numstat --no-renames <c>^1 <c> -- <file>` — v2 `deleted` == numstat for all 53 events, 0 mismatches. Proposed fix (already in v2): exclude only the `--- a/` header.
2. **Window-max restoration (statuses)** — v1 measured set membership at tip; v2 maximises the held multiset over the event's window. Status flips: kotodama `c53782ab875e` SCORECARD partial(2)→restored(41/41) and README unrestored(0)→restored(20/20) (both repaired at `dee308944df6`, re-truncated at tip); kumitate `c86088720e23` unrestored→partial (1 re-added copy at `1a162a4dac`), `c91fe967ff63` 1→2; chousa `c2a6e338bb29` partial(1)→unrestored(0) and tameshi `b14ff1100f5b` partial(21)→partial(1) — v1 overclaimed on kept pre-existing copies; kama SCORECARD 2416→2420 and souji 71→72 track the corrected counts.

## Report-only observations (not fixed in place; counters frozen)

- Working-copy invisibility persists: 19 jj-colocated lanes are audited at git HEAD; unexported jj commits / working-copy truncations are invisible.
- No threshold-crossing detection changes: deltas are 1–4 lines; the smallest flagged events are ≥20 lines in both versions.

## Evidence

- `N3Fleet/fleet.md` — per-lane v2 table (21 lanes), full v1↔v2 diff tabulation, sample `--`-prefixed deleted lines, anchor reproduction.
- `N3Fleet/audit/<lane>.json` ×20 (v2 sibling receipts) + `N3Fleet/audit/kama-anchor-3a09a1d9.json` + `N3Fleet/audit/combined.json`.
- Round-46 v1 receipts consulted at `.ufo/waves/round-46/w1/out/N3Fleet/audit/<lane>-shokunin.json` (read-only).
- No tools installed (RULES.md read; python3 + git only). Lane and fleet repos read-only; the only writes are in this out directory.
