# report.md — CRT01ClaimC2, round 70, lane kama, claim C2 (operability)

Seat: falsify C2. Advisory only: no verdict, no lane edits, no subagents. Every claim
below is a command with its exit code or a receipt path; the only writes are this out
directory and `/fast/scratch/hyaku/kama-r70/CRT01ClaimC2/` (deleted before yield).

Bottom line: **the frozen counter is sound on the three polarities the seat names but blind
to five designs that violate the frozen target; the landed bytes close the sharp waiver
boundary, and the F1/F2 format findings were integrated at `af6eb6c2`. Remaining: the five
counter holes (fixed by the delivered boundary control), F3 (unknown-waiver exit 0), F5
(OSError reclassification, tradeoff) and F6 (three passages still quote the pre-integration
green line).**

Tip evolution observed while reviewing: `73597158` (C2 landing `7be07423`, census
`a82cad11…`) → `af6eb6c2` (integration: `waived=` only when used, `CENSUS_NOT_EVALUATED`
prefix, `SKILL.md` row; census `44bebd67…`) → `2fc9ce1e` (final measured tip receipt) →
`a8df1af5` (wave evidence, including this seat's output directory).

---

## 0. What I scored

| object | sha256 |
|---|---|
| `controls/freeze.txt` | `ec616473a8673e1e4d959c03b4610af553ae6ef93acf596b981da5256fa9c17f` |
| `controls/refused-member-control.py` | `37fd20eb30ec08a488eea3644f1b2f4b7bb0062b0c12d90bd5a643d2424623b3` |
| base census `measured/before/round65-host-census-base.py` | `463899182af0d154859e86da785051760e4bc314f5489659ea32424c18374513` |
| pre-integration landing `73597158` / `7be07423` | `a82cad11d777aa4b34d8ae96b66250d52853ed880d4c2eaa510ea8b4bf37dc68` |
| final landing `af6eb6c2` (`tools/round65-host-census.py`) | `44bebd671c0d12118c92ace1ef6bd7491a60c7acbce79f1668b81a822b245919` |

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

(`evidence/base-failopen.out`.) The base verdict key is `refused=`, not `not_evaluated=` —
the control's pair is the only signal that changes.

### 1.2 The three named polarities are rejected; five other designs pass

```
$ python3 counterexamples.py
shim                               frozen control                                       exit  verdict
s1-always-fail                     … refused_fixture_exit=1 allpass_fixture_exit=1    1  FAIL (rejected)
s2-refusal-as-pass                 … refused_fixture_exit=0 allpass_fixture_exit=0    1  FAIL (rejected)
s3-cosmetic-not-evaluated          … refused_fixture_exit=0 allpass_fixture_exit=0    1  FAIL (rejected)
s4-refusal-as-fail                 … refused_fixture_exit=1 allpass_fixture_exit=0    0  PASS (hole)
s5t-hardcoded-total                … refused_fixture_exit=1 allpass_fixture_exit=0    0  PASS (hole)
s6w-waiver-swallows-failure        … refused_fixture_exit=1 allpass_fixture_exit=0    0  PASS (hole)
s7-argparse-in-main                <no line>                                          2  FAIL (rejected)
s8r-second-call-silent             … refused_fixture_exit=1 allpass_fixture_exit=0    0  PASS (hole)
s10d-refusal-branch-deleted        … refused_fixture_exit=1 allpass_fixture_exit=0    0  PASS (hole)
exit 0
```

So: always-exit-1 rejected; refusal-as-pass rejected; cosmetic `not_evaluated` with exit 0
rejected — but **five other designs keep the pair and violate the target** (`attack.md` §3).

### 1.3 The landed bytes, both controls

At `af6eb6c2` (`evidence/final-af6eb6c2-census-and-cli.out`):

```
$ python3 .ufo/waves/round-70/controls/refused-member-control.py tools/round65-host-census.py
REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0      exit 0

$ python3 .ufo/waves/round-70/w1/out/CRT01ClaimC2/c2-boundary-control.py \
      tools/round65-host-census.py --frozen-control \
      .ufo/waves/round-70/controls/refused-member-control.py --cli
ok frozen_counter / bare_main_call / fixture_refused / fixture_allpass / fixture_failing
ok single_verdict_line / target_literal
ok waiver_refusal / waiver_failure / waiver_prefix
warn waiver_unknown: exit=0 but the unknown name is named on stderr
ok reentry / population
ok marker:missing dependency / marker:invalid path / marker:cannot resolve master
warn cli_unknown_waiver: exit=0 with the unknown name named on stderr
C2_BOUNDARY_CONTROL pass=15 fail=0 warn=2 skipped=0                       exit 0
```

Without `--cli`: `pass=15 fail=0 warn=1 skipped=1`. On the pre-integration bytes
`a82cad11…`: `pass=13 fail=0 warn=3 skipped=1` (the two extra warns were F1/F2, now fixed);
on the base bytes: `pass=6 fail=9 warn=1 skipped=1`, exit 1. The full shim matrix is in
`evidence/boundary-matrix.out`.

The control's default frozen-counter path is its sibling; the file is committed at
`w1/out/CRT01ClaimC2/c2-boundary-control.py`, so invoke it with `--frozen-control` (as
above) or copy it beside `controls/refused-member-control.py`. A layout test with both
files in one directory (no `--frozen-control`) printed `ok frozen_counter`.

### 1.4 The real census

```
$ python3 tools/round65-host-census.py            # at af6eb6c2, 31.9 s
HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22 tierA_fail=0 tierB_fail=0
CENSUS_EXIT=0
```

Matches the L1's receipt `measured/after/census-at-af6eb6c2.out` line for line. Mid-flight
(at `a82cad11`, while C1's harness repair was still landing) the same run read
`pass=21 fail=1 not_evaluated=0 waived=0 total=22 tierA_fail=1 tierB_fail=0`, exit 1; the
single member that moved is C1's reconciler arm, not a C2 member.

**The freeze's literal target now appears**: `grep -c "HOST_CENSUS pass=22 fail=0
not_evaluated=0 total=22"` → `1` at `af6eb6c2` (`evidence/final-af6eb6c2-census-and-cli.out`),
and `0` on the pre-integration receipt (measured: `evidence/literal-and-mining.out`).

### 1.5 Member set untouched

```
$ python3 -      # loads base bytes and final landed bytes, compares tuples
base rows: 22 final rows: 22
final == base: True
tiers: {'A': 12, 'B': 10}
refusal markers: ['cannot resolve master', 'invalid path', 'missing dependency']
```

Boundary control `population` check: 22 members, tiers `{A: 12, B: 10}`, exact pinned name
set, three refusal markers still pinned on their members — `ok`. The three markers still
mean not-evaluated: injected one-member fixtures for each produce `not_evaluated=1 fail=0`
with no `pass`/`FAIL` line — `marker:*` ok. Canonical table dump
`evidence/table-base.json` sha256 `f89ce38d…`.

### 1.6 Waiver boundary (in-process fixtures, every channel)

- refused member + `--waive <exact name>` → exit 0, `not_evaluated=1`, `waived=1`, reason
  kept, member line marked `[waived]` — `ok`.
- failing member + `--waive <exact name>` → exit 1, `fail=1`, member line `FAIL`, stderr
  says the waiver is unused — `ok` (a failure is never waivable).
- `--waive synthetic` (prefix of `synthetic-refused`) → exit 1 — `ok` (exact-name match).
- `--waive no-such-member` → exit 0 + stderr warning — `warn` (F3).
- OSError spawn path, measured (`evidence/spawn-oserror-probe.out`):

```
base-census.py            exit=1  FAIL [A] gone-binary: spawn error … ; fail=1 tierA_fail=1
ex02-candidate.py         exit=1  refused [A] gone-binary: … ; not_evaluated=1 tierA_fail=0
ex02-candidate.py --waive gone-binary   exit=0  … [waived]; not_evaluated=1 waived=1
```

A missing `.py` member does **not** reach this path (the census prefixes `sys.executable`,
so Python exits 2 and the member lands as `FAIL` with `tierA_fail=1` in both base and landed
bytes). Only a missing interpreter/binary is reclassified.

## 2. Answers to the seat's four asks

1. **Polarity:** the three named shims are rejected (1.2). The counter nonetheless admits
   five non-compliant designs that keep the pair `(1,0)` — refusal-as-fail, literal
   `total=22`, waiver-swallows-failure, silent second call, refusal branch deleted. Root
   cause: exit-only reading; no failing-member fixture, no waiver fixture, no population
   assertion, no re-entrancy assertion.
2. **The waiver hole:** the landed bytes close it (refusal waivable by exact name; a failing
   member never; prefix names do not match; the waived member keeps its reason and
   `waived=` count). But the frozen counter cannot see the difference — `s6w` scores `(1,0)`
   while reporting `pass [A] synthetic-broken (waived)` and exit 0. The boundary is
   guaranteed by review, not by the counter; the delivered control makes it executable.
3. **The member set is untouched:** 22 / 12 A + 10 B, exact table equality, three refusal
   markers still classify as not-evaluated, and the real population run shows the same
   counts as base. C1's kill-rule condition (22 members, reconciler arm registered) holds.
4. **Is `not_evaluated` in the verdict enough?** No, and the exit alone is not either. No
   tracked tool parses either field; the exit is hand-copied into receipts. The lane's own
   mining pattern reads the **last** `HOST_CENSUS` match (`SCR01Lesson.md:41`:
   `grep -o 'HOST_CENSUS[^|]*' "$f" | tail -1`): on the pre-integration bytes a red/waived
   run produced a mangled concatenation (measured in `evidence/literal-and-mining.out`); at
   `af6eb6c2` the explanation line is `CENSUS_NOT_EVALUATED …`, so one prefix remains.
   Conversely `not_evaluated` is the only field that distinguishes "did not run" from
   "failed", and the frozen counter never asserts it. Both must be present **and
   asserted**; the assertion is what the delivered control adds.

## 3. Defects and tradeoffs at `a8df1af5`

| id | class | finding | state |
|---|---|---|---|
| C | defect (central) | five designs pass the frozen counter while violating the target | **open** — fixed by `c2-boundary-control.py` |
| F1 | defect | `waived=0` interposed before `total` made the freeze's literal absent from the green receipt | **resolved at `af6eb6c2`** (`waived=` only when used) |
| F2 | defect | second `HOST_CENSUS` prefix (`HOST_CENSUS exit 1: …`) broke `tail -1`/grep verdict readers | **resolved at `af6eb6c2`** (`CENSUS_NOT_EVALUATED` prefix) |
| F4 | calibration drift | `SKILL.md:1690` registered `refused=R` and exit 0 for a pinned refusal | **resolved at `af6eb6c2`** (row rewritten, committed) |
| F6 | provenance residue | `SCORECARD.md:3714`, `LOG.md:2681`, `corpus/lessons/round-70.md:75` quote the pre-integration green line and cite `measured/after/census-at-tip.out`; the final-values paragraph (`SCORECARD.md:3732`) correctly cites `measured/after/census-at-af6eb6c2.out` | **partially resolved** — annotate the three earlier passages or point them at the new receipt; do not rewrite the old receipt |
| F3 | policy (warn) | unknown `--waive <name>` exits 0 with a stderr warning | open; optional exit 2 (needs the exit map to document 2) |
| F5 | tradeoff | a missing member *binary* is `not_evaluated` (waivable) instead of `fail`; `tierA_fail` no longer counts it | open; L1's call |
| — | not a defect | frozen counter's three polarities; waiver exact-name scope; member table; exit rule `failed == 0 and not unwaived_ne` | — |

## 4. What I could NOT verify

- The round validator's matching mode for the target line. It no longer matters: the
  literal is present at `af6eb6c2` and the token form was always present.
- Windows-host behavior: no Windows path exercised; the adaptation is byte-identical to
  base.
- The `--cli` process probe beyond `af6eb6c2`: I ran it there (`pass=15 fail=0 warn=2
  skipped=0`); a later tip must re-run it if the census changes again.
- Whether the L1 wants the boundary control registered as a tracked instrument (I did not
  propose registration: it is a wave-local control, like the frozen counter).

## 5. Exact bytes/paths the L1 must land

1. **Second control.** `w1/out/CRT01ClaimC2/c2-boundary-control.py`
   (sha256 `7b364ae1fcc66e6dceb8e8c37a0931e138442ab970094ae3a84dce9e30ccea80`) is already
   committed at that path. If it is to live beside the frozen counter, copy it to
   `.ufo/waves/round-70/controls/c2-boundary-control.py`, where its sibling default works
   without `--frozen-control`; otherwise keep invoking it with `--frozen-control`.
   Post-landing command and expected line are in §1.3.
2. **`counterexamples.py`** (sha256
   `d6df475b7a42e66a93376680324896d176484d9e6e1a44df75096b2f57e9ced8`) stays as the
   wave-local reproduction receipt; run it from anywhere.
3. **`superseded/`** holds the F1/F2 patch and corrected bytes — **superseded by
   `af6eb6c2`, do not apply**; kept as the reasoning record (the integration used the
   prefix `CENSUS_NOT_EVALUATED` instead of the patch's `CENSUS_EXIT`, and the same
   `waived=` rule).
4. **F6:** point `SCORECARD.md:3714`, `LOG.md:2681` and `corpus/lessons/round-70.md:75` at
   `measured/after/census-at-af6eb6c2.out` (the L1's own receipt, line
   `HOST_CENSUS pass=22 fail=0 not_evaluated=0 total=22 tierA_fail=0 tierB_fail=0`,
   `EXIT=0`), or add a one-sentence note that the quoted line is the `a82cad11…` output and
   the tool now prints the contiguous form. Keep both receipts.

## 6. Hygiene

- No tool installed or upgraded; no pacman transaction; no tooling exception needed.
- No git/jj mutation in the lane: only `rev-parse`, `log`, `status`, `show`, `diff`,
  `ls-tree`. The one `git init`/`git apply` fixture lived under
  `/fast/scratch/hyaku/kama-r70/CRT01ClaimC2/fx.*`, asserted `rev-parse --show-toplevel`
  equal to itself before writing, and was deleted.
- Writes: this out directory and the scratch directory only; scratch is removed before
  yield. No `/tmp` artifact is cited as evidence.
- No lane file edited, created or deleted; the census was scored read-only from its landed
  path (the only mutation was the L1's own integration while the review ran).
