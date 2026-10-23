# ScoutHeldRules

C1's rule is not already held by the four named instruments, and no SKILL.md instrument-registry section describes it.

Overlap means: checks a `SCORECARD.md` or `SHONEN.md` statement at the line's writing revision W (`git blame --line-porcelain` of that line) for class P, H, N, C, T, or Q, as `count-c1.py` defines them. **full** = that check; **partial** = same class on those files but not at W; **none** = not that check. None of the four calls `git blame`.

| tool | inputs | rule | overlap |
|---|---|---|---|
| `tools/citation-provenance.py` | registry `registry/required-citations.json`; default docs include `SCORECARD.md` and `LOG.md`, not `SHONEN.md`; lane git | exact `cite(rev, path, sha256=64hex)` present, blob digest equals it, rev ancestor of `origin/master` unless `--allow-off-ref` | **none** |
| `tools/prereg-time-check.py` | caller `--repo --path --rev`; `--max-future` 86400 or `--strict` | ISO times in `rev:path` vs committer time of `git log -1` on that path (one file version, not each line) | **none** |
| `tools/report-landing-audit.py` | fleet `.ufo/reports/round-N/kama.md`, optional draft, errata ledger, lane and fleet git | unresolved/ambiguous/omitted landed citations; not SCORECARD/SHONEN | **none** |
| `tools/sources-append-only.py` | `--from --to`, default `corpus/SOURCES.md` | registry rows append-only; immutable cells not edited | **none** |

Closest cousins, still not partial: citation-provenance hashes a blob at the revision named inside `cite()`, and checks that revision against `origin/master`, which is not H or C at W. prereg-time-check flags a future timestamp against the file's last-touch committer time; class T uses the line's blame commit, a different separator set (`T~` vs a bare space), and no 86400s horizon. It is also absent from SKILL.md (`prereg-time` does not occur). `SKILL.md` has no `SHONEN`, no `blame`, and no `writing revision`. The round-17 SOURCES row still says 14 selftest cases; the round-18 row says 42.

Self-tests, this run, all exit 0: citation-provenance `selftest: ok (24 cases)`; prereg-time-check `SELFTEST PASS` (scratch `/fast/scratch/hyaku/kama-r29/w1/ScoutHeldRules/ptc-selftest-4fn8se9d`); report-landing-audit `selftest cases=79 failed=0`; sources-append-only `42/42 selftest cases passed`. No install.

Detail table: `.ufo/waves/round-29/w1/out/ScoutHeldRules/held-rules.md`. Limit: other tools than these four were not opened.
