#!/usr/bin/env python3
"""Build the validated round-56 v2 swarm spec; 64 distinct claim/frontier attacks."""
import json
from pathlib import Path

L = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
W = L / ".ufo/waves/round-56"
OUT = W / "w1/out"
FREEZE = "efc6b3ec6fb6ea308c15855e9b8b62856f4255b7"
BASE = "e10b6d39af450e8d652be9ac2986768b531fe13f"
DIRECTIVE = Path.home().joinpath(".agents/skills/godspeed/directive.md").read_text().rstrip("\n")

context = f"""# Goal
Round 56, kama local model serving and endpoint health. One v2 wave, 64 seats, build and attack together. L1 is the frozen-topology planner seat; no planner role is added to this validated wave.

## Frozen claims (before data)
C1 — operability 8->8. At a live child with `LD_AUDIT=/usr/lib/libexpat.so.1`, `tools/round56-env-leg-test.py` calls the selected counter's `env_leg`: the round-55 counter is the red baseline (`ld_audit=missed`, exit 0), the round-56 counter detects the variable (`ld_audit=detected`, exit 0), and a one-line mutant deleting LD_AUDIT from BAD_ENV misses it so the battery's expected-detected assertion fails. Predicate, targets, kill rule and counter hash are frozen in {W}/preregistration.json. Frozen counter `tools/round56-replay-code-audit.py` sha256 fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f.
C2 — calibration 7->7. `tools/round56-prereg-check.py` parses the committed battery ROSTER and compares it exactly with the preregistered roster; base at {BASE}: present=0, met=False; freeze {FREEZE}: present=1 roster_match=1 kills=1 controls=2 met=True. Predicate and kill rule in {W}/preregistration.json. Frozen checker sha256 c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853.

## Shared read-only surfaces and write bounds
- Lane tree {L} is READ-ONLY for seats except each seat's unique output directory {OUT}/<SeatName>/; no shared production edits. Fleet root /home/vgpnk/Projects/shokunin, sibling lanes, and /home/vgpnk/Projects/shokuknow are READ-ONLY. Never mutate lane jj state/index; never run git add/commit/reset in the lane.
- Every `Report:` trailer path is relative to {L}; write it at {L}/<that path>. Any other deliverable belongs only in {OUT}/<SeatName>/.
- Per-seat scratch is `/fast/scratch/hyaku/kama-r56/<SeatName>/`; create it, set TMPDIR explicitly, use at most one shared clone, copy needed receipts into your output directory, and remove scratch before yielding. Never use /tmp for evidence or large scratch.
- Tooling authorization: any agent may install/upgrade useful tools; first read /home/vgpnk/.omp/agent/RULES.md, use official channels, and report tool/version/channel/reason. Pacman transactions are PAUSED host-wide: never invoke pacman; use uv/npx/official binary or file an L0 question. Do not change route config.
- The L1 already ran the base controls and committed the freeze. Seats are advisory, never judges. Do not change claim predicates, counters, target, kill rule or preregistration after scoring starts. Report exact command/output/exit and any defect with a proposed fix; never claim unrun checks passed.
"""

items = []
def add(name, role, axes, text):
    items.append({"name": name, "role": role, "axes": axes, "milestone": "round-56 falsification",
                  "item": f"/skill:godspeed\n{DIRECTIVE}\n\nRound 56 item {name}: {text}"})

