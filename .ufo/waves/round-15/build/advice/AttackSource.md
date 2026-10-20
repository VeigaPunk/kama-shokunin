# AttackSource — bounded source/guard attribution attack

## Axes and finding

Impacted axes: **calibration** (claim strength versus actual evidence), **quality/provenance** (vendor facts versus kama policy), and **discernment** (a sourced readiness rejection is not an independent review of executable guard correctness). Operability/runtime readiness remains outside the claimed repair; no numeric change is supported by this review.

The inspected wording does **not currently attribute duplicate-corpus semantics to S012**. The potentially misleading shortcut would be to treat “reopened S012; rejected readiness overclaim” as evidence that the duplicate guard works, or as a new vendor-defined guard rule. The strongest local counterexample demonstrates that these propositions are independent. This is a fixable attribution risk, not a reason to weaken the requested fail-closed behavior. No canonical judgment, admission, or shipping decision is made here.

## Falsifiable counterexample — sourced boundary true, guard false

Use the literal names in `PrependDuplicate-array`: `n15`, followed by `n00` through `n15`. There are 17 declared names but 16 distinct stripped names. Build each case from the first original fixture, changing only the case name; its expected result is `loaded_same_digest`, exit 0. This uses the assigned fixture schema rather than malformed captures or a substitute classifier.

**[INFERENCE from static code; not executed]** Against the frozen pre-repair runner, this corpus does not enter the corpus-rejection branch: `unique == 16`, so `unique < 16` is false and `corpus_problems()` returns no problems. With an available, launchable classifier and successful file staging, the runner reaches the child-launch path for all 17 fixtures. Fixture names are not passed to the classifier, and temporary directories are indexed, so a repeated fixture name does not itself prevent child launches. The unchanged first-fixture inputs yield the metadata-only finding; every child can still report `readiness: "unknown"` and `scope: "offline-captures-not-runtime"`.

Thus the sourced readiness boundary can remain entirely respected while the pre-child duplicate guarantee is false. Even a matching readiness field on every child cannot establish that no child started. The classifier's separate rejection of duplicate selected **model entries inside one capture** cannot catch repeated **case names across the corpus**.

Falsifying the claimed repair requires an invalid corpus of this shape to reach any child, or to be rejected only by the minimum-cardinality check. S012 cannot distinguish that failure from a correct repair. A 16-name all-distinct control is needed to distinguish a real duplicate guard from unconditional corpus refusal.

## Evidence inspected

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py:350-383`: strips names, checks only the minimum unique count, then loops into measurement when no corpus problem exists. Lines 211-251 show indexed staging and the actual child invocation; lines 60-66 define the independent readiness/scope constants.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-corpus-guard/PrependDuplicate.json:2-24,75-95`: concrete 17-name duplicate control and matching 16-name valid control. Object-envelope controls are also present at lines 26-48 and 97-118.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-evidence/cases.json:2-17`: first fixture has one matching tags entry and one matching ps entry, equal digests, expected exit 0 and finding `loaded_same_digest`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py:218-276`: selected-model duplicate checks operate within captures; matching digests produce metadata correspondence, with readiness/scope supplied separately. Lines 85-86 set those constants.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/ollama-evidence-replay.md:30-46`: vendor pages document response fields, not the lane's matching/precedence/readiness policy.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-15.md:15-23`: separates guard evidence from the readiness rejection; explicitly states that S012 does not establish duplicate-corpus policy.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/build/advice/Sources.md:22-38`: the source author's own report expressly excludes guard-mechanics, fixture-count and runner-correctness endorsements. This report is author-side advice, not an independent gate disposition.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:24`: S012's used-by cell includes the round-15 lesson; this link alone does not endorse every claim in that lesson.

Public source opened read-only during this review on 2026-10-20: [Ollama GET /api/ps](https://docs.ollama.com/api/ps), OpenAPI 3.1.0 / info.version 0.1.0, `responses.'200'.description`: “Models currently loaded into memory” (5 words). The response schema concerns running-model metadata; it specifies no fixture-name uniqueness, corpus minimum, Python preflight, or child-process ordering contract. This source does not itself say that loaded models cannot serve; the bounded conclusion is that the documented response and offline captures do not establish present inference readiness.

## Smallest safe correction / retention recommendation

Retain the lesson's explicit separation. If tightening the ambiguous phrase “retains the sourced domain constraint of C1,” replace only that attribution with:

> S012 is used only for the readiness-boundary rejection. Duplicate-case rejection and pre-child ordering are kama measurement policy; their evidence is the runner change and discriminating frozen-before/final-after measurements, not the vendor page.

Keep three evidence columns distinct: (1) vendor loaded-memory semantics; (2) kama's stripped-name duplicate policy; (3) measured pre-child behavior. For the main agent's evidence collection, require the invalid matrix to fail against the frozen runner and to be rejected by the final runner with the duplicate-specific error and independently observed zero child starts; retain a valid unique control that actually measures children. A nonzero outer exit or `readiness: unknown` alone is insufficient. Do not count the source reopening as new guard knowledge, new readiness coverage, runtime restoration, or an outside correctness endorsement. No classifier semantics or extra normalization is needed for this correction.

## Limits

Static bounded review only. No probes, tests, builds, linters, formatters, smoke runs, verification commands, child processes, runtime invocations, installs, or host/service changes. The counterexample's predicted executions are explicitly inferences, not observed receipts. The immutable frozen runner supplies the before-state evidence; concurrent final runner/harness work and complete red/green receipts were not verified. Only this assigned report was written; no source, fixture, lesson, registry, or historical receipt was edited.

Report: .ufo/waves/round-15/build/advice/AttackSource.md
