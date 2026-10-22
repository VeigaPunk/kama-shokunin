# CodePerRunCache — per-run store/cache ownership, branch/fleet-root binding, repeated invocation after a changed local object store

**Lane:** leaf member (no subagent dispatch). **Scope:** `tools/report-landing-audit.py` at
`2e254a1763a9c08aa07fc53081287f506c447d84`.
**Verdict: PARTIAL.** The per-run ownership discipline HOLDS. Two defects found, one of them a
verdict-regression against the frozen r23 baseline on a non-promisor repository.

## Snapshot and identity

| item | value |
|---|---|
| pinned revision (scratch clone) | `2e254a1763a9c08aa07fc53081287f506c447d84` |
| candidate auditor sha256 | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` |
| frozen r23 auditor sha256 | `da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1` |
| grid-recorded auditor sha256 | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` (matches; grid `auditor_sha256.current`) |
| scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/CodePerRunCache` (`--no-hardlinks`, detached at the pinned commit) |
| git | 2.56.0 |
| installs | none |
| production touched | none (read-only: `git branch -a`, `git remote -v`, `git count-objects -v`, `git fsck --unreachable`, `git rev-list --objects --all`) |

All fixtures are plain local git repositories built under scratch. No network, no transport, no
promisor remote, no execution payload. `TMPDIR` set per subprocess to
`/fast/scratch/hyaku/kama-r24/falsify/CodePerRunCache/probe/tmp`.

---

## Axis 1 — per-run store/cache ownership, no global sticky state: **HOLDS**

Verified by static inspection plus measurement.

* `RepoStore` (`tools/report-landing-audit.py:107-131`) is a per-run instance with
  `__slots__ = ("path", "root", "_missing")`. `_missing` is memoised **per store instance**, never
  at module scope. `run()` (`:762-766`) builds two fresh stores per invocation.
* No module-level mutable cache exists: no `lru_cache`, no module dict, no global sentinel.
  `RANK` (`:100`) is a read-only literal. `RepoStore.__slots__` is the only state.
* **Measurement — cross-run stickiness (probe Q6 / probe9 (e)):** in one process, audit a
  hole-bearing repo → `exit 2`; audit a clean repo → `exit 0`; re-audit the hole repo →
  `exit 2`. The clean repo is **not** contaminated by the prior hole repo's diagnosis.
  `clean_affected=False`.
* **Measurement — store lifetime (probe Q9):** an existing store's memoised set is unchanged
  after the object store changes (`cached_unchanged=True`); a *fresh* store sees the new hole
  (`fresh_store_sees_new=True`). Exactly the documented "computed once per store, in this run
  only" contract.
* **Measurement — no acquisition (probe Q5 / probe H):** object inventory before/after the audit
  is unchanged in both repositories (`acquired_lane=[]`, `acquired_fleet=[]`). The audit neither
  writes nor materialises objects.
* **Measurement — no residue (probe M7 / probe9 (e)):** digests of `.git` and of the working tree
  are byte-identical before and after a run.

**Conclusion:** the store/cache is owned by the run, not by the module or the process. No global
sticky state. This axis does not yield a finding.

## Axis 2 — selected-branch binding: **VIOLATED (finding F-1, medium)**

**The store's `root` does not scope the diagnosis.** `RepoStore.root` is the pinned lane tip
(`run()` `:762`, `build_store` `:680-686`), but `missing_reachable` (`:646-676`) discards it:

```python
roots = present_roots(repo)          # EVERY present commit/tree/tag, reachable or not
if root not in roots:
    roots.append(root)
