# End-of-wave hygiene — round 52, lane kama (X10Hygiene)

Verdict: **the wave's own process/memfd/scratch footprint is clean** (`pgrep -af llama-server` empty,
`memfd:llama` count 0, no file at the top of `/fast/scratch/hyaku/kama-r52`, no kama path in the fleet
status), **with five named residuals**: (F1) the build tip's consumer rejects every `--server-fd` receipt
its own producer emits, (F2) four tracked lane files are uncommitted as the L1 integrates live, (F3) two
orphaned round-49 stub processes are still holding sockets, (F4) an untracked sibling-campaign tree plus 12
kernel/btrfs files appeared at the fleet root during the sweep, and (F5) the lane's jj working copy reports a
3,727-path deletion set that the disk and git both contradict (most likely an artifact of this seat's own
`jj` invocation from outside the workspace).

Snapshot: **2026-10-27T02:22:35-03:00**, host `plazir27`, kernel `7.2.11-arch1-1`.
All commands below were run from this seat's scratch (`/fast/scratch/hyaku/kama-r52/X10Hygiene`, removed at
02:22:35) against a `git clone --shared` of the lane checked out at the build tip
`5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`. Nothing in the lane or the fleet repo was written, staged,
committed or deleted by this seat.

## A. Read of the measured battery

`measured/measure.sh` has **23 `run` invocations**; at 02:16 there were 23 `*-build.out` receipts and 23
`*-k5.out` reruns; at 02:22 only the `*-build.out` receipts remain (the `*-k5.out` files were removed by
the integration running in the lane; see F2).

| receipt | verdict line | exit |
|---|---|---|
| `c1-build.out` | `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True` | 0 |
| `c2-build.out` | `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True` | 0 |
| `gate-build.out` | `registered 50 unregistered 0 defective 0` | 0 |
| `cap-build.out` | `listed 11 observed 11 missing 0 unsubstantiated 0 met True` | 0 |
| `r41-build.out` | `axes=6 facts=36 ... mismatches=0 met=True` | 0 |
| `r42-build.out` | `... mismatches=0 maxN=51 met=True` | 0 |
| `r43-build.out` | `unreg=0 defect=0 flags=0 pins=0 ... registered=50 mismatches=0 met=True` | 0 |
| `pointer-build.out` | `pointer: ok (### Planned (round 52) ...)` + 13 `measured: ok` | 0 |
| `digest-build.out` | `tokens=134 blob=119 external_ok=8 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` | 0 |
| `hexrun-build.out` | `tokens=1930 distinct=333 lane_oid=223 md5_blob=1 upstream_ok=97 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0` | 0 |
| `sao-build.out` | `added S500 (allowed)` / `no append-only violations` | 0 |
| `aoa-build.out` | `summary commits=350 files=99 events=109 restored=67 partial=0 unrestored=0 ungraded=37 disclosed=5 permitted_lines=58 disclosed_lines=10 bad_disclosures=0 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0` | 0 |
| `aoa-selftest-build.out` | `AOA_SELFTEST pass=51 fail=0` | 0 |
| `klr-selftest-build.out` | `KLR_SELFTEST pass=31 fail=0` | 0 |
| `live-selftest-build.out` | `selftest: ok; closed tcp6 listeners ::1:37031, ::ffff:127.0.0.1:42375` | 0 |
| `cr-selftest-build.out` | `selftest: 16 VALID and 1 NOT-EVALUATED receipts accepted; 107 mutations + unreadable case rejected` | 0 |
| `tally-build.out` | rounds 40-47 table, no `met` line (historical tool, `rounds=40-47`) | 0 |
| `r48c2-build.out` | `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True` | 0 |
| `r49c1-build.out` | `witness=1 cap=1 newrow=1 witnessed=3/3 met=True` | 0 |
| `r50c1-build.out` | `bind=1 teardown=1 newrow=1 bound=3/3 met=True` | 0 |
| `r51c1-build.out` | `bind=1 own=0 teardown=1 newrow=1 bound=3/3 owned=0/3 met=False` | **1** |
| `r51c2-build.out` | `fixture=1 lane=1 scenarios=9/9 lost=10 disclosed=10 met=True` | 0 |
| `census-build.out` | warnings `W01×1, W04×94` then `kama ok .../corpus/SOURCES.md` | 0 |

- `r51c1` is the only non-zero exit, and it is the **superseded** round-51 path binding: at the round-52 tip
  the replay's own server is a memfd, so `own` measures 0/3 by construction (the assigned supersession).
  A reader must not take "battery clean" to mean "every receipt exits 0".
