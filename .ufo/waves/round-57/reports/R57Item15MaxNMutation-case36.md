# R57Item15MaxNMutation — distinct case 36

Mutation: in an isolated clone rooted at `7b74e2f2515a6f598918488fa5144658ff29925f`, rename only the `## Round N` heading lines for N=47,48,49,50,51,52,53,55,56 to `## Archived entry N`. This preserves the content and section boundaries but makes the counter-derived maximum round heading 46. Mutation commit: `b1a79db2389b6ddb134890dad943980c8b3ce853`. Fixture root was verified with `git rev-parse --show-toplevel` before fixture mutations.

The source counter defines maxN as the greatest number in SCORECARD headings matching `^## Round (\\d+)`. Baseline at the frozen post-repair tip:

```text
$ python3 tools/round42-selfdesc-reconcile.py --repo <fixture> --tip 7b74e2f2515a6f598918488fa5144658ff29925f
 tip=7b74e2f2515a6f598918488fa5144658ff29925f
 r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=56 met=True
exit=0
```

Mutated revision:

```text
$ python3 tools/round42-selfdesc-reconcile.py --repo <fixture> --tip b1a79db2389b6ddb134890dad943980c8b3ce853
 tip=b1a79db2389b6ddb134890dad943980c8b3ce853
 r41=0 banner=1 planned=1 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=2 maxN=46 met=False
 detail: banner: head lacks 'Latest measured round: 46'
 detail: planned: section does not name '### Planned (round 47)'
exit=1
```

The frozen no-op instrument, replaying the previously observed exact `c1-noop.py` body, says `mismatches=0 maxN=46 met=True` with exit 0 on both baseline and mutation (outputs byte-identical, `cmp` exit 0). It therefore escapes case 36. This does not show a defect in the actual round-42 counter: the real counter rejected the inconsistent mutation. It does show the no-op's reported `46` is a fixed assertion unrelated to the committed maxN; the source counter's documented/implemented meaning of maxN is a maximum round-heading number.

Receipts and exact replay script: `.ufo/waves/round-57/w1/out/R57Item15MaxNMutation/`. The fixture is scratch-only; no lane source file or shared control was edited.

Case-36 evidence: .ufo/waves/round-57/reports/R57Item15MaxNMutation-case36.md
