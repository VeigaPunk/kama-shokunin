VERDICT: confirm — editing round-16 `measure.py` is safe (no digest pin, no closure routing, no round-17 consumer); recommend fix now, but prove the guard in /tmp, never by rerunning the counting command in the lane.

Axes: **operability** (a counting command whose provenance read can false-fail or false-pass on ambient state) and **calibration** (rec 6 asks for parity with the two gates that already guard their git reads). Everything below is read-only measurement plus a /tmp git sandbox; nothing in the lane was executed or written except this Report.

## Decision

**Fix, L1-owned, one confined edit at `.ufo/waves/round-16/measure.py:115-117`.** The edit is mechanically safe — nothing pins the file's bytes. The *only* unsafe step is the obvious one: demonstrating it by running the counting command inside the lane, because every run rewrites the two receipts that `acceptance.json` pins (F5). Do the edit, prove it by replaying the exact argv/env against a `/tmp` repo (F6), and disclose old→new sha256. Deferring is defensible only if L1 will not spend ten minutes on a proven-inert change; there is no correctness reason to defer.

## F1 — Decisive: the file is not pinned anywhere; the edit breaks no recorded digest

- `acceptance.json:6` names the command **by path only**: `"counting_command": "python3 .ufo/waves/round-16/measure.py"`. There is no digest for it.
- I enumerated every digest in `acceptance.json`: **16 total** (9 fields whose name ends in `sha256` + 7 values under `receipt_files`, `acceptance.json:36-44`). They are the two probes, the matrix set, and C2's tool/probe/receipt/control/replay files. **None is `measure.py`.**
- Observed bytes: `measure.py` sha256 `205966ad5fe6fbed0b5228b6ae4bcf7060e504818b1386c8478e5f98045b77e8`, working tree clean, committed blob `ce009cd` at master. Grepping the lane for that digest and blob (`--exclude-dir=interactive-sessions --exclude-dir=.git --exclude-dir=.jj`) returns **nothing**.
- `SKILL.md:534` pins the *contract*, not the bytes: "matrix set digest and counts (72 rows, 17 loading) match the pins and the gate exits are 1/0". The matrix pin lives in the script at `measure.py:281` (`EXPECTED_MATRIX_SHA256 = "bf9068d8…"`), over `tests/probe-verdicts/*.json`, not over itself.
- Neither frozen manifest lists it: `.ufo/waves/round-16/frozen/manifest.json` describes only `kama-probe-before.sh`; `.ufo/waves/round-17/frozen/manifest.json` lists five files, none of them round-16's `measure.py`.
- `.ufo/waves/round-16/build/validation.json` pins only the wave-runner stdout/taskCall digests — no per-file digest table. There is no `.ufo/state/` in this lane at all (`ls .ufo/state` → No such file or directory), so no state pin exists to break.

## F2 — The closure references the file but does not pin or route it

- `corpus/lessons/round-16-verifier-spotcheck.md:5`: "No lane-authored file was edited." — a statement about the closure's own discipline, not a pin.
- `:75`: the closure re-measured only "the exits of `measure.py` and `stale-statements.py`", i.e. behaviour, which the proposed edit leaves unchanged.
- `:86`: "All **16 of 16** recorded digests match the committed blobs" — the same 16 digests audited in F1; `measure.py` is not among them.
- The routed-defect list `:180-187` (items 1-6) **does not include rec 6**; item 6 is the check.py/live-harness debt. So no round-17 claim inherits this as an obligation, and no closure statement becomes false if the file changes. Consequence: it is unowned work — it must be an explicit L1 integration edit, not a claim-repair item.

## F3 — No round-17 measurement consumes `measure.py`, so the edit cannot perturb C1's baseline

