# Round 52 W1 — seat J5HostMemfd: C1 preregistered-limit probe (host-install memfd)

**Verdict: CONFIRMED.** A fixture build whose `sealed_member()` fills the memfd from the host's byte-identical `/home/vgpnk/.local/opt/llama-b11909/llama-server` instead of the archive's member stream is scored by the frozen C1 counter exactly as the build is: `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True`, exit 0 (fixture tip `bf38556daf3b354ce58045feaf04f4ef5f53c911`). The preregistered C1 limit ("a memfd filled from the host's byte-identical install meets the counter") holds with no residue. A second probe that fills from the *extracted* member path (`23651db1a8fdf73b49d6dd1e87d3a02c755be1e5`) also meets, so the unobserved quantity is the memfd's byte provenance in general, not only the host install.

No lane, fleet or shokuknow file was written; the only shared-state read was the lane clone source and the round-48 receipts. Nothing was installed (`strace` 7.2 and `bubblewrap` 0.13.1 are pre-existing host tools). No `llama-server` from my probes is left running.

## 1. Fixture build and the exact patch

Scratch `S=/fast/scratch/hyaku/kama-r52/J5HostMemfd`, one `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (toplevel asserted `$S/lane`), `git -C $S/lane checkout 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8`, then this edit to `tools/kama-live-replay.py:230-237` (full diff in `decoy.patch` beside this report):

```diff
@@ -226,14 +226,10 @@ def sealed_member(archive, member, want):
-    with tarfile.open(archive) as tf:
-        try:
-            ti = tf.getmember(member)
-        except KeyError:
-            raise Refused(f"member-absent-in-archive:{member}") from None
-        if not ti.isreg():
-            raise Refused(f"member-not-a-regular-file:{member}")
-        src = tf.extractfile(ti)
+    # ROUND-52 WAVE-1 DECOY (seat J5HostMemfd): the memfd is filled from the host's
+    # byte-identical b11909 install, not from the archive's member stream.
+    HOST_INSTALL = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
+    with open(HOST_INSTALL, "rb") as src:
         fd = os.memfd_create(os.path.basename(member), os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
```

Everything else is untouched: the same `memfd_create(name=basename(member), CLOEXEC|ALLOW_SEALING)`, the same streaming sha256 (`memfd-digest-mismatch`), the same `F_ADD_SEALS 15` + `F_GET_SEALS` check, the same `own` identity (dev/inode/seals/digest) handed back to `replay()`. The archive is still acquired, hashed and extracted, and the extracted member's digest is still checked against `server.sha256` (`tools/kama-live-replay.py:368-372`) before `sealed_member` runs — so the decoy is *only* wrong about where the memfd bytes come from.

Host binary digest matches the frozen server constant: `sha256sum /home/vgpnk/.local/opt/llama-b11909/llama-server` → `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`, size 17864; counter `SERVER_SHA` is the same string (`tools/round52-replay-memfd-audit.py:22`).

Commit (fixture identity, toplevel asserted first):

```
$ git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit -a -m "round-52 w1 J5HostMemfd decoy: sealed_member fills the memfd from the host b11909 install"
bf38556daf3b354ce58045feaf04f4ef5f53c911
 tools/kama-live-replay.py | 12 ++++--------
```

## 2. Frozen counter, verbatim run and output

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin
$ python3 tools/round52-replay-memfd-audit.py --repo "$S/lane" --tip bf38556daf3b354ce58045feaf04f4ef5f53c911 --scratch "$S" --out "$S/decoy-c1.out"
tip=bf38556daf3b354ce58045feaf04f4ef5f53c911
bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: bind b1: pid 394176 port 36743 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 683783130 recorded, nonce 'kama witness 8faab9e4e8cd4dbc' round-tripped
detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:161424 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
detail: bind b2: ... detail: sealed b2: running image '/memfd:llama-server (deleted)' 00:01:165682 seals 15 ...
detail: bind b3: ... detail: sealed b3: running image '/memfd:llama-server (deleted)' 00:01:180571 seals 15 ...
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 1 rows new since base; 1 name memfd_create(2): ['| S500 |']
exit=0   (real 0m28.9s)
```

Receipt kept as `decoy-c1.out`. Leg-for-leg it is indistinguishable from `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/measured/c1-build.out` (`met=True`, `sealedruns=3/3`, same `'/memfd:llama-server (deleted)' ... seals 15 ... recorded in server_exe and own_server` wording); only pids, ports, memfd inodes and nonces differ. Frozen counter bytes are the preregistered ones: `sha256sum tools/round52-replay-memfd-audit.py` = `053ff50261812de3236697dd8dc847b3dff9507f8290b0d42aaf65c12e1121f5` (matches the preregistration `counter_sha256`).

Second probe (fill from `$work/server/<member>` instead of `$work/download/<archive>`), `decoy2-extracted-path.patch`, tip `23651db1a8fdf73b49d6dd1e87d3a02c755be1e5`:

```
$ python3 tools/round52-replay-memfd-audit.py --repo "$S/lane" --tip 23651db1a8fdf73b49d6dd1e87d3a02c755be1e5 --scratch "$S" --out "$S/decoy2-c1.out"
bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True
exit=0   (real 0m18.5s)
```

Receipt kept as `decoy2-c1.out`. This shape is outside the literal preregistered limit wording (it does not read the host install) but inside its cause, and it is the shape a future round is most likely to meet by accident.

## 3. Why the counter cannot see it (file:line)

The counter observes only the *result*, never the source of the bytes:

- `tools/round52-replay-memfd-audit.py:361-395` (`sealed_exe`): opens `/proc/<pid>/exe`, `F_GET_SEALS`, `st_nlink`, link prefix `/memfd:`, sha256. All of these are properties of the finished memfd.
- `tools/round52-replay-memfd-audit.py:551-566` (`bind_one`): compares the rerun receipt's `server_exe` and the replay's `own_server` (dev, inode, seals) against that same observed image. `own_server` is the replay's *self-report* of the descriptor it created (`tools/kama-live-replay.py:254-255`), so it agrees with itself whatever was written into it.
- `tools/round52-replay-memfd-audit.py:617`: the counter checks that `tools/kama-live-replay.py` **exists** at the tip; it never reads its text, so the deleted `tarfile.open(...)` call is invisible.
- `tools/round52-replay-memfd-audit.py:565-576` (`newrow_leg`): only the `corpus/SOURCES.md` S-row.

The live child does not help either: `kama-llamacpp-live.py:786-812` (`sealed_fd`) verifies seals, size and `sha256 == --server`'s digest — a property of the bytes, which the host install and the archive member share by construction (that is exactly what "byte-identical" means in the limit).

## 4. What observation would distinguish it, and what is cheap

I ran each candidate on the frozen build tree (`$S/base-tree`, extracted from `5dacf2c7`) as control and on the decoy, one receipt (`round-48/c2/live/receipt-1.json`).

| Observation | Build (control) | Decoy | Distinguishes? | Cost |
|---|---|---|---|---|
| memfd name | `memfd_create("llama-server", MFD_CLOEXEC\|MFD_ALLOW_SEALING)` (`trace-base.log:2185`) | identical, same args, same line (`trace-decoy.log:2185`); `/proc/pid/exe` → `/memfd:llama-server (deleted)` | **no** | free |
| fd provenance (dev/inode/seals in `own_server`) | 00:01:<random>, seals 15 | same shape, different random inode | **no** — no fixed identity to compare, and it is the decoy's own report | free |
| open-set: does the replay open the host install? | 0 hits for `local/opt/llama-b11909/llama-server` in `trace-base.log` | 1 hit, `trace-decoy.log:484578 openat(..., "/home/vgpnk/.local/opt/llama-b11909/llama-server", O_RDONLY\|O_CLOEXEC) = 3`, same pid that runs `memfd_create` | **yes, for this decoy** | cheap: one `strace -f -y -e trace=%file` replay, ~6 s/run, both runs done in 12 s |
| availability: hide the host install | `bwrap --dev-bind / / --tmpfs /home/vgpnk/.local/opt python3 -I base-tree/tools/kama-live-replay.py ...` → `replay match=True exit=0` (`base-bwrap.out`) | same command on the decoy → `refused=could-not-run:FileNotFoundError:...'/home/vgpnk/.local/opt/llama-b11909/llama-server' exit=2` (`decoy-bwrap.out`) | **yes, for this decoy** | cheapest mechanical test: ~6 s/run, no tracing, works unprivileged (bubblewrap 0.13.1) |
| read/write ordering into the memfd | memfd write (`trace-rw-base.log:6216`, pid 902307) sits immediately after `read(3</.../download/llama-b11909-bin-ubuntu-x64.tar.gz>, ..., 1048576)` lines | decoy-2's memfd write (`trace-rw-decoy2.log:5598`, pid 927312) sits immediately after `read(3</.../server/llama-b11909/llama-server>, ... 17864)` | **yes for both file-source decoys, but fragile** | ~1 MB trace per run, needs `-y`/pid/offset correlation; a decoy that reads the archive and then fills from elsewhere satisfies it |

Reading the two trap prompts explicitly:

- **The memfd's name is not a lever.** The frozen build names the memfd `basename(member)` (`kama-live-replay.py:237`), which is `llama-server` for every source; naming it after the source (`/memfd:host-install`, `/memfd:archive-member`) would leak nothing either way, because the name is chosen by the replay, not derived from provenance.
- **fd provenance is not a lever.** The only provenance the counter could compare is the replay's own `own_server` dict, which the decoy controls; the observed side (`/proc/<pid>/exe`) carries no source information by design of `memfd_create(2)`.
- **strace is a lever only against a specific file.** The host-install open set and the mount-hide both catch *this* decoy because it reads a path the observer can see or hide. Decoy-2 reads the extracted tree, which the build also opens (`sha256_file(server)`, 17 opens of that path in `trace-base.log`), so the open set does not separate it; only write/read ordering does, and ordering is a heuristic a decoy can satisfy before diverging.

**Is any of it cheap enough to become a counter leg?** The mount-hide is: `bwrap` (or `unshare -m` + `mount -t tmpfs`) is available on this host, costs one extra replay per leg, and its logic is one line — "the replay still matches with `/home/vgpnk/.local/opt` emptied". It closes the exact preregistered shape (any decoy that reads the host install), but not decoy-2 and not a decoy that reads a copy of the bytes anywhere else. A complete closure is not cheap and arguably not possible from the counter's side: the kernel offers no attestation of which file's bytes were copied into a `memfd` (no fs-verity/IMA coverage of an anonymous file), so beyond ptrace-level read/write correlation the only sound design is to shrink *what the replay can reach* rather than to audit what it did.

## 5. Proposed next-round closure (proposal only; counters and preregistration are frozen)

1. **Cheap, partial (recommended):** add a `sealed-host-hidden` leg to the C1 counter's successor — run one replay under `bwrap --dev-bind / / --tmpfs /home/vgpnk/.local/opt` and require `match=True`. Verified working here in both directions (`base-bwrap.out`, `decoy-bwrap.out`); +6 s, unprivileged, and it kills the natural host-decoy without touching the build.
2. **Design change, stronger:** make the replay itself run under a mount namespace exposing only its `work/` tree (archive, extracted tree, model), so no on-disk server copy other than its own extraction is reachable; then "filled from the archive stream" is true by construction of its visible filesystem, and decoy-2 becomes impossible rather than merely unobserved. This is a build-side claim, not a counter leg.
3. **Not recommended:** a write/read-ordering leg (per §4). It is the only probe that separates decoy-2, but it demands `strace` in the counter, a ~1 MB trace per run, pid/fd/offset correlation, and it is defeated by a replay that reads the archive member it does not use.

## 6. Limits and risks of this probe

- The decoy keeps archive acquisition, extraction and the extracted-member digest check; a decoy that also removed those would be caught by other legs (and by `compare`), so this probe isolates exactly the memfd fill.
- The mount-hide test hides all of `/home/vgpnk/.local/opt`; a host layout with other tools under that directory could change behaviour of unrelated paths. On this host the replay reads none of them (base run under the same bwrap passed, `base-bwrap.out`).
- `bwrap` needs unprivileged user namespaces; if a future host disables them, the mount-hide leg must fall back to `unshare -m` (untested here) or be reported unavailable.
- Both decoy commits are ephemeral: the scratch clone is deleted per the operator directive, so `bf38556d` / `23651db1` will not resolve. Reproduction is the two patches beside this report applied to `5dacf2c7`, committed with a fixture identity, then the counter command in §2.

## 7. Artifacts (in `.ufo/waves/round-52/w1/out/J5HostMemfd/`)

- `decoy.patch` — host-install decoy diff; `decoy2-extracted-path.patch` — extracted-tree decoy diff.
- `decoy-c1.out`, `decoy2-c1.out` — frozen counter receipts (both `met=True`, exit 0).
- `trace-base.log`, `trace-decoy.log` — `strace -f -y -e trace=%file,memfd_create,fcntl` open sets; `trace-rw-base.log`, `trace-rw-decoy2.log` — read/write ordering into the memfd.
- `base-bwrap.out`, `decoy-bwrap.out`, `decoy2-bwrap.out` — mount-hide runs.

Reproduction of the counter run, from the fleet root:

```
S=/fast/scratch/hyaku/kama-r52/J5HostMemfd; mkdir -p "$S"; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" checkout 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8
git -C "$S/lane" apply /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J5HostMemfd/decoy.patch
git -C "$S/lane" -c user.name=fx -c user.email=fx@invalid commit -a -m decoy
cd /home/vgpnk/Projects/shokunin/kama-shokunin
python3 tools/round52-replay-memfd-audit.py --repo "$S/lane" --tip "$(git -C "$S/lane" rev-parse HEAD)" --scratch "$S"
rm -rf "$S"
```
