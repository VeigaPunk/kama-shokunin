# Scout — `objects/info/alternates` (clone --shared / --reference)

Channel: repository-local git object-store borrowing, as probed by
`tools/report-landing-audit.py`. Base line cited below is the frozen blob
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`
(sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`,
no isolation flags). The lane working tree changed concurrently during this scout,
not by me (`git status` → `M tools/report-landing-audit.py`,
sha256 `b6064767b1ce6b8833f977bb9fdfb45702c70427a9a792961ed3cc2636d89bda`,
contains `GIT_ISOLATION`); I snapshotted it and reran the whole grid against it —
output was **byte-identical** (`diff out-base.log out-worktree.log` empty). So the
candidate direction does not touch this channel.

All fixtures ran only in `/tmp/kama-r23/CloseKama22.ScoutAlternates` (fresh repos,
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, git 2.56.0, no network).
No audited repo was written. The real lane and fleet repos were read only:
neither has `<gitdir>/objects/info/alternates`, so current ledger rows are unaffected.

## Verdict

**affects-verdict** — one line in `<repo>/.git/objects/info/alternates`
pointing at an unrelated object store flips a fabricated citation from
`failed` (exit 1) to `clean` (exit 0). No process execution, and the crash
variant degrades to a typed `could-not-evaluate` (exit 2), not a traceback.

Mechanism (base blob lines):

- `lookup()` (`:100-132`) asks `git cat-file --batch-check` (`:114`) per repo and
  labels any object git can resolve as `found`; git resolves through
  `objects/info/alternates`.
- `audit_round()` (`:258-296`) turns that into `unresolved-full-hash`,
  `landed-unresolved`/`landed-ambiguous`; `apply_errata()` (`:343-357`) uses the
  same lookup for errata corrections, so a correction hash borrowed from another
  store also becomes valid.
