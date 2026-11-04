# CRT02RecordCritic — the landing sequence and the receipt discipline

Read-only attack over the lane at `master = bc9e30599b6c6133bb094f0e7abd1a9f512778ec` (the revision
every receipt below names). Scratch: `/fast/scratch/hyaku/kama-r73/CRT02RecordCritic` (fixtures
removed; the harness sources are preserved in `harness.txt`). No lane file was modified.

Instruments measured (`sha256` at receipt time):

| file | sha256 |
|---|---|
| `tools/round73-round-scope-cases.py` | `65d9a753067e1d2e72eb58e082e317c8aa9242d2495e65f3b4123c837527c577` |
| `tools/round73-receipt-claim-binding.py` | `888eb0755df7a5b3424900ad6dd1e862c5ea9ab90140867adb008b968503be54` |
| `tools/round73-province-host-drift.py` | `ec7bfd3fdf26be7338975c07443cdd15945f378d6f01774a70ef8e71934cd919` |
| `tools/round72-receipt-tip-binding.py` (frozen base) | `a9a4e8d30546a11e6d5165b566e856e4eb8cccb11d48c5526587fd3d859b2bbd` |
| `tools/pre-report-gate.py` | `59842d4604a2d0b85db428b7b79a6758ca0dd1ffdbdc651a31a53bfbd94893e9` |

The base tool I graded with is a byte copy: its sha256 equals the lane blob at `master`
(`fixtures.out` line 9). The C2 tool was absent when this seat started and landed, untracked, mid-run
(see D6); every verdict below is against the sha above.

## Verdict in one paragraph

The two counters work as frozen: on the B6 survivor the base tool is green and the claim tool is
red naming `stale-claim`; on an instrument commit after the receipt's revision the base tool is red
naming the path; on a backticked `.md` under the wave dir both tools are exit 2, not green. The
planned sequence — instrument tip `T`, receipts with `# rev=T`, record commit `R`, final binding run
at `R` — is sound **only** if `T` is the last commit that touches an instrument input and `R` touches
only record paths. Three facts make the current shape unable to reach green without re-running:
(1) every seat receipt in the wave is stamped at the pre-instrument master (95 of 95 `.out` files
under `w1/` carry `# rev=bc9e3059…` when counted; 85 when this seat first counted — the population
only grows), so **no seat receipt may be cited by the round record**;
(2) the frozen pre-freeze control receipt is un-citable — the freeze commit itself wrote an
instrument input; (3) a receipt's header can never equal the tip that contains it (hash fixed
point), so the C2 claim pass is green only vacuously, at `claims=0`. Three holes in the frozen
notation are measured and named in §1.3 (D2/D3 in §5 are two of them).

## 1. Fixture reproduction

Command shape for every fixture (the copy of the frozen tool is `round72-receipt-tip-binding.py`,
sha `a9a4e8d3…`):

```
python3 <scratch>/round72-receipt-tip-binding.py --repo <fixture> --round 73 --tip master
python3 <lane>/tools/round73-receipt-claim-binding.py --repo <fixture> --round 73 --tip master
```

Full transcript: `w1/CRT02RecordCritic/fixtures.out`.

### 1.1 The legible positive control (assignment item 1a)

`S0`: instrument commit `T0`; receipt `# rev=T0`; delta `T0..R` touches only `.ufo/waves/round-73/`,
`SCORECARD.md`, `corpus/lessons/round-73.md`; the record line says **"measured at rev `<T0>`"**.

```
base  exit=0  RECEIPT_TIP_BINDING round=73 cited=1 bound=1 unbound=0 shifted=0 stale=0
claim exit=0  RECEIPT_CLAIM_BINDING round=73 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0
```

So the record can state a claim on a `rev=T` receipt without any tip claim and stay green. The
claim counter is `claims=0` here — that is the only reachable green value (§3).

### 1.2 The B6 shape and the other failure variants

