# R01C1Semantics — Round 56 env-leg review

## Detection path and evidence

At freeze `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`, `tools/round56-replay-code-audit.py` has `BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")` (line 147). `environ_keys(pid)` reads `/proc/<pid>/environ` as bytes, splits NUL-delimited entries, extracts bytes before the first `=`, decodes names as UTF-8 with replacement, and returns a set; `OSError` returns `None` (325–330). `env_leg` reports unreadable as a problem and returns `None`; otherwise it compares each BAD_ENV entry by exact set membership and adds `env: server environment carries <name>` before returning sorted names (430–441). In the live counter flow it runs only after the reported server pid is confirmed to descend from the replay process (695–705); env problems are emitted in the receipt (796–798, 817–818).

Verified frozen counter SHA-256 `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f`, matching preregistration. Live commands, run in `/fast/scratch/hyaku/kama-r56/R01C1Semantics`:

- `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round56-env-leg-test.py --counter /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-replay-code-audit.py --expect missed` → `ld_audit=missed ... problems=[]`, exit 0. The loader emitted `ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.`
- Same command with `round56-replay-code-audit.py --expect detected` → `ld_audit=detected ... problems=['env: server environment carries LD_AUDIT']`, exit 0; same loader warning.
- One-line mutant removing `LD_AUDIT` from BAD_ENV with `--expect missed` → `ld_audit=missed ... problems=[]`, exit 0. With `--expect detected` → `ld_audit=missed ... problems=[]`, exit 1.

The direct test checks that `/proc` exposes the variable name despite the deliberately unsuitable audit DSO being rejected by this glibc. It does not demonstrate successful DSO audit injection; the preregistration explicitly limits C1 to name detection.

## Edge review / disposition

No actionable false positive or false negative was found for the frozen predicate. Exact-name membership avoids substring/name collisions; byte parsing preserves ASCII `LD_AUDIT` even if other names are malformed UTF-8; empty values remain conservatively flagged. Unreadable or vanished pids fail closed as `None` and produce a problem, not a clean result. A zombie/reaped-pid probe returned `None` and `env: environ of pid … unreadable`; a live child carrying LD_AUDIT produced the expected problem.

One wording mismatch is worth recording, but does not invalidate the measured predicate: the preregistration says the mutant “so the battery's expected-detected check fails,” whereas the committed battery roster explicitly assigns `m-drop-ldaudit` expected=`missed` (battery lines 15–18), and the runner invokes that mutant with `--expect missed` (line 50). Accordingly, the mutant leg itself passes when it misses; the positive-control leg's expected-detected assertion would fail if that mutant were substituted for the positive control. The one-line mutant was observed to miss, and substitution for the detected expectation was observed to exit 1.

The preregistration calls the red baseline the “round-55 counter”; the battery selects `tools/round54-replay-code-audit.py`. At base commit `e10b6d39af450e8d652be9ac2986768b531fe13f`, the available replay counter is round54; the round-56 freeze commit message identifies that base as the round-55 verifier spot-check. This is a naming/history convention, not a behavior discrepancy.

## Verification gaps

I exercised the focused env-leg driver and mutant only. I did not run the full battery or replay-code audit. No additional variable coverage (for example, names outside frozen BAD_ENV) is claimed.