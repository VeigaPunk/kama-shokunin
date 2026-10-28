# MT14C1NonceBind — C1 counter: vacuous NONCE binding and old-receipt replay

Seat: MT14C1NonceBind (mutation-tester, leaf). Axis: operability. Milestone: falsify C1 counter.
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (amendment-1 counter `tools/round63-c1-counter.py`, blob 56c54c84).
Scratch clone: `git clone --shared` of the lane, detached at the tip; every mutant committed in the clone only. Lane, lane index, jj state and fleet untouched (read-only git only).
Tools installed: none (stock python3 3.14.8; no pacman, no installs).
Evidence: `.ufo/waves/round-63/w1/out/MT14C1NonceBind/` (replay harness, old receipts, replayed receipt, mutant diffs).

## Where the nonce is checked (tip 03a6a1d8)

- `grade()`: `out['nonce_match'] = bool(NONCE) and receipt.get('nonce') == NONCE` (line 263). `NONCE` is the module global set in `main()` from `witness_run()`'s fresh `r63-<40 bits>` value.
- `score()`: `'live_nonce': bool(NONCE) and NONCE in (w.get('sent_prompt') or '')` (line 309).
- Controls naming the nonce: exactly one, `stale` (receipt with `nonce='r60-dead'`, expects `nonce_match`). No control names `live_nonce`.
- The counter's own `observe()` always sends `f'{nonce} under the'`, so `live_nonce` is structurally true for the counter's own witness; it can only be falsified by a control that edits the witness.

## Mutants (clone commits; each run from `$D/tools/` against its committed tree)

| id | commit | change | verdict |
|---|---|---|---|
| base | 03a6a1d8 (unmutated) | none | met=True |
| M1 | 5f2d59ca | `nonce_match = True` and `live_nonce = True` (the requested mutant) | **KILLED** |
| M2 | 9bc9039e | `nonce_match = True` only | **KILLED** |
| M3 | 0ac9c1ec | `live_nonce = True` only | **SURVIVED** (met=True) |

### Counter output, verbatim (one line each)

base (unmutated, tip 03a6a1d8), exit 0:
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
M1 (both nonce checks vacuous), exit 1:
```
tool_present=1 live_ok=1/1 controls_targeted=43/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=0/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
error: escape stale expect=nonce_match fails=[]
```
M2 (`nonce_match` only), exit 1:
```
tool_present=1 live_ok=1/1 controls_targeted=43/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=0/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
error: escape stale expect=nonce_match fails=[]
```
M3 (`live_nonce` only), exit 0:
```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```

Reading: M1 and M2 are killed by the single `stale` control, which escapes with `fails=[]` (a receipt whose only defect is the nonce is scored met). M3 survives: no control in the 44 names `live_nonce`, so the witness-side nonce check can be removed with the counter still reporting met=True.

M3 is a real gap, not an equivalent mutant of the predicate: the freeze predicate says the outside request's `usage.prompt_tokens` must equal the /tokenize count "for that nonce prompt". A witness whose `sent_prompt` lacks the run nonce is never graded.

Closure experiment (clone only, not proposed as a lane edit): add one witness control `add('witness', receipt, 'live_nonce', wm(sent_prompt='no run nonce here'))` and set `EXPECT_CONTROLS = 45`.
- unmutated + control: `controls_targeted=45/45 ... met=True ... witness=7/7` (exit 0)
- M3 + control: `controls_targeted=44/45 eval_selftest=3/3 errors=0 met=False ... witness=6/7` with `error: escape witness expect=live_nonce fails=[]` (exit 1)
So one added witness control kills M3 while keeping the unmutated counter met.

## Replay of old receipts (counter-level)

Method: `replay-harness.py` loads a counter file by path, runs its real `main()` once against the tip (real hold child, real outside witness), and at the first `score()` call (the live receipt) re-scores stored receipts against the same witness and the same run NONCE. Inputs:
- `r62-final-v1` = `.ufo/waves/round-62/measured/c1-final-receipt.json` (schema v1, nonce r62-60ab035c67)
- `r62-prewave-v1` = `.ufo/waves/round-62/measured/c1-prewave-receipt.json` (schema v1)
- `v2-earlier-run` = receipt of an earlier unmutated counter run at the tip (schema v2, nonce r63-e9a146391b, child pid and port of that run)
- `+rebound-pid-port` = the v2 earlier receipt with `child_pid` and `port` overwritten to the current live witness's values
- `+rebound-pid-port+run-nonce` = additionally `nonce` set to the current run's NONCE

Results (`REPLAY <tag> ... met=... fails=...`):

Unmutated counter (03a6a1d8), run nonce r63-aae33d329e, witness pid=port matched the live child:
```
REPLAY r62-final-v1 schema=kama-completion-live/v1 nonce=r62-60ab035c67 met=False fails=['completion_headers', 'completion_prompt_tokens', 'completion_request_bound', 'completion_untruncated', 'inconsistent:missing-checks', 'live_pid', 'live_port', 'nonce_match', 'schema']
REPLAY r62-prewave-v1 schema=kama-completion-live/v1 nonce=r62-d4d183a95c met=False fails=['completion_headers', 'completion_prompt_tokens', 'completion_request_bound', 'completion_untruncated', 'inconsistent:missing-checks', 'live_pid', 'live_port', 'nonce_match', 'schema']
REPLAY v2-earlier-run schema=kama-completion-live/v2 nonce=r63-e9a146391b met=False fails=['live_pid', 'live_port', 'nonce_match']
REPLAY v2-earlier-run+rebound-pid-port schema=kama-completion-live/v2 nonce=r63-e9a146391b met=False fails=['nonce_match']
REPLAY v2-earlier-run+rebound-pid-port+run-nonce schema=kama-completion-live/v2 nonce=r63-aae33d329e met=True fails=[]
```
M1 (both vacuous) and M2 (nonce_match vacuous) on the same method:
- unmodified v1 and v2 receipts: still rejected, by `schema`, `missing-checks`, `live_pid`, `live_port` (the nonce is no longer among the failures, but the pid/port binding still rejects them).
- `+rebound-pid-port`: M1 and M2 accept (met=True, fails=[]). The unmutated counter rejects it on `nonce_match`.
- `+rebound-pid-port+run-nonce`: accepted by all three counters, including unmutated, since every binding field now matches.

