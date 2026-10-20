VERDICT: partial — the C2 counter's named kills are not refuted, but two detector-self assertions are one-sided (a blinded oracle leaves all 35 wrapper checks green) and one normalisation declaration is deletable without any red; the delivered counter also no longer reproduces the retained official family-(b) count.

# SimplifyC2 — counters and detector-self machinery

Seat: `KamaR18.SimplifyC2` (simplifier, leaf). Base: pushed lane master
`1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. All runtime below was executed in a
separate clone `/tmp/kama-r18-falsify-SimplifyC2` (`git clone` + `git switch -c
seat/SimplifyC2 1c325b2…`), never in the shared lane. **No production file was
edited**; the shared-tree hashes of the five C2 files equal the clone's HEAD
hashes (below). No tools installed or upgraded. No `jj`, no git writes in the
lane.

## Axes

1. **Fail-capability** — if the machinery being "self-checked" is removed or
   blinded, does the self-check go red?
2. **Authority count** — how many places must agree for one declared fact
   (mode → changed field → normalisation)?
3. **Measurement integrity** — does the delivered counter produce the number the
   claim records?
4. **No-harm** — production untouched, loopback-only ephemeral listeners,
   scratch removed.

## Green pristine baseline at HEAD (all run in the clone)

| command | exit | observed |
|---|---|---|
| `python3 tests/probe-verdicts/fault-controls.py --selftest --matrix-dir tests/probe-verdicts` | 0 | `passed=true`, `faults_checked=18`, `classifier_cases=23`, `wrapper_checks=35`, `problems=[]`; escape both ways (`direct-kill survived=true/alive_after_reap=false`, `group-kill survived=false`); F0 gate reject→code 2, accept→code 1/accepted 1; elapsed ~1 s |
| `python3 tests/probe-verdicts/check.py --selftest` | 0 | `tests=72 passes=72 failures=0`; `5/5 malformed tests rejected`; timeout cleanup pass; 38 s |
| `python3 tools/sources-append-only.py --selftest` | 0 | `42/42 selftest cases passed` |
| `python3 .ufo/waves/round-18/dispatch-provenance.py --selftest` | 0 | `selftest: 30/30 checks passed` |
| `python3 .ufo/waves/round-18/c2/survivors.py --selftest` | 0 | `selftest: 60/60 checks passed` (HEAD; the retained official artifact is 57/57 from the measured commit) |
| `python3 .ufo/waves/round-18/c2/survivors.py --family b --jobs 1 --json --out …/b.json` | 0 | `before 3 survived → after 3 killed`, `inconclusive 0/0`, frozen-witness `mismatches []`, 481.7 s, `teardown.scratch_removed=true`, bind guard `binds=474 distinct=464 protected_hits=[] listening_after.owned=[]` |

Hashes of the reviewed HEAD files (shared lane **and** clone, identical):

```
58dac1f71346734532bddc60a2d20f95f640406e924b1aec00a0b750feed072a  tests/probe-verdicts/fault-controls.py
12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5  tests/probe-verdicts/check.py
87cad1cad4565be01ce06e7f92c578c2f449c951894a880166040c3f118dc3ac  .ufo/waves/round-18/c2/survivors.py
4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d  tools/sources-append-only.py
93705f17a2b2dfeab1e80c886bcb53ae5a8e43b0c6e86e91b73a65ad5c1ea72f  .ufo/waves/round-18/dispatch-provenance.py
```

## F1 (high) — circular wrapper oracle: `selftest_wrapper` checks the wrapper against an unchecked judge

`fault-controls.py:1282-1337` (`selftest_wrapper`) runs each of the 35 non-slow
wrapper corruptions through the real wrapper and then calls
`_wrapper_problem(...)` (`:1229-1280`). A job is accepted iff
`_wrapper_problem` returns `None`. Nothing ever feeds `_wrapper_problem` an
output it must **reject**, so its discrimination is asserted only by itself.

`_wrapper_problem` is **selftest-only**: the only call site is `:1318` inside
`selftest_wrapper` (`grep -n _wrapper_problem` shows `1229` def, `1268/1271/1276`
interior, `1318` call). `run_fault` (`:882-940`) never calls it, so this is
detector-self evidence, not fault detection.

Experiments (`python3 exp/<name>.py --selftest --matrix-dir tests/probe-verdicts`,
all under the clone; base file sha `58dac1f7…`):

| mutant | edit | sha256 | exit | `passed` | problems |
|---|---|---|---|---|---|
| `fc_blind.py` | insert `return None` as first statement of `_wrapper_problem` | `e21a233a…` | **0** | **true** | **0** (35 wrapper checks) |
| `fc_normblind.py` | `served_normalised_equal` returns `True` | `136ffa28…` | **0** | **true** | **0** |
| `fc_notarget.py` (positive control) | `if target:` → `if False and target:` in `classify_run` | `087b7ab4…` | 1 | false | 8 (`classifier: … got 'own-fault'`, `target-conjunct attribution …`) |

So the same `--selftest` *is* fail-capable for the classifier, but **not** for
the wrapper judge: a judge that accepts everything is indistinguishable from
the real one, and all 35 checks become vacuous.

Repair: two negative assertions in `invoke`, reusing the same 35 jobs:
1. feed a **non-equivalent** forged value (declared field + `"X"`) and require a
   problem for every mode whose declared equivalence is not `None`;
2. feed an output with an **undeclared extra change** (extra top-level key for
   JSON modes, trailing byte for byte modes) and require a problem.

Evidence the repair is fail-capable (merged patch below; base sha
`58dac1f7…`):

| mutant | exit | `passed` | problems |
|---|---|---|---|
| `fc_merged.py` (patch only) | 0 | true | 0, `wrapper_checks=35` |
| `fc_merged_blind.py` (`return None`) | 1 | false | **35** `oracle accepted an output with an undeclared extra change` |
| `fc_merged_normblind.py` (`return True`) | 1 | false | **4** `oracle accepted a non-equivalent forged value` (F12 `case`, `gguf-suffix`, `whitespace`, `fullwidth`) |
| `fc_merged_nonom.py` (declaration deleted) | 1 | false | 1 `mode 'reason-case' has no field declaration in MODE_SPEC` |

## F2 (medium-high) — a normalisation declaration is deletable without any red, and the guard is load-bearing for H1/H5 kills

`FIELD_OF_MODE` (`:1021-1024`) and `NORMALISED_EQUAL` (`:1042-1045`) are two
independent lookups used by the same judge. The normalisation lookup is
`NORMALISED_EQUAL.get(mode)` followed by `if same and not same(...)`
(`:1275-1280`): a missing entry silently skips the equivalence check. Nothing
asserts that a mode that *declares* a normalisation still has one.

Experiment (base sha `58dac1f7…`):

| mutant | edit | sha256 | exit | `passed` | problems |
|---|---|---|---|---|---|
| `fc_nonom.py` | delete `"reason-case"` from `NORMALISED_EQUAL` | `8a50b8c3…` | **0** | **true** | **0** |
| `fc_badvariant.py` | wrapper `reason-case` emits `reason + "-forged"` instead of `swapcase()` | `d73d545a…` | 1 | false | 1 `wrapper F9[0] reason-case: 'served-id-mismatch-forged' is not 'served-id-mismatch' under the mutant's normalisation` |
| `fc_badvariant_nonom.py` | both edits above | `6f108b05…` | **0** | **true** | **0** |

