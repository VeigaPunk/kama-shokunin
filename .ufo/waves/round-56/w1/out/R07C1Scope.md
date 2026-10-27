# R07C1Scope — C1 scope against operability

## Axis and claim
`AXES.md:13` defines operability as runnable artifacts (checklists/commands/scripts) that run and produce the stated outcome. The lane scope is local model serving and endpoint health (`shokunin.conf:52`). C1 is narrowly preregistered as an `env_leg` classification claim; it does not, by itself, claim a new endpoint-health capability or a score increase (8→8).

## Finding — scope wording overstates live-serving evidence (medium)
The observed battery tests do **not** exercise a serving endpoint or a llama-server process. `tools/round56-env-leg-test.py:20-29` launches `sleep 5` with `LD_AUDIT` in its environment, calls `mod.env_leg(pid, probs)` directly, and classifies the result by searching the problem strings. The committed receipts show old counter `ld_audit=missed`, new counter `ld_audit=detected`, and mutant `ld_audit=missed`, each with exit 0 (`.ufo/waves/round-56/measured/base-c1.out`, `build-c1.out`, `m-drop-ldaudit.out`). This demonstrates that the executable test distinguishes the variable name on a synthetic live child; it does not demonstrate endpoint health or detection on a running model server.

The preregistration predicate accurately says “live child process,” and its limits explicitly say this does not establish successful audit-DSO injection (`preregistration.json:13,49`). However, the `round56-env-leg-test.py` module docstring says “live child carrying LD_AUDIT” but says the value “must be rejected by the new BAD_ENV”; the counter's `env_leg` docstring calls it the “server environment” (`round56-replay-code-audit.py:430-433`). That phrasing, and the round goal's serving/endpoint-health context, can imply a live-serving measurement that these receipts do not support. Proposed fix: retain the current narrow C1 result, but label it consistently as a synthetic-child/unit probe of the `env_leg` name classifier and state explicitly that no server or endpoint was exercised; do not represent it as endpoint-health evidence.

## Runtime-path context
The full counter has a real-server path: `bind_one` waits for `ready.json`, checks that the announced PID descends from the replay, then calls `env_leg(pid, eprobs)` (`round56-replay-code-audit.py:687-706`). It aggregates that as an environment leg only when no environment problems were found (`:796-798`). But the frozen battery receipts are standalone `env_leg` calls, not outputs of that full counter path. Moreover, the replay constructs the server environment from `LIVE_ENV_KEYS = ("PATH", "HOME", "LANG", "LC_ALL")` plus `TMPDIR` (`tools/kama-live-replay.py:127-155`), so inherited `LD_AUDIT` is excluded; this round's synthetic injection does not establish behavior for a server actually launched with that variable.

The frozen full-counter docstring's summary question still names only `LD_PRELOAD` (and its leg list says `LD_PRELOAD`/`DYLD_INSERT_LIBRARIES`) at lines 8-15 and 63-65, while `BAD_ENV` includes `LD_AUDIT` at line 147. The new header and `env_leg` docstring describe the LD_AUDIT addition. This is a maintenance/documentation inconsistency, not evidence that the synthetic battery failed.

## Calibration / evidence boundary
The new counter hash matches the preregistered digest: `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f`. The standalone evidence supports the frozen detection predicate and its controls, but not a claim that an actual model server carried or rejected LD_AUDIT, that audit code injection succeeded, or that endpoint health was tested. The `/usr/lib/libexpat.so.1` probe output explicitly reports glibc rejected it for missing `la_version`; the preregistration correctly disclaims successful injection. No full C1 replay-counter result appears in the round-56 `measured/` or `controls/` outputs inspected here.

## Residual risk and verification gaps
- Keep C1 interpreted as a targeted operability test of a reusable classifier, with score unchanged; avoid extrapolating to current serving health.
- If a future claim needs live-server coverage, add an authorized end-to-end test through `bind_one`/replay with a controlled server environment, or clearly state why the replay whitelist makes such an injected environment unreachable. Do not change the frozen predicate after scoring.
- No endpoint-health observation was run by this seat; no fresh probe is claimed.
