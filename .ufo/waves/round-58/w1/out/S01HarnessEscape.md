# S01HarnessEscape — round-58 harness review (operability)

Target `tools/round58-battery-exec-check.py` at tip `e4891d8a`, invoked as the frozen counter invokes it
(`python3 CHECKER --repo FIXTURE --tip HEAD --work <scratch>`, fixtures in
`/fast/scratch/hyaku/kama-r58/S01HarnessEscape`). Escapes ran inside the checker's own harness child;
markers outside scratch were captured, then deleted. No lane write. Receipts: the sibling directory.

## Verdict
Four batteries that should be rejected are accepted `met=True` (genuine baseline accepted too): escape
(real exec + writes outside scratch), forged (executes nothing), fabricated (nonexistent script),
faillegs (3/4 own assertions false). Frozen C1 is unchanged at the tip (counter rc=0: genuine=1/1
benign=3/3 noop_rejected=11/11 errors=0 met=True) — LIMITS on what the checker certifies, not predicate changes.

## F1 CRITICAL — battery authors the evidence file
`--harness-out <res>` is in the child's `sys.argv` (probe E14 captured it verbatim). A battery writes its
own `{"frames": [...]}` then calls `os._exit(0)`, so the harness's `open(out_path,"w")` after `exec` never
runs and the forged file is read as evidence. `fixtures/forged` defines no
`run`/`assert_mutant_breaks_detection` and executes nothing; checker -> rc=0
`roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=n/a met=True`; direct harness child
rc=0 and `harness-result-forged.json` is the battery-authored frames. Attacks C1's "executed battery legs"
and S517's "stubbed side-effect records" premise: the record is battery-supplied text, not observation.
Impact: arbitrary C1 credit with zero legs.

## F2 CRITICAL — acceptance scores call shape, not leg outcome
`faillegs` ledger `{"all_ok": false}`: 3/4 legs `ok:false` (base-old observed `detected` vs expected
`missed`; m-drop-ldaudit same; mutant assert rc 0 vs required 1) -> checker rc=0 `legs=3/3 met=True`.
`fake_run` returns a constant `ld_audit=detected`, so the genuine battery's own assertions also fail under
the harness while `genuine accept exit=0`. N01/N06 are rejected only for lacking the `--counter` string,
not for doing no work (`fabricated` calls a nonexistent script and is accepted).

## F3 HIGH — "nothing is written, nothing is run" is false
In the accepted escape battery (`escape-report.json`): `open(p,"w")` E1 true, `Path.open("w")` E3 true,
`os.makedirs` E0 true, `shutil.copy` E8 true, `os.remove` E9 true — 5 files created/removed in
`/home/vgpnk/kama-r58-S01-escape/` 16:55:10-16:55:28; `ctypes.CDLL(None).system(b"uname -n > ...")` E10
rc=0 wrote host `plazir27`; `importlib.reload(subprocess)` E12 -> real `git version 2.56.0`; `os.posix_spawn`
E13 -> pid 2916434; `open("/etc/hostname")` E2 -> `plazir27` (real FS, bypasses `blob_for`). Same battery:
checker rc=0 `legs=3/3 mutant_assert=1 met=True`. Controls that hold: `os.system` E5 blocked, `Popen` E6
blocked, `os.popen` E4 blocked via `Popen`, `Path.write_text/write_bytes/mkdir` E7 swallowed, `TemporaryDirectory` E11 virtual.

## F4 HIGH — `clean_env` scrubs only `GIT_*`
`PYTHONPATH=<scratch>/pyinj` `sitecustomize.py` -> 2 runs (pid 2952859 checker, pid 2952977 harness child,
both argv1=`--repo`); `LD_PRELOAD` constructor -> 7 runs (checker, child, its git children). Both still
`met=True`: pre-patch code execution in the process that is supposed to be hermetic.

## F5 MEDIUM — observer control and scratch scope
The battery calls `sys.setprofile(None)` successfully, keeps its recorded frames, then E12 runs a real
command unobserved; exec'd descendants (E12/E13) are outside the profiler by construction. `--work`/`TMPDIR`
only places the checker's own files: the demonstrated primitives write to `$HOME` and would write to the
lane equally (not executed; lane read-only for this seat).

## Smallest remediation
R1 (F1) evidence over an inherited pipe written incrementally; missing/partial = could-not-evaluate; never trust a child-argv path.
R2 (F2) require the battery's own exit 0 and/or receipt fields in addition to frames.
R3 (F3/F5) run under `bwrap`/`unshare`: lane read-only, scratch-only writable, no network — monkeypatching cannot cover builtin `open`, `ctypes`, `os.posix_spawn`.
R4 (F4) scrub `PYTHONPATH PYTHONHOME PYTHONSTARTUP PYTHONUSERBASE PYTHONNOUSERSITE LD_PRELOAD LD_AUDIT`; run the child with `-I -S`.
R5 (F5) `sys.addaudithook` (cannot be removed) or external observation (ptrace/strace).

## Limits, not credit
Survivors outside the 11 enumerated variants are LIMITS; `c1-tip.out` still rc=0, 11/11 rejected, met=True.
Lane diffs present at seat start (S517/S518 rows, round-56 measured outs at 16:51:52) are not this seat's; grep for `kama-r58-S01-escape` in the lane returns nothing.
