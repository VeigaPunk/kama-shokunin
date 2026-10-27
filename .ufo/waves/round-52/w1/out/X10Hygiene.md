# X10Hygiene — round 52 end-of-wave hygiene (lane kama)

**Verdict: the wave's own footprint is clean** — `pgrep -af llama-server` empty (exit 1), `memfd:llama` count 0
across every `/proc/<pid>/fd`, zero files at the top of `/fast/scratch/hyaku/kama-r52`, no kama path in the
fleet status, `/fast` 587 G free — **and a clean battery**: five re-runs (C1, C2, hexrun, gate, digest) at
`5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` reproduce `measured/*-build.out` value for value, exit 0.
**One defect found at the build tip**: the committed receipt checker rejects every `--server-fd` receipt the
build's own producer emits (`met=True` is unaffected — C1's counter does not use that checker). The fix
exists only as an uncommitted working-tree edit. Four non-defect residuals are named below.

Snapshot 2026-10-27T02:22:35-03:00, host plazir27, kernel 7.2.11-arch1-1. Full detail, tables and every
command are in `w1/out/X10Hygiene/hygiene.md`; raw receipts in `w1/out/X10Hygiene/`.

## Battery read (23 `run` invocations in `measured/measure.sh`)

- `c1-build.out`: `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True`, exit 0. Sealed legs
  read `/memfd:llama-server (deleted)` with `seals 15` and the frozen digest `35ac50fb…7d8d7ff0`;
  teardown `invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`; `newrow` `| S500 |`.
- `c2-build.out`: `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`, exit 0.
- `gate` 50/0/0, `cap` 11/11 met, `r41` 36 facts / 0 mismatch, `r42` 0 mismatch / maxN=51, `r43` 50 registered /
  0 mismatch, `pointer` ok + 13 `measured: ok`, `digest` `ledger_bad=0 wrong_unflagged=0`, `hexrun`
  `ledger_bad=0 wrong_flagged=3`, `sao` `no append-only violations`, `aoa` `restored=67 unrestored=0
  regressed=0 vanished=0 bad_declarations=0`, `aoa-selftest` 51/0, `klr-selftest` 31/0, `cr-selftest` 16/107,
  `r48c2`/`r49c1`/`r50c1`/`r51c2` met, `cap` met — all exit 0.
- **The battery is not all-exit-0**: `r51c1-build.out` exits **1** (`own=0/3 met=False`) — the superseded
  round-51 path binding, failing by construction at a memfd tip. Expected; must not be read as a defect.
- `census-build.out` exit 0; its warning multiset is byte-identical to `census/start.out` (95 lines each,
  `diff` empty → `census-warn-delta.txt`, 0 B), so the build added no census warning.

## Five re-runs this seat made (clean `git clone --shared` at 5dacf2c7)

| command | exit | vs build receipt |
|---|---|---|
| `tools/round52-replay-memfd-audit.py --repo . --tip 5dacf2c7… --scratch …/c1` | 0 | `met=True`; identical after pid/port/inode/nonce normalization |
| `tools/round52-append-restore-check.py --repo . --tip 5dacf2c7… --scratch …/c2` | 0 | `met=True`; identical |
| `tools/hexrun-census.py scan --repo . --rev 5dacf2c7…` | 0 | identical |
| `tools/gate-registry-check.py --rev 5dacf2c7…` | 0 | identical |
| `tools/digest-ledger.py scan --repo . --rev 5dacf2c7…` | 0 | identical |

`rerun-vs-build.txt` shows the only remaining diff lines are the wrapper `$ …`/`exit=0` lines this seat added
and the abbreviated `--rev`. C1's teardown leg passed in this seat's run, and the (1)/(2) sweeps afterwards
show no server and no `memfd:llama`.

## The five required items