- Census: the build's warning multiset is **identical to the round-52 start census** —
  `diff <(grep W0 census/start.out|sort) <(grep W0 measured/census-build.out|sort)` is empty (95 lines each,
  saved as `census-warn-delta.txt`, 0 bytes). `S499` duplicate-url and the `W01 tierC` line are pre-existing.
- `cr-selftest-build.out` (16 VALID / 107 mutations) is the **committed** checker's count; F1 shows why that
  number does not cover the receipts this build's replay emits.

## B. Re-runs this seat made (five, on a clean clone of the lane at 5dacf2c7)

| # | command (cwd = clone) | exit | result vs `measured/*-build.out` |
|---|---|---|---|
| 1 | `python3 tools/round52-replay-memfd-audit.py --repo . --tip 5dacf2c7... --scratch <S>/c1` | 0 | `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True`; byte-identical after normalizing pid/port/inode/nonce |
| 2 | `python3 tools/round52-append-restore-check.py --repo . --tip 5dacf2c7... --scratch <S>/c2` | 0 | `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`; byte-identical after normalization |
| 3 | `python3 tools/hexrun-census.py scan --repo . --rev 5dacf2c7...` | 0 | identical (`tokens=1930 distinct=333 ... ledger_bad=0`) |
| 4 | `python3 tools/gate-registry-check.py --rev 5dacf2c7...` | 0 | identical (`registered 50 unregistered 0 defective 0`) |
| 5 | `python3 tools/digest-ledger.py scan --repo . --rev 5dacf2c7...` | 0 | identical (`tokens=134 ... ledger_bad=0`) |

C1's own teardown leg passed in this seat's run: `invoker SIGKILLed with 3 descendants; after 0.10 s alive []
port refuses ok`; the three sealed legs read `/memfd:llama-server (deleted)` with `seals 15` and the frozen
digest `35ac50fb...7d8d7ff0`, and `newrow` found `| S500 |`. Receipts:
`c1-rerun.out`, `c2-rerun.out`, `hexrun-rerun.out`, `gate-rerun.out`, `digest-rerun.out`,
`rerun-vs-build.txt` in this directory. The only diff lines left are the wrapper `$ …` / `exit=0` lines this
seat added and the abbreviated `--rev 5dacf2c7` echo; every measured value is unchanged.

## C. The five required items

### (1) `pgrep -af llama-server`
```
$ pgrep -af llama-server      → (no output) exit=1
$ pgrep -x llama-server       → (no output) exit=1
```
Clean. One earlier sweep hit `sha256sum ./… ./llama-server …` (a path string in another agent's checksum
command line), not a server; `pgrep -x` and `ps -eo comm` confirm nothing named `llama-server` runs.

### (2) leftover memfds
```
$ ls -l /proc/*/fd 2>/dev/null | grep -c 'memfd:llama'      → 0
$ ls -l /proc/[0-9]*/fd 2>/dev/null | grep -c 'memfd:llama' → 0
```
No `memfd:llama*` anywhere. The only memfds on the host are the desktop stack's
(`shared-memory-region` 282, `wayland-cursor` 28, `pipewire-memfd` 13, `smithay-client-toolkit` 6,
`pulseaudio` 4, `dbus-broker-log` 2, `gdk-wayland`, `lp_dma_buf`, `allocation`). No process has a
`/memfd:` executable (`readlink /proc/*/exe` sweep: none).

### (3) `/fast/scratch/hyaku/kama-r52`
```
1076M  M3Live      464M  L1          385M  X7Regen    385M  W3Mistakes
 385M  V5Review   385M  Sim1        385M  N1Overlap  385M  M4Ctr
 385M  M1Ctr      385M  L5Slice
total 4696M in 15 dirs; 0 files at the top level; /fast has 587G free (28% used)
```
At 02:19 the same tree was 10,313M in 32 dirs (largest `J6RenameOver` 2290M); seats freed it as they
finished. This seat's 386M was removed at 02:22:35. No scratch directory outside a seat's own name exists.

