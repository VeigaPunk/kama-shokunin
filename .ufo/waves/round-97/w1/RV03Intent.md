# RV03Intent — round 97 w1: what the budget counter enforces, and whether round-97's controls can be gamed

Seat `RV03Intent`, lane `kama-shokunin`, wave `round-97/w1`. Attack only: no tracked lane file was
edited, no frozen predicate changed, no `git add/commit/stash/checkout` in the lane. Every command
below was run against revs read from the lane (`git show`) or against a `--shared` clone inside
`/fast/scratch/hyaku/kama-r97/RV03Intent/` (deleted before yield; receipts copied here).

Revisions named:

| name | rev | what it is |
|---|---|---|
| base | `40763bd2ca1e3f99881247eaa9f5e3ef3b596653` | round-96 close (the rev every control receipt names) |
| freeze | `9e605d416c199b3c9913a2125b04f9c5a16f5668` | round-97 freeze commit (three counters + plan) |
| HEAD | `e057166e09ec069725bd0b0433fc50275ecd03ea` | round-97 amendment 1 (C2 host-speed parameter) |
| probe bytes | base `11e5b01b…` / freeze+HEAD `0897ebff…` | `sha256` of `tools/kama-probe.sh` |

`git diff 40763bd2 9e605d41 -- tools/kama-probe.sh` is **comment-only** (+14/−8 lines, all inside the
`MAX_STEPS` comment block). The executable parser is byte-identical between base and freeze, which is
what makes the base-rev control receipts transferable to the freeze probe — an inference, stated as
such, not something a receipt asserts.

## 1. What the round-96 counter was built to enforce

`tools/round96-router-budget.py` (512 lines) enforces one sentence: **a candidate's verdict is a pure
function of its bytes, not of the host clock and not of a constant pass wrapper**. Its 13 cells encode
that:

- W01/W02/W03 (1/8/40 distinct slow files) grade the *whole listing*; W03 is the round-94
  `timeout 60`-wrapper discriminator and is guarded by `w03 >= 1.25 x 60 s` (`:431`, `:472`), exiting
  2 rather than claiming a discriminator that does not exist on this host;
- W11 (`mid.gguf`, 700 000 tensors) is the MAX_STEPS-vs-constant-6 discriminator (`:196`);
- W12/W13 are the two disclosed undecidable cells (`-`), W09 the MAX_TENSORS cell;
- W10 is the file-identity (ctime) cell;
- every cell is graded at **two** host loads and `positive_mismatches` separates the disclosed cells
  (`W09`, `W12`) from hard ones (`:490-495`).

Its own oracle, however, still carried the false constant: `if n_tensors > 833_333: return "-"`
(`tools/round96-router-budget.py:222`) — the round-96 counter *itself* encoded the constant-6 ceiling
its docstring had just been corrected about. That is the defect round-97's oracle removes.

## 2. Behavioural difference table (96 → 97)

| dimension | round96 | round97 |
|---|---|---|
| cells | `CELLS = 13` (`:95`) | `CELLS = 17` (`:142`) + `LEGACY_CELLS`/`NEW_CELLS` (`:143-148`) |
| fixtures | `gguf()` single-dim only (`struct.pack("<IQIQ", 1, elems, 0, off)`) | `gguf(nd=…)` (`:265`); four new fixtures `t900k`, `mid4`, `t833333`, `maxmeta` (`:429-437`) |
| oracle (`fixture_class`) | flat `n_tensors > 833_333 → "-"` (`:222`) | `steps = 4 + T*(5+nd)` vs `5_000_000` (`:325-326`) + `maxmeta` size branch (`:313`) |
| cell set | always all 13 | `--cells {all,legacy,new}`, filtered at `:502`; new-only forces `n_slow = 0` (`:466-470`) |
| W10-rewrite | unconditional | gated on `slow` and on the selection (`:513`) |
| mutation machinery | none | `MUTANTS` byte patches; each anchor must occur **exactly once** or `CannotEvaluate` (`:246-`/`:612-620`) |
| control mode | none | `--control/--expect`; `runs = 1` forced (`:588`); returns before the MARGIN guard and before the load pass (`:619-630`) |
| usage guard | none | `--control` needs `--expect`; `caught` needs a mutant → **exit 64** (`:585-587`) |
| exit-0 condition | `len(cids) == CELLS` (13) | `len(cids) == want_cells`, `want_cells = 17` or `len(selected)` (`:670-680`) |
| summary fields | `cells, mismatches, positive_mismatches, load_cells, load_stable, budget, probe, probe_sha256, base_sha256, rev, w03_seconds, load1_nat, burners` | **identical set, no new field**; `load_cells` still `len(cids)` = union size (`:671-676`) |
| `--runs` validation | none (`:431`) | none (`:588`) |
| `--probe-file` | present, `mode="override"` | present, `mode="override"` (`:607-608`) |

