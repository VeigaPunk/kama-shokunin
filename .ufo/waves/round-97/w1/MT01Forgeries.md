# MT01Forgeries — round 97 w1 — independent mutation test of the two C2 instruments

Seat: mutation tester (leaf). Lane `kama-shokunin`, wave that attacks landed work.
Out dir `.ufo/waves/round-97/w1/out/MT01Forgeries/`, scratch `/fast/scratch/hyaku/kama-r97/MT01Forgeries/`
(deleted at exit; every receipt copied here first). No tracked lane file was edited.

## 0. Bytes under test

| object | rev | sha256 |
|---|---|---|
| lane `master` after amendment 1 (appeared mid-seat; it records a could-not-evaluate, it does not change the counter) | `e057166e` | — |
| round-97 freeze commit | `9e605d41` | — |
| probe under claim (`git show 9e605d41:tools/kama-probe.sh`) | `9e605d41` | `0897ebffc304fe8d487eff4194f39e42210c3dbc2116e5511fbc472237487ca8` |
| probe in the freeze-time control receipts | `40763bd2` | `11e5b01b8d01b5c56ad0200f04c0871a95d398eafc71a3819cb2629fc561e709` |
| `tools/round97-router-budget.py` | `9e605d41` = `e057166e` | `24e2fad7c4fb58e9f3a4b56d8bbff776beac7ebd4a27fef581fae529fcb6ca2c` |

Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`
(`git rev-parse --show-toplevel` → `$S/lane`). All counters were driven with
`--repo $S/lane --rev 9e605d41`; no run read the lane worktree.

Method: my own patches (never the counter's `MUTANTS` bytes), my own GGUF writer, my own HTTP
stub and detector (`out/MT01Forgeries/harness.py`), then both counters with
`--probe-file <my mutant>`.

## 1. Patches (each anchor occurs exactly once in the freeze probe; `bash -n` passes)

```
P = freeze probe as committed, sha 0897ebff…

A  one step per tensor header (name/dims free)          sha de49e3f1f8889545eb536b3706eefed90f595bd46eb295b8b39f8647f0ab9d1b
--- a/tools/kama-probe.sh
+++ b/tools/kama-probe.sh
@@ -752,2 +752,3 @@ (tools/kama-probe.sh)
                 tt, off = u32(), u64()
+                steps[0] -= 4 + nd  # MT-A: one step per tensor header (name/dims free)
                 if tt not in QSIZES:

B  constant 6 steps per header, any rank                sha 7cd3894278eb70e9192aa8e41465c48a5ed10a049fcf3f2a7f4302dd6d38a990
@@ -752,2 +752,3 @@ (tools/kama-probe.sh)
                 tt, off = u32(), u64()
+                steps[0] += 1 - nd  # MT-B: a constant 6 steps per header, any rank
                 if tt not in QSIZES:

C  MAX_META = 100 MiB (added line, cap overridden)      sha 0c6e7c2797a50ed9798335f8421162b38df2b95feb5cf5cd43fd71872216edef
@@ -587,1 +587,2 @@ (tools/kama-probe.sh)
 MAX_STEP_BYTES = MAX_STEPS  # one need() call per bounded read/seek; kept for readers
+MAX_META = 100 * 1024 ** 2  # MT-C: 100 MiB header-position cap

D  ctime dropped from the SEEN key                      sha 2901ca9f1af551aab40e1d2cd08a494aab8031ba3c866a932452b9898399fcb4
@@ -616,1 +616,1 @@ (tools/kama-probe.sh)
-    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
+    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)  # MT-D: ctime dropped

E  (extra, isolates the W17 class) true preamble drop   sha f9e6507f1b22b95a35620d812972617e3e428f8ca4407153ccee23808c151103
@@ -724,1 +724,2 @@ (tools/kama-probe.sh)
             n_tensors, n_kv = u64(), u64()
+            steps[0] -= 4  # MT-E: the four preamble steps are free

G  (extra, one-sidedness probe) MAX_STEPS lowered       sha bd52585d51643617ccfe209d24010bd7f8aeddc1b100a6e5f43f73a0397de14e
   MAX_STEPS = 5_000_000  ->  MAX_STEPS = 4_000_000
