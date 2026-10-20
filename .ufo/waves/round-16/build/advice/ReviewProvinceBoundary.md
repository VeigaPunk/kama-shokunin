# Review — province write boundary for the lane-owned live fixture

Round 16 (hyaku phase 2), build wave. Seat: `KamaR16.ReviewProvinceBoundary`.
Read-only review of PROVINCE.md and QUALITY.md KQ5 against claim C2
(`tools/kama-llamacpp-live.py`). Reviewed as **design**, not delivered code:
the owned file is absent at 2026-10-20T10:29:27-03:00; the design text is
`.ufo/waves/round-16/build/spec.json:59` (item `LiveHarness`).

## Verdict

**Yes — the ephemeral, lane-owned `llama-server` on an unregistered loopback port
stays inside the province write boundary, and no L0 ruling is required for it as
designed.** It writes none of the three enumerated operator surfaces, invokes no
service control, and its only persistent host artifacts are the toolchain install
explicitly named by the standing operator tooling directive and a lane-named cache.
An **append-only PROVINCE note is required**, but to *record classification and
narrow authority*, not to grant permission: without it, existing sentences
read as contradicted by C2.

Two conditions decide the verdict; if either is dropped, L0 is the honest route:

1. Declare `~/.cache/kama-shokunin/models/` lane-owned (it is the only host write
   not named by the operator directive).
2. Carry the narrowing sentence for round-1's "endpoint outside the registry" rule
   (`corpus/lessons/round-1-safety.md:88-90`). The append below narrows lane
   probing authority; it never widens it.

## Boundary accounting

| Action | Enumerated boundary? | Disposition | Evidence |
|---|---|---|---|
| `~/.config` write | yes, forbidden | not written | `PROVINCE.md:45-49` "kama never writes to `~/.config`, `~/.omp`, or systemd units"; C2 design has no such path, and a bounded name scan (`find ~/.config -maxdepth 4 \( -iname '*llama*' -o -iname '*kama*' \)`) found none (2026-10-20) |
| `~/.omp` write | yes, forbidden | not written | same boundary sentence; the C2 design has no `~/.omp` path |
| systemd unit/service write | yes, forbidden | not written; plain child process | `PROVINCE.md:45-49`; design launches with `start_new_session=True`, no unit (`.ufo/waves/round-16/build/spec.json:59`); `systemctl --user list-unit-files 'llama*' 'qwen*'` → no rows |
| `~/.local/opt/llama-b11755/`, `~/.local/bin/llama-server` | not enumerated | operator-authorized toolchain install | `.omp/agent/RULES.md:7-8` "official release binary into `~/.local/bin`"; verified symlink, no pacman owner |
| `~/.cache/kama-shokunin/models/` | not enumerated | lane-owned cache | `stories260K.gguf` sha256 `270cba1b…256d` matches the claim (full read) |
| `/tmp` run log | not enumerated | round-1-sanctioned scratch | `corpus/lessons/round-1-safety.md:35-36` "only permitted scratch side effect is temporary files under `/tmp`, with cleanup" |
| ephemeral loopback listener | not a write | fixture, not a service; unregistered port | design binds `127.0.0.1:0`; observed `net.ipv4.ip_local_port_range = 32768 60999`, disjoint from 8080/34113 |
| receipt at `--out` | lane artifact | measurement artifact only | design writes receipt to `--out` or stdout; no `registry/history` write |

The loaded invariant that keeps the province's own observed state true:
`PROVINCE.md:24-28` says "Serving runtime is explicitly unavailable on the concrete
surfaces" and "restoring a unit is operator-owned work under the boundary below."
A kernel-assigned ephemeral port keeps "nothing listens on `8080` or `34113`"
(`PROVINCE.md:25`) literally true before, during and after a run, and restores no
unit. Verified at 10:29:27-03:00: no `llama-server` process, no listener on 8080/34113.

## Findings by severity

### Medium — M1: the persistent install collides with "never claims an installed server"

