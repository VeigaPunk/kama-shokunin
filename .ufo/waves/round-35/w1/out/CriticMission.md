# CriticMission — round 35

Seat: CriticMission. Target: the MISSION.md versus prompt axis conflict. Judged on calibration. MISSION.md was not edited. Neither frozen predicate was changed.

## Verdict

A calibration claim is allowed when mission files win. Naming the conflict without editing MISSION.md satisfies the round instruction. The preregistration's reason for keeping C1 on calibration does not.

"Mission files win" strikes prompt text that conflicts with binding sentences in MISSION.md and AXES.md. It does not promote the historical example at MISSION.md:29 into the current assignment. The binding fleet-shape sentences put current axes on the `shokunin.conf` LANES row. That row is operability + calibration. The prompt copies that row, then states the precedence clause. The copied row does not conflict with the binding sentences, so the clause does not strike it. Calibration is one of the six axes AXES.md defines. Among the assigned pair, the recorded reading is calibration 7 against operability 8, so a calibration claim is the lowest-assigned-axis claim, not an off-axis extension.

The round instruction is: MISSION.md:29 still says operability + freshness; do not edit it; name the conflict if axis authority is touched; do not change either predicate. Not editing, naming the conflict in the round report, and leaving C1 calibration 7→7 and C2 coverage 9→9 unchanged meets that instruction. Naming is not a license to retarget C1 onto freshness, and it is not proof that the preregistration's selection rule is the mission rule.

## Counterexample

Proposed approach, `.ufo/waves/round-35/preregistration.json` `mission_conflict`: C1 works calibration because it is the lowest non-retired numeric axis, tied with depth and adjacency; the conflict is named and therefore does not change either predicate.

That reason fails on the strongest local counterexample.

1. Wrong denominator. MISSION.md:43 and AXES.md ("at least one claim works the lane's lowest-scoring non-retired axis") select inside the lane's assignment, not across every scored axis. Depth 7 and adjacency 7 are not on the live pair. A tie with them does not make depth or adjacency equally obligatory, and it is not why calibration is allowed. Round 11 already separated those facts (`SCORECARD.md:226-228`: lowest assigned is calibration 7 versus operability 8; the historical table tie is a different sentence). The preregistration collapses them.

2. Line-29 reading left open. If "mission files win" meant MISSION.md:29 overrides the prompt, the assigned pair would be operability + freshness, both last held at 8, and C1 calibration plus C2 coverage would miss the lowest-assigned-axis obligation. The preregistration names the string mismatch and then cites the numeric tie. It never cites the fence that makes line 29 non-current. A closure reader can reject C1 as off-assignment. That kill stays open until the name states the fence and the delegation.

3. Duplicate authorities the name does not pick. `SCORECARD.md:6-7` still says assigned LIVE axes are operability and freshness. `SCORECARD.md:192` still says MISSION.md:29 overrides the prompt. `shokunin.conf:3-4` says the conf file only tells the driver where the fleet is. Any of those, read alone, flips the verdict. Round 11 (`SCORECARD.md:222-227`) supersedes earlier current-assignment statements; it does not delete them. Citing "the conflict is named" without saying which text is current is false provenance.

## Evidence

Re-derived at fleet HEAD `0df83da5164cf40c4eb9d7e6deb9e617b1545217`. `git status --porcelain` on `MISSION.md` and `shokunin.conf` was empty. Cited commits are ancestors of that HEAD.

Committed mission sentences (`git show HEAD:MISSION.md`):

- Lines 9-11: lanes are declared in `shokunin.conf`; each LANES row carries `id`, `repo`, and `axes`.
- Lines 16-17: "Historical example — the upstream fleet's initial nine-lane config, not the current roster (axes preserved):"
- Line 29, inside that fence: `kama: ... axes: "operability + freshness (local model serving/endpoints)"`. This is the only `kama:` axis string in MISSION.md.
- Lines 50-51: conf assignments are initial; a lane may add or remove an axis only by a falsifiable claim recorded in SCORECARD.md.

`(axes preserved)` is not a live override. It is the retained parenthetical from the previous label, "Initial config (the upstream fleet's nine lanes, axes preserved):". Commit `db25a48b679adaecebe291163b24bbc1e55c2b8a` (2026-10-19, ancestor) changed that label to "Historical example ... not the current roster" and, in the same diff, wrote lines 9-11 so the current row carries axes. The kama axis string at line 29 was not rewritten (blame `e867f786e867745f41d878d759eeeffb6b5de7fa`). The same commit both demoted the yaml block and pointed current axes at the LANES row. Reading line 29 as beating lines 9-11 contradicts that commit.