reviewers = [
("R01C1Semantics", "Read env_leg, environ_keys and BAD_ENV at the frozen tip; establish exact detection path and any false-positive/negative edge."),
("R02C1Baseline", "Independently rerun the old counter red baseline and verify the exact missed outcome and process cleanup."),
("R03C1Build", "Independently rerun the round-56 positive control and verify LD_AUDIT is present in /proc environ and rejected."),
("R04C1Mutation", "Inspect the one-line m-drop-ldaudit mutant and verify the battery's expected-detected condition fails on it."),
("R05C1Exit", "Audit all three C1 receipts for exit=<rc> and confirm each exit is the actual child command return code."),
("R06C1Fields", "Check that C1 assertions bind exact ld_audit field values rather than a substring or presence test."),
("R07C1Scope", "Review C1 claim scope against operability definition; identify any implied live-serving claim not evidenced."),
("R08C1Source", "Re-open the committed S512 snapshot and live rtld-audit(7); verify the located quote and 25-word limit."),
("R09C2Roster", "Compare preregistration battery.roster byte-semantics with AST-literal ROSTER in the harness; list any mismatch."),
("R10C2Counter", "Review prereg-check's BASE red and frozen-tip green predicates, including missing-file behavior."),
("R11C2Mutation", "In a private fixture clone, change a roster designation and verify the prereg checker returns met=False."),
("R12SCORECARD", "Check scorecard round-56 rows, axes, commands and evidence pointers for calibration self-assessment drift."),
("R13Lesson", "Audit round-56 Gate and Mistakes against CORPUS.md: quote, access date, class/evidence/captured-by/fix, old->new changes."),
("R14Report", "Review the report draft/evidence bundle for all required headings and evidence pointers; identify missing sections."),
("R15Prompt", "Check this wave context/task specificity, 64-seat band, role-floor, attack share and scratch/write rules."),
("R16Digest", "Recompute frozen counter/checker sha256 from the committed freeze tree and compare with preregistration."),
]
for n,t in reviewers: add(n,"reviewer",["operability","calibration"],t)
critics = [
("K01C1Vacuity","Try the cheapest do-nothing control for C1: old counter against the same LD_AUDIT child; does it meet the new predicate? Explain why/why not."),
("K02C2Vacuity","Try a do-nothing checker at the base tip and a deliberately mismatched roster; verify neither reaches the target."),
("K03AxisFit","Attack the distinct-axis requirement: determine whether C1 is operability and C2 calibration rather than two calibration claims."),
("K04ClaimSizing","Challenge whether C1's before/after is one re-derivable value and reachable in one round; flag any unstated broader guarantee."),
("K05PredicateIdentity","Compare frozen C1 and C2 predicate sentences to checker code and receipt fields; list wording/code mismatches."),
("K06NoHarm","Inspect changed paths and claims for scope expansion, route/config changes, or harmed axis evidence."),
("K07SourceScope","Challenge S512 scope/tier and S513 rejection; does S512 directly ground the lesson without claiming an audit DSO loads?"),
("K08DoNothing","Independently replay both frozen base controls at BASE and assess whether either control can reach its target."),
]
for n,t in critics: add(n,"critic",["operability","calibration"],t)
mutants = [
("M01DropAudit","Mutate BAD_ENV by deleting LD_AUDIT in a scratch copy; the env-leg test must miss it and battery assertion must fail."),
("M02RenameAudit","Mutate the test's env var name to LD_AUDIT_X; prove the expected-detected assertion fails."),
("M03InvertExpected","Mutate the positive-control EXPECT from detected to missed; show the battery rejects the mutation."),
("M04RosterSwap","Change m-drop-ldaudit designation from kill to control in scratch; checker must reject roster mismatch."),
("M05RosterDelete","Delete the positive-control roster member in scratch; checker must reject the roster."),
("M06CountMutation","Change the preregistered kill/control count in scratch; checker must fail the declared target."),
("M07BaseMutation","Change preregistered base hash in scratch; checker must fail closed."),
("M08ReceiptField","Replace exact ld_audit field comparison with substring presence in scratch harness and identify whether checker catches it."),
]
for n,t in mutants: add(n,"mutation-tester",["calibration"],t)
sentinels = [
("S01WriteScope","Audit the frozen wave outputs and lane status for any seat changes outside unique out directories; report exact paths."),
("S02Scratch","Check whether the committed counter, harness and spec contain a hardcoded /tmp scratch root; report exact locations."),
("S03SecretScan","Check new round-56 files for credential values, private URLs, or op:// references; report a bounded sweep."),
("S04Policy","Verify source snapshots and corpus rows cite public sources only and do not claim the host install is globally trusted."),
]
for n,t in sentinels: add(n,"sentinel",["operability"],t)
revengers = [
("V01RouteDefects","Map round-55 verifier defects 1,2,4,5,6,7,9,10 to committed round-56 evidence; classify each closed/open/operator-owned."),
("V02StaleLesson","Re-check the round-55 Mistakes row-1 claim against its named receipt files and verify round-56 correction is append-only."),
("V03ScorecardDrift","Check stale depth/calibration SCORECARD labels and round-56 re-anchor evidence; identify remaining drift."),
("V04LateOutputs","Inventory inherited round-55 late seat output files, compare preserved artifacts, and report if any remain uncommitted."),
]
for n,t in revengers: add(n,"revenger",["calibration"],t)
executors = [
("X01ReplayC1","Run the frozen C1 battery once from the lane root; compare every printed outcome with the committed receipts."),
("X02ReplayC2","Run prereg-check against the freeze tip and report exact stdout and exit code."),
("X03CleanEnv","Set hostile GIT_CONFIG_GLOBAL and GIT_CONFIG_NOSYSTEM in a scratch environment; verify prereg-check still reads committed bytes."),
("X04EnvNames","Probe a live sleep child with LD_AUDIT set and enumerate the env_leg result; do not start llama-server."),
("X05ControlSeparation","Run C1 and C2 controls independently; show C1 outcome is independent of the C2 roster checker and vice versa."),
("X06Census","Re-run sources-census start receipt against current registry; compare to committed start output and report exit."),
("X07Anchors","Run a bounded test that the S512 quote occurs in the opened snapshot and that the lesson's quote word count is <=25."),
("X08ExitReceipts","Parse battery receipts and verify each records exit code and exact outcome field."),
]
for n,t in executors: add(n,"executor",["operability","calibration"],t)
scouts = [
("Q01Source512","Live-fetch https://man7.org/linux/man-pages/man7/rtld-audit.7.html and verify S512's quote, anchor and revision against the committed snapshot."),
("Q02Source513","Live-fetch https://man7.org/linux/man-pages/man8/ld.so.8.html; verify the S513 quote and the stated rejection rationale."),
("Q03CorpusContract","Read CORPUS.md SOURCES contract and determine whether the S512/S513 rows obey append-only and Gate rules."),
("Q04Considerthese","Check the latest considerthese proposal list and verify round-56's disposition of the still-pending pin-gap proposal."),
("Q05Province","Check PROVINCE boundary: local server env variable detection remains in kama, not auth/config or model quality."),
("Q06SiblingOverlap","Read sibling provinces for overlaps with local endpoint env audit; report contested ownership only if evidenced."),
("Q07SCORECARD","Derive assigned axes and lowest-axis obligation from shokunin.conf/AXES/SCORECARD; report any mismatch."),
("Q08CensusEnd","At final tip, run the frozen sources-census command and record exact output and exit code."),
]
for n,t in scouts: add(n,"scout",["calibration"],t)
scribes = [
("W01LessonReview","Review the committed round-56 lesson for Gate and Mistakes completeness; propose precise corrections in your output only."),
("W02ReportSkeleton","Draft a report checklist matching the required sections and all evidence that exists; do not invent results."),
("W03TrendReview","Assess expansion/quality/discernment trends from committed work only; give evidence for each, no scalar."),
("W04LogScorecard","Check the round-56 LOG and SCORECARD entries for append-only and claim/counter correspondence."),
]
for n,t in scribes: add(n,"scribe",["calibration"],t)
connectors = [
("C01PatternScan","Scan sibling lanes for a reusable pattern to freeze roster-vs-battery correspondence; return pointers and fit/no-fit."),
("C02OverlapScan","Cross-claim scan: identify any overlap between the operational LD_AUDIT classifier and calibration roster gate; advise whether causally separable."),
]
for n,t in connectors: add(n,"connector",["operability","calibration"],t)
simplifiers = [
("Z01DeadWeight","Review round-56 tools for unnecessary code or duplicated logic; propose only verified deletions that preserve the predicates."),
("Z02EvidenceLean","Review new wave evidence for derivable/oversized artifacts and identify what is necessary for independent replay."),
]
for n,t in simplifiers: add(n,"simplifier",["operability","calibration"],t)

assert len(items) == 64, len(items)
spec = {"wave":"kama-r56-w1", "reportDir":".ufo/waves/round-56/w1/out", "maxLanes":64,
        "axes":["operability","calibration"], "context":context, "items":items}
(W/"w1").mkdir(parents=True, exist_ok=True)
(W/"w1/spec.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False)+"\n")
print(f"wrote {W}/w1/spec.json items={len(items)}")