| fixture | shape | base | claim | read |
|---|---|---|---|---|
| `S4` | receipt header `T0`; record-only delta; line says "the gate ran at the report tip" | 0, `bound=1` | **1**, `claims=1 unbound_claims=1`, finding `stale-claim … x.out :: 9: …at the report tip` | the B6 survivor is killed |
| `S5` | same, two cited receipts, line says "Both receipts at the tip" | 0, `bound=2` | **1**, two `stale-claim` findings, `claims=1 unbound_claims=1` | every cited receipt on the line is checked |
| `S7` | tip claim on a line that also cites `tools/gate.py` (repo-root, out of scope) | 0 | **1**, `stale-claim` | repo-root citations do not dilute the line |
| `c2_b6` (lane control fixture) | the committed survivor | 0 | **1**, `stale-claim … round-72/measured/a.out` | reproduces the round's own before-state |
| `S1a` | record backticks `.ufo/waves/round-73/w1/SEAT01/report.md` | **2** | **2** (echoes the base error) | red, but as could-not-evaluate |
| `S1b` | same `.md`, section-relative `w1/SEAT01/report.md`, landed | **2** | **2** | red, but as could-not-evaluate |
| `S3` ×10 | receipt `# rev=T0`; one commit after `T0` touches `P`; then record | **1** each | not run | red, `shifted` naming `P` |
| `S2a` | record backticks `w1/SEAT01/`, which holds one bound receipt **and** `report.md` | **0**, `cited=1 bound=1` | **0**, `claims=0` | **GREEN — hole named below** |
| `S2b` | record backticks `w1/SEAT01/`, which holds only `report.md` | **2**, `cited directory carries no receipt file` | — | red |

`S3` paths, each a separate fixture, each red naming the path:
`tools/gate.py`, `SKILL.md`, `PROVINCE.md`, `corpus/SOURCES.md`, `corpus/knowledge/k.md`,
`registry/r.md`, `plans/round-73-claims.md`, `.ufo/l0-questions.md`, `MISSION.md`,
`corpus/QUALITY.md`.

### 1.3 The three holes named

1. **A directory citation is green and quietly drops every non-receipt it holds** (`S2a`). The
   frozen notation says "a cited directory denotes the receipt files beneath it", so this is
   declared behaviour — but it is also the escape from the `.md` abort: `w1/SEAT01/` is green while
   `w1/SEAT01/report.md` is exit 2. It is green **only if every receipt in that directory binds**;
   because every seat receipt is stamped pre-`T`, citing a seat directory will in practice be red.
2. **A section-relative `.md` citation is green before the file lands and exit 2 after** (`S1c` vs
   `S1b`): `w1/SEAT02/report.md` cited before it exists is skipped (`exit=0`); once committed it is
   `cited path is not a receipt file (.md)` → exit 2. Seat reports land with the record, so a
   record that backticks one cannot be evaluated at its own tip.
3. **The phrase list has escapes.** With one receipt per line, all headers `T0` (not the tip), the
   claim tool counted 2 of 7 lines (`wording.out`):

   | line | counted |
   |---|---|
   | `measured at rev <T0>: …` | no |
   | `run at the instrument tip: …` | no (not a frozen token) |
   | `AT THE TIP: …` | **yes** (case-insensitive) |
   | `the gate ran at the report tip: …` | **yes** |
   | `the report-tip check: …` | no (hyphen) |
   | `the tip of the report: …` | no |
   | `the check at tip: …` | no (bare) |

   The counter is a wording lint over three literals, not a binding of meaning. A line using
   "report-tip" or "instrument tip" is uncounted yet is the same unsupported claim when the cited
   header is not that revision.

## 2. The landing sequence: every way `T..R` produces `shifted`

Planned: `T` (instrument tip) → receipts `# rev=T` → `R` (record) → final binding run at `R`.
The base tool's delta rule is `every commit in <header>..<tip> touches only record paths`, where the
record paths for round 73 are `.ufo/waves/round-73/`, `corpus/lessons/`, `LOG.md`, `SCORECARD.md`,
`corpus/README.md`. Anything else is a finding (`sequence.out`, `realhistory.out`):

| # | way `shifted` appears | evidence (verbatim) |
|---|---|---|
| 1 | a receipt is stamped before `T` (every seat receipt: 95/95 `.out` files under `w1/` name `bc9e3059`) | `B`: `shifted … seat.out :: tools/round73-province-host-drift.py touched by ec883b838684` |
| 2 | any instrument file lands **after** `T` and before the final run | `C1`: `shifted … scope.out :: SKILL.md touched by 6d0793efd110` |
| 3 | `R` itself carries one instrument file (e.g. the QUALITY criterion riding with the record) | `E`: `shifted … scope.out :: corpus/QUALITY.md touched by 9090b62e29f1` (the record commit) |
| 4 | `T` is rewritten/amended after receipts name it | `D`: `shifted … rewrite.out :: header rev beb5d681e2b6 is not an ancestor of 2353464ece7b` |
| 5 | the record cites the frozen pre-freeze receipt (`# rev=6e961996`) | `realhistory.out`: `shifted … measured/before/score-survivors-base.out :: plans/round-73-claims.md touched by 24bc96ad6e78` — the freeze commit alone, no round instrument needed |
| 6 | the record cites its own final-binding receipt | `F`: `stale … final-binding.out :: absent at 5fc8d44d36b8…` |
| 7 | a `P`-class path is touched by any commit in the delta — the ten `S3` runs: `tools/**`, `SKILL.md`, `PROVINCE.md`, `corpus/SOURCES.md`, `corpus/knowledge/**`, `registry/**`, `plans/**`, `.ufo/l0-questions.md`, `MISSION.md`, `corpus/QUALITY.md` | `S3` table in `fixtures.out` |

