# Row F02-report-invalid-utf8 — independent hand rebuild

**Verdict: HOLDS as graded; PARTIAL as a closed channel.**
(1) The fault premise is real and reproduces on the frozen arm: the committed
fleet report is byte-for-byte non-UTF-8 and the frozen auditor exits 1 with an
uncaught `UnicodeDecodeError` traceback (exit 1 is also the "failed" verdict
code, with empty stdout). (2) The graded expectation — exit 2, stderr
containing `output is not UTF-8` — is the right *kind* of outcome: the tool
cannot decode the only evidence artifact, and exit 2 is the only outcome among
{0,1,2} that neither fabricates a clean/failed verdict nor invents a defect
kind. It is, however, **over-pinned**: the pass condition matches a substring
of current's diagnostic, so a behaviorally identical refusal with reworded
stderr is scored NOT-MET (observed, §2). (3) The invalid-bytes read paths are
closed for crashes and flips, but two **ungraded near variants on the same
report-bytes channel still get a wrong verdict on current** (§3): a UTF-8 BOM
turns a clean report into `landed-section-missing` + `landed-omitted`
(exit 1), and a committed **symlink** at the report path is audited as if its
link-target string were the report — crafted, it yields a clean exit 0 on a
dangling link.

Base `245a37f69628c2c6bb29bbf17897d8fb5946c857`. Clone
`/tmp/kama-r23w2/RowF02ReportInvalid-2`, `rev-parse HEAD` verified equal.
Auditor blobs: current `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`
(= committed `tools/report-landing-audit.py`); frozen
`09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f` (extracted
from `4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`).
Runtime: git 2.56.0, CPython 3.14.8. No installs or upgrades were needed or
made.

## 1. Premise and frozen arm — observed

Rebuilt by hand from `tests/report-audit/repo-state-grid.py:226-231`
(`f_report_bytes`), **not** by importing the grid. Lane `master`: commit
`round-1: work` @1000, author `kama-shokunin`, on `f`. Fleet `HEAD`:
`.ufo/reports/round-1/kama.md` @2000 whose bytes are
`# kama round 1\n\n## Landed changes\n\n- <lc>\n\xff\xfe bad\n` (bad bytes
placed exactly where the builder puts them, after the Landed block). Row
declared at `:540`; reason at `:580`; pass condition at `:626-630`.

```
$ git -C fleet show HEAD:.ufo/reports/round-1/kama.md | tail -c 12
b'06a7\n\xff\xfe bad\n'      utf8-valid=False
```

Hand run, argv `--lane-repo lane --fleet-repo fleet --json --rounds 1 --no-errata`:

```
frozen  exit=1 traceback=True   stdout empty
        UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 78
        (raised inside subprocess._translate_newlines)
current exit=2 traceback=False  stdout empty
        could-not-evaluate: round 1: cannot read .ufo/reports/round-1/kama.md
        at fleet HEAD: git show HEAD:.ufo/reports/round-1/kama.md in <fleet>:
        output is not UTF-8: 'utf-8' codec can't decode byte 0xff in position 78
```

Same results without `--json`. Clean counterfactual (identical fixture minus
the two bad bytes): **both arms exit 0, `required=1`, `defects=[]`** — the
frozen failure is caused by the bad bytes, not by the fixture shape.

Grid cross-check on the clone (3 consecutive runs, identical each time):

```
$ python3 tests/report-audit/repo-state-grid.py --case F02-report-invalid-utf8 --arm both --json
frozen  F02-report-invalid-utf8 fault exit=1 tb=True  met=False
current F02-report-invalid-utf8 fault exit=2 tb=False met=True
```

Frozen cause: `git()` at frozen blob `:87-97` runs git with `text=True`
(`:90`), so decoding happens inside `subprocess.run`; `UnicodeDecodeError` is
a `ValueError`, while frozen `main` catches only `EvalError` (`:835`) and
`OSError` (`:838`) — the traceback escapes and exit 1 collides with the
"failed audit" code. Current cause: explicit strict decode at
`tools/report-landing-audit.py:122-126`, wrapped per-round at `:296-303`, and
`main` maps `EvalError` to exit 2 at `:909-911`.

Also observed, and not claimed by the grid: `f_report_bytes` performs **no**
premise check (no `require(...)` in `:226-231`), unlike e.g. `f_log_encoding`
at `:216-223`; the grid docstring at `:4-6` says each case verifies its
premise. The premise does hold — verified independently above — but this row
would not notice if `publish()` ever normalized the bytes.

## 2. Is the expected outcome the correct one? — yes in kind, over-pinned as a test

Evidence that exit 2 is the intended *policy*, not a coincidence:

- The tool's own exit contract, `tools/report-landing-audit.py:43-46`:
  `2 could-not-evaluate (missing/irregular report, unusable git or non-UTF-8
  git output, ...)` and `Errors are never verdicts.` A report the tool cannot
  decode is an irregular report, so 2 is the documented answer.
- The alternatives are worse: 0 asserts clean on bytes that were never read;
  1 requires choosing a defect kind, but `KINDS` is a closed set
  (`:79-81`) with no "unreadable report" member, so exit 1 would be a verdict
  fabricated over unread input. Refusal is the only non-fabricating outcome.