The guard is not cosmetic. F9 is supposed to kill H1 because H1 compares the
reason case-insensitively. F9's forged reason must therefore be
case-equivalent to the honest one. With the weakened F9 (exact suffix) the
fault is detected by **both** the unmutated and the H1 check.py, i.e. it no
longer distinguishes the mutant:

```
real      fault-controls F9 x check.py       exit=0  F9.detected=True
real      fault-controls F9 x check_H1.py    exit=1  F9.detected=False  (check exited 0, wanted 1)
weakened  fc_badvariant  F9 x check.py       exit=0  F9.detected=True
weakened  fc_badvariant  F9 x check_H1.py    exit=0  F9.detected=True   ← indistinguishable
```

`check_H1.py` sha `4d3793d8…` (the named H1 edit from
`MUTANTS["a"]`). If such a weakened F9 shipped, family (a) would still report
H1 `killed` (fault-controls exit 1) although the fault also fires on the
unmutated detector — a false kill for the named survivor. Current production is
not weakened; this is a regression path whose only detector is the deletable
table entry.

## F3 (medium) — the delivered counter no longer produces the retained official count

The official C2 artifact and the delivered code disagree about family (b):

| | retained official artifact | HEAD (`87cad1ca…`) |
|---|---|---|
| file | `.ufo/waves/round-18/runs/c2-survivors.json`, sha `bd217de0…`, 249 500 B, started `2026-10-20T22:40:05Z`, 1577.1 s | clone run `exp/b.json`, sha `838aeada…`, 481.7 s |
| measured commit | `c6dc46fabc51…` (`tool.sha256=2af03fed…`, pre-repair) | `1c325b2e58…` |
| family (b) after | `FC-target inconclusive`, `FC-f6cache inconclusive`, `FC-f0gate killed`; `counts.after.total=2`, `inconclusive.after=2` | all three `killed`; `after.total=0`, `inconclusive=0` |
| exit | **2** | **0** |
| counter selftest | `57/57` (`runs/c2-counter-selftest.stdout`, sha `545e2ebe…`, 43.277 s) | `60/60` (43.5 s) |

