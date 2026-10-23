# VerifyLogFreshness — kama round 29 attempt 2, wave w2

Seat: `VerifyLogFreshness` (kama w2). Read-only on the lane except this report and its evidence
directory. No tools installed. No `pacman`. No lane git index writes, no `git add/commit/checkout`,
no `git worktree add` on the lane. Scratch: `/tmp/kama-r29-w2-VerifyLogFreshness-14/` only.

Item: run the two re-verification commands the LOG entry claims, plus
`report-landing-audit --help` / `--selftest`.

## Verdict

**PASS on the exit codes, with one number in the LOG entry that is off by one relative to the
task's expectation, and one path in the LOG entry that is stale relative to the landed tip.**

| Check | Result |
|---|---|
| `tools/prereg-time-check.py --selftest` exit code | **0** (PASS) |
| `tools/prereg-time-check.py --selftest` printed `[FAIL]` lines | **0** |
| `tools/prereg-time-check.py --selftest` printed `[PASS]` **case** lines | **13** (not 15) |
| `tools/prereg-time-check.py --selftest` stdout lines containing the substring `PASS` | **14** (13 `[PASS]` case lines + the `SELFTEST PASS` aggregate line) |
| `tools/citation-provenance.py --selftest` stdout | `selftest: ok (24 cases)` |
| `tools/citation-provenance.py --selftest` exit code | **0** (PASS) |
| `tools/citation-provenance.py --selftest` stderr | one expected line: `citation-provenance: cannot read /tmp/citation-provenance-pae6lsuf/lane/absent.md: [Errno 2] ...` — from the deliberate unreadable-doc case; process still exits 0 |
| `tools/report-landing-audit.py --help` exit code | **0**; prints the usage block (options `--lane-repo --fleet-repo --branch --lane --rounds --report --errata --no-errata --json --selftest`) |
| `tools/report-landing-audit.py --selftest` exit code | **0**; prints `selftest cases=79 failed=0` |

The assignment expected "15 PASS exit 0". **15 is not reachable at any revision of the tool.**
The working-tree/landed tool prints 13 `[PASS]` case lines; the pre-patch tool prints 10. The
number 14 (PASS-mentioning lines) and 13 (case lines) are the only two counts the tool can
produce. The landed LOG entry already uses the exact phrasing that avoids the ambiguity.

## 1. The re-verification command the LOG entry names

LOG.md:1859-1862 (landed tip `6de225c289b7682bf280cffb4a07de3fb7d1275c`, still the narrative
content at the later tip `7f595a3bf8027e5e48cac3634e79990df513c7ab`):

```
Re-verification (freshness): `tools/prereg-time-check.py --selftest` 13 cases PASS plus the
SELFTEST PASS aggregate line, exit 0 (working-tree tool, seat-unique /tmp scratch);
ScoutHeldRules re-ran citation-provenance, report-landing-audit and sources-append-only self-tests,
all exit 0.
```

Commands run (all from `/home/vgpnk/Projects/shokunin/kama-shokunin`, scratch under `/tmp`):

```
$ /usr/bin/python3 tools/prereg-time-check.py --selftest --scratch /tmp/kama-r29-w2-VerifyLogFreshness-14/scratch
... exit 0
$ /usr/bin/python3 tools/citation-provenance.py --selftest
selftest: ok (24 cases)                                            # exit 0
$ /usr/bin/python3 tools/report-landing-audit.py --selftest
selftest cases=79 failed=0                                         # exit 0
$ /usr/bin/python3 tools/report-landing-audit.py --help
usage: report-landing-audit.py [-h] [--lane-repo LANE_REPO] ...   # exit 0
```

Full stdout/stderr captured under `evidence/` in this directory:
`prereg-time-check.selftest.out/.err`, `citation-provenance.selftest.out/.err`,
`report-landing-audit.selftest.out/.err`, `report-landing-audit.help.out`, `exits.txt`.

### 1a. The count is 13 case lines, not 15 — and the "14" in the earlier attempt-1 wording was a line count, not a case count

The attempt-1 attempt's LOG wording (uncommitted, seen at 15:33 local) was:

```
Re-verification (freshness): `tools/prereg-time-check.py --selftest` 14 PASS exit 0;
```

Measured across the three tool revisions:

| tool revision | `[PASS]` case lines | stdout lines containing `PASS` | `[FAIL]` lines |
|---|---:|---:|---:|
| `35b90184` (pre-patch) | 10 | 11 | 0 |
| `513eba3b` (patched, mined fix committed) | 12 | 13 | 0 |
| landed tip `6de225c` / working tree (11 `case()` calls + 2 error cases) | **13** | **14** | 0 |

