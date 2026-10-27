# J6RenameOver — round 52 w1, lane kama (rename-over probe, C1)

**Verdict:** the round-52 build survives a rename-over of a byte-identical host `llama-server` over `<work>/server/<member>` — frozen C1 counter `met=True`, exit 0, the running image is the replay's sealed memfd (path inode differs) — while at the round-51 base the *same* rename-over is invisible: the round-51 replay returns `match=True` with zero mismatches and the round-51 counter returns `met=True`, exit 0. The round-51 D5 rename-over `[INFERENCE]` therefore resolves to **"a rename-over at the member path met the round-51 counter"**, not to a detected substitution.

Axes moved: operability (C1) — the round-52 mechanism is confirmed unaffected by path substitution; the round-51 record gains a measured closure fact.

Scratch: `/fast/scratch/hyaku/kama-r52/J6RenameOver` (removed at the end). One `git clone --shared` of the lane, toplevel asserted equal to `$S/lane` before each fixture commit (`git rev-parse --show-toplevel`), fixture identity `fx <fx@invalid>`. No tool installs; no lane write; no service change; no llama-server of mine left running (`pgrep -af llama-server | grep -c J6RenameOver` → `0`).

---

## 1. Probe A — build `5dacf2c7` + rename-over (expect met=True)

Fixture commit `d203d4543249f8c4244de9599234bbf2a6cb4d7a` (parent `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`), one file, +6 lines, inserted immediately after `sealed_member()` returns at `tools/kama-live-replay.py:400`:

```diff
         own_fd, own = sealed_member(archive, need["server.member"], want_srv)
+        # round-52 probe J6RenameOver (round-51 J4Hardlink left rename-over an [INFERENCE]):
+        # rename a byte-identical copy of the host's b11909 install over the extracted
+        # member path right after the memfd is filled; the running image must stay the memfd
+        _probe_copy = os.path.join(work, "probe-llama-server")
+        shutil.copy2("/home/vgpnk/.local/opt/llama-b11909/llama-server", _probe_copy)
+        os.replace(_probe_copy, server)
         argv[-2:-2] = ["--server-fd", str(own_fd)]
```

(`shutil.copy2`, not `copyfile`: the first attempt used `copyfile`, produced a mode-0644 member, and the live tool refused with `setup_error = "server-not-executable:<work>/server/llama-b11909/llama-server"` — a probe defect, fixed by preserving the mode; the member at the path is mode 755, nlink 1, byte-identical to the host file, sha256 `35ac50fb…d7ff0`, size 17864.)

Frozen counter (sha256 `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5`, equal to `preregistration.json` `counter_sha256`):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round52-replay-memfd-audit.py \
  --repo $S/lane --tip d203d4543249f8c4244de9599234bbf2a6cb4d7a \
  --scratch $S/c1-build --out $O/c1-rename-over-build.out
```

Output (exit **0**, full text in `c1-rename-over-build.out`):

```
tip=d203d4543249f8c4244de9599234bbf2a6cb4d7a
bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 754791 port 43319 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 2094477706 recorded, nonce 'kama witness b92889b1ec69b1bc' round-tripped
detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:151501 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: bind b2: pid 760289 port 35137 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1022012290 recorded, nonce 'kama witness a0723f04789a4fed' round-tripped
detail: sealed b2: running image '/memfd:llama-server (deleted)' 00:01:156363 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: bind b3: pid 779315 port 38825 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 615995709 recorded, nonce 'kama witness 31ea31f0fcc9d6ad' round-tripped
detail: sealed b3: running image '/memfd:llama-server (deleted)' 00:01:164684 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 1 rows new since base; 1 name memfd_create(2): ['| S500 |']
```

Direct evidence that the rename landed and is irrelevant to the image — one manual replay of receipt 1 through the same patched tip (`tools/kama-live-replay.py`, witness dir, `--witness-timeout 5`; exit 0, `match=True`, `mismatches=[]`):

```
server_exe = {"dev": "00:01", "inode": "165713", "nlink": 0, "opened": true,
              "path": "/memfd:llama-server (deleted)", "seals": 15,
              "sha256": "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0", "size": 17864}
