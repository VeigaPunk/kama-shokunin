# SrcRepoLayout — gitrepository-layout(5): reopened used source; no `.promisor` evidence

Seat: `KamaR23-2.SrcRepoLayout-2` (leaf, no dispatch). Lane base
`0df800e896f6bce285a81e794ad4ae1d1e6c3a71`; read at HEAD
`d1b9d956a0beda9ac32a1a2cf6ced875faeada0d` (preregistration commit only).
No production or registry file edited.

## Verdict

**Reopened used source — not reusable as a new `.promisor` authority; no
SOURCES row is admissible from this page.**

`https://git-scm.com/docs/gitrepository-layout` is already registered as
**S094** (`corpus/SOURCES.md:106`, `mined`, used-by
`corpus/lessons/round-23.md`). It supports the alternates / object-store
locality half of this ticket. It contains **zero** occurrences of
`promisor` or `partial clone` in the live page, the canonical 2.49.0 page, the
upstream `v2.56.0` adoc, the upstream `master` adoc, and the local git 2.56.0
man page. The pack-`.promisor` half is therefore **outside this source's
coverage**, not new scope this page can carry. Adding a row for it would be a
false anchor.

## Opened source (exact)

| Field | Observation |
|---|---|
| URL | `https://git-scm.com/docs/gitrepository-layout` |
| Access date | **2026-10-21** (UTC; HTTP `date: Wed, 21 Oct 2026 17:53:41 GMT`) |
| HTTP/body | `200`, 64,533 bytes, sha256 `d497ee1e5a006482032f513f42d57b93a2d3c0200aeecd017a89cfb03e9a9b22` |
| Page title | `Git - gitrepository-layout Documentation` |
| Version shown | footer `Latest version ▾ gitrepository-layout last updated in 2.49.0`; changes table `2.49.1 → 2.56.0 no changes`; local `git --version` = `2.56.0` |
| Versioned URL | `/gitrepository-layout/2.56.0` → `301` → `/2.56.0/` → 632-byte meta-refresh canonical `/gitrepository-layout/2.49.0` → `200`, 64,404 bytes, sha256 `5df325827af95187bcfc109a36b3f6c59781d19ad753fd6f68c539aa44ac87e9` |
| Upstream cross-check | `raw.githubusercontent.com/git/git/v2.56.0/Documentation/gitrepository-layout.adoc`: `200`, 11,890 bytes, sha256 `39ce8d137a30e1fd80eeae146b1c424e56f688f4ddd001259eb98543d3209439`; `master` adoc byte-identical (same sha256) |
| Local cross-check | git 2.56.0 man5 `gitrepository-layout.5.gz`: alternates text at line 141; `grep -ci promisor` = `0` |

Why both version labels are correct: the page's live content is the 2.56.0
manual (unchanged since 2.49.0), and git-scm.com canonicalizes the versioned
2.56.0 URL to the 2.49.0 snapshot because no text changed in between.

## Exact anchors and quotes (verbatim, ≤25 words)

| Anchor | Section | Quote | Words |
|---|---|---|---|
| `#Documentation/gitrepository-layout.txt-objectsinfoalternates` | objects/info/alternates | "This file records paths to alternate object stores that this object store borrows objects from, one pathname per line." | 19 |
| same | objects/info/alternates | "relative paths (relative to the object database, not to the repository!)" | 11 |
| `#Documentation/gitrepository-layout.txt-objects` | objects, second bullet | "You could be using the objects/info/alternates or $GIT_ALTERNATE_OBJECT_DIRECTORIES mechanisms to borrow objects from other object stores." | 16 |
| `#Documentation/gitrepository-layout.txt-objects` | objects, first bullet | "You could have an incomplete but locally usable repository by creating a shallow clone." | 14 |
| `#Documentation/gitrepository-layout.txt-objects` | objects, closing note | "This directory is ignored if $GIT_COMMON_DIR is set and \"$GIT_COMMON_DIR/objects\" will be used instead." | 14 |
| `#Documentation/gitrepository-layout.txt-objectspack` | objects/pack | "Packs (files that store many objects in compressed form, along with index files to allow them to be randomly accessed) are found in this directory." | 25 |
| `#Documentation/gitrepository-layout.txt-objectsinfohttp-alternates` | objects/info/http-alternates | "This file records URLs to alternate object stores that this object store borrows objects from, to be used when the repository is fetched over HTTP." | 25 |

Each normalized quote occurs exactly once; each anchor id occurs once in the
live HTML. Full evidence: `out/SrcRepoLayout/evidence.md`.

## Existing registry rows: reopened vs new scope

- **S094** — `corpus/SOURCES.md:106` (identical at base `0df800e`):
  `gitrepository-layout(5)`, scope "on-disk history rewriting and borrowing:
  info/grafts, shallow, refs/replace, objects/info/alternates", status
  `mined`, opened `2026-10-21`, recheck `on-release`, used-by
  `corpus/lessons/round-23.md`. This is the **reopened used source**.
- No other row names this page; the only nearby in-tier mention is S089's
  "Neither covers info/grafts or shallow" (`corpus/SOURCES.md:101`). Last row is
  S101; next unused id would be S102.
- **Alternates/locality** — already inside S094's scope and anchor
  (`objects/info/alternates`, plus §objects). No new row needed.
