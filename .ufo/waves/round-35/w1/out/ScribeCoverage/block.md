## Coverage map — round 35 addition

| Entry | Covers | Round |
|---|---|---|
| `knowledge/endpoint-health-probe-conventions.md` | what a health-probe signal means, as distinct from an engine route and from a remote platform deployment | 35 |

## Correction sentence — r34 coverage-map claim

The r34 report's coverage-map sentence is false at 719655f: committed fleet report `16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md` (blob `7610d532696f5c6e214840fa2ec4112584589252`) says the coverage map gains two entries (`corpus/knowledge/serving-alias-contract.md`, `corpus/knowledge/served-model-id-resolution.md`), but `git show 719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/README.md` contains `serving-alias-contract.md` 0 times and `served-model-id-resolution.md` 0 times (README blob `df71357b4605858a014f90c08ca2c5fedb8f1a45`, identical to its parent).
