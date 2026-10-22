# CodeLookupMerge — round-24 falsification of `lookup()` cross-repository merging

**Verdict: FALSIFIED (source defect confirmed at the pinned revision; one
order-dependent regression with two reachable call paths).** The bare-vs-peeled
known-wrong-type axis and the tagged-missing-target axis both hold *only* when
the object lives in the **first** audited store; the production store order
puts the fleet repository second, so a wrong-type citation that exists only in
the fleet repository is reported as an unreadable object (`unknown`, exit 2)
instead of the normal wrong-type finding (exit 1).

Nothing in production was edited. All measurement ran against a detached
scratch clone; the lane tree, `production/.jj/index`, fleet, routing and
services were not touched.

---

## 1. Snapshot under test

| item | value |
|---|---|
| repository | `/home/vgpnk/Projects/shokunin/kama-shokunin` |
| pinned commit | `2e254a1763a9c08aa07fc53081287f506c447d84` (detached, scratch only) |
| file under test | `tools/report-landing-audit.py` |
| blob id of file at that commit | `91518a9d661c1f97670fc588e724ce5f97c972ac` |
| production working-tree copy | identical (`git hash-object` = `91518a9d…`, `git status --porcelain` empty) |
| scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/CodeLookupMerge/repo` (`--no-hardlinks`) |
| git | 2.56.0 (satisfies the inherited `git >= 2.45` prerequisite) |
| TMPDIR for every subprocess | `/fast/scratch/hyaku/kama-r24/falsify/CodeLookupMerge/tmp` |
| installs performed | none (no tool was installed or updated) |

## 2. The defect (static, pinned source)

`tools/report-landing-audit.py:184-251`, `lookup()`:

```
204:     bare = lookup(stores, tokens) if peel else None      # UNION over all stores
...
211:     for store in stores:                                 # PER STORE
219:         for token, line in zip(tokens, lines):
220:             if line.endswith(" missing"):
221:                 if (bare is not None and bare[token] == "found"
222:                         and status[token] == "absent"):
223:                     unresolved.append(token)
...
237:         if unresolved:
238:             # the object is here; ask whether what it dereferences to is
239:             # here too: ...
242:             out = git(store.path, "cat-file", "--batch-check",
243:                       stdin="".join(f"{t}^{{}}\n" for t in unresolved))
...
249:                 offer(token, "unknown" if line.endswith(" missing")
250:                       else "wrongtype")
```

The comment on line 238 states the intent — *"the object is here"* — but the
presence test that decides it is `bare[token] == "found"` (line 221), and
`bare` is the **union over every store** (line 204). A store that does **not**
hold the object therefore still enters the dereference branch, runs
`<token>^{}` in a repository where the object does not exist, gets `missing`
back, and **offers `unknown` for an object it does not have**.

Consequence of the rank table (`RANK = {"absent":0,"wrongtype":1,"unknown":2,
"ambiguous":3,"found":4}`, line 100): `unknown` (2) outranks `wrongtype` (1),
so the spurious `unknown` masks the true answer from the store that *does*
hold the object. The masking is also protected by the `status[token] ==
"absent"` guard on line 222: once the first store has raised the status to
`unknown`, the second store's `missing` line is skipped, so the second store
never gets to report `wrongtype` at all.

The store order is fixed by `run()` at line 764-766:

```
764:     stores = (build_store(lane_repo, tip),
765:               build_store(fleet_repo, fleet_tip))
```

so the **lane repository is the first store and the fleet repository the
second**. The defective path is therefore the *production* path for any
wrong-type citation that lives only in the fleet repository.

Two call paths reach the defective `peel` branch:
`audit_round()` line 487-489 (`## Landed changes` citations, peel `^{commit}`)
and `apply_errata()` line 560 (errata corrections, peel `^{commit}`).

### Minimal correction (report only — no production edit)

Make the presence test per store instead of global. Either

* compute the bare map per store inside the loop and use
  `bare_store[token] == "found"` on line 221, or
* when a peel line is `missing`, re-ask **the same store** for the bare object
  and only run the `^{}` dereference probe when *that* store holds it.

With that change the first store never offers `unknown` for an object it
lacks, the second store's `wrongtype` survives, and the final verdict becomes
order-independent. `RANK` itself should stay as it is (`unknown` outranking
`wrongtype` is a deliberate design choice for objects that genuinely cannot be
read). Independently, line 249 mislabels every non-`missing` dereference
answer as `wrongtype`; a `ambiguous` answer (or `excluded`/`dangling`) from
`^{}` should not be reported as `wrongtype`. With the per-store presence test
the `ambiguous` line no longer reaches line 249, but tightening it is cheap
insurance.

