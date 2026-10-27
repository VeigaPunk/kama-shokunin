# V03ScorecardDrift — round 56: stale depth/calibration SCORECARD labels and the round-56 re-anchor evidence

Seat: V03ScorecardDrift (round 56, kama lane). Scope: SCORECARD.md `depth` and
`calibration` rows, the head banner the re-anchor rewrites, and the round-56
re-anchor evidence. Read-only on the lane; every mutation below happened in a
throwaway clone under `/fast/scratch/hyaku/kama-r56/V03ScorecardDrift/` whose
`git rev-parse --show-toplevel` printed that clone before any commit.

Lane HEAD at measurement: `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`.
Working tree at snapshot: `SCORECARD.md` sha256
`1bddff003549e39ab6a68088d9fe91732dd959127e016066b0fb297fcac10993`
(`M SCORECARD.md`, `3 insertions(+), 3 deletions(-)`), mtime 13:07:09. The edit
landed **while this seat was reading**: the first parse of the calibration row
showed `→ 41` / round-53, later parses showed `42` / round-55 / round-56 plus the
new banner. Both states are in `receipt-label-history.txt`; the HEAD-object
readings are unaffected. The edit is in flight by the integration; this seat
neither made nor committed it.

Receipts for every number below are in
`.ufo/waves/round-56/w1/out/V03ScorecardDrift/` (`receipt-*.txt`).

## 1. Contract reconstructed from the tree (not from names)

The labels are graded by three separate instruments, none of which is a judge:

| Instrument | What it actually enforces | Source of truth |
|---|---|---|
| `tools/round41-scorecard-reconcile.py` | Per axis row: backticked hashes equal `sha256` of the file at `--tip`; cited line counts equal `wc -l`; **each `run … → …` fact is executed in a `git archive` export and its stdout must equal the cited string**; cited paths must exist at `--tip`; row must carry a hash or run fact | `AXES.md:75-83` (row = score + evidence pointer + last-change round) |
| `tools/round42-selfdesc-reconcile.py` | Banner must contain `operability + calibration`, must say `Latest measured round: <maxN>` where **maxN = greatest N over `^## Round (\d+)`**; the **first** `## Planned` section must name `### Planned (round <maxN+1>)` and that heading must exist followed by a numbered item; Saturation must state the derived vector, the canon first-working list, and the nudge token | its module docstring, read in full |
| `tools/append-only-audit.py` (v6) | SCORECARD head sections are re-derived in place **while not gutted**; a deleted graded line must reappear somewhere at `--to` ("restored") or the event is graded `unrestored` | `registry/append-only-contract.tsv:3` |

Measured facts the two rows claim, re-derived at `efc6b3ec`:

```
$ sha256sum SKILL.md corpus/knowledge/endpoint-identity.md
2d7c22125c3eee4d55134df9e15a92d1d2a8071337e96522c768a4c8cf3f4c14  SKILL.md
0100ac6d89876b2f11a58542ae1ab75c3765f61d9d138fdad4d720074ddf13d7  corpus/knowledge/endpoint-identity.md
$ wc -l SKILL.md corpus/knowledge/endpoint-identity.md   → 1612, 218
$ grep -c '^## ' SKILL.md                                → 43
$ python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))" → 42
$ python3 tools/capability-repertoire-audit.py --selftest → CAP_SELFTEST pass=2 fail=0
$ python3 tools/instrument-agreement.py --selftest        → IA_SELFTEST pass=4 fail=0
$ verdict-ledger data rows 204; claim-outcome-ledger data rows 126
```

Image shape, compressed: the two rows carry six independently re-derivable
figures and three prose labels (`evidence re-anchored round N`, `latest outside
closure … (verdict)`, `→ 41/42 (outside closures on record)`); the counters test
the six figures and **none of the three labels**.

## 2. Label state per commit (calibration row byte-identical at c2c05e30, bf336baa, e10b6d39, efc6b3ec; depth row identical from bf336baa on)

