VERDICT: confirm — all seven behaviour-bearing H-mutant anchors still occur exactly once in current check.py (byte-identical to the round-17 attack target); H4 and H8 remain non-mutants.

# Scope

Read-only recon for C2 (calibration). I did not re-run any mutant or detector. Anchor counts, hashes and line numbers below are observed on current bytes; every "distinguishing shape" is a static derivation from the gated code paths unless marked otherwise.

Round-17 advice read: `.ufo/waves/round-17/falsify/advice/MutC1Preregistered.md` (H1–H4) and `MutC1Preregistered2.md` (H5–H8).

Target file: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py`, sha256 `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099`, identical to the round-18 frozen copy `.ufo/waves/round-18/frozen/tests_probe-verdicts_check.py` and to the hash both round-17 seats recorded as pristine. `git log 54a29268..e75cf680 -- tests/probe-verdicts/check.py` printed nothing, so no round-17 mutant anchor has drifted in line content or number.

# Anchor verification (grep -c, fixed strings)

| Mutant | Anchor (current bytes) | `grep -c` | Line |
|---|---|---|---|
| H1 | `and record["reason"] == expected["reason"]` | 1 | 475 |
| H2 | `record["verdict"] == expected["verdict"]` | 1 | 474 |
| H3 | `r.get("method") == "GET"` | 1 | 374 |
| H4 | `test, record["verdict"])` | 1 | 469 |
| H5 | `record["served_model"] == record["served_model_expected"]` | 1 | 471 |
| H6 | `"stub accepted no requests; probe never "` (insertion anchor) | 1 | 457 |
| H7 | `row = rows[0]` | 1 | 397 |
| H8 | `len(rows)` (proposed cardinality guard) | **0** | — |

Observed quotes backing the table: `check.py:475` "and record["reason"] == expected["reason"]"; `check.py:474` "record["verdict"] == expected["verdict"]"; `check.py:374` "return any(r.get("method") == "GET""; `check.py:470-471` "record["served_model_ok"] = (" / "record["served_model"] == record["served_model_expected"])"; `check.py:397` "row = rows[0]"; `check.py:457-458` "record["error"] = ("stub accepted no requests; probe never " / "reached a listening socket")".

The only `record["passed"]` assignment is `check.py:473` ("record["passed"] = ("), and the default is `check.py:428` (""passed": False,"). H6 is therefore a genuine new statement insertion, not a rewrite of an existing one.

# H1 — reason casefolds

Exact edit (`check.py:475`):

```python
-            and record["reason"] == expected["reason"]
+            and record["reason"].casefold() == expected["reason"].casefold()
```

Distinguishing probe-output shape ([INFERENCE]): an otherwise honest `ReadyControls.expect-exact-id` row with `reason` uppercased, e.g.

```json
{"rows":[{"verdict":"MODEL_OK","reason":"MATCHED","drift":false,"served_model":"kama-ready"}]}
```

Against the matrix expectation `"verdict": "MODEL_OK", "reason": "matched", "exit": 0` (`ReadyControls.json:42-43`). Original: reason conjunct false → `passed` false → check exit 1. Mutant: every other conjunct is untouched (verdict, exit, drift, served_model, route), so the row passes and the check exits 0.

Why round 17 missed it: the only reason-corrupting fault appends a suffix, `fault-controls.py:284` "row["reason"] = str(row.get("reason")) + "-forged"". A suffix survives casefolding, so F1 still fails H1 and reports `detected: true`. No F0–F8 input and no matrix row ever varies only letter case — the probe's reason vocabulary is entirely lowercase (e.g. `kama-probe.sh:507` "C_REASON=llamacpp-loading", `:539` "C_REASON=matched").

# H2 — verdict strips

Exact edit (`check.py:474`):

```python
-            record["verdict"] == expected["verdict"]
+            record["verdict"].strip() == expected["verdict"].strip()
```

Distinguishing probe-output shape ([INFERENCE]): pad a **non-model-verdict** row. On `LoadingEnvelope.canonical-alias` (`LoadingEnvelope.json:25` "expected": {"verdict": "MODEL_LOADING", "reason": "llamacpp-loading", "exit": 2}) emit `verdict: "MODEL_LOADING "` with `served_model: "-"`, `drift: true`, honest exit 2 and GET /v1/models recorded. Original fails the verdict conjunct; mutant strips and passes, and every other conjunct holds — `expected_served_model` maps any verdict outside (`MODEL_OK`,`MODEL_MISMATCH`) to `"-"` (`check.py:354-355`), the row's served value is `"-"`, and the drift predicate `record["drift"] == (record["verdict"] != "MODEL_OK")` is still true for the padded string (`check.py:479`).

Witness-design trap, observed in code: padding a `MODEL_OK` row instead does **not** distinguish the mutant, because the raw padded verdict makes `expected_served_model` return `"-"` while the row carries `"kama-ready"`, so `served_model_ok` stays false. The round-17 advice flagged this only as a vague possibility ("padded MODEL_OK can instead trip those other guards"); the loading row is the clean witness.

Why round 17 missed it: F4 only lowercases — `fault-controls.py:289` "row["verdict"] = v.lower()" — which `strip()` cannot undo, so F4 remains detected. No fault and no matrix row contains whitespace in a verdict.

# H3 — route match ignores HTTP method

Exact edit (`check.py:374-376`):

```python
-    return any(r.get("method") == "GET"
-               and r.get("path", "").split("?", 1)[0] == "/v1/models"
-               for r in requests)
+    return any(r.get("path", "").split("?", 1)[0] == "/v1/models"
+               for r in requests)
```

Distinguishing probe-output shape ([INFERENCE]): a cached honest `MODEL_OK` row replayed by a wrapper that, on the live stub port, issues exactly one request `HEAD /v1/models` and never a GET. The stub records it: `check.py:216` "self._seen.append({"method": self.command, "path": self.path})" runs before route lookup, and `check.py:255-258` serves every method through the same responder ("if name.startswith("do_"): / return self._respond"). Original: `route_ok` false → `passed` false. Mutant: path present → `route_ok` true → row passes.

Why round 17 missed it: F6 exercises the wrong **path**, not the wrong method — `fault-controls.py:243` "hit("/health")                       # reachable port, wrong route". Under F6 the stub never sees `/v1/models` in any form, so the path conjunct is false for original and mutant alike and `route_ok` is identical `false` in both. `F6_ROWS = ROWS_FULL[:-1]` (`fault-controls.py:95`) also excludes the closed-port row; method is never varied anywhere.

# H4 — not a mutant (no behaviour-bearing site)

`check.py:468-469` already reads

```python
        record["served_model_expected"] = expected_served_model(
            test, record["verdict"])
