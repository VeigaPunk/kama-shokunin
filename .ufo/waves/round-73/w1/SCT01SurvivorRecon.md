# SCT01SurvivorRecon — round 73, w1 (kama): read-only reconnaissance for C1, C2, C3

Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`. All probes read **revision
`bc9e30599b6c6133bb094f0e7abd1a9f512778ec`** (`git -C <lane> rev-parse master`, read at receipt-write
time and repeated at the head of every receipt). The round-72 record was read at the **freeze
revision `6e9619963fef5a3f8899324e9497416a00eab7e6`** named by `plans/round-73-claims.md`.
Seat bounds honoured: no lane file written except this report and the receipts under
`.ufo/waves/round-73/w1/SCT01SurvivorRecon/`; no git/jj mutation anywhere; scratch
`/fast/scratch/hyaku/kama-r73/SCT01SurvivorRecon` deleted before yield.

This seat is reconnaissance only. It builds nothing, fixes nothing, and changes no counter byte.

---

## 1. Survivor rebuild + base counter — the pre-state reproduces exactly

Fixture builder (`build-survivors.py`, sha256 pinned in `controls/freeze.txt`):

```
python3 .ufo/waves/round-73/controls/build-survivors.py \
        --work /fast/scratch/hyaku/kama-r73/SCT01SurvivorRecon/ctrl \
        --meta /fast/scratch/hyaku/kama-r73/SCT01SurvivorRecon/ctrl/fixtures-meta.json
→ FIXTURE c1_clean … / c1_a5 / c1_a6e / c1_a7sub2 / c2_b6 / c3_stale / META …
   BUILD_EXIT=0 ; every fixture toplevel == its own directory (builder asserts it; re-checked with
   `git -C <fixture> rev-parse --show-toplevel`)
```

Base counter (`tools/round72-round-scope.py`, byte-frozen), receipt
`SCT01SurvivorRecon/base-counter-survivors.out`:

| invocation | observed stdout | exit |
|---|---|---|
| `--repo …/c1_clean --round 73 --tip master` | `ROUND_SCOPE round=73 cases=3 findings=0` | 0 |
| `--repo …/c1_a5 --round 73 --tip master` | `ROUND_SCOPE round=73 cases=3 findings=0` | 0 |
| `--repo …/c1_a6e --round 71 --tip master` | `ROUND_SCOPE round=71 cases=3 findings=0` | 0 |
| `--repo …/c1_a7sub2 --round 73 --tip master` | `ROUND_SCOPE round=73 cases=3 findings=0` | 0 |

So `base_green=3` for the three survivors, and `c1_clean` is green with 0 findings, matching
`measured/before/score-survivors-base.out`
(`SURVIVORS c1 base_green=3 v2_killed=0 v2=absent`). **The three survivors are real on this host and
this git version; nothing about the freeze's premise is stale.** [OBSERVED]

---

## 2. The exact mechanism that hides each survivor, and the minimal command that exposes it

Line numbers are `tools/round72-round-scope.py` at the freeze revision. Receipt:
`SCT01SurvivorRecon/exposing-commands.out`.

The single entry point `evaluate` (line 282) resolves the repo at line 285 through `resolve_repo`
(defined at 114), which runs `git rev-parse --show-toplevel`, so `root` is **always the primary
worktree**, and then runs exactly three graders (lines 291–293). `CASE_ORDER` is `("label","stray",
"ignored")` (line 79); there is no fourth case.

### A5 — linked-worktree dirt

*Mechanism.* `_stray_findings` (252–263) runs `git status --porcelain -uall` at **line 253 with no
pathspec and only from `root`**. A linked worktree (`git worktree add`) is a separate working tree
with its own index and HEAD; no `git status` invocation reports another working tree's files. The
string `worktree` occurs **zero times** in the module (`grep -n "worktree\|ignore-submodules\|submodule"
tools/round72-round-scope.py` → NO MATCH). Only the label case ever reads outside the working tree
(`cat-file` at the tip), and the ignored case is pathspec-scoped (§A6), so a dirty linked worktree
has no grader at all.

*Observed.*

```
$ git -C c1_a5 status --porcelain -uall                 # what the base reads
(empty)                                                 exit=0
$ git -C c1_a5 worktree list --porcelain
worktree …/c1_a5      HEAD 5db7823…  branch refs/heads/master
worktree …/c1_a5-wt   HEAD 5db7823…  detached
$ git -C c1_a5-wt status --porcelain -uall
 M LOG.md
