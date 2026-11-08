# MT02SetterCounterMutants — r94 C2 counter mutation probe

## Scope
- Subject: frozen C2 counter `tools/round94-setter-sweep.py` at M2 `6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623`
  (child of M1 `a27656a454b1a2364f8b6e55f42fbca8c2e86ee4`, base `e6f1dccecbad6dea44a129dabc928822c458e824`,
  freeze F `285f17832d0e26364366bbf19888d68f1838249b`),
  sha256 `49c5d0cb346ff4d693aecc5a287dc6bf09f916e0acc69ef5f8872366e41b9fff`; lane copy and my copy identical
  before and after the probe.
- Inputs copied from M2: `SKILL.M2.md` sha256 `9eecd40cc7b0570d1370c1c929a8efced8e91325eff87ff964992e0b2e8ff5ea`,
  `SOURCES.M2.md` sha256 `07878961a8cab65c3ffa0cc136cbb9cf3abe986f38ddb21f7fb01b772a70d51a`; archive b12177 sha256
  `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13` (re-verified by the counter every run).
- 29 single-point mutants (m01–m29) under `.ufo/waves/round-94/w1/out/MT02SetterCounterMutants/mutants/`; each is one
  asserted-once replacement (m07 is the two-line PORT_TOK/NP_TOK swap; footprints in `runs/mutant-diffstat.txt`).
- Detector A: the committed control shape — counter stdout on the M2 `SKILL.md`/`SOURCES.md` (via `--skill-file`/
  `--sources-file`) must equal `.ufo/waves/round-94/measured/c2.out`. Detector B: a forged SKILL row rejected by the
  pristine counter must still be rejected by the mutant.
- Host load1 135–206 during the probe (`uptime`); no timing claim. Lane read-only; scratch
  `/fast/scratch/hyaku/kama-r94/MT02SetterCounterMutants/` removed after receipts were copied.

## Commands and outputs (true exit codes)
1. `git clone --shared …/kama-shokunin scratch/wt && git -C scratch/wt checkout --detach 6aa5fa6b…` → rc 0;
   `rev-parse --show-toplevel` = scratch/wt; `sha256sum` lane vs copy = `49c5d0cb…` both.
2. `curl -sfL https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177` → rc 0; sha256 `f50a52f4…`.
3. `python3 counter.M2.py --repo scratch/wt --rev 6aa5fa6b… --work … --archive … --skill-file SKILL.M2.md
   --sources-file SOURCES.M2.md` → rc 1 (control-file branch, `counter.M2.py:357`); 96 lines; `cmp` vs
   `measured/c2.out` rc 0 (`runs/baseline.out`).
4. Same without `--skill-file/--sources-file` (files read via `git show` at M2) → rc 0, stdout identical to (3)
   (`runs/predicate-nofiles.out`) — the frozen predicate's exit-0 form reproduces.
5. `python3 mutation-run.py` → rc 0; 29/29 mutants compile; rerun rc 0 and `cmp summary.run1 summary.run2` rc 0.
6. `python3 extra-probes.py` → rc 0; `python3 equivalence-m20.py` → rc 0; `python3 diffstat.py` → rc 0.
7. `bash restore-check.sh` → counter_rc=1, `cmp` restored vs baseline rc 0, pristine sha unchanged; lane counter
   sha unchanged (`49c5d0cb…`).

## Findings
F1 NOTE — Detector A alone kills the 8 population/parser mutants, so the committed control exercises POP_RE, both
population clauses, both special cases, both token regexes and the R18/R19 parser: m01 pop=90 rows=92; m02 pop=80,
12 unbound, R19 want=0 got=7; m03 pop=70 rows=92; m04 pop=82; m05 pop=91; m06 pop=90; m07 `SETTER_MISSING`
arg.cpp:1373/2515/2521…; m08 decisions=1/2 (`runs/summary.tsv:2-9`, `runs/m01.outing`…`runs/m08.outing`).

F2 NOTE — 16 gate relaxations survive Detector A byte-identically and are killed only by a forged row; for each, the
pristine counter rejects the forged input on the mutated gate and the mutant prints `met=True` (`runs/forge-pri-*`,
`runs/forge-m*-*`):
- m09 parameter-token (n_parallel) — f16 — `parameter-token`
- m10 entry-enum — f05, f12 — `entry-enum`
- m11 effect-enum — f13 — `effect-enum`
- m12 dash-param-setter — f10 — `dash-param-setter`
- m13 param-unrelated — f11 — `param-unrelated`
- m14 INT_RHS literal — f06 — `value-literal`
- m15 value-empty — f07 — `value-empty`
- m16 text equality→substring — f01 — `text`
- m17 source check removed — f02 — `source`
- m18 source containment relaxed to `b12177` — f03 — `source`
- m19 derived scope (set_examples) — f04 — `derived`
- m21 decision set equality→subset — f08 — `setter-set want=20 got=21`
- m22 decision header (parameter cell) — f17 — `header`
- m23 decision-names — f18 — `decision-names`
- m24 decision id-uniqueness — f09 — `cells` (R19 replaced by a second R18; pristine dbound=1, mutant dbound=2)
- m28 condition-empty — f14 — `condition-empty`

