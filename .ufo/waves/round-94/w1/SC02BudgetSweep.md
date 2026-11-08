# SC02BudgetSweep — round-94 C1 defect-class sweep (operability)

Seat SC02BudgetSweep, lane `kama-shokunin`. Revisions: base `e6f1dccecbad6dea44a129dabc928822c458e824` (claims' B), M1
`a27656a454b1a2364f8b6e55f42fbca8c2e86ee4` (C1 measured), M2 `6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623` (tip), F
`285f17832d0e26364366bbf19888d68f1838249b` (freeze). Host 32 cores, `load1` **155–443** throughout (quoted per timing cell). Swept
`tools/kama-probe.sh` @M1 and `tools/round94-router-budget.py` @M1 for verdicts still depending on host load/time or entry count — the r93 SC02
F1/F2/F3 class C1 claims to close. No lane file modified; fixtures in scratch + my out dir. `Report:` = this file.

## Commands and outputs (exit codes)

```
$ python3 tools/round94-router-budget.py --repo <lane> --rev a27656a4 --work <scratch>
ROUTER_BUDGET could-not-evaluate: fixture slow.gguf: base loader state '-', designed 'invalid'
COUNTER_EXIT=2                                   # <-- predicate wants 0
$ ... --rev e6f1dcce (claims' base)               # do-nothing control
ROUTER_BUDGET could-not-evaluate: fixture slow.gguf: base loader state '-', designed 'invalid'
COUNTER_BASE_EXIT=2
$ python3 harness/router_counterbase.py fx/counterfix/body.json files 0   # r92 BASE loader, 10x
0 -   0 -   0 invalid   0 -   0 -   0 -   0 invalid   0 -   0 invalid   0 invalid   # 4/10 invalid
$ # F2: SAME 400k file, SAME M1 probe, alternating runs
try0: state='0\t-' wall=15.44s load1=443.09 | try1: state='0\tinvalid' wall=11.01s load1=434.61
try2: state='0\t-' wall=15.51s load1=425.15 | try3: state='0\tinvalid' wall=10.24s load1=418.21
$ # F3: 40 distinct slow files (150k tensors each)
probe=probe_m1.sh rc=2 wall=60.69s load1=162.00 verdict=MODEL_OK router-unloaded-autoload
probe=probe_base.sh rc=0 wall=5.76s load1=155.68 verdict=MODEL_OK router-unloaded-autoload
$ # control: same listing, same load, wrapper timeout 60 -> 600
probe=probe_m1_wrapper600.sh rc=2 wall=232.09s load1=324.22 verdict=MODEL_UNLOADED router-model-invalid
$ # F5 paired: 63 fast-invalid + 1 borderline-600k listing, 192 burners
borderline_state=63  -   ->  probe_verdict=MODEL_OK router-unloaded-autoload
$ # same listing at ambient load (borderline decided invalid) -> MODEL_UNLOADED router-model-invalid
# same listing, ambient load (borderline decided invalid) -> MODEL_UNLOADED router-model-invalid
$ env -u PYTHONUNBUFFERED timeout 60 python3 router_m1.py <body> files 0..39 | wc -l   -> 0
$ timeout 60 python3 router_m1.py <body> files 0..39 | wc -l                           -> 40
$ # /props timing (M1 probe, 4 valid entries = the P01 positive-cell shape)
props_delay=0 -> rc=0 MODEL_OK router-unloaded-autoload;  props_delay=3 -> rc=0 same
props_delay=6 -> rc=2 MODEL_UNLOADED router-unloaded          # <-- false red (base identical)
fx/n400000: STEPS=2400004 headroom_vs_4M=1599996 | fx/n600000: STEPS=3600004 headroom=399996
fx/d20 (counter's own shape): STEPS=900004 headroom=3099996   # 6 steps/tensor
$ git cat-file -e 285f1783:tools/round94-router-budget.py  -> ABSENT at the freeze commit F
```

## Findings
**F1 — BLOCKER — the C1 predicate does not hold at M1 on this host: the counter exits 2, not 0.**
`round94-router-budget.py:513` sets `rp = probe_router_py(bbytes)` from `BASE = 5af79495` (line 105) — the **r92-era** probe, whose `MAX_STEPS,
DEADLINE = 4_000_000, time.monotonic() + 4.0` (`5af79495:tools/kama-probe.sh:563`) is a **single shared** 4 s deadline. The sanity gate (line 327)
asks that loader to classify the counter's *own* `slow.gguf` fixture (150 000 tensors = 900 004 steps, 3.9–5.0 s wall here); at this load the 4 s
shared deadline expires mid-parse, the loader answers `-`, and the gate raises `CannotEvaluate` → exit 2. The gate is a coin flip (6/10 runs `-`) and
runs **before** any cell, so the counter never prints `ROUTER_BUDGET cells=19 … load_stable=1`. The committed receipt `measured/c1.out` was produced
where the fixture happened to parse inside 4 s (`load1_nat=232.08`); here the predicate is unreachable. Same exit-2 at base `e6f1dcce` → not an M1
regression; the counter cannot evaluate at either revision on a loaded host. The counter's `BASE` is also **not** the claims' base `e6f1dcce` (whose
probe likewise has a shared 4.0 s deadline, `e6f1dcce:…:563`), so the gate is unsound under either choice.
**F2 — BLOCKER — the per-file deadline still flips the verdict on host load (r93 F1 class, not closed).**
`gguf_parse` now resets `DEADLINE = time.monotonic() + PER_FILE_SECONDS` per file (M1 605–607), but the budget is still **wall-clock**, so a file
whose parse straddles 15 s grades `invalid` at low load and `-` (undecided → loadable, round-89 rule) at high load. Same file, same probe, four
alternating runs at load1 418–443: `invalid, invalid, -, -` / `- invalid - invalid` (10.2–15.5 s wall). Through the probe:
`MODEL_UNLOADED/router-model-invalid` vs `MODEL_OK/router-unloaded-autoload` — the exact flip the claim says is removed. At 400 000 tensors = 2 400
004 steps there is **1.6 M steps of headroom against MAX_STEPS=4 M**, so the step bound never fires and PER_FILE_SECONDS is the only binding
constraint — and it is load-dependent. The counter cannot see this: its fixture is 150 000 tensors (900 004 steps), never approaching the 15 s slice,
so `load_stable=1` is trivially satisfied outside the band. The fix relocates the defect from a *shared* 4 s deadline to a *per-file* 15 s wall
deadline without making the verdict load-independent.

**F3 — BLOCKER — `timeout 60` truncates the file-state pass; a long distinct-file listing flips to a false
green MODEL_OK.** `router_file_states` (M1 820) wraps the whole `files` pass in `timeout 60`. With 40 distinct slow files (the counter's own 150
000-tensor shape) the pass needs ~102 s, so the wrapper kills it at 60 s (rc=124) and only 33 of 40 state lines survive. The surviving lines are all
`invalid`, but the lost 7 are absent, so `nbad(33) < ncand(40)` in `router_refine` (M1 884) → `unloaded=1` → `MODEL_OK / router-unloaded-autoload`
(887). Reproduced: M1 probe wall=60.69 s, verdict `MODEL_OK router-unloaded-autoload`, rc=2. Control: same listing, same load, `timeout 60`→`timeout
600` gives `MODEL_UNLOADED router-model-invalid` (wall=232 s) — so the **wrapper**, not the per-file budget, is the cause. The base probe gives the
same false green at 5.76 s (its shared 4 s deadline starves every candidate after the first), so M1 has **not** closed the r93 F-class here; it moved
the starvation from the in-process deadline to the wrapper timeout. The claims' disclosed limit covers only "the counter's own 20 s cell budget, not
the probe's" — but the truncation is the **probe's** `timeout 60`, and R08 uses only **4** distinct slow files (~9 s), so no counter cell reaches it.

**F4 — DEFECT — `/props` fetch timing decides a positive cell: a slow `/props` turns
MODEL_OK/router-unloaded-autoload into a false MODEL_UNLOADED/router-unloaded.** `router_autoload` (M1 830) fetches `/props` with `--max-time
"$TIMEOUT"` (default 5 s). On timeout it returns 1, `autoload` stays 0, and `router_refine` skips the whole file-state block (876 `if [ "$ncand" -gt 0
] && router_autoload "$port"`), so `unloadable` is never set and the verdict falls through to `down` → `MODEL_UNLOADED / router-unloaded`. On the P01
positive-cell shape (4 valid entries): delay 0 → rc=0 `MODEL_OK router-unloaded-autoload`; delay 3 → rc=0 same; delay 6 → rc=2 `MODEL_UNLOADED
router-unloaded`. Identical on the base probe, so pre-existing, not an M1 regression — but a verdict that depends on wall time, in the same C1 class,
and the counter's stub answers `/props` instantly so no cell exercises it. A real router under load can exceed 5 s on `/props`; the probe then reports
drift (exit 2) for a healthy router.

**F5 — NOTE — `router_refine`'s `nbad < ncand` aggregation is fail-open on *any* lost state, and the
listing-level verdict is load-dependent.** M1 884: `if [ "$nbad" -lt "$ncand" ]; then unloaded=1; fi`. One candidate whose state never arrives
(truncated wrapper, F3) or is undecided (F2) makes the whole listing `MODEL_OK` even when every other candidate is `invalid`. Measured, paired on one
fixed 64-entry listing (63 fast-invalid + 1 borderline 600k file), 192 burners: `borderline_state=63 -` → `probe_verdict=MODEL_OK
router-unloaded-autoload`; the same listing at ambient load (borderline decided `invalid`) → `MODEL_UNLOADED router-model-invalid`, and across
consecutive runs on one fixture the verdict alternated (`MODEL_UNLOADED ×3, then MODEL_OK`). The round-89 "undecided stays loadable" rule is applied
per *listing* here, though the claim states it "applies per file, not per call" — one undecided candidate outvotes 63 decided ones. Bounded in that it
is the documented rule, but it is the mechanism by which F2 and F3 become false greens.

**F6 — NOTE — 11 of the 14 claimed round-94 receipts do not exist; the K3 counter anchor is unresolvable.**
`plans/round-94-claims.md` names under `.ufo/waves/round-94/`: `controls/c1-base.out`, `controls/c1-forgeries.{py,out}`, `controls/c2-base.out`,
`controls/c2-forgeries.{py,out}`, `controls/census-start.out`, `controls/harm-base.out`, `controls/sources-opened.out`, `controls/c2-rows.md`,
`controls/c2-section.md`, `measured/gate-final.out`. Present: only `measured/c1.out`, `measured/c2.out`, `controls/c2-build-candidate.py` (all
tracked). A filesystem search over the whole fleet finds no round-94 copy of any missing name (other lanes have their own round-40/46/47 `c1-base.out`
copies). So the do-nothing control, the C1 and C2 forgery sets, the C3 census baseline and the harm baseline (K2) cannot be re-run from the tree — I
substituted my own base-revision run (`counter_base_at_this_host.out`) for the do-nothing control. The C1 *cell* receipt `measured/c1.out` does exist
and shows `load_stable=1`, so the cells ran once on a host where the F1 gate happened to pass. Separately, K3 ("the counter changes after this
commit") is anchored to a freeze commit that does not contain the counter: `git cat-file -e 285f1783:tools/round94-router-budget.py` → absent at F;
the counter first appears at M1, one commit *after* the freeze. Its bytes are stable M1→M2→HEAD (`0fd099ba…`), so the substance of K3 holds; the
anchor does not.
**F7 — NOTE — json_array / print_table buffering is not a live defect at the sizes the claim exercises.** `json_array` (~250) concatenates in a loop (`out="$out,"$'
'"$r"`), quadratic in row count; `print_table` accumulates all rows. Both are bounded by the *registry* row count (36 rows in `registry/endpoint-consumers.tsv`), not by listing size, so the 2048-entry cells do not stress them; the r92 one-pass awk fixes removed the genuine O(n²) listing-side paths (`router_match`, `AWK_NORM`). Not a C1-class defect; recorded to close the candidate.

**F8 — NOTE — the counter's `BUDGET=30.0` (line 108) contradicts the claims' "20 s cell budget" (`plans/round-94-claims.md:51`), and `KILL=120` interacts with the counter's own 60 s wrapper.** A cell needing 60–120 s of wrapper time is killed by `KILL=120` (subprocess timeout), so the receipt would show `unparsed(rc=-9)` rather than a timeout. Cosmetic for the 19 shipped cells (all ≤ 22 s here) but the disclosed limit is misstated.

## Deliverables

- `.ufo/waves/round-94/w1/out/SC02BudgetSweep/counter_M1_at_this_host.out` — counter at M1 here: 19 cell
lines, then `could-not-evaluate`, exit 2.
- `.ufo/waves/round-94/w1/out/SC02BudgetSweep/counter_base_at_this_host.out` — same at base `e6f1dcce`:
`could-not-evaluate`, exit 2.
- `.ufo/waves/round-94/w1/out/SC02BudgetSweep/repro.sh` — rebuilds every fixture, re-runs F2/F3/F4 (writes
only under a scratch dir it is given).
- This report: `.ufo/waves/round-94/w1/SC02BudgetSweep.md`.

Scratch `/fast/scratch/hyaku/kama-r94/SC02BudgetSweep/` removed after copying receipts. No lane file, registry entry or endpoint modified; no
POST/load/unload/completion sent to 127.0.0.1:1234.

VERDICT: falsified — the C1 predicate does not hold at M1 on this host (counter exits 2, not 0), and the per-file 15 s wall deadline plus the `timeout
60` wrapper still flip MODEL_UNLOADED/router-model-invalid to MODEL_OK/router-unloaded-autoload under load, leaving the r93 F1 defect class open.
