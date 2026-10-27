# Sen1Mem — C1 memory read: exposure, fail-closed shape, archive trust, code_mappings opens

**Verdict: the memory read is read-only, its bytes never reach the receipt, and a `ptrace_scope=2`
host fails closed on exactly one leg — but the reference those bytes are compared against is a
plain file inside the counter's own scratch dir that the launched replay can rewrite, so C1's code
leg can be made to pass on non-release library bytes (HIGH, demonstrated with the counter's own
`code_observe`).**

## 0. Ground and pinning

- Host: Linux 7.2.11-arch1-1, uid 1000, `/proc/sys/kernel/yama/ptrace_scope` = **1**, python 3.14.8.
- Counter under review: `tools/round53-replay-code-audit.py`, sha256
  `1a7a144204ba8b7ea9791706ab5fc90f1dab55db12a824a1af5ae89a81b75d8f` — equal to
  `counter_sha256` in `.ufo/waves/round-53/preregistration.json` (C1) and unmodified in the lane
  working tree.
- Tool revisions cited for the live tool / replay are the **build** `c22602bd…` (`git show
  c22602bd:tools/kama-llamacpp-live.py`, `…/kama-live-replay.py`). The lane working tree is dirty
  from other wave seats' edits (`git status --porcelain`: `M tools/kama-live-replay.py`,
  `M tools/kama-llamacpp-live.py`, `M SKILL.md`, …), so every line number below is the build's.
- I did **not** run either counter end to end (not needed for these defects, and no network run was
  required). The L1's receipts are cited only as copies: `c1-build.out.copy`, `base.c1.out.copy`.
- Probes run the counter's **own functions**, imported from a byte copy of the frozen file
  (`sha256` re-checked), against real processes and real tarfiles. Nothing was wrapped in a tracer.

## 1. F1 (HIGH) — the "own download" is writable by the process under audit

Code path:

1. the counter writes its download to `<S>/counter-archive.tar.gz` (line 747), hashes the **file**
   once (`sha_file(apath) != ARCHIVE_SHA`, line 752), then opens it **by path** and holds it
   (`Archive.__init__` → `tarfile.open(path)`, line 379).
2. it then starts the replay (`bind_one` 560 → `start_replay` 516) with an environment built by
   `prepare_env` that sets `TMPDIR = <S>/tmp-<tag>` (line 499). So the replay computes
   `S = dirname(TMPDIR)` and the reference sits in that same directory.
3. same uid, no privilege boundary: `<S>` is `mkdtemp` 0700 but owned by the counter's uid, the file
   is 0644 (measured), and the replay — code at `--tip`, i.e. the thing being audited — can rewrite
   it at start-up, before the counter's first member read (the cache is empty then, lines 383-390).
4. member bytes are read from the still-open descriptor at `member()` time
   (`tarfile.ExFileObject` seeks `ti.offset_data`), so an in-place rewrite that keeps the layout
   (same names, sizes, order — trivially produced by the attacker) changes what `want` is (line 424).

Evidence:

```
$ python3 archive-ref-probe.py            # out-archive-ref.txt, rc=0
counter download            …/sen1mem-ref-7b1bpsjf/counter-archive.tar.gz
frozen digest of download   14f3b349188fbc95... (compared once, line 752)
replay TMPDIR               …/sen1mem-ref-7b1bpsjf/tmp-b1
-> dirname(TMPDIR) is S     True; the reference sits in it: …/counter-archive.tar.gz
-> same uid as the counter  uid 1000; file mode 0o644; S mode 0o700
replay-like child           rewrote (same layout, same uid) …/counter-archive.tar.gz rc=0
digest after the rewrite    c84236e2c41b2f21...  equals the frozen digest: False
arc.member('llama-b11909/libggml-base.so.0.27.0') -> 'ATTACKER-SWAPPED-BYTESAT'  RELEASE? False  SWAPPED? True
```

