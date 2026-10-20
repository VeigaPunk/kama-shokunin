VERDICT: confirm — the delivered producer, gate and both counters hold loopback-only argv, refuse 8080/34113/registry ports before any socket, and leave no seat-owned listener in the recorded runs; only narrow forward-looking residuals remain, none of which weakens a recorded claim.

# PortsFootprint — loopback, registered-port refusal, cleanup, installs

Seat `KamaR18.PortsFootprint`, round-18 FALSIFY. Read-only against lane tip
`1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; every executed command ran in my clone
`/tmp/kama-r18-falsify-PortsFootprint/clone` (`git rev-parse HEAD` =
`1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, `git status --porcelain` empty) and scratch
`/tmp/kama-r18-falsify-PortsFootprint`. No lane write except this report. `ss` was read
only. No service, unit, global config or installed artifact was changed.

Clone command (exact):
`git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-PortsFootprint/clone`
then `git -C ... switch -q -c seat/PortsFootprint 1c325b2e58fcfdc6761f645b44cedfb1d65243e6`.

## 1. Loopback binding — observed

`tools/kama-llamacpp-live.py` has no `--host` CLI (argparse lines 1008–1029); the launch
argv hardcodes `--host 127.0.0.1` at `tools/kama-llamacpp-live.py:1244`, and the probe
argv/URL are `127.0.0.1` (`:742`, `:423`, ready captures via `http.client` at `:507-508`).
All three official receipts agree:

| receipt | port | argv `--host` | argv `--port` | server log line | outcome |
|---|---|---|---|---|---|
| `live/receipt-1.json` | 33769 | 127.0.0.1 | 33769 | `listening on http://127.0.0.1:33769` | pass |
| `live/receipt-2.json` | 44109 | 127.0.0.1 | 44109 | `listening on http://127.0.0.1:44109` | pass |
| `live/receipt-3.json` | 45359 | 127.0.0.1 | 45359 | `listening on http://127.0.0.1:45359` | pass |

Gate verdicts: `runs/live-gate-{1,2,3}.stdout` each `VALID <receipt>` (exit files 0).
The v3 gate re-derives the whole argv list and rejects any mismatch
(`tests/llamacpp-live/check-receipt.py:481-486` host/port, `:495-515` exact-list equality),
so a wildcard or duplicate `--host` cannot be laundered into a VALID receipt. This is the
closure for `ProbeArgvEffects.md:66-90` (b11755 last-duplicate-wins binds `0.0.0.0`).

Ownership is loopback-only and fail-closed: `_listen_inodes` counts a LISTEN row only when
the address is loopback and explicitly does not count wildcard rows
(`tools/kama-llamacpp-live.py:348-367`, docstring `:354`); `port_owned_by` then matches the
socket inode against the child's fd table (`:370-388`); `verify_live` turns anything but
`child` into a setup error (`:654-668`, called pre-captures/pre-probe/post-probe at
`:1314`, `:1368-1369`, `:1375`). tcp6 rows are decoded by reversing each host-endian word and
accept **only** exact `::1` or `::ffff:127/8` (`:311-325`); the selftest exercises four
synthetic rows plus two real IPv6 listens (`:1035-1091`, exact bound forms `::1` and
`::ffff:127.0.0.1`, exit line 1104 `selftest: ok; closed tcp6 listeners ...`).

Other scripts in the assigned set bind loopback only:
`tests/llamacpp-live/controls.py:270` (`127.0.0.1`), `:404` (`::ffff:127.0.0.1`, dual
stack), `:406` (`127.0.0.1`), and its header states every fake binds only those
(`:147-149`); `tools/test-snapshot.sh:64` (`127.0.0.1:0`, trap cleanup `:19-24`, explicit
kill `:135-136`); `tests/probe-verdicts/check.py:456` (`127.0.0.1:0`, `shutdown()`/
`server_close()` at `:508-509`). `tools/kama-probe.sh` reads listeners with
`ss -ltnpH` only (`:246`) and its HTTP client is `curl --noproxy '*'` to the `--port` it
is given (`:294`); the lifecycle tool never invokes the probe's `listeners` subcommand —
only `check` (`tools/kama-llamacpp-live.py:742`, sole call site `:1374`).

## 2. Registered-port refusal — observed, plus one executed experiment