```

`present_roots` (`:637-644`) enumerates `git cat-file --batch-all-objects`, i.e. the whole object
database, not the root's reachable set. The `root` argument therefore adds at most one extra
traversal root and never restricts anything.

**Measurement (probe Q1):** on a fixture whose hole is reachable only from the unselected `side`
branch, `missing_reachable(lane, master_tip) == missing_reachable(lane, side_tip) ==
missing_reachable(lane, "HEAD")` — `master_eq_side=True master_eq_head=True`. The selected branch
is not a binding.

**Measurement (probe Q9 (d), git shim):** the auditor's fleet reads are
`show HEAD:.ufo/reports/round-1/kama.md`, `log --diff-filter=A … -- <rel>`,
`rev-parse --verify HEAD^{commit}`, `ls-tree … HEAD`. The fleet `fleet_tip` computed at `:762` is
used **only** as the store root — and that root is ignored as shown above. The fleet content
reads are anchored to live `HEAD`, not to the pinned tip.

This directly contradicts the module docstring (`:110-115`), which claims the store "remembers the
objects the repository references but cannot serve — over all its present objects, reachable or
not" *as an explicit alternative* to the root, and the `RepoStore` docstring (`:108-113`) which
calls `root` "the commit root the audit reads". The code does the store-wide thing; the docstring
describes it; the *name* `root` and the parameter plumbed into `build_store(lane_repo, tip)`
suggest a per-branch binding that does not exist.

**Contract impact.** `oracle-amendment-1.json` prospective_expected[4] and the graded row
`PG31-missing-object-unselected-branch-promisor` require that a missing object reachable only from
an unselected branch not change the verdict. The candidate satisfies PG31/PG32 only because that
fixture's hole is a **blob** (blob-only holes are not "opaque"). Make the same fixture's hole a
**tree** and the store-wide scope makes it opaque and the verdict flips to exit 2 — see F-2.

## Axis 3 — repeated invocation after a changed local object store: **VIOLATED (finding F-2, medium)**

**The verdict is not a function of the audited content; it is a function of garbage in the object
database.** Because the diagnosis scope is store-wide (F-1), an object that **no ref reaches**
still enlarges the hole set, and `opaque_hole` (`:705-717`) then refuses.

**Measurement (probe Q3 / T5 / G1 / probe9 (c)):** a dangling tree created by
`git mktree --missing` (present in the object database, reachable from **no** ref —
`reachable_from_refs=False`) that names a missing tree, combined with an ordinary fabricated
citation, yields:

```
cand: exit 2  could-not-evaluate: round 1: unknown: unavailable required object:
      0123…4567 could be hidden behind the missing tree or commit 1111…1111
```

**Measurement — the twin comparison (probe T3):** the marked fixture gives exit 2; its otherwise
identical full twin gives exit 1 with the ordinary finding
`unresolved-full-hash:0123…`. `twins_differ=True`. The two repositories hold the same commits,
the same refs, and the same report; only the presence of unreachable garbage differs. This breaks
the amended contract's twin rule (prospective_expected[3]: "Complete marked versus unmarked twins …
retain identical substantive verdicts") and, more precisely, the amendment's rule that a
*diagnosis* is not a precondition.

**Measurement — the verdict flips under routine maintenance (probe Q4 / T4 / probe9 (c)):**

```
before garbage:  exit 1
with garbage:    exit 2
after `git gc --prune=now`:  exit 1        # flips = True
```

The *same* logical content audited before and after a garbage-collection gives different
verdicts. The audit is not reproducible across a `gc`. This is the "repeated invocations after a
changed local object store" failure the assignment targets.

**Severity qualifier — production exposure is currently nil, by luck.** Census of the two real
repositories at this revision:

| repo | present roots | reachable from refs | unreachable present roots | missing | opaque |
|---|---|---|---|---|---|
| lane `/home/vgpnk/Projects/shokunin/kama-shokunin` | 2348 | 1754 | 594 | 0 | 0 |
| fleet `/home/vgpnk/Projects/shokunin` | 5446 | 5235 | 211 | 0 | 0 |

Both real stores currently have `missing=0, opaque=0`, so no live verdict is affected today. The
lane is a `jj` repository (`.jj` present) and carries 594 unreachable present objects; `jj`'s
normal operation creates and abandons such objects. The exposure is latent, not hypothetical, and
the failure mode is a **verdict flip**, not a crash.

## Finding F-3 — cross-store wrong-type citation misclassified as "unknown" (high)

This one is outside the strict axis wording but is a genuine correctness regression found while
testing the store boundary, and it is the most serious result of this lane. Reporting it.

**Mechanism.** `lookup()` (`:184-251`) is a *cross-store* function: it iterates `for store in
stores:` and offers each store's answer through `offer()`/RANK (`:184-251`, `:100`). The peel
probe is per-store, but the "is the object here at all" test is made against the **union** of all
stores:

```python
bare = lookup(stores, tokens) if peel else None     # :204  -- UNION over stores
...
if line.endswith(" missing"):
    if (bare is not None and bare[token] == "found"   # :218  -- cross-store fact
            and status[token] == "absent"):
        unresolved.append(token)
    continue
