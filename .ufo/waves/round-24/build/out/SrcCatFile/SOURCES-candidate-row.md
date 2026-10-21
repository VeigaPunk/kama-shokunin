# Candidate SOURCES row (not applied)

Next free id after S101 is S102, but `advice/SrcPromisorCode.md` already drafts S102.
L1 assigns the final id (S103 shown). This row is only for the negative wording
correction; if L1 prefers prose correction in the round-24 lesson, do not append it.

| S103 | Git git-cat-file batch-output scope correction — https://git-scm.com/docs/git-cat-file | docs | A | what a `--batch-check` `missing` record means at Git 2.56.0: a name unresolved at that invocation, not proof of absence; the page is silent on promisor/partial-clone fetching and on type-mismatch records | §BATCH OUTPUT missing paragraph, rendered lines 267-269, anchor `#_batch_output`, sentence “If a name is specified on stdin that cannot be resolved to an object in the repository” and record `<object> SP missing LF`; §OPTIONS `<type>`, lines 38-44, anchor `#Documentation/git-cat-file.txt-lttypegt`; page “git-cat-file last updated in 2.56.0” (2.56.0 dated 2026-09-28), installed man footer “Git 2.56.0 2026-09-27”; opened 2026-10-21 | supersedes S083 — the page says a name “cannot be resolved to an object in the repository”, not that the object is absent; rendered text has zero occurrences of promisor, partial clone, lazy or fetch; a `<type>` mismatch has no documented batch record or exit status, and the second `<object> SP missing LF` (line 289) is `--follow-symlinks`-only. | queued | 2026-10-21 | on-release | — |

Notes for L1:

- Status is `queued` because no committed consumer cites this row yet. Flip to `mined`
  only when `corpus/lessons/round-24.md` (or a knowledge entry) cites it by path.
- The quote is 17 words, well under the 25-word gate:
  “If a name is specified on stdin that cannot be resolved to an object in the repository”.
- If the lane instead prefers to keep S083 untouched, the same correction can live as
  lesson prose; S083's anchor and quote remain accurate, only its “absence” gloss is not.
