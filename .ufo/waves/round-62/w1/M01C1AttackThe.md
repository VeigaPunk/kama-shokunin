# M01C1AttackThe — C1 receipt tamper probe

Report: `.ufo/waves/round-62/w1/M01C1AttackThe.md`

**Axis:** operability. Counter source loaded from `master:tools/round62-c1-counter.py`; obtained a fresh live receipt with the counter at tip `65d7cad0fce90e34de37527cde22e97b63b118bf` in my isolated scratch. Counter's own actual output: `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True`.

The scratch replay attempted the eight `main()` tamper-family mutations and three additional forgeries, reproducing `grade()` and `score()` from the committed counter and supplying a witness matching the receipt nonce, PID, port, alias, pinned digests and fingerprint. **Replay was inconclusive:** before it could produce any mutation verdict, `score()` raised `AttributeError: 'NoneType' object has no attribute 'get'` at `grade()` line 130 (`u = cj.get('usage') or {}`). Thus no ACCEPTED/REJECTED claim is made for any forgery. The receipt is parseable (9,443 bytes; completion capture 593 bytes), and the counter's own live/control pass was successful. This is a replay harness/evidence discrepancy, not evidence of a surviving mutant.

Mutations attempted in order: completion envelope body `text_completion`→`chat.completion`; `hold.released=false`; `teardown.child_pre_dead=true`; `teardown.returncode=137`; `teardown.port_closed=false`; verdict `FAIL`; completion2 `text` key→`content`; both pinned digests replaced by zeroes. Additional attacks: add fabricated capture entry; delete `checks.health_ready`; rename `verdict` to `result`. All three additional attacks likewise have no score output because replay failed before a verdict.

Pristine `score()` baseline: same exception (not a passing baseline). Therefore per protocol this run cannot classify mutations as killed or survived. No tools installed/updated. Scratch cleanup was performed before returning; live receipt and exact output are retained in the wave evidence directory.
