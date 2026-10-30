# MT22ListenerShapes — round 64, wave f — C1 listener topology vs the amended counter

Seat: MT22ListenerShapes (leaf, advisory). Item: attack item (C1) — listener topology
against the amended counter. Tip under test: `23b3fdb1a925129a9961cf551f6d40bf251602cb`
(counter with AMENDMENT 1/1a/1b; tool byte-identical to the freeze commit).
Instrument: `tools/round64-c1-counter.py` **unmutated**, always run from the scratch
clone path against the clone's committed forged tip; verdict one-liners below come from
that file. A diagnostic wrapper (`mt22-diag.py`) runs the *same unmodified counter file*
and additionally dumps every `collect()` snapshot (listeners / holder pids /
unreadable sets) — used for observation only; its `met=` lines agree with the verdict
runs wherever both exist.

Forged tools: one hook block inserted into `tools/kama-completion-live.py`
(192 insertions vs the tip; diff in `out/MT22ListenerShapes/code/forged-tool.patch`),
shape selected at run time by a one-shot flag file (MT01's technique) so the counter's
91 control families stay genuine on every scored run (verified: forge patch applies to
the forged text with offsets, no fuzz). Committed in the scratch clone:
- `47405e64…` (blob `c48211c3…`): shapes reuseport, v6, v6root, ns, fwd, unixfront
- `c95065e8…` (blob `5fefcfc8…`): = 47405e64 + daemon-command mode fix; v6daemon,
  mappeddaemon (first attempt, daemon-side ValueError → honest runs, discarded)
- `0c37129d…` (blob `9a45946f…`): = c95065e8 + clean forger shutdown + a tool-driven
  close signal; final runs for v6, v6daemon, mappeddaemon, fwd, unixfront
A **pre-started root daemon** (scratch file, not part of the tool) accepts one command
per connection and holds the requested listener; it is started *before* the counter's
tool process, so its `/proc/<pid>/fd` is unreadable (root-owned) and its start ticks
precede the tool's — outside the counter's `unreadable_own` gate
(`round64-c1-counter.py:452-455` records it as `unreadable_old`; the only graded gate
is `unreadable_own` at `:485`; `unreadable_old` is never read by any check).

## Verdicts

| # | item | forgery | verdict | decisive check / observation |
|---|------|---------|---------|------------------------------|
| 0 | — | none (control) | met=True 91/91 | — |
| a | (a) SO_REUSEPORT 2nd listener, same port/addr | forger binds SO_REUSEPORT on the run port before the child spawn | KILLED (not buildable) | kernel: the pinned llama-server does not set SO_REUSEPORT — after-child bind = EADDRINUSE; forger-first → child rc=1 → `live: no receipt/witness produced tool exited before hold.json` |
| b1 | (b) 2nd listener at `::1:<runport>` (v6only=1), same-uid tool-spawned | helper holds ::1:P | KILLED | `bind_holders` + `bind_exe`/`bind_argv`/`bind_maps`/`bind_ref_files`/`bind_claim` — and **`bind_listener` is NOT among the failures**: the counter admits the second listener by address class |
| b2 | (b) 2nd listener at `::1:<runport>`, **root**, tool-spawned (`sudo -n`) | helper holds ::1:P | KILLED | `bind_holders` **alone** — the root holder is invisible to the holder scan but graded via `unreadable_own` (started after the tool): AMENDMENT 1's fix works |
| b3 | (b) 2nd listener at `::1:<runport>`, **root, PRE-STARTED daemon** | daemon holds ::1:P | **SURVIVED** | **no check decides**: met=True 91/91 while the counter's own snapshot shows TWO listeners on the run port (both `loopback: true`), holder set = [pinned child only], `unreadable_own = []` |
| c | (c) IPv4-mapped listener `::ffff:127.0.0.2:<runport>` (v6only=0), root pre-started daemon | mappeddaemon | KILLED | `bind_listener` **alone** — `_hex_loopback` rejects `…FFFF00000200007F` while the tool's own `_tcp6_is_loopback` accepts it (classifier divergence, §4) |
| d | (d) unix-socket front: run port held by a TCP→unix→child front (child moved to a second port) | unixfront | KILLED | `bind_exe`/`bind_holders`/`bind_claim`/`bind_argv`/`bind_maps`/`bind_ref_files` — the holder is the python front; the unix hop itself is invisible (`listeners()` is TCP-only) |
| e | (e) real child moved to a second port; grandchild TCP forwarder holds the advertised run port (relays to the child, so all answers stay genuine) | fwd | KILLED | `bind_exe`/`bind_holders`/`bind_argv` (+ `listener_holders_pinned`, `verdict`); `bind_claim` passes (both sides attribute the same front) and `bind_ancestry` passes (descendant) — identity of the holder is the decider |
| f | (f) listener inside a user+net namespace the tool created (binds 127.0.0.1:<runport> inside the ns) | ns | SURVIVED / blind | met=True 91/91; counter `listeners()` = **one** inode (its own namespace) while the helper's log proves it was listening on the same port inside its ns |

Baseline control (unmutated tip, unmutated counter): `met=True`, 91/91, errors=0.

## The survivor (b3) — full detail

Construction: the forged tool sends the run port to a **pre-started root daemon**
(start ticks < tool start ticks); the daemon binds `::1:<runport>` (IPV6_V6ONLY=1),
listens, serves canned llama-shaped answers, and closes when the release file appears.

Counter observation (diagnostic, both snapshots identical):
```json
{"port": 38727,
 "listeners": [{"inode": 2316277111, "loopback": true},
               {"inode": 2316225215, "loopback": true}],
 "holder_pids": [2751413],
 "holder_exes": ["/home/vgpnk/.local/opt/llama-b11755/llama-server"],
 "unreadable_own": [], "unreadable_old": 540}
```
Verdict one-liner (unmutated counter):
```
tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
```
Deciding code: `listeners()` (`:250`) enumerates **every** LISTEN socket on the port in
the counter's namespace, both families; `_hex_loopback` (`:240`) admits exactly
`0100007F`, `::1`, and the v4-mapped `::ffff:127.0.0.1` — so `bind_listener` (`:480`)
passes with two sockets on the run port and never asserts a single listener.
`bind_holders` (`:483`) compares the set of holders it could *read* to `{hold_pid}`;
the root daemon is unreadable (skipped by `holder_pids`, `:270`) and predates the tool
(so `unreadable_own` is empty). The tool's own receipt bookkeeping is computed with the
same blind scan (`kama-completion-live.py:_proc_holders` skips unreadable fd tables),
so `bind_claim` passes too. Nothing else looks at the second socket.

Operability consequence, demonstrated live (`out/MT22ListenerShapes/code/demo-dual.py`,
output `demo-dual-out.txt`): with the pinned server on `127.0.0.1:P` and the daemon on
`[::1]:P`, the same port number answers two different `/v1/models`:
`127.0.0.1` → the real pinned model list; `[::1]` → the fabricated canned list.
The counter probes `127.0.0.1` only (`http()`, `:215`), so the rogue endpoint is never
exercised, and both `/health` answers look healthy.

Relation to the acknowledged limits (freeze.txt "Survivors acknowledged and NOT
fixed"): MT01 O3/O4 = an own-uid non-dumpable helper that existed before the tool and
holds a **dup of the child's socket** (one listener inode; an unattributable second
*acceptor*). b3 is the same root cause — holder attribution requires a readable fd
table, and the start-time gate exempts pre-tool processes — but it is a **distinct
second LISTEN socket**: the counter's own snapshot shows two sockets on the run port
while it certifies the run, which the dup case never shows. It also moves the invisible
holder to root ownership (the amendment's `unreadable_own` gate is start-time-scoped,
not uid-scoped, so a pre-tool root holder is equally exempt).

## KILLED details (counter one-liners, failure sets verbatim)

- a (reuseport, forger-first): `tool_present=1 live_ok=0/1 … errors=1 met=False` —
  `error: live: no receipt/witness produced tool exited before hold.json` (the child
  died on EADDRINUSE; after-child ordering measured EADDRINUSE too, `facts-out.txt`).
- b1 (v6, same-uid): `error: live: ["bind_argv", "bind_claim", "bind_exe",
  "bind_holders", "bind_maps", "bind_ref_files"]` — diag: two listeners, holders =
  [llama-server child, python3.14 helper]. (`teardown_port_closed` appeared in one
  earlier attempt while the forger's closer crashed; the final run's set is the clean
  identity family above.)
- b2 (v6root): `error: live: ["bind_holders"]` — diag: two listeners, holders =
  [child] only, `unreadable_own = [<root helper pids>]`. AMENDMENT 1's fix holds for
  tool-spawned root holders (this also re-scores wave-b MT02's V3/V5/V6 shapes: a
  root holder started by the tool is now graded).
- c (mappeddaemon): `error: live: ["bind_listener"]` — diag: two listeners, second
  `loopback: false` (`::ffff:127.0.0.2`). Single-cause: with an invisible pre-started
  holder, bind_holders/bind_claim pass and the address class is the only decider.
- d (unixfront): `error: live: ["bind_argv", "bind_exe", "bind_holders", "bind_maps",
  "bind_ref_files", "listener_holders_pinned", "teardown_observed",
  "teardown_port_closed", "verdict"]` — diag: one listener, holder = python3.14.
  The unix hop is invisible to `listeners()`; the kill is holder identity.
- e (fwd): `error: live: ["bind_argv", "bind_exe", "bind_holders", "bind_maps",
  "bind_ref_files", "listener_holders_pinned", "teardown_observed",
  "teardown_port_closed", "verdict"]` — diag: one listener, holder = python3.14; the
  child answered every probe through the front, so the kill is purely identity
  (`bind_claim` and `bind_ancestry` pass — the front is a descendant, as the seat's
  "grandchild" phrasing anticipates). (`teardown_*` failures are a forgery-mechanics
  race — the front's close raced the tool's port check — not a counter check.)
- f (ns): verdict-run flake then clean: first attempt `error: live: ["bind_holders"]`
  (ambient `unreadable_own` burst, §6); re-run clean `met=True 91/91` with
  `listeners()` = one inode — the counter does not see the netns listener.

## Scope observations (not bypasses)

1. **`listeners()` is namespace-scoped and TCP-only** (`/proc/net/tcp{,6}` of the
   reading process; unix sockets never appear). A same-port listener in a tool-created
   user+net ns (f) is invisible to `listeners()`, `holder_pids`, `bind_ns` and to the
   teardown port-closure check — but it is also unreachable from the counter's
   namespace, so it cannot answer or steal the run port. Blind spot, not a bypass.
2. **Classifier divergence between tool and counter**: the tool's
   `_tcp6_is_loopback` accepts `::ffff:127.0.0.2` (and its v4 rule accepts any `127.x`
   — last byte `7F`), while the counter's `_hex_loopback` accepts only exactly
   `127.0.0.1`, `::1`, `::ffff:127.0.0.1`. The counter is stricter; the divergence is
   measurable (`facts2-out.txt`) but not exploitable, because `bind_listener` is graded
   from the counter's own enumeration.
3. **`::ffff:127.0.0.1:<runport>` cannot coexist with the child's v4 bind** (measured
   EADDRINUSE; v6only=1 → EINVAL), so variant (c) at the child's own address is not
   buildable; the mapped address that *does* coexist (`::ffff:127.0.0.2`) is rejected
   by `bind_listener`.
