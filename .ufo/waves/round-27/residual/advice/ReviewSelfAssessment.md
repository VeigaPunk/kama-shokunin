VERDICT: partial — 56 of 57 checkable statements in the three self-assessment surfaces verify against repo state at 52632caa; the one failure is a dangling forward pointer (the round-27 report named by the C1 "Measured commit" cell does not exist).

Scope: `SCORECARD.md` "## Round 27" (lines 1365–1401), `corpus/README.md` "Frontier disposition — round 27" (lines 412–421), `SHONEN.md` (whole file). Tip verified: `git rev-parse HEAD` → `52632caa2ed813c1c12f7a9dcab3556b4f0bd9eb`. Read-only git only; no edits.

## Statement table — SCORECARD.md ## Round 27

| # | Statement (SCORECARD:line) | Check | Result |
|---|---|---|---|
| 1 | C1 claim type "measured" (:1369) | prereg C1 has predicate/target/kill_rule | holds |
| 2 | Axis = depth (:1369) | `preregistration.json` `"axis": "depth"` | holds |
| 3 | depth 7 → 7 (:1369) | round-26 row `depth 7 → 7` (:1322); canonical table :21 `1 → 7`; no promotion claimed | holds |
| 4 | Verdict "miss (honest stop)" (:1369) | kill_rule: "counted < 15 at the landed tip is a miss"; lesson §Claims; LOG :1762 "C1 — miss" | holds |
| 5 | "withdrawn before data" (:1369) | `a3/plan.json` `C1.disposition = "withdrawn before data"` | holds |
| 6 | "no data seat dispatched" (:1369) | plan.json: "No data seat of round 27 was ever dispatched"; lesson §Claims | holds |
| 7 | "under the frozen kill rule counted < 15 … is a miss" (:1369) | prereg `kill_rule` verbatim match | holds |
| 8 | Evidence pointer `a3/plan.json` (:1369) | file exists, `kama-r27-attempt3-plan/v1` | holds |
| 9 | Evidence pointer lesson §Claims (:1369) | `corpus/lessons/round-27.md` §Claims present | holds |
| 10 | Tip receipt `a3/c1-tip.out` (:1369) | exists; body: `registered 0 counted 0 target 15 met False not-counted []`, exit 0, measured at d183ec57 | holds |
| 11 | Counting command = prereg C1.command (:1369) | prereg: `/usr/bin/python3 .ufo/waves/round-27/count-c1.py --out <receipt.json>   (from the lane root of a fresh clone… --lane DIR … --repo GITDIR)` — SCORECARD quotes the prefix | holds |
| 12 | Measured commit "lane tip at report time (see the report)" (:1369) | no `kama.md` in fleet `.ufo/reports/round-27/` (only chousa, kagi, kaidoku, kake, kengaku, kotodama, mori, tameshi, tsukuroi); lane `.ufo/reports/` holds only round-5; `find .ufo/waves/round-27 -name 'kama*.md' -o -name '*report*'` → 0 hits | **mismatch** — pointer names an artifact that does not exist at the assessed tip (forward reference; the measured commit itself is recorded in `a3/c1-tip.out` as d183ec57) |
| 13 | X1 claim type exploratory (:1370) | plan.json `X1.type = exploratory` | holds |
| 14 | Axis = calibration (:1370) | plan.json `axis = calibration` | holds |
| 15 | calibration 7 → 7 (no number) (:1370) | prior calibration 7 (round-26 correction :1354; canonical :23); AXES.md:52–55 permits verdict-instead-of-number | holds |
| 16 | "`unprovable` until a named non-author reviewer rules" (:1370) | fleet `AXES.md:43–51`: `unprovable-but-better` only with named non-author reviewer, else `unprovable`; plan verdict_rule identical | holds |
| 17 | "wave seats are evidence only" (:1370) | plan: "Seat findings are evidence for the reviewer, never the verdict" | holds |
| 18 | Pointer `knowledge/echo-discriminating-counters.md` (:1370) | exists (140 lines) | holds |
| 19 | Pointer "QUALITY.md KQ37 and its round-27 qualification" (:1370) | KQ37 row at QUALITY.md:219; "## Round 27 qualification" at :221–242 | holds |
| 20 | Pointer "lesson §X1 evidence" (:1370) | exists; 8-row seat table | holds |
| 21 | X1 surface = method entry + admission criterion, "not a new server error signature" (:1373-1375) | entry :10–12 "not a new llama-server error signature"; KQ37 is a criterion row | holds |
| 22 | "round-26 counter's echo test read stored request text (count-c1.py:384)" (:1375) | `git show eb09e742:…/count-c1.py:384` → `c["e_not_echoed"] = sig not in req_bytes` (sha 6501737c… matches frozen round-26 counter) | holds |
| 23 | "a base-tree shortcut met it 12/12" (:1375) | `round-26-verifier-spotcheck.md:98–116`: `registered 12 counted 12` on base `1560e4d8` | holds |
| 24 | "QUALITY.md held no echo rule" (:1376) | `git show 0ec32cac:corpus/QUALITY.md | grep -in 'echo\|KQ37'` → exit 1 (empty) | holds |
| 25 | "round-26 preregistration and spot-check named the echo and split-message classes as round evidence only" (:1376-1377) | r26 prereg :26 names "request-echo" and "one message split into several rows"; spot-check defect 2 routes the fix; entry :14–20 confirms neither was lane knowledge | holds |
| 26 | defects 1, 3, 4, 5, 6, 7 repaired (:1381) | d1: LOG :1728 + :1747 two appended corrections; d3: `repairs/d3-r26-shortcut-pins/{info-help.txt,info-version.txt,README.json}`; d4: `repairs/d4-r26-dead-seat-errors/` three jsonl + README.json; d5: mislabel verified (`c1-tip.out:2` `tree=7e5ff9b5…`, `git cat-file -t` → commit; `c2-kq36-tip.out:2` same); w1a3 `ReviewRepairD5D6Notes.md` verdict holds; d7: S138 :150 "supersedes S133 … 1810-1835" | holds |
| 27 | "defect 2 met by the A3 counter and KQ37 with the shortfalls recorded" (:1381) | A3 counter sha256 = `49491b80…2765` (frozen bytes, verified); decoded-string clause + shape refusal documented entry :94–121; KQ37 :219 + qualification. Caveat: lesson :47 calls the per-class receipt leg "met only vacuously" — SCORECARD omits the qualifier (see N2) | holds (note) |
| 28 | "defect 8 (count-c2.py reads cell values from the receipt) open" (:1382) | `.ufo/waves/round-25/count-c2.py` still compares receipt `cells[]` values directly (:122–189); no round-26/27 counter replaced it; lesson :80–83 "not fixed" | holds |
| 29 | Calibration note: four first-landed errors caught by wave seats (:1385-1386) | all four seat reports exist: `w1a3/advice/{ReviewRepairD1Log,CriticEntryFactsSources,CriticC1Withdrawal,ReviewUntrackedDisposal}.md` | holds |
| 30 | "each is corrected by an appended entry or a superseding row" (:1386) | LOG miscount → appended entry (LOG :1747); S136 → S139 superseding row; "neither meets nor misses" + "1853" → first-landed lesson text (`git show 324d5d6:corpus/lessons/round-27.md` :6, :20) revised in place with an appended parenthetical disclosure — not literally an appended entry or row (see N3) | holds (note) |
| 31 | Other scores held: operability 8, freshness 8, coverage 9, adjacency 7 (:1389) | identical to round-26 held line (:1354-1355); freshness 8/coverage 9 reach via appended round-10 errata (canonical table :20,:22 superseded, disclosed) | holds |
| 32 | "Capabilities: none claimed" (:1389) | X1 counting command "none"; no capability row added | holds |
| 33 | Planned r28 "Repair defect 8" (:1394) | consistent with defect 8 open | holds |
| 34 | Planned r28 "counter must meet KQ37 with its round-27 qualification (boundary leg, Unicode case folding)" (:1394-1396) | qualification §1 boundary leg (:226-235) and §3 case folding (:240-242) exist | holds |
| 35 | Planned r28 "committed non-author control receipts per class before any data seat" (:1396-1397) | KQ37 row + kill_rule require exactly this | holds |

