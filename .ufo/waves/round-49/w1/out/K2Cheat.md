# Round 49 lane kama — seat K2Cheat: C2 shortcut attack

Verdict: **the frozen C2 counter rejects the four "cheaper tool" shortcuts (all met=False), but it is still fooled into met=True by a no-origin tool that under-reports the ungraded count (M-E/M-F/M-G); the minimal hardening is a per-event arithmetic invariant (`graded + ungraded == deleted`) plus lane-derived differential fixtures.**

All measurements are on a scratch `git clone --shared` of the lane at build tip
`74558c71c38ceaeace15fd4cf8aa9d84977584b1` (fixture identity), running the frozen counter
`tools/round49-append-audit-v4-check.py` (`counter_sha256 26c465a9…` per preregistration) with
`--tip <mutant commit>` — the counter extracts `tools/append-only-audit.py` from `git archive <tip>`,
so each mutant is a commit on top of the build tip that changes only that file. No lane file was
mutated; no tools installed (git 2.56.0, Python 3.14.8 pre-existing; RULES.md read; no pacman).

## Baseline (real v4 tool at build tip) — received

```
$ python3 tools/round49-append-audit-v4-check.py --repo $S/lane --tip 74558c71… --scratch $S/base --out $S/base.receipt.txt
fixture=1 lane=1 scenarios=8/8 met=True        (exit 0)
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 82
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 65 <= natively exempt 65
```
(L1's dry-run claim reproduced.) Note: the counter's own native bound is 23 for event `dd9f5dc6c0e6`
while the truthful tool reports 17 — the lane leg is an *upper-bound-only* check, it never compares
the tool's report against an independent count.

## The four requested shortcuts and the bonus no-origin evasions

Each mutant: branch from `74558c71…`, one commit changing `tools/append-only-audit.py` only. Patch
files and receipts are in this directory; tips and receipt summaries below.

| id | change (vs v4) | tip | receipt | result |
|----|-----------------|-----|---------|--------|
| M-A | **shape-recognition grader**: exempt carve-out kept only for the counter's launder geometry (file `SCORE.md`, 25 deletions, `regrow line` present, deleted text `^dated line \d+ r49$`); everything else v3 title-based (no origin) | `37dc009b5cb020590abe7c5a49fe6048759b702a` | `ma.receipt.txt` | `fixture=1 lane=0 scenarios=8/8 met=False` |
| M-B | **'dated'-text grader**: exempt carve-out only when deleted text lacks `b"dated"`; real v4 binds kept | `c28ed64e49d5b77a2cbcf30314a7927fd731e253` | `mb.receipt.txt` | `fixture=1 lane=0 scenarios=8/8 met=False` |
| M-B2 | 'dated'-or-table-row (`b"| "` prefix) grader (variant) | `a77571c3045b79bebbd5a06fe8acc691645c8a1f` | `mb2.receipt.txt` | `fixture=1 lane=0 scenarios=8/8 met=False` (lane exits 1, regressed 1) |
| M-C | **counter-binds copy** (verbatim `token/says/binds/NEG3/NEGW` from the counter) + v3 title-based grading | `bb28e3ba6b499831f1865db44bc0b54eb4b07088` | `mc.receipt.txt` | `fixture=0 lane=0 scenarios=7/8 met=False` (launder FAIL; lane 72>65) |
| M-D(20) | **ungraded-cap exemption drop** (X=20): if an event's eligible-exempt deletions exceed X, grade them all | `dbc423732340f0839482eb68df4c812bbca00138` | `md20.receipt.txt` | `fixture=0 lane=0 scenarios=7/8 met=False` (native-head FAIL) |
| M-D(30) | same with X=30 | `ab0d5b6343227555ea5f19a83c894e04e651f8d8` | `md30.receipt.txt` | `fixture=0 lane=0 scenarios=7/8 met=False` (launder FAIL) |
| M-E | **underreport-un gradeded**: v4 grading untouched, but reported `ungraded` flattened to 0 for the lane file `SCORECARD.md` | `1a49d84d69e310c6d7670c267feb145ec0bd027b` | `me.receipt.txt` | `fixture=1 lane=1 scenarios=8/8 met=True` |
| M-F | **no-origin 'dated' heuristic + underreport** (v3-style grading, `b"dated"` carve-out, flatten for `SCORECARD.md`) | `264e7df63dd6d3c2a6a6acf843d542dfec824237` | `mf.receipt.txt` | `fixture=1 lane=1 scenarios=8/8 met=True` |
| M-G | same as M-F with the `origins()` call removed entirely (zero origin code) | `b06cead9f81c786d5fb2fb386690529bb4078ee8` | `mg.receipt.txt` | `fixture=1 lane=1 scenarios=8/8 met=True` |

## Evidence (key receipt lines)

Real tool at build tip (baseline, above) exits 0.

M-A (`ma.receipt.txt`): `fixture=1 lane=0 scenarios=8/8 met=False`; fixture leg all 8 ok (shape
trigger fires only on the launder geometry — `native-head`, `dated-loss` pass because they are not
fixture-shaped and fall back to title-based exemption, which is exactly what the launder fixture
expects for them); lane leg:
```
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 72 > natively exempt 65
```
v3-style grading ungrades 72 on the big event; the counter's native bound (65) rejects it.

M-B (`mb.receipt.txt`): `fixture=1 lane=0 scenarios=8/8 met=False`; `0718b6abbda6 … ungraded 71 > natively exempt 65`.
The 'dated' grep removes exactly one of the seven non-native lines (the line `retain the dated source
records…` in `dd9f5dc6c0e6` moves 17→16, still ≤ 23), but the other six laundered rows ("| sources-registry…",
"| ollama-offline-evidence-replay…", "| live-llamacpp-lifecycle…", "| gguf-declared-identity-replay…",
"| context-capacity-receipt…", "| instrument-agreement…", "| pin-watch…") have no 'dated' text, so a
text heuristic cannot reach 65. The origin rule is the only cheap discriminator there.

M-B2 (`mb2.receipt.txt`): bound now passes (10 ≤ 23, 48 ≤ 65), but the extra grading corrupts the
restoration accounting: `lane: tool exit 1 events 5 … regressed 1` — the counter's exit-0 gate
catches this variant.

M-C (`mc.receipt.txt`): `scenario launder: FAIL exit 0 (want 1)` (title-based exemption leaves the
laundered lines ungraded); lane `0718b6abbda6 … ungraded 72 > natively exempt 65`. Copying the
counter's binder exactly does not help: binds are orthogonal to grading.

M-D(20)/M-D(30) (`md20.receipt.txt`, `md30.receipt.txt`): the two grading fixtures `launder` and
`native-head` delete exactly 25 lines under the same exempt `## Axes` section (identical geometry),
so a count threshold cannot separate them: with X=20 both drop the exemption (native-head FAILs,
wants exit 0); with X=30 neither drops (launder FAILs, wants exit 1). Both lanes also exit 1
(regressed 1) because dropping the exemption on the big event re-classifies deleted text as graded
but unrestored.

M-E (`me.receipt.txt`): `fixture=1 lane=1 scenarios=8/8 met=True`, `lane: … ungraded_lines 0` —
the counter's lane leg (`round49-append-audit-v4-check.py:343-344` `if not e.get("ungraded"): continue`;
`:355` `if e["ungraded"] > native:`) only upper-bounds the tool's self-reported count. The event
dict arithmetic is now inconsistent (`graded + ungraded != deleted`), and nothing checks it.

