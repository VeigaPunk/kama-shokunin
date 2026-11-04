# EX04GateArm7 — C wiring: pre-report gate arm 7 `round74-v2` (patch `arm7.patch`)

Seat: EX04GateArm7, kama r74 w1, leaf (no subagents, no broadcast). Lane
`/home/vgpnk/Projects/shokunin/kama-shokunin`. `tools/pre-report-gate.py` is byte-frozen
for every seat including this one, so the lane file was **not** edited: the amendment
lives in the unified-diff patch
`.ufo/waves/round-74/w1/EX04GateArm7/arm7.patch`, which the L1 applies at integration
(recipe in §4). No freeze disagreement: the patch implements the round-74 wiring note
verbatim — arm 7 composes the three v2 counters, each absent → the arm fails closed
naming the absent module, and the verdict becomes
`PRE_REPORT round=<N> arms=7 failed=<f> uncommitted=<u>`
(`plans/round-74-claims.md:57-58`, repeated in each of C1/C2/C3's wiring bullets).

Evidence base: patch context matches the committed gate bytes at
`git rev-parse master` = `b0b903a0854365fbf4d1ba4d18ae9a66052cce4f`
(gate sha256 `59842d4604a2d0b85db428b7b79a6758ca0dd1ffdbdc651a31a53bfbd94893e9`, verified
unchanged in the lane after all runs below). All runs executed in a scratch clone
(`git clone --shared`, HEAD `b0b903a0`) with `TMPDIR` under the scratch root.

## 1. What the patch changes — `tools/pre-report-gate.py` only (+194/−34 → 842 lines)

| element | before | after |
|---|---|---|
| `ARM_ORDER` | `[names from ARM_SPECS] + ["round-clean"]` (6 arms) | `+ ["round-clean", "round74-v2"]` (7 arms); arms 1–6 keep their exact names, order and instruments |
| `ROUND74_V2_MODULES` | — | new constant: `(canon, round74-selfdesc-canon.py, --repo {repo})`, `(claim-v2, round74-receipt-claim-binding.py, --repo {repo} --round {round} --tip {tip})`, `(drift-v2, round74-province-host-drift.py, --repo {repo})` |
| `evaluate()` | 5 spec arms + built-in `round-clean` | appends arm 7 after `round-clean`: resolves each module from the tools dir (`--tools-dir` aware) exactly like `ARM_SPECS`; absent script → `missing <script>` detail record + arm exit 1; non-zero exit → arm fails with that code; arm detail = the three counters' `_detail` lines joined ` \| ` (per-counter verdict line + first `*_V2_FINDING`, same convention as arms 4/5) | 
| `VERDICT_RE` | 5 keys | + `round74-v2-canon` → `SELFDESC_CANON_V2 `, `round74-v2-claim-v2` → `RECEIPT_CLAIM_V2 `, `round74-v2-drift-v2` → `PROVINCE_HOST_DRIFT_V2 ` (trailing space keeps `*_FINDING` lines from matching, same trick as `ROUND_SCOPE_V2 `) |
| `_detail()` | defects = DIRTY/MISSING/… + `ROUND_SCOPE_V2_FINDING` | also matches `V2_FINDING_RE` (`SELFDESC_CANON_V2\|RECEIPT_CLAIM_V2\|PROVINCE_HOST_DRIFT_V2)_FINDING `; `_DEFECT_ARMS` gains the three arm-7 counter keys so a failure names the counter that broke |
| `PREDICATE` | `arms=6`, five instruments | `arms=7`, five instruments plus the three round-74 v2 counters arm 7 composes (amended per the plan's wiring note, same sentence shape as the r72 precedent) |
| verdict/docstring | `arms=6` everywhere | `arms=7`; arms list gains line 7; new `round74-v2` paragraph (composition, fail-closed absence, never vacuous green); round-71 `arms=5` / round-72-73 `arms=6` receipts kept readable as historical records; receipts line gains the r74 entry; `main()` description and `--tools-dir` help updated |
| selftest | stubs for arms 1–5; checks (a)–(l), `pass=12` | + `_STUB_CANON` / `_STUB_CLAIM_V2` / `_STUB_DRIFT_V2` honouring `red-arms.txt` (keys `round74-canon` / `round74-claim-v2` / `round74-drift-v2`), written into the fixture tools dir; checks (m) red canon stub, (n) green trio, (o) deleted drift-v2 stub → `pass=15` |

The selftest stays stub-only for arm 7 on purpose: the three real modules are landed by
sibling seats during this same wave, so a selftest that hard-copied them could not have
run at patch time; the fail-closed composition is instead proven by checks (m)/(o) and by
the scored run in §5.

## 2. Selftest arms retargeted 6→7 (exactly three, and why)

The frozen r72 receipt (`EX03GateArm6/selftest.out`) and r73 receipt
(`EX04GateArm/selftest.out`) pin `want_line="PRE_REPORT round=70 arms=6 …"` for the
all-green fixture verdicts. The round-74 patch makes the same fixtures render `arms=7`,
so exactly these three checks had their `want_line` moved 6→7:

1. **`green`** (check (a)) — the all-green fixture; its pinned verdict string is the
   gate's headline shape, so it is retargeted to
   `PRE_REPORT round=70 arms=7 failed=0 uncommitted=0`.
2. **`round-scope-green`** (check (h)) — green round-scope stub; the r72 six-arm
   amendment receipt pinned this exact `arms=6` line as the six-arm green proof.
3. **`round-scope-v2-clean`** (check (i)) — real round-73 counter through arm 5; the r73
   re-point receipt pinned this exact `arms=6` line.

No other existing check needed a retarget: the red checks (b), (c), (d), (e), (f), (g),
(j), (k) assert `want_failed=1` with arm 7 green via stubs, and (l) is a pure
`_detail()` unit probe. The new checks (m), (n), (o) pin arm 7's own red/green/missing
behaviour at `arms=7`.

## 3. Selftest — run, observed

Command (scratch clone, patched):

```
$ cd /fast/scratch/hyaku/kama-r74/EX04GateArm7/clone
$ TMPDIR=/fast/scratch/hyaku/kama-r74/EX04GateArm7/tmp python3 tools/pre-report-gate.py --selftest
```

Result: **`PRE_REPORT_SELFTEST pass=15 fail=0`**, exit 0. Arms in order, all PASS:
`green`, `wave-uncommitted`, `stale-newest-closure`, `missing-declared-path`,
`dirty-declared-path`, `crlf-declared-path`, `round-scope-red`, `round-scope-green`,
`round-scope-v2-clean`, `round-scope-v2-a5-red`, `round-scope-v2-a6-red`,
`verdict-selector`, `round74-v2-red`, `round74-v2-green`, `round74-v2-missing` —
12 pre-existing arms green (arms 1–6 exercised exactly as before, each rendering
`arms=7` in its verdict) plus the three new arm-7 arms. Every green-fixture verdict line
reads `PRE_REPORT round=70 arms=7 failed=0 uncommitted=0`. Key arm-7 lines from the
transcript:

```
  PRE_REPORT_ARM round74-v2 exit=0 ok SELFDESC_CANON_V2 canon_round=70 canon_rows=2 demonstrated=0 total=2 invisible=0 | RECEIPT_CLAIM_V2 round=70 cited=0 bound=0 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0 bound_revisions=0 | PROVINCE_HOST_DRIFT_V2 blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0 edited=0
  PRE_REPORT round=70 arms=7 failed=0 uncommitted=0          # (n) round74-v2-green
  PRE_REPORT_ARM round74-v2 exit=1 FAIL SELFDESC_CANON_V2 canon_round=70 canon_rows=2 demonstrated=1 total=3 invisible=1 | SELFDESC_CANON_V2_FINDING invisible 73 stub-capability | RECEIPT_CLAIM_V2 … | PROVINCE_HOST_DRIFT_V2 …   # (m) round74-v2-red
  PRE_REPORT_ARM round74-v2 exit=1 FAIL SELFDESC_CANON_V2 … | RECEIPT_CLAIM_V2 … | missing round74-province-host-drift.py   # (o) round74-v2-missing
```

Full transcript: `selftest.out`.

## 4. Patch application recipe (L1-owned; I did not touch the lane file)

The patch is a unified diff (`diff -u`, labels `a/tools/pre-report-gate.py` /
`b/tools/pre-report-gate.py`), sha256 `2ef8350374156579fad69af1612b1826931f0c465ae46f27efe25757b7586b8b`,
408 lines, +194/−34 against the committed gate bytes (sha256
`59842d46…93e9` at `b0b903a0`). Apply from the lane root:

```
cd /home/vgpnk/Projects/shokunin/kama-shokunin
git apply --check .ufo/waves/round-74/w1/EX04GateArm7/arm7.patch   # context guard
git apply .ufo/waves/round-74/w1/EX04GateArm7/arm7.patch
```

(`patch -p1 < .ufo/waves/round-74/w1/EX04GateArm7/arm7.patch` is equivalent.) The patch
context is the byte-frozen gate, so if any other edit lands in `tools/pre-report-gate.py`
first, `git apply` fails closed with a context mismatch instead of integrating a
wrong-base amendment. **Post-condition check for the L1:**
`sha256sum tools/pre-report-gate.py` must equal
`6d2e379796de027cc246aaa1673a175d058ea35f1f3ad5c9b9128a095045c1c0`
(recorded in `patched-sha256.txt`; verified `cmp`-identical to the tested working copy).

## 5. Scored run over the scratch clone at `--round 74` — verdict + red demo

Requirement: with the v2 modules absent the patched gate's arm 7 must fail (red demo).
The scratch clone is a clone of the committed tree (`b0b903a0`), where the three modules
do not exist (`ls tools/round74-*.py` → No such file or directory — receipt header in
`gate-round74.out`). Observed:

```
$ TMPDIR=…/tmp python3 tools/pre-report-gate.py --repo . --round 74 --tip master
PRE_REPORT_ARM selfdesc exit=1 FAIL detail: closure_ptr: calibration row latest outside closure is round-72; newest at tip is round-73
PRE_REPORT_ARM newest-closure exit=1 FAIL STALE_CALIBRATION row_names=corpus/lessons/round-72-verifier-spotcheck.md newest=corpus/lessons/round-73-verifier-spotcheck.md newest_date=2026-11-04
PRE_REPORT_ARM receipt-audit exit=0 ok RECEIPT_POINTER_AUDIT files=2 cited=186 resolved=168 expanded=4 corrected=14 unresolved=0
PRE_REPORT_ARM worktree-landing exit=0 ok WORKTREE_LANDING_CHECK paths=5 clean=5 dirty=0 missing=0 untracked=0 unreadable=0
PRE_REPORT_ARM round-scope exit=1 FAIL ROUND_SCOPE_V2 round=74 cases=6 findings=1 | ROUND_SCOPE_V2_FINDING stray tools/pre-report-gate.py status= M
PRE_REPORT_ARM round-clean exit=0 ok files=0
PRE_REPORT_ARM round74-v2 exit=1 FAIL missing round74-selfdesc-canon.py | missing round74-receipt-claim-binding.py | missing round74-province-host-drift.py
PRE_REPORT round=74 arms=7 failed=4 uncommitted=0
EXIT=1
```

- **Verdict string**: `PRE_REPORT round=74 arms=7 failed=4 uncommitted=0` — the frozen
  `arms=7` shape, exactly as the plan's wiring note pins.
- **Red demo**: arm 7 fails closed naming each absent module
  (`missing round74-selfdesc-canon.py | missing round74-receipt-claim-binding.py | missing
  round74-province-host-drift.py`) — never a vacuous green.
- Arms 1–6 states are clone-state properties, not patch defects: selfdesc/newest-closure
  are the known round-72/73 carry-over reds on committed bytes; `round-scope` names
  `stray tools/pre-report-gate.py status= M` — the patch itself, uncommitted in the
  scratch clone (at L1 integration the amendment is part of the round record; the
  scored green run with all seven arms is the L1's post-integration gate). Full
  transcript: `gate-round74.out`.

## 6. Risks and flags for the L1

1. **Mid-wave lane state**: while this seat ran, siblings landed
   `tools/round74-province-host-drift.py`, `tools/round74-seat-count-check.py` and
   `tools/round74-selfdesc-canon.py` in the lane as untracked files
   (`git status --porcelain -uall -- tools/`); `round74-receipt-claim-binding.py` had
   not landed at yield time. My receipts deliberately ran against the committed clone
   (fail-closed red demo, §5); a scored **green** run requires all three modules present
   and is owned by the L1 after integration.
2. **Selftest is stub-only for arm 7** (unlike arms (i)–(k), which copy the real
   round-73 counter): the v2 modules did not exist when the patch had to be testable,
   and they may still be mid-edit during integration. The composition contract (three
   counters, right argv, fail-closed absence, per-counter detail) is pinned by
   (m)/(n)/(o) and the §5 scored run.
3. **Arm-7 detail line is long** (~330 chars: three counters' verdict lines joined) —
   longer than other arms' details but single-line; `render()` and `--json` carry it
   verbatim. Receipts above show it in full.
4. **Not verified by me**: no run of the patched gate against a tree where a v2 module
   exists but is broken mid-execution (spawn covered by `_run` OSError → 127 path,
   structurally identical to arm 5's r72 live spawn failure); mutation coverage of the
   three v2 modules is `MT01Mutants`' scope.
5. **No tool installs** this seat (nothing needed beyond `python3`/`git`/`diff`, all
   pre-existing).
6. The round-scope `stray` finding on the patched gate file (§5) is expected in any
   tree where the patch is applied but uncommitted; it disappears once the L1 commits
   the amendment as part of the round record.

## 7. Files written

Lane (all under `/home/vgpnk/Projects/shokunin/kama-shokunin`):

- `.ufo/waves/round-74/w1/EX04GateArm7/arm7.patch` (the amendment; the only artifact the L1 applies)
- `.ufo/waves/round-74/w1/EX04GateArm7/selftest.out` (full 15-arm selftest transcript, exit 0)
- `.ufo/waves/round-74/w1/EX04GateArm7/gate-round74.out` (scored round-74 run in the scratch clone, exit 1, red demo)
- `.ufo/waves/round-74/w1/EX04GateArm7/patched-sha256.txt` (expected post-apply gate sha256)
- `.ufo/waves/round-74/w1/EX04GateArm7/report.md` and `.ufo/waves/round-74/w1/EX04GateArm7.md` (this report, both paths per the seat brief)

`tools/pre-report-gate.py` in the lane was **not** modified (sha256 re-verified
`59842d46…93e9` after all runs). No other lane file was created, modified or deleted;
the frozen tools (`round42/round72-*/round73-*`, `pre-report-gate.py`) are byte-untouched.

## 8. Scratch

`/fast/scratch/hyaku/kama-r74/EX04GateArm7/` held the pristine/patched working copies
(`work/`), the `--shared` clone (`clone/`) and `tmp/` (selftest TMPDIR); every receipt
was copied into the wave out dir first. The selftest's own fixture work dir was removed
by the selftest itself (no `--keep`). The scratch dir is deleted before yield; no `/tmp`
path is cited as evidence anywhere in this report.