## 3. Measurements (one bounded offline object fixture; no grid, no network)

Fixture (all local, no remote, no promisor, no execution payload; every git
call carries the tool's own `GIT_ISOLATION`, i.e. `--no-lazy-fetch`,
`--no-replace-objects`):

* repo **A** = stand-in for a store that *lacks* the object,
* repo **B** = stand-in for a store that *holds* it.

Facts planted in B: a plain blob; an annotated tag → blob (target available,
wrong type); an annotated tag → a commit object that was then deleted
(unreadable target); a plain commit. A additionally holds 3000 blobs so that
one 4-hex prefix is ambiguous there, plus one copy of a colliding object in B.

### 3.1 Unit level — `lookup()` verdicts by store order

Source: `out/CodeLookupMerge/unit-lookup-probe.txt` (script
`out/CodeLookupMerge/probe.py`).

| token fact (object lives only in B) | `stores=(A,B)` peel `^{commit}` | `stores=(B,A)` peel `^{commit}` | truth |
|---|---|---|---|
| blob (known-present, not a commit) | **`unknown`** | `wrongtype` | `wrongtype` |
| tag → blob (target available, wrong type) | **`unknown`** | `wrongtype` | `wrongtype` |
| tag → deleted commit (unreadable target) | `unknown` | `unknown` | `unknown` (holds) |
| plain commit | `found` | `found` | `found` (holds) |

`bare` (peel `""`) is `found` for all four in both orders — the union bare
answer is correct; only the peeled verdict diverges.

Consequence through `refuse_unknown()` (line 419):

```
blob-only-in-B  stores=(A,B) -> REFUSE exit2: round 1: unknown: unavailable
   required object: 20b1a083… is present but its content cannot be served
blob-only-in-B  stores=(B,A) -> no refusal   (wrongtype is a failed finding)
```

The refusal message is **factually false** in the lane-first order: the
object *is* present and its content *is* served — by the fleet repository.

### 3.2 End-to-end — the tool's real store order

Source: `out/CodeLookupMerge/e2e-order-probe.txt` (script
`out/CodeLookupMerge/e2e.py`).

Identical report text, identical blob, blob in the *same physical repository*
(`repoX`) in both arms; only the lane/fleet assignment changes, i.e. only the
store order changes.

Arm 1 — blob in the **first** store (`--lane-repo repoX --fleet-repo repoY`):

```
exit=1
round=1 required=1 post_report=0 defects=1
  UNCORRECTED landed-unresolved 0219228bc6f98b3128c2edcb6ac2be22a328ab29
summary … by_kind.landed-unresolved=1 … status=failed
```

Arm 2 — blob in the **second** store (`--lane-repo repoY --fleet-repo repoX`),
i.e. the production order lane→fleet with the object in the fleet repo:

```
exit=2
stdout: <empty>
stderr: could-not-evaluate: round 1: unknown: unavailable required object:
        0219228bc6f98b3128c2edcb6ac2be22a328ab29 is present but its content
        cannot be served
```

Same citation, same bytes, same repository holding the blob → **exit 1
(wrong-type finding) vs exit 2 (refusal)** purely by store order.

### 3.3 Errata path in isolation

A draft that does **not** cite the blob, plus one errata row whose correction
is the blob (`1 unresolved-full-hash deadbee1 <blob> evidence`):

```
arm1 (blob in FIRST store):  exit=1
   errata-invalid line=1 correction=0219228bc6f98b3128c2edcb6ac2be22a328ab29
   summary … errata_unmatched=1 errata_invalid=1 status=failed
arm2 (blob in SECOND store): exit=2
   stderr: could-not-evaluate: errata line 1: unknown: unavailable required
           object: 0219228bc6f98b3128c2edcb6ac2be22a328ab29 is present but its
           content cannot be served
```

A correction that is a perfectly readable blob is reported as "content cannot
be served" instead of "not a valid correction".

### 3.4 Raw git facts the code depends on (observed)

```
'<blob>^{commit}'   -> '<blob>^{commit} missing'
'<blob>^{}'         -> '<blob> blob 12'
'<tag>^{commit}'    -> '<tag>^{commit} missing'
'<tag>^{}'          -> '<blob> blob 12'          (tag -> blob, target available)
'<gone-tag>^{}'     -> '<gone-tag>^{} missing'    (tag -> deleted commit)
'ambiguous4hex'     -> 'ambiguous'
'ambiguous4hex^{commit}' -> 'missing'             (why the bare pre-pass exists)
```

## 4. Contract impact

