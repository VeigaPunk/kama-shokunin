# J6Ablation — round 50 C2 ablation controls

**Verdict: all three assigned definition ablations of `tools/append-only-audit.py` at 97c864be are caught by the frozen C2 counter (`fixture=0`, `met=False`, exit 1), each by exactly the scenario built for it — fence / crlf-launder / order-b — while the build tip and a no-op commit on it stay `fixture=1 lane=1 12/12 met=True`. Two further probes (dropping the v3 not-gutted `eligible` test; ignoring `only=` prefix regions) still pass `met=True`, so those two rules have zero coverage in C2; the `eligible` gap is load-bearing on the lane (it accounts for 6 of the 89 ungraded lines).**

## Setup

- Scratch `S=/fast/scratch/hyaku/kama-r50/J6Ablation`, `TMPDIR=$S`. One `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin` per probe, each `git checkout --detach 97c864be…`, `git rev-parse --show-toplevel` asserted equal to the clone dir before every commit, commits made with `-c user.name=r50j6-fixture -c user.email=r50j6-fixture@invalid -c commit.gpgsign=false`. The lane was never written; no `jj`, no `pacman`, nothing installed.
- Provenance: `tools/append-only-audit.py` at 97c864be, in the lane worktree and in my clone all sha256 `a3170a6fcbded95670e37750ab1ef72054e49ff83fc967e0c5f236ae10e205bd`; `tools/round50-append-audit-v5-check.py` at 601c8889, at 97c864be and in the worktree all sha256 `925f07a48a02ad54a9c89230aac7e54c8dafee4ba2e8a823dcb851b9cf48ca46`, equal to `preregistration.json` `claims[C2].counter_sha256` — the counter I ran is the frozen one.
- Every run was `python3 tools/round50-append-audit-v5-check.py --repo <my clone> --tip <probe commit> --scratch "$S" --out <receipt>`; `python3 -V` = 3.14.8, `git --version` = 2.56.0. Each ablation tree differs from 97c864be in `tools/append-only-audit.py` only (`git diff --shortstat 97c864be HEAD`).
- Fixture identity commits (parents all `97c864bead3ee4a2f629574e77263d33834ec98a`):

| probe | commit | hunks | tool sha256 |
|---|---|---|---|
| A v4 fence-blind section scan | bdd65b8a42138fed5ae2955e872e8df1483fb376 | 6+/14− | c41daac25571bbad593f7cad8ebebbeb48d4accb4f2cc0facdf0860ad0cf783f |
| B byte-exact origin keys | a0c99c34df14d38544c41404733bd7a142ea6b78 | 3+/4− | 56f30fd34e6fbdd08a8e154879d8b8a74bd9a1485ba1771bda278f2038ae4e0a |
| C v4 first-in-rev-list origin | 45ac43257e5d7498187d9c13901a84f6e0386418 | 19+/28− | 27b40a493f82bcf9e7a47a11217be39319835dcc265e0a78d6a814cf75e0400a |
| A+B+C combined | d6cfdb205fc486629a1b23326b1152691bb957d2 | 28+/46− | 4651a3049b1e3dac289e4decf4949a677deff44b202ea44e2aa94f094c496481 |
| D v3 section-only carve-out (extra) | 38fba2c4ecc5cbb9d1d1d610756ef78c3787e11b | 2+/3− | 66f7edc74105bdd35463679184ee02092ebade200191ccb0244a7352ed5b4ec2 |
| E no not-gutted test (extra) | 578d05ac6b23f1c52029007be05efb9daccbc618 | 3+/3− | c1e30462c866c3edec3c5c9c8d49d78319d697c31fb375475cc0a9f3b2af623f |
| F `only=` prefix gate removed (extra) | 4771e44d01aa5118e8357ba3d66cdb05da6e684b | 1+/2− | 5a303cf64951d187fb899b4bd0ee5da103d87801528e171f90141ec03a9e4fca |
| no-op control commit | 9094de67226823253453734b73fbfbf285300b5d | 0 | a3170a6f… (unchanged) |

Exact patches: `receipts/ablation-{a,b,c,d,all,e,f}.diff` (unified, `git diff 97c864be HEAD`).

## Receipts (measured)

