# A register row's introduction is the commit blame attributes to that row

source: S571 — https://git-scm.com/docs/git-blame — DESCRIPTION lines 2146-2147 — opened 2026-11-04
verified-at: 2026-11-04 — the quote is at the line named in the live page (sha256 `cc28e3b8…e187`, 82763 bytes, 2847 lines); the behaviour is exercised by `tools/round81-append-debt.py --selftest` arms `row-intro-later`, `row-intro-earlier`, `row-intro-unbound` and `late-path-bound`.
recheck: `python3 tools/round81-append-debt.py --repo . --round 83` → the `late` bucket is an EVENT count (`late = len((late_covered - frozen_keys) & graded_keys)`), so 20 new rows over 8 events raise it by 8; re-run `python3 -c "import subprocess;print(subprocess.run(['git','-C','.','blame','--line-porcelain','HEAD','--','registry/append-only-late.tsv'],capture_output=True,text=True).stdout.count(chr(10)))"` for the line count.

## The rule

The late-acceptance rule accepts an undeclared deletion event when "a committed late-register row's
introducing commit is a strict descendant of the event commit". `git blame` answers exactly that
question for a line: "Annotates each line in the given file with information from the revision which
last modified the line." So `git blame --line-porcelain <rev> -- <register>` maps a register line to the
commit that last touched it, and a row appended this round is attributed to this round's commit.

## Why the file's introduction is the wrong answer

`git log --diff-filter=A <rev> -- <register>` returns the commit that first created the file — one
commit for the whole register. A row appended after that commit then appears to predate the event it
accepts, so a register can never accept an event created after it first existed. That is the defect
round 82 repaired (`register-introduction-conflated`) and round 83 extended to the caller-supplied path:
`--late FILE` must resolve the same per-row attribution for the path it was handed, or refuse the path
with exit 2. A row whose line cannot be blamed is `unbound-register`, never accepted.

## What it does not say

Blame says nothing about whether the acceptance is honest — a row can be appended by any commit. The
rule's teeth are elsewhere: exact cell equality against the frozen audit, the accepting round strictly
greater than the deletion round, and the note's deletion round bound to the event commit's own subject.
Blame only answers "which commit introduced this row", and the answer is one commit per row.
