VERDICT: confirm — the new "Vocabulary growth" case at `tools/test-snapshot.sh:162-183` is correct, offline, and red on the frozen probe by construction (two LOW findings and two INFO notes, none blocking).

# Item

`git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff 20e392e b8e485c -- tools/test-snapshot.sh`

One hunk only: `@@ -161,0 +162,23 @@` — 23 added lines, no deletions:

- seeds `$HIST/latest.tsv` with `fixture-a / MODEL_LOADING / llamacpp-loading / - / PORT / yes` and `fixture-z / MODEL_LOADED / bogus / - / PORT / no`;
- runs `snapshot --registry "$REG" --history "$HIST"` (registry is `fixture-b` at this point, fixture already killed);
- asserts: exit 2; `fixture-a row-absent (was verdict=MODEL_LOADING` in DELTA.md; fixture-a never audited as malformed; fixture-a never warned; fixture-z warned; fixture-z audited+dropped.

# What I ran (lane root; exit codes verbatim)

1. Frozen identity: `git show 20e392e:tools/kama-probe.sh > /tmp/.../before-from-git.sh`; `sha256sum` both files → `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` for each; `diff -q` → exit 0. `grep -n MODEL_LOADING .ufo/waves/round-16/frozen/kama-probe-before.sh` → exit 1 (no match); its whitelist (line 895) has only the six pre-round verdicts. The frozen probe **is** the pre-round probe.
2. Current probe: `bash tools/test-snapshot.sh` → exit 0, `RESULT pass=30 fail=0`; rerun → exit 0, identical. (30 = 24 pre-existing + 6 new; matches `.ufo/waves/round-16/run-test-snapshot.txt`.)
3. Frozen probe: `KAMA_PROBE=$PWD/.ufo/waves/round-16/frozen/kama-probe-before.sh bash tools/test-snapshot.sh` → exit 1, `RESULT pass=27 fail=3`; rerun → exit 1, same three. Fails:
   - `FAIL MODEL_LOADING baseline row accepted and diffed (pattern fixture-a row-absent \(was verdict=MODEL_LOADING absent)`
   - `FAIL MODEL_LOADING baseline row dropped as malformed`
   - `FAIL MODEL_LOADING baseline row warned as malformed`
   The other 27 assertions pass, including the case's own exit-2 and fixture-z checks — so the red is confined to the MODEL_LOADING-trust path.
4. Sensitivity isolation (M1): copy of `b8e485c:tools/kama-probe.sh` with `|*\ MODEL_LOADING\ *` replaced by a duplicate `|*\ NOT_HTTP\ *`; `diff` of mutant vs current probe → only line 939 differs. `KAMA_PROBE=.../m1-noloading.sh bash tools/test-snapshot.sh` → exit 1, 27/30, **the identical three failures**. The case is sensitive to that one whitelist token, not to the classify/listeners/doc changes in the same commit.
5. Two-sidedness (M3): current probe plus `|*\ MODEL_*` appended at `:939`. `KAMA_PROBE=.../m3-overbroad-modelstar.sh bash tools/test-snapshot.sh` → exit 1, 28/30; only `FAIL unknown verdict still warns` and `FAIL unknown verdict still audited and dropped`. `fixture-z` (`MODEL_LOADED`) is an effective near-miss guard: an overbroad glob is rejected.
6. Offline proof: `sudo -n unshare -n bash -c 'ip link set lo up; cd /home/vgpnk/Projects/shokunin/kama-shokunin && bash tools/test-snapshot.sh'` → exit 0, `RESULT pass=30 fail=0`. In that namespace only loopback exists, so no external network was reachable and none is needed. Corroboration: every URL in the harness is `http://127.0.0.1:$PORT/...` (`tools/test-snapshot.sh:79-84`), the stub server binds `127.0.0.1:0` (`:57-72`), and `ss` is only used by `listeners` (`tools/kama-probe.sh:244`), which `snapshot --registry` never calls.
7. Artifact truth (cleanup-neutralized scratch copy of the harness, current probe, retained WORK dir):
   - `snap6.out`: `[kama-probe] latest.tsv: dropping malformed baseline row for id='fixture-z'`; `[kama-probe] latest.tsv had malformed rows (dropped); this snapshot rebaselines them`; `snapshot=... rows=1 model_ok=0 drift=1 transitions=2 exit=2`; **no** fixture-a warning.
   - `DELTA.md` appended block: `- 2026-10-20T13:56:05Z baseline-note malformed-row-dropped id='fixture-z'`, `- ... fixture-b row-added verdict=DEAD port=42839 served=-`, `- ... fixture-a row-absent (was verdict=MODEL_LOADING port=42839)`.
   - `latest.tsv` after the run: header + `fixture-b	DEAD	connection-refused	-	42839	yes`; both seeded rows are gone — the seeded trust anchor is replaced, not leaked.
   - `snap6.out` shows `prev=-` because the seeded TSV omits the `#@snapshot_id` header that the writer always emits (`tools/kama-probe.sh:1089`).
