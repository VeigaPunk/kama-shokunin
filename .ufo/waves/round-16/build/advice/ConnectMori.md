# ConnectMori — kama C1/C2 × mori overlap scan (round 16 build wave)

Seat: `KamaR16.ConnectMori`. Read-only; nothing written except this Report. Axes: **operability + calibration**.
Read at 2026-10-20 ~10:2x–10:4x -03. Probe file was under concurrent edit during the read; its hash/line numbers below are a read-time observation, not a stable pin.

## Verdict

There is **no detection overlap on the two objects this round creates** — a transient loopback listener and a transient `llama-server` process. mori has no port/process inventory; its only process probe is the watchdog `pgrep` filter, which the C2 argv does not match. The seam is therefore not a fight over a surface but an **unowned residue question** [INFERENCE]: neither mori, tsukuroi, souji nor kama's own `listeners` census proves that an arbitrary lane-launched process or listener is gone. kama must prove only its own pid/pgid/port, publish the run window as handoff evidence, and must not infer host health from the live run. The one real detection overlap is resource accounting (cgroup/PSI), which is cumulative and non-attributing.

## Evidence — what mori actually observes

1. **mori's Core is six fleet surfaces plus a journal window; none is a listener or process table.**
   `mori-shokunin/PROVINCE.md:22-28` lists `SURFACE watchdog`, `SURFACE waves`, kill/OOM journal classes, the same-boot journal window, resource runway, tmux relevance and lane silence. Quote: “Watchdog liveness — census `SURFACE watchdog`: watchdog pid/start and log freshness” (`PROVINCE.md:22`); “Resource runway — `SURFACE disk` and `SURFACE cgroup`” (`PROVINCE.md:26`). There is no `ss`, socket, port or process-census surface in that list.

2. **mori's process observation is watchdog-scoped and explicitly identity-poor.**
   `PROVINCE.md:48` (FR5): “argv-substring matches do not establish daemon identity.” The only pid row is the watchdog (`PROVINCE.md:22`), and `SKILL.md:38` reads “process alive, last tick stale” as a watchdog judgment. A C2 child argv is `llama-server -m … --alias … --host 127.0.0.1 --port …`, so it does not match the `shokunin-watchdog` filter. [INFERENCE] It is invisible to `SURFACE watchdog`, not misclassified by it.
   The filter's transient false-positive is already measured on mori's side: “a short-lived concurrent process whose command line merely mentions `shokunin-watchdog` can register as `pids≥1`” (`mori-shokunin/corpus/evidence/README.md:55-60`, corroborating read outside the named bound). This is a *name-collision* risk for anything that mentions the daemon, not for C2's argv.

3. **tmux relevance is pane-cwd, not process-tree.**
   `SKILL.md:44`: “pane-cwd classification only; foreign is a relevance fact, never an unhealthy fleet.” Corroboration: `tools/mori-census.sh:46-47` says a session is foreign “even if its process tree works on fleet files.” A C2 child in a fleet tmux pane only moves `session_activity`; in a foreign pane the session is never probed. Neither is a process observation.

4. **Journal kill classes are unit/process-record classes, not an arbitrary-child census.**
   `PROVINCE.md:24`: “unit-process SIGKILL results and unit failures”; `SKILL.md:31`: records are counted by catalog `MESSAGE_ID`, including “`98e32220…` unit-process SIGKILL.” The C2 child is not a systemd unit; [INFERENCE] its SIGTERM/SIGKILL teardown produces no `98e32220` unit record and no `d9b373ed` unit-failure record. A non-unit kernel OOM *record* is FR1 frontier, not a census probe (`PROVINCE.md:44`: “event-time kernel summary/victim token validation … remain frontier”). [INFERENCE] A crash that produces a system coredump would be counted as an unattributed `coredump_notice`, not as the harness.

5. **Resource accounting is the one real overlap, and it cannot attribute the harness.**
   `PROVINCE.md:26` owns “memory PSI/fill/avail, and scope high-watermark”; `SKILL.md:41` says a local threshold can flip the roll (“a local placeholder can flip the roll”). Corroboration: `tools/mori-census.sh:1663-1669` prefers the parent slice's `memory.events.local` and falls back to `user@<uid>.service/memory.events`; `:1800-1805` fires `CGROUP_OOM_KILL crit` only from that local counter, otherwise `CGROUP_OOM_KILL_CUMULATIVE info` with “attribute the event before treating it as fleet evidence.” A C2 child sits in a descendant cgroup; under the default (local readable) path its kill lands in the ancestor/cumulative counter (info), not the parent-slice local counter (crit), and only the fallback service-file read would cover it. `memory.current`/`memory.peak`/PSI still include it. The C2 model is 1,185,376 bytes (host fact report `ScoutHostRuntimeFacts.md`: 1.12 MiB, 22 GiB available), so a resource alarm is implausible [INFERENCE], but the counters carry no per-process attribution: a census during/after the run cannot say the harness caused a delta.

