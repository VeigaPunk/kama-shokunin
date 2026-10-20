# Scout — corpus/SKILL statements about 503, loading, `/health` readiness, and non-2xx grading

Scope: every statement in `corpus/**/*.md` and `SKILL.md` mentioning 503, "Loading model",
`unavailable_error`, `is_ready`, `/health` readiness, or how the probe grades non-2xx.
Method: bounded grep of those two paths only (`503|Loading model|loading|unavailable_error|is_ready|/health|non-2xx|non-model|FOREIGN_SERVICE|MODEL_LOADING`), then line-anchored reads
(`nl -ba`). Read-only seat: no probe, server, gate, or runtime was executed. C1 facts are the
assigned context plus a read of `tools/kama-probe.sh:404-538` (classify); code is read only for
grounding, not edited.

Status vocabulary used here: **CONSISTENT** = agrees with C1; **STALE** = true of the frozen
probe/historical sample but wrong or incomplete versus the C1 repair, so it must move;
**CONTRADICTED** = a C1 fact falsifies the statement as written; **GAP** = no statement exists
where C1 needs one.

## 1. Contradicted statements

| # | path:line | quote (≤25 words) | why |
|---|---|---|---|
| C-1 | `corpus/knowledge/endpoint-identity.md:17` | "A live HTTP error response from a non-model service is foreign, not dead." | Rule 5 is **any** non-2xx other than 401/403 → `FOREIGN_SERVICE`. C1: llama.cpp b11755 `server-http.cpp:307-325` answers every non-frontend path with 503 `{"error":{"message":"Loading model",...}}` while `is_ready` false; L1 smoke graded it `FOREIGN_SERVICE non-2xx-non-model-http`. This is the corpus origin of the overreach. |
| C-2 | `corpus/knowledge/endpoint-identity.md:126` | "A live non-`2xx` non-HTML response is a foreign service." | Same rule restated as an anti-pattern ("Treating every HTTP error as dead"): the remedy sentence itself encodes the reject-all non-2xx behaviour C1 rejects for the loading body. |
| C-3 | `corpus/knowledge/listener-census.md:368` | "Needs an explicit \"HTTP responder that is not the model API\" clause, status-agnostic." | A status-agnostic foreign clause is exactly the C1 defect: the loading 503 *is* an HTTP responder that is not the model API, yet is the model server mid-load. Its 404 rows (#2,#7,#12-18) stay `FOREIGN_SERVICE` under C1's scope limit, so only the prescription is contradicted, not those verdicts. |
| C-4 | `corpus/knowledge/served-identity-crosswalk.md:52` | "on llama.cpp single-model it can even be observed mid-load." | `MODEL_OK` mid-load implies a 200 model list. C1 measured `GET /v1/models` → 503 while loading, so no list/ID exists to match at b11755. |
| C-5 | `SKILL.md:361` | "No: llama.cpp may list an id during loading" | Same claim as C-4 in the SKILL calibration table; measured b11755 behaviour contradicts "may list". |
| C-6 | `corpus/knowledge/listener-census.md:363` | "The contract's rule table only assigns a verdict for **2xx** responses" | False against today's table (`endpoint-identity.md:17` rule 5) and code (`tools/kama-probe.sh:521` `non-2xx-non-model-http`); the paragraph's premise that non-2xx has no verbatim rule is obsolete. |

C-4/C-5 carry a revision skew that L1 must resolve rather than assume: the S001 README pin is
`c0fd7862`, C1's measurement is b11755. The docs warrant "`meta` may be `null` while loading"
(`served-identity-crosswalk.md:33`); the b11755 behaviour is a hard 503. Both cannot be asserted
as one fact. [INFERENCE] The safe corpus fix is to state the measured b11755 rule and keep the
c0fd7862 doc wording explicitly revision-scoped, not to delete the docs claim.

## 2. Stale statements (accurate before the repair, wrong after)

| # | path:line | quote (≤25 words) | why |
|---|---|---|---|
| S-1 | `SKILL.md:12-13` | "Verdict vocabulary is shared with `tools/kama-probe.sh`" + six-value list | Closed enumeration omits `MODEL_LOADING`; "shared with" makes the SKILL a parity claim the repaired probe will break. |
| S-2 | `corpus/knowledge/endpoint-identity.md:3` | "The verdict vocabulary is fixed" | Same closed six-value list; "fixed" is falsified by adding a seventh verdict. |
| S-3 | `corpus/knowledge/consumer-registry.md:84-85` | "The **live verdict** column uses the binding vocabulary" | Third copy of the closed six-value list. |
| S-4 | `SKILL.md:131` | "`FOREIGN_SERVICE` or `NOT_HTTP`" | Decision-table row for "a different kind of service" is the only landing place for an unexpected HTTP answer; a loading llama.cpp returns `MODEL_LOADING`, so the table has no applicable row. [INFERENCE] A reader applying it would map the new verdict onto the old one. |
| S-5 | `SKILL.md:173` | "Process alive; says **nothing** about which model" | The identity claim is correct, but the action "Follow with `/v1/models`" can land on the same 503 loading body and, unqualified, misgrades it as foreign. |
| S-6 | `corpus/knowledge/endpoint-identity.md:89` | "Gate traffic on a matching expected ID." | The identity-readiness flow has no loading branch: the gate route (`/v1/models`) returns 503 during load. |
| S-7 | `corpus/knowledge/endpoint-identity.md:111` | "Three identical non-`MODEL_OK` verdicts are a stable failure/drift, not a flake." | Three `MODEL_LOADING` samples are a transient load state, not "stable failure/drift"; the rule needs an explicit loading exception. |
| S-8 | `corpus/knowledge/endpoint-identity.md:88` | "Lightweight process/service liveness." | For llama.cpp, `/health` 503 is a documented load state while the process is alive (`runtime-health-surface-matrix.md:14`); the liveness label invites reading a non-2xx health answer as process failure. |
| S-9 | `corpus/knowledge/served-identity-crosswalk.md:9` | "can answer while that model is still loading" | True of the 503 but incomplete: the crosswalk never says the answer *is* 503 with no list. |
| S-10 | `corpus/knowledge/served-identity-crosswalk.md:33` | "`meta` can be `null` \"for example, while the model is still loading\"" | Manual-only premise that a list exists mid-load; see revision skew above. |
| S-11 | `corpus/README.md:119` | "llama.cpp nullable loading metadata" | Index description repeats the same manual premise; no measured `/v1/models` 503 fact exists in the index. |
| S-12 | `corpus/lessons/round-1-safety.md:52-53` | "the observed 404 is a probe mismatch/error" | Conflicts with the binding table's later `404`→`FOREIGN_SERVICE` (`endpoint-identity.md:17,44`); adjacent non-2xx-grading confusion, not a 503 claim. |
| S-13 | `corpus/knowledge/served-model-identity.md:3,44` | "readiness-field probes" / "the readiness/metrics field fragment" | Labels the retained `/health`,`/props`,`/slots` bytes as readiness evidence; the sample is a loaded server only and cannot show the loading 503. README:103-106 already limits the entry's scope. |

## 3. Consistent statements (keep; do not rewrite)

| # | path:line | quote (≤25 words) | note |
|---|---|---|---|
| K-1 | `corpus/knowledge/runtime-health-surface-matrix.md:14` | "503 `unavailable_error` \"Loading model\" while loading; 200 `{\"status\": \"ok\"}` when loaded" | Matches C1. Pinned to c0fd7862, not b11755 — anchor skew only. |
| K-2 | `corpus/knowledge/runtime-health-surface-matrix.md:15` | "503 only on `EngineDeadError`" | vLLM's 503 means engine-dead, not loading. This is the engine-collision fact that forces a **body-exact** predicate, never a status-only one. |
| K-3 | `corpus/knowledge/runtime-health-surface-matrix.md:26` | "`/health` remains a lightweight liveness signal whose body must not be read as identity." | Consistent, but silent on non-2xx classification of `/v1/models` (see gap G-1). |
| K-4 | `corpus/SOURCES.md:13` | "`/health` is a load-state surface (503 loading, 200 loaded)" | Matches C1. |
| K-5 | `corpus/SOURCES.md:60` | "llama.cpp `/health` still 503 loading vs 200 loaded" | Recheck statement confirms the same semantics. |
| K-6 | `corpus/knowledge/endpoint-identity.md:9` | "exit `0` only for `MODEL_OK` and `2` for other verdicts" | Survives C1: `MODEL_LOADING` is drift-true, so targeted mode still exits 2. |
| K-7 | `corpus/knowledge/endpoint-identity.md:13-15` | "No TCP connection ... `DEAD`" / "`401` or `403` ... `UNAUTHORIZED_SERVICE`" | Rules 1-3 unaffected by C1. |
| K-8 | `corpus/knowledge/endpoint-identity.md:44` | "Both are `FOREIGN_SERVICE`, not `DEAD`" | Matches C1's scope limit: 404 text/plain from containerd/omp keeps `FOREIGN_SERVICE`. |
| K-9 | `corpus/knowledge/endpoint-identity.md:97,99` | "one request per sample with no automatic retry loop" / "A refusal or timeout is `DEAD`" | Facts about the probe, still true; they explain why one shot during load returns a loading verdict. |
| K-10 | `corpus/knowledge/endpoint-identity.md:123`; `SKILL.md:252` | "Treating `/health` as model readiness" / "Reading `/health` as identity." | Anti-patterns remain valid. |
| K-11 | `SKILL.md:202` | "Never describe exit `2` as model readiness." | Still correct; `MODEL_LOADING` must not be described as readiness either. |
| K-12 | `corpus/QUALITY.md:9,40` | "A configured URL, listener, `/health` answer, completion success, or September MODEL_OK" / "available inventory, loaded residency, advertised identity and inference readiness are separate propositions" | KQ1/KQ13 support C1's premise that a load-state answer is not identity evidence. |
| K-13 | `SKILL.md:73-75`; `endpoint-identity.md:190-193`-class samples (`listener-census.md:190-193`); `cross-lane-scope.md:20` | "`GET :34113/health` / `{\"status\":\"ok\"}`" | Dated historical loaded-server samples; they make no loading-state claim. |
| K-14 | `corpus/lessons/round-11.md:31`; `corpus/lessons/round-11-verifier-spotcheck.md:157` | "S001 allows null `meta` while loading" | Accurate as a **documentation** statement about c0fd7862; conflicts with b11755 measurement only when promoted to runtime behaviour (C-4). |
| K-15 | `corpus/README.md:31,90,103-106` | "classification/health decision table: identity vs liveness, readiness signals" | Index descriptions are consistent; they point at the entry that needs the new rule. |

## 4. Gaps (no statement exists where C1 needs one)

- **G-1 — `/v1/models` 503 is absent from the whole target set.** Grep for `/v1/models` near 503
  returns nothing; S001 is cited only for `/health` (`SOURCES.md:13`, matrix:14). C1's verdict
  keyed on `GET /v1/models` therefore has no corpus anchor at all.
- **G-2 — no b11755 / `704366d76` / `server-http.cpp` citation** anywhere in `corpus/` or
  `SKILL.md` (grep returned zero rows). Every existing llama.cpp anchor is `c0fd7862`.
- **G-3 — no reason enumeration for `llamacpp-loading`.** `endpoint-identity.md:19` lists reasons
  only for the 2xx shapes; no table row or sentence would carry the new reason.
- **G-4 — mutation matrix has no loading class.** `corpus/lessons/probe-mutation-matrix.md:11-16`
  covers M1 foreign HTML, M2 dead, M3 OK, M4 look-alike, M5 401, M6 garbage, M7 path id; no
  "model server answers non-2xx while loading" mutation, which is exactly the class C1's stub
  matrix must own.
- **G-5 — rule 5's only worked example is a non-model service** (`--port 43999`, containerd,
  `endpoint-identity.md:17`); no example distinguishes a model-server 503 from it.

