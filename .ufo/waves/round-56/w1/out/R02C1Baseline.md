# R02C1Baseline — independent old-counter red-baseline rerun

**Result:** reproduced the frozen old-counter outcome; the test child was terminated and reaped. No test child remained afterward.

## Evidence and commands

The frozen battery identifies the old counter as `tools/round54-replay-code-audit.py` (`tools/round56-env-leg-battery.py:13`). Its `BAD_ENV` is `("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")` (`tools/round54-replay-code-audit.py:146`), while the round-56 counter adds `LD_AUDIT` (`tools/round56-replay-code-audit.py:147`). The round-56 counter's SHA-256 was independently checked as `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f`, matching the preregistration.

In `/fast/scratch/hyaku/kama-r56/R02C1Baseline` with `TMPDIR` explicitly set there, ran:

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round56-env-leg-test.py \
  --counter /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round54-replay-code-audit.py \
  --expect missed
```

Exact captured output is in `R02C1Baseline/base-c1-rerun.out`:

```text
ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.
ld_audit=missed pid=2054686 problems=[]
exit=0
```

After the harness returned, `kill -0 2054686` reported ESRCH (`pid 2054686 reaped`), and `pgrep -x sleep` reported `no sleep processes post-run`. There were no `sleep` processes before the run either.

A separate direct `env_leg` observation, with a child started using `LD_AUDIT=/usr/lib/libexpat.so.1`, confirmed `child_has_LD_AUDIT=True`, `env_leg_problems=[]`; after `terminate()`/`wait()`, it reported `returncode=-15 reaped=True`. Exact output is in `R02C1Baseline/observation.out`. The loader warning shows this glibc rejected the supplied object as an audit interface; this probe establishes variable-name presence/classification, not successful audit-DSO injection.

## Scoped finding

The old counter red baseline is independently reproduced exactly: the live child's `LD_AUDIT` name is present, the old `env_leg` does not classify it, and the harness's expected `missed` result exits 0. Process cleanup is verified. This matches the frozen baseline contract; no defect to report against this scoped target.
