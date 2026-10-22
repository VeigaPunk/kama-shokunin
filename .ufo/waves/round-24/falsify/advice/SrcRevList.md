# SrcRevList — r24 fresh source falsification: S102 git-rev-list, S104 fsck rejection

Seat: `KamaR23-2.SrcRevList-3` (leaf; no dispatch). Base/pinned revision:
`2e254a1763a9c08aa07fc53081287f506c447d84`. Read-only: no source row, production file,
fixture or test was edited or run; no candidate/grid/suite execution; no installs. Scratch clone:
`/fast/scratch/hyaku/kama-r24/falsify/SrcRevList` (`--no-hardlinks`, detached at the pinned commit).

This check says nothing about, and does not relabel, the withdrawn unknown-from-metadata
expectation; it audits only the two source rows named in the ticket.

## Verdict

| Item | Verdict | Basis |
|---|---|---|
| S102 row: anchor / version / access date / quote / teaches scope | **HOLDS** | Fresh page is the same 2.56.0 page; all three named options exist; quote is 16 words and verbatim; teaches stays inside traversal output. |
| S102 lessonGate quote coverage | **PARTIAL (minor, non-falsifying)** | The Gate quotes the `--missing=print` sentence. The row's `teaches` also asserts the `?` prefix and `allow-any` silent omission; both are verbatim in the same section (8 and 9 words) but are not quoted in the Gate bullet. |
| S102 knowledge use | **HOLDS** | Knowledge, SKILL and both tools use only the documented format; none claims an exit policy, remote absence or completeness theorem from this page. |
| S104 rejection of fsck green as local-availability proof | **HOLDS** | `mark_object` returns for a recognized promisor object before the `HAS_OBJ` check; consumers reject the availability inference only, not fsck's general validity. |
| S104 knowledge use | **HOLDS** | Wording is scoped to availability; no general fsck-invalidity claim. One inferred precondition is worth recording (see below). |
| Cosmetic | observed | S102 anchor cell literally omits " in " and spaces: `last updated2.56.0, opened2026-10-21`. The version and date are correct; first-commit immutable cell, so no in-place edit (KQ22). |

No source falsification found. The only partial is presentational quote coverage in the round
lesson, not a false registry claim.

## Snapshot and exact base

- Production `HEAD` = `2e254a17…`; `git status --porcelain` shows only the untracked
  `.ufo/waves/round-24/falsify/` tree. Judged files are byte-identical between the pinned commit
  and the working tree (sha256: SOURCES.md `f42c7552…`, lesson `a1950674…`, knowledge `d39b8cc1…`,
  SKILL.md `0509d532…`, auditor `ea51bc35…`, grid `b034e159…`).
- Host `git --version` = `2.56.0`, matching the page label.
- Fresh page `https://git-scm.com/docs/git-rev-list`: HTTP/2 200, 254770 B,
  sha256 `6eca09d9ef21dd4270ff2c73cac7ee26964aebc470f4dfc52705eb27749ce65f`,
  `Date: Wed, 21 Oct 2026 19:46:44 GMT`, `Last-Modified: Wed, 21 Oct 2026 15:55:45 GMT`.
  This is the same sha256 the build-phase opening recorded, so **no page drift** between the
  build open and this reopen.
- Version-pinned `https://git-scm.com/docs/git-rev-list/2.56.0`: HTTP 200, 254641 B,
  sha256 `2c9b7ed2177a70b69fa1c801f026ce2a2e6ece0a842f2055c98f44b7c405c7d4`; normalized text
  1799 lines vs 1799 lines for latest, unified diff 0 lines.
- `builtin/fsck.c` at tag `v2.56.0`: HTTP 200, sha256
  `d25f3b1a0b96f736bea3c77b79368501d87b1a2d23a0b1daf170b2c2e5a9ca35`, identical to the
  build-wave copy `build/out/SrcFsck/fsck-builtin.c`.
- `packfile.c` at tag `v2.56.0`: HTTP 200, sha256
  `021b1b9b25551070a3a1f986d1972ef93ef9695c3ff4f60eeb0a9a0798b94032`.

