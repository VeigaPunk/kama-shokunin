# Row F26-huge-author-timestamp — independent hand rebuild

**Verdict: PARTIAL — premise holds, graded outcome is defensible but not
principled, and current still mis-handles near variants of the same channel.**
The fault premise is real and reproduces on the frozen arm by hand (exit 1,
`ValueError` traceback). The graded expectation (exit 2,
`unexpected git log record`) is *permissible* under C1, because the object is
fsck-invalid (`badDateOverflow`) and no verdict was asserted. But it is not
the uniquely correct outcome (git normalises that date to 0, which yields the
substantive `landed-omitted` verdict), and the row's safety credit is not
attributable to the timestamp check at all: with that check removed (mutant
M25) current still exits 2 through the catch-all. Over-refusals remain:
a git-valid 13-digit date (fsck-clean) is refused (current 2 where frozen and
the correct verdict are 0), and a huge date on a non-round/other-author
commit is refused before the population filter (current 2, frozen 0).

Base `245a37f69628c2c6bb29bbf17897d8fb5946c857`. Clone
`/tmp/kama-r23w2/RowF26HugeAuthor`, `rev-parse HEAD` verified equal. Auditor
blobs: frozen `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`
(extracted from `4fe9339f…:tools/report-landing-audit.py`), current
`f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`. Runtime:
git 2.56.0, CPython 3.14.8. No installs or upgrades were needed or made. No
`lsp` device exists in this seat's toolset; `read`/`grep` (literal search) and
direct subprocess observation were used instead.

## 1. Premise and frozen arm — observed

Fixture rebuilt by hand from `tests/report-audit/repo-state-grid.py:466-478`
(`f_huge_timestamp`; row at `:569`, pinned reason at `:590`), **not** by
importing the grid: lane `master` `round-1: work` @1000 (cited), fleet
`HEAD` report `.ufo/reports/round-1/kama.md` @2000 citing it, then a raw
commit `hash-object --literally` with parent = cited commit, author
`kama-shokunin`, author field `'9'*5000`, committer 1100, subject
`round-1: overflow`.

Observed in the hand-built repo:

```
git log -z --format=%H%x00%an%x00%at%x00%s master
  record 0: 19e7c11c…  kama-shokunin  9999…(5000 digits)  round-1: overflow
  record 1: 3632c9da…  fixture        1000                 round-1: work
git fsck --no-dangling  → rc=1
  error in commit 19e7c11c…: badDateOverflow: invalid author/committer
  line - date causes integer overflow
git log -1 --format=%at HEAD            → the 5000 raw digits
git log -1 --date=unix --format=%ad HEAD → 0
git log -1 --format=%ct HEAD            → 1100
```

Hand runs (`--lane-repo … --fleet-repo … --json --rounds 1 --no-errata`):

| arm | exit | observed |
|---|---|---|
| frozen | **1** | traceback `ValueError: Exceeds the limit (4300 digits) for integer string conversion: value has 5000 digits`, raised at blob line 161 `int(atime)` (frozen shape check is `[0-9]+`, so it passes the 5000 digits and converts only because author/subject matched) |
| current | **2** | `could-not-evaluate: unexpected git log record '19e7c11c…' '9999…'` — pinned reason matched |

Grid row itself, in the clone:
`python3 tests/report-audit/repo-state-grid.py --arm both --case F26-huge-author-timestamp`
→ `frozen … exit=1 kinds=unparseable tb=1 NOT-MET`,
`current … exit=2 kinds=None tb=0 met`, grid exit 1 (frozen arm). The L1's
claimed frozen-arm premise for this row is reproduced independently. No hang,
no program execution (`exec=0`; builder supplies no marker), no timeout.

## 2. Is the expected outcome correct?

Refusal (exit 2) is **defensible**: `git fsck` declares the author line
invalid (`badDateOverflow`), so asserting which round commits precede the
fleet cutoff from a corrupt object is guesswork; the tool's documented policy
is "Errors are never verdicts" (`tools/report-landing-audit.py:84-85`,
`:909-924`). Under the four named C1 harms (exit-1 traceback, flip, hang,
program execution) exit 2 passes.

But it is not uniquely correct, and the grid over-pins it:

- Git itself normalises the same commit to date **0** (`%ad` with
  `--date=unix` above), which is `<= cutoff 2000`; the commit is author
  `kama-shokunin`, subject `round-1: overflow`, uncited. An implementation
  using the normalised date would emit the substantively true
  `landed-omitted` (exit 1) and be graded **NOT-MET**, although it violates
  no C1 harm. The pinned reason at `:590` therefore encodes one conservative
  reading, not the correctness property. Counterfactual observed: the same
  hand fixture with the raw author date replaced by `0` (git's normalised
  value) gives current **exit 1, defects `['landed-omitted']`**, no stderr.
- Current does not implement the rationale it would need for that reading.
  The check is a **digit-count cap**, not git validity:
  `tools/report-landing-audit.py:195` (`re.fullmatch(r"[0-9]{1,12}", atime)`).
  A zero-padded date (`000000000001`, also fsck "invalid author/committer
  line - zero-padded date") passes that cap and gets a verdict (exit 1,
  `landed-omitted`, observed both arms). So "fsck-invalid ⇒ refuse" is not
  the rule in force.
