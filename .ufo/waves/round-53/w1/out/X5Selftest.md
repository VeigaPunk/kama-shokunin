# X5Selftest — round-53 selftest strength (kama lane, build c22602b)

Verdict: **both selftests pass at the frozen build, but 4 of the 7 required sabotages survive**: (c) the `no-archive-library` rule has no covering case, (d) `member_digests`' regular-member filter is untested, (e) the maps inode compare is unreachable in the selftest, and (g) the executable-bit filter is invisible to it. (f) is killed, but only by an assertion on the refusal *reason*, not by any hash of the newcomer. One validated case per survivor is proposed below; each fails the sabotaged copy and passes the frozen build.

Axes (godspeed): **A — kill coverage** (does one mutation of one rule turn a selftest red?), **B — proposal validity** (the new case must fail the sabotage and pass the unmutated build, cheaply and deterministically).

## Setup

```
S=/fast/scratch/hyaku/kama-r53/X5Selftest; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
git -C "$S/lane" rev-parse --show-toplevel        -> /fast/scratch/hyaku/kama-r53/X5Selftest/lane
git -C "$S/lane" checkout -q c22602bd8d83ab26349d1087e916ca537ee4f9d1
git -C "$S/lane" rev-parse HEAD                   -> c22602bd8d83ab26349d1087e916ca537ee4f9d1
sha256sum $S/lane/tools/kama-live-replay.py       -> 6c0bfbdfa586e0beb47a8ba1f1c617b9db295dfe4f7357299493e04989e98102
sha256sum $S/lane/tools/kama-llamacpp-live.py     -> 82b253e58ae75457b3dc81e6a7450510a50f815e3503bc6a2b61b7d1342b349d
```

The lane worktree has since moved: `git status --porcelain -- tools/` there reports `M tools/kama-live-replay.py`, `M tools/kama-llamacpp-live.py` (uncommitted wave fixes; `verify_code` gained an `own` parameter and `malformed`/`foreign-memfd` problems). Per the seat spec every run below used the frozen `c22602b` clone, not that worktree. The proposed patches also apply to the current worktree by dry run (see Proposal validation).

## Baseline (frozen build)

```
python3 $S/lane/tools/kama-live-replay.py --selftest --scratch $S/base
  -> KLR_SELFTEST pass=43 fail=0   (exit 0)
python3 $S/lane/tools/kama-llamacpp-live.py --selftest
  -> selftest: ok; closed tcp6 listeners ::1:36161, ::ffff:127.0.0.1:36705   (exit 0)
```

Logs: `selftest-replay-build.log`, `selftest-llamacpp-build.log`.

## Sabotage matrix (one mutation at a time, scratch copies only)

| # | mutation | site (frozen) | selftest | observed | killed? |
|---|---|---|---|---|---|
| a | digest mismatch accepted (`elif e["sha256"] != digests[member]` → `elif False`) | `tools/kama-live-replay.py:343` | replay | `FAIL code-digest-differs: exit=0`; `pass=42 fail=1`, exit 1 | **yes** |
| b | `uid != 0` outside the tree treated as host (`elif e.get("uid") != 0` → `elif False`) | `tools/kama-live-replay.py:347` | replay | `FAIL code-foreign: exit=0`; `pass=42 fail=1`, exit 1 | **yes** |
| c | `no-archive-library` rule deleted (`if not members:`) | `tools/kama-live-replay.py:351-352` | replay | `pass=43 fail=0`, exit 0 | **NO** |
| d | `member_digests` hashes non-regular members (`and ti.isreg()` removed) | `tools/kama-live-replay.py:299` | replay | `pass=43 fail=0`, exit 0 | **NO** |
| e | maps inode compare removed (`str(st.st_ino) != ino`) | `tools/kama-llamacpp-live.py:818` | llamacpp | `selftest: ok`, exit 0 | **NO** |
| f | `(deleted)` branch removed, deleted pathnames opened | `tools/kama-llamacpp-live.py:804` | llamacpp | `AssertionError: code_mappings hashed a renamed-over path`, exit 1 | **yes** (by reason only, F5) |
| g | executable-bit filter removed (`'x' not in f[1]`) | `tools/kama-llamacpp-live.py:793` | llamacpp | `selftest: ok`, exit 0 | **NO** |