- Counterfactual (§1): removing only the bad bytes yields exit 0, so the
  refusal is caused by exactly the undecodable content and by nothing else.

Where the expectation is weaker than it looks:

- The pass condition is `reason.encode() in err` (`repo-state-grid.py:626-630`)
  with `reason = "output is not UTF-8"` (`:580`) — a substring of current's
  **diagnostic wording**, not part of the public contract (the contract fixes
  the exit code, not the sentence). Demonstrated with a wording-only mutant of
  the committed auditor (`output is not valid UTF-8 text: ...`, same exit 2,
  same EvalError path, no traceback):

  ```
  $ python3 tests/report-audit/repo-state-grid.py --case F02-report-invalid-utf8 \
        --arm current --current /tmp/kama-r23w2/f02/msg-mutant.py
  current F02-report-invalid-utf8 fault exit=2 kinds=None tb=0 exec=0 timeout=0 NOT-MET
  grid exit=1
  ```

  A clearer repair message therefore *breaks* this row even though behaviour
  is unchanged. [INFERENCE] The row grades current's phrasing plus the
  refusal; it does not grade the C1 property "must not crash/flip/hang".
- The row also pins the *policy* (refuse) rather than the property. A
  fail-open implementation that decoded with `surrogateescape` and still
  produced a correct 0/1 verdict for ASCII Landed sections would be NOT-MET.
  That is a defensible reading of C1 (no crash, no hang) but not what is
  graded here. I do not call the expectation wrong: refusing to certify a
  document you cannot read is the conservative, documented choice.

Control that the row does discriminate the real property: a lax-decoding
mutant (`.decode("utf-8", "replace")`, the M23-style change) returns
**exit 0, kinds=[]** and is NOT-MET (`grid exit=1`) — the row does catch a
lost refusal.

One fail-closed side effect, observed by inspection (not run as a row): the
`EvalError` is raised inside the per-round list comprehension (`:484`), so one
undecodable selected report aborts *all* selected rounds (exit 2, no partial
JSON). Consistent with "errors are never verdicts"; ungraded.

## 3. Near variants of the same channel that current still gets wrong — yes

All fixtures below were hand-built in fresh `/tmp` repos with
`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, explicit identity.
None of these rows exists in the grid (grep for `bom`, `feff`, `symlink`,
`120000` in `repo-state-grid.py` and `isolation-mutants.py`: no matches).

### 3a. UTF-8 BOM / U+FEFF before the Landed heading → false defects (same text-decode boundary)

Draft fixture (fleet HEAD has only a README commit, so the cutoff is "now";
the lane's round-1 commit @1000 is required). The only difference between the
two arms of the observation is three bytes:

```
$ # draft bytes: BOM + "## Landed changes\n\n- <lc>\n", --report 1=draft.md
current  exit=1  kinds=['landed-omitted', 'landed-section-missing']   (frozen identical)
$ # identical draft without the BOM
current  exit=0  kinds=[]                                            (frozen identical)
```

Committed variant confirms it is not a draft-only path: title line, then
`\xef\xbb\xbf## Landed changes` → `exit=1 kinds=['landed-omitted',
'landed-section-missing']`; the same bytes without the BOM → `exit=0
kinds=[]`.

Mechanism: `git()` decodes strict `utf-8`, not `utf-8-sig`
(`tools/report-landing-audit.py:122-126`), so the text begins with U+FEFF;
`landed_match` (`:168-169`) requires `^## Landed changes`, which cannot match
behind the zero-width character; `section is None` then emits
`landed-section-missing` and marks every pre-cutoff commit omitted
(`:333-345`).

Why I call it wrong rather than a format choice: the auditor's own selftest
accepts a draft whose first line is `## Landed changes` and expects `rc == 0`
(`:838-844`), so this document shape is supported; an editor saving
`utf-8-sig` produces exactly the BOM'd bytes. The verdict depends solely on an
encoding signature. Caveat: strict CommonMark also would not read
`U+FEFF##` as a heading, so "correct" is a policy judgment; the observed fact
is that a BOM alone flips 0 → 1 with two fabricated defects. Both arms behave
identically, so this is pre-existing, not a round-23 regression. [INFERENCE]
Repair: strip a leading U+FEFF after decode (or decode `utf-8-sig`); the
mid-file U+FEFF case needs its own decision.

### 3b. Non-regular committed report blob audited as the report (same read expression `git show HEAD:<rel>`)

The report path is read with `git(fleet_repo, "show", f"HEAD:{rel}")`
(`:296-303`) and only *decoded*; the tree mode is never checked. The tool
already refuses non-regular drafts (`stat.S_ISREG`, `:209-212`) and
non-regular SOURCES.md (`:250-255`, mode must be `100644`/`100755`), so the
committed report is the odd one out.