Two inherited holes survive the rewrite unchanged: `--runs` is never validated (`--runs 0`,
`--runs -7` accepted), and `--probe-file` substitutes arbitrary bytes for the probe under claim with
only the `probe=`/`probe_sha256=` fields recording it.

## 3. Gaming attempts and outcomes

All runs below are real; each left a receipt in this directory. `+1`/`+2`/fake probes were built in
scratch from `git show 40763bd2:tools/kama-probe.sh` with an asserted unique anchor.

| # | attempt | command (lane root) | outcome |
|---|---|---|---|
| R2 | the frozen 17-cell predicate with **no probe run** | `--runs 0 --allow-clock --burners 0` | **`cells=17 mismatches=0 positive_mismatches=0 load_cells=17 load_stable=1 … w03_seconds=0.0 burners=0`, exit 0** |
| R3 | probe that overcharges **+1 step/tensor header**, 4 new cells | `--cells new --control --expect survived --mutant none --probe-file plus1` | `cells=4 cells_ok=4 survived=1 … ok=1`, exit 0 |
| R4 | same `+1` probe, **all 13 legacy cells** | `--cells legacy --control --expect survived --mutant none --probe-file plus1` | `cells=13 cells_ok=13 survived=1 … ok=1`, exit 0 (W11 green, W03 74.86 s) |
| R5 | hand-written probe with **no GGUF parse and no budget**, 4 new cells | `--cells new --control --expect survived --mutant none --probe-file fake` | `cells=4 cells_ok=4 survived=1 … probe=override … ok=1`, exit 0 |
| R6 | honest negative control: `flat6` on the new cells | `--cells new --control --expect survived --mutant flat6` | `cells_ok=3 survived=0 caught=1`, exit 1 — control mode does discriminate |
| R8 | probe that overcharges **+2 steps/header**, 13 legacy cells | `--cells legacy --slow-files 8 --control --expect survived --mutant none --probe-file plus2` | `cells=13 cells_ok=12 survived=0 caught=1`, exit 1 — W11 is the sentinel |
| — | C1 and C3 on the `+1` probe | scratch clone, commit `ef60fd43` over `e057166e` | `SELF_ASSESS97 checks=14 mismatches=0 met=True` and `DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True`, both exit 0 |
| — | exit-code probes | `--rev deadbeef … --control` / `--control` alone / `--control --expect caught --mutant none` / natural `--cells new` | 2 / 64 / 64 / **2** (the MARGIN guard fires at `w03=0.0`) |

Receipts: `rv03-zerorun17.out`, `rv03-newcells.out`, `rv03-legacy-plus1.out`,
`rv03-legacy-plus2.out`.

### 3.0 The three hypothesised skip vectors, checked

- **A cell skipped.** No path. `cells = [c for c in cells if c[0] in set(selected)]` (`:502`) only
  narrows to the *named* set, and every cell in the narrowed list is graded. A cell missing from one
  pass surfaces twice: `cells=len(cids)` shrinks and the missing key degrades to
  `(False, [], "-", "-")`, which trips `load_stable=0` and a mismatch. In control mode a skipped cell
  would raise `survived` (smaller `n`), but the only narrowing input is `--cells`, whose effect is
  printed in the same line as `cells=<n>`. Not exploitable without editing the counter.
