# SrcMarker — S103/S104 source-marker re-open (round 24)

Seat: `KamaR23-2.SrcMarker` (leaf; no delegation, no candidate runs, no edits).
Pinned base: `2e254a1763a9c08aa07fc53081287f506c447d84` (commit time
`2026-10-21 16:45:12 -0300`; production HEAD read-only and my detached
scratch clone both report this exact hash). Scratch:
`/fast/scratch/hyaku/kama-r24/falsify/SrcMarker/` with `TMPDIR` set there.
Re-open time: `2026-10-21T19:46:50Z`.

## Verdict

**HOLDS for S103 and S104. No claim is falsified.** The only finding is the
non-blocking S103 quote-fidelity note below.

Axes checked: URL/anchor, version label, access date, quote fidelity/length,
teaches scope against the round-24 Gate and the knowledge use, and — for
S104 — whether the rejection is limited to local availability rather than
general fsck validity.

One **non-blocking** S103 quote-fidelity note is recorded below: the Gate
quote is a verbatim prefix but is truncated without an ellipsis; the full
sentence is 23 words and would still fit the ≤25-word rule. It does not
invert or overstate the page and no row rewrite is required for admission.

## S103 — partial-clone `§Handling Missing Objects`

### Re-open and anchor

- `curl -sS -L --max-time 60 -o partial-clone.html -w '%{http_code} %{url_effective} %{size_download}\n' 'https://git-scm.com/docs/partial-clone'`
  → exit 0, `200 https://git-scm.com/docs/partial-clone 51719`.
- The fragment URL `https://git-scm.com/docs/partial-clone#_handling_missing_objects`
  → exit 0, `200`, 51719 bytes, **byte-identical** to the bare URL
  (`sha256 8a6493225f76dba8e5b1eb75234f7370e057ee87c11e07a2681dbf522b16c9ad`).
  Fragments are client-side; the anchor is real:
  `grep -c 'id="_handling_missing_objects"'` → `1`.
- The quoted paragraph is inside the **first `<li>`** of that section: the
  rendered `<h2 id="_handling_missing_objects">Handling Missing Objects</h2>`
  is followed by `<ul><li><p>An object may be missing …</p><div class="paragraph"><p>These promisor packfiles …</p></div></li>`.
  The tagged AsciiDoc source confirms the same list structure at
  `Documentation/technical/partial-clone.adoc` v2.56.0 lines 108–118: the
  heading at 108, first bullet at 111, continuation marker `+` at 115, and
  the quoted sentence at 116–118 inside that first bullet.
- Registry anchor cell `§Handling Missing Objects, first bullet` is therefore
  **accurate at bullet granularity**. Precision note: the quote is the first
  bullet's **second paragraph**, not its opening sentence; this is not a
  defect, only a reading of "first bullet".

### Version and access date

- Page footer: `<span class="light d-flex">partial-clone last updated in 2.56.0</span>`
  (saved page line 1300). Registry row and Gate both say `last updated2.56.0`.
  **Match.**
- Versioned page `https://git-scm.com/docs/partial-clone/2.56.0` → exit 0,
  `200`, 51590 bytes, `sha256 d5c98adfca1e50b6addc241c7cf15bc2fc3ff259f01f1a374c229afc875d7be1`;
  contains the same quote and footer. The row cites the unversioned URL, but
  the version label itself is correct and the declared recheck is
  `on-release`, so this is not drift-blind.
- The tag-pinned design source
  `https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/technical/partial-clone.adoc`
  → exit 0, `200`, 14948 bytes,
  `sha256 9512d7ee0b79680f61d3f98c9eae42cc1dbaeef63535c5502cff66d7bce19264`,
  and carries the same sentence at lines 116–118. This independently ties the
  rendered page's claim to tag v2.56.0.
- Registry `opened2026-10-21`, Gate `Opened 2026-10-21`; my fresh read is
  `2026-10-21T19:46:50Z`. **Same UTC date, match.** The row's `opened` column
  is also `2026-10-21`.

### Quote length and fidelity

Gate quote (round-24 lesson, lines 24–25):

> “These promisor packfiles consist of a \"<name>.promisor\" file with arbitrary contents”

- Word count: **11** (`These promisor packfiles consist of a "<name>.promisor"
  file with arbitrary contents`) — within ≤25.
