# VerifyMistakeFix — kama round 29, wave 2 (attempt 2)

Seat: `kama-r29-w2-VerifyMistakeFix-6` (executor)
Lane repo: `/home/vgpnk/Projects/shokunin/kama-shokunin` (branch master, HEAD `513eba3ba51a142c9936553e3a85918345eb5c4c`)
Scope: verify the round-29 "mined mistake" fix to `tools/prereg-time-check.py` (space/tilde
timestamp forms) against the inherited attempt-1 receipts, and attack the fix.
Bounds respected: **no lane mutation.** Only `git archive` extraction into `/tmp`, a scratch
`git clone` under `/tmp`, and `--scratch` dirs under `/tmp`. No `git worktree add`, no lane
`git add/commit/checkout/reset`, no writes outside this seat's output directory and `/tmp`.

---

## 1. Verdict summary

| # | Claim under test | Verdict |
|---|---|---|
| V1 | Patched tool at `75b78bb4` exits 1 flagging `2026-10-23 ~08:45Z (later than commit by 404s)` | **PASS** — reproduced byte-identical |
| V2 | Patched tool at `d8bf1804` exits 0 | **PASS** — reproduced byte-identical |
| V3 | Original tool at `75b78bb4` exits 0 (the mined blindness) | **PASS** — reproduced byte-identical |
| V4 | `--selftest` in the working tree: 15 PASS, exit 0 | **FAIL — count is 13, not 15** (see D1) |
| V5 | Patched tool at `513eba3b` exits 0 | **FAIL for the round-28 prereg path (exit 1)**; exit 0 only for the round-29 prereg path (see D2) |
| V6 | The widened regex harms nothing else in the lane | **PASS** — exactly 1 new flag lane-wide, the intended target (see §4) |
| V7 | The fix kills the 3 mutants MutateTimeCheck found surviving | **PASS only with the uncommitted working-tree case**; at committed HEAD all 3 still survive (see D3) |
| V8 | The lesson/LOG receipts for the fix are committed | **FAIL** — 2 of 7 mined receipts are untracked (see D4) |

**Overall: the fix itself is correct, minimal and harmless. The attempt-1 narrative around it has four
defects (D1–D4), all of which the L1 must repair before landing.**

---

## 2. Method

