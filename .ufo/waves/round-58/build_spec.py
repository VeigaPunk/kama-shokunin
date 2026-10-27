#!/usr/bin/env python3
"""Build the round-58 v2 swarm spec (72 seats): build and attack together, L1 is the planner."""
import json
from pathlib import Path

L = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
W = L / ".ufo/waves/round-58"
OUT = W / "w1/out"
BASE = "2f53614e6f5895560edb775cc3e74841aa0dd44c"
FREEZE = "dcd69473dd7e33b316e2ba238a48e5119a6cd809"
CTRL = "cb1ef10228193d2134440bca1175bf560b2e67be"
BUILD = "e4891d8a4c9c70e97124980c2ec9aee5762a7f0a"
MAN = "941acf70583a2b3a1d33460b31967e0efd291f3e"
DIRECTIVE = Path.home().joinpath(".agents/skills/godspeed/directive.md").read_text().rstrip("\n")

context = f"""# Goal
Round 58, kama local model serving and endpoint health (axes operability + calibration). One v2 wave, 72 seats, build and attack together. The L1 holds the planner seat; no planner role is in this wave. Seats are advisory leaves: they find and report, they never judge, commit or edit production files.

## Frozen claims (frozen before any seat result; text in {W}/controls/freeze.txt at {FREEZE})
C1 - operability 8->8: `tools/round58-battery-exec-check.py` (execution-bound battery checker; the battery is run as __main__ under a hermetic harness with a profile hook) accepts the genuine round-56 battery and 3/3 behaviour-preserving rewrites and rejects 11/11 enumerated no-op variants (roster literal intact), 0 evaluation errors. Frozen counter `tools/round58-c1-counter.py`, variants `tests/round58-battery-variants/` at {FREEZE}. Base (round-57 checker `tools/round56-prereg-check.py`): genuine=1/1 benign=1/3 noop_rejected=1/11 met=False. Build tip {BUILD}: genuine=1/1 benign=3/3 noop_rejected=11/11 met=True. Sourced on S517 (Python sys.setprofile docs).
C2 - calibration 7->7: at the measured tip `tools/round42-selfdesc-reconcile.py` reports 0 mismatches and the SCORECARD calibration row's "latest outside closure" pointer names the highest-numbered `corpus/lessons/round-N-verifier-spotcheck.md`, repeats N in "including round N" and carries the verdict token the fleet MANIFEST.json holds for kama lane_round N. Frozen counter `tools/round58-c2-counter.py --manifest-rev {MAN}`. Base: mismatches=4 (r42=1 stale=1 verdict=1 including=1); the row stated round 56 `(admitted)` while MANIFEST says round 56 `rejected-honest-stop`. After the row fix the closure-pointer counters are 0; r42 stays 1 until the L1 lands the round-58 SCORECARD section (banner and Planned heading), which is expected and not a defect.
Controls (committed {CTRL}, `.ufo/waves/round-58/controls/`): C1 do-nothing checkers always-accept, always-reject, hash-only and the base checker all fail the frozen predicate; C2 controls (claim deleted, verdict flipped only) fail it. The kill rule is the frozen text; seat-found survivors outside the 11 enumerated variants are LIMITS to report, never retroactive predicate changes.

## Revisions
Base {BASE}; freeze {FREEZE}; controls {CTRL}; build tip {BUILD}. Read committed bytes with `git -C {L} show <rev>:<path>`; the working tree may move while the L1 integrates.

## Shared read-only surfaces and write bounds
- Lane tree {L} is READ-ONLY for seats except your own unique output directory {OUT}/<SeatName>/. Fleet root /home/vgpnk/Projects/shokunin, sibling lanes and /home/vgpnk/Projects/shokuknow are READ-ONLY (never run campaign tools there). No git add/commit/reset/stash/checkout/switch/pull/push and no mutating jj anywhere. Fixture repos: `D=$(mktemp -d -p $S) && git -C "$D" init -q`, every git call names `-C "$D"`, verify `git -C "$D" rev-parse --show-toplevel` equals `$D` before the first commit; never run git/jj commit with a throwaway identity elsewhere.
- Every `Report:` trailer path is relative to {L}; write it at {L}/<that path>. Any other deliverable goes only under {OUT}/<SeatName>/. Seat tools start at the fleet root, so every path you write is absolute under {L}.
- Scratch root: `S=/fast/scratch/hyaku/kama-r58/<SeatName>`; `mkdir -p "$S"`, set TMPDIR="$S" explicitly, trap/finally removal before you yield, copy receipts into your output directory first. Never write evidence or scratch under /tmp (the reaper deletes it). One live clone per seat (`git clone --shared`, `git worktree` is forbidden, `git archive` is fine).
- Tooling authorization (operator, 2026-10-19): any agent may install/upgrade tools that help the task; read /home/vgpnk/.omp/agent/RULES.md first (official channels, update-safety gate); record tool, version, channel, reason. pacman is PAUSED host-wide: never run pacman; use uv/npx/official binary in ~/.local/bin or report the need.
- Report exact command, output and exit code for every check; an unrun check has not passed. Name what your finding attacks (claim, counter, variant, source row, lesson, SCORECARD row). Never fabricate. Keep the report under 60 lines.
"""