- After whitespace normalization, the quoted span is **byte-exact** in the
  rendered page and in the v2.56.0 AsciiDoc. The page continues:
  `(like the "<name>.keep" files), in addition to their "<name>.pack" and "<name>.idx" files.`
- **Note:** the Gate closes the quotation after `contents` without an ellipsis.
  The omitted continuation does not reverse or weaken the quoted proposition,
  and the registry `teaches` cell restores the `.pack`/`.idx` part. The full
  sentence is **23 words**, still ≤25, so the minimal optional correction is
  simply to quote the full sentence (or add `…` after `contents`). This is a
  fidelity nit, not a false claim.

### Teaches scope vs Gate and knowledge use

Registry row (`corpus/SOURCES.md:115`), scope:
`paired promisor-pack marker representation, not completeness of locally required audit evidence`.
Teaches: promisor pack has `.promisor` beside `.pack`/`.idx`; marking records
promised-object provenance; local availability is a separate question tested by
the lane's paired complete/incomplete fixtures.

Page facts used:
- promisor packfiles consist of `<name>.promisor` (arbitrary contents) in
  addition to `<name>.pack` and `<name>.idx`;
- the local repository specially indicates filtered packfiles obtained from
  promisor remotes as promisor packfiles;
- a missing object may arise from partial clone/fetch **or** corruption, and
  the marker is what differentiates the cases;
- a promisor object is one the repository knows promisor remotes promised,
  including objects referenced by another promisor object.

This supports the positive/negative content and, crucially, does **not** say
that the marker proves any particular needed object is absent or present.
The row's scope explicitly excludes completeness of required audit evidence.
The Gate's consequence sentence (“its presence does not prove every object
needed by an audit is absent”) is **already labelled a lane inference tested by
complete-state twins, not a quote**; the knowledge file uses S103 only
negatively (“Promisor packaging alone answers nothing (S103)”), and SKILL.md
line 845 uses “S103 packaging provenance”. No consumer converts S103 into a
positive availability claim.

`used-by` check: `corpus/lessons/round-24.md`, `corpus/knowledge/error-is-not-a-verdict.md`
and `SKILL.md` literally name S103. `tests/report-audit/promisor-grid.py` does
not contain the literal string `S103`, but it implements the distinction
(`promisor_facts`, lines 250–271, plus the paired complete/incomplete cases);
in the two audit/grid code consumers checked for literal S101/S102/S103 text
(`promisor-grid.py`, `tools/report-landing-audit.py`), no such row citation
appears. Used-by is a semantic consumer cell here, not a textual citation
requirement; **no mismatch**. (Other tools do cite source IDs where their logic
is pinned to one, e.g. `tools/kama-llamacpp-live.py` cites S036; that is not a
rule that every used-by entry must quote the ID.)

**S103 token: PASS** (with the non-blocking truncation note above).

## S104 — `fsck.c` promisor exception

### Marker and lines

- `https://raw.githubusercontent.com/git/git/v2.56.0/builtin/fsck.c`
  → exit 0, `200`, 26980 bytes,
  `sha256 d25f3b1a0b96f736bea3c77b79368501d87b1a2d23a0b1daf170b2c2e5a9ca35`.
- Registry/Gate cite `mark_object`, lines 143–149. Exact read:

```
143  if (is_promisor_object(options->repo, &obj->oid))
144          /*
145           * Further recursion does not need to be performed on this
146           * object since it is a promisor object (so it does not need to
147           * be added to "pending").
148           */
149          return 0;
...
151  if (!(obj->flags & HAS_OBJ)) {
152          if (parent && !odb_has_object(options->repo->objects, &obj->oid,
153                                        ODB_HAS_OBJECT_RECHECK_PACKED)) {
154                  ... "broken link" ...
160                  errors_found |= ERROR_REACHABLE;
161          }
162          return 1;
163  }
```

The early return at 143–149 is **before** the `HAS_OBJ` check at 151–163, so a
promisor object is neither presence-checked nor queued for recursion. Registry
teaches “mark_object returns for a promisor object before HAS_OBJ checking” is
exact.

### Why a green fsck is not local-availability proof

The exemption is not a single branch; it is repeated on every availability
path, and fsck deliberately disables lazy fetch:

- `cmd_fsck` lines 884–885: `/* fsck knows how to handle missing promisor objects */`
  and `repo->fetch_if_missing = 0;`.
- `check_reachable_object` lines 253–255: a missing promisor object returns
  before the `missing %s %s` error at 258–261.