```
$ python3 keys-bounds-probe.py            # out-keys-bounds.txt, rc=0  (part 1)
   child 3138773: 10 executable file mappings (the counter's filter)
   1a honest archive            4 ranges compared, 4 problems
      code: mapped bytes … of libggml-cpu-zen4.so differ from the archive member
      code: mapped bytes … of libggml.so.0.27.0 differ from the archive member
      code: mapped bytes … of libggml-base.so.0.27.0 differ from the archive member
      code: mapped bytes … of libllama-server-impl.so differ from the archive member
      leg `not cprobs and cobs is not None` -> False  (code=0: control holds)
   1b archive rewritten to those bytes  4 ranges compared, 0 problems: []
      leg `not cprobs and cobs is not None` -> True  (code=1: FALSE PASS)
```

1a is the wave's declared ablation control (a library swapped after its member check) and the
counter catches it. 1b is the same four swapped libraries with the counter's reference rewritten:
zero problems, `code=1`, on bytes that are not the release archive's.

**Why the other checks do not cover it.** The receipt/`own_code` digest comparisons in `bind_one`
hash the *same* mutable `arc` (line 625 → 628/630), so they agree with a receipt recorded from the
same swapped bytes; the only other guard — the replay's archive-stream digest — is computed by the
audited code itself (`kama-live-replay.py:290` `member_digests`, `:305` `verify_code` at the build,
`:319`, `:329`). The mem comparison is the one check that does not trust the tip, and its reference
is under the tip's control. A replay that (a) rewrites `<S>/counter-archive.tar.gz` with its swapped
members and (b) puts the same bytes into its tree satisfies both, i.e. **C1 can report `met=True`
while the server executes non-release library bytes**. The claim's own wording — "compared with its
own download of the archive" — is unenforced after download; the prereg's limits do not disclose it.

Smallest remediation (`c1-reference-immutability.diff`, hunks 1-2): read the archive once, hash
*those bytes*, and parse *those bytes*:

```diff
     def __init__(self, path):
-        self.tf = tarfile.open(path)
+        with open(path, "rb") as fh:
+            self.blob = fh.read()
+        self.tf = tarfile.open(fileobj=io.BytesIO(self.blob))
```
```diff
-            if sha_file(apath) != ARCHIVE_SHA:
+            arc = Archive(apath)      # one read: the bytes hashed are the bytes parsed
+            if hashlib.sha256(arc.blob).hexdigest() != ARCHIVE_SHA:
                 detail.append("counter archive download does not hash to the frozen digest")
+                arc = None
             else:
-                arc = Archive(apath)
                 detail.append("counter archive: its own download, frozen digest")
```
Validated in scratch: `patch -p1 --dry-run` rc=0, `patch` + `python3 -m py_compile` ok, and
`out-fix-check.txt` with the patched module shows the same rewrite no longer moves `member()` and
the digest is still the download's. (Alternative, if the frozen counter cannot change: move the
reference out of the replay's reachable tree, e.g. into a dir the replay cannot traverse, which this
kernel does not offer for the same uid — hence the bytes-in-memory fix.)

## 2. F2 (LOW here, MEDIUM on a `ptrace_scope=0` host) — attach without a descendant gate

`bind_one` records `server pid <pid> does not descend from the replay process <rp>` (lines 576-577)
and **continues**: `observe` (578), `sealed_exe` (579) and `code_observe` (581) then open
`/proc/<pid>/{exe,environ,fd,maps,mem}` for a pid taken from `<wd>/ready.json`, which the replay
writes (`wait_ready`, 528). On this host `ptrace_scope=1` denies the attach (probe B below). On a
`ptrace_scope=0` host — which the counter's own docstring admits ("Yama ptrace_scope 0 or 1", line
70) — the ATTACH read succeeds for **any same-uid pid**, so the audited replay chooses which
same-uid process's memory and `/proc/<pid>/environ` the counter reads. Exposure is bounded (only
digests and pass/fail text are recorded, line 433), but a read reachable from replay-controlled data
is the wrong shape. Fix: hunk 3 of the diff — no `/proc` read unless `descends_from(pid, rp)`.

## 3. F3 (LOW) — unbounded per-row allocation, and zero padding past the member

