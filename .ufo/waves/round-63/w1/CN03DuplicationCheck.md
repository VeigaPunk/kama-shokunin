# CN03DuplicationCheck — round-63 duplication connector (kama, operability)

Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09`. Tip claims were read from `git show <tip>:path` and `git grep <tip>`. The candidate new entry is the **uncommitted working-tree draft** of `corpus/knowledge/completion-request-plane.md` (+44/−3; its section "Round-63 strict response grading" is at draft lines 74–112) plus uncommitted `corpus/SOURCES.md` rows S527/S528.

Line anchors: `T:n` = tip blob line; `D:n` = working-tree draft line. The tip `completion-request-plane.md` is 71 lines and has no v2 section. The v2 grader exists at tip in `tools/kama-completion-live.py` and `tools/round63-c1-counter.py`.

Scope: scan only. No counter was run, no live server was started, nothing was committed, and no lane file was edited. Evidence: `.ufo/waves/round-63/w1/out/CN03DuplicationCheck/overlap-evidence.txt`.

## Bottom line

- Most of the v2 grading restates material the corpus already holds. The restated items are the finish_reason/usage/timings rules, the digest binding, the outside nonce observer, the named-check credit rule, the sensitivity and planted-control self-tests, and the reconciler at mismatches=0.
- Genuinely new ground is narrow: (1) the completion-route source facts S527/S528 (uncommitted, see §6); (2) the exact `application/json` Content-Type rule on the completion POST; (3) the `usage.prompt_tokens == /tokenize(prompt)` equality and the fingerprint equality; (4) the collateral cap of 5 failing checks (30 for envelope); (5) the exit-code leg of the sensitivity test; (6) the proxy-honouring `urllib` finding.
- The draft repeats itself and is partly stale. "Round 63 adds nine checks" (D:78) is wrong: three of the nine table rows are existing v1 check names. Tip `T:43-44` is stale against the tip tool. Draft `D:58` still points at the round-62 counter. Some grading status is stated twice, once superseded inline.
- Several tensions need the L1's decision before any entry is written (§7). The largest: C2 counts tip-state reconciler mismatches as calibration, which KQ39 classifies as drift.

## 1. The v2 draft table, row by row (D:83–93)

Column "new name" means the check name is absent from the round-62 v1 receipt `.ufo/waves/round-62/w1/out/W02KnowledgeDraft/receipt.json` (checks: bad_request_graded, completion_deterministic, completion_envelope, completion_fingerprint, completion_finish_reason, completion_model_id, completion_timings, completion_usage, …).

| Row (draft line) | New name? | Overlap (path:line) | Classification |
|---|---|---|---|
| `completion_headers` (D:85) | yes | `corpus/knowledge/endpoint-identity.md:16` (row 4: any non-2xx/401/403 with `text/html` → FOREIGN_SERVICE); `SKILL.md:129` (HTML-page symptom); `SKILL.md:175` (HTML 404 on `/v1/models`, `POST /v1/chat/completions`) | Partial. The principle "content type is route evidence" is restated. The exact `application/json` requirement on the completion POST is new. Conflicts in breadth with `endpoint-identity.md:18` (row 6, 2xx model arrays: "any non-HTML content type" → MODEL_OK). See §7.2. |
| `completion_untruncated` (D:86) | yes | none. `git grep -i truncat` over corpus/knowledge, QUALITY.md and SKILL.md hits only unrelated numeric-truncation rows (SKILL.md:1184–1220) | New ground. Own-work receipt-integrity rule, near KQ66 and KQ43 in spirit only. |
| `completion_choice_shape` (D:87) | yes | `T:27` (choices[0].text is "a string is graded, its content never"); `T:43-44` (non-invariant: "any completion string would pass") | Partial. `index`/`logprobs`/single-choice rules are source-derived (S527, new). "Non-empty text" is a fixed-request observation. The tip tool already checks non-empty text (`tools/kama-completion-live.py:381–388`), so `T:43-44` is stale at tip. The draft corrects it (D:43-44). |
| `completion_finish_reason` (D:88) | **no** | `T:28` (graded `length`/`stop`); `T:53-54` (lists `completion_finish_reason` as an existing check); round-62 receipt | Restatement. Only the source ground (S527 lines 374–377) is new. |
| `completion_id_created` (D:89) | yes | `T:47` (id/created recorded but ungraded); draft supersedes it inline at `D:47-48` | Partial. S527 field facts are new. The 10^9 floor is the lane's own bound and is labelled as such. |
| `completion_usage` (D:90) | **no** | `T:31` (sum graded; `cached_tokens` "present, ungraded") | Restatement plus a small delta: `cached_tokens ≤ prompt_tokens`. |
| `completion_timings` (D:91) | **no** | `T:32` (`predicted_n` equals `usage.completion_tokens`; `predicted_ms` numeric) | Restatement plus a delta: `cache_n`/`prompt_n` non-negative, `predicted_ms` finite. Field names from S528 (new ground). |
| `completion_prompt_tokens` (D:92) | yes | `QUALITY.md:421` (KQ76: an observer's "fresh nonce answered by the server's own tokenizer surface — `POST /tokenize`"); `QUALITY.md:435` (KQ80: the observer derives facts itself); `corpus/README.md:1113–1122`, `:1277` (tokenize as observer, lane README) | Partial. The observer/tokenize technique is restated from KQ76. The equality `usage.prompt_tokens == tokenize count` is new and is honestly fixture-limited at D:92–93. |
| `completion_request_bound` (D:93) | yes | `QUALITY.md:315` (KQ43: receipt records invoked argv and digests); `QUALITY.md:386` (KQ66: input digest) | Restatement (own-work binding of request bytes). |

Tally of the nine v2 table rows: restatement 4 (finish_reason, usage, timings, request_bound), partial 4 (headers, choice_shape, id_created, prompt_tokens), new 1 (untruncated).

## 2. Draft prose outside the table

- **D:95–104, counter item (a)**: re-hashing model and server files. Restates KQ66 (`QUALITY.md:386`) and KQ74 (`QUALITY.md:410`: a recorded digest bound to the artifact the same run used). Restatement.
- **D:95–104, item (b)**: listener ownership from the counter's own outside contact, child pid and port. Restates KQ76 (`QUALITY.md:421`), KQ80 (`:435`) and KQ81 (`:436`, child_pid equals observed pid). Restatement.
- **D:95–104, item (c)**: nonce, held child's `/tokenize`, and `system_fingerprint` equality. The nonce and tokenize parts restate KQ76. Fingerprint equality is new, but the fingerprint is build-level (`b11755-704366d76`, `T:30`), so it binds the process, not the model.
- **D:106–108, proxy**: `urllib` honours `HTTP_PROXY`; the draft switched to the lane's proxy-free opener. `git grep -i proxy` over corpus/knowledge, QUALITY.md and SKILL.md finds nothing about it. **New.**
- **D:110–112, Not asserted**: no overlap found.
- **D:83–93 intro "adds nine checks"** (D:78): inaccurate. Six names are new (headers, untruncated, choice_shape, id_created, prompt_tokens, request_bound). Three are existing v1 names extended (finish_reason, usage, timings).

## 3. Counter control mechanics (what the entry would describe)

| Mechanism (tip path:line) | Overlap (path:line) | Classification |
|---|---|---|
| C1 credit: named check in the failure set and ≤5 collateral failures, 30 for envelope (`tools/round63-c1-counter.py:50–51`, `:489–495` `is_hit`) | `QUALITY.md:122` (KQ21: a retained control misbehaves exactly as the check names, and the gate rejects it with only the failing check flipped); `corpus/knowledge/error-is-not-a-verdict.md:70–72` ("a grid credits a refusal only when its stderr carries the pinned reason, so the catch-all cannot launder an unrelated failure"); `:76–77` (a kill counts only on exit 1, never on could-not-evaluate) | Named-check rule: restatement of KQ21 and `error-is-not-a-verdict.md:70–72`. The collateral cap: **new**. `git grep -i collateral` over corpus and SKILL.md at tip returns nothing. The constants 5 and 30 are L1 choices with no source row. |
| C1 evaluator self-test: 3 planted wrong-reason controls (`round63-c1-counter.py:52`, `:498`) | `QUALITY.md:121` (KQ20: detector fails when the grading is removed; unfaulted control must pass); `error-is-not-a-verdict.md:20–24` (a positive genuine-rejection control stops an always-error classifier) | Restatement. |
| C2 verdict: pattern emitted AND exit 0 (`tools/round63-c2-counter.py:215–217`, `verdict_fn`) | `error-is-not-a-verdict.md:7–10` ("a declared exit code and the subject's emitted verdict"), `:12–24` (exit status ambiguity), `:26–28` (FAIL literal before abort is not credit); `QUALITY.md:142` (KQ25) | Restatement. |
| C2 sensitivity: strip pattern until absent, flip exit code (`round63-c2-counter.py:234–241`, `is_sensitive`) | `QUALITY.md:509` (KQ101 clause c: mutating the bound capture field flips the computed verdict) | Restatement of KQ101(c). **New:** the exit-code leg (0→1, else→0) and the strip-until-absent loop. |
| C2 four planted defective verdict functions (`round63-c2-counter.py:250–268`, `sensitivity_selftest`) | `QUALITY.md:121` (KQ20); `QUALITY.md:378` (KQ63: "shown able to fail" must exit nonzero on defective input) | Restatement. |
| C2 registry rows: manifest template match, quote ≥8 chars in the frozen prefix, dead-path check, recorded verdict equals computed (`registry/capability-claims-r63.tsv`; `round63-c2-counter.py` docstring) | `QUALITY.md:509` (KQ101 clauses a–d, near verbatim: "a claim-registry row binds a manifest triple, a located quote, and a flip-tested verdict"). | Restatement. The entry should cite KQ101 rather than restate it. |
| C2 reconciler `round42-selfdesc-reconcile.py --repo --tip` reports mismatches=0 | `QUALITY.md:346` (KQ49), `:354` (KQ52: the same command, the same value); `SKILL.md:1433` (round-42 row) | Restatement. Base count 8 is kept on purpose (freeze). |
| C2 control families credited only on a met baseline | `QUALITY.md:121` (KQ20: the unfaulted control must pass on the same rows) | Restatement. |
| Both counters re-run at the landed tip | `QUALITY.md:203` (KQ36), `:362` (KQ54) | Restatement of obligation. See §7.5 on the registry row. |

## 4. SKILL.md decision rows

- **`SKILL.md:129`, `:175`** (HTML page, HTML 404): overlap with `completion_headers`. Restatement at the same principle.
- **`SKILL.md:158–165`** ("Request-time id does not validate the model"): `POST /v1/chat/completions` echoes the file path. The completion route echoes `--alias` (`T:29`, `live.py:393–395`). The two routes differ and neither cross-references the other. No contradiction. A new entry should cite both and name the route.
- **`SKILL.md:261–263`** (common mistake 4: "never use request success as identity evidence") and **`QUALITY.md:9`** (KQ1 rejects a completion success offered as present served-model identity): C1 uses the completion answer, fingerprint and token count to bind a listener. This is adjacent to the boundary, not a duplicate. The entry must say the binding is listener and request-plane evidence, not model identity. Model identity stays with file hashes and `/v1/models`. See §7.3.
- **`SKILL.md:142–156`** (served-id normalization: basename, strip `.gguf`, case-sensitive): `completion_model_id` (`live.py:393–395`) is exact string equality with `--alias`. The name suggests identity normalization and the code does exact echo. A naming hazard, not a duplicate.
- **`SKILL.md:546–548`** (round-16 503 rows: `Loading model` → MODEL_LOADING; any other 503 → FOREIGN_SERVICE) and **`endpoint-health-probe-conventions.md:7–17`** (a 503 can be an admission rejection, not a death verdict): the completion grader grades only status 400/500 on the malformed request (`live.py:470–474`, `T:37–39`). Neither the draft nor the tip says what a 503 on `/v1/completions` means. **Gap, not duplication:** a new entry on the completion error surface would need its own 503 statement grounded in `endpoint-health-probe-conventions.md:9–17` and `:27–66`.
- **`SKILL.md:283–285`** (common mistake 10: "Mistaking a green `check` for coverage"): spirit overlaps C2. Restatement, minor.
- **No completion-request-plane decision row exists at tip** (grep `completion` in SKILL.md hits only :160 and :261–263). A new SKILL decision row for "a completion response fails strict grading" would be new ground, but it would have to avoid restating §1.

## 5. The other three corpus/knowledge files

- **`corpus/knowledge/endpoint-health-probe-conventions.md`** (71 lines at tip): no v2 check overlaps its 503 material. Its correction sections (`:27–71`) show the lane's append-only correction style, relevant to the in-place edits in the draft (§6).
- **`corpus/knowledge/serving-alias-contract.md`** (50 lines at tip): `:12–14` (rule: the served name is the string the client sends and the server echoes, not the checkpoint path), `:18–26` (vLLM first-alias), `:39–43` (path-shaped served name, ja). Overlaps `T:29` and `completion_model_id` on the general rule. The llama.cpp `/v1/completions` echo is observed here, and `:47–50` records that none of its rows was observed against a running server. That observation is genuinely new ground for the entry to add.
- **`corpus/knowledge/error-is-not-a-verdict.md`** (285 lines at tip): `:7–10`, `:12–28`, `:55–77` (Round-23 section, `:70–72`, `:76–77`). This is the strongest pre-existing statement of the C1 and C2 rules. Any new text on credit and exit semantics should cite these lines. The file's `## Round24` region is append-only per `registry/append-only-contract.tsv`, so new prose here goes in a new appended section.
- **`corpus/knowledge/completion-request-plane.md` itself**: `T:24–33` is the observed table; `T:43–44` is stale against the tip tool; `T:47` is superseded in the draft but still present; `T:53–55` lists three v2 names as existing checks; `T:57–58` points to the round-62 counter. Draft `D:58` still points to `round62-c1-counter.py`, which is stale. The draft grades id/created in two places (`D:47–48` superseding `T:47`; `D:89`). Recommendation: one merged table with a v1/v2 column, not a superseded line plus a second table.

