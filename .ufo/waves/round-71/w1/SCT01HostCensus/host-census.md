# Host census — every `province-host:` surface re-derived on this host

Seat SCT01HostCensus (kama round 71, wave 1, axis: freshness). Read-only against the lane;
all fixtures under `/fast/scratch/hyaku/kama-r71/SCT01HostCensus`. PROVINCE.md, tools and
corpus were not edited.

**Live host identity:** `Linux plazir27 7.2.11-arch1-1 #1 SMP PREEMPT_DYNAMIC Fri, 16 Oct 2026 00:28:58 +0000 x86_64 GNU/Linux`
(`uname -s` → `Linux`; `/etc/os-release` → `NAME="Arch Linux"`, `PRETTY_NAME="Arch Linux"`; `git --version` → `git version 2.56.0`).
The marker prose describes Windows 10.0.26200 / Git Bash / `git 2.55.0.windows.3`.

## Method and scoring

Declared probe per surface kind, matching `tools/round65-province-host-audit.py`:
`file`/`dir` → `test -e <expanded path>`; `env` → `printenv UFO_SRC`; `spawn` → real
`python3 -c "import sys"` run graded by exit code. The four prose surfaces use the commands
named in the seat spec. `~` below = `/home/vgpnk`.

Marker verdict = the PROVINCE.md round-65/67 sentence for the tag, all dated
`absent-on-this-host (2026-10-31)`. A surface is **contradicted** iff the live verdict differs
from that sentence (present where the marker says absent, or vice versa).

Population: **11 marker lines, 12 tags** (the llama line carries `llama-b11755-install` and
`llama-server-link`), plus **4 prose surfaces** = 16. Result: **contradicted 14/16 — 10 tags +
4 prose; 2 tags still match** (`qwen-coder-unit` file, `janitor-md`).

## Tag results

| tag | marker | live | contradicted |
|---|---|---|---|
| `omp-binary` | absent | present, ELF binary | yes |
| `llama-b11755-install` | absent | present, 61-entry dir | yes |
| `llama-server-link` | absent | present, resolving symlink | yes |
| `kama-cache-gguf` | absent | present (`models/`) | yes |
| `llama-b11755-archive` | absent | present, cited digest matches | yes |
| `qwen-coder-unit` | absent | absent (systemd itself present) | no |
| `opencode-json` | absent | present, 74-byte JSON | yes |
| `janitor-md` | absent | absent (file and dir) | no |
| `ufo-src` | unset + no checkout | unset, but checkout found | yes |
| `ollama-v04011-install` | absent | present (`bin/`, `lib/`) | yes |
| `fixture-gguf-model` | absent | present, GGUF v3 | yes |
| `python3-interpreter` | alias stub, exit 49 | real CPython 3.14.8, exit 0 | yes |

## Exact commands and outputs (verbatim receipt `census-raw.out`)

