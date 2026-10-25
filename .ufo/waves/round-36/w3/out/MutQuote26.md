# MutQuote26 — round 36 wave 3 — 25-word bound on the S329 located quote

Seat: `.ufo/waves/round-36/w3/out/MutQuote26/`. Leaf, no subagents. No lane file was
edited; the probe lived entirely in scratch copies inside the seat directory.

## Measured

Source row: `corpus/SOURCES.md` line 462 (S329, SGLang `http_server.py` at tag v0.5.22).
Located quote, after the `lines 790-791 —` locator prefix, verbatim:

> Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead.

Detector (`wordcount_gate.py`): whitespace-token count of the located-quote text,
hard bound `len(quote.split()) <= 25`; exit 0 = PASS, exit 1 = FAIL.

| bytes | file | count | detector output | exit |
|---|---|---|---|---|
| pristine | `MutQuote26/s329-quote-pristine.txt` (sha256 18c42fa38c637e3cd5e9575e8c8542af570a275abd4b0bca36c025380ae7d348) | 16 | `16 words (limit 25) -> PASS` | 0 |
| mutant (26 words) | `MutQuote26/s329-quote-mut26.txt` (sha256 1328d15fe14667b6b82af22a979cbc9b2acec306823afcbcebfbbb6ce1afdec8) | 26 | `26 words (limit 25) -> FAIL` | 1 |

Mutant text (pristine + one appended 10-word sentence, smallest behavior-bearing
point for this bound — the word count itself):

> Endpoint '/get_model_info' is deprecated and will be removed in a future version. Please use '/model_info' instead. Users must migrate all client callers to the replacement route.

## Verdict per arm

- **Pristine (16 words): PASSES the 25-word check** (16 ≤ 25).
- **Mutant (26 words): FAILS the 25-word check** (26 > 25, one word over the bound).

## The check a gate must apply

`len(located_quote_text.split()) <= 25` — a **whitespace-token upper-bound check
applied to the located-quote field of each SOURCES registry row after stripping the
`lines X-Y —` locator prefix**. A gate without this per-row check cannot distinguish
the 26-word mutant from the compliant draft; with it, the mutant is killed at ingest.

## Restoration evidence

No lane byte was mutated, so restoration is a no-op verified by hash equality
(before == after, run at probe start and probe end):

```
ff192aca88362a8e87cff2aaa4679dd99e1c89da9994323ef6be43795d1439ee  corpus/SOURCES.md
7b6d36c66e0e9323209d487aa85e9653fb77a81dc07e3ecdabd64f65eb541491  corpus/lessons/round-36.md
cd79bba0b9bdec7ae714c1afef024b5e48d53b341558f77fef5bd90f33415a5c  corpus/knowledge/sglang-native-route-deprecation.md
825f7b3c1a79369cf0b1e9b68d39c36a1ea434d7a18ef600dc42fad8d3a99847  corpus/QUALITY.md
50432cfcfc6ece5b671a64fb9d8a3d9e775e82a8a088d7b786c15a8f55cc22d5  corpus/README.md
```

`MutQuote26/lane-after.sha256` holds the after-run hashes; both sets match, and no
mutating git/jj command was run anywhere.

## Inference (not measured)

- If the round-36 gate does not already enforce this bound on the quote field, the
  mutant survives the current gate set — a coverage finding against ingest, not a
  license to change the contract. The bound stands; the check is what must exist.
- Even counting the 2-token locator (`lines 790-791`) with the quote, the pass/fail
  split is unchanged (18 vs 28), so the verdict is robust to locator-inclusive counting.