Not in the append-only contract: `completion-request-plane.md`, `endpoint-health-probe-conventions.md`, `serving-alias-contract.md`. In-place edits there are allowed, but the draft still leaves the superseded text beside its replacement.

## 6. Genuinely new ground a new entry would add

1. **S527/S528 field-level source facts** for the completion response and the timings object (draft `D:78–81`). Caveat: the raw bytes are **untracked** (`.ufo/waves/round-63/source/server-common.cpp.704366d76` sha256 `b4f4aae7…954d442`, `server-task.cpp.704366d76` sha256 `4c3f413b…233495`; `git ls-files .ufo/waves/round-63/source` is empty). S527 and S528 are absent from tip `corpus/SOURCES.md` (uncommitted +2 lines in the working tree). The entry must not cite them until they are committed.
2. **Exact `application/json` Content-Type on the completion POST** (D:85), with its breadth conflict against `endpoint-identity.md:18` (§7.2).
3. **`usage.prompt_tokens == /tokenize(prompt)` equality** on the pinned fixture (8 = 8, D:92–93). Fixture-limited: the `add_special` rule has no source line.
4. **Fingerprint equality as process binding** (build-level, `T:30`).
5. **Collateral cap** (5 failing checks, 30 for envelope) and `is_hit` set semantics (`round63-c1-counter.py:489–495`). No corpus precedent. It would need its own QUALITY row, or it stays a counter-local rule.
6. **Exit-code leg of sensitivity** (0→1, else→0) and strip-until-absent (`round63-c2-counter.py:234–241`). Extends KQ101(c).
7. **Proxy-honouring urllib finding** (D:106–108). Not in the corpus.
8. **`completion_untruncated`** (D:86). No precedent.

