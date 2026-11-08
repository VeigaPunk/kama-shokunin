# CR02Wording — round-98 claim wording vs instrument (attack that caused 26/26 rejections)

Seat CR02Wording. Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`, freeze `34ad44e9`,
base `681c80a4`. Read: `plans/round-98-claims.md`, `.ufo/waves/round-98/claims.json`,
`tools/round98-self-assessment-audit.py`, `tools/round98-router-budget.py`,
`tools/round98-depth-boundary-audit.py`, `corpus/lessons/round-98.md`,
`SCORECARD.md`, `SKILL.md` (all at `HEAD` = freeze commit).

Commands: `python3 tools/round98-self-assessment-audit.py --repo . --rev HEAD`
→ `SELF_ASSESS98 checks=20 mismatches=3 met=False rev=34ad44e9…` exit 1 (expected: surfaces
not yet rolled forward). `python3 tools/round98-depth-boundary-audit.py --repo . --rev HEAD`
→ `DEPTH_BOUNDARY98 rows=6 checks=12 mismatches=4 met=False` exit 1 (expected: 6 rows, no S622).

## Clause table

| claim | sentence clause | enforced? | required narrowing or amendment |
|---|---|---|---|
| C1 `/home/vgpnk/Projects/shokunin/kama-shokunin/plans/round-98-claims.md:43-49` "the lane's graded self-assessments match the repo, heading included" | self-assessments (plural, unrestricted) match the repo | **No** — C1 enforces 20 named surfaces only: 1-3 depth sha/lines/##-count; 4-5 adjacency sha/pipe-count; 6 capability pointer; 7-8 probe comment `5 + nd` + per-rank ceilings; 9 round-96 table rows; 10-11 S621/S620 existence+status; 12 round-96 counter identity; 13-14 round-96 receipt needles+quote; 15 docstring constants; 16 count agreement (`depth_forgeries`, `skill_variants`, `doc_cells`, `cells=19`, W14-W19 ∈ depth+sec97, S620/S621 ∈ sec97); 17 SOURCES ids unique; 18 charge-site equality; 19 heading count word (`the (\w+) graded forgeries` on the exact `### Round 97 correction` line, vs `len(mutants)` from `MUTANTS` parse); 20 overcharge named in depth+sec97+rdoc+`MUTANTS`. `tools/round98-self-assessment-audit.py:301-362` | **Narrow the sentence**: "the lane's 20 named self-assessment surfaces match the repo, heading included". The current headline claims the unrestricted plural; the instrument grades a finite named set. The plan's own disclosed limit (`plans/round-98-claims.md:72-73` "The audit grades exactly the 20 named surfaces") is honest but does not travel with the headline, `claims.json` (`name` field, same unrestricted wording) or the lesson (§5-8 repeats the unrestricted sentence). |
| C1 | "the heading is [now] graded" — heading counts match the repo | **Partially** | Check 19 enforces the count *word equals the parsed mutant count* (5). It does **not** enforce that the heading lists the right five identities, that the heading's other 8 words are true, or that any *second* heading/duplicate doesn't say something else — `next()` takes the first matching line. Check 16/20 enforce *presence* (`"overcharge" in depth.lower()`, `w in sec97 for W14-W19`) — a surface listing the five names in a "not graded" context still passes. And the depth row's *round97* prose ("six KV-free rows … four graded probe forgeries W14…W17" in `SCORECARD.md:17`) is false at `HEAD` but only caught because check 16's regexp happens to hit `(\w+) graded probe forgeries`; at the *measured* commit that prose must be rewritten, but nothing enforces the *old* round-97 history sentence being retired vs appended. No counter-example passes at `HEAD` (mismatches=3, exit 1) — this is a forward-looking looseness: the sentence is wider than all three checks combined. |
| C1 | "match the repo" (second-order claims: receipt quotes, docstring constants) | **Partially** | Checks 13-14 enforce the round-96 summary *needle string* is in receipt **and** in `score.replace("`","")` (`tools/round98-self-assessment-audit.py:262-276`). Presence of the string is not "the header matches": per the carried RV01 §2.10 limit (plan `plans/round-98-claims.md:171-173`) further numbers/summaries in those receipts are ungraded. Check 15 enforces `MAX_STEPS`/`5000000`/`MAX_META`/`512` substrings in the *docstrings* (`tools/round98-self-assessment-audit.py:282-289`) — a docstring can state the probe's constants while the probe itself differs; only check 18 (charge sites) and 7-8 (comment) touch the probe, and those are string/site-shape checks, not behavior. C2 is the behavioral gate; C1's sentence "match the repo" overstates checks 15/18 to a reader who doesn't read the disclosed limit. |
| C2 `/home/vgpnk/Projects/shokunin/kama-shokunin/plans/round-98-claims.md:75-82` "the budget counter grades the overcharge probe the 17-cell set misses" | counter grades (discriminates) the +1/header overcharge probe | **Yes, in predicate+controls** | W18/W19 geometry verified: real 4,800,004 ≤ MAX_STEPS → `invalid`; +1 probe 4+7×800,000=5,600,004 → `-`; W19 real 4,680,004 → `invalid`; +1 probe 5,200,004 → `-`. Window 714,286 < T ≤ 833,332 (nd=1), 500,000 < T ≤ 555,555 (nd=4). `controls/c2-new-mutants.out:36-49` shows `overcharge` caught on both W18 and W19 (`cell_ok=0 caught=1`, `ok=1`); `controls/c2-legacy-mutants.out:18` shows `survived=1` on the 17-cell set. **But** the discrimination lives in the *control receipts*, not the frozen predicate command — the predicate (`--mutant none`) grades only the real probe. A reader of the headline + predicate alone misses that the "grades" property is carried by the control runs. Smallest amendment: append "as shown by the control receipts (`survived=1` on the 17 cells, `caught=1`/`cell_ok=0` on W18/W19)". |
| C2 | "grades the overcharge probe" (class) | **No — grades the named +1 mutant only** | `MUTANTS` (`tools/round98-router-budget.py:192-193`) is one byte patch: `steps[0] += 1` at loop top. A probe overcharging +1 on a *subset* (e.g. only nd=1 headers, only when name length > 8) can evade W18 while passing all 19 — W19 (nd=4) would not see an nd=1-only overcharge, and W18's fixture uses short names. The plan's parenthetical (`plans/round-98-claims.md:98-100`) defines the class as "the `+1` window 714,286 < T ≤ 833,332 at nd=1 and 500,000 < T ≤ 555,555 at nd=4" — that is the *T*-window, not a *probe-behavior*-window. C3's "the class is ≥+1" (`plans/round-98-claims.md:150-152`) is true only for uniform per-header overcharge ≥+1 (verified: +2 probes need ≥5,720,004); conditional overcharge is ungraded and undisclosed. Required narrowing: "grades the uniform +1/header overcharge mutant and any uniform ≥+1/header overcharge". |
| C2 (f) `/home/vgpnk/Projects/shokunin/kama-shokunin/plans/round-98-claims.md:121-122` "W18/W19 expect `invalid`: they pin the overcharge class from the decidable side; they do not pin the budget's lower bound (**W11 does**, in the same run)" | W11 pins the lower bound | **FALSE — W11 pins neither side** | W11 (700k, nd=1): real 4,200,004 → `invalid`. Undercharge probe → also `invalid` (green). Overcharge probe needs 4+7×700,000=4,900,004 ≤ MAX_STEPS → also `invalid` (green). Flat-6 probe needs 4,200,004 → `invalid` (green). W11 catches none of the named mutants. The lower bound is pinned by **W14** (900k nd=1: real `-`, undercharge → `invalid` → red; `controls/c2-new-mutants.out:15-21` shows `undercharge` red on W14/W15/W17). W11's actual role is historical: it discriminates M1's probe from the pre-round-96 base probe (`tools/round98-router-budget.py:106-107` "the base probes grades this `-`"), not any of the five round-98 mutants. Smallest correction: replace "(W11 does, in the same run)" with "(W14 does, from the `-` side, in the same run)". This is inside a disclosed limit — a limit that misattributes coverage is a false clause, not an honest limit. |
| C2 (g) `plans/round-98-claims.md:123-124` "`--probe-file` grades an override probe bound only by `probe_sha256`; `--allow-clock` and `--runs < 1` are refused or excluded" | refused or excluded from the predicate | **Partially false** | `--probe-file` is not refused — it is a supported predicate-shaped invocation, bound only by the printed `probe_sha256` (no binding to the frozen probe's bytes in `--control` mode, which is also reachable with `--probe-file`). `--allow-clock` *downgrades* the DEADLINE refusal to grading the clock probe as a red control (`tools/round98-router-budget.py:644-645`), and `--runs 0` *is* refused (`:616-618`) but `--runs 1` is accepted and is what control runs use (weaker than predicate `runs=2`). "Excluded from the predicate" is true only as a claim about the frozen command sentence, not an enforcement. The threat is small but the clause "refused or excluded" promises more than the parser enforces. |
| C2 (a)-(d) | forgery classes, ctime memo, slow `/props`, wall-clock wrapper | **Honest** | (a) KV/string-step overcharge ungraded — true and disclosed. (b) ctime memo unobservable — true: probe parses once per invocation (`tools/kama-probe.sh` ROUTER_PY). (c) slow `/props` decided as undecided — routed, disclosed. (d) pass-level wall clock — routed, disclosed. These survive attack. |
| C3 `/home/vgpnk/Projects/shokunin/kama-shokunin/plans/round-98-claims.md:126-132` "the step-budget boundary table grades the overcharge window rows" | table grades the overcharge window | **No — the row arithmetic is not the window** | The audit recomputes `steps = 4 + T×(5+nd)` / verdict against `MAX_STEPS` read from the probe at the graded rev (`tools/round98-depth-boundary-audit.py:69-73,103-108`), and requires exactly the 8 `REQUIRED` pairs incl. (800,000, nd=1) and (520,000, nd=4) (`:37-38,111-131`). What it **never** checks: (i) that the rows *are* the overcharge window — the "+1 probe needs 5,600,004 → `-`" column is not in the table and not in the audit; a table with correct real-parse arithmetic but no mention of the +1 parse passes and does not "grade the overcharge window", it grades the real-parse boundary. (ii) The SKILL body at HEAD still says "The six rows below" (`SKILL.md:2449`, `git show HEAD:SKILL.md`), "four probe variants survive all 13 of its cells" (`SKILL.md:2466`), and the heading says "the three graded forgeries" (`SKILL.md:2443`) — at the measured commit these must be rolled forward by C1, but C3's audit never grades the body's row-count prose or the heading at all (it grades `rows == 8` from the `ROW` regex, not the sentence "six rows"/"eight rows"). Required narrowing: "the step-budget boundary table grades the real-parse arithmetic for the two T values that sit inside the overcharge window". |
| C3 After `plans/round-98-claims.md:140-143` "it cites S620 (spec), S621 (the corrected code row) and S622 (the spec's header struct … grounding the four preamble steps as the header struct's four fields)" | S622 grounds preamble=4 | **String-presence only** | The audit checks `"S622" in sect` (`tools/round98-depth-boundary-audit.py:119`) — nothing more. S622's *existence*, status `mined`, kind/tier, URL/quote are graded by **no** counter: C1 checks 10-11 cover S621/S620 only (`tools/round98-self-assessment-audit.py:236-252`; grep for S622 in C1 = 0 hits); the `## Gate` table in `corpus/lessons/round-98.md:15-23` is where S622 is actually grounded. The grounding claim therefore rests on the lesson Gate, not on either counter — the plan's "Sourced claim: C3 rests on S622" (`plans/round-98-claims.md:156-159`) overstates the instrument. Smallest correction: "C3 rests on the lesson `## Gate` row S622; the counter enforces citation of S620/S621/S622 by name only". |
| C3 disclosed limit `plans/round-98-claims.md:148-152` "The table grades the eight named boundary classes and every row present in the section; it is not a proof over all `(T, nd)` pairs" + "the graded mutant is +1, the class is ≥+1" | class ≥+1 caught | **True for uniform overcharge; undisclosed qualifier** | Verified above (+2 caught on both new cells). But as with C2, *conditional* overcharge (only some headers) and *compensating* overcharge (+1/header −1 elsewhere) are outside the "class" and undisclosed. Also "every row present" is enforced only for rows matching the `ROW` regex (`:39-41`) — a boundary row in a non-conforming format (no trailing `|`, different spacing) is silently skipped, not mismatched; only `rows != 8` and `REQUIRED - seen` catch it. Format evasion is possible but the `rows == 8` gate makes it partial. Disclose: "every *regex-conforming* row present". |

## M2 — "captured by the counter's own control run": false

Lesson `corpus/lessons/round-98.md:50-56` (M2):

> Evidence: the first r97set control receipt printed `cells=16`, not 17 — `W01-slow-x1` had
> been dropped from the cells list when the W18/W19 rows were inserted… Captured-by: the
> counter's own control run (the `cells=` count in the summary line). Fix: W01 restored…
> Shown able to fail: the 16-cell receipt stands in the wave dir as the red evidence.

**No check names the missing cell.** In `--control` mode the counter returns at
`tools/round98-router-budget.py:653-675`, *before* the `want_cells` comparison at `:715-722`:

```python
if a.control:
    n_ok = sum(1 for good, _, _, _ in natural.values() if good)
    n = len(natural)                    # 16 in the defective run
    survived = int(n_ok == n)           # 16 == 16 → 1
    ...
    else:
        ok = survived if a.expect == "survived" else caught   # survived=1, expect=survived → ok=1
    print(f"ROUTER_BUDGET98_CONTROL cells={n} … survived={survived} … ok={ok}")
    return 0 if ok else 1               # exit 0, GREEN
```

A 16-cell control run with all 16 graded cells ok prints `cells=16 cells_ok=16 …
survived=1 … ok=1` and exits 0. Nothing compares `n` to `len(R97_CELLS)` (17) or names
`W01-slow-x1`. The only route that would have caught it — `len(cids) == want_cells`
(`:722`) — is unreachable from `--control`, and the failing receipt *was* a control receipt.
Only `--expect-cell W01-slow-x1` would have named it (missing cell → exit 2, `:661-664`),
but the legacy control ran without `--expect-cell` (`expect_cell=-` in the surviving receipt,
`controls/c2-legacy-mutants.out:18`).

**The "red evidence" is absent.** `grep -rn "cells=16" <lane> --exclude-dir=.git` → only the
lesson prose itself; `git log --all` shows every committed `c2-legacy-mutants.out` blob
(`34ad44e9`, `2c650b0f`, `f153aef8`) is `cells=17 … ok=1`. The 16-cell receipt was overwritten/
never committed — it "stands in the wave dir" only as a prose claim, and `.ufo/waves/round-98/controls/` holds one `c2-legacy-mutants.out` (17 cells).

**Verdict: captured-by is false.** The catch was made by **L1 reading the printed count**,
not by the counter — whose exit code was 0. This is exactly the round's standing failure class
("the counter goes green on a narrower property than the sentence claims"): the control run's
green property was "every *run* cell survived", not "the 17 round-97 cells survived".
M1's honest pattern is "Captured-by: the wave (RV01SelfAssess), not the counter" (`round-98.md:44-45`);
M2 should carry the same attribution. Smallest correction: change M2's `Captured-by` to
"`L1` read of the `cells=` summary line — the control run exited 0 (`ok=1`)" and either commit
the 16-cell receipt or delete "the 16-cell receipt stands in the wave dir as the red evidence".
The lesson's own contrast makes this material: M1 and M2 are presented as different capture
routes, but M2's route does not exist in the instrument.

## Disclosed limits: honest, except (f) and the S622 grounding

- **C1 `plans/round-98-claims.md:72-73`** ("The audit grades exactly the 20 named surfaces; other
  SCORECARD rows and prose elsewhere are not graded") — **honest**. Live ungraded cells at HEAD:
  `SCORECARD.md:15` (operability row, round-83 terminals), `:16` (freshness row, round-83),
  `:18` (coverage, row 9, unbounded prose), `:19` (calibration, unbounded prose), `:20`
  (adjacency, only sha/pipe-count graded),
  `SCORECARD.md:6` ("Current authority (round 96) … Latest measured round: 96" — false the moment
  M1/M2/M3 are measured, ungraded), plus every `§Round NN` section below `## Axes`. A false
  sentence planted in any of those stays green. So the task's question is answered: **"the lane's
  graded self-assessments match the repo" is false as written** — the instrument's property is
  "the 20 named surfaces match the repo". The disclosed limit is honest, but the *headline sentence*
  and `claims.json`'s identical `name` are not narrowed to it; the limit does not cure the headline.
- **C2 (f)** — a limit that contains a false coverage clause ("W11 does") is not honest (see table).
  (a)-(e),(g) are honest in substance; (g) overstates enforcement as noted.
- **C3** — "not a proof over all `(T, nd)` pairs" is honest; "the class is ≥+1" needs the
  uniform-overcharge qualifier; the S622 grounding is lesson-carried, not counter-carried (see table).

## Smallest safe corrections (no frozen predicate is changed)

1. C1 headline → "the lane's **20 named** self-assessment surfaces match the repo, heading included"
   (plan §C1 heading, `claims.json` C1 `name`, lesson §5-8).
2. C2 headline → append "as shown by the control receipts (`survived=1` on the 17 cells,
   `caught=1`/`cell_ok=0` on W18/W19)"; define the graded class as **uniform** +1/header (and
   uniform ≥+1/header).
