# CR01 — falsify C2 (two registers; permitted and out-of-region classes)

Seat: CR01Critic (kama r77 w1, leaf; judged on freshness). Attack the approach, not the owner.
Freeze commit: `7d60e2ab58866a0366937d61c9712483be57b36e` (adds `plans/round-77-claims.md`).
Base revision: `cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7`. During this seat's run the C2
counter landed (`d86ce85b`, counter blob `a3b3ec410998df443bd785ec2972f7a86a993ba3`,
byte-identical in worktree, at `d86ce85b`, and at `master`=`3442cb6a500e470c635da5e92da17d392628dda0`
at test time), so findings below are split into plan-level (frozen text) and landed-bytes
(`tools/round77-append-registers.py` @ `a3b3ec41`). Tooling: nothing installed (none needed).
All git writes happened in a fixture repo `$D=/fast/scratch/hyaku/kama-r77/CR01Critic/tmp.USSjtOjoQO`
(`git init -q`, `fetch -q <lane> master`, `update-ref HEAD cc6e1d3c…`; toplevel asserted before
every write; the lane was only read). Scratch deleted after receipts were copied here.

## Findings at a glance

| id | severity | claim |
|----|----------|-------|
| F1 | frozen-plan incoherence (load-bearing) | strict "own introduction cutoff" reading makes the frozen after-line unreachable; only ruling (a) reaches `exempt=56` |
| F2 | design hole, executed by the landed bytes | a register row naming the audited tip commit itself — even an uncommitted worktree row — blesses that commit's damage; exit 0 demonstrated |
| F3 | defect: receipt rot | registers are read from the working tree; one future round's row flips the frozen counting command to exit 1; uncommitted rows count; no register blob shas in the summary |
| F4 | clean | `out_of_region` does NOT swallow a deletion inside `## Errata` (landed bytes uphold ruling (c)) |
| F5 | clean | `permitted` does NOT swallow an event with one graded line (declared condition excludes 3 real mixed events) |
| F6 | clean | rotation: normal appends not flagged; re-add with new rows flagged; unchanged re-add is a subset |
| F7 | control | do-nothing leaves 9 (landed) / 41 (round-76 counter); rows alone can never cover the 28 permitted + 4 out-of-region events |

## F7 — do-nothing control and the row-only ceiling

Do-nothing, round-76 counter, fixture at base (exit 1):

```
$ python3 $D/tools/round76-append-exempt.py --repo $D
APPEND_EXEMPT events=241 register=53 exempt=47 restored=95 disclosed=5 unaccounted=41 cutoff=10f37171fb696c542586cbee96ea4a509ab74afc introductions=2 rotation_safe=1
APPEND_EXEMPT_FINDING unaccounted 83bee7fa… consumer-registry.md missing valid exempt row   (x4)
APPEND_EXEMPT_FINDING unaccounted 3285cdf7… SOURCES.md missing valid exempt row              (x28)
APPEND_EXEMPT_FINDING unaccounted ba9f7248… SCORECARD.md missing valid exempt row            (x9)
exit=1
```

Byte-identical to the frozen receipt `.ufo/waves/round-77/measured/before/c2-append.out`.
The 41 split exactly 9 SCORECARD + 28 SOURCES + 4 consumer-registry.

Do-nothing, landed counter, base registers (exit 1):

```
$ python3 $D/tools/round77-append-registers.py --repo $D --to cc6e1d3c…
APPEND_REGISTERS to=cc6e1d3c… events=241 accepted=53 exempt=47 permitted=28 out_of_region=4 restored=95 disclosed=5 unaccounted=9 accepted_cutoff=10f37171… exempt_cutoff=c2aa7fb2… introductions=1/1 rotation_safe=1
APPEND_REGISTERS_FINDING unaccounted ba9f7248… SCORECARD.md no valid accounting bucket  (x9)
exit=1
```

