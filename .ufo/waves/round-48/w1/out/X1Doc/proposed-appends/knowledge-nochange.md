# `corpus/knowledge/` — census result: no v3 drift, no append proposed

Measured at `380bcdff9c8af06997c482f6eb03db926a794a2b` over all 36 files of `corpus/knowledge/*.md`.

Census commands (run against the committed blobs, not the working tree):

```
git show 380bcdff:<file> | grep -n "append-only-audit\|append-only-contract\|contract\.tsv\|append-only/v"
git show 380bcdff:<file> | grep -n "append-only"
```

Result: **zero** knowledge lines cite `tools/append-only-audit.py`, the contract file, the schema string, a cell
count, or a command whose output changes under v3. The only `append-only` mentions are three, and each is correct at
the build:

| line | text | disposition |
|---|---|---|
| `corpus/knowledge/consumer-registry.md:30` | `## Errata — 2026-10-14 re-census (append-only; rows below keep their round-1 text)` | The row added in round 48 uses this as its `declared_at` (`A-corr`, `only=## Errata@…:30`); the tool reports `declarations[8] = {path: corpus/knowledge/consumer-registry.md, declared_at: …:30, region: only, ok: true}` (`evidence/02-audit380.json`), and the heading census now marks it `covered=yes` (`evidence/15-heading-census-380.out`). Nothing to append: the heading is the declaration, not a stale claim. |
| `corpus/knowledge/context-capacity.md:245` | `## Errata — round 26` | Carries no "append-only" word and has no contract row; KQ71 therefore does not bind it, and a round that cites it must still disposition it. No correction is possible in the entry without inventing a declaration the file does not make. |
| `corpus/knowledge/served-identity-crosswalk.md:94` | "here because registry cells are append-only" | A `corpus/SOURCES.md` `A-row` claim whose `declared_at` is `SKILL.md:578` and whose guard is `tools/sources-append-only.py`; unrelated to `append-only-audit`. Still true. |

`corpus/knowledge/instrument-run-agreement.md:20` cites `tools/sources-append-only.py` — a different instrument, also
still true.

So the knowledge surface contributes **no** drift item for this round and no proposed append; the one KQ71
counterexample that named it lives in `corpus/QUALITY.md:398` and is superseded there, not here.
