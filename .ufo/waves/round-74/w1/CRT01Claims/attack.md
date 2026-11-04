# CRT01Claims — round-74 claim-falsification attack log

Seat: CRT01Claims (critic, kama r74 w1). Scope: refute C1/C2/C3 as frozen in
`plans/round-74-claims.md`. All work in `/fast/scratch/hyaku/kama-r74/CRT01Claims/`
(scratch, deleted after receipts were copied here). No frozen file was edited; no
git mutations outside fixture dirs under the scratch root (fixture identity
`-c user.name=fixture -c user.email=fixture@invalid -c commit.gpgsign=false`,
`toplevel` asserted before first commit, `git init -b master`).

Method: three independent **oracle counters** (`oracles.py`, critic's own reference
implementation of each frozen predicate) were validated against the frozen scorer's
expectations on the committed fixtures rebuilt into scratch (`build-survivors.py`,
`KAMA_R74_SCRATCH=/fast/scratch/hyaku/kama-r74/CRT01Claims/fixtures`), then used to
grade the executors' v2 modules on attack fixtures the frozen scorer does not cover.

Oracle validation on the frozen fixtures (all match the kill rule):

```
c1_invisible ORACLE rc=1  SELFDESC_CANON_V2 canon_round=74 canon_rows=7 demonstrated=4 total=7 invisible=4
c1_clean     ORACLE rc=0  ... total=7 invisible=0
c2_wrapped   ORACLE rc=1  RECEIPT_CLAIM_V2_FINDING wrapped-claim ... claims=1 unbound_claims=1
c2_offset    ORACLE rc=1  RECEIPT_CLAIM_V2_FINDING offset-claim ...
c2_mixed_honest      ORACLE rc=0  ... bound_revisions=1
c2_clean_realizable  ORACLE rc=0  ... bound_revisions=1
c3_edited    ORACLE rc=1  PROVINCE_HOST_DRIFT_V2 ... edited=1
c3_clean     ORACLE rc=0  ... edited=0
```

Base legs (frozen tools over the rebuilt fixtures, at this run time):

```
BASE c1_invisible probe-canon-base: canon_round=71 canon_rows=3        (the R73-D1 hole)
BASE c2_wrapped  r73: exit=0 claims=0 unbound_claims=0                 (line-scoped miss)
BASE c2_offset   r73: exit=0 claims=0 unbound_claims=0
BASE c3_edited   r73: exit=0 stale=0                                   (newest-only blind)
Frozen selftests at this run time: r42 5/5, r72 16/16, r73-c2 14/14, r73-c3 9/9 — all green.
```

---

## C1 — calibration (`tools/round74-selfdesc-canon.py`)

### F1a duplicate demonstrated name (`nc1_dup_demo`)
Fixture: BOLD71 + `### demonstrated in round 73` with `round-scope-cases` on TWO rows
+ `### demonstrated in round 74`. Hand census: 7 distinct names; the duplicate row
inflates any row-sum to 8.

```
$ python3 score-matrix.py --claim c1 --fixtures new-fixtures/nc1_dup_demo
nc1_dup_demo V2 rc=1    SELFDESC_CANON_V2 canon_round=71 canon_rows=3 demonstrated=4 total=7 invisible=4
nc1_dup_demo ORACLE rc=1 SELFDESC_CANON_V2 canon_round=74 canon_rows=7 demonstrated=4 total=7 invisible=4
```
REFUTATION FAILS on this axis: the v2 deduplicates (`total=7` over 8 table rows).
A row-summing implementation would have printed total=8 and contradicted the claim's
own hand census — the fixture is load-bearing; the module survives it.

### F1b demonstrated table OLDER than the bold canon (`nc1_old_demo`)
Fixture: BOLD71 + `### Capabilities demonstrated in round 70` carrying a new name
`legacy-audit` + demo73 + demo74. The round-70 table is OLDER than the newest bold
canon (71), so its name must count toward `total` but NOT toward `invisible`.

