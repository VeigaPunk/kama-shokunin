# Round 47 · lane kama · seat L2Concurrent — two simultaneous replays of one receipt

**Verdict: the hypothesis holds exactly as scoped and fails as a general fleet property.** Two replays of
`c2/live/receipt-1.json` started in the same instant in separate `--work` dirs both exited 0 with
`match=True`, recorded 11/11 checks, picked distinct ports, and left no listener and no child behind — twice
(pair 1 and a re-run pinned to the frozen commit), plus 600 further two-way pairs (1200 runs) with zero
collisions. But the clause is only true at two-way concurrency: at twelve-way concurrency the tool's
`bind(:0)`/release/rebind port pick (tools/kama-llamacpp-live.py:371-378) did collide — 1 collision in 1860
live lifecycle runs, 2.4e-4 per simultaneous pick pair — and a collision is reported by
tools/kama-live-replay.py as **`exit 1`, `match=False`, with `check:teardown_port_closed:True->False`**, i.e.
as a teardown/leak regression although nothing leaked and the endpoint is healthy. The failure is
fail-closed (never a false pass) but misattributed.

---

## 1. Conditions and identity

The build landed at lane commit `3a09a1d93dcc16799cf6c4b48786e6440af134c4`. I did not re-run the shipped
bytes by assumption; I hashed them against that commit:

| file | working-tree sha256 | == HEAD | == 3a09a1d9 |
|---|---|---|---|
| `tools/kama-live-replay.py` | `39cd387a3a95b47865d81484ffe30664e653d5016c4c75d47abf6e855e43fdd0` | yes¹ | yes¹ |
| `tools/kama-llamacpp-live.py` | `65301a3c76f925bf3316673d3774269f6d93ca22f4ccdb7c7139e6826b8ae65d` | yes | yes |

¹ verified at 21:31Z, before every run below; `tools/kama-llamacpp-live.py` still hashes to the same blob now. A peer seat
edited `tools/kama-live-replay.py` at 18:34:09 -0300 (21:34:09Z) — after my measurements — adding a `notes` array,
`live-exit:<n>` mismatches, `original:no-evaluated-check`, fetch `.part` cleanup and two selftest cases
(worktree sha256 now `80149f0105e5629a3dee800817858742d0adbb8f97e201fc2d272452e81372bf`). Not my edit. **Every line anchor
and the proposed diff in this report are at the frozen commit `3a09a1d9`, which is the code my evidence came from**, and the
diff needs rebasing onto that newer worktree.

`git -C <lane> status --porcelain -- tools/` printed nothing (clean at 21:31Z; see ¹). Receipt used:
`c2/live/receipt-1.json`, sha256 `a4caf311ac030ce3c50373d7f2c37aa62895bcec5deb93bfa8bbd24e0706e80d`
(the copy I ran is byte-identical, `replay-pair/source-receipt-1.json`). Host kernel `7.2.11-arch1-1`,
Python `3.14.8`. No tool installs were needed.

Everything I ran wrote only under my scratch and this out directory; the lane was read-only.

## 2. The assigned trial — two replays, one start instant, separate `--work`

Both pairs were launched by a two-line barrier (`run A & run B &` in one shell, 0.1 ms apart) with
separate `--work` dirs; listeners and children were sampled during the run and checked after it.

| pair | tools | exit A/B | `match` | ports chosen (rerun receipt `argv`) | checks | child pids after | `ss -ltnp` llama listeners after | `pgrep -f llama-server` after |
|---|---|---|---|---|---|---|---|---|
| 1 | lane tree (= `3a09a1d9`) | 0 / 0 | True / True | **35567 / 44199** | 11/11 each | 2628543, 2629822 → both gone | 0 | none of mine |
| 2 | `git clone --shared` checked out at `3a09a1d9` | 0 / 0 | True / True | **34025 / 37747** | 11/11 each | 869333, 870450 → both gone | 0 | none of mine |

Both replays also verified the two digests before use (they must, or they refuse): archive
`bf94332a…e695b` and model `270cba1b…d256d` in each `--work/download/`, `teardown.log_path: null`,
`port_listener_ownership: child`, `outcome: pass`.

