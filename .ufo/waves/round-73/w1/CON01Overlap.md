# CON01Overlap — cross-lane overlap scan and the round-72 routed defects

Seat `CON01Overlap`, kama round 73, wave w1. Read-only: this seat wrote no lane file, ran no
mutating git/jj command in `L`, and dispatched no subagent.

Measured at lane `master` = `bc9e30599b6c6133bb094f0e7abd1a9f512778ec` (the wave-dispatch
commit; the claims freeze base is `6e961996`). Every receipt under
`.ufo/waves/round-73/w1/CON01Overlap/` starts with the `# rev=` line read at the moment it was
written; this report cites receipts, not memories.

---

## 0. Two brief corrections (recorded, not acted on)

1. **The scan path in the brief does not exist as written.** `/home/vgpnk/Projects/*-shokunin`
   matches exactly one directory, `/home/vgpnk/Projects/kimi-shokunin`, and it has no `tools/`
   (`ls: cannot access '/home/vgpnk/Projects/kimi-shokunin/tools': No such file or directory`).
   The lanes live one level down, in `/home/vgpnk/Projects/shokunin/*-shokunin` — 21 of them, 13
   with a tooling surface (`tools/`, `verifiers/` or `scripts/`). I scanned the real set and list
   the tool counts in `sibling-family-census.out`.
2. **The trailer and item 4 name two different locations.** The `Report:` trailer renders
   `.ufo/waves/round-73/w1/CON01Overlap.md`; item 4 names the directory
   `.ufo/waves/round-73/w1/CON01Overlap/`. Both exist: this file is the report, the directory
   holds the receipts.

---

## 1. Commands run

| # | Command (cwd = `L`, `PYTHONDONTWRITEBYTECODE=1` on every python) | Observed | Receipt |
|---|---|---|---|
| 1 | per-lane tool inventory + `grep -l` for the three families over `*/tools`, `*/verifiers`, `*/scripts` | 327 lines; counts below | `sibling-family-census.out` |
| 2 | seven-defect probe (§6 of the r72 closure) at seat start | see §4 | `r72-defects-state.out` |
| 3 | located evidence for each family owner (`grep -n`/`sed` over sibling sources) | 120 lines | `prior-art-legs.out` |
| 4 | per prior-art tool: its own lane `SKILL.md` mention count + first mention | 16 tools: **14 in a registry row, 1 prose-only, 1 with no mention** (+3 prose graders, all unmentioned, in the addendum) | `sibling-registry-rows.out` |
| 5 | sibling `corpus/` grep for knowledge entries on the three topics | see §2.4 | `sibling-knowledge-overlap.out` |
| 6 | `python3 tools/gate-registry-check.py --repo L` (worktree mode) | `registered 82 unregistered 0 defective 0`, exit 0 | `gate-registry-worktree.out` |
| 7 | `python3 tools/round42-selfdesc-reconcile.py --repo L --tip master` | `mismatches=1 met=False`, exit 1 | `selfdesc-at-master.out` |
| 8 | `git clone --shared` fixture, worktree snapshot committed, `gate-registry-check --rev HEAD` | `registered 85 unregistered 0 defective 0`, exit 0 | `gate-registry-snapshot.out` |
| 9 | same fixture, `round42-selfdesc-reconcile --tip HEAD` | `mismatches=7 met=False`, exit 1 | `selfdesc-snapshot.out` |
| 10 | the three frozen counting commands, read-only | C1 exit 1 `findings=80`; C2 exit 2; C3 exit 0 | `claims-live-state.out` |
| 11 | frozen-blockquote vs `PREDICATE` comparison for all three modules | 658/658, 659/659, 564/564 chars, exact | `predicate-identity.out` |
| 12 | seven-defect probe re-run after the wave's seats landed | see §4 | `r72-defects-state-final.out` |
| 13 | seven-defect probe re-run after `corpus/lessons/round-73.md` and `LOG.md` landed | see §4 | `r72-defects-state-after-lesson.out` |
| 14 | `python3 tools/pre-report-gate.py --selftest` (to learn the new tally) | `PRE_REPORT_SELFTEST pass=12 fail=0`, exit 0 | quoted in §5.2 |
| 15 | `sha256sum`/`wc -l` on `SKILL.md`, `PROVINCE.md`; knowledge-file count | `e18278db…`/1729, `51662b7a…`/310, 43 — later `b6186dd7…`/1729, `6075e5c3…`/322 | `head-table-latest.out` |

