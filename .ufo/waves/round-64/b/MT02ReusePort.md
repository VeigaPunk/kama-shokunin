# MT02ReusePort — round 64, wave b, C1 falsification: second listener on the run port

Seat: MT02ReusePort (leaf). Tip under test: `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a` (frozen; base `0c1eff3c`).
Counter: `tools/round64-c1-counter.py` as committed at the tip, unmutated except the clone-only mutant M1.
Scratch clone (removed after evidence copied): `/fast/scratch/hyaku/kama-r64/b/MT02ReusePort/clone`.
Evidence: `.ufo/waves/round-64/b/out/MT02ReusePort/` (outputs, receipts, patch, observer, bind experiment).

## Verdict

1. **Literal attack: not buildable.** A SO_REUSEPORT listener on `127.0.0.1:P` beside the pinned child fails with
   EADDRINUSE; in reverse order the child exits. The pinned `llama-server` does not set SO_REUSEPORT. Variant V0
   (forger tries the bind, otherwise honest): **not a survivor — met=True 76/76**, nothing installed.
2. **Functional equivalent: works.** A forger takes the child's own listening fd with `pidfd_getfd` and accepts on
   that socket, so the kernel splits probes between child and forger (measured 7 of 20 probes answered by the
   canned forger, observer V4).
3. **SURVIVED — root-owned holder with forwarder (V3).** A helper started with `sudo -n` dups the child's listener and
   forwards each request to a second pinned llama-server. The live predicate **accepts** it: `live_ok=1/1` in both
   receipt-producing counter runs (V3, V3-rep2), and the observer run (V3b) shows the holder set is the child alone
   with 20/20 real answers and `REQUEST_OK`. **No check decides.** The holder-set check skips the helper (its
   `/proc/<pid>/fd` raises PermissionError and its `/proc` owner is root, so it is recorded neither as a holder nor
   as unreadable). The reference-agreement check passes because the forwarder's answers are the pinned server's.
   The printed `met=False` is not a detection: the round-63 `forge` controls produce no receipt on this modified
   tip tool (section 5). The decisive line is `live_ok=1/1`.
4. **Same-uid forgers are caught.** Dumpable same-uid holder (V1, V5): holder-set check (`bind_holders`,
   `bind_claim`). Non-dumpable same-uid holder (V2, V6): holder-set fail-closed branch (`unreadable_own` →
   `bind_holders` alone).
5. **Canned root answerer (V4)** escapes in 1 of 4 receipt-producing runs; the other 3 are rejected by reference and
   answer-shape checks. The holder set is blind in all four.
6. **Counter-side fix, clone-only (M1):** dropping the own-uid gate in `holder_pids` kills the root survivor on
   `bind_holders` alone; the unforged base tip still prints `met=True` 76/76 (M2, one run). Not committed; a
   counter change needs a numbered AMENDMENT before wave f.

| Variant | Forger | Holder set seen by counter | Decider |
|---|---|---|---|
| V0 | SO_REUSEPORT on 127.0.0.1 | bind refused | none; no forgery installed (met=True) |
| V1 | same-uid dup + forwarder, dumpable | child + tool | holder-set: `bind_holders`, `bind_claim` |
| V2 | same-uid dup + forwarder, non-dumpable | child; tool unreadable | holder-set fail-closed: `bind_holders` alone |
| V3 | **root** dup + forwarder | **child only** | **none — SURVIVED** (live_ok=1/1) |
| V4 | root dup, canned | child only | answer checks (`live_text`, `live_ref_text`, `live_ref_usage`, `live_object`, `live_ptok`), 3/4 |
| V5 | `::1` listener, dumpable | child + tool | holder-set: `bind_holders`, `bind_claim` |
| V6 | `::1` listener, non-dumpable | child; tool unreadable | holder-set fail-closed: `bind_holders` alone |
| V7 | `127.0.0.2` listener, dumpable | child + tool | `bind_listener` (address class), plus holder-set |
| M1 | counter mutant on V3 | root helper counted unreadable | holder-set: `bind_holders` alone (KILLED) |

