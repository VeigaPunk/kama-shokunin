VERDICT: confirm - registry row r18-validation-supplement matches its cite token and `git show <rev>:<path>` bytes exactly; doc binding holds but is retrospective (token added after the pinned rev).

# Row under test (registry/required-citations.json:37-43)
- id `r18-validation-supplement`, rev `101f3991d3570bc9350fbf9c5561f4be1185699d`,
  path `.ufo/waves/round-18/build/validation-supplement.json`,
  sha256 `b081d09c0c89c8b463610b6b2523a19e1934d36543897284b6b3310412511f03`,
  doc `corpus/lessons/round-18.md`. Exactly 1 row with this id (grep -c = 1).

# Matching cite token (corpus/lessons/round-18.md:461)
- `cite(101f3991d3570bc9350fbf9c5561f4be1185699d, .ufo/waves/round-18/build/validation-supplement.json, sha256=b081d09c0c89c8b463610b6b2523a19e1934d36543897284b6b3310412511f03)`
- Exactly 1 occurrence in the current doc (grep -cF = 1).
- Programmatic tuple compare (rev, path, sha256) row vs token: True.

# Byte verification (read-only git)
- `git rev-parse --verify 101f3991^{commit}` OK; commit dated 2026-10-20 20:36:34 -0300,
  subject "checkpoint(r18): preserve developed code, tools, corpus and evidence after
  coordinator quota failure; unadmitted".
- `git show 101f3991:.ufo/waves/round-18/build/validation-supplement.json | sha256sum`
  = `b081d09c0c89c8b463610b6b2523a19e1934d36543897284b6b3310412511f03` (1009 bytes).
  Row == git bytes: True. Blob exists at the pinned rev, so the artifact pin is
  contemporaneous with the round-18 checkpoint (unlike the residual-assignments case).
- Worktree copy of the artifact hashes identically: no drift for the pinned artifact.

# Doc binding
- Row.doc names corpus/lessons/round-18.md; that file carries the exact matching token
  at line 461, and prose reference at round-18.md:215 ("build/validation-supplement.json").
- Canonical frozen evidence agrees: .ufo/waves/round-20/runs/0957ce61/citation-count.stdout:72-83
  lists the same rev/path/sha256, documents=[.../corpus/lessons/round-18.md],
  observed_sha256 equal to pinned sha256, error null, status ok.

# Findings
1. [confirm] Revision, path, SHA-256 and doc binding all match; no mismatch found in this row.
2. [limitation] The doc binding is retrospective: corpus/lessons/round-18.md at the pinned
   rev 101f3991 does NOT contain the cite token (git show | grep -cF token = 0) and hashes
   to `b6687628cfd4d17e4dcc0ba73e5ed2934c653d1ac390dd434092992556292b53` there vs
   `a42351338885d77d590b0bbb909a6a78bf3135e4fd02d8c9b218c993749ae0b7` in the worktree.
   The token first appears at rev `33a6777866d0f63d894ef21bc863486bcb35b56c`
   (2026-10-21 05:01:18 -0300, git log -S), i.e. ~8.5h after the pinned checkpoint, and the
   doc has 7 further commits up to HEAD. No registry field pins the doc's own bytes, so the
   citation appendix is a later round-19/20 edit, not part of the round-18 checkpoint.
   The pinned artifact itself IS contemporaneous; only the token is later.
3. [note] Same retrospective-token pattern likely applies to the other round-18.md:459-464
   appendix rows; sibling lanes cover those. Out of my scope.

No registry or document was modified; no scratch was needed (read-only git + sha256sum only).