```

So when store A does not hold the token but store B does, the union says "found" and store A's
`cat-file --batch-check <tok>^{}` probe — issued against **A**, which has nothing — returns
`missing`, which is then offered as **`unknown`**. RANK puts `unknown` (2) above `wrongtype` (1),
so the union's answer becomes `unknown`, and `refuse_unknown` (`:419-449`) refuses.

**Measurement (probe T1 / X5 / probe9 (a) / diffprobe C1).** A report cites a 40-hex token that
is a **blob held only by the fleet**; the lane holds no such object.

```
frozen r23: exit 1  kinds=['landed-unresolved:a916f5956ea3']
candidate:  exit 2  kinds=[]
  stderr: could-not-evaluate: round 1: unknown: unavailable required object:
          a916f5956ea382d1a79158a8d5638b57e709bf0f is present but its content cannot be served
```

Direct mechanism isolation (`lookup` called with one store at a time):

```
lookup((lane,),  [tok], '^{commit}')  -> {'tok': 'absent'}
lookup((fleet,), [tok], '^{commit}')  -> {'tok': 'wrongtype'}
lookup((lane,fleet), [tok], '^{commit}') -> {'tok': 'unknown'}    # <- union poisons
```

The candidate's message is also **factually false**: it says the object "is present but its
content cannot be served", when in fact the object is perfectly servable — it is a blob, i.e. a
*proved local wrong type*, which the local-object contract defines as an ordinary failed finding
(`landed-unresolved`), not an unknown.

**Contrast — the same blob in the lane is handled correctly** (probe X3/C2): `exit 1
landed-unresolved`. The defect is purely a consequence of the **store ordering**: `stores` is
`(lane, fleet)` (`:765-766`), so the lane is polled first and its "absent" answer poisons the
fleet's later, correct "wrongtype" answer. Reverse the order and the bug disappears.

**Contract impact.** The amended contract and `oracle-supplement-2.json` `not_unresolved` are
explicit: *"A known-present blob/tree that merely fails commit peeling is not an absent citation;
it keeps the normal wrong-type finding."* The candidate converts exactly that case into a
could-not-evaluate whenever the wrong-type object lives in the second audited store. K1 in
`build/advice/CritUnknown.md` ("a 40-hex token found locally as a blob or tree is a decisive
wrong type") and the frozen r23 behaviour (exit 1) both say exit 1.

**The graded grid does not cover this.** `PG38-wrong-type-citation-plain` and
`PG39-wrong-type-citation-promisor` build the wrong-type blob in the **lane** only
(`promisor-grid.py` `c_wrong_type_citation_plain` → `build(..., wrong_type=True)` puts
`shas["f_blob"]` in the report's Landed section; that blob lives in the lane). The fleet-side
wrong-type case is ungraded — it is the row the grid lacks.

**Real-world reachability.** Of the 98 rounds of committed fleet reports under
`/home/vgpnk/Projects/shokunin/.ufo/reports/`, a scan of every `## Landed changes` section for
non-commit 40-hex tokens resolves to **zero** occurrences today. So F-3 does not currently change
any production verdict. It is latent, but it is a plain wrong verdict on any repository pair where
the cited wrong-type object is in the fleet.

