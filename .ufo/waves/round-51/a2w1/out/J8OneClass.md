# J8OneClass — round 51, lane kama, C2 (calibration) ablation control

**Verdict: the frozen C2 counter rejects all three malformed ledgers and the unmodified lane commit measures met=True in the same clone — `lane=0` for every ablation, `fixture=1 scenarios=9/9` throughout — so the calibration claim's ledger legs are doing work, with one measured boundary: a dropped disclosure row in a region-restricted file (`SCORECARD.md`) is caught only by the tool's own gate, not by the counter's independent key-by-key recomputation.**

## Axes (godspeed)

| axis | move | kept? |
|---|---|---|
| calibration | does the frozen counter's `lane` leg go to 0 for each single-mechanism ledger corruption the preregistration names (v1), plus two it does not name (v2, v3)? | yes — all three lane=0, met=False |
| calibration | are the counter's two detection channels (tool gate vs counter's own recomputation) actually independent? | partly — v2/v3 prove independence on whole-file files; probe p1 measures the region-restricted blind spot |
| operability | no process, network or lane mutation introduced | yes — no llama-server started, scratch clone only |

## Setup

Scratch `S=/fast/scratch/hyaku/kama-r51/J8OneClass`; one clone `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; toplevel asserted (`git -C $S/lane rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r51/J8OneClass/lane`); branch `r51j8` cut at the lane commit `138af25b963450b6520794995605fa7dbbcd87e0`; every variant commit made with `-c user.name=fx -c user.email=fx@invalid -c commit.gpgsign=false` inside that clone only. The lane itself was never written: the only lane reads were `git show 138af25b:registry/append-only-disclosures.tsv` and the counter/tool bytes.

Baseline ledger copied: `.ufo/waves/round-51/a2w1/out/J8OneClass/baseline-ledger-138af25b.tsv` (166 data rows, sha256 `17d2b067ad7272976bda88fac9d8cbc0b77d2d93d2f2a376b3b0a5171d2803bb`; classes 160 `in-place-edit`, 5 `revert`, 1 `removal` — exactly the six rows the seat names).

Build receipt transfer checked: `git -C $S/lane diff --stat 73bf2a7a17104a62a3e442912c8776cbd8dedbd5 138af25b963450b6520794995605fa7dbbcd87e0 -- registry/append-only-disclosures.tsv tools/append-only-audit.py registry/append-only-contract.tsv` printed nothing (exit 0) — the C2 paths are byte-identical between the met=True build receipt tip and the lane commit, so the build's `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True` transfers to `138af25b`.

Anchor run (unmodified tip, same clone, same counter bytes):

```
$ python3 tools/round51-append-audit-v6-check.py --repo $S/lane --tip 138af25b963450b6520794995605fa7dbbcd87e0 --scratch $S --out .../c2-v0-baseline-138af25b.out
fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True          (exit 0)
detail: lane: tool v6 threshold 1 exit 0 events 106 disclosed_lines 166 permitted_lines 58; own lost lines in whole-file-graded files 142; ledger lines 166
```

## Results

| run | tip (clone) | ledger change vs `138af25b` | counter line | exit | tool `bad_disclosures` | tool exit |
|---|---|---|---|---|---|---|
| v0 baseline | `138af25b` | none | `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True` | 0 | — | 0 |
| v1 in-place-edit | `9cf6ae008402ced405ed1738d7410a92a76af697` | `6 insertions(+), 6 deletions(-)`; all 6 non-`in-place-edit` classes → `in-place-edit` | `fixture=1 lane=0 scenarios=9/9 lost=142 disclosed=166 met=False` | 1 | **6** | 1 |
| v2 drop-row | `3dd579699dbae10b602a078a6dd298b2deaf9b0c` | original classes, row `d183ec57 corpus/lessons/round-27.md 55cfcefa…` (`removal`) removed | `fixture=1 lane=0 scenarios=9/9 lost=142 disclosed=165 met=False` | 1 | 0 | 1 |
| v3 junk-row | `9af52b0db1f40d0689e1fcf48b6e7795cdc5a709` | original rows + 1 junk row `d183ec57 corpus/lessons/round-27.md d7fa4059…` class `removal` | `fixture=1 lane=0 scenarios=9/9 lost=142 disclosed=167 met=False` | 1 | **1** | 1 |
| p1 probe (extra) | `5b7a12a1e5f36b35eb84fdd64e58a0cd351cea56` | original classes, `SCORECARD.md` row `db6bfa8d … e3fe531f…` removed | `fixture=1 lane=0 scenarios=9/9 lost=142 disclosed=165 met=False` | 1 | 0 | 1 |

Every run: `events 106`, `permitted_lines 58`, `files 96`, counter's own `lost=142` unchanged — each variant commit touches only `registry/append-only-disclosures.tsv` (no contract file), so no event is added and the ablation is confined to the ledger's verification role. The fixture leg is 9/9 in all five runs (it builds its own ledgers, so lane-ledger corruption cannot move it — no collateral).

## Per-variant evidence (verbatim)

### v1 — every class rewritten to `in-place-edit`

```
$ python3 tools/round51-append-audit-v6-check.py --repo $S/lane --tip 9cf6ae008402ced405ed1738d7410a92a76af697 --scratch $S --out .../c2-v1-in-place-edit.out
fixture=1 lane=0 scenarios=9/9 lost=142 disclosed=166 met=False    (exit 1)
detail: lane: tool definition v6 threshold 1 exit 1 {'unrestored': 1, 'partial': 1, 'regressed': 0, 'bad_disclosures': 6, 'bad_declarations': 0}
detail: lane: ledger ed135b3cb869 LOG.md 2ee99d81fe2e class in-place-edit != own ['revert']
detail: lane: ledger ed135b3cb869 LOG.md b0a06400ef3c class in-place-edit != own ['revert']
detail: lane: ledger ed135b3cb869 LOG.md df41705d9aab class in-place-edit != own ['revert']
detail: lane: ledger ed135b3cb869 LOG.md eb379fbf0bf9 class in-place-edit != own ['revert']
detail: lane: ledger ed135b3cb869 LOG.md eee7f85d24a8 class in-place-edit != own ['revert']
detail: lane: ledger d183ec572a5e corpus/lessons/round-27.md 55cfcefa6432 class in-place-edit != own ['removal']
detail: lane: tool v6 threshold 1 exit 1 events 106 disclosed_lines 160 permitted_lines 58; own lost lines in whole-file-graded files 142; ledger lines 166
```

Tool side (`v1-tool.json`, `tool-json-summaries.txt`): `summary.bad_disclosures=6`, `unrestored=1`, `partial=1`, `disclosed_lines=160` (six rows stop counting), reasons `class in-place-edit is not ['revert']` ×5 and `… is not ['removal']` ×1 (tool `tools/append-only-audit.py:692`). The six bad rows are exactly the six non-`in-place-edit` rows the seat names; the counter also carries its own class leg (`tools/round51-append-audit-v6-check.py:346`), so this variant is rejected by **two independent** checks.

### v2 — classes kept, one row dropped

```
fixture=1 lane=0 scenarios=9/9 lost=142 disclosed=165 met=False    (exit 1)
detail: lane: tool definition v6 threshold 1 exit 1 {'unrestored': 1, 'partial': 0, 'regressed': 0, 'bad_disclosures': 0, 'bad_declarations': 0}
detail: lane: d183ec572a5e corpus/lessons/round-27.md: own lost 8 ledger 7 (1 keys differ)
detail: lane: tool v6 threshold 1 exit 1 events 106 disclosed_lines 165 permitted_lines 58; own lost lines in whole-file-graded files 142; ledger lines 165
```

Tool side: `bad_disclosures=0`, `unrestored=1`, and the event now carries the undisclosed key `55cfcefa…` (class `removal`) — the tool's exit 1 comes from `unrestored` (`tools/append-only-audit.py:762`). This is the strongest independence evidence: the counter's **own** recomputation, not the tool, reports `own lost 8 ledger 7` (`tools/round51-append-audit-v6-check.py:361`) — it rebuilds the lost-key multiset from first-parent `-U0` diffs and the tip blob and names the missing key itself.

### v3 — original rows plus one junk row (no line hashes to `d7fa4059…`)

```
fixture=1 lane=0 scenarios=9/9 lost=142 disclosed=167 met=False    (exit 1)
detail: lane: tool definition v6 threshold 1 exit 1 {'unrestored': 0, 'partial': 0, 'regressed': 0, 'bad_disclosures': 1, 'bad_declarations': 0}
detail: lane: ledger d183ec572a5e corpus/lessons/round-27.md d7fa4059f0f6 class removal != own []
detail: lane: d183ec572a5e corpus/lessons/round-27.md: own lost 8 ledger 9 (1 keys differ)
detail: lane: tool v6 threshold 1 exit 1 events 106 disclosed_lines 166 permitted_lines 58; own lost lines in whole-file-graded files 142; ledger lines 167
```

Tool reason: `count 1 > unheld graded lines 0 with that key` (`tools/append-only-audit.py:689`). Note the counter's receipt line reports `disclosed=167` while the tool's `disclosed_lines=166`: the receipt's `disclosed` is the raw ledger line sum, so it is inflated by junk rows — only `lane`/`met` decide validity. Junk is caught twice: tool gate and the counter's key comparison (`tools/round51-append-audit-v6-check.py:361-364`).

### p1 — probe: dropped row in a region-restricted file (`SCORECARD.md`, `exempt=## …`)

