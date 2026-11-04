# LAB01Probes — kama round-73 wave 1 bounded probe

Seat: `LAB01Probes` (leaf; no subagent dispatch). Lane revision at write time:
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master` =
`bc9e30599b6c6133bb094f0e7abd1a9f512778ec` (read before every receipt was written; all six
receipts carry it as their first line).

Host at run time (observed): `uname -s` = `Linux`, `uname -m` = `x86_64`, `uname -r` =
`7.2.11-arch1-1`, `/etc/os-release` `ID=arch`. Tools used: `git 2.56.0`, GNU coreutils
`uname 9.12`, `man`/`groff`/`col`, `pacman` query mode only (`-Q`, `-Qi`, `-Qo`; no transaction).
No tool was installed, upgraded or removed for this seat.

Read first: `plans/round-73-claims.md` (frozen). This seat produced **no disagreement** with the
freeze; nothing outside `$S` and my two assigned write paths was written.

## Verdict table

| # | Hypothesis (as assigned) | Verdict | Decisive observation |
|---|---|---|---|
| H1 | `.gitmodules` `submodule.<name>.ignore=all` hides submodule dirt from the parent `git status --porcelain -uall`; `--ignore-submodules=none` shows it | **CONFIRMED** | same dirt: default status empty, `--ignore-submodules=none` prints ` M mod` (one record) |
| H2 | `git worktree list --porcelain` enumerates a `--detach` linked worktree; its dirt is invisible from the primary, visible via its own status | **CONFIRMED** | enumeration lists both absolute paths; primary status empty; linked status ` M file.txt` + `?? untracked.txt` |
| H3 | `git status --porcelain -uall --ignored -- <missing-dir>` exits 0 empty; an existing dir with one ignored file prints one `!!` record | **CONFIRMED** | 5 absent/empty-path forms all exit 0 empty; each existing-dir form prints exactly one `!!` line |
| H4 | `uname -s`, `uname -m`, `/etc/os-release` `ID` are stable across a kernel-version change while `uname -r` is not | **CONFIRMED** for observed values and for “`-r` moves”; stability across the upgrade is **[INFERENCE]** (no reboot performed) | release field moved `7.1.4.arch1-1 → 7.2.3.arch1-3 → 7.2.11.arch1-1` in the package log; `-s`/`-m`/`ID` are not kernel-release fields and os-release is owned by `filesystem` |
| A1 (addendum) | `git check-ignore` reports a *tracked* file whose name matches an ignore pattern as ignored | **REFUTED** as stated | default `check-ignore` consults the index: exit 1, no output; only `--no-index` matches |

Full transcripts: `LAB01Probes/h1.out`, `h2.out`, `h3.out`, `h4.out` (plus addenda `h3x.out`,
`h4x.out`). Driver sources executed: `LAB01Probes/probe.py.txt`, `LAB01Probes/probe_extra.py.txt`
(identical to the executed files except for the prepended `# rev=` line).

---

## H1 — `submodule.<name>.ignore=all` in `.gitmodules` vs parent `status --porcelain -uall`

Fixture (`$S/h1`): `subrepo` (local repo, one commit) added into `parent` as `mod` with
`git -C parent -c protocol.file.allow=always submodule add <subrepo> mod`, committed; then
`git -C parent config -f .gitmodules submodule.mod.ignore all`, `.gitmodules` committed.
Both toplevels asserted equal to their fixture dirs before the first commit
(`git -C <dir> rev-parse --show-toplevel`; both `/fast/scratch/.../h1/{subrepo,parent}`, exit 0).
All commits: `git -C <dir> -c user.name=fixture -c user.email=fixture@invalid commit`.

Documentary basis (`man 5 gitmodules`, observed): “`submodule.<name>.ignore` — Defines under what
circumstances `git status` and the diff family show a submodule as modified… `all` — The submodule
will never be considered modified…” and “This setting affects status, update-index, diff and log”.

