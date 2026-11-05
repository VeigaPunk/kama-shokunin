# MT02GateArmBattery — C2 gate-arm mutation battery (round 87, wave 1)

Seat: MT02GateArmBattery. Judged on: operability. Milestone: kama r87 w1.
Revision measured: `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659` (freeze commit; scratch clone verified
toplevel, `git status --porcelain` empty, HEAD equal). Base `362b0d4a241520c9bc79b204c042d9fcefbb06ea`.

## Scope

- Built `battery.py` (independent mutation battery for arm `round86-instruments`), to be run by the L1 on the
  integrated EX02 candidate. Delivered at
  `.ufo/waves/round-87/w1/out/MT02GateArmBattery/battery.py` (349 lines, sha256
  `0da3e75fd0f3146b5db4ba4ac81fdac8964b091ffa159e51cfc2bf28084e83b3`).
- Ran it against the MASTER gate at `94e8fe7b` (committed `tools/pre-report-gate.py`, sha256
  `0ad6a80aa20af72eea5741fd3a44e62840c260692c7e65b45e0ea8dd04316979`, equal to `git show HEAD:` blob hash).
- Validated the battery itself against a synthetic candidate (`synth-candidate-builder.py`: master gate plus a
  round86-instruments arm wired as the frozen C2 claim describes, with three green instrument stubs). The
  synthetic candidate is NOT EX02's candidate and proves nothing about EX02; it only proves the battery kills
  a correct-looking arm's seven faults.
- No candidate files, no lane writes, no git writes, no subagents, no network, no tool installs.

## Commands and outputs

Master gate (mandated run), `exit=0`, wall `52.94s`:
```
$ python3 battery.py --gate <scratch>/master-gate/pre-report-gate.py --repo <scratch>/wt
GATE_ARM_MUTANT G1 expect=killed got=escaped
GATE_ARM_MUTANT G2 expect=killed got=escaped
GATE_ARM_MUTANT G3 expect=killed got=escaped
GATE_ARM_MUTANT G4 expect=killed got=escaped
GATE_ARM_MUTANT G5 expect=killed got=escaped
GATE_ARM_MUTANT G6 expect=killed got=escaped
GATE_ARM_MUTANT G7 expect=killed got=escaped
GATE_ARM_MUTANTS mutants=7 killed=0 escaped=7
```
Stderr (`master-run.stderr.txt`): pristine arm `missing` on all three scenarios; every mutant
"not applied" (no arm function, no ARM_ORDER entry, no append site, no `"round86-instruments"` literal).
Consistent with the expectation: with no arm, every mutant counts as escaped.

Synthetic candidate (battery self-check), `exit=0`, wall `173.14s`:
```
GATE_ARM_MUTANT G1..G7 expect=killed got=killed   (all seven)
GATE_ARM_MUTANTS mutants=7 killed=7 escaped=0
```
Per-mutant kill clause (stderr, `synth-selftest.stderr.txt`):
- G1 arm missing on default -> killed by "missing".
- G2 always-ok, pristine not-ok on default -> killed by masking clause.
- G3 weakened summary, pristine not-ok on default -> killed by masking clause.
- G4 arm reads repo `tools/` (real instruments green, `pass=17 fail=0`, `pass=13 fail=0`), pristine not-ok
  on default -> killed by masking clause. Note: the clone's `tools/` already contains three real round86 files
  (`round86-mutant-owners.py`, `round86-pin-origin.py`, `round86-rendered-cells.py`), so the leak is green and
  only the masking clause kills it.
- G5 first-only loop, pristine not-ok on the g5 scenario -> killed by masking clause.
- G6 exception swallowed, pristine `missing` (real `RuntimeError` injected into the gate's instrument call) ->
  killed by masking clause.
- G7 renamed arm, arm missing on default -> killed by "missing".

Pre-run, `python3 -m py_compile` on battery.py printed `compile-ok`; `ast.parse` `ast-ok`.

## Findings

1. Verdict rule clarified (deviation from the literal seat text, required to be consistent). The seat says
   "killed iff the arm is missing or not ok" and also "with no arm, every mutant escapes". Under the literal
   rule G2, G3, G5, G6 can never be killed (the mutant arm is ok on every fault), and G4 is killed only by
   accident. The battery therefore kills a mutant when its arm is missing or not-ok, OR when its arm is ok while
   the pristine candidate arm is not-ok on the same faulty tools (the mutant masks a fault). Anchor-absent
   mutants count escaped. Evidence: `battery.py` `verdict()` and docstring.
2. Real instrument summary prefixes (for the L1 and for EX02). The arm's `ROUND86_MODULES` must use the
   prefixes the instruments actually print:
   - `round86-rendered-cells.py` -> `RENDERED_CELLS_SELFTEST` (`round86-rendered-cells.py:503`)
   - `round86-mutant-owners.py` -> `DEBT_MUTANT_OWNERS_SELFTEST` (`round86-mutant-owners.py:253`), NOT
     `MUTANT_OWNERS_SELFTEST`. A candidate using the wrong prefix fails its own real instrument.
   - `round86-pin-origin.py` -> `PIN_ORIGIN_SELFTEST` (`round86-pin-origin.py:275`)
   These are the lines the grep returned; the battery itself derives the tuple from the candidate, so it does
   not depend on this list.
3. My first synthetic candidate used the wrong `MUTANT_OWNERS_SELFTEST` prefix; the arm then failed on
   the real instrument. Corrected in `synth-candidate-builder.py`; no effect on the master result.
4. Limitation: the instrument summary detail in the G4 stderr line is truncated at 200 chars, so
   `round86-pin-origin.py`'s own result is not fully visible in the receipt. I did not run the instruments
   directly (out of item scope).
5. `--work` is honored (battery's own mkdtemp lives under it and is removed on exit). Without `--work` the
   battery uses `tempfile`, which honors `TMPDIR` and falls back to the platform default; the battery itself
   never names `/tmp`.

## Required correct-arm behaviour, per mutant (for the L1 to check EX02's candidate by reading)

- G1 (arm removed): `"round86-instruments"` must be an entry in `ARM_ORDER`, after `round83-instruments`, and
  `evaluate()` must append the arm's result. Removing either makes the arm missing.
- G2 (always-ok): the arm function must derive `ok` from each instrument's own exit code and fullmatched
  summary; it must not hard-code `"ok": True` or return ok without running the three instruments.
- G3 (weakened summary): each instrument's final line must fullmatch `<PREFIX> pass=[0-9]+ fail=0`
  (literal `fail=0`, so `pass=0 fail=1` fails), and exit must be 0. Both conditions are required.
- G4 (tools path leak): instruments must be resolved with `os.path.join(tools_path, script_name)` (the
  `tools_dir` argument), never from `repo_path` or a hard-coded `tools/` path. The clone already carries real
  round86 instruments, so the leak is only visible through the faulty `tools_dir` copy.
- G5 (first instrument only): all three modules in the tuple must run, and a missing, red or malformed
  summary from ANY of them must set the arm not-ok. The loop must not be sliced (`[:1]`, `break`, early return).
- G6 (exception swallowed): the arm must not catch exceptions around its instrument calls or around the
  append, and must not convert an exception to ok. Any exception must propagate or produce not-ok.
- G7 (renamed arm): the string `"round86-instruments"` must be the same literal in `ARM_ORDER` and in the
  returned dict's `"name"`, with no `round-86-instruments` variant.

VERDICT: battery built and validated (synthetic correct-looking arm kills 7/7; master gate kills 0/7 with
exit 0 on every run), the EX02 candidate is not yet checked by it; the L1 runs `battery.py` on the integrated gate.
