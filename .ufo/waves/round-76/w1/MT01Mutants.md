# rev=b06cc612711560c53eef3ec21484c6963601262f
# MT01 — frozen-base probes and pre-registered counter mutants

Axes: operability (gradeability without population loss), calibration (value-bound facts), freshness (event accounting and earliest cutoff).

Read the entire frozen plan (206 lines); did not change it. Frozen module extracted with `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show b06cc612711560c53eef3ec21484c6963601262f:tools/round72-receipt-tip-binding.py`. Only own scratch copies were mutated. No commits, installations, lane-source changes, or fixture git mutations.

## 1. Frozen-base effects

Every probe used exactly:

```sh
python3 /fast/scratch/hyaku/kama-r76/MT01Mutants/round72-receipt-tip-binding.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --round 75 --tip b06cc612711560c53eef3ec21484c6963601262f
```

Pristine exit **2**, stdout empty, stderr:

```text
RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.py): .ufo/waves/round-75/controls/build-spec.py (corpus/lessons/round-75.md:125)
```

| id | Frozen source point / exact edit in scratch | Expected detector | Observed result | Verdict |
|---|---|---|---|---|
| A | `_expand_one`, lines 324–328: replace non-receipt exception with `return []` | Same round-75 command; can the record grade? | exit 1; `cited=11 bound=6 unbound=2 shifted=3 stale=0` | Gradeable, not clean. Inconclusive as a mutation kill because pristine already exits 2. |
| B | module line 114: append `".py"` to `RECEIPT_EXTS` | Does admitted fenced source bind? | exit 1; `cited=13 bound=6 unbound=4 shifted=3 stale=0` | No: build-spec.py AND mutation-control.py are unbound. Inconclusive kill. |
| C | `_citations`, line 408: add fence-state walk before token iteration, ignoring fenced lines | Population with fenced bytes invisible | exit 1; `cited=11 bound=6 unbound=2 shifted=3 stale=0` | Population remains 11, not zero. Inconclusive kill. |

C's exact replacement for original line 408:

```python
    fence = None
    for i, line in enumerate(lines):
        if fence is not None:
            ch, n = fence
            stripped = line.lstrip(" ")
            k = len(stripped) - len(stripped.lstrip(ch))
            if len(line) - len(stripped) <= 3 and k >= n and not stripped[k:].strip(" \t"):
                fence = None
            continue
        opener = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if opener and not (opener[1][0] == "`" and "`" in opener[2]):
            fence = (opener[1][0], len(opener[1]))
            continue
```

This is a bounded fence-visibility probe, not a complete replacement counter: it does not reject an unclosed fence. The grammar uses the existing audit's opening/closing rules; original token loop remains after it.

Exact stdout/stderr, commands, exits and SHA-256 values for pristine, A/B/C and each restoration are in `MT01Mutants/runs.json` and the corresponding `<label>.stdout.out` / `<label>.stderr.out` receipts. These are raw command streams after the required revision header. A and C report the same five findings: header-less assimilation/summary.out and controls/freeze.txt; PROVINCE.md shifted before/c1-mutants.out, before/c2-mutants.out and before/c3-audit.out. B additionally reports the two source files unbound.

## 2. Pre-registration: C1 and C2 absent at observation

Both `tools/round76-receipt-scope.py` and `tools/round76-selfrecord-facts.py` were absent at initial discovery and at the start of execution. Thus these are **red-first registrations, NOT executed passes or kills**. Implementers supplied planned function anchors. Numeric source lines cannot honestly be supplied for nonexistent files; the exact statement anchor below is the line selector, to be resolved after landing. This is an explicit prerequisite gap, not a fabricated line number.

Each mutation is independent, applied only to a pristine scratch copy; detector is `python3 <scratch-copy> --repo /home/vgpnk/Projects/shokunin/kama-shokunin --selftest` (C1 also passes `--work /fast/scratch/hyaku/kama-r76/MT01Mutants/fixtures` if its interface supports it). Record baseline and restored outputs with the same invocation. A baseline failure makes the result inconclusive. Survivor criterion for every row: pristine and restored suites pass, mutation changes production behavior, but the named arm remains green and no other arm fails.

| id | File / function / line selector | Exact pre-registered edit | Expected frozen arm / required red observation |
|---|---|---|---|
| C1-E | tools/round76-receipt-scope.py / audit / empty-live guard | Replace the empty-live could-not-evaluate branch with a clean zero-population return, preserving the normal result schema | fence-none-live: must no longer see required exit 2 |
| C1-U | same / audit / unclosed-fence guard | Replace the unclosed-fence rejection condition with `False` | fence-unclosed: must no longer see required exit 2 |
| C1-N | same / audit / live nonreceipt classifier | Omit the nonreceipt finding and continue to next live citation | fence-live-nonreceipt: must fail required exit 1 AND named finding |
| C1-T | same / _classify_receipt / changed-path exclusion test | Replace the test rejecting a path outside record specs with `False` | shift-tools: tools/ drift becomes bound, violating exit 1 |
| C2-Z | tools/round76-selfrecord-facts.py / main / normal audit call | Replace normal evaluation body with `print("SELFRECORD_FACTS claims=8 mismatches=0 corrected=5 unbacked=0"); return 0` | cheat arm: stale fixture must still report five named mismatches, exit 1 |
| C2-V | same / apply_correction / `if value != expected:` | Change to `if False:`; leave remaining correction acceptance intact | correction-wrong-value: wrong correction must not be accepted |

