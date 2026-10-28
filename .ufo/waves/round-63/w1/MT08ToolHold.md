# MT08ToolHold — falsify the C1 hold window (round 63, kama)

Seat: MT08ToolHold (mutation-tester, leaf, no subagents). Judged on: operability.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (AMENDMENT 1 counter; unmutated counter `tools/round63-c1-counter.py` run from the clone path, `--repo <clone> --tip <mutant commit>`).
Lane checkout, lane index, lane jj state, fleet files: not written. Mutants lived only in scratch `--shared` clones (`clone-<M>`), committed inside them as seat identity; the clones are deleted before yield.
Tools installed/updated: none (no installs; pacman not used).

## Baseline (unmutated tool at the tip, unmutated counter)

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
exit 0, wall 5.6 s. Baseline is met, so every mutant result below is attributable to the mutation.

## Mutants (one mutation each, all in `tools/kama-completion-live.py`)

| id | mutation (tool side) | mutant commit | verdict | reps |
|---|---|---|---|---|
| M1a | skip hold: write hold.json, set `w={'released': True}` at once, no wait; hold.json left on disk | 2a88580c | KILLED | 3/3 |
| M1b | skip hold: as M1a but hold.json unlinked immediately | d3df66ba | KILLED | 1/1 |
| M2 | early release: tool writes `release` itself, calls hold_for_witness (returns at once), then keeps the child alive 3 s before teardown | 483d0193 | **SURVIVED** | 3/3 |
| M3 | hold.json carries `'pid': os.getpid()` (the tool's pid, not the child's) | c2869cb7 | KILLED | 1/1 |
| M4a | never writes hold.json; honours `--hold-timeout 90` | 1b34f70a | KILLED | 1/1 |
| M4b | never writes hold.json; ignores the timeout and waits forever for `release` | 9c13f0a0 | KILLED | 1/1 |
| M4c | never writes hold.json; skips the wait entirely, claims released=True, exits | 4e980d77 | KILLED | 1/1 |
| M4d | never writes hold.json; sleeps forever, never releases | 9219ec57 | KILLED | 1/1 |
| M5 | early release with no post-release life (M2 minus the 3 s sleep) | f4b54e77 | KILLED | 3/3 |

### Counter output, verbatim (stdout; stderr `error:` lines summarised where long)

- M1a (rep 1; reps 2 and 3 identical except timing):
  `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]`
  `error: live: ["live_created", "live_ctype", "live_fp_capture", "live_fp_shape", "live_model", "live_object", "live_owned", "live_ptok", "live_status", "live_text"]`  rc=1, wall 385 / 512 / 762 ms
- M1b: `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]`
  `error: live: ["live_created", "live_ctype", "live_fp_capture", "live_fp_shape", "live_model", "live_model_sha", "live_nonce", "live_object", "live_owned", "live_pid", "live_port", "live_ptok", "live_server_sha", "live_status", "live_text"]`  rc=1, wall 384 ms
- M2 (reps 1, 2, 3 identical):
  `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]`  rc=0, wall 4413 / 4351 / 4425 ms
- M3: `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]`
  `error: live: ["live_owned", "live_pid"]`  rc=1, wall 434 ms
- M4a: `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]`
  `error: live: ["hold_released", "live_created", "live_ctype", "live_fp_capture", "live_fp_shape", "live_model", "live_model_sha", "live_nonce", "live_object", "live_owned", "live_pid", "live_port", "live_ptok", "live_server_sha", "live_status", "live_text", "verdict"]`  rc=1, wall 90457 ms
- M4b: `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]`
  `error: live: ["live_created", "live_ctype", "live_fp_capture", "live_fp_shape", "live_model", "live_model_sha", "live_nonce", "live_object", "live_owned", "live_pid", "live_port", "live_ptok", "live_server_sha", "live_status", "live_text"]`  rc=1, wall 120357 ms
- M4c: `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]`
  `error: live: ["live_created", "live_ctype", "live_fp_capture", "live_fp_shape", "live_model", "live_model_sha", "live_nonce", "live_object", "live_owned", "live_pid", "live_port", "live_ptok", "live_server_sha", "live_status", "live_text"]`  rc=1, wall 344 ms
- M4d: `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]`
  `error: live: no receipt produced`  rc=1, wall 180439 ms
- M5 (reps 1, 2, 3): `tool_present=1 live_ok=0/1 controls_targeted=0/0 eval_selftest=0/3 errors=1 met=False families[]`
  `error: live: ["live_created", "live_ctype", "live_fp_capture", "live_fp_shape", "live_model", "live_model_sha", "live_nonce", "live_object", "live_owned", "live_pid", "live_port", "live_ptok", "live_server_sha", "live_status", "live_text"]`  rc=1, wall 378 / 348 / 356 ms

Evidence: `.ufo/waves/round-63/w1/out/MT08ToolHold/` (stdout/stderr per run, `receipts/*.receipt.json`, `diffs/<M>.diff`, `run-mut.sh`).

## Finding 1 — SURVIVED: the hold gate is self-attested (M2, 3/3)

M2 writes the release file itself before calling `hold_for_witness`, so the tool's hold ends at once, then keeps the (genuine, pinned) child listening for 3 s before teardown. The unmutated counter observes the child in that 3 s and returns `met=True`, `controls_targeted=44/44`, `eval_selftest=3/3`.