1. `pgrep -af llama-server` → no output, `exit=1`; `pgrep -x llama-server` → `exit=1`. Clean. (An earlier
   match was a path string in another agent's `xargs sha256sum ./… ./llama-server …`, not a server.)
2. `ls -l /proc/*/fd 2>/dev/null | grep -c 'memfd:llama'` → **0** (same over `/proc/[0-9]*/fd` → 0). Only the
   desktop stack's memfds exist (`shared-memory-region` 282, `wayland-cursor` 28, `pipewire-memfd` 13, …);
   no process runs a `/memfd:` executable.
3. `/fast/scratch/hyaku/kama-r52`: **4696 M in 15 dirs, 0 top-level files** —
   `M3Live 1076M, L1 464M, X7Regen/W3Mistakes/V5Review/Sim1/N1Overlap/M4Ctr/M1Ctr/L5Slice 385M each`.
   At 02:19 it was 10,313 M / 32 dirs (`J6RenameOver` 2290 M largest); this seat's 386 M was removed at
   02:22:35.
4. `git -C …/shokunin status --porcelain` → `?? btrfs-scrub@.service ?? dev-replace.c ?? kengaku-shokukin/
   ?? kstrtox.c ?? scrub.c ?? scrub237.c ?? sha256-live.txt ?? sysfs.c ?? systemd.kill.xml
   ?? tags-btrfs-progs.txt ?? tags-linux.txt ?? tags-systemd.txt ?? vsprintf.c`.
   At 02:16 it was only `?? kengaku-shokukin/`; the 12 plain files have mtimes 02:22:07–16 (created **during**
   this sweep) and are btrfs/systemd/kernel research material plus a `sha256sum` dump — **not kama files, not
   deleted**. `kengaku-shokukin/` is a **different campaign's** tree (its file
   `.ufo/waves/round-46/w1/R46CritC1Freeze.md` cites `plans/round-46-claims.md` and `a3w1` wave reports that
   exist only under it; the kama lane has no `plans/round-46-claims.md` and no `a3w*` dirs) and was mutating
   between my two listings. **No fleet-root file belongs to a kama seat.**
5. `git -C …/kama-shokunin status --porcelain` → `M corpus/QUALITY.md` (12+), `M corpus/SOURCES.md` (2+),
   `M tests/llamacpp-live/check-receipt.py` (24+/2-), `M tools/kama-live-replay.py` (48+/1-), plus the
   untracked round-52 wave dirs (`c1/`, `d3/`, `integration/`, `w1.ready*`, `w1/out/`). HEAD `34d82600` =
   build `5dacf2c7` + w1 spec. These four are the **L1's live integration** (S501/S502, KQ89–KQ93,
   M2Replay survivor checks — `.ufo/waves/round-52/integration/m2replay-survivors-killed.out`), captured
   read-only in `lane-status.txt`, `corpus-inflight.diff`, `kama-live-replay.diff`,
   `check-receipt-fd-mode.diff`. The `measured/*-k5.out` reruns present at 02:16 were removed by that
   integration at ~02:20 (not by this seat).

## Defect F1 — consumer rejects the producer's `--server-fd` receipts

At `5dacf2c7` (and unchanged at `34d82600`: `git diff --stat 5dacf2c7 HEAD -- tests/llamacpp-live/check-receipt.py tools/kama-llamacpp-live.py` is empty):

- `tools/kama-llamacpp-live.py:1957` puts `LD_LIBRARY_PATH` into `child_env` in `--server-fd` mode; `:1962`
  records it in `receipt['child_env_keys']` alongside `server.fd`.
- `tests/llamacpp-live/check-receipt.py:65` (`CHILD_ENV_ALLOWLIST = {"PATH","HOME","LANG","LC_ALL","TMPDIR"}`)
  and `:643` (`elif k not in CHILD_ENV_ALLOWLIST: bad(...)`) reject that name.

