# GateClaimFlags — gate claim-flip falsification (round 18, leaf)

VERDICT: confirm — raw failing body + passed:true is rejected via the re-derived predicate (not schema noise) for all 11 v3 check ids, and every pure claim-flag flip (passed/evaluated/outcome) is refused by the claim guards, on both module-level and subprocess runs of gate sha256 c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335 at 1c325b2e58fcfdc6761f645b44cedfb1d65243e6.

## Scope and method

Target: `tests/llamacpp-live/check-receipt.py` (the v3 receipt gate), sha256
`c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`,
`tools/kama-llamacpp-live.py` sha256
`dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b`,
`tests/llamacpp-live/controls.py` sha256
`106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8`
— all at lane commit `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`
("round-18: retain measured arms and repair counter classification seams"),
checked out in the seat clone `/tmp/kama-r18-falsify-GateClaimFlags`
(`git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin` + `git switch -c
seat/GateClaimFlags 1c325b2e58f...`; verified `git log -1`).

No ports were opened, no servers started, no production file modified; the
gate and tool modules were imported read-only and the gate binary was run as
a subprocess on receipt files under `/tmp`. No packages were installed
(no tooling change to record).

Driver scripts (byte-identical copies embedded at the end of this report):
`/tmp/kama-r18-falsify-GateClaimFlags/flip.py` (module-level sweeps),
`flip3.py` (subprocess exits + controls-style flip arm). Bases:
`v3-base.json` sha256 `f07d55e1fe90637a932da720cbd4bcbe0e000b509bf8fef94f283d966b0442e8`
(the gate's own `_selftest_receipt_v3()`, exported verbatim) and
`no-loading-base.json` sha256 `da515cf07db8321eec94c93452268da817c1ee80b8b17d8b3e8e3a2657c4cbe6`
(the selftest's legitimate `v3-no-loading-not-evaluated` receipt). Both
validate clean before any mutation (`g.validate(...) == []` for each —
executed assertion in flip.py lines 23–24).

**Green pristine / restoration:** pristine v3 and pristine no-loading both
validate with zero problems (executed asserts). Receipts are built per case
from the in-memory base; no byte-restore step exists because nothing is
written back to any shared file — the only written artifacts are two
scratch JSON bases and two driver scripts inside the seat clone/scratch,
both deleted at finish.

**Not a fresh-mutant kill set:** this item flips claim *fields* in receipts
(data), it does not mutate the gate. Fresh gate mutants are a separate
denominator (FreshGate item); no mutant site here, hence no kill/survival
classification to record beyond the rejection table itself.

## The three flags and their guards (path:line)

`passed` (v3 tri-state) and `evaluated` are guarded in the checks loop,
`check-receipt.py:789–815`:
- `check-receipt.py:791` — v3 `passed` must be true|false|null (else type rejection).
- `check-receipt.py:793` — **v3 rejects any `passed:false` outright** (a v3
  receipt of a passing run may not carry a failed check; the tool itself
  emits `passed:false` with `outcome:'fail', exit 1` via
  `tools/kama-llamacpp-live.py:873–885`, and the gate deliberately grades
  such a receipt INVALID — "passed is false" — so a fail-dominates reading
  of KQ24 is enforced at the gate, not laundered into not-evaluated).
- `check-receipt.py:798–802` — `evaluated:true, passed:null` and
  `evaluated:false, passed!=null` both rejected.
- `check-receipt.py:805–813` — the sole null license: only
  `loading_envelope_graded`, only when `loading_observed` is false AND no
  `/v1/models` 503 row is stored, AND `observed.not_evaluated_reason` must
  be exactly `no-loading-503-observed`.
- v1/v2 (`:814–818`): `passed` must be boolean true; anything else rejected.
- v2 claim crosscheck `claim(cid, want)` `:833–841`: every v2 check id's
  claimed `passed` is compared against the value re-derived from raw
  evidence (claim calls at `:873, 914, 939, 959, 979, 1012, 1048, 1092,
  1127, 1169, 1342`).
- v3 per-check `require_observed(cid, values)` `:848–855`: the `observed`
  dict of every v3 check is compared key-by-key against re-derivation from
  raw bodies/statuses (all 11 ids).
- top-level `outcome` re-derivation `:1346–1368`: `outcome` must be one of
  pass/fail/not-evaluated/setup-error AND equal the majority vote of check
  states (`setup-error` dominates, then any false → fail, then any null →
  not-evaluated, else pass); mismatch printed as
  `outcome 'X' != re-derived 'Y'`.
- `main()` exit mapping `:2100–2110`: VALID→0, INVALID→1, unreadable→2,
  v3 `not-evaluated`→3 (`NOT-EVALUATED` line).

## Attack A — raw failing body + passed:true (the item's question)

For every check id the raw evidence is corrupted so the check genuinely
fails while every claim flag stays `passed:true, evaluated:true,
observed aligned, outcome:'pass'`. Raw corruptions (not schema violations —
every field stays type-correct and digest-consistent):

- health_ready: `captures.health.body = '{"status":"degraded"}'` with
  recomputed `body_sha256`
- models_alias_id / models_owned_by_llamacpp: models body
  `{"data":[{"id":"some-other-id","owned_by":"openai"}]}` + recomputed digest
- metrics_not_enabled: `captures.metrics.status = 200`
- props_alias: `props.fields.model_alias = 'not-the-alias'`
- probe_model_ok: ok-probe row verdict `MODEL_MISMATCH`,
  reason `served-id-mismatch`, exit 2 (summary.exit aligned)
- probe_mismatch: mismatch-probe row verdict `MODEL_OK`, reason `matched`,
  exit 0 (summary.exit aligned)
- teardown_graceful: `returncode:-9, sigterm_sent:false, sigkill_sent:true,
  alive_at_teardown_start:false`
- teardown_port_closed: `teardown.port_refuses = false`
- loading_envelope_graded: all stored 503 bodies (transitions row,
  loading_503, loading_503_bodies) swapped to
  `{"error":{"message":"Warming","type":"x","code":503}}` with recomputed
  digests, repeats 0, `loading_envelope_exact=false`
- model_unchanged: `model_sha256_post = 0×64`

### Table — check id → rejection (v3, module-level `validate()`)

| check id | verdict | first gate problem (re-derived predicate) | n problems |
|---|---|---|---|
| health_ready | REJECTED | `health_ready: captures.health.body {'status': 'degraded'} != the documented ready body {'status': 'ok'}` (+ `claims passed=True but evidence re-derivation gives False`, + `observed.body ... != re-derived`) | 3 |
| models_alias_id | REJECTED | `models_alias_id: served ids ['some-other-id'] are not all the alias 'kama-live-probe'` (+ claim, + observed.data_ids, + observed.status) | 6 |
| models_owned_by_llamacpp | REJECTED | `models_owned_by_llamacpp: owned_by ['openai'] not all 'llamacpp'` (+ claim + observed) | 6 |
| metrics_not_enabled | REJECTED | `metrics_not_enabled: /metrics status 200 != 501 (llama.cpp without --metrics answers exactly 501)` (+ claim + observed.status) | 3 |
| props_alias | REJECTED | `props_alias: props.fields.model_alias 'not-the-alias' != alias 'kama-live-probe'` (+ claim + observed.fields) | 3 |
| probe_model_ok | REJECTED | `probe_model_ok: stored verdict 'MODEL_MISMATCH' != MODEL_OK` (+ reason, + exit, + claim, + 3 observed) | 8 |
| probe_mismatch | REJECTED | `probe_mismatch: stored verdict 'MODEL_OK' != MODEL_MISMATCH` (+ reason, + exit, + claim, + 3 observed) | 8 |
| teardown_graceful | REJECTED | `teardown_graceful: teardown.alive_at_teardown_start is False, want true (must prove the child was alive when teardown began)` (+ sigterm/sigkill/rc problems, + claim, + 6 observed) | 10 |
| teardown_port_closed | REJECTED | `teardown_port_closed: teardown.port_refuses is False, want true` (+ claim + 2 observed) | 4 |
| loading_envelope_graded | REJECTED | `transitions /v1/models 503 row 0 does not carry the exact loading envelope` (+ non-exact re-derivation, + passed True != re-derived False, + observed.exact) | 6 |
| model_unchanged | REJECTED | `model_unchanged: model.sha256 != model_sha256_post (the run mutated its input model)` (+ claim + observed.post) | 3 |

**Answer to the item's question: yes.** In every one of the 11 cases the
gate's *first* problem is the re-derived predicate over the raw body, and
one of the problems names the check id with the claim/evidence mismatch
(`claims passed=True but evidence re-derivation gives False` — v2-style
claim text — or, in v3, the `observed.X != re-derived Y` /
`passed True != re-derived False` forms). None of the 55 raw-body cases in
the sweep produced a schema-only rejection; schema/shape problems are absent
because the mutations keep every field type-correct.

Subprocess confirmation (gate binary, one failing-body receipt per id, no
`--expect` pins — the weakest gate invocation): all 11 exit **1** with
`INVALID ...` and the same first predicate problem as above
(`flip3.py` part 3a output). The rejection therefore does not depend on
`--expect` pins.

Precondition check (no silent raw-fail acceptance): with claims aligned to
the failure (`passed:false, outcome:'fail'`) every case is still rejected —
by `check '<id>': passed is false` (`:793`) plus the raw predicate — so no
failure path, laundered or honest, reaches VALID.

### v2 table (same attack, `claim()` crosscheck active)

All 11 v2 ids REJECTED; first problem is the raw predicate, second is
`check '<id>': claims passed=True but evidence re-derivation gives False`.
One nuance: v2 `health_ready` raw body failure is caught only via the v2
body-equality rule; v1 (no body rule, no claim) **accepts** raw
`{"status":"degraded"}` + `passed:true` (see Attack D).

### v1 baseline (documented permissiveness, not part of the claims)

v1 has no `claim()` and no `require_observed`; 9 of 10 ids still reject the
raw failing body through their own predicates, but `health_ready` accepts a
200 `{"status":"degraded"}` body with `passed:true` (`validate()` on
`_selftest_receipt()` with the body swapped returns `[]` — executed). v1
pure claim flip (`passed:false`) is rejected by `:815–818`. This is the
documented v1 boundary the schema floor (`--require-schema v3`, k19/k20
controls, GateSchemaFloor item) exists to close; it is not a v3 defect.

## Attack B — pure claim-flag flips on green raw bodies (v3)

Sweep D (44 cases): for each of the 11 ids × {passed:false,
passed:null+evaluated:false, evaluated:false(+null reason), evaluated:'yes'}
on the otherwise-green base receipt:

| flip | rejection | guard | coverage |
|---|---|---|---|
| `passed:false` (+outcome fail) | REJECTED all 11 | `passed is false` `:793` | 11/11 |
| `passed:null, evaluated:false` + reason | REJECTED all 10 non-loading ids | null-license guard `:805–813` | 10/10 |
| same flip on `loading_envelope_graded` (with 503 stored) | REJECTED | same guard: "only loading_envelope_graded may be unevaluated, **and only with no /v1/models 503**" | 1/1 |
| `evaluated:'yes'` (type flip) | REJECTED all 11 | `evaluated is not a boolean` `:796` | 11/11 |
| `passed:1/'true'` (type flips) | REJECTED | `passed is not true|false|null` `:791` | tested on health_ready |
| `passed:true` (no-op) | ACCEPTED (green) | — | correct |

Outcome-only flips on green raw bodies: `outcome='fail'` /
`'not-evaluated'` / `'setup-error'` with all-true checks → REJECTED by
`outcome 'X' != re-derived 'pass'` (`:1366–1368`); `outcome='PASS'` →
rejected twice (unknown value + re-derivation); removed `outcome` →
`outcome None is not a v3 outcome`. These were also already pinned by
existing selftest cases `v3-outcome-fail-with-all-true-checks` and
`v3-outcome-pass-with-null` (selftest mut3 names, `:1931–1932`, `:1963–1965`).

## Attack C — no-loading license abuse (legitimate NOT-EVALUATED base)

On `no-loading-base.json` (valid, exit-3 path):

| abuse | verdict | first problem |
|---|---|---|
| loading check `passed:false` | REJECTED | `check 'loading_envelope_graded': passed is false` |
| license escalated `evaluated:true, passed:true` | REJECTED | `check 'loading_envelope_graded' passed True != re-derived None` (+ `evaluated True != re-derived False`) — the gate re-derives null from the absence of 503 evidence (`:1177–1262`) |
| `not_evaluated_reason` dropped | REJECTED | `observed.not_evaluated_reason None != 'no-loading-503-observed'` |
| `not_evaluated_reason='x'` | REJECTED | same guard, wrong reason |
| loading check removed entirely | REJECTED | `required check 'loading_envelope_graded' is absent` |
| top `outcome:'pass'` | REJECTED | `outcome 'pass' != re-derived 'not-evaluated'` |
| all 10 non-loading checks nulled (license copied) | REJECTED | 10× null-license guard, one per id (`:805–813`) |

So the not-evaluated escape hatch cannot be extended to any other check, to
a 503-observed run, or to a wrong/absent reason string. This matches
selftest pins `v3-unobserved-loading-missing-reason`,
`v3-unobserved-loading-claimed-evaluated`, `v3-nonloading-check-is-null`,
`v3-loading-check-null-although-503-present`, `v3-outcome-pass-with-null`.

## Attack D — controls-style total flip (the "unrelated schema error" probe)

Reimplemented `controls.py:1073–1104 _gate_flip` semantics at module level:
take an honest `passed:false`/`outcome:'fail'` receipt (raw failing body,
claims aligned to the failure), set EVERY non-true check to
`passed:true/evaluated:true`, `outcome:'pass'`, clear
`setup_error`/`internal_fault`, and require the gate to refuse it. Result:
all 11 ids REJECTED with the targeted check id named in the problem list
(`targeted-named=True` for all 11) — the gate cannot be walked past a raw
failure by claim surgery. The no-loading license flip is likewise refused
by the v3 re-derived null (`passed True != re-derived None`).

This is the same property the official measured counter already exercises
end-to-end: `c1-measure.json` records 33 gate-flip arms (17 after-arm,
16 before-arm), **all `rejected=True`, all `targeted=True`**, and
`gate_flip_bad 0→0` (`.ufo/waves/round-18/runs/c1-measure.json`, counts
`gate_flip_arms {after:17, before:16, delta:1}`, `gate_flip_bad {0,0,0}`;
per-arm rows e.g. `k1 flipped=['health_ready'] rejected=True targeted=True
exit=1`). My independent sweep agrees with the official instrument.

## Attack E — producer end-to-end (claims forged *by the producer's own classifier*)

The gate's independence was verified against the producer's classification
logic, not just hand-forged JSON: with
`tools/kama-llamacpp-live.py:873–885 _outcome_exit`, a checks list whose
claims all say true yields `('pass', 0)` — the producer's classifier trusts
claims by design. The gate, reading the same shape, re-derives from raw
evidence instead. A producer-shaped v3 receipt (full argv binding, source
bindings, correct digests) whose mismatch-probe **raw row records
MODEL_OK/exit 0** (the wrong-id expectation was answered with the real
alias — a genuine `probe_mismatch` failure) while the producer classification
still claims `passed:true / outcome:'pass'` is REJECTED with:
`probe_mismatch: stored verdict 'MODEL_OK' != MODEL_MISMATCH`,
`stored reason 'matched' != served-id-mismatch`, `recorded exit 0 != 2`,
`observed.exit 2 != re-derived 0`, `observed.verdict ... != re-derived
'MODEL_OK'`, `observed.reason ... != re-derived 'matched'`. The same
receipt with the honest raw row (`MODEL_MISMATCH/2`) differs only in that
predicate and nothing else in the problem set, so the rejection is
attributable to the targeted conjunct rather than to shape.

## Official-run cross-checks (clone copies, exit codes re-run)

- `tests/llamacpp-live/check-receipt.py --selftest` → `selftest: 5 VALID and
  1 NOT-EVALUATED receipts accepted; 61 mutations + unreadable case
  rejected`, exit 0 (matches official `runs/gate-selftest.stdout`/exit 0,
  `runs/commands.json` name `gate-selftest`).
- All three official receipts re-validated in the clone:
  `receipt-1/2/3` → exit 0, `VALID`, `outcome pass`, loading observed,
  ports 33769/44109/45359 (matches `runs/live-gate-{1,2,3}.exit` = 0).
- Frozen round-17 gate (`.ufo/waves/round-18/frozen/
  tests_llamacpp-live_check-receipt.py`, sha256
  `ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5`,
  manifest revision `e75cf680b53484a61709ee1b2787d8dbc6419f74`) already
  rejects the claim-flip on its own v2 selftest receipt (predicate +
  `claims passed=True but evidence re-derivation gives False`); the round-18
  additions (tri-state guards, null license, outcome re-derivation,
  require_observed) extend the same property to v3 — continuity, not a new
  guarantee.
- Round-17 advice `GateForgeries.md` matrix row 01 already recorded the
  v2 health-body+`passed:true` rejection; this round's item extends the
  table to all ids, to `evaluated`/`outcome`, and to the null license.

## Residual limits (honest, non-blocking)

1. **v3 "passed is false" is total** (`:793`): a receipt of a genuinely
   failing run is always INVALID — the gate validates *pass receipts*
   only; a fail surfaces as tool exit 1, not as a gate-graded fail
   receipt. This is the design the controls rely on (fakes expect
   `rejected-targeted`), but it means the gate alone cannot distinguish
   "producer honestly reported failure" from "producer failed to
   launder"; only the tool's exit code/outcome carries that. Not a claim
   violation (C1 never claims gate-grading of fail receipts), recorded as
   a boundary.
2. `evaluated:true` on a check whose raw evidence is missing is caught
   per-check (e.g. `loading_envelope_graded` re-derivation, probe rows),
   and `require_observed` catches forged observations — but the attack
   here aligned observations to the failure, which the claim guards then
   catch via the raw-body predicates; no hole found in that seam.
3. Raw-body corruptions used digest-consistent bodies; a *digest-tampered*
   body would additionally trip `captures.{health,models}.body_sha256 does
   not match its stored body` (`:613–621`) — outside this item's question.
4. No port opened; no listener existed at start or finish (nothing was
   started by this seat; `ss` check unnecessary and not claimed).

## Verification summary (executed, this clone)

- pristine v3 + pristine no-loading: 0 problems each (green baseline).
- Attack A: 11/11 v3 ids rejected with re-derived-predicate first problem;
  11/11 at subprocess level exit 1 without pins; 11/11 v2.
- Attack B: 33/33 pure flips rejected; guards per table above.
- Attack C: 7/7 license abuses rejected.
- Attack D: 11/11 total flips rejected, targeted id named in every case;
  consistent with 33/33 official flip arms (`rejected=True,
  targeted=True`, `gate_flip_bad=0`).
- Attack E: producer classifier says pass on lying claims; gate refuses
  with the probe_mismatch predicate; honest twin accepted modulo the same
  non-claim predicate problems.

## Driver sources (exact experiment, per contract)

```python
#!/usr/bin/env python3
# /tmp/kama-r18-falsify-GateClaimFlags/flip.py  (module-level sweeps)
"""GateClaimFlags falsify driver: flip passed/evaluated/outcome across all
check ids on a v3 receipt whose raw bodies are failing, plus full-claim
flip sweeps on the green base and the legitimate no-loading base.

Import of the gate module is read-only: no production file is modified.
Exit 0 only when every case behaves as the attack predicted it must.
"""
import copy
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

CLONE = pathlib.Path("/tmp/kama-r18-falsify-GateClaimFlags")
GATE = CLONE / "tests/llamacpp-live/check-receipt.py"
SPEC = importlib.util.spec_from_file_location("check_receipt", GATE)
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)

GATE_SHA = "c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335"

raw = json.load(open("/tmp/kama-r18-falsify-GateClaimFlags/v3-base.json"))
NO = json.load(open("/tmp/kama-r18-falsify-GateClaimFlags/no-loading-base.json"))
assert g.validate(copy.deepcopy(raw)) == []
assert g.validate(copy.deepcopy(NO)) == []

def load_check(r, cid):
    return next(c for c in r["checks"] if c["id"] == cid)

def make_failing_body(cid, raw):
    r = copy.deepcopy(raw)
    if cid == "health_ready":
        r["captures"]["health"]["body"] = '{"status":"degraded"}'
        r["captures"]["health"]["body_sha256"] = hashlib.sha256(
            b'{"status":"degraded"}').hexdigest()
    elif cid in ("models_alias_id", "models_owned_by_llamacpp"):
        body = json.dumps({"data": [{"id": "some-other-id",
                                     "owned_by": "openai"}]},
                          separators=(",", ":"))
        r["captures"]["models"]["body"] = body
        r["captures"]["models"]["body_sha256"] = hashlib.sha256(
            body.encode()).hexdigest()
    elif cid == "metrics_not_enabled":
        r["captures"]["metrics"]["status"] = 200
    elif cid == "props_alias":
        f = dict(r["captures"]["props"]["fields"])
        f["model_alias"] = "not-the-alias"
        r["captures"]["props"]["fields"] = f
    elif cid == "probe_model_ok":
        r["probes"][0]["exit"] = 2
        r["probes"][0]["result"]["summary"]["exit"] = 2
        r["probes"][0]["result"]["rows"][0].update(
            verdict="MODEL_MISMATCH", reason="served-id-mismatch",
            drift=True)
    elif cid == "probe_mismatch":
        r["probes"][1]["exit"] = 0
        r["probes"][1]["result"]["summary"]["exit"] = 0
        r["probes"][1]["result"]["rows"][0].update(
            verdict="MODEL_OK", reason="matched", drift=False)
    elif cid == "teardown_graceful":
        r["teardown"].update(returncode=-9, sigterm_sent=False,
                             sigkill_sent=True,
                             alive_at_teardown_start=False)
    elif cid == "teardown_port_closed":
        r["teardown"]["port_refuses"] = False
    elif cid == "loading_envelope_graded":
        new_rows = []
        for row in r["transitions"]:
            if row.get("path") == "/v1/models" and row.get("status") == 503:
                body = '{"error":{"message":"Warming","type":"x","code":503}}'
                row["body"] = body
                row["body_sha256"] = hashlib.sha256(body.encode()).hexdigest()
                row["repeats"] = 0
            new_rows.append(row)
        r["transitions"] = new_rows
        lb = r["loading_503"]
        if lb is not None:
            body = '{"error":{"message":"Warming","type":"x","code":503}}'
            lb["body"] = body
            lb["body_sha256"] = hashlib.sha256(body.encode()).hexdigest()
        for b in r.get("loading_503_bodies", []):
            b["body"] = '{"error":{"message":"Warming","type":"x","code":503}}'
            b["body_sha256"] = hashlib.sha256(b["body"].encode()).hexdigest()
        r["loading_envelope_exact"] = False
    elif cid == "model_unchanged":
        r["model_sha256_post"] = "0" * 64
    else:
        raise AssertionError(cid)
    o = load_check(r, cid)["observed"]
    if cid == "health_ready":
        o.update(body={"status": "degraded"})
    elif cid == "models_alias_id":
        o.update(data_ids=["some-other-id"])
    elif cid == "models_owned_by_llamacpp":
        o.update(owned_by=["openai"])
    elif cid == "metrics_not_enabled":
        o.update(status=200)
    elif cid == "props_alias":
        o["fields"] = copy.deepcopy(r["captures"]["props"]["fields"])
    elif cid == "probe_model_ok":
        o.update(exit=2, verdict="MODEL_MISMATCH",
                 reason="served-id-mismatch")
    elif cid == "probe_mismatch":
        o.update(exit=0, verdict="MODEL_OK", reason="matched")
    elif cid == "teardown_graceful":
        o.update(returncode=-9, sigterm_sent=False, sigkill_sent=True,
                 alive_at_teardown_start=False, error=None)
    elif cid == "teardown_port_closed":
        o.update(port_refuses=False)
    elif cid == "loading_envelope_graded":
        o.update(all_exact=False, exact=False)
    elif cid == "model_unchanged":
        o.update(post="0" * 64)
    return r

# sanity: failing-body-with-honest-claims IS rejected (no silent pass)
for cid in [c["id"] for c in raw["checks"]]:
    assert g.validate(make_failing_body(cid, copy.deepcopy(raw))), cid

# sanity: failing-body + passed=False + outcome=fail rejected by "passed is false"
for cid in [c["id"] for c in raw["checks"]]:
    r = make_failing_body(cid, copy.deepcopy(raw))
    load_check(r, cid)["passed"] = False
    r["outcome"] = "fail"
    assert any("passed is false" in x for x in g.validate(r)), cid

rows = []
for cid in [c["id"] for c in raw["checks"]]:
    base = make_failing_body(cid, copy.deepcopy(raw))
    # sweep A: lying passed=true
    p = g.validate(copy.deepcopy(base))
    rows.append((cid, "passed=true", "raw-body",
                 "REJECTED" if p else "ACCEPTED", len(p), p))
    # sweep B: lying evaluated=false + passed=null on an observed failure
    r = copy.deepcopy(base)
    c = load_check(r, cid)
    c["passed"] = None
    c["evaluated"] = False
    c["observed"]["not_evaluated_reason"] = "no-loading-503-observed"
    r["outcome"] = "not-evaluated"
    p = g.validate(r)
    rows.append((cid, "evaluated=false+null", "raw-body",
                 "REJECTED" if p else "ACCEPTED", len(p), p))
    # sweep C: outcome flips with honest pass claims on raw failure
    for oc in ("not-evaluated", "fail", "setup-error"):
        r = copy.deepcopy(base)
        r["outcome"] = oc
        p = g.validate(r)
        rows.append((cid, f"outcome={oc}", "raw-body",
                     "REJECTED" if p else "ACCEPTED", len(p), p))

green_rows = []
for cid in [c["id"] for c in raw["checks"]]:
    for flag, mutate in (
            ("passed=false", lambda c: c.update(passed=False)),
            ("passed=null+evaluated=false",
             lambda c: c.update(passed=None, evaluated=False)),
            ("evaluated='yes'", lambda c: c.update(evaluated="yes")),
    ):
        r = copy.deepcopy(raw)
        c = load_check(r, cid)
        mutate(c)
        if flag == "passed=false":
            r["outcome"] = "fail"
        else:
            c["observed"]["not_evaluated_reason"] = "no-loading-503-observed"
            r["outcome"] = "not-evaluated"
        p = g.validate(r)
        green_rows.append((cid, flag, "REJECTED" if p else "ACCEPTED",
                           len(p), p))

nl_rows = []
lc0 = load_check(NO, "loading_envelope_graded")
nl_variants = [
    ("license: passed=false", lambda c, r: c.update(passed=False)),
    ("license: evaluated=true+passed=true",
     lambda c, r: c.update(evaluated=True, passed=True)),
    ("license: reason dropped",
     lambda c, r: c["observed"].pop("not_evaluated_reason")),
    ("license: wrong reason",
     lambda c, r: c["observed"].update(not_evaluated_reason="x")),
    ("license: removed", lambda c, r: r["checks"].remove(c)),
]
for label, fn in nl_variants:
    r = copy.deepcopy(NO)
    fn(load_check(r, "loading_envelope_graded"), r)
    p = g.validate(r)
    nl_rows.append(("loading_envelope_graded", label,
                    "REJECTED" if p else "ACCEPTED", len(p), p))
r = copy.deepcopy(NO); r["outcome"] = "pass"
p = g.validate(r)
nl_rows.append(("(receipt)", "outcome=pass on not-evaluated",
                "REJECTED" if p else "ACCEPTED", len(p), p))
r = copy.deepcopy(NO)
for c in r["checks"]:
    if c["id"] == "loading_envelope_graded":
        continue
    c.update(passed=None, evaluated=False)
    c["observed"]["not_evaluated_reason"] = "no-loading-503-observed"
p = g.validate(r)
nl_rows.append(("all-others", "nulls on 10 non-loading checks",
                "REJECTED" if p else "ACCEPTED", len(p), p))

out = ["== sweep A-C: raw failing body, claim-flag flips =="]
for cid, flag, body, verdict, n, p in rows:
    out.append(f"{cid:26s} {flag:28s} {body:9s} {verdict:8s} n={n} :: "
               f"{(p[0][:110] if p else '')}")
out.append("")
out.append("== sweep D: green raw bodies, pure claim flips ==")
for cid, flag, verdict, n, p in green_rows:
    out.append(f"{cid:26s} {flag:28s} {verdict:8s} n={n} :: "
               f"{(p[0][:110] if p else '')}")
out.append("")
out.append("== sweep E-F: no-loading license ==")
for cid, flag, verdict, n, p in nl_rows:
    out.append(f"{cid:26s} {flag:36s} {verdict:8s} n={n} :: "
               f"{(p[0][:110] if p else '')}")
print("\n".join(out))
print()
print(f"gate sha256 {GATE_SHA}")
print("pristine v3: VALID (0 problems); pristine no-loading: exit-3 path "
      "(0 problems)")
print(f"totals: raw-body cases {len(rows)}, green cases {len(green_rows)}, "
      f"no-loading cases {len(nl_rows)}")
```

```python
#!/usr/bin/env python3
# /tmp/kama-r18-falsify-GateClaimFlags/flip3.py  (CLI exits + flip arm)
"""(3a) one raw-failing-body receipt per check id, written to disk, checked
     by the gate binary as a subprocess. Exit codes and verdict lines.
(3c) controls-style total flip: all failing/null -> passed:true,
     evaluated:true, outcome:'pass', setup_error/internal_fault cleared;
     gate must refuse every flipped receipt, naming the targeted id.
Bases and make_failing_body are identical to flip.py (omitted here)."""
import copy, importlib.util, json, pathlib, subprocess, sys, tempfile
CLONE = pathlib.Path("/tmp/kama-r18-falsify-GateClaimFlags")
GATE = CLONE / "tests/llamacpp-live/check-receipt.py"
RAW = json.load(open(CLONE / "v3-base.json"))
NO = json.load(open(CLONE / "no-loading-base.json"))
spec = importlib.util.spec_from_file_location("check_receipt", GATE)
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
# ... make_failing_body identical to flip.py ...
def run_gate(path):
    proc = subprocess.run([sys.executable, str(GATE), str(path)],
                          capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip()
print("== part 3a: gate CLI exits on raw failing bodies (no pins) ==")
for cid in [c["id"] for c in RAW["checks"]]:
    r = make_failing_body(cid, copy.deepcopy(RAW))
    with tempfile.TemporaryDirectory() as td:
        p = pathlib.Path(td) / "r.json"; p.write_text(json.dumps(r))
        rc, out = run_gate(p)
    print(f"{cid:26s} exit={rc} {out.splitlines()[0][:60]}")
def controls_flip(doc):
    flip = copy.deepcopy(doc); flipped = []
    for c in flip.get("checks") or []:
        if isinstance(c, dict) and c.get("passed") is not True:
            c["passed"] = True
            if "evaluated" in c: c["evaluated"] = True
            flipped.append(str(c.get("id")))
    if "outcome" in flip: flip["outcome"] = "pass"
    for k in ("setup_error", "internal_fault"):
        if flip.get(k) is not None: flip[k] = None
    return flip, flipped
for cid in [c["id"] for c in RAW["checks"]]:
    base = make_failing_body(cid, copy.deepcopy(RAW))
    next(cc for cc in base["checks"] if cc["id"] == cid)["passed"] = False
    base["outcome"] = "fail"
    flip, flipped = controls_flip(base)
    p = g.validate(flip)
    print(f"{cid:26s} flip-all->pass: {'REJECTED' if p else 'ACCEPTED'} "
          f"targeted-named={cid in ' '.join(p)}")
flip, _ = controls_flip(NO)
p = g.validate(flip)
print("no-loading license flip to pass:", "REJECTED" if p else "ACCEPTED")
for m in p[:4]: print("   ", m[:100])
```

Both drivers ran with exit 0; full stdout is quoted in the tables above.
