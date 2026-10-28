# MT13ProbeTokens - round 64 kama, wave b: C1 probe-token attack (operability)

Seat: MT13ProbeTokens (leaf, no subagents). Tip under test: f6a4ea9a8b5a876d685b08e7e582ec0723412a4a
(freeze commit; base 0c1eff3c). Counter: tools/round64-c1-counter.py at f6a4 (sha256 b69c4b07...,
identical to `git show f6a4:tools/round64-c1-counter.py`). Evidence: .ufo/waves/round-64/b/out/MT13ProbeTokens/.
Scratch /fast/scratch/hyaku/kama-r64/b/MT13ProbeTokens removed after copy. Clone commits used for forgeries
were `wip` commits in my own clone only (T3 646359e7 canned, T4 3f0d64de replay); nothing pushed or committed in the lane.
Tools: none installed or upgraded. Used the pinned llama-server b11755 (~/.local/opt/llama-b11755, sha b6a31a8e...)
and the system python3.

Baseline (genuine tool at f6a4, unmutated counter):
    tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]

## 1. Fuzz: draw_probes -> probe() -> probe_fails, against the genuine pinned server

Harness: out/harness/fuzz.py imports the counter by path and calls draw_probes, reference_run (fresh reference
server, same flags as the tool), probe() on a live server, and probe_fails(p, ref, idx) for both probes of each draw.
Live server flags are the tool's (-c 512 -t 1, alias kama-completion-probe, 127.0.0.1, unregistered free port).
The live side is a server the harness starts with the tool's flags, not the tool's hold window; probe(), probe_fails() and the reference are the counter's own functions.

| run | mode | draws | answers | draws with any failing probe_fails |
|---|---|---|---|---|
| fuzz-fresh-1 (smoke) | live fresh per draw | 5 | 10 | 0 |
| fuzz-fresh-64 | live fresh per draw | 100 | 200 | 0 |
| fuzz-shared-64 | one live server across 100 draws (cache carries) | 100 | 200 | 0 |
| fuzz-fresh-7 | live fresh per draw | 400 | 800 | 0 |
| total | | 605 | 1210 | **0 false fails** |

Checked on every answer: usage_prompt_tokens == tokenize_count, timings prompt_n + cache_n == usage_prompt_tokens,
usage_completion_tokens == n_predict, text == reference text, usage_completion_tokens == reference. All 1210 held.
Coverage gaps the fuzz exposed (not false fails, but untested regions of the predicate):
- finish_reason was `length` for 1210/1210 answers. The model never emitted EOS inside 3..9 tokens, so the
  `stop` branch of the finish gate (`finish_reason != 'length' or uc == n`) and the `uc < n` path are never exercised by
  genuine traffic, so no genuine answer tested that branch. Zero false fails were observed, but for this model that is absence of evidence.
- usage_completion_tokens == n_predict in all 1210 genuine answers, so live_ref_usage's completion half never
  discriminates a genuine answer from a forged one that echoes n_predict.
- n_predict over 3..9 is drawn uniformly (counts 3:198 4:153 5:166 6:167 7:193 8:133 9:200), but no control
  checks the draw itself (see mutant m08).
- cache_n > 0 for 630/1210 answers (probe 1 shares the nonce prefix with probe 0). In shared mode cache_n differed
  from the fresh reference in 25 answers; cache_n is not graded against the reference, and pn+cn==up held in all.