Extraction (no worktree, per the L1 steering correction):

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive 75b78bb4  | tar -x -C /tmp/kama-w2-VerifyMistakeFix/tree-75b78bb4
git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive d8bf1804  | tar -x -C /tmp/kama-w2-VerifyMistakeFix/tree-d8bf1804
git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive 513eba3b  | tar -x -C /tmp/kama-w2-VerifyMistakeFix/tree-513eba3b
git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-w2-VerifyMistakeFix/clone
```

Tool bytes at each revision (`sha256`):

| tree | sha256 of `tools/prereg-time-check.py` |
|---|---|
| `tree-75b78bb4` (= `tree-d8bf1804`, identical) | `3d508f776e5b8fac2685dcb80f5bb5c3865427baec3046c4f5b51bed336358c1` |
| `tree-513eba3b` (the mined fix, committed) | `ca72edf2a210a763c1d8cbc7a57aa70445a2794c195fc288e82d6dfe7d473dd4` |
| lane working tree (fix + one extra selftest case) | `ab685ac2973a1b287ebff4bb6f147de3a6530b15768e02ef2bc64077f8c043eb` |

The `ca72edf2…` digest matches the one MutateTimeCheck recorded
(`.ufo/waves/round-29/w1/advice/MutateTimeCheck.md:3`), so the committed fix is the one that was tested.

---

## 3. Exit codes — every run, measured

Command form (repo = the scratch clone, so the lane is never touched):
`python3 <tool> --repo /tmp/kama-w2-VerifyMistakeFix/clone --path <path> --rev <rev> --strict`

| # | tool | rev | path | exit | vs. receipt |
|---|---|---|---|---|---|
| A | patched (`ca72edf2…`, at 513eba3b) | 75b78bb4 | `.ufo/waves/round-28/preregistration.json` | **1** | **byte-identical** to `mined/patched-75b78bb4.out` |
| B | patched | d8bf1804 | `.ufo/waves/round-28/preregistration.json` | **0** | **byte-identical** to `mined/patched-d8bf1804.out` |
| C | original (`3d508f77…`, at 75b78bb4) | 75b78bb4 | `.ufo/waves/round-28/preregistration.json` | **0** | **byte-identical** to `mined/orig-75b78bb4.out` |
| D | patched | 513eba3b | `.ufo/waves/round-28/preregistration.json` | **1** | **no receipt exists** — see D2 |
| E | patched | 513eba3b | `.ufo/waves/round-29/preregistration.json` | **0** | **no receipt exists** |
| F | patched | 75b78bb4 | `.ufo/waves/round-29/preregistration.json` | **2** | path absent at that rev (`no commit touches …`) |
| G | original | d8bf1804 | `.ufo/waves/round-28/preregistration.json` | **0** | control, no receipt |
| H | original | 513eba3b | `.ufo/waves/round-28/preregistration.json` | **0** | control, no receipt |

Diff evidence (`diff` against the committed receipts, run A/B/C):

```
IDENTICAL: patched-75b78bb4.out == r1.out
IDENTICAL: patched-d8bf1804.out == r2.out
IDENTICAL: orig-75b78bb4.out == r3.out
```

Self-test exit codes:

| # | tool | exit | `[PASS]` lines | `PASS`-substring lines |
|---|---|---|---|---|
| S1 | working tree (`ab685ac2…`) | **0** | **13** | 14 |
| S2 | committed 513eba3b (`ca72edf2…`) | **0** | 12 | 13 |
| S3 | original 75b78bb4 (`3d508f77…`) | **0** | 10 | 11 |
| S4 | receipt `mined/patched-selftest-v2.out` | 0 | 13 | 14 |
| S5 | receipt `mined/patched-selftest.out` | 0 | 12 | 13 |
| S6 | receipt `mined/orig-selftest.out` | 0 | 10 | 11 |

Selftest scratch dirs were under `/tmp/kama-w2-VerifyMistakeFix/…` (seat-unique), never the default
`/fast/scratch/hyaku/kama-r26/ExecPreregTimeCheck`.

---

## 4. Harm surface of the widened regex — measured, not asserted

The fix widens `TIME_RE` from `\d{4}-\d{2}-\d{2}T…` to `\d{4}-\d{2}-\d{2}(?:T| ~| )…` and widens
`parse_iso` to match. The risk is false positives on legitimate text. Measured by running **both**
tools over **every** tracked file at `513eba3b` (8662 files), at both the default horizon
(86400 s) and `--strict`, and comparing flag sets:

```
### mf=86400 (default-horizon(86400)): 8662 files; PATCHED-only extra flags in 1 file(s)
  FILE .ufo/waves/round-28/preregistration.json
    ORIG   : (none)
    PATCHED: FLAG line 41: 2026-10-23 ~08:45Z (later than commit by 404s)

### mf=-1 (strict): 8662 files; PATCHED-only extra flags in 1 file(s)
  FILE .ufo/waves/round-28/preregistration.json
    ORIG   : (none)
    PATCHED: FLAG line 41: 2026-10-23 ~08:45Z (later than commit by 404s)
```

**The widened regex adds exactly one flag lane-wide, and it is the intended target.** No collateral
false positives. (Both tools flag the same ~25 other files in `--strict` mode — those are the
pre-existing legitimate-future provider-reset timestamps the horizon exists for; the widened regex
does not add to that set.)

---

## 5. Mutants — the fix is only as strong as the case that kills the mutants

MutateTimeCheck (`.ufo/waves/round-29/w1/advice/MutateTimeCheck.md`) reported 3 surviving mutants:
M02/M05 (plain-space recognition removed from `TIME_RE` / from `parse_iso`) and M07 (parsed seconds
zeroed). I reproduced all three, in-process **and** via subprocess, against **both** the committed
tool and the working-tree tool:

```
=== M02-no-plain-space-in-TIME_RE ===
  committed-513eba3b     selftest exit=0 PASS=12 verdict=SURVIVED
  working-tree           selftest exit=1 PASS=12 verdict=KILLED
      [FAIL] flag: space-separated seconds-precision time 7 s after commit: expect 1, got 0
