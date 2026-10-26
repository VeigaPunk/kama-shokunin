# K2Cheat — round 46, C2 shortcut attack (calibration)

**Verdict:** the frozen C2 counter admits three non-capabilities at `met=True` — a tool that imports the
grader, a tool that recognises the fixture by its shape, and a shim that executes the genuine tool from a
fixed path — because the fixture is byte-shape-fixed and no leg ever reads the tool's source; `met=True`
therefore does not certify "capability acquisition 7 → 7". A tested hardening (randomized fixture + source
leg) rejects all three and keeps the genuine tool at `met=True` (3/3 runs, different random shapes).

Counter attacked: `kama-shokunin/tools/round46-append-audit-check.py` (frozen, 276 lines).
Build/controls state: `kama-shokunin/.ufo/waves/round-46/controls/{base,junk-c2-hardcoded,junk-c2-norestore}.c2.out`.

## Axes

| axis | question |
|---|---|
| A1 reach | does the shortcut reach `met=True` under the frozen counter? |
| A2 shortcut-ness | does it implement the capability or borrow/recognise it? |
| A3 cost | lines a shortcut needs vs. the genuine tool |
| A4 generality | works on repos it has never seen? |
| A5 detectability | is it caught by the frozen counter, by source inspection only, or not at all? |

Moves kept = those that raise A1/A5 (reach under the frozen counter, or defeat the cheapest hardening);
moves that raise A3 while keeping A1 were kept as the strongest attacks (T2/T5 are ~30 lines, T3 ~70).

## Reach table

Frozen counter, all runs on a `--shared` fixture clone of the lane (base `4a2a4d55`, cheat tool committed at
`tools/append-only-audit.py` with a SCORECARD row whose last cell is `46`; identity `r46-cheat <r46-cheat@invalid>`
inside the clone only). Full receipts: `receipts/frozen.*.out`, `receipts/summary.tsv`.

| # | candidate | frozen | hardened | classification |
|---|---|---|---|---|
| T1 | import the counter's `recompute` from `--repo` (`tools/t1-repo-import.py:15-24,37`) | **exit 1** `selftest=1 fixture=0 lane=1 table=1 met=False` | exit 1 (source=0, fixture=0) | insufficient |
| T2 | T1 plus fallback to a fixed absolute counter path (`tools/t2-fixedpath-import.py:14,18-20`) | **exit 0** `selftest=1 fixture=1 lane=1 table=1 met=True` | exit 1 (`source=0`) | **shortcut** |
| T3 | recognise the fixture (subjects `c1..c7` + `notes.md`) and emit its expected events; hardcode the lane's 5 events otherwise (`tools/t3-fixture-shape.py:58-67`) | **exit 0** `selftest=1 fixture=1 lane=1 table=1 met=True` | exit 1 (`fixture=0`) | **shortcut** |
| T4 | print the selftest pass line only, empty event list (`tools/t4-selftest-only.py:23`) | exit 1 `selftest=1 fixture=0 lane=0 table=1 met=False` | exit 1 | insufficient |
| T5 | `exec(compile(open(FIXED_TOOL).read()))` of the genuine tool from a fixed path, fake selftest (`tools/t5-fixedpath-real-tool.py:10,18-21`) | **exit 0** `selftest=1 fixture=1 lane=1 table=1 met=True` | exit 1 (`source=0`) | **shortcut** |
| B | genuine tool (`4a2a4d55:tools/append-only-audit.py`) + the missing SCORECARD row | exit 0 `met=True` | exit 0, 3/3 runs `met=True` | legitimate (reference) |

The lane's existing controls cover hardcopy replay and no-restoration but not these three: `junk-c2-hardcoded.c2.out`
shows the hardcoded-lane control fails **only** the fixture leg (`selftest=1 fixture=0 lane=1 table=1 met=False`),
i.e. the fixture is the single discriminator, and T2/T3/T5 defeat it without implementing anything.

## Defect 1 — the fixture is byte-shape-fixed, so it is recognisable