4. **Answer substitution remains closed on the TCP plane**: every topology that puts a
   non-pinned process on the probed socket dies on `bind_exe`/`bind_holders`
   (fwd/unixfront), and any second pinned server a tool might stand in with is a
   genuine pinned server (the CR03-disclosed bookkeeping class, not re-tested here).

## Host-noise operability note (for the L1)

The host floor of same-uid unreadable processes (`unreadable_old`) was 534–4469 during
my runs. Twice, a transient burst of ~100–160 same-uid unreadable pids (other seats'
short-lived non-dumpable helpers) started inside the counter window and landed in
`unreadable_own`, failing `bind_holders` on runs that were otherwise clean (my first
manual v6 attempt; the first ns verdict run). Both re-runs passed. This is MT02 §6.2's
flake source, now quantified: `bind_holders` can fail-closed on honest runs purely from
sibling-seat noise.

## Method, privilege, tools

- Clone recipe followed; all edits and commits inside the scratch clone; the lane was
  only read (read-only git). Work dirs fresh per run (`--work`), inside the scratch.
- No tools installed or upgraded (system python3 3.14.8, `patch`, `iproute2`, `sudo`,
  `unshare` all present). Privilege used: `sudo -n` to start/stop my own root daemon
  and helpers (MT02 precedent); `unshare -Urn` for the namespace helper.
