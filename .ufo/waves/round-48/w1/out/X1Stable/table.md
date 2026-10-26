# X1Stable — v3 graded/ungraded stability across eight tips (round 48)

Tool: `tools/append-only-audit.py` (schema append-only-audit/v3, sha256 below), contract passed as a
file: `registry/append-only-contract.tsv` at the build tip 380bcdff (frozen 5-row v3 contract), so the
only thing that moves between runs is `--to`.

Command per tip:
```
python3 <lane>/tools/append-only-audit.py --repo $S/lane --to <rev> \
        --contract <lane>/registry/append-only-contract.tsv --json
```

| # in rev-list | tip | note |
|---|---|---|
| 1 | `d48e8cc32fef` | oldest sampled revision |
| 5 | `052cb1e94c0a` |  |
| 10 | `0fddf257a0c5` | first tip with 5 events (post-0718b6ab restorations) |
| 15 | `4a2a4d55d09d` |  |
| 20 | `42ea1204aef3` | first tip where the r45 banner loss bites (regressed=1) |
| 25 | `46a924e027f0` |  |
| 30 | `33e005827742` | round-47 closure (round-48 base) |
| 32 | `380bcdff9c8a` | round-48 build tip (measured commit) |

## Per-event table at the eight tips

Fields as printed by v3: `deleted graded ungraded restored_max held_at_to status` (+ process exit code).

| tip | event | file | deleted | graded | ungraded | restored_max | held_at_to | status | exit |
|---|---|---|---|---|---|---|---|---|---|
| `d48e8cc3` | `dd9f5dc6` | SCORECARD.md | 31 | 14 | 17 | 14 | 14 | restored | 1 |
| `052cb1e9` | `dd9f5dc6` | SCORECARD.md | 31 | 14 | 17 | 14 | 14 | restored | 1 |
| `0fddf257` | `dd9f5dc6` | SCORECARD.md | 31 | 14 | 17 | 14 | 14 | restored | 1 |
| `0fddf257` | `0718b6ab` | LOG.md | 2292 | 2292 | 0 | 2292 | 2292 | restored | 1 |
| `0fddf257` | `0718b6ab` | SCORECARD.md | 2421 | 2349 | 72 | 2349 | 2349 | restored | 1 |
| `0fddf257` | `0718b6ab` | corpus/QUALITY.md | 375 | 375 | 0 | 375 | 375 | restored | 1 |
| `0fddf257` | `0718b6ab` | corpus/README.md | 663 | 663 | 0 | 663 | 663 | restored | 1 |
| `4a2a4d55` | `dd9f5dc6` | SCORECARD.md | 31 | 14 | 17 | 14 | 14 | restored | 1 |
| `4a2a4d55` | `0718b6ab` | LOG.md | 2292 | 2292 | 0 | 2292 | 2292 | restored | 1 |
| `4a2a4d55` | `0718b6ab` | SCORECARD.md | 2421 | 2349 | 72 | 2349 | 2349 | restored | 1 |
| `4a2a4d55` | `0718b6ab` | corpus/QUALITY.md | 375 | 375 | 0 | 375 | 375 | restored | 1 |
| `4a2a4d55` | `0718b6ab` | corpus/README.md | 663 | 663 | 0 | 663 | 663 | restored | 1 |
| `42ea1204` | `dd9f5dc6` | SCORECARD.md | 31 | 14 | 17 | 14 | 14 | restored | 1 |
| `42ea1204` | `0718b6ab` | LOG.md | 2292 | 2292 | 0 | 2292 | 2292 | restored | 1 |
| `42ea1204` | `0718b6ab` | SCORECARD.md | 2421 | 2349 | 72 | 2349 | 2348 | restored | 1 |
| `42ea1204` | `0718b6ab` | corpus/QUALITY.md | 375 | 375 | 0 | 375 | 375 | restored | 1 |
| `42ea1204` | `0718b6ab` | corpus/README.md | 663 | 663 | 0 | 663 | 663 | restored | 1 |
| `46a924e0` | `dd9f5dc6` | SCORECARD.md | 31 | 14 | 17 | 14 | 14 | restored | 1 |
| `46a924e0` | `0718b6ab` | LOG.md | 2292 | 2292 | 0 | 2292 | 2292 | restored | 1 |
| `46a924e0` | `0718b6ab` | SCORECARD.md | 2421 | 2349 | 72 | 2349 | 2348 | restored | 1 |
| `46a924e0` | `0718b6ab` | corpus/QUALITY.md | 375 | 375 | 0 | 375 | 375 | restored | 1 |
| `46a924e0` | `0718b6ab` | corpus/README.md | 663 | 663 | 0 | 663 | 663 | restored | 1 |
| `33e00582` | `dd9f5dc6` | SCORECARD.md | 31 | 14 | 17 | 14 | 14 | restored | 1 |
| `33e00582` | `0718b6ab` | LOG.md | 2292 | 2292 | 0 | 2292 | 2292 | restored | 1 |
| `33e00582` | `0718b6ab` | SCORECARD.md | 2421 | 2349 | 72 | 2349 | 2348 | restored | 1 |
| `33e00582` | `0718b6ab` | corpus/QUALITY.md | 375 | 375 | 0 | 375 | 375 | restored | 1 |
| `33e00582` | `0718b6ab` | corpus/README.md | 663 | 663 | 0 | 663 | 663 | restored | 1 |
| `380bcdff` | `dd9f5dc6` | SCORECARD.md | 31 | 14 | 17 | 14 | 14 | restored | 0 |
| `380bcdff` | `0718b6ab` | LOG.md | 2292 | 2292 | 0 | 2292 | 2292 | restored | 0 |
| `380bcdff` | `0718b6ab` | SCORECARD.md | 2421 | 2349 | 72 | 2349 | 2349 | restored | 0 |
| `380bcdff` | `0718b6ab` | corpus/QUALITY.md | 375 | 375 | 0 | 375 | 375 | restored | 0 |
| `380bcdff` | `0718b6ab` | corpus/README.md | 663 | 663 | 0 | 663 | 663 | restored | 0 |