`tools/round46-append-audit-check.py:151-183` builds one fixed shape every run: `LOG.md`, 60 base lines,
+10 appended (`:166-171`), delete 30 (`:174`), restore (`:177`), delete 25 (`:179`), delete 5 (`:181`),
commit subjects literally `c1`..`c7` (`:170-181`), decoy `notes.md` (`:170,176,181`). The counter's own docstring
claims a fixture "whose content it cannot know in advance" (`:11`); the *content* is random, the *shape* is not.

Command that shows it (`T3` emits the two expected events from commit subjects alone, no diff is read):

```
S=/fast/scratch/hyaku/kama-r46/K2Cheat
python3 kama-shokunin/tools/round46-append-audit-check.py --repo $S/fxclone \
        --tip ae72db0d10b6ec0a52b363b5daec1701d2fd33ba --scratch $S/f2 --out receipts/frozen.t3-fixture-shape.out
# exit 0; selftest=1 fixture=1 lane=1 table=1 met=True
```

Smallest safe correction: draw the fixture per run — declared file from `FILES`, base/append counts,
deleted index sets (so counts are random), commit subjects as random hex, decoy file name random — and derive
the expected event set from those draws instead of literals (`:216-221` today). Implemented and tested in
`proposed/round46-append-audit-check.py:194-241` (`build_fixture` returns `meta`), `:281` (expectations
come from `meta`). Result: T3 `fixture=0`.

## Defect 2 — a tool may delegate to the grader, and no leg notices

The counter writes the tool at tip to a temp file and runs it as an opaque subprocess (`:206-208`, `run_tool`
`:139-141`); it never inspects what that source does. So a ~30-line tool that imports the frozen counter
(`T2`) or `exec`s the genuine tool (`T5`) produces the expected JSON on every repo, including the fixture, and
reaches `met=True` with the four frozen legs. `T1` shows the *only* accidental guard: a `--repo`-relative import
fails on the fixture because the fixture does not carry the counter — one fixed absolute path removes it.

```
python3 kama-shokunin/tools/round46-append-audit-check.py --repo $S/fxclone \
        --tip 0c36a696e81ebc48ff4957874eca640fe82cfdf1 --scratch $S/f2 \
        --out receipts/frozen.t2-fixedpath-import.out    # exit 0, met=True
python3 kama-shokunin/tools/round46-append-audit-check.py --repo $S/fxclone \
        --tip b929f4d8e1a8e923562516430b6d98cd35c31a59 --scratch $S/f2 \
        --out receipts/frozen.t5-fixedpath-real-tool.out # exit 0, met=True
```

Smallest safe correction: a fifth leg on the tool text at `--tip` — AST scan that rejects (a) the counter's name
in any non-docstring string, (b) `spec_from_file_location`/`module_from_spec`/`run_path`/`import_module`,
(c) `exec`/`eval`/`compile`/`__import__`, (d) a `subprocess` argument ending in `.py`.
Implemented and tested at `proposed/round46-append-audit-check.py:158-191` (scan), `:268-272` (leg),
`:256,323` (`source=` in the output line). Result: T2 and T5 `source=0` → `met=False`; the genuine tool,
whose docstring mentions the counter (`4a2a4d55:tools/append-only-audit.py:10-11`), still reads `source=1`
(the scan skips module/function docstrings), and the randomized fixture passes 3/3 runs.

## Defect 3 — the selftest leg is a string match

`:210-214` accepts any process that prints `AOA_SELFTEST pass=n fail=0` with `n >= 6` and exits 0; `T2`/`T3`/`T5`
print that line without running a selftest. Alone it is not enough (`T4` exits 1 at `lane=0`), which is why the
control `junk-c2-hardcoded` also failed only on `fixture`, but it removes one of four legs from the defence and
contributes nothing when combined with Defect 1. A cheap strengthening (untested, proposal only): run
`--selftest` on a copy of the tool whose declared threshold line is mutated and require a nonzero exit;
otherwise keep the leg and rely on the fixture + source legs.

## Impacted axes / judgment

