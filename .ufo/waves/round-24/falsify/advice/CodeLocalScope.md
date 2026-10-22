# CodeLocalScope — round-24 falsification of 2e254a1 (negative diagnosis vs ordinary object resolution)

**Lane**: leaf member (no subagent dispatch). **Kind**: bounded reviewer check, not a grid run.
**Question assigned**: does the candidate separate a *negative diagnosis* (a genuinely missing
cited object, including one hidden behind another ref or a dangling tree) from *ordinary object
resolution* (a present but unreachable object resolves normally)? And: does the **PG40 open
builder actually cite the missing side blob**?

**Verdict in one line**: the candidate's separation **HOLDS** on every assigned shape (4/4 legs,
12 measurements, 0 falsifications); the **PG40 open row is premise-mismatched** — its builder cites a
fabricated token, **not** the missing side blob, so PG40 as built does not exercise the scope
distinction at all and must stay ungraded. No headline credit is taken for the ungraded row.

---

## 1. Snapshot, pins, environment (observed)

| item | value |
|---|---|
| pinned revision | `2e254a1763a9c08aa07fc53081287f506c447d84` (`round-24: land completed 64-seat build evidence and explicitly carry residual closure debt`, commit time 1792611912) |
| scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/work` (`git clone --no-hardlinks` from `/home/vgpnk/Projects/shokunin/kama-shokunin`, detached checkout of the pinned sha) |
| scratch worktree state | `git status --porcelain` → empty (no local edits) |
| production tree | untouched; `git -C …/kama-shokunin rev-parse HEAD` = same pinned sha; only untracked path is the wave artifact dir `.ufo/waves/round-24/falsify/` |
| source tool sha256 | `tools/report-landing-audit.py` = `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` → matches the assigned pin **source tool `ea51bc35…`** |
| runner sha256 | `tests/report-audit/promisor-grid.py` = `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` → matches **runner `b034e159…`** |
| manifest sha256 | `tests/report-audit/promisor-grid-expectations.json` = `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` → matches **manifest `d86b7bea…`** |
| mutation probe sha256 | `tests/report-audit/promisor-mutants.py` = `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` → matches **mutation probe `6e0b9d62…`** |
| toolchain | git 2.56.0, Python 3.14.8 (floor `git >= 2.45` satisfied) |
| installs / updates | **none** (no pacman, uv, cargo, npm, release binary was used in this lane) |

All four artifact digests equal the pins carried in my assignment, so the objects measured here are
the assigned objects.

---

## 2. Commands executed (exact), with exit codes

```
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin work      # exit 0
git -C work checkout --detach 2e254a1763a9c08aa07fc53081287f506c447d84       # exit 0
sha256sum tools/report-landing-audit.py tests/report-audit/promisor-grid.py \
          tests/report-audit/promisor-grid-expectations.json \
          tests/report-audit/promisor-mutants.py                              # exit 0
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/tmp \
  python3 probe.py  /fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/out   # exit 0
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/tmp \
  python3 probe2.py /fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/out2  # exit 0
grep -n -- "--missing" tools/report-landing-audit.py                            # exit 0
grep -n -i "promisor|partialclone|partial clone" tools/report-landing-audit.py  # exit 0
```

Inside `probe.py`/`probe2.py` the auditor was invoked as the grid invokes it
(`--lane-repo … --fleet-repo … --rounds 1 --json --no-errata`, 30 s grid timeout, process-group
kill) — 8 subprocess runs + 3 in-process runs (the counterfactual arm patches the imported module
only, never a production file). **No full grid, no frozen arm, no mutation suite, no selftest was
run.** No network, no transport, no execution payload, no PM08.

---

## 3. Findings, by severity

### F1 — HIGH (fixture defect, not a candidate defect): the PG40 open builder does **not** cite the missing side blob

`tests/report-audit/promisor-grid.py:675`

```python
def c_missing_cited_unselected_branch_promisor(root, tmp):
    return build(root, tmp, lane_mark="config", unselected_hole=True,
                 fake_landed=True, drop=("unselected_blob",))
```

`build()` publishes the report with `cites = [lane_commit] + [FAKE]` (`fake_landed=True` adds the
constant `FAKE = 0123456789abcdef0123456789abcdef01234567`); `notes` is empty because
`cited_blob`/`cited_hidden_blob` are not set. The dropped object `unselected_blob` (the `side.txt`
blob of the `side` branch) is therefore **never mentioned in the report**.

Measured (scenario A, PG40 built exactly as the grid builds it):

```
report_text:
  # kama round 1

  ## Landed changes

  - 58866b563cd900df310588effe79028efc104c33
  - 0123456789abcdef0123456789abcdef01234567

cited_tokens_in_report      = [0123456789abcdef0123456789abcdef01234567,
                               58866b563cd900df310588effe79028efc104c33]
