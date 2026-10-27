# J5EnvNames — Envnames-leg edge probe (C1, round 55)

**Verdict: BAD_ENV is underinclusive on this host.** The live server carries exactly five
environment names (`HOME`, `LANG`, `LD_LIBRARY_PATH`, `PATH`, `TMPDIR`); none of the
code-injection channels can reach it through any of the three scrub layers, so the envnames
leg is a producer-mutation detector — and in that model it names only one live glibc channel
(`LD_PRELOAD`), while the second one, **`LD_AUDIT`, is unnamed and demonstrably executes
non-archive code in the server while the frozen counter prints `met=True`**.

Two defects, both measured against the frozen counter (sha256
`c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`, matching the
preregistration); two independent fixes are supplied and validated in `fix/`.

---

## 1. The measured live environment (the seat's first ask)

A held server from the landed build (pristine `tools/kama-llamacpp-live.py` at the freeze tip
`9c60eae6f7ed84f7da93d219a406aadc30958c6c`), started through the same replay tool the counter
uses. Provenance note: I invoked the replay from my shell, so the *outer* env is wider than the
counter's `prepare_env` scrub and `HOME` is the real home rather than a scratch `home-<tag>`.
The server's env **names** are nevertheless identical to the counter's own run — the counter's
frozen control receipt records the same count (`envnames b1: 5 environment variable names
recorded`), and the layering in §2 shows why the extra outer names cannot pass the allowlists:

```
python3 tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-1.json \
  --work $S/work3 --out $S/replay-out3.json --witness-dir $S/wd3 --witness-timeout 600
tr '\0' '\n' < /proc/<pid>/environ
```

`/proc/<pid>/environ` of the server (pid 2545025), names and values
(`receipts/honest-server-environ.txt`):

```
PATH=<the harness PATH>
HOME=/home/vgpnk
LANG=en_US.UTF-8
TMPDIR=/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/work3/tmp
LD_LIBRARY_PATH=/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/work3/server/llama-b11909
```

**Five names.** This matches the counter's own frozen control receipt
(`.ufo/waves/round-55/c1/battery/control.out`: `envnames b1: 5 environment variable names
recorded`) and explains `m-ldaudit-foreign.out`'s 6 (5 + the mutant's `LD_AUDIT`). The live
tool's own process carries four (`HOME LANG PATH TMPDIR`, `receipts/live-tool-environ-names.txt`).

Honest executable mappings (`receipts/honest-server-exec-mappings.txt`): 8 archive members
under the unpacked tree, `/memfd:llama-server`, the 13 `/usr/lib` host libraries of the frozen
`HOST_LIBS` set, and `[vdso]`. Host identities with inodes are in
`receipts/honest-host-libs.txt`.

## 2. Reachability in the scrubbed `child_env`

The server's environment is fixed by three nested allowlists; ambient `LD_*` / `GLIBC_*` /
`GCONV_PATH` never reach it:

| layer | code | names that pass |
|---|---|---|
| counter → replay | `tools/round54-replay-code-audit.py:154,614-629` (`PASS_ENV` + HOME/XDG_CACHE_HOME/TMPDIR + canary + PYTHONPATH) | PATH, LANG, http(s)_proxy, NO_PROXY, HOME, XDG_CACHE_HOME, TMPDIR, KAMA_R51_CANARY, PYTHONPATH |
| replay → live child | `tools/kama-live-replay.py:128,152-155` (`LIVE_ENV_KEYS`) | PATH, HOME, LANG, LC_ALL, TMPDIR |
| live tool → server | `tools/kama-llamacpp-live.py:126,2188-2189` (`CHILD_ENV_KEYS`) | PATH, HOME, LANG, LC_ALL, TMPDIR |

then `tools/kama-llamacpp-live.py:2195` **overwrites** `LD_LIBRARY_PATH` with
`os.path.dirname(server_real)` (needed because the memfd image has no `$ORIGIN`).

Measured (`python3` import of the live tool with a poisoned `os.environ` containing
`LD_PRELOAD`, `LD_AUDIT`, `LD_LIBRARY_PATH`, `LD_PRELOAD_32`, `GLIBC_TUNABLES`, `LD_DEBUG`):

```
CHILD_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')
child_env names (before the tool's own LD_LIBRARY_PATH) = ['HOME', 'LANG', 'PATH']
child_env names (as the server is actually spawned)     = ['HOME', 'LANG', 'LD_LIBRARY_PATH', 'PATH']
```

