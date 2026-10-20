# ScoutPortPolicy — ports C2 must never bind, and the refusal rule

**Seat:** `KamaR16.ScoutPortPolicy` (scout, leaf, advisory only)
**Lane root:** `/home/vgpnk/Projects/shokunin/kama-shokunin`
**Report:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/build/advice/ScoutPortPolicy.md`
**Date:** 2026-10-20
**Tooling record:** nothing installed, upgraded or restarted. Read-only seat: the two named registry files, exactly one `ss -ltn` snapshot, the pinned llama.cpp b11755 sources (`704366d76`) and the Linux port allocator source. No server started, no socket bound.
**Question answered:** which ports C2 must never bind; whether `bind(127.0.0.1:0)` can return one; the refusal rule, stated so L1 can measure it.

---

## 1. Registered consumer ports — hard deny

Registry rows (tab-separated, header at `:34`); ports taken from the `declared_baseurl` column, never from digit runs.

| Port | Registry id(s) | Evidence (`path:line`) | Quote |
|---|---|---|---|
| **8080** | `omp-llama-cpp-default` | `registry/endpoint-consumers.tsv:35` | "code-level fallback pin, not proof of the effective environment-selected URL" |
| **34113** | `ufo-fsd-thetick` | `registry/endpoint-consumers.tsv:36` | "surviving explicit pin; historical positive control, currently DEAD" |
| **34113** | `ufo-fsd-local-helper` | `registry/endpoint-consumers.tsv:37` | "surviving explicit DEFAULT_URL pin" |

Baseline state (`registry/history/latest.tsv:2-4`, snapshot `20261014T124232Z`): all three rows are `DEAD` / `connection-refused`, on ports `8080`, `34113`, `34113`.

**Parsing rule for the deny set:** take the authority's port from each row's `declared_baseurl`; do not regex digits across the file. The file says so itself: `registry/endpoint-consumers.tsv:26` — "A bare digit run is never read as a port — "Qwen3-Coder-30B" is not port 30." A naive `\d+` also yields `6901` (from `RFC6901`, `:19`).

Registry-authoritative registered set: **{8080, 34113}**.

## 2. Current TCP listeners — hard deny at measurement time

One `ss -ltn` snapshot, 2026-10-20 (read-only, not repeated). Distinct ports, with the addresses actually observed:

| Port | Local address(es) from `ss -ltn` | Note |
|---|---|---|
| **53** | `127.0.0.53%lo:53`, `127.0.0.54:53`, `172.17.0.1:53` | three listeners, no `127.0.0.1` row |
| **631** | `127.0.0.1:631`, `[::1]:631` | |
| **5355** | `0.0.0.0:5355`, `[::]:5355` | |
| **8787** | `127.0.0.1:8787` | unattributed local service cluster |
| **8788** | `127.0.0.1:8788` | |
| **8789** | `127.0.0.1:8789` | |
| **8790** | `127.0.0.1:8790` | |
| **8791** | `127.0.0.1:8791` | |
| **8793** | `127.0.0.1:8793` | |
| **8795** | `127.0.0.1:8795` | |
| **8796** | `127.0.0.1:8796` | |
| **36381** | `127.0.0.1:36381` | ephemeral-range socket |

Observed line form (verbatim): `LISTEN 0      512        127.0.0.1:36381      0.0.0.0:*`.
The block is a snapshot, not an invariant: the probe's own history calls this "ephemeral socket churn" (`LOG.md:165`), so the live set MUST be recomputed at run start.

**Deny by port number, not by socket address.** `127.0.0.1:53` would bind successfully while `127.0.0.53:53` is listening (different local address), so a successful bind-test is not evidence that a port is safe. Same for `172.17.0.1:53`. These ports are denied because a consumer that resolves `127.0.0.1:<port>` must never reach the lane's toy server, not because the kernel would refuse the bind.

## 3. Union — ports C2 must never bind

Sorted: **53, 631, 5355, 8080, 8787, 8788, 8789, 8790, 8791, 8793, 8795, 8796, 34113, 36381** (14 ports).

Soft-reserved (MUST NOT be selected by omission; not in the hard set): **9931** — llama-server's default when `--port` is absent (`tools/server/server-http.h:78`: `int port    = 9931;`; local `llama-server --help`: "port to listen (default: 9931)"). Omission is a collision with a concurrent lane, not a registry violation. `11434`/`1234` appear only as historical consumer endpoints in `corpus/knowledge/consumer-registry.md`; they are not registry rows and are not in the hard set.

## 4. Can `bind(127.0.0.1:0)` ever yield one of them? **Yes — 34113.**

The kernel picks an ephemeral port from `ip_local_port_range`, after subtracting only `ip_local_reserved_ports`:

- Host range: `/proc/sys/net/ipv4/ip_local_port_range` = `32768	60999`.
- Host reserved list: `/proc/sys/net/ipv4/ip_local_reserved_ports` is **empty** — nothing protects 34113.
- Range doc: `https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt:907-914` — "Defines the local port range that is used by TCP and UDP to choose the local port."
- Reserved-port doc, `:916-919` — "These ports will not be used by automatic port assignments (e.g. when calling connect() or bind() with port number 0)." Default Empty (`:945`).
- Allocator, `https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/plain/net/ipv4/inet_connection_sock.c`:
  - `:348` `offset = get_random_u32_below(remaining);`
  - `:355` `port = low + offset;`
  - `:359` `if (inet_is_local_reserved_port(net, port)) continue;`
  The scan steps by two across the whole range and skips **only** reserved ports; no awareness of application conventions.

Per-port verdict:

| Port | In `[32768, 60999]`? | Free right now? | Reachable by `bind(0)`? |
|---|---|---|---|
| **34113** | **yes** | **yes** (`latest.tsv:3-4` DEAD; no `ss` row) | **YES** |
| **36381** | yes | no (currently bound) | yes once that socket closes |
| **8080** | no | yes | no, unless the range is widened |
| 53, 631, 5355, 8787-8796 | no | — | no, under the current range |
| 9931 | no | yes | no, under the current range |

[INFERENCE] per-draw risk if `bind(0)` is used unguarded: the odd-parity offset has 14,116 possible values over this range, so one draw lands on 34113 with probability ≈ 1/14,116; repeated starts accumulate. It is not a 1-in-65,535 long shot, and the allocator deliberately sweeps the range, so "can" means "will, given enough runs".

**Consequence for the dispatched C2 design** (`.ufo/waves/round-16/build/make_spec.py:15`: "a free loopback port that is never a registered consumer port"): `bind(0)` plus a refuse/retry check is *mandatory*, not defensive decoration. `bind(0)` alone cannot support the claim.

**Do not use llama-server's own `--port 0` as the final bind.** It is supported for a single TCP host and reports the real port (`tools/server/server-http.cpp:507-512`: `const auto bound_port = srv->bind_to_any_port(host);` … `port = bound_port;`; the address string at `:522-523` and the log at `tools/server/server.cpp:543-544`: `SRV_INF("listening on %s\n", address.c_str());`). But the listener is already up, and answering, before any check can run — on this server even while loading (`GET /v1/models` → 503, per the C2 observation at `.ufo/waves/round-16/build/make_spec.py:16`). A kernel-chosen 34113 would therefore be *served* before a post-hoc check could reject it. Resolve the port in the harness, gate it, then pass a concrete `--port`.

## 5. Refusal rule (normative advice for `tools/kama-llamacpp-live.py`)

**R1 — Deny set is computed, not asserted.** At start: `REGISTRY_PORTS` = ports parsed from the `declared_baseurl` authority of every non-comment row of `registry/endpoint-consumers.tsv` (today `{8080, 34113}`); `LIVE_PORTS` = every TCP port in `state LISTEN` from `/proc/net/tcp` + `/proc/net/tcp6` (all local addresses, both families); `CONVENTION` = `{9931}`. `DENY = REGISTRY_PORTS | LIVE_PORTS | CONVENTION`. Record the three sets and their provenance in the receipt.

**R2 — Do not let the kernel choose unconstrained.** Preferred: iterate a lane block disjoint from the ephemeral range and from `DENY` (default **61000–61099**), bind-test each on `127.0.0.1` (bind, close, no `listen()`), take the first free one. If the block intersects the current `ip_local_port_range` or `DENY`, abort rather than shift silently. Acceptable fallback: `bind(0)` + immediate gate (R3) + bounded retry; never hand `0` to llama-server.

**R3 — Gate before spawn, on the concrete port.** If `p in REGISTRY_PORTS` → exit 2, naming the registry ids. If `p in LIVE_PORTS` → exit 2, naming "live listener". If `p in CONVENTION` → exit 2. No child is spawned on any refusal. Never treat a busy port as "skip to the next one" when the caller named it explicitly.

**R4 — Launch fixed.** `--host 127.0.0.1 --port <p>` (literal IP, never `localhost`, never `0.0.0.0`/`::`), no `--reuse-port`. The help text is explicit: "allow multiple sockets to bind to the same port (default: disabled)". (`SO_REUSEPORT` is not inherited from cpp-httplib's default here: `vendor/cpp-httplib/httplib.h:2585` initialises to `default_socket_options`, but `server-http.cpp:85-94` replaces it with a lambda that sets only `SO_REUSEADDR` unless the flag is given — a correction to `SentinelLiveSafety.md` F3; either way, never pass the flag.)

**R5 — Verify after bind, before any request.** Parse the actual port from `listening on http://127.0.0.1:<PORT>` (`server.cpp:543-544`). Require `actual == p`; if not, or if `actual in DENY`, kill the child and fail without probing it. Then prove ownership: exactly one `LISTEN` inode for `p`, and that inode appears in `/proc/<child.pid>/fd`; no listener owned by the child on any `REGISTRY_PORT`.

