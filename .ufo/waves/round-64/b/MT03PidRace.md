# MT03PidRace — wave b, attack C1 (holder binding across raw_a → probes → raw_b)

Seat: MT03PidRace (leaf, no subagents). Judged on: operability. Milestone: falsify C1 binding.
Tip under test: f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (freeze commit; base 0c1eff3c…).
Counter: tools/round64-c1-counter.py at that tip, unmutated, unless a line says "mutant".
Evidence: .ufo/waves/round-64/b/out/MT03PidRace/ (receipts/, tools/, drivers/).

## Verdict

- **The binding is defeated by a holder that exists only inside the probe window.** A forged tool that
  steals the pinned child's listener fd (pidfd_getfd) for the duration of the counter's probes answers
  those probes from a second pinned llama-server and gives the fd back before the last answer. The
  forgery **survives the binding**: `live_ok=1/1` in 6/6 counter runs (variants c, c1), with bind_stable,
  bind_holders, bind_exe, bind_argv, bind_maps, bind_ancestry, hold_fresh, bind_listener and every
  live_ref_* check passing.
- The forgery's full counter line is `met=False` in all 6 runs, but **only** through a control-cap cascade
  in the round-63 forgeries (forgeA/forgeA2), not through the binding. Proof by control: the same hook code
  inert (`off`) gives met=True 76/76.
- **What decides it:** the forged pinned child is SIGSTOPped from hold.json until the steal, so at raw_a
  its `/proc/<pid>/stat` state is `T`. The counter's holder_record never reads state. A counter mutant
  that records the state and requires S/R at each snapshot (`bind_state`) rejects the forgery
  (`live: ["bind_state"]`, every other binding and reference check still true), keeps the freeze tip
  met=True 76/76, and does not credit the late-stop variant (which forges nothing).
- No variant reaches a clean met=True. Two of the three requested mutants are KILLED on named checks.

## Results

| variant | what the forged tool does | live stage (counter `live:` line) | full line | verdict |
|---|---|---|---|---|
| base (freeze tip) x3 | none | pass | met=True 76/76 (3/3) | control |
| (a) cn | probe 1 proxied to P3; probes 2 and later canned | FAIL live_ref_text, live_ref_usage, live_run_field, live_created; bind_stable True, bind_holders True | met=False, live_ok=0 | KILLED by live_ref_text (2/2 runs) |
| (b) b | steal; probe 1 proxied; listener fd handed to a second process K (pass_fds); first holder SIGKILLed | FAIL bind_stable (raw_a {pinned H}; raw_b {pid 2604725, python, exe not pinned}) + hold_released, teardown_clean, teardown_port_closed, verdict | met=False, live_ok=0 | KILLED by bind_stable (2/2 runs) |
| (c) c | SIGSTOP child from hold.json; steal on first queued connection; all 4 probe requests answered by P3; SIGCONT child before the 4th answer | PASS all binding and reference checks (bind_stable True, bind_holders True, live_ref_* pass) | met=False (forgeA/forgeA2 cap cascade), live_ok=1/1 | **SURVIVED the binding** (3/3 full runs, 2/2 driver runs) |
| (c1) c1 | as c, steal for the first connection only (window ≈ 10 ms) | PASS | met=False (forgeA/forgeA2 cascade; runfield once), live_ok=1/1 | **SURVIVED the binding** (3/3 full runs) |
| counter mutant `bind_state` on c | counter records holder state at both snapshots, requires S/R | FAIL bind_state only | met=False, live_ok=0 | KILLED by holder state (1/1) |
| counter mutant `bind_state` on base | same mutant, honest tip | pass | met=True 76/76 | mutant does not over-reject (1/1) |
| (c-late) cl | no stop before the probe; SIGSTOP only when a connection is queued | PASS, but no steal happened (served_in_window=0, log empty, 3/3) | met=True (2/3); met=False (1/3, forgeA cascade) | not a forgery: the child accepts first |
| off control | c's hook block present, inert (no setup, no thread) | pass | met=True 76/76 (1/1) | cascade is caused by the active steal, not by the code's presence |

Counter output lines (head through met=; the `families[...]` tail is elided here and is complete in receipts/):