### Minimal correction (measured, not applied to production)

In `tools/report-landing-audit.py`, `lookup()`, replace the cross-store `bare` presence test with
a **per-store** presence test: before offering `unknown`/`wrongtype` for a store, confirm the
token is actually present in *that* store.

```python
# in the per-store loop, after collecting `unresolved`:
here = git(store.path, "cat-file", "--batch-check",
           stdin="".join(f"{t}\n" for t in unresolved))
here_lines = here.split("\n")[:len(unresolved)]
if len(here_lines) != len(unresolved):
    raise EvalError(f"cat-file --batch-check in {store.path}: short output")
unresolved = [t for t, l in zip(unresolved, here_lines)
              if not l.endswith(" missing")
              and not l.endswith(" ambiguous")
              and not l.endswith(" excluded")
              and not l.endswith(" dangling")]
```

and change the collection condition at `:218-221` to append every `missing` line (not only those
whose union state is `found`), letting the per-store filter above decide.

A ready-to-apply copy is at
`/fast/scratch/hyaku/kama-r24/falsify/CodePerRunCache/probe/fixed-auditor.py`
(sha256 `e411b60d649ba892669bc551a08c9adc48e5e1ba247d6a0f60b4296eff190bc9`), produced by
`probe/mkfix.py`. **Production was not edited.**

**Measured effect of the correction (all commands below, offline, bounded):**

| check | result |
|---|---|
| `python3 probe/fixed-auditor.py --selftest` | `selftest cases=62 failed=0`, exit 0 |
| `python3 tools/report-landing-audit.py --selftest` (candidate, for comparison) | `selftest cases=62 failed=0`, exit 0 |
| candidate on fleet-only-blob fixture | exit 2 |
| **fixed** on the same fixture | **exit 1, `landed-unresolved:a916f5956ea3`** (matches frozen) |
| **fixed** on tag-with-unavailable-target (must stay unknown) | exit 2 (unchanged) |
| **fixed** on fleet-side tag-with-unavailable-target | exit 2 (unchanged) |
| **fixed** on lane-blob citation | exit 1 `landed-unresolved` (unchanged) |
| **fixed** on blob in both stores | exit 1 `landed-unresolved` (unchanged) |
| **fixed** on errata correction naming a fleet blob | exit 1 + `errata_invalid` row (matches frozen) |
| `promisor-grid.py --arm current --current probe/fixed-auditor.py`, two bounded invocations covering 18 distinct rows (PG22, PG26, PG30, PG31, PG32, PG33, PG34, PG35, PG37, PG38, PG39, PG41, PG42, PG44, PG45, PG46, PG47, PG48) | `violations 0`, every row `met True` in both invocations |

Final re-verification with explicit exit-code capture on the fleet-only-blob fixture
(`probe/run9/fixtures/A`), the F-3 regression witness:

```
frozen  report-landing-audit.py  exit=1     (landed-unresolved)
candidate report-landing-audit.py exit=2    (unknown: present but content cannot be served)
fixed   fixed-auditor.py          exit=1     (landed-unresolved)
```

**Residual after the correction:** F-2 (the store-wide scope) is **not** fixed by it — the fixed
auditor still gives exit 2 on the dangling-garbage fixture (probe G1: `fixed=(2,[])`). F-2 needs
the scope changed, not the lookup.

### Minimal correction for F-2 (scope), not applied

`missing_reachable` must not treat unreachable garbage as part of the store's history. The
smallest change that preserves the intended PG46/PG47/PG48 behaviour is to root the walk at the
**audited root plus the refs** rather than at every present object:

```python
roots = git(repo, "rev-list", "--objects", "--no-object-names", "--all")  # ref-reachable
```

instead of `present_roots(repo)`, keeping the `root` argument meaningful. This needs the
missing-id walk to remain `--missing=print`-based so a *missing tree* is still detectable, and it
needs a separate bounded pass for the non-leaf classification (the `--filter=blob:none` walk
already present at `:669-673`). **This is a design change to a live contract area; I did not
apply it and did not measure a candidate.** I report it as the required shape of the correction,
not as a validated patch.