Commands (pair 1; pair 2 is the same driver against the pinned clone):

```
python3 <lane>/tools/kama-live-replay.py --receipt <receipt-1> --work $S/wA --out $S/a.json &
python3 <lane>/tools/kama-live-replay.py --receipt <receipt-1> --work $S/wB --out $S/b.json &
# → replay match=True refused=None mismatches=0 exit=0   (both, exit 0)
ss -ltnp | grep -i llama     # → no llama listeners (pre and post)
pgrep -af llama-server       # → pre: none; post: only a *peer seat's* process
```
Retained: `replay-pair/` (a.json, b.json, A.log, B.log, timing.txt, ss-pre/ss-post, ss-during,
pgrep-pre/post, pgrep-during.uniq, rerun-A/B.json, source-receipt-1.json), `replay-pair2/` (c.json,
d.json, C/D.log, timing2.txt, ss2-*, pgrep2-*, rerun-C/D.json).

**Limit of this trial, measured, not assumed:** the two serve phases did *not* overlap. Pair 1 windows were
`21:25:44.015–.178Z` and `21:25:44.288–.455Z` (110 ms apart); pair 2 `21:32:17.382–.560Z` and
`21:32:17.686–.864Z` (126 ms apart). The ~23 MB archive + model download and extraction serialize the two
replays, so the pair exercises the download/verify path but *not* the `bind(:0)` release/rebind window
(`pick_port`, tools/kama-llamacpp-live.py:371-378). That gap is what §3 closes.

## 3. Amplification (same lifecycle, cheap, in parallel)

Each harness run is the lane's own `tools/kama-llamacpp-live.py` invoked with the argv that
`kama-live-replay.py:152-156` constructs (server/model already acquired by the pair above, so no repeated
23 MB downloads), N runs started in the same instant, one `--out` each; a round is flagged on any non-zero
exit, any `setup_error`, or a duplicate port inside the round.

| campaign | rounds | runs | collisions | exits | leftover listener / child |
|---|---|---|---|---|---|
| N=6 | 8 | 48 | 0 | 48 × `exit=0`, 11/11 checks, 48 distinct ports | 0 / none |
| N=2 at scale | 600 | 1200 | 0 | 1200 × `exit=0` | 0 / none |
| N=12 campaign A | 6 (stopped at 6) | 72 | **1** (round 6) | round 6: one `setup-error` | 0 / none |
| N=12 campaign B | 45 | 540 | 0 | 540 × `exit=0` | 0 / none |

Totals: **1860 live lifecycle runs + 4 replays, 1 observed collision**; 4086 simultaneous pick-pair
opportunities → **2.4e-4 per pair, 5.4e-4 per run**. At two-way the observed rate is 0/600 pairs
(95 % upper bound ≈ 5e-3 per pair). Commands: `N=6 ROUNDS=8 bash amp.sh`, `N=2 MAXR=600 OUT=$S/stress2
bash stress.sh`, `N=12 MAXR=200 bash stress.sh`, `N=12 MAXR=45 OUT=$S/stress12b bash stress.sh`.
Retained: `amp/rounds.txt`, `collision12/rounds.txt`, `collision12/rounds-campaign-b.txt`,
`collision12/rounds-n2-600.txt`, `collision12/listeners-after*.txt`, `collision12/pgrep-after.txt`.

## 4. The collision, in detail

Round 6 of campaign A, two runs were handed **port 44879** by `pick_port`:

```
round=6 n=12 ports=12 dup_within_round=[44879] bad=['1:setup-error'] setup_error=['1:port-listener-not-our-child']
```

* loser `collision12/r6-1.json`: `port 44879`, `outcome setup-error`, `setup_error
  port-listener-not-our-child`, `port_listener_ownership foreign`, checks
  `teardown_graceful=False`, `teardown_port_closed=False`, `loading_envelope_graded=not-evaluated`,
  `model_unchanged=True`; `teardown`: `alive_at_teardown_start=false`, `returncode=1`,
  `sigterm_sent=false`, `port_refuses=false`, `log_lines=[]` (its child died before binding; pid 3760690
  is gone).
