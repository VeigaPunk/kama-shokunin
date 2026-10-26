# X2Lane — round 49: v3 vs v4 `append-only-audit` across lane history

**Verdict:** across 8 lane tips (438127bc~40 … 74558c71) and thresholds 1/2/5/10/20, v4 changes exactly **one** lane event's counts — `0718b6ab SCORECARD.md`, ungraded 72 → 65 (graded 2349 → 2356) — and **no event's status**: v4 never turns a lane event `partial` or `unrestored`, and v3/v4 exit codes agree in all 20 tip × contract-mode configurations.

## Method and boundary

- Tools: `tools/append-only-audit.py` as of **v3** = 438127bc01ff3b99f98468549d58046f932490ef and **v4** = 74558c71c38ceaeace15fd4cf8aa9d84977584b1 (extracted with `git show <rev>:tools/append-only-audit.py`, run from scratch, never from the lane tree).
- Tips: `git rev-list --reverse 438127bc…ef~40..74558c71…b1` = 42 commits; `idx = i*(N-1)//7` for i in 0..7 (N=42) → indices 0,5,11,17,23,29,35,41; endpoints included.
- Contract modes, per the assignment ("with the contract at each tip"):
  - **tip** — no `--contract`; the tool resolves `registry/append-only-contract.tsv` at `--to`.
  - **pinned** — the 5-column contract as of the build tip (`sha256` prefix b1f139c28864df93, 2001 B), passed via `--contract` to every tip. This mode exists because the tip mode is not evaluable before the contract exists (finding F1); it holds the contract constant so the v3/v4 differential is observable across the whole span.
- Thresholds: 20 (tool default) at all 8 tips × 2 modes × 2 tools = 32 runs; plus 1 (§ assignment), 2, 5, 10 at 74558c71 (pinned) for a sensitivity axis = 8 runs.

| idx | tip | subject | contract at tip |
|---|---|---|---|
| 0 | `098df344d977` | round-44: wave-1 spec and dispatch (v2, 65 seats), C1/C2 drafts | absent |
| 1 | `58ffddd60e1f` | round-45: wave kama-r45-w1 spec, dispatch | absent |
| 2 | `0fddf257a0c5` | round-45: tip regression receipts at 82b5e9d3 | absent |
| 3 | `96d329186e77` | round-46: wave kama-r46-w1 spec | absent |
| 4 | `172b8ad040d5` | round-46 verifier spot-check (integrator, hyaku) | absent |
| 5 | `76a7aaff588f` | round-47: measured results, wave results, end census | 4-column (v2 shape), 936 B |
| 6 | `c4b2175d2ff9` | round-48: integration (measured) | 5-column, 2001 B |
| 7 | `74558c71c38c` | round-49: build — replay witness, bounded archive-member, v4 definitions | 5-column, 2001 B (same blob as idx 6) |

Commands (cwd `/fast/scratch/hyaku/kama-r49/X2Lane`, clone = `git clone --shared <lane> $S/lane`):

```
python3 $S/v3.py --repo $S/lane --to <tip> --threshold <t> [--contract <tsv>] --json      # exit 0/1/2
python3 $S/v4.py --repo $S/lane --to <tip> --threshold <t> [--contract <tsv>] --json      # exit 0/1/2
python3 sweep.py $S/lane $S/v3.py $S/v4.py <out>        # driver, reproduces all 40 run records
python3 summarize.py $S/lane                            # matrix.tsv + events.tsv
python3 analyze-regrade.py $S/lane $S/v4.py 74558c71… 0718b6ab… SCORECARD.md regraded-7.tsv
```

Replay check: a second `sweep.py` run into a clean directory reproduced all 40 records byte-equal after dropping the `contract` path label ("normalised mismatches []").

## Per-tip summary (threshold 20)

