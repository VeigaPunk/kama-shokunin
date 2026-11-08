# EX02BudgetControl — round 97 wave 1 (C2 control reproduction)

Seat: `EX02BudgetControl` (leaf). Scope: independently reproduce C2's new-cell control matrix,
one legacy survival control, the fixture oracle, and the control mode's exit-code behaviour.
No tracked lane file was edited; receipts live under
`.ufo/waves/round-97/w1/out/EX02BudgetControl/`.

## Revision pins (as resolved at run time)

- `--rev master` → `e057166e09ec069725bd0b0433fc50275ecd03ea` (round-97 amendment 1;
  `master` advanced from the freeze commit `9e605d41` to `e057166e` during this wave).
- Counter bytes identical at `9e605d41`, `e057166e`, `HEAD`: sha256
  `24e2fad7c4fb58e9f3a4b56d8bbff776beac7ebd4a27fef581fae529fcb6ca2c`.
- Probe under claim at `master`/`e057166e`/`9e605d41`: sha256
  `0897ebffc304fe8d487eff4194f39e42210c3dbc2116e5511fbc472237487ca8`.
- Base probe at `40763bd2` (the sha the freeze receipts pin): `11e5b01b…c561e709`.
  `git diff 40763bd2 9e605d41 -- tools/kama-probe.sh` is comment-only (the `5 + nd`
  ceiling text); no parser or constant change. Full diff read.
- Host: Linux 7.2.11-arch1-1, 32 cores, Python 3.14.8, git 2.56.0. No tool installed.

## 1. New-cell controls — real probe and four mutants

Command (identical template; one `--work` dir per run):

```
python3 tools/round97-router-budget.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --rev master --work <scratch>/work-new-<m> --cells new --control \
  --expect survived|caught --mutant none|flat6|undercharge|maxmeta|nopreamble
```

### Real probe (`--expect survived --mutant none`), rc=0, wall 17.2 s

```
ROUTER_BUDGET97_CELL nat W14-900k-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.89s
ROUTER_BUDGET97_CELL nat W15-700k-nd4 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/3.23s
ROUTER_BUDGET97_CELL nat W16-maxmeta ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.23s
ROUTER_BUDGET97_CELL nat W17-833333-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.78s
ROUTER_BUDGET97_CONTROL cells=4 cells_ok=4 mutant=none expect=survived survived=1 caught=0 probe=rev probe_sha256=0897ebffc304fe8d487eff4194f39e42210c3dbc2116e5511fbc472237487ca8 rev=e057166e09ec069725bd0b0433fc50275ecd03ea ok=1
```

### Mutants (`--expect caught`), all rc=0, wall 22.3–23.4 s (four run in parallel)

| mutant | shape | red cells | summary |
|---|---|---|---|
| `flat6` | constant 6 steps/header (dims collapsed to one `rd(8*nd)`) | W15 | `cells_ok=3 caught=1`, sha `cae7b367…` |
| `undercharge` | `need()` charges only when `n >= 32` | W14, W15, W17 | `cells_ok=1 caught=1`, sha `3a709856…` |
| `maxmeta` | `MAX_META` 512 MiB → 100 MiB | W16 | `cells_ok=3 caught=1`, sha `22c311f1…` |
| `nopreamble` | **intended** preamble-drop; actual effect: all `need()` charging removed (see D1) | W14, W15, W17 | `cells_ok=1 caught=1`, sha `b27dc8bf…` |

Verbatim per-cell lines are in `out/EX02BudgetControl/new-{flat6,undercharge,maxmeta,nopreamble}.out`.
Reproduction of the freeze receipts: applying the frozen `MUTANTS` byte table to the base probe
reproduces every `probe_sha256` in `.ufo/waves/round-97/controls/c2-new-mutants.out` exactly
(`flat6 14efbe6f…`, `undercharge 2e31ff3b…`, `maxmeta 6b5f6db4…`, `nopreamble 9035b55e…`).

**Verdict:** the four shipped mutants are each `caught=1` on the new cells, and the real probe is
`survived=1`. Cells W14/W15/W16 behave exactly as the plan states (W14 undercharge, W15 flat6,
W16 maxmeta). W17 is exercised only in the sense that it is red for every mutant that removes
header charging; the specific preamble-drop class it was sized for is **not** delivered by the
frozen mutant named `nopreamble` (D1).

## 2. Legacy survival control (one mutant, timed)

```
python3 tools/round97-router-budget.py --repo … --rev master \
  --work <scratch>/work-legacy-undercharge \
  --cells legacy --control --expect survived --mutant undercharge
```

