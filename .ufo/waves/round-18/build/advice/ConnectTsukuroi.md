VERDICT: partial — pacman stays paused and mkinitcpio 42.2-1 is already installed; neither named file mentions llama-server or a stress tool.

Seat: KamaR18.ConnectTsukuroi-2. Read only `tsukuroi-shokunin/SKILL.md` and `tsukuroi-shokunin/corpus/README.md`. No install. No host probe. No lane measurement.

## Axes

- Operability (kama live `llama-server` lifecycle, and tsukuroi host mutation refusal).
- Calibration (tool exit 2 / gate not-evaluated stays distinct from a false check).
- Substrate fidelity (current-use boot text versus the still-printed pending-upgrade bullet).

## Evidence

### llama-server under `~/.local`

No hit in either file for `llama`, `gguf`, `ggml`, `.local/bin`, or `llama-server`. The only `.local` in the host-operability skill is cgroup memory, not a user prefix.

- `tsukuroi-shokunin/SKILL.md:1106` — ``memory.events[.local]`` (cgroup counter; not `~/.local`).

Tsukuroi therefore states no path, argv, port, or ownership rule for the operator binary `~/.local/bin/llama-server`. It also does not authorize replacing or packaging that binary. [INFERENCE] kama's own "operator-owned, never modify" rule remains the only constraint on that path; these two files add none.

### Pacman pause (binding)

- `tsukuroi-shokunin/SKILL.md:1853` — "all pacman transactions remain paused under the current operator ruling."
- `tsukuroi-shokunin/SKILL.md:1814` — "The dated decision is `BLOCKED_FOR_AGENT_PACKAGE_ACTION`."
- `tsukuroi-shokunin/SKILL.md:1830` — "this round installs no package, runs no service action, no privileged probe and no repair."
- `tsukuroi-shokunin/SKILL.md:156` — "`pacman -Sy` (`-Syu` too) writes the sync db".
- `tsukuroi-shokunin/SKILL.md:157` — "`pacman -S/-R/-U`, `yay`-install paths".
- `tsukuroi-shokunin/SKILL.md:1921` — "authorizes no pacman, mkinitcpio, limine-update, snapper or service action."
- `tsukuroi-shokunin/SKILL.md:1926` — "db.lck absent". Absence of the lock is not a clearance; the same notice does not lift the pause.
- `tsukuroi-shokunin/SKILL.md:1934` — "no installation is advised".
- `tsukuroi-shokunin/SKILL.md:1934` — "This capture does not query or resolve checkupdates, so its availability and any use elsewhere remain unknown".
- `tsukuroi-shokunin/corpus/README.md:162` — "pending updates remain unknown."
- `tsukuroi-shokunin/corpus/README.md:162` — "package/service/boot actions stay operator-owned."

`SKILL.md:1663` ("do not install it or substitute bare `pacman -Sy`") assumed `pacman-contrib` was absent. `SKILL.md:1934` supersedes that absence for `paccache` ("resolves /usr/bin/paccache") and still forbids installing. Kama must not run `pacman -S`, `-Sy`, `-Syu`, `-U`, or `yay` to fetch a server dependency, `pacman-contrib`, or a stress package.

### mkinitcpio story kama must not revive

The fleet tooling line that still says mkinitcpio 42 is a *pending* move of root to `/sysroot`, with `btrfs-overlayfs` and `plymouth` still expecting a `/new_root` directory, contradicts current-use text.

- `tsukuroi-shokunin/SKILL.md:1927` — "mkinitcpio 42.2-1 installed (local database entry)".
- `tsukuroi-shokunin/SKILL.md:1927` — "The \"Installed `mkinitcpio 41.1-1` with 42.2-1 pending\" reading is superseded".
- `tsukuroi-shokunin/SKILL.md:1947` — "image `/new_root` is a symlink to`/sysroot` in the42.2 UKIs and pathname compatibility was namespace-emulated."
- `tsukuroi-shokunin/SKILL.md:1947` — "Never revive a predicted silent no-op from the historical pending-upgrade paragraph."
- `tsukuroi-shokunin/corpus/README.md:150` — "the upgrade ran on 2026-10-20 and 42.x keeps `/new_root` as a symlink to `/sysroot`, so both hooks resolve (namespace emulation; not boot-tested)."
- `tsukuroi-shokunin/corpus/README.md:152` — "upstream may drop the compatibility symlink".

Contradiction, not smoothed: `SKILL.md:1927` keeps the sentence after line 1834 as "remains an untested risk, not a clearance." `corpus/README.md:118` still says "mkinitcpio-42 `/new_root` hook compatibility remains an untested risk with no clearance." `corpus/README.md:38` still prints "Pending `mkinitcpio` 42 upgrade strands two `/new_root` hooks". `corpus/README.md:149` says that Frontier bullet "is superseded", and `corpus/README.md:165` says "Historical Frontier bullets about pending42 ... remain superseded". Emulation is not boot or rollback certification (`SKILL.md:1947` — "This is not a whole snapshot boot or rollback certification.").

