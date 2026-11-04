# CON01Overlap — cross-lane overlap scan + inherited-defect disposition

Seat: `CON01Overlap` (connector, axis `adjacency`), kama round 72 wave 1. Read-only: no lane or
sibling file was edited, no gate was executed in a sibling lane, no sibling worktree was touched.

- kama read at `HEAD = a3cc39f0` (`git show HEAD:<path>` for record surfaces; worktree files for
  `tools/` because wave seats are writing them concurrently). Date 2026-11-03.
- Siblings read from `/home/vgpnk/Projects/shokunin/*-shokunin/{tools/*,SKILL.md}` worktrees.
  Registration line numbers are that lane's own `SKILL.md` at scan time.
- Host: `git version 2.56.0`.
- The two frozen claim predicates are taken verbatim from `plans/round-72-claims.md`. Nothing below
  amends them; §5 lists contradictions and under-specifications for the L1, not edits.

## 1. Prior art by purpose

### 1a. Receipt → revision / tip binding (C2's family)

| lane | path (registry) | predicate | exit map | kama disposition |
|---|---|---|---|---|
| tameshi | `tools/receipt-revision-gate.py` (`SKILL.md:1547`) | every named receipt carries exactly one distinct `rev=`; for `positive`/`verdict` it must equal `--certified` (or name a revision byte-identical over `--paths`); `control` tokens must be ancestor-or-equal | `0` PASS · `3` REFUSED with named `RECEIPT_*` codes · `2` certified revision unresolvable · `1` usage | **Adopt** the role taxonomy, `\brev=` token extraction and `merge-base --is-ancestor` leg. **Re-derive** the population (round self-record, not a caller list) and the `shifted` class, which it does not have. This is the named precedent, and it binds *one* revision per receipt — it never asks what happened after that revision. |
| tameshi | `tools/receipt-commit-bind.py` (unregistered; in-file exit map) | a commit message naming an evidence/`tools/` path must carry or resolve it in that commit's tree; range sweep with three arms | `0` clean · `1` defects · `2` setup **including "nothing to check"** | **Adopt** the fail-closed rule: an empty population is exit 2, never a vacuous green. Its arm-1 blind spot (a path named nowhere in the range is never a candidate) is the same vacuity C1's kill rule forbids. |
| tameshi | `tools/receipt-window.py` (`SKILL.md:2196`) | a receipt is admissible only with a unique id, a 64-hex instrument sha, and an aware interval; a receipt measured with frozen bytes must end before the edit window starts | `0`/`1`/`2`/`64` | **Adopt** the edit-window non-overlap idea — it is a *stronger* `shifted` (time-bound rather than path-bound). **Re-derive**: kama receipts carry no `measurement_interval`, so C2 can only bind revision + delta paths. |
| kotodama | `tools/check-receipt-seq.py` (unregistered in `SKILL.md`; in-file contract) | header equality `stamped == evaluated == measured`, tree oid, counter sha; `--lands` reads committed bytes at a revision and prints `moved_past=True` when `main` has moved past it; `--topo` requires the carrying commit's parent to equal the stamped revision | `0`/`1`/`2` | **Adopt** committed-bytes-at-rev reads and the `moved_past` signal. **Re-derive** the verdict: kotodama states the flag is "never a verdict change", so C2's `shifted` is the first gate to grade it. |
| souji | `census/round-57/c2-counter.py` (`SKILL.md:765`) | every manifest receipt binds a durable full-40 `rev=`, an `EXIT=`, and a matching `instrument_sha256=`; a commit reachable only from `refs/jj/*` is `KEEP-ONLY` | `0`/`1`/`2`; selftest `control=FALSE-GREEN-REJECTED` | **Adopt** the durability rule (jj keep refs are not durable) and the instrument-sha leg. **Do not duplicate** its ancestry/delta work — it grades none. |
| chousa | `tools/receipt-pin.py` (`SKILL.md:159`) | receipt header `REVISION=` must equal `--revision` and `SHA256=` must equal the blob at `REVISION:PATH` | `0` PASS · `1` malformed/inconsistent · `2` usage/environment | **Adopt** digest-of-committed-bytes as an optional third leg. **Do not duplicate** now: it grades a receipt's *content*, not its binding to a tip. |
| tsukuroi | `tools/check-cited-receipts-r62.py` (`SKILL.md:5371`) | every `.ufo/waves/round-<N>/…` path named by any tracked text blob at REV exists as a blob in the *same* REV tree | `0`/`1`/`2` | **Adopt** the citation grammar and the round-scoping rationale (whole-history would be permanently red over other repos). This is C2's `stale` class at the same revision; C2 moves the existence check to the tip. |
| mado | `tools/mado-receipt-citecheck.py` (unregistered) | caller-named artifacts' path citations resolve in `git ls-tree -r <rev>`; top-anchored, fail-closed extraction grammar | `0`/`1`/`2` | **Adopt** the grammar (`tops`, boundary set, trailing-punctuation trim, 4 MiB cap). **Re-derive** the population: kama's is the round self-record. |
| kama | `tools/round68-receipt-pointer-audit.py` (registered, in-lane) | section-relative `` `measured/<rest>` `` pointers resolve at `--rev`, with brace/glob expansion and an append-only resolution ledger | `0`/`1`/`2` | **Do not duplicate**: it grades a different pointer class (section-relative `measured/` only) and already owns expansion rules C2 should reuse, not re-implement. |
| tsukuroi | `tools/check-revision-binding.py` + `tools/_revision.py` (`SKILL.md:1902`, `:2079`) | every gate's `--revision` binds identically: `HEAD`/`@`/branch → `E-REVISION-INVALID`; unlanded → `E-REVISION-NOT-LANDED`; unpushed → `E-REVISION-NOT-PUSHED` | `0`/`1`/`2` | **Adopt the semantics** for C1/C2's own `--tip` (kama has no shared binder; each counter parses its own). **Do not port** the judge or its matrix. |

