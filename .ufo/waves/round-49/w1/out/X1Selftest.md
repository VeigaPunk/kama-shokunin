# X1Selftest — round 49, lane kama — selftest power

**Verdict: both selftest-power legs deliver. The three round-49 `_provenance_selftest()` bound cases ported unchanged onto the round-48 `verify_archive_member()` all fail or hang there (sparse hangs past the 10 s cap, killed), and a proposed `kama-live-replay.py --selftest` case drives `--witness-dir` end to end: it passes 23/23 on 74558c71 + the test-only diff and fails on two mutants that drop the pass-through (exit 2 `no-rerun-receipt`, selftest exit 1).** No production line is changed by the replay diff (42 added lines, 0 removed); no lane file was edited.

Axes named: **operability** (can a regression in the round-49 bounds or in the witness hand-off be detected by a test, not just by the counter?), **friction** (offline, ~0.2 s pass, ~10 s per failing witness case), **evidence durability** (frozen copies + logs in my out dir, scratch removed).

## 1. Ported bound cases: round-49 cases on round-48 code

Harness (deliverable, offline, no server, no network):
`port-round49-cases.py --old <438127bc live tool> --new <74558c71 live tool> --scratch DIR`
Each case is a child process; the parent imposes the 10 s cap and does no hashing. The stubs are built exactly as `_provenance_selftest()` builds them (tools/kama-llamacpp-live.py:1359-1407 at 74558c71). Command actually run:

```
S=/fast/scratch/hyaku/kama-r49/X1Selftest
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" show 438127bc01ff3b99f98468549d58046f932490ef:tools/kama-llamacpp-live.py > work/kama-llamacpp-live-438127bc.py
git -C "$S/lane" show 74558c71c38ceaeace15fd4cf8aa9d84977584b1:tools/kama-llamacpp-live.py > work/kama-llamacpp-live-74558c71.py
python3 .../port-round49-cases.py --old work/kama-llamacpp-live-438127bc.py \
        --new work/kama-llamacpp-live-74558c71.py --scratch "$S/port-st"
```
Exit **0**; `port-round49-cases.log` (`"ok": true`), wall 10.3 s; stub sizes 251 B (archive), 206 B (sparse).