## Statement table — corpus/README.md round 27

| # | Statement (README:line) | Check | Result |
|---|---|---|---|
| 36 | `knowledge/echo-discriminating-counters.md` entry row (:416) | file exists | holds |
| 37 | Covers: refuses decoded echoes, one row per message frame, signature inside server-owned text (:416) | entry :25–140 + KQ37 + qualification §1 | holds |
| 38 | "live b11755 echo at `server-common.cpp:1375` (S137)" (:416) | SOURCES.md:149 anchors `server-common.cpp` lines 1363–1377 @704366d, sha b4f4aae7…; live probe `w1a3/out/ExecLiveEchoProbe/` exists | holds |
| 39 | "RFC 8259 §7 escapes (S136, S139)" (:416) | SOURCES.md:148, :151 both present; S139 supersedes S136 wording | holds |
| 40 | "not a new server error signature" (:416) | entry :11 verbatim intent | holds |
| 41 | Round column = 27 (:416) | consistent | holds |
| 42 | "C1 (depth, new request-validation signatures) was not run on data and is a miss" (:418-419) | prereg axis depth, SKILL surface "request-validation signatures"; kill-rule miss confirmed by tip receipt | holds |
| 43 | "K05 beyond the lane fixture, router-mode model errors, other engines and registered-consumer reconciliation remain open" (:419-420) | README :63–72 + :271-275 keep K05 authorized-runtime-dependent; round-26 disposition names router/engines/consumers open; PROVINCE :45 write boundary keeps consumers operator-owned | holds |
| 44 | "X1 is exploratory; no admission is claimed here" (:420-421) | plan X1 + AXES rule; no verdict asserted in README | holds |

## Statement table — SHONEN.md (all four `[~]` author assertions)

