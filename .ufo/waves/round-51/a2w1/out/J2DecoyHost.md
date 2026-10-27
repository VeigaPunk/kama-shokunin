# J2DecoyHost — round 51 C1 ablation (the round-50 J4Decoy shape)

**Verdict: the C1 counter rejects the decoy — `bind=1 own=0 teardown=1 newrow=1 bound=3/3 owned=0/3 met=False` (exit 1) at fixture tip `d8ace78994214b9f09dddb0900888e997506ac5b`, against `bind=1 own=1 teardown=1 newrow=1 met=True` (exit 0) at the untouched build tip `138af25b963450b6520794995605fa7dbbcd87e0`.** The decoy exec'd the host's own `/home/vgpnk/.local/opt/llama-b11909/llama-server` — byte-identical to the frozen server digest, so every digest test passes — and the counter's own `/proc/<pid>/exe` read caught it on file identity (dev:inode), exactly where round-50 R6 C1/J4Decoy left the hole. No adaptation was needed: the host install hashes to the frozen server digest.

## Setup (fixture, no lane mutation)

```
S=/fast/scratch/hyaku/kama-r51/J2DecoyHost; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane     # exit 0
git -C $S/lane rev-parse --show-toplevel   -> /fast/scratch/hyaku/kama-r51/J2DecoyHost/lane
git -C $S/lane checkout --detach 138af25b963450b6520794995605fa7dbbcd87e0
```