So "14 PASS" was a count of *stdout lines containing the string `PASS`* (13 `[PASS]` case lines
plus the final `SELFTEST PASS` aggregate line), not 14 passing cases. The landed entry at
LOG.md:1859-1860 replaced it with "13 cases PASS plus the `SELFTEST PASS` aggregate line", which
is unambiguous and matches what I measured. **The 15 in the assignment brief matches no revision
of the tool and appears to be an arithmetic slip in the dispatch text, not a lane defect.**

Evidence for the 13/14 split, from the tool's own case list at the landed tip
(`tools/prereg-time-check.py`, 11 `case(...)` calls at lines 191-212 plus two non-case checks
printed as `[PASS] missing path` and `[PASS] bad revision` at lines 214-224):

```
$ git show HEAD:tools/prereg-time-check.py | grep -c '^\s*case('
11
$ grep -c '^\[PASS\]' evidence/prereg-time-check.selftest.out
13
$ grep -c 'PASS' evidence/prereg-time-check.selftest.out
14
```

### 1b. The receipt the LOG cites reproduces byte-for-byte

The landed receipt `.ufo/waves/round-29/mined/patched-selftest-v2.out` (61 lines) vs my live run
at the same tip:

```
$ diff <(grep -v 'selftest repo:' evidence/prereg-time-check.selftest.out) \
       <(grep -v 'selftest repo:' .ufo/waves/round-29/mined/patched-selftest-v2.out)
59a60
> exit=0
```

The only difference is the receipt's trailing `exit=0` line, which the lane's other mined
receipts also carry (`orig-selftest.out`, `patched-selftest.out`, `orig-75b78bb4.out` all end
with `exit=0`). The 60 stdout lines are identical, and the per-line `[PASS]`/`[FAIL]` verdicts
match. A copy of that committed receipt is in `evidence/committed-receipt-patched-selftest-v2.out`.

### 1c. The other three self-tests the LOG entry attributes to ScoutHeldRules

The LOG line claims "ScoutHeldRules re-ran citation-provenance, report-landing-audit and
sources-append-only self-tests, all exit 0". I re-ran all three independently (not relying on
ScoutHeldRules' receipt):

```
$ /usr/bin/python3 tools/citation-provenance.py --selftest
selftest: ok (24 cases)                                            # exit 0
$ /usr/bin/python3 tools/report-landing-audit.py --selftest
selftest cases=79 failed=0                                         # exit 0
$ /usr/bin/python3 tools/sources-append-only.py --selftest
42/42 selftest cases passed                                        # exit 0
```

All three exit 0, as claimed. `sources-append-only.py --selftest` prints `42/42 selftest cases
passed` and writes no files.

## 2. One defect in the landed LOG entry: the re-verification line names a stale tool state

LOG.md:1860 says the selftest was run against the "**working-tree tool**". At the landed tip the
tool is **committed** — the working tree and `HEAD` are byte-identical:

```
$ git diff HEAD -- tools/prereg-time-check.py | wc -l
0
$ sha256sum tools/prereg-time-check.py
53c8fc742e7f84e546b58d24667e3972dda90240b9fb8449c42ecb5eaaaff498
$ git show HEAD:tools/prereg-time-check.py | sha256sum
53c8fc742e7f84e546b58d24667e3972dda90240b9fb8449c42ecb5eaaaff498
```

The "working-tree tool" qualifier was true when the line was drafted (the tool diff was
uncommitted then) and became stale when the L1 committed it in `6de225c`. It is a wording
staleness, not a false exit code — the count (13 cases) and the exit (0) are correct for the
committed tool too, which I re-verified at the landed tip with the byte-identical tool.

**Suggested fix (L1 only):** drop "working-tree tool" and the scratch parenthetical, or write
"committed tool at `6de225c`". The `(working-tree tool, seat-unique /tmp scratch)` clause also
mixes a provenance claim with a process note in a claim sentence.

## 3. Two independent attacks on the mined-mistake fix (beyond the item, in scope as "verify")

The LOG entry's mined-mistake sentence is: "`tools/prereg-time-check.py` now reads
`YYYY-MM-DD ~HH:MMZ` / `YYYY-MM-DD HH:MMZ` (was blind to the round-28 A1 text; now flags it,
exit 1)". I attacked this claim directly rather than taking the receipts for it.

