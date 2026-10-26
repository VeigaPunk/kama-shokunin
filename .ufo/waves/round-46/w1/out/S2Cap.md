# S2Cap — round-46 capability entry for `append-only-audit`

**Verdict: the entry is drafted and verified end-to-end on a scratch clone — `capability-repertoire-audit` reads `listed 10 observed 10 missing 0 unsubstantiated 0 met True`, the lane's `round42-selfdesc-reconcile` reads `mismatches=0 met=True`, and the frozen C2 counter reads `selftest=1 fixture=1 lane=1 table=1 met=True` — but only together with four head-section/near-file edits the counters force, plus a separate pre-existing calibration re-anchor that no capability entry can carry alone.**

Axes: calibration (capability repertoire stays an honest census of what runs). Evidence quality: every claim below is a command output in `w1/out/S2Cap/receipt/`.

## Behaviour delivered

Canonical repertoire entry, to be spliced inside L1's `## Round 46` section at end of `SCORECARD.md` (`w1/out/S2Cap/proposed-round46-canonical.md`):

```
**Capabilities — canonical list as of round 46**

Same four columns as the round-43 canonical list, which stays byte-intact; one row is added.

| Capability | What it can now do | Evidence pointer | First-working round |
|…|  (the nine round-43 rows, verbatim)  |…|…|
| append-only-audit | Set the lane's five append-only self-description files (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md) against its git history: list every commit that deletes >= 20 lines from one of them, report how many of those lines the file holds again at the audited revision and which later commit first restored all of them, and exit 1 on a partial or unrestored mass deletion | `tools/append-only-audit.py`; `tools/round46-append-audit-check.py`; run `python3 tools/append-only-audit.py --repo . --to <commit> --json` | 46 |
```

Matching head mirror row, byte-identical, appended after the `hexrun-census` row, plus the mirror intro's `round-43` → `round-46` (`w1/out/S2Cap/proposed-scorecard-head-edits.md`).

Why "first working round 46" is substantiated rather than asserted: the tool exists at `4a2a4d55` and runs — `python3 tools/append-only-audit.py --selftest` → ten `pass` lines and `AOA_SELFTEST pass=10 fail=0` exit 0 (`receipt/06-appendonly-selftest.out`); on the lane's own history at that commit it reports the five events the C1/C2 brief describes, exit 1 for the two partials (`receipt/07-appendonly-lane-base.json`: `0718b6ab` LOG/QUALITY/README restored by `82b5e9d3`, `0718b6ab` SCORECARD `2416/2417` partial, `dd9f5dc6` SCORECARD `24/31` partial).

## Gates run (clone of the lane at `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`, patch applied, synthetic commits)

| State | `capability-repertoire-audit` | `round42-selfdesc-reconcile` | frozen `round46-append-audit-check` |
|---|---|---|---|
| base `4a2a4d55` | `listed 9 observed 9 … met True` (exit 0) | `mismatches=1` (exit 1) — pre-existing `r41` | n/a (no row) |
| `78be6d4e` = `proposed.patch` | `listed 10 observed 10 missing 0 unsubstantiated 0 met True` (exit 0), `canonical_line 2452`, `capability_tables 12` | `mismatches=1` (exit 1) — same single pre-existing `r41` | `selftest=1 fixture=1 lane=1 table=1 … met=True` (exit 0) |
| `ba67ee83` = `proposed-full.patch` | `listed 10 observed 10 … met True` (exit 0) | `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=45 met=True` (exit 0) | `… met=True` (exit 0) |

The patched tree adds **zero** mismatches to the baseline: `mismatches=1` before and after the capability patch, from the same single `r41` detail (`receipt/02-…`, `receipt/04-…`).

Specificity arms (each a commit in the same clone, `receipt/13`–`receipt/20`):

- Mirror row removed → repertoire census still `met True`; the lane's `caps` leg fails (`head names` lack `append-only-audit`). The mirror row is load-bearing, but only for the lane's own counter.
- Canonical fragment removed (mirror row kept) → `listed 9 observed 10 missing 1 met False`; `retired=1 caps=1`. The canonical table is load-bearing for the census.
- Evidence cell stripped of every resolving path → `unsubstantiated 1 met False`. The evidence pointer is load-bearing.
- Non-existent token added next to the real one → census still `met True, unsubstantiated 0`; only the lane's `province` leg catches it (`province=1`).

## Touched surfaces

Written: only `w1/out/S2Cap/` (proposals, patches, `receipt/`, `receipt.md`) and this report. The lane was read-only: `git show`/`git log`/`git ls-tree` and the counters with `--repo <lane>`; no index, jj state, or tracked file was modified. Fixture commits were made only in the scratch clone with `-c user.name/-c user.email` and toplevel asserted before the first one.

Forced companion edits (all in `proposed.patch`, each mapped to the leg that fails without it):

1. `SCORECARD.md:117` mirror intro `round-43` → `round-46` (accuracy; not counter-enforced).
2. `SCORECARD.md:129` mirror row (leg `caps`).
3. `SCORECARD.md:57` `6 axes and 9 capabilities` → `10` (leg `retired`).
4. `SCORECARD.md:135` `first-working rounds … 43` → `… 43, 46`, `kept current in round 43` → `round 46`, `entered in round 43` → `round 46` (leg `saturation`).
5. `PROVINCE.md:17` lane-instruments clause naming both tools (leg `province`), which forces `SCORECARD.md:17` coverage-row `PROVINCE.md sha256 36d6bb3a…` → `659a5101…`, 186 lines unchanged (leg `r41` hash).

