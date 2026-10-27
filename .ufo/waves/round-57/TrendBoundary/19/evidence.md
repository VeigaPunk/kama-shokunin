# R57Item19TrendBoundary — distinct case 40 evidence (read-only, no verdict authority)

Lane `kama-shokunin`; assigned axes `shokunin.conf` kama row = operability + calibration. The
`MISSION.md:29` "operability + freshness" example is an unresolved L0 conflict and is not
resolved here. No shared/source edits, no installs (none needed), no commits/jj.

Pinned tips (the lane committed repeatedly during the read; every claim names its tip):
- frozen base `b89bdab2cc114735ec5d331c6c610134258f7864` (round-56 closure)
- freeze `89dc4f5239fe1f875adda4613812e77fb9bbc7cc`; pre-data ordering correction
  `7c873d7b4e3839489a93d6334cdf93fe5d34d19f`
- binding build `7b74e2f2515a6f598918488fa5144658ff29925f`
- measured-outcome tips `8640e34cad02adcd247ba0862da63f6fb2aab0df`,
  `16efcf5eedf4887df188790eec48afbb023e7991`, `77e7f5eef2b0c759b7509056c7c511255477496d`,
  `3d2d5d4d6cba3028ec5358832a67f192cc0e41ec`
- final pin `8a7f19760242bbe523fa2d7d1b22528b587633c1`

Receipts: `.ufo/waves/round-57/TrendBoundary/19/receipts/` (committed-blob sha256s in
`sha256-committed-tip.txt`; final counter run in `counter-final-tip.out`). Uncommitted worktree
edits observed during the read are not used as evidence.

## 1. Claim-identity boundary (C1/C2 mean different things in three documents)

| Document | C1 | C2 |
|---|---|---|
| seat item prompt | calibration: stale canonical capability row count, "maxN=56 instead of expected 46" | operability: canonical-row execution/content binding, no-op `met=True exit 0` |
| `controls/freeze.txt` | same ordering | same ordering |
| `controls/freeze-amendment.txt` (pre-data, supersedes ordering) | operability: round-56 prereg-check no-op defect | calibration: stale verifier-spotcheck count 42→43 |
| committed `SCORECARD.md` §Round 57 | operability: no-op roster control (sourced on S516) | calibration: verifier-spotcheck count |

The label→axis mapping differs between the frozen seat prompt/freeze.txt and the later
committed amendment/SCORECARD. This seat reports the mapping, not a resolution; any trend
attribution keyed to "C1"/"C2" must name its document version.

## 2. "expected 46" provenance — a round-46-era maxN, not a capability row count

Counter derivation (`tools/round42-selfdesc-reconcile.py`, sha256 `9736923e…`):

```
rounds = [int(m.group(1)) for l in lines for m in [re.match(r"^## Round (\d+)", l)] if m]
maxn = max(rounds)
```

- base `b89bdab2`: `mismatches=1 … maxN=56 met=False`, exit 1 (`receipts/counter-base.out`)
- `7c873d7b`: identical (`receipts/counter-prebind.out`)
- `7b74e2f2`: `mismatches=0 … maxN=56 met=True`, exit 0 (`receipts/counter-head-binding.out`)
- `8640e34c` onward: `mismatches=0 … maxN=57 met=True`, exit 0 — maxN moved because that
  commit appends a `## Round 57` SCORECARD heading; `receipts/counter-final-tip.out` at
  `8a7f1976`. `maxN` is a moving derivation, not a frozen count.

`maxN=46` appears only at:
- `controls/c1-noop.py` literal `print("mismatches=0 maxN=46 met=True")`
- `controls/noop-c1.out`, `controls/noop-c2.out`
- SCORECARD line 2676 (base snapshot) inside `## Round 46 — …`, as the historical round-46
  receipt "round-42 self-description counter `mismatches=0 maxN=46 met=True`"