## 5. Integration implications for L1 (advice, not verdicts)

1. `endpoint-identity.md:9` declares **first-match precedence**. A `MODEL_LOADING` predicate must
   therefore be evaluated *before* rule 5, or rule 5 must be split into "503 with exact loading
   body" and "other non-2xx". Appending it after rule 5 leaves it unreachable. [INFERENCE from
   the doc's own "applies this ordered table".]
2. Keep the predicate body-exact (`message == "Loading model"`, `type == "unavailable_error"`,
   integer `code == 503`, all exact). matrix:15 is the corpus reason a status-only predicate
   cannot be engine-neutral; the C1 scope limit (e.g. llama.cpp "no slot available"
   `unavailable_error`) is the second.
3. Four text sites must move together for vocabulary parity: `SKILL.md:12-13`,
   `endpoint-identity.md:3`, `consumer-registry.md:84-85`, plus the table in
   `endpoint-identity.md:11-19`; then the decision table row at `SKILL.md:131` and the
   three-sample rule at `endpoint-identity.md:111`.
4. Add the measured fact (b11755: `/v1/models` 503 with the loading body until ready) at the S001
   row or a new S-row in `SOURCES.md`, and reconcile the c0fd7862 "nullable `meta`" wording at
   `served-identity-crosswalk.md:9,33` as revision-scoped rather than silently dropping it.
5. Do not move exit semantics (`endpoint-identity.md:9`) or rules 1-2/401-403/404 scope limits
   (`endpoint-identity.md:13-15,17,44`); C1 keeps them.

## 6. Limitations and confidence

- Read-only: no runtime, probe, stub, or gate run; nothing was written except this report.
- C1 facts are supplied context + the L1 smoke observation; I independently confirmed the
  frozen-probe branch (`tools/kama-probe.sh:521` `non-2xx-non-model-http`) and that classify()
  has no body-based loading predicate, but I did not re-measure llama.cpp.
- `c0fd7862` (docs) vs `b11755` (C1 measurement) is a real anchor skew; the contradiction rows
  C-4/C-5/S-10/K-14 are the affected family and should be treated as one decision, not four.
- Confidence: high on path:line and quotes (all verified with `nl -ba`); medium on the
  docs-vs-measurement reading, where the interpretive step is marked [INFERENCE].
- Tool installs: none — no package, upgrade, or channel was used for this seat.
