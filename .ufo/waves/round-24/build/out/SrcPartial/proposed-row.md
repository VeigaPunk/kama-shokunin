Candidate SOURCES representation (NOT applied; registry edit belongs to L1).

Registry state observed 2026-10-21 while this lane ran (working tree, uncommitted):
- `corpus/SOURCES.md` already gained S102 (git-rev-list), S103 (partial-clone
  promisor-pack representation), and S104 (fsck promisor exception) from sibling lanes.
  `git diff --stat` shows `corpus/SOURCES.md | 3 +++`, so these rows are not in base
  0df800e896f6bce285a81e794ad4ae1d1e6c3a71.
- The earlier draft in this lane proposed S102; **do not apply it**. S102 is taken, and
  S103 already covers the marker-representation half of this claim.

Preferred (no fourth row for one page/section): amend S103 before it is committed.
Because S103 is absent from base 0df800e, it is an "added row" under
tools/sources-append-only.py (`a row present only in --to is allowed`, docstring line 19),
so its cells are still editable without violating the append-only guard. Replace S103 with:

| S103 | Partial-clone promisor-pack representation — https://git-scm.com/docs/partial-clone#_handling_missing_objects | docs | A | promisor marker as provenance, not a missing-object inventory; not completeness of locally required audit evidence | §Handling Missing Objects: `.promisor` "arbitrary contents" (adoc 116-118), promisor-object definition (120-123), "no need ... list of missing objects" (128-129), footnote [a] (336-337), at git.git tag v2.56.0; page "last updated in 2.56.0", opened 2026-10-21 | A promisor pack has a .promisor file alongside its .pack/.idx, with arbitrary contents; the client keeps no missing-object list and a promisor object may be locally present. Marking records promised-object provenance; whether required evidence is locally available is separate, and a local miss is unknown, not absence. | mined | 2026-10-21 | on-release | corpus/lessons/round-24.md, tools/report-landing-audit.py |

Fallback if S103 is already committed/frozen when this is read: append S105 after S104
(inside the Registry table, before `## Paths`; an EOF append is a parse error):

| S105 | partial-clone design note, promisor metadata versus promises — https://git-scm.com/docs/partial-clone#_handling_missing_objects | docs | A | promisor metadata is promise/provenance, not a local missing-object inventory; excludes lazy-fetch behavior (S099) and completeness verdicts (S103) | §Handling Missing Objects: "arbitrary contents" (adoc 116-118), promisor-object definition (120-123), "no need ... list of missing objects" (128-129), footnote [a] (336-337), at git.git tag v2.56.0; page "last updated in 2.56.0", opened 2026-10-21 | REOPENED page, not a new source; complements S099/S103, supersedes neither. Marker contents are arbitrary and no missing-object list is kept; a promisor object is one the remote promised, whether present in a promisor packfile or referenced by one, so metadata does not say which required objects are absent. A local miss stays unknown. | mined | 2026-10-21 | on-release | corpus/lessons/round-24.md, tools/report-landing-audit.py |

Representation notes:
- Primary quote (19 words): "This means that there is no need for the client to explicitly
  maintain an expensive-to-modify list of missing objects."
- S103 is a sibling lane's row. L1 owns any change and should confirm the sibling's claim is
  preserved; the replacement keeps its `.promisor` alongside `.pack`/`.idx` sentence and its
  "locally available evidence is separate" conclusion.
- Neither variant claims upstream changed or withdraws S092/S099's sentence; registry
  supersession language is lane-local (convention at `corpus/SOURCES.md:141`).
- S099 remains the authority for "no check as to whether the missing object is actually a
  promisor object is performed"; this row does not restate that sentence.
