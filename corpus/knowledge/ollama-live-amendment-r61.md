# Ollama live-claim amendment ledger — round 61 (C2)

Contract: `registry/ollama-live-claims-r61.tsv` rows whose computed verdict contradicts
their recorded verdict append the *observed* JSON value (or its sha256) here verbatim —
the amendment is evidence of the honest miss, so the frozen counter
(`tools/round61-c2-counter.py`) can find it.

At freeze time no row is contradicted: all 17 bound rows compute `verdict=true` against the
committed receipt `.ufo/waves/round-61/live/receipt.json` (schema kama-ollama-live/v2).
This file intentionally starts empty below the rule block; contradicted observed values land
below this line in later amendments only.

## Amendments

(none)