No literal `46` exists in the counter. Canonical capability rows are 11 (highest canonical
heading "canonical list as of round 49", unchanged through the final pin); the sum of rows over
all canonical tables is 76 (3+6+7+8+9+10+11+11+11).
`receipts/maxn46-provenance*.txt`, `receipts/capability-rows.txt`.

Frozen "expected 46" target test — scratch copy of the counter with `maxn = 46` forced, run
against `8640e34c`:

```
r41=0 banner=1 planned=1 … mismatches=2 maxN=46 met=False
detail: banner: head lacks 'Latest measured round: 46'
detail: planned: section does not name '### Planned (round 47)'
```

(`receipts/counter-maxn46-mutant.out`, exit 1.) A repair that makes the counter report 46
breaks its own banner/planned legs; the committed repair kept `maxn` derived and changed only
the stale expected literal 42→43.

## 3. No-op reachability boundary of the C1 operability evidence

The committed checker (`tools/round56-prereg-check.py`, sha256 `dee6f922…`, unchanged through
the final pin) binds roster members to `ast.Call` nodes whose first argument is a matching
string constant. Five independently constructed fixture repos (each `git rev-parse
--show-toplevel` asserted equal to the fixture dir before committing) were checked at their own
HEAD:

| Fixture battery | Result | Exit |
|---|---|---|
| real round-56 battery (blob copied from `7b74e2f2`) | `present=1 roster_match=1 kills=1 controls=2 met=True` | 0 |
| pure no-op: exact `ROSTER` literal, `main(): return 0` | `met=False` | 1 |
| call-token no-op: exact `ROSTER`, stub `run(...)` calls for all three roster names, nothing executed or asserted | `met=True` | 0 |
| dead-branch no-op: the same calls inside `if False:` | `met=True` | 0 |
| roster with one control removed | `roster_match=0 met=False` | 1 |

(`receipts/case40-prereg-variants.json`.) The frozen predicate text says a no-op that "executes
none" must be rejected; the dead-branch fixture executes none and is accepted. `SCORECARD.md`
§Round 57 names the limit ("checks the call-site inventory in the committed battery AST"), but
`corpus/lessons/round-57.md` C1 says "so a no-op harness cannot satisfy the counter", broader
than the measured boundary. The L1-measured no-op receipt reproduced while its fixture existed:
`met=False`, exit 1 (`receipts/noop-control-rerun.txt`; fixture
`/fast/scratch/hyaku/kama-r57/noop-control`, tip `8caa23a2…`). That fixture was removed by its
owner during this read; see §4.

## 4. Operability of the frozen controls themselves

- `controls/c1-noop.py` prints its own `mismatches=0 maxN=46 met=True` and exits 0
  (`receipts/c1-noop-rerun.txt`). No instrument inside the lane consumes that script, so
  `freeze.txt`'s `noop_C1=met=True exit=0 despite skipping data` is a property of the fixture's
  own print, not a measured false green of a counter.
- `controls/noop-c2.out` records `canonical_table_reads=0`, `self_description_reads=0`; no
  producer script exists in the wave (`grep -rn canonical_table_reads` matches only the receipt).
  It is an unverifiable hand-written receipt.
- `controls/canonical-noop` and `controls/no-canonical` are plain directories with no `.git` and
  no recorded tip/command. Running the counter with `--repo` pointed at them resolves the
  enclosing lane repository and evaluates the lane tip instead:
  `tip=8640e34c … r41=10 … mismatches=10 met=False` and `r41=12 … mismatches=12 met=False`
  (`receipts/counter-on-canonical-noop.txt`, `receipts/counter-on-no-canonical.txt`). As frozen
  controls they are inert unless copied into a separate repo and committed (no such receipt).
- `measured/noop-c1.out` cites `fixture=/fast/scratch/hyaku/kama-r57/noop-control` and
  `tip=8caa23a2…`; that commit is absent from the lane repository (`git cat-file -e` fails), and
  the scratch fixture has since been removed by its owner. The receipt reproduces only while
  that out-of-repo fixture exists; it is not re-derivable from the committed tree.

