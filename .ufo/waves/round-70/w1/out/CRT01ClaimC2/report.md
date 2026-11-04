# report.md — CRT01ClaimC2, round 70, lane kama, claim C2 (operability)

Seat: falsify C2. Advisory only: no verdict, no lane edits, no subagents. Every claim
below is a command with its exit code or a receipt path; the only writes are this out
directory and `/fast/scratch/hyaku/kama-r70/CRT01ClaimC2/` (deleted before yield).

Bottom line: **the frozen counter is sound on the three polarities the seat names but
blind to five designs that violate the frozen target; the landed bytes close the sharp
waiver boundary and leave two receipt-readability defects plus one stale registered exit
map.** The landing (`7be07423`, tip `73597158`) is green on the freeze's substance; the
freeze's *literal* target line does not occur in the landed receipt.

---

## 0. What I scored

| object | sha256 |
|---|---|
| `controls/freeze.txt` | `ec616473a8673e1e4d959c03b4610af553ae6ef93acf596b981da5256fa9c17f` |
| `controls/refused-member-control.py` | `37fd20eb30ec08a488eea3644f1b2f4b7bb0062b0c12d90bd5a643d2424623b3` |
| base census `measured/before/round65-host-census-base.py` | `463899182af0d154859e86da785051760e4bc314f5489659ea32424c18374513` |
| landed census `tools/round65-host-census.py` (tip `73597158`, landing commit `7be07423`) | `a82cad11d777aa4b34d8ae96b66250d52853ed880d4c2eaa510ea8b4bf37dc68` |

The worktree census was byte-identical to EX02's delivered candidate when I scored it,
and is the committed file at `73597158` (`git show HEAD:tools/round65-host-census.py |
sha256sum` → `a82cad11…`).

## 1. Commands, outputs, exit codes

### 1.1 The fail-open reproduces at base

```
$ python3 .ufo/waves/round-70/controls/refused-member-control.py \
      .ufo/waves/round-70/measured/before/round65-host-census-base.py
{"refused_fixture": ["pass [A] synthetic-pass", "refused [A] synthetic-refused: fail-closed
 refusal: synthetic NTFS stand-in (control) (marker 'invalid path')",
 "HOST_CENSUS pass=1 fail=0 refused=1 total=2 tierA_fail=0 tierB_fail=0"],
 "allpass_fixture": ["pass [A] synthetic-pass", "pass [A] synthetic-pass-2",
 "HOST_CENSUS pass=2 fail=0 refused=0 total=2 tierA_fail=0 tierB_fail=0"]}
REFUSED_MEMBER_CONTROL refused_fixture_exit=0 allpass_fixture_exit=0
exit 1
```

(`evidence/base-failopen.out`). The base verdict key is `refused=`, not `not_evaluated=` —
the control's pair is the only signal that changes.

### 1.2 The three named polarities are rejected

```
$ python3 counterexamples.py
shim                               frozen control                                       exit  verdict
s1-always-fail                     REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=1    1  FAIL (rejected)
s2-refusal-as-pass                 REFUSED_MEMBER_CONTROL refused_fixture_exit=0 allpass_fixture_exit=0    1  FAIL (rejected)
s3-cosmetic-not-evaluated          REFUSED_MEMBER_CONTROL refused_fixture_exit=0 allpass_fixture_exit=0    1  FAIL (rejected)
s4-refusal-as-fail                 REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0    0  PASS (hole)
s5t-hardcoded-total                REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0    0  PASS (hole)
s6w-waiver-swallows-failure        REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0    0  PASS (hole)
s7-argparse-in-main                <no line>                                               2  FAIL (rejected)
s8r-second-call-silent             REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0    0  PASS (hole)
s10d-refusal-branch-deleted        REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0    0  PASS (hole)
exit 0
```

So: always-exit-1 rejected; refusal-as-pass rejected; cosmetic `not_evaluated` with exit 0
rejected. **Five other designs pass** (details in `attack.md` §3).

### 1.3 The landed bytes, both controls

