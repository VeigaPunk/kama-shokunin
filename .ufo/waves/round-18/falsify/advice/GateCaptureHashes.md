VERDICT: partial — v3's named bindings (health/models body↔body_sha256, models/health/metrics capture statuses, v3 expected_model_id equality, outcome derivation) hold, but 22 forged receipts stay VALID and one /health-503 receipt is accepted NOT-EVALUATED; leaves enumerated below, 6 of 6 re-confirmed on the real committed receipt-1.json under the official pinned invocation.

# GateCaptureHashes — round-18 falsify: gate v3 capture bodies/statuses/errors, summary/expected_model_id nulls, ungraded leaves

Seat: KamaR18.GateCaptureHashes (leaf, no subagents). Advice to L1 only; no production, fleet, or evidence edits. 2026-10-20.

## Method and environment

- Clone (runtime checks ran ONLY here): `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-GateCaptureHashes && git -C … switch -q -c seat/GateCaptureHashes 1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; HEAD `1c325b2 round-18: retain measured arms and repair counter classification seams`.
- Files under attack (committed bytes): `tests/llamacpp-live/check-receipt.py` sha256 `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`; `tools/kama-llamacpp-live.py` sha256 `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b` — the tool digest equals the official `--expect-tool-sha256` in `.ufo/waves/round-18/runs/commands.json` (live-gate-1 argv), so the clone attacked exactly the measured bytes.
- `/usr/bin/python3` = Python 3.14.8. **No installs** (none needed). **No ports opened**: every experiment is a static receipt-mutation + gate-CLI run; final `ss -ltn` shows no seat-owned listener (I started zero socket-bound processes). `git status --porcelain` = `?? scratch/` only (no tracked file touched).
- Green pristine: gate `--selftest` → exit 0, "5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations + unreadable case rejected". Synthetic pristine v3 literal via official-style invocation (`--expect-{model,server,probe,tool}-sha256 … --require-schema v3`) → `VALID`, exit 0. Real `.ufo/waves/round-18/live/receipt-1.json` (v3, outcome pass, loading_observed true, port 33769) pristine under the official pins → exit 0.
- Forgeries are in-memory `copy.deepcopy` mutations of receipts; no receipt on disk in the lane was modified; case JSONs lived only in the clone's scratch (removed at finish).

## Claim-side result (why not refute)

The specific holes C1 names are closed in v3 and my red controls confirm each kill:

| Control (forgery) | Gate exit | Attribution (first problem) |
|---|---|---|
| `captures.health.body_sha256="0"*64` | 1 | `captures.health.body_sha256 does not match its stored body` — gate recomputes digests at `check-receipt.py:605-621` |
| `captures.models.status=503` (M7 analog, on real receipt-1) | 1 | `models_alias_id: captures.models.status 503 != 200 (round-18 RevTriStateDesign)` + observed mismatch, 4 problems (`:906-908`, `:932-934`) |
| probe `summary.exit=99` | 1 | `summary.exit 99 != recorded exit 0` (`:699-702`) |
| v3 row `expected_model_id=null` | 1 | `row expected_model_id None != record expect 'kama-live-probe'` (`:731-735`) |
| `captures.metrics.status=200` | 1 | `metrics_not_enabled: /metrics status 200 != 501` |
| `outcome="pass"` on the no-loading receipt | 1 | `outcome 'pass' != re-derived 'not-evaluated'` (`:1346-1368`) |

Also held: loading 503 transition/body digest + repeats + dropped-count grading (`:1195-1299`), loading_503 status/path (`:524-529`), health_ready body/status (`:863-885`), exact v3 argv (`mut3` set unchanged), source-binding validation. `health`/`models` stored bodies ARE bound to their digests in v3 — the attack headline question is answered **enforced** for those two captures.

## Findings — ungraded leaves remaining (concrete forgeries, all executed)

Fresh mutants: 24 synthetic candidates + 7 real-receipt cases, a separate denominator from the named round-17 set; none folded into it.

### H1 (High) — null-license slip: a recorded `/health` 503 loading envelope is accepted NOT-EVALUATED

- Forgery: take the gate-valid no-loading v3 receipt (`loading_observed=false`, `loading_503=null`, `loading_envelope_graded` passed=null/evaluated=false, reason `no-loading-503-observed`), insert one transition row `{"path":"/health","status":503,"body":"<exact S036 loading envelope>","body_sha256":<its digest>,"repeats":3}`.
- Executed: exit **3 (NOT-EVALUATED)** both bare and with `--expect-* … --require-schema v3`. Case `scratch/cases/leaf-health503-not-evaluated-null-license.json` (source regenerates it).
- Why the gate cannot see it: `model_503_rows` filters `/v1/models` only (`check-receipt.py:540-544`); `loading_observed` is bound only to that subset (`:549-551`); the not-evaluated license (`:803-813`, `:1289-1292`) checks `model_503_rows`, `loading_503`, and `loading_503_bodies` — a `/health` 503 row matches none of them.
- Plausibility: the producer itself polls `/health` through the same recorder (`tools/kama-llamacpp-live.py:626` `_observe('health', '/health', …)`), so such rows are producer-shaped. The receipt then claims `no-loading-503-observed` while its transitions record a loading 503 envelope with repeats — the exact "unobserved vs observed" distinction v3 was built to make (M2/KQ24), slipping on the second polled route.

### M1 (Medium) — `captures.props` / `captures.slots` statuses and body digests are completely ungraded

- `check-receipt.py:601-603` requires the capture objects to exist; the v3 digest loop covers only `("health","models")` (`:605-621`); `props_alias` binds only `fields` (`:961-977`, `require_observed("props_alias", {"fields": …})`); no check reads slots at all beyond presence.
- Executed (all exit 0, 0 problems, bare AND official-pinned): `props.body_sha256="garbage-not-hex"` (not even hex-format checked), `slots.body_sha256="0"*64`, `props.status=503`, `props.status=null`, `slots.status=500`.
- Re-confirmed on the real receipt-1.json under the official invocation: `real-props-status-503` and `real-slots-digest-zero` → `VALID` exit 0.

### M2 (Medium) — capture/teardown `error` fields are never graded

- No gate line reads `captures.{health,models,props,slots,metrics}.error` or `teardown.error` (grep over the gate: only producer-side files define them, `tools/kama-llamacpp-live.py:468,674,1178`). The producer writes `error: null` on every successful capture; `teardown_graceful.require_observed` even pins `observed.error == teardown.error`, making an error string *self-consistent*.
- Executed (exit 0 each): `health.error="ConnectionResetError"` beside its 200 `{"status":"ok"}` body; `models.error="BadStatusLine"`; `props.error`/`slots.error`/`metrics.error` set; `teardown.error="OSError: sigterm write failed"` with matching observed — a "graceful SIGTERM" check that passed while recording a teardown error. Real receipt: `real-health-error-set` → VALID.

### M3 (Medium) — probe `result.summary` is optional to the gate; null/missing strips the exit cross-check

- `check-receipt.py:699-702`: `sexit = dig(res, "summary", "exit")` — `dig` returns MISSING through a null/absent key (`:183-190`), and MISSING is skipped. The producer's kama-probe `check` **always** emits `summary` (`tools/kama-probe.sh:891`: `{"registry_rows_evaluated": …, "model_ok": …, "drift": …, "exit": …}`), so the gate floor is weaker than the producer shape.
- Executed (exit 0 each): `summary=null` on both probes, `summary` key deleted, `summary` reduced to `{"exit":0}` (registry_rows_evaluated/model_ok/drift dropped — content beyond exit ungraded). Control `summary.exit=99` is rejected. Real receipt: `real-summary-null` → VALID.

### M4 (Medium) — transition rows outside `/v1/models` 503 are ungraded; no final-transition ↔ `captures.health` cross-check

- Only `model_503_rows` are digest/envelope-checked (`:561-566`, `:1195-1218`); every other transition row is free. The producer's final `/health` 200 row and `captures.health` describe the same response but nothing equates them.
- Executed (exit 0 each): final `/health` 200 row `body_sha256="0"*64`; final `/health` 200 row body swapped to `{"status":"pwned"}` with matching digest; injected `/v1/models` 200 row with body `<html>foreign</html>` + zero digest; injected row `status=null, error=null` (producer-impossible: `status=null` ⇒ error set, `kama-llamacpp-live.py:467-468`). Real receipt: `real-health-transition-digest-zero` → VALID — the real receipt's health-transition digest tampered to zeros passes the official gate.

### Low leaves

- L1 `internal_fault` key removable: producer v3 always emits it (`kama-llamacpp-live.py:1178` initializes `internal_fault: None`; `:890` sets `internal:<ExcType>`); a receipt with the key stripped is gate-identical to "no fault observed" (exit 0). Real receipt: `real-internal-fault-key-absent` → VALID. (A *non-mirrored* internal_fault IS killed — `setup_error` pinning at `:275-277`, `:286-290`.)
- L2 probe `rows[1:]` ungraded (`:243-249` reads only rows[0]; documented first-row grading): appended contradictory `MODEL_MISMATCH/served-id-mismatch/ghost-model` row → exit 0. Producer emits exactly one row for live check, so forged-only.
- L3 capture `headers` ungraded: `captures.health.headers={"server":"nginx","content-type":"text/html"}` beside the exact ok body → exit 0.
- L4 `loading_503.t_ms` free (status/path/body/digest are bound; the timestamp is not) → exit 0.
- L5 `tool` block removable → exit 0 **bare**; closed under official mode (pinned run exits 1, `:439-440`). The official live-gate runs carry all four pins (`commands.json:257-289`), so this is convention-closed, matching the round-17 note that pins are runner convention, not gate-enforced.

### Notes (recorded, out of v3 scope or fail-closed)

- N1 v2 receipts tolerate `rows[0].expected_model_id=null` (`:726-730` checks only non-null; v3 equality at `:731-735` kills it). Executed: v2 base exit 0 bare, exit 1 pinned+`--require-schema v3`. The "optional expected_model_id null" license is v1/v2-only.
- N2 False-reject hazard, fail-closed: gate recomputes digests over `body.encode("utf-8")` (`:618-620`) while the producer hashes raw bytes and decodes stored text with `errors='replace'` (`kama-llamacpp-live.py:469-470,676`). A stored body containing invalid UTF-8 would be rejected rather than forged-through. Latent only (llama.cpp bodies are UTF-8); no forgery found on this seam.
- N3 v3 requires the exact V2 check-id set (`:821` uses `REQUIRED_CHECKS_V2` for v2+v3); no v3-specific widening was found there.

## Residual risk and verification gaps

- Forgeries were built on the gate's own valid v3/v2 literals and the committed real receipt-1.json; receipts 2/3 were not separately mutated (same shape, same grading code paths — risk of divergence negligible but not zero).
- I did not test whether the C1 counter (`round-18/c1/measure.py`) or `controls.py` catches any of these leaves — my item was the gate; the leaves could still be gated upstream by the control suite. That is exactly where L1 should look before quoting "schema floor" beyond the named holes.
- H1's practical exploitability depends on the producer ever recording a `/health` 503 row (possible per `kama-llamacpp-live.py:626`, observed never in the three real receipts); the forgery itself needs no server.
- All exits above were produced by `/usr/bin/python3 tests/llamacpp-live/check-receipt.py <case.json> [official pins] [--require-schema v3]` in the clone; full tables in `scratch/results.json` (regenerated by the inlined source; clone removed at finish).

## Exact experiment source

`scratch/forge.py` (synthetic-literal matrix; table above is its stdout):

```python
#!/usr/bin/env python3
"""Seat GateCaptureHashes round-18 falsify: concrete receipt forgeries vs gate v3.

Static experiment only: mutates in-memory copies of the gate's own valid v3/v2
selftest receipts, writes each to scratch/cases/, and runs the committed gate
CLI on it. No server, no ports, no production-file edits.
"""
import copy
import hashlib
import json
import os
import subprocess
import sys
import importlib.util

