# AuditRepair — r24 C1: promisor-metadata repair of `tools/report-landing-audit.py`

Seat: `KamaR23-2.AuditRepair-2` (leaf). Scratch clone: `/fast/scratch/hyaku/kama-r24/AuditRepair`
(`git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin`), base observed
`0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (the r23 tip; the r24 preregistration base).

Deliverables (no production file was touched; the lane/fleet working trees, `.jj` and the lane
Git index are unchanged, nothing was committed or pushed):

- candidate file: `.ufo/waves/round-24/build/out/AuditRepair/report-landing-audit.py`
  (sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`)
- unified patch: `.ufo/waves/round-24/build/out/AuditRepair/report-landing-audit.patch`
  (`git diff -- tools/report-landing-audit.py` from the scratch clone; +417/−73)

Policy authority: `.ufo/waves/round-24/oracle-amendment-1.json` (landed `123640b`) and
`.ufo/waves/round-24/oracle-supplement-2.json` (landed `aacbd520`).

## Verdict

The round-23 blanket refusal (`extensions.partialclone`, `remote.*.promisor`, and any paired
`objects/pack/*.promisor` marker) is gone: a repository that merely *declares* a partial clone
is now audited exactly like its unmarked twin — same clean/failed verdict, same defect kinds and
tokens, no fetch, no transport, no timeout. What decides a citation is not the declaration but
whether the content the citation names can be read:

| case | round-23 | candidate | why |
|---|---|---|---|
| marked repo, all objects present locally, fabricated citation | exit 2 `partial clone` | exit 1 `unresolved-full-hash` | the local object database is the history the audit reads; a declaration is not evidence |
| marked repo, all objects present locally, citations valid | exit 2 | exit 0/1 (the twin's verdict) | same |
| marked **or plain** repo, cited object referenced but not servable (blobless clone, F23) | exit 2 `promisor pack` | exit 2, content-derived reason naming the object | absence is not proved: the history names it and the store cannot hand it over |
| cited object is a known tag whose target is unavailable | exit 2 (metadata) | exit 2, content-derived reason | the object is here, its content is not readable |
| locally present blob/tree cited as a Landed commit | exit 1 `landed-unresolved` | exit 1 `landed-unresolved` | the object name fixes the type: a proved mismatch, not an unknown |
| unrelated missing blob/tree/branch (never cited) | exit 2 (metadata) | no effect on the verdict | it blocks nothing; the audit reads what it reads |
| missing tree (opaque hole) + every citation resolved | — | the ordinary verdict | the diagnosis is not a precondition |
| missing tree (opaque hole) + an unresolved citation | — | exit 2 | the hidden names make the unresolved token unevaluable |
| citation found in the *other* audited repository | resolved | resolved | the lookup stays repository-wide |

Exit codes are unchanged (0 clean / 1 failed / 2 could-not-evaluate), the JSON document keeps
its shape (no new keys), and no flag or deadline changed.

## What the candidate does (path:line in the candidate file)

1. `:100` — `RANK` precedence for the local answers:
   `absent < wrongtype < unknown < ambiguous < found`. A resolved object wins; an ambiguous
   prefix is a proved fact; an object whose content cannot be read is *unknown*; a known object
   of the wrong type is a proved mismatch; an object nobody holds is the weakest answer.
2. `:184` — `lookup(stores, tokens, peel="")` returns
   `found|ambiguous|unknown|wrongtype|absent` (round 23 returned `found|ambiguous|missing`).
   - the bare (un-peeled) answer is still asked first, so git's `missing` for an ambiguous short
     name under a peel cannot hide the ambiguity (round-23 behaviour kept).
   - when the bare answer is *found* but the peel is `missing`, a second
     `cat-file --batch-check` with the `^{}` peel asks whether what the object dereferences to
     is here too: `missing` → **unknown** (a tag whose target the store cannot serve, or any
     object whose content is unavailable), otherwise **wrongtype** (a blob/tree/tag of a known
     type: a proved mismatch). The peel is a native git expression, so no tag chain is parsed
     here. `lookup()` never raises: the second repository is still consulted, so a citation
     absent in a marked lane and present in the fleet stays *found*.
3. `:266` — `required_read(what, exc)`: a read of evidence the audit needs failed → the refusal
   names what was wanted (`unavailable required object: …`). Applied to the lane history log,
   the fleet's first-add log, the committed report and the `SOURCES.md` blob/tree reads; the
   underlying git failures are preserved verbatim inside the message.
   `:280` — `root_tree(repo, root)`: the tree id the root commit names, read from the commit
   header (`git log -1 --format=%T`, which reads no tree), so a refusal about a missing tree
   names that tree: `…:corpus/SOURCES.md (tip tree a33984f2…) in <lane>` and
   `….ufo/reports/round-1/kama.md at fleet HEAD (tip tree cf831cbe…, <fleet>)`. When even the
   commit cannot be read, the original error/path reason is kept.
4. `:400` — `refuse_unknown(rnd, status, stores)`: the refusal, raised **before** any
   finding is emitted. A resolved, ambiguous or wrong-type token is a finding; a token nobody
   holds is a proved absence, unless
   - the store references it and cannot serve it → exit 2 `unknown: unavailable required
     object: <token> is referenced by the history of <repo> but the repository cannot serve it`;
   - a missing tree or commit could hide it → exit 2 `… could be hidden behind the missing tree
     or commit <oid> in <repo>`, naming the unavailable object itself (the lowest missing
     tree/commit id the store reports, so the refusal is deterministic);
   - the object is present but its content cannot be read → exit 2 `… is present but its
     content cannot be served`.
   No errata row can rescue these: unavailable content is not a defect to correct.
5. `:431` — `audit_round(...)`: the two citation lookups (the full-hash scan and the Landed
   citations) call `refuse_unknown` before the defects are built; an ordinary absent citation
   stays an ordinary finding and the ordinary errata path applies to it.
6. `:522` — `apply_errata(...)`: an errata correction whose content cannot be read is refused
   as unknown, never counted as `errata-invalid` (a guessed verdict about the authority input).
7. `:614` — `present_roots(repo)`: every present object that can root a traversal (the commits,
   trees and tags the local object database holds, reachable or not, strict 40-hex ids only). A
   dangling commit, tree or tag can reference an object the store cannot serve and no ref
   reaches it.
8. `:630` — `missing_reachable(repo, root)`: `(missing, opaque)` — the object ids the store
   references but cannot serve, and the subset that hides names. Two walks over the same roots:
   `rev-list --objects --missing=print --no-object-names --stdin` (every missing id) and the
   same with `--filter=blob:none` (the missing ids that are not blobs, so a missing tree or
   commit is visible). The commit graph is switched off (`-c core.commitGraph=false`) so it
   cannot hide an unavailable object. Both walks go through the existing `git()` wrapper, so
   they inherit `--no-lazy-fetch`, `--no-replace-objects`, the log/signature suppression,
   `GIT_CONFIG_GLOBAL=/dev/null` and the 20 s deadline.
9. `:659` — `build_store(repo, root)`: the audited repository and the pinned root (the lane
   branch tip or the fleet tip). The root is the audit's context, **not** a completeness gate;
   the store-wide diagnosis runs only for a citation no audited repository resolves.
10. `:668`/`:684` — `unknown_citation(stores, token)` (the store whose history references the
    cited token but cannot serve it) and `opaque_hole(stores)` (the store with a missing tree or
    commit **and the id of one such object**, so a refusal names the unavailable object, not
    only the cited token).
11. `:725` — `run(...)`: the roots are explicit and per-run; `stores = (build_store(lane_repo,
    tip), build_store(fleet_repo, fleet_tip))`. No global cache, no metadata classifier.

### Removed (the stale machinery)

`promisor_state()` (the config/pack-marker classification), the `objects/pack` marker refusal,
the `extensions.partialclone`/`remote.*.promisor` config refusal and the now-unused `git_bool()`
parser are gone: metadata must not affect a verdict, so classifying it would only be dead
weight. `check_history_repo()` keeps the sha1, non-top-level, shallow and grafts refusals
byte-identical and still runs **before** any availability probe.

## Promoted outcomes and why (missing / blob / tree / commit)

- **missing (an object the history references but the store cannot serve)** → exit 2, never a
  proved absence. The contract (base `tools/report-landing-audit.py:12-19`) is "a 40-hex token
  that is no git object in the lane or fleet repo". When the local history *names* the object
  and the store cannot serve it, "no git object here" is a fact about the local copy, not about
  the repository. The remedy is a bounded `--no-lazy-fetch` walk of the store's present
  objects; a token that names a `?`-reported id is unknown (exit 2), every other unresolved
  token keeps the ordinary finding (exit 1) and the ordinary errata path.
- **opaque hole (a missing tree or commit)** → the names of the objects below it are unknown, so
  an unresolved token could be hiding there: exit 2 for that token, and no effect at all when
  every citation resolves.
- **blob / tree (locally present, cited as a commit)** → exit 1 `landed-unresolved`, unchanged.
  A full 40-hex name fixes the type, so the mismatch is proved; the bare
  `cat-file --batch-check` answer (which carries the type) is the evidence, not git's `missing`
  line under a peel.
- **tree / commit / report blob that the audit must read** → exit 2, unchanged and for free,
  and the reason names the unavailable object (the tip tree id for a missing tree, the blob id
  for a missing blob, the path for a missing report):
  `git log` (`rc 128`, "Failed to traverse parents"), `git log --diff-filter=A` (`rc 128`,
  "unable to read tree"), `git show HEAD:<report>` (`rc 128`, "bad object"), `git cat-file blob`
  (`rc 128`, "bad file") all fail through the strict `git()` wrapper → `EvalError` → exit 2,
  now with the reason class `unavailable required object` and the wanted path/object named.
  Per-read errors are preserved; no blanket precondition was added in their place.
- **tag whose target is unavailable** → exit 2. The object is present, so the peel cannot be
  read: `^{}` distinguishes "dereferences to a known object" (a proved wrongtype → exit 1) from
  "the target cannot be served" (unknown → exit 2).

## Measured (this candidate, git 2.56.0, Python 3.14.8)

- `python3 tools/report-landing-audit.py --selftest` → **62 cases, 0 failed**. The 50 round-23
  cases are unchanged; 12 new cases cover the round-24 behaviour:
  `wrongtype-citation-is-a-failed-finding`, `promisor-metadata-keeps-the-local-verdict` (a
  marked lane with `extensions.partialClone`, `remote.origin.promisor`,
  `remote.origin.partialclonefilter`, a paired `.promisor` marker and a `core.sshCommand` trap →
  the same verdict as the unmarked twin and **the trap file was never created**),
  `promisor-remote-is-never-contacted`, `unrelated-missing-object-does-not-block`,
  `citation-of-a-missing-object-is-unknown`, `errata-cannot-rescue-unavailable-content`,
  `errata-corrects-an-ordinary-absent-citation`, `known-tag-with-unavailable-target-is-unknown`,
  `blob-hole-is-not-an-opaque-hole`, `missing-tree-is-an-opaque-hole`,
  `unused-tree-hole-does-not-block-resolved-citations`,
  `opaque-hole-makes-an-unresolved-token-unknown`.
- historical ledger parity: `--lane-repo /home/vgpnk/Projects/shokunin/kama-shokunin
  --fleet-repo /home/vgpnk/Projects/shokunin --rounds 10- --json` → exit 0 and the JSON document
  is **byte-identical** to the round-23 base output (`cmp` clean; 14 rounds, 9 defects,
  9 corrected, `status=clean`). The spliced round-22 fake hash stays an ordinary
  `unresolved-full-hash` that the committed errata row corrects (the amendment's "historical
  spliced fake absent, not referenced").
- the diagnosis walks run only when a citation is unresolved after both repositories; on the
  real lane and fleet they report no missing object at all (0 `?` lines), in ≈0.01 s and
  ≈0.03 s respectively.

## Retained round-23 grid: measured, with the documented expectation changes

Measured in the scratch clone with the retained grid
(`python3 tests/report-audit/repo-state-grid.py --arm both --current <candidate> --json`,
46 rows, git 2.56.0):

- **candidate arm: 2 violations, 0 tracebacks, 0 timeouts** — the two violations are exactly
  the policy rows below; every other control, contract and fault row passes, including the rows
  that check the refusals, the fault traps and the no-fetch property.
- frozen arm (the grid's own pinned revision `4fe9339f…`): 29 violations, 9 tracebacks,
  2 timeouts — that revision is an r23 mid-round state that no longer satisfies the current
  grid rows, so the r23 tip `0df800e…` (the preregistration base) is the meaningful baseline;
  against that tip the candidate keeps the selftest and the historical ledger byte-identical
  (measured above).

Policy rows that change (documented, not silently):

- `F23-promisor-pack-without-config` — exit 2 **kept**, **reason changed** from
  `promisor pack` to the content-derived
  `unknown: unavailable required object: 6e98d181389d343031fd578c6a775ce0889a8b0d is
  referenced by the history of …/blobless but the repository cannot serve it`. The cited blob is
  referenced by the history and cannot be served, so exit 2 is still the right outcome; the
  refusal now names the object instead of the declaration.
- `F06-lazy-fetch-command` — exit 2 → **exit 1** (`unresolved-full-hash` for the fabricated
  hash, plus the round-23 `landed-unresolved`). The fixture's lane is complete, so the
  fabricated hash is a proved absence; the row's fault check still holds — the
  `core.sshCommand` marker file was **not** created.
- `F27-filter-only-promisor-remote` — exit 1 unchanged (the fabricated hash is a proved
  absence; the trap is not triggered).
- `T01-blobless-partial-clone` — exit 0 (the lane's missing blobs are never cited; the report
  and the cited commits are served).
- `F10/F11/F15/F21/F28` (shallow, grafts, sha256, nested subdirectory, shallow fleet) — exit 2
  with the **byte-identical** reason lines: the history checks run before any availability
  probe.
- `O01-alternates-foreign-object`, `O02-gitfile-redirect` — the inherited *open* rows (the
  alternates/gitfile loophole, explicitly not claimed by this round): the candidate reports the
  local verdict instead of refusing; they stay open findings, not regressions of this repair.
- New rows the repair is expected to satisfy (frozen by GridOracle-2 in
  `build/out/GridOracle/promisor-grid-expectations.json`): a complete marker-only clone with a
  fabricated citation → exit 1; an object missing behind another local branch and cited → exit 2
  (the store-wide walk sees it because every present object is a root); an unrelated hole →
  the ordinary verdict; a missing non-leaf tree plus an unresolved citation → exit 2; the same
  hole with every citation resolved → exit 0; an errata-corrected fabricated hash in a marked
  complete store → exit 0.

## Dissent (recorded, not implemented)

`CritUnknown-2` (independent pre-implementation judgement,
`.ufo/waves/round-24/build/advice/CritUnknown.md`) argues for a **closure completeness
precondition**: "exit 1 when no repository's object closure has a missing object; exit 2 only
when a promisor-backed store's closure actually lacks a reachable object", with the walk over
`--all` refs in both repositories and the promisor-backed set including
`remote.*.partialclonefilter`. That variant refuses a repository that is incomplete but locally
sufficient for the audit (an unrelated historical blob or another branch's missing object),
which the amendment and the Main instruction reject ("a whole pinned-root reachable-tree
precondition is broader than availability of objects actually required by the audit; do not
introduce it merely to retain refusal"), and it re-introduces a metadata classifier the
amendment forbids. The candidate therefore implements the token-specific diagnosis; the two
agree on every expected row listed above (F23 2, F27 1, F06 1 with no fetch marker, T01 0,
marker-only fake 1, other-ref-missing 2). CritUnknown-2's further point that a *short* wrong-type
token inside an incomplete promisor store should be unknown is not implemented: it would make
the verdict depend on the store's metadata, which the amendment forbids, so the round-23
behaviour (a definite `landed-unresolved`) is kept.

## Interface notes for the sibling oracles

- CLI, flags, exit codes and the JSON document are unchanged; no new keys.
- The stable refusal tokens are `unknown: unavailable required object` (citation refusals) and
  `unavailable required object:` (failed reads of required evidence). Both appear only on
  `could-not-evaluate:` lines, never on "partial clone (" or "promisor pack".
- Cross-repository resolution is unchanged (a citation present in either audited repository is
  found); the lookup is never scoped to a reachable set.
- The mutation anchors (candidate path, sha256 and the exact line ranges) were sent to
  `KamaR23-2.MutationOracle-2`.

## Risks and limits

- The diagnosis needs the cited token to be a prefix of a reported missing id (40-hex exact, or
  a 7..39-hex prefix). A short token that matches nothing local is not diagnosed as unknown
  unless a missing id starts with it.
- The store-wide walk enumerates every present commit, tree and tag of a repository; on a very
  large repository this is the most expensive step, and it runs only when a citation is
  unresolved after both repositories.
- An unknown *errata correction* refuses (exit 2); an unknown *citation* cannot be corrected by
  an errata row (unavailable content is not a defect).
- The opaque-hole rule is store-wide: a missing tree in either audited repository makes every
  unresolved citation of that audit unknown. It is deliberately not narrowed to the pinned root,
  because the hole may hide the cited name.
- Not claimed: remote repository completeness, remote abbreviation uniqueness, closure of the
  inherited parser/alternates/gitfile/size-limit findings, live serving capability, or any
  scalar score.

## Installs

None. No pacman transaction, no host service or configuration change, no network access, no
model override. Only the tools already present were used (git 2.56.0, Python 3.14.8).