=== M05-no-plain-space-in-parse_iso ===
  committed-513eba3b     selftest exit=0 PASS=12 verdict=SURVIVED
  working-tree           selftest exit=1 PASS=12 verdict=KILLED
      [FAIL] flag: space-separated seconds-precision time 7 s after commit: expect 1, got 0
=== M07surgical-zero-seconds-only ===
  committed-513eba3b     selftest exit=0 PASS=12 verdict=SURVIVED
  working-tree           selftest exit=1 PASS=12 verdict=KILLED
      [FAIL] flag: space-separated seconds-precision time 7 s after commit: expect 1, got 0
```

Subprocess confirmation (`/tmp/kama-w2-VerifyMistakeFix/mut2.sh`, same verdicts):

```
mutant=m02  base=committed selftest_exit=0 PASS=12 FAIL=0 verdict=SURVIVED
mutant=m02  base=wtree     selftest_exit=1 PASS=12 FAIL=1 verdict=KILLED
mutant=m07s base=committed selftest_exit=0 PASS=12 FAIL=0 verdict=SURVIVED
mutant=m07s base=wtree     selftest_exit=1 PASS=12 FAIL=1 verdict=KILLED
```

This **confirms** the lane's claim in `corpus/lessons/round-29.md:125` ("MutateTimeCheck's 3
surviving mutants … are killed by the added 7-second case") — **but only for the uncommitted
working-tree tool**. At committed `513eba3b` all three still survive. See D3.

Note also: a broader "zero all parsed fields" mutant (M07-wide) is killed by **both** versions — the
lane's narrower surgical M07 is the harder one, and the working-tree case does kill it.

---

## 6. Defects found (report only — L1 integrates)

### D1 — The self-test PASS count in the task spec and in LOG.md/lesson is wrong

The item text says "run `--selftest` in the working tree expecting 15 PASS exit 0". Measured: **13**
`[PASS]` lines (11 `case()` calls + missing-path + bad-revision), exit 0. The working tree has
**11** `case()` calls and **13** assertions total; 15 is unreachable by any variant of this tool.

The narrative artifacts repeat the same off-by-N:

- `LOG.md:1858` (uncommitted): ``Re-verification (freshness): `tools/prereg-time-check.py --selftest` 14 PASS exit 0;``
- `corpus/lessons/round-29.md:125` (uncommitted): ``self-test 14 PASS exit 0 (`mined/patched-selftest-v2.out`)``

14 is the count of lines **containing the substring** "PASS" (13 `[PASS]` + 1 `SELFTEST PASS`).
The receipt `mined/patched-selftest-v2.out` likewise has 13 `[PASS]` lines and 14 "PASS"-substring
lines. So "14 PASS" is defensible only under the substring reading; "15 PASS" (spec) is wrong under
every reading. **Recommend: state "13 cases, 13 PASS, exit 0" and drop the ambiguity.** This matters
because C1 counts `Q`-class statements — a quoted output count that is off by one is precisely the
mistake class this round measures.

### D2 — The spec's "at 513eba3b expect exit 0" is false for the round-28 prereg path

Measured (row D above): patched tool at `513eba3b` on `.ufo/waves/round-28/preregistration.json`
**exits 1**, still flagging `2026-10-23 ~08:45Z (later than commit by 404s)`. This is *correct
behaviour* — the false timestamp is still physically in that frozen file and the commit that wrote
it (`75b78bb4`, 08:38:16Z) is still its last committer, so the text is still 404 s in the future.
The round-29 repair was append-only elsewhere (`LOG.md`, `corpus/lessons/round-29.md`), deliberately
leaving the frozen bytes untouched.

But the spec expectation, and the absence of any `513eba3b` receipt in `mined/`, leave this
unrecorded. **Recommend: add a receipt showing exit 1 at `513eba3b` on the round-28 prereg path
and state explicitly that the false bytes survive by design and that the repair is an appended
record, not an edit.** The exit-0 result at `513eba3b` (row E) is on the *round-29* prereg path,
which contains no timestamps at all — a different fact that should not be conflated.

### D3 — The mutant-killing selftest case is uncommitted; the committed tip still lets all 3 mutants survive

The working tree adds exactly one case relative to `513eba3b`:

```diff
@@ -206,6 +206,8 @@ def selftest(scratch: str) -> int:
          '{"note": "Written 2026-10-23 ~03:45Z by the L1"}\n', EXIT_FLAGGED)
     case("clean: space-separated time before commit",
          '{"note": "frozen 2026-10-23 03:10Z"}\n', EXIT_CLEAN)
