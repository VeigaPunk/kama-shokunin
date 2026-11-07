# MT02 — mutation testing of the frozen C2 counter (`tools/round93-setter-rows.py`)

Seat `MT02SetterCounterMutants`, kama round 93 wave 1. Scratch `/fast/scratch/hyaku/kama-r93/MT02SetterCounterMutants/`
(own seat only, removed at the end). The lane was read-only: every counter under test is a copy in this out dir, and
`tools/round93-setter-rows.py` was never written (sha256 before and after = `367eed2f…`).

## Scope

26 single-point mutants of the counter at M2 `ee19acbdabc8ac572e82ae56459c364457895b06`
(sha256 `367eed2f16d4d240170ed0bc8c96f6a9c6f1c2593b2b380e4f467e963f0ea185`; byte-identical at F `0f272a37`, M1
`fe5f031c` and the current tip `4c4adc63`). Each mutant changes exactly one contiguous point — `difflib` reports one
non-equal block for all 26 (`mutants/summary.tsv:2`, column `hunks`). The committed battery
`.ufo/waves/round-93/controls/c2-forgeries.py` was copied to `c2-forgeries-MT02.py`; the only change is that the counter
path comes from `C2_COUNTER` (3-line diff, `battery-copy.diff`). Cases, forgeries, expected strings and the corpus
inputs are byte-identical.

## Commands and outputs (true exit codes)

1. Counter at M2 on the real section (positive control):
   `python3 …/mutants/m2-counter.py --repo . --rev ee19acbd… --work <scratch>/real --archive <scratch>/b12177.tar.gz`
   → exit 0, `SETTER_ROWS population=48 rows=48 bound=48 unbound=0 missing=0 duplicates=0 fabricated=0
   derived_checked=47 derived_disagree=0 decisions=2 decisions_bound=2 … skill=rev` (`logs/m2-real.out`). Reproduces
   `measured/c2.out`.
2. `C2_COUNTER=…/mutants/m2-counter.py python3 …/c2-forgeries-MT02.py <scratch>/bat/m2-counter <archive>` (cwd = lane)
   → exit 0, `C2_CONTROLS total=12 as_expected=12`. Output is byte-identical to `controls/c2-forgeries.out` apart from
   that receipt's trailing `exit=0` line (`logs/m2-counter.out`), so the copy changes no control behaviour.
3. `python3 …/run-battery.py` → 27 battery runs (baseline + 26 mutants), 14.4–19.4 s each at load 75 (load in every
   log header); 10 mutants killed, 16 survived (`logs/<id>.out`).
4. `python3 …/survivor-forgeries.py` → exit 0, `MT02_FORGERIES total=16 failures=0` (`logs/survivor-forgeries.out`).
5. `python3 …/frozen-probes.py` → exit 0; probes G1–G3 each print a fully bound section (`logs/frozen-probes.out`).
6. `python3 …/analysis.py` → `population=48`, `rows_with_multiple_long_options=0` (`logs/analysis.out`).

Load average at the start 89.3, during the runs 64–75, at the end 48.9; all verdicts are behavioural (no timing claim).

## Findings

**F1 NOTE — the committed battery is much thinner than 12/12 suggests.** 16 of 26 single-point weakenings survive it,
and 13 of those are demonstrated false greens: the frozen counter rejects the forged section with a named reason while
the mutant prints `population=48 rows=48 bound=48 unbound=0 missing=0 duplicates=0 fabricated=0 derived_checked=47
derived_disagree=0 decisions=2 decisions_bound=2` — every `met` clause at `tools/round93-setter-rows.py:360` satisfied,
so as a real `SKILL.md` section it would exit 0 (`logs/survivor-forgeries.out`). The two most consequential are 24
(`R16` value → `9999` binds) and 08 (`R17` decision may omit P20, the `--gpt-oss-20b-default` start that sets 2 slots):
the decisions are the artifact's product, and only one committed case each touches them.

**F2 DEFECT — `scope` is ungraded outside `common/arg.cpp` and unnamed in K2.** The derived scope rule runs only when
`f == "common/arg.cpp"` (`tools/round93-setter-rows.py:266`), and K2 enumerates "parameter, condition, effect or value"
(`plans/round-93-claims.md:80`) — not scope. Probe G2 empties P36's scope cell and the frozen counter prints a fully
bound section (`logs/frozen-probes.out` G2), so a wrong scope on any of the 24 non-`arg.cpp` rows is caught neither by
the counter nor by the reviewer rule the claim names, and it is absent from the disclosed-limit list
(`plans/round-93-claims.md:73-74`). The claim's row spec does carry a scope cell, so the wording gap is in K2.

**F3 NOTE — non-literal value cells are only non-empty-checked.** B5 requires the integer literal only when `INT_RHS`
matches (`tools/round93-setter-rows.py:252-258`); probe G1 rewrites P09's value `the parsed PORT` to `8080` and the
frozen counter binds it. The counter docstring states the rule, but the claims' disclosed-limit list does not repeat it
while K2 does name `value`, so the reviewer read is the only guard; no committed control tests a non-literal value.

**F4 NOTE — the “first long option” derivation has no discriminating power on this population.** Every population
`add_opt` block declares exactly one long option (`rows_with_multiple_long_options=0`, `logs/analysis.out`), so mutant
07 (`opts[0]` → `opts[-1]`, `tools/round93-setter-rows.py:221`) is observationally identical to the frozen counter on
all 48 rows; no `SKILL.md` forgery can kill it.

