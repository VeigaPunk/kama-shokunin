# MT07RefAgree - round 64 wave b - C1 reference-check attack (operability)

Seat: MT07RefAgree (leaf, no subagents). Tip under test: f6a4ea9a8b5a876d685b08e7e582ec0723412a4a
(the committed C1 instrument; base 0c1eff3). Frozen predicate: controls/freeze.txt, C1-r64.
Evidence: .ufo/waves/round-64/b/out/MT07RefAgree/ (harness sources, jsonl/summaries, 60 genuine
run outputs, forged-tool patch, procfs/Yama probes). Scratch removed after copy.

## Verdicts (headline)

- (a) Probe collisions are rare but real. Text-identical probe pairs: 9/1200 in-run seeds (0.75%).
  Text+usage collision (which would let a replayed answer pass the reference checks): 0/1200 in-run;
  123/319,600 independent pairs (3.8e-4). Effect on the counter: a false fail, not a false pass
  (the runfield swap control escapes exactly when texts collide).
- (b) A forged server that proxies to a second pinned server **SURVIVES** the counter when the
  listener holder is a root process (forged tool uses `sudo -n`). Live witness passes, the
  counter prints `met=True`. The reference check does not help: the forwarded answers are genuine.
  Unprivileged forwarders cannot take the listener (Yama ptrace_scope=1), so they are KILLED.
  Decisive observation for the survivor: **absence** - holder_pids() records a root-owned holder
  in neither `pids` nor `unreadable`. Minimal fix (one line, tested) kills it - see section B.
- (c) Genuine tool, 60 runs: live reference disagreements 0/60. One live fail 1/60 (`bind_holders`,
  cause not determined, not a reference disagreement). The counter's `bind_ancestry` control
  escapes in 29/30 background launches (met=False 30/30 there) and 0/30 foreground: a launch-context
  bug in the counter, separate from the reference check. Fixed locally by a 1-token change (section D).

## Tools installed / updated

None. Passwordless `sudo -n` was used (already available) for the privileged forwarder test only.
Python 3.14.8 used as-is; the pinned llama-server is ~/.local/opt/llama-b11755 (sha b6a31a8e...).
Pacman not touched.

## A. Reference-check collisions (attack a)

Harness: `harness_a.py` (imports the committed counter module from the scratch clone, read only;
per seed: `draw_probes(Random(seed), nonce)` -> `reference_run()` -> `probe_fails()` on the
replay of probe 1's full answer with probe 2's counter-owned sent_prompt/n_predict). One fresh
pinned reference server per seed, exactly as the counter starts it.

| sample | seeds / pairs | text identical | usage identical | text+usage | replay passes ref checks |
|---|---|---|---|---|---|
| in-run, run 1 | 200 | 0 | 0 | 0 | 0 |
| in-run, run 2 | 1000 | 9 (n equal in all 9; 9/143 n-equal seeds = 6.3%) | 0 | 0 | 0 |
| pairwise (`harness_a2.py`) | 800 candidates, 319,600 pairs | 4,483 (1.40%) | - | 123 (3.8e-4) | 123 by construction (all ref-check inputs equal) |

Facts behind it (out/MT07RefAgree/out-a3/summary.json, out-a2/pair_summary.json):
- The stories260K model answers the same short prefix (". \n", ". \nOne") for many prompts; text
  equality needs equal n_predict (drawn 3..9), then matching text.
- prompt-token counts (ptok) equal in only 6/1000 in-run seeds, so usage almost never matches.
- Counter consequence (measured): runfield `swap_answer` escapes whenever probe texts are equal
  (9/9 in-run collisions; the swap then trips only `live_ref_usage`). Genuine run therefore
  prints met=False. Observed once in 60 genuine runs (below):

  `error: escape runfield/live_ref_text expect=live_ref_text met=False nfails=1 fails=['live_ref_usage']`

Reading: a replayed probe-1 answer can pass as probe 2 only on a text+ptok+ctok+n collision
(~1 in 2600 independent pairs; 0 in 1200 in-run). A forger would still need the reference
answer for the run's random prompts, which it can only get from a second pinned server (B).
So (a) is a calibration/false-fail finding (about 0.75% per run), not a practical bypass.

## B. Forged server with a second pinned server (attack b)

### B1. Unprivileged route is closed (procfs / Yama)
- `yama2.py` (out yama2.out): a sibling process calling `pidfd_getfd` on the child's listener
  gets `-1 Operation not permitted`; the ancestor gets fd 6. So a same-uid forwarder that is not
  an ancestor of the pinned child cannot take the listener. The tool itself is an ancestor, but
  it holds the listener visibly (dumpable: holder check -> bind_holders) or non-dumpable
  (own-uid, start >= tool start -> unreadable_own -> fail closed). `nd_test.py/nd_forger.py`:
  a non-dumpable same-uid process gives `PermissionError` on /proc/<pid>/fd and keeps its
  own-uid stat owner, so the counter's `unreadable_own` branch fires.