## Command → exit → token/finding

| Command (scratch cwd unless noted) | Exit | Token / finding |
|---|---|---|
| `git clone --no-hardlinks --quiet /home/vgpnk/Projects/shokunin/kama-shokunin kama-src` (cwd `/fast/scratch/hyaku/kama-r24/falsify/SrcRevList`) | 0 | clone created |
| `git checkout --quiet --detach 2e254a1763a9c08aa07fc53081287f506c447d84` (cwd `kama-src`); `git rev-parse HEAD` | 0 | `2e254a1763a9c08aa07fc53081287f506c447d84`; clean worktree |
| `curl -sS -D headers-revlist.txt -o git-rev-list.html https://git-scm.com/docs/git-rev-list` | 0 | `HTTP/2 200`; 254770 B; `6eca09d9…`; `Date: Wed, 21 Oct 2026 19:46:44 GMT` |
| `curl -sS -o revlist-2.56.0.html -w '%{http_code} %{size_download}' https://git-scm.com/docs/git-rev-list/2.56.0` | 0 | `200 254641`; `2c9b7ed2…`; normalized diff vs latest: 0 lines |
| `grep -n "git-rev-list last updated in 2.56.0" revlist-2.56.0.html` | 0 | line 1322: `git-rev-list last updated in 2.56.0` |
| `grep -n "missingmissing-action" revlist-2.56.0.html` | 0 | line 4654: `id="Documentation/git-rev-list.txt---missingmissing-action"`; `---objects` and `---no-object-names` ids also present |
| Python normalized quote check on pinned HTML | 0 | print sentence `True, 16 words`; allow-any omission `True, 9 words`; allow-any continuation `True, 15 words`; `?` prefix `True, 8 words` |
| `curl -sS -o fsck.c https://raw.githubusercontent.com/git/git/v2.56.0/builtin/fsck.c` | 0 | sha256 `d25f3b1a…`; equals build copy |
| `awk 'NR==143||NR==149||NR==151' fsck.c` | 0 | `143: if (is_promisor_object(options->repo, &obj->oid))`; `149: return 0;`; `151: if (!(obj->flags & HAS_OBJ)) {` |
| `curl -sS -o packfile.c https://raw.githubusercontent.com/git/git/v2.56.0/packfile.c` | 0 | sha256 `021b1b9b…`; `2061-2078 is_promisor_object`; seeding under `repo_has_promisor_remote(r)` |
| `git show 2e254a17:corpus/SOURCES.md`, extract S102/S104 cells | 0 | S102 anchor/teaches byte-identical from `ed1cc3a` through `2e254a17` (only used-by changed at `f1e755e`); S104 anchor/teaches unchanged |
| `git rev-parse HEAD` / `git status --porcelain` (production, read-only) | 0 | `2e254a17…`; only `?? .ufo/waves/round-24/falsify/` |
| `git --version` | 0 | `git version 2.56.0` |

## S102 — cell check against the fresh page

Row (pinned, exact):
`scope` = "object traversal output for an explicitly selected root; not an exit-policy or
completeness theorem"; `anchor` = "`--objects`, `--no-object-names`, `--missing=<missing-action>`;
last updated2.56.0, opened2026-10-21"; `teaches` = "`--missing=print` continues traversal while
printing encountered missing IDs prefixed with `?`; `allow-any` silently omits them. Exit2 and
required-evidence policy belong to the lane, not this manual."