**F5 NOTE — `MIN_POP` is not load-bearing.** The archive digest pins population at 48, and `len(prow) == n`
(`tools/round93-setter-rows.py:360`) is the live guard: mutant 11 (`MIN_POP` 40 → 1) is killed by no forgery, and the
5-row probe F11 gives the same `rows=5 … missing=43` rejection under both counters (`logs/survivor-forgeries.out`).

**F6 NOTE — the `duplicates=0` predicate clause is redundant on this input.** With duplicate detection removed (mutant
12) a duplicated P12 prints `rows=49 bound=49 … duplicates=0`; the section is still rejected by `rows/bound == n`, so
the lost detection is a diagnostic label, not a false green (`logs/12-duplicate-removed.out`, F12).

**F7 NOTE — kills are narrow where they exist.** 03 is killed only by V6, 06 only by V5, 21 only by V2, 22 only by V10,
and 09/10 only by V7/V9; dropping or relaxing any one of those cases would leave its check unguarded.

## Mutant table (kill = battery case whose expectation broke; forgery = single-cell forgery that kills a survivor)

| Id | single-point edit | Verdict |
|---|---|---|
| 01 | `POP_RE` drops `AIP_HTTP_PORT` | killed P0,V3,L1 (P35 becomes `fabricated`, population 47) |
| 02 | `PORT_TOK`/`NP_TOK` bodies swapped | killed P0,V2,V4,V5,V6,V7,V9,L1 |
| 03 | B5 integer-literal comparison removed | killed V6 |
| 04 | B2 exact text → `t in line` | **survived**; F04: P09 text `params.port` → frozen `text`, mutant green |
| 05 | B6 source-row lookup removed | **survived**; F05: P09 source S600 → frozen `source`, mutant green |
| 06 | B7 scope comparison removed | killed V5 |
| 07 | `arg_block` returns last long option | **survived**; no forgery (F4) |
| 08 | R16/R17 decision-name check removed | **survived**; F08: R17 drops “P20 …” → frozen `decision-names`, mutant green |
| 09 | overriding-set `==` → `want ⊆ got` | killed V7 |
| 10 | overriding-set `==` → `got ⊆ want` | killed V9 |
| 11 | `MIN_POP` 40 → 1 | **survived**; no forgery (F5) |
| 12 | duplicate detection removed | **survived**; F12 diagnostic only (F6) |
| 13 | B4 `-`/`unrelated` pairing removed | **survived**; F13: P08 effect `unrelated` → frozen `unrelated-pairing`, mutant green |
| 14 | B3 `n_parallel` token check removed | **survived**; F14: P08 param `n_parallel` → frozen `parameter-token`, mutant green |
| 15 | `D_RE` no longer recognises R17 | killed P0,V9,L1 (decisions=1) |
| 16 | D-row `supersedes` check removed | **survived**; F16: R16 supersedes `R08` → frozen `header`, mutant green |
| 17 | B7 `ex == LLAMA_EXAMPLE_X` check removed | **survived**; F17: P01 condition enum → frozen `derived`, mutant green |
| 18 | B5 `value-empty` check removed | **survived**; F18: P09 value `-` → frozen `value-empty`, mutant green |
| 19 | effect vocabulary removed | **survived**; F19: P02 effect `declarez` → frozen `effect-enum`, mutant green |
| 20 | parameter vocabulary removed | **survived**; F20: P02 param `parallel` → frozen `parameter-enum`, mutant green |
| 21 | `missing` forced to 0 | killed V2 |
| 22 | archive digest pin removed | killed V10 (rc 2 → rc 1) |
| 23 | backtick strip removed | killed P0,V2,V4,V5,V6,V7,V9,L1 |
| 24 | D-row value-vs-default check removed | **survived**; F24: R16 value `9999` → frozen `value`, mutant green |
| 25 | `value-not-dash` check removed | **survived**; F25: P08 value `5` → frozen `value-not-dash`, mutant green |
| 26 | `condition-empty` check removed | **survived**; F26: P36 condition empty → frozen `condition-empty`, mutant green |

Restoration: the lane counter's bytes were never altered (`sha256sum` `367eed2f…` before and after); `git status
--porcelain` in the lane has no modified tracked entry (only untracked wave artifacts, some from sibling seats). The
scratch tree is deleted after the receipts above were copied here.

## Deliverables (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-93/w1/out/MT02SetterCounterMutants/`)

- `mutants/01-…py … 26-…py`, `mutants/m2-counter.py` (byte copy of M2), `mutants/manifest.tsv` (edit + sha256),
  `mutants/summary.tsv` (hunks, verdict, evidence).
- `c2-forgeries-MT02.py`, `battery-copy.diff`; `make-harness.py`, `run-battery.py`, `survivor-forgeries.py`,
  `frozen-probes.py`, `analysis.py`, `summarize.py`.
- `logs/` — 26 mutant batteries + `m2-counter.out` (baseline 12/12), `m2-real.out`, `survivor-forgeries.out`,
  `frozen-probes.out`, `analysis.out`.

VERDICT: holds — C2's predicate reproduces at M2 with the untouched counter (`367eed2f…`, 48/48, decisions 2/2, exit 0)
and the committed battery is 12/12; the mutation result is a control-coverage finding (16/26 survivors, 13 demonstrated
false greens under a weakened counter plus one K2 wording gap on `scope`), not a falsification of the landed claim.
