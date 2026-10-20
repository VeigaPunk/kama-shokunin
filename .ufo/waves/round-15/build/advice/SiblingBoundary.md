# SiblingBoundary — round 15 kagi / kumitate / kengaku adjacency (connector)

- **Seat:** `KamaR15.SiblingBoundary-3`, UFO-FSD connector, leaf. This is parent-dispatched author-side advice, not outside review.
- **Root:** `/home/vgpnk/Projects/shokunin/kama-shokunin`. Paths are relative to it unless absolute, with these abbreviations: `build/` and `advice/` = `.ufo/waves/round-15/build/` and `.ufo/waves/round-15/build/advice/`; `lessons/` and `knowledge/` = `corpus/lessons/` and `corpus/knowledge/`; `round-14/…` = `.ufo/waves/round-14/…`; `kagi-shokunin/…`, `kumitate-shokunin/…`, `kengaku-shokunin/…` and `kumitate PROVINCE` sit under `/home/vgpnk/Projects/shokunin/`; `../AXES.md` and `AXES.md` = `/home/vgpnk/Projects/shokunin/AXES.md`; bare `check.py`, `measure.py` and `cases.json` = `tests/ollama-corpus-guard/check.py`, `.ufo/waves/round-14/measure.py` and `tests/ollama-evidence/cases.json`.
- **Read time:** 2026-10-20T08:21:16Z (`date -u`). Files changed while I read them. Line numbers and digests are as of read time.
- **Digests at read time:**

  | File | sha256 | Lines |
  |---|---|---|
  | `tests/ollama-corpus-guard/check.py` | `0ca9a542…` | 732 (it was `2ec5db64…` earlier in this review) |
  | `.ufo/waves/round-14/measure.py` | `46c5866d…` | guard at 358–359 |
  | `.ufo/waves/round-15/frozen/measure-before.py` | `fda61e00…` | |
  | `tools/kama-ollama-evidence.py` | `38d1f5d2…` | equals the round-14 verified digest |
  | `tests/ollama-evidence/cases.json` | `4a4de0b8…` | equals the outside 51/51 recount |
  | `LOG.md` | `17162865…` | 881 |
  | `corpus/lessons/round-15.md` | `92af5ae9…` | 99 |

- **Writes:** this file only.
- **Tooling:** nothing was installed or updated. The operator's pacman pause, relayed by KamaR15, is acknowledged. No uv, npx or binary install was needed.

## Axes

- **Calibration** (C1 axis; `../AXES.md:15`): gaps named honestly, overreach caught, entries match repo state.
- **Adjacency** (`../AXES.md:16`): evidence belonging to another domain is reported, not absorbed. The verdict must stay **unchanged**.
- **Operability, freshness, depth, coverage:** must not move.

## 1. Evidence — the boundary seen from both sides