```
# s1: .ufo/reports/round-1/kama.md committed as a symlink (ls-tree: 120000 blob)
#     link target string = "## Landed changes\n\n- <lc>\n"; link dangles
$ git show HEAD:.ufo/reports/round-1/kama.md
b'## Landed changes\n\n- db796f8b820bf3825c58832419138cdba23206a7\n'
s1 current exit=0 kinds=[]        # clean verdict; frozen exit=0 as well
s2 regular blob, same bytes: exit=0 (indistinguishable)
# v8/v15: symlink with an ordinary target path
current exit=1 kinds=['landed-omitted', 'landed-section-missing']
# s3: gitlink (mode 160000) at the report path
current exit=2  fatal: bad object HEAD:.ufo/reports/round-1/kama.md
```

So a committed symlink is either a **false clean** (crafted target text that
parses as a report) or a **false-defect flip** (ordinary target path audited
as if it were the report), and the worktree link may not even resolve. Per
the tool's own contract the outcome should be exit 2 ("missing/irregular
report", `:43`). Same read path as F02; different byte-level trick. Both arms
identical → pre-existing. (Security impact is limited because whoever can
commit the report can commit a clean one; the issue is correctness of what
"the committed report" means.)

### 3c. Not claimed

- NUL bytes in a report are accepted (`exit=0`); NUL is valid UTF-8 and I
  found no wrong verdict from it, so this is not a fault claim, only a gap in
  the "is this a text document" notion.
- The invalid-UTF-8 channel itself is closed: draft bad bytes (exit 2),
  lane `corpus/SOURCES.md` bad bytes (exit 2), UTF-16 report (exit 2), bad
  bytes in the title, in the Landed citation line, or after `## Notes` (all
  exit 2 with the same reason). No invalid-bytes input reached a 0/1 verdict.

## 4. What current gets right on this channel (observed)

- Exact F02 fixture: exit 2, no traceback, pinned reason; deterministic over
  3 grid runs and repeated hand runs; identical under `--json` and text mode.
- Refusal is placement-independent (whole-file strict decode): bad bytes in
  the title, on a citation line, or after a later section all exit 2.
- Clean counterfactual: both arms exit 0.
- `surrogateescape` is used at only two sites (`:184` lane log,
  `:418` report path listing) and both are constrained: the lane-log fields
  are validated (`sha` `[0-9a-f]{40}`, `atime` `[0-9]{1,12}`, author exact
  ASCII equality, subject only prefix-matched) and only the SHA reaches the
  result document; the listing yields only `[0-9]+` round numbers. I found no
  invalid-bytes path that reaches a verdict.
- Errata read (`:371`) and draft read (`:209-215`) are strict and caught;
  bad bytes there are exit 2 (F16 mechanism).

## 5. Not verified

- The other 25 grid rows, the declared totals (frozen 0/26, current 26/26,
  8/8 controls, 0 tracebacks/executions/timeouts), `--selftest` 50/50, the
  rounds 10-22 ledger comparison, and the 24 mutants / M02 / M20 claims.
  Only F02 and my own mutants were run.
- No repair was implemented or tested; the BOM-strip and regular-blob-check
  directions are [INFERENCE] only.
- Only git 2.56.0 / CPython 3.14.8 on Linux; other versions and locales were
  not exercised (the declared floor is git >= 2.45).
- No hang or command-execution channel was exercised (out of this row).
- No network, no URLs cited.

## 6. Files written

- `.ufo/waves/round-23/falsify/advice/RowF02ReportInvalid.md` (this report)
- `.ufo/waves/round-23/falsify/out/RowF02ReportInvalid-2/hand_f02.py`
- `.ufo/waves/round-23/falsify/out/RowF02ReportInvalid-2/variants.py`
- `.ufo/waves/round-23/falsify/out/RowF02ReportInvalid-2/variants2.py`
- `.ufo/waves/round-23/falsify/out/RowF02ReportInvalid-2/variants3.py`
- `.ufo/waves/round-23/falsify/out/RowF02ReportInvalid-2/run.log`
- `.ufo/waves/round-23/falsify/out/RowF02ReportInvalid-2/grid-f02.json`
- `.ufo/waves/round-23/falsify/out/RowF02ReportInvalid-2/msg-mutant-grid.txt`
- `.ufo/waves/round-23/falsify/out/RowF02ReportInvalid-2/lax-mutant-grid.txt`
- `.ufo/waves/round-23/falsify/out/RowF02ReportInvalid-2/frozen-audit-4fe9339.py`
  (sha256 `09ecd63b…`)
- scratch outside the lane: `/tmp/kama-r23w2/RowF02ReportInvalid-2` (clone),
  `/tmp/kama-r23w2/f02/` (hand fixtures, mutants, logs)

No tracked lane file, index, `.jj`, sibling lane, fleet root, global config or
`~/.omp` was written; no commits, pushes or jj commands; no pacman.

## 7. Citation corrections (appended after write)

Three `path:line` anchors above were off by a few lines at
`245a37f6`; the observations and conclusions are unchanged:
`KINDS` is at `tools/report-landing-audit.py:78-79` (not `:79-81`); the
per-round `audit_round` list comprehension is at `:480` (not `:484`); the
section-missing defect is appended at `:320-322` and the omission loop runs
`:332-337` (the range `:333-345` named both in one span). All other anchors
were re-read and match.