## The same question over all 32 tips of the range (`33e0058~30..380bcdff`)

Graded/ungraded per event across every tip at which the event exists — the full series is in
`res/all32-trajectory.json`; here is each event's distinct value set:

| event | file | tips | deleted | graded values | ungraded values | restored_max values | graded non-increasing | ungraded non-decreasing | restored_max falls |
|---|---|---|---|---|---|---|---|---|---|
| `dd9f5dc6` | SCORECARD.md | 32 | 31 | [14] | [17] | [14] | True | True | False |
| `0718b6ab` | LOG.md | 25 | 2292 | [2292] | [0] | [0, 2292] | True | True | False |
| `0718b6ab` | SCORECARD.md | 25 | 2421 | [2349, 2421] | [0, 72] | [0, 2349] | True | True | False |
| `0718b6ab` | corpus/QUALITY.md | 25 | 375 | [375] | [0] | [0, 375] | True | True | False |
| `0718b6ab` | corpus/README.md | 25 | 663 | [663] | [0] | [0, 663] | True | True | False |

`held_at_to` and the exit code are the fields that do move (same events, same tool, same contract):

| event | file | held_at_to transitions (tip where the value starts) |
|---|---|---|
| `dd9f5dc6` | SCORECARD.md | d48e8cc3:14, 0718b6ab:0, 82b5e9d3:14 |
| `0718b6ab` | LOG.md | 0718b6ab:0, 82b5e9d3:2292 |
| `0718b6ab` | SCORECARD.md | 0718b6ab:0, 82b5e9d3:2349, 4340cf2f:2348, 380bcdff:2349 |
| `0718b6ab` | corpus/QUALITY.md | 0718b6ab:0, 82b5e9d3:375 |
| `0718b6ab` | corpus/README.md | 0718b6ab:0, 82b5e9d3:663 |