A round appending only the nine SCORECARD rows plus the landed counter-side classes reaches the
target (`exempt=56 … unaccounted=0`, exit 0 — reproduced in the fixture and at the lane). A round
that appends rows but no counter-side classes cannot: **no register row class can ever cover the
28 permitted or 4 out-of-region events** — an accepted row requires the event to carry undisclosed
graded lines (`round75-append-accepted.grade` builds `expected` from `undisclosed` only), and an
exempt-head row requires `ungraded == deleted`; permitted events have `ungraded == 0` and
out-of-region events have `graded == 0, permitted == 0`. Appending the nine rows under the OLD
counter makes things worse, not better (exit 1, 41 unaccounted + 18 rotation findings — each of
the 9 young rows is flagged twice: once in the row loop, once in the global "both ledgers bound
by the earliest introduction" loop):

```
$ python3 $D/tools/round76-append-exempt.py --repo $D   # HEAD = base + 9 rows
APPEND_EXEMPT events=241 register=53 exempt=47 … unaccounted=41 … rotation_safe=0
FINDING lines: 59 (rotation=18, unaccounted=41)
```

## F1 — the load-bearing divergence: strict cutoffs cannot reach the target

The nine strict rows demanded by the C2 content checks (ungraded, `graded==0`,
`ungraded==deleted`, sections == parents, eligible), with ancestry against both register
introductions (accepted `10f37171`, exempt `c2aa7fb2`) and the audit revision:

```
commit                                    cnt sections                    <=ACC  <=EXM  <=to
11c08bdc0064b9566dc220821db8b9116c6cf788    1 ## Axes                     False  True   True
417bbf811f2968a4567d3d3159ccf22b5d171e4d    1 ## Saturation               False  False  True
461d2adbf2b3fe596a53cb392e2bc6e82af79bfb    1 ## Axes                     False  False  True
661622b50b6b49310321e8cb99618010cf65bb75    1 ## Axes                     False  False  True
900e31b762d51b155fe79f2ef689ca52143e391e    1 ## Axes                     False  True   True
ac1c8538e391bb76cf1118da10d375b95cc4c1e9    2 ## Axes                     False  True   True
b919f0cb35f40e444899b8de70ea79b813ece678    3 ## Axes|## Planned          False  True   True
ba9f724800b7385fc3b732924ffebd143344367d    2 ## Axes|## Capabilities     False  True   True
c1ae92d56f61786c22924553038578f23971875e    2 ## Axes                     False  False  True
```

ALL nine are younger than the accepted register's introduction (why the old single cutoff
rejected them), but **four are younger than the exempt register's own introduction `c2aa7fb2`**.
Under the predicate's literal phrase "under that register's own introduction cutoff", those four
rows are inadmissible forever: `exempt` caps at 52 and `unaccounted >= 36` — the frozen after-line
`exempt=56 … unaccounted=0` is **unreachable**. Only scope ruling (a) ("a row is admissible when
the event commit it names is an ancestor of the audit revision") reaches the target, and the
landed counter implements exactly that (`lambda commit: ancestor(repo, commit, data['to'])`).
The predicate sentence and the ruling are not paraphrases; they pick different reachable outcomes.
This is a freeze divergence for the lesson, already sent to SC02Lesson; the smallest coherent
reading that satisfies both the growth motivation and the target is ruling (a), and the predicate
phrase should be recorded as divergent, not re-scoped silently.

## F2 — the growth hole the landed bytes execute: same-commit, uncommitted blessing

Ruling (a) leaves no temporal bound on rows. Two demonstrations against the landed counter.

**(a) accepted register**: fixture tip `9e91de10f77b…` deletes one graded, never-restored,
never-disclosed line of `corpus/README.md`; an **uncommitted worktree row** in
`registry/append-only-accepted.tsv` names the tip commit itself (hash/count/class/note all
valid). `accepted` moves 53 → 54 — the fresh deletion is accounted as "accepted history" by a
row that exists nowhere in git:

```
$ python3 $D/tools/round77-append-registers.py --repo $D --to 9e91de10f77b…
APPEND_REGISTERS to=9e91de10… events=242 accepted=54 exempt=47 … unaccounted=10 … rotation_safe=1
```

(exit 1 here is caused solely by an unrelated fixture collision, see Fixture notes; the bless
itself succeeded — the new event sits in the accepted bucket.)

**(b) exempt register, clean exit 0**: fixture tip `30b88bf21476…` re-derives `## Retired`
in place (deletes one line, adds one line — the operation the contract declares re-derived)
**in the audited commit itself**, plus an uncommitted exempt-head row naming that commit, plus
the nine strict rows:

```
$ python3 $D/tools/round77-append-registers.py --repo $D --to 30b88bf21476…
APPEND_REGISTERS to=30b88bf2… events=242 accepted=53 exempt=57 permitted=28 out_of_region=4 restored=95 disclosed=5 unaccounted=0 accepted_cutoff=10f37171… exempt_cutoff=c2aa7fb2… introductions=1/1 rotation_safe=1
exit=0
```

Green, with a head edit made and blessed in the very commit under audit, and the blessing row
never committed. Every kill arm stays quiet: the row exists (not `missing-row`), counts match
(not `wrong-count`), the deletion is in an exempt head section, not inside an `only=` region
(not `inside-region`), and no path was re-introduced (not `rotation`).

This contradicts the lane's own doctrine in three places: the audit's disclosure rationale
("a ledger that accepts new rows would bless any later damage" — round-51 K2Cheat/K2Design),
the round-75 tool's own default cutoff (`precedes` = proper ancestor of the register's
introduction; under it the same fixture exits 1 with `post-introduction`, demonstrated:
`accepted=53 unaccepted=1 post-intro=1 exit=1`), and the round-76 counter's
post-introduction/rotation arms. The frozen C2 ruling (a) removed the bound and the landed
bytes execute the removal. Classification for the judge: if (a)-growth is intended (the target
requires it), this is an accepted tradeoff and the kill-rule list should say so honestly; if
not, the fix is: **a row is admissible only when the event it names is a proper ancestor of the
commit that first carries the row** (9/9 target rows pass; same-commit rows fail). Note the
exempt-head variant is the milder case (the audit already classes non-gutted head deletions as
sanctioned re-derivations); the accepted-register variant blesses arbitrary graded deletions.