+    case("flag: space-separated seconds-precision time 7 s after commit",
+         '{"note": "frozen 2026-10-23 03:19:50Z"}\n', EXIT_FLAGGED)
```

(`git diff tools/prereg-time-check.py` in the lane; also `diff` of the working tree against
`clone/tools/prereg-time-check.py` at `513eba3b`.)

This one case is what kills M02, M05 and M07 (§5). It is **not committed**. If the L1 lands
`513eba3b` as-is, the lane ships a falsifier whose selftest still passes for all three mutants, and
the lesson's "the added 7-second case kills them" claim is false of the landed tree.
**Recommend: land the working-tree tool change together with the mined receipts.**

### D4 — Two of the seven mined receipts are untracked, yet the lesson cites them as evidence

```
TRACKED   orig-75b78bb4.out
TRACKED   orig-selftest.out
TRACKED   patched-75b78bb4.out
TRACKED   patched-d8bf1804.out
TRACKED   patched-selftest.out
UNTRACKED patched-selftest-v2.out
UNTRACKED survivor-recheck.out
```

`corpus/lessons/round-29.md:125` cites `mined/patched-selftest-v2.out` and
`mined/survivor-recheck.out` as the proof that the mutants are killed. Neither is in commit
`513eba3b`. **Recommend: commit both.**

### D5 — Minor: the tool's own `--help`/docstring still describes only the `T` form

`tools/prereg-time-check.py` module docstring (lines 4–7, still present at HEAD) says the tool
"read[s] every ISO-8601 UTC time (YYYY-MM-DDTHH:MM[:SS]Z)". After the fix it also reads
`YYYY-MM-DD ~HH:MMZ` and `YYYY-MM-DD HH:MMZ`. The in-code comment at lines 39–41 documents the
widening, but the user-facing docstring and `--help` output were not updated. Cosmetic, but this
docstring is the tool's contract.

### D6 — Minor, disclosed: residual notation limits of the widened regex

Measured against the patched `TIME_RE`:

```
MATCH tilde-space (mined case)     '2026-10-23 ~08:45Z'
MATCH plain space                  '2026-10-23 08:45Z'
MATCH T form                       '2026-10-23T08:45Z'
MISS  tilde-space-space            '2026-10-23 ~ 08:45Z'
MISS  lowercase t                  '2026-10-23t08:45Z'
MISS  fractional seconds           '2026-10-23T08:45:00.123Z'
MATCH plain space + seconds        '2026-10-23 08:45:00Z'
MISS  no Z                         '2026-10-23 08:45'
MISS  tilde no space               '2026-10-23~08:45Z'
```

These are outside the mined mistake class and the round-29 preregistration uses no timestamp form
at all, so no current statement is affected. Note the counter's own T-class regex
(`count-c1.py:72`, `\b(20\d\d-\d\d-\d\d)(?:T| ~|T~)\d\d:\d\d(?::(\d\d))?Z`) and the tool's regex
now differ in **both directions**: the counter matches `T~` but not a plain space; the tool matches
a plain space but not `T~`. Worth disclosing rather than leaving as an accident.

---

## 7. Things I checked that were fine

- The mined fix itself (`TIME_RE` + `parse_iso` widening) is committed in `513eba3b` and is
  minimal — 2 regex strings plus a comment. `git diff tree-75b78bb4 → tree-513eba3b` shows no other
  change to the tool.
- The fix does not break the legitimate-future-data case: the round-26 provider-reset
  `2026-10-25T14:27:28Z` is still `clean` under the default horizon and still `flag` under
  `--strict`, exactly as before (selftest cases 4 and 5 PASS in all three tool versions).
- `parse_iso` and `TIME_RE` remain consistent: every `TIME_RE` match shape is accepted by
  `parse_iso` (verified by the `~`, plain-space and `T` forms above), so no match is silently
  dropped or double-counted.
- The counter is byte-identical to the frozen one the round claims:
  `sha256(.ufo/waves/round-29/count-c1.py) = fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`,
  matching the spec. The counter does **not** reference `prereg-time-check.py` or `08:45`, so the
  mined-fix claim is outside C1's measured universe — it is a repair, not a C1 data row.
- The appended A1 correction is genuinely append-only: `git show 513eba3b:.ufo/waves/round-28/preregistration.json`
  still contains the original `~08:45Z` bytes, and the correction lives in `corpus/lessons/round-29.md`
  and `LOG.md`.

---

## 8. Commands the L1 should run after landing

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain
git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --cached --stat
python3 tools/prereg-time-check.py --selftest --scratch /tmp/ptc-selftest-postland
# expect: exit 0, 13 [PASS] lines, "SELFTEST PASS"
```

