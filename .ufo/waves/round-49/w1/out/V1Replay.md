# V1Replay — round-49 code review: `tools/kama-live-replay.py` witness pass-through

**Verdict: the round-49 change to `kama-live-replay.py` is correct and fail-closed; the only actionable gap is missing selftest coverage of the witness path (proposed diff attached), plus two doc-drift nits and one validation asymmetry.**

Reviewed: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff 438127bc01ff3b99f98468549d58046f932490ef 74558c71c38ceaeace15fd4cf8aa9d84977584b1 -- tools/kama-live-replay.py` (saved as `diff-kama-live-replay.patch`). Ran in a scratch `git clone --shared` of the lane whose `tools/kama-live-replay.py` is byte-identical to 74558c71 (`git diff --stat 74558c71 HEAD -- tools/kama-live-replay.py` empty; clone HEAD 122c4ee95701587cef7f4342c3d175622ec2f4ad).

---

## Findings

### 1. Low — no selftest case exercises the witness path (main actionable gap)
`_selftest()` (`kama-live-replay.py:306-436`) has 22 cases (provenance, digests, unsafe member, v5 pins, projection, compare) and none passes `witness_dir`; `run()` (`:366`) calls `replay(rp, work, live=live, allow_file=True)` with no witness args. The whole round-49 surface (argv splice, grown subprocess bound, `res["witness_dir"]`, witness-block-is-not-compared) is untested.

**Proposed diff:** `proposed-selftest-witness.patch` (in this out dir) adds two cases after `run("projection-differs", ...)` (`:411`):
- `witness-passthrough` — v4 receipt, fake live tool (built from the existing `fake_live` source) that: asserts `--witness-dir` and `--witness-timeout` both appear before `--out` in argv, asserts the timeout value parses to exactly `2.0`, writes `ready.json`, adds a `witness` block to the rerun receipt, then sleeps 1.2 s. `replay(..., witness_dir=wdir, timeout=0.5, witness_timeout=2.0)` must exit 0 with `match=True`, `res["witness_dir"] == os.path.abspath(wdir)`, and `ready.json` present.
- `witness-v5-passthrough` — same via a v5 receipt (`--server-archive` also spliced), pinning the combined insertion order.

The 1.2 s sleep sits inside the grown bound (2.5 s) but outside the plain `timeout` (0.5 s), so the case verifies the timeout arithmetic, not just argument plumbing.

**Teeth (verified by running):** each of three mutations flips both new cases to FAIL while the other 22 stay green:

| mutation | result |
|---|---|
| remove the witness splice (`CUT 275.=279`) | `FAIL witness-passthrough: exit=2 refused=no-rerun-receipt:exit=1:... a.index('--witness-dir')` |
| drop `+ (witness_timeout if witness_dir is not None else 0)` (`:281`) | `FAIL witness-passthrough: exit=2 refused=could-not-run:TimeoutExpired` |
| add `"witness": rec.get("witness")` to `projection()` | `FAIL witness-passthrough: exit=1 refused=None mism=['projection:witness:null->{"released": true, ...']` |

Unmutated: `KLR_SELFTEST pass=24 fail=0`, exit 0 (baseline without the change: `pass=22 fail=0`).

Not covered offline: `main()`'s `--witness-dir` isdir gate and the child-side `--witness-timeout > 0` check (these need CLI subprocess / real live tool; both are single-statement checks, and the child check is the live tool's own selftest domain).

### 2. Low — doc drift: Usage synopsis and J-keys line not extended
- `kama-live-replay.py:33` — `Usage:` synopsis still reads `... [--live TOOL] [--timeout S]`; the new `[--witness-dir D] [--witness-timeout S]` (described in prose at `:42-45`) are missing.
- `:37` — module docstring's `Writes J: {schema, receipt, work, rerun_receipt, match, refused, mismatches, notes, inputs}` omits the new top-level `witness_dir` key that `replay()` now sets (`:279`).

Fix: extend both lines to name `--witness-dir/--witness-timeout` and `witness_dir`.

### 3. Nit — validation asymmetry: `--witness-timeout` not validated in `main()`
`main()` validates `--witness-dir` locally (`:482` `ap.error("--witness-dir must be an existing directory")`) but not `--witness-timeout`. A bad value (0, negative, `nan`) is caught only by the live child's `parser.error('--witness-timeout must be > 0')` (`kama-llamacpp-live.py:1583-1584`) after spawn, surfacing as `refused=no-rerun-receipt:exit=2:<stderr tail>` — fail-closed, but with a degraded diagnostic, and `--witness-timeout inf` passes the child's `> 0` check and makes `subprocess.run(timeout=inf)` unbounded. Suggest mirroring the child's check (reject `not v > 0`, including non-finite) next to `:481-482`.

---

## Verified-correct items (with evidence)

- **argv insertion position, with and without `--server-archive`.** Base argv always terminates in `["--out", rerun]`. v5 splice `argv[-2:-2] = ["--server-archive", archive]` (`:273-274`) is followed by the witness splice `argv[-2:-2] = ["--witness-dir", os.path.abspath(witness_dir), "--witness-timeout", str(witness_timeout)]` (`:275-279`). Final order: `... --server-archive A --witness-dir D --witness-timeout T --out R` (v5) / `... --model-url U --witness-dir D --witness-timeout T --out R` (v4). Both insert *before* the trailing `--out` pair; neither can split a `--flag value` pair; `--out` remains last. `str(witness_timeout)` ("120.0"/"2.0") parses back as float in the child. No positional-arg contract is disturbed (all other lane callers — round47/48 audits — invoke the CLI with named args and no witness flags; no module imports `replay()`).
- **Timeout arithmetic.** `:281` `timeout=timeout + (witness_timeout if witness_dir is not None else 0)` — grows only when a witness is requested, exactly matching the docstring ("the bound grows by the witness timeout"). M2 above proves the case catches a regression.
- **`res["witness_dir"]`** (`:279`) is set before `subprocess.run`, so it survives a `TimeoutExpired`/`Refused` path and lands in the written J (`main()` dumps `res` verbatim, `:486`), pointing the observer at the ready.json directory.
- **`main()` validation** (`:481-482`): `ap.error` on non-directory `--witness-dir`; placed after the `--receipt/--work/--out` check and after the `--compare`/`--selftest` early returns, so it cannot interfere with those modes. `--witness-dir` is independently re-validated by the child (`kama-llamacpp-live.py:1581-1582`), so a directory deleted between validation and child start fails closed too.
- **Docstring prose** (`:42-45`): accurate — child receives both flags, observer reads `ready.json` and creates `release`, receipt gains a `witness` block that records release, witnessed replay matches exactly like an unwitnessed one.
- **The witness block is ignored by `compare()`/`projection()`, and that is correct.** `projection()` (`:168-196`) returns only `props/slots/health/models/metrics/loading/teardown/ownership`; `compare()` (`:198-233`) checks schema, outcome, server/model sha256, evaluated checks, v5 provenance pins, and the projection. Nothing reads the rerun's `witness` key. This is the right design: the three recorded receipts predate round 49 and have no `witness` block (comparing it would make every witnessed replay mismatch), and `port/pid/dir/waited_ms` are instance facts the projection deliberately excludes. `released=False` (observer absent) must not fail surface equality — the guarantee lives in the frozen C1 counter, which independently requires `rr["witness"]["released"] is True` (`round49-replay-witness-audit.py:324-326`). M3 pins this invariant.

---

## Residual risk and verification gaps
- **Orphan `llama-server` on subprocess timeout** (pre-existing pattern): `subprocess.run` kills only the live tool on `TimeoutExpired`; the live tool's `llama-server` child could survive. With the witness hold the exposure window is bounded by `+witness_timeout`, and the child's normal runtime is seconds against a 600+120 s bound — theoretical, unchanged in character by this diff.
- The live tool overwrites `port_listener_ownership` with a post-witness verify (`kama-llamacpp-live.py:1864-1865`); that is the compared ownership projection for witnessed reruns. Passed in the L1 dry run (3/3); noted as cross-tool interaction, live-tool seat's scope.
- I did not run the real C1 counter (network + real server starts; sibling seats are running it concurrently — 14 `llama-server` PIDs observed on host, none tracing to this seat's scratch). Evidence here is code inspection plus the offline selftest console; the L1 dry-run facts are as given.
- `main()`'s `--witness-dir` error path not executed end-to-end (requires CLI invocation); single-statement logic, trivially correct.

## Evidence (commands, outputs, exit codes)
- Baseline at 74558c71: `python3 $S/lane/tools/kama-live-replay.py --selftest --scratch $S/st-base` → `KLR_SELFTEST pass=22 fail=0`, exit 0.
- With proposal applied: `pass=24 fail=0`, exit 0 (also `selftest-final.txt`).
- Mutations (each `cp $S/klr-cased.py` restore between): M1 `FAIL ... exit=2 refused=no-rerun-receipt:exit=1`; M2 `FAIL ... exit=2 refused=could-not-run:TimeoutExpired`; M3 `FAIL ... exit=1 mism=['projection:witness:null->...']`; all three overall `KLR_SELFTEST pass=22 fail=2`, exit 1.
- No tools installed (none needed); no services started/stopped by this seat; no git/jj mutation anywhere (clone edits were working-tree-only, reverted, and the clone was removed).

## Files written
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Replay.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Replay/diff-kama-live-replay.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Replay/proposed-selftest-witness.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Replay/selftest-final.txt`