Every exit code above was read from the process, not inferred: commands 6–9 write `# exit=N`
into the receipt itself; 10 does the same per claim.

Two receipts carry a later addendum block (`prior-art-legs.out`, `sibling-registry-rows.out`) for
tameshi's three prose-grading instruments, which the first pass over `grep -l` missed because none
of them contains the words "tip", "revision binding" or "claim". Each addendum repeats its own
`# rev=` line and records the command it ran.

---

## 2. Cross-lane overlap

### 2.1 (a) Worktree / ignored-path / submodule cleanliness

What exists, in the lanes' own words:

| Lane | Instrument | Population it actually grades | Registered? |
|---|---|---|---|
| kama | `tools/round72-round-scope.py` (r72 C1) | `git status --porcelain -uall` over **the primary worktree only**; ignored paths only under `.ufo/waves/round-<N>/` | yes, `SKILL.md:312` |
| kama | `tools/round67-worktree-landing-check.py` | declared paths' worktree bytes vs HEAD blobs (no `git status` at all) | yes (gate arm 4) |
| kama | `tools/pre-report-gate.py` arm `worktree-landing` | as above | yes |
| mori | `tools/mori-unlanded-check.py` | `.ufo/waves/round-N/`, `corpus/`, `tools/`, top-level `*.md`; **"`.scratch/` and anything git ignores are outside the scope on purpose"** | yes, `SKILL.md:973` |
| kaidoku | `tools/round-42/prefile-gate.py` | round-scope uncommitted paths are **fatal**; **"ignored residue under the same scopes"** is an **"Advisory check (reported, exit-neutral)"** (`:15`, implemented at `:288` with `--ignored=matching`) | yes, `SKILL.md:1804` |
| kaidoku | `tools/round-45/frozen-path-preflight.py` | `dirty` arm: worktree clean **under the frozen pathspec only** | yes, 5 mentions |
| souji | `tools/souji-worktree-drift.py` | worktree **registration** drift (26 repositories / 27 registrations / 0 prunable), never cleanliness | yes, `SKILL.md:264` |
| souji | `tools/cand-*.sh` | `git worktree list --porcelain` used to **count** worktrees when a `.git` file (linked worktree / submodule checkout) is met | — |

**Shared ground.** Three lanes already measure "uncommitted under the round scope" (kama r72,
kaidoku, mori) and kaidoku already measures **ignored residue** under that scope. Two lanes
already walk `git worktree list` (souji counts registrations; kama does not).

**The one leg C1 adds** — and it is exactly one leg per survivor, not a re-implementation:

* **A5 `worktree`**: no lane grades a *linked worktree's* `git status`. souji lists the
  registrations but grades drift of the registration set, not the content; kama's r72 `stray` case
  runs `git status` from the primary checkout, which cannot see another worktree's edits.
  C1 adds *the same grader over a new population*.
* **A6 `ignored-older-label`**: kaidoku measures ignored residue but **deliberately neutralises it
  (exit-neutral)**; mori excludes ignored paths **by policy**; kama r72 makes them fatal but only
  under `round-<N>`, so a valid label for round `N-2` hides round-`N` ignored work. C1 crosses the
  ignore boundary with the `M >= N` bound and no allow-list escape.
* **A7 `submodule`**: `git status` in the parent reports a submodule as one line unless
  `--ignore-submodules=none` is passed, and `submodule.<name>.ignore=all` suppresses even that.
  No lane owns this; C1's case runs `git status -uall` **inside** each initialized submodule and
  re-reads the parent at `--ignore-submodules=none`.

### 2.2 (b) Receipt tip / claim binding

