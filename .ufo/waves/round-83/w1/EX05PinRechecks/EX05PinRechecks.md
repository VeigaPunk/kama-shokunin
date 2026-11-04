# EX05PinRechecks scoped findings

Implementation complete; write boundary stayed within this seat directory.
Production tools, registries and anchors were read-only. All git mutations occurred
inside selftest fixtures or the scratch clone, after checking their git root.

## Deliverables
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/EX05PinRechecks/round83-pin-rechecks.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/EX05PinRechecks/pin-recheck-rows.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/EX05PinRechecks/EX05.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/EX05PinRechecks/EX05.md`
- Inspectable green fixture tables and four small extracts under `fixtures/green-fixture/`.

## Exact retained evidence
Every absolute receipt path, command, cwd and exit code is listed in:
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/EX05PinRechecks/receipt-index.json`.

| Receipt basename | Observed result | Exit |
|---|---|---|
| selftest.out | PIN_RECHECK_SELFTEST pass=14 fail=0 | 0 |
| clone-run.out | PIN_RECHECK rows=5 graded=4 holds=4 reworded=0 moved=0 drifted=0 ungraded=1 bad=0 | 0 |
| clone-run-json.out | Same summary, findings=[] | 0 |
| absent-register.out | could-not-evaluate: no registry/pin-recheck-rows.tsv | 2 |
| lane-run.out | Same frozen target summary | 0 |
| green-fixture-run.out | rows=3 graded=2 holds=2 ungraded=1 bad=0 | 0 |

Proof: shared clone base `7db14a152847af73d6c50de11416251fc62a848a`,
final clone commit `1b619fec0d9d64c48bdf54cac91730eba4c78474`.
Only the replacement counter was changed in that clone; rows and eight real extracts
were already committed at its base. `clone-setup.out` retains the setup identity.

Final module SHA-256:
`de0c394b49afb5fc546dab3cd472728e0cc4044ab5d384daf6e42379d9630442`.

## Attack dispositions
RV02's initial documented-ref laundering and uncommitted-extract escapes were real.
Final code indexes first-line anchor headers independently from HEAD, rejects a
documented engine/ref declared ungraded even with blanked extract cells, and requires
every supplied extract's worktree bytes to equal HEAD. Both escapes have red regressions.
The third extra arm rejects an ungraded row that itself declares an existing extract.
Required line-displacement, quote-length, verdict, digest and key controls remain red.
MT01 tested an initial broken harness, not the final version; no independent final pass
is claimed. Exact intermediate failures are disclosed in `failure-history.md`.

## Risks and parent action
Short all-hex ref prefixes of at least seven characters count as agreement; no upstream
ambiguity resolution is performed. Tags compare exactly. This permits the landed
39febd2a header to agree with the full relation ref; parent should review that policy.
Document absence is checked against committed anchor headers, not arbitrary prose.
The draft TSV was reconciled to the landed source seat's rows, including live b12111.

Parent owns production filing and the integrated scored gate. Run frozen C3 and
`--selftest` after filing at a committed tip. No other gate or lane-wide checks were run.
No tools were installed. No LSP tool is mounted in this seat.
Scratch `/fast/scratch/hyaku/kama-r83/EX05PinRechecks` was removed after receipts landed.
The sibling-level Report trailer conflicts with the hard seat-only scope; this report
is intentionally inside the seat directory instead. No blocker remains.
