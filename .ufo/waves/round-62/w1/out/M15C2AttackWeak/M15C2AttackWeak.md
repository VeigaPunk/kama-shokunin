# M15C2AttackWeak — weak-family falsification probe, round-62 C2 counter

- Seat: M15C2AttackWeak (v2 wave, kama r62, axis calibration; leaf, no subagents)
- Tip probed: master `65d7cad0fce90e34de37527cde22e97b63b118bf`
- Frozen instrument bytes: `tools/round62-c2-counter.py` sha256
  `15d11f1ce8f8cb85e002d83c50b40d2bd7e4dfa561d8dd2d453e2daa09c05929`;
  `registry/capability-claims-r62.tsv` sha256
  `6f8365c71983bb54058212439a7bc891bae1eb58f2b40a15bd7be91f88e62009`
  (both `git show master:<path>`; counter imported unmodified from the blob)
- Method: the frozen counter module was imported from the master blob into my
  scratch and driven through its own `main()` / `score_registry()` /
  `run_bound()` / `controls()`. Lane repo accessed read-only
  (`git show`/`archive` only). All mutations happened in the scratch tip-tree
  extraction (`work/tip/`) and in scratch registry strings; the lane working
  tree was never modified (verified: `tools/sources-append-only.py` in the
  lane = pristine `2e23a04e…` before and after everything below).
- Receipts: `driver.log`, `driver.py`, `restore.log`, `reg-pristine.tsv`,
  `round62-c2-counter.py` (blob copy) in
  `.ufo/waves/round-62/w1/out/M15C2AttackWeak/`.
- Tool installs: none (python3 stdlib only; no pacman, per host pause).

## 0. Baseline: INCONCLUSIVE on this host (pristine bytes, exit 1)

Real counter, pristine registry, pristine tip tree:

```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4 canonical=62 controls_rejected=8/8 errors=0 met=False
[A] counter exit=1 (0 == met)
```

The 4 mismatches are exactly 2 rows failing live, each counted twice (verdict
+ recorded-observation):

- `context-capacity-receipt` — `observed='TIMEOUT'` (900 s host-idle window
  never opened under the concurrent peer load).
- `live-ollama-lifecycle` — early-failure receipt (`argv_child: null`,
  `captures: {}`, `elapsed_s: 0.0`; pinned-archive acquire/launch failed under
  contention).

The other 10 rows, incl. the live llamacpp lifecycle, are green. `errors=0`,
canonical=62, controls 8/8 rejected — the failure mode is environmental, not
registry-shaped. The freeze notes C2 was measured met=True in a parallel
measurement at spec time; this host right now cannot reproduce the green
baseline. Per the mutation protocol this makes baseline-dependent verdicts
inconclusive, and I say so per variant below.

Note: the counter's `--no-live` path cannot certify anything: its stub scorer
returns `sensitive=False`, which forces a mismatch on every bound row, so
`--no-live` always prints `met=False`. All scoring above is executed.

## 1. V1 / V1b — weak family: registry pattern shortened to a substring — REJECTED

Registry mutation only (pattern column `45/45 selftest cases passed` → `pass`;
second probe `IA_SELFTEST pass=` → `pass=`), scored by the instrument's own
`score_registry()` on warm live-run results:

```
[V1 weak: pattern->substring (sources-registry)] population=12 rows=12 covered=11/12 bound=11 sensitive=11/11 dead=0 mismatches=4 errors=0 met=False
[V1 weak: pattern->substring (sources-registry)] error: pattern:sources-registry
[V1 weak: pattern->substring (sources-registry)] VERDICT: REJECTED
[V1b weak: pattern->substring (instrument-agreement)] population=12 rows=12 covered=11/12 bound=11 sensitive=11/11 dead=0 mismatches=4 errors=0 met=False
[V1b weak: pattern->substring (instrument-agreement)] error: pattern:instrument-agreement
[V1b weak: pattern->substring (instrument-agreement)] VERDICT: REJECTED
```

`score()` requires `row['pattern'] == tpl['pattern']` byte-exact against the
frozen manifest template, so any registry-side weakening dies with a
`pattern:<cap>` error before the row is even bound. The counter's own control
family 7 (`weak`) performs precisely this mutation and is rejected
(controls_rejected=8/8). Not a falsification; the registry-side weak family is
closed by design.

## 2. V2 — pattern equal to template, output contains it inside a deceptive line — ACCEPTED (falsification)

Mutant (scratch tip-tree copy of `tools/sources-append-only.py` only; bytes
`2e23a04e…` → `bd9bd708…`) emits the frozen pattern as a substring of one
lying line and exits 0, running no checks:

```python
msg = ("45/45 selftest cases passed "
       "(RETRACTED - 0/45 checks executed, verdict FAIL)")
print(msg)          # stderr-only variant also probed
sys.exit(0)
```

Pristine registry bytes, real executed scoring:

