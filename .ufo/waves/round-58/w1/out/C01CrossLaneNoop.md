# C01CrossLaneNoop: sibling-lane execution-binding and no-op controls (round 58)

Axes: operability (C1), calibration (C2, not touched). Read-only scan of sibling `tools/` plus one tip run.

## Checks run (exact commands, exit codes)
1. `git -C kama-shokunin show e4891d8a4c9c70e97124980c2ec9aee5762a7f0a:tools/round58-battery-exec-check.py > $S/checker-tip.py`, then `python3 $S/checker-tip.py --repo <kama> --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`
   output: `present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True`, exit 0. Matches the frozen build-tip row (met=True). Receipt: `.ufo/waves/round-58/w1/out/C01CrossLaneNoop/tip-checker-run.txt`.
2. Scan: `grep -rlE "setprofile|settrace|meta_path|addaudithook|importlib|unittest.mock|monkeypatch" */tools` over sibling lanes. Hits: mado, tsukuroi, mori, kaidoku, chousa, tameshi, kotodama (tools dirs).
3. Thread probe (`$S/probe_gaps.py`, `sys.setprofile` plus `threading.Thread` running `subprocess.run`): `thread_frames_seen_by_setprofile: 0`, exit 0. Confirms `sys.setprofile` is per-thread, so a `run` called in a worker thread is invisible to the checker.
4. Stub-gap probe (same script): `os.posix_spawn("/bin/true", ...)` ran unstubbed, exit 0. The kama harness stubs `subprocess.run/call/check_call/check_output`, `Popen`, and `os.system`. It does not stub `os.posix_spawn`, `os.execv*`, or `os.fork`.
5. Scratch `$S` removed afterwards.

## Candidates and fit
- **mado-shokunin `.ufo/waves/round-47/w1/ExecStraceTrip/auditwrap.py`** (`sys.addaudithook` in a `runpy` wrapper, `python3 -I`). Fit: yes, as a second in-process layer. It writes a hit per `os.exec*`, `os.system`, `os.spawn*`, `subprocess.*`, `_posixsubprocess.fork_exec`, `ctypes.*`. Its receipts show `ctypes.dlopen`/`call_function` and `_posixsubprocess.fork_exec` caught (`receipts/audit-bad-ffi.txt`, `audit-bad-forkexec.txt`). Caveat: the wrapper is a detector, not a sandbox. `audit-clean.txt` is empty. I did not run it against kama's battery. [INFERENCE] that wrapping the harness child with an audit hook would close gap 4, since CPython audits `os.posix_spawn`/`os.exec*`; unverified here.
- **mado `receipts/probe-run.txt` (L2, strace)**: confirms `strace -f -e trace=%process` sees `execv`, `posix_spawn`, `os_spawnv`, and `fork_only`. Fit: a process-level oracle outside the child. Heavier than needed for the C1 predicate; it needs `strace` and ptrace permission (yama=1 here). Not recommended for the frozen checker.
- **tsukuroi `tools/probe-git-child-env-r31.py`** (`strace -f -e trace=execve -v` over child argv/env). Fit: a pattern for counting real execve children; it is the environment-contract probe, not a battery binder. No fit for C1 beyond the strace note above.
- **mori `tools/mori-round15-regressions.py`** (`sys.modules` shim and a pinned helper digest). Fit: no. It is a fixture-pack gate, not execution binding.
- **kaidoku `tools/round-43/c2-controls-r43.py`** (byte-exact frozen control tables, sha256 verified, do-nothing control pinned to an old revision). Fit: yes as a pattern for building the C1 do-nothing controls so the control doesn't drift to the reference. Already the same idea as kama's frozen controls; no code reuse needed.
- **chousa `tools/mechanism-witness.py`** (`bash -x` PS4 trace witnessing which function ran). Fit: a witness pattern for shell gates, not Python batteries. No fit for kama.
- **tameshi `bash-witness-study.py` / kotodama** `sys.addaudithook('open')` read-set measurement (mentioned in `expected.json` notes, scratch-only). Fit: optional for reads, not for C1.

## Limits found in kama's checker (predicate unchanged; reported only)
- L1 (thread blindness): `run` frames in threads are not recorded, so a battery that dispatches its legs through a thread pool gets `executed=0` and is rejected. This is a false-reject risk, not a false-accept. The frozen 11 no-op variants and the genuine battery are single-threaded, so C1 is not affected.
- L2 (hermeticity): `os.posix_spawn`, `os.execv*`, `os.fork` are not blocked. A battery could start an unrecorded real process. The predicate still requires a `--counter` record per leg, so such a process does not satisfy acceptance. Not a bypass of the 11 no-op variants. Would need an audit-hook layer (candidate above) to close.
- No seat-found survivor outside the 11 enumerated variants was produced by this scan; I did not build new no-op variants.

## Verdict
- Pointers for C1: mado `auditwrap.py` (fit, second layer, unverified against kama); kaidoku control-table pattern (fit, already reflected).
- Tip checker reproduces the frozen `met=True` row.
- Not judged here: whether C1 is met under the frozen predicate, and C2 (calibration) is out of scope for this seat.

## Verification
- Run once: the tip checker (exit 0, met=True), the thread probe (exit 0), the posix_spawn probe (exit 0).
- Main agent should re-run the tip checker and the frozen counter `tools/round58-c1-counter.py` once, after the wave.
- No edits to kama, no git mutations, no sibling lanes modified; ran nothing in shokuknow. Scratch removed.
- Tooling: no installs.
