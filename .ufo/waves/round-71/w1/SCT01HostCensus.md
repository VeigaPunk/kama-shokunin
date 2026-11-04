# SCT01HostCensus — round 71 host census (axis: freshness)

Seat: scout (leaf). Read-only against the lane; fixtures under
`S=/fast/scratch/hyaku/kama-r71/SCT01HostCensus` (deleted on exit). Read first:
`plans/round-71-claims.md` (C3 freshness) and PROVINCE.md §Round-65/67. PROVINCE.md, tools and
corpus were **not** edited.

## Verdict

- **Live host identity:** `Linux plazir27 7.2.11-arch1-1 #1 SMP PREEMPT_DYNAMIC Fri, 16 Oct 2026 00:28:58 +0000 x86_64 GNU/Linux`
  (`uname -s` → `Linux`; `/etc/os-release` → `NAME="Arch Linux"`; `git --version` → `git version 2.56.0`).
  Marker prose: Windows 10.0.26200, Git Bash (MinGW64), `git 2.55.0.windows.3`.
- Population: **11 marker lines, 12 tags** (llama line carries two), plus **4 prose surfaces** = 16.
- **Contradicted: 14/16 — 10 tags + 4/4 prose.** Matching: 2 tags.
- Contradicted tags: `omp-binary`, `llama-b11755-install`, `llama-server-link`,
  `kama-cache-gguf`, `llama-b11755-archive`, `opencode-json`, `ufo-src`,
  `ollama-v04011-install`, `fixture-gguf-model`, `python3-interpreter`.
- Matching tags: `qwen-coder-unit` (unit file genuinely absent), `janitor-md` (file and
  `agents/` dir genuinely absent).
- Consistency note: this equals the frozen C3 counter's before-state `contradicted=14`
  (`measured/before/province-markers.out`). That is an arithmetic convergence check, not a
  claim about how the C3 tool scores.

## Exact probes and results

`~` = `/home/vgpnk`. Full verbatim receipt: `w1/SCT01HostCensus/census-raw.out`.

| surface | declared command | exact result |
|---|---|---|
| `omp-binary` | `test -e ~/.local/bin/omp` | exit 0; ELF x86-64, 276785328 B, sha256 `6737ee24…7b0f` |
| `llama-b11755-install` | `test -e ~/.local/opt/llama-b11755` | exit 0; dir, 61 entries (`libllama.so.0.7.0`, `llama-server` 17864 B) |
| `llama-server-link` | `test -e ~/.local/bin/llama-server` | exit 0; `-> ~/.local/opt/llama-b11755/llama-server`, sha256 `b6a31a8e…cd804` |
| `kama-cache-gguf` | `test -e ~/.cache/kama-shokunin` | exit 0; dir with `models/` |
| `llama-b11755-archive` | `test -e ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` | exit 0; 22240468 B gzip, sha256 `753bfa73…6e226` |
| `qwen-coder-unit` | `test -e ~/.config/systemd/user/qwen-coder.service` | exit 1 |
| `opencode-json` | `test -e ~/.config/opencode/opencode.json` | exit 0; 74 B JSON, sha256 `f2e40703…ea0f9` |
| `janitor-md` | `test -e ~/.config/opencode/agents/janitor.md` | exit 1 (whole `agents/` dir also exit 1) |
| `ufo-src` | `printenv UFO_SRC` + checkout search | env unset (exit 1); checkout found (see below) |
| `ollama-v04011-install` | `test -e ~/.local/opt/ollama-v0.40.11` | exit 0; dir with `bin/`, `lib/` |
| `fixture-gguf-model` | `test -e ~/.cache/kama-shokunin/models/stories260K.gguf` | exit 0; 1185376 B, GGUF v3, 48 tensors, sha256 `270cba1b…bd256d` |
| `python3-interpreter` | `python3 -c "import sys"; echo EXIT=$?` | exit 0; `/usr/bin/python3`, Python 3.14.8 (GCC 16.2.1) |

Prose surfaces:

1. **Host identity** — `uname -a` output above; Arch Linux. Marker says Windows → contradicted.
2. **`python3` Store alias** — `python3 -VV` → `Python 3.14.8`; `python3 -c "import sys"` exit 0;
   `type -a python3` → `/usr/bin/python3`. Marker says alias stub exit 49 → contradicted.
