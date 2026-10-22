# CodeStatusPriority — round-24 falsification of the audit tool's five-state lookup ranking

**Seat:** `KamaR23-2.CodeStatusPriority` (reviewer, leaf, read-only except this report and its `out/` artifacts)
**Lane target:** attack `lookup()`'s five-state ranking — *found wins across repositories*, *known wrongtype vs unknown*, *actual missing tag target* — and preserve inherited non-promisor semantics.
**Verdict:** **PARTIAL** — two axes hold, two are falsified by one root cause.
**Snapshot:** detached `2e254a1763a9c08aa07fc53081287f506c447d84` (tree `90d19f20e02caf0c7a52e152f020e98e3c416af3`), `tools/report-landing-audit.py` blob `91518a9d661c1f97670fc588e724ce5f97c972ac`. Inherited r23 base for comparison: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`.
**Execution:** one bounded offline fixture measurement of my own (no full grid, no network, no promisor remote, no lazy fetch, PM08 not executed). Tooling: git 2.56.0, python3, bash — **nothing installed or updated**.

---

## Axes and verdicts

| # | Axis | Verdict | Evidence |
|---|---|---|---|
| A1 | *found* wins across repositories | **HOLDS** | unit: `cross-repo-found` → `found` for both store orders; CLI case **H** → exit 0 clean |
| A2 | *actual missing tag target* (object held, content unservable) | **HOLDS** as a per-store classification | unit: single store → `unknown`; CLI case **I** (target missing in both repos) → exit 2, content-derived refusal |
| A3 | *known wrongtype vs unknown* merged across repositories | **FALSIFIED** | the merge is not the declared `RANK` max: it is store-order dependent (unit + CLI cases **D**/**E**) and produces one false refusal (**B**, **F**) and one false failed verdict (**D**) |
| A4 | inherited non-promisor semantics preserved | **FALSIFIED** | case **B**: r23 base → exit 1 `landed-unresolved`; `2e254a1` → exit 2 could-not-evaluate, on a complete, non-promisor, hole-free pair of repositories |

---

## Root cause (one defect, two consequences)

`tools/report-landing-audit.py`

* `:100` declares the merge order the tool intends: `RANK = {"absent": 0, "wrongtype": 1, "unknown": 2, "ambiguous": 3, "found": 4}`.
* `:184` `lookup(stores, tokens, peel="")` returns one state per token, *"across stores"*.
* `:204` `bare = lookup(stores, tokens) if peel else None` — the bare answer used below is the **aggregate over all stores**, not the answer of the store being examined.
* `:216-219` the "present but unservable" gate:

  ```python
  if line.endswith(" missing"):
      if (bare is not None and bare[token] == "found"
              and status[token] == "absent"):
          unresolved.append(token)
  ```

  Two independent faults:
  1. `bare[token] == "found"` is **global**: a store that does not hold the object at all is still pushed into the "the object is here, ask whether its dereference is servable" probe, because *another* store holds it.
  2. `status[token] == "absent"` makes the **second** store's answer conditional on the **first** store's answer, so the cross-store merge is not the `RANK` max the module declares.
* `:237-245` the follow-up `^{}` probe answers `missing` both for "this store does not hold the object" and for "this store holds the object but cannot serve its content"; the code maps the first case to `unknown` as well.

Net effect: **absence in a store is indistinguishable from unservable content in a store**, and the resulting state depends on the order in which the two audited repositories are visited (`run()` builds `stores = (lane, fleet)` at `:765-766`).

---

## Findings

### F1 — HIGH — False could-not-evaluate for a conclusive wrong-type object held only by the *second* audited repository

The 40-hex citation names a **blob** that lives in the fleet repository and is absent from the lane repository. Nothing is missing anywhere; both repositories are complete, non-promisor, hole-free.

```
$ python3 .../tools/report-landing-audit.py --lane-repo .../cli-B-blob-in-fleet-only/lane \
      --fleet-repo .../cli-B-blob-in-fleet-only/fleet --branch master --lane kama --rounds 24 --json
exit=2
stderr: could-not-evaluate: round 24: unknown: unavailable required object: \
        bfa655111293037a5564088d1a9bbca4cbcf446b is present but its content cannot be served