**R6 — Test hook, same gate.** Add `--port N` (or `KAMA_LLAMACPP_PORT`) routed through R3, so the refusal path is executable on demand. Without it, the "refuse 8080/34113" branch cannot be measured: 8080 is unreachable through `bind(0)` on this host, and 34113 is a ~1/14,116 draw. An unexercised safety branch is not evidence.

**R7 — Teardown proof.** Kill the process group, wait, and assert: no listener on `p`, no surviving llama-server PID, and `connect(127.0.0.1:p)` refused. Re-run the `DENY` listener scan and require no lane-owned socket on any `REGISTRY_PORT`.

**R8 — No host mutation.** Do not write `ip_local_reserved_ports` (the kernel-native way to protect 34113/8080: `ip-sysctl.txt:916-919`), do not touch sysctl, systemd, `~/.config` or the registry.

Minimal shape:

```python
DENY = REGISTRY_PORTS | LIVE_PORTS | {9931}
if args.port is not None:                       # R6 test hook
    if args.port == 0: refuse(0, "not a concrete port")
    if args.port in DENY: refuse(args.port, provenance(args.port))
    p = args.port
else:
    lo, hi = read_range()                       # /proc/sys/net/ipv4/ip_local_port_range
    p = first_free_127001(61000, 61099, lo, hi, DENY)   # R2
assert p not in DENY
spawn(["llama-server", "-m", model, "--alias", alias,
       "--host", "127.0.0.1", "--port", str(p), "-c", ctx, "-t", threads, "--no-webui"])
actual = wait_for_listening_line()              # R5
if actual != p or actual in DENY: kill_and_fail()
assert listener_owned_by_child(p) and not child_owns_any(REGISTRY_PORTS)
```