## Why the exit code moves (32 tips)

| tip | commits | files | events | regressed | bad_declarations | partial | unrestored | ungraded_lines | exit |
|---|---|---|---|---|---|---|---|---|---|
| `d48e8cc3` | 280 | 82 | 1 | 0 | 3 | 0 | 0 | 17 | 1 |
| `6b8ccfb3` | 281 | 83 | 1 | 0 | 3 | 0 | 0 | 17 | 1 |
| `1641aa07` | 282 | 83 | 1 | 0 | 3 | 0 | 0 | 17 | 1 |
| `58ffddd6` | 283 | 83 | 1 | 0 | 3 | 0 | 0 | 17 | 1 |
| `052cb1e9` | 284 | 83 | 1 | 0 | 3 | 0 | 0 | 17 | 1 |
| `85977699` | 285 | 83 | 1 | 0 | 3 | 0 | 0 | 17 | 1 |
| `21945c61` | 286 | 83 | 1 | 0 | 3 | 0 | 0 | 17 | 1 |
| `0718b6ab` | 287 | 84 | 5 | 1 | 3 | 0 | 4 | 17 | 1 |
| `82b5e9d3` | 288 | 84 | 5 | 0 | 3 | 0 | 0 | 89 | 1 |
| `0fddf257` | 289 | 84 | 5 | 0 | 3 | 0 | 0 | 89 | 1 |
| `a553bd7c` | 290 | 84 | 5 | 0 | 3 | 0 | 0 | 89 | 1 |
| `221525bc` | 291 | 84 | 5 | 0 | 3 | 0 | 0 | 89 | 1 |
| `0163fea2` | 292 | 85 | 5 | 0 | 3 | 0 | 0 | 89 | 1 |
| `57909443` | 293 | 85 | 5 | 0 | 3 | 0 | 0 | 89 | 1 |
| `4a2a4d55` | 294 | 85 | 5 | 0 | 3 | 0 | 0 | 89 | 1 |
| `96d32918` | 295 | 85 | 5 | 0 | 3 | 0 | 0 | 89 | 1 |
| `7d057345` | 296 | 85 | 5 | 0 | 3 | 0 | 0 | 89 | 1 |
| `4340cf2f` | 297 | 86 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `4991ecc2` | 298 | 86 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `42ea1204` | 299 | 86 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `e8fa87ef` | 300 | 86 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `172b8ad0` | 301 | 87 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `bbcc6dc2` | 302 | 87 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `3a09a1d9` | 303 | 87 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `46a924e0` | 304 | 87 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `383f1fc7` | 305 | 88 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `3442d707` | 306 | 88 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `76a7aaff` | 307 | 88 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `6b7e6cf8` | 308 | 88 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `33e00582` | 309 | 89 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `12284ba3` | 310 | 89 | 5 | 1 | 0 | 0 | 0 | 89 | 1 |
| `380bcdff` | 311 | 89 | 5 | 0 | 0 | 0 | 0 | 89 | 0 |

Reading: at tips 1–17 the exit 1 is produced by `bad_declarations=3` only (the frozen v3 contract is
graded against revisions where `corpus/README.md:761`, the declaring line, does not yet say append-only —
binding is evaluated at `<to>`, contract row and pointer are the tip's). At tip 8 (`0718b6ab`) three
`unrestored` events and the same 3 unbound declarations. At tips 18–31 (`4340cf2f`..`12284ba3`) a single
`regressed=1`: `0718b6ab SCORECARD` `held_at_to=2348 < restored_max=2349`, i.e. the round-45 banner that
rounds 46–47 overwrote. Only the measured tip `380bcdff` exits 0 — after the build appended the two
superseded banners (`held_at_to` back to 2349). No tip in the range changes any event's graded/ungraded.
