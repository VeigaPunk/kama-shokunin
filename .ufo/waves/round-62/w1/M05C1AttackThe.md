# M05C1AttackThe — C1 predead mutation probe

- Axis: operability.
- Counter source: `master` = `65d7cad0fce90e34de37527cde22e97b63b118bf`; extracted `tools/round62-c1-counter.py` SHA-256 `275610b51eb1be219cdaa3c3e15e3568b590f35e7a1b3ceb42ab0374243f4d8d`.
- Baseline receipt: `/fast/scratch/hyaku/kama-r62/measure/c1b/receipt.json`, schema `kama-completion-live/v1`; receipt bytes copied into scratch and output below. `grade()` requires stored check names exactly equal recomputed graded names. The committed receipt has an additional `checks.hold_released`, so it yields `inconsistent=['unexpected-checks']` and score `met=False`; the counter invocation itself also failed while processing controls at `grade()` (`AttributeError: 'NoneType' object has no attribute 'get'`, line 130, after the tamper mutation makes completion JSON unparsable). Thus the literal unmodified committed receipt is not accepted by the extracted grader; baseline is inconclusive as a counter run.
- To isolate the requested predicate, reconstructed the grader's expected check shape from that receipt by removing only the extra `checks.hold_released` key. No other receipt fields were changed. Supplied an in-memory witness satisfying the live predicate (status 200, matching alias/PID/port, valid fingerprint, nonce-bound prompts, listener owned, pinned digests). In this shape, pristine score is `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}`.

| Receipt mutation | Result | `score()` output |
|---|---|---|
| `teardown.child_pre_dead=true` | REJECTED | `{'met': False, 'alltrue': False, 'verdict_ok': True, 'live': True, 'inconsistent': ['teardown_clean']}` |
| Child died mid-hold, but receipt says `child_pre_dead=false`, `returncode=-15` | ACCEPTED | `{'met': True, 'alltrue': True, 'verdict_ok': True, 'live': True, 'inconsistent': []}` |
| Child died mid-hold, but receipt says `child_pre_dead=false`, `returncode=0` | ACCEPTED | `{'met': True, 'alltrue': True, 'verdict_ok': True, 'live': True, 'inconsistent': []}` |

**Falsification (verbatim):** The C1 receipt grader accepts a receipt with `teardown.child_pre_dead=false` and `teardown.returncode=-15` (or `0`) as `met=True`, even when the child in fact died during the hold. `grade()` derives teardown cleanliness solely from `not td.get('child_pre_dead') and td.get('returncode') in (0, -15)`; it does not bind these claims to teardown event evidence. This falsifies receipt-byte-only detection of mid-hold death; `child_pre_dead=true` itself is rejected, but changing that field to false evades the predicate.

Evidence files retained in `.ufo/waves/round-62/w1/out/M05C1AttackThe/`: `receipt-pristine.json` (copied receipt), `pristine.json` (expected-shape baseline), `child_pre_dead-true.json`, and two forged receipts (`child_died_mid-hold_but_false,_returncode--15.json`, `child_died_mid-hold_but_false,_returncode-0.json`). No tools installed. Scratch removed after copying evidence. Counter tally: unable to produce because the counter errored during control grading; traceback noted above.

Report: .ufo/waves/round-62/w1/M05C1AttackThe.md