```
[C-mutant] row sources-registry: verdict=True observed='45/45 selftest cases passed' sensitive=True dead=False -> ROW ACCEPTED=True
[C-stderr-only] verdict=True observed='45/45 selftest cases passed' sensitive=True dead=False -> ACCEPTED=True
[C-mutant: pristine registry, deceptive tool output] population=12 rows=12 covered=12/12 bound=12 sensitive=12/12 dead=0 mismatches=4 errors=0 met=False
[C-mutant] counter exit=1 (0 == met)
```

Answer to the seat question: **the verdict check is substring-only.**
`run_bound()` decides with `tpl['pattern'] in (p.stdout + p.stderr) and
rc == 0` — no line anchoring, no output-shape check, no comparison against the
tool's real behavior. All three "binding" checks pass on the lie:

- verdict: the pattern occurs in the lying line, rc=0;
- recorded observation: the row's `observed` column is the bare pattern, which
  is a substring of the lying line, so `row['observed'] not in observed`
  never fires;
- sensitivity: `out.replace(pattern, MUT)` deletes the pattern from the lie
  too, so the flip test cannot distinguish a real 45-case pass from a
  retraction line.

With the lying row active the counter line is byte-identical to the pristine
baseline (`bound=12 mismatches=4 … met=False`) — the only reason it is not
`met=True` here is the two environment-failing rows of §0. On a host where all
12 runs pass, this mutant yields a fully green counter: **ACCEPTED.** The C2
sentence "its emitted verdict equals the recorded one and is sensitive" is
falsified at the semantics level: equality and sensitivity are evaluated on
substring presence, not on truthful emission.

## 3. Controls are blind to emission honesty

With the lying row active, `controls()` still rejects 8/8
(`[C-mutant] controls_rejected=8/8 escapes={}`). All 8 families mutate the
registry text; none re-examines what a bound run actually emitted, and family
7 ("weak") is exactly V1, caught by template equality rather than by output
inspection. So the 8-family battery adds nothing against the V2 hole.

## 4. V3a / V3b — observed-column weakening — REJECTED here; vacuous by code on a green host

```
[V3a: observed column emptied (all rows)] population=12 rows=12 covered=12/12 bound=12 sensitive=12/12 dead=0 mismatches=2 errors=0 met=False
[V3a: observed column emptied (all rows)] VERDICT: REJECTED
[V3b: observed column -> "a" (sources-registry)] population=12 rows=12 covered=12/12 bound=12 sensitive=12/12 dead=0 mismatches=4 errors=0 met=False
[V3b: observed column -> "a" (sources-registry)] VERDICT: REJECTED
```

Both are rejected in this environment only because of the two §0 rows:
emptying the `observed` column drops mismatches 4 → 2, i.e. every healthy
row's recorded-observation check contributes nothing. The check is
`if row['observed'] and row['observed'] not in observed` — an empty cell skips
it entirely, and `'a'` is a substring of any pattern containing an `a`. On a
host where all 12 runs pass, either registry scores `mismatches=0` →
`met=True`. Inconclusive at counter level here (baseline failed); the
row-level hole is confirmed by the delta and the code.

## 5. Restoration evidence

Two driver crashes left the mutant bytes in the scratch tip tree (a crashed
run overwrote its own `.orig` backup before dying). Restored from the master
blob and verified (`restore.log`):

```
pristine-in-scratch-before-restore: bd9bd7082bc93f461f645a13a19f2a9429f387b8ac47f081d5d68d0a3154e586  (mutant)
restored:  2e23a04e6b34b2381f403c34fd6f765ad0355315dfb79dbfd749663d946d568d
git-blob:  2e23a04e6b34b2381f403c34fd6f765ad0355315dfb79dbfd749663d946d568d
expected-pristine (recorded before mutation): 2e23a04e6b34b2381f403c34fd6f765ad0355315dfb79dbfd749663d946d568d
```

Restored tool rerun for real: the full 45-case selftest executes and ends
`45/45 selftest cases passed`, rc=0 — visibly different behavior from the
one-line lie, which run_bound scored identically. Lane working tree:
`2e23a04e…` throughout (never modified). Scratch root removed after receipts
were copied out.

## Verdict summary

| Variant | Mutation | Verdict |
|---|---|---|
| V1 | registry pattern → substring `pass` | REJECTED (`pattern:sources-registry`) |
| V1b | registry pattern → substring `pass=` | REJECTED (`pattern:instrument-agreement`) |
| V2 | truthful-looking tool replaced by deceptive one-liner containing the frozen pattern | **ACCEPTED — falsification; verdict check is substring-only** |
| V2-stderr | same lie on stderr only | ACCEPTED at row level (stdout+stderr are concatenated before matching) |
| V3a | `observed` column emptied | REJECTED here (baseline inconclusive); check vacuous on green host |
| V3b | `observed` column → `a` | REJECTED here (baseline inconclusive); check vacuous on green host |

One-line counter output (pristine baseline, this host):

```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4 canonical=62 controls_rejected=8/8 errors=0 met=False
```
