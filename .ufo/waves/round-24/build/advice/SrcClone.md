# SrcClone — git-clone(1) `--filter=blob:none` / `--no-checkout`

Seat: SrcClone (leaf scout, no dispatch). Assignment: open the official
`https://git-scm.com/docs/git-clone` page, return exact anchor / version / access
date / ≤25-word quote and claim-vs-source limits, and decide reopened-used vs new
scope against the existing SOURCES rows. No registry edit was made.

## Verdict

**ADMIT as a NEW source row (next free id S102).** Not a reopened previously used
source: no `git-clone` row exists and no non-wave file cites the URL. The scope —
clone-time `--filter` request and `--no-checkout` worktree suppression — is not
covered by any registered Git row. It supersedes nothing.

## Reopened-used vs new-scope evidence (base corpus, unchanged at HEAD)

- `grep -rn "git-clone" .` excluding `./.ufo/` → **zero** hits; no production,
  knowledge or lesson file cites the page.
- `corpus/SOURCES.md` holds **101** rows, S001–S101 (`grep -c '^| S'` → 101).
  The only rows mentioning clone are partial-clone rows, not this page:
  `corpus/SOURCES.md:104` (S092) and `:111` (S099), both
  `https://git-scm.com/docs/partial-clone`; `:101` (S089) is `git(1)`
  `--no-lazy-fetch`; `:106` (S094) is `gitrepository-layout`.
