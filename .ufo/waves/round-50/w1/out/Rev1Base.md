# Rev1Base — round-50 attack-surface reconstruction (kama lane)

**Verdict: every round-49 cheat reproduces at the base commit exactly as its seat reported (base counter `met=True` on all three C1 cheats, the v4 tool silently ungrading all three C2 cheats), and the build closes each one by a mechanism I can name and show; but the round-50 C1 counter still admits a seventh cheat — a *fabricating replay* that runs the real b11909 server as its own child, scrubs the canary, writes `child_pid`/`model_mapping` itself and copies the captures — at `bind=1 teardown=1 newrow=1 met=True` in 15.7 s, so R1 is closed against the reported decoy shapes, not against a replay that lies.**

Round-50 build measured: `97c864bead3ee4a2f629574e77263d33834ec98a`; base: `26ecba64ad6fb571d09074b07202d1618a46ecd1`; round-49 build tip used for the base-counter reproductions: `74558c71c38ceaeace15fd4cf8aa9d84977584b1`. All runs were on one `git clone --shared` of the lane (`HEAD 3b79eadd` at the time), read-only toward the lane; every counter is a byte copy taken from git:

| file | source | sha256 |
|---|---|---|
| `r49c1.py` | `26ecba64:tools/round49-replay-witness-audit.py` | `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1` |
| `r50c1.py` | `97c864be:tools/round50-replay-bind-audit.py` | `ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89` (= preregistration C1 `counter_sha256`) |
| `r50c2.py` | `97c864be:tools/round50-append-audit-v5-check.py` | `925f07a48a02ad54a9c89230aac7e54c8dafee4ba2e8a823dcb851b9cf48ca46` (= preregistration C2 `counter_sha256`) |
| base replay | `26ecba64:tools/kama-live-replay.py` | `f615d9a0ee0402a59820ff47df2dbc44eb868ba1c28c4d4dedc108f901e16894` |
| base live tool | `26ecba64:tools/kama-llamacpp-live.py` | `0b31f8e6bd98f978c98e6029bfa322c37bac6ae09f9ebf4d770a3fe9ab88a3ba` |
| base append tool (v4) | `26ecba64:tools/append-only-audit.py` | `408aabc6906923d4bcc313ee3507f9b17202a837a47d0a78e62dba2da63f6a5e` |
| build replay | `97c864be:tools/kama-live-replay.py` | `d5c58972c0fd8f818b8dd2bd81f6cbc3a87c7f23b65805a804bf09b579a5a239` |
| build live tool | `97c864be:tools/kama-llamacpp-live.py` | `61e777b743aedb55c9532c4892d14a6cf0600f9f6f260595d635ec50ff708507` |
| build append tool (v5) | `97c864be:tools/append-only-audit.py` | `a3170a6fcbded95670e37750ab1ef72054e49ff83fc967e0c5f236ae10e205bd` |

Scratch: `S=/fast/scratch/hyaku/kama-r50/Rev1Base` (wiped below). Fixtures are one-commit repos built from the lane's own objects through `.git/objects/info/alternates` + `read-tree`/`update-index` (`mkfx.py`); a working-tree copy is impossible for these revisions (a round-36 seat left a recursively nested `.ufo/waves/round-36/w3/out/MutRowPipe/probe/.ufo/...` path that `shutil.copytree` cannot reproduce — the first attempt died with `shutil.Error`). `fixture-diffs.out` proves each fixture differs from its source commit in exactly one file:

```
== fx-decoy49 vs 74558c71…   tools/kama-live-replay.py | 564 +--…   1 file changed
== fx-setsid49 vs 74558c71…  tools/kama-live-replay.py | 634 +--…   1 file changed
== fx-decoy50 vs 97c864be…   tools/kama-live-replay.py | 665 +--…   1 file changed
== fx-setsid50 vs 97c864be…  tools/kama-live-replay.py | 735 +--…   1 file changed
== fx-fabricate50 vs 97c864be… tools/kama-live-replay.py | 700 +--… 1 file changed
```

---

## 1. Reproductions at the base commit (each cheat passes)

### A1 — decoy replay with copied receipt (K1Cheat attack 1; routed R1)

