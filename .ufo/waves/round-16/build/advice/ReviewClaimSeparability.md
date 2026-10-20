# ReviewClaimSeparability — C1 / C2 causal separability

Seat: read-only reviewer. Nothing installed or updated; no lane gate, harness or test executed
(this item allows none). Every runtime statement below is derived from reading source at the
paths cited; runtime verification remains L1's.

State reviewed (10:19–10:38 -03), because the build wave was landing throughout:

| artifact | state |
|---|---|
| `tools/kama-probe.sh` | frozen-identical `93ee4302…cd64` at 10:19; rewritten twice (10:27 `d0d48d8d…`, 10:34 `6edd3c4c…`) |
| `tests/probe-verdicts/*.json` | 8 families, 64 tests, 15 `MODEL_LOADING` expectations (re-counted at close) |
| `tests/probe-verdicts/check.py` | `fd49ff7c…` |
| `.ufo/waves/round-16/measure.py` | `f74b5a9d…` (gained a `directional` guard at 10:36) |
| `tools/kama-llamacpp-live.py` | `9f0cfba4…` |
| `tests/llamacpp-live/check-receipt.py` | `805c64f8…` |

Every artifact above was rewritten at least once while this review ran; line numbers are as of the
shas in this table and symbol names are the durable citation.

## 1. Separability verdict

**C1 verifies without C2: yes. C2 verifies without C1: yes. Axes are distinct: yes.**

Dependency graph (only directed edges shown; nothing else is shared):

```
C1 gate = check.py -> {8 stub-matrix JSON, kama-probe.sh (before|after), measure.py}
          no llama-server, no registry port, no receipt, no live HTTP
C2 gate = kama-llamacpp-live.py -> {llama-server, GGUF, kama-probe.sh (read-only use), check-receipt.py}
          zero reference to MODEL_LOADING (grep count 0 in both C2 files)
```

- C1's counting command never launches a server: `run_check` is only
  `["python3", str(CHECK), "--probe", str(probe), "--json"]`
  (`kama-shokunin/.ufo/waves/round-16/measure.py:141`).
- C2 never mentions the new verdict: `grep -c MODEL_LOADING` returns 0 for
  `tools/kama-llamacpp-live.py` and `tests/llamacpp-live/check-receipt.py`.
