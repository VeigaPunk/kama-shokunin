# SCT01ReceiptRecon — receipts, revisions and the drift class (kama round 72, w1)

Read-only scout seat. Lane `kama-shokunin`, milestone `kama r72 w1`.
**Tip checked: `a3cc39f08f4692e990921cf938d0269f6c25fc93` (`master`).** The freeze (`plans/round-72-claims.md`) was read in full and
not edited; this seat reports observations only.

## Result in one table

| metric | occurrences | distinct paths |
|---|---|---|
| receipt citations enumerated (SCORECARD rounds 70-71 + `corpus/lessons/round-7*.md`) | **77** | **39** |
| unbound — no `# tip=`/`# rev=` in the first five lines | **55** | **28** |
| strict header (`# tip=`) — the only form the frozen C2 predicate accepts | 7 | 3 |
| lenient header (`tip=` with no `#`) | 15 | 8 |
| shifted — `<rev>..tip` touches the frozen instrument list (`tools/ SKILL.md PROVINCE.md corpus/SOURCES.md corpus/knowledge/ registry/ plans/`) | **22** | **11** |
| shifted under this seat's five-prefix list (no `registry/`, `plans/`) | 15 | 8 |
| non-ancestor header revision (absent from the lane repo) | 5 | 3 |
| stale — cited receipt absent at the tip | **0** | **0** |
| bound and clean under the frozen list | **0** | — |

Also cited in the same six texts but outside the receipt population: 14 evidence files, 4 scripts,
5 directories, 1 missing path (a fixture-relative `w1/out/` in prose). Full per-citation table:
`.ufo/waves/round-72/w1/SCT01ReceiptRecon/table.tsv` (102 lines); method and the 39-row distinct
table: `.ufo/waves/round-72/w1/SCT01ReceiptRecon/recon.md` §1-§3.

## (a) Findings

1. **Nothing cited is stale.** All 39 distinct cited receipt paths exist as blobs at
   `a3cc39f0`. The drift here is revision binding, not missing files.
2. **Unbound dominates: 55/77 citations (28/39
   distinct) name no revision.** No receipt puts its tip line after line 5 — the line is absent.
3. **Only 3 distinct receipts use the strict `# tip=` form** the frozen predicate
   accepts (the three round-71 `measured/after/*-at-tip.out`). 8 more use `tip=`
   without `#` (round-70 reconciler family, `round-71/measured/before/reconciler.out`): `unbound`
   under the frozen wording, though the round-70 report calls that line a header. Reported as a
   wording disagreement, not an edit to the freeze.
4. **Every bound receipt is shifted: 22/22 under the
   frozen list; 15 under the seat text's five prefixes.**
   `7be07423..a3cc39f0` touches 9 instrument inputs (both round-71 tool sets, `SKILL.md`,
   `PROVINCE.md`, `corpus/SOURCES.md`, two `corpus/knowledge/` entries). The three `4b284653`
   receipts are clean under the five-prefix list and shifted under the frozen list only because
   round 72's freeze commit touches `plans/round-72-claims.md` (`4b284653..a3cc39f0` = 19 files).
5. **3 distinct receipts (5 citations) name revisions absent from the
   lane repo** — `a7ae13ab6211…` (`check-kill-probe-intact.out`, `check-kill-probe-gutted.out`) and `af6e1c84d146…`
   (`reconciler-record-only-dry.out`). `git cat-file -t` and `git merge-base --is-ancestor` both
   exit 128. The round-70 lesson's L1 correction 3 records this by hand; the table is its census.
6. **Resolver hazards, named not hidden:** `w1/out/` in `round-71.md` Mistake 2 describes a fixture
   clone (resolves to a nonexistent lane dir), and `.ufo/waves/round-16/17/live/receipt*.json` joins
   two waves with `/`. Both must be could-not-evaluate (C2 exit 2), never `stale`.
7. 12 citations in the same texts point at older waves (`round-16/48/49/61/67/68/69`) through the
   round-70 capability table; outside the `round-7*` population, excluded from every count above.

## (b) `.ufo/reports/round-71/kama.md` (fleet repo, read-only)