?? stray-in-wt.txt
```

*Minimal exposing command.* `git worktree list --porcelain`, then `git -C <each> status --porcelain
-uall` for every entry except the primary. [OBSERVED]

### A6 — a valid older-round label hides a later round's ignored work

*Mechanism.* `_ignored_findings` (267–279) builds the pathspec from the **CLI label**, not from the
directory the work sits in:

```
268:    wave_rel = ".ufo/waves/round-{}".format(round_no)
269:    proc = _git(root, "status", "--porcelain", "-uall", "--ignored", "--", wave_rel)
275:        if not record.strip() or record[:2] != "!!":
```

With `--round 71` the pathspec is `.ufo/waves/round-71`; the planted `hidden.log` sits in
`.ufo/waves/round-72` and is invisible to `stray` as well because `.gitignore:1:*.log` ignores it.
The label case stays green because `plans/round-71-claims.md` exists at the tip in the seed.

*Observed.*

```
$ git -C c1_a6e status --porcelain -uall --ignored -- .ufo/waves/round-71
(empty)                                                 exit=0
$ git -C c1_a6e status --porcelain -uall --ignored -- .ufo/waves
!! .ufo/waves/round-72/hidden.log
$ git -C c1_a6e check-ignore -v .ufo/waves/round-72/hidden.log
.gitignore:1:*.log	.ufo/waves/round-72/hidden.log
$ python3 tools/round72-round-scope.py --repo …/c1_a6e --round 72 --tip master     # relabelled
ROUND_SCOPE_FINDING label plans/round-72-claims.md rev=master status=absent
ROUND_SCOPE_FINDING ignored .ufo/waves/round-72/hidden.log
ROUND_SCOPE round=72 cases=3 findings=2                  exit=1
```

*Minimal exposing command.* Drop the label-derived pathspec (`-- .ufo/waves`) or enumerate
`.ufo/waves/round-<M>` on the filesystem and grade each with `--ignored`. [OBSERVED]

### A7 — `submodule.<name>.ignore=all`

*Mechanism.* Both graders use plain `git status` (lines 253 and 269) and therefore honour
`.gitmodules`. gitmodules(5), `submodule.<name>.ignore`, value `all`: *"The submodule will never be
considered modified"*; git-status(1): `--ignore-submodules` `all` *"is the default"*, and `none`
*"can be used to override any settings of the ignore option in git-config(1) or gitmodules(5)"*.
The effective value is the `.gitmodules` one (`git config --get submodule.sub.ignore` → exit 1,
unset). The module never passes `--ignore-submodules` and never re-enters a submodule with `-C`.

*Observed.*

```
$ git -C c1_a7sub2 status --porcelain -uall
(empty)                                                 exit=0
$ git -C c1_a7sub2 status --porcelain -uall --ignored -- sub
(empty)                                                 exit=0
$ git -C c1_a7sub2 status --porcelain -uall --ignore-submodules=none
 M sub
$ git -C c1_a7sub2/sub status --porcelain -uall
 M child.txt
?? leak.txt
$ cat c1_a7sub2/.gitmodules
[submodule "sub"]
	path = sub
	url = …/c1_a7_subrepo
	ignore = all
$ git -C c1_a7sub2 submodule status
 6f42fe876d5a971c0268ac85ddb0508bdab1e037 sub (heads/master)      # leading space = initialized