```
nc1_old_demo V2 rc=1    SELFDESC_CANON_V2 ... total=7 invisible=4
nc1_old_demo ORACLE rc=1 ... total=8 invisible=4
```
DIVERGENCE, freeze cannot adjudicate. The v2 computes `total` as
|bold-canon ∪ demonstrated-newer-than-bold| = 3+4 = 7, excluding the older
demonstrated table's name. The oracle computes the union over ALL recognized tables
= 8. Both satisfy every frozen fixture (the frozen set contains no demonstrated
table older than the bold canon), and the freeze's sentence "`total` counts the
distinct names across the newest-by-round resolution" admits both readings.
Impact: two minimally-compliant v2 implementations print different `total` for the
same record — the claim's receipt is not deterministic across implementations.
Smallest safe correction (future round; freeze is frozen): add one fixture whose
demonstrated table is older than the bold canon and pin `total` to the hand census.

### F1c no bold canon at all (`nc1_demo_only`)
Fixture: only `### demonstrated in round 73` + `### demonstrated in round 74`
(no bold heading anywhere). r42 `canon()` sees nothing (base resolves round −1/0).

```
nc1_demo_only V2 rc=1  canon_round=-1 canon_rows=0 demonstrated=4 total=4 invisible=4
nc1_demo_only ORACLE rc=1 canon_round=74 canon_rows=4 demonstrated=4 total=4 invisible=4
```
Both implementations agree: with no bold canon, every demonstrated name is
`invisible` — exit 1. A "no-bold ⇒ nothing invisible" implementation would exit 0
here (wrong in the claim's favor); neither v2 module does that. (Minor: `canon_round`
differs — −1 vs 74; unscored by the frozen scorer.)

### F1d score-survivors gaming (arm 4)
Randomized-path copy of `c1_invisible` (`zz-c1_invisible-cf9a6f`, byte-identical git
tree, name carries no fixture token):

```
zz-c1_invisible-cf9a6f V2 rc=1 SELFDESC_CANON_V2 ... total=7 invisible=4   (identical verdict)
```
Grep of the module's grading path: no `sys.argv`, basename, or fixture-name
branching (`user.name=fixture` hits are the selftest identity). Module selftest
builds its arms in `tempfile.mkdtemp(prefix="selfdesc-canon-v2-selftest-")` —
generic paths. Selftest: `SELFDESC_CANON_V2_SELFTEST pass=11 fail=0`.
Gaming fails; receipt accepted. Observation (non-blocking): running the selftest
without `--repo` from a cwd without `plans/` dies with a raw FileNotFoundError
traceback instead of a usage error — robustness nit, not a predicate violation.

**C1 verdict: NOT refuted.** One genuine freeze ambiguity (F1b: `total` semantics)
that the frozen kill fixtures cannot distinguish; the claim's core assertion
(demonstrated tables are visible; invisible=0 required) survives every attack.

---

## C3 — freshness (`tools/round74-province-host-drift.py`)

### F3a edited OLDER block under a clean newest (`nc3_newest_no_token`)
Fixture: round-72 block recorded at A (`recorded at A` token), then a round-73 block
appended (no token, matches live triple, newest), then the round-72 block's date
edited. Base r73 leg stays green (newest == live). A "preserve only the newest
block" implementation — the cheapest compliant-looking gut — exits 0.

```
nc3_newest_no_token V2 rc=1  PROVINCE_HOST_DRIFT_V2 ... edited=1
    PROVINCE_HOST_DRIFT_V2_FINDING edited-block line=3 round=72 recorded-at=7717...: rev=7717... resolved-at=e574...: at-recorded='Round-72 host-identity block (2026-11-01)...' at-tip='Round-72 host-identity block (2026-11-02)...'
nc3_newest_no_token ORACLE rc=1 ... edited=1
```
The v2 grades EVERY token-carrying block, not just the newest — the gut fails.
Frozen scorer blind spot confirmed: the frozen set has only single-block fixtures;
this behavior is unexercised by `score-survivors.py` (see F3d).