```

keyed on the **observed** verdict, as its own docstring states at `check.py:350` ("So, keyed on the OBSERVED verdict"). There is no expected-verdict baseline to weaken, so the preregistered edit is an identity. Distinguishing shape: none — pristine and "mutated" bytes are identical and both accept the same inputs. It must stay outside the mutant denominator (round-17 advice already says so).

# H5 — served IDs normalise (lower + strip `.gguf`)

Exact edit (`check.py:470-471`):

```python
-        record["served_model_ok"] = (
-            record["served_model"] == record["served_model_expected"])
+        record["served_model_ok"] = (
+            [sid.lower().removesuffix(".gguf")
+             for sid in (record["served_model"] or "").split(",")]
+            == [sid.lower().removesuffix(".gguf")
+                for sid in record["served_model_expected"].split(",")])
```

Distinguishing probe-output shape ([INFERENCE]): the honest `ReadyControls.expect-exact-id` row (`expected_served_model` = `"kama-ready"`, derived from the stub body's `data[0].id`) with `served_model` changed to `"KAMA-READY"` — or `"kama-ready.GGUF"`, which the `.lower()` normalises before `.removesuffix(".gguf")` removes it. Original: `served_model_ok` false → row fails. Mutant: `"kama-ready" == "kama-ready"` → row passes with all other conjuncts honest.

Why round 17 missed it: F5 substitutes a wholly different id — `fault-controls.py:293` "row["served_model"] = "kama-forged-id"" — which no case/suffix normalisation maps onto `kama-ready`, so F5 stays detected. Neither the pair nor any fault emits a case- or extension-only variant of the correct id.

# H6 — no-request branch accepts

Exact edit (insert between `check.py:458` and `check.py:459`):

```python
             record["error"] = ("stub accepted no requests; probe never "
                                "reached a listening socket")
+            record["passed"] = True
             return record
