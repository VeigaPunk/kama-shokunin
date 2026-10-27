# J8LeaveRows — C2 ablation: A-corr disclosure rows left in place, restored lines kept

**Verdict: PASS — the frozen C2 counter catches the ablation at both the build tip (5dacf2c7) and the current lane tip (34d82600): `fixture=1 lane=0 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=165 met=False` (counter exit 1), through two independent detectors — the tool's v6 over-count rule (`bad_disclosures=155`, tool exit 1) and the counter's own A-corr-ledger rule (45 flagged `(commit, file)` pairs that hold 155 rows)**

## 1. What was ablated and why it is the right ablation

The build's C2 claim rests on two separable legs: (a) the 155 deleted A-corr lines are re-appended verbatim, so `corr_lost=0`; (b) their ledger rows are removed, so the ledger names only the 10 A/A-row lines a verbatim re-append cannot repair. The frozen base control isolates (a) alone: `controls/base.c2.out` → `corr_lost=151 row_lost=10 disclosed=165 met=False`, and its tool exits **0** (`lane: tool v6 threshold 1 exit 0 … disclosed_lines 165`), i.e. every one of the 165 rows is a *valid* disclosure at base. This seat's ablation is the mirror image: rows left, lines kept. If the counter still met at that state, leg (b) would be unmeasured.

Ablation rows: `git show 9ff76b1f:registry/append-only-disclosures.tsv` at the build has 165 rows; the build ledger (`registry/append-only-disclosures.tsv` at 5dacf2c7) has 10 (7 `corpus/SOURCES.md` A-row rows + 3 `registry/report-landing-errata.tsv` A rows, byte-identical to their base rows — checked per file with `diff`). Restoring the base blob therefore adds exactly the **155** A-corr rows and leaves the 10 keepers untouched.

Row inventory of the 155 (from `corrrows.tsv`, shipped): 45 distinct `(commit, file)` pairs over 18 files — SCORECARD.md 23, LOG.md 22, corpus/README.md 20, lessons/round-26 17, round-27 13, round-38 11, round-16 11, round-25 10, round-28 6, round-19 6, round-42 4, round-18 4, round-1 2, corpus/QUALITY.md 2, round-43 1, round-40 1, round-4-recensus 1, round-32-verifier-spotcheck 1; by class 149 `in-place-edit`, 5 `revert`, 1 `removal`.

## 2. Fixtures (all in my own `git clone --shared`; `git rev-parse --show-toplevel` asserted = `/fast/scratch/hyaku/kama-r52/J8LeaveRows/lane` before every commit; commits made with `-c user.name=fx -c user.email=fx@invalid -c commit.gpgsign=false`)

Every arm changes exactly one file, `registry/append-only-disclosures.tsv`, and leaves the 18 `## Restored lines (round 52)` blocks in place.

| arm | parent | commit | change | `git show --stat` |
|---|---|---|---|---|
| A (primary) | `5dacf2c7` build | `aea1a3d3edb4fd1ad5febaaae1a288fefa4ef237` | base 165-row ledger restored | 1 file, **155 insertions** |
| B (per-event) | `5dacf2c7` build | `b5afb9554e8fc7ec2c51dcb7f3b0b5993c8c8c3e` | the 5 rows of one A-corr event (`fd48f9a3`, LOG.md) | 1 file, **5 insertions** |
| C (current tip) | `34d82600` lane tip | `8a6ce2a6c437880f2db08a20bd8c97a6b3bfe4bf` | base 165-row ledger restored | 1 file, **155 insertions** |

Patches: `ablation-A-build.patch`, `ablation-B-oneevent.patch`, `ablation-C-tip.patch`.

No-op checks per arm tip: `git -C $S/lane status --porcelain` empty; tree diff vs parent is the one ledger file only; arm A/C ledger is byte-identical to the base blob (`git show aea1a3d3:registry/append-only-disclosures.tsv | diff - base.tsv` → empty); the 18 restoration blocks still exist at each tip (`grep -cE '^#{2,3} Restored lines \(round 52\)'` → 18 files, 1 block each; SCORECARD.md uses `###`, the other 17 `##`).

## 3. Counter runs (frozen counter, never edited; `python3 …/tools/round52-append-restore-check.py --repo $S/lane --tip <sha> --scratch $S --out <receipt>`)

| run | tip | headline | exit | receipt |
|---|---|---|---|---|
| baseline @ build | 5dacf2c7 | `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True` | 0 | `build-c2.out` |
| baseline @ lane tip | 34d82600 | `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True` | 0 | `tip-c2.out` |
| **arm A** | aea1a3d3 | `fixture=1 lane=0 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=165 met=False` | **1** | `ablate-c2.out` |
| arm B | b5afb955 | `fixture=1 lane=0 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=15 met=False` | **1** | `ablate-one-c2.out` |
| **arm C** | 8a6ce2a6 | `fixture=1 lane=0 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=165 met=False` | **1** | `armc-c2.out` |

Reproduction check: `build-c2.out` is line-identical to the L1's battery receipt `.ufo/waves/round-52/measured/c2-build.out` (`diff <(tail -n +2 measured/c2-build.out) build-c2.out` → only the seat's own trailing `exit=0` line is extra). The fixture leg is 8/8 in every run above, including the failing ones — the ablation moves the lane leg only, so the failure cannot be blamed on a fixture regression.

