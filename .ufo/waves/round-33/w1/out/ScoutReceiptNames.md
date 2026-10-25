# ScoutReceiptNames — round-33 w1 (build + falsify)

**Target:** map each round-32 `*-v2.out` filename in
`.ufo/waves/round-32/c2/controls/` to its actual bytes and intended fixture.
Read-only scout; no files modified.

## Method

- Read every file in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-32/c2/controls/` (13 files) plus the siblings `before-base.out`, `gate-tip.out`, `gate-data-tip.out`, `selftest-*.out`, `SUMMARY.md`, and `.ufo/waves/round-32/preregistration.json`.
- `sha256sum`/`wc -c` over all `*-v2.out`, `*-v1.out`, and `before-base.out` for byte-identity (no diffs inferred — hashes observed below).
- `grep` over `.ufo/waves/round-32/` for every control name; no report outside `c2/SUMMARY.md` cites any `*-v2.out` name.

## Byte-identity (observed)

SHA256, all three "stale" names **and** `before-base.out` are the same 136 bytes:

```
002a4b6072f54c8213b9914a1d8a15c5992907e8a26c7d685df5c6c519482a77  controls/empty-exit-v2.out
002a4b6072f54c8213b9914a1d8a15c5992907e8a26c7d685df5c6c519482a77  controls/nonexistent-path-v2.out
002a4b6072f54c8213b9914a1d8a15c5992907e8a26c7d685df5c6c519482a77  controls/thin-row-v2.out
002a4b6072f54c8213b9914a1d8a15c5992907e8a26c7d685df5c6c519482a77  before-base.out
```

The three real fixture captures have distinct hashes/sizes: `thin-v2.out` 205B `72274403…`, `noexit-v2.out` 98B `6093142f…`, `badpath-v2.out` 131B `06782824…`.

## The three stale `*-v2.out` files — name → actual output → intended fixture

All three files hold **identical bytes: the v2 gate's before-state run on the
unmodified base tree** (two prose-only counters; no fixture injected):

```
unregistered .ufo/waves/round-17/count-verdicts.py
unregistered .ufo/waves/round-26/count-c1.py
registered 7 unregistered 2 defective 0
```

| Stale filename (path suffix `.ufo/waves/round-32/c2/controls/`) | Actual content | Intended fixture (preregistration `controls` + `after_predicate`; selftest arm name) | Where the intended fixture's real output actually lives |
|---|---|---|---|
| `thin-row-v2.out` | base-tree output above — **no fixture lines** | `CtlThinRow` / selftest arm `thin-row`: 5-col registry row for `.ufo/waves/round-29/count-c1.py` missing cells → expect `defective …: thin-row` (+ entangled `empty-entry`, `empty-exit-map`), `defective 3` | `thin-v2.out` |
| `empty-exit-v2.out` | base-tree output above — **no fixture lines** | `CtlEmptyExitMap` / selftest arm `empty-exit-map`: row for `.ufo/waves/round-29/count-c1.py` with empty exit-map cell → expect `defective …: empty-exit-map`, `defective 1` | `noexit-v2.out` |
| `nonexistent-path-v2.out` | base-tree output above — **no fixture lines** | `CtlNonexistentPath` / selftest arm `missing-path`: row for `.ufo/waves/round-29/count-c1.py` whose entry cites `.ufo/waves/round-999/count-c999.py` → expect `defective …: missing-path:.ufo/waves/round-999/count-c999.py`, `defective 1` | `badpath-v2.out` |

## The three real `*-v2.out` files (verbatim bytes)

`controls/thin-v2.out` (205B, `72274403…`) — the CtlThinRow capture:

```
defective .ufo/waves/round-29/count-c1.py: thin-row
defective .ufo/waves/round-29/count-c1.py: empty-entry
defective .ufo/waves/round-29/count-c1.py: empty-exit-map
registered 9 unregistered 0 defective 3
```

`controls/noexit-v2.out` (98B, `6093142f…`) — the CtlEmptyExitMap capture:

```
defective .ufo/waves/round-29/count-c1.py: empty-exit-map
registered 9 unregistered 0 defective 1
```

`controls/badpath-v2.out` (131B, `06782824…`) — the CtlNonexistentPath capture:

```
defective .ufo/waves/round-29/count-c1.py: missing-path:.ufo/waves/round-999/count-c999.py
registered 9 unregistered 0 defective 1
```

## Intent evidence

- `.ufo/waves/round-32/preregistration.json` C2 `after_predicate`: "each control fixture (thin-row, empty-exit-map, nonexistent-path, prose-only) exits 1 printing the named defect (`defective <path>: thin-row`, `defective <path>: empty-exit-map`, `defective <path>: missing-path:<path>`, or `unregistered <path>`)"; `controls`: `["CtlThinRow", "CtlEmptyExitMap", "CtlNonexistentPath", "CtlProseOnly", "MutEachCheck", "Selftest"]`.
- `c2/SUMMARY.md` lines 14-19 describe the expected content **under the stale names** (`thin-row-v2.out`, `empty-exit-v2.out`, `nonexistent-path-v2.out`); the bytes it describes are in fact the bytes of `thin-v2.out`/`noexit-v2.out`/`badpath-v2.out`. So the SUMMARY's semantic claims are right but its filenames point at the stale copies.
- `selftest-*.out` corroborate fixture names/verdicts: arms `thin-row` → `defective …: thin-row` with `defective 3`; `empty-exit-map` → `defective 1`; `missing-path` → `defective …: missing-path:.ufo/waves/round-999/count-c999.py` with `defective 1` (hermetic path `.ufo/waves/round-98/count-selftest.py`).
- `before-base.out` line in SUMMARY (line 20-21): "v2 semantics on the base tree exit 1 with the two prose-only counters `unregistered` — the repair's real-tree before-state" — exactly the 136-byte payload inside all three stale files.

## Mechanism (inference)

`[INFERENCE]` The capture step that produced `thin-row-v2.out`, `empty-exit-v2.out`,
`nonexistent-path-v2.out` ran the v2 gate against the plain base/lane tree (or an
unpatched fixture path) instead of the three fixture trees, then a second pass
re-captured the real fixture outputs under the short aliases `thin`/`noexit`/`badpath`.
Net effect: each intended control output exists exactly once on disk, but under a
different filename than `SUMMARY.md`/preregistration names use.

## Adjacent observations (for the routed C2 defects)

- None of the six `*-v2.out` files carries an inline `EXIT_CODE=` line; only the
  seven `*-v1.out` files do (`EXIT_CODE=0`). Relevant to the routed "missing
  inline exit code" defect.
- All seven `*-v1.out` files (`thin`, `noexit`, `badpath`, `thin-row`, `empty-exit`,
  `nonexistent-path`, `prose-only`) are byte-identical 40B do-nothing-gate output
  (`72032b1e…`): `registered 9 unregistered 0` + `EXIT_CODE=0`. For the do-nothing
  v1 gate this is the expected uniform pass; `prose-only-v1.out` is not
  distinguishable on disk from the others.
- No `prose-only-v2.out` exists; the prose-only v2 evidence is `before-base.out`
  (which is also what the three stale files duplicate).
- Mutation receipts under `mutations/` use the short names (`MutNoThin-vs-CtlThin`,
  `MutNoPath-vs-CtlBadPath`, `MutNoExitMap-vs-CtlNoExitMap`, plus two negative arms
  `…-vs-CtlBadpath`); `MutNoExitMap-vs-CtlNoExitMap.out` content not reproduced
  here but present.

## Confidence and remaining unknowns

- **High confidence:** the three stale filenames hold byte-identical base-tree output (hash-verified); the intended fixture outputs exist under the short alias names (content matches preregistration `after_predicate` exactly).
- **Unknown:** the exact capture commands/env that produced each file (no per-file command log committed); whether `967d8852` or `c4c46ad` introduced the stale copies is not needed for the mapping — the controls directory lands in commit `c4c46ad` ("round-32: C2 — gate-registry-check v2 …").
- **Note for L1:** round-33 already mirrors this finding — `round-33/preregistration.json` C1 `after_predicate` says the correction table "maps thin-row, empty-exit-map, and missing-path to their exact existing receipts" and the stale files "remain explicitly disclosed as legacy evidence"; `amendment-1.json` cites `badpath-v2.out` as the observed missing-path receipt.

## Tooling ledger

No installs or updates performed; `sha256sum`/`wc`/`grep`/`git log` (read-only) sufficed. Pacman remains paused per orchestrator ruling 2026-10-20.
