VERDICT: confirm — C1/C2 map onto KQ19/KQ18/KQ17/KQ11/KQ4/KQ6/KQ13 with named gaps; no existing KQ reaches SOURCES registry-cell immutability (KQ7/KQ14 nearest, scope-bound).

# Scout report — which QUALITY.md rows apply to C1, C2, and S041

Read-only seat. Files read: `corpus/QUALITY.md` (whole, `:raw`, 109 lines), `tests/probe-verdicts/check.py`,
`tools/kama-llamacpp-live.py`, `/home/vgpnk/Projects/shokunin/.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`,
`corpus/lessons/round-16.md`, `corpus/lessons/round-16-verifier-spotcheck.md`,
`.ufo/waves/round-16/falsify/advice/MutateHarness.md`, `.ufo/waves/round-17/build/make_spec.py`,
and the three round-17 KQ drafts. No gate, mutant runner, or controls suite was executed.

Line numbers come from the worktree read this session; every cited lane file is unmodified against
master `cff9e62f05aa` (`git status --porcelain` over those paths printed nothing).

## 0. Claim mechanics independently confirmed (so the KQ map is grounded)

- `tests/probe-verdicts/check.py:337` collects five fields — `("verdict", "reason", "drift", "served_model", "evidence")` — but `:340-347` compares only verdict, reason, exit and drift. `served_model` is never graded.
- Route evidence is recorded (`make_handler(test["routes"], test["default_route"], record["requests"])`, `:308`) and used only by the empty-request guard `:323`; no per-row assertion that `GET /v1/models` was requested.
- Malformed output: `:331-332` catches `json.JSONDecodeError, KeyError, IndexError, TypeError`, but `record[key] = row.get(key)` (`:337-338`) raises `AttributeError` when `rows[0]` is a list/string/number; `grade()` catches only `OSError` (`:349`) and `main()` catches only `HarnessError` (`:478-479`), so the traceback escapes (exit 1, not 2). The lesson records this: `corpus/lessons/round-16.md:157-158` "malformed probe output ends in a traceback (exit 1, not 2)".
- The matrix cannot encode an expected `served_model`: `check.py:56` `EXPECTED_KEYS = {"verdict", "reason", "exit"}`; and the nine files are pinned — `.ufo/waves/round-16/measure.py:281` `EXPECTED_MATRIX_SHA256 = "bf9068d89e4cb8a0…"`.
- Live tool: `health_ready` grades only `health_status == 200` (`tools/kama-llamacpp-live.py:938-940`); `teardown_exited` passes on `returncode is not None` (`:1024-1028`); `teardown_port_closed` reads only `port_refuses` (`:1029-1032`); `loading_envelope_exact` is recorded at `:922` and its helper ends `Not a check.` (`:176`). A teardown exception becomes `{'error': …}`, then `['returncode']` at `:1026-1027` raises `KeyError` inside the `finally`, before the receipt write at `:1049`.
- S041: first committed at `b8e485c`; `git show b8e485c:corpus/SOURCES.md` has anchor "port 32845, 10 checks" while the current row (`corpus/SOURCES.md:53`) has "port 37527, tool sha256 b8c5e8d4…"; `teaches` also differs. The lesson discloses it (`corpus/lessons/round-16.md:147-149`).

## 1. C1 — gate grading claims, fault controls, mutants: existing rows that apply