```

Note the parent-side probe names only `sub`; the files that leaked are named only by the
per-submodule porcelain. [OBSERVED]

---

## 3. Bound check for the C1 `M >= N` rule (receipt `SCT01SurvivorRecon/ignored-bound.out`)

Live lane worktree, read-only:

* `git status --porcelain -uall --ignored -- .ufo/waves` → **49** `!!` records.
* Rounds carrying ignored records: **M = 25, 34, 45, 46, 47, 49, 50, 57, 59, 64, 70**
  (counts 1, 3, 1, 1, 3, 12, 1, 1, 1, 23, 2).
* **max M = 70**; the `M >= 73` filter prints nothing; **0** ignored records live outside a
  `round-<M>/` directory.
* Narrow query at the counter's own pathspec:
  `git status --porcelain -uall --ignored -- .ufo/waves/round-73` → **0** `!!` records
  (only `??` untracked files, which `ignored` does not grade).
* `git worktree list --porcelain` → **one** entry (the primary).
* Lane submodule population: `git submodule status` empty, no gitlink (`ls-files -s | grep ^160000`),
  no `.gitmodules`, no `submodule.*` config → **A7 is unexercised in the lane**.

**Consequence for the claim.** For `N=73` the `ignored-older-label` population is **empty on the
live lane**, and A5/A7 have **no positive case in the lane at all**. A green live lane therefore
proves nothing about the new cases: all three kills must be evidenced by the fixtures. That is
consistent with the freeze (the kill rule names only fixtures) but it means a "live lane exits 0"
receipt cannot be used as operability evidence for C1's new cases.

Live-state caveat, mid-wave: at probe time the lane had 54 uncommitted records —
4 tracked modifications (`PROVINCE.md`, `SKILL.md`, `corpus/QUALITY.md`, `corpus/README.md`), 45
untracked files inside `.ufo/waves/round-73/`, 5 untracked outside it. The `stray` case will be red
until those are committed or allow-listed; that is expected mid-wave, not a defect
(`SCT01SurvivorRecon/live-state.out`).

---

## 4. Two design hazards the C1 executor must handle (or the counter is exit-2 red on a clean repo)

### 4.1 A registered-but-prunable linked worktree makes `git -C` fail with 128

`git worktree list --porcelain` keeps listing a worktree whose directory was deleted and annotates
the block with `prunable gitdir file points to non-existent location`. Running the case's
`git -C <path> status --porcelain -uall` then exits **128**
(`fatal: cannot change to '…': No such file or directory`), which the frozen exit map classifies as
"a git command failure" → **exit 2**, even though the repository is clean. The case must either skip
blocks carrying a `prunable` line or treat the missing directory as a finding, never as
could-not-evaluate. Receipt: `SCT01SurvivorRecon/worktree-hazard.out`.

### 4.2 `detached` is not a defect, and the primary block must be skipped

The live lane's own main worktree is a **detached HEAD**
(`git symbolic-ref -q HEAD` → exit 1; `git status -sb` → `## HEAD (no branch)`), and
`worktree list --porcelain` prints `detached` for it. A case that grades `detached` as dirt
false-positives on the lane itself; a case that grades the primary block double-reports what `stray`
already reports.

### 4.3 `ignored-older-label` must enumerate the filesystem, not the git tree

The frozen sentence says "every `.ufo/waves/round-<M>/` **directory present in the worktree**". In
`c1_a6e` the planted `round-72` directory is **not tracked**:

```
$ ls -d c1_a6e/.ufo/waves/round-*        → round-71, round-72
$ git -C c1_a6e ls-tree --name-only HEAD .ufo/waves/  → .ufo/waves/round-71
$ git -C c1_a6e cat-file -e HEAD:.ufo/waves/round-72
fatal: path '.ufo/waves/round-72' exists on disk, but not in 'HEAD'
```

