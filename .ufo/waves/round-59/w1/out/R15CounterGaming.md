# R15CounterGaming — round 59, kama (godspeed)

Axes: operability + calibration (calibration=7, lowest assigned). One v2 wave, advisory only.
Attacked clause (frozen, untouched): C1-r59 counter `tools/round59-c1-counter.py` with finite
controls `tests/round58-battery-variants` + `tests/round59-battery-variants`; kill rule
"any outcome-unbound control accepted → claim not met".
Question: does the frozen counter detect a checker keyed to fixture directory names,
commit author/message, or variant basenames instead of observed leg outcomes?

## Answer

**No for fixture directory names.** A 15-line checker that executes no battery leg, observes no
`ld_audit` value, and decides solely from the fixture directory basename passes the frozen C1
counter with `met=True`, exit 0. Author/message and variant-basename keying carry no per-fixture
signal (they collapse or fail for information-theoretic reasons, not because gaming is caught).

## Vectors and runs

Scratch: `/fast/scratch/hyaku/kama-r59/R15CounterGaming` (TMPDIR set explicitly; removed after).
Frozen tip: `aca8d0067ea25627c5015c2193c843965148bc8e` (verified via `git rev-parse --verify …^{commit}`).
Counter executed read-only from the lane copy; every fixture repo the counter itself builds uses
`git -C <fx>`, asserts `rev-parse --show-toplevel == fx`, and commits identity
`kama-r59-counter <kama-r59@invalid>` message `fixture` inside its own scratch dir.

| Run | Command (abridged) | Result | Counter exit |
|---|---|---|---|
| R1 baseline | `python3 tools/round59-c1-counter.py --repo <lane> --tip aca8d00… --work $S/base` | `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True` (4.3 s) | 0 |
| R2 dirname-keyed gamer | same + `--checker $S/gamed-dirname.py` | `genuine=1/1 benign=3/3 noop_rejected=16/16 errors=0 met=True` (0.78 s) | 0 |
| R3 author/message-keyed gamer | same + `--checker $S/gamed-author-message.py` | `genuine=1/1 benign=3/3 noop_rejected=0/16 errors=0 met=False` | 1 |

Gamer source (executed via the counter's supported `--checker` pre-data-shortcut interface):

```python
# gamed-dirname.py — verdict keyed to fixture directory basename only
name = pathlib.Path(a.repo).resolve().name
return 1 if name.startswith("N") else 0
```

Direct demo: `--repo …/demo/N12-ignore-leg-result` → `verdict=reject`, exit 1;
`--repo …/demo/genuine` → `verdict=accept`, exit 0. No battery source was opened in either case.

## Findings

**F1 — HIGH, confirmed (executed): the frozen C1 counter cannot detect fixture-directory-name
gaming.** R2 scored a perfect 21/21 accept/reject pattern with `met=True`, exit 0, from a checker
that observes nothing. Root causes, all in `tools/round59-c1-counter.py`:
1. The counter names every fixture directory exactly after the variant (`fx = work / name` over
   `["genuine"] + BENIGN + OLD_NOOPS + NEW_NOOPS`), so the basename telegraphs the required
   verdict: `N*` must reject, everything else must accept.
2. Verdicts come from checker exit codes only (`{0: "accept", 1: "reject"}`); checker stdout is
   captured into `outcomes` but the 4th tuple field is never printed or validated — a checker
   that confesses "basename-keyed; no outcome observed" in every detail line is invisible.
3. The kill rule counts acceptances/rejections, never the *reason* for them. The name-gamer
   rejects every control for the wrong reason, so "any outcome-unbound control accepted" never
   fires while outcome-binding is entirely absent.
Corroborating runtime asymmetry: baseline 4.3 s vs gamed 0.78 s — the gamed run did no leg work;
the counter measures no duration and no per-leg receipts.

**F2 — MEDIUM, confirmed (executed): author/commit-message keying has zero per-fixture signal,
and the author string is a harness-detection oracle.** All 21 fixtures carry the identical
identity `kama-r59-counter <kama-r59@invalid>` and message `fixture`, so R3's gamer could only
return a constant verdict (uniform accept → `noop_rejected=0/16`, `met=False`, exit 1). The
counter survives this vector because the vector is information-free — not because gaming is
detected. Side leak: any checker can read the author string to learn it is being counted.

**F3 — LOW, confirmed: variant basenames have no in-fixture carrier; the vector collapses into
F1.** The counter writes each variant blob to the constant path `tools/round56-env-leg-battery.py`,
and at the frozen tip none of the 20 variant files contains its own basename
(20/20 `no-self-name` via `git show <tip>:<variant> | grep -F <name>`); B1/N16 docstrings are
byte-identical headers. The only surviving carrier of a variant's name is the counter-chosen
fixture directory name — the F1 channel.

**F4 — MEDIUM, inference from counter source (not executed; lane is read-only for this seat):
the committed-checker path is equally exposed.** Without `--checker`, the counter extracts the
blob at `tools/round59-battery-outcome-check.py` from the tip and treats it as an opaque
exit-code source (`checker.write_bytes(blob(a.repo, tip, CHECKER))` → `subprocess.run` →
classify returncode). A lane commit replacing that path with the name-keyed twin would pass
identically; nothing audits checker source or requires outcome receipts in its output.

## Scope of the finding

This is a control-gap result, not evidence that the committed checker games: R1 reproduced the
frozen pass genuinely at the measured tip. The C1-r59 predicate's finite controls distinguish
*what* a checker concludes but not *why*; name-based gaming therefore satisfies the counter
while violating the predicate sentence ("its own `--expect` maps to that leg's returned
`ld_audit` value"). Claim-level impact for L1: the C1 counter alone cannot certify
outcome-binding against this vector.

Recommendation (for the round owner; nothing frozen was altered by this seat): randomize
fixture directory names with a per-run opaque mapping, vary per-fixture author/message, require
and validate per-leg receipts (`ld_audit=…`, declared exit) in checker stdout, and/or add
deceptive-name controls (fixture named `N*` carrying a genuine battery, and vice versa) so
name-keying fails on the merits.

## Residual risk and verification gaps

- Content-hash-table gaming (checker embedding variant blob hashes) was **not** attempted;
  by the same exit-code-only trust it would likely also pass — unexecuted, unclaimed.
- F4 is code-read inference; the lane write needed to execute it is out of bounds for this seat.
- C2 calibration was not attacked (fixture gaming is C1 domain); C2's counter derives fields
  itself and does not share the checker-exit-code trust pattern.
- Environment observation: `git -C /home/vgpnk/Projects/shokunin rev-parse HEAD` resolves to
  `0f99f606120d0c884656c6e7a290f0e8f33c2181`, not the `3f3dd973…` stated in the assignment —
  recorded, not acted on; C1 runs are tip-pinned and unaffected. External S517/S518 spot-check
  remains unrecorded; no discernment progress is claimed.

## Compliance

Installs: none (no tooling needed; pacman untouched). Lane untouched except this report file;
no commits/pushes; no sibling-lane, fleet, or shokuknow writes; no `/tmp` use; scratch tree
removed before yield; no subagent dispatch (leaf).

Report: .ufo/waves/round-59/w1/out/R15CounterGaming.md