Reference-agreement decides only in V4 (probabilistic, answer checks). Holder-set decides V1, V2, V5, V6, V7 and M1.
Nothing decides V3.

## 1. Kernel facts (`out/MT02ReusePort/bind-experiments.txt`, real pinned b11755 server, fresh port per case)

```
child-then-reuseport-127.0.0.1 : 127.0.0.1 SO_REUSEPORT beside pinned child: EADDRINUSE Address already in use
reuseport-first-then-child     : forger REUSEPORT bound first; child rc = 1
child-then-127.0.0.2           : v4 127.0.0.2 BIND OK; 127.0.0.1 health still {"status":"ok"}
child-then-::1                 : v6 ::1 BIND OK; 127.0.0.1 health still {"status":"ok"}
```

Consequences: the counter probes `127.0.0.1` only, so `::1` and `127.0.0.2` listeners are never probed and matter
only through the holder set. A same-host second acceptor must share the child's socket, i.e. hold a duplicate of its
fd. `pidfd_getfd` is allowed here (Yama ptrace_scope=1, forger's own child, dumpable child).

## 2. Forged tool (what was built)

One knob-driven block in `tools/kama-completion-live.py` of the scratch clone. Final root variant as a patch vs the
tip: `out/MT02ReusePort/forge-root-forward.patch` (271 lines, mostly the helper source). Knobs: `FORGE_NET`
(`reuseport` | `dup` | `rootdup` | `::1` | `127.0.0.2`), `FORGE_NONDUMP` (`prctl(PR_SET_DUMPABLE,0)`),
`FORGE_ANSWER` (`forward` to a second pinned llama-server the tool starts, or `canned` constant `{"status":"ok"}`).
Hook points: after the tool's own `listener_holders_pinned` scan (so the receipt names only the child), before the
hold window; stop before teardown. Variant commits in the clone: V1 `2358e293`, V2 `64931e0b`, V3 `7b7a9eb3`,
V4 `610c4a94`, V0 `d26011e1`, V5 `dd072c6f`, V6 `dc70b10a`, V7 `425fd45f`. Each scored by the unmutated counter:
`python3 <clone>/tools/round64-c1-counter.py --repo <clone> --tip <commit> --work <scratch>/work/<V>`.

**Minimal edit for the survivor (V3):** (a) start a second pinned llama-server on another loopback port (the
forwarding upstream); (b) start `sudo -n python3 helper.py <child_pid> <port> <upstream> <stopfile> <readyfile>
forward`; the helper calls `pidfd_open(child)`, `pidfd_getfd(pidfd, <child's LISTEN fd>)` (syscall 438), and serves a
forwarder on that socket; (c) stop the helper via stop-file, then the upstream, before the tool's SIGTERM.

## 3. Observed procfs state of the survivor (observer V3b; `out/…/observer-V3b-rootdup-forward.txt`)

```
listeners(35457) = [(1879429083, True)]                      # one inode
holder_pids = [2059502] unreadable_own_uid = [1500, 2911361] # only the child; helper absent from both
  holder pid=2059502 exe=…/llama-server exe_sha=b6a31a8e9761 ...
forge-helper pid=2060954 owner_uid=0 me=1000 fd_table=NOT readable (Permission denied) in_holder_pids=False in_unreadable_own=False
forge-helper pid=2061073 owner_uid=0 me=1000 fd_table=NOT readable (Permission denied) in_holder_pids=False in_unreadable_own=False
ss -ltnp :35457 -> users:(("llama-server",pid=2059502,fd=3))  # ss attributes the port to the child alone
20x POST /tokenize answered by: {'canned {"status":"ok"}': 0, 'real tokenize': 20, 'error': 0}
receipt verdict=REQUEST_OK ... listener_holders=[{... 'pid': 2059502}];  tool exit rc=0; listeners after exit = []
```

**The procfs observation that decides V3 is an absence.** `holder_pids` records a pid as a holder only when it reads
`/proc/<pid>/fd` and finds the inode; it records a pid as unreadable only when that read fails AND
`os.stat('/proc/<pid>').st_uid == os.getuid()`. The helper's read fails with EACCES and its `/proc` owner is 0, so it
is in neither set and never reaches `bind_holders`. The counter's only fail-closed branch is same-uid
(`holder_pids` → `collect()` `unreadable_own` → `grade_binding()` `bind_holders`).

## 4. Counter results (one-liners, verbatim up to elided family detail)

Baseline (unforged tip):
```
tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 … witness=5/5]
```

KILLED — same-uid dumpable forger, V1 (`dup`, forward):
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 … errors=1 met=False families[]
error: live: ["bind_ancestry", "bind_argv", "bind_claim", "bind_exe", "bind_holders", "bind_maps"]
```

KILLED — same-uid non-dumpable forger, V2 (`dup`, forward, `prctl`):
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 … errors=1 met=False families[]
error: live: ["bind_holders"]
```

V0 — literal SO_REUSEPORT attempt, bind refused, honest otherwise (`forge-bind.err`: `[Errno 98] Address already in use`):
```
tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[… forge=3/3 …]
```

KILLED — `::1` dumpable (V5): `error: live: ["bind_ancestry", "bind_argv", "bind_claim", "bind_exe", "bind_holders", "bind_maps"]`
KILLED — `::1` non-dumpable (V6): `error: live: ["bind_holders"]`
KILLED — `127.0.0.2` dumpable (V7): `error: live: ["bind_ancestry", "bind_argv", "bind_claim", "bind_exe", "bind_holders", "bind_listener", "bind_maps"]`
(each with `tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 … met=False families[]`)

**SURVIVED — root-owned holder + forwarder (V3), first run:**
```
tool_present=1 live_ok=1/1 controls_targeted=74/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[… forge=1/3 …]
error: forge forgeA: no receipt/witness []     error: forge forgeA2: no receipt/witness []
```
**SURVIVED — V3-rep2 (same commit), the exact line:**
```
tool_present=1 live_ok=1/1 controls_targeted=74/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=2/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=0/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
```
V3-rep1 (same commit) gave `live: no receipt/witness produced` (helper teardown hang, section 6.1): neither escape nor detection.

**V4 — canned root answerer, six counter runs at `610c4a94`:**
```
run1 live_ok=1/1  ESCAPE (all probe connections reached the child; receipt present)
run2 live_ok=0/1  live: no receipt/witness produced        (teardown hang; not a detection)
run3 live_ok=0/1  live: [live_created, live_fp_capture, live_fp_shape, live_model, live_object, live_ptok, live_ref_text, live_ref_usage, live_run_field, live_text]
run4 live_ok=0/1  live: no receipt/witness produced        (teardown hang; not a detection)
run5 live_ok=0/1  live: [live_created, live_fp_capture, live_fp_shape, live_model, live_object, live_ptok, live_ref_text, live_ref_usage, live_run_field, live_text]
run6 live_ok=0/1  live: [live_created, live_fp_shape, live_model, live_object, live_ptok, live_ref_text, live_ref_usage, live_run_field, live_text]
```
Observer V4: `20x POST /tokenize … {'{"status":"ok"}': 7, real: 13}`. Escape 1/4 receipt-producing runs (small N;
an unbroken pass at a 65/35 split predicts about 0.18, consistent).

**M1 (clone-only counter mutant: `holder_pids` gate `if os.stat(...).st_uid == me:` → `if True:`) on the committed V3 tool:**
```
tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=['bind', 'canned', 'detach', 'digest', 'forge', 'hdr', 'hold', 'idcr', 'listener', 'log', 'outside', 'pathcopy', 'predead', 'preload', 'proxy', 'ptok', 'relabel', 'reqbind', 'runfield', 'schema', 'shape', 'sigterm', 'stale', 'stalehold', 'tamper', 'timing', 'trunc', 'witness'] eval_selftest=0/3 errors=1 met=False families[]
error: live: ["bind_holders"]
```
M2 (same mutant, unforged base tip): `tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 … met=True`.

## 5. What V3 does and does not show

- It is a live-predicate acceptance. The forged run passes every `bind_*`, `hold_fresh`, `bind_claim` and
  `teardown_observed` check, and every probe check including reference agreement (the forwarder returns the
  pinned server's own text, usage and fingerprint).
- `met=False` is a side effect of editing the tip tool. The round-63 patches (forgeA/forgeA2/forgeB2, relabel) apply
  to whatever tool is at `--tip`; with the root-helper branch active inside it, forgeA yields no receipt, and a
  family that cannot run is not credited. This is a counter fragility (section 6.3), not a detection.
- It needs root (`sudo -n`, passwordless on this host). Under a same-uid threat model the survivor does not exist
  (V1, V2, V5, V6 are caught). Whether root-owned holders are in the C1 threat model is a decision for L1; the
  predicate says "every holder", and that is false here.

## 6. Operability observations (for L1)

1. **Helper teardown hang (my forger, not the counter).** The helper ignored its stop file in several runs (observer
   runs V3-rootdup-forward and V4-rootdup-canned; forgeA/forgeA2 scenario runs). I cleared them with
   `sudo -n kill -TERM` on my own pids. It exited normally in V3, V3b, V3-rep2. A hung tool writes no receipt; those
   runs count as neither escape nor detection (V3-rep1, V4 run2, V4 run4).
2. **Host-noise flake source.** Same-uid non-dumpable processes exist on this host (other seats' `helper.py` pids
   1293346, 1618428; 1Password's browser helper). `collect()` records a same-uid unreadable pid as `unreadable_own`
   only if it started at or after the tool; one such process starting inside a counter window fails `bind_holders`.
   My baseline runs were not affected (those pids predate the tool).
3. **Forge family depends on the tip tool's text.** Observed: V3 `forge=1/3`, V3-rep2 `forge=2/3`, V4 run1 `forge=0/3`.
   In V4 run1 forgeA was rejected by `bind_holders` but with 16 failing checks, above `SCENARIO_CAP=14`, so the
   rejection was not credited: collateral cap is a second fragility.
4. **Holder check is uid-gated.** M1 (ungated) kills the root survivor and keeps the base at 76/76 in one run. It
   changes behaviour on a busy host (any unreadable pid started in-window fails), so it needs an AMENDMENT and a
   host-noise soak before adoption. Not committed.

## 7. Method, tools, privilege

- Clone recipe followed; all edits in the scratch clone; commits only there; no lane, fleet, sibling or shokuknow file
  touched. Ports: loopback `bind(0)` only; 8080 and 34113 not used.
- Tools: none installed or upgraded. Present: python3 3.14.8 (system), `ss` (iproute2), `ps`.
- Privilege: `sudo -n` to start the root helper (V3/V4 runs) and `sudo -n kill -TERM` on my own helper pids. Nothing else.
- Written outside scratch: only this report and `out/MT02ReusePort/` (observer, bind experiment, patch, receipts).

## 8. Limits

- V4 was not run through M1; it is expected to die on `bind_holders` before the answer checks [INFERENCE, not run].
- No rebuilt SO_REUSEPORT llama-server was built; its digest would fail `bind_exe`/`server_digest` [INFERENCE from code].
- The helper teardown hang is observed, not root-caused; no verdict above depends on it.
- Sample sizes are small (V3: 2 counter + 1 observer; V4: 4 receipt-producing counter runs).

Counter one-liner for the survivor (V3-rep2, unmutated counter, tip `7b7a9eb3`):

`tool_present=1 live_ok=1/1 controls_targeted=74/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False`

Counter one-liner for the same forgery with the holder gate removed (M1, clone-only mutant):

`tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 … eval_selftest=0/3 errors=1 met=False` / `error: live: ["bind_holders"]`