## Findings

**F1 — pre-existing, blocks `met=True` at both `4a2a4d55` and the lane tip `96d32918` (not caused by this entry).** `SCORECARD.md:18` cites `run python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))" → `31`` while the tree holds 32 such files; the 32nd arrived in `0163fea2` (round-45 verifier spot-check) *after* the round-45 measured commit `21945c61`, where 31 was correct (`git ls-tree 21945c61 corpus/lessons/ | grep -c verifier-spotcheck` → 31; `… 4a2a4d55 …` → 32). Show: `python3 tools/round42-selfdesc-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 96d329186e777080c03ac89fdd2366714d504dc3` → `r41=1 … mismatches=1 met=False`, detail `calibration run … no stdout line == '31'`. The row's own prose ("that figure is the number of … blobs at the measured commit") cannot stay true and passing once the tip moves past the measured commit — the counter evaluates the run at the tip. Proposed fix, verified: `31` → `32` plus `re-anchored round 46` (`w1/out/S2Cap/proposed-calibration-reanchor.patch`); with it `mismatches=0 met=True` (`receipt/10-selfdesc-full.out`).

**F2 — the frozen C2 counter's `table` leg is weaker than its contract sentence.** `tools/round46-append-audit-check.py:58-59` says "entered in the SCORECARD capability table"; lines 246-250 accept *any* SCORECARD line that starts with `|`, contains `append-only-audit` and ends in `46`. At arm `d459fa49` the canonical repertoire table has no such row (the head mirror table does) and the counter still reads `table=1 … met=True` (`receipt/18-armB-no-canon-c2counter.out`). Show: `python3 tools/round46-append-audit-check.py --repo <clone> --tip d459fa49…`. Proposed fix (a finding against a frozen counter, not applied): require the line to sit in the table that follows the highest `canonical list as of round N**` marker — the same rule `capability-repertoire-audit.py` already implements — or add a leg that the capability census reads `listed=10`.

**F3 — `capability-repertoire-audit.py`'s `unsubstantiated` leg is `any()`, not `all()`** (`evaluate()`: `if not any(path_exists(root, rev, t) for t in tokens)`). One resolving token immunises a row against any number of bogus ones: arm `b3c5b7c9` adds `tools/does-not-exist.py` and the census still reads `unsubstantiated 0 met True`, while the lane's `province` leg is what notices (`province=1`). Show: `receipt/19-armD-bogus-token-capaudit.out`, `receipt/20-…`. Proposed fix: count a row unsubstantiated unless *every* tool/registry token it cites resolves.

**F4 — `restored_at_tip` moves for ordinary edit rounds, which the ledger has no way to distinguish from losses.** The four SCORECARD lines this entry rewrites (17, 57, 117, 135) and the calibration line (18) are lines that `0718b6ab` deleted and `82b5e9d3` restored, so the verbatim counter credits five fewer restorations: `0718b6ab SCORECARD.md 2417/2416 partial` at base → `2417/2412` after the capability patch (`receipt/07-…`, `receipt/08-…`) → `2417/2411` after the calibration re-anchor (`receipt/12-…`). Status stays `partial` and the exit code stays 1, so no verdict moves; but any reader of C2's `restored_at_tip` should know that a legitimate line rewrite is indistinguishable from a loss in that number, and that the number will keep falling as rounds edit repaired lines. Not a defect against the frozen contract (which is exact-text by design); recorded here so the C2 seat's ledger reading is not over-read.

## Out of scope / not done

- `## Round 46` section body, head banner `Latest measured round: 46`, `### Planned (round 47)`: keyed to `maxN`, i.e. to L1's section heading; my clone arms deliberately stop at `maxN=45` so the only deltas measured are the ones the capability row causes.
- C1 (b11906 ledger, the 20 rows to read) and the C2 measurement at the integration commit: not this seat's.
- No claim is made that the lane's round-46 C2 is met; the counter run above is on a synthetic scratch commit, not the integration commit.
- No tool installed or upgraded (python3, git only); no service touched; scratch removed.

## Artifacts

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S2Cap/`:

- `proposed-round46-canonical.md` — the canonical fragment (heading, prose, 10-row table), splice-ready.
- `proposed-scorecard-head-edits.md` — items 1–7 with line numbers, the leg each satisfies, and the measured failure without it.
- `proposed-province-clause.md` — the `PROVINCE.md:17` clause and its digest consequence.
- `proposed.patch` (80 lines, base → `78be6d4e`) — capability entry + head counts + PROVINCE clause + coverage digest; applies clean to `4a2a4d55`.
- `proposed-calibration-reanchor.patch` (13 lines) — the separable F1 fix.
- `proposed-full.patch` (82 lines, base → `ba67ee83`) — both; reverse-applies to `ba67ee83`.
- `receipt/01…20` — every command's stdout/JSON above.
- `receipt.md` — file → command → first output line → exit code index.