**Consequence:** no injection name is reachable by inheritance. The only route is a change to
the producer's source (`tools/kama-llamacpp-live.py` or `tools/kama-live-replay.py`) — which is
precisely the threat model of the C1 kill battery (its `m-ldpreload` mutant edits the live
tool to add `child_env['LD_PRELOAD']`). Under that model the envnames leg's *name list* is the
control, and it is incomplete.

## 3. Per-name judgement (glibc 2.44, x86-64, this host)

Mechanism probes were run against standalone binaries built in scratch
(`fix/audit_evil.c`, `fix/audit_hard.c`, `fix/ctor_hard.c`).

| name | in `BAD_ENV`? | reachable in scrubbed child_env | can introduce non-archive code on this glibc | measured |
|---|---|---|---|---|
| `LD_PRELOAD` | yes | only by producer mutation | **yes** — preloaded DSO's constructor runs | ctor marker written |
| `DYLD_INSERT_LIBRARIES` | yes | only by producer mutation | **no** — macOS/BSD dyld; glibc never reads it | no ctor marker |
| `LD_AUDIT` | **no** | only by producer mutation | **yes** — a DSO exporting `la_version` is dlopen'd in a separate linker namespace *before* the program's objects, its constructors run, and it stays mapped `r-xp` | ctor marker written; 5 `r-xp` maps rows for the audit DSO |
| `LD_LIBRARY_PATH` | **no** | present in the honest env, but the tool overwrites it with a fixed value | yes in general (a rogue `libm.so.6` on the path ran its ctor), but the value is the archive tree whose members the code leg byte-compares | ctor marker written for a manual hijack dir |
| `LD_PRELOAD_32` / `LD_LIBRARY_PATH_32` | **no** | only by producer mutation | **no** — 32-bit loader only; the server is x86-64 | `LD_PRELOAD_32` produced no ctor |
| `LD_CONFIG` | **no** | only by producer mutation | **no** — glibc does not honour it | `LD_DEBUG=libs` still `search cache=/etc/ld.so.cache` |
| `LD_DEBUG` / `LD_DEBUG_OUTPUT` | **no** | only by producer mutation | no code loading; `LD_DEBUG_OUTPUT` *creates a file* at an attacker-chosen path (write primitive, not injection) | `dbgout.<pid>` created |
| `GLIBC_TUNABLES` | **no** | only by producer mutation | **no** — tunables are a closed behaviour set; none loads a DSO | honoured, no code path |
| `GCONV_PATH` | **no** | only by producer mutation | not for this process — glibc loaded `/usr/lib/gconv/EUC-JP.so` even with `GCONV_PATH` set, and the server imports no iconv/gconv symbol (0 undefined) | system module won |
| `LD_ORIGIN_PATH`, `LD_PROFILE*`, `LINES`, `COLUMNS` | no | only by producer mutation | no code loading / no effect | no effect / no file |

The irrelevant half of the pair is worth stating plainly: on this host **`DYLD_INSERT_LIBRARIES`
is inert**, so `BAD_ENV` currently spends one of its two slots on a name that cannot fire,
while the second live glibc channel is unnamed.

## 4. Defect 1 (primary) — the envnames leg omits `LD_AUDIT`

`tools/round54-replay-code-audit.py:146`

```python
BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")
```

### The command that shows it

One-line mutation of the live tool in **my own clone** (fixture identity, never the lane):

```
child_env['LD_AUDIT'] = '/fast/scratch/.../hostlib/libm.so.6'   # root-owned, exports la_version
python3 tools/round54-replay-code-audit.py --repo $S/lane --tip 64795a19ad94a7d4241d828fe35d3fa3c5195c1c ...
```

### The result (`receipts/counter-ldaudit-mutant.out`)

```
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True
detail: envnames b1: 6 environment variable names recorded, none of LD_PRELOAD/DYLD_INSERT_LIBRARIES
detail: code b1: 8 archive files (16 executable ranges) byte-equal ..., 14 root-owned host files
```

`met=True` while, from the same run:

* the planted DSO's constructor executed **inside the server process** — `/tmp/audit-ran`
  contains `audit ctor ran pid=925257`, `pid=928827`, `pid=934042`, which are exactly the
  receipt's `bind b1/b2/b3: pid …` server pids;
* the plant is mapped `r-xp` in the server (`receipts/MUTANT-server-exec-mappings.txt` lists
  `/fast/.../hostlib/libm.so.6` among the executable mappings);