And re-check the three mutants against the landed tool (they must all be KILLED):

```
python3 tools/prereg-time-check.py --selftest --scratch /tmp/ptc-selftest-postland
# with the three one-line mutants applied (plain-space removed from TIME_RE;
# plain-space removed from parse_iso; parsed seconds forced to 0):
# expect exit 1 with
#   [FAIL] flag: space-separated seconds-precision time 7 s after commit: expect 1, got 0
```

---

## 9. Files and paths referenced

- Raw evidence preserved in this seat's directory (does not depend on `/tmp` surviving):
  `.ufo/waves/round-29/w2/out/kama-r29-w2-VerifyMistakeFix-6/evidence/`
  — `exit-code-summary.txt` (all exit codes), `r1.out`–`r5.out` (reproduced runs),
  `wt-selftest.out` / `committed-selftest.out` (self-test runs), and the five scripts
  (`verify.sh`, `harm.py`, `diffscan.py`, `mutants.py`, `mut2.sh`) that produced every number above.
- Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`
- Tool: `tools/prereg-time-check.py` (working tree `ab685ac2…`; committed `513eba3b` → `ca72edf2…`; pre-fix `75b78bb4` → `3d508f77…`)
- Receipts: `.ufo/waves/round-29/mined/{orig-75b78bb4,orig-selftest,patched-75b78bb4,patched-d8bf1804,patched-selftest,patched-selftest-v2,survivor-recheck}.out`
- Narrative: `LOG.md:1858`; `corpus/lessons/round-29.md:125`; `SCORECARD.md:1496`
- Mutant seat: `.ufo/waves/round-29/w1/advice/MutateTimeCheck.md`, `.ufo/waves/round-29/w1/out/MutateTimeCheck/`
- Counter: `.ufo/waves/round-29/count-c1.py` (sha256 `fe11d599…7383`)
- Scratch (this seat): `/tmp/kama-w2-VerifyMistakeFix/` — `clone/`, `tree-{75b78bb4,d8bf1804,513eba3b}/`,
  `verify.sh`, `harm.py`, `diffscan.py`, `mutants.py`, `mut2.sh`, `wt-selftest.out`, `committed-selftest.out`,
  `r1.out`–`r5.out`, `mut/`, `mut2/`, `scratch*/`

No tools were installed or updated for this seat (no `uv`/`npx`/binary installs, no `pacman`).
Python 3.14.8 and Git 2.56.0 already present were used as-is.
