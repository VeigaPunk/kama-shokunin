VERDICT: confirm — F9–F17 and the detector self-checks are implemented; all six named H-mutants yield their targeted accepted fault on the robust current checker.

# Scope and axes

Axes: **calibration** (whether each declared surviving check.py mutant is distinguishable), **self-calibration** (whether fault-controls itself fails when its F0 gate, per-row cache isolation, or targeted-conjunct attribution is weakened), and **operability** (malformed JSON and process-tree timeout faults are safely recorded and cleaned up).

Implemented only `tests/probe-verdicts/fault-controls.py` as the source change in my seat clone; the clone's `check.py` was replaced with the current C2CheckPyRobust deliverable only as a test input. Delivered the fault-controls source and frozen-base unified diff, and wrote this exclusive report. No lane matrix, frozen artifact, fleet state, runtime service, or other lane code was edited. The clone was based on round-start `e75cf680b53484a61709ee1b2787d8dbc6419f74`.

# Delivered files

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/KamaR18.C2FaultControls-2/fault-controls.py` — SHA-256 `58dac1f71346734532bddc60a2d20f95f640406e924b1aec00a0b750feed072a`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/KamaR18.C2FaultControls-2/fault-controls.py.diff` — unified diff against frozen `tests_probe-verdicts_fault-controls.py`; SHA-256 `cff09e77d508e4ebd7f2b6e317be662041ea43d1d8049b5e09acd927ad7c8511`.
- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/advice/C2FaultControls.md`.

`cmp` of the final clone source and delivered source exited 0. The frozen source hash was `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312`.

# Implementation

Added F9–F14 at `fault-controls.py:252-303`; their `kills` entries map to H1, H2, H3, H5, H6 and H7. Added crash debt controls F15–F17 at `:306-335`; existing fault/output keys remain, with additive metadata (`kills`, `debt`, `slow`, `escaped_pids`, etc.). CLI `--probe`, `--matrix-dir`, `--check`, `--only-fault`, and exit meanings 0/1/2 remain available (`:1471-1490`).

- F9 swap-cases the reason over mixed-case matrix reasons; H1's surviving comparison is documented as `record["reason"].casefold()` in `MutC1Preregistered.md:31`.
- F10 applies leading-space, trailing-space and trailing-newline variants to MODEL_LOADING (`LoadingEnvelope.canonical-alias`), FOREIGN_SERVICE and DEAD rows. This includes the MODEL_LOADING row required to distinguish the `.strip()` mutant; the old mutant was `record["verdict"].strip()` (`MutC1Preregistered.md:51`). The MODEL_OK and MODEL_MISMATCH rows are intentionally excluded because padding those can also break drift or served-model checks.
- F11 pre-passes and replays each stub row independently after issuing only POST, HEAD, or lowercase `get` to `/v1/models`; it never issues a GET on that path. This distinguishes the method-blind mutant (`MutC1Preregistered.md:71-72`).
- F12 uses only MODEL_OK/MODEL_MISMATCH rows with a non-placeholder served id. Case and `.gguf` suffix variants target H5's exact lower/remove-suffix normalization; whitespace and fullwidth/NFKC variants separately cover other normalizers. H5's cited mutation is `sid.lower().removesuffix(".gguf")` (`MutC1Preregistered2.md:29-34`).
- F13 replays an honest result without touching the stub at all, targeting H6's no-request branch (`MutC1Preregistered2.md:40-44`).
- F14 emits exactly two rows: a deep-copied reason-corrupted first row and a separate deep copy of the honest row last. This catches `rows[-1]` grading (`MutC1Preregistered2.md:50-54`).
- F15 injects 100,000 nested arrays and F16 a 5,000-digit integer; bodies travel through scratch files rather than an oversized environment string. These target the observed `RecursionError` and integer-limit `ValueError` (`MalformedNonUtf8.md:29-30`).
- F17 has the wrapper wait on a same-process-group child `sleep` with a unique argument. After check.py exits, fault-controls observes whether that child survived; a verified escaped child is killed and makes F17 ACCEPTED. This exercises the documented shell-child leak (`TimeoutPath.md:27-40`). `--skip-slow` skips both F7 and F17.

Fault classification remains fail-closed: each faulted row must be present, `passed` must be exactly false, and the row must fail the declared targeted conjunct. Tracebacks, missing rows, wrong exits, wrapper exit 9, and off-target failures cannot count as detections (`:653-753`). F0 is run and accepted before any fault count; all fault rows must be covered by F0, and cached pre-passes are keyed by row and must pass themselves (`:795-821`, `:946-1005`).

Selftest now checks classifier edge cases, wrapper mutations, the F0 gate and F17 cleanup with no real probe/port (`:1070-1458`). The F0 selftest runs rejecting and accepting stub check.py scripts; shared F6 cache is rejected as a multi-row replay; and an off-target verdict-only failure verifies target attribution. The mutation-sensitive source lines were preserved exactly and uniquely for the survivor runner: `_per_row("f6", "/health", F6_ROWS)` at `:216`, `if target:` at `:735`, and `if not positive["detected"]:` at `:977`.

# Verification and retained evidence

Python was 3.14.8. The matrix pin reproduced: 9 files, 72 tests, SHA-256 `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`.

Commands below ran in the disposable clone (the long-run commands inherited `PYTHONDONTWRITEBYTECODE=1` and the seat-local `PYTHONPATH=/tmp/kama-r18-C2FaultControls-guard`, which kept ephemeral test binds on loopback ports 49152–60999 and away from protected ports 8080/34113). No package/tool installation occurred.

1. `python3 -m py_compile fault-controls.py` — **exit 0**.
2. `python3 fault-controls.py --selftest --matrix-dir /tmp/kama-r18-C2FaultControls/tests/probe-verdicts` — **exit 0**, `passed:true`, `faults_checked:18`, 23 classifier cases, 35 wrapper checks; reject-everything F0 gate returned code 2 before counts, accept-everything F0 led to one accepted fault. The escape selfcheck observed direct-kill `survived:true` and group-kill `survived:false`, with neither child alive after cleanup.
3. Full current suite command:
   `python3 /tmp/kama-r18-C2FaultControls/tests/probe-verdicts/fault-controls.py --check /tmp/kama-r18-C2FaultControls/tests/probe-verdicts/check.py --probe /tmp/kama-r18-C2FaultControls/tools/kama-probe.sh --matrix-dir /tmp/kama-r18-C2FaultControls/tests/probe-verdicts --json`
   — **exit 0**, F0 true, 17 detected / 0 accepted. F1–F17 all detected; F6/F8/F10/F11/F12/F13 variant exits were all check exit 1. This was rerun on final main-path behavior (112.9 seconds).
4. Same full command with `--check /tmp/kama-r18-C2FaultControls/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py` (round-16 check, SHA-256 `b853576edd54e006c4d8742c1a7335a0d6cca475d107acce7792da75b6145762`) — **exit 1**, F0 true, 9 detected / 8 accepted. F5/F6/F8 and the H3/H5 coverage faults F11/F12, plus crash debts F15–F17, were accepted.
5. Same full command with `--check /tmp/kama-r18-C2FaultControls-work/frozen-r18-check.py` (round-17 check, SHA-256 `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099`) — **exit 1**, F0 true, 14 detected / 3 accepted; F15–F17 were accepted.
6. Frozen round-17 fault-controls against the round-16 check — **exit 1**, 5 detected / 3 accepted; against the round-17 check — **exit 0**, 8/0; against integrated current check.py — **exit 0**, 8/0. This preserves the old detector's measured baseline while the new faults improve coverage.
7. H mutants were hand-applied as one-site substitutions to separate `/tmp` copies of the integrated current check.py (`12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5`). With the new fault-controls and each corresponding `--only-fault`, all six yielded suite **exit 1**, `accepted:1`, and the named fault's `detected:false` (the mutant accepted the injected fault): H1/F9 exit 0; H2/F10 `[0,0,0]`; H3/F11 `[0,0,0,0]`; H5/F12 `[0,0,1,1]` (case and suffix accepted, whitespace and fullwidth still rejected); H6/F13 `[0,0,0,0]`; H7/F14 exit 0. The H7 result was rerun after adding the explicit deep-copied honest last row. H edits followed the exact advice mutations: reason `.casefold()`, verdict `.strip()`, removing the GET condition, per-ID lowercase/remove-suffix, setting `passed=True` in the no-request branch, and selecting `rows[-1]`.

Exact targeted H-mutant commands (all used the same `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/kama-r18-C2FaultControls-guard`; working directory `/tmp/kama-r18-C2FaultControls-work`; each suite exited 1):

```sh
python3 /tmp/kama-r18-C2FaultControls/tests/probe-verdicts/fault-controls.py --check /tmp/kama-r18-C2FaultControls-work/mut-rob-H1/check.py --probe /tmp/kama-r18-C2FaultControls/tools/kama-probe.sh --matrix-dir /tmp/kama-r18-C2FaultControls/tests/probe-verdicts --json --only-fault F9
python3 /tmp/kama-r18-C2FaultControls/tests/probe-verdicts/fault-controls.py --check /tmp/kama-r18-C2FaultControls-work/mut-rob-H2/check.py --probe /tmp/kama-r18-C2FaultControls/tools/kama-probe.sh --matrix-dir /tmp/kama-r18-C2FaultControls/tests/probe-verdicts --json --only-fault F10
python3 /tmp/kama-r18-C2FaultControls/tests/probe-verdicts/fault-controls.py --check /tmp/kama-r18-C2FaultControls-work/mut-rob-H3/check.py --probe /tmp/kama-r18-C2FaultControls/tools/kama-probe.sh --matrix-dir /tmp/kama-r18-C2FaultControls/tests/probe-verdicts --json --only-fault F11
python3 /tmp/kama-r18-C2FaultControls/tests/probe-verdicts/fault-controls.py --check /tmp/kama-r18-C2FaultControls-work/mut-rob-H5/check.py --probe /tmp/kama-r18-C2FaultControls/tools/kama-probe.sh --matrix-dir /tmp/kama-r18-C2FaultControls/tests/probe-verdicts --json --only-fault F12
python3 /tmp/kama-r18-C2FaultControls/tests/probe-verdicts/fault-controls.py --check /tmp/kama-r18-C2FaultControls-work/mut-rob-H6/check.py --probe /tmp/kama-r18-C2FaultControls/tools/kama-probe.sh --matrix-dir /tmp/kama-r18-C2FaultControls/tests/probe-verdicts --json --only-fault F13
python3 /tmp/kama-r18-C2FaultControls/tests/probe-verdicts/fault-controls.py --check /tmp/kama-r18-C2FaultControls-work/mut-rob-H7/check.py --probe /tmp/kama-r18-C2FaultControls/tools/kama-probe.sh --matrix-dir /tmp/kama-r18-C2FaultControls/tests/probe-verdicts --json --only-fault F14
```
8. Final fault-controls self-mutants, each `--selftest --matrix-dir ...` — all **exit 1** with parseable JSON and a named `problems[]` entry:
   - dropped target conjunct (`if False and target:`): `classifier: target-conjunct attribution: reason fault failed on verdict only...`;
   - shared F6 cache: `F6: replay run shares one cache across 4 rows; must be per-row`;
   - F0 gate bypass: `F0 gate: a reject-everything check.py was not refused before any fault counted...`.
   These match the three observed self-mutants in `MutFaultControlsSelf.md:36-39,77-80,100-102`.

Exact self-mutant commands (all used `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/kama-r18-C2FaultControls-guard`; each exited 1 and emitted the named parseable selftest failure above):

```sh
python3 /tmp/kama-r18-C2FaultControls-work/final2-self-a-no-target/fault-controls.py --selftest --matrix-dir /tmp/kama-r18-C2FaultControls/tests/probe-verdicts
python3 /tmp/kama-r18-C2FaultControls-work/final2-self-c-shared-f6-cache/fault-controls.py --selftest --matrix-dir /tmp/kama-r18-C2FaultControls/tests/probe-verdicts
python3 /tmp/kama-r18-C2FaultControls-work/final2-self-d-f0-bypass/fault-controls.py --selftest --matrix-dir /tmp/kama-r18-C2FaultControls/tests/probe-verdicts
```
9. Final port/process census: `ss -ltnp` showed no listener on 8080 or 34113; no `sleep 240.*` child and no seat test process remained. Other unrelated host listeners remained untouched.

The integrated current checker used for the current-side result was the lane-provided robust version, SHA-256 `12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5`; it recorded both decoder-limit faults per row and killed the F17 probe process group on timeout. The round-17 repair and frozen values above are retained separately, not conflated with the current result.

# Limits and blockers

- F17 is Linux-specific (`/proc`) and the control exercises a child that inherits the probe process group; it does not establish cleanup for a child that deliberately calls `setsid()`/moves to another process group. It does verify the requested same-group escape case and cleans the observed child before return.
- F12's case and `.gguf` variants directly distinguish H5. Whitespace and NFKC variants cover additional plausible normalizers; they are not equivalent under H5's exact lower/remove-suffix mutation and therefore remain detected by that mutant.
- These are synthetic fault-injection checks of the verdict harness, not a live llama-server run or a claim about endpoint behavior outside the 72-row matrix.
- LSP was unavailable: `read xd://lsp` returned `No such tool`; source inspection and exact-site mutation checks were used instead.
- Installs/updates: none.
