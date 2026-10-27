# R57Item42SiblingOverlap — distinct case 63 (cross-claim / sibling-overlap scan, read-only)

Role: connector, leaf seat, no subagent dispatch. No commits, pushes, jj/git mutations, or writes to tracked files. Scratch: `/fast/scratch/hyaku/kama-r57/R57Item42SiblingOverlap/` (removed after receipts were copied). Receipts: `.ufo/waves/round-57/reports/R57Item42SiblingOverlap-case63.receipts/` (`commands.txt` lists every command and exit). The dispatch names no explicit `Report:` trailer for this seat; I used the convention peer seats already use (`.ufo/waves/round-57/reports/<Seat>-case<N>.md`).

Installs/updates: none. Only in-repo `python3` and `git` were used.

## 0. Tip moved during the scan

Every result below is pinned to an explicit SHA; none is "HEAD".

| Moment | HEAD | Notes |
|---|---|---|
| seat start | `7c873d7b round-57: correct frozen claim targets before data` | freeze amendment committed here |
| mid-scan | `7b74e2f2 round-57: bind prereg roster to executed calls` | operability edit to `tools/round56-prereg-check.py` **and** SCORECARD calibration 42→43 in one commit |
| latest read | `8640e34c round-57: record measured counter outcomes` | adds `## Round 57` section; `Latest measured round: 57` |
| frozen base | `b89bdab2` | base for every "before" receipt |

## 1. Claim labels: dispatch and amendment disagree (planner decision)

- `w1-spec.json` / `w1-dispatch.json` (commit `89dc4f52`) say: **C1 = calibration**, stale canonical capability row count / `maxN=56` vs expected `46`; **C2 = operability**, canonical-row execution/content binding.
- `controls/freeze-amendment.txt` (commit `7c873d7b`, "committed before any seat findings", "supersedes the earlier round-57 freeze's claim ordering only") says: **C1 = operability**, round-56 prereg checker no-op false green; **C2 = calibration**, `tools/round42-selfdesc-reconcile.py` stale count (expects 42, tree holds 43); "C1 and C2 are distinct axes, each measured independently."
- The SCORECARD `## Round 57` section (`8640e34c`) follows the amendment labels.

I did not resolve the conflict. Per the amendment, the dispatch's C1 target is superseded; the analysis below uses the amendment labels and checks the dispatch's targets as well.

## 2. Findings

### F1 — The dispatch's C1 target ("stale canonical row count, maxN 56 → 46") has no repo basis

Measured with the counter's own helpers (`canon()` from `round42-selfdesc-reconcile.py`) on the committed SCORECARD:

| tip | canonical round selected | canonical rows | max `## Round N` heading | counter `maxN` |
|---|---|---|---|---|
| `b89bdab2` | 49 | 11 | 56 | 56 |
| `7b74e2f2` | 49 | 11 | 56 | 56 |
| `8640e34c` | 49 | 11 | 57 | 57 |

- Canonical row count is **11** at every tip, and the Retired section states "11 capabilities"; the counter's `caps` fact is 0 at all tips. There is no stale canonical row count.
- `maxN` is not a checked fact. The round-42 counter only prints it, and it feeds the banner and Planned facts, which compare against the same maxN. Nothing in the counter expects 46.
- The only places the literal `46` appears are the hand-written no-op fixtures (`controls/c1-noop.py` prints `mismatches=0 maxN=46 met=True`; `controls/noop-c1.out` and `noop-c2.out` repeat it) and the historical SCORECARD line 2676 (`## Round 46` measured block: "`maxN=46`"). The dispatch's "expected 46" is therefore a hardcoded output copied from a no-op control, which is the defect class the claim is supposed to reject.

### F2 — The amendment's calibration repair (42→43) is real, but it leaves round 43 red and shares a cell with it

- Round-42 counter (`tip` → summary, exit):
  - `b89bdab2` → `mismatches=1 maxN=56 met=False`, exit 1; detail: calibration run "no stdout line == '42'".
  - `7b74e2f2` → `mismatches=0 maxN=56 met=True`, exit 0.
  - `8640e34c` → `mismatches=0 maxN=57 met=True`, exit 0.