- Those unprivileged variants are therefore KILLED by existing branches (counter controls
  `proxy=1/1`, `canned=1/1`, `detach=1/1`, `forge=3/3` in every met line). [INFERENCE for the
  tool-as-holder variants: not run live, analytic from the same branches.]

### B2. Privileged forwarder - SURVIVED
Forged tool (clone commits 438525d4, gated 94d5e6f6; diff in out/clone-evidence/forgery-tool-and-forger.patch):
- The tool, right after its own listener gate, runs only for the `live` witness label:
  `sudo -n python3 tools/rootforge.py <child> <port> <server> <model> <alias> <hold>`
  then waits for `forger.ready`. (9 lines.)
- `rootforge.py` (149 lines, run as root): starts a second pinned llama-server on a hidden port
  (the "reference answerer"); `pidfd_open(child)` + `pidfd_getfd` on the child's listening socket
  (root has CAP_SYS_PTRACE); `SIGSTOP`s the child; serves the run port with an HTTP forwarder to
  the hidden server; exits on `release`, on child death, or after 600 s (SIGCONT + kill of the
  hidden server).

Procfs facts (verify_forge.py / verify_forge.out, run by hand on the forged tool):
```
{"hold_pid": 2814744, "port": 46241, "child_state": "T"}
{"counter_scan_holders": [2814744], "unreadable_own": [1500, 2911361], "listener_inodes": [1881880824]}
{"answers": [{"text": "00 mad", ...}, {"text": "00 pr", ...}]}
... 2815368 root sudo -n ... rootforge.py 2814...   2815432 root python3 rootforge.py ... (forwarder)
tool rc 0
{"verdict": "REQUEST_OK", "listener_holders": [{"pid": 2814744, "exe": ".../llama-server", "exe_sha256": "b6a31a8e..."}], "checks_failed": []}
```
- The child is stopped (`T`); the counter's scan finds only the child; the forwarder (root, pid
  2815432) appears in neither `holder_pids` output set. Reason: `holder_pids()` reads
  `/proc/<pid>/fd` -> PermissionError -> `os.stat('/proc/<pid>').st_uid == me` is False for uid 0
  -> the branch does nothing (`sudo`-owned processes are silently skipped). Verified:
  `sudo -n python3 -c 'os.stat(/proc/<self>).st_uid'` -> 0.
- The tool's own `listener_holders_pinned` uses the same blind scan, so the tool's receipt agrees.
- The reference check passes because the answers are genuine: live_ref_text/live_ref_usage do
  not fire. The reference agreement adds nothing against forwarding.

Counter lines (the same forged tip, foreground chain):
```
forgeR3 (94d5e6f6, first run):  tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 ... witness=5/5]
forgeR3 (repeat):               same line, met=True
```
Verdict: **SURVIVED** (decided by the absence of a procfs observation for a non-own-uid holder).

Earlier ungated run (438525d4, hook also in the forge controls): live_ok=1/1 but
`met=False` from control artefacts of the hook (forge=0/3, `forge/forgeA2 escape ... nfails=33`
over the cap of 14); not used as the verdict.

### B3. Counter fix that kills it (one-line, tested locally - not committed; AMENDMENT needed)
M1 = in `holder_pids()` drop the `st_uid == me` filter (`if True:`), i.e. fail closed on any
unreadable fd table whose start is at or after the tool's start (the existing `collect()` filter):
```
M1 on forged tip 94d5e6f6:  tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 ... eval_selftest=0/3 errors=1 met=False
                            error: live: ["bind_holders"]
M1 on genuine tip f6a4ea9a: tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 ... eval_selftest=3/3 errors=0 met=True
```
Verdict on the forgery under M1: **KILLED** (bind_holders; decided by the root holder now recorded
as unreadable). One run each; a root process started after the tool during a real run would now
also fail closed (false fail risk, not measured).

## C. Non-determinism (attack c): genuine tool, 60 runs

Two batches of 30 genuine counter runs at f6a4ea9a (`loop_c.sh` background via `nohup`, parent chain
short; `loop_c2.sh` foreground chain). Output: out/MT07RefAgree/out-c, out-c2.