Two further producers visible in the tool's own code, so labelled **[INFERENCE]** (not measured
here): a **merge commit** is listed with `diff-tree -m`, so the merge's per-parent diffs include
every file that differs from either parent (instrument files included); and a **rename** across the
instrument/record boundary is listed as delete+add because `--no-renames` is fixed, so both paths
are graded. Land linearly; do not rename across the boundary.

### 2.1 What the L1 must do instead — the only sequence that reaches green

1. **One instrument tip.** Land every instrument input in one commit `T` (or a linear chain whose
   last commit is `T`): the three tools, `tools/pre-report-gate.py`, `PROVINCE.md`'s
   `Round-73 host-identity block`, `SKILL.md`'s three registry rows, `corpus/SOURCES.md` rows,
   `corpus/knowledge/**`, `corpus/QUALITY.md`. All of those are outside the record-path list, so
   they must be **before** `T`, not after. (`corpus/README.md` is itself a record path — it may land
   with `R`; it is listed here only because SCR02 may touch it.)
2. **Freeze the instruments.** After `T`, write no `tools/`, `SKILL.md`, `PROVINCE.md`,
   `corpus/SOURCES.md`, `corpus/knowledge/`, `corpus/QUALITY.md`, `registry/`, `plans/`,
   `MISSION.md` or `.ufo/l0-questions.md` bytes. `plans/round-73-claims.md` is already committed at
   `24bc96ad`; never touch it (the freeze forbids it anyway).
3. **Re-run every counter the record will cite at `T`**, and let each receipt's first line be
   `# rev=<T>` read from `git -C L rev-parse master` at that moment. Do not re-stamp an older
   receipt; re-run the command. Seat receipts (mine included) are evidence for the wave, not for the
   record.
4. **Commit `R` as record-only** — `SCORECARD.md` `## Round 73`, `corpus/lessons/round-73.md`,
   `LOG.md`, and everything under `.ufo/waves/round-73/` (all seat reports and receipts). Verify
   `git -C L diff-tree --no-commit-id --name-only -r R` is a subset of the record list before
   declaring `R`.
5. **Run the claim tool at `R`**: `python3 tools/round73-receipt-claim-binding.py --repo . --round 73
   --tip master` must print `cited=… bound=… unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0`
   and exit 0. If the record wording produces `claims>0`, rewrite the wording in a new record-only
   commit `R2`; `claims=0` is the only satisfiable green (see §3 and D1).
6. **Do not cite, with backticks, in the record**: any `measured/before/**` receipt (shifted by the
   freeze commit); any seat receipt (all `# rev=bc9e3059…`); any `.md`/`.py` under the wave dir
   (exit 2 once landed); any directory under the wave dir unless every receipt beneath it is
   `# rev=T`; the final binding run's own receipt (it cannot exist at `R`; land it in `R2` and do not
   cite it). Cite instrument paths (`tools/**`, `SKILL.md`, …) in prose or with backticks — they are
   out of scope — but a `.md` under `.ufo/waves/round-73/` is the trap.