## 7. Tensions to route to the L1 (observations, not verdicts)

1. **KQ39 vs C2 calibration definition.** KQ39 (`QUALITY.md:289`) judges a calibration statement at its writing revision W. True at W but false later is drift, assigned to freshness. C2 counts reconciler mismatches at the tip (`round63-c2-counter.py` `selfdesc_mismatches(tip_tree, …)`; the reconciler docstring says terms are "derived from the tree at --tip"). A head statement true at its writing revision and false at tip would be drift under KQ39 and a mismatch under C2. The L1 should check whether the base 8 include drift-only items.
2. **`completion_headers` breadth.** `endpoint-identity.md:18` (row 6) accepts any non-HTML content type for a 2xx model array. The completion draft (D:85) requires exactly `application/json`. Different routes, not contradictory, but the entry must state the scope or readers will see two rules.
3. **Completion success as listener evidence.** `QUALITY.md:9` (KQ1) and `SKILL.md:261–263` forbid completion success as identity. The C1 receipt uses the completion answer to bind a listener. The entry must scope this to listener and build evidence.
4. **No 503 statement for the completion route** (§4). Grader accepts only 400/500 on the bad request.
5. **KQ54 registry row.** `QUALITY.md:362` (KQ54) requires a five-column instrument-registry row for each round-scoped counter at the landed tip. `git show 03a6a1d8:SKILL.md | grep -c 'round.\?63'` returns 0, so no round-63 registry row exists at tip. Routed for the L1; I did not run `gate-registry-check.py`.
6. **Uncommitted grounding.** The draft cites untracked source bytes (§6.1) and uncommitted SOURCES rows. The tip cannot reproduce the S527/S528 ground.
7. **Count drift.** "Adds nine checks" (D:78) vs six new names and three extended (§2).
8. **Stale tip text.** `T:43–44` vs `tools/kama-completion-live.py:381–388`. `T:57–58` points to the round-62 counter.

