VERDICT: partial — every canonical null forgery (non-loading null, wrong reason/evaluated, laundered ready-capture 503, real failure+null) is INVALID and legitimate no-loading stays NOT-EVALUATED, but two forged transition-row encodings (trailing-slash path, string status) launder an observed /v1/models 503 into exit-3 NOT-EVALUATED.

# GateNullLicense — round-18 falsify (seat KamaR18.GateNullLicense)

## Target and environment

- Lane master `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, separate clone:
  `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-GateNullLicense`
  then `git switch -c seat/GateNullLicense 1c325b2e58...`. All runtime checks ran in that clone.
  `git rev-parse HEAD` → `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`.
- Gate under attack: `tests/llamacpp-live/check-receipt.py`
  sha256 `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`.
- All receipts synthetic JSON; **no sockets, no listeners, no servers** were created by this seat.
- Installs: none (python3 stdlib only; no pacman/uv/npx/cargo/npm activity).

## Green pristine baseline (required for kill claims)

Executed: `python3 tests/llamacpp-live/check-receipt.py --selftest` → exit 0,
stdout `selftest: 5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations + unreadable case rejected`
— byte-identical to the official `.ufo/waves/round-18/runs/gate-selftest.stdout` read from the same clone.

## Controls (legitimate behavior preserved)

| case | receipt | exit | stdout head |
|---|---|---|---|
| control-no-loading-legit | selftest's `v3-no-loading-not-evaluated` builder (check-receipt.py:1852-1871), replicated verbatim | 3 | `NOT-EVALUATED ...` |
| control-full-pass-legit | `_selftest_receipt_v3()` | 0 | `VALID ...` |

## Findings by severity

### F1 MEDIUM — transition-row encoding seam launders an observed /v1/models 503 to NOT-EVALUATED

`model_503_rows` selects transitions with exact Python equality
`path == "/v1/models" and status == 503` (check-receipt.py:540-544); everything else in a
transitions row is never schema-checked. `no_loading_observed` (check-receipt.py:1289-1292)
therefore stays true, the null license at :806-813 holds, and `main` prints NOT-EVALUATED
exit 3 (:2104-2109) even though the receipt's own `transitions` array visibly records a 503
against the models endpoint. Two executed forgeries (envelope body + digest copied from the
real 503 row, appended to the legit no-loading receipt):

- `A3-transition-503-path-trailing-slash` — row `{"path": "/v1/models/", "status": 503, ...}` → **exit 3** `NOT-EVALUATED`
- `A3-transition-503-string-status` — row `{"path": "/v1/models", "status": "503", ...}` → **exit 3** `NOT-EVALUATED`

This violates the KQ24 letter ("only when no /v1/models 503 was observed") for forged
receipts and is the round-18 M7 laundering class one encoding deeper: the selftest's own
standard rejects a forged `captures.models.status=503` (my `A3-models-capture-503-ids-intact`
re-run: exit 1, 4 problems, `models_alias_id: captures.models.status 503 != 200 (round-18 RevTriStateDesign)`),
yet an equally visible 503 in `transitions` is launderable. Same-class unread variants:
`"/V1/models"` casing, `503.0`, status `True`/`"503 "`.

Bounded impact: the producer cannot emit these encodings — `tools/kama-llamacpp-live.py`
records `'status': resp.status` (int, :512, :428) and only literal `'/v1/models'`/`'/health'`
path strings (:580, :612, :626). So there is no live-tool laundering path; this is a
gate re-derivation hardening + selftest-coverage seam, exactly the kind of forge the gate
is built to invalidate. Advice: type/pin transitions rows in the v3 schema floor
(int status, exact known paths — or normalize before matching) and add both forgeries as
`mut3` cases expecting 1.

### F2 LOW — selftest gap behind F1

`mut3` cases (check-receipt.py:1884-1965) cover a 503 row with a **non-exact body** and a
**truncated row**, but no mutant carries a 503 row whose path spelling or status type
escapes the :540-544 equality. The named-survivor set is unaffected (C2 separation);
this is a fresh-denominator finding only.

### F3 INFO (design boundary, not a defect) — non-models 503s don't block the null license

`A3-health-503-transition-noise` — transitions row `{"path": "/health", "status": 503}` with
the loading check null → exit 3. Consistent with the v3 design: the loading observation is
defined as /v1/models 503 rows (S036 binding, M7 fix, check-receipt.py:526-529 restricts
`loading_503.path` to `/v1/models` in v3), and the ready `/health` capture is graded
separately by `health_ready`. Recorded so the boundary stays visible; no action requested.

## Confirmed: all four attack classes require INVALID (29 forgeries, 29 INVALID)

Exact gate evidence, all against the legit no-loading receipt unless stated:

1. **Forge null on a non-loading check** — each of the 10 non-loading required ids nulled
   (`passed=None, evaluated=False, reason set, outcome="not-evaluated"`): all exit 1.
   Representative problem line (health_ready):
   `check 'health_ready': only loading_envelope_graded may be unevaluated, and only with no /v1/models 503`
   (from :806-810). The conjunct `cid != "loading_envelope_graded"` fires for every
   non-loading id regardless of loading state, so the license is id-scoped, not state-scoped.
2. **Null with wrong reason / evaluated** — reason ` "no-loading-503-observed "` (trailing
   space), `NO-LOADING-503-OBSERVED`, `None`, `""`, `"loading-unobserved"`, missing key:
   all exit 1 (:811-813, exact string compare). `evaluated=True` with `passed=None`: exit 1,
   `check 'loading_envelope_graded': evaluated true but passed is null` + `evaluated True != re-derived False`
   (:797-798, :1304-1307). `evaluated` key removed: exit 1 (:794-795). Forged
   `observed.loading_observed=True` or `distinct_bodies=3`: exit 1 via the re-derived
   `expected_observed` comparison (:1308-1320). Null + outcome `"pass"`: exit 1
   (outcome re-derivation :1355-1368).
3. **Observed bad503 laundered to null** — canonical encodings all INVALID:
   exact-path 503 row re-added → exit 1 with 7 problems (`loading_observed False != whether
   transitions contain a /v1/models 503` :551-553; `passed None != re-derived False`;
   `evaluated False != re-derived True`; bodies/dropped/first-loading mismatches
   :1210-1214, :1236-1242, :1259-1263, :1300-1307); ready models capture 503 ids intact →
   exit 1 (M7 enforcement). Residual encoding-only escapes: see F1.
4. **Real failure + null** — served-id drift on the ok probe
   (`probe ok: served_model 'someone-elses-model' != alias 'kama-live-probe'`, :733-736) +
   null retained → exit 1; teardown `returncode=1` contradiction + null → exit 1 (3 problems).
   Additionally any `passed=false` is itself fatal (:792-793), and `states`-based outcome
   re-derivation (:1355-1368) blocks `fail`/`not-evaluated` mislabels, so a real failure
   can neither pass nor launder to NOT-EVALUATED.

Outcome-level forgeries: `outcome="not-evaluated"` on a fully-evaluated pass receipt →
exit 1; full pass with the licensed null flipped to `outcome="pass"` → exit 1.

## Residual risk and verification gaps

- Attacked the gate only. The producer's null emission (`tools/kama-llamacpp-live.py:857-864`
  `_check`) was read (:858-864 requires a reason for every null), not executed against a live
  server — the lane's no-server bound forbids it, and the official live receipts
  (`.ufo/waves/round-18/live/receipt-1..3.json`) are all pass receipts, so real-run
  NOT-EVALUATED behavior was not exercised end-to-end. Gate-side re-derivation is the
  enforcement actually claimed, and that is what was tested.
- 31/31 harness cases matched their declared expected exits (29 forgery INVALIDs + 2
  controls). These are fresh-denominator forgeries, separate from the round-17 named set;
  nothing here was added to any retained counter.
- F1 escapes require the forger to rewrite recorded transition evidence into encodings the
  producer never emits; they do not touch the legitimate no-loading exit-3 path (control held).
- Inconclusive-by-bound: none of the four attack classes produced a timeout, own-fault, or
  missing site; no pristine baseline was invalid.

## Exact experiment source (falsify_gate_null.py, run from the clone root)

```python
#!/usr/bin/env python3
"""GateNullLicense falsify harness.

Forgeries the v3 null license of tests/llamacpp-live/check-receipt.py:
  A1 forge null on a non-loading check (each of the 10 other required ids)
  A2 null with wrong/missing reason, wrong evaluated
  A3 observed bad503 laundered to null (transitions row encoding seams)
  A4 real failure + null
Controls: the legitimate no-loading receipt must stay exit 3 NOT-EVALUATED
and the full pass receipt exit 0 VALID.

Runs the gate as a subprocess exactly like its own selftest does.
No sockets are opened; every receipt is synthetic JSON.
"""
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GATE = os.path.join(HERE, "tests", "llamacpp-live", "check-receipt.py")
OUTDIR = os.path.join(HERE, "falsify-run")
os.makedirs(OUTDIR, exist_ok=True)