- Kernel fact probes: `facts.py`, `facts2.py` (outputs in `out/…/code/`). The namespace
  helper's fd table was measured readable from the parent after
  `unshare(CLONE_NEWUSER|CLONE_NEWNET)` + `PR_SET_DUMPABLE(1)`.
- Honest-disclosure: my first fwd/unixfront attempts crashed the tool with a
  RecursionError (my hook re-entered `subprocess.Popen` after rebinding it); the
  scored runs use the fixed hook (original captured before rebinding). The first
  v6root helper ran without the sudo prefix (my bug) and behaved as the same-uid case;
  the scored v6root run has the prefix.

## Bounds and restoration

- Lane untouched: read-only git only; no lane file written except this report and
  `out/MT22ListenerShapes/`. Lane HEAD before: `6203f6f5c3dde650fe004ab855249c29e1189aba`;
  lane tool blob at the tested tip: `a0c26e14184d664bef75013aac6f1c2a7bb47881eb4bf372b5bb70a26861423c`.
- All mutations lived in the disposable scratch clone (commits listed above) and are
  removed with the scratch root after evidence staging; the counter file scored is the
  unmutated tip blob (`git show`), so no instrument bytes were changed anywhere.
- Ports: loopback ephemeral only; 8080/34113 never touched; only my own helper/daemon
  processes were killed.

## Evidence

`out/MT22ListenerShapes/` — `runs/` (r2-/r3-/r4-*.out/.err + summary2/3/4.txt),
`diag/` (collect() snapshots per shape), `code/` (forged-tool.patch, commits.txt,
builder/daemon/diag/demo sources, fact outputs), `facts/`. Full untruncated one-liners
are in `runs/`; the lines quoted above are verbatim from those files.