### F3b `recorded at` rev that does not exist in the repo (`nc3_token_impossible`)
Block names a valid 40-hex commit from a DIFFERENT repository.

```
nc3_token_impossible V2 rc=2  PROVINCE_HOST_DRIFT_V2 could-not-evaluate: recorded at rev unresolvable: b0c9e422... (fatal: Needed a single revision)
nc3_token_impossible ORACLE rc=2  ... unresolvable
```
Both fail closed to exit 2, exactly the freeze's could-not-evaluate class. (A
recorded-at rev equal to the tip's own commit is a git hash fixpoint and cannot be
committed; the "edited before its recorded rev" case is therefore only constructible
as an out-of-repo/unresolvable rev, which both modules map to exit 2.)

### F3c literal "byte-identical at `<rev>`" is unimplementable (semantics note)
In the frozen `c3_clean`/`c3_edited` fixtures the block does not exist at rev A at
all (A is the seed commit; the block lands in the next commit). No implementation
can require byte-identity AT A; every compliant module must resolve the block's
bytes at their first appearance in A..tip. Both the v2 (`resolved-at=e574...`) and
the oracle implement first-appearance semantics. The freeze's wording survives only
under this reading; the module's receipt makes the reading observable.

### F3d selftest-blindness (arm 2, frozen scorer)
Gutted behavior that passes the ENTIRE frozen scorer: the preservation leg limited
to the newest block. The frozen `c3_edited`/`c3_clean` are single-block fixtures;
`score-survivors.py` (controls/score-survivors.py:144-164) never constructs a
multi-block file. Named fixture that catches the gut: `nc3_newest_no_token` (F3a).
The v2 module's own selftest closes this independently:
`PROVINCE_HOST_DRIFT_V2_SELFTEST pass=10 fail=0`, and its selftest arms build in
`tempfile.mkdtemp` dirs (`f0-clean`, `f1-edited`) — generic paths, frozen-shape
replays. Grep: no fixture-name branching in the grading path.

### F3e score-survivors gaming (arm 4)
```
zz-c3_edited-34bd43 V2 rc=1  ... edited=1        (identical verdict to named fixture)
```
Gaming fails; receipt accepted.

**C3 verdict: NOT refuted.** The v2 survives all falsification attempts including
the multi-block preservation case the frozen scorer does not exercise.

---

## C2 — operability (`tools/round74-receipt-claim-binding.py`)

Module landed during this seat (EX02ClaimV2, tested bytes sha256
`0f231fac27a2b49e99a8d186162f62942a7f9328bf0dcb8d987eabc98051ab44`, selftest
`RECEIPT_CLAIM_V2_SELFTEST pass=15 fail=0`). All C2 attack fixtures were built and
oracle-graded BEFORE the module landed (pre-registration, F2a-F2f below); the
module was then run over every one of them:

```
c2_wrapped        V2 rc=1 wrapped-claim    ORACLE rc=1 wrapped-claim
c2_offset         V2 rc=1 offset-claim     ORACLE rc=1 offset-claim
c2_mixed_honest   V2 rc=0 bound_revisions=1  ORACLE rc=0 bound_revisions=1
c2_clean_realizable V2 rc=0 bound_revisions=1 ORACLE rc=0 bound_revisions=1
nc2_stale_explicit   V2 rc=1 stale-revision  ORACLE rc=1 stale-revision
nc2_two_receipts     V2 rc=1, one stale-revision finding per unbound receipt
                     ORACLE rc=1 (oracle's improvised kind: stale-claim)
nc2_recorded_at_hex  V2 rc=1 stale-revision  ORACLE rc=1 stale-revision
nc2_lesson_only      V2 rc=1 wrapped-claim (lesson blob, line 4)  ORACLE rc=1 (line 3)
zz-c2_wrapped-7fcb21    V2 rc=1 wrapped-claim     (identical to named fixture)
zz-c2_offset-7affcd     V2 rc=1 offset-claim      (identical)
zz-c2_mixed_honest-765353 V2 rc=0 bound_revisions=1 (identical)
```