- The timestamp check is not load-bearing for the fault. Mutant
  `M25-timestamp-shape` (regex weakened to `[0-9]+`) on the same hand fixture
  still gives **exit 2** — through the catch-all:
  `could-not-evaluate: internal: ValueError: ValueError('Exceeds the limit
  (4300 digits)…')`. `python3 tests/report-audit/isolation-mutants.py
  --only M25-timestamp-shape --json` reports `killed: true`,
  `failed_rows: ["F26-huge-author-timestamp"]`, but the kill is only a
  pinned-reason mismatch; crash/flip/hang/exec are unchanged from current.
  The "22 killed" count therefore includes a purely cosmetic kill, and F26
  does not by itself evidence timestamp-channel closure.

## 3. Near variants of the same channel that current still gets wrong

All fixtures hand-built as above; table is observed exits
(`fsck` = `git fsck --no-dangling` on lane where the raw commit lives).

| variant | git fsck | frozen | current | correct |
|---|---|---|---|---|
| V0 same as row: 5000-digit author date, lane author, `round-1:` | badDateOverflow | 1 (traceback) | 2 (`unexpected git log record`) | refusal defensible |
| **V1 13-digit author date `9999999999999`, lane author, `round-1:`** | **clean (rc 0)** | **0** | **2 `unexpected git log record`** | **0** |
| V2 12-digit author date `999999999999`, same | clean | 0 | 0 | 0 |
| **V3 5000-digit author date, author `someone`, subject `note: decoration`** | badDateOverflow | **0** | **2 `unexpected git log record`** | **0** |
| V4 huge committer date only (author 1100) | badDateOverflow | 1 `landed-omitted` | 1 `landed-omitted` | not a timestamp-channel fault |
| V5 zero-padded `000000000001`, lane author, `round-1:` | zeroPaddedDate | 1 `landed-omitted` | 1 `landed-omitted` | substantive omission; inconsistent with refusal reading |
| **V6 huge author date on the fleet report commit instead** | badDateOverflow (fleet) | **1 (traceback)** | **2 `internal: ValueError`** | 0 (normalised cutoff 0, cited lane commit @1000 is post) |

- **V1 is the clearest miss.** `9999999999999` is a valid git timestamp
  (`git fsck` clean, `%at` and `%ad` both render it), the commit is
  post-cutoff so not required, and the report cites the only pre-report
  round commit: the correct verdict is 0. Frozen returns 0; current refuses
  with exit 2 because `{1,12}` rejects any 13+ digit value. This is a
  false refusal of valid repository state, and it is not among the declared
  tradeoffs (only shallow/partial clones and git >= 2.45 are declared). A
  uintmax-sized bound (`{1,19}`/`{1,20}`) or comparing lengths before `int`
  would keep V0's refusal without V1's.
- **V3** shows the validation moved ahead of the author/subject filter:
  frozen validates the field shape only (`[0-9]+`) and never converts an
  atime for a non-matching record, so it returns the correct 0; current
  refuses the whole lane because a decorative commit has a long date. Any
  lane whose history contains a huge-date unrelated commit becomes
  unauditable.
- **V6** shows the fleet half of "audited repos" has no timestamp handling:
  the report commit's date goes through `report_cutoff` → `int(out[-1])`
  (`tools/report-landing-audit.py:203-206`), and the only reason current
  returns exit 2 is the generic catch-all (`:918-924`, message
  `internal: ValueError`, no pinned reason); frozen crashes at the same
  site. Safe-by-catch-all, not by a timestamp rule.

V4/V5 are recorded as **not** falsifiers: a huge committer date never reaches
the auditor's date logic, and a zero-padded date yields the same substantive
omission both arms already gave.

## 4. What was NOT verified

- Only F26 of the grid was run (`--case`), not the 26-fault/8-control
  population or the L1's 26/26, 0-traceback totals.
- Only mutant M25 was run; M24 (catch-all) was not exercised against V6.
- No test of 14–19-digit bounds or the 20-digit uintmax edge; no test of
  timezone-field corruption, errata round-number digits, or `--rounds` beyond
  the existing F24 row.
- No LSP: no `lsp` device is mounted for this seat; definition/caller tracing
  was text-level `read`/`grep`, not semantic.
- No program-execution marker exists in F26's builder, so "cannot run
  programs" is vacuous for this row (I confirmed the builder returns no
  marker; the row's `executed` field is always false).

## 5. Files written

- This report:
  `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/RowF26HugeAuthor.md`
- Clone `/tmp/kama-r23w2/RowF26HugeAuthor` (HEAD `245a37f6…`; no tracked
  file modified, no commits, no jj commands).
- `/tmp/frozen-audit-F26.py` (frozen blob copy),
  `/tmp/aud-m25.py` (M25 mutant for the hand fixture).
- Scratch fixtures: `/tmp/f26-hand/`, `/tmp/f26-scan/`, `/tmp/f26-var/*`
  (V0–V6), `/tmp/f26-nul/` (NUL-in-author probe: NUL in the author name
  empties `%an`/`%at` rather than shifting fields; current refuses on the
  empty atime, so the NUL channel does not shift this record format).
- No lane tracked file, index, `.jj`, sibling lane, domain source, or global
  config was written.