own_server = {"dev": "00:01", "inode": "165713", "memfd": true, "seals": 15, "member": "llama-b11909/llama-server", ...}
path stat  = dev=103:05 inode=882670252 nlink=1 mode=100755 size=17864
```

The executed image (memfd `00:01:165713`) is not the file at the member path (`103:05:882670252`); the path is the host copy the probe renamed over it. This is exactly the round-52 claim's shape: the path no longer participates in what runs.

**Build-side boundary (measured, not inferred):** the rename-over is invisible only because the substituted bytes equal the frozen digest. A variant of the same probe that flips one byte of the copy before `os.replace` (same position) makes the replay refuse: `match=False`, `live_exit=2`, rerun `outcome=setup-error`, `setup_error = provenance-member-digest-mismatch` (live tool cross-checks the downloaded archive member against the `--server` path). So the live tool's path-based provenance check still guards a *differing* substitution; the round-52 C1 property is about the *running image*, and it holds.

## 2. Probe B — base `9ff76b1f` + the same rename-over (does round-51 notice?)

Fixture commit `70109e7bca37493eb67bb160cb02026e7ae130b0` (parent `9ff76b1f763512be2f554cbbfd0b2213b63b0847`), inserted after the archive-member digest check and before the replay's own fd hold, `tools/kama-live-replay.py:315-322`:

```diff
         if not isinstance(want_srv, str) or got_srv != want_srv:
             raise Refused(f"member-digest-mismatch:want={want_srv}:got={got_srv}")
+        # probe J6RenameOver: rename a byte-identical copy of the host's b11909 install over
+        # the extracted member path after the archive-based digest check, before the fd hold
+        _probe_copy = os.path.join(work, "probe-llama-server")
+        shutil.copy2("/home/vgpnk/.local/opt/llama-b11909/llama-server", _probe_copy)
+        os.replace(_probe_copy, server)
         res["inputs"].update({"archive": archive, "model": model, "server": server})
```

(The same position relative to evidence: after the archive-based verifications, before the path is bound and the server is started.)

Round-51 replay, receipt 1, manual run (exit **0**):

```
replay match=True refused=None mismatches=[] exit=0
server_exe = {"dev": "103:05", "inode": "280207190", "opened": true,
              "path": ".../wb/server/llama-b11909/llama-server",
              "sha256": "35ac50fb…d7ff0", "size": 17864}
own_server = {"path": ".../wb/server/llama-b11909/llama-server", "dev": "103:05", "inode": "280207190"}
path stat  = inode=280207190 nlink=1
```

It does **not** notice. The base replay opens the path *after* the substitution (`tools/kama-live-replay.py:351-352` at base: `own_fd = os.open(server, …)`, `own = os.fstat(own_fd)`), so its `own_server` and the live tool's `server_exe` are both the substituted inode; the nlink-1 check passes (a renamed-over copy has one link); digest, size and mode all match because the copy is byte-identical.

Round-51 counter (sha256 `e5753c453c30bd311e4c12fc962d324c7db482233b64b22795658b47b6ee5155`; blob at the base equals the blob in the lane HEAD):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-replay-exe-audit.py \
  --repo $S/lane --tip 70109e7bca37493eb67bb160cb02026e7ae130b0 \
  --scratch $S/c1-base --out $O/c1-rename-over-base-r51counter.out
```

Output (exit **0**):

```
tip=70109e7bca37493eb67bb160cb02026e7ae130b0
bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True
detail: own b1: running image 103:05:1489349909 is the extracted member, recorded in server_exe and own_server
detail: own b2: running image 103:05:415317747 is the extracted member, recorded in server_exe and own_server
detail: own b3: running image 103:05:1622493182 is the extracted member, recorded in server_exe and own_server
detail: newrow: 1 rows new since base; 1 name proc_pid_exe(5): ['| S499 |']
```

The counter's detail line calls the substituted file "the extracted member" because its `own_exe()` (`tools/round51-replay-exe-audit.py:351-378`) compares `/proc/<pid>/exe` to `os.stat(<work>/server/<member>)` *at observation time* — the same path the probe had already renamed over. The predicate's subject, "the very file that replay extracted" (docstring `tools/round51-replay-exe-audit.py:5`), is not what is compared.

**Detection boundary (measured control):** the same base tree with the rename moved after the fd hold (`own_fd = os.open(server)` at base `tools/kama-live-replay.py:351`, substitution at 352) makes the round-51 replay notice:

```
replay match=False mismatches=['server-exe:not-own-member:103:05:1889979910!=103:05:413570010',
                               'server-exe:member-links:0'] exit=1
own_server = {"dev": "103:05", "inode": "413570010"}
```

So round-51 detection depends solely on ordering relative to the replay's own `os.open(server)` — which the suspect replay controls. Under the placement used for the build probe, round-51 is silent.

## 3. Findings

