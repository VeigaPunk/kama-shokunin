# K05C2Noop — C2 calibration falsification

**Axes:** calibration (primary); operability (checker behavior).

**Attacked claim/clause:** frozen C2 calibration predicate/sentence, specifically the requirement that the calibration row's latest outside-closure pointer/token/count are recomputed by a runnable checker from lane tree plus explicitly named fleet HEAD, and that the row contains the correctly bound latest pointer and including round. No discernment progress is claimed; S517/S518 spot-check remains unrecorded.

## Smallest counterexample

At measured lane tip `2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35`, the counter passes without any row edit:

```text
python3 tools/round59-c2-counter.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 --fleet-ref HEAD
exit=0
tip=2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 fleet=0f99f606120d0c884656c6e7a290f0e8f33c2181 maxN=57 manifest=rejected-honest-stop
rows=44 mismatches=0 met=True
row_missing=0 typed_count=0 pinned_fleet_revision=0 pointer_missing=0 pointer_round=0 pointer_verdict=0 including_round=0 count_command=0
```

I also created a disposable fixture under `/fast/scratch/hyaku/kama-r59/K05C2Noop/fixture`, copied measured SCORECARD and committed lesson-tree bytes into it, changed **only the calibration row** to append `STATIC ASSERTION: this pointer/count is hard-coded, not dynamically derived.`, committed only inside that fixture after asserting `git -C "$F" rev-parse --show-toplevel` equaled `$F`, and ran:

```text
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round59-c2-counter.py --repo "$F" --tip 2eed869e2094075cf9b07062e216ccd71ade5837 --fleet-ref HEAD
exit=0
tip=2eed869e2094075cf9b07062e216ccd71ade5837 fleet=0f99f606120d0c884656c6e7a290f0e8f33c2181 maxN=57 manifest=rejected-honest-stop
rows=44 mismatches=0 met=True
row_missing=0 typed_count=0 pinned_fleet_revision=0 pointer_missing=0 pointer_round=0 pointer_verdict=0 including_round=0 count_command=0
```

The fixture is scratch-only and was removed before reporting. No lane source, frozen counter/fixture, fleet file, or commit was changed.

## Evidence and impact

Counter source evidence: `tools/round59-c2-counter.py` lines 49–62 derives spotcheck file names/max round and looks up the closure verdict, but lines 63–72 only test (a) whether the row contains a numeric typed-count literal, (b) any 40-hex literal, (c) whether a matching pointer and `including round` text agree with the current values, and (d) whether the counter command string appears. It does not evaluate the row's claimed count derivation or require pointer/token provenance to be dynamically generated. The counter can only see the emitted row text, not whether its assertions are static. The appended explicit static assertion preserves all strings the checker recognizes, so it reaches `mismatches=0` despite the promised dynamic computation being false.

The unedited measured row is an even smaller instance: it statically spells the currently correct round 57 and `rejected-honest-stop` and passes; agreement at one tip does not establish recomputation. This is a **counter/checker false acceptance**, not evidence that the present pointer values are factually wrong. It directly invalidates the frozen C2 predicate; calibration is impacted, with operability implicated because the checker does not test the demanded property.

## Smallest safe correction

Do not admit C2 on this counter. Replace row-text-presence checks with an executable contract that independently recomputes and compares the row's emitted count/pointer/verdict against the lane tree and named fleet ref, and retain pre-data controls that alter each field while preserving the genuine S517/S518 records. A self-asserted prose marker is not evidence of dynamic derivation. This finding does not alter the frozen claim, target, controls, or fixtures.

**Installations:** none.