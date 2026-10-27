# S3FleetOverlap — sibling-overlap scan (kama round 55)

**Verdict: no contested scope.** None of the three named sibling lanes (kengaku, kumitate, mori) claims round 55's C1 surface (process code-identity auditing of a served model) or C2 surface (citation-disposition checking of self-assessment files); all three route serving-plane/endpoint identity to kama explicitly, and the frozen-counter + do-nothing-control pattern round 55 uses is fleet-wide since hyaku phase-4 — chousa is its closest exemplar, so kama is a participant in a shared pattern, not its unique holder.

Seat: S3FleetOverlap (scout, leaf). Read-only over the fleet. No counters run, no fixtures built, no installs, no services touched.

## 1. What round 55 touched (surface definitions from the freeze)

- **C1 operability 8→8** — `tools/round54-replay-code-audit.py` (sha256 `c81fe971…579af`), re-frozen at base `3a600d2f`. Predicate: a replay of each of the three committed round-48 v5 b11909 receipts holds a server whose executable mappings each match the counter's own download of the release archive (read once, hashed once, two agreeing `/proc/<pid>/mem` passes) or a frozen root-owned host set. Kill battery: control + LD_PRELOAD/env-name + text-flip/code + member-flip/rehash + foreign-ld-audit vector analysis. Newrow source row re-pointed at S511; every git call runs with inherited `GIT_*` stripped. (`.ufo/waves/round-55/preregistration.json` claims.C1; base control `controls/base.c1.out` newrow=0 met=False exit 1; build `measured/c1-build.out` met=True exit 0.)
- **C2 calibration 7→7** — `tools/round54-cited-path-check.py`, re-frozen with a new `superseded` ledger class (live base citation re-pointed to a cited, resolving replacement) plus fixture scenario; BASE deliberately stays at the round-53 tip `0b75a84c` so the drop horizon includes the round-54 re-anchor (a same-tip base let the do-nothing control pass; the §9 pre-freeze check caught it). The counter reads only kama self-assessment files — SCORECARD.md, SHONEN.md, SKILL.md — plus `registry/cited-path-corrections.tsv` and lane/fleet git history. (`.ufo/waves/round-55/preregistration.json` claims.C2, separability, disclosure.)

## 2. Named-sibling scan (the three PROVINCE.md files)

### kengaku-shokunin/PROVINCE.md — no claim; explicit route to kama

- Round-24 "Province map → Adjacent" table: "**kama** — serving plane + endpoint identity — …kama is rostered and owns serving-plane health/detection and endpoint identity; kengaku keeps *interpretation* evidence and never remediates flags" (`PROVINCE.md`, round-24 Adjacent table).
- Round-9 "Refusals": "**Not owned:** the model-serving plane (llama-server flags, slot/batch config) — no lane owns it; escalate to the integrator" — that older "unowned" wording was itself ruled a misroute in the 2026-10-14 fleet audit (below) and superseded by the round-24 route.
- What kengaku keeps is *capability-interpretation* evidence: the round-10 process-level pin (`/proc/1299/cmdline`, 41-token argv, q4_0 KV) "is capability-*interpretation* evidence this lane keeps, but flag-change authority … stays unowned" (round-10/11 report-outs). That is argv/flag interpretation, not code-identity auditing of the served process.
- kengaku's lane-internal citation instruments — `plans/registry_check.py` ("a bounded frozen13-row/35-path literal-reference diagnostic, not semantic source truth", round-28) and `plans/sources_adopt.py` (pre-append adoption gate, round-29 attempt-2) — operate on kengaku's *own* corpus/SOURCES.md registry, and it records "the fleet census … remains the registry's authority". Same pattern family as kama C2, own-files-only. Not a claim on kama's surface.

### kumitate-shokunin/PROVINCE.md — no claim; explicit route to kama

- Adjacent band: "**Local model serving and endpoints → kama.** Prompt and skill craft → kotoba. Research method → chousa." (`PROVINCE.md:29`).
- Domain is OMP task/hub orchestration and ufo-fsd scripts/runtime; nothing in Core/Frontier touches code-identity auditing or citation disposition.

