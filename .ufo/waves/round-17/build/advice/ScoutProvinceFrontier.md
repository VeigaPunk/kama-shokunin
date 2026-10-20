VERDICT: n/a — mapping seat: C1 advances no §Frontier bullet; C2 moves only the round-16 tail item at README:219-221, not the four bullets at 68-78.

Read-only at lane tip `cff9e62f05aa7cfb9059444f62eb787100719713`; `PROVINCE.md` sha256 `04d4f684…`, `corpus/README.md` sha256 `0f3a2239…`, both clean in `git status`. No measurement, no gate, no server, no install.

# Answer in one table

| Row | Lines | C1 | C2 | Text that moves |
|---|---|---|---|---|
| §Frontier F1, still-live source anchors | README:68-70 | no | method only: adds new anchors, corrects none | none in 68-70 |
| §Frontier F2, declared-vs-served context | README:71-72 | no | no | none; K05 returns open |
| §Frontier F3, non-author spot-check | README:73-74 | no | no | none; must be declared untouched |
| §Frontier F4, operator/integrator prerequisites | README:75-78 | no | touches receipt leg, closes nothing | none in 75-78; stated in new tail |
| `probe-mutation-matrix` coverage row | README:40 | no — different mutation target | no | none; must not be re-pointed |
| `llamacpp-loading-lifecycle` coverage row | README:206 | no | yes, append correction | row bytes unchanged |
| round-16 frontier disposition | README:217-224 | no | yes, one item changes status | superseded by appended text |
| admission block | README:22-23 | no | touches receipt leg only | appended clarification at most |
| known gap, llama.cpp only | README:60-63 | no | no | none |
| surface rows | PROVINCE:10-15 | referent 12-13 | referent 13 | no edit; append note |
| round-16 fixture note | PROVINCE:55-69 | no | yes, v1→v2 facts | append after 69 |
| L0 fixture question | PROVINCE:61-64 | no | no | unchanged |

# A. README §Frontier (66-78): no bullet moves

- F1 README:68-69 — "Correct still-live source anchors through new cited correction entries; historical corpus samples stay immutable." C1 cites no source anchor. C2 opens new anchors (llama.cpp `704366d76` `/health` handler + shutdown path; Python `subprocess.Popen.returncode`) but corrects no *still-live* anchor, so it applies the rule without advancing the debt. [INFERENCE] if the handler body proves narrower than the doc, that would be a genuine F1 correction — see limits.
- F2 README:71-72 — "Reconcile declared-vs-served context size only as a separate feature move when an authorized serving runtime permits". Neither claim compares context. `tools/kama-llamacpp-live.py` records `/props` fields (`props_alias`, line 961-968) and a model hash, never `n_ctx`. K05 must return open in the round-17 disposition.
- F3 README:73-74 — "Non-author spot-check of at least one admitted and one rejected candidate; unavailable in round 5". Neither claim is non-author. The C1 mutant runner and C2 `controls.py` are author-built fault controls; the only non-author artifacts are `corpus/lessons/round-16-verifier-spotcheck.md:187` ("Five `check.py` harness mutants survive. `served_model` is not graded") and `…:187` route-match debt, which are *reports of debt*, not fresh independent review. Do not claim F3.
- F4 README:75-77 — "Operator/integrator prerequisites, not corpus expansion: authorized native role bindings, a real receipt binding, serving-runtime disposition". C2 makes a receipt *re-derivable* (`tests/llamacpp-live/check-receipt.py:2` is "Independent validator for a kama-llamacpp-live/v1 receipt"; v2 must dispatch on version and still accept v1 per `:45` `RECEIPT_SCHEMA = "kama-llamacpp-live/v1"`). That is the precondition for a binding, not the binding. README:22-23 — "Round admission is blocked by missing native role routes and receipt bindings" — stays true on the role-routes leg, and PROVINCE:61-63 "only for the process this tool started, **pending L0 ratification**" is unchanged.

# B. Coverage map and tail

