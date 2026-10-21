# RevFailureMap — failure map of the kama closure check's error handling

**Round 24 · lane `RevFailureMap` · reviewer · leaf member (no dispatch)**
Base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` · HEAD at review time `d1b9d95`
(round-24 preregistration commit).

**Target reviewed:** `tools/report-landing-audit.py` (967 lines). Verified
unchanged between the base and HEAD: `git diff 0df800e d1b9d95 -- tools/ tests/`
is empty, so the reviewed text is the base candidate.

**Scope of this lane:** the *error disposition* of the candidate closure check —
git timeouts, undecodable git output, git non-zero returns, and the
`missing/unknown` answer of `cat-file --batch-check` — i.e. which paths end in
`EvalError` (exit 2, could-not-evaluate), which end in a verdict (exit 0/1),
and which can end in a traceback. No implementation, no production edit, no
full-suite run, no offensive fixture. All fixtures are local, synthetic and
offline (`file://` to a directory that is deleted before probing, or no remote
at all).

---

## 1. Axes

| # | axis | question this lane answers |
|---|---|---|
| A1 | **error→exit discipline** | does every failure mode of the closure check land in `EvalError` → exit 2, never in an exit-1 verdict and never in an unhandled traceback? |
| A2 | **evidence availability** | does the tool distinguish *proved absent* (a verdict) from *not available locally* (unknown → exit 2)? |
| A3 | **operability** | do refusals scale with *metadata* (cheap, wrong) instead of with *availability* (expensive, right)? |

A2 is the r24 C1 calibration axis (7→7); A1 and A3 are the guard rails that
must not move while A2 is repaired.

---

## 2. The failure map

Current disposition of every error channel in the candidate, with the source
line that decides it. "required" is the r24 disposition per
`.ufo/waves/round-24/preregistration.json` (`expected_after`).

| # | channel | observable at the source | decides | current disposition | required |
|---|---|---|---|---|---|
| C1 | git call exceeds the deadline | `subprocess.TimeoutExpired` | `:121-125` | `EvalError` → **exit 2** | exit 2 ✔ |
| C2 | git cannot be executed | `OSError` | `:126-127` | `EvalError` → **exit 2** | exit 2 ✔ |
| C3 | git returns non-zero (any reason: bad object, unreadable tree, old git without `--no-lazy-fetch`) | `proc.returncode != 0` | `:128-130` | `EvalError` → **exit 2** | exit 2 ✔ |
| C4 | git stdout is not UTF-8 | `UnicodeDecodeError` on `decode("utf-8","strict")` | `:131-135` | `EvalError` → **exit 2** | exit 2 ✔ |
| C5 | git stderr is not UTF-8 | `stderr.decode(errors="replace")` | `:129-130` | tolerated, never fatal | exit 2 not required ✔ |
| C6 | report file is not a regular file / unreadable / not UTF-8 | `os.stat` / `read_text` | `:221-227` | `EvalError` → **exit 2** | exit 2 ✔ |
| C7 | errata file unreadable / not UTF-8 | `read_text` | `:377-382` | `EvalError` → **exit 2** | exit 2 ✔ |
| C8 | malformed errata row | `parse_errata` | `:359-372` | `EvalError` → **exit 2** | exit 2 ✔ |
| C9 | `git log` record layout unexpected | field count / sha / author time | `:197-210` | `EvalError` → **exit 2** | exit 2 ✔ |
| C10 | `cat-file --batch-check` output shorter than the query | line count | `:156-157` | `EvalError` → **exit 2** | exit 2 ✔ |
| C11 | citation resolves to a *ref*, not an object prefix | `parts[0]` does not start with the token | `:170-172` | `EvalError` → **exit 2** | exit 2 ✔ |
| C12 | repository is shallow / grafted / non-sha1 / not top-level | `rev-parse`, grafts file | `:443-453` | `EvalError` → **exit 2** | exit 2 ✔ (history-truncating) |
| C13 | **repository merely carries promisor metadata** (`.promisor` pack, `remote.*.promisor`, `extensions.partialclone`) — every object present locally | config / pack listing | `:454-457`, `:462-465` | `EvalError` → **exit 2** | **must equal the plain twin's verdict** ✘ |
| C14 | **required object not available locally in a promisor-backed repo** | `cat-file --batch-check` → `<oid> missing`, **rc = 0** | `:159-160` → sinks `:326-327`, `:338-342`, `:405-407` | **exit 1 verdict** (`unresolved-full-hash` / `landed-unresolved` / `errata-invalid`) | **exit 2, unknown** ✘ |
| C15 | required *tree* not available locally | `git log --diff-filter=A -- <path>` → rc 128 `fatal: unable to read tree` | `:128-130` via `:215-218` | `EvalError` → **exit 2** | exit 2 ✔ |
| C16 | required *commit* not available locally | `git log` → rc ≠ 0 | `:128-130` via `:192` | `EvalError` → **exit 2** | exit 2 ✔ |
| C17 | required *report blob* not available locally | `git show HEAD:<rel>` → rc ≠ 0 | `:310-313` | `EvalError` → **exit 2** | exit 2 ✔ |
| C18 | `SOURCES.md` blob not available locally | `git cat-file blob` → rc ≠ 0 | `:268` | `EvalError` → **exit 2** | exit 2 ✔ |
| C19 | citation resolved in the *other* audited repository | `lookup` aggregation | `:152-173` | found → no defect ✔ (unreachable today because C13 refuses first) | must stay found ✔ |
| C20 | genuine omitted pre-cutoff lane commit | `landed-omitted` sink | `:344-350` | exit 1 (plain repo) / exit 2 (promisor-marked, via C13) | exit 1 `landed-omitted` in **both** ✘ |
| C21 | filesystem read that is not a git call (grafts bytes, report bytes, errata bytes, pack dir listing) | blocking `read_*`/`iterdir` | `:225`, `:379`, `:456`, `:479` | unbounded wait; `OSError` escapes as a generic exception | bounded; `EvalError` |
| C22 | non-`EvalError` escape (`ValueError` from `int()`, `OSError` from `read_bytes`/`iterdir`) | not caught by any local handler | `:211`, `:218`, `:456`, `:479` | caught by `main` → exit 2, but stderr says `output:` (OSError) or `internal:` (ValueError) | `EvalError` |

