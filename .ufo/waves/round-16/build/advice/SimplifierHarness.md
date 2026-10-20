# SimplifierHarness — round 16 build advice (YAGNI review)

Seat `KamaR16.SimplifierHarness`, leaf, read-only. Lane root
`/home/vgpnk/Projects/shokunin/kama-shokunin`. The only file written is this report.

## Axes

1. **Calibration (C1)** — the stub matrix must stay red on the frozen probe, green on the
   repaired probe, and keep positive controls that defeat reject-all / loading-all probes.
2. **Operability (C2)** — one live llama-server run must produce a receipt whose teardown is
   proved and whose claims are independently re-derivable.
3. **Failure surface** — every element that can fail without changing a measurement is a cost.
4. **Evidence integrity** — one authority per fact; a second copy of a schema is a future lie.

## Method and limits

- Parsed all 9 matrix files (72 tests, 119,825 bytes) with `json`; read `check.py`,
  `measure.py`, `kama-llamacpp-live.py`, `check-receipt.py`, and the frozen probe.
- File state read at 10:36 -03; `kama-llamacpp-live.py`, `check.py` and `measure.py` were
  still being revised during this read, so every `path:line` is as of that snapshot. A ninth
  family (`NearMissTriple.json`, 8 tests) landed at 10:36:36 and is included.
- No lane gate, harness, test, or server was run; L1 owns every measurement.
- No `lsp` device is bound in this seat, so "no caller" claims are literal proofs: full-set
  JSON parse for matrix fields, whole-tree `grep` for identifiers (recorded here because the
  semantic device was unavailable). No installs.
- Read-only commands only: `git show 20e392e:tools/kama-probe.sh`, `git cat-file -t`,
  `llama-server --version`, `llama-server --help`, `sha256sum`.

## Headline

The single deletion that pays for itself: **`check-receipt.py` carries a second copy of the
receipt schema, and it has already drifted from the producer on four keys.** As landed it
rejects every receipt `kama-llamacpp-live.py` can emit — while its `--selftest` still reports
"valid receipt accepted". Delete the copy and the selftest; bind the gate to the producer's
exact keys. That removes roughly 40% of the file and turns the gate from red to meaningful.

## P1 — C2 gate is red on any real receipt (by inspection, not executed)

Producer shape: `tools/kama-llamacpp-live.py:561-591` builds the receipt; consumer:
`tests/llamacpp-live/check-receipt.py:341-579` (`def validate(...)`).

| # | Producer emits | Gate reads | Consequence on a real receipt |
|---|---|---|---|
| R1 | `tools/kama-llamacpp-live.py:563` `'started_utc': _utc_now(),` and `:723` `receipt['ended_utc'] =` | `:356` `started = _parse_ts(receipt.get("started"))` | 2 problems: `started None is not a parseable ISO timestamp` (same for `ended`) |
| R2 | `tools/kama-llamacpp-live.py:405` `rec['result'] = json.loads(cp.stdout)` | `:159` `j = p.get("json")` | `probe_model_ok: no stored probe run with verdict MODEL_OK`; same for `probe_mismatch` |
| R3 | `tools/kama-llamacpp-live.py:363` `props['fields'] = props_fields` (no body kept) | `:491` `v.get("model_alias"), str):` on the capture dict | `props_alias: no model_alias recorded from /props` |
| R4 | `tools/kama-llamacpp-live.py:455` `out['port_refuses'] = True` | `:555` `for k in ("port_closed", "port_refused", "port_dead"):` | `teardown_port_closed: no evidence the port refuses connections after teardown` |

`grep` over the gate finds **zero** occurrences of `started_utc`, `ended_utc`, `result`,
`fields`, or `port_refuses`. Six problem lines, exit 1, on every good receipt. The digests
(top-level `server`/`model`), the `captures.*.path` lookup, and `teardown.returncode` do
match, which is why the drift was not obvious at a glance.

Root cause, stated by the gate's own advice:
`.ufo/waves/round-16/build/advice/LiveReceiptGate.md:7` — "the harness file did not exist at
write time". The selftest literal (`check-receipt.py:632` `"started": "2026-10-20T13:00:00Z",`)
encoded the gate's spelling, not the producer's, so the selftest proved only self-consistency.

**Recommendation (delete + rebind).** Keep the gate's independence (it must still re-derive
from stored probe output and never trust `passed`), drop its *shape tolerance*:

