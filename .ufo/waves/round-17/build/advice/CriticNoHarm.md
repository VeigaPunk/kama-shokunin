VERDICT: partial — C1/C2 as specified break no pinned artifact; three procedural/provenance hazards (in-lane measure.py rewrites, detector-swap count, stray __pycache__) need correction

Seat: KamaR17.CriticNoHarm-2 (critic, read-only). Lane tip `cff9e62` (`git rev-parse master`). Read at 2026-10-20 while executors were still writing: `tests/probe-verdicts/check.py`, `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py` and `tools/kama-probe.sh` were still byte-identical to the frozen copies (b853576e…, b8c5e8d4…, 6b9576a1…, 36b64978…). `.ufo/waves/round-13/measure.py` had been edited, but only in its docstring (sha 351fc35b…). For C1/C2 I reviewed the proposed design and the round-16 evidence, not final code.

## Axes named
probe-matrix breadth and digest (round-16 measure.py) · round-16 tracked receipts · v1 receipt validation · probe vocabulary and served_model contract · test-snapshot.sh · SKILL.md exit tables (rows 430, 533–536) · round-13 gate exit table · SOURCES census and append-only · lane hygiene under jj · C1 count provenance.

## Strongest counterexample I could test locally (no harm found)
Question: would the new C1 invariants (served_model, route-match) add failures to either round-16 arm and break `directional`/`breadth`? Method: replay of the committed round-16 receipts (`.ufo/waves/round-16/run-before.json`, `run-after.json`) against the nine matrices. No gate was executed.
- In both arms, all 71 stub rows recorded `GET /v1/models`. The only row with no requests is `AuthAndDead.closed-port-connection-refused` (closed mode).
- On every one of the 55 non-`MODEL_LOADING` rows, `served_model` and `verdict` are identical before and after.
- Every row with `served_model` ≠ `-` is `MODEL_OK` or `MODEL_MISMATCH` with a `data[].id` body. Every other verdict reports `-`. This matches `tools/kama-probe.sh:455` "C_VERDICT='' C_SERVED='-'" and `:526-529`.
- Conclusion [INFERENCE]: if the derivation is correct, the new invariants are satisfied in both arms. round-16 `measure.py` should still give 55/17 → 72/0, `equal=True`, PASS.

## Findings (counterexample → evidence → axes → smallest safe correction)

**N1 (high, certain). Running round-16 `measure.py` in the lane rewrites tracked, sha-pinned round-16 receipts.**
- Evidence:
  - `.ufo/waves/round-16/measure.py:171-172`: "out = WAVE / f"run-{name}.json" … out.write_text(".
  - `check.py:316`: "record["port"] = port", which is an ephemeral port, so the bytes differ on every run.
  - `.ufo/waves/round-16/acceptance.json` pins "run-before.json": "86c59347…" and "run-after.json": "5df94191…". These still match today (sha256sum).
  - Round-16 already hit this: `corpus/lessons/round-16.md:169` "ran `measure.py` by accident, rewrote both run receipts and restored them with `git checkout`".
- Axes: round-16 receipts, provenance.
- Correction: L1 runs the no-harm measure only in a `/tmp` clone with the new `check.py` overlaid (check C1-a). Then confirm the lane copies still hash to 86c59347…/5df94191….

**N2 (high, calibration/provenance). The C1 before→after count changes the detector as well as the subject.**
- Evidence: the claim text reads "frozen check.py + round-16 pair detector) -> after (current check.py + pair + fault controls)". The `C1MutantRunner` spec adds M6–M8 "applicable only to a check.py that has them", so the denominators are 5 vs 8.
- Fault controls F1–F4 and F7 target exactly the ignore-reason, ignore-exit, ignore-drift, casefold and timeout mutants.
- [INFERENCE] M1–M5 on the frozen `check.py` would also die under `--detector full`. The drop in survivors would then be credited to the new detector, not to the repaired `check.py`.
- Axes: calibration (false provenance).
- Correction: report the full 2×2 {frozen, current} × {pair, full}, and give survived/applicable for each cell. Credit `check.py` only for the difference within the same detector (M6–M8 on current, and malformed-output handling).

**N3 (medium, observed now). An untracked `tools/__pycache__/` is in the lane.**
- Evidence: `git status` shows "?? tools/__pycache__/". It holds `sources-append-only.cpython-314.pyc`, mtime 12:21:02. `git check-ignore` matches nothing for it, while `.ufo/state/` and `registry/history/.lock` are ignored (`registry/history/.gitignore:3`).
- [INFERENCE] Under jj colocation, unignored files are snapshotted into `@`, so it can be swept into a commit.
- `fault-controls.py`/`mutants.py` importing `check.py`, or C2 K6 importing the live tool via runpy/importlib, would create `tests/probe-verdicts/__pycache__/` or `tools/__pycache__/` the same way.
- Axes: lane hygiene, jj-migration risk.
- Correction: set `sys.dont_write_bytecode = True` (or `PYTHONDONTWRITEBYTECODE=1` for child processes) in every runner that imports a lane module. L1 deletes `tools/__pycache__/` before the helper commit. A `__pycache__/` line in `.gitignore` is optional.

