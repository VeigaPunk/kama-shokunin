# R05BenignEquivalence — round 58

Axis: operability (C1). Ran the frozen execution-bound battery checker/counter against the genuine battery, B1–B3, and the 11 enumerated no-op variants; scratch copy was extracted from build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a` under `/fast/scratch/hyaku/kama-r58/R05BenignEquivalence`.

- Command: `python3 "$S/tools/round58-c1-counter.py" --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a --checker "$S/tools/round58-battery-exec-check.py" --work "$S" --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-58/w1/out/R05BenignEquivalence/counter.txt` (with `S=/fast/scratch/hyaku/kama-r58/R05BenignEquivalence`, `TMPDIR="$S"`); exit 0.
- Output: `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`. Genuine, B1-rename-comment, B2-helper-leg, B3-concat-labels accepted (all exit 0); each N01–N11 rejected (each exit 1). No divergence observed; these benign variants are behavior-preserving under this execution-bound checker as tested.
- Initial attempt with `--repo "$S"` exited 2 (`could-not-evaluate: invalid tip`): extracted archive is not a Git repo. Corrected by using the read-only committed lane repo as blob source; counter creates and commits each fixture only inside its own scratch fixture directory.

Receipt: `.ufo/waves/round-58/w1/out/R05BenignEquivalence/counter.txt`.
