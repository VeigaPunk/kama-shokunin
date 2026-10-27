# X12Portability — round 59 / kama / w1 (advisory falsification, leaf)

Seat move: inspect interpreter availability and exercise the frozen C1 checker/counter and the
C2 counter with the interpreters actually present, separating *observed* runs from *unrun*
interpreters. Axes: operability, calibration.

## Attacked clauses

- C1-r59 sentence/predicate: "each round-56 battery leg is accepted only when its own named
  expected outcome is tied to that leg's actual observed field/value and exit … 0 evaluation
  errors", measured by `tools/round59-c1-counter.py` at `aca8d0067ea25627c5015c2193c843965148bc8e`.
  Axis attacked: **operability** — is the measurement the same object on every interpreter and
  environment the lane can actually be verified on, and are its inputs fail-closed?
- C2-r59 sentence/predicate: calibration row re-derived "from the lane tree plus the explicitly
  named fleet HEAD"; "successful counter output must bind the exact lane tip and resolved fleet
  revision". Axis attacked: **calibration** — reproducibility of the binding.
- Kill rules were treated as exact and were not touched. No target, counter, variant, or frozen
  control was modified; all fixtures were built by the counters themselves in my scratch.

## Frozen commands issued (verbatim, cwd = ambient fleet root)

```
python3 tools/round59-c1-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip aca8d0067ea25627c5015c2193c843965148bc8e --work /fast/scratch/hyaku/kama-r59/X12Portability/work-<cfg>

python3 tools/round59-c2-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip 2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 --fleet-ref HEAD
```
(`TMPDIR` was exported to my scratch for every run; `<cfg>` varied only by interpreter.)

## Interpreter inventory actually present (observed)

| interpreter | implementation / version | source |
|---|---|---|
| `/usr/bin/python3` (= `python3`, = `python`) | CPython 3.14.8 | system |
| `~/.local/bin/python3.11` | CPython 3.11.17 | uv |
| `~/.local/bin/python3.12` | CPython 3.12.15 | uv |
| `~/.local/bin/python3.13` | CPython 3.13.16 | uv |
| uv `cpython-3.9` | CPython 3.9.25 | uv, pre-installed |
| uv `cpython-3.10` | CPython 3.10.22 | uv, pre-installed |
| uv `cpython-3.15` | CPython 3.15.0 | uv, pre-installed |
| uv `cpython-3.14+freethreaded` | CPython 3.14.8, `Py_GIL_DISABLED=1` | uv, pre-installed |
| uv `pypy-3.11` | PyPy 3.11.16 | uv, pre-installed |

No install or update was performed for this seat (`uv 0.13.0` used read-only via `uv python list`).

## O1 — interpreter invariance (observed, all runs)

C1 at `aca8d006` under **3.9, 3.10, 3.11, 3.12, 3.13, 3.14.8, 3.14t, 3.15.0, PyPy 3.11**:
every run `rc=0`, and all nine output files are byte-identical
(`md5 bbe6582183e1bb674685b6763797904d`):

```
tip=aca8d0067ea25627c5015c2193c843965148bc8e
predicate=C1-r59 outcome-binding checker accepts genuine+3/3 benign and rejects 16/16 no-ops, errors=0
genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True
```

C2 at `2c7443ab` under the same nine interpreters (plus the `--out` path): every run `rc=0`,
byte-identical (`md5 d8e166be2941e24f1f3c8cf713d8734d`):

```
tip=2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 fleet=3f3dd97345ef1aedfdaec818c9e58675d4f41e3f maxN=57 manifest=rejected-honest-stop
rows=44 mismatches=0 met=True
row_missing=0 typed_count=0 pinned_fleet_revision=0 pointer_missing=0 pointer_round=0 pointer_verdict=0 including_round=0 count_command=0
```

The standalone checker `tools/round59-battery-outcome-check.py --repo <lane> --tip aca8d006…`
under CPython 3.9 and under `/usr/bin/python3` both printed verbatim
`runs=5 passed=5/5 errors=0 met=True` with `rc=0`.

