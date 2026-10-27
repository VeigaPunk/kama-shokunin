# X2Rerun — second independent C1 measurement at 5dacf2c7

**Verdict: agreement — C1 met (`met=True`) on two sequential frozen-counter runs at `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` on one clone; verdict line byte-identical across both runs and to the L1 build receipt; each run's b1–b3 server image is a `/memfd:` link with seals 15 on device `00:01` and three distinct inodes.**

## Setup

- Tip measured: `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` (build), resolved by the counter itself (`git rev-parse <tip>^{commit}` inside the counter, `round52-replay-memfd-audit.py:593`).
- Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r52/X2Rerun/lane`; `git -C $S/lane rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r52/X2Rerun/lane`; HEAD of the clone is `34d82600` (wave spec) — the counter reads the **tip tree** via `git archive --format=tar <tip>` (`round52-replay-memfd-audit.py:594`), not HEAD, so the wave-spec commit does not enter the measured tree.
- Same clone, same scratch root for both runs, sequential. Counter never edited.
- `pgrep -x llama-server` before and after: no such process (the three `pgrep -af llama-server` matches earlier were unrelated `sha256sum ./llama-server …` census processes, not servers).
- Network: `https://github.com` → 200, `https://huggingface.co` → 200.

## Commands and results

```
python3 .../tools/round52-replay-memfd-audit.py --repo $S/lane \
  --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch $S --out <out>/pass1.out   # rc=0, 34.24 s (bash wall)
python3 .../tools/round52-replay-memfd-audit.py --repo $S/lane \
  --tip 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 --scratch $S --out <out>/pass2.out   # rc=0, 28.57 s (EPOCHREALTIME; bash wall 28.73 s)
```