### Carrier: the setting lives in `.gitmodules`, not in `.git/config`

```
$ git -C .../parent config --get submodule.mod.ignore
  (no output)
[exit=1]
$ git -C .../parent config -f .gitmodules --get submodule.mod.ignore
  all
[exit=0]
```
So a consumer that inspects only `.git/config` misses the setting; `git status` itself honors the
`.gitmodules` value. Enumeration form that sees it:
```
$ git -C .../parent config -f .gitmodules --get-regexp '^submodule\..*\.path$'
  submodule.mod.path mod
[exit=0]
```

### Positive control — same dirt, before the setting

```
[C1] $ git -C .../parent status --porcelain -uall
   M mod
[exit=0]
[C2] $ git -C .../parent/mod status --porcelain -uall
   M base.txt
  ?? untracked.txt
[exit=0]
```

### State A — modified tracked file + untracked file inside the submodule, `ignore=all` in force

```
[A1] $ git -C .../parent status --porcelain -uall
  (no output)
[exit=0]
[A2] $ git -C .../parent status --porcelain -uall --ignore-submodules=none
   M mod
[exit=0]
[A3] $ git -C .../parent status --porcelain -uall --ignore-submodules=all
  (no output)
[exit=0]
[A4] $ git -C .../parent/mod status --porcelain -uall
   M base.txt
  ?? untracked.txt
[exit=0]
[A5] $ git -C .../parent submodule status --recursive
   9706f17039b075a2c51a4bf383b3e0c53ca0c769 mod (heads/main)
[exit=0]
```

### State B — untracked file only (tracked file restored)

```
$ git -C .../parent/mod checkout -- base.txt
[exit=0]
[B1] $ git -C .../parent status --porcelain -uall
  (no output)
[exit=0]
[B2] $ git -C .../parent status --porcelain -uall --ignore-submodules=none
   M mod
[exit=0]
[B3] $ git -C .../parent/mod status --porcelain -uall
  ?? untracked.txt
[exit=0]
[B4] $ git -C .../parent submodule status --recursive
   9706f17039b075a2c51a4bf383b3e0c53ca0c769 mod (heads/main)
[exit=0]
```

**Confirmed**, both clauses, with the control making the setting the demonstrated cause (identical
dirt yields ` M mod` before the setting and nothing after it).

Calibration details this establishes for the C1 `submodule` case:

1. The parent form at `--ignore-submodules=none` is **not vacuous**: it overrides `.gitmodules`
   `ignore=all` and reports the submodule even when the only dirt is an *untracked* file (B2).
2. That parent record is **submodule-granular**: one ` M mod` line, no file names inside. File-level
   paths exist only in the per-submodule status (A4/B3: `base.txt`, `untracked.txt`, relative to the
   submodule root). A finding detail for a submodule necessarily names a (submodule path, inner
   path) pair; the frozen predicate does not pin that detail shape.
3. `git submodule status --recursive` is **not** a dirt detector: the prefix stayed a space in A5
   and B4 (content dirt, tracked or untracked, does not touch the recorded-SHA comparison). It is
   usable for enumeration / initialized-state (`-` prefix for uninitialized), not for grading dirt.

Confidence: high (direct observation plus same-dirt control).

---

## H2 — linked worktree enumeration and dirt visibility

Fixture (`$S/h2`): `primary` repo, one commit; `git -C primary worktree add --detach <linked> HEAD`.
Primary toplevel and linked toplevel both asserted equal to their directories (exit 0).

```
[1] $ git -C .../primary worktree list --porcelain
  worktree /fast/scratch/hyaku/kama-r73/LAB01Probes/h2/primary
  HEAD 612cb5a05b1be02af6f673cffa1b919152b61a31
  branch refs/heads/main

  worktree /fast/scratch/hyaku/kama-r73/LAB01Probes/h2/linked
  HEAD 612cb5a05b1be02af6f673cffa1b919152b61a31
  detached

[exit=0]
[2] $ git -C .../linked rev-parse --show-toplevel
  /fast/scratch/hyaku/kama-r73/LAB01Probes/h2/linked
[exit=0]
$ git -C .../linked rev-parse --git-common-dir
  /fast/scratch/hyaku/kama-r73/LAB01Probes/h2/primary/.git
[exit=0]
```

