VERDICT: confirm - Round-18 line 42 original and superseding text recovered byte-exact; the only in-place edit to pre-existing round-18 content since 8bf99cae is 30ed378 line 42; the two other in-place edits touched round-19's own appended erratum; draft correction written.

# Scope
Target: `30ed378` rewrote `corpus/lessons/round-18.md` line 42 in place. Lane tip `37bd4c5bd456a2f8a54d3312c28495c321715856`, base `8bf99cae7de2517fd4ebe209f3b940aeabb6b687`. Lane not modified (read-only `git show` / `git diff` / `git log`; no lane file written).

# Recovered text (all commands run, exit 0)
- `git show 30ed378^:corpus/lessons/round-18.md | sed -n 42p` -> exit 0; md5 `658e1de5…`.
- `git show 8bf99cae:corpus/lessons/round-18.md | sed -n 42p` -> exit 0; md5 `658e1de5…`; `cmp` with the `30ed378^` line -> exit 0 (identical).
- `git show 30ed378:corpus/lessons/round-18.md | sed -n 42p` -> exit 0; md5 `19a0873b…`; `cmp` with `37bd4c5…` line 42 -> exit 0 (identical).
- Original (338 bytes), verbatim: `| Handler installed implies SIGTERM necessarily terminates with 0 | reject S043's overclaim; S047 narrows it | Same pinned files: \`server.cpp\` install at 534 precedes call at 576, and \`server-queue.cpp:279\` resets the handler's \`running = false;\` at 134. An actual termination guarantee additionally needs locking/shutdown assumptions. |`
- Superseding (382 bytes), verbatim: `| Handler installed implies SIGTERM necessarily terminates with 0 | reject S043's overclaim; S047 narrows it | Same pinned files: \`server.cpp\` install at 534 precedes call at 576, and \`start_loop()\` overwrites \`terminate()\`'s \`running = false\` (134) with \`running = true\` at \`server-queue.cpp:279\`. An actual termination guarantee additionally needs locking/shutdown assumptions. |`
- `git diff --word-diff=plain 30ed378^ 30ed378 -- corpus/lessons/round-18.md` -> exit 0; the only changed span is the "Same pinned files" clause.
- Copies saved: `.ufo/waves/round-20/build/out/Lesson18Line42/round-18-line42-original.txt`, `…/round-18-line42-superseding.txt`.

# Commits touching round-18.md since 8bf99cae
`git log --format='%h %s' 8bf99cae..37bd4c5… -- corpus/lessons/round-18.md` -> exit 0: `30ed378`, `028235e`, `f1790e2`, `7229fa9`. (`37bd4c5` does not touch the file.)

| Commit | Change to round-18.md (`--stat`/`--numstat`) | Pre-existing round-18 content touched? |
|---|---|---|
| 7229fa9 | +36 lines, append `## Erratum — round-19 routed defects` and `## Round-19 citation provenance` at end | No (append) |
| f1790e2 | 1+/1-, one `cite(…, live-gate-1.stdout, sha256=…)` line inside the round-19 citation block: rev `eb78788b…`→`1b85a24e…`, sha `b2043ba8…`→`1cb5a41b…` | No (round-19 appended text) |
| 028235e | 3+/1-, one bullet inside the round-19 citation block replaced by a revision-qualified bullet plus `cite(1c325b2e…, …live-gate-1.stdout…)` and a second bullet | No (round-19 appended text) |
| 30ed378 | 1+/1-, line 42 | **Yes: the only in-place edit to pre-existing round-18 content** |

Cumulative check: `git diff --numstat 8bf99cae 37bd4c5… -- corpus/lessons/round-18.md` -> exit 0, `39 1`. Hunks: `@@ -39,7 +39,7 @@` (the single line-42 pair) and `@@ -383,3 +383,41 @@` (pure append of 38 lines). Line count 385 -> 423 = 385 + 38. No other in-place edit to lines 1–382 of the pre-existing lesson.

# Note on f1790e2 and 028235e
Both edited text that round-19 appended in `7229fa9`, not round-18 text. The wave's "append, never rewrite" rule still applies to those bytes; flagged for the L1 as a finding, not as a defect in round-18 content [INFERENCE: whether the rule covers an appended erratum's own lines is a policy question for the L1].

# Line-42 claim check (pinned file, read-only)
- `git show 37bd4c5…:.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/server-queue.cpp` -> exit 0; sha256 `168385b7…`; saved in `/tmp` scratch (deleted before finish).
- `grep -n running` -> exit 0: line 134 `running = false;` (inside `terminate()`, lines 132–136); line 279 `running = true;` (inside `start_loop()`, from line 278).
- Conclusion: the `30ed378` wording matches the file; the original's "279 resets … at 134" inverts the attribution. The verdict (reject S043; S047 narrows) is not changed.
- [INFERENCE] The lane's sources copy equals the upstream blob at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` cited in the lesson; not checked (no network, no blob hash comparison).

# Draft correction (for L1 to append; not written into the lane lesson)
File: `.ufo/waves/round-20/build/out/Lesson18Line42/correction-draft.md`. It is titled `## Erratum — round-18 line 42 wording superseded (appended in round 20)`, records the original row verbatim, quotes the superseding row verbatim, states the reason, and keeps the verdict unchanged. It does not revert line 42, per the wave's "append a correction, never rewrite" rule [INFERENCE: a revert, if the L1 chooses one, is a separate decision].

# Out of scope / not done
- No lane file edited; no append made to `corpus/lessons/round-18.md`.
- No build, test or live step run (not assigned).

# Tools
None installed or updated.

# Artifacts
- `.ufo/waves/round-20/build/advice/Lesson18Line42.md` (this report)
- `.ufo/waves/round-20/build/out/Lesson18Line42/correction-draft.md`
- `.ufo/waves/round-20/build/out/Lesson18Line42/round-18-line42-original.txt`
- `.ufo/waves/round-20/build/out/Lesson18Line42/round-18-line42-superseding.txt`