The four rows marked ✘ are the r24 repair surface; C1–C12 and C15–C19 are the
behaviour that must survive it.

---

## 3. Findings

### S1 — HIGH — promisor **metadata alone** turns a complete repository into exit 2, before any object is consulted

`check_history_repo` refuses on three metadata signals:
`:454-457` (a `*.promisor` marker next to a `*.pack`), `:462-464`
(`extensions.partialclone`), `:463-464` (`remote.<name>.promisor` truthy).
None of them says anything about *availability*; they only say the repository
*could* fetch. The refusal happens in `run()` at `:514-515`, before
`resolve_branch`, before `load_source_urls` and before any `lookup`, so it
decides the whole audit.

Measured (twin probe, `out/RevFailureMap/twin-output.txt`): four arms with
**byte-identical content and every object present locally**; only the metadata
differs.

```
arm A-plain             exit=0  defects=[]
arm B-config-marker     exit=2  could-not-evaluate: …: partial clone (remote.origin.promisor)
arm C-pack-marker       exit=2  could-not-evaluate: …: partial clone (promisor pack)
arm D-extensions-marker exit=2  could-not-evaluate: …: partial clone (extensions.partialclone)
## 1/4 arms equal the plain arm
```

This is the r23 rejection: the same substantive verdict (clean) is replaced by
could-not-evaluate, i.e. an operability and calibration harm, not a safety win.
`expected_after` #1 requires arms B/C/D to equal arm A.

### S2 — HIGH — a "missing" answer in a promisor-backed repository becomes an exit-1 **verdict**, not exit 2

`cat-file --batch-check` answers `<oid> missing` with **rc = 0**, so `git()`
does not raise and the answer is indistinguishable from "proved absent". The
`missing` state then flows into three verdict sinks:

* `:326-327` → `unresolved-full-hash` (exit 1),
* `:338-342` → `landed-unresolved` / `landed-ambiguous` (exit 1),
* `:405-407` → `errata-invalid` (exit 1).

Measured in a genuine blobless partial clone (local `file://` origin, deleted
before probing, so a fetch could not have succeeded even if attempted), with
the tool's own isolation flags
(`out/RevFailureMap/partial-clone-output.txt`):

```
cat-file --batch-check(old blob) rc=0 stdout='… missing' stderr=''
cat-file --batch-check(commit)  rc=0 stdout='… commit 164'
packs before == packs after ;  fetch attempted (pack count grew): False
```

