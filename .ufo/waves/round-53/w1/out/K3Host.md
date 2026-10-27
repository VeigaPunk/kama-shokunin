# K3Host — round 53 (C1 host-file rule attack)

**Verdict: the host-file rule is sound for a uid-1000 attacker on this host (no acceptance bypass found), and the btrfs st_dev divergence it relies on is real — but the frozen rationale mis-diagnoses the mechanism ("btrfs/overlay"; there is no overlayfs here), the dev-drop is wider than necessary (the maps dev is recoverable exactly from /proc/self/mountinfo), and the trusted set is any root-owned file — demonstrably broad, since root-owned third-party libraries under /opt pass with zero byte comparison. This breadth is the preregistration's own disclosed limit, so C1's met=True stands; the fixes are a comment correction plus mountinfo-based dev comparison now, and host-set anchoring as a round-54 predicate change.**

Seat: K3Host (critic, leaf). Target of the attack: the C1 host-file rule —
`stat() shows uid 0, the row's inode, and the counter cannot write; the row's dev is
not compared` (preregistration C1 predicate; implemented at
`tools/round53-replay-code-audit.py:444-450` and `tools/kama-live-replay.py:337-341`).
No lane files were modified; the lane tree was read-only throughout. Full raw probe
transcript: `K3Host/K3Host-probe-evidence.txt` (89 lines, captured 2026-10-27T06:21Z).

## Q1 — btrfs/overlay st_dev divergence: CONFIRMED, mechanism pinned, collisions real

Commands (transcript sections 1-6):

- `stat -c '%D %d %i %u %a' /usr/lib/libc.so.6` → `%D=20 st_dev=32 inode=13506903 uid=0 mode=755`
- `grep libc /proc/self/maps` → `7f900a800000-... r--p 00000000 00:1e 13506903 /usr/lib/libc.so.6`
  → stat st_dev minor is **32 (0x20)** while the maps dev column is **00:1e (minor 30)**.
  The counter's "00:1e vs 00:20" pre-freeze observation reproduces exactly. (exit 0)
- `findmnt /` → `btrfs /dev/mapper/root[/@]`; `grep ' - btrfs ' /proc/self/mountinfo` → four
  subvolumes `@ @home @pkg @log`, **every one with mount dev `0:30`** = the maps dev.
  No overlayfs mount exists anywhere on this host, so the frozen comment's
  "btrfs/overlay" is wrong about overlay (exit 0).
- Per-subvolume stat st_dev: `/` `%D=20`, `/home` `%D=38` (0x38=56), `/var/cache/pacman/pkg`
  `%D=39`, `/var/log` `%D=3a`. Mechanism: **stat() reports btrfs's per-subvolume anonymous
  device; /proc/<pid>/maps reports the mount device (0:30), which /proc/self/mountinfo
  also reports.** Verified live: an executable mmap of a file on `@home`
  (`/home/vgpnk/.local/opt/llama-b11909/llama-server`) shows maps dev `00:1e` while
  `fstat` says `st_dev=56 (0x38)` (transcript section 4, python probe, exit 0).
- **Inode collisions across the two device views are real**: btrfs inode numbers are
  unique per subvolume, not per fs. `/`, `/home`, `/var/cache/pacman/pkg` and `/var/log`
  are four distinct directories that **all have inode 256** (transcript section 6). In a
  maps row every one of them appears as `00:1e 256`. So with the dev column unused, the
  identity (path, dev=00:1e, inode) that receipts carry for host files is ambiguous
  across subvolumes of this filesystem.

Impact on the counter: for its own in-namespace accept/reject the dev-drop changes no
verdict (the counter `os.stat`s the path in the shared mount namespace, so the inode it
reads is the inode of the file the path resolves to, and replacement attacks change
inode/uid and are caught). But the relaxation was **unnecessary**: mountinfo recovers
the maps dev bit-for-bit (0:30 == 00:1e) for btrfs here and the model mapping on xfs
`/fast` already matched exactly at build (`c1-build.out`: dev `103:05` == stat major
259 minor 5). Compare mountinfo dev and the cross-subvolume collision stops mattering.

