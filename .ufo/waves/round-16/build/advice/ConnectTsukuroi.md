# ConnectTsukuroi — tsukuroi-shokunin overlap scan (read-only seat)

capture: 2026-10-20T13:20–13:29Z (10:20–10:29 -0300)
kama base observed: HEAD `20e392e`; `git status --short` → `M tools/kama-probe.sh`, `?? tests/probe-verdicts/`, `?? .ufo/waves/round-16/` — sibling work in progress, so working-tree line numbers below are timestamped.
sources read: tsukuroi `SKILL.md`, `PROVINCE.md`, `MINT.md`, `AGENTS.md`, `LOG.md:775-850`, `corpus/QUALITY.md`, `corpus/knowledge/adjacency-handoffs-fleet-r1.md`, `tools/tsukuroi-census.sh` (grep + two ranges); kama `PROVINCE.md`, `corpus/knowledge/cross-lane-scope.md`, `tools/kama-probe.sh` and `.ufo/waves/round-16/frozen/kama-probe-before.sh` (sha256 `93ee4302…cd64`).
Read-only seat: no probe, gate, harness, test, server launch, or install ran. Outputs are advice; L1 measures.

## 0. Summary

The two declarations do **not** collide on the measurement: kama owns the endpoint, tsukuroi owns the OS. They collide on the **durable artifact**: C2 installs ≈53.8 MiB of code under `~/.local/opt` and a PATH shim under `~/.local/bin`, and neither province's write boundary nor either census declares or sees that tree. The pacman pause is a second, explicit contradiction: the always-on RULES channel order lists pacman first; tsukuroi's own record requests a host-wide tooling pause. Kama must hand off a host-inventory receipt and must not absorb package health, installs, or restarts.

## 1. Contested scope

### A. `~/.local/opt/llama-b11755` + `~/.local/bin/llama-server` — unowned-path class

Observed (read-only `ls -la`, 10:2x local): install tree `total 55128` KiB, mtimes 2026-10-20 08:10; `~/.local/bin/llama-server` is a symlink to `/home/vgpnk/.local/opt/llama-b11755/llama-server` (10:17); model `~/.cache/kama-shokunin/models/stories260K.gguf` = 1,185,376 B (10:17). No digest of any of these was taken by this seat.

- kama's declared write boundary names only three trees: `PROVINCE.md:45-46` — "kama never writes to `~/.config`, `~/.omp`, or systemd units." `~/.local/opt`, `~/.local/bin`, and `~/.cache` are undeclared write surfaces, not forbidden ones.
- tsukuroi owns the package/foreign inventory: `PROVINCE.md:8-9` — "pacman state (`pacman -Qkk` verify loops, foreign/AUR census, `.pkg.tar.zst` receipt discipline)".
- Neither arm of that census sees this tree. The foreign arm compares "`pacman -Qm` (name version per row)" (`tools/tsukuroi-census.sh:624`); `-Qm` enumerates pacman-known foreign packages, so a bare tarball with no local DB entry is outside it [INFERENCE: pacman foreign semantics; not exercised here]. `grep -n 'HOME\|~/\|/home/' tools/tsukuroi-census.sh` returned no matches (bounded grep, 2026-10-20); the only `command -v` use is a dependency check, `have() { command -v "$1" …}` (`:497`), not a PATH/ownership inventory.
- Precedent for the class, not a missing capability: tsukuroi had to add a separate root arm because "`/` is owned by no package (`pacman -Qo /` rc=1), so -Qkk cannot judge it" (`tools/tsukuroi-census.sh:355-357`), and QUALITY #13 states "because -Qkk cannot see /, the census separately reports root-directory mode" (`corpus/QUALITY.md:17`). A tarball install is the same structural case on a user path.
- Province tension to state, not smooth over: `kama PROVINCE.md:10` says kama "never claims an installed server". C2's install is therefore a **test capability artifact**, not a registered producer; the round must say so and must not let the install read as serving-domain evidence.
- The symlink is also a PATH-resolution fact no census here covers: tsukuroi has no PATH/shim inventory (bounded grep above), and kama's registry is baseURL-only. SentinelInstallChain audits shadowing; the receipt should record the symlink target so a later audit need not guess.