```

Distinguishing probe-output shape ([INFERENCE]): on a **stub-mode** row (server bound, so `server is not None`), a wrapper that makes zero requests to the port, prints a cached honest single-row document, and exits 0. Original: the `not record["requests"]` branch records the "stub accepted no requests" error and returns with the default `passed: False` → check exit 1. Mutant: `passed: True` → check exit 0 (the row's verdict/reason/route fields remain null because the return happens before `probe_output_row`).

Why round 17 missed it: no fault reaches "bound stub, zero recorded requests, valid stdout". F7 hangs and leaves through the separate timeout return (`check.py:447-451`). F8 runs the real probe first (`fault-controls.py:258` "p = subprocess.run(["bash", real] + args, capture_output=True, text=True)") and then corrupts stdout, so requests are non-empty and the row fails on malformed output, not here. F6 touches `/health`, which also makes `requests` non-empty. The fault table has no zero-request mode at all.

# H7 — grades the last row

Exact edit (`check.py:397`):

```python
-    row = rows[0]
+    row = rows[-1]
```

Distinguishing probe-output shape ([INFERENCE], and the witness is already executed evidence for admission): two rows, honest first, forged last, e.g.

```json
{"rows":[{"verdict":"MODEL_OK","reason":"matched","drift":false,"served_model":"kama-ready"},
         {"verdict":"FORGED_SECOND_ROW","reason":"ungraded-second-row","drift":true,"served_model":"not-the-served-id"}]}
```

Original grades `rows[0]` → row passes, check exit 0. Mutant grades the forged last row → verdict/reason/served conjuncts fail → exit 1. The round-17 H8 seat actually ran this exact shape against pristine bytes and observed `{"tests":1,"passes":1,"failures":0,...}` with exit 0, so the admission half is observed, not inferred; only the mutant's rejection is inferred.

Why round 17 missed it: every F8 variant is single-row or row-less — `fault-controls.py:171-187` supplies `[]`, `{"rows":[]}`, `{"rows":[["x"]]}`, `{"rows":[null]}`, non-JSON and non-UTF-8. None carries two distinguishable objects, so `rows[0]` and `rows[-1]` are the same element. Additionally the fault wrapper itself always mutates the first row (`fault-controls.py:279` "row = doc["rows"][0]"), so F1–F5 structurally cannot exercise index sensitivity. The real probe emits exactly one row per invocation (`kama-probe.sh:841-849`, cli-override arm setting `EV_N=1`), so the before/current pair can never observe the divergence either.

# H8 — not a mutant (no cardinality guard exists)

`grep -cF 'len(rows)' check.py` = **0**. The documented contract is first-element grading, not one-row grading: `check.py:382-383` "Contract: one JSON object whose "rows" is a non-empty list"; `check.py:395-396` rejects only a missing/empty list; `check.py:397` selects the first element. There is no exact-one-row condition to weaken, so there is no old→new edit. The two-row acceptance is pre-existing policy, and the same document is simultaneously H7's kill witness.

# Cross-cutting: why the round-17 detector set is blind to these six

- F0–F8 corrupt exactly one field each with a character-level substitution that the mutants do not invert: suffix (F1), lowercase (F4), id replacement (F5), boolean flip (F3), exit flip (F2). Strips, casefolds and `.gguf` removal are none of those.
- The remaining faults vary **behaviour**, not field spelling: wrong path (F6), timeout (F7), malformed cardinality/encoding (F8).
- The pair comparator cannot help: it only re-observes two real probe binaries over the 72 matrix rows and compares `SIG_FIELDS` (`mutants.py:118`), with requests reduced to a unique `(method, path)` set (`mutants.py:117-121`). Both probes emit lowercase reasons, uppercase verdicts, exact ids, single rows, and always at least one `/v1/models` request — so no arm ever produces a shape where these conjuncts disagree.
- Consequence for C2 counting: the live survivor set from round 17 is H1, H2, H3, H5, H6, H7 (six), with H4 and H8 excluded as non-mutants. Any round-18 detector that claims a survivor reduction must add inputs that emit the shapes above (case-only reason, whitespace-only verdict on a non-model verdict, HEAD-only `/v1/models`, case/extension-only id, zero-request valid stdout, two-row honest-first document), or target an independent conjunct as `MutControlsSelf`/`MutFaultControlsSelf` propose.

# Limitations

- I did not execute the mutants, the matrix, `fault-controls.py` or any probe. Mutant outcomes quoted from the two round-17 advice files are that seat's executed evidence; the distinguishing shapes and per-conjunct derivations here are [INFERENCE] from `check.py` line-by-line reading, except the H7 admission witness which round 17 ran and recorded.
- No port was bound, no llama-server was started, nothing was written outside this report. No tool was installed or updated.
- The H2 loading-row witness depends on the matrix row's honest served value being `"-"`; that follows from `expected_served_model`'s `MODEL_LOADING` branch (`check.py:354-355`) and `kama-probe.sh:455` ("C_VERDICT='' C_SERVED='-'"), not from a live probe run.