| KQ (QUALITY.md line) | Clause that applies (quote) | What it does for C1 | What it leaves open |
|---|---|---|---|
| KQ19 (109) | "verdict, reason, exit and drift are all graded" | It is the criterion the round-16 matrix was admitted under (`corpus/lessons/round-16.md:46` "admit (KQ19)"); it requires the frozen red arm and literal near-misses ("a green run lacks the frozen red arm or the near-misses"). | It grades the *documentation* of grading, not load-bearing: round 16 satisfied it while all five grading-weakening mutants survived (`MutateHarness.md` §Result). It omits `served_model` and route-match entirely, so it cannot be cited for the new invariants. |
| KQ18 (87) | "demonstrated by a discriminating red/green pair through the actual runner CLI" | Supplies the frozen-red/current-green counting shape and the no-edit rule ("The frozen original stays byte-intact as the red control; only the guard changes"). | Scoped to a corpus validator's rejection promise and one guard; no per-field mutation, no fault-injected subject. |
| KQ11 (38) | "Missing-field and altered-prefix controls must fail before the repair counts." | Direct precedent that the fault-control suite must be red-capable before the repair is admitted. | Scoped to legacy provenance supplements, not gate grading. |
| KQ17 (72) | "Malformed, missing, duplicate or unavailable evidence fails closed to `unknown`/`invalid_input` (exit 2)" | Fail-closed precedent for malformed probe output. | Scoped to classifier input evidence, not a harness parsing its subject's stdout; no explicit traceback ban. Also supplies count discipline: "a count is admitted only under its own stated anchor condition". |
| KQ4 (12) | "the exact command/exit distinguishes drift from probe failure" | Requires the harness exit to separate subject failure from harness fault; also "fixtures are called real-runtime integration" rejects inflating a matrix pass. | No per-named-field falsifiability. |
| KQ15 (49) / KQ16 (61) | "SHA-256 digest integrity against a pinned manifest naming the snapshot hash, source commit and source path"; "Corrections land as a new dated snapshot plus its own manifest" | Governs the frozen/current arms' provenance and prevents a correction by rewriting the frozen bytes. | Identity/provenance only; they do not make any comparison load-bearing. KQ16 still bounds the claim: a textual gate does not establish semantic admission. |
| KQ12 (39) | "Claims identify their fixed denominator and prior overlapping coverage." | Applies to the mutant census: fixed mutant set as denominator; a `site_missing` mutant must be could-not-evaluate, not silently survivor or killed. | Axis/coverage framing only. |
| KQ9 (31), KQ10 (32) | "count first, then read"; "inside the task's declared scope" | Counting the nine matrices / only L1 runs the counting command. | Method-level. |
| KQ14 (41) | "human/source review establishes the claim's content" | A killed-mutant count is detector sensitivity, not proof the probe is right. | Boundary only. |
| Review boundary (17) | "Author and parent-dispatched advisor agreement are not an outside spot-check." | A detector written by the gate's author is author-recorded until non-author review. | The round-17 fault suite/mutant runner are self-authored (build spec `SelfAuthoredDetectors` already attacks this). |

## 2. C1 — the gap a new row (KQ20) must close

1. **Admission must be load-bearing, per named field.** A documented grading is admitted only when removing that one comparison changes an observed outcome (mutant killed: per-row field, pass/fail vector, or exit). Pair totals are exactly the failed detector: frozen 55/17 vs current 72/0 left `ignore-reason`, `ignore-exit`, `ignore-drift`, `casefold-verdict` and `timeout-pass` alive (`MutateHarness.md` table). No existing row forbids accepting that pair.
2. **Two probe-contract invariants no KQ covers.** (a) `served_model` derived from each row's literal stub `routes` plus `kama-probe.sh` classify() semantics; (b) for every stub-mode row, the stub's recorded requests include `GET /v1/models`. Because the nine matrices are byte-pinned and `EXPECTED_KEYS` has no `served_model`, the expected value must be derived, never added as a new expected key.
3. **Malformed subject output is a recorded per-row failure, never a traceback.** The fault standard must be: exit 1 **and** parseable JSON **and** the faulted row `passed: false`; a traceback is neither pass nor detection (this is also the fault-controls definition in `make_spec.py` C1FaultControls).
4. **Fault wrappers are the only admissible input space** for fields a correct probe never gets wrong (case, timeout, malformed shapes), because the matrices may not be edited. This is the structural reason the row must require both mutants and fault-injected subjects.
5. **Counting discipline.** Fixed mutant set (M1–M5 from round 16, M6–M8 only where the repaired checker has the site), `site_missing` reported as could-not-evaluate, surviving/accepted counts verbatim for frozen and current, detector pinned by digest, no frozen fixture or matrix byte edited.
6. **Do not over-admit.** The row must not claim the timeout path is covered until a slow wrapper exercises it (round-16 limitation: "the timeout exception path was not exercised"), and must not turn a killed-mutant count into semantic admission (KQ16/KQ14).

## 3. C2 — fail-capable live checks: existing rows that apply