Per-draw data: out/fuzz/*.json (every answer, its fields and its failure set).

## 2. Canned answerer: all non-reference probe fields right

out/harness/canned_answerer.py is a python listener (the run-port holder) that:
- starts a hidden child pinned llama-server as a tokenisation oracle (never a listener) and reads the fingerprint
  from its /v1/completions; /tokenize is forwarded to the oracle, so tokenize_count is exact by construction;
- answers /v1/completions with status 200, application/json, object text_completion, model alias, a fresh id and
  created, the oracle fingerprint, usage_prompt_tokens = oracle count, completion_tokens = n_predict,
  finish_reason length, timings prompt_n = up, cache_n = 0, predicted_n = n_predict;
- text is the fixed string " a fixed sentence the model never said" (the only field a reference check can see);
- speaks the hold protocol (kama-completion-hold/v1) and writes a receipt copied from a genuine run with its own
  truthful holder (its own python exe).

Scored through the counter's own witness_run / score_run (out/harness/canned_score.py), same draws, same reference:

    seed 64 probe-level: probe_fails = ['live_ref_text'] on both probes (all non-ref fields pass, incl. live_ref_usage)
    seeds 1..5 same: probe_fails = ['live_ref_text'] on every probe (out/score/canned-seed*.out)
    full score: met=False fails=['bind_ancestry','bind_argv','bind_exe','bind_maps',
                'inconsistent:listener_holders_pinned','listener_holders_pinned','live_ref_text']

So the non-reference probe checks do not stop a canned answerer at all; the reference text check and the procfs
holder checks do. Holder checks that decide it, all read from /proc of the hold pid (= this python process):
- /proc/<pid>/exe readlink -> python, not the pinned server (bind_exe; listener_holders_pinned);
- /proc/<pid>/cmdline argv[0] = python, no --port/--alias flags (bind_argv);
- /proc/<pid>/maps: python and libpython, not the pinned library set (bind_maps);
- /proc/<pid>/stat ppid chain does not contain the tool pid, because the tool is itself the holder (bind_ancestry).
bind_holders, bind_listener, bind_env, hold_fresh and teardown pass for this forger: its holder is the hold pid.

Cross-check (canned tool committed at T3 = 646359e7, unmutated counter):
    tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=['bind', 'canned', 'detach', 'digest', 'forge', 'hdr', 'hold', 'idcr', 'listener', 'log', 'outside', 'pathcopy', 'predead', 'preload', 'proxy', 'ptok', 'relabel', 'reqbind', 'runfield', 'schema', 'shape', 'sigterm', 'stale', 'stalehold', 'tamper', 'timing', 'trunc', 'witness'] eval_selftest=0/3 errors=1 met=False families[]

Cross-check with the counter mutated (each run on T3):
    m01 drop live_ref_text:  tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=['bind', 'canned', 'detach', 'digest', 'forge', 'hdr', 'hold', 'idcr', 'listener', 'log', 'outside', 'pathcopy', 'predead', 'preload', 'proxy', 'ptok', 'relabel', 'reqbind', 'runfield', 'schema', 'shape', 'sigterm', 'stale', 'stalehold', 'tamper', 'timing', 'trunc', 'witness'] eval_selftest=0/3 errors=1 met=False families[]
    -> live fails = bind_ancestry, bind_argv, bind_exe, bind_maps, listener_holders_pinned. KILLED by the procfs holder observation.
    m15 disable all 8 bind_* and listener_holders_pinned:  tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=['bind', 'canned', 'detach', 'digest', 'forge', 'hdr', 'hold', 'idcr', 'listener', 'log', 'outside', 'pathcopy', 'predead', 'preload', 'proxy', 'ptok', 'relabel', 'reqbind', 'runfield', 'schema', 'shape', 'sigterm', 'stale', 'stalehold', 'tamper', 'timing', 'trunc', 'witness'] eval_selftest=0/3 errors=1 met=False families[]
    -> live fails = ['live_ref_text']. KILLED by the reference answer alone.
    m16 both off:  (no met= line: counter exits 1 with a traceback; last stderr line: StopIteration)
    -> live passes (live_ok=1), so the controls run and build_controls crashes (StopIteration in the bind_maps
    control, which expects the genuine .so maps). No met= line; exit 1. KILLED only by an error.

## 3. SURVIVED forgery: a genuine child holder with a replayed lifecycle

The canned answerer is caught because its holder is python. A holder that IS the pinned server passes every procfs
check, so the question is what the counter says about the lifecycle the tool claims. It says nothing: the receipt's
captures (health, models, props, completion, tokenize, completion2, bad_request, teardown) are self-reported bytes
graded for internal consistency only (grade() re-hashes the bodies it is given). The counter's own probes check the
child's answers, not that the tool performed the requests.

Forger (out/harness/replay_tool.py, and the clone-only edit out/harness/make_replay_tool.py + replay_block.txt):
the tool starts a genuine pinned llama-server as its own child on a free loopback port, writes hold.json for it,
waits for release, and writes a copy of a genuine receipt (out/harness/genuine-receipt.json) with only nonce,
child_pid, port, listener_holders (truthful for the child) and hold rewritten. It sends no request of its own.

Minimal tool edit, clone only (T4 = 3f0d64de; diff = 46 insertions to tools/kama-completion-live.py in main(),
guarded by `'/live/hold' in args.hold_dir` so only the counter's live run is replayed; forged variants keep the real
run()):
    the counter scored at T4, unmutated:
    tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]

Without the guard (T2 = 6b5cda53, replay for every run), live_ok=1/1 and the live check passes; the full line is
    tool_present=1 live_ok=1/1 controls_targeted=72/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=0/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=0/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
and the four escapes are forge/forgeA, forge/forgeA2, forge/forgeB2 and relabel, because those variants are
patch-derived from the replay tool and so replay too. The guard is an artifact of the counter's control family and
is not needed for the live check to pass.

Verdict: SURVIVED. Procfs decides nothing here: every observation the counter makes is genuine (exe re-hashes to the
pinned digest, argv/env/maps pinned, child of the tool started after it, hold.json fresh, holder pid = hold pid,
teardown observed after the counter's release). What the counter lacks is any evidence that this run's request plane
happened: no counter-sent request carries a per-run value that the captured bodies must echo. The receipt nonce is the
only per-run field and the tool simply copies it. The replay passes at 3/3 seeds (out/score/replay-seed*.out).
This is a C1 kill-rule item: "a receipt the counter accepts without its own live contact" (the captures have no live
contact with this run).

Proposed fix (NOT implemented or measured; for the L1 to consider as an amendment): (a) the counter sends the tool a
per-run prompt that embeds the probe nonce, and grade() requires captures.completion.request_body to contain it
(this also needs the tool's fixed PROMPT check in grade() changed); (b) the counter re-derives the completion text
from its own reference server for the captured request_body and requires equality with captures.completion. A replay
carries the old prompt and old text, so it fails (a); a forger that computes the new text needs the real model,
which the holder checks already bind.

## 4. Mutants of the counter (genuine tool at f6a4; counter edited in the clone, restored after each run)

Mutants are exact-string replacements, asserted to match once (out/harness/mutate.py). Each line below is the counter's
own one-liner, verbatim.

| id | edit | verdict | decided by |
|---|---|---|---|
| m01 | drop live_ref_text from probe_fails | KILLED | control runfield/live_ref_text escapes (reference answer) |
| m02 | drop live_ref_usage from probe_fails | KILLED | control runfield/live_ref_usage escapes (reference usage) |
| m03 | drop finish-reason gate `finish_reason != 'length' or uc == n` | SURVIVED | no control; redundant with live_ref_usage on genuine draws (uc == n in 1210/1210) |
| m04 | drop `pn + cn == up` | KILLED at live | live_ok=0 on the genuine run (timings) |
| m05 | drop live_ptok (up == tokenize_count) | KILLED | control witness/live_ptok escapes (tokenize oracle) |
| m06 | drop live_status (HTTP 200) | SURVIVED | no control names live_status |
| m07 | drop live_fp_shape | SURVIVED | no control names live_fp_shape; the fingerprint is still tied to the capture by live_fp_capture |
| m08 | n_predict fixed at 8 (no 3..9 draw) | SURVIVED | no control checks the draw distribution |
| m09 | reference hollowed (witness['ref'] = []) | KILLED at live | live_ok=0 on the genuine run (reference text) |
| m13 | bind_holders forced True | KILLED | controls proxy 0/1, forge 0/3 escape; the check that the run-port holder set equals {hold pid} is no longer applied |
| m14 | bind_exe forced True | KILLED | controls canned 0/1, pathcopy 0/1 escape; /proc/<pid>/exe readlink + sha256 no longer checked |

Mutant one-liners:
    m01  tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=3/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    m02  tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=3/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    m03  tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    m04  tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=['bind', 'canned', 'detach', 'digest', 'forge', 'hdr', 'hold', 'idcr', 'listener', 'log', 'outside', 'pathcopy', 'predead', 'preload', 'proxy', 'ptok', 'relabel', 'reqbind', 'runfield', 'schema', 'shape', 'sigterm', 'stale', 'stalehold', 'tamper', 'timing', 'trunc', 'witness'] eval_selftest=0/3 errors=1 met=False families[]
    m05  tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=4/5]
    m06  tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    m07  tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    m08  tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    m09  tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 missing_families=['bind', 'canned', 'detach', 'digest', 'forge', 'hdr', 'hold', 'idcr', 'listener', 'log', 'outside', 'pathcopy', 'predead', 'preload', 'proxy', 'ptok', 'relabel', 'reqbind', 'runfield', 'schema', 'shape', 'sigterm', 'stale', 'stalehold', 'tamper', 'timing', 'trunc', 'witness'] eval_selftest=0/3 errors=1 met=False families[]
    m13  tool_present=1 live_ok=1/1 controls_targeted=69/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=17/20 canned=1/1 detach=1/1 digest=1/1 forge=0/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=0/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    m14  tool_present=1 live_ok=1/1 controls_targeted=72/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=18/20 canned=0/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=0/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]

Note on m13/m14: live_ok stays 1 because the genuine child is the holder; the kill is in the controls, so the
procfs holder observation is decisive only in the controls (proxy/forge/canned/pathcopy), not in the live run.

## 5. Which procfs observation decides what

- Canned answerer (python holder, correct probe fields): /proc/<hold pid>/exe, cmdline, maps and the ancestry chain
  decide it (bind_exe, bind_argv, bind_maps, bind_ancestry) with listener_holders_pinned; the reference text decides
  it independently (x-m15). Both off: it passes live and the controls crash (x-m16).
- Replay forger (genuine child holder): no procfs observation decides it. Its absence is the finding: the counter never
  observes the tool's requests, so the holder observation is only a holder observation.

## 6. Other observations (minor, not forgeries)

- Hold residue: witness_run does not clear hold/release in a reused --work. A second counter run in the same --work
  made my canned tool exit before writing hold.json ("tool exited before hold.json") and produced "no witness"
  (out/score/canned-seed*.out before the rerun). This is a reuse hazard of the same class as RV03 F1, on the C1 side.
- The counter reads all tool bytes from git blobs at --tip, so its own forgery controls patch the tip text. Any edit
  that changes the text the patches apply to changes which controls run (T2 escapes), so a forger built from the tool
  text is not an independent control.

## Reproduction (L1)

The clone recipe at f6a4 plus: `python3 harness/mutate.py <id>` (writes the counter into the clone working tree,
exact-string replacements, asserted once; `restore` reverts), `python3 harness/make_replay_tool.py`,
`python3 harness/canned_answerer.py`-as-tool (needs the template at harness/genuine-receipt.json, a path hardcoded
in the forged tool), and `python3 harness/fuzz.py fresh|shared N SEED`. All paths in the harness are absolute scratch
paths; the L1 must rebind them to a fresh scratch before rerunning. SHA256SUMS in the out dir covers the counter and
both forged tools.

Final counter one-liner (SURVIVED forgery, T4): tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
