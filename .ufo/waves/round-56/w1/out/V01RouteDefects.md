# V01RouteDefects — round-55 routed defects 1, 2, 4, 5, 6, 7, 9, 10 mapped to round-56 evidence

Seat: V01RouteDefects (leaf member, no dispatch). Lane: `kama-shokunin`, round 56.
Assignment: map the eight routed defects (3 and 8 are out of scope by the seat text) to
committed round-56 evidence and classify each closed / open / operator-owned.
Advisory only: nothing here scores a claim or edits the lane.

**Lane state at read time:** `HEAD = efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` (freeze),
base `e10b6d39af450e8d652be9ac2986768b531fe13f`. `git status --porcelain` at
2026-10-27T13:07–13:10 -03:00 showed `M SCORECARD.md` plus untracked
`.ufo/waves/round-56/{build_spec.py,census/,measured/,w1.ready,w1.ready.partial,w1/}`,
`corpus/lessons/round-56.md`, `.ufo/waves/round-55/w1/w1-results.json`, and 40 paths under
`.ufo/waves/round-55/w1/out/`. The integration was writing during this seat's run (see
§Live divergence, N3); every uncommitted statement below is timestamped by that read.

Surfaces read: `corpus/lessons/round-55-verifier-spotcheck.md` (the routed list),
`.ufo/waves/round-56/preregistration.json`, `controls/`, `measured/`,
`tools/round56-{env-leg-test,env-leg-battery,prereg-check,replay-code-audit}.py`,
`tools/round54-replay-code-audit.py`, `tools/round41-scorecard-reconcile.py`,
`tools/round42-selfdesc-reconcile.py`, `tools/round43-registry-audit.py`,
`tools/gate-registry-check.py`, `.ufo/waves/round-55/c1/battery/run-battery.py`,
`.ufo/waves/round-56/w1/{spec.json,dispatch.json,validate.out}`, `SCORECARD.md`,
`corpus/SOURCES.md`, `corpus/lessons/round-55.md`, `corpus/lessons/round-56.md`.

## Verdict table

| # | Routed defect (r55 closure wording) | Round-56 surface | Verdict |
|---|---|---|---|
| 1 | C1 battery roster diverged from the immutable preregistration; re-freeze and land it | `preregistration.json` `battery.roster` + `tools/round56-env-leg-battery.py:15` + `tools/round56-prereg-check.py` | **Closed as worded** (roster equality committed and gate-killed); **new residual N1** — the roster literal is never bound to the executed runs, so the divergence class survives |
| 2 | Lesson staleness: `round-55.md` row 1 names two receipts deleted at integration | `corpus/lessons/round-56.md` §Mistakes (append-only correction) | **Content closed, commit open** — correction exists only as untracked bytes at HEAD |
| 4 | Receipts record no exit codes | `controls/base-c{1,2}.out`, `measured/{base-c1,build-c1,m-drop-ldaudit}.out` vs `measured/build-c2.out` | **Partial** — every C1 receipt carries `exit=`; the C2 measurement does not, by construction (N2 route) |
| 5 | `run-battery.py` leg assertion is a substring presence test | `round56-env-leg-battery.py:30` exact value+exit assertion | **Partial** — exact-value assertion satisfied for the one leg; kill-row semantics inverted (N2); old file untouched as history |
| 6 | S510/S511 anchor cells omit the revision element | `corpus/SOURCES.md:263-264` | **Open** — no revision element at HEAD; the value ("last updated in 2.56.0") is in both snapshots |
| 7 | Uncommitted late seat outputs (2 modified + 10 untracked) | `git status` at freeze | **Open and larger** — 40 uncommitted paths under `round-55/w1/out` + `w1-results.json`, plus six new round-56 work products |
| 9 | Attack-share classification basis not recorded in the spec | `.ufo/waves/round-56/w1/spec.json` | **Open** — no classification field; only the prose "build and attack together" |
| 10 | Stale SCORECARD labels (depth suffix; calibration "latest outside closure") | `SCORECARD.md` worktree edit | **Open at HEAD / fix in flight** — two labels corrected in the uncommitted edit; the edit cites a `§Round 56` section that does not exist (N3); gate red at HEAD is partly inherited from the base (N4) |

No defect in the routed set is operator-owned. Every one is lane-reachable.

## Per-defect detail