## F3 — defect: receipt rot (worktree register reads)

The landed counter reads both registers from the working tree
(`(repo / ACCEPTED).read_bytes()`), inverting the round-76 discipline ("Inputs are committed at
the audit's explicit `to` revision, never worktree TSVs"). Consequences, all demonstrated:

1. The frozen counting command is only green while the worktree registers stay byte-identical.
2. One row naming an event outside the `--to` audit — exactly what round 78's legitimate growth
   will add — flips the frozen command to exit 1 while every bucket stays green:

```
$ python3 $D/tools/round77-append-registers.py --repo $D --to cc6e1d3c…   # registers = green + 1 future row
APPEND_REGISTERS to=cc6e1d3c… events=241 accepted=53 exempt=56 … unaccounted=0 … rotation_safe=1
APPEND_REGISTERS_FINDING wrong-class 3ea72307c6aa… consumer-registry.md not a class-bound exempt-head event
exit=1
```

   The round-77 C2 receipt cannot survive the next round's append; and the failure mode
   (`unaccounted=0` + exit 1 via a `wrong-class` finding) is confusing to debug.
3. The blessing rows of F2 need no commit at all.
4. The summary line prints `accepted_cutoff`/`exempt_cutoff` but not the register blob shas, so
   a receipt does not record which register bytes produced it.

Root cause is a frozen-text bind: the counting command pins `--to cc6e1d3c…` (base) while the
growth semantics require rows newer than base — no committed-blob reading can satisfy both.
Smallest safe correction: read registers at `--to` and run the frozen command at the round tip,
recording the divergence in the lesson's §Freeze divergences (or, minimally, print both register
blob shas in the summary line so receipts are at least self-identifying).

## F4 — clean: `out_of_region` does not swallow an inside-region deletion

Fixture `264d8ce63b95…` deletes one row **inside** the declared `## Errata` region of
`corpus/knowledge/consumer-registry.md`:

```
audit at 264d8ce6: deleted=1 graded=1 ungraded=0 permitted=0 status=unrestored undisclosed=1
landed counter: out_of_region=4 (unchanged) … unaccounted=10, exit=1
```

