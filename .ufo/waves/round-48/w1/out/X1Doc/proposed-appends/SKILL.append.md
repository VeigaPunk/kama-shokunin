# Proposed append for `SKILL.md` (drafted by seat X1Doc; append-only, never in place)

Anchor: end of `SKILL.md` at `380bcdff9c8af06997c482f6eb03db926a794a2b` (1463 lines, last line
`- A receipt whose log file is gone still replays: …`). Append the block below at EOF, as new lines.
`SKILL.md` holds no row in `registry/append-only-contract.tsv`; nothing in the block declares the file
append-only, and the heading carries no `append-only` word so the KQ71 heading census gains no uncovered claim.
The block supersedes the instrument statements in rows 1441, 1442, 1450 and 1453, plus the exit-map cell of the
round-48 tool row (`SKILL.md:1473` on the integration tree, which reads "1 otherwise"); their measured round-46/47
values stay quoted as history.

---

### Round-48 superseding note on the round-46 and round-47 instrument rows (v3 contract format)

Drafted at lane commit `380bcdff9c8af06997c482f6eb03db926a794a2b` by seat X1Doc. Rows 1441, 1442, 1450 and 1453
describe `tools/append-only-audit.py` and its two counters as they were before the round-48 build replaced the tool
with schema `append-only-audit/v3` (tool sha256
`ec9c6d206fccfd9b9b04526b54da34207c48ab9f0768c3285128cd59fcf60f72`) and the contract with a nine-row, five-cell
file (sha256 `ca0618e50fadc4b0d53b0d8a61868b0ea7fbf33b3429c125a0d5643022a77075`; header
`path<TAB>rule<TAB>declared_at<TAB>region<TAB>note`). Each row's own measured numbers remain true at the tip it
names; what changed is what a reader gets when re-running the row's command at a tip at or after this build.

- **Row 1441 (round-46 C2 counter).** Its fixture and lane legs read the graded tool at `--tip`, so at the v3 build
  they compare v3 output against v1 expectations. Measured:
  `python3 tools/round46-append-audit-check.py --repo <clone> --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch <dir>`
  prints `selftest=1 fixture=0 lane=0 table=1 lane_events=5 lane_unrestored=0 lane_partial=2 met=False`, exit 1, with
  `detail: fixture full ok=False rc=2 got=[]` (its fixture writes a four-cell contract, which v3 refuses) and
  `detail: lane rc=0 missing=[… deleted=2290 …]`. The row's pinned measurement still reproduces at its stated tip:
  `--tip 4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` prints `selftest=1 fixture=1 lane=1 table=0 lane_events=5
  lane_unrestored=0 lane_partial=2 met=False`, exit 1, matching the row's `table=0 … met=False` text.
- **Row 1442 (round-46 tool row).** The tool no longer prints `restored_at_tip=`. v3 prints
  `event <commit12> <file> deleted=N graded=G ungraded=U restored_max=K held_at_to=H status=S restored_best=<c12|->
  restored_by=<c12|->`, `declaration <path> <declared_at> unbound: <reason>` for a row that does not bind, then
  `summary commits=C files=F events=E restored=R partial=P unrestored=U ungraded=G ungraded_lines=U regressed=R
  vanished=V unmatched=M binary=B bad_declarations=D`. `--contract <tsv>` exists beside `--files`, and `--files`
  binds no declaration. Exit 1 also fires on a regressed event, a vanished declared path and an unbound declaration
  (`tools/append-only-audit.py:469-474`); exit 2 on a malformed or CRLF contract.
- **Row 1450 (round-47 C1 counter).** "four cells per row" is now five, and the counter refuses the v3 contract:
  `python3 tools/round47-append-audit-v2-check.py --repo <clone> --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch <dir>`
  prints `selftest=1 contract=0 lane=0 fixture=0 stable=0 files=0 lane_events=0 lane_mismatch=-1 fixture_mismatch=-1
  met=False`, exit 1, with `detail: contract: header line is not exactly path<TAB>rule<TAB>declared_at<TAB>note` and
  `detail: fixture: tool exit=2, stdout is not one JSON object`. It still meets its predicate at its own build tip
  (`--tip 3a09a1d93dcc16799cf6c4b48786e6440af134c4`: `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85
  lane_events=5 lane_mismatch=0 fixture_mismatch=0 met=True`, exit 0). The round-48 successor is
  `tools/round48-append-audit-v3-check.py` — `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89
  lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`, exit 0, at `380bcdff`.
- **Row 1453 (round-47 tool row).** The `--json` document is `{"schema": "append-only-audit/v3", "to", "threshold",
  "contract", "files", "commits", "events", "declarations", "vanished", "unmatched_patterns", "binary_changes",
  "summary"}`; `files` is the expanded path list (89 at `380bcdff`; 87 at `3a09a1d9` under this contract, where the
  row's `files=85` was read), and `summary` carries `ungraded`, `ungraded_lines`, `regressed`, `vanished`,
  `unmatched` and `bad_declarations` beside the v2 counters. The selftest at `380bcdff` is
  `AOA_SELFTEST pass=27 fail=0` (the row records `pass=19` after the round-47 wave), with the v3 cases
  `exempt-rewritten`, `exempt-gutted`, `exempt-gutted-then-regrown`, `dated-rewritten`, `only-errata` and `clamp`
  added to the pinned set. Deleted counts still come from the `-U0` hunk headers and the hunk-count refusal is now
  at `tools/append-only-audit.py:400` (the row is silent on its line number; `corpus/QUALITY.md:397` cites the v2
  line 203).
- **Exit map, all four rows.** Read "1" as: a `partial` or `unrestored` event, a `regressed` event, a `vanished`
  declared path, or an unbound declaration (`tools/append-only-audit.py:469-474`). It is **not** "1 otherwise":
  `unmatched_patterns` and `binary_changes` are reported and do not change the exit. Measured on a copy of the
  build's contract with one added row (`LOG.md/*`, bound at `README.md:16`): `unmatched-pattern LOG.md/*`,
  `summary … unmatched=1 …`, **exit 0**.
