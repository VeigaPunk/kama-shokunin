# Simp2Tool — YAGNI review, append-only-audit.py + check-fragment.py (round 46, lane kama)

**Verdict:** both tools are already lean; the only real dead weight is one duplicated full-history
traversal, three option/plumbing surfaces with zero callers (`--files` + its threading, `--scratch`)
and one tautological selftest clause. Proposed as `simplify.diff` (applies cleanly at lane HEAD
96d32918; −6 lines in the tool, one fewer `git rev-list` per run, no behaviour change on any
measured input). One duplicate selftest case found (`no-deletion` ≡ `below-threshold` on the tool's
code path) and deliberately **not** proposed for removal this round (receipts cite `pass=10`).
One real defect found in `check-fragment.py`: it exits 0 when a row is invalid.

## Method

Read both files in full plus the contracts that bind them: the C2 counter docstring
(`tools/round46-append-audit-check.py:1-82`) and its driver code (`:190-276`), and the C1 per-row rules
(`tools/round46-release-recheck-audit.py:196-340`). Baseline copies in scratch were
byte-identical to the lane files (`md5sum` = `82fca73a07f9de198ae67b616972f1a1` /
`2e057b4dfcfed15b176f1182bae9ed74`; `git status --porcelain -- <both paths>` empty). All edits were
made on scratch copies; the lane was not written to. No tools were installed (no pacman, no uv).

## Proposed deletions — `simplify.diff` (primary, all hunks proven)

