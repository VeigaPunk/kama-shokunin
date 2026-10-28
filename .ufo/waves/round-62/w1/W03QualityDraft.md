# W03QualityDraft — three QUALITY criteria drafted from round 62

Seat: W03QualityDraft (scribe, advisory leaf). Axes: operability + calibration.
No commit, no lane-source edit outside this report, no verdict on C1/C2, no subagent dispatch.
Read first: `.ufo/waves/round-62/controls/freeze.txt` (base `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`,
do-nothing receipts `c1-base.txt` / `c2-base.txt` beside it).
Lane tip at the start and end of this seat: `65d7cad0fce90e34de37527cde22e97b63b118bf`
(`git rev-parse master`, read-only).
Scratch: `/fast/scratch/hyaku/kama-r62/w/W03QualityDraft/` — created with `mkdir -p`, passed explicitly,
removed before return; the one receipt is copied here as `probe-output.txt`.
Tool installs: **none**. No pacman transaction was attempted (host-wide pause honoured); nothing was
installed or upgraded, so there is no tool/version/channel/reason row to record.

## 1. Integration-ready text (mirrors `corpus/QUALITY.md`; appended at the end, no earlier line moves)

```markdown
## Criteria added — round 62 (drafted by wave seat W03QualityDraft; each cites `corpus/lessons/round-62.md`)

No earlier criterion is superseded. KQ95's evidence-pointer rule and KQ20/KQ99's rule that a graded
field must be able to fail remain in force. KQ102 binds a capability row to a frozen executable
template; KQ103 makes a frozen counter's crash on malformed input a recorded pre-freeze defect;
KQ104 narrows a scan-bound claim to its class census. Same columns as the table above; appended at
the end so no existing line moves.

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ102 | A capability self-assessment row is admitted only when (a) the newest `**Capabilities — canonical list as of round N**` section of `SCORECARD.md` carries it exactly once with its frozen row prefix, (b) `registry/capability-claims-r62.tsv` binds it to exactly one allowed frozen template — binding id, `run` string with its `%T` tip-tree, `%S` scratch, `%R` repo and `TIPREV` tip placeholders, and the `pattern` the run must emit — with no second row or free-form command claiming the same capability, (c) that template is executed at the measured tip in a scrubbed environment with a scratch `TMPDIR`, and (d) the emitted verdict equals the recorded one, no bound target path is dead, and the row is sensitive in a way the same predicate can fail: the decisive substring is mutated in the run's output and the row re-scored as a mismatch, so a green row cannot stay green when its evidence changes. Gate: `mismatches=0 dead=0`, every control family rejected, `errors=0`. | A paraphrase or shortened pattern (`weak`: `pass`), a free-form command (`free`: `bash -c "echo ok"`), a `notobs` or self-reported binding, a renamed or duplicated slug, a verdict re-read from the row's own cell. A sensitivity leg that only asks whether the pattern survives the replacement text the test wrote itself does not show the row depends on its evidence: `sensitive = not (pattern in out.replace(pattern, MUT) …)` is true for every green, non-dead row of the frozen r62 manifest. | `controls/c2-base.txt` at `a959fd90`: newest canonical list lacked the r61 row (`prefix:live-ollama-lifecycle`), `registry absent`, exit 1; r62 adds the row (`SCORECARD.md:3272-3289`, 12 rows) and `tools/kama-live-replay.py`'s scratch-root `makedirs` fix so `live-receipt-replay` emits `KLR_SELFTEST pass=48 fail=0`. Fixed sensitivity conjunct: `tools/round62-c2-counter.py:269-271`; `out/A05C2Sensitivity/sensitivity-probe.txt`; `corpus/lessons/round-62.md` `vacuous` row. |
| KQ103 | A frozen counter is evidence about receipts only when it is survivable to adversarial receipts: for each malformed or tampered input class the claim names — empty receipt, absent or non-object `captures`, non-string `body`, a `body` whose sha256 disagrees with the recorded one, wrong container types for `checks`/`usage`/`timings` — the counter reaches a declared not-met verdict or a declared error count, never an uncaught exception, and each class's disposition is recorded with the claim. A crash on malformed input is a counter defect recorded pre-freeze-fix: the record names the counter path, its byte revision (sha256 or `rev:path`), the raising line and the input; the fix is a pre-freeze build, and the frozen bytes are the fixed bytes. A guard that exists only in an uncommitted working tree is a defect record, not a repair; `met=True` from bytes other than the frozen tip's is not survivability evidence. | `AttributeError: 'NoneType' object has no attribute 'get'` at `tools/round62-c1-counter.py:130` from the tip blob on `{}` and on the counter's own `tamper[0]` input (completion body changed, `body_sha256` stale), i.e. the frozen blob aborts its control loop before printing a summary. Reading a traceback as a rejected control, or as `errors=0`. | `corpus/lessons/round-62.md` Mistakes row `vacuous` (C1 body-hash mismatch) with `.ufo/waves/round-62/measured/c1-before-fix.txt`; reproduced from the tip blob by `out/E01CompletionRepeat/tipblob.stderr.txt` (3/3) and by this seat (`out/W03QualityDraft/probe-output.txt`). KQ24/KQ25 keep an exception in its own class. |
| KQ104 | A claim whose decisive output is a scan's residual (`unknown=0` from `tools/digest-ledger.py scan` or `tools/hexrun-census.py scan`) is admitted only when the round prints the scan's whole class census — every class key the tool emits with its count, zeros included (for these two tools `tokens`, `distinct`, `blob`/`lane_oid`, `md5_blob`, `external_ok`, `external_absent`, `upstream_ok`, `unverifiable`, `wrong_flagged`, `ledger_bad`, `wrong_unflagged`, `unknown`) — states the population those counts are over, and gives every non-lane class its rule: an `unverifiable` token's note and re-verification route, a `wrong` token's linked correct run, an `upstream` token's committed evidence file that contains it, and an `external_absent` token named as classified but not confirmed. A ledger row added in the round classifies a token only where re-deriving its class rule decides that token; a row that merely names it does not. | A claim resting on `unknown=0` alone while `unverifiable`, `wrong_flagged`, `external_absent` or `ledger_bad` carry the rest; a residual `unknown` (or synonym) bucket holding any token; a scan over an unstated or truncated population; ledger rows written only to empty `unknown`; `unverifiable` rows whose note gives no reason or route. | The r62 bound scan rows take `unknown=0` as their decisive substring (`registry/capability-claims-r62.tsv:9-10`), while the same tip runs print `unverifiable=7 external_absent=1 wrong_flagged=1` and `unverifiable=9 wrong_flagged=3` beside the zero (`out/E05LedgerScans/digest-scan-tiprev.txt`, `hexrun-scan-tiprev.txt`); the fleet commit ids the lane cites are `upstream` only through `.ufo/waves/round-62/census/fleet-commit-evidence.json`. |

Drafted by wave seat W03QualityDraft (`.ufo/waves/round-62/w1/out/W03QualityDraft/`), for integration
by the kama L1, round 62. KQ102 supplements KQ95 and KQ99; KQ103 carries the round's
`measured/c1-before-fix.txt` record into the instrument-admission rule; KQ104 narrows KQ50/KQ55's
scan evidence to the census the claim must print.
```

