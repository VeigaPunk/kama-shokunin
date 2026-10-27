# Q05Province — PROVINCE boundary (Round 56)

## Axes

- **Calibration:** Does the evidence support the frozen scope and outcome without overstating it?
- **Operability:** Does the check concern kamas local serving-process operation rather than another domain?

## Finding

**No province-boundary defect found.** The LD_AUDIT check belongs to kamas local serving-process operability: it observes a server childs environment variable *names* and rejects a code-injection loader variable. It does not change auth/credential flows, consumer configuration, endpoint routing, or model quality. The check is a process-integrity adjunct to local serving/health, not a new auth/config or quality claim.

## Evidence (observed)

- `PROVINCE.md:3-4` defines kama as “local model serving & endpoint health”; lines 42-45 refuse model quality/eval (kengaku) and credential material/auth flows (kagi), and line 47 onward prohibits kama from writing operator-owned config/systemd.
- `tools/round56-replay-code-audit.py:147` adds `LD_AUDIT` to `BAD_ENV`, alongside `LD_PRELOAD` and `DYLD_INSERT_LIBRARIES`. `environ_keys` (`:325-330`) reads `/proc/<pid>/environ` and extracts only bytes before `=`; it discards values. `env_leg` (`:430-441`) checks those names against `BAD_ENV`, appends a problem on a match, and returns sorted names. In the replay leg (`:705`), it is called only after confirming the announced server PID descends from the replay process (`:697-704`).
- The frozen preregistration (`.ufo/waves/round-56/preregistration.json:13-15`) specifies this exact local-child `LD_AUDIT` detection predicate and targeted C1 kill condition. It explicitly limits interpretation at line 49: the probe establishes presence of the variable and classifier response, not successful audit-DSO injection.
- Committed battery receipts: `measured/base-c1.out` says `ld_audit=missed`, `exit=0`; `measured/build-c1.out` says `ld_audit=detected`, with `problems=[...LD_AUDIT]`, `exit=0`; `measured/m-drop-ldaudit.out` says `ld_audit=missed`, `exit=0`. The positive and mutant receipts include the dynamic-loader warning that `/usr/lib/libexpat.so.1` lacks `la_version` and was ignored; this is consistent with the preregistered limitation, not evidence of successful injection. `measured/build-c2.out` records `present=1 roster_match=1 kills=1 controls=2 met=True` for calibration.

## Scope / limits

This supports only the environment-name classifiers local-process boundary. The exercised `round56-env-leg-test.py` creates a live `sleep` child with `LD_AUDIT` and invokes `env_leg`; it does **not** exercise an actual llama-server or establish endpoint health, authentication safety, model identity/quality, or successful code loading. No auth/config or model-quality surface was inspected or modified. No tooling installed.

Report path: `.ufo/waves/round-56/w1/out/Q05Province.md`.