- C2 is the calibration axis ("capability acquisition 7 → 7"). Each of T2/T3/T5 would let a seat claim the
  capability row with no capability present; the ledger's `restored_by`/`status` values in that case are true by
  construction (T2/T5) or copied from a fixed table (T3), so they carry no evidence.
- A1/A5: three reach `met=True`; after the proposed correction, none do and the reference tool still does.
  Regression surface of the correction is the fixture leg only (lane/table/selftest legs unchanged; the genuine
  tool's three lane events are untouched — receipts show identical 5-event lane lines).

## Residual risk (not fixed by the proposal)

The source leg is heuristic: a path assembled from fragments (`"round46-" + "append-audit-check.py"`,
`os.path.join` of parts) or `python3 -c` with inline code evades (a) and (d); only (b)/(c) catch the load
primitive. A tool that *vendors* a copy of `recompute` passes every leg — but then it computes the events from
git itself, so the question moves from capability to provenance, which belongs to the L1's review, not to the
counter. [INFERENCE] A sandboxed run (tool with the lane tree unreadable) would close delegation structurally;
that needs process isolation the counter does not currently use.

## Baseline / build status observed (not my item, but relevant to C2)

The genuine tool at `4a2a4d55` passes selftest/fixture/lane but fails `table`: no SCORECARD line contains
`append-only-audit` with last cell `46` at `4a2a4d55` **or** at the lane tip `96d32918`.

```
git -C kama-shokunin show 4a2a4d55:SCORECARD.md | grep -c 'append-only-audit'   # 0
git -C kama-shokunin show 96d32918:SCORECARD.md | grep -c 'append-only-audit'   # 0
python3 kama-shokunin/tools/round46-append-audit-check.py --repo kama-shokunin \
        --tip 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050 --scratch $S/c2base
# selftest=1 fixture=1 lane=1 table=0 met=False, exit 1
```

So C2 cannot be met at any measured commit until the capability row is appended; my fixture candidates add it
only in the throwaway clone to isolate the tool legs.

## Method / reproduction

Scratch `S=/fast/scratch/hyaku/kama-r46/K2Cheat` (removed at the end); one `--shared` clone, every commit with
`-c user.name=r46-cheat -c user.email=r46-cheat@invalid -c commit.gpgsign=false` and
`git rev-parse --show-toplevel == $S/fxclone` asserted before the first commit. Scripts kept at
`repro/drive.py` (build + frozen scoring) and `repro/harden.py` (hardened scoring). No lane file, index or jj
state touched; lane accessed read-only (`git show`, `git log`, counter `--repo`). No tools installed; pacman
untouched; `gh` unused.

Frozen run per candidate:

```
S=/fast/scratch/hyaku/kama-r46/K2Cheat
git clone -q --shared --no-checkout kama-shokunin $S/fxclone
git -C $S/fxclone checkout -q --detach 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050
cp <candidate>.py $S/fxclone/tools/append-only-audit.py
printf '\n| append-only-audit | control | tools/append-only-audit.py | 46 |\n' >> $S/fxclone/SCORECARD.md
git -C $S/fxclone add -A
git -C $S/fxclone -c user.name=r46-cheat -c user.email=r46-cheat@invalid -c commit.gpgsign=false \
        commit -q -m "round-46 c2 cheat <name>"
python3 kama-shokunin/tools/round46-append-audit-check.py --repo $S/fxclone --tip <sha> --scratch $S/f --out <receipt>
```

Hardened run: same `--repo/--tip`, counter replaced by `proposed/round46-append-audit-check.py`
(`proposed/hardening.diff`, 180 diff lines). Exit codes: frozen T2/T3/T5 = 0, T1/T4 = 1, reference = 0;
hardened T1/T2/T3/T4/T5 = 1, reference = 0.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K2Cheat.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K2Cheat/tools/{t1-repo-import,t2-fixedpath-import,t3-fixture-shape,t4-selftest-only,t5-fixedpath-real-tool}.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K2Cheat/receipts/{frozen,hardened}.*.out`, `receipts/summary.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K2Cheat/proposed/round46-append-audit-check.py`, `proposed/hardening.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K2Cheat/repro/{drive,harden}.py`
