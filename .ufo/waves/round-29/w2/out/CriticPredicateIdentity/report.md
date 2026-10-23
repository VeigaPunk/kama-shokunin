# CriticPredicateIdentity — round 29 attempt 2

## Scope, axes, and advisory answer

**Impacted axis: calibration** (truthful self-assessment and provenance); operability is implicated only in whether a reviewer can identify the measured predicate. This is a scoped adversarial review, not a canonical judgment, admission, integration, or axis-fit verdict.

**The operative target is unambiguous and frozen as a preregistration-plus-counter bundle. The sentence-identity defect is representational/non-fatal to that measured target, but the literal conformance rule remains unsatisfied.** Calling it merely a punctuation mistake, claiming that the receipt independently contains the full contract, or declaring the mandatory rule waived would be unjustified. If the canonical judge requires literal three-way sentence identity as an admission condition, the frozen artifacts fail that condition; a passing measurement cannot override it. This seat does not make that admission decision.

## Counterexample: the promised third sentence does not exist

Paths below are absolute:

- Preregistration: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/preregistration.json:14-20`.
- Counter: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py:4-43`.
- Fresh pinned receipt, produced by peer `kama-r29-w2-RerunCounter` and inspected directly by this seat: `/tmp/kama-w2-rerun-RerunCounter/receipt.json:1-125`.

The counter's lines 4-5 claim “the same sentence as preregistration.json C1.predicate and the label `unresolved` in the receipt”. In fact:

1. Preregistration line 14 contains two sentences and explicitly incorporates the frozen extractor and counter docstring's six class rules.
2. Counter lines 7-40 expand those definitions into multiple sentences and a six-class specification; lines 42-43 separately state the target.
3. The fresh receipt contains neither a predicate sentence nor `predicate` or `kill_rule` fields. A direct structured read returned `has_predicate: false` and `has_kill_rule: false`. Its complete keys were:

```text
append_only, base, by_class, correction_rows, counter, counter_sha256,
false_corrections, met, mismatched_at_base, mismatches, statements,
target, tip, unresolved, unresolved_ids, valid_corrections
```

This directly falsifies literal three-way sentence identity without constructing a hypothetical input. The receipt label `unresolved` is an integer result, not an independently complete definition.

## Operative fields: what agrees, and where the authority lives

| Field | Observed evidence | Assessment |
|---|---|---|
| target | Preregistration line 19: `mismatched_at_base >= 1 and unresolved == 0 at the measured lane tip (receipt field met)`; counter lines 42-43 repeat the conjunction and lines 340-341 emit/evaluate it; fresh receipt `target` is `mismatched_at_base >= 1 and unresolved == 0`, with the full measured `tip`. | Same Boolean condition; measured-tip prose is supplied by the receipt's revision field, not a changed threshold. |
| counter sha256 | Preregistration line 17 and fresh receipt line 14 both contain `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`; independent Git-object hashing below agrees at freeze, controls, and data. | Fixed executable identity, including its incorporated class rules and extractor. |
| kill_rule | Preregistration line 20: `A miss under this predicate is reported as a miss. The predicate, counter, extractor and target are never amended, re-scaled or narrowed after this freeze; a counter defect found later is disclosed as a limit, never repaired for this claim.` | Explicit and frozen in preregistration, **absent from the receipt**. A receipt-only review is insufficient; the preregistration must remain part of the evidence bundle. |

Fresh pinned receipt fields inspected directly:

```json
{
  "base": "2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d",
  "tip": "513eba3ba51a142c9936553e3a85918345eb5c4c",
  "counter_sha256": "fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383",
  "target": "mismatched_at_base >= 1 and unresolved == 0",
  "statements": 69,
  "mismatched_at_base": 11,
  "append_only": true,
  "valid_corrections": 11,
  "false_corrections": [],
  "unresolved": 0,
  "met": true
}
```

The pinned fresh receipt's SHA-256, independently computed by this seat, is `f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504`. The retained lane receipt `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/final/c1-513eba3b-cleanenv.json:12-17,119-124` records the same relevant fields. The baseline `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/before/c1-base.json` records the same digest/target with `mismatched_at_base: 11`, `unresolved: 11`, and `met: false`.

