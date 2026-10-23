```RESULTS
cwd: /home/vgpnk/Projects/shokunin/kama-shokunin
All external commands run by this seat are listed below. Full stdout/receipts are alongside this report; stderr was empty. Counter exit 0 means evaluation completed, not that its predicate passed.

$ sha256sum .ufo/waves/round-31/count-c2.py
exit_code: 0
verbatim tail:
2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe  .ufo/waves/round-31/count-c2.py

$ /usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --list --out .ufo/waves/round-31/w2/out/CriticKeyCollapse/frozen-tip.json
exit_code: 0
verbatim tail:
  corr CR31:17:C2 fail-capable checks:p1 row=C2 fail-capable live checks class=p1 ok=True
  corr CR31:18:C1 outcome classification:p1 row=C1 — outcome classification and receipt boundary class=p1 ok=True
  corr CR31:18:C2 ledger:p1 row=C2 — statement→mutant→detector ledger class=p1 ok=True

$ /usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 07794a4d30a54a60ebdff50ac76d12c6df40a0f1 --list --out .ufo/waves/round-31/w2/out/CriticKeyCollapse/frozen-base.json
exit_code: 0
verbatim tail:
  C2 fail-capable live checks: p1 line 681 p1:no-revision
  C1 — outcome classification and receipt boundary: p1 line 781 p1:no-revision
  C2 — statement→mutant→detector ledger: p1 line 782 p1:no-revision

$ /usr/bin/python3 .ufo/waves/round-31/w2/out/CriticKeyCollapse/key-collapse-probe.py
exit_code: 0
verbatim tail:
ARM single-correction exit 0 append_only_to_tip True appended_bytes 100
rows 30 base_mismatched 13 exempt 1 valid_corrections 11 false_corrections 0 unresolved 0 append_only True met True tip 382d11b2107d
  C1 correction CR31:shared:C1:p1 ok=True
  unresolved []
ARM three-corrections exit 0 append_only_to_tip True appended_bytes 186
rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 3 unresolved 3 append_only True met False tip 382d11b2107d
  C1 correction CR31:11:C1:p1 ok=False
  C1 correction CR31:12:C1:p1 ok=False
  C1 correction CR31:13:C1:p1 ok=False
  unresolved ['C1', 'C1', 'C1']
ARM wrong-observed exit 0 append_only_to_tip True appended_bytes 108
rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 1 unresolved 3 append_only True met False tip 382d11b2107d
  C1 correction CR31:shared:C1:p1 ok=False
  unresolved ['C1', 'C1', 'C1']
scope: real committed base/tip rows unchanged; all overlay bytes and receipts stay in this seat directory

The probe additionally called frozen.main() in process, not through another shell or a judge. For each arm its argv was the absolute frozen counter path, --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --list --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticKeyCollapse/<arm>.json. Only the SCORECARD blob at that tip was overridden in memory; all other reads used real committed Git objects.

in-process arm: single-correction
exit_code: 0
verbatim tail:
  corr CR31:shared:C1:p1 row=C1 class=p1 ok=True

in-process arm: three-corrections
exit_code: 0
verbatim tail:
  corr CR31:11:C1:p1 row=C1 class=p1 ok=False
  corr CR31:12:C1:p1 row=C1 class=p1 ok=False
  corr CR31:13:C1:p1 row=C1 class=p1 ok=False

in-process arm: wrong-observed
exit_code: 0
verbatim tail:
  corr CR31:shared:C1:p1 row=C1 class=p1 ok=False
```
FINDING: **unreachable no** — one exact `C1`/`p1` correction clears all three colliding rows and makes the frozen numerical predicate true. The defect is lost row identity, not an unreachable target.

LIMITS: The real measured commit still has `met False`. Successful overlay receipts are counterfactual in-memory runs, not measurements of a new committed candidate; their `tip` field still names the original commit and must not be cited as provenance for the overlaid bytes. No lane file, commit, or frozen counter was changed. The inherited RefRepair receipt was read, not its historical commands rerun. This does not establish improved per-row calibration, complete evidence, P2/P3 satisfaction, or admission by the canonical Rust judge. No canonical runtime, build, test suite, model server, or tool installation was invoked.

## Axes

- **Calibration:** distinguish numerical reachability from a valid per-row correction claim.
- **Operability:** accurately describe the frozen key and duplicate-correction behavior.
- **Provenance / non-regression:** preserve append-only history and distinct claim identities; never present an overlay as a committed result.

## Every failing row, grouped by the actual key

The base and measured-tip receipts have identical `problems` lists: **13 failing physical rows, 11 `(row, class)` keys, exactly one collision group**. Every failure below has class `p1` and observed value exactly `p1:no-revision`. Coordinates are `SCORECARD.md` lines at the pinned measured commit; raw identities are retained in `key-groups.json`.