F3 NOTE — the one tightening mutant m27 (`startswith("## ")`→`startswith("##")`, `counter.M2.py:130`) is killed
strict: a `#### note` line inserted inside the section makes the mutant stop reading (49 rows bound, 43 missing,
decisions 0/2, met=False) while the pristine counter accepts the same input unchanged (92 bound, met=True,
`runs/forge-pri-f15_subheading.out` vs `runs/forge-m27-f15_subheading.out`). The real parser is robust here.

F4 NOTE — four mutants survive both detectors; each is provably inert, so no forgery exists:
- m20 `opts[0]`→`opts[-1]` (`:210`): all 34 `common/arg.cpp` population rows enumerate to 11 `arg_block=None`,
  23 blocks with exactly one distinct long option, 0 with two (`runs/m20-equivalence.txt`); no row can distinguish.
- m25 `MIN_POP=90`→1 (`:57`): population is fixed at 92 by the sha256-pinned archive; a different archive is
  rejected before grading (`counter.M2.py:159`). Latent only for a future pin bump, not observable at M2.
- m26 duplicate check removed (`:222`): not load-bearing for accept. Accept needs `bound==n ∧ missing==0`; a
  duplicate shares a key, so distinct keys < bound = n, hence missing>0. f20 (93 rows: mutant
  `SETTER_SWEEP 92 93 2 93 0 0 0 0 … decisions=1/2 met=False`, pristine `dup=1 met=False`) and f20b (92-row swap:
  mutant missing=1 met=False). Only diagnostics differ (`duplicates=0` vs 1).
- m29 `len(prow)==n` removed (`:352`): implied by `bound==n ∧ unbound==0` because `len(prow)=bound+unbound`;
  f20, f20b and f21 (91 rows, bound=91) all give met=False (`runs/forge-m29-*`).

F5 NOTE — no false green was found in the frozen oracle: the pristine counter rejected all 20 forged row/decision
inputs (f01–f14, f16–f18, f20, f20b, f21) and accepted only the valid f15; rejection reasons and mutant `met` are in
`runs/evidence.txt` and `runs/summary.txt`.

F6 DEFECT — the C2 control receipts named by `plans/round-94-claims.md` and by this seat's spec are not present at
round 94. `git ls-tree -r 285f1783 -- .ufo/waves/round-94` is empty; `git ls-tree -r 6aa5fa6b -- .ufo/waves/round-94`
contains only `controls/c2-build-candidate.py`; the working tree likewise has only that file plus `measured/c1.out`
and `measured/c2.out`, which are absent from both commit trees (they are indexed by the jj-synced working copy, not
committed). `controls/c2-base.out`, `controls/c2-forgeries.py/.out`,
`controls/c1-base.out`, `controls/sources-opened.out`, `controls/harm-base.out`, `controls/census-start.out`,
`controls/c2-rows.md` and `controls/c2-section.md` are absent (a repo-wide glob finds same-named files only in
rounds ≤93). The counter's behaviour is unaffected, but the claims' "committed with it" sentence and the seat's
receipt list do not match the tree; my forgery set is the only executed adversarial control for C2's gates.

F7 NOTE — control mode is not distinguishable by exit code: with `--skill-file`/`--sources-file` the counter prints
`met=True` and still exits 1 (`counter.M2.py:357`), so Detector A compares stdout, not rc. Without the overrides it
exits 0 with identical stdout (command 4). A receipt consumer must not read rc 1 as a failed predicate when the run
used control files.

## Deliverables (all under `.ufo/waves/round-94/w1/out/MT02SetterCounterMutants/`)
- `counter.M2.py` (`49c5d0cb…`), `SKILL.M2.md` (`9eecd40c…`), `SOURCES.M2.md` (`07878961…`).
- `mutants/m01.py`…`m29.py` (per-file sha256 in `runs/manifest.sha256`), `mutation-run.py`, `extra-probes.py`,
  `equivalence-m20.py`, `diffstat.py`, `summarize.py`, `evidence.py`, `restore-check.sh`, `rerun-check.sh`,
  `predicate-check.sh`.
- Receipts: `runs/summary.tsv`, `runs/summary.run1.tsv`, `runs/summary.run2.tsv`, `runs/mutation-run.stdout`,
  `runs/forge-pri-*.out`, `runs/forge-m*-*`, `runs/m01.outing`…`runs/m29.outing`, `runs/baseline.out`,
  `runs/restored.out`, `runs/predicate-nofiles.out`, `runs/m20-equivalence.txt`, `runs/mutant-diffstat.txt`,
  `runs/forges.diff.txt` (the exact forged cell edits; forge inputs are regenerated deterministically by the two
  driver scripts), `runs/evidence.txt`, `runs/summary.txt`, `runs/manifest.sha256`.

VERDICT: holds — all 25 behaviour-bearing mutants are killed (8 by the committed control, 16 by forged rows, 1
strict), the 4 survivors are provably inert, and the frozen counter reproduces `measured/c2.out` byte-for-byte and
accepts no forged row.
