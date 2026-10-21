# ConnPlan — audit() data-walk: required object roots, outputs, and a boring state-passing design

Lane: leaf connector (no dispatch). Base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
(`tools/report-landing-audit.py` unchanged since base — verified
`git diff --stat 0df800e HEAD -- tools/ tests/` → empty). Read-only on production:
**no production file was edited.** Host: git 2.56.0, Python 3.14.8, Arch x64.

## Verdict

The whole round-24 repair is **one hole and one new state value**.

Every object the audit *reads* is already fail-loud: a missing required object makes
the corresponding `git` call exit non-zero, and `git()`
(`tools/report-landing-audit.py:111-136`) turns that into `EvalError` → exit 2.
The **single** place where git *reports* absence instead of failing is
`cat-file --batch-check` inside `lookup()`
(`tools/report-landing-audit.py:139-175`, call site `:153`, `missing` branch `:159`).
That is the only place where a verdict can be built on a *guessed* absence.

Therefore: **do not add a whole-repository object-closure check**
(`git rev-list --objects --missing=print --no-object-names`, the shape proposed in the
AuditRepair lane prompt). Measured: an unrelated deleted blob does not change any
audit-relevant output (probe Q2), while a blobless partial clone would fail such a
check on *every* blob — re-creating exactly the over-refusal this round repairs.
Fix the one hole instead: split `missing` into *definitely absent* and *absence
uncertain* (promisor-backed store), and keep *present-but-not-a-commit* a definite
finding.

## Axes named

| axis | what this lane touches |
|---|---|
| C1 calibration (7→7, lowest assigned axis) | the exit-2 vs exit-1 boundary for a missing citation; over-refusal removed, false-defect avoided |
| operability harm repair | a complete promisor-marked clone must receive a real verdict, not a blanket refusal |
| contract / exit semantics | exit 0 clean, 1 failed, 2 could-not-evaluate; defect kinds unchanged |
| substrate (git isolation) | `--no-lazy-fetch`, `--no-replace-objects`, log/signature suppression, `GIT_TIMEOUT` untouched |
| verification surface | the frozen r23 grid + the new promisor grid + mutants need the policy table below |

## 1. Call-graph data-walk (production tool, base 0df800e)

`run(args)` `:501` → the whole audit is one tree; every `git` call is listed.

| # | node (file:line) | git call | object root it needs | output that depends on it | how absence surfaces today |
|---|---|---|---|---|---|
| A1 | `parse_rounds` `:411` | `ls-tree -r --name-only HEAD -- .ufo/reports` `:429` | fleet HEAD commit + `.ufo/reports` tree | round selection | rc≠0 → exit 2 (probe A: "fatal: not a tree object") |
| A2 | `check_history_repo` `:438` | `rev-parse --show-object-format/--show-prefix/--is-shallow-repository/--git-path`, `config --list` `:443-465` | *metadata only* (no objects) | refusals: sha1, non-top-level, shallow, grafts, **blanket promisor refusal** | **the harm**: promisor metadata ⇒ exit 2 even when the store is complete |
| A3 | `resolve_branch` `:489` | `for-each-ref`, `rev-parse --verify <branch>^{commit}` `:494-497` | pinned lane branch tip commit | `tip` (root for A4, A6, A7) | rc≠0 → exit 2 |
| A4 | `run` `:517` | `rev-parse --verify HEAD^{commit}` (fleet) | fleet HEAD commit | fleet root | rc≠0 → exit 2 |
| A5 | `load_source_urls` `:258` | `ls-tree <tip> -- corpus/SOURCES.md` `:260`; `cat-file blob <oid>` `:268` | lane tip tree + the SOURCES blob | `source_url_hashes`; which 40-hex tokens are exempt | ls-tree rc≠0 → exit 2 (probe A); cat-file rc≠0 → exit 2 (probe B: "fatal: bad file") |
| A6 | `audit_round` `:302` | `show HEAD:<report>` `:310` | fleet HEAD tree + report blob | the audited text (citations, Landed section) | rc≠0 → exit 2 (probe D: "fatal: bad object") |
| A7 | `report_cutoff` `:215` | `log --diff-filter=A --format=%at -- <rel>` `:216` | fleet **path history** of the report + its trees | `cutoff` ⇒ which lane commits are *required* vs `post_report` | rc≠0 → exit 2 (probe Q3: "fatal: unable to read tree") |
| A8 | `round_commits` `:189` | `log -z --format=%H%x00%an%x00%at%x00%s <branch>` `:192` | lane commit graph reachable from `tip` | `required`, `post_report`, `landed-omitted` `:344-350` | rc≠0 → exit 2 (probe Q4: "fatal: Failed to traverse parents") |
| A9 | `lookup` `:139` (call sites `:325`, `:336`, `:404`) | `cat-file --batch-check` per repo `:153` | the *cited object itself* (any object in the store) | `unresolved-full-hash` `:326`, `landed-unresolved` `:339`, `landed-ambiguous` `:340`, `errata_invalid` `:406` | **rc=0, line `<name> missing`** → the token is treated as absent → a *guess* |
| A10 | `load_errata` `:374` | `show <tip>:registry/report-landing-errata.tsv` `:383` | lane tip tree + errata blob | `corrected` / `uncorrected` / `errata_unmatched` | rc≠0 → exit 2 |

