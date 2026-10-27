# S5Limits — round-53 seat report (carried-limits table)

Verdict: the round-53 build **closes 6** of the 13 C1 limits carried from rounds 50-52 + the round-52 outside closure R2 (libraries-by-path K2Design, btrfs dev mismatch, recorded-URL freshness, and the three round-51/52 image-binding limits held closed), **narrows 2** (host-install memfd / unobserved download — everything executed is now byte-verified against the archive, but provenance is still unobserved, preregistration L0; model-by-path — libraries closed, the model mapping stays path-bound), and **leaves 5** (`vm.memfd_noexec=2`, probe PATH execution, model-bytes-rewritten-after-mapping, kills during download/readiness, pid-join edges, prerelease cliff). Full table with per-row evidence: `.ufo/waves/round-53/w1/out/S5Limits/limits.md`.

Scope: read-only seat. No counter runs of my own were needed — the seat question is answered by reading the carried-limits sections against the frozen round-53 counter, the build receipts, and the wave ablation receipts. Cited receipts are copied into `.ufo/waves/round-53/w1/out/S5Limits/`.

## Evidence (commands, outputs, file:line)

Sources of the limits:

- `sed -n '2891,2901p' SCORECARD.md` — round-50 "### What `met=True` does not show (round-50 wave attacks)" is **empty**; its carried C1 limits live in "Planned (round 51)" item 2 (`SCORECARD.md:2893`): pid-join edges, mapped-file rewrite-after-load indistinguishability, btrfs dev mismatch fail-closed, record-time fetching of the recorded URLs, prerelease cliff.
- `corpus/lessons/round-50-verifier-spotcheck.md:119` (R6) — adds decoy in-place exec (J4Decoy), probe PATH execution (Sen1Env), model bytes rewritten after mapping, counter `--out` parent creation.
- `SCORECARD.md:2917-2924` (round 51) — copy decoy K1Cheat3/J3CopyDecoy; hardlink J4Hardlink (replay refuses, frozen counter does not check); download unobserved; separate dev/inode snapshots / no held descriptor (K1Design3); re-carries probe PATH / model rewrite / kills.
- `SCORECARD.md:3013-3017` (round 52) — host byte-identical memfd meets (J5HostMemfd), `--server`/foreign memfd (K1Cheat); code in `libllama-server-impl.so` + `libggml*` loads by path (K2Design); `vm.memfd_noexec=2`.
- `corpus/lessons/round-52-verifier-spotcheck.md:139-141` (R2) — counter-owned extraction as the next reference; libraries and model by path; download unobserved; memfd_noexec; round-50 carried (probe PATH, model rewrite, kills).

Round-53 build disposition:

- **Libraries-by-path: CLOSED.** Counter reads each executable range from `/proc/<pid>/mem` via `os.pread` and byte-compares to its own archive download (`tools/round53-replay-code-audit.py:393-460`); required names `:103`. Build receipt `measured/c1-build.out` (copied): `bind=1 sealed=1 code=1 teardown=1 newrow=1 ... coderuns=3/3 met=True`, "8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem to the counter's own archive, 13 root-owned host files", listing `libllama-server-impl.so`, `libggml-base.so.0.27.0`, `libggml.so.0.27.0`, `libggml-cpu-zen4.so` among the 8. Ablations (copied): `J2SwapUnchecked/c1-j2.out` (swap after member check, lying `verify_code`) `code=0 ... met=False`, "mapped bytes 7f6b22eb8000-7f6b22ed8000 (offset 00012000) of llama-b11909/libggml-rpc.so differ from the archive member"; `J3ForgedReceipt/c1-forged.out` (forged receipt digests) `code=0`, the memory read catches what the forged receipt claims; `J4OmitLib/c1-omit.out` (live tool omits `libggml-base.so.0.27.0`) `code=0` via the `code_mappings`/`own_code` legs; `J1SwapChecked/c1-swap.out` `bind=0 ... code=0` (replay refused first). Tool side: `tools/kama-live-replay.py:320-367` `verify_code()` refuses `code-mapping:digest / not-a-member / foreign / unopened / no-archive-library`; `tools/kama-llamacpp-live.py:774` `code_mappings()`.
- **Host-memfd / unobserved download: LEFT** (preregistration `limits[0]`: "bytes, not provenance, are compared"). The `code` leg compares only bytes; the invoker is the round-52 one (docstring `:29-32`). J6HostMemfd's seat dir holds only `probe.patch` — no run receipt (see defect D1).
- **Model-by-path: LEFT.** `code` leg filters `x` rows only (`:410`); model stays on the round-50 leg `mapped_model()` stat+sha-by-path (`:307-330`, "bind: the round-50 bind leg, unchanged" `:34`); preregistration `limits[2]` (L2).
- **`vm.memfd_noexec=2`: LEFT** (memfd-exec mechanism unchanged); new counter-side constraint: Yama `ptrace_scope` 0/1 needed for the `code` leg (docstring tail; S507, `corpus/SOURCES.md:260`).
- **Probe PATH execution: LEFT.** `PASS_ENV`/`INVOKER` byte-identical to the round-50 counter (`tools/round53-replay-code-audit.py:111-114` == `tools/round50-replay-bind-audit.py:113-116`).
- **Model rewrite-after-mapping: LEFT** (`mapped_model()` unchanged; preregistration L3). **Kills during download/readiness: LEFT** (`READY_WAIT=600` `:108`, `wait_ready`/`reap` `:528-553`, legs declared unchanged). **Pid-join: LEFT** (`:34`, `replay_pid()` `:538-543`). **Prerelease cliff: LEFT** (b11909 still pinned, `:88-99`).
- **btrfs dev mismatch: CLOSED** for host files — matched by inode + uid 0 + not-writable, dev explicitly not compared (`:431-441`); "13 root-owned host files" in the build receipt.
- **Recorded URLs: CLOSED** — counter fetches the frozen URLs itself ("counter archive: its own download, frozen digest", `measured/c1-build.out`; docstring `:15-20`).
- **Copy decoy / hardlink / snapshot atomicity: CLOSED at round 52, held closed** — `sealed=1 sealedruns=3/3`, `/memfd:llama-server (deleted)` seals 15 (`measured/c1-build.out`); link-count-0 check `sealed_exe` `:462-494`; the round-53 memory read removes the path-vs-inode race class for libraries.

## Defects

**D1 (wave-evidence gap, minor): two preregistered C1 controls have no committed counter-run receipt.**
`grep -rln "LD_PRELOAD\|HostMemfd\|sealed_host" .ufo/waves/round-53/measured/ .ufo/waves/round-53/controls/` → no matches; `ls .ufo/waves/round-53/w1/out/J5Preload/` → only `control.patch`; `ls .ufo/waves/round-53/w1/out/J6HostMemfd/` → only `probe.patch`. The other four C1 ablations (J1-J4) have committed `c1-*.out` receipts with `met=False`; J5 (LD_PRELOAD of a user-owned library — the preregistration's "loads one library from outside the tree" control) and J6 (the host-install memfd probe that demonstrates L0) do not, as of this writing. The C1 kill rule is "any leg 0 at the measured commit, or met=True on any control", so missing control receipts leave the control half of the kill rule unexercised for two named controls. Seats may still be running; this is a point-in-time observation.
Proposed fix (for the L1, not applied — lane is read-only for me): run both controls in a fixture clone of the build (`git clone --shared`, fixture identity, `python3 tools/round53-replay-code-audit.py --repo <clone> --tip <fixture> --scratch $S --out <receipt>`) and commit the two receipts under `.ufo/waves/round-53/w1/out/{J5Preload,J6HostMemfd}/` or the integration controls dir, alongside the existing J1-J4 receipts. Expected: J5 → `code=0` (a user-owned executable mapping outside the unpacked tree fails the root-owned/inode test at `:431-441`); J6 → `met=True` (demonstrating L0: bytes, not provenance).

No counter, preregistration, or lane-file defects found; the frozen counter matches its preregistration sha256 (`1a7a1442…`) as used by the wave seats (e.g. `J2SwapUnchecked/commands.txt`).

## Notes

- No installs or upgrades were needed (no pacman; read-only seat, system Python only).
- No services started; no `llama-server` processes started by me (`pgrep -af llama-server` not needed — none started).
- Scratch `/fast/scratch/hyaku/kama-r53/S5Limits` removed after writing.