| Sibling | Kama side | Sibling's own PROVINCE | Round-15 surface at the border (committed bytes) |
|---|---|---|---|
| **kagi** | `PROVINCE.md:40` refuses credential material and auth flows. `SKILL.md:27-31` and `:139` say "Do not copy a global config or environment into the corpus". QUALITY KQ2 (`:10`, never inspect environment values) and KQ5 (`:13`, nonsecret shape only). | `kagi-shokunin/PROVINCE.md:3` covers secrets and vault ops. `:63` says kama routes credential needs through L0, kagi owns runtime auth and credential custody, and siblings' output tripwires are hygiene, not vault ops. | `measure.py:199-208` and `check.py:309-319` each give children a fixed five-key environment: PATH, HOME, TMPDIR, LANG, LC_ALL. Under the harness, the runner itself never holds the operator's environment (`check.py:375`). A direct runner invocation still inherits its caller's environment, but it passes only PATH on to children. The audit hook writes only `event` (`check.py:273-276`). **This line carries the whole guarantee:** CPython 3.14.7 calls `sys.audit("subprocess.Popen", executable, args, cwd, env)` (`/usr/lib/python3.14/subprocess.py:1858`), so the event's arguments include the child `env`. R2 keeps `Cursor RESOURCE_EXHAUSTED` verbatim (`lessons/round-15.md:38`). A secret-shaped tripwire over the round-15 outputs found no matches (§6). `.ufo/interactive-sessions/` is gitignored (`.gitignore:1`, 0 tracked files). HostSafety's search bypassed that ignore; containment is recorded at `lessons/round-15.md:94-99`. |
| **kumitate** | `PROVINCE.md:41` refuses dispatch and route mechanism. `SKILL.md:139` and `knowledge/cross-lane-scope.md:28`. | `kumitate-shokunin/PROVINCE.md:3` covers "OMP task/hub, ufo-fsd scripts & runtime". `:12` makes the ufo-fsd-alpha `scripts/` layer core. `:19` puts the OMP harness contract (task batch) on its frontier. `:27` sends local serving to kama. `:28` files upstream ufo-fsd-alpha defects for the operator and never patches them. `kumitate-shokunin/corpus/knowledge/omp-task-contract.md:70-74` says a non-blocking spawn is a background job; it says nothing about a job limit or its scope. | `build/validation.json` ran `ufo-swarm-wave.mjs run`, exit 0, empty stderr; its stdout equals `build/dispatch.json`. Policy: maxLanes 64, waveMaxLanes 100, hardCeiling 100, globalRunnerCeiling 1056. `taskCall` has keys `{context,tasks}`. All 64 tasks have keys `{agent,name,task}` only, so there is **no per-task model or route**. Roles: scout 20, executor 17, reviewer 9, critic 6, connector 4, scribe 4, sentinel 2, revenger 2 — no planner seat. `build/spawn-result.json` and `build/spawn-result-retry.json` each list 64/64 names refused with `Background job limit reached (100)`, and `details.results` is `[]`. `build/direct-spawn-result.json` holds 64 ids, equal to `{KamaR15.<task>-3}`, to `build/assignments.json` values and to `advice/swarm-registry.json` agentIds. Its `source` string is written by L1 and no payload is committed. **Seat-side corroboration:** the shared Context and task text this seat received match `taskCall.context` (sha256 `0df8a2aa…`, 2148 chars) and the SiblingBoundary task (sha256 `b02d2a28…`, 961 chars) by visual comparison. The only extras are a one-line harness preface and the trailing operator tooling directive. This covers 1 of 64 seats and is not a digest of the received bytes. |
| **kengaku** | `PROVINCE.md:40,42-43` refuse model quality and eval. `knowledge/cross-lane-scope.md:27` gives batteries, scoring, calibration and quality claims to kengaku. | `kengaku-shokunin/PROVINCE.md:3` covers LLM research and evaluation. `:19` is its own offline replay gate (`grader.py`). `:121-122` put judge calibration of its own grader on its frontier. `:132` sends serving plane and endpoint identity to kama. `:33` and `:139` say "the shared word 'probe' carries no scope". `:27-28` and `:137` send OMP route resolution, fallback policy and operational failure taxonomy to kumitate. | The check.py verdict map is `clean`/`test_failed`. `SKILL.md:495` says "neither means serving readiness". `knowledge/ollama-evidence-replay.md:347-348` says "never a model or readiness verdict". `measure.py:78` makes no model-quality claim. `check.py` LIMITS (`:84-95`) has no such line; prose covers it. The matrix at read time has 12 files and 50 tests: 27 expected-rejected and 23 accepted. The 23 accepted tests total **402 names**, which means 402 classifier runs over **one** cloned capture: `cases.json[0]` `loaded_same_digest`, with no remote markers. None of `check.py`, `measure.py` or `tools/kama-ollama-evidence.py` contains a generation endpoint or network import. |

## 2. Contradictions

- **C1 — limit scope.** `LOG.md:876` says "the session-wide background-job limit100". The committed refusal text only says `Background job limit reached (100). Wait for running jobs to finish or cancel one.` Kumitate's contract entry (`kumitate-shokunin/corpus/knowledge/omp-task-contract.md:70-74`) states no scope. "Session-wide" is therefore an unsourced statement about kumitate-owned harness behavior. That is a small act of absorption plus an overclaim.
- **C2 — "unchanged retry".** `LOG.md:876-877` says "One direct unchanged retry". The validated payload is pinned: `validation.json` stdout equals `dispatch.json`. The payload of the direct call was not committed, though; `direct-spawn-result.json` holds only ids and an L1 summary. The identity census and this seat's prompt support "unchanged" but do not prove it.
- **C3 — R2 rule.** The draft rule at `advice/R2Partial.md:33` says a seat is terminal only when the integration record gives it an accepted disposition. The round-14 data contradict it: `round-14/integration-review.json:10` accepts the "ScopeSimplifier/ExistingProbe contract", while `:23` lists ExistingProbe as a dead seat. Acceptance and dispatch lifecycle are independent, as verifier R2 (`lessons/round-14-verifier-spotcheck.md:143`) and landed `lessons/round-15.md:38` say. Adopting the draft would also make kama define OMP task-batch completion semantics, which is on kumitate's frontier (`kumitate PROVINCE:19`). The landed lesson text is right; do not adopt the draft rule.
- **C4 — missing handoff.** `PROVINCE.md:51-53` requires naming out-of-province evidence for its owning lane in the round report. The dispatch refusal is kumitate's evidence, but `LOG.md:875-878` records it as an L1 fact with no owner named.