```
$ python3 .ufo/waves/round-70/controls/refused-member-control.py tools/round65-host-census.py
REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0      exit 0

$ python3 w1/out/CRT01ClaimC2/c2-boundary-control.py tools/round65-host-census.py \
      --frozen-control .ufo/waves/round-70/controls/refused-member-control.py
ok frozen_counter / bare_main_call / fixture_refused / fixture_allpass / fixture_failing
warn single_verdict_line: 2 HOST_CENSUS-prefixed lines on the refused fixture
warn target_literal: 'pass=2 fail=0 not_evaluated=0 total=2' does not appear in
     'HOST_CENSUS pass=2 fail=0 not_evaluated=0 waived=0 total=2 tierA_fail=0 tierB_fail=0'
ok waiver_refusal / waiver_failure / waiver_prefix / reentry / population
ok marker:missing dependency / marker:invalid path / marker:cannot resolve master
warn waiver_unknown: exit=0 but the unknown name is named on stderr
C2_BOUNDARY_CONTROL pass=13 fail=0 warn=3 skipped=1                       exit 0
```

With `--cli` (a full census run inside the check; at the green tip):

```
warn cli_unknown_waiver: exit=0 with the unknown name named on stderr
C2_BOUNDARY_CONTROL pass=13 fail=0 warn=4 skipped=0                       exit 0
```

(`evidence/boundary-matrix.out`, `evidence/boundary-cli.out`.)

### 1.4 The corrected bytes (2-line format fix)

```
$ python3 w1/out/CRT01ClaimC2/c2-boundary-control.py w1/out/CRT01ClaimC2/ex02-candidate-corrected.py \
      --frozen-control .ufo/waves/round-70/controls/refused-member-control.py
ok … all 15 checks … warn waiver_unknown (unknown name exits 0, named on stderr)
C2_BOUNDARY_CONTROL pass=15 fail=0 warn=1 skipped=1                       exit 0
```

Patch applies to the landed bytes from the lane root and reproduces the corrected sha256:

```
$ diff -u --label a/tools/round65-host-census.py --label b/tools/round65-host-census.py \
      <landed bytes> <corrected bytes> > correction.patch        # exit 1 (differences expected)
$ git -C $FIXTURE apply --check $PWD/correction.patch            # APPLY_CHECK_OK
$ git -C $FIXTURE apply $PWD/correction.patch                    # APPLY_OK
$ sha256sum $FIXTURE/tools/round65-host-census.py
c985c114610779019c732851a0503f8fff0b642f36b4ab26019fde2f6f10d703  (== ex02-candidate-corrected.py)
```

(`$FIXTURE` was `mktemp -d /fast/scratch/hyaku/kama-r70/CRT01ClaimC2/fx.XXXX` with its own
`git init`; `git -C "$FIXTURE" rev-parse --show-toplevel` printed `$FIXTURE` before the
apply. The fixture was removed afterwards.)

Note: the `--cli` probe on the corrected copy in the out directory is **not** valid — the
census derives `LANE` from `__file__`, so an out-of-lane copy runs members with the wrong
cwd. Run `--cli` only after landing.

### 1.5 The real census at the landing tip (receipt, not my run)

`.ufo/waves/round-70/measured/after/census-at-tip.out`:

```
HOST_CENSUS pass=22 fail=0 not_evaluated=0 waived=0 total=22 tierA_fail=0 tierB_fail=0
EXIT=0
```

My independent runs of those committed bytes: at the mid-flight state
(`python3 tools/round65-host-census.py`, 34.5 s) `pass=21 fail=1 not_evaluated=0 waived=0
total=22 tierA_fail=1 tierB_fail=0`, exit 1; at the landing tip (31.6 s)
`HOST_CENSUS pass=22 fail=0 not_evaluated=0 waived=0 total=22 tierA_fail=0 tierB_fail=0`,
`CENSUS_EXIT=0` (`evidence/realrun-landed-tip.out`). Counts and population are consistent;
the single member that moved between the two runs is C1's reconciler arm, not a C2 member.

**The freeze's literal target `HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22` does
not occur in the landed green line** — `waived=0` is interposed. Measured on the landed
receipt (`evidence/literal-and-mining.out`): literal count `0`, interposed form count `1`.
The round's own record quotes the interposed form (`SCORECARD.md:3714`), so the record is
honest but the freeze's literal is unmet.

With the two-line correction applied, the same real population at the tip prints exactly
the freeze's literal — in-process load with `LANE` pinned to the lane root, 32.2 s
(`evidence/realrun-corrected-at-tip.out`):

```
HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22 tierA_fail=0 tierB_fail=0
EXIT=0
```