So `--no-lazy-fetch` is honoured (no fetch), the object is genuinely absent
locally, and the tool sees only `missing` — indistinguishable from a token that
never existed. With the S1 refusal removed (measurement copy, diff in
`out/RevFailureMap/measurement-copy.diff`) the disposition is
`out/RevFailureMap/unknown-citation-norefusal.txt`:

```
arm P-plain-absent          exit=1  [('unresolved-full-hash', '0123…4567')]   # proved absent: correct
arm Q-promisor-absent       exit=1  [('unresolved-full-hash', '0123…4567')]   # unknown: WRONG, must be exit 2
arm R-promisor-found-elsewhere exit=0  []                                       # resolved in the other repo: correct
```

Removing the blanket refusal alone therefore converts an over-refusal into a
**false verdict**. Both halves of the repair are required:
(i) metadata must not decide, and (ii) "missing" in a promisor-backed
repository must become *unknown* → exit 2.

### S3 — HIGH — the "resolved locally by another audited repository" rule is unreachable today

`expected_after` #4: *"A missing citation in any promisor-backed repository is
unknown, not proved absent: exit2 unless resolved locally by another audited
repository."* The aggregation in `lookup` (`:152-173`) already implements the
"unless" half — a token found in either repo is `found`. But the "exit2"
half is unreachable: the repository is refused at `:514-515` before the lookup
runs. Measured on the base tool (`out/RevFailureMap/unknown-citation-base.txt`):

```
arm P-plain-absent            exit=1  [('unresolved-full-hash', …)]  # correct
arm Q-promisor-absent         exit=2  could-not-evaluate: … partial clone (remote.origin.promisor)
arm R-promisor-found-elsewhere exit=2  could-not-evaluate: … partial clone (remote.origin.promisor)   # WRONG: R is resolvable
```

Arm R is a repository pair whose every object is present and whose citation is
resolvable in the other audited repository; it must produce the plain twin's
verdict.

### S4 — MEDIUM — the refusal set must be split, not deleted