Command that shows it (real wave receipt, seat J3CopyDecoy's honest build):

```
$ python3 <5dacf2c7 copy of check-receipt.py> \
    .ufo/waves/round-52/w1/out/J3CopyDecoy/j3-rerun-receipt-honest-build.json --require-schema v5
INVALID …: 1 problem(s)
  - child_env_keys element is outside the allowlist PATH/HOME/LANG/LC_ALL/TMPDIR
exit=1
$ python3 <lane working-tree copy> <same receipt> --require-schema v5
VALID …; exit=0
```

Impact: C1's `met=True` is unaffected (the counter never calls the checker), but the lane cannot certify any
`--server-fd` receipt with its own validator at the build tip; `cr-selftest`'s `16 VALID / 107 mutations`
count does not cover the new mode.

Proposed fix (already present as an uncommitted working-tree edit; full text in
`w1/out/X10Hygiene/check-receipt-fd-mode.diff`): admit `LD_LIBRARY_PATH` **only** when `server.fd` is
recorded — constant at `:69` (`CHILD_ENV_FD_MODE = {"LD_LIBRARY_PATH"}`), union at `:644`, plus one VALID
case at `:2043` and one mutation (`ld-library-path-without-fd`) at `:2044`. Land it **with** the producer
(the in-flight `corpus/QUALITY.md` row `KQ93` says exactly this) and re-take
`measured/cr-selftest-*.out` (totals move off 16/107). Note the edit is unattributed:
`w1/out/V2Review.md:9` says "Proposed fix (not applied)" (mtime 02:11) while the file changed at 02:14.

## Residuals (reported, not fixed — outside this seat)

- **F2 state**: `tools/kama-live-replay.py` has already grown 48 lines past the build (MFD_EXEC + `EINVAL`
  fallback at `:238-243`, sealed-bytes re-digest, new selftest cases). Counters read the tip **commit**
  (`round52-replay-memfd-audit.py:594` `git archive`), so build receipts stay attributable to `5dacf2c7`,
  but **C1 must be re-measured once integration lands** — the cached receipt describes the old tool.
  Host has `vm.memfd_noexec = 0`, so MFD_EXEC is portability, not a precondition of today's `met=True`.
- **F3 leftover processes**: two orphaned round-49 stubs, `2553430` and `2608023` (PPID 1494, 5 h 45 m,
  0.0 % CPU, one socket each, stdout to deleted `kama-r49/M1Ctr/…/w1.log`). Not `llama-server`, not round 52;
  not killed by this seat (no service control), to be reaped with the round-49 scratch.
- **F4 foreign fleet-root writes**: the 12 files and `kengaku-shokukin/` in item 4, written 02:22:07–16 and
  still changing. Named only.
- **F5 jj**: `jj -R <lane> status` reports `D` 3,727 paths (rounds 36–43 `.ufo` artifacts), `M` 4, `?` 121,
  yet every sampled path exists on disk and git is clean for it (`git ls-files .ufo/waves/round-36/assimilation`
  = 278; `git status` on that path empty), and the same paths are also listed as untracked — internally
  contradictory. Both invocations ran from a cwd outside the workspace, so this is most likely an artifact of
  that invocation [INFERENCE]: **ignore it** (`jj-status-summary.txt`) and have the L1 run its own
  `jj status` from inside the lane before any jj-based integration. **Disclosure**: `jj status`
  auto-snapshots the working copy (`.jj/working_copy` mtime 02:18) — the only lane state this seat touched;
  no jj/git mutation followed, and the lane/fleet files were otherwise read-only.

## Limits
No build/lint/test/formatter beyond the five battery re-runs plus the one receipt validation used as F1's
evidence. No tool installed (nothing needed; `pacman` untouched per the pause). Network only as the counters
themselves use it (~75 MB b11909 archive + ~1 MB model from github.com/huggingface.co). Every llama-server
raised was raised by C1 on loopback and torn down by C1's own leg; the (1)/(2) sweeps confirm none survives.

## Absolute paths written
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/hygiene.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/hygiene-sweep.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/c1-rerun.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/c2-rerun.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/hexrun-rerun.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/gate-rerun.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/digest-rerun.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/rerun-vs-build.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/build-vs-k5.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/census-warn-delta.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/lane-status.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/check-receipt-fd-mode.diff
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/kama-live-replay.diff
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/corpus-inflight.diff
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X10Hygiene/jj-status-summary.txt