```

`A` nets `(5+nd) - (4+nd) = 1` step/header; `B` nets `(5+nd) + (1-nd) = 6`; `C` is a cap of
104857600 bytes; `D` removes the fifth key field; `E` nets `4 + T·(5+nd) - 4`.

## 2. Own detector: the patches do what they claim, and are distinguishable

`harness.py` runs `bash <probe> check --port <p> --expect good --json` against its own stub and
its own fixtures ("-" = `MODEL_OK router-unloaded-autoload`, `invalid` =
`MODEL_UNLOADED router-model-invalid`). Fixtures written by `harness.py` itself; expected steps
are `4 + T·(5+nd)`.

| fixture (T, nd) | steps | P | A | B | C | D | E | N¹ | U¹ |
|---|---|---|---|---|---|---|---|---|---|
| t833334 (833,334; 1) | 5,000,008 | - | inv | - | - | - | - | inv | inv |
| t833333 (833,333; 1) | 5,000,002 | - | inv | - | - | - | **inv** | inv | inv |
| t900k (900,000; 1) | 5,400,004 | - | inv | - | - | - | - | inv | inv |
| m700k4 (700,000; 4) | 6,300,004 | - | inv | **inv** | - | - | - | inv | inv |
| n555556 (555,556; 4) | 5,000,008 | - | inv | inv | - | - | - | inv | inv |
| s120m (120 MiB KV + bad offset) | — | inv | inv | inv | **-** | inv | inv | inv | inv |
| strbig (6·10⁶ string elements) | — | - | - | - | - | - | - | - | - |
| ok | — | - | - | - | - | - | - | - | - |

¹ N/U = the counter's own `nopreamble` / `undercharge` patches, applied to the **freeze** probe
bytes (reproduced only to compare behaviour; not used as my mutants).

Every required separation exists: `A` flips all header-budget fixtures, `B` flips only the
rank-4 ones, `C` flips only the 120 MiB header fixture, `E` flips only the 833,333 boundary, and
`D` flips nothing (see §6).

## 3. Counter results — exact receipt lines

### 3.1 round-96 counter (13 cells, its whole set; natural pass only)

Command per probe:
`python3 tools/round96-router-budget.py --repo $S/lane --rev 9e605d41 --work … --runs 1 --slow-files 40 --burners 0 --allow-clock --skip-load --probe-file <mutant>`
(`--allow-clock` is needed because that counter has no control mode; it bypasses only the
host-speed guard and the DEADLINE check, and `--skip-load` keeps it to one natural pass, the
same shape as the frozen `--control` receipts.)

| probe | cells ok=1 | cells ok=0 | receipt tail |
|---|---|---|---|
| P | 13 | 0 | `ROUTER_BUDGET96 cells=13 … probe_sha256=0897ebff…` |
| A | 13 | 0 | `… probe_sha256=de49e3f1… w03_seconds=75.1 …` |
| B | 13 | 0 | `… probe_sha256=7cd38942… w03_seconds=74.8 …` |
| C | 13 | 0 | `… probe_sha256=0c6e7c27… w03_seconds=200.9 …` |
| D | 13 | 0 | `… probe_sha256=2901ca9f… w03_seconds=232.9 …` |
| E | 13 | 0 | `… probe_sha256=f9e6507f… w03_seconds=221.5 …` |

The 13 round-96 cells survive **all** of A–E: the legacy set cannot discriminate any of them,
exactly as the round-96 closure (MT01 G1) stated.

### 3.2 round-97 counter, `--cells legacy --control --expect survived`

```
ROUTER_BUDGET97_CONTROL cells=13 cells_ok=13 mutant=none expect=survived survived=1 caught=0 probe=override probe_sha256=de49e3f1f8889545eb536b3706eefed90f595bd46eb295b8b39f8647f0ab9d1b rev=9e605d416c199b3c9913a2125b04f9c5a16f5668 ok=1
```
(identical line for P, B, C, D, E with their own `probe_sha256`; all `cells_ok=13 survived=1`,
exit 0). The legacy half is unchanged, including W10-rewrite
(`v1=MODEL_UNLOADED/router-model-invalid v2=MODEL_OK/router-unloaded-autoload v3=MODEL_UNLOADED/router-model-invalid`).

### 3.3 round-97 counter, `--cells new --control --expect survived`

| probe | per-cell | summary |
|---|---|---|
| P | W14 W15 W16 W17 all `ok=1` | `cells=4 cells_ok=4 … survived=1 caught=0 … ok=1` exit 0 |
| A | `W14 ok=0`, `W15 ok=0`, W16 `ok=1`, `W17 ok=0` | `cells=4 cells_ok=1 … survived=0 caught=1 … ok=0` exit 1 |
| B | W14 `ok=1`, `W15 ok=0`, W16 `ok=1`, W17 `ok=1` | `cells=4 cells_ok=3 … caught=1 …` exit 1 |
| C | W14 `ok=1`, W15 `ok=1`, `W16 ok=0`, W17 `ok=1` | `cells=4 cells_ok=3 … caught=1 …` exit 1 |
| D | all four `ok=1` | `cells=4 cells_ok=4 … survived=1 caught=0 … ok=1` exit 0 |
| E | W14 `ok=1`, W15 `ok=1`, W16 `ok=1`, **`W17 ok=0`** | `cells=4 cells_ok=3 … caught=1 …` exit 1 |
| G | all four `ok=1` | `cells=4 cells_ok=4 … survived=1 caught=0 … ok=1` exit 0 |

Literal lines (C and E; the naive ones share the shape):

```
ROUTER_BUDGET97_CELL nat W16-maxmeta ok=0 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_OK/router-unloaded-autoload/0.66s
ROUTER_BUDGET97_CELL nat W17-833333-nd1 ok=0 want=MODEL_OK/router-unloaded-autoload run1=MODEL_UNLOADED/router-model-invalid/10.32s
```

Note: the counter refuses `--expect caught` together with `--probe-file`
(`tools/round97-router-budget.py:585`), so a non-author cannot emit a `caught=1` line for their
own patch; the per-cell `ok=` lines are the only admissible evidence, and the summaries above are
`survived=0 caught=1` printed under `--expect survived`. That is API friction, not a false green.

### 3.4 Survival / catch matrix (17 cells = 13 legacy + 4 new)

| mutant | round-96 13 | r97 legacy 13 | r97 W14 | W15 | W16 | W17 | verdict |
|---|---|---|---|---|---|---|---|
| A one step/header | survives | survives | **catches** | **catches** | – | **catches** | caught |
| B constant 6/header | survives | survives | – | **catches** | – | – | caught |
| C MAX_META 100 MiB | survives | survives | – | – | **catches** | – | caught |
| D ctime dropped | survives | survives | – | – | – | – | **survives (disclosed)** |
| E preamble free | survives | survives | – | – | – | **catches** | caught |
| G MAX_STEPS 4 M | not run as a counter; my harness shows the W11 shape flips (F3) | not run | – | – | – | – | survives the *new* cells (4/4) |

## 4. Findings

**F1 — The four new cells are sized past the four named forgery classes.** A (per-header charge
removed, `undercharge` class) is caught by W14/W15/W17; B (constant 6, `flat6` class) by W15; C
(100 MiB cap, `maxmeta` class) by W16; and a *true* preamble drop (E) by W17 alone. Sizing
margins: any integer per-header charge ≤ 5 at nd=1 flips W14 (900 000·5 = 4 500 000 ≤ 5 000 000
still decides); W15's constant-6 probe needs ≤ 833 332 headers to stay inside the budget and the
cell sits at 700 000; W17's 833 333 is the unique integer count that separates 4 + 6T from 6T.
No false red on the pristine probe: P is 4/4 and 13/13.

**F2 — The counter's `nopreamble` mutant is not a preamble mutant, and its receipt does not
evidence the W17 arithmetic.**
`tools/round97-router-budget.py:174-175` replaces the charge with
`steps[0] += 0 if steps[0] < 4 else 1`. `steps[0]` starts at 0 and the four preamble reads are
4, 4, 8, 8 bytes (< 32), so nothing ever increments it: the branch condition is never satisfied,
`steps[0]` stays 0 for every file that reaches the tensor loop without a string array — which
includes all four new-cell fixtures — and the tensor-header budget is **absent**. On every
header-only fixture that is indistinguishable from `undercharge` (also 0/header): the N and U
columns of §2 are identical on all eight fixtures, and both frozen receipts print the same
`cells_ok=1` (W14/W15/W17 red). So the `nopreamble` block of
`.ufo/waves/round-97/controls/c2-new-mutants.out` proves "headers unbudgeted", not "preamble
free"; its W17 red is explained without the `4 999 998` arithmetic at all. The instrument is
nevertheless correctly sized: my E (`steps[0] -= 4` after the preamble, which keeps a real
budget) is caught by **W17 alone** (`W14 ok=1 W15 ok=1 W16 ok=1 W17 ok=0`, §3.3) — the first
executed evidence of the class the cell is documented to catch. Caveat for exactness: N and U
diverge only when the KV phase alone has already consumed 5 000 000 − 5 … 5 000 000 − 1 steps
before a tensor header, a shape no cell contains.
*Receipt-honesty defect: the mutant's name and docstring sentence ("a probe that does not
charge the four preamble steps") do not describe the bytes.*

**F3 — `--cells new --control` is a one-sided detector; a wrong probe is survived.** Three of the
four new cells expect the undecidable state `-`. Probe G sets `MAX_STEPS = 4_000_000` (a cap 20 %
too low) and scores `ROUTER_BUDGET97_CONTROL cells=4 cells_ok=4 … survived=1 caught=0 … ok=1`.
It is wrong: on the round-96 W11 shape it flips the decision —
`P m700k1(700 000 at nd=1) -> MODEL_UNLOADED/router-model-invalid` vs
`G m700k1 -> MODEL_OK/router-unloaded-autoload` (my harness, same 26 MB fixture). The 17-cell
predicate is sound because legacy W11 pins the lower bound; the *control receipt* shape
("new cells only, expect caught") is not evidence of correct arithmetic on its own. Any future
claim that reads `caught=1` from the four new cells as proof of the `5 + nd` arithmetic would be
over-reading it.

**F4 — The freeze-time control receipts patched the wrong probe bytes (behaviourally harmless).**
`controls/c2-new-mutants.out` / `c2-legacy-mutants.out` print `rev=40763bd2ca1e…` and a mutated
`probe_sha256` derived from `11e5b01b…` (the round-96 probe), while the claim's probe at the
freeze commit is `0897ebff…` (C1 checks that constant-6 sentence's removal in that very file).
`git diff 40763bd2 9e605d41 -- tools/kama-probe.sh` changes 2 lines and both are comments
(`# Round 96 …` prose and the trailing comment on `MAX_STEPS = 5_000_000`); the code is
byte-identical, so no verdict can differ. Still, the receipts do not name the bytes the plan
calls "the probe under claim".

