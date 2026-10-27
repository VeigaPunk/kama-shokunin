# Sen2Proc — /proc observation hardening of round-50 C1 (r50 attack + frontier)

**Verdict: all five adversarial /proc paths I exercised end fail-closed — no false pass through C1 — but the observation layer has three hardening defects and one unenforced invocation assumption: pid identity is jiffy-granular (`pid_alive`), `port_refuses` reads a connect *timeout* as a refusal, the witness handshake carries no process identity, and the counter silently depends on the `--scratch` filesystem having `maps dev == stat st_dev` (a btrfs scratch turns the measurement into a kill).**

Seat: Sen2Proc, leaf, lane kama, round 50. Build measured: lane commit
`97c864bead3ee4a2f629574e77263d33834ec98a`; base `26ecba64ad6fb571d09074b07202d1618a46ecd1`.
Counter under test: `tools/round50-replay-bind-audit.py`, sha256
`ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89` (equals the
preregistration's `counter_sha256`). Tools at the build: `tools/kama-llamacpp-live.py`
`61e777b743aedb55c9532c4892d14a6cf0600f9f6f260595d635ec50ff708507`,
`tools/kama-live-replay.py` `d5c58972c0fd8f818b8dd2bd81f6cbc3a87c7f23b65805a804bf09b579a5a239`.
Host: `CLK_TCK=100`, `kernel.pid_max=4194304`, `/` and `/home` btrfs (subvols `/@`, `/@home`),
`/fast` and `/tmp` xfs. Lane read-only: nothing was written, fetched or committed in the lane; the
counter and both tools were imported from copies extracted with `git archive 97c864be` into my
scratch (byte-identical to the lane files). No tools installed or upgraded. Every llama-server I
started was on an ephemeral loopback port chosen by its driver and torn down by it; `pgrep -af
llama-server` at the end shows only servers owned by other seats (paths under their scratch), none
of mine.

Artifacts (all under `.ufo/waves/round-50/w1/out/Sen2Proc/`): `probe1-direct.json`,
`probe1-reuse.json`, `probe2.json`, `probe2b.json`, `probe2b-observe.json`, `live-dead.json`,
`live-race.json`,
`probe34-xfs.json`, `probe34-deleted.json`, `probe34-btrfs.json`, `probe5.json`, the five drivers
`probe1.py`/`probe2.py`/`probe2b.py`/`probe34.py`/`probe5.py`, and `commands.txt`.

---

## 1. pid reuse — does the counter's `pid_alive` bind a pid to its starttime?

**Yes, it compares `/proc/<pid>/stat` field 22, and that catches reuse in a later clock tick; it
does not survive reuse inside the same 10 ms tick.**

Source: `tools/round50-replay-bind-audit.py:234-241` (`stat_fields` = state, ppid, starttime),
`:244-248` (`pid_alive`: `False` for absent/Z/X; then `start is None or st[2] == start`), `:425-437`
(`reap` kills only on a true `pid_alive(pid, start)`), `:513`, `:518` (teardown snapshot `{pid:
starttime}`, compared with the starttime), `:477` (the only call without a starttime, after the
replay exits — a stale starttime would only *false-fail* there).

Commands and outputs (`probe1.py`; exit 0 for both):

* direct: a live `sleep` with `start=3556704` → `alive_no_start=true`,
  `alive_true_start=true`, `alive_start_plus_1=false`, `alive_start_minus_1=false`.
* rapid spawn loop, 300 children: starttime non-decreasing, no pid overlap, all 300 reported dead
  afterwards with and without their starttime (`probe1-direct.json`).
* forced reuse (`unshare -r -p -f --mount-proc`; the next pid is set with
  `/proc/sys/kernel/ns_last_pid`): 5/5 same-tick attempts reused the pid with **`start_delta=0`**,
  and 2/2 later-tick attempts (50 ms delay) reused it with `start_delta=5` ticks.

| attempt | old start → new start | `pid_alive(pid, old_start)` | `reap`'s exact predicate + action |
|---|---|---|---|
| same-tick ×5 | 3554064 → 3554064 | **true** | new process SIGKILLed, `rc=-9` |
| later-tick ×2 | 3554089 → 3554094 | false | new process survives |

Verdict: **the starttime is a 10 ms-granular identity, not a process identity.** A pid whose whole
life fits in one tick, recycled inside that tick, is indistinguishable from the old process.
Demonstrated in an isolated pid namespace: the counter's exact kill predicate
(`pid_alive(pid, start)`) evaluated true for the *new* process and the following `os.kill(pid,
SIGKILL)` killed it (`probe1-reuse.json`). Reachability in the counter is narrow: the reused
process must be born in the same tick as the snapshot entry's own starttime, i.e. the snapshot
member must have been born and killed within one jiffy — the real snapshot members (replay, live
tool, server) live for seconds, so their `starttime` cannot collide with a later birth. On this
host pid reuse also requires the 4,194,304-entry pid space to wrap, or write access to
`ns_last_pid` (CAP_SYS_ADMIN over the counter's pid namespace). Severity **Low / informational**;
the same pid-not-pidfd window exists between `p.poll()`/`pid_alive` and `os.kill`/`os.killpg`
(`:425-437`).

## 2. ready.json written while the server child is already dead

**The live tool's guard rejects an already-dead child, but the announce is not atomic: a child that
dies between the guard's `poll()` and `os.replace` is published in ready.json as a dead pid. The
counter then fails closed (six problems, bind leg 0).**

Source: `tools/kama-llamacpp-live.py:326-372` — guard `if not _child_running(proc): raise
SetupError('witness-child-exited-before-announce')` at `:340-341`, tmp `O_EXCL|O_NOFOLLOW` open at
`:346`, `os.replace(tmp, ready_path)` at `:351`, hold loop `_child_running` at `:358-359`, unlink of
ready.json at `:364-370`. Counter: `:408-415` `wait_ready` accepts the first dict with an int `pid`
and `port` (no schema check, no starttime); `observe` at `:343-372` re-reads `/proc`.

Evidence:

* Guard on an already-dead child (child waited before the call): `SetupError
  witness-child-exited-before-announce`, `ready_exists=false` (driver inline, run once).
* Announce race (`probe2b.py`, inotify on the witness dir; on `IN_CREATE ready.json.tmp.<pid>` the
  live tool is SIGSTOPped after the guard, the server child SIGKILLed, then SIGCONT — the tool
  publishes anyway): `ready.json` read with `pid=1334824`, and
  `announced_pid_stat_at_read=["Z", 1333477, 3565161]`, `announced_pid_alive_at_read=false`; the
  file stayed readable for `witness.waited_ms=105` and was then removed; the live tool exited 2
  with `setup_error="post-witness:child-exited-rc-9"`, `witness.released=false`,
  `port_listener_ownership="unproven"`. The counter's own `observe()` on that pid appended six
  problems: `exe sha256 None is not the frozen server`, `no LISTEN socket on 34909 owned by pid …`,
  `server environ unreadable`, `server parent environ unreadable (pid None)`, `maps unreadable`,
  `nonce round-trip failed: URLError: [Errno 111] Connection refused` (`probe2b-observe.json`;
  the handshake itself in `probe2b.json`).
* Kill-after-ready (the ordinary "pid later exits before observation" case, `probe2.py`): ready.json
  present with the killed pid at +0 ms, gone at +200 ms (the counter's poll cadence), and the same
  six `observe` problems; the receipt keeps `model_mapping.mapped=true` (recorded before the hold)
  but `witness.released=false` and exit 2 (`live-dead.json`, `probe2.json`).

Verdict: **fail-closed.** A dead announced pid cannot pass: the exe digest, LISTEN-socket
ownership, nonce round-trip and model mapping all need the live process, and the post-release join
then also requires `witness.released=true`, exit 0 and the rerun receipt's `child_pid`/`model_mapping`.
What is missing is any *identity* in the handshake (see finding F4): the counter cannot tell "the
child died after announce" from "the pid was recycled", and a server killed by the host (OOM) turns
the kill predicate into `met=False` with no retry.

## 3. model path whose maps entry is `(deleted)` (open fd)

**Everyone fails closed: the live tool records `mapped:false, reason:"model-path-not-in-maps"`, the
counter's `mapped_model` returns `None` + "no mapping … hashing to the frozen model".**

Run (`probe34.py deleted`, model copy on xfs, unlinked 0.3 s after the server was ready; exit 0).
The maps row before the unlink is
`7f85…-7f85… r--s 00003000 103:05 1489165952 /fast/…/xfs-model/del/stories260K.gguf`, after it
`… /fast/…/xfs-model/del/stories260K.gguf (deleted)`. Live tool: `mapped:false,
reason:"model-path-not-in-maps"` — the maps pathname is compared as an exact string to
`os.path.realpath(model)` (`kama-llamacpp-live.py:696`, `:698-699`), and `" (deleted)"` breaks the
equality. Counter: `mapped_model` returns `None` and appends `no mapping of pid 601776 is a file
hashing to the frozen model (24 file mappings)` (`round50-replay-bind-audit.py:309-341`: it
`os.stat()`s each maps pathname, the deleted name no longer exists).

Verdict: fail-closed; a deleted mapping can never pass. Two notes: the reason token blames the
*path* for what is a deletion (a `model-path-deleted` token would be honest), and the replay's
refusal text (`kama-live-replay.py:343-348`) is then `model-mapping:model-path-not-in-maps`.

## 4. dev/inode mismatch (btrfs subvolume) — model on `/home`

**The preregistration's limit is real on this host: for a file under `/home` (btrfs subvol
`/@home`) `/proc/<pid>/maps` reports `00:1e` while `stat().st_dev` is `00:38`; the inode matches.
The live tool fails closed with `mapped-file-is-not-the-model-path`; the counter returns `None`.**

Run (`probe34.py btrfs /home/vgpnk/.cache/kama-r50-sen2proc/stories260K.gguf`, exit 0):

* `stat`: dev `00:38` (raw 56), inode `238239318`, size 1185376.
* maps: `… r--s 00003000 00:1e 238239318 /home/…/stories260K.gguf`; `/proc/self/mountinfo` line 23:
  `0:30 /@home /home … btrfs /dev/mapper/root … subvolid=257` — the maps dev is the superblock dev
  (0:30 = `00:1e`), the per-subvolume stat dev is the anonymous 0:38.
* live tool: `{"mapped": false, "reason": "mapped-file-is-not-the-model-path", "dev": "00:1e",
  "inode": "238239318", "path_dev": "00:38", "path_inode": "238239318"}`
  (`kama-llamacpp-live.py:710-713` rejects on the dev string though the inode is the same).
* counter: `mapped_model=None`, problem `no mapping of pid 604868 is a file hashing to the frozen
  model (24 file mappings)`; on xfs the same driver is the control: `mapped:true`, dev `103:05`,
  counter `("103:05","278841497")` (`probe34-xfs.json`).

Verdict: fail-closed, and consistent with the preregistered limit "on filesystems whose maps dev
differs from stat st_dev (btrfs subvolumes) the check fails closed. The counter's scratch is xfs."
But the counter neither pins nor records that assumption: it takes `--scratch` (or `TMPDIR`), and
the replay downloads the model into `S/work-<tag>/download` under it. Run with `--scratch` on
`/home` (btrfs), the live tool records `mapped:false` for every leg; the replay's mismatch branch
(`kama-live-replay.py:344-346`) then refuses with `model-mapping:mapped-file-is-not-the-model-path`,
so C1 would return `bind=0 … met=False` — a **false kill**, not `could-not-evaluate`. [INFERENCE:
the live-tool result and the mismatch branch are measured/read, the end-to-end `bind=0` was not run
with a btrfs scratch.] Today's invocation is safe
(operator scratch `/fast` is xfs; `/tmp` is xfs), but the instrument depends on its caller for
this.

## 5. Port stealing between the counter's check and its release

**A stranger on the observed port only ever flips the counter to fail; the one hole is the
opposite: a listener whose accept queue is saturated makes `port_refuses` return true (2.0 s
timeout treated as refusal) while the port is still LISTENing.**

Source: `round50-replay-bind-audit.py:200-218` (`listen_inodes`, loopback 127.0.0.1 and ::1),
`:251-260` (`port_refuses`: connect → false; **any** `OSError` → true), `:345-349` (exe + LISTEN and
the socket must be in the server's fd table), `:477` (post-release `pid_alive(pid) or not
port_refuses(port)`), `:513-521` (teardown `ok = not alive and refused and ready.pid in snap`).

Run (`probe5.py`, exit 0; all sockets in-process):

* stranger `listen(8)` on the port: `/proc/net/tcp` shows `0A` inode `704476636`,
  `counter_listen_inodes` = that inode, `port_refuses=false` in 0.003 s → the post-release check and
  the teardown leg append/fail (fail-closed).
* `SO_REUSEPORT` steal against the existing (non-REUSEPORT) listener: `EADDRINUSE` — a port cannot
  be taken over while the server owns it.
* saturated accept queue (`listen(0)`, 8 unaccepted connects): `/proc/net/tcp` still `0A`, but
  `port_refuses=true` after **2.002 s**, and the socket is still listening after the probe. So the
  counter's "port refuses" is forgeable by any local process holding the port with a full backlog;
  the process-death observations are independent of it, so no bind/teardown false pass follows, but
  the "port refuses" sub-claim can be false.
* control (nothing listening): `port_refuses=true` in 0.000 s.

Also noted: refusal is probed only on `127.0.0.1` while listener detection accepts `::1`; the live
tool always starts the server with `--host 127.0.0.1`, so this asymmetry is theoretical.

---

## Findings (severity, exploit path, evidence, impact, smallest remediation)

**F1 — `pid_alive` identity is jiffy-granular; `reap`/`killpg` are pid-addressed (Low).**
Exploit path: a process with CAP_SYS_ADMIN over the counter's pid namespace (or an abnormally small
pid space) forces a pid whose birth shares the snapshot entry's starttime tick, then `reap`'s
`os.kill(pid, SIGKILL)` (`:427-431`) or the `poll()`→`killpg` window (`:432-436`) hits the wrong
process; demonstrated: new process `rc=-9` under the counter's exact predicate
(`probe1-reuse.json`). Impact: wrong-target SIGKILL within the counter's uid; in the counter's own
tree the colliding member must have been born and killed in one tick, so this is not reachable
with today's long-lived replay/live/server members. Remediation: snapshot with
`os.pidfd_open(pid)` and use `select` on the pidfd for liveness and `signal.pidfd_send_signal` for
kills (reuse-proof by construction); as a stopgap, add the process `comm` and re-verify the pidfd.

**F2 — `port_refuses` classifies a connect timeout as "refuses" (Low).** `:251-260`. Any local
listener with a full accept queue (or a netfilter DROP) yields true in ~2 s while the port is
LISTENing (`probe5.json`). Impact: the "port refuses" clause of the bind/teardown verdicts can be
satisfied falsely; process death is checked independently, so there is no full false pass. Also,
each timeout burns 2 s inside the 30 s teardown loop (`:513-516`). Remediation: return true only on
`ConnectionRefusedError`; treat timeout/reset as "unknown → not refused", or decide from
`/proc/net/tcp{,6}` state `0A` for the same address family set used by `listen_inodes`.

**F3 — the measurement silently depends on the `--scratch` filesystem (Medium, for the run not the
instrument).** `mapped_model` (`:309-341`) and `model_mapping` (`kama-llamacpp-live.py:710-713`)
compare the maps dev string with `stat().st_dev`; on btrfs subvolumes these differ by encoding
(`00:1e` maps vs `00:38` stat, same inode), so a scratch on btrfs makes all three bind legs fail
and C1 returns `bind=0 met=False` — a false kill rather than `could-not-evaluate` (probe 4;
preregistration limits name the assumption; the `bind=0` consequence is [INFERENCE] from the
live-tool measurement plus `kama-live-replay.py:344-346`, not an end-to-end run). Impact: invocation-dependent verdict. Remediation
(smallest): after downloading its model, the counter `mmap`s it and compares the dev
`/proc/self/maps` reports with `stat().st_dev`; on mismatch print
`could-not-evaluate: scratch-maps-dev` (exit 2) and record the scratch mount. Optional stronger
fix for both sides: fstat/hash `/proc/<pid>/map_files/<start>-<end>` (the exact mapped file, works
for deleted files and carries its own dev+inode) instead of re-opening by pathname.

**F4 — the witness handshake carries no process identity and is not schema-checked (Low,
hardening).** `ready.json` is `{schema, port, pid, written_utc}` only (`kama-llamacpp-live.py:333-334`);
the guard at `:340` is a `poll()` and the publish at `:351` is not atomic with it; the counter's
`wait_ready` (`:408-415`) checks only the int types. Demonstrated: a ready.json naming a pid in
state `Z` at read, alive=false (`probe2b.json`, `probe2b-observe.json`). Impact: with today's legs the counter fails closed
(probe 2); the gap matters because the join "observed pid == rerun `child_pid`" (`:471-476`) is by
number, and a same-tick recycle (F1) or a planted file with the right shape is not distinguishable
by the handshake. Remediation: write the server's `starttime` (stat field 22) into ready.json, have
`wait_ready` require `schema == "kama-live-witness/v1"` and the starttime, and open a pidfd on the
announced pid before observing; the live tool should hold its own pidfd across the announce.

**Not re-reported** (already known): the two round-50 counters are not in SKILL.md's instrument
registry; SCORECARD/LOG/lesson/QUALITY/README entries are pending; S496/S497/S498 name
`corpus/lessons/round-50.md`; the gate registry reports the counters unregistered. I add nothing
there.

## What I did not run

I did not run the full C1 counter against the build (L1 owns the 46 s measurement and another seat
was already replaying the same three receipts from its own scratch while I probed; the 3 × ~75 MB
download would only duplicate it). My probes therefore do not confirm or contradict
`bind=1 teardown=1 newrow=1 met=True` at `97c864be`; they show that each observation the counter
relies on fails closed when the process behind it is gone, reused, deleted or path-aliased.

## Limits of this seat's evidence

* Same-tick reuse was forced with `ns_last_pid` inside `unshare -r -p -f --mount-proc`; that
  requires CAP_SYS_ADMIN over the pid namespace, which an ordinary host user does not have.
* The btrfs dev mismatch is a property of this host's btrfs subvolume mounts; it is exactly the
  case the preregistration's limit names.
* All live-tool runs in this seat used the b11909 install directly (`/home/vgpnk/.local/opt/
  llama-b11909/llama-server`, sha not recorded here) and the frozen model
  (`270cba1b…d256d`, 1,185,376 bytes); no server was left running.