1. **No defect in the round-52 C1 mechanism.** The measured build (`d203d454` = `5dacf2c7` + probe) keeps `bind=1 sealed=1 teardown=1 newrow=1 met=True` with a host-copy rename-over at the member path; the witnessed image is `/memfd:…`, nlink 0, seals 15, frozen digest, and `server_exe`/`own_server` agree on its dev/inode. The preregistered limit "a memfd filled from the host's byte-identical install meets" is untouched; this probe covers the *path* side and shows the path no longer participates in the image at all.
2. **Round-51 closure fact (not a counter bug to fix in place).** The round-51 counter's `own` leg met on a substituted image: `tools/round51-replay-exe-audit.py:5` ("the very file that replay extracted") and `:519` ("is the extracted member") state provenance the leg cannot observe, because `own_exe()` (`:369-378`) binds to `os.stat()` of the path at observation time and the base replay opens that path only after the digest check (`tools/kama-live-replay.py:351-352` at `9ff76b1f`). Resolution for the round-52 closure: rename-over joins copy (J3CopyDecoy) and hardlink (J4Hardlink) as a shape that met the round-51 count; the round-52 memfd image supersedes that binding. If the round-51 text is ever reused, the honest form is: "running image dev/inode equals the member path's dev/inode as stat()ed at observation time" — no "extracted" claim. Full proposed replacement text: `proposed-round51-own-detail.txt`.
3. **Scope note.** Nothing here widens C1: the 3-receipt counter result is the evidence; the base result is advisory (it measures the round-51 predicate, which this round supersedes) and must not be read as a round-52 leg.

## 4. Evidence files (all under `.ufo/waves/round-52/w1/out/J6RenameOver/`)

- `c1-rename-over-build.out` — frozen C1 counter at `d203d454`, `met=True`, exit 0.
- `c1-rename-over-base-r51counter.out` — round-51 counter at `70109e7b`, `met=True`, exit 0.
- `build-probe.patch`, `base-probe.patch`, `base-orderB.patch` — the three probe diffs (`git show` of the fixture commits / scratch diff).
- `build-rename-over-result.json`, `build-rename-over-rerun-receipt.json` — manual build replay (match true; memfd `00:01:165713` vs path `103:05:882670252`).
- `base-rename-over-result.json`, `base-rename-over-rerun-receipt.json` — manual base replay (match true, 0 mismatches).
- `base-orderB-result.json`, `base-orderB-rerun-receipt.json` — ordering control (2 mismatches).
- `build-mutated-result.json`, `build-mutated-rerun-receipt.json` — differing-bytes control (`provenance-member-digest-mismatch`, exit 2).
- `evidence.txt` — consolidated stat/receipt/counter-hash lines.
- `proposed-round51-own-detail.txt` — proposed corrected wording.

Commands used (all with `S=/fast/scratch/hyaku/kama-r52/J6RenameOver`, `O=<this dir>`, `TMPDIR=$S`):

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane           # toplevel asserted
git -C $S/lane checkout -B probe-build 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
# edit tools/kama-live-replay.py; commit with -c user.name=fx -c user.email=fx@invalid   -> d203d454
python3 <lane>/tools/round52-replay-memfd-audit.py --repo $S/lane --tip d203d454… --scratch $S/c1-build --out $O/c1-rename-over-build.out
git -C $S/lane checkout -B probe-base 9ff76b1f763512be2f554cbbfd0b2213b63b0847
# edit tools/kama-live-replay.py; commit fixture identity                                -> 70109e7b
python3 <lane>/tools/round51-replay-exe-audit.py  --repo $S/lane --tip 70109e7b… --scratch $S/c1-base  --out $O/c1-rename-over-base-r51counter.out
python3 $S/tree/tools/kama-live-replay.py       --receipt …/receipt-1.json --work $S/w2  --out $S/o2.json  --witness-dir $S/wd2 --witness-timeout 5
python3 $S/tree-base/tools/kama-live-replay.py  --receipt …/receipt-1.json --work $S/wb  --out $S/ob.json  --witness-dir $S/wdb --witness-timeout 5
python3 $S/tree-orderB/tools/kama-live-replay.py --receipt …/receipt-1.json --work $S/wb2 --out $S/ob2.json --witness-dir $S/wdb2 --witness-timeout 5
python3 $S/tree-mut/tools/kama-live-replay.py   --receipt …/receipt-1.json --work $S/wm  --out $S/om.json  --witness-dir $S/wdm --witness-timeout 5
```

Risks: none to the lane or fleet state; the probe commits exist only in the deleted scratch clone. Blockers: none.