* the counter *saw* an extra host file and admitted it: **14 root-owned host files where the
  honest build has 13**.

The envnames leg recorded the `LD_AUDIT` name (`6 environment variable names`) and did not
treat it as a problem, because `BAD_ENV` does not contain it.

### Isolating the env leg as load-bearing (`receipts/counter-mutant3.out`)

The identical plant and the identical colliding basename, but via `LD_PRELOAD`:

```
bind=1 sealed=1 code=1 teardown=1 newrow=1 ... envnames=0/3 hostlibs=3/3 ... met=False
detail: envnames b1: env: server environment carries LD_PRELOAD
```

`code=1` and `hostlibs=3/3` — the code leg admits the same plant by basename — so **only the
envnames leg catches it**. Replace the name with `LD_AUDIT` and nothing catches it.

### The code leg is a partial backstop (`receipts/counter-mutant2.out`)

Same `LD_AUDIT` vector, but the DSO is named `libauditplant.so` (no `HOST_LIBS` collision):

```
bind=1 sealed=1 code=0 teardown=1 newrow=1 ... envnames=3/3 hostlibs=0/3 ... met=False
detail: code b1: code: root-owned host library .../hostlib/libauditplant.so is not in the frozen host set
```

So `LD_AUDIT` is caught by the *code* leg only while the attacker does not pick a colliding
basename — and picking one is free.

### Proposed fix A (`fix/fix-A-bad-env-LD_AUDIT.diff`, full text `fix/counter-fixed.py`)

```diff
-BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")
+# K1Cheat (round 55, seat J5EnvNames): the pair was incomplete. glibc honours a
+# SECOND code-injection variable, LD_AUDIT, which loads a DSO in a separate linker
+# namespace BEFORE the program's own objects and runs its constructors; a DSO
+# exporting la_version is loaded and stays mapped (measured on this host,
+# glibc 2.44). LD_PRELOAD_32/LD_LIBRARY_PATH_32 apply to the 32-bit loader only
+# (the b11909 server is x86-64), DYLD_INSERT_LIBRARIES is macOS/BSD (no effect
+# on glibc), LD_CONFIG is not honoured by glibc, and LD_LIBRARY_PATH is set by
+# the live tool to the server's own directory (a fixed value, not inherited).
+BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")
```

Validated both ways:

* on the mutant tip → `envnames=0/3 … met=False` (`receipts/counter-fixed-on-mutant.out`);
* on the pristine freeze tip → `met=True` (`receipts/counter-fixed-on-pristine.out`), i.e. no
  false positive on the honest build (its five names contain no `LD_AUDIT`).

`DYLD_INSERT_LIBRARIES` is deliberately kept (harmless, and meaningful on a macOS runner);
the point of the fix is that the *live* set is now complete.

## 5. Defect 2 (amplifier) — host libraries are admitted by basename alone

`tools/round54-replay-code-audit.py:558-563` admits any root-owned, non-writable file whose
**basename** is in `HOST_LIBS`, without pinning the path or the inode:

```python
if st.st_uid != 0 or str(st.st_ino) != ino or os.access(path, os.W_OK):
    ... continue
if os.path.basename(path) not in HOST_LIBS:
    probs.append(f"code: root-owned host library {path} is not in the frozen host set")
    continue
```

A root-owned plant at *any* path named `libm.so.6` (or `libc.so.6`, `libstdc++.so.6.0.36`,
`libzstd.so.1.5.7`, …) therefore enters the `host` set — which is why the LD_AUDIT run printed
14 host files instead of 13 and still passed. The frozen limits text covers "a byte-identical
host install", but not "a different file that merely shares a basename".

### Proposed fix B (`fix/fix-B-hostlib-inode-pinning.diff`, full text `fix/counter-pinned.py`)

Pin each basename to the inode measured for the honest build (table in
`receipts/honest-host-libs.txt`):

```python
HOST_LIB_IDS = {"ld-linux-x86-64.so.2": "13506894", "libbrotlicommon.so.1.2.0": "8043",
                "libbrotlidec.so.1.2.0": "8046", "libbrotlienc.so.1.2.0": "8049",
                "libcrypto.so.3": "13509470", "libc.so.6": "13506903",
                "libgcc_s.so.1": "621207", "libgomp.so.1.0.0": "632877", "libm.so.6": "13506913",
                "libssl.so.3": "13509472", "libstdc++.so.6.0.36": "621215",
                "libz.so.1.3.2": "13508283", "libzstd.so.1.5.7": "8527"}
...
if str(st.st_ino) != HOST_LIB_IDS[os.path.basename(path)]:
    probs.append(f"code: root-owned host library {path} inode {st.st_ino} is not the frozen "
                 f"host object {HOST_LIB_IDS[os.path.basename(path)]}")
    continue
```