* winner `collision12/r6-2.json`: same port, `outcome pass`, 11/11 checks, child log
  `server_on_li: listening on http://127.0.0.1:44879`, pid 3760726 gone.

What the guard did right: the loser's first `/v1/models` answer at `t_ms=17` was a 503 served by
`server: llama.cpp` — the *winner's* server — and the D1 ownership probe
(tools/kama-llamacpp-live.py:643-649) discarded every body, recorded `foreign`, and raised a setup error
instead of capturing a neighbour's endpoint. **No false pass is possible through this path.**

What is wrong is the reporting. The loser's two teardown checks are evaluated `False` while its own
observed block says `port_listener_ownership: foreign`; `kama-live-replay.py`'s `compare()`
(tools/kama-live-replay.py:108-119) then reduces the whole event to:

```
outcome:pass->setup-error
check:health_ready:not-evaluated            (×8 check ids)
check:teardown_graceful:True->False
check:teardown_port_closed:True->False      ← reads as "the harness leaked a listener"
→ match=False, exit=1  (collision12/collision-compare.json)
```

`exit 1` is the tool's "it ran and differs" code, so under fleet concurrency the operability gate reports
a *listener leak / teardown regression* that never happened. Reproduced independently with a forced
port-in-use (foreign listener on 38153, `--port` path): live `exit 2`, `setup_error port-in-use:38153`,
0 checks evaluated, `compare()` → 13 mismatches, `exit 1` (`forced/forced-summary.json`).

## 5. Defects and proposed fixes

**D1 — port-pick release/rebind race (medium; operability).**
`tools/kama-llamacpp-live.py:371-378` binds `127.0.0.1:0`, reads the offered port, closes the socket, and
only then lets the child bind (`:1481`, `--port`); the receipt itself documents the window at
`tools/kama-llamacpp-live.py:1473-1475` ("a sub-second collision race is possible"). Command that shows it:
`N=12 MAXR=200 bash stress.sh` → round 6 above. Fix proposals, both in this out dir:
* `patches/proposed-replay-retry.diff` — retry the rerun (bounded, 3 attempts) when the rerun receipt's
  `setup_error` is an ownership token, record `rerun_attempts` in the replay JSON, and report an exhausted
  or non-transient setup error as **refused/exit 2**, not as a mismatch. This is the minimal fix and it
  repairs the gate without hiding anything (each live attempt stays one lifecycle).
* Alternative, inside the live tool: wrap pick + spawn + readiness (anchors `:1457`, `:1503-1548`) in a
  bounded retry that re-picks on `port-listener-not-our-child` / `port-listener-ownership-unproven` after
  reaping the failed child, recording `port_pick_attempts`; rejected as the first fix because it is a
  ~70-line re-indent of the monolithic `main()` and it hides retries inside a *measurement* receipt.

**D2 — teardown checks claim a foreign port (medium-low; misattribution).**
`tools/kama-llamacpp-live.py:1694-1725` computes `teardown_graceful`/`teardown_port_closed` as `False`
whenever the port is not proven ours, so a run whose child never bound reports a leak on a port another
process owns (evidence: r6-1 observed blocks, above). Fix:
`patches/proposed-live-teardown-ownership.diff` — when `port_listener_ownership != 'child'` both checks
become **not-evaluated** with reason `port-not-ours:foreign` (the observed block keeps the ownership), and
the healthy path is unchanged.