## 5. Expansion evidence (what the tree supports)

| Tip | `corpus/knowledge/*.md` | SOURCES rows | highest canonical capability table |
|---|---|---|---|
| `b89bdab2` | 36 | 256 | round 49 (11 rows) |
| `7b74e2f2` | 36 | 256 | round 49 (11 rows) |
| `8a7f1976` | 36 | 257 | round 49 (11 rows) |

`git diff b89bdab2 8a7f1976 -- corpus/knowledge` is empty. The only SOURCES change is one
appended row, S516 (own-work, tier A, mined, `tools/round56-env-leg-battery.py` call-site
inventory), added at `16efcf5e`. Round-57 census start and end both exit 0; the lesson's
"257 rows after" re-derives from `grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
corpus/SOURCES.md` = 257 (the validator output itself is a 102-line warning/ok stream).

Supported: no net-new admitted `knowledge/` entry, no frontier row advance, no capability
admission. Not supported: an `expansion: improved` verdict under `CORPUS.md` rule 4 ("Expansion
is knowledge, not rows"), because S516 is a source row and no `knowledge/` entry was admitted.
Also not supported: `expansion: harmed` — no admitted entry is shown to fail its bar. Whether an
own-work code-byte source row is a "new kind of source" under `LEARNING.md`'s expansion
observable is an open attribution question; this seat records it rather than ruling it.

## 6. Quality evidence (what the receipts do and do not establish)

`LEARNING.md` defines quality as entries re-verified/deepened/superseded, or stale entries
re-verified, with no admitted entry failing its re-check.

- `git diff b89bdab2 8a7f1976 -- corpus/knowledge` is empty: no knowledge entry is re-verified,
  deepened or superseded by this round. Entry-level quality evidence is absent.
- C1 (`receipts/case40-prereg-variants.json`) supports narrowly: the genuine battery is accepted
  and a roster-literal-only no-op is rejected. It does not establish that battery effects or
  assertions executed (§3). Final receipts: `measured/c1-committed-tip.out`
  (`present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0, `tip=3d2d5d4d`).
- C2 (`receipts/counter-head-binding.out`, `receipts/spotcheck-glob-worktree.txt`) supports:
  the SCORECARD calibration literal (43) equals the committed `*verifier-spotcheck.md` count and
  the worktree glob result (43), so `mismatches=0` at `7b74e2f2`/`8640e34c`/`8a7f1976`. The r41
  leg reads its expected literal from the same SCORECARD row it checks — self-consistency, not
  independent derivation; a coordinated edit of both sides would not be distinguished. The tree
  side is independently re-derivable (43 committed blobs), so the current agreement is factual.
  Final receipt `measured/c2-committed-tip.out` (`mismatches=0 maxN=57 met=True`, exit 0,
  `tip=3d2d5d4d`).

Supported: an instrument-level correction (stale literal → tree-derived count) and a narrow
call-site predicate. Not supported: a quality-trend improvement in the `LEARNING.md` sense (no
entry re-verified/deepened) and the general statement "no-op harness cannot satisfy the counter".

## 7. Discernment evidence

- `corpus/lessons/round-57.md` at the final pin contains one gate decision: S516 ADMIT (own-work,
  tier A, mined) and zero REJECT decisions (`grep -cE 'ADMIT|REJECT'` = 1). `LEARNING.md` requires
  at least one admit **and** one reject in the non-author sample; the round's Gate states "no
  independent verifier of this round is available before filing; dispatched members are lane
  authors." With no reject and no outside reviewer, no round-57 discernment sample exists.
- `LEARNING.md` ("A subagent the lane dispatched is still the lane") makes every seat check —
  including this file — advisory, not non-author judgment.
- Contradiction on record, present at base and at the final pin: `SCORECARD.md` round-56
  §Trend verdicts says `discernment — unchanged`, while the round-56 outside closure
  (`corpus/lessons/round-56-verifier-spotcheck.md`) says `Discernment — harmed` for the S513
  reject disagreement. `grep -i trend tools/round42-selfdesc-reconcile.py` returns nothing: no
  counter checks trend verdicts against lessons.
- Round-56 outside routed defects = 4 (MISSION axis conflict; bind C2-style gates to executed
  entries; revisit S513 reject rationale/discernment miss; append-only audit exit 1 and invalid
  declarations). At the final pin the round-57 lesson has three mistake rows: no-op-counter
  (= defect 2), discernment-disagreement (= defect 3, routed not fixed), and
  calibration-staleness (an in-round finding). Defects 1 (MISSION conflict) and 4 (append-only
  audit exit 1) have no lesson row: 2 of 4 outside routed defects are lesson-addressed.

## 8. S515 non-author spot-check (advisory only)

- URL: https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT
- Access date: 2026-10-27 (live fetch, `curl` exit 0; page "last updated in 2.56.0")
- Located section/anchor: `GIT_CONFIG_COUNT` / `Documentation/git-config.txt-GITCONFIGCOUNT`
- Located quote (18 words): "all environment pairs GIT_CONFIG_KEY_<n> and
  GIT_CONFIG_VALUE_<n> up to that number will be added to the process’s runtime configuration"
- Snapshot sha256 `706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a`, identical
  to the committed round-56 snapshot and the round-57 committed snapshot; the live page is
  byte-identical.
- Preceding page sentence: "If GIT_CONFIG_COUNT is set to a positive number" — the quoted
  fragment omits the positive-number precondition but the located passage carries it.

Advisory: **agree** with the S515 ADMIT. The quote is ≤25 words, the location is exact, and the
environment-pair semantics (pairs up to COUNT, zero-indexed, missing key/value an error) are as
cited. (`receipts/s515-reopen.txt`.)

## 9. One admit/reject decision spot-check (advisory only)

Round 57 records one ADMIT and no REJECT, so the sampled decisions are the round-56 gate rows
named by this seat prompt (S515) and the round-56 reject the outside closure contested (S513):

| Decision | Re-opened source | Advisory | Reason |
|---|---|---|---|
| S515 ADMIT | live git-config page (above) | agree | 18-word located quote directly supports runtime config injection via environment pairs. |
| S513 REJECT | https://man7.org/linux/man-pages/man8/ld.so.8.html (live, 2026-10-27) | source supports the closure's disagreement | The 18-word `LD_AUDIT` quote is present, and the same page contains both "secure-execution" and "dynamic string tokens" — the topics the gate's flip names. A pure "overlap" reason does not establish redundancy without narrowing scope. |

(`receipts/s513-reopen.txt`.) The final-pin round-57 lesson now has a `discernment-disagreement`
mistake row that preserves this disagreement and explicitly does not claim discernment
improvement; this advisory agrees with that routing and exercises no decision authority.

## 10. Limits

- Read-only on the lane: no shared-file edits, no commits/jj/git mutations outside private
  scratch fixtures (each asserted with `git rev-parse --show-toplevel` before any fixture commit).
- No tool installs; no version/channel to record.
- The wave kept committing during the read (`b89bdab2 → … → 8a7f1976`); every claim is pinned to a
  commit or an exact file hash, and the final counter run is `receipts/counter-final-tip.out`.
- Scratch under `/fast/scratch/hyaku/kama-r57/R57Item19TrendBoundary/` was cleared after copying
  receipts here. The L1's `/fast/scratch/hyaku/kama-r57/noop-control` fixture was observed during
  the read, reproduced its receipt then, and was later removed by its owner; this seat did not
  modify it.
- This seat has no verdict authority: no admission, axis-score change or trend verdict is made.