Four of the six refusals in `check_history_repo` are *history-truncating* and
are legitimate: non-sha1 object format (`:443-445`), not a repository top level
(`:446-447`), shallow (`:448-449`), grafts (`:450-453`). Those make visible
history differ from object history, and exit 2 is right for them. The two
promisor signals are not in that class: a promisor-marked repository with all
objects present has a *complete* visible history. The repair should turn the
promisor signals into a **per-repository flag** ("this repository may hold
objects that are not local"), not delete the checks and not keep them as
refusals. Note that the `.promisor` *pack marker* is not even a completeness
signal: a plain clone of a filtered remote writes one while holding every
object (measured: the first probe run produced
`pack-….promisor` in a clone that had all objects).

### S5 — MEDIUM — `lookup` has no "unknown" state and no per-repository attribution

The status vocabulary is `{found, ambiguous, missing}` (`:139-174`). Two
consequences for the repair:

* there is no state for "not available locally but possibly available", so the
  three sinks (`:326-327`, `:338-342`, `:405-407`) cannot express
  "unknown ≠ absent";
* `lookup` folds the repositories together (`:152-173`) and discards *which*
  repository answered. The repair needs to know that a token was missing in a
  promisor-backed repository (→ unknown) even when another repository resolved
  it (→ found, per `expected_after` #4). The aggregation must therefore record
  per-repository answers, not just the folded status.

A second-order point: `lookup` is called three times with different tokens
(`:325` full hashes, `:336` landed abbreviations with the `^{commit}` peel,
`:402` errata corrections with the peel). A per-repository "missing in a
promisor-backed repo" rule has to be applied at **all three**, otherwise the
repair fixes `unresolved-full-hash` and leaves `landed-unresolved` and
`errata-invalid` issuing exit-1 verdicts on unproven absence.

### S6 — LOW/MEDIUM — filesystem reads are outside the 20 s deadline

`:225` (`read_report`), `:379` (`load_errata`), `:456` (`objects/pack`
`iterdir()`) and `:479` (`grafts_effective` `read_bytes()`) block without any
deadline. The comment at `:122-123` states the intent ("a hang is never a
verdict") but the guarantee only covers git subprocesses. A hung or
network-mounted path blocks the audit indefinitely. `grafts_effective` is
partly protected: a non-regular `info/grafts` is refused unread
(`:476-477`), but a *regular* file on a hung filesystem is read at `:479`.

### S7 — LOW — some failures are not `EvalError`

`OSError` from `:479` (`read_bytes`) and `:456` (`iterdir`), and `ValueError`
from `int(atime)` (`:211`) and `int(out[-1])` (`:218`), are not caught by any
local handler. They reach `main` and therefore exit 2 — **no verdict leaks** —
but the message is a generic one, measured through `main()`
(`out/RevFailureMap/probe-output.txt`, section D):

```
D1 unreadable info/grafts -> exit=2 stderr="could-not-evaluate: output: [Errno 13] Permission denied: '…/.git/info/grafts'"
D2 non-numeric %at        -> exit=2 stderr='could-not-evaluate: internal: ValueError: ValueError("invalid literal for int() with base 10: \'not-a-number\'")'
```

D1 is mislabelled: an *input-side* `PermissionError` is reported as an
**output** failure (`main`'s `except OSError` at `:951-956`, whose handler was
written for a failed `print`). D2 falls into the `internal:` catch-all
(`:957-963`). The exit code is right in both cases; the r24 wording "every
error stays `EvalError`" is not literally met at these four sites, and an
operator reading "output:" would look in the wrong place.

### S8 — LOW — the promisor detection truncates multi-line config values

`:461` splits a `git config --null --list` entry at the **first** newline
(`entry.partition("\n")`). A value containing a newline is cut after its first
line, so `git_bool` (`:482-487`) sees only that fragment; e.g. a value
`"no\nyes"` reads as `False` and the repository is not recognised as
promisor-backed. The repair's detection should let git normalise the boolean:
`git config --type=bool --get-regexp '^remote\..+\.promisor$'` (query
`extensions.partialclone` separately — it is a *string*, not a bool), and keep
`git_bool` only as a fallback.

### S9 — INFORMATIONAL (positive) — the timeout / decode / return-code contract is correct and must not regress

`git()` (`:111-136`) maps every subprocess failure to `EvalError`:
`TimeoutExpired` → `:121-125`, `OSError` → `:126-127`, non-zero return →
`:128-130`, undecodable stdout → `:131-135` (strict by default;
`surrogateescape` only at the three call sites `:193` lane log records,
`:430` report path listing, `:459` config listing). `main` (`:941-963`) catches
`EvalError` → 2, `OSError` → 2, and **any other `Exception` → 2** with an
`internal:` prefix, so an unanticipated failure can never surface as an
exit-1 verdict or a traceback. `argparse` usage errors exit 2 as well; a
keyboard interrupt exits 130, which is not a verdict.

Measured (branch probes, `out/RevFailureMap/probe-output.txt`, 11/11 as
expected): timeout → `EvalError`; `OSError` → `EvalError`; rc 128 → `EvalError`;
undecodable stdout → `EvalError`; undecodable stderr with rc 0 → tolerated;
CRLF-only output normalised; plus the two non-`EvalError` escapes of S7,
which still exit 2.

### S10 — INFORMATIONAL — `cat-file` answers the tool does not name

`:165-166` treats `excluded` and `dangling` as "not found". Per
`git-cat-file(1)` (local man page, read 2026-10-21) the documented answers for
`--batch-check` are `missing`, `excluded`, `ambiguous`, `submodule` and the
normal `<oid> <type> <size>`; `dangling` belongs to `--follow-symlinks`
reporting, and `excluded` requires `--filter=` (never passed by the tool), so
both branches are effectively dead. `submodule` is **not** handled: a gitlink
oid answers `missing` in practice (measured: `git cat-file --batch-check` on a
gitlink oid → `missing`, rc 0), but if git ever emitted `submodule`, the
3-field parse at `:167-169` would raise `EvalError` — fail-closed and
acceptable. The vocabulary should be enumerated once, in the repair, when
"unknown" is added.

### S11 — INFORMATIONAL — `GIT_TIMEOUT` is per call, not per audit

`:108`/`:120` bound each git call at 20 s; a full historical audit issues
many calls and there is no overall deadline. Keep as is (the prereg says
preserve existing deadlines), but the repair must not add *new* unbounded work
(a per-repo `git config` sweep is bounded; a per-token `git cat-file` call
would multiply the deadline exposure).

---

## 4. Acceptance points

Each is checkable by a command in this lane's `out/` directory. AP1–AP3 are
the repair's definition of done; AP4–AP9 are "do not regress" guards.

| id | acceptance point | how to check | state today |
|---|---|---|---|
| **AP1** | promisor **metadata alone** must not change the exit code or the defect set: arms B (`remote.origin.promisor=true`), C (`.promisor` pack marker), D (`extensions.partialclone`) must equal arm A (plain) in `(exit, defects)` | `python3 .ufo/waves/round-24/build/out/RevFailureMap/probe-twin.py tools/report-landing-audit.py` → must print `4/4 arms equal the plain arm` | **1/4** ✘ |
| **AP2** | a citation that is absent **everywhere** must be `exit 1 unresolved-full-hash` in a plain repository and **`exit 2` (could-not-evaluate, no defects)** in a promisor-backed repository; a citation resolvable in the *other* audited repository must stay a normal verdict | `python3 …/probe-unknown-citation.py <candidate> candidate` → arms P/Q/R | P ✔, Q ✘ (exit 1), R ✘ on base (exit 2) |
| **AP3** | the repair must add an "unknown/not-available" state to `lookup` and handle it at **all three** sinks — `tools/report-landing-audit.py:326-327`, `:338-342`, `:405-407` — so that no not-found answer becomes a defect without first consulting the per-repository availability flag | `grep -n 'unknown\|not-available\|unavailable' tools/report-landing-audit.py` → a state plus three handlers | absent ✘ |
| **AP4** | no lazy fetch, no transport, no repo-configured program, no replace-ref substitution: keep `GIT_ISOLATION` (`:93-95`) and the single subprocess call site (`:117`) | `grep -n 'subprocess' tools/report-landing-audit.py` → exactly one call site | ✔ (must stay) |
| **AP5** | every git failure mode stays `EvalError` → exit 2: timeout, `OSError`, rc ≠ 0, undecodable stdout; undecodable stderr tolerated | `python3 …/probe-error-branches.py` → `11/11` (nine branch probes + the two non-`EvalError` escapes, which must also stay exit 2) | **11/11** ✔ |
| **AP6** | the history-truncating refusals survive: non-sha1 (`:443-445`), not-top-level (`:446-447`), shallow (`:448-449`), grafts (`:450-453`) all still exit 2 | one fixture per refusal | ✔ (must stay) |
| **AP7** | an unavailable **tree** still exits 2 after the promisor refusal is removed: the path-limited log fails with rc 128 `fatal: unable to read tree` (measured) → `:128-130` → `EvalError`; the repair must not convert a non-zero return into "no commit found" (`:318` also raises, so both are exit 2 — but the repair must not add a `--ignore-missing`-style flag) | `out/RevFailureMap/partial-clone-output.txt`, treeless arm | ✔ (must stay) |
| **AP8** | the decode contract is unchanged: strict by default, `surrogateescape` only at `:193`, `:430`, `:459`; `GIT_TIMEOUT` still 20 s and passed to every git call | `grep -n 'errors=' tools/report-landing-audit.py` → three `surrogateescape` sites, no others | ✔ (must stay) |
| **AP9** | no non-`EvalError` escape remains at `:211`, `:218`, `:456`, `:479` (S7) — wrap them so the stderr names the cause instead of `output:` / `internal:` | `python3 …/probe-error-branches.py` → section D: D1 must not say `output:`, D2 must not say `internal:` | ✘ (S7) — both exit 2 today, with a generic message |
| **AP10** | a genuine omitted pre-cutoff lane commit stays **`landed-omitted`, exit 1** in a promisor-marked lane (`expected_after` #2) — a repair that maps "promisor-marked" to a blanket exit 2 fails this | `python3 …/probe-promisor-omission.py <candidate> candidate` → arms O/P/Q | P ✘ on base (exit 2); ✔ on the refusal-removed copy |
| **AP11** | the promisor detection must not depend on a config value's raw spelling (S8): use git-normalised booleans | `grep -n 'git_bool' tools/report-landing-audit.py` → replaced by `--type=bool` query | ✘ (S8) |
| **AP12** | no-harm twin: the wave's own lane and fleet (which carry no promisor metadata) must keep identical exit codes and defect sets before and after the repair | L1's historical-ledger re-run (r23 evidence, unchanged) | out of this lane's scope |

---

## 5. Residual risk and verification gaps

**Residual risk (after a correct repair):**

* R-1 — *Availability is decided per object, but the audit asks about objects
  it never names.* The repair can only classify a token it actually looks up.
  A promisor-backed lane whose history is locally complete but whose **future**
  commits live on the promisor is indistinguishable from a complete lane — the
  audit can only see what it reads. `expected_after` #6 ("metadata-only
  declarations do not establish incompleteness") accepts this, but the scorecard
  wording must not claim the tool can prove a repository is complete.
* R-2 — *The "unknown" verdict is not per-token in the current data model.*
  `run()` produces one document per audit; an unknown citation aborts the whole
  audit (exit 2) rather than naming the offending token. The exit-2 message
  must carry the token and both repository names, otherwise the operator
  cannot act on it.
* R-3 — *`git log` completeness in a promisor-backed lane.* Commits were
  present in both measured partial clones (blobless and treeless: `git log`
  rc 0, both commits listed), so the omission channel survives promisor
  metadata. A repository that is missing a *commit* was not measured here
  (r23 F28 recorded exit 2 for that channel).
* R-4 — *`objects/info/alternates` and gitfile worktrees* are outside this
  lane's scope and remain unmeasured for the "unknown" rule: an object
  borrowed through an alternate is local, but the borrowed repository's
  promisor status is not inspected.

**Verification gaps (not run here — stated as gaps, not as claims):**

* No full-suite, historical-ledger, or mutation run (out of lane scope; L1
  runs once after integration).
* The "missing **commit**" channel (C16) was not measured in this lane; the
  r23 F28 row is the only evidence.
* The `--filter=` / `excluded` / `submodule` answers of `cat-file
  --batch-check` were not exercised (the tool never passes `--filter=`).
* Behaviour on git < 2.45 (no `--no-lazy-fetch` → rc ≠ 0 → exit 2) and on a
  non-UTF-8 `i18n.logOutputEncoding` was not re-measured.
* `.git/objects/info/alternates`, gitfile worktrees, SHA-256 repositories and
  linked worktrees were not measured; they are unchanged by this lane.
* No source was fetched; no network transport was used at any point. The only
  remote in the fixtures was a local `file://` directory that was deleted
  before probing, and `example.invalid`-style URLs were never contacted.

---

## 6. Files written, tooling, and what was *not* touched

Written (this lane's out directory and the advice file only):

* `.ufo/waves/round-24/build/advice/RevFailureMap.md` — this report.
* `.ufo/waves/round-24/build/out/RevFailureMap/failure-map-scan.py` +
  `scan.txt` — read-only AST scan of the candidate (git call sites and their
  decode modes, except handlers, raise sites, filesystem reads).
* `.ufo/waves/round-24/build/out/RevFailureMap/probe-error-branches.py` +
  `probe-output.txt` — the six `git()` error-branch probes plus the two
  non-`EvalError` escapes, observed through `main()` (11/11).
* `.ufo/waves/round-24/build/out/RevFailureMap/probe-twin.py` +
  `twin-output.txt` — plain vs promisor-marked twins (1/4 today).
* `.ufo/waves/round-24/build/out/RevFailureMap/probe-partial-clone.py` +
  `partial-clone-output.txt` — offline blobless/treeless clone: `missing` is
  rc 0, no fetch occurs.
* `.ufo/waves/round-24/build/out/RevFailureMap/probe-unknown-citation.py` +
  `unknown-citation-base.txt`, `unknown-citation-norefusal.txt` — the
  unknown-citation disposition on the base tool and on the refusal-removed
  measurement copy.
* `.ufo/waves/round-24/build/out/RevFailureMap/probe-promisor-omission.py` +
  `omission-base.txt`, `omission-norefusal.txt` — genuine-omission
  disposition.
* `.ufo/waves/round-24/build/out/RevFailureMap/tool-MEASUREMENT-no-promisor-refusal.py`
  + `measurement-copy.diff` — **measurement artefact, not a candidate
  implementation**: the base tool with the two promisor refusals replaced by
  `pass`, used only to show where the "missing" answer lands once the blanket
  refusal is gone. It is not a proposed fix; S2/S5 require a real "unknown"
  state that this artefact does not contain.

Not touched: `tools/`, `tests/`, `corpus/`, `registry/`, the lane's `.jj` and
Git index, sibling lanes, the fleet, operator configs, r23 wave evidence
(unchanged; the prereg's r23 corrections are the scribe lanes' business), and
no host service or configuration. No commit, no push, no index entry.

Scratch (throwaway, all under `/fast/scratch/hyaku/kama-r24/RevFailureMap/`):
the measurement copy of the tool and the temporary fixture trees created by the
probes (`rfm-promisor-*`, `rfm-partial-*`, `rfm-twin-*`, `rfm-unk-*`,
`rfm-omit-*`). The twin probe removes its own tree; the others are inert local
repositories.

**Tooling:** no package was installed, updated or removed in this lane — the
review needed only the preinstalled `git 2.56.0`, `python 3.14.8` and `man`
(offline `git-cat-file(1)`), so no install record is owed.