**F5 — Stale "three" where the artifact has four.** `tools/round97-router-budget.py:13`
("Round 97 adds three cells past that:") is followed by four cells (W14–W17); `NEW_CELLS` has
four and `CELLS = 17`. `plans/round-97-claims.md:76-77` says "the three control receipts … and
`caught=1` for the three new cells, one per mutant". C1 does not grade this prose (it grades
`tools/round96-router-budget.py` byte-identity, SKILL.md and SCORECARD), so the mismatch is
unobserved by the frozen instruments. Same defect class as the round-96 stale disclosures.

**F6 — D (ctime) is not observable from the probe's public path.**
`SEEN` is a module global and every `router_file_states` call is a fresh `python3 -c "$ROUTER_PY"`
process, so the memo never spans invocations; within one invocation the `files` loop stats each
named path and parses an inode once. The ctime component of the key can change only if the
inode's metadata changes between two `gguf_state` calls **of the same process**, and the probe
never writes a candidate, so no listing can cause that; only a concurrent external writer could,
which makes any detector timing-dependent rather than deterministic. Measured on a
200,000-header fixture: 1 path 2.89 s,
4 hard links to one inode 2.83 s (one parse — memo hit), 4 distinct copies 11.07 s (four
parses); P and D return identical states on all eight fixtures, including the two-invocation
W10 rewrite (`v2` `MODEL_OK`, `v3` `MODEL_UNLOADED/router-model-invalid`). The `W10-rewrite` cell
therefore does not exercise the ctime key either — it compares two invocations, where `SEEN` is
empty. D surviving all 17 cells is the disclosed limit, and the disclosure's reason is correct.

