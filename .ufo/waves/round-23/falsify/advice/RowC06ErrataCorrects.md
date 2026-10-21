# C06-errata-corrects-omission — independent falsification

Seat: CloseKama22.RowC06ErrataCorrects-2. Base: lane `245a37f69628c2c6bb29bbf17897d8fb5946c857`
(clone `/tmp/kama-r23w2/RowC06ErrataCorrects-2`, `rev-parse HEAD` = that value).
Auditor hashes: frozen blob `4fe9339f…:tools/report-landing-audit.py`
sha256 `09ecd63b…b3f`; committed current sha256 `f228f174…8a7`
(`git hash-object` `f10d811eafcc5bc853abdf75c4a05ec2374cd579` = `245a37f6:tools/report-landing-audit.py`).
git 2.56.0, Python 3.14.8. No tools installed.

## Verdict

**HOLDS.** The C06 row's premise is real and reproduces on a hand-built fixture in
both arms, and the expected outcome (exit 0, defect kind `landed-omitted` still
reported as corrected) is the contract-correct one, not merely what current does:
the frozen arm produces the identical JSON summary and the same rendered
`corrected landed-omitted` line.

Separately, the same errata channel still has a **current-only false failure** and
two **both-arm false-clean holes** (§5). None of them touches the C1
repository-local-git-state claim; C06 itself is not falsified.

## 1. What the row asserts (at 245a37f6)

- `tests/report-audit/repo-state-grid.py:162-167` builds: cited round-1 commit at
  t=1000, fleet report at t=2000, then an uncited lane commit `x` at t=1500
  (`round-1: more`), then a lane commit at t=1600 of
  `registry/report-landing-errata.tsv` = `1\tlanded-omitted\t<x>\t<x>\tev`.
- `tests/report-audit/repo-state-grid.py:535-536` expects `exit 0` with kinds
  `["landed-omitted"]` (control; both arms graded).

## 2. Hand-built fixture (no import of the grid)

`/tmp/kama-r23w2/c06/build.sh` runs fresh `git init` repos with
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1` and per-command identity,
reproducing the already-read builder step for step. Observed:

```
LC=db796f8b820bf3825c58832419138cdba23206a7
X=29e8ea69cc44bbb72af22255c5231a7d13b577e0
LANE_TIP=5960ded71ad0831cd5d9997ae39a6b60053e5bf0
FLEET_TIP=ebcb436228cc3c28fd415f5afcce3312e1151be4
5960ded7… fixture 1600 errata
29e8ea69… kama-shokunin 1500 round-1: more
db796f8b… kama-shokunin 1000 round-1: work
```

## 3. Observed runs on that fixture

With errata enabled (`--rounds 1 --json`, no `--no-errata`), cwd fixture root:

| arm | exit | kinds | corrected | uncorrected | unmatched | invalid | status |
|---|---|---|---|---|---|---|---|
| frozen | 0 | `[landed-omitted]` | 1 | 0 | 0 | 0 | clean |
| current | 0 | `[landed-omitted]` | 1 | 0 | 0 | 0 | clean |

Both JSON documents are identical; defect
`29e8ea69cc44bbb72af22255c5231a7d13b577e0`, `corrected_by: [1]`,
`cutoff: 2000`, `required: 2`, no traceback, no stderr, no execution, no timeout.

Control that the premise is real — same fixture with `--no-errata`:

```
frozen  --no-errata exit=1 kinds=[landed-omitted] status=failed uncorrected=1
current --no-errata exit=1 kinds=[landed-omitted] status=failed uncorrected=1
```

So the omission exists in both arms and the single ledger row is exactly what
flips the verdict. Render mode current:

```
round=1 required=2 post_report=0 defects=1
  corrected landed-omitted 29e8ea69cc44bbb72af22255c5231a7d13b577e0
