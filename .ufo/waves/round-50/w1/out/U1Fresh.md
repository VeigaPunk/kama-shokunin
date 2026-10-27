U1Fresh — C1 counter fresh-session operability: VERDICT PASS on the frozen environment (xfs scratch): 2/2 back-to-back runs met=True at 97c864bead3ee4a2f629574e77263d33834ec98a, ~15.5 s wall each, teardown 0.10 s, zero surviving processes; on a btrfs scratch it fails closed exactly as the frozen limit predicts (bind=0/3, met=False) because /proc/<pid>/maps shows dev 00:1e where stat() of the same pathname+inode shows 00:38 — and the new model_mapping layer independently refuses the same way (replay exit 1, mapped=False).

# Scope
Seat U1Fresh, lane kama round 50, claim C1 (operability). Fresh-session runs of
`tools/round50-replay-bind-audit.py` (frozen sha256 `ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89`,
verified against `preregistration.json` claim C1 `counter_sha256` — match).
Measured commit `97c864bead3ee4a2f629574e77263d33834ec98a` (object verified present
in the clone via `git cat-file -t` → `commit`). Lane clone:
`git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (HEAD
3b79eaddf38246c637cc7ba1a94ab363422876b6; the counter measures `--tip` via
`git archive`, so HEAD is irrelevant). Counter run read-only; all writes under my
scratch `/fast/scratch/hyaku/kama-r50/U1Fresh/` (xfs) and, for run 3,
`/home/vgpnk/u1fresh-btrfs-scratch/` (btrfs, `/dev/mapper/root`).

# Commands and results

Runs (all three identical apart from `--scratch` and `--out`):
```
TMPDIR=$S python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round50-replay-bind-audit.py \
  --repo $S/lane --tip 97c864bead3ee4a2f629574e77263d33834ec98a \
  --scratch <dir> --out <receipt>
