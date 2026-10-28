# X08StabilityC1 - C1 counter repeat/concurrency at freeze f6a4ea9a

Tip scored: f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (clone checkout, nothing edited; counter sha256 prefix b69c4b075f36b12f).
Command (each run, fresh --work): `python3 tools/round64-c1-counter.py --repo $D --tip $T --work $S/work-<n>` from `$D/tools`.
Host: load average 49-54 throughout (other seats' servers). Raw outputs/stderr: `out/X08StabilityC1/` (seq*, con*, x*).

## 1. Five sequential runs (required item)
Per-run wall time was not captured for this batch (my timing used `bc`, which is not installed; it printed
`error: command not found: bc` to stderr - a harness error of mine, not a counter error). The whole batch took 41.3 s => ~8.3 s/run.
Counter output (families table identical in all met=True lines; shown once):

| run | rc | line |
|---|---|---|
| 1 | 0 | tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True |
| 2 | 0 | same, met=True |
| 3 | 0 | same, met=True |
| 4 | 1 | tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[...runfield=3/4...] (all others at declared count) |
| 5 | 0 | same as 1, met=True |

Families on met=True: bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5.

Run 4 full stderr (only counter stderr line; the `bc` lines are mine):
`error: escape runfield/live_ref_text expect=live_ref_text met=False nfails=1 fails=['live_ref_usage']`
live_ok=1/1 on that run (the genuine live lifecycle passed); errors=0; only control family hit: runfield (the `swap_answer` control).

## 2. Three concurrent runs (separate --work, started together)
| run | rc | wall | result |
|---|---|---|---|
| con1 | 0 | 8.73 s | 76/76 families_exact=1 eval_selftest=3/3 errors=0 met=True |
| con2 | 0 | 8.83 s | same met=True |
| con3 | 0 | 8.75 s | same met=True |
All stderr empty. Concurrency (3 live servers + reference servers each on own free loopback ports) did not disturb the counter; wall ~8.8 s vs ~8.3 s sequential.

## 3. Extra sequential batch (timed): 10 more runs
x1..x10 all rc=0 met=True 76/76, stderr empty, wall 8.19-8.65 s (e.g. x1 8589 ms, x6 8190 ms, x10 8251 ms).
Tally over all 18 scored runs (5 + 3 + 10): 17 met=True, 1 met=False (run 4). No other flake, no timeout, no `error:` besides the one above.

## 4. Classification of the run-4 flake: COUNTER DEFECT (control construction), not host load, not the tool
Mechanism (read from tools/round64-c1-counter.py):
- Control `runfield/live_ref_text` (`swap_answer`, line ~1349-1355) builds the forged witness by copying probe 0's whole answer into probe 1 (keeping probe 1's sent_prompt and n_predict), and demands that the failure set contain `live_ref_text`.
- `probe_fails` (line 665-668) raises `live_ref_text` only if probe1.text != ref[1].text. The forged probe 1 carries probe 0's text, so the control works only if the two randomly drawn probes (draw_probes: k in 2..24 words, n in 3..9, distinct (k,n)) produce different greedy texts on the reference model (stories260K).
- When the two texts coincide, the copied answer matches ref[1].text, `live_ref_text` is not raised, and the swap is rejected only by `live_ref_usage` (usage differs because (k,n) differ). That is exactly the observed set: `fails=['live_ref_usage']`, nfails=1. The forgery is still caught, but not by the check the control names, so the frozen kill rule ("each rejected by the check it names") counts it as an escape and `runfield=3/4`, met=False.

Evidence it is a random probe-draw collision, not load:
- Reproduction by sampling: out/X08StabilityC1/sim-probe-text-collision.py imports the counter's own draw_probes/probe, starts one pinned server (same flags as the reference) and draws 400 probe pairs: texts_equal=7/400 (1.75%, 95% CI ~0.7-3.6%), usage_equal=0/400. Collisions all have equal n_predict and short texts, e.g. (7,7,'.\nOne day,','.\nOne day,'), (3,3,'. \n','. \n'), (4,4,'. \nO','. \nO'), (3,3,'s. ',' s. ').
- Run-4 reference log (out/.../seq4-ref-server.log) shows normal operation (2 prompts, 78 and 58 tokens, released cleanly); live_ok=1/1, errors=0, all other 75 controls in place - no timeout/port/teardown symptoms, which are the host-load signatures. The probe seed is os.urandom per run so run 4's exact draw cannot be replayed; the sampled rate (1.75%/run) is consistent with 1 in 18 (observed 5.6%, p~0.25 under the 1.75% rate).
- Host load was ~50 for all runs; the other 17 runs (incl. 3 concurrent) were clean on the same load, and the failure signature is a deterministic function of the draw.

Consequence for the instrument: the counter's own frozen predicate ("all 76 targeted controls ... each rejected by the check each names") fails on ~1-2% of runs at an unchanged tip with an unchanged tool. A met=False from this signature (`escape runfield/live_ref_text ... fails=['live_ref_usage']`, runfield=3/4) must not be read as a defect of kama-completion-live.py v3.
Possible fix (not applied - I edited nothing; L1's call and would be a numbered AMENDMENT): have draw_probes redraw until the two reference answers' texts differ (or make the swap control compose from the reference answer of the other probe), so the control is deterministic. Equivalent fix for any other control whose named check depends on the two random answers differing: I checked `live_ref_usage` (adds +1 to probe 0, always differs) and found no other text-equality dependency.

## 5. Housekeeping
Tools installed: none. No mutating git outside the scratch clone (only `git checkout` of the freeze in my own clone). No process of mine left (pgrep on scratch path empty). The sim server was my own and terminated with SIGTERM. Scratch removed after receipts were copied.

One-line receipts:
- run 4: `tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 ... eval_selftest=3/3 errors=0 met=False (runfield=3/4)`
- 3 concurrent: met=True x3, 18 scored runs total: 17 True / 1 False (counter-defect flake, ~1.75% per run by sampling).