| # | Site (baseline lines) | Deletion | Why it is weight | Proof |
|---|---|---|---|---|
| H1 | `tools/append-only-audit.py:85-89` | second `git rev-list --topo-order --reverse --parents` walk; `commits` now collected from the same walk | identical history walked twice; `commits` is exactly the key order of `parents` | `--json` byte-identical on the lane at `0163fea2`, `4a2a4d55` and with `--threshold 1` (`receipts/{lane,tip,thr}-{before,after}.json`, `cmp` silent) |
| H2 | `:81-82,90,96-97,121,299,314,316` | `--files` option, `audit(..., files=None)` parameter, `files or FILES`, `"files": files` | no caller anywhere in the lane or fleet (`grep -rn "append-only-audit.py.*--files"` → only the tool's own docstring and a `.pyc`); the JSON key survives as `FILES`, so the output shape is unchanged | `--files` now exits 2 (argparse, `receipts/flags-files.err`); every retained invocation identical |
| H3 | `:25,31,303,306` | `--scratch` option | every caller roots fixtures through `TMPDIR` (the C2 counter passes `env=dict(os.environ, TMPDIR=work)`; `build_controls.py:70` does the same for the counter) | `--selftest` with `TMPDIR` set → `AOA_SELFTEST pass=10 fail=0`; `--scratch` now exits 2 (`receipts/flags-scratch.err`) |
| H4 | `:261,265,272` | `base = git rev-parse HEAD`, the `main_c =` binding and `and base != main_c` | the clause compares two different commits' ids: it can only be False on a hash collision, i.e. it tests nothing | selftest case `merge-first-parent` still passes (`receipts/selftest-after.out`) |
| H5 | `.ufo/waves/round-46/tools/check-fragment.py:55-56,70,72` | `ids` list; three `x.split("\t")` per row → one | duplicated parse of the same row; `ids` is the key order of `verdict` | `check-fragment.py` output byte-identical on a 2-row fragment (`receipts/cf-{before,after}.out`, `cmp` silent) |

Diffstat: `2 files changed, 20 insertions(+), 24 deletions(-)` (`tools/append-only-audit.py` 325 → 319 lines;
`check-fragment.py` 83 → 85 lines — the comprehension becomes a loop, a wash traded for one split per row).

**Not deleted on purpose.** `--json`, `--to`, `--selftest`, `--threshold` are contract or seat surface:
`round46-append-audit-check.py:222,223,233` run `--repo R --to REV --json` and `:146` parses the `events` key,
and seat `L2Lowthr` runs `--threshold 1 --json` (`w1/build_spec.py:96`). `Repo.blobs`'s empty-input guard
(`tools/append-only-audit.py:62`) is load-bearing for an event at tip (`later` is `[]`).

## Findings (reported, not fixed)

**F1 — doc coupling of H2/H3.** `.ufo/waves/round-46/w1/out/S9Skill/skill.md:15` (proposed SKILL.md
instrument row) documents `[--files <a,b,...>]` and `[--scratch <dir>]`. If `simplify.diff` lands, that cell
must read:

```
| Round-46 append-only self-description audit (claim C2 capability) | tool + selftest: `python3 tools/append-only-audit.py --repo <dir> [--to <rev>] [--threshold <n>] [--json]`; `python3 tools/append-only-audit.py --selftest` | … (rest unchanged) |
```

No tracked lane doc mentions either flag (`grep -- "--files\|--scratch" SKILL.md SCORECARD.md LOG.md corpus/…`
→ only `LOG.md:1894`, an unrelated round-43 `prereg-time-check` note).

**F2 — `no-deletion` tests nothing distinct (retained).** `git log` line counts aside, I traced executed
lines per selftest case (`receipts/trace.json`, `trace-pairs.txt`): `no-deletion` and `below-threshold`
differ **only** in their own fixture lines (`[('t_none',184)…189]` vs `[('t_below',192)…197]`); every line of
`audit`/`Repo`/`_git` they execute is the same, and both assert `events == [] and exit_code == 0`. Because
`no-deletion` is expressible only by an absurd mutant ("event iff zero deletions"), it adds no mutant kill.
**Retained** because two sibling deliverables quote the count: `w1/out/S2Events/section.md:114` and
`w1/out/S2Cap/receipt/06-appendonly-selftest.out:11` both say `AOA_SELFTEST pass=10 fail=0`, and the frozen
counter only requires `n >= 6` — dropping the case would make those rows stale for no measured gain.
`optional-drop-no-deletion.diff` is supplied for whoever lands it together with those two rows: measured
`AOA_SELFTEST pass=9 fail=0` (`receipts/selftest-optional.out`) with every `--json` output byte-identical
(`opt-lane.json`, `opt-thr.json`).

**F3 — defect: `check-fragment.py` exits 0 on an invalid row.** `.ufo/waves/round-46/tools/check-fragment.py:78`
returns `0` unconditionally after printing detail lines. Measured on a fragment whose `release` cell is still
`b11889`:

```
$ python3 …/check-fragment.py frag-badrow.tsv cf-bad
detail: S001 invalid: release cell
exit=0        # receipts/cf-invalid-exit0.out
```

A seat that checks `$?` sees success on a rejected row. Proposed fix (5 lines, keeps the documented output):

```python
        bad_row = 0
        for i in verdict:
            hits = [x for x in lines if x.startswith(f"detail: {i} ")]
            print("\n".join(hits) if hits else f"VALID {i} {verdict[i]}")
            bad_row += bool(hits)
        …
        return 1 if bad_row else 0
```

Note the counter itself cannot supply this: a partial fragment always makes it report `met=False` (91-row
population), so its exit code is 1 either way — the helper is the only place the signal can be produced.

**F4 — caveat of H3.** With `--scratch` gone, `tempfile.gettempdir()` falls back to `/tmp` when `TMPDIR` is
unset or unwritable (measured: `TMPDIR=/nonexistent-audit-root … --selftest` → exit 0, fixtures created in
`/tmp`). Fixtures are still removed on exit; seats that follow the operator directive (export `TMPDIR` into
scratch) are unaffected. This is stdlib behaviour, not a tool path.

## Preservation evidence (all commands from `/fast/scratch/hyaku/kama-r46/Simp2Tool`)

1. `git clone -q --shared <lane> clone && git -C clone checkout --detach 96d32918…`;
   `git -C clone rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r46/Simp2Tool/clone`;
   `git apply --check -p1 simplify.diff` → OK; `git apply -p1` → OK; committed only in the clone
   (`-c user.name=sim2tool-fixture …`, tip `d832e6cd80ae2b9755f8a7b11b0301dbfb34b7e2`).
2. `python3 base-aoa.py --selftest --scratch "$S"` → `AOA_SELFTEST pass=10 fail=0` (exit 0);
   `python3 clone/tools/append-only-audit.py --selftest` → `pass=10 fail=0` (exit 0). Per-case lines identical.
3. Lane runs (read-only, `--repo <lane>`):
   `--to 0163fea2 --json` (exit 1), `--to 0163fea2` text (exit 1), `--to 4a2a4d55 --json` (exit 1),
   `--to 4a2a4d55 --threshold 1 --json` (exit 1) — before vs after: `cmp` silent on all four
   (`JSON/TEXT/TIP/THRESHOLD-IDENTICAL`).
4. `check-fragment.py` on `frag-holds.tsv` (S001 holds, S015 unchanged-file, corrected to `release=b11906`):
   before and after both print `VALID S001 holds` / `VALID S015 unchanged-file`, exit 0, `cmp` silent.
5. Frozen C2 counter, unpatched control vs patched clone — same legs, same events:
   ```
   $ python3 tools/round46-append-audit-check.py --repo <lane>       --tip 96d32918…  # control
   $ python3 tools/round46-append-audit-check.py --repo <patched clone> --tip d832e6cd…
   selftest=1 fixture=1 lane=1 table=0 lane_events=5 lane_unrestored=0 lane_partial=2 met=False
   ```
   (`table=0` is the not-yet-landed SCORECARD row, item S2Cap — identical in both receipts:
   `receipts/c2-base.out`, `receipts/c2-new.out`.)
6. Timing: no claim. 3 runs each at `4a2a4d55`: before 0.735/0.741/0.747 s, after 0.740/0.748/0.751 s —
   H1 removes a process spawn, not measurable time at 293 commits.

## Tradeoff

H2/H3 remove a documented-but-uncalled interface; the only cost is the one-line SKILL.md row update in F1
(and, for H3, the `/tmp` fallback caveat in F4). Nothing else measured changes: selftest, lane events at
three revisions, the two-row C1 fragment, and the frozen C2 counter's four legs are identical.

## Boundaries respected

Lane files, `git`/`jj` state, counters, preregistration, controls and the fleet repo untouched; the only
fixture commits were made inside `/fast/scratch/hyaku/kama-r46/Simp2Tool/clone` after asserting its
toplevel. Scratch removed at the end; every receipt cited here was copied into this directory first.
