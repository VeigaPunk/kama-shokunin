# SC03MistakeSweep — round-87 wave 1 (read-only mistake sweep)

Seat: SC03MistakeSweep · Lane: kama · Milestone: kama r87 w1 · Read-only seat (no gate run, no lane edit).

- Freeze commit measured: `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659` (`master` = `HEAD` = this hash; `rev-parse --abbrev-ref HEAD` → `HEAD`, detached/exported).
- Base: `362b0d4a241520c9bc79b204c042d9fcefbb06ea`.
- All git commands below were read-only (`status`, `log`, `ls-files`, `ls-tree`, `cat-file`, `check-ignore`, `diff --stat`, `rev-parse`). No gate was run.

---

## Scope

The seat spec asks for three things, all performed:

1. Lane + fleet-root working-tree status, every untracked/modified path enumerated and its round named.
2. Round-86 stray confirmation: do `w3/EX02GateCensus.md` / `w3/CN01OverlapScan.md` exist on disk; do their `out/` dirs exist and are they tracked.
3. Exact path visibility of the `round-clean` and `round-scope` gate arms, read from source.

I also swept the live tree for mistakes the two arms would and would not catch, since item (3) determines the honest "captured-by" answer for each class.

---

## Commands and outputs

### 1. Lane status

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain -uall
```

Exit 0. Every path is under `.ufo/waves/round-87/` → **round 87** for all of them. Categorised (71 records at the time of the sweep; the wave is still running so the count grew during the sweep):

```
 56 w1/out/*                     (seat out-dir deliverables)
 15 w1/<SEAT>.md                 (seat report trailers)
  7 w1/-runtime                  (w1-dispatch.json, w1-plan.out, w1-run.err,
                                  w1-spec.json, w1.ready, w1.ready.dispatched,
                                  w1/swarm-registry.json)
```

Sample of the runtime + seat-report records:

```
?? .ufo/waves/round-87/w1-dispatch.json
?? .ufo/waves/round-87/w1-plan.out
?? .ufo/waves/round-87/w1-run.err
?? .ufo/waves/round-87/w1-spec.json
?? .ufo/waves/round-87/w1.ready
?? .ufo/waves/round-87/w1.ready.dispatched
?? .ufo/waves/round-87/w1/swarm-registry.json
?? .ufo/waves/round-87/w1/CN01OverlapScan.md
?? .ufo/waves/round-87/w1/EX02GateArmWire.md
?? .ufo/waves/round-87/w1/MT01SelectorBattery.md
?? .ufo/waves/round-87/w1/SB01LessonDraft.md
```

**Round attribution: round 87 for every one.** No modified (tracked) lane file — the `??`-only output means the lane tree's tracked content is byte-clean at the freeze.

### 2. Fleet-root status

```
$ git -C /home/vgpnk/Projects/shokunin status --porcelain
 M .scratch/run15-state.json
```

Exit 0. One modified path: `.scratch/run15-state.json`. It is a **fleet-root** file, not a kama-lane path — it carries the hyaku run-15 lane ledger (`"run": 15`, `"date": "2026-11-03"`, per-lane `block_start` counters; kama's entry reads `"block_start": 87`). It has **no round in its path**: the round it belongs to is the operator's *run 15*, not a kama round. Its own lane field is `kama → block_start 87`.

Note the fleet root ignores the lane: `.gitignore:1:*-shokunin/` (`git check-ignore -v kama-shokunin` → `.gitignore:1:*-shokunin/  kama-shokunin`, exit 0). So the fleet-root status can never show a kama-lane straggler; the lane's own status is the only view.

### 3. Lane log

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --oneline -3
94e8fe7b round-87: freeze claims C1/C2, do-nothing controls, commit round-86 strays (R86V1)
362b0d4a round-86 verifier spot-check (integrator, hyaku): non-author admit/reject
079cd67c round-86: normalize the fence-line wording in the record
```

Exit 0. `94e8fe7b` adds exactly 8 files (579 insertions): `.ufo/waves/round-86/w3-results.json`, `.ufo/waves/round-86/w3/SC01DanglingPointers.md`, `.ufo/waves/round-86/w3/out/SC01DanglingPointers/findings.md`, the four `.ufo/waves/round-87/controls/` files, and `plans/round-87-claims.md`.

### 4. Round-86 strays — disk presence and tracked state

```
$ for p in .ufo/waves/round-86/w3/EX02GateCensus.md .ufo/waves/round-86/w3/CN01OverlapScan.md \
           .ufo/waves/round-86/w3/out/EX02GateCensus .ufo/waves/round-86/w3/out/CN01OverlapScan; do ... done
ABSENT .ufo/waves/round-86/w3/EX02GateCensus.md
ABSENT .ufo/waves/round-86/w3/CN01OverlapScan.md
EXISTS .ufo/waves/round-86/w3/out/EX02GateCensus
EXISTS .ufo/waves/round-86/w3/out/CN01OverlapScan
```

```
$ git -C ... ls-files '.ufo/waves/round-86/w3/**'
```

Exit 0. The listing contains `.ufo/waves/round-86/w3/out/EX02GateCensus/findings.md` and `.ufo/waves/round-86/w3/out/CN01OverlapScan/findings.md` — **both `out/` dirs are tracked** — and contains **neither** `w3/EX02GateCensus.md` nor `w3/CN01OverlapScan.md`. The two seat-report trailers are absent from disk *and* from the index.

Round attribution: **round 86** (path `.ufo/waves/round-86/w3/`).

Confirmed by the w3 settlement record, which contains all 12 seats including the two:

```
$ python3 -c "… json.load(open('.ufo/waves/round-86/w3-results.json')) …"
EX02GateCensus   | agent=executor   | output: "# EX02GateCensus verdict — kama r86 w3, terminal record tip bafae7af…"
CN01OverlapScan  | agent=connector  | output: {"summary": ["C1: adjacent precedents in souji/mori/kaidoku…", …]}
```

So both seats ran and produced output; only their `Report:` trailer files were never written. 10 of 12 round-86 w3 seat trailers are tracked (`.ufo/waves/round-86/w3/*.md`, direct children only).

### 5. Arm visibility — read from source

**`round-clean`** — `tools/pre-report-gate.py:615-616`, and the arm record at `:628-633`:

```python
wave_rel = f".ufo/waves/round-{round_no}"
argv_clean = ["git", "-C", repo_path, "status", "--porcelain", "-uall", "--", wave_rel]
```

Scope: **exactly one round directory**, `.ufo/waves/round-<N>/` for the `--round` value passed on the command line, in the primary worktree only. At `--round 87` it sees `.ufo/waves/round-87/` and nothing else. It sees tracked-modified and untracked (`-uall`) records under that directory. It does **not** see git-ignored records (no `--ignored` flag), other rounds, other directories (`tools/`, `plans/`, `corpus/`), or linked worktrees. It cannot see a file that does not exist.

**`round-scope`** — `tools/pre-report-gate.py:256-257` runs `tools/round73-round-scope-cases.py --repo <repo> --round <N> --tip <tip>`; six cases (`CASE_ORDER`, `tools/round73-round-scope-cases.py:96`), dispatched at `:344-362`:

| case | source | paths it can see |
|---|---|---|
| `label` | `round72-round-scope.py:229` | `plans/round-<N>-claims.md` at `--tip` only — the round's own plan |
| `stray` | `round72-round-scope.py:252` | **whole primary worktree**, `git status --porcelain -uall` with no path argument — every untracked/modified path in the repo, any round, any directory, minus `--allow` |
| `ignored` | `round72-round-scope.py:267` | `.ufo/waves/round-<N>/` only, `--ignored` records |
| `worktree` | `round73-round-scope-cases.py:155` | every linked worktree's whole status |
| `ignored-older-label` | `round73-round-scope-cases.py:181` | every present `.ufo/waves/round-<M>/` with **M ≥ N** — at `--round 87` that is round-87 and later only; round-86 and older are outside the population by design |
| `submodule` | `round73-round-scope-cases.py:249` | every initialised submodule worktree + parent |

Measured visibility of the live tree:

```
$ git status --porcelain -uall -- .ufo/waves/round-87        → 71
$ git status --porcelain -uall                               → 71   (same set)
$ git status --porcelain -uall --ignored -- .ufo/waves/round-87
!! .ufo/waves/round-87/controls/__pycache__/c1-probes.cpython-314.pyc
```

The `__pycache__` is git-ignored (`.gitignore:3:__pycache__/`), so it is invisible to `round-clean` (no `--ignored`) but **visible to `round-scope`'s `ignored` case** at `--round 87` — that is the one arm that can see it.

---

## Findings

Each class: class · evidence pointer · captured-by (decided from §5) · fix.

### MC1 — round-86 seat-report trailers never written (2 of 12)

- **Class:** missing deliverable; a `Report:` trailer contract that was declared but never materialised, and whose absence is invisible to every gate arm.
- **Evidence:** `.ufo/waves/round-86/w3/EX02GateCensus.md` and `.ufo/waves/round-86/w3/CN01OverlapScan.md` — ABSENT on disk and absent from `git ls-files`; their `out/` evidence dirs are tracked (`out/EX02GateCensus/findings.md`, `out/CN01OverlapScan/findings.md`). Both seats have output in `.ufo/waves/round-86/w3-results.json`. Required by `corpus/lessons/round-86-verifier-spotcheck.md:13` and `:80` ("write the missing `w3/EX02GateCensus.md` and `w3/CN01OverlapScan.md` seat reports (or record why absent)").
- **Captured-by:** **none.** `round-clean` is round-scoped to `--round <N>` (`:616`) and sees only that round's directory; at `--round 86` it would have seen the *untracked* strays, but a file that was never created produces no `git status` record at all — no arm grades "declared path absent". `round-scope`'s `stray` case (`round72-round-scope.py:252`) lists existing untracked paths, not missing ones; `label` grades one plan file; `ignored`/`worktree`/`submodule` grade ignored records and worktrees. `seat-yield.py` counts missing seat reports, but it is **not wired into any gate arm** (`grep -rn seat-yield tools/` matches only its own file) and its `locate()` needs a `*-results.json`/`results.json` *inside* the wave dir, while rounds 85/86 put it one level up (`.ufo/waves/round-86/w3-results.json`), so `seat-yield.py .ufo/waves/round-86/w3` exits 2 `could-not-evaluate` (measured).
- **Fix:** write the two trailers (their content is recoverable from the committed `w3-results.json` `output` fields and the committed `out/` evidence) or record explicitly why absent; and give the gate an arm that grades declared-path existence, since no arm does today.

### MC2 — the round-87 wave's own untracked artifacts (71 paths) will turn the gate red

- **Class:** uncommitted round work — the exact R86V1 class, one round later.
- **Evidence:** the 71 `??` records in §1, all under `.ufo/waves/round-87/`. The C2 do-nothing control receipt `.ufo/waves/round-87/controls/c2-gate-before.out:6` shows `PRE_REPORT_ARM round-clean exit=0 ok files=0` — measured *before* the wave wrote anything. Round-86's identical class is documented at `corpus/lessons/round-86-verifier-spotcheck.md:13,43,80`.
- **Captured-by:** **both** `round-clean` (`pre-report-gate.py:615-616`, scoped to `.ufo/waves/round-87/`) and `round-scope`'s `stray` case (whole-repo). This is the one class the gate is built to catch, and it is caught twice.
- **Fix:** the L1 commits the wave outputs (seat trailers + `out/` payloads + the 7 runtime files) before the terminal gate run, as rounds 85/86 did — round-86's `w1-dispatch.json`, `w1-spec.json`, `w1.ready`, `w1/swarm-registry.json` were committed in `f4c7acaa` at dispatch time and `w1-run.err` in `c5d71b7a`.

### MC3 — `w1-plan.out` is a new artifact class with no tracked precedent

- **Class:** untracked runtime artifact that no prior round committed.
- **Evidence:** `.ufo/waves/round-87/w1-plan.out` (36.8 KB) is untracked. `git ls-files | grep plan.out` returns only two unrelated fixtures (`.ufo/waves/round-81/measured/control/debt-no-plan.out`, `.ufo/waves/round-83/w1/CR01FalsifyClaims/frozen-plan.out`); `git log --all --diff-filter=A -- '*w1-plan.out' '*w2-plan.out' '*w3-plan.out'` is empty, and no `w*-plan.out` exists on disk in any earlier round. Every other round-86 wave runtime file has a tracked precedent.
- **Captured-by:** `round-clean` and `round-scope`/`stray` — both. But unlike MC2 there is **no precedent for committing it**, so the L1 must make a deliberate choice rather than follow the round-85/86 pattern by analogy.
- **Fix:** commit it alongside the other six runtime files (it is the wave plan the driver wrote, comparable to `w1-dispatch.json`), or drop it from the wave dir. Leaving it untracked is what makes the terminal gate red.

### MC4 — a git-ignored `__pycache__` inside the round-87 controls dir

- **Class:** git-ignored artifact written into the current round's wave directory.
- **Evidence:** `git status --porcelain -uall --ignored -- .ufo/waves/round-87` → `!! .ufo/waves/round-87/controls/__pycache__/c1-probes.cpython-314.pyc` (mtime 2026-11-05 05:12:36). Mechanism reproduced in scratch: `importlib.util.spec_from_file_location(...).exec_module(...)` on `controls/c1-probes.py` writes a sibling `__pycache__` because that file's `load()` does **not** set `sys.dont_write_bytecode` — unlike the lane's own guarded importers (`tools/round73-round-scope-cases.py:121-128` sets `sys.dont_write_bytecode = True` around `exec_module`; `tools/pre-report-gate.py:428` sets `PYTHONDONTWRITEBYTECODE=1` for children). The frozen battery `controls/c1-probes.py:23-31` has no such guard.
- **Captured-by:** `round-scope`'s `ignored` case only (`round72-round-scope.py:267` — `.ufo/waves/round-<N>/` with `--ignored`, at `--round 87` that is the round-87 dir, so it **is** in population). `round-clean` cannot see it (no `--ignored` flag). Note `ignored-older-label` (`round73-round-scope-cases.py:181-193`) skips `M < N` **by design** — the source comment at `:36` says older rounds are excluded because "the lane's committed-then-ignored `__pycache__` leftovers live there" — so the same artifact is tolerated in round-86 but is a live finding in round-87.
- **Fix:** the L1 removes `.ufo/waves/round-87/controls/__pycache__/` before the terminal gate run, and the guard idiom from `round73-round-scope-cases.py:121-128` is the precedent to copy into any tool that `exec_module`s a path under the wave dir.

### MC5 — the C2 do-nothing control's `round-scope` failure is under-explained in the receipt

- **Class:** evidence-quality defect in a frozen control receipt; the arm's detail line names one finding while the count says four.
- **Evidence:** `.ufo/waves/round-87/controls/c2-gate-before.out:5` reads `PRE_REPORT_ARM round-scope exit=1 FAIL ROUND_SCOPE_V2 round=87 cases=6 findings=4 | ROUND_SCOPE_V2_FINDING label plans/round-87-claims.md rev=master status=absent`. The gate prints `findings=4` but names only `defects[0]` (`pre-report-gate.py:399-403`: `defects[0]` appended to the detail). The other three findings are not in the receipt.
- **Captured-by:** not a defect class the gate arms are meant to catch; it is a **receipt-fidelity** limit of the gate's own `_detail()` helper. The three unnamed findings are, from source, the three case-`stray` records the round-86 strays would produce (whole-repo `git status --porcelain -uall`, `round72-round-scope.py:252`) — consistent with the same receipt's `round-clean exit=0 ok files=0`, which proves the strays were outside round-87's wave dir and therefore visible **only** to `stray`. This confirms §5's asymmetry empirically.
- **Fix:** none required for C1/C2 correctness — but the report should not cite `findings=4` as four round-87 problems. Only the `label` finding is round-87-specific; the other three are round-86 residue.

### MC6 — the round-scope `label` case is red until the freeze commit lands on `master`

- **Class:** plan-not-at-tip; the round's own claims plan is invisible to the `label` case at the base revision.
- **Evidence:** `controls/c2-gate-before.out:5` — `ROUND_SCOPE_V2_FINDING label plans/round-87-claims.md rev=master status=absent`. Confirmed structurally: `.ufo/waves/round-87` does not exist at base (`git cat-file -t 362b0d4a:.ufo/waves/round-87` → `fatal: path … exists on disk, but not in '362b0d4a'`; `ls-tree` at base ends at `round-86`). The plan exists only from `94e8fe7b` onward.
- **Captured-by:** `round-scope`'s `label` case (`round72-round-scope.py:229-249`, reads the plan blob at `--tip`). This is the arm doing its job; the red is a base-state fact, not a defect.
- **Fix:** none — it is expected to turn green once `master` carries `plans/round-87-claims.md`. The C2 harm rule ("every `PRE_REPORT_ARM` line ok at `362b0d4a` stays ok at R") is unaffected: `round-scope` was already red at base, and the base-ok arms (`receipt-audit`, `worktree-landing`, `round-clean`, `round74-v2`, `round77`/`78`/`81`/`82`/`83-instruments`) are all ok at base and all green in the receipt.

### MC7 — `w1-plan.out` and the seat-trailer convention are inconsistent with round-86's layout

- **Class:** layout drift in the wave directory that a round-scoped arm will count as uncommitted.
- **Evidence:** round-86 tracked its seat trailers at the **wave-dir top level** (`.ufo/waves/round-86/w3/SC01DanglingPointers.md`, 10 of 12) with detail under `w3/out/<SEAT>/`. Round-87 writes trailers to `.ufo/waves/round-87/w1/<SEAT>.md` (15 present, untracked) and payloads to `w1/out/<SEAT>/`. The same convention holds for round-85 (`w1/CR01PredicateCritic.md` etc., 4 trailers) but round-85/w1 also has `out/CN01OverlapScan/CN01OverlapScan.md` — so both shapes exist in the lane.
- **Captured-by:** `round-clean` + `round-scope`/`stray` — as MC2/MC3, by untracked-ness, not by layout.
- **Fix:** no change needed to layout; commit what the seats wrote. Noted so the L1 does not "normalise" a shape the seat spec did not ask for.

---

## Observations that are NOT defects (recorded so the L1 does not chase them)

- **The three round-86 R86V1 strays are genuinely fixed.** `94e8fe7b` commits `w3-results.json`, `w3/SC01DanglingPointers.md` and `w3/out/SC01DanglingPointers/findings.md`; `git status` shows no round-86 path. The claims file's statement "the three files are committed as they stand, not rewritten" is accurate.
- **The round-86 `out/` dirs being tracked while the trailers are not is not an inconsistency** — it is exactly the MC1 shape: evidence committed, deliverable absent.
- **The fleet-root `.scratch/run15-state.json` modification is not a kama defect.** It is the operator's run-15 ledger in the fleet repo, outside the lane, and the lane is git-ignored from the fleet root (`.gitignore:1:*-shokunin/`). It carries no round in its path; the round it belongs to is run 15.
- **No tracked lane file is modified.** The lane's `??`-only status means `tools/`, `plans/`, `corpus/`, `SCORECARD.md`, `LOG.md` are byte-clean at the freeze.

---

## Deliverables

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-87/w1/out/SC03MistakeSweep/sweep.md` — this report.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-87/w1/SC03MistakeSweep.md` — the `Report:` trailer copy.
- No lane tree file was edited. Scratch dir `/fast/scratch/hyaku/kama-r87/SC03MistakeSweep/` removed.
- No tool was installed or upgraded (no pacman, uv, cargo, npm, release binary).

---

VERDICT: The two round-86 seat-report trailers (`w3/EX02GateCensus.md`, `w3/CN01OverlapScan.md`) remain unwritten and **no gate arm can see that** (captured-by: none) — MC1; round-87's own 71 untracked wave paths plus the new `w1-plan.out` (no tracked precedent) will turn both `round-clean` and `round-scope` red unless the L1 commits them — MC2/MC3; and a git-ignored `__pycache__` now inside `round-87/controls/` is visible to `round-scope`'s `ignored` case only — MC4; all round-87 paths attributable to the wave, the fleet-root `.scratch/run15-state.json` is run-15 state outside the lane.