Evidence from `work-M2-1/receipt.json` (kept in receipts/):
- `hold = {'dir': …, 'released': True}`; check `hold_released = {'passed': True, 'reason': 'the release file appeared inside the hold window'}`. The reason text is false: the file existed before the tool began waiting.
- `teardown.waited_ms = 7`, `returncode = 0`, `port_closed = True`.
- The hold dir ends with a 3-byte `release` (`go\n`, the counter's own write after observing). The tool's early `early\n` (6 bytes) was overwritten, so nothing on disk records that the hold never waited.

Why the counter credits it (lane code, read-only):
1. `grade()` sets `out['hold_released'] = bool(hold.get('released'))`, i.e. it recomputes the check from the tool's own claim. Nothing ties that bit to the handshake.
2. The tool discards its own hold duration: `tools/kama-completion-live.py:560` does `receipt['hold'] = {'dir': args.hold_dir, 'released': released}`, overwriting the `waited_ms` that `hold_for_witness` returned (line 492-493 before it). The receipt therefore cannot show how long the hold lasted, and the counter has nothing to check it against.
3. The counter's hold controls only flip True→False (`add('tamper', … {'released': False})`, `add('hold', … {'released': False})`). No control drives released=True without a genuine wait, so the 44/44 set cannot see this class.

What is and is not falsified. The live answer is real: the child was alive, the listener belonged to the receipt's pid, the fingerprint and the /tokenize count matched (all live_* checks pass). M2 does not fake the request-plane observation. It falsifies the operability claim that the hold window existed and was released by the outside observer, and the check text that asserts it. Under the frozen predicate ("every graded check recomputed true") `hold_released` is therefore satisfied by the tool's own word.

Candidate kill for L1 to evaluate (not implemented or run here): (a) keep the tool's `waited_ms`/`orphaned` in the receipt and require the counter's observation to fall inside `[hold.json seen, release written]`; or (b) require that `release` does not exist when the counter first sees hold.json and at the observation (not run; expected to bite on M2 because the tool creates `release` within microseconds of `hold.json`, but the poll timing makes it a strengthening, not a proof). Add a control family "release-before-wait" that must be rejected by `hold_released`.

## Finding 2 — kills are timing luck, not design (M1a, M1b, M5)

M1a/M1b/M5 are killed, on the evidence I have, because the counter's 0.25 s poll finds hold.json after the child has already begun teardown [INFERENCE from the fail sets: M1a has `live_owned`/`live_status` failing while `live_pid` passes, so hold.json was read but the listener was gone]. A slightly faster observer would contact the child inside the teardown window and the same mutant could pass. Three reps each gave the same answer; I did not measure the miss rate beyond that. The counter has no mechanism that rejects a released-without-wait receipt when the observation succeeds, so these KILLs should not be cited as hold-gate coverage.

## Finding 3 — counter exit behaviour when the tool never writes hold.json

The counter's loop is `while elapsed < 120: if hold.json: observe …; if proc.poll() is not None: break`, followed by writing `release` and `proc.wait(timeout=60)` then kill. Measured wall times (run-mut.sh, `date +%s%N` around the counter):

| variant | tool behaviour | counter wall | exit | message |
|---|---|---|---|---|
| M4c | exits at once, no hold.json, no wait | 0.34 s | 1 | live fails (`live_owned`, `live_pid`, …) |
| M4a | never writes hold.json, waits for release with honoured 90 s timeout | 90.46 s | 1 | adds `hold_released`, `verdict` |
| M4b | never writes hold.json, waits forever for release | 120.36 s | 1 | live fails; counter's 120 s deadline writes `release` |
| M4d | never writes hold.json, never releases, hangs | 180.44 s | 1 | `error: live: no receipt produced` |

So the counter's wait is `min(tool exit, 120 s)` plus, for a hung tool, a further 60 s `proc.wait` and a kill (120 + 60 = 180 s observed). The 120 s bound is hard-coded and is not tied to the tool's own `--hold-timeout 90`. In M4d the failure is reported only as `no receipt produced`: the hold diagnosis is lost. The kill in M4d sent SIGKILL to the tool. Whether its llama-server child then died is [INFERENCE: the tool sets PR_SET_PDEATHSIG]; a process-list check after the run showed no `MT08ToolHold` clone process, but the server argv carries no scratch path, so that is an absence check, not a ppid proof.

## Finding 4 — wrong pid is caught (M3, KILLED)

hold.json `pid = os.getpid()` (the tool's own pid): `live_owned` (the claimed pid does not own the listener) and `live_pid` (w.pid ≠ receipt child_pid) fail; nothing else. This is a clean, named-check kill. The counter's `live_owned` asks whether the pid it is given owns the listener, so a wrong pid passes only if that pid really owns the port.

## Limits of this seat

- Single-host, single-model fixture (stories260K.gguf, pinned). No other hold windows were exercised.
- Race-based kills (M1a, M1b, M5) were run 1–3 times, not a rate study.
- The candidate kill for Finding 1 was described, not implemented or run; per the seat's bounds, no lane source was edited.

## Tally

MT08ToolHold: baseline met=True; mutants=9 (M1a, M1b, M2, M3, M4a, M4b, M4c, M4d, M5); KILLED=8; SURVIVED=1 (M2, early release with a post-release child life, 3/3); tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09; counter exit on a tool that never writes hold.json: 0.34 s (exits), 90.46 s (honoured timeout), 120.36 s (waits on release), 180.44 s (hangs, no receipt).