### 1b. Pre-report aggregation (C1's family, aggregation half)

| lane | path (registry) | predicate | exit map | kama disposition |
|---|---|---|---|---|
| souji | `tools/souji-pre-report-gate.sh` (`SKILL.md:256`) | five checks: local tip == remote tip; report non-empty; exactly one `## SHONEN`; **whole-lane** `git status --porcelain=v1 --untracked-files=all` empty; prereg non-empty. `--contract` adds a report-contract check | `0` all PASS · `1` any FAIL · `2` usage | **Adopt** two rules: the always-pass FALSE-GREEN fixture in `tests/fixtures/r27-pre-report-gate.sh`, and "printed FAIL with exit 0 is a failure" (its contract arm prints `vacuous success` when no `check-*` line appeared). **Re-derive** the arms: kama aggregates instruments, souji aggregates prose/report facts. |
| kasegi | `corpus/instruments/r46-landing-gate.py` (`SKILL.md:1163`) | `--pre-report`: tree-clean, jj-state, remote-tip, placeholders. `--post-report`: report-readable, cited hashes resolve, ancestor, **final-is-tip**, date order, SHONEN heading | `0`/`1` (`landing-gate … exit=0|1`); selftest `cases=30` | **Adopt** the post-report `ancestor` + `final-is-tip` arm: C2 is the receipt-level instrument of exactly that claim, and kasegi still checks it by hand-written report facts. **Do not duplicate** — kama consumes only its own instruments as evidence. |
| tsukuroi | `tools/check-seat-scope.py` (`SKILL.md:1901`) | every seat report closes with a truthful `Scope: executed=…`; a non-`none` value requires `EXEC-AUTHORIZED`; `--revision` bound via `_revision.py` | `0`/`1`/`2` | **Do not duplicate** (population is seat reports). **Adopt** its honesty clause: counts are declarations, never verified executions — the same sentence C1's `findings=<f>` and C2's `bound=<b>` need. |
| souji | `tools/souji-landing-gate.py` (`SKILL.md:229`) | registry-cited scripts parse; pins match committed bytes; seat-reported failures are carried into the lesson; cited-path integrity | `0`/`1`/`2` | **Do not duplicate** (landing-claim consistency, not round scope). Its "read committed bytes, never `git archive`" provenance rule is worth copying verbatim. |

