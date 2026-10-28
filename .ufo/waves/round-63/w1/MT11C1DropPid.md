# MT11C1DropPid — C1 operability mutation probe (round 63, kama)

Seat: mutation-tester, leaf (no subagents). Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`
(freeze amendment 1). Advisory findings only; no verdict on the C1 claim, no lane edit, no commit to the lane.
Evidence: `.ufo/waves/round-63/w1/out/MT11C1DropPid/` (outputs, stderr, patches, receipts, `attack.py`).

## Setup and tools
- Scratch: `/fast/scratch/hyaku/kama-r63/w/MT11C1DropPid` (clones `clone` = tip, `m1`, `m2`, `m3`; removed before yield).
- Each mutant committed in its own clone (`git -C <clone> -c user.name=seat ... commit -m mutant`); each counter run from
  `<clone>/tools/` with `--repo <clone> --tip <clone HEAD> --work <scratch>/work-<n>`.
- Baseline: unmutated counter at the tip, `--repo <clone>` (blobs at 03a6a1d8), run from the clone.
- Tools: python3 3.14.8 and `llama-server` (~/.local/bin, pre-existing) used by the lane tool. Installed nothing.
  No pacman transaction. No ~/.local/bin write.
- Live contacts: only the lane tool's own unregistered loopback ports (receipt ports 37735 child, 39639 canned server
  in the attacker driver); operator llama-server on 1234/45669 untouched.

## Baseline (unmutated, tip)
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
exit 0.

## Mutants (the clauses are `live_pid` and `live_port` in `score()`, lines 304-307 at the tip)

| id | mutation | counter output (verbatim, one line) | verdict |
|---|---|---|---|
| M1 | remove `live_pid` AND `live_port` clauses | `tool_present=1 live_ok=1/1 controls_targeted=42/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=1/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=5/6]` | KILLED |
| M2 | remove `live_pid` only | `tool_present=1 live_ok=1/1 controls_targeted=42/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=1/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=5/6]` | KILLED |
| M3 | remove `live_port` only | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]` | **SURVIVED** |

Escapes, verbatim from stderr:
- M1: `escape witness expect=live_pid fails=[]`; `escape fake-foreign expect=live_pid fails=[]`.
- M2: `escape witness expect=live_pid fails=[]`; `escape fake-foreign expect=live_pid fails=['live_port']`.
- M3: none.

Answers to the item question:
- M1 (both clauses dropped): fake-foreign escapes (`fails=[]`), witness pid=1 escapes (`fails=[]`), and met is **False** (42/44).
- M2 (pid clause only): witness pid=1 escapes; fake-foreign is rejected only by `live_port`, so it is not credited under
  the named-check rule. met is False.
- M3 (port clause only): met stays **True** at 44/44.

## Finding 1 (prominent) — `live_port` is a surviving clause
M3 survives because no control names `live_port`. A grep of the tip counter finds it only at line 306 (`'live_port': ...`);
the expected-name set in `build_controls()`/fakes contains `live_pid`, `live_owned`, `live_fp_capture`, `live_ptok`, `live_object`,
`live_text` and no port check. The port binding of the outside witness to the receipt's port is therefore untested by the
44-control set, which contradicts the frozen predicate's "whose listener is the receipt's child" wording only to the extent that
it is enforced solely by `live_pid` plus `live_owned`.
[INFERENCE] With `live_pid` kept, `live_owned` makes the port redundant in practice, because the real child owns only its
bound port. This was not tested (no second-listener child built).
Fix direction (not applied here; the counter is frozen by amendment 1): one control, e.g. witness port changed to a
different loopback port owned by the child, expecting `live_port`. Any such change is a counter amendment for the L1 to decide.

## Finding 2 — the canned-server attack with the real child pid is rejected only by `live_owned`
Driver `attack.py` (in the outputs directory): runs the tip tool in hold mode, reads the real `ready.json` (child pid
2388566, port 37735 in this run), writes an attacker `hold.json` naming the real child pid and a canned, self-consistent
loopback server (usage.prompt_tokens equal to its /tokenize count, fingerprint copied from the real server, alias and both
SHAs pinned), observes it with the counter's own `observe()`, releases the hold, and re-scores the genuine receipt.

Variant A (attacker hold.json pid = real child, port = canned):
```
-- variant A-real-child-pid: witness pid=2388566 port=39639 listener_owned=False usage=5 tok=5 fp_match=True
   genuine            live_gate_met=False fails=['live_owned', 'live_port']
   m1-drop-pid+port   live_gate_met=False fails=['live_owned']
   m2-drop-pid        live_gate_met=False fails=['live_owned', 'live_port']
   m3-drop-port       live_gate_met=False fails=['live_owned']
```
The real-child-pid variant is rejected in every mutant, solely by `live_owned` (listener not in the child's fd table).

Variant B (attacker hold.json pid = attacker's own pid, port = canned; canned server runs in the attacker process):
```
-- variant B-attacker-pid: witness pid=2388349 port=39639 listener_owned=True usage=5 tok=5 fp_match=True
   genuine            live_gate_met=False fails=['live_pid', 'live_port']
   m1-drop-pid+port   live_gate_met=True fails=[]
   m2-drop-pid        live_gate_met=False fails=['live_port']
   m3-drop-port       live_gate_met=False fails=['live_pid']
```
Under M1 a fully canned server passes the entire live gate (`live_gate_met=True fails=[]`). The counter's own verdict is still
met=False for M1, but only because 42/44 controls escape; the live path itself would have accepted the canned server.
So the M1 kill rests entirely on the `fake-foreign` and `witness pid=1` controls, which is what the item asked to show.

Root of the two findings: `listener_owned` proves that *some* pid named by hold.json owns the port; the only bindings
of that pid to the receipt's child (`live_pid`) and of the port to the receipt (`live_port`) are the two clauses in
question. `live_owned` alone is not a child binding.

## Finding 3 — hold.json is taken from the first parsable file (code reading, NOT exercised)
`witness_run()` reads whichever `hold.json` appears first. The tool writes its own `hold.json` at kama-completion-live.py
line 490 with `open(...,'w')`, then `ready.json`. An attacker who writes an earlier, valid `hold.json` could therefore be
read first. [INFERENCE] This was not run against the real `witness_run`; the attack driver replays the same consumer
logic (`observe` on the attacker hold) after `ready.json`, not the race itself.

## Not done / limits
- Mutants were run once each; outputs are deterministic in the code paths above (1.5 s wall each).
- No mutation of kama-completion-live.py or kama-llamacpp-live.py was run (not in the item).
- The race in Finding 3 was not reproduced; the second-listener redundancy claim in Finding 1 was not tested.

## Cleanup
Receipts and outputs copied to `.ufo/waves/round-63/w1/out/MT11C1DropPid/` (base/m1/m2/m3 `.out`/`.err`, the three `.patch`
files, `attack.py`, `attack.out`, and receipt JSONs). Scratch root removed before yield. Lane, fleet, lane index and sibling
lanes untouched.

Final tally: M1 KILLED, M2 KILLED, M3 SURVIVED (live_port has no naming control); attacker variant A rejected by live_owned,
variant B passes the live gate under M1.
Counter line (M3, the survivor): `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]`