Failure details (arms A and C, identical apart from the tip): 
```
lane: tool definition v6 threshold 1 exit 1 {'unrestored': 0, 'partial': 0, 'regressed': 0, 'bad_disclosures': 155, 'bad_declarations': 0}
lane: ledger discloses c6199a254244 corpus/README.md, an A-corr file (restore by append)
… (45 such lines, one per (commit, file) pair)
lane: tool v6 threshold 1 exit 1 events 109 disclosed_lines 10; own graded 5868; own unheld A-corr 0, A/A-row 10; ledger lines 165
```
`grep -c "an A-corr file" armc-c2.out` → **45** (= the 45 `(c,f)` pairs holding the 155 rows; the counter dedupes its detail per pair, the mass is carried by `disclosed=165` and the tool's `bad_disclosures=155`).

## 4. The tool's over-count rule, run directly at arm A

`python3 tools/append-only-audit.py --repo $S/lane --to aea1a3d3… --json` → **exit 1**; summary `{unrestored:0, partial:0, regressed:0, bad_disclosures:155, bad_declarations:0, disclosed_lines:10, events:109}`; all 155 bad rows carry the same reason, the over-count rule at `tools/append-only-audit.py:703-704`:

> `count 1 > unheld graded lines 0 with that key`

Full JSON `tool-ablate.json`, digest `tool-ablate-summary.txt`. Because every row is flagged for over-count (the line it discloses is held at tip), the classes are not the trigger (149 in-place-edit / 5 revert / 1 removal would each be "ok" at the base state, as `controls/base.c2.out` shows with the tool exiting 0). This is exactly the property the counter relies on: a disclosure of a line that is now held is a defect, not a bookkeeping row.

## 5. Two independent detectors (code evidence, not narration)

- Tool leg: `tools/append-only-audit.py:703-704` sets `dverdict` on `cnt > unheld[hsh]`; `:736` counts it into `bad_disclosures`; `:776` makes it exit 1. Observed: exit 1, `bad_disclosures=155`.
- Counter's own leg: `tools/round52-append-restore-check.py:483-484` — `if led.get((c, f)): … "an A-corr file (restore by append)"` — fires per row-bearing `(c,f)` pair **independently of the tool JSON**; and `:443` puts `bad_disclosures: 0` into the required summary, `:488` rejects a row naming a non-event, `:529/:538` make `met` decide the exit code. Observed: 45 counter-authored lines even though the counter's own recomputation found `corr_lost=0`.

Cross-arm contrast that shows both legs are load-bearing and separable:

| state | `corr_lost` | tool exit / bad_disclosures | counter |
|---|---|---|---|
| base control (`controls/base.c2.out`) | 151 | 0 / (none reported; 165 rows all valid) | met=False |
| build / current tip | 0 | 0 / 0 | met=True |
| arm A/C (rows left, lines kept) | **0** | **1 / 155** | met=False |

So C2 is not met-at-build merely because `corr_lost` is 0; the ledger leg is measured, and removing it is detected at both the build tip and the current tip. The current-tip arm C also settles whether the w1-spec commit changes the picture: `git diff --name-only 5dacf2c7 34d82600 | grep -v '^\.ufo/'` is empty, and arm C reproduces arm A result-for-result.

## 6. Findings / risks

- No defect found in the frozen counter or in the tool. Defect-shaped observations, not defects: (i) the counter's A-corr detail is deduped per `(commit, file)`, so 155 offending rows print as 45 lines and the row mass appears only in `disclosed=<n>` and the tool summary — the verdict is unaffected; (ii) the tool's `disclosed_lines` drops from 165 (base) to 10 (arm A) once the rows are over-counted, which is the intended reading.
- Preregistered limit visible in this state: the A-corr ledger rule is unconditional for a declared A-corr file, so a future "disclose a genuinely unrepaired A-corr loss" state cannot exist without failing C2 — consistent with the contract (`restore by append`), recorded here as the intended shape, not as a limitation to fix.
- Arm B shows the same detector at per-event scale (one commit's 5 LOG.md rows → tool `bad_disclosures=5`, counter `disclosed=15`, one A-corr pair line), so the rule is not a bulk-only threshold effect.
- No blocker. Nothing was installed (no pacman, no uv/npx installs), no llama-server was started or left behind (`pgrep -af llama-server` clean after the runs; C2 starts none), lane and fleet repos untouched, frozen counters/preregistration unmodified.

## 7. Cleanup

`/fast/scratch/hyaku/kama-r52/J8LeaveRows` (clone + receipts source) removed after the receipts were copied here; every cited receipt lives in this directory with `SHA256SUMS.txt`.

Files in this directory: `J8LeaveRows.md`, `ablate-c2.out`, `armc-c2.out`, `ablate-one-c2.out`, `build-c2.out`, `tip-c2.out`, `tool-ablate.json`, `tool-ablate-summary.txt`, `corrrows.tsv`, `ablation-A-build.patch`, `ablation-B-oneevent.patch`, `ablation-C-tip.patch`, `SHA256SUMS.txt`.