6. **The r16 journal window is cursor-anchored, not a wall-clock join.**
   `PROVINCE.md:25`: “The first record must match the anchor cursor and boot exactly.” A C2 receipt's `started`/`ended` UTC is not a `mori-journal-anchor-v1` cursor. [INFERENCE] mori's window probe cannot consume the receipt automatically; the handoff is evidence for a human/operator query, not a machine join. FR11 remains frontier (`PROVINCE.md:51`).

## Evidence — what kama owns and what C2 creates

7. **kama owns serving-port discovery and endpoint liveness, not a process census.**
   `kama-shokunin/PROVINCE.md:10`: `listeners` does “`ss -ltn` loopback enumeration + per-listener classification”; “kama governs discovering whatever serves these ports and never claims an installed server.” `PROVINCE.md:13` owns “liveness/readiness probe conventions.” The ephemeral unregistered port is therefore inside kama's *discovery* surface but is not a producer to be registered.

8. **The live run must not be read as producer restoration.**
   `kama-shokunin/PROVINCE.md:21-22`: “reports pin correctness and serving liveness separately and never asserts `MODEL_OK` from retired samples.” The registry rows for 8080/34113 remain `DEAD`; C2 deliberately serves an unregistered port. The C2 report must say the registered consumer endpoints remain unserved.

9. **The boundary is symmetric.**
   `mori-shokunin/PROVINCE.md:67`: “mori does not infer serving health from host/resource signals.” The converse also holds from kama's own rule: `kama-shokunin/PROVINCE.md:51`: “Out of province → report, never absorb.” A live `MODEL_OK` at an ephemeral port says nothing about host memory, kills or fleet liveness.

10. **The residue question has no owner.**
    mori: no process/port surface (`PROVINCE.md:22-28`). tsukuroi: OS/systemd units (`mori PROVINCE.md:12-14`), and the C2 child is not a unit. souji: “Owns artifact cleanup, not process/fleet health” (`mori PROVINCE.md:69`). kama: `listeners` is a serving-endpoint classification, not a process inventory, and the harness port is unregistered. So a leaked non-listening child or a stray listener from a lane harness would be invisible to every current census surface [INFERENCE]. This is a **gap to report, not a surface for kama to absorb**.

11. **C2's specified teardown proof is direct-child + port only.**
    `build/spec.json:59` (LiveHarness): “prove process exited (returncode) and port refuses connections.” `spec.json:64` (LiveReceiptGate) requires “checks ids … `teardown_exited`, `teardown_port_closed`.” Neither proves the **process group** is gone. Because the launch uses `start_new_session=True`, the child is a group leader; a group-scoped absence probe is available and cheap.

12. **The C1 matrix already binds its verdicts to the probe bytes; C2 does not.**
    `spec.json:14` (VerdictHarness output): `{"schema":"kama-probe-verdicts/v1","probe":path,"probe_sha256":hex,...}`. The LiveHarness spec records the server's `realpath` and `sha256` but only names `--probe PATH` without a digest (`spec.json:59`). At read time the frozen before probe was `93ee4302…cd64` and the live `tools/kama-probe.sh` was `d0d48d8d…` with `MODEL_LOADING` already in `VOCAB` (`tools/kama-probe.sh:60`), `C_VERDICT=MODEL_LOADING`/`llamacpp-loading` (`:502-503`) and the old `non-2xx-non-model-http` fallback pushed to `:562` (frozen `:521`). [INFERENCE] A C2 receipt without a probe digest cannot say which probe semantics produced its `probe_model_ok`/`probe_mismatch` claims.

## Contested scope

| Question | Owner | Ruling for this wave |
|---|---|---|
| Is the thing at this baseURL the configured model, right now? | kama (`PROVINCE.md:42-43`) | `MODEL_LOADING` stays a kama endpoint verdict; mori must not grade it as fleet health. |
| Is the ephemeral harness process/listener gone? | **unowned** | kama proves only its own pgid + port; the residual fleet question is handed up, not absorbed into `listeners`/`check`. |
| Did the live run stress memory or get something killed? | mori (resource/kill classes) and tsukuroi (OS) | kama reports the child's exit/returncode only; it does not attribute cgroup/PSI/coredump/journalevents. |
| Is a registered consumer port alive? | kama (`PROVINCE.md:10,21-22`) | C2's unregistered port changes nothing; 8080/34113 remain `DEAD`. |
| Is a service/unit enabled/healthy? | tsukuroi | kama writes no unit; the harness is an ephemeral child (`PROVINCE.md:45-48`). |
| Is the model any good? | kengaku (`PROVINCE.md:40`) | C2 is a lifecycle/identity check, not an eval. |

