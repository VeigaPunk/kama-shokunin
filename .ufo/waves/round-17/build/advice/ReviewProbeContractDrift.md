VERDICT: confirm — both invariants C1 asks for have landed in check.py during this review (verified in the current snapshot); the residual drifts are the served-model blind spot in the live gate, an unpinned probe-document identity, and four key/vocabulary inconsistencies.

Reviewed snapshot (both Python gates were rewritten repeatedly while this seat read; every anchor below was re-verified against these exact bytes):

| file | sha256 (first 12) | mtime (-03) | size | churn |
|---|---|---|---|---|
| `tests/probe-verdicts/check.py` | `b460b7867b49` | 12:27:03 | 27573 | changed 5× during review |
| `tests/llamacpp-live/check-receipt.py` | `f6467f5af0ad` | 12:29:30 | 59570 | changed during review (v1+v2 validator landing) |
| `tools/kama-probe.sh` | `36b64978ee3a` | 11:03:02 | 49744 | unchanged |

An earlier check.py snapshot (510 lines) had none of the new invariants; an intermediate one
briefly carried an unreachable duplicate grading block after `return record` — both states are
gone. If either file moves again, re-anchor by the quoted symbol, not by these numbers.

Also present and untracked: `tests/probe-verdicts/__pycache__/check.cpython-314.pyc` (12:27:14).
It is not a `*.json`, so C1's byte-identical-matrix constraint is intact by the letter, but the
matrix directory should stay clean — exclude `__pycache__` from the commit.

# Row-key contract map (`check --json`; probe is stable)

| key | --port row (852) | registry row (875) | consumers row (790/807) | check.py reads | check-receipt.py reads |
|---|---|---|---|---|---|
| `id` | yes | yes | yes | no | no |
| `consumer_path` | `"-"` | yes | yes | no | no |
| `resolver` | **no** | yes | yes (807 only; cli row 790 omits) | no | no |
| `declared` | yes | yes | yes | no | **yes** (599) |
| `resolved_from_file` | **no** | yes | yes | no | no |
| `file_match` | yes | yes | yes | no | no |
| `resolver_kind` / `resolve_kind` | `resolver_kind` | `resolve_kind` | `resolve_kind` | no | no |
| `endpoint` | **no** | yes | yes | no | no |
| `port` | **no** | yes | yes | no | no (receipt-level `port`, 236) |
| `expected_model_id` | yes | yes | yes | no | **yes** (593) |
| `verdict` | yes | yes | yes | **yes** (460, 467) | **yes** (573) |
| `reason` | yes | yes | yes | **yes** (460, 468) | **yes** (573) |
| `served_model` | yes | yes | yes | **yes** (460-475) | **never read** |
| `drift` | yes | yes | **no** | **yes** (460, 472) | **yes** (580, 587) |
| `evidence` | yes | yes | yes | read 460, never compared | never read |
| `notes` | yes | yes | yes | no | no |

Document-level: `schema`, `subcommand`, `summary.*`, `verdict_vocabulary`, `exit_codes`,
`registry`. check.py reads **none**; check-receipt.py reads `schema` (563) and `summary.exit`
(566-568).

Direct answer:

- **Keys the gates read that `check` can omit: none.** `{verdict, reason, drift, served_model,
  evidence, expected_model_id, declared}` is emitted by both row emitters (852, 875).
- **Vice versa is where the drift lives:** nine emitted row keys plus five document keys are read
  by no gate, and `evidence` is read into check.py's record (460) but never compared.
- Subcommand asymmetry: `drift` exists only on `check`/`snapshot` rows; `consumers` rows (807)
  lack it, and `check --port` rows (852) lack `port`/`endpoint`/`resolver`/`resolved_from_file`
  that registry rows carry. Both gates reject those shapes fail-closed (below), but nothing
  documents the difference.

# Closed by the in-flight C1 repair (verified, not inferred)

- **`served_model` is now graded.** `check.py:460-464` copies the row key, computes
  `record["served_model_expected"] = expected_served_model(test, record["verdict"])` and
  `record["served_model_ok"] = (...)`; conjunct at 473. The derivation (`served_ids_of`, 286-320)
  is a faithful mirror of probe `served_ids()` (`kama-probe.sh:350-368`): same five-group
  precedence, same str/non-empty filter, same `dict.fromkeys` dedupe, same dict-only top level.
  It must stay **raw** — `served-id-carries-gguf-suffix` pins `served_model: "kama-ready.gguf"`;
  normalising (as `served_persist`, `kama-probe.sh:1007`, does for snapshot) would break it.
- **Route-match is now graded.** `check.py:441`, `446` set `record["route_ok"] =
  fetched_models_route(test, record["requests"])`; `fetched_models_route` (357-369) requires
  method `GET` and `path.split("?",1)[0] == "/v1/models"` (matching the handler's query-stripped
  fallback at 217-221), and returns `None` for non-stub rows. The conjunct `route_ok is not False`
  (474) correctly treats `None` (the one `port_mode: closed` row) as not-applicable. All 71
  stub-mode rows are in scope; the stub logs every request at 216.
