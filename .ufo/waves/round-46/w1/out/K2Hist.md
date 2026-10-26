# K2Hist — round 46, C2 independent recomputation (append-only-audit)

**Verdict:** the event *set* reproduces exactly (5 events at `4a2a4d55`, same statuses, same
`restored_by`, same exit 1), but the tool's `deleted` / `restored_at_tip` counts are wrong on
2 of the 5 rows — undercounted by precisely the number of **removed content lines whose text
begins with `--`** — and the C2 counter's "independent recomputation" leg passes on those same
wrong counts (`lane=1`), so for this defect class the independence the claim buys does not
exist. The defect is not cosmetic: a fixture whose commit deletes 21 lines (>= the frozen
threshold of 20), two of them `--`-prefixed, is reported as **0 events, exit 0**. On the lane's
own history the defect changes no status, no `restored_by` and not the exit code, because the
largest non-event deletion is 18 lines and the single unrestored line is untouched by it.

Axis impacted: **calibration** (C2 7 -> 7, capability acquisition). Nothing here touches C1 /
freshness.

## Method (no tool or counter source read for the recomputation)

The contract read was the module docstrings only (`tools/append-only-audit.py` lines 1–32,
`tools/round46-append-audit-check.py` lines 1–60). The recomputation is my own script,
`K2Hist/independent.py`, hunk-driven (`@@ -a,b +c,d @@` states how many `-` lines follow, so a
removed line rendered `--- ...` can never be mistaken for a file header), with git's own
`--numstat` deletion count cross-checked for every `(commit, file)` pair:

    git -C <lane> rev-list --topo-order --reverse 4a2a4d55...   # 294 commits
    for each c (skip root): git diff --no-renames -U0 <c>^1 <c> -- <5 files>
    git diff --no-renames --numstat <c>^1 <c> -- <5 files>      # independent count

- 294 commits, 5 declared files, threshold 20: **5 events**, `restored=3 partial=2 unrestored=0`.
- Patch-parser count vs `--numstat` deletion count: **0 disagreements over all 294 x 5 pairs**
  (`independent.py` -> `count_mismatches: []` in `mine-4a2a4d55.json`).
- Same recomputation at the preregistration base `0163fea2` (292 commits): same 5 events.
- `tools/append-only-audit.py` is absent at `0163fea2` (`git cat-file -e ...0163fea2:tools/
  append-only-audit.py` -> exit 128) and byte-identical at `4a2a4d55` and `96d32918`
  (sha256 `793dab9ffe0c41c7a5427324fd6f8bf0c3b40b0f9083d417e38d5e5792a7227f`).

## Recomputation vs the tool at `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`

| commit | file | git `--numstat` deleted | my `deleted` | tool `deleted` | my `restored_at_tip` | tool | status | restored_by |
|---|---|---|---|---|---|---|---|---|
| `dd9f5dc6` | SCORECARD.md | 31 | 31 | 31 | 24 | 24 | partial | — |
| `0718b6ab` | SCORECARD.md | **2421** | **2421** | **2417** | **2420** | **2416** | partial | — |
| `0718b6ab` | LOG.md | **2292** | **2292** | **2290** | **2292** | **2290** | restored | `82b5e9d3` |
| `0718b6ab` | corpus/QUALITY.md | 375 | 375 | 375 | 375 | 375 | restored | `82b5e9d3` |
| `0718b6ab` | corpus/README.md | 663 | 663 | 663 | 663 | 663 | restored | `82b5e9d3` |

`numstat-vs-tool.out`: `rows_mismatched=2 of 5`, `delta=4` (SCORECARD) and `delta=2` (LOG).
Exit codes: tool 1, my recomputation-equivalent exit 1 (2 partial). `corpus/SOURCES.md` has no
event at this revision. The one unrestored SCORECARD line is a normal table row
(`| depth | **7** | \`SKILL.md\` sha256 ... (1420 lines); run`), i.e. the honest round-45
truncation residue; both implementations find exactly that one line missing at tip.

