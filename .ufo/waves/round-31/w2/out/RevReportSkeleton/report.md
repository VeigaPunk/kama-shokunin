# RevReportSkeleton — report-conformance checklist for `.ufo/reports/round-31/kama.md`

```RESULTS
Audit snapshot: lane tip moved mid-audit (bda324bb → addeb57); final state at addeb57c5d717785a94105a2e36cc8a76940fb6c, jj `local=remote`, `ahead=0` (pushed). `git status` shows only `??` untracked paths — every worktree file I read equals committed bytes at HEAD. Full verbatim capture: receipts.txt (same directory). Commands:

$ git rev-parse HEAD                                    [exit=0]  addeb57c5d717785a94105a2e36cc8a76940fb6c
$ git log --format='%h %ci %s' -8                        [exit=0]  tail: addeb57 C3 row+receipt | bda324b C3 freeze | 382d11b SOURCES repair | d45f947 LOG+lesson | b4f3edc SCORECARD | 54c6f4f remap | 3b1e84f surface | 0e6f8ed freeze
$ git status --porcelain                                 [exit=0]  ?? c1/c1-bda324bb.json ?? c1/c1-382d11b2.json ?? c2/c2-382d11b2.json ?? c2/c2-bda324bb.json ?? c3/gate-after-final.out ?? c3/gate-mutation-dropped-row.out ?? w2/out/ ?? w2/validate.err ?? w2/validate.json  (earlier snapshot also listed c1/c1-382d11b2.json)
$ git ls-tree -r HEAD --name-only -- .ufo/waves/round-31/c3/  [exit=0]  gate-after-progress.out | gate-before.out | r29-at-tip.json | r29-counter-sha256.txt
$ git ls-tree HEAD --name-only -- .ufo/waves/round-31/w1/   [exit=0]  items | out   (no spec.json/plan.json/taskCall.json)
$ git ls-tree HEAD --name-only -- .ufo/waves/round-31/w2/   [exit=0]  census-validate-start.out | plan.json | spec.json | taskCall.json
$ git show --stat addeb57                                [exit=0]  SKILL.md +1 | c3/gate-after-progress.out +7 | c3/r29-at-tip.json +125
$ ls /home/vgpnk/Projects/shokunin/.ufo/reports/round-31/ [exit=0]  chousa kaidoku kake kotodama mori tameshi tsukuroi — kama.md ABSENT
$ grep -n 'bda324b\|addeb57\|attempt 2' LOG.md            [exit=0]  only r18/r25/r29 attempt-2 headers; no round-31 attempt-2 entry
$ grep -n 'gate-registry-check\|capabilities' SCORECARD.md [exit=0] last: `### capabilities: append — none` (line 1607); no C3 row
$ tail -n 6 c3/gate-before.out                           [exit=0]  `unregistered .ufo/waves/round-29/count-c1.py` `registered 8 unregistered 1` `exit=1`
$ tail -n 6 c3/gate-after-progress.out (committed)       [exit=0]  `registered 9 unregistered 0` `exit=0` + `at bda324bb … unregistered 1 exit=1`
$ tail -n 6 c3/gate-after-final.out (UNTRACKED)          [exit=0]  `registered 9 unregistered 0` `exit=0`
$ tail -n 6 c3/gate-mutation-dropped-row.out (UNTRACKED) [exit=0]  `unregistered .ufo/waves/round-29/count-c1.py` `registered 8 unregistered 1` `exit=1`
$ tail -n 6 c3/r29-counter-sha256.txt                    [exit=0]  `fe11d599…7383  .ufo/waves/round-29/count-c1.py`
$ python3 … c3/r29-at-tip.json                           [exit=0]  `met True tip bda324bbc5c1… statements 69 mismatched_at_base 11 unresolved 0`
$ python3 … c1/c1-382d11b2.json (UNTRACKED)              [exit=0]  `registered 18 counted 17 target 12 met True not-counted ['K31-10']`
$ python3 … c1/c1-bda324bb.json (UNTRACKED)              [exit=0]  `registered 18 counted 17 target 12 met True not-counted ['K31-10']`
$ python3 … c2/c2-382d11b2.json (UNTRACKED)              [exit=0]  `rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip 382d11b2107d`
$ python3 … c2/c2-bda324bb.json (UNTRACKED)              [exit=0]  `… met False tip bda324bbc5c1`
$ python3 … c1/c1-54c6f4fe.json (committed)              [exit=0]  `registered 18 counted 17 target 12 met True not-counted ['K31-10']`
$ python3 … c2/c2-b4f3edc0.json (committed)              [exit=0]  `rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip b4f3edc0bfc1`
$ tail -n 5 census-start.out                             [exit=0]  `kama E12 S187…S191 row outside Registry section`
$ tail -n 5 census-end.out                               [exit=0]  `kama ok …corpus/SOURCES.md` (after W04 dup-url warnings)
$ tail -n 5 w2/census-validate-start.out                 [exit=0]  `kama ok …corpus/SOURCES.md`
$ tail -n 4 c1/hold-r30.out                              [exit=0]  `… unresolved 0 met True tip 0e6f8ed6891c`
$ tail -n 6 controls/RefRepair/receipt.txt               [exit=0]  `rows 28 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 3 unresolved 3 append_only True met False … ARM-FAILED-THE-TARGET`
$ grep -n 'round-29/count-c1' SKILL.md                   [exit=0]  line 1291 row committed at addeb57 (sha256 `fe11d599…7383`, cites `c3/r29-at-tip.json`)
$ python3 … w2/taskCall.json                             [exit=0]  `w2 tasks: 44`
$ ls corpus/knowledge/                                   [exit=0]  includes chat-adapter-outcomes.md, cross-lane-scope.md (verified `git ls-tree` = present)
$ grep -n 'KQ41\|chat-adapter' corpus/QUALITY.md         [exit=0]  KQ41 row at :303
$ grep -n 'SHONEN\|Marker rule\|Sources & frontier\|Trend verdicts' .ufo/prompts/kama-round-31.md  [exit=0]  sections at L104-119; marker rule L121-125 exempts Sources&frontier + Trend verdicts
$ scripts/hyaku/jj-lane.sh state <lane>                  [exit=0]  `branch=master local=addeb57… remote=addeb57… ahead=0 behind=0 head=detached tracked=0 untracked=9`
$ git merge-base --is-ancestor 382d11b2… HEAD            [exit=0]  dispatch tip is ancestor of HEAD
$ existence checks (git ls-tree HEAD)                    [exit=0]  chat-adapter-outcomes.md=1, round-30-verifier-spotcheck.md=1, c2/c2-tip.json=0, w1/spec.json=0
Tool installs: none. No lane tracked file edited; no lane git/jj write issued.
```

FINDING: Skeleton can be drafted for five of six required sections from committed bytes at `addeb57`; **SHONEN is the only section that CANNOT be filled at `[x]` from committed evidence** (no named non-author verifier exists for round 31 — draftable only as `[~]`/`[ ]`). Committed-evidence gaps to disclose, not paper over: (a) `LOG.md` has no round-31 attempt-2 entry, so `bda324b`/`addeb57` cannot be tied to a LOG entry in Landed changes; (b) `SCORECARD.md` has no C3 row (still `capabilities: append — none`) and its C2 measured-commit cell points at absent `.ufo/waves/round-31/c2/c2-tip.json`; (c) C3's mutation-control receipt and the clean final gate receipt are untracked; (d) all wave-2 seat outputs are untracked and wave-1 spec/plan/taskCall were never committed.

LIMITS: I did not re-run either frozen counter, the gate, or the census — every "after" number above is read from stored receipts, not re-derived. `gate-after-progress.out` is a composite note (worktree run + `at bda324bb` run), not a single `tools/gate-registry-check.py --rev addeb57` invocation; the `--rev`-keyed committed receipt does not exist. The tip may move again before the report is written; "committed today" means `addeb57`. `w2/validate.json`/`validate.err` and `w2/out/` are untracked by design of the wave flow — seats commit under their own directories per the validator contract; whether the L1 commits `w2/out/` wholesale is its call. Missing wave-1 spec/plan may be deliberate (w1 predates the spec-commit convention in this repo); flagged, not judged. The report file itself does not yet exist — this checklist is advisory to the L1, not a verdict on the round.

## Skeleton checklist — `/home/vgpnk/Projects/shokunin/.ufo/reports/round-31/kama.md`

Order fixed by `/home/vgpnk/Projects/shokunin/.ufo/prompts/kama-round-31.md` §4 (L104–119).

### 1. Work performed — FILLABLE
- [ ] Declares C1 (depth), C2 (calibration), C3 (operability, capability acquisition) + axes
- Committed artifacts:
  - `.ufo/waves/round-31/preregistration.json`
  - `.ufo/waves/round-31/preregistration-c3.json`
  - `.ufo/waves/round-31/count-c1.py`, `.ufo/waves/round-31/count-c2.py`
  - `.ufo/waves/round-31/sources/SNAPSHOT.json`, `.ufo/waves/round-31/sources/llama.cpp-704366d/*` (7 files)
  - `.ufo/waves/round-31/before/pilot-c1.json`, `.ufo/waves/round-31/before/c2-base.out`
  - `.ufo/waves/round-31/controls/Ctl*/`, `.ufo/waves/round-31/controls/RefRepair/` (13 arm dirs)
  - `.ufo/waves/round-31/w1/items/*.md`, `.ufo/waves/round-31/w1/out/**`, `.ufo/waves/round-31/w1/out/swarm-registry.json`
  - `.ufo/waves/round-31/w2/spec.json`, `plan.json`, `taskCall.json`, `census-validate-start.out`
  - `.ufo/waves/round-31/census-start.out`, `census-end.out`
  - `SKILL.md` (§Round-31 chat-completions parameter outcomes; §Round-31 instrument registry rows)
  - `registry/chat-param-outcomes-r31.json`
  - `corpus/knowledge/chat-adapter-outcomes.md`
  - `corpus/QUALITY.md` (KQ41)
  - `corpus/SOURCES.md` (S180–S191 inside `## Registry`)
  - `corpus/lessons/round-31.md`
  - `SCORECARD.md` (§Round 31, §Round 31 corrections, §Planned round 32)
  - `LOG.md` (§round 31, line ~1930)
  - `tools/gate-registry-check.py`
- CANNOT-FILL items (disclose): no `LOG.md` entry names attempt 2 / `bda324b` / `addeb57`; no `SCORECARD.md` C3 row; `w2/out/` seat outputs untracked; `w1` spec/plan/taskCall never committed (shape narratable only from `w1/items/`, `w1/out/swarm-registry.json`).

### 2. Landed changes — FILLABLE (two rows lack their required LOG anchor)
- Committed artifacts:
  - `LOG.md` §round 31
  - `git log` rows: `0e6f8ed` `3b1e84f` `54c6f4f` `b4f3edc` `d45f947` `382d11b` `bda324b` `addeb57` (committer dates in receipts.txt)
  - `SCORECARD.md` §Round 31
- CANNOT-FILL items (disclose): `bda324b` and `addeb57` rows cannot cite a LOG.md entry — none exists; per contract every landed change is "tied to a LOG.md entry" so these two rows are structurally incomplete until `LOG.md` grows the attempt-2 entry.

### 3. Before → after measurements — FILLABLE
- Committed artifacts:
  - C1 before: `.ufo/waves/round-31/before/pilot-c1.json` (+ `preregistration.json` C1.before_command, exit 2 at `07794a4d`)
  - C1 after: `.ufo/waves/round-31/c1/c1-54c6f4fe.json` (`met True`, not admitted — pair with `.ufo/waves/round-31/w1/out/CriticClaimSize/c1-noop.json`, `w1/out/RevCounterFair/f1-receipt.json`, `f2-receipt.json`)
  - C2 before: `.ufo/waves/round-31/before/c2-base.out`
  - C2 after: `.ufo/waves/round-31/c2/c2-b4f3edc0.json` (`met False`; pair with `.ufo/waves/round-31/controls/RefRepair/receipt.txt`)
  - C3 before: `.ufo/waves/round-31/c3/gate-before.out`, `.ufo/waves/round-31/c3/r29-counter-sha256.txt`
  - C3 after: `.ufo/waves/round-31/c3/gate-after-progress.out`, `.ufo/waves/round-31/c3/r29-at-tip.json`
  - Hold: `.ufo/waves/round-31/c1/hold-r30.out`
- CANNOT-FILL items (disclose): C3's frozen predicate pieces not yet committed — `c3/gate-after-final.out` and `c3/gate-mutation-dropped-row.out` (mutation-control, do-nothing control is `gate-before.out` itself); fresher C1/C2 re-scores `c1/c1-382d11b2.json`, `c1/c1-bda324bb.json`, `c2/c2-382d11b2.json`, `c2/c2-bda324bb.json` untracked; `SCORECARD.md`'s C2 measured-commit cell names absent `c2/c2-tip.json` (use `c2-b4f3edc0.json`); `gate-after-progress.out` is a composite note, not a `--rev addeb57` run.

### 4. Sources & frontier — FILLABLE (conformance item, NOT a marker predicate)
- Committed artifacts:
  - `corpus/SOURCES.md`
  - `.ufo/waves/round-31/census-start.out` (12× E12 — repaired in-round), `.ufo/waves/round-31/census-end.out` (`ok`), `.ufo/waves/round-31/w2/census-validate-start.out` (`ok`)
  - `corpus/lessons/round-31.md` `## Gate` (S180–S191, tier A, located quotes ≤25 words)
  - `corpus/knowledge/chat-adapter-outcomes.md`, `corpus/README.md`, `README.md`, `PROVINCE.md`
  - `.ufo/waves/round-31/w1/out/ExecCensus/*`, `w1/out/ExecCensusRows/*` (committed under w1/out)
- CANNOT-FILL items: none for drafting; round-end validate (post-`addeb57`) is the latest committed `ok` at `w2/census-validate-start.out` — a final end-of-round run is pending by definition (round open).

### 5. Trend verdicts — FILLABLE as author verdicts (conformance item, NOT a marker predicate)
- Committed artifacts:
  - expansion: `corpus/knowledge/chat-adapter-outcomes.md`, `corpus/SOURCES.md` (S180–S191), `SKILL.md` §Round-31 table
  - quality: `corpus/QUALITY.md` (KQ41), `corpus/lessons/round-31.md` `## Mistakes`, `SCORECARD.md` §Round 31 corrections
  - discernment: `.ufo/waves/round-31/w1/out/CriticClaimSize/c1-noop.json`, `w1/out/RevCounterFair/{f1,f2,f3}-receipt.json` + `findings.md`, `.ufo/waves/round-31/controls/*`, `corpus/lessons/round-30-verifier-spotcheck.md` (routed repairs list)
- CANNOT-FILL items (disclose): no committed non-author verification of round 31 exists — discernment verdict is author-side only (mirrors round-30 report's "unchanged pending" treatment); C3's contribution to any verdict rests on §3's committed+uncommitted mix above.

### 6. SHONEN — CANNOT FILL at `[x]` (only `[~]`/`[ ]` reachable today)
- Committed artifacts (pointers for `[~]` lines):
  - `SHONEN.md` (4 boxes, all `[~]` author assertions — unchanged since round 29)
  - `SKILL.md` (§§Decision table, Error signatures, Checklist; §Round-31 table)
  - `LOG.md` §round 31 (domain-task log line)
  - `corpus/knowledge/chat-adapter-outcomes.md` §Run-it content, `corpus/knowledge/cross-lane-scope.md`
  - `PROVINCE.md` §Write boundary
- CANNOT-FILL reason (disclose): every box requires a named non-author verifier for `[x]`; none is committed for round 31, so the honest section is four `[~]` lines — same posture as `.ufo/reports/round-30/kama.md`. A `[x]` written today would be fabrication.

### Marker-rule exclusions (note, verbatim source: `.ufo/prompts/kama-round-31.md` L121–125)
- Sources & frontier and Trend verdicts are conformance items, NOT marker predicates: a report that names real committed work but skips them is `ok` + a logged minimum-content conformance defect.
- Marker predicates (round fails if absent): Work performed, Landed changes, Before → after measurements, SHONEN, and evidence pointers — all four currently draftable; SHONEN only at `[~]`.