Result: rc=0, **all 13 cells ok**, `cells=13 cells_ok=13 survived=1 caught=0`;
`WALL_SECONDS=140.00 USER=111.65 SYS=16.64 MAXRSS_KB=362376` (`/usr/bin/time`).
Inner times: W03-slow-x40 `70.12s`, W02 `12.82s`, W05 `13.21s`, W01 `1.73s`, W11 `2.77s`,
W08 `2.15s`, W12 `1.30s`, W13 `1.22s`; W04/W06/W07/W09/W10 < 0.3 s each. Full output:
`out/EX02BudgetControl/legacy-undercharge.out`. The 13 names are byte-identical to
`tools/round96-router-budget.py`'s set (checked by name extraction).

Notes: (a) the 140 s wall includes a light single-process analysis that overlapped part of the
run (the 17 s probe-sensitivity check); W03 itself is the dominant cost. (b) W03 at 70.12 s is
below the 75 s margin (`1.25 × 60 s`), i.e. on this host the predicate path with the default
`--slow-files 40` would hit the guard — exactly the condition round-97 amendment 1 records
(`--slow-files 72`). Control mode deliberately does not apply that guard; the survival claim is
about the 13 cells, not the wrapper.

## 3. Fixture oracle re-derivation (independent)

Method: a standalone parser (`out/EX02BudgetControl/oracle_ex02.py`) re-reads the exact bytes the
counter's own `nat/` work dir contained (captured during the real-probe control, before the tool's
`shutil.rmtree`), parses GGUF v3 strictly from the layout, and computes class from the probe's
disclosed constants (`MAX_STEPS 5_000_000`, preamble 4, `5 + nd` per header, `MAX_META 512 MiB`,
`MAX_TENSORS 1_000_000`). It imports neither the counter nor the probe.

```
ORACLE t900k.gguf designed=- derived=- agree=1 {'n_tensors': 900000, 'n_kv': 0, 'size': 36000048, 'preamble_steps': 4, 'kv_steps': 0, 'why': 'Unknown: MAX_STEPS', 'steps_at_return': 5000001}
ORACLE mid4.gguf designed=- derived=- agree=1 {'n_tensors': 700000, 'n_kv': 0, 'size': 44800048, 'preamble_steps': 4, 'kv_steps': 0, 'why': 'Unknown: MAX_STEPS', 'steps_at_return': 5000001}
ORACLE maxmeta.gguf designed=invalid derived=invalid agree=1 {'n_tensors': 1, 'n_kv': 1, 'size': 167772239, 'preamble_steps': 4, 'kv_steps': 5, 'header_steps': 6, 'nd_values': [1], 'steps_per_header': 6.0, 'why': 'offset 1099511627776 != expect 0 on tensor 0', 'steps_at_return': 15}
ORACLE t833333.gguf designed=- derived=- agree=1 {'n_tensors': 833333, 'n_kv': 0, 'size': 33333360, 'preamble_steps': 4, 'kv_steps': 0, 'why': 'Unknown: MAX_STEPS', 'steps_at_return': 5000001}
```

Arithmetic re-derived from the raw bytes: `t900k 4+900000*(5+1)=5400004 > 5 000 000 → -`;
`mid4 4+700000*(5+4)=6300004 → -`; `t833333 4+833333*6=5000002 → -` (the tight boundary;
`833332 → 4999996 → invalid`); `maxmeta 4 + 5 KV + 6 header = 15 steps`, position after the
160 MiB string = 167 772 205 < 512 MiB, then declared offset `1<<40 ≠ 0` → `invalid`.
**No disagreement** with the counter's designed classes; captured-byte sha256:
`t900k 0e0a51cf…`, `mid4 868d489b…`, `maxmeta d2e18f44…`, `t833333 90d60f50…`
(`out/EX02BudgetControl/fixtures.sha256`). At `MAX_META = 100 MiB` the tensor-name `need()` at
position 167 772 205 raises Unknown → `-`, which is what the `maxmeta` mutant run observed
(`MODEL_OK/router-unloaded-autoload`), so W16's discriminator is real.

## 4. Control-mode exit codes (probed, not inferred)

| case | command tail | rc | summary |
|---|---|---|---|
| expectation met (real) | `--cells new --control --expect survived --mutant none` | 0 | `survived=1 … ok=1` |
| expectation met (mutant) | `--cells new --control --expect caught --mutant flat6` | 0 | `caught=1 … ok=1` |
| expectation violated | `--cells new --control --expect survived --mutant flat6` | **1** | `survived=0 caught=1 … ok=0` |
| usage (caught without a mutant) | `--control --expect caught --mutant none` | **64** | `ROUTER_BUDGET97 usage: …` |
| unresolvable rev | `--rev deadbeefdeadbeef --control --expect survived --mutant none` | **2** | `could-not-evaluate: unresolvable rev …` |
| anchor not exactly once | `--probe-file <probe with need() anchor altered> --mutant undercharge` | **2** | `could-not-evaluate: mutant undercharge: anchor appears 0 times, not exactly once` |

