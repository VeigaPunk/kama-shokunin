# attack.md — CRT01ClaimC2 (round 70, lane kama, claim C2)

Role: advisory critic. No verdict, no lane edits, no subagents. Everything below is
reproducible from the frozen bytes and the delivered files.

## 0. Scored objects (read-only)

| object | sha256 |
|---|---|
| `controls/freeze.txt` | `ec616473a8673e1e4d959c03b4610af553ae6ef93acf596b981da5256fa9c17f` |
| `controls/refused-member-control.py` | `37fd20eb30ec08a488eea3644f1b2f4b7bb0062b0c12d90bd5a643d2424623b3` |
| base census (`measured/before/round65-host-census-base.py`) | `463899182af0d154859e86da785051760e4bc314f5489659ea32424c18374513` |
| pre-integration landing (`tools/round65-host-census.py` at `73597158`, commit `7be07423`) | `a82cad11d777aa4b34d8ae96b66250d52853ed880d4c2eaa510ea8b4bf37dc68` |
| final landing (`tools/round65-host-census.py` at `af6eb6c2`) | `44bebd671c0d12118c92ace1ef6bd7491a60c7acbce79f1668b81a822b245919` |

The final landing implements this seat's F1/F2 findings (`waived=` only when used;
`CENSUS_NOT_EVALUATED` prefix) and rewrites the `SKILL.md:1690` exit map. The central
finding below is independent of the landing: it is about the **frozen counter**, which
did not change.

---

## 1. The fail-open reproduces, and the base changes nothing but the verdict key

```
$ python3 .ufo/waves/round-70/controls/refused-member-control.py \
      .ufo/waves/round-70/measured/before/round65-host-census-base.py
{"refused_fixture": ["pass [A] synthetic-pass", "refused [A] synthetic-refused: ... (marker 'invalid path')",
                     "HOST_CENSUS pass=1 fail=0 refused=1 total=2 tierA_fail=0 tierB_fail=0"],
 "allpass_fixture": ["pass [A] synthetic-pass", "pass [A] synthetic-pass-2",
                     "HOST_CENSUS pass=2 fail=0 refused=0 total=2 tierA_fail=0 tierB_fail=0"]}
REFUSED_MEMBER_CONTROL refused_fixture_exit=0 allpass_fixture_exit=0
exit 1
```

A member that emitted a pinned refusal reads as a pass; the counter's pair is `(0, 0)`.

## 2. The counter's polarity holds on the three named shims

Built from the frozen base bytes by `counterexamples.py` (one asserted replacement each);
`python3 counterexamples.py` reproduces the whole table:

| shim | mechanism | pair | control exit |
|---|---|---|---|
| s1 always-exit-1 | `return 1` unconditionally | (1, 1) | 1 — rejected |
| s2 refusal-as-pass | base bytes | (0, 0) | 1 — rejected |
| s3 cosmetic `not_evaluated` | prints `not_evaluated=1`, exit still `failed==0` | (0, 0) | 1 — rejected |

So the counter is sound on the three polarities the seat names; a cosmetic key alone does
not fool it.

## 3. Five designs PASS the frozen counter and violate C2's frozen target

Same generator, same command. Mechanism → the fact the freeze names that the design breaks.

| shim | mechanism | pair | control exit | what it breaks |
|---|---|---|---|---|
| s4 refusal-as-fail | refusal branch increments `failed` | (1, 0) | **0 PASS** | verdict prints `fail=1 refused=0`; the freeze's refused fixture must carry `not_evaluated=1`, and a refusal is not a defect. The exit is still derived from `failed` — the base's defect relabelled. |
| s5t literal total | `total=22` is a literal, not `len(MEMBERS)` | (1, 0) | **0 PASS** | a 2-member fixture prints `total=22`. The freeze's kill rule "deleting the member fails the registered total=22" becomes mechanically unenforceable: the counter never reads the population. |
| s6w waiver swallows a failure | a waiver marks a *failing* member `pass (waived)` | (1, 0) | **0 PASS** | the seat's sharp boundary: exit 0 with `HOST_CENSUS pass=2 fail=0 not_evaluated=0` and `pass [A] synthetic-broken (waived)`. |
| s8r second call silent | `_RAN` guard: the second in-process `main()` prints nothing, returns 0 | (1, 0) | **0 PASS** | the counter reuses ONE module object for both fixtures; the all-pass fixture produces no verdict line at all, and the counter still prints (1, 0). |
| s10d refusal branch deleted | `hit = None`; refusal markers are unknown | (1, 0) | **0 PASS** | all three pinned refusal markers classify as `FAIL`. Direct attack on "the three refusal markers still mean refusal". |

