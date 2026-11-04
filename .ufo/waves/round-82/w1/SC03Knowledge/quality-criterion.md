## Criterion added — round 82 (2026-11-04; no outside review yet)

KQ133 stays in force. This row carries the round-82 mined mistake — a rule's prose says "a row's
introducing commit" while its code resolved one `git log --diff-filter=A` commit for the whole
register, so a late register could never accept an event created after it first existed — into one
admission check: prose and code resolve the same identifier, and the repair is disclosed with a
red-before receipt and a red-capable arm.

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ134 | A rule's prose and its code resolve the same identifier: when a rule says "a row's introducing commit", the instrument resolves that row's own introduction (`git blame` on the register line in round 82), never one commit for the whole container; a repaired instrument keeps its rule sentences and adds a red-capable arm that fails under the old resolution. Check: `tools/round81-append-debt.py`'s `blame_rows` resolves each late row's own introducing commit, and its `row-intro-later`, `row-intro-earlier` and `row-intro-unbound` selftest arms cover the row-level reading (`pass=25` with them), the first red under the register-level resolution. | The rule sentence is rewritten to match the code instead of the code to the rule; a docstring or prose note substitutes for an arm; the repair has no committed red-before receipt (`c2-debt-register-level-before.out`), or no arm can fail under the old resolution; a register whose introduction postdates every graded event is treated as unable to accept (the conflation this row forbids). | `corpus/lessons/round-82.md` §Mistakes (`register-introduction-conflated`); `tools/round81-append-debt.py` `blame_rows` + `row-intro-*` arms; red-before `.ufo/waves/round-82/measured/defects/c2-debt-register-level-before.out`. |
