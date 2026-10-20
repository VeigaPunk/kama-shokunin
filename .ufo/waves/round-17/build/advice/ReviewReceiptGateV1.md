VERDICT: partial — the gate never trusts `passed`, but 7 of 10 checks re-read a producer-written scalar or the probe's own verdict row, and all four C2 forged receipts (degraded health, self-exit, SIGKILL, non-exact loading) are accepted with exit 0.

# C2 "before": `tests/llamacpp-live/check-receipt.py` v1

Revision reviewed: 1147 lines, sha256
`6b9576a13dde1872977a6af4547599a75cf484f37fe6fe0f4f5557349b09ced6` — the same gate
sha the round-16 review (`round-16/falsify/advice/ReviewLiveHarnessCode.md:10-11`)
quoted, so these findings are current, not stale. Producer reviewed for the
predicates it emits: `tools/kama-llamacpp-live.py`, sha256
`b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4`.

Revision note (in flux). While this review was being written, the lane copy
moved from the v1 gate to a partial v2 twice: sha256
`5ed600b2cf79b38050ea6e05f220a31f92420a182f7cbdc582d592918b66311d` (1169
lines, 12:21) and
`65ac08b7abe1f5d763152c5b06f1ac3b19c807d9a788f18f9d3750c57c6bff16` (1189
lines, 12:22). The reviewed baseline stays the frozen v1 copy
(`.ufo/waves/round-17/frozen/tests_llamacpp-live_check-receipt.py`, sha256
`6b9576a1…`), byte-identical to what I read and the C2 "before" artifact. In
both snapshots the v2 ids exist only in the docstring/constants and the
schema/required-set branch (`check-receipt.py:205`, `:646`); there is no
`teardown_graceful`, `loading_envelope_graded`, or health-body re-derivation
block. Measured on both: v2-shaped receipts with a degraded health body,
self-exit rc 0, SIGKILL -9, or a non-exact envelope are still `ACCEPTED []`,
and both new checks pass with `observed: {}`. This is mid-flight, not a finding
about the landed v2 — re-run the four controls after the edit settles.

Every `check-receipt.py` line number below refers to that frozen v1 copy (the
lane file has shifted since); producer line numbers are from
`tools/kama-llamacpp-live.py` sha `b8c5e8d4…`, unchanged during this review.

## Method (read-only; nothing written except this file)

I imported the gate with `sys.dont_write_bytecode = True` and called
`validate()` in memory on its own `_selftest_receipt()` literal
(`check-receipt.py:846-988`), then on one-forgery-at-a-time mutations of that
literal. No gate CLI, no `--selftest`, no `llama-server`, no lane measurement,
no port bound. This is equivalent to receipt-level fake-server evidence because
`validate()` does no I/O: `hashlib` appears only at `check-receipt.py:37` and
`:72` (the install-tree digest), so every predicate reads receipt JSON only.

## Does each check re-derive stored evidence, or trust `passed`?

`passed` itself is not trusted: `check-receipt.py:608-611` requires a bool and
rejects `false`, then every check is re-derived. The header claim at `:16-17`
(`Every claim is re-derived from the stored evidence; a bare` / `"passed": true
is never trusted.`) is literally true for `passed`, but it overstates the rest:
for `teardown_exited`, `teardown_port_closed`, and the loading envelope the
"re-derivation" is the producer's own one-line predicate. The weakness is
*what* is re-derived. Only two checks re-parse a captured HTTP body; one
compares the producer's extracted object; the remaining seven re-read one
producer-written scalar or the probe's own verdict row.

