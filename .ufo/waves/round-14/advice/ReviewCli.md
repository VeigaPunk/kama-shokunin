# ReviewCli — round-14 CLI error mapping, stdout JSON, missing files, argparse

Owner: `Classifier` (`tools/kama-ollama-evidence.py`). Fixtures: `tests/ollama-evidence/cases.json` (static read only, 768 lines).

## Final static review (landed code)

Method: static reading of `tools/kama-ollama-evidence.py` (522 lines) and `tests/ollama-evidence/cases.json`. No tests, builds, selftests, or smoke runs were executed, per assignment.

**Verified in code (no defect observed):**
- argv: `Parser.error` raises `CliError` → one `invalid_input` JSON on stdout, exit 2 (`_run`, lines 474-480). `--help` goes through argparse `parser.exit()` → exit 0 plaintext; `main` re-raises `SystemExit`.
- Catch-all: `main` maps any `Exception` to `invalid_input` exit 2 (lines 511-518); uncaught-exception exit 1 cannot reach the verdict path.
- Missing/unavailable: `os.open` failure, non-regular (FIFO/dir/device, via `fstat` after `O_NONBLOCK`), oversized (`MAX_INPUT_BYTES`, bounded read loop), non-UTF-8, invalid JSON, duplicate keys (`_pairs`), NaN/Infinity (`_constant`), RecursionError → fixed `{label}_input_*` codes, no path or value interpolation.
- Missing ps input → `ps_input_*` → invalid_input; empty ps array accepted (`validate_capture`, `classify`).
- Types: `name`, `model`, `digest`, `remote_model`, `remote_host` must be `str` when present, else invalid_input (`validate_capture` 181-183). Empty-string remote markers treated as absent.
- Identity: exact, case-sensitive match on name or model; no normalization. Duplicate selected entries → invalid_input. Name/model conflict within selected entry → identity_conflict.
- `loaded_same_digest` requires exactly one tags and one ps match, equal nonempty digests, no remote marker.
- stdout: one JSON object, `ensure_ascii`, `allow_nan=False`; keys match the schema list; `readiness`/`scope` constants.
- Selftest: child processes via `[sys.executable, '-I', '-B', SCRIPT, ...]`, per-case TemporaryDirectory cwd, 30 s timeout, asserts exit, finding_id, child `verdict_exit`, schema, readiness, scope. Schema `kama-ollama-evidence-selftest/v1`; `clean` requires `>= MIN_CASES` (16) and zero failures; distinct names enforced. No module import of the script. Stdlib only; no network; writes only inside TemporaryDirectory.
- Committed cases (~50): literal expected_exit/expected_finding present; exit-to-finding map consistent with `FINDING_EXIT` for every case read.

**Findings (by severity):**

- **Medium — F1. Remote precedence vs digest presence diverges from contract literal (needs L1 ruling).** Contract: "remote tags or selected ps markers → remote_inventory regardless digest." Code checks digest presence before remote markers (`classify` 236-243 for tags, 238-239 for ps before 244-250). Committed fixture `remote_missing_digest` (cases.json 703-716) encodes the divergence: exit 2 `unknown`. The Fixtures task text ("remote takes precedence only after schema valid") supports the literal reading (schema, not digest). If the literal stands: move remote-marker checks ahead of digest-presence checks and flip the fixture to `remote_inventory` exit 1. The docstring (lines 33-38) documents the current choice explicitly, so this is a ruling, not a bug.

- **Low — F2. Unselected entries missing identity or digest pass silently.** Contract lists "missing identity/digest" under fail-closed. `validate_capture` checks types only when fields are present; an entry with neither `name` nor `model` is ignored by `_matching`, and an unselected entry with no digest is ignored. No committed case covers either. Real Ollama tags entries carry all fields, so strict validation is low-cost. L1 ruling needed.

- **Low — F3. `--cases` is unrequested surface.** It lets selftest run an arbitrary case file, so a green selftest need not refer to the committed `cases.json`. The default path is correct. Consider removing it (clean cutover) unless L1 approves.

- **Low — F4. Stdout failure in the catch-all.** If `emit` raises (e.g., BrokenPipe), `main`'s handler calls `emit` again and the exception escapes as a traceback (exit 1). Edge case only.

- **Nit — N1.** Docstring line 38 is unwrapped and exceeds line-length conventions.

**Verdict (advisory):** no blocking defect observed. F1 needs an L1 ruling before the fixture is final. F2-F4 are contract-risk or hardening items.

## Pre-landing findings (superseded where the landed code addresses them)

- H1 uncaught exception exit 1 — addressed (catch-all).
- H2 argparse default stdout — addressed (`Parser.error`).
- M1 duplicate JSON keys — addressed (`_pairs`).
- M2 truthiness on remote markers — addressed (`isinstance` checks).
- M3 `--selftest` unreachable under required args — addressed (validated after parse).
- M4 selftest must run real CLI — addressed (child processes).
- M5 selftest/verdict exit collision — L1 accepted; `finding_id` authoritative.
- L1 diagnostics echo caller values — addressed (fixed reason codes).

## Evidence used
- `tools/kama-ollama-evidence.py` lines 1-522 (read in ranges).
- `tests/ollama-evidence/cases.json` lines 1-768.
- Contract text: `.ufo/waves/round-14/spec.json`; lane task text: `.ufo/waves/round-14/dispatch.json`.

## Limits
- Static reading only; not executed. Exit-code and selftest results are unobserved.
- No check of whether the child-process selftest passes on a real interpreter.

## Installs / updates
None. No tool was installed, upgraded, or invoked beyond read-only file inspection and peer messages.