| # | Statement | Check | Result |
|---|---|---|---|
| 45 | SKILL.md §§Decision table, Error signatures, Checklist (:5-6) | headings exist: `## Decision table` :125, `## Historical error signatures` :167, `## Checklist` :193 | holds |
| 46 | LOG.md §§round 1–3 executed reconciliation/invocation history (:7) | `## round 1` :7, `## round 2` :100, `## round 3` :203 | holds |
| 47 | "current `DEAD` is not model readiness" (:7) | LOG rows DEAD = `connection-refused` (:211, :285) | holds |
| 48 | Round 16: LOG §round 16 + `live/receipt.json` 10/10 v1 checks, unregistered port, MODEL_OK/matched exit 0, teardown (:8) | receipt schema `kama-llamacpp-live/v1`, `checks` len 10 all `passed:true`; port 37527 absent from `registry/endpoint-consumers.tsv`; LOG :925–990 | holds |
| 49 | Round 17: `receipt-{1,2,3}.json` 11/11 v2 checks, gate VALID with four pins (:8) | each receipt `checks` len 11 all `passed:true`; `live/gate.txt`: `VALID` ×3, exit 0 ×3, probe+tool pins printed (four-pin set corroborated lesson :172) | holds |
| 50 | `controls.py` "8 bad fake-server shapes rejected, frozen pair accepted 6" (:8) | lesson :166–168: current run 0 accepted-bad (bad shapes k1–k8 rejected); frozen tool+gate 6 accepted-bad; controls.py k1–k8 docstring | holds |
| 51 | SKILL.md §Checklist + `snapshot-history.md` §Run it (:9-10) | SKILL :193; snapshot-history `## Run it` :7 | holds |
| 52 | "independent execution review remains open" (:10) | consistent; no closure evidence | holds |
| 53 | PROVINCE.md §Write boundary + `cross-lane-scope.md` (:11-12) | PROVINCE :45 "Write boundary (hard)"; knowledge file exists | holds |
| 54 | "service repair, routing and credentials remain operator/sibling-owned" (:12) | PROVINCE write boundary + cross-lane-scope entry | holds |
| 55 | All four boxes `[~]`, none `[x]` | file shows `[~]` ×4 | holds |
| 56 | SHONEN names no round-27 surface | nothing in SHONEN claims round-27 artifacts; consistent (no promotion claimed this round) | holds |
| 57 | Box-2 wording "no non-author mark" both times (:8) | consistent with no non-author verifier | holds |

## Mismatch count: 1 (statement 12, low severity — forward reference)

The C1 row's "Measured commit" cell reads "lane tip at report time (see the report)". No round-27 kama report exists in the lane or the fleet `.ufo/reports/round-27/` tree at the assessed tip (nine sibling lanes filed; kama absent). The measured commit itself is recoverable (`a3/c1-tip.out` names d183ec57; `git log` shows 52632ca is exactly the receipt-landing commit), so this is a dangling pointer, not a wrong fact — it presumably resolves when the round-27 report is written at closure.

## Precision notes (not counted as mismatches)

- N1 — statement 12 is the only unresolvable pointer; every other file, line and sha pointer resolves.
- N2 — statement 27: SCORECARD says defect 2 "met by the A3 counter and KQ37"; the lesson (:47) adds "met only vacuously" for the no-data-seat receipt leg. The SCORECARD sentence omits the qualifier but stays consistent because the claim was withdrawn — the vacuity is conveyed by the C1 row itself. Borderline understatement, not a wrong claim.
- N3 — statement 30: two of the four same-round corrections (withdrawal wording, 1846 header) were made by in-place revision of first-landed draft text plus an appended parenthetical disclosure (`git diff 324d5d6 d183ec5 -- corpus/lessons/round-27.md`), not strictly "an appended entry or a superseding row". The two record-class corrections (LOG entry, SOURCES row) do follow the appended/superseding pattern. Wording stretch, disclosed in place.
- N4 — canonical axis table (SCORECARD :20, :22) still shows freshness 7/coverage 8 from round 3/1; the 8 and 9 come from appended errata. Pre-existing structure, not a round-27 statement.

## Residual risk / verification gaps

- X1's `unprovable` verdict depends on "no named non-author reviewer on record" at the assessed tip; the residual wave is in flight and may add one later — a re-check after closure is cheap.
- Seat-result consistency inside the lesson §X1 evidence table (the 12/12, 0/12, 1/12 replay numbers) was spot-checked via artifact existence and the ExecOfflineEchoReplay/ScoutRawEchoInLaneTools reports, not re-executed; I ran no counter and no live server (no port block in my item).
- The d3 pin claim "sha256 equal what the pinned b11755 binary prints today" is recorded in `repairs/d3-r26-shortcut-pins/README.json:15` by the L1; I did not re-run `llama-server --help/--version` (contract: seats without a port block start no server).
- SHONEN's four `[~]` boxes remain author assertions by design; the pointers all resolve but the underlying "no named non-author verifier" status is asserted, not independently shown.
- No tools installed; none needed (all checks used git, sha256sum, python3 stdlib).
