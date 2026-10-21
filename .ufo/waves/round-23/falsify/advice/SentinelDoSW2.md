Verdict: falsified.

Severity: High (availability/resource-exhaustion DoS against an audit run on attacker-controlled repository state or an attacker-selected `--errata` path). No attacker-controlled program execution was observed or attempted.

Axes: availability (FIFO hangs); memory containment (large history / SOURCES registry); result behavior (clean verdict vs explicit refusal); collateral (all hostile fixtures isolated under `/tmp`).

## Exploit path and evidence

All trials used fresh `/tmp` Git repositories, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, explicit author/committer identity, and local data only. Git was 2.56.0. The clone was verified at `245a37f69628c2c6bb29bbf17897d8fb5946c857`. Common command under test:

```text
/usr/bin/python /tmp/kama-r23w2/SentinelDoSW2/tools/report-landing-audit.py --lane-repo <fixture>/lane --fleet-repo <fixture>/fleet --rounds 10 --no-errata --json
```

For the timeout cases, the runner gave the command four seconds, then killed its process group; `timeout` below means no auditor exit status was produced before that watchdog killed it.

| Hostile input | Observed result |
|---|---|
| FIFO at `<fixture>/lane/.git/config` | Hung: watchdog at 4.005 s; no stdout/stderr. A Git process blocks before the audit can complete repository checks. |
| FIFO at `<fixture>/lane/.git/objects/info/alternates` | Hung: watchdog at 4.004 s; no stdout/stderr. |
| FIFO at `<fixture>/lane/.git/info/grafts` | Refused: exit 2, `could-not-evaluate: .../.git/info/grafts rewrites history` (0.037 s). |
| FIFO passed as `--report=10=<fifo>` | Refused: exit 2, `could-not-evaluate: .../hostile-report: not a regular file` (0.043 s). |
| FIFO passed as `--errata=<fifo>` with `--no-errata` omitted | Hung: watchdog at 4.005 s; no stdout/stderr. |
| Worktree `.mailmap` FIFO (control) | Verdict: exit 0, `status=clean`, `defects=0` (0.048 s). |
| Worktree `corpus/SOURCES.md` FIFO after committing a regular blob (control) | Verdict: exit 0, `status=clean`, `defects=0` (0.050 s); the committed blob is used. |
| 20,000 packed tag refs (`packed-refs` 1,320,105 bytes) | Verdict: exit 0, `status=clean`, `defects=0` (0.052 s; 384 MiB address-space limit). This size did not trouble the tested path; larger ref populations were not tested. |

The direct input-path contrast is in `tools/report-landing-audit.py:209-215` (`read_report` checks `stat`/regular-file mode) versus `:362-371` (`--errata` calls `Path.read_text` without a regular-file check). The Git wrapper at `:108-127` uses `subprocess.run(..., capture_output=True)` with no timeout or output bound. Repository checks at `:426-448` call Git before the later graft/pack checks, so a FIFO in Git metadata can block those earlier calls. The `.mailmap` control is consistent with the explicit `log.mailmap=false` isolation at `:93-96`.

### Memory boundary

- **Pathological SOURCES alternatives:** committed a 4,477,013-byte `corpus/SOURCES.md` with 12,000 valid, long, shared-prefix HTTPS source URLs; the report included a long near-match. With a 512 MiB `RLIMIT_AS`, the common command returned exit 2 after 2.214 s with `could-not-evaluate: internal: MemoryError: MemoryError()`. With a 1 GiB `RLIMIT_AS`, it returned exit 0 / `status=clean` in 3.084 s. Linux `RUSAGE_CHILDREN.ru_maxrss` immediately after that run was 716,476 KiB (about 700 MiB). The generated expression is from the unbounded alternatives in `:246-268`; this is high memory amplification from a few MiB of committed source data, not an exponential-regex claim.
- **Enormous log output:** two reachable commit subjects totaling 256 MiB were emitted by the full-history log path. At 384 MiB `RLIMIT_AS`, Git failed and the auditor returned exit 2 in 0.742 s with `could-not-evaluate: git log -z --format=%H%x00%an%x00%at%x00%s ...: rc=128 fatal: Out of memory, realloc failed`. At 1 GiB, it returned exit 0 / `status=clean` in 1.141 s; maximum child RSS observed was 803,804 KiB (about 785 MiB). A 64 MiB subject alone also returned clean under a 256 MiB address-space limit (0.385 s).

Relevant pinned-code paths: `tools/report-landing-audit.py:180-200` captures and splits the complete `git log` output; `:246-268` builds and compiles regex alternations from every accepted URL; `:108-127` buffers Git stdout without a size ceiling. Git's log documentation describes the unbounded traversal source: [https://git-scm.com/docs/git-log](https://git-scm.com/docs/git-log) — “List commits that are reachable by following the `parent` links from the given commit(s).” Python documents the explicit FIFO-prone read path: [https://docs.python.org/3/library/pathlib.html#pathlib.Path.read_text](https://docs.python.org/3/library/pathlib.html#pathlib.Path.read_text) — “Return the decoded contents of the pointed-to file as a string.”

## Impact and smallest remediation

A reviewer can be made to wait indefinitely on a local repository containing a FIFO at `.git/config` or `objects/info/alternates`; a caller can similarly block the explicit `--errata` read. Several-MiB committed metadata or large commit subjects can consume hundreds of MiB, with constrained runs refusing after allocation failure. The observed code paths fail the no-hang/resource-containment expectation even though bounded-memory failures returned exit 2 rather than a false clean verdict.

Smallest remediation: add a real per-Git-process deadline and ensure timed-out children are terminated; apply the existing regular-file gate to explicit errata; and set explicit input/output and URL-count/compiled-pattern ceilings before buffering or compiling attacker-sized data. No code remediation was made in this sentinel trial.

## Not verified

Did not test beyond 20,000 packed refs, larger SOURCES populations, unconstrained host OOM, every possible Git metadata FIFO/path, other Git versions, or attacker-configured program execution. The high RSS figures are from the bounded synthetic fixtures and current host/runtime only; no generic threshold is claimed.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/SentinelDoSW2.md` (this report).
- Synthetic repositories and their Git objects, refs, reports, FIFOs, and test blobs are under `/tmp/kama-r23w2/SentinelDoSW2-nw2h949p/` (scenario directories include `mailmap-fifo`, `grafts-fifo`, `config-fifo`, `alternates-fifo`, `report-fifo`, `errata-fifo`, `errata-fifo-real`, `sources-worktree-fifo`, `sources-worktree-fifo-real`, `huge-refs-real`, `sources-regex-real`, and `huge-log-real`). No tool was installed; no tracked file in the clone was edited.