---

## Residual risk and verification gaps

* **F-1/F-2 are ungraded by the oracle.** No row in
  `tests/report-audit/promisor-grid-expectations.json` builds a wrong-type blob in the *fleet*,
  nor an unreachable-garbage hole. The grid's builders put wrong-type objects in the lane and
  drop objects that remain ref-reachable. The grid therefore reports `violations 0` while both
  defects are live. Two grid rows would close the gaps:
  1. wrong-type citation whose blob is in the **fleet** only → expect exit 1 `landed-unresolved`;
  2. an unreachable dangling tree naming a missing tree + a fabricated citation → expect the
     ordinary verdict (exit 1), identical to the garbage-free twin.
* **PG40 remains open** (`open_rows`, "the traversal scope for diagnosing an unresolved token is
  contested"). F-1/F-2 sharpen that open row: the candidate's scope is not "all refs" but "all
  present objects", which is strictly wider than the contested all-refs reading. The
  `oracle-amendment-1.json` text it must satisfy — "unrelated unavailable objects must not become
  a blanket precondition" — is violated by the garbage case.
* **The `--filter=blob:none` walk (`:669-673`) has an unresolved soundness question** inherited
  from `CritUnknown.md`'s qualification: a missing **tree** hides the names below it, so
  `--missing=print` cannot list a cited object under that hole. The candidate's second walk
  classifies non-leaf holes but does not, on its own, establish which token is hidden; it refuses
  on *any* opaque hole. That is the intended conservative behaviour under
  `oracle-supplement-2.json` rows PG46/PG47, and it is what makes PG33/PG34 (exit 2) correct. I
  did not find a defect here, but the second walk's necessity under the Git 2.45 floor is
  unverified by me: `--filter=blob:none` + `--missing=print` on the two real repositories
  completed in 0.03 s (lane) / 0.08 s (fleet), and no `--missing=print-info` or `--missing-only`
  was introduced (the supplement's version constraint is respected).
* **Unverified:** I did not run the full 47-row grid or the full r23 frozen grid (assignment
  bounds: one bounded check). The 13-row subset I did run is listed above. The mutation harness
  (`tests/report-audit/promisor-mutants.py`, `isolation-mutants.py`) was not run; a new mutant
  "per-store presence replaced by the cross-store union" would kill F-3, and one "store-wide
  present-object roots replaced by ref-reachable roots" would kill F-2.
* **The candidate auditor sha256 `ea51bc35…` matches the grid's recorded `current` arm**, so the
  artefact measured here is the one the grid measured.
* **Fixture hazard acknowledged from a peer** (`KamaR23-2.CaseFleetBlobless`): a blobless clone
  keeps a reachable local `file://` origin, so any probe **without** `--no-lazy-fetch`
  materialises the missing blobs and silently evaporates the premise. My fixtures are plain
  local repositories with **no remote at all**, so no lazy-fetch path exists; the auditor's own
  `--no-lazy-fetch` isolation is retained in every call (confirmed via the git shim: every one of
  the 22 logged calls carried `--no-lazy-fetch`).

## Files written

* This report:
  `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CodePerRunCache.md`
* Probe scripts and outputs (scratch, not production):
  `/fast/scratch/hyaku/kama-r24/falsify/CodePerRunCache/probe/{probe.py,probe2.py,probe3.py,probe4.py,probe5.py,probe6.py,probe7.py,probe8.py,probe9.py,diffprobe.py,mkfix.py,fixed-auditor.py,frozen/report-landing-audit.py,gitshim/git}`
* No production file was modified. No commit, no branch, no ref, no config, no fleet, no sibling
  lane, no operator routing, no service. The production repository was only read
  (`git branch -a`, `git remote -v`, `git count-objects -v`, `git fsck --unreachable`,
  `git rev-list --objects --all`) and the fleet reports were read for the citation census.
