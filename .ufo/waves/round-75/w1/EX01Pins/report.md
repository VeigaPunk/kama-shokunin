# EX01Pins — round 75 C1 implementation

Axes: calibration (declared interpretation versus reversed reading), operability (exit map, owned scratch, no lane mutations).

## Files changed

- `tools/round75-interpretation-pins.py` — new executable counter.
- `.ufo/waves/round-75/w1/EX01Pins/report.md` — this advisory report.
- `.ufo/waves/round-75/w1/EX01Pins.md` — requested Report-trailer pointer to this report.

## Implemented behavior

The module embeds the frozen C1 blockquote as its one-line `PREDICATE`. P1 writes a SCORECARD fixture with the round-71 three-row bold canon and a round-60 demonstrated table containing those names and two extras. It imports both original r74 canon logic and an independently loaded mutated copy, requiring pristine total 3 and mutant total 5. Both source replacements are copied exactly from the frozen control's C1_MUTANTS entries.

P2 reuses the r74 module's inherited `_Fixture` helper, whose constructor verifies its own git toplevel before commits. The instrument and plan are present in c0; the receipt names c0; the next commit c1 is mentioned only as a recorded-at content id in the round's record. The receipt is `.ufo/waves/round-74/r.out`, so the exact backticked basename `r.out` resolves through the base module's wave-relative citation rule. The original and any-hex mutant run as full CLI subprocesses, including the frozen base audit. Required outcomes are original exit 0 and mutant exit 1 with `stale-revision`.

Scoring requires both declared outcomes and both specified mutant outcomes. A mismatch names its pin and declared, observed, and mutant values; escaped mutants fail. Missing dependencies, fixture/CLI execution failure, and misuse map to exit 2. `--repo`, `--work`, `--keep`, `--json`, and `--selftest` are supported. Imports suppress bytecode; temporary copies and git fixtures are confined to owned work. Nonempty explicit work directories are rejected without deletion.

The selftest includes predicate equality, the actual clean experiment, and a separately executed copied-counter cheat changing P1's declared value from 3 to 5. Its required red result is exit 1, `declared=1 killed=1 escaped=1`, and a P1 finding naming declared 5 / mutant 5. The parent selftest succeeds only if that cheat fails as required.

## Retained evidence and verification status

No verification command was executed. Higher-priority fleet instructions prohibit build/lint/test/formatter execution during the editing wave and assign post-integration gates to the parent. Consequently there is **no measured real-lane exit code or output line**, and **no measured selftest exit code or output line**. The following are commands for the parent, not passing receipts:

```text
TMPDIR=/fast/scratch/hyaku/kama-r75/EX01Pins python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round75-interpretation-pins.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin
TMPDIR=/fast/scratch/hyaku/kama-r75/EX01Pins python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round75-interpretation-pins.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --selftest
```

Create the named scratch root first and remove it after retaining outputs. Expected, **unobserved** clean line: `INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0`; expected selftest line: `INTERPRETATION_PINS_SELFTEST pass=3 fail=0`.

Actual retained tool evidence: the source creation returned `Successfully wrote 12048 bytes` and `Made executable via chmod +x`; the surgical edit response showed the receipt moved to the wave root and the plan moved before c0. These are write receipts, not runtime verification. No shell command was run, so no shell exit code is asserted.

Source evidence read: frozen plan in full; r74 canon `resolve()` and fixture constants; r74 binding `_claim_pass_v2`, audit, fixture usage and CLI; frozen C1_MUTANTS exact replacement tuples; critic attack §F2c; r72 `_Fixture` lines 543–572, citation resolution lines 347–382, and default record paths lines 217–224. The plan must be seeded before c0 because `plans/` is not a record-only surface.

## Risks, disagreements, and blockers

- Required runtime evidence remains blocked by verification ownership; the parent was notified directly. No semantic disagreement with the frozen C1 predicate.
- The r74 receipt module is concurrently owned by another seat; this implementation does not modify it. Parent integration runs must exercise the final shared bytes.
- No LSP interface is exposed in the mounted tool inventory. A discovery glob for `xd://*lsp*` returned `Path is not a directory: xd://`; this is a failed discovery, not proof an external LSP server is absent. Definitions were read directly.
- No tool installations or upgrades; no git mutations, tests, builds, formatters, or shell commands executed by this seat.
- No seat scratch directory was created, so none remains to clean. The frozen plan, frozen tools, other seats' files, and external substrates were not written by this seat.