Mutation diffs: `mutations-replay.diff`, `mutations-llama.diff`. Logs: `sabotage-{a..g}.log`.

Caveat on method: (e)/(g) first run flat in a directory without the lane's `registry/endpoint-consumers.tsv` aborted with `SetupError: registry-unreadable` — that is not a kill. The matrix rows above are the rerun with the copies placed at `$S/run-<x>/tools/kama-llamacpp-live.py` and `$S/run-<x>/registry -> $S/lane/registry` (the tool resolves `LANE = SCRIPT.parent.parent`, `tools/kama-llamacpp-live.py:92-94`).

## Findings

**F1 (survivor c — the existing case is mislabeled).** The existing case `code-no-archive-library` (`tools/kama-live-replay.py:713`) rewrites the first mapping's path to `/usr/x` but keeps `'uid':y.st_uid`, i.e. the test user's uid. `verify_code` then refuses it at the *foreign* branch, so the emptiness rule is never the reason the case goes red. Direct proof with an empty tar and the exact mutated entry shape:

```
frozen:      probs = ['code-mapping:foreign:/usr/x:uid=1000', 'code-mapping:no-archive-library']
sabotage c:  probs = ['code-mapping:foreign:/usr/x:uid=1000']          # selftest still green
```

(`attribution-no-archive-library.log`.) Removing the rule alone leaves the suite at 43/43.

**F2 (survivor d).** The fixture archive holds only regular members (`tarfile.add` of `build/bin`), and `member_digests` is only queried with mapping names, so `ti.isreg()` never changes an outcome. Against the sabotaged copy a **hardlink member** is silently accepted as an archive library: `tarfile.extractfile` resolves `LNKTYPE` to its target's bytes, the digest matches the mapped file's hash, and `verify_code` returns `verified: True` with `members: {'build/bin/libhard.so': ...}` (`proposal-vs-sabotage-d.log`).

**F3 (survivor e).** The only rename-over assertion (`tools/kama-llamacpp-live.py:1819`) is pre-empted by the `(deleted)` branch at `:804`, which refuses before any `os.open`. So the inode compare at `:818` has zero coverage even though it is the only identity check for root-owned host files (`sdev != dev` is waived when `st.st_uid == 0`).

**F4 (survivor g).** `code_mappings` dedupes on `(path, dev, ino)` and the selftest looks the exe up by path only, so the first row seen decides and `r--p`/`rw-p` data mappings are recorded unnoticed when the `x` filter is removed. Operational consequence (inference from `verify_code`, not a counter run): a removed filter records the mmapped **model** (and any data mapping under the tree) as code, and `verify_code` rejects it as `not-a-member` — C1 would go `met=False` on a sabotage the selftest does not see. The proposed case shows the recording empirically on an `mmap(PROT_READ)` fixture.

**F5 (f killed, but weakly).** With the `(deleted)` branch removed, opening the literal `"<path> (deleted)"` fails with `ENOENT`, so the newcomer at the un-suffixed path is still never hashed (the inode compare is the backstop); the red comes from `reason == 'mapped-file-deleted'` (`:1819`). It is a kill, but it asserts the label, not the property. No change required by this seat; note it if the reason string is ever refactored.

**F6 (harness pitfall, not a code defect).** A copied `kama-llamacpp-live.py` outside the lane tree aborts `--selftest` at `refused_ports()` with `SetupError: registry-unreadable`, which reads as exit 1 and could be mistaken for a kill. Any repeat of this exercise must keep the lane layout (`tools/` + `registry/` sibling).

## Proposed cases (validated)

Both patches are against the frozen `c22602b` files; they are also dry-run clean on the current (in-flight) worktree, at the offsets shown.