## Q2 — root-owned, user-NOT-writable, NON-system libraries the server could map: FOUND, and both implementations accept them

Command (transcript section 8): `find /opt /usr/local /srv /var/lib /home -name '*.so*'
-type f -uid 0` → dozens of hits, e.g. `/opt/1Password/libffmpeg.so` (uid 0, mode 644),
`/opt/spotify/libcef.so` (uid 0, mode 644), `/opt/intel/oneapi/compiler/2026.0/lib/libiomp5.so`
(uid 0, mode 755). All are world-readable (mmap-able; `/` is not mounted `noexec`),
none is an OS system library, and none lives in a vgpnk-writable directory
(`/opt` and `/usr/local` are `root:root 755`; transcript section 7).

Acceptance demo (transcript section 9, python reimplementation of the two frozen
branches against real stat data, exit 0): for each of the three files above, the
counter's branch `st.st_uid != 0 or str(st.st_ino) != ino or os.access(path, os.W_OK)`
(`round53-replay-code-audit.py:447`) is False (i.e. **accepted as a host file**), and
the replay's branch `e.get("uid") != 0` (`kama-live-replay.py:362`) records it as a
trusted host entry. **Bytes are compared to no reference** — exactly the
preregistration's disclosed limit ("host libraries ... are only classed as root-owned
and not writable; their bytes are not compared"). The live recorder would even hash
and store its bytes (`kama-llamacpp-live.py:774-838`), but nothing checks them.

Meaning: the trusted-code set is "any root-owned, counter-unwritable file", which on
this host silently includes third-party application libraries and grows on any package
install, with no frozen-set diff and no new-file signal (the counter only counts
`host`). Demonstrated breadth is wider than the "libc, libstdc++, libssl, ..." the
preregistration names. Disclosed tradeoff → not a defect for round 53; anchor it later
(see Fix 4).

## Q3 — could a user-owned lib under /usr exist?

Not without privilege, for direct placement (transcript section 7, all exit 0):
- `find /usr -xdev -type d -writable` → **0** writable directories for uid 1000;
  `/usr/local` and `/opt` are `root:root 755`.
- `find /usr -xdev ! -uid 0 -print` → exactly one file: `/usr/lib/systemd/system-sleep/keyboard-backlight`,
  owned **vgpnk:vgpnk** — proof that user-owned files under `/usr/lib` do occur in
  practice (installed via privilege at some point). It is not a library and its
  directory is root-owned, so it cannot be leveraged further.
- `fs.protected_hardlinks = 1`, `fs.protected_symlinks = 1` — no hardlink/symlink
  shortcut into library directories.
- Both frozen implementations reject any user-owned mapping: `uid != 0` →
  `code-mapping:foreign` in `kama-live-replay.py:362-363` and a `code:` problem in
  `round53-replay-code-audit.py:447-450`. The C1 fixture set exercises exactly this
  shape with a user-owned `libfake.so` (`kama-live-replay.py:577-580`).