Kama must not run `mkinitcpio`, `limine-update`, or `bash tools/boot-chain-audit.sh --live` to "respect" that gate. `SKILL.md:1965` — "not run round18" and "privileged live reads only when separately authorized". `SKILL.md:1986` — "no current --live audit or boot action is inferred".

Also refuse `snapper list-configs`: `SKILL.md:1743` — "not a non-activating probe" (it can start `snapperd`). `SKILL.md:1749` — "Starting a fresh invocation is an operator-owned state change".

### Stress tooling (unnamed; adjacent facts bind)

No hit for `stress`, `stress-ng`, or `sysbench` in either file. Adjacent current-use facts:

- `tsukuroi-shokunin/SKILL.md:1938` — "earlyoom is installed1.9.0-1 and active/enabled atR18".
- `tsukuroi-shokunin/SKILL.md:1938` — "this later state cannot explain the historical OOM or certify other memory guards".
- `tsukuroi-shokunin/corpus/README.md:162` — "Runtime earlyoom/zswap ... are S060, not historical OOM attribution".
- `tsukuroi-shokunin/SKILL.md:159` — "`nvidia-smi -r` (GPU reset)" is a forbidden mutating verb. `nvidia-smi --query-*` is the allowed read (`SKILL.md:153`).
- `tsukuroi-shokunin/SKILL.md:1123` — historical "`sar`/`atop`/`dool`/`dstat` absent, no `/var/log/sa`" is not current for `sar`.
- `tsukuroi-shokunin/SKILL.md:1979` — "S060 resolves /usr/bin/sar and its /var/log/sa listing is empty, not a missing directory."
- `tsukuroi-shokunin/SKILL.md:1979` — "This does not backfill a pre-kill snapshot".
- `tsukuroi-shokunin/SKILL.md:1981` — "No package, restart, boot or recovery action is authorized."
- `tsukuroi-shokunin/SKILL.md:158` — `systemctl start/stop/restart/enable/disable/preset` is forbidden. Do not stop `earlyoom` or start a sysstat collector so a llama run has a load trace.

`SKILL.md:1979` says atop/dool/dstat "were not independently re-audited". Do not treat the old "absent" list as a reason to install them.

## Proposed move

One move. If the operator `llama-server` cannot be observed, keep C1 on the v3 could-not-evaluate path (tool exit 2; gate exit 3 only when the receipt is a well-formed v3 with every evaluated check true and the only shortfall a legitimate null). Do not repair the host to manufacture a pass.

Refused from this lane, for that failure and for any "while we are here" prep: every pacman/yay transaction; `mkinitcpio` and `limine-update`; `boot-chain-audit.sh --live`; `nvidia-smi -r`; `systemctl` lifecycle actions against `earlyoom` or sysstat; installing `stress`/`stress-ng`/`sysbench`/`atop`/`dool`/`dstat` or a second llama-server. Do not rewrite the pending-upgrade warning into a boot-chain task. The hooks resolve through the 42.2 symlink; that is not clearance to rebuild.

Calibration stays intact only if this refusal is limited to no observation (today's zero-observation exit 1 is the R4 defect). A server that answered and failed `models_alias_id`, `probe_model_ok`, or another targeted check stays a failed check, not exit 2.

## Risks

- Reading only `corpus/README.md:38` or `SKILL.md:1833` revives the pending-42 story and invites an initramfs rebuild. Current-use is `SKILL.md:1927` and `:1947` plus `corpus/README.md:149-153`.
- Widening exit 2 to a live wrong payload hides R5 targeted failures and harms calibration.
- `corpus/README.md:162` leaves pending updates unknown. Refreshing the sync db to "check safety" is the forbidden `-Sy` partial-upgrade path (`SKILL.md:156`, `SKILL.md:1641-1645`).
- earlyoom is active. [INFERENCE] a large GPU load could be killed; the pinned `stories260K` fixture is not shown in these two files, so this scan does not claim that fixture trips earlyoom. The binding part is: do not disable the killer.
- `SKILL.md:1926` last pacman.log line is `pacman -D -q --asexplicit` for zcode, with no "transaction completed" line in the R18 tail, so completion is unknown. Another transaction would stack on that unknown. Not a kama receipt field.

## Verification

L1 only. This seat did not run `c1/measure.py`, `c2/survivors.py`, or a lane gate.

- Re-grep the two files for `llama`, `gguf`, `stress-ng`, `sysbench` (expect no hits) and re-read `SKILL.md:1853`, `:1927`, `:1947`.
- C1 before/after: a zero-observation or pre-bind failure is tool exit 2, not exit 1, and not a pacman install.
- A control that already has a false targeted check still fails that check.
- Confirm no new listener on registry ports and no `pacman`/`mkinitcpio`/`nvidia-smi -r` in the seat exec log.

## Limitations

Knowledge notes, `SOURCES.md`, and `.ufo/waves/round-18/l1-capture/host-capture-r18.txt` were not opened. Quotes from those captures appear only as citations already printed in the two named files. `~/.local/bin/llama-server` was not stat'd. Installs: none.