Additional planned C1 arms (not frozen named kill arms): fence-quoted-skip is challenged by removing `_fence_flags` filtering; shift-selfdesc by removing PROVINCE.md from specs; unbound-named by classifying missing headers as bound. These are not claimed measured results.

## 3. C3 appeared during execution: applied matrix

`tools/round76-append-exempt.py` landed during the probe. Captured source SHA-256 `c9e3bf8d788442fe29e10b6461410397a9a1f1f20d459358c53256015255fb21`. Independent scratch copies were tested concurrently, never modified in the lane.

Detector for each id:

```sh
python3 /fast/scratch/hyaku/kama-r76/MT01Mutants/c3-<id>.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --selftest
```

Pristine and every restored detector report exit **1**:

```text
APPEND_EXEMPT_SELFTEST audit-fixture-green FAIL exit=1 expected=0
APPEND_EXEMPT_SELFTEST missing-row PASS exit=1 expected=1
APPEND_EXEMPT_SELFTEST wrong-count PASS exit=1 expected=1
APPEND_EXEMPT_SELFTEST wrong-class PASS exit=1 expected=1
APPEND_EXEMPT_SELFTEST rotation-reintroduced PASS exit=1 expected=1
APPEND_EXEMPT_SELFTEST pass=4 fail=1
```

| id | File / function / exact line edit | Expected arm | Observed mutant output (exit always 1) | Verdict |
|---|---|---|---|---|
| missing | c3-missing.py / grade / 165: replace `bad("unaccounted", ...)` with `buckets["exempt"] += 1` | missing-row | missing-row FAIL, pass=3 fail=2 | Inconclusive; arm detects difference but baseline red |
| count | c3-count.py / grade / 136: remove `or int(count) != event["ungraded"]` | wrong-count | wrong-count FAIL, pass=3 fail=2 | Inconclusive; arm detects difference but baseline red |
| class | c3-class.py / grade / 132: remove `or klass != CLASS` | wrong-class | unchanged: wrong-class PASS; pass=4 fail=1 | Inconclusive; apparent escape masked by failed green fixture |
| rotation | c3-rotation.py / introduction_history / 86: `return introductions[::-1]` | rotation-reintroduced | unchanged: rotation-reintroduced PASS; pass=4 fail=1 | Inconclusive; earliest-cutoff selection not exercised by injected ancestry callback |
| audit | c3-audit.py / read_audit / 50: `if process.returncode not in (0, 1):` → `if False:` | audit-fixture arms | unchanged: pass=4 fail=1 | Inconclusive; no audit-failure fixture detects missing failure guard |

Frozen plan names `audit-fixture arms` collectively, not individual arm names. Landed implementation has only audit-fixture-green. Its failure means none of the above is a valid whole-suite kill or proven survivor. Exact outputs and commands are preserved, including restored runs under each mutant's identical pathname.

### Findings and behavior differences

1. **Observed baseline failure:** C3's own green arm is red before mutation and after restoration. Do not report five kills from five nonzero exits.
2. **Cutoff coverage gap [INFERENCE]:** reversing introduction_history changes the selected cutoff from earliest to latest when there are multiple introductions; rotation-reintroduced injects a list and callback at grade(), and does not run real delete/re-add history. Its output is unchanged under this defect. This is an apparent semantic escape, not a proven survivor because baseline fails and the current history need not contain multiple introductions.
3. **Audit failure coverage gap [INFERENCE]:** removing subprocess exit-code validation would accept valid JSON from a failing audit. Existing healthy-audit fixture has unchanged output; no failing-audit arm exists in the captured source. Again not a scored survivor.
4. **Wrong-class arm masking:** removing only class equality leaves wrong-class green. Other eligibility failures may mask the removed check; the failed green fixture prevents attributing this to useful coverage. Requires a passing baseline before scoring.

No contract changes are proposed. Frozen counts and exit map remain authoritative. C3 source re-derives exemption sections itself; its header states the frozen audit does not serialize an exemption class. This is an implementation/plan interface difference to record, not permission to edit the plan.

## 4. Restoration, provenance and cleanup

Base copy SHA-256 before and after EACH mutation: `a9a4e8d30546a11e6d5165b566e856e4eb8cccb11d48c5526587fd3d859b2bbd`. Restored base command consistently returns the same exit-2 bytes. All five C3 copies restored byte-identically to captured source hash above; each restored selftest yields the same baseline failure. Mutant hashes and outputs are in runs.json. All scratch files are deleted after receipt persistence, before terminal handoff.