## 8. Suggested edits for the L1 (advisory; the seat does not edit)

- Merge D:83–93 and T:24–33 into one table with v1/v2 columns. Drop "adds nine".
- Replace the restated mechanisms (§3) with pointers to KQ21, KQ20, KQ25, KQ52, KQ76, KQ80, KQ101, and `error-is-not-a-verdict.md:7–28, :70–77`. Keep only the deltas: the collateral cap, the exit-code leg, the usage-to-tokenize equality, the content-type rule, the proxy finding.
- Decide whether the collateral cap becomes a QUALITY row (next free ID) or stays counter-local.
- Add an explicit 503 sentence referencing `endpoint-health-probe-conventions.md:9–17`, or state it is not graded.
- Fix `D:58` to `round63-c1-counter.py`.

## 9. What was and was not checked

- Checked: tip blobs for `corpus/knowledge/completion-request-plane.md`, `endpoint-health-probe-conventions.md`, `serving-alias-contract.md`, `error-is-not-a-verdict.md`, `endpoint-identity.md`, `corpus/QUALITY.md`, `SKILL.md`, `SCORECARD.md` (round-63 list only), and the counters and live tool at tip. The round-62 v1 receipt check names. The draft's working-tree lines. The untracked source hashes.
- Not run: no counter, no live server, no `gate-registry-check.py`, no `round42-selfdesc-reconcile.py`, no tests.
- Tools installed: none. Git: read-only (`show`, `grep`, `ls-files`, `rev-parse`). No commits, no lane or fleet edits, no shared-tree writes beyond this report and the evidence file.
- Scratch directory `/fast/scratch/hyaku/kama-r63/w/CN03DuplicationCheck` holds only tip copies made for reading; removed before yield.

Tally: v2 table rows restatement 4 / partial 4 / new 1 of 9; tensions routed 8 (§7).
