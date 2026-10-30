# CR05C2Fidelity - C2 freeze fidelity (round 64, wave f, seat CR05C2Fidelity)

Item: compare the C2-r64 predicate in `controls/freeze.txt` (lines 65-87) with the
`tools/round64-c2-counter.py` docstring (lines 6-38) and with what the code enforces, field by
field. Lane read-only. All runs and mutants are in clones of `23b3fdb1a925129a9961cf551f6d40bf251602cb`
under `/fast/scratch/hyaku/kama-r64/f/CR05C2Fidelity/`. Receipts: `out/CR05C2Fidelity/`.
Tools installed: none (stdlib python3, git, bash, pgrep). No pacman. No commit outside clones.

Counter sha256 at tip = `c8b725e5...93e2e`, matching the freeze's build disclosure.

## 0. Baseline

Unmutated run at the tip reproduces `controls/c2-prewave-tip.txt` byte-for-byte (string compare
of the `tip=` line: equal). Receipt `out/CR05C2Fidelity/tip1.out`. So the instrument is stable.
The ~24 s run includes the ~21 s host-busy wait, consistent with the disclosure.

## 1. Docstring vs frozen sentence (word-level diff)

The docstring header says the predicate is "identical to .ufo/waves/round-64/controls/freeze.txt".
It is not. Divergences:

| # | freeze.txt (C2-r64) | docstring (lines 6-38) | disclosed where |
|---|---|---|---|
| D1 | host-busy when the refusal's printed pid set "equals the counter's pgrep set at the same moment" | "is covered by the counter's pgrep observations and covers every pid present in both its before and after pgrep" | freeze 219-223 only, a trailing paragraph **absent from the tip's freeze.txt** (tip file is 194 lines; 0 hits for "C2 build disclosure") |
| D2 | "`all_ports_closed: true`" | "`all_ports_closed\": true`" (stray quote) | no |
| D3 | "while **its selftest keeps one** fixture that must still print `no-disclosure`" | "while **a** fixture that must still print `no-disclosure` does" | no |
| D4 | "(tally_disclosed=8/8; **base 1/8: `no-disclosure` for rounds 56-62**)" | "(tally_disclosed=8/8)" | no |

D1 is the only disclosed one, and its correction is not in the tip's freeze. At the tip, the
frozen text still demands a clause the code cannot meet (see §8). Impacted axis: calibration.

## 2. Field-by-field: frozen name -> enforcing lines

| field (frozen value) | enforced at | status |
|---|---|---|
| covered=12/12 | `score` 536-597, `reg_met` 599, `TARGETS` 204, `gate` 1047 | enforced |
| mismatches=0 | `score` 580-586 (outcome and observed); 204 | enforced. Counts two different things (live outcome, `observed` text), frozen text names one |
| pinned=13/13 | `PINS` 79-106 (= 12 manifest tools + RECON, verified by set equality); `check_pins` 338-352 (wrong-length table is `pin-table`); 1547 | enforced |
| regress_flipped=12/12 | `regress_plan` 646-682, `apply_regression` 626-644, `flip_status` 1022-1028, 1553-1564 | **enforced against a tip-owned table** (§3) |
| printers_rejected=12/12 | `printer_source` 779-801, `printer_status` 1030-1045, `printer_rejected` 1571-1595, count 1590-1591 | enforced, but the ctx printer is not the frozen "runs nothing" printer (§5); counts only reason `regress-inapplicable` |
| idle_ok=1 | `idle_check` 432-454, `busy_check` 456-484, `classify` 486-507, `idle_controls` 1200-1295, 1596-1601 | enforced; busy subset clause unenforced (§8) |
| work_reuse_refused=1 | `work_reused` 245-249, exit 2 in `main` 1461-1465, `work_controls` 1297-1317, 1611-1626 | enforced |
| closure_ptr=1 | `closure_check` 860-884, `closure_planted` 924-943, `planted_verdict` 945-957, 1606 | enforced |
| reconciler mismatches=0 (printed `recon_mismatches`) | `recon_eval` 814-830, `run_recon` 832-838, 1605 | enforced |
| tally_disclosed=8/8 | `tally_count` 961-968, `run_tally` 970, 1607 | enforced; base 1/8 is **unenforced** (D4) |
| errors=0 | `F['errors']` 1628 = registry errors + canonical problems only | **narrower than "errors"** (§6) |
| "each appear exactly once" (canonical list) | `canonical_rows` 289-311 scans `lines[start+1:start+40]` at 305 | **window-bounded, unenforced beyond line 40** (§7) |
| "with the frozen row prefix" | `canon_problems` 314-333, prefix check at 331 (`prefix:` tag); quote-prefix check in `score` at 555 | enforced |
| "its run template executed live in an allowlisted environment" | `Runner.run` env = PATH/HOME/LANG/LC_ALL/TMPDIR/PYTHONDONTWRITEBYTECODE | enforced |

