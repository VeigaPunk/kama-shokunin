# J1PathExec — Round 52 C1 ablation control (no memfd)

**Verdict:** with only the round-52 memfd wiring removed from the build tree, the frozen C1 counter reports `bind=1 sealed=0 teardown=1 newrow=1 bound=3/3 sealedruns=0/3 met=False` (exit 1) where the build reports `met=True` — the `sealed` leg is exactly the leg the memfd mechanism carries, and the other three legs (`bind`, `teardown`, `newrow`) do not move.

## Inputs and integrity

| Item | Value |
|---|---|
| Lane (read-only) | `/home/vgpnk/Projects/shokunin/kama-shokunin` (never written; `git status` here shows only other seats' pre-existing edits/untracked receipts) |
| Fixture clone | `git clone --shared … $S/lane`; `git -C $S/lane rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r52/J1PathExec/lane` (verified before the commit) |
| Build (ablation parent) | `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` |
| Ablation commit | `fc51ebca94bc4a7bf8404016a504bb81a4209573`, identity `fx <fx@invalid>`, one file: `tools/kama-live-replay.py`, +20/−73 (`ablation.diff`) |
| Frozen counter | `tools/round52-replay-memfd-audit.py` sha256 `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5` == preregistration `claims[0].counter_sha256`; not edited |
| Scratch | `$S=/fast/scratch/hyaku/kama-r52/J1PathExec` (`TMPDIR=$S`), removed at the end |

The counter ran against the clone at the ablation commit; the counter builds its own tree with `git archive <tip>`, so the measured tree is precisely the ablation commit's tree.

## What the control removes (build `5dacf2c7:tools/kama-live-replay.py`)

- `:397-401` — the round-52 comment, `own_fd, own = sealed_member(archive, need["server.member"], want_srv)` and `argv[-2:-2] = ["--server-fd", str(own_fd)]` are gone. The replay no longer creates a memfd and no longer passes `--server-fd`.
- `:403` — `pass_fds=(own_fd,)` removed from the live-child `subprocess.run`.
- `:420-437` — the round-52 server-exe block removed in full: no `res["own_server"] = own`, no digest / dev+inode / seals+nlink+`/memfd:` comparison against `rr["server_exe"]`.
- Result: the live child is started as in round 51 — `--server <work>/server/<member>` — and execs that extracted path (`tools/kama-llamacpp-live.py:1952` `if args.server_fd is not None` is simply not taken; `--server-fd` defaults to `None` at `:1479`).

Kept deliberately (not on the runtime path): `sealed_member()` itself (`:212`), `import fcntl`, `F_ADD_SEALS/F_GET_SEALS/SEALS_ALL`, and its two unit selftest cases. The member-digest verification before exec (build `:364-370`) is untouched, so the ablated replay still refuses a member whose bytes differ from `--server`'s digest. Selftest coherence: the fake live's `server_exe` producer is reverted to the round-51 `os.stat(s)` form (`:464-466`, it would otherwise index a `--server-fd` argument that no longer exists), and the four round-51/three round-52 end-to-end cases that assert the removed comparison are dropped (`:537-539`). The replay's `--selftest` was **not run** (parent-owned gate); the pruning is by construction.

Docstring updated (`:54-70`) so the control tree does not claim a binding it no longer makes.

## Frozen counter run (exit 1)

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round52-replay-memfd-audit.py \
    --repo $S/lane --tip fc51ebca94bc4a7bf8404016a504bb81a4209573 \
    --scratch $S/c1 --out .ufo/waves/round-52/w1/out/J1PathExec/c1-ablated.out
tip=fc51ebca94bc4a7bf8404016a504bb81a4209573
bind=1 sealed=0 teardown=1 newrow=1 bound=3/3 sealedruns=0/3 met=False
exit=1   (17.9 s)
```

Receipt `c1-ablated.out` (21 `detail:` lines). Per run (b1/b2/b3) the sealed failures are the counter's own witness, not the replay's refusal:

- `sealed: running image link '<work>/server/llama-b11909/llama-server' is not an anonymous memfd`
- `sealed: running image has link count 1, not 0`
- `sealed: F_GET_SEALS on the running image failed: Invalid argument` (`seals` `None` on an ordinary file)
- `sealed: rerun server_exe {… 'nlink': 1, 'seals': None, 'path': '<work>/server/llama-b11909/llama-server', 'sha256': '35ac50fb…d8d7ff0' …} does not record the observed sealed image`
- `sealed: replay own_server None does not name the observed memfd`

All three bind legs passed with the round-50 checks intact (`exe+listen+tree+env+mapped ok, child_pid joined, mapping … recorded, nonce … round-tripped`), so the observed process is the receipt's server running from the extracted member; `teardown: … after 0.10 s alive [] port refuses ok`; `newrow: 1 rows new since base; 1 name memfd_create(2): ['| S500 |']`.

## Attribution / separability

| Reading | Receipt | `bind` | `sealed` | `teardown` | `newrow` | met |
|---|---|---|---|---|---|---|
| Round-52 build | `.ufo/waves/round-52/measured/c1-build.out` | 1 | 1 (3/3) | 1 | 1 | True |
| Base (round-51 tip) | `.ufo/waves/round-52/controls/base.c1.out` | 1 | 0 | 1 | 0 | False |
| **This control** (build minus memfd wiring) | `c1-ablated.out` | 1 | 0 | 1 | 1 | **False** |

The control differs from the base only in `newrow` (the S500 source row is present at this tree), and from the build only in `sealed`. So `newrow` is not what carries the build's pass, `bind`/`teardown` are not, and the `sealed` leg's verdict tracks the memfd wiring alone.

## Independent runtime evidence (not a counter run)

One replay of `receipt-1.json` from the ablation tree ($S/probe, exit 0, `match True`, `mismatches []`):

- `rerun-receipt-1.json` → `argv[0] = …/probe/work/server/llama-b11909/llama-server` (the extracted path; no `--server-fd` anywhere in argv), `server.fd` absent, `schema kama-llamacpp-live/v5`.
- `server_exe` = `{"opened": true, "path": "<work>/server/llama-b11909/llama-server", "nlink": 1, "seals": null, "size": 17864, "sha256": "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"}` — the extracted path, recorded but not compared.
- `replay-result-1.json` → keys `[… match, mismatches, notes, refused, rerun_receipt …]`; **no `own_server` key**, which is why the counter's last sealed line reads `own_server None`.

## Limits and notes

- The control keeps `sealed_member()` reachable only from `--selftest`; a review that treats "no memfd" as "no memfd code anywhere" will want it deleted, but the runtime path (launch + comparison) is what C1 measures and it is fully ablated.
- Preregistered limits untouched: an ablation control, not a lane revision; it changes no claim, counter, control or preregistration file.
- Network used by the counter and probe: `github.com` b11909 release (~75 MB/replay) and `huggingface.co` stories260K (~1 MB). No `pacman` (host-wide pause), no tool installs.
- No `llama-server` from this seat survives: `pgrep -af llama-server` shows none whose path contains `J1PathExec` (the two live rows belong to peer seat M2Replay's own counter run).
- Fixture-commit recipe (the clone was scratch and is removed): `git clone --shared <lane> $S/lane`; `git -C $S/lane checkout --detach 5dacf2c7…`; apply `ablation.diff`; `git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit` (hash changes with the fixture timestamp).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J1PathExec.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J1PathExec/c1-ablated.out` (frozen counter receipt, exit 1)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J1PathExec/ablation.diff` (build→control unified diff)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J1PathExec/kama-live-replay.ablation.py` (full patched file, as committed)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J1PathExec/rerun-receipt-1.json` (probe rerun receipt: argv, server_exe)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J1PathExec/replay-result-1.json` (probe replay result: `match True`, no `own_server`)
