# M2Tool — C2 tool mutation test (kama round-46, wave 1)

**Verdict:** 39 mutants of `tools/append-only-audit.py` (frozen at lane commit 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050): **28 killed** (26 by the tool's own `--selftest`, 2 by the frozen counter's lane leg), **10 survived with demonstrated pristine-vs-mutant divergence** (selftest coverage gaps — findings F1–F10 below, each with a proposed selftest case), **1 equivalent** (M30, structurally inert at its callsite). The frozen counter `tools/round46-append-audit-check.py` itself shows no defect: on the pristine tool all three exercisable legs pass (`selftest=1 fixture=1 lane=1`; `table=0` at the frozen tip because the SCORECARD capability row has not landed yet — constant across every mutant, so verdicts key on the three legs).

## Method

- Scratch `S=/fast/scratch/hyaku/kama-r46/M2Tool` (removed at end; `/tmp` never used).
- Pristine = `git -C kama-shokunin show 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050:tools/append-only-audit.py` → `pristine.py`, 325 lines, sha256 `793dab9ffe0c41c7a5427324fd6f8bf0c3b40b0f9083d417e38d5e5792a7227f`; byte-identical to the lane working-tree file (`diff -q` clean).
- One fixture clone: `git clone -q --shared <lane> $S/fixture`. Per mutant: `git -C $S/fixture checkout -q --detach 4a2a4d55...`; assert `git rev-parse --show-toplevel` == the fixture dir; write the mutant to `tools/append-only-audit.py`; `git add` + commit with the fixture identity (`user.name=aoa-fixture`, `user.email=aoa-fixture@invalid`, `commit.gpgsign=false`); assert tip's parent == 4a2a4d55. No lane git/jj state touched.
- Per mutant, two detectors:
  1. **direct selftest**: `python3 <mutant> --selftest --scratch $S/st` — rc and `AOA_SELFTEST pass=n fail=m`.
  2. **frozen counter**: `python3 kama-shokunin/tools/round46-append-audit-check.py --repo $S/fixture --tip <tip> --scratch $S/ctr`. The counter extracts the tool from the fixture tip (`git show <tip>:tools/append-only-audit.py`), so the mutant is what runs in all three legs.
