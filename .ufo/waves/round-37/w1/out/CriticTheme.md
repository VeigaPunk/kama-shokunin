# CriticTheme — round 37 wave 1: the theme boundary

Seat: `L1Kama37.ChemicalCatshark` (critic). Read-only throughout: lane repo, the
read-only package, sibling `PROVINCE.md` files. No endpoint sampled, no curl run,
no tool installed, no lane or package byte written except this file.

Items I was asked to attack:

1. Is KV-cache reclamation inside kama's province (endpoint health semantics), or
   is it creeping into model-quality/serving-performance territory the Refuses
   list bars?
2. Does the lane's boundary rule — *"is the thing at this baseURL the model this
   config believes it is, right now"* (`PROVINCE.md:40-43`) — cover why a request
   is **rejected** or **re-prefilled**?
3. Narrowest honest statement of the theme that stays in province.

**Verdict in one paragraph.** KV-cache reclamation is **not** barred by a named
refusal, and that is the problem rather than the defence. The Refuses line names
model quality/eval, credentials, dispatch mechanism and remote web; it does not
name serving performance, so nothing in the lane's rule set catches a performance
claim dressed as endpoint knowledge. Reclamation is outside for a checkable
reason instead: at a fixed baseURL it moves none of the three variables kama
grades (served identity, readiness, pin correctness), its own staged source row
declares that it "carries no endpoint semantics", and every answer-facing
consequence it does have is already held by four committed entries. Of the three
candidate files, **one sentence** is new province-bearing knowledge. The theme as
worded ("engine internals that shape what a served endpoint answers") is wide
enough to admit the model's weights; it needs a second clause before it can be
written into `PROVINCE.md`, and the round must not read this admission as depth.

---

## 1. The strongest counterexample: the lane's own arbitration rule

`corpus/knowledge/cross-lane-scope.md:32` states the falsifiable test:

> Hold the consumer text, credentials, route table, and evaluation inputs fixed and
> vary one cause at a time: if changing only the response at a fixed baseURL/port
> changes service or served-model identity, the finding belongs to kama …

Vary **only the reclamation policy** at a fixed baseURL — SGLang's scored radix
leaves against vLLM's block pool. Under the lane's owned surfaces the prediction
is: `/v1/models` bytes unchanged, `/health` bytes unchanged, `/props` and `/slots`
unchanged, `kama-probe.sh check` exit unchanged, drift count unchanged, identity
verdict unchanged. A kama verdict cannot move, so by the lane's own rule the
finding is not kama's.

This is a thought experiment, not an executed probe — labelled `[INFERENCE]`.
What makes it more than speculation is that the package's own scope cells say the
same thing in writing (table in §2): none of the three documents is anchored on a
route, a status code, or a response field.

**The counterpart that does move an answer.** Vary only *cache state* rather than
policy and two things change at the endpoint: a 503 whose meaning is "saturated,
retry elsewhere" rather than "loading" or "dead", and the presence/absence of a
cache-reset route. Both are already held (§3). So the province-bearing slice of
this frontier is **state as it appears in the answer**, never the reclamation
algorithm — and the round's three files are ~90% algorithm.

## 2. Evidence: what the sources themselves claim to be about

From the staged package `SOURCES.append.md` (read-only), the `scope` column of
each row the candidate files cite:

| row | tier | staged `scope` cell | does it carry endpoint semantics? |
|---|---|---|---|
| S330 | A | "vLLM V1 scheduling and batching model as the project documents it; **not a runtime observation**" | no |
| S333 | A | "the SGLang KV-cache reclamation rule; **engine-internal, carries no endpoint semantics**" | no — stated by the row itself |
| S334 | A | "SGLang session-reference semantics; a session is not a KV pin" | **yes** — request-field meaning |
| S335 | A | "the primary statement of RadixAttention's evictability rule; historical" | no |
| S346 | B | "Chinese reverse-engineering write-up … **not authoritative for engine behaviour**" | no |
| S347 | A | "how a kv-cache block is keyed … **the design page, not an observed runtime**" | no |
| S363 | A | "vLLM's prefix-cache design at the current documentation line" | no |

The strongest single line in the round's own paperwork is S333's scope:
*"engine-internal, carries no endpoint semantics."* A round whose corpus is
defined by *endpoint* semantics cannot admit an entry whose supporting row
disclaims them without saying, in the entry, that the row is crosswalk material
only.

Section-level disposition of the three candidate files (substance only; the
provenance trios and "what this does not establish" blocks are boundary text and
all three are in province as written):

| file | section | in province? |
|---|---|---|
| `kv-cache-reclamation-models.md` | "Two reclamation models, not one" (vLLM scheduler, SGLang radix) | **out** — mechanism |
| | "The rule that is easy to get wrong" (`session_id` is not a memory pin, does not carry context) | **in** — request-field semantics; the only new fact in the three files |
| | "The Chinese-language source map (secondary)" | out — file map, already labelled B |
| `prefix-cache-reuse-models.md` | "The mechanism" (ancestry hash, full blocks, collision) | **out** — mechanism |
| | "Why this differs from SGLang's model" | borderline — the *non-portability warning* is crosswalk-useful; the comparison of mechanisms is not |
| `prefix-cache-reuse-models-amendment-2026-10-23.md` | "The correction" (v0.9.0 → v0.32.0 default hash) | out for endpoint purposes — a vendor **documentation line** changed, not any deployment; a doc-version delta is not endpoint drift |
| | "What the amendment does not establish" | in |