An `ls-tree`-based enumeration misses the fixture and the survivor survives again. On the lane
disk and tree agree (63 = 63), so only the fixture catches this. Receipt:
`SCT01SurvivorRecon/a6-enumeration.out`.

### 4.4 "initialized" must be tested before grading a submodule

`git submodule status` prefixes an uninitialized submodule with `-`; `git -C <sub>` on such a path
fails, which would again turn a clean repo into exit 2. Grade only entries with a leading space/`+`.

---

## 5. Citation census for C2 (receipt `SCT01SurvivorRecon/citation-census.out`)

Population: `SCORECARD.md`'s `## Round 72` section (69 lines from offset 3818, which includes the
`### Planned (round 73)` subsection because the base tool stops only at the next `^## `) plus the
whole of `corpus/lessons/round-72.md`, both at the freeze revision. Tokens were produced and
classified by the base tool's own functions (`TOKEN_RE`, `_citations`, `_resolve_citation`,
`_in_scope`, `_expand_one`, `is_receipt`) imported from
`tools/round72-receipt-tip-binding.py`, not re-implemented.

**223 backticked tokens.**

| class | as a round-72 record | as a round-73 record (at the freeze rev) |
|---|---|---|
| `prose` (rejected by the tool's pre-filters: whitespace, `...`, or a skip character such as `<` `>` `$` or a quote) | 61 | 61 |
| `repo-root` (first segment exists at the tip: `LOG.md`, `SCORECARD.md`, `corpus/…`, `tools/…`, `plans/…`) | 29 | 29 |
| `section-relative-absent` (not receipt-like, not present under the round base — identifiers, flags, short shas, `S175`) | 107 | 109 |
| `qualified-other-round` (`.ufo/` prefix outside the graded base) | 1 | 13 |
| **`receipt` (in scope)** | **25** | **11** |

* **How many are receipts: 25 tokens**, resolving to **147 distinct receipt paths**
  (`RECEIPT_TIP_BINDING round=72 cited=147 bound=6 unbound=105 shifted=24 stale=12`, exit 1 — the
  base tool's own verdict at the freeze revision). 135 of those paths are present at the tip; 12 are
  absent (7 `kill-*.out` — ignored, label-wronground, non-receipt, shifted, stale, stray, unbound —
  plus `fetch.out`, `freeze.txt`, `quote.txt`, `w1-results.json`, `w1-dispatch.json`).
* **How many would be in scope for a round-73 record: 11 tokens.** They are section-relative, so the
  base tool rebinds them to `.ufo/waves/round-73/…`: `kill-{label-wronground,stray,ignored}.out`
  (3 paths), `kill-{unbound,stale,shifted,non-receipt}.out` (4), `w1/CRT01ReceiptAttack/live-r71-min.out`,
  `fetch.out` (×3 occurrences, 1 path), `quote.txt`, `w1/w1-results.json`, `freeze.txt`,
  `w1-results.json`, `w1-dispatch.json`. Twelve other receipt tokens are fully qualified
  `.ufo/waves/round-72/…` and are therefore **skipped** by a round-73 audit.

### 5.1 The `/` token: one punctuation accident supplies 92% of the citation population

`corpus/lessons/round-72.md:90` reads `` `allow`/`subdir-repo`/`json` ``. `TOKEN_RE` is
`` `([^`\n]+)` ``, so the `/` **between two closed backtick spans is itself a token**. A bare `/`
resolves via `rel = "/"` → `full = ".ufo/waves/round-72//"` → `root = ".ufo/waves/round-72"` with
`dir_hint = True` → `_expand_one` returns **every receipt file in the wave tree: 135 paths**. Every
one of those 135 is graded, which is why `cited=147` and `findings=141` rather than a dozen.
At the r73 record tip the round-73 tree will exist, so the same accident there would sweep every
round-73 receipt (including each new `kill-*.out` the seats write).

### 5.2 Tip-claim lines: 7 exist, and none of them cites a receipt → `claims=0`

Lines matching `at the tip` / `at the report tip` / `report tip`:
`SCORECARD.md:3827, 3836, 3880, 3886` and `corpus/lessons/round-72.md:17, 136, 158`. Every one is
prose *about* the wording class (or `## Gate`/`## Mistakes` commentary); none carries an in-scope
receipt token. Under the frozen C2 sentence — "every self-record line that cites a receipt **and**
answers it with a tip claim" — the r72 record therefore yields `claims=0`, and the claim pass is
**vacuously green on it**. The B6 fixture is the only thing that can exercise the pass. Recommendation
to the L1: put at least one genuine tip claim in the r73 record (a receipt whose header *is* the
record tip), so the pass reports `claims>=1` and the green is not vacuous. This is an observation,
not a rule change; the freeze is untouched.

