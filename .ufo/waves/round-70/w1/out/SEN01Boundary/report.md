# SEN01Boundary — report (round 70, w1)

Seat: boundary audit of the round's intended edits, read-only. Deliverables:
`boundary.md` (findings) and this file; the trailer copy is
`.ufo/waves/round-70/w1/out/SEN01Boundary.md`. No tracked lane file was edited, created or
deleted; no git/jj mutation was run on the lane; no tool was installed or upgraded (nothing
needed). All writes are under
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-70/w1/out/SEN01Boundary/` and
`/fast/scratch/hyaku/kama-r70/SEN01Boundary/` (scratch deleted before yield).

## Environment and tips

```
$ cd /home/vgpnk/Projects/shokunin/kama-shokunin && git rev-parse HEAD
0e14facd0c619f45a6461821d2bd80ddac9855b1
$ git log --oneline -2
0e14facd round-70: frozen claims C1/C2 before data, the refused-member control (base bytes fail-open), and the wave-1 spec/dispatch
6035e952 round-69 verifier spot-check (integrator, hyaku): non-author admit/reject
$ git diff --stat 6035e952..HEAD -- tools/
(no output; tools are byte-identical at base and tip, so every selftest below runs the base-tip bytes)
$ git status --porcelain      # at first read
?? .ufo/waves/round-70/w1.ready
?? .ufo/waves/round-70/w1.ready.dispatched
?? .ufo/waves/round-70/w1/out/
```

The landing was live while I audited. Two SCORECARD snapshots were tested:

```
SCORECARD.md  md5 53990e14ebd32ec676e18ee3225710ac   (first snapshot, diff 6+/4-)
SCORECARD.md  md5 664badf320ae56760099c27e0aab534f   (second snapshot, diff 26+/6-)
PROVINCE.md   md5 248e7de5b074550d04c53e9b0fe0902a   (dirty, 1+/1-)
```

## 1. The four guard selftests (base-tip bytes), cwd = lane root

```
$ python3 tools/append-only-audit.py --selftest
... 51 pass lines ...
AOA_SELFTEST pass=51 fail=0
EXIT=0
$ python3 tools/sources-append-only.py --selftest
... 46 ok lines ...
46/46 selftest cases passed
EXIT=0
$ python3 tools/round67-worktree-landing-check.py --selftest
PASS clean-control ... PASS nested-path-clean ...
WLC_SELFTEST pass=6 fail=0
EXIT=0
$ python3 tools/round68-receipt-pointer-audit.py --selftest
ok: clean control resolves ... ok: non-measured backticks are not citations
9/9 selftest arms passed
EXIT=0
```

## 2. Live guard verdicts at the base tip

```
$ python3 tools/append-only-audit.py --to 6035e952 > /fast/scratch/.../aoa-6035e952.out 2>&1
EXIT=1
summary commits=504 files=133 events=180 restored=86 partial=0 unrestored=28 ungraded=61 disclosed=5 permitted_lines=627 disclosed_lines=10 bad_disclosures=0 ungraded_lines=270 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=5