### `prop-kama-live-replay.patch` (kills c, d)

```diff
--- a/tools/kama-live-replay.py
+++ b/tools/kama-live-replay.py
@@ -707,6 +707,38 @@
                       and list(res["own_code"].get("members", {})) == ["build/bin/libfake.so"]
                       and res["own_code"].get("host") == ["/usr/lib/libc.so.6"],
                       f"exit={code} own_code={res.get('own_code')} mism={res['mismatches']}"))
+        # round 53 (X5Selftest survivors c and d): verify_code's refusals called directly,
+        # so each rule is exercised alone instead of as a side effect of another entry
+        import io
+        oc, probs = verify_code({"read": True, "mappings": [
+            {"path": "/usr/lib/libc.so.6", "dev": "00:1e", "inode": "1", "opened": True,
+             "uid": 0, "sha256": "0" * 64}]}, arc, os.path.join(d, "no-tree"))
+        cases.append(("code-hostonly-no-library",
+                      probs == ["code-mapping:no-archive-library"]
+                      and oc == {"verified": False, "members": {}, "host": ["/usr/lib/libc.so.6"]},
+                      f"own_code={oc} probs={probs}"))
+        hard = os.path.join(d, "hard.tar.gz")
+        payload = b"\x7fELF hardlinked payload " + os.urandom(16)
+        with tarfile.open(hard, "w:gz") as tf:
+            reg = tarfile.TarInfo("build/bin/libpayload.so")
+            reg.size = len(payload)
+            tf.addfile(reg, io.BytesIO(payload))
+            link = tarfile.TarInfo("build/bin/libhard.so")
+            link.type = tarfile.LNKTYPE
+            link.linkname = "build/bin/libpayload.so"
+            tf.addfile(link)
+        htree = os.path.realpath(os.path.join(d, "hard-tree"))
+        os.makedirs(os.path.join(htree, "build", "bin"))
+        hpath = os.path.join(htree, "build", "bin", "libhard.so")
+        with open(hpath, "wb") as fh:
+            fh.write(payload)
+        oc, probs = verify_code({"read": True, "mappings": [
+            {"path": hpath, "dev": "00:01", "inode": "1", "opened": True, "uid": 1000,
+             "sha256": hashlib.sha256(payload).hexdigest()}]}, hard, htree)
+        cases.append(("code-non-regular-member",
+                      "code-mapping:not-a-member:build/bin/libhard.so" in probs
+                      and "build/bin/libhard.so" not in oc["members"],
+                      f"own_code={oc} probs={probs}"))
         # the sealed memfd is filled from the archive's member stream, not from the path
         fd, ident = sealed_member(arc, "build/bin/llama-server", ssha)
         try:
```

### `prop-kama-llamacpp-live.patch` (kills e, g)

