# R04C1Mutation — C1 falsification

## Result
The one-line `m-drop-ldaudit` mutant is faithfully reproduced, and it is killed by the expected-detected check: its `env_leg` output is `ld_audit=missed`, while `round56-env-leg-test.py --expect detected` exits 1. The frozen counter detects the same live-child variable and exits 0 under `--expect detected`. This supports the frozen C1 target; it does not assess C2.

## Mutant integrity
- Frozen counter SHA-256: `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` (matches the preregistration).
- Mutant SHA-256: `a3faaf6ea4c0ec0a4232d1a96da8e351d5584c0e116d9707e61e4342f364ddb4`.
- Construction: copied the frozen counter to the seat scratch, then changed only line 147 from `BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")` to `BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")`. `diff` showed exactly that one-line hunk (`diff_exit=1`, ordinary diff-found-changes status). The frozen deletion anchor occurred exactly once. The mutant's remaining `LD_AUDIT` text is in explanatory docstrings, not the BAD_ENV tuple.
- Source behavior: `env_leg` calls `environ_keys(pid)` and appends `env: server environment carries {bad}` for each `bad` in `BAD_ENV` (`tools/round56-replay-code-audit.py:430-441`).

## Executed checks
Ran each from `/fast/scratch/hyaku/kama-r56/R04C1Mutation` with `TMPDIR=/fast/scratch/hyaku/kama-r56/R04C1Mutation/tmp`, using:

`python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round56-env-leg-test.py --counter <counter> --expect <expected>`

| Counter | Expected | Observed stdout | Exit | Outcome |
|---|---|---|---:|---|
| `tools/round54-replay-code-audit.py` (old baseline) | `missed` | `ld_audit=missed pid=2315570 problems=[]` | 0 | match |
| `tools/round56-replay-code-audit.py` | `detected` | `ld_audit=detected pid=2315573 problems=['env: server environment carries LD_AUDIT']` | 0 | match |
| scratch `counter-m-drop-ldaudit.py` | `missed` | `ld_audit=missed pid=2315576 problems=[]` | 0 | match |
| scratch `counter-m-drop-ldaudit.py` | `detected` | `ld_audit=missed pid=2315579 problems=[]` | 1 | **expected-detected assertion fails; mutant killed** |

All four child runs also emitted this loader diagnostic on stderr: `ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.` The DSO path exists as `/usr/lib/libexpat.so.1` (symlink to `libexpat.so.1.13.0`). This is consistent with the claim's stated limit: the probe checks the environment variable name, not successful audit-DSO injection.

Independent environment witness: spawned `sleep` with `LD_AUDIT=/usr/lib/libexpat.so.1`, then read `/proc/<pid>/environ` after 0.05s and 0.30s; both samples returned `LD_AUDIT_in_environ=True` and `LD_AUDIT=/usr/lib/libexpat.so.1`. An immediate pre-settle sample was false due to racing `execve`; it was not used as evidence.

## Battery semantics and evidence
The committed battery defines the mutant roster expected value as `missed` and runs that mutant leg with `--expect missed` (`tools/round56-env-leg-battery.py:15-18, 42-50`); that roster leg passes when it misses. The expected-detected falsification is the separate direct run above (`--expect detected`, exit 1). I did **not** execute the committed battery because it writes receipt files under the read-only lane `measured/` directory. The pre-existing measured receipts agree with the control and mutant legs.

Copied exact leg output receipts are under `.ufo/waves/round-56/w1/out/R04C1Mutation/receipts/`: `replay-base-c1.out`, `replay-build-c1.out`, `replay-m-drop-ldaudit.out`, and `replay-m-drop-ldaudit-expect-detected.out`.

## Defects / proposed fix
No defect found in the one-line mutant or the expected-detected test result. Scope nuance: the committed roster battery's mutant entry expects `missed`; the claim's phrase “battery's expected-detected assertion fails” is demonstrated by the separate direct expected-detected invocation, not by the battery's mutant roster leg itself. No change proposed, since changing the roster expectation would alter the frozen preregistered contract.