- `git_env()` (`:79-84`) removes inherited `GIT_*` and nulls user/system config,
  but says nothing about the repo's object store; `git()` (`:87-97`) adds no
  object-store isolation. The docstring promise at `:80-81` ("neither the audited
  repos … can be redirected") is false for this channel.

## Observed fault grid (base blob; same under the current candidate snapshot)

Fixture: `out/CloseKama22.ScoutAlternates/fixture.sh`; raw logs `out-base.log`,
`out-worktree.log`. Setup: unrelated `donor` commit `e8c46f47…`, confirmed absent
from lane (`git -C lane cat-file -e` → rc 1); lane `round-1: work` commit
`16fc48b7…`; fleet report `.ufo/reports/round-1/kama.md` citing both hashes.
Audit invocation throughout:
`python3 audit-base.py --lane-repo lane --fleet-repo fleet --branch master --lane kama --rounds 1 --no-errata`

| Row | Repo-local state | exit | defect output |
|---|---|---|---|
| A control | no alternates file | 1 | `unresolved-full-hash e8c46f47…` + `landed-unresolved e8c46f47…`, `status=failed` |
| B | `lane/.git/objects/info/alternates` → `/tmp/…/donor/.git/objects` (absolute) | **0** | `defects=0 … status=clean` |
| C | same line in `fleet/.git/objects/info/alternates` | **0** | `defects=0 … status=clean` |
| D2 | relative line `../../../donor/.git/objects` in lane (relative to the object db, per doc) | **0** | `defects=0 … status=clean` (separate run; the fixture's row D uses the wrong depth `../../` and stays rc 1) |
| F | inherited `GIT_ALTERNATE_OBJECT_DIRECTORIES=` (stripped by `git_env`) | 0 | same false clean |
| G | alternates → nonexistent dir | 1 | identical to control |
| H | alternates → regular file | 1 | identical to control |
| I | alternates → store whose loose object bytes are corrupt | 2 | `could-not-evaluate: git cat-file --batch-check …: rc=128 … fatal: loose object e8c46f47… is corrupt` (no traceback) |
| J | audit against `git clone --shared lane sdclone` (file intact) | 1 | identical to control; genuine lane citation resolves through the borrowed store (`required=1`, no defect for `16fc48b7…`) |
| J2 | same shared clone, alternates file emptied | 2 | `could-not-evaluate: git rev-parse --verify master^{commit} … rc=128 fatal: Needed a single revision` |

Notes:
- Row D with `../../donor/…` stays rc 1 because that resolves to `lane/donor/…`;
  the correct depth (D2) reproduces the flip. Relative lines are legal and are
  resolved against the object database, not the repo root.
- Extra-dir warning test: `GIT_ALTERNATE_OBJECT_DIRECTORIES=/nonexistent` prints
  `error: object directory /nonexistent does not exist; check .git/objects/info/alternates`
  to stderr but returns rc 0 and still resolves the donor object. The audit's
  `git()` captures and discards stderr when rc == 0, so such warnings are invisible
  in audit output.
- No git switch disables the file: `GIT_ALTERNATE_OBJECT_DIRECTORIES=` (empty)
  does not suppress `objects/info/alternates` (row E2: donor still prints
  `commit 118`); `--no-replace-objects --no-lazy-fetch` leave it in force (E4);
  `git-cat-file(1)` and `git-rev-parse(1)` document no alternates option
  (local man pages, 2.56.0). The only kill switch is emptying/removing the file
  or not honoring it at all — see below.
- `objects/info/http-alternates` is HTTP-fetch-only per the layout doc and was not
  exercised; it is not a local lookup channel.

## Why "disable alternates" is not viable

`git clone --shared` / `--reference` create exactly this file and the clone starts
with no objects of its own. Observed: `cat sdclone/.git/objects/info/alternates` →
`/tmp/kama-r23/CloseKama22.ScoutAlternates/lane/.git/objects` (absolute; same for a
`--reference` clone). Emptying it makes the audit fail **before any round is read**,
at the first `git rev-parse --verify master^{commit}` peel (row J2, both scripts):
the ref value exists but its commit object lives only in the donor. With the file
intact the same shared clone audits normally and correctly resolves the lane's real
citation through the borrowed store. So a blanket "ignore/refuse alternates" rule
turns every legitimate scratch clone into exit 2, which contradicts the stated
intent that `--shared` clones remain legitimate.

A `--dissociate` clone (or any ordinary clone, including `--no-hardlinks`) has no
alternates file and materializes its own objects — observed: `git clone --no-hardlinks donor nhl`
and plain `git clone donor plain` both lack `objects/info/alternates` and carry 3 own
object files; `--shared --dissociate` likewise lacks the file. That is the legitimate
way to get a self-contained repo for a standalone verdict.

## Honest limit wording (proposal)

For `git_env()`/module docstring (replace the current "neither the audited repos …
can be redirected" claim):

> No inherited `GIT_*` variables and no user/system config. This does not isolate
> the audited repositories' object stores: objects reachable through
> `objects/info/alternates` (created by `git clone --shared`/`--reference`) resolve
> as if local, and no supported git switch ignores them. A verdict therefore trusts
> every object store the audited repositories name.

For the verdict/summary surface:

> `clean` means no defect against the object stores visible to the audited
> repositories. A borrowed store named in `objects/info/alternates` widens
> "resolvable" and is part of the trust base; run the audit on the canonical
> repository (or a `--dissociate` clone) for a self-contained verdict.

If the round prefers to put this channel inside the measured grid rather than the
limit note, two coherent designs exist; neither is prototyped here:
(a) **surface, don't refuse** — detect a nonempty `<gitdir>/objects/info/alternates`
and mark the result/summary as borrowed-store-scoped (keeps shared clones working);
(b) **judge by reachability** — accept a citation only if reachable from the audited
refs instead of merely present; graph walks resolve through alternates, so shared
clones keep working. (b) is a semantic change to `lookup()` and would also close the
pre-existing dangling-object widening noted below. Do not silently scrub the file:
that breaks shared clones (J2).

## Trust boundary / adjacent observed fact

- Alternates is the same trust class as replace refs: it needs write access to the
  audited repo's git dir (or choosing a shared clone as `--lane-repo`). Unlike
  replace refs, it can make an arbitrary 40-hex resolve with no object in the
  audited store at all.
- Even without alternates, `lookup`'s `found` already means "present in the object
  store", not "in the audited history": a commit left dangling by
  `git reset --hard HEAD^` still answers `<sha> commit 171` to
  `cat-file --batch-check` (scratch `dangle` repo). Alternates only widens the store;
  the wording above should say "object store trust", not "alternates only".

## Did not verify

- Other git versions/platforms; partial-clone promisor interaction with alternates;
  `--reference-if-able`; linked worktrees/`GIT_COMMON_DIR`.
- `objects/info/http-alternates` local behavior (doc says HTTP-only).
- Whether the reachability-based `lookup` would leave the historical ledger and the
  50-case selftest unchanged (not implemented).
- Real lane/fleet repos only inspected for the alternates file (both absent); no
  audit run against them.

## Files written

- `.ufo/waves/round-23/build/advice/ScoutAlternates.md` (this report)
- `.ufo/waves/round-23/build/out/CloseKama22.ScoutAlternates/fixture.sh`
- `.ufo/waves/round-23/build/out/CloseKama22.ScoutAlternates/out-base.log`
- `.ufo/waves/round-23/build/out/CloseKama22.ScoutAlternates/out-worktree.log`

No tools installed. No REA devices. No subagents.
