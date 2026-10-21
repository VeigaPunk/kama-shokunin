# F16-errata-invalid-utf8 — falsify

**Verdict: HOLDS.** The fault premise is real and reproduces exactly in the
frozen arm; the grid's expected outcome (exit 2, stderr contains
`output is not UTF-8`) is the correct, contract-grounded outcome, not merely
what current happens to do. One near variant of the same errata read path is
still misclassified by current: a 7–39-hex ledger `correction` that collides
with a repository-local tag/branch name yields exit 2
`citation ... names a ref` where the errata contract says the row is
`errata-invalid` (exit 1). That variant is not F16's row; it is an unlisted
gap in the same file/read path (finding F16-N1, confidence high on
observation, medium on which outcome is normative).

Lane HEAD `245a37f69628c2c6bb29bbf17897d8fb5946c857`. Frozen blob
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`
(sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`),
current `tools/report-landing-audit.py` (sha256
`f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`). Both
hashes equal the grid's own `auditor_sha256` output. Environment: git 2.56.0,
Python 3.14.8. No tools installed (nothing to record). All current-arm runs
used the clone's committed `tools/report-landing-audit.py` (clone working
tree clean at `245a37f6`); the shared lane checkout acquired sibling
working-tree edits during this run and was not used for any arm.

## Method (independent of the grid)

* Clone `git clone --no-hardlinks <lane> /tmp/kama-r23w2/CloseKama22.RowF16ErrataInvalid-2`;
  `git -C … rev-parse HEAD` → `245a37f6…`, as required.
* Frozen arm extracted with
  `git -C <clone> cat-file blob 4fe9339f…:tools/report-landing-audit.py > /tmp/kama-r23w2/frozen-audit.py`.
* Fixtures rebuilt **by hand** (no import of `repo-state-grid.py`) in fresh
  `/tmp` repos with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`,
  explicit identity, no network. Reproducers:
  `/tmp/kama-r23w2/RowF16-variants.py` and `/tmp/kama-r23w2/RowF16-refcorr.py`.
* Fixture-equivalence check: my builder produced the same object ids as the
  grid's own case run — lane round-1 commit
  `db796f8b820bf3825c58832419138cdba23206a7`, ledger tip
  `043ff9dc2bc8aa6cdfc83cf90e51f1cb79c12f65`; the grid's current-arm stderr
  names the same tip suffix `…fc83cf90e51f1cb79c12f65:registry/report-landing-errata.tsv`.
  The fixture semantics (author `fixture`, @1600, bytes `# \xff bad\n`) are
  therefore reproduced bit-for-bit.

Grid's builder/expectation at HEAD:
`tests/report-audit/repo-state-grid.py:398-402` (`f_errata_bytes`), row at
`:557` (`("F16-errata-invalid-utf8", "fault", f_errata_bytes, 2, None)`),
reason pin at `:586` (`"output is not UTF-8"`), runner at `:600-635`.

## (1) Fault premise — REAL, observed in frozen

Command (both arms; cwd a scratch dir, both repos in /tmp):
`python3 <auditor> --lane-repo <lane> --fleet-repo <fleet> --json --rounds 1`

* Frozen: **rc=1**, stdout empty, stderr is a traceback. Frames observed:
  `load_errata` (`4fe9339f…:tools/report-landing-audit.py:339`) → `git`
  (`:89`, `capture_output=True, text=True` at `:90`) →
  `subprocess._translate_newlines`, ending
  `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 2: invalid start byte`.
  Full capture: `/tmp/kama-r23w2/rowf16-exact-frozen.err`.
* Current: **rc=2**, stdout empty, stderr
  `could-not-evaluate: git show 043ff9dc…:registry/report-landing-errata.tsv in …: output is not UTF-8: 'utf-8' codec can't decode byte 0xff in position 2: invalid start byte`
  — the REASONS pin matches; no traceback. Capture:
  `/tmp/kama-r23w2/rowf16-exact-current.err`.
* Control on the identical fixture with a valid UTF-8 comment (`# ok\n`):
  frozen **rc=0**, current **rc=0**. So the fault is exactly the undecodable
  committed blob, not the fixture's errata commit, author or timestamps.