`code_observe` takes the row length from the server's own maps and allocates it twice:

```python
422  lo, hi = (int(v, 16) for v in f[0].split("-"))
424  want = data[off:off + (hi - lo)]
425  want += b"\0" * ((hi - lo) - len(want))
427  got = os.pread(mem, hi - lo, lo)
```

```
$ python3 keys-bounds-probe.py            # out-keys-bounds.txt, part 3
   maps row 7fb1b0c00000-7fb1c0c00000 perms r-xs: 268435456 bytes (256 MiB), archive member 'big-extra.so' is 4096 bytes
   code_observe -> 1 ranges, problems ["code: no mapped archive member matches libllama-server-impl.so (mapped: ['big-extra.so'])", …]
   VmHWM 27824 kB -> 550424 kB
```

So one map row of the audited server drives ~2×N bytes of the counter's memory, with no cap. The
same output also shows the padding rule: a 4096-byte member mapped over a 256 MiB file produced **no
"mapped bytes differ" problem** — bytes past the member's end are expected to be zeros and pass.
Fix: hunk 3 of the diff (cap at 64 MiB, refuse the row) and treat a row extending past the member as
a problem instead of padding it.

## 4. Question 1 — what the read exposes, and does the counter ever write?

- **Open**: `os.open(f"/proc/{pid}/mem", os.O_RDONLY)` (line 405). **Reads**: only `os.pread`
  (line 427). Static check: `grep -n "O_RDWR\|O_WRONLY\|pwrite\|os\.write\|ptrace(" tools/round53-replay-code-audit.py` → no match (grep exit 1). The counter never writes through this descriptor.
- Empirical (`out-mem-leg.txt`, part A, rc=0): a descendant child wrote a marker at a printed
  address; the probe `pread` returned `b'SEN1MEM-MARKER '`; `os.write(fd, b"\x00")` →
  `EBADF (Bad file descriptor)`. The read is one-way.
- Exposure: `PTRACE_MODE_ATTACH_FSCREDS` on the process the counter started — `proc_pid_mem(5)`:
  "Permission to access this file is governed by a ptrace access mode `PTRACE_MODE_ATTACH_FSCREDS`
  check" — and under `ptrace_scope=1` "the target process must be a descendant of the caller"
  (`man 2 ptrace`, `/proc/sys/kernel/yama/ptrace_scope`, value 1). It reads only executable rows
  with a `/` pathname (lines 411-416), i.e. the server's text segments, and the outcome stored is a
  boolean plus the string `mapped bytes <range> (offset …) of <member> differ from the archive
  member` (line 433) — **no byte content is recorded anywhere**.
- `observe` (341) additionally reads `/proc/<pid>/exe` (sha256), `/proc/<pid>/environ` (only to test
  for the planted canary), `/proc/<pid>/fd` (socket ownership) and `/proc/<pid>/maps` — all
  read-only, all on the counter's own descendant. Residual exposure beyond that: F2 only.

## 5. Question 2 — under `ptrace_scope 2` the receipt says `code=0`, and it fails closed

Yama at 2: "Only processes with the `CAP_SYS_PTRACE` capability in the user namespace of the target
process may perform `PTRACE_MODE_ATTACH` operations" (`man 2 ptrace`). Yama gates ATTACH, not READ,
so `/proc/<pid>/maps` and `/proc/<pid>/exe` (`PTRACE_MODE_READ_FSCREDS`, per `proc_pid_maps(5)` and
`proc_pid_exe(5)`) still open; only `/proc/<pid>/mem` is refused. Probe B reproduced exactly that
state from a non-descendant under scope 1:

```
$ python3 mem-leg-probe.py <non-descendant-pid>     # out-mem-leg.txt, part B, rc=0
   /proc/<pid>/maps (PTRACE_MODE_READ)   readable: 43 rows, 7 executable
   c1.code_observe(pid, tree, arc=None)  -> None
      problem: code: /proc/3416901/mem unopenable: Permission denied
   c1.sealed_exe(pid) (READ mode)        -> tuple (image opened), problems 4: ['sealed: F_GET_SEALS …']
   counter leg expression (line 660) `not cprobs and cobs is not None` -> False
```

