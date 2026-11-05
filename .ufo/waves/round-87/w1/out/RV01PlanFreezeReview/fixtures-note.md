no-work probe results (see nw.py, nw-results.txt), run at the frozen selector sha f9d36b5be0683fdc…:
  closure-file-only   -> mismatches=2 closure=0 disposition=0 newest_closure=86  (row still names round-85; exit 1)
  scorecard-row-only  -> mismatches=1 closure=0 disposition=1 newest_closure=85  (disposition from body-word oracle; exit 1)
  both-edits          -> mismatches=0 exit 0 — but this rewrites corpus/lessons/round-86-verifier-spotcheck.md,
                         which the plan's fresh-start clause forbids ("history is retained and not repaired").
Conclusions:
  (a) No SCORECARD-only edit satisfies C1.1 (always at least the closure-shape mismatch remains).
  (b) No closure-file-only edit satisfies it either (the closure fact reads the row, not the file).
  (c) The only data-only path rewrites a tracked closure body — forbidden.
  => C1 requires the selector work; the no-work escape is closed for the SCORECARD-only variant,
     and the forbidden-history variant exists but cannot be a legitimate round deliverable.