Live row, committed `shokunin.conf:52`: `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`. That calibration token has been the conf row since `cdb31686d1c5165a8759eade51d7a802594a776f` (2026-10-13) and was restated by `7d02e9671f86a12646c07ba93ae6891bfba3cdf0` (2026-10-15), four days before the historical relabel. The operator who wrote "not the current roster" left the calibration row in place.

Of the nine historical axis strings, kama is the only one whose axis tokens differ from the live LANES row (freshness versus calibration). Aggregator's only difference is "mint/dormancy" versus "mint and dormancy". The example preserved upstream wording. It is not a second current roster.

Prompt bind, committed `4ae80f41bc9241473d8deb4bba5cc85efa0575b0:.ufo/prompts/kama-round-35.md:5-7`: lane axes "operability + calibration ..."; where the prompt conflicts with MISSION.md + AXES.md, the mission files win. That string is `{{AXES}}` from `templates/round-prompt.md:6-7`, filled by `scripts/shokunin-watchdog.sh:182` from `LANE_AXES`, which the watchdog parses from the conf LANES table (`scripts/shokunin-watchdog.sh:68-79`). The prompt does not invent the pair. It copies the row the binding mission sentence already designates.

AXES.md defines calibration and does not name a kama subset. It does not forbid a second claim on another defined axis. It does forbid treating every scored axis as the lowest-axis obligation.

Recorded readings used by the preregistration, not re-measured here: round 33 holds depth 7, freshness 8, coverage 9, adjacency 7 (`SCORECARD.md:1882`); round 34 states assigned axes operability 8 + calibration 7 and calls calibration the lowest assigned non-retired axis (`SCORECARD.md:1896-1897`). Retired section still says none (`SCORECARD.md:57-59`), but that block's "both assigned axes" sentence is the round-5 pair and is not the current assignment. No SCORECARD row records a falsifiable removal of calibration or a return to freshness after the conf row changed.

Conf header trap: `shokunin.conf:3-4` defers SSOT to MISSION.md + AXES.md and says this file only launches lanes. `shokunin.conf:16-18` calls the third field the improvement contract. The header loses to the mission sentence it defers to. That sentence says the LANES row carries axes. It does not resurrect the fenced example.

## Impacted axes

- Calibration. The preregistration's because-clause is a self-assessment that does not match the rule in the files it cites. Leaving it uncorrected lets a closure reject C1 as off-axis, or lets a later round treat depth or adjacency as equally required. That is the harm. C1's frozen predicate (correction rows, re-derived committed-byte facts, unchanged r34 report blob) is not the defect and must not be rewritten to "fix" it.
- Operability and freshness. A line-29-wins reading would obligate one of them and would change the frozen C1 axis. That retarget is the correction this seat rejects.
- Coverage. C2 stays an extension on a distinct defined axis under the winning reading. It is not made illegal by the fence, and it is not the axis this conflict selects. Do not move C2 onto freshness to paper over the name.

No axis score is moved by this review. Calibration remains the recorded 7. This seat does not admit the round.

## Smallest safe correction

Do not edit MISSION.md. Do not edit `shokunin.conf`. Do not edit the frozen preregistration. Do not change either predicate. Do not retarget C1 to freshness.

Carry this name into the round report (the preregistration file is not the report):

Axis authority, named not edited. MISSION.md:29 still says operability + freshness. That line sits in the historical-example fence at MISSION.md:16-17, relabeled by `db25a48b679adaecebe291163b24bbc1e55c2b8a`; "(axes preserved)" is the retained parenthetical, not a current assignment. Binding sentences MISSION.md:9-11 put current axes on the LANES row. `shokunin.conf:52` is operability + calibration. The round prompt copies that row and yields where it conflicts with MISSION.md + AXES.md; the copied row does not conflict with those sentences. AXES.md defines calibration. Recorded assigned scores are operability 8 and calibration 7, so calibration is the lowest assigned non-retired axis. The tie with depth 7 and adjacency 7 is not the selection rule. C1 stays calibration 7→7. C2 stays coverage 9→9. Operator-side drift between the fenced example and the LANES row remains for the integrator. This name does not edit it.

KQ12 agrees with that delegation but is lane-authored. It is not the authority for this verdict. The mission sentences are.
