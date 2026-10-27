CONFIRMED: the frozen round-52 C1 counter rejects the round-51 J3CopyDecoy shape at the round-52 build - `bind=1 sealed=0 teardown=1 newrow=1 bound=3/3 sealedruns=0/3 met=False`, exit 1 - and the failing evidence is the counter's own `/proc/<pid>/exe` observation (an ordinary file with a directory entry), not the replay self-check this control removes.

## Control built

- Fixture: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r52/J3CopyDecoy/lane`, detached at build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`. `git -C <clone> rev-parse --show-toplevel` printed the clone (checked before the commit); its `--git-dir`/`--git-common-dir` are `<clone>/.git` (no gitfile), so the lane's git/jj state was untouched. Fixture commit `5fff7ff48d167c68a5d7c5ae139f3f5dd98eb94a` (`j3-probe-commit.out`), identity `fx <fx@invalid>`.
- Patch (`j3-probe.patch`, one file, +7/-24) on `tools/kama-live-replay.py`:
  - fixture `tools/kama-live-replay.py:374`: after the member digest check, `shutil.copyfile("/home/vgpnk/.local/opt/llama-b11909/llama-server", server)` overwrites the extracted member `<work>/server/llama-b11909/llama-server` in place. Host digest `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` = the frozen server digest (`j3-copy-evidence.txt`), so the provenance and member-digest checks above it still pass.
  - fixture `:402-405`: the round-52 memfd mechanism removed - no `sealed_member()` call, no `--server-fd`, no `pass_fds` (build `5dacf2c7:tools/kama-live-replay.py:397-404`). The live tool is started with `--server <member path>` and execs that path.
  - build `:420-437` (the replay's own round-52 check: `own_server` plus the `server_exe` dev/inode/seals/nlink/`/memfd:` comparison) removed, so the control tests the counter, not the replay's self-refusal. Consequence: the replay result has no `own_server` key (observed below).
- Frozen instrument verified unchanged: `sha256sum tools/round52-replay-memfd-audit.py` = `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5`, equal to `counter_sha256` in `.ufo/waves/round-52/preregistration.json`. Patched replay in the measured tree: `6293d843427171efa02e493759a19e274a723c941f0d6816beb0aaa0b9329b21` (`git show 5fff7ff4:tools/kama-live-replay.py` hashes the same).

## Frozen counter run

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round52-replay-memfd-audit.py \
  --repo /fast/scratch/hyaku/kama-r52/J3CopyDecoy/lane \
  --tip 5fff7ff48d167c68a5d7c5ae139f3f5dd98eb94a \
  --scratch /fast/scratch/hyaku/kama-r52/J3CopyDecoy \
  --out .../.ufo/waves/round-52/w1/out/J3CopyDecoy/j3-copydecoy.c1.out
```
exit 1 (`j3-copydecoy.c1.out`):

```
tip=5fff7ff48d167c68a5d7c5ae139f3f5dd98eb94a
bind=1 sealed=0 teardown=1 newrow=1 bound=3/3 sealedruns=0/3 met=False
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 512998 port 37565 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1956500374 recorded, nonce 'kama witness 1fe33a6b2a08d7b5' round-tripped
detail: sealed b1: sealed: F_GET_SEALS on the running image failed: Invalid argument
detail: sealed b1: sealed: running image link '/fast/scratch/hyaku/kama-r52/J3CopyDecoy/r52c1-s1zcm22f/work-b1/server/llama-b11909/llama-server' is not an anonymous memfd
detail: sealed b1: sealed: running image has link count 1, not 0
detail: sealed b1: sealed: rerun server_exe {'dev': '103:05', 'inode': '1955770758', 'nlink': 1, 'opened': True, 'path': '/fast/scratch/hyaku/kama-r52/J3CopyDecoy/r52c1-s1zcm22f/work-b1/server/llama-b11909/llama-server', 'seals': None, 'sha256': '35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0', 'size': 17864} does not record the observed sealed image ('103:05', '1955770758')
detail: sealed b1: sealed: replay own_server None does not name the observed memfd
... (b2 pid 523033 port 32825, b3 pid 533750 port 41823: identical five-line sealed blocks)
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 1 rows new since base; 1 name memfd_create(2): ['| S500 |']
```

Reading:
- Every bind leg passes (`bound=3/3`): the decoy's bytes are the frozen server's, so exe digest, listener, nonce/vocabulary round-trip, process tree, canaries, mapped model, `child_pid` join and the round-50 teardown are unaffected. The control isolates the round-52 leg.
- `sealed=0` (`sealedruns=0/3`) comes from the counter's own open of `/proc/<pid>/exe` (`tools/round52-replay-memfd-audit.py:368-396`, messages at `:385`, `:387`): the link is the extracted member path, not `/memfd:`, `st_nlink` is 1, and `F_GET_SEALS` on the opened regular file raises `EINVAL`. This is independent of the removed replay check.
- The rerun receipt's `server_exe`, written by the unmodified live tool, agrees: `nlink: 1`, `seals: null`, `path` = the member path, digest correct (`j3-rerun-receipt-copydecoy.json`). `own_server` is absent because the replay check was removed, and the leg reports it (`:507`).

## Retained A/B (same receipt, same archive)

One direct replay of `.ufo/waves/round-48/c2/live/receipt-1.json`, both runs `match=True exit=0`, recorded in `j3-probe-replay.json` / `j3-honest-replay.json` and `j3-copy-evidence.txt`:

| | decoy (fixture `5fff7ff4`) | honest build (`5dacf2c7`) |
|---|---|---|
| extracted member after the run | `mtime=2026-10-27 02:11:20`, inode 1822251804, nlink 1 | `mtime=2026-10-26 17:52:20`, inode 1352719985, nlink 1 |
| member sha256 | `35ac50fb…d7dff0` (17864 B) | `35ac50fb…d7dff0` (17864 B) |
| replay `own_server` | `None` (key absent) | `{"memfd": true, "seals": 15, "dev": "00:01", "inode": "183462", "member": "llama-b11909/llama-server", "sha256": "35ac50fb…d7dff0"}` |
| rerun `server.fd` | absent | `{"dev": "00:01", "inode": "183462", "nlink": 0, "seals": 15, "sha256": "35ac50fb…d7dff0"}` |
| rerun `server_exe` | path `/…/work/…/server/llama-b11909/llama-server`, `nlink 1`, `seals null` | path `/memfd:llama-server (deleted)`, `nlink 0`, `seals 15` |

The archive member's tar header mtime is `2026-10-26T17:52:20` (same file; the host install was extracted from it). The honest path leaves that mtime in place; the decoy's member mtime is the run time, i.e. the committed `shutil.copyfile` line wrote the file after extraction. The copy is otherwise invisible to path checks: same bytes, same size, and `copyfile` truncates in place so the inode is the extracted one - exactly the round-51 observation that a byte-identical copy at the member path cannot be told from the extracted member by dev/inode/digest.

## Comparison with round 51 (`.ufo/waves/round-51/a2w1/out/J3CopyDecoy.md`)

- Round 51: the same shape (byte copy of the host install over the member path) met the then-frozen counter - `bind=1 own=1 teardown=1 newrow=1 met=True` - because that leg compared the running image's dev/inode to `os.stat(member)`, which an in-place copy preserves.
- Round 52: reproducing the shape requires dismantling the build's memfd construction (there is otherwise no on-disk running image to substitute), and the counter then fails on its own `/proc` observation: `sealed=0 met=False`. The round-51 route to `met=True` is closed; the remaining route is the preregistered limit (a sealed memfd filled from the byte-identical host install), which this control does not exercise.
- The base control (`.ufo/waves/round-52/controls/base.c1.out`) gives the same `bind=1 sealed=0 teardown=1 newrow=0 met=False` for the unbuilt tree; the measured build (`measured/c1-build.out`) gives `bind=1 sealed=1 teardown=1 newrow=1 met=True`. The decoy matches the base shape's `sealed=0` while keeping `newrow=1`, i.e. it is rejected by the leg, not by an absent source row.

## Observation (advisory, verdict unaffected)

`tools/round52-replay-memfd-audit.py:497-503` folds identity and seals into one condition, so the message claims a dev/inode mismatch when only the seals differ: in this run the quoted `server_exe` carries the observed `('103:05', '1955770758')` and is still reported as "does not record the observed sealed image". A reviewer reading only that line can misread a seal failure as an identity failure. Proposed message split (frozen counter - not edited, advisory only): `j3-counter-diag.diff`. Leg result is correct as is.

## Risks / limits

- The preregistered C1 limit (a sealed memfd filled from the host's byte-identical install meets the counter) is untouched and unexercised here.
- The mtime delta is the only trace of the copy in the fixture and it is forgeable (round-51 receipt); the counter's verdict does not rest on it - it rests on `/proc/<pid>/exe` (`/memfd:` link, `st_nlink`, `F_GET_SEALS`).
- The fixture keeps the build's offline `--selftest` block, which still builds a fake live tool around `--server-fd` and would fail at this commit. It was not run and is not on the counter's path (`--selftest` only).
- No installs or upgrades were made; pacman was not run.

## Verification performed here

- `python3 -m py_compile tools/kama-live-replay.py` at the fixture: exit 0 (`COMPILE_OK`).
- Frozen C1 counter at the fixture tip: exit 1, `bind=1 sealed=0 teardown=1 newrow=1 met=False`.
- Two direct replays (decoy and honest-build code) on the committed v5 receipt: both `match=True`, exit 0; their receipts and JSONs retained.
- `pgrep -af llama-server` filtered for this seat's scratch: no process. The only `llama-server` lines on the host belong to peer `J2Unsealed`'s scratch and were left alone.
- No build/lint/test suite was run (leaf rule; the parent owns the post-integration gate).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J3CopyDecoy.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J3CopyDecoy/j3-copydecoy.c1.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J3CopyDecoy/j3-probe.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J3CopyDecoy/j3-probe-commit.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J3CopyDecoy/j3-probe-replay.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J3CopyDecoy/j3-rerun-receipt-copydecoy.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J3CopyDecoy/j3-honest-replay.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J3CopyDecoy/j3-rerun-receipt-honest-build.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J3CopyDecoy/j3-copy-evidence.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J3CopyDecoy/j3-counter-diag.diff`
