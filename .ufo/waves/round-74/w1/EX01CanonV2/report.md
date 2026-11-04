# EX01CanonV2 — kama round 74 w1, C1 build: `tools/round74-selfdesc-canon.py`

Seat: EX01CanonV2 (godspeed). Lane: kama-shokunin. Claim: C1 (calibration, R73-D1).
Base revision per the freeze: `868dd701bff531be6a36da742d3418f98818e5eb`
(`plans/round-74-claims.md:3`); measured live at worktree tip `b0b903a0`
(`git rev-parse master`, with other seats' wave files uncommitted — see
"Risks and disagreements").

## Files written (write scope honoured)

- `tools/round74-selfdesc-canon.py` — the C1 v2 counter (new file, the exact
  name the plan freezes). sha256
  `2f4e473f5ad9f999042155edcf01995cdf8e05c477dedaafc516657f3608eea7`.
- `.ufo/waves/round-74/w1/EX01CanonV2/v2-fixture-runs.out` — the three
  scorer-expectation runs plus the base control probe over `c1_invisible`.
- `.ufo/waves/round-74/w1/EX01CanonV2/selftest.out` — the selftest receipt.
- `.ufo/waves/round-74/w1/EX01CanonV2/base-probe-live.out` — the frozen r42
  `canon()` over the live lane (the hole, measured live).
- `.ufo/waves/round-74/w1/EX01CanonV2/report.md` — this report.
- This report is also written at the seat-spec trailer path
  `.ufo/waves/round-74/w1/EX01CanonV2.md`.

No frozen file was edited: `tools/round42-selfdesc-reconcile.py` sha256 is
unchanged at `3d9aff8f9c2236c2cb9337b08846da82de718bc1d9e8f1d283f1a71a03acd5c0`
(measured before and after; the module is imported, never copied, import
guarded against `__pycache__`). `git diff --name-only` shows only the
pre-existing `PROVINCE.md` worktree modification (a sibling seat's C3 token
addition, not mine — I never wrote it; see Risks). No git/jj mutation was
run anywhere. Fixtures were built only under my scratch dir
`/fast/scratch/hyaku/kama-r74/EX01CanonV2/` with the committed builder
(rebuilt there, committed meta paths never mutated) and the scratch dir was
deleted before yielding. No tools were installed this wave (none needed).

## Behaviour (as frozen)

`PREDICATE` is the plan's C1 blockquote carried verbatim on one line
(byte-equal to `plans/round-74-claims.md:39-49` minus `>` marks and line
breaks; asserted by two selftest arms, including one reading the plan blob at
`master` via `git cat-file`). The counter:

1. imports the byte-frozen r42 reconciler's `canon()` and `table_rows`;
2. resolves every capability table by round number regardless of heading
   markup — bold `**Capabilities — canonical list as of round <M>**` (the
   r42 `canon()` population), unbolded `## Capabilities — canonical list as
   of round <M>` and `### Capabilities demonstrated in round <M>` (a
   demonstrated table wins over a canonical table at the same round so
   demonstrated additions are never hidden);