```

Premise, measured on the same fixture:

```
lane_missing=[]   fleet_missing=[]            # rev-list --objects --missing=print
git -C fleet cat-file -p bfa655…  -> "notes"   rc=0   # the fleet serves it completely
git -C lane  cat-file -t bfa655…  -> rc=128    # the lane simply lacks it
git -C lane  config --get remote.origin.promisor -> rc=1   (no promisor, no remote, either repo)
git -C fleet fsck -> clean, rc=0
```

The refusal reason is **factually false**: the object *is* present and its content *can* be served. The correct outcome for a citation that resolves to a locally present non-commit is the proved wrong-type finding.

Same fixture, same token, the blob held by the **lane** instead (case **A**) → `exit=1`, defect `landed-unresolved bfa655111293037a5564088d1a9bbca4cbcf446b` — i.e. the verdict changes with **which** audited repository holds the object, and the control without the wrong-type citation (case **C**) → `exit=0 clean`. So case B's exit 2 is caused solely by the wrong-type citation.

**Inherited-semantics comparison (axis A4)** — the r23 base tool on the *same* fixtures:

```
$ python3 .../base/report-landing-audit.py --lane-repo .../base-B-blob-in-fleet-only/lane \
      --fleet-repo .../base-B-blob-in-fleet-only/fleet --branch master --lane kama --rounds 24 --json
exit=1  status: failed  defects: [('landed-unresolved', 'bfa655111293037a5564088d1a9bbca4cbcf446b')]
```

r23 base: A → exit 1, B → exit 1 (the wrong-type finding, regardless of which repository holds the object).
`2e254a1`: A → exit 1, **B → exit 2**. This is an **unrequested behavior change for non-promisor repositories**: it needs no promisor metadata, no partial clone, no missing object — only two complete repositories and a citation of the wrong type. It also contradicts the amendment's *promisor metadata alone never changes a local-object resolution or a clean/failed verdict*: the verdict here changed with no metadata and no incompleteness at all.

### F2 — HIGH — The *conclusive wrongtype* vs *genuine unavailable tag target* merge is store-order dependent

Fixture: an annotated tag whose target is a blob. The **lane** holds tag+target (conclusive `wrongtype`); the **fleet** holds the tag but cannot serve the target blob (genuine `unknown`). The same two repositories with the roles swapped give the opposite answer.

```
case D  (lane conclusive, fleet unknown)   -> exit=1
          defect: landed-unresolved 0fc4f617da61b7346d7d658a810f9490dfe725bd
case E  (lane unknown, fleet conclusive)   -> exit=2
          stderr: could-not-evaluate: round 24: unknown: unavailable required object: \
                  0fc4f617da61b7346d7d658a810f9490dfe725bd is present but its content cannot be served
```

The same pair of physical repositories therefore yields **exit 1 in one role and exit 2 in the other**. Under the module's own declared order (`unknown`=2 > `wrongtype`=1) *both* must be `unknown`/exit 2; under a "a conclusive store outranks an unevaluable one" policy *both* must be `wrongtype`/exit 1. `2e254a1` implements neither — the answer follows the visit order, not the ranking. Unit-level confirmation with the tool's own `lookup()`:

```
wrongtype(lane)+unknown(fleet) | stores(lane,fleet) -> wrongtype   # RANK max would be unknown
wrongtype(lane)+unknown(fleet) | stores(fleet,lane) -> unknown
blob-in-lane-only              | stores(lane,fleet) -> wrongtype
blob-in-lane-only              | stores(fleet,lane) -> unknown
blob-in-fleet-only             | stores(lane,fleet) -> unknown
blob-in-fleet-only             | stores(fleet,lane) -> wrongtype
```

### F3 — MEDIUM — Further causal variant: the same false `unknown` reaches the errata-correction path

`apply_errata` (`:560`) performs the same peeled lookup for errata corrections. A correction token that names an object only the fleet holds produces a **refusal** where the contract's outcome is a *rejected errata row* (a verdict, not a no-verdict):

```
case F  errata correction = fleet-only blob   -> exit=2
          stderr: could-not-evaluate: errata line 1: unknown: unavailable required object: \
                  bfa655111293037a5564088d1a9bbca4cbcf446b is present but its content cannot be served
case G  same correction, blob also in the lane -> exit=1
          errata_invalid=1  errata_unmatched=1
