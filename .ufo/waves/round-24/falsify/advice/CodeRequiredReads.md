# CodeRequiredReads — round-24 falsification (leaf seat, static + bounded fixtures)

Target attacked: the **actual required-read paths** of the round-24 auditor
(`tools/report-landing-audit.py`): history, tree, `corpus/SOURCES.md`, fleet
report, errata ledger. Two claims under attack:

1. **no catch-and-pass** — a failed required read must never become a verdict
   (exit 0/1) and never a silently skipped read;
2. **`root_tree()` is an error-identity helper only** — it may enrich a refusal
   message, but it may not create a verdict and may not act as an upfront gate.

Scope discipline: static source reading + ONE bounded offline fixture family
(11 cells built with the repository's own fixture builders). No full grid, no
mutation probe, no network/transport/execution payload, no lazy fetch.

---

## 0. Snapshot, hashes, environment

| item | value |
|---|---|
| pinned revision (observed) | `2e254a1763a9c08aa07fc53081287f506c447d84` (detached in scratch) |
| scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/CodeRequiredReads` (`git clone --no-hardlinks`, production repo untouched) |
| source tool | `tools/report-landing-audit.py` sha256 `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` — matches the contract's `ea51bc35…` |
| runner | `tests/report-audit/promisor-grid.py` sha256 `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` — matches `b034e159…` |
| manifest | `tests/report-audit/promisor-grid-expectations.json` sha256 `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` — matches `d86b7bea…` |
| mutation probe | `tests/report-audit/promisor-mutants.py` sha256 `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2` — matches `6e0b9d62…` |
| git / python | `git version 2.56.0` / `Python 3.14.8` |
| oracle used | `.ufo/waves/round-24/oracle-snapshot-before-inspection.json` (live = `amended` view where present) |

All four contract hashes were recomputed in the scratch checkout and match the
round-24 dispatch payload: the audited base is exactly the pinned revision.
The inherited Git ≥ 2.45 prerequisite stays open at L0 and is **not** claimed
here.

---

## 1. Verdict

| # | claim under attack | verdict |
|---|---|---|
| C1 | history read failure (`git log`) is never catch-and-pass | **HELD** |
| C2 | tree read failure (`ls-tree` on the tip tree) is never catch-and-pass | **HELD** |
| C3 | SOURCES read failure (`ls-tree` + `cat-file blob`) is never catch-and-pass | **HELD** |
| C4 | fleet/draft report read failure is never catch-and-pass | **HELD** |
| C5 | errata read failure is never catch-and-pass | **HELD** (exit 2 observed) — but see **F1**, a form inconsistency |
| C6 | `root_tree()` cannot create a verdict | **HELD** |
| C7 | `root_tree()` cannot act as an upfront gate | **HELD** |
| F1 | every required read refusal carries the same content-derived identity (object id + tip tree) | **FALSIFIED (low severity)** — the errata read is the one required read that is not wrapped in `required_read()`; it still exits 2, so no oracle row and no verdict is affected |
| F2 | an out-of-scope errata row cannot turn an unavailable object into a failed verdict | **FALSIFIED (medium severity)** — the `invalid` comprehension is not scoped to the audited rounds; **primary finding and minimal correction belong to `KamaR23-2.CodeErrataBoundary`**; my independent corroboration and the r23-inheritance fact are in §7.1 |

Overall: **HELD** for the assigned attack surface, with **one low-severity
form defect (F1)** and **one medium-severity scope defect (F2)** reported, both
with minimal corrections (F2's primary ownership is
`KamaR23-2.CodeErrataBoundary`; §7.1 carries my independent corroboration).
No oracle row is violated by my cells; nothing here is relabelled as an
achieved *withdrawn* expectation.

---

## 2. Static review of every required read (source, pinned revision)

Production module = `tools/report-landing-audit.py` (1332 lines). The selftest
block (lines 837–1289) is not production. Every `except` in the production
region, exhaustively:

| line | construct | disposition |
|---|---|---|
| 166 | `except subprocess.TimeoutExpired` (git) | raises `EvalError` → exit 2. A hang is never a verdict. |
| 171 | `except OSError` (git spawn) | raises `EvalError` → exit 2. |
| 178 | `except UnicodeDecodeError` (git output) | raises `EvalError` → exit 2 (non-UTF-8 output is not a verdict). |
| **275** | `except EvalError` **inside `root_tree()`** → `return None` | the only deliberate swallow; see §3. |
| 293 | `except EvalError` (lane `git log -z`) | `raise required_read(...)` → exit 2 (**history**). |
| 320 | `except EvalError` (fleet `git log --diff-filter=A`) | `raise required_read(...)` → exit 2 (**cutoff**). |
| 333 | `except (OSError, UnicodeDecodeError)` (draft report file) | raises `EvalError` → exit 2 (**report**, draft path). |
| 369 | `except EvalError` (lane `ls-tree corpus/SOURCES.md`) | `raise required_read(...)` → exit 2 (**tree/SOURCES**). |
| 383 | `except EvalError` (lane `cat-file blob <SOURCES>`) | `raise required_read(...)` → exit 2 (**SOURCES blob**). |
| 460 | `except EvalError` (fleet `git show HEAD:<report>`) | `raise required_read(...)` → exit 2 (**report**, committed path). |
| 537 | `except (OSError, UnicodeDecodeError)` (`--errata PATH` file) | raises `EvalError` → exit 2 (**errata**, file path). |
| 726 | `except FileNotFoundError` (`info/grafts` probe) | `return False` — a *missing* grafts file is a fact (no grafts), not a failed read. An unreadable grafts file raises `OSError` → exit 2. |
| 1313–1327 | `main()` handlers (`EvalError`, `OSError`, bare `Exception`) | all print `could-not-evaluate:` and return **2**; the bare `Exception` arm guarantees an unanticipated error is never a verdict. |

`load_errata` (line 539) calls `git(lane_repo, "show", f"{tip}:{ERRATA}")`
**without** a `try/except` — the `EvalError` propagates to `main()` → exit 2.
That is still "no catch-and-pass" (measured, §4), but it is the only required
read that does not carry the shared refusal identity → **F1**.

No other production `except` swallows a failure into a default that a verdict
depends on. `lookup()` raises `EvalError` on a short/unexpected `cat-file`
reply (lines 199–201, 231–235) instead of guessing.

---

## 3. `root_tree()` — error identity, not a verdict, not a gate

Definition (lines 266–277):

```python
def root_tree(repo, root):
    """The tree id the root commit names, or None. …"""
    try:
        tree = git(repo, "log", "-1", "--format=%T", root).strip()
    except EvalError:
        return None
    return tree if re.fullmatch(r"[0-9a-f]{40}", tree) else None
```

Call sites — **exactly three**, every one of them inside an `except EvalError`
handler of a required read, and in all three the value is used *only* to build
the message string:

* line 321 (`report_cutoff`, fleet `git log --diff-filter=A`)
* line 370 (`load_source_urls`, lane `ls-tree corpus/SOURCES.md`)
* line 461 (`audit_round`, fleet `git show HEAD:<report>`)

`grep -n root_tree tools/report-landing-audit.py` → 266 (def), 321, 370, 461.
No fourth call site, no call on a success path, no call at start-up.

Consequences, all confirmed empirically in §4:

* **It cannot create a verdict.** Its only output is the `{tree}` field of a
  refusal string that is raised as `EvalError`; there is no code path in which
  a `tree` value selects a defect, a status, or a summary field.
* **It cannot be an upfront gate.** It runs *after* a read has already failed
  (never before), and the refusal it enriches is the refusal the failed read
  already produced. A repository whose tree is missing but which is otherwise
  complete still gets an ordinary verdict (PG45 → exit 0 clean), and a
  repository with no missing object at all is never probed (PG07 → exit 0
  clean, no stderr).
* **It survives the missing tree.** `git log -1 --format=%T <tip>` reads the
  tree id from the *commit header*, so the id is available even when the tree
  object itself is absent — the refusal then names the exact missing object
  (measured: PG15/PG16 name `tip tree 1c13e47ce9f8088dc933a80123cf6a8ee2fa701d`,
  which is byte-identical to the dropped fixture object `shas["tip_tree"]`).

---

## 4. Bounded offline measurement (11 cells, current arm only)

Driver: `.ufo/waves/round-24/falsify/out/CodeRequiredReads/required_reads_probe.py`
(a copy of `/fast/scratch/hyaku/kama-r24/falsify/CodeRequiredReads/driver/required_reads_probe.py`).
It imports the pinned repository's own fixture builders
(`tests/report-audit/promisor-grid.py`, unmodified) and grades each cell with
the harness's own `grade()` against the **oracle snapshot** rows (live =
`amended` view where the case defines one).

Command (exit 0):

```
TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/CodeRequiredReads \
python3 /fast/scratch/hyaku/kama-r24/falsify/CodeRequiredReads/driver/required_reads_probe.py \
  /fast/scratch/hyaku/kama-r24/falsify/CodeRequiredReads/driver/required_reads_probe.json
```

Per-cell results — `exit` is the auditor's own exit code; "met" = the cell
satisfies the oracle's live expectation including the harness form checks
(`could-not-evaluate:` prefix, no verdict document on stdout, the reason names
the unavailable object, and never the r23 metadata refusal):

| cell | family | exit | expected | met | finding / token evidence |
|---|---|---|---|---|---|
| PG07-complete-lane-plain | control (no hole) | 0 | 0 | yes | clean document, `status=clean`, defects 0 |
| PG13-missing-lane-blob-promisor | SOURCES blob | 2 | 2 | yes | `unavailable required object: 58866b56…:corpus/SOURCES.md (051975b0ced83169116c235e7691c0a1a8313300)` — names the missing blob |
| PG14-missing-lane-blob-plain | SOURCES blob (twin) | 2 | 2 | yes | same refusal text, same blob id |
| PG15-missing-lane-tree-promisor | tip tree | 2 | 2 | yes | `…corpus/SOURCES.md (tip tree 1c13e47ce9f8088dc933a80123cf6a8ee2fa701d) … fatal: not a tree object` — names the missing tree |
| PG16-missing-lane-tree-plain | tip tree (twin) | 2 | 2 | yes | identical refusal |
| PG45-missing-unused-tree-plain | unused tree | 0 | 0 | yes | clean verdict, no stderr — a missing tree that is **not** on the read path is not a gate |
| PG17-missing-fleet-report-promisor | fleet report | 2 | 2 | yes | `unavailable required object: .ufo/reports/round-1/kama.md at fleet HEAD (tip tree b1e11739fedfb736f2936bd9addf7e4a286d462e, …)` |
| PG18-missing-fleet-report-plain | fleet report (twin) | 2 | 2 | yes | identical refusal |
| PG21-missing-ancestor-promisor | lane history | 2 | 2 | yes | `unavailable required object: the kama history of daf9cd57…: … fatal: Failed to traverse parents of commit daf9cd57…` — names the missing ancestor |
| PG25-unknown-citation-plain | proved absence | 1 | 1 | yes | verdict: defects `unresolved-full-hash` + `landed-unresolved`, token `0123456789abcdef0123456789abcdef01234567` — the diagnosis walk runs in a plain repo and yields a **verdict**, not a refusal |
| PROBE-errata-blob-missing | errata ledger | 2 | 2 | yes | `could-not-evaluate: git show 51f8d619…:registry/report-landing-errata.tsv … rc=128 fatal: bad object …` — no verdict, no silent pass (see **F1** for the form) |

Across all 11 cells: `traceback=false`, `timed_out=false`, `leaked=false`, and
`objects_acquired={"lane": [], "fleet": []}` — i.e. **no object was ever
fetched or materialised** (every probe in the harness is `--no-lazy-fetch`;
see also the fixture hazard reported by `KamaR23-2.CaseFleetBlobless`).

`PROBE-errata-blob-missing` is the one cell I authored (not an oracle row): the
ledger is present and authorized, only its blob is removed. A silent pass over
that read would have produced exit 1 (uncorrected spliced citation) or exit 0
(corrected); the observed exit is 2 → **no catch-and-pass** on the errata
read.

---

## 5. Finding F1 (low severity) — the errata read lacks the shared refusal identity

**Where:** `tools/report-landing-audit.py`, `load_errata`, line 539:

```python
    return parse_errata(git(lane_repo, "show", f"{tip}:{ERRATA}"),
                        f"{args.branch}:{ERRATA}")
```

**Observed:** the refusal is the bare git error
`could-not-evaluate: git show <tip>:registry/report-landing-errata.tsv in <repo>: rc=128 fatal: bad object <tip>:registry/report-landing-errata.tsv`.

**Why it matters (bounded):** every other required read goes through
`required_read()` and therefore states (a) the fixed class prefix
`unavailable required object:`, (b) *which* object was wanted (blob id / tree
id / path), and (c) the tip-tree identity of the store. The errata refusal
states none of that: it names the path but not the missing blob id and not the
tip tree. Under the amended contract ("missing objects actually required by
audit reads remain could-not-evaluate exit2, **with a content-derived reason**")
the reason is still content-derived (path + git's `bad object`), so no oracle
row is violated and the exit code is unchanged; but a grader of the
`names_any_of: ["$errata_blob"]` shape used elsewhere in the grid would not
find the object identity, and the refusal is not comparable with the four
sibling refusals.

**Minimal correction (NOT applied — production is read-only for this seat):**

```python
    try:
        text = git(lane_repo, "show", f"{tip}:{ERRATA}")
    except EvalError as exc:
        tree = root_tree(lane_repo, tip)
        what = (f"{tip}:{ERRATA} (tip tree {tree}) in {lane_repo}" if tree
                else f"{tip}:{ERRATA} in {lane_repo}")
        raise required_read(what, exc) from exc
    return parse_errata(text, f"{args.branch}:{ERRATA}")
```

Exit code, verdict semantics and every other observable are unchanged: the
read still refuses with exit 2; only the refusal's identity string changes.
(Overlaps with `KamaR23-2.CodeErrataBoundary`; my measurement is independent.)

---

## 6. Observations that are not defects (recorded, not claimed)

* `lookup()`'s `excluded` / `dangling` branches (lines 225–227) are
  **unreachable** in the auditor's usage, so they cannot turn an unavailable
  object into a proved-absence verdict. Verified against the git source
  (official HTTPS read of `builtin/cat-file.c`, v2.56.0): `excluded` is
  printed only under an active object filter (`LOFC_BLOB_NONE` /
  `LOFC_BLOB_LIMIT`), and `dangling` only for `DANGLING_SYMLINK`; the auditor
  calls `cat-file --batch-check` with bare hex tokens and no `--filter`.
  Observed for a missing object: `ce013625… missing`.
* The whole-store diagnosis walk (`missing_reachable`, lines 651–678) is
  **lazy**: `RepoStore.missing()` is first called from `unknown_citation` /
  `opaque_hole`, which are reached only from `refuse_unknown` /
  `apply_errata` on an *unresolved* token. PG25 shows the walk runs in a plain
  repository and still ends in a verdict (exit 1) — it is a diagnosis, not a
  precondition. No upfront gate.
* `rev-list --objects --missing=print --filter=blob:none` in a **plain**
  repository returns rc 0 on git 2.56.0 (measured) and the git 2.45 source
  carries no "only supported" die for that combination (official HTTPS read of
  `builtin/rev-list.c` / `revision.c`, v2.45.0) → no new Git-floor pressure
  from the second walk. The inherited Git ≥ 2.45 prerequisite itself remains
  open at L0 and is not claimed here.
* `grafts_effective`'s `FileNotFoundError → False` is a legitimate *absence*
  (no grafts file ⇒ no grafts), not a swallowed failure.

---

## 7. Residual risk and verification gaps (explicit)

* **Not run:** the full grid (45 cells × 2 arms), the mutation probe
  (`promisor-mutants.py`), the isolation mutants, the r23 **frozen** arm, and
  the historical parity/selftest of the harness. My cell set is 11 bounded
  fixtures; a sibling's full-grid result is still the authority for the whole
  population.
* **Not exercised:** the *draft* report path (`--report N=PATH`) with an
  unreadable file and the `--errata PATH` file branch were checked **statically
  only** (`read_report` → `EvalError`; `Path.read_text` wrapped at line 537).
* **Not exercised:** the auditor against the real production lane/fleet
  (read-only seat; the probe used synthetic fixtures only), and the cost of the
  whole-store walk on the production object stores.
* **Version:** measured on git 2.56.0 only; the inherited Git ≥ 2.45 floor is
  untested here (open at L0).
* **Fixture hazard honoured:** every probe of mine used `--no-lazy-fetch`
  (the harness helpers `object_inventory`/`object_exists`/`missing_objects`
  do; a stray `git cat-file -e HEAD:<path>` on a blobless clone would
  materialise the missing blob and destroy the premise — reported by
  `KamaR23-2.CaseFleetBlobless`).
* No production file was edited; no lane `production/.jj/index`, fleet,
  sibling, operator config, routing or service was touched.

---

## 7.1 Addendum — F2 (errata scope asymmetry): independent corroboration

**Ownership:** the primary finding and the minimal correction are
`KamaR23-2.CodeErrataBoundary`'s (their arm A8). What follows is my
independent corroboration from the required-read lane, plus one fact they do
not state: the defect is **inherited verbatim from the r23 frozen base**, i.e.
it is not a round-24 regression.

**Static (pinned source).** `apply_errata` (lines 543–586) scopes two of its
three row classifications to the audited rounds and leaves the third unscoped:

* `unmatched` — lines 553–554: `e["round"] in selected and e["line"] not in used`
* the unavailable-object refusal loop — the scope guard at line 563 (`if token is None or e["round"] not in selected: continue`) inside the loop at 561–578
* `invalid` — lines 583–585: **no `selected` guard**

**Frozen-base check (observed).** `git cat-file blob 0df800e896f6bce285a81e794ad4ae1d1e6c3a71:tools/report-landing-audit.py`
(read in the scratch clone, never from a working-tree path) has sha256
`da5041a8191e0e6ec385adc7c659ddc7544a835aff65dd45b34de623c5765af1`, byte-identical
to the oracle's `derived_from.frozen_auditor_sha256` — the frozen base I compare
against is the oracle's own frozen blob. In that blob the `invalid`
comprehension is at lines 405–407 with the same text and no `selected` filter,
`unmatched` is already scoped at 397–398, and the partial-clone refusals are at
457 / 465. In r23 this path was unreachable in practice, because r23 refused
partial clones outright (`partial clone (promisor pack)`); the round-24 repair
makes an *unavailable* object reachable on this path for the first time.
(Independent provenance confirmation of the same fact in
`KamaR23-2.CodeErrataBoundary`'s Addendum 2.)

**Measurement (3 bounded runs, my own fixture shape; evidence
`out/CodeRequiredReads/errata_scope_probe.json`).** The ledger's round-1 row is
present and authorized; one extra row for **round 2** (never audited) is added;
in two of the three runs the row's correction token is an object the lane
history references but cannot serve (its blob is dropped after the commit):

| arm | correction token | exit | result |
|---|---|---|---|
| round-2 row, correction = fabricated absent 40-hex | absent | **1** | `status=failed`, `errata_invalid=1` — a *failed verdict* about a round the audit never read |
| round-2 row, correction = unavailable object (referenced, unservable) | unavailable | **1** | `status=failed`, `errata_invalid=1` — the **same unavailable object** that the in-scope arm refuses with exit 2 is here turned into a failed verdict |
| round-1 row (audited), correction = unavailable object | unavailable | **2** | `could-not-evaluate: errata line 2: unknown: unavailable required object: 56d7b323… is referenced by the history of <lane> but the repository cannot serve it` — no verdict document |

So the amended contract's "an unavailable required object is never a clean or
failed verdict" holds **inside** the audited rounds (exit 2, content-derived,
no rescue) and is broken **outside** them: the same unavailable object yields
exit 2 in an audited round and exit 1 in an unselected one, because `invalid`
is computed over every ledger row while `unmatched` and the refusal loop are
not.

**Minimal correction** (owned by `KamaR23-2.CodeErrataBoundary`, verified on
their scratch copy, **not applied here** — production is read-only for this
seat): add `e["round"] in selected and` to the `invalid` comprehension at
lines 583–585, so an out-of-scope ledger row is ignored exactly like an
unmatched out-of-scope row (exit 0 clean) while in-scope behaviour and the
round-1..20 population stay unchanged.

**Reading of the contract (my judgement, not a claim of the oracle):** an
out-of-scope row is not evidence the audit reads, so refusing with exit 2
would be a scope error of its own; ignoring it (the proposed correction) is
the consistent reading. Either way the present exit 1 is wrong: it is a
failed verdict about a round the audit did not read, and — in the unavailable
variant — a failed verdict about an object the repository cannot serve.

---

## 8. Files written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/CodeRequiredReads.md` — this report.
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CodeRequiredReads/required_reads_probe.py` — the bounded driver (copy of the scratch copy).
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CodeRequiredReads/required_reads_probe.json` — raw per-cell evidence (exit codes, full stderr/stdout, premise shas, acquired-object deltas).
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CodeRequiredReads/cells.md` — the cell table in §4, machine-readable copy.
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/CodeRequiredReads/errata_scope_probe.json` — raw evidence for §7.1 (F2: out-of-scope vs in-scope unavailable errata correction; exits 1 / 1 / 2).
* Heavy scratch (clone, fixtures, probe root): `/fast/scratch/hyaku/kama-r24/falsify/CodeRequiredReads/` (removed after each run except the driver).

## 9. Tooling

No install, update or upgrade was performed by this seat: git 2.56.0 and
Python 3.14.8 were already present and sufficient, so the channel order in the
operator tooling directive was not entered. All pacman transactions remain
paused; no system, service or configuration mutation was made.

Report: .ufo/waves/round-24/falsify/advice/CodeRequiredReads.md
