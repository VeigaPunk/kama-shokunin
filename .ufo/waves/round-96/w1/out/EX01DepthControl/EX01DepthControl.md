# EX01DepthControl — round-96 C2 (depth) — Godspeed seat report

Seat: EX01DepthControl. Lane: kama-shokunin. Base: `5d43528badc31ad6c0ca1848c00561f531924e4d`.
Freeze (F): `58001b71`. Amendment 1: `e2fed9f5`. Tip at seat run: `bbdfc930` (= `bbdfc930cf99845f7b5c4ab63f3bfd51ba39e582`).
Assignment: run the frozen C2 counter at base and at the newer revision, paste both receipts, confirm base mismatches (table absent, old ceiling sentence) and that the new number is green; write this report to out/EX01DepthControl.md.

## Verdict: GREEN at the new revision, RED at base — the C2 counter discriminates

The counter is `tools/round96-depth-audit.py` (frozen in the F commit `58001b71`).
- Base `5d43528b`: `DEPTH_AUDIT checks=7 mismatches=6 met=False`, exit 1 — RED. The base is NOT green, so the counter discriminates: the step-cost table is absent, `MAX_STEPS` is 4 000 000, and S618 does not exist.
- Tip `bbdfc930`: `DEPTH_AUDIT checks=7 mismatches=0 met=True`, exit 0 — GREEN.
- Freeze `58001b71` itself: `DEPTH_AUDIT checks=7 mismatches=0 met=True`, exit 0 — the landed work is green at the freeze revision too (the table and patch landed in the same F commit).
- Kill rule K1 note: the counter is byte-identical to the freeze commit except for the disclosed amendment-1 regex anchor (see §3). No predicate change.

## 1. Receipts (verbatim, pasted)

1.1 Frozen base control committed at F (`.ufo/waves/round-96/controls/c2-base.out`):

    DEPTH_AUDIT checks=7 mismatches=6 met=False

1.2 Seat re-run at the local tip (`bbdfc930`), and at F (`58001b71`) for identity
(`python3 tools/round96-depth-audit.py --repo . --rev <rev>`):

    DEPTH_AUDIT checks=7 mismatches=0 met=True   (tip bbdfc930, exit 0)
    DEPTH_AUDIT checks=7 mismatches=0 met=True   (freeze 58001b71, exit 0)
    DEPTH_AUDIT checks=7 mismatches=6 met=False  (base 5d43528b, exit 1)

1.3 Raw receipt files copied to the out dir: `c2-base-rerun.out`, `c2-freeze.out`, `c2-tip.out`
(same bytes as the stdout lines above; scratch copies in `/fast/scratch/hyaku/kama-r96/EX01DepthControl/`, deleted after copying).

## 2. What the base mismatch is — and is not

The 6 base mismatches decompose (checked 7 total) as: `MAX_STEPS` is 4 000 000 (≠ 5 000 000) → +1;
derived ceiling 4 000 000/6 = 666 666 ≠ 833 333 → +1; `1 tensor header = 6 steps` absent → +1;
`ceiling 833,333` absent → +1; `S618` absent from SKILL.md → +1; S618 row absent from
`corpus/SOURCES.md` → +1. The `ceiling 1,000,000` anti-check does not fire at base (the literal
string `ceiling 1,000,000` does not appear in base SKILL.md — the old false sentence lived in the
probe's code comment, not in SKILL.md prose; the counter's anti-check is therefore a tip-side guard,
not a base discriminator).

Base facts verified independently:
- Base SKILL.md: no `1 tensor header = 6 steps`, no `ceiling 833,333`, no `S618`, no
  `ceiling 1,000,000` literal.
- Base probe: `MAX_STEPS = 4_000_000` (line 575 at `5d43528b`); its comment still says a file
  needing more than `MAX_STEPS` is `-` — correct as far as it goes, but the disclosed ceiling
  sentence naming 1 000 000 (MAX_TENSORS) as if binding is not in the probe either. The counter
  does not grade the old sentence by presence; it grades the new table by presence and arithmetic.
- Base `corpus/SOURCES.md`: no S618 row (adds S618 in `58001b71`).

Tip facts verified independently:
- `MAX_STEPS = 5_000_000` at `tools/kama-probe.sh:581`; the comment immediately above names the
  binding ceiling (`~833 333 tensor headers`), attributes the correction to round-95 amendment 4 /
  SC02 F1, and says KV/string work makes the effective ceiling slightly lower. The old 1 000 000
  sentence is replaced ("that sentence is replaced, not kept").
- SKILL.md adds `### Round 96 correction (step-cost table; dated 2026-11-08)` at end of file:
  `1 tensor header = 6 steps` (name `u64`+skip 2: u64 1 + skip 1; `nd` `u32` 1; dims `u64` 1;
  type `u32` + offset `u64` 2), `MAX_STEPS = 5 000 000`, `833 333 tensor headers`,
  `(ceiling 833,333)`, the 700 000-tensor worked example (4 200 000 steps), the `-` = undecidable →
  loadable error signature, and the S618 citation (`ggml/include/ggml.h` @ b12177, sha256
  `590e00a5…67392`, opened 2026-11-08). The closing `S618` line truncates at the file's last shown
  line in the diff; the full cited line is present at tip (verified: `S618` in SKILL.md at HEAD = true).
