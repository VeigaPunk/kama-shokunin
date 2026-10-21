# Source dependencies of the round-24 `error-is-not-a-verdict` append

**Ledger only. No `corpus/SOURCES.md` edit; no row admitted by this seat.**

Base observed: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
Lane HEAD at drafting time: `123640b49f668f1ee6d8412d7232c74484f63c0a`
("round-24: append preintegration local-object oracle correction and qualify
r23 evidence"; touches only `.ufo/waves/round-24/oracle-amendment-1.json` and
`LOG.md`). `git diff 0df800e HEAD -- corpus/knowledge/` is empty — the
knowledge corpus is still at base.
Draft under discussion:
`.ufo/waves/round-24/build/out/ScribeKnowledge/error-is-not-a-verdict.round24-append.md`
(patched copy `error-is-not-a-verdict.with-round24.md`; unified diff
`error-is-not-a-verdict.round24.patch`, 192 lines, `git apply --check` OK).

## Rows the append cites

| id | row status at drafting time | what the append uses it for |
|---|---|---|
| S083 | admitted (`corpus/SOURCES.md:95`), mined 2026-10-21 | `git cat-file --batch-check` prints `missing` for a name that cannot be resolved to an object and `ambiguous` for an ambiguous short name; a process failure is distinguished by exit status, so a failed git call stays an error rather than a missing verdict |
| S089 | admitted (`:101`), mined 2026-10-21, **reopened** this wave by `SrcGlobalGit` | `--no-lazy-fetch` "stops on-demand fetches of missing objects from the promisor remote"; `--no-replace-objects` stops replacement refs; "Neither covers info/grafts or shallow" — isolation is a set of named channels, not a general repository statement |
| S099 | admitted (`:111`), mined 2026-10-21, supersedes S092 | §Handling Missing Objects: git performs "no check as to whether the missing object is actually a promisor object" — a promisor declaration is not an assertion about any particular object's presence |
| S102 | **admitted in the working tree during this wave** (`corpus/SOURCES.md:114`, `corpus/lessons/round-24.md` §Gate) | `git rev-list --missing=print` "is like allow-any, but will also print a list of the missing objects" — encountered-missing output; the append presents it as a bounded probe, explicitly *not* a completeness theorem and not an exit policy |
| S103 | **admitted in the working tree during this wave** (`:115`) | A promisor pack "consist[s] of a `<name>.promisor` file with arbitrary contents" — the marker records packaging provenance, not the absence of anything an audit needs |
| S104 | **rejected in the working tree during this wave** (`:116`), cited as a rejected oracle | `builtin/fsck.c` `mark_object` returns early for a promisor object before the HAS_OBJ check, so a green fsck is not proof that every promised object is locally present; the registry's own flip is to demonstrate required-object availability directly |

S089 was reopened in this wave by seat `SrcGlobalGit`
(`.ufo/waves/round-24/build/advice/SrcGlobalGit.md`,
`.ufo/waves/round-24/build/out/SrcGlobalGit/{pins.json,git-options-excerpt.txt}`):
page `https://git-scm.com/docs/git`, "git last updated in 2.56.0", opened
2026-10-21T17:53:47Z, html sha256 `0dd80d87d78dd275e1e26cad29064a7594b7bc4518fbcebf5ec2474e587ab8e6`,
pinned `/2.56.0` sha256 `336f7842f6015f12fa5fd9f2ed788d4c6d91fc19375a4b50424b5958dfd97f94`,
tag-stripped text identical.

One sentence the append uses is **not** in the admitted S089 `teaches` cell
and is therefore attributed to the reopened page rather than to the row:

> "Useful together with git cat-file -e <object> to see if the object is
> locally available."

(`build/out/SrcGlobalGit/pins.json` → `quotes.no_lazy_fetch_use`, 15 words;
page anchor `#Documentation/git.txt---no-lazy-fetch`.) If L1 wants that
sentence inside the registry, it becomes a **row change** to S089, not a new
row: the page, anchor and quote are already pinned by the reopen. Until
then the append cites it as a page quote with its evidence path and the
`teaches` cell stays as filed.

## Claims the append declines to cite

| claim | seat / artifact | status |
|---|---|---|
| `remote.<name>.partialclonefilter` alone registers a promisor remote (git v2.56.0 `promisor-remote.c`, `promisor_remote_config`, lines 148–163; raw sha256 `175e67e1b2cc62db1ead26007ba1e5502f9b585fd33dbc45b59f9876b34f9bca`) | `SrcPromisorCode` → `build/out/SrcPromisorCode/{SOURCES-candidate-row.md,evidence.md}` | **not admitted.** The working tree's S102/S103/S104 came from `SrcRevList`, `SrcRepoLayout`/`SrcPartial` and `SrcFsck`; the `promisor-remote.c` row was not taken. The append names the gap in its Limits paragraph instead of leaning on the claim |
| `git cat-file -e` exit-status semantics (exit 0 iff the object exists and is valid) | `SrcCatFile` → `build/out/SrcCatFile/{SOURCES-candidate-row.md,catfile-2.56.0.txt:32-35}` | **not admitted.** `corpus/lessons/round-24.md` §Gate records the proposed supersession of S083 as having no premise ("the actual S083 row says 'unresolvable object' and explicitly limits peel-specific semantics"). The append therefore rests on S083's admitted wording and does not cite the `-e` exit status |

Two further negatives are recorded rather than used as support:
`git-fsck`'s manual, installed man page and v2.56.0 adoc contain **no**
statement about promisor objects
(`build/out/SrcFsck/evidence.md`: `promisor|promise|partial clone` → 0 hits
in all three), and `gitrepository-layout(5)` contains no `promisor` string
(`build/out/SrcRepoLayout/evidence.md`: 0 hits in the live page, the 2.49.0
canonical rendering, both upstream adocs and the local man5). Neither tool
is an availability oracle in either direction.

## Awaiting openings

Nothing in the appended section requires a source that has not been opened.
The only claim the append would like to lean on and cannot is the
`partialclonefilter`-only promisor registration noted above; it is named as
a gap, not asserted.

No new page fetch, no network request and no package install was performed
by this seat.

## Verification performed on the artifacts

- `git apply --check` on `error-is-not-a-verdict.round24.patch` →
  **APPLY-CHECK OK** (check only; nothing applied to the repository).
- Byte relation: the base knowledge file is 4704 characters (4716 bytes);
  the patched copy is 15851 characters and is exactly
  `base + "\n" + appended-section`, so the earlier 80 lines are unchanged.
- Production file `corpus/knowledge/error-is-not-a-verdict.md` untouched:
  `git diff -- corpus/knowledge/error-is-not-a-verdict.md` is empty.