- **A fixture class the oracle mislabels.** Cannot make a cell green. `fixture_class` is consulted
  only by `build_fixtures` (`:440-445`); the cell expectations are the hardcoded
  `(verdict, reason)` tuples (`:480-500`), so a disagreement raises `CannotEvaluate` → exit 2 and a
  cell verdict never consults the oracle.
- **A mutant patch that silently does not apply.** Refused: `apply_mutant` raises unless the anchor
  occurs exactly once (`:612-620`). Run: `--control --expect caught --mutant flat6 --probe-file
  fake-probe.sh` → `could-not-evaluate: mutant flat6: anchor appears 0 times, not exactly once`,
  exit 2. Residual risk: an anchor occurring once in dead text (comment/string) instead of live code —
  for all four mutants the anchor is live (`grep -c` for the `def need(n):` anchor in the probe = 1,
  and it is the only `need()` used by the tensor loop).

### 3.1 The `survived=1` string proves nothing on its own (R2, R3, R4, R5)

`survived = int(n_ok == n)` (`tools/round97-router-budget.py:624`) and
`ok = survived if a.expect == "survived" else caught` (`:626`) with `return 0 if ok else 1` (`:630`).
There are four ways to reach `survived=1 … ok=1`/exit 0 without the probe under claim having the
intended arithmetic, all of them through documented flags:

1. **`--mutant none`** — the usage guard only rejects `caught` with `mutant == "none"`
   (`:585-587`), so `--control --expect survived --mutant none` is legal. R3/R4/R5 are exactly that
   shape: `survived=1 … mutant=none … ok=1`, exit 0. Byte-shape-wise these are the same lines the
   plan quotes, differing only in `mutant=` and `probe_sha256=`.
2. **`--probe-file`** — `mbytes, mode = a.probe_file.read_bytes(), "override"` (`:607-608`). A 40-line
   probe that never parses a GGUF header and has no step budget at all (it answers `MODEL_OK` for
   files under 100 MB) survives the four new cells (R5). The four new cells therefore prove the cells
   are *necessary*, not that the graded probe has the arithmetic.
3. **`--runs 0`** — `good = all(...)` over an empty run list is `True`, so every cell prints `ok=1`
   with no `runN=` detail. In natural mode the only thing that catches this is
   `if not a.allow_clock and w03 < MARGIN * BASE_WRAPPER` (`:633`); `--allow-clock` — a flag whose
   help text exists to grade a *round-94* probe — disables it. R2: the exact frozen summary string,
   `cells=17 mismatches=0 … load_stable=1`, exit 0, with the probe invoked for **1 of 17 cells**
   (W10-rewrite runs its three invocations unconditionally). The one tell in the summary is
   `w03_seconds=0.0 burners=0`.
4. **`--cells new`** in natural mode is never green without `--allow-clock` (the MARGIN guard fires at
   `w03 = 0.0` because W03 does not exist in a new-only pass) — so the selector is not by itself a
   green-receipt generator.

A fifth route is *latent* and not reachable through the CLI: with an empty selected set the same code
prints `survived=1` (0 == 0) and exits 0. The selection can never be empty today (new cells are added
unconditionally at `:480`; the legacy branch forces `n_slow = max(8, n_slow)` at `:467`), so this is
a missing guard, not a live hole.

### 3.2 The counter cannot see a per-header overcharge (R3, R4, clone)

`+1` step per tensor header is a one-line patch that changes no parse semantics (an extra
`steps[0] += 1` beside `tt, off = u32(), u64()`). Its true ceiling is
`(5,000,000 − 4) // 7 = 714,285` at nd=1, not the `833,332` that `SKILL.md:2453` states and that
`tools/round97-router-budget.py` docstring repeats. Result: **all 17 cells green** (R3 new, R4 legacy,
including W11, the tightest legacy sentinel: 700,000 × 7 = 4,900,004 ≤ 5,000,000, still `invalid`).

Why no counter sees it:

- W17 (`833,333` at nd=1, `5,000,002` vs `5,000,000`) has **2 steps** of headroom, so it can only catch
  *under*charges; an overcharge only moves the file further past the cap;
- `W14`/`W15` are 400,004 and 1,300,004 steps past the cap — insensitive to ±1;
- `W16` is a `MAX_META` cell, not a step cell;
- C1's arithmetic checks are **substring tests on the probe text** (`:143` `"5 + nd" not in probe`;
  `:151` `want not in probe`), so a comment that says `5 + nd` over a parser that charges `6 + nd`
  passes;
- C3's row check recomputes with the formula *literal* `PREAMBLE + t * (5 + nd)`
  (`tools/round97-depth-boundary-audit.py:103`) against the probe's `MAX_STEPS` only — it never binds
  the table to the parser's charges, so the table stays "consistent" with a false `5 + nd`.

So: **`--control --expect survived` can print `survived=1` for a probe whose arithmetic is wrong**
(R3/R4), and **a false self-assessment still passes C1 and C3** (clone run, both `met=True`). The
plan discloses exactly this class —
C2 "Disclosed limits (a) … a probe that charges a wrong number of steps inside a single header is not
graded" — so C2 is honest about the gap; the gap is that C1's and C3's predicates are worded so that
the same probe satisfies them. "Does every row recompute from the probe's `MAX_STEPS`?" is true; it is
just not the question depth needs.

The window is exactly +1 step/header. `+2` gives 700,000 × 8 = 5,600,004 > 5,000,000, which flips W11
from `invalid` to `-`: run R8 (`--cells legacy --slow-files 8 --control --expect survived
--probe-file plus2`) returns `cells=13 cells_ok=12 … survived=0 caught=1`, exit 1, with the only red
cell being `W11-700k ok=0 want=MODEL_UNLOADED/router-model-invalid
run1=MODEL_OK/router-unloaded-autoload`. So the legacy set's overcharge sentinel is W11, and it fires
one step later than the new cells would.

### 3.3 Exit codes

| situation | code | evidence |
|---|---|---|
| predicate met | 0 | R2 |
| any cell red / a mutant survives on the new cells | 1 | R6 |
| fixture `fixture_class` disagreement, unresolvable rev, missing probe, stub never accepts, anchor not unique, probe still on a wall clock | 2 (`CannotEvaluate`) | `--rev deadbeef` → 2; `measured/c2.out` (W03 guard) → 2; `--mutant flat6 --probe-file <no-anchor>` → 2 |
| any other exception (e.g. `PermissionError` on the work dir) | 1 (uncaught traceback) | `--work <chmod 500 dir>/x` → `PermissionError`, exit 1 |
| `--control` without `--expect`, or `caught` with `mutant none` | 64 | run |
| **empty selected cell set** | **0** (`survived=1`) | latent, unreachable via CLI |
| **`--runs 0`** | **0** with zero probe invocations | R2 |

So: a fixture-build failure is never 0 (2 or 1), and `--control` cannot be driven to 0 by an empty
cell set through the CLI; but the *natural* predicate can be driven to 0 with no probe execution.

## 4. Do the control receipts prove what the plan says?

`plans/round-97-claims.md` §C2 claims: the predicate string at M2, plus "the three control receipts
print `survived=1` for the 13 legacy cells and `caught=1` for the three new cells, one per mutant".

**What holds.** I recomputed every `probe_sha256` in `controls/c2-legacy-mutants.out` and
`controls/c2-new-mutants.out` from `git show 40763bd2:tools/kama-probe.sh` and the counter's own
`MUTANTS` table: five of five match exactly (`mutant=none` → `11e5b01b…`; `flat6` → `14efbe6f…`;
`undercharge` → `2e31ff3b…`; `maxmeta` → `6b5f6db4…`; `nopreamble` → `9035b55e…`). The receipts are
therefore authentic: those exact bytes ran, and the 13 legacy cells were all green under each forgery
(`cells=13 cells_ok=13 … survived=1`) while each forgery turned at least one new cell red
(`cells=4 cells_ok=1..3 … caught=1`). For `flat6` and `maxmeta` the intended cell is the *only* red
one (W15 / W16); `undercharge` and `nopreamble` take collateral reds (W14+W15+W17, and the same), so
`caught=1` is a "some cell caught it" statement, never a per-cell one — `caught=1` would also be
printed if an incidental cell (an `unparsed(rc=…)`) failed.

