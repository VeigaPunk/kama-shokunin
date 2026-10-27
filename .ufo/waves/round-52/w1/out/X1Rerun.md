# X1Rerun — round 52, lane kama: independent C1 measurement (operability)

**Verdict: C1 reproduces independently and exactly — at build `5dacf2c7` the frozen counter reports `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True` (exit 0), at base `9ff76b1f` it reports `bind=1 sealed=0 teardown=1 newrow=0 bound=3/3 sealedruns=0/3 met=False` (exit 1); both outputs agree with the L1's `measured/c1-build.out` and `controls/base.c1.out` on every line once only the by-design variable fields are normalized. No defect found.**

## Setup (read-only lane, own clone)

    S=/fast/scratch/hyaku/kama-r52/X1Rerun; export TMPDIR="$S"
    git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane      # rc=0
    git -C $S/lane rev-parse --show-toplevel        -> /fast/scratch/hyaku/kama-r52/X1Rerun/lane
    git -C $S/lane rev-parse 5dacf2c7^{commit} 9ff76b1f^{commit}
      -> 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 / 9ff76b1f763512be2f554cbbfd0b2213b63b0847  rc=0

Frozen counter bytes verified against the preregistration before measuring (counter unchanged freeze → build, so the two runs use one instrument):

| check | value |
|---|---|
| `sha256sum kama-shokunin/tools/round52-replay-memfd-audit.py` | `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5` |
| `git show 8551ba7f:tools/round52-replay-memfd-audit.py \| sha256sum` | `053ff502…e1121f5` |
| `git show 5dacf2c7:tools/round52-replay-memfd-audit.py \| sha256sum` | `053ff502…e1121f5` |
| `preregistration.json` claims[0].`counter_sha256` | `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5` |

No tool installs, no pacman transaction (host guard respected), no service started by me outside the lane tools' own loopback servers.

## Run 1 — build tip `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`

    cd /home/vgpnk/Projects/shokunin/kama-shokunin
    python3 tools/round52-replay-memfd-audit.py --repo $S/lane \
      --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 \
      --scratch "$S/m-build" \
      --out kama-shokunin/.ufo/waves/round-52/w1/out/X1Rerun/c1-build.out   # rc=0, exit=0 appended