- `snapshot_ref` lines 535–542: when `parse_object` fails and the ref target is
  a promisor object, the ref is counted valid (`default_refs++`) and no
  `invalid sha1 pointer` error is emitted.
- `fsck_handle_reflog_oid` lines 469–473: an invalid reflog entry is skipped
  for a promisor object instead of raising `ERROR_REACHABLE`.

The support definition closes the loop: `packfile.c` v2.56.0
(`sha256 021b1b9b25551070a3a1f986d1972ef93ef9695c3ff4f60eeb0a9a0798b94032`)
`add_promisor_object` (lines 2006–2058) inserts the object itself and then the
OIDs it references — tree entries at 2043–2044, commit tree and parents at
2047–2053, tag target at 2054–2056 — **without an existence check on those
referenced OIDs**. `is_promisor_object` (2061–2078) then answers by membership
in that set (built over `ODB_FOR_EACH_OBJECT_PROMISOR_ONLY`, 2073–2074).
Therefore promisor membership can be true for an object that is not locally
present, which is exactly the case `mark_object` skips.

The walker hands such a missing referent to `mark_object` as a **non-NULL
placeholder with the correct type but without `HAS_OBJ`**. In the library
`fsck.c` v2.56.0, `fsck_walk_tree` calls `lookup_tree`/`lookup_blob` and then
`options->walk(...)` (lines 376/380 and 383/387), and `fsck_walk_commit` calls
`options->walk` on each parent (line 461); `options->walk` is `mark_object`,
installed at `builtin/fsck.c` 888. `lookup_blob` (blob.c 7–13),
`lookup_tree` (tree.c 167–173) and `lookup_commit` (commit.c 101–107) call
`create_object` when the OID is absent from the object hash, and the allocators
set the type (`alloc_blob_node` sets `OBJ_BLOB`, alloc.c 79–84;
`alloc_tree_node` sets `OBJ_TREE`, 86–91; `init_commit_node` sets `OBJ_COMMIT`,
118–122) while `create_object` leaves `flags = 0`. The type check at
`builtin/fsck.c` 135 therefore passes, and the promisor early return at
`builtin/fsck.c` 143–149 is what suppresses the `HAS_OBJ`-missing report at
151–162. This is the concrete mechanism, not an inference from the absence of
a check.

**Conclusion:** green fsck cannot prove that every promised object is locally
present. The S104 rejection is correct.

### Scope: availability, not general fsck validity

The rejection does **not** claim fsck is invalid or useless, and the row on
review keeps that boundary:

- Non-promisor failures still report: broken link at 123–132, missing object
  at 151–162, `check_reachable_object` missing at 258–261, invalid ref at
  544–546, invalid reflog at 470–472.
- Object content is still checked through `fsck_object` (419–424) and the
  object-database walk (`odb_fsck`, 934–938).
- The row's scope is literally “rejection of fsck green as proof every promised
  object is locally present”; Gate body says “A green fsck is not proof every
  promised object is locally present”; knowledge says “fsck green cannot
  substitute for required-object availability”; SKILL says “not local
  availability proof”.
- The Gate heading “reject as a proposed completeness oracle” is shorthand for
  that availability use; the body and every downstream use narrow it. A full
  grep for `fsck` over `corpus/`, `SKILL.md`, `LOG.md`, `tools/`, `tests/` and
  `registry/` returned only the S104 row, its round-24 Gate bullet, knowledge
  line 105 and SKILL line 846; none asserts general fsck invalidity.
- Boundary, not a counterexample: `is_promisor_object` only builds its set
  when `repo_has_promisor_remote(r)` (`packfile.c` 2067). The rejection is
  about promised objects in promisor-remote repositories; a bare `.promisor`
  file with no promisor remote is a different configuration and is not
  claimed here. The row and Gate both say “promised object”, so the boundary
  is already implicit.

**S104 token: PASS** — the rejection is correctly confined to local
availability proof, not general fsck validity.

## Token ledger