### 5.3 Notation classes the L1 must avoid to keep the round's own record green

1. **Never let `/` sit between two backticked tokens** (`` `a`/`b` ``). Write `` `a` / `b` `` with
   spaces, or one token: `` `a/b` ``. Otherwise each `/` cites the whole wave tree (135 files in r72).
2. **No section-relative receipt tokens.** `fetch.out`, `freeze.txt`, `w1-results.json`,
   `w1-dispatch.json`, `quote.txt`, `w1/…/live-r71-min.out` all rebind to `.ufo/waves/round-73/…`.
   Qualify as `.ufo/waves/round-73/…` — qualification removes ambiguity but does **not** exempt a
   round-73 path; only a *different* round's `.ufo/waves/round-<other>/…` is skipped.
3. **No brace expansion** in a citation (`kill-{a,b,c}.out`): one token becomes 3–4 graded receipts,
   each of which must exist at the tip and carry the tip header.
4. **No ellipsis notation** (`.../receipt-tip-control-old.out`): `...` is a pre-filter, so the
   citation is silently *invisible* — it neither binds nor is graded. Do not use it for evidence.
5. **No bare `/`** (see above).
6. **A plain-text path with no backticks cites nothing**; a tip claim on such a line is ungraded.
7. **`at the tip` / `report tip` must not appear on a line that cites a receipt** unless that
   receipt's `# tip=`/`# rev=` header is exactly the record tip. Naming the measured revision
   instead is the admitted form (the claim's non-goal).
8. Repo-root tokens (`LOG.md`, `SCORECARD.md`, `corpus/knowledge/…`) are out of scope: harmless, but
   they prove nothing to either tool.

---

## 6. C2 sequencing constraint the record must respect (receipt `SCT01SurvivorRecon/record-path-rule.out`)

The base tool's declared record allow-list is fixed (`default_record_paths`, lines 217–224):

```
.ufo/waves/round-<N>/   corpus/lessons/   LOG.md   SCORECARD.md   corpus/README.md
```

A receipt is `bound` only when its header rev is an ancestor of the tip **and every path changed in
`rev..tip` is one of those five**. Everything else shifts it. Applied forward to round 73, these
planned edits are **not** record paths:

```
SKILL.md                                             record_path=False
PROVINCE.md                                          record_path=False
tools/round73-round-scope-cases.py                   record_path=False
tools/round73-receipt-claim-binding.py               record_path=False
tools/round73-province-host-drift.py                 record_path=False
corpus/SOURCES.md                                    record_path=False
corpus/knowledge/receipt-tip-binding.md              record_path=False
corpus/QUALITY.md                                    record_path=False
plans/round-73-claims.md                             record_path=False
```

The effect is already measurable: the round-72 record grades `bound=6` at `6e961996` but
`bound=0 … shifted=30` at `bc9e3059`, because `24bc96ad` touched `plans/round-73-claims.md` and
`bc9e3059` touched `.ufo/waves/round-73/*`, neither of which is a round-72 record path
(`SCT01SurvivorRecon/live-state.out`).

**Forward rule for a green round-73 record:** land every non-record change first (the three tools,
`SKILL.md`, `PROVINCE.md`, `corpus/SOURCES.md`, `corpus/knowledge/*`, `corpus/QUALITY.md`), measure
the receipts at the last such commit, then commit only record-path changes to the tip; in the record,
name that revision instead of the tip unless the header literal is the tip. Any non-record commit
after a receipt's header — including the `PROVINCE.md` block C3 is writing right now — shifts every
receipt measured before it.

Also: `--round 73` cannot be graded yet. At master the base tool prints
`RECEIPT_TIP_BINDING_UNREADABLE SCORECARD.md at master carries no '## Round 73' section; the round's
self-record cannot be read` (exit 2), and `corpus/lessons/round-73.md` does not exist. Both blobs must
exist before either C2 command produces a number.

---

## 7. Host triple (C3 input; receipt `SCT01SurvivorRecon/host-triple.out`)

| field | live value |
|---|---|
| `uname -s` | `Linux` |
| `uname -m` | `x86_64` |
| `/etc/os-release` `ID` | `arch` |

Context lines: `uname -a` → `Linux plazir27 7.2.11-arch1-1 #1 SMP PREEMPT_DYNAMIC Fri, 16 Oct 2026
00:28:58 +0000 x86_64 GNU/Linux`; `uname -r` → `7.2.11-arch1-1`; `uname -v` →
`#1 SMP PREEMPT_DYNAMIC Fri, 16 Oct 2026 00:28:58 +0000`; `uname -n` → `plazir27`.

**Does a kernel-only change move the triple? No.** From coreutils uname(1): `-s, --kernel-name`
prints "the kernel name" (the OS ABI name, `Linux`, independent of the build); `-m, --machine` prints
"the machine hardware name" (`x86_64`, a property of the hardware/ABI); the fields a kernel package
update moves are `-r, --kernel-release` and `-v, --kernel-version`. From os-release(5), `ID=` is "a
lower-case string … identifying the operating system, excluding any version information", i.e. a
distro identifier read from `/etc/os-release`, not from the running kernel. A machine move or an
OS/distro reinstall does move the triple; a kernel update does not. [OBSERVED fields + manual text;
INFERENCE for the counterfactual.]

**PROVINCE.md state (live, and it changed while this seat ran):** there was **no** host-identity
block when the seat started (`grep -n 'host-identity block' PROVINCE.md` → no match; the only host
prose was the round-71 re-derivation at line 272, which records `uname -s` and `uname -r` but never
`uname -m` or the os-release `ID`). By the time the receipt was written, line 310 carried:

```
Round-73 host-identity block (2026-11-03). Host triple: `uname -s` -> `Linux`; `uname -m` -> `x86_64`;
`/etc/os-release` `ID` -> `arch`. Graded by `tools/round73-province-host-drift.py`; a host move is
answered by appending a later block, never by editing this one.
```

That block's triple equals the live triple above, it is the newest (and only) block in file order, and
its first line matches the frozen grammar `Round-<N> host-identity block (YYYY-MM-DD)`. It was
**uncommitted** at probe time (` M PROVINCE.md`), and `PROVINCE.md` is not a base-tool record path
(§6) — so it must be committed before the receipts it is meant to be contemporaneous with are
measured, or those receipts shift.

---

## 8. Confidence and remaining unknowns

* **Observed** (exact command + exit in the named receipt): every fixture build, every counter run,
  every exposing command, the ignored-record census and bound, the census counts and the 147/6/105/24/12
  split, the record-path list, the tip-claim line set, the host triple, the PROVINCE block.
* **Inference:** the claim that a kernel-only update leaves `uname -s`/`-m` and `ID` unchanged
  (manual-based, not experimentally induced — this seat did not update a kernel).
* **Unknown / out of scope:** whether the three v2 modules will be implemented against these traps;
  the final record tip and therefore the final `cited/bound/…` numbers; whether the L1 will allow-list
  `PROVINCE.md`/`SKILL.md` in C1's `stray` case (the frozen predicate says the allow-list is declared,
  but does not declare it).