- Verdict rule: direct selftest fail or counter `selftest=0` → killed-by-selftest; counter `fixture=0` or `lane=0` → killed-by-counter; all three legs 1 → survived (then probed for real divergence on constructed inputs); no divergence on any constructed input + structural argument → equivalent.
- **Baseline (pristine, no mutant):** counter rc=1, `selftest=1 fixture=1 lane=1 table=0 lane_events=5 lane_unrestored=0 lane_partial=2 met=False` — the 5 lane events match the preregistration exactly: 0718b6ab LOG.md 2290 restored by 82b5e9d3, corpus/QUALITY.md 375 restored, corpus/README.md 663 restored, 0718b6ab SCORECARD.md 2417 deleted/2416 at tip partial, dd9f5dc6 SCORECARD.md 31/24 partial. `table=0`: no SCORECARD table line naming `append-only-audit` with last cell `46` at 4a2a4d55 (nor at lane HEAD 96d32918 — the capability row is L1's integration step). Counter runtime ≈ 2.9 s; full 39-mutant sweep ≈ 2 min (`logs/driver-run3.txt`).

## Results (`results.tsv`, 39 rows + header)

| verdict | count | mutants |
|---|---|---|
| killed-by-selftest | 26 | M01 M02 (threshold `<`→`<=` / `+1`), M05 M06 (`---` exclusion), M07 (deletion text keeps `-`), M09 (root commit not skipped), M11 M13 (set→list TypeError), M16 (reversed restored_by search), M17 (`later=[]`), M18 (last match kept), M19 (any-line restored_by), M20 (restored/unrestored labels swapped), M21 M22 (status thresholds), M24 M25 M26 M27 (exit code), M31 M32 M33 M34 M35 (cat-file batch parsing), M36 (drop `--reverse`), M38 (`--name-status`) |
| killed-by-counter | 2 | M12, M15 (see below) |
| survived | 11 | M03 M04 M08 M10 M10b M14 M23 M28 M29 M30 M37 → 10 findings + 1 equivalent |

Counter kills (frozen counter's lane leg, `logs/M12-counter.txt`, `logs/M15-counter.txt`):

- **M12** (`restored_at_tip` counted distinct instead of per deleted line): lane leg `missing=[... LOG.md 2290 2290 restored ...] extra=[... LOG.md 2290 **2003** partial ...]` — SCORECARD 2416→1789, QUALITY 375→209. The lane's deleted-line sets contain duplicates; the contract's "each deleted line counted on its own; duplicates may share one occurrence" is load-bearing and only the lane leg catches it.
- **M15** (restored_by search starts at `i+2`, skipping the immediate successor): lane leg `restored_by` flips 82b5e9d3→0fddf257 on all three restored events — 82b5e9d3 is the immediate successor of 0718b6ab in rev-list order, so skip-next is observable on the lane.

## Findings (survivors; probe evidence in `probe-out/<id>.txt`, diffs in `mutants/<id>.diff`)

**F1 — M03 (argparse `--threshold` default 20→21).** The selftest never exercises `main()`: it calls `audit()` directly, whose signature default stays 20, so 10/10 cases pass; the counter never passes `--threshold` and its fixture (30/25) and lane (min 31) events all exceed 21. Probe (exactly-20 deletion, CLI default): pristine `rc=1 events=[(…, 'LOG.md', 20, 0, 'unrestored', '-')]`; mutant `rc=0 events=[]`. A CLI user silently misses exactly-20 events. Proposed selftest case (kills): drive `main(["--repo", f.d, "--to", t, "--json"])` on a 20-deletion fixture via `contextlib.redirect_stdout`, assert 1 event with `deleted == 20` and rc 1.

**F2 — M04 (`--threshold < 1` validation removed).** Probe: `--threshold 0` → pristine `rc=2` stderr `could-not-evaluate: --threshold must be >= 1`; mutant `rc=1` and reports an event (on larger repos every touched commit floods in as a `deleted=0 … restored` event). Proposed selftest case (kills): `main(["--repo", f.d, "--to", t, "--threshold", "0"])` with redirected stderr, assert rc 2 and `could-not-evaluate` present.

**F3 — M08 (merge diff against last parent instead of first).** The selftest's only merge case (`t_merge_first_parent`) uses `-s ours` where the second parent's content is a *subset* of the merge result, so the diff vs either parent has 0 deletions — blind to parent choice; the lane has no discriminating merge. Probe (side branch *adds* 30 unique lines, merge `-s ours`): pristine `rc=0 events=[]`; mutant `rc=1 events=[(merge, 'LOG.md', 30, 0, 'unrestored', '-')]` — a deletion invented at the merge commit. Proposed selftest case (kills M08 and M10b): `t_merge_second_parent_additions` — side commit appends 30 unique lines (no deletion), main appends 1, merge `-s ours`; assert `res["events"] == []` and `exit_code(res) == 0`.

**F4 — M10 / M10b (deletions unioned across all parents instead of first parent).** M10 unions only the `-U0` diff (gated by the first-parent prefilter); M10b unions the prefilter too. Probe (conflict merge: side=base[:30] → 5 first-parent deletions; main=base[:10]+extra15 → 15 second-parent deletions; resolved to base[:25]): pristine 1 event (main, 30, partial); both mutants add a spurious merge event `deleted=20 unrestored` (`probe-out/M10.txt`, `probe-out/M10b.txt`). Proposed selftest case (kills M10): `t_merge_conflict_union` — the conflict-resolved merge above; assert no event at the merge commit.

**F5 — M14 (restored_by search starts at `i`, including the event commit).** Needs duplicated line text to observe. Probe (file holds 40 unique lines + a duplicated 20-line block; event deletes the block, texts still present; `--to` = event commit): pristine `restored_by='-'`; mutant `restored_by=` the event commit itself — "restored by" the commit that deleted them. Proposed selftest case (kills): `t_restored_by_excludes_self` — duplicate-block fixture, audit to the next commit, assert `restored_by == next_commit and restored_by != event_commit`.

**F6 — M23 (summary `partial` counts every non-restored event).** `exit_code` is unchanged (partial∨unrestored ⇔ non-restored), JSON `events` unchanged, so both legs pass; only the printed `summary` object lies. Probe (30-deletion unrestored): pristine `summary partial=0 unrestored=1`; mutant `partial=1`. Proposed selftest case (kills): `t_summary_counts` — assert `res["summary"] == {"commits": 2, "events": 1, "restored": 0, "partial": 0, "unrestored": 1}` on the unrestored fixture.

**F7 — M28 / M29 (`--no-renames` dropped from both diffs / from the prefilter).** No rename fixture in the selftest; no rename of the five files in lane history. Probe: LOG.md (50 lines) deleted while SCORECARD.md (previously absent) appears with identical content — git reports `R100 LOG.md→SCORECARD.md` (captured in `probe-out/M28.txt`); pristine: event `(LOG.md, 50, unrestored)`; both mutants: `events=[]` — a mass deletion vanishes. Proposed selftest case (kills both): `t_rename_hides_deletion` — `f.commit({"SCORECARD.md": a}, delete=["LOG.md"])` after LOG.md was the only holder of `a`; assert exactly 1 event on LOG.md with `deleted == 50`, status unrestored.

**F8 — M37 (`--topo-order` dropped from the rev-list).** restored_by is "first commit after the event **in the rev-list order**"; without `--topo-order` that order is committer-date. Probe (E deletes 20 dated T5; its child R restores dated T1; side commit cs holds the lines dated T3; merge): topo order `… E R cs M` → pristine `restored_by=R`; date order `R cs E … M` → mutant `restored_by=cs`. Lane survives because lane dates are monotone with topology. Proposed selftest case (kills): `t_restored_by_topo_order` with `GIT_COMMITTER_DATE`/`GIT_AUTHOR_DATE` set per commit (needs a `date=` parameter on `Fixture.commit`), asserting `restored_by == R`.

**F9 — M30 (`--no-renames` dropped from the `-U0` diff only): EQUIVALENT, not a finding.** That diff always passes exactly one path (`-- f`); git rename detection pairs a deleted path with an added path only when both endpoints are inside the pathspec, so `-M` can never engage at this callsite (rename f→g ⇒ f shown as plain deletion; rename g→f ⇒ f shown as pure addition). Empirical: in the rename fixture, `git diff -M -U0 c1 c2 -- LOG.md` still prints the full 50-line deletion (`probe-out/M30.txt` header capture); pristine and mutant outputs are identical. No input distinguishes it.

**F10 — M10b note.** First attempt was skipped on a bad anchor (12-space indent vs the real 8) and rebuilt; the rebuilt mutant is the stronger form of F4 and survives all three legs (`results.tsv` row M10b) — killed only by the proposed `t_merge_second_parent_additions`.

## Coverage observations for the lane (not defects in the frozen counter)

1. The selftest never exercises `main()`/CLI parsing (F1, F2 survive).
2. The selftest's only merge case is `-s ours` with second-parent content a subset of the merge result — blind to parent selection and unions (F3, F4 survive).
3. No duplicate-line fixture (F5 survives; M12 survives the selftest and is caught only by lane luck — the lane's own history carries duplicates).
4. No rename fixture (F7 survives).
5. Committer dates are never manipulated (F8 survives).
6. The `summary` object is never asserted (F6 survives).
7. The frozen counter's fixture has no *partial* event: status-threshold mutants M21/M22 pass its fixture leg and die only on the lane leg (fine today — the lane carries 2 partial events; a future lane without partials would weaken that leg).

## Integrity / restoration

- Lane never written to: lane `tools/append-only-audit.py` sha256 `793dab9f…` == `pristine.py`; `git -C <lane> diff 4a2a4d55 -- tools/append-only-audit.py tools/round46-append-audit-check.py` empty; `git -C <lane> status --porcelain tools/` empty. The mutant lives only in my disposable fixture clone and scratch (removed at end, per operator directive — scratch declared disposable).
- No tools installed (none needed); pacman untouched; no services started; no subagents spawned.

## Evidence files (all under the out directory below)

`results.tsv` (39 rows), `logs/` (baseline counter + 39×2 per-mutant selftest/counter outputs + driver runs), `probe-out/` (11 divergence records), `mutants/` (10 unified diffs), `pristine.py`, `driver.py`, `probe.py`.
