# M12C2AttackVerdict — verdict-family attack on the round-62 C2 counter

Seat: attack (mutation tester), round 62 kama, axis **calibration**. Posture:
godspeed. Leaf member — no subagents, no installs (python3/git sufficient; no
pacman touched). Assigned probe: falsify the C2 predicate via the verdict
family — verdict flipped to false while the live run is green, and verdict
recorded true for a capability whose bound run FAILS — and report whether the
recorded-vs-computed verdict check catches it.

## Instrument and method

- Counter and registry taken at the spec-time master
  `65d7cad0fce90e34de37527cde22e97b63b118bf`, byte-pinned:
  `tools/round62-c2-counter.py` sha256 `15d11f1ce8f8cb85e002d83c50b40d2bd7e4dfa561d8dd2d453e2daa09c05929`,
  `registry/capability-claims-r62.tsv` sha256 `6f8365c71983bb54058212439a7bc891bae1eb58f2b40a15bd7be91f88e62009`
  (scratch copies byte-identical to `git show master:`). Lane master advanced
  to `101737047afeea3a97ceacb98b6d76fa174ed7e4` (L1 committing) during the
  run; all probes stayed pinned to the spec-time tip.
- Fixtures lived only in scratch (`/fast/scratch/hyaku/kama-r62/w/M12C2AttackVerdict/`):
  first a single-commit archive export (commit `b2646c9…`, discarded — see
  V0a), then `fixture2`, a full-history clone with a pristine checkout at
  `65d7cad…`. The variant commit `711c517ee1d3a41b2a901ea82153a0bdcb6acae1`
  adds one change: `tools/sources-append-only.py` (the victim, first registry
  row, cheapest deterministic selftest) gets a module-top
  `sys.exit(3)` after writing one stderr marker line,
  `SELFTEST-BROKEN-SEAT-VERDICT`. The marker contains no hex-run/digest
  tokens; both scanner rows were re-measured green (`unknown=0`) at the
  variant tip, so the only behavior change is the victim's.
- Detector: the counter's own `main()` for baselines (plus its per-row
  `_EXEC_CACHE` dump), and for the mutation worlds a gate-checked replay:
  `score()`/`controls()` from the pinned module over per-row values measured
  live by the counter itself, validated by reproducing the baseline facts
  exactly before any mutation is applied
  (`verdict-family-combination.txt`). The victim row's variant values were
  measured live via the counter's own `run_bound`
  (`victim-variant-probe.txt`): computed verdict **false**, observed
  `'SELFTEST-BROKEN-SEAT-VERDICT\n'`, dead false.

## V0 baselines

- **V0a (archive fixture, discarded)**: `mismatches=8 … met=False`, exit 1 —
  fixture artifact, not a tip property: `digest-ledger` and `hexrun-census`
  bound runs are git-history-dependent (`unknown=8` / `unknown=242` on the
  archive vs `unknown=0` on the full clone, matching lane master exactly).
  Method finding: the C2 counter must be run with `--repo` at a full-history
  clone; archive/shallow exports false-fail these two rows.
- **V0 (full-history clone @ `65d7cad…`)**: `population=12 rows=12
  covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4
  canonical=62 controls_rejected=8/8 errors=0 met=False`, exit 1.
  **C2 did not reproduce met in this execution window**: the
  `context-capacity-receipt` row hit `run_bound`'s 900 s TIMEOUT (no
  host-idle window under fleet load — several sibling llama-server children
  were continuously alive), and `live-ollama-lifecycle` failed at setup
  (`argv_child null, elapsed_s 0.0`). Both rows are outside the verdict
  family; the victim row is green (computed true == recorded true). The 4
  mismatches are exactly those two rows (verdict + observed each). No tip
  receipt exists in `.ufo/waves/round-62/controls/` to compare against.
  Baseline-as-a-whole is inconclusive for those rows; the verdict-family
  probes below are row-level, and the two artifacts offset identically in
  pristine and mutated worlds.

## Verdict-family variants (victim: `sources-registry`)

