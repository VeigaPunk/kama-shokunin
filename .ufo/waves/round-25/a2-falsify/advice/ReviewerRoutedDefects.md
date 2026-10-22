# ReviewerRoutedDefects: round-24 routed defects checked against round-25 repo state

Verdict: defect found. Medium: the PM08 wording change has no authority that routed defect 2 requires, and the lane's own records disagree on whether it is a repair. Low: routed defect 3's original-hash sub-item is not dispositioned, and two visibility gaps need one line each. The M-series repair, the locator correction and the no-overclaim checks hold.

Pinned: committed bytes at fa3b62ae6475d111eb466d79af616aeebb08bbb9. Lane master is 46be41cf674301953837c8863cd2026e8a21fcb0, one commit later, which adds only the a2-falsify spec, dispatch, registry and report draft. Base: 147f5bdd3228ab712520b5f377346cb2d9a64769. Check numbers C1-C29 refer to `.ufo/waves/round-25/a2-falsify/out/ReviewerRoutedDefects/checks.md`.

Short names used below: M-series or M11, M17, M33 are the isolation mutants in `tests/report-audit/isolation-mutants.py`. PM01-PM11 are the promisor mutants in `tests/report-audit/promisor-mutants.py`, and PM08 is their manual review-only note. C1 and C2 are the two round-25 claims (calibration repair, context-capacity learning). K-cells, X-cells and L-cells are the context-capacity fixture cells.

## Per-defect verdicts

Routed defects: `corpus/lessons/round-24-verifier-spotcheck.md:149-160`. Dispositions: `corpus/lessons/round-25.md:55-77`.

| # | Routed defect | Verdict |
|---|---|---|
| 1 | Keep original clauses and the seven original-unmet cells; never turn amended 47/47 into success | Holds (C2, C4, C20) |
| 2 | Correct PM08 and registered mutation semantics only through separately authorized work; keep the gap visible | M-series repair holds (C5-C13). PM08 wording: defect, authority and claim status (finding M1) |
| 3 | Keep the append lineage, original-hash gaps and exact ScribeLesson/ConnSources locators | Locators and lineage hold (C16, C18). Original-hash gap not dispositioned (finding L1). Root report bytes not verifiable from the lane (finding L2) |
| 4 | Keep native-role, chronology, scope and changed-input qualifications; no no-effects, backend-identity, continuous-floor or full-isolation claim | Holds (C19-C21). Minor: continuous-floor not named; native-role limits not restated in round 25 (finding L4) |
| 5 | H2 operator-owned; no floor approval, replay, policy-hold recovery, endpoint or service action, promotion or next-round permission | Holds as worded (C22, C23). Visibility gap on the live fixture's POST scope (finding L3) |

## Findings by severity

### Medium

M1. The PM08 wording change has no recorded authority, and the lane's records disagree on whether it is a repair.
- Routed text, `round-24-verifier-spotcheck.md:151-152`: "Correct stale PM08/registered mutation semantics only through separately authorized future work".
- The change: `SKILL.md:887` and `SKILL.md:992-993` now call PM08 a "manual review-only note, unexecuted, uncredited" and "not settled evidence".
- The lesson calls it repaired and cites no authority: `corpus/lessons/round-25.md:58-63`. The LOG says "PM08 wording in `SKILL.md` corrected": `LOG.md:1667-1668`.
- The preregistration limits the repair to the M-series instrument (`.ufo/waves/round-25/preregistration.json:14`). Its `not_claimed` list excludes "PM08 execution credit" (`:26`). No amendment, pilot or errata file mentions PM08 wording (C15).
- The SCORECARD limits the repair too: "This repairs only the M-series portion of routed defect 2; PM08 remains outside the claim" (`SCORECARD.md:1270`).
- Content check: the new wording matches the round-24 decision (`corpus/lessons/round-24.md:318-327`) and the instrument's own review-only entry (`tests/report-audit/promisor-mutants.py:419-437`). I found no harm from the wording itself. The defect is the authority and the claim status.
- Smallest correction: either (a) cite the authorization in lesson item 2 and the LOG entry (the wave brief or operator instruction that covers routed wording), or (b) relabel the change as "wording alignment, authority pending closure". In both cases, make `SCORECARD.md:1270` and lesson item 2 say the same thing.

### Low

L1. Routed defect 3's original-hash sub-item is not dispositioned.
- Routed text, `round-24-verifier-spotcheck.md:153-154`: "Preserve the unresolved prepared-versus-landed append lineage, original-hash gaps and exact ScribeLesson/ConnSources locator corrections."
- The round-25 disposition (`corpus/lessons/round-25.md:64-73`) covers the locator and the lineage. It never names the original-hash gap.
- The gap is real. The fleet-root report line 16 says the ScribeLesson 185-byte supersession headers were "removed ... with creation-size/body but no prior original-SHA proof" (C17). No round-25 change touches it, so it is preserved in substance and undocumented.
- Smallest correction: one sentence in lesson item 3, for example "Original-hash gap: ScribeLesson's 185-byte headers have no prior original-SHA proof (kama.md:16, unchanged)."