| KQ (QUALITY.md line) | Clause that applies (quote) | What it does for C2 | What it leaves open |
|---|---|---|---|
| KQ19 (109) | "names the pinned upstream code that emits the state" | The documented ready/loading states and exact triple are already settled for the probe matrix; the live tool's DOC copies them (`kama-llamacpp-live.py:77-82`). | It is stub/probe-CLI scoped ("shown by a literal stub matrix run through the probe CLI"); a live receipt's checks are ungoverned. Its exact-body discipline is what `health_ready` fails to apply. |
| KQ6 (28) | "cites an opened `SOURCES.md` row whose tier fits that scope" | Makes the new S042–S045 rows (llama.cpp `/health` ready handler, signal/shutdown path, `subprocess.Popen.returncode`) mandatory and tier-scoped. | Governs the statement, not the predicate: no row requires the pass condition to encode the cited exact value (`{"status":"ok"}`) rather than a proxy (status 200). |
| KQ4 (12) | "the exact command/exit distinguishes drift from probe failure" | Bounds what a real-runtime receipt may claim and requires exit classes (subject failure vs internal fault). | No per-check falsifiability. |
| KQ18 (87) | "demonstrated by a discriminating red/green pair through the actual runner CLI" | Structural ancestor of `controls.py`: accepted-bad before → after, frozen control intact. | Corpus-validator scope; the live harness consumes real subject responses. |
| KQ11 (38) | "Missing-field and altered-prefix controls must fail before the repair counts." | Applies directly to the controls acceptance ("accepted-bad == 0 before the repair counts"). | Provenance-supplement scope. |
| KQ17 (72) | "Malformed … evidence fails closed"; "a selected higher-precedence could-not-evaluate finding does not erase a count" | Fail-closed precedent for the receipt-on-internal-fault requirement and for separating a check's result from the receipt's verdict. | Offline classifier that writes only stdout; the live harness's fault path (no receipt when `finally` raises) is uncovered. |
| KQ13 (40) | "available inventory, loaded residency, advertised identity and inference readiness are separate propositions" | Prevents a 200 body, a `/health` answer, or a `/v1/models` id from standing in for readiness. | Separation only; no falsifiability. |
| KQ1 (9) | "A current endpoint claim includes the actual authorized probe command, sampled time/revision, complete verdict and real exit code"; rejects "A configured URL, listener, `/health` answer … as present served-model identity" | Bounds the receipt as an endpoint claim and requires the real exit code. | Claim scope, not check strength. |
| KQ12 (39), KQ14 (41) | fixed denominator; human/source review | Control inventory as denominator; a green control suite is not semantic proof of runtime health. | Framing only. |

## 4. C2 — the gap a new row (KQ21) must close

1. **Subject-behaviour control per named check, retained with its failing result.** Each live check must be flipped by a control in which the subject misbehaves: `health_ready` on 200 `{"status":"degraded"}`; `teardown_graceful` on self-exit rc 0 with no signal sent, ignored SIGTERM→SIGKILL −9, and nonzero exit on SIGTERM; `teardown_port_closed` only when child ownership was proven earlier; `loading_envelope_graded` when the observed body is non-exact. The check must fail *in the same harness*, and the control plus its failing receipt/gate result must be retained.
2. **A classification obligation no existing KQ has.** Every check carries one label by what its failure can come from — `subject`, `input-integrity`, `harness-integrity`. Only `subject` checks count toward a subject claim; a check no control flips is labelled, never counted. Today `model_unchanged` (`tools/kama-llamacpp-live.py:1033-1036`) and post-reap `teardown_port_closed` (`:1029-1032`) are counted as checks but cannot fail for subject behaviour.
3. **A captured field no check grades is observation-only.** `loading_envelope_exact` is exactly this today (`tools/kama-llamacpp-live.py:922` record; `:176` "Not a check."); it may not support a PASS/VALID claim.
4. **Fault path.** An internal exception in setup/readiness/teardown/receipt-write still writes a receipt recording `setup_error` and exits 2. Today a teardown error dict → `KeyError('returncode')` at `tools/kama-llamacpp-live.py:1026-1027` escapes the `finally` before the write at `:1049` — the round-16 review recorded `receipt_written False`.
5. **No-harm and counting.** v1 receipts (`round-16/live/receipt.json`, `receipt-frozen-probe.json`) must still validate unchanged; the frozen tool+gate is the red arm; `accepted_bad` before → after is the count; controls never on registered ports.

## 5. S041 in-place SOURCES edit — which KQ should have caught it

Contract rule: `/home/vgpnk/Projects/shokunin/.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:49` — "Only `status`, `recheck` and `used-by` change in place". The amendment changed `anchor` and `teaches` (values above), disclosed at `corpus/lessons/round-16.md:147-149`; routed as defect 3 at `corpus/lessons/round-16-verifier-spotcheck.md:184` — "Contract rule 2 lets only `status`/`recheck`/`used-by` change in place".