| case (new selftest's exact call) | old 438127bc (10 s cap) | new 74558c71 (control) |
|---|---|---|
| size-mismatch `(arc, asha, 'rel/llama-server', ssha, 1)` | **raised TypeError** `verify_archive_member() takes 4 positional arguments but 5 were given`, 58 ms | SetupError `provenance-member-size-mismatch`, 57 ms |
| sparse `(sparse, sha256(sparse), 'rel/llama-server', ssha)` | **HANG, killed at 10.0 s** (10,010 ms), no output | SetupError `provenance-member-sparse`, 49 ms |
| not-regular `(DIR, asha, 'rel/llama-server', ssha)` | **raised SetupError `provenance-archive-unreadable`** (wrong token), 58 ms | SetupError `provenance-archive-not-regular`, 53 ms |

Why the old code behaves this way (saved copy `kama-llamacpp-live-438127bc.py`, same line numbers as `git show 438127bc:tools/kama-llamacpp-live.py`):
- `193` signature `verify_archive_member(archive, asset_sha256, member, server_sha256)` — no `server_size`, so the size predicate is not expressible; the ported call is a TypeError.
- `198-203` `sha256_file(archive)` runs with **no `stat` first**: a directory opens as `IsADirectoryError` → caught as `provenance-archive-unreadable` (`214-216`), not `-not-regular`; a FIFO/device would block here, which is the round-49 `-not-regular` case's subject.
- `205-212` `tarfile.open(archive)` + `getmember` + unbounded `extractfile` hash: the 206-byte PAX archive declaring a `10**15`-byte GNU-sparse member is hashed in full. At the observed streaming rate this does not finish inside 10 s — the round-48 Sen2Live F1 hazard, reproduced.
- The new code's guards are at 74558c71 `tools/kama-llamacpp-live.py:230-235` (`S_ISREG`, size cap), `252-254` (streaming index cap), `260-264` (`sparse`, `size != server_size`) — all before the member is hashed (`266-269`).

## 2. Witness selftest case for `kama-live-replay.py` (proposed diff)

`witness-selftest-proposed.diff` (applies cleanly: `patch -p1 --dry-run` exit 0 against 74558c71's file; full patched text in `kama-live-replay-witness-selftest.py`). It adds `import threading`, `import time`, and one `_selftest` case `witness-passthrough` after `projection-differs`. **Nothing in the production path changes** — `replay()`/`main()` at `tools/kama-live-replay.py:234-281` are untouched (the diff contains no removed lines).

What the case does (in the selftest's own temp tree, reusing the existing `fake_live`):
1. builds `witness-live.py` = a witness prefix (`json,os,sys,time`; `a.index('--witness-dir')`, `a.index('--witness-timeout')`; write `ready.json` `{schema:'kama-live-witness/v1', pid, timeout}`; poll for `release` up to 15 s; write `released`) followed by the unchanged fake receipt body — so the rerun receipt only exists after the release;
2. runs `replay(receipt(), ..., live=witness_live, allow_file=True, witness_dir=wdir, witness_timeout=15)` while an observer thread waits for `ready.json`, records it, then writes `release`;
3. passes only when: replay exit 0, `ready.json` schema `kama-live-witness/v1`, child pid present, forwarded timeout == 15, and the child's `released` marker exists.

Runs (logs in my out dir, exit code appended to each log):

| code under test | command | result |
|---|---|---|
| 74558c71 + proposed diff | `python3 kama-live-replay-witness-selftest.py --selftest --scratch "$S/st-patched"` | **`pass witness-passthrough`; `KLR_SELFTEST pass=23 fail=0`; exit 0** (`selftest-patched-74558c71.log`) |
| mutant A — drops the whole `argv[-2:-2] = [...--witness-dir...]` block (`witness-mutant-a-drops-passthrough.diff`) | same | **`FAIL witness-passthrough: exit=2 ... refused=no-rerun-receipt:exit=1` (child `ValueError` at `a.index('--witness-dir')`); `pass=22 fail=1`; exit 1** |
| mutant B — drops only `--witness-timeout` (`witness-mutant-b-drops-timeout.diff`) | same | **`FAIL witness-passthrough` (child dies at `a.index('--witness-timeout')`); `pass=22 fail=1`; exit 1** |

The mutants are diffed against the patched file in the same directory. The pass evidence is the child's own file effects (`ready.json` seen by the observer, `released` written only after release), not the replay's own claim.

## 3. Optional (advisory, beyond the item): untested archive-level token

At 74558c71 the archive-level bound `provenance-archive-too-many-members` (MEMBER_MAX_COUNT, `tools/kama-llamacpp-live.py:209,252`) and `provenance-archive-too-large` (`:208,233`) are exercised by **no** selftest and by no C1 leg (C1's `cap` leg only covers the sparse member, as its docstring says). I verified both tokens by hand against 74558c71: a 4097-entry tar → `provenance-archive-too-many-members` in 38 ms; a 2 GiB sparse regular file → `provenance-archive-too-large` in 0 ms (no read). I propose `optional-archive-too-many-members.diff`: one index-cap case in `_provenance_selftest` (7 added lines, `many.tar` + one tuple). Evidence: unpatched 74558c71 selftest `ok` exit 0; patched selftest `ok` exit 0 (`live-selftest-optional-many-members.log`); with the production cap check removed the same selftest exits 1 with `AssertionError` (`live-selftest-optional-many-members-mutant.log`) — the case discriminates. I deliberately did **not** propose a selftest for `-too-large`: `truncate(2 GiB)` is only cheap on a sparse-capable filesystem, so a selftest would risk materialising 2 GiB on CI; the hand check above is the safe evidence.

## Risks / limits

- The witness case is function-level (`replay()`), not through `main()`: it does not cover the CLI guard `--witness-dir must be an existing directory` (`tools/kama-live-replay.py:481-482`). That guard is one line and unchanged in round 49; adding a CLI-level case would need a subprocess and a second receipt, which I left out of the minimal proposed diff.
- A failing `witness-passthrough` costs ~10 s (observer fallback deadline) before it reports; passes are ~0.2 s.
- The 10 s ported-case cap is the OS wall clock on this host; the sparse hazard is unbounded by construction (10^15 declared bytes), so the hang result does not depend on host speed.

## Housekeeping

- Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`: read-only git only (`git clone --shared`, `git show`, `git diff --stat`), no writes outside my out dir and this report; no jj, no index mutation. Fleet root untouched.
- Scratch `S=/fast/scratch/hyaku/kama-r49/X1Selftest` removed after copying every log/diff cited here; no llama-server was started by me (checked `pgrep -af llama-server` for my scratch path: none), no pacman, no tool installs.

## Paths written (all under `/home/vgpnk/Projects/shokunin/kama-shokunin/`)

- `.ufo/waves/round-49/w1/out/X1Selftest.md` (this report)
- `.ufo/waves/round-49/w1/out/X1Selftest/port-round49-cases.py`
- `.ufo/waves/round-49/w1/out/X1Selftest/port-round49-cases.log`
- `.ufo/waves/round-49/w1/out/X1Selftest/kama-llamacpp-live-438127bc.py` (frozen module under test)
- `.ufo/waves/round-49/w1/out/X1Selftest/witness-selftest-proposed.diff`
- `.ufo/waves/round-49/w1/out/X1Selftest/kama-live-replay-witness-selftest.py` (full patched text)
- `.ufo/waves/round-49/w1/out/X1Selftest/witness-mutant-a-drops-passthrough.diff`
- `.ufo/waves/round-49/w1/out/X1Selftest/witness-mutant-b-drops-timeout.diff`
- `.ufo/waves/round-49/w1/out/X1Selftest/selftest-patched-74558c71.log`
- `.ufo/waves/round-49/w1/out/X1Selftest/selftest-mutant-a-drops-passthrough.log`
- `.ufo/waves/round-49/w1/out/X1Selftest/selftest-mutant-b-drops-timeout.log`
- `.ufo/waves/round-49/w1/out/X1Selftest/optional-archive-too-many-members.diff`
- `.ufo/waves/round-49/w1/out/X1Selftest/optional-archive-too-many-members-mutant-drops-cap.diff`
- `.ufo/waves/round-49/w1/out/X1Selftest/live-selftest-baseline-74558c71.log`
- `.ufo/waves/round-49/w1/out/X1Selftest/live-selftest-optional-many-members.log`
- `.ufo/waves/round-49/w1/out/X1Selftest/live-selftest-optional-many-members-mutant.log`
