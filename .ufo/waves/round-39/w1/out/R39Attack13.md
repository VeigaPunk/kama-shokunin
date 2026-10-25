# R39-13 — base/tip byte re-derivation

**Axes:** calibration, coverage. **Verdict:** no byte-count counterexample observed for the base/tip files I re-derived; however the reported source reopen byte size is not independently verified by this lane evidence.

- At frozen base `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`, `git show <base>:corpus/SOURCES.md | wc -c` yields **183,011** bytes; working tip `wc -c corpus/SOURCES.md` yields **183,695**. README: **37,703 → 38,234** bytes. These are consistent with additions but byte growth alone does not establish claim predicates.
- The new amendment at tip is **3,994** bytes; `git cat-file -e <base>:corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` fails (exit 128), consistent with absence at base.
- `LOG.md:11` reports the reopened OpenAI List models Markdown as **1,657 bytes**, but the round-39 assimilation evidence directory contains no captured upstream Markdown body/byte-count receipt for independent byte re-derivation. The quoted line/text and that size therefore remain a provenance limitation, not a demonstrated false count.
- `assimilation/claim-after.out` records S472 row census and C1/C2 counters; those records do not record byte sizes. Thus C1 calibration 7→7 and C2 coverage 9→9 remain unchallenged by byte counts here; the size of the quoted upstream artifact is not independently substantiated.

**Smallest safe correction:** include a retained exact upstream body (or immutable local capture) and its `wc -c` output/command in the provenance record; keep the byte count distinct from the claim counters and do not infer either axis score from file growth.