```
base-1  : tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[…]
c-1     : tool_present=1 live_ok=1/1 controls_targeted=74/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[…]
          error: escape forge/forgeA expect=bind_holders met=False nfails=19 fails=['bind_ancestry','bind_argv','bind_exe','bind_holders','bind_maps','listener_holders_pinned','live_created','live_ctype']
          error: escape forge/forgeA2 expect=bind_holders met=False nfails=18 fails=['bind_ancestry','bind_argv','bind_claim','bind_exe','bind_holders','bind_maps','live_created','live_ctype']
c1-1    : tool_present=1 live_ok=1/1 controls_targeted=74/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[…]
c1-first: tool_present=1 live_ok=1/1 controls_targeted=73/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[…]
          error: escape runfield/live_ref_text expect=live_ref_text met=False nfails=1 fails=['live_ref_usage']
cn-1    : tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=[…] eval_selftest=0/3 errors=1 met=False families[]
          error: live: ["live_created", "live_ref_text", "live_ref_usage", "live_run_field"]
b-1     : tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=[…] eval_selftest=0/3 errors=1 met=False families[]
          error: live: ["bind_stable", "hold_released", "teardown_clean", "teardown_port_closed", "verdict"]
cm-c-1  : tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=[…] eval_selftest=0/3 errors=1 met=False families[]
          error: live: ["bind_state"]
cm-base : tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[…]
off-1   : tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[…]
cl-1    : tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[…]
```

## The survived forgery (c / c1): what the counter sees and does not see

Binding readout (drivers/drv.py, unmutated counter, receipts/drv-b-binding.out is b; c readout in
receipts/drv2-c-run2.out and receipts/state-readout-c.out):

- raw_a holders = [pinned H]; raw_b holders = [pinned H]; bind_stable True (same pid, start_ticks, exe sha).
- grade_binding(raw_a): all eight bind_* True. The forged answerer P3 is a real pinned llama-server on the
  same model with the same flags, so argv, exe, maps and env checks cannot distinguish it either.
- Probes: answers byte-identical to the reference server (text, usage, timings, tokenize counts), so every
  live_ref_* check passes. Answer correctness cannot see the substitution.

