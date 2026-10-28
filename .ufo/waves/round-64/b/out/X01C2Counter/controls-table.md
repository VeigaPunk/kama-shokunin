# Controls table (round-64 C2 counter)

Counter sha256 c8b725e57f6e761735e832d127ec6df622d4a9dff09893b5fa31131c64d93e2e; 120 controls in 14 families (`EXPECT_CONTROLS`=120). A control is rejected when the failure tag in the last column is among the tags its mutated input produced and the unmutated input does not produce it; all controls are credited only while the unmutated baseline is met.

| family | n | what is mutated |
|---|---|---|
| canon | 4 | the newest canonical list of SCORECARD.md: a row dropped, heading demoted to round 63, a row prefix altered, a row duplicated |
| closure | 5 | the calibration row pointer: stale, absent, no row, no spotcheck files, pointing above the newest |
| flip | 11 | the decision functions behind regress_flipped and printers_rejected, fed planted outcomes (true->true, host-busy->host-busy, base false, base undeclared, printer not accepted, printer that still passes, a printer that flips) |
| gate | 16 | each frozen field planted one step off its target, and population 11, and an unknown reconciler count: gate() must name the field |
| idle | 21 | both outcomes of the context-capacity row on planted receipts: busy with invented / empty / partial / missing host_idle / ok host_idle / wrong error / a cell run / exit 0 / text missing; idle with exit 1 / pattern missing / pattern only / zero cells / unobserved / errored / ports open / foreign pid seen / exit code 2 |
| pattern | 5 | patterns that must bind the whole claim: unknown=01, unknown=0 followed by text, IA_SELFTEST pass=0 fail=3, pass=3 fail=0, a dead tool path |
| pins | 5 | the pin check: a bound tool edited, the reconciler edited, a tool absent, the pin table cut to 12, a dependency (round-41 counter, round-25 count) edited |
| printer | 2 | printer copies of all 12 tools (plain: the regression does not apply; decoy: original source kept in comments so the regression applies and the printer still passes) |
| reconciler | 11 | the reconciler verdict: exit 1 beside mismatches=0, no count, silent crash, nonzero count, met=False; and the planted stale-pointer comparison (no count, repaired run fails, stale run passes, no mismatch increase, no detail line, detail on the repaired run) |
| registry | 17 | one registry row or column of registry/capability-claims-r64.tsv: dropped, renamed, binding/verdict/quote/pattern/run/outcomes forged, quote shortened below 8 chars or emptied, row duplicated (identical and conflicting), observed cell forged/blank/fragment, a free-form row |
| regress | 11 | the regression table registry/capability-regress-r64.tsv and its application: find twice/absent, replace==find, multi-line cell, replacement that does not compile, row missing/duplicated/wrong tool_path/unbound cap, and a harmless regression that must not count (run live on pin-watch) |
| selftest | 1 | the four planted defective verdict functions of the sensitivity self-test |
| tally | 8 | tally_disclosed over planted record sets (all no-disclosure, one, unreadable, round missing, none) and the no-disclosure fixture status relabelled/unreadable/none |
| work | 3 | --work reuse: an empty pre-existing tip/ dir, a run/ dir only, and the counter run a second time on its own --work (must exit 2 work-reused, print no met=) |

## Per control

