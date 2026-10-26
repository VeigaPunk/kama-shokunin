# K1Fixture — C1 fixture-leg power attack (round 47)

**Verdict: the fixture leg pins 10 of the 12 v2 definition clauses. The `held` max(0,·) clamp's negative branch and the merge-commit first-parent selection are exercised by NO leg (variants V-A and V-C pass all five legs, `met=True`); the exact-20 event threshold is pinned only by the tool's own selftest, while the fixture's coverage of it is nondeterministic (P=11/35 per run; passed 12/15 sampled runs).**

## 1. Setup and baseline (fixture identity = lane at 3a09a1d93dcc16799cf6c4b48786e6440af134c4)

Counter: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round47-append-audit-v2-check.py`
(sha256 `a180ab84cc642731a6bd5fca92e5218dfaa6c074279e2f001110b348d73755ed` — matches the frozen preregistration).
Tool under test at tip: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py`
(sha256 `5d47bc77e9bde41a1af1fcba449e60fd027d9ed30fbf2770a5a53f177856f874`).

Read-only lane clone (every run below used `git clone --shared`):
`git clone --shared -q /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`, tip verified
`3a09a1d93dcc16799cf6c4b48786e6440af134c4`.

Baseline run:
```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round47-append-audit-v2-check.py \
  --repo $S/lane --tip 3a09a1d93dcc16799cf6c4b48786e6440af134c4 --scratch $S/run-baseline
```
→ `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True` exit 0 (evidence `out/K1Fixture/run-baseline.out`).