| Lane | Instrument | Binds | Reads a citing prose line? |
|---|---|---|---|
| tameshi | `tools/receipt-revision-gate.py` (r56, 359 lines) | a receipt's `rev=` to `--certified REV` **taken from the caller**; `--paths FILE` admits an earlier revision whose bytes are identical on those paths | no |
| tameshi | `tools/receipt-commit-bind.py` (r65/r66) | receipt **names in commit messages** to the commit bytes that carry them | no (commit message ≠ record prose) |
| tameshi | `tools/command-binding.py` | argv/cwd/revision/exit/stdout of a declared bundle against a caller-owned expected file | no |
| tsukuroi | `tools/check-revision-binding.py` (1591 lines) | whether the lane's own `--revision` gates are *bound the same way* | no |
| chousa | `tools/receipt-pin.py` | `REVISION=` header ↔ `git cat-file blob REVISION:PATH` (header self-consistency vs the pinned blob) | no |
| kaidoku | `tools/round-62/base-binding-sweep.py` | each annotation's `base:` value, threaded per receipt | no |
| kotodama | `tools/harness/receipt_guard.py`, `check-receipt-seq.py` | receipt-write preflight / sequence discipline | no |
| tameshi | `tools/pointer-recheck.py` (r71) | a record's cited **line pointer** still hits its needle at the revision the record names | **yes — but the revision is manifest data, not the sentence** |
| tameshi | `tools/figure-attribution.py` (r68) | a record **figure** pinned to a named receipt lives in *that* receipt's committed bytes (0 occurrences of `rev=`) | yes — content attribution, not header identity |
| tameshi | `tools/count-recheck.py` (r70) | a record's printed **count** equals what its named command prints at the revision the record names | yes — count, not revision |
| kama | `tools/round72-receipt-tip-binding.py` | the cited receipt **population** of the round's own record: exists, header, ancestor-of-tip, `rev..tip` = record-only | no |

**Shared ground.** Every sibling binds a receipt to a revision where the revision is an *input*
(a flag, a commit message, a header field, or a manifest cell). Three tameshi instruments do grade
record **prose**, but each grades *content* — pointer target, figure bytes, re-run count — with the
revision supplied by the manifest. None reads what the **citing line claims about the revision**.

This is not a near-miss invented here: tameshi's own manifest schema already carries the doctrine
C2 mechanises — `record_rev (40-hex; pin the revision whose bytes you verified against, never
"tip")` (`tools/pointer-recheck.py:58`). tameshi states the rule for its *manifest*; nothing states
or grades it for a **prose** claim, which is the exact shape r72's B6 survivor exploited.