```
fixture=1 lane=0 scenarios=9/9 lost=142 disclosed=165 met=False    (exit 1)
detail: lane: tool definition v6 threshold 1 exit 1 {'unrestored': 1, 'partial': 0, 'regressed': 0, 'bad_disclosures': 0, 'bad_declarations': 0}
detail: lane: tool v6 threshold 1 exit 1 events 106 disclosed_lines 165 permitted_lines 58; own lost lines in whole-file-graded files 142; ledger lines 165
```

Here the counter emits **no** ledger-vs-own-recompute line: `SCORECARD.md` is not whole-file graded, so only the tool's exit code moves `lane` to 0 (`tools/round51-append-audit-v6-check.py:269`, `:368-370`). The rejection stands, but on one channel. This is the preregistration's own disclosed limit (`preregistration.json:44`) realized and measured: for `SCORECARD.md` and the two `only=## …` entries the counter cannot recompute the lost set key for key.

## Channel analysis

| variant | tool gate | counter's own recompute | verdict |
|---|---|---|---|
| v1 classes | bad_disclosures 6 (class, `append-only-audit.py:692`) | class leg (`…check.py:346`) | both |
| v2 drop (whole-file file) | unrestored/undisclosed (`tools/append-only-audit.py:718`, `:762`) | key-set equality (`…check.py:361`) | both |
| v3 junk (whole-file file) | count check (`tools/append-only-audit.py:689`) | key-set equality (`…check.py:361`) | both |
| p1 drop (region-restricted file) | unrestored (`tools/append-only-audit.py:718`, `:762`) | none | tool only |