### 1c. Round-scope / cleanliness / ignored-file / whole-tree porcelain (C1's family, scope half)

| lane | path (registry) | predicate | exit map | kama disposition |
|---|---|---|---|---|
| kaidoku | `tools/round-42/prefile-gate.py` (`SKILL.md:1804`) | (a) every wave settled; (b) `git status --porcelain -z` clean under **four** round scopes (`.ufo/waves/round-N/`, `corpus/evidence/round-N/`, `plans/`, `tools/round-N/`); (c) no stray `*.err`; (d) lesson `w*/Name.md` pointers resolved at HEAD. `--ignored=matching` residue is **advisory only** | `0` green · `1` red · `2` argparse usage error. Its registry row discloses that a root which is not a work tree also exits `1` via `SystemExit` "although nothing was evaluated" | **Closest single precedent to C1.** **Adopt**: multi-scope round pathspec, `-z` form, rename `src` handling. **Re-derive**: grade the ignored class as a *finding* — here it is `WARN`, exit-neutral, which is exactly the vacuity C1 removes. **Do not copy its exit map**: an unevaluable root is a finding here; C1's frozen map sends "not a git repository" to `2`. |
| kaidoku | `tools/round-29/prefile-check.sh` (`SKILL.md:1363`) | whole-tree `git status --porcelain` empty (with `GIT_OPTIONAL_LOCKS=0`) and two freeze gates green | `0` PASS · `1` FAIL · `2` usage/unreadable | **Adopt** whole-tree scope as the complement to C1's case B. Its recorded limit ("cannot see a still-running seat"; an untracked-only mutant is caught only by an untracked-only probe) is the honest boundary C1's receipt should repeat. |
| kaidoku | `tools/round-45/frozen-path-preflight.py` (`SKILL.md:1761`) | arms `commit` (no commit in FREEZE..REV touches a frozen pathspec), `restored`, `blob`, `dirty` (`status --porcelain -z`), `pathspec` | `0`/`1`/`2` | **Adopt the delta-sweep method** for C2's `rev..tip` arm — and its documented merge blindness (`git log --name-only` misses a merge's own resolution edit; the tool uses `-m --diff-merges=first-parent`). See §5.1. |
| mori | `tools/mori-unlanded-check.py` (`SKILL.md:973`) | round-scoped unlanded: `.ufo/waves/round-N/`, `corpus/`, `tools/`, top-level `*.md`; **".scratch/ and anything git ignores are outside the scope on purpose"** | `0` `UNLANDED=clean` · `1` `UNLANDED=dirty paths=K` · `2` setup | **Do not duplicate**; it is the named contrast. mori excludes the ignored class by design — C1's case C is the one instrument that grades it. |
| mori | `tools/mori-index-clean.sh` (`SKILL.md:904`) | staged or intent-to-add entries fail; **refuses a verdict when porcelain v1 and v2 disagree** | `0`/`1`/`2` | **Adopt** the v1/v2 disagreement refusal: a one-line anti-vacuity check C1 can add or at least name as a limit. |
| souji | `tools/souji-fleet-root-census.py` (`SKILL.md:675`) | top-level entries with kind/tracked/ignored, ignored computed per name by `git check-ignore --no-index` (**never a listing**) | tool, read-only, no gate verdict | **Adopt the caveat, not the tool**: `--no-index` answers "would this path be ignored", including *tracked* paths, and a recursive listing would walk operator-protected subtrees. See §5.2. |
| souji | `tools/souji-verify.sh`, `souji-quarantine.sh`, `cand-*.sh` (not round gates) | `status --porcelain --untracked-files=all --ignored=matching -- <target>` used as the precondition of a destructive operation | `0`/`1` | **Adopt the pattern only** (empty output is the precondition). These are not gates over a round. |
| kama | `tools/round67-worktree-landing-check.py` (`SKILL.md:1709`) | every declared path's worktree bytes equal its HEAD blob (`DIRTY`/`MISSING`/`UNTRACKED`/`UNREADABLE`) | `0`/`1`/`2` | **Do not duplicate**: it compares bytes; C1 classifies git state. C1's arm-6 should compose with it, not replace it. |