```diff
--- a/tools/kama-llamacpp-live.py
+++ b/tools/kama-llamacpp-live.py
@@ -1814,6 +1814,45 @@
         finally:
             proc.kill()
             proc.wait()
+    # round 53 (X5Selftest survivors e and g): the maps line's inode and its executable bit
+    # are each checked alone - a path that resolves to another inode is refused, and a
+    # mapping without `x` is data, never code
+    import builtins
+    with tempfile.TemporaryDirectory(prefix='kama-code-map-x5-') as directory:
+        other = os.path.join(directory, 'not-the-mapping')
+        with open(other, 'wb') as fh:
+            fh.write(b'not the mapped file')
+        ost = os.stat(other)
+        row = ('00400000-00401000 r-xp 00000000 %02x:%02x %d %s\n'
+               % (os.major(ost.st_dev), os.minor(ost.st_dev), ost.st_ino + 12345, other))
+        _real_open = builtins.open
+        builtins.open = lambda p, *a, **k: io.StringIO(row) if str(p).endswith('/maps') else _real_open(p, *a, **k)
+        try:
+            got = code_mappings(os.getpid())
+        finally:
+            builtins.open = _real_open
+        ent = next((e for e in got.get('mappings') or [] if e.get('path') == other), None)
+        if not (ent and ent.get('opened') is False and ent.get('reason') == 'path-is-not-the-mapped-file'):
+            raise AssertionError(f'code_mappings accepted a path whose inode is not the mapped one: {ent}')
+        body = os.path.join(directory, 'mapped-data.bin')
+        with open(body, 'wb') as fh:
+            fh.write(b'data, not code\n' * 64)
+        mmap_child = ("import mmap,os,sys,time\n"
+                      "fd=os.open(sys.argv[1], os.O_RDONLY)\n"
+                      "m=mmap.mmap(fd, 0, prot=mmap.PROT_READ)\n"
+                      "print('ready', flush=True)\n"
+                      "time.sleep(30)\n")
+        proc = subprocess.Popen([sys.executable, '-c', mmap_child, body],
+                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
+        try:
+            proc.stdout.readline()
+            got = code_mappings(proc.pid)
+            leaked = [e for e in got.get('mappings') or [] if e.get('path') == body]
+            if got.get('read') is not True or leaked:
+                raise AssertionError(f'code_mappings recorded a non-executable mapping: {leaked}')
+        finally:
+            proc.kill()
+            proc.wait()
     if code_mappings(2 ** 22 + 7).get('read') is not False:
         raise AssertionError('code_mappings read maps of a pid that does not exist')
```

### Validation

| proposed suite | run against | result |
|---|---|---|
| replay + both cases | frozen replay | `KLR_SELFTEST pass=45 fail=0`, exit 0 (`proposal-replay-original.log`) |
| replay + both cases | sabotage c copy | `FAIL code-hostonly-no-library` … `pass=44 fail=1` (`proposal-vs-sabotage-c.log`) |
| replay + both cases | sabotage d copy | `FAIL code-non-regular-member` … `pass=44 fail=1` (`proposal-vs-sabotage-d.log`) |
| llamacpp + both cases | frozen live | `selftest: ok` + `code_mappings_selftest ok` (`proposal-llamacpp-original.log`) |
| llamacpp + both cases | sabotage e copy | `AssertionError: code_mappings accepted a path whose inode is not the mapped one` (`proposal-vs-sabotage-e.log`) |
| llamacpp + both cases | sabotage g copy | `AssertionError: code_mappings recorded a non-executable mapping` (`proposal-vs-sabotage-g.log`) |
| both patches, `patch -p1 --dry-run` | current in-flight worktree copy | `Hunk #1 succeeded at 726 (offset 19 lines)` / `at 1820 (offset 6 lines)`, exit 0 (`proposal-dryrun-current-worktree.log`) |

### Risks

- The proposed cases are validated against the frozen `c22602b` build only. The current worktree's uncommitted wave hunks (replay `malformed`/`foreign-memfd`, llama `anonymous-memfd`) do not touch the four rules exercised here, and the patches dry-run clean there — [INFERENCE], since that tree is being edited concurrently and was not run as a whole.
- No C1/C2 counter run was made from this seat (other seats own it); F4's counter-level impact is inferred from `verify_code`'s code path, not measured.
- Sabotage copies and patches live only in scratch/out; no lane file was edited, nothing was committed, no service was started (selftests only bind and immediately close their own loopback listeners), and no tool was installed.

## Artifacts

All under `.ufo/waves/round-53/w1/out/X5Selftest/`: `selftest-replay-build.log`, `selftest-llamacpp-build.log`, `sabotage-{a,b,c,d,e,f,g}.log`, `mutations-replay.diff`, `mutations-llama.diff`, `attribution-no-archive-library.log`, `prop-kama-live-replay.patch`, `prop-kama-llamacpp-live.patch`, `proposal-replay-original.log`, `proposal-vs-sabotage-{c,d}.log`, `proposal-llamacpp-original.log`, `proposal-vs-sabotage-{e,g}.log`, `proposal-dryrun-current-worktree.log`.
