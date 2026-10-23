# ConfirmM08 — C1 first falsifier, sid SCORECARD.md:Q:f1021c03db:0

## Statement

Base SCORECARD.md line 833 (connect 2aa46e24), written by W = `7229fa95eb122310e9e5334ad799ee3006293ebd`
(round-19, "citation provenance, install-tree pin, r18 defect corrections"):

```
`baseline=VALID members=3 rejected=0/3` exit 1, with `--tree-sha`
```

Class Q (quoted measurement output), token `` `baseline=VALID members=3 rejected=0/3` ``.
Counter observed `q:no-artifact` — the span is not byte-identical in any committed blob of the
tree at W other than SCORECARD.md / SHONEN.md / LOG.md / corpus/**.

## Independent verification (counter not run; git read-only only)

1. **W confirmed by blame** — `git blame -L 833,833 --line-porcelain 2aa46e24 -- SCORECARD.md`
   names `7229fa95eb122310e9e5334ad799ee3006293ebd` (author/committer kama-shokunin,
   committer-time 1792564487), summary "round-19: citation provenance, install-tree pin, r18
   defect corrections", previous line blob `8bf99cae…`.
2. **Full line at base** reads exactly `` `baseline=VALID members=3 rejected=0/3` exit 1, with `--tree-sha` ``.
3. **Q rule by hand**: span length 37 (6–200 ok), contains digits and "=" (ok), does not start
   with python3/python/bash/sh/git/node/./tools// (ok). It must occur verbatim in ≥1 blob of the
   tree at W outside the four exclusions.
4. **Verbatim search at W** — `git grep -F -n 'baseline=VALID members=3 rejected=0/3'
   7229fa95 -- ':!SCORECARD.md' ':!SHONEN.md' ':!LOG.md' ':!corpus'` → **no matches** (exit 1).
   The only places the string appears anywhere at W are the statement line itself
   (SCORECARD.md:833, excluded) and, for the *prefix* `baseline=VALID`, SCORECARD.md:834
   (excluded) and the tool docstring template
   `tests/llamacpp-live/install-tree-grid.py:16` — `` `baseline=VALID|INVALID members=N rejected=K/N tree_pin=on|off` ``,
   which is **not** verbatim (has `|INVALID`, `members=N`, `K/N`, `tree_pin=on|off`).
5. **Intended referent** — the statement belongs to round-19 SCORECARD C2 (sixth pin
   `--expect-install-tree-sha256`). The counting tool prints (install-tree-grid.py:113–115):

   ```
   baseline=<VALID|INVALID> members=<n> rejected=<k>/<n> tree_pin=<on|off>
   ```

   so the no-pin run summary would be `baseline=VALID members=3 rejected=0/3 tree_pin=off`
   exit 1. That full line first appears in committed artifacts in **5b108c1**
   (`round-19/evidence/c2-grid.txt`, `round-19/build/advice/*.md`), a verified descendant of W
   (`git merge-base --is-ancestor` exit 0). At W no capture of the run exists (the round-19
   wave tree at W contains only build/assignments.json, build/dispatch.json, build/spec.json,
   build/advice/swarm-registry.json).
6. **Later artifacts**: at master the span occurs only in post-W files
   (advice/evidence under `round-19`, `round-20/build/out/*.stdout`, round-29 receipts and
   control artifacts) — none existed at W.

## Verdict

**confirmed-false** — the counter's `q:no-artifact` is correct. At W no committed artifact
(other than the statement's own file) carries the quoted span verbatim: the quote truncates
the real output line (`… tree_pin=off` dropped) and was written from the tool's documented
format, not from a captured artifact that existed at W.

Cause (≤25 words, for the correction row):
> Quoted baseline output never existed verbatim in any committed artifact at W; the statement paraphrased the tool's documented format.

## Residual risk / verification gaps

- The statement could be read as citing the *expected* output format rather than an observed
  capture; under the frozen Q rule the bar is verbatim occurrence in a committed blob at W,
  which fails regardless.
- I did not run install-tree-grid.py (no runtime needed; no llama-server involved). The exact
  rendered summary line is inferred from the print statement at W (`[INFERENCE]`, installed by
  reading install-tree-grid.py:105–120 at W).
- No other Q failure mode (e.g. span starting with an excluded prefix) applies: the span is
  cleanly a measurement-output quote; failure is purely absence of the artifact.