- The one wave mention, `.ufo/waves/round-23/falsify/advice/SrcS094.md:121`,
  records that the page was **not** opened ("I did not open git-replace(1) or
  git-clone(1) …").
- The *practice* is already in the repo without a source row:
  `tests/report-audit/repo-state-grid.py:203-204` and `:600-601` run
  `clone -q [--no-checkout] --filter=blob:none --no-local file://…`, and
  `:489-490` sets `remote.origin.partialclonefilter=blob:none`. So the row would
  document existing fixture practice; that is new registry scope, not a reopening.

## Page facts

Access: **2026-10-21** (local 14:59 −03; UTC 17:59Z).
Fetch: `curl -sS -L --max-time 60 https://git-scm.com/docs/git-clone -o git-clone.html`
→ HTTP 200, 107886 bytes, sha256
`d6e7b5e8b4e5d65401f4f002f94ccdac2faa27f914261b0db0916aef85b66dc9`.

Version: the page prints **"git-clone last updated in 2.54.0"**; the changes table
carries **"2.55.0 → 2.56.0 no changes"**; the 2.54.0 row is dated 2026-04-20.
`/docs/git-clone/2.54.0` → HTTP 200, byte-identical sentences, sha256
`efe89007422070dde3837e2389d297d97d1bfcc79354fe90ebbab263978bdce3`;
`/docs/git-clone/2.56.0` → a 599-byte meta-refresh to `/docs/git-clone/2.54.0`,
i.e. the 2.56.0 pin resolves to the 2.54.0 text rather than an independently
updated 2.56.0 manual. Host interpreter: `git version 2.56.0`.

Anchors (each `id` present exactly once in the fetched HTML; the page's own
synopsis links to each exactly once):

- `https://git-scm.com/docs/git-clone#Documentation/git-clone.txt---filterfilter-spec`
  — OPTIONS `--filter=<filter-spec>` (definition block at text lines 2741–2765)
- `https://git-scm.com/docs/git-clone#Documentation/git-clone.txt---no-checkout`
  — OPTIONS `-n`, `--no-checkout` (text lines 2709–2712)

Quotes (verbatim after collapsing the page's own line wrap):

1. **9 words** — "Do not checkout HEAD after the clone is complete."
   (§`--no-checkout`; the only sentence defining the option.)
2. **11 words** — "will filter out all blobs (file contents) until needed by Git"
   (§`--filter`; full sentence, 14 words: "For example, `--filter=blob:none` will
   filter out all blobs (file contents) until needed by Git.")
3. Supporting, **22 words** — "Use the partial clone feature and request that the
   server sends a subset of reachable objects according to a given object filter."
4. Worktree confirmation (submodule clause, the page's only statement that
   `--no-checkout` means no worktree): "This option is ignored if the cloned
   repository does not have a worktree/checkout (i.e. if any of
   `--no-checkout`/`-n`, `--bare`, or `--mirror` is given)".

## Claim-vs-source limits (what this page does NOT establish)

1. **No lazy-fetch mechanics.** "promisor" occurs only in the `--filter=auto`
   paragraph (promisor-remote protocol, `promisor.acceptFromServer`). The page
   never mentions missing-object lookups, `.promisor` packfiles, or
   `remote.<name>.promisor`. Do not cite it for "missing-object lookups fetch".
   It does say the filter value is persisted in configuration ("As with other
   filter specifications, the 'auto' value is persisted in the configuration"),
   which is about the filter value, not the promisor-remote flag.
2. **No filter-spec definition.** It delegates: "For details on all other
   available filter specifications, see the `--filter=<filter-spec>` option in
   git-rev-list[1]." `git-rev-list` 2.56.0 (fetched 200, "last updated in
   2.56.0") states "The form `--filter=blob:none` omits all blobs."
3. **No completeness claim.** The page never says a `blob:none` clone contains
   all commits and trees; that follows only from the filter being a *blob* filter
   (git-rev-list "omits all blobs"). Treat "commits and trees are present" as
   [INFERENCE] from the two pages plus local observation, not as this quote.
4. **Clone-time request, not repository property.** `--filter` "request[s] that
   the server sends a subset"; the page says nothing about what may be inferred
   about an existing repository's completeness from its provenance.
5. **Checkout→blob relation is not here.** `--no-checkout` is documented only as
   "Do not checkout HEAD"; that checkout *needs* blobs belongs to partial-clone
   §Handling Missing Objects ("checkout (and any other command using
   unpack-trees) has been taught to bulk pre-fetch all required missing blobs in
   a single batch", 21 words), not to git-clone.
6. **No verdict semantics.** Nothing about audit exit classes, evidence
   completeness, or "missing means never existed". Partial-clone says the
   opposite: "An object may be missing due to a partial clone or fetch, or
   missing due to repository corruption." (18 words, same section).
7. **Server support unstated.** The page says the clone asks the server; it does
   not say what happens when filtering is refused. The fixtures keep
   `uploadpack.allowFilter=true` (`repo-state-grid.py:205`, `:600`) — repo
   practice, not page text.

## Bounded offline fixture measurement (scratch only, no network)

Transcript: `.ufo/waves/round-24/build/out/SrcClone/evidence.md`. Local
`file://` + `--no-local` clones of a one-commit source in
`/fast/scratch/hyaku/kama-r24/SrcClone/fx2..fx4`:

- `--filter=blob:none --no-checkout` → one pack holding **commit + tree only**;
  `GIT_NO_LAZY_FETCH=1 git cat-file -e <blob>` exits nonzero (MISSING); no
  worktree file.
- `--filter=blob:none` with checkout → **two packs**; the blob sits in the second
  pack and the worktree file reads `hello` → the checkout hydrated the blob.
- `--no-checkout`, then plain `git cat-file -e <blob>` → exit 0 and packs 1→2 →
  the missing-object lookup fetched the blob.

This matches "until needed by Git" plus partial-clone's bulk-prefetch sentence,
and shows the isolation is carried by `--no-lazy-fetch` (S089), not by the clone
flags.

## Split for the C1 claim

- **Observed in docs:** `blob:none` omits blobs only (git-rev-list);
  `--no-checkout` leaves no worktree; a missing object may come from a partial
  clone *or* corruption, and Git does not check whether the missing object is a
  promisor object.
- **[INFERENCE]** A `blob:none --no-checkout` clone is locally complete for
  commit and tree objects, so a required commit/tree found locally is real
  evidence and promisor metadata alone is not incompleteness.
- **[INFERENCE]** A required blob that cannot resolve under `--no-lazy-fetch` is
  genuinely absent locally → exit 2, never clean; but absence does not prove the
  commit never existed, so an unresolved citation is exit 2 unless another
  audited repository resolves it locally.
- **Not supported by any opened page:** completeness of a pre-existing repository
  inferred from its provenance; any exit-code policy.

## Proposed row text (for L1 — not applied)

| S102 | git-clone(1) partial-clone request and checkout — https://git-scm.com/docs/git-clone#Documentation/git-clone.txt---filterfilter-spec | docs | A | clone-time `--filter` request and `--no-checkout` worktree suppression; not lazy-fetch mechanics, filter-spec definitions, or audit verdicts | OPTIONS `--filter=<filter-spec>` and `-n/--no-checkout`; page "git-clone last updated in 2.54.0", changes table "2.55.0 → 2.56.0 no changes"; opened 2026-10-21 | `--filter` asks the server for a subset by object filter and `--filter=blob:none` filters out all blobs until needed by Git; `--no-checkout` does not checkout HEAD, so the clone has no worktree. Filter-spec definitions are delegated to git-rev-list(1). | mined | 2026-10-21 | on-release | corpus/lessons/round-24.md (pending) |

Adjacent note (no edit): S099's anchor cell already names partial-clone
§Handling Missing Objects, but its teaches cell quotes only the "no check"
sentence. If the r24 claim leans on corruption-vs-clone ambiguity or checkout
bulk prefetch, those quotes belong in the round lesson; amending the S099 cell is
L1's call.

## Unverified / not done

- Fragment delivery cannot be verified over HTTP (fragments are not sent);
  verified instead by matching `id=` attributes and the page's own `href="#…"`
  links (one each).
- Did not run the repo-state grid, selftest or any kama test; only the
  3-command scratch fixture above.
- Did not register or open git-rev-list as a row (no row exists; URL fetched 200,
  "last updated in 2.56.0").
- Did not test a server that refuses `--filter`; no network transport used
  (`file://` only, `protocol.file.allow=always`).
- Base observed at start: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`. During
  this seat HEAD advanced to `d1b9d956a0beda9ac32a1a2cf6ced875faeada0d`, touching
  only `LOG.md` and the round-24 preregistration; `corpus/SOURCES.md` line
  numbers were re-checked and are unchanged.
- Software: curl 8.23.0, git 2.56.0, Python 3.14.8. No installs or updates.