## 2. Adopt / re-derive / do not duplicate — one sentence each

- **Adopt (C2):** tameshi's `\brev=` extraction + role taxonomy + `merge-base --is-ancestor`; kotodama's committed-bytes-at-rev reads and `moved_past`; souji-r57's durable-ref and instrument-sha legs; tsukuroi-r62/mado/`round68` citation grammars; tameshi `receipt-commit-bind`'s "empty population = exit 2".
- **Adopt (C1):** kaidoku r42's multi-scope round pathspec + `-z`; mori's v1/v2 disagreement refusal; souji's FALSE-GREEN control fixture and "printed FAIL, exit 0" refusal; kasegi's final-is-tip/ancestor post arm.
- **Re-derive (genuinely new):** C2's `shifted` **verdict** (kotodama only flags), and its *instrument-input allow-list* — no sibling distinguishes "record paths" from "instrument inputs", so nothing can be adopted for that leg.
- **Re-derive (C1):** grading the ignored class as a finding (kaidoku has the detection but downgrades it to advisory), and the case-A label check (no sibling anchors a round label on a lane-owned freeze plan at a revision).
- **Do not duplicate:** kama's own `pre-report-gate.py` arms 1-5, `round67`, `round68`, `report-landing-audit.py`, `gate-registry-check.py`; souji's landing gate; tsukuroi's seat-scope and revision-binding judge; mado's citecheck; mori's unlanded check.
- **Registry hygiene:** three of the strongest precedents (kotodama `check-receipt-seq.py`, mado `mado-receipt-citecheck.py`, tameshi `receipt-commit-bind.py`) have **no `SKILL.md` row**. C1/C2 must not repeat that: both rows are SCR03's assignment, with a full exit map including `2`.

## 3. Inherited defects — disposition

Round-71 verifier spot-check (`corpus/lessons/round-71-verifier-spotcheck.md` §8), five items:

| # | Defect | Disposition in round 72 |
|---|---|---|
| 1 | C2 selftest tally false in three records (report `pass=8`; `SKILL.md:310` `pass=19`; lesson "19 arms"; true `pass=18 fail=0`) | **OPEN.** No round-72 seat prompt assigns it. At HEAD `a3cc39f0`, `SKILL.md:310` still reads `BOUNDARY_SELFTEST pass=19 fail=0`; the fleet report is another repository and cannot be edited. SCR03 already rewrites that same row for defect 2 — correcting the self-test cell costs one cell. Otherwise route to r73. |
| 2 | C2 registry row omits exit `2` (census waiver boundary) | **CLOSED by r72 SCR03** (prompt: "amend the `Census waiver boundary` row's exit map to include `2 could-not-evaluate` (round-71 routed defect 2)"). |
| 3 | `LOG.md` depth anchor stale (`0b61e118…` vs landed `7ff94d67…`) | **CLOSED by r72 SCR03** (prompt: appended correction naming defect 3, `7ff94d67…`, 1724 lines, 48 sections; append, never in-place). |
| 4 | C1 receipt described as "at the report tip" while its header names `4b284653` | **CLASS CLOSED by C2; instance remains historical.** C2's predicate makes the hand-written invariance argument a command: r71's post-receipt commits touch `.ufo/waves/**` and `corpus/lessons/**`, both default record paths, so the r71 case grades green under C2 while the wording defect stays in the fleet report (unwritable from this lane). Stating that the class, not the sentence, is repaired is the honest disposition. |
| 5 | Coverage map has no row for `knowledge/pre-report-gate.md` | **CLOSED by r72 SCR02(b)** (prompt names "the round-71 spot-check section 8 item 5 defect"). Verified open at HEAD: `git show HEAD:corpus/README.md \| grep -c pre-report-gate` → `0`. |

