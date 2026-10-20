VERDICT: confirm — every one of the 9 EnvelopeShapes oracles (verdict, reason, exit) is correct against the landed `classify()` and the C1 rule; two redundancy/precision findings, no wrong oracle.

Scope: `tests/probe-verdicts/EnvelopeShapes.json` @ lane commit b8e485c, judged against
`tools/kama-probe.sh:428-449` (`body_is_llamacpp_loading`), `:451-566` (`classify`), and the
C1 rule as stated in the round-16 assignment. Lane tree clean for both files
(`git status --porcelain` → empty).

## What I ran

1. `python3 --version` → `Python 3.14.8` (exit 0).
2. Current-probe run of exactly the 9 family rows:
   `python3 tests/probe-verdicts/check.py --json --only <each of 9 names>` →
   **exit 0**, `tests=9 passes=9 failures=0`, wall 4.91 s.
   Per-row: 7× `FOREIGN_SERVICE/non-2xx-non-model-http/2`, 2× `MODEL_LOADING/llamacpp-loading/2`
   (`ExtraFieldsAllowed`, `Padding64KiB`) — exactly the rows' `expected` triples.
   Receipts kept at `/tmp/kama-r16-FamilyEnvelopeShapes/envelope.json` (+ `.err` stdout summary).
3. Frozen-probe separability control, same 9 rows, `--probe .ufo/waves/round-16/frozen/kama-probe-before.sh`:
   **exit 1** (expected: harness returns nonzero on failure), `tests=9 passes=7 failures=2`;
   the two failures are exactly `ExtraFieldsAllowed` and `Padding64KiB` (frozen emits
   `FOREIGN_SERVICE/non-2xx-non-model-http/2` for both). Frozen artifact identity checked first:
   `sha256sum` → `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`, equal to
   `.ufo/waves/round-16/frozen/manifest.json:sha256`.
4. Independent predicate replication + mutation table (python3, all 9 stub bodies, exact
   `json.loads` semantics as `body_is_llamacpp_loading`): landed predicate reproduces all 9
   oracles (0 mismatches). Mutants and the rows that catch them:

   | mutant | caught by |
   |---|---|
   | byte-substring (space/case-insensitive search for the three literal tokens, no parse) | `InvalidJsonBody`, `TopLevelArray`, `CodeAsString`, `NestedEnvelope`, `BomPrefixedJson` |
   | recursive `$..error` search | `TopLevelArray`, `NestedEnvelope` |
   | accept `code` string `"503"` | `CodeAsString` |
   | require only message+type (drop code) | `MissingCode` (also `CodeAsString`) |
   | accept `error` as a string containing the message | `ErrorAsString` |
   | decode with `utf-8-sig` (tolerate BOM) | `BomPrefixedJson` |
   | read only first 4096 bytes | `Padding64KiB` |
   | unwrap a single-element top-level list | `TopLevelArray` |
   | drop `isinstance(doc, dict)` (no-topdict-check) | **none** — array has no `.get`, so behaviour is identical |
   | message prefix/case-insensitive (`'loading model' in msg.lower()`) | **none in this family** (covered cross-family by `Overbroad503.lowercase-loading`, `NearMissTriple.message-trailing-period`, `NearMissTriple.message-surrounding-space`) |

5. `pgrep -x llama-server` → exit 1 (no processes); I started no server and bound no port.
   No installs or upgrades.

## Row-by-row finding

All bodies are 503 + `Content-Type: application/json`, `port_mode: stub`, `default_route: null`,
`expect: "*"`, so every row lands on `classify`'s 503 path. After the gate declines, `is2=0`,
HTML sniff fails (body starts `{`/`\ufeff{`), `body_has_model_array` fails → `FOREIGN_SERVICE`
/ `non-2xx-non-model-http` / exit 2 (`tools/kama-probe.sh:556-562`). Positives return early at
`:503-508` with `MODEL_LOADING` and requests `[/v1/models, /health]` (no `/metrics` trap), as the
run receipts show.

- `InvalidJsonBody` — truncated JSON (73 B) carrying all three literal tokens. Landed: parse
  fails → reject. Oracle right. `why` accurate ("all triple tokens" verified byte-for-byte).
- `TopLevelArray` — envelope wrapped in a 1-element array. Oracle right. **Precision note**
  (Low): the `why` says it "fails the JSON-object requirement", but that requirement is not
  load-bearing for this body — removing `isinstance(doc, dict)` changes nothing because a list
  has no `.get` (mutant table row 9). The row's real marginal value is pinning "must not unwrap
  a list" (mutant unique to this row).
- `ErrorAsString` — `{"error":"Loading model"}`. Oracle right; `why` accurate. Not a duplicate
  of `Overbroad503.error-string`, whose body is `{"error":"maintenance"}` (different body, same
  triple).