Artifact: `decoy-replay.py` (the round-49 seat's own file, copied byte-identical, sha256 `2b7bfcf4a11ef5ce0b53f5a86ad407727b56ec086e3ef905933596c6a4c4fb5f`). Fixture `fx-decoy49` = tree at `74558c71` with only `tools/kama-live-replay.py` replaced; fixture commit `06c9e6d18db6b123612c356b300723177aeb4d60`.

```
$ python3 $S/r49c1.py --repo $S/fx-decoy49 --tip 06c9e6d1… --scratch $S/s-a1base --out a1-base-decoy-copied-receipt.out
exit=0   (5.3 s)
witness=1 cap=1 newrow=1 witnessed=3/3 met=True
detail: witness w1: pid 523305 port 36641 exe+listen+model ok, nonce 'kama witness 6386f303c5ac36e7' round-tripped
detail: witness w2: pid 526527 port 48955 exe+listen+model ok, nonce 'kama witness bf95296b7b560a9b' round-tripped
detail: witness w3: pid 529791 port 32795 exe+listen+model ok, nonce 'kama witness 61b823ab953f50bf' round-tripped
```

The receipt the decoy wrote is the round-48 original with a `witness` block: `a1-standalone-copied-receipt.json` holds `child_pid 611093` (the round-48 pid) while the decoy's own witness was `pid 1877668` (`a1-standalone-ready.json`) — the counter never compared them. Base counter: `witness_one()` trusts `ready.json` (`26ecba64:tools/round49-replay-witness-audit.py:302-311`), reads the rerun receipt only for `witness.released` (`:323-326`), and `grep -c child_pid` over the file → **0**.

Build counter on the same cheat (fixture `fx-decoy50`, tree at `97c864be`, fixture commit `3afee6d115791d27e66b6bef975852bad1b9ad16`):

```
$ python3 $S/r50c1.py --repo $S/fx-decoy50 --tip 3afee6d1… --scratch $S/s-a1build
exit=1   (36.6 s incl. the 30 s teardown window)
bind=0 teardown=0 newrow=1 bound=0/3 met=False
detail: bind b1: server pid 919728 carries the planted KAMA_R50_CANARY
detail: bind b1: server parent pid 919442 carries the planted KAMA_R50_CANARY
detail: bind b1: rerun child_pid 611093 != observed pid 919728
detail: bind b1: rerun model_mapping None does not record the observed mapping ('103:05', '1149831972')
detail: teardown: invoker SIGKILLed with 2 descendants; after 30.05 s alive [931764, 932066] port ACCEPTS FAIL
detail: newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['| S496 |']
```

Closing mechanisms: rerun `child_pid` join (`tools/round50-replay-bind-audit.py:470-472`), `model_mapping` vs the counter's own `/proc/<pid>/maps` read (`:473-477`), the environment allow-list + canaries (`:376-393`) with `self-import` marker check (`:478-485`), and the allowed-list/`-I` spawn in the replay (`tools/kama-live-replay.py:88,113,307-332`).

### A2 — PYTHONPATH/sitecustomize hijack (K1Cheat attack 2; routed R1)

Artifact: `sitecustomize.py` (logs every import; execs the decoy when the starting interpreter is `kama-live-replay.py`). Pristine tree at `74558c71`, no lane file changed:

```
$ K1_DECOY=1 PYTHONPATH=$S/hijack K1_HIT_LOG=$S/hijack.log K1_DECOY_PATH=…/decoy-replay.py \
    python3 $S/r49c1.py --repo $S/lane --tip 74558c71… --scratch $S/s-a2base
exit=0   (5.4 s)
witness=1 cap=1 newrow=1 witnessed=3/3 met=True
```

`a2-base-sitecustomize.hijack.log` shows the hijack landing on the replay interpreter three times (and never on the live tool's witness path):

```
import pid=616305 was_replay=True argv=['…/tree/tools/kama-live-replay.py', '--receipt', '…/receipt-1.json', …
exec   pid=616305 was_replay=True argv=['…/tree/tools/kama-live-replay.py', …
import pid=616305 was_replay=False argv=['…/decoy-replay.py', …
… (same for receipt-2, pid 619786; receipt-3, pid 623447)
```

Base counter: `env = dict(os.environ)` (`round49-replay-witness-audit.py:431-435`) and `subprocess.Popen([sys.executable, <tree>/tools/kama-live-replay.py, …], env=env)` with no `-I` (`:297-298`), so the replay's interpreter imports the attacker's `sitecustomize` before any lane code runs.

Build, same hostile environment, pristine tree at `97c864be`:

```
$ K1_DECOY=1 PYTHONPATH=$S/hijack K1_HIT_LOG=$S/hijack.log K1_DECOY_PATH=…/decoy-replay.py \
    python3 $S/r50c1.py --repo $S/lane --tip 97c864be… --scratch $S/s-a2build
exit=0   (14.9 s)
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: bind b1: pid 2431230 port 45583 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 143511640 recorded, nonce … round-tripped
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
hijack log: one line, `import pid=2361516 was_replay=False argv=['…/r50c1.py', …]` — the counter's own interpreter
```

Closing mechanisms: the environment is built from `PASS_ENV` only with `PYTHONPATH` overwritten by the counter's own canary directory (`round50-replay-bind-audit.py:113-114,376-393`); the replay is started through a `python3 -I` invoker with the replay itself under `-I` (`:402-404`, `INVOKER` at `:114-115`); the replay launches the live child under `-I` with `LIVE_ENV_KEYS` only (`kama-live-replay.py:88,307-332`); the canary marker must stay empty (`:478-485`). This is the one closure whose *test* is a negative (no import line), not a failure line — the attack cannot reach the replay at all.

### A3 — double-fork + setsid (the "stranger" cheat)

Artifact: `decoy-setsid.py` (sha256 `352089555c8ea694d8c71a0f22d71211d953f11e7b61bd4f490e95c00feaf6ed`). The server is forked from a middle process that calls `setsid()` and exits, so the server's ppid is a subreaper outside the replay tree; the decoy additionally writes `child_pid` and a real maps-derived `model_mapping`, i.e. exactly the fields the build counter joins on. Standalone proof:

```
plain decoy : server 1877668 stat ppid=1877250 (the decoy)     ─ receipt child_pid 611093 (copied)
setsid decoy: server 1877678 stat ppid=1494    (not 1877258)   ─ receipt child_pid 1877678, model_mapping
              {'mapped': True, 'sha256': '270cba1b…', 'dev': '103:05', 'inode': '1543538341', …}
```

Base counter on `fx-setsid49` (commit `a26b09c632ffea1ec4aeb8f73a0af85da4c3d5e8`):

```
$ python3 $S/r49c1.py --repo $S/fx-setsid49 --tip a26b09c6… --scratch $S/s-a3base
exit=0   (5.8 s)
witness=1 cap=1 newrow=1 witnessed=3/3 met=True
detail: witness w1: pid 763780 port 50567 exe+listen+model ok, nonce … round-tripped
```

Base counter has no ancestry check at all — `ready["pid"]` is observed directly (`round49-replay-witness-audit.py:306-311`) and the replay's process tree is never read.

Build counter on `fx-setsid50` (commit `5c22e1007c6d81aaac7eeb641b421170107884f2`):

```
$ python3 $S/r50c1.py --repo $S/fx-setsid50 --tip 5c22e100… --scratch $S/s-a3build2
exit=1   (38.5 s)
bind=0 teardown=0 newrow=1 bound=0/3 met=False
detail: bind b1: server pid 1414444 does not descend from the replay process 1414012
detail: bind b1: server parent environ unreadable (pid 1494)
detail: teardown: announced pid 1435246 is not under the invoker
detail: teardown: invoker SIGKILLed with 1 descendants; after 30.04 s alive [1434951] port ACCEPTS FAIL
```

Closing mechanism: the ppid-chain leg, `descends_from(pid, replay_pid)` (`round50-replay-bind-audit.py:452-453`, helper `:297-310`). The second failure line is incidental, not designed: the reparent target on this host is a subreaper (pid 1494), whose `/proc/1494/environ` is unreadable, and the counter fails closed on an unreadable parent environ (`:345-350`). With a readable reparent target only the tree leg would fire — still enough, since the chain cannot pass *through* a subreaper to a descendant of the replay.

### A4 — a killed counter leaves the whole tree up (routed R2; X1Kill I2)

`r2-leak.py` reproduces the base counter's spawn shape exactly (`round49-replay-witness-audit.py:297-298,431-435`: `Popen` of the tree's replay with `env = dict(os.environ)` + HOME/XDG/TMPDIR, no `start_new_session`, no `preexec_fn`), waits for `ready.json`, then SIGKILLs the parent:

```
$ python3 $S/r2-leak.py $S/tree49 .ufo/waves/round-48/c2/live/receipt-1.json $S/r2 r2-leak-base.json
ready: server pid 2203865 port 39185; parent 2173856 descendants 3
  descendant 2173996 ppid 2173856 …/tree49/tools/kama-live-replay.py --
  descendant 2199997 ppid 2173996 …/tree49/tools/kama-llamacpp-live.py
  descendant 2203865 ppid 2199997 …/r2/work/server/llama-b11909/llama-server -m …
2 s after SIGKILL of the counter-shaped parent: alive [2173996, 2199997, 2203865] port ACCEPTS
cleanup: port refuses survivors []
```

Base replay has no `PR_SET_PDEATHSIG` of its own (`git show 26ecba64:tools/kama-live-replay.py | grep -c PR_SET_PDEATHSIG` → 0), so the replay survives its parent and holds the server until the witness timeout. Build closing mechanisms: replay self-pdeathsig (`kama-live-replay.py:100-110`, called at `:587`), live-child pdeathsig (`:332`), live-tool→server pdeathsig (`kama-llamacpp-live.py:661-676,1888`), and the counter's teardown leg that SIGKILLs the invoker and requires every descendant gone within 30 s plus a refusing port (`round50-replay-bind-audit.py:497-535`). Measured at the build: `after 0.10 s alive [] port refuses ok` (A2-build run above); the base control at `26ecba64` is `after 30.05 s alive [3206230, 3223128, 3226396] port ACCEPTS FAIL` (`c1-counter-base-control.out`, reproduced here, exit 1).

### B1 — fenced fake heading (K2Origin F4; routed R3)

Fixture: a `## Axes` line inside a fenced block, then 25 dated lines that are deleted.

```
fence base-v4 : exit=0 event={'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'}
fence build-v5: exit=1 event={'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'}
```

The base tool's `sections()` (`26ecba64:tools/append-only-audit.py:273-280`) takes any `## ` line as a title, including one inside a fence, so the dated lines are *born* under the fake exempt title and their origin becomes `## Axes`; the ungraded test at `:482-483` then exempts them. The build's `sections()` is fence-aware (`97c864be:tools/append-only-audit.py:306-323`, with `fence_open`/`fence_close` implementing CommonMark 0.31.2 §4.5), so the origin stays `## Round 1` and the deletion is graded (`:542-544`).

### B2 — CRLF laundering (K2Origin F5; routed R3)

25 dated LF lines are moved under `## Axes` with CRLF endings, then deleted there.

```
crlf-launder base-v4 : exit=1 event={'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'}
crlf-launder build-v5: exit=1 event={'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'}
```

Precisely: in v4 the *exit* is 1, but it comes from the earlier move event; the actual 25-line deletion is `graded 0 / ungraded 25`, i.e. the dated loss is hidden — the cheat works. All events, same fixture and contract:

```
v4 events: 5774e89e deleted 25 graded 25 ungraded 0 unrestored   (the CRLF move)
           089e6510 deleted 25 graded 0  ungraded 25 ungraded    (the deletion — hidden)
v5 events: 5774e89e deleted 25 graded 25 ungraded 0 unrestored
           089e6510 deleted 25 graded 25 ungraded 0 unrestored
```

v4's origin keys are byte-exact (`:445-447`, ungraded test `:482-483`), and the CRLF birth under `## Axes` becomes the origin. v5 normalises the key with one trailing CR dropped (`key()`, `97c864be:tools/append-only-audit.py:275-277`) and looks up `org.get(key(text), …)` (`:542-544`), so the origin is the LF birth under `## Round 1` and the deletion is graded.

### B3 — order flip (K2Origin F3; routed R3)

Identical trees, only the merge parents swapped (`[ca, cb]` vs `[cb, ca]`); the twin line is born under `## Axes` on branch A and under `## Round 1` on branch B.

```
order-a base-v4 : exit=0 event={'deleted': 25, 'graded': 0,  'ungraded': 25, 'status': 'ungraded'}
order-a build-v5: exit=0 event={'deleted': 25, 'graded': 0,  'ungraded': 25, 'status': 'ungraded'}
order-b base-v4 : exit=1 event={'deleted': 25, 'graded': 1,  'ungraded': 24, 'status': 'unrestored'}
order-b build-v5: exit=0 event={'deleted': 25, 'graded': 0,  'ungraded': 25, 'status': 'ungraded'}
```

v4's `origins()` takes the first blob in `git rev-list --topo-order --reverse` that holds the text (`26ecba64:tools/append-only-audit.py:431-449`), so the first-listed sibling decides whether the twin's origin is exempt; v5 computes the union over every *birth* (a commit holding the key while no parent does — `97c864be:tools/append-only-audit.py:480-500`), which is order-free, so both orders yield the same verdict.

### Counter-level confirmation (C2)

```
$ python3 $S/r50c2.py --repo $S/lane --tip 26ecba64…   exit=1
fixture=0 lane=1 scenarios=9/12 met=False
detail: scenario order-b: FAIL exit 1 (want 0)
detail: scenario fence: FAIL exit 0 (want 1)
detail: scenario crlf-launder: FAIL exit 1 (want 1) event={…'graded': 0, 'ungraded': 25…} want {…'graded': 25, 'ungraded': 0…}
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 82

$ python3 $S/r50c2.py --repo $S/lane --tip 97c864be…   exit=0
fixture=1 lane=1 scenarios=12/12 met=True
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 72 <= v5 natively exempt 72
```

This reproduces both committed controls (`controls/base.c2.out`, same three FAIL lines) and the measured `12/12`. It also shows the lane leg is powerless against these three cheats — at base it passed (`lane=1`) with the v4 tool: the lane leg's binder is the v4 rule and its bound is the v5 native count (`round50-append-audit-v5-check.py`, lane leg), so only the fixture legs detect F3–F5. That is the disclosed V2Ctr limit, now demonstrated.

---

## 2. Findings at the build (defects → exact line → command → proposed fix)

### F1 (major, C1) — a fabricating replay meets the round-50 counter: `met=True`, 15.7 s

The counter reads the rerun receipt only for `witness.released`, `child_pid` and `model_mapping` (`tools/round50-replay-bind-audit.py:464-477`); it never asks whether the live tool ran, and nothing it observes is tied to the captures the receipt carries. `decoy-fabricate.py` (sha256 `62e18bdd6b0bfeeeb170d99273ec6f51ab18ab498626f25374b9c1d844c9b971`) is a replay that:

1. re-execs itself with a clean environment, so neither it nor its server carries `KAMA_R50_CANARY` (`/proc/<decoy>/environ` and `/proc/<server>/environ` both canary-free; verified);
2. starts the real host b11909 server on the frozen model as **its own child** (ppid chain replay → server, so the `tree` leg passes), with `PR_SET_PDEATHSIG` on both itself and the child;
3. holds for the witness, tears the server down on release, and writes a rerun receipt that is the round-48 original with only `child_pid`, `port`, `witness` and `model_mapping` set to what the counter observes.

```
$ python3 $S/r50c1.py --repo $S/fx-fabricate50 --tip eefeb37c197e79d7b0da108b47c93767b86c634b --scratch $S/s-fab
exit=0   (15.7 s)
bind=1 teardown=1 newrow=1 bound=3/3 met=True
detail: bind b1: pid 141654 port 59299 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1149817196 recorded, nonce … round-tripped
detail: bind b2: pid 144612 … mapping dev 103:05 inode 1149817196 recorded …
detail: bind b3: pid 149303 … mapping dev 103:05 inode 1149817196 recorded …
```

The receipt is provably not a fresh rerun (`a5-standalone-fabricated-receipt.json` vs the round-48 original): `captures`, `checks` and `provenance` are byte-identical, `started_utc`/`ended_utc` are still `2026-10-26T22:26:23.509Z`/`…879Z`, and during the hold **no `kama-llamacpp-live.py` process exists** (`live tool processes during the hold: []`). The same inode (`1149817196`, the counter's single `counter-model.gguf`) across all three legs is the only tell, and it is forgeable by copying the model per work dir.

Proposed fix (six lines in `bind_one`, after `ready` is read, `round50-replay-bind-audit.py:441-454`): require the announced pid's **parent** to be this tree's isolated live tool, and that tool's parent to be the replay —

```python
pst = stat_fields(pid)
parent = pst[1] if pst else None
if parent is None or not descends_from(parent, rp) or b"kama-llamacpp-live.py" not in open(
        f"/proc/{parent}/cmdline", "rb").read():
    probs.append(f"server parent {parent} is not an isolated kama-llamacpp-live.py under the replay")
```

Verified against an honest run of the build tree (`$S/sah`, receipt-1): server 486507 → parent 483340 `python3 -I …/tree50/tools/kama-llamacpp-live.py …` → grandparent 462756 the replay, so the check has no false positive on the measured path; the fabricating decoy fails it by construction (its server's parent is the decoy replay itself, `a5-standalone-ready.json` run: parent cmd `/usr/bin/python3 …/decoy-fabricate.py`). A cheaper companion check: `model_mapping.path` must lie under the replay's work dir (honest: `…/work/download/stories260K.gguf`; this decoy: the counter's shared `counter-model.gguf`).

Residual (do not overclaim the fix): a forger that also starts the live tool with a pre-downloaded archive defeats a provenance-of-process check too. The receipt is written by the process under test, so the only sound end state is to move trust from the receipt to observations the counter makes itself (e.g. issue the captured surfaces' requests — `/health`, `/props`, `/slots`, `/models`, `/metrics` — and compare body digests with the receipt's captures), or to make the replay's record-time inputs (archive, model) session-specific. `[INFERENCE]` on the exact residual attack cost; the demonstrated one is real and measured.

### F2 (medium, C1 teardown) — the promised survivor kill cannot reach a reparented server

`tools/round50-replay-bind-audit.py:64` says "The counter kills any survivor afterwards"; `reap()` (`:425-435`) kills only descendants of the invoker plus the snapshot, and the setsid server is not a descendant. Observed: after the A3-build run the counter had exited and a server was still listening —

```
$ python3 $S/r50c1.py --repo $S/fx-setsid50 --tip 5c22e100… --scratch $S/s-a3build2
… detail: teardown: invoker SIGKILLed with 1 descendants; after 30.04 s alive [1434951] port ACCEPTS FAIL
--- post-counter leftover scan:
LEFTOVER pid 648094 cwd /fast/scratch/hyaku/kama-r50/Rev1Base/s-a3build2/r50c1-t41pug_6/tree (deleted)
```

The leg itself is fail-closed (correct verdict), but the leftover is an operator leak: a loopback listener outlives the counter. Proposed fix: in the `teardown_leg` finally, when `ok` is false (or the port still accepts), resolve the LISTEN socket inode for the announced port from `/proc/net/tcp{,6}` and find the owning pid by scanning `/proc/<pid>/fd` (the counter already has both helpers, `listen_inodes`/`pid_socket_inodes`), then SIGKILL that pid. ~8 lines; no effect on the honest path (port refuses, nothing to kill).

### F3 (low, claim wording) — the canary proves non-inheritance, not honesty

`descends_from`+canary+join are all satisfiable by a replay that sanitises its own environment and writes its own fields (A3 and F1 did exactly that: `server environ canary: False | parent environ canary: False`). The load-bearing environment closure is the counter's allow-list and the two `-I` flags (A2-build), not the canary. The preregistration predicate's phrase "free of the canaries" is therefore weaker than it reads. Suggested wording for round 51: "the replay does not hand the counter's environment to any interpreter it starts", with the canary as the instrument and `-I`/allow-list as the mechanism.

### F4 (low, C1) — join and `model_mapping` are correspondence, not authenticity

My setsid decoy wrote `child_pid` equal to the observed pid and a real maps-derived `model_mapping` and passed those two legs; only the `tree` leg caught it. So the join closes the *specific* round-49 decoy (which copied `child_pid` verbatim, measured: `611093 != observed pid`) but adds no resistance to a replay that lies consistently. This is the mechanism that makes F1 possible; F1's fix is the one that matters.

---

## 3. Mechanism map (what closes what)

| Cheat | Base behaviour (this run) | Build mechanism (file:line) | Build behaviour (this run) |
|---|---|---|---|
| decoy replay + copied receipt | `met=True`, 5.3 s | rerun `child_pid` join `round50-replay-bind-audit.py:470-472`; `model_mapping` vs own maps read `:473-477`; allow-list env `:376-393`; replay isolated `kama-live-replay.py:307-332`; live tool records mapping `kama-llamacpp-live.py:678-726,2003` | `bind=0`, three named failures |
| sitecustomize hijack | `met=True`, 5.4 s | `PASS_ENV` + own `PYTHONPATH` `:113-114,376-393`; `python3 -I` invoker and `-I` replay `:402-404`; replay's `-I`/`LIVE_ENV_KEYS` live child `kama-live-replay.py:88,307-332`; empty marker `:478-485` | `met=True` honestly, hostile module never imported by the replay |
| double-fork + setsid | `met=True`, 5.8 s | `descends_from(pid, replay_pid)` `:452-453` (+ incidental fail-closed parent-environ `:345-350`) | `bind=0`, `does not descend` |
| killed counter | replay+live+server alive, port accepts | replay self-pdeathsig `kama-live-replay.py:100-110,587`; live-child pdeathsig `:332`; live→server pdeathsig `kama-llamacpp-live.py:661-676,1888`; counter teardown `:497-535`, `start_new_session` `:404` | `after 0.10 s alive [] port refuses ok` |
| fenced fake heading | v4 exit 0, 25 dated lines ungraded | fence-aware `sections()` `append-only-audit.py:306-323` | exit 1, `graded 25` |
| CRLF laundering | v4 deletion event ungraded 25 | `key()` CR-strip `append-only-audit.py:275-277`, test `:542-544` | exit 1, `graded 25` |
| order flip | v4 exit 0 vs 1 on identical trees | birth-union `origins()` `append-only-audit.py:480-500` | both orders exit 0, `ungraded 25` |
| **fabricating replay (new)** | n/a | **none** — receipt trust is total `:464-477` | **`met=True` (F1)** |

## 4. Operability notes and limits

- The reparent target on this host is a subreaper (pid 1494), not init; a `setsid` escape therefore still fails the tree leg (the chain cannot pass through the subreaper into the replay) and additionally fails the parent-environ read closed. `[INFERENCE]` on hosts without such a subreaper the ppid would be 1 and only the tree leg would fire — same verdict.
- The base counter leaves its scratch behind only on hard kill (its `finally` removes `S`), and the build counter's scratch is removed on every exit; the A3-build leftover process had a `(deleted)` cwd.
- No tool was installed or upgraded (no pacman; stdlib only). `pgrep -af 'kama-r50/Rev1Base'` is empty after every run; the only `llama-server` processes seen were peers' (`Sen3Teardown`), untouched. `$S` deleted before delivery.

## 5. Reproduction commands

```sh
S=/fast/scratch/hyaku/kama-r50/<seat>; mkdir -p "$S"; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
R=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Rev1Base
# counters, byte copies of the frozen blobs
git -C "$S/lane" show 26ecba64:tools/round49-replay-witness-audit.py > "$S/r49c1.py"
git -C "$S/lane" show 97c864be:tools/round50-replay-bind-audit.py > "$S/r50c1.py"
git -C "$S/lane" show 97c864be:tools/round50-append-audit-v5-check.py > "$S/r50c2.py"
# fixtures: one-commit repos, the lane tree with tools/kama-live-replay.py replaced
python3 "$R/mkfx.py" "$S/lane" 74558c71c38ceaeace15fd4cf8aa9d84977584b1 "$S/fx-decoy49" tools/kama-live-replay.py "$R/decoy-replay.py"
python3 "$R/mkfx.py" "$S/lane" 74558c71c38ceaeace15fd4cf8aa9d84977584b1 "$S/fx-setsid49" tools/kama-live-replay.py "$R/decoy-setsid.py"
python3 "$R/mkfx.py" "$S/lane" 97c864bead3ee4a2f629574e77263d33834ec98a "$S/fx-decoy50" tools/kama-live-replay.py "$R/decoy-replay.py"
python3 "$R/mkfx.py" "$S/lane" 97c864bead3ee4a2f629574e77263d33834ec98a "$S/fx-setsid50" tools/kama-live-replay.py "$R/decoy-setsid.py"
python3 "$R/mkfx.py" "$S/lane" 97c864bead3ee4a2f629574e77263d33834ec98a "$S/fx-fabricate50" tools/kama-live-replay.py "$R/decoy-fabricate.py"
# A1-A3 base (r49 counter), 5-6 s each
python3 "$S/r49c1.py" --repo "$S/fx-decoy49"  --tip 06c9e6d18db6b123612c356b300723177aeb4d60 --scratch "$S/s-a1" --out a1.out
python3 "$S/r49c1.py" --repo "$S/fx-setsid49" --tip a26b09c632ffea1ec4aeb8f73a0af85da4c3d5e8 --scratch "$S/s-a3" --out a3.out
K1_DECOY=1 PYTHONPATH="$S/hijack" K1_HIT_LOG="$S/hijack.log" K1_DECOY_PATH="$R/decoy-replay.py" \
  python3 "$S/r49c1.py" --repo "$S/lane" --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --scratch "$S/s-a2" --out a2.out
# A1/A3/A5 build (r50 counter)
python3 "$S/r50c1.py" --repo "$S/fx-decoy50"     --tip 3afee6d115791d27e66b6bef975852bad1b9ad16 --scratch "$S/s-b1" --out b1.out
python3 "$S/r50c1.py" --repo "$S/fx-setsid50"    --tip 5c22e1007c6d81aaac7eeb641b421170107884f2 --scratch "$S/s-b3" --out b3.out
python3 "$S/r50c1.py" --repo "$S/fx-fabricate50" --tip eefeb37c197e79d7b0da108b47c93767b86c634b --scratch "$S/s-b5" --out b5.out
# R2 leak at base
python3 "$R/r2-leak.py" "$S/tree49" .ufo/waves/round-48/c2/live/receipt-1.json "$S/r2" r2.json
# C2: fixtures against both tool trees (extracted with `git -C lane archive <c> | tar -x -C <dir>`), and the counter at both tips
python3 "$R/c2-fixtures.py" "$S/r50c2.py" "$S/c2fx" "base-v4=$S/tree26" "build-v5=$S/tree50"
python3 "$S/r50c2.py" --repo "$S/lane" --tip 26ecba64ad6fb571d09074b07202d1618a46ecd1 --scratch "$S/c2a" --out c2base.out
python3 "$S/r50c2.py" --repo "$S/lane" --tip 97c864bead3ee4a2f629574e77263d33834ec98a --scratch "$S/c2b" --out c2build.out
```

`sitecustomize.py` was staged as `$S/hijack/sitecustomize.py` for A2; `$S/tree49`, `$S/tree26` and `$S/tree50` are `git archive` extractions of `74558c71`, `26ecba64` and `97c864be`; fixtures were built by `mkfx.py`, which borrows the clone's objects through `.git/objects/info/alternates` (no working-tree copy).

## 6. Written here

- `a1-base-decoy-copied-receipt.out`, `a1-build-decoy-copied-receipt.out`, `a1-standalone-copied-receipt.json`, `a1-standalone-ready.json`
- `a2-base-sitecustomize.out`, `a2-base-sitecustomize.hijack.log`, `a2-build-sitecustomize.out`
- `a3-base-setsid.out`, `a3-build-setsid.out`, `a3-build-setsid-console.out`, `a3-standalone-setsid-receipt.json`, `a3-standalone-ready.json`
- `a5-build-fabricating-replay.out`, `a5-standalone-fabricated-receipt.json`, `a5-standalone-ready.json`
- `c1-counter-base-control.out`, `c2-counter-base.out`, `c2-counter-build.out`, `c2-fixtures.out`, `fixture-diffs.out`
- `r2-leak-base.out`, `r2-leak-base.json`, `decoy-replay.py`, `decoy-setsid.py`, `decoy-fabricate.py`, `sitecustomize.py`, `mkfx.py`, `c2-fixtures.py`, `r2-leak.py`