In-window observer (drivers/drv2.py: a separate sampler polling the listener's holder set every ~1 ms from
hold.json, outside the counter's logic). Run 2 of c:

```
transitions (ms from first sample): [0.0, [3641730]] → [90.77, [3641138, 3641730]] → [219.02, [3641730]] → [287.74, []]
tool_pid 3641138 = holder_ppid of H; H = 3641730 (hold pid); probe windows 31.8 ms and 17.9 ms
```

So during the probe window the **tool process itself** holds a dup of the run-port listener fd. The counter
reads holders only at raw_a (before any probe connection is queued) and at raw_b (after the last answer and
the steal's release). Both snapshots show {H}. The counter's procfs reads are the only places it looks.

Decisive procfs observations, by what they show:

| observation | at raw_a | at raw_b | read by counter? | would reject c? |
|---|---|---|---|---|
| holder set (pid, start_ticks, exe sha) | {H} | {H} | yes | no (transient is invisible) |
| holder state `/proc/H/stat` field 3 | **T** (stopped) | S | **no** | **yes** (bind_state) |
| holder set during the probe window | {tool, H} (sampler, 1 ms) | n/a | no | yes (not built, see below) |
| owner of each probe's accepted socket | n/a (no probe queued yet) | n/a | no | [INFERENCE] yes (during the probes the accepted socket is the tool's; not measured) |

Raw states (state-readout-c.out): c → raw_a ['T'], raw_b ['S']; base → raw_a ['S'], raw_b ['S'].

Window timing (receipts/mt03-*-window.json, steal → release, the forged tool's own clock):
c 9.1 ms (4 requests), c1 10.4 ms (1 request), cn 5.5 ms (4 requests, canned after 2). These are the
"few milliseconds around the probes" of variant (c). The sampler (1 ms) saw the window in 2/2 runs, so an
in-window observer would have caught it, at least in these runs.

Minimal forged edit (what makes c survive; receipts/tools/forge-mt03-c.vs-freeze.patch is the full diff, 234
lines, of which ~150 are generic HTTP forwarding glue):

1. Before writing hold.json: start a second pinned llama-server P3 (argv copied from the tool's receipt argv,
   new port, wait for /health) and `SIGSTOP` the child H. The stop keeps H from accepting the first probe.
2. After hold.json, a thread polls /proc/net/tcp for the run port's LISTEN row with rx_queue > 0 (a
   connection the counter queued after raw_a).
3. `pidfd_getfd(pidfd_open(H), listener_fd)` (syscall 438 via ctypes; same uid, child of the tool, so yama
   scope 1 allows it). Accept on the dup, forward each request to P3, relay the answer.
4. Before the last answer leaves: `SIGCONT` H and close the dup, so the next snapshot sees only H.

## Other findings from this attack (each with receipt)

1. **SIGTERM on the first holder breaks a handoff** (b, first attempt): llama-server's graceful stop calls
   shutdown(2) on its listening socket, which the inherited fd shares. The handoff process got
   `OSError: [Errno 22]` at accept(); probe 2 got no answer and raw_b was empty
   (receipts/handoff-sigterm-repro-k.err, handoff-sigterm-repro.out, re-run on branch mt03-bterm, 1/1).
   That run is killed by bind_stable plus live collateral. The reported handoff uses SIGKILL, which closes
   the first holder's fd without touching the socket; its failing set is bind_stable plus tool-side cascades
   (hold_released, teardown_clean, teardown_port_closed, verdict) from the child dying inside the hold.
2. **forgeA/forgeA2 cap cascade (c, c1, late-stop cl run 1).** forge_variants() patches the tip's own tool
   text (blob at --tip). Any hold-window code in the tip is therefore also inside the round-63 forgeries.
   With the hooks active, each forged run fails 18–19 checks (cap 14) though bind_holders is in the set. With
   the hooks present but inert (off), forge=3/3 and met=True. The counter credits a control only under its
   cap, so a change to the tip's hold window moves the controls, not only the live check. Operability
   finding for the counter: the control suite's base is coupled to the tool under judgment.
3. **runfield/live_ref_text control is vacuous when the two reference answers coincide.** swap_answer copies
   probe 0's text onto probe 1; probe_fails then compares text to ref[1]. If ref[0].text == ref[1].text the
   control cannot fail on text. Observed: 1 escape (c1-first, live_ref_usage only) in 16 full control-suite
   runs in this wave (base x4, c x3, c1 x3, off x1, state-mutant on base x1, cl x3, cl state-mutant x1). In
   30 fresh reference draws the two texts were never equal (eqrate.out; [INFERENCE] the rate is low but not
   zero). A flake, reported as data; not a forgery result.
4. **The late-stop variant forges nothing in 3/3 runs** (cl): the child accepts the queued probe before the
   forger's 0.5 ms poll sees rx_queue > 0, so no steal happens and the child answers honestly. A forger
   needs the child stopped before the probe (caught by bind_state), or a sub-millisecond race it lost 3/3.

## Counter mutant tested: holder state (not a tip change; scored by the mutant counter)

Diff: receipts/tools/counter-state-mutant.vs-freeze.patch (34 lines): holder_record records
`/proc/<pid>/stat` state; grade_binding adds `bind_state` = all holders in {S, R} at raw_a and raw_b.
Results: c → live_ok=0, live: ["bind_state"]; base → met=True 76/76; cl (honest) → met=True 76/76.
Limits (stated, not verified): (i) a holder can be non-stopped and still steal the fd, but only by winning an
accept race (lost 3/3 here); (ii) the transient holder remains invisible to raw_a/raw_b, so a state check
kills this forgery but not any forger that avoids stopping the child. The check the claim needs is the
owner of each probe's accepted socket, or a holder sample during the probes. Not built, not tested
([INFERENCE]).

## Process and bounds

- Clone: /fast/scratch/hyaku/kama-r64/b/MT03PidRace/clone (git clone -q --shared; checkout f6a4ea9; branches
  mt03-c, mt03-c1, mt03-cn, mt03-b, mt03-off, mt03-cm, mt03-cl). All commits are in the clone only.
  The lane, the fleet repo and the L1 index were not touched. The forged tool texts are saved in
  receipts/tools and tools/.
- No installs or upgrades. No pacman. No edits in ~/.local/bin. Python 3.14 stdlib only (ctypes, http.client).
- Only my processes were started (checked by `pgrep -f MT03PidRace`: none left). Second pinned servers are
  children of the forged tool (PDEATHSIG) or are terminated by the forger/handoff at release. The other
  llama-server processes on the host belong to other seats and were not touched.
- Host noise: 3 baseline runs at the freeze tip were all met=True 76/76, so the counter itself ran clean on
  this host during the wave.
- Repro: write the forged text into a fixture repo's tools/kama-completion-live.py (receipts/tools/*.py),
  commit, then `python3 tools/round64-c1-counter.py --repo <fixture> --tip <commit> --work <scratch>` with the
  unmutated counter (sha256 in receipts/counter-sha256.txt). For the state mutant use
  drivers/round64-c1-counter.STATE-MUTANT.py.
- Scratch root deleted after copying receipts (per the seat spec).

## Receipts

receipts/tip-base-*.out (base x3), c-1/c-2/c1-1/c1-2/c1-first (+err), cn-first/cn-1, b-after-sigkill/b-1,
off-1, state-mutant-on-c/state-mutant-on-base, cl-late-stop-unmutated-{1,2,3} (+err, +window json),
cl-late-stop-state-mutant, drv-b-binding, drv2-c-run1/run2, state-readout-{c,base}, mt03-*-window json,
ref-text-equality-30draws, counter-sha256.txt. tools/: forged texts (c, c1, cn, b, cl, off) and patches.

Operability tally: 2 of 3 requested mutants KILLED on named checks (cn: live_ref_text; b: bind_stable);
the window variant (c) SURVIVED the binding (live_ok 6/6) and is caught only by the counter's holder-state
observation, which the counter does not make today.

Final counter lines (verbatim heads; full lines in receipts/):
base-1: tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[…]
c-1:    tool_present=1 live_ok=1/1 controls_targeted=74/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[…]
cm-c-1: tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=[…] eval_selftest=0/3 errors=1 met=False families[]
