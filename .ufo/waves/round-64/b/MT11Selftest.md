# MT11Selftest - C1 evaluator self-test attack (round 64, wave b)

Seat: MT11Selftest (leaf, mutation-tester). Item: falsify the counter's evaluator
(`tools/round64-c1-counter.py` at tip f6a4ea9a8b5a876d685b08e7e582ec0723412a4a).
Evidence: `.ufo/waves/round-64/b/out/MT11Selftest/` (outs/, receipts/).
Scratch clone `/fast/scratch/hyaku/kama-r64/b/MT11Selftest/clone` (base f6a4ea9), restored to clean after every mutant; scratch removed at yield.
Tools: none installed or upgraded. Python 3.14.8; the counter's pinned `llama-server` (~/.local/bin, sha-checked by the counter). No pacman. No ports other than the counter's `free_port()` loopback ones touched.

## 0. Baseline (honest tip, shipped counter)

```
tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
```
exit 0, 8.5 s. Honest baseline is met=True.

## 1. What the evaluator actually does (read from the tip file)

- `is_hit(s, expect, cap)` (L1218): `(not met) and expect in fails and len(fails) <= cap`. The `not met` conjunct is redundant (met = not fails, and `expect in fails` implies not met): dead, equivalent.
- `EXPECT_FAMILIES` (L58) is compared by dict equality on both `fam_tot` and `fam_ok` (L1509). Families are the only gate on per-family accounting.
- `score_run` (L1528) adds `live_nonce` when the counter's outside probes' `sent_prompt` lacks the per-run probe nonce. `sent_prompt` is `http()`'s request bytes (`probe()` L777, `http()` returns `request_bytes`): the counter's own payload. The nonce check is therefore structurally unable to fire on any live run; it is a dead guard. No build_controls entry has `live_nonce` as its expected name.
- `credit(..., clean_receipt=True)` (L1555) applies the receipt-level veto only to the 7 fake-template scenarios (`plan`, L1592). The forged-tool credits (`forge`, `relabel`) use no veto.
- `eval_selftest_run` (L1537) has 3 cases: (1) stale nonce vs `live_ptok` must be refused; (2) the envelope edit (26 fails) vs `completion_envelope` at default cap 5 must be refused; (3) genuine receipt vs `nonce_match` must be refused. **No case requires a credit.** There is no positive control.
- Note on case 2: it is a cap plant. The envelope cascade is refused only because it exceeds MAX_COLLATERAL=5, which is the intended refusal (the same edit is credited in the `tamper` family under ENVELOPE_CAP=30). It is not an accident.

## 2. Mutant verdicts on the shipped counter (honest tip)

Each mutant is an edit of the clone's counter file (uncommitted), run from the clone path with `--tip f6a4ea9`; the committed tool is unchanged. Each was restored with `git checkout` before the next run.

| # | Mutant (edit of the counter) | Honest-tip output | Verdict | Deciding gate |
|---|---|---|---|---|
| M1 | `is_hit` ignores cap: `return (not s['met']) and expect in s['fails']` | `eval_selftest=2/3 ... met=False` | **KILLED** | self-test case 2 (the over-cap envelope cascade is no longer refused). Families unchanged (tamper uses cap 30). |
| M2 | family match compares totals only: `fam_match = total == EXPECT_CONTROLS and rejected == EXPECT_CONTROLS` | `families_exact=1 ... eval_selftest=3/3 ... met=True` | **SURVIVED** | none (honest run has exact families) |
| M3 | exception path credits fam_ok: in the plan `except` (L1619-1621) add `fam_ok[fam] += 1` | `... met=True` | **SURVIVED** (path not reached on honest run) | would be `errors` only (see plant P-E) |
| M4 | score_run skips probe-nonce check: `if False and not all(...)` | `... met=True` | **SURVIVED** (dead guard) | none (see plant P-B) |
| M5 | `clean_receipt` credit is a no-op: `if False and hit and clean_receipt:` | `... met=True` | **SURVIVED** (veto never fires on honest run) | none (see plant P-C) |
| M9 (extra) | always refuse: `is_hit` returns `False` | `controls_targeted=0/76 ... eval_selftest=3/3 ... met=False` | KILLED by families only | families gate; the self-test passes 3/3 |
| M10 (extra) | always accept: `is_hit` returns `True` | `controls_targeted=76/76 ... eval_selftest=0/3 ... met=False` | KILLED by self-test only | self-test case set |