The 0/1/2/64 mapping is honest for every reachable path I exercised. Limits/defects below.

## Findings

### D1 (calibration, medium) — `nopreamble` is not a preamble-drop; it disables all `need()` charging

`tools/round97-router-budget.py:174-175` patches

```
def need(n):
            steps[0] += 1
```

to

```
def need(n):
            steps[0] += 0 if steps[0] < 4 else 1
```

The condition tests the counter it is supposed to increment; `steps[0]` starts at 0 and never
reaches 4, so **every** `need()` call charges 0, not just the four preamble calls. Direct probe
runs on the captured fixtures (`out/EX02BudgetControl/preamble_drop_probe.out`):

```
honest       t900k    -> 0  -
honest       mid4     -> 0  -
honest       t833333  -> 0  -
droppreamble t900k    -> 0  -            (reconstructed true preamble-drop: `steps = [-4]`)
droppreamble mid4     -> 0  -
droppreamble t833333  -> 0  invalid      (W17 only)
nopreamble   t900k    -> 0  invalid      (shipped mutant: total charge removal)
nopreamble   mid4     -> 0  invalid
nopreamble   t833333  -> 0  invalid
```

Consequences: (i) the shipped mutant's red-cell signature (W14, W15, W17) is identical to
`undercharge`'s, so the frozen control receipts do **not** distinguish a preamble-drop probe from
a per-header-removal probe; (ii) the plan's C2 sentence "W17-833333-nd1 … catches a probe that
does not charge the four preamble steps" is true of the *cell* — I verified a real `steps = [-4]`
patch flips only W17 — but no frozen mutant implements that class, so the receipt does not prove
it. The exit code is honest about what ran (`caught=1` for the actual bytes), the mutant name and
the claim text are not. A patch that actually drops only the preamble would need a separate call
counter (or initialize `steps = [-4]`), not a test on `steps[0]`.

### D2 (latent robustness, low) — control exit 0 does not assert cell completeness

`tools/round97-router-budget.py:622-630`: `survived = int(n_ok == n)` over `natural.values()`,
with no `n == len(selected)` assertion. If a selection ever produced zero cells, `0 == 0` would
print `survived=1 cells=0 … ok=1` and exit 0. Not reachable through the current CLI for
`--cells legacy` (`n_slow = max(8, n_slow)` at line 455 keeps the legacy block alive), but the
guard is missing; the control's honesty currently rests on the static cell list plus `cells=N`
being eyeballed. My runs printed `cells=4`/`cells=13` as expected.

### D3 (calibration, low) — control receipts pin the base probe, not the probe under claim

The freeze receipts' `probe_sha256=11e5b01b…` / mutant hashes are the bytes at `40763bd2`; the
probe at the frozen/amended rev is `0897ebff…` (comment-only diff, verified above). Behaviour is
identical and my re-run at `master` reproduces the same cell outcomes and the same *patched*
hashes, so no claim is broken; but the receipt does not bind the M2 probe bytes. A future
non-comment probe edit would be invisible to these receipts until re-run.

### D4 (brief inconsistency, informational) — "16 cells / three mutants" vs frozen "17 / four"

The wave brief's C2 line says "16 cells; W14/W15/W16 catch three probe mutants". The frozen plan
(`plans/round-97-claims.md` §C2), `claims.json`, and the counter all say 17 cells (13 + W14–W17)
and four graded mutants. I graded the frozen set; the brief's count is stale.

### D5 (limit) — `caught` is "any cell red", single natural pass

Control mode forces `runs=1` and credits `caught=1` on any red cell, with no per-mutant expected
cell and no repeat. A transient host failure would certify `caught`; for `--expect survived` it
would falsely certify that the legacy set discriminates. My runs were stable and matched the
freeze receipts cell-for-cell, and the per-cell lines make the discriminating cell inspectable,
but the summary exit code alone does not encode which cell caught. Related: `--control --expect
caught --mutant none` is rejected (rc=64), so an arbitrary external probe cannot be certified
through the control mode without stacking one of the frozen mutants — I tested the true
preamble-drop by invoking the extracted probe directly instead.

## No-change / cleanup

- No tracked lane file, jj state, git index, or sibling lane touched. Read-only git only
  (`show`, `rev-parse`, `diff`, `log`, `status`).
- Fixtures were built by the counter inside my scratch; the three named plus `t833333.gguf` were
  copied out of the `nat/` work dir before the tool's cleanup (hashes above).
- Scratch `/fast/scratch/hyaku/kama-r97/EX02BudgetControl/` is removed before yield; receipts are
  in `.ufo/waves/round-97/w1/out/EX02BudgetControl/`.
- No tool installed or upgraded.