| variant | registry says | run does | mismatches | counter | verdict |
|---|---|---|---|---|---|
| V1 | `false` | green (measured live in V0) | 4 → 5 | met=False | **REJECTED** (caught) |
| V2 | `true` | FAILS (tool broken, measured live at variant tip) | 4 → 6 | met=False | **REJECTED** (caught) |
| V3 | `false` + observed synced to failing output | FAILS (same live values) | 4 → 4 (victim adds **0**) | met gated only by V0's two environment rows | **ACCEPTED** (conditional realization — see below) |

- **V1** (the family's named mutation): recorded false vs computed true →
  verdict inequality mismatch. Same mutation shape as control family
  `verdict`, which is one of the 8/8 rejected families at baseline. The
  counter catches it.
- **V2 (assigned probe)**: recorded true while the bound run fails → caught
  twice: computed verdict (false) ≠ want (true), and the recorded observed
  (`45/45 selftest cases passed`) is absent from the failing output. **The
  recorded-vs-computed verdict check does catch a lying-green registry.**
- **V3**: a failing capability recorded honestly as false, with `observed`
  set to the actual failing output substring, contributes **zero** mismatches
  and passes every gate the counter applies (covered 12/12, bound 12,
  dead 0, errors 0, controls 8/8 rejected in the replica). `met=False` in my
  window is caused solely by V0's two environment-failed rows; in a window
  where they are green — the state in which the L1 measured C2 met=True at
  this tip — this registry scores **met=True**. End-to-end met=True was not
  realizable here because the operator wrap-up guard froze any further
  acquiring live pass. This is a falsification of the freeze's kill-rule
  clause *"a bound run whose live execution does not emit its frozen
  pattern"*: the counter implements only the symmetric
  recorded-vs-computed equality (it catches lies in both directions), never
  an absolute "computed verdict must be true". A coverage finding, reported
  as such — not a license to change the contract.

## Additional findings

1. **C2's met at tip is environment-sensitive** (operability note):
   `context-capacity-receipt` starves when no host-idle window appears within
   900 s under fleet load, and `live-ollama-lifecycle` failed at setup in
   this window. A C2 pass/fail is a property of the execution window as much
   as of the tip.
2. `digest-ledger` / `hexrun-census` bound runs require full git history;
   archive exports of the identical tree false-fail (V0a receipts).
3. Counter mechanics observed: the sensitivity check is vacuous on failing
   runs (`sensitive=True` whenever rc≠0, part of the V3 chain); the execution
   cache is keyed `(tip, cap)`, which is what let V2/V3 share one live pass.

## Integrity

- Lane untouched by me: read-only git only; master blob shas for the counter
  and registry unchanged (`15d11f1c…`, `6f8365c7…`); lane worktree churn is
  the L1's. All mutations lived in scratch fixtures; the mutated victim file
  was restored byte-exact after probing (sha256 `2e23a04e6b34b2381f403c34fd6f765ad0355315dfb79dbfd749663d946d568d`
  on both sides — `restoration-and-integrity.txt`).
- No tool installs; pacman untouched. Scratch dir removed after all receipts
  were copied into `.ufo/waves/round-62/w1/out/M12C2AttackVerdict/`:
  `00-instrument-and-fixture.txt`, `v0-baseline2.txt`,
  `v0a-baseline1-archive-fixture.txt`, `victim-variant-probe.txt`,
  `verdict-family-combination.txt`, `reg-a3.diff`, `reg-a3.tsv`,
  `claims-pristine.tsv`, `counter-copy-pinned.py`, `driver_baseline.py`,
  `driver_a2_a3.py` (designed full-pass A2/A3 driver, superseded by the
  combination path under the operator freeze), `restoration-and-integrity.txt`.

## Tally

```
population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 mismatches=4 canonical=62 controls_rejected=8/8 errors=0 met=False   (V0 baseline @ 65d7cad, full-history clone)
V1 recorded-false-while-green:   mismatches 4->5, met=False -> REJECTED (counter catches)
V2 recorded-true-while-failing:  mismatches 4->6, met=False -> REJECTED (counter catches; assigned probe answered: YES, the check catches it)
V3 honest-false-while-failing:   victim adds 0 mismatches, all gates green -> ACCEPTED (conditional realization; kill-rule clause not implemented)
```
