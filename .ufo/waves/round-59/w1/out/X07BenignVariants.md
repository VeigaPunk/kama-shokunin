# X07BenignVariants — round 59 w1 (kama)

Item: Verify B1-B3 are behavior-preserving rewrites of genuine and accepted under frozen C1 counter. Include diffs and outcome.

Seat type: falsification probe (leaf). Advisory only; not a judge. No axis movement claimed, no S517/S518 discernment progress claimed.

## Verdict

| item | attacked clause | result |
|---|---|---|
| B1-rename-comment | C1-r59 "genuine+3/3 benign accepted, 0 eval errors" (counter predicate frozen at 494c1657) | **accepted**, exit 0; behavior-identical to genuine |
| B2-helper-leg | same clause | **accepted**, exit 0; behavior-identical to genuine |
| B3-concat-labels | same clause | **accepted**, exit 0; behavior-identical to genuine |
| genuine (reference) | same clause | **accepted**, exit 0 |

All three benign variants are behavior-preserving rewrites of `tests/round58-battery-variants/genuine.py`, established two ways: (a) textual diff at the frozen tip, (b) frame-level identity of the checker's profiled observations (labels, argv, per-leg return values, battery exit) in the baseline and under each of the checker's four one-leg fault injections. The frozen C1 counter accepts all three with `met=True`, `errors=0`.

## Frozen target and command

- lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only use)
- measured tip: `aca8d0067ea25627c5015c2193c843965148bc8e` (C1 measured commit)
- scratch: `/fast/scratch/hyaku/kama-r59/X07BenignVariants` (removed before yield)

Exact command (TMPDIR explicit, cwd = scratch, absolute script path, no lane writes):

```
export TMPDIR=/fast/scratch/hyaku/kama-r59/X07BenignVariants
cd /fast/scratch/hyaku/kama-r59/X07BenignVariants
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c1-counter.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip aca8d0067ea25627c5015c2193c843965148bc8e \
  --work /fast/scratch/hyaku/kama-r59/X07BenignVariants \
  --out .../w1/out/X07BenignVariants/c1-counter.out
```

Exit `0` in 4.27 s. Full output (sha256 `84856a06eaeeda4f77952a52ec328618e49e8ea2035dc5523bf616142746cf48`), byte-identical in substance to frozen pre-data receipt `controls/c1-candidate-final.out` except that receipt's own copy:

```
tip=aca8d0067ea25627c5015c2193c843965148bc8e
predicate=C1-r59 outcome-binding checker accepts genuine+3/3 benign and rejects 16/16 no-ops, errors=0
genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True
detail: genuine accept exit=0
detail: B1-rename-comment accept exit=0
detail: B2-helper-leg accept exit=0
detail: B3-concat-labels accept exit=0
detail: N01-calls-removed reject exit=1
... N02..N11 reject exit=1 ...
detail: N12-ignore-leg-result reject exit=1
detail: N13-wrong-leg-expected reject exit=1
detail: N14-ignore-mutant-result reject exit=1
detail: N15-duplicate-leg-label reject exit=1
detail: N16-decoy-counter-call reject exit=1
```

B1/B2/B3 are selected by `BENIGN` in `tools/round59-c1-counter.py:11` and read from `VARIANT_DIR = "tests/round58-battery-variants"` (line 22); the counter loads each blob from the passed tip, builds a throwaway fixture repo per variant, and runs `tools/round59-battery-outcome-check.py` against it.

## Diffs (frozen-tip blobs, `genuine.py` → variant)

Blob hashes at `aca8d006` (identical to working tree, verified):

```
genuine            69b77a6a64f2667757842c2471ddc256d12ceb5ccca6df0a57b88bbe17ab51c5
B1-rename-comment  844f306004b2505546f10f58d448787a0ea483c8321d5d0b50a00692fdee35d3
B2-helper-leg      84ef76673347fcb18011e5a1ea67657016e648a6d1ee25195e244ebc66a66628
B3-concat-labels   f1e9597afa3dc2d3a638b228c3663e1fae788e0cb3ed69c4359d8c55ad07eb36
```

### B1-rename-comment (rename local `results` → `outcomes`, add one comment; no semantic change)