Code path, line by line (counter, frozen):

- `observe` (341): `sha_file(/proc/<pid>/exe)`, `environ`, `maps` — READ mode → still work, so the
  bind problems do not change;
- `sealed_exe` (462): `/proc/<pid>/exe` opened READ → sealed leg unchanged;
- `code_observe` (393): maps read succeeds (411), then line 405 raises `EPERM` →
  line 407 `probs.append(f"code: /proc/{pid}/mem unopenable: {exc.strerror}")` → line 408
  `return None`;
- `bind_one` (560): `cobs` is `None`, so the leg expression at line 660
  (`not cprobs and cobs is not None`) is **False**; `coded` is not incremented → `coderuns=0/3`;
  `met` (line 776) is False; the receipt is written to `--out` (784-786); `return 0 if met else 1`
  (787) → exit 1.

The receipt it would print:

```
tip=<tip>
bind=1 sealed=1 code=0 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=0/3 met=False
detail: code b1: code: /proc/<pid>/mem unopenable: Operation not permitted
detail: code b2: code: /proc/<pid>/mem unopenable: Operation not permitted
detail: code b3: code: /proc/<pid>/mem unopenable: Operation not permitted
```

(EPERM is what the Yama check returns; the scope-1 non-descendant path above produced EACCES from
the same `open` — same branch, line 407.)

**Fail closed: yes.** The failed read cannot turn a leg green (`cobs is None`), no other leg is
skipped, nothing in the lane, the tree or the server is mutated on that path, and the exit status is
non-zero. Two caveats, neither a soundness defect:

1. the failure is *claim-failure shaped* (`met=False`, exit 1) rather than "could not evaluate" —
   exit 2 exists only for git failures (line 726). A preflight on ATTACH access (a throwaway child
   whose `/proc/<pid>/mem` the counter opens before starting anything) → exit 2 would keep a scope-2
   host from writing a defect-shaped receipt.
2. the docstring already declares the envelope "ptrace_scope 0 or 1" (line 70), so this is outside
   the declared support, not a hidden dependency.

## 6. Question 3 — archive download, member sizes, path traversal

- **Size bounds**: the archive is digest-pinned before it is parsed (`sha_file(apath) != ARCHIVE_SHA`,
  752), so declared member sizes are bounded by the pinned ~30 MB archive; `Archive.cache`
  (381-390) keeps each member it was asked for — bounded by those members, shared across the three
  replays. The unbounded allocation is the *map-row* buffer, not the archive: F3.
- **Member names are only keys**: `Archive.member` → `tarfile.getmember(name)` (line 384) is an
  exact-name lookup. From `out-keys-bounds.txt` part 2: `'../etc/passwd'` → `None`, `'/etc/passwd'`
  → `None`, `'libggml.so.0.27.0/../../x'` → `None`, `''` → `None`. A maps path that string-prefixes
  the tree but escapes it (`<tree>/../../x`) is `relpath`'ed to a non-member and becomes a problem
  (line 420) — never a read outside the archive. The tree branch also never `stat`s the path: the
  mapped *bytes* are what is compared, so a lying pathname cannot make the counter read a file.
- **Extraction of the tip** (730-732) drops symlinks/hardlinks (`None` from the filter) and applies
  `tarfile.data_filter`: a crafted member `../../sen1mem-escaped` raised
  `OutsideDestinationError` and nothing was written outside the destination; the symlink member was
  dropped (`out-keys-bounds.txt` part 2: `escaped file exists: False; symlink extracted: False`). The
  tip comes from `git archive` (which cannot carry such names), so this is defence in depth.
- The real defect on this surface is not traversal but **reference mutability**: F1.

## 7. Question 4 — new exposure in the live tool's `code_mappings`

