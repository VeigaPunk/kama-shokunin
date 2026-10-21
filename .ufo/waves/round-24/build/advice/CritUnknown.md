# CritUnknown — unknown object absence vs missing promised evidence (round 24)

## Qualification appended 2026-10-21 18:11 UTC to oracle-amendment-1 (`123640b`); earlier sections are kept unchanged

I accept the amendment's scope. Only unresolved tokens refuse; an unrelated hole is no blanket
precondition; P07 = 2, P08 = 1, P08b = 1; abbreviation uniqueness against remote-only objects is not
claimed. This supersedes my all-refs-closure gate (ruling v3) as a precondition.

**Qualification (soundness bound on token membership):** the membership test is exact only when every
missing object it lists is a **blob**. A missing **tree** or **commit** hides the names beneath it,
so `--missing=print` cannot list a cited object under that hole, although local history names it there.
Measured with `out/CritUnknown/hidden_probe.py`, output in `hidden-output.txt`; the fixture is
independently built from the grid helpers. A promisor lane cites blob `6e98d18…` at `d/f`:

| Hole | `--missing=print-info` lists | Cited token listed? | Full twin | Token-membership rule |
|---|---|---|---|---|
| blob only | `?6e98d18… path=d/f type=blob` | yes | 0 | 2 (correct) |
| tree `d` and its blob | `?a33984f… path=d type=tree` only | **no** | 0 | **1, a false failure** (frozen also 1) |

In the tree-hole case, local history (commit, then tree `d`) names the cited blob, so this is exactly
"a locally unresolved citation known to name unavailable referenced local content", the amendment's
expectation 3. The membership test cannot see it.

**Smallest sound refinement (still no closure precondition):**
- An unresolved token is could-not-evaluate if any of these hold:
  - it equals a listed missing id;
  - it is a prefix of a listed missing id (for checkable abbreviations);
  - **any listed missing object has `type=tree` or `type=commit`**, since `--missing=print-info` gives types in git 2.56.
- Only blob-only holes, such as `--filter=blob:none` clones and P08, keep the exact per-token verdict.
- It fires only when (a) a citation is unresolved and (b) a non-leaf object is missing, so a resolved
  audit and blobless clones are never refused for an unrelated hole.
- Rows to add: P09 (tree hole hiding the cited blob, expected 2) and P09b (tree hole plus an unrelated
  fabricated token, expected 2, undecidable locally). Mutant: "membership ignores non-blob holes",
  killed by P09.
- If the authority declines the refinement, P09 must be declared as a not-claimed limit next to remote abbreviation uniqueness.

## Anchor resolution (parent query: BASE :12-19 plus the corrected-fake witness)

**Agreed:** metadata does not change the local contract. BASE `:12-19` defines both defects by
local object membership ("no git object in the lane or fleet repo", "no commit in either repo"),
with no claim about a remote object universe.
- When every object that the lane's and fleet's refs reach is stored locally, an absent token is
  a defect and errata apply. The witness below measures exactly that: the complete promisor-marked
  lane gives 0 with 9/9 corrected, identical to the unmarked twin.
- An "unknown leads to could-not-evaluate" rule that fires in this case contradicts both the anchors
  and the witness. It is the self-imposed prereg row 4, and it is not supported.
- In the candidate, metadata never decides a verdict. It only scopes where the closure check runs,
  which keeps non-promisor audits byte-identical.

