VERDICT: partial — kama/tsukuroi do not collide on endpoint measurement, but the persistent `~/.local` artifact has no accepting owner, and routed defect 5 must be disclosed by kama rather than delegated to tsukuroi as a repair.

# ConnectTsukuroi — round 17 build: host repair/install ownership (routed defect 5)

capture: 2026-10-20, kama lane tip `cff9e62f05aa7cfb9059444f62eb787100719713` (`git rev-parse master`); working tree carried sibling edits (`M .gitignore`, `M AGENTS.md`, `?? .ufo/waves/round-17/`), so working-tree line numbers below are timestamped.
sources read: tsukuroi `SKILL.md`, `PROVINCE.md`, `MINT.md`, `corpus/QUALITY.md`, `tools/tsukuroi-census.sh` (three ranges) only; kama `PROVINCE.md`, `LOG.md:938-945`, `corpus/lessons/round-16-verifier-spotcheck.md:100-125,180-189`, `corpus/knowledge/cross-lane-scope.md`, `.ufo/l0-questions.md:58`, round-16 `measure.py:276-292`, round-16 `live/receipt.json`, round-17 `build/make_spec.py`, `build/advice/{ScoutInstallFootprint,ScribeInstallDisclosure}.md`.
Read-only seat: no gate, harness, test, server, mutation runner or install ran; no port bound. Read-only observations used: `command -v -a llama-server`, `ls -l`, `stat`, `sha256sum`, `pacman -Qo/-Qq`, and one 4-line digest recompute. L1 should re-run anything it quotes.

## 1. Axes named

- **operability** — a host artifact that outlives the run is discoverable, owned, and re-checkable without re-deriving it by hand.
- **calibration** — every graded claim carries a probe that can distinguish the states it claims to distinguish; an ungraded recorded field is a defect, and cannot-evaluate is never a pass.

## 2. Contested scope

### A. "Host repair/install ownership" is not a handoff tsukuroi can accept

Round-17's routing text for this seat is `build/make_spec.py:219`: "host repair/install ownership: the llama.cpp b11755 install, PATH link and retained tarball (routed defect 5)". Tsukuroi's own declaration refuses exactly that authority:

- `tsukuroi-shokunin/PROVINCE.md:27-28` — "Never installs, upgrades, or removes packages; never restarts services. Detection and report; the operator remediates."
- `tsukuroi-shokunin/MINT.md:18-19` — "read-only detection and report; never installs, upgrades, removes, or restarts".
- `tsukuroi-shokunin/SKILL.md:144` restates it as "never installs, upgrades, removes, or restarts".

So a kama report that says "hand the install to tsukuroi" is dead on arrival; the repair authority is the operator's. Round-16 already reached the correct split on its own evidence: `corpus/lessons/round-16-verifier-spotcheck.md:186` — "Leave the install itself alone; it is operator-owned." [INFERENCE] The role string describes an adjacency, not a capability; it should not be read as an acceptance by tsukuroi.

### B. `~/.local/opt` is visible to neither census — the "host inventory" half is also unserviceable today

- Tsukuroi owns "pacman state (`pacman -Qkk` verify loops, foreign/AUR census, `.pkg.tar.zst` receipt discipline)" (`tsukuroi/PROVINCE.md:8-9`).
- Its foreign arm enumerates pacman-known foreign packages only: `tools/tsukuroi-census.sh:620` — `cap "$PACMAN" -Qm`. A tarball tree with no local-db entry never appears there; `grep -c 'HOME\|/home/' tools/tsukuroi-census.sh` returned `0` (2026-10-20), so no user-local path arm exists.
- The structural precedent is in the same gate: "`/` is owned by no package (`pacman -Qo /` rc=1), so -Qkk cannot judge it" (`tools/tsukuroi-census.sh:355-356`). An unowned `~/.local` tree is the same class on a user path; adding that arm is a tsukuroi **province** change, which is an L0/integrator decision, not something kama can request as a routine handoff.

Consequence: routed defect 5 cannot be closed by routing a finding to tsukuroi. Kama must disclose it in its own artifact and name the operator as the actor; a tsukuroi analysis packet, if ever wanted, needs an ownership ruling first — "unresolved ownership goes to the protocol integrator, never to whichever lane answered first" (`tsukuroi/PROVINCE.md:41-42`).

### C. The `/usr/bin` absence claim needs a discriminating probe

The spotcheck sentence is `corpus/lessons/round-16-verifier-spotcheck.md:116`: "the host had none: `/usr/bin/llama-server` is absent and no package owns it." The absence half is load-bearing and true (`ls -l /usr/bin/llama-server` → `No such file or directory`; `command -v -a llama-server` → only `~/.local/bin/llama-server`, 2026-10-20). The ownership half adds nothing to it:

```
$ pacman -Qo /usr/bin/llama-server            → error: No package owns /usr/bin/llama-server   rc=1
$ pacman -Qo /usr/bin/definitely-not-a-path-xyz → error: No package owns /usr/bin/definitely-not-a-path-xyz   rc=1
$ pacman -Qo ~/.local/bin/llama-server        → error: No package owns /home/vgpnk/.local/bin/llama-server   rc=1
```

`pacman -Qo` emits the same message and rc for an absent path as for an existing unowned one, so it cannot establish absence. Record `test -e`/`ls` for existence and keep `pacman -Qo` (if used at all) as a separate package-provenance fact — the exact conflation that C1 is repairing in `check.py` (recorded-but-not-graded vs graded).

### D. PATH precedence is a shell-local observation, not a host invariant

`kama/PROVINCE.md:68-69` says the link is "`~/.local/bin/llama-server` link (which now precedes `/usr/bin` on PATH) and the cache persist on the host; removal is the operator's call." In this shell that is literally true (`~/.local/bin` is PATH entry 4, `/usr/bin` entry 13); `command -v -a` finds only the link. It is [unknown] for a login shell, a systemd unit, or any lane runtime. State it as "observed in the invoking shell on 2026-10-20", or the sentence becomes the same class of overclaim as "no package owns it". The narrower true sentence is already in the spotcheck: "shadows nothing: no `/usr/bin/llama-server` exists" (`corpus/lessons/round-16-verifier-spotcheck.md:122`).

### E. The retained tarball is the one footprint fact not in any structured artifact

`~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` = 22,240,468 B, mtime 2026-10-20 10:17:48 -0300; sha256 `753bfa73…e226` per `LOG.md:940-942` and `ScoutInstallFootprint.md:39,113`. The round-16 receipt pins the extracted tree (`server.install_tree`, `install_tree_sha256 6c216313…`) and the launcher digest, but contains no key for the archive; `.ufo/l0-questions.md:58` names "`~/.local/opt/llama-b11755`" and the link, not the archive. Removal owner: operator. This is exactly routed defect 5, and two sibling seats already supply the facts (`ScoutInstallFootprint.md`) and the prose (`ScribeInstallDisclosure.md:1-5`, `:37`); the missing layer is a graded, re-checkable record (§5).

### F. The declared disclosure route is dangling

`kama/PROVINCE.md:51-53` sends out-of-province facts to `corpus/knowledge/cross-lane-scope.md`, but `grep -c tsukuroi corpus/knowledge/cross-lane-scope.md` returned `0` at the lane tip: the registry has consumer/endpoint rows only (`:10-18`, `:24-30`) and no host/install row. Adding one is a lane-owned corpus edit for L1; it is not a claim expansion and needs no new gate.

## 3. What kama must hand off rather than absorb

1. **Retention/removal** of tree + PATH link + archive + `~/.cache/kama-shokunin` model → **operator** (L0 question (b), `.ufo/l0-questions.md:58`; the lane already says "removal is the operator's call", `kama/PROVINCE.md:69`). Tsukuroi is not a removal channel for the reason in §2A.
2. **Package-ownership / foreign census** (`pacman -Qo`, `-Qm`) → tsukuroi's analysis surface (`PROVINCE.md:8-9`; `-Qo` is an allowed read-only verb, `SKILL.md:148-152`) — but flag that its census has no `~/.local` arm (§2B), so this is a request for a ruling, not an assignable task. Kama must not build that arm.
3. **Disk headroom / cleanup verdict** (`df`, `du`) → tsukuroi read-only (`SKILL.md:125-126`, "Headroom + cache shape"). Kama may quote the 22 MB archive size as provenance; it must not grade host capacity.
4. **Host-runtime failures** (loader, CPU backend, RAM) → integrator, with the exact command/exit; never install a system package or driver to make a live receipt pass.
5. **PATH policy** → nobody claims it. Neither province's owned-surfaces table has a PATH/shim row; kama records its own shell-local `command -v -a` result and stops there.
6. **Do not put the binary, model or archive in `registry/endpoint-consumers.tsv`** — rows are "baseURL pins in surviving/loadable consumers" (`kama/PROVINCE.md:11`); a host artifact is not a consumer pin, and adding it would make `check` evaluate a non-consumer.
7. **Never absorb a host-health verdict into the C2 receipt.** The receipt is a record of the tool's own child; package state, boot, and service health stay out (§5 defines the exact boundary).