**Interpretation:** the checker/counter measurement carries no interpreter ambiguity across
CPython 3.9–3.15, the freethreaded build, or PyPy. The `sys.setprofile`-based frame capture and
the `--child` re-entry behave identically everywhere tested. This *supports* C1's operability on
the interpreter axis; it is not by itself evidence that the legs are outcome-bound (that is the
other seats' attack).

## O2 — interpreter binding is `sys.executable`, not `PATH`

Probe: prepend `$S/decoybin` containing a `python3` that prints `DECOY python3 INVOKED` to stderr
and exits 99, then run C1 under CPython 3.13 with `PATH="$S/decoybin:$PATH"`.

```
rc=0 ; occurrences of DECOY in output: 0 ; met=True (identical hash)
```

C1 and the checker spawn children with `sys.executable`, so only the *top-level* `python3` in the
frozen command resolves through `PATH`. Recorded because the frozen command line itself says
`python3` (unpinned), while the measured behaviour is interpreter-invariant (O1), so the unpinned
name is harmless here — the host's `python3` is 3.14.8 and is one of the nine verified configs.

## O3 — other environment dimensions (observed)

| probe | result |
|---|---|
| `LC_ALL=C LANG=C`, cwd `/` | C1 `met=True rc=0`, identical output |
| `LC_ALL=C` + `--out` on C2 | identical text to UTF-8 run, `rc=0` |
| `PYTHONOPTIMIZE=1` (C1) / `=2` (C2) | `met=True rc=0`, identical |
| `python3 -X dev` (C1) | `rc=0`, no ResourceWarning/DeprecationWarning emitted |
| `--work "<path with spaces>"` | `rc=0`, `met=True` |
| two concurrent C1 runs sharing one `--work` root | both `rc=0`, identical (`mkdtemp` isolation) |
| four C1 + four C2 runs in parallel across interpreters | all `rc=0`, identical |
| `TMPDIR` pointing at a non-existent nested path | created by `os.makedirs`, `rc=0`; C2 needs no scratch at all |
| `--work` omitted, `TMPDIR` set | `rc=0`, identical |
| direct shebang exec (`./tools/round59-c2-counter.py …`) | `rc=0` (mode 0755, `#!/usr/bin/env python3`) |
| imports of the three tools | stdlib only: `argparse, json, os, pathlib, re, shutil, subprocess, sys, tempfile` |
| declared Python floor | **none** (`pyproject.toml`, `setup.cfg`, `.python-version`, README requirement absent); 3.9 is the empirically tested floor |

## F1 — FAIL-CLOSED input handling (observed, all correct)

```
--tip deadbeef   (C1) -> could-not-evaluate: invalid tip                          rc=2
--tip deadbeef   (C2) -> could-not-evaluate: unresolvable lane tip or fleet ref    rc=2
--fleet-repo /nonexistent/fleet -> could-not-evaluate: unresolvable …              rc=2
--fleet-ref nosuchref            -> could-not-evaluate: unresolvable …              rc=2
--fleet-repo <the lane>          -> could-not-evaluate: missing SCORECARD, lessons tree, or MANIFEST  rc=2
--checker /nonexistent/checker.py-> could-not-evaluate: checker file absent        rc=2
```

Non-vacuity probes (scratch-only, **not** part of the frozen measurement — no frozen target was
altered):

```
C1 at pre-fix tip 2c7443ab: rc=1  genuine=0/1 benign=0/3 noop_rejected=16/16 errors=0 met=False
C2 vs a scratch fleet commit whose MANIFEST drops the kama r57 closure:
  rc=1  manifest=None  mismatches=1  pointer_verdict=1  met=False
```

So the counters are not always-accepting shells: both return `1` on a genuine mismatch and `2` on
unusable input.

## F2 — DEFECT: ambient `GIT_*` environment is not scrubbed in children

Observed (clean environment = pass; the *only* change is two exported variables):

```
# C1, clean:
mc1 clean   rc=0  genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True
# C1, GIT_DIR=/nonexistent/gitdir  (alone):
            rc=1  genuine=0/1 benign=0/3 noop_rejected=16/16 errors=0 met=False
# C1, GIT_WORK_TREE=/nonexistent/wt (alone):
            rc=1  genuine=0/1 benign=0/3 noop_rejected=16/16 errors=0 met=False
# C1 detail lines under contamination: "genuine reject exit=1", "B1… reject", "B2… reject", "B3… reject"
# C2, same contamination: could-not-evaluate: unresolvable lane tip or fleet ref   rc=2
# standalone checker under contamination: runs=5 passed=0/5 errors=5 met=False      rc=1
        {"error": "child failed", "exit": 2, "fault": "baseline", "passed": false}
```

Cause (read from the committed sources at the measured tips):

- `tools/round59-battery-outcome-check.py` `child()` builds its fixture view with
  `real_run(["git", "-C", repo, "ls-tree"…])` / `real_run([... "show" …])` using the **inherited**
  environment (its helper `git()` strips `GIT_*`, `real_run` does not), so `GIT_DIR`/`GIT_WORK_TREE`
  redirect those queries and `blob_for()` fails.
- `tools/round59-c1-counter.py` scrubs `GIT_*` only for *its own* `git()` calls, then hands the
  checker `env={**os.environ, "TMPDIR": …}`; the contaminated environment reaches the checker
  and its `--child` grandchildren.
- `tools/round59-c2-counter.py` `git()` does **not** scrub `GIT_*` at all.

Impact on the two axes (this is why it matters, and why it is not a fabrication of a pass):

- The failure direction is **false negative**, never false accept. Under contamination the C1
  counter reports `errors=0` and classifies every leg — including `genuine` and all three benign
  legs — as a legitimate `reject`. The frozen kill rule ("any genuine leg rejected … -> claim not
  met") therefore converts an environment accident into a *claim-level kill* that looks like real
  defect evidence. C2 exits `2`, which the kill rule also reads as "claim not met"
  ("genuine cannot evaluate").
- A verifier whose shell exports `GIT_DIR`/`GIT_WORK_TREE` (colocated jj/git workflows, git hooks,
  some CI runners) will reproduce "not met" on a tree that measures "met" here. Nothing in the
  counter output distinguishes the two cases, so the operability claim ("the frozen command is a
  reproducible measurement") is not satisfied for arbitrary verifier environments on the tips
  measured.
- I did not and must not edit the counters; the finding is reported to L1 for the fix (scrub
  `GIT_*` in every child env — `os.environ` minus `GIT_*` — the way the top-level helpers already
  do) and for recording the environment used for the canonical receipts.

Not a falsification of C1-r59/C2-r59 as measured: in a clean environment both are `met=True` and
the interpreter axis is invariant.

## F3 — OBSERVATION: C2's `--fleet-ref HEAD` binding is time-dependent

- Brief states the fleet HEAD is `3f3dd97345ef1aedfdaec818c9e58675d4f41e3f`.
- At run time `git -C /home/vgpnk/Projects/shokunin rev-parse HEAD` =
  `0f99f606120d0c884656c6e7a290f0e8f33c2181` ("rounds ledger: tabi r40 closure (rejected-honest-stop)").
  The fleet moved during this wave; the briefly-stated revision is now the second commit back.
- `MANIFEST.json` blob differs between them (`73fe58936c2c27873359887cedb744a473d8ac7f` vs
  `c2d7e4c2be7b05ed7ecf0e26926395754119afeb`), so a replay must pin the revision, not `HEAD`.
- Verdict is stable across both bindings (observed):

```
--fleet-ref HEAD (resolved 0f99f606…): met=True mismatches=0   rc=0
--fleet-ref 3f3dd973…            : met=True mismatches=0   rc=0   (matches the recorded control)
```

Both revisions carry the kama r57 closure with `verdict=rejected-honest-stop`
(`{'lane':'kama','lane_round':57,'type':'closure','verdict':'rejected-honest-stop'}` in both MANIFESTs),
so no kill. But the recorded control
(`.ufo/waves/round-59/controls/c2-after-current-head.out`, `fleet=3f3dd973…`) is **not**
reproducible from the frozen command line alone once the fleet advances; the honest replay form is
`--fleet-repo /home/vgpnk/Projects/shokunin --fleet-ref 3f3dd97345ef1aedfdaec818c9e58675d4f41e3f`.
The counter already prints the resolved revision, so the binding is explicit in the output — this
is a calibration/reproducibility note, not a mismatch.

## Unrun / not exercised (stated as such)

- CPython 3.7 and 3.8 — not installed and not obtainable from the local uv inventory; **unrun**.
  3.9 is the empirically tested floor; the code's actual floor is ≥3.7 by inspection
  (`subprocess.run(capture_output=…)`), but that is `[INFERENCE]`, not observed.
- Non-Linux platforms, conda/pyenv-managed interpreters, `python3` shadowed by a venv — unrun.
- Native `jj` invocation of these tools — not applicable (they are `git -C` only); unrun by design.
- No external S517/S518 spot-check was performed or claimed; I make **no** discernment-progress claim.

## Write-boundary compliance

- Lane tree read via `git -C` and `read` only. After all runs:
  `git -C kama-shokunin status --porcelain | grep -v '^??'` → empty (no tracked modification);
  the only lane write is this report file.
- All fixtures/scratch under `/fast/scratch/hyaku/kama-r59/X12Portability` with `TMPDIR` exported;
  no `/tmp` use; the fixture-commit assertion `git -C "$FX" rev-parse --show-toplevel` equalled
  `$FX` before every scratch `commit`; throwaway identity was passed via `-c user.name/-c user.email`
  only for scratch fixtures.
- Scratch tree removed before yield (evidence is transcribed above verbatim).

## Verdict for this seat

- **C1-r59 (operability, interpreter axis): not falsified.** Nine interpreter configurations
  (CPython 3.9/3.10/3.11/3.12/3.13/3.14.8/3.14t/3.15.0, PyPy 3.11) return byte-identical
  `met=True` output at `aca8d006`; input errors fail closed with `rc=2`; the counter is not
  always-accepting (`rc=1` on a pre-fix tip).
- **C2-r59 (calibration, reproducibility): not falsified at either fleet revision** (`3f3dd973`,
  and the now-current `0f99f606`), but the frozen command's `--fleet-ref HEAD` makes the recorded
  binding non-replayable after fleet movement; pin the revision.
- **Blocking operability defect (F2):** ambient `GIT_DIR`/`GIT_WORK_TREE` flips C1 from
  `met=True` to a *bogus* `met=False` (all legs, including `genuine` and benign, reported as
  legitimate rejects with `errors=0`) and C2 to `rc=2`. Until the counters scrub `GIT_*` from
  child environments, an "operability established" statement is environment-conditional, and a
  contaminated verifier can produce a false claim-level kill.