Receipt revision identifies the fixed round-75 data revision for the base probe. C3 source was uncommitted working-tree content supplied by its owner; its hash above, not the receipt header, identifies those bytes. C3 invokes the audit against the lane's committed revision, unlike the base's explicit --tip; no claim is made that its source exists at the base revision.

Self-evaluation: accuracy 4 (C3 baseline forbids scored kills), completeness 4 (absent C1/C2 prevent numeric source anchors or runs), clarity 4 (raw streams separated from interpretations), actionability 4 (all landed C3 edits numeric; missing modules use statement anchors), conciseness 4 (19 runs retained outside prose); mean 4.0. Highest-impact next action is to establish a passing C3 baseline, then repeat the registered mutations; C1/C2 registrations require landed source. No installation or update performed.

## 5. Subsequent arrivals: C1 and C2 matrix executed

This measured section supersedes the earlier availability limitation and self-evaluation's missing-run caveat: both tools arrived before handoff. All 33 runs are retained in runs.json. No tool source in the lane was changed.

C1 captured source SHA-256 `ea1bc4c5405c22ba7966582de11a77da48248f3250fe950ecc6cf4a4bbf184c0`; C2 `98e874495faddfbcf0004609a14471842fc8bf98f21ebe4e6219654591212674`. Imported r72/r73/audit dependencies copied into own scratch; bytecode disabled by C1. C1 fixtures assert ownership before commits; C2 fixtures write only their own raw object trees.

C1 exact commands substitute `pristine`, `empty`, `unclosed`, `nonreceipt`, or `tools` for `<id>`:

```sh
python3 /fast/scratch/hyaku/kama-r76/MT01Mutants/c1-<id>.py --selftest --work /fast/scratch/hyaku/kama-r76/MT01Mutants/fx-<id>
```

Pristine exit 0 `RECEIPT_SCOPE_SELFTEST pass=7 fail=0`; each restored copy under the same invocation exits 0 with the same seven arms green.

| id | tools/round76-receipt-scope.py source function / exact edit | Expected arm | Observed | Verdict |
|---|---|---|---|---|
| empty | audit line 153 `if not live:` → `if False:` | fence-none-live | expect=2 got=0 FAIL; live_citations=0; suite pass=6 fail=1 exit 1 | killed |
| unclosed | _fence_flags line 68 `if fence is not None:` → `if False:` | fence-unclosed | expect=2 got=0 FAIL; suite pass=6 fail=1 exit 1 | killed |
| nonreceipt | audit line 163 replace classification with `continue` | fence-live-nonreceipt | expect=1 got=0 FAIL; live_citations=2 but bound=1; suite pass=6 fail=1 exit 1 | killed |
| tools | audit line 155 append `"tools/"` to record specs | shift-tools | expect=1 got=0 FAIL; bound=1 shifted=0; suite pass=6 fail=1 exit 1 | killed |

C2 exact commands substitute `pristine`, `value`, or `zeros` for `<id>`:

```sh
python3 /fast/scratch/hyaku/kama-r76/MT01Mutants/c2-<id>.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --selftest --work /fast/scratch/hyaku/kama-r76/MT01Mutants/fx2-<id>
```

Pristine exit 0 `SELFRECORD_FACTS_SELFTEST pass=5 fail=0`; both restored copies under identical invocation exit 0, all five arms green.

| id | tools/round76-selfrecord-facts.py source function / exact edit | Expected arm | Observed | Verdict |
|---|---|---|---|---|
| value | apply_correction line 211 `if value != expected:` → `if False:` | correction-wrong-value | that arm FAIL; others PASS; pass=4 fail=1 exit 1 | killed |
| zeros | audit lines 218–236 replace entire body with `print("SELFRECORD_FACTS claims=8 mismatches=0 unbacked=0 corrected=5"); return 0` | cheat / stale-data detector | red-at-base, correction-wrong-value, correction-value-bound FAIL; worktip-graph and cheat-zeros PASS; pass=2 fail=3 exit 1 | killed by other arms, NOT cheat-zeros |

**Named-arm finding:** C2's `cheat-zeros` remains PASS under the production constant-output mutation. It checks rejection of a separate hardcoded cheat program and does not itself assert the production program's behavior. The suite does kill this mutant through red-at-base and correction arms, so this is named-arm attribution divergence, not a suite survivor.

Final aggregate: six scored kills (C1 four, C2 two), zero proven survivors; C3 five inconclusive because its baseline green fixture fails; three base probes are diagnostic effects, not kills. C3 rotation/audit apparent escapes remain coverage findings with the explicit baseline caveat above. Restored source hashes for C1/C2 equal the captured hashes; all commands, hashes, stdout/stderr and exits retained. No further runtime invoked.