Validated independently of fix A (fix A is **not** applied in this variant):

* on the mutant tip → `code=0/3 hostlibs=0/3 … met=False`
  (`receipts/counter-pinned-on-mutant1.out`, detail:
  `… libm.so.6 inode 557634341 is not the frozen host object 13506913`);
* on the pristine freeze tip → `met=True` (`receipts/counter-pinned-on-pristine.out`).

Either fix alone closes the demonstrated bypass; A closes the naming gap, B closes the
basename-collision class (which also covers an `LD_LIBRARY_PATH` value hijack, a `GCONV_PATH`
module, and any future loader channel).

## 6. The battery's `m-ldaudit-foreign` conclusion is over-general

`.ufo/waves/round-55/c1/battery/run-battery.py` records `m-ldaudit-foreign` as a **vector**
(expected `met=True`) with the justification "the LD_AUDIT vector for loading a root-owned
foreign lib is empirically void on this glibc", and the preregistration repeats it. That test
used `LD_AUDIT=/usr/lib/libexpat.so.1`, which exports no `la_version`:

```
$ nm -D --defined-only /usr/lib/libexpat.so.1 | grep -c la_version
0
$ LD_AUDIT=/usr/lib/libexpat.so.1 ./plain
ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface:
       undefined symbol: la_version; ignored.
```

ld.so refuses *that* object for a missing symbol; it does not refuse `LD_AUDIT`. With a DSO
that exports `la_version` the loader loads it, maps it `r-xp`, and runs its constructors
(measured, and again inside the real server process in §4). The battery receipt is accurate
as a record of the libexpat probe; its generalising sentence is falsified, and the seat brief's
premise ("m-ldaudit-foreign already showed LD_AUDIT of a non-audit DSO is ignored") holds only
for non-audit DSOs.

Note also that the *predicate as written* is satisfied by the §4 mutant: "a root-owned host
file whose basename is in the frozen host set" admits the plant, and "the server carries no
LD_PRELOAD" is literally true. The counter implements its predicate faithfully; the predicate
and the env leg are too weak, which is the defect.

## 7. Notes, scope, and hygiene

* The lane was read-only for this seat. The three mutants are fixture commits in my own
  `git clone --shared` at `/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/lane` (branch
  `seat-j5-envnames`, tips `64795a19`, `7c17a31b`, `25be26c2`), committed with
  `user.name=fx / user.email=fx@invalid` after checking `rev-parse --show-toplevel`.
  `git -C <lane> status` shows only another seat's `J2RowCap` files.
* The planted library was installed root-owned with `sudo` **inside my own scratch**
  (`$S/hostlib/`) and removed with the scratch. `sudo -n true` succeeded; no `pacman`
  transaction was attempted and no tool was installed or upgraded (gcc, sudo, python3 were
  already present), so there is no tooling change to record.
* The held servers were torn down; `pgrep -af 'llama-server|kama-llamacpp-live|kama-live-replay'`
  matching my scratch returns 0, and `receipts/` retains the captures. `/tmp/audit-ran`
  (the constructor's marker, which proves in-server execution) was left by the counter runs
  and is not cited as evidence — the pids are quoted in this report instead.

## 8. Files written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J5EnvNames.md`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J5EnvNames/receipts/`
  (`counter-ldaudit-mutant.out`, `counter-mutant2.out`, `counter-mutant3.out`,
  `counter-fixed-on-mutant.out`, `counter-fixed-on-pristine.out`,
  `counter-pinned-on-mutant1.out`, `counter-pinned-on-pristine.out`,
  `honest-server-environ.txt`, `honest-server-environ-names.txt`,
  `honest-server-exec-mappings.txt`, `honest-host-libs.txt`,
  `MUTANT-server-exec-mappings.txt`, `server-environ.txt`, `server-environ-names.txt`,
  `live-tool-environ-names.txt`)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/J5EnvNames/fix/`
  (`fix-A-bad-env-LD_AUDIT.diff`, `fix-B-hostlib-inode-pinning.diff`, `counter-fixed.py`,
  `counter-pinned.py`, `audit_evil.c`, `audit_hard.c`, `ctor_hard.c`)