## 3. Proposed move (one)

**A two-sided boundary ledger that can be checked against committed bytes, carrying the one new kumitate handoff.**

L1 does three things:

1. **Fix `LOG.md:875-878`.** This is L1's own round-15 text. Replace "the session-wide background-job limit100" with the verbatim `Background job limit reached (100)`. Then do one of two things with "unchanged":
   - pin it, by stating that the direct call passed `dispatch.json` `taskCall` verbatim (canonical sha256 `4c0ab2ef8d6ff4eb5b98f56d9a3dafa8e4c7781dd518a78b437a33f3018821ef`, command in §6); or
   - replace it with "a direct retry of the validated payload; direct-call bytes not separately committed".
2. **Append a three-row ledger to `corpus/lessons/round-15.md`.** That lesson is new this round, so appending is allowed. Draft:

   | Owner | Kama observed (committed) | Kama does not claim | Falsifier (explicit paths, static) |
   |---|---|---|---|
   | kagi | Five-key child environments (`measure.py:199-208`, `check.py:309-319`); the audit hook stores event names only (`check.py:273-276`); R2 string kept verbatim | Any environment value read or recorded beyond PATH pass-through; provider quota or auth diagnosis; any session or credential read | The only `stream.write` calls in `check.py` are `event + "\n"` and the marker `"x\n"`; both environment builders are five-key dict literals; the secret-shape grep over round-15 paths matches nothing |
   | kumitate | 2 × 64/64 refusals `(100)` with `results: []`; direct ids equal the registry; task keys `{agent,name,task}` | The limit's scope or cause; any change to dispatch policy, the swarm script or ufo-fsd-alpha; any route or model selection; any classification of `RESOURCE_EXHAUSTED` | The dispatch census in §6 |
   | kengaku | Test-contract verdicts only; the 402 accepted-control runs are one cloned capture | Any score, battery, judge calibration, readiness, or classifier accuracy beyond the 51-case denominator | The matrix and template census in §6; no generation endpoint or network import in the three code files |

3. **Add three handoff lines to the fleet report**, ready to paste:
   - **kumitate:** "Kama reports round-15 dispatch evidence for your OMP task-batch/ufo-fsd surface: the validated 64-task wave (`build/dispatch.json`; `validation.json` exit 0) was refused twice, 64/64 names `Background job limit reached (100)`, `results: []` (`spawn-result.json`, `spawn-result-retry.json`). A direct retry spawned 64 (`direct-spawn-result.json`, L1-authored). Tasks carry only `agent,name,task`. Kama inspected no occupying jobs, classified neither this nor round-14's `Cursor RESOURCE_EXHAUSTED`, and changed no policy or ufo-fsd-alpha file. Limit scope and any fix belong to kumitate and the operator."
   - **kagi:** "Kama reports no credential surface touched: runner and harness children get a fixed five-key environment; the process-audit hook stores event names only, although CPython's `subprocess.Popen` audit arguments include `env`; R2 stays verbatim with no quota or auth inspection; a secret-shaped tripwire over round-15 outputs matched nothing. One seat's ignore-bypassing grep touched a gitignored session-log path; it is excluded and contained (`lessons/round-15.md:94-99`)."
   - **kengaku:** "Kama's round-15 'calibration' is its fleet self-assessment axis (`AXES.md:15`), not evaluation calibration. The corpus-guard matrix grades a runner's admission contract, generates nothing and scores no model. Its 23 accepted controls run the unchanged classifier 402 times on one cloned capture, which is invocation evidence, not 402 cases; the denominator stays 51. As with 'probe', the shared words 'calibration', 'replay' and 'grade' carry no scope."

No code change is required. **One optional, conditional point:** if AttackSentinel or FalsifyAudit lead L1 to strengthen attribution, compute a boolean inside the hook (for example, "the wrapper path is in argv") and never serialize the hook's arguments.

## 4. Affected axes

- **Calibration — improves** within the C1 axis. Two author statements that went beyond the committed bytes (C1, C2) are caught, and every boundary sentence gets a falsifier. The score stays 7 → 7, no separate claim or credit is taken, and the move rests on no outside discovery.
- **Adjacency — exercised, not credited.** The kumitate line fulfils `PROVINCE.md:51-53` and KQ5. The verdict should stay `unchanged`; claiming improvement would be inflation.
- **Operability, freshness, depth, coverage — unchanged.** No runtime, source, surface or code change is involved.

## 5. Risks

