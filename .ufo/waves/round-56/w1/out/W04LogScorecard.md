# W04LogScorecard — round-56 `LOG.md` / `SCORECARD.md`: append-only and claim/counter correspondence

Seat: W04LogScorecard (scribe, leaf member — no subagent dispatch). Judged axis: calibration.
Milestone: round-56 falsification. Lane: `kama-shokunin` (read-only except this output directory).

Audit tip: `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` ("round-56: freeze LD_AUDIT env leg and
prereg roster controls"), plus the uncommitted working-tree state of `SCORECARD.md`.

Audited bytes (sha256, full list in `W04LogScorecard/SHA256SUMS.txt`):

| Surface | Digest / identity |
|---|---|
| `LOG.md` (worktree; equals `HEAD:LOG.md` blob `aca58d3e…`) | `5d810a984539d46cfab0413d1fc8e6e588c291aca20328665b16af87474c6eaa` |
| `SCORECARD.md` (worktree; `HEAD` blob `b1765081…`) | `1bddff003549e39ab6a68088d9fe91732dd959127e016066b0fb297fcac10993` |
| `.ufo/waves/round-56/preregistration.json` | `fa4b5a100a9fd6ceaec93c537f3d9264a0883fac873368243ff1ae041d82ee68` |
| `tools/round56-replay-code-audit.py` (frozen C1 counter) | `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` |
| `tools/round56-prereg-check.py` (frozen C2 checker) | `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` |
| `tools/round54-replay-code-audit.py` (round-55 C1 counter, base) | `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` |
| `tools/round56-env-leg-test.py` (harness, not frozen) | `ec7a2519f6d4b2e1bd08a7ead042a53c7b60e2f58af8e4db008dfd661acf82ac` |
| `tools/round56-env-leg-battery.py` (battery, not frozen) | `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c` |

## Verdict

**Not admitted at the audit tip.** Two required appends are absent (no round-56 `LOG.md` entry at
all; no dated `## Round 56` SCORECARD section), and the one round-56 append that does exist — the
uncommitted `SCORECARD.md:6` head banner — (a) points at a section that does not exist, (b) fails
the lane's own self-description counter, and (c) deletes the round-55 banner in place, which the
lane's own append-only auditor grades `unrestored`. Claim/counter correspondence for the frozen
C1/C2 targets holds on the measured bytes with three receipt-side gaps (F5–F7). Nothing here
falsifies C1 or C2; what fails is the reporting surface that is this seat's subject.

## Findings

### F1 — No round-56 `LOG.md` entry (blocking for this seat)

`README.md:16` declares `LOG.md` "append-only round log: the evidence that motivated each change";
`AGENTS.md:4` requires "Every change appends a LOG.md entry with the evidence that motivated it."
The freeze commit touched ten paths and none is `LOG.md`:

```
$ git show --stat --oneline HEAD
efc6b3ec round-56: freeze LD_AUDIT env leg and prereg roster controls
 .ufo/waves/round-56/controls/base-c1.out      |   3 +
 .ufo/waves/round-56/controls/base-c2.out      |   3 +
 .ufo/waves/round-56/preregistration.json      |  51 ++
 .ufo/waves/round-56/sources/ld.so.8.html      | 828 ++++
 .ufo/waves/round-56/sources/rtld-audit.7.html | 606 ++++
 corpus/SOURCES.md                             |   4 +
 tools/round56-env-leg-battery.py              |  55 ++
 tools/round56-env-leg-test.py                 |  36 +
 tools/round56-prereg-check.py                 |  75 ++
 tools/round56-replay-code-audit.py            | 973 ++++++++++
 10 files changed, 2634 insertions(+)

$ git log --oneline -1 -- LOG.md
c2c05e30 round-55 w1 integration: … LOG entry …

$ grep -c -i 'round 56\|round-56' LOG.md   →  0
$ git diff --stat HEAD -- LOG.md            →  (empty; worktree == HEAD)
```

The log's last content is the round-55 bullet, appended **inside** the `## Round 53` section
(`LOG.md:2435` is the last `##` heading; `LOG.md:2444` the last line, ending in a newline after
`… under \`.ufo/waves/round-55/\`.`). There is no `## Round 54` and no `## Round 55` heading, so
"append a round-56 entry" has no correct section to extend as the file stands.

**Fix (append-only):** append, after `LOG.md:2444`, a new `## Round 56 — LD_AUDIT env-name
classification and prereg/battery roster fidelity (2026-10-27)` section carrying the evidence the
freeze commit actually produced: base/freeze tips, C1 base miss → build detect → one-line mutant
miss, C2 base `met=False` exit 1 → freeze `met=True`, counter digests `fc3d4b63…`/`c7b0d787…`,
the S512/S513 gate decisions, and pointers to `.ufo/waves/round-56/{controls,measured}/`. Do not
retro-headline rounds 54/55; a forward heading is a legal append.

### F2 — No dated round-56 SCORECARD section; the banner's pointer is dangling (blocking)

Every prior round carries `## Round N` plus a measured-results subsection (last are
`SCORECARD.md:3057` `## Round 55`, `:3090` "What `met=True` does not show (round 55)"). Round 56
has neither:

```
$ grep -n '^## Round 56\|^### Round-56\|^### What .met=True. does not show (round 56)' SCORECARD.md
(no output)
$ grep -n '^## ' SCORECARD.md | tail -2
3057:## Round 55 — …
3105:### Planned (round 56)
$ grep -n 'Current authority (round' SCORECARD.md | head -2
6:**Current authority (round 56):** … Round 56 froze and measured C1 … (SCORECARD §Round 56) …
143:**Current authority (round 53):** …            ← archived head banners are only 42–51 (:2742-2766) and 53 (:143)
```

So `SCORECARD.md:6` cites `SCORECARD §Round 56`, which does not exist, and `### Planned (round 56)`
still carries round 55's plan text verbatim (`:3105-3119`, including "SCORECARD calibration
run-fact 40→41"). The lane's declared head counter agrees:

```
$ python3 tools/round42-selfdesc-reconcile.py --repo <lane> --tip HEAD           (rc=1)
tip=efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=55 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '41' (exit 0)
```

(the tree now holds 42 such files — `python3 -c "…"` → `42` — so the HEAD row's `41` is stale)

and at the worktree tip with the round-56 banner committed (scratch clone, commit `a1bfd0484…`,
"test: round-56 SCORECARD live edit as-is"):

```
r41=0 banner=1 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=55 met=False
detail: banner: head lacks 'Latest measured round: 55'
```

**Fix:** append `## Round 56 — …` with a claim table (C1/C2 rows as in `SCORECARD.md:3057-3074`),
`### What met=True does not show (round 56)`, and `### Round-56 measured results` naming
`.ufo/waves/round-56/measured/{build-c1,build-c2,m-drop-ldaudit}.out`; only then may the banner say
"Latest measured round: 56". Advance `### Planned (round 56)` → `### Planned (round 57)` (see F4
for its append-only handling).

### F3 — The round-56 banner deletes the round-55 banner in place; the lane's auditor grades it `unrestored` (blocking, append-only)

`SCORECARD.md:6` is the head banner; the append-only contract (`registry/append-only-contract.tsv`)
declares `SCORECARD.md` `A-corr` with region
`exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities@SCORECARD.md:6` — dated round
sections append-only, the five head sections re-derived in place. Banners are graded: the
SCORECARD's own round-48 note (`SCORECARD.md:2740`) records that rounds 46–47 rewrote the banner
without keeping the superseded text, that the audit flagged it, and that "from round 48 on, each
round appends the banner it replaces here".

The uncommitted edit (`W04LogScorecard/scorecard-worktree.diff`, `git diff --numstat` → `3 3` for
`SCORECARD.md`, nothing for `LOG.md`) replaces line 6 and two `## Axes` rows. The round-55 banner
text is gone from the worktree:

```
$ grep -c 'the C1 kill rule fired on its literal text' SCORECARD.md   →  0
```

Measured with the lane's own auditor, in a scratch clone of the lane at `efc6b3ec` with the
worktree `SCORECARD.md` copied in as a test commit (`a1bfd0484…`; the lane itself was not
committed to):

```
$ python3 tools/append-only-audit.py --repo <clone> --to a1bfd0484…
event a1bfd04846b7 SCORECARD.md deleted=3 graded=1 ungraded=2 permitted=0 restored_max=0 held_at_to=0 disclosed=0 status=unrestored …
summary commits=376 files=105 events=120 restored=69 partial=0 unrestored=4 ungraded=42 disclosed=5 …
(run exit 1; the lane at efc6b3ec has unrestored=3, see F4 — the edit is the +1)
```

**Fix (demonstrated):** re-append the superseded round-55 banner as its own line under
`## Historical head sections` (`SCORECARD.md:139`), next to the archived round-53 banner at `:143`.
With exactly that one line inserted and committed in the scratch clone (`8a66e38d3…`), the same
auditor reads:

```
event a1bfd04846b7 SCORECARD.md deleted=3 graded=1 ungraded=2 … restored_max=1 held_at_to=1 status=restored restored_by=8a66e38d3ed2
summary … unrestored=3 …   (back to the pre-edit baseline)
```

The line to append is byte-exact `git show efc6b3ec:SCORECARD.md | sed -n 6p` (939 bytes).

### F4 — Baseline append-only state at the freeze tip: `LOG.md` clean, `SCORECARD.md` already red by two events

```
$ python3 tools/append-only-audit.py --repo <lane> --to HEAD        (exit 1)
summary commits=375 files=105 events=119 restored=69 partial=0 unrestored=3 ungraded=42 disclosed=5
        permitted_lines=59 disclosed_lines=10 bad_disclosures=0 ungraded_lines=223
        regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0
```

`LOG.md`: 13 events, **all `restored`** — the log is still append-only clean. The three unrestored
events are:

| Event | File | Lost line (identified by re-hashing the commit's deleted lines) |
|---|---|---|
| `e81d90e64b04` (round-53 integration) | `SCORECARD.md` deleted=3 graded=1 | the round-52 authority banner (`sha256 5457296e…`); `grep -c 'Latest measured round: 52'` → 0 |
| `4bd7521a704e` (round-55 integration) | `SCORECARD.md` deleted=3 graded=1 | the literal line `### Planned (round 55)` (`sha256 c35b44ca…`); absent from the file (`grep -n '^### Planned' ` jumps `3050:…(round 54)` → `3105:…(round 56)`) |
| `c2c05e30b80e` (round-55 integration) | `corpus/lessons/round-55.md` deleted=33 graded=33 | 33 graded lines, no disclosure row |

This matters to round 56 twice: the round-56 banner edit repeats the `e81d90e6` failure mode (F3),
and the required `### Planned (round 56)` → `### Planned (round 57)` rename will repeat the
`4bd7521a` failure mode unless the superseded heading line is re-appended as well. Neither
pre-existing loss is round 56's; they are the reasons the gate reads `exit 1` both before and after
a correct round-56 append, so a round-56 integration that reports "audit exit 1" must say which
events are inherited.

### F5 — C2's freeze receipt does not record its exit status; the base receipt does (minor, correspondence)

```
$ cat .ufo/waves/round-56/controls/base-c2.out
tip=e10b6d39af450e8d652be9ac2986768b531fe13f
present=0 roster_match=0 kills=0 controls=0 met=False
exit=1
$ cat .ufo/waves/round-56/measured/build-c2.out
tip=efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
present=1 roster_match=1 kills=1 controls=2 met=True
```

The frozen target in `.ufo/waves/round-56/preregistration.json` says the freeze-tip check is
`exit 0`. `tools/round56-prereg-check.py:42-43` and `:66-68` write only
`tip/present/roster_match/kills/controls/met` into `--out`; the exit line in `base-c2.out` came
from an ad-hoc wrapper, so the two receipts of one claim were captured by different producers.
`return 0 if met else 1` (`:71`) makes exit 0 derivable from `met=True`, so this is an inference,
not a recorded outcome. (C1's receipts are consistent: the battery appends
`exit={returncode}` itself, `tools/round56-env-leg-battery.py:25-26`.)

**Fix:** have the checker append `exit=<rc>` to its own `--out` text (or record the wrapper
invocation in a `### Round-56 measured results` row) and re-emit `build-c2.out` with it.

### F6 — C1's "the battery's expected-detected assertion fails" is not produced by the frozen battery (minor, correspondence)

The frozen battery's roster (`tools/round56-env-leg-battery.py:15-21`) marks the mutant
`m-drop-ldaudit` as `{"designation": "kill", "expected": "missed"}` and `run()`
(`:22-31`) passes it `--expect missed`; `ok = returncode == 0 and fields["ld_audit"] == expected`.
A missing mutant therefore prints `pass` and the battery exits 0. The battery's own stdout, run by
seat X01ReplayC1 (`w1/out/X01ReplayC1/replay-battery-stdout.txt`, peer artifact, not my
execution):

```
base-old-counter: ld_audit=missed exit=0 -> pass
round56-counter: ld_audit=detected exit=0 -> pass
m-drop-ldaudit: ld_audit=missed exit=0 -> pass
battery_exit=0
```

The claim's clause is true only for a **separate** harness invocation that the frozen battery never
makes; wave seats made it: seat M01DropAudit leg A `--expect detected` →
`ld_audit=missed … exit=1` (`w1/out/M01DropAudit/battery-kill-graded-detected.out`, precedent in
`X04EnvNames/harness-mutant-expect-detected.out` → `exit=1`). The frozen kill rule
("falsified if … the single-line mutant still detects it") is satisfied by
`measured/m-drop-ldaudit.out`'s `ld_audit=missed`, but no lane receipt shows the battery asserting
the kill. There is also no battery-level receipt in the round-56 wave directory at all: `measured/`
holds only the four child receipts.

**Fix:** either reword the prereg target/lesson to "a mutant that still detected would fail the
battery's positive-control leg" (the actual mechanism), or add a graded-detect leg
(`--expect detected` on the mutant, expected `exit=1`) to the battery and save its stdout and exit
under `measured/`.

### F7 — The prereg's C1 `counter` cell names two files but carries one digest (minor, correspondence)

`.ufo/waves/round-56/preregistration.json` C1: `"counter": "tools/round56-env-leg-test.py +
tools/round56-replay-code-audit.py"`, `"counter_sha256": "fc3d4b63…"`. The digest matches only
`tools/round56-replay-code-audit.py` (verified). The harness that actually decides
`ld_audit=detected|missed` (`tools/round56-env-leg-test.py:24-27`:
`keys is not None and any("LD_AUDIT" in x for x in probs)`) and the battery that fixes the roster
(`round56-env-leg-battery.py`) have no frozen digest in the prereg (lane bytes `ec7a2519…`,
`79b19596…`). The C1 kill rule ("the measured counter sha256 differs from the frozen digest")
therefore binds one of the two named files. The wave's measured receipts come from the harness.

**Fix:** split the cell into `counter` + `counter_sha256` and `harness` + `harness_sha256`
(and, if the roster is to be frozen by hash, `battery_sha256`), or add the harness/battery digests
to `limits`.

## Claim/counter correspondence table (frozen targets vs receipts)

| Frozen element | Prereg / assignment | Receipt observed | Correspondence |
|---|---|---|---|
| C1 base (round-55 counter) | `ld_audit=missed`, exit 0 | `controls/base-c1.out`: `ld_audit=missed pid=1758490 problems=[]` / `exit=0`; `measured/base-c1.out` same, `pid=1759696`, `exit=0` | **match** |
| C1 build | `ld_audit=detected`, exit 0 | `measured/build-c1.out`: `ld_audit=detected pid=1759698 problems=['env: server environment carries LD_AUDIT']` / `exit=0` | **match** |
| C1 mutant | `ld_audit=missed`; kill rule = "mutant still detects" | `measured/m-drop-ldaudit.out`: `ld_audit=missed pid=1759704 problems=[]` / `exit=0` | **match on the rule**; the "expected-detected assertion fails" clause is not receipted by the battery (F6) |
| C1 counter digest | `fc3d4b63…` | `tools/round56-replay-code-audit.py` → `fc3d4b63…` | **match** |
| C1 base lineage | "the round-55 counter" | battery `OLD = tools/round54-replay-code-audit.py`; lane digest `c81fe971…` == round-55 prereg C1 `counter_sha256`; only difference from the new counter is `BAD_ENV` (line 146 vs 147, `LD_AUDIT` added) | **match** |
| C2 base | `present=0 roster_match=0 met=False`, exit 1 at `e10b6d39` | `controls/base-c2.out` exactly that + `exit=1`; `git cat-file -e e10b6d39:.ufo/waves/round-56/preregistration.json` and `…:tools/round56-env-leg-battery.py` both exit 128 ("exists on disk, but not in …") | **match** |
| C2 freeze | `present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0 at `efc6b3ec` | `measured/build-c2.out` exactly that; exit not recorded (F5) | **match**, exit by inference |
| C2 roster identity | prereg roster three entries vs battery `ROSTER` AST | prereg `{base-old-counter: control/missed, round56-counter: positive-control/detected, m-drop-ldaudit: kill/missed}`; battery `ROSTER` lines 15-21 identical; `met=True` is the checker's AST-equality result | **match** |
| C2 checker digest | `c7b0d787…` | `tools/round56-prereg-check.py` → `c7b0d787…` | **match** |
| Scores | operability `8 -> 8`, calibration `7 -> 7` | banner: "Scores remain operability 8 and calibration 7" | **match** |
| Axes calibration fact | worktree row: `… → 42` "(outside closures on record, including round 54 and 55)" | `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` → `42`; `corpus/lessons/round-54-verifier-spotcheck.md` and `round-55-verifier-spotcheck.md` exist | **match** |
| Axes depth fact | worktree row: "evidence re-anchored round 55" | `sha256sum SKILL.md` → `2d7c2212…`, `grep -c '^## '` → `43`, `wc -l` → `1612` (unchanged from HEAD row; attribution matches `ec030b36`) | **match** |
| Banner evidence pointer | "… (SCORECARD §Round 56)" | no `## Round 56` heading; selfdesc `banner=1` at the edited tip | **mismatch** (F2) |
| Banner "measured" | "froze and measured C1 … and C2 …" | `.ufo/waves/round-56/measured/` is untracked (`git status --porcelain` → `?? .ufo/waves/round-56/measured/`); the prereg names that directory as `receipt_dir` | **holds on disk, uncommitted** |

## Gates / commands run (all read-only on the lane)

| # | Command | Outcome |
|---|---|---|
| 1 | `git show --stat --oneline HEAD`; `git log --oneline -1 -- LOG.md`; `git log --oneline -4 -- SCORECARD.md` | freeze commit has no `LOG.md`; last LOG commit `c2c05e30` (round 55) |
| 2 | `grep -c -i 'round 56\|round-56' LOG.md`; `grep -n 'Current authority (round' SCORECARD.md`; `grep -n '^## ' SCORECARD.md \| tail -25` | 0 LOG refs; banner 56 at `:6` (only archived: 45–51, 53 at `:2742-2766`, `:143`); no `## Round 56` |
| 3 | `sha256sum` over the eight audited bytes | see table above / `SHA256SUMS.txt` |
| 4 | `python3 tools/append-only-audit.py --repo <lane> --to HEAD` and `--json` | `unrestored=3`, `events=119`, `LOG.md` 13/13 restored, exit 1 (F4) |
| 5 | `python3 tools/round42-selfdesc-reconcile.py --repo <lane> --tip HEAD` | `r41=1 banner=0 … maxN=55 met=False`, exit 1 (F2) |
| 6 | scratch clone of the lane at `efc6b3ec`; copy worktree `SCORECARD.md`; commit `a1bfd0484…`; `append-only-audit --to <commit>` | new event `deleted=3 graded=1 ungraded=2 status=unrestored`, `unrestored` 3→4, exit 1 (F3) |
| 7 | same clone; `round42-selfdesc-reconcile --tip <commit>` | `r41=0 banner=1 … maxN=55 met=False`, detail `head lacks 'Latest measured round: 55'` (F2) |
| 8 | same clone; insert `git show efc6b3ec:SCORECARD.md \| sed -n 6p` after `## Historical head sections`; commit `8a66e38d3…`; audit `--to` it | event becomes `restored`, `unrestored=3` (pre-edit baseline), exit 1 (F3 repair) |
| 9 | `cat` of all six round-56 receipts; `grep -n` of the three tools' output/exit lines | F5, F6, F7 |

Lane integrity: no commit, `git add`, or `jj` command was run in `/home/vgpnk/Projects/shokunin/kama-shokunin`;
the pre-existing uncommitted `SCORECARD.md` edit (mtime 13:07) and the pre-existing round-55
untracked outputs were read, not authored or modified. Clone commits exist only in
`/fast/scratch/hyaku/kama-r56/W04LogScorecard/clone` and were removed with the scratch directory.
`TMPDIR` was set explicitly for every scratch run. No tool installs, no `/tmp` use.

## Out of scope

- Whether C1/C2 capability claims are true, admitted, or correctly scored (other seats; this seat
  reports only the LOG/SCORECARD surfaces and the receipt correspondence).
- The pre-existing unrestored events themselves (`e81d90e6`, `4bd7521a`, `c2c05e30` round-55
  lesson) — reported as baseline, not repaired; `corpus/lessons/round-55.md` line restoration is
  the round-55/round-56 lesson owner's scope.
- Other seats' findings and the wave's settlement; peer receipts are cited with attribution only.
- Fleet-root `LOG.md` / `SCORECARD.md` (read-only; both contain zero round-56 references) and the
  round-55 untracked outputs in the lane.

## Proposed repairs, in order

1. Append a `## Round 56` LOG section after `LOG.md:2444` (F1).
2. Append `## Round 56`, `### What met=True does not show (round 56)` and
   `### Round-56 measured results` to `SCORECARD.md`; then the banner's `Latest measured round: 56`
   and `SCORECARD §Round 56` become true (F2).
3. In the same SCORECARD edit, re-append the byte-exact round-55 banner under
   `## Historical head sections` (F3), and re-append `### Planned (round 56)` when renaming it to
   round 57 (F4).
4. Make `round56-prereg-check.py --out` record `exit=<rc>` and re-emit `build-c2.out` (F5).
5. Add the graded-detect leg (or reword the target) and save the battery's stdout/exit under
   `measured/` (F6); split `counter`/`harness` digests in the prereg (F7).

## Artifact paths (this seat)

- `.ufo/waves/round-56/w1/out/W04LogScorecard.md` — this report
- `.ufo/waves/round-56/w1/out/W04LogScorecard/append-only-audit-head.txt` (lane, `--to HEAD`, exit 1)
- `.ufo/waves/round-56/w1/out/W04LogScorecard/append-only-audit-head.json` and `…-json.txt` (same run, `--json`)
- `.ufo/waves/round-56/w1/out/W04LogScorecard/append-only-audit-round56-edit-asis.txt` (scratch commit `a1bfd0484…`, exit 1)
- `.ufo/waves/round-56/w1/out/W04LogScorecard/append-only-audit-round56-edit-banner-reappended.txt` (scratch commit `8a66e38d3…`, exit 1)
- `.ufo/waves/round-56/w1/out/W04LogScorecard/selfdesc-head-efc6b3ec.txt` (exit 1)
- `.ufo/waves/round-56/w1/out/W04LogScorecard/selfdesc-round56-edit-asis.txt` (exit 1)
- `.ufo/waves/round-56/w1/out/W04LogScorecard/scorecard-worktree.diff` (`git diff HEAD -- SCORECARD.md`)
- `.ufo/waves/round-56/w1/out/W04LogScorecard/clone-A-vs-freeze.diff` (scratch: worktree SCORECARD vs `efc6b3ec`)
- `.ufo/waves/round-56/w1/out/W04LogScorecard/SHA256SUMS.txt`