- Read the seven exact locations the producer writes: `captures.health.status`,
  `captures.models.body` (then `json.loads`), `captures.props.fields.model_alias`,
  `probes[*].{expect,exit,result.rows[0]}`, `teardown.{returncode,port_refuses}`,
  `server.sha256`/`model.sha256`, `started_utc`/`ended_utc`.
- Delete `_walk`, `_find_dicts`, `_key(d, *names)` (`:65`), the alias loops in `_probe_exit`
  (`:140-148`), `_digest` (`:316-339`) and `_alias` (`:298-314`). That is ~180 lines of
  multi-spelling search replaced by ~40 lines of exact reads.
- If a name must change, change it in one place; a gate that accepts every spelling cannot
  enforce a schema and cannot tell a wrong receipt from a right one.

Smaller but real: `--expect-server-sha256` is ambiguous. The context calls `753bfa73…e226`
the "asset" hash, and it is **not** the executable's hash [INFERENCE: it is the release
archive]; the installed executable is `sha256sum
~/.local/opt/llama-b11755/llama-server` = `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`
(`llama-server --version` → `version: 0.7.0-dev (build 11755, commit 704366d76)`). Passing the
asset hash to the gate rejects a valid receipt. Name the field `binary_sha256` (or drop the
flag and rely on the model pin, which is unambiguous: `stories260K.gguf` =
`270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`).

## P2 — deletions and merges that improve an axis and harm none

### Gate

- **D1 Delete `--selftest` and `_selftest_receipt`** (`check-receipt.py:586-766`, ~180 lines).
  It is a second receipt literal plus 10 mutations; it validates the validator, not C2, and it
  already disagrees with the producer. Replacement negative control costs one line for L1: run
  the gate on a copy of the real receipt with `port` set to 8080 and require exit 1. That uses
  the real schema and cannot drift.
- **D2 Collapse the alias layer** (see P1). Net ~140 lines removed, schema enforcement gained.

### Stub matrix (72 tests / 119,825 bytes → ~58 tests; arithmetic [INFERENCE])

- **D3 Remove the 3 exact duplicate tests.** Same `routes`+`port_mode`+`expect`+`expected`,
  byte-identical payloads (verified by hashing all 72):
  - `tests/probe-verdicts/EnvelopeShapes.json:106` `"name": "EnvelopeShapes.CodeAsString",`
    ≡ `tests/probe-verdicts/Overbroad503.json:83` `"name": "Overbroad503.code-string",`
  - `tests/probe-verdicts/ForeignControls.json:104` `busy-unavailable-error` ≡
    `Overbroad503.json:35` `no-slot-available`
  - `ForeignControls.json:120` `loading-message-wrong-type` ≡ `Overbroad503.json:67`
    `server-error-type`

  Keep the Overbroad503 copies (that family is the overbroad-rejection control); delete the
  other copies. One copy of each near-miss still pins the exact-triple rule.
- **D4 Merge the `/health` variants in LoadingRace** (9 → 5). `LoadingRace.json:24,45,61,82`
  differ from `:3` only in the `/health` route; the `/v1/models` payload hash is identical
  (`a2ca48c948…`). The probe reads `/health` only to decorate evidence:
  frozen `kama-probe-before.sh:500` `local h; h=$(probe_short "$port" "/health")` feeds
  `C_EVIDENCE`, never `C_VERDICT`. One test (`HealthAlreadyOk`, the observed race) pins
  "`/health` is not consulted"; the four others cannot change an outcome. Keep the three
  inverse tests (`:99,120,141`): they differ in `expect` and pin MODEL_OK/wildcard/mismatch.
- **D5 Delete `EnvelopeShapes.Padding64KiB`** (`EnvelopeShapes.json:213` `"pad": "AAAA…`,
  65,536 chars). It is 60.1% of all matrix bytes (file 72,036 of 119,825) for one claim
  ("size and extras do not defeat detection") already covered by `ExtraFieldsAllowed`
  (`:134`). The matcher parses the whole file
  (`tools/kama-probe.sh:433` `doc = json.load(open(sys.argv[1]))`), so length is not a
  discriminating dimension for a JSON implementation.
- **D6 Merge LoadingEnvelope variants** (8 → 4). `no-server-header`, `plain-json-content-type`,
  `pretty-printed-body`, and `key-order-permuted` cannot add a verdict: the loading branch
  reads only the 503 status and the parsed body (`tools/kama-probe.sh:503`
  `if [ "$F_CODE" = "503" ] && …`; `:433` JSON parse). `Server` is evidence-only
  (`frozen:421-422`, `:486`), Content-Type does not enter the branch, `json.load` ignores
  whitespace, and `NearMissTriple.readme-key-order-positive` already pins key order as a
  positive MODEL_LOADING case. Keep `canonical-alias`, `wildcard-expect` and `dash-expect`
  (the two wildcard literals are cheap), and `every-non-frontend-path` (the only catch-all
  test).