**What does not hold.**

- The sentence's own counts are false on both numbers: `CELLS = 17` (`tools/round97-router-budget.py:142`),
  `NEW_CELLS` has four members (`:147`), and the control evidence is **two files**
  (`controls/c2-legacy-mutants.out`: four `CONTROL` blocks, one per mutant;
  `controls/c2-new-mutants.out`: five — a `mutant=none` baseline plus the four mutants) — not "three
  control receipts … three new cells". The plan's own "Before"/"Do-nothing
  control" paragraphs and `claims.json` say **four**. The same wrong count is in
  `tools/round97-router-budget.py:13` ("Round 97 adds three cells past that:", followed by four
  bullets) and `SKILL.md:2443` ("the three graded forgeries" over a four-mutant set). The wave's own
  dispatch carries a *third* tally — `16 cells; W14/W15/W16 catch three probe mutants`
  (`.ufo/waves/round-97/w1-spec.json`, `w1-dispatch.json`). No counter reads
  the plan, the round-97 counter's docstring, the SKILL heading or the dispatch, so all of them
  survive a green C1. This is round-96's failure class (a false string beside a green counter) with
  the grader removed rather than inverted.
- `tools/round97-router-budget.py:93` states the W03 guard as ">= 1.5 x 60 s"; `MARGIN = 1.25`
  (`:157`) and the refusal message prints 1.25 (`measured/c2.out`). Copied verbatim from
  `tools/round96-router-budget.py:58`. Ungraded.
- The controls were run at **base**, not at M2. That transfers only because the base→freeze probe diff
  is comment-only (my `git diff`, above); it is not evidence the receipt carries.
- The four committed legacy `survived=1` receipts show W03 at 53.62 s, 59.11 s, 61.84 s and 70.95 s —
  every one **below** the 75 s margin (`MARGIN x BASE_WRAPPER`, `:633`) that the natural predicate
  requires on this host. Control mode returns before that guard (`:619-630`), so the legacy survival
  evidence and the natural predicate cannot be produced from the same host state; my own `+1` legacy
  run measured W03 at 74.86 s (still below the guard). This is consistent with amendment 1's
  `--slow-files 72`, not a defect in the survival claim (W03's role in a legacy control is just
  another green cell).
- **The C2 predicate has not been measured.** At `e057166e`,
  `git show e057166e:.ufo/waves/round-97/measured/c2.out` is byte-identical to
  `controls/c2-could-not-evaluate.out` (`diff` → identical) and ends `c2_exit=2`
  (`W03 natural pass 55.0s < 1.25 x 60s`). A `measured/` receipt that is a copy of the refusal under a
  measurement label is mislabelled, and it is the only receipt in that class without a `rev=` /
  `probe_sha256=` field, so it is not tied to any commit. Amendment 1 records this honestly and adds
  `--slow-files 72`; `git show --stat e057166e` confirms no `tools/` byte changed, so kill rule K1 is
  intact.
- `load_cells` is `len(cids)` over the **union** of natural and load keys (`:671-676`), so
  `load_cells=17` is printed even in R2 where the load pass graded nothing (`burners=0`,
  `w03_seconds=0.0`). A *short* load pass still trips `load_stable=0` and a mismatch (missing key
  degrades to `(False, [], "-", "-")`), so this is a label defect, not a false-pass hole.

At observation time (08:23–08:25) the working tree showed `M .ufo/waves/round-97/measured/c2.out`
(0 bytes) and untracked `measured/c1.out`, `measured/c3.out`, `controls/census-end.out` — a concurrent
seat is writing measurements. Everything above quotes committed bytes (`git show e057166e:…`).

## 5. Findings