After dirtying the linked worktree (tracked modification + untracked file):

```
[3] $ git -C .../primary status --porcelain -uall
  (no output)
[exit=0]
[4] $ git -C .../primary status --porcelain -uall --ignored
  (no output)
[exit=0]
[5] $ git -C .../linked status --porcelain -uall
   M file.txt
  ?? untracked.txt
[exit=0]
[6] $ git -C .../linked worktree list --porcelain
  <same two stanzas as [1], identical bytes>
[exit=0]
[7] $ git -C .../primary status --porcelain -uall -- .
  (no output)
[exit=0]
```

**Confirmed.** Calibration details for the C1 `worktree` case:

- Records are blank-line separated stanzas; the primary stanza carries `branch <ref>`, a detached
  linked worktree carries `detached` and **no** branch line; paths are absolute.
- The primary’s status is blind to linked-worktree dirt **even with `--ignored`** ([3], [4], [7]) —
  enumeration plus a per-path `git -C <path> status --porcelain -uall` is the only observed way to
  see it.
- The linked worktree’s status prints paths relative to *that* worktree’s root, not the primary
  root. In this fixture the linked worktree is entirely outside the primary worktree, so its dirt
  has no primary-root-relative path; a finding detail needs the worktree path plus the inner path.

Confidence: high.

---

## H3 — absent round dir vs an existing dir with ignored content

Fixture (`$S/h3`): repo with `.gitignore` = `*.bin`, committed; `existing/ignored.bin` present and
ignored; `empty-dir/` present and empty. Toplevel asserted (exit 0).

### Missing/empty paths — no error, empty output

```
[M1] $ git -C .../repo status --porcelain -uall --ignored -- missing-dir
  (no output)   [exit=0]
[M2] $ git -C .../repo status --porcelain -uall --ignored -- missing-dir/
  (no output)   [exit=0]
[M3] $ git -C .../repo status --porcelain -uall --ignored -- .ufo/waves/round-73
  (no output)   [exit=0]
[M4] $ git -C .../repo status --porcelain -uall --ignored -- .ufo/waves/round-72
  (no output)   [exit=0]
[M5] $ git -C .../repo status --porcelain -uall --ignored -- empty-dir/
  (no output)   [exit=0]
```

### Existing dir with one ignored file — exactly one `!!` record

```
[E1] $ git -C .../repo status --porcelain -uall --ignored -- existing/
  !! existing/ignored.bin     [exit=0]
[E2] $ git -C .../repo status --porcelain -uall --ignored -- existing
  !! existing/ignored.bin     [exit=0]
[E3] $ git -C .../repo status --porcelain -uall --ignored=matching -- existing/
  !! existing/ignored.bin     [exit=0]
[E4] $ git -C .../repo status --porcelain -uall --ignored
  !! existing/ignored.bin     [exit=0]
```

### Round-named dir that is itself matched by an ignore pattern

`.gitignore` extended to `*.bin` + `.ufo/waves/round-7*/`, `.ufo/waves/round-73/cache.pyc` created:

```
[W1] $ ... --ignored -- .ufo/waves/round-73
  !! .ufo/waves/round-73/cache.pyc      [exit=0]
[W2] $ ... --ignored=matching -- .ufo/waves/round-73
  !! .ufo/waves/round-73/               [exit=0]
[W3] $ ... --ignored -- .ufo/waves/round-72            (absent)
  (no output)                           [exit=0]
```

**Confirmed.** Calibration details:

- An absent path (missing dir, nested missing path, or existing-but-empty dir) is **exit 0 with
  empty output**, for both `dir` and `dir/` forms and for the exact `.ufo/waves/round-<N>` form.
  Absence must not be mapped to the counters’ exit-2 (could-not-evaluate) class.
- Both ignore modes yield exactly **one** record for this population, but the *shape* differs:
  traditional names the file inside the ignored dir, `--ignored=matching` names the directory with
  a trailing slash. A dedupe/path-equality step sees different strings.
- An entirely ignored round dir is only reachable through `status --ignored` or a directory
  listing. `git ls-files` lists index entries, so it would not see such a dir — **[INFERENCE]**
  (a general `ls-files` property; no `ls-files` observation was taken in this seat).

### Addendum `h3x` — tracked vs untracked under an ignore pattern

Fixture: `.ufo/waves/round-72/w1/tracked.pyc` committed **before** `*.pyc` was added to
`.gitignore`; afterwards an untracked `untracked.pyc` is created in the same dir.

```
[X1] $ git -C .../repo status --porcelain -uall --ignored -- .ufo/waves/round-72
  !! .ufo/waves/round-72/w1/untracked.pyc      [exit=0]
[X2] $ ... --ignored -- .ufo/waves/round-72/w1/tracked.pyc
  (no output)                                   [exit=0]
[X3] $ git -C .../repo check-ignore -v .ufo/waves/round-72/w1/tracked.pyc
  (no output)                                   [exit=1]
[X3b] $ git -C .../repo check-ignore --no-index -v .ufo/waves/round-72/w1/tracked.pyc
  .gitignore:2:*.pyc	.ufo/waves/round-72/w1/tracked.pyc   [exit=0]
[X4] $ git -C .../repo check-ignore -v .ufo/waves/round-72/w1/untracked.pyc
  .gitignore:2:*.pyc	.ufo/waves/round-72/w1/untracked.pyc [exit=0]
[X5] $ git -C .../repo status --porcelain -uall --ignored
  !! .ufo/waves/round-72/w1/untracked.pyc      [exit=0]
```

Documented, `man 1 git-check-ignore`: “`--no-index` — Don’t look in the index when undertaking the
checks. This can be used to debug why a path became tracked…”.

So: a committed file is never a `!!` record even when an ignore pattern matches its name, and the
default `git check-ignore` agrees with that (index consulted); only `--no-index` shows the pattern
match. This is why “committed-then-ignored leftovers” are outside the ignored population (the
`M >= N` bound is a further, separate restriction). Confidence: high.

---

## H4 — host triple vs `uname -r`

Live values (receipt `h4.out`):

```
$ uname -s        → Linux        [exit=0]
$ uname -m        → x86_64       [exit=0]
$ uname -r        → 7.2.11-arch1-1  [exit=0]
$ uname -v        → #1 SMP PREEMPT_DYNAMIC Fri, 16 Oct 2026 00:28:58 +0000  [exit=0]
$ uname -a        → Linux plazir27 7.2.11-arch1-1 #1 SMP PREEMPT_DYNAMIC Fri, 16 Oct 2026 00:28:58 +0000 x86_64 GNU/Linux
$ cat /proc/sys/kernel/osrelease → 7.2.11-arch1-1  [exit=0]
$ grep -E '^(ID|NAME|VERSION_ID|BUILD_ID|PRETTY_NAME)=' /etc/os-release
  NAME="Arch Linux"
  PRETTY_NAME="Arch Linux"
  ID=arch
  BUILD_ID=rolling   [exit=0]
```

Provenance and the moving field:

