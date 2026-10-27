# F19C2LiteralPredicate — C2 literal-predicate falsification

Axes: calibration (C2; lowest assigned axis) and operability. Frozen claim/predicate unchanged. Attack target is the K01 W1 registry and C2 counter, not the lane claim verdict.

## Counterexample and evidence
W1 `out/K01C2DoNothingCritic/registry.tsv` puts five unrelated predicates on population lines 35, 44, 46, 60, and 141: respectively `c['version']['version'] == '0.40.11'`, `c['ps-before']['models'] == []`, `c['tags-empty']['models'] == []`, `c['v1-model-single']['object'] == 'model'`, and `c['generate']['done'] == True`. The quotes on those lines discuss policy/inference or digest joins, not those literal fields. The remaining nine rows are `not-observable` with generic reasons.

W1 ran the real counter CLI on a clone with that varied registry. Exact output: `population=14 rows=14 covered=14/14 evaluated=5 eval_lines=5 sensitive=5/5 bound=5 contradicted=0 amended=0/0 receipt_ok=1 controls_rejected=35/35 errors=0 met=True` (exit 0). Its repeated-version-predicate minimal variant also returned that same met=True line. Thus all three requested probes (version literal, empty ps-before, done=true) pass when attached to unrelated lines; varied registry shows them all accepted together. C2 score checks quote substring/length, predicate equals recorded verdict and mutation sensitivity, but no semantic relation between line and predicate. Controls do not address it.

## Smallest safe correction
A frozen line-key → relevant capture-field binding enforced by the counter; reject live predicates outside their line's binding. Also constrain generic not-observable rows to specific, supportable missing-capture causes. Preserve frozen population and claim; do not alter verdicts in this falsification.