## 2. Grounding

### 2.1 KQ102 — a capability row binds a frozen executable template

- Population and base: the C2 counter freezes 12 capabilities and the base receipt prints
  `population=12 rows=0 covered=0/12 bound=0 … canonical=49 … errors=3 met=False`, with
  `error: canonical rows must contain each frozen capability once: [...]`, `error: prefix:live-ollama-lifecycle`,
  `error: registry absent` (`controls/c2-base.txt`, base `a959fd90`).
- The newest canonical section at the tip is `SCORECARD.md:3272` `**Capabilities — canonical list as of round 62**`,
  with 12 rows (last row `live-ollama-lifecycle`, first-working round 61) and the note that
  `tools/kama-live-replay.py` gained a scratch-root `makedirs` fix so the bound row emits
  `KLR_SELFTEST pass=48 fail=0`.
- `registry/capability-claims-r62.tsv` carries 12 bound rows; the `run` cell equals the manifest template
  and the `pattern` cell is the decisive output substring (e.g. `45/45 selftest cases passed`,
  `"outcome": "pass"`, `"all_ports_closed": true`, `KLR_SELFTEST pass=48 fail=0`).
- Control families the frozen counter builds for this criterion (`tools/round62-c2-counter.py:292-348`):
  `drop`, `rename`, `binding` (live→selftest id swap), `verdict` (true→false), `quote` (paraphrase),
  `free` (`bash -c "echo ok"`), `weak` (`pass`), `notobs` — exactly the shapes KQ102 rejects.
- Sensitivity is a predicate member: `score()` adds `mismatches` when `not sensitive` (`:233-235`),
  and `run_bound` computes `sensitive = not (tpl['pattern'] in mut and rc == 0 and not dead)`
  with `mut = out.replace(tpl['pattern'], MUT)` (`:269-271`). A07/A05 seats attack that leg;
  A05's receipt shows the leg is not literally constant (`P='a'` is false because `MUT` contains `a`),
  but for the twelve frozen patterns and `MUT='__kama_mut__'` it cannot go false on a green, non-dead
  run. KQ102 therefore states the leg as a row-level flip, not a substring-survival test.

### 2.2 KQ103 — a frozen counter must survive adversarial receipts

- Frozen C1 counter at the measured tip: `git show master:tools/round62-c1-counter.py` sha256
  `275610b51eb1be219cdaa3c3e15e3568b590f35e7a1b3ceb42ab0374243f4d8d`; working-tree file
  `a3498308938ed4715cfdf1ce5c9a2e4ddf9cb5f9befbba29857980721fe8c415`; `git diff` is exactly 3 lines
  (line 130 `u = (cj or {}).get('usage')`, line 139 `t = (cj or {}).get('timings')`, line 165
  `if 'hold_released' in (receipt.get('checks') or {})`).
- This seat's independent probe (imported the tip blob; called `grade()` only; no subprocess, server or
  network): `empty-receipt {}` and `tamper-body-sha-mismatch` both raise
  `AttributeError: 'NoneType' object has no attribute 'get'` (`probe-output.txt`, this directory).
- The counter's control loop has no guard around `score(ctl, witness)`
  (`tools/round62-c1-counter.py:437-443`), and `grade()` dereferences `cj` at line 130 after
  `cap('completion')` returns `None` — so `tamper[0]` (the counter's own input) aborts the run before
  the summary line. Seat E01CompletionRepeat reproduced this through the CLI 3/3 deterministically and
  shows the two `(cj or {})` guards alone are not enough (`live: {"alltrue": true, … "inconsistent":
  ["unexpected-checks"] …}`); all three deltas are needed to reach `met=True`
  (`out/E01CompletionRepeat/tipblob.stderr.txt`, `derived-2line.stdout.txt`, report §4).
- The defect was already recorded before the freeze: `.ufo/waves/round-62/measured/c1-before-fix.txt`
  names the same line and input and the follow-up guard, and `corpus/lessons/round-62.md` carries it
  as a `vacuous` Mistakes row. What the frozen claim lacks is the guarded bytes at the tip.

### 2.3 KQ104 — a scan-bound claim is its class census, not its residual

- Bound rows: `registry/capability-claims-r62.tsv:9-10` (`digest-ledger`, `hexrun-census`) bind
  `unknown=0` as the decisive output substring.
- The same scans at the tip print (E05 receipts, verbatim):
  - `digest-scan-tiprev.txt`: `tokens=143 blob=125 external_ok=9 external_absent=1 unverifiable=7 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0`
  - `hexrun-scan-tiprev.txt`: `tokens=2051 distinct=392 lane_oid=271 md5_blob=1 upstream_ok=108 unverifiable=9 wrong_flagged=3 ledger_bad=0 unknown=0`
- Class rules already in force: `tools/digest-ledger.py` classifies `blob | ledger (by class) | wrong_unflagged | unknown`
  and counts `external_absent` for a ledger-declared external artifact that is missing, `ledger_bad` for an
  empty `unverifiable` note (`:29-47`, `:135-152`); its exit code is nonzero on
  `ledger_bad + wrong_unflagged + unknown` only, so `external_absent=1` coexists with exit 0.
- The upstream class is evidence-file-bound here: `.ufo/waves/round-62/census/fleet-commit-evidence.json`
  lists the 40-hex fleet commits with a note that they were checked with
  `git -C /home/vgpnk/Projects/shokunin cat-file -t <sha> -> commit` (2026-10-28).
- Ledger growth this round: `registry/hexrun-ledger.tsv` has 9 rows dated 2026-10-28 (111 `upstream`,
  9 `unverifiable`, 3 `wrong` overall); `registry/digest-ledger.tsv` has 3 (11 `external`, 7
  `unverifiable`, 1 `wrong`). Those are the rows that move previously-unknown cited tokens into a class;
  KQ104 requires the class rule, not the row's presence, to decide each one.

## 3. Findings (reported, not adjudicated — conflicts kept verbatim for the canonical judge)

1. **The frozen C1 counter bytes crash on their own `tamper` family; the frozen tip cannot print the
   measured state.** Spec text: “C1 met=True at tip 65d7cad0fce90e34de37527cde22e97b63b118bf
   (tool_present=1 live_ok=1/1 all 16 controls rejected errors=0)”. At those bytes the counter exits
   with `AttributeError: 'NoneType' object has no attribute 'get'` at `round62-c1-counter.py:130`,
   `exit=1`, empty stdout (this seat: `probe-output.txt`; E01: `tipblob.stderr.txt`, 3/3). The
   `met=True` lines in `out/E01CompletionRepeat/run1.stdout.txt` and `par-r1.stdout.txt` come from the
   working-tree bytes `a3498308…`, which carry 3 uncommitted lines against the tip blob `275610b5…`.
2. **The untracked knowledge entry states the same tip-level `met=True`.**
   `corpus/knowledge/completion-request-plane.md:3`: `verified-at: 2026-10-28 — lane tip
   65d7cad0fce90e34de37527cde22e97b63b118bf, counter `tools/round62-c1-counter.py` met=True`. The tip
   blob of that counter cannot reach the print. (Entry is `??` in `git status`, not a committed byte.)
3. **C2 sensitivity wording conflict.** `corpus/lessons/round-62.md` says
   “for any nonempty pattern, `pattern in out.replace(pattern, MUT)` is false by construction, so
   `sensitive` is always true”; seat A05C2Sensitivity shows a counterexample (`P='a'`, `MUT='__kama_mut__'`)
   where the leg is false, so it is not always true — but for the twelve frozen manifest patterns it is
   true on every green, non-dead run. Both texts are quoted in KQ102's motivation; the criterion uses
   the narrower reading (a row-level flip, not substring survival).
4. **A residual zero is not a classification.** The two bound scan rows pass on `unknown=0` while the
   same receipts carry `unverifiable=7 external_absent=1 wrong_flagged=1` and
   `unverifiable=9 wrong_flagged=3`. `external_absent` is counted as classified by the digest tool yet
   is not a confirmed token; nothing in the row's decisive substring distinguishes the two.
5. Frozen-instrument gaps a sibling (R05FreezeFidelity) recorded and KQ103 does not reach: C1's
   “byte-pinned” has no digest check, model/server sha256 are receipt-asserted rather than re-hashed at
   the counter boundary, `pdeathsig` and “unregistered port” are not counter-verified, and per-check
   `passed` may be null without counting as disagreement. These are reported here only as context for
   the judge; KQ103 is scoped to survivability.

## 4. Out of scope / not done

- No verdict on C1 or C2, no score or axis change; the canonical judge holds that.
- No edit to `corpus/QUALITY.md`, `SCORECARD.md`, `LOG.md`, any registry, counter or tool; the text above
  is a draft for L1 integration.
- No live server was started by this seat: the probe imported the counter module and called `grade()`;
  no port was bound and no registered consumer was contacted.
- Not re-measured: whether the working-tree counter (3 deltas) reaches `met=True` end-to-end — E01 reports
  6/6 green, this seat did not rerun it.
- Not checked: the C2 full measurement (running in parallel by other seats), `tools/kama-completion-live.py`
  internals, ledger row contents beyond class/date counts.

## 5. Touched surfaces

- Created: `.ufo/waves/round-62/w1/W03QualityDraft.md`, `.ufo/waves/round-62/w1/out/W03QualityDraft/W03QualityDraft.md`,
  `.ufo/waves/round-62/w1/out/W03QualityDraft/probe-output.txt`.
- Scratch `/fast/scratch/hyaku/kama-r62/w/W03QualityDraft/` created and removed; receipt copied here first.
- Git: read-only only (`rev-parse`, `show`, `diff`, `status`, `log`). No mutating git/jj command, no commit,
  no fleet-repo write, no sibling-lane or lane-index write.

W03 tally: criteria drafted 3 (KQ102–KQ104) · canonical population 12 · base controls read 2 (both exit 1) · frozen counter byte pairs compared 1 (tip vs worktree) · independent crash reproductions 2 of 2 malformed classes · live runs 0 · installs 0 · lane edits 0 · scratch removed 1 · C1/C2 verdicts issued 0

Report: .ufo/waves/round-62/w1/W03QualityDraft.md
