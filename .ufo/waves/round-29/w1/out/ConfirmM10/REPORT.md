# ConfirmM10 — sid `SCORECARD.md:P:1c6c1f3e4c:0`

## Verdict: confirmed-false (counter `p:absent` is correct)

Base statement (SCORECARD.md line 1349 at 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d):

```
	(`.ufo/reports/round-25/kama.md:120-129`: quality unchanged, discernment
```
(continues on 1350: `unchanged) and the outside closure (...)` — part of
"### Round 26 correction — round-25 trend verdicts (routed defect 6)").

## Hand-applied class P rule (count-c1.py docstring, not executed)

> P `path:L`/`path:L-M`: the blob `W:path` exists and has at least max(L, M) lines (fail: p:absent, p:beyond-eof)

- Writing revision: `git blame -L 1349,1349 --line-porcelain 2aa46e24 -- SCORECARD.md`
  → `7f84cd0e7662432b7b93e7586f86a40b06e5fdae` (committer time 1792727435 =
  2026-10-23T03:50:35Z; summary "round-26: C1 live error signatures …").
- `git cat-file -e 7f84cd0e:.ufo/reports/round-25/kama.md` → fatal: path does not
  exist (exit 128) → **p:absent**, not p:beyond-eof.
- Stronger: `git log --all --follow -- .ufo/reports/round-25/kama.md` in the lane
  repo is empty — the path **never existed at any lane revision**, so this cannot
  be repaired by any later lane commit either.
- Decisive detail: the lane's `.ufo/` at W does contain a `reports/` directory,
  but its only entry is `round-5/kama.md`. The pointer is therefore
  lane-plausible in form while unresolvable in fact.

## Intended referent

The fleet repo's round-25 report:
`/home/vgpnk/Projects/shokunin/.ufo/reports/round-25/kama.md` — tracked in the
fleet repo, committed at `f1a75c9` ("round-25: kama report", committer time
1792664361 = 2026-10-22T10:19:21Z, ~17.5 h before W), 177 lines, unchanged since
that commit (working-tree mtime equals the commit time; `git diff --stat
f1a75c9 -- <file>` empty). Its lines 120-129 read exactly:

```
- **quality: unchanged** — routed wording and count corrections
  ...
- **discernment: unchanged** — attack findings were turned into stricter
  counters and scoped claims, but the round declared C1 on an axis it does
  not fit; C1 earns no calibration credit.
```

This is precisely the content the SCORECARD sentence cites ("quality unchanged,
discernment unchanged"). So the sentence's *substance* was true at writing
against the fleet artifact; the *pointer* is wrong for the lane-resolved P class
(fleet-relative file spelled as a lane-relative path). Under the frozen
predicate the statement does not hold at W — the counter's `p:absent` is the
right observed value.

## Cause (correction-row wording)

Pointer cites the fleet repo's .ufo/reports/round-25/kama.md; that file exists
only in the fleet repo, never in the lane tree.

## Residual risk / gaps

- None material. All checks are read-only git in the lane repo plus read-only
  inspection of the fleet working tree/fleet git; no counter execution, no
  writes to tracked lane files.
- `git diff --stat f1a75c9 -- .ufo/reports/round-25/kama.md` compares the
  committed blob against the current index/worktree of the fleet repo; it
  produced no output (unchanged). Line count and lines 120-129 verified from
  the committed blob itself.
- Tooling directive: no tools installed (git and python3 already present).

Outputs: `verdict.json` (same directory), advice at
`.ufo/waves/round-29/w1/advice/ConfirmM10.md`.
