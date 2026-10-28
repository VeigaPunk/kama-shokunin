# R03ClaimBoundary — Round 62 claim separability

Axes reviewed: operability and calibration. Scope: whether C1/C2 are causally separable, whether their measurements overlap, and whether both independently land against the frozen baseline. Read-only review; no verdict on claim admission.

## Dependency graph

```text
C1: tools/kama-completion-live.py + C1 counter
      └─ live-completion-request-plane capability (outside frozen 12)

C2: newest canonical 12 rows + capability-claims-r62.tsv
      └─ execute each frozen capability's own bound template + 8 controls
         (no edge to C1 receipt/tool/capability)
```

There is no required C1→C2 edge or C2→C1 edge in the frozen predicates. C1 can be met without C2: its counter requires the completion tool, pinned llama.cpp child/receipt, independent outside live nonce-bound observation and 16 controls; it does not consult the SCORECARD canonical list, calibration registry, or C2 counter. C2 can be met without C1: its population is expressly the 12 pre-round-62 capabilities; it requires those rows and their own allowed runs, not the new completion capability or its receipt. Freeze states the completion row is “outside this frozen calibration population and is independently measured by C1” (`.ufo/waves/round-62/controls/freeze.txt:43-45`); the C2 counter repeats that boundary (`tools/round62-c2-counter.py:17-18`).

## Axis distinction and acquisition accounting

AXES.md defines operability as runnable artifacts/checklists producing stated outcomes (lines 13) and calibration as self-assessment matching observed repo state (line 15). It also defines capability acquisition as distinct from axis quality (lines 57-64). C1's claimed improvement is a real request-plane instrument and live answer (freeze lines 11-27); C2's is checking correspondence of self-assessment to executed evidence for the frozen repertoire (lines 29-54). Thus the claims target distinct axes and their predicates are independently falsifiable, consistent with the causally-separable rule at AXES.md lines 25-35.

C2 does **not** double-count C1's acquisition: the frozen population is fixed at 12, and the separate `live-completion-request-plane` is excluded. The canonical Round-62 list shows the 12 rows, ending in `live-ollama-lifecycle` (`SCORECARD.md:3272-3293`); the C2 registry has those 12 entries (`registry/capability-claims-r62.tsv:2-13`). C1's capability acquisition is explicitly named only in the C1 scorecard claim (`SCORECARD.md:3269`), not among those rows. C2 does execute one live llama.cpp lifecycle among its own frozen population, but it is the pre-existing `live-llamacpp-lifecycle` capability, not C1's new POST /v1/completions request-plane capability (`registry/capability-claims-r62.tsv:4`; freeze lines 34-44).

## Findings

No actionable claim-boundary defect found in the frozen design: the axes are distinct, the counter populations/required artifacts do not depend on each other, and C2's calibration count excludes C1's newly acquired capability. The fixes listed for C2 include SCORECARD/registry/ledger and a replay scratch-root repair (freeze lines 49-54); those are dependencies of C2's own 12 bound checks, not prerequisites for C1's live request-plane predicate.

## Residual risk / verification gap

This is a static predicate/dependency review, not a counter execution or claim verdict. C1 and C2 may share environmental prerequisites (the pinned model and host capacity), so their runtime success is not statistically independent; that does not create logical predicate dependency or count the C1 capability in C2. No tools installed or updated.