## 4. Reusable conventions (cheap, already written elsewhere)

1. **Gate registry row** — `tsukuroi/SKILL.md:1705-1709`: Name | Kind | Entry command | Verdict map | Self-test | Pinned values | Write scope | Owner. Kama's growing gate set (`check.py`, `check-receipt.py`, `fault-controls.py`, `mutants.py`, `controls.py`) has no single table saying which is a gate, its exit map, its self-test, its write scope. One row per gate makes "which command is the counting command" answerable without reading `make_spec.py`.
2. **Self-verifying case contract** — `tsukuroi/SKILL.md:269-271`: every case "asserts exit code + verdict + plane substring + fixture byte-unchanged, plus a `host=fixture-host` check". Transplant: each C1/C2 control case should assert exit code, the specific faulted row/check id in output, and **the nine matrix files byte-unchanged** after the case. The digest is already in-lane and reproduces exactly today: `round-16/measure.py:280-286` defines `matrix_digest()` ("The digest covers every *.json file name and its sha256 under tests/probe-verdicts/, sorted by name") and pins `EXPECTED_MATRIX_SHA256`; I recomputed 9 files → `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` (matches). This turns C1's HARD CONSTRAINT from a promise into a per-case assertion.
3. **Cannot-evaluate ≠ pass** — `tsukuroi/SKILL.md:411-412`: "an unreadable plane → `BLOCKED` arm, never a fake pass"; `tsukuroi/SKILL.md:29-30`: "The third state is not 'corrupt'; it is 'cannot be assessed read-only'". This is the same shape C2 needs for exit 2 on internal faults and C1 for exit 2 on harness/schema errors — and it is the reason `loading_envelope_exact` being recorded-but-ungraded is a defect, not a gap.
4. **Bounded negatives** — `tsukuroi/corpus/QUALITY.md:13`: "Every negative claim includes its bounded search/probe sweep command, scope and date". Applied here: the `/usr/bin` absence sentence needs its `ls`/`test -e` command, scope, and date (§2C/§2D).
5. **Seat scope** — `tsukuroi/corpus/QUALITY.md:33`: "a read-only assignment is not permission for extra package/log/ownership probes". Kama's advice seats should not run `pacman -Qo` to "finish" a disclosure; L1 measures. (This seat did one `pacman -Qo` semantics probe and declares it; it is not a census.)
6. **Re-read the cited declaration** — `tsukuroi/PROVINCE.md:72`: "Re-read the cited declaration before a later handoff." Concrete proof of why: tsukuroi's own `SKILL.md:144` still cites `PROVINCE.md:16-17` for "never installs", but 16 is the "Additional owned surfaces" heading and 17 a blank line; the sentence is at `PROVINCE.md:27-28`. Kama's report must cite 27-28.
7. **Closure states** — `tsukuroi/PROVINCE.md:65-68`: "Track closure states separately: `prepared`, `reported`, `acknowledged`, `accepted`, `resolved`. Acknowledgement is not acceptance". Applied here: the routed-defect-5 disclosure can reach `reported` this round; it cannot reach `resolved` without an operator decision on question (b).

## 5. Proposed move (one, bounded): grade the disclosure in the v2 receipt

**Claim.** Routed defect 5 is currently satisfied by prose in a report (`ScribeInstallDisclosure.md`). Prose is not re-checkable and three seats re-derived the same bytes this round. Put the four missing facts in the C2 receipt and grade them, without grading any host-health or package state.

**C2 (additive to `kama-llamacpp-live/v2`; all v1 fields unchanged):**

```json
"host_footprint": {
  "path_resolution": ["/home/vgpnk/.local/bin/llama-server"],
  "usr_bin_llama_server": {"probe": "test -e /usr/bin/llama-server", "exists": false},
  "retained_asset": {"path": "/home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz",
                     "probe": "stat", "present": true, "bytes": 22240468,
                     "sha256": "753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226"},
  "removal_owner": "operator (install and removal operator-owned; package ownership not assessed here)"
}
```

- `path_resolution` is the tool's own PATH scan for `llama-server` (Python, not a shell); it is the fact the PROVINCE sentence claims.
- `usr_bin_llama_server` is existence only. No `pacman -Qo`, no package field — that half is handed off (§2C, §3.2).
- `retained_asset` records the archive; `present:false` with `bytes`/`sha256` null is a valid recorded state, so a later operator cleanup does not invalidate an old receipt.
- `removal_owner` is a string, not a graded policy.

**`tests/llamacpp-live/check-receipt.py` (v2 branch only; v1 untouched) — four rules, all shape/consistency, none re-executes a host probe:**