```
=== host identity ===
## uname-a
CMD: uname -a
Linux plazir27 7.2.11-arch1-1 #1 SMP PREEMPT_DYNAMIC Fri, 16 Oct 2026 00:28:58 +0000 x86_64 GNU/Linux
EXIT=0
## uname-s
CMD: uname -s
Linux
EXIT=0
## os-release
CMD: grep -E "^(NAME|VERSION_ID|PRETTY_NAME)=" /etc/os-release
NAME="Arch Linux"
PRETTY_NAME="Arch Linux"
EXIT=0
=== path tags (declared probe: test -e PATH) ===
## omp-binary
CMD: test -e /home/vgpnk/.local/bin/omp; echo EXIT=$?
EXIT=0
-rwxr-xr-x 1 vgpnk vgpnk 276785328 Nov  1 17:11 /home/vgpnk/.local/bin/omp
ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=588d7307f333293c728b74df19b7323c20736899, not stripped
6737ee2415555a3656cc7b89c14d1c25c18658ee4c0fd4f7309705149ccb7b0f  /home/vgpnk/.local/bin/omp
## llama-b11755-install
CMD: test -e /home/vgpnk/.local/opt/llama-b11755; echo EXIT=$?
EXIT=0
drwxr-xr-x 1 vgpnk vgpnk 2182 Oct 20 08:10 /home/vgpnk/.local/opt/llama-b11755
ENTRIES=61
f /home/vgpnk/.local/opt/llama-b11755/ggml-rpc-server
f /home/vgpnk/.local/opt/llama-b11755/libggml-base.so.0.27.0
... (30 of 61 entries printed; excerpt ends at LICENSE. llama-server confirmed separately: -rwxr-xr-x 17864 B)
## llama-server-link
CMD: test -e /home/vgpnk/.local/bin/llama-server; echo EXIT=$?
EXIT=0
lrwxrwxrwx 1 vgpnk vgpnk 48 Oct 20 10:17 /home/vgpnk/.local/bin/llama-server -> /home/vgpnk/.local/opt/llama-b11755/llama-server
symbolic link to /home/vgpnk/.local/opt/llama-b11755/llama-server
b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804  /home/vgpnk/.local/bin/llama-server
## kama-cache-gguf
CMD: test -e /home/vgpnk/.cache/kama-shokunin; echo EXIT=$?
EXIT=0
drwxr-xr-x 1 vgpnk vgpnk 12 Oct 26 16:57 /home/vgpnk/.cache/kama-shokunin
ENTRIES=1
d /home/vgpnk/.cache/kama-shokunin/models
## llama-b11755-archive
CMD: test -e /home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz; echo EXIT=$?
EXIT=0
-rw-r--r-- 1 vgpnk vgpnk 22240468 Oct 20 10:17 /home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz
gzip compressed data, from Unix, original size modulo 2^32 56340480
753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226  /home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz
## qwen-coder-unit
CMD: test -e /home/vgpnk/.config/systemd/user/qwen-coder.service; echo EXIT=$?
EXIT=1
## opencode-json
CMD: test -e /home/vgpnk/.config/opencode/opencode.json; echo EXIT=$?
EXIT=0
-rw------- 1 vgpnk vgpnk 74 Oct 24 21:28 /home/vgpnk/.config/opencode/opencode.json
JSON text data
f2e407032af1ed069eff43357fce24346d8c8edc31cb736ab9091c063f0ea0f9  /home/vgpnk/.config/opencode/opencode.json
## janitor-md
CMD: test -e /home/vgpnk/.config/opencode/agents/janitor.md; echo EXIT=$?
EXIT=1
## janitor-dir
CMD: test -e /home/vgpnk/.config/opencode/agents; echo EXIT=$?
EXIT=1
## ollama-v04011-install
CMD: test -e /home/vgpnk/.local/opt/ollama-v0.40.11; echo EXIT=$?
EXIT=0
drwxr-xr-x 1 vgpnk vgpnk 12 Oct 27 18:22 /home/vgpnk/.local/opt/ollama-v0.40.11
ENTRIES=2
d /home/vgpnk/.local/opt/ollama-v0.40.11/bin
d /home/vgpnk/.local/opt/ollama-v0.40.11/lib
## fixture-gguf-model
CMD: test -e /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf; echo EXIT=$?
EXIT=0
-rw-r--r-- 1 vgpnk vgpnk 1185376 Oct 26 16:57 /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
GGUF file format version 3, 48 tensors, 19 metadata entries
270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d  /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
=== ufo-src (declared probe: env UFO_SRC) ===
CMD: printenv UFO_SRC (empty output = unset); echo EXIT=$?
UFO_SRC=<unset>
EXIT=1
CMD: command -v ufo; echo EXIT=$?
EXIT=1
=== python3-interpreter (declared probe: spawn kind = real run) ===
CMD: python3 -c "import sys"; echo EXIT=$?
EXIT=0
CMD: command -v python3; type -a python3; python3 -VV
/usr/bin/python3
python3 is /usr/bin/python3
Python 3.14.8 (main, Oct  2 2026, 10:23:31) [GCC 16.2.1 20260810]
EXIT=0
CMD: python -c "import sys"; echo EXIT=$?
EXIT=0
=== ss/flock absence prose claim ===
CMD: command -v ss; echo EXIT=$?
/usr/bin/ss
EXIT=0
CMD: command -v flock; echo EXIT=$?
/usr/bin/flock
EXIT=0
CMD: ss -ltn | wc -l
36
EXIT=0
=== qwen-coder-unit prose clause: systemd presence ===
CMD: command -v systemctl; echo EXIT=$?
/usr/bin/systemctl
EXIT=0
CMD: test -d /home/vgpnk/.config/systemd/user; echo EXIT=$?
EXIT=0
=== opencode dir shape (read-only) ===
CMD: ls -la /home/vgpnk/.config/opencode 2>&1; echo EXIT=$?
total 20
drwxr-xr-x 1 vgpnk vgpnk  144 Oct 24 21:28 .
drwxr-xr-x 1 vgpnk vgpnk 2196 Nov  2 23:14 ..
-rw------- 1 vgpnk vgpnk 163 Oct 11 13:35 cli.json
-rw------- 1 vgpnk vgpnk  74 Oct 24 21:28 opencode.json
-rw-r--r-- 1 vgpnk vgpnk  95 Oct 24 21:28 opencode.json.tui-migration.bak
-rw------- 1 vgpnk vgpnk  64 Oct 11 12:53 service.json
-rw-r--r-- 1 vgpnk vgpnk  68 Oct 24 21:28 tui.json
EXIT=0
=== omp dir shape (read-only) ===
CMD: ls -la /home/vgpnk/.omp 2>&1; echo EXIT=$?
total 1724080
drwxr-xr-x 1 vgpnk vgpnk        292 Nov  3 21:13 .
drwx------ 1 vgpnk vgpnk       2998 Nov  3 21:34 ..
drwx------ 1 vgpnk vgpnk       3890 Nov  3 21:33 agent
-rw-r--r-- 1 vgpnk vgpnk       1242 Oct 11 07:52 APPEND_SYSTEM.md
-rw-r--r-- 1 vgpnk vgpnk    176128 Nov  3 21:13 autoqa.db
drwxr-xr-x 1 vgpnk vgpnk         18 Oct 11 10:43 browser-relay
drwxr-xr-x 1 vgpnk vgpnk       332 Nov  3 14:37 cache
-rw------- 1 vgpnk vgpnk         37 Oct  6 15:58 install-id
drwxr-xr-x 1 vgpnk vgpnk    861220 Nov  3 21:33 logs
drwxr-xr-x 1 vgpnk vgpnk         30 Nov  1 17:25 natives
drwxr-xr-x 1 vgpnk vgpnk         12 Oct  3 19:11 oauth
drwxr-xr-x 1 vgpnk vgpnk         90 Oct 25 02:13 plugins
drwx------ 1 vgpnk vgpnk          0 Oct 22 04:05 profiles
drwxr-xr-x 1 vgpnk vgpnk         24 Oct 10 15:48 puppeteer
drwx------ 1 vgpnk vgpnk         14 Oct  3 19:10 run
drwx------ 1 vgpnk vgpnk          0 Oct 23 09:32 ssh-control
-rw-r--r-- 1 vgpnk vgpnk 1404887040 Nov  1 17:14 stats.db
-rw-r--r-- 1 vgpnk vgpnk   98304 Nov  3 20:26 stats.db-shm
-rw-r--r-- 1 vgpnk vgpnk 360289912 Nov  2 17:45 stats.db-wal
drwxr-xr-x 1 vgpnk vgpnk         24 Oct 19 17:52 wt
EXIT=0
```