**F7 — Freeze-time baseline for the new cells is the round-96 probe.** The first block of
`controls/c2-new-mutants.out` ("real probe, new cells, expect survived") has
`rev=40763bd2 … probe_sha256=11e5b01b…`; my P run against the freeze bytes
(`probe_sha256=0897ebff…`) is `cells=4 cells_ok=4 … survived=1` (§3.3), so the claim's baseline
holds, but the frozen receipt again names the pre-freeze bytes (same comment-only diff as F4).

**F8 — W16 grades only *lowered* caps.** It discriminates caps below ~160 MiB; a probe with
`MAX_META` raised survives (it grades `invalid` past the 160 MiB string either way). That matches
the declared class ("the 100 MiB cap"), recorded here as a limit, not a defect.

## 5. Secondary probe — C3 depth audit (not the assigned pair, run because depth is judged)

`tools/round97-depth-boundary-audit.py` against a scratch fixture repo (`git init` in
`$S/depthfx`, `rev-parse --show-toplevel` asserted; SKILL.md + probe copied from `9e605d41`):

| fixture commit | change | output | verdict |
|---|---|---|---|
| lane `9e605d41` (the predicate) | — | `DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True` rc 0 | green |
| v0 | pristine copy | `rows=6 checks=8 mismatches=0 met=True` rc 0 | green |
| v1 | probe `MAX_STEPS = 6_000_000`, table untouched | `rows=6 checks=8 mismatches=4 met=False` rc 1 | rows recompute from the probe |
| v2 | row 833,333 states `5,000,004` | `rows=6 … mismatches=1` rc 1 | steps checked |
| v3 | row 833,332 says `> budget` with correct steps | `rows=6 … mismatches=1` rc 1 | comparison checked |
| v4 | required row 555,556 deleted | `rows=5 … mismatches=1` rc 1 | required set enforced |
| v5 | a second *correct* 900,000 row | `rows=7 checks=9 mismatches=0 met=True` rc 0 | duplicate correct row passes (benign) |
| v6 | an extra row with wrong steps | `rows=7 checks=9 mismatches=1 met=False` rc 1 | every present row graded |