| Axis | Observation | Result |
|---|---|---|
| anchor | All three options are in §Object Traversal at the pinned page; dt anchors `---objects`, `---no-object-names`, `---missingmissing-action` (line 4654). The row's `source` URL carries no fragment; it locates the section by option name, the same bare-URL convention as S089/S090/S091/S092/S093. | holds |
| version | Page label line 1322: `git-rev-list last updated in 2.56.0`; host git 2.56.0. Row literal `last updated2.56.0` states the same version, missing " in " and a space. | holds; cosmetic |
| access date | Row `opened2026-10-21`; fresh reopen 2026-10-21; Gate preamble says "Opened 2026-10-21 by this lane" (round-23 precedent uses the same shared-preamble date rather than per-row dates). | holds |
| ≤25-word quote | Lesson Gate quote: "The form --missing=print is like allow-any, but will also print a list of the missing objects." = 16 whitespace-delimited words, normalized-exact against the pinned page lines 4673–4674. | holds |
| teaches: print continues | Page: print "is like allow-any"; allow-any "will allow object traversal to continue if a missing object is encountered" (4663–4664). | holds (one-step page relation) |
| teaches: `?` prefix | Page 4674: "Object IDs are prefixed with a “?” character." True for non-`-z` output; `-z` replaces the marker with a `missing=yes` token (HTML 3828; the non-`-z` note is 4716). No cited consumer uses `-z`. | holds, with a scope limit |
| teaches: allow-any silent | Page 4664–4665: "Missing objects will silently be omitted from the results." | holds |
| teaches: not exit/completeness | The page states no numeric exit policy for the cited forms and no closure guarantee; the lane's exit2/evidence rule is marked as lane policy. | holds |
| lessonGate coverage | The Gate bullet quotes only the print sentence. The `?`-prefix clause and the allow-any-silent clause are taught in the row but not directly quoted in the Gate. Both are verbatim and short in the same section (8 and 9 words), and the build advice already recorded them. | **partial, minor** |
| knowledge use | `error-is-not-a-verdict.md:103–105` calls the `?` output "only … a bounded diagnostic, not a global completeness precondition or proof about a remote object universe"; `SKILL.md:843–846` calls the walks diagnostics "not an integrity theorem"; auditor `:63–66,658–675` and grid `:293–297` use exactly `rev-list --objects --missing=print --no-object-names` and parse `?`. Nothing attributes an exit code, remote absence or closure to S102. | holds |
| `--filter` coverage | The second diagnostic walk uses `--filter=blob:none`; the page documents it at `#Documentation/git-rev-list.txt---filterfilter-spec` (dt line 4577), but the S102 row does not name it. No consumer attributes the blob/tree distinction to S102 (the grid is cited as the evidence), so this is a coverage gap, not a mis-citation. | observation only |

Partial-correction candidate (optional, does not touch the immutable row): append to the lesson
Gate bullet the two already-verified sentences, each far below the 25-word limit —
`Object IDs are prefixed with a “?” character.` (8 words) and
`Missing objects will silently be omitted from the results.` (9 words). If L1 prefers strict
append-only lesson correction, put the same sentences in an appended correction paragraph naming
the existing bullet. No new source row is needed; the row's `teaches` is correct as filed.

## S104 — rejection scope judgment

Row (pinned, exact): `scope` = "rejection of fsck green as proof every promised object is locally
present"; `anchor` = "`mark_object`, lines143–149, v2.56.0; opened2026-10-21"; `teaches` =
"REJECTED: treating fsck green as a local-completeness oracle; mark_object returns for a promisor
object before HAS_OBJ checking. flip: demonstrate availability of the required evidence directly
rather than infer it from this fsck result."

