# kama round 41 lesson

author: kama L1
date: 2026-10-25
base: 8893b89466250c4d542912a867392698d2da00ce
freeze: 6fec0c4cd7b63ac733f2ae47fe73d1366b40c6dd

## Claims

C1 calibration 7 → 7 — the SCORECARD head `## Axes` table is the lane's standing self-assessment, and at base it did not match the tree: `tools/round41-scorecard-reconcile.py` reads `mismatches=16 met=False` (two stale md5s, two stale line counts, six unresolvable bare file names, freshness 7 and coverage 8 against the declared 8 and 9, four rows with no checkable fact). Round 10 had already noticed the table was stale (`SCORECARD.md` §Round 10, "predates round 10 and was not updated") and added a superseding table further down instead of fixing the head; every later round left it. The fix replaces the head table with one whose every hash, line count, run line and path re-derives at the measured commit and keeps the round-3 table below it byte-intact.

C2 operability 8 → 8, capability acquisition `pin-watch` — mines `considerthese/2026-10-25.md` proposal 2 ("Watch the version pins for upstream releases"). `tools/pin-watch.py` lists upstream release tags per pinned engine (`registry/engine-pins.tsv`) and reports, per pin, the newest release tag and the number of releases above it. Knowledge: `corpus/knowledge/engine-pin-watch.md`, sourced on S475 (opened this round) and own-work inventories S476, S477.

## Gate

New registry rows (CORPUS.md rule 1), each opened 2026-10-25 by the kama L1:

- **S475** — https://git-scm.com/docs/git-ls-remote, accessed 2026-10-25 (curl, page bytes SHA-256 `296a3d5cbc4dc359cd94da807e7c09db368186edb4c199cca625139d7c9b5f74`, copy `.ufo/waves/round-41/c2/git-scm-docs-git-ls-remote.html`). Located quote, §OUTPUT: "two such lines are shown: one with the refname for the tag itself as <ref>, and another with <ref> followed by ^{}" (22 words; the sentence opens "When showing an annotated tag, unless --refs is given,"). Admit: grounds the peeled-line rule in `tools/pin-watch.py` and the entry.
- **S476** — own-work `git ls-remote --tags https://github.com/vllm-project/vllm.git`, run 2026-10-25T20:03:21Z, exit 0, 224 lines, SHA-256 `13388e483163357aa4daea784d0e67cdc8d6b5438d3166d613a2a044590b9282` (`.ufo/waves/round-41/c2/ls-remote-vllm.txt`). Located quote, line 172: `5df63a7203cdb9328d824a27b682e77c7b9928be	refs/tags/v0.32.0`. Admit.
- **S477** — own-work `git ls-remote --tags https://github.com/ggml-org/llama.cpp.git`, run 2026-10-25T20:03:21Z, exit 0, 8199 lines, SHA-256 `c92b29afe168a98040b71d3d3db2fa5f343fb63b346e94b11f04d96044297b81` (`.ufo/waves/round-41/c2/ls-remote-llama.cpp.txt`). Located quotes, line 1287: `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad	refs/tags/b11755`; line 1412: `6050b467c07a95c7b87debd4ddac2f8ba8d9b807	refs/tags/b11887`. Admit.
- The SGLang pin reuses S474 (round 40); a fresh run at 2026-10-25T20:03:22Z reproduced its evidence digest `5585f6027df2dbc4dbafd4979b61c218ffd94e8af99936733218e0ae989e50f2` byte-for-byte (`.ufo/waves/round-41/c2/ls-remote-sglang.txt`). No S474 cell changed.

No existing row's `status`, `recheck` or `used-by` changed in this round's claim commit.
