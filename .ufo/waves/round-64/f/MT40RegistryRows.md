# MT40RegistryRows — C2 registry-row falsification (round 64, wave f)

Seat: MT40RegistryRows (mutation-tester, leaf). Milestone: falsify C2. Judged on: calibration.
Tip under test: `23b3fdb1a925129a9961cf551f6d40bf251602cb` (the measured tip).
Instrument under test (unmutated throughout): `tools/round64-c2-counter.py`
sha256 `c8b725e57f6e761735e832d127ec6df622d4a9dff09893b5fa31131c64d93e2e`.
Lane files touched by me: **none** (read-only lane; every edit was in my own scratch clone).
Evidence: `.ufo/waves/round-64/f/out/MT40RegistryRows/` (index: `evidence-summary.md`).
Tools installed: none — python3 / git / pgrep / bash only, all preinstalled. No pacman
transaction (pacman is PAUSED host-wide).

## Method

One mutant commit per registry edit in a `--shared` clone of the lane at the measured tip;
each committed tip is scored by the **unmutated** counter run from `$D/tools/` with
`--repo $D --tip <committed tip> --work <fresh scratch>` (fresh dir per run, deleted after).
Baseline at the same tip and the same PATH: `met=True` (full line in
`out/BASELINE-pristine-tip.out`). Every mutant below is a single-field registry edit, so the
`registry:` line on the counter's stderr names the deciding field.

## Result: the nine mandated mutants are all KILLED

| # | mutation (registry/capability-claims-r64.tsv) | verdict | deciding field (counter stderr) |
|---|---|---|---|
| M01 | swap rows 1 and 2 `run` templates | **KILLED** | `registry: run:sources-registry`, `registry: run:ollama-offline-evidence-replay` → `covered=10/12`, `errors=2` |
| M02 | shorten row 1 `quote` below the 8-char floor (`Curate`) | **KILLED** | `registry: quote:sources-registry` → `covered=11/12`, `errors=1` |
| M03 | change row 1 `observed` to `FORGED-OBSERVED` | **KILLED** | `registry: observed:sources-registry` → `mismatches=1` |
| M04 | duplicate row 1 | **KILLED** | `registry: dup-row:sources-registry` → `errors=1` |
| M05 | row 1 `pattern` → `usage:` (a line the tool prints regardless) | **KILLED** | `registry: pattern:sources-registry` → `covered=11/12`, `errors=1` |
| M06 | add a 13th capability row | **KILLED** | `registry: unbound-cap:extra-capability` → `errors=1` |
| M07 | remove the `outcomes` column | **KILLED** | `registry: header` → `covered=0/12`, `errors=1` |
| M08 | change row 1 `binding` word (`census`→`scan`) | **KILLED** | `registry: binding:sources-registry:scan` → `covered=11/12`, `errors=1` |
| M09 | put a TAB inside row 1's `quote` cell | **KILLED** | `registry: cols:10` → `covered=11/12`, `errors=1` |

Counter one-liners (M01-M09; each ends `met=False`, exit 1):

```
M01 tip=d1e2796a2a10 population=12 covered=10/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=2 ... met=False
M02 tip=792883bd68b7 population=12 covered=11/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=1 ... met=False
M03 tip=c7c64b1b951f population=12 covered=12/12 mismatches=1 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 ... met=False
M04 tip=f817fc4a6328 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=1 ... met=False
M05 tip=31614f6e31f1 population=12 covered=11/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=1 ... met=False
M06 tip=5c3b44edadde population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=1 ... met=False
M07 tip=f92751c99c2c population=12 covered=0/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=1 ... met=False
M08 tip=0766af9103d4 population=12 covered=11/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=1 ... met=False
M09 tip=00277fe087fb population=12 covered=11/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=1 ... met=False
```

(The `controls_rejected=0/120` in each is the counter's own design: control credit is withheld
while the baseline is unmet — `note: baseline not met - control credit withheld`. The gate that
kills each mutant is the `covered`/`errors`/`mismatches` field the `registry:` line names.)

Two further mutants the same instrument also kills, showing the checks are not one-deep:
M13 (swap two rows' `pattern` cells) → `registry: pattern:sources-registry` + `pattern:ollama-offline-evidence-replay`;
M14 (drop `host-busy` from the context-capacity row's `outcomes`) → `registry: outcomes:context-capacity-receipt`;
M16 (duplicate row with conflicting content) → `registry: dup-row:sources-registry`;
M19 (`verdict=false`) → `registry: verdict-value:sources-registry:false`;
M22 (rename row 1's `cap` to another bound cap) → `registry: quote:pin-watch` + `dup-row:pin-watch`;
M25 (`verdict=host-busy` on a single-outcome row) → `registry: hostbusy-not-declared:pin-watch`;
M26 (row 1 quotes another capability's text) → `registry: quote:sources-registry`;
M15/M23/M24/M18/M20 (TAB in `observed`; context-capacity `verdict`/`observed` crossed) →
`registry: cols:10` and `registry: observed:context-capacity-receipt` → `mismatches=1`.
All KILLED, met=False.

## Result: three mutant classes SURVIVE (coverage findings, not claim verdicts)

These are survivors of the *instrument*, at `met=True`. They are reported as findings; I judge
no claim.

**S1 — M10: the recorded `verdict` of the two-outcome row is never compared with the live
outcome.** The context-capacity row's `verdict` cell was changed from `host-busy` to `true` and
its `observed` cell from `host-not-idle-before-K1` to `"all_ports_closed": true`. The counter
accepts it: `registry: ` (nothing), `gate-misses: []`, `met=True`, while its own live run of that
row reports `tip=host-busy` (the measured host is busy — the operator's `llama-server`s are up).
```
M10 tip=effa7691c9ec population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 ... met=True
   | gate-misses: []
   | row context-capacity-receipt: tip=host-busy(22.5s) regress=flipped printer=(True, 'regress-inapplicable')
```
Reproduced twice (initial run and confirmation rerun, `out/M10-*.rerun.out`): `met=True` both
times. Mechanism (`tools/round64-c2-counter.py:570-586`): the recorded `verdict` is checked only
against the row's *declared* outcome set (`rec not in spec['outcomes']`), and the live outcome is
checked only against the same declared set (`outcome not in spec['outcomes']`); nothing compares
the two. The row's `observed` cell is checked against `want_observed(spec, rec)` — i.e. against the
*recorded* verdict, not the *live* one. So the registry can claim the idle outcome on a host that
measured busy, and the counter still scores the row as met. Scope: only rows with two declared
outcomes can show this (the other 11 have one outcome each, so recorded and live coincide).
M23/M24 show the counter does catch a *mixed* pair (recorded verdict `true` with the busy
`observed` text, or vice versa) via `observed:context-capacity-receipt`; S1 is the consistent
pair, which is exactly the dangerous direction. Note the freeze's own wording for the row
("the recorded verdict is the outcome at the measured host") is a property the instrument does
not enforce for this row.

**S2 — M11 / M21 / M29 / M30: the `note` column is parsed but never graded.** Rewriting the
context-capacity row's `note` to a false statement ("the idle outcome was observed live on the
measured host; no copy of the tool was run"), rewriting every row's note, or emptying the
context-capacity note, all score `met=True` with `gate-misses: []`:
```
M11 tip=2edabc836073 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 ... met=True
   | gate-misses: []
```
Mechanism: `note` is in `COLS` (line 198) and is parsed, but `score()` (lines 544-597) never
reads `row['note']`, and no control family references it. The `note` is where the row states the
outcome semantics in prose, so a registry whose prose contradicts the machine-checked facts
scores identically to an honest one. This is a documentation-drift exposure, not a way to make a
false claim pass: every graded field still has to match.

**S3 — M12 / M17 / M27: the `quote` cell is a free substring of the canonical row prefix.**
Replacing row 1's `quote` with a different ≥8-char substring of the same canonical prefix
(`Curate where kama learns`), with a prefix fragment (`| sources-registry`), or with exactly the
8-character floor string, all score `met=True` (`gate-misses: []`). Mechanism
(`tools/round64-c2-counter.py:554-556`): the check is `row['quote'] not in spec['prefix'] or
len(row['quote']) < 8` — the quote only has to be *some* ≥8-char substring of the canonical
row's prefix, so it does not pin which sentence of the capability the registry row refers to.
M26 (a quote from a *different* capability) is KILLED, so the quote still binds the row to the
right capability; what survives is the intra-row ambiguity.

**S4 — M28: row order is not graded** (reversing the 12 rows scores `met=True`). Noted for
completeness; the registry is read as a set of rows, so this is benign.

## Result: the 12 patterns are unique to the success path

Each bound tool was run in two failing modes and the row's pattern shown absent
(`out/pattern-uniqueness.txt`, complete transcript):

* **Bad-argument mode** (argparse/usage rejection), all 12 rows: pattern **absent**, rc=2.
* **Work-stage failure** (the tool runs, then fails at its work — model digest mismatch,
  unreadable model, unreadable captures, bad GGUF magic, missing pins file, missing contract,
  missing receipts, a failing command): pattern **absent** in all 11 rows that have such a
  reachable mode.

Two honest caveats found while probing, both outside the registry rows:

* The **context-capacity** row's pattern `"all_ports_closed": true` is *printed by the refusal
  path too*: the host-busy refusal emits `{"all_ports_closed": true, "cells": 0, ...}` with
  `rc=2`. The counter does not rely on the bare pattern for this row — `idle_check`/`busy_check`
  require exit code 0 plus receipt cells/observed/host_idle fields — so the row is still graded
  correctly (the counter's live run of it is `host-busy`, correctly classified). The registry
  cell is still the quoted `"all_ports_closed": true`, i.e. the pattern is not by itself
  success-unique for that one row.
* The two scan rows share the pattern `unknown=0`, which is also printed by a scan that
  classified **nothing** (an empty document population yields `tokens=0 … unknown=0`, rc=0).
  The counter's `eol` anchoring and the row's own `tokens>0` population at the tip keep this
  from being a live false positive (the tip scan sees 149 and 2094 tokens), but the pattern
  alone does not prove the scan examined anything.

## Restoration evidence

The clone's working-tree registry is byte-identical to the base blob, and the lane is untouched:

```
sha256 clone working tree : dfdad95562914de3b0f8d2584d1244b86e02378376f524e188fd0fb0cfb375af
sha256 base blob (23b3fdb): dfdad95562914de3b0f8d2584d1244b86e02378376f524e188fd0fb0cfb375af
sha256 lane registry       : dfdad95562914de3b0f8d2584d1244b86e02378376f524e188fd0fb0cfb375af
git -C <lane> status --porcelain -- registry/ tools/   ->  (empty)
```
No commit, no push, no mutating git/jj command in the lane; no `git add` in the lane; no
`llama-server`/`ollama` process of mine was left running; every `--work` was deleted after its
run; the scratch root `/fast/scratch/hyaku/kama-r64/f/MT40RegistryRows` is removed before yield.

## Summary

The nine mandated registry-row mutations are all KILLED, each by the specific field named on the
counter's stderr (`run`, `quote`, `observed`, `dup-row`, `pattern`, `unbound-cap`, `header`,
`binding`, `cols`), and all twelve patterns are absent from their tool's failing modes. Four
survivor classes are reported above as coverage findings for the L1 to weigh, not as verdicts:
the two-outcome row's recorded verdict is not compared with its live outcome (S1), the `note`
column is ungraded (S2), the `quote` cell is a free ≥8-char substring of the canonical prefix
(S3), and row order is ungraded (S4).

Baseline counter line at the measured tip (the item's requested one-liner):

```
tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True
```