| family | control | failure it must produce | rejected in trial B |
|---|---|---|---|
| canon | canon-drop-row | `canon-missing` | yes |
| canon | canon-old-round | `canon-round` | yes |
| canon | canon-prefix | `prefix` | yes |
| canon | canon-dup-row | `canon-dup` | yes |
| closure | closure-stale-pointer | `closure-stale` | yes |
| closure | closure-no-pointer | `closure-nopointer` | yes |
| closure | closure-no-row | `closure-norow` | yes |
| closure | closure-no-files | `closure-nofiles` | yes |
| closure | closure-pointer-above-newest | `closure-stale` | yes |
| flip | flip-true-to-false | `flipped` | yes |
| flip | flip-unchanged | `not-flipped` | yes |
| flip | flip-busy-unchanged | `not-flipped` | yes |
| flip | flip-busy-to-false | `flipped` | yes |
| flip | flip-base-false | `base-false` | yes |
| flip | flip-base-undeclared-busy | `base-host-busy` | yes |
| flip | printer-not-accepted | `printer-not-accepted` | yes |
| flip | printer-real-regression-fails | `no-working-regression` | yes |
| flip | printer-regression-inapplicable | `regress-inapplicable` | yes |
| flip | printer-still-true-after-regression | `not-flipped` | yes |
| flip | printer-that-flips-is-not-rejected | `printer-sensitive` | yes |
| gate | gate-covered | `covered` | yes |
| gate | gate-mismatches | `mismatches` | yes |
| gate | gate-pinned | `pinned` | yes |
| gate | gate-deps_pinned | `deps_pinned` | yes |
| gate | gate-regress_flipped | `regress_flipped` | yes |
| gate | gate-printers_rejected | `printers_rejected` | yes |
| gate | gate-idle_ok | `idle_ok` | yes |
| gate | gate-work_reuse_refused | `work_reuse_refused` | yes |
| gate | gate-closure_ptr | `closure_ptr` | yes |
| gate | gate-recon_mismatches | `recon_mismatches` | yes |
| gate | gate-tally_disclosed | `tally_disclosed` | yes |
| gate | gate-tally_selftest | `tally_selftest` | yes |
| gate | gate-sens_selftest | `sens_selftest` | yes |
| gate | gate-errors | `errors` | yes |
| gate | gate-recon-unknown | `recon_mismatches` | yes |
| gate | gate-population | `population` | yes |
| idle | busy-invented-set | `intersection-not-seen` | yes |
| idle | busy-standing-pid-omitted | `intersection-not-seen` | yes |
| idle | busy-empty-set | `seen-empty` | yes |
| idle | busy-no-host-idle | `no-host-idle` | yes |
| idle | busy-host-idle-ok | `no-host-idle` | yes |
| idle | busy-no-receipt | `no-receipt` | yes |
| idle | busy-wrong-error | `receipt-error` | yes |
| idle | busy-ran-a-cell | `receipt-error` | yes |
| idle | busy-exit-0 | `rc` | yes |
| idle | busy-text-missing | `text` | yes |
| idle | idle-exit-1 | `rc-or-pattern` | yes |
| idle | idle-pattern-missing | `rc-or-pattern` | yes |
| idle | idle-pattern-only | `no-receipt` | yes |
| idle | idle-zero-cells | `idle-cells` | yes |
| idle | idle-unobserved | `idle-cells` | yes |
| idle | idle-cells-zero-observed-one | `idle-cells` | yes |
| idle | idle-ports-open | `idle-cells` | yes |
| idle | idle-exit-code-in-receipt | `idle-cells` | yes |
| idle | idle-errored | `idle-cells` | yes |
| idle | idle-host-not-ok | `idle-host` | yes |
| idle | idle-foreign-pids-seen | `idle-host` | yes |
| pattern | eol-anchor-digest | `pattern-or-rc` | yes |
| pattern | eol-anchor-trailing-text | `pattern-or-rc` | yes |
| pattern | selftest-prefix-only | `pattern-or-rc` | yes |
| pattern | selftest-count-short | `pattern-or-rc` | yes |
| pattern | dead-tool | `dead` | yes |
| pins | pin-tool-edit | `pin` | yes |
| pins | pin-reconciler-edit | `pin` | yes |
| pins | pin-absent | `pin-absent` | yes |
| pins | pin-table-short | `pin-table` | yes |
| pins | dep-edit | `pin` | yes |
| printer | decoy-printers | `not-flipped` | yes |
| printer | plain-printers | `regress-inapplicable` | yes |
| reconciler | recon-exit-1-with-zero | `exit-or-met` | yes |
| reconciler | recon-no-count | `nocount` | yes |
| reconciler | recon-crash-silent | `nocount` | yes |
| reconciler | recon-count-nonzero | `nonzero` | yes |
| reconciler | recon-met-false-zero | `exit-or-met` | yes |
| reconciler | planted-no-count | `planted-nocount` | yes |
| reconciler | planted-fixed-fails | `planted-fixed-fails` | yes |
| reconciler | planted-stale-passes | `planted-stale-passes` | yes |
| reconciler | planted-no-increase | `planted-no-increase` | yes |
| reconciler | planted-no-detail | `planted-no-detail` | yes |
| reconciler | planted-detail-on-fixed | `planted-no-detail` | yes |
| registry | drop | `covered` | yes |
| registry | rename | `unbound-cap` | yes |
| registry | binding | `binding` | yes |
| registry | verdict-value | `verdict-value` | yes |
| registry | quote-prefix | `quote` | yes |
| registry | quote-short | `quote` | yes |
| registry | quote-empty | `quote` | yes |
| registry | free | `binding` | yes |
| registry | weak-pattern | `pattern` | yes |
| registry | hostbusy-undeclared | `hostbusy-not-declared` | yes |
| registry | outcomes-forged | `outcomes` | yes |
| registry | dup-identical | `dup-row` | yes |
| registry | dup-conflict | `dup-row` | yes |
| registry | run-tamper | `run` | yes |
| registry | observed-forged | `mismatch` | yes |
| registry | observed-blank | `mismatch` | yes |
| registry | observed-fragment | `mismatch` | yes |
| regress | find-twice | `regress-inapplicable` | yes |
| regress | find-absent | `regress-inapplicable` | yes |
| regress | noop-regression | `regress-noop` | yes |
| regress | syntax-break | `regress-syntax` | yes |
| regress | missing-row | `regress-missing` | yes |
| regress | duplicate-row | `regress-dup` | yes |
| regress | wrong-tool-path | `regress-path` | yes |
| regress | unbound-cap | `regress-unbound` | yes |
| regress | multiline-find | `regress-multiline` | yes |
| regress | multiline-replace | `regress-multiline` | yes |
| regress | harmless-regression | `not-flipped` | yes |
| selftest | sens-insensitive-verdicts | `sens-selftest` | yes |
| tally | tally-all-no-disclosure | `tally-undisclosed` | yes |
| tally | tally-one-no-disclosure | `tally-undisclosed` | yes |
| tally | tally-unreadable | `tally-undisclosed` | yes |
| tally | tally-round-missing | `tally-undisclosed` | yes |
| tally | tally-no-records | `tally-undisclosed` | yes |
| tally | tally-fixture-relabelled | `fixture` | yes |
| tally | tally-fixture-unreadable | `fixture` | yes |
| tally | tally-fixture-none | `fixture` | yes |
| work | empty-tip-dir | `work-reused` | yes |
| work | run-dir-only | `work-reused` | yes |
| work | second-run-same-work | `work-reused` | yes |