stdout (also the counter's `--out` bytes, stderr empty, 30.6 s wall):

```
tip=5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 323309 port 36547 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1023441104 recorded, nonce 'kama witness 1bd6c32c7bd2ff62' round-tripped
detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:160282 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: bind b2: pid 327645 port 37665 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 750672580 recorded, nonce 'kama witness e99b57ff99984afb' round-tripped
detail: sealed b2: running image '/memfd:llama-server (deleted)' 00:01:168509 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: bind b3: pid 330335 port 39763 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1006686073 recorded, nonce 'kama witness 5c7a2c27b48f0b0b' round-tripped
detail: sealed b3: running image '/memfd:llama-server (deleted)' 00:01:165675 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 1 rows new since base; 1 name memfd_create(2): ['| S500 |']
exit=0
```

## Run 2 — base tip `9ff76b1f763512be2f554cbbfd0b2213b63b0847`

    python3 tools/round52-replay-memfd-audit.py --repo $S/lane \
      --tip 9ff76b1f763512be2f554cbbfd0b2213b63b0847 \
      --scratch "$S/m-base" \
      --out .../w1/out/X1Rerun/c1-base.out                                    # rc=1, exit=1 appended

```
tip=9ff76b1f763512be2f554cbbfd0b2213b63b0847
bind=1 sealed=0 teardown=1 newrow=0 bound=3/3 sealedruns=0/3 met=False
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 353134 port 39225 … ok … mapping dev 103:05 inode 682298501 recorded, nonce 'kama witness dc641e62e12a2d18' round-tripped
detail: sealed b1: sealed: F_GET_SEALS on the running image failed: Invalid argument
detail: sealed b1: sealed: running image link '…/work-b1/server/llama-b11909/llama-server' is not an anonymous memfd
detail: sealed b1: sealed: running image has link count 1, not 0
detail: sealed b1: sealed: rerun server_exe {'dev': '103:05', 'inode': '1752616022', 'opened': True, 'path': '…/work-b1/server/llama-b11909/llama-server', 'sha256': '35ac50fb…d7ff0', 'size': 17864} does not record the observed sealed image ('103:05', '1752616022')
detail: sealed b1: sealed: replay own_server {'path': '…/work-b1/server/llama-b11909/llama-server', 'dev': '103:05', 'inode': '1752616022'} does not name the observed memfd
   (same five-line block for b2, b3)
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 0 rows new since base; 0 name memfd_create(2): []
exit=1
```

Exactly the do-nothing control shape the preregistration froze: the only legs that collapse at base are `sealed` (0/3) and `newrow` (0), while `bind` 3/3 and `teardown` still hold — so the build's delta is the memfd mechanism, not host capability (the same host passed memfd at build minutes later).

## Line-by-line agreement

Method: `compare-logs.py` (copy in the out dir) drops a leading `$ …` shell header line (L1's two reference files carry one; a `--out` receipt does not, which is the only raw-text difference) and normalizes only the fields listed under "differ by design" below; everything else must match character for character.

- `c1-build.out` vs `measured/c1-build.out`: **12/12 lines agree**, exit line `exit=0` both.
- `c1-base.out` vs `controls/base.c1.out`: **24/24 lines agree**, exit line `exit=1` both.

Must agree (and do):

| field | build (mine / L1) | base (mine / L1 control) |
|---|---|---|
| `tip=` | `5dacf2c7…90c8` / same | `9ff76b1f…b0847` / same |
| leg flags + counts | `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True` / same | `bind=1 sealed=0 teardown=1 newrow=0 bound=3/3 sealedruns=0/3 met=False` / same |
| counter vocabulary | `512 tokens` / same | `512 tokens` / same |
| bind verdict tokens (×3) | `exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode … recorded, nonce … round-tripped` / same | same / same |
| model mapping dev | `103:05` / same | `103:05` / same |
| sealed verdict (×3) | `running image '/memfd:llama-server (deleted)' 00:01:<ino> seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server` / same wording, same `00:01` dev, `seals 15`, same frozen digest | the same three failure texts per receipt (`F_GET_SEALS … Invalid argument`; `link … is not an anonymous memfd`; `link count 1, not 0`) plus `server_exe`/`own_server` not naming the memfd / same ordering and wording |
| `server_exe` dict in base | — | keys `dev,inode,opened,path,sha256,size`; `opened=True`, `sha256=35ac50fb…d7ff0` (frozen), `size=17864` / identical except inode/path |
| teardown | `3 descendants; after <T> s alive [] port refuses ok` / same | same / same |
| newrow | `1 rows new since base; 1 name memfd_create(2): ['| S500 |']` / same | `0 rows new since base; 0 name memfd_create(2): []` / same |
| exit | 0 / 0 | 1 / 1 |
| stderr (both runs) | empty | empty |

Differ by design (values, never verdicts — per-run instances):

| field | mine | L1's |
|---|---|---|
| server pids | 323309, 327645, 330335 / 353134, 356498, 359486 | 3033161, 3039647, 3045781 / 563321, 577618, 591754 |
| loopback ports | 36547, 37665, 39763 / 39225, 32795, 46101 | 45271, 41245, 38741 / 46167, 35981, 43693 |
| nonces | witness 1bd6c32c…, e99b57ff…, 5c7a2c27… | witness ad89cfc0…, 5f6026f9…, 1c5831ce… |
| memfd inodes (build) | 160282, 168509, 165675 | 155472, 152532, 140223 |
| extracted-tree inodes (base `server_exe`/`own_server`) | 1752616022, 1352602072, 19962144 | 1692755493, 881739242, 1620245009 |
| model mapping inodes | 1023441104, 750672580, 1006686073 | 10056, 550093473, 2080388728 |
| scratch/work paths | `…/X1Rerun/m-*/r52c1-*/work-b*/…` | `…/L1/meas-build/…`, `…/L1/c1base/…` |
| header line | none (`--out` bytes only) | `$ python3 tools/round52-replay-memfd-audit.py …` |

The constant `dev 00:01` on the sealed image is the memfd anonymous inode filesystem, and `dev 103:05` on the model mapping / base extracted tree is the filesystem holding the scratch — both stayed identical across all four runs; only the inode/pid/port/nonce instances moved.

## Notes (not defects)

1. The counter's own `sealed` leg (`tools/round52-replay-memfd-audit.py:361-395`) opens `/proc/<pid>/exe` itself and requires `/memfd:` link, `st_nlink == 0`, `F_GET_SEALS ⊇ 15` and the frozen digest; the rerun-receipt comparison (`:495-508`) requires `server_exe.opened/sha256/dev/inode/seals`. It does not itself re-assert `server_exe.nlink == 0` or the `/memfd:` path of the *receipt* field — those are enforced by the replay (`tools/kama-live-replay.py:429-437`), and a green `bind` requires the replay's `match is True` (`:479-483`), so the refused-run path is still closed transitively. This matches the frozen docstring; recorded for the ledger reader only.
2. `newrow` is a diff of `corpus/SOURCES.md` rows base→tip containing `man7.org/linux/man-pages/man2/memfd_create.2.html`; the single row is `corpus/SOURCES.md:253` (`| S500 |`).
3. The teardown timing (`after 0.10 s`) is a measured quantity, not an asserted one; both runs observed 0.10 s. Contract-relevant parts (`alive []`, `port refuses ok`, 3 descendants) agreed exactly.
4. The sealed build path is the one claimed: `kama-live-replay.py:222-256` fills a `memfd_create(…MFD_ALLOW_SEALING)` from the archive member stream, hashes it (`memfd-digest-mismatch` on drift), seals it (`F_ADD_SEALS 15`, re-read), and passes it as `--server-fd` with `pass_fds` (`:399-403`); `kama-llamacpp-live.py:1952-2005` validates it (`sealed_fd`, `:786-810`) and execs `executable=/proc/<live pid>/fd/N` with `argv[0]` the `--server` path, `LD_LIBRARY_PATH`/cwd in the install tree and an absolute model path; `server_exe` records `nlink`/`seals` (`:731-771`).

## Evidence retained (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X1Rerun/c1-build.out` — counter `--out` at `5dacf2c7` + `exit=0`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X1Rerun/c1-base.out` — counter `--out` at `9ff76b1f` + `exit=1`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X1Rerun/cmp-build-mine-vs-measured.txt` — 12/12 agreement, per-line
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X1Rerun/cmp-base-mine-vs-control.txt` — 24/24 agreement, per-line
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X1Rerun/compare-logs.py` — the normalizer (variable-field list only)

## Risks / limits

- Both runs share one host and one kernel; the counter's model (~1 MB) and server asset (~75 MB per replay) downloads were fetched fresh in each run and accepted by digest (`counter vocabulary: 512`, digest checks), so this is not a cached-artifact pass.
- The measurement is the frozen counter's; I did not build an independent memfd observer (the counter already opens `/proc/<pid>/exe` itself). No leg was re-run to "confirm" a failure; every verdict above is a single executed run.
- Nothing blocked; the only cross-seat observation is a live `kama-llamacpp-live.py` process under `/fast/scratch/hyaku/kama-r52/J5HostMemfd/` and another seat's `sha256sum` over install paths at the time of my `pgrep -af llama-server` — not mine, left untouched. No process referencing my scratch path remained (`pgrep -af 'kama-r52/X1Rerun'` → none), the counter removed its own temp trees, and every port it used was asserted refusing after exit.
- Scratch `/fast/scratch/hyaku/kama-r52/X1Rerun` (clone + work roots) removed after copying the above.