| token | result | evidence |
|---|---|---|
| `S103-URL-ANCHOR` | PASS | 200; `id="_handling_missing_objects"` occurs once; quote is inside the first `<li>` (second paragraph) |
| `S103-VERSION` | PASS | footer `partial-clone last updated in 2.56.0`; row/Gate 2.56.0; tagged adoc v2.56.0 lines 108–118 |
| `S103-ACCESSDATE` | PASS | fresh open 2026-10-21T19:46:50Z; row/Gate 2026-10-21 |
| `S103-QUOTE-25` | PASS | 11 words (full sentence 23) |
| `S103-QUOTE-FIDELITY` | PASS-NOTE | verbatim prefix; unmarked truncation after `contents`; full 23-word sentence fits; meaning preserved |
| `S103-TEACHES-SCOPE` | PASS | positive content page-sourced; availability/completeness excluded; Gate labels its inference |
| `S103-KNOWLEDGEUSE` | PASS | knowledge line 95 and SKILL 845 use only the negative consequence |
| `S103-USEDBY` | PASS | lesson/knowledge/SKILL literal; promisor-grid is a semantic code consumer |
| `S104-URL-LINES` | PASS | raw v2.56.0 200; 143–149 exact; 151 `HAS_OBJ` check |
| `S104-VERSION` | PASS | tag-pinned URL `v2.56.0` |
| `S104-ACCESSDATE` | PASS | row opened 2026-10-21; fresh read 2026-10-21 |
| `S104-QUOTE-25` | PASS | only short code fragments quoted |
| `S104-AVAILABILITY-ONLY` | PASS | exemptions at 143–149, 253–255, 535–542, 469–473; `fetch_if_missing=0` |
| `S104-NOT-GENERAL-VALIDITY` | PASS | non-promisor error paths and content checks remain; all consumer wording is availability-specific |
| `S104-KNOWLEDGEUSE` | PASS | knowledge 105 and SKILL 846 say availability, not fsck validity |

## Command / exit ledger

| command (abbreviated) | exit / status | observation |
|---|---|---|
| `curl … https://git-scm.com/docs/partial-clone` | shell 0; HTTP 200 | 51719 bytes, sha256 `8a649322…b16c9ad` |
| `curl … https://git-scm.com/docs/partial-clone#_handling_missing_objects` | shell 0; HTTP 200 | 51719 bytes, identical hash; fragment client-side |
| `curl … https://git-scm.com/docs/partial-clone/2.56.0` | shell 0; HTTP 200 | 51590 bytes, sha256 `d5c98adf…75d7be1` |
| `curl … Documentation/partial-clone.{adoc,txt}` (guessed paths) | HTTP 404, 14 bytes each | wrong source path; superseded by the technical path below |
| `curl … Documentation/technical/partial-clone.adoc` at v2.56.0 | shell 0; HTTP 200 | 14948 bytes, sha256 `9512d7ee…ce19264`; section 108–118 |
| `curl … builtin/fsck.c` at v2.56.0 | shell 0; HTTP 200 | 26980 bytes, sha256 `d25f3b1a…e5a9ca35` |
| `curl … fsck.c` (library) at v2.56.0 | shell 0; HTTP 200 | 40504 bytes, sha256 `c871ede1…7bc51d9`; `fsck_walk_tree` 354–400, `fsck_walk_commit` 402–469, `fsck_walk` 482–504 |
| `curl … packfile.c` at v2.56.0 | shell 0; HTTP 200 | 58979 bytes, sha256 `021b1b9b…8b94032` |
| `curl … blob.c/tree.c/commit.c/alloc.c` at v2.56.0 | shell 0; HTTP 200 each | 403/5343/53610/2855 bytes; `lookup_*` placeholders and allocator types |
| `git clone --no-hardlinks --quiet … repo` | 0 | scratch clone only |
| `git checkout --detach --quiet 2e254a17…` | 0 | detached pinned checkout |
| `git rev-parse HEAD` | 0 | `2e254a1763a9c08aa07fc53081287f506c447d84` |
| `git status --porcelain` | 0 (empty) | clean scratch |
| `cmp -s <pinned> <production>` ×6 | 0 each | `SOURCES.md`, `round-24.md`, `error-is-not-a-verdict.md`, `SKILL.md`, `promisor-grid.py`, `report-landing-audit.py` identical |
| Python whitespace-normalized quote test | exit 0 | quote found `True`; 11/23 words |
| `grep -c 'id="_handling_missing_objects"'` | 0 | `1` |
| `grep -n 'last updated' partial-clone.html` | 0 | line 1300 |
| `sed`/`awk` reads of fsck.c | 0 | lines 113–167, 246–264, 454–475, 528–562, 884–885 |
| `grep -n check_reachable_object…` | 0 | live call sites 347 and 942 |