- **D7 Drop `NonLoadingStatuses.err502-envelope` and `err504-envelope`.** All three 5xx tests
  hit the same `else` branch, and the expectation is only "status must be exactly 503"; `500`
  plus `429` (4xx) already covers both ranges, and `404` covers the JSON non-model path.

### Stub-matrix schema

- **D8 Delete `family` from every test.** It duplicated the file stem 72/72
  (`"family": "LoadingRace",` at `LoadingRace.json:4`; the name at `:3` is
  `LoadingRace.HealthAlreadyOk`). `check.py:286` (`"family": test["family"],`) is the only
  copier; the record already carries `source` (the filename). Derive the family from the
  `source` stem, **not** from the name: `NearMissTriple.code-float-503.0` makes
  `name.rsplit(".", 1)[0]` return `NearMissTriple.code-float-503`, so `measure.py`'s current
  name-prefix fallback (`:196-204`) would split that test into a phantom family if the field
  were deleted naively. One line in `check.py` (`family = os.path.splitext(source)[0]`) fixes it.
- **D9 Delete `expected.exit`.** It is a pure function of the verdict: 72/72 rows agree
  with `0 if MODEL_OK else 2`. The probe contract is frozen `kama-probe-before.sh:31`
  ("Exit codes: 0 … | 2 …") implemented at `:805` `else EV_DRIFT=1;` and `:837`
  `[ "$EV_DRIFT" -gt 0 ] && return 2 || return 0`. `check.py` can derive it at load — `:143-146` already forces it to
  equal `0 if MODEL_OK else 2`, and `:343` compares the observed exit — so no detection is
  lost. 72 fewer expected values that can be wrong.
- Keep `default_route`: three LoadingEnvelope tests use it (`grep` shows 3 non-null), and it
  is the only way to express "every non-frontend path answers 503" without listing paths the
  probe may add later.

### MeasureRunner (`measure.py`)

- **D10 Delete the extra `--probe NAME=PATH` mode** (`:244-258` parser, `:54-55`
  `NAME_RE`/`RESERVED_NAMES`, `:267` the argument, `:280-283` duplicate check). No consumer:
  the exit rule (below) counts only `before`/`after`, and the C1 claim needs exactly those two.
  This also removes the name-escape/reserved-name validation surface.
- **D11 Collapse the tolerant readers to `check.py`'s emitted shape.** `check.py:279-343`
  emits flat `verdict`/`reason`/`probe_exit`/`passed: bool` and `passes`/`failures` totals.
  Dead alternatives in `measure.py`: `_verdict` nested/`observed_verdict` branches
  (`:208-220`), `count_field("passed")`/`("failed")` aliases (`:182-190`), the int branch of
  `record_passed` (`:221-230`). ~15 lines, one convention.
- Keep `stdout_sha256` and `stderr_tail` (receipt evidence), keep the frozen check: the
  landed code correctly uses `git cat-file blob <commit>:<path>` (`:116-127`), fixing the
  design's bare-commit form — `git cat-file blob 20e392ea…` fails with
  `fatal: git cat-file 20e392ea…: bad file`. The `DEFAULT_COMMIT`/`DEFAULT_SOURCE_PATH`
  fallbacks (`:49-50`) are only reachable if the manifest loses fields it always has
  (`frozen/manifest.json:4,5`); optional delete.
- Measurement tightening (not a deletion): require the *before-failure set* to be exactly the
  MODEL_LOADING-expecting tests, not just "≥1 failure". Today a red for an unrelated reason
  plus a green after still passes `all_changed_loading` when no verdict changed. Two lines.

### Live harness (`kama-llamacpp-live.py`)

- **D12 Delete `--ctx`/`--threads`** (`:496-497`) and the duplicate receipt fields
  `'ctx': args.ctx` / `'threads': args.threads` (`:576-577`). They are constants 256/1 and
  are already recorded in `argv` (`:593-602`). One source of truth for the launch.
- **D13 Trim the `/props` capture to `model_alias`** (`:355-357`). `total_slots`,
  `is_sleeping`, `build_info`, and `default_generation_settings.n_ctx` have no consumer:
  `props_alias` reads only `model_alias` (`:669`), `build_info` restates the sha-pinned
  server identity, and `n_ctx` restates `-c`.