Root cause, one sentence: **the counter reads only the exit code, and no fixture carries a
failing member or a waiver, so `not_evaluated`, the population, the waiver scope and the
second call are all unasserted.**

`s7 argparse-in-main` is the sixth shape, rejected only by crashing: the control exits 2
with **no** `REFUSED_MEMBER_CONTROL` line because `main()` inherited the control's own
argv. The landed bytes avoid it with a tolerant parser that skips unknown tokens.

## 4. The waiver boundary in the landed bytes

Driven through every channel (`main(waive=…)`, `CENSUS_WAIVE`, `sys.argv --waive`):

- refused member + `--waive <its exact name>` → exit 0, `not_evaluated=1 waived=1`, the
  member's own line keeps its reason and gains `[waived]`. **The pressure valve works.**
- failing member + `--waive <its exact name>` → exit 1, `fail=1`, member line `FAIL`,
  stderr names the waiver as unused. **A failure is not waivable.** Closed.
- `--waive synthetic` (a prefix of `synthetic-refused`) → exit 1. Exact-name matching.
- `--waive no-such-member` → exit **0** with a stderr warning naming the name. Not
  dangerous (it cannot green a not-evaluated member), but a typo leaves an operator red
  after a full 32 s re-run and only stderr says why. **F3, warn.**
- OSError spawn path: base → `FAIL`, `tierA_fail=1`; landed → `not_evaluated=1`,
  `tierA_fail=0`, and an explicit waiver clears the exit to 0
  (`evidence/spawn-oserror-probe.out`). A missing `.py` member still lands as `FAIL`
  because the interpreter runs and exits 2. **F5, tradeoff**, not a frozen-target
  violation.

The **counter cannot see any of this**: s6w shows the identical pair for a landing that
leaks. The waiver scope is guaranteed by review, not by the counter.

## 5. The member set is untouched

- base table == final table, tuple-for-tuple: `22` rows; `12` tier A, `10` tier B; three
  refusal-carrying members with markers `missing dependency`, `invalid path`,
  `cannot resolve master`. Canonical dump `evidence/table-base.json`
  sha256 `f89ce38decee49fbcb1a4c29a7053e7e4545584122535cfbcde9e0bae986c307`.
- three pinned refusal markers still mean not-evaluated: injected one-member fixtures for
  each marker produce `not_evaluated=1 fail=0` and no `pass`/`FAIL` line (`marker:*` ok).