- **H1** `host_footprint` is required for v2; absent block → invalid (fail-closed).
- **H2** `usr_bin_llama_server.exists` must be a JSON boolean, and `probe` must name an existence probe (`test -e`, `test -f`, `ls`, `stat`, `command -v`); any `pacman`-based probe is invalid with the reason "pacman -Qo cannot establish absence (identical rc=1 for absent and unowned paths)". This is the calibration rule: the graded artifact must record a probe that discriminates.
- **H3** consistency: `path_resolution` must be a non-empty list containing the receipt's `server.arg`; if `/usr/bin/llama-server` appears in it, `exists` must be true.
- **H4** `retained_asset`: `present` true → integer `bytes > 0` and 64-hex sha256; `present` false → both null; `probe` always present.

**`tests/llamacpp-live/controls.py` — two receipt-mutation controls (K8, K9), reusing the existing K0 good receipt:**

- **K8** rewrite `usr_bin_llama_server` to `{"probe": "pacman -Qo /usr/bin/llama-server", "exists": false}` → gate exit 1.
- **K9** delete `host_footprint` → gate exit 1.

**Why this is the right axis.** Calibration is the lowest axis (7): the move converts a prose disclosure into a graded invariant whose failures are named (missing block, non-discriminating probe, inconsistent resolution). It also lifts operability: one canonical, digest-pinned footprint per run replaces hand re-derivation, and the archive finally appears in a structured artifact instead of only `LOG.md`. It harms nothing: no existing check changes, v1 receipts still validate, no write, no host mutation, no province expansion — the probe target is the binary the tool already launches.

**Axes:** calibration +, operability +; no other axis touched.

## 6. Risks

- The gate grades the **recorded** probe string, not the executed command; a dishonest receipt can write `test -e` and run `pacman -Qo`. Only L1's re-run checks truth. State this limit rather than pretending H2 is authenticity.
- Requiring the block makes every future v2 receipt carry four extra read-only calls; all are local and sub-millisecond except the archive hash (~22 MB). If that cost is unwanted, drop `sha256` and keep `bytes`+`mtime`; do not drop the block.
- H3 as written assumes `/usr/bin` is on the tool's PATH. It is here; if a future environment omits it, a real `/usr/bin/llama-server` would be invisible to `path_resolution` while `exists` is true — H3 allows that direction, so no false failure.
- If the operator later installs a pacman `llama-server` at `/usr/bin`, the receipt's old `exists:false` becomes historical; receipts are statements at capture time and must not be retro-validated against the host.
- K8/K9 test the gate, not the tool; they belong in `controls.py` only because that file already owns "run tool, run gate, judge both". Do not add a third runner.
- Scribe's prose draft and this field set must agree; L1 should derive the report paragraph from the receipt, not write both independently.

## 7. Verification (for L1)

1. `python3 tests/llamacpp-live/controls.py --tool <frozen/current tool> --gate <frozen/current gate> --only K0` still accepted; `--only K8` and `--only K9` produce `accepted_bad == 0` with the gate exiting 1.
2. Round-16 v1 receipts still validate unchanged: `check-receipt.py .ufo/waves/round-16/live/receipt.json` and `…/receipt-frozen-probe.json` → exit 0.
3. A fresh real v2 receipt shows `host_footprint.path_resolution == ["/home/vgpnk/.local/bin/llama-server"]`, `usr_bin_llama_server.exists == false`, `retained_asset.bytes == 22240468`, sha256 `753bfa73…e226`, and `removal_owner` naming the operator.
4. After the run, the C1 pin still holds: recompute `matrix_digest()` over `tests/probe-verdicts/*.json` → 9 files, `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32` (recomputed 2026-10-20 before any executor landed).
5. Bounded negative check: `ss -ltnp` shows no listener from these runs; nothing was written outside the temporary receipt path.

## Limitations

- Tsukuroi's corpus was read at 2026-10-15-verified declarations; `PROVINCE.md:70-71` warns sibling declarations can drift, and I re-read the cited lines but did not re-run its census.
- No tsukuroi seat was contacted; §2A/§2B are readings of declarations plus one bounded grep of its gate, not a recipient response.
- The `pacman -Qo` non-discrimination finding is one probe on this host (pacman version unrecorded). It is asserted as observed behaviour, not as a documented pacman contract; [INFERENCE] it generalises to any path not in a package's file list.
- PATH precedence was observed in this shell only.

## Installs

None. No tool was installed or updated; every command used was already present (`ls`, `stat`, `sha256sum`, `command`, `pacman -Qo/-Qq`, `python3`). No pacman transaction ran.
