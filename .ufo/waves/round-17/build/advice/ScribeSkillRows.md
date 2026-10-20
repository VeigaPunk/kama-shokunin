VERDICT: partial — append-ready SKILL.md draft written with rows for all six requested tools; four of the new tools do not exist yet and their exits are spec-derived, so they are marked PROVISIONAL; the round-13 finding is confirmed by reading code only, not by running the gate.

Owned write: `.ufo/waves/round-17/build/drafts/skill-round17.md` (9,299 bytes). Nothing else in the lane was written. No lane gate, measurement, `jj`, git write, or llama-server was run.

# Behaviour

The draft gives `## Round-17 gate grading and fail-capable live checks (owner: kama)` in the Round-16 seven-column table style, plus a second table of "proves / does not prove" per row, and an order-of-operations paragraph. Rows: probe fault controls, C1 mutant counting command, C2 fake-server controls, SOURCES append-only guard, receipt v2 gate, live lifecycle receipt v2, and the round-13 finding.

# Exit status of each row

| Row | Status of the tool | Exit basis |
|---|---|---|
| `tests/probe-verdicts/fault-controls.py` | absent (checked 2026-10-20 15:16Z) | spec `.ufo/waves/round-17/build/spec.json`, task text "exit 0 iff accepted == 0, 1 otherwise, 2 own fault" — PROVISIONAL |
| `.ufo/waves/round-17/c1/mutants.py` | absent; `c1/` is empty | spec gives no exit code; totals only — **exit codes unknown**, stated as NOT SPECIFIED |
| `tests/llamacpp-live/controls.py` | absent; `tests/llamacpp-live/` holds only `check-receipt.py` | spec "exit 0 iff accepted_bad == 0 and good_ok, else 1; 2 own fault" — PROVISIONAL |
| `tools/sources-append-only.py` | absent | spec "Exit 0 no violations, 1 violations, 2 unreadable/parse error" — PROVISIONAL |
| receipt v2 gate | v1 still in place, sha256 `6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6` | spec "Exits unchanged: 0 valid / 1 invalid / 2 unreadable" — PROVISIONAL for v2 path |
| live harness v2 | v1 still in place, sha256 `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4`; v1 exits read from code | v2 "receipt always written on internal faults, exit 2" from spec — PROVISIONAL |
| round-13 gate | unchanged code | exits read from code and SKILL.md:430 |

# Findings and evidence

- **Round-13 new finding is real in the code (read, not run).** `.ufo/waves/round-13/measure.py:385` reads `head_quality = git_read(['cat-file', 'blob', f'{head}:{QUALITY_GIT_PATH}'], commands)`; `:397` is `worktree_matches_head = final == head_quality`; `:446-447` appends `'worktree_not_at_measured_revision'` when it is false; `:455` requires it for `clean`; `:457` returns `'clean' if clean else 'documentation_mismatch'`. HEAD comes from `:295` `rev-parse HEAD`. Access 2026-10-20. The jj audit reached the same conclusion by sandboxed replay: `/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md:154` — "SKILL.md reads exit 1 as a failed gate, so the lane would publish a false failure." [INFERENCE: the replay was on jj 0.45.1 and the audit did not run the live gate on this lane; I did not re-run it.]
- **SKILL row exit map.** `SKILL.md:430` — "1 failed (`documentation_mismatch`); 2 could-not-evaluate (`snapshot_tampered`". The draft keeps this map and adds the ordering note rather than changing exit semantics; the proposed reclassification is marked "not decided".
- **Unborn HEAD.** `JjAuditKama.md:118` records round-13 `rev-parse HEAD` on unborn HEAD → exit 3 `probe_error`; consistent with SKILL.md:430's "3 could-not-evaluate (`probe_error`…)".
- **C1 grader gap, confirmed by Round-16 advice.** `.ufo/waves/round-16/falsify/advice/MutateHarness.md:20` — "**Result: survived 5; killed 0; inconclusive 0.**" The five mutants are ignore-reason, ignore-exit, ignore-drift, casefold-verdict, timeout-pass (table lines 24-28). Access 2026-10-20.
- **Probe hashes move under the pair detector.** `tools/kama-probe.sh` now hashes `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`; `MutateHarness.md:173` cites `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50` for the same file. The Round-16 frozen probe `.ufo/waves/round-16/frozen/kama-probe-before.sh` is `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`. Round-17 frozen probe `.ufo/waves/round-17/frozen/tools_kama-probe.sh` = current. [INFERENCE: the probe changed after Round 16 at an unknown commit; I did not identify it.] The draft therefore pins the Round-16 frozen probe as the `pair` "before" baseline, as the spec instructs.
- **C1 check.py grading lines.** `tests/probe-verdicts/check.py:331` — `row = doc["rows"][0]` sits inside a `try` (`:329-336`) that catches `JSONDecodeError`, `KeyError`, `IndexError` and `TypeError`: stdout `[]` or `{"rows":[]}` becomes a recorded row error. The uncaught path is `:337-338`, outside that `try`: when `rows[0]` is a list, string or number (for example `{"rows":[["x"]]}`), `row.get(key)` raises `AttributeError`, which the function's only handler (`:349`, `OSError`) does not catch, so the run ends in a traceback. The spec's malformed-output fault F8 is what exercises this path. `:337-338` read verdict, reason, drift, served_model, evidence without checking `served_model`; `:346` — `and record["drift"] == (record["verdict"] != "MODEL_OK")`. Sha256 `b853576edd54e006c4d8742c1a7335a0d6cca475d107acce7792da75b6145762` (current equals `.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py`). [INFERENCE: the AttributeError path is read from code; I did not execute it.]
- **C2 harness v1 checks.** `tools/kama-llamacpp-live.py:50` — `SCHEMA = 'kama-llamacpp-live/v1'`; `:1000` — `exit_code = 0 if all(c['passed'] for c in checks) else 1`; `:801` — `return 3` on digest mismatch. Round-16 review, `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:82-83`: "`teardown_exited` proves reaping, not teardown (high)"; it cites `tools/kama-llamacpp-live.py:1024-1028` asserting only `receipt['teardown']['returncode'] is not None`. Access 2026-10-20. I read these lines via grep and the review; I did not re-open 1024-1028 myself.
- **Append-only rule.** `/home/vgpnk/Projects/shokunin/CORPUS.md:116` — "Only `status`, `recheck` and `used-by` change in place, and each change". `corpus/lessons/round-16-verifier-spotcheck.md:184` — "Contract rule 2 lets only `status`/`recheck`/`used-by` change in place". Access 2026-10-20.
- **S041 in-place edit, verified by git read.** `git show b8e485c:corpus/SOURCES.md` line 53 vs `git show ccc4bb3:corpus/SOURCES.md` line 53: the receipt cell changes from 13:49:38 port 32845 to 14:06:27 port 37527 with `tool sha256 b8c5e8d4…`; the teaches cell adds the 503 loading envelope claim. Both revisions exist (`git cat-file -t` = commit). This is the case the SOURCES guard must flag.
- **Planned exit and selftest text.** Spec text quoted, not re-read from code: sources-append-only — "Exit 0 no violations, 1 violations, 2 unreadable/parse error" and "It must flag S041 for `--from b8e485c --to ccc4bb3`". fault-controls — "exit 0 iff accepted == 0, 1 otherwise, 2 own fault". controls — "exit 0 iff accepted_bad == 0 and good_ok, else 1; 2 own fault". Source: `.ufo/waves/round-17/build/spec.json` (the task blocks named for each tool). Access 2026-10-20.
- **Round-16 artifacts the draft cites exist.** `.ufo/waves/round-16/live/receipt.json`, `.ufo/waves/round-16/live/receipt-frozen-probe.json`, `.ufo/waves/round-13/frozen/expected.json` — listed on disk.