7. **Leave the worktree clean**: arm 6 grades primary worktree + every linked worktree + every
   initialised submodule, and the gate's `round-clean` arm grades `git status --porcelain -uall --
   .ufo/waves/round-73`. Every seat receipt/report must be committed before the final gate run.
   Keep `PYTHONDONTWRITEBYTECODE=1` everywhere: an ignored `__pycache__` under `.ufo/waves/round-73/`
   is a C1 `ignored` finding.

The sequence with the final run already moves the tip: run the binding at `R`, then land its output
as `R2` (`.ufo/waves/round-73/` only) and run again at `R2`; `F2` shows the receipt with header `R`
binds cleanly at `R2` because the delta is record-only.

## 3. Wording classes (assignment item 3)

Measured against the claim tool (`wording.out`). All cited receipts have header `T0`, not the tip.

**May use — legible and green:**
- `measured at rev <40-hex>` where the hex is the receipt's own header (`S0`);
- `receipt header rev=<40-hex>`, `the receipt names <40-hex>`;
- `run before the record commit`, `measured before the record landed` (no revision is claimed);
- `run at the instrument tip <40-hex>` **only when the same line names the header hex** — the
  phrase is uncounted, so without the hex it is a claim the counter cannot see.

**Must avoid:**
- `at the tip`, `at the report tip`, `report tip` (frozen tokens, case-insensitive; the line is a
  finding whenever any cited receipt's header ≠ the tip);
- `report-tip`, `at tip`, `the tip of the report`, `at the wave tip`, `at the carrier tip`, `at the
  final tip` — uncounted by the frozen list but the same unsupported description; a reader cannot
  check them and the counter will not either.

**Structural fact:** no receipt present at tip `<rev>` can carry `# rev=<rev>`; the receipt's bytes
would be inside the tree whose hash they contain. `S6` commits the same file three times, each time
naming the previous commit, and the new sha never equals the named one. So every tip claim is false
by construction and the only green C2 record is one with **zero tip claims** — the record must name
the revision the receipt measured, never the tip.

## 4. Pre-report gate arm 6 at the time of writing (assignment item 4)

Exact arm command (what `tools/pre-report-gate.py` builds for `round-scope` at `master`):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round73-round-scope-cases.py \
    --repo /home/vgpnk/Projects/shokunin/kama-shokunin --round 73 --tip master
```

Observed (`arm6-live.out`, exit 1):

```
ROUND_SCOPE_V2 round=73 cases=6 findings=148
# finding classes: {'stray': 148}
# round-clean arm (gate argv verbatim): git -C <lane> status --porcelain -uall -- .ufo/waves/round-73 -> files=135
```

So at that run: **148 stray findings, 0 ignored-path findings, 0 label findings** — the plan heading
is green (the first line of `plans/round-73-claims.md` is `# kama round 73 — frozen claims`), the
`.ufo/waves/round-73/` wave dir is not ignored, and there is no linked-worktree or submodule finding
in the lane. Every finding is an uncommitted file: the instruments themselves (`PROVINCE.md`,
`SKILL.md`, `corpus/QUALITY.md`, `corpus/README.md`, `tools/pre-report-gate.py`, the three
`tools/round73-*.py`) plus the wave's receipts and reports. The count is time-varying (earlier in
this seat's run the same v2 arm printed 73 findings and the gate's round-clean count was 69 while
seats were still writing); the receipt is the measurement.

Will arm 6 pass at the final tip? Yes, if and only if: (a) `git status --porcelain -uall` is empty
for the primary worktree (all 148 strays committed, no `.md`/`.out`/script left untracked);
(b) no ignored path under `.ufo/waves/round-73/`; (c) no linked worktree and no initialised
submodule is dirty; (d) the plan heading still names 73. The module's own selftest demonstrates the
green path: `ROUND_SCOPE_V2_SELFTEST pass=26 fail=0`, including the `clean` arm at
`ROUND_SCOPE_V2 round=73 cases=6 findings=0` (`c1-selftest.out`). Note the selftest must be run with
cwd inside a git repo (its plan-predicate arm resolves the default `--repo .`); from a non-repo cwd
it exits 1 — run it from the lane.

## 5. Scoped defects and freeze disagreements (the freeze is not edited)