### 1 — C1 battery roster vs immutable preregistration — CLOSED as worded, residual N1

Committed evidence, both tips, read-only rerun of the frozen checker:

```
$ python3 tools/round56-prereg-check.py --repo <lane> --tip e10b6d39af450e8d652be9ac2986768b531fe13f
tip=e10b6d39af450e8d652be9ac2986768b531fe13f
present=0 roster_match=0 kills=0 controls=0 met=False
exit=1
$ python3 tools/round56-prereg-check.py --repo <lane> --tip efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
tip=efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
present=1 roster_match=1 kills=1 controls=2 met=True
exit=0
```

Byte equality was reproduced independently: `ROSTER` at `tools/round56-env-leg-battery.py:15`
is literal-equal to `preregistration.json` `battery.roster` (three entries:
`base-old-counter`/control/missed, `round56-counter`/positive-control/detected,
`m-drop-ldaudit`/kill/missed), and the exported C1 receipt set
`measured/{base-c1,build-c1,m-drop-ldaudit}.out` matches the prereg's control and mutant
names one for one. The re-freeze the closure asked for landed in the freeze commit itself
(`efc6b3ec`, 10 files: prereg + controls + sources + four gates).

Residual (N1): the roster constant is dead after its definition —
`grep -n ROSTER tools/round56-env-leg-battery.py` returns only line 15 — and the battery
executes three hard-coded calls at lines 40, 41, 50. C2 compares the literal to the
preregistration, so a future edit that adds or renames a `run(...)` call without touching
`ROSTER` stays `met=True`. That is structurally the round-55 defect (frozen roster vs
executed list) one level down, not a new class.

### 2 — Lesson staleness — CONTENT CLOSED, COMMIT OPEN

```
$ for p in .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out \
           .ufo/waves/round-55/c1/battery/m-extra-in-tree.out; do
      test -e "$p" && echo "present $p" || echo "missing $p"; done
missing .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out
missing .ufo/waves/round-55/c1/battery/m-extra-in-tree.out
```

`corpus/lessons/round-55.md:97-104` still carries the false sentence (it is frozen
history; rewriting it would be the round-53 defect). The append-only correction exists as
`corpus/lessons/round-56.md:19` (`class: stale-premise`, with the exact check and the
"do not rewrite the frozen lesson" fix), but `git status` shows that file as `??`
untracked at HEAD. Until the integration commit, the correction is not evidence.

### 4 — Exit codes in receipts — PARTIAL

```
controls/base-c1.out        ld_audit=missed ...            exit=0
controls/base-c2.out        present=0 ... met=False        exit=1
measured/base-c1.out        ld_audit=missed ...            exit=0
measured/build-c1.out       ld_audit=detected ...          exit=0
measured/m-drop-ldaudit.out ld_audit=missed ...            exit=0
measured/build-c2.out       tip=efc6b3ec... met=True       (no exit line)
```

`od -c .ufo/waves/round-56/measured/build-c2.out` ends `... m e t = T r u e \n` — no `exit=`.
Cause is code, not accident: `tools/round56-prereg-check.py` writes its `--out` text at the
two `open(a.out, "w").write(text)` sites and never appends the return code (the value is
returned to the shell but lost from the receipt). `round56-env-leg-battery.py:24` does the
opposite and appends `exit={p.returncode}`, which is why all five C1 receipts carry it.
Proposed fix: in `prereg-check.py`, append `f"exit={rc}\n"` to `text` before the write (or
have the caller wrap), and re-issue `measured/build-c2.out`.

### 5 — Leg assertion: presence test → exact values — PARTIAL

The routed sentence names `.ufo/waves/round-55/c1/battery/run-battery.py:140`:

```
140:            leg_failed = f"{leg} " in "\n".join(
141:                ln for ln in text.splitlines() if ln.startswith("detail: "))
142:            ok = rc == 1 and not met and leg_failed
```

That file is unchanged at HEAD (it is a frozen round-55 wave artifact; leaving it is
correct). The round-56 battery replaces the pattern with an exact field/value assertion —
`tools/round56-env-leg-battery.py:30`: `ok = p.returncode == 0 and fields.get("ld_audit") == expected`
— which is the requested class, and there is only one leg, so no per-leg discrimination is
owed. Two caveats: line 27 computes `expected_result` and never uses it (dead), and the
kill row's assertion is inverted; see N2.

