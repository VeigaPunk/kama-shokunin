# J2Unsealed — Round 52 C1 ablation (unsealed memfd): the counter catches it, and the seal is load-bearing

**Verdict:** dropping `F_ADD_SEALS` makes the frozen C1 counter report `sealed=0 met=False` (build control `met=True`) while the replay itself still says match, and a standalone probe shows an unsealed memfd's running image **can** be rewritten and truncated through a descriptor held across the exec — ETXTBSY blocks only *fresh* opens, so `F_SEAL_WRITE` is not redundant with exec's deny-write.

## Inputs and integrity

| Item | Value |
|---|---|
| Lane (read-only) | `/home/vgpnk/Projects/shokunin/kama-shokunin` |
| Clone (fixture) | `$S/lane` = `/fast/scratch/hyaku/kama-r52/J2Unsealed/lane`, `git clone --shared`, `git rev-parse --show-toplevel` verified equal before the commit |
| Build | `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` (ablation's parent, by construction) |
| Ablation commit | `adc00bf5ef32833b89ce8cf8a71f2c2886aad55b` (`git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit`) |
| Frozen counter | `tools/round52-replay-memfd-audit.py` sha256 `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5` == preregistration `claims[0].counter_sha256`. Not edited. |
| Kernel | `7.2.11-arch1-1` |

The ablation is 2 files, 5 insertions / 9 deletions (`ablation-adc00bf5.diff`):
- `tools/kama-live-replay.py:247` — `F_ADD_SEALS` and the `memfd-not-sealed` refusal removed (`seals = fcntl.fcntl(fd, F_GET_SEALS)` only).
- `tools/kama-live-replay.py:432` — the `server-exe:not-sealed-memfd` (seals/nlink//memfd:) `elif` replaced by a comment.
- `tools/kama-llamacpp-live.py:796` — `sealed_fd()` accepts `seals 0` (`if not stat.S_ISREG(st.st_mode) or seals is None:`).

## Frozen counter runs (harness works in both directions)

```
$ python3 .../round52-replay-memfd-audit.py --repo $S/lane --tip 5dacf2c7… --scratch $S/c1ctl      # exit 0
bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True
detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:184376 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server

$ python3 .../round52-replay-memfd-audit.py --repo $S/lane --tip adc00bf5e… --scratch $S/c1abl2     # exit 1
bind=1 sealed=0 teardown=1 newrow=1 bound=3/3 sealedruns=0/3 met=False
detail: sealed b1: sealed: running image seals 0 lack some of 15
detail: sealed b1: sealed: rerun server_exe {'dev': '00:01', 'inode': '174282', 'nlink': 0, 'opened': True, 'path': '/memfd:llama-server (deleted)', 'seals': 0, 'sha256': '35ac50fb…d7ff0', 'size': 17864} does not record the observed sealed image ('00:01', '174282')
```
(same pair of `sealed` detail lines for b2, b3; receipts in `c1-build-control.out`, `c1-ablation-adc00bf5.out`)

Readings:
- **The counter catches it twice, independently**: its own `F_GET_SEALS` on `/proc/<pid>/exe` (`round52-replay-memfd-audit.py:388-389`) and the rerun receipt's `server_exe.seals` conjunct (`:502-503`). All three receipts fail both.
- **Only the seal conjunct fails.** Everything else that identifies the image is unchanged under the ablation: `'/memfd:llama-server (deleted)'`, `nlink 0`, the frozen digest, and (from the counter's own observation) the *same* dev/inode it reports. `bind=1 teardown=1 newrow=1` ⇒ the ablation is isolated to the `sealed` leg, not to endpoints, provenance, teardown, or the S500 source row.
- **The loosened lane code judges itself clean.** `bind=1` is only possible if the replay exited 0 with `match` true (`:484-486` appends `replay exit … match …` to the bind problems otherwise); the ablation's replay accepted seals 0 and returned no mismatch. So the property is carried by the frozen counter alone, exactly as the round asserted.
- Endpoints are unaffected: tokenize/detokenize nonce round-trip, model mapping, canaries and process tree all still pass under the unsealed image — sealing costs no operability, it only buys immutability.

Not re-measured by me: the frozen base control (`controls/base.c1.out`, `sealed=0` for a *different* reason — the image is the extracted path, not a memfd; see its `F_GET_SEALS … Invalid argument` and `link count 1` details).

## Probe: can an unsealed memfd be written while a process runs from it?

`probe_unsealed_memfd_write.py` (payload: `/bin/sleep` copied into a memfd, exec'd through `/proc/<parent>/fd/<n>` with `pass_fds` and `argv[0]` = the memfd name — the same exec shape as `kama-llamacpp-live.py:1996`); raw rows in `probe-unsealed-run.json`. Every case measured, none asserted.

| case (child running) | unsealed memfd | sealed memfd (15) | on-disk file |
|---|---|---|---|
| `/proc/<child>/exe` | `/memfd:j2unsealed-unsealed-memfd (deleted)`, nlink 0 | `/memfd:…-sealed-memfd (deleted)`, nlink 0 | the path, nlink 1 |
| `F_GET_SEALS` | `0` | `15` | `EINVAL` |
| `write(2)` on fd held across exec | **SUCCESS** (1 byte) | `EPERM` | exec refused: `ETXTBSY` |
| `pwrite` 4 B at offset 0 + readback | **SUCCESS**, readback `00000000`, was `7f454c46` (ELF magic overwritten in the running image) | `EPERM` | — |
| `ftruncate(size-1)` / `ftruncate(size+1)` | **SUCCESS** / **SUCCESS** | `EPERM` / `EPERM` | — |
| `open(/proc/<child>/exe, O_RDWR)` + write | `ETXTBSY` | `ETXTBSY` | `open(path, O_RDWR)` → `ETXTBSY` |
| `open(/proc/self/fd/<n>, O_WRONLY)` + write | `ETXTBSY` | `ETXTBSY` | — |
| `F_ADD_SEALS(15)` after exec | `SUCCESS` (0) | `EPERM` (F_SEAL_SEAL) | — |
| after the child exits: `write(2)` / `ftruncate` on the held fd | **SUCCESS** / **SUCCESS** | `EPERM` / `EPERM` (sealed) | — |

**Answer: SUCCESS, not ETXTBSY — on the descriptor that was opened before the exec.** ETXTBSY (`exec`'s deny-write) only guards reopening the image; it does not stop a writable fd carried across `execve`. Consequences:

1. **Seals add something real.** An unsealed memfd is *weaker* than the on-disk round-51 path, not equal to it: on disk, exec is impossible while an `O_RDWR` fd is held (`ETXTBSY`), so no writer can exist; a memfd execs happily and the holder keeps write access. `F_SEAL_WRITE` is what restores immutability.
2. **The holder is real, not hypothetical.** The replay keeps the memfd `O_RDWR` for the whole run and hands the *same* descriptor to the live child (`kama-live-replay.py:400` `sealed_member(...)`, `:403` `pass_fds=(own_fd,)`), so both processes can mutate the running server's image under the ablation (offset-0 rewrite, append, shrink, grow). The readback proves the image's own bytes change while it serves.
3. **The guard in the build is durable; ETXTBSY is not.** After the child exits, the same held fd writes again on an unsealed memfd — the deny-write window is lifetime-bound, the seal is not.
4. Sealing *after* exec succeeds in the probe, so a late seal is technically possible — but it cannot undo prior writes, and it may fail with `EBUSY` if the process holds a writable `MAP_SHARED` mapping (`llama-server` maps its own image; **[INFERENCE]**, not measured).

## Findings

- **F1 (minor, diagnostic precision, counter is frozen — report only).** `tools/round52-replay-memfd-audit.py:503` prints `rerun server_exe {…} does not record the observed sealed image ('00:01', '174282')` even when dev/inode *do* match and only `seals` differ; the message names just dev:inode, which reads as a dev/inode mismatch. The dict in the same line does carry `'seals': 0`, so an operator can still tell. Proposed message-only change in `counter-message-proposal.diff` (not applied).
- **F2 (design note, for the round's lesson/frontier, not a defect).** Because the writable fd is inherited by the live child, the seal is the only thing making that inheritance inert. Any future path that creates the memfd without `MFD_ALLOW_SEALING`, or that seals after exec, loses the property silently — the counter would still say `sealed=0`, but the replay's own checks would not.
- **F3 (limits of this evidence).** Probe payload is a copied `/bin/sleep` (same kernel path: `execve` of a memfd through a `/proc/<pid>/fd` link; shmem, nlink 0, `/memfd:` link), not `llama-server`; single host kernel `7.2.11-arch1-1`; `vm.memfd_noexec` not exercised. Counter runs are the frozen tool unmodified at its preregistered sha256.

## Commands run (all from the fleet root or `$S`)

```
git clone --shared -q …/kama-shokunin $S/lane; git -C $S/lane rev-parse --show-toplevel   # $S/lane
git -C $S/lane checkout -B abl 5dacf2c7…; <patch>; git -C $S/lane -c user.name=fx … commit -am "…"   # adc00bf5
python3 …/round52-replay-memfd-audit.py --repo $S/lane --tip 5dacf2c7… --scratch $S/c1ctl   # exit 0, met=True
python3 …/round52-replay-memfd-audit.py --repo $S/lane --tip adc00bf5… --scratch $S/c1abl2  # exit 1, met=False
python3 probe_unsealed_memfd_write.py                                                       # exit 0
pgrep -af llama-server   # empty; no leftovers from these runs
```
Scratch `$S` removed after copying the receipts and probe evidence. Immediately before the ablation commit, `git -C $S/lane diff --stat` showed exactly `tools/kama-live-replay.py | 9 ++-------` and `tools/kama-llamacpp-live.py | 5 +++--` (5 insertions, 9 deletions). The lane repo itself was only read (`git rev-parse`, `git log`, `git cat-file`); no file under `/home/vgpnk/Projects/shokunin/kama-shokunin` was modified. (A post-cleanup `git status` on the already-deleted clone is not evidence and is not claimed.)

## Files written
- `.ufo/waves/round-52/w1/out/J2Unsealed.md` (this report)
- `.ufo/waves/round-52/w1/out/J2Unsealed/c1-ablation-adc00bf5.out`
- `.ufo/waves/round-52/w1/out/J2Unsealed/c1-build-control.out`
- `.ufo/waves/round-52/w1/out/J2Unsealed/ablation-adc00bf5.diff`
- `.ufo/waves/round-52/w1/out/J2Unsealed/counter-and-tool-sha256.txt`
- `.ufo/waves/round-52/w1/out/J2Unsealed/counter-message-proposal.diff`
- `.ufo/waves/round-52/w1/out/J2Unsealed/probe_unsealed_memfd_write.py`
- `.ufo/waves/round-52/w1/out/J2Unsealed/probe-unsealed-run.json`
