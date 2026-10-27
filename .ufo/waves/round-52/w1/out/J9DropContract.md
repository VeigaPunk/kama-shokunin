# J9DropContract — C2 ablation control: contract row dropped / narrowed (round 52, lane kama)

**Verdict: the control holds.** The frozen C2 counter returns `met=False` (`fixture=1 lane=0`) on every ablation I built — the `corpus/lessons/*.md` row deleted (A0, A1), the `LOG.md` region narrowed to `only=## X@LOG.md:16` (A2), and both edits together (A3) — always through its base-contract leg (`tools/round52-append-restore-check.py:453-456`), while the untouched build `5dacf2c7` measures `met=True` on a fresh clone. The tip's append-only tool alone does **not** see the row deletion (exit 0), so the counter's base-contract comparison is the only detector of the un-declaration. No defect found in the frozen instruments; no proposed fix.

## Fixture (my own `git clone --shared`)

Scratch: `/fast/scratch/hyaku/kama-r52/J9DropContract` (`TMPDIR` set there). One live clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; toplevel asserted `= /fast/scratch/hyaku/kama-r52/J9DropContract/lane` before the first commit. Detached at the build, then four fixture branches, each committed with `-c user.name=fixture -c user.email=fixture@invalid -c commit.gpgsign=false`:

| id | commit | edit vs `5dacf2c7` | numstat |
|---|---|---|---|
| A0 | `030449e004af28e3c0818f6dca96ce260b4e9bf2` | delete contract row `corpus/lessons/*.md` only | +0 −1 |
| A1 | `985006d3c87fc6bfb9693b7b4aa76a2772db30d6` | same row deleted **and** the 14 `corpus/lessons/*.md` `## Restored lines (round 52)` blocks reverted (block heading → EOF) | +0 −257 |
| A2 | `073eef96e0d5b03a789e5d21f648fb0209e226d0` | `LOG.md` region cell `*` → `only=## X@LOG.md:16` (1 line) | +1 −1 |
| A3 | `233c53767458ea464de6bf33c25244321257f86a` | A1 + A2 in one commit | +1 −258 |
| ref | `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` | build, untouched | — |

`git diff --numstat 5dacf2c7 985006d3` → `added=0 deleted=257` (256 restored-block lines + 1 contract row), so A1 removes only the block content and the row; no other byte changed. `sys.exit` of the truncation script is not used — the driver asserted the single row was dropped (`len(ls)-len(keep)==1`).

Base and build carry the same two rows the ablations attack (`registry/append-only-contract.tsv`: line 2 `LOG.md … * …`, line 7 `corpus/lessons/*.md … * …`; identical in `git show 9ff76b1f:…`), so "present at tip unchanged" is exactly what A0–A3 break.

## Frozen C2 counter — results

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round52-append-restore-check.py \
  --repo $S/lane --tip <commit> --scratch $S --out <receipt>