**The one leg C2 adds.** The claim pass runs over the same two record blobs at the tip
(`SCORECARD.md`'s `## Round <N>` section, `corpus/lessons/round-<N>.md`) and grades the direction
nobody grades: a line that says **`at the tip` / `at the report tip` / `report tip`** must cite a
receipt whose own `tip=`/`rev=` header **is** that tip. That is the exactly-inverted test from
tameshi's `--paths` allowance: tameshi asks "may this earlier revision stand for the certified
one?" (byte identity); C2 asks "does the sentence make the claim the header cannot support?" —
a receipt measured earlier is admissible *only when the citing line names that revision*.

### 2.3 (c) Host identity / drift

| Lane | Instrument | Grades | Does it grade the *identity*? |
|---|---|---|---|
| kama | `tools/round71-province-host-claims.py` | each `province-host:TAG` **marker** and prose claim against a declared surface's presence | no |
| kama | `tools/round65-province-host-audit.py`, `round65-host-census.py` | the round-65 absent-surface list / which instruments run here | no |
| kotoba | `verifiers/check_host_skill_surfaces.py` | installed host `*/SKILL.md` bytes vs the lane copies (identical / drifted / lane-absent) | no (skill bytes, not host) |
| kumitate | `scripts/surface-probe.mjs` | live product surfaces (`ufo-sighting surface --json`, dispatcher status) | no |
| tsukuroi | `corpus/knowledge/host-drift-recheck-r64.md` | 20 host **planes** (packages, systemd, journal, drivers, update-safety) re-measured against a stored snapshot, `recheck: 30d`; its header names the host in prose (`host plazir27`, kernel `7.2.11-arch1-1`) | no — prose, no counter |

**Shared ground.** Two lanes record a host identity (`tsukuroi` in a knowledge header, `kama` in
PROVINCE.md's round-65/67 Windows notes and the round-71 re-derivation), and nobody grades it.

**The one leg C3 adds.** `Round-<N> host-identity block (YYYY-MM-DD)` with the triple
`uname -s` / `uname -m` / `/etc/os-release` `ID`, newest block graded, append-only (a host move is
answered by appending, never editing). It does not re-probe surfaces — it grades the one sentence
`round71-province-host-claims.py` structurally cannot: "the host this record describes is the host
we are on". A kernel-only update leaves the triple unchanged, which is the point.

### 2.4 Knowledge-entry overlap (what the sibling corpora already hold)

Located by grep over `*/corpus` (`sibling-knowledge-overlap.out`); these are the entries a
future round should read *before* writing another one on the same ground:

* **(b)** `tameshi/corpus/knowledge/receipt-revision-binding.md`, `required-command-binding.md`;
  `chousa/corpus/knowledge/receipt-identity-r65.md`, `receipt-digest-provenance-r67.md`,
  `line-binding-r31.md`; `kotodama/corpus/knowledge/verification/append-only-record-verification.md`,
  `header-conformance-readings.md`.
* **(a)** `souji/corpus/knowledge/count-objects-linked-worktree-garbage.md`,
  `git-repo-structure-common-dir.md`, `jj-colocation-receipts.md`.
* **(c)** `tsukuroi/corpus/knowledge/host-drift-recheck-r64.md`,
  `systemd-unit-load-plane-r73.md`; `chousa/corpus/knowledge/host-source-resolution-r66.md`.

kama's two new entries land the same day as these: `corpus/knowledge/round-scope-survivor-cases.md`
and `corpus/knowledge/host-identity-drift-gate.md` (both untracked at seat time). Neither name
collides with a sibling path, so the overlap is topical, not duplicative — but the drift entry
should cite `tsukuroi/host-drift-recheck-r64.md` as the plane-level neighbour if it wants to be
re-openable by a reader of either lane.

### 2.5 Registry presence in the owning lane (`sibling-registry-rows.out`)

Named in an actual registry row (14 of the 16): `mori-unlanded-check.py` (1),
`kaidoku/round-42/prefile-gate.py` (1), `kaidoku/round-62/base-binding-sweep.py` (1),
`souji-worktree-drift.py` (1), `tameshi/receipt-revision-gate.py` (row at `:1547`),
`tameshi/command-binding.py` (row at `:2062`), `chousa/receipt-pin.py` (1),
`tsukuroi/check-revision-binding.py` (1), `kotodama/harness/receipt_guard.py` (1),
`kotoba/check_host_skill_surfaces.py` (1), `kumitate/surface-probe.mjs` (1),
`kama/tools/round72-round-scope.py` (`:312`), `round72-receipt-tip-binding.py` (`:313`) and
`round71-province-host-claims.py` (`:311`).
`kaidoku/tools/round-45/frozen-path-preflight.py` is named in **prose only** (5 mentions, no row).
`tameshi/tools/receipt-commit-bind.py` has **0** `SKILL.md` mentions — it is a lane instrument with
no registry row; that is tameshi's finding, not kama's, and it is status-neutral here. The same is
true of tameshi's three prose graders: `pointer-recheck.py`, `figure-attribution.py` and
`count-recheck.py` each have **0** `SKILL.md` mentions (`sibling-registry-rows.out`, addendum 2).
Whether that is a defect depends on tameshi's own population rule, which is theirs to define; for a
kama reader the practical consequence is that the nearest prior art to C2 is **not discoverable
from tameshi's registry** and has to be found in `tools/` or via a lane lesson.

### 2.6 Ownership call (one sentence per family)

* **(a) uncommitted cleanliness** is a *shared* class, not an owned one: kama owns the fatal
  whole-repo form, kaidoku owns the fatal round-scope form plus an exit-neutral ignored residue,
  mori owns a scoped form that excludes ignored paths by policy. **Nothing owns linked-worktree
  content or submodule content**, which is the whole of C1's added leg.
* **(b) receipt-to-revision binding** is **tameshi's** (six instruments now counted: revision gate,
  commit bind, command binding, plus three prose graders — pointer, figure attribution, count),
  with chousa owning header↔blob identity and kaidoku owning `base:` threading; kama r72 owns *the
  record's cited population*. tameshi's prose graders take the revision from a **manifest** and
  grade **content**; tameshi's own schema forbids the value `"tip"` there. **Nothing grades a prose
  sentence's *tip claim* against the receipt it cites**, which is C2's added leg — and it is the
  only leg that composes with tameshi's corpus rather than replacing it (it enforces, on prose, the
  doctrine tameshi already writes into its manifests).
* **(c) host** is split three ways and nobody owns identity: kama owns province *surface markers*
  (`round71`), tsukuroi owns host *plane* drift with a 30-day recheck, kotoba owns installed *skill*
  bytes. **Nothing owns "the recorded host is the host we are on"**, which is C3's added leg.

---

## 3. Contradictions stated, not smoothed

