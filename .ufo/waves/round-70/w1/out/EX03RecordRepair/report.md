# EX03RecordRepair — advisory record edits

Axes: operability + calibration; calibration 7 is the lowest assigned axis, saturation 8, nudge inactive. No verdict, axis promotion, tracked-file edit, tool installation, dispatch, build, test, formatter or smoke run was performed.

## Deliverables and landing order

1. `record-repair.patch`: unified diff against the exact `6035e952` SCORECARD.md and PROVINCE.md blobs. Apply only after reconciling with any already-landed L1 edits; the live working tree was changing during discovery. This is a base diff, not an instruction to overwrite current records.
2. `round70-sections.md`: append to SCORECARD.md after filling the explicitly marked L1 placeholders. It intentionally supplies the claim-table **header only**, never invented measured rows/verdicts. It supplies the Round 70 heading and Planned 71 numbered items that make the head's round-70/71 pointers coherent. Do not append it twice if L1 already has Round 70.
3. `verify.sh`: isolated base clone recipe; accepts one optional absolute unified harness-patch path. It commits only inside its guarded fixture, with the lane-configured identity, and prints the reconciler's real summary/exit. It is not executed in this editing wave. Run `bash .ufo/waves/round-70/w1/out/EX03RecordRepair/verify.sh <EX01-harness.patch>` after integration. Omitting the harness patch deliberately leaves the base's git-run failures observable.
4. `commands.json`: exact argv, stdout, stderr and exit of the four subprocess discovery commands (two complete base blobs and identity lookups), plus final scratch cleanup; retained output is not truncated. The commands are directly reproducible from their argv arrays.

## Retained base receipt (supplied evidence; not rerun)

```text
tip=6035e952c2521999e192d6f236331f265ac98392
r41=2 banner=1 planned=1 retired=1 saturation=0 caps=0 receipts=0 readme=0 province=4 rel=0 closure_ptr=0 mismatches=10 maxN=69 met=False
detail: r41 operability run `python3 tools/gate-registry-check.py --selftest` no stdout line == 'GATE_SELFTEST pass=7 fail=0' (exit 1)
detail: r41 calibration run `python3 tools/round69-newest-closure-counter.py --since-round 63` no stdout line == 'NEWEST_CLOSURE … row_current=true' (exit 2)
detail: banner: head lacks 'Latest measured round: 69'
detail: planned: section does not name '### Planned (round 70)'
detail: retired: does not state '15 capabilities'
detail: province: PROVINCE.md lacks tools/round67-worktree-landing-check.py (capability worktree-landing-check)
detail: province: PROVINCE.md lacks tools/round68-receipt-pointer-audit.py (capability receipt-pointer-audit)
detail: province: PROVINCE.md lacks registry/receipt-pointer-resolutions.tsv (capability receipt-pointer-audit)
detail: province: PROVINCE.md lacks tools/round69-newest-closure-counter.py (capability newest-closure-counter)
detail: closure_ptr: calibration row latest outside closure is round-68; newest at tip is round-69
EXIT=1
```

## Each detail line → rule → exact disposition

| Base detail | Rule | Exact proposed edit / owner |
|---|---|---|
| r41 operability gate selftest has no expected stdout, exit 1 | Imported r41 run facts must execute and produce the cited line | No record weakening. EX01 repairs the metadata-free run harness; this patch leaves the cited command and expected output intact. |
| r41 calibration newest-closure command has no expected stdout, exit 2 | Same imported run-fact rule | Same EX01 dependency; updating the row's closure pointer is necessary but does not provide git metadata to the harness. |
| banner lacks Latest measured round: 69 | Banner number equals max dated Round heading | Round-70 landing head says `Latest measured round: 70`; append supplied Round 70 section. It does not claim this unmeasured fixture passed. |
| planned lacks Planned (round 70) | First Planned section names maxN+1; actual heading followed by item 1 | Head pointer becomes `### Planned (round 71)` below (§Round 70); append supplied heading and three numbered items. Existing dated Planned 70 remains byte-exact. |
| retired lacks 15 capabilities | Count equals rows in highest-numbered canonical table | `None. 6 axes and 13 capabilities remain active.` → `None. 6 axes and 15 capabilities remain active.` |
| province lacks tools/round67-worktree-landing-check.py | Every tools/registry evidence token in canonical rows appears in PROVINCE | Add token and worktree/HEAD identity description to existing lane-instruments row. |
| province lacks tools/round68-receipt-pointer-audit.py | Same token rule | Add token and receipt-resolution description to that row. |
| province lacks registry/receipt-pointer-resolutions.tsv | Same token rule | Add token alongside receipt audit in that row. |
| province lacks tools/round69-newest-closure-counter.py | Same token rule | Add token and newest-closure identity description to that row. |
| closure_ptr names round 68 while newest is 69 | Exactly one latest-outside-closure pointer equals newest tree blob; every including round K equals it | Calibration row pointer round-68 → round-69; `both round-68 claims` → `both round-69 claims`; `including round 68` → `including round 69`; row re-anchor round 69 → 70. |