| tip | mode | v3 exit | v4 exit | events | v3 graded / ungraded_lines | v4 graded / ungraded_lines | v3 R/P/U/G | v4 R/P/U/G | bad_decls v3/v4 |
|---|---|---|---|---|---|---|---|---|---|
| 098df344 | tip | 2 | 2 | — | — | — | — | — | — (contract absent) |
| 098df344 | pinned | 1 | 1 | 1 | 14 / 17 | 14 / 17 | 1/0/0/0 | 1/0/0/0 | 3 / 3 |
| 58ffddd6 | tip | 2 | 2 | — | — | — | — | — | — (contract absent) |
| 58ffddd6 | pinned | 1 | 1 | 1 | 14 / 17 | 14 / 17 | 1/0/0/0 | 1/0/0/0 | 3 / 3 |
| 0fddf257 | tip | 2 | 2 | — | — | — | — | — | — (contract absent) |
| 0fddf257 | pinned | 1 | 1 | 5 | 5693 / 89 | 5700 / 82 | 5/0/0/0 | 5/0/0/0 | 3 / 3 |
| 96d32918 | tip | 2 | 2 | — | — | — | — | — | — (contract absent) |
| 96d32918 | pinned | 1 | 1 | 5 | 5693 / 89 | 5700 / 82 | 5/0/0/0 | 5/0/0/0 | 3 / 3 |
| 172b8ad0 | tip | 2 | 2 | — | — | — | — | — | — (contract absent) |
| 172b8ad0 | pinned | 1 | 1 | 5 | 5693 / 89 | 5700 / 82 | 5/0/0/0 | 5/0/0/0 | 0 / 0 |
| 76a7aaff | tip | 2 | 2 | — | — | — | — | — | — (4-col contract rejected by both) |
| 76a7aaff | pinned | 1 | 1 | 5 | 5693 / 89 | 5700 / 82 | 5/0/0/0 | 5/0/0/0 | 0 / 0 |
| c4b2175d | tip | 0 | 0 | 5 | 5693 / 89 | 5700 / 82 | 5/0/0/0 | 5/0/0/0 | 0 / 0 |
| c4b2175d | pinned | 0 | 0 | 5 | 5693 / 89 | 5700 / 82 | 5/0/0/0 | 5/0/0/0 | 0 / 0 |
| 74558c71 | tip | 0 | 0 | 5 | 5693 / 89 | 5700 / 82 | 5/0/0/0 | 5/0/0/0 | 0 / 0 |
| 74558c71 | pinned | 0 | 0 | 5 | 5693 / 89 | 5700 / 82 | 5/0/0/0 | 5/0/0/0 | 0 / 0 |

`R/P/U/G` = restored/partial/unrestored/ungraded events. `bad_decls` 3 at tips 0–3 is the pinned mode applying a later contract to a tree where `corpus/README.md:761` does not yet say append-only — identical under v3 and v4, so it is a mode artifact, not a differential.

Threshold sensitivity at 74558c71 (pinned, identical event key sets):

| threshold | events | v3 graded / ungraded_lines | v4 graded / ungraded_lines | v3 R/P/U/G | v4 R/P/U/G |
|---|---|---|---|---|---|
| 1 | 100 | 5954 / 194 | 5961 / 187 | 18/4/59/19 | 18/4/59/19 |
| 2 | 61 | 5924 / 185 | 5931 / 178 | 12/4/35/10 | 12/4/35/10 |
| 5 | 31 | 5856 / 170 | 5863 / 163 | 11/3/13/4 | 11/3/13/4 |
| 10 | 14 | 5784 / 125 | 5791 / 118 | 6/2/4/2 | 6/2/4/2 |
| 20 | 5 | 5693 / 89 | 5700 / 82 | 5/0/0/0 | 5/0/0/0 |

At every threshold the ungraded-line offset is exactly 7 and the status counters are identical.

## The one differing event (every tip ≥ 0fddf257, every threshold)

`events.tsv` flags 12 v3/v4 pairs, all the same event:

| commit | file | deleted | v3 graded / ungraded | v4 graded / ungraded | v3 status | v4 status | v3 restored_max / held_at_to | v4 restored_max / held_at_to |
|---|---|---|---|---|---|---|---|---|
| `0718b6abbda6` | `SCORECARD.md` | 2421 | 2349 / 72 | 2356 / 65 | restored | restored | 2349 / 2349 | 2356 / 2356 |

This reproduces the C2 claim (72 → 65, event stays restored) independently of the frozen counter. Fields `restored_best`/`restored_by` are `82b5e9d33a19` under both, i.e. all 2356 graded lines are present again at 82b5e9d3; the event is **held**, so the extra 7 lines cannot push it to `partial`.

The 7 re-graded lines (`regraded-7.tsv`, recomputed from v4's own `origins` at
`tools/append-only-audit.py:423` and the carve-out at `:475`; eligible titles at 74558c71:
`## Axes`, `## Planned`, `## Retired`, `## Saturation`, `## Capabilities`):

| parent line | section it was deleted from | origin (first appearance) |
|---|---|---|
| SCORECARD.md:121 | `## Capabilities` | `## Round 34 — capability repertoire and instrument-registry coverage (2026-10-24)` |
| SCORECARD.md:122 | `## Capabilities` | `## Round 34 …` |
| SCORECARD.md:123 | `## Capabilities` | `## Round 34 …` |
| SCORECARD.md:124 | `## Capabilities` | `## Round 34 …` |
| SCORECARD.md:125 | `## Capabilities` | `## Round 34 …` |
| SCORECARD.md:126 | `## Capabilities` | `## Round 34 …` |
| SCORECARD.md:127 | `## Capabilities` | `## Round 41 — head axes table reconciled to the tree (calibration) and the pin-watch capability (operability) (2026-10-25)` |

i.e. capability rows written in dated round sections that were later moved into an exempt head section and dropped there — exactly the laundering class the v4 origin rule targets. The other 65 lines v4 still leaves ungraded are rows born in an exempt head section (their `origin` title is one of the five exempt titles).

## Findings

