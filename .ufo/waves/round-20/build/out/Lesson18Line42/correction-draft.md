## Erratum — round-18 line 42 wording superseded (appended in round 20)

- **Row "Handler installed implies SIGTERM necessarily terminates with 0" (line 42, rewritten in place by `30ed378`).** Original row, verbatim from `git show 8bf99cae:corpus/lessons/round-18.md | sed -n 42p` (byte-identical at `30ed378^`):

  > | Handler installed implies SIGTERM necessarily terminates with 0 | reject S043's overclaim; S047 narrows it | Same pinned files: `server.cpp` install at 534 precedes call at 576, and `server-queue.cpp:279` resets the handler's `running = false;` at 134. An actual termination guarantee additionally needs locking/shutdown assumptions. |

  Superseding wording, verbatim from `git show 30ed378:corpus/lessons/round-18.md | sed -n 42p`. Only the "Same pinned files" cell changes; the candidate cell, the decision cell and the closing sentence are identical in both:

  > | Handler installed implies SIGTERM necessarily terminates with 0 | reject S043's overclaim; S047 narrows it | Same pinned files: `server.cpp` install at 534 precedes call at 576, and `start_loop()` overwrites `terminate()`'s `running = false` (134) with `running = true` at `server-queue.cpp:279`. An actual termination guarantee additionally needs locking/shutdown assumptions. |

- **Reason for the superseding wording.** The original attributed the reset to `server-queue.cpp:279` and gave line 134 as its location. In the pinned file, line 134 is `running = false;` inside `terminate()` and line 279 is `running = true;` inside `start_loop()`. The superseding wording states that mapping. The verdict (reject S043's overclaim; S047 narrows it) is unchanged.
- **Status of line 42.** Line 42 keeps the `30ed378` wording. This correction, not the in-place rewrite, is the record of the original text; the original is quoted above verbatim.