The report claims the tip is **`7fb6cb4e31dc2f96e4815240a12bfe8da4d07e2e`** ("measured lane commit
… `ls-remote` equals the local tip"). It cites 23 paths: 15 receipts, 3 dirs, 3 evidence files,
2 scripts. The 15 receipts (`W:` = `.ufo/waves/`):

| receipt cited | exists | header | revision named | ancestor of tip |
|---|---|---|---|---|
| `W:round-71/measured/after/boundary-at-tip.out` | yes | `# tip=` | 4b2846535fd918881ed3fc664aa46ef130a7d568 | yes |
| `W:round-71/measured/after/pre-report-at-tip.out` | yes | `# tip=` | 4b2846535fd918881ed3fc664aa46ef130a7d568 | yes |
| `W:round-71/measured/after/province-claims-at-tip.out` | yes | `# tip=` | 4b2846535fd918881ed3fc664aa46ef130a7d568 | yes |
| `W:round-71/measured/before/census-shim-control.out` | yes | none | — | — |
| `W:round-71/measured/before/git-status.out` | yes | none | — | — |
| `W:round-71/measured/before/newest-closure.out` | yes | none | — | — |
| `W:round-71/measured/before/pre-report-shortcut.out` | yes | none | — | — |
| `W:round-71/measured/before/province-claims.out` | yes | none | — | — |
| `W:round-71/measured/before/receipt-audit.out` | yes | none | — | — |
| `W:round-71/measured/before/reconciler.out` | yes | `tip=` no `#` | f3ee44f47a9680437eeae63a8fa8807552a65119 | yes |
| `W:round-71/measured/before/wlc.out` | yes | none | — | — |
| `W:round-71/w1/EX01PreReportGate/selftest.out` | yes | none | — | — |
| `W:round-71/w1/EX03ProvinceClaims/kill1-flipped.out` | yes | none | — | — |
| `W:round-71/w1/EX03ProvinceClaims/kill2-wrongtag.out` | yes | none | — | — |
| `W:round-71/w1/EX03ProvinceClaims/kill3-rewrite.out` | yes | none | — | — |

Counts: **11 of 15 unbound**; 3 name `4b284653`; 1 names `f3ee44f4`.

**Mismatches named (the class C2 removes):**

1. **"The instrument runs at the report tip"** (C1 work item) vs
   `pre-report-at-tip.out` line 1 = `# tip=4b2846535fd918881ed3fc664aa46ef130a7d568`.
   `git rev-list --count 4b284653..7fb6cb4e` → **3** (1375f51c, 9458c3d7, 7fb6cb4e); to `a3cc39f0`
   → 6. The Before→after section names `4b284653` correctly, so the *claim* is the defect.
2. **"`9458c3d7` (final gate confirmation)" has no receipt naming `9458c3d7`.**
   `grep -rl 9458c3d7 .ufo/waves/round-71/` → nothing; that commit adds
   `measured/after/pre-report-at-final.out` whose header is `# tip=1375f51c…`, and the report
   never cites that receipt.
3. **"seven green receipts at `4b284653`" is eight.** `git show --stat 1375f51c` → 8 files changed,
   all `measured/after/*.out` (boundary, newest-closure, pre-report-at-tip, province-claims,
   receipt-audit, reconciler-at-tip, sources-census, wlc).
4. **11 of 15 cited receipts are unbound**, so the report's tip statement is checkable
   only against the three gate receipts it names — and those three disagree with it.

Adjacent, same class: `corpus/lessons/round-71.md` says "the lane tip `9458c3d7` equals `ls-remote
origin refs/heads/master`" while the block stating it lands in `7fb6cb4e`; the round-71 verifier
spot-check calls `4b284653` "two commits before" `7fb6cb4e` where `rev-list --count` gives 3.

## (c) Ignored file is invisible to `-uall`, visible to `--ignored`

Throwaway fixture `mktemp -d -p $S` + `git init`, toplevel asserted equal to `$D`, one commit with
`git -C "$D" -c user.name=fixture -c user.email=fixture@invalid commit`, fixture removed by
`trap … EXIT`. Raw transcript: `.ufo/waves/round-72/w1/SCT01ReceiptRecon/ignored-fixture.out`.

```
fixture=/fast/scratch/hyaku/kama-r72/SCT01ReceiptRecon/fixture.vr2LK0
toplevel=/fast/scratch/hyaku/kama-r72/SCT01ReceiptRecon/fixture.vr2LK0
--- status --porcelain -uall
?? .ufo/waves/round-72/untracked.out
rc=0
--- status --porcelain -uall --ignored
?? .ufo/waves/round-72/untracked.out
!! .ufo/waves/round-72-ignored-only/ignored-only.out
!! .ufo/waves/round-72/ignored.out
rc=0
--- gate-arm form: status --porcelain -uall -- .ufo/waves/round-72
?? .ufo/waves/round-72/untracked.out
rc=0 files=1
--- gate-arm form with --ignored
?? .ufo/waves/round-72/untracked.out
!! .ufo/waves/round-72/ignored.out
rc=0 files=2
--- ignored-only wave dir: gate-arm form (status --porcelain -uall -- .ufo/waves/round-72-ignored-only)
<empty>
rc=0 files=0
--- ignored-only wave dir: with --ignored
!! .ufo/waves/round-72-ignored-only/ignored-only.out
rc=0 files=1
--- check-ignore verdict
.gitignore:1:ignored.out	.ufo/waves/round-72/ignored.out
rc=0
--- check-ignore on a non-ignored path
rc=1
```

The three decisive commands, run with `$D` = the `mktemp` fixture (the transcript names the
concrete path), and their observed output:

```
$ git -C "$D" status --porcelain -uall
?? .ufo/waves/round-72/untracked.out
rc=0

$ git -C "$D" status --porcelain -uall --ignored
?? .ufo/waves/round-72/untracked.out
!! .ufo/waves/round-72-ignored-only/ignored-only.out
!! .ufo/waves/round-72/ignored.out
rc=0

$ git -C "$D" status --porcelain -uall -- .ufo/waves/round-72-ignored-only
<empty>
rc=0 files=0
```

The ignored-only wave dir is the vacuous green the base arm cannot see: the same dir with
`--ignored` prints `!! .ufo/waves/round-72-ignored-only/ignored-only.out` and `files=1`. The
mixed dir shows both classes at once (`files=1` under the base arm — only the untracked file —
`files=2` with `--ignored`). `git check-ignore -v .ufo/waves/round-72/ignored.out` →
`.gitignore:1:ignored.out` (exit 0); `git check-ignore -q .ufo/waves/round-72/untracked.out` →
exit 1.

## Freeze movement observed (recorded, not judged)

The worktree `plans/round-72-claims.md` gained a **"Freeze amendment 2, 2026-11-03T22:50 -03"**
block (empty population `cited=0` → exit 2) after this seat read the plan in full (before its first clock reading, `22:45:47 -03`). The
committed copy at `a3cc39f0` still hashes to `39f4ddbc…`, exactly the hash `controls/freeze.txt`
pins — so the frozen commit does not carry amendment 2. At `date -Iseconds` = `2026-11-03T22:49:03-03`
the worktree file's `stat` mtime read `22:42:21`, i.e. earlier than both the declared amendment time
and the 22:44 read that lacked the block. Recorded as a time-provenance observation (the round-71
"impossible correction date" class); no lane file was edited and nothing here is judged.

## Files written (all inside `.ufo/waves/round-72/w1/`)

`SCT01ReceiptRecon.md` (this report) and `SCT01ReceiptRecon/`: `recon.md`, `table.tsv`,
`recon.json`, `report71-receipts.json`, `report71.out`, `commands.out`, `ignored-fixture.out`,
`distinct-table.md`, `enumerate.py`, `report71.py`, `ignored-fixture.sh`, `commands.sh`.
No lane file was edited; no git or jj mutation was run anywhere.

## Limits

The population is paths *cited* in the six named texts; receipts quoted only by value are not
counted. Section boundaries are heading-based, so the "capabilities as of round 71" table counts
inside the round-70 section. `master` moved during the recon (`090a0b25` → `a3cc39f0`); every
number stands at `a3cc39f0` and is recomputable by `enumerate.py a3cc39f08f4692e990921cf938d0269f6c25fc93`.