# Limitations and unknowns

- Exit code of `c1/mutants.py` is not stated anywhere in the spec; the draft says so rather than inventing one. L1 must choose it before integration.
- The self-test count for the v2 receipt gate is not stated beyond "at least 10 v2 mutations" in the spec; the draft says PROVISIONAL.
- `controls.py` and `fault-controls.py` self-tests are not specified; the draft says "none specified".
- I did not open llama.cpp source (`704366d76`) this session; the C2 citations of `/health` and SIGTERM anchors are the seat that writes those DOC strings, and the draft makes no source claim about them.
- The round-13 "proposed reclassification" is a design suggestion for L1, not a fix; it is marked undecided.
- The draft cites `corpus/SOURCES.md` rows by id and revision. Nothing was appended to any lane doc.
- No output of the not-yet-written tools exists; the draft's PROVISIONAL marks must be replaced by observed exits after the executors land and L1 runs their commands.

# Sources opened (all accessed 2026-10-20)

- `SKILL.md:507-553` (Round-16 section); row lines 531-536 — "grades verdict, reason, exit and drift" (line 533).
- `tests/probe-verdicts/check.py:281-383` — `row = doc["rows"][0]` (line 331); `and record["drift"] == (record["verdict"] != "MODEL_OK")` (line 346).
- `tools/kama-llamacpp-live.py:1-78` and grep hits at 50, 801, 1000 — `SCHEMA = 'kama-llamacpp-live/v1'` (line 50).
- `.ufo/waves/round-13/measure.py:286-300, 378-458` — `worktree_matches_head = final == head_quality` (line 397).
- `.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md` (full) — "SKILL.md reads exit 1 as a failed gate, so the lane would publish a false failure." (line 154).
- `.ufo/waves/round-16/falsify/advice/MutateHarness.md` (full) — "survived 5; killed 0; inconclusive 0" (line 20).
- `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md` (full) — "`teardown_exited` proves reaping, not teardown" (line 82).
- `corpus/lessons/round-16-verifier-spotcheck.md:180-187` — routed defects 3 and 6.
- `/home/vgpnk/Projects/shokunin/CORPUS.md:116` — "Only `status`, `recheck` and `used-by` change in place".
- `corpus/SOURCES.md` lines 1-12 (contract header) and row S041 at line 53 in `b8e485c` and `ccc4bb3` (git read).
- `.ufo/waves/round-17/build/spec.json` — task blocks for the four unwritten tools and the `kama-llamacpp-live/v2` task.
- `.ufo/waves/round-17/frozen/manifest.json` — frozen hashes; `~/.omp/agent/RULES.md` read for the tooling directive.

# Installs

None. No package, binary or configuration was installed or changed.