## 3. The duplicate-authority finding: the in-province content is already held

Four committed entries already hold every answer-facing fact these files reach
for. Admitting the mechanism as endpoint knowledge would put a second, weaker
authority on each:

| fact the candidates reach for | where the lane already holds it | evidence tier |
|---|---|---|
| a 503 can be a deliberate admission rejection, distinct from dead and from loading | `corpus/knowledge/endpoint-health-probe-conventions.md:1-19` | docs row S327, tier A, dated |
| the engine's cache-reset route differs and vLLM's needs `VLLM_SERVER_DEV_MODE=1` | `corpus/knowledge/serving-alias-contract.md:27-32` | S205, tier B |
| "cache usage" is not one number across engines (`vllm:kv_cache_usage_perc` vs `sglang:cache_hit_rate` vs `llamacpp:n_tokens_max`, which is not live KV use) | `corpus/knowledge/serving-metrics-crosswalk.md:17`, and `:42` "Metrics stay out of the identity-verdict path" | S001/S003/S007, tier A |
| how much KV exists, pool vs per-slot ceiling, measured | `corpus/knowledge/context-capacity.md` (14 fixture cells, S106–S113) | own-work, live receipt |

Note the asymmetry: on KV capacity the lane holds a **measured** account for its
own fixture; the new files offer a **documented** account for two engines the
lane has never run. If both sit unlabelled in `corpus/knowledge/`, a reader can
cite the docs model where the lane has a receipt — the exact failure
`context-capacity.md` was built to prevent.

Two smaller identity defects in the same vein:

- **Vocabulary collision.** `kv-cache-reclamation-models.md:19` says reclamation
  is "block-pool and **admission-shaped**". The lane reserves "admission" for the
  HTTP 503 verdict (`endpoint-health-probe-conventions.md:13-17`, "admission
  valves"). Two meanings for one word in one corpus invites a reader to conclude
  that reclamation *causes* 503 rejections.
- **Calibration, KQ39-class.** `kv-cache-reclamation-models.md:11` justifies the
  entry with "no documented account of *why* a served request is slow, rejected,
  or re-prefilled". "Rejected" is false at the writing revision: the lane holds a
  documented vLLM rejection (`--max-num-queued-reqs` → 503, S327) and a documented
  llama.cpp hard-bound reject (round-28 request-field outcomes, HTTP 400). "slow"
  asserts a need this lane has never had a surface to grade. Only the `session_id`
  gap is real.

## 4. Does the boundary rule cover "rejected" and "re-prefilled"?

Split the question; the rule answers one half only.

- **Rejected — partly, and only on the answer side.** The rule's variable is
  *what is at this baseURL*. A rejection changes what the endpoint does to one
  request, not what it is. The rule therefore covers a rejection **when the
  rejection is itself the evidence about serving state**: a 503 that means
  saturated rather than dead, a 400 that means a schema reject rather than a
  wrong model. That reading is in province and already held. The rule does **not**
  cover the engine's reason machinery — queue depth, prefill backlog, priority
  abort — which only explains a status the lane already classifies.
- **Re-prefilled — no, and it cannot be made to.** Re-prefill is a cost/latency
  event. It moves no identity, readiness or pin-correctness predicate, so the
  rule's variable does not change. Its only observable trace is a metric, and the
  lane's metrics entry already rules that metrics stay out of the identity-verdict
  path. Under this lane's rule, "why a request was re-prefilled" is out of
  province; reporting it out is the honest move.

So the theme cannot be justified by "it tells you why a request was rejected or
re-prefilled". For rejection the answer is already in the corpus; for re-prefill
the answer is no.

## 5. The narrowest honest statement

> **Engine cache and admission state is state the request does not carry.** It
> decides which answer a caller gets at a fixed baseURL — which status, whether a
> cache-control route exists at all, and whether a request field such as SGLang's
> `session_id` means what the caller thinks — and kama holds an engine's
> documented model only for those answer-facing consequences. It licenses no
> prediction of latency, reuse rate, throughput or answer quality, and it
> establishes nothing about any running endpoint.

Why this wording and not the assignment's:

- it names the **subject** (server-side state absent from the request), not the
  **mechanism** (radix trees, block hashes, schedulers), so a reader cannot slide
  from "the cache is not in the request" to "explain the scheduler";
- it keeps all three in-province consequences (status, route existence, field
  meaning) and drops the two out-of-province ones (latency, quality);
- it survives the arbitration rule: each consequence is an answer a probe can
  read;
- it excludes "is the request safe", which the vLLM collision note would
  otherwise import (a cross-tenant KV collision is an isolation claim, and the
  equality advice the amendment retires is deployment advice — neither is kama's).

A one-line per-sentence test the L1 can apply without me: *would this sentence
change a probe's verdict, or an answer field a probe reads?* If not, it is
crosswalk material and must be labelled as such or cut.

## 6. Smallest safe correction

Each item is scoped to what an author can do in one edit; none changes C2's
frozen predicate (names, existence, S-ids) and none touches a held entry's bytes.

1. **Write the theme where province is decided, not in an entry's `ground:` line.**
   Append a round-37 note to `PROVINCE.md` carrying §5's sentence verbatim, in the
   style of the round-28 and round-31 notes. Reason: today the only statement of
   this frontier is `kv-cache-reclamation-models.md:11`, i.e. the claimant argues
   its own scope, and C2 grades nothing about meaning.
2. **Fix the ground line.** Replace "no documented account of why a served request
   is slow, rejected, or re-prefilled" with the one real gap: *the lane holds the
   answer side of admission (S327) and the cache-control routes (S205), but holds
   no request-field semantics for SGLang's `session_id`.* Check: the new sentence
   must be false at no committed byte — `grep -n "admission" corpus/knowledge/endpoint-health-probe-conventions.md`
   and the S205 line in `serving-alias-contract.md` both exist.
3. **Label the retained mechanism as crosswalk, and ban the comparison it invites.**
   Any kept mechanism paragraph carries an explicit "not endpoint semantics"
   line and points at `serving-metrics-crosswalk.md:17` for why two engines'
   cache numbers are not comparable. Check: a reader following the pointer cannot
   read the new entry as authorising a cross-engine cache-hit comparison.
4. **Rename "admission-shaped" (line 19)** to a phrase that does not collide with
   the held 503 vocabulary — "block-pool shaped" is available.
5. **Cite release-pinned revisions for the two SGLang documents.** The package
   already carries release-pinned rows for exactly these two files (S352, S353 at
   tag `v0.5.22`, each described as "the stable version pin that the published
   page lacks") and pairs them with a different entry. Admitting the KV entry on
   the branch-commit rows (S333, S334) creates two rows per document with the
   admitted entry holding the weaker anchor. Precedent is the lane's own: round 36
   admitted S328 at tag `v0.5.22` for the same reason. Check: for each of the two
   documents the lane ends with one row whose anchor names a release tag, or an
   append-only explanation of why two rows are needed.
6. **Cross-reference, don't compete.** Add one line to the KV entry relating
   capacity (`context-capacity.md`: how much KV exists), reclamation (which KV
   survives), and the exporter number; state that no llama.cpp measurement
   transfers to vLLM or SGLang. Check: the sentence names both files.
7. **Do not claim depth.** C2 is coverage 9 → 9 and these are documentation rows
   with no live measurement; the round report should say so, so the entry is not
   read as a depth move against `context-capacity.md`'s measured cells.
8. **Amendment provenance.** `prefix-cache-reuse-models-amendment-2026-10-23.md:5-6`
   opens "staged by round 2" — a campaign-round pointer with no meaning in this
   lane's corpus. Rewrite to name the lane file it amends and the date; keep the
   correction scoped to the vendor's documented default, with no deployment
   advice.
9. **Make the recheck runnable from the lane root.** `kv-cache-reclamation-models.md:10`
   says "re-run the row recheck commands for S330, S333, S334, S335 and S346 in
   SOURCES-PROPOSED.md"; that file does not exist in this repo (`ls SOURCES-PROPOSED.md`
   → no such file) — the only copy is the read-only package's
   `lanes/kama/SOURCES-PROPOSED.md`, which will never be a lane path. A future round
   that re-runs this entry's recheck (KQ36) cannot. Follow
   `serving-alias-contract.md:8`, which lists the per-row recheck commands inline.
   Check: the entry's `recheck:` line resolves inside `kama-shokunin/`.

## 7. Axis impact

| axis | held | effect of an over-wide theme | effect of the correction |
|---|---|---|---|
| adjacency | 7 | claims adjacency to serving performance with no surface that grades it — the weakest form of an adjacency claim, and the one this lane's own `cross-lane-scope.md:49` adjacency rule forbids absorbing | adjacency gains a precise, checkable statement; this is the only axis the correction can move |
| coverage | 9 | three more files raise the count while the meaning thins toward a neighbouring subject | count unchanged, meaning preserved |
| depth | 7 | docs-only mechanism competing with 14 measured fixture cells | no depth claim made |
| calibration | 7 | ground line asserts a gap that committed bytes contradict (KQ39: false at W is a mismatch) | sentence becomes true at W |
| operability 8, freshness 8 | — | unaffected; no endpoint sampled, no probe changed | unaffected |

## 8. Limits of this critique

- The arbitration test in §1 is `[INFERENCE]` from the sources' own scope cells; I
  ran no server and issued no request. I did not re-fetch any URL — this seat's
  authorization covers only URLs named in its own item, and it names none.
- I did not audit anchor text or quote placement of the candidate rows (KQ45);
  that is another seat's charge. My finding about rows is limited to the `scope`
  column.
- I do not judge whether the three files should be admitted at all. C2 is frozen
  and its predicate is satisfiable as written; my finding is that its predicate
  grades nothing about the theme, so the theme's prose is the only gate — which is
  why §5 and §6 exist.