The module survives the entire matrix. Its own selftest independently closes the
F2a/F2b/F2f blind spots (arms `stale-revision`, `two-receipts-stale`,
`lesson-wrapped-claim`). PREDICATE constant: ws-normalized byte-match with the
plan's C2 blockquote. Frozen scorer with all three modules:
`SURVIVORS c2 base_green=2 v2_killed=2 v2=present clean=True`.

### F2g finding path field (new, minor)
The v2's finding line names the RECEIPT path
(`RECEIPT_CLAIM_V2_FINDING wrapped-claim .ufo/.../a.out :: 6`); r73 and the oracle
name the RECORD path (`SCORECARD.md :: 3`). The predicate format
`<kind> <path> :: <line>` does not pin whose path; the frozen scorer greps only the
kind. Under-specification note; no verdict impact.

### F2a stale explicit revision — the `stale-revision` kind is never exercised by the frozen set (`nc2_stale_explicit`)
Fixture: receipt header `# rev=c0`; record paragraph names c1 (a different, valid,
ancestor commit): `re-run at revision <c1> naming \`r.out\``. Expect: mention ≠
header → `stale-revision` finding, exit 1, bound_revisions=0.

```
nc2_stale_explicit ORACLE rc=1
    RECEIPT_CLAIM_V2_FINDING stale-revision SCORECARD.md :: 3: - C2 evidence: re-run at revision 383c189d... naming `.ufo/waves/round-74/measured/r.out`.
    RECEIPT_CLAIM_V2 ... claims=0 unbound_claims=0 bound_revisions=0
```
Frozen-scorer blind spot (arm 2): NONE of the four frozen c2 fixtures contains an
explicit-revision mention whose hex differs from the cited receipt's header —
`c2_wrapped`/`c2_offset` are tip-claim fixtures, `c2_mixed_honest`/`c2_clean_realizable`
bind. A v2 that NEVER emits `stale-revision` and never counts `bound_revisions`
passes all four frozen fixtures with exit 0/1 exactly as expected. Named catch
fixture: this one.

### F2b one paragraph, two receipts, one tip claim — no frozen finding kind (`nc2_two_receipts`)
Fixture: receipts `r.out` (rev=c0) and `r2.out` (rev=c1); one line cites both and
claims `measured at the report tip`. Both headers ≠ tip.