- SOURCES.md adds the S618 row (sha256 `590e00a5…67392`, status `mined`, not `rejected`).

## 3. Counter-amendment note (kill rules K1/K2 read)

At HEAD the counter differs from its freeze-commit bytes by exactly the disclosed amendment-1 fix:
`re.search(r"MAX_STEPS = ([0-9_]+)", probe)` → `re.search(r"^MAX_STEPS = ([0-9_]+)", probe, re.M)`
(`git diff 58001b71 HEAD -- tools/round96-depth-audit.py`: 1 line). Reason per
`plans/round-96-amendment-1.md`: the unanchored regex matched the prose comment
`MAX_STEPS = 5 000 000` first (spaces, not underscores) and parsed `5` instead of the assignment
`MAX_STEPS = 5_000_000`. Without the anchor the predicate is unmeasurable; with it, both base and
tip read correctly (base exit 1, tip exit 0, no `could-not-evaluate`). SHA256 of the counter:
F `505cd488…`, HEAD `9a2d302a…` — the single-line difference. The claims-file
counter-bytes-identical condition is met modulo this disclosed, behavior-preserving instrument fix;
it does not move any threshold (checks=7, `STEPS_PER_HEADER=6`, `CEILING=833_333` unchanged).
K2 (table arithmetic vs probe constants): 5 000 000 // 6 = 833 333 = the counter's `CEILING`, and
the probe comment plus SKILL.md both derive the ceiling from the arrow value — holds.
K3 (S618 status): `mined`, not `rejected` — holds.

## 4.God-mode frontwalk (named, applied)

- Axes named (from plans/round-96-claims.md SCORECARD): operability 8, freshness 8, depth 7,
  coverage 9, calibration 7, adjacency 7. C2 works depth (lowest non-retired axis, 7).
- Cheap parallel iteration: this seat re-ran the frozen C2 counter at three revisions
  (base, freeze, tip) in one batch and diffed the three layers (probe, SKILL.md, SOURCES.md) in
  the same turn; no serial follow-up needed.
- Moves kept: (a) base vs tip receipt pair proving discrimination; (b) independent grep of the
  four tip ingredients at both revisions; (c) amendment-1 diff isolated to the single regex line.
- Moves rejected: none needed this seat. No edits were assigned to this seat ("never edits a
  tracked lane file") and none were made.
- Frontier read: depth is closed on the declared predicate. The remaining depth gap (depth 7) is
  carried, not closed — it belongs to later rounds, not to this wave.

## 5. Retained evidence (exact)

- `DEPTH_AUDIT checks=7 mismatches=6 met=False` — base `5d43528b`, exit 1 (reproduces the frozen
  `controls/c2-base.out`).
- `DEPTH_AUDIT checks=7 mismatches=0 met=True` — tip `bbdfc930`, exit 0 and freeze `58001b71`, exit 0.
- Probe: `MAX_STEPS = 4_000_000` (base) → `MAX_STEPS = 5_000_000` (tip, line 581).
- SKILL.md: step-cost table present at tip only (lines after §Round 96 correction).
- S618 row present at tip, absent at base; status `mined`.
- Counter diff: 1 line (regex anchor, amendment 1); checks and thresholds unchanged.

## 6. Risks and blockers

- [blocker] None for this seat's claim. The C2 predicate is met at tip and discriminated at base.
- [risk] The only byte-level change to the frozen C2 instrument is amendment 1's anchored regex —
  disclosed and required. If the integrator grades "bytes identical to the freeze commit" literally
  without the amendment, K1 would trip on the counter file itself; `plans/round-96-amendment-1.md`
  is the instrument's own record that this is an instrument repair, not a claim change. Seat takes
  no position beyond the fact.
- [risk] The counter's anti-check (`ceiling 1,000,000` absent) is toothless at base (literal absent
  in base SKILL.md); discrimination rides on the five presence checks plus the derived-ceiling
  equality, which is sufficient and does not depend on the anti-check.

## 7. Files changed

None. Seat wrote only its own report and receipt copies:
- `w1/out/EX01DepthControl/EX01DepthControl.md` (this report; the `EX01DepthControl.md` path in
  the assignment is the out-dir report).
- `w1/out/EX01DepthControl/c2-base-rerun.out`, `c2-freeze.out`, `c2-tip.out` (fresh re-runs; the
  freeze-time `controls/c2-base.out` was read, not edited).
- Scratch: `/fast/scratch/hyaku/kama-r96/EX01DepthControl/` (copies above; deleted on exit).
- No lane file edited. No commit, push, or git/jj mutation.

## 8. Godspeed closure line

Verdict to the integrator: C2 is landed and green at the measured revision (`bbdfc930`), the base is red under the same instrument, and the instrument change since freeze is the single disclosed anchor patch. The frontier on depth moves only when a later round names the next lowest axis; nothing in this seat's evidence blocks C2 closure.