Caveat that must be stated (environment condition, outside the counter's threat model):
`sudo -n true` succeeds (exit 0) and vgpnk is in the `docker` group (`docker ps` works,
exit 0), so uid 1000 **can mint root-owned files anywhere** on this host via either
path. The rule's premise "root-owned ⇒ not user-controllable" is therefore conditional
on "user = uid 1000 without sudo/docker". Inside the counter-user model the rule holds;
if the lane ever wants the stronger meaning "operator-controlled", it needs a package
or frozen-set anchor, not a uid check.

## Findings

- **F1 (fixable defect, contract-visible, cosmetic):** the frozen rationale
  mis-diagnoses the mechanism. `round53-replay-code-audit.py:444-446` comment: "the
  maps `dev` of a file on this host's **btrfs/overlay** root is not the st_dev stat()
  reports (00:1e vs 00:20 ...)". There is no overlayfs on this host; root is btrfs
  subvolume `@`, stat shows the per-subvolume anonymous device, maps shows the mount
  device 0:30, and mountinfo reproduces the maps dev exactly. The same wrong phrase is
  in `kama-llamacpp-live.py:778-780` ("this host's btrfs/overlay root reports another
  st_dev than maps does"). Show with: `grep -n 'btrfs/overlay'
  tools/round53-replay-code-audit.py tools/kama-llamacpp-live.py` → matches at
  :44 and :779. Proposed corrected wording is in
  `K3Host/K3Host-stronger-rule.patch`. (The numbers "00:1e vs 00:20" themselves are
  accurate.)
- **F2 (unnecessary relaxation, low severity):** dev is not compared at all even though
  it is recoverable from /proc/self/mountinfo on this host (and inode collisions across
  subvolumes are real, Q1). Today this only weakens receipt identity, not verdicts, so
  it is not a kill; the smallest correction is the mountinfo-dev comparison in
  `K3Host/K3Host-stronger-rule.patch`.
- **F3 (disclosed tradeoff, evidenced):** the trusted set is unanchored "any root-owned
  file" (Q2). Accept for round 53 per the preregistration's explicit limit; recommend
  round-54 anchoring (Fix 4).
- **F4 (environment condition, informational):** sudo + docker group make uid-0
  mintable by uid 1000 on this host (Q3); the rule's premise must be read as scoped to
  the unprivileged counter user. One user-owned file already exists under `/usr/lib`.
- **F5 (informational hardening):** the counter's host branch does not check
  `S_ISREG` (the live tool does, `kama-llamacpp-live.py:817-819`) and does not check
  parent-directory writability; replacement attacks are caught by the inode/uid check,
  so severity is informational.

## Smallest safe correction

1. (F1/F2) In a future counter revision: replace "btrfs/overlay ... not compared" with
   the pinned mechanism and compare `mountinfo_dev(path)` (major:minor of the covering
   mount from /proc/self/mountinfo) against the maps dev, keeping uid 0, inode match,
   not-writable; add `S_ISREG` and a parent-directory writability check. Reference diff:
   `K3Host/K3Host-stronger-rule.patch`.
2. Keep C1's round-53 verdict as measured: none of F1-F5 lets a uid-1000 attacker pass
   foreign code through the host-file leg, and the archive-member leg is byte-compared
   from /proc/<pid>/mem.
3. Round-54 predicate item: freeze the observed 13-file host set (path, mount-dev,
   inode, size, mtime, sha256) and fail `code` on any new/changed/missing host file;
   optionally anchor to `pacman -Qo` ownership with a clean `pacman -Qk`.
4. Do not re-report the known integration items (SCORECARD §Round 53, LOG, QUALITY,
   README, SKILL registry, lesson, Planned (round 54)) — none are contradicted here.

## Evidence index

- `K3Host/K3Host-probe-evidence.txt` — full transcript of every probe above with exit
  codes (sections 0-9; identity, libc stat/maps, mountinfo, per-subvolume st_dev, live
  @home mmap probe, inode-collision table, /usr writability scan, protected_* sysctls,
  sudo/docker probes, root-owned .so inventory, acceptance demo).
- `K3Host/c1-build.out.cited` — copy of `.ufo/waves/round-53/measured/c1-build.out`,
  the L1 receipt cited above (13 root-owned host files; model dev `103:05`).
- Frozen sources cited by line: `tools/round53-replay-code-audit.py:44,393-397,443-450`
  (comment, code_observe, host branch); `tools/kama-llamacpp-live.py:774-838,817-820`
  (code_mappings recorder, dev tolerance for root-owned files);
  `tools/kama-live-replay.py:309-311,337-341` (verify_code contract and host branch).
- No tools were installed or upgraded this seat; no pacman transaction attempted
  (host-wide pause); no services started (no llama-server was ever launched — the only
  server-side process in my probes was a python one-shot mmap); scratch
  `/fast/scratch/hyaku/kama-r53/K3Host` removed after writing this report.

## Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K3Host.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K3Host/K3Host-probe-evidence.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K3Host/K3Host-stronger-rule.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/K3Host/c1-build.out.cited`
