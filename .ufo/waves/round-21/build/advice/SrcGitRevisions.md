VERDICT: confirm - gitrevisions(7) opened 2026-10-21; both target sentences verified verbatim in three independent renders and byte-pinned; draft row S066 supports C1's unresolved-token semantics.

## Source identity (all opened 2026-10-21)
- Online: https://git-scm.com/docs/gitrevisions — fetched HTTP 200; page states "gitrevisions last updated in 2.56.0" (2026-09-28), latest entry in its version table.
- Local: `/usr/share/man/man7/gitrevisions.7.gz` (`man -w 7 gitrevisions`), host git 2.56.0 (`git --version`), sha256 29d3cb6149a407830c93491dbe673acf824b3887071fbe028ff589263ce5f972; text dump at /tmp scratch carried both sentences (dump lines 29 and 158-160).
- Pinned body: `Documentation/revisions.adoc` in git.git at tag `v2.56.0` — tag object 2478544319491bbd2a42cc57a83e3d2f4730a280, peeled commit a018953688f1b10bddf91bff8747068f5f4746a4 (git ls-remote, exit 0); shallow sparse clone exit 0; `git show HEAD:Documentation/revisions.adoc` exit 0; sha256 b23a9eb17d9b193adccee6b79cb1c1fef450703dae925a33b8a1c6f6639d82ff, 424 lines. The man page shell `Documentation/gitrevisions.adoc` is `include::revisions.adoc[]` — observed in the 36-line shell file.

## Verbatim quotes (located, ≤25 words each)
1. §SPECIFYING REVISIONS, entry `<sha1>`, revisions.adoc line 16: "a leading substring that is unique within the repository." (9 words). Same entry lines 17-20 gloss it: "if there is no other object in your repository whose object name starts with dae86e" (16 words).
2. Same section, entry `<rev>^{<type>}`, revisions.adoc lines 175-176: "dereference the object at '<rev>' recursively until an object of type '<type>' is found" (14 words; the quoting around `<rev>`/`<type>` is stripped in the rendered man page and web page, which carry the identical sentence).

## Not already a row
`grep gitrevisions corpus/SOURCES.md` matches only Search-log lines 91-92 (round-12: "with gitrevisions consulted by the scout") — consulted 2026-10-20, never registered. Next free id is S066 (registry ends at S065).

## Which statement it supports
Supports C1 (calibration, report-landing-audit); refutes nothing; C2 untouched. Observed in `tools/report-landing-audit.py` (read lines 54-93; grep hits at 11-20, 72-76, 202-204): docstring lines 11-20 define `unresolved-full-hash` (40-hex token that is no git object) and `landed-unresolved` (7..40-hex token that "does not resolve to a commit"); `is_object()` lines 69-76 executes `git cat-file -e <token>^{commit}`; `main()` lines 203-204 execute `rev-parse --verify <branch>^{commit}` / `HEAD^{commit}`. gitrevisions(7) supplies exactly the two halves of that resolution: a hex token names an object only as a unique leading substring of an existing object name, and `^{commit}` peeling is what lets a tag object's hash resolve to a commit (`<rev>^0` is "a short-hand for `<rev>^{commit}`", line 178-179).

## Draft row (paste into the Registry; L1 owns corpus/SOURCES.md)
| S066 | Git gitrevisions manual — https://git-scm.com/docs/gitrevisions (man source Documentation/revisions.adoc @ git.git v2.56.0) | docs | A | Git revision-syntax semantics the report-landing audit relies on: abbreviated object names and `<rev>^{<type>}` peeling; not report policy, not endpoint truth | §SPECIFYING REVISIONS, entry `<sha1>` line 16 and entry `<rev>^{<type>}` lines 175-176; revisions.adoc sha256 b23a9eb17d9b193adccee6b79cb1c1fef450703dae925a33b8a1c6f6639d82ff at v2.56.0 (tag 24785443, peeled commit a0189536), opened 2026-10-21; local man page gitrevisions.7.gz (git 2.56.0, sha256 29d3cb61) agrees | "a leading substring that is unique within the repository." (9 words); "dereference the object at '<rev>' recursively until an object of type '<type>' is found" (14 words) — a 7..40-hex token names a commit only as a unique prefix of an existing object that peels to one, the mechanical basis of unresolved-full-hash and landed-unresolved | queued | 2026-10-21 | on-release | — |
- Proposed status `queued` (opened this round, not yet cited). Flip to `mined` when the round-21 lesson/knowledge entry for the audit cites it; the flip condition is the `used-by` cell gaining a real path.

## Suggested Search-log line for round 21
- **2026-10-21 — landing-audit revision-syntax ground.** Question: which authoritative text defines when a hex token names a commit and how `^{commit}` peeling works? Where: git-scm.com gitrevisions manual, the host man page, and git.git v2.56.0 `Documentation/revisions.adoc`. Identified 3 renders of one source, screened 3, included 1 new registry row (S066), excluded 0. Stop: both sentences located and byte-pinned; no broader Git claim sought.

## Commands executed (exit codes)
- `man --nh --nj 7 gitrevisions` dump → exit 0 (354 lines); `man -w 7 gitrevisions` → path above; `git --version` → git version 2.56.0.
- read https://git-scm.com/docs/gitrevisions → HTTP 200, version table 2.56.0 (2026-09-28) latest.
- read raw.githubusercontent.com/git/git/master/Documentation/revisions.txt → HTTP 404; `curl -sf .../refs/tags/v2.56.0/Documentation/revisions.txt` → exit 22; `curl -sf api.github.com .../contents/Documentation/revisions.txt?ref=v2.56.0` → exit 22. Cause: the doc split into `.adoc` (observed in the tree), not a network outage — the `.adoc` body fetched cleanly via git protocol.
- `git ls-remote` → exit 0 (ids above); `git clone --depth 1 --branch v2.56.0 --filter=blob:none --sparse https://github.com/git/git.git` → exit 0; `git show HEAD:Documentation/{gitrevisions,revisions}.adoc` → exit 0 (second one is the byte pin).
- `grep -n -F` located quotes at revisions.adoc lines 16 and 175-176; sha256sum values above are from executed runs.
- Read-only lane access: grep/read of `tools/report-landing-audit.py` and `corpus/SOURCES.md`; no lane file modified.

## Honesty notes
- No tool installs (tooling directive: nothing to record).
- The row text and the C1 mapping are this scout's proposal; the L1 integrates. [INFERENCE] none beyond that delegation; every quote and exit above was executed.
- Scratch /tmp/kama-r21-SrcGitRevisions (clone + dumps) deleted after writing this report.
