# ProvenanceLedger — round-16 build advice

**File written:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/dispatch-provenance.py` (stdlib only, `#!/usr/bin/env python3`, executable).
**Routes:** routed defect 4, `corpus/lessons/round-15-verifier-spotcheck.md:168` — "Preserve environment bindings and refused-attempt payload identity/timing with wave evidence."

## Behavior

Two modes, mutually exclusive, one shared ledger file (`{schema: "dispatch-provenance-ledger-v1", entries: [...]}`, atomic tempfile+`os.replace` write; an existing ledger that is unparseable or wrong-schema is refused at exit 70, never clobbered).

1. `dispatch-provenance.py --spec PATH --out LEDGER [--timeout S]`
   - Runs `node /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs run --spec <abspath>` (script existence confirmed; stdout is the `ufo-swarm-wave-dispatch-v1` payload whose `taskCall` field is `{context, tasks}` or `null`, per `ufo-swarm-wave.mjs:1292-1316`).
   - Environment: `os.environ` copy + exactly `UFO_CONFIG_PATH=/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json` (file exists), `UFO_FLEET_ALLOW_EXTERNAL_TOOLS=1`, `UFO_PROJECT_ROOT=/home/vgpnk/Projects/shokunin/kama-shokunin`.
   - Entry records: `kind: "wave_run"`, `argv`, `cwd`, `env_bindings` (only those three names/values — no other env is captured anywhere), `spec`/`spec_sha256`, `started`/`ended` UTC (ISO-8601 Z, microseconds), `exit`, `spawn_error`, `stdout_sha256`/`stdout_bytes`, `stderr_sha256`/`stderr_bytes`, `stdout_parseable`, `taskCall_sha256` (sha256 of `json.dumps(taskCall, sort_keys=True, separators=(',',':'), ensure_ascii=False)`; hashes `"null"` when stdout is unparseable or `taskCall` is null — distinguish via `stdout_parseable`), `counts` (`{dispatch: payload.counts verbatim|null, tasks: len(taskCall.tasks)|null, resume_sends: len(payload.resumeSends)|null}`).
   - Process exit = the child's exit code (wrapper faults: 64 usage, 70 spawn/ledger-refusal, 74 I/O).

2. `dispatch-provenance.py --attempt-result PATH --label refused|spawned --out LEDGER`
   - Entry records: `kind: "attempt"`, `label`, `at` UTC, `attempt_result` abspath, `result_sha256`, `result_bytes`, `parseable`, `refused`/`spawned` counts (null when unparseable), `bound_task_call_sha256` + `bound_run_index` copied from the most recent `wave_run` entry — tying a refused task call to the same taskCall digest. Exits 0.

## Design choices

- **Binding by digest, not by payload copy:** the attempt entry stores `bound_task_call_sha256` (plus run index for human navigation), so a refusal is provably tied to the exact taskCall JSON `run` emitted without duplicating 100+ KB of payload per receipt.
- **Conservative count extraction:** refused/spawned counts come only from (a) dict keys literally named `refused`/`spawned` with int values, and (b) `status`/`state` string fields equal to `refused`/`spawned` (matches the real `build/spawn-result.json` progress-row shape, `status: "pending"|...`). Unparseable results still record `result_sha256` + `parseable: false`.
- **Environment minimality:** only the three mandated names are written into `env_bindings`; nothing else from `os.environ` is read into the ledger (no credential/session leakage into wave evidence).

## Verification performed (own file only)

- `python3 -m py_compile` — clean.
- `--help` — renders both modes.

Not run against any spec — per assignment, L1 runs every measurement including the real `run` receipt and the refused/spawned attempt append.

## Limitations

- `taskCall_sha256` digests `null` for both "resume-only wave" (legitimate `taskCall: null`) and "stdout was an error payload"; `stdout_parseable` and `exit` disambiguate — consumers must check both fields.
- `bound_task_call_sha256` binds to the *latest* `wave_run` in the ledger; interleaving two specs into one ledger would mis-bind later attempts (L1 controls this: one ledger per wave).
- Count extraction is heuristic by contract ("if parseable"); a refusal shape that reports zero via absence of fields yields `refused: 0`, not a flag — `parseable` is the only coverage signal.
- `node` is resolved via inherited `PATH` (fnm shim on this host); the ledger records `argv[0]` as `node`, not a resolved absolute path — the interpreter identity is implicitly the host's `PATH` at run time.

## Installs

None. Host `node` and `python3` pre-exist; stdlib only.
