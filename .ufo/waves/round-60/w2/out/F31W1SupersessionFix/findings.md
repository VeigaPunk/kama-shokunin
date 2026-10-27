# F31W1SupersessionFix — W2 falsification

Axes: calibration (directly), operability (only if adopted as a reliable check).

Frozen claim: S513's flip fired and its rejected row is unmarked; intended fix is a pointer to S518 (freeze.txt lines 45–47). W1 E01's check instead defines unresolved as any supersedes pair where rejected target lacks a qualifying lesson pointer and/or the superseder itself is rejected. On base it reports `pairs=33 unresolved=3 ids=S095,S505,S513 met=False`; its S513-only probe remains `unresolved=2 ids=S095,S505 met=False` (E01 report, lines 6–9).

SC01's independent flip-fire scan reports exactly one true contradiction: S518→S513. S509→S505 is not a fired flip: S509 is itself rejected and says “as S505”; S096→S095 is a narrowing positive fact, while S105→S095 rejects cross-API inference. Both S096 and S105 share target S095, but their distinction is explicit in SC01 pairs.tsv lines 18,21,31,34 and findings.md lines 15–17.

Finding: E01's broad rejection-based predicate does not isolate the intended defect; it falsely flags S096/S105 distinction and S509 as unresolved, and cannot be made green by the frozen S513 pointer alone. It therefore fails calibration against the frozen claim, even though it catches S513. Do not change claim verdicts/predicates here.

Exact evidence: E01SupersessionCheck.md outputs above; SC01 pairs.tsv and findings.md. No lane files changed; no tests/tools run in W2.