```diff
 def main():
+    # create the receipt directory first
     OUT.mkdir(parents=True, exist_ok=True)
     scratch = pathlib.Path("/fast/scratch/hyaku/kama-r56/l1-battery")
     scratch.mkdir(parents=True, exist_ok=True)
-    results = []
-    results.append(comparator_selftest(OUT / "comparator-selftest.out"))
-    results.append(run("base-old-counter", OLD, "missed", OUT / "base-c1.out"))
-    results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))
+    outcomes = []
+    outcomes.append(comparator_selftest(OUT / "comparator-selftest.out"))
+    outcomes.append(run("base-old-counter", OLD, "missed", OUT / "base-c1.out"))
+    outcomes.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))
     with tempfile.TemporaryDirectory(prefix="mutant-", dir=scratch) as d:
         ...
-        results.append(run("m-drop-ldaudit", mutant, "missed", OUT / "m-drop-ldaudit.out"))
-        results.append(assert_mutant_breaks_detection(
+        outcomes.append(run("m-drop-ldaudit", mutant, "missed", OUT / "m-drop-ldaudit.out"))
+        outcomes.append(assert_mutant_breaks_detection(
             mutant, OUT / "m-drop-ldaudit-target-fails.out"))
-    return 0 if all(results) else 1
+    return 0 if all(outcomes) else 1
```

No stale `results` reference remains (all 6 references renamed; execution exit 0 confirms).

### B2-helper-leg (identity delegation through a new helper; same positional args)

```diff
+def _leg(label, counter, expected, out):
+    return run(label, counter, expected, out)
+
+
 def main():
     ...
-    results.append(run("base-old-counter", OLD, "missed", OUT / "base-c1.out"))
-    results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))
+    results.append(_leg("base-old-counter", OLD, "missed", OUT / "base-c1.out"))
+    results.append(_leg("round56-counter", NEW, "detected", OUT / "build-c1.out"))
     ...
-        results.append(run("m-drop-ldaudit", mutant, "missed", OUT / "m-drop-ldaudit.out"))
+        results.append(_leg("m-drop-ldaudit", mutant, "missed", OUT / "m-drop-ldaudit.out"))
```

`_leg` forwards `(label, counter, expected, out)` in the exact order of `run`'s signature; the mutant-assert leg remains a direct `assert_mutant_breaks_detection` call. No leg is rerouted.

### B3-concat-labels (constant-folded string concatenation; same runtime labels)

```diff
-    results.append(run("base-old-counter", OLD, "missed", OUT / "base-c1.out"))
-    results.append(run("round56-counter", NEW, "detected", OUT / "build-c1.out"))
+    results.append(run("base-" + "old-counter", OLD, "missed", OUT / "base-c1.out"))
+    results.append(run("round56-" + "counter", NEW, "detected", OUT / "build-c1.out"))
```

Both concatenations evaluate to the original labels; the checker's runtime label set is unchanged.

## Behavior-equivalence evidence (stronger than "accepted")

Method: fresh fixture repo per variant in scratch (`git -C <fx> init`, assert `rev-parse --show-toplevel` == fixture dir, `user.name=x07-probe`, `user.email=x07@invalid`, never a throwaway identity outside the fixture), battery file = variant blob, side files from tip `aca8d006`. For each variant I invoked the frozen checker's own child harness directly in all five modes: `--fault ""` (baseline) plus one fault per leg (`base-old-counter`, `round56-counter`, `m-drop-ldaudit`, `mutant-assert`):

```
python3 <lane>/tools/round59-battery-outcome-check.py --child \
  --repo <fixture> --tip HEAD --source <fixture>/tools/round56-env-leg-battery.py \
  --out out.json --fault <fault>
```