Outputs of the audit (the verdict-bearing surface): per-round result dict `:351-357`
(`round, report, report_committed, cutoff, round_commits, required, post_report,
source_url_hashes, defects`), summary `:531-538` (`defects, corrected, uncorrected,
by_kind, errata_rows, errata_unmatched, errata_invalid, required_commits,
post_report_commits, status`), exit status `:538-539`, JSON/text rendering
(`main` `:926-960`).

**Conclusion of the walk:** A1–A8 and A10 already fail loud. **A9 is the hole.** A
required-object check that is *not* a whole-repo closure is therefore unnecessary:
the audit's evidence roots are exactly the objects it reads, and git already
refuses to answer when one of them is gone.

### Required object roots (pinned, per audit invocation)

| root | pin | used by |
|---|---|---|
| lane branch tip commit | `resolve_branch` (`:489-497`) | A5, A6(errata), A8 |
| lane commit graph from the tip | `git log <tip>` | A8 (omission detection) |
| lane tip tree + `corpus/SOURCES.md` blob | `ls-tree`/`cat-file` | A5 (URL exemption) |
| lane tip tree + errata blob | `git show <tip>:<path>` | A10 |
| fleet HEAD commit + tree | `rev-parse`/`ls-tree` | A1, A4 |
| fleet report blob per selected round | `git show HEAD:<rel>` | A6 |
| fleet **path history** of that report | `git log --diff-filter=A -- <rel>` | A7 (cutoff) |
| cited objects (commit/tree/blob), store-wide, **not** closure-limited | `cat-file --batch-check` | A9 |

Note the last row: a citation resolves against the *whole object store*, not the
branch closure — an existing but unreachable commit is still resolvable
(case `CaseUnreachableCitation`). A closure-based check (`rev-list --objects`) can
therefore never decide "is this citation missing?"; only A9 can.

## 2. The one hole, measured

`out/ConnPlan/probe_git_behavior.py` (git 2.56.0, local synthetic repos only, no
remote, no transport program, `--no-lazy-fetch` on every call; output in
`out/ConnPlan/probe-output.txt`):