| Tip | `depth` last cell | calibration count | calibration latest closure | calibration last cell |
|---|---|---|---|---|
| `c2c05e30` (round-55 integration, row written here) | `… re-anchored round 54`, **values still `7f454761…`/1600/42 while `SKILL.md` at this commit is `2d7c2212…`/1612/43** | `41` (correct: 41 blobs) | `round-53-verifier-spotcheck.md` **(rejected)** | `… re-anchored round 53` |
| `bf336baa` (round-55 tip) | `… re-anchored round 54` (values repaired to `2d7c2212…`/1612/43) | `41` | same | same |
| `e10b6d39` (round-55 spotcheck lands → **42 blobs**) | same | `41` (**stale**) | round-53 (**stale**) | same (**stale**) |
| `efc6b3ec` (round-56 base/freeze) | same | `41` (**stale**) | round-53 (**stale**) | same (**stale**) |
| working tree `1bddff00` | `… re-anchored round 55` (**correct**) | `42` (**correct**) | `round-55-verifier-spotcheck.md` **(admitted, correct)** | `… re-anchored round 56` |

The depth row's values were repaired in two follow-up commits — `ec030b36`
(`grep -c '^## '` 42→43) and `4bd7521a` (sha `7f454761…`→`2d7c2212…`, 1600→1612
lines) — and **neither touched the suffix**, which is exactly how the depth
label drift arose. The calibration row never moved after it was written.

The `latest outside closure` half was **wrong when the row was written**: the
round-54 spotcheck (`rejected-honest-stop, admitted=false`) landed in
`3a600d2f`, the round-55 base, before `c2c05e30` typed "round-53 … (rejected)"
(the round-53 label is the row's own word; `corpus/lessons/round-53-verifier-spotcheck.md`
carries no `verdict:` header line, so this seat did not independently grade it).
The count half became wrong only at `e10b6d39`. So the row has been wrong in
two different ways for two different spans, and the round-55 verifier's defect
10 named only the first.

## 3. At the only committed tip, both named counters are red (the stale label is a broken fact, not only a mislabel)

```
$ python3 tools/round41-scorecard-reconcile.py --tip efc6b3ec…   (exit 1)
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=1 met=False
detail: calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '41' (exit 0)

$ python3 tools/round42-selfdesc-reconcile.py --tip efc6b3ec…   (exit 1)
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=55 met=False
```

Both read `--tip` blobs, never the worktree, so the in-flight edit cannot clear
them. The depth row is **not** implicated in the red: its six figures re-derive
and only its suffix was stale.

## 4. The in-flight edit fixes the rows but makes the banner false: `Latest measured round: 56` with maxN=55

The worktree edit is three lines: banner `(round 55)`→`(round 56)` and
`Latest measured round: 55`→`56`; depth suffix `round 54`→`55`; calibration
`41`→`42`, `round-53 … (rejected; re-anchored round 54)`→`round-55 … (admitted)`,
suffix `round 53`→`round 56`. Graded in a clone with exactly those bytes
committed (`4022cfec`, HEAD+worktree `SCORECARD.md`):

```
$ python3 tools/round41-scorecard-reconcile.py --repo <clone> --tip 4022cfec…   (exit 0)
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True
$ python3 tools/round42-selfdesc-reconcile.py --repo <clone> --tip 4022cfec…    (exit 1)
r41=0 banner=1 planned=0 … mismatches=1 maxN=55 met=False
detail: banner: head lacks 'Latest measured round: 55'
```

`grep -c '^## Round 56' SCORECARD.md` → `0`. The banner also cites
`(SCORECARD §Round 56)`, a section that does not exist. **Same class as the
round-55 defect 10 it is repairing** — a label asserting a body that is not
there — plus a new dangling pointer.

## 5. A section-only fix is *still* red: the `planned` fact binds the pointer line

Landing `## Round 56` raises maxN to 56; the `planned` fact then requires the
first `## Planned` section (`SCORECARD.md:53`, currently `The live plan is
\`### Planned (round 56)\``) to name `### Planned (round 57)` **and** that
heading to exist followed by a numbered item. Proven by minimal mutation in the
clone:

- `f37368be` = `4022cfec` + `## Round 56` stub appended → `banner=0 planned=1`
  `met=False` (`detail: planned: section does not name '### Planned (round 57)'`).
- `ff9bbabb` = `f37368be` + pointer line 53 repointed to round 57 + a
  `### Planned (round 57)` subsection with a numbered item → `met=True maxN=56`.

So "land the section" (the obvious fix for the dangling pointer) trades a
`banner` red for a `planned` red unless the pointer and its subsection move in
the same commit.

## 6. The banner replacement is an append-only loss, and the banner's own preservation claim is false

The worktree banner says *"the round-55 authority is kept under §Historical head
sections"*. It is not: `grep -n 'Current authority (round'` over the worktree
returns 56, 53, 45–51, 42–44 — no round-55 text anywhere. At HEAD the string
existed only at line 6, i.e. the line the edit replaced.

`append-only-audit` grades exactly that:

```
$ python3 tools/append-only-audit.py --repo . --to efc6b3ec…   (baseline)
summary … restored=69 unrestored=3 …                       # bf336baa: deleted=1 graded=1 restored=1
$ python3 tools/append-only-audit.py --repo <clone> --to 4022cfec…   (same bytes, committed)
event 4022cfec SCORECARD.md deleted=3 graded=1 ungraded=2 permitted=0 restored_max=0 held_at_to=0 status=unrestored
summary … restored=69 unrestored=4 …
```

Precedent in the same file: `bf336baa` (round-55 integration) deleted 1 graded
line and **restored** it by appending the round-53 banner verbatim under
§Historical head sections. The round-56 edit deletes the round-55 banner and
appends nothing, so `unrestored` 3→4. `registry/append-only-contract.tsv:3`
makes the head re-derivable but not gutted; a lost banner is graded.

## 7. Remaining drift neither the counters nor the routed defect 10 catch

**7.1 §Saturation window sentence is false at round 56.**
`SCORECARD.md:137` ends: *"A capability entered in round 47, so the window is not
exhausted either."* The highest canon table (`as of round 49`) has first-working
rounds `10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47` — max 47. With N=4 the
window was exhausted at round 51; at round 56 it is 9 rounds of no entry. The
sentence was true for rounds 48–50 and has been stale for 51–56. The
`round42-selfdesc-reconcile.py` saturation fact checks only the derived vector,
the canon first-working list and the `nudge inactive` token, so it cannot see
this sentence. The verdict (nudge inactive) stays right for the other reason
(calibration 7 < line 8), which is why the stale clause is invisible in every
receipt.

**7.2 The round-54 rejection disappears from SCORECARD.**
The edit rewrites the parenthetical to `(admitted)` and drops the previous
`(rejected; …)`. There is no `## Round 54` section (round 54 was an honest
stop); `grep -ci 'round.54' SCORECARD.md` → 8 hits, and every one is the
round-55 section's *counters* or the spotcheck-file run fact — `grep -c
'rejected-honest-stop'` → 0, and no line names the round-54 verdict. After the
edit the file records the round-55 admission and **nothing about the round-54
rejection**, which is a calibration-relevant fact and the reason round-55's run
fact counts the round-54 spotcheck as the 41st. Cheap repair:
`(round 54 rejected-honest-stop; round 55 admitted)`.

**7.3 The round-56 measurement receipts are untracked while the banner says
"measured".**
`git status --porcelain .ufo/waves/round-56` → `?? .ufo/waves/round-56/measured/`.
The committed controls at `efc6b3ec` are red exactly as preregistered
(`controls/base-c1.out`: `ld_audit=missed … exit=0`; `controls/base-c2.out`:
`present=0 roster_match=0 … met=False exit=1`), so "red base controls committed
before data" holds; the `build`/mutant receipts backing "measured" are worktree
only and must land with §Round 56.

**7.4 Convention note (not a defect, needs one sentence).** The calibration count
changed at `e10b6d39`, not in round 56, yet the suffix now reads `re-anchored
round 56` (the round of the *action*), while depth reads `round 55` (also the
action round). Consistent, but the §Round 56 section should state that the 41→42
bump came from the round-55 outside closure landing at the round-56 base, so the
next reader does not re-derive drift from the dates.

## 8. Verified re-anchor recipe (two commits, both green, no lane mutation)

A. **Rows only** (depth suffix `round 55`; calibration `42`, round-55 admitted,
suffix `round 56`), banner untouched → maxN stays 55:

```
tip=5a710b0d…  r41 met=True mismatches=0  |  r42 met=True mismatches=0 maxN=55   (both exit 0)
```

B. **One atomic body commit**: `## Round 56` section (maxN→56) + repoint
`SCORECARD.md:53` to `### Planned (round 57)` + that subsection with a numbered
item + append the round-55 banner **verbatim** under §Historical head sections:

```
tip=ff9bbabb…  r41 met=True  |  r42 met=True mismatches=0 maxN=56   (both exit 0; section+pointer only)
tip=6a1db785…  r41 met=True  |  r42 met=True mismatches=0 maxN=56   (both exit 0; banner also appended)
append-only: event 4022cfec SCORECARD.md deleted=3 graded=1 ungraded=2 permitted=0
             restored_max=1 held_at_to=1 status=restored restored_by=5a710b0d   # first tip where the
             round-55 banner line exists again
summary … restored=72 unrestored=4 …   # the residual 4 includes my own intermediate stub commit
                                       # ff9bbabb, whose pointer-line replacement restored nothing;
                                       # it is a scratch artifact, not a lane commit
```

The audit grades deleted *lines by content anywhere at the tip*, so placement in
§Historical head sections satisfies it, and that placement is what the banner's
own sentence promises.

Plus 7.1/7.2/7.3 in the same commit (the saturation sentence and the rejection
parenthetical are inside the graded/scanned head block; neither counter checks
them, so they will not turn red — they are corrections, not gates).

## 9. Divergence ledger

| # | Surface | At HEAD | In-flight worktree | Graded by | Severity |
|---|---|---|---|---|---|
| D1 | depth suffix | `re-anchored round 54` (round 55 re-anchored it: `ec030b36`, `4bd7521a`) | fixed → 55 | none (prose) | label |
| D2 | calibration count | `41` vs 42 in tree since `e10b6d39` | fixed → 42 | round41 `run_bad` | **red at HEAD** |
| D3 | calibration latest closure | round-53 rejected; true value round-55 admitted (round-54 rejected-honest-stop before it) | fixed → round-55 admitted, **round-54 rejection lost** | none (prose) | label + lost fact |
| D4 | calibration suffix | `re-anchored round 53` | fixed → 56 | none (prose) | label |
| D5 | banner | `round 55`, maxN=55 → consistent | `round 56` with maxN=55 and missing `§Round 56` | round42 `banner` | **new red if committed alone** |
| D6 | `## Planned` pointer | round 56 (correct at maxN 55) | unchanged | round42 `planned` | **red once §Round 56 lands** |
| D7 | banner preservation | round-55 banner at line 6 only | deleted, not re-appended; own claim ("kept under §Historical head sections") false | append-only-audit `unrestored` | **contract loss** |
| D8 | saturation window sentence | stale since round 51 | unchanged | none | stale derived claim |
| D9 | round-56 measured receipts | untracked | untracked | — | evidence not committed |

## 10. Confidence and limits

High confidence on D2, D5, D6, D7: each was demonstrated by executing the
named instrument against committed bytes and against a clone carrying exactly
the worktree bytes, with the minimal mutation that flips each fact. High on D1,
D3, D4, D8, D9: direct byte reads plus `git log` on the row and the canon table.

Not run (out of seat): the round-56 C1/C2 counters, the round-54/55 cited-path
and replay counters, sources census, any lane edit or commit. No tool installs
were needed (git, Python 3.14.8 stdlib, the lane's own counters). Scratch
`/fast/scratch/hyaku/kama-r56/V03ScorecardDrift/` was removed after the receipts
were copied here.