**The one place the anchors alone do not decide:** stores that lack an object their own history names
(F23: `fsck` reports a "broken link from tree a33984f… to blob 6e98d18…").
- Read literally, `:12-13` gives F23 exit 1 (`[unresolved-full-hash]`, frozen's answer).
- BASE nonetheless already refuses such shapes. `:43-44` lists "shallow/grafted … repository" as
  could-not-evaluate, and `:439` gives the reason: "visible history is not its object history". `:45` adds
  "Errors are never verdicts".
- F23 has that shape, and its full twin is 0, so exit 1 would be a false failure. F23 = 2 rests on that
  principle, not on metadata and not on the prereg unknown rule.
- If the authority declines to extend `:43-44`/`:439` to promisor-backed stores missing a
  reachable object, the anchors give F23 = 1, and `out/CritUnknown/local-contract.patch` (unmeasured)
  implements that. Either choice keeps the witness at 0.

## Historical witness (CritScores contradiction), measured

The witness is the real lane, rounds 10-22, audited against the real fleet (read-only).
Script: `out/CritUnknown/witness.sh`; output: `witness-output.txt`.
- Errata row 3 (`registry/report-landing-errata.tsv`) corrects
  `unresolved-full-hash 0957ce619789d13d894ef21bc863486bcb35b56c`, a spliced hash that is absent
  from both the lane and the fleet.
- The marked copy is a scratch clone of the lane, repacked, with a `.promisor` file next to its pack.
  The rev-list closure check over all refs finds 0 missing objects. The spliced token is
  `missing` in both the marked copy and its unmarked twin.

| Tool on | Real lane | Unmarked twin | Complete promisor-marked |
|---|---|---|---|
| r23 (`0df800e`) | 0, 9 defects / 9 corrected | 0, 9/9 | **2** "partial clone (promisor pack)" |
| candidate (ruling v3) | 0, 9/9 | 0, 9/9 | **0, 9/9** |

A literal prereg-row-4 implementation (an absent citation in any promisor-backed repository is
could-not-evaluate) raises on `0957ce61` before errata are applied. It therefore gives exit 2 here,
just as r23 does: that is the contradiction CritScores found. Ruling v3 gates the unknown state on
**incomplete** closure, so a complete store keeps the local-object answer. The defect is reported
and then corrected by the errata row, giving exit 0, identical to the unmarked twin. Real repositories
were not written: no `.promisor` file exists in the lane's or the fleet's `objects/pack`, and the clone
passed the `--show-toplevel` guard.

**Complete closure plus an unrelated absent token is an ordinary failed verdict. Incomplete
closure in a promisor-backed repository plus an absent token is could-not-evaluate (exit 2).
F23 is exit 2. F27, F06 and the marker-only fabricated case are exit 1.**

1. **Complete closure means local absence is a failed verdict, whatever the metadata says.** Closure is
   complete when `rev-list --objects --no-object-names --all --missing=print` prints no `?` line in
   either audited repository. The local store then holds every object its refs reach, which is
   exactly the store of a full clone with the same refs. The local-membership answer of the
   defect definitions (`tools/report-landing-audit.py:12-19`) and the full-clone answer coincide,
   so nothing is guessed. Promisor metadata is only a declaration and does not establish
   incompleteness (prereg row 6). Applying prereg row 4 literally ("any promisor-backed
   repository leads to could-not-evaluate") is an unnecessary refusal here. Report it as an
   original expectation not met, with a prospective correction.
2. **Incomplete closure in a promisor-backed repository means an unresolved citation is
   could-not-evaluate.** In F23 (`repo-state-grid.py:195-213`), `fsck` reports `broken link from tree
   a33984f… to blob 6e98d18… / missing blob 6e98d18…`. The rev-list check reports
   `?6e98d18… path=f type=blob`, which is the cited token (`out/CritUnknown/f23-output.txt` plus this
   check). The lane's own tree names the object, so "no git object in the lane repo" is
   contradicted by local evidence, and "found" cannot be verified locally. That makes exit 2 the
   only justified answer.
   - The basis is closure, not "required" evidence: the auditor never reads that blob.
   - Required-object absence is a separate exit 2, through git's non-zero exit with lazy fetch off.
   - The full-clone twin of F23 is 0 and frozen's exit 1 was a false failure; neither is evidence for exit 1.
3. **Closure must cover all refs, not only the selected roots.** An object reachable only from
   another local branch or tag is present in a full clone with the same refs, and citing it there
   is clean. A selected-root check would wrongly fail it.
4. **Scope.** The rule applies only when the repository is promisor-backed by any of:
   - a `.promisor` file with a sibling `.pack`;
   - `extensions.partialclone`;
   - `remote.*.partialclonefilter`;
   - `remote.*.promisor` set to true.

   A non-promisor repository with missing objects (for example the corrupt `Lbare`, where `fsck`
   reports `missing commit` and exits 2) keeps r23 behavior, so the non-promisor path is unharmed.
   Git itself agrees on the promisor/non-promisor split: on the configured promisor fixture `Lc1`,
   `fsck` reports the missing commit as promised (rc 0).
5. **Inside the could-not-evaluate regime** (an incomplete promisor repository), these still bind:
   - K1: a 40-hex token found locally as a blob or tree is a decisive wrong type, so `landed-unresolved` (exit 1).
   - K2: a short token that is not found, is ambiguous, or has the wrong type is exit 2.
   - K4: an unknown citation dominates errata and other defects (exit 2).
   - K5: git exit codes stay strict; no `--exclude-promisor-objects`.
   - K6: check both repositories into a list before taking `any()`.
6. **Not adopted:** a narrower rule for incomplete stores where every missing object is a blob
   (`--missing=print-info` gives `type=`). There, a token that matches no missing id or prefix could
   be failed. Missing trees and commits hide the names beneath them, and the prefix handling adds
   complexity, so this is deferred.

| Row | r23 | Ruling v3 | Basis |
|---|---|---|---|
| F23 (cited blob, reachable, missing) | 2 | **2**, reason text changes to "citation unknown" | point 2 |
| F27 (filter-only remote, complete, fabricated hash) | 1 | 1 | point 1 |
| F06 (partialclone config, complete, fabricated hash) | 2 | **1** `[landed-unresolved, unresolved-full-hash]`, lazy-fetch marker absent | point 1 |
| T01 (blobless clone hydrated by checkout, complete) | 2 | **0** | point 1 |
| C09, C10 (not promisor-backed) | 0 | 0 | point 4 |
| Marker-only complete lane, fabricated hash (new row) | 2 | **1** `[unresolved-full-hash]` | point 1 |
| Cited object missing only behind another ref (new row) | — | **2** | point 3 |
| Required commit/tree/report/SOURCES/errata missing | 2 | 2 (git exit code) | point 2 |

Mutants to add, each killed by the row named:
- closure over selected roots only, killed by the new other-ref row;
- `partialclonefilter` dropped from the promisor check, killed by an incomplete filter-only row
  (F27 alone does not kill it, because it is complete);
- closure check skipped (metadata alone decides), killed by F06 or the marker-only row (1 becomes 2);
- unknown citations not dominant, killed by a K4b row.

Implementation status:
- **`out/CritUnknown/candidate.patch`** implements exactly this ruling: the `promisor_backed()` check
  above, an all-refs `--missing=print` closure check, `promised` threaded into every `lookup()`,
  K1, K2, K4 and K6. It is reinstated. It is unmeasured.
- **`out/CritUnknown/local-contract.patch` is withdrawn.** My v2 ruling (F23 = 1) read "no git object in
  the repo" as membership in the store. It ignored that F23's own tree names the cited object.
- I checked the mutant anchors against the candidate. Only M14 and M22 (the two promisor
  `raise` lines, which are now `return True`) no longer match. M13, M27, M29 and M30 match exactly
  once: the grafts variable name and the `for repo in (lane_repo, fleet_repo):` loop are kept, and the
  loop evaluates every repository before combining (K6). `isolation-mutants.py` exits 2 until M14 and
  M22 are re-anchored to the `return True` lines, or retired with documentation.

## FINAL DECISION under the confirmed local-object contract (supersedes both sections below)

**A missing citation is a failed verdict whenever every required read succeeds.
Promisor metadata and object closure do not enter. Expected F23: exit 1, kinds
`[unresolved-full-hash]`.** This holds because the contract defines the defect, not
because any closure is complete. A "complete selected-root closure" gate would **not**
give F23 exit 1; see point 3.

Source evidence (`tools/report-landing-audit.py` at `0df800e`, identical at `d1b9d95`):
1. The contract defines defects by local membership. `:12-13` says `unresolved-full-hash` means "a 40-hex token
   … that is no git object in the lane or fleet repo". `:17-19` says `landed-unresolved` means "… is no commit in either repo".
   `:49` neutralizes lazy fetch, so "in the repo" means the local store. `:53-54` adds that borrowed objects "still
   resolve as local". Exit 2 (`:42-45`) covers unusable git, unreadable input or a refused repository shape, never citation
   absence. The only text that makes promisor absence non-evidence is r23's refusal (`:440-441`, `:450-465`).
   That is the policy being calibrated, not the defect definitions.
2. Required evidence is separate, and git enforces it with lazy fetch off.
   `probe-output.txt` shows non-zero exits for:
   - a missing ancestor commit (`log` rc 128);
   - a missing fleet tree (`log --diff-filter=A` rc 128);
   - a missing subtree (`ls-tree` rc 1);
   - a missing report blob (`show` rc 128);
   - a missing SOURCES blob (`cat-file blob` rc 128).

   `git()` turns rc != 0 into exit 2 (`:128-130`). Citation targets are tested for membership, never read, so they are not required evidence.
3. **F23 is not closure-complete, even at the selected root.** The fixture (`repo-state-grid.py:195-213`)
   cites `lc:f`, the lane tip's own blob, and its premise is that this blob is absent. Measured:
   `rev-list --objects --no-object-names --missing=print master` on the F23 clone gives exactly `?6e98d18…`, which is the
   cited blob. A selected-root gate therefore yields F23 = 2. Only the pure local contract yields 1.
   The required reads all succeed: lane commits and trees, the complete fleet, no SOURCES.md, `--no-errata`.
   Frozen measured `(1, ['unresolved-full-hash'])` (`f23-output.txt`), which is the contract answer.
4. My earlier "all-ref closure" decision came from the full-twin oracle, i.e. prereg row 1's wording; under that oracle F23's twin
   is 0. The authority's contract is local membership, not the twin, so that decision and `candidate.patch` are
   **withdrawn; do not integrate**. Prereg row 4 (exit 2 for a missing citation in a promisor-backed
   repository) is contradicted by this contract. Report it as an original expectation not met, with the correction appended.

Expected rows under the local contract (derived from source and fixture premises, not from running a candidate):

| Row | r23 | Local contract |
|---|---|---|
| F23 promisor pack, no config, cited blob absent | 2 | **1** `[unresolved-full-hash]` |
| F06 partialclone config, fabricated `fake2` cited in Landed | 2 | **1** `[landed-unresolved, unresolved-full-hash]`, lazy-fetch marker absent |
| F27 filter-only remote, fabricated cited | 1 | 1 (unchanged) |
| T01 blobless clone, all cited present | 2 | **0** |
| C09, C10 | 0 | 0 |
| Complete lane, paired `.promisor` only, fabricated cited | 2 | **1** `[unresolved-full-hash]` |
| Required commit/tree/report/SOURCES/errata object absent | 2 | 2 (git rc) |

Consequences for my earlier findings:
- K1 and K2 need no special handling: a wrong-type or short-collision answer is the local answer, so `landed-unresolved` is correct.
- K4 and K6 do not arise, because there is no unknown state and no flag.
- K5 still binds: keep `git()` strict, and never use `--exclude-promisor-objects`, `--missing=*` or an rc-tolerant `ls-tree`.
- K3's predicate question disappears, because no metadata is read at all.

Minimal patch: `out/CritUnknown/local-contract.patch` (39 changed lines). It deletes the promisor-pack and
promisor-config refusal and the now-unused `git_bool`, and states the contract in the docstring. It is unmeasured.

Mutation harness impact: M14, M22, M27 and M29 anchor on the deleted code. `isolation-mutants.py:119-122` then
exits 2 ("pattern matches 0 times") until those four are retired, and the retirement must be documented.
M02 (drop `--no-lazy-fetch`) is kept and gets stronger: F06 and F27 now reach the citation lookup, so dropping the flag
runs the fixture's `core.sshCommand` and the marker kills the mutant.

## DECISION (parent query, supersedes K3's F27 change and the "any promisor" scope below)

Use closure over **all refs** in both repositories, not only the selected roots. A promisor-backed
repository in which no object reachable from any ref is missing gives ordinary local-absence
verdicts. "Unknown" (exit 2) applies only when a promisor-backed repository lacks an object
reachable from some ref.

Why: the oracle is the otherwise identical full clone. A full clone with the same refs holds
exactly the objects those refs reach. If every one of them is present locally, every
`cat-file` answer matches the twin's, so the verdicts must match too. That includes K1, K2 and
tag peels, because a commit that only the remote holds is absent from the twin as well. This
matches the local two-repository contract and prereg row 6 ("metadata-only declarations do not
establish incompleteness"). Prereg row 4 must be read as "promisor-backed **and incomplete**".

Selected roots are not enough. An object reachable only from another local branch or tag
is present in the twin, where a citation of it is `found` (clean). Checking only the audited roots
would call it absent and give a false exit 1. This was derived from the twin definition; no
fixture was built.

**Evidence** (`out/CritUnknown/f23_probe.py` -> `f23-output.txt`; it uses the grid's own builders):

| Case | frozen r22 | r23 | full twin | all-ref closure |
|---|---|---|---|---|
| grid F23 as built (cited blob absent from blobless clone) | 1 | 2 | **0** (the origin lane holds the blob) | `?6e98d18…` missing |
| complete lane, paired `.promisor` only, fabricated hash cited | 1 | **2 (harm)** | 1 `unresolved-full-hash` | complete |

The parent's premise does not hold for grid F23. F23 cites a real blob that the clone lacks, so
it is not complete. Its full twin is clean, which makes frozen's exit 1 a **false failure**,
and r23's exit 2 correct. F23 stays exit 2 under the closure rule. The case the parent
describes (marker only, complete, fabricated hash) is real r23 harm. The closure rule restores
exit 1 there.

Grid consequences (this replaces the list further down):
- F23 stays 2, with the reason text changed to "citation unknown".
- F27 **stays 1**: the lane is complete and the fabricated hash is absent in the twin as well.
- F06 goes from 2 to 1, with the lazy-fetch marker still absent.
- T01 goes from 2 to graded control 0.
- New control: the marker-only complete lane citing a fabricated hash expects 1 `unresolved-full-hash`.
- New row: a lane missing an object reachable only through another ref, citing that object, expects 2.
- Mutant: "closure over selected roots only" must be killed by that new row.

Cost: `rev-list --objects --all --missing=print` took 0.24 s wall for both real repositories
together (6,044 and 9,423 objects, 0 missing). It runs only for promisor-backed repositories,
so non-promisor audits are unchanged.

Candidate updated (`out/CritUnknown/candidate.patch`, +73/-29). The new `promisor_backed()`
holds the K3 predicate. `check_history_repo` returns whether the repository is promisor-backed
and lacks a reachable object, using `rev-list --objects --no-object-names --all --missing=print`
(no path text to parse) with a strict exit-code check. It never uses `--exclude-promisor-objects`
(K5). Non-promisor repositories with corruption keep their r23 behavior (out of scope).

Verdict: the r24 repair is sound only if three distinctions are kept that git's
`cat-file --batch-check` stdout does not make. (1) "missing" is printed identically
for a never-existing object, a promised-but-absent object, a wrong-type peel and a
tag whose target is absent. (2) Local wrong-type is decisive only for a 40-hex name.
(3) An unknown must dominate every verdict, including errata outcomes. Required
evidence needs no metadata refusal: with `--no-lazy-fetch`, every required read
probed fails git (rc != 0). The r23 metadata refusal can therefore go, provided rc
stays strict. Candidate patch:
`.ufo/waves/round-24/build/out/CritUnknown/candidate.patch` (unverified: not run, per contract).

Base: lane tool at `0df800e` (lane HEAD `d1b9d95` only adds preregistration/LOG; tool identical).
git 2.56.0. Fixtures: hand-built offline promisor repos (pack-objects + `.promisor` +
config, `remote.origin.url=/nonexistent`), no transport. Evidence:
`out/CritUnknown/probe.sh` -> `probe-output.txt`; `out/CritUnknown/lookup_probe.py` -> `lookup-output.txt`.
Scratch: `/fast/scratch/hyaku/kama-r24/CritUnknown/{probe,collide,clone}`. No installs.

## Axes
A1 correct verdict on complete promisor-marked repos (= full clone) · A2 no guessed
absence (unknown -> exit 2) · A3 required-evidence availability -> exit 2 · A4 cross-repo
resolution and wrong-type unchanged · A5 non-promisor no-harm · A6 isolation/timeout kept.

## Counterexamples (with evidence)

**K1 — wrong-type and promised-absent are indistinguishable in peeled stdout (A1, A4).**
`probe-output.txt` "batch-check peel Lmark": `5626abf…^{commit} missing` (blob),
`1572c24…^{commit} missing` (tree), `0123…^{commit} missing` (never existed); "Ltag":
`36d03b6…^{commit} missing` (tag present, target commit promised-absent). Only stderr
(`expected commit type, but the object dereferences to blob type`) or the bare pass
(`blob 4`) differs. `tools/report-landing-audit.py:159-160` discards both. A patch that
maps peeled "missing" in a promisor repo to unknown turns a wrong-type 40-hex Landed
citation into exit 2, whereas the full twin gives `landed-unresolved` exit 1. That breaks the
"exact same findings" expectation. Correction: carry the bare type. A full 40-hex name found
locally as blob/tree in ANY audited repo is decisive (an object name fixes its type), so it
stays `landed-unresolved`. Cross-repo check: `lookup((Lc1, Lfull), BA, "^{commit}") ->
missing` (`lookup-output.txt`), which must stay a defect even with Lc1 promisor-backed.

**K2 — a local wrong-type abbreviation is NOT decisive in a promisor repo (A1, A2).**
`lookup-output.txt` collision section: the blob `1a9a4fe…` and the commit `1a9a445…` share the prefix `1a9a4`.
The full clone gives `bare: ambiguous` and `peel: found`, because `^{commit}` disambiguation prefers the commit.
After the commit becomes promised-only, the same lookup gives `bare: found` and `peel: missing`, with stderr
`expected commit type … blob`. That is byte-identical to a true wrong-type citation. Treating the
abbreviation as a decisive wrong type gives a false exit 1 where the full clone is clean. Likewise,
"ambiguous bare + missing peel" can become `found` once a promised commit exists. Correction: in
promisor-backed audits, every short token that is not `found` (missing, ambiguous, or wrong-type)
is unknown, exit 2. The 5-hex demo exercises the same git path as 7+ hex. The 7-hex length is
[INFERENCE]: the collision cost was not built.

**K3 — `F27` is guessed absence today, and the predicate must include `partialclonefilter` (A2).**
`tools/report-landing-audit.py:462-464` checks only `extensions.partialclone` and
`remote.*.promisor`. The F27 fixture (`tests/report-audit/repo-state-grid.py:482-497`) proves
that a filter-only remote is a promisor remote, because git lazy-fetches through it. Yet the grid grades F27 as exit 1 with
`landed-unresolved`/`unresolved-full-hash` for an absent fake 40-hex (`repo-state-grid.py:674-675`). Under prereg
row 4, this must become exit 2. A patch that keeps the r23 predicate leaves F27 at exit 1 and
F23 (a `.promisor` pack with no config) at exit 2: two authorities disagree on what "promisor-backed" means.
Correction: the predicate is a `.promisor` file with a sibling `.pack`, OR `extensions.partialclone`
(any value), OR `remote.*.partialclonefilter` (any value), OR `remote.*.promisor` true.
C09 (`promisor=false`) and C10 (orphan marker) stay non-promisor, so the controls keep exit 0.

**K4 — errata paths convert unknown into a verdict (A2).**
(a) `tools/report-landing-audit.py:404-407`: if an errata correction commit is absent from a
promisor repo, `errata-invalid` gives exit 1. It must be unknown, exit 2.
(b) A row correcting `unresolved-full-hash FAKE` where FAKE is absent from a promisor repo: the full
twin is clean (exit 0, C11 shape). If the patch records FAKE as "unknown, not a defect", the row becomes
`errata-unmatched` and exit 1. The truth is in {0, 1}, so the answer is exit 2.
(c) A definite `landed-omitted` plus one unknown citation: exit 1 would be built on partial evaluation.
Correction: an unknown raises EvalError (exit 2) and dominates defects and errata. Raising inside
`lookup()` covers all three call sites (`:325`, `:336`, `:404`) with no JSON schema change.

**K5 — "tolerate the gap" git modes silently truncate (A3).**
`rev-list --exclude-promisor-objects main` on Lc1 (a missing ancestor) returns **rc=0 with empty output**
(`probe-output.txt`), because every object lives in the promisor pack. `round_commits` would then see 0 commits,
yielding no `landed-omitted` and a false clean. `rev-list --missing=print` returns rc=0 and only `?`-marks the
gaps. Strict reads fail correctly: `log` gives rc=128 "Failed to traverse parents" (but prints partial stdout
first); `log --diff-filter=A` with a missing tree gives rc=128 "unable to read tree"; `ls-tree` with a missing
subtree gives **rc=1 with partial stdout** (round-2 silently dropped from the listing); `show HEAD:path` with a
missing tree gives rc=128 with a misleading "exists on disk, but not in 'HEAD'"; `cat-file blob` gives rc=128.
A blobless fleet still yields the cutoff (`3000`, rc=0), because tree diffs need no blobs.
Correction: keep `git()`'s rc check (`:128-130`) for every call. Never use `--exclude-promisor-objects`,
`--missing=*`, or rc-tolerant `ls-tree`. Never read "path does not exist" as "report absent" or
"legacy, no SOURCES" (`load_source_urls` `:260-262` would silently reclassify URL hashes).

**K6 — `any()` short-circuit skips the fleet's refusals (A6).**
If `check_history_repo` returns a promisor flag and the patch writes
`promised = any(check_history_repo(r) for r in repos)`, a promisor lane stops the generator. The
fleet's shallow/grafts/sha1/top-level checks never run, so F28 (shallow fleet) would be audited with a wrong cutoff.
Correction: evaluate both repos into a list, then take `any`.

## Justified refusals (exit 2), and what must stay a verdict

| Situation | Outcome |
|---|---|
| Required commit/tree/blob/report/SOURCES/errata object absent | exit 2, via git rc != 0 under `--no-lazy-fetch` |
| Citation not found in any repo, some repo promisor-backed | exit 2 |
| Short citation wrong-type/ambiguous, some repo promisor-backed | exit 2 (K2) |
| 40-hex tag citation whose peel fails, promisor-backed | exit 2 (target may be promised) |
| 40-hex citation found as blob/tree in any repo | `landed-unresolved` exit 1 (decisive) |
| Citation found as commit in the other repo | found (exit 0 path) |
| Complete promisor-marked repo, all cited found | same verdict as full twin |
| Uncited pre-cutoff lane commit, promisor-marked | `landed-omitted` exit 1 |
| No repo promisor-backed | unchanged from r23 (A5) |

Declared tradeoff (not fixable locally; must go in not_claimed/docs): a 7+-hex abbreviation
found uniquely in a promisor repo may collide with a promised-only object. The full twin would say
`landed-ambiguous` where we say found. Ambiguity against unfetched objects is undetectable.
Open [INFERENCE]: `.promisor` packs inside an alternates donor are not scanned. Either scan
the alternates' pack dirs or keep alternates explicitly unclaimed, as at `:53-55`.

## Grid expectation changes and rows to add
- `F27-filter-only-promisor-remote`: 1 -> 2, plus a REASONS pin (the "citation unknown" text). This is a policy change: document it.
- `F06-lazy-fetch-command`: stays 2. The reason changes from "partial clone" to the unknown text, and the marker must stay absent.
- `F23-promisor-pack-without-config`: stays 2. The reason changes from "promisor pack" to the unknown text (the cited blob is absent everywhere).
- `T01-blobless-partial-clone`: tradeoff 2 -> graded control 0, matching frozen.
- Add: 40-hex blob citation in a promisor lane -> 1 `landed-unresolved`; the K2 collision -> 2; Lc1 cited
  C1 resolved by the full fleet -> 0; a tag citation whose target is promised -> 2; the K4a/b/c rows -> 2.
- Mutants that must be killed: drop `partialclonefilter` (F27 -> 1); treat short wrong-type as decisive (K2 -> 1);
  make unknown non-dominant (K4b -> 1); `any()` generator (shallow fleet + promisor lane -> verdict);
  `--exclude-promisor-objects` in `round_commits` (missing-ancestor omission -> 0).

## Candidate (smallest safe correction)
`out/CritUnknown/candidate.patch` changes only `tools/report-landing-audit.py` (+61/-29):
- `check_history_repo` keeps the shallow, grafts, sha1 and top-level refusals, and returns the promisor predicate (K3) instead of raising.
- `run` checks both repos (K6) and threads `promised` into `audit_round` and `apply_errata`.
- `lookup` reuses the existing bare pass to record types (no extra git calls) and raises EvalError for any unsettled token when `promised`, except 40-hex blob/tree (K1, K2, K4).
- The module docstring is updated.

Unverified: selftest, grid and mutants were not run. L1 should run
`python3 tools/report-landing-audit.py --selftest`,
`python3 tests/report-audit/repo-state-grid.py --arm both --json`,
`tests/report-audit/isolation-mutants.py`, and the prereg promisor grid.
