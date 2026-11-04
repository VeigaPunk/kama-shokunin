# A `behind` relation is a recheck trigger, not knowledge drift

source: S563
verified-at: 2026-11-04
recheck: `python3 tools/pin-watch.py check --repo .` then re-open each `behind` row's pinned document at its own ref (`S564` for llama.cpp)

## The register and its two numbers

`registry/engine-pin-relations.tsv` relates every pinned serving-engine ref the lane holds to the
newest upstream tag at a dated read. Two cells carry the whole signal: `newer` (how many releases sort
above the pinned ref) and `newest` (the tag observed). Neither cell says anything about knowledge: the
register is a **trigger**, and the only question it licenses is "does the document the lane cites still
state what the lane holds?".

## The cheapest honest resolution

Re-open the pinned document at the **pinned** ref (S564, `tools/server/README.md` at `b11755`) and at
the **newest** tag (S563, the same file at `b12103`), then locate the anchored statement in both. The
round-82 read: the `### GET /health` section shifts one line (479 → 480) and the sentence the lane
relies on — "This endpoint is public (no API key check). `/v1/health` also works." — is byte-identical
at both refs, while the document grows 2402 → 2620 lines (audio and voice surfaces). The release gap
of 348 tags produced no change in the held health statement, so the relation row's `behind` count is a
recheck trigger whose verdict is `holds`, not a drift finding.

## What a recheck row must carry

A graded recheck names the relation row (engine + ref), the newest tag observed at the recheck date,
the two document URLs with their sha256, the located anchor (line number plus the quote), and a verdict
from {`holds`, `reworded`, `moved`, `drifted`}. A newer-tag document that says something else is
`reworded` or `drifted` only when the anchored *statement* changed; a line shift is `holds` with the
new line number recorded.

## Limits

- The relation register and a recheck say nothing about model quality, served behavior or whether an
  engine is running; those stay with the probe and the registry rows.
- A `behind` row never invalidates a mined corpus row by itself. Corpus drift is decided by re-opening
  the cited source under `CORPUS.md` rule 1, which is what a recheck row's evidence is.
- The register's `newest` value is a dated observation: upstream can move between two reads, so a
  recheck's receipt must name the tag list it saw.