### (4) `git -C /home/vgpnk/Projects/shokunin status --porcelain`
```
?? btrfs-scrub@.service   ?? dev-replace.c   ?? kengaku-shokukin/   ?? kstrtox.c
?? scrub.c   ?? scrub237.c   ?? sha256-live.txt   ?? sysfs.c
?? systemd.kill.xml   ?? tags-btrfs-progs.txt   ?? tags-linux.txt   ?? tags-systemd.txt
?? vsprintf.c
```
At 02:16 this was only `?? kengaku-shokukin/`. The 12 plain files appeared between 02:22:07 and 02:22:16
(mtimes), i.e. **during this sweep**: btrfs/systemd/kernel research material (`scrub.c`, `scrub237.c`,
`dev-replace.c`, `sysfs.c`, `vsprintf.c`, `kstrtox.c`, `systemd.kill.xml`, `btrfs-scrub@.service`, three
`tags-*.txt`) and `sha256-live.txt` (628 B, matching the concurrent `xargs sha256sum` over a PATH dir).
They are **not kama files** and were not deleted. `kengaku-shokukin/` is a **different campaign's** tree, not
the kama lane: its only file now is `.ufo/waves/round-46/w1/R46CritC1Freeze.md`, which cites
`plans/round-46-claims.md` and `R45HoSymlinks.md`/`R45HoIncludeIf.md` wave paths (`a3w1`) that exist only
under `kengaku-shokukin` — the kama lane has no `plans/round-46-claims.md` and no `a3w*` wave dirs. The tree
was mutating under my checks (a `plans/` and a `round-45/a3w1/` set appeared and vanished within a minute),
so treat it as an active foreign workspace. **No fleet-root path belongs to a kama seat at 02:22:35.**

### (5) `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain`
```
 M corpus/QUALITY.md                       (12 +)
 M corpus/SOURCES.md                       (2 +)
 M tests/llamacpp-live/check-receipt.py    (24 +, 2 -)
 M tools/kama-live-replay.py               (48 +, 1 -)
?? .ufo/waves/round-52/c1/F_GET_SEALS.2const.txt   ?? .ufo/waves/round-52/c1/mfd_noexec.txt
?? .ufo/waves/round-52/d3/   ?? .ufo/waves/round-52/integration/
?? .ufo/waves/round-52/w1.ready   ?? .ufo/waves/round-52/w1.ready.dispatched
?? .ufo/waves/round-52/w1/out/    (95 seat entries)
```
HEAD is `34d82600` (build `5dacf2c7` + the w1 spec commit). The four modifications are the **live
integration**: `corpus/SOURCES.md` adds `S501`/`S502`, `corpus/QUALITY.md` adds `KQ89`–`KQ93`,
`tools/kama-live-replay.py` grows beyond the build's file (mtime 02:19:18) and gains seat-M2Replay survivor
checks (`.ufo/waves/round-52/integration/m2replay-survivors-killed.out`), and `tests/llamacpp-live/check-receipt.py`
(mtime 02:14:17) admits the fd-mode environment name. Diffs saved as `lane-status.txt`,
`corpus-inflight.diff`, `kama-live-replay.diff`, `check-receipt-fd-mode.diff`. **Nothing was staged,
committed or reverted by this seat.**

## D. Findings

### F1 (defect at the build tip) — the committed consumer rejects every receipt the build's producer emits
At `5dacf2c7` (and unchanged at `34d82600`: `git -C <clone> diff --stat 5dacf2c7 HEAD -- tests/llamacpp-live/check-receipt.py tools/kama-llamacpp-live.py` is empty):
- producer `tools/kama-llamacpp-live.py:1957` sets `child_env['LD_LIBRARY_PATH']` in `--server-fd` mode and
  `:1962` records `receipt['child_env_keys'] = sorted(child_env)`; the commit's own `c2`/C1 receipts carry
  that name (`server.fd` present).
- consumer `tests/llamacpp-live/check-receipt.py:65` allows only `PATH/HOME/LANG/LC_ALL/TMPDIR`, and `:643`
  rejects anything else.

