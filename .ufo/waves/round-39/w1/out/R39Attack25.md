# R39Attack25 — staged payload source-date provenance

## Finding
The working evidence records a fresh source opening on 2026-10-25 and ties the S472 row to that date, but the amendment filename is dated 2026-10-24. This is not itself a contradiction: the lesson says the amendment was staged beforehand and its source was reopened and re-grounded on the later date. The evidence supports the narrow source-date claim; it does not establish the exact time the staged package was created or independently validate the upstream page’s historical content.

## Observations
- `corpus/lessons/round-39.md:17-19` names staged amendment `served-identity-crosswalk-amendment-2026-10-24-r16.md`, says its source was re-grounded this round, and explicitly says S472 was opened by the lane on 2026-10-25. It records the OpenAI Markdown endpoint, located `created` quote, 1,657-byte capture, SHA-256 `2bbf06bb7a1687dbc9d25ce86c5d249b3f9d1e2c60efc32dbf7af2e4d052793f`, and a prior HTML fetch also dated 2026-10-25.
- `corpus/SOURCES.md:216` gives S472 opened date `2026-10-25`, recheck 90d, and `used-by` the dated amendment. Its scope expressly limits the source to field semantics, not local endpoint identity/readiness.
- `assimilation/openai-list.md` is the retained source capture; sibling evidence (`R39Attack01.md`, `R39Attack23.md`) records the same digest and quote. These are working-tree evidence, not proof that the claim was committed at the frozen base.
- `git status --short` in `/fast/scratch/hyaku/kama-r39` showed the R39 corpus/lesson additions as untracked, and the S472 row as part of the working `corpus/SOURCES.md` modification. The selected base commit is `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`; round-specific S472 is absent there per the existing no-op receipts.

## Limits / assessment
No observed inconsistency in the recorded source-opening date or row provenance; supports the narrow C1 source-date evidence, not a numeric score change. A fetched page and its local hash show what was retained, not a trusted timestamp or independent confirmation of the page’s content as of 2026-10-25. The filename’s 2026-10-24 stamp dates the amendment label, not the 2026-10-25 source observation. No live service was contacted and no checks were run.

## Evidence and scope
Read-only inspection of `/fast/scratch/hyaku/kama-r39` task spec, round-39 lesson, S472 registry row, assimilation source capture, and existing sibling reports; inspected lane Git log/status only. No files changed, no commands installed, and no out-of-scope repositories or runtime surfaces inspected.