Lane events (from the counter's own recomputation, script `k1_vacompare.py`):
| event commit | file | deleted | restored_max | restored_best | restored_by | status |
|---|---|---|---|---|---|---|---|
| dd9f5dc6c0e… | SCORECARD.md | 31 | 24 | dd9f5dc6c0e… | — | partial |
| 0718b6abbda6a… | LOG.md | 2292 | 2292 | 82b5e9d33a1… | 82b5e9d33a1… | restored |
| 0718b6abbda6a… | SCORECARD.md | 2421 | 2420 | 82b5e9d33a1… | — | partial |
| 0718b6abbda6a… | corpus/QUALITY.md | 375 | 375 | 82b5e9d33a1… | 82b5e9d33a1… | restored |
| 0718b6abbda6a… | corpus/README.md | 663 | 663 | 82b5e9d33a1… | 82b5e9d33a1… | restored |

## 2. v2 definition clauses × fixture coverage

Definition source: counter docstring lines 27–50; implementations: `recompute()` (counter 201–238) and `audit()` (tool 175–226). Fixture construction: `build_fixture()` (counter 394–512); fixture leg asserts `files`, each event's (commit,file,deleted,restored_max,restored_best,restored_by,status), schema and exit 1 (counter 515–552).

| clause | fixture exercises it? | where (fixture line refs) | other legs' rescue |
|---|---|---|---|
| contract (TSV header, 4 cells, rule, declared_at) | partial — only valid-contract expansion | build_fixture 437–444; leg equality on `files` (544–546) | contract leg (counter 274–304) validates rows; malformed contract only in tool selftest `t_contract` (tool 425–440) |
| files (fnmatch expansion over `ls-tree`, sorted, dedup) | yes (pattern expansion, sort) | 437–438 patterns → LOG.md + r1/r2.md; files equality 541–543 | same in contract leg; overlap-dedup never reachable by current patterns (all disjoint) |
| commits (topo-order, first-parent diff, root skip) | yes for linear/root; **merges: no** | fixture has 0 merges; root c-root (445) | lane has 2 merges (2f7303c, 5396a876) but their non-first-parent diffs have max 2 deletions (below threshold) → invisible; tool selftest `t_merge_first_parent` (353–366) uses `-s ours` (second-parent diff is additions) → also invisible (see §4 F2) |
| lines (blob split, trailing nonempty segment, byte-exact, `\r` in line) | yes | CRLF (425), `--`/`---` (424), triplicated (426), no-final-newline (431); E1 deletes all special kinds (448–458) | tool selftest `t_dashdash`, `t_crlf_and_eof` |
| deleted (hunk-header count == numstat; multiset D) | yes | all events 448–511; 19-cut no-event (507–511); undeclared notes −30 no-event (461–464) | tool selftest `t_dashdash` (22 lines incl. `--`) |
| event (deleted ≥ 20) | yes, but **exact-20 is nondeterministic** | k1∈[22,30], k2∈[20,26], k3∈[20,24], move=21, cut=19; exactly-20 only when k2/k3 draw 20 (P=11/35 per run) | tool selftest `t_exact_unrestored` (301–309) pins exactly 20 deterministically; lane events all ≥31 → lane never discriminates the boundary (see §4 F3) |
| K (M_parent − D) | yes (K>0 and K=0) | trip: D=1,K=2 (426,451); kept lines K=1 in E1/E3 | tool selftest `t_multiset` (D=3,K=0) |
| held (min(D, max(0, M−K))) | **clamp negative branch: no** | all fixture M≥K by construction — post-event removals only touch deleted lines (K=0) | lane has exactly one real trigger (empty-line group K=432→M=7, event dd9f5dc6 at window commit 0718b6ab) but it changes no output key; tool selftest `t_window_max` trims only restored (K=0) lines → clamp never observable (see §4 F1) |
| window (event commit → `<to>` inclusive) | yes | multi-commit windows; sustained max (move 500–506); later decrease (c-again 492–495) | stable leg (counter 555–584) exercises cross-tip monotonicity |
| restored_max | yes | partial/restored/unrestored all present (480–506) | — |
| restored_best (first attaining; null when 0) | yes | r3/r1c/mv/None (496–506) | lane partial-event ties (attained at many commits) |
| restored_by (first full; else null) | yes | r3/mv/None; sustained full at mv..tip → first-vs-last tie-break visible | lane restored events sustained to tip |
| status (restored/unrestored/partial) | yes | E1 partial, E2 unrestored, E3/move restored | — |

## 3. Variants: wrong only in one unexercised clause

Each variant = a fresh `git clone --shared` of the lane at the fixture identity + one commit that edits only
`tools/append-only-audit.py` (identity env `user.name=fixture`, `-c user.name/-c user.email/-c commit.gpgsign=false`;
toplevel asserted before commit; no lane/fleet write). Counter run per variant with `--tip=<variant tip>`.
Patches: `out/K1Fixture/<V>.patch`; run outputs: `out/K1Fixture/run-<V>.out`.

| variant | clause mutated | change (tool line) | selftest | contract | lane | fixture | stable | met |
|---|---|---|---|---|---|---|---|---|
| V-A | held clamp dropped | `max(0, M[l]-K[l])` → `M[l]-K[l]` (212) | 1 | 1 | 1 | 1 | 1 | **True (exit 0)** |
| V-B | absent blob → parent lines | `M = r.lines(wb[…])` → fallback to parent blob (211) | 0 (14/1) | 1 | 1 | 1 | 1 | False |
| V-C | merge last-parent | `parts[1]` → `parts[-1]` (191) | 1 | 1 | 1 | 1 | 1 | **True (exit 0)** |
| V-D | exact-20 boundary | `ns[f] < threshold` → `ns[f] <= threshold` (199) | 0 (13/2) | 1 | 1 | 1* | 1 | False |
| V-E | multiset→set D | `collections.Counter(dl)` → `Counter(set(dl))` (204) | 0 (14/1) | 1 | 0 (8 mism) | 1 | 1 | False |
| V-F | v1-style tip-only restoration | window scan → only last window commit (209–217) | 0 (12/3) | 1 | 0 (10 mism) | 0 (8 mism) | 1 | False |

Variant tips: V-A `44aafd6770a141409fa57e6adab600f678fee27c` (first attempt `eeec0dc2…` had a broken indentation — kept as
`run-V-A-broken-indent.out` for transparency), V-B `f0dc5ff5c3206ae3b7eef163776874b139395652`,
V-C `bc86bd5dfbcb3ea4c04abb30ca9bd3e2e1050927`, V-D `7ebb7e2dfa2e09e96cb1586c8681ac33f6851066`,
V-E `0e3d3ec763f5c8ffeb11791f2e0a596fd31b921e`, V-F `9d69a61ff48a1c2921ee1211d30ff01df341309b`.

*V-D fixture = stochastic: 12 of 15 runs fixture=1 (fixture_mismatch=0), 3 of 15 fixture=0 (mismatch=1) — exact-20 drawn only when k2 or k3 = 20 (P = 1−(6/7)(4/5) = 11/35 ≈ 31%).

## 4. Findings

### F1 — the `held` clamp `max(0, M[l]−K[l])` is unverifiable by every leg (V-A passes `met=True`)
- Defect location: tool `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py:212`; the counter's own
  recomputation has the identical formula (`round47-append-audit-v2-check.py:228`), so both share the blind spot.
- Command that shows it: `python3 …/round47-append-audit-v2-check.py --repo $S/V-A --tip 44aafd6770a141409fa57e6adab600f678fee27c --scratch $S/run-V-A-fixed`
  → `selftest=1 contract=1 lane=1 fixture=1 stable=1 … met=True`, exit 0 (evidence `run-V-A-fixed.out`, `V-A.patch`).
- Why it is invisible: the multiset formula only differs when some window commit has `M[l] < K[l]` (a kept line removed after
  the event). The lane contains exactly one such case — event dd9f5dc6 SCORECARD.md, empty-line group K=432 → M=7 at window
  commit 0718b6ab — and there the unclamped held is −425 vs 0 (`k1_vacompare.py`: exactly one held-map difference, zero KEY
  difference), i.e. the divergence never lands on the argmax commit, so all seven output keys are unchanged. The fixture never
  produces M<K at all (post-event removals only delete K=0 lines). Tool selftest `t_window_max` trims only restored (K=0) lines.
- Proposed fix (smallest safe): make the fixture create a visible M<K case — after a restoration, delete one **kept
  duplicate** line (K>0) in a later commit while some other deleted lines remain restored, so the clamped and unclamped
  `restored_max` differ (status flips restored↔partial). Add an equivalent selftest case. Then V-A fails the fixture leg.

### F2 — merge-commit first-parent selection is exercised by no leg (V-C passes `met=True`)
- Defect location: tool line 191 (`parents[parts[0]] = parts[-1]`); counter line 209 (`parts[1]`).
- Command: `python3 …/round47-append-audit-v2-check.py --repo $S/V-C --tip bc86bd5dfbcb3ea4c04abb30ca9bd3e2e1050927 --scratch $S/run-V-C`
  → `met=True`, exit 0 (evidence `run-V-C.out`, `V-C.patch`).
- Why invisible: the fixture has no merge commits. The lane has two merges (2f7303c, 5396a876) but their non-first-parent
  diffs have at most 2 deletions of contract files (verified `git diff --numstat --no-renames <p2> <m> -- …`), so a
  last-parent tool emits the same 5 events. The tool selftest `t_merge_first_parent` (tool 353–366) merges with
  `-s ours`, whose second-parent diff is pure additions — it cannot distinguish first- from last-parent semantics.
- Impact: a tool that diffs merges against the wrong parent would mis-score any future merge whose side branch carries ≥20
  deletions of a declared file (e.g. a revert-squash), and this counter would bless it.
- Proposed fix: add a selftest case whose merge keeps the side branch's deleted tree (e.g. `-s theirs`, or an explicit tree
  commit), asserting the event lands on the side commit and no phantom event appears at the merge; optionally add a merge
  to the fixture.