v1 is the decisive one: with `MAX_STEPS` raised to 6,000,000 exactly three rows flip (833,333,
900,000, 555,556) and the literal `5,000,000` check fails — the audit is not literal-presence
matching. Limits observed: the S620/S621 and `5,000,000` checks are literal substring presence,
and the prose is not graded (already disclosed for C3 as "not a proof over all (T, nd) pairs").

## 6. False greens, summarised

1. **New-cells-only control (F3, demonstrated):** `cells_ok=4 survived=1` for `MAX_STEPS =
   4_000_000`. Only the union with legacy W11 pins the arithmetic; the new cells alone are
   one-sided (three of four expect `-`).
2. **`nopreamble` receipt (F2, demonstrated):** `caught=1` is real (the probe is wrong) but the
   class it claims (preamble) is not the class it instantiates (no header budget); the W17
   arithmetic had no isolating receipt until this seat's E.
3. **D:** all-green, correctly disclosed as unobservable, and it is unobservable (F6).
4. Not a false green: the pristine probe is green on 13/13 and 4/4 with base bytes `0897ebff…`,
   and the three invalid-expecting legacy cells (W01/W02/W03/W07/W11) still carry the other
   direction of the budget, which is what keeps F3 from being a defect of the predicate.

## 7. Evidence and restoration

- Receipts (copied to `w1/out/MT01Forgeries/receipts/`): `r96-{P,A,B,C,D,E}.out`,
  `r97-{P,A,B,C,D,E}-{legacy,new}.out`, `r97-G-new.out`, `my-harness-matrix.txt`,
  `my-harness-bigmatrix.txt`, `memo-timing.txt`, `depth-audit-mutants.txt`.
- Detector and driver: `w1/out/MT01Forgeries/harness.py`, `drive.sh`.
- The lane was never written: lane `tools/kama-probe.sh` sha256 stays
  `0897ebffc304fe8d487eff4194f39e42210c3dbc2116e5511fbc472237487ca8`; the clone's worktree was
  never modified (mutants live under `$S/mut/`, the depth fixture under `$S/depthfx/`).
- Scratch `/fast/scratch/hyaku/kama-r97/MT01Forgeries` removed after the copy
  (`rm -rf -- "$S"`).
- Tooling: none installed (bash, python3 stdlib, read-only git only).

## 8. Limits of this seat

Natural-pass (control) grading only: no synthetic-load pass was run, so these results speak to
cell discrimination, not to the predicate's `load_stable=1` clause. Four named classes plus my E
and G were graded; the counter's disclosed limit (a wrong inner-header charge that leaves the
totals at 5+nd) was not probed beyond B and E.