Cause: `combine_arms` (`survivors.py:976-985`) was changed after the measurement
(`git diff c6dc46f..HEAD -- .ufo/waves/round-18/c2/survivors.py`): at the
measured commit `inconclusive` won over `killed`; at HEAD `killed` wins when any
arm is conclusive, and three regression cases were added (`:1732-1750`). The
change itself is sound — the FC-target/FC-f6cache main arms are own faults
(`fault-controls: own fault: F1: fault declares no target conjunct`, because
`if False and target:` skips the success return and falls into the raise), and
an own fault is not evidence either way; the targeted selftest kill is. This is
exactly the KQ24 "a real evaluated result dominates a missing observation"
rule applied to detector arms.

But the SCORECARD/lesson text still records the pre-repair raw result ("two FC
inconclusives"), and no corrected rerun exists in `runs/`. A reader rerunning
the delivered command gets a different number than the claim records. Either
retain a post-repair official run artifact, or keep the pre-repair number and
state the composite repair is unmeasured. The original failed artifact must
stay (it is retained history).

## F4 (low, real deletion) — the inconclusive status set is duplicated verbatim

`survivors.py:1444-1447` and `:1597-1601` both spell
`{"inconclusive", "error", "not_exercised", "baseline_invalid"}`. `count()`
produces `counts["inconclusive"]`; `run_count()` re-derives the per-item list
for `inconclusive_reasons`. They should be one module constant (next to `GOOD`
at `:214`). No behavioral change expected; the exit decision reads
`counts["inconclusive"]`, so the only failure mode today is a diagnostics list
that silently omits an item if one literal is edited. Delete candidate: one
literal, two sites → one constant.

## F5 (low, examined, not recommended as a pure deletion) — an unreachable kill branch

`classify_a` (`:882-907`) returns `killed` on any `exit == 1` at `:898` before
the `decision["accepted"] > 0` branch at `:899-901`; `fc_view.accepted_ids`
(`:873-874`) exists only for that branch's message. `run_suite` sets
`code = 0 if accepted_n == 0 else 1` (`fault-controls.py:1008`), so for the
real tool `exit 1 ⇔ accepted>0` and the branch is unreachable. It is defensive
code with no reachable producer. Deleting it as-is would make an impossible
inconsistent document (exit 0, accepted>0) fall through to `survived`; if it is
deleted, the inconsistency should become `inconclusive`, not `survived`. Low
value — leave it or convert it, do not simply cut it.

## Retained complexity (deletion candidates rejected, with evidence)

1. **`served_ids_of` duplicated in `check.py:311` and `fault-controls.py:574`**
   (bodies byte-identical apart from the docstring) and the two derived
   functions `expected_served_model` (`check.py:357`, keyed on the observed
   verdict) vs `contract_served_model` (`fault-controls.py:607`, keyed on the
   row's routes/status). **Do not merge.** `fault-controls` judges *copied and
   mutated* `check.py` files; importing the subject's function would let a
   family-(a) mutant change its own judge. The two derivations currently agree
   on all 72 matrix rows (`expected != contract: 0`), which is the preserved
   contract. Tradeoff: divergence is not tested; if wanted, a one-off
   differential assertion inside `fault-controls --selftest` over the already
   staged matrix bodies would cover it without a new file.
2. **`parser_rejected and recorded_failure` in `check.py`'s malformed-output
   selftest** looks redundant (both derive from `probe_output_row`), but the
   first conjunct pins the exception-type prefix (`RecursionError:` /
   `ValueError:`) while the second pins `grade`'s `malformed probe output:`
   plumbing. Two different contracts; keep.
3. **`_CELL_EDIT_EXIT` in `sources-append-only.py:371-375`** is written out
   independently of the compared-set constant (`opened` denied, `status`
   allowed, etc.), and the provenance selftest recomputes the canonical-hash
   formula literally and pins `ensure_ascii=False`. Both are independent
   oracles, not circular; 42/42 and 30/30. Keep.
4. **The 35 wrapper checks are not deletable.** They are only "weight" if the
   oracle discriminates; F1/F2 are about making that true, not about removing
   the checks.
5. `fault-controls.py:69-73` docstring says `--selftest` validates "every
   wrapper corruption against a canned probe document". Literally true, but it
   validates wrapper→oracle, not oracle→intent. If the patch is not taken,
   qualify that sentence.

## Recommended patch (tested in scratch; **not applied**)

Two options, both from base `58dac1f7…`:

- **B (recommended, single authority):** replace `FIELD_OF_MODE` +
  `NORMALISED_EQUAL` + the two-lookup block in `_wrapper_problem` with one
  `MODE_SPEC` table, and add the two negative controls. Unknown modes become an
  error instead of a skipped check, and a mode cannot declare a field without
  also declaring its equivalence. Diff: **+47 / −13** (net +34).
- **A (smaller diff, keeps two tables):** add a `NORMALISING_MODES` constant
  and fail closed when a normalising mode has no entry, plus the two negatives.
  Diff: **+33 / −8** (net +25). It fixes the same two failure modes but adds a
  third declaration source; less aligned with "one authority".

Option B's exact diff (`diff -u tests/probe-verdicts/fault-controls.py
exp/fc_merged.py`; the patched file sha is `b03b3a49…`):

```diff
@@ -1018,10 +1018,27 @@
              "error"}
 
 # Wrapper corruption -> the one row field it may change.
-FIELD_OF_MODE = {"reason": "reason", "reason-case": "reason",
-                 "verdict": "verdict", "verdict-pad": "verdict",
-                 "drift": "drift", "served": "served_model",
-                 "served-norm": "served_model", "first-row": "reason"}
+# One declaration per corrupting mode: (field it may change, how the forged
+# value must relate to the honest one). None means plain inequality is the
+# whole claim; "variant" defers to served_normalised_equal(run["variant"]).
+def _casefold_equal(forged, honest):
+    return forged.casefold() == honest.casefold()
+
+
+def _strip_equal(forged, honest):
+    return forged.strip() == honest
+
+
+MODE_SPEC = {
+    "reason": ("reason", None),
+    "reason-case": ("reason", _casefold_equal),
+    "verdict": ("verdict", None),
+    "verdict-pad": ("verdict", _strip_equal),
+    "drift": ("drift", None),
+    "served": ("served_model", None),
+    "served-norm": ("served_model", "variant"),
+    "first-row": ("reason", None),
+}
@@ -1039,10 +1056,6 @@
     return apply(forged) == apply(honest)
 
 
-NORMALISED_EQUAL = {
-    "reason-case": lambda forged, honest: forged.casefold() == honest.casefold(),
-    "verdict-pad": lambda forged, honest: forged.strip() == honest,
-}
@@ -1265,15 +1278,15 @@
     forged = rows[0]
     changed = sorted(k for k in set(forged) | set(honest)
                      if forged.get(k) != honest.get(k))
-    field = FIELD_OF_MODE.get(mode)
+    if mode not in MODE_SPEC:
+        return f"mode {mode!r} has no field declaration in MODE_SPEC"
+    field, same = MODE_SPEC[mode]
     if changed != [field]:
         return f"changed {changed}; the fault declares only {field!r}"
-    if mode == "served-norm":
+    if same == "variant":
         same = lambda forged, honest: served_normalised_equal(
             forged, honest, run["variant"])
-    else:
-        same = NORMALISED_EQUAL.get(mode)
-    if same and not same(forged[field], honest[field]):
+    if same is not None and not same(forged[field], honest[field]):
         return (f"{forged[field]!r} is not {honest[field]!r} under the "
                 "mutant's normalisation, so it cannot kill that mutant")
     return None
@@ -1317,6 +1330,27 @@
             problem = _wrapper_problem(run, proc.returncode, proc.stdout,
                                        canned)
+            if problem is None:
+                if run["mode"] in MODE_SPEC and \
+                        MODE_SPEC[run["mode"]][1] is not None:
+                    altered = json.loads(proc.stdout)
+                    altered["rows"][0][MODE_SPEC[run["mode"]][0]] += "X"
+                    if _wrapper_problem(
+                            run, proc.returncode,
+                            json.dumps(altered).encode(), canned) is None:
+                        problem = ("oracle accepted a non-equivalent "
+                                   "forged value")
+                if problem is None:
+                    if run["mode"] in ("malformed", "pass") or \
+                            run["mode"] in REPLAY_MODES:
+                        bad = proc.stdout + b"x"
+                    else:
+                        bad = json.dumps(dict(json.loads(proc.stdout),
+                                              undeclared_extra=1)).encode()
+                    if _wrapper_problem(run, proc.returncode, bad,
+                                       canned) is None:
+                        problem = ("oracle accepted an output with an "
+                                   "undeclared extra change")
             if problem is None and cache is not None:
```

Tradeoff: option B is **not** a byte reduction (net +34). It removes one
duplicated dispatch authority and one fail-open path, and makes the existing 35
wrapper checks fail-capable; the added lines are negative controls, not new
abstraction. Option A is +25 lines and keeps the two tables. Table-only (merge
without negatives) is +26/−13 (net +13) and closes F2 but **not** F1: with
`fc_tableonly_blind.py` and `fc_tableonly_normblind.py` the selftest is still
exit 0/passed true (measured), while `fc_tableonly_nonom.py` is exit 1 with
`mode 'reason-case' has no field declaration in MODE_SPEC`.

## KQ23 / KQ24 relevance

- **KQ23** (account for every post-arming write to the deciding state): here the
  deciding read is `_wrapper_problem`'s return and the "arming" is the
  normalisation declaration. `fc_nonom` removes the arming and the observed
  result is unchanged (green), which is the assertion-level analogue of a reset
  that silently undoes the handler. The patch makes the removal observable and
  the declaration single-sourced.
- **KQ24** (do not collapse unobserved into failed/pass): the counter's
  `killed/survived/inconclusive` and fault-controls' `exit 2` own fault are the
  three-way split; HEAD's `combine_arms` correctly lets a conclusive targeted
  kill dominate an own-fault arm. The retained official artifact predates that
  rule and records the two arms as `inconclusive`; the number must not be
  retro-edited, but the delivered code's number needs its own artifact.

## Reproducibility

- Clone: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin
  /tmp/kama-r18-falsify-SimplifyC2 && git -C … switch -q -c seat/SimplifyC2
  1c325b2e58fcfdc6761f645b44cedfb1d65243e6`.
- All mutants are byte-exact single replacements of the SHA-pinned base file;
  the replacement recipes are the diff above plus the one-line tampers named in
  F1/F2/F5. Mutant hashes used in this report:
  `fc_blind.py e21a233a…`, `fc_normblind.py 136ffa28…`, `fc_nonom.py 8a50b8c3…`,
  `fc_notarget.py 087b7ab4…`, `fc_badvariant.py d73d545a…`,
  `fc_badvariant_nonom.py 6f108b05…`, `fc_fixed.py 64e4f494…`,
  `fc_fixed_blind.py a206d5c4…`, `fc_fixed_normblind.py 524d1356…`,
  `fc_fixed_nonom.py fa80c427…`, `fc_merged.py b03b3a49…`,
  `fc_merged_nonom.py c846d42d…`, `fc_merged_badvariant.py a5faaf0e…`,
  `fc_merged_blind.py 2a4b315b…`, `fc_merged_normblind.py c080dd41…`,
  `fc_tableonly.py adc0b88f…`, `fc_tableonly_nonom.py c5e41e05…`,
  `fc_tableonly_blind.py 59fa674c…`, `fc_tableonly_normblind.py dd92267e…`,
  `check_H1.py 4d3793d8…`, family-b rerun `b.json 838aeada…`.
- Commands: `python3 exp/<mutant>.py --selftest --matrix-dir
  tests/probe-verdicts`; `python3 tests/probe-verdicts/fault-controls.py
  --check <check.py> --probe <clone>/tools/kama-probe.sh --matrix-dir
  <clone>/tests/probe-verdicts --only-fault F9 --json` (absolute paths: relative
  probe paths fail F0 because the wrapper runs from a temp cwd — observed exit
  2, `suite INVALID — positive control F0 failed`, not a defect in the tool).
- Scratch `/tmp/kama-r18-falsify-SimplifyC2` was removed after this report; the
  report carries the patch and recipes.

## Limits and disclosures

- Only family (b) and the selftests were rerun; families (a), (c), (d), (e) are
  read from the retained official artifact, not reproduced by this seat. I did
  not rerun the full official counting command (it takes ~26 min and belongs to
  L1).
- No production, fleet, sibling-repo, frozen-evidence or old-lesson edits. The
  five C2 file hashes in the shared lane equal HEAD (listed above). Other seats'
  modifications visible in `git status` (`PROVINCE.md`, `SKILL.md`,
  `corpus/README.md`, `make_spec.py`, …) are not mine and were not touched.
- One concurrency deviation: `fc_nonom`'s selftest (≈1 s) overlapped the
  family-b counter rerun in the same seat. Both only bind port-0 loopback stub
  servers via the counter's guard; no registered port was used. Final checks:
  no listener on 8080/34113; no process references this seat's clone/scratch;
  my family-b run reports `teardown.scratch_removed=true` and
  `listening_after.owned=[]`. Three *other*-seat counter suites (`a/H*`,
  scratch `/tmp/kama-c2-survivors-*`) were live during the final scan and are
  not attributable to this seat (this seat ran only `--family b`).
- No language server was mounted in this seat, so "no semantic callers" proofs
  here are exhaustive in-file call-site enumeration plus greps of the reviewed
  file set, not LSP `references`. That is weaker than semantic proof; the
  affected claims are the F4/F5 deletion candidates only, and both are marked
  low-value and not applied.
- No tools installed or upgraded (tooling directive: nothing to record).
