# EX01FreezeAuditControl — control of the C3 instrument (`tools/round95-freeze-audit.py`)

## Scope

Read-only control of the round-95 C3 counter: (a) `--selftest`; (b) runs on the round-95 plan at the freeze
commit F and at the lane tip, and on the round-94 plan at its freeze `285f1783` and at the tip, and on the
round-93/round-92 plans at their freeze commits; (c) ten forged plans committed in one scratch clone; (d) the
receipt-defect classes the tool cannot see. Revisions measured: B `2011161d5e5612fa953708cf54084b7f10ce99b1`,
F `c798e831d6703428563a70789d1252dc39503d60`, M1 `f63256607916cdeb35580a7af315b5f4b54eba18`, M2
`beef89229c0d6c5b42f1ed937b857648c535c6cf`, tip-at-end `bba10f75b18c7219446da7d2bca81995a381fd7a` (master moved
from M2 to `719214fa` + `bba10f75` while the control ran; both r94 tip runs agree). Counter bytes:
sha256 `3f76d26754705c04098f726f3a2ea2e20a86e2637edb2a51ab5aef0809a82cce` at B/F/M1/M2/tip/worktree — identical,
and `git diff c798e831 bba10f75 -- tools/round95-freeze-audit.py` is empty. No load raised, no burners, no
network, no tool installs, no lane edit (I wrote only this file and my out dir; the LOG.md/SCORECARD.md/
measured/c1.out modifications and `w1/` untracked files predate me).

## Commands and outputs (true exit codes)

1. `python3 tools/round95-freeze-audit.py --selftest` → `FREEZE_AUDIT_SELFTEST pass=5 fail=0`; **exit 0**
   (`out/EX01FreezeAuditControl/selftest.out`).
2. r95 plan @ F: `--repo . --rev c798e831` → `FREEZE_AUDIT receipts=7 present=7 missing=0 tokens=0 matching=0
   cited=17 unresolved=4 met=False`; **exit 1** (S616, S617, S616, S617 — both rows land at M2, not F).
3. r95 plan @ `beef8922` and @ `bba10f75` → `... cited=17 unresolved=0 met=True`; **exit 0** (identical both).
4. r94 plan @ `285f1783` → `receipts=12 present=0 missing=12 tokens=0 matching=0 cited=11 unresolved=4
   met=False`; **exit 1**; 12 `FREEZE_AUDIT_MISSING`, `FREEZE_AUDIT_TOOL_MISSING
   tools/round94-router-budget.py`, `tools/round94-setter-sweep.py`, 4× `S604`. Byte-identical to the committed
   `controls/c3-base.out` (`c3_base_exit=1`) — the control receipt is truthful.
5. r94 plan @ `beef8922` and @ `bba10f75` → `receipts=12 present=9 missing=3` (`controls/c1-forgeries.py`,
   `controls/c2-forgeries.py`, `w1/SC02ProbeVerdictSweep.md`) `unresolved=0 met=False`; **exit 1**.
6. r93 plan @ `0f272a37` → `receipts=14 present=14 missing=0 tokens=0 cited=14 unresolved=8 met=False`;
   **exit 1** (S600–S603 ×2; rows added at `ee19acbd` after its freeze). jj-keep twin `6c2a2fae` same tree,
   same line.
7. r92 plan @ master freeze `309eadaf` → `receipts=9 present=8 missing=1` (`controls/c2-forgeries.sh`)
   `cited=10 unresolved=4 met=False`; **exit 1** (S596/S597 ×2). jj-keep `2bde82c6` has identical plan bytes
   but a SOURCES tree where S596/S597 resolve → `unresolved=0` (**exit 1**, missing receipt only).
8. Amendment 1 predicate @ `bba10f75`: `--plan plans/round-95-amendment-1.md` → `receipts=9 present=9
   missing=0 tokens=24 matching=24 cited=14 unresolved=0 met=True`; **exit 0** — reproduces the amended claim
   and the working-tree `measured/c3-amended.out`. Same command @ `c798e831` → `FREEZE_AUDIT
   could-not-evaluate: ... absent`; **exit 2**.
9. Ten forged plans, one scratch clone @ `1e6968127e42d5304586339035689194bcce4686` (`out/.../forgeries.out`):
   ghost receipt → 1 MISSING **exit 1**; ghost token same line → `TOKEN_MISSING ...:ghost_metric` **exit 1**;
   rejected S-rows S024/S026 → `cited=2 unresolved=0 met=True` **exit 0**; two-line predicate with
   `ghost_metric=0` → `tokens=0 ... met=True` **exit 0**; `missing_paths=0` (dict key, never printed) →
   `tokens=2 matching=2 met=True` **exit 0**; `missing=999 present=999` → **exit 0**; `controls/x.out:12` +
   bare names → `receipts=0 met=True` **exit 0**; fabricated-content receipt → `present=1 met=True` **exit 0**;
   directory `.ufo/waves/round-95/controls/` → `present=1 met=True` **exit 0**; unbackticked command +
   ghost token → **exit 0**.

## Findings

