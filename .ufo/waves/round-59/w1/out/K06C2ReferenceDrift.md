# K06C2ReferenceDrift — C2 fleet snapshot binding

## Counterexample / evidence
The counter resolves the `--fleet-ref` to a commit on every invocation, rather than pinning a prior fleet revision. In `evaluate` (`tools/round59-c2-counter.py:34-43`), it runs `git -C <fleet> rev-parse --verify <fleet_ref>^{commit}` and uses the resolved `frev` to read `MANIFEST.json`; `main` passes the current `--fleet-ref` through (`:80-85`) and prints that resolved commit (`:90`).

Used an isolated clone of fleet in `/fast/scratch/hyaku/kama-r59/K06C2ReferenceDrift/run2`, verified `git -C "$F" rev-parse --show-toplevel` equaled `$F`, and used `--fleet-ref HEAD` for both calls. Exact observed results:

- `python3 .../round59-c2-counter.py --repo .../kama-shokunin --tip 2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 --fleet-repo "$F" --fleet-ref HEAD` → exit 0; `fleet=0f99f606120d0c884656c6e7a290f0e8f33c2181 ... manifest=rejected-honest-stop ... mismatches=0 met=True`.
- Advanced only fixture HEAD using `git -C "$F" -c user.name=Fixture -c user.email=fixture@example.invalid commit --allow-empty -m 'fixture advance HEAD'` (new HEAD `d565e8e7f169134184da088fecc592457895c554`). Repeated identical counter command → exit 0; `fleet=d565e8e7f169134184da088fecc592457895c554 ... manifest=rejected-honest-stop ... mismatches=0 met=True`.

Fixture and scratch were removed by the command's exit trap. No tools installed.

## Axis impact and smallest safe correction
- **Operability:** positive narrow evidence: symbolic `HEAD` is resolved at call time, and output exposes the exact snapshot used. No reference drift or stale-revision defect demonstrated.
- **Calibration:** no demonstrated calibration defect from snapshot binding alone. This does not supply missing S517/S518 evidence or establish the frozen overall C2 predicate; the available closure remains `rejected-honest-stop` as stated in the task.
- **Correction:** none for invocation-time snapshot resolution. For reproducibility across separate calls, callers should record the emitted fleet commit and pass that exact revision when they require a stable comparison. Do not claim this check proves external spot-check availability or full C2 satisfaction.
