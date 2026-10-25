# ConnSibling — sibling-overlap scan, kama round-37 wave 1

Seat: `L1Kama37.UndergroundBedbug` (connector). Read-only. Target: does engine
KV-cache / prefix-cache **internals** belong to kama, kengaku (model eval) or kumitate
(orchestration tooling) — and does the boundary rule “what a served endpoint answers”
cover it?

Read (nothing written outside this path; no git/jj mutation, no pacman, no install):
kama `PROVINCE.md` (`:1-55`, `:88-159`), `corpus/QUALITY.md`, `README.md:1-10`,
`corpus/knowledge/serving-metrics-crosswalk.md:1-30`,
`corpus/knowledge/sglang-native-route-deprecation.md:1-30`; kengaku `PROVINCE.md`
(`:1-70`, `:123-228`); kumitate `PROVINCE.md`, `SKILL.md:1-30`; package
`shokuknow/merge/kama/` (`MERGE-REPORT.md`, `SOURCES.append.md`, three entries);
peer seats in this wave (`CriticTheme.md`, `ReviewFrontier.md`, `RevengerIntent.md`,
`ScoutRegister.md`, `ScoutGate.md`, `ExecCollision.md`, `FetchS335.md`, `FetchS346.md`).
Scans: `grep -ril -E 'kv[-_ ]cache|prefix[-_ ]cache|radix'` over kengaku and kumitate
`corpus/knowledge/` → **0 hits each**; `vllm|sglang` over kumitate `corpus/` → **0 hits**.
Plain `cache` does occur in kumitate — `SKILL.md:610` (gate-mutants battery text),
`corpus/knowledge/cost-and-profile.md:32,79,338` (`agents.route_cache`,
`canonical_cached` profile memoization), `corpus/knowledge/runtime-remainder-census.md:174`
(`TRUSTED_GODSPEED_CACHE`) — every one an **OMP/agent** cache, none a model KV or
prefix cache.

## 1. Ownership — three refusals, no competing claim

| lane | operative text | claim on engine-internal KV/scheduling docs |
|---|---|---|
| **kama** | Domain “local model serving & endpoint health”; owns `/health`, `/props`, `/slots`, served-model-id reconciliation, drift; holds `serving-metrics-crosswalk.md` (`vllm:kv_cache_usage_perc`, `sglang:cache_hit_rate`, S001/S003/S007) and `sglang-native-route-deprecation.md` (S328/S329) | **Conditional holder**: the mechanism as the *explanation* of an answer surface it already governs. No flag-change authority (write boundary `:44-48`) |
| **kengaku** | `PROVINCE.md:24` “**Not owned:** the model-serving plane (llama-server flags, slot/batch config) — no lane owns it; escalate to the integrator instead of remediating.” `:136` routes “serving plane + endpoint identity” to kama and keeps only *interpretation* evidence (`--kv-unified`, q4_0 KV, `--parallel`); “flag-change authority is unowned/integrator”. Its `vLLM docs` surface row is scoped to “novelty pricing of local findings” | **None.** Eval/interp only; refuses the plane and never reads engine docs as engine-mechanism claims |
| **kumitate** | Domain “orchestration & tooling — OMP task/hub dispatch, ufo-fsd scripts & runtime” (`SKILL.md:3`); bands are ufo-fsd script/runtime, `~/.kimi-code`, own instruments; §Adjacent “Local model serving and endpoints → kama.” Its dispatch object is **OMP task/hub** dispatch (swarm wave / sighting / native round), not request-to-replica routing. It does hold an agent-side `agents.route_cache` (`corpus/knowledge/cost-and-profile.md:32`) | **None on model KV/prefix cache.** Zero `kv[-_ ]cache` / `prefix[-_ ]cache` / `radix` / `vllm` / `sglang` hits; its `route_cache` is the OMP agent route table, a different object |

Three edges that must stay named: (i) cache-aware **scheduling inside one engine**
(SGLang §5.2, S335) is not kumitate’s dispatch; (ii) cache-aware **load balancing
across replicas** would be serving-plane routing that *no* lane owns — kengaku `:24`
sends it to the integrator; (iii) the word “cache” has a stranger in kumitate
(`agents.route_cache`, the OMP agent route table), so “prefix-cache-aware routing”
must not be handed to it by word-association that mirrors the wrong way. None of the
three makes model-KV internals kama’s or a sibling’s.

**Consequence for the round:** if kama declines the theme, it is not adoptable by a
sibling; the residual is integrator-routed, not reassigned.

## 2. Does “what a served endpoint answers” cover it? — only the answer-shaping subset, and the lane’s bytes disagree about how much

1. **The written boundary sentence is narrower than practice.** `PROVINCE.md:41-43`:
   kama answers *“is the thing at this baseURL the model this config believes it is,
   right now”* — identity only. Yet the owns table and held corpus run well past
   identity: `/slots`, `/props`, the metrics crosswalk, r26 error signatures, r28
   request-field schema. Under the sentence alone, cache internals are out; under the
   held-surface list, the answer-facing part is in.
