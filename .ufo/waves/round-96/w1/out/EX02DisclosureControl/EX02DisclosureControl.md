# EX02DisclosureControl — Round-96 C3 (calibration) base-counter check

Seat: `EX02DisclosureControl` (L1 KamaR96, lane repo kama-shokunin). Read `plans/round-96-claims.md` (frozen, base `5d43528badc31ad6c0ca1848c00561f531924e4d`) first; ran the frozen C3 counter at that base to confirm the instrument discriminates.

## Base run (verbatim receipt)

```
$ python3 tools/round96-disclosure-audit.py --repo . --rev 5d43528badc31ad6c0ca1848c00561f531924e4d
DISCLOSURE_AUDIT checks=5 mismatches=2 met=False
EXIT=1
```

Receipt saved at `c3-base-run.out` beside this report.

## Confirmation: mismatches > 0 at base

The instrument **discriminates**: it is red at base (`mismatches=2`, exit 1) and — per the frozen predicate — goes green only at M3 after C1+C3 land. Per-check trace at base:

1. **FAIL (1):** probe at base has `MAX_STEPS = 4_000_000` (line 575 of `tools/kama-probe.sh`) and no `6 steps per tensor header` sentence → ceiling sentence still names the 4M/old geometry.
2. **PASS:** neither `MAX_TENSORS = 1_000_000` literal nor `the ceiling is 1,000,000` exact string is present together at base (the base comment already carries a ceiling clause, but the counter grades the frozen pair).
3. **FAIL (1):** `tools/round96-router-budget.py` does not exist at base revision → `20 + 25 * npaths` not in counter → mismatch.
4. **PASS (note):** SCORECARD `router-byte-decided` cites `f6325660`; that commit **does** resolve and **is** an ancestor of base tip `5d43528b`. At base the stale-pointer defect is not yet fatal to this check — it becomes fatal only when M1b `c810f51e` lands as the filing revision; per `plans/round-96-claims.md` the pointer must point at or before the tip at M3.
5. **PASS:** probe at base already carries wrapper literal `20 + 25 * npaths` (line 862).

2 mismatches are enough to satisfy the do-nothing control semantics: exit 1 at base, expected `mismatches=0 met=True` exit 0 at M3.

## Verdict

Instrument can discriminate (kill rule K3 not triggered). No lane files were modified by this seat; findings only in this out dir. Scratch `/fast/scratch/hyaku/kama-r96/EX02DisclosureControl/` removed on exit.

Files changed: none in lane repo. Out: `EX02DisclosureControl.md`, `c3-base-run.out`.

Suggested main-agent check: run `python3 tools/round96-disclosure-audit.py --repo . --rev <M3>` post-integration; expect `mismatches=0`.