Adding the four tokens changes PROVINCE's hash, so the same patch re-anchors the coverage row to **c936b2e7f9efdcc605a77b06fe6af181bf1f1c584f577aed742b71ad01325fba**, retaining **270 lines**. This is the candidate blob identity, not an assertion about concurrent L1 bytes.

The highest canonical heading at base is round **69**, with **15 data rows** (header/separator excluded). Round 70 adds no capability row, so Retired must say **15 capabilities** at landing. Saturation's first-working rounds and score vector already match and remain unchanged; the capability mirror already matches and remains unchanged.

The existing archive is actually `### Superseded head banners (kept verbatim; round 48)`, not a level-two heading. The patch appends the replaced base line 6 byte-exact at that archive's end before `## Round 48`; no dated round text is replaced or deleted. The five re-derived sections are exempt per `registry/append-only-contract.tsv` SCORECARD row; unchanged head sections are not gratuitously restyled.

## Remaining drift / checks reserved to L1

- Record-only base fixture cannot honestly promise `mismatches=0`: the receipt contains two independent imported run-fact failures. Expected removal of the eight record failures is an inference until L1 runs the integrated tool. EX01's real harness repair is required; no checks are disabled here.
- `record-repair.patch` alone intentionally depends on appending the supplied Round 70/Planned 71 section. Without it, maxN remains 69 while head says 70 and Planned 71.
- A later closure blob round 70 would require both row tokens to advance to 70; this candidate targets the round-70 landing before its own outside closure, whose newest supplied closure is 69.
- Any additional PROVINCE or SKILL edits by L1 require re-deriving their final hashes and line counts. The patch cannot predict concurrent final blobs.
- The full reconciler, five-arm selftest, canonical-count audit, append-only checks, patch application and real census were **not run**, per editing-wave guard. `verify.sh` is a runnable recipe, not a retained green receipt.
- LSP is not exposed by this seat's tool inventory; no supported-symbol refactor was needed for the Markdown records. No credentials/session/config secret values were read.

## Exact discovery commands and outputs

The retained `commands.json` holds the complete outputs/exit=0 of:

```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 6035e952:SCORECARD.md
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 6035e952:PROVINCE.md
git -C /home/vgpnk/Projects/shokunin/kama-shokunin config --get user.name
# stdout: kama-shokunin (newline); exit 0
git -C /home/vgpnk/Projects/shokunin/kama-shokunin config --get user.email
# stdout: kama@shokunin.local (newline); exit 0
```

Additional non-subprocess inspection used read/grep against the frozen claims, supplied receipt, reconciler docstring/evaluator, append-only contract and extracted blobs; these tools do not supply process exit codes. Canonical parsing printed `canonical round 69 data rows 15`; candidate generation printed `Generated PROVINCE candidate identity: c936b2e7f9efdcc605a77b06fe6af181bf1f1c584f577aed742b71ad01325fba lines 270` and `Patch bytes: 21319`. An accidental `%load "scripts/none.py"` call failed with ENOENT before executing any script; no file was created. No other verification output is claimed.

Scratch cleanup ran `bash -c 'S=/fast/scratch/hyaku/kama-r70/EX03RecordRepair; trap '\''rm -rf -- "$S"'\'' EXIT; printf "%s\n" "Removing seat scratch on EXIT"'`: stdout `Removing seat scratch on EXIT`, exit 0. Its exact argv/streams are retained in commands.json.

EX01 supplied the optional harness patch path: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-70/w1/out/EX01ReconHarness/diff.patch`. Pass this as verify.sh's argument after EX01 publishes it; this report does not claim to have read, applied or tested those candidate bytes.

## Self-evaluation (advisory, not lane judgment)

Accuracy 4: base bytes retained; integrated green unobserved. Completeness 4: all requested artifacts supplied, with mandatory harness dependency exposed. Clarity 4: landing-only placeholders distinguished from measured claims. Actionability 4: base diff and guarded script supplied, integration remains L1-owned. Conciseness 4: explicit ten-detail mapping retains necessary repetition. Overall 4.0; primary improvement is L1 integration measurement, intentionally prohibited here. User agreement is not assumed.