- `MissingCode` — message+type, no code. Oracle right; `why` accurate ("all three members are
  required", `tools/kama-probe.sh:428-449`).
- `CodeAsString` — `"503"` string. Oracle right. **Redundancy** (Low): this row is an exact
  byte-for-byte duplicate of `Overbroad503.code-string` — same status, same headers
  (`Content-Type: application/json`), same canonical body
  `{"error":{"message":"Loading model","type":"unavailable_error","code":"503"}}`, same
  expected triple. One of the two could be dropped without losing coverage; the 72-row count
  currently double-counts this case.
- `ExtraFieldsAllowed` — exact triple plus `meta`/`n_ctx_train` siblings. Oracle
  `MODEL_LOADING/llamacpp-loading/2` right; evidence string from the run: "body matches the
  llama.cpp loading envelope: not ready; runtime identity and served model unverified".
  `why` accurate.
- `NestedEnvelope` — triple under `outer.error`. Oracle right. Note: it detects the same
  mutant class (recursive search) as `TopLevelArray`; neither is strictly redundant because
  each also pins a distinct non-recursive mutant, but the pair is the weakest marginal value
  in the family (Medium-low).
- `Padding64KiB` — `pad` measured at exactly 65536 chars, body on the wire 65620 B (curl has
  no `--max-filesize`; `fetch()` uses only `-o/-D/-w`, `tools/kama-probe.sh:286-301`).
  Oracle `MODEL_LOADING` right, and this is the **only** row that catches a body-size cap
  (unique in the mutant table). `why` accurate.
- `BomPrefixedJson` — body starts `ef bb bf` + exact envelope. `utf-8` → `JSONDecodeError:
  Unexpected UTF-8 BOM`; `latin-1` → column 1 error; `utf-8-sig` parses. Landed strict parser
  rejects → oracle `FOREIGN_SERVICE` right. `why` accurate as written ("strict JSON parsing
  rejects a leading BOM").
  **Judgment call** (Low, [INFERENCE]): this oracle pins a parser choice, not a llama.cpp
  behaviour. RFC 8259 §8.1 permits parsers to ignore a BOM, so `MODEL_LOADING` would also be
  defensible under the C1 rule text; the row would flip if the gate ever opened with
  `encoding="utf-8-sig"`. It is honest (fail-closed) and does discriminate (mutation table),
  but it is the family's most implementation-coupled row and should be read as "strict branch
  pinned", not "rule-derived".

## `why` citations

No row in this family cites an upstream path or `file:line` (the only numbers are `503`,
`'503'`, `64 KiB`). So there is **no frozen-numbering citation risk inside `EnvelopeShapes.json`**
— the concern named in the attack brief applies to other families (e.g. `NearMissTriple`,
`ForeignControls`), not here.

## Redundancy / non-discrimination summary

- Exact duplicate: `EnvelopeShapes.CodeAsString` ≡ `Overbroad503.code-string` (measured across
  all 72 rows by canonical `(status, headers, body, expected)`; 6 duplicate groups exist in the
  corpus, 5 of them outside this family).
- Mechanistically weak: `TopLevelArray` (the dict check it cites is not observable);
  `NestedEnvelope` overlaps `TopLevelArray` on the recursive-search mutant.
- Relative to the C1 change itself, 7/9 rows are **non-discriminating**: the frozen probe
  already passes them (control run above). That is expected — they are fail-closed regression
  guards, not change evidence — but the family's contribution to the 17-row changed set is
  exactly 2 rows, matching `measure.py`.

## Coverage gap (not a wrong row)

No row anywhere in the 72 supplies an **extra key inside the `error` object** (survey of all 53
parseable `error` objects in the corpus: every one has exactly `{message,type,code}` except
`MissingCode`, which is missing a key).
A stricter implementation requiring `set(error) == {message,type,code}` is therefore
indistinguishable from the landed code on the whole corpus, even though the landed code
allows inner extras. The C1 statement only promises "extra top-level keys allowed", so this is
a gap in the family's own "extras must not defeat detection" claim, not a contract violation.
Also uncovered corpus-wide (out of family, flagged for L1, [INFERENCE]): the documented
"python3 required, else old FOREIGN_SERVICE" fail-closed branch has no matrix row.

## Limitations

- Mutation table is my own predicate re-implementation over the stub bodies, not the probe;
  the probe's behaviour is established by the two real runs (current + frozen).
- The `BOM` judgment rests on RFC 8259 §8.1 reading, marked [INFERENCE]; no upstream
  llama.cpp evidence bares on it (llama.cpp does not emit a BOM).
- I did not re-run `measure.py` (contract) and did not modify any lane file; only this Report
  and `/tmp/kama-r16-FamilyEnvelopeShapes/` (removed after writing).

## Residual risk

Low. The family's oracles are implementation-faithful and the two positives are the only
change-discriminating rows; the risks are (a) the code-string duplicate inflating distinct
coverage by one, (b) the BOM row's future fragility if the parser is made lenient, and (c) the
missing inner-extras row.

Installs: none.