* This seat reports **no disagreement with the freeze**. One operability note is offered, not a rule
  change: the C2 claim pass is vacuously green on a record whose tip claims never sit on a
  receipt-citing line (§5.2).

---

## 9. Files written (all inside the seat's write scope)

```
.ufo/waves/round-73/w1/SCT01SurvivorRecon.md                     this report
.ufo/waves/round-73/w1/SCT01SurvivorRecon/base-counter-survivors.out
.ufo/waves/round-73/w1/SCT01SurvivorRecon/exposing-commands.out
.ufo/waves/round-73/w1/SCT01SurvivorRecon/ignored-bound.out
.ufo/waves/round-73/w1/SCT01SurvivorRecon/a6-enumeration.out
.ufo/waves/round-73/w1/SCT01SurvivorRecon/worktree-hazard.out
.ufo/waves/round-73/w1/SCT01SurvivorRecon/citation-census.out
.ufo/waves/round-73/w1/SCT01SurvivorRecon/record-path-rule.out
.ufo/waves/round-73/w1/SCT01SurvivorRecon/live-state.out
.ufo/waves/round-73/w1/SCT01SurvivorRecon/host-triple.out
```

Every `.out` above starts with `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec`. No `__pycache__` was
created under the wave directory (`PYTHONDONTWRITEBYTECODE=1` on every python invocation; the census
and record-path scripts ran from scratch).