* `oracle-supplement-2.json` → `not_unresolved`: *"A known-present blob/tree
  that merely fails commit peeling is not an absent citation; it keeps the
  normal wrong-type finding even when unrelated opaque holes exist."*
  **Violated** in the lane-first order: the wrong-type finding is replaced by
  an `unknown` refusal.
* Round-24 goal contract: *"knownwrongtype=>failed1"*. **Violated**: the same
  known wrong type yields exit 2 when the object lives in the fleet repository.
* *"A known tag with unavailable target requires an actual dereference and may
  refuse."* — the tagged-missing-target axis **holds** for the verdict
  (`unknown` in both orders, exit 2), but in the lane-first order the
  `unknown` is produced by a dereference probe in a repository that does not
  contain the tag, i.e. not by the required actual dereference. The verdict is
  right; the reasoning is not. This is a latent trap: the same mechanism would
  let a *readable* tag→blob be reported as unreadable (see §3.1, row 2).
* The bare (no-peel) path is unaffected: full-hash resolution stays `found`
  in every order, so the `unresolved-full-hash` defect kind is not disturbed.
* The `found` verdict is never masked (`found` = rank 4 is the maximum), and
  `ambiguous` (rank 3) is never masked either. **Only `wrongtype` is
  maskable**, because `unknown` (2) > `wrongtype` (1).

## 5. Secondary observation (low impact, not fixed here)

The union merge also lets `found` (4) hide `ambiguous` (3): when the prefix is
ambiguous in one store and uniquely resolvable in the other, the per-store
ambiguity fact is discarded and the citation is reported `found`
(if the other store resolves it to a commit) or `wrongtype`/`unknown`
(if it resolves it to a non-commit). Impact is low because the audit's
`ABBREV` scanner (line 87) only emits 7..40-hex tokens, and a genuinely
ambiguous 7-hex prefix needs a real prefix collision; the fixture had to use
4 hex to demonstrate it (git's minimum abbreviation length), which the audit's
own scanner would never produce. Per the lane bounds, **no prefix-ambiguity
behaviour was changed or proposed for change**; this is recorded as an
observation only.

## 6. Related, already-known duplicate evidence (recorded, not suppressed)

`KamaR23-2.CaseFleetBlobless` reported from the PG43 fleet-unhydrated-blobless
lane that the blobless fixture's reachable `file://` origin lets a stray
`git cat-file -e HEAD:<path>` materialise missing blobs and turn a correct
exit 2 into a false clean exit 0. This report uses a *different* mechanism
(static merging of two stores, no promisor, no origin) and my fixture never
contacts any remote; every probe ran with the tool's own `--no-lazy-fetch`
isolation. `KamaR23-2` (parent) reported the same class of regression as
"GLOBAL bare presence wrongly used as CURRENT store presence"; this report is
the independent pinned-revision measurement of that class, and adds the
tag→blob and errata-path variants requested.

## 7. Files written

* `.ufo/waves/round-24/falsify/advice/CodeLookupMerge.md` (this report)
* `.ufo/waves/round-24/falsify/out/CodeLookupMerge/unit-lookup-probe.txt`
* `.ufo/waves/round-24/falsify/out/CodeLookupMerge/e2e-order-probe.txt`
* `.ufo/waves/round-24/falsify/out/CodeLookupMerge/probe.py`
* `.ufo/waves/round-24/falsify/out/CodeLookupMerge/e2e.py`

Heavy scratch (clone + throwaway repos + TMPDIR), outside the lane tree:
`/fast/scratch/hyaku/kama-r24/falsify/CodeLookupMerge/`.

## 8. Unverified items / residual risk

* **Not measured:** whether any *real* round-24 fleet report cites a
  wrong-type object that exists only in the fleet repository. A full audit
  sweep was out of bounds for this lane; the defect is proven at the source
  and fixture level, and its production reach is a question of the corpus.
* **Not measured:** the same regression against a store pair where the fleet
  repository is a partial clone (`blob:none`) — the masking does not depend on
  promisor metadata, but that combination was not exercised.
* **Not measured:** `unresolved-full-hash` verdicts in the peeled path are
  unaffected by construction (bare path only), so the `unresolved-full-hash`
  defect kind was not re-verified end-to-end beyond the fixture.
* The proposed correction was reasoned from the source but **not applied and
  not executed**; per the lane bounds, no production edit was made.
* The `unknown`/`wrongtype` rank order (`RANK`, line 100) was left untouched
  in the proposal; any change there would alter other documented semantics
  and needs a separate decision by L1.

Report: .ufo/waves/round-24/falsify/advice/CodeLookupMerge.md