| run | verdict line | exit | lane ungraded_lines | failing scenario(s) |
|---|---|---|---|---|
| build 97c864be (control, `control-97c864be.txt`) | `fixture=1 lane=1 scenarios=12/12 met=True` | 0 | 89 (17≤23, 72≤72) | — |
| no-op commit 9094de67 (`ablation-ctrl-noop.txt`) | `fixture=1 lane=1 scenarios=12/12 met=True` | 0 | 89 (17≤23, 72≤72) | — |
| A bdd65b8a (`ablation-a.txt`) | `fixture=0 lane=1 scenarios=11/12 met=False` | 1 | 89 (17≤23, 72≤72) | **fence** `exit 0 (want 1)` |
| B a0c99c34 (`ablation-b.txt`) | `fixture=0 lane=1 scenarios=11/12 met=False` | 1 | 89 (17≤23, 72≤72) | **crlf-launder** `{'deleted':25,'graded':0,'ungraded':25,'status':'ungraded'} want {'deleted':25,'graded':25,'ungraded':0,'status':'unrestored'}` |
| C 45ac4325 (`ablation-c.txt`) | `fixture=0 lane=1 scenarios=11/12 met=False` | 1 | 82 (17≤23, 65≤72) | **order-b** `exit 1 (want 0)` |
| A+B+C d6cfdb20 (`ablation-all.txt`) | `fixture=0 lane=1 scenarios=9/12 met=False` | 1 | 82 (17≤23, 65≤72) | order-b, fence, crlf-launder |
| D 38fba2c4 (`ablation-d.txt`) | `fixture=0 lane=1 scenarios=10/12 met=False` | 1 | 89 (17≤23, 72≤72) | **launder** `exit 0 (want 1)`, **crlf-launder** (event ungraded 25) |
| E 578d05ac (`ablation-e.txt`) | `fixture=1 lane=1 scenarios=12/12 met=True` | 0 | **95 (23≤23, 72≤72)** | none |
| F 4771e44d (`ablation-f.txt`) | `fixture=1 lane=1 scenarios=12/12 met=True` | 0 | 89 (17≤23, 72≤72) | none |
| base 26ecba64 (`control-base-26ecba64.txt`) | `fixture=0 lane=1 scenarios=9/12 met=False` | 1 | 82 | (round-49 tool: not part of this seat) |

Every run also satisfied the counter's arithmetic leg: no `graded+ungraded!=deleted` and no `deleted != numstat` detail line appears in any receipt, including the ablations (the four definition changes move lines between `graded` and `ungraded`, never out of the accounting).

## What each ablation proves

- **A (fence-blind sections)** — `sections()` body at 97c864be:306–325 replaced by the v4 scan (`line.startswith(b"## ")`, no `fence_open`/`fence_close`). `fence` scenario flips to `exit 0`: the 25 dated lines behind the fenced fake `## Axes` are ungraded. The fence rule is the only discriminator and it works.
- **B (byte-exact keys)** — `key()` at 97c864be:275–279 returns `ln`. `crlf-launder` flips: the 25 CRLF-moved lines have no origin of their own and the last event is `ungraded` instead of `unrestored`. The CRLF normalization is load-bearing and detected.
- **C (v4 first-in-rev-list origin)** — `origins()` at 97c864be:480–508 replaced by the round-49 rule (`git show 26ecba64:tools/append-only-audit.py`, "first blob in rev-list order that holds the text"). Only **order-b** fails (`exit 1`); order-a passes. That asymmetry is the point: with parents `[ca, cb]` topo-order visits branch A (the `## Axes` birth) first and the v4 rule accidentally reproduces the v5 answer; with `[cb, ca]` it visits branch B (`## Round 1`) first and grades all 25. A one-legged fixture set would have missed F3; both legs are needed and both are present.
- The no-op commit control (same tool bytes, new commit) is `met=True`, so the failures above are the patches, not the added fixture commit or the extra lane history.

## Findings (calibration of C2 itself; nothing patched, the counters are frozen)