The only genuine seam is the **word “liveness”** [INFERENCE]: mori grades fleet liveness (`PROVINCE.md:22`), kama grades endpoint liveness (`PROVINCE.md:13`). A live endpoint is not a live fleet, and a live fleet is not a live endpoint.

## What kama must hand off rather than absorb

- **Kill/OOM/coredump/PSI cause and attribution** → mori (and tsukuroi for unit/OS state). C2 may report `returncode`, `teardown_exited`, `teardown_port_closed`; it may not say “the host/OOM/cgroup killed it” or “the host is healthy.”
- **Service restoration / unit state** → tsukuroi/operator (`kama PROVINCE.md:24-28,45-48`).
- **Model quality** → kengaku (`PROVINCE.md:40`).
- **Fleet-wide residue detection** → no owner; the C2 report should name the gap and the run window so an operator or a future mori surface can correlate it. Do not add a process/listener surface to kama to close it.
- **Endpoint health** → kama; mori must not infer a serving state from resource or host signals (`mori PROVINCE.md:67`).

Also keep the C1/C2 vocabularies distinct: mori's `unavailable` means “could not observe” (`SKILL.md:152`: “A missing surface is reported as `unavailable`, never as unhealthy”), while llama.cpp's `unavailable_error` is a serving state. `MODEL_LOADING` is an *observed* state, not mori's `unavailable`, not `DEAD`, and not `FOREIGN_SERVICE`. Likewise C2's `loading_observed=not-observed` is not evidence that llama.cpp never answers 503 (QUALITY #34/#36).

## Reusable conventions (mori → kama)

| Convention | mori source | Application to C1/C2 |
|---|---|---|
| Pre-registered expected gradient against a frozen gate SHA | `corpus/QUALITY.md:25-26` “a pre-registered expected gradient: exact tally and PASS set against the frozen gate SHA” | C1's frozen-before/red + repaired/green + positive controls; do not run the matrix before the freeze and call it a before/after. |
| Hash every verdict-driving input at load and end | `QUALITY.md:78` “A gate receipt must hash each declared input at load and at end” | Add `probe.sha256` to the C2 receipt (the C1 harness already emits `probe_sha256`, `spec.json:14`); compare the two at integration. |
| Label fixture vs live | `QUALITY.md:91` “A nonzero positive vector is labelled by its source”; “a fixture vector is never reported as live positive load” | The C1 stub matrix is a fixture-family result; C2 is one live observation. L1's scorecard must not merge them, and `loading_observed=not-observed` must stay a non-result. |
| “Unavailable” is not “zero” and not “unhealthy” | `SKILL.md:152`; `QUALITY.md:82` “a valid empty capture is a positive 0 … never evidence that no event occurred” | An unparsable/missing 503 body keeps its existing verdict; `MODEL_LOADING` requires the exact triple; `not-observed` is not a negative claim. |
| A written selftest is not permission to run it | `QUALITY.md:100-101` “Writing a selftest … is not permission to run it” | Writers of the matrix files, `check.py`, `kama-llamacpp-live.py` and `check-receipt.py` must mark their dev runs “not measurements”; L1 measures once. |
| Sweep the registry row when the gate/source changes | `QUALITY.md:102-103` “A registry row is swept whenever its gate, selftest, or source changes” | The new verdict changes `VOCAB`, `listeners` summary (`tools/kama-probe.sh:731`), snapshot whitelist (`:937`) and the lane's gate description; the row must be swept after the probe lands. |
| A baseline's volatile set is declared; a re-pin is recorded | `QUALITY.md:19-20` “A baseline declares its volatile field set, derivation window, host and gate SHA” | `latest.tsv`/DELTA must accept a `MODEL_LOADING` row rather than drop it as malformed; a re-pin needs a reason, not a green. |
| A green fixture never establishes drift freshness | `QUALITY.md:104` “A green fixture or sibling gate never establishes drift freshness” | C2's live receipt is not a re-pin of kama's drift baseline and does not change the DEAD registry verdicts. |

## Proposed move (one bounded amendment)

**Make the C2 live receipt self-verifying for the two things no fleet census can see: the exact probe bytes it ran, and the process group it killed.** This is one additive amendment to `kama-llamacpp-live/v1`, not a new surface:

1. **Probe identity (calibration).** In `tools/kama-llamacpp-live.py`, capture `sha256` of the `--probe` path before the first probe invocation and emit `probe: {path, sha256}`. Add `--expect-probe-sha256 HEX` to `tests/llamacpp-live/check-receipt.py` so L1 can assert the receipt's probe bytes equal the repaired probe measured by the C1 matrix (the `probe_sha256` that `check.py` emits; `spec.json:14`). If they differ, the live receipt does not support the matrix's C1 claim; rerun or record both hashes explicitly.
2. **Group-scoped teardown (operability).** Record `child_pid` and `pgid` at launch. After SIGTERM/SIGKILL and the wait, assert `os.killpg(pgid, 0)` raises `ProcessLookupError`; fold this into the existing `teardown_exited.observed` as `pgid_absent=true` (no new required check id, so the receipt gate's nine-id list is unchanged). Label `teardown_scope=own-process-group`.
3. **Handoff block (contract).** Emit `fleet_handoff: {started, ended, port, pgid, scope: "own-process-group-only", host_claims: "none"}`; L1's C2 report states that (a) no mori surface observes this process/listener, (b) any journal/cgroup/coredump/PSI evidence overlapping the window is mori/tsukuroi evidence to attribute, not harness success, and (c) registered consumer ports remain unserved.

**Why this is the right move:** C1's matrix already binds `probe_sha256` to its verdicts; C2's live receipt currently binds only server/model. The wave edits the probe, so an unbound live receipt is a calibration hole. The residue question is the one seam the mori scan exposes; a group-scoped proof is the only cheap, self-contained way to claim teardown without inventing a fleet surface. It improves both assigned axes and harms neither: one hash, one `killpg` probe, no new file, port, service, or write outside the existing temp/out paths.

## Risks

- **pgid observation is not “no residue.”** `killpg(pgid, 0)` proves the *launched* group is gone; a descendant that escaped via `setsid` would not be caught (the port check may catch a listener, not a silent orphan). The receipt must say `scope=own-process-group`, never “host clean.”  [INFERENCE] llama-server does not daemonize by default, so the risk is theoretical for b11755.
- **Conservative false-fail.** A recycled pgid or an unreaped zombie grandchild can make the check fail or pass oddly; a failure is the safe direction (the run fails rather than overclaims). Do not retry the check to green.
- **Gate compatibility.** If `check-receipt.py` rejects unknown identity keys or extra observed fields, the probe/handoff fields must be accepted as additive before use. If not, L1 should keep the receipt unchanged and put the probe hash in the L1 run record; the claim then remains reproducible but not self-contained. [INFERENCE] The current gate prompt requires each of nine ids “exactly once and passed” (`spec.json:64`) and does not forbid extras.
- **Moving probe.** `tools/kama-probe.sh` is under concurrent edit; hash at launch, compare to the matrix run's hash, and never cite a probe hash without the time it was taken.
- **Live-state rarity.** The tiny model can load fast enough that `loading_observed=not-observed` [INFERENCE]; that is not evidence against the C1 envelope. The stub matrix is the deterministic calibration; the live run is one observation (QUALITY #34/#36).
- **Resource counters are cumulative.** A mori census after the run cannot date or attribute the harness's memory contribution; do not use `CGROUP_OOM_KILL*`, `memory.peak` or PSI as teardown evidence.

## Verification for L1 (not run by this seat)

1. After `LiveHarness` and `LiveReceiptGate` land: one live run with the pinned model digest; `check-receipt.py RECEIPT --expect-model-sha256 … --expect-server-sha256 … --expect-probe-sha256 "$(sha256sum tools/kama-probe.sh | cut -d' ' -f1)"` → exit 0.
2. Assert `receipt.probe.sha256` equals the repaired probe's `probe_sha256` in the C1 matrix run output; if not, the live receipt cannot be used as evidence for the C1 claim.
3. Assert `receipt.pgid` is present, `teardown_exited.passed=true` with `pgid_absent=true`, and `.port` is neither 8080 nor 34113; then independently `ss -ltn` after the run shows no listener on `.port`.
4. Run the C1 matrix: frozen before red, repaired green; positive controls (`LoadingEnvelope`/`LoadingRace`) pass; `probe_mismatch` is `MODEL_MISMATCH served-id-mismatch` exit 2.
5. Do not run the mori census as part of C2; if a fleet observation is wanted, it is a separate read-only run, and its resource rows must not be read as harness attribution.

## Limitations and installs

- Read-only seat: no probe, harness, census, gate or stub server was run; the two `sha256sum` calls were for evidence only.
- `tools/kama-llamacpp-live.py` did not exist at read time (`ls tools/`, 10:2x); this advice is forward-looking and does not review an implementation.
- Mori inputs were bounded to `SKILL.md`, `PROVINCE.md` and `corpus/QUALITY.md`; `tools/mori-census.sh`, `corpus/knowledge/observability-surfaces-r2.md` and `corpus/evidence/README.md` were read only to corroborate mechanism, and are marked as corroborating reads.
- The probe file was concurrently edited; current line numbers (`:60`, `:502-503`, `:562`, `:731`, `:937`) and hash `d0d48d8d…` are read-time observations, not pins. The frozen before hash `93ee4302…cd64` matches the frozen snapshot.
- No installs, upgrades, service changes, or port bindings.
