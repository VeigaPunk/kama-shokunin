VERDICT: confirm - registry row r18-live-receipt-1 matches its cite token and the pinned `git show <rev>:<path>` bytes exactly; no mismatch in any checked field.

Seat: KamaR18Recovery.CitationR18LiveReceipt1-2 (leaf, read-only). No lsp device in this seat's toolset; item is byte/JSON-level (no code-symbol resolution), evidence below is command output and file:line. Git use was read-only show/rev-parse/cat-file/diff/status per parent clarification.

Row under test — registry/required-citations.json:30-35 (only occurrence of this id, line 31):
  id   r18-live-receipt-1
  rev  1c325b2e58fcfdc6761f645b44cedfb1d65243e6
  path .ufo/waves/round-18/live/receipt-1.json
  sha  e616f67e2e2bec196402f56ed3a45fb68f78c9f4e927f0ea7d8acd170caf6d75
  doc  corpus/lessons/round-18.md

Checks (observed 2026-10-21, all commands read-only):
1. rev exists: `git cat-file -t 1c325b2e…` = commit; 2026-10-20 20:13:58 -0300,
   "round-18: retain measured arms and repair counter classification seams".
2. path at rev: `git rev-parse 1c325b2e…:.ufo/waves/round-18/live/receipt-1.json`
   = blob 6b23f87eadf0ec189d3fd141a55c9f0a1f2553d3 (path present at pin).
3. sha256 of pinned bytes: `git show 1c325b2e…:<path> | sha256sum` =
   e616f67e2e2bec196402f56ed3a45fb68f78c9f4e927f0ea7d8acd170caf6d75, 27632 bytes —
   byte-exact match to the row's sha256.
4. drift: working-tree .ufo/waves/round-18/live/receipt-1.json has the same
   sha256 and 27632 bytes; `git diff --stat 1c325b2e… -- <path>` lists no change
   for the receipt. Pinned bytes = current bytes.
5. doc binding: doc field corpus/lessons/round-18.md contains the matching cite
   token at corpus/lessons/round-18.md:460:
   `S055 receipt: cite(1c325b2e58…, .ufo/waves/round-18/live/receipt-1.json, sha256=e616f67e…)`
   — rev, path, and sha256 each identical to the registry row.
6. bound-content sanity: receipt JSON `outcome`="pass"; `checks` length=11 with
   all 11 `evaluated`=true and `passed`=true (e.g. checks[0] id=health_ready) —
   matches the binding claim in corpus/lessons/round-18.md:53
   ("`outcome`: `pass`; `checks`: 11 evaluated true").
7. frozen-evidence consistency: identical row values at
   .ufo/waves/round-20/runs/0957ce61/citation-count.stdout:61-64 and
   .ufo/waves/round-20/build/out/R18CitationRows/required-citations.json:31-34.
8. cleanliness: `git status --porcelain` on the registry, the doc, and the
   receipt is empty — all three are committed at HEAD; the cite token at
   round-18.md:460 is not a dirty-tree artifact.

Observation (not a mismatch, recorded for honesty): the formal `cite(...)` token
(round-18.md:460) does not appear in the doc bytes at the pinned rev —
`git show 1c325b2e…:corpus/lessons/round-18.md | grep -n receipt-1` returns only
line 53 — and round-18.md gained +288 lines since the pin (`git diff --stat`).
The row's doc field carries no rev pin; the token matches the row at current
HEAD, so the binding holds. The token postdates the pinned artifact, consistent
with the R18 recovery appendix that also cites 101f3991… artifacts
(round-18.md:461-463).

Residual risk: none found for this row. Scope was this single row; sibling rows
(s055-commands, gate-live-1, c2-official-stdout, r18-validation-supplement) were
only read as context, not verified.

No mutations, no scratch directory needed; registry and documents untouched.