### 6 — S510/S511 revision element — OPEN

```
$ grep -o 'last updated in [0-9.]*' .ufo/waves/round-55/sources/git-docs-git-config.html | head -1
last updated in 2.56.0
$ grep -o 'last updated in [0-9.]*' .ufo/waves/round-54/sources/git-docs-git.html | head -1
last updated in 2.56.0
```

Cell dump for the two rows at HEAD (`corpus/SOURCES.md:263-264`) — anchor/teaches cells:

```
S510 teaches: §Documentation/git.txt, `codeGITDIRcode` anchor (HTML copy
              `.ufo/waves/round-54/sources/git-docs-git.html`); opened 2026-10-27 by the L1
S511 teaches: §GIT_CONFIG_COUNT (HTML copy
              `.ufo/waves/round-55/sources/git-docs-git-config.html`); opened 2026-10-27 by the L1
```

No `2.56.0` (or any revision) token in either row — the same programmatic scan that finds
`6.19`/`2025-05-17` in S512/S513 finds none in S510/S511. So the round-56 gate added the
element for its own new rows and left the two rows the routed defect names untouched;
`SOURCES.md` is unmodified at HEAD and in the worktree. Fix is one token per row
(`git 2.56.0`, available in the committed snapshots) plus the old→new line the closure asks
for.

### 7 — Uncommitted late outputs — OPEN, scope grew

```
$ git status --porcelain | grep -c 'round-55/w1/out'
40
$ git status --porcelain | grep -vE 'round-55/w1/out'
 M SCORECARD.md
?? .ufo/waves/round-55/w1/w1-results.json
?? .ufo/waves/round-56/build_spec.py
?? .ufo/waves/round-56/census/
?? .ufo/waves/round-56/measured/
?? .ufo/waves/round-56/w1.ready
?? .ufo/waves/round-56/w1.ready.partial
?? .ufo/waves/round-56/w1/
?? corpus/lessons/round-56.md
```

The two tracked modifications are `J2RowCap/j2-rowcap-unit-harness.{py,json}`
(`git diff --stat` → `330 insertions(+), 13 deletions(-)`); the rest are new seat outputs
(D1, J1, J2, J3, J4, J5, J6, M1, M2, M6, V2, V4, V7, X7BatteryReplay). At the round-55
closure this count was "2 modified + 10 untracked"; it is now 40 under `w1/out` plus
`w1-results.json`, i.e. round-55 seats kept landing while round 56 was open. The closure's
instruction — commit or sweep before the successor's own report — is unmet at the freeze.
The round-56 work products in the same list (`measured/`, `w1/`, `census/`, lesson,
`build_spec.py`) are normal in-wave state that the integration commit is expected to carry.

### 9 — Attack-share classification basis — OPEN

`.ufo/waves/round-56/w1/spec.json` has exactly the keys
`wave, reportDir, maxLanes, axes, context, items`; 64 items, each with
`name, role, axes, milestone, item`. There is no attack/build field anywhere, and
`note` is absent from both `spec.json` and `dispatch.json` (only `dispatch.json`'s dispatch
note exists, and it is about the single batched task call). The only occurrence of the
word "attack" is the prompt prose "build and attack together" in `context`.
`validate.out` records only counts (`spawn=64`) and the per-member role.

For the record, the classification that *can* be derived, with its rule stated so it is
disputable: roles `critic` (8) + `mutation-tester` (8) + `sentinel` (4) + `revenger` (4) =
24/64 = 37.5%; the remaining `reviewer` (16) + `executor` (8) + `scout` (8) + `scribe` (4) +
`connector` (2) + `simplifier` (2) = 40/64. Either way the ≥25% bar clears; what the
closure asked for is that this rule be *written into the spec*, and it is not. Proposed fix:
add `"attack": {"basis": "role", "roles": [...], "count": 24, "share": 0.375}` to
`spec.json` before the wave output is committed, and cite it from the report's attack-share
sentence.

### 10 — Stale SCORECARD labels — OPEN AT HEAD, FIX UNCOMMITTED

At HEAD both labels are still the ones the closure named: depth row
`score round 1; evidence re-anchored round 54` (after the round-55 re-anchors
`ec030b36`/`4bd7521a`), calibration row
`... → 41 (outside closures on record); ... latest outside closure
corpus/lessons/round-53-verifier-spotcheck.md (rejected; re-anchored round 54)`.
The uncommitted worktree edit corrects exactly those two cells:

```
-depth | ... | score round 1; evidence re-anchored round 54
+depth | ... | score round 1; evidence re-anchored round 55
-calibration | ... → 41 (outside closures on record); ... round-53-verifier-spotcheck.md (rejected; re-anchored round 54)
+calibration | ... → 42 (outside closures on record, including round 54 and 55); ... round-55-verifier-spotcheck.md (admitted)
```

`git diff --stat -- SCORECARD.md` → `3 insertions(+), 3 deletions(-)`. The corrected count
is arithmetically right (`python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `42`).
But the label half of the defect was already a *broken fact* before round 56: at the base
commit the same reconcile is red for the count, not merely mislabeled (N4). Two problems
block calling this closed:

- **N3:** the edited head paragraph now reads "...with red base controls committed before
  data (SCORECARD §Round 56)" while `grep -c '^## Round 56' SCORECARD.md` → `0`. The edit
  points at a section that does not exist; the section must land in the same commit or the
  paragraph becomes the round-55 defect-10 class again.
- **N4:** with the fix only in the worktree, all three scorecard gates still read the HEAD
  blob and stay red — and one of the reds is not the label.

## Live divergence and new defects (route to round 57 unless fixed in this integration)

**N1 — the C2 gate proves literal equality, not executed equality.** See §1. A one-field
mutation *is* killed (verified: flipping `m-drop-ldaudit`'s designation to `control` in a
scratch clone of the two committed files gives `roster_match=0 ... met=False`, exit 1), so
the frozen C2 kill rule holds; the gap is that no gate binds `ROSTER` to the battery's
`run(...)` calls. Fix: iterate `ROSTER` in `main()` (one spec table driving both the
preregistration and the calls), or have the battery print the executed names and let C2
compare printed names to the roster.

**N2 — the C1 kill row cannot fail; the frozen target's stated mechanism is unobserved.**
`preregistration.json` target: "one-line mutant removing LD_AUDIT from BAD_ENV:
ld_audit=missed, so the battery's expected-detected check fails". The battery instead runs
the mutant with `--expect missed` (`round56-env-leg-battery.py:50`) and asserts equality, so
the row's `ok` is True and the committed receipt records `exit=0`:

```
$ python3 tools/round56-env-leg-test.py --counter tools/round56-replay-code-audit.py --expect detected   # positive control
ld_audit=detected pid=1905956 problems=['env: server environment carries LD_AUDIT']
exit=0
$ python3 tools/round56-env-leg-test.py --counter <mutant copy, LD_AUDIT removed> --expect detected
ld_audit=missed pid=1905972 problems=[]
exit=1
$ python3 tools/round56-env-leg-test.py --counter <same mutant> --expect missed
ld_audit=missed pid=1905975 problems=[]
exit=0
```

So the mechanism is real but the *committed* invocation is the inverted one; no round-56
receipt exhibits a failing expected-detected assertion, and the battery exits 0 on all three
rows by construction. The frozen kill rule ("falsified if ... the single-line mutant still
detects it") is not triggered — the mutant does miss — so C1 is not falsified. But this is
the round-53/55 "vacuous kill rule" class in the evidence chain, and it is the one place a
calibration-focused reader should press. Fix: run the kill row with `--expect detected` and
record its `exit=1`, or assert `fields.get("ld_audit") != "detected"` explicitly as a
*kill* condition, keeping the receipt that proves the assertion can fail. Also delete
`expected_result` at line 27 or use it.

**N3 — dangling `§Round 56` pointer in the SCORECARD worktree edit.** Described in §10.
Must land the section (or drop the reference) before the integration commit.

**N4 — the scorecard gate suite is red at HEAD, and not only from the label.** Recorded
exits, all against `tip=efc6b3ec`:

```
tools/round41-scorecard-reconcile.py  exit=1  axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=1 ... met=False
tools/round42-selfdesc-reconcile.py   exit=1  r41=1 ... maxN=55 mismatches=1 met=False
tools/round43-registry-audit.py       exit=1  unreg=4 defect=0 flags=0 pins=0 selftest=1 dc=0 spot=1 hidden=0 pop=58 registered=54 mismatches=6 met=False
tools/gate-registry-check.py --selftest      exit=1  GATE_SELFTEST pass=5 fail=1
tools/gate-registry-check.py --repo . --rev HEAD  exit=1  registered 54 unregistered 4 defective 0
```

Two independent causes:
(a) the four round-56 gates are unregistered in `SKILL.md` (its registry ends at the
round-55 rows, `SKILL.md:1598-1612`), and the gate selftest's own `lane-tip` fixture fails
because of them — `FAIL lane-tip efc6b3ec6fb6: exit=1 line='registered 54 unregistered 4 defective 0'`,
while SKILL.md documents `GATE_SELFTEST pass=6 fail=0`. Round-56 integration must add four
5-column registry rows (with `--flag` names and pinned sha256 prefixes: `fc3d4b63…ff6f`,
`c7b0d787…9853`) and re-pin the documented selftest count.
(b) `spot=1` — the calibration row states 41, the tree holds 42 — and this is **inherited
from the base**, not introduced now:

```
$ python3 tools/round41-scorecard-reconcile.py --tip e10b6d39af450e8d652be9ac2986768b531fe13f
tip=e10b6d39af450e8d652be9ac2986768b531fe13f
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=1 ... met=False
detail: calibration run ... no stdout line == '41' (exit 0)
```

i.e. the round-55 closure commit added the 42nd `*verifier-spotcheck.md` while leaving the
count it cites at 41. The uncommitted SCORECARD fix repairs (b); (a) is still owed.

**N5 — the round-56 lesson cites a census receipt that does not exist.**
`corpus/lessons/round-56.md:24` names `.ufo/waves/round-56/census/end.out` as the after-run
receipt; `ls .ufo/waves/round-56/census/` → `start.out` only. This is the same
"quoted output, no committed receipt" class as round-55 Rev3 D2 and it is in an untracked
file, so it can still be fixed before commit (run the census, write `end.out`, keep the
sentence).

**N6 — the round-56 lesson claims eight defect dispositions but records one.**
Line 3 says the round "answers ... routed defects 1, 2, 4, 5, 6, 7, 9, 10"; the only
per-defect entry is the defect-2 `stale-premise` row (line 19). There is no table mapping
the other seven to receipts. Since the closure reads the lesson as the round's narrative of
record, the mapping in this report can be adopted (or condensed into it) at integration.

## Frozen-claim cross-check (advisory, read-only)

- C1 baseline: the round-55 counter blob at HEAD hashes
  `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` (its preregistered
  round-55 digest) and `BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")` at line 146; it
  prints `ld_audit=missed ... exit=0`. The round-56 counter blob hashes
  `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` and adds `LD_AUDIT`
  (line 147), printing `ld_audit=detected ... exit=0`. Both digests match
  `preregistration.json`; no tool is uncommitted.
- C2: base red (`present=0 ... met=False`, exit 1), freeze green
  (`present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0); blob hash
  `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` matches; the
  one-field designation mutation is red (exit 1). Predicate, targets, kill rules and hashes
  are consistent with the frozen text as written.
- The only gap between frozen text and observed behavior is N2's phrasing
  ("the battery's expected-detected assertion fails"), which describes an invocation the
  battery does not perform.

## Confidence and limits

- High confidence on every "observed" item: each is a command whose stdout/exit is quoted
  above and re-runnable read-only at `efc6b3ec`.
- The lane was being written during this seat's read window; §7/§10 counts and the SCORECARD
  diff are snapshots at 13:07–13:10 -03:00 and may already have moved. The HEAD-blob facts
  (gates red, unregistered gates, S510/S511 rows, missing census `end.out`) are stable as
  long as HEAD stays `efc6b3ec`.
- `[INFERENCE]` marks: that the four unregistered gates are an integration-time
  registration obligation rather than a deliberate omission (the round-55 rows are
  registered the same way, and SKILL.md documents a selftest count that only holds when
  the population is registered); and that the derived 37.5% role split is a plausible
  basis, not the lane's chosen rule.
- No lane mutation, no jj/git state change, no tool installs (nothing needed; `pacman`
  untouched). Scratch `/fast/scratch/hyaku/kama-r56/V01RouteDefects/` held the mutant copy,
  the C2 mutation clone and a `TMPDIR`; it is removed before this file is yielded.
- This seat is advisory. It does not rule on the round-55 kill-rule firing, does not rescore
  C1/C2, and does not adopt or edit the lesson.