| probe | result | consequence |
|---|---|---|
| Q1 `cat-file --batch-check` on a deleted object in a promisor-marked store | rc=0, `<oid> missing` | absence is *reported*: this is the hole (A9) |
| Q2 deleted *unrelated* blob → `git log -- <report path>` and `git log <tip>` | rc=0, cutoff and commit list unchanged | **no whole-repo closure check is needed**; a closure check would over-refuse |
| Q3 deleted tree needed by the path history → `git log -- <path>` | rc=128, "fatal: unable to read tree" | exit 2 already, for free |
| Q4 deleted ancestor commit → `git log <tip>` | rc=128, "fatal: Failed to traverse parents" | exit 2 already, for free (no truncated history) |
| Q5 `rev-list --objects --missing=print --no-object-names` | rc=0, missing object printed with a `?` prefix | usable as a *diagnostic*, but it is whole-repo scoped ⇒ over-refusal risk |
| Q6 absent oid under `--no-lazy-fetch` with `core.sshCommand` armed | rc=0, `missing`, **marker not created** | lazy fetch stays suppressed; no transport ran |
| Q7 `cat-file --batch-check <blob>^{commit}` | stdout `<oid>^{commit} missing`, stderr "expected commit type, but the object dereferences to blob type" | stdout alone cannot separate *absent* from *present-but-not-a-commit*; the **bare** query must be consulted (the bare pass already exists at `:149`) |

`out/ConnPlan/probe2-output.txt` (required-object failure modes):

| probe | result |
|---|---|
| missing root tree → `ls-tree` | rc=128 "fatal: not a tree object" → exit 2 |
| missing SOURCES blob → `cat-file blob` | rc=128 "fatal: bad file" → exit 2 |
| missing report blob → `show HEAD:<rel>` | rc=128 "fatal: bad object" → exit 2 |

## 3. Boring state-passing design

No globals, no caches, no new abstractions beyond one record and one status value.

**(a) One record per audited repository.** `check_history_repo` (`:438`) keeps every
refusal it has today (sha1 `:445`, non-top-level `:446`, shallow `:448`, effective
grafts `:451-453`) and *stops refusing* on promisor metadata; instead it **returns**
the promisor flag:

```python
class RepoState(NamedTuple):
    path: Path
    promisor: bool      # metadata: a promisor remote may hold missing objects
```

Promisor detection (metadata only, all offline, no remote contacted):
`extensions.partialclone` set (git prints the key lower-cased — measured), or
`remote.<name>.promisor` true (`git_bool` `:482`), or `remote.<name>.partialclonefilter`
set (r23 grid F27 measured that a filter-only remote *is* a promisor remote: the
lazy fetch ran), or a **paired** `objects/pack/*.promisor` + `*.pack`
(`--git-path objects/pack`, so bare/linked-worktree safe; the pairing keeps the
r23 `C10-orphan-promisor-marker` control at exit 0).

**(b) One audit-wide state, passed explicitly.** In `run()` (`:514-515`):

```python
states = tuple(check_history_repo(r) for r in (lane_repo, fleet_repo))
promisor = any(s.promisor for s in states)          # one bool, no cache
```
then `promisor` is passed down: `audit_round(..., promisor=promisor)` (`:519`),
`apply_errata(..., promisor=promisor)` (`:522`),
`lookup(repos, tokens, peel, promisor=promisor)` (`:325`, `:336`, `:404`).
One flag is enough, because the decision is "a token absent from *every* audited
store while *some* audited store is promisor-backed".

**(c) One new status value, decided at the very end of `lookup()`.**
`lookup` returns per token one of:

| status | meaning | consumer action |
|---|---|---|
| `found` | the object is in an audited store | no finding (unchanged) |
| `ambiguous` | the abbreviation matches several objects | `landed-ambiguous` (unchanged, definite) |
| `notcommit` | the object is **present** but is a blob/tree and cannot peel to a commit | `landed-unresolved` / `errata_invalid` — a **definite** finding (unchanged kind) |
| `missing` | absent from every audited store **and** no audited store is promisor-backed | `unresolved-full-hash` / `landed-unresolved` (unchanged) |
| `unknown` | absent from every audited store **and** some audited store is promisor-backed | **exit 2** — absence is not evidence |

Two implementation constraints (both load-bearing):

1. **`lookup` must not raise.** The bare-name recursion at `:149` runs *before* the
   repo loop; if it raised on `unknown`, the audit would refuse **before** the
   second repository is consulted, breaking cross-repo resolution
   (`CaseCrossRepoFound`: absent in the promisor lane, present in the fleet ⇒
   `found`). The conversion to `unknown` must happen *after* every repo has been
   consulted, and the refusal must happen in the consumer.