Candidate rows, in order of fit:

| KQ (line) | Why it could have fired | Why it did not / did not reach |
|---|---|---|
| **KQ7 (29)** | The only explicit append-only correction rule: "with every correction appended at the end of its file"; rejects "a dated line is rewritten". | Its subject is a correction round's stale-anchor ledger and file-end appends; a registry row is not "a dated line", and it names no cell allowlist. |
| **KQ14 (41)** | Explicitly preserves that rule: "KQ14 (supersedes KQ7's sufficiency, preserves its append-only rule)". | Ledger-semantics row; adds no registry-cell obligation. |
| KQ3 (11) | Generic byte preservation: "Corrections preserve old corpus bytes." | No cell allowlist and no mechanical check; its reject column is about stale anchors/pids. |
| KQ11 (38) | "preserve the original byte prefix" | Scoped to legacy provenance supplements (metadata review vs live revalidation), not registry rows. |
| KQ16 (61) | Append-only correction mechanics: "Corrections land as a new dated snapshot plus its own manifest" | Frozen snapshot/receipt scope only. |
| KQ6 (28) | Points at `SOURCES.md` rows | Citation/tier only; constrains citing a row, not editing it. |

**Answer:** [INFERENCE] KQ7, as preserved by KQ14, is the row that *should* have caught the S041 edit — it is the lane's only append-only criterion, and rule 2 is the same obligation in registry form. In practice no KQ fired, because KQ7/KQ14 are correction-round and file-end scoped and neither names `corpus/SOURCES.md` registry cells or the `status`/`recheck`/`used-by` allowlist. KQ3 is a weaker secondary ("Corrections preserve old corpus bytes") that could have been read to apply, but it requires no cell-level check either.

**Gap a registry rule (KQ22) must close:** immutable cells (`id, source, kind, tier, scope, anchor, teaches, opened`) byte-identical from first commit; allowlist `status`/`recheck`/`used-by` with old→new logging; a regenerated artefact takes a `supersedes S0NN —` row; and a fail-capable round-end detector whose base is the registry's first commit `1e41928` (verified: `git log --diff-filter=A -- corpus/SOURCES.md` → `1e41928 round-10: sources registry (30 rows)…`), because `cff9e62` already contains the S041 amendment. Historical flags (S041 at `ccc4bb3`) must be a named exception list, and the exception list itself needs non-author review or it can absorb any violation.

## 6. Draft reconciliation (advice, not admission)

The build already drafted the three rows: `.ufo/waves/round-17/build/drafts/quality-kq20.md`, `quality-kq21.md`, `quality-kq22.md` (spec prompts at `.ufo/waves/round-17/build/make_spec.py:238-240`). My derived gaps are closed by their wording: KQ20 (a)–(d) covers per-field mutants, single-field fault subjects, frozen/current counts and digest-pinned detectors; KQ21 covers subject controls, the three labels, observation-only fields and the fault receipt; KQ22 covers immutable cells, the `1e41928` base and the named historical exception. Residual notes for L1, not defects I can prove:

- KQ20: the pinned-matrix consequence is only implicit. L1 should state that `served_model` is derived from `routes` + probe contract because `EXPECTED_KEYS` (`check.py:56`) admits no new expected key and `EXPECTED_MATRIX_SHA256` pins the set.
- KQ21: labels have no schema field today (the draft says so: `check-receipt.py:53-63` has ten IDs and no label). If v2 does not carry labels, the rule is prose-only.
- KQ22: the named-exception mechanism is the one place a violation can be admitted by naming it; its exhaustiveness needs the same non-author review the "Review boundary" (`QUALITY.md:17`) demands.

## Limitations

- Read-only; I ran no gate, mutant runner, controls suite, or probe, and started no server. All code claims are from reading committed bytes at the lane tip, not from execution.
- I did not open the llama.cpp sources or `tools/kama-probe.sh` classify() semantics; the `served_model` derivation is the C1HarnessGrading executor's obligation (the spec tells it to read classify() and report violations rather than weaken).
- `EXPECTED_MATRIX_SHA256` was read from `measure.py:281`, not recomputed.
- Drafts are author-written advice; under `QUALITY.md:17` they are not an outside spot-check.
- Items marked [INFERENCE] are my reading, not an observed test.

## Installs

None. No tool was installed or updated; only `git` read-only commands, `grep`, `sed`, `nl`, and `python3 -c` (stdlib JSON) were used.
