VERDICT: confirm - install_tree() is deterministic on untouched inputs (2 calls, 2 fresh interpreters, 20 repeats: one digest, 6c216313…, equal to the round-18 receipt pin and to the lane gate's recomputation), so nondeterminism does not threaten the sixth pin.

Scope: leaf probe, read-only against the live install dir and the lane. Exact commands, exits and sha256 of every output: /tmp/kama-r19-TreeDeterminism/out/RECEIPT.md.

## Observed
- Probe (`out/probe_install_tree.py`, exit 0, `DETERMINISTIC`):
  - Call 1 and call 2, nothing touched between: both `6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`, identical 51-member map. Elapsed 0.027405 s and 0.027227 s.
  - Two fresh interpreters: same digest, 0.027610 s and 0.027269 s. Repeat batch n=20: one distinct digest, median 0.026626 s (min 0.026126, max 0.027554).
  - Install-dir snapshots (kind, size, inode, mode, mtime, ctime per entry) before, between, after two calls, and at end are identical: `touched_during_probe: false`.
- Pin: digest equals receipt-1 `server.install_tree_sha256`; map equals the receipt's 51-member map; no member mtime after receipt start 2026-10-21T05:10:23Z.
- Gate recomputation (`install_tree_sha`, lane `tests/llamacpp-live/check-receipt.py` sha 10912f24…, run with `python3 -B`): same digest, equal to pin, exit 0.
- Boundary (`out/mutate_install_tree.py`, copies only, exit 0): 13/13 cases matched their code-reading predictions; live dir untouched.
  - Digest unchanged: path change, touched mtimes, chmod, rewrite with same bytes, added symlink, added subdirectory.
  - Digest changes: one flipped byte in `libllama.so.0.7.0`, added file, renamed member, deleted member, unreadable member (silently dropped, 50 members), unreadable install dir (returns `({}, None)`).
  - Raises: non-UTF-8 member name gives an uncaught `UnicodeEncodeError`.

## Findings
1. Determinism holds on untouched inputs; the sixth pin's premise is not falsified.
2. The operability limit is sensitivity, not nondeterminism: any byte change, addition, deletion or rename among the 51 members moves the whole-tree digest. The pin therefore gates the entire install tree. A rebuild that touches unrelated members would break it [INFERENCE from the boundary table]. This matches round-18 `falsify/advice/ConnectTsukuroi.md`, which prefers the impl pin as the stable one.
3. Silent subset: `install_tree()` (`tools/kama-llamacpp-live.py:178`) drops an unreadable member without a diagnostic, so the digest can cover a subset with no error.
4. Evidence gap (observed): `.ufo/waves/round-18/runs/commands.json` (measured_commit eb78788b…, 32 records) has no argv containing `--expect-install-tree-sha256` and no `tree-grid*` or `tree-pin-negative` records; `runs/` has no such files (receipt rows 7-9). The uncommitted `runs/run.py` (lines 65-69) contains them. The sixth pin's live gate and the "pre-pin 0/3, with pin 3/3" grid therefore have no recorded official execution in the lane. I did not verify those claims.
5. Install-dir timeline (observed): dir mtime 2026-10-20T11:10:36Z, so no entry was added, removed or renamed at or after receipt start. Dir ctime 2026-10-20T13:17:53Z is later, consistent with a metadata-only change [INFERENCE].
6. Drift: the lane gate changed after my copy (copy afc9e79b…, lane 10912f24…). The producer is unchanged (83eac5c0… in both). The gate check was re-run against the lane file.

## Installs, lane writes, processes
None installed or updated. No servers, subagents, or lane git/index operations. The lane `tests/llamacpp-live/__pycache__` pre-dates this session; gate imports used `-B`, so the only lane write is this report.

## For main agent
- Confirm the sixth-pin live-gate and grid runs exist as recorded artifacts before citing C2 (finding 4).
- If the install dir changes, re-run `out/probe_install_tree.py`; the digest is per-state and moves only when bytes or membership change.