3. C2 (f) → "(**W14** does, from the `-` side, in the same run)".
4. C3 headline → "the step-budget boundary table grades the real-parse arithmetic for the two T
   values inside the overcharge window"; qualify "every row present" with "every `ROW`-regex-
   conforming row"; state the S622 grounding rests on the lesson Gate, with the counter enforcing
   citation-by-name only.
5. M2 → re-attribute capture to `L1`'s read of the summary line (counter exit was 0); commit or
   withdraw the "16-cell receipt stands in the wave dir" red-evidence claim.
6. None of the five requires touching a frozen predicate, counter, or tracked lane file — they are
   sentence narrowings of the kind the standing failure class demands.

## Evidence

- `python3 tools/round98-self-assessment-audit.py --repo . --rev HEAD` → mismatches=3.
- `python3 tools/round98-depth-boundary-audit.py --repo . --rev HEAD` → rows=6 mismatches=4.
- `git show HEAD:SKILL.md | grep -n "Round 97 correction"` → heading "the three graded
  forgeries" (`SKILL.md:2443`); "The six rows below" (`SKILL.md:2449`); "four probe variants
  survive all 13 of its cells" (`SKILL.md:2466`).
- `git show HEAD:SCORECARD.md` depth row (`SCORECARD.md:17`): "six KV-free rows … four graded
  probe forgeries W14…W17" — stale at freeze, only the regexp in check 16 sees it.
- `tools/round98-router-budget.py:653-675` (control early-return, no `want_cells`) vs `:715-722`
  (predicate-only count gate); `:661-664` (`--expect-cell` names missing cells — unused by the
  legacy control).
- `grep -rn "cells=16"` over the lane → lesson prose only; all committed `c2-legacy-mutants.out`
  blobs → `cells=17`.
- Borders recomputed: 800,000 nd=1 real 4,800,004 / +1 5,600,004; 520,000 nd=4 real 4,680,004 /
  +1 5,200,004; +2 probes 6,400,004 / 5,720,004; flat-6 probes 4,800,004 / 3,120,004 (green on
  W18/W19); W11 overcharge 4,900,004 (green); W14 undercharge red per
  `controls/c2-new-mutants.out:15-21`.
