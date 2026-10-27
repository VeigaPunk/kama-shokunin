KILLED: 11/18 C2 counter mutants; 7 survived the bounded trees (coverage findings), 0 equivalent.

## Method and controls

Read the counter contract/docstring and copied `tools/round52-append-restore-check.py` to the assigned scratch. Pristine SHA-256 before and after the campaign: `29dfd886d858f24d7cbd7a62d829c35545fc39294fe7923c59eae1ecc30853ea`; it matched the lane source both times. All mutations were isolated copies; the lane was not modified. One shared clone was rooted at `/fast/scratch/hyaku/kama-r52/M4Ctr/lane` and verified with `git rev-parse --show-toplevel` before fixture commits.

Detector command (repeated once for each pristine/mutant/restored copy and tip):

```sh
python3 <counter-copy.py> --repo /fast/scratch/hyaku/kama-r52/M4Ctr/lane --tip <full-tip> --scratch <unique-run-dir>
```

Pristine baseline: build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` → exit 0, `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`; J8LeaveRows control `6529905d552c739e8c83b5d5bd72eca0c710a966` → exit 1, `fixture=1 lane=0 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=165 met=False`; J10DropContractRow control `ceb90a0f6fa90b7798e6bca3aa587322ec3511c8` → exit 1, `fixture=1 lane=0 scenarios=8/8 corr_lost=0 row_lost=7 disclosed=10 met=False`. J8 restored the 155 removed ledger rows; J10 removed the base `registry/report-landing-errata.tsv` contract row. Both controls were committed only in the verified scratch clone with fixture identity.

After mutation runs, pristine bytes were rerun against all three tips. Outputs and exits exactly matched the baseline above; pristine hash remained identical. The actual full stdout for all 54 mutant×tip runs, all six pristine runs, and the 18 mutant source copies are preserved under `.../out/M4Ctr/`. Every mutant run had the same eight internal scenarios unless otherwise reported.

## Mutants and observed verdicts

“Killed” means at least one output/exit differs from pristine on the same tree; the direction and witness are shown. “Survived” means the three tested tips matched pristine; each includes a distinguishing scenario not exercised by these trees.

| Mutant | Defect introduced (counter source line) | Result / witness |
|---|---|---|
| M01 | Require >=4 backticks in `OPEN` rather than >=3 (97) | **Survived.** Killing scenario: a triple-backtick fence in a region-restricted parent blob containing a `## ` line; broken open recognition would change the section assigned to subsequent deletions. |
| M02 | Remove the backtick-info-string prohibition in `sections()` (170) | **Survived.** Killing scenario: in a region-restricted parent blob, a backtick fence opener whose info string itself contains a backtick, followed by a heading/deletion; the mutant falsely opens a fence. |
| M03 | Require closing fence length >= opener length + 1 (164) | **Survived.** Killing scenario: an opener and closer of equal length in a region-restricted parent blob, with a section heading/deletion after the closer. |
| M04 | Match `# ` instead of `## ` as section marker (174) | **Killed on build:** exit 1, fixture 0 (6/8), `corr_lost=116`; across controls likewise failed. |
| M05 | Treat the exempt title list as one title rather than splitting on `|` (186) | **Killed on build:** exit 1, fixture 0 (7/8), `corr_lost=116`; exempt-inside scenario failed. |
| M06 | Parse `Only` instead of `only` in `region_of` (187) | **Killed on build:** exit 2; output `could-not-evaluate: region 'only=## Errata@NOTES.md:4' unreadable`. |
| M07 | Invert exempt grading condition, `s not in arg` → `s in arg` (240) | **Killed on build:** exit 1, fixture 0 (6/8), `corr_lost=116`; exempt fixtures failed. |
| M08 | Use substring containment instead of `startswith` for `only=` (242) | **Survived.** Killing scenario: an only-prefix `## Round24` with section title `## Appendix: Round24 notes`; containment grades it, startswith does not. Existing `## Errata`/`## Round24` fixtures do not distinguish. |
| M09 | Remove cell 10 from permitted-cell exclusions, `MUT=(7,9)` (98) | **Killed on build:** exit 1, `lane=0`, `row_lost=49` (pristine 10). |
| M10 | Match deleted A-row against new rows by cell 1 rather than id cell 0 (228) | **Killed on build:** exit 1, `lane=0`, `row_lost=50` (pristine 10). |
| M11 | Remove the `max(0, …)` floor in unheld calculation (296) | **Survived.** Killing scenario: a repeated identical line where an event deletes one occurrence but the tip has fewer copies than the parent's kept-multiset count; without the floor the counter overstates unheld. |
| M12 | Change unheld cap from `min(n, …)` to `min(n+1, …)` (296) | **Killed on build:** exit 1, `lane=0`, `corr_lost=-22`; altered counts surfaced in the lane result. |
| M13 | Compute `kept` from the tip blob instead of the parent minus event deletions (288–289) | **Killed on build:** exit 1, fixture 0 (7/8), `corr_lost=5856`; fenced verbatim re-append scenario failed. |
| M14 | Classify only `A-row` (not `A`) as a row file (472) | **Killed on build:** exit 1, `corr_lost=3`, `row_lost=7` (pristine corr loss 0). |
| M15 | Disable A/A-row ledger key/count equality check (475) | **Survived.** Killing scenario: keep lane otherwise valid but alter an A-row ledger key or count; pristine detects the mismatch, while this mutant skips the comparison. J8 was caught independently by A-corr disclosures. |
| M16 | Disable the base-contract-row presence check (455) | **Survived.** J10 was not isolating: the tool itself exited 1 and its remaining ledger row was undeclared, so the mutant still failed. Killing scenario: narrow/drop a base contract row for a file with no relevant deletion events or ledger entries, leaving the tool and other legs passing; only the base-contract check then distinguishes. |
| M17 | Set `NSCEN=9` instead of 8 (102) | **Killed on build:** exit 1, `fixture=0`, `scenarios=8/9`, while `lane=1`. |
| M18 | Change final `fl and ll` to `fl or ll` (529) | **Killed by controls:** J8 and J10 both returned exit 0, `met=True` although pristine returned exit 1, `met=False`. |

## Evidence inventory and cleanup

Full outputs: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/M4Ctr/receipts/` (60 files: 18×3 mutant runs, 3 pristine baselines, 3 restored runs). Mutant source copies: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/M4Ctr/mutants/` (18 files); mutant hashes: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/M4Ctr/mutant-hashes.txt`. Pristine source hash evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/M4Ctr/pristine-hashes.txt` was not created; the matching hash is recorded above and in the original counter/source hash check before cleanup. Scratch `/fast/scratch/hyaku/kama-r52/M4Ctr` was removed after preserving evidence. No service was started.
