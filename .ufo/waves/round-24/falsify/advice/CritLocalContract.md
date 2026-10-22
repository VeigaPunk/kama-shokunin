# CritLocalContract — r24 fresh falsification of 2e254a1763a9c08aa07fc53081287f506c447d84

Verdict: **FALSIFIED (partial)**. The candidate violates "known wrong type ⇒ failed exit 1" and regresses the frozen r23 verdict on a *plain, complete* lane/fleet pair. When a cited object is present only in the fleet (the second store) and is not a commit, the run refuses with exit 2. The refusal reason is also false: it says "is present but its content cannot be served". The defect is small and fixable, not a tradeoff. The rest of the local-object contract held on every row I measured.

## Snapshot

- Scratch: `/fast/scratch/hyaku/kama-r24/falsify/CritLocalContract/repo`. It was cloned `--no-hardlinks` from the lane and checked out detached. `git rev-parse HEAD` printed `2e254a1763a9c08aa07fc53081287f506c447d84`, so the base matches exactly.
- Observed sha256 values:
  - auditor `tools/report-landing-audit.py`: `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`
  - runner `promisor-grid.py`: `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`
  - manifest `promisor-grid-expectations.json`: `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`
  - mutation probe `promisor-mutants.py`: `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`
  - frozen auditor `0df800e:tools/report-landing-audit.py`: `da5041a8…5af1`, which matches the oracle snapshot.
- Git used for the checks: 2.56.0. I did not test the Git ≥ 2.45 floor; it remains open at L0.

## Counterexample 1: a fleet-only blob or tree is misclassified as unknown (DEFECT)

**Mechanism (static, `lookup()` lines 204–250).** `bare` is the answer aggregated across *all* stores. Inside the per-store loop, a token whose `t^{commit}` is missing is queued for the `t^{}` follow-up whenever `bare[token] == "found"`, even if *this* store does not hold the object. The lane store is visited first and does not have the object, so its `t^{}` also comes back `missing`, and `offer(token, "unknown")` sets the token to `unknown` (rank 2). Then the fleet store, which does hold the blob, skips the token because its status is no longer `absent`. The token ends as `unknown`, `refuse_unknown` raises, and the run exits 2. The outcome depends on store order: the same blob held by the lane gives the correct `wrongtype`.

**Fixture.** The fixture is benign and offline, using plain `git init` repositories. It has no promisor metadata and no removed objects; `rev-list --objects --missing=print --all` prints `?` 0 times in both repositories. Files:
- script: `.ufo/waves/round-24/falsify/out/CritLocalContract/fleet_only_wrongtype.sh`
- outputs: `fleet_only_wrongtype.out.txt` (candidate) and `fleet_only_wrongtype.arms.txt` (frozen and patched)

Command: `bash fleet_only_wrongtype.sh <auditor> <scratch>`. It runs `report-landing-audit.py --lane-repo lane --fleet-repo fleet --branch master --rounds 1 --no-errata|--errata F --json` for each case.

| case | candidate ea51bc35 | frozen da5041a8 | patched e8ee2faa |
|---|---|---|---|
| lane blob in Landed (control) | exit 1 landed-unresolved | exit 1 | exit 1 |
| **fleet-only blob** in Landed | **exit 2** "…bef05aa1… is present but its content cannot be served" | exit 1 landed-unresolved | exit 1 landed-unresolved |
| **fleet-only tree** in Landed | **exit 2** (same false reason) | exit 1 | exit 1 |
| **fleet-only blob, 12-hex abbrev** | **exit 2** | exit 1 | exit 1 |
| errata correcting the lane blob (control) | exit 1, errata-invalid | exit 1 | exit 1 |
| **errata, defect = lane blob, correction = fleet-only blob** | **exit 2** "errata line 1: unknown: …" | exit 1, errata-invalid | exit 1, errata-invalid |

The errata row shows that `apply_errata` inherits the same defect, because it calls `lookup(..., "^{commit}")`. A correction that names a known non-commit fleet object should give `errata-invalid` with exit 1. Instead the candidate refuses.