| id | defect | evidence | axis |
|---|---|---|---|
| D1 | the C2 claim pass is vacuous-green at `claims=0`, and a non-vacuous tip claim is unsatisfiable (hash fixed point) — `unbound_claims=0` is reachable only by having no tip claims, so the counter grades wording, not truth (the frozen non-goal already admits it does not prove honesty) | `S0` green at `claims=0`; `S6`; §3 | calibration |
| D2 | the frozen phrase list has escapes (`report-tip`, `at tip`, `the tip of the report`, `instrument tip`) | `wording.out`: 2 of 7 counted | calibration |
| D3 | a directory citation is green and silently drops the non-receipt files in it, so it circumvents the `.md` exit-2 rule | `S2a` vs `S1a`/`S1b` | operability |
| D4 | a backticked `.md`/`.py` under the wave dir is exit 2 once landed (inherited from the frozen base tool's "not a receipt file" rule; the r72 attack recorded it as E10/E11). The round's record legitimately wants to name seat reports, and cannot | `S1a`/`S1b`; live claim run is exit 2 until the round section exists | operability |
| D5 | the C1 `--selftest` exits 1 from a non-git cwd (its plan-predicate arm resolves the default `--repo .` and raises `ScopeError`, after every fixture arm has already PASSed); harmless when run from the lane, but the exit is not the tool's own verdict | `c1-selftest-nongit.out` (exit 1) vs `c1-selftest.out` (lane cwd, pass=26 fail=0) | operability |
| D6 | the three instruments landed **untracked** during the wave and were still being written while seats ran (only `round73-province-host-drift.py` existed at this seat's first `ls`; the C1 and C2 modules appeared later in the same run; `git status` shows all three as `??`). Any verdict against their current bytes — including this seat's fixtures, measured against the sha above — is evidence about an uncommitted file, not the round's instrument. **No such verdict is final until the bytes are committed at `T`** and the counters re-run | first `ls` at seat start: only `tools/round73-province-host-drift.py`; later `ls`: all three; `git status` `?? tools/round73-*.py` | calibration |

D6 is the operational consequence: my receipts (and every other seat's) are stamped `bc9e3059` and
were measured against uncommitted instrument bytes. The record must not cite them; it must cite
counters re-run at `T` from the committed bytes.

## 6. Counterexample, evidence, impacted axes, smallest safe correction

**Counterexample.** The L1 follows the stated sequence exactly — instruments at `T`, receipts
`# rev=T`, record `R` — and still gets `RECEIPT_TIP_BINDING … shifted=1` because one seat receipt
with header `bc9e3059` was cited (or the before-control receipt, or a QUALITY criterion that rode
with `R`, or a SKILL.md row that landed after `T`). The seat receipt is `B`, the before-control
receipt is `realhistory.out`, the QUALITY criterion is `E`, and the SKILL.md row is `C1`.

**Evidence.** `fixtures.out` (S0–S7, c2_b6), `sequence.out` (A–F2), `realhistory.out` (the freeze
commit alone shifts the before-receipt), `wording.out` (2 of 7 phrase variants counted),
`arm6-live.out` (148 strays, 0 ignored, 0 label, round-clean 135), `c1-selftest.out` (26/26, clean
arm green), `claim-live.out` (lane exit 2 until `## Round 73` exists; selftest 14/14).

**Impacted axes.** Operability is the direct axis: every failure above is a red counter on a
correctly written record. Calibration is touched twice — the C2 claim counter's only green value is
`claims=0` (D1), and the phrase list's escapes (D2) let an unsupported claim through. No product,
serving or freshness surface is involved: all fixtures are throwaway repos under scratch.

**Smallest safe correction.** Land all instrument inputs in one commit `T`; after `T` write only
record paths; re-run every counter the record cites at `T` and stamp `# rev=T`; commit seat
receipts/reports and the record as `R`; cite only those re-run receipts and name the receipt's
header revision (`measured at rev <hex>`) with no `tip` description anywhere in the `## Round 73`
section or the lesson; land the final binding run's output as `R2`. That is the whole fix — no
rule change, no freeze edit.

## Files written

- `.ufo/waves/round-73/w1/CRT02RecordCritic.md` (this report)
- `.ufo/waves/round-73/w1/CRT02RecordCritic/fixtures.out`
- `.ufo/waves/round-73/w1/CRT02RecordCritic/sequence.out`
- `.ufo/waves/round-73/w1/CRT02RecordCritic/wording.out`
- `.ufo/waves/round-73/w1/CRT02RecordCritic/realhistory.out`
- `.ufo/waves/round-73/w1/CRT02RecordCritic/arm6-live.out`
- `.ufo/waves/round-73/w1/CRT02RecordCritic/claim-live.out`
- `.ufo/waves/round-73/w1/CRT02RecordCritic/c1-selftest.out`
- `.ufo/waves/round-73/w1/CRT02RecordCritic/c1-selftest-nongit.out`
- `.ufo/waves/round-73/w1/CRT02RecordCritic/harness.txt` (the exact harness sources)

Every receipt's first line is `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec`, read at write time.
Scratch `/fast/scratch/hyaku/kama-r73/CRT02RecordCritic` is deleted before yield; `harness.txt`
carries the scripts that produced the four fixture receipts.

> Warning to the L1: this report lives at `w1/CRT02RecordCritic.md` and the receipts at
> `w1/CRT02RecordCritic/`. Do not backtick either path in the `## Round 73` section or the lesson —
> the `.md` is exit 2, and the directory is green only if every receipt inside binds, which these
> are not (all `# rev=bc9e3059…`).