At the build (`tools/kama-llamacpp-live.py:774`): every executable mapping with a `/` pathname is
opened `O_RDONLY | O_NOFOLLOW | O_NONBLOCK` (804), `fstat`ed (810) and hashed only when the inode
matches (and the dev, except for root-owned files) (812-813); `(deleted)` paths are never opened
(798-801); `/memfd:` rows are skipped (792-793); only `size`, `uid` and `sha256` are recorded
(825-826).

- **No writes, no content**: the descriptor is read-only and only a digest leaves the function.
- **`O_NOFOLLOW` is final-component only**, but the inode/dev comparison closes rename-over and
  mid-path symlink substitution; a mismatch is recorded as `path-is-not-the-mapped-file`, never guessed.
- **New exposure = a confused-deputy read**: the *set of paths opened* is chosen by the audited
  server's `/proc/<pid>/maps`, not by the tool. Any readable file the server maps is opened and read
  to `st_size` inside the audit tool. Nothing but a digest is kept, so there is no exfiltration; the
  cost is **unbounded time**: there is no size cap on the hash loop (817-823), so a server that maps
  a huge (e.g. sparse 100 GB) file makes the live tool hash 100 GB before it returns. Recommend
  skipping rows above a bound with a recorded reason (the same class of fix as F3).
- **Root-owned files are matched by inode only** (dev deliberately not compared, 812-813; disclosed
  in the docstring). Consequence for evidence: `code_mappings[].sha256` can be the digest of a
  *different* root-owned file that happens to share the inode number on another filesystem, and
  `own_code.host` can name a path that is not the mapping. The counter's host branch has the same
  rule (`round53-replay-code-audit.py:447`), and host files' bytes are not compared at all — so this
  costs receipt accuracy, not soundness; it is the weakest statement in an otherwise byte-level claim.
- Not a finding: `O_NONBLOCK` means a FIFO cannot stall the open, and the tool only opens paths the
  server had already mapped, which requires the server to have had access to them.

## 8. Proposed patch — validated, not applied

`c1-reference-immutability.diff` (three hunks: immutable reference / row cap / descendant gate).

```
$ cp <frozen counter> $S/pt2/tools/round53-replay-code-audit.py
$ cd $S/pt2 && patch -p1 --dry-run < c1-reference-immutability.diff   -> rc=0
$ patch -p1 -s < … && python3 -m py_compile tools/round53-replay-code-audit.py   -> compiles OK
$ python3 out-fix-check.txt (patched module, out-fix-check.txt)
  member() bytes are the download's: True
  blob digest still the frozen one:   True
  ranges read: 0 problems: ['code: maps row 7f9418000000-7f9428000000 of big.so is 268435456 bytes; not read']
  VmHWM: 29716 kB
```

## 9. Hygiene

- No tools installed or upgraded (nothing was needed; no pacman, no uv/npx/binary changes).
- No llama-server started by me; `pgrep -af llama-server` → no output (exit 1).
- Scratch: `/fast/scratch/hyaku/kama-r53/Sen1Mem` only; removed before finishing. No writes in the
  lane, the fleet repo, or `measured/`.

## Artifacts (this directory)

- `mem-leg-probe.py`, `out-mem-leg.txt` — probe 1: read-only descendant read (marker read back,
  write → EBADF); non-descendant maps ok / mem denied; the counter's own `code_observe`, `sealed_exe`
  and leg expression on that pid.
- `archive-ref-probe.py`, `out-archive-ref.txt` — probe 2: `<S>` derivable from the replay's
  `TMPDIR`; in-place rewrite by a same-uid child moves `Archive.member()` off the frozen download.
- `keys-bounds-probe.py`, `out-keys-bounds.txt` — probe 3: honest archive → 4 mismatches (leg 0);
  rewritten archive → 0 problems (leg 1, false pass); member names are keys only; traversal refused;
  256 MiB row → VmHWM 27 824 → 550 424 kB; zero-tail padding passes.
- `out-fix-check.txt` — the patched counter on the same tamper and the same 256 MiB row.
- `c1-reference-immutability.diff` — proposed fixes (validated; not applied to the lane).
- `c1-build.out.copy`, `base.c1.out.copy` — the L1 receipts cited here.