(`grep -c` for the freeze's literal: `1`.)

### 1.6 Member set untouched

```
$ python3 -  # loads base bytes and landed bytes, compares tuples
base rows: 22 cand rows: 22 pinned rows: 22
cand == base: True
tierA: 12 tierB: 10
refusal-carrying members: 3
distinct refusal markers: ['cannot resolve master', 'invalid path', 'missing dependency']
```

Boundary control `population` check: 22 members, tiers `{A: 12, B: 10}`, exact pinned name
set, three refusal markers still pinned on their members — `ok`. The three refusal markers
still mean not-evaluated: injected one-member fixtures for each marker produce
`not_evaluated=1 fail=0` with no `pass`/`FAIL` line — `ok`.

### 1.7 OSError spawn path (tradeoff, measured)

`evidence/spawn-oserror-probe.out`, a member whose argv is a missing non-`.py` binary:

```
base-census.py            exit=1  FAIL [A] gone-binary: spawn error … ; fail=1 tierA_fail=1
ex02-candidate.py         exit=1  refused [A] gone-binary: spawn error … ; not_evaluated=1 tierA_fail=0
ex02-candidate.py --waive gone-binary   exit=0  … [waived]; not_evaluated=1 waived=1
```

A missing `.py` member does **not** reach this path (the census prefixes `sys.executable`,
so Python exits 2 and the member lands as `FAIL` with `tierA_fail=1` in both base and
landed bytes). Only a missing interpreter/binary is reclassified.

## 2. Answers to the seat's four asks

1. **Polarity:** the three named shims are rejected (1.2). The counter nonetheless admits
   five non-compliant designs that keep the pair `(1,0)`: refusal-as-fail, literal
   `total=22`, waiver-swallows-failure, silent second call, refusal branch deleted. Root
   cause: exit-only reading; no failing-member fixture, no waiver fixture, no population
   assertion, no re-entrancy assertion.
2. **The waiver hole:** the landed bytes close it (refusal waivable by exact name; a failing
   member is never waivable; prefix names do not match; the waived member keeps its reason
   and `waived=` count). But the frozen counter cannot see the difference — `s6w` scores
   `(1,0)` while reporting `pass [A] synthetic-broken (waived)` and exit 0. The boundary is
   guaranteed by review, not by the counter; the delivered control makes it executable.
3. **The member set is untouched:** 22 / 12 A + 10 B, exact table equality, three refusal
   markers still classify as not-evaluated, and the real population run shows the same
   counts as base. C1's kill-rule condition (22 members, reconciler arm registered) holds.
4. **Is `not_evaluated` in the verdict enough?** No, and the exit alone is not either. No
   tracked tool parses either field; the exit is hand-copied into receipts. The round's own
   mining command reads the **last** `HOST_CENSUS` match
   (`w1/out/SCR01Lesson.md:41`: `grep -o 'HOST_CENSUS[^|]*' "$f" | tail -1`), and on a red
   or waived run the landed bytes print a second `HOST_CENSUS`-prefixed explanation line,
   so that reader records prose and loses the counts. Conversely `not_evaluated` is the only
   field that distinguishes "did not run" from "failed", and the frozen counter never
   asserts it. Both must be present **and asserted**; the assertion is the missing piece,
   and it is what the delivered control adds.

## 3. Defects and tradeoffs

| id | class | finding | smallest safe correction |
|---|---|---|---|
| F1 | defect (cheap) | `waived=0` interposed before `total`, so the freeze's literal green line is absent from the landed receipt | emit `waived=` only when `> 0` (delivered `correction.patch`) |
| F2 | defect (cheap) | second `HOST_CENSUS` prefix (`HOST_CENSUS exit 1: …`) on red/waived runs. Measured on the landed control receipt with the lane's own mining pattern (`SCR01Lesson.md:41`, `grep -o 'HOST_CENSUS[^|]*' \| tail -1`): the match is a mangled concatenation of the refused verdict, the explanation and the all-pass verdict, not a verdict line (`evidence/literal-and-mining.out`). Any refused/waived census receipt mined this way reads prose | print `CENSUS_EXIT 1: …` (same patch) |
| F3 | policy (warn) | unknown `--waive <name>` exits 0 with a stderr warning | optional exit 2 before running members; needs the exit map to document 2 |
| F4 | calibration drift | `SKILL.md:1690` still registers `refused=R` and exit 0 for a pinned refusal; the landed tool prints `not_evaluated=` and exits 1 unless waived. Not machine-caught (gate checks row shape/paths; the reconciler does not read this row) | one-row replacement, §5 |
| F5 | tradeoff | a missing member *binary* is now `not_evaluated` (waivable) instead of `fail`; `tierA_fail` no longer counts it | keep base behavior for `OSError`, or accept and document that `tierA_fail` is not the not-run count |
| — | not a defect | the frozen counter's three polarities; waiver exact-name scope; member table; exit rule `failed == 0 and not unwaived_ne` | — |

## 4. What I could NOT verify

- The round validator's matching mode for the target line (literal substring vs `k=v`
  tokens). F1 is therefore filed as a WARN with the exact consequence; applying the patch
  satisfies either mode.
