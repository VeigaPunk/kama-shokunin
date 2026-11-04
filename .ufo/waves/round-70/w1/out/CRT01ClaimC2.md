# CRT01ClaimC2 — C2 attack (advisory)

Seat: falsify C2. Read-only on the lane; the files below are candidate bytes for the L1.
Full evidence, commands and exit codes:
`.ufo/waves/round-70/w1/out/CRT01ClaimC2/report.md` and `attack.md` in the same directory.

Pins: frozen counter `37fd20eb…`; base census `46389918…`; C2 landing bytes `44bebd67…`
at tip `af6eb6c2` (the pre-integration landing `a82cad11…` at `73597158` was also scored;
`af6eb6c2` implements this seat's F1/F2 corrections and rewrites `SKILL.md:1690`). Later
tips `2fc9ce1e` (final measured receipt) and `a8df1af5` (wave evidence, this seat's output
directory committed) do not change the census or the controls; the boundary control is
committed at `w1/out/CRT01ClaimC2/c2-boundary-control.py`.

## Findings

1. **The fail-open reproduces** on the base bytes: pair `(0, 0)`, control exit 1.
2. **The counter's three named polarities hold**: always-exit-1 → `(1,1)` rejected;
   refusal-as-pass → `(0,0)` rejected; cosmetic `not_evaluated` with exit 0 → `(0,0)`
   rejected. `counterexamples.py` reproduces all three.
3. **Five designs PASS the frozen counter and violate the frozen target** (pair `(1,0)`,
   control exit 0):
   - refusal reclassified as `fail` (`fail=1 not_evaluated=0`; exit still derived from
     `failed`);
   - literal `total=22` (2-member fixtures print 22; the "deleting the member fails
     total=22" kill rule is mechanically unenforced);
   - waiver swallows a genuine FAILURE (`pass … (waived)`, exit 0);
   - second in-process call prints nothing (the counter reuses one module object);
   - refusal branch deleted (all three pinned refusal markers land as `FAIL`).
   Root cause: the counter reads only the exit; `not_evaluated`, the population, the
   waiver scope and re-entrancy are unasserted. This is the seat's central result and it is
   independent of the landing.
4. **The landed bytes close the sharp waiver boundary**: refusal waivable by exact name; a
   failing member is never waivable; prefix names do not match; re-entrant; population
   derived. Boundary control on `44bebd67…`: `pass=15 fail=0 warn=1 skipped=1`, exit 0
   (`warn` = the unknown-waiver policy below).
5. **F1/F2 (format) are resolved at `af6eb6c2`**: `waived=` is printed only when used, so
   the freeze's literal `HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22` now appears;
   and the explanation line uses the distinct prefix `CENSUS_NOT_EVALUATED`, so exactly one
   `HOST_CENSUS`-prefixed line exists and a `tail -1` miner reads counts. The pre-integration
   bytes printed `… waived=0 total=22 …` and a second `HOST_CENSUS exit 1:` line; measured
   literal count was `0` before the integration. The `superseded/` directory holds the
   critic's equivalent patch — do not apply it.
6. **F6 (provenance residue): the record is one format generation behind in three
   passages.** `measured/after/census-at-af6eb6c2.out` now exists and its contiguous line is
   cited in the final-values paragraph (`SCORECARD.md:3732`). But `SCORECARD.md:3714`,
   `LOG.md:2681` and `corpus/lessons/round-70.md:75` still quote the pre-integration line
   (`… waived=0 total=22 …`) and cite `census-at-tip.out` (the `a82cad11…` output). Fix:
   point those three at the new receipt, or label the quoted line as the `a82cad11…` output.
   Keep both receipts (the lane preserves old receipts).
7. **F3 (open, policy): unknown `--waive <name>` exits 0** with a stderr warning. Safe (it
   cannot green a not-evaluated member) but a typo costs a full re-run and only stderr says
   why. `warn` in the boundary control.
8. **F5 (tradeoff): OSError spawn path** is `not_evaluated` (waivable) instead of the base's
   `fail`; a missing `.py` member still lands as `fail` because the interpreter runs and
   exits 2. Consequence: `tierA_fail` no longer counts a tier-A member whose *binary* is
   absent. Not a frozen-target violation.
9. **Member set untouched**: 22 members (12 A / 10 B), base table == final table
   tuple-for-tuple, three refusal markers still classify as not-evaluated. Real population
   run at the landing tip: `HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22
   tierA_fail=0 tierB_fail=0`, exit 0. C1's kill-rule condition (22 members, reconciler arm
   registered) holds.
10. **Receipt reader:** no tracked tool parses the census verdict; the exit is the only
    machine signal and is hand-copied into receipts. `not_evaluated` distinguishes "did not
    run" from "failed" but is unasserted by the frozen counter, so neither field alone
    closes the hole. `c2-boundary-control.py` is the missing assertion.

## Deliverables (candidate bytes, L1 lands)

| file | target | sha256 |
|---|---|---|
| `CRT01ClaimC2/c2-boundary-control.py` | `.ufo/waves/round-70/controls/c2-boundary-control.py` | `7b364ae1fcc66e6dceb8e8c37a0931e138442ab970094ae3a84dce9e30ccea80` |
| `CRT01ClaimC2/counterexamples.py` | reproduction of the five counterexamples (wave-local receipt) | `d6df475b7a42e66a93376680324896d176484d9e6e1a44df75096b2f57e9ced8` |
| `CRT01ClaimC2/superseded/` | F1/F2 patch + corrected bytes — **superseded by `af6eb6c2`, do not apply** | — |

## Exact post-landing commands

```
python3 .ufo/waves/round-70/controls/refused-member-control.py tools/round65-host-census.py
  -> REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0   (exit 0)

python3 .ufo/waves/round-70/controls/c2-boundary-control.py tools/round65-host-census.py --cli
  -> expect C2_BOUNDARY_CONTROL pass=15 fail=0 warn=2 skipped=0             (exit 0)
     (warn = unknown-waiver exit 0 on the in-process and the CLI probe)

python3 tools/round65-host-census.py > .ufo/waves/round-70/measured/after/census-at-<tip>.out
  -> HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22 tierA_fail=0 tierB_fail=0   (exit 0)
     (F6: new receipt; cite it from SCORECARD.md:3714 and corpus/lessons/round-70.md)
```