* Grid's own case run in the clone:
  `python3 tests/report-audit/repo-state-grid.py --case F16-errata-invalid-utf8 --json`
  → grid rc=1; current `{exit: 2, traceback: false, met: true}`; frozen
  `{exit: 1, kinds: "unparseable", traceback: true, met: false}`.

Inference (high confidence): the frozen crash is Python's text-mode subprocess
decode, not the auditor's own decode; the frozen `git()` catches only
`OSError` (`4fe9339f…:87-96`), so `UnicodeDecodeError` escapes as a traceback.
The row's builder passes no execution marker (`marker=None`), so the grid's
`executed` field is trivially false; I did not instrument this path for
program execution or hang independently.

## (2) Expected outcome — CORRECT (contract, not just current behaviour)

The auditor's documented exit contract at HEAD
(`tools/report-landing-audit.py:42-45`) says exit 2 is for
"unusable git or non-UTF-8 git output, shallow/grafted/non-sha1 repository,
malformed ledger, empty round selection, output failure" and `:46` says
"Errors are never verdicts." The errata blob is git output
(`load_errata`, `:362-371`, `git show <tip>:registry/report-landing-errata.tsv`).
The current refusal is raised at the decode boundary
(`:123-126`, "undecodable output is an EvalError, never a traceback verdict",
`:109-111`), before any JSON is emitted: stdout was empty, so no partial
verdict leaks. Exit 2 cannot be mistaken for clean (0) or failed (1), and the
stderr reason names the actual cause. This is fail-closed and matches the
contract; the frozen arm's exit-1 traceback is the violation the row pins.

The one defensible alternative — a bytes-level parser that skips an
undecodable *comment* line and returns the true verdict — is **not** the
declared behaviour: `parse_errata` (`:347-356`) skips comments only after
decoding the whole blob, and the contract says non-UTF-8 git output is exit 2.
The fixture's bad byte is inside a comment (`# \xff bad`), so the refusal is
broader than semantically necessary, but it is a whole-audit refusal, not a
flip. **Conclusion: exit 2 + reason is correct.** Confidence high.

Same strict boundary verified on the adjacent reads (all exit 2, no
traceback, full matrix in `/tmp/kama-r23w2/RowF16-variants.out`):

| variant | current outcome |
|---|---|
| bad byte inside a semantically meaningful data row | 2 `output is not UTF-8` |
| UTF-16LE ledger with BOM | 2 `output is not UTF-8` |
| `--errata PATH` with bad byte | 2 `cannot read errata …` |
| committed `corpus/SOURCES.md` bad byte | 2 `git cat-file … output is not UTF-8` |
| committed fleet report bad byte (F02 class) | 2 `… output is not UTF-8` |
| UTF-8 BOM / space-indented comment | 2 `malformed row` (valid UTF-8) |
| NUL inside a comment | 0 (comment skipped) |
| CRLF and lone-CR row endings | 0, row corrects the defect |
| CR mid-field | 2 `malformed row` |
| ledger absent at tip / ledger path is a tree | 2 |

## (3) Near variant current still gets wrong — F16-N1

**A ledger correction token (7–39 hex) that collides with a repository-local
ref name.** Repro: `python3 /tmp/kama-r23w2/RowF16-refcorr.py`, observed:

```
[before any ref]  current rc=1 errata_invalid=1 status=failed
                  frozen  rc=1 errata_invalid=1 status=failed
[tag deadbee1]    current rc=2 "could-not-evaluate: <lane>: citation deadbee1 names a ref"
                  frozen  rc=0 errata_invalid=0 corrected=1 status=clean
[branch deadbee1] current rc=2 "… citation deadbee1 names a ref"
                  frozen  rc=0 errata_invalid=0 corrected=1 status=clean
```

Fixture: report cites the round-1 commit plus fake token
`1234567890abcdef1234567890abcdef12345678` (one `unresolved-full-hash`
defect); ledger row
`1\tunresolved-full-hash\t<fake>\tdeadbee1\tev`; `deadbee1` is not an object
abbreviation until a tag/branch of that name is created.

* Documented correct outcome (errata paragraph,
  `tools/report-landing-audit.py:38-40`): "A row is `errata-invalid` when its
  correction is not a lane/fleet commit (resolvable kinds)" → `errata_invalid=1`,
  exit **1** (observed before the ref exists).