L2. The round-24 root report's bytes cannot be checked from the lane.
- `.ufo/reports/round-24/kama.md` is not tracked in the lane (C17). The closure's commit 9eeecdcc is not in the lane repository.
- The fleet-root copy has mtime 2026-10-21 22:48, which predates round 25. Its sha256 is 89b9f529d3ed323d9a2c9af0b3f3e2aeb324365971b19fa030cf6bb7dbd648ac. No recorded digest in the closure directory matches it or names it (C17).
- `.ufo/waves/round-25/a2-build/advice/ScribeLocatorErrata.md:43` says "Round-24 report bytes untouched (read-only seat)". That is a seat's statement, not a hash comparison.
- Smallest correction: record the sha256 above as the baseline in lesson item 3, and say that no earlier digest exists.

L3. The live fixture's POST scope is disclosed only in the corpus README.
- C2 posts to `/tokenize` (`tools/kama-context-capacity.py:494`) and to `/completion` (`:520`).
- `corpus/README.md:399-400`: "The round-16 fixture scope is still pending L0 ratification; the L cells used POST `/completion`, beyond the GET-only round-16 admission." The lesson's item 5 (`corpus/lessons/round-25.md:75-77`) and the LOG entry do not mention it.
- Routed item 5 is not violated as worded: the POST use comes from the preregistration, not from this note.
- Smallest correction: one sentence in lesson item 5 and the LOG entry, for example "C2's live cells used POST /tokenize and POST /completion, beyond the GET-only round-16 admission; fixture scope pending L0 ratification." Also name `/tokenize`, which the README omits.

L4. Routed item 4 omits continuous-floor, and round 25 does not restate the native-role limits.
- Routed text, `round-24-verifier-spotcheck.md:155-156`, names "continuous-floor". The round-25 disposition (`corpus/lessons/round-25.md:73-74`) does not.
- No round-25 text makes a continuous-floor claim (C21), so nothing is overclaimed.
- "Native-role ... kept": round-25 text does not restate the captured-alias and answering-provider limits (C19). They survive only in round-24 records, which no round-25 commit touched (C2).
- Smallest correction: name continuous-floor in lesson item 4, and say that the native-role limits remain in round-24 text.

L5. A new SKILL statement lacks the other-build label.
- `SKILL.md:189-190`: "both slots share one 16384-cell pool".
- `corpus/knowledge/context-capacity.md:178-185` labels the basis as the sibling lane's production capture from another build, "not a kama observation" (C27). The SKILL line carries no such label.
- Smallest correction: add "(other build, sibling capture; not a kama observation)" to `SKILL.md:189-190`.

L6. Author trend readings in the round-25 SCORECARD section.
- `SCORECARD.md:1291-1293`: "expansion improved", "quality unchanged-to-improved", "discernment improved".
- These are not promotions. No score moved, and `SCORECARD.md:1294-1295` says "Outside closure alone decides admission". But the round-24 quality verdict is still "harmed" (`corpus/lessons/round-24-verifier-spotcheck.md:144`). These readings should not be read as repairing it.
- Smallest correction: mark the trend sentence as "author reading; closure decides".

L7. Report draft placeholders (landing hygiene).
- At 46be41c, `.ufo/waves/round-25/report-draft.md` contains `LANE_TIP` (lines 6 and 68), `WAVE2_COMMITS` (line 61), `END_CENSUS` (line 77), and "TBD" trend verdicts (lines 87-89) (C29). Fill or remove each before landing.

### Note (no action needed for this item)

N1. The isolation mutant id M08 is absent (C11). It has never been present in the file's history: the first version, e0f0434, already skips it. No document mentions it. No id was reused or retired in round 25. Harmless. The closure may want a one-line note in the instrument docstring.

## New harms checked

- No round-24 file changed (C2). No round-24 claim was restated as success (C20).
- No llama-server process or listener is left (host check, read-only). Every C2 port closed and every child reaped (C23).
- No registered consumer port was used. The C2 cells used 47400-47413, inside the tool's range 47400-47419. That range does not contain 8080 or 34113 (pinned as refused, C24), nor any other port named in SKILL.md (11434, 8790, 8791, 8888, 34955, 41453, from the historical registry text at SKILL.md:171-180).
- No lane file was edited by this seat outside its own out and advice paths.

## Residual risk

- C1 measures anchor occurrence, not semantics. M17 may be unkillable (`tests/report-audit/isolation-mutants.py:27-40` says so, marked as an inference). The 26-of-28 kill count carries that open denominator question.
- The promisor instrument's anchors are fresh only at this tip (C13). Nothing in the round-25 record re-runs them at landing.

## Verification gaps

- The lsp device is not mounted (`xd://lsp`: "No such tool"). Caller and definition checks used text search and direct code reading.
- I did not repeat the 28-mutant grid. I read the committed full-run JSON (C12) and re-ran the cheap anchor count (C7-C9).
- I did not start, probe or repeat any llama-server cell. I parsed the committed receipt (C23).
- External source rows S106-S113 were not re-opened. They are outside these five defects.
- The round-24 root report has no recorded digest. The sha256 above is the first baseline.
- Not checked: the coverage erratum at `SCORECARD.md` lines 562 and 1019, and any claim outside the five routed items.

## Files written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/out/ReviewerRoutedDefects/checks.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/out/ReviewerRoutedDefects/promisor-anchors-tip.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/advice/ReviewerRoutedDefects.md (this report)
- Scratch only, outside the lane: /fast/scratch/hyaku/kama-r25a2w2/ReviewerRoutedDefects/ (clone of the lane at fa3b62ae; efe58e96 archive; first-isolation-mutants.py; promisor-anchors-tip.json and .err; c1-tip-mutants.json; root-report-sha.txt; report-draft-46be41c.md).

Tool installs: none. Host git 2.56.0 observed and not changed.