```

So the false `unknown` has **two** call sites (`:487` landed-section citations, `:560` errata corrections), and the third lookup site (`:475`, the full-hash scan) is immune because it passes no peel.

**Why the fixed47 oracle cannot see F1/F2:** the false `unknown` is masked whenever the true best state outranks it (`found`=4, `ambiguous`=3). It becomes decisive exactly when the true best state is `wrongtype`=1 or `absent`=0 — i.e. only in the *second* store's direction. `tests/report-audit/promisor-grid.py` places the wrong-type blob in the **lane** (`shas["f_blob"]`, the lane's file blob) for PG38/PG39, so only the first-store direction is covered; no oracle row mixes a conclusive wrongtype with a genuine unknown in the other repository. Reported as a **coverage gap only** — no expectation is proposed or changed here.

### F4 — MEDIUM — The reason string must be content-derived *and* true

`:435` and `:568` emit *"is present but its content cannot be served"* for a state that, in case B/F, was produced by a store that does not hold the object at all. The amendment requires a *content-derived* reason; a reason that is refuted by `git cat-file -p` on the audited store is not derived from the content.

---

## Constraint for the fix owner (no patch proposed here)

`AuditRepair-2` owns the fix proposal; this lane only constrains it.

1. **Per-store facts.** A store's *own* bare answer decides whether that store may contribute `unknown`. Only a store that **holds** the object may say "present but unservable"; absence in a store is `absent` for that store and must never be laundered into `unknown`.
2. **Order-independent merge.** The cross-store merge must be a function of the *set* of per-store states, not of their visit order. Whatever policy is chosen (the declared `RANK` max, or "a conclusive per-store state outranks an unevaluable one"), cases **D** and **E** must produce the same verdict, and case **B** must produce the wrong-type finding (exit 1) under either policy, because the lane's absence is not evidence of anything.
3. **Holds that must not regress.** `found` across repositories (A1) and the genuine `unknown` when the object is held but its content cannot be served (A2) are verified and must survive the change; case **I** (target missing in both repositories) must stay exit 2.
4. **True reasons.** The refusal text must be derivable from the audited store's content (e.g. "held here, its target cannot be served here"), never asserted for an object that store does not hold.

---

## Exact commands, exits, findings/tokens

Tool under test: `/fast/scratch/hyaku/kama-r24/falsify/CodeStatusPriority/tools/report-landing-audit.py` (blob `91518a9d…`, revision `2e254a1`).
Invocation shape (all cases):

```
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CodeStatusPriority \
python3 tools/report-landing-audit.py --lane-repo <W>/lane --fleet-repo <W>/fleet \
        --branch master --lane kama --rounds 24 --json
