# R57Item43CounterRepair — distinct case 64 (independent evidence)

Separate evidence file for case 64, produced without importing `tools/round42-selfdesc-reconcile.py` or its repaired prototype. Axes: calibration + operability. Read-only on the lane; no shared writes, no installs.

## Independent derivation

Command set (plain git plumbing + text tools, no counter code), captured verbatim in
`.ufo/waves/round-57/measured/R57Item43/case64-independent.out`:

```
git show "$TIP":SCORECARD.md | grep -c '^## Round '
git show "$TIP":SCORECARD.md | grep -o '^## Round [0-9]*' | awk '{print $3}' | sort -n | tail -1
git show "$TIP":SCORECARD.md | grep -o 'Latest measured round: [0-9]*' | head -1
git show "$TIP":SCORECARD.md | grep -c '^## Round 46 '
git show "$TIP":SCORECARD.md | grep -o 'maxN=46' | wc -l
grep -o 'maxN=[0-9]*' .ufo/waves/round-57/controls/c1-noop.py
grep -c 'glob\|open(\|subprocess\|SCORECARD' .ufo/waves/round-57/controls/c1-noop.py
git show "$TIP":SCORECARD.md | grep -c 'canonical list as of round'
git show "$TIP":SCORECARD.md | grep -o 'canonical list as of round [0-9]*' | awk '{print $6}' | sort -n | tail -1
```

Observed (tip `8a7f19760242bbe523fa2d7d1b22528b587633c1`):

```
round_headings=58
max_round_heading=57
head_declares=Latest measured round: 57
round46_headings=1
round46_measured_text=1 occurrences of literal maxN=46 in SCORECARD
noop_control_literal=maxN=46
noop_reads_input=0
canonical_headings=10
highest_canonical=49
```

## What this independently establishes

1. The derived latest-round value at this tip is **57 from 58 headings**, and the SCORECARD head declares the same 57 — the counter's `maxN=57` is a tree fact, not an instrument artefact.
2. The literal `46` appears exactly once in SCORECARD, inside the round-46 regression record `round-42 self-description counter mismatches=0 maxN=46 met=True`; `## Round 46` still exists as a *historical* heading. 46 is therefore a past-tense value.
3. The frozen no-op control prints `maxN=46` and reads nothing (`noop_reads_input=0`); its `met=True, exit 0` is a constant, so "expected 46" is the no-op's literal, not an observation of the tree. The frozen claim's `maxN=56 instead of expected 46` is falsified in both directions: 56 was the correct frozen-tip value and 46 is not derivable at any live tip read this round (56 at `b89bdab2`/`7b74e2f2`, 57 at `16efcf5e`/`77e7f5ee`/`8a7f1976`).
4. Canonical heading selection is a different namespace: 10 `canonical list as of round N` headings, highest 49 — unchanged by any `maxN` repair, independently matching `semantics.out` (`canon_round=49, rows=11`).

## Cross-file consistency (independent of the prototype)

- Frozen `controls/base-c1.out` and a fresh run at `b89bdab2` agree byte-for-byte (`mismatches=1 maxN=56 met=False`, exit 1).
- Sibling fixtures read only: `canonical-noop` selects canonical round 49, `no-canonical` selects 48; both keep 57 round headings, max 56 (at the frozen tip).
- Constructed stale-46 fixture (`fd956dd1`, 48 headings, max 46) makes the frozen counter emit `banner=1 planned=1 mismatches=3 met=False` — the counter itself rejects a head/heading inconsistency, so a 46-reporting counter on today's tree would be red, not green.

## Remaining uncertainty

- Single observation channel: all numbers derive from the SCORECARD blob at a tip. If a future edit adds a `## Round N` heading for a non-current section with N above the latest, the maximum would inflate; no canonical-round declaration currently prevents that (recorded as a limit in the main report).
- The literal witness handling distinguishes "no witness field" from "witness=0"; a claimant that fabricates `reads=<n>` is not detectable by this check alone.

Report: .ufo/waves/round-57/reports/R57Item43CounterRepair-case64.md
