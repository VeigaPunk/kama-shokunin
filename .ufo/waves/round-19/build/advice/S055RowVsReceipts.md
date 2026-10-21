VERDICT: partial - the erratum's live/ pointers, timestamps, port and checkpoint-byte claims hold; seven S055 cells still resolve ambiguously; the lesson's gate cite was wrong at 7229fa9 and is fixed at HEAD f1790e2, but the "checkpoint revision" label is still wrong.

Scope: `corpus/SOURCES.md` S055 (line 67) and erratum (lines 217-221). Identical at 8bf99ca, 7229fa9 and HEAD f1790e2. Evidence and exit codes: `/tmp/kama-r19-S055RowVsReceipts/out/S055-anchor-verdicts.md`, with `out/s055-anchor-matrix.json` and `out/s055-entries-matrix.json`.

Resolved:
- "2026-10-20T22:38:48.776Z", "22:38:48.924Z", "port 33769": live/receipt-1 only.
- "raw receipts live/receipt-1..3": live family; bytes equal checkpoint 101f3991 and every later commit through HEAD.
- Erratum E1 (commands.json absent at c6dc46f, present from 1c325b2): true. E2 (live/ bytes restored): true. E3 (tip gate outputs describe live-recovery, tool 83eac5c0): true at HEAD.

Still ambiguous:
1. "first receipt": live/receipt-1 and live-recovery/receipt-1 are both index 1; only the timestamp or port disambiguates.
2. "schema kama-llamacpp-live/v3": matches all six receipts.
3. "tool sha256 dc036d7d...": the value fits live/1-3. As a file it exists only at c6dc46f and 1c325b2; checkpoint 101f3991 holds ec7a7567 and the tip holds 83eac5c0.
4. "commands/exits in round-18/runs/commands.json": two committed contents. ce7dc79c (1c325b2 through eb78788) binds live/ with measured_commit c6dc46f; b8dadf30 (1b85a24 through HEAD) binds live-recovery/ with measured_commit eb78788. The erratum's "1c325b2/101f3991 onward" spans both.
5. "at measured c6dc46fabc51...": the hash resolves, but the file is absent at c6dc46f (git cat-file rc 128). "Measured" versus "containing" commit is unresolved.
6. Source "python3 .ufo/waves/round-18/runs/run.py": four committed producer versions. Only 1c325b2/101f3991 (sha e3c957ca, line 43) writes live/; the rest write live-recovery/.
7. Erratum "tip's runs/live-gate-*.stdout": bare path. It reads live/ output at 1c325b2 through eb78788 and live-recovery output at 1b85a24 through HEAD.

Defects in the erratum's evidence (not in the S055 row):
- D1, fixed at HEAD f1790e2: at 7229fa9, `corpus/lessons/round-18.md:419` cited eb78788 `live-gate-1.stdout` (sha b2043ba8) as "the recovery gate output"; those bytes read `VALID .../live/receipt-1.json`. The registry row `gate-live-1` pinned the same token. `tools/citation-provenance.py` at 7229fa9 exited 0 (run in a clone), so the mislabel passed. HEAD now pins 1b85a24 / 1cb5a41b.
- D2, still present: `round-18.md:416-417` calls cite(1c325b2) "the checkpoint revision"; the checkpoint is 101f3991. Bytes are identical, so only the label is wrong.
- D3, still present: `round-18.md:53` cites the bare path `runs/live-gate-1.stdout`.

Drift (observed 06:37-06:43Z; lane HEAD f1790e2 after 7229fa9 and 5b108c1):
- run.py PID 415882 (measured_commit 7229fa95) regenerated `live-recovery/receipt-1..3.json` at 06:40:32Z in the lane working tree. The bytes (8ad0efb6, 5a0e8f65, c88bef3f) differ from HEAD (89728a02, be75336f, 2ee71e01). The new receipts are v3, pass 11/11, tool 83eac5c0, ports 46223/44331/33747. None matches an S055 anchor cell.
- The working-tree `runs/commands.json` is an in-progress 34-entry file (sha c82dbfa0). Committed HEAD still holds b8dadf30.
- `live/` receipts, the committed and working-tree `live-gate-{1,2,3}.stdout` bytes, and the tool are unchanged, so cells 1-6 and erratum E1/E2 are unaffected.

Suggested: keep S055 cells on committed blobs (ce7dc79c at 1c325b2, or b8dadf30 at 1b85a24); change the "checkpoint revision" label at round-18.md:416 to 101f3991; read "tip" as HEAD (`git show HEAD:`), not the working tree, while a run is active.

No lane file was edited. No process, server, install or subagent was started by this seat.
