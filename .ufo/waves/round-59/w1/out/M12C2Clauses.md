# M12C2Clauses — Round 59

Axes: operability; calibration (assigned 7, lowest). Advisory-only counter falsification.

## Procedure and baseline

Ran the frozen C2 detector, without changing target, controls, or fixtures:

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c2-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 --fleet-ref HEAD
```

Output (exit 0): `tip=2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 fleet=0f99f606120d0c884656c6e7a290f0e8f33c2181 maxN=57 manifest=rejected-honest-stop`; `rows=44 mismatches=0 met=True`; all eight mismatch values were zero. This baseline is interpretable.

Copied the counter into `/fast/scratch/hyaku/kama-r59/M12C2Clauses/counter.py` (initial SHA-256 `1aa0cf055734c89f8b51d3cdc64ce5d1f50afaefd5dde070dfe37c541617e1b5`). For each probe separately, changed only one `mismatches` dictionary clause value to constant `0`, then ran the same detector arguments against the frozen lane tip and fleet `HEAD`. All eight probes independently returned exit 0, reported `mismatches=0 met=True`, and reported every clause value zero:

| Mutated clause (forced to 0) | Detector output / exit | Verdict |
|---|---|---|
| `row_missing` | `mismatches=0 met=True`; exit 0 | Survived (not killed) |
| `typed_count` | `mismatches=0 met=True`; exit 0 | Survived (not killed) |
| `pinned_fleet_revision` | `mismatches=0 met=True`; exit 0 | Survived (not killed) |
| `pointer_missing` | `mismatches=0 met=True`; exit 0 | Survived (not killed) |
| `pointer_round` | `mismatches=0 met=True`; exit 0 | Survived (not killed) |
| `pointer_verdict` | `mismatches=0 met=True`; exit 0 | Survived (not killed) |
| `including_round` | `mismatches=0 met=True`; exit 0 | Survived (not killed) |
| `count_command` | `mismatches=0 met=True`; exit 0 | Survived (not killed) |

Thus the frozen counter detects none of these individual mismatch-clause deletions on the pristine passing case. This is a coverage finding about these one-clause probes, not a changed claim or permission to alter the frozen detector.

## Restoration

The scratch counter was restored byte-for-byte in `finally`; restored SHA-256 is `1aa0cf055734c89f8b51d3cdc64ce5d1f50afaefd5dde070dfe37c541617e1b5`, matching initial. Scratch directory was removed by shell trap before completion. No lane source, fixtures, fleet files, or commits were modified. No tools installed.