A second fresh receipt, `/tmp/kama-w2-rerun-RerunCounter-origin/receipt.json`, names remote tip `49f849f292c338f5e4e2cc8a60eb1372a8f40412`, with the same counter digest/target and `unresolved: 0`, `met: true`. **Do not label that remote-tip receipt as a measurement of 513eba3b.** The pinned receipt above is the evidence used for the inherited data commit. This is a provenance distinction, not evidence of a target change.

## Independent frozen-byte evidence

Read-only commands were run by this seat in the lane repository. For each revision below, the command was:

```text
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show <revision>:.ufo/waves/round-29/count-c1.py | sha256sum
```

| Revision | Observed SHA-256 output |
|---|---|
| freeze `827d136546b85059a984b34970f5b493d9a71290` | `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383  -` |
| controls `35b90184f638ab6a4149092b93143c7a2b873787` | `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383  -` |
| data `513eba3ba51a142c9936553e3a85918345eb5c4c` | `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383  -` |

`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse <revision>:.ufo/waves/round-29/preregistration.json` returned the same Git blob id for all three revisions:

```text
5e4b49a7ba5c99577f55514e474efd3d7a5d0037
5e4b49a7ba5c99577f55514e474efd3d7a5d0037
5e4b49a7ba5c99577f55514e474efd3d7a5d0037
```

`git -C /home/vgpnk/Projects/shokunin/kama-shokunin hash-object .ufo/waves/round-29/preregistration.json` returned `5e4b49a7ba5c99577f55514e474efd3d7a5d0037` for the actual preregistration read in this review. `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py` returned the frozen counter digest above. Thus target, counter digest, and kill rule were not changed between those named checkpoints or in the reviewed working copies. This establishes those checkpoints, not a claim to have audited every intervening commit.

## Strongest semantic objection beyond punctuation

The prose is not a perfectly interchangeable executable specification. Counter docstring lines 27-30 exclude Q spans starting with `sh`; implementation line 66 excludes `"sh "` (trailing space), and lines 219-223 use `startswith(Q_CMD)`.

**[INFERENCE, static counterexample; not executed]** A backticked `shell=1` span meets the implementation's length/digit/equals tests and does not start with `"sh "`, so it is eligible for extraction; a literal application of the docstring's `sh` exclusion rejects it. This is a real prose/code precision difference, not an alternative threshold. The preregistration's incorporation of the **frozen extractor** identifies which implementation actually ran, but does not make the prose literally exact.

A direct structured read of `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/kama-r29-w2-VerifyRefPaste/receipt.json` selected `.all_statements[]` with `class == "Q"` and token prefix `sh`; it returned `sh_prefix_tokens: []` (25 Q statements total). Therefore this specific prefix counterexample does not identify a changed result in the frozen 69-statement population. It must not be generalized to “all prose and code are semantically identical”, or to universal recognizer correctness.

## Smallest safe correction

1. In new explanatory/report text only, state: **“The preregistration incorporates the digest-frozen extractor and class rules; the receipt records an evaluation of its target, not a third copy of its predicate sentence.”** Cite preregistration line 20 for the kill rule, and name the full measured tip.
2. Explicitly retain the literal same-sentence conformance defect and the prose/code precision limit. The existing disclosure at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-29.md:49-53,119` is disclosure, not proof that the canonical judge waived a rule.
3. Do **not** edit the frozen predicate, counter/docstring, target, extractor, existing receipts, or correction rows to make them appear conformant. No after-data rewording can truthfully establish that the required sentence existed in all three frozen artifacts. If literal identity is a required admission gate, report that failure; a conformant replacement needs a separately preregistered future claim, not a retrospective repair of this one.

No tradeoff is shown in the frozen target itself. The unacceptable trade would be purchasing a passing/conformant narrative by silently replacing the original contract or misattributing a later remote-tip receipt.

## Execution and delivery bounds

This seat inspected existing fresh receipts and ran only read-only Git/hash commands. It did not run the Python counter, tests, a model server, a judging runtime, or another agent; no lane/index/jj/source changes and no tools installed or updated.

This full report is written only to the seat-owned directory, as required by the hard write bound. The requested trailer projection `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/CriticPredicateIdentity.md` lies outside that directory and was not written by this leaf; the integrator can place the report there under its own authority.