1. **Ignored paths: three lanes, three policies.** mori excludes them *by design*; kaidoku measures
   them and neutralises the result *by design* (`exit-neutral`); kama r72 makes them fatal inside
   `round-N`. r73 adds a fourth: fatal with an `M >= N` bound. None of these is wrong inside its
   own lane — but a fleet reader who assumes "ignored residue is graded" is right for kaidoku only
   as a *warning*. There is no shared definition of the class.
2. **Admissibility of an older revision.** tameshi: an older revision is admissible when its bytes
   are identical **on declared paths** (`--paths`). kama r72: an older revision is admissible when
   it is an ancestor and the delta is **record-only**. Same question, two incompatible tests;
   neither is a superset, so a receipt can be green under one and red under the other.
3. **Host recording: prose vs counter.** tsukuroi's `host-drift-recheck-r64.md` records the host
   and a 30-day recheck in a header a human reads; kama's C3 will grade a block a counter reads.
   Neither grades the other's artifact, and C3's block does not inherit the 30-day cadence.
4. **Measurement artefact worth naming for L1:** `tools/gate-registry-check.py` worktree mode reads
   the counter **population** from `git ls-tree -r HEAD` (`tracked_counters`, `:117-134`) but
   `SKILL.md` from disk. A counter that is not yet committed is therefore **outside the population**
   and its missing row is invisible. Measured: `82` before the commit, `85` on the snapshot (§5).

---

## 4. Round-72 §6 routed defects — closed / open

Probed three times, because the record landed while this seat ran: `r72-defects-state.out` (seat
start), `r72-defects-state-final.out` (after all three modules and the three registry rows) and
`r72-defects-state-after-lesson.out` (after `corpus/lessons/round-73.md` and `LOG.md` appeared).
Items 1, 2, 5 and 7 did not move across the three probes; items 3 and 4 did, on the third.

| # | Defect | State | What shows it |
|---|---|---|---|
| 1 | Stale C2 tally and line count | **OPEN** | `SCORECARD.md` still carries `pass=14 fail=0` **twice** and `14 arms` **once** (`grep -c` → 2 and 1); committed tool at master is 961 lines with 16 `_arm(` calls (`git show master:tools/round72-receipt-tip-binding.py \| wc -l` → 961; `grep -c '^    _arm('` → 16). Neither the report nor the §Round 72 row was touched by r73 so far. |
| 2 | C2 cannot grade the lane's own record | **OPEN (module built; SCORECARD section missing)** | Module now exists in the worktree (`test -f tools/round73-receipt-claim-binding.py` → 0) but is **not at master** (`git cat-file -e master:…` → 128). `corpus/lessons/round-73.md` now exists (`test -f` → 0), but `SCORECARD.md` still has no `## Round 73` (`grep -c` → 0), so the frozen counting command exits 2: `RECEIPT_CLAIM_BINDING_UNREADABLE … SCORECARD.md at master carries no '## Round 73' section`. r72's red is reproduced verbatim and, per the frozen plan, stays red as history: `RECEIPT_TIP_BINDING round=72 cited=138 bound=0 unbound=105 shifted=24 stale=9` (`.ufo/waves/round-72/measured/after/receipt-tip-binding-at-f3cd3623.out:141`). |
| 3 | `used-by` old→new table location | **CLOSED (artefact); r72 pointer still stale** | `corpus/lessons/round-73.md:131` now carries "`used-by` changes, old → new (CORPUS.md rule 2)" and its S175 row (`:135`) records the round-72 additions `corpus/lessons/round-72.md`, `corpus/knowledge/receipt-tip-binding.md` alongside round 73's. The rule-2 artefact therefore exists in a lesson — but the r72 sentence that misdirected a reader is untouched: `corpus/lessons/round-72.md:102` still reads "(old→new recorded in its report)". |
| 4 | Rejected SOURCES row with reason + flip | **CLOSED** | `corpus/lessons/round-73.md` §Gate carries `grep -c 'REJECTED'` → **2** and `grep -c 'flip:'` → **2**: own-work receipts → `REJECTED: lane-authored control bytes are evidence a counter reads, not a learnable external source; flip: none`, and the deferred package → `REJECTED: no entry from the package was re-grounded in round 73 …; flip: a later round that re-opens an entry in full and passes the per-entry PROVINCE.md scope and QUALITY.md bar checks`. The rejection is now a curation artefact, not a prose note. (The r72 §Gate still carries the old prose form; the form is repaired forward, not retro-edited.) |
| 5 | Stale-lane line not re-derivable | **OPEN** | `/home/vgpnk/Projects/shokunin/.ufo/reports/round-72/kama.md:199` still says "the round reported inside one driver tick"; the r73 report does not exist yet (`test -f …/round-73/kama.md` → 1). r72's launch→complete is 22:34:21→23:08:57 = **34 m 36 s**, ≈ 4.6× the 450 s fleet tick. |
| 6 | Before-control receipts lack exit codes | **CLOSED** | `.ufo/waves/round-73/measured/before/score-survivors-base.out` carries two `# exit=` lines and `sources-census-start.out` one (`# exit=0`): `grep -c '^# exit='` → 2 / 1. |
| 7 | Unreceipted disclosure (`unrestored 33 → 41`) | **OPEN** | `grep -rln 'unrestored' .ufo/waves/round-73/ --exclude-dir=CON01Overlap` returns only this seat's own report (`w1/CON01Overlap.md`) — the `--exclude-dir` covers the receipt directory, not the sibling `.md`. No `append-only-audit.py --repo` receipt exists in the wave: the only `append-only-audit` hits are `SCT01SurvivorRecon/ignored-bound.out:13-14`, which list another lane's ignored `__pycache__` paths, not a re-run of the count. |

