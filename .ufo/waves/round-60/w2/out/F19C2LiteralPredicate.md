# F19C2LiteralPredicate — C2
- Axes: calibration (C2); operability. Target: W1 K01 literal-predicate registry vs frozen C2.
- Evidence: W1 registry attaches version, empty `ps-before`, tags-empty, v1-model-single and `generate.done` predicates to unrelated inference/digest-join lines; nine other rows are generic not-observable.
- Exact counter output: `population=14 rows=14 covered=14/14 evaluated=5 eval_lines=5 sensitive=5/5 bound=5 contradicted=0 amended=0/0 receipt_ok=1 controls_rejected=35/35 errors=0 met=True` (exit 0).
- This demonstrates all three requested literals accepted despite no line-to-predicate semantic binding; controls do not catch irrelevance.
- Smallest safe correction: frozen line→capture-field binding enforced for each predicate; constrain not-observable reasons to evidenced causes.
- Details: `.ufo/waves/round-60/w2/out/F19C2LiteralPredicate/findings.md`.