items = []


def add(name, role, axes, text):
    items.append({"name": name, "role": role, "axes": axes, "milestone": "round-58 falsification and frontier",
                  "item": f"/skill:godspeed\n{DIRECTIVE}\n\nRound 58 item {name}: {text}"})


OC = ["operability", "calibration"]
reviewers = [
 ("R01HarnessIsolation", "Read the harness in `tools/round58-battery-exec-check.py` at the build tip; list every side effect a hostile battery could still perform despite the patches (open(), os.* writes, socket, ctypes, importlib, pathlib methods not patched). Prove each with a scratch fixture; classify exploitable / contained."),
 ("R02ProfileHookSemantics", "Attack the sys.setprofile frame tracking: generators, threads, recursion, exceptions raised inside `run`, nested watched calls. Does the stack pop correctly? Find a fixture where a leg is recorded as run-with-counter but no counter subprocess belonged to that frame."),
 ("R03PredicateCode", "Compare the frozen C1 predicate sentence in freeze.txt to `tools/round58-c1-counter.py` and to the receipt text; list any wording/code/label mismatch."),
 ("R04VariantFidelity", "For each of the 15 files in `tests/round58-battery-variants/`, verify by diff against genuine.py that the variant is exactly what its name says (single anchored edit) and that every N-variant keeps the ROSTER literal intact and the file compiling."),
 ("R05BenignEquivalence", "Run each benign variant B1-B3 and the genuine battery for real in a scratch sandbox copy of the lane (never the shared lane tree) and confirm they behave identically to genuine; if they diverge, B-variants are not behaviour-preserving."),
 ("R06C2Semantics", "Review `tools/round58-c2-counter.py`: regex robustness for the claim pointer, the first `## Axes` section selection, manifest lookup by (type, lane, lane_round), and the maxN derivation. Find a SCORECARD edit that makes it falsely green."),
 ("R07C2ManifestBinding", "Verify the manifest rev pin: read MANIFEST.json at the pinned fleet rev and at fleet HEAD; confirm kama r56 and r57 rows, and explain what happens to the claim once the round-58 closure row appends (the pointer will legitimately go stale: say how the report should phrase the measured-tip rule)."),
 ("R08FreezeOrder", "Check the commit order base -> freeze -> controls -> build -> fix in `git log` of the lane; verify no counter, variant or predicate byte changed after the freeze commit except through a new commit named in the report; report any post-freeze change to frozen files."),
 ("R09ScorecardRow", "Review the SCORECARD calibration row after the round-58 edit against the observed repo (44 spotchecks, closure verdict); check every claim in the row re-derives at the build tip; report any new false statement."),
 ("R10CliContract", "Verify the new checker keeps the old checker's CLI and output contract (`--repo --tip --out`, exit 0/1/2, summary line shape) so downstream callers of `tools/round56-prereg-check.py` can swap it; list callers in the lane that name the old tool."),
]
for n, t in reviewers: add(n, "reviewer", OC, t)
critics = [
 ("K01DoNothingC1", "Build the cheapest control that skips the claimed C1 work and still meets the frozen predicate (e.g. a checker keyed on the variant file names, on the presence of `if False`, on a hash list). Score it with the frozen counter in scratch; if one reaches met=True the counter is wrong - report it with the receipt."),
 ("K02DoNothingC2", "Same for C2: edit only the calibration row text in a scratch clone commit so the counter reports met=True without the repo state being true (e.g. correct round and token but wrong count, or claim text injected in another section). Report receipts."),
 ("K03AxisAttribution", "Challenge whether C1 is an operability move (a runnable artifact) and C2 a calibration move (self-assessment vs observed state), whether they are causally separable (each verifiable without the other), and whether any universal clause hides in either predicate."),
 ("K04OverclaimScope", "List every sentence in freeze.txt and the SCORECARD edit that claims more than the counters enumerate (e.g. 'executed', 'binds execution'); propose the exact narrowed wording for the report."),
 ("K05SurvivorHunt1", "Think like round-57's E03: invent five NEW no-op battery variants outside the 11 enumerated (conditional-expression labels, a `run` that spawns a different counter, decoy subprocess calls, labels executed but results ignored, os._exit before legs) and run the checker on each in scratch. List survivors with receipts."),
 ("K06SurvivorHunt2", "Attack the checker's `counter>=1` rule: construct batteries where `--counter` appears in argv but the leg is vacuous (e.g. echo with --counter, calling /bin/true --counter). Report which are accepted; propose a binding that rejects them without breaking genuine."),
 ("K07FrozenCounterGaming", "Attack `tools/round58-c1-counter.py` itself: can a checker pass by detecting the fixture repo (commit message `fixture`, author c1-counter, directory names) or by reading the committed variants? Score such a checker in scratch."),
 ("K08TrendHonesty", "Given C1/C2 outcomes so far and the round-57 closure (rejected-honest-stop, discernment harmed), draft the honest wording the report should use for expansion/quality/discernment trends; flag any trend the evidence cannot yet support."),
 ("K09StagnationAndLowestAxis", "Verify from SCORECARD/AXES that calibration 7 is the lowest assigned axis, the nudge is inactive, and that C2 works it; list any rule the round's claim set might breach."),
 ("K10S513Disagreement", "Argue the round-56 outside disagreement on S513 (rejected as overlapping rtld-audit(7)): read the live man7 ld.so(8) page and the committed `.ufo/waves/round-56/sources/ld.so.8.html`; decide for or against the original rejection with located quotes <=25 words and say what QUALITY criterion the disagreement teaches."),
]
for n, t in critics: add(n, "critic", OC, t)
mutants = [
 ("M01DropCounterFlag", "In a scratch copy of the checker, delete the `--counter in argv` requirement; run the frozen C1 counter. Report whether any N variant becomes accepted (the counter must then fail; if it does not, the counter does not guard that clause)."),
 ("M02DropAssertClause", "Scratch-mutate the checker to ignore `assert_mutant_breaks_detection` execution (assert_ok always true); score with the frozen counter. N07 should flip to accepted: report."),
 ("M03DropRosterMatch", "Scratch-mutate `match` to always True; score with the frozen counter and report which variants flip (none are roster mutants, so state what the frozen set cannot see)."),
 ("M04DropKillsControls", "Scratch-mutate the `kills == 1 and controls == 2` conjunct; score and report."),
 ("M05HarnessNoWatch", "Scratch-mutate WATCHED to just `run`; score; report flips."),
 ("M06StackPopRemoval", "Scratch-mutate the profile hook so frames are never popped; score; report flips and why."),
 ("M07FakeResultExit", "Scratch-mutate fake_run's return code to 1 and its stdout to empty; the genuine battery's legs read these; report whether acceptance still holds (the checker does not depend on pass/fail of legs, state that clearly)."),
 ("M08TimeoutAndErrors", "Scratch-mutate TIMEOUT to 0 and the harness-failure branch to return 1 instead of 2; score and report whether the counter's `errors=0` clause detects it."),
 ("M09C2CounterMutants", "Mutate `tools/round58-c2-counter.py` in scratch (drop `stale`, drop `verdict`, drop `including`, swap manifest lookup key); build a SCORECARD scratch commit for each that only that mutant would pass; report which mutants survive the frozen controls."),
 ("M10VariantMutants", "Take the 11 N variants; for each, produce a one-edit repair that makes the battery genuinely run again (undo the no-op) and confirm the checker accepts it - shows each N variant was rejected for the planted reason, not incidentally."),
]
for n, t in mutants: add(n, "mutation-tester", OC, t)
executors = [
 ("X01ReplayC1Fresh", f"From a fresh `git clone --shared` of the lane at {BUILD} in your scratch, run `python3 tools/round58-c1-counter.py --repo <clone> --tip {BUILD} --checker tools/round58-battery-exec-check.py` and the checker against the lane's real round-56 battery; paste output and exit codes."),
 ("X02ReplayC1Base", f"Run the same counter with `--checker-blob {BASE}:tools/round56-prereg-check.py` against tip {FREEZE}; confirm `genuine=1/1 benign=1/3 noop_rejected=1/11 met=False` and list which variants the old checker wrongly accepts."),
 ("X03ReplayC2", f"Run `python3 tools/round58-c2-counter.py --repo <clone> --tip <rev> --manifest-rev {MAN}` at base {BASE}, freeze {FREEZE} and build {BUILD}; paste the three outputs; confirm base mismatches=4."),
 ("X04ScratchHygiene", "Run the checker and both counters with TMPDIR pointed at a fresh scratch dir and with HYAKU_SCRATCH unset; verify nothing is created under /tmp and no tree remains after exit (compare directory listings before/after)."),
 ("X05HostileGitEnv", "Run the C1 checker and counter with hostile GIT_DIR, GIT_WORK_TREE, GIT_CONFIG_GLOBAL and HOME pointing elsewhere; verify committed bytes are still read and results are unchanged."),
 ("X06PythonPortability", "Run the checker under every other python3 interpreter on the host (python3.x binaries, `uv python list`) if any; report version-dependent failures (sys.setprofile event shape, f_locals semantics in 3.13+)."),
 ("X07RealBatteryInHarness", "Run the real genuine battery (not the harness) in an isolated sandbox copy of the lane with scratch OUT dirs so it writes nowhere shared, and compare its printed leg lines with the labels the harness recorded; confirm the harness's recorded legs equal the real legs."),
 ("X08Timing", "Time the checker and the C1 counter 5 times each; report min/median/max wall seconds and whether the 60 s timeout has margin."),
 ("X09NewNoopFixtures", "Create five new committed-style no-op variants of the battery in scratch (not in the lane tree) different from `tests/round58-battery-variants/` and run the checker; deliver the files and receipts so the L1 can decide whether they become limits."),
 ("X10CensusStartEnd", "Run `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` and compare to `.ufo/waves/round-58/census/start.out`; report row count and exit code; do not edit the registry."),
 ("X11SelfdescCounter", f"Run `python3 tools/round42-selfdesc-reconcile.py --repo <clone> --tip {BUILD}` and explain the remaining mismatch; propose the minimal SCORECARD head edit (banner, Planned heading) that brings it to 0 once a `## Round 58` section exists, tested on a scratch commit."),
 ("X12LegacyCallers", "grep the lane for every caller or doc that names `round56-prereg-check.py`; for each say whether it should now point at the new checker and whether replacing would break an existing receipt/selftest."),
]
for n, t in executors: add(n, "executor", OC, t)
scouts = [
 ("Q01SourcePySetprofile", "Open https://docs.python.org/3/library/sys.html#sys.setprofile live; verify the quote 'it isn't called for each executed line of code (only on call and return' and report anchor, page revision date and access date. Also confirm sys.setprofile call-event semantics for a nested generator."),
 ("Q02SourcePyTrace", "Open https://docs.python.org/3/library/trace.html and https://docs.python.org/3/library/sys.html#sys.monitoring; judge whether either is a stronger or complementary source for execution evidence (with <=25-word located quotes) and name the registry scope you would give it."),
 ("Q03SourceS513Reopen", "Live-fetch https://man7.org/linux/man-pages/man8/ld.so.8.html; locate LD_AUDIT text and quote it (<=25 words); compare to S513's registered reason and flip condition in `corpus/SOURCES.md`; recommend keep-rejected/flip with reasons."),
 ("Q04Considerthese", "Read /home/vgpnk/Projects/shokunin/kama-shokunin/considerthese/ newest file; list still-unimplemented proposals and propose which ONE this round could ground through the lane bar (pointer is not evidence)."),
 ("Q05AssimilationScan", "Read-only: /home/vgpnk/Projects/shokuknow/merge/kama/MERGE-REPORT.md and its knowledge/ listing; report whether any entry fits PROVINCE and the claims (do not run campaign tools; do not adopt)."),
 ("Q06ManifestHistory", "From MANIFEST.json (read-only, fleet HEAD) list every kama closure row r54-r57 with verdict, admitted, spotcheck path; compare to the SCORECARD statements about those closures (grep SCORECARD for 'admitted'); report every other mismatch as an unclaimed finding."),
 ("Q07ProvinceFit", "Check PROVINCE.md: is an execution-bound counter for the battery within operability of local-serving/endpoint-health tools, and does anything sibling-owned (kumitate tooling) overlap? Report contested scope only with evidence."),
 ("Q08RegistryIdScan", "Run the id census: highest S-id in corpus/SOURCES.md, whether S517 is free, and the duplicates warnings list; report exact numbers (read-only)."),
 ("Q09SpotcheckDefects", "Read corpus/lessons/round-57-verifier-spotcheck.md routed defects 1-5; for each say whether this round's claims address it, route it, or leave it, with evidence pointers."),
 ("Q10OldBatteryUse", "Find every committed receipt or doc that depends on the old roster-only checker semantics (round-56/57 measured outputs); report which would change meaning if the new checker replaced it."),
]
for n, t in scouts: add(n, "scout", OC, t)
scribes = [
 ("W01LessonGateDraft", f"Draft (output file only) the `## Gate` section of corpus/lessons/round-58.md: S517 admit with URL, access date 2026-10-27, located quote <=25 words, scope; an S513 disposition from your own live read; ≥1 admit and ≥1 reject recorded for non-author spot-check. Base facts only on sources you open."),
 ("W02MistakesDraft", "Draft the `## Mistakes` table (class | evidence pointer | captured-by | fix) for round 58 from: the round-57 false '(admitted)' wording, the C1 AST-only checker, the S513 unlearned disagreement, the stale-count recurrence (count goes stale after every closure). Each row needs a pointer that resolves."),
 ("W03QualityCriterion", "Draft one append-only QUALITY.md criterion (superseding nothing) taught by the S513 disagreement: how to reject a source for 'overlap' only after checking the flip-condition topics against the overlapping source; cite the lesson and the round-56/57 spotchecks."),
 ("W04ScorecardSection", "Draft the SCORECARD `## Round 58` section (claims table, measured results placeholders marked PENDING, `### Planned (round 59)` heading with a numbered item) in the exact style of `## Round 57`, so tools/round42-selfdesc-reconcile.py reaches 0 mismatches; test the draft in a scratch clone."),
 ("W05LogDraft", "Draft the LOG.md round-58 entry in the style of the round-57 entry; PENDING markers where measurements are not final."),
 ("W06ReportSkeleton", "Draft the report skeleton `.ufo/reports/round-58/kama.md` with the required section order (Work performed, Landed changes, Before to after measurements, Sources & frontier, Trend verdicts, SHONEN four lines) including the Stale-lane line; use PENDING where unknown."),
 ("W07SourcesRowDraft", "Draft the S517 registry row in the 11-column schema (id source kind tier scope anchor teaches status opened recheck used-by) for the sys.setprofile page; no cell may contain a literal pipe; validate against `scripts/sources-census.sh validate --file` on a scratch copy of the registry with the row appended."),
 ("W08KnowledgeEntry", "Draft a short knowledge entry `corpus/knowledge/battery-execution-evidence.md` (source: S517; verified-at; recheck) stating what profile-hook execution evidence does and does not establish (call events only; stubbed subprocess; no leg result semantics). Output file only; <60 lines."),
]
for n, t in scribes: add(n, "scribe", OC, t)
connectors = [
 ("C01CrossLaneNoop", "Scan sibling lanes' tools/ (read-only) for execution-binding or no-op-control patterns (call tracing, import hooks, mutation controls) reusable by kama's checker; return pointers and fit/no-fit."),
 ("C02ClaimSeparability", "Cross-claim scan: could C1's landing change C2's counter output or vice versa (shared files SCORECARD.md, tools/)? Verify with scratch commits of each claim alone."),
 ("C03LedgerPattern", "Look across the fleet MANIFEST and lane SCORECARDs for the same stale-pointer pattern (a lane naming its latest outside closure) and report whether a shared binding check exists or is reusable; read-only."),
]
for n, t in connectors: add(n, "connector", OC, t)
sentinels = [
 ("S01HarnessEscape", "Security-review the harness: craft a battery that escapes the hermetic patches (e.g. open('/path','w'), os.popen, ctypes, importlib of a real subprocess) and show whether the checker run writes outside scratch or executes a command; report only in scratch and delete artifacts."),
 ("S02ScratchAndSecrets", "Sweep the round-58 new files for hardcoded /tmp, credentials, private URLs, op:// references; report exact locations."),
 ("S03WriteScope", "After the wave settles list all untracked/modified paths in the lane and fleet roots (`git status --porcelain` read-only) and flag any outside .ufo/waves/round-58/ that a seat wrote."),
]
for n, t in sentinels: add(n, "sentinel", ["operability"], t)
revengers = [
 ("V01OldCheckerIntent", f"Reverse-engineer why the round-57 checker was AST-only: read its git history (`git log --format=%h\\ %s -- tools/round56-prereg-check.py`), the round-57 prompt/lesson and E03 evidence; state the original intent and whether the execution-bound design preserves it."),
 ("V02RosterOrigin", "Reconstruct from round-56 evidence why the roster has exactly 2 controls and 1 kill and whether `kills == 1 and controls == 2` is a meaningful constant or a magic number in the new checker."),
 ("V03ClosureDriftHistory", "Reconstruct how the SCORECARD calibration row's closure pointer drifted over rounds 52-57 (git log -S on 'latest outside closure'); report each stale instance with commit and the MANIFEST truth at that time."),
]
for n, t in revengers: add(n, "revenger", OC, t)
simplifiers = [
 ("Z01CheckerDeadWeight", "Review the new checker and counters for dead code, duplicated helpers and needless complexity; propose only verified deletions that keep every receipt identical."),
 ("Z02EvidenceFootprint", "Estimate the byte and file footprint of round-58 committed evidence and of the wave's expected outputs; name what is necessary for independent replay and what should not be committed."),
 ("Z03VariantSetMinimality", "Test whether each of the 11 N variants adds distinct coverage: for each, report which checker clause alone rejects it; identify redundant variants without deleting any (the set is frozen)."),
]
for n, t in simplifiers: add(n, "simplifier", OC, t)

assert len(items) == 72, len(items)
spec = {"wave": "kama-r58-w1", "reportDir": ".ufo/waves/round-58/w1/out", "maxLanes": 128,
        "axes": OC, "context": context, "items": items}
(W / "w1").mkdir(parents=True, exist_ok=True)
(W / "w1-spec.json").write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
print(f"wrote {W}/w1-spec.json items={len(items)}")