Nothing above was repaired — the assignment says "do not repair anything", and each open item is a
file this seat does not own.

---

## 5. Registry and self-description (item 3)

### 5.1 Pre-commit run — green, and vacuous for this round

```
PYTHONDONTWRITEBYTECODE=1 python3 tools/gate-registry-check.py --repo /home/vgpnk/…/kama-shokunin
registered 82 unregistered 0 defective 0
# exit=0
```

`git ls-tree -r --name-only HEAD | grep -c 'tools/round73-'` → **0**. The three new modules are
untracked, so the population does not contain them. This run is **not** evidence that the three
rows are correct; it is evidence about the 82 older counters only.

### 5.2 Post-landing snapshot — real measurement of this round's tree

Because L1 has not committed, I built the measurement in scratch rather than assert it:
`git clone --shared` of `L` under `$S`, copied the ten non-`.ufo` paths `git status` names, asserted
`git -C $C rev-parse --show-toplevel` equals the clone, committed with the throwaway identity
(`fixture <fixture@invalid>`), fixture tip `ac3ff80b`.

```
python3 tools/gate-registry-check.py --repo <fixture> --rev HEAD
registered 85 unregistered 0 defective 0
# exit=0
```

**All three new rows are registered and well-formed** (`Round scope v2` `SKILL.md:314`,
`Receipt-claim binding` `:315`, `Province host drift` `:316`), and the population rises 82 → 85
exactly as the three modules predict.

Same snapshot, the self-description reconciler:

```
python3 tools/round42-selfdesc-reconcile.py --repo <fixture> --tip HEAD
r41=6 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 closure_ptr=0
mismatches=7 maxN=72 met=False
# exit=1
```

The `r41` six are the head-table pins this round's own files moved; `closure_ptr` is r73's inherited
red. Values re-derived now (and they will move again as the lesson lands — L1 must re-derive at the
record tip):

| Head-table value | Cited at master | Observed (snapshot → last read before yield) |
|---|---|---|
| `SKILL.md` sha256 | `972f124e…` | `e18278db06e1205f…` → `b6186dd716dd483a…` |
| `SKILL.md` lines | 1726 | 1729 (both reads) |
| `PROVINCE.md` sha256 | `7fa09fab…` | `51662b7a67bd1054…` → `6075e5c38f21e56b…` |
| `PROVINCE.md` lines | 308 | **310** → **322** |
| `corpus/knowledge/*.md` (filtered count) | 41 | **43** (both reads) |
| `PRE_REPORT_SELFTEST` | `pass=8 fail=0` | **`pass=12 fail=0`** (re-run: exit 0) |

Two of the six moved *again between the snapshot and the last read* (`SKILL.md` `b6186dd7…`,
`PROVINCE.md` `6075e5c3…` with 12 more lines). That is the point of listing them: they are derived
values, and L1 must re-derive them at the record tip rather than copy this table.

### 5.3 The `closure_ptr` red predates this round