So the nonce binding is the only check that distinguishes the rebound replay from a live receipt, but it is not the only defence against unmodified stale receipts (pid/port cover those).

## Replay through the tip tool (the realistic vector) — SURVIVED, prominent

The counter never reads a stored receipt; it scores whatever `kama-completion-live.py` writes at the tip. So the question "can a replayed receipt be accepted by the unmutated counter" is answered by a tool that publishes an old receipt. Probe (TOOLPROBE, clone commit 24a80206): after `run(args)`, if the verdict is REQUEST_OK, the tool replaces the receipt with the stored v2 earlier-run receipt, updated only with this run's `nonce` (from argv), `child_pid` and `port`. The hold child, the witness and the outside request are all live. Scored by the **unmutated** counter (tip blob 56c54c84):

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
```
(exit 0; run nonce r63-1b3a0eafd9, witness pid 2615454 port 45407 = receipt child_pid/port.)

Checked in the published receipt (`toolprobe-replayed-receipt.json`): every `captures[*].body_sha256` is byte-identical to the earlier run's; `at` is the earlier run's `2026-10-28T22:41:49.437Z`; `hold.dir` and `server_log` point into the earlier run's work dir. None of these is graded.

Verdict: **SURVIVED**. The unmutated counter accepts a replayed lifecycle. The predicate says the lifecycle must be run live and its receipt re-derived from captured bytes; the grader checks neither that the captures belong to this run nor the receipt's `at`, `hold.dir` or `server_log`. The only run binding is the nonce, which the tool receives on argv and echoes, so it is not a secret the tool cannot forge. The counter's own live witness constrains only pid, port, fingerprint and the live prompt-token count, and a replayed capture with the same fingerprint passes all of those.

Why the counter cannot see it: the tool's requests carry the fixed `args.prompt`, never the nonce (`grep` of tip `tools/kama-completion-live.py`: `'prompt': args.prompt` at 207/347/487, no nonce in any request), so no captured request is bound to the run's nonce by content.

## Answer to the item question

- Can a stored old receipt, unmodified, be accepted by the unmutated counter? **No.** v1 (r62 final, r62 prewave) and v2 (earlier run) are all rejected, by `live_pid`/`live_port` and `nonce_match` (and `schema`/`missing-checks` for v1).
- Can one be accepted by the unmutated counter at all? **Yes**, in two forms: (a) a receipt whose `nonce`, `child_pid` and `port` are rewritten to the current run's values (harness: met=True); (b) a tip tool that publishes a stored lifecycle with the run's nonce and child pid/port (TOOLPROBE: met=True, exit 0). Both are SURVIVED defects of the counter/control set, not of the nonce check alone: no control in the 44 targets run-binding of captures (`at`, `hold.dir`, `server_log`, captured-request nonce).
- With the nonce binding vacuous (M1/M2), (a) and (b) are accepted as well (rebound harness: met=True); unmodified replays stay rejected, by pid/port.

## Side finding: the 3-plant evaluator self-test cannot see the nonce defect

Under M1 the self-test still prints `eval_selftest=3/3`. Plant 1 (stale receipt, expecting `live_ptok`) and plant 3 (genuine receipt, expecting `nonce_match`) are refused because the re-score is met, not because the named check fails. The self-test counts "not credited", which a vacuous check satisfies. It does not test that a named check can fail.

## Recommendations (for the L1; not applied in the lane)

1. Add the witness control `live_nonce` (closure experiment above). Kills M3; keeps unmutated at 45/45 with EXPECT_CONTROLS=45.
2. Bind captures to the run: have the tool put the run nonce in the completion prompt it sends (e.g. `f'{nonce} {PROMPT}'`), grade `completion.request_body` contains the nonce, and have the counter's outside witness check `usage.prompt_tokens` against the *captured* prompt rather than a fixed one. Add controls for `at` outside the run window, `hold.dir` not equal to this run's, and `server_log` not under this run's work dir. Each needs a control naming it, under the cap.
3. Make the self-test check that a named check can fail (plant a receipt whose only defect is the named check and expect it in fails), not only that a credited control is refused.

## Tally

M1 KILLED (stale=0/1, met=False) · M2 KILLED (stale=0/1, met=False) · M3 SURVIVED (met=True, witness=6/6, no control names live_nonce) · tool-replay probe SURVIVED (unmutated counter met=True, exit 0) · old unmodified receipts accepted by unmutated counter: none (r62 v1 ×2, v2 earlier ×1 all met=False) · rebound/replayed receipts accepted by unmutated counter: yes (harness +rebound-pid-port+run-nonce; tool probe).

Scratch `/fast/scratch/hyaku/kama-r63/w/MT14C1NonceBind` removed after evidence copy.