**N4 (medium). Scratch copies of `check.py` without the nine matrices pass vacuously.**
- Evidence: `check.py:152` "sources = sorted(CHECK_DIR.glob("*.json"))" (CHECK_DIR is the script's own dir) and `:493` "code = 0 if doc["failures"] == 0 else 1". With zero matrix files this yields tests=0, exit 0.
- A mutant or fault scratch dir that is missing or has extra JSON makes "killed"/"detected" meaningless.
- Axes: matrix breadth, calibration.
- Correction:
  - Each scratch runner asserts that the scratch set digest equals `bf9068d8…` and that the unmutated baseline run reports `tests == 72`. Otherwise it exits 2 (own fault).
  - Optional, and invisible on today's 72 rows: `check.py` exits 2 on zero selected tests.
  - The new `--selftest` duplicate-name case must be built in memory or in a TemporaryDirectory, never by writing a JSON file into `tests/probe-verdicts/` (that would move the digest pinned at `measure.py:281`).

**N5 (medium). The served_model derivation would become a second authority for the probe contract.**
- Evidence: the probe picks ids in this order: `data[].id` → `models[].id` → `models[].name` → `models[].model` → top-level `id`, deduplicated (`kama-probe.sh:357-367`). It reports them only when "is2 -eq 1 ] && [ "$has_models" -eq 1" (`:524`).
- The matrix exercises only `data[].id` (12 rows), so a simplified derivation passes 72/72 but diverges silently elsewhere.
- One stub row has no explicit `/v1/models` route and relies on `default_route` (`LoadingEnvelope.every-non-frontend-path`). The stub also strips query strings (`check.py:215-219`).
- Axes: probe vocabulary/contract, calibration.
- Correction: the derivation honours `default_route` and query-strip exactly like `make_handler`. It splits on {MODEL_OK, MODEL_MISMATCH} → ids, everything else → `-`, and adds no seven-verdict list of its own (`kama-probe.sh:64` `VOCAB` stays the only list). Its docstring states the precedence it implements and the limit that only `data[].id` is exercised.

**N6 (medium). The round-13 exit table is changing while the SKILL draft says it is not.**
- Evidence:
  - The in-flight docstring adds "4 worktree_not_at_measured_revision (live --quality bytes differ from the measured HEAD blob …)".
  - The draft `build/drafts/skill-round17.md` row says "existing command unchanged … no code change this round".
  - `SKILL.md:430` already says "undeclared nonzero codes could-not-evaluate", so exit 4 is compatible with the table. The round-17 section must still declare it.
- `JjRound13Gate` may edit `.ufo/waves/round-13/frozen/expected.json` "only if its selftest requires it". Doing so changes a pinned round-13 artifact: sha 21b6c4ac…, cited in `.ufo/waves/round-13/acceptance.json` and `advice/Measure.md`.
- Axes: round-13 gate exit table, SKILL.md.
- Correction: keep `expected.json` byte-identical (sandbox fixtures go in TemporaryDirectory). Reconcile the SKILL draft with the landed code before it is appended.

**N7 (low). SKILL.md rows 533/535/536 go stale; the knowledge and lesson text is historical.**
- Evidence: `SKILL.md:533` "grades verdict, reason, exit and drift"; `:535` "0 all 10 checks pass … 2 setup error"; `:536` "10 check ids".
- Convention: `SKILL.md:509` "superseded, not edited".
- Correction: append a round-17 section that supersedes these rows, covering:
  - served_model and route grading;
  - 11 v2 checks;
  - exit 2 now includes internal faults;
  - the new selftest counts;
  - round-13 exit 4.
- Rows 430 and 533–536 stay byte-identical. Leave the `corpus/lessons/round-16*.md` "10 checks" lines alone.

**N8 (low). Two tokens for one setup_error class.**
- Evidence: the v1 tool writes "receipt['setup_error'] = f'unexpected:{type(exc).__name__}'" (`tools/kama-llamacpp-live.py:1008`). The spec adds `internal:<ExcType>`. No consumer parses either token (grep: only the tool, its frozen copy and round-17 drafts).
- Correction: either keep `unexpected:` for the main body and use `internal:` only for teardown/finally faults, with both documented, or use one token. Do not leave two names for the same path.

**N9 (low, [INFERENCE]). teardown_graceful `returncode == 0` is a tradeoff, not a defect.**
- The round-16 real receipt shows "returncode": 0, "sigkill_sent": false, "sigterm_sent": true, "term_wait_ms": 3. The predicate holds for the measured path.
- An operator-interrupted run, where a second signal reaches the child, could exit nonzero and fail the check.
- Acceptable, because a `terminated:` run is already invalid (`setup_error` set). The DOC string should say so.

## No-harm checks for L1 (command → expected output)
No `/tmp` clone may bind 8080, 34113 or a registry port; none of these commands does.

**C1-a. Round-16 measure (matrix digest, breadth, directional).**
- Command: `git clone -q --branch master /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/l1-r17-nh && cp /home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py /tmp/l1-r17-nh/tests/probe-verdicts/check.py && python3 /tmp/l1-r17-nh/.ufo/waves/round-16/measure.py; echo measure_exit=$?`
- Expected, matching `.ufo/waves/round-16/measure-stdout.txt`:
  - `matrix: 9 files, set sha256 bf9068d8…`
  - `before	1	55	17` and `after	0	72	0`
  - per-family lines identical to measure-stdout lines 11-12
  - `directional: loading_expectations=17 before_failed=17 changed=17 equal=True`
  - `breadth: … ok=True; … ok=True`
  - `result: PASS`, `measure_exit=0`
- Delete the clone afterwards.

**C1-b. Lane receipts untouched.** `sha256sum .ufo/waves/round-16/run-before.json .ufo/waves/round-16/run-after.json` → `86c59347…` and `5df94191…`.

**C1-c. Matrix pinned.**
- The `measure.py:286-290` digest recomputed in the lane → `9 bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`.
- `git status --short tests/probe-verdicts` → only ` M …/check.py` and `?? …/fault-controls.py`. No `*.json`, no `__pycache__`.

**C1-d. Current gate.**
- `python3 tests/probe-verdicts/check.py --json --selftest` → `tests=72 passes=72 failures=0`, all selftest cases rejected, exit 0.
- Per row, `served_model` and the request list equal the values in `run-after.json` (0 diffs).

**C1-e. Frozen probe vector unchanged.**
- New `check.py` with `--probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` → exit 1, 55/17.
- The failing names are exactly the 17 rows with `expected.verdict == MODEL_LOADING`, the same set the frozen `check.py` fails.

**Vocabulary.**
- `sha256sum tools/kama-probe.sh` → `36b64978…`.
- `grep -n '^VOCAB=' tools/kama-probe.sh` → line 64, seven words.
- `check.py` contains no seven-verdict list.

**test-snapshot.** `bash tools/test-snapshot.sh` → last lines `RESULT pass=30 fail=0`, exit 0 (as `.ufo/waves/round-16/run-test-snapshot.txt`). It depends only on `tools/kama-probe.sh` (`test-snapshot.sh:7`).

**v1 receipts.**
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --expect-tool-sha256 b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4` → `VALID …`, exit 0.
- Same command with `receipt-frozen-probe.json` and `--expect-probe-sha256 93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` → `VALID`, exit 0.
- `receipt-frozen-probe.json` with probe pin `36b64978…` → exit 1. All three match `.ufo/waves/round-16/live/controls.txt`.
- `--selftest` → still includes the 26 v1 mutations plus at least 10 v2 mutations, exit 0.
- Two extra one-off cases, built in /tmp:
  - a v1 receipt with only `schema` set to v2 → exit 1;
  - a v2 receipt with only `schema` set to v1 → exit 1 (v1 rejects unexpected ids: `check-receipt.py:618-620`).

**Live tool pre-launch exits** (no launch, no bind; reproduces `controls.txt`):
- `--model-sha256 000…0` → exit 3, "refusing to launch".
- `--port 34113` → exit 2, `port-refused-registered:34113`.
- `--port 8080` → exit 2.
- A port already in use → exit 2.
- If v2 now writes a receipt for these, that receipt has non-null `setup_error` and the gate exits 1.
- After any live or fake run: `ss -ltnp` shows no harness listener, and `pgrep -f llama-server` is empty.

**SKILL.md.** `git diff -U0 SKILL.md` shows only lines added after the current line 552. Rows 430 and 533–536 are unchanged.

**Round-13 gate**, rerun with the edited script against the recorded commands in `.ufo/waves/round-13/acceptance.json`:
- frozen before (`--manifest …/expected.json --quality …/frozen/before/corpus/QUALITY.md`) → exit 1 `documentation_mismatch`;
- frozen after → exit 0 `clean`;
- `--selftest` → exit 0;
- live run after the helper commit → exit 0 `clean`;
- in a /tmp clone with QUALITY.md edited but clean and uncommitted → exit 4, not 1.
- `sha256sum .ufo/waves/round-13/frozen/expected.json` → `21b6c4ac…`.
- QUALITY.md KQ20–22 are appended only; `historical_prefix_preserved` stays true.

**SOURCES.**
- `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate kama` → only the existing `W04 S031 …` warning plus `ok`, exit 0 (as `.ufo/waves/round-17/sources-before-validate.txt`).
- Land `controls.py`, `fault-controls.py` and `sources-append-only.py` before any new row lists them in used-by; otherwise the census raises E11 "used-by path missing on disk".
- `tools/sources-append-only.py --from cff9e62 --to <tip>` → 0. Against the S041 window → 1.

**Hygiene.** `git status --short` shows no `__pycache__` and no files outside the declared write set before the helper commit.

## Limitations
- C1/C2 code was not yet written when I reviewed it, so N4, N5, N8 and N9 judge the specification. L1 must apply the checks above to the landed bytes.
- I ran no gate, measure, control or tool, and wrote no scratch files. The only things computed were sha256 values, the matrix digest, and a read-only replay of the committed JSON receipts.
- The jj snapshot behaviour in N3 is [INFERENCE] from jj's documented auto-tracking; I did not exercise it (no jj commands allowed).

## Installs
None.
