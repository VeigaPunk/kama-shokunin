# K04ClaimSizing — C1 scope and re-derivability

## Axes
- **Operability:** C1 is a single, re-derivable `env_leg` predicate: whether `LD_AUDIT` appears among the live child’s `/proc/<pid>/environ` variable names and is appended to `probs`. The observed transition is `missed` → `detected`; the frozen round-56 counter hash matches preregistration.
- **Calibration:** The specified before/after controls are reachable in one round and distinguish the one-line `BAD_ENV` change. The unchanged score `8 -> 8` is not evidence of broader service improvement.

## Evidence
- Frozen C1 predicate/target and limits: `.ufo/waves/round-56/preregistration.json` lines 13–16, 49. The limits expressly constrain the result to environment-variable-name rejection and disclaim successful audit-DSO injection and a complete replay-code audit refresh.
- `tools/round56-env-leg-test.py` lines 20–29 sets `LD_AUDIT`, launches a live `sleep` child, calls selected `env_leg`, and returns according to the expected detected/missed value.
- `tools/round56-replay-code-audit.py` lines 147 and 430–441 adds `LD_AUDIT` to `BAD_ENV`; `env_leg` records a problem when present. In `bind_one` lines 705 and 824–825, the environment leg is returned as `envnames`; `main` lines 941, 949, 955 requires it for `met`. Thus detection is not merely cosmetic.
- The compared round-54 counter has `BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")`; the round-56 diff’s functional change is adding `LD_AUDIT` to that tuple. The round-55 start is `e10b6d39`, and the freeze is `efc6b3ec`.
- Observed frozen receipts: `controls/base-c1.out` reports `ld_audit=missed`, exit 0; `measured/build-c1.out` reports `ld_audit=detected` and `env: server environment carries LD_AUDIT`, exit 0; `measured/m-drop-ldaudit.out` reports `missed`, exit 0. The loader also emits the expected warning that this particular libexpat object lacks `la_version`; this does not affect the name-presence probe.
- `sha256sum`: round-56 counter `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` (matches frozen); prereg checker `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` (matches frozen).

## Counterexample / defect
The narrow C1 value is solid, but one target sentence is polarity-ambiguous: preregistration line 14 says the mutant misses, “so the battery’s expected-detected check fails.” The committed battery instead calls the mutant with `--expect missed` (lines 18, 42–50), so this is an expected successful kill demonstration, not a failing battery run. The measured mutant receipt indeed exits 0. The correct failure condition is that the mutant still detects `LD_AUDIT` (or that the positive control does not detect it); the mutant’s expected `missed` result is a pass for the kill battery.

Also, “round-55 counter” is the inherited `tools/round54-replay-code-audit.py` file, not a file named round55; the baseline tip is the round-55 start. This is understandable from history but less directly reproducible by the filename alone.

## Broader-guarantee boundary and smallest safe correction
Do not read this as proof that an arbitrary audit DSO can inject code, that `LD_AUDIT` is removed, or that every replay/server endpoint is healthy. It establishes detection of the variable **name** in a controlled live child and its contribution to this counter’s environment leg; the frozen limits already disclaim the wider guarantees. Keep predicate, scoring, counter, and kill rule frozen. Correct only the explanatory target prose in any future report/version: state that mutant `missed` is the expected battery pass, and identify the baseline as the round-55 tip’s inherited round-54 counter. No post-score preregistration edits recommended.