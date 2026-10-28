## M10C2AttackRename — C2 rename-family mutation

Measured at master `65d7cad0fce90e34de37527cde22e97b63b118bf`; used counter and registry bytes from that tip. The frozen MANIFEST contains exact keys, and `score()` checks `cap not in manifest` before looking up the frozen prefix/template. I used the same callable scoring interface with deterministic successful/sensitive synthetic scorer output (no live runs); this isolates slug matching and must not be interpreted as full C2 measurement.

| Variant | Result | Scoring facts |
|---|---|---|
| Unmutated registry baseline | ACCEPTED | population=12 rows=12 covered=12 bound=12 eval_lines=12 sensitive=12 dead=0 mismatches=0 errors=0 |
| Rename `sources-registry` → `sources` (substring of manifest slug) | REJECTED | population=12 rows=12 covered=11 bound=11 eval_lines=11 sensitive=11 dead=0 mismatches=0 errors=0; `err_list=[unbound-cap:sources]` |
| Rename `sources-registry` → `sources-registry-extra` (manifest slug as prefix) | REJECTED | population=12 rows=12 covered=11 bound=11 eval_lines=11 sensitive=11 dead=0 mismatches=0 errors=0; `err_list=[unbound-cap:sources-registry-extra]` |

Verdict: exact membership matching is used; both unknown prefix/substring renames fail to cover the frozen population and are rejected by the met predicate. No falsification found. No software installed.

Restoration: mutations existed only in in-memory strings; lane source and registry bytes were not modified. Scratch path `/fast/scratch/hyaku/kama-r62/w/M10C2AttackRename` removed before return.

ACCEPTED=1/3 REJECTED=2/3 (including baseline)