**Impacted axes.**
- Correctness: the "known wrong type ⇒ failed exit 1" rule is broken.
- No-harm: a non-promisor complete repository now gets exit 2 where r23 gave exit 1, so a failed verdict is hidden behind a refusal.
- False provenance: the reason claims the object is unavailable, but it is present in an audited repository.
- Twin parity: unaffected, because both sides of the pair fail the same way.

No graded grid row covers this case. PG38 and PG39 put the wrong-type blob in the lane, the store visited first.

**Smallest safe correction.** This is the diff I applied to a scratch copy only, saved as `out/CritLocalContract/minimal-correction.diff`. The follow-up query should ask about the bare object in the *same* store and skip stores that do not hold it:

```diff
-            out = git(store.path, "cat-file", "--batch-check",
-                      stdin="".join(f"{t}^{{}}\n" for t in unresolved))
-            lines = out.split("\n")[:len(unresolved)]
-            if len(lines) != len(unresolved):
+            out = git(store.path, "cat-file", "--batch-check",
+                      stdin="".join(f"{t}\n{t}^{{}}\n" for t in unresolved))
+            lines = out.split("\n")[:2 * len(unresolved)]
+            if len(lines) != 2 * len(unresolved):
                 raise EvalError(f"cat-file --batch-check in {store.path}: "
                                 f"short output")
-            for token, line in zip(unresolved, lines):
+            for token, here, line in zip(unresolved, lines[::2], lines[1::2]):
+                if here.endswith(" missing"):
+                    continue
                 offer(token, "unknown" if line.endswith(" missing")
                       else "wrongtype")
```

The patch keeps "a tag held by this store whose target this store cannot serve is unknown". It adds no metadata gate and no new Git primitive, so the version floor is unchanged. I also recommend a graded twin row next to PG38: a fleet-only blob cited in Landed, expected exit 1 with `landed-unresolved $blob`. That row turns this defect into an oracle check, and the mutation probe could include the order-dependent variant as a mutant.

**Patch no-harm check (bounded).** I ran the grid on 10 rows only, not the whole suite: `promisor-grid.py --arm current [--current patched] --case …` with `TMPDIR` set to scratch. The rows were PG26, PG27, PG30, PG33, PG34, PG38, PG39, PG46, PG47 and PG48. The candidate scored graded 10, violations 0. The patched copy also scored graded 10, violations 0, with identical exits (0 0 0 2 2 1 1 2 2 0), 4 of 4 twins compared, and 0 tracebacks or timeouts. Outputs are in `grid-subset-{candidate,patched}.json`. Both arms also reported `amended_view_met 0/10`; I did not investigate that counter. It looks like a reporting field rather than a grading failure, but that is [INFERENCE].

## Contract items that held

- **Promisor metadata alone changes nothing.** Statically, `check_history_repo` no longer inspects promisor state. `missing()` is computed lazily, and only for a token whose state is not found, ambiguous or wrongtype. PG26, PG30 and PG39 match their plain twins.
- **A known required object that is missing gives exit 2.** Every required read (the round log, the report `show`, the first-add log, the `SOURCES.md` ls-tree and blob) is wrapped in `required_read`, which names the object. PG33, PG34 and PG46 refuse.
- **A token absent from a complete pair gives exit 1, and errata still apply.** PG30 gives exit 0, because errata matching runs after `refuse_unknown` only when the store has no hole that the token could name.
- **An opaque hole gives exit 2 only for an unresolved token.** `opaque_hole` is reached only from `refuse_unknown`, or from the errata branch for an absent correction. PG47 gives exit 2 and PG48 gives exit 0. A blob-only unrelated hole does not block, as PG41 and PG42 show statically: the blob walk only matches the token by prefix.
- **Manual-backed availability claims.** Each claim the source makes rests on documented Git behaviour:
  - `--missing=print` prefixes missing ids with `?`, per git-rev-list(1).
  - `--no-lazy-fetch` is documented as equivalent to `GIT_NO_LAZY_FETCH=1`, per git(1).
  - `core.commitGraph=false` is a conservative choice: git(1) says commit-graph parsing checks object existence only under `GIT_COMMIT_GRAPH_PARANOIA`.
  - `X^{}` on a non-tag returns X, per gitrevisions(7).

  The source does not assert remote completeness or remote abbreviation uniqueness.
