VERDICT: partial — the C1 and C2 motivating evidence and the S041 and jj-risk facts reproduce against the files; two jj-risk claims need correcting (`.ufo/state/` is an uncommitted worktree edit; `registry/history/.lock` is already ignored).

# Scope and writes

- Owned draft: `.ufo/waves/round-17/build/drafts/log-entry.md` (written, 4222 bytes). No lane doc was edited.
- Access date for every source below: 2026-10-20. Local paths only; no URLs were quoted.
- Git use was read-only (`rev-parse`, `show`, `status`, `diff`, `check-ignore`, `ls-files`, `log`). No `jj` command was run. No measurement script, mutant runner, llama-server or fake server was started; no port was bound.

# Findings with located quotes

## C1 — verdict-matrix gate (`tests/probe-verdicts/check.py`)

- `.ufo/waves/round-16/falsify/advice/MutateHarness.md:20` — "**Result: survived 5; killed 0; inconclusive 0.**"
- `.ufo/waves/round-16/falsify/advice/MutateHarness.md:150` — "**The timeout exception path was not exercised.**"
- `tests/probe-verdicts/check.py:340-347` — the pass expression compares verdict, reason, `probe_exit`, and drift. Mutants delete the reason, exit and drift terms, casefold the verdict, or pass on timeout.
- `tests/probe-verdicts/check.py:329-338` (read this session) — the `try` ends at line 336 (`return record`). Lines 337-338, `for key in ("verdict", "reason", "drift", "served_model", "evidence"): record[key] = row.get(key)`, sit outside it. A non-object `rows[0]` would raise there. This is [INFERENCE] from reading; the traceback was not run.
- `served_model` is not graded in the pass expression, and there is no route-match assertion. Both match the brief; I did not grep for them beyond the 337 read.

## C2 — live llama.cpp harness (`tools/kama-llamacpp-live.py`, 1078 lines)

- `tools/kama-llamacpp-live.py:938-939` — "`checks.append(_check('health_ready', health_status == 200,`" grades status only.
- `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:68` — "## H1 — No check grades the loading envelope (high)". Read with `kama-llamacpp-live.py:922`, "`receipt['loading_envelope_exact'] = loading_envelope_exact(loading_503)`", which no check consumes.
- `tools/kama-llamacpp-live.py:1024-1028` — `teardown_exited` asserts `receipt['teardown']['returncode'] is not None`. Its `sigterm_sent false` self-exit case passed in the advice run `se`.
- `tools/kama-llamacpp-live.py:1020-1021` and `1026` — the exception path stores `{'error': ...}` and then indexes `['returncode']`. The advice fault run showed `ESCAPED KeyError` and `receipt_written False`. Reproduced by the advice author, not by this seat.
- Harness sha at review was `b8c5e8d4…`. The file is now 1078 lines, the same count the advice recorded, and the cited lines match it.

## Mined mistake — SOURCES S041

- `corpus/SOURCES.md:53` — the S041 row is `own-work`, tier A, `mined`, with the receipt as anchor.
- `corpus/lessons/round-16-verifier-spotcheck.md:184` — "Contract rule 2 lets only `status`/`recheck`/`used-by` change in place, so a later receipt regeneration must take a superseding row."
- `corpus/SOURCES.md:3` — "Contract: `SOURCES-CONTRACT-v1` (kaika, 2026-10-19, frozen)." **Unknown:** the contract text is not in this lane. Rule 2 is known only through the lesson's quotation.
- `corpus/lessons/round-16.md:147` — "S041's anchor and teaches cells were amended before closure because the receipt file was regenerated". This differs in wording from line 184 (`after the row's first commit`), but both place the first commit at `b8e485c`.
- Fix target `tools/sources-append-only.py` does not exist (checked: `No such file or directory`). `tests/probe-verdicts/fault-controls.py` and `tests/llamacpp-live/controls.py` also do not exist. `.ufo/waves/round-17/c1/` is an empty directory, so `mutants.py` is absent.

## jj-migration risks — `.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md`

- Line 154, R1 — "Under jj, `@` is perpetually ahead of `HEAD` until the helper commits and moves the bookmark".
- Line 156, R2 — "`git rev-parse HEAD` exits 128 in a colocated repo with no commits."
- Line 158, R3 — "`jj commit -m … -- <untracked>` prints a warning, creates an empty commit, and **exits 0**".
- **Correction to the brief's `.ufo/state/` claim.** `git show master:.gitignore` (committed cff9e62) prints only `.ufo/interactive-sessions/`. `git diff -- .gitignore` shows the uncommitted line `+.ufo/state/`. So `.ufo/state/` is not ignored in committed history; the fix exists only in the worktree. `git ls-files .ufo/state` returns 0 entries, and `.ufo/state` does not exist on disk.
- **Correction to the brief's `registry/history/.lock` claim.** `git show master:registry/history/.gitignore` lists `.lock` at line 3, and `git check-ignore -v --no-index registry/history/.lock` reports that line. The risk is not present.
- Worktree state at read time, outside this seat's scope: ` M .gitignore`, ` M AGENTS.md`, `?? .ufo/waves/round-17/`. The draft records this for L1.

# Limitations

- The draft's measured fields are `[L1 fills]`. I did not run `check.py`, `mutants.py`, `controls.py` or the live tool, so no measured number is claimed.
- The C2 line numbers come from the advice author's review at `b8c5e8d4…`. They are re-checked against the current 1078-line file, but the harness was edited during that review.
- The R2 and R3 facts come from the audit's isolated sandbox runs. I did not re-run them.
- Whether the SOURCES contract is frozen as stated at `corpus/SOURCES.md:3` is unverified; rule 2's text is taken from the lesson.

# Installs

None. Nothing was installed or updated by this seat.
