# EX01SelfAssessControl — round-97 instruments run against round-98 claim surfaces

Seat: EX01SelfAssessControl · Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` · Repo rev tested: `34ad44e9f783b35a804f020d6b02c48c04ade481` (`34ad44e9 round-98 freeze`, `master`) · Plan: `plans/round-98-claims.md` (read first, C1/C2/C3 frozen predicates bound this cross-check) · Date: 2026-11-08

## Command 1 — round-97 self-assessment audit at master (freeze commit)

Command (run from `/home/vgpnk/Projects/shokunin/kama-shokunin`, `bash`):

```
python3 tools/round97-self-assessment-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev master
```

Exact output (captured verbatim to scratch `r97-selfassess.out`):

```
SELF_ASSESS97 checks=18 mismatches=0 met=True rev=34ad44e9f783b35a804f020d6b02c48c04ade481 skill_sha256=863eb35d606eff786035df9a22a98922a4471f39171b0725bc70ea018067b068
```

Exit: `0`

### Decision on the heading word 'three' — PASS (it does pass, as predicted)

The master's live SKILL heading still reads, at `SKILL.md:2443`:

```
### Round 97 correction (step-budget boundary table and the three graded forgeries; dated 2026-11-08)
```

verified by `git show master:SKILL.md | grep -n "Round 97 correction"`. At the same rev the frozen round-97 population is four mutants / four cells, and round-98's C1 rolls the graded population to five mutants / 19 cells — so the heading word `three` is a live mismatch against both. The round-97 audit nonetheless prints `mismatches=0` because its `section()` helper never reads the heading line. Evidence, `tools/round97-self-assessment-audit.py:87-97` (confirmed byte-identical at `master` via `git show master:tools/round97-self-assessment-audit.py | sed -n '87,97p'`):

```python
def section(text: str, heading: str):
    lines = (text or "").splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith(heading)), None)
    ...
    for l in lines[start + 1:]:        # line 93: heading line (index `start`) excluded; body starts at start+1
```

So `section()` matches the heading only to locate the body, then slices from `start + 1`, i.e. the heading line itself is structurally invisible to every check that grades §Round 97 (notably check 16, docstring at lines 39-41: "SCORECARD's depth row, SKILL's §Round 97 and the counter docstring each name W14-W17 and say four"). The audit grades the body prose's `four` and passes; the heading's `three` is ungradable by construction. This is exactly the heading-count blindness named in round-98's frozen plan ("the round-97 audit carried (its check 16 never read the section heading, so the live 'three graded forgeries' heading passed while the body said four)"), and this cross-check reproduces it live at the freeze commit.

## Command 2 — round-97 router-budget control at master (`--cells new --expect survived`)

Command (run from `/home/vgpnk/Projects/shokunin/kama-shokunin`, `bash`):

```
python3 tools/round97-router-budget.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev master --work /fast/scratch/hyaku/kama-r98/EX01SelfAssessControl --cells new --control --expect survived
```

Exact output (captured verbatim to scratch `r97-budget.out`; `entries=0` on every cell):

```
ROUTER_BUDGET97_CELL nat W14-900k-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.36s entries=0
ROUTER_BUDGET97_CELL nat W15-700k-nd4 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.30s entries=0
ROUTER_BUDGET97_CELL nat W16-maxmeta ok=1 want=MODEL_UNLOADED/router-model-invalid run1=MODEL_UNLOADED/router-model-invalid/0.16s entries=0
ROUTER_BUDGET97_CELL nat W17-833333-nd1 ok=1 want=MODEL_OK/router-unloaded-autoload run1=MODEL_OK/router-unloaded-autoload/2.36s entries=0
ROUTER_BUDGET97_CONTROL cells=4 cells_ok=4 mutant=none slow_files=40 runs=1 expect=survived expect_cell=- cell_ok=- survived=1 caught=0 probe=rev probe_sha256=40ab387ee9877a9505af61172db5fc1cd2006021fb026e761e558e307a5b4a6e rev=34ad44e9f783b35a804f020d6b02c48c04ade481 ok=1
```

Exit: `0` (wall ~13 s; second run 12.86 s, first identical run 21.73 s)

Notes: `--cells new` here selects round-97's "new" set = the four C2 cells W14-W17, `cells=4 cells_ok=4`. `mutant=none` because no `--mutant` given (this leg is a natural-probe-survived control, not an overcharge-mutant leg); `survived=1` is the expected control outcome, not a claim about forgery resistance. `probe_sha256=40ab387ee9…` is the probe bytes at rev `34ad44e9`.

## Verdict — do the round-97 instruments discriminate round-98's defects?

No: both round-97 instruments are green on round-98's freeze commit while the two round-98 defects they should in principle see are live on the same bytes. The self-assessment audit prints `checks=18 mismatches=0` at the freeze commit even though the graded heading says "three" while the frozen populations are four (round-97) and five (round-98) mutants — because `section()` at `tools/round97-self-assessment-audit.py:93` slices the heading line away (`lines[start + 1:]`), so check 16 grades the body's "four" and never the heading's word. The budget counter likewise stays green (`cells=4 cells_ok=4 survived=1`, exit 0) because its 17-cell / 4-new-cell sets contain no cell that separates a `+1/header` overcharge parse from the real parse — every cell it scores (W14-W17) is on the same side of `MAX_STEPS` under both parses, which is precisely the window round-98's W18-800k-nd1 and W19-520k-nd4 cells (19-cell successor set, round98 counter) exist to close. Neither round-97 instrument is therefore usable as a discriminator for the round-98 claims C1 and C2; only the successor round98 counters (20 checks with the heading graded at check 19; 19 cells with W18/W19 pinning the overcharge class) discriminate the frozen defects. No tracked lane file was edited; receipts copied to the out dir; scratch removed before yield.

## Provenance / reproduction

- Lane repo: `/home/vgpnk/Projects/shokunin/kama-shokunin`, tested rev `34ad44e9f783b35a804f020d6b02c48c04ade481` (`master` = round-98 freeze, HEAD at seat run).
- Starting state verified: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --oneline -3` → `34ad44e9`, `681c80a4`, `ac014090`.
- Tools installed/upgraded: none (system `python3` + `git` only). RULES check: `/home/vgpnk/.omp/agent/RULES.md` read only if install needed — none performed for this seat (pacman untouched per host guard).
- Receipts: `out/EX01SelfAssessControl/r97-selfassess.out`, `out/EX01SelfAssessControl/r97-budget.out` (verbatim copies of scratch captures).
- No `git add/commit/stash/checkout/switch/reset/pull/push` or mutating jj command run; only `git show/rev-parse/log/grep` reads.