$ python3 tools/append-only-audit.py --to HEAD > /fast/scratch/.../aoa-HEAD.out 2>&1
EXIT=1
summary commits=505 files=133 events=180 restored=86 partial=0 unrestored=28 ungraded=61 disclosed=5 permitted_lines=627 disclosed_lines=10 bad_disclosures=0 ungraded_lines=270 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=5
```

The five unbound declarations printed by both runs (exact lines):

```
declaration SCORECARD.md <- corpus/README.md:761 unbound: declared_at corpus/README.md:761 does not say append-only for SCORECARD.md
declaration corpus/QUALITY.md <- corpus/README.md:761 unbound: ...
declaration corpus/README.md <- corpus/README.md:761 unbound: ...
declaration corpus/SOURCES.md <- SKILL.md:578 unbound: ...
declaration corpus/lessons/*.md <- corpus/README.md:1239 unbound: ...
```

Drift localisation (script over `git log --reverse 380bcdff..HEAD -- <path>` checking whether
the cited line still says append-only):

```
corpus/README.md:761  last_good=c2c05e30b80e first_bad=750e76b9363b  now="  context-capacity rows' scope already excludes."
corpus/README.md:1239 last_good=c2c05e30b80e first_bad=750e76b9363b  now='- Carried over unchanged and not re-measured here: the b11906 ledger p'
SKILL.md:578         last_good=c2c05e30b80e first_bad=dc48ee2e9f45  now='of any real deployment.'
```

Candidate re-anchors tested with the tool's own `binds()` (imported by path):

```
SCORECARD.md       via README:768 -> True
corpus/QUALITY.md  via README:768 -> True
corpus/README.md   via README:768 -> True
corpus/SOURCES.md  via README:768 -> True
corpus/lessons/*.md via README:1246 -> True
corpus/SOURCES.md  via SKILL:578 -> False
corpus/SOURCES.md  via SKILL:607 -> True
```

Base-clone live runs (own fixture clone; toplevel asserted = the clone):

```
$ git clone --shared -q <lane> /fast/scratch/.../baseclone && git -C <clone> checkout -q 6035e952
$ git -C <clone> rev-parse --show-toplevel
/fast/scratch/hyaku/kama-r70/SEN01Boundary/baseclone
$ cd <clone> && python3 tools/round67-worktree-landing-check.py --paths SCORECARD.md,LOG.md,PROVINCE.md,SKILL.md,corpus/SOURCES.md
clean SCORECARD.md / clean LOG.md / clean PROVINCE.md / clean SKILL.md / clean corpus/SOURCES.md
WORKTREE_LANDING_CHECK paths=5 clean=5 dirty=0 missing=0 untracked=0 unreadable=0
EXIT=0
$ python3 tools/round68-receipt-pointer-audit.py --repo <clone> --rev 6035e952
RECEIPT_POINTER_AUDIT files=2 cited=134 resolved=117 expanded=4 corrected=13 unresolved=0
EXIT=0
$ cd <lane> && python3 tools/sources-append-only.py --from 6035e952^ --to 6035e952
no append-only violations
EXIT=0
$ python3 tools/gate-registry-check.py --selftest
PASS lane-tip ... GATE_SELFTEST pass=7 fail=0
EXIT=0
$ python3 tools/gate-registry-check.py
registered 79 unregistered 0 defective 0
EXIT=0
$ python3 tools/round42-selfdesc-reconcile.py --repo <lane> --tip 6035e952
tip=6035e952c2521999e192d6f236331f265ac98392
r41=2 banner=1 planned=1 retired=1 saturation=0 caps=0 receipts=0 readme=0 province=4 rel=0 closure_ptr=0 mismatches=10 maxN=69 met=False
detail: r41 operability run `python3 tools/gate-registry-check.py --selftest` no stdout line == 'GATE_SELFTEST pass=7 fail=0' (exit 1)
detail: r41 calibration run `python3 tools/round69-newest-closure-counter.py --since-round 63` no stdout line == 'NEWEST_CLOSURE … row_current=true' (exit 2)
detail: banner: head lacks 'Latest measured round: 69'
detail: planned: section does not name '### Planned (round 70)'
detail: retired: does not state '15 capabilities'
detail: province: PROVINCE.md lacks tools/round67-worktree-landing-check.py (capability worktree-landing-check)
detail: province: PROVINCE.md lacks tools/round68-receipt-pointer-audit.py (capability receipt-pointer-audit)
detail: province: PROVINCE.md lacks registry/receipt-pointer-resolutions.tsv (capability receipt-pointer-audit)
detail: province: PROVINCE.md lacks tools/round69-newest-closure-counter.py (capability newest-closure-counter)
detail: closure_ptr: calibration row latest outside closure is round-68; newest at tip is round-69
EXIT=1
```

This reproduces the frozen BEFORE exactly (`mismatches=10`, exit 1).

Worktree-landing check on the live lane at 20:56Z (mid-landing; informational):

```
$ cd <lane> && python3 tools/round67-worktree-landing-check.py --paths SCORECARD.md,LOG.md,PROVINCE.md,corpus/SOURCES.md
DIRTY SCORECARD.md
clean LOG.md
DIRTY PROVINCE.md
clean corpus/SOURCES.md
WORKTREE_LANDING_CHECK paths=4 clean=2 dirty=2 missing=0 untracked=0 unreadable=0
EXIT=1
```

## 3. Fixture matrix (own clones, `git clone --shared`, fixture identity, toplevel asserted)

Each case is a clone of the lane at `0e14facd` plus one commit; the audit was run at that
commit with `--json`. Baseline = the HEAD JSON (`aoa-head.json`, `events=180
unrestored=28`).

| case | edit | new audit event(s) | SOURCES / receipt guard |
|---|---|---|---|
| A | SCORECARD snapshot `53990e14…` | `SCORECARD.md del=5 graded=1 ungraded=4 restored_max=1 status=restored` | — |
| A2 | SCORECARD snapshot `664badf3…` (current) | `SCORECARD.md del=5 graded=1 ungraded=4 restored_max=1 status=restored`; summary `events=181 restored=87 unrestored=28` | receipt audit exit 0, `cited=135 resolved=118 expanded=4 corrected=13 unresolved=0` |
| B | A2 minus the appended old-banner copy | `del=5 graded=1 ungraded=4 restored_max=0 status=unrestored` (28→29) | — |
| B+disc | B + valid 6-field disclosure row | `bad_disclosures=1` (`names a commit at or after the ledger's introduction b6bed925b032: restore by append`); event stays `unrestored` | — |
| C | delete 4 `\| **` rows under `## Axes` | `del=4 graded=4 ungraded=0 status=unrestored` | — |
| D | rewrite one §Round 69 line | `del=1 graded=1 status=unrestored` | — |
| E | append §Round 70 + LOG + lesson + SOURCES row at EOF | no new event | sources exit **2**: `HEAD:corpus/SOURCES.md:644: row-like line outside the parsed registry table` |
| E2 | same, row inserted after S541 inside `## Registry` | no new event | `added S542 (allowed)`, `no append-only violations`, exit 0 |
| F | S541 `teaches` changed | — | exit 1: `VIOLATION S541: cell \`teaches\` changed in place` |
| G | S541 `status` changed | — | exit 0: `no append-only violations` |
| H | S541 row removed | — | exit 1: `VIOLATION S541: row removed` |
| J3 | §Round 70 citing a missing `measured/...` | — | receipt audit exit 1: `UNRESOLVED file=SCORECARD.md line=3697 round=70 cited=\`measured/before/absent-receipt.out\` target=.ufo/waves/round-70/measured/before/absent-receipt.out` |
| K | rewrite one `corpus/lessons/round-69.md` line | `del=1 graded=1 status=unrestored` (28→29) | — |
| L | rewrite one `LOG.md` line | `del=1 graded=1 status=unrestored` (28→29) | — |

The append-only audit exit was **1 in every case** (it is 1 at baseline), so the exit cannot
distinguish a clean landing from a violating one; the event list and the `unrestored` count
are the discriminating signal.

## 4. Receipt-pointer ledger cwd hazard

```
$ cd <caseJ3 clone> && python3 tools/round68-receipt-pointer-audit.py --repo <clone> --rev HEAD
RECEIPT_POINTER_AUDIT files=2 cited=136 resolved=118 expanded=4 corrected=13 unresolved=1
EXIT=1
$ cd /fast/scratch/... && python3 <clone>/tools/round68-receipt-pointer-audit.py --repo <clone> --rev HEAD
RECEIPT_POINTER_AUDIT files=2 cited=136 resolved=118 expanded=4 corrected=0 unresolved=14
EXIT=1
```

`--ledger` defaults to the cwd-relative `registry/receipt-pointer-resolutions.tsv` (line 457)
and `_read_ledger` returns `[]` when the file does not exist (lines 133-135), although the
docstring says an unreadable ledger is exit 2. Same rev, same tool: 13 corrections applied
from the lane cwd, 0 from anywhere else. Landing commands must `cd` into the lane or pass
`--ledger`.

## 5. Credential / operator-owned scan

```
$ { git diff -U0 SCORECARD.md PROVINCE.md; cat .ufo/waves/round-70/measured/**/*.out .ufo/waves/round-70/controls/*.py; } \
    | grep -cEi 'sk-[a-z0-9]{10}|ghp_[a-z0-9]{10}|github_pat_|BEGIN [A-Z ]*PRIVATE KEY|aws_secret|api[_-]?key *=|password *=|Bearer [A-Za-z0-9._-]{10}'
0
```

No credential material in the intended edits. The one operator-owned surface the round makes
live is the reconciler's `run_fact` (`tools/round41-scorecard-reconcile.py:131-139`):
`subprocess.run(["bash","-c",cmd], cwd=<temp git-archive export>, timeout=300)` with the full
inherited environment, executing commands parsed from SCORECARD evidence cells. No shell
execution in the census (`subprocess.run(argv)`, `cwd=LANE`, per-member temp dir,
`shutil.rmtree(..., ignore_errors=True)` in `finally`).

## 6. What I could NOT verify

- A *later* edit than the landed bytes: the L1 landed `7be07423` + `73597158` while I wrote,
  and I re-measured those exact bytes (§8). Any further edit must be re-tested with case
  A2's method; the pending uncommitted `corpus/SOURCES.md` `used-by` edit is measured but not
  yet in a commit.
- The full 22-member census and the reconciler at the *pre-landing* tip (C1/C2 seats own
  those); I ran the census at the landed tip (§8) and the reconciler at base only to
  corroborate the frozen BEFORE.
- A disclosure-ledger row for a post-introduction commit: tested and **rejected** by design
  (`restore by append`), so no legal disclosure path exists for a round-70 deletion.

## 7. Deliverables and exact paths

- `…/w1/out/SEN01Boundary/boundary.md` — findings (§1-§7).
- `…/w1/out/SEN01Boundary/report.md` — this evidence log.
- `…/w1/out/SEN01Boundary.md` — trailer report (self-contained summary).
- Scratch `/fast/scratch/hyaku/kama-r70/SEN01Boundary/` — deleted before yield.

## 8. Post-landing re-measurement (the record landed while I wrote)

The L1 landed `7be07423` ("round-70 C1+C2: …", 15 files, +899/−35, including both tools and
the record) and `73597158` (measured receipts). Re-measured at those bytes, cwd = lane root:

```
$ git log --oneline 0e14facd..HEAD
73597158 round-70 measured: reconciler 0 mismatches at 7be07423, five-arm selftest green, census pass=22 fail=0 not_evaluated=0, newest-closure row_current=true, receipt-pointer audit intermediate red preserved
7be07423 round-70 C1+C2: self-description reconciles at the tip (run facts execute against a tip checkout; record drift repaired) and the census verdict is fail-closed on not-evaluated members

$ python3 tools/append-only-audit.py --to 7be07423
EXIT=1
summary commits=506 files=133 events=181 restored=87 partial=0 unrestored=28 ungraded=61 disclosed=5 permitted_lines=627 disclosed_lines=10 bad_disclosures=0 ungraded_lines=274 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=5
# the only new event vs base:
#   7be07423 SCORECARD.md del=5 graded=1 ungraded=4 restored_max=1 status=restored

$ python3 tools/append-only-audit.py --to 73597158 --json
EXIT=1
summary: events=181 restored=87 unrestored=28 ungraded=61 disclosed=5 regressed=0 bad_declarations=5

$ python3 tools/round68-receipt-pointer-audit.py --repo . --rev 73597158
RECEIPT_POINTER_AUDIT files=2 cited=141 resolved=124 expanded=4 corrected=13 unresolved=0
EXIT=0

$ python3 tools/sources-append-only.py --from 0e14facd --to 73597158
no append-only violations
EXIT=0

$ python3 tools/round67-worktree-landing-check.py --paths SCORECARD.md,LOG.md,PROVINCE.md,SKILL.md,corpus/SOURCES.md
clean SCORECARD.md
clean LOG.md
clean PROVINCE.md
clean SKILL.md
DIRTY corpus/SOURCES.md
WORKTREE_LANDING_CHECK paths=5 clean=4 dirty=1 missing=0 untracked=0 unreadable=0
EXIT=1

$ python3 .ufo/waves/round-70/controls/refused-member-control.py tools/round65-host-census.py
REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0
EXIT=0

$ timeout 280 python3 tools/round65-host-census.py
HOST_CENSUS pass=22 fail=0 not_evaluated=0 waived=0 total=22 tierA_fail=0 tierB_fail=0
EXIT=0
```

The pending `corpus/SOURCES.md` worktree edit changes only S052's `used-by` cell
(`… round-18.md` → `… round-18.md, corpus/lessons/round-70.md`). Exact-byte fixture test of
that edit:

```
$ cp <lane>/corpus/SOURCES.md <clone>/corpus/SOURCES.md
$ git -C <clone> -c user.name=boundary -c user.email=b@invalid -c commit.gpgsign=false commit -qam "pending S052 used-by edit"
$ python3 <clone>/tools/sources-append-only.py --repo <clone> --from HEAD^ --to HEAD
no append-only violations
EXIT=0
```

It was permitted (exit 0) and then landed in `910e6747`; at the final tip the audit records it as `910e6747 corpus/SOURCES.md del=1 graded=0 ungraded=0 status=ungraded` (a permitted line), and the WLC is clean.

Landed tool boundary notes: the census exits `0` only when `fail == 0` and every
not-evaluated member is explicitly `--waive`d (exact name, warns on unknown/unused, never
covers a fail); the frozen counter does not exercise `--waive`, so keep the registered
command waiver-free. The reconciler now runs fact commands in a `git clone --shared`
checkout of the tip (alternates to the lane object store), deletes it at exit, and still
inherits the full environment — keep fact commands read-only.


### Final tip `a8df1af5` (the record tip `af6eb6c2` plus additive wave evidence)

```
$ git log --oneline -2
a8df1af5 round-70 wave evidence: 13 seat outputs (executors, scribes, scouts, reviewers, critic, mutation-tester, sentinel, connector), the critic's boundary control and the probe reports; final audit receipts at 2fc9ce1e
2fc9ce1e round-70 appended: final measured tip af6eb6c2 (reconciler 0, selftest 5/5, census 22/0/0 literal), wave attack dispositions, LOG wave-integration bullets

$ python3 tools/append-only-audit.py --to a8df1af5
EXIT=1
summary commits=511 files=133 events=183 restored=87 partial=0 unrestored=28 ungraded=63 disclosed=5 permitted_lines=628 disclosed_lines=10 bad_disclosures=0 ungraded_lines=276 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=5
# 2fc9ce1e and a8df1af5 add no audit event (pure additions); unrestored stays 28.

$ python3 tools/round68-receipt-pointer-audit.py --repo . --rev a8df1af5
RECEIPT_POINTER_AUDIT files=2 cited=157 resolved=140 expanded=4 corrected=13 unresolved=0
EXIT=0

$ python3 tools/sources-append-only.py --from 0e14facd --to a8df1af5
no append-only violations
EXIT=0

$ python3 tools/round67-worktree-landing-check.py --paths SCORECARD.md,LOG.md,PROVINCE.md,SKILL.md,corpus/SOURCES.md
WORKTREE_LANDING_CHECK paths=5 clean=5 dirty=0 missing=0 untracked=0 unreadable=0
EXIT=0

$ timeout 280 python3 tools/round65-host-census.py
HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22 tierA_fail=0 tierB_fail=0
EXIT=0
```

Final boundary verdict: every record event the round added is `restored` or `ungraded`; no
new unrestored event landed; receipt-pointer, sources, WLC and census are green at the final
tip. The append-only audit remains exit 1 for the pre-existing `unrestored=28` +
`bad_declarations=5` only.