3. prints one
   `SELFDESC_CANON_V2 canon_round=<N> canon_rows=<c> demonstrated=<d> total=<t> invisible=<i>`
   line where `canon_round/canon_rows` are always the r42 `canon()`'s bold
   resolution (the form the record's own reconciler sees), `demonstrated` is
   the distinct names carried only by tables newer than `canon_round`,
   `total` is `|canon names ∪ demonstrated names|` (the full repertoire the
   newest-by-round resolution reaches — 7 = 3 bold-canon names + 4
   demonstrated-only names on the kill fixture), and `invisible` is the
   demonstrated subset the bold canon does not name;
4. exits 0 iff `invisible=0`; exits 1 printing one
   `SELFDESC_CANON_V2_FINDING invisible <round> <name>` per invisible
   capability, named at the round of the newest table carrying it; exits 2
   (`could-not-evaluate`) on CLI misuse, unreadable SCORECARD.md, or no
   parseable capability table. A scored run never exits 2 for a finding.

## Receipts (all re-runnable; unrun checks are not claimed)

Selftest, 11/11 arms (`selftest.out`):

```
SELFDESC_CANON_V2_ARM predicate ok
SELFDESC_CANON_V2_ARM predicate-at-tip ok
SELFDESC_CANON_V2_ARM kill-invisible ok
SELFDESC_CANON_V2_ARM clean-bold-covers ok
SELFDESC_CANON_V2_ARM bold-only ok
SELFDESC_CANON_V2_ARM demo-newer-round ok
SELFDESC_CANON_V2_ARM scorecard-missing ok
SELFDESC_CANON_V2_ARM no-capability-table ok
SELFDESC_CANON_V2_ARM cli-misuse ok
SELFDESC_CANON_V2_ARM repo-not-directory ok
SELFDESC_CANON_V2_ARM work-not-empty ok
SELFDESC_CANON_V2_SELFTEST pass=11 fail=0
```

Arms cover: the predicate-vs-plan blockquote equality (worktree copy and the
`master` blob), the kill fixture (exit 1, invisible=4, each finding named),
the clean fixture (exit 0, total=7, invisible=0), a bold-only record, a
demonstrated table newer than the bold canon, both exit-2 content classes
(missing SCORECARD, no capability table) and CLI-misuse classes. Fixture
identities per the lane rule (`fixture`/`fixture@invalid`, no gpg).

Scorer expectations, run manually over the committed builder's fixtures
rebuilt into my scratch (`v2-fixture-runs.out`):

```
BASE_C1 canon_round=71 canon_rows=3          # probe-canon-base over c1_invisible, exit 0 (the hole)
SELFDESC_CANON_V2_FINDING invisible 74 live-ollama-lifecycle
SELFDESC_CANON_V2_FINDING invisible 74 province-host-drift
SELFDESC_CANON_V2_FINDING invisible 73 receipt-claim-binding
SELFDESC_CANON_V2_FINDING invisible 73 round-scope-cases
SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=4 total=7 invisible=4   # c1_invisible, exit 1
SELFDESC_CANON_V2 canon_round=74 canon_rows=7 demonstrated=0 total=7 invisible=0   # c1_clean, exit 0
```

Live lane run (expected red until the round-74 record commit lands the bold
round-74 canonical list):

```
SELFDESC_CANON_V2_FINDING invisible 73 province-host-drift
SELFDESC_CANON_V2_FINDING invisible 73 receipt-claim-binding
SELFDESC_CANON_V2_FINDING invisible 72 receipt-tip-binding
SELFDESC_CANON_V2_FINDING invisible 72 round-scope
SELFDESC_CANON_V2_FINDING invisible 73 round-scope-cases
SELFDESC_CANON_V2 canon_round=71 canon_rows=17 demonstrated=22 total=22 invisible=5   # exit 1
```

Findings decode: the demonstrated round-73 table names `round-scope-cases`,
`receipt-claim-binding`, `province-host-drift` (round 73 each), and the
unbolded round-72 canonical list names `round-scope`, `receipt-tip-binding`
(round 72) — all invisible to the frozen `canon()` which resolves round 71
(`base-probe-live.out`: `BASE_C1 canon_round=71 canon_rows=17`). This is the
R73-D1 class the plan's motivating evidence measures at base
(`plans/round-74-claims.md:28-34`: base `canon()` returns round 71/17 rows
while the real repertoire is 22). `total=22` matches the record's own "these
three demonstrated operations extend it to 22" (`SCORECARD.md:3924`).

Frozen-module health: r42 selftest still 5/5 after my runs
(`SELFDESC_SELFTEST ... pass=5 fail=0`, run in my scratch work dir).

## Risks and disagreements

- **`total` semantics under the freeze.** The kill rule pins
  `c1_invisible → total=7` while the module docstring defines
  `total` = "distinct names in the newest-by-round resolution"
  (`plans/round-74-claims.md:53`). Reading `total` as only the names of
  tables at the newest round yields 2 on that fixture (the demonstrated
  round-74 table alone) — contradicting the frozen kill rule. I implemented
  the only reading satisfying both pinned numbers (7 = 3 bold-canon ∪ 4
  demonstrated-only): the full repertoire the newest-by-round resolution
  reaches, i.e. the union of the bold-canon names and the names only newer
  tables carry. On every other surface the readings coincide (`c1_clean`
  7, live lane 22, bold-only arm 3). Reported per the freeze rule ("a seat
  that disagrees reports a disagreement and never edits this file"); no
  frozen file was touched.
- **Live-lane measurement noise.** The live run and the r42 selftest were
  measured while sibling seats hold uncommitted wave files and a pre-existing
  `PROVINCE.md` worktree edit (47 porcelain records at measurement time; the
  PROVINCE edit is the round-74 `recorded at 868dd701…` token another seat
  added — my module never reads PROVINCE.md and I did not write that line).
  Neither affects the C1 arms, which read only `SCORECARD.md` and
  `plans/round-74-claims.md`; the scorer's own C1 legs read only fixture
  dirs.
- **Fixture dirs are plain directories.** The committed builder writes the
  C1 fixtures without `git init`; the frozen predicate's exit-2 set names
  "SCORECARD.md unreadable or no capability table", so `--repo` is probed as
  a directory (a git toplevel when it is a git repository). Grading the
  committed fixtures and the lane both work; the selftest's own git fixtures
  assert the toplevel rule before their first commit.
- `--repo` defaults to `.` (the r73-module convention); the frozen receipt
  command names `--repo <lane>` explicitly. (Harness note: the
  could-not-evaluate banner prints on stdout and the process exits 2 per the
  frozen exit map; a bare `head` pipeline can mask that code.)