## Snapshot revision / hashes

- Base/pinned: `2e254a1763a9c08aa07fc53081287f506c447d84`; production HEAD
  read-only equals it; scratch detached HEAD equals it; scratch clean.
- Pinned ledger file hashes:
  - `corpus/SOURCES.md` `f42c75522e064b34bcaedd3188c85967718a625b7886786c430bdbebaf17d9bd`
  - `corpus/lessons/round-24.md` `a1950674df72352ad4ee0d2b250075e986b390654f62916cf744709d11d1ee45`
  - `corpus/knowledge/error-is-not-a-verdict.md` `d39b8cc18de4c8c8d48be8f06cfcc80e219a24f5dd117083c0829ccae6ddf5ee`
  - `SKILL.md` `0509d53290c20a175bbe8b97cd0dccb6acf472c61449abe374d179fe282f83dd`
  - `tests/report-audit/promisor-grid.py` `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`
  - `tools/report-landing-audit.py` `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`
- Source hashes as listed above; `out/SrcMarker/` retains the fetched bytes.

## Observed vs inferred

**Observed (fetched/read at the pinned revision):**
- HTTP statuses, byte counts, and SHA-256 of the page, versioned page, tagged
  AsciiDoc, `fsck.c`, and `packfile.c`.
- Exact page footer, section markup, quote text, word counts, and the
  first-bullet placement.
- Exact code lines and live call sites in `fsck.c`; the `add_promisor_object`
  insertion of referenced OIDs without an existence check in `packfile.c`;
  `fsck_walk_tree`/`fsck_walk_commit` dispatch in the library `fsck.c`; and
  `lookup_blob`/`lookup_tree`/`lookup_commit` creating typed placeholders via
  `create_object` (`alloc.c` sets `OBJ_BLOB`/`OBJ_TREE`/`OBJ_COMMIT` but not
  `HAS_OBJ`), which is the object `mark_object` skips for promisor membership.
- Registry row, Gate, knowledge, SKILL, and used-by text at the pinned commit;
  production and scratch bytes are identical.

**Inferred / not executed:**
- The marker-vs-availability consequence in the S103 Gate is a lane inference;
  the Gate already labels it as such. I did not run the paired fixtures.
- The S104 mechanism is code-observed through `add_promisor_object` and the
  `lookup_*`/`mark_object` path; I did not execute `git fsck` on a crafted
  promisor repository. The judgment is about the **scope** of the row's
  rejection, not an empirical claim that every green fsck is unsound. General
  fsck validity was not tested and is not asserted.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/SrcMarker.md`
  (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/SrcMarker/pins.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/SrcMarker/partial-clone.html`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/SrcMarker/partial-clone-2.56.0.html`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/SrcMarker/partial-clone-v2.56.0.adoc`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/SrcMarker/fsck-v2.56.0.c`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/SrcMarker/packfile-v2.56.0.c`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/SrcMarker/fsck-lib-v2.56.0.c`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/SrcMarker/blob-v2.56.0.c`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/SrcMarker/tree-v2.56.0.c`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/SrcMarker/commit-v2.56.0.c`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/SrcMarker/alloc-v2.56.0.c`
- Scratch only: `/fast/scratch/hyaku/kama-r24/falsify/SrcMarker/repo` (detached
  pinned clone) and the fetched source files beside it.

No source row edits, no candidate/grid runs, no execution-bearing probes, no
installs or upgrades. The peer-reported blobless-clone lazy-fetch hazard was
not exercised: I created no promisor/blobless fixture, and the only git
operations were a local `--no-hardlinks` clone, detached checkout, `rev-parse`,
and `status` on the lane repository.

## Unverified items

- Remote repository completeness and remote abbreviation uniqueness are out of
  scope and not claimed.
- The unversioned `git-scm.com` page can drift after 2026-10-21; the row's
  `on-release` recheck is the mitigation, and the tag-pinned AsciiDoc is the
  stronger cross-check I used.
- I did not verify GitHub tag object signatures; the `v2.56.0` raw URLs are
  official HTTPS source reads.
- I did not run the promisor grid or any candidate arm; the candidate behavior
  is L1's measurement, not this seat's.
- The S103 quote truncation note is advisory only. If L1 wants strict
  no-unmarked-ellipsis fidelity, quote the full 23-word sentence or append
  `…`; no admission or row-status change follows from either choice.