### mori-shokunin/PROVINCE.md — no claim; explicit refusal

- Header refuses: "endpoint and model-serving health (→ kama)". The kama adjacency row: "kama — Owns local model-serving and endpoint health; mori does not infer serving health from host/resource signals."
- Nearest in-family items are own-record bindings, not the C1 surface: round-19 C2 receipts "with current executing-code identity separately recorded" and round-22's "measurement driver binds every executing input to the measured commit" — instrument/receipt identity for mori's own census tools, not process code-identity auditing of a served model. Mori also owns freeze-order verdicts "judging the lane's own claim labels against commit order … calibration of mori's own record, not a fleet ruling" — adjacent, not contested.
- Mori's retention/reconciliation probes (rounds 18/22/23) are own-evidence accounting; no citation-disposition claim over self-assessment files generally.

**Contested-scope candidates: none.** Confidence high — all three files route the surface to kama in writing, and C1's ownership was already fleet-adjudicated (below).

## 3. Adjacent-but-not-contested notes (beyond the three names)

- **kaidoku** (not named in the seat, checked for adjacency): owns "what a binary actually links or loads (ELF reading)" and `carrier-guard.py` "executes *copies* of a binary to observe mode/content changes" (`PROVINCE.md:4,48,57`; `SKILL.md:606`). kengaku's round-38 prior-art block already drew the split: "kaidoku owns what a *binary actually links or loads* (ELF reading)"; kama's replay audit binds served code identity to a released archive digest — a different question, on kama's adjudicated serving plane. Not contested.
- **chousa** owns the generic method: "citation chaining and hop resolution; claim-vs-source verification" (`PROVINCE.md:5`). kama itself records that routing (round-38 note: "The generic pinning *method* … is chousa's ground; the specific re-pin of the two held docs rows is kama's"). kama C2 is an instrument over kama's own self-assessment files, an instance of the fleet-parallel-homed pattern, not a move on chousa's method.
- Historical adjudication: `.ufo/waves/shokunin12h-20261014-p1-audit/members/FleetDeadPathAudit.md` DUP-05 — kama "Explicitly owns local model-serving processes, port 34113, and endpoint identity"; kengaku's "no lane owns it" was a "Direct Contradiction & Misrouting"; fix: "Route endpoint identity to Kama". Repeated in `KengakuRecordConformance.md:119,157` ("kama owns endpoint identity while kengaku refuses serving plane — AGREE (kama province confirms)").

## 4. Fleet scan: counters frozen before data with do-nothing controls

**The pattern is fleet-standard, not unique to kama.** Since hyaku phase-4 (2026-10-23) every lane prompt carries addendum §9: "A target must be one a do-nothing control cannot reach. Freeze one predicate that is the same sentence in the plan, the same condition in the counter's code and the same label in the receipt" and "Before freezing, build the cheapest control that skips the claimed work, score it with the frozen counter, and commit that receipt: if it meets the target, the counter or target is wrong — fix it before data" (`.scratch/goal-20261023-hyaku-24h.md:148-150`; `.ufo/prompts/chousa-round-2*.md` and later).

Concrete holdings (evidence: grep over lane dirs, see `out/S3FleetOverlap/evidence-greps.txt`):