```
Counter bytes at the lane equal the preregistration hash: `sha256sum tools/round52-append-restore-check.py` → `29dfd886d858f24d7cbd7a62d829c35545fc39294fe7923c59eae1ecc30853ea` = `preregistration.json` claims[C2].`counter_sha256`.

| tip | exit | headline | lane failure detail |
|---|---|---|---|
| `5dacf2c7` (build) | 0 | `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True` | — |
| A0 `030449e0` | 1 | `fixture=1 lane=0 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=False` | `lane: base contract row corpus/lessons/*.md A-corr * absent or changed at tip` |
| A1 `985006d3` | 1 | `fixture=1 lane=0 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=False` | same single line |
| A2 `073eef96` | 1 | `fixture=1 lane=0 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=False` | `lane: tool definition v6 threshold 1 exit 1 {... 'bad_declarations': 1}` + `lane: base contract row LOG.md A-corr * absent or changed at tip` |
| A3 `233c5376` | 1 | `fixture=1 lane=0 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=False` | both base-contract lines |

The fixture leg stayed `8/8` in every run (all eight scenario detail lines `ok`), so the controls isolate the lane leg. `corr_lost` stays 0 and `row_lost=10`/`disclosed=10` match the ledger's 10 rows, i.e. the counter's **own** recomputation is not what fails — the `--base` contract comparison at `tools/round52-append-restore-check.py:453-456` is:

```python
have = {(c[0], c[1], c[3]) for c in crow if len(c) >= 4}
for c in parse_contract(btext):
    if (c[0], c[1], c[3]) not in have:
        detail.append(f"lane: base contract row {c[0]} {c[1]} {c[3][:40]} absent or changed at tip")
```

docstring contract for that leg: `tools/round52-append-restore-check.py:55-57` ("every row of it at --base must be present at --tip with the same path, rule and region (a dropped or narrowed row fails the lane leg)").

Lane base control for comparison, `.ufo/waves/round-52/controls/base.c2.out:1-2`: `tip=9ff76b1f… / fixture=1 lane=0 scenarios=8/8 corr_lost=151 row_lost=10 disclosed=165 met=False`.

## The tip's append-only tool — the row is the audit switch

```
python3 $S/lane/tools/append-only-audit.py --repo $S/lane --to <commit> --json
```

| tip | exit | files | events | restored | unrestored | bad_declarations / bad_disclosures |
|---|---|---|---|---|---|---|
| `5dacf2c7` | 0 | 99 | 109 | 67 | 0 | 0 / 0 |
| A0 | 0 | **9** | 86 | 44 | 0 | 0 / 0 |
| A1 | 0 | **9** | 86 | 44 | 0 | 0 / 0 |
| A2 | 1 | 99 | 109 | 54 | 0 | **1** / 0 |
| A3 | 1 | 9 | 86 | 31 | 0 | **1** / 0 |

- **A0/A1: the tool exits 0.** Deleting the wildcard row removes `corpus/lessons/*.md` from the audited set (10 declarations → 9, `files` 99 → 9), so the reverted blocks become ungraded rather than unrestored. A0 and A1 summaries are byte-identical (`tool-A0.json` vs `tool-A1.json` differ only in `to`, `contract`, `disclosures_ledger`), which shows the block revert is invisible to the tool once the row is gone. Only the counter's base-contract leg catches this.
- **A2/A3: the tool catches the narrowed region independently.** `tool-A2.json` `/declarations/0` = `{"path":"LOG.md","region":"only","ok":false,"reason":"only pointer LOG.md:16 does not declare '## X' append-only"}` (`tools/append-only-audit.py:312`); `ungraded_lines` 210 → 2530, consistent with LOG.md's ~2.3k lines leaving the graded set. So the narrow is caught twice (tool *and* counter base-contract leg); the row deletion is caught once (counter only).

Instrument note (not a defect; consistent with the frozen contract): C2's "restored, not un-declared" sensitivity rests entirely on the `--base` row comparison — the counter never requires that a *tip* row exist, only that every base row survive. A lane that dropped the row would pass both `corr_lost=0` and the tool; the base-contract leg is what kills it, exactly as the docstring specifies. Second note: the leg keys on `(path, rule, region)` only, so a note-cell edit alone would pass — also as documented ("same path, rule and region").

## Evidence retained

All under `.ufo/waves/round-52/w1/out/J9DropContract/` (copied out of scratch):
`ctl-build.c2.out`, `ctl-A0.c2.out`, `ctl-A1.c2.out`, `ctl-A2.c2.out`, `ctl-A3.c2.out` (full counter receipts incl. `detail:` lines), `tool-build.json`, `tool-A0.json`, `tool-A1.json`, `tool-A2.json`, `tool-A3.json` (tool JSON), `fixture-shas.txt`, and the four control diffs `ctl-a0-drop-only.patch`, `ctl-a1-drop-revert.patch`, `ctl-a2-log-only.patch`, `ctl-a3-both.patch`.

## Housekeeping

- No pacman, no installs, no service start/stop. I started no llama-server; `pgrep -af llama-server` shows two live child processes owned by a sibling seat's scratch (`/fast/scratch/hyaku/kama-r52/R1Old/…`), left untouched — none of mine.
- The lane repo, fleet repo and shokuknow were read-only; no jj state touched. Scratch clone removed after the receipts were copied.
- Risks: none new. Carried: the counter's exempt= simplification (preregistration limit) is untouched by this control; the A1 row deletion also removes lesson lines from the *tool's* scope, so a future wave that wants the tool to notice an un-declaration would need its own base-contract check (the counter already has one).

## Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J9DropContract.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/J9DropContract/` (15 evidence files listed above)