2. **`notcommit` needs the bare query's type.** The bare pass already asks the
   un-peeled name (`:149`); its `cat-file --batch-check` line carries the type
   (`<oid> <type> <size>`, parsed at `:168`). Today that type is thrown away by the
   recursion, and the peel line reports a blob as `missing` (probe Q7). The bare
   pass must therefore surface the type, and the outer call must keep `notcommit`
   instead of downgrading it to `missing`/`unknown` (a blob/tree can never peel to a
   commit — that is a *proof*, not an absence).

   Minimal shape: one private helper that returns `{name: (state, type)}` per repo,
   used by both the bare and the peeled pass; `lookup` keeps its current signature
   plus `promisor=False`. The alternative (a second bare query only for the tokens
   the peel reported missing) is a smaller diff but costs one extra `git` call in the
   failure path only.

**(d) One refusal helper, three call sites.** The rule "unknown ⇒ exit 2" is written
once:

```python
def require_resolved(status, where):
    unknown = sorted(t for t, s in status.items() if s == "unknown")
    if unknown:
        raise EvalError(f"{where}: absence of {', '.join(unknown)} is uncertain "
                        "in a promisor-backed store")
```
called at the three consumption sites — full-hash `:325-327`, Landed `:336-341`,
errata `:404-408`. `EvalError` → exit 2 with the existing "could-not-evaluate:"
prefix (`main` `:947-949`).

**e) Findings that must NOT change.** (Peer-corroborated: the
`CaseWrongTypeCitation` cell measured the frozen arms itself — unmarked exit 1,
promisor-marked exit 2 "partial clone (remote.origin.promisor)" — and pins the
regression guard: with a promisor mark added, the same *present* blob must stay a
definite `landed-unresolved` exit 1, never exit 2.)
`notcommit` keeps today's kinds
(`landed-unresolved`, `errata_invalid`); `ambiguous` stays `landed-ambiguous`; a
full-hash token that is a locally present **blob** stays `found` (no finding,
`OracleLocalBlobType`). The selftest pins the lookup vocabulary for non-promisor
fixtures — `lookup((lane,), ["0"*40]) == {"0"*40: "missing"}`
(`tools/report-landing-audit.py:836`), `{"…": "ambiguous"}` `:832-834` — so `missing`
must stay `missing` when no audited store is promisor-backed, and `unknown` must
appear only in the promisor case.

**Why a wrongtype citation yields exactly one finding** (peer-corrected; the
correction is *not* a span exclusion): the FULL scan **does** see Landed-span
tokens. `classify_full_hashes` (`:283-300`) appends every FULL match whose start
is inside the Landed span (`:293` `lo <= start < hi`); only an exact Registry-URL
occurrence *outside* that span is diverted to `classified`. (The r23 grid row F04 —
a fabricated citation inside Landed — expects **both** `landed-unresolved` and
`unresolved-full-hash`, which is only possible if the full-hash scan sees Landed
tokens.) So a Landed blob token T is seen by **both** lookups: the no-peel lookup
(`:325`) *resolves* it (a present blob is a valid existence token → `found` → no
`unresolved-full-hash`), and the peel to a commit fails (`notcommit` →
`landed-unresolved`). "No `unresolved-full-hash`" is therefore a **presence fact**,
not a Landed-span exclusion, and no expectation may be written as
SOURCES-dependent.

**f) `unknown` may arise only from a cited token's absence.** (Peer-measured
anchor: `non-promisor-unrelated-hole` — an unrelated missing blob referenced by a
post-report tree, deleted from the store and cited nowhere — is exit 1 with the
same single defect at the frozen base.) A hole that no citation names must never
produce exit 2, promisor-marked or not: the `unknown` state is created inside
`lookup()` for the tokens that are looked up, never by a store-wide scan. This is
the measured reason to reject the `rev-list --objects --missing=print` closure
variant (§Verdict, §2 Q2/Q5): a closure check would answer "this store has a hole"
and refuse, converting a legitimate exit 1 into exit 2. The promisor-marked variant
of that row must also stay exit 1 with the same single defect.