**F1 — the "contract at each tip" leg is evaluable at 2 of 8 tips, identically for v3 and v4.** `registry/append-only-contract.tsv` first lands at 3a09a1d9 (round-47 build); tips 0–4 (098df344, 58ffddd6, 0fddf257, 96d32918, 172b8ad0) are before it, so both tools exit 2 with
`could-not-evaluate: git show <tip>:registry/append-only-contract.tsv: fatal: path … does not exist`.
Tip 5 (76a7aaff) carries the **4-column v2** contract (header `path rule declared_at note`, 936 B) and both tools reject it with
`could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>region<TAB>note` (exit 2). Consequence for calibration: the v3→v4 differential is only observable on 5-column-contract history, which is why the pinned mode is reported alongside. No v3/v4 difference in either failure mode (identical exit and message).

**F2 — v4's binding half never fires on the lane's own contract history.** Declarations (`path`, `ok`, `reason`) are identical between v3 and v4 at all 8 tips. The only unbound rows anywhere are the 3 at tips 0–4, and their reason in both versions is `declared_at corpus/README.md:761 does not say append-only for <path>` — a text-presence failure, not a token/negation/wildcard decision. So the word-bounded token (`tools/append-only-audit.py:216`), the three-word negation window (`:212`) and the wildcard self-declaration rule are exercised only by C2's fixtures and by v4's own selftest, not by lane history. This bounds the "v4 closes K1Binding" claim to fixture evidence; it does not contradict it.

**F3 — latent direction, not observed.** The origin rule can only *move* lines from ungraded to graded, so `graded` rises monotonically; `restored_max` is a hindsight maximum, so if a re-graded line were never restored the event could in principle move `restored → partial` (v4 raises `graded` toward `ng` while `restored_max` stays below). On this lane it does not: the 7 lines reappear at 82b5e9d3 and `restored_max == graded == held_at_to` under v4. No event changes status at any of the five thresholds, so the mapping `v4 partial/unrestored ⊆ v3 partial/unrestored` holds on all measured history.

**F4 — output shape.** Top-level key sets differ by exactly one key: v4 adds `definition: "v4"` (`tools/append-only-audit.py:504`); `schema` stays `append-only-audit/v3` in both, event key sets are identical, and text mode (`--json` absent) differs only in the two numbers of the one event and the `ungraded_lines` summary field. A consumer that keys on `schema` alone cannot distinguish v3 from v4 output — intended by the frozen C2 contract, recorded here as an interoperability note.

**F5 — context on the population v4 inherited.** At `--threshold 1` both versions report 100 events: 59 unrestored, 4 partial, 19 ungraded, 18 restored (regressed 0, vanished 0, binary 0). v4 changes none of these counters; the default threshold 20 contracts the population to 5 restored events. All 63 non-restored events sit at commits **before** the contract's introduction at 3a09a1d9 (63 of 63, measured against `rev-list --reverse 74558c71`); they are historical deletions of now-contracted files (`corpus/SOURCES.md` 18, `LOG.md` 8, `SCORECARD.md` 7, `corpus/README.md` 6, lesson files 22, `registry/report-landing-errata.tsv` 1, `corpus/QUALITY.md` 1), i.e. outside the declared era rather than a v4 classification change.

**Defects found: none.** No file/line in `tools/append-only-audit.py` v4 produces a classification that disagrees with the frozen C2 contract docstring; no proposed fix is attached. F1–F5 are measurement boundaries, not counter- or tool-edit requests.

## Files written

- `.ufo/waves/round-49/w1/out/X2Lane.md` (this report)
- `.ufo/waves/round-49/w1/out/X2Lane/matrix.tsv` — 40 runs: tip, subject, contract era, mode, threshold, exit, events, graded/deleted/ungraded_lines, R/P/U/G, regressed, bad_decls, the could-not-evaluate text, `schema`, `definition`
- `.ufo/waves/round-49/w1/out/X2Lane/events.tsv` — 496 per-event rows with `v3_v4` DIFF flags
- `.ufo/waves/round-49/w1/out/X2Lane/regraded-7.tsv` — the 7 re-graded lines with parent line, section, origin title, text
- `.ufo/waves/round-49/w1/out/X2Lane/runs/` — 40 run records (raw stdout + parsed JSON + exit/stderr) and the two selftest logs (`v3.py` 28 cases exit 0, `v4.py` 30 cases exit 0)
- `.ufo/waves/round-49/w1/out/X2Lane/contracts/` — contract at 74558c71 (5-column) and at 76a7aaff (4-column) as passed to `--contract`
- `.ufo/waves/round-49/w1/out/X2Lane/tips.json`, `sweep.py`, `summarize.py`, `analyze-regrade.py` — tip selection and reproducible drivers
- `.ufo/waves/round-49/w1/out/X2Lane/text-mode-v3.txt`, `text-mode-v4.txt` — text mode at 74558c71 (`diff -u` = 2 changed lines: the event line and `ungraded_lines`)

No lane file was written or staged; the lane was read through a `git clone --shared` in scratch, all runs read-only. No tool was installed or upgraded in this seat.