8. Hygiene: `pgrep -x llama-server` → exit 1 (none). `pgrep -af 'kama-snapshot-test.*server.py'` caught one transient fixture from a concurrent sibling seat (`.../kama-snapshot-test.sKDL9Y/server.py`); it exited before I finished and was not one of my runs. My fixtures die in `cleanup`; kept WORK dirs and `/tmp` scratch were removed after this report.

# Findings

**LOW-1 — the negative DELTA.md assertion is ledger-global and order-coupled.** Line 172 greps the entire append-only `DELTA.md` for `malformed-row-dropped id='fixture-a'`, not the block this snapshot appended. It is sound in the shipped order (snap5 drops `garbage garbage garbage`, nothing earlier touches fixture-a), but it is not scoped. Evidence: my M2 mutant (whole whitelist replaced, so `DEAD` was no longer accepted) made snap4 emit `- ... baseline-note malformed-row-dropped id='fixture-a'`; the new case then printed `FAIL MODEL_LOADING baseline row dropped as malformed` even though snap6 had accepted the row and `snap6.out` carried no fixture-a warning. Any future case that legitimately drops a fixture-a row as malformed will make this line lie. Fix: capture `wc -l < "$HIST/DELTA.md"` before `run_probe` and grep `tail -n +$((n+1))`, or rely on the already-scoped `snap6.out` negative check.

**LOW-2 — the case pins the second hand-maintained verdict list, not `VOCAB`.** `MODEL_LOADING` lives in two independent literals: `VOCAB` at `tools/kama-probe.sh:62` and the `diff_baseline` case at `tools/kama-probe.sh:939`. This case pins only the latter; `grep -rn vocabulary tests/` → empty, so nothing asserts the JSON `verdict_vocabulary`. [INFERENCE] A round that adds a verdict to `VOCAB` but forgets the whitelist would make snapshots silently drop that verdict's baseline rows as malformed — the exact regression this case exists to prevent, mirrored — and no test in `tests/` would fail; the reverse drift (whitelist without `VOCAB`) leaves `listeners`/`check`/`snapshot` JSON advertising a six-verdict vocabulary while emitting the seventh. Suggested test move: in the same case run `snapshot --json` and assert `MODEL_LOADING` is in `verdict_vocabulary`, which would tie both lists together.

**INFO-1 — the exit-2 assertion (lines 169-170) is non-discriminating.** It passes on the frozen probe and on M1 because exit 2 is driven by fixture-b's `DEAD` row, not by the accepted baseline row. It is a valid guard, but it is not evidence that the vocabulary change produced drift. Asserting `transitions=2 exit=2` on `snap6.out` would discriminate: the frozen probe rebaselines (`transitions=0`) and would fail on that string too.

**INFO-2 — the seeded baseline is not byte-shaped like a real one.** `#@snapshot_id` is omitted, so `prev_snapshot=-`. No test pins `prev_snapshot` (`grep -n prev tools/test-snapshot.sh` → empty), so nothing is lost today; noted only so a future header-validating parser does not make this case fail for an unrelated reason.

# Residual risk

- The case does not exercise the classifier that *produces* `MODEL_LOADING`; it deliberately tests only baseline trust ("no live loading server is needed", lines 164-166). Production coverage lives in the stub matrix and live receipts, which are other seats' items.
- The block is sequence-coupled to the preceding dead fixture and `write_registry fixture-b`: it requires fixture-a to be absent from the registry. The comment names the dead fixture and fixture-b but not the registry-absence dependency; [INFERENCE] reordering would break it.

# Limitations

- No `lsp` tool/language server is exposed in this seat's toolset, so no semantic diagnostics were possible for bash; all verification is by execution, `git diff`/`diff`, and artifact inspection.
- I did not audit other test files, the 72-row matrix, or the live harness; I did not run `measure.py`.

# Installs

None.