```

| case | premise | exit | finding / stderr |
|---|---|---|---|
| A blob-in-lane-only | fleet lacks that blob | 1 | `landed-unresolved bfa655111293037a5564088d1a9bbca4cbcf446b` |
| B blob-in-fleet-only | **nothing missing anywhere** | **2** | `could-not-evaluate: round 24: unknown: unavailable required object: bfa655… is present but its content cannot be served` |
| C control (no wrong-type citation) | nothing missing | 0 | clean, no defects |
| D tag: lane conclusive, fleet target missing | fleet lacks the target blob | 1 | `landed-unresolved 0fc4f617da61b7346d7d658a810f9490dfe725bd` |
| E tag: lane target missing, fleet conclusive | lane lacks the target blob | **2** | `could-not-evaluate: round 24: unknown: … 0fc4f617… is present but its content cannot be served` |
| F errata correction = fleet-only blob | nothing missing | **2** | `could-not-evaluate: errata line 1: unknown: unavailable required object: bfa655… is present but its content cannot be served` |
| G errata correction, blob also in lane | nothing missing | 1 | `errata_invalid=1 errata_unmatched=1`, no defects |
| H cross-repo found (fleet's commit cited) | nothing missing | 0 | clean, no defects |
| I tag target missing in both repos | both lack the target blob | 2 | `could-not-evaluate: round 24: unknown: … 957389df4f2c6c68a8bb26b2ac7cc670db491f18 is present but its content cannot be served` |
| r23 base A | as A | 1 | `landed-unresolved bfa655…` |
| r23 base B | as B | 1 | `landed-unresolved bfa655…` ← inherited semantics, changed at `2e254a1` |

Unit-level (`lookup()` imported from the pinned tool, two `RepoStore`s over the same fixtures):

| token / stores | bare (lane) | bare (fleet) | peeled `^{commit}` |
|---|---|---|---|
| blob, stores(lane,fleet) | absent / found | found / absent | `unknown` (lane lacks it) |
| blob, stores(fleet,lane) | — | — | `wrongtype` |
| commit only in fleet | absent | found | `found` (both orders) |
| tag with unservable target, single store | — | found | `unknown` |
| tag: wrongtype(lane)+unknown(fleet), stores(lane,fleet) | — | — | `wrongtype` |
| tag: wrongtype(lane)+unknown(fleet), stores(fleet,lane) | — | — | `unknown` |

---

## Observed vs inferred

**Observed (measured in this run):** every exit code, defect kind and token, both stderr strings, the premise dumps (`rev-list --objects --missing=print` per repository), `cat-file -t`/`-p` on the cited object in each repository, `config --get remote.origin.promisor`, `remote -v`, `fsck`, the per-store and aggregate bare answers, and the r23-base comparison on identical fixtures.

**Inferred (not measured):** that a production report would cite a 40-hex non-commit that only the fleet holds (the trigger for F1/F3) — the shape is reachable in principle, not observed in the repository's own reports; and that the blast radius is limited to the two peeled call sites — this follows from the code (`:475` no peel, `:487` landed, `:560` errata) and all three sites were exercised in this run (`:475` in every case, `:487` in A/B/D/E, `:560` in F/G).

**Not exercised by design:** no full grid, no promisor-marked/partial-clone variant (the defect reproduced with *no* promisor metadata at all, so a promisor variant was not needed), no PM08 execution (static only, per contract), no network, no transport or execution payloads.

---

## Source-ledger supplement at this pinned revision

Observed at `2e254a1`: `corpus/SOURCES.md` holds **105** rows; **S105** is the explicit *rejected* record for the S095 cross-API inference (S095 stays filed as `rejected`; S096 remains the narrowed positive decoder fact). I introduced no new source row — this lane's finding is a defect in the repository's own code, not a third-party fact — and I did not reconcile any used-by cell. The source-census final verification stays L1-owned.

---

## Files written

* `.ufo/waves/round-24/falsify/advice/CodeStatusPriority.md` (this report)
* `.ufo/waves/round-24/falsify/out/CodeStatusPriority/probe.py` — the bounded fixture/measurement script (offline, `--no-lazy-fetch` everywhere, empty global/system git config)
* `.ufo/waves/round-24/falsify/out/CodeStatusPriority/probe-results.json` — raw unit + CLI + r23-base results
* `.ufo/waves/round-24/falsify/out/CodeStatusPriority/transcript.txt` — verbatim command/exit/finding transcripts
* `.ufo/waves/round-24/falsify/out/CodeStatusPriority/transcript.sh` — the transcript driver (re-runnable against the scratch fixtures)

Scratch (not part of the repository): `/fast/scratch/hyaku/kama-r24/falsify/CodeStatusPriority/` — `git clone --no-hardlinks` of `/home/vgpnk/Projects/shokunin/kama-shokunin`, detached at `2e254a1`, plus `base/report-landing-audit.py` (from `0df800e`), the generated fixtures under `work/`, `probe.py` and `transcript.sh`. `TMPDIR` was set to that directory for every subprocess.

**Nothing in `production/`, `.jj/index`, the fleet, sibling lanes, operator config, routing, services or any real object store was touched. No production file was edited.**

---

## Unverified items

1. The 47-case oracle was **not** re-run (lane bound: one bounded check, no full grid). The claim that PG38/PG39 cover only the first-store direction is read from `tests/report-audit/promisor-grid.py:319-380` (`shas["f_blob"]` is the lane's blob) plus the PG38/PG39 case entries, not from a grid execution.
2. Behaviour of the same shapes under **promisor-marked** repositories was not measured; the defect was reproduced without any promisor metadata, so the promisor path is *not* claimed to be affected or unaffected.
3. No fix was attempted or evaluated; `AuditRepair-2` owns the proposal, and the merge policy (RANK-literal vs "conclusive wins") is an owner decision I did not make.
4. `git` here is 2.56.0; the inherited **Git ≥ 2.45 prerequisite remains open at L0** and was not exercised at the floor version. `--filter=blob:none --missing=print` (used by the tool's own diagnosis, `:671-677`) is 2.45+ and was available in this run.
5. Real-world reachability of a fleet-only wrong-type citation inside kama's own reports was not searched (that is a corpus question outside this lane).
6. The r23-base comparison used the base file extracted with `git show 0df800e:tools/report-landing-audit.py`; it was executed as a standalone file, not as a checked-out tree, so any behaviour that depends on files beside the tool in the base tree was not covered.

Report: .ufo/waves/round-24/falsify/advice/CodeStatusPriority.md