## D1 — defect: `tools/append-only-audit.py:102` drops removed lines that start with `--`

    tools/append-only-audit.py:102
        dele = [x[1:] for x in d.split("\n") if x.startswith("-") and not x.startswith("---")]

The filter excludes every raw diff line starting with `---`, not only the file header
`--- a/<path>` / `--- /dev/null`. A removed content line whose text starts with `--` is
rendered `---<text>` and is therefore silently dropped from `dele`; `restored_at_tip` is then
computed over the reduced list, so both numbers move together. On this history the dropped
texts are exactly the six argparse-style lines in the round-45 truncation:

    --out .ufo/waves/round-20/runs/0957ce61` ran **21 commands**, all declared   (x4 in SCORECARD.md)
    --tip <full-commit>` reads `listed 3 observed 6 missing 3 ...                 (LOG.md)
    --rev <full-commit>` reads `registered 10 unregistered 2 defective 0` ...      (LOG.md)

Only one commit in the whole 294-commit history contains such lines (`0718b6ab`), which is why
the defect is invisible everywhere else.

Behavioural proof, deterministic fixtures (`probes.py`, own repos, `git rev-parse
--show-toplevel` asserted before the first commit):

    probes.out
    A numstat_deleted=27  tool_exit=1 tool_events=[(26, 'unrestored')]   # 1 '--' line dropped
    B numstat_deleted=39  tool_exit=1 tool_events=[(36, 'unrestored')]   # '--x', '-- y', '--- z' dropped; '++ w' kept
    C numstat_deleted=21  tool_exit=0 tool_events=[]                     # FALSE NEGATIVE

Case B fixes the rule precisely: it is a raw-prefix test on `---`, so `--x` (`---x`), `-- y`
(`--- y`) and `--- z` (`---- z`) are all lost while `++ w` (`-++ w`) survives. Case C is the
worst consequence: 21 git-deleted lines is an event by the frozen threshold, the tool reports
none and **exits 0**. (The earlier lane-shape probe: 25 deleted -> 23, both `--` lines gone.)

Blast radius on the lane, checked rather than assumed:

- near-threshold census at `4a2a4d55` (true deleted in 15..26 per `(commit, file)`): the only
  non-events are 18-line deletions (`83bee7fa`, `ef76777e`, SCORECARD.md); nothing sits in the
  20..23 window where the undercount could hide an event. So the 5-event set and the exit code
  are correct *today* — the false-negative class is latent, not active.
- the two dropped-and-restored rows keep their status (`restored` / `partial`) and their
  `restored_by`; the single unrestored line is not one of the dropped texts.

**Proposed fix** — `K2Hist/proposed-fix.diff` (32 lines, `patch -p1` applies cleanly to a
pristine copy: `PATCH_APPLIED`): count deletions only inside hunks, and reword the docstring
line 15 so the contract no longer invites the bug.

    -            dele = [x[1:] for x in d.split("\n") if x.startswith("-") and not x.startswith("---")]
    +            dele = []
    +            in_hunk = False
    +            for x in d.split("\n"):
    +                if x.startswith("@@"):
    +                    in_hunk = True
    +                elif in_hunk and x.startswith("-"):
    +                    dele.append(x[1:])

and the docstring: "`-` lines inside the hunks of that diff; the file header lines that precede
the first `@@` (`--- a/<path>`, `--- /dev/null`) are not deletions, but a removed content line
whose text starts with `--` (rendered `--- ...`) is".

Validated, not asserted: the patched copy on the lane at `4a2a4d55` prints
`summary {commits 294, events 5, restored 3, partial 2, unrestored 0}` with
`SCORECARD 2421 / 2420` and `LOG 2292 / 2292` — identical to my independent numbers — and still
exits 1 (`fixed-tool-4a2a4d55.json`). Its `--selftest` stays `AOA_SELFTEST pass=10 fail=0`,
because **the shipped selftest cannot see the bug either**: its content generator is
`lines(tag, n) = [f"{tag} line {i} {os.urandom(4).hex()}"]` (`tools/append-only-audit.py:167`)
and never produces a line starting with `--`. Add one selftest case whose deleted line text
starts with `--` (and one starting with `---`, which renders `----`).