Round-71 lesson (`corpus/lessons/round-71.md`) routed survivors:

| Survivor | Disposition |
|---|---|
| C1 S1 — a wrong `--round` label is a vacuous green | **CLOSED in kind by C1** (case `label`, anchor `plans/round-<N>-claims.md` at `<rev>`; the freeze amendment already moved the anchor off the fleet prompt). |
| C1 S2 — round work outside the wave dir is invisible | **CLOSED in kind by C1** (case `stray`, whole-tree status minus the declared record allow-list; the round-71 "Ceiling" names the same limit for `corpus/knowledge/` and `tools/` edits). |
| C1 S3 — a git-ignored file inside the wave dir is invisible | **CLOSED in kind by C1** (case `ignored`; `--allow-ignored` explicitly not offered). |
| C2 `m7` — `waiver_keeps_not_evaluated` forced true survives (no isolating fixture) | **OPEN.** It is a selftest-arm coverage finding on `census-waiver-boundary.py`; no round-72 seat holds it. |
| C3 `m6` — correction-date guard has no fixture | **OPEN.** C3 is not this round's claim. |
| C3 attack `iv` — a duplicated tag paragraph reads as a false red | **OPEN.** No round-72 seat holds it. |
| C1 "Ceiling" — a child arm that exits 0 on an unevaluable state still reads green | **NOT CLOSED by C1's predicate** (the new arm only fails on non-zero exit); it remains a limit of the *other five* arms. Name it in the lesson. |

## 4. Who owns a `receipt-tip`-shaped gate

**tameshi owns the receipt→revision half; no sibling owns the tip half as a verdict.**

- `tameshi/tools/receipt-revision-gate.py` (`SKILL.md:1547`) is the registered gate for "does this receipt name the revision it certifies", with ancestry for control sets and byte-identity for `--paths`.
- `kotodama/tools/check-receipt-seq.py` computes the tip question (`moved_past=True`) and deliberately refuses to let it change a verdict (unregistered in-file contract).
- `kaidoku/tools/round-45/frozen-path-preflight.py` owns the *method* for a delta sweep over frozen paths (instrument inputs are not its object).
- `souji/census/round-57/c2-counter.py` (`SKILL.md:765`) owns receipt revision *durability* and instrument-sha binding.

Proposed replacement for the existing `Receipt-tip binding` bullet in
`corpus/knowledge/cross-lane-scope.md` § "Overlap rules — round 71" (proposal for the L1; this seat
wrote no lane file):

> **Receipt-tip binding** — tameshi (`tools/receipt-revision-gate.py`, `SKILL.md:1547`) owns the
> receipt→revision binding (one `rev=`, equal to `--certified`, or byte-identical over `--paths`;
> `control` tokens ancestor-or-equal); souji (`census/round-57/c2-counter.py`, `SKILL.md:765`) owns
> revision *durability* (full-40, not `refs/jj` keep-only) plus `instrument_sha256=`; kotodama
> (`tools/check-receipt-seq.py`) computes whether a branch moved past the lands revision and keeps
> it a flag; kaidoku (`tools/round-45/frozen-path-preflight.py`, `SKILL.md:1761`) owns the delta-sweep
> method (and its merge blindness). kama's `tools/round72-receipt-tip-binding.py` is the first gate
> that makes the tip question a verdict, by grading a *path allow-list* over `rev..tip`: record paths
> pass, `tools/**`/`SKILL.md`/`PROVINCE.md`/`corpus/SOURCES.md`/`corpus/knowledge/**`/`registry/**`/
> `plans/**` are `shifted`. Rule: a sibling's binding result is never kama's evidence, and kama's
> `shifted` is not comparable to souji's `KEEP-ONLY` or tameshi's `RECEIPT_REV_MISMATCH`.

