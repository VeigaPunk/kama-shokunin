# M3Tool — C2 v6 mutation probe

**Verdict: 20 mutations tested; selftest killed 12, 8 survived; frozen C2 lane counter killed 1 survivor and accepted 7 (survivors relative to this detector).**

Mutant source was copied from `tools/append-only-audit.py` into `/fast/scratch/hyaku/kama-r51/M3Tool/append-only-audit.py` (pristine SHA-256 `3d0eaa168c26f006da656e635995f14d43c57c3a9af43ddf1b954f5ca3070c11`). Mutants were isolated copies; the lane was not modified. Each selftest invocation used `python3 <mutant>.py --selftest --scratch <scratch>/<mutant-name>`; command exit 0 = survived, exit 1 with `FAIL <case>` = killed. Selftest captured output was clipped in this report to the decisive case name; all executed outputs are in the running task transcript.

## Selftest results

| Mutation | Result / decisive case |
|---|---|
| ROW regex accepts S-number >=2 digits | Survived (exit 0) |
| MUTABLE_COLS changes status column to immutable | Killed: `v6-arow-mutable` |
| eleven-cell requirement changed to ten | Killed: v6 A-row row cases |
| permitted `keep()` equality inverted | Killed: `v6-arow-mutable` |
| A-row file set forced empty | Killed: v6 A-row mutable case |
| disclosure CR rejection disabled | Survived (exit 0) |
| SHA-256 field requires 63 hex chars | Killed: bad disclosure cases |
| disclosure field count changed | Killed: bad disclosure cases |
| unheld graded line count forced to zero | Killed: `v6-disclosed` |
| Revert subject classified as removal | Survived (exit 0) |
| in-place-edit/removal branches swapped | Killed: `v6-disclosed`, `v6-bad-disclosures` |
| disclosed status no longer requires positive disclosed count | Survived (exit 0) |
| unheld JSON output emits before-consumption counter | Survived (exit 0) |
| bad-disclosure exit condition removed | Killed: bad-disclosure cases |
| default threshold changed 1 to 20 | Killed: `v6-default-threshold` |
| disclosure loop index replaced by all rows | Killed: disclosure fixture cases |
| disclosure hash omits CR-stripping `key()` | Survived (exit 0) |
| disclosure count comparison `>` changed to `>=` | Killed: `v6-disclosed` / count boundary |
| permitted position shifted by one | Killed: A-row cases |
| backtick toggle made always true | Killed: `v6-arow-code-span-pipe` |
| ungraded count includes permitted rows | Survived (exit 0) |

The requested `class_valid` probe had no exact anchor in source; it was not counted among the 20 tested mutations. The valid-class branch is `if klass not in CLASSES` (source lines 687-694), not the attempted `elif` anchor.

## Frozen C2 counter

Pristine control:

`python3 .../round51-append-audit-v6-check.py --repo /fast/scratch/hyaku/kama-r51/M3Tool/lane --tip 138af25b963450b6520794995605fa7dbbcd87e0 --scratch /fast/scratch/hyaku/kama-r51/M3Tool`

Exit **0**, output `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`; details confirm all nine scenarios pass, including code-span pipe, valid disclosure, four malformed disclosures, partial disclosure, and two-files-one-commit. Lane receipt: `tool v6 threshold 1 exit 0 events 106 disclosed_lines 166 permitted_lines 58; own lost lines ... 142; ledger lines 166`.

For each selftest survivor, I wrote that mutant into the isolated shared clone at the frozen lane commit, made a fixture-identity commit after checking clone root, and ran the frozen counter at that mutant commit. Clone root: `/fast/scratch/hyaku/kama-r51/M3Tool/lane`. Results:

| Survivor | Counter exit | Counter verdict | Interpretation |
|---|---:|---|---|
| ROW regex | 0 | met=True | Accepted; equivalent on this detector's constructed/lane data |
| CR rejection | 0 | met=True | Accepted; equivalent on this detector's constructed/lane data |
| Revert class | 1 | met=False | **Killed**: frozen counter's own classification finds wrong mechanical class |
| disclosed-status predicate | 0 | met=True | Accepted; equivalent on this detector's constructed/lane data |
| undisclosed JSON counter output | 0 | met=True | Accepted; detector does not exercise that output detail |
| CR-stripped line hash | 0 | met=True | Accepted; no lane fixture exposes CR distinction |
| ungraded count includes permitted | 0 | met=True | Accepted; detector does not independently assert this JSON count |

**Coverage findings:** the frozen counter catches the Revert-class mutant despite selftest survival. Seven other selftest survivors pass it; the distinctions involving malformed disclosure CR bytes, >2-digit S ids, empty unheld JSON representation, ungraded count, and the `disclosed` branch's zero-disclosure edge are not exposed by this counter's fixtures or lane assertions. No claim is made that these mutations are behaviorally equivalent outside the exercised inputs.

No tools installed or updated. Scratch was removed after copying the required evidence into the report. No independent receipt files were written.