Fields gated by the code but **not named in the frozen sentence** (extra conjuncts, none
disclosed in the tip's freeze):

- `deps_pinned=2` (`DEP_PINS` 109-113, `N_DEPS` 116, 1548, `TARGETS` 204). Pins
  `tools/round41-scorecard-reconcile.py` and `.ufo/waves/round-25/count-c2.py`, which the frozen
  13 do not include. Wave-b seat X01 disclosed it in its own build report ("stricter than the
  freeze"), not in freeze.txt. Killed by mutant 4 (§4).
- `tally_selftest=1` (1008-1017, 980-1005, 1383-1388, 1608). Not named.
- `sens_selftest=4` (`sensitivity_selftest` 391-405, 1609). Not named.
- `population` (1054, 1543). Forced to 0 whenever `canon_probs` is non-empty. Not named.

Printed but not gated (additions, not omissions): `tip=`, `recon[...]`, `tally[...]`, `families[...]`.

## 3. "the counter's own table": regressions are read from the tip (SURVIVED)

Freeze 72-73: "a planted one-line regression of the bound tool - **the counter's own table**".
No such table exists in the counter. `REGRESS = 'registry/capability-regress-r64.tsv'` (line 60)
is read from the tip (`blob(repo, tip, REGRESS)`, line 1487). It is not in `PINS` or `DEP_PINS`,
so the tip chooses both `find` and `replace`. The freeze's Fix list names
`capability-claims-r64.tsv` but not the regress table. The table entered at `bf0db9e3` (wave-b
integration) and is disclosed only at freeze 216 (post-tip).

**Mutant 1 (SURVIVED).** Tip table replaced by 12 rows, each `import argparse` ->
`import argparse; raise SystemExit(1)`. Every tool dies at import, so every verdict flips
without touching capability logic. Counter at mutant tip `114296e0c8dcbf95e4838a6a41e32850c34fdc55`:

```
tip=114296e0c8dc population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] families[...all full...] met=True
```

`regress_flipped=12/12` therefore attests that some tip-chosen edit flips each verdict, not that
the counter's own planted regression does. `regress_table_controls` 1722-1766 tests the table's
shape only.

## 4. Extra pins: deps_pinned is a load-bearing conjunct the freeze never publishes (KILLED)

**Mutant 4 (KILLED).** One comment line appended to `tools/round41-scorecard-reconcile.py` at
the tip (not a frozen bound file; no capability row runs it). Mutant tip
`e53826e415c72292a8ed1730cd262fb3198cd536`:

```
tip=e53826e415c7 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=1/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] families[] met=False
```

The frozen kill rule is "any field below its frozen value". A tip satisfying every frozen clause
can fail on a file the frozen sentence never mentions. Either the freeze should list 15 bound
files, or `deps_pinned` should be dropped from `TARGETS`.

## 5. "a printer copy ... runs nothing": the ctx printer fabricates a receipt

Freeze 74-75: "a printer copy of each tool (emits the row's pattern, **runs nothing**)".
`printer_source` 779-801 does this for 11 rows. For `context-capacity-receipt` it also writes a
fabricated idle receipt to `--out` (`cells=1, observed=1, all_ports_closed=true,
host_idle.ok=true, other_pids_seen=[]`). The docstring of `printer_source` (780-782) says so; the
frozen sentence does not. The frozen wording read literally is also unimplementable here: a
pattern-only ctx printer is rejected by the verdict function before sensitivity is checked
(`printer_status` 1036 requires the printer to be accepted first).

**Mutant 7 (KILLED, for an unfrozen reason).** Ctx printer rewritten to print the pattern only.
Tip `b1188dea89d13acbecefc703cb121972e9eceb2e`:

```
tip=b1188dea89d1 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=11/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[...met=True] families[] met=False
```
stderr: `row context-capacity-receipt: ... printer=(False, 'printer-not-accepted')`.

## 6. `errors=0` does not mean "no error"

`F['errors']` (1628) = registry parse and binding errors + canonical-list problems. It excludes
pin mismatches (`pin_probs`), dep-pin mismatches (`dep_probs`) and regression-table errors
(`rerrs`). Those are gated under other names, so no failure escapes the gate, but the printed
`errors=0` cannot distinguish a clean run from one with pin or regression errors. The kill rule
reads "any error".

## 7. "each appear exactly once": a 40-line window, and the duplicate survives (SURVIVED)

Freeze 66-68: the 12 capabilities "each appear exactly once in the newest canonical list". The
code parses `lines[start+1:start+40]` (305) and never looks further. The freeze does not define
the list's extent, so the window is an unfrozen bound.

Mutant series (all at tip-derived clones, same 23b3fdb1 base):

| mutant | edit | result | by which clause |
|---|---|---|---|
| 2 | dup row after the `### Planned` heading (outside the table) | KILLED, `met=False` | `recon_mismatches=1` |
| 3 | 31 filler rows + dup, dup at line 3357 (in window) | KILLED | `canon-missing`, `errors=1`, `recon_mismatches=2` |
| 5 | clean dup `live-ollama-lifecycle` right after row 12 (in window) | KILLED | `canon-dup` |
| 6 | 30 filler rows + dup at 3399 (out of window) | KILLED | `canon-missing: live-ollama-lifecycle`, recon 2 |
| 8 | 30 filler rows + dup at 3393 (out of window) | KILLED | `recon_mismatches=2`; the recon detail shows the **filler** rows (`note-0`...) cause it, so this kill is **confounded** |
| 9 | **28 prose spacer lines only, no new table rows**; dup at 3398 (out of window, same table section) | **SURVIVED: `met=True`** | none |

**Mutant 9 (SURVIVED), the clean result.** Tip `48e94308ae445ee3b157dec10af0cf6695a19dcc`:

```
tip=48e94308ae44 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] families[canon=4/4,...] met=True
```
stderr: `gate-misses: []`, no `problem:` line. The reconciler also reports `r41=0 ... caps=0 ... met=True`.
Only the duplicate's position changed, and the counter is silent. The control `canon-dup-row`
(1140-1163) inserts the duplicate immediately after its real row, so the declared control family
never exercises a duplicate past the window. Caveat: the duplicate sits after prose inside the
round-64 section, so a markdown renderer would show it as a stray paragraph. The freeze's "exactly
once in the list" is not defined to exclude that, and the counter's own list is the window.

## 8. The idle clause: code implements the disclosed rule, the frozen text is unsatisfiable

Freeze 76-79 requires the busy pid set to "equal the counter's pgrep set at the same moment",
which `other_pids_seen` (a union over the tool's ~21 s polling window, per X10) cannot meet. The
code implements the replacement rule from freeze 219-223: `busy_check` 456-484 requires only
`set(before) & set(after) <= set(seen)`. The code is right and the frozen sentence is wrong.

The docstring (lines 21-24) also says the printed set "is covered by the counter's pgrep
observations". `busy_check` has no such subset test. In-process check: `busy_check` returns
`(True, 'busy')` for a printed set `standing + [999999999]`, a pid the counter never observed. The
docstring claims a bound the code does not enforce.

## 9. Other behaviours the sentence does not state

- The idle outcome is proved with a PATH shim: a `pgrep` that exits 1 is placed first on PATH
  (`Runner.run` fake_idle, 725-737; `idle` path 1598-1600). Disclosed in freeze 216-219 via X10,
  not in the predicate sentence.
- `mismatches` counts two different failures (live outcome 583-584, observed text 586-587).
- `recon_mismatches` is printed under a name the freeze does not use ("reconciler mismatches=0").
- The closure conjunct is graded on fixture commits built by plumbing in a shared clone
  (`make_fixture_commit` 900-922). Faithful to "turns false on a planted stale pointer".

## 10. Smallest safe corrections

1. Regressions: embed the twelve `find`/`replace` pairs in the counter, or pin
   `registry/capability-regress-r64.tsv` in `PINS` (13 -> 14) and say so in the sentence.
2. Canonical window: scan to the next `## ` or `### ` heading instead of `start+40` (305), and add
   a control that places a duplicate past the window (mutant 9 as the control input).
3. `errors`: fold pin, dep-pin and regression-table problems into `F['errors']` (1628).
4. dep pins: name the two extra files in the freeze's sentence, or drop `deps_pinned` from `TARGETS`.
5. Printers: amend the sentence to describe the ctx receipt writer honestly. Pattern-only ctx
   printers need a verdict-function change, which is the larger fix.
6. Freeze text: move the idle correction (D1) and the base 1/8 clause (D4) into the C2-r64 sentence
   itself, and fix docstring D2/D3 and the false subset claim in §8.

## 11. Mutant ledger (this seat)

| # | edit (tip) | outcome | key line |
|---|---|---|---|
| 1 | tip regression table replaced (`114296e0c8dc`) | SURVIVED, met=True | 120/120 |
| 2 | dup row outside table (`d42b8346`) | KILLED | recon_mismatches=1 |
| 3 | 31 filler + dup, in window (`b48f4722`) | KILLED | canon-missing, errors=1 |
| 4 | comment in round41 dep file (`e53826e4`) | KILLED | deps_pinned=1/2 |
| 5 | clean dup in window (`e4b059b0`) | KILLED | canon-dup |
| 6 | 30 filler + dup out of window (`a1814f4d`) | KILLED | canon-missing (confounded by filler) |
| 7 | ctx printer prints pattern only (`b1188dea`) | KILLED | printers_rejected=11/12 |
| 8 | 30 filler + dup out of window (`fd8ab1e9`) | KILLED, confounded | recon from filler rows |
| 9 | 28 prose spacers + dup beyond line 40 (`48e94308`) | **SURVIVED, met=True** | gate-misses=[] |

Receipts: `out/CR05C2Fidelity/` (tip1, mut1-5, mut7-9 `.out`/`.err`, mutant tip shas).
Lane untouched. Clones and scratch removed at yield.

## 12. Counter line (unmutated tip, my run)

`tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True`