Wall time: **pass1 ≈ 34.1 s, pass2 28.6 s** (pass1 was timed by the shell envelope, pass2 by `EPOCHREALTIME` around the counter; the pass2 envelope minus measured run = 0.16 s, so pass1's counter time is ≈34.1 s). Both are within the same order of magnitude; the spread is the network-bound part (each of the three replays re-downloads the server archive and the model).

Exit codes: `0` (met), `0` (met). No `could-not-evaluate` path.

Both receipt files are byte-identical to their captured stdout (`cmp pass1.out pass1.stdout`, `cmp pass2.out pass2.stdout` → identical), i.e. `--out` and console text are one artifact.

## Verdict line

pass1.out:2 and pass2.out:2, identical bytes:

```
bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True
```

This is also the exact line of the L1 build receipt `.ufo/waves/round-52/measured/c1-build.out:3`, so three independent instances of the counter (one L1, two this seat) agree on the verdict sentence. Masked comparison (`pid`, `port`, `inode`, nonce, teardown duration normalised) shows the two receipts are otherwise **identical** — same detail ordering, same leg sentences, same `newrow: 1 rows new since base; 1 name memfd_create(2): ['| S500 |']`.

## Per-receipt image evidence (b1–b3)

From the counter's own `sealed` detail lines (`round52-replay-memfd-audit.py:361-392`, printed at `:527-529`), each line carries link / dev:inode / seals:

| run | leg | `/proc/<pid>/exe` link | dev:inode | seals | distinct inode in run |
|---|---|---|---|---|---|
| pass1 | b1 | `/memfd:llama-server (deleted)` | `00:01:170737` | 15 | 3/3 |
| pass1 | b2 | `/memfd:llama-server (deleted)` | `00:01:179292` | 15 | |
| pass1 | b3 | `/memfd:llama-server (deleted)` | `00:01:165677` | 15 | |
| pass2 | b1 | `/memfd:llama-server (deleted)` | `00:01:165680` | 15 | 3/3 |
| pass2 | b2 | `/memfd:llama-server (deleted)` | `00:01:179304` | 15 | |
| pass2 | b3 | `/memfd:llama-server (deleted)` | `00:01:151479` | 15 | |

- `/memfd:` link: 3/3 in both runs (the counter reads the link itself with `readlink`, `:365`, and fails the leg otherwise).
- seals 15: 3/3 in both runs (`F_GET_SEALS = 1034`, `SEALS = 15`, `:91-92`; check `:388-389` — note the leg accepts a superset, the printed value is exactly 15 in all six observations).
- link count 0: enforced per leg (`:386-387`, message "running image has link count N, not 0") — it is not printed in the success line (see observation O1).
- device `00:01` (anonymous-inode device, not the btrfs `103:05` the model mapping uses): 6/6.
- distinct inodes: within each run the three legs are three different inodes; across the two runs the sets are disjoint (`{170737,179292,165677}` vs `{165680,179304,151479}`). The values come from the anonymous-inode allocator, so near-neighbours (165677 vs 165680) appear across runs but never coincide.
- The per-leg dev:inode that the counter observed is additionally required to equal the rerun receipt's `server_exe` dev/inode/seals/digest and the replay's `own_server` dev/inode with `memfd: true` (`:499-507`); every leg printed "recorded in server_exe and own_server", so both the live tool's `sealed_fd` record (`tools/kama-llamacpp-live.py:786-811`) and the replay's own memfd identity (`tools/kama-live-replay.py:222-257,400,426`) agree with the counter's independent `/proc/<pid>/exe` read in all six observations.

Carried legs in both runs: bind 3/3 (exe digest, listener, nonce round-trip against the model's own vocabulary, process tree, canaries clean, mapped model dev/inode joined via `child_pid`), teardown ok at 0.10 s in both runs (invoker SIGKILLed with 3 descendants, tree gone, port refusing), newrow 1 (`| S500 |` at `corpus/SOURCES.md:253`, absent at base).

## Discrimination (negative control, not re-run)

The frozen base control `.ufo/waves/round-52/controls/base.c1.out:2` reads `bind=1 sealed=0 teardown=1 newrow=0 met=False`, and its `sealed` details are the path-shaped failures (link is the extracted path, `F_GET_SEALS` → `EINVAL`, `st_nlink` 1, `server_exe`/`own_server` name dev `103:05`). The same counter therefore separates the base from the build on exactly the legs my two runs exercise; the sealed leg is not passing vacuously.

## What this measurement does and does not establish

Establishes, at `5dacf2c7`, for three committed v5 b11909 receipts: the server an outside observer witnesses during a replay runs an image with no directory entry, a `/memfd:` link, all four seals, the frozen server digest, and the rerun's and replay's own records name that same image; the round-50 bind and teardown legs still hold; the memfd surface is a SOURCES row (`S500`).

Does not establish (preregistered limits, `preregistration.json` limits[0..2], unchanged): a sealed memfd filled from the host's own byte-identical install would also meet — archive provenance is not observed; shared libraries (`libllama-server-impl.so`, `libggml*`) still load from the extracted tree by path via `LD_LIBRARY_PATH` (`tools/kama-llamacpp-live.py:1957`), only the server image is sealed; the round-50 carried limits (probe PATH execution, in-place rewrite of model bytes after mapping, kills during download/readiness) are untouched.

## Observations (no change requested; counters are frozen)

- **O1 — receipt does not print `st_nlink`.** The success line prints link, dev:inode, seals (`:527-529`) but not the link count, which the leg does enforce at `:386-387`. A reader of a green receipt therefore cannot see one of the four facts the predicate names ("no link count") without trusting the leg. Not a defect in the measurement; it is an observability gap if the receipt is ever the only artifact. A future (not this wave) tweak would append `nlink 0` to the success sentence.
- **O2 — `own_server.path` in the replay is a literal, not a `readlink`.** The replay records the path field as the constant `'/memfd:llama-server (deleted)'` in its own record (the live tool's `server_exe` path comes from its own open/read of `/proc/<pid>/exe`). Irrelevant to this verdict: the counter's sealed leg reads the link itself and compares dev/inode/seals/digest against both records; the literal never carries a leg.
- **O3 — wall-time spread 34.1 s vs 28.6 s** between two runs of the same commit: expected from the per-replay network downloads (`READY_WAIT` is 600 s, so the leg is not near any timeout). Not a stability risk at this margin.

No lane file was modified: `git -C $S/lane status --porcelain` was empty before and after both runs; the counter is read-only on `--repo` and removes its own scratch (`round52-replay-memfd-audit.py:643`). No tool was installed or upgraded (nothing needed). No llama-server left running.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X2Rerun.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X2Rerun/pass1.out` (run 1 receipt, `--out`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X2Rerun/pass1.stdout` (run 1 console capture)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X2Rerun/pass2.out` (run 2 receipt, `--out`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X2Rerun/pass2.stdout` (run 2 console capture)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/X2Rerun/agreement.txt` (machine-written agreement summary: verdict identity, masked identity, per-leg link/dev:inode/seals)