- Axis names: C1 = calibration (catches a lane overreach: a loading model labelled a
  foreign service), C2 = operability as a capability acquisition. C1 works calibration 7,
  the lowest non-retired axis, satisfying the AXES.md obligation
  (`AXES.md` §Working the axes: "At least one claim works the lane's **lowest-scoring
  non-retired axis**").
- [INFERENCE] C2's receipt will almost always show `loading_observed: false` on this host:
  the 260K-parameter / 1.13 MiB `stories260K.gguf` may finish loading before the first 0.5 s poll. That does not
  weaken C2, because the field is recorded, never asserted (see §2).

## 2. Which C2 checks would change if C1 had not landed: none

C2's checks are computed either by the harness's own `urllib` GETs or by probing a *ready*
server; C1 only adds a branch gated on `F_CODE = "503"` before the HTML/FOREIGN fallbacks
(`tools/kama-probe.sh:503-508`, sha `6edd3c4c`), and the ready path begins at `:522`.

| check | would change? | why (evidence) |
|---|---|---|
| `health_ready` | no | harness's own GET; `http_get` at `kama-llamacpp-live.py:265-308` |
| `models_alias_id` | no | parses `/v1/models` body captured by harness (`:399`, check `:719-723`) |
| `models_owned_by_llamacpp` | no | same capture, check `:724-728` |
| `metrics_not_enabled` | no | own GET `/metrics` (`:438`, check `:729-733`) |
| `props_alias` | no | own GET `/props` (`:408-437`, check `:736-740`) |
| `probe_model_ok` | no | probe runs only after `if not ready: raise SetupError` (`:702-703`), probes at `:741`; 2xx model-array path untouched (`kama-probe.sh:522-539`) |
| `probe_mismatch` | no | same 2xx path; `model_matches` at `kama-probe.sh:381-395` |
| `teardown_exited` | no | process returncode (`kama-llamacpp-live.py:484-533`) |
| `teardown_port_closed` | no | connect-refused probe (same function) |

Two receipt *fields* do differ by probe revision, not by judgment: `probes[].result` embeds the
probe JSON, whose `verdict_vocabulary` string changes with C1 (`kama-probe.sh:62`), and whose
`registry` path differs when the frozen copy is used (its `REPO_ROOT` is
`.ufo/waves/round-16`). A receipt sha256 therefore is **not** stable across C1 landing even
though every check outcome is.

## 3. Findings

### F1 — medium — C1 falsifies two "fixed vocabulary" documents; no wave item owns them

`corpus/knowledge/consumer-registry.md:84-85`: "The **live verdict** column uses the binding
vocabulary: `MODEL_OK` | `MODEL_MISMATCH` |" … `NOT_HTTP`. And
`corpus/knowledge/endpoint-identity.md:3`: "The verdict vocabulary is fixed: `MODEL_OK`,
`MODEL_MISMATCH`, `FOREIGN_SERVICE`, `UNAUTHORIZED_SERVICE`, `DEAD`, and `NOT_HTTP`."
After `MODEL_LOADING` enters `VOCAB` (`tools/kama-probe.sh:62`) both sentences are false.
`SKILL.md:12-13` has the same list, but `ScribeSkillSection` owns it; no spec item names either
corpus file (spec grep: only `RevengerRound1Live` mentions `endpoint-identity`, and it is
read-only). Under AXES.md "no axis is harmed", this is a freshness/calibration harm introduced
by C1 unless L1 routes it. Advice: add both lines to the round's doc delta, or have C1's report
name them stale.

### F2 — medium — matrix rationales cite pre-change line numbers that no longer resolve

`tests/probe-verdicts/AuthAndDead.json`, `AuthAndDead.401-authentication-error-envelope`:
"status branch (kama-probe.sh:459) fires before any body check". Line 459 of the *frozen* file
is the 401 branch; in the probe at sha `6edd3c4c` the 401 branch is at `:495-496` and line 459 is
the `Server:` evidence line, just above `case "$F_RC"`. Same drift for `:426-430` (now `:462-466`) and `:436-440`
(now `:472-476`). The oracles themselves remain correct; only the audit trail broke. Because the
matrix claims oracles are "derived from … classify() source", a reader following the citation
now reads the wrong code. Advice: cite branch names, or label the numbers "(frozen snapshot)".
This cannot be caught by the gate — `why` is not graded.

### F3 — closed during review — C1's gate briefly accepted an empty change list

At 10:29 `measure.py:346-350` read `all_changed_loading = all(` … `and all_changed_loading)`;
`all([])` is `True`, so before-red/after-green with *no* resolvable verdict change would have
exited 0 printing `PASS … 0 verdict change(s)`. The version at `f74b5a9d` (10:36) adds a
`directional` conjunct (`measure.py:348-363`): `directional = (bool(loading_names) and
before_failed == loading_names and changed_names == loading_names and set(before_recs) ==
set(after_recs))`. That is non-vacuous in every direction this review could construct — no
loading expectations (`bool(...)` false), a non-loading before-failure, or an unresolvable
record shape (empty `changed` ≠ 15 loading names) all fail. No action needed; keep the guard if
`measure.py` is touched again. [INFERENCE] the fix is the integration step the comment names:
"L1 integration, after ConnectTameshi/ReviewKq19Interplay".

### F4 — low — C2's receipt records the probe's path but not its identity

`tools/kama-llamacpp-live.py:635`: `'probe': str(args.probe),`. Since
`probes[].result` embeds `verdict_vocabulary`, the same command produces different receipt
bytes before and after C1. Advice: add `probe: {path, sha256}` (VerdictHarness already emits
`probe_sha256`, `check.py:486`) and let `check-receipt.py` *print* a mismatch against the
current file rather than fail — failing would make old receipts unrunnable, i.e. would make C2
depend on C1's revision, the opposite of separability.

### F5 — low — `loading_observed` is status-only, not envelope-exact

`kama-llamacpp-live.py:356`: `if (loading_503 is None and result['status'] == 503):` — any 503
on `/health` or `/v1/models` sets `loading_observed` (`:700`). The verbatim body is stored, so
the evidence is there; the *name* overclaims. Advice: C2's report must say "a 503 was observed,
body recorded verbatim" and not "the documented loading envelope was verified"; and never turn
this into a check (see §6).

### F6 — low — `props_alias` documentation anchor does not exist in the pinned README

`kama-llamacpp-live.py:89-91`: "llama.cpp server /props returns model_alias equal to the
--alias value (server_params -> props endpoint, b11755)". The pinned README's `/props`
example and field list (`.ufo/waves/round-16/sources/llama.cpp-704366d/README.md:908-933`) omit
`model_alias`; `grep -rn model_alias` over the four pinned files returns nothing. The field is
real in code: `server-context.cpp:5245` `{ "model_alias", meta.model_name }` (fetched at commit
`704366d76`). So the check is satisfiable, but its stated anchor is not. Advice: anchor to that
source line and add `server-context.cpp` to `sources/pins.json` — otherwise the pinned evidence
set cannot defend C2's `props_alias`.

### F7 — low — one negative control's rationale is imprecise

`tests/probe-verdicts/Overbroad503.json`, `Overbroad503.no-slot-available`: "Real llama.cpp
unavailable_error envelope but message is 'no slot available' (server up, all slots busy)".
At the pinned commit the string requires the request parameter `fail_on_no_slot` and zero idle
slots, on a task-creation path — `server-context.cpp:5393-5396`
`if (!req.get_param("fail_on_no_slot").empty())` … `format_error_response("no slot available", ERROR_TYPE_UNAVAILABLE)`.
The oracle is right (it must stay FOREIGN_SERVICE); the parenthetical is not. Add the source
line so the negative control is auditable.

## 4. Verified positives (so L1 need not re-derive them)

- Frozen identity holds: `frozen/kama-probe-before.sh` sha256 = `93ee4302…cd64` = `manifest.json`
  = `git cat-file blob 20e392ea…:tools/kama-probe.sh` = the working tree file before the 10:27
  edit. `measure.verify_frozen` cannot exit 4 on this repository.
- The new branch is ordered exactly as the engine behaves: 401/403 first (`:495-496`), loading
  (`:503-508`), then HTML/FOREIGN fallbacks (`:510+`). Engine order is state-first, auth-second
  (`server-http.cpp:354` vs `:357`), i.e. a real llama.cpp cannot answer 401 while loading, so
  the probe's reverse order is unreachable-but-harmless; the matrix's `401-carrying-loading-
  envelope` tests the probe invariant, not an engine state.
- Loading ⇒ drift ⇒ exit 2 is structural, not new code: non-MODEL_OK sets `drift=true`
  (`kama-probe.sh:848-849`) and `eval_rows` returns 2 (`:881`).
- `check.py` grades verdict, reason, probe exit **and** the drift invariant
  `drift == (verdict != "MODEL_OK")` (`check.py:340-347`), so C1's "drift true" is a measured
  assertion rather than an implied one; it emits `tests/passes/failures/records`
  (`:488-491`) exactly as `measure.py` reads them.
- `check-receipt.py` is verdict-agnostic: any non-MODEL_OK verdict requires exit 2 and is
  otherwise unconstrained (`:224-230`), and `_probe_expected` tolerates
  `expect|expected|expected_model_id|expect_model` (`:150-151`). No C1 coupling.
- Anti-vacuity controls exist and are strong: 8 ready controls, 8 overbroad-503 negatives,
  7 non-503 statuses, 5 auth-body controls plus 2 dead/raw controls, 8 foreign controls.

## 5. Advice to L1 (cheap, ordered)

1. Run `measure.py` once the build wave is quiescent, and record the probe sha it measured.
   Expect the frozen arm to fail **exactly** 15 rows (LoadingEnvelope 8 + LoadingRace 5 +
   EnvelopeShapes 2) and the repaired arm to fail 0; the `directional:` line must print
   `equal=True`. A before-failure outside those 15 is a matrix fault, not a probe success.
2. **Direct separability control for C2** (one server launch, not a substitute for the primary
   receipt): run `tools/kama-llamacpp-live.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh`
   and then `check-receipt.py` on that receipt. Exit 0 with the *pre-C1* probe is the empirical
   proof that C2 needs no part of C1; attach it beside the primary receipt, labelled as a control.
3. Read the `directional:` line the gate prints; that conjunct is what makes C1 non-vacuous.
   If a later edit drops it, re-apply the equivalent guard (`len(changed) >= 1`).
4. When citing C2, pin the pair (receipt sha256, probe sha256). Never claim a receipt is
   byte-reproducible across C1 landing.
5. Route F1's two corpus lines in the same round, or list them as knowingly stale.
6. If the matrix goes red, attribute before concluding: `check.py` exit 2 is a harness/schema
   error, exit 1 is a probe failure; the per-family table localizes a bad sibling file.
7. Do not run the live harness concurrently with `measure.py`: `closed` mode binds-then-releases
   a port, and a live ephemeral server could take it between release and probe. Serialize.
8. Reject any late change that adds `loading_observed` to `checks[]` — that single edit would
   make C2 fail without C1 and destroy this separability result.

## 6. Residual risk / gaps

- I executed no gate, harness or test; every behavioural claim in §2/§4 is source-derived.
  The live harness's runtime behaviour on b11755 remains unverified by me.
- `loading_observed` may be legitimately false on this host; C2's report must say so.
- The matrix `why` text and its line citations are not machine-checked (F2), so this class of
  drift is invisible to both gates.
- The `directional` guard compares `before_failed == loading_names` exactly, so one flaky
  `closed`-mode row on the frozen arm (port reused between close and probe) fails the whole
  gate and mimics a probe defect. Re-run before attributing in that case.
- [INFERENCE] `data[]` at b11755 carries one entry whose `id` is the alias, so
  `models_alias_id`'s `all(i == alias)` holds; a future build listing aliases as separate
  entries would fail that check for an engine reason, not a lane defect.
- [INFERENCE] `props` and `models` captures are fetched after `/health` 200; because llama.cpp
  gates every non-frontend path on one `is_ready` atomic (`server-http.cpp:308`), no
  loading-window race exists between the ready poll and the probe runs.