- **Cost of the store-wide walk** (`walk_timing.out.txt`). On the scratch lane clone (2348 commit, tree and tag roots, about 7.3k objects), the roots took 0.05 s and each walk 0.01 s, against the 20 s per-call timeout. So the walk is not a hidden blanket-refusal risk at lane scale. This is observed on the clone only. The real lane's dangling objects and the fleet repository were not measured, because those are production object stores.

## Tradeoffs and minor items (no rejection required)

1. **Cross-store tag** (`xstore_tag.out.txt`). A lane tag object whose target commit exists only in the fleet gives exit 2 on both the candidate and the patch, while frozen gives exit 1. Supplement 2 says "a known tag with unavailable target requires an actual dereference and may refuse", so this is permitted. The reason text, however, says the target is unavailable even though another audited repository holds it. If L1 wants that case resolved, parse the tag's `object` header and look it up across stores. That is a larger change than the patch above.
2. **Found prefix that also matches a missing object.** A short Landed token can resolve locally to one present commit while also prefixing a missing referenced object. The candidate reports it as found, which matches the supplement ("only when a citation is unresolved"). The cost is that a citation which is ambiguous within the referenced local universe is reported as resolved. This is acceptable under the local contract.
3. **Wording.** `unknown_citation` refusals say the token "is referenced by the history of `<repo>`". The walk is rooted at *every present* commit, tree and tag (`present_roots`), including dangling ones, so the referencing object may not be in any history. The function name `missing_reachable` is similarly loose. Exit 2 is still correct; only the reason text overstates provenance. The smallest correction is to say "referenced by an object in `<repo>`".

## Observed vs inferred

- Observed: every exit code, reason string and grid count above, and the static reading of lines 184–250, 419–447, 543–586 and 635–717 at ea51bc35.
- [INFERENCE]: that no other caller relies on the current cross-store `unknown` behaviour. A static search found `lookup` called only from `audit_round` (twice) and `apply_errata`. Also [INFERENCE]: that `amended_view_met` is a reporting counter.

## Not run (by contract or scope)

I did not run the full grid, the selftest, the mutation probe or historical parity on the patch. L1 should run them on any integrated fix. I did not run PM08 or any execution-bearing or network probe. I made no production edits. I installed no tools.

## Files written

All paths are absolute under `/home/vgpnk/Projects/shokunin/kama-shokunin/`:
- `.ufo/waves/round-24/falsify/advice/CritLocalContract.md`
- `.ufo/waves/round-24/falsify/out/CritLocalContract/`:
  - `fleet_only_wrongtype.sh`
  - `fleet_only_wrongtype.out.txt`
  - `fleet_only_wrongtype.arms.txt`
  - `xstore_tag.out.txt`
  - `walk_timing.out.txt`
  - `grid-subset-candidate.json` and `.err`
  - `grid-subset-patched.json` and `.err`
  - `minimal-correction.diff`

Scratch files only, under `/fast/scratch/hyaku/kama-r24/falsify/CritLocalContract/`: `repo/`, `fx/`, `frozen-audit.py`, `patched-audit.py`, `audit.diff`, `tmp/`.

Report: .ufo/waves/round-24/falsify/advice/CritLocalContract.md

Addendum (static, observed): `lookup` callers are lines 204 (recursive bare), 475, 487 (`audit_round`), 560 (`apply_errata`), plus single-store selftest probes at 1083-1087, which a per-store follow-up cannot change.

Report: .ufo/waves/round-24/falsify/advice/CritLocalContract.md

Addendum 2 (re: CaseFleetBlobless lazy-fetch hazard): unaffected. My fixtures (`fleet_only_wrongtype.sh`, `xstore_tag`) are plain `git init` repos with no remote or promisor config; the timing walk ran with `--no-lazy-fetch` on a non-promisor scratch clone; the grid subset ran without `--keep` and I did not manually inspect any blobless fixture.

Report: .ufo/waves/round-24/falsify/advice/CritLocalContract.md