Reading the code (not measured here): a **junk** row whose (commit, file) is a real event of a region-restricted file is caught by the counter's own per-row bound `n > dk[lh]` (`:369`), so the single-channel gap is specific to a *missing* row in a region-restricted file — the same shape as v2 but on `SCORECARD.md` / the `only=##` entries.

## Findings

1. **No defect in the frozen counter or the v6 tool.** Every ablation that claim C2 must reject is rejected (`lane=0`, `met=False`, counter exit 1), including the one the preregistration names (`controls` line: "a ledger whose every class is `in-place-edit`") and two it does not (drop-row, junk-row). The unmodified lane commit measures `met=True` in the same clone and tool bytes, so the ablations are single-mechanism.
2. **Calibration observation (not a defect, no edit proposed):** the counter's independent recomputation covers whole-file-graded files only. A dropped row in `SCORECARD.md` or a `only=## Errata` entry is still rejected, but solely through the tool's summary gate — if the tool's region logic were wrong in the same commit, the ablation p1 would pass `lane=1`. Preregistered as a limit (`preregistration.json:44`); recorded here as measured, for the lane L1's judgment on whether the round-52 counter should re-derive graded lines for region-restricted files independently of the tool.
3. **Receipt hygiene:** the counter's `disclosed=N` field is a raw ledger line sum (v1: 166 while the tool counts 160; v3: 167 vs 166). Read `lane`/`met` and the tool summary, not `disclosed`, when judging a ledger.
4. The six non-`in-place-edit` rows are exactly `5× revert` (commit `ed135b3c`, LOG.md — the round-50 R6 loss) `+ 1× removal` (commit `d183ec57`, corpus/lessons/round-27.md `55cfcefa…`); the seat's "6 rows" figure is confirmed against the blob (`awk -F'\t' 'NR>1{c[$5]++}'` → `in-place-edit 160, removal 1, revert 5`).

## Limits

- One clone, one lineage: v1/v2/v3/p1 are sequential commits on branch `r51j8` (parents `138af25b → v1 → v2 → v3 → p1`). Each measurement reads the ledger blob at its own tip only, and no variant adds an event (`events 106` throughout), so the sequencing does not enter any verdict — but the tips are not independent trees.
- `junk` used a deterministic non-line sha256 (`sha256("r51-j8-junk-line-not-in-any-blob")` = `d7fa4059f0f63e5046afbd74ef1a4f93c6bca530a2d155198b761550b4112d0e`) so the receipt is reproducible; it is random with respect to every blob line.
- No new tool installed; no pacman run; no llama-server started by this seat (the live `llama-server`/`kama-llamacpp-live.py` processes seen at `pgrep` time belong to peers `X1Fresh` (pid 978513/979061) and `R1Rerun` (pid 1031208) and were left untouched).
- Scratch `S` removed at the end (`rm -rf /fast/scratch/hyaku/kama-r51/J8OneClass`); every receipt cited above lives in this directory.

## Files written

- `.ufo/waves/round-51/a2w1/out/J8OneClass.md` — this report
- `.ufo/waves/round-51/a2w1/out/J8OneClass/ablate_ledger.py` — deterministic ledger generator (three variants, noted in its docstring)
- `…/c2-v0-baseline-138af25b.out` (+ `.stdout`), `…/c2-v1-in-place-edit.out`, `…/c2-v2-drop-row.out`, `…/c2-v3-junk-row.out`, `…/c2-p1-drop-region-row.out` (+ `.stdout` twins) — frozen-counter receipts
- `…/v1-tool.json`, `…/v2-tool.json`, `…/v3-tool.json` (+ `.stderr`) and `…/tool-json-summaries.txt` — tool-side `bad_disclosures`/`undisclosed` evidence
- `…/ledger-diff-v1.patch`, `…/ledger-diff-v2.patch`, `…/ledger-diff-v3.patch`, `…/ledger-diff-p1.patch` — ledger delta of each variant against `138af25b`
- `…/baseline-ledger-138af25b.tsv` — the unchanged ledger blob as measured
- `…/variant-tips.txt` — the four ablation tips
