# TriplicateName — corpus-guard fixture matrix (R15, outside R1)

## Files changed
- `tests/ollama-corpus-guard/TriplicateName.json` (new, sole assigned file)

## Fixture shape
Shared schema: array of objects `{name, names, envelope, expected_rejected}`.
`names` are literal JSON string arrays (no expressions); `envelope` is
`"array"` or `"object"` matching `load_cases` in
`.ufo/waves/round-15/frozen/measure-before.py` (top-level list vs
`{"cases": [...]}`).

## Matrix (6 scenarios, all `TriplicateName`-prefixed ids)

| id | entries | distinct stripped | envelope | expected_rejected |
|---|---|---|---|---|
| `TriplicateName_array_n08_triplicated_separated` | 18 | 16 | array | true |
| `TriplicateName_object_n08_triplicated_separated` | 18 | 16 | object | true |
| `TriplicateName_array_n08_triplicated_adjacent` | 18 | 16 | array | true |
| `TriplicateName_array_n08_triplicated_strip_equivalent` | 18 | 16 | array | true |
| `TriplicateName_array_16_distinct_no_duplicate` | 16 | 16 | array | false |
| `TriplicateName_object_16_distinct_no_duplicate` | 16 | 16 | object | false |

- Invalid scenarios hold `n08` three times (separated positions, adjacent
  run, or whitespace-padded strip-equivalents `" n08"` / `"n08 "`), giving
  16 distinct stripped names — above `MINIMUM_UNIQUE_CASES` = 16, so the
  old unique-count-only guard cannot reject them; only a total-vs-unique
  duplicate check can.
- Valid counterparts are the same corpora with the two extra `n08`
  entries removed: 16 distinct, no duplicates, both envelopes.
- Every name is a non-empty stripped string, so all scenarios exercise the
  real duplicate corpus policy (`corpus_problems`), never malformed-schema
  or missing-name paths.

## Evidence retained
- `.ufo/waves/round-15/frozen/measure-before.py:350-362` —
  `corpus_problems` strips names, counts `len(set(declared))`, and only
  flags `unique < MINIMUM_UNIQUE_CASES`; total-vs-unique is never
  compared, so 16-unique duplicate corpora reach `measure_case` children.
- `.ufo/waves/round-15/frozen/measure-before.py:109-128` — `load_cases`
  accepts list or `{"cases": [...]}` envelopes (drives `envelope` field).
- `.ufo/waves/round-15/frozen/measure-before.py:354` — `name.strip()`
  canonicalization (drives the strip-equivalent scenario).

## Limitations / risks
- No execution or generation performed per lane bounds; fixtures are
  static literals only. Harness cloning/validation belongs to
  `GuardHarness` and the L1 post-integration gate.
- The strip-equivalent scenario assumes the harness injects each `names`
  item verbatim as the case `name`; if the harness itself normalizes
  names before writing, `" n08"`/`"n08 "` still arrive at the guard
  unchanged only if stored verbatim — expected_rejected stays true either
  way since the guard strips before comparing.
- No tool installs or upgrades performed (prefer-no-installs guidance).

Report: .ufo/waves/round-15/build/advice/TriplicateName.md