## 5. Second-order findings on this round's own predicates (verified)

### 5.1 C2's delta arm inherits a merge blind spot

`git log -1 --name-only <merge>` prints only the subject; the merge's own resolution edit is
invisible. Measured on the lane's two historical merges:

```
$ git rev-list --merges master | while read c; do git log -1 --format='%h %s' $c; done
2f7303c2 Integrate remote documentation; preserve local round log
5396a876 Merge pull request #2 from VeigaPunk/devin/wiki-link
$ git log -1 --format='%h %s' --name-only 2f7303c2 | wc -l      -> 1
$ git diff-tree -m --name-only --no-commit-id 2f7303c2 | wc -l  -> 8
$ git log -1 --format='%h %s' --name-only 5396a876 | wc -l      -> 1
$ git diff-tree -m --name-only --no-commit-id 5396a876 | wc -l  -> 2
```

Both merges are old and outside any short `rev..tip` delta today, so the risk is latent, not live.
The frozen sentence says "every commit in `<rev>..<tip>` touches only declared record paths"; an
implementation that uses `git log --name-only` satisfies the sentence on paper and misses a merge
resolution edit. kaidoku routed this exact blindness as `R45-CL6`. Fix is one flag
(`--diff-merges=first-parent` with `--name-status`), and the limit must be named either way.

### 5.2 "git-ignored" has three spellings and they disagree on a tracked path

Fixture (throwaway repo under `$S`, removed): `a.log` committed **before** `.gitignore` gained
`*.log`, so it is tracked and matches the pattern; `b.log` untracked and matching.

```
$ git status --porcelain -uall --ignored=matching -- .ufo/waves/round-72
!! .ufo/waves/round-72/b.log                      # a.log is NOT listed
$ git status --porcelain -uall -- .ufo/waves/round-72
                                                  # nothing
$ git check-ignore -v -- …/a.log …/b.log
.gitignore:1:*.log  .ufo/waves/round-72/b.log     # a.log is NOT reported (index-aware)
$ git check-ignore --no-index -v -- …/a.log …/b.log
.gitignore:1:*.log  .ufo/waves/round-72/a.log     # a.log IS reported
.gitignore:1:*.log  .ufo/waves/round-72/b.log
```

So a `check-ignore --no-index` implementation of C1 case C reds a *committed* path whose name
merely matches an ignore glob; the status spelling does not. The frozen predicate says "no path
under `.ufo/waves/round-<N>/` is git-ignored", and both readings are defensible — the builder must
declare which tool answers it, because the two produce different `findings=<f>` on the same tree.
Also: `check-ignore` resolves patterns for paths that do not exist (`…/zzz.log` → printed, exit 0),
so it must be fed existing paths, not declared ones.

### 5.3 The ignored-class finding count depends on the `--ignored` mode

Same fixture, one ignored directory plus two ignored files:

```
$ git status --porcelain -uall --ignored=matching -- .ufo/waves/round-72
!! .ufo/waves/round-72/seat/__pycache__/          # directory, one record
!! .ufo/waves/round-72/seat/sub/c.log
!! .ufo/waves/round-72/top.log                    # 3 records
$ git status --porcelain -uall --ignored=traditional -- .ufo/waves/round-72
!! …/seat/__pycache__/a.pyc
!! …/seat/__pycache__/b.pyc
!! …/seat/sub/c.log
!! …/top.log                                      # 4 records
```

Bare `--ignored` behaved as `traditional` here (git 2.56.0). `findings=<f>` is part of C2's and C1's
verdict lines, so the mode is part of the predicate's meaning. The frozen kill rule's fixture (one
ignored file) is mode-invariant; a directory case is not.

### 5.4 The lane's live ignored class is `__pycache__/`