3. **NTFS `|` path** — `findmnt -T <lane>` → `btrfs` (`/home`), `findmnt -T <S>` → `xfs`
   (`/fast/nvme1n1p2`). The lane track contains `.ufo/waves/round-52/w1/out/c -l\` → 18\`|`
   (bytes via `od -c`); `WORKTREE=present`. Scratch fixture (`mktemp -d -p S`, toplevel asserted
   equal to `$D`): `git init`, `git add -- 'dir/out/c -l\` → 18\`|'`, `git commit`,
   `git checkout -- 'dir/out/c -l\` → 18\`|'` → all exit 0, payload restored, status clean.
   Marker says checkout impossible on this host → contradicted.
4. **`ss`/`flock` absence** — `command -v ss` → `/usr/bin/ss` (exit 0); `command -v flock` →
   `/usr/bin/flock` (exit 0); `ss -ltn | wc -l` → 36. Marker says both absent → contradicted.

`ufo-src` evidence (two-condition marker: "`UFO_SRC` is unset and no ufo-fsd checkout was located"):

```
$ git -C /home/vgpnk/Projects/ufo-fsd-alpha rev-parse --is-inside-work-tree
true
$ git -C /home/vgpnk/Projects/ufo-fsd-alpha rev-parse --show-toplevel
/home/vgpnk/Projects/ufo-fsd-alpha
$ git -C /home/vgpnk/Projects/ufo-fsd-alpha rev-parse --short HEAD
fb7157fc
remote: https://github.com/VeigaPunk/ufo-fsd-alpha.git
PRESENT config/the-tick.machine.json
PRESENT scripts/local-helper.mjs
```

## Ambiguities and scoring

- **`ufo-src` is two conditions.** The round-65 audit tool's declared probe is env-only
  (`UFO_SRC`), which would read absent and not contradict; the marker's own sentence is the
  conjunction, and its second half fails. Scored **contradicted=yes** on the marker sentence;
  this is the one tag where tool surface and marker text disagree. `UFO_SRC` itself is unset
  in this environment (the checkout is not env-pinned).
- **`qwen-coder-unit`.** Scored on the declared file surface (absent → **no**). The marker's
  rationale clause "no systemd on this host" is contradicted: `/usr/bin/systemctl` exists and
  `~/.config/systemd/user` exists. Clause stale, tag verdict not.
- **`janitor-md`.** File and directory both absent → marker holds under either reading (**no**).
- Stale supporting details beyond verdicts: `opencode-json` claims the dir holds
  `opencode.jsonc` with only `$schema`; live dir holds `opencode.json` (74 B) and no `.jsonc`.
  `omp-binary` claims `~/.omp/` holds only `agent/settings.json`; live `~/.omp` has 17 entries
  incl. `stats.db` (1.4 GB) and `logs/`.

## Consequence for C3 (stated, not applied)

Needed corrections are the 10 contradicted tags plus the 4 prose surfaces, each as a later
`correction-on-host (DATE) \`province-host:TAG\`` line whose present/absent verdict matches the
live probes above. `qwen-coder-unit` and `janitor-md` need no tag correction. PROVINCE.md was
not edited by this seat.

## Artifacts

- `kama-shokunin/.ufo/waves/round-71/w1/SCT01HostCensus/host-census.tsv` — 16 rows + header,
  5 columns (`tag, marker_verdict, live_verdict, contradicted, probe_command`).
- `.../SCT01HostCensus/host-census.md` — full verbatim outputs and scoring notes.
- `.../SCT01HostCensus/{census-raw.out,pipe-checkout.out,probe.sh,pipe-test.sh}` — receipts and
  reproducible drivers.

## Could not verify / limits

- No endpoint contact: no request to 8080/34113/11434; `ss -ltn` was listener metadata only.
- I did not prove `/home/vgpnk/Projects/ufo-fsd-alpha` is the same tree historical `$UFO_SRC`
  named on the former host; only that a live ufo-fsd checkout carrying both pinned consumer
  files exists here.
- The Windows-host claims cannot be re-derived from this host beyond their contradiction here;
  no Windows artifact was reachable for comparison.
- Tool installs: none (no package manager, network or PATH change).