Full M-lines (copies in out/outs/m*.out):

```
M1  tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=2/3 errors=0 met=False families[... all k/k ...]
M2  tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[... all k/k ...]
M3  tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[... all k/k ...]
M4  tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[... all k/k ...]
M5  tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[... all k/k ...]
M9  tool_present=1 live_ok=1/1 controls_targeted=0/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=0/20 canned=0/1 ... witness=0/5]
M10 tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=0/3 errors=0 met=False families[bind=20/20 canned=1/1 ... witness=5/5]
```
(`[... all k/k ...]` = the baseline family list, unchanged; full text in out/outs/.)

Which procfs observation decides: **none of these mutants is decided by a procfs read at scoring time.** Every verdict is pure arithmetic over the receipt, witness and binding already captured by the live run. The procfs observations enter only as named checks (`bind_*`, `hold_fresh`, `teardown_observed`) that a credited control must trip. P-C below is the one place where a procfs check is load-bearing: the fake `detach` must trip `bind_ancestry` for its credit; the receipt veto is the decider on top of that.

## 3. Plants: does a planted, real defect make each survivor flip?

Plants are edits of the clone on top of the shipped counter. Each planted run is compared to the shipped counter running the same plant.

| Plant | What it does | Shipped counter + plant | Mutant + plant | Survivor flipped? |
|---|---|---|---|---|
| P-A positive case | add `health` body `{"status":"OK"}` vs `health_ready`, must be credited; `EXPECT_EVAL_SELFTEST=4` | `eval_selftest=4/4 ... met=True` | M9 + P-A: `eval_selftest=3/4 ... met=False` | yes for M9 (self-test alone now kills refuse-all) |
| P-B witness nonce | witness control: probe0 `sent_prompt='no nonce here'`, expect `live_nonce`; `witness` family 5→6 | `controls_targeted=77/77 ... witness=6/6 ... met=True` | M4 + P-B: `controls_targeted=76/77 ... witness=5/6 ... met=False`; `escape witness/live_nonce expect=live_nonce met=True nfails=0` | **yes** (M4 killed) |
| P-C garbled fake template | `tpl` written with health body `{"status":"OK"}`: all 7 fakes carry a receipt-level failure (`health_ready`) | `controls_targeted=69/76 ... met=False` (7 escapes: "fails=['bind_ancestry','health_ready','inconsistent:health_ready']" etc.) | M5 + P-C: `controls_targeted=76/76 ... families_exact=1 ... met=True` | **yes** (M5 accepted, shipped rejects) |
| P-D family misfile | `add('stale', 'nonce_match', ...)` relabelled as `'log'` | shipped: `families_exact=0 missing_families=['stale'] ... met=False` | M2 + P-D: `families_exact=1 missing_families=['stale'] ... met=True` | **yes** (M2 accepted; the output line itself is self-contradictory: `families_exact=1` next to `missing_families=['stale']`) |
| P-E exception | plan mode `'cannedX'` (KeyError in `write_fake`) | shipped: `controls_targeted=75/76 ... families_exact=0 ... errors=1 met=False`; `error: fake canned: KeyError: 'cannedX'` | M3 + P-E: `controls_targeted=76/76 ... families_exact=1 ... errors=1 met=False` | no flip in `met` (both False); M3's family accounting does differ (`canned=1/1`), and only the `errors` gate holds it |

Probe-nonce note: P-B's probe0 `sent_prompt` edit is credited by the shipped counter as `live_nonce` within the cap of 5 (`witness=6/6`, `met=True`); the M4 run shows the same control escaping with `fails=[]` once the check is gone.

## 4. The valuable survivor (forgery shape)

