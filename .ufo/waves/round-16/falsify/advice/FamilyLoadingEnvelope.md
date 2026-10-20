VERDICT: partial — all 8 literal oracles in `LoadingEnvelope.json` are right and reproduce (8/8 current, 0/8 frozen), but 2 of the 8 rows add no discriminating coverage (one is observationally identical to `canonical-alias`) and 1 `why` describes a fixture the harness cannot produce ("No Server header"), so that row's named invariant is untested.

Seat: FamilyLoadingEnvelope (falsify wave, round 16). State attacked: lane HEAD `b8e485c`.
Identities (measured state): `tools/kama-probe.sh` sha256 `6edd3c4c…fa50` (working tree
clean at measurement time); frozen probe
`93ee4302…cd64` = `frozen/manifest.json` = `git show 20e392e:tools/kama-probe.sh`;
`tests/probe-verdicts/LoadingEnvelope.json` `12bc261c…6f03`; `tests/probe-verdicts/check.py`
`fd49ff7c…6140`.
**Concurrent edit (not mine):** after my runs another seat left comment/doc-only edits in
the tree — `tools/kama-probe.sh` is now `36b6497…29d3` (header comment rewritten, net +2
lines, `classify()` untouched) and `check.py` is now `b853576…5762` (docstring/help "3"→"4").
Every `kama-probe.sh` line number below refers to the measured blob; on the current tree add
+2 (e.g. loading branch `504-505`→`506-507`, expect case `530`→`532`). I re-ran the 8-row
family against the current tree: 8/8 pass, exit 0, so none of the findings depend on it.
I edited no lane file, started no llama-server (`pgrep -x llama-server`
exit 1 before and after; `ss` found nothing on 8080/34113, exit 1) and did not run
`measure.py`. Scratch `/tmp/kama-r16-FamilyLoadingEnvelope/` was removed after this report.

## Axes

- **A1 oracle** — does each `expected` triple equal what the C1 rule and the landed
  `classify()` must produce?
- **A2 why** — does the fixture actually exercise the mechanism its `why` names?
- **A3 discrimination** — can any row fail for a reason no other row in the family detects?
- **A4 citations** — do cited source spans support the sentence they are attached to?

## A1 — all 8 oracles: CONFIRM

Commands (whole matrix, both probes, full output in /tmp then discarded):

- `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json`
  → **exit 0**, `tests=72 passes=72 failures=0` (37.99 s).
- `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json`
  → **exit 1**, `tests=72 passes=55 failures=17` (37.78 s).
- Frozen failure set == the rows whose `expected.verdict == "MODEL_LOADING"`: 17 = 17,
  set equality true (checked programmatically, not by eye).
- Family slice, current: 8/8 pass, each `verdict=MODEL_LOADING reason=llamacpp-loading
  probe_exit=2 drift=True`. Family slice, frozen: 0/8, all
  `FOREIGN_SERVICE/non-2xx-non-model-http/2`.

That is the L1 measurement reproduced independently. The triple itself is exact in the code:
`kama-probe.sh:504-505` set the two literals, and exit 2 is the drift path
(`eval_rows`, `:848-849` CLI-override branch sets `EV_DRIFT=1` for any non-`MODEL_OK`,
`:881` returns 2; `cmd_check` propagates it `:887-892`). `check.py:340-347` additionally
asserts `drift == (verdict != "MODEL_OK")`, so the C1 "drift" clause is graded even though
the schema has no `expected.drift` field. `expected.exit` 2 is therefore the only legal
value and the rows state it correctly.

Row-by-row:

| row | oracle | `why` | marginal discrimination |
|---|---|---|---|
| canonical-alias | ✓ | true; one imprecise causal clause (A2.3) | base positive |
| wildcard-expect | ✓ | mechanically true, overstates the risk (A2.2) | **none found** (A3) |
| dash-expect | ✓ | true | unique for the `-` literal (`m-dash`) |
| no-server-header | ✓ | **FALSE premise** (A2.1) | unique for a Server-value gate (`m-server`) |
| plain-json-content-type | ✓ | true; one unevidenced aside (A2.3) | unique (`m-ct`) |
| key-order-permuted | ✓ | true; wire order confirmed (A2.4) | unique (`m-order`) |
| pretty-printed-body | ✓ | true | unique (`m-compact`) |
| every-non-frontend-path | ✓ | true of the fixture, but unobservable (A3) | **none** — strict duplicate of canonical-alias |

## A2 — `why` accuracy