Producer: `HARD_REFUSED_PORTS = {8080, 34113}` (`tools/kama-llamacpp-live.py:68`);
`refused_ports()` adds every port token the registry TSV expresses
(`:246-268`, patterns `:255-264`); `pick_port` raises `port-refused-registered:<p>`
**before** any connect or bind on the explicit path (`:289-292`), and the bind(:0) path
retries until the offered port is outside the set (`:302-311`, 64 attempts). The frozen
round-17 tool carries the same set and function
(`.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:68,246,275`), so the measure's
"before" arm is not a gap either.

Executed (clone, no server launch, no listener): extracted set and refusal calls
```
refused count= 2 sorted sample= [8080, 34113]
8080 SetupError: port-refused-registered:8080
34113 SetupError: port-refused-registered:34113
picked [43733,45759,...] any refused: False
```
and the CLI refusal path end-to-end with a scratch copy of `/bin/true` as `--server` and a
20-byte model (scratch `/tmp/kama-r18-falsify-PortsFootprint/refusal`, nothing launched):
```
--port 8080  -> exit 2, receipt setup_error=port-refused-registered:8080,
                port=None argv=None child_pid=None teardown=None outcome=setup-error
--port 34113 -> exit 2, receipt setup_error=port-refused-registered:34113,
                port=None argv=None child_pid=None teardown=None outcome=setup-error
```
`ss -ltnH` before/after both invocations: no new LISTEN row (diff showed one preexisting
`127.0.0.1:60201` row present before and absent after — not created by these commands;
the refusal path opens no socket). This is the only runtime experiment I ran.