```
$ ls -l /etc/os-release
  lrwxrwxrwx ... /etc/os-release -> ../usr/lib/os-release      [exit=0]
$ pacman -Qo /usr/lib/os-release /etc/os-release
  /usr/lib/os-release is owned by filesystem 2025.10.12-1
  error: No package owns /etc/os-release                        [exit=1]
$ ls -1 /usr/lib/modules
  6.18.57-2-lts
  7.2.11-arch1-1                                                [exit=0]
$ pacman -Q linux linux-lts
  linux 7.2.11.arch1-1
  linux-lts 6.18.57-2                                           [exit=0]
$ cat /usr/lib/modules/*/pkgbase → linux-lts, linux            [exit=0]
$ pacman -Qo /usr/lib/modules/6.18.57-2-lts /usr/lib/modules/7.2.11-arch1-1
  .../6.18.57-2-lts/ is owned by linux-lts 6.18.57-2
  .../6.18.57-2-lts/ is owned by linux-lts-headers 6.18.57-2
  .../7.2.11-arch1-1/ is owned by linux 7.2.11.arch1-1
  .../7.2.11-arch1-1/ is owned by linux-headers 7.2.11.arch1-1   [exit=0]
$ grep -E 'upgraded linux ' /var/log/pacman.log | tail -5
  [2026-10-11T16:14:35-0300] [ALPM] upgraded linux (7.1.4.arch1-1 -> 7.2.3.arch1-3)
  [2026-10-20T09:16:42-0300] [ALPM] upgraded linux (7.2.3.arch1-3 -> 7.2.11.arch1-1)
```

Documented field semantics (`man 1 uname`, `man 2 uname`, `man 5 os-release`, all observed):

- `-s, --kernel-name` → “print the kernel name”; `-m, --machine` → “print the machine hardware
  name”; `-r, --kernel-release` → “print the kernel release”.
- `struct utsname`: `sysname` = “Operating system name (e.g., "Linux")”, `release` = “Operating
  system release (e.g., "2.6.28")”, `machine` = “Hardware type identifier”.
- os-release `ID=` = “A lower-case string … identifying the operating system, excluding any
  version information and suitable for processing by scripts”.

`pacman -Qi` (receipt `h4x.out`): both `linux 7.2.11.arch1-1` and `linux-lts 6.18.57-2` declare
`Architecture: x86_64`.

**Verdict.** The observed parts are confirmed: `uname -r` equals the kernel’s `osrelease` string
(`7.2.11-arch1-1`) and corresponds to the running `linux` package version `7.2.11.arch1-1` (same
release/arch/revision with the package’s dot-form separator; the modules directory carries the
uname form); this machine’s package log records the release
moving twice (`7.1.4.arch1-1 → 7.2.3.arch1-3 → 7.2.11.arch1-1`) while `-s` = `Linux`, `-m` = `x86_64` and `ID` = `arch` are
not derived from that release (os-release is owned by `filesystem`, not by any kernel package; both
installed kernels are x86_64 builds).

The temporal half — that `-s`, `-m` and `ID` *remain* unchanged after a kernel-only upgrade — is
**[INFERENCE]**: no reboot was performed (per ticket), so it rests on the documented field
semantics (`sysname` is the OS name; `machine` the hardware type; `ID` excludes version
information) plus the observed package ownership, not on a before/after reboot. Confidence: high
for the live values and for “`-r` is the moving field”; medium-high for the post-reboot inference.

Consequence for the C3 counter’s triple: grading `uname -s`, `uname -m`, `/etc/os-release` `ID`
cannot be broken by a kernel-only move; `uname -r` must stay out of the triple. Also: resolving
package ownership of `/etc/os-release` reports “No package owns” because it is a symlink — resolve
`/usr/lib/os-release` or simply read the file.

---

## Calibration notes handed to the round (no freeze edit, no module edit)

These are mechanics only; the C1/C2/C3 owners decide what to do with them.

1. **C1 `submodule`**: the predicate’s two halves are both observed non-vacuous on `2.56.0` — the
   per-submodule `git status --porcelain -uall` gives file-level paths, and the parent status at
   `--ignore-submodules=none` overrides a `.gitmodules` `ignore=all` and gives one
   submodule-level ` M <path>` record. `git submodule status` must not be used as the dirt check:
   it did not flag either tracked-content or untracked-content dirt.