* Frozen: creating the tag flips the audit from **failed (1)** to **clean
  (0)** and the fake defect is reported `corrected` — a repository-local ref
  hijacking the verdict. That is the F13 class at a new entry point.
* Current: the same tag flips the audit from the verdict **1** to
  **could-not-evaluate 2**. Mechanism (observed in source): `apply_errata`
  calls `lookup(repos, corrections, "^{commit}")` (`:389-392`); `lookup`'s
  peel pre-pass (`:137-140`) runs the bare lookup, and the F13 guard
  (`:161-163`) raises `"{repo}: citation {token} names a ref"` for any token
  git resolved through a ref. So the guard added for report citations leaks
  into errata validation.
* Consequence: repository-local refs (mutable) can convert an errata verdict
  into a whole-audit refusal; the errata paragraph reserves exit 2 for
  unreadable/malformed ledgers, not for one invalid correction. Whether this
  is a defect depends on reading "ref-named citations are refused"
  (trust paragraph, `:48-52`) as covering corrections too; the errata
  paragraph, which calls the field `correction`, says exit 1. It is not
  declared anywhere; no grid row exercises it (F13 exercises only the report
  citation entry point).
* Recommendation for L1: either classify ref-named corrections as
  `errata-invalid` (skip the ref-name guard for corrections; the pre-ref run
  already produces exit 1), or declare ref-named corrections as an exit-2
  refusal in the docstring and add a graded row. Note a 40-hex ref name does
  **not** trigger this (git treats 40-hex as an object name; observed exit 1,
  `errata_invalid=1`), and a correction that is an annotated-tag *object* sha
  is accepted via `^{commit}` peeling (observed exit 0) — a peel-semantics
  choice, not a ref.

## Secondary observations (outside F16's verdict)

* **Out-of-scope ledger row.** `20\tunresolved-full-hash\t<fake>\t<missing>\tev`
  on a clean `--rounds 1` audit gives exit **1**, `errata_invalid=1`
  (frozen identical). The docstring makes `invalid` unscoped while
  `unmatched` is round-scoped (`:385-396`); literal contract permits it, but
  auditing one round can be failed by another round's row. Candidate open,
  not a regression.
* **Grid premise claim.** The docstring says a fixture whose fault never
  materialized makes the grid exit 2
  (`tests/report-audit/repo-state-grid.py:4-6`), but `run_case` (`:600-635`)
  performs no premise assertion; only builders that call `require()` do, and
  `f_errata_bytes` calls none. A never-materialized fault that still matched
  the expectation would be scored `met` (grid exit 0/1), not 2. This does not
  affect F16 — its premise does materialize — but the claim is broader than
  the code.
* **Invalid-byte `--branch`.** A branch named with a raw `0xff`, passed as
  `--branch $'br\xff'`, plus a malformed ledger row: rc=2, no traceback
  (stderr escapes the surrogate), so no crash channel found there.

## Not verified

* Did not run the full 26-fault/8-control grid, the selftest, or the
  rounds-10-22 ledger no-harm comparison; only F16 plus the 29-run variant
  matrix above.
* Did not test on git < 2.56 or Python < 3.14; the declared git >= 2.45 floor
  was not exercised.
* Did not test alternates (O01), gitfile redirect (O02), promisor/shallow/
  sha256/mailmap rows (other owners), or any network/lazy-fetch path.
* Did not verify the L1 numbers for rows other than F16.

## Files written

* `.ufo/waves/round-23/falsify/advice/RowF16ErrataInvalid.md` (this report).
* `/tmp/kama-r23w2/CloseKama22.RowF16ErrataInvalid-2/` (clone at 245a37f6).
* `/tmp/kama-r23w2/frozen-audit.py` (extracted frozen blob).
* `/tmp/kama-r23w2/RowF16-variants.py`, `RowF16-variants.out`,
  `RowF16-refcorr.py`, `RowF16-refcorr.out`,
  `rowf16-exact-{frozen,current}.{out,err}`, `brprobe/`.

No lane tracked file, index, `.jj`, fleet root, sibling lane or global config
was touched; no commits, pushes or jj commands; no installs.
