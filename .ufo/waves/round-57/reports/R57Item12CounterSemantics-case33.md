# R57Item12CounterSemantics — case 33 independent test

Distinct case 33 of round 57, seat `R57Item12CounterSemantics`. Companion to `R57Item12CounterSemantics.md` (main report). This file records an independent test of the same question, separate from the tool's own code path.

Question tested: does `tools/round42-selfdesc-reconcile.py` (its `met=` verdict) agree with independently derived semantic facts about its section selection and maxN, when run on the same mutated SCORECARD commits?

## Independence

- The oracle is `oracle.py` (scratch copy; receipt in `measured/R57Item12/oracle.py`). It does not import, read, or call `tools/round41-*` or `tools/round42-*`. It parses SCORECARD commits with its own fence-aware scan and checks six semantic rules (O1-O6) that the tool does not encode in the same way.
- Inputs: the 12 mutant commits built by `mutants.py` from the pinned tip `8640e34cad02adcd247ba0862da63f6fb2aab0df`, plus the pinned tip itself. The tool's verdicts are read from `measured/R57Item12/summary.tsv`, which the tool itself wrote.
- Comparison is differential: each commit's oracle flags minus the pinned base's oracle flags. The base has 48 O6 flags (unresolved `.ufo/` citations that exist in the working tree or are historical) and 1 O5 flag (SCORECARD line 2969, a fenced `## Round 30` heading). Those are subtracted.

Oracle rules:

- O1 maxN/banner: highest `## Round N` heading, space optional (`Round ?N`), outside fences; `Latest measured round: N` in the head must equal it.
- O2 canonical: highest `canonical list as of round N` header in any punctuation form; its table names must equal the Capabilities mirror names.
- O3 live plan: `### Planned (round maxN+1)` must sit under a `## Round maxN` section, not elsewhere.
- O4 Retired: exactly one `## Retired` heading; every `N capabilities` token in it must equal the canonical row count (exact token).
- O5 fence: count of `## ` lines inside fenced blocks (shadowing risk).
- O6 receipts: every backticked `.ufo/` path in SCORECARD must exist at the commit (all rounds, not only 40/41).

The oracle has no rule for the tool's forbidden-phrase checks (`Both assigned axes`, `every model endpoint is dead`). That is a known blind spot and is reported as such below.

## Results

Command: `CL=/fast/scratch/hyaku/kama-r57/R57Item12CounterSemantics/clone python3 oracle.py out/summary.tsv 8640e34cad02adcd247ba0862da63f6fb2aab0df` → exit 0; output `measured/R57Item12/oracle.tsv`.

Base (pinned tip, unmodified): `maxN=57 canon=r49 rows=11 flags=49` (48 O6 + 1 O5; subtracted).

| Mutant | Tool met | Tool mismatches | Oracle new flags | Agreement |
|---|---|---|---|---|
| M0-base-unmodified | True | 0 | none | agree (clean) |
| M1-maxn-bump-plain-heading | False | 3 | O1, O3 | agree (detect) |
| M2-round-nospace-heading | True | 0 | O1, O3 | **disagree**: tool ignores `## Round58` (regex needs a space); oracle counts it. The file contains `## Round24` (line 1245) in the same form |
| M3-canon-colon-decoy | True | 0 | O2, O4 | **disagree**: colon-form canonical header ignored by `canon()` |
| M3b-canon-bold-decoy | False | 2 | O2, O4 | agree (detect) |
| M4a-planned-heading-moved-to-eof | True | 0 | O3 | **disagree**: plan heading accepted outside its section |
| M4b-planned-pointer-removed | False | 1 | O3 | agree (detect) |
| M5a-retired-duplicate-at-eof | True | 0 | O4 (2 Retired headings) | **disagree**: duplicate heading ignored (`[:1]`) |
| M5b-retired-substring-16-111 | True | 0 | O4 (token 111 ≠ 11) | **disagree**: substring check passes |
| M5c-retired-false-live | False | 2 | none | **oracle blind spot**: forbidden-phrase rule not modeled; tool stricter here |
| M6-fenced-decoy-shadows-retired | True | 0 | O5 (+2 fenced headings) | **disagree**: fenced decoy shadows live section |
| M7a-receipt-cites-round56-missing | True | 0 | O6 (`.ufo/waves/round-56/does-not-exist.out`) | **disagree**: receipts only for rounds 40/41 |
| M7b-receipt-cites-round41-missing | False | 1 | O6 (`.ufo/waves/round-41/does-not-exist.out`) | agree (detect) |

Counts: 12 mutants + pinned base. Agreements 6 (M0, M1, M3b, M4b, M7b; M0 clean). Tool misses that the oracle flags: 7 (M2, M3, M4a, M5a, M5b, M6, M7a). Oracle blind spot: 1 (M5c, where the tool is stricter). No case where the tool flags and the oracle has no flag except the phrase rule.

Per-mutant detail is in the tool receipts `measured/R57Item12/<label>.out` (`exit=` line included) and diffs `<label>.diff`.

## Specific sub-results

- M5b mechanism (verified): the tool's Retired check is `f"{len(names)} capabilities" not in rt`. With 11 names, `"11 capabilities"` is found inside `"111 capabilities"`. In M3b the decoy canonical table has 1 row, so the check is `"1 capabilities" in "None. 6 axes and 11 capabilities …"`, which is also a substring match; `retired=0` in M3b is therefore a false pass, not a detection. Its saturation and caps mismatches are the real detections (`measured/R57Item12/M3b-canon-bold-decoy.out`).
- M4b mechanism (verified): with the §Planned pointer text removed, `ph = "### Planned (round 58)"` is no longer a substring of the `## Planned` section, so `planned=1`. With the pointer kept, the check passes even though the only heading is at EOF (M4a). The planned check is satisfied by the superseded pointer prose, not by the plan's location.
- M6 mechanism (verified): `sections()` splits on any line starting `## `, including inside a fenced block; the fenced decoy is `sections(sc,"Retired")[0]`.
- M7a mechanism (verified): `RECEIPT_ROUNDS = (40, 41)` (tool line 75); a Round 56 section is never scanned.

## Consequence for the claim under test

The independent oracle agrees with the tool's verdict on the base and on the mutants the tool was designed to catch (M1, M3b, M4b, M7b). It disagrees on seven shortcut classes the tool does not catch. Because the base is clean (`met=True`, maxN=57 at the pinned tip), the seven survivors are not visible from the base receipts; they appear only under mutation. So the counter's green verdict at the pinned tip does not establish the semantic facts the counter's own docstring claims.

This does not show that the lane's current SCORECARD is wrong. It shows the counter cannot be relied on as evidence against these shortcut classes without repair.

## Receipts (wave path)

- `measured/R57Item12/oracle.py`, `oracle.tsv`, `mutants.py`, `summary.tsv`, `ufo-cites-check.txt`
- `measured/R57Item12/<label>.out` and `<label>.diff` for M0 … M7b, `B-b89bdab2-frozen-claim-base.out`, `B-7c873d7b-claim-freeze.out`, `B-pinned-tip.out`

## Limits

- Mutations were applied to a scratch clone only; the lane repo was not modified.
- The oracle is my own rule set, so "disagree" means "the tool's rule does not match this rule", not that either is the single correct semantics. The M5c row shows the oracle is incomplete.
- Tips moved during the seat (`7c873d7b` → `7b74e2f2` → `8640e34c`). All numbers here are pinned to `8640e34c` unless labelled otherwise.
- No installs or version changes were made for this file (system `git` and `python3` only).