ROOT = "/tmp/kama-r18-falsify-GateCaptureHashes"
GATE = os.path.join(ROOT, "tests", "llamacpp-live", "check-receipt.py")
CASES_DIR = os.path.join(ROOT, "scratch", "cases")
PY = "/usr/bin/python3"

spec = importlib.util.spec_from_file_location("check_receipt", GATE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ENVELOPE = json.dumps({"error": {"message": "Loading model",
                                 "type": "unavailable_error",
                                 "code": 503}},
                      separators=(",", ":"))
ENV_SHA = hashlib.sha256(ENVELOPE.encode()).hexdigest()
PINS = ["--expect-model-sha256", mod.MODEL_SHA,
        "--expect-server-sha256", mod.SERVER_SHA,
        "--expect-probe-sha256", mod.PROBE_SHA,
        "--expect-tool-sha256", mod.TOOL_SHA]


def check_by_id(r, cid):
    return next(c for c in r["checks"] if c["id"] == cid)


def probe_by_expect(r, expect):
    return next(p for p in r["probes"] if p["expect"] == expect)


def make_no_loading(base):
    r = copy.deepcopy(base)
    r["transitions"] = [
        row for row in r["transitions"]
        if not (row.get("path") == "/v1/models" and row.get("status") == 503)]
    r.update(loading_503=None, loading_503_bodies=[],
             loading_bodies_dropped=0, loading_observed=False,
             loading_envelope_exact=None, outcome="not-evaluated")
    lc = check_by_id(r, "loading_envelope_graded")
    lc.update(passed=None, evaluated=False)
    lc["observed"].update({
        "loading_observed": False, "distinct_bodies": 0,
        "bodies_dropped": 0, "total_503_responses": 0,
        "all_exact": None, "exact": None,
        "not_evaluated_reason": "no-loading-503-observed"})
    return r


BASE_V3 = mod._selftest_receipt_v3()
BASE_V2 = mod._selftest_receipt_v2()
NO_LOADING = make_no_loading(BASE_V3)

CASES = []


def case(name, fn, base=None, kind="leaf"):
    CASES.append((name, fn, base, kind))


def row0(r, expect):
    return probe_by_expect(r, expect)["result"]["rows"][0]


# ---- controls (gate must reject: expect exit 1) ---------------------------
case("ctl-models-capture-503",
     lambda r: r["captures"]["models"].update(status=503), NO_LOADING, "ctl")
case("ctl-health-digest-zero",
     lambda r: r["captures"]["health"].update(body_sha256="0" * 64), None,
     "ctl")
case("ctl-summary-exit-mismatch",
     lambda r: [p["result"]["summary"].update(exit=99) for p in r["probes"]],
     None, "ctl")
case("ctl-v3-row-expected-model-id-null",
     lambda r: row0(r, r["alias"]).update(expected_model_id=None), None, "ctl")
case("ctl-metrics-status-200",
     lambda r: r["captures"]["metrics"].update(status=200), None, "ctl")
case("ctl-outcome-pass-on-no-loading",
     lambda r: r.update(outcome="pass"), NO_LOADING, "ctl")

# ---- body/digest leaves ----------------------------------------------------
case("leaf-props-digest-garbage",
     lambda r: r["captures"]["props"].update(body_sha256="garbage-not-hex"))
case("leaf-slots-digest-zero",
     lambda r: r["captures"]["slots"].update(body_sha256="0" * 64))
case("leaf-props-status-503",
     lambda r: r["captures"]["props"].update(status=503))
case("leaf-props-status-null",
     lambda r: r["captures"]["props"].update(status=None))
case("leaf-slots-status-500",
     lambda r: r["captures"]["slots"].update(status=500))

# ---- capture error-field leaves -------------------------------------------
case("leaf-health-error-set",
     lambda r: r["captures"]["health"].update(error="ConnectionResetError"))
case("leaf-models-error-set",
     lambda r: r["captures"]["models"].update(error="BadStatusLine"))
case("leaf-props-error-set",
     lambda r: r["captures"]["props"].update(error="TimeoutError"))
case("leaf-slots-error-set",
     lambda r: r["captures"]["slots"].update(error="ProtocolError"))
case("leaf-metrics-error-set",
     lambda r: r["captures"]["metrics"].update(error="TimeoutError"))


def _teardown_error(r):
    msg = "OSError: sigterm write failed"
    r["teardown"]["error"] = msg
    check_by_id(r, "teardown_graceful")["observed"].update(error=msg)


case("leaf-teardown-error-set", _teardown_error)

# ---- probe summary leaves ---------------------------------------------------
case("leaf-summary-null",
     lambda r: [p["result"].update(summary=None) for p in r["probes"]])


def _summary_missing(r):
    for p in r["probes"]:
        p["result"].pop("summary", None)


case("leaf-summary-missing", _summary_missing)


def _summary_shape(r):
    for p in r["probes"]:
        p["result"]["summary"] = {"exit": p["exit"]}


case("leaf-summary-shape-stripped", _summary_shape)

# ---- v2 expected_model_id null (out of v3 scope, recorded) ------------------
case("leaf-v2-row-expected-model-id-null",
     lambda r: [row0(r, p["expect"]).update(expected_model_id=None)
                for p in r["probes"]], BASE_V2, "leaf-v2")

# ---- transitions leaves -----------------------------------------------------
case("leaf-health-transition-digest-zero",
     lambda r: r["transitions"][2].update(body_sha256="0" * 64))


def _health_transition_body(r):
    body = '{"status":"pwned"}'
    r["transitions"][2].update(
        body=body,
        body_sha256=hashlib.sha256(body.encode()).hexdigest())


case("leaf-health-transition-body-swap", _health_transition_body)


def _extra_models_200_row(r):
    r["transitions"].insert(2, {
        "t_ms": 950, "path": "/v1/models", "status": 200, "error": None,
        "body": "<html>foreign</html>", "body_sha256": "0" * 64,
        "body_read_truncated": False, "body_over_cap": False,
        "headers": {}, "repeats": 0})


case("leaf-extra-models-200-garbage-row", _extra_models_200_row)


def _status_null_error_null_row(r):
    r["transitions"].insert(2, {
        "t_ms": 5, "path": "/props", "status": None, "error": None,
        "body_sha256": None, "body": None, "body_read_truncated": False,
        "body_over_cap": False, "headers": {}, "repeats": 0})


case("leaf-transition-status-null-error-null", _status_null_error_null_row)


def _health503_null_license(r):
    r["transitions"].insert(2, {
        "t_ms": 800, "path": "/health", "status": 503, "error": None,
        "body_sha256": ENV_SHA, "body": ENVELOPE,
        "body_read_truncated": False, "body_over_cap": False,
        "headers": {"server": "llama.cpp",
                    "content-type": "application/json; charset=utf-8"},
        "repeats": 3})


case("leaf-health503-not-evaluated-null-license", _health503_null_license,
     NO_LOADING, "leaf")
case("leaf-loading-503-tms-forged",
     lambda r: r["loading_503"].update(t_ms=999999))

# ---- probe rows[1:] ungraded -------------------------------------------------


def _extra_contradictory_row(r):
    ok = probe_by_expect(r, r["alias"])
    extra = copy.deepcopy(ok["result"]["rows"][0])
    extra.update(verdict="MODEL_MISMATCH", reason="served-id-mismatch",
                 drift=True, served_model="ghost-model")
    ok["result"]["rows"].append(extra)


case("leaf-probe-rows-extra-contradictory", _extra_contradictory_row)

# ---- schema-floor / optional-block leaves ------------------------------------
case("leaf-internal-fault-key-absent",
     lambda r: r.pop("internal_fault", None))
case("leaf-tool-block-removed", lambda r: r.pop("tool", None))
case("leaf-capture-headers-forged",
     lambda r: r["captures"]["health"].update(
         headers={"server": "nginx", "content-type": "text/html"}))

# ---- run ----------------------------------------------------------------------
os.makedirs(CASES_DIR, exist_ok=True)
pristine_problems = mod.validate(copy.deepcopy(BASE_V3))
print(f"pristine-validate problems: {pristine_problems}")

rows = []
for name, fn, base, kind in CASES:
    r = copy.deepcopy(BASE_V3 if base is None else base)
    fn(r)
    path = os.path.join(CASES_DIR, name + ".json")
    with open(path, "w") as fh:
        json.dump(r, fh, indent=1, sort_keys=True)
    bare = subprocess.run([PY, GATE, path], capture_output=True, text=True)
    pinned = subprocess.run([PY, GATE, path, *PINS, "--require-schema", "v3"],
                            capture_output=True, text=True)
    problems = mod.validate(r)
    rows.append({
        "name": name, "kind": kind,
        "bare_exit": bare.returncode, "bare_line": bare.stdout.strip(),
        "pinned_exit": pinned.returncode,
        "pinned_line": pinned.stdout.strip(),
        "n_problems": len(problems),
        "first_problem": problems[0] if problems else "",
    })

hdr = f"{'name':44} {'k':8} {'bare':5} {'pinned':7} {'prob':4} note"
print(hdr)
print("-" * len(hdr))
for row in rows:
    print(f"{row['name']:44} {row['kind']:8} {row['bare_exit']:<5} "
          f"{row['pinned_exit']:<7} {row['n_problems']:<4} "
          f"{row['first_problem'][:70]}")

with open(os.path.join(ROOT, "scratch", "results.json"), "w") as fh:
    json.dump(rows, fh, indent=1)

# required verdicts
failed = []
for row in rows:
    if row["kind"] == "ctl" and row["bare_exit"] != 1:
        failed.append(("CONTROL-NOT-RED", row["name"], row["bare_exit"]))
    if row["kind"].startswith("leaf") and row["bare_exit"] == 1 \
            and row["kind"] != "leaf-v2":
        # a predicted leaf that the gate actually rejects: not a leaf
        failed.append(("PREDICTED-LEAF-REJECTED", row["name"],
                       row["bare_exit"]))
print("\nREQUIRED-VERDICT FAILURES:", failed if failed else "none")
```

`scratch/realforge.py` (real receipt-1.json under the official invocation):

```python
#!/usr/bin/env python3
"""Apply leaf forgeries to the REAL committed round-18 receipt-1.json and run
the gate with the official invocation (4 pins + --require-schema v3)."""
import copy
import json
import os
import subprocess

ROOT = "/tmp/kama-r18-falsify-GateCaptureHashes"
GATE = os.path.join(ROOT, "tests", "llamacpp-live", "check-receipt.py")
REAL = os.path.join(ROOT, ".ufo", "waves", "round-18", "live",
                    "receipt-1.json")
PINS = ["--expect-model-sha256",
        "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d",
        "--expect-server-sha256",
        "b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804",
        "--expect-probe-sha256",
        "36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3",
        "--expect-tool-sha256",
        "dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b"]

with open(REAL) as fh:
    base = json.load(fh)
print("real receipt:", base["schema"], "outcome:", base.get("outcome"),
      "loading_observed:", base.get("loading_observed"),
      "port:", base.get("port"))

# pristine control under official invocation
p0 = os.path.join(ROOT, "scratch", "real-pristine.json")
with open(p0, "w") as fh:
    json.dump(base, fh, indent=1, sort_keys=True)
r = subprocess.run(["/usr/bin/python3", GATE, p0, *PINS,
                    "--require-schema", "v3"], capture_output=True, text=True)
print(f"{'pristine':42} exit={r.returncode} {r.stdout.strip()}")


def health200_index(rec):
    for i, t in enumerate(rec["transitions"]):
        if t.get("path") == "/health" and t.get("status") == 200:
            return i
    return None


MUTS = [
    ("real-props-status-503",
     lambda x: x["captures"]["props"].update(status=503)),
    ("real-slots-digest-zero",
     lambda x: x["captures"]["slots"].update(body_sha256="0" * 64)),
    ("real-health-error-set",
     lambda x: x["captures"]["health"].update(error="ConnectionResetError")),
    ("real-summary-null",
     lambda x: [p["result"].update(summary=None) for p in x["probes"]]),
    ("real-internal-fault-key-absent",
     lambda x: x.pop("internal_fault", None)),
]


def _health_transition(x):
    i = health200_index(x)
    assert i is not None, "no /health 200 transition in real receipt"
    x["transitions"][i]["body_sha256"] = "0" * 64


MUTS.append(("real-health-transition-digest-zero", _health_transition))

# red control on real receipt: models capture 503 (M7)
MUTS.append(("ctl-real-models-status-503",
             lambda x: x["captures"]["models"].update(status=503)))

outdir = os.path.join(ROOT, "scratch", "real-cases")
os.makedirs(outdir, exist_ok=True)
for name, fn in MUTS:
    x = copy.deepcopy(base)
    fn(x)
    path = os.path.join(outdir, name + ".json")
    with open(path, "w") as fh:
        json.dump(x, fh, indent=1, sort_keys=True)
    p = subprocess.run(["/usr/bin/python3", GATE, path, *PINS,
                        "--require-schema", "v3"], capture_output=True,
                       text=True)
    tag = "LEAF-ACCEPTED" if (name.startswith("real-")
                              and p.returncode == 0) else (
        "REJECTED" if p.returncode == 1 else f"exit={p.returncode}")
    print(f"{name:42} exit={p.returncode} {p.stdout.strip()}  -> {tag}")
```

## Cleanup

Clone and scratch removed at finish (`rm -rf /tmp/kama-r18-falsify-GateCaptureHashes`); nothing copied back except this report and the inlined source above. No installs recorded. No seat-owned listener remains (none was ever opened).
