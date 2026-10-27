# R03C1Build — independent rerun of the round-56 positive control

Axes: operability (C1), calibration (C2). Seat scope: rerun the C1 positive control and verify LD_AUDIT is present in `/proc/<pid>/environ` and rejected. Leaf member — no subagents, no lane mutations, one scratch dir.

## Identity checks

- Lane HEAD at run time: `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` (the freeze commit).
- `sha256sum tools/round56-replay-code-audit.py` → `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` — **equals the frozen digest** (C1 kill-rule identity condition holds).
- `sha256sum tools/round56-prereg-check.py` → `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` — equals the frozen C2 digest (noted in passing; C2 legs were not this seat's assignment).
- Base counter for the red baseline: `git show e10b6d39af450e8d652be9ac2986768b531fe13f:tools/round54-replay-code-audit.py` — byte-identical (`cmp`) to the tip's `tools/round54-replay-code-audit.py`, whose `BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")` carries no `LD_AUDIT` (line 146), so the round-55 counter is exactly the expected red baseline. sha256 `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`.

## Rerun legs (all commands run with `TMPDIR=/fast/scratch/hyaku/kama-r56/R03C1Build`, from the lane root; receipts in `out/R03C1Build/`)

1. Positive control — `python3 tools/round56-env-leg-test.py --counter tools/round56-replay-code-audit.py --expect detected`
   → `ld_audit=detected pid=1924868 problems=['env: server environment carries LD_AUDIT']`, `exit=0`. Matches the frozen target (detected, exit 0). Receipt: `out/R03C1Build/leg1-positive.log`.
2. Red baseline — `python3 tools/round56-env-leg-test.py --counter <scratch>/round54-counter-base.py --expect missed`
   → `ld_audit=missed pid=1930467 problems=[]`, `exit=0`. Matches the frozen target (missed, exit 0). Receipt: `out/R03C1Build/leg2-baseline.log`.
3. Kill mutant `m-drop-ldaudit` — scratch copy of the frozen counter with the one-line deletion `LD_AUDIT` from `BAD_ENV` (full diff: `out/R03C1Build/mutant.diff`, one changed line), run with `--expect detected`
   → `ld_audit=missed pid=1933622 problems=[]`, **`exit=1`**: the battery's expected-detected assertion fails exactly as the target demands. Receipt: `out/R03C1Build/leg3-mutant.log`.
4. Independent `/proc` witness (own harness `verify-proc-environ.py`, names only) — spawned `sleep 5` with `LD_AUDIT=/usr/lib/libexpat.so.1`:
   → `pid=1930466 environ_names=269 LD_AUDIT_present=True value_exact=True expat_mapped_rows=0`; child stderr: `ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.`; verdict `present-and-rejected`, `exit=0`. Receipt: `out/R03C1Build/leg4-proc-witness.log`.

## Verdicts

- **LD_AUDIT present in `/proc/<pid>/environ`**: yes — byte-exact entry `LD_AUDIT=/usr/lib/libexpat.so.1` in the live child's environ (name read from `/proc`, not assumed from `Popen`).
- **Rejected**: yes, twice — (a) rtld refuses the object as an audit interface (`undefined symbol: la_version`) and maps no `libexpat` row (`expat_mapped_rows=0`), consistent with the preregistration `limits` note; (b) the round-56 counter's `env_leg` flags the variable by name (`env: server environment carries LD_AUDIT`).
- **C1 positive control**: independently reproduced end-to-end (baseline missed / counter detected / kill mutant misses and fails the battery). No kill-rule condition triggered: counter sha matches the frozen digest, baseline misses, round-56 counter detects, mutant misses.

## Defect scan

- No defect found in the exercised paths. The 0.05 s probe window after `Popen` is safe against the 5 s child; stdout/stderr interleaving of the driver's output vs the child's rtld error varies between runs (buffering) and is cosmetic only.
- Observation, not a defect: the witnessed environ carries 269 inherited names; `env_leg` reads names only and records them, never values — consistent with its docstring and no value leakage observed in outputs.

Residual risk: legs cover the env-leg driver only; the counter's replay/server legs (frozen `SERVER_SHA` model serve, bind, kill) were not this seat's assignment and were not run.

Report: .ufo/waves/round-56/w1/out/R03C1Build.md