missing_side_blob_sha       = 2299c37978265a95cbe835a4b0f0bbf15aad5549
side_blob_cited_in_report   = false
fabricated_token_cited      = true
side_ref_exists             = true
premise.lane_missing        = []          <-- the grid's own probe sees NO hole
diagnosis.missing (auditor) = [2299c37978265a95cbe835a4b0f0bbf15aad5549]
diagnosis.opaque            = []
audit                       = exit 1, stderr empty, verdict document present
   defects: landed-unresolved 0123456789abcdef0123456789abcdef01234567
            unresolved-full-hash 0123456789abcdef0123456789abcdef01234567
```

Two consequences:

1. **PG40 as built is a "fabricated token cited + uncited missing side-branch blob" fixture** — the
   same shape as PG37/PG41 — *not* the "missing cited object behind another ref" case its name
   claims. It therefore cannot discriminate the traversal-scope question (refs-only closure vs
   store-wide closure) in either direction. Its amended expectation stays `null` (ungraded); the
   fixed47 headline is untouched and **no headline credit is claimed here**.
2. **The grid's own premise probe is blind to this hole**: `missing_objects()` walks only
   `refs/heads/master`, so `premise.lane_missing == []` even though the store cannot serve the
   side blob. The candidate's store-wide diagnosis (`present_roots`: every present
   commit/tree/tag, reachable or not) *does* see it. A row whose premise check cannot see the hole
   it is named after is a weak witness; the intended shape was re-measured directly below.

Minimal correction (reported, **not** applied — production is read-only for this lane): the PG40
builder should cite the missing side blob, e.g.

```python
def c_missing_cited_unselected_branch_promisor(root, tmp):
    built = build(root, tmp, lane_mark="config", unselected_hole=True,
                  fake_landed=True, drop=("unselected_blob",))
    # republish the report citing the dropped side blob, and keep the
    # fabricated token, so the row measures the scope question it names
    ...
```

A second, smaller defect in the same builder family: `build()` computes
`premise["lane_missing"]` over `refs/heads/master` only, so a hole behind `refs/heads/side` is
invisible to the premise check (`premise-hole-detected` in the grid's selftest would not fire for
this family). Reporting only; no edit.

### F2 — HOLDS: a missing **cited** object behind another ref ⇒ exit 2 (content-derived)

Scenarios B / E / E2: the report cites `2299c379…` (the dropped side blob, reachable only from
`refs/heads/side`).

```
stderr: could-not-evaluate: round 1: unknown: unavailable required object:
        2299c37978265a95cbe835a4b0f0bbf15aad5549 is referenced by the history of
        <lane> but the repository cannot serve it
exit 2, stdout empty (no verdict document), timed_out false
```

Identical exit and identical reason for the **plain** twin (E, no promisor metadata) and the
**promisor** twin (E2, `remote.origin.promisor=true` + `extensions.partialclone=origin`): the
token-scoped rule is applied to every store and is not conditioned on metadata.

### F3 — HOLDS: a missing **cited** object behind a *dangling* (ref-unreachable) tree/commit ⇒ exit 2

Scenario B2 / counterfactual G, H: the `side` ref is deleted, so the side commit and its tree are
present but unreachable from any ref; the report cites the missing blob they reference.

```
candidate (store-wide roots):  exit 2
  stderr: could-not-evaluate: round 1: unknown: unavailable required object:
          2299c379… is referenced by the history of <lane> but the repository cannot serve it
  stdout: empty
counterfactual (present_roots restricted to ref-reachable roots: 5 roots -> 3 roots):
  exit 1
  defects: unresolved-full-hash 2299c379…, landed-unresolved 2299c379…