2. **The staged row disclaims endpoint semantics itself.** `SOURCES.append.md:10`
   (S333) scope cell: “the SGLang KV-cache reclamation rule; **engine-internal,
   carries no endpoint semantics**”. Already quoted by `CriticTheme.md:68,76`; my
   scan adds that no sibling claims the object that cell disclaims.
3. **What the rule does cover, exactly:** `vllm:kv_cache_usage_perc`,
   `sglang:cache_hit_rate`, `num_used_tokens`, `token_usage`
   (`serving-metrics-crosswalk.md:17`) and the queue/prefill answers behind
   `--enable-metrics` — i.e. the *meaning* of a surface kama already measures. Not
   covered: eviction scoring as such, radix structure as such, and any “the endpoint
   answers X” without an observed answer on this host.

**Verdict.** kama is the owning lane for the answer-shaping slice; the mechanism as
such is unowned serving-plane internals (kengaku `:24`). Siblings: zero contested
holdings, zero absorbing candidates.

## 3. Relationship to peer findings in this wave (not re-derived here)

| finding | seat | my scan’s disposition |
|---|---|---|
| `ground:` cites a “serving-stack internals” frontier item absent from the lane | `ReviewFrontier.md:85-94`, `RevengerIntent.md:167-169` (D1) | Confirmed from the sibling side too: the phrase exists only in the package and wave scratch copies; no kengaku/kumitate file uses it either, so it is not a sibling’s declared item being borrowed |
| “staged by round 2” implies a kama round 2 that never wrote these paths | `RevengerIntent.md` D4 | Confirmed: `git log --all -- corpus/knowledge/prefix-cache-reuse-models.md` is empty |
| `recheck: … SOURCES-PROPOSED.md` unreachable in-lane | `RevengerIntent.md` D5 | Confirmed; package ships `SOURCES.append.md` |
| S335/S346 are r36-register `payload-absent` kama rows, re-opened this round | `ScoutRegister.md` §1–2, `ScoutGate.md` | Confirmed by URL identity (S200→S335 arXiv 2312.07104; S211→S346 AaronYang llm ch.6); re-open receipts 200/sha-pinned |
| mechanism sections are outside the boundary; one sentence is new | `CriticTheme.md` §2–3 | Agreed; my contribution is the sibling arbitration that decides *where the residual goes* |

## 4. One bounded move

**File the split authority in the round-37 coverage block — one paragraph, no new
mechanism claim — and name the integrator route for the residual.**

Text the block adds, in these terms:

> These three entries are engine-documentation crosswalk material (vLLM v0.9.0 and
> v0.32.0 design pages; SGLang rev-pinned docs), admitted to explain the *meaning* of
> cache surfaces the lane already crosswalks (`serving-metrics-crosswalk.md:17`,
> S001/S003/S007). They carry no endpoint semantics of their own — S333's scope cell
> says so — and flag-change authority for KV quantization, `--parallel` and
> session/prefix policy remains unowned, escalated to the integrator (kengaku
> `PROVINCE.md:24,:136`). The one province-bearing fact they add is S334's: a
> session reference is **not** a memory pin, so a request must still carry its full
> intended prompt.

Why this is the move: it converts `CriticTheme`'s “out of province” disposition into a
filed boundary instead of an unstated one; it keeps the three files landing (C2 counts
file names + new S-ids), so coverage is not harmed; and it prevents the round from
silently absorbing the unowned mechanism as kama authority, which is the calibration
hazard. It also forecloses the sibling question permanently: no lane can later claim
the theme was absorbed without contradicting this paragraph.

## 5. Risks

- **Coverage-only admission.** If the paragraph is the only restraint, a later round
  can cite the mechanism as endpoint fact. Mitigation: the paragraph names S333’s own
  disclaimer and the integrator escalation, both checkable.
- **Router drift.** SGLang §5.2 “Cache-Aware Scheduling” (S335) invites a future entry
  into replica-routing policy — unowned. One sentence now, naming it, is cheaper than
  a boundary repair later.
- **Rewriting staged bytes.** Provenance re-anchoring (D1/D4/D5) is lane-authored
  adaptation; the package copy must not be presented as the landed text (KQ3).

## 6. Verification (planner/scribe; not run here)

1. `python3 tools/round37-coverage-audit.py --repo … --tip <full-commit>` →
   `named 3 files_exist 3 cited_new 3 met True`, exit 0.
2. `grep -n 'carries no endpoint semantics\|integrator' corpus/README.md` → the block
   carries both, next to the three names.
3. `grep -c 'SOURCES-PROPOSED' corpus/knowledge/*.md` → 0.
4. `git log --all --oneline -- corpus/knowledge/prefix-cache-reuse-models.md` → only
   round-37 commits.
5. kengaku/kumitate unchanged: `git -C ../kengaku-shokunin status --porcelain` and the
   same for kumitate → empty (this wave touched neither).

Scope: nothing edited outside this file; `git` read-only; no server started; package
read-only; considerthese read for framing only.