```
Run 1 scratch `$S/run1` (xfs), run 2 scratch `$S/run2` (xfs), run 3 scratch
`/home/vgpnk/u1fresh-btrfs-scratch` (btrfs). A companion watcher
(`watch.py`, in the out dir) polled the scratch root at 200 ms: ready.json /
release mtimes, /proc births+deaths of replay/tool/server processes, the
.gguf maps line + stat() of each llama-server, and `du -sb` of the scratch root.

| run | fs    | verdict line                                        | exit | wall   | teardown (counter) |
|-----|-------|------------------------------------------------------|------|--------|--------------------|
| 1   | xfs   | `bind=1 teardown=1 newrow=1 bound=3/3 met=True`      | 0    | 15.76 s| 0.10 s             |
| 2   | xfs   | `bind=1 teardown=1 newrow=1 bound=3/3 met=True`      | 0    | 15.21 s| 0.10 s             |
| 3   | btrfs | `bind=0 teardown=1 newrow=1 bound=0/3 met=False`     | 1    | 15.44 s| 0.10 s             |

Receipts: `c1-run1-xfs.out`, `c1-run2-xfs.out`, `c1-run3-btrfs.out`.
Watcher logs: `watch-run1-xfs.json`, `watch-run2-xfs.json`, `watch-run3-btrfs.json`.

Wall times are much lower than the ~46 s L1 dry-run figure: the ~75 MB GitHub
asset + ~1 MB HF model download was fast this session (downloads are the dominant
cost; READY_WAIT is 600 s so slower networks just extend the run).

## Witness windows (watcher, 200 ms poll; offset = s since watcher start)

Run 1 (xfs): b1 ready 6.52 → release 6.88 → server dead 6.93; b2 server born 9.08 →
release 9.38 → dead 9.46; b3 server born 11.96 → release 12.27 → dead 12.34.
teardown leg: server maps seen 14.89 → invoker+replay+tool+server all dead 15.26
(≤0.4 s end-to-end; counter's own measure 0.10 s).
Run 2 (xfs): b1 ready 6.27 → release 6.61 → dead 6.67; b2 ready 8.96 → release
9.30 → dead 9.35; b3 server born 11.70 → release 11.98 → dead 12.04.
teardown leg: server maps 14.38 → tree dead 14.72 (≤0.35 s; counter 0.10 s).
Each bind-leg hold (ready → release) is ~0.3–0.4 s: the counter's whole
exe/listen/nonce/tree/env/mapped witness completes in that window; exit to dead
≤ ~0.4 s. `ready.json` for b2/b3 in run 1 and b3 in run 2 was created and read
between poll ticks; server birth/release/death timestamps bound the windows.

## Network / disk bytes (du)

du peak of the scratch root while running: run 1 = 624,283,960 B (595.4 MiB),
run 2 = 624,312,721 B, run 3 = 624,283,574 B — reproducible within ~29 KB.
Composition (from the counter source): the extracted `git archive` tree, the
counter's own model download (~1 MB, verified sha256), and four replay legs each
in a fresh `work-<tag>` dir, each downloading the ~75 MB b11909 server asset
(extract included) plus the ~1 MB model — so ≈4×76 MB of downloads plus extracted
artifacts coexist near the peak; du is apparent bytes written to scratch, an
upper bound on network bytes and a floor on total download volume. The counter
`rmtree`s its mkdtemp on exit (verified: run dirs empty afterwards; `du_last=0`
at watch end).

## Leftover processes

After run 1: `pgrep -f llama-server` showed sibling seats' servers only
(X11ModelSwap's live replay, J4Decoy/J2NoPdeathsig/R1Rerun2/S2Gate2 counters
mid-flight on this shared host) — every PID whose cmdline named my scratch or
clone was gone (`pgrep -af U1Fresh` → none besides the watcher, which exits
on the stop flag). After run 2 and at final check: `pgrep -f llama-server` →
empty globally; `pgrep -af 'U1Fresh|u1fresh-btrfs'` → none. The teardown leg's
SIGKILL of the invoker took replay+live tool+server down within the counter's
0.10 s in all three runs — pdeathsig chain works on both filesystems.

## btrfs vs xfs — the maps dev/inode difference (the one real difference)

xfs (`/dev/nvme1n1p2`): maps line `7fc21000e000-... r--s 00003000 103:05 1755625687
.../work-b1/download/stories260K.gguf`; stat of the same pathname →
`st_dev 103:05 st_ino 1755625687` — dev+inode agree, sha256 == frozen model,
`mapped` check passes, bind 3/3.

btrfs (`/dev/mapper/root`, `/home/vgpnk` st_dev `00:38` / decimal 56):
maps line `7f69a4606000-... r--s 00003000 00:1e 238299543
.../work-b1/download/stories260K.gguf`; stat of the same pathname →
`st_dev 00:38 st_ino 238299543`. The inode is identical; the dev column is not —
/proc maps reports the mount's anonymous dev (major:minor `00:1e`, i.e. the
file-handle/subvolume pair seen at mount time) while `stat()` reports `00:38`
(decimal 56, the `st_dev` of `/home`). `stat -c %d /home/vgpnk` = 56 and
`/fast/scratch` = 66309 (0x10305 = `103:05`), consistent with the maps values.

Consequence, exactly the frozen limit (`preregistration.json` limits[1]):
`mapped_model()` (counter, tools/round50-replay-bind-audit.py:328-338) rejects the
candidate on the dev compare → `bind b1: no mapping of pid 4065398 is a file
hashing to the frozen model (24 file mappings)` for all three receipts →
`bind=0 bound=0/3 met=False`, exit 1. It fails closed, not open: it cannot bind
the model on btrfs rather than binding the wrong file.

Independently — and this is the C1 build working as claimed — the replay itself
refused the rerun on btrfs: `replay exit 1 match False` with
`model_mapping {'dev': '00:1e', 'inode': '238299543', 'mapped': False,
'path_dev': '00:38', 'reason': 'mapped-file-is-not-the-model-path'}` — the live
tool recorded the maps-side dev/inode (00:1e/238299543), compared it to a stat of
the pathname (00:38), and declined to claim a mapping it could not verify. Two
independent layers agree on the same dev discrepancy and both fail closed.
teardown and newrow legs are fs-insensitive (`teardown=1 newrow=1` on btrfs too).

Note for the record: the limit's parenthetical says "btrfs subvolumes"; observed
here on the plain /home subvolume the maps dev (00:1e) differs from stat st_dev
(00:38) — consistent with "filesystems whose maps dev differs from stat st_dev",
no wording change needed.

# Findings

- No defect in the counter: repeatability confirmed (identical verdicts, stable
  du within 29 KB), teardown ≤0.4 s externally / 0.10 s internally, no process or
  file leakage, fail-closed on a filesystem it cannot verify.
- Minor observation (not a defect): the frozen limit's example filesystem is
  btrfs subvolumes; the observed mechanism on /home is maps-side dev `00:1e` vs
  stat-side `00:38` with identical inode — i.e., the discrepancy is real even
  without creating a nested subvolume. The limit covers it verbatim.
- Cross-seat noise: the shared host runs many siblings' counters concurrently;
  watcher logs include foreign processes (kept in the JSONs, filtered in this
  report). Committed `ready.json` files inside the archived lane tree also
  appear as watcher events — artifacts of the archive extract, not live servers.
- Tooling installs: none (no installs or upgrades performed).

# Cleanup

`rm -rf /fast/scratch/hyaku/kama-r50/U1Fresh` and the btrfs scratch dir removed
after copying every cited artifact to the out dir. No commits, no lane writes
outside this report + out dir, no services started by me (all llama-server
processes were spawned by the counter inside its sandbox and are gone).

Report: .ufo/waves/round-50/w1/out/U1Fresh.md
