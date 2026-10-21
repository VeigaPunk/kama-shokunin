# SrcRepoLayout evidence — gitrepository-layout(5), 2026-10-21

Seat: `KamaR23-2.SrcRepoLayout-2` (leaf, no dispatch). Lane base:
`0df800e896f6bce285a81e794ad4ae1d1e6c3a71`; observed HEAD at read time:
`d1b9d956a0beda9ac32a1a2cf6ced875faeada0d` (preregistration commit only,
`git diff --stat 0df800e..HEAD` = `.ufo/waves/round-24/preregistration.json`,
`LOG.md`). No repository write; this directory and the advice report are the
only files written.

## Fetch log

| Observation | Command | Result |
|---|---|---|
| Live page | `curl -sS -D headers.txt -o layout.html https://git-scm.com/docs/gitrepository-layout` | `200 https://git-scm.com/docs/gitrepository-layout 64533`; HTTP/2 `date: Wed, 21 Oct 2026 17:53:41 GMT`; `last-modified: Wed, 21 Oct 2026 15:55:44 GMT` |
| Page sha256 | `sha256sum layout.html` | `d497ee1e5a006482032f513f42d57b93a2d3c0200aeecd017a89cfb03e9a9b22` |
| Title | `grep -o '<title>[^<]*' layout.html` | `Git - gitrepository-layout Documentation` |
| Version footer | normalized page text | `Latest version ▾ gitrepository-layout last updated in 2.49.0`; changes table first row `2.49.1 → 2.56.0 no changes`; next row `2.49.0 2025-03-14` |
| Versioned 2.56.0 URL | `curl -sS -D vheaders.txt -o /dev/null -w '%{http_code} -> %{redirect_url}' .../gitrepository-layout/2.56.0` | `301 -> https://git-scm.com/docs/gitrepository-layout/2.56.0/` |
| Followed 2.56.0 URL | `curl -sSL -o layout-2560.html .../gitrepository-layout/2.56.0/` | `200`; 632-byte HTML meta-refresh with `link rel=canonical` and `url=https://git-scm.com/docs/gitrepository-layout/2.49.0` |
| Canonical 2.49.0 page | `curl -sSL -o layout-2490.html https://git-scm.com/docs/gitrepository-layout/2.49.0` | `200 .../2.49.0 64404`; `last updated in 2.49.0`; sha256 `5df325827af95187bcfc109a36b3f6c59781d19ad753fd6f68c539aa44ac87e9` |
| Upstream doc, tag v2.56.0 | `curl -sS -o gitrepository-layout-2.56.0.adoc https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitrepository-layout.adoc` | `200 11890`; sha256 `39ce8d137a30e1fd80eeae146b1c424e56f688f4ddd001259eb98543d3209439` |
| Upstream doc, master | same URL with `master` | `200 11890`; sha256 identical `39ce8d137a30e1fd80eeae146b1c424e56f688f4ddd001259eb98543d3209439` |
| Local interpreter | `git --version`; `zcat /usr/share/man/man5/gitrepository-layout.5.gz` | `git version 2.56.0`; man page carries the alternates text at line 141 |

Access date for all reads: **2026-10-21** (UTC; live fetch 17:53:41Z).

## Negative coverage for `.promisor` / partial clone

| Artifact | Command | Result |
|---|---|---|
| Live page, raw HTML | `grep -ic promisor layout.html` | `0` |
| Canonical 2.49.0 page | `grep -ic promisor layout-2490.html` | `0` |
| Live page, normalized text | Python regex `partial[ -]clone` | `0` |
| Upstream v2.56.0 adoc | `grep -ic promisor gitrepository-layout-2.56.0.adoc` | `0` |
| Upstream master adoc | `grep -ic promisor master.adoc` | `0` |
| Local man5, git 2.56.0 | `zcat ... | grep -c -i promisor` | `0` |
| `objects/pack` section | normalized text around `objects/pack` | only the generic pack/index sentence below; no marker suffix, no `*.keep` or `*.promisor` |

The same `grep -Eci 'partial[ -]clone'` returns `0` for `layout-2490.html`,
both upstream adocs, and the local git 2.56.0 man5 page.

The `objects/pack` section text in full:

> Packs (files that store many objects in compressed form, along with index
> files to allow them to be randomly accessed) are found in this directory.

## Exact quotes (verbatim after the page's own line-wrap normalization)