| batch | runs | live_ok | live reference disagreements (live_ref_text/usage) | live other fails | runfield swap escape (text collision) | bind_ancestry escape | met=True |
|---|---|---|---|---|---|---|---|
| background (nohup) | 30 | 29/30 | 0/30 | 1 (`bind_holders`, run14) | 1 (run18) | 29/30 | 0/30 |
| foreground | 30 | 30/30 | 0/30 | 0 | 0 | 0/30 | 30/30 |

Reference-check false-fail rate on genuine runs: 0/60. Whole-counter met=False: 30/60, all from the
background batch (29 `bind_ancestry` escapes plus run14's live fail); the foreground batch is 30/30 met=True.

Counter lines (verbatim):
```
(bg, typical)  tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 ... errors=0 met=False
               error: escape bind/bind_ancestry expect=bind_ancestry met=True nfails=0 fails=[]
(bg, run14)    tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 ... errors=1 met=False
               error: live: ["bind_holders"]
(bg, run18)    error: escape runfield/live_ref_text expect=live_ref_text met=False nfails=1 fails=['live_ref_usage']
(fg, all 30)   tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 ... errors=0 met=True
```
- run14 `bind_holders` (live): `bind_holders` requires holders == {hold pid}, no `unreadable_own`
  and hold_port == port. The binding snapshot of that run was not persisted, so the clause is not
  identified. The likely source is an own-uid, non-dumpable process started during the run window
  (the host had such processes: another seat's helper, 1Password browser support). [INFERENCE]
  Not reproduced in 30 foreground runs.
- `bind_ancestry` escape (control `tool_pid: 1`): the control is only rejected when pid 1 is not in the
  holder's 8-entry `ppid_chain` (tool, counter, then 6 ancestors). Foreground launch: the counter's
  ancestors run through omp, bash, alacritty, Hyprland, start-hyprland, systemd (1494) before pid 1,
  so pid 1 falls outside the window. Background launch (nohup, reparented): counter -> loop script ->
  systemd (1494) -> pid 1 is inside the window, and the control escapes. Launch-context dependent,
  not reference related (`chain_fg.out` shows the foreground ancestry).

### D. Counter-control fix (tested locally, not committed)
M2 = `tool_pid: 1` -> `tool_pid: 0` (ppid_chain never yields 0):
```
M2 foreground: tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 ... errors=0 met=True
M2 background: tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 ... errors=0 met=True
```

## Mutant table

| # | mutant (what it is) | counter run | verdict | decided by |
|---|---|---|---|---|
| a1 | two probes identical in text (in-run) | harness, 1200 seeds | 9 text collisions -> swap control escape (false fail) | text equality; usage differs |
| a2 | replay probe 1 answer as probe 2 | pairwise 319,600 | 123 pairs pass ref checks; 0 in-run | text+ptok+ctok+n all equal |
| b1 | unprivileged forwarder / proxy to 2nd pinned server | Yama probe + existing controls | KILLED (cannot take listener; proxy/canned/detach controls 1/1) | ancestor rule; visible holder |
| b2 | root forwarder + 2nd pinned server (forgeR3) | live witness | **SURVIVED**, met=True | absence: root holder in no procfs set |
| b2+M1 | same, counter drops st_uid filter | live witness | KILLED, bind_holders | unreadable fd of a post-tool process |
| b3 | non-dumpable same-uid holder | nd_test | KILLED by unreadable_own (observed; counter branch) | /proc/<pid>/fd PermissionError + own uid |
| c1 | genuine tool, 60 runs | counter | 0/60 ref disagreements | - |
| c2 | bind_ancestry control launch-context | counter, bg/fg | flake (29/30 bg) | pid 1 inside 8-deep ppid chain |
| c2+M2 | control token 1 -> 0 | counter, bg/fg | met=True both | - |

## Notes for the L1
- The round-64 counter's own tool-side and counter-side holder checks share the same blind spot;
  the fix is the counter's `holder_pids()` (M1) and should be an AMENDMENT before wave f.
- The swap control (runfield) should not require `live_ref_text` alone when texts collide; a probe
  draw with distinct texts (or a control using usage) avoids the false fail (~0.75% per run).
- The bind_ancestry control should use a value that is never a ppid (0), per M2.
- Forged-tool evidence is in out/MT07RefAgree/clone-evidence/ (patch + rootforge.py + tip sha
  94d5e6f6a10bd37ac3514c4b5750d725c481bc81). Clone is scratch only; nothing committed to the lane.
- Cleanup: three root processes left by my forgeR2 run (pids 2857332/2857335/2857354) were killed by
  me; none remain. Scratch root removed after copy.

Final counter line for the survivor (the one-liner the falsifier should rerun):
`tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True` (forged tip 94d5e6f6a10bd37ac3514c4b5750d725c481bc81)
