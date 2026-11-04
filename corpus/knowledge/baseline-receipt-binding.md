source: S550 — own re-runnable round-77 baseline counter (command + receipts below); the mechanics it rests on are held by S073 (git-log `--diff-filter`) and S175 (`merge-base --is-ancestor`); lane policy: plans/round-77-claims.md:30-82 and tools/round77-citation-baseline.py.
verified-at: 2026-11-04 -03 — dated documentation/design census at master 7d60e2ab58866a0366937d61c9712483be57b36e (freeze commit), base cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7. No C1 execution is claimed by this entry.
recheck: python3 tools/round77-citation-baseline.py --repo . --round 75; independently inspect introduction history and compare the receipt blobs at introduction and the audited tip.

# Baseline receipts bind to their introduction, not subsequent work

## Declared baseline class

The frozen round-77 C1 rule distinguishes a pre-work measurement from an at-the-tip
receipt. Only a receipt path under a `measured/before/` directory gets the baseline
rule. Its first five lines must identify one 40-hex revision R. Let I be the commit
that introduced that path and T the audited tip. Binding requires R to be an
ancestor of I and the receipt's bytes at I to equal its bytes at T. An old revision
alone is not a baseline credential.

S073 documents addition selection (the round's own live re-open of that manual, retained at `corpus/lessons/round-77.md` §Gate, produced the quote below); the fetched --diff-filter paragraph
names A as Added (retained HTML lines 6732-6736). Its complete sentence at line 6737
is: “Any combination of the filter characters (including none) can be used.”
Thus `git log --diff-filter=A --format=%H <tip> -- <path>` selects additions;
choosing the introducing addition, resolving ancestry and comparing historical
blob digests remain lane policy and work, not assertions supplied by that quote.
Access of the retained copy: 2026-11-04 -03. Retained bytes:
`.ufo/waves/round-77/w1/SC01Knowledge/git-log.html`, sha256
`0be728012bad1e48a590db5fa1cd56c9eb4cc746e4b3e1b9bb00954c90ec2961`.

## Why the delta-default rule is wrong here

A before receipt records the state before the work it motivates. Later tool or
registry changes are expected; requiring an unchanged instrument-input delta
from R to T would make a successful repair invalidate its own baseline. Header
ancestry establishes temporal eligibility; introduction-to-tip byte identity
keeps that baseline from being rewritten. Neither condition says the old
measurement describes the current tool.

At-the-tip receipts keep the inherited delta rule. The frozen round76 module
still excludes only declared self-description paths from shifting a receipt;
C1 must not excuse a `tools/` change for an ordinary receipt merely to reach a
population target.

## Three failure legs and controls

1. **Wrong ancestry:** R is not an ancestor of I. Keep the baseline shifted and
   name the ancestry failure; frozen arm `baseline-nonancestor` must reject it.
2. **Changed baseline bytes:** the blobs at I and T differ. Keep it shifted and
   name byte instability; `baseline-edited` must reject it.
3. **Wrongly widened ordinary-receipt rule:** an at-the-tip receipt has a
   non-self-description delta such as a `tools/` edit. It stays shifted;
   `shift-tools` must reject the attempted blanket old-revision exemption.

These are required failure witnesses, not runs performed by this documentation
seat. Missing/unreadable evidence is could-not-evaluate rather than proof of
binding. The inherited fenced-history and nonreceipt scopes still apply.

## Boundary

This dated census explains the frozen predicate, not a green demonstration of
its implementation. It proves no receipt's actual ancestry, digest equality or
semantic truth and does not establish the target bound=9 count. Two explicitly
named legacy headerless receipts may remain unbound under the plan; that is not
permission to bind a newly headerless baseline. Git documentation supplies
mechanics only, not endpoint health, round admission or causal correctness.