- **D14 Delete `port_pick_note`** (`:589-590`); it is static prose repeated in every receipt.
  The bind/rebind race belongs in a comment, not in data.
- Do **not** delete `HARD_REFUSED_PORTS` (`:57`) even though `refused_ports()` (`:141`) already
  harvests 8080/34113 from the registry: the item text names both, and the registry could
  change. Keep the broad regexes; they implement "any port number appearing in the TSV".
- Credit where due: transitions already fold repeats (`readiness_loop` via `_sig`/`repeats`),
  so the per-transition body copy (`:230`) is bounded and kept — no deletion needed.

### `check.py`

- **D15 Delete `--selftest` and `SELFTEST_MALFORMED`** (`:359-392`, wiring `:490-493`).
  It tests the schema validator, not the probe; the matrix load already fails closed on every
  one of those malformations (`:104-148`). L1 never reads it.
- Delete the `family` record echo with D8 (`:286`) and `expected.exit` with D9 (`:141-146`, `:343`).
- Optional: `--only` (`:438-440`) has no consumer in the measurement flow; keep only as a
  debugging aid, it costs ~8 lines.

## P3 — optional trims (low value, listed for completeness)

- `metrics_not_enabled` check (`kama-llamacpp-live.py:662`) is tautological for the pinned
  binary: `llama-server --help` says `--metrics … (default: disabled)` and the harness never
  passes it. The `/metrics` capture already records 501. Keep if the 9-check receipt is the
  documented surface; drop the check id if not.
- `health_ready` is the readiness loop's exit condition, so it cannot fail independently; keep
  it as the documented claim.
- 39 route objects carry a `Server` header that only appears in evidence strings
  (`frozen:421-422`, `:486`). Harmless; if removed, D6's `no-server-header` variant goes too.
- `documented_by` on each check is unused by the gate but is cheap evidence metadata; keep.

## Kept on purpose (deletion candidates I rejected)

- `port_mode: closed` and `{"raw":"close"}` are different wire facts (DEAD vs NOT_HTTP);
  both are exercised (`LoadingRace`, `AuthAndDead`).
- The three inverse `LoadingRace` tests differ in `expect` (alias / `*` / wrong id) and pin
  three distinct outcomes.
- `Overbroad503`'s remaining near-misses (lowercase, wrong type, string code, no wrapper,
  plain text, nginx HTML) are distinct bug classes for a loading-from-message or
  loading-from-status implementation.
- `why` is one line per test and is the failure-triage text; keep and print it on failure.
- `body_json` vs `body_text` vs `raw` are three real encodings; merging pushes serialization
  into 58 files.
- `NearMissTriple`'s 8 tests (float/bool/string code, message period/space, router-stream
  message, empty 503, key-order positive, HTML-labelled envelope) are distinct near-misses
  with no exact duplicates; keep them.

## Preserved contract

- C1: 58 tests still include red-before/green-after MODEL_LOADING expectations across
  `LoadingEnvelope`, `EnvelopeShapes.ExtraFieldsAllowed`, and `LoadingRace.HealthAlreadyOk`,
  plus the positive controls (`ReadyControls` MODEL_OK, `AuthAndDead`, `NonLoadingStatuses`,
  `Overbroad503`, `ForeignControls`). Exit is still asserted (derived), reasons still exact.
- C2: all 9 check ids, the port guard, the model digest (exit 3 pre-launch), SIGTERM→SIGKILL
  teardown with `returncode` and `port_refuses`, and the 30 s probe timeout stay.
- Provenance: frozen snapshot sha256 `93ee4302…cd64` == `git show 20e392e:tools/kama-probe.sh`
  (verified); manifest fields `source_commit`/`source_blob` are consistent.

## Tradeoffs and limitations

- The matrix merges trade hypothetical-implementation guards for size/time; each deleted test
  is provably non-discriminating under the C1 rule and the landed `json.load` matcher, not
  merely "unused today".
- Gate rebinding makes the validator stricter: a receipt that stores evidence under a new
  spelling will be rejected until the producer changes in the same commit. That is the
  intended contract, and it is what was missing.
- Findings are by inspection; the read-only seat executed no validator or harness. The four
  P1 key gaps are exhaustive `grep` misses, not guesses.
- Matrix `why` strings cite `kama-probe.sh:NNN`; those lines already shifted by +6 when the
  loading block landed, so the citations are stale. Prefer `classify()` branch names.