The C1 claim's "round-16 pair detector" is **`check.py` run directly over the two probes**, not `measure.py`. The `C1MutantRunner` item (`build/spec.json`, item name `C1MutantRunner`; dispatched at `build/dispatch.json:542-544`) specifies: "`pair` = run the mutated check.py (copied into a scratch dir with the nine matrix *.json files)" with `--probe` on the frozen and current probes. `mutants.py` therefore owns its own scratch detector and never invokes round-16 `measure.py`. [INFERENCE: `mutants.py` does not exist yet (`round-17/c1/` is empty); this is read from its item text, not from code. If the builder instead shells out to `measure.py`, it would both (a) write `.ufo/waves/round-16/run-*.json` in the lane and (b) need this file's digest pinned — both reasons to land the edit and record its sha256 before that runner is first executed.]

## F4 — The defect is real in both directions (demonstrated in /tmp, not inferred)

`measure.py:115-117` runs `["git", "-C", str(LANE), "cat-file", "blob", spec]` with **no `env=`**, so it inherits the caller's whole environment, and with no replace guard. Sandbox `/tmp/r17-parity` (removed):

- **False pass (replace ref).** With `git replace <pinned-commit> <forged-commit>`, `git cat-file blob <pinned>:tools/x` returned `FORGED-BLOB`; with `--no-replace-objects` it returned `REAL-BLOB`. This defeats `measure.py:127` (`elif blob.stdout != frozen`), the only leg that ties the frozen snapshot to the pinned commit. The lane has **no replace refs today** (`git for-each-ref refs/replace` → empty), so the spoof is latent, not present.
- **False fail (inherited GIT_\*).** `GIT_DIR=<other repo>` / `GIT_OBJECT_DIRECTORY=<empty dir>` turned the same read into `rc 128`; with `GIT_DIR` unset it exits 0 with the true bytes. In `measure.py` that becomes exit 4 "frozen verification failed" — a *tamper* verdict for a clean snapshot. This is the direction that would poison a repeated measurement loop.
- **Inert today.** On the lane's actual spec, plain and guarded reads are byte-identical: `git -C . cat-file blob 20e392e…:tools/kama-probe.sh` and `git --no-pager --no-replace-objects -C . cat-file …` both hash to `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`, equal to the frozen file and to `acceptance.json:8`. My shell has every relevant `GIT_*` unset, and the lane has no replace refs, so the guard changes nothing in the current environment — exactly what "robustness fix, not a jj-compatibility fix" (`JjAuditKama.md:183`) predicts.

`JjAuditKama.md:122` states the gap precisely: "Separate latent defect: no `--no-replace-objects` and no GIT_* scrub, unlike the other two gates".

## F5 — Why a lane rerun to "prove" the fix is the one unsafe action

- `measure.py:171-172` writes the receipt unconditionally: `out = WAVE / f"run-{name}.json"` then `out.write_text(...)`. There is no `--dry-run` and no selftest (`build_parser` at `measure.py:260-275` exposes only `--probe` and `--timeout`).
- Those two files are pinned by digest in `acceptance.json:36-44` (`run-before.json` `86c59347…`, `run-after.json` `5df94191…`). Any lane invocation dirties both, so the closure's 16/16 digest re-check would stop reproducing. The round-16 lesson records the same hazard and that nothing mechanically prevents it: "open: no mechanical guard stops a seat running it" (`corpus/lessons/round-16.md:169`).
- Even the receipt's `stdout_sha256` cannot serve as the proof handle: "`stdout_sha256` is irreproducible by construction" (`.ufo/waves/round-16/falsify/advice/RerunMatrixFrozen.md:31`) because it hashes stub ports.
- A clone avoids all of it: `WAVE`/`LANE` derive from `__file__` (`measure.py:40-41`), so a copy under `/tmp` writes its receipts into the copy. But that is a measurement run and belongs to L1, and it is not needed for this change (F6).

## F6 — The concrete fix and its proportionate proof

Edit exactly the git read, nothing else:

1. Argv: `["git", "--no-pager", "--no-replace-objects", "-C", str(LANE), "cat-file", "blob", spec]` — the same prefix shape as `round-13/measure.py:278` and `round-12/fidelity.py:95`.
2. Environment: add `env=git_env()` modelled on `round-13/measure.py:264-278` — strip every `GIT_*` key, then set `GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1`, `GIT_OPTIONAL_LOCKS=0`, `GIT_TERMINAL_PROMPT=0`. For the strictest parity, add `GIT_CONFIG_NOSYSTEM=1` and `GIT_CONFIG_GLOBAL=os.devnull` as `round-12/reproduce.py:32-34` does; round-13's own LIMITS call the round-12 method "the config-suppressing reference" (`round-13/measure.py:132`), so either choice must be stated, not implied.
3. Leave the exit table and every comparison untouched: exit 4 still means "frozen snapshot does not match its manifest or the git blob" (`SKILL.md:534`).

Proof, in order: `python3 -m py_compile .ufo/waves/round-16/measure.py`; then replay the **exact new argv + env** against the `/tmp` sandbox in three cases — clean repo (identical blob), repo with a `git replace` (true blob, not the forged one), `GIT_DIR`/`GIT_OBJECT_DIRECTORY` poisoned (exit 0, true blob). That is sufficient because the change is confined to one subprocess invocation and the lane read was already shown byte-identical (F4). A full clone run is optional end-to-end evidence, not a requirement — and must never be done in the lane.

Disclosure conditions (all cheap, all required):

- Record old `205966ad…` → new sha256 in the round-17 lesson and the round-16 gate row's notes. The lane already accepts post-closure runner repair with the old receipt kept intact: "The receipt itself is preserved byte-for-byte" (`corpus/lessons/round-15.md:34`).
- State that on-disk `measure.py` now differs from `git show 726f737:.ufo/waves/round-16/measure.py`; the round-16 `measured_revision` (`acceptance.json:3`) still describes the receipts correctly, but a future byte-diff must not read the divergence as tampering.
- If any future runner (including `mutants.py`) invokes `measure.py`, pin its sha256 at invocation time.
- Consistency note, beyond rec 6's letter: `.ufo/waves/round-16/stale-statements.py:58` has the identical unguarded shape (`["git", "-C", str(LANE), "show", f"{rev}:{path}"]`). If the goal is parity, either fix both in one commit or say explicitly that only `measure.py:116` is in scope; fixing one and silently leaving its sibling reproduces the same inconsistency rec 6 is correcting.

## Residual risk

- The "inert today" observation is local to my environment (all `GIT_*` unset, zero replace refs). That is precisely why the guard is cheap insurance, not proof of a live attack.
- Editing a closed round's counting command has an auditability cost: the bytes on disk cease to equal the bytes at the measured revision. The disclosure requirement (F6) is the whole mitigation and must not be skipped.
- [INFERENCE] Exit codes and the 55/17 vs 72/0 verdict remain unchanged after the edit because only the git subprocess's flags/environment change and object resolution is identical on a clean repo; I could not observe a post-edit run (forbidden), so this is a static conclusion plus the sandbox equivalence.

## Verification gaps / what was executed

- Executed: read-only `git cat-file`/`for-each-ref`/`rev-parse`/`status` in the lane; `sha256sum`; the `/tmp/r17-parity` sandbox (`git init`, commit, `git replace`, env-redirection scenarios), removed afterwards. **No** `measure.py`, `mutants.py`, `controls.py`, probe, harness, selftest or lane gate was run; no server was started; ports 8080/34113 were not touched.
- Not verified: whether `GIT_CONFIG_*` alone can alter `cat-file blob` output (round-12 treats config suppression as the reference; I did not probe it), and L1's actual shell environment at measurement time.
- Installs/updates: none. No tool, package or config was installed or changed. Sandbox `/tmp/r17-parity` deleted; `ss -ltnp` shows no listener attributable to this seat.