### Checkout search for `ufo-src` (second condition of the marker sentence)

```
$ git -C /home/vgpnk/Projects/ufo-fsd-alpha rev-parse --is-inside-work-tree
true
$ git -C /home/vgpnk/Projects/ufo-fsd-alpha rev-parse --show-toplevel
/home/vgpnk/Projects/ufo-fsd-alpha
$ git -C /home/vgpnk/Projects/ufo-fsd-alpha rev-parse --short HEAD
fb7157fc
$ for f in config/the-tick.machine.json scripts/local-helper.mjs; do test -e "/home/vgpnk/Projects/ufo-fsd-alpha/$f" && echo "PRESENT $f"; done
PRESENT config/the-tick.machine.json
PRESENT scripts/local-helper.mjs
$ find /home/vgpnk/Projects -maxdepth 3 -iname '*ufo*'
/home/vgpnk/Projects/ufo-fsd-alpha        (remote: https://github.com/VeigaPunk/ufo-fsd-alpha.git)
```

### `|`-path checkout fixture (NTFS prose claim)

Filesystem: `findmnt -no FSTYPE,SOURCE,TARGET -T <lane>` → `btrfs /dev/mapper/root[/@home] /home`;
`-T /fast/scratch/...` → `xfs /dev/nvme1n1p2 /fast`. Neither is NTFS.