- **Malformed probe output no longer tracebacks.** `probe_output_row` (372-397) rejects non-JSON,
  non-dict top level, non-list/empty `rows`, non-dict `rows[0]`, non-str verdict/reason, non-bool
  drift; `grade` records `malformed probe output: ...` (453-455) and returns a failed row. The old
  `doc["rows"][0]` + `row.get(...)` path that raised uncaught `AttributeError` is gone from the
  live block.

One landing caveat remains; the other was closed while this report was being written:

## L1 (Medium) — `expected_served_model` keys on the *observed* verdict

`check.py:347` — `if verdict not in ("MODEL_OK", "MODEL_MISMATCH"): return "-"`; called at 461-462
with `record["verdict"]`.

This is sound only while the exact-verdict conjunct (467) runs in the same expression: a probe
reporting `FOREIGN_SERVICE` + `served_model: "-"` passes `served_model_ok` and is caught by the
verdict compare. Keying on `test["expected"]["verdict"]` instead is strictly stronger — a wrong
verdict would then also fail the served check — and removes the self-reference that a future
refactor (reordering, or relaxing the verdict compare) could turn into a tautology. All 11 rows
with a non-`-` value are `MODEL_OK`/`MODEL_MISMATCH`, so the stronger key changes no current
result.

## L2 (closed during review) — summary attribution

`check.py:572-576` now appends `served_model=<observed> (expected <want>)` when
`served_model_ok is False`, and `route=missing-GET-/v1/models` when `route_ok is False`, so a row
failing only on the new invariants is distinguishable from a clean row. No action; the earlier
snapshot printed neither.

# Open findings

## O1 (Medium) — check-receipt.py still never grades `served_model`; the asymmetry now runs the other way

`tests/llamacpp-live/check-receipt.py:996` is the file's only `served_model` occurrence and it is
the selftest literal. Probe-row reads are verdict/reason (573), drift (580, 587),
expected_model_id (593-597), declared (599-603).

The matrix gate is now stricter than the live gate: a receipt whose stored probe row claims the
wrong served model (or `"-"` where ids exist) validates. check-receipt already has both sides in
hand — the row and the re-parsed `captures.models.data_ids` used by `models_alias_id` — so the
cross-check is a two-line addition, not new evidence. If C1 only claims check.py, record this as
accepted residual rather than leaving it implicit.

## O2 (Medium) — neither gate pins the probe document's identity

`check.py:372-397` validates row shape only; `schema`/`subcommand` are never read.
`check-receipt.py:563-568` validates `schema` and `summary.exit` but not `subcommand`.

So a probe mutant that renames `"schema": "kama-probe/v1"` → `"kama-probe/v0"`, stales
`subcommand`, or makes `summary.exit` disagree with its process exit still passes all 72 matrix
tests. This is the C1 scope boundary: if the fault-control wrappers corrupt any of these fields,
check.py must grade them or the suite must exempt them explicitly. Decide and write it down, or
(b) and (c) will disagree on the count.

## O3 (Low) — one subcommand, two spellings: `resolver_kind` vs `resolve_kind`

`kama-probe.sh:852` (--port row) emits `"resolver_kind":"cli-override"`;
`kama-probe.sh:875` (registry row) emits `"resolve_kind":%s`; consumers JSON 790/807 use
`resolve_kind`, while the consumers table header (781) prints `resolver_kind`.
`check-receipt.py:992` pins only the --port spelling in its fixture; no gate reads either. The
same split is in prose (`SKILL.md:182` `resolver_kind=raw`, `SKILL.md:206` `resolve_kind`).
[INFERENCE] Pick one before the fault-control suite starts asserting row key sets, otherwise it
freezes the inconsistency.

## O4 (Low) — `expected_model_id` substitutes `-` for an absent/empty `--expect`

`kama-probe.sh:851` — `"$(jstr "${OPT_EXPECT:--}")"`; classify treats `''|'*'|'-'` as the same
wildcard arm (533-534). Usage documents "any" (108). check-receipt compares the field literally to
the recorded expect (593-597), so a receipt recording `expect: ""` would be rejected although the
probe behaved as documented. No live path triggers it: the matrix always passes `--expect`
(`check.py:275-277`) and the live tool always does (frozen `tools_kama-llamacpp-live.py:623`).

## O5 (Low) — header/usage vocabulary drifts from the code it documents

- `kama-probe.sh:25` `# Common flags: --json  --registry PATH  --timeout S  --connect-timeout S  --help`
  omits `--ufo-src`, implemented at 142-143 and in usage at 112.
- `kama-probe.sh:50` documents `schema kama-probe/v2` for snapshot only; the `kama-probe/v1`
  documents emitted by check/consumers/listeners (891, 816, 745) are undocumented, while
  `check-receipt.py:60` pins `kama-probe/v1`.
- Same envelope, two citations: `kama-probe.sh:34` `server-http.cpp:307-328` vs line 422
  `307-325`.
