# M13C2AttackQuote — C2 quote-family probe

Tip checked: `master` = `65d7cad0fce90e34de37527cde22e97b63b118bf`.

I imported `tools/round62-c2-counter.py`, parsed the committed `registry/capability-claims-r62.tsv` (12 rows, no parser errors), and applied its `score()` to the baseline and mutations using a deterministic scorer returning each row's recorded `observed` value as the observed output, with `verdict=True`, `sensitive=True`, `dead=False`. This exercises quote eligibility and the counter's scoring facts without the live execution layer.

| Variant for `sources-registry` quote | Scoring output (population, rows, covered, bound, eval_lines, sensitive, dead, mismatches, errors, err_list) | Result |
|---|---|---|
| Baseline `Curate where` | 12, 12, 12, 12, 12, 12, 0, 0, 0, [] | ACCEPTED |
| Case-changed `curate where` | 12, 12, 11, 11, 11, 11, 0, 0, 0, [`quote:sources-registry`] | REJECTED |
| Other capability's substring `Reconcile ca` (from the `ollama-offline-evidence-replay` prefix) | 12, 12, 11, 11, 11, 11, 0, 0, 0, [`quote:sources-registry`] | REJECTED |

Neither attack falsified the predicate. The quote check is case-sensitive substring membership in the prefix looked up by that row's own `cap`, so the cross-capability quote is rejected too. (`mismatches` counts run-result/observation discrepancies, not quote errors; rejected quote variants appear in `err_list` and reduce coverage/bound rows.)

No tools installed or updated.

Scratch cleanup: performed; scratch root removed. Counter invocation with `--no-live` did not complete within its 300-second timeout, so the reported numerical scoring outputs are from direct `score()` calls; no full counter verdict is claimed.

Report: `.ufo/waves/round-62/w1/M13C2AttackQuote.md`