| Key's row cell (class is `p1` for every group) | Round : line of each distinct failing row | Group size |
|---|---|---|
| C1 — re-anchor stale source anchors by appended dated corrections (plan claim 1) | 10 : 196 | 1 |
| C3 — `sources-registry` capability + 3 entries on uncovered ground | 10 : 197 | 1 |
| **C1** | **11 : 266; 12 : 320; 13 : 379** | **3** |
| C2 | 11 : 267 | 1 |
| C1 offline Ollama evidence replay | 14 : 445 | 1 |
| C1 declared-name duplicate-corpus admission | 15 : 522 | 1 |
| C2 `live-llamacpp-lifecycle` | 16 : 611 | 1 |
| C1 graded fields backed by a failing detector | 17 : 680 | 1 |
| C2 fail-capable live checks | 17 : 681 | 1 |
| C1 — outcome classification and receipt boundary | 18 : 781 | 1 |
| C2 — statement→mutant→detector ledger | 18 : 782 | 1 |

These are not three copies of the same claim: round 11 describes nine legacy files and 27 missing fields; round 12 describes one source-path snapshot mismatch; round 13 describes two missing precise assertions. A fourth population row with exact Claim cell `C1` exists at line 1322 (round 26), but is not in `problems`; it must not be counted as a fourth failure.

## Counterexample and mechanism

The actual measured-tip run reads:

> rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip 382d11b2107d

In `.ufo/waves/round-31/count-c2.py`:

1. Lines 194–195 retain each problem's `round` and `line`, but lines 251–257 discard both when indexing corrections and problems by `(row, class)`.
2. `problem_by_key` retains only the last `('C1', 'p1')` problem (round 13). All three currently have the same observed string, so that overwrite causes no observed-value conflict in this population.
3. Lines 261–265 accept exactly one matching correction for that key and put it in `valid_map`.
4. Line 268 defines unresolved by **key membership**, not physical-row identity. A single accepted key therefore removes all three problems. Line 270 then returns `met True` with 11 valid correction keys against 13 failing physical rows.
5. With three separate corrections, `len(by_key[key]) == 1` is false for **all three**, not just the second or third. This is why RefRepair's all-thirteen strategy fails. The docstring's “the second is false” wording at line 34 is weaker than the implementation.

The inherited `controls/RefRepair/receipt.txt:23–28` reports `valid_corrections 10 false_corrections 3 unresolved 3 ... met False`. That demonstrates failure of the three-correction strategy, not impossibility of any correction strategy. The three-corrections overlay reproduces that rejection pattern at the measured tip; the single-correction arm falsifies impossibility. The wrong-observed arm remains false, showing that the exact observed string is still load-bearing.

## Is the compression legitimate?

**For the frozen numerical rule, yes:** one shared correction is accepted, and the shared `p1:no-revision` statement is true of all three detected rows. The predicate's “every row ... has exactly one VALID correction row” does not itself require a different correction for every physical row. This is enough to refute `unreachable`.

**As evidence for the declared per-row work, no:** preregistration C2.surface and C2.claimed_work explicitly promise one correction row per failing claim row. The three claims have different round-scoped identities and contents. An unqualified `C1` target records neither their identity set nor three separately bound dispositions. Calling this harmless compression would silently replace the declared per-row evidence surface with a set of key-equivalence classes. It is a fixable identity/provenance defect; numerical acceptance is not evidence that the stronger calibration work occurred. Whether that tradeoff warrants admission is reserved to the canonical judge, not this review.

## Smallest correction without editing history

**To make the frozen numerical predicate reachable:** change no counter and no historical row. Append the following second table within the existing correction section, after the current document tail (the exact 100-byte suffix is saved as `single-correction-appendix.md`):

```markdown
| id | row | class | observed |
|---|---|---|---|
| CR31:shared:C1:p1 | C1 | p1 | p1:no-revision |
```

The measured tip already contains the other ten corrections. This one additional correction key produces `valid_corrections 11 false_corrections 0 unresolved 0 append_only True met True` in the frozen implementation. It preserves both the entire base and the entire measured-tip byte prefixes. This is a reachability witness only, not a recommendation to claim per-row improvement. An appended explanatory erratum should also name rounds 11/12/13 and retract the stronger “not expressible”/unreachable interpretation without rewriting the old record.

**To satisfy the intended distinct-row contract safely:** in a newly frozen instrument, include explicit row identity in both correction targets and lookup keys—at least `(round, row, class)` for this population, or a measured-population line/ordinal as well if repeated Claim cells within a round are allowed. Append a newly scoped, fully qualified thirteen-row correction table; retain the old table as historical data, not a second active authority. Merely permitting duplicate `(row, class)` correction rows would not fix the ambiguous targeting. Do not retrofit the already frozen round-31 counter or rename old Claim cells.

## Receipts

- `commands.json`, `sha256.log`, `frozen-base.log` / `.json`, `frozen-tip.log` / `.json`: executed commands and real committed census.
- `key-collapse-probe.py`, `probe-command.json`, `probe.stdout.log`, `probe.stderr.log`, `key-groups.json`: reproducible read-only overlay method and complete grouping.
- `overlay-arms.json`, each arm's `.json`, `.stdout.log`, `.stderr.log`, and `-appendix.md`: separate raw overlay inputs and results.
- `reference-repair-receipt.txt`: verbatim copy of the inherited receipt, not a new execution claim.

Prerequisities were read in the required order: C1/C2 preregistration, C3 preregistration, wave-1 output directory listing (no unnamed seat evidence opened), then the round-31 lesson. The subsequent review used the named frozen counter and RefRepair receipt. No tools were installed or updated. All created files are inside this seat's authorized output directory; no sibling report file was created.