1. **chousa — closest exemplar.** Round-29: counter sha256 `574ffcad…` frozen with `before-do-nothing-v{1,2,3}.json`; 45 control receipts under `.ufo/waves/round-29/controls/`; freeze commit `f9fd6d6c` ("freeze C1 predicate, counter, fixture and do-nothing before receipt (pre-data)"); v1 voided when a label-keyed shortcut hit 130/130. QUALITY criterion 24 "Pre-data control screen" (do-nothing, all-false, junk, no-reader, label/id-keyed controls scored before any data seat). Round-30: `CtlTrivialC1/do-nothing.py` re-scored at each authorized freeze (78/106, receipts `receipt-do-nothing-c1-{run1,h3,v4}.json`).
2. **kengaku — kill-battery precedent.** Round-10: "Independent mutation battery (L2-written pre-grader, executed twice, byte-identical): M0 control exit 0; M1–M3 exit 1 → 4/4, 100% kill rate" (`.ufo/reports/round-10/kengaku.md:38`); round-38+ probes with disclosed control-time ordering.
3. **kumitate** rounds 63/64: control set 14→75 cases after wave-1 attacks, disclosed in `controls/CHANGES-AFTER-FREEZE.md` (`.ufo/l0-questions.md:167,170`); `gate-mutants.mjs` is a 43-mutant gate battery.
4. **tameshi** `tools/mutate-and-run.sh` — fleet exit-graded mutation runner; kengaku round-37/38 names tameshi's method and kumitate's gate-mutants as *the* precedents for mutation-testing a lane's own gate.
5. **souji** rounds 19–22: `preregistration.txt` frozen before data with committed before/after receipts.
6. **Do-nothing controls that caught bad targets (the pattern working):** kaidoku r29 (trivial baseline 152/152 → rejected, `l0-questions.md:114`); kake r34 (no-parse replay and junk rows met both counters, `:119`); tsukuroi r30/r31 (sourceless fixture 10/10; scripted non-reader 8/8, `:120`); chousa r29-v1 (label-keyed 130/130 voided v1).
7. **Env-injection falsifier vectors — shared technique family.** chousa r37: "unprivileged LD_PRELOAD moved verdicts 4/7 (forge) and 3/7 (false stale)" — C1 claim text killed (`.ufo/reports/round-37/chousa.md:77-78,154`); chousa r41: gate child unsets `LD_PRELOAD`/`LD_LIBRARY_PATH` with a frozen 14-name pin table (round-41 report:9,15). tsukuroi r30: "git-env leak probe 17/30 → 0/33; LD_PRELOAD and other channels owed" (`.ufo/waves/hyaku/PHASE4.md:71`, tsukuroi round-30 report:91-92,174-175). kama round-54 battery already records `LD_PRELOAD`/`DYLD_INSERT_LIBRARIES` as a failure and strips `GIT_*` on every git call. Round 55's kill battery (control + LD_PRELOAD/envnames + text-flip + member-flip/rehash + foreign ld-audit) is the same family, applied to the served-code replay.

**What kama holds uniquely:** the *instrument* — no other lane replays a served llama-server or audits served-process code identity against its own archive download (kengaku r31: "Sibling lanes hold no competing claim on this surface"). The *freeze discipline* around it (base/do-nothing controls committed beside the preregistration, kill battery) is borrowed from the fleet standard. So: pattern shared, instrument unique, scope uncontested.

## 5. Commands and evidence trail

- Reads: `kengaku-shokunin/PROVINCE.md` (648 lines), `kumitate-shokunin/PROVINCE.md`, `mori-shokunin/PROVINCE.md` (476 lines), `kama-shokunin/PROVINCE.md`, `chousa-shokunin/PROVINCE.md`, `kaidoku-shokunin/PROVINCE.md` (selected sections), `kama-shokunin/.ufo/waves/round-55/preregistration.json`.
- Greps (pattern → key hits): `do-nothing|preregistration|kill battery` fleet-wide; `code-identity|cited-path|superseded` fleet-wide; `LD_PRELOAD|ld.audit` fleet-wide; `do-nothing` restricted to eleven lane dirs; `frozen before data|frozen counter`; `self-assessment`; `endpoint identity|serving-plane health`; `kama|identity|serving` in the kengaku/kumitate province tails. Full hit list: `out/S3FleetOverlap/evidence-greps.txt`.
- No counter executed (seat is a scout; both counters are frozen and read-only to this seat). No files outside this report and its out directory were written. Scratch `/fast/scratch/hyaku/kama-r55/w1/S3FleetOverlap` removed after writing.

No defects found in round-55 surfaces by this scan (nothing to propose fixes for). No blockers.