Ruling (c) upheld: a deleted line inside the declared region kills the class; the event cannot
be exempt-head (no exempt titles on that file) or permitted (A-corr), so it stays a finding.
Fixture `6be5b40528e2…` deletes one census line **outside** the region:
`graded=0 ungraded=1 status=ungraded` → `out_of_region=5` (the new event classed) — the class
works as declared. (Fixture noise: the outside-deletion shifted the line-addressed `declared_at`
pointer `consumer-registry.md:30`, so the audit adds a `bad_declarations` finding — frozen-audit
pointer fragility, out of C2's scope, noted for honesty.)

## F5 — clean: `permitted` does not swallow a one-graded-line event

From the frozen audit JSON at base (independent recomputation): the permitted bucket is exactly
28 events, all on `corpus/SOURCES.md` (the only A-row file with events), each satisfying the
declared condition `permitted == deleted ∧ graded == 0 ∧ ungraded == 0`. The population also
contains **3 real mixed events** that a laxer rule would swallow — e.g.
`5890d1a0e20c SOURCES.md: deleted=7 permitted=6 graded=1` — and all three are excluded by the
declared condition (6 ≠ 7, 276 ≠ 638, 277 ≠ 639). All three are also `restored`, so a
`permitted>0` counter would double-bucket them and break exactly-once accounting. The landed
counter's own `permitted-overclaim` selftest arm (graded defeats a forged `permitted==deleted`)
PASSes. Answer: the declared condition is the right guard and holds on the data.

## F6 — clean: rotation answers, with the rule's own logic and the landed bytes

* Re-added register carrying one new row → flagged. Landed fixture `b7b7f930…` (delete, re-add
  with 9 new rows): `introductions=1/2 rotation_safe=0`, finding
  `rotation b7b7f930… registry/append-only-exempt.tsv re-introduction carries new rows`, exit 1.
  The landed `history()` compares against the **last extant version** ("the immediately preceding
  version of a deleted path is the last extant version, not the absent blob at the re-add's
  parent") — this also resolves the subset-rule ambiguity (an absent-version reading would flag
  even identical re-adds).
* Normal append → **not** flagged. Landed fixture `36dedcd9…` (one appended row naming a young
  event): no rotation finding, `rotation_safe=1`, row valid (`exempt=48`, `unaccounted=8`).
  The round-76 counter, by contrast, labels the same append's young row class `rotation`
  (mislabel: `introductions=2 > 1` picks the label; fixture evidence captured).
* Unchanged delete/re-add → subset, not flagged (`rotation_safe=1`); exit stays 1 only via the
  9 unaccounted.
* Landed `--selftest`: 7/7 PASS (`audit-fixture-green, missing-row, wrong-count, wrong-class,
  inside-region, rotation-reintroduced, permitted-overclaim`). The old counter's selftest: 6/6 PASS.

## Target arithmetic — each bucket derived independently from the audit JSON

Independent recomputation (`buckets.py`) from
`python3 tools/append-only-audit.py --repo <lane> --to cc6e1d3c… --json` (exit 1; 241 events):

| bucket | value | derivation |
|--------|-------|------------|
| events | 241 | `len(events)` == `summary.events` |
| restored | 95 | `status=="restored" ∧ held_at_to==graded` (status-only count is also 95) |
| disclosed | 5 | `status=="disclosed"` |
| accepted | 53 | `round75-append-accepted.grade` — **identical with and without the temporal bound**, so ruling (a) does not inflate the base bucket |
| exempt | 47 (+9 = 56) | rows valid under the C2 content checks; at base all 47 are also valid under the old single cutoff; the +9 are exactly the strict-row set of F1 |
| permitted | 28 | declared condition; all `corpus/SOURCES.md` |
| out_of_region | 4 | uncovered ungraded events on `only=`-files; all `corpus/knowledge/consumer-registry.md` |

Pairwise disjoint (no overlaps). At base: 95+5+53+47+28+4 = 232, remainder = **exactly the nine
strict rows**; after the round's nine rows: **95+5+53+56+28+4 = 241 = events, exact partition**.
The frozen arithmetic is correct and each bucket is honestly derived.

## Fixture notes (honesty)

* `0718b6ab` demotion: the README-deletion fixtures (`9e91de10…`, `ed593921…`) re-deleted a line
  that base event `0718b6ab` (corpus/README.md, graded=663, restored, held_at_to=663) had
  restored, dropping `held_at_to` to 662. The audit status stays `restored` (window-max,
  X1Stable) but the counter's "restoration held at the audit revision" bucket demotes it —
  correct behavior, and it is the sole cause of exit 1 in demonstration (a). My candidate filter
  used the audit's `summary.restored`, which cannot see the demotion.
* The outside-Errata fixture shifted the line-addressed `declared_at` pointer
  (`consumer-registry.md:30`), adding a `bad_declarations` finding — fixture artifact, not a
  counter defect.

## Receipts (absolute paths, command, exit code)

All under this directory (`…/.ufo/waves/round-77/w1/CR01Critic/`):

| file | command | exit |
|------|---------|------|
| `receipts/audit-base.json` | `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py --repo <lane> --to cc6e1d3c… --json` | 1 (expected: unrestored events at base) |
| `receipts/fixtures.out` | `python3 $S/c2_fixtures.py` (old-counter fixtures) | 0 |
| `receipts/fixup.out` | `python3 $S/fixup.py` (9-row NC1, NC4 diff, NC6) | 0 |
| `receipts/landed.out` | `python3 $S/landed.py` (landed-counter battery) | 0 |
| `receipts/airtight.out` | `python3 $S/airtight.py` (self-bless exit-0, receipt rot) | 0 |
| `scripts/*.py` | the four drivers + `buckets.py` + `fixture-path.txt` | — |

Verbatim lane runs: `python3 tools/round77-append-registers.py --repo . --to cc6e1d3c…` → the
frozen target line, exit 0 (at `master`=`3442cb6a`); `--selftest` → 7/7 PASS, exit 0.

## Checks Main should run

1. `cd /home/vgpnk/Projects/shokunin/kama-shokunin && python3 tools/round77-append-registers.py --repo . --to cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7; echo $?` → expect the target line, exit 0 (and re-run after ANY register change: F3 predicts exit 1).
2. `python3 tools/round77-append-registers.py --selftest; echo $?` → 7/7, exit 0.
3. If F2/F3 are accepted as defects: the correction is scoped in F2 (proper-ancestor-of-row-commit) and F3 (registers at `--to`, counting command at the round tip, §Freeze divergences entry).