- The 15-string reason vocabulary (`kama-probe.sh:466-566`) is not documented in the header, while
  check-receipt pins four of them (575, 591).

Verdict vocabulary is clean: header 28-30 = usage 119 = `VOCAB` (74), and all nine matrix files
use only those seven strings. The reason sets agree too: check-receipt's `("matched",
"expected-wildcard")` (575) and `("served-id-mismatch", "unresolvable-id")` (591) are exactly the
classify arms at `kama-probe.sh:534`, `539`, `540`, `541`.

## O6 (Low) — the matrix validator does not pin expected values to the probe vocabulary

`check.py:140-149` accepts any string verdict/reason and only enforces `MODEL_OK ⇒ exit 0`. No
false pass today (467 is exact equality), but a matrix edit can encode a verdict the probe can
never emit, and a count-pair detector cannot tell that from a regression. Guardrail only, given
the byte-identical-matrix constraint.

## O7 (design note, affects C1's counting) — the timeout mutant has no cheap fault wrapper

`check.py:52` `PROBE_TIMEOUT = 30`; `build_parser` (595-608) exposes only `--probe`, `--only`,
`--json`, `--selftest` — no timeout override. A wrapper probe that hangs to exercise
"timeout-pass" costs 30 s per affected row. Either add a `--probe-timeout` flag, or drive that
fault by importing check.py and patching `run_probe` (275). Without one of these, the round-16
`timeout-pass` mutant is the one fault the wrapper-only suite cannot reach affordably.

## O8 (info) — the compliant seam for temp matrices exists and is already exercised

`check.py:152` `def load_matrix(directory=CHECK_DIR):`; the selftest builds duplicate-name files in
a `TemporaryDirectory` and calls `load_matrix(tmp_path)` (512-540) — explicitly "without touching
the matrix dir". The fault-control suite should use the same seam (importing check.py, which is
also what creates the stray `__pycache__` noted above), never a new `*.json` under
`tests/probe-verdicts/`, which keeps the nine-file set digest and the 72/17 breadth intact.

# Confirmed consistent (checked, no action)

- `declared` in --port mode is `http://127.0.0.1:$OPT_PORT/v1` (`kama-probe.sh:848`), exactly what
  check-receipt.py:599-603 demands; the receipt fixture mirrors the --port row key set 1:1
  (check-receipt.py:987-1000 vs `kama-probe.sh:852`), including omitting `port`.
- `drift` is a real JSON boolean in both check modes (852 prints `${EV_DRIFTROW[0]}`, 875 prints
  `$drift`), so check-receipt's strict `is not False` / `is not True` (580, 587) holds; check.py's
  `==` (472) is merely laxer.
- `drift == (verdict != MODEL_OK)` holds in both emitters (847-851, 869-871), and check.py's
  expected-exit mapping (0 iff `MODEL_OK`) matches `eval_rows` returning 2 on any drift.
- Served-model feasibility, derived independently in memory from the nine matrix files: 61/72 rows
  must report exactly `-`; 11 carry ids (8 `MODEL_OK`, 3 `MODEL_MISMATCH`). The 11:
  `ReadyControls.expect-exact-id` / `-wildcard-star` / `-wildcard-dash` / `-different-id` (`kama-ready`),
  `-gguf-path-basename` (`stories260K`), `served-id-carries-gguf-suffix` (`kama-ready.gguf`),
  `ollama-name-not-served-id` (`kama-ready` — proving `data[].id` beats `models[].name`),
  `second-data-id-match` (`kama-ready,tiny-vocab`),
  `LoadingRace.InverseHealthLoadingModelsOk` / `InverseWildcardExpect` /
  `InverseHealthLoadingIdMismatch` (`stories260K`). 19 matrix routes use `body_text` (parsed
  identically on both sides); 71/72 tests are `port_mode: stub`, 1 is `closed`.
- `models_route` (322-330) resolves the exact `/v1/models` key then `default_route`, matching the
  handler except for query-suffixed keys (217-221); no matrix test defines `/v1/models?...`, so
  the two cannot diverge today.

# Residual risk / verification gaps

- Static review only: no lane gate, mutant runner, control suite, or live tool was executed; no
  port bound; nothing installed. The `AttributeError` fix and the new invariants are verified by
  reading the bytes, not by a run.
- Both Python gates were rewritten during the review; findings are anchored to the snapshot table
  above. Five different check.py states were observed in minutes, so a claim that survives to
  the final commit must be re-anchored by content, not by these line numbers.
- `served_ids_of` and `served_ids` agree on UTF-8-BOM bodies by both failing to parse (→ `[]`), so
  `EnvelopeShapes.BomPrefixedJson` expects `-` on both sides. The probe's no-python3 grep fallback
  (374-380) has different precedence; python3 is present here.
- `jstr` (`kama-probe.sh:178-186`) escapes only `\ " TAB LF CR`; without python3, `emit_json`
  emits unvalidated JSON, so another control byte in a `Server:` header yields invalid JSON —
  check.py then records a malformed-output row (453-455), not a false pass.
