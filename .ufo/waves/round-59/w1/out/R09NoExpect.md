# R09NoExpect — Round 59 C1 falsification

Axes: operability and calibration. Targeted frozen clause: each named `run`/mutant leg must bind its own `--expect` to that leg’s observed `ld_audit` value and exit; outcome-unbound controls must reject.

**Mutation:** remove the value following `--expect` in one battery leg. **Checker classification: not scored; no error/reject/false-accept outcome established.** The frozen C1 counter reads `tools/round56-env-leg-battery.py` and all fixtures from committed blobs at `--tip` (`tools/round59-c1-counter.py:76-85`), then scores those fixed bytes. Its CLI has no battery override; `--checker` only substitutes the checker (`:49-50,60-68`). A scratch-edited battery therefore cannot be passed to that counter without changing frozen counter behavior/inputs. A pass of the committed battery would not establish outcome for the requested mutation.

Evidence: lane HEAD is `4a541190b6d494a4e99116249632e99aab80adcc`; the assigned C1 tip exists (`aca8d0067ea25627c5015c2193c843965148bc8e`). Frozen prompt names C1 counter command but this seat did not run it, because it cannot score this battery mutation. The outcome checker’s `calls_ok` predicate only checks that each captured argv contains `--expect` (`tools/round59-battery-outcome-check.py:187-198`); its fake subprocess treats a missing value as `expected=None` and returns 1 (`:69-76`). This suggests the checker’s instrumentation can observe rejection, but does not constitute an executed scored counter result on a changed leg.

Exact commands run:

```sh
git -C /home/vgpnk/Projects/shokunin rev-parse --show-toplevel
# /home/vgpnk/Projects/shokunin
git -C /home/vgpnk/Projects/shokunin rev-parse HEAD
# 0f99f606120d0c884656c6e7a290f0e8f33c2181
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse --show-toplevel
# /home/vgpnk/Projects/shokunin/kama-shokunin
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD
# 4a541190b6d494a4e99116249632e99aab80adcc
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show -s --format='%H %s' aca8d0067ea25627c5015c2193c843965148bc8e
# aca8d0067ea25627c5015c2193c843965148bc8e round-59: score counterfactual leg failures
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show -s --format='%H %s' 2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35
# 2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 round-59: capture mutant leg result correctly
```

No installs. No lane source edits or counter execution. No calibration/discernment progress claimed.