- The same SCORECARD calibration cell is read by `tools/round43-registry-audit.py` "spot" leg, which matches the strict regex `` `(\d+)` \(outside closures on record\) ``. The repaired wording is "`43` (outside closures on record, including round 56; …)", so the strict regex matches **0** lines at `8640e34c` (loose prefix regex: 1).
- Round-43 at `b89bdab2`: `unreg=4 defect=0 flags=0 pins=0 selftest=1 dc=0 spot=1 hidden=0 pop=58 registered=54 mismatches=6 met=False`, exit 1.
- Round-43 at `8640e34c`: same counts, `mismatches=6 met=False`, exit 1; detail includes `spot: calibration row states none, tree holds 43`.

So the repair changed the literal but not the grammar the round-43 gate reads. Round 43 was already red at base (four unregistered `round56-*` tools, `GATE_SELFTEST pass=5 fail=1`, and the spot leg) and is still red. The amendment's "require mismatches=0" is satisfied only for round 42. Whoever repairs calibration must either keep the round-43 wording or own a round-43 change, which is a separate claim.

### F3 — The operability repair (`executed`) is a syntactic call-literal check, and a dead-code no-op passes it

`7b74e2f2` adds to `tools/round56-prereg-check.py`:
```
invoked = {label for every ast.Call named run/assert_mutant_breaks_detection with a string-literal first arg, anywhere in the AST}
executed = expected_roster_names <= invoked
met = match and executed and kills == 1 and controls == 2
```
`executed` is reachability-blind: a call inside a function nothing calls counts as executed.

Fixtures (scratch git repos; toplevel asserted before each commit; battery body and prereg from HEAD):

| fixture | checker | result | exit |
|---|---|---|---|
| `fx-genuine` (unmodified battery, tip `1420a90e`) | HEAD (`7b74e2f2`+) | `roster_match=1 kills=1 controls=2 met=True` | 0 |
| `fx-noop` (ROSTER kept, `main(): return 0`, no run calls; tip `b8378e2c`) | b89 (pre-round-57) | `met=True` | 0 — round-56 false green reproduced |
| `fx-noop` | HEAD | `met=False` | 1 — the amendment's predicate for this shape holds |
| `fx-deadcode` (all three `run(...)` literals moved into an uncalled `_never_called()`; `main(): return 0`; tip `33459ace`) | HEAD | `roster_match=1 kills=1 controls=2 met=True` | **0 — survivor** |
| `fx-deadcode` | b89 | `met=True` | 0 |

AST check on `fx-deadcode`: `run-literal base-old-counter line 70`, `round56-counter line 71`, `m-drop-ldaudit line 80`; `_never_called` is referenced nowhere. The battery runs nothing, and the checker says met.

The sibling SCORECARD text (`## Round 57`, `8640e34c`) already concedes this: "C1 does not assert that every runtime effect of a battery call was executed; it checks the call-site inventory in the committed battery AST." The amendment's predicate is "rejects a no-op that declares the matching roster but executes none". The dead-code fixture is exactly that shape and the gate accepts it. The name `executed` overstates what is checked. This is the same gap the dispatch's C2 ("row-content execution binding") describes, and it lives in the same file and commit.

### F4 — Commit bundling: both claims landed in one commit

`7b74e2f2` contains the operability edit to `tools/round56-prereg-check.py`, the calibration literal in `SCORECARD.md`, `LOG.md`, and `corpus/lessons/round-57.md`. The amendment requires the two axes to be "measured independently". The measurements were in fact taken independently (round 42 and the prereg checker are separate tools), but the one-commit landing means a revert of either claim reverts both. This is a process note, not a counter defect.

### F5 — Peer overlap

`.ufo/waves/round-57/reports/R57Item22SiblingOverlap-case43.md` (peer, case 43) reaches the same F2 and F3 results. I reproduced them independently from fresh fixtures with separate commands and did not rely on that report's receipts. Its statement that the `maxN=46` literal comes from SCORECARD line 2676 matches my grep (`2676:Regressions at 4340cf2f … maxN=46`). Its round-43 finding is consistent with my F2.

R57Item04 (case 25) and R57Item25 (case 46) cover the canonical-row binding and the expected-46 control; they agree with F1 (canonical rows re-derive at 11, and the no-op prints 46 literally). I did not re-run their scratch drivers.

## 3. Commands and exits (summary; full list in receipts `commands.txt`)

```
round42 --tip b89bdab2 -> mismatches=1 maxN=56 met=False            exit 1
round42 --tip 7b74e2f2 -> mismatches=0 maxN=56 met=True             exit 0
round42 --tip 8640e34c -> mismatches=0 maxN=57 met=True             exit 0
round56 --tip b89bdab2 -> roster_match=1 kills=1 controls=2 met=True exit 0
round56 --tip 7b74e2f2 -> same                                      exit 0
round56 --tip 8640e34c -> same                                      exit 0
round56 fx-genuine     -> met=True                                  exit 0
round56 fx-noop (HEAD) -> met=False                                 exit 1
round56 fx-noop (b89)  -> met=True                                  exit 0   (false green)
round56 fx-deadcode    -> met=True                                  exit 0   (survivor)
round43 --tip b89bdab2 -> mismatches=6 met=False (spot=1)           exit 1
round43 --tip 8640e34c -> mismatches=6 met=False (spot=1)           exit 1
```

Receipts: `.ufo/waves/round-57/reports/R57Item42SiblingOverlap-case63.receipts/*.out`, fixtures `…receipts/fixtures/` (battery-HEAD.py, battery-noop.py, battery-deadcode.py, prereg.json).

## 4. Overlap map

| Shared surface | C-calibration (amendment C2) | C-operability (amendment C1) | Other readers |
|---|---|---|---|
| SCORECARD calibration cell (line 18) | literal 42→43, counted by round-42 `r41` fact | — | round-43 spot leg (strict regex; red at base and tip) |
| `tools/round56-prereg-check.py` | — | `executed` added | none in tools/; round-43 lists it as unregistered |
| `.ufo/waves/round-56/preregistration.json`, `tools/round56-env-leg-battery.py` | — | roster source | round-56 artifacts |
| canonical list (round 49, 11 rows) | — | — | round-42 `caps`/`province`, round-41/43 reads; not changed by either claim |
| `maxN` | not a counted fact | not a counted fact | hardcoded `46` in no-op fixtures and SCORECARD line 2676 |

Shared file: none between the two tools. Shared cell: SCORECARD calibration line (read by round 42 and round 43). Shared commit: `7b74e2f2`.

## 5. Recommendations for the planner (not applied)

1. Resolve the label conflict (§1) before any repair seat edits; the dispatch's C1 target (`maxN` 46 / canonical row count) should be dropped as unsupported, since the repo's canonical row count is 11 and `maxN` is unchecked.
2. Calibration: either keep round-43-compatible wording for the spot cell or name round-43's grammar as a separate, in-scope repair; do not claim round 43 green.
3. Operability: `executed` must mean reachable from `main`, or the name and the amendment predicate should be narrowed to "call-site inventory present". The dead-code fixture is the discriminating control for either choice.

## 6. Verification the main agent should run (not run by this seat as a repair step)

1. `python3 tools/round42-selfdesc-reconcile.py --repo . --tip <tip>` → expect `mismatches=0 met=True`.
2. `python3 tools/round56-prereg-check.py --repo . --tip <tip>` → expect `met=True`; and against a no-op fixture (ROSTER kept, no calls) → `met=False`; against the dead-code fixture → currently `met=True` (survivor, F3).
3. `python3 tools/round43-registry-audit.py --repo . --tip <tip>` → currently `spot=1` and `mismatches=6` (F2); expect a repair owner.

## 7. Limits

- Read-only on the repo. Fixtures are scratch git repos, each with a toplevel assertion before commit. No repo object was created.
- The fixtures reproduce the checker's AST predicate; they do not show that the battery's runtime behaviour is correct (out of scope).
- I did not verify the S515 source or the round-56 outside-defect lesson (other seats own them).
- The tip moved three times during the scan; the table in §0 lists the SHAs used.