- real population run at `af6eb6c2` (31.9 s):
  `HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22 tierA_fail=0 tierB_fail=0`, exit 0.
  Mid-flight (at `a82cad11` during C1's repair) the same run read `pass=21 fail=1`, the one
  red being the reconciler arm (C1's file). C1's kill-rule condition (22 members,
  reconciler arm registered) holds.

## 6. Is `not_evaluated` in the verdict enough? No — and the exit alone is not either

1. **No tracked tool parses `HOST_CENSUS` or `not_evaluated`.** The only hits are the
   census itself, wave receipts, and prose. The exit code is the only machine-readable
   signal, and it is hand-copied into receipts (`EXIT=n` appended by the seat's shell; no
   `EXIT=` producer exists in `tools/`).
2. **The lane's own receipt miner reads the last `HOST_CENSUS` match**
   (`SCR01Lesson.md:41`: `grep -o 'HOST_CENSUS[^|]*' "$f" | tail -1`). On the
   pre-integration bytes a red/waived run printed a second `HOST_CENSUS`-prefixed line, and
   the match became a mangled concatenation of the verdict, the explanation and the
   all-pass verdict (`evidence/literal-and-mining.out`). At `af6eb6c2` the explanation line
   is `CENSUS_NOT_EVALUATED …`, so exactly one `HOST_CENSUS` prefix remains. **F2 resolved.**
3. **The freeze's literal green line was absent before the integration.**
   `measured/after/census-at-tip.out` (21:00, produced by `a82cad11…`) reads
   `… not_evaluated=0 waived=0 total=22 …`; `grep -c` for the freeze's literal
   (`pass=22 fail=0 not_evaluated=0 total=22`) was `0`. The `af6eb6c2` green run prints the
   literal (`evidence/final-af6eb6c2-census-and-cli.out`, grep count `1`). **F1 resolved.**
4. **The records are one format generation behind.** `SCORECARD.md:3714` and
   `corpus/lessons/round-70.md` quote the 21:00 receipt's interposed line, and that receipt
   is still cited. The tool now prints a different green line, so a reader who re-runs the
   cited command at the tip gets a line the record does not quote. **F6, open.** Fix: run
   the census at the tip into a *new* receipt (the lane preserves old receipts rather than
   overwriting them) and point the record and the lesson at it.

Conclusion: `not_evaluated` is *necessary* (the only field distinguishing "did not run"
from "failed") but *insufficient as evidence* because nothing asserts it; the exit is what
callers branch on but cannot distinguish a waived non-run from a run. The assertion must be
codified — `c2-boundary-control.py`, without touching the frozen bytes.

## 7. Impacted axes

- **operability (C2, held 8):** target met on the frozen counter and on the boundary probes
  at `af6eb6c2`; remaining: F3 policy, F5 tradeoff, F6 receipt provenance.
- **calibration (C1, held 7):** the `SKILL.md:1690` exit-map drift (F4) found against
  `a82cad11` is repaired at `af6eb6c2`; the row now names `not_evaluated`, the contiguous
  green line and the `CENSUS_NOT_EVALUATED` explanation. F6 keeps a calibration residue:
  the record and the lesson quote a receipt from superseded bytes. Neither is
  machine-caught (the gate grades row shape/paths; the reconciler does not read these
  surfaces).
- **no C1 harm:** member table byte-identical, reconciler untouched; the census's earlier
  red was C1's arm.

## 8. Smallest safe corrections

1. **Land `c2-boundary-control.py`** beside the frozen counter and run it at the landing
   tip with `--cli`. It asserts the frozen pair *and* the five facts the pair cannot see
   (verdict tokens, population, waiver scope, exact-name matching, re-entrancy). Expect
   `pass=15 fail=0 warn=2 skipped=0`, exit 0 (both warns are F3).
2. **F6:** produce `measured/after/census-at-<tip>.out` from the landed bytes (new file;
   do not overwrite the 21:00 receipt), then update the pointer in `SCORECARD.md:3714` and
   the quoted line in `corpus/lessons/round-70.md`. My run is
   `evidence/final-af6eb6c2-census-and-cli.out`; the L1 should produce its own at its final tip.
3. **F3 (optional):** unknown `--waive` name → exit 2 before running members. Needs the
   exit map to document 2.
4. **F5 (optional):** keep `OSError` as `fail` (base behavior), or document that
   `tierA_fail` is not the not-run count.
5. Do **not** apply `superseded/correction.patch`: `af6eb6c2` already implements its two
   changes with different wording.

## 9. Defect vs tradeoff

- Fixable defects: the five counter holes (add the boundary control); F6 stale receipt
  pointers (new receipt + pointer update); F3 (policy choice).
- Tradeoffs the L1 owns: unknown-waiver exit 0 vs 2; OSError as `not_evaluated`;
  `not_evaluated` counting waived members (the landed bytes keep the raw count and print
  the waived subset — the recommended reading).
- Not defects: the frozen counter's three polarities; the waiver scope in the landed bytes
  (closed); the member set (untouched); the exit rule (`failed == 0 and not unwaived_ne`).

## 10. Not verified

- The round validator's matching mode for the target line (literal vs tokens). Before the
  integration the literal was absent; at `af6eb6c2` it is present, so either mode passes.
- Windows-host behavior (no Windows path exercised; the adaptation is byte-identical to
  base).
- The `--cli` process probe on the final bytes must be run by the L1 at its final tip; I
  ran it at `af6eb6c2` and record the result in `report.md`.