**D3 — a rerun that could not run is reported as "it ran and differs" (low; contract).**
(Still true on the newer worktree: it appends `live-exit:2` to `mismatches` but keeps `match=False`, `exit 1`.)
`tools/kama-live-replay.py` documents `2 refused (… or could not run)` but maps a rerun receipt carrying
`setup_error` onto `compare()` + `exit 1` (module docstring "Exit:" at `tools/kama-live-replay.py:18-19`,
and `replay()`'s `return res, (0 if res["match"] else 1)` at `:165`). A port collision — or any setup transient — therefore looks like
an endpoint regression. Fixed by the same `patches/proposed-replay-retry.diff` (`refused =
rerun-setup-error:<token>`, `exit 2`).

**Patch validation I ran (on copies in my scratch, never in the lane):**
* `python3 -m py_compile` on both patched copies → OK.
* `patches/proposed-replay-retry.diff` applied copy: `--selftest` → `KLR_SELFTEST pass=10 fail=0`, `exit=0`
  (all ten offline cases unchanged); a `file://` fixture whose fake live tool returns
  `port-listener-not-our-child` once and then a matching receipt → `exit 0`, `match=True`,
  `rerun_attempts=[collision, clean]`; always-collision fake → `exit 2`,
  `refused=rerun-setup-error:port-listener-ownership-unproven`, 3 attempts; non-transient
  (`model-digest-mismatch`) → `exit 2` after 1 attempt.
* `patches/proposed-live-teardown-ownership.diff` applied inside my scratch clone at `3a09a1d9` (because
  the tool resolves `LANE` from its own path): one real lifecycle → `outcome pass`, 11/11 evaluated,
  `teardown_graceful`/`teardown_port_closed` still `True`/evaluated, `port_listener_ownership child`
  (`patches/patched-live-healthy-run.json`). Clone restored afterwards (0 dirty paths, blob sha256 back to
  `65301a3c…ae65d`). The D2 branch itself is not exercised by a live run — it needs a foreign listener on
  the very port the tool picks — so D2 rests on the observed r6-1 receipt plus the patch review.

## 6. Mechanism probes (why the race exists, why it is rare)

* `amp/bindseq.py` (replica of the release/rebind step): bind `:0` → read → close → bind `:0` → read,
  200 000 trials: **22** times the just-released port was reassigned (**1.1e-4**). The hazard is real at the
  syscall level and of the same order as the observed fleet rate.
* `amp/bindrace.py`: 750 pairs of *simultaneously live* `:0` sockets never shared a port (0/750) — and that
  probe cannot see this race at all, because two live listeners can never share a port. It is retained only
  to show the negative is uninformative; `bindseq.py` supersedes it.
* The 12-way campaigns are the only reliable estimator: 1/51 rounds; campaign B (540 runs) saw none, so the
  rate is low — a wave with two replays will essentially always be clean, a wave that fans out twelve
  replays will hit this roughly once every hundred rounds.

## 7. Limits, and things that are not findings

* The two assigned pairs did not overlap in time at the serve phase (§2); do not read them as a race test.
* `pgrep -af llama-server` after pair 1 showed one `tools/kama-llamacpp-live.py …K2Fresh…` process — a peer
  seat's run (b11755), not my child; my children are identified by pid (all gone) and by scratch path.
* My first patched-live-tool run outside the clone ended `setup_error probe-not-found:<scratch>/tools/
  kama-probe.sh`: the tool derives `LANE` from `__file__`, so a copy outside the tree cannot find the probe.
  A defect of my check, not of the patch; the clone run above is the valid one.
* `bc` is not installed on this host; the `total ports chosen` line of `scripts/stress.sh` therefore printed
  empty. The totals in §3 were recomputed from the retained `rounds*.txt` (48 + 1200 + 72 + 540 = 1860).
* No service was started outside the lane tools: every `llama-server` was a child of
  `kama-llamacpp-live.py`, on a `pick_port`-chosen loopback port, torn down by the tool; 0 listeners and 0
  children of mine remain (`ss -ltnp`, `pgrep -af`, `/proc/<pid>` for every recorded `child_pid`).
* Lane, fleet repo, sibling lanes read-only; no git/jj mutation in the lane (only a `--shared` clone in
  scratch, checked out to `3a09a1d9`, toplevel asserted as `$S/lane`).
* Scratch `/fast/scratch/hyaku/kama-r47/L2Concurrent` removed after these artifacts were copied; no `/tmp`
  path is cited.

## 8. Evidence index (this directory)

`summary.json` (machine-readable roll-up) · `transcript.md` (commands, exits, verbatim key output) · `replay-pair/` · `replay-pair2/` · `amp/` · `collision12/`
(r6-1 loser, r6-2 winner, round logs, `collision-compare.json`) · `forced/` · `patches/` (two proposed
diffs + patched healthy run) · `scripts/` (drive.sh, drive2.sh, amp.sh, stress.sh, bindseq.py, bindrace.py).