```

The counterfactual arm shows the candidate's `present_roots` (every present commit/tree/tag, not
only ref-reachable ones) is **load-bearing**: a refs-only closure would report a *false* "proved
absent" failed verdict (exit 1) for a blob the store demonstrably references and cannot serve. This
is the same shape as `build/advice/ConnClosure.md`; independently reproduced here.

### F4 — HOLDS: a **present** unreachable object resolves normally (never the negative diagnosis)

| scenario | cited object | present | ref-reachable | diagnosis.missing | result |
|---|---|---|---|---|---|
| C | ref-unreachable **commit** `51fba425…` | yes | no | `[]` | **exit 0**, no defects, no refusal |
| C2 | ref-unreachable **blob** `2299c379…` | yes | no | `[]` | **exit 1**, defect `landed-unresolved` only — the object resolves as *present but not a commit* (the `wrongtype` branch of `lookup`), never as missing |
| F / F2 | fabricated token cited, missing blob **uncited** | — | — | `[2299c379…]` | **exit 1** (defects `unresolved-full-hash` + `landed-unresolved` on the fabricated token) under both the candidate and the refs-only counterfactual, with identical documents |

A present object never enters `missing_reachable` (`rev-list --missing=print` lists only ids the
store cannot serve), so the negative diagnosis cannot fire on it; and an *uncited* hole never
blocks anything — no blanket closure precondition, in both the plain and the promisor twin.

### F5 — HOLDS: no metadata blanket refusal, no transport, floor unchanged (static + observed)

* Promisor-marked fixtures return ordinary verdict documents (exit 0/1, **empty stderr**); the
  r23 strings `partial clone (` / `promisor pack` appear in no refusal.
* Every exit-2 reason is content-derived and names the object id (the grid's `names_any_of`
  requirement is satisfiable by the candidate's own stderr).
* Static: `tools/report-landing-audit.py` uses only `--missing=print` (lines 64, 659, 673) — **no**
  `--missing=print-info`, **no** `--missing-only` → the documented Git floor is not raised; the
  `--filter=blob:none` second walk is a pre-existing 2.45 primitive.
* Static: `GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch", …)` covers every git call;
  the auditor contains no `fetch`/remote/transport invocation (the `remote`/`url` hits are the
  source-URL regexes).
* Every probe used `--no-lazy-fetch` plumbing (the grid's own `object_exists`,
  `missing_objects`, `object_inventory` helpers are all `--no-lazy-fetch`); the `CaseFleetBlobless`
  hazard (a reachable `file://` origin that a stray probe could lazy-fetch) does not apply to my
  fixtures, whose promisor remote URL points at a non-existent path.

---

## 4. Holds / falsified / partial — explicit

* **Holds (candidate)**: F2, F3, F4, F5 — negative diagnosis vs ordinary resolution is separated
  correctly at the pinned revision, for plain and promisor stores alike, and the store-wide root
  set is what makes the dangling-tree case correct.
* **Falsified**: nothing in the candidate. No assigned behavioural requirement failed.
* **Partial / premise defect (fixture, not candidate)**: F1 — the PG40 open builder does not cite
  the missing side blob; PG40 as built cannot discriminate the scope question and must remain
  ungraded. If L1 later promotes PG40 to a graded exit-2 row, the candidate would score exit 1 —
  correctly, because in that fixture the fabricated token is a proved absence and the missing blob
  is uncited. Any such promotion must first fix the builder.
* **Not claimed**: no statement about the 47-row headline, the frozen arm, the mutation suite, the
  selftest, or any row outside this lane's scope.

---

## 5. Residual risk and verification gaps

1. **PG40's fate** (F1): if the open row is ever graded as built, the score is a fixture artefact,
   not a candidate defect. Fixing the builder (cite the side blob) is the only honest route.
2. **Grid premise blindness**: `missing_objects()` over `refs/heads/master` misses holes behind
   other refs, so `premise-hole-detected`-style checks are weaker for this family than the
   auditor's own diagnosis. Unverified whether other rows of the fixed47 share the blindness.
3. **Blobless-clone lazy-fetch hazard** (raised by `CaseFleetBlobless`): my fixtures never use a
   blobless clone with a reachable origin, so I did **not** re-measure that hazard; I only confirm
   my own probes used `--no-lazy-fetch` throughout.
4. **Unmeasured**: the frozen (r23) arm for these shapes, `promisor-mutants.py`, the auditor
   selftest, and the amended oracle's other rows. None are claimed.
5. **Fixture-time assumption**: the lane tip is `master` and the report is a single fleet commit;
   the pinned auditor defaults (`--branch master`, `--rounds 1`) were used, so multi-round and
   non-master behaviour was not exercised.

---

## 6. Files written (absolute)

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CodeLocalScope.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CodeLocalScope/probe.py`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CodeLocalScope/probe2.py`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CodeLocalScope/probe-result.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CodeLocalScope/counterfactual-result.json`

Heavy scratch/temp (not part of the deliverable): `/fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope/{work,grid-root,grid-root2,out,out2,tmp}`.

**Production was not modified.** No lane, fleet, sibling, operator config, routing, service, or
object store was touched; no `.jj/index` write; no system install; no network.

### Provenance note (appended after the first write)

`git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain` shows
` M .ufo/waves/round-24/build/advice/GridOracle.md` alongside the untracked wave artifact dirs.
That modification is **not** this lane's: this lane wrote only
`.ufo/waves/round-24/falsify/advice/CodeLocalScope.md` and
`.ufo/waves/round-24/falsify/out/CodeLocalScope/*` (scratch clones and probes live under
`/fast/scratch/hyaku/kama-r24/falsify/CodeLocalScope`). Recorded for the L1's provenance audit; no
action taken on it.

Report: .ufo/waves/round-24/falsify/advice/CodeLocalScope.md