## 4. Contradictions (stated, not smoothed)

1. **Prereg item 1 vs item 4.** "Complete local promisor-marked lane and fleet
   clones with valid cited commits: exact same substantive clean/failed findings as
   otherwise identical full clones, not exit2" vs "A missing citation in any
   promisor-backed repository is unknown, not proved absent: exit2 unless resolved
   locally by another audited repository." For a promisor-backed store with an
   **invalid** citation the two cannot both hold: the full clone says exit 1
   (failed), the promisor clone says exit 2 (unknown). The prereg's qualifier
   ("with valid cited commits") resolves it in favour of exit 2 — but every
   "complete promisor" parity case in the new grid must therefore use **valid**
   citations, and must not assert exit-1 parity for an invalid citation.
2. **Coarse uncertainty vs the existing r23 rows.** The rule is store-level, not
   object-level: a promisor-marked store makes *every* local absence uncertain,
   even when that store is complete (CaseCompleteLane / CaseCompleteFleet). This
   is intentional (absence in a promisor store is never proof), but it means a
   "complete promisor-marked" case with a typo'd citation is exit 2, not exit 1.
3. **Metadata vs content.** Promisor-ness is still detected from *metadata*
   (config keys, pack markers). The repair changes what metadata *means* (a
   reason to doubt absence) — not what it proves. "Metadata-only declarations do
   not establish incompleteness" (prereg) is honoured: metadata alone never
   produces a verdict *or* a refusal; only a missing required object does.

## 5. Frozen r23 grid rows whose expectation must change (for ConnNoHarm)

| row | frozen | under the new policy | why |
|---|---|---|---|
| `F27-filter-only-promisor-remote` | exit 1, kinds `[landed-unresolved, unresolved-full-hash]` | **exit 2** (unknown citation) | a filter-only remote is a promisor remote → the fake token's absence is uncertain. The row's *other* invariant ("no transport ran") must be asserted by the marker, not by the exit code, since exit 2 no longer distinguishes "refused" from "policy". |
| `F06-lazy-fetch-command` | exit 2, reason `partial clone` | exit 2, **reason changes** to the unknown-absence message | the fake token is absent in a promisor-marked lane → unknown → exit 2, but no longer via the blanket refusal |
| `F23-promisor-pack-without-config` | exit 2, reason `promisor pack` | exit 2, **reason changes** | paired `.promisor`+`.pack` markers make the store promisor-backed; the missing blob in the report text is absent everywhere → unknown → exit 2 |
| `C09-promisor-false-config` | exit 0 | exit 0 (unchanged) | `promisor=false` ⇒ not promisor-backed (`git_bool` `:482`) |
| `C10-orphan-promisor-marker` | exit 0 | exit 0 (unchanged) | a `.promisor` marker without its `.pack` is not a promisor pack |
| `T01-blobless-partial-clone` | exit 0 | exit 0 (unchanged) | blobless clone keeps commits and trees; the cited commit resolves ⇒ `found`; no whole-repo closure check ⇒ no new refusal |

These are the "explicitly documented policy-row expectation changes" the prereg
measurement note allows; every other frozen row (including the real rounds 10–23
ledger) must stay byte-identical, because neither audited store is promisor-backed
there.

## 6. Risks

* **Over-refusal in the other direction.** With the coarse rule, a promisor-backed
  store turns every invalid citation into exit 2 (§4.1). Accepted by the prereg,
  but it must be visible in the grid expectations, not hidden.
* **`notcommit` regression.** If a future edit drops the bare pass (`:149`) or
  downgrades `notcommit` to `missing`, a definite finding silently becomes exit 2
  (or, worse, an unknown becomes a false defect). Keep the selftest cases
  `blob-is-not-a-correction` (`:864-868`) and `ambiguous-prefix-is-ambiguous`
  (`:831-836`), and add one wrongtype-in-Landed case (`CaseWrongTypeCitation`
  expects a real failed finding, not "uncertain missing").