Compared the full profiled frame list (label, argv of each leg's subprocess call, per-leg returned bool) and the battery exit code.

Result: for all four variants in all five modes the frames are exactly equal to genuine's; the exit codes are equal as well. Per-leg returns (identical for genuine, B1, B2, B3):

```
baseline            exit=0  base-old=True  r56=True  m-drop=True  mutant-assert=True
fault base-old      exit=1  base-old=False r56=True  m-drop=True  mutant-assert=True
fault r56           exit=1  base-old=True  r56=False m-drop=True  mutant-assert=True
fault m-drop        exit=1  base-old=True  r56=True  m-drop=False mutant-assert=True
fault mutant-assert exit=1  base-old=True  r56=True  m-drop=True  mutant-assert=False
```

Baseline argv (identical across variants; representative):

```
base-old-counter -> python3 <lane>/tools/round56-env-leg-test.py --counter <lane>/tools/round54-replay-code-audit.py --expect missed
round56-counter  -> python3 <lane>/tools/round56-env-leg-test.py --counter <lane>/tools/round56-replay-code-audit.py --expect detected
m-drop-ldaudit   -> python3 <lane>/tools/round56-env-leg-test.py --counter /virtual/round59/counter.py --expect missed
mutant-assert    -> python3 <lane>/tools/round56-env-leg-test.py --counter /virtual/round59/counter.py --expect detected
```

So B1-B3 preserve, for every leg, the leg's own `--counter`/`--expect` argv, the leg's bound observed outcome, and the leg-local fault propagation: a one-leg fault fails exactly that leg and flips the battery to exit 1, identically to genuine. Acceptance is substantive, not vacuous.

Evidence files (in this dir):
- `c1-counter.out` — frozen counter output, exit 0, sha256 `84856a06eaeeda4f77952a52ec328618e49e8ea2035dc5523bf616142746cf48`
- `frame-equivalence.json` — all 20 child outcomes (4 variants × 5 modes), sha256 `a9fd2557e62fe0b70dbe8677f3a25c99740e9360cb06a4529743731d6c4c55ce`

## Provenance / calibration notes (advisory, not a kill)

- Freeze ordering verified: `5d957d24` (freeze claims/kill rules) → `494c1657` ("add outcome and calibration gates": r59 counter, r59 checker, N12-N16) → `114fdf78` (pre-data control receipts incl. `c1-candidate.out`) → `aca8d006` (measured). `494c1657` is an ancestor of `114fdf78`, which is an ancestor of `aca8d006`. No data preceded the frozen counter/checker.
- **B1-B3 are inherited round-58 artifacts**, added at `dcd69473` ("round-58: freeze C1/C2 counters, variant set and predicates before data"). `controls/make-variants.py` for round 59 generates only N12-N16 and does not regenerate the benign trio; `round59-c1-counter.py` reuses `tests/round58-battery-variants` for `BENIGN`. The blobs are unchanged from `dcd69473` through `aca8d006`, and unchanged from `aca8d006` to fleet-lane HEAD `4a541190` (empty `git diff aca8d006..HEAD` over all four C1 artifact paths), so the reuse is of pre-data bytes, not post-hoc edits.
- The phrase "3/3 benign" therefore carries **no new discriminative information about benign rewrites**: the same trio already scored `benign=3/3` in `round-58/measured/c1-final.out` (r58 exec checker, no per-leg fault injection). What is new in round 59 is that the same trio is re-accepted by a structurally different checker (`tools/round59-battery-outcome-check.py`, per-leg fault propagation via profiler), which is a stronger form of the same pass, not fresh evidence. New discrimination in C1-r59 comes from N12-N16; those are outside this item and are not attacked here.
- Minor wording gap, not a failure: `freeze.txt` names the finite controls directory `tests/round59-battery-variants`, while the benign controls actually live in `tests/round58-battery-variants`. This is consistent with "preserve prior variants" but means the frozen control set is split across two directories; a reader checking only the round-59 directory would not see B1-B3.
- No installs or updates were made (nothing was needed); pacman untouched.

## Not run / deliberate bounds

- The genuine battery was **not** executed unharnessed: `tests/round58-battery-variants/genuine.py` hardcodes `LANE = /home/vgpnk/Projects/shokunin/kama-shokunin` and writes under `LANE/.ufo/waves/round-56/measured`, which would violate the read-only lane bound. All execution went through the checker's virtualized child harness (path reads via `git show`, writes virtualized), i.e. exactly how the frozen counter exercises the battery. No divergence between harnessed and real execution was measured or assumed; this is a stated bound on the evidence.
- No source edits, no commits, no pushes, no sibling-lane or fleet touches, no task/spawn. Only this dir plus `/fast/scratch/hyaku/kama-r59/X07BenignVariants` were written; scratch removed before yield.

## Risk / blocker

- None blocking. Residual risk: acceptance of B1-B3 depends on the checker profiling by function name `run`/`assert_mutant_breaks_detection`; B2 shows a same-file helper wrapper is not itself gated (it delegates identically here). A helper that altered argv or returned a constant would be caught only insofar as it perturbs the glued frame (as N12/N14/N15/N16 test). That is a property of the frozen checker, not of the benign set, and is reported for the judge; it does not change this item's outcome.
