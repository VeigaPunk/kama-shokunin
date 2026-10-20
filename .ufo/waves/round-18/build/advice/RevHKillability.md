VERDICT: confirm — H1–H3 and H5–H7 are all non-equivalent; each has a concrete probe fault rejected by current check.py and accepted by its mutant.

# Scope and axes

Axes: **calibration** (does each named mutation alter observable acceptance?), **fault distinguishability** (a concrete probe response that splits current from mutant), and **isolation** (no lane source changes; loopback-only scratch execution).

I tested exactly H1–H3 and H5–H7 from the two preregistered advice files, against the lane's observed current `tests/probe-verdicts/check.py`. Its SHA-256 was `ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099`, matching the round-18 frozen checker. Each mutant was applied only to a scratch copy; all witnesses used the single matrix row `ReadyControls.expect-exact-id`. For every row below, the current checker exited 1 with `passed=false`; the described mutant exited 0 with `passed=true`. These are distinguishability proofs, not a claim that the existing `fault-controls.py` detects these faults.

# Findings by potential impact if the mutation were shipped

Severity here ranks the false-acceptance behavior of the isolated mutation, not a defect in the unmutated current source.

## High — H6: no-request branch can pass

**Decision: witness exists; not equivalent.** The probe made no request to the live stub but emitted a JSON `MODEL_OK` / `matched` row. Current result: `requests=[]`, `route_ok=false`, error `stub accepted no requests; probe never reached a listening socket`, exit 1. H6 result: the same error record had `passed=true`, exit 0.

- Current branch: `tests/probe-verdicts/check.py:454-459` — “if server is not None and not record[\"requests\"]:”.
- Mutation: `MutC1Preregistered2.md:42-44` — “record[\"passed\"] = True”.

## Moderate — H3: non-GET request satisfies route check

**Decision: witness exists; not equivalent.** The probe sent `POST /v1/models` and emitted an otherwise matching `MODEL_OK` / `matched` row. Current recorded `route_ok=false` and exited 1; H3 recorded `route_ok=true` and exited 0.

- Current route predicate: `tests/probe-verdicts/check.py:374-376` — “r.get(\"method\") == \"GET\"”.
- Mutation: `MutC1Preregistered.md:71-72` — “r.get(\"path\", \"\").split(\"?\", 1)[0] == \"/v1/models\"”.

## Moderate — H5: suffix normalization accepts a different served ID

**Decision: witness exists; not equivalent.** The stub's expected ID was `kama-ready`; the probe reported `kama-ready.gguf`, with the other `MODEL_OK` fields correct. Current `served_model_ok=false`, exit 1; H5 `served_model_ok=true`, exit 0.

- Current exact comparison: `tests/probe-verdicts/check.py:470-471` — “record[\"served_model\"] == record[\"served_model_expected\"]”.
- Mutation: `MutC1Preregistered2.md:29-34` — “sid.lower().removesuffix(\".gguf\")”.
- Fixture identity: `tests/probe-verdicts/ReadyControls.json:15` — “\"id\": \"kama-ready\"”.

## Moderate — H7: a good last row masks a bad first row

**Decision: witness exists; not equivalent.** The probe returned two objects: first `MODEL_OK` with forged reason `forged`, then the correct `MODEL_OK` / `matched` object. Current grades the first and exits 1; H7 selects the last and exits 0.

- Current selection: `tests/probe-verdicts/check.py:397` — “row = rows[0]”.
- Mutation: `MutC1Preregistered2.md:53` — “row = rows[-1]”.

## Low — H1: case-folding accepts an incorrect reason

**Decision: witness exists; not equivalent.** The probe returned reason `MATCHED` instead of expected `matched`, with the remaining row fields and GET request correct. Current exited 1; H1 exited 0.

- Current exact comparison: `tests/probe-verdicts/check.py:475` — “record[\"reason\"] == expected[\"reason\"]”.
- Mutation: `MutC1Preregistered.md:31` — “record[\"reason\"].casefold() == expected[\"reason\"].casefold()”.

## Low — H2: trimming accepts a whitespace-corrupted verdict

**Decision: witness exists; not equivalent.** The probe returned verdict `MODEL_OK ` (one trailing space), `drift=true`, reason `matched`, and served model `-`. These values keep the separate drift invariant and observed-verdict-derived served-model check consistent. Current exited 1; H2's stripped comparison exited 0.

- Current exact comparison: `tests/probe-verdicts/check.py:474` — “record[\"verdict\"] == expected[\"verdict\"]”.
- Mutation: `MutC1Preregistered.md:51` — “record[\"verdict\"].strip() == expected[\"verdict\"].strip()”.

**Equivalent mutants:** none among the six assigned mutations. Each has a concrete current-reject/mutant-accept witness; none is merely inferred from a detector-survival report.

# Verification, residual risk, and gaps

- Ran 12 checker invocations sequentially: current and corresponding mutant once for each witness. Observed paired exit/pass results were `1/false` versus `0/true` for all six; all stdout documents parsed and contained the expected single matrix record. Scratch probe/checker/matrix copies were removed afterward.
- The checker starts each stub at `127.0.0.1` on port `0` (`check.py:437` — “ThreadingHTTPServer((\"127.0.0.1\", 0), handler)”) and shuts it down/closes it in `finally` (`check.py:487-490`). Post-run `ss -ltnp` still displayed host listeners, including Python processes; they were not attributed to this run, stopped, or modified. No llama-server was started.
- The `lsp` device was unavailable: the `xd://lsp` lookup returned “No such tool”. No LSP status/references/definition/diagnostics were available; the evidence above is from direct executions plus cited source text, not grep-based semantic claims.
- These runs establish existence of distinguishing inputs, not completeness of the mutant set, a general correctness proof, or whether an existing detector suite includes these exact faults. No official measurements or lane gates were run. No installs or updates.
