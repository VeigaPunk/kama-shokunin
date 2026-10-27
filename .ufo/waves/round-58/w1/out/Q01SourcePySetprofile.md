# Q01SourcePySetprofile — source findings

Axes: operability (primary-source evidence) and calibration (precise scope).

- **Source / anchor:** [Python 3.15.2 `sys.setprofile`](https://docs.python.org/3/library/sys.html#sys.setprofile), anchor `#sys.setprofile` (section starts at rendered line 1464).
- **Quote verified:** “for example it isn’t called for each executed line of code (only on call and return, but the return event is reported even when an exception has been set).” The live page matches the requested quote.
- **Call-event semantics:** The same section defines `'call'` as “A function is called (or some other code block entered”; profiler callback receives `arg=None`. It defines `'return'` as a function/code block about to return; `arg` is the returned value or `None` when exception causes the event. It lists events `'call'`, `'return'`, `'c_call'`, `'c_return'`, `'c_exception'`.
- **Nested generator qualification:** The docs specify function/code-block entry events, not a separate generator-resume event. Consequently a nested generator's execution is profiled as its generator code block is entered/resumed and yields/returns through the documented call/return events; the quote alone does not imply a callback for each yielded value or executed line. Exact event sequencing across generator creation, each `next()`/resume, yield, and exhaustion is **not explicitly enumerated in this section**; avoid claiming more from this source alone.
- **Page revision date:** “Last updated on Oct 27, 2026 (16:42 UTC)” (page footer).
- **Access date:** 2026-10-27 (live URL read during this assignment).

## Checks
- Command: open/read `https://docs.python.org/3/library/sys.html#sys.setprofile` via `read`; output included the full section and quote. Exit code: not exposed by reader tool.
- Command: read `https://docs.python.org/3/library/sys.html:2020-2025`; output gave footer revision date. Exit code: not exposed by reader tool.