Host install identity (no adaptation needed — it equals the counter's frozen `SERVER_SHA`):

```
35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0  /home/vgpnk/.local/opt/llama-b11909/llama-server
ELF 64-bit LSB pie executable, x86-64 ... size=17864   stat: dev=56 (0x38) inode=238037577
```

## The decoy patch (`fixture-decoy.diff`, applied in the clone only)

Two changes to `tools/kama-live-replay.py`, committed with a fixture identity after re-asserting the toplevel:

1. new constant `DECOY_SERVER = "/home/vgpnk/.local/opt/llama-b11909/llama-server"` (clone:89-92), and the live child is started with `--server DECOY_SERVER` (clone:328) instead of `server` — while `server = <work>/server/<member>` stays the extracted member and its **digest check is kept** (`member-digest-mismatch` at `tools/kama-live-replay.py:305-310`), so the decoy is not refused on provenance;
2. the round-51 mismatch block is removed (`tools/kama-live-replay.py:359-368`: the `server-exe:…` / `server-exe:sha256:` / `server-exe:not-own-member:` appends), so the replay refuses nothing and exits 0. `res["own_server"]` is **kept**, naming the extracted member honestly — the decoy does not hide a field, it lies only by exec'ing a different file.

```
git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit -aqm "fixture: decoy replay execs host b11909 install, no server-exe mismatch block"
-> d8ace78994214b9f09dddb0900888e997506ac5b   (parent 138af25b963450b6520794995605fa7dbbcd87e0, author fx <fx@invalid>)
```

## Counter run on the decoy (frozen, unmodified)

```
python3 .../tools/round51-replay-exe-audit.py --repo $S/lane --tip d8ace78994214b9f09dddb0900888e997506ac5b --scratch $S --out .../J2DecoyHost/c1-decoy.out
EXIT=1
tip=d8ace78994214b9f09dddb0900888e997506ac5b
bind=1 own=0 teardown=1 newrow=1 bound=3/3 owned=0/3 met=False
detail: bind b1: pid 912464 port 43117 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 413902614 recorded, nonce 'kama witness f649c6e6f45b22a2' round-tripped
detail: own b1: own: running image dev:inode 00:38:238037577 is not the replay's extracted member /fast/scratch/hyaku/kama-r51/J2DecoyHost/r51c1-47gshok1/work-b1/server/llama-b11909/llama-server (103:05:1753616769)
detail: own b1: own: replay own_server {'path': '.../work-b1/server/llama-b11909/llama-server', 'dev': '103:05', 'inode': '1753616769'} does not name the observed member file
   (b2, b3 identical in shape: image 00:38:238037577; members 103:05:1621152437 / 103:05:1489524772)
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 1 rows new since base; 1 name proc_pid_exe(5): ['| S499 |']
```

Paired control, same clone, same counter, untouched build tip (isolates the patch as the only cause):

```
python3 .../tools/round51-replay-exe-audit.py --repo $S/lane --tip 138af25b963450b6520794995605fa7dbbcd87e0 --scratch $S
EXIT=0
bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True
detail: own b1: running image 103:05:414994447 is the extracted member, recorded in server_exe and own_server   (b2, b3 likewise)
```

## What the catch actually was

- Every round-50 leg the counter keeps survives the decoy: `bind=1` (3/3: exe digest, listener, nonce/vocabulary round-trip, process tree, canaries, mapped model, `child_pid` join, released, teardown-after-exit) and `teardown=1` (0.10 s). The decoy would have met the round-50 positive legs.
- The digest is not what caught it. `observe`'s `sha_file(f"/proc/{pid}/exe") != SERVER_SHA` (counter:318-320) emits **no** problem line for any of the three receipts, and the rerun receipt records `server_exe.sha256 = 35ac50f…` (`rerun-receipt-decoy.json`): the executed bytes are the frozen server. A digest-only check passes — the exact statement of R6 C1 ("a digest says which bytes run, not which file").
- `own` caught it on file identity: `own_exe` (counter:351-378) opens `/proc/<pid>/exe`, `fstat()`s it, and compares dev:inode against `os.stat(<work>/server/<member>)`; got `00:38:238037577` vs want `103:05:*` under every receipt, so `oprobs` is non-empty and `owned=0/3`. The second own-check (counter:494-497) independently rejects the replay's honest `own_server`, because it must equal the **observed** image.
- So the ablation is decisive for the frontier claim: the round-51 `own` leg, not the carried round-50 legs and not the digest, is the load-bearing addition.

Direct evidence that the replay itself did not refuse (the decoy must lose only to the outside observer):

```
python3 $S/lane/tools/kama-live-replay.py --receipt $S/lane/.ufo/waves/round-48/c2/live/receipt-1.json --work $S/replay1 --out $S/replay1.json
replay match=True refused=None mismatches=0 exit=0        EXIT=0
own_server   = {"path": ".../replay1/server/llama-b11909/llama-server", "dev": "103:05", "inode": "1754043240"}
server_exe   = {"dev": "00:38", "inode": "238037577", "opened": true,
                "path": "/home/vgpnk/.local/opt/llama-b11909/llama-server",
                "sha256": "35ac50f…d7ff0", "size": 17864}
server.arg   = /home/vgpnk/.local/opt/llama-b11909/llama-server
child_pid    = 949120      witness = None      (unwitnessed run: no --witness-dir)
```

`pgrep -af llama-server` after every run: empty — nothing I started survived.

## Carried limits (not defects I am grading)

1. `own` compares the running image's `(dev, inode)` and bytes with the extracted member path. A member path that is a **same-filesystem hardlink** to the host install would make the two identical, and the counter could not tell how the member path came to be. Here it is unreachable: the host install is on dev `00:38` (`/home`) and the replay's work dir on dev `103:05` (`/fast`), so a cross-device hardlink is impossible; a bind mount would need root.
2. The base control (`controls/base.c1.out`) shows the same `own=0` signature for a different reason — the base tooling records no `server_exe`/`own_server` at all, so its own-leg detail lines read "None does not …". The base receipt therefore cannot distinguish "tooling absent" from "decoy present"; this run is the discriminating one (both fields populated, image still foreign).
3. Kept out of scope per the seat brief: the SKILL-registry gap for the two round-51 counters, the r41/r42/r43 `run_bad`/spot counts, the census E11 S499 used-by target, and the round-50 v5 counter's `lane=0` — all already on the lane L1's list.

## Cleanup

`kill` of servers handled by the tools; `rm -rf /fast/scratch/hyaku/kama-r51/J2DecoyHost` after copying the receipts below. Nothing was written inside `/home/vgpnk/Projects/shokunin/kama-shokunin` except this report and the `out/J2DecoyHost/` directory; the lane clone was mutated only in scratch. No tool installs.

## Artefacts (absolute)

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J2DecoyHost.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J2DecoyHost/c1-decoy.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J2DecoyHost/c1-buildtip-138af25b.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J2DecoyHost/fixture-decoy.diff
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J2DecoyHost/replay1-decoy.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J2DecoyHost/rerun-receipt-decoy.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/J2DecoyHost/host-b11909-sha256.txt
