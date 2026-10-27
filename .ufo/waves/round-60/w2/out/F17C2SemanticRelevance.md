# F17C2SemanticRelevance — C2 semantic relevance
- Counterexample: W1 K01 registry predicates can be falsifiable and still unrelated to their quoted population statement.
- Exact varied registry: `w1/out/K01C2DoNothingCritic/registry.tsv` (D0–D13; exact rows detailed in findings.md).
- D0 quotes inference policy at ollama-evidence-replay.md:35 but asserts only `c['version']['version'] == '0.40.11'`.
- D1–D4 likewise test unrelated receipt fields; D5–D13 are generic not-observable rows.
- Exact met output: `population=14 rows=14 covered=14/14 evaluated=5 eval_lines=5 sensitive=5/5 bound=5 contradicted=0 amended=0/0 receipt_ok=1 controls_rejected=35/35 errors=0 met=True` (exit 0).
- Counter evidence: quote check is substring-only; falsifiable() checks mutation sensitivity, not semantic binding.
- Axes impacted: calibration; operability not directly disproved.
- Smallest safe future correction: frozen population-line → allowed capture-field binding; require predicate path intersection.
- No lane files, predicates, or claim verdicts changed; no tools installed.