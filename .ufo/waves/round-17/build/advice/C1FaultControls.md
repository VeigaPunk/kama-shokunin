VERDICT: confirm — fault-controls.py delivers the C1 counting command: on the pre-round check.py 3 of 8 faults are ACCEPTED (F5 served_model, F6 route-skip, F8 malformed); on the current repaired check.py only F8's non-UTF-8 variant is still accepted, and that is a real residual defect in check.py, not tool noise.

# File written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py`
  sha256 `d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312`, 33332 bytes, mode 0755.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/C1FaultControls.md` (this report).
- No `*.json` added under `tests/probe-verdicts/`; the nine matrix files are untouched (set digest still `bf9068d8…`, 72 tests — asserted by the tool itself). `/tmp/KamaR17.C1FaultControls-2-*` scratch deleted; no `__pycache__`.

# Counting result (advice runs; L1 re-measures)

`python3 tests/probe-verdicts/fault-controls.py --json`

| check.py under test | sha256 | F0 gate | detected | accepted | accepted set |
|---|---|---|---|---|---|
| pre-round (`git show cff9e62:tests/probe-verdicts/check.py`) | `b853576e…` | PASS | 5 | **3** | F5 served_model, F6 route-skip, F8 malformed |
| current repaired (`tests/probe-verdicts/check.py`) | `b460b786…` | PASS | 7 | **1** | F8 malformed (non-UTF-8 variant only) |

Per-fault detection on the current check.py: F1 reason, F2 exit, F3 drift, F4 verdict, F5 served_model (incl. DEAD row), F6 route (4 stub rows, one run each), F7 hang/error. F8 detects 5 of 6 variants (`[]`, `{"rows":[]}`, `{"rows":[["x"]]}`, `{"rows":[null]}`, non-JSON) and accepts `non-utf8`. Wall time 57.9 s (F7 alone ~41 s).

# Behaviour

CLI `fault-controls.py --check PATH [--probe PATH] [--matrix-dir DIR] [--json] [--only-fault ID] [--skip-slow] [--list] [--selftest]`.

- Stages a `TemporaryDirectory`: byte-copies `--check` to `check.py`, copies the nine `*.json` verbatim, writes `wrap.py` (bash `exec python3 - "$@" <<'FAULT_WRAPPER_EOF'` heredoc so check.py's `bash <probe>` invocation lands argv in `sys.argv`), `cache/`.
- Before grading it re-derives the round-16 set digest — `"".join(f"{f.name} {sha256(f.read_bytes())}\n")` over sorted files — and asserts `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` plus 72 tests, on both the source dir and the staged dir; any mismatch is exit 2, never a verdict.
- F0 positive control runs first on all five row kinds: identity pass-through must yield exit 0 with every row `passed: true`; failure prints `suite INVALID` and exits 2 (L1 ruling 1). It runs even with `--only-fault`.
- Detection per fault: every run exits 1, stdout parses as JSON, every faulted row has `passed: false`, **and** the fault's `target` conjunct appears in that row's locally re-derived failures (`verdict`, `reason`, `exit`, `drift`, `served_model`, `route`, `error`). Conjuncts are recomputed from the record plus the matrix row's own literal routes (`contract_served_model` mirrors `kama-probe.sh:335-368` precedence; route requires a recorded `GET /v1/models`). A wrapper crash that only produces `error` can therefore never read as a field-fault detection (L1 ruling 3).
- F6 uses one check.py invocation per row (its own pre-pass cache file), so only the route conjunct differs (L1 ruling 2); the closed DEAD row is excluded as specified.
- F8 carries bodies as base64 `FAULT_BODY_B64`, writes raw bytes, and keeps the real probe's exit code so stdout is the single corrupted field (L1 ruling 5).
- `run_check` starts check.py in its own session and `os.killpg(SIGKILL)` on the 150 s cap, so a wedged mutant/wrapper group is reaped and classes as accepted (rc 124), never hung (L1 ruling 7).
- Output `{"schema":"kama-fault-controls/v1","check","check_sha256","probe_sha256","matrix":{"files","tests","sha256"},"positive_control","seconds","faults":[{"id","title","target","rows","runs","check_exit","detected","why"}],"detected","accepted"}`; exit 0 iff `accepted == 0`, 1 otherwise, 2 own fault (bad argv/path, digest pin mismatch, F0 failure, F6 pre-pass failure).

# Calibration probes (scratch, /tmp, removed)

- Reject-everything mutant (grade always false): F0 fails → `suite INVALID — positive control F0 failed`, exit 2. A harness that fails everything cannot launder an accepted=0.
- Ignore-reason mutant (`and record["reason"] == expected["reason"]` → `and True`, check.py:468): F0 passes, F1 is ACCEPTED. This reproduces the round-16 survivor class on demand and shows the counter responds to grading-weakening mutations rather than only to output corruption.

# Findings for other seats

1. **Residual C1 defect — non-UTF-8 probe output tracebacks.** `tests/probe-verdicts/check.py:279` `"return subprocess.run(argv, capture_output=True, text=True,"` decodes strictly; `UnicodeDecodeError` is raised before `probe_output_row` (check.py:372) and is not in any caught tuple, so check.py dies with a traceback, empty stdout, exit 1. My F8 `non-utf8` row (`\xff\xfe{bad`) is the only accepted control on the current check.py. Fix: `errors="replace"` on the subprocess call (or catch `UnicodeDecodeError` into a recorded error). Cite: `tests/probe-verdicts/check.py:279`.
2. `served_model` inversion direction is confirmed caught: forging `kama-forged-id` fails MODEL_OK, MODEL_MISMATCH **and** the DEAD row (check.py must require `-` there).
3. Route conjunct is confirmed caught only where it exists: every stub-mode F6 row fails on `route`; the closed-port DEAD row is exempt by construction.
4. The frozen copy `.ufo/waves/round-17/frozen/tests_probe_verdicts_check.py` disappeared from the lane around 12:46 (directory survived, file did not); I reconstructed the pre-round harness with `git show cff9e62:tests/probe-verdicts/check.py`, sha256 `b853576e…`, matching `frozen/manifest.json` exactly. Report the missing frozen artifact to L1 if it was not intentionally re-captured.

# Known limitations

- `contract_served_model` mirrors the probe's python3 path; if `kama-probe.sh`'s extraction or loading-envelope semantics change, this derivation must move with it (both files are cited in its docstring).
- [INFERENCE] The 150 s per-run cap bounds a pathological mutant; a mutant slow enough to need more than that on a 5-row `--only` run would read as accepted, not detected.
- F6's pre-pass failure is an own fault (exit 2), not an accepted control: a harness that cannot even run the honest probe is invalid input rather than a check weak enough to accept the route skip.
- The conjunct re-derivation is a second implementation of the grading contract by design (independence is the point), so it cannot detect a defect the two implementations share — e.g. a probe-contract change that both mis-model identically.
- F7 costs ~41 s and F8 ~12 s; `--skip-slow` drops only F7. `--only-fault` still runs F0 (~1.2 s).
- `--matrix-dir` is accepted, but the pinned set digest makes anything but the canonical nine-file set an immediate exit 2.

# Installs

None. No packages installed or upgraded; pacman untouched. No ports bound beyond check.py's own ephemeral loopback stubs (8080/34113 clear after every run); no stray wrapper processes.
