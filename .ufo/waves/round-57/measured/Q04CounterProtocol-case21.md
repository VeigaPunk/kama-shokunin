# Q04CounterProtocol — distinct case 21

Scope: read-only independent attack on the frozen round-57 do-nothing controls and current calibration counter. No source files changed; no tooling installed.

## Evidence

Command:

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-57/controls/c1-noop.py
```

Exact stdout and exit:

```text
mismatches=0 maxN=46 met=True
exit=0
```

The script body is only a comment identifying it as a do-nothing control and `print("mismatches=0 maxN=46 met=True")`; it does not inspect the registry, self-description, or canonical table. This directly reaches the frozen C1 target.

Frozen control receipts independently state:

```text
noop-c1.out:
fixture=c1-noop.py
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-57/controls/c1-noop.py
mismatches=0 maxN=46 met=True
exit=0

noop-c2.out:
control=no-op instrument
canonical_table_reads=0
self_description_reads=0
summary=mismatches=0 maxN=46 met=True
exit=0
```

Therefore the frozen C2 no-op also reaches the advertised target despite zero canonical-table and self-description reads. Both frozen targets are reachable by a do-nothing control; they fail the prompt §9 pre-freeze discrimination condition.

Current `tools/round42-selfdesc-reconcile.py` does perform repository reads in `evaluate()` (notably canonical `SCORECARD.md` via `canon(sc)`, the SOURCE census, and other checks), but its round-57 frozen base receipt is `base-c1.out`, whose observed line is `mismatches=1 maxN=56 met=False` (exit 1), with detail that it expects an unrelated `verifier-spotcheck.md` count of 42. The target's claimed corrected maxN=46 is not reached by this baseline counter. That does not rehabilitate C1/C2: the independently executed hard-coded control and frozen C2 receipt both report met=True.

The applicable §9 text (fleet prompt `.ufo/prompts/kama-round-57.md`, section 9) requires the cheapest control that skips claimed work to be scored before freeze; if it meets the target, the counter or target is wrong and must be fixed before data. Verdict: target falsified for both frozen claims, on the supplied receipts and direct C1 execution. This is evidence, not a judgment/admission.