### 3a. The A1 form is now detected; the pre-patch tool was blind to it

At the *patched* tool (`513eba3b`) against the round-28 preregistration at `75b78bb4`:

```
$ /usr/bin/python3 <513eba3b:tools/prereg-time-check.py> --repo . \
    --path .ufo/waves/round-28/preregistration.json --rev 75b78bb4900aae1edcdb6b229bb8c572c20fcbce --strict
  FLAG line 41: 2026-10-23 ~08:45Z (later than commit by 404s)
RESULT fail: 1 timestamp(s) later than the committer time          # exit 1
```

At the *pre-patch* tool (`35b90184`), same arguments:

```
  no ISO-8601 UTC timestamps found
RESULT pass: no timestamp later than the committer time            # exit 0
```

So the fix is real and it is the difference between exit 1 and exit 0 on the historical A1 text.
The control revision `d8bf1804` still passes (exit 0, "no ISO-8601 UTC timestamps found") on the
patched tool, so the fix did not simply start flagging everything.

### 3b. The added 7-second selftest case actually kills the mutants the wave-1 report said survived

`.ufo/waves/round-29/w1/out/MutateTimeCheck/mutants.md` reported three survivors (M02/M05
plain-space removed, M07 seconds discarded) and the landed `mined/survivor-recheck.out` claims
the added 7-second case kills them. I rebuilt four of those mutants against the landed tool in
`/tmp` and ran the selftest on each:

| mutant | mutation | selftest result |
|---|---|---|
| `mut_nospace.py` | `TIME_RE` loses the plain-space alternative `(?:T\| ~\| )` → `(?:T\| ~)` | **killed** — `[FAIL] flag: space-separated seconds-precision time 7 s after commit: expect 1, got 0`, `SELFTEST FAIL`, exit 1 |
| `mut_noseconds.py` | `TIME_RE` loses `(?::\d{2})?` | **killed** — 3 `[FAIL]` lines incl. the 7-second case, exit 1 |
| `mut_M05_parse_nospace.py` | `parse_iso` regex loses the plain-space alternative | **killed** — the 7-second case `[FAIL]`, exit 1 |
| `mut_M07_parse_noseconds.py` | `parse_iso` discards seconds (`datetime(y, mo, d, h, mi, 0, ...)`) | **killed** — the 7-second case `[FAIL]`, exit 1 |

The added case is therefore load-bearing, not decorative: removing either the plain-space form or
the seconds precision from either the matcher or the parser now fails the selftest. This
corroborates `mined/survivor-recheck.out` independently.

## 4. Freshness of the receipt the LOG entry cites for C1

LOG.md:1841 cites `.ufo/waves/round-29/final/c1-513eba3b.out` for "fresh-clone receipt
`unresolved 0 met True`". I re-ran the frozen counter (sha256 `fe11d599…7383`, unchanged) against
a **fresh clone of the lane remote** at the pushed tip and at the measured commit:

```
$ git clone -q https://github.com/VeigaPunk/kama-shokunin.git /tmp/.../clone-remote
$ git rev-parse master
49f849f292c338f5e4e2cc8a60eb1372a8f40412
$ /usr/bin/python3 .ufo/waves/round-29/count-c1.py --repo /tmp/.../clone-remote \
    --tip refs/heads/master --out /tmp/.../c1-at-pushed-master.json
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 49f849f292c3
```

Identical to the cited receipt line, and `met True` still holds at the **pushed** master tip
`49f849f2` (which is one commit past the measured `513eba3b`):

```
$ git merge-base --is-ancestor 513eba3b origin/master   # exit 0 (YES_ANCESTOR)
$ git ls-remote origin master
49f849f292c338f5e4e2cc8a60eb1372a8f40412	refs/heads/master
```

Counter bytes in the fresh remote clone are identical (`fe11d599…7383`). A separate local clone
pinned to `513eba3b` reproduces the same line. Also verified: `git show 827d1365:.ufo/waves/round-29/count-c1.py | sha256sum`
= `fe11d599…7383`, i.e. the counter was not edited between the freeze and the tip.

## 5. `report-landing-audit` beyond `--help`/`--selftest`

The item said "or its selftest if present"; both were run. The full (non-selftest) audit is worth
recording because the LOG entry's neighbourhood depends on it:

* `--rounds 29` against the fleet repo: `round=29 required=3 post_report=0 defects=0 …
  status=clean`, **exit 0**. The fleet round-29 kama report now exists
  (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-29/kama.md`, fleet commit `9596e03`).
* Full audit over rounds 10-: **exit 1**, `status=failed`, `defects=10 corrected=9 uncorrected=1`.
  The single uncorrected defect is **round 27**, `landed-unresolved 49491b80` — the fleet's
  round-27 report cites the counter sha prefix `49491b80…2765` inside a `## Landed changes`
  section. **This is a pre-existing round-27 condition, not round-29**; no round-29 defect is
  present (`--rounds 29` is clean). It is flagged here only so the L1 knows the whole-history
  audit is red for a reason outside this round.

## 6. Other claims in the same LOG entry, spot-checked

| Claim (LOG.md) | Check | Result |
|---|---|---|
| "69 statements of six classes" | `final/c1-513eba3b.json` `by_class` sums to 69 over C/H/N/P/Q/T | **PASS** |
| "11 were false at writing (4 pointers, 7 quoted outputs)" | mismatch class histogram from the same JSON: `{'Q': 7, 'P': 4}` = 11 | **PASS** |
| "14 control seats scored before any data (`35b90184`): no control meets `unresolved == 0`" | `controls/call.json` `tasks` length = 14 (13 `Ctl*` + `RefPaste`); of the 13 `Ctl*` counters none has `unresolved 0`; `RefPaste` (the reference policy, not a control) is the one with `unresolved 0 met True` | **PASS** — the wording "no control meets `unresolved == 0`" is correct because RefPaste is not a control; the lesson (`corpus/lessons/round-29.md:25-28`) states the same distinction explicitly |
| "census 173 → 177 rows, exit 0" | `git show 2aa46e24:corpus/SOURCES.md \| grep -c '^| S'` = 173; tip = 177; `scripts/sources-census.sh validate --root … kama` exit 0, stdout 84 lines (1 `ok` + 83 `W04`), stderr 0 bytes | **PASS** |
| "Sources S174-S177 … opened this round" | 4 rows added to `corpus/SOURCES.md`, ids S174–S177 | **PASS** |
| "Re-verification (freshness)" census claim in the same paragraph | re-ran the census script: exit 0 | **PASS** |

## 7. Lane-state event observed during this seat (reported, not acted on)

While this seat was running, the lane working tree was reset and re-landing happened under me:

* At ~15:41 the working tree carried the attempt-1 leftovers (modified `LOG.md`, `SCORECARD.md`,
  `SHONEN.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md`, `tools/prereg-time-check.py`; untracked
  `.ufo/waves/round-29/{final,mined,w1}`, `corpus/knowledge/self-assessment-at-writing.md`,
  `corpus/lessons/round-29.md`) — the artifacts this item was asked to verify.
* At ~15:52 that working tree was replaced: `git status` went clean, `HEAD` moved to `49f849f2`,
  and `.ufo/waves/round-29/w2/` (including this seat's own output directory) disappeared from the
  filesystem. The content was not lost — it survives in the lane's jj history as commits
  `04e4c5d6f31c` (child of `513eba3b`, holding `final/`, `w1/`, `w2/` with 234 `w2` paths
  including this seat's `out/VerifyLogFreshness/evidence/*`) and `eef70399c161` (child of
  `49f849f2`, holding the narrative diff).
* By ~16:07 the L1 landed the integration: lane tip `6de225c289b7682bf280cffb4a07de3fb7d1275c`
  ("round-29 attempt 2: verification wave w2 (64 seats, orchestrator-dispatched) integration;
  narrative, verbatim repairs, wave evidence, lesson/knowledge/SOURCES landing"), with a
  follow-up evidence commit `227dd1e` carrying `final/c1-6de225c2.out/.json`.

**All measurements in this report were re-taken against the landed tip `6de225c`**, and the
numbers reported above are the landed-tip numbers. The earlier pre-reset numbers are reported
only where the difference is itself the finding (§1a table, which spans tool revisions, not tree
states). No lane file was modified by this seat; the L1 remains the single integrator.

A follow-up L1 commit `7f595a3` ("round-29 attempt 2: late-arriving VerifyLogFreshness seat
evidence (all re-verification selftests exit 0)") picked up this seat's `evidence/` directory. I
re-ran all four commands once more at that tip: `prereg-time-check --selftest` exit 0 with 13
`[PASS]` case lines and 0 `[FAIL]`, `citation-provenance --selftest` exit 0, `report-landing-audit
--selftest` exit 0, `report-landing-audit --help` exit 0 — unchanged from the `6de225c` run. The
narrative text under verification (LOG.md:1859-1862) is unchanged by that commit.

Two scratch-hygiene notes, disclosed:

* Several `--selftest` invocations I ran **before** the steering correction arrived used the
  tool's default `--scratch /fast/scratch/hyaku/kama-r26/ExecPreregTimeCheck`, which creates a
  persistent scratch repo per run. That path now holds 16 `ptc-selftest-*` directories, 13 of them
  created during this wave (15:00 local or later); sibling seats ran the same tool concurrently,
  so the split between mine and theirs is not separately attributable. The fleet round-29 report
  already discloses one such residue (`ptc-selftest-ywq_7og0`) from a sibling seat. I did **not**
  delete anything outside my seat's `/tmp` directory, per my bounds. After the correction every
  run used `--scratch /tmp/kama-r29-w2-VerifyLogFreshness-14/scratch`.
* The lane was reset mid-seat, so the `w2/` tree this report lives in was briefly absent; the
  report was rewritten against the landed tip.

## 8. Summary for the L1

1. **Both re-verification commands the LOG entry names pass.** `prereg-time-check.py --selftest`
   exit 0, 0 `[FAIL]`, 13 `[PASS]` cases + the aggregate line; `citation-provenance.py --selftest`
   exit 0 printing `selftest: ok (24 cases)`. `report-landing-audit.py --help` exit 0 and
   `--selftest` exit 0 (`selftest cases=79 failed=0`). The third self-test the entry names
   (`sources-append-only.py --selftest`, `42/42`) also exits 0.
2. **The "15 PASS" in the dispatch brief is unreachable** at every tool revision (10 / 12 / 13
   case lines). The landed LOG wording ("13 cases PASS plus the `SELFTEST PASS` aggregate line")
   is the correct one; no narrative change is needed for the count.
3. **One stale clause to fix:** LOG.md:1860's "working-tree tool" — the tool is committed at the
   tip and byte-identical (`53c8fc74…`). Rewrite as "committed tool at `6de225c`" or drop the
   parenthetical.
4. **The mined-mistake fix is independently confirmed** on both axes the LOG claims: the A1
   `~08:45Z` text flips exit 0 → exit 1 across the patch, the `d8bf1804` control still passes, and
   the added 7-second selftest case kills all four mutant shapes I rebuilt (plain-space and
   seconds-precision, in both the matcher and the parser).
5. **C1's receipt is fresh:** the frozen counter re-run in a fresh clone of the lane remote at the
   pushed tip `49f849f2` prints the identical line and `met True`; the counter bytes are unchanged
   since the freeze.
6. **Not a round-29 defect, but the L1 should know:** the whole-history `report-landing-audit` run
   exits 1 with one uncorrected round-27 defect (`landed-unresolved 49491b80`). `--rounds 29` is
   clean.

## Evidence index (all paths absolute)

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/VerifyLogFreshness/report.md` — this report
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/VerifyLogFreshness/evidence/exits.txt`
* `…/evidence/prereg-time-check.selftest.out` / `.err` — 60 stdout lines, stderr empty
* `…/evidence/citation-provenance.selftest.out` / `.err` — `selftest: ok (24 cases)` + the expected stderr line
* `…/evidence/report-landing-audit.selftest.out` / `.err` — `selftest cases=79 failed=0`
* `…/evidence/report-landing-audit.help.out` — usage block
* `…/evidence/committed-receipt-patched-selftest-v2.out` — copy of the committed mined receipt
* `…/evidence/lane-tip.txt` — lane tip at the last re-run: `7f595a3bf8027e5e48cac3634e79990df513c7ab`
  ("round-29 attempt 2: late-arriving VerifyLogFreshness seat evidence"); the narrative under
  verification is the `6de225c` attempt-2 integration commit, unchanged by that follow-up
* `…/evidence/LOG.reverification-lines.txt`, `…/evidence/LOG.round29-section.txt` — the LOG text under verification
* Lane tool under test: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/prereg-time-check.py`
  (sha256 `53c8fc742e7f84e546b58d24667e3972dda90240b9fb8449c42ecb5eaaaff498` at the landed tip)
* Mutants and scratch clones: `/tmp/kama-r29-w2-VerifyLogFreshness-14/` — left in place for the L1
  to inspect; nothing outside it was created, modified or deleted

## Tooling

None installed. No `pacman` (host-wide pacman pause respected). Only pre-existing `git`, `bash`,
`awk`, `grep`, `python3`, and `find` were used; `timeout` was used for the fleet-side runs.