Gate side: `port_refusal_set` must be non-empty, sorted, duplicate-free, in range, contain
both hard pins; `port` must not be a hard pin and must not be inside the receipt's own
refusal set (`tests/llamacpp-live/check-receipt.py:312-339`; `HARD_PINS` `:49`). Mutants
`port-34113` and `port-inside-refusal-set` are among the 61 rejected in
`runs/gate-selftest.stdout` ("5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations +
unreadable case rejected"). The controls suite stages the full registry copy and refuses to
run on an unreadable/empty one (`controls.py:828-835`), and every fake receives the port the
tool already chose, so no control can bind 8080/34113.

## 3. Cleanup — observed

Producer teardown (`tools/kama-llamacpp-live.py:798-850`): SIGTERM to the process group only
when the child is freshly alive (`:807`, F5); SIGKILL after `TERM_GRACE` only after a
re-check; `port_refuses` re-derived (`:831`); temp log reduced and unlinked in `finally`
(`:846-852`). On a fault *inside* teardown, the `finally` handler records the fault and
still SIGKILLs a live child and re-checks the port (`:1401-1452`), so a BaseException cannot
skip the kill path. `pdeathsig` is requested in the child but honestly recorded
`prctl_ok: "unknown"` (`:391-404`; receipts show `"requested": true`).

All three receipts: `alive_at_teardown_start=true`, `sigterm_sent=true`,
`sigkill_sent=false`, `returncode=0`, `port_refuses=true`,
`port_listener_ownership="child"`, `internal_fault=null`, `setup_error=null`. Their
`log_path` files (`/tmp/kama-llamacpp-live-thvgxiao.log`, `-s9c951vr.log`,
`-qjjagq8y.log`) are absent now, i.e. the in-run unlink executed.

Retained controls that target this area, from `runs/c1-measure.json` per-control rows:
- `k3` rejected-targeted on `["teardown_graceful","teardown_port_closed"]`;
- `k4`/`k5`/`k8` rejected-targeted on `teardown_graceful` (SIGTERM ignored / exit 1 /
  default disposition);
- `k6` rejected-targeted on `teardown_graceful` + `RuntimeError` (teardown fault);
- `k15` rejected-targeted on `teardown_port_closed` (helper keeps the listener after the
  server's exit 0 — the exact cleanup predicate);
- `k18` rejected-targeted on `teardown_graceful` + `KeyboardInterrupt`;
- `k17` `after: accepted`, `before: rejected-targeted` on
  `["teardown_graceful","teardown_port_closed","loading_envelope_graded"]` with target
  `["ownership"]` — the IPv6/mapped-ownership fix takes effect while the frozen tool
  cannot prove it.
Both measure arms record `leaked_processes: []` and `warnings: []`; `reap_scratch` scans
`/proc/*/cmdline` for the scratch root and killpg's a self-led group
(`.ufo/waves/round-18/c1/measure.py:250-302`, used at `:336`, `:824-826`, `:1025`,
final `:1588`).

C2 has the stronger residue audit: generated sitecustomize refuses non-loopback binds,
refuses protected ports, and remaps port 0 into 49152–60999
(`.ufo/waves/round-18/c2/survivors.py:495-562`, install `:562`, protected set `:180`/`:466-470`);
`runs/c2-survivors.json` reports `bind_guard.summary`: `binds 1464`, `distinct_ports 1385`,
`min_port 49152`, `max_port 60993`, `protected_hits []`,
`listening_after {"command":"ss -ltnpH","exit":0,"owned":[]}`; `teardown`
`{"scratch_removed": true, "marked_stragglers_killed": []}`. The guard is Python-only and
that limit is stated (`:113-118`); the actual c2 children are Python.

Current host state (read-only, after all my commands): 27 LISTEN rows at the snapshot
(sibling falsify seats add/remove their own loopback rows continuously, so a re-run will
differ in count), none on 8080 or 34113 (`ss -ltnH | grep -E ':(8080|34113)\b'` → `NO 8080/34113 LISTENERS`), no
`llama-server` process (`pgrep -af 'llama-server|llama-refusal'` empty), no process naming
my scratch root.

One preexisting residue found, unrelated to listeners: four `/tmp/kama-llamacpp-live-*.log`
files — `43ko5kam.log` 0 B 12:46, `ijt9laux.log` 0 B 12:49, `rx9qd1uu.log` 1073 B 18:01,
`xeo3pbbg.log` 1073 B 18:01 (times local -03). The tool's unlink runs on normal and fault
paths; these are consistent with harness processes killed externally (the two 18:01 files
fall inside the build window, 21:01Z). No process or socket corresponds to them.

## 4. Installs / retained artifacts — disclosed

No install or update by this seat or by the round-18 official run. Evidence:
- The 32 `runs/commands.json` argvs (window `2026-10-20T22:34:56Z`–`22:40:05Z`) contain no
  `pacman`, `uv`, `pip`, `npm`, `cargo`, `curl`, `wget`, `systemctl` or `install` token
  (`grep` over the JSON returned only header keys/no match).
- None of the assigned scripts invokes a package manager, service manager or downloader;
  the only fetch-like code is the probe's `curl` against the caller's loopback port.
- Build-wave advice records "no tools installed or updated" (`build/advice/C1LiveTool.md:29,37`,
  `C1Gate.md:29`, `C1Measure.md:38`, `C2AppendOnly.md:89`, `C2Provenance.md:19`,
  `C2Survivors.md:12`, `MutBaselineControls.md:264`, `MutBaselineDetectors.md:349`,
  `MutBaselineH.md:231`) and the host-wide pacman pause being respected
  (`build/advice/ConnectTsukuroi.md:23-41,74`).

Retained preexisting artifacts, read-only, hashes re-derived now:
| artifact | bytes | sha256 | mtime (-03) |
|---|---|---|---|
| `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` | 22,240,468 | `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226` | 2026-10-20 10:17:48 |
| `~/.local/opt/llama-b11755/llama-server` | 17,864 | `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` | 2026-10-20 08:10:36 |
| `~/.cache/kama-shokunin/models/stories260K.gguf` | 1,185,376 | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` | 2026-10-20 10:17:54 |

These match the official pins (`runs/commands.json:12-17` and every `live-gate` pin) and the
model digest re-hashed equals the receipt pre/post digest, so the runs used these bytes.
Install disclosure and archive disposition are on record in the L0 queue, not invented here:
`.ufo/l0-questions.md:58` (round-16: installed b11755 under the tooling directive, linked
`~/.local/bin/llama-server`, pinned 1.2 MB CI GGUF) and `:68` (round-17: include the
22,240,468-byte archive `753bfa73…e226` in the keep-or-remove ruling). Keep-or-remove remains
operator-pending; no round-18 file deletes or re-installs either artifact.

Other observed download, not attributable to round 18 and not referenced by any round-18
command: `~/.local/opt/dl/wabt-1.0.42-linux-x64.tar.gz` (4,761,911 B, mtime 17:31 -03 =
20:31Z, ~28 min before build dispatch). `/etc/llama.cpp` does not exist. Per contract I did
not read `~/.config`, so the user-level llama.cpp config file's presence is
could-not-evaluate.

Wildcard exposure note: `build/advice/ProbeArgvEffects.md:66-90` records a deliberate
`--host 0.0.0.0` host-netns listener seen for 14.2 ms, killed with SIGKILL, `ss` empty
afterwards, no HTTP sent; the lesson records it as unnecessary exposure
(`corpus/lessons/round-18.md` "Execution conformance disclosures"). The current tool cannot
grade that state as a pass: a wildcard row is not a loopback inode (`:348-367`), so
`verify_live` returns `port-listener-ownership-unproven` (`:654-668`). My current `ss`
snapshot shows no residue, but I cannot retrospectively prove the build-wave history beyond
that disclosed report.

## 5. Residual limits (visible; none is a kill)

R1. `teardown_port_closed`'s `port_refuses` is IPv4-loopback only:
`_port_refuses` connects to `('127.0.0.1', port)` (`tools/kama-llamacpp-live.py:786-795`).
A lingering tcp6 listener on the same numeric port would not be seen by that claim. The
producer's argv forces `--host 127.0.0.1`, and pre-teardown ownership reads tcp6 and treats
wildcard as unproven, so the tool's own child cannot produce that state; the check's
documentation says only "refuses connections after teardown" (`:130-135`), so no recorded
statement is false. Forward-looking narrowing only.

R2. The gate's registered-port block is hard pins + the receipt's self-declared
`port_refusal_set` (`check-receipt.py:312-339`), not re-derived from
`registry/endpoint-consumers.tsv`. Today `refused_ports()` on the committed registry returns
exactly `{8080, 34113}` (executed), so producer and gate agree. If the registry gains a port
in a format the producer's six regexes miss, or a third port, a forged receipt that omits it
could pass this block. No present gap.

R3. Four leftover `/tmp/kama-llamacpp-live-*.log` files (§3). Not listeners; owner
undetermined; consistent with externally killed harness runs. The tool unlinks in `finally`
and twice retries (`:1527-1536`).

R4. Harness-SIGKILL cleanup rests on best-effort `PR_SET_PDEATHSIG`, recorded as
`prctl_ok: "unknown"` (`:391-404`). k6/k18 exercise in-process faults; no retained control
SIGKILLs the real server's harness and proves the child dies. The claim as written is about
recorded teardown, not this path, and does not overstate it.

R5. C1's residue proof is the `/proc` cmdline scan (`measure.py:250-302`,
`leaked_processes: []`), not an `ss` audit; C2 adds the `ss -ltnpH` audit (`owned: []`).
Asymmetry in instrument strength, not a defect in the evidence used (c1 fakes' argv always
names the scratch root).

R6. `HOME` is in the child env allowlist (`:84`), so upstream's
`${XDG_CONFIG_HOME:-~/.config}/llama.cpp/config.ini` channel is reachable
(`build/advice/ScoutLlamaArgParse.md:15`). CLI wins over INI, so `--host`/`--port` cannot be
overridden, and `/etc/llama.cpp` is absent; non-argv options (e.g. api-key, ssl) could still
change and would fail the tool's checks closed, and the receipt would not show it because
`LOG_KEEP` (`:77`) drops `using config file:`. No loopback/registered-port impact. User
config existence not checked (contract).

## Limits and remaining unknowns

- I ran no real-server lifecycle (that experiment was not assigned to this seat); my runtime
  evidence is the two refusal invocations plus receipt/JSON re-derivation and one host `ss`
  snapshot.
- The c1 count remains could-not-evaluate at top level on the measured commit
  (`runs/c1-measure.json` exit 2, fault `"before: misclassified=1 but 0 row(s) classified
  misclassified"`); its per-control rows are the raw evidence quoted here, not a passing
  arm. That counter defect belongs to its owner, not this audit.
- Ownership of the four leftover `/tmp` logs and any build-wave listener history beyond the
  disclosed 14.2 ms wildcard run are unresolved; neither affects current host state
  (no 8080/34113 listener, no llama-server process at end of audit).
- Temporary scratch `/tmp/kama-r18-falsify-PortsFootprint` (clone, refusal receipts,
  `ss` snapshots) was removed after this report was written; the clone was never modified
  or committed.