`kama-shokunin/.gitignore` is `.ufo/interactive-sessions/`, `.ufo/state/`, `__pycache__/`. At HEAD,
0 tracked paths under `.ufo/waves/` match `git check-ignore --no-index`, so C1 case C is green on
the committed tree; but `git status --porcelain -uall --ignored=matching -- tools/__pycache__`
prints `!! tools/__pycache__/` (1 record, 0 tracked files), and any seat that imports a lane module
from inside `.ufo/waves/round-72/` creates an ignored directory there that the five-arm gate cannot
see. That is the concrete instance of r71 S3, not a hypothetical.

### 5.5 C2's own before-control receipts cannot satisfy C2

`measured/before/receipt-tip-control-old.out` and `round-scope-control-old.out` are headerless
(`BINDING_CONTROL cited=3 accepted=3 rejected=0`; `SCOPE_CONTROL base_rev=d30a8696 …`). C2 grades
"every receipt path cited by the round's self-record (`SCORECARD.md`'s round-`<N>` section and
`corpus/lessons/round-<N>.md`)". If the L1 cites them from either surface, the gate emits
`RECEIPT_TIP_FINDING unbound` — correctly, by its own rule. The freeze cannot be amended, and the
control receipts cannot be restamped without editing frozen bytes. The only clean sequencing: keep
those two citations in `plans/round-72-claims.md` (not a scanned surface) and cite the *tool's*
after-receipts from SCORECARD/lesson. `base_rev=` is also invisible to a `\brev=` regex and is not a
`# tip=`/`# rev=` header, so a naive 8-hex match would still not bind it.

### 5.6 C2's record-path list does not classify a file this wave writes

Frozen C2 lists:

- record paths: `.ufo/waves/round-<N>/**`, `corpus/lessons/**`, `LOG.md`, `SCORECARD.md`, `corpus/README.md`
- instrument inputs: `tools/**`, `SKILL.md`, `PROVINCE.md`, `corpus/SOURCES.md`, `corpus/knowledge/**`, `registry/**`, `plans/**`

`corpus/QUALITY.md` appears in **neither** list, and SCR02(c) is assigned to append a criterion to
it. Under the frozen sentence ("every commit in `<rev>..<tip>` touches only declared record paths")
that commit is a `shifted` finding naming `corpus/QUALITY.md`. The same holds for the two instrument
inputs this wave writes on purpose (`corpus/SOURCES.md` by SCR01, `corpus/knowledge/**` by SCR02,
`SKILL.md` by SCR03, `tools/**` by EX01-EX03): any receipt measured *before* those commits is
`shifted` at the tip.

This is a **disagreement to record, not an edit**: either the tool's default list includes
`corpus/QUALITY.md` (and the frozen enumeration is incomplete), or the wave must sequence writes so
that every receipt it cites is measured *after* the last instrument-input commit (r71's own
receipts were taken at `4b284653` *after* its instrument commits, and the later lesson edit was a
record path — which is why C2 would grade the r71 case green). The sequencing rule is the actionable
part: **instrument inputs first, scored receipts next, record-path commits last.**

### 5.7 C1's case-A anchor is absent at the round's stated base revision

The plan says "Base revision `d30a8696`", while `controls/freeze.txt` says `base=090a0b25…`.

```
$ git cat-file -e d30a8696:plans/round-72-claims.md ; echo rc=$?
fatal: path 'plans/round-72-claims.md' exists on disk, but not in 'd30a8696'
rc=128
$ git cat-file -e 090a0b25:plans/round-72-claims.md ; echo rc=$?
rc=0
$ git show 090a0b25:plans/round-72-claims.md | head -1
# kama round 72 — frozen claims
```

Both statements are true of different moments (pre-freeze master vs the freeze commit), but C1 case
A grades "the plan exists at `<rev>`". Run with the *base* revision it reports a finding on a
legitimate state; run with the *freeze* commit or a later tip it is green. The counting command in
the freeze (`--tip master`) is safe; the report must name which revision the arm was measured at,
and it must be ≥ `090a0b25`.

### 5.8 C1's "declared record allow-list" is the predicate's only unenumerated term