- **Pack `.promisor`** — no row, and this page cannot supply one. The
  established pattern is one row per page (correction rows S082/S083/S085
  supersede rather than duplicate), so a second gitrepository-layout row would
  also violate the registry's one-page convention. No correction row is needed
  for S094 itself: r23 falsification admitted it within its scope.

Correct promisor authorities, for L1's decision (not new rows from me):
`S099` partial-clone §Handling Missing Objects (lazy fetch), `S100`
git-config `extensions.partialclone` / `remote.<name>.promisor`, and `S089`
git `--no-lazy-fetch`. Note the exact marker definition is in partial-clone
**§Design Details**, not S099's §Handling Missing Objects anchor:
"These promisor packfiles consist of a \"<name>.promisor\" file with arbitrary
contents (like the \"<name>.keep\" files), in addition to their \"<name>.pack\"
and \"<name>.idx\" files." (23 words; excerpt in
`out/SrcRepoLayout/partial-clone-promisor-excerpt.md`). If L1 needs a directly
anchored marker definition, that is a registry-owner correction decision; this
seat makes no edit.

## Claim-vs-source limits (C1 repair)

| Prospective claim | Source support | Limit |
|---|---|---|
| `objects/pack/*.promisor` marks a partial clone | **No** | Zero `promisor`/`partial clone` text on the page, both adocs, and the local man page. §objects/pack lists only pack + index files. |
| A `.promisor` marker means required objects may be absent | **No** | The page never connects any pack marker to missing objects or on-demand fetch. |
| Promisor config or lazy fetch means absence is not evidence | **No** | No config/lazy-fetch text at all. Use S099/S100/S089. |
| Metadata-only declarations do not establish incompleteness | **Framing only** | §objects calls a store "usually self sufficient" and lists two ways to violate it (shallow, alternates); it does not define promisor metadata or state that a marker is insufficient. Usable as locality context, not as the policy anchor. |
| A store borrowing through alternates is incomplete but locally usable | **Yes, for local paths** | "borrow objects from other object stores"; relative paths resolve to the object database; "otherwise is OK as long as objects/info/alternates points at the object stores it borrows from." |
| Alternates are guaranteed local-only / never network | **No** | The page says the HTTP fetcher also tries to use `objects/info/alternates` remotely, and documents URL-based `objects/info/http-alternates`. |
| Objects through alternates "resolve as local" | **Paraphrase only** | Page says "borrow"; r23 S094 falsification C3 already flagged the tool's stronger wording (`tools/report-landing-audit.py:53`). Do not grade a transparency claim from S094. |
| Object store is always `<repo>/.git/objects` | **No** | `$GIT_COMMON_DIR/objects` can replace it. This is a locality fact, not an audit-trust rule. |
| Blanket refusal of any promisor-marked repository | **No** | Nothing on this page warrants it; the r23 breadth is recorded locally at `corpus/lessons/round-23.md:76` and `:205-208` (T01/F23 refused where frozen gave a verdict). The page's pack section is neutral. |
| Timeout, `--no-lazy-fetch`, signature suppression | **No** | Not covered here; S089/S100. |

The page's §objects list is illustrative ("a few ways"), so the absence of a
promisor bullet is a **documentation-coverage** limit, not proof that git has no
promisor mechanism. Do not cite it as negative evidence about git behaviour.

## Local context observed (not source evidence)

- `tools/report-landing-audit.py:455-457` refuses a `.promisor` with a sibling
  `.pack`; `:465` refuses `extensions.partialclone` or a true
  `remote.<name>.promisor`.
- `tests/report-audit/repo-state-grid.py:195` (`f_promisor_pack`), `:670`
  (`F23-promisor-pack-without-config`), `:545` (`c_orphan_marker`), `:680`
  (`C10-orphan-promisor-marker`), `:585`/`:686` (`O01-alternates-foreign-object`).
- `corpus/lessons/round-23.md:171` (M4): four zero-byte `.promisor` markers in
  the real fleet repository made the audit refuse it — the exact
  marker-only harm class the preregistration targets. The page supplies no
  warrant for marker-only refusal; it does supply the alternates side of the
  repair.

## Recommendation

1. **No SOURCES edit, no new row.** Keep S094 as `mined`; its page/version/
   anchor set is factually backed within its registered scope.
2. Do **not** use this page to justify `.promisor`/promisor-config detection or
   blanket refusal. For C1, use S099/S100/S089 plus availability of the
   required objects; use S094 only for the alternates-complete case and the
   "incomplete but locally usable" framing.
3. If L1 later revises S094's prose (append-only correction, not required by
   this ticket), prefer the page's word "borrow" over "resolve as local" and
   add the relative-path caveat. A `.promisor` marker anchor would have to be
   the partial-clone §Design Details correction path, not gitrepository-layout.

## Not run

No fixtures, audit runs, grid, selftest, mutation run, or tests. The
partial-clone page was fetched only to name the correct authority; no row is
proposed from it here. `[INFERENCE]` applies only to the recommendation that
marker detection cannot be graded from this page; the zero-match observations
are direct.

## Installs / updates

None.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/advice/SrcRepoLayout.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/SrcRepoLayout/evidence.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/SrcRepoLayout/gitrepository-layout-2.56.0.adoc`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/SrcRepoLayout/partial-clone-promisor-excerpt.md`
