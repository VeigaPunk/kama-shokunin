# AttackConstant — bounded static review

## Axes

- Fail-closed duplicate rejection before any classifier child starts.
- Operability: valid unique-name corpora still execute and measure every fixture.
- Policy identity: compare stripped case names only, preserving case sensitivity; identical capture payloads are allowed.
- Evidence integrity: actual runner CLI, actual classifier, independent child marker, and no runtime/readiness claim.

## Counterexample and finding

A runner that always reports `duplicate case names`, exits 1, returns every record unmeasured, and starts zero classifier children would satisfy every duplicate-only negative row. More negative rows cannot distinguish that mutation from the intended repair.

The planned positive controls distinguish it. A concrete falsifiable positive row is:

```json
{
  "name": "AttackConstant_positive16_example",
  "names": ["n00", "n01", "n02", "n03", "n04", "n05", "n06", "n07", "n08", "n09", "n10", "n11", "n12", "n13", "n14", "n15"],
  "envelope": "array",
  "expected_rejected": false
}
```

Clone the first original fixture for each name, changing only its `name`, as required by the assignment. This has exactly 16 distinct stripped names despite having identical capture payloads. Its expected observations, not executed results, are:

| Behavior | Runner exit | Passed | Failed | Classifier marker lines |
| --- | ---: | ---: | ---: | ---: |
| Intended valid measurement | 0 | 16 | 0 | 16 |
| Constant pre-child rejection | 1 | 0 | 16 | 0 |

The paired negative is the same corpus with `n00` appended: 17 fixtures, 16 distinct stripped names, expected exit 1, passed 0, failed 17, and zero classifier marker lines. The old minimum-only guard cannot distinguish the pair; the intended duplicate guard can. These expectations are static counterexamples, not a claim that either run occurred.

## Local evidence

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py:350-362` collects nonempty stripped names and rejects only when their distinct count is below 16. It does not reject an additional duplicate once 16 distinct names exist.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py:375-395` in the inspected snapshot sends any corpus problem to unmeasured records without reaching `measure_case`; successful measurement instead traverses every fixture. This is precisely the route a reject-all mutation would abuse.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-evidence/cases.json:2-17` supplies the literal seed: equal selected tags/ps digests, `expected_exit: 0`, and `expected_finding: loaded_same_digest`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py:261-275` contains the positive metadata-correspondence finding and its schema/verdict/readiness/scope payload. This is offline correspondence, not serving readiness.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/build/spec.json`, `items[name=GuardHarness]`, describes accepted rows requiring exit 0, passed equal to total, failed 0, and marker count equal to total, using the real classifier wrapper. This is proposal evidence, not an independent instruction source or proof of implementation.
- The same specification's `items[name=ValidBoundaries]` describes 16-unique, 32-unique, object-envelope 16-unique, and case-sensitive `N00` positive controls. `items[name=AppendDuplicate]` also describes a duplicate-removed positive counterpart.

## Smallest safe correction / recommendation

Preserve the planned positive controls and execute the full committed matrix for final acceptance. With those controls present and the specified accepted-row checks implemented, a constant reject-all runner cannot satisfy the matrix. This attack does not establish a defect in that proposed design.

Close the remaining omission risk: a nonempty matrix is not necessarily a two-sided matrix. Require at least one literal `expected_rejected: false` control in the full matrix used for acceptance, as well as the required duplicate negatives. Do not treat a negative-only `--only` run as complete evidence. The row above, paired with its appended-duplicate negative, is sufficient to distinguish this mutation; the other planned positives additionally protect envelope, cardinality, and case-sensitive identity behavior.

For positive assertions, bind the expected total and child count to `len(names)` from the literal fixture, not merely to a runner-reported `total`. For the example, require total 16, 16 records, passed 16, failed 0, exit 0, and marker count 16. Otherwise self-consistent zero/truncated runner counters could make an alleged positive control vacuous. Keep actual classifier execution; do not replace it with a success-shaped fake response.

A reject-all implementation is a fixable operability defect, not an acceptable safety-versus-availability tradeoff. Whether evidence is admitted remains solely with the canonical Rust judge. No score, runtime-restoration, or receipt change is recommended.

## Scope and limitations

Static advisory review only. At the initial file discovery, the proposed `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-corpus-guard/` fixtures and harness were not yet present; their implementation and final contents are not asserted here. The frozen source and available runner snapshot were read, not executed. No probes, tests, builds, linters, formatters, smoke runs, runtime invocation, host mutation, or installs were performed. Only this assigned report was written; no source, fixture, historical receipt, or lesson was changed.

Report: .ufo/waves/round-15/build/advice/AttackConstant.md
