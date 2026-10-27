# C02 — C1/C2 overlap scan

## Axes
- **Operability (C1):** live-child `LD_AUDIT` name detection by `env_leg` and its baseline/mutant battery.
- **Calibration (C2):** exact equality of the committed battery roster and preregistered roster, plus required designation counts.

## Evidence and causal relationship
The claims share a *description surface*, not the measured predicate. Preregistration lines 29–35 define three roster entries; the battery repeats those entries as literal `ROSTER` at lines 15–19. C2 (`round56-prereg-check.py`) reads only committed preregistration and battery blobs, AST-extracts that literal, compares equality, and counts designations. It does not load or execute the counter or battery, probe a process environment, or assess whether the listed outcomes are true. Its source explicitly says this at lines 2–4 and its comparison/count logic is lines 53–71.

C1 has the opposite dependency: the env-leg test imports the selected counter and probes a live `sleep` process at lines 17–29; `env_leg` checks the keys against `BAD_ENV` at counter lines 430–441. The battery runs the old counter, new counter, and a one-line `BAD_ENV` mutant at lines 40–50. Its outcome assertions use the `expected` argument at lines 22–31; they do not derive execution behavior from `ROSTER`.

This yields **causal separability, with a narrow artifact coupling**. C2 can remain green if the duplicated roster literals agree while C1's classifier is broken (or while the C1 driver stops consuming roster metadata). Conversely, C1 can pass its three outcome checks while a roster field/designation drifts, making C2 fail. Shared literal names and expected-outcome labels are coupled for bookkeeping, but neither claim's measured result establishes the other's predicate. In particular, C2's green result is not independent evidence that `LD_AUDIT` was detected; C1's battery is the behavioral evidence.

## Observed receipts (not rerun)
- Battery source invokes `python3 tools/round56-env-leg-test.py --counter <counter> --expect <expected>` (battery lines 22–24). Recorded `base-c1.out`: `ld_audit=missed ...`, `exit=0`; `build-c1.out`: `ld_audit=detected ... problems=['env: server environment carries LD_AUDIT']`, `exit=0`; `m-drop-ldaudit.out`: `ld_audit=missed ...`, `exit=0`. The loader also reports that `/usr/lib/libexpat.so.1` cannot be loaded as an audit interface (`undefined symbol: la_version`); preregistration limit correctly disclaims successful audit-DSO injection.
- Recorded C2 base receipt: `present=0 roster_match=0 kills=0 controls=0 met=False`, `exit=1`. Freeze receipt: `present=1 roster_match=1 kills=1 controls=2 met=True` (no exit line in that receipt; preregistration records target exit 0).
- Frozen counter/checker hashes and kill rules are recorded in preregistration; no counters, predicates, or shared files were changed for this scan.

## Bounded proposal and risks
**No change to this frozen round.** Preserve the split claims and describe C2 as roster-fidelity calibration, not behavioral validation. If a later round wants stronger coupling, add a separately preregistered check that the behavioral battery consumes the roster (or mechanically binds each roster entry to its invocation); do not retrofit this into frozen C2. Risk of leaving the current split as-is: a future battery edit may render the roster informational while C2 still passes. Risk of coupling them now: it changes the frozen C2 predicate/counter and contaminates the current calibration result.

## Verification
Read-only source and receipt inspection only; no checks were run. Evidence: `preregistration.json` C1/C2 definitions and limits; `round56-prereg-check.py` lines 2–4, 53–71; `round56-env-leg-battery.py` lines 15–50; `round56-env-leg-test.py` lines 17–29; `round56-replay-code-audit.py` lines 430–441; receipts named above.
