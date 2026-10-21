# SrcPySubprocess — draft SOURCES rows (calibration: signal-killed children are errors, not verdicts)

All three rows below were machine-validated against
`scripts/sources-census.sh validate --today 2026-10-21` on a scratch clone of
kama-shokunin @ 37bd4c5bd456a2f8a54d3312c28495c321715856 with the row appended
after S057. Executed results are in advice/SrcPySubprocess.md.

## Draft A — RECOMMENDED (pinned cpython blob; validated exit 0, no new code)

| S058 | CPython `Doc/library/subprocess.rst` @ v3.14.8 (tag commit 8e6e75d9102e39bed2a2b279203a396741180f12) — https://github.com/python/cpython/blob/v3.14.8/Doc/library/subprocess.rst | docs | A | telling a signal-terminated child from one that chose its exit status, for kama's Python 3.14 instruments on POSIX; the termination cause only, not the lane's error-versus-verdict rule, not Windows | `Popen.returncode` lines 949-964 (negative `-N` at 958-959, `shell=True` note at 961-964); `CalledProcessError.returncode` 240-243; raw sha256 05cd782c5181481ad961788dd678b99c903eb3ff53e0ebab3095c38b48c74dfd (61603 B), byte-identical at 3.14 head e152a82bf3bd on 2026-10-21; rendered as docs.python.org/3.14/library/subprocess.html "Python 3.14.8 documentation"; the `shell=True` note is absent at v3.14.0 | "A negative value -N indicates that the child was terminated by signal N (POSIX only)." (15 words, 958-959); a shell "may map signals to codes such as 128+N" (8 words, 962-963). A negative code means the subject chose no exit status, so kama records could-not-evaluate, never reject or accept (kama's rule, not the doc's); a shell or a `sys.exit(p.returncode)` re-exit hides the sign (137, 143, 247 observed). | mined | 2026-10-21 | on-release | tools/error-verdict-census.py |

Notes: id S058 is the next free slot at the round-start tip (L1 renumbers if a
sibling takes it). `url_of` takes the FIRST http(s) URL of the source cell, so
the cpython blob (not the docs page) is the census key: no W04 vs S044. E11
fires until `tools/error-verdict-census.py` exists — commit the row with that
tool (validated with a placeholder file; otherwise clean).

## Draft B — alternative (docs page URL; validated exit 0 but adds one W04)

| S058 | Python `subprocess` — `Popen.returncode` (Python 3.14) — https://docs.python.org/3.14/library/subprocess.html#subprocess.Popen.returncode | docs | A | telling a signal-terminated child from one that chose its exit status, for kama's Python 3.14 instruments on POSIX; the termination cause only, not the lane's error-versus-verdict rule, not Windows | §`Popen.returncode` (negative `-N` sentence; `shell=True` 128+N note, new in 3.14.x, absent at v3.14.0); §`CompletedProcess.returncode`; page titled "subprocess — Subprocess management — Python 3.14.8 documentation", "Last updated on Oct 21, 2026 (06:47 UTC)", page sha256 68c0a3cb9253c697ab7a27f6d653c2d9eda061adfa9e1f8a702d872ed3603634 (207127 B, fetched 2026-10-21); pinned source Doc/library/subprocess.rst @ v3.14.8 sha256 05cd782c5181481ad961788dd678b99c903eb3ff53e0ebab3095c38b48c74dfd | "A negative value -N indicates that the child was terminated by signal N (POSIX only)." (15 words); a shell "may map signals to codes such as 128+N" (8 words). A negative code means the subject chose no exit status, so kama records could-not-evaluate, never reject or accept (kama's rule, not the doc's); a shell or a `sys.exit(p.returncode)` re-exit hides the sign (137, 143, 247 observed). | mined | 2026-10-21 | on-release | tools/error-verdict-census.py |

Observed: `W04	S058	duplicate url docs.python.org/3.14/library/subprocess.html
across scopes` (url_of strips the fragment, colliding with S044; warning only —
validate exit stayed 0). Distinct scope avoids E04. A is preferred.

## Draft C — optional lead (bash's 128+N relabeling; queued, tier A)

| S059 | GNU Bash Reference Manual, §Exit Status — node "Exit Status" (host copy `/usr/share/man/man1/bash.1.gz`, bash 5.3.20-1, man-pages 6.19-1) | docs | A | how the shell layer bash adds relabels a child's signal death as a positive exit status behind Python's negative-returncode convention; not other shells' wording, not Python itself | EXIT STATUS lines 5909-5925 of the decompressed bash.1 (fatal-signal sentence at 5924-5925); SHELL GRAMMAR §Pipelines lines 583-585 (simple-command 128+n rule); gz sha256 b68beb3e385f7d8aead26bf7887c12f93ca769dcd528fd7282d70938b09bdffe; online copy https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html timed out (25 s, connection) on 2026-10-21 — reopen before use | "When a command terminates on a fatal signal N, bash uses the value of 128+N as the exit status." (18 words, §Exit Status). Behind bash, a killed child arrives as 137/143 — positive, sign-indistinguishable from a chosen exit code (host cells observed). | queued | 2026-10-21 | on-release | — |

## Suggested lesson-style line (SOURCES.md contract: URL, access date, quote)

- **2026-10-21 — subprocess returncode signal semantics.** URL:
  https://github.com/python/cpython/blob/v3.14.8/Doc/library/subprocess.rst
  (rendered https://docs.python.org/3.14/library/subprocess.html#subprocess.Popen.returncode,
  accessed 2026-10-21). Quote: "A negative value ``-N`` indicates that the child
  was terminated by signal ``N`` (POSIX only)." — `Popen.returncode`, lines
  958-959 of Doc/library/subprocess.rst at tag v3.14.8 (page: Python 3.14.8
  documentation, "Last updated on Oct 21, 2026 (06:47 UTC)").