- Windows-host behavior: no Windows path exercised; the adaptation is byte-identical to
  base.
- The corrected bytes through the *process boundary* at the real path: the corrected file
  cannot sit at `tools/round65-host-census.py` (lane is read-only for this seat), so its
  real-population run used an in-process load with `LANE` pinned to the lane root (green,
  freeze literal present, `evidence/realrun-corrected-at-tip.out`). The `--cli` process
  probe must be rerun after landing.
- Whether the L1 intends to keep the double `HOST_CENSUS` prefix as a feature; I found no
  consumer that wants two prefixes, but it is a policy call.

## 5. Exact bytes/paths the L1 must land

1. **Second control** — copy
   `w1/out/CRT01ClaimC2/c2-boundary-control.py`
   (sha256 `7b364ae1fcc66e6dceb8e8c37a0931e138442ab970094ae3a84dce9e30ccea80`) to
   `.ufo/waves/round-70/controls/c2-boundary-control.py`. Its default frozen-control path
   is its sibling, which is correct at that location. Run at the landing tip:

   ```
   python3 .ufo/waves/round-70/controls/c2-boundary-control.py tools/round65-host-census.py --cli
   ```
   Expect `C2_BOUNDARY_CONTROL pass=15 fail=0 warn=2 skipped=0` after (2) is applied
   (`warn` = F3 on both probes: the in-process unknown waiver and the CLI one), exit 0.
   Before (2): `pass=13 fail=0 warn=4`. With the optional exit-2 policy (F3) as well:
   `pass=17 fail=0 warn=0 skipped=0`.

2. **Census format fix** — apply `w1/out/CRT01ClaimC2/correction.patch`
   (sha256 `a095e623c29e7fcde4a59aa452ae270042462ce70c0df8c97d063a0221f27b7b`) from the
   lane root, or copy `ex02-candidate-corrected.py`
   (sha256 `c985c114610779019c732851a0503f8fff0b642f36b4ab26019fde2f6f10d703`) over
   `tools/round65-host-census.py`. The patch was dry-run and applied on a scratch fixture
   whose toplevel was the fixture; the result hash equals the corrected file's.

3. **`SKILL.md:1690` row replacement** (calibration drift, F4). Exact old → new cells:

   old exit-map cell:
   `0 every member passes or refuses with a pinned reason (`HOST_CENSUS pass=N fail=0 refused=R`); 1 any member fails (exit nonzero without a pinned refusal marker)`

   new exit-map cell:
   `0 `fail=0` and every not-evaluated member named by an explicit repeatable `--waive <member-name>` (`HOST_CENSUS pass=N fail=0 not_evaluated=R [waived=W] total=T`); 1 any member failed, or any not-evaluated member is unwaived`

   (No pipe characters; the row keeps five cells. If F3's exit 2 is adopted, append
   `; 2 could-not-evaluate (unknown --waive name)`.)

4. **Receipts** — the wave-local files `counterexamples.py`
   (sha256 `d6df475b7a42e66a93376680324896d176484d9e6e1a44df75096b2f57e9ced8`) and
   `evidence/*` stay under `w1/out/CRT01ClaimC2/` as the reproduction record; no lane
   registration is needed for either (wave-local control, not a registered instrument).

## 6. Hygiene

- No tool installed or upgraded; no pacman transaction; no tooling exception needed.
- No git/jj mutation in the lane: only `rev-parse`, `log`, `status`, `show`, `diff`,
  `ls-tree`. The one `git init`/`git apply` fixture lived under
  `/fast/scratch/hyaku/kama-r70/CRT01ClaimC2/fx.*`, asserted `rev-parse --show-toplevel`
  equal to itself before writing, and was deleted.
- Writes: this out directory and the scratch directory only; scratch is removed before
  yield. No `/tmp` artifact is cited as evidence.
- No lane file edited, created or deleted; the census was scored read-only from its
  landed path.