summary reports=1 defects=1 corrected=1 uncorrected=0 errata_unmatched=0 errata_invalid=0 status=clean
render exit=0
```

Cross-check of the grid's own slice (`--case C06-errata-corrects-omission
--arm both`) reports `met` for frozen and current, exit 0 both — consistent with
my hand fixture, which was built independently.

## 4. Is the expected outcome correct?

Yes, against the declared contract at `tools/report-landing-audit.py:34-42`:
"A defect is corrected only by a row with equal round, kind and token" and
"Exit: 0 clean (no uncorrected defect, no unmatched/invalid errata row)". The row
at `:36-40` additionally requires, for `landed-omitted`, that the correction
"differs from the omitted commit itself" be rejected — so `correction == token`
is the only legal shape, exactly what the fixture uses. Corrected defects stay
visible (`:383`, render `corrected`), so kinds `[landed-omitted]` with exit 0 is
the right pair; exit 1 would contradict the ledger semantics and the selftest's
`errata-clean` expectation (`:809`).

Caveats (design, not falsification): the fixture proves *ledger acknowledgement*,
not report repair — the fleet report blob at HEAD still omits `x`, so a lane-side
append-only ledger can waive an omission. The `evidence` column is never
validated (empty or `ev` both pass; variant 10). That is the declared trust
model, and the frozen arm behaves identically, so it cannot be a round-23
regression.

## 5. Same-channel near variants (fresh /tmp repos, both arms)

Harness `/tmp/kama-r23w2/c06/variants.py`; full matrix in
`.ufo/waves/round-23/falsify/out/RowC06ErrataCorrects/variants.json`.

| # | variant | frozen | current |
|---|---|---|---|
| 01 | baseline C06 | exit0 clean, corr1 | exit0 clean, corr1 |
| **03** | `unresolved-full-hash` erratum correction = real lane commit in **uppercase** (`DB796F8B…`) | **exit0 clean, invalid 0** | **exit1 `failed`, invalid 1** |
| 18 | same, 7-hex uppercase prefix | exit0 clean | exit1 invalid 1 |
| 02 | correction = unrelated real commit (`lc` for a fabricated token) | exit0 clean, corr2 | exit0 clean, corr2 |
| 07 | `landed-section-missing` token `-`, correction = free text | exit0 clean | exit0 clean |
| 16 | `landed-section-missing` correction = `f`*40 (no such object) | exit0 clean | exit0 clean |
| 05 | `landed-omitted` token+correction uppercase | exit1 unmatched1 | exit1 unmatched1 invalid1 |
| 06 | `landed-omitted` token = 7-hex prefix, correction = full | exit1 invalid1 | exit1 invalid1 |
| 08 | CRLF ledger | exit0 clean | exit0 clean |
| 09 | duplicate identical correct rows | exit0 clean | exit0 clean |
| 11 | stale row after report cites the commit | exit1 unmatched1 | exit1 unmatched1 |
| 12 | ledger commit authored `kama-shokunin`, subject `round-1: ledger` | exit1, new omission uncorrected | exit1, same |
| 13 | omission correction = a different real commit | exit1 invalid1 | exit1 invalid1 |
| 14 | correction = 40 zeros | exit1 invalid1 | exit1 invalid1 |

### N1 (current-only, contract contradiction): uppercase OID correction

`apply_errata` now filters corrections through `re.fullmatch(r"[0-9a-f]{7,40}")`
at `tools/report-landing-audit.py:389-392`; `status.get("DB796F8B…")` is `None`,
so `:393-395` marks the row `errata-invalid` and the run exits 1 even though the
defect is matched and `corrected`. The frozen arm had no such filter
(`4fe9339f…:tools/report-landing-audit.py:355-356`) and returned exit 0 clean.
git itself resolves the uppercase name:

```
$ printf '%s\n' '29E8EA69CC44BBB72AF22255C5231A7D13B577E0' | git -C lane cat-file --batch-check
29e8ea69cc44bbb72af22255c5231a7d13b577e0 commit 188        # rc=0
$ … call the committed lookup directly with that token
peel=''        -> EvalError: …: citation 29E8… names a ref
peel='^{commit}' -> EvalError: …: citation 29E8… names a ref
```

So the correction *is* a lane commit under git's own object-name semantics, and
`:161-163`'s lowercase `startswith` guard would misclassify it as ref-named even
if the filter were merely widened to `[0-9a-fA-F]`. A fix needs case
normalization at parse/lookup (and in the `landed-omitted` equality at `:395`),
not just a regex character class. Latent today: all 9 real ledger rows
(`registry/report-landing-errata.tsv`) have lowercase hex in both columns
(`awk -F'\t'` uppercase count = 0), so no current verdict is flipped by this yet.
Impact if triggered: a valid correction turns clean into `failed` (exit1), a
false failure on ledger content — not repository-local git state, so C1 is
unaffected.

### N2 (both arms): correction relatedness is never checked

Variant 02: report contains fabricated 40-hex `1234…5678` outside Landed; ledger
row `1 unresolved-full-hash 1234…5678 <real cited commit> unrelated`; both arms
report `corrected=2 … status=clean`, exit 0, while the non-object token remains in
the report. The check at `:389-395` only asks whether the correction resolves; a
ledger row can launder a fabricated citation by naming any real commit. Same
shape for `landed-unresolved`/`landed-ambiguous`. Real ledger rows happen to be
prefix-related (row 3: `0957ce61…` corrects a splice by `0957ce61…`), but nothing
enforces it.

### N3 (both arms): `landed-section-missing` is waivable with anything

`RESOLVABLE` excludes `landed-section-missing`, so `:393-395` never validates its
correction: variants 07 and 16 both exit 0 clean with the report still having no
`## Landed changes` section, one naming free text and one naming a nonexistent
40-hex object. This is consistent with the docstring's parenthetical
"(resolvable kinds)" but means the strongest structural defect has the weakest
correction check.