spec = importlib.util.spec_from_file_location("gate", GATE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

EXPECTS = ["--expect-model-sha256", gate.MODEL_SHA,
           "--expect-server-sha256", gate.SERVER_SHA,
           "--expect-probe-sha256", gate.PROBE_SHA,
           "--expect-tool-sha256", gate.TOOL_SHA]

NON_LOADING_V3 = [
    "health_ready", "models_alias_id", "models_owned_by_llamacpp",
    "metrics_not_enabled", "props_alias", "probe_model_ok",
    "probe_mismatch", "teardown_graceful", "teardown_port_closed",
    "model_unchanged",
]


def legit_no_loading():
    """Byte-faithful copy of the selftest's v3-no-loading-not-evaluated
    builder (check-receipt.py:1852-1871)."""
    r = gate._selftest_receipt_v3()
    r["transitions"] = [
        row for row in r["transitions"]
        if not (row.get("path") == "/v1/models"
                and row.get("status") == 503)]
    r.update(loading_503=None, loading_503_bodies=[],
             loading_bodies_dropped=0, loading_observed=False,
             loading_envelope_exact=None, outcome="not-evaluated")
    c = next(c for c in r["checks"]
             if c["id"] == "loading_envelope_graded")
    c.update(passed=None, evaluated=False)
    c["observed"].update({
        "loading_observed": False,
        "distinct_bodies": 0,
        "bodies_dropped": 0,
        "total_503_responses": 0,
        "all_exact": None,
        "exact": None,
        "not_evaluated_reason": "no-loading-503-observed",
    })
    return r


def null_check(r, cid):
    c = next(c for c in r["checks"] if c["id"] == cid)
    c.update(passed=None, evaluated=False)
    c.setdefault("observed", {})["not_evaluated_reason"] = \
        "no-loading-503-observed"


def loading_null_wrong_observed(r, key, value):
    c = next(c for c in r["checks"]
             if c["id"] == "loading_envelope_graded")
    c["observed"][key] = value


def run_case(name, receipt, want, note=""):
    path = os.path.join(OUTDIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh)
    proc = subprocess.run(
        [sys.executable, GATE, path, *EXPECTS],
        capture_output=True, text=True)
    first = proc.stdout.splitlines()[0] if proc.stdout else ""
    ok = proc.returncode == want
    print(f"{'PASS' if ok else 'DIFF'} {name}: exit {proc.returncode} "
          f"(want {want}) :: {first[:150]}")
    if not ok and note:
        print(f"     note: {note}")
    return {"name": name, "exit": proc.returncode, "want": want,
            "stdout_first": first, "sha256": hashlib.sha256(
                json.dumps(receipt, sort_keys=True).encode()).hexdigest(),
            "match": ok}


def main():
    results = []

    # Controls -------------------------------------------------------------
    legit = legit_no_loading()
    results.append(run_case("control-no-loading-legit",
                            copy.deepcopy(legit), 3,
                            "must stay NOT-EVALUATED"))
    results.append(run_case("control-full-pass-legit",
                            gate._selftest_receipt_v3(), 0,
                            "must stay VALID"))

    # A1: forged null on every non-loading check id ------------------------
    for cid in NON_LOADING_V3:
        r = legit_no_loading()
        null_check(r, cid)
        results.append(run_case(f"A1-null-on-{cid}", r, 1,
                                "non-loading check must never be null"))

    # A2: wrong / missing reason and evaluated states ----------------------
    for label, key, value in [
            ("trailing-space", "not_evaluated_reason",
             "no-loading-503-observed "),
            ("upper-case", "not_evaluated_reason",
             "NO-LOADING-503-OBSERVED"),
            ("none", "not_evaluated_reason", None),
            ("empty", "not_evaluated_reason", ""),
            ("wrong-word", "not_evaluated_reason", "loading-unobserved")]:
        r = legit_no_loading()
        loading_null_wrong_observed(r, key, value)
        results.append(run_case(f"A2-reason-{label}", r, 1))

    r = legit_no_loading()
    c = next(c for c in r["checks"]
             if c["id"] == "loading_envelope_graded")
    c["observed"].pop("not_evaluated_reason")
    results.append(run_case("A2-reason-missing", r, 1))

    r = legit_no_loading()
    c = next(c for c in r["checks"]
             if c["id"] == "loading_envelope_graded")
    c["evaluated"] = True
    results.append(run_case("A2-evaluated-true-while-unobserved", r, 1))

    r = legit_no_loading()
    c = next(c for c in r["checks"]
             if c["id"] == "loading_envelope_graded")
    c.pop("evaluated")
    results.append(run_case("A2-evaluated-key-missing", r, 1))

    r = legit_no_loading()
    loading_null_wrong_observed(r, "loading_observed", True)
    results.append(run_case("A2-observed-loading-forged-true", r, 1))

    r = legit_no_loading()
    loading_null_wrong_observed(r, "distinct_bodies", 3)
    results.append(run_case("A2-observed-distinct-forged", r, 1))

    # A3: laundering a real 503 into the no-loading license ----------------
    base503 = next(row for row in gate._selftest_receipt_v3()["transitions"]
                   if row.get("path") == "/v1/models"
                   and row.get("status") == 503)

    r = legit_no_loading()
    forged = dict(base503)
    forged["path"] = "/v1/models/"
    r["transitions"].append(forged)
    results.append(run_case("A3-transition-503-path-trailing-slash", r, 3,
                            "HYPOTHESIS: 503 row visible in transitions "
                            "but laundering exits 3 if uncounted"))

    r = legit_no_loading()
    forged = dict(base503)
    forged["status"] = "503"
    r["transitions"].append(forged)
    results.append(run_case("A3-transition-503-string-status", r, 3,
                            "HYPOTHESIS: string status invisible to "
                            "loading re-derivation"))

    r = legit_no_loading()
    forged = dict(base503)
    r["transitions"].append(forged)
    results.append(run_case("A3-null-although-503-present", r, 1,
                            "exact-path 503 row must kill the null"))

    r = legit_no_loading()
    r["captures"]["models"]["status"] = 503
    results.append(run_case("A3-models-capture-503-ids-intact", r, 1,
                            "M7 ready-capture 503 must not launder"))

    r = legit_no_loading()
    forged = {"path": "/health", "status": 503, "error": None,
              "body_sha256": hashlib.sha256(b"{}").hexdigest(),
              "body": "{}", "repeats": 0, "t_ms": 5}
    r["transitions"].append(forged)
    results.append(run_case("A3-health-503-transition-noise", r, 3,
                            "v3 loading is models-only; expect 3 by "
                            "design"))

    # A4: real observed failure + null -------------------------------------
    r = legit_no_loading()
    ok_probe = next(p for p in r["probes"] if p["expect"] == gate.ALIAS)
    row = ok_probe["result"]["rows"][0]
    row["served_model"] = "someone-elses-model"
    results.append(run_case("A4-served-id-drift-plus-null", r, 1,
                            "real probe drift must dominate the null"))

    r = legit_no_loading()
    r["teardown"]["returncode"] = 1
    r["teardown"]["alive_at_teardown_start"] = True
    results.append(run_case("A4-teardown-rc1-plus-null", r, 1,
                            "graceful-teardown contradiction"))

    # A7: outcome-level forgeries ------------------------------------------
    r = gate._selftest_receipt_v3()
    r["outcome"] = "not-evaluated"
    results.append(run_case("A7-outcome-not-evaluated-no-null", r, 1))

    r = legit_no_loading()
    r["outcome"] = "pass"
    results.append(run_case("A7-outcome-pass-with-null", r, 1))

    n_ok = sum(1 for x in results if x["match"])
    print(f"\n{len(results)} cases, {n_ok} matched the required exit, "
          f"{len(results) - n_ok} diverged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Command: `python3 falsify_gate_null.py` (clone root) → `31 cases, 31 matched the required exit, 0 diverged`, harness exit 0. Per-forged-receipt sha256 digests are recorded by the harness over canonical `json.dumps(sort_keys=True)`; the raw forged JSONs lived only in `<clone>/falsify-run/` and were removed with the clone.

## Cleanup attestation

- Clone and scratch `/tmp/kama-r18-falsify-GateNullLicense` removed before finish (removal command and its exit recorded in the session log).
- No `git`/`jj` writes anywhere in `/home/vgpnk/Projects/shokunin/kama-shokunin`; no lane index, fleet, or frozen-evidence mutation; production files untouched; nothing copied back except this report and the embedded source above.
- No listener was ever opened by this seat (no bind/connect in any executed code); final `ss -ltn` check shows nothing on 8080/34113 and no seat-owned process group remains.
