# M09C2AttackDrop — C2 drop-family probe

Axis: calibration. Frozen source tip: `65d7cad0fce90e34de37527cde22e97b63b118bf` (master at probe time). `tools/round62-c2-counter.py` and `registry/capability-claims-r62.tsv` were read from that tip. The counter's acceptance condition requires `facts['covered'] == facts['population']` and `facts['bound'] >= facts['population']`, plus the remaining canonical/control predicates.

Reproduced `parse_registry()` and `score()` from the frozen counter in isolated scratch, with a deterministic scorer returning true, observed text from each row, sensitive=true, dead=false. Baseline scoring output: `population=12 rows=12 covered=12 bound=12 eval_lines=12 sensitive=12 dead=0 mismatches=0 errors=0 err_list=[]`.

- **Drop one bound row** (`ollama-offline-evidence-replay`): **REJECTED**. Scoring: `population=12 rows=11 covered=11 bound=11 eval_lines=11 sensitive=11 dead=0 mismatches=0 errors=0 err_list=[]`. Coverage is 11/12, so the acceptance equality fails.
- **Drop that row and duplicate another capability row** (`sources-registry`): **REJECTED**. Scoring: `population=12 rows=12 covered=11 bound=12 eval_lines=12 sensitive=12 dead=0 mismatches=0 errors=0 err_list=[]`. Duplicate increases rows/bound but set-based coverage remains 11/12; the acceptance equality fails. No coverage-gaming falsification observed.

`Report:` `.ufo/waves/round-62/w1/M09C2AttackDrop.md`
