VERDICT: confirm — no-harm holds at round commit 54a2926: tools/test-snapshot.sh is RESULT pass=30 fail=0 (exit 0) and tests/probe-verdicts/check.py --selftest is 72/72 + 5/5 (exit 0), zero failures.

# Axes attacked
- A1 no-harm (snapshot suite): `tools/test-snapshot.sh` behavioral suite still fully green at the round commit, i.e. the round-17 changes (graded `served_model`, GET /v1/models route, malformed/non-UTF-8 row capture in `tests/probe-verdicts/check.py`) did not regress the `kama-probe.sh snapshot` contract.
- A2 no-harm (checker oracle): `check.py --selftest` oracle self-consistency intact — all 72 embedded verdict cases and the malformed-test rejection subtest.
- Target: round commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3` ("round-17: graded check.py fields with fault controls and mutant grid; live receipt v2 …"), verified via `git log -1` in the clone.

# Method / hermeticity (read before running)
- Contract clone: `git clone` of the lane into `/tmp/KamaR17.SnapshotClone-clone`, `git checkout -q 54a2926…`; no lane tool was ever executed in the lane directory. All runs used `PYTHONDONTWRITEBYTECODE=1`.
- `tools/test-snapshot.sh` runs in a `mktemp -d` workdir (`umask 077`); its fixture is a python `http.server` bound on an ephemeral loopback port published via `$WORK/port`, addressed as `http://127.0.0.1:$PORT/v1` (tools/test-snapshot.sh:20,36-45) — no fixed port, no 8080/34113 contact.
- `check.py --selftest` is offline: embedded fixtures (tests/probe-verdicts/check.py:493-524) plus `tempfile.TemporaryDirectory` (check.py:541).

# Commands run (exact, with exits)
1. `cd /tmp/KamaR17.SnapshotClone-clone && PYTHONDONTWRITEBYTECODE=1 bash tools/test-snapshot.sh`
   → **exit 0**; final line `RESULT pass=30 fail=0` — exactly the expected tally. All 30 rows PASS; notable no-regression evidence: "dead fixture makes snapshot exit 2", "MODEL_OK to DEAD transition recorded", "served-id transition recorded", "malformed line never becomes phantom transition", "MODEL_LOADING baseline row accepted and diffed", "unknown verdict still audited and dropped", "snapshot --port refused with probe-error exit", "symlinked history dir refused", byte-stability of unchanged `DELTA.md`/`latest.tsv`.
2. `cd /tmp/KamaR17.SnapshotClone-clone && PYTHONDONTWRITEBYTECODE=1 python3 tests/probe-verdicts/check.py --selftest`
   → **exit 0**; final lines `tests=72 passes=72 failures=0` and `selftest: 5/5 malformed tests rejected (ok)` — exactly the expected 72/72 + 5/5. 72 PASS rows: AuthAndDead 7, EnvelopeShapes 9, ForeignControls 8, LoadingEnvelope 8, LoadingRace 9, NearMissTriple 8, NonLoadingStatuses 7, Overbroad503 8, ReadyControls 8 (= 72).

# No-harm residue checks
- `git status --porcelain` in the clone after both runs: empty (clean) — both entry points left zero repo-side residue (workdir/trap discipline holds).
- `pgrep -af 'kama-snapshot-test|server.py'`: no process of mine remained (the two `fake_server.py`/live-controls hits are sibling seats' `/tmp/SeparabilityNoHarm-*` and `/tmp/ControlsSafety-*` runs — not touched, per lane bounds).
- `ss -ltnp`: no 8080/34113 listeners at any point of my run.

# Findings against the claim
- None. No defect, no flake signal, no contract drift observed in either entry point. No finding kept or discarded beyond the two expected outputs.

# Limitations
- Scope was the two named entry points only; fault-controls/mutant-grid counting and live receipt v2 reruns belong to sibling seats and were not attacked here.
- Single-shot runs: no repetition, so no flake-rate estimate. [INFERENCE] hermetic design (tempdir + ephemeral loopback fixture + embedded selftest fixtures) makes nondeterminism unlikely, but it is unmeasured.
- `--selftest` exercises the checker's oracle logic on embedded fixtures only; it does not validate any lane registry state.

# Installs
- None (no pacman, no uv, no downloads) — host tooling sufficed.

# Scratch
- `/tmp/KamaR17.SnapshotClone-clone`, `/tmp/KamaR17.SnapshotClone-snapshot.log`, `/tmp/KamaR17.SnapshotClone-selftest.log` removed before finish; `ls -d /tmp/KamaR17.SnapshotClone*` confirms nothing remains.
- Only lane write: this Report file.