### F3 — the exact-20 event boundary is pinned only by the tool selftest; the fixture leg is nondeterministic on it (V-D)
- Defect location: tool line 199 (`ns[f] <= threshold` vs `ns[f] < threshold`); counter `recompute` line 218 uses `<`.
- Command: `python3 …/round47-append-audit-v2-check.py --repo $S/V-D --tip 7ebb7e2dfa2e09e96cb1586c8681ac33f6851066 --scratch $S/run-V-D-<n>`
  → `selftest=0 … met=False` always (tool selftest `t_exact_unrestored` pins 20), but `lane=1` in all 15 runs (lane events
  are 31..2421) and `fixture=1` in 12/15 runs (evidence `run-V-D-*.out`). So the fixture alone would admit the boundary bug
  in ~69% of runs; only the tool's selftest catches it deterministically.
- Proposed fix: in `build_fixture()` pin one event at exactly 20 (e.g. fix k2=20 or make the 21-line move a 20-line move) so
  the threshold boundary is deterministic, not a draw.

### Gaps rescued by other legs (no counter defect, but fixture-blind)
- V-B (absent file ⇒ parent lines): `selftest=0` only — the absent-file branch is exercised only by tool selftest
  `t_file_removed` (343–351). The fixture never deletes a declared file; the lane's contract files persist. If the tool
  selftest were ever removed, this branch would be unobservable.
- V-E (multiset→set): caught by selftest **and** lane (`lane_mismatch=8`) — lane deleted-line multisets contain duplicates
  (LOG.md 2292→2005 distinct, SCORECARD.md 2421→1793, QUALITY.md 375→209, README.md 663→483), so the fixture's single
  triplicated line (D=1) would not have caught it. The lane rescues this fixture gap.
- V-F (v1 D2 regression): caught by selftest, lane and fixture — the window-maximum property is solidly pinned.

## 5. Evidence artifacts (absolute paths)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K1Fixture.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K1Fixture/`
  - `run-baseline.out`, `run-V-A-fixed.out`, `run-V-A-broken-indent.out`, `run-V-B.out`, `run-V-C.out`, `run-V-D.out`,
    `run-V-D-{2..15}.out`, `run-V-E.out`, `run-V-F.out`
  - `V-A.patch`, `V-B.patch`, `V-C.patch`, `V-D.patch`, `V-E.patch`, `V-F.patch` (unified diffs vs 3a09a1d…)
  - `stat.txt`

No tools installed (nothing beyond existing python3/git needed; no pacman, no uv/npm).
Fixture clones, analysis scripts and run scratch lived under `/fast/scratch/hyaku/kama-r47/K1Fixture/` and were removed on
finish (verbatim evidence copied to `out/K1Fixture/` first).

Contributions: this seat is a leaf; no subagents spawned, no peer coordination needed.