**Split:** kama retains the artifact and its provenance receipt; tsukuroi would retain host inventory only if it declares an unowned-path arm; the operator owns retention and removal (tsukuroi "Never installs, upgrades, or removes packages" `PROVINCE.md:27-28`; kama's boundary grants no host-tree removal). Kama must **not** add the binary or model path to `registry/endpoint-consumers.tsv` — that registry holds baseURL consumers (`PROVINCE.md:11`; `corpus/knowledge/cross-lane-scope.md:9-18`) — and must not assert package health.

### B. Pacman pause vs the RULES channel order

- `/home/vgpnk/.omp/agent/RULES.md:7` — "Channel order: `sudo pacman -S --needed --noconfirm <pkg>` → … official release binary into `~/.local/bin`" — versus this wave's contract: "ALL pacman transactions are PAUSED host-wide" (`.ufo/waves/round-16/build/spec.json:2`).
- tsukuroi has already recorded the cause and its own containment: `LOG.md:785-786` — "Host incident ground truth: … 'HOST PARTIAL UPGRADE during mado r15'"; `LOG.md:787-789` — "No install, removal, upgrade, downgrade, reboot, service action … is part of this round"; `LOG.md:833-835` — the fleet L0 question "requests operator recovery and a host-wide tooling pause; no package or service action is taken."
- The update-safety gate is read-only and refuses installs in its own text: `SKILL.md:1641-1644` — "Bare `pacman -Sy` is unsupported"; `SKILL.md:1663` — "do not install it or substitute bare `pacman -Sy`"; `SKILL.md:1830-1832` — "this round installs no package … any full `-Syu` remains an operator action behind the news gate."
- Measured residue behind the pause: `SKILL.md:1646-1649` — "This host ran bare `-Sy` twice (`/var/log/pacman.log:1405`, `:2287`)"; after `:2287`, 7 `-S`/`-Rns` transactions with "0 `upgraded` / 64 `installed` lines".
- Boot-chain blocker: `SKILL.md:1833-1835` — "Installed `mkinitcpio 41.1-1` with 42.2-1 pending and two `/new_root`-only hooks make mkinitcpio-42 compatibility an untested risk, not a clearance"; `LOG.md:789-790` calls the blocker "operator-owned". No lane may read the gate as clearance.

**Split:** there is no "route the install through tsukuroi" path — tsukuroi refuses installs by province (`PROVINCE.md:27-28`), and its gate is manual, read-only advice. C2's official-release-binary channel is the compliant channel for this wave. The install record must state **no pacman transaction ran**, and the RULES.md:7-vs-pause contradiction belongs to the integrator/L0, not to kama or tsukuroi. [INFERENCE] the later, narrower host-wide pause supersedes channel 1 for this wave; the contract text itself is explicit.

### C. Service restarts and unit writes

- kama: `PROVINCE.md:45-49` forbids `~/.config`, `~/.omp`, systemd-unit writes; `PROVINCE.md:27-28` — "restoring a unit is operator-owned work".
- tsukuroi: `PROVINCE.md:27-28` — "Never installs, upgrades, or removes packages; never restarts services."; `SKILL.md:156-162` lists "`systemctl start/stop/restart/enable/disable/preset`" as forbidden.
- C2's `start_new_session` llama-server is not a systemd service; no unit exists. That makes the seam clean but also **unobservable**: tsukuroi's unit plane cannot see the process, so kama's `listeners` census is the only trace (`PROVINCE.md:10`; working-tree capture 13:29Z: `tools/kama-probe.sh:708` `cmd_listeners`, dispatch `:1127`).

**Split:** both provinces agree; restate as a shared prohibition. A failed live launch must never be "fixed" by a unit write or a restart. Teardown proof must be kama's own bounded negative.

### D. Host-runtime failure (ldd, CPU backend, RAM) has no declared route

- ADJ-01 is directional tsukuroi→kama: tsukuroi retains "Kernel, driver, device and user-unit state" and "Kama must obtain its own endpoint evidence" (`PROVINCE.md:46`). There is no kama→tsukuroi row for a host finding produced by a sibling's own harness.
- The table's own rule covers the gap: "If no row fits, report to the integrator" (`PROVINCE.md:59-61`); "unresolved ownership goes to the protocol integrator, never to whichever lane answered first" (`PROVINCE.md:41-42`).

**Split:** a missing shared library, CPU-backend failure, or RAM shortfall is a host finding. Kama reports it via the integrator with the exact `ldd`/command/exit, and does not install a system package or driver to make the live receipt pass. Lane-local tool acquisition (RULES.md:3-9) is a different act from host remediation, which tsukuroi reserves to the operator (`PROVINCE.md:27-28`). [INFERENCE] on the routing; the prohibition is explicit in both provinces.

### E. Verdict vocabulary / calibration

- tsukuroi's discipline is directly reusable: fixed vocabulary, "three states, never a scalar score"; "Every verdict carries the probe and the observed value that produced it, so a non-author can re-derive it" (`SKILL.md:27-29`); "The third state is not 'corrupt'; it is 'cannot be assessed read-only'" (`SKILL.md:29-30`).
- kama's frozen vocabulary: `frozen/kama-probe-before.sh:55`; the new state is already planted in the working tree at `tools/kama-probe.sh:60`, branch `:501-505`.
- Calibration advice: give `MODEL_LOADING` a **means / never means** row in the same shape. Means: `GET /v1/models` returned 503 with the exact llama.cpp loading envelope at probe time. Never means: will become ready, model is correct, server is healthy, or "any 503 is loading" (the scope limit keeps "no slot available" as `FOREIGN_SERVICE`). This is the same guard tsukuroi uses to keep `BLOCKED` from being read as "corrupt".
- Cross-site consistency: adding a state to a fixed vocabulary is not one edit. Frozen enumeration sites: `:55` (VOCAB), `:680/:687` (summary counter), `:895` (baseline validator). The working tree has updated all three (`:60`, `:721/:731`, `:937`) as of capture; a missed site makes `latest.tsv` drop rows with "dropping malformed baseline row" (`frozen:896`). State this in the C1 report so a later reader can re-derive the wiring.
- Residual overreach (advice only, not this seat's fix): `frozen:521-522` emits reason `non-2xx-non-model-http` with evidence "(non-2xx HTTP from a non-model service)" — it asserts a service's **nature** from one response, the same class C1 corrects. Evidence text is not persisted ("Persisted rows exclude evidence, notes, resolved URLs" `frozen:47`), but the **reason is** persisted (the `latest.tsv` row is "id,verdict,reason,served,port,fmatch", `frozen:42`). Keep the reason code stable if the prose is softened. [INFERENCE from those two comments; persistence was not exercised here.]

### F. Registry inclusion

`endpoint-consumers.tsv` rows are baseURL consumers (`PROVINCE.md:11`; `cross-lane-scope.md:9-18`). A tarball binary and a GGUF file are not consumer pins; adding them would change the registry's meaning and could make `check` evaluate a non-consumer path. Keep the receipt beside the wave artifacts, not in the registry.

## 2. What kama must hand off rather than absorb

1. **Host-inventory facts** of the C2 artifacts — path, realpath, provenance, pacman owner = none, retention = operator.
2. **Host-runtime defects** — via the integrator, with tsukuroi as probable owner and exact `ldd`/command/exit.
3. **Nothing else**: no package-health verdict, no removal, no restart, no unit, no pacman action, no claim that a server is installed.

## 3. Reusable convention (adopt the cheap ones)

- **Handoff packet + closure states**: `PROVINCE.md:54-68`; "Track closure states separately: `prepared`, `reported`, `acknowledged`, `accepted`, `resolved`. Acknowledgement is not acceptance" (`:65-67`).
- **Bounded negatives**: `corpus/QUALITY.md:13` — "Every negative claim includes its bounded search/probe sweep command, scope and date." This is exactly what C2's "tears it down and proves teardown" and "no `~/.config`/systemd writes" need.
- **obs / inf / unknown separate**: `corpus/QUALITY.md:6`.
- **Digest ≠ ownership**: `adjacency-handoffs-fleet-r1.md:63-66` — "A digest match is drift evidence, not ownership proof; the cited text supplies ownership."
- **Re-read the declaration, not the pointer**: `PROVINCE.md:70-73` — "Re-read the cited declaration before a later handoff." Concretely, tsukuroi's own `SKILL.md:144` still cites `PROVINCE.md:16-17` for "never installs", but those lines are the "Additional owned surfaces" heading; the sentence is at `PROVINCE.md:27-28`. Cite 27-28 in kama's report.
- kama already has the handoff **rule** (`cross-lane-scope.md:49-51`, ending "For host-owned configuration and services, report drift and leave the change to the operator"), but not closure states or the negative-claim rule. Two lines in the next knowledge entry cover both; no new gate needed.

## 4. Proposed move (one, bounded)

**Attach a host-inventory receipt to the C2 live receipt, in tsukuroi's packet shape, and route it `prepared`→`reported` to the integrator with tsukuroi named as probable owner.**

Fields (six — all already produced by the harness or one read-only command away):

1. install tree: path, realpath, version/commit, asset URL + sha256, channel, install date;
2. ownership: `pacman -Qo` on both paths → none (read-only; tsukuroi's allowed verbs include `-Qo`, `SKILL.md:149-150`);
3. symlink: target, creation time;
4. listener: bind address/port/pid + teardown sweep (`ss -ltn`, loopback scope, timestamp, port absent);
5. model: path, size, sha256, source;
6. negatives: no `~/.config`, `~/.omp`, systemd-unit, or pacman-transaction touch — each either measured before/after or explicitly labelled design-level [INFERENCE].

**Why this is non-obvious:** the round reads the install as authorized capability acquisition and the server as ephemeral, so both provinces treat the mutation as out of scope — yet the artifact persists and neither lane's census sees it. Without the receipt, C2 improves the operability axis by leaving behind an invisible unowned tree and a PATH shim; with it, the host-inventory fact is falsifiable, bounded, and routeable without expanding either province.

**Axes:** operability (host-inventory completeness, teardown falsifiability) and calibration (bounded negatives, obs/inf/unknown separation). No probe verdict changes; no new host mutation.

## 5. Risks

- **Overlap with sibling audits**: SentinelInstallChain and ScoutHostRuntimeFacts will cover security and runtime depth. Keep the receipt to inventory + negatives and cite their reports; do not duplicate them.
- **Overclaimed negatives**: without before/after capture, "no `~/.config` write" is design-level, not measured. Label it so (QUALITY #13's shape), or it becomes a calibration defect.
- **Retention implication**: the receipt must name the operator as removal owner; kama cannot promise cleanup under its boundary.
- **Concurrent edit**: `tools/kama-probe.sh` changed during this seat (`M` vs HEAD `20e392e`, sha256 `d0d48d8f…` at capture). Frozen `93ee4302…cd64` is the stable before-anchor; re-anchor after integration.
- **Registry creep**: do not enter the binary/model in `endpoint-consumers.tsv`.
- **Province tension**: `PROVINCE.md:10` "never claims an installed server" — the receipt must read "capability artifact", not producer.

## 6. Verification L1 can run

- Cross-check every receipt field against the live-receipt JSON and the teardown `ss` output.
- Confirm each negative carries command + scope + timestamp, or is labelled design-level.
- Confirm `pacman -Qo` on both paths returns rc=1 (no owner) and that `/var/log/pacman.log` gained no line in the run window (bounded read).
- Confirm no registry row was added and no `~/.config`/`~/.omp`/unit mtime changed in the window.
- Confirm the receipt names operator retention and records closure state `reported`, not `accepted`.

## 7. Limitations and deviations

- Read-only: no probe, gate, harness, test, server, or install ran; no digest of the installed binaries or model; no endpoint request.
- Deviation recorded, not claimed as verification: one `ls -la` on the three C2 artifact paths (presence/time/size only), per tsukuroi's seat-scope rule `corpus/QUALITY.md:33` (R16-SEAT-SCOPE).
- tsukuroi declarations were read 2026-10-20; they drift (`PROVINCE.md:70-73`). kama working-tree anchors are timestamped because the probe is under active sibling edit.
- Installs/updates by this seat: none.