- **Boilerplate.** Keep the ledger to three rows and three handoff lines.
- **The handoff could be read as a diagnosis.** It quotes facts verbatim. The observation that policy ceilings (1056/100) do not reflect the refusal is `[INFERENCE]`, and the owner decides. Finding out which jobs held the limit would need session or process inspection, which is forbidden.
- **The seat attestation is weak.** It is one seat of 64, compared visually. The L1 digest (or the softer wording) is the primary fix.
- **Drift.** `check.py` changed during this review. Run the falsifiers on the final committed revision; the line numbers here are as of read time.
- **The 402 figure could itself become inflation** if someone sums `child_count` as classifier cases. The ledger must call it invocation evidence. PriorCoverage owns expansion accounting.

## 6. Verification for L1

Use explicit paths only. Do not search the lane root, bypass ignores, or touch session or history.

```sh
cd /home/vgpnk/Projects/shokunin/kama-shokunin
python3 - <<'EOF'
import json, re
b = '.ufo/waves/round-15/build/'
d = json.load(open(b + 'dispatch.json')); tc = d['taskCall']; n = [t['name'] for t in tc['tasks']]
print(sorted(tc) == ['context', 'tasks'], {tuple(sorted(t)) for t in tc['tasks']} == {('agent', 'name', 'task')})
print(set(json.load(open(b + 'direct-spawn-result.json'))['ids']) == {f'KamaR15.{x}-3' for x in n}, set(n) == set(d['registry']['members']))
for f in ('spawn-result.json', 'spawn-result-retry.json'):
    s = json.load(open(b + f)); print(f, len(re.findall(r'Background job limit reached \(100\)', s['text'])), s['details']['results'])
EOF
python3 -c 'import json,hashlib;tc=json.load(open(".ufo/waves/round-15/build/dispatch.json"))["taskCall"];print(hashlib.sha256(json.dumps(tc,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest())'
grep -n -E 'stream\.write|environ' tests/ollama-corpus-guard/check.py .ufo/waves/round-14/measure.py
grep -n -E '/v1/chat|/api/generate|/api/chat|import (socket|urllib|http)' tests/ollama-corpus-guard/check.py .ufo/waves/round-14/measure.py tools/kama-ollama-evidence.py
python3 -c 'import json,glob;t=[x for f in sorted(glob.glob("tests/ollama-corpus-guard/*.json")) for x in json.load(open(f))];a=[x for x in t if not x["expected_rejected"]];c=json.load(open("tests/ollama-evidence/cases.json"));c=c["cases"] if isinstance(c,dict) else c;print(len(glob.glob("tests/ollama-corpus-guard/*.json")),len(t),len(t)-len(a),len(a),sum(len(x["names"]) for x in a),[x["name"] for x in c if isinstance(x,dict) and x.get("expected_exit")==0][0])'
```

Results this seat observed at read time from these read-only reads:

- Dispatch census: `True True`, `True True`, `64 []` twice.
- Payload digest: `4c0ab2ef…`.
- Writes and environment reads: only `event + "\n"`, `"x\n"` and the two `os.environ.get("PATH")` lines.
- Generation endpoints and network imports: none.
- Matrix census: 12/50/27/23/402; the template is `cases.json[0]` `loaded_same_digest`.
- Secret-shaped pattern grep over `tests/ollama-corpus-guard`, `corpus/lessons/round-15.md`, `.ufo/waves/round-15/{build,frozen}` and `round-14/measure.py`: no matches.

## 7. Limitations and disclosures

- **Read-only commands run:**
  - JSON censuses of the round-15 build artifacts and matrix
  - `sha256sum`, `wc`, `date`
  - `git check-ignore` and `git ls-files | wc -l`, metadata only
  - a grep of `/usr/lib/python3.14/subprocess.py` for `sys.audit`
  - targeted greps on the explicit files named above

  No tests, runner, check.py or probe were executed.
- **Read-only sibling reads:** `kagi-`, `kumitate-` and `kengaku-shokunin/PROVINCE.md`, plus one targeted grep of `kumitate-shokunin/corpus/knowledge`.
- **Disclosure:** one early `glob` for `.ufo/**/SiblingBoundary*` ran with gitignore disabled. It listed directory names, which can include the ignored `.ufo/interactive-sessions/`. It opened no file content and matched nothing.
- **No forbidden access:** no history, session, `agent.db`, credential or auth access, and no `omp` CLI.
- **Not established:**
  - the bytes of the direct call's payload
  - what the other 63 seats received
  - the final committed revisions of `check.py` and `measure.py`
  - whether the runner's spawns also raise `os.posix_spawn` audit events (that belongs to FalsifyAudit)
  - the scope or cause of the job limit (that belongs to kumitate)

Report: .ufo/waves/round-15/build/advice/SiblingBoundary.md