Reproduced on a real wave receipt (seat J3CopyDecoy's honest-build rerun):
```
$ python3 <committed 5dacf2c7 copy of check-receipt.py> \
    .ufo/waves/round-52/w1/out/J3CopyDecoy/j3-rerun-receipt-honest-build.json --require-schema v5
INVALID …: 1 problem(s)
  - child_env_keys element is outside the allowlist PATH/HOME/LANG/LC_ALL/TMPDIR
exit=1
$ python3 <lane working-tree check-receipt.py> <same receipt> --require-schema v5
VALID …; exit=0
```
Proposed fix: **land the working-tree change together with the producer** — it is exactly
`w1/out/X10Hygiene/check-receipt-fd-mode.diff` (comment at `:66-69`, `allowed` union at `:644`, one VALID
case `fd-mode-ld-library-path-valid` at `:2043` and one mutation `ld-library-path-without-fd` at `:2044`,
so the selftest totals move off 16/107). The in-flight `corpus/QUALITY.md` row `KQ93` already states the rule
("a producer change … lands together with the consumer that validates them"); integration must not land the
producer without it, and `cr-selftest-build.out` must be re-taken after it lands. Note the edit is
**unattributed**: `w1/out/V2Review.md:9` says "Proposed fix (not applied)" (report mtime 02:11:13) while the
file was modified at 02:14:17; the L1 should record who applied it.

### F2 (state, not a defect) — the lane is being integrated while the wave is measured
Four tracked files are uncommitted (item 5). Two consequences worth stating:
- The claim counters materialize their tree from the tip **commit**
  (`tools/round52-replay-memfd-audit.py:594` `git archive --format=tar <tip>`), and `measure.sh` clones the
  repo, so a dirty worktree cannot leak into a receipt — the build receipts stay attributable to
  `5dacf2c7`. This seat's reruns used a clean clone for the same reason.
- But the *measurement* is only reproducible while the tools stay at `5dacf2c7`. `tools/kama-live-replay.py`
  has already grown (48 added lines: `MFD_EXEC` with an `EINVAL` fallback at `:238-243`, a re-read digest
  check of the sealed memfd, new selftest cases), so after integration lands, C1 must be re-measured at the
  new tip; the cached `c1-build.out` no longer describes the tool that will be committed. The round-52
  `*-k5.out` reruns that could have shown this drift were removed from `measured/` at ~02:20.
- `vm.memfd_noexec = 0` on this host, so the `MFD_EXEC` change is portability (policy 1/2), not a
  precondition of the `met=True` measured here.

### F3 (environment leftover, not this wave) — two orphaned round-49 stubs
```
2553430  1494  05:45:43  python3 /fast/scratch/hyaku/kama-r49/M1Ctr/r49c1-k_sicwpn/work-w1/stub.py …
2608023  1494  05:45:04  python3 /fast/scratch/hyaku/kama-r49/M1Ctr/r49c1-tj8m881o/work-w1/stub.py …
```
Both are round-49 witnesses, 0.0 % CPU, one socket each, stdout/stderr to now-deleted `w1.log` files under
round-49 scratch. They are not `llama-server` and not round-52; this seat did not kill them (no service
control). Whoever reaps round-49 scratch should take them, or they will outlive the round.

### F4 (foreign writes at the fleet root) — named, not touched
The 12 files and `kengaku-shokukin/` in item (4), created/mutated 02:22:07-16 and continuously changing.
None is a kama artifact. They sit at the fleet root, which every seat spec forbids writing; the L1 may want
to tell their owner, but they are not round-52's to clean.

### F5 (jj) — a 3,727-path deletion set that disk and git contradict; unreliable, do not act on it
`jj -R <lane> status` (run twice from outside the workspace) reports `D` 3,727 paths, `M` 4, `?` 121.
The `D` set spans rounds 36-43 `w*.`/`c*`/`assimilation` artifacts, yet every sampled path is **present on
disk** and git is clean for them (`git ls-files .ufo/waves/round-36/assimilation` = 278, `git status` on the
same path empty) — and the same paths are also listed as untracked in the same output, which is internally
contradictory. Both invocations used a cwd outside the lane workspace; the most plausible reading is an
artifact of that invocation, not a lane condition [INFERENCE]. **Disclosure**: the seat spec says never
mutate the lane's jj state, and `jj status` auto-snapshots the working copy (`.jj/working_copy` mtime moved
to 02:18); that is the only state this seat touched, and no jj/git mutation followed. The L1 should run its
own `jj status` **from inside the lane** before any jj-based integration and ignore this summary
(`jj-status-summary.txt`).

## E. Not done / limits
- No build, lint, test or formatter run other than the five battery re-runs and one receipt validation used
  as F1's evidence (per seat scope; the parent owns the gate).
- No tool installed (nothing needed); `pacman` untouched per the host-wide pause.
- No network access beyond what the counters themselves do (C1 downloads the ~75 MB b11909 archive and the
  1 MB model from github.com/huggingface.co).
- Nothing was started except the three llama-servers each C1 run raises on loopback; C1's own teardown leg
  and the (1)/(2) sweeps confirm they are gone.
- The lane, the fleet repo and `kengaku-shokukin`/foreign files are untouched.