**F1 — the lane leg has no discriminating power for any C2 definition change.** `lane=1` in all six probes and both controls; the only lane number that moves is `ungraded_lines` (89 build/89 A/89 B/89 D/89 F, 82 C, 95 E), and one-sided bounds let 82, 89 and 95 all pass. All discriminative evidence for C2 sits in the 12 constructed fixtures. That matches the preregistered limit ("C2's lane leg bounds the tool's ungraded count by the counter's own v5 count per event … the binder is still the v4 copy") but the measured breadth is wider than the sentence suggests: a tool grading 7 lines v5 ungrades (C, `0718b6ab` 65 vs the counter's 72) passes, because the bound is `tool ≤ counter`.

**F2 — the v3 `eligible` (section-not-gutted) test has zero coverage, and it is load-bearing on the lane (defect-class gap, counter-side).** `tools/append-only-audit.py:533-535` computes `eligible` and `:544` requires `s in eligible and org.get(key(text), …) & titles`; replacing the eligibility test with plain membership (`s in titles`) — probe E — still yields `fixture=1 lane=1 scenarios=12/12 met=True`, while the lane's `dd9f5dc6c0e6` event rises from 17 to 23 ungraded lines. Measured cause (scratch probe, `probe_eligible.py`, copied to `out/J6Ablation/`): the event deletes 31 SCORECARD.md lines; 6 are under `## Retired`, whose parent count is 9 against a window max of 4 → gutted → v5 grades them; the 17 ungraded sit under still-eligible `## Axes`(7), `## Planned`(9), `## Saturation`(1); the remaining 8 are outside every exempt title and graded under either rule (14 = 6 + 8). The counter cannot see it because its own binder at `tools/round50-append-audit-v5-check.py:489-491` counts `native` as "parent section an exempt title and origin ∩ exempt" — no eligibility term — so `23 <= 23` passes by construction.
*Proposed fix (round 51, counter-side, one of):* (i) add a 13th fixture scenario `gutted`: `SCORE.md` = `## Axes` + 25 lines + `## Round 1` + 3; event deletes the 25 while `## Axes` shrinks to 4 and dated lines regrow → expect the v5 tool `deleted=25 graded=25 ungraded=0 status=unrestored exit 1` and the E-ablated tool `exit 0`; (ii) tighten the lane binder: compute `eligible` in `native` (per-title window max vs parent count) and require `e["ungraded"] == native` for events with `ungraded > 0`. (i) is the cheaper and order-robust of the two; (ii) makes the dd9f5dc margin 17≤23 into 17≤17.

**F3 — the `only=` region rule has zero coverage in C2.** Two lane rows are `only=` (`registry/append-only-contract.tsv:10` `corpus/knowledge/consumer-registry.md only=## Errata@…:30`, `:11` `corpus/knowledge/error-is-not-a-verdict.md only=## Round24@…:173`) and both have no event, so removing the prefix gate (`:540-541`) — probe F — changes nothing: `met=True`, lane 89 exactly as the build. No fixture uses `only=` (all 12 use `exempt`). *Proposed fix:* one fixture with an `only=## Errata` row where dated text above `## Errata` is deleted and must stay graded, and text inside `## Errata` deleted while `## Errata` regrows must be ungraded; or accept as a stated limit in the C2 docstring.

**F4 — the origin test is invisible on the lane, not just bounded.** Probe D (v3 section-only carve-out) fails `launder` and `crlf-launder` but leaves the lane at exactly the build's 89 ungraded lines: on this history every section-only-ungraded line also has an exempt origin. So the lane supplies no positive evidence for the origin rule either; the fixtures carry it alone. Consistent with F1, worth writing into the C2 docstring limits so round 51 does not read `lane=1` as "the definitions hold on the lane".

**F5 — the order-a leg alone would not catch F3-order dependence.** C fails order-b only. The pair is correctly constructed (same trees, parents swapped) and load-bearing; a future edit must not collapse the two scenarios into one.

## Risks / blockers

- None blocking. F2/F3 are calibration gaps in a frozen counter, reported as findings per the lane contract; the C2 predicate as written (`ungrades no deleted line the v5 definitions grade`) is what the E probe violates while the counter reports met=True — the operator of the claim should know the operationalization is the looser `≤ counter count`, not the definition.
- Everything here was measured on my own `--shared` clones of the lane plus fixture-identity commits inside them; the lane repo, its jj state and its index were not touched, and no lane file was edited.

## Reproduce

```
S=/fast/scratch/hyaku/kama-r50/J6Ablation; export TMPDIR=$S
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/ab-a
git -C $S/ab-a checkout --detach 97c864bead3ee4a2f629574e77263d33834ec98a
git -C $S/ab-a apply <out>/receipts/ablation-a.diff        # likewise b, c, d, e, f, all
git -C $S/ab-a -c user.name=r50j6-fixture -c user.email=r50j6-fixture@invalid \
  -c commit.gpgsign=false commit -qam "ablation a"
python3 tools/round50-append-audit-v5-check.py --repo $S/ab-a \
  --tip $(git -C $S/ab-a rev-parse HEAD) --scratch $S
```

## Files written

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J6Ablation/`:

- `J6Ablation.md` — `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/J6Ablation.md` (this report)
- `probe_eligible.py` — the `## Retired` / eligibility measurement quoted in F2
- `receipts/ablation-{a,b,c,d,e,f,all}.txt` — counter receipts (`--out`), with `.stdout`, `.stderr`, `.exit`
- `receipts/ablation-{a,b,c,d,e,f,all}.diff` — the exact fixture patches against 97c864be
- `receipts/ablation-ctrl-noop.txt` — no-op-commit control (`.stdout`, `.stderr`, `.exit`)
- `receipts/control-97c864be.txt` — build-tip control · `receipts/control-base-26ecba64.txt` — base negative control (each with `.stdout`, `.stderr`, `.exit`)