### Smaller observations

- N4: token equality at `:382` is literal, so an uppercase or abbreviated token
  for an omitted commit never matches (variants 05/06, both arms exit 1), although
  git treats uppercase OIDs as the same object.
- N5: a row whose defect disappeared after a report revision is `errata-unmatched`
  (variant 11, exit 1 both arms); an append-only ledger has no retraction row, so
  the failure is permanent.
- N6: a ledger commit authored `kama-shokunin` with subject `round-1: …` is itself
  a required uncited commit (variant 12, exit 1 both arms) — correct per the
  omission rule, but surprising for a correction ledger.
- The grid cannot catch these: C06 is a control and pins only exit/kinds, no
  stderr reason, and none of the variants is a repository-local git-state channel.

## Not verified

- Full grid population (26 faults + 8 controls), `isolation-mutants.py` (M02/M20),
  separate-context selftest 50/50, rounds 10-22 historical ledger, no-harm runs.
  I ran only the C06 slice and my own fixture/variants.
- `--errata PATH` mode, real fleet history, `--report N=PATH` drafts, other rounds,
  git < 2.45, non-Linux, non-sha1/promisor/shallow repositories.
- The L1 claim "frozen 0/26 faults, 8/8 controls" beyond C06; the open O01/O02 and
  second-Landed-section/ambiguity items.
- Whether the intended errata contract wants correction relatedness or
  case-insensitive OIDs; N1 is measured against the tool's own `:36-40` wording
  and observed git behavior, not against an external spec (gitrevisions documents
  "The full SHA-1 object name (40-byte hexadecimal string)" but is silent on case:
  https://git-scm.com/docs/gitrevisions; batch-check semantics:
  https://git-scm.com/docs/git-cat-file, "Print object information and contents
  for each object provided on stdin.").

## Files written

- `.ufo/waves/round-23/falsify/advice/RowC06ErrataCorrects.md` (this report)
- `.ufo/waves/round-23/falsify/out/RowC06ErrataCorrects/{build.sh,variants.py,variants.json,grid-c06.json,out-frozen.json,out-current.json,noerr-frozen.json,noerr-current.json}`
- `/tmp/kama-r23w2/RowC06ErrataCorrects-2` (clone at pinned HEAD)
- `/tmp/frozen-audit-C06.py` (frozen blob extraction)
- `/tmp/kama-r23w2/c06/{build.sh,variants.py,variants.json,variants.err,grid-c06.json,grid-c06.err,fx/,var/}`

No tracked lane file, `.jj`, Git index, fleet/sibling lane, domain source, global
config or `~/.omp` was written.

## Errata (appended after first write)

- §5 URL quote corrected for exactness: the `git-cat-file` page's
  `--batch-check` wording is "Print object information for each object provided
  on stdin." The phrase with "and contents" belongs to `--batch`. The cited URL
  and the observed uppercase-OID behavior are unchanged.