`round42-selfdesc-reconcile --repo L --tip master` → `mismatches=1 met=False`, exit 1,
`detail: closure_ptr: calibration row latest outside closure is round-71; newest at tip is round-72`.
`SCORECARD.md:18` still names `corpus/lessons/round-71-verifier-spotcheck.md` and "including round 71",
while `corpus/lessons/round-72-verifier-spotcheck.md` landed at the freeze base `6e961996`. This is
a **base-revision defect**, not one of this round's seats' making: the r72 closure commit post-dates
r72's own record, and nothing between `6e961996` and `bc9e3059` refreshed the pointer. The
pre-report gate's `selfdesc` arm runs at `{tip}`, so **it is red at the report tip until L1 fixes it.**

### 5.4 What the L1 must still land

1. **The commit itself.** Until then `gate-registry-check` is vacuous (82, new modules outside the
   population) and every receipt in this wave measured an uncommitted tree.
2. **`SCORECARD.md` head table** — the six values in §5.2, re-derived at the record tip, not copied
   from this table.
3. **The calibration row's closure pointer** — round-71 → round-72, and "including round 71" →
   "including round 72" (`closure_ptr` = 0 today; `met=False`).
4. **`SCORECARD.md` `## Round 73` and `corpus/lessons/round-73.md`.** C2 exits 2 without them
   (`RECEIPT_CLAIM_BINDING_UNREADABLE … no '## Round 73' section`); the `planned` fact also expects
   `### Planned (round 74)` once `## Round 73` exists.
5. **The r72 §6 record corrections.** Closed by this round's record so far: **item 3** (the rule-2
   old→new table is now in `corpus/lessons/round-73.md` §Gate and names the round-72 additions),
   **item 4** (two `REJECTED: …; flip: …` rows in the same table), **item 6** (before receipts carry
   `# exit=`). Still open: **item 1** (`SCORECARD.md`'s `pass=14` twice and `14 arms` once),
   **item 2** (pending `## Round 73`), **item 5** (the r73 report's own stale-lane line),
   **item 7** (no `append-only-audit.py --repo` receipt under the wave).
6. **Re-run at the committed tip:** `gate-registry-check --rev master` (expect `registered 85
   unregistered 0 defective 0`) and `round42-selfdesc-reconcile --tip master` (expect
   `mismatches=0 met=True`). If either differs, the difference is a real finding, not a formatting
   one.

---

## 6. Live state of the three claims (context only — not this seat's verdict)

`claims-live-state.out`, read-only, one run each at seat time:

* **C1** `ROUND_SCOPE_V2 round=73 cases=6 findings=80`, exit 1 — every finding is a `stray` record
  over the round's own uncommitted wave files, which is the expected mid-round state (the scored
  run is at the record tip, and the whole wave must be committed before it can be green).
* **C2** exit 2 — `SCORECARD.md` carries no `## Round 73` section; the lesson alone is not enough
  (§5.4 item 4).
* **C3** `PROVINCE_HOST_DRIFT blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0`,
  exit 0 — the round-73 block EX03 appended already matches this host.

**Predicate identity** (`predicate-identity.out`): each module's `PREDICATE` is one line and is
byte-equal, after whitespace normalisation, to the corresponding blockquote in
`plans/round-73-claims.md` — 658/658, 659/659 and 564/564 characters. That is a read-only
cross-check of the freeze sentence, not a verdict on any claim.

---

## 7. Limits of this seat

* I verified **no claim**. The three counting commands above were run once each to record state;
  their scoring belongs to the executors, the reviewer and the two critics.
* I ran no lane gate, and exactly one selftest (`pre-report-gate.py --selftest`, to learn that the
  tally moved 8 → 12). Everything else is `grep`, `sed`, `wc`, `sha256sum`, `git` read-only
  (`rev-parse`, `ls-tree`, `cat-file`, `show`, `status`), and the two reconcilers.
* One scratch clone existed: `git clone --shared` under
  `/fast/scratch/hyaku/kama-r73/CON01Overlap/`, with the toplevel assertion and the throwaway
  identity, removed on exit. The scratch root was deleted before this report was yielded.
* No `__pycache__` was created under the wave dir (`PYTHONDONTWRITEBYTECODE=1` on every python
  invocation; `find .ufo/waves/round-73 -name '__pycache__' -o -name '*.pyc'` returns nothing, and
  the round-scope counter's own `ignored` case reported 0 findings in the live run). `tools/__pycache__`
  exists but predates this seat: no file in it is newer than 22:49.
