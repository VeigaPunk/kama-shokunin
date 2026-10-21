VERDICT: confirm - S064 row matches the live Python 3.14.8 docs: anchor, quote, tier/status, scope and used-by all check out; negative -N is parent-observed signal termination, provably not a subject-emitted verdict.

## Row under test
corpus/SOURCES.md:76 (S064) — docs | tier A | status mined | opened 2026-10-21 | recheck on-release |
scope "POSIX subprocess returncode signal convention in Python 3.14" |
anchor "CompletedProcess.returncode, negative -N paragraph; Python 3.14 documentation opened 2026-10-21" |
used-by corpus/knowledge/error-is-not-a-verdict.md, corpus/lessons/round-20.md

## Live page (opened 2026-10-21)
URL https://docs.python.org/3.14/library/subprocess.html served title
"subprocess — Subprocess management — Python 3.14.8 documentation"; row's "Python 3.14"
opened 2026-10-21 is consistent, observed revision 3.14.8 (recheck field on-release is the
correct trigger; no new revision seen today).

Located excerpt at anchor #subprocess.CompletedProcess.returncode:
> Exit status of the child process. Typically, an exit status of 0 indicates
> that it ran successfully.
> A negative value `-N` indicates that the child was terminated by signal `N` (POSIX only).

Corroboration on the same page:
- #subprocess.CalledProcessError.returncode: "If the process exited due to a signal, this
  will be the negative signal number."
- #subprocess.Popen.returncode repeats the same negative -N sentence, plus a shell=True
  caveat: the return code then reflects the shell's own exit status, which may map signals
  to codes such as 128+N. No conflict with the row; the row claims only the -N convention.

## Quote/meaning check (the falsification target)
- Quote matches: corpus/lessons/round-20.md:57 quotes the identical sentence with anchor
  §CompletedProcess.returncode.
- Meaning: -N is the parent's decode of the child's wait status (WIFSIGNALED), POSIX-only.
  It is an observation about how the child died, not a status the child chose to emit.
  On POSIX, a deliberate exit status is masked to 0–255, so -N is unreachable as an
  emitted verdict.
- Local reproduction (Python 3.14.8, same revision as the docs page, 2026-10-21):
  `sh -c 'kill -9 $$'` → parent sees returncode -9;
  `os._exit(-9)` → parent sees 247 (=-9 & 0xff), never a negative value.
  So a negative returncode cannot be a subject-emitted verdict; docs statement confirmed
  behaviorally. (Local reproduction is supporting evidence, not the pinned citation.)

## Tier/status/scope/used-by
- Tier A with scope bound to the returncode signal convention: scoped correctly — the
  docs qualify "(POSIX only)" exactly as the row's scope states.
- Status mined, opened 2026-10-21: consistent with corpus/lessons/round-20.md:63-64
  ("New rows S058–S064 ... 5 mined") and the round census line round-20.md:157
  ("rows57→64, A54→61/C3, mined46→51"), which counts S064 as tier-A mined.
- Used-by verified: corpus/knowledge/error-is-not-a-verdict.md:1 cites S064 and lines
  17-18 ("S064 describes negative POSIX returncodes as signal termination; that alone is
  not a subject verdict either") — an accurate restatement, not an overreach;
  corpus/lessons/round-20.md:16,57,157 cite S064 for the same bounded claim.
- Row teaches sentence "timeout or signal policy belongs to the caller": the returncode
  paragraph itself is silent on policy; the page supports it indirectly (run() kills the
  child on timeout expiry and re-raises TimeoutExpired; check/check_returncode() decide
  rejection). Read as a usage boundary, not a docs claim, it does not contradict the
  source. Flagging as interpretation, not a defect.

## Residual unknowns
- None blocking. Docs pages are unversioned in the row (revision recorded only as access
  date + "Python 3.14"); the recheck=on-release policy covers drift, and today's open
  shows 3.14.8 unchanged from the row's meaning.

SOURCES.md not edited. No installs performed. No scratch files created (reproduction used
only `python3 -c`).
