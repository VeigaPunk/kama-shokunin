# Draft SOURCES row — S066 gitrevisions(7) (KamaR21.SrcGitRevisions-6, 2026-10-21)

One new registry row for `corpus/SOURCES.md` (L1 integrates; registry ends at S065,
no existing gitrevisions row — only round-12 Search-log mentions). Same row text is
in `.ufo/waves/round-21/build/advice/SrcGitRevisions.md`.

| S066 | Git gitrevisions manual — https://git-scm.com/docs/gitrevisions (man source Documentation/revisions.adoc @ git.git v2.56.0) | docs | A | Git revision-syntax semantics the report-landing audit relies on: abbreviated object names and `<rev>^{<type>}` peeling; not report policy, not endpoint truth | §SPECIFYING REVISIONS, entry `<sha1>` line 16 and entry `<rev>^{<type>}` lines 175-176; revisions.adoc sha256 b23a9eb17d9b193adccee6b79cb1c1fef450703dae925a33b8a1c6f6639d82ff at v2.56.0 (tag 24785443, peeled commit a0189536), opened 2026-10-21; local man page gitrevisions.7.gz (git 2.56.0, sha256 29d3cb61) agrees | "a leading substring that is unique within the repository." (9 words); "dereference the object at '<rev>' recursively until an object of type '<type>' is found" (14 words) — a 7..40-hex token names a commit only as a unique prefix of an existing object that peels to one, the mechanical basis of unresolved-full-hash and landed-unresolved | queued | 2026-10-21 | on-release | — |

Byte pins behind the anchor (executed 2026-10-21):
- git.git tag v2.56.0: tag object 2478544319491bbd2a42cc57a83e3d2f4730a280,
  peeled commit a018953688f1b10bddf91bff8747068f5f4746a4 (`git ls-remote` exit 0).
- Documentation/revisions.adoc @ v2.56.0: sha256 b23a9eb17d9b193adccee6b79cb1c1fef450703dae925a33b8a1c6f6639d82ff,
  424 lines; quote lines 16 and 175-176 (`git show HEAD:...` exit 0, grep -n -F).
- Host man page /usr/share/man/man7/gitrevisions.7.gz (git 2.56.0):
  sha256 29d3cb6149a407830c93491dbe673acf824b3887071fbe028ff589263ce5f972;
  same sentences at dump lines 29 and 158-160.
- Web manual: "gitrevisions last updated in 2.56.0" (2026-09-28), HTTP 200.

Audit tie (supports C1): tools/report-landing-audit.py `is_object()` runs
`git cat-file -e <token>^{commit}` (lines 69-76); docstring defines
landed-unresolved at lines 13-14; `rev-parse --verify <branch>^{commit}` at 203-204.
