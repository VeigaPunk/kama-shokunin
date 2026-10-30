# X11 C1 stability — round 64 wave f

Measured candidate: `23b3fdb1a925129a9961cf551f6d40bf251602cb`, checked out in the seat clone at `/fast/scratch/hyaku/kama-r64/f/X11StabilityC1Final/clone`. All runs used fresh `--work` directories under that scratch root. No lane files were edited.

## Results

Counter line shown verbatim; wall time is measured elapsed milliseconds. Every stderr was empty except those listed explicitly.

### Five sequential runs

1. `rc=1`, `1308 ms`; `tool_present=1 live_ok=0/1 controls_targeted=0/0 of 91 families_exact=0 missing_families=['bind', 'canned', 'detach', 'digest', 'forge', 'hdr', 'hold', 'idcr', 'listener', 'log', 'outside', 'pathcopy', 'predead', 'preload', 'proxy', 'ptok', 'receiptbind', 'relabel', 'replay', 'reqbind', 'runfield', 'schema', 'shape', 'sigterm', 'stale', 'stalehold', 'tamper', 'timing', 'trunc', 'witness'] eval_selftest=0/8 errors=1 met=False families[]`; stderr: `error: live: ["bind_holders"]`.
2. `rc=1`, `1288 ms`; same counter line as run 1; stderr: `error: live: ["bind_holders"]`.
3. `rc=1`, `1295 ms`; same counter line as run 1; stderr: `error: live: ["bind_holders"]`.
4. `rc=0`, `74749 ms`; `tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]`; stderr empty.
5. `rc=1`, `1343 ms`; same counter line as run 1; stderr: `error: live: ["bind_holders"]`.

### Three concurrent runs

All three succeeded, with identical full counter line (the line below) and empty stderr:

- concurrent 1: `rc=0`, `74837 ms`
- concurrent 2: `rc=0`, `74741 ms`
- concurrent 3: `rc=0`, `74742 ms`

`tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]`

### Two overlapping runs

Started run 1, then run 2 three seconds later while run 1 was active. Run 1 returned early; run 2 completed its live phase.

- overlap 1: `rc=1`, `1471 ms`; `tool_present=1 live_ok=0/1 controls_targeted=0/0 of 91 families_exact=0 missing_families=['bind', 'canned', 'detach', 'digest', 'forge', 'hdr', 'hold', 'idcr', 'listener', 'log', 'outside', 'pathcopy', 'predead', 'preload', 'proxy', 'ptok', 'receiptbind', 'relabel', 'replay', 'reqbind', 'runfield', 'schema', 'shape', 'sigterm', 'stale', 'stalehold', 'tamper', 'timing', 'trunc', 'witness'] eval_selftest=0/8 errors=1 met=False families[]`; stderr: `error: live: ["bind_holders"]`.
- overlap 2: `rc=0`, `75109 ms`; `tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]`; stderr empty.

## Assessment and retained evidence

5/5 sequential: 1 met, 4 met=False; 3/3 concurrent: met; overlap: first met=False, second met. All failures are immediate `bind_holders` live-phase errors, before any targeted controls. Classification: **host contention / transient procfs holder visibility** [INFERENCE]; evidence is the identical failure form and ~1.3–1.5 s termination, contrasted with full successful control coverage on subsequent or simultaneous runs. This attribution is not proven; a counter/tool defect remains possible. Every false is an observed run, not a pass.

`pgrep -af llama-server` before and after the whole run batch showed the same single pre-existing Ollama server (PID 3262613, port 37323, model under `/fast/scratch/hyaku/kama-r61-closure/...`); no additional llama-server process remained afterward. Retained detailed stdout/stderr, elapsed metadata and pgrep snapshots in `.ufo/waves/round-64/f/out/X11StabilityC1Final/` where available from the run capture. Scratch clone/work were under the required seat scratch root; scratch cleanup is performed before handoff.

Evidence limitation: no raw output files were copied from scratch into the lane out directory in this pass; verbatim output lines and stderr are preserved above. No tools were installed or updated.

Final successful counter output line:
tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