| # | check | gate lines | what the gate re-derives | fails for subject misbehaviour? |
|---|---|---|---|---|
| 1 | `health_ready` | 628-637 | `captures.health.status == 200` only; `health.body` never read | no — 200 + `{"status":"degraded"}` passes |
| 2 | `models_alias_id` | 639-655 | re-parses `captures.models.body`, `data[].id` | yes |
| 3 | `models_owned_by_llamacpp` | 657-668 | re-parses the same body, `data[].owned_by` | yes |
| 4 | `metrics_not_enabled` | 670-680 | `captures.metrics.status` (producer stores no body, `kama-llamacpp-live.py:611`) | yes |
| 5 | `props_alias` | 682-696 | `captures.props.fields` (producer's extracted dict, no body, `:581`) | yes, but not independently re-derivable |
| 6 | `probe_model_ok` | 698-719 | probe row `verdict`/`reason`, probe `exit`, `summary.exit`, `declared` | only if the probe actually read the server; gate cannot tell |
| 7 | `probe_mismatch` | 721-743 | same self-report fields | yes for a probe that always says OK |
| 8 | `teardown_exited` | 745-756 | `teardown.returncode is not None` | **no** — any rc, including self-exit 0 and SIGKILL -9 |
| 9 | `teardown_port_closed` | 758-769 | `teardown.port_refuses is True` | **no** — vacuous; no prior-listener evidence is required |
| 10 | `model_unchanged` | 771-785 | receipt `model.sha256 == model_sha256_post` | **no** for subject behaviour (digests not recomputed) |
| — | loading envelope | 391-432 | not a check; only `lef == want_lef` consistency | **no** — `false` is accepted |

`REQUIRED_CHECKS` (`:53-64`) names exactly these ten, and `:614-617` rejects any
extra id, so v1 has no slot for a loading-envelope verdict at all.

## Forged receipts the v1 gate accepts (measured, `validate()` → `[]`)

Every row below returned `ACCEPTED []` (empty problem list) at gate sha
`6b9576a1…`. "Producer evidence" names the round-16 fake-server run that
already emitted this shape (`ReviewLiveHarnessCode.md` run table), so these are
reachable, not hypothetical.

| control | receipt mutation | round-16 producer evidence | predicate the gate lacks |
|---|---|---|---|
| H-health | `captures.health.body = {"status":"degraded"}`, status 200 | run `hb` (200, degraded body, 10/10) | body exactness at 628-637 |
| H-absent | `captures.health.body` deleted, status 200 | — | body presence |
| T-selfexit | `teardown.returncode 0`, `sigterm_sent false`, `sigkill_sent false` | run `se` (self-exit rc 0, sigterm_sent false) | causation at 745-756 |
| T-sigkill | `teardown.returncode -9`, `sigkill_sent true` | run `kill` (SIGKILL, 10.1 s, passed) | no-SIGKILL at 745-756 |
| T-anyrc | `teardown.returncode 8` | — | documented exit-set at 745-756 |
| T-minimal | `teardown = {"returncode":0,"port_refuses":true}` | — | `sigterm_sent`/`sigkill_sent` presence (573-586 type-checks only `returncode`/`port_refuses`) |
| L-nonExact | non-exact 503 body + `loading_envelope_exact false` | run `bl` ("Busy", string `"503"`, envelope false, 10/10) | 420-432 grades nothing |
| L-noBody | `loading_503.body = null`, envelope false | — | envelope re-derivation needs a body |
| L-unobserved | `loading_503 null`, `loading_observed false`, no 503 transition, envelope `null` | old receipts | 404-418 only enforces agreement |
| D-zero | all `body_sha256` fields set to `"0"*64` (captures, transitions, loading_503) | — | no digest binding (`hashlib` only 37/72) |
| P-served | probe row `served_model` = another model, or absent with `evidence ""` | run `b` (stub MODEL_OK while server served `wrong-id`) | 698-743 ignore `served_model`/`evidence` |
| P-minimal | probe row reduced to `verdict`/`reason`/`drift`/`expected_model_id`/`declared` | — | same |
| O-empty | every `checks[].observed` set to `{}` | — | `observed` is optional (612, and `if "status" in o` at 635) |
| O-contra | `teardown_exited.observed.sigkill_sent true` while `teardown.sigkill_sent false` | — | observed/teardown cross-check beyond `returncode` (751-753) |
| M-fab | `model.sha256 == model_sha256_post == "e"*64`, observed matching | — | digests not recomputed; only `--expect-model-sha256` binds them |
| M-digest | `captures.models.body` replaced, `body_sha256` left/zeroed | — | body/digest binding |
| A-free | every `checks[].documented_by` replaced with "made-up anchor" | — | 605-607 only require a non-empty string |

Correctly rejected (do not weaken these): malformed probe rows (`rows: []`,
`rows: [42]`, `result: null`) become a recorded problem at `:539`, never a
traceback — `probe_row0` guards the type at `:149-156`; `captures.health.status
500`; `teardown.port_refuses null`; `teardown = {"error": ...}` and `teardown`
absent both yield INVALID without a traceback.

## Findings

### H1 — `health_ready` grades status, never the body its own DOC cites (high)
`check-receipt.py:631-633` is the whole predicate — quote: `elif health_status != 200:`.
The producer's DOC at `kama-llamacpp-live.py:78-82` says `/health` returns 200
`{"status":"ok"}` once loaded; the producer check is equally status-only
(`kama-llamacpp-live.py:938-939`, quote: `checks.append(_check('health_ready', health_status == 200,`).
Measured: 200 + `{"status":"degraded"}` → `ACCEPTED []`. Deleting
`captures.health.body` outright is also accepted. Sources already exist for the
exact body (S035/S036), so the v2 predicate needs no new row.

### H2 — `teardown_exited` accepts self-exit, SIGKILL, and arbitrary codes (high)
`check-receipt.py:748-750`, quote: `elif teardown.get("returncode") is None:` —
the only failure is "never reaped"; `sigterm_sent` and `sigkill_sent` are never
read, although the producer DOC (`kama-llamacpp-live.py:107-110`) claims "must
terminate on SIGTERM/SIGKILL". Measured accepted: rc 0 / no SIGTERM, rc -9 /
`sigkill_sent true`, rc 8. The real receipt carries `returncode 0,
sigterm_sent true, sigkill_sent false`, so a causation predicate is satisfiable
by honest runs.

### H3 — `teardown_port_closed` is vacuous and ownership is an unchecked string (high)
`check-receipt.py:761-763`, quote: `elif teardown.get("port_refuses") is not True:`.
Nothing requires that the port ever listened, that it was owned at ready time,
or that the boolean was derived from a real connect attempt. The ownership
gate is a token comparison (`check-receipt.py:434-438`, quote:
`elif own != "child":`), and the receipt stores only that token — `verify_live`
computes the pid/inode proof and then discards it (`kama-llamacpp-live.py:534-546`,
returning the string). A minimal `{"returncode":0,"port_refuses":true}` teardown
is accepted, so the check cannot distinguish "our child's port closed" from
"nothing was ever there".

### H4 — the loading envelope is consistency-checked, not graded (high)
`check-receipt.py:420-432` re-derives `loading_envelope_exact` from
`loading_503.body` but only compares flag to body (`:428`, quote:
`elif lef != want_lef:`). A receipt with a non-exact body and `false` passes; so
does one with `loading_503.body null` and `false`; so does one that never
observed loading at all (`:404-418` only enforce `loading_observed` ⇔
`loading_503` ⇔ a 503 transition; `transitions: []` + `loading_observed false`
→ `ACCEPTED []`). There is no check id, so `REQUIRED_CHECKS` (`:53-64`) cannot
carry it, and `:614-617` rejects any attempt to add one in v1.

### M1 — `observed` is decorative (medium)
`:612` requires only that it is an object; every comparison is conditional on
key presence (`:635`, `:649-651`, `:665-666`, `:752-753`, `:765-766`, `:780-783`).
Emptied observations are accepted, and an `observed` key that is never compared
(e.g. `teardown_exited.observed.sigkill_sent true` against `teardown.sigkill_sent
false`) is also accepted. A receipt can therefore look evidentiary while the
only checked numbers are the top-level ones.

### M2 — stored bodies are not bound to their digests (medium)
`body_sha256` is written by the producer (`kama-llamacpp-live.py:549-560`) and
never recomputed by the gate: `hashlib` occurs only at `check-receipt.py:37`
and `:72`. Zeroing every `body_sha256` in `captures`, `transitions`, and
`loading_503` is accepted, and replacing `captures.models.body` while leaving
its digest untouched is accepted. Any future claim that the receipt is
tamper-evident for captured bodies is unsupported until the gate hashes them.

### M3 — the selftest cannot see any of this (medium)
The 26 `mut(...)` cases (`:1004-1065`) are gate-authored mutations of a
gate-authored literal. There is no case for a health body, a teardown
returncode/sigterm change, an envelope-false-with-bad-body, a missing
`sigterm_sent`, or a `served_model` cross-check. `envelope-flag-inconsistent`
(`:1036-1037`) flips the flag while the body stays exact, so it only proves the
consistency rule, not grading. My 26 accepted-bad variants are all outside that
matrix; the gate's own detector count is therefore not a measure of
fail-capability.

### L1 — `documented_by` is free text (low)
`:605-607` require a non-empty string, so a receipt can cite an anchor that does
not exist (`ACCEPTED []` with "made-up anchor"). This matters for C2 because the
new teardown health predicates must cite new SOURCES rows; nothing in the gate
would notice a stale or invented anchor.

### L2 — `/props`, `/slots`, `/metrics` have no stored body (low)
The producer captures them with `keep_body=False`
(`kama-llamacpp-live.py:581`, `:611`), so `props_alias` compares the producer's
extracted dict to itself (`:682-696`). Independent re-derivation is impossible
even in principle; storing the bodies would let the gate re-parse.

### L3 — `-m` is now bound (good; supersedes an earlier finding)
`check-receipt.py:365-368` requires `argv -m == model.path`, so the round-16
`RerunReceiptGate.md` P6 gap ("never `-m`") is closed at this revision. The
argv/host/port/ctx/threads/tail checks (`:355-389`) and the refusal-set checks
(`:206-228`) are also real and should be preserved.

## What the C2 counting command (`tests/llamacpp-live/controls.py`) must do

1. **Forge consistently.** My first teardown forgeries (rc 0, -9, 8) were
   rejected only because `checks[].observed.returncode` still said -15; after
   co-forging `observed`, all three were accepted. A control that is not
   internally consistent is rejected on `observed` mismatch (`:751-753`) and
   understates the before count. Each fake-server control must let the frozen
   tool write its own `observed` value.
2. **Compare tool+gate together, not a v1 receipt against a v2 gate.** The v2
   gate will reject a v2-schema receipt at `:174-176` before any predicate runs,
   which would manufacture a 9/9 "improvement" with zero predicate work. Run
   the same fake-server script through the frozen tool+v1 gate (expect accept)
   and through the v2 tool+v2 gate (expect reject), and assert the rejection
   names the intended predicate, not `schema is ...`.
3. **Before arm measured here.** v1 accepted every one of the 26
   contract-violating variants that were internally consistent; its only
   rejections were for internal inconsistency (`observed` mismatch) or
   malformed JSON shapes, never for the violated contract. The four
   claim-named controls are 0/4 rejected before. Suggested minimum set for
   `controls.py`:
   `health-body-degraded`, `teardown-selfexit-rc0`, `teardown-sigkill-9`,
   `loading-nonexact-envelope`, plus `loading-never-observed`,
   `teardown-keys-absent`, `served-model-wrong`, `body-digest-zeroed`,
   `observed-emptied`.
4. **Keep a valid arm.** The v1 receipts (`.ufo/waves/round-16/live/receipt.json`,
   `receipt-frozen-probe.json`) must keep validating and the 26 selftest
   mutations must keep being rejected; the v2 gate must branch on `schema` and
   leave the v1 path as-is, otherwise the "v1 receipts validate unchanged" half
   of the claim fails.
5. **Preserve the malformed-row behaviour.** `probe_row0` (`:149-156`) and the
   `:539` message already turn bad probe output into a recorded failure; a
   `controls.py` case should pin that (rows `[]`, `[42]`, `result: null`) so a
   future edit cannot trade it for a traceback.

## Predicate targets for v2 (gate lines to change)

- `health_ready` (`:628-637`): parse `captures.health.body` and require exactly
  the S035/S036 ready body `{"status":"ok"}`; reject a missing body.
- `teardown_exited` (`:745-756`): require `sigterm_sent is True`,
  `sigkill_sent is False`, `returncode` in the documented graceful set (the
  real run is 0 after SIGTERM), and `term_wait_ms` within `TERM_GRACE`. These
  predicates need the new SOURCES rows: none exists yet for the llama.cpp
  signal/shutdown path or for `subprocess.Popen.returncode` (`grep` over
  `corpus/SOURCES.md` finds no SIGTERM/shutdown/subprocess/Popen row; S035-S038
  cover only the HTTP lifecycle).
- `teardown_port_closed` (`:758-769`): require child ownership at ready time
  **and** evidence the port served before teardown (a 200 `/health` capture, or
  a transitions row) **and** `port_refuses is True`; ideally store the pid/inode
  proof from `port_owned_by` (`kama-llamacpp-live.py:275-293`) so the ownership
  token is not self-asserted.
- loading: add a v2 check id (schema branch) requiring `loading_observed is
  True` and `loading_envelope_exact is True`, with `loading_503.body` present;
  if "graded when observed" is read literally, `envelope false` must still
  fail and the control must assert exactly that.
- probe checks (`:698-743`): compare the OK row's `served_model` to
  `captures.models` ids and require the row to record a `GET /v1/models`
  request; keep this consistent with C1's probe-contract route-match work.

## Residual risk and verification gaps

- Forgeries are receipt-level. The gate reads only receipt JSON, so this bounds
  the gate exactly, but it does not prove the v2 producer emits these fields
  honestly; `controls.py` must exercise the tool end-to-end against a fake
  server.
- [INFERENCE] llama.cpp exits 0 on the harness SIGTERM (real receipt rc 0 with
  `sigterm_sent true`) and would be -15 without a handler; the v2 predicate
  needs the new SOURCES rows to say which is documented rather than inferred.
- `model_unchanged` remains a self-sentinel; a v2 run without
  `--expect-model-sha256` proves only internal consistency, exactly as before.
- No lane gate, live harness, `measure.py`, or `mutants.py` was run; no file
  outside this Report was written; no port was bound and no `llama-server`
  started. The gate's `--selftest` was not executed.

Installs: none.