2. **C1 `worktree`**: the primary status cannot see linked-worktree dirt in any form tried
   (default, `--ignored`, path-scoped); `worktree list --porcelain` enumerates absolute paths and
   marks detached entries; each path must be graded in place, and a linked worktree outside the
   primary root has no primary-root-relative path.
3. **C1 `ignored` / `ignored-older-label`**: absent pathspecs are exit 0 empty (never an error, so
   never exit 2); an existing ignored population yields one `!!` per path in either ignore mode
   (file-shaped in traditional mode, dir-shaped with `--ignored=matching`); committed files are
   never `!!`; default `check-ignore` agrees with status, `--no-index` does not.
4. **C3**: the triple (`Linux`/`x86_64`/`arch`) contains no kernel-release data; `uname -r` does.
   `/etc/os-release` is a symlink into the `filesystem` package.

## Files written (exact)

Under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-73/w1/`:

| Path | sha256 |
|---|---|
| `LAB01Probes/h1.out` | `e616cf5d78a7aeac24f4e6d831b32b44ab749b9e8648cf0e2c3acbc2deae741e` |
| `LAB01Probes/h2.out` | `b7f371aa03be6cbe368bbdf74c733be574aade8f569274af0df017b4da29b622` |
| `LAB01Probes/h3.out` | `6fbcc348f04c134546d8481eb79f6f2c09569c704f86893dbf2a249c59926763` |
| `LAB01Probes/h3x.out` | `aa216131ae7ea54c385e5e75b0330552916a8599e1ed626b3fca482f22f682ef` |
| `LAB01Probes/h4.out` | `56fd725abf3bb135e94feb3becfc0e03d40eb4217a9d3b755132cbed8caad59d` |
| `LAB01Probes/h4x.out` | `1eb1bedafc92015ddf26c4c09ad798df0edd5231f80ff266f05fee0576572a4c` |
| `LAB01Probes/probe.py.txt` | `fbf4a53e709fee9020c6858ef82ce517779eadc50796daa0c7f9f599bd6b0518` |
| `LAB01Probes/probe_extra.py.txt` | `9fca967feebd42d99b5b7a569610fb81fadb2d306bc560471710f8d369148be0` |
| `LAB01Probes.md` (this report) | — |

Every receipt begins `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec`. No `__pycache__` or `.pyc`
exists under `.ufo/waves/round-73/` (checked with `find`), because every python invocation ran
`PYTHONDONTWRITEBYTECODE=1` and the drivers live in `$S`.

## Boundaries

- Scratch: `$S = /fast/scratch/hyaku/kama-r73/LAB01Probes/` held the two driver sources and six
  fixture trees; all fixtures were created fresh per run and `$S` was deleted before yielding.
- No mutating git/jj command ran in the lane. Every fixture git call named `-C <fixture>`; every
  commit used `-c user.name=fixture -c user.email=fixture@invalid`; each fixture’s toplevel was
  asserted equal to its directory **immediately after `git init` and before that repository’s first
  `git add`/commit** (the receipts show the `rev-parse --show-toplevel` / `[assert ok]` pair before
  the first `commit` line in each), and the linked worktree was asserted immediately after
  `worktree add`. Submodule creation used `-c protocol.file.allow=always`.
- Commit SHAs printed in the receipts are per-run values (fixtures are rebuilt from scratch on every
  run, including commit timestamps); no claim in this report depends on a particular SHA. The
  meaningful bytes in those lines are the status prefixes, which are stable across the runs made
  here (`M mod`, `M base.txt`, `?? untracked.txt`, and the space prefix of `submodule status`).
- Nothing was written to the fleet repo, `MANIFEST.json`, `.ufo/state/`, sibling lanes, or
  `plans/round-73-claims.md`. No host state was written; `pacman` ran queries only.