## D2 — defect: the C2 counter's `lane` leg is not independent for this class

`python3 tools/round46-append-audit-check.py --repo <lane> --tip 4a2a4d55... ` (`counter-4a2a4d55.out`):

    selftest=1 fixture=1 lane=1 table=0 lane_events=5 lane_unrestored=0 lane_partial=2 met=False
    event: 0718b6abbda6 SCORECARD.md deleted=2417 restored_at_tip=2416 status=partial
    event: 0718b6abbda6 LOG.md deleted=2290 restored_at_tip=2290 status=restored

`lane=1` is only reachable if the counter's own recomputation yields `deleted=2417` / `2290`
for those rows, because the frozen lane leg requires "equal sets of (commit, file, deleted,
restored_at_tip, status, restored_by)". Git's own count is 2421 / 2292. So either the counter's
recomputation shares the `startswith("---")` rule, or the lane leg does not compare the count
fields — both are defects against the frozen leg (the preregistration's "matches an independent
recomputation on ... the lane's own history"). Its fixture leg cannot catch either: its fixture
content is random (`--scratch`-built repo, "random line content (os.urandom)" per its own
docstring), so a line beginning `--` has probability ~2^-16 per line — the class is
unreachable by construction, and `fixture=1` is not evidence of parser agreement.

Smallest safe correction for the counter (frozen file — a finding, not an edit): build the
fixture's deleted lines to include at least one whose text starts with `--` and one with
`---`, and keep its count comparison source-independent (e.g. compare `deleted` against
`git diff --numstat`), then re-run at the integration tip.

## D3 — state at the audited revision: `table=0` (not a defect of the tool)

At `4a2a4d55` the counter reads `table=0 met=False`, exit 1: SCORECARD.md has no `|`
capability-table line naming `append-only-audit` — at `4a2a4d55` **and at the current lane tip
`96d32918`** (`git show <rev>:SCORECARD.md | grep -n append-only` finds only unrelated rows at
lines 14/26/271/808/1068/1589). C2's frozen predicate requires `table=1`, so C2 cannot be
reported met from this revision; the row must be appended in the integration commit and the
counter re-run at the measured tip. Per the frozen kill rule, `met=False` at the measured
commit is an honest stop — it must not be narrowed after data.

## D4 — the counts quoted in the claim text are the tool's, not git's

"0718b6ab SCORECARD partial (2416/2417)" and "LOG 2290" are the undercounted figures. Honest
numbers: SCORECARD **2420/2421**, LOG **2292/2292**, dd9f5dc6 SCORECARD 24/31 (this row is
unaffected). The event set, statuses, `restored_by` and exit 1 are unchanged, so C2's boolean
does not flip on this history — but any report that prints 2416/2417 as "deleted lines of that
commit" is wrong by 4, and the detector it certifies would miss a 20–22-line deletion that
contains `--`-prefixed lines (case C).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K2Hist.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/K2Hist/independent.py`
- `.../w1/out/K2Hist/mine-4a2a4d55.json`, `mine-0163fea2.json`
- `.../w1/out/K2Hist/tool-4a2a4d55.json`, `fixed-tool-4a2a4d55.json`
- `.../w1/out/K2Hist/numstat-vs-tool.py`, `numstat-vs-tool.out`
- `.../w1/out/K2Hist/probes.py`, `probes.out`, `probe-fx3-false-negative.out`, `probe-fx3-threshold-23.out`
- `.../w1/out/K2Hist/counter-4a2a4d55.out`, `sha256.out`
- `.../w1/out/K2Hist/proposed-fix.diff`

Tooling: none installed or upgraded. Scratch `/fast/scratch/hyaku/kama-r46/K2Hist` removed
after the receipts were copied; no lane file, no fleet file and no git/jj state was modified
(read-only `git show`/`diff`/`rev-list` only; fixtures were throwaway repos under my scratch).
