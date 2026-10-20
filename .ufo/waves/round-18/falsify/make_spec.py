#!/usr/bin/env python3
"""Round-18 fresh falsifiers; each item attacks a concrete delivered surface."""
import json, pathlib, subprocess, collections
L='/home/vgpnk/Projects/shokunin/kama-shokunin'
W=L+'/.ufo/waves/round-18'
REV=subprocess.check_output(['git','-C',L,'rev-parse','master'],text=True).strip()
G=pathlib.Path('/home/vgpnk/.agents/skills/godspeed/directive.md').read_text()
HEAD='/skill:godspeed\n'+G.rstrip()+'\n\n'
context=f'''# Goal
kama round 18 FALSIFY wave. Attack delivered code at pushed lane master `{REV}`. Read {L}/corpus/lessons/round-18.md, SCORECARD.md §Round 18, QUALITY.md KQ23/KQ24 and official raw runs under {W}/runs/. L1 integrates and owns admission; your advice is NOT an outside non-author judgment.
Claims: C1 operability (8→8) — v3 live lifecycle receipt, separate not-evaluated (tool2/gate3) from failed (1), six retained targeted controls, schema floor, exact argv, all recorded loading transitions, tcp6 child ownership, BaseException receipts. Sourced on S048/S050/S051/S054. C2 calibration (7→7, lowest) — bounded named-survivor statement→mutant→detector repair over check.py, fault-controls, append-only and provenance; no general immunity claim. C1 production files: tools/kama-llamacpp-live.py and tests/llamacpp-live/*.py plus round18/c1/. C2: tests/probe-verdicts/*.py, tools/sources-append-only.py, round18/dispatch-provenance.py and round18/c2/. Probe and nine matrix JSON unchanged.
# Contract
All reads/commands/writes use ABSOLUTE paths. Every `Report:` trailer path is relative to {L} — write it at {L}/<that path>. Write ONLY your own report, plus scratch in /tmp/kama-r18-falsify-<Seat> (remove before finish). No edits to production, fleet, sibling repos, frozen evidence or old lessons. No jj commands; no git writes in {L}; never touch lane index/jj/fleet state. Runtime/gate checks run ONLY in your separate clone: `git clone -q {L} /tmp/kama-r18-falsify-<Seat>` then `git -C <clone> switch -q -c seat/<Seat> {REV}`. Copy nothing back except your report and the exact experiment source inside that report. Never run the official counting commands against the live lane; your clone contains committed code and evidence.
No ports 8080/34113 or any registered consumer port. Loopback-only ephemeral listeners, one server per seat at a time; teardown process group before finish and prove no seat-owned listener remains. Installed b11755 binary/model are read-only; no systemd/global config/service changes. Never read/list/search .ufo/interactive-sessions, ~/.omp except RULES.md, ~/.config, credentials, session/history/transcript stores; recursive grep excludes interactive-sessions,.git,.jj. Never dump environment values.
Report FIRST line exactly VERDICT: confirm|partial|refute|n/a — short reason. Every finding needs path:line or executed command/stdout/stderr/exit, hashes, limits and installs. A runtime timeout, own-fault, invalid pristine baseline or missing mutant site is INCONCLUSIVE, not a kill. Survived/equivalent/site_missing remain visible. Targeted mutation kills need a green pristine, red mutation attributable to the targeted assertion, and byte-exact restoration. Fresh mutants are a separate denominator from the named round17 set.
Operator tooling authorization (2026-10-19): install/upgrade helpful tools after reading /home/vgpnk/.omp/agent/RULES.md; record tool/version/channel/reason. ALL pacman transactions PAUSED host-wide; only uv tool/npx/official binary under ~/.local/bin, never -Sy/-Syu/-U/-R, downgrade or host-service restart. When pause lifts, `pacman -Sp --print-format '%n %v' <pkgs>` first and proceed only if no package listed is already installed.
Leaf only (executor may one read-only labrat); never agent://all, never ask, no model parameters. L1 is planner; connector scans overlap. No tests/build/formatters except the exact bounded experiments assigned in your item.
'''
items=[]
def add(n,r,t): items.append({'name':n,'role':r,'prompt':HEAD+t})
# Dedicated rerunners, each owns a different empirical cell/family.
add('RerunC1Frozen','executor',f'''# Attack: C1 before arm
In your clone run the exact frozen-arm counting invocation from {W}/runs/ (read c1/measure.py --help). Reproduce frozen tool+gate under current controls; separately run frozen round17 controls on frozen pair and compare with round17 committed 6 accepted-bad/1 inconclusive. Record input digests, per-control classifications, exit and differences. Do not call a schema/argparse own-fault a targeted rejection.''')
add('RerunC1Current','executor',f'''# Attack: C1 after arm
In your clone rerun current tests/llamacpp-live/controls.py with current tool/gate (read --help and official raw invocation under {W}/runs/). Check every targeted id and gate-flip result; zero-loading classified tool2/gate3, mapped-good accepted, internal faults exactly2. Compare output excluding timing with L1's committed output.''')
add('RerunC2H','executor',f'''# Attack: C2 H family
In clone rerun c2/survivors.py family a using --help, compare every named H mutant outcome and baseline with {W}/runs/. Confirm original H edit strings match round17 MutC1Preregistered reports, no timeout/own-fault counted killed, all matrix/probe bytes pinned. Include commands and exact exits.''')
add('RerunC2Self','executor',f'''# Attack: C2 detector-self families
In clone rerun c2/survivors.py families b,c,d (use --help); compare F0/cache/target self-mutants, opened/blank-line mutants and refused0→82 input with {W}/runs/. Check full diagnostics vs decision tuples and distinguish parser own-fault from targeted selftest detection.''')
add('LiveV3','executor',f'''# Attack: real producer/gate compatibility
In clone run current live tool three times against /home/vgpnk/.local/opt/llama-b11755/llama-server and /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d, free loopback ports. Gate with --require-schema v3 and all four pins. Record loading observations/checks/outcome/exits per run. Compare fake K0 captures with real surfaces (semantic bodies, not timestamps); teardown proof. A legitimate no-loading outcome is NOT-EVALUATED, never a pass.''')
reviews={
'GateNullLicense':'Gate: forge null on a non-loading check; null with wrong reason/evaluated; observed bad503 laundered to null; real failure+null. Require INVALID, preserve legitimate no-loading NOT-EVALUATED. Run cloned selftest and synthetic receipts.',
'GateSchemaFloor':'Gate: declare v1/v2 under --require-schema v3; test each floor and unknown schema. Show current v3 cannot escape by merely self-declaring older schema when caller requires v3; report default permissive boundary honestly.',
'GateArgv':'Gate: insert api-key/duplicate host/duplicate port/short alias/ctx-size before required suffix, not only at argv end. Require exact equality rejects each. Test raw relative model.arg remains valid on a genuine receipt.',
'GateLoadingTransitions':'Gate: mutate only one /v1/models 503 transition body while retained bodies stay exact; repeats/sha/over-cap/drop257 coverage. Test each corruption independently, retain green pristine.',
'GateBinding':'Gate: mutate source_binding url/path/commit/span_text/span_sha/file_sha/line range independently. Verify full tools/server URL (L1 integration bug) and distinguish internal consistency from upstream authentication.',
'GateInternalFault':'Gate: internal_fault/setup_error mismatch, forged successful outcome with an internal fault, false-check+null precedence. Read producer BaseException structure; identify receipt-less paths still reachable.',
'GateLegacy':'Run historical round16 v1 and round17 v2 receipts against frozen/current gates with identical four pins; require same exits/VALID text; frozen-probe mismatch negative control stays INVALID. Test schema floor explicitly intentional.',
'GateModelsStatus':'Attack RevTriStateDesign fix: no-loading receipt with captures.models.status503 but valid ids/owners. Require INVALID and targeted model status; mutate tool model-status check and see controls/selftest catch it.',
'GateCaptureHashes':'Gate v3 health/models bodies vs body_sha256, capture statuses/error fields, optional summary/expected_model_id null. Determine ungraded leaves remaining, with concrete forgeries not absence-only assertions.',
'GateLoadingCounts':'Gate: loading_observed / total_503_responses / repeats / dropped mismatch and health-only503 vs models503. Does null license consistently use models observations? Derive producer vs gate agreement, no false positives.',
'GateClaimFlags':'Gate: flip passed/evaluated/outcome across all check ids. Does a raw failing body plus passed:true get rejected for re-derived predicate rather than unrelated schema error? Table with check id→rejection.',
'ToolFaultPaths':'Tool in clone: inject KeyboardInterrupt/SystemExit/RuntimeError into readiness, teardown, rehash and epilogue output handling. Require receipt+setup-error/2 where output writable and cleanup. No blanket help/usage conversion. Keep signal handling prompt.',
'CheckDecoder':'check.py malformed probe nested JSON, 5000-digit int, nonUTF8 and valid successor. Require parseable failed row with error and continued next row, no traceback. Verify existing exit table unchanged.',
'CheckTimeout':'check.py timeout wrapper spawns sleep in same PGID. Prove timeout row and child killed. Also detach a child in separate session safely then reap it; report containment limit rather than claim full process-tree kill.',
'FaultF0':'fault-controls: attack F0 bypass (remove enforcement); bad identity must prevent scoring. Empty F0 row list/fault list must not pass vacuously. Run selftest and a forged check instrument independently.',
'FaultCache':'fault-controls: shared F6 cache mutation; prove per-row cache identity changes the graded result, not only diagnostics. Review H3 non-GET and H6 no-request variants for confounding target failure.',
'FaultTarget':'fault-controls: drop targeted conjunct requirement, feed off-target-only failing check row. Require selftest catches exact target loss; exit2 own-fault never counted detected.',
'AppendCells':'sources-append-only: mutate each immutable cell compare individually (opened/kind/tier/scope/anchor/source/teaches); run own selftest, positive allowed-cell cases. How does comparison invariant fail vs actual violation?',
'AppendParser':'sources-append-only: post-blank rows, later table, duplicate/missing header, column reorder, duplicate id, heading boundary, malformed row. Require no silent loss. Legitimate historical sources all still parse.',
'ProvenanceRefusal':'round18 provenance: raw round17 82-refusal and round18 95-refusal inputs, spawned75 header/rows, mixed/duplicate labels. Correct count and method, never numeric job-cap100 mistaken as refusal count.',
'CounterC1':'Attack c1/measure.py itself: frozen-source binding, interpreter/probe/registry pins, per-cell raw output retention, classifications, exit predicates; falsify accepted_bad or uncontrolled counters with a synthetic child output in clone.',
'CounterC2':'Attack c2/survivors.py itself: baseline guard, required flags on frozen detector, expected before vector, site_missing/equivalent/inconclusive denominator, timeout handling, hashes and retained intermediate outputs. Any own-fault counted kill is a defect.',
'Separability':'C1/C2 causally separate? Run bounded 2x2 revert/copy checks in sandbox: C1 controls with C2 files frozen/current; C2 detector subset with C1 files frozen/current. Shared probe/matrix unchanged. Distinguish provenance guard dependency from claim behavior.',
'PriorKills':'C2 no-harm: rerun original F1-F8 fault controls and round17 M1-M9 mutant full-detector arm in clone (read commands). New H fixes must not lose old kills. Report any changed prior verdict, timeout or site_missing honestly.'
}
for n,t in reviews.items(): add(n,'reviewer','# Attack: '+t+'\nUse clone only; exact script/command and outputs in your Report.')
scouts={
'ReopenS048':'Open S048 kernel v7.2 URL and in6.h. Compare retained raw pins, locate four-word printer and type. Re-derive ::1/mapped127 hex with real ephemeral bind if needed; verify knowledge entry source correspondence.',
'ReopenS049':'Open S049 proc_net_tcp.rst; verify narrower teaching/deprecation and negative IPv6-format scope, Gate quote/location/access, no unsupported state-code attribution.',
'ReopenS050':'Open S050 RFC4291; verify ::1 exact /128 and mapped layout/prefix104, knowledge entry and Gate quotes. Check no literal pipe corrupts SOURCES cells.',
'ReopenS051':'Open Python3.14 exceptions S051 actual redirect/canonical title; verify BaseException hierarchy and tool receipt rationale, no Python3.15 provenance.',
'ReopenS052':'Open pytest exit codes S052; verify empty vs failed distinct, page version unknown and lane numbering not falsely attributed. Check Gate quote.',
'ReopenS053':'Open official Automake1.19 manual/tar member S053; verify rejected-as-basis reason and quote, not recorded as unopened or mined. Never install pacman packages.',
'ReopenS054':'Open pinned common/arg.cpp S054; verify repeated flag warning/host clear, exact source digest. Last-wins claim scoped, --api-key append caveat not suppressed.',
'ReopenS047':'Open S047 pinned server-queue.cpp and server.cpp. Review newly supplied Gate as necessary condition, not sufficient termination. Check KQ23 reset/read accounting and S043 README correction.',
'KnowledgeOwnership':'Review new knowledge/loopback-listener-ownership.md against original coverage map: genuinely new mechanism? Every claim grounded, network namespace/race limits, no big-endian proof falsely claimed.',
'CorpusCensus':'Run source census validator/census on committed clone tree and compare before/end counts. Source append-only every consecutive source-changing commit pair; added-then-edited rows must not hide.',
'StaleDocs':'Sweep current-tense docs for v2/no503-fails/BaseException-escapes/14-case-selftest/Python3 path. Historical text may remain only with resolvable appended supersession; list uncorrected live statements.',
'MatrixProbeBytes':'Recompute nine-file72-row matrix digest and probe SHA at round start and current commit. All must equal original. No JSON row, probe comment or alias behavior silently repinned.',
'FrozenManifest':'Verify every frozen source byte against e75cf680 git blob, manifest path mapping/SHA256SUMS/prior_exposure. Old artifacts not treated heldout. Check frozen pycache/temp files excluded/removed.',
'WaveProvenance':'Verify 95 refusal zero-spawn, refit75 payload validation policy hash/band/taskCall canonical SHA, registry75 assignments, terminal/dead counts. No missing refused attempts or fabricated answering model.',
'ShonenState':'Review four SHONEN boxes and report marks: no [x] without named independent non-author; live fixture not consumer reconciliation, no promotion implied.',
'PortsFootprint':'Audit assigned scripts/receipts for loopback, registered-port refusals and cleanup; read ss only, no services changed. Installs disclosed incl. retained preexisting archive/model and no current pacman use.'
}
for n,t in scouts.items(): add(n,'scout','# Attack: '+t+'\nRead-only except own Report; bounded experiment only if explicitly named.')
critics={
'C1Admission':'Judge C1 declared before→after and no-harm honestly from code/runs. Null is not acceptance; coverage counts cannot conflate schema failures with targeted controls. Numeric axis remains8.',
'C2Admission':'Judge C2 as calibration by sentence→mutant→detector ledger. Does each statement match exercised evidence? Lowest axis7 obligation and causal separation. Bound counts, no mastery score inflation.',
'NoHarm':'Adversarial no-trade review over all axes. Legacy gate outputs, process safety, old detector kills, parser historical cases and docs unchanged/corrected. A gain cannot net out a regression.',
'TrendVerdicts':'One verdict expansion/quality/discernment, no scalar. New procfs entry uncovered ground; KQ23 grounded in outside R2; no lane seat substitutes independent non-author sample. Correct round17 outside discernment improved.',
'MistakesFailCapable':'Review each round18 Mistakes row and routed R1-R7: class/evidence/captured-by/fix shown able to fail. Reject merely promised tests or reject-everything KQ23. Track seven earlier dead attacks now covered or not.',
'SourcedSupport':'Verify C1 actually depends on opened S048/S050/S051/S054, not decorative pytest numbering. Check new rows Gate/access/quotes and no immutable old-cell changes.',
'SurvivorUniverse':'Named round17 universe vs fresh wave2 mutants: separate denominators; site_missing/equivalent/inconclusive never silently removed. Original frozen witnesses and prior kills retained.',
'ScoreCapabilities':'Review SCORECARD canonical state/current row, capability unchanged, stagnation window2/4, other axis no-harm, measured commit and commands. New knowledge not an unearned capability.'
}
for n,t in critics.items(): add(n,'critic','# Attack: '+t)
for n,t in {
'FreshGate':'Preregister and run 4 fresh non-equivalent v3 gate mutants NOT identical to existing selftest cases; each has off-suite distinguishing receipt, exact source site, green pristine and targeted kill/survival. Try status/counter/schema-boundary weaknesses, no production edits.',
'FreshFault':'Preregister and run 4 fresh fault-controls/check.py detector mutants beyond H1-H7 and named F0/cache/target. Off-suite witness required; test current detector, distinguish equivalent/site_missing/inconclusive. State full universe.',
'FreshAppend':'Preregister and run 4 fresh append-only parser/provenance mutants beyond opened/blank-line/refusal parser. Run selftest + distinguishing fixture; never count an own-fault as targeted kill.',
'FreshControls':'Preregister and run 4 fresh live-control classifier mutants beyond dropped gate-flip/K0 exit/K6 exact2. Try null laundering/fail precedence/target attribution/mapped-good. Run selftest and selected controls in clone, report survivors honestly.'
}.items(): add(n,'mutation-tester','# Fresh mutation attack: '+t)
for n,t in {
'ConnectKagi':'Check exact argv remains launch-identity verification, not claimed secret scanning/auth health; no credential values copied. Re-read kagi SKILL/corpus README only and advise handoff.',
'ConnectKumitate':'Check refused-count correction and producer-shape offer to kumitate; no fleet tooling ownership absorption. Re-read kumitate SKILL/corpus README only.',
'ConnectTameshi':'Compare mutation denominator/targeted-kill/equivalent rules with tameshi SKILL/corpus README only; report disagreements, do not alter sibling.',
'ConnectTsukuroi':'Review host footprint/pacman pause/preexisting install boundary vs tsukuroi SKILL/corpus README only; no live boot/update commands.'
}.items(): add(n,'connector','# Cross-axis overlap: '+t)
for n,t in {
'ReportWork':'Draft evidence-backed Work performed/Landed changes report bullets from actual committed code/LOG. No fabricated hashes; use observed branch commit.',
'ReportNumbers':'Draft Before→after table from raw c1/c2 outputs, commands and input hashes. Audit every number and missing denominator; do not fill absent data by inference.',
'ReportSources':'Draft Sources & frontier census before/end, tiers/status/old→new cells, frontier moved; every new row Gate and source opening. Source census shape is not admission.',
'ReportWaves':'Draft wave seat totals/role mix/dead/error texts/95 refused->75 refit, capacity checks and planner mapping from committed provenance. No inference of actual answering model.',
'ReportTrends':'Draft three trend verdict rationales and SHONEN [~] evidence, preserving outside-review distinction. Use critics reports and LEARNING definitions.',
'LessonResiduals':'Draft lesson falsify dispositions: confirmed findings, repaired vs retained debt with exact report references. Never say all addressed if a fresh mutant survives.',
'ReportHandoff':'Draft report Stale-lane line, installs none-or-actual, existing two L0 questions, inherited state, future planned item. Check no new duplicate operator question was filed.'
}.items(): add(n,'scribe','# Evidence draft only (write in your Report): '+t)
for n,t in {
'SafetyDelivered':'Review actual tool/controls safety invariants, process-group kill identity, IPv6-loopback-only, refused ports, env allowlist, registry fail-closed and forged argv kept data. Bounded selected fake run permitted in clone.',
'PrivacyScope':'Audit round18 diff/evidence for privacy boundaries, env values/credentials/session excerpts, fleet-root misroots, new artifacts>10MiB. No opening forbidden stores; inspect only lane round18 outputs.'
}.items(): add(n,'sentinel','# Security attack: '+t)
for n,t in {
'RevGateDelta':'Trace frozen→current gate changes; identify every v1/v2 branch whose semantics may have shifted accidentally. Check code against recorded legacy oracle.',
'RevToolDelta':'Trace frozen→current tool exit paths, initial setup failures/digest mismatch/help/signal/teardown/emit; match docstring and receipt guarantees, find any dead return or double teardown.',
'RevFCDelta':'Trace frozen→current fault-control variant mapping to each named H/F survivor; ensure targeted failure not a confound from new check.py crash fix.',
'RevCriterion':'Reconstruct M8→KQ23 lesson and reset-omission positive/negative controls. Are claims newly weakened appropriately, or hiding S047 sufficiency overclaim?'
}.items(): add(n,'revenger','# Reverse intent review: '+t)
for n,t in {
'SimplifyC1':'Review new live tool/gate/control code for avoidable duplication/dead paths; suggest only cuts preserving measured bytes/behavior (no edits).',
'SimplifyC2':'Review counters and detector-self machinery for unnecessary abstraction/circular assertions; suggest simplification with behavioral evidence, no code edits.'
}.items(): add(n,'simplifier','# Simplification review: '+t)
assert 64<=len(items)<=100,len(items)
spec={'context':context,'reportDir':'.ufo/waves/round-18/falsify/advice','maxLanes':100,'items':items}
p=pathlib.Path(W+'/falsify/spec.json');p.write_text(json.dumps(spec,indent=1,ensure_ascii=False)+'\n')
print('revision',REV,'seats',len(items),'roles',dict(collections.Counter(i['role'] for i in items)))
