# ExecHistoricalGate — HistoricalNoHarm rerun, committed auditor @ 245a37f6 (round-23 FALSIFY wave 2)

## Verdict: HOLDS (no falsification)

The HistoricalNoHarm gate rerun against the **committed** auditor at
`245a37f69628c2c6bb29bbf17897d8fb5946c857` vs frozen (`4fe9339f` blob) is
byte-identical on stdout, stderr and exit status for all three invocations
(ledger, `--no-errata`, `--selftest`), both within-run (current vs frozen) and
against the build wave's committed baseline artifacts. `no-harm-gate=PASS`,
harness exit 0.

## Arms

| arm | source | blob | sha256 |
|---|---|---|---|
| frozen | `git show 4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py` | `fcc255ce5115a749dfbd09cf992ba9851a2dc90a` | `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f` |
| current (this rerun) | committed `245a37f6:tools/report-landing-audit.py` | `f10d811eafcc5bc853abdf75c4a05ec2374cd579` | `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7` |

Blob evidence (commands in my clone, HEAD verified `245a37f6…`):
`git rev-parse HEAD` → `245a37f6…`; `git hash-object tools/report-landing-audit.py`
→ `f10d811e…` (worktree = committed, clean clone); `git rev-parse 4fe9339f:tools/report-landing-audit.py`
→ `fcc255ce…`. Frozen sha256 matches the committed baseline `pins.txt`
(`.ufo/waves/round-23/build/out/HistoricalNoHarm/pins.txt:5`).

**Noteworthy:** the committed baseline `pins.txt:4` records the build wave's
current arm as `current_worktree_blob=d577c5aa…` / `current_sha256=d0a96599…` —
a pre-commit working snapshot, *not* the committed `f10d811e…`. The committed
auditor differs from that snapshot, and this rerun exercised the exact
committed bytes. [INFERENCE] This is the first gate run with the committed
`f10d811e` bytes as the current arm. Between the arms the auditor changed 119
insertions / 38 deletions (`git diff --stat 4fe9339f 245a37f6 -- tools/report-landing-audit.py`).

## Command

```
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r23w2/ExecHistoricalGate   # HEAD verified 245a37f6…
env KAMA_LANE_REPO=/tmp/kama-r23w2/ExecHistoricalGate KAMA_FLEET_REPO=/home/vgpnk/Projects/shokunin \
  bash /tmp/kama-r23w2/ExecHistoricalGate/out-rerun/run-historical.sh
# → observed exit: gate-exit=0
```

`KAMA_LANE_REPO` points at my clone so the current arm is exactly the committed
`245a37f6` bytes (hermetic vs lane working-tree drift); audited rounds 10–22
history is the same object set as the lane repo. Fleet repo used read-only.

## Evidence

### 1. Within-run current-vs-frozen byte-identity (harness criterion, run-historical.sh:73-80)
- `history.vs-diff` = 0 bytes; `no-errata.vs-diff` = 0 bytes; `selftest.vs-diff` = 0 bytes
  (diff -u of frozen vs current stdout+stderr per variant).
- Exits: history frozen=0 current=0; no-errata frozen=1 current=1; selftest frozen=0 current=0.
- All six `.err` files = 0 bytes. Harness `gate-stderr.txt` = 0 bytes.
- Final line: `no-harm-gate=PASS` (`gate-stdout.txt`).

### 2. Rerun vs build-wave committed baseline (all 12 out/err files, `cmp -s`)
`frozen-history.{out,err}`, `current-history.{out,err}`,
`frozen-no-errata.{out,err}`, `current-no-errata.{out,err}`,
`frozen-selftest.{out,err}`, `current-selftest.{out,err}` — **all IDENTICAL**
to `.ufo/waves/round-23/build/out/HistoricalNoHarm/*`. All exit files match
baseline (0,1,0 on both arms both runs). Despite the current arm differing
(`d577c5aa` snapshot vs committed `f10d811e`), `current-*.out` is
byte-identical to the baseline's `current-*.out`.

### 3. Semantic checks (rerun baseline-counts.txt, byte-identical to committed baseline-counts.txt)
- ledger: `exit=0 status=clean rounds=10-22 reports=13 defects=9 corrected=9
  uncorrected=0 required=54 post_report=5 errata_rows=9 errata_unmatched=0
  errata_invalid=0` — matches declared 9 corrected defects, exit 0.
- `--no-errata`: `exit=1 status=failed defects=9 uncorrected=9 errata_rows=0` — matches declared exit 1 / 9 defects.
- selftest: `exit=0 selftest cases=50 failed=0` — matches declared 50/50.
- Per-round table (rounds 10–22, incl. round 18×3, round 20×5 corrected defects)
  identical line-for-line to the committed baseline.

### 4. Rerun pins (`out/ExecHistoricalGate/pins.txt`)
`lane_master=245a37f6… lane_base=4fe9339f… fleet_head=f06d3855…
frozen_blob=fcc255ce… current_worktree_blob=f10d811e… rounds=10-22`

Observation: fleet HEAD moved twice during this session (`7f48c5ed…` at build
time → `7235b8dd…` at clone time → `f06d3855…` at gate pins) and lane master
moved `4fe9339f…` → `245a37f6…`, yet all six outputs stayed byte-identical —
the rounds 10–22 ledger depends on neither HEAD state (read-only log/show over
fixed history).

## Not verified
- Fault grid (`tests/report-audit/repo-state-grid.py`), isolation mutants, and
  the open attacks (alternates, gitfile redirect, ambiguity overwrite, second
  Landed section, errata CR, sibling tools) — sibling seats' scope, not rerun here.
- Only the harness's three invocation forms over rounds 10–22; no other
  `--rounds` values or flags.
- Identity established by content `cmp`/`diff` of captured outputs; I did not
  independently re-hash stream captures beyond the harness's `.sha256` files.
- Python 3.14.8 / git 2.56.0 already present; **no installs performed**.

## Files written
- `.ufo/waves/round-23/falsify/advice/ExecHistoricalGate.md` (this report)
- `.ufo/waves/round-23/falsify/out/ExecHistoricalGate/` — 19 retained evidence files:
  `pins.txt`, `baseline-counts.txt`, `gate-stdout.txt`, `gate-stderr.txt`,
  `{history,no-errata,selftest}.vs-diff`, 6× `*.exit`, 6× `*.sha256`
- Workspace only (not lane): `/tmp/kama-r23w2/ExecHistoricalGate/` (clone) and
  `…/out-rerun/` (raw rerun artifacts)
