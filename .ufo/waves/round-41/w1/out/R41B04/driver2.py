#!/usr/bin/env python3
"""R41B04 driver 2: w1-peeled survival rates under pins-current/composed,
plus a feature census at the candidate receipt's seed (1072186973)."""
import random
import harness

paths = harness.build_variants()

legs = [("w1-peeled", "pins-current"), ("w1-peeled", "pins-current+no-unreadable")]
rows, _ = harness.run_legs(paths, legs, range(1, 31))
print(harness.pivot(rows))

mod = harness.get_mod(paths, "pristine")
rng = random.Random(1072186973)  # seed recorded in .ufo/waves/round-41/c2/candidate.out
feats = [harness.case_features(*mod.make_case(rng, i)) for i in range(mod.CASES)]
agg = {}
for f in feats:
    for k, v in f.items():
        agg[k] = agg.get(k, 0) + v
print("CANDIDATE-SEED 1072186973 pristine census:", agg)
