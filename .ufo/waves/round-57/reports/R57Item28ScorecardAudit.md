# R57Item28ScorecardAudit — SCORECARD/SHONEN calibration assertions vs tree

Seat `round57/ScorecardAudit/28` (leaf, read-only). Judged axes: calibration, operability.
Committed bytes only: `git show` / `cat-file` / `archive` at each named tip. No lane file,
control, or source tree was written; no commit, install, or verification suite was run.

Tips used:

- base `b89bdab2cc114735ec5d331c6c610134258f7864` (round-56 verifier spot-check)
- `7c873d7b4e3839489a93d6334cdf93fe5d34d19f` (round-57 pre-data claim correction)
- `8640e34cad02adcd247ba0862da63f6fb2aab0df` (round-57 measured counter outcomes)
- `8a7f19760242bbe523fa2d7d1b22528b587633c1` (lane tip when this audit was written)

## Verdict

One concrete stale count exists on the calibration surface and it is exactly the round-57 C2
target: the `## Axes` calibration row claimed **42** `corpus/lessons/*verifier-spotcheck.md`
closures while the measured tree carried **43**. At the frozen base and at `7c873d7b` that one
fact is the counter's only mismatch; at `8640e34c` and `8a7f1976` the row says 43 and the
counter is green. Every other numeric assertion in the calibration row re-derives exactly.

The prompt's "counter currently reports maxN=56 instead of expected 46" is **not** a stale-count
defect and the expectation is not re-derivable. `maxN` is the greatest `## Round N` heading in
SCORECARD; it equals the current round in every measured section that recorded it (46, 47, 49,
50, 51, 52), was 56 at the base, and is 57 now. The literal `46` survives only in the round-46
regression prose and in the frozen no-op stub.

## 1. The stale count (C2 calibration)

```text
$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip b89bdab2
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
exit=1
```

```text
$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip 8640e34c     # and at 8a7f1976
r41=0 banner=0 ... mismatches=0 maxN=57 met=True
exit=0
```

Independent derivation (`case49/calib-count-audit.py`, claim vs git tree vs the row's own
counting command executed in a `git archive` export of the same tip):

```text
tip=b89bdab2...  axis=calibration claim=42 tree_count=43 exec_count=43 stale=True  reason=claim!=tree exit=1
tip=7c873d7b...  axis=calibration claim=42 tree_count=43 exec_count=43 stale=True  reason=claim!=tree exit=1
tip=8640e34c...  axis=calibration claim=43 tree_count=43 exec_count=43 stale=False reason=claim==tree==exec exit=0
tip=8a7f1976...  axis=calibration claim=43 tree_count=43 exec_count=43 stale=False reason=claim==tree==exec exit=0
```

So the stale token is SCORECARD's claim, not the tool: `round41-scorecard-reconcile.py` parses
the claim from the tip's SCORECARD and executes the row's command inside the tip archive
(`run_fact`, lines 131–140; archive export at lines 183–193). It cannot disagree with a tree
count except through a stale or wrong claim. The repair is one token (42 → 43), and it is only
visible to the instrument once committed, because the counter never reads the working tree.

## 2. `maxN` is derived and current, not a stale expected value

`round42-selfdesc-reconcile.py` computes `maxn = max(int(m.group(1)) for "## Round (\d+)" lines)`
and asserts the head says `Latest measured round: <maxN>` (plus the next `### Planned (round
maxN+1)` heading). SCORECARD itself records the value as time-indexed:

```text
line=2676 section="## Round 46 ..." maxN=46
line=2723 section="## Round 47 ..." maxN=47
line=2878 section="## Round 49 ..." maxN=49
line=2902 section="## Round 50 ..." maxN=50
line=2931 section="## Round 51 ..." maxN=51
line=3027 section="## Round 52 ..." maxN=52
```

At the base the newest measured round is 56, so `maxN=56` is correct; at the tip it is 57.
Candidate derivations tested at the tip, none of which yields 46: `## Round` heading lines 58,
distinct rounds 50, max 57; canonical-list tables 9, highest round 49, rows 11; spotcheck blobs
43; `corpus/lessons/*.md` 99; SOURCES rows 256. The only `maxN=46` text in the tip's SCORECARD is
line 2676, inside the round-46 regression record. The frozen no-op stub printed the same literal
(`mismatches=0 maxN=46 met=True`, exit 0) without reading any input. Treating that literal as the
expected value would make a do-nothing printer indistinguishable from the instrument.

## 3. Remaining calibration counts: all fresh at `8a7f1976`

| Assertion in the calibration row | Asserted | Re-derived | Verdict |
|---|---|---|---|
| verifier-spotcheck closures | 43 | 43 (git tree, and executed glob in the tip export) | fresh |
| `registry/verdict-ledger.tsv` rows | 204 | 204 data rows (205 lines incl. header) | fresh |
| trend ledger rounds | 10–43 | 10–43 | fresh |
| trend classes | `agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15` | identical | fresh |
| `registry/claim-outcome-ledger.tsv` rows / claims | 126 / 63 | 126 / 63 | fresh |
| claim-ledger rounds | 10–44 | 10–44 | fresh |
| claim classes | `agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1` | identical | fresh |
| `capability-repertoire-audit.py --selftest` | `CAP_SELFTEST pass=2 fail=0` | identical, exit 0 | fresh |
| `instrument-agreement.py --selftest` | `IA_SELFTEST pass=4 fail=0` | identical, exit 0 | fresh |
| axes / capabilities | "6 axes and 11 capabilities" | axis vector 6; highest canonical list round 49, 11 rows | fresh |
| latest outside closure | round 56, admitted | `corpus/lessons/round-56-verifier-spotcheck.md` exists at tip | fresh |

Ledger classes re-derived with the SCORECARD's own strength orders (`harmed < unchanged <
unprovable < unprovable-but-better < improved`; `not-met < unprovable < partial < met`, `mixed`
→ other). The denominators are the rows the prose names: 87 trend keys with both sides present,
61 claim keys excluding the `other` and `absent` keys — both reproduce.

## 4. Stale currency marker, not a count

`## Saturation` says "kept current in round 49" while `maxN=57`, and the highest canonical
capability list is `as of round 49` although rounds 50–57 have sections. The frozen counter has no
predicate for the currency sentence (it checks vector, first-working rounds and the nudge only), so
this survives green. Reported, not resolved: advancing the canonical list is an author decision,
not an audit edit.

## 5. Operability link and the frozen control

The calibration instrument is commit-bound and execution-free only in part: it reads SCORECARD
from the tip but runs the row's command against an archive of the tip, so a claim can only be
falsified by bytes at that revision. Two consequences observed this round:

- A working-tree snapshot committed only in scratch (`98078550`; SCORECARD working-tree git blob
  `8f2a9dd5`) mid-edit reported `banner=1 planned=2 mismatches=3 maxN=57 met=False`, exit 1:
  a `## Round 57` heading existed before the head/planned sentences were updated. Green requires
  the head, the new round heading and the next plan to land in one commit. At `8a7f1976` they do.
- The frozen literal control cannot see any of this. My captured run of
  `.ufo/waves/round-57/controls/c1-noop.py` (present at 15:05–15:14, later removed by the
  integrator's reorganisation of `controls/`; the captured receipt is authoritative) printed
  `mismatches=0 maxN=46 met=True`, exit 0,
  while the content-bound instrument read `claim=42 tree=43 exec=43 stale=True`, exit 1 at the
  same base. Advice to the C2 gate owner (not implemented here): require
  `claim == tree_count == exec_count`, and treat a counting command that emits no integer as
  `cannot-evaluate`, not as a pass.

## 6. Claim ordering

The wave context names C1 calibration (maxN) and C2 operability; `controls/freeze-amendment.txt`
(pre-data) and `SCORECARD` §Round 57 name C1 operability (no-op roster) and C2 calibration
(spotcheck count). The findings above are invariant to the naming: the only stale count is the
spotcheck 42 → 43, and the maxN "expected 46" target has no derivation under either label.

## 7. SHONEN

`SHONEN.md` carries no numeric calibration assertion (the word "calibration" does not occur).
Its 9 backticked lane paths all resolve at the tip; the only ratio tokens are historical
execution receipts `10/10` and `11/11`. No stale count there.

## 8. Limits

- The head-table hash/line facts were re-derived at the working tree and at the fixture base
  (`axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 mismatches=0 met=True`); they were not
  re-run at every intermediate tip.
- A correct count proves the row matches the tree at that tip; it does not prove the row measures
  anything the outside closure would agree with (that is the calibration score, unchanged at 7).
- The lane advanced from `7c873d7b` to `8a7f1976` while this audit ran; the tip beside each
  receipt is authoritative.

## Receipts

`.ufo/waves/round-57/measured/R57Item28ScorecardAudit/`: `lane-tips.out`, `final-tip.out`,
`r42-tips.out`, `r42-at-tip.out`, `fixtures.out`, `controls-vs-instrument.out`,
`inventory-at-tip.out`, `ledger-derive.out`, `maxn-provenance.out`, `shonen-paths.out`,
`calib-selftests.out`, `measure-counts.out`, `snapshot-sha.txt`, plus the instruments
`calib-count-audit.py`, `ledger-derive.py`, `inventory.py`, `mutate.py`, `run-fixtures.sh`.
Distinct case 49: `.ufo/waves/round-57/reports/R57Item28ScorecardAudit-case49.md`.

Report: .ufo/waves/round-57/reports/R57Item28ScorecardAudit.md