Lane track already carries the exact path (bytes confirmed with `od -c`):
`.ufo/waves/round-52/w1/out/c -l\` → 18\`|` — and `WORKTREE=present`.

Fixture (`mktemp -d -p S`, toplevel asserted equal to `$D` before commit):

```
INIT_EXIT=0
TOPLEVEL_ASSERT=ok
CREATED: -rw-r--r-- 1 vgpnk vgpnk 18 Nov  3 21:38 c -l` → 18`|
EXIT=0   (git add -- 'dir/out/c -l` → 18`|')
EXIT=0   (git commit -m 'pipe path')
0000000   d   i   r   /   o   u   t   /   c       -   l   `     342 206
0000020 222       1   8   `   |  \n
REMOVED_WORKTREE_COPY=yes
EXIT=0   (git checkout -- 'dir/out/c -l` → 18`|')
RESTORED=yes PAYLOAD=pipe-path-payload
EXIT=0   (git status --porcelain, empty)
```

## Ambiguous surfaces and how they were scored

1. **`ufo-src` is two conditions** (env unset AND no checkout). The round-65 audit tool's
   declared probe is env-only, which would read `absent` and not contradict. The marker
   sentence is the conjunction, so a found checkout makes it false: scored **contradicted**.
   This is the one tag where the tool surface and the marker text disagree. `UFO_SRC` itself
   remains unset in this environment; the checkout is not env-pinned.
2. **`qwen-coder-unit`** — the declared surface (unit file) is absent, matching the tag, so
   **not contradicted**. The marker's supporting clause "no systemd on this host" is
   contradicted (`/usr/bin/systemctl`, `~/.config/systemd/user` exists). The clause is stale
   independently of the tag.
3. **`janitor-md`** — tag surface is the file; both the file and the whole `agents/` dir are
   absent, so marker and live agree under either reading: **not contradicted**.
4. **Marker supporting details stale beyond the tag verdict**: `opencode-json` says the dir
   holds `opencode.jsonc` with only `$schema`; live dir holds `opencode.json` (74 B) and no
   `.jsonc`. `omp-binary` says `~/.omp/` holds only `agent/settings.json`; live `~/.omp` holds
   17 entries including `stats.db` (1.4 GB) and `logs/`.

## Consequence for C3 (stated, not applied)

Fourteen surfaces need a later, dated `correction-on-host (DATE) \`province-host:TAG\`` line
whose claimed present/absent verdict agrees with these live probes: the 10 tags marked
`yes` above plus the four prose surfaces (`host-identity`, `python3-alias`, `ntfs-pipe-path`,
`ss-flock-absence`). The two matching tags (`qwen-coder-unit`, `janitor-md`) need no tag
correction; their supporting clauses are stale. PROVINCE.md was **not** edited by this seat.

## Not verified / limits

- No endpoint was contacted; no port 8080/34113/11434 request was made. `ss -ltn` (listener
  metadata only) emitted 36 lines; no listener classification was performed.
- The `ufo-src` checkout was identified from the `ufo-fsd-alpha` repo remote; I did not prove
  it is the same tree the historical `$UFO_SRC` pointed at on the former host, only that it is
  a live checkout carrying both pinned consumer files.
- Tool installs: none (no package manager, network, or PATH change was made).