## 10. Commands run (all with observed output; verbatim in the receipts)

| # | command | observed |
|---|---|---|
| 1 | `build-survivors.py --work <S>/ctrl --meta <S>/ctrl/fixtures-meta.json` | 6 `FIXTURE` lines, `META …`, exit 0 |
| 2 | `git -C <each fixture> rev-parse --show-toplevel` | equals the fixture dir for all six |
| 3 | `round72-round-scope.py --repo <c1_clean> --round 73 --tip master` | `findings=0`, exit 0 |
| 4 | `round72-round-scope.py --repo <c1_a5> --round 73 --tip master` | `findings=0`, exit 0 |
| 5 | `round72-round-scope.py --repo <c1_a6e> --round 71 --tip master` | `findings=0`, exit 0 |
| 6 | `round72-round-scope.py --repo <c1_a7sub2> --round 73 --tip master` | `findings=0`, exit 0 |
| 7 | `round72-round-scope.py --repo <c1_a6e> --round 72 --tip master` | 2 findings (`label`, `ignored`), exit 1 |
| 8 | `git -C <a5> status --porcelain -uall` | empty |
| 9 | `git -C <a5> worktree list --porcelain` / `worktree list` | primary + `c1_a5-wt` (detached) |
| 10 | `git -C <a5-wt> status --porcelain -uall` | ` M LOG.md`, `?? stray-in-wt.txt` |
| 11 | `git -C <a6e> status --porcelain -uall --ignored -- .ufo/waves/round-71` | empty |
| 12 | `git -C <a6e> status --porcelain -uall --ignored -- .ufo/waves` | `!! .ufo/waves/round-72/hidden.log` |
| 13 | `git -C <a6e> check-ignore -v .ufo/waves/round-72/hidden.log` | `.gitignore:1:*.log …` |
| 14 | `git -C <a6e> ls-tree --name-only HEAD .ufo/waves/` | only `.ufo/waves/round-71` |
| 15 | `ls -d <a6e>/.ufo/waves/round-*` | round-71 and round-72 |
| 16 | `git -C <a6e> cat-file -e HEAD:.ufo/waves/round-72` | `path … exists on disk, but not in 'HEAD'` |
| 17 | `git -C <a7sub2> status --porcelain -uall` | empty |
| 18 | `git -C <a7sub2> status --porcelain -uall --ignored -- sub` | empty |
| 19 | `git -C <a7sub2> status --porcelain -uall --ignore-submodules=none` | ` M sub` |
| 20 | `git -C <a7sub2>/sub status --porcelain -uall` | ` M child.txt`, `?? leak.txt` |
| 21 | `cat <a7sub2>/.gitmodules` | `ignore = all` |
| 22 | `git -C <a7sub2> submodule status` | one initialized entry, leading space |
| 23 | `git -C <a7sub2>/sub rev-parse --show-toplevel` | the submodule dir |
| 24 | `git -C <L> status --porcelain -uall --ignored -- .ufo/waves` | 49 `!!` records |
| 25 | `… \| awk '$1=="!!"{print $2}' \| sed -E 's#^\.ufo/waves/round-([0-9]+)/.*#\1#' \| sort -n \| uniq -c` | M=25,34,45,46,47,49,50,57,59,64,70 |
| 26 | same pipeline, `sort -n \| tail -1` | `70` |
| 27 | same pipeline, `awk '$1>=73'` | empty |
| 28 | `git -C <L> status --porcelain -uall --ignored -- .ufo/waves/round-73` | no `!!` records |
| 29 | `git -C <L> status --porcelain -uall -- .ufo/waves/round-73` | `?? …` only |
| 30 | `ls -d <L>/.ufo/waves/round-*` | 63 dirs (11–73) |
| 31 | `git -C <L> worktree list --porcelain` | one entry, `detached` |
| 32 | `git -C <prune> worktree list --porcelain` (after deleting the linked dir) | block with `prunable …` |
| 33 | `git -C <prune-wt> status --porcelain -uall` | `fatal: cannot change to …`, exit 128 |
| 34 | `git -C <prune> worktree prune --dry-run -v` | `Removing worktrees/prune-wt: …` |
| 35 | `git -C <L> status --porcelain -uall \| wc -l` | 54 |
| 36 | `git -C <L> status --porcelain -uall \| grep -v '^??'` | 4 tracked modifications |
| 37 | `grep -n '^## Round 73' SCORECARD.md` | absent |
| 38 | `test -f corpus/lessons/round-73.md` | absent |
| 39 | `round72-receipt-tip-binding.py --repo . --round 73 --tip master` | `RECEIPT_TIP_BINDING_UNREADABLE …`, exit 2 |
| 40 | `round72-receipt-tip-binding.py --repo . --round 72 --tip master` | `cited=147 bound=0 unbound=105 shifted=30 stale=12`, exit 1 |
| 41 | `python3 census.py <out.json>` | 223 tokens; classes as §5; base verdict at freeze rev |
| 42 | `python3 census-render.py census.json <rev>` | the rendered census receipt |
| 43 | `python3 record-paths.py` | record allow-list + non-record paths + per-path `record_path=` |
| 44 | `uname -s / -m / -r / -v / -n / -a`; `grep ^ID= /etc/os-release` | `Linux`, `x86_64`, …, `ID=arch` |
| 45 | `man 1 uname` (`-s`, `-m`, `-r`, `-v` definitions); `man 5 os-release` (`ID=`) | quoted in §7 |
| 46 | `grep -n 'host-identity block' PROVINCE.md` | no match at start; line 310 by receipt time |
| 47 | `git -C <L> submodule status`; `ls-files -s \| grep ^160000`; `test -f .gitmodules`; `config --get-regexp ^submodule\.` | empty / none / absent / none |
| 48 | `git symbolic-ref -q HEAD`; `git status -sb` | exit 1; `## HEAD (no branch)` |
| 49 | `git log --name-status --format='COMMIT %h %s' 6e961996..master` | 2 commits; non-record path `plans/round-73-claims.md` |
| 50 | `grep -n "worktree\|ignore-submodules\|submodule" tools/round72-round-scope.py` | NO MATCH |
| 51 | `sed -n '229,300p' tools/round72-round-scope.py` (numbered) | line numbers cited in §2 |