C1 says "no path outside the declared record allow-list is uncommitted" but never enumerates it,
while C2 enumerates both lists. Two readings, both executable, different populations:

- allow-list = C2's record paths **including** `.ufo/waves/round-<N>/**` → case B grades work outside
  the wave dir (r71 defect ii) and does not duplicate arm 5's round-clean; ignored paths are still
  absolute findings (case C is not exempted by the allow-list).
- allow-list = the five self-record paths of `round67` **excluding** the wave dir → case B becomes a
  second, coarser copy of arm 5 and reds on every uncommitted wave receipt mid-round.

The first reading is the only one that closes r71 defect (ii) without redundancy, and the module
must say so in its `PREDICATE`/docstring for the claim to be gradeable by a reader. This is a
contract gap for the L1 to record, not a disagreement with the freeze's intent.

## 6. Commands run (all read-only or in `$S`)

```
ls -d /home/vgpnk/Projects/*-shokunin ; for d in …; ls "$d/tools" | wc -l
ls */tools/*.py */tools/*.sh | grep -Ei 'receipt|tip|rev(ision)?-|porcelain|clean|ignor|scope|pre-report|…'
grep -n -Ei 'receipt[- ]?(revision|tip|binding)…|porcelain|gitignore|pre-report|round-scope|worktree[- ]landing' */SKILL.md
sed -n '1,45p' <each sibling tool>            # 14 headers, listed in §1
grep -rn "check-ignore|--ignored" */tools/ */SKILL.md
grep -rln "rev-list|diff --name-only|diff-tree" */tools/
grep -rn "record.path|record_path|allow-list|allowlist" */tools/
git -C kama-shokunin rev-parse master ; git log --oneline -8 ; git rev-list --merges --count master
git -C kama-shokunin log -1 --format='%h %s' --name-only <merge> | wc -l
git -C kama-shokunin diff-tree -m --name-only --no-commit-id <merge> | wc -l
git -C kama-shokunin diff --name-only d30a8696..HEAD
git -C kama-shokunin cat-file -e d30a8696:plans/round-72-claims.md   # rc=128
git -C kama-shokunin cat-file -e 090a0b25:plans/round-72-claims.md   # rc=0
git -C kama-shokunin ls-tree -r --name-only HEAD | grep '^\.ufo/waves/' | git check-ignore --no-index --stdin | wc -l   # 0
git -C kama-shokunin status --porcelain -uall --ignored=matching -- .ufo/waves/round-72     # 13 ?? records, 0 !!
git -C kama-shokunin status --porcelain -uall --ignored=matching -- tools/__pycache__       # !! tools/__pycache__/
git -C kama-shokunin show HEAD:corpus/README.md | grep -c 'pre-report-gate'                  # 0
git -C kama-shokunin show HEAD:SKILL.md | sed -n '310p' | grep -o 'pass=[0-9]* fail=[0-9]*'  # pass=19 fail=0
# fixtures under /fast/scratch/hyaku/kama-r72/CON01Overlap (removed):
git init ; commit a.log before .gitignore ; add *.log ; status/check-ignore matrix (§5.2)
git init ; __pycache__/ + *.log ; status --ignored=matching|traditional matrix (§5.3)
```

Fixture repos asserted `git rev-parse --show-toplevel` == the `mktemp -d` dir; commits used
`-c user.name=fixture -c user.email=fixture@invalid`; no lane repository was mutated.

## 7. Limits of this scan

- Sibling tools were read as **text**, not executed. No sibling verdict is claimed; registration and
  exit maps come from their `SKILL.md` rows and docstrings.
- kama's `tools/` was read from the worktree while EX01–EX03 are writing it; the record surfaces
  (`SKILL.md`, `corpus/README.md`) were read from committed bytes at `a3cc39f0`.
- The five round-71 §8 items are dispositioned against the *seat prompts* in
  `.ufo/waves/round-72/w1-spec.json`; a closure asserted there is not a closure observed. Only §3's
  HEAD checks (`SKILL.md:310`, `corpus/README.md`) are observed facts.
