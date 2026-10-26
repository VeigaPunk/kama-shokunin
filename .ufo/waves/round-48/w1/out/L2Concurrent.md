# L2Concurrent — round 48 (lane kama, C2 operability): concurrent v5 replay

**Verdict: hypothesis survives — 24 concurrent/parallel v5 replays of `receipt-1.json` in separate
`--work` dirs: all 24 exited 0 with `match=True`, used 24 distinct ports, every rerun proved
`port_listener_ownership=child` with `teardown.returncode=0` and `port_refuses=true`, and left no
child process and no listener behind. No lane defect found; two observability caveats recorded
below (not defects, no lane change proposed).**

Hypothesis under test (seat L2Concurrent, frozen wording):
> two v5 replays of the same receipt started at the same moment in separate `--work` dirs both
> exit 0 with `match=True` and leave no listener and no child behind.

Content tested: `tools/kama-live-replay.py` and `tools/kama-llamacpp-live.py` are byte-identical at
lane HEAD `b85783e889c261ff870da65d091ff1014ffe7c10` and at the build commit
`380bcdff9c8af06997c482f6eb03db926a794a2b` (`git diff --stat 380bcdff HEAD -- tools/ registry/`
→ empty; `git show 380bcdff:tools/kama-live-replay.py | sha256sum` =
`69837013ec64b78a192e91b5b6a604a7437890c9e5a9c21dd175a0e87eb8b15f` = the file I ran). So this
evidence is evidence about the build, not about the later wave-spec commit.

## Commands (all from scratch `$S=/fast/scratch/hyaku/kama-r48/L2Concurrent`, `export TMPDIR=$S`)

Receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/c2/live/receipt-1.json`
(schema `kama-llamacpp-live/v5`, outcome `pass`, 11/11 evaluated checks passed, model commit
`499bc8821c6b12b4e53c5bffcb21ec206f212d81`, asset `bf94332a…695b`, model `270cba1b…256d`).

    1  python3 …/tools/kama-live-replay.py --receipt <R> --work $S/wA  --out $S/a.json   &   # pair 0
    2  python3 …/tools/kama-live-replay.py --receipt <R> --work $S/wB  --out $S/b.json   &
      wait
    3  for i in 1..5: same two commands concurrently with --work $S/p$i/wiki | $S/p$i/wikj   # pairs 1-5
    4  four processes concurrently: --work $S/q1 … $S/q4                                     # four-way
    5  8 processes concurrently:   --work $S/m0 … $S/m7                                      # eight-way

Each replay re-acquires both artifacts from https and re-hashes them before running
(`kama-live-replay.py:218-219` with `acquire` at `:126-131`), verifies the archive member digest before executing it
(`:222-230`), sets `TMPDIR=<work>/tmp` for the live run (`:233`) so the live tool's `mkstemp`
server log (`kama-llamacpp-live.py:1625`) and its atomic receipt publish (`:1418`) stay inside that
work dir, and lets the live tool pick a fresh loopback port (`pick_port`, `kama-llamacpp-live.py:391`).
No file outside `--work`/`--out` is written by either tool (grep for `expanduser|HOME|.cache|flock`
in the live tool: only `CHILD_ENV_KEYS` carries `HOME`).

## Evidence

### 1. Simultaneous pair (the literal hypothesis), exit codes and logs

    === A ===  replay match=True refused=None mismatches=0 exit=0      A_EXIT=0
    === B ===  replay match=True refused=None mismatches=0 exit=0      B_EXIT=0

    A rerun: port 38195 pid 1436015 outcome pass ownership child teardown rc 0 port_refuses True
    B rerun: port 45559 pid 1435996 outcome pass ownership child teardown rc 0 port_refuses True
    A/B inputs: archive_sha256 bf94332a…695b, model_sha256 270cba1b…256d (both, freshly fetched)
    rerun provenance.verified: {"at":"record","archive_sha256":bf94332a…,"member_sha256":35ac50fb…,
                               "model_sha256":270cba1b…}; provenance.model.commit 499bc882…

Artifacts: `a.json`, `b.json`, `rerun-receipt-pair0-A.json`, `rerun-receipt-pair0-B.json`.

### 2. All 24 replays (`trials.json` → `summary`)

    replays 24 | all_exit0_match_true true | all_outcome_pass true
    all_ownership_child true | all_teardown_rc0_port_refuses true
    distinct_ports 24 of 24 | child_pids_alive_now []
    batches: pair0 2, pair1-5 10, four-way 4, eight-way 8
    ports: 38195 45559 39189 44103 46623 42301 43099 40757 45449 37783 41427 32903
           43327 44193 32915 36067 42843 36957 35529 36757 45627 44631 40643 36285

Eight-way batch wall time 4.04 s (per replay 2.97–3.25 s); five pair batches 15.98 s total. No
pair and no batch ever produced two equal ports; no run reported `foreign`/`unproven` ownership.
Child pids checked with `/proc/<child_pid>` after each batch: none alive.

### 3. Leftover scan (scoped to what this seat started)

    pgrep -af </fast/scratch/hyaku/kama-r48/L2Concurrent>   → no m*/wA/q* server procs
    ss -ltnp vs baseline (`ss-diff-after-pairs.txt`)        → byte-identical (<(diff) empty)
    /proc check of all 24 recorded child_pids               → []

Two contaminations of the *global* scans were observed and are **other seats**, not leftovers of
mine:
* `pgrep -af llama-server` matched peer pid 1655535, whose argv is
  `/usr/bin/python3 …/kama-llamacpp-live.py --server …/K2Cheat/…/llama-server …` — i.e. the *live
  tool's python process*, not a server. It was gone at the next check.
* The 8-way batch's `ss` diff showed one new listener `127.0.0.1:39259 users:(("llama-server",pid=1772275))`
  that vanished within seconds; 39259 is not one of my 24 ports and 1772275 was never one of my
  child pids.

### 4. Port-collision semantics are fail-safe (frozen tools, no edits)

Deliberate collision: two live-tool runs on the same explicit `--port 45311`, 50 ms apart, same
server/model from `wA`:

    B_EXIT=2   B receipt: outcome setup-error  setup_error "port-in-use:45311"
               port null, child_pid null, ownership unproven, transitions 0, checks []
    A_EXIT=0   A receipt: outcome pass, port 45311, ownership child, teardown rc 0
    port 45311 free afterwards; no server from this test alive

So a lost race cannot become a false pass: `pick_port` refuses an occupied port before spawning
(`kama-llamacpp-live.py:412-416`), and if a server ever answered on a port whose LISTEN socket is
not the child's, the first HTTP response is graded `port-listener-not-our-child` and every recorded
body is discarded (`kama-llamacpp-live.py:688-695`, `_discard_bodies` at `:756`), which the replay
turns into a `projection:ownership`/`outcome` mismatch → exit 1. Artifacts: `collA.json`,
`collB.json`.

### 5. The documented release/rebind window, measured

`pick_port` binds `127.0.0.1:0`, releases, and the server re-binds — "a sub-second collision race
is possible" (`kama-llamacpp-live.py:418-424`, receipt `port_pick_note` at `:1595`). Harness
`portrace.py` loads the *lane* module and has N workers barrier-synchronised per round: each calls
the real `pick_port(refused)`, then binds/listens on the offered port (a duplicate offer shows up as
`EADDRINUSE`):

    portrace rounds=300 workers=2 picks=600 duplicate_offers=0 bind_errors=0
    portrace rounds=150 workers=4 picks=600 duplicate_offers=0 bind_errors=0

1200 synchronised offers, 0 duplicates: the kernel's ephemeral allocator did not hand the same port
to two simultaneous pickers, so the race is a documented residual risk rather than an observed one.
Artifacts: `portrace.py`, `portrace2.log`, `portrace4.log`.

## Notes on coverage (not defects, nothing to fix in the frozen tools)

1. **The frozen C2 counter never runs replays concurrently.** `round48-live-replay-v5-audit.py:398`
   iterates the three receipts in a plain sequential loop (`for n, path in enumerate(RECEIPTS, 1)`),
   using `work-replay-<n>` per receipt. Concurrency is therefore outside C2's contract; this seat's
   24 trials are the only concurrency evidence for the v5 replay path, and they are seat-level.
2. **`pgrep -f llama-server` is an unusable leftover detector in this fleet**, because the live
   tool's own argv contains `--server …/llama-server` (demonstrated above with peer pid 1655535).
   A correct post-replay leftover check reads the recorded `child_pid`/`port` from the rerun receipt
   (`/proc/<child_pid>`, `ss -ltnp | grep :<port>`) instead of pattern-matching processes; a baseline
   `ss` diff alone is also unsafe while sibling seats run (demonstrated: foreign port 39259).

## Residual risks

* Port release/rebind window above: 0/1200 observed, so risk is small but not zero. Should it ever
  fire, the losing replay exits 1 with `port-listener-not-our-child` or `server-exited-early-rc…` —
  loud, never a silent pass.
* Both replays fetch the same two URLs concurrently; a CDN/RateLimit partial response would surface
  as `digest-mismatch:…` / `could-not-run:URLError` (exit 2), not as a false match. Not observed.
* Reusing one `--work` for two replays is not exercised here (the contract gives `--work DIR` per
  replay, and `:244` requires the *live* process to have written the rerun receipt this run; a
  nonzero live exit is independently graded as `live-exit:N` at `:250-251`).

## Files written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent.md`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/trials.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/a.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/b.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/a.log`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/b.log`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/rerun-receipt-pair0-A.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/rerun-receipt-pair0-B.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/collA.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/collB.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/collA.log`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/collB.log`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/portrace.py`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/portrace2.log`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/portrace4.log`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/ss-baseline.txt`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/ss-after-pairs.txt`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/ss-after-eight-way.txt`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/ss-diff-after-pairs.txt`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/eight-way-m0.log`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/L2Concurrent/four-way-q1.log`

Tool installs: none (no pacman, no uv/npx; nothing needed). Lane tree untouched by this seat
(report and artifacts only).