The shipped counter's clean-receipt veto is not pinned by any control on the honest path. Minimal clone edit: M5, i.e. `if False and hit and clean_receipt:` (the veto block at L1557-1562 disabled). On the honest tip this prints `met=True`. The forgery shape that the veto exists to reject is a fake tool that holds a genuine receipt copy but garbles one receipt-level check; P-C reproduces that exact shape for all seven fake scenarios (template with `health_ready` failing). Shipped: `met=False`, 7 escapes. M5: `met=True`, 76/76. So a future edit that drops the veto would ship a counter that credits forged fakes, and no honest-run control catches it. This is the strongest survivor.

Probe-nonce check (M4) is the second: it is dead code on every live run, because the counter writes its own nonce into the requests it inspects. It only fires on an offline edit of the witness (P-B). It can never see a forgery.

## 5. Proposed self-test plants (for L1 to consider as an AMENDMENT; I did not edit the instrument)

1. **Positive control** (P-A): add one credited case to `eval_selftest_run` and set `EXPECT_EVAL_SELFTEST=4`. Without it the self-test accepts an evaluator that refuses everything (M9: `eval_selftest=3/3`, killed only by families). Verified: M9+P-A -> 3/4.
2. **Family exactness as a function**: factor `fam_match` into a pure function and have the self-test require it False on a misfiled dict (P-D). Kills M2 (verified via P-D run).
3. **Nonce check exercised**: an offline self-test case: score_run on a witness whose probe sent_prompt lacks the nonce must have `live_nonce` in fails (P-B). Kills M4 (verified). Alternatively delete the dead guard; the L1 decides, since either removes the equivalent-survivor.
4. **Clean-veto exercised**: an offline self-test case: credit of a fake whose failure set includes a RECEIPT_LEVEL name must be refused (P-C). Kills M5 (verified via the P-C run).
5. **Exception accounting**: a self-test that drives a plan entry through an unknown mode and requires `met=False` (P-E). Only the `errors` gate kills M3; this just pins it.
6. Keep the existing case 2 (cap plant); it is what kills M1 and is correct as written. Rename its comment so it reads as a cap plant, not a wrong-reason plant.

Each proposal changes the evaluator, so under the freeze it needs a numbered AMENDMENT committed before the next wave. I did not edit the instrument.

## 6. Summary

- Shipped counter kills: M1 (via the cap plant), M9, M10. Does not kill: M2, M3, M4, M5 (all met=True on the honest tip).
- Plants: P-A (positive control) is the one plant that exposes refuse-all to the self-test (M9 + P-A: `eval_selftest=3/4`). P-B, P-C and P-D each flip `met` in the planted run: M4 via P-B (`met=False`), M5 via P-C (`met=True` while shipped is False), M2 via P-D (`met=True` while shipped is False). P-E does not flip `met` for M3; only the `errors` gate holds it.
- The self-test as shipped is one-sided: it proves refusal, never credit. Refuse-all passes it 3/3 and is caught only by family accounting.
- No procfs observation decides any evaluator verdict; procfs enters only as named checks that controls must trip.

## 7. Receipts and cost

- 19 live counter runs including the diagnostic instrumented run (base, M1, M2, M3, M4, M5, M9, M10, plus P-A/P-B/P-C/P-D/P-E originals and their mutant pairings), each 8-10 s; exit 0 or 1 as the counter's met gate says.
- Diagnostic instrumented copy (prints per-is_hit fail sets): out/outs/diag-*.
- Base live receipt: out/receipts/base-live-receipt.json.
- Clone restored to f6a4ea9 (git status clean); scratch root removed at yield.
- Operability note (the bash wrapper): a counter run that exits 1 aborted the rest of my chained command, so cleanup was re-issued in a separate call each time. No state was left behind; confirmed clean.

tally (for the L1): base met=True 76/76; shipped mutants killed by counter output = 3/7 (M1, M9, M10 extra); survived = 4 (M2, M3, M4, M5). Plants flipping `met` on their survivor = 3/4 (P-B for M4, P-C for M5, P-D for M2); P-E holds M3 by `errors` only.
