# M02RenameAudit — round-56 env-name mutant

- **Mutant:** In an isolated scratch copy of `tools/round56-env-leg-test.py`, changed only the child environment keyword from `LD_AUDIT` to `LD_AUDIT_X`; retained the detector assertion and its `--expect` handling unchanged.
- **Expected detector:** Round-56 env-leg test with `counter-r56.py` and `--expect detected`; the same assertion logic used by `round56-env-leg-battery.py` must fail when the renamed key is not classified.
- **Frozen counter:** scratch copy SHA-256 `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f`, matching the preregistered digest. `env_leg` checks exact key membership in `BAD_ENV`; it does not match `LD_AUDIT_X` to `LD_AUDIT`.

## Commands and observed results

Commands below ran from `/fast/scratch/hyaku/kama-r56/M02RenameAudit`; `TMPDIR=/fast/scratch/hyaku/kama-r56/M02RenameAudit` and `PYTHONDONTWRITEBYTECODE=1` were used for detector invocations.

- Pristine r54 baseline: `python3 test.py --counter counter-r54.py --expect missed` → `ld_audit=missed pid=2289170 problems=[]`, `EXIT=0`.
- Pristine r56 positive control: `python3 test.py --counter counter-r56.py --expect detected` → `ld_audit=detected pid=2289171 problems=['env: server environment carries LD_AUDIT']`, `EXIT=0`.
- Mutant with expected-detected: `python3 test.py --counter counter-r56.py --expect detected` → `ld_audit=missed pid=2315567 problems=[]`, `EXIT=1`.
- Mutant with expected-missed: `python3 test.py --counter counter-r56.py --expect missed` → `ld_audit=missed pid=2315566 problems=[]`, `EXIT=0`.
- Replication of the battery's `run()` assertion against the mutant test: `round56-counter (mutant test): ld_audit=missed exit=1 -> fail`.
- Child-environment check: `LD_AUDIT_X present: True | LD_AUDIT present: False`.
- Restored pristine r56: `python3 test.py --counter counter-r56.py --expect detected` → `ld_audit=detected pid=2324613 problems=['env: server environment carries LD_AUDIT']`, `EXIT=0`.

The loader emitted the expected ignored-audit-object diagnostic in pristine runs: `ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.` This did not affect the detector exits.

## Verdict and restoration evidence

**Killed.** The renamed environment key is present in the live child, but exact-name classification reports no problem; the expected-detected assertion exits 1. The untouched expected-missed assertion exits 0. Pristine test SHA-256 before mutation and after restoration: `ec7a2519f6d4b2e1bd08a7ead042a53c7b60e2f58af8e4db008dfd661acf82ac`; restored `test.py` and `test.orig.py` hashes matched. No lane source or shared production file was modified. No tools installed or updated.