| id | axis | severity | finding | file:line | command that shows it |
|---|---|---|---|---|---|
| F1 | calibration | block | the frozen C2 predicate, the counter docstring and SKILL's depth heading all say "three" new cells/forgeries/receipts where the counter has four and 17 cells | `plans/round-97-claims.md:76-77`; `tools/round97-router-budget.py:13,142,147`; `SKILL.md:2443` | `grep -n "three" plans/round-97-claims.md tools/round97-router-budget.py SKILL.md`; `grep -c ROUTER_BUDGET97_CONTROL .ufo/waves/round-97/controls/c2-new-mutants.out` (5) and `…c2-legacy-mutants.out` (4) |
| F2 | operability | high | `--runs 0` + `--allow-clock` yields the exact frozen summary and exit 0 with no probe graded | `tools/round97-router-budget.py:588,633,671-680` | R2 `rv03-zerorun17.out` |
| F3 | operability | high | `--control --expect survived --mutant none` is accepted, so `survived=1 … ok=1 exit 0` needs no forgery | `:585-587,624-630` | R3/R4/R5 |
| F4 | operability | high | `--probe-file` grades arbitrary bytes; a probe with no parser survives the four new cells | `:607-608` | R5 |
| F5 | calibration+depth | high | a +1 step/header overcharge passes all 17 cells and keeps C1 (`checks=14 mismatches=0`) and C3 (`rows=6 checks=8 mismatches=0`) green while `SKILL.md:2453`'s 833,332 ceiling is false of it | `tools/round97-router-budget.py:325-326`; `tools/round97-self-assessment-audit.py:143,151`; `tools/round97-depth-boundary-audit.py:103`; `SKILL.md:2453` | R3, R4, clone commit `ef60fd43` |
| F6 | operability | medium | `load_cells`/`cells` count the union, not the cells the load pass graded | `:671-676` | R2 (`load_cells=17 … burners=0`) |
| F7 | calibration | medium | C1 checks 13-14 are substring co-presence against lane-owned, un-pinned round-96 receipts; checks 7-8 are substring tests on the probe text | `tools/round97-self-assessment-audit.py:143,151,199-200` | `git log --oneline -- .ufo/waves/round-96/measured/{c2,c3}.out` (one commit: `f6122036`) |
| F8 | process | high | `measured/c2.out` at `e057166e` is a byte-identical copy of the refusal receipt (`c2_exit=2`); no `rev=`/`probe_sha256=` field ties it to a commit | `.ufo/waves/round-97/measured/c2.out`; `.ufo/waves/round-97/controls/c2-could-not-evaluate.out` | `diff <(git show e057166e:.ufo/waves/round-97/measured/c2.out) .ufo/waves/round-97/controls/c2-could-not-evaluate.out` |
| F9 | operability | low | no `n == 0` guard on the control summary: an empty cell set would print `survived=1` and exit 0 (unreachable via the CLI today) | `:624` | code read; `--cells new` forces new cells unconditionally (`:480`) |
| F10 | calibration | low | the counter's own docstring states the W03 guard as 1.5× where `MARGIN = 1.25` | `tools/round97-router-budget.py:93,157`; cf. `tools/round96-router-budget.py:58` | `grep -n "1.5 x 60\|MARGIN = " tools/round97-router-budget.py` |

## 6. Confidence and limits of this seat

- High: F1, F2, F3, F4, F6, F8, F10 (executed byte diffs and runs); F5's 17-cell survival and its
  +1/+2 window (R3, R4, R8 executed); F9 (code path read).
- Medium: the base→M2 transfer of the control receipts (comment-only probe diff, computed not
  receipted); the exact C1/C3 behaviour under a *different* arithmetic forgery (one probe variant
  tested — the +1 overcharge).
- Not claimed: the ctime memo shape, the slow `/props` verdict and the pass-level wrapper (all
  disclosed by the plan and out of this seat's scope); no probe was run against a live llama.cpp
  server.
- Tools installed: none. Scratch `/fast/scratch/hyaku/kama-r97/RV03Intent/` (clone, probes, work
  dirs) is removed before yield; the runs above left no state outside this directory.
