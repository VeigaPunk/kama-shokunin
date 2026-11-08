# MT01Forgeries — independent mutation test of the round-98 C2 instrument

Seat: `MT01Forgeries` (leaf, no dispatch). Wave: round 98 w1. Lane: `kama-shokunin`.
Scope: attack the already-landed C2 instrument; no frozen predicate changed, no tracked lane
file edited, no lane git/jj state touched.

## 1. Instrument bytes under test

| object | revision | sha256 |
|---|---|---|
| `tools/kama-probe.sh` (probe under claim) | `34ad44e9f783b35a804f020d6b02c48c04ade481` (round-98 freeze) | `40ab387ee9877a9505af61172db5fc1cd2006021fb026e761e558e307a5b4a6e` |
| same, at `681c80a4` (the frozen controls' `--rev`) | `681c80a4e3c745c22559f74b2c2a1917bdc66fc6` | `40ab387e…` — `git diff --stat 681c80a4 34ad44e9 -- tools/kama-probe.sh` is empty |
| `tools/round98-router-budget.py` (counter) | HEAD = freeze rev; clone byte-identical | `83d3226f7d213213db0daa4ba08b09160ee1f356a7f12761194b24d311d90398` |

At the start of this seat the lane HEAD was `34ad44e9` (round-98 freeze); it has since advanced
to `160e22dd` (M1), with `tools/kama-probe.sh` and `tools/round98-router-budget.py` byte-identical
(the shas above). The clone used for every run is pinned at `34ad44e9`; all receipts print
`rev=34ad44e9f783b35a804f020d6b02c48c04ade481` because `--probe-file` overrides the probe and
`HEAD` was that commit in the clone.

The probe's charge sites read from the bytes: `need()` at `tools/kama-probe.sh:646-653`,
the per-string-element loop at `:692-718`, the tensor header at `:747-753`; `MAX_STEPS =
5_000_000` at `:584`. Measured from the mutated parser (not assumed): preamble `p = 4`,
header cost `5 + nd` (6 at nd=1, 9 at nd=4) — `frozenmut.json`, pristine row.

Method: clone the lane with `git clone --shared` into
`/fast/scratch/hyaku/kama-r98/MT01Forgeries/repo`, write MY OWN byte patches against the probe
bytes (`mk_mutants.py`, exact-once anchors, refuse otherwise), then

1. `patchcheck.py` — the extracted `ROUTER_PY` parser on tiny synthetic GGUFs with a reduced
   `MAX_STEPS` set in the exec namespace, so each patch's charge change is measured directly;
2. `selfcheck.py` — the full probe under `bash check --port … --json` (the counter's own
   `Runner`/`Stub`, imported read-only) against near-boundary fixtures I built that no counter
   cell contains;
3. the frozen counter, `--control` (natural pass only; no burners) with `--cells legacy`,
   `--cells new` and `--cells r97set`, `--probe-file <mutant>` (`run_matrix.py`,
   `run_matrix2.py`, `rerun_BCE.py`; receipts under `receipts/`, matrix in
   `matrix_final.json`).

## 2. My mutants (own patch text, not the counter's `MUTANTS`)

| id | class | patch site | sha256 |
|---|---|---|---|
| `A_kv2x` | header cost kept at `5+nd`, but every step inside a KV value is charged twice (the per-element string charge included) | `skip_value` wrapper: execute `_skip_value`, then add its step delta again (`diffs/A_kv2x.diff`) | `d63f30b1d8ddc0e6f601766b52462047564d65ff85f75a20f6847b17ad94748a` |
| `B_flat6` | constant 6 steps per header for any `nd>=1` | after the dims read: `steps[0] -= nd - 1 if nd >= 1 else 0`, so `5+nd-(nd-1)=6` (`diffs/B_flat6.diff`) | `1c9e88fc013f539679046da3eae85a79869ec1071b3471bdc86570a054f15298` |
| `C_maxmeta100` | `MAX_META` 512 MiB → 100 MiB, own two-line form | `MAX_META = 100 * 1024 ** 2` (`diffs/C_maxmeta100.diff`) | `ea2b204183ff7ea076ed7dd6622e4a20b53f585e9914bedcabe6422a2e8bcac4` |
| `D_minus1` | one FEWER step per header: `5+nd` → `4+nd` | loop top: `steps[0] -= 1` (`diffs/D_minus1.diff`) | `df9e29a2d5b1a73f0c2747e62e9c903891b497583bb0a5a334ac1de2327492a3` |
| `E_plus1` | one MORE step per header: `5+nd` → `6+nd` | after the header completes: `steps[0] += 1` (`diffs/E_plus1.diff`) | `9c27e52475aa736d8743ec65bf620c194fb770ac6152624d7e7aefe22172c593` |
| `F_plus2` | two MORE steps per header: `5+nd` → `7+nd` | loop top: `steps[0] += 2` (`diffs/F_plus2.diff`) | `d895c563bfd000fa1eda7bd99dbbb88853a1f4c71b5bc15427837e7ae5e5399b` |

Patch application: each anchor asserted `bytes.count(anchor) == 1` before replacement
(`mk_mutants.py`); all six mutants pass `bash -n`; manifest with per-anchor sha/length and
per-mutant sha in `mutants/manifest.json`.

Note on independence: my first-draft `+1` patch was inserted at the loop top and turned out
byte-identical to the counter's own `overcharge` mutant (`b7bdbfae…`). I moved the extra step
to the post-header site (`9c27e524…`) so the probe is not the counter's bytes; it still grades
identically on every cell (section 5). `C` must set the same constant value, but its patch text
is my own two-line form.

## 3. Patch semantics verified on tiny fixtures (reduced budget)

`patchcheck.py` loads each probe's embedded parser and sets `MAX_STEPS` in the namespace after
loading (the parser code path is the probe's own bytes; the budget is reduced so a 30-header
file lands on the boundary the patch moves). Output (`patchcheck.json`):

```
PATCHCHECK pristine     nd1_30_cap170=- nd1_30_cap200=invalid nd4_30_cap200=- strarr_30_cap60=invalid maxmeta110=invalid
PATCHCHECK A_kv2x       nd1_30_cap170=- nd1_30_cap200=invalid nd4_30_cap200=- strarr_30_cap60=-       maxmeta110=invalid
PATCHCHECK B_flat6      nd1_30_cap170=- nd1_30_cap200=invalid nd4_30_cap200=invalid strarr_30_cap60=invalid maxmeta110=invalid
PATCHCHECK C_maxmeta100 nd1_30_cap170=- nd1_30_cap200=invalid nd4_30_cap200=- strarr_30_cap60=invalid maxmeta110=-
PATCHCHECK D_minus1     nd1_30_cap170=invalid nd1_30_cap200=invalid nd4_30_cap200=- strarr_30_cap60=invalid maxmeta110=invalid
PATCHCHECK E_plus1      nd1_30_cap170=- nd1_30_cap200=-       nd4_30_cap200=- strarr_30_cap60=invalid maxmeta110=invalid
PATCHCHECK F_plus2      nd1_30_cap170=- nd1_30_cap200=-       nd4_30_cap200=- strarr_30_cap60=invalid maxmeta110=invalid
PATCHCHECK E_plus1@230=invalid F_plus2@230=-
PATCHCHECK_OK
```

Each mutant differs from pristine only where its class predicts: A on the KV string-array case
(`invalid`→`-`), B on nd=4 (`-`→`invalid`), C on the 110 MiB maxmeta fixture
(`invalid`→`-`), D on nd=1 at cap 170 (`-`→`invalid`), E/F at cap 200 (`invalid`→`-`), and E/F
are separated at cap 230.

## 4. End-to-end on self-built fixtures the 19 cells do not contain

`selfcheck.py` runs the real probe (`bash check --port … --expect good --json`) against
fixtures I built, through the counter's `Stub`/`Runner`. Designed classes are printed by the
script. Verdicts (`selfcheck.json`):

| fixture | pristine | A_kv2x | B_flat6 | C_maxmeta100 | D_minus1 | E_plus1 | F_plus2 |
|---|---|---|---|---|---|---|---|
| `kvarr_2p6m` (2.6M-element string array + bad tensor offset) | `MODEL_UNLOADED/router-model-invalid` 0.46s | **`MODEL_OK/router-unloaded-autoload` 0.44s** | invalid | invalid | invalid | invalid | invalid |
| `nd4_650k` (650k headers nd=4, bad offset) | `MODEL_OK/…` 1.74s | `MODEL_OK` | **`MODEL_UNLOADED/router-model-invalid` 1.95s** | `MODEL_OK` | `MODEL_OK` | `MODEL_OK` | `MODEL_OK` |
| `nd1_950k` | `MODEL_OK/…` 1.78s | `MODEL_OK` | `MODEL_OK` | `MODEL_OK` | **`MODEL_UNLOADED/router-model-invalid` 1.97s** | `MODEL_OK` | `MODEL_OK` |
| `nd1_720k` | `MODEL_UNLOADED/router-model-invalid` 1.58s | invalid | invalid | invalid | invalid | **`MODEL_OK/…` 1.44s** | **`MODEL_OK/…` 1.30s** (also noted) |
| `maxmeta110` (110 MiB KV string, bad tensor) | `MODEL_UNLOADED/router-model-invalid` 0.12s | invalid | invalid | **`MODEL_OK/…` 0.12s** | invalid | invalid | invalid |

`SELFCHECK_OK`. So each patch is behaviorally real on bytes the counter never builds.

## 5. Counter receipts: survive / catch matrix

Every run is `--control` (natural pass only). `probe=override` identifies my bytes by sha; the
counter's control line prints `mutant=none` for overrides.

| mutant | legacy (13) | r97set (17) | new (19-set's 6 new cells) |
|---|---|---|---|
| `A_kv2x` | survived 13/13 | survived 17/17 (direct) | survived 6/6 |
| `B_flat6` | survived 13/13 | caught W15 (composed; W15 ∈ r97set) | caught: 5/6, W15 red |
| `C_maxmeta100` | survived 13/13 | caught W16 (composed) | caught: 5/6, W16 red |
| `D_minus1` | survived 13/13 | caught 15/17, W14+W17 red (direct) | caught: 4/6, W14+W17 red |
| `E_plus1` | survived 13/13 | survived 17/17 (direct) | caught: 4/6, W18+W19 red |
| `F_plus2` | caught 12/13, W11 red | caught W11 (composed) | caught: 4/6, W18+W19 red |
| pristine (my copy of the claimed probe) | — | — | 6/6 survived |

“Composed” means the red cell is a member of `R97_CELLS` (`tools/round98-router-budget.py:158`)
and its cell line was measured in the 6-cell run; A, D and E were run directly on `r97set`.
No claimed cell is green in these runs.

Exact control and red-cell lines (receipts relative to
`.ufo/waves/round-98/w1/out/MT01Forgeries/receipts/`):

```
A_kv2x-legacy.out:  ROUTER_BUDGET98_CONTROL cells=13 cells_ok=13 mutant=none slow_files=40 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=override probe_sha256=d63f30b1… rev=34ad44e9… ok=1
A_kv2x-r97set.out:  ROUTER_BUDGET98_CONTROL cells=17 cells_ok=17 mutant=none slow_files=40 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=override probe_sha256=d63f30b1… rev=34ad44e9… ok=1
A_kv2x-new.out:     ROUTER_BUDGET98_CONTROL cells=6 cells_ok=6 mutant=none slow_files=40 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=override probe_sha256=d63f30b1… rev=34ad44e9… ok=1

B_flat6-legacy.out: ROUTER_BUDGET98_CONTROL cells=13 cells_ok=13 … survived=1 caught=0 … probe_sha256=1c9e88fc… ok=1
B_flat6-new.survived-mode.out: ROUTER_BUDGET98_CONTROL cells=6 cells_ok=5 … expect_cell=W15-700k-nd4 cell_ok=0 survived=0 caught=1 … probe_sha256=1c9e88fc… ok=0
  ROUTER_BUDGET98_CELL nat W15-700k-nd4 ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/2.10s entries=0

C_maxmeta100-legacy.out: ROUTER_BUDGET98_CONTROL cells=13 cells_ok=13 … survived=1 caught=0 … probe_sha256=ea2b2041… ok=1
C_maxmeta100-new.survived-mode.out: ROUTER_BUDGET98_CONTROL cells=6 cells_ok=5 … expect_cell=W16-maxmeta cell_ok=0 survived=0 caught=1 … probe_sha256=ea2b2041… ok=0
  ROUTER_BUDGET98_CELL nat W16-maxmeta ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/0.13s entries=0

D_minus1-legacy.out: ROUTER_BUDGET98_CONTROL cells=13 cells_ok=13 … survived=1 caught=0 … probe_sha256=df9e29a2… ok=1
D_minus1-new-W14.survived-mode.out: ROUTER_BUDGET98_CONTROL cells=6 cells_ok=4 … expect_cell=W14-900k-nd1 cell_ok=0 survived=0 caught=1 … probe_sha256=df9e29a2… ok=0
  ROUTER_BUDGET98_CELL nat W14-900k-nd1 ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/1.92s entries=0
  ROUTER_BUDGET98_CELL nat W17-833333-nd1 ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/1.80s entries=0
D_minus1-r97set.survived-mode.out: ROUTER_BUDGET98_CONTROL cells=17 cells_ok=15 … expect_cell=W14-900k-nd1 cell_ok=0 survived=0 caught=1 … probe_sha256=df9e29a2… ok=0  (W14+W17 red)

E_plus1-legacy.out: ROUTER_BUDGET98_CONTROL cells=13 cells_ok=13 … survived=1 caught=0 … probe_sha256=9c27e524… ok=1
E_plus1-r97set.out: ROUTER_BUDGET98_CONTROL cells=17 cells_ok=17 … survived=1 caught=0 … probe_sha256=9c27e524… ok=1
E_plus1-new-W18.survived-mode.out: ROUTER_BUDGET98_CONTROL cells=6 cells_ok=4 … expect_cell=W18-800k-nd1 cell_ok=0 survived=0 caught=1 … probe_sha256=9c27e524… ok=0
  ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/6.15s entries=0
  ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/3.91s entries=0

F_plus2-legacy-W11.survived-mode.out: ROUTER_BUDGET98_CONTROL cells=13 cells_ok=12 … expect_cell=W11-700k cell_ok=0 survived=0 caught=1 … probe_sha256=d895c563… ok=0
  ROUTER_BUDGET98_CELL nat W11-700k ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/1.34s entries=40
F_plus2-new-W18.survived-mode.out: ROUTER_BUDGET98_CONTROL cells=6 cells_ok=4 … expect_cell=W18-800k-nd1 cell_ok=0 survived=0 caught=1 … probe_sha256=d895c563… ok=0
  ROUTER_BUDGET98_CELL nat W18-800k-nd1 ok=0 … run1=MODEL_OK/router-unloaded-autoload/1.35s entries=0
  ROUTER_BUDGET98_CELL nat W19-520k-nd4 ok=0 … run1=MODEL_OK/router-unloaded-autoload/1.39s entries=0

pristine-new.out: ROUTER_BUDGET98_CONTROL cells=6 cells_ok=6 … survived=1 caught=0 … probe_sha256=40ab387e… ok=1
```

### Answers to the two sizing questions

- **+2/header is caught by W18 and W19.** Both cells are red in every F run
  (`cells_ok=4`, W18 and W19 red). It is also caught earlier by the 13-cell legacy set at
  `W11-700k` (`cells_ok=12`): 4 + 700 000×(5+1+2) = 5 600 004 > 5 000 000, so the 700k nd=1
  fixture flips `invalid`→`-`. The class is caught by both sets, not only the new cells.
- **-1/header is caught, by W14 and W17, in both the 19-cell set and the 17-cell `r97set`,
  and missed by the 13 legacy cells.** `4 + 900 000×5 = 4 500 004 ≤ 5 000 000` makes W14's
  900k nd=1 file decide `invalid` where it must stay `-`; `4 + 833 333×5 = 4 166 669` does the
  same at W17. Receipts above. The frozen `undercharge` mutant is a zero-charge probe, not a
  -1/header probe, so this class is graded by the cells but not literally exercised by the
  frozen mutant (my `D` is the literal -1 probe).
- **+1/header survives 13/13 legacy and 17/17 r97set and is caught only by W18/W19** — the
  round-98 window claim is reproduced with independently written bytes. The window arithmetic
  also reproduces: real nd=1 `invalid` iff `T ≤ 833 332`, +1 `-` iff `T ≥ 714 286`; real nd=4
  `invalid` iff `T ≤ 555 555`, +1 `-` iff `T ≥ 500 000`; 800 000 and 520 000 sit strictly
  inside those windows.

## 6. Findings

### F1 — `A_kv2x` (double-charged KV/string work) survives all three cell sets; it is disclosed, and it is observable

Receipts `A_kv2x-legacy.out` (13/13 green), `A_kv2x-new.out` (6/6), `A_kv2x-r97set.out`
(17/17). This is not a violation of the frozen predicate: `plans/round-98-claims.md:115`
discloses exactly this class (“a probe that charges a wrong number of non-header steps (KV,
string elements) is not graded”). It is a coverage finding, and it is not hypothetical: on
`kvarr_2p6m` the real probe decides `MODEL_UNLOADED/router-model-invalid` (0.46s) while the
mutant decides `MODEL_OK/router-unloaded-autoload` (0.44s) — i.e. a probe that overcharges
KV/string work grades an unloadable model as loadable while passing all 19 cells. The graded
property is header accounting only; any reading of C2 wider than its disclosed limits is
green on a wrong probe.

### F2 — the `--probe-file` override cannot reach the `--expect caught` control interface

```
$ python3 …/tools/round98-router-budget.py --repo … --rev HEAD --work … \
    --probe-file …/mutants/B_flat6.sh --cells new --control --expect caught --expect-cell W15-700k-nd4
ROUTER_BUDGET98 usage: --control requires --expect and, for `caught`, a --mutant
# exit=64
```
(`receipts/B_flat6-new.out`; gate at `tools/round98-router-budget.py:613`.) Naming a `--mutant`
does not help: `apply_mutant` runs on the bytes after the `--probe-file` override
(`:639-644`), so it would stack that mutant's patch on the override bytes. An external
probe's named-cell red is therefore only expressible as
`--control --expect survived --expect-cell <cid>`, which prints `cell_ok=0 survived=0 caught=1`
and exits 1 (the receipts in section 5). The frozen controls are unaffected (they use
`--mutant` over the revision bytes), and no false green results — but the “caught” control as
written is not reproducible for an independently supplied probe, only the survive-mode cell
assertion is.

### F3 — no false green among the five graded classes; the frozen control receipts reproduce

Every frozen `controls/c2-new-mutants.out` mutant was re-run in this environment with the
frozen counter and probe bytes (`receipts/frozen-*.out`, `reproduce_frozen.json`). The
`probe_sha256` values reproduce exactly and the named cells redden:

| frozen mutant | sha256 (reproduced) | measured charge class | cells_ok | red |
|---|---|---|---|---|
| `flat6` | `6f543d16b73e85ae4f9aa2dbae713879b12c1b1a9370e6b14c32d6892c39df38` | 4 + 6/header at nd=1 **and** nd=4 | 5 | W15 |
| `undercharge` | `eb5613718e500edf8835f6d38ecf838dce2aee3072742019aafcef89ba62a336` | 0.0 + 0.0/header (zero-charge, not -1) | 3 | W14, W15, W17 |
| `maxmeta` | `7ba6f7f9cc53b4d7c88b40d6f1787ab3806099e946c181c8c9ac824aeb8b7b56` | `MAX_META` 100 MiB | 5 | W16 |
| `nopreamble` | `f7ed00271757cd78e5d2c9b4413de5dad811e97f59af56d0d18c9a4a831a5034` | preamble 0, headers unchanged | 5 | W17 |
| `overcharge` | `b7bdbfae4ec8757b5fcfe34874fa720955df71a187f5ddbfaca29ea3838d6219` | 4 + 7/header nd=1, 4 + 10/header nd=4 | 4 | W18, W19 |

The `flat6` label is accurate in its bytes (constant 6 at both ranks, not merely at nd=1);
the `overcharge` control is +1/header; `controls/c2-legacy-mutants.out` (`--cells r97set`,
overcharge, `survived=1`, `cells=17`) is reproduced by my independently written `E`
(`E_plus1-r97set.out`, 17/17 green). The receipts were produced at `--rev 681c80a4`, whose
probe bytes are identical to the freeze revision's (section 1), and every mutant sha in them
re-derives from `apply_mutant` over those bytes — the controls bind the same instrument that
HEAD carries.

### F4 — set-level summary (which set misses what)

- 13-cell `legacy`: misses A, B, C, D, E; catches F (W11).
- 17-cell `r97set`: misses A and E (both directly measured 17/17 green); catches B (W15),
  C (W16), D (W14+W17), F (W11).
- 19-cell set: misses A only; catches B, C, D, E, F.
- The +1 window is exactly the one the round-97 17-cell set missed; W18/W19 close it for the
  unconditional +1 and +2 classes. A conditional overcharge (e.g. only at nd=0, or +1 only on
  the last header) is outside the graded class and was not mutated.

## 7. Limits of this mutation check

- Six single-point byte patches; compound probes (e.g. +1 at nd=1 combined with -1 at nd=4)
  were not tested. The graded class is “unconditional +k per header”; `k ≥ 2` is caught, and
  `k = -1` is caught, but the accidental passes for conditional forms remain unmeasured.
- `patchcheck.py` sets `MAX_STEPS` in the exec namespace, so it grades the parser function and
  its charge arithmetic, not the shell wrapper; `selfcheck.py` covers the full `bash check`
  path end-to-end.
- Control mode only (no `--load` pass): all C2 cell verdicts are step-deterministic by design
  and the frozen controls are natural-only. The predicate's load-side assertions were not
  re-run by this seat.
- The out-dir fixtures are near-boundary by construction and derive their classes from the
  probe's own arithmetic; they are not a proof over all `(T, nd)`.

## 8. Restoration evidence

- The lane's `tools/kama-probe.sh` was never written: `sha256sum` is still
  `40ab387ee9877a9505af61172db5fc1cd2006021fb026e761e558e307a5b4a6e`, and
  `tools/round98-router-budget.py` is still `83d3226f7d213213db0daa4ba08b09160ee1f356a7f12761194b24d311d90398`.
  This seat wrote only `.ufo/waves/round-98/w1/out/MT01Forgeries/` and the assigned report
  `.ufo/waves/round-98/w1/MT01Forgeries.md`.
  Concurrent lane seats did modify five tracked paths during the wave (`controls/c1-base.out`,
  `controls/c3-base.out`, `corpus/lessons/round-98.md`, `LOG.md`, `SCORECARD.md`; the last two were
  still being written at 11:22:59, after this report). Those are not this seat's writes and were
  not touched: the lane advanced from `34ad44e9` to `160e22dd` (M1) while this seat ran, and both
  instrument files remained byte-identical throughout.
- The clone's tracked probe sha equals `git show HEAD:tools/kama-probe.sh`
  (`40ab387e…`); `git -C <clone> status --porcelain` is empty before and after all runs; the
  counter sha in the clone equals the lane's (`83d3226f…`).
- Mutants exist only as copies under `out/MT01Forgeries/mutants/` (sha in
  `mutants/manifest.json`); the frozen-mutant copies under `frozen-mutants/` were materialized
  by `apply_mutant` for measurement only.
- Scratch `/fast/scratch/hyaku/kama-r98/MT01Forgeries/` (clone, work dirs, self-built fixtures)
  is removed after the receipts were copied into the out dir.

## 9. Tooling

No installs or upgrades; host `python3` 3.14.8, `git`, `bash`, `diff` used as found. No pacman,
no host services, no burners started by this seat (the counter's `--control` path raises none).