* **Refusal before resolution.** See §3(c)(1) — raising inside `lookup` breaks
  cross-repo resolution.
* **Alternates / gitfile stores.** The paired-marker scan uses
  `--git-path objects/pack`, i.e. the repository's own store. A promisor-backed
  *donor* store reached through `objects/info/alternates` is not scanned, so an
  absence there can still be reported as a definite defect. This is the r23
  `O01-alternates-foreign-object` open row and stays explicitly unclaimed (the
  tool docstring already says so, `:54-56`); it is a *defect*-direction
  limitation, not a false-clean.
* **Cutoff semantics are out of scope.** The fleet first-add cutoff (A7) keeps its
  r23 semantics; the repair must not replace it with a tip-only check
  (`OracleFleetHistory`).
* **No isolation change.** `--no-lazy-fetch`, `--no-replace-objects`,
  `log.follow/showRoot/showSignature/mailmap`, `i18n.logOutputEncoding`,
  `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_TIMEOUT` (`:107`) stay exactly as they are;
  probe Q6 shows the marker never fires.

## 7. Verification (bounded; no full-suite runs by this lane)

1. `python3 tools/report-landing-audit.py --selftest` — vocabulary and finding
   kinds unchanged (the non-promisor fixtures must still yield `missing`).
2. The five frozen r23 rows in §5 re-measured, with the reason strings updated.
3. The new promisor grid (`tests/report-audit/promisor-grid.py --arm both --json`)
   against the preregistered expectations, including the complete-promisor parity
   cases **with valid citations** (§4.1).
4. The real rounds 10–23 ledger audit: `--json` output byte-identical to the
   frozen arm.
5. `out/ConnPlan/probe_git_behavior.py` re-run on the host git — the six
   behaviours the design rests on are git-version dependent and should be
   re-measured, not assumed.
6. The wrongtype six-arm case (`advice/CaseWrongTypeCitation.md`, peer-built and
   base-anchored) is the canonical regression guard for §3(e)/§3(f): all six arms
   expect **exit 1 with exactly one defect** (`landed-unresolved`, the blob token
   T) — including the promisor-marked arms and the promisor-marked arm with an
   unrelated hole. Two independent mutants are killed by it: a store-wide closure
   check (exit 2 instead of exit 1) and treating `notcommit` as `unknown`
   (exit 2 instead of exit 1).

## 8. Cross-lane notes

* **AuditRepair (executor):** implement §3, not a `rev-list --objects` closure
  check (§Verdict, §2 Q2). The two load-bearing implementation constraints are
  §3(c)(1) *do not raise inside `lookup`* and §3(c)(2) *keep the bare type*.
* **GridOracle:** encode the store-level uncertainty rule (§4.1) and the five
  changed rows (§5); a complete-promisor parity case must use valid citations.
* **CaseWrongTypeCitation / CaseCrossRepoFound / CaseUnknownCitation:** the
  expected outcomes follow from §3(c): present-blob ⇒ definite finding;
  absent-in-promisor-but-present-in-fleet ⇒ `found`; absent-everywhere-in-promisor
  ⇒ exit 2.
* **MutationOracle / MutationDesign:** the semantic mutations are exactly the
  three states — drop the `unknown` refusal (false defect), drop the cross-repo
  resolution (premature refusal), and treat `notcommit` as `unknown` (a definite
  finding turned into exit 2).

## Files written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/advice/ConnPlan.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/ConnPlan/probe_git_behavior.py`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/ConnPlan/probe-output.txt`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/ConnPlan/probe2.py`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/build/out/ConnPlan/probe2-output.txt`

Scratch (not part of the deliverable): `/fast/scratch/hyaku/kama-r24/ConnPlan/scratch`
(clone of the lane repo, `git clone --no-hardlinks`), used only for the read-only
base check. No production file was modified; no commit, no push; no install and no
pacman transaction.
