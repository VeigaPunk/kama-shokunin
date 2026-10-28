# SN01LoopbackSecurity — round-63 security review of the live request plane

Tip: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`. All runs used a `git clone --shared` checkout
at that tip in scratch (toplevel asserted); the lane was read only. No commit, push, or mutating
git against the lane or fleet. Scope: `tools/kama-completion-live.py` (v2), its primitives in
`tools/kama-llamacpp-live.py` (`pick_port`, `refused_ports`, `port_owned_by`, `_preexec_pdeathsig`,
`prepare_witness_dir`, `hold_for_witness`, `_OPENER`), and `tools/round63-c1-counter.py`. Advisory
seat: no verdict on the frozen claims.

Tools: none installed or upgraded. Present binaries used: `strace` 7.2, `ss`, python3 3.14.8,
llama-server b11755 (sha256 `b6a31a8e…`, matches the pinned digest). No pacman.

## Summary

No Critical or High finding. Held under exercise: loopback-only bind, proxy-free opener against
hostile and dead proxies, first-answer gate against a stranger that answers `/health`,
PR_SET_PDEATHSIG, tool-side body cap, env hygiene. Defects are operability and evidence integrity
(F1, F2 Medium), plus Low items that need a same-uid writer, a hostile child, or a shared hold dir.

| # | Sev | Finding |
|---|-----|---------|
| F1 | Medium | `hold_released` passes for a release that arrived before the window; teardown overwrites witness timing |
| F2 | Medium | stale `hold.json` from a killed run: counter contacts the stale port, releases too early, loses the receipt |
| F3 | Low | counter `observe()` POSTs nonce requests to any port named in `hold.json`; no refused-port check |
| F4 | Low | tool writes `hold.json` through a planted symlink (victim outside hold dir overwritten) |
| F5 | Low | refused set omits operator ports 1234 and 45669; 45669 is in the ephemeral range |
| F6 | Low | `port_owned_by` accepts a foreign listener on another 127/8 address |
| F7 | Low | counter `http()` reads bodies unbounded (100 MiB → 223 MiB RSS) |
| F8 | Low | receipts and server log carry `/home/vgpnk` (username) |
| F9 | Info | timeouts are per-operation; a drip holds the call 15 s on a 2 s timeout |
| F10 | Info | server hashed then exec'd by path, no fd pin (code-read) |
| F11 | Info | `prepare_witness_dir` probe lacks `O_NOFOLLOW|O_EXCL` (code-read) |

## Verified controls (exercised)

- **V1 loopback.** `--host 127.0.0.1`; `ss -ltnp` during a hold shows only `127.0.0.1:33677`,
  owned by the child.
- **V2 proxy-free.** `HTTP_PROXY`, `http_proxy`, `HTTPS_PROXY`, `https_proxy`, `ALL_PROXY`,
  `all_proxy` set to a hostile accepting listener, then to a dead port: both `REQUEST_OK`. Hostile
  connections: **0**. `strace -f` over the run: every `connect()` is `127.0.0.1:<child port>`; no
  reference to either proxy port (`exp/proxy/`).
- **V3 gate G1.** Stranger on the picked port answers `GET /health` 200: `SETUP_ERROR`,
  `listener on 44999 is not owned by child 3324937`, rc 2. Stranger got one request
  (`GET /health`), zero POSTs; child dead.
- **V4 gate G2.** Stranger answers 404: `SETUP_ERROR` (`child-exited`), rc 2, child dead.
- **V5 pdeathsig.** Tool SIGKILLed while holding: child gone at first poll (0 ms), still gone at 5 s.
- **V6 counter harness death.** Counter SIGKILLed during its hold: tool and llama-server both gone
  within 0.05 s; the tool exits via orphan teardown (`waited_ms` 3, rc 0).
- **V7 body cap, tool.** 100 MiB response: 65,536 bytes kept, `body_truncated=True`, 24.6 MiB RSS.
- **V8 env hygiene.** Planted `KAMA_SECRET_PROBE=do-not-leak-7731` appears in no artifact.
- **V9 refused explicit ports.** `--port 8080` and `--port 34113` → `port-refused-registered`,
  raised before any connect (in-process, no network).
- **V10 stale release.** `prepare_witness_dir` removes `release` and `ready.json` at tool start.

## Findings

### F1 (Medium) — pre-window release passes `hold_released`; witness timing discarded

`hold_for_witness` ends when `release` exists, with no check that it arrived after the hold began.
The check reason says "appeared inside the hold window". At teardown (`kama-completion-live.py`
~L560) `receipt['hold'] = {'dir', 'released'}` overwrites the witness record (`waited_ms`,
`orphaned`). The docstring promise "true only when the release file appeared inside the window" does
not hold.

Repro: `exp/exp_release.py`. Watcher creates `hold/release` 0.19 s, as soon as the run port accepts a
connect, before any POST and before the hold. Result: `REQUEST_OK`, `hold {"released": true}` with no
timing, `hold_released` passed with "appeared inside the hold window".

Impact: the receipt reports an observer window that did not exist. The counter grades `hold_released`
as a bare boolean. This does not bypass the counter's own live contact (`observe()` still needs
answers from the child), but the window evidence is not what the receipt claims.

Fix: merge rather than overwrite the witness fields; record `hold_started_utc` and the release mtime;
fail unless release mtime is after hold start; the counter compares that mtime with its observe time.

### F2 (Medium) — stale `hold.json` from a killed run: contact, early release, lost receipt

`prepare_witness_dir` removes `ready.json`, `release`, and probes, but not `hold.json`; the tool unlinks
`hold.json` only on a normal return. A killed run leaves `hold.json` with a dead child's port and pid.
The counter's `witness_run` does not clear `work/hold` and polls for `hold.json` right after `Popen`.

Repro: `exp/exp_stale.py`. The work dir holds a `hold.json` naming a live unrelated stub (port 35029,
pid 424242). Observed: the stub received `POST /v1/completions` and `POST /tokenize` (nonce prompt) from
the counter before its own tool served anything; `witness_port 35029`, `witness_pid 424242`;
`new_run_receipt_port null`, `new_run_verdict null`. End state: `hold/` has `hold.json` and `ready.json`,
no `release`, no receipt.

Mechanism (end state plus code, not separately instrumented): the counter wrote `release` at time zero;
the tool's `prepare_witness_dir` (`kama-llamacpp-live.py` ~L299-300) removed it at start; the tool held
with a fresh `ready.json` until its 90 s timeout; the counter gave up at 60 s and killed it.

Impact (operability): re-running in a work dir left by a killed run fails, after an unintended POST to a
port named by a previous run, which may now belong to someone else.

Fix: tool unlinks `hold.json` in `prepare_witness_dir`. Counter clears `work/hold` before `witness_run`,
and writes `release` only after reading a `hold.json` whose pid matches the `ready.json` child.

### F3 (Low) — nonce POSTs go to any port named in `hold.json`

`witness_run` takes `port` and `pid` from `hold.json` and calls `observe()`, which POSTs
`/v1/completions` and `/tokenize`. `listener_owned` is computed in the returned dict, after both POSTs.
No refused-port check exists in the counter.

Repro: `exp/exp_observe.py`. Stub on an unregistered free port (35527) received both POSTs with
`observe_listener_owned null`. No registry port was contacted.

Impact: whoever can write `hold/hold.json` (same uid, or a shared hold dir) can aim nonce requests at a
registered consumer port (8080, 34113, 45669, 1234). Low.

Fix: check the port against `refused_ports()` and the pid against the `ready.json` child before the first
POST; or take the port only from `ready.json`.

### F4 (Low) — tool follows a planted symlink writing `hold.json`

`kama-completion-live.py` writes the hold doc with `open(..., 'w')`: no `O_NOFOLLOW`, no `O_EXCL`, and
`hold.json` is not in the `prepare_witness_dir` cleanup list. The witness temp file in
`kama-llamacpp-live.py` does use `O_EXCL|O_NOFOLLOW`, so the hardening is applied inconsistently.

Repro: `exp/exp_hold.py` run A. `hold/hold.json -> A-victim.txt` (outside the hold dir), planted before the
run. Victim before: `VICTIM-ORIGINAL-CONTENT`. At ready time the symlink is intact and the victim holds
the hold document (`"schema": "kama-completion-hold/v1", "port": 33677, "pid": 3207855`). Receipt
`REQUEST_OK`.

Impact: any file the tool's user can write is overwritten when the hold dir is writable by someone
else. Counter hold dirs are 0755 under owner-only scratch, so this needs a shared location. Low.

Fix: write a fresh temp name with `O_EXCL|O_NOFOLLOW`, then `os.replace`, as `ready.json` does.

### F5 (Low) — refused set omits operator ports 1234 and 45669

`HARD_REFUSED_PORTS = {8080, 34113}`; in-process `refused_ports()` is exactly `[8080, 34113]`. No
registry row names 1234 or 45669. `ip_local_port_range` is `32768 60999`, which contains 45669, so the
default `pick_port` (`bind(127.0.0.1, 0)`) can offer it whenever the operator's server is down. Explicit
`--port 45669` calls `socket.create_connection` (`pick_port` L565) before it can say `port-in-use`:
a TCP connect to the foreign server.

Repro: `refused_ports()` in-process. The connect path is code-read only; the live listener was not
contacted, per the bound.

Impact: the tool can take 45669 while the operator's server is down, so its restart fails. Low.

Fix: add 1234 and 45669 to `HARD_REFUSED_PORTS`.

### F6 (Low) — ownership gate accepts a foreign listener on another loopback address

`_proc_listener_inode` accepts any 127/8 address, and `port_owned_by` returns True when any LISTEN inode
on the port is the child's.

Repro: `exp/exp_gate.py` G3. Stranger on `127.0.0.2:P` before the run; child binds `127.0.0.1:P`. The
`listener_owned` check passes ("owned by child 3326477"); the stranger got 0 requests. The run fails only
on `teardown_port_closed` ("a listener survives on the run port"). The fail-closed backstop is teardown,
not the first-answer gate. The counter's `listener_owned` uses the same primitive.

Impact: the gate's stated guarantee is weaker than written. Requests were not redirected, since both sides
use `127.0.0.1`. Low.

Fix: require every LISTEN inode on the port to belong to the child, or check the 127.0.0.1 listener only.

### F7 (Low) — counter `http()` reads bodies without a cap

`round63-c1-counter.py` `http()` calls `r.read()` unbounded; the tool caps at 64 KiB.

Repro: `exp/exp_body.py`. 100 MiB stub, one process per client: tool 65,536 bytes kept, 24.6 MiB RSS;
counter 104,857,600 chars kept, **223.1 MiB** RSS.

Impact: a hostile child can exhaust the counter's memory during the window. Low.

Fix: bounded read (cap + 1); over-cap is a failed check.

### F8 (Low) — home path and username in receipts and server log

`receipt.json` holds `model.path`, `server.path`, `argv` (`/home/vgpnk/...`), and `captures.props.body`
includes llama-server's `"model_path":"/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"`. The
server log has the same paths. No secret appeared: the env allowlist kept the planted probe out.

Repro: `exp/exp_release.py` leakage scan: `receipt.json` and `work/server.log` contain `/home/vgpnk`. The
copies under `out/` carry the same strings.

Impact: username and layout in committed evidence. Low.

Fix: record paths relative to `$HOME`; keep the sha256 binding; redact `model_path` in the stored body.

### F9 (Info) — per-operation timeouts; a drip holds the call

`POLL_TIMEOUT` (5 s) and the counter's 10 s apply per socket operation. Repro: `exp/exp_body.py` trickle,
30 bytes at one byte per 0.5 s, `timeout=2`: returned after **15.0 s**, `status 200`, 30 bytes. Short-body
detection rests on `completion_untruncated` (Content-Length vs `body_bytes`, code-read L373-380, not run here).
Needs a compromised server. Fix: a whole-request deadline.

### F10 (Info, code-read) — server hashed by path, exec'd by path

`kama-completion-live.py` L228-235 hashes `server` and L256-289 `Popen`s the same path. A same-uid writer can
swap the binary between the two. v5 pins a memfd (`--server-fd`); the v2 request-plane tool does not.
Fix: sealed memfd, or check `/proc/<pid>/exe` against the pinned digest after start.

### F11 (Info, code-read) — probe write follows a symlink planted in a race

`prepare_witness_dir` (`kama-llamacpp-live.py` L311-317) opens `.witness-write-probe.<pid>` with `open(..., 'w')`
after its cleanup pass. A symlink planted between the two would be followed and the target truncated. Needs a
same-uid or shared-dir writer. Fix: `O_CREAT|O_EXCL|O_NOFOLLOW`.

## Not exercised

- SO_REUSEPORT race on the same 127.0.0.1 port: argued from Linux bind rules, not tested.
- Explicit `--port 45669` connect and the live operator listener: deliberately not contacted.
- F10 and F11: code-read only.

## Counter line (verbatim, not adjudicated)

`python3 tools/round63-c1-counter.py --repo <clone> --tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09 --work <scratch>/c1-baseline`
printed:

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```

Exit code not captured.

## Evidence

`.ufo/waves/round-63/w1/out/SN01LoopbackSecurity/` (25 files): `exp-scripts/` (drivers), `proxy/`
(receipts, raw strace, `connect-destinations.json`), `hold/` (run A receipt and summary), `gate/summary.json`,
`body/` (summary and client), `release/receipt.json` (F1), `counter-kill/receipt.json` (V6),
`stale-hold/` (F2 leftovers), `c1-baseline.out` and `.err`. Copied receipts contain `/home/vgpnk` (F8).

Install record: none. Scratch root removed after copying; no stray processes from these runs remained.