| Axis | Observation | Result |
|---|---|---|
| anchor | Fresh tag-pinned file: line 143 is `if (is_promisor_object(options->repo, &obj->oid))`, line 149 is `return 0;`; the `HAS_OBJ` test is line 151. The anchor's inclusive range covers the check, comment and return. | holds |
| version | Raw URL is tag `v2.56.0`; fresh bytes sha256 `d25f3b1a…`, identical to the build-wave copy; host git 2.56.0. No digest is recorded in the row, consistent with S101's code-row convention. | holds |
| access date | Row `opened2026-10-21`; fresh fetch 2026-10-21; Gate preamble date. | holds |
| quote | Gate code quote `if (is_promisor_object(options->repo, &obj->oid))` … `return 0;` is verbatim at lines 143/149; token count is far below 25. | holds |
| mechanism | `mark_object` returns for a recognized promisor object before the `HAS_OBJ` branch (143–151); `check_reachable_object` likewise returns before printing `missing` for promisor objects (253–255); a reflog/ref target that is missing is tolerated when `is_promisor_object` (462–470, 534–542); `repo->fetch_if_missing = 0` (884–885); connectivity runs after the object scan (983). The object scan only sees objects the store holds, so a missing promised object need not produce a green-breaking error. | holds |
| scope: availability only | The rejection targets "fsck green ⇒ every promised object locally present". It does not claim fsck cannot detect corruption, broken links or missing non-promisor objects; the cited code still checks those. Consumers say "not local availability proof" / "cannot substitute for required-object availability", not "fsck is invalid". | holds |
| inferred precondition | `is_promisor_object` seeds its set only when `repo_has_promisor_remote(r)` (packfile.c 2061–2078). The skip therefore presupposes a configured promisor remote; a `.promisor` pack marker alone does not by itself establish the skip. The row's scope does not state this, but the rejection remains valid for the partial-clone/promisor-remote case that motivated it. | inference boundary |
| knowledge use | `error-is-not-a-verdict.md:105` and `SKILL.md:845–846` are scoped to availability and do not import general fsck validity. The knowledge sentence is a general-oracle claim ("cannot substitute"), not a claim that fsck green proves nothing about any individual non-promisor object. | holds |
| side checks | `promisor-grid.py` contains no fsck call, so omitting it from S104's `used-by` is correct. The lesson's "A green fsck is not proof every promised object is locally present" matches the code path. | holds |

Optional precision note if L1 wants the mechanism's precondition recorded:
"the skip applies to objects `is_promisor_object` recognizes; its set is seeded only when a
promisor remote is configured." This is a note only — no immutable-row rewrite, and no change to
the rejection's scope.

## Observed vs inferred

**Observed (commands above):** page identity/hash/label; pinned-page text identity; the four
sentences and their word counts; the three option anchors; the S102/S104 registry cells and their
immutable history; the fsck lines 143/149/151 and adjacent promisor tolerances; the packfile
seeding condition; consumer lines in the lesson, knowledge file, SKILL, auditor and grid; the
pinned commit equality of every judged file.

**Inferred (not executed):** (a) "print continues traversal" follows from the page's own
"is like allow-any" plus allow-any's continuation sentence; (b) a green fsck can coexist with a
missing promised object — the early returns and the scan/connectivity order show the path, but
fsck itself was not run; (c) the promisor-skip precondition follows from the `repo_has_promisor_remote`
guard in `is_promisor_object`; (d) the general-oracle reading of the knowledge sentence, as opposed
to a per-object claim about a reachable, non-promisor object.

**No claim:** remote repository completeness, remote abbreviation uniqueness, a numeric Git exit
policy from the rev-list page, or any change to the withdrawn original expectation.

## Files written

- `.ufo/waves/round-24/falsify/advice/SrcRevList.md` (this report)
- `.ufo/waves/round-24/falsify/out/SrcRevList/evidence.txt` (command/hash/line log)

Both paths are relative to `/home/vgpnk/Projects/shokunin/kama-shokunin`. No production file was
touched. The only production-tree write is inside the untracked falsify artifact directory.

## Unverified / not run

- No execution of `git fsck`, no promisor-grid or report-landing-audit run, no candidate run, no
  full suite, no fixture or blobless clone opened (so the peer-reported blobless lazy-fetch hazard
  cannot contaminate this check). History/commit reads ran in the fresh scratch clone at the pinned
  commit; two read-only `git rev-parse`/`git status` checks ran in the production tree to confirm the
  exact base, and the pinned-vs-worktree hashes were computed with read-only `git show`/`sha256sum`.
- The dynamic proposition "real partial clone with a missing promised object still exits 0 fsck" is
  code-inferred, not observed.
- Source-census/append-only verification and the final 105-row count remain L1-owned; this report
  does not claim them.
- No network beyond four plain HTTPS GETs (latest page, pinned 2.56.0 page, tag-pinned `fsck.c`, tag-pinned `packfile.c`) plus two HEAD checks.