- README:40 indexes the wrong lesson for C1 — "mutation classes the probe must detect + the classes it misses". `corpus/lessons/probe-mutation-matrix.md` contains zero mentions of `harness`, `survive`, `check.py` or `detector` (grep count 0), so C1's mutants (which corrupt check.py, the detector, not the probe) must not be filed there. Text at 40 does not move.
- README:206 — "…the probe's `MODEL_LOADING` mapping and limits, one live lane-owned run". C2 gives a second, v2-graded run and supersedes the limits enumerated at `corpus/knowledge/llamacpp-loading-lifecycle.md:144-148` ("`health_ready` checks the status only, not the `{"status":"ok"}` body"; "`loading_envelope_exact` is recorded, not graded"). Per `corpus/QUALITY.md:29` ("with every correction appended at the end of its file"; reject when "a dated line is rewritten"), the row and the lesson stay byte-identical and the correction appends inside the knowledge entry.
- README:207 — "C1/C2 gate decisions, mined mistake M1 (round-1 overreach)". Round-17 needs its own row; round-16's row is not edited.
- README:209-215 — "The `/health` 503 body was already held at `knowledge/runtime-health-surface-matrix.md:14`". The matrix body reads "200 `{"status": "ok"}` when loaded". C2's health predicate must match the tool's own DOC at `tools/kama-llamacpp-live.py:78-80` ("GET /health returns 200 `{"status":"ok"}` once the model is loaded"). If the `704366d76` handler emits more than that, the matrix line needs an appended correction and F1 becomes genuinely touched. [INFERENCE] pending the llama-health-handler seat.
- README:219-221 — "Still open: live grading of a loading server by the receipt". This is the one string whose *status* C2 changes. Today no check consumes the envelope: `tools/kama-llamacpp-live.py:922` computes it, `:848` initialises it, and no `_check` names it; the falsify table at `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:55` records "**no check consumes it**", with control `bl` (line 26) showing `loading_observed true` and a non-exact envelope still at 10/10. After v2 the sentence becomes "graded when observed; catching the real window remains open" — appended, not rewritten.
- README:223-224 — "A lane-owned fixture was sampled; nothing was restored." Still exactly true; C1/C2 add no endpoint.
- README:60-63 — "Real-runtime reconciliation is proven for llama.cpp only." Unchanged; round 17 remains llama.cpp-only and the sample is not a consumer probe.

# C. PROVINCE.md

- Lines 10-15 are province declarations. C1's nearest referents are line 12 "| served-model-id reconciliation | `GET /v1/models` vs `--alias` vs the configured model id |" and line 13 "| liveness/readiness probe conventions | `/health`, `/props`, `/slots` |"; C2's is line 13. C1 grading `served_model` plus stub route-match makes the probe's *own* contract load-bearing, which is a new artifact — not a change to what kama owns. Recommend: do not edit 10-15.
- Line 55-56 "**Round-16 note — lane-owned live fixture (2026-10-20).** `tools/kama-llamacpp-live.py` starts one llama-server child" and line 60 "tears it down in the same run" remain true, but v2 makes the teardown *graded*: `:1025-1026` today passes on `receipt['teardown']['returncode'] is not None` alone; `:1030-1031` grades `port_refuses is True`; `:938` grades `health_status == 200` only. The falsify table (`ReviewLiveHarnessCode.md:45,52,53`) records health "**no, in a completed run**; body ignored", teardown "**no** for any userspace behavior", port-closed "**vacuous on failed runs**". Those three predicate changes plus "receipt always written, exit 2" are new facts that belong in a round-17 note appended after line 69 — not as edits to 55-69.
- Line 65-66 "changes no registered row: the three consumers stay `DEAD`." C2's control suite starts only fake servers on ephemeral loopback; this sentence survives unchanged and should be restated in the new note.
- PROVINCE has no Frontier section and no mention of `receipt`, `probe-verdict`, `mutant` or `calibrat` (grep counts 0). So C1 has *no* existing PROVINCE text to move; any PROVINCE prose for C1 is new, and its natural home is the corpus lesson row, not the province.

# Candidate text (append-only; no existing line moves)

D1 — `corpus/README.md`, insert after line 228:

```
## Round-17 calibration gate and fail-capable lifecycle receipt (2026-10-20)

| Entry | Covers | Round |
|---|---|---|
| `lessons/round-17.md` | probe-verdict gate calibration (`served_model` and stub route-match graded from each row's literal stub routes; malformed probe output recorded per row), fault controls, `check.py` surviving-mutant count before→after; `kama-llamacpp-live/v2` fail-capable checks and the accepted-bad control count | 17 |

Frontier disposition: no §Frontier bullet (lines 68-78) moves. Line 68's
anchor rule was applied, not advanced — round 17 adds new anchors and corrects
no still-live one. Line 71's context-size move is untouched (K05 open). Line
73's non-author spot-check is not supplied by the fault controls or the mutant
runner, both author-built, so discernment stays unverified. Line 75's
receipt-binding leg is nearer (the v2 receipt is re-derivable and v1 still
validates), but admission stays blocked at lines 22-23 by missing native role
routes.

The line-219 item changes status only: the receipt now grades
`loading_envelope_exact` whenever `loading_observed` is true, so a non-exact
envelope cannot pass. Catching a real load window (the model loads in
milliseconds) remains open, as do router mode and sleep, other engines, K05,
and the registered consumers, which stay `DEAD`. The nine
`tests/probe-verdicts/*.json` files are byte-identical to round 16; the
72-row / 17-loading breadth is unchanged and no new `*.json` was added.
```

D2 — `corpus/knowledge/llamacpp-loading-lifecycle.md`, append after line 148:

```
*[correction 2026-10-20 (round 17, C2): lines 144-148 describe
`kama-llamacpp-live/v1` and are superseded by `kama-llamacpp-live/v2`:
`health_ready` requires the documented `{"status":"ok"}` body, not status 200
alone; `teardown_exited` requires harness-initiated SIGTERM, no SIGKILL and the
documented graceful exit status; `teardown_port_closed` is graded only after
ownership of the port by the child was proven; `loading_envelope_exact` is
graded whenever `loading_observed` is true; an internal fault still writes a
receipt and exits 2. `tests/llamacpp-live/check-receipt.py` re-derives every v2
check and still validates v1 receipts unchanged.]*
```

D3 — `PROVINCE.md`, append after line 69:

```
**Round-17 note — calibration gate and fail-capable lifecycle receipt (2026-10-20).**
`tests/probe-verdicts/check.py` grades two probe-contract invariants per stub
row beyond verdict/reason/exit/drift: the `served_model` the stub's
`/v1/models` body implies, and that the probe issued `GET /v1/models`.
Malformed probe output is recorded as a per-row failure, not a traceback.
`tools/kama-llamacpp-live.py` moves to receipt `kama-llamacpp-live/v2`: health
requires the documented ready body; teardown is graded as harness-initiated
SIGTERM with no SIGKILL and the documented exit status; port-closed is graded
only after ownership was proven; the loading envelope is graded when observed;
an internal fault writes a receipt and exits 2. `tests/llamacpp-live/check-receipt.py`
re-derives every v2 check and still validates v1. This adds no surface,
endpoint or registered-consumer sample: the three consumers stay `DEAD`
(lines 65-66) and the L0 question at lines 61-64 is unchanged.
```

# Do-not-write list

1. Do not rewrite README:66-78, 40, 206, 219-224 or 22-23 (KQ7 at `corpus/QUALITY.md:29`). All deltas are appends.
2. Do not claim matrix growth or breadth: nine `tests/probe-verdicts/*.json` stay byte-identical, no new `*.json`, 72 rows / 17 loading fixed (`corpus/lessons/round-16-verifier-spotcheck.md:165` — "C1: frozen 55/17 → 72/0 on a 72-row, 17-loading matrix").
3. Do not file C1 under README:40 / `probe-mutation-matrix.md`.
4. Do not claim F3, F4 or any §Frontier bullet advanced or closed, and do not claim round-16 routed defect 6 is independently retested — the spotcheck's "Five `check.py` harness mutants survive" is a dated record, and round 17's count is author-run.
5. Do not edit PROVINCE:10-15 or 55-69; append after 69.
6. Do not describe the receipt as a "real receipt binding"; the receipt is re-derivable, the binding is not made.

# Limitations

- Line numbers are from tip `cff9e62f`; both docs verified clean before read.
- I did not open the llama.cpp `704366d76` `/health` handler source (owned by `KamaR17.ScoutLlamaHealthHandler-2`). Whether the ready body is exactly `{"status":"ok"}` at that commit — and therefore whether D2's "documented body" needs a corpus correction at `runtime-health-surface-matrix.md:14` — is unverified here. [INFERENCE]
- I did not read `tests/probe-verdicts/fault-controls.py` or `.ufo/waves/round-17/c1/mutants.py`: neither exists at tip, so the before/after mutant count cannot be pinned by this seat. Only the before state is grounded: five mutants SURVIVED per `.ufo/waves/round-16/falsify/advice/MutateHarness.md:24-28`.
- C1's malformed-row traceback path is grounded statically: `check.py:332` catches `JSONDecodeError/KeyError/IndexError/TypeError` around `doc["rows"][0]`, but `:338` then calls `row.get(key)` outside that guard, so a non-object `rows[0]` raises uncaught `AttributeError`. Not executed.
- `PROVINCE.md` and `corpus/README.md` carry no round-17 text yet (grep `probe-verdict`/`mutant` = 0 in both), so "what would move" is a proposal, not a diff.

# Installs

None. No pacman, uv, npm or binary install was attempted or needed.