M-F/M-G (`mf.receipt.txt`, `mg.receipt.txt`): identical `met=True`; M-G has `origins()` deleted
(`diff` shows the `org = origins(f)…` line gone), so this is a tool that reaches met=True with **no
v4 origin rule at all**: 'dated' text heuristic for the fixtures, computed ungraded flattened to 0
for the lane's `SCORECARD.md`.

## Findings

1. **All four classic shortcuts fail the frozen counter** (met=False), each for a different reason
   and each caught by a different gate: M-A/M-B/M-C by the lane native bound; M-B2 by the exit-0 /
   regressed gate; M-D by fixture geometry symmetry (cannot separate launder from native-head).
2. **The counter is nonetheless spoofable to met=True without implementing origin**: M-F/M-G (dated
   heuristic + under-reported ungraded) pass every leg. The lane leg trusts the tool's own
   `ungraded` number; nothing recomputes it or checks arithmetic.
3. The fixture leg's expectations are written by construction (exact exit codes and event dicts), so
   any heuristic that recognizes the fixture *shapes* (SCORE.md/NOTES.md/regrow lines, 'dated' text)
   can pass the fixture leg; the lane leg is the only place where origin actually matters, and it is
   only an upper bound.

## Proposed hardening (counter-side; frozen now, so proposed, not applied)

- **Arithmetic invariant** in `lane_leg` (round49-append-audit-v4-check.py, after line 343): for
  every event require `e["deleted"] == e["graded"] + e["ungraded"]`. This alone defeats M-E/M-F/M-G
  (their flat `ungraded=0` breaks `2421 = 2356 + 0`). The honest v4 tool satisfies it on both lane
  events (31 = 14 + 17; 2421 = 2356 + 65).
- **Differential probe**: after the lane leg, build a lane-derived repo at `--tip` (clone), inject a
  held deletion of a line born *outside* an exempt section but moved under one (use lane-realistic
  text, not 'dated'/table-row shapes), and require the tool to exit 1. This catches any remaining
  shape/word heuristic (M-A/M-B) and any under-report; the counter already has all the fixture
  plumbing (`Fx`, `run_tool`) to do this.
- Keep the existing upper bound (it is what catches the over-ungrading v3-style shortcuts).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Cheat.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/K2Cheat/` containing:
  - `baseline-v4.receipt.txt`, `ma.receipt.txt`, `mb.receipt.txt`, `mb2.receipt.txt`,
    `mc.receipt.txt`, `md20.receipt.txt`, `md30.receipt.txt`, `me.receipt.txt`, `mf.receipt.txt`,
    `mg.receipt.txt` (counter stdout for each tip, with exit codes)
  - `m_a.patch`, `m_b.patch`, `m_b2.patch`, `m_c.patch`, `m_d20.patch`, `m_d30.patch`,
    `m_e.patch`, `m_f.patch`, `m_g.patch` (unified diffs of each mutant against `74558c71…`)
- Scratch `/fast/scratch/hyaku/kama-r49/K2Cheat` removed on completion.