## 6. Measurement plan for the refusal (what L1 can run)

| Forced input | Required observable |
|---|---|
| `--port 8080` | exit 2; stderr names `omp-llama-cpp-default`; no child spawned; no `LISTEN` on 8080 |
| `--port 34113` | exit 2; stderr names `ufo-fsd-thetick` and `ufo-fsd-local-helper`; no child; no `LISTEN` on 34113 |
| `--port 8791` (live) | exit 2; stderr says live listener; no child |
| `--port 53` | exit 2 (must refuse although a `127.0.0.1:53` bind would succeed) |
| `--port 61042` (allowed) | proceeds; `actual == 61042`; child owns no socket on 8080/34113; teardown proof holds |
| `--port 0` | exit 2 ("not a concrete port"); probe also rejects `<1` (`tools/kama-probe.sh:157`: "`--port` out of range") |

The negative rows defeat an accept-all implementation; the allowed row defeats a reject-all implementation. Both are required, or the gate is unfalsifiable.

## 7. Why the deny set is an operability requirement, not hygiene

`kama-probe.sh snapshot` persists a dated JSON, a TSV baseline and a transition ledger (`tools/kama-probe.sh:19-22`: "dated JSON + a TSV baseline … transitions are appended to DELTA.md"; ledger format at `:48`: "`<ts> id field old->new`"). If the toy server ever occupied 34113, a `snapshot` taken while it was up would record `ufo-fsd-thetick`/`ufo-fsd-local-helper` transitioning from `DEAD` to a verdict carrying the toy model id — a false transition in the permanent drift record, produced by the very lane that is trying to certify endpoint truth. The 8080 row carries `expected_model_id` `-`, so a serving toy on 8080 could even read as `MODEL_OK` under `--expect` `*`/`-`.

## 8. Limits and unknowns

- `ss -ltn` is one snapshot with no process attribution (`-p` not used); "unattributed local service cluster" for 8787-8796 is accurate but unnamed.
- The listener set is expected to churn; the hard-deny list in §2 is valid only at measurement time. The rule, not the list, is the deliverable.
- 34113's freedom is inferred from two sources agreeing (no `ss` row; `latest.tsv` `connection-refused`), not from a connect attempt — this seat did not touch the port.
- The per-draw probability in §4 is [INFERENCE] from the allocator's offset arithmetic; no `bind(0)` loop was run, precisely to avoid landing on 34113.
- If any registered consumer comes alive during C2, the deny rule still applies unchanged; C2 must prove non-ownership, not that the consumer is DEAD.