```
nc2_two_receipts ORACLE rc=1
    RECEIPT_CLAIM_V2_FINDING stale-claim SCORECARD.md :: 3: - C2 evidence: measured at the report tip, see `...r.out` and `...r2.out`.
    RECEIPT_CLAIM_V2 ... cited=2 claims=1 unbound_claims=1 bound_revisions=0
```
SPEC GAP: the freeze's claim finding kinds are exactly
`wrapped-claim|offset-claim|stale-revision`. This paragraph is one line (not
wrapped, not offset) and names no explicit revision (not stale-revision), yet at
least one cited receipt is unbound — the case "which finding names what?" has no
frozen answer. A minimally-compliant v2 must improvise a kind (or silently grade it
clean, which would be wrong in the claim's favor). Divergence between implementations
is guaranteed; the freeze cannot be used to reject either. Smallest safe correction
(future round): pin the kind for unbound-without-kind (e.g. inherit r73's
`stale-claim`) and add this fixture to the kill set.

### F2c `recorded at <hex>` that is NOT a revision mention (`nc2_recorded_at_hex`)
Fixture: receipt header=c0; record: `probe recorded at <c1> naming \`r.out\`
(content id, not a run revision)`.

```
nc2_recorded_at_hex ORACLE rc=1   (literal reading: any 40-hex mention binds → c1 ≠ c0 → stale-revision)
```
AMBIGUITY: the freeze says "a paragraph that names an explicit 40-hex revision
binds each cited receipt whose header equals that revision". Under the literal
reading ANY 40-hex token (including a content id in a `recorded at` clause) is a
"named revision" and a header mismatch is a finding. Under a context reading
(bind only re-run/measurement mentions) this paragraph is clean. The frozen
fixtures cannot distinguish the readings (their only explicit mentions are
genuine re-run citations). Two minimally-compliant implementations diverge on this
record. Smallest safe correction (future round): define "names an explicit revision"
as a 40-hex token in binding context, or accept any-hex binding as the frozen
semantics — but pick one in the receipt text.

### F2d the mixed-case arm is load-bearing (arm 3)
Strawman: `strawman-casesensitive.py` — a 1-line mutation of the oracle (mention
hex no longer lowercased before comparison), i.e. a paragraph-scoped, otherwise
fully compliant, CASE-SENSITIVE v2:

```
== strawman over frozen c2_mixed_honest:
RECEIPT_CLAIM_V2_FINDING stale-revision SCORECARD.md :: 3: - C2 evidence: re-run at revision BBB10873... naming `.ufo/waves/round-74/measured/a.out`.
RECEIPT_CLAIM_V2 ... bound_revisions=0
rc=1
== strawman over frozen c2_clean_realizable:
RECEIPT_CLAIM_V2 ... bound_revisions=1
rc=0
```
A case-sensitive v2 exits 0 on every other frozen fixture and fails c2_mixed_honest
TWICE over: the `stale-revision` finding forces exit 1, and even with the finding
suppressed `bound_revisions=0` fails score-survivors.py:125's
`"bound_revisions=1"` check. Exact record text that proves it (frozen builder,
build-survivors.py:195-196):
`- C2 evidence: re-run at revision BBB1087337E3B56B92EF1A6D4BC983F44B140B23 naming \`.ufo/waves/round-74/measured/a.out\`.`
against receipt header `# rev=bbb1087337e3b56b92ef1a6d4bc983f44b140b23` — the
upper-case hex IS the receipt's own commit (builder rewrite), so the arm is honest,
not a string-match trap. Arm load-bearing; refutation of the arm FAILS.

### F2e score-survivors gaming (arm 4)
Receipt if the module landed: see appendix below. Pre-registered acceptance
criterion (as assigned): a v2 that string-matches fixture names or paths would print
KILLED verdicts on `zz-*` copies whose paths contain no fixture token; honest
grading must reproduce the named-fixture verdicts byte-identically. Oracle proof
that honest grading is path-independent:

```
zz-c2_wrapped-7fcb21    ORACLE rc=1  claims=1 unbound_claims=1   (identical to named fixture)
zz-c2_offset-7affcd     ORACLE rc=1  claims=1 unbound_claims=1
zz-c2_mixed_honest-765353 ORACLE rc=0  bound_revisions=1
```

### F2f claim paragraph living ONLY in the lesson file (`nc2_lesson_only`)
The frozen c2 fixtures put the graded paragraph in SCORECARD.md's `## Round 74`
section; the lesson file `corpus/lessons/round-74.md` is an empty stub (frozen
builder C2_SEED). The frozen predicate grades BOTH record blobs, but a v2 that
never reads the lesson half passes every frozen fixture.

```
nc2_lesson_only ORACLE rc=1
    RECEIPT_CLAIM_V2_FINDING wrapped-claim corpus/lessons/round-74.md :: 3: report tip, receipt `.ufo/waves/round-74/measured/a.out`.
    RECEIPT_CLAIM_V2 ... claims=1 unbound_claims=1 bound_revisions=0
```
Catch fixture built and oracle-graded; a lesson-blind v2 exits 0 here — wrong in
the claim's favor. Same blind-spot class as F2a/F3d.

### F2h live-path volatility disclosure (process, not claim)
After EX02's tested bytes were graded (sha `0f231fac…`, selftest 15/15), the live
file `tools/round74-receipt-claim-binding.py` was observed rotating through further
digests during this seat: `fb34f3d9…` (selftest pass=6 fail=3; `blob-reader-seam`
FAIL — a case-sensitivity mutant), `ac7dc369…`, `5c6174c4…` (mtime 01:25, size
24570 vs EX02's 32144). This is concurrent mutation-testing activity touching the
live path; an earlier overwrite (sha `8d7329e7…`, unimportable, emitted
`stale-claim`) is preserved by EX02 at
`.ufo/waves/round-74/w1/EX02ClaimV2/receipts/overwritten-peer-version.py`. All
observed variants were re-run against my C2 matrix and remained oracle-consistent
on verdicts and counts (receipts below); selftest arms are the kill mechanism that
catches the mutants. C1 (`2f4e473f…`) and C3 (`118ae07…`) module bytes were
byte-stable across this entire seat (sha256 before/after diff empty).

---

## Summary (axes: calibration, operability, freshness)

| Attack | Result |
|---|---|
| F1a duplicate demonstrated name | v2 dedups (`total=7`); refutation FAILS |
| F1b old demonstrated table vs `total` | genuine freeze ambiguity (7 vs 8); fixtures cannot adjudicate — routed |
| F1c no bold canon | both: all names invisible, exit 1; refutation FAILS |
| F1d C1 gaming | no path/name branching; random-copy verdicts identical; FAILS |
| F2a stale-revision never exercised by frozen set | module emits stale-revision (selftest arm + nc2 run); blind spot confirmed for the frozen scorer alone |
| F2b two-receipt tip claim | module: one stale-revision finding per unbound receipt; oracle: stale-claim; both exit 1 — freeze enumeration gap routed (F2b), accepted repair noted |
| F2c `recorded at`-hex ambiguity | module grades literally (any 40-hex mention binds) = oracle literal reading; context reading still possible — routed |
| F2d mixed-case arm load-bearing | case-sensitive strawman fails c2_mixed_honest on exit code AND bound_revisions; FAILS to refute |
| F2e C2 gaming | no name/path branching in grading path (7 hits all selftest-scoped); zz-copy verdicts identical — gaming fails; receipt accepted |
| F2f claim only in lesson file | module grades lesson blob (exit 1 wrapped-claim, lesson line 4); blind spot closed by module, open in frozen scorer |
| F2g finding path field | v2 names receipt path; r73/oracle name record path; predicate unpinned — note only |
| F2h live-path volatility | C2 file rotated through ≥4 digests post-grading (mutation testing); all variants oracle-consistent on my matrix; disclosed with receipts |
| F3a edited older block, clean newest | v2 grades all blocks; refutation FAILS |
| F3b unresolvable recorded-at rev | both exit 2; FAILS |
| F3c literal at-rev semantics | first-appearance semantics pinned by receipt; note only |
| F3d C3 selftest-blindness | newest-only gut passes frozen scorer; caught by F3a; v2 selftest closes it |
| F3e C3 gaming | random-copy verdicts identical; FAILS |

No claim refuted on its own terms. All three v2 modules survive every constructed
fixture — 11 new fixtures plus 5 randomized-path copies. Four freeze-level defects
are routed report-only (F1b `total` semantics; F2b finding-kind enumeration for
unbound same-line/multi-receipt claims; F2c context-free hex-mention binding; plus
F2g/F3c notation notes) — the "the frozen fixtures cannot distinguish two
minimally-compliant implementations" class, i.e. under-specification, not
contradictions. One process disclosure (F2h): the C2 live file rotated through
several digests under concurrent mutation testing after grading; every observed
variant remained oracle-consistent on my matrix. The freeze was not edited.
