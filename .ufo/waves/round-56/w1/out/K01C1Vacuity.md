# K01C1Vacuity — round-56 C1 do-nothing control

Seat task: run the cheapest do-nothing control for C1 — the OLD (round-55-inherited)
counter against the same `LD_AUDIT` child — and answer whether it meets the new
predicate. Verdict: **no**; the predicate is non-vacuous.

## Identity of the "old counter"

The committed battery (`tools/round56-env-leg-battery.py:13`) names
`OLD = tools/round54-replay-code-audit.py`: round 55 inherited the round-54 counter
unchanged, so this file IS the round-55 counter (sha256
`c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`). The round-56
counter hashes to the frozen digest
`fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` — matches
preregistration.

The only env-relevant delta between them (diff of the two files):
`BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")` →
`("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")`, plus BASE/docstring updates.
`env_leg` (same shape in both) reads `/proc/<pid>/environ` keys and appends a problem
only for names in `BAD_ENV`.

## Commands run (all exit codes observed)

Cwd `/fast/scratch/hyaku/kama-r56/K01C1Vacuity`, `TMPDIR` set there. `python3
tools/round56-env-leg-test.py --counter <C> --expect <E>` from lane
`/home/vgpnk/Projects/shokunin/kama-shokunin`:

1. OLD, `--expect missed`  → `ld_audit=missed pid=2072955 problems=[]`, **exit=0**
   (battery posture; matches committed `measured/base-c1.out`).
2. OLD, `--expect detected` → `ld_audit=missed pid=2073023 problems=[]`, **exit=1**
   — under the NEW predicate the do-nothing control FAILS.
3. NEW, `--expect detected` → `ld_audit=detected pid=2073075
   problems=['env: server environment carries LD_AUDIT']`, **exit=0**.
4. Environ presence: `env LD_AUDIT=/usr/lib/libexpat.so.1 sleep 5`;
   `tr '\0' '\n' < /proc/$pid/environ | grep '^LD_AUDIT='` → exactly 1 line
   `LD_AUDIT=/usr/lib/libexpat.so.1`. Each child also emitted
   `ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit
   interface: undefined symbol: la_version; ignored.` — the DSO is refused, yet the
   variable NAME persists in environ, which is all the predicate requires.

Receipts copied to `.ufo/waves/round-56/w1/out/K01C1Vacuity/`.

## Why the old counter cannot meet the predicate

The predicate asserts on the variable NAME, not on successful audit-DSO injection.
The old `env_leg` loops `for bad in BAD_ENV: if bad in keys: probs.append(...)`;
`LD_AUDIT` is absent from its `BAD_ENV`, so `probs` stays empty → `detected` is
False → `ld_audit=missed`. With `--expect detected` the driver returns 1. No
special-casing, timing, or glibc refusal changes this: detection is a tuple
membership test over names.

## Impact on the claim

- C1 kill rule untouched: base counter misses (run 1), round-56 counter detects
  (run 3), frozen sha256 verified locally. The do-nothing lane is genuinely red
  against the new predicate, so "do nothing" is correctly falsified — the predicate
  is not vacuously satisfiable.
- No defect affecting scoring.

## Minor wording defect (non-scoring)

`preregistration.json` C1 target prose says the mutant "misses it so the battery's
expected-detected check fails". The committed battery actually runs the mutant with
`--expect missed` (`round56-env-leg-battery.py:50`) and PASSES it (exit 0 in
`measured/m-drop-ldaudit.out`) — correctly, since the mutant is the kill designated
to reproduce baseline behavior. The prose describes a hypothetical
expected-detected assertion that does not exist in the battery. Cosmetic only;
suggested fix: reword to "the mutant misses it, matching baseline, and would fail
any expected-detected assertion" — or leave as is; the kill rule already covers the
dangerous case ("the single-line mutant still detects it").

## Tool installs

None (python3 + coreutils only; pacman untouched per pause).

Report: .ufo/waves/round-56/w1/out/K01C1Vacuity.md