**F1 BLOCKER (false green, frozen sentence not enforced).** The cited-S-id gate reads the access date, not the
status: `tools/round95-freeze-audit.py:76-77` stores `cells[8]`, but the SOURCES table's status is `cells[7]`
(`opened` is 8). `sources_status` returns `S024 -> '2026-10-19'`, `S030 -> '2026-10-19'` while both rows carry
`| rejected | 2026-10-19 |`; corpus-wide cells[7] is `{mined:321, queued:8, rejected:28}` and cells[8] is 18
dates. The `elif st == "rejected"` branch (line 128) can never fire on all 28 rejected rows, contradicting the
frozen plan:122 ("`status` not `rejected`") and the tool's own docstring:27 ("`mined` or `queued`"). Forged plan
I rejected-S-rows passes `unresolved=0 met=True`. The counter is frozen (K2), so this sentence needs an
Amendment-2 narrowing or the arm is dead for the round.

**F2 DEFECT (token arm accepts unprinted metrics and arbitrary values).** Tokens are read only from a line that
also holds a backticked `python3 tools/<tool>.py` (lines 104-119), and only the *name* is checked as a substring
of the tool's bytes (line 119) — the value is never compared. All four shipped plans (r92 line 46, r93 line 54,
r94 line 57, r95 line 111) put the quoted output on the line after the command, so every real run reports
`tokens=0` — the M6 protection has never fired in situ (F, r92, r93, r94 all `tokens=0`). Forged plans: a ghost
metric on the next line passes; `missing_paths=0` passes because it is a Python dict key, not a printed metric;
`missing=999 present=999` passes. Amendment 1 rewrote its own lines to one line and now gets `tokens=24`, which
proves the arm is line-scoped, not metric-scoped.

**F3 DEFECT (frozen C3 predicate false at F; acknowledged by Amendment 1).** At F the run is
`receipts=7 present=7 missing=0 tokens=0 matching=0 cited=17 unresolved=4 met=False`, exit 1 — C3's own K1
fires, because S616/S617 are committed at M2 (`beef8922`). Amendment 1 narrows C3 to the landed tip and that
narrowed predicate reproduces green (9/9/24/24/14). The frozen sentence remains false as written.

**F4 DEFECT (round-94 M5 class survives, and C3 cannot see it).** `plans/round-95-claims.md:27-28` names
`harm-base.out` and `harm-tip.out` as "committed with M1/M2"; no round-95 harm receipt exists in any git
object (`git rev-list --all --objects | grep -E 'round-95/.*harm'` empty), and M1's tree carries none, so C1's
K2 phrase "the base harm receipt the M1 commit carries" (plan:59) is unfalsifiable from the repo. The names are
bare (no backticks, no `controls/` prefix), so the audit's receipt arm ignores them — exactly the M5 class.
Amendment 1 adds c1/c2/c3/census receipts but no harm receipt.

**F5 NOTE (path-form coverage).** Receipts count only when backticked and matching `.ufo/waves/round-N/...` or
`controls|measured|w\d/...<ext>` (lines 44-45). `controls/x.out:12`, bare `harm-base.out`, `gates/x.json`,
`final/x.out` and all unbackticked names are invisible — the plan's five measurement-time names are
unbackticked, so `receipts=7` never covered them (forged plans G and J, exit 0).

**F6 NOTE (counting semantics; content ungraded, disclosed).** A directory counts as a receipt
(`.ufo/waves/round-95/controls/` → present; round-94's 12 included `.ufo/waves/round-94/controls/`), and any
backticked mention counts — Amendment 1's 9 includes two prose-mentioned `measured/*.out`. `controls/
c2-section-candidate.md` (a 144-line draft section, not a run output) is counted as a receipt. Forged
fabricated receipt passes; content-level forgeries are the disclosed limit (Amendment-1 M4) but remain the
largest class the name-based audit cannot catch.

**F7 NOTE (rev selection).** jj-keep twins have different trees: for r92, `2bde82c6` (tree includes S596/S597)
gives `unresolved=0` where master freeze `309eadaf` gives `unresolved=4`; the tool grades whatever rev it is
handed and cannot tell a canonical freeze from a working-copy snapshot.

**F8 NOTE (selftest blind spots).** `--selftest` 5/5 covers ghost receipt, present count, same-line ghost token,
clean plan, token count ≥3 — none of F1, F2, F5, F6. K3 can stay green with the rejected arm dead.

**F9 NOTE (positive calibration).** The presence arm discriminates correctly on history: r94 at its freeze
(12/0/12 + missing tools + S604), r93 at its freeze (S600–S603 unresolved because the rows landed later), r92 at
its master freeze (1 missing receipt + S596/S597 unresolved). The instrument is a real red/green oracle for
physical presence; the weak arms are token semantics and row status.

## Deliverables

`out/EX01FreezeAuditControl/`: `selftest.out`, `control-runs.out` (all plan runs + exits), `forgeries.out`
(10 forged runs + exits), `sources-index.out` (S024/S030/S593 + column histogram proof), `counter-identity.out`
(sha256 across revs), `forged-plans/` (10 plan sources + fabricated receipt). Scratch clone removed before yield.

VERDICT: partial — the amendment's narrowed predicate reproduces at the tip (9/9/24/24/14, exit 0) and the presence arm reddens the historical plans, but frozen C3 is false at F and the counter's rejected-status arm is dead on all 28 rejected rows while its token arm accepts unprinted metric names and arbitrary values.