Each normalized quote occurs exactly once (`str.count == 1`).

| Anchor id | Page section | Quote | Words |
|---|---|---|---|
| `Documentation/gitrepository-layout.txt-objectsinfoalternates` | objects/info/alternates | "This file records paths to alternate object stores that this object store borrows objects from, one pathname per line." | 19 |
| same | objects/info/alternates | "relative paths (relative to the object database, not to the repository!)" | 11 |
| `Documentation/gitrepository-layout.txt-objects` | objects, second bullet | "You could be using the objects/info/alternates or $GIT_ALTERNATE_OBJECT_DIRECTORIES mechanisms to borrow objects from other object stores." | 16 |
| `Documentation/gitrepository-layout.txt-objects` | objects, first bullet | "You could have an incomplete but locally usable repository by creating a shallow clone." | 14 |
| `Documentation/gitrepository-layout.txt-objects` | objects, closing note | "This directory is ignored if $GIT_COMMON_DIR is set and \"$GIT_COMMON_DIR/objects\" will be used instead." | 14 |
| `Documentation/gitrepository-layout.txt-objectspack` | objects/pack | "Packs (files that store many objects in compressed form, along with index files to allow them to be randomly accessed) are found in this directory." | 25 |
| `Documentation/gitrepository-layout.txt-objectsinfohttp-alternates` | objects/info/http-alternates | "This file records URLs to alternate object stores that this object store borrows objects from, to be used when the repository is fetched over HTTP." | 25 |

All four distinct anchor ids resolve once each in the live HTML
(`grep -o 'id="Documentation/gitrepository-layout.txt-<anchor>"'` count = 1
each): `objects`, `objectspack`, `objectsinfoalternates`,
`objectsinfohttp-alternates`.

## Correct authority for the `.promisor` marker (boundary note, not part of S094)

`https://git-scm.com/docs/partial-clone#_design_details`, fetched 2026-10-21,
HTTP 200, 51,719 bytes, sha256
`8a6493225f76dba8e5b1eb75234f7370e057ee87c11e07a2681dbf522b16c9ad`, contains 43
case-insensitive `promisor` matches. Exact sentence (23 words):

> These promisor packfiles consist of a "<name>.promisor" file with arbitrary
> contents (like the "<name>.keep" files), in addition to their "<name>.pack"
> and "<name>.idx" files.

This sentence is in `#_design_details`, whereas the registered row S099 anchors
`#_handling_missing_objects`. The `.promisor` marker definition is therefore not
inside S099's registered anchor.

## Registry rows read (no edit)

- `git show 0df800e:corpus/SOURCES.md | sed -n '106p'` → S094 row:
  `Git gitrepository-layout(5) — https://git-scm.com/docs/gitrepository-layout`,
  scope `on-disk history rewriting and borrowing: info/grafts, shallow,
  refs/replace, objects/info/alternates`, status `mined`, opened `2026-10-21`,
  recheck `on-release`, used-by `corpus/lessons/round-23.md`.
- S089 at `corpus/SOURCES.md:101` (git global options), S099 at `:111`
  (partial-clone §Handling Missing Objects), S100 at `:112` (git-config keys).
- Last row id `S101`; next unused id would be `S102` if L1 ever opens a new
  source. This seat recommends none.

## Local context observed (not source evidence)

- `tools/report-landing-audit.py:455-457` refuses a `.promisor` file with a
  sibling `.pack`; `:465` refuses `extensions.partialclone` or a true
  `remote.<name>.promisor`.
- `tests/report-audit/repo-state-grid.py:195` (`f_promisor_pack`), `:670`
  (`F23-promisor-pack-without-config`), `:545` (`c_orphan_marker`), `:680`
  (`C10-orphan-promisor-marker`), `:585`/`:686` (`O01-alternates-foreign-object`).
- `corpus/lessons/round-23.md:171` (M4) records four zero-byte `.promisor`
  markers written into the real fleet repository that made the audit refuse it;
  `:205-208` records that a complete blobless partial clone (T01) and a paired
  promisor pack without promisor config (F23) are refused where frozen gave a
  verdict.

## Not run

No fixtures, no audit invocation, no grid, no selftest, no mutation run, no
registry edit, no production edit. The partial-clone page was opened only to
name the correct authority; it is not proposed here as a new row.

## Installs / updates

None.