**A2.1 `no-server-header`: refuted.** The harness always emits a `Server` header.
`check.py:188-191` `version_string()` returns `self._server_header or STUB_SERVER_HEADER`
(`STUB_SERVER_HEADER = "kama-stub"`, `:52`), and `send_response()` unconditionally calls
`self.send_header("Server", self.version_string())` (`:193-197`). The route-declared header
is consumed at `:228-231`, and an empty value is falsy, so omission is **not expressible**
by the current schema. The probe's own evidence proves the fixture sends it: both current and
frozen records for this row read
`GET /v1/models -> 503 application/json; charset=utf-8 (Server: kama-stub) (body matches the llama.cpp loading envelope…)`.
So the row tests "a non-llama.cpp Server value", not "no Server header at all"; the claimed
invariant (detection without the header) is unverified by any row. The row is not useless:
it is the only row that fails a mutant gated on `F_SERVER = llama.cpp` (`m-server`, below).

**A2.2 `wildcard-expect` / `dash-expect`: mechanically true, risk overstated.** `expected`
is read only inside the 2xx-with-model-array block: guard at `kama-probe.sh:522`, `case` at
`:530`; the only other uses are the parameter binding (`:452`) and the evidence string
(`:542`). A 503 body with no `data[]`/`models[]` can never reach line 530, so no
`--expect` value can be "promoted" on this path. The statements "never promoted to
expected-wildcard" and "wins before any id logic runs" are true but describe an impossible
race. (This is also why the two rows are redundant — A3.)

**A2.3 Minor imprecision, keep.** `canonical-alias` says the alias expect is irrelevant
"because a loading server serves no id yet"; the operative reason is branch order — a
synthetic 503 that *did* carry a model array would still return `MODEL_LOADING` because the
loading branch precedes the 2xx block. `plain-json-content-type` says "proxy or older build
may strip it"; b11755 always sets `"application/json; charset=utf-8"`
(`server-http.cpp:315-323`), and no older-build evidence is cited. The row is still
rule-justified: the knowledge entry's table says "any `Content-Type`"
(`corpus/knowledge/llamacpp-loading-lifecycle.md:58`).

**A2.4 `canonical-alias` "Byte-exact" — CONFIRM, but with a pin gap.** [INFERENCE from
upstream source; the live receipt never captured the envelope.] I verified the wire
bytes from upstream source, not by assumption: `server-common.h:25` `using json =
common_json;`; `common_json` wraps `nlohmann::ordered_json` (upstream `common/json.cpp:14`);
`safe_json_to_str` is `data.dump_safe()` (`server-common.cpp:1695-1697`); `dump_safe` is
`dump(-1, ' ', false, replace)` (`common/json.cpp:343-345`), i.e. compact, insertion-ordered.
The initializer in `server-http.cpp:316-323` inserts `message`, `type`, `code` in that
order, so the wire body is exactly the row's `body_text`
`{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`.
Caveat for L1: `common/json.h` / `common/json.cpp` are **not** in
`.ufo/waves/round-16/sources/pins.json`, and the live receipt never saw the envelope
(`.ufo/waves/round-16/live/receipt.json`: `loading_observed: false`, `loading_503: null`,
`loading_envelope_exact: null`; its `health` capture is a ready 200). The byte-order claim is
therefore true but rests on an unpinned file; I fetched it at the pinned commit and recorded
`json.h` `a352f313…d22f`, `json.cpp` `d8c55644…98f2`. Pinning those two files (or wording the
row "envelope" rather than "byte-exact") closes the gap. This is also the file that makes
`NearMissTriple.readme-key-order-positive`'s "live server sends message,type,code" true —
that row's claim is sound for the same reason, not because of a live capture.

## A3 — redundancy / non-discrimination: 2 rows

I ran eight one-line mutants of the landed probe (copies under /tmp; each differs only by an
extra condition or an early `case "$expected"`), `check.py --only` for exactly these 8 rows.
Each run exited 1 (the rows named below failed):

| mutant | added behavior | rows it fails |
|---|---|---|
| `m-server` | loading also requires `F_SERVER = llama.cpp` | **no-server-header** only |
| `m-ct` | loading also requires `Content-Type: application/json; charset=utf-8` | **plain-json-content-type** only |
| `m-order` | re-serialize parsed JSON compactly, compare to wire literal (order-sensitive, whitespace-insensitive) | **key-order-permuted** only |
| `m-byte` | compare body bytes to the wire literal | key-order-permuted, **pretty-printed-body** |
| `m-compact` | require body to start `{"error":{"` plus the three key fragments (whitespace-sensitive, order-insensitive) | **pretty-printed-body** only |
| `m-star` | early `expect == "*"` → `MODEL_OK/expected-wildcard` | wildcard-expect, plain-json-content-type, pretty-printed-body |
| `m-dash` | early `expect == "-"` → `MODEL_OK/expected-wildcard` | **dash-expect** only |
| `m-wild` | both early | dash-expect, wildcard-expect, plain-json-content-type, pretty-printed-body |
| frozen probe | no loading branch at all | all 8 |

Findings:

1. **`every-non-frontend-path` is a strict duplicate of `canonical-alias`.** Same expect
   (`stories260K`), same two probed paths, and the current records are equal field-for-field
   on `verdict`, `reason`, `probe_exit`, `served_model`, `drift`, `evidence` and `requests`:
   `GET /v1/models -> 503 … (body matches …); GET /health -> 503|application/json; charset=utf-8`
   for both. The difference (explicit routes vs `default_route` only) is invisible because
   the loading branch requests only `/v1/models` (`classify` `:454`) and `/health`
   (`:506`); it never asks `/` or `/metrics` on this branch. The source claim is true
   (`server-http.cpp:307-328`); it is simply not probe-observable, so the row can only fail
   if `canonical-alias` fails.
2. **`wildcard-expect` has no unique coverage.** It fails under `m-star` and `m-wild`, but so
   do `plain-json-content-type` and `pretty-printed-body`, which carry the same body and the
   same `expect: "*"`. Since `expected` is unreachable before the loading branch (A2.2), any
   implementation keyed on `"*"` trips three rows at once; any implementation keyed on
   `expected` generally also trips `canonical-alias`. No mutant I constructed fails this row
   alone. `dash-expect` is different: it is the only row with `"-"`, so it does have unique
   coverage (`m-dash`).

The remaining five rows each have at least one mutant only they catch, so they are
discriminating. Note the family is deliberately positive-only (all 8 fixtures carry the
correct envelope); the near-miss discrimination lives in `NearMissTriple` / `Overbroad503`,
which is a scope split, not a defect here.

## A4 — citations

- `every-non-frontend-path` cites `server-http.cpp:312-325`. The block is `307-328`; the
  cited span omits `:308` `if (!is_ready.load())` and `:309-311` `if
  (frontend_paths.count(req.path))`, i.e. exactly the two conditions the row's "EVERY
  non-frontend path while !is_ready" sentence depends on. `312-325` does contain the 503
  status, the envelope initializer and `return false`. The knowledge entry already uses the
  correct range (`llamacpp-loading-lifecycle.md:3`: `middleware_server_state lines 307-328`).
  Low severity; cite `307-328` if the row survives.
- No other row cites upstream lines, and no row cites `kama-probe.sh` line numbers, so the
  frozen/current numbering question does not arise in this family. The frozen probe is 1092
  lines vs 1136 at the measured blob (1138 in the current tree); nothing in the family
  depends on probe line numbers.

## Recommendations (severity order)

1. **Medium — fix `no-server-header` or drop it.** Either rename to
   `non-llamacpp-server-value` and rewrite the `why` (it is the only `m-server` catcher), or
   add an omission sentinel to `check.py` (schema change owned by the checker seat; today
   `version_string()` at `:191` cannot return an absent header). Do not leave a row whose
   stated invariant no fixture can produce.
2. **Medium — remove `every-non-frontend-path`.** Strict duplicate; keep the source fact in
   the knowledge entry where it already is.
3. **Low — remove/merge `wildcard-expect`.** Its expect dimension is already exercised twice
   by `plain-json-content-type` and `pretty-printed-body`; keep `dash-expect` (unique `-`).
4. **Low — pin `common/json.h` + `common/json.cpp`** (digests above) under
   `.ufo/waves/round-16/sources/`, or drop "Byte-exact" from `canonical-alias`. The rules are
   parse-based, so "envelope" loses nothing.
5. **Low — cite `server-http.cpp:307-328`** if row 8 is kept.
6. **Info for L1** — if recommendations 2 and 3 are applied, the matrix becomes 70 rows /
   15 `MODEL_LOADING`; `measure.py` must be re-run by L1 (I did not run it), and any narrative
   that says "72 rows / 17 loading" must move with it.

## Limitations

- Mutants are my constructions. "No mutant fails only X" is evidence about this mutant set,
  not a proof of zero coverage; for `expect` it *is* structural (the value is unreachable
  before the loading branch), for `every-non-frontend-path` it is exact (identical observable
  exchange).
- I attacked only `LoadingEnvelope.json` rows. Cross-family rows were read only to check
  overlap; `EnvelopeShapes.*` (extra keys), `LoadingRace.*` (health surfaces) and
  `NearMissTriple.*` were not re-graded beyond the full-matrix run.
- `common/json.h`/`common/json.cpp` were fetched from `raw.githubusercontent.com` at the
  pinned commit, not from the lane's pinned copies (they are absent there).
- Harness-side detail (`__pycache__` dirs under `tests/probe-verdicts/` and `tools/` appeared
  at 11:00 local from another seat importing those modules, after my runs) is outside my
  item; L1 should ensure they are not committed.

## Installs / tooling

None. No package, tool or model was installed or updated. Scratch: one `curl` of two upstream
files and eight probe mutants, all under `/tmp/kama-r16-FamilyLoadingEnvelope/`, since removed.