`PROVINCE.md:10` — "kama governs discovering whatever serves these ports and never
claims an installed server". C2 leaves a persistent, PATH-resolvable llama.cpp binary
(`~/.local/bin/llama-server` → `~/.local/opt/llama-b11755/llama-server`). Without an
explicit classification, a later reader can cite that artifact as an installed serving
producer, or read C2 as the "restoring a unit" work reserved to the operator
(`PROVINCE.md:27-28` — "restoring a unit is operator-owned work under the boundary
below"). The append must call it a lane toolchain artifact and forbid registry,
listener-census and observed-state citation. The installed binary is not a package
dependency: `pacman -Qo ~/.local/bin/llama-server` → "No package owns".

### Medium — M2: `~/.cache/kama-shokunin` is the one host write with no named authorization

Round 1 allowed the lane's scratch only under `/tmp`: "only permitted scratch side
effect is temporary files under `/tmp`, with cleanup"
(`corpus/lessons/round-1-safety.md:35-36`). The operator directive names only the
binary channel — "official release binary into `~/.local/bin`"
(`.omp/agent/RULES.md:7-8`) — and does not name model/data downloads. The GGUF is
1,185,376 bytes, digest-pinned, and the directory is lane-scoped, so this is a
declaration gap, not an unsafe write. Either declare `~/.cache/kama-shokunin/` in the
append (preferred; it survives operator cleanup of `/tmp`) or relocate the fixture
model under `/tmp`/the lane repo. Do not let it stay unnamed.

### Medium — M3: round-1 routes "any endpoint outside the registry" to L0; the append must scope it by narrowing

`corpus/lessons/round-1-safety.md:88-90` — "L0 must approve any endpoint outside the
declared local model registry." The fixture port is such an endpoint by construction.
The safety predicate behind that rule is met and verifiable: the endpoint is authored
by the same tool that probes it; the probe is GET-only; and `check --port` evaluates
exactly one row and does not read the registry at all — `read_registry "$OPT_REGISTRY"`
appears only in the non-port branch (`tools/kama-probe.sh:837-853`). The append below
therefore *narrows* authority ("only the server this tool started") and leaves L0
routing in force for foreign endpoints. If L1 instead writes a note that claims the
fixture is authorized absent L0 without that narrowing sentence, the note is
self-granted expansion and should be rejected.

### Low — L1: `start_new_session=True` makes an unhandled harness death leave a serving child

Design: `start_new_session=True` and "Always tear down (try/finally, signal handlers)"
(`.ufo/waves/round-16/build/spec.json:59`). `try/finally` and signal handlers do not
cover `SIGKILL`; the detached child survives with its ephemeral port bound. The receipt
proves teardown only on handled paths. Recommend a preflight that refuses to start while
a prior `kama-live-probe` child is alive (one server at a time is already the design's
own constraint), and a bounded `killpg`/wait before the port-closed proof. A leaked
child is lane-owned and stop-able without operator involvement; it is still a serving
process the province says is not claimed.

### Low — L2: fixture evidence can contaminate lane censuses and history

A `listeners` census taken while a fixture is alive will enumerate it as a model
endpoint (any loopback port, `ss -ltn` based). `snapshot` is structurally protected —
"snapshot refuses --port: a matrix probe has no registry baseline to persist"
(`tools/kama-probe.sh:157-158`) — but its default history write is
`OPT_HISTORY="$REPO_ROOT/registry/history"` (`tools/kama-probe.sh:73`), so a receipt
must go to `--out`, never that directory. `check` is safe: registry rows keep their own
ports, and port mode never reads the registry (`tools/kama-probe.sh:837-853`). The
append must forbid census citation during a live run and forbid `registry/history`
placement.

### Low — L3: the child inherits the full parent environment

The design records argv and "never env"
(`.ufo/waves/round-16/build/spec.json:59`), but does not restrict what the child
receives. [INFERENCE] A loopback model server that inherits the agent session
environment can carry tokens into a process tree readable via `/proc`. Round 1's rule is about not
discovering or copying secrets — "kama must not discover or copy secrets itself"
(`corpus/lessons/round-1-safety.md:86-87`) — and this is compatible with a minimal env.
`ldd ~/.local/opt/llama-b11755/llama-server` resolves `libggml*.so.0` from the install
dir, so no `LD_LIBRARY_PATH` is needed. [INFERENCE] `llama-server` needs no secret
environment to serve a local GGUF; pass only `PATH`, `HOME`, `LANG`, `LC_ALL`, `TMPDIR`.

### Low — L4: port exclusion should be derived from endpoint ports, not any digit run

Design: refuse a port that is "any port number appearing in
registry/endpoint-consumers.tsv" (`.ufo/waves/round-16/build/spec.json:59`). The TSV
also contains model digits (`Qwen3-Coder-30B-…`), so a literal scan excludes sub-1024
values; harmless here because the ephemeral range starts at 32768, but it is the wrong
predicate to codify. Derive the set from each row's declared/resolved endpoint port,
keep 8080/34113 as fixed members, bound the retry loop, and fail closed. [INFERENCE]
Port 0 cannot return 8080/34113 under the observed `32768 60999` range; the explicit
exclusion is defense in depth.

### Low — L5: the footprint guarantee is bound to recorded inputs, but `--probe` is not digest-pinned

The design records "server/model identity"
(`.ufo/waves/round-16/build/spec.json:59`) and takes `--probe PATH` with only the lane
default. An overridden probe is an executable the harness launches without a recorded
digest, so the receipt cannot prove which script ran or that it stayed inside this
note's footprint. Record the probe's `realpath`+sha256 in the receipt as is done for
server and model, or restrict `--probe` to the lane path. The harness's own temp/out
writes stay bounded either way; the evidence that only the lane probe ran does not.

### Informational — I1: footprint verified at 10:29:27-03:00 (point-in-time)

`~/.local/bin/llama-server` is a symlink to `~/.local/opt/llama-b11755/llama-server`
(created 10:17); the release asset
`~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` hashes to
`753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`, matching the
claimed `753bfa73…e226`; the model hashes to
`270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; no process and
no registered-port listener were observed. After the 10:17 smoke run, `~/.cache` gained
only the lane-named `kama-shokunin`; `~/.cache/llama*`, `~/.llama` and
`~/.local/state/llama*` do not exist — [INFERENCE] the binary's own runtime writes stay
inside the declared cache, not proven for every launch because no `strace` was run. The
tarball (21.2 MiB) is retained dead weight once its digest is recorded; operator may
remove it.

## Proposed append-only PROVINCE note

Append after `PROVINCE.md:53` (end of file). No earlier byte moves; this satisfies the
lane's append-only rule — "every correction appended at the end of its file"
(`corpus/QUALITY.md:29`, and KQ14 preserves it at `corpus/QUALITY.md:41`).

```markdown
**Lane-owned live fixture (round 16, 2026-10-20 — append; earlier bytes unchanged).**
`tools/kama-llamacpp-live.py` may start an ephemeral llama.cpp server that belongs to
this lane, to exercise `tools/kama-probe.sh` against a real runtime. It is a fixture:
not a unit, not an enabled service, not a timer, not a listening producer this lane
claims (`:10` stays as written), and not a restoration of the retired `qwen-coder`
surface (`:24-28` stays as written). The two registered ports remain unserved before,
during and after a run.
- Footprint, lane-owned and bounded: `~/.local/opt/llama-b11755/` with the
  `~/.local/bin/llama-server` symlink (official release b11755; asset sha256
  `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`),
  `~/.cache/kama-shokunin/models/` (digest-pinned GGUF only), one temporary log under
  `/tmp` deleted after the run, and the receipt at the caller's `--out`. Nothing under
  `~/.config`, `~/.omp`, or systemd is written; no `systemctl`, `systemd-run`, `docker`
  or `sudo` is invoked. The `~/.local` install rests on the operator tooling directive
  (`.omp/agent/RULES.md:1-14`, official binary channel), not on a lane grant; the
  operator may remove the artifacts at any time, and an absent or digest-mismatched
  binary is a setup error, never a skip or pass. Footprint guarantees bind to the
  recorded server/model/probe identities; an overridden input is outside this note.
- Run rules: bind `127.0.0.1` only, on a kernel-assigned ephemeral port (`bind :0`,
  observed range `32768-60999`), never `8080`/`34113` and never a port derived from a
  registry row; GET-only metadata (`/health`, `/v1/models`, `/props`, `/slots`,
  `/metrics`); no request body, credentials, or generation request; a minimal child
  environment, with argv and identity digests recorded and env never recorded.
- Evidence rules: the fixture port is outside the consumer registry by construction.
  This note authorizes probing only the server this tool started — it does not
  authorize contacting any other listener, so `corpus/lessons/round-1-safety.md:88-90`
  continues to require L0 for foreign endpoints. A fixture `MODEL_OK` is evidence about
  the probe, not about any registered consumer: it is never a registry row, never a
  `registry/history` entry (receipts use `--out`), and never a `listeners` census row —
  do not take a census while a fixture is alive. `check` still evaluates only registry
  rows, so the observed-state sentences above are unchanged by a green live receipt.
- Teardown: SIGTERM the process group, then SIGKILL; the receipt proves the pid exited
  and the port refuses connections. A run is one server at a time; a leftover child is
  a lane-owned process to stop, not a service to manage.
- Still operator/L0: making the server resident or unit-managed, adding a timer,
  binding a registered consumer port, or writing any enumerated operator surface.
```

## KQ5 reading (the rule the item asked about)

`corpus/QUALITY.md:13` — "External service/config actions remain an operator handoff;
route/secret/eval findings go to the province owner. Reports contain nonsecret shape
evidence only." The fixture is not an external service action in KQ5's sense: it enables
no service ("A training admission requires enabling services, repointing consumers,
installing timers" is the reject column), repoints no consumer, installs no timer, and copies no config/environment/session body.
It contacts no foreign listener. Its receipt records argv, identity digests, status
codes and a filtered log subset — nonsecret shape evidence. KQ5 is satisfied, provided
the receipt never carries the env and never treats the fixture as a registered consumer.

## Residual risk and verification gaps

- Read-only seat: no lane gate, harness, matrix or measurement was run; nothing here is
  lane evidence. The reviewed artifact (`tools/kama-llamacpp-live.py`) does not exist
  yet; findings target the assigned design at `.ufo/waves/round-16/build/spec.json:59`.
- Probe line numbers cite `tools/kama-probe.sh` md5 `13c9b8d576254b9c09392650a5caac6e`,
  1134 lines, mtime 10:27:17-03:00 (C1 work in flight). They can shift on the next edit.
- Host checks are point-in-time (10:29:27-03:00) and bounded: they attest the sampled shape,
  not a permanent absence.
- [INFERENCE] Minimal-env safety and port-0 exclusion follow from the observed sysctl
  and `ldd` output, not from a launch experiment in this seat.
- The strongest residual risk is a harness death that leaves a child running (L1);
  the province note states ownership of that process but cannot enforce teardown.

## Install record

None. This seat installed or upgraded no tool.
