# rev=b06cc612711560c53eef3ec21484c6963601262f
# CR01Falsify — round 76 do-nothing controls

Axes: operability (C1), calibration (C2), freshness (C3). Review only; no admission, integration, or rule changes.

## Method and provenance

Read the complete frozen plan at freeze 1a85a991fce5b76b60f88a5cab3df98d253b1a4a. All populations and Git derivations below use immutable base b06cc612711560c53eef3ec21484c6963601262f. C1 uses the committed round72 counter as the expressly allowed closest substitute. C2/C3 use the newly authored round76 modules, not falsely represented as committed at the freeze; reviewed snapshots were selfrecord-facts #0564 and append-exempt #A95E. Their frozen predicates remain the authority. Control drivers call the real grading functions; the printed per-control exit is the grading result, whereas process_exit=0 is the driver's successful completion. C1 and C2 overlay only self-record input bytes in memory; historical blobs and graph derivations remain real Git reads. This avoids all Git mutations and does not alter any lane record. No tools installed.

Every command receipt is pasted in full below, including the command and exit. Driver source is retained here because scratch is deleted. C3 input audit was produced by `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --to b06cc612711560c53eef3ec21484c6963601262f --json`, exit 1 (expected audit findings); its stdout JSON is the input to C3. The drivers and receipt capture run with cwd /fast/scratch/hyaku/kama-r76/CR01Falsify, never the fleet root. Capture prepends the revision and command; the remainder is command stdout/stderr unchanged, followed by process_exit.

## C1 — fence stripping is necessary but insufficient

Counterfactual: strip fenced bodies, retain the same receipt files and revisions, then merely admit PROVINCE.md in a scope file. Original and PROVINCE-only readings still hit the fenced build-spec.py and exit 2, so they cannot establish nonreceipt=0. The substitute reports unreadability rather than a numeric nonreceipt field; do not misread that as zero. Fence stripping reaches cited=11, bound=6, unbound=2, shifted=3, stale=0, exit 1, exactly matching the frozen dryrun. Stripping everything destroys the required section and exits 2, not success.

Stronger counterexample: after adding *all* declared self-description paths (PROVINCE.md, SKILL.md, corpus/**), the same three receipts remain shifted: their recorded revision predates b8ed256829589a13a0ba2249a8ae9e2b8800fb5a's registry/append-only-contract.tsv edit. Read-only `git show --format=fuller --stat b8ed256829589a13a0ba2249a8ae9e2b8800fb5a -- registry/append-only-contract.tsv` exited 0 and reported one insertion and one deletion (commit subject: bind the SCORECARD exempt region to its own declaration line). The frozen predicate expressly says registry deltas still shift.

Reachability: none of the skip-work controls reaches the target. More importantly, the frozen bound=9 shifted=0 target is inconsistent with these unchanged receipt revisions and the frozen registry-delta rule. This falsifies the assertion that the *declared scope expansion alone* resolves all three shifts; it does not demonstrate a do-nothing success. Smallest safe correction: preserve shifted findings, report this freeze disagreement, and define any different target/provenance treatment in a later claim. Do not silently whitelist registry changes or rewrite old receipt revision headers.

### C1 command + full output + exit

```text
# rev=b06cc612711560c53eef3ec21484c6963601262f
# cmd: python3 /fast/scratch/hyaku/kama-r76/CR01Falsify/c1.py
CONTROL mode=original scope=base
RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.py): .ufo/waves/round-75/controls/build-spec.py (corpus/lessons/round-75.md:125)
exit=2
CONTROL mode=fences scope=base
RECEIPT_TIP_FINDING unbound .ufo/waves/round-75/assimilation/summary.out :: no tip=/rev= header among the first 5 lines
RECEIPT_TIP_FINDING unbound .ufo/waves/round-75/controls/freeze.txt :: no tip=/rev= header among the first 5 lines
RECEIPT_TIP_FINDING shifted .ufo/waves/round-75/measured/before/c1-mutants.out :: PROVINCE.md touched by c9ab73d84205
RECEIPT_TIP_FINDING shifted .ufo/waves/round-75/measured/before/c2-mutants.out :: PROVINCE.md touched by c9ab73d84205
RECEIPT_TIP_FINDING shifted .ufo/waves/round-75/measured/before/c3-audit.out :: PROVINCE.md touched by c9ab73d84205
RECEIPT_TIP_BINDING round=75 cited=11 bound=6 unbound=2 shifted=3 stale=0
exit=1
CONTROL mode=original scope=province
RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.py): .ufo/waves/round-75/controls/build-spec.py (corpus/lessons/round-75.md:125)
exit=2
CONTROL mode=fences scope=province
RECEIPT_TIP_FINDING unbound .ufo/waves/round-75/assimilation/summary.out :: no tip=/rev= header among the first 5 lines
RECEIPT_TIP_FINDING unbound .ufo/waves/round-75/controls/freeze.txt :: no tip=/rev= header among the first 5 lines
RECEIPT_TIP_FINDING shifted .ufo/waves/round-75/measured/before/c1-mutants.out :: registry/append-only-contract.tsv touched by b8ed25682958
RECEIPT_TIP_FINDING shifted .ufo/waves/round-75/measured/before/c2-mutants.out :: registry/append-only-contract.tsv touched by b8ed25682958
RECEIPT_TIP_FINDING shifted .ufo/waves/round-75/measured/before/c3-audit.out :: registry/append-only-contract.tsv touched by b8ed25682958
RECEIPT_TIP_BINDING round=75 cited=11 bound=6 unbound=2 shifted=3 stale=0
exit=1
CONTROL mode=fences scope=declared
RECEIPT_TIP_FINDING unbound .ufo/waves/round-75/assimilation/summary.out :: no tip=/rev= header among the first 5 lines
RECEIPT_TIP_FINDING unbound .ufo/waves/round-75/controls/freeze.txt :: no tip=/rev= header among the first 5 lines
RECEIPT_TIP_FINDING shifted .ufo/waves/round-75/measured/before/c1-mutants.out :: registry/append-only-contract.tsv touched by b8ed25682958
RECEIPT_TIP_FINDING shifted .ufo/waves/round-75/measured/before/c2-mutants.out :: registry/append-only-contract.tsv touched by b8ed25682958
RECEIPT_TIP_FINDING shifted .ufo/waves/round-75/measured/before/c3-audit.out :: registry/append-only-contract.tsv touched by b8ed25682958
RECEIPT_TIP_BINDING round=75 cited=11 bound=6 unbound=2 shifted=3 stale=0
exit=1
CONTROL mode=all scope=base
RECEIPT_TIP_BINDING_UNREADABLE SCORECARD.md at b06cc612711560c53eef3ec21484c6963601262f carries no '## Round 75' section; the round's self-record cannot be read
exit=2

process_exit=0
```

## C2 — prose and identity relabelling do not correct facts

Counterfactual 1: append a dated province-digest correction naming the superseded digest but saying only “The values changed.” The fixture is a real scratch SCORECARD text overlaid at the immutable base; it supplies no Revision or Corrected value. It remains mismatches=5 unbacked=1 corrected=0, exit 1, explicitly province-digest wrong-value. The known true digest is still derived from c9ab73d842051db5f8320bced4357bf13cf14108, not from the appended prose.

Counterfactual 2: replace the LOG work-tip token with ba9f724800b7385fc3b732924ffebd143344367d, the actual commit introducing that LOG sentence (read-only git log -G in the driver). Fact id **log-worktip** refuses it: filed=ba9f7248… derived=c9ab73d8…, exit 1. The rule is worktip(): find the oldest introduction of the round75 outside-closure path, traverse first-parent commits after the LOG freeze through that boundary newest-first, and select the first commit touching a non-record path. record_path() does not treat PROVINCE.md as record-only. Thus identity comes from the graph and changed paths, not whatever token the LOG asserts. Correction parsing also requires a dated appended block, superseded bytes/locator, a valid evidence revision, and a re-derived corrected value.

Reachability: these do-nothing controls cannot reach the target; valid value-bound evidence is necessary for correction credit. No C2 falsification found in the assigned controls. This is a necessity observation, not an assertion that the complete target was exercised successfully.

### C2 command + full output + exit

```text
# rev=b06cc612711560c53eef3ec21484c6963601262f
# cmd: python3 /fast/scratch/hyaku/kama-r76/CR01Falsify/c2.py
CONTROL base record_commit=ba9f724800b7385fc3b732924ffebd143344367d
SELFRECORD_FACTS claims=8 mismatches=5 unbacked=1 corrected=0
SELFRECORD_FACT province-digest filed=0e8dc562f99367c3668c5ac2375c49828efa3152aa61fc235f28e896b271b5c4 derived=af459acfa975d418a389f0ce19b8f1f40dd7e08d15c7eb0e9f2eb27e45d45697
SELFRECORD_FACT log-worktip filed=b8ed256829589a13a0ba2249a8ae9e2b8800fb5a derived=c9ab73d842051db5f8320bced4357bf13cf14108
SELFRECORD_FACT log-mistakes filed=4 derived=5
SELFRECORD_FACT log-tally filed=PRE_REPORT_SELFTEST pass=18 fail=0 derived=unbacked
SELFRECORD_CORRECTION log-tally unbacked
SELFRECORD_FACT closure-pointer filed=corpus/lessons/round-74-verifier-spotcheck.md derived=corpus/lessons/round-75-verifier-spotcheck.md
exit=1
CONTROL prose-only record_commit=ba9f724800b7385fc3b732924ffebd143344367d
SELFRECORD_FACTS claims=8 mismatches=5 unbacked=1 corrected=0
SELFRECORD_CORRECTION province-digest wrong-value
SELFRECORD_FACT province-digest filed=0e8dc562f99367c3668c5ac2375c49828efa3152aa61fc235f28e896b271b5c4 derived=af459acfa975d418a389f0ce19b8f1f40dd7e08d15c7eb0e9f2eb27e45d45697
SELFRECORD_FACT log-worktip filed=b8ed256829589a13a0ba2249a8ae9e2b8800fb5a derived=c9ab73d842051db5f8320bced4357bf13cf14108
SELFRECORD_FACT log-mistakes filed=4 derived=5
SELFRECORD_FACT log-tally filed=PRE_REPORT_SELFTEST pass=18 fail=0 derived=unbacked
SELFRECORD_CORRECTION log-tally unbacked
SELFRECORD_FACT closure-pointer filed=corpus/lessons/round-74-verifier-spotcheck.md derived=corpus/lessons/round-75-verifier-spotcheck.md
exit=1
CONTROL relabel-own-record-commit record_commit=ba9f724800b7385fc3b732924ffebd143344367d
SELFRECORD_FACTS claims=8 mismatches=5 unbacked=1 corrected=0
SELFRECORD_FACT province-digest filed=0e8dc562f99367c3668c5ac2375c49828efa3152aa61fc235f28e896b271b5c4 derived=af459acfa975d418a389f0ce19b8f1f40dd7e08d15c7eb0e9f2eb27e45d45697
SELFRECORD_FACT log-worktip filed=ba9f724800b7385fc3b732924ffebd143344367d derived=c9ab73d842051db5f8320bced4357bf13cf14108
SELFRECORD_FACT log-mistakes filed=4 derived=5
SELFRECORD_FACT log-tally filed=PRE_REPORT_SELFTEST pass=18 fail=0 derived=unbacked
SELFRECORD_CORRECTION log-tally unbacked
SELFRECORD_FACT closure-pointer filed=corpus/lessons/round-74-verifier-spotcheck.md derived=corpus/lessons/round-75-verifier-spotcheck.md
exit=1

process_exit=0
```

## C3 — 83 count copies fool a naive counter, not the class/section check

Counterfactual: construct exactly one row per status=ungraded event, copy each event.ungraded count, but perform no class or parent-section derivation. The naive row/count-equality counter accepts: rows=83, copied_lines=126, exit=0. The frozen-rule implementation refuses: wrong-class=83, unaccounted=83, exit 1 (and post-introduction findings). Exact rejecting check: grade(), lines 129–135 in #A95E, requires the event to be ungraded with graded==0, ungraded==deleted, every deleted parent section contract-exempt, class==exempt-head, and the row's section string equal the derived section list. A count copied accurately cannot satisfy these predicates. The count-equality guard at lines 136–139 cannot catch a correctly copied count; claiming wrong-count kills this particular control would be false. The empty-register control also leaves exactly 83 unaccounted, exit 1.

Stronger counterexample: even the module's own class_register(), with derived classes and section strings, leaves exempt=47 unaccounted=36, wrong-class=31, post-introduction=10, exit 1. Audit status=ungraded does **not** imply exempt-head: it includes permitted A-row and only-prefix cases. Also, rows after cutoff 10f37171fb696c542586cbee96ea4a509ab74afc fail ancestry. The frozen motivating “83 events (341 lines) are SCORECARD exempt-head re-derivations” assertion is false: the 83 zero-graded events carry only 126 event.ungraded lines, and include non-SCORECARD files; summary.ungraded_lines=341 also includes ungraded lines in mixed events. Full receipt below names the exact events.

Reachability: do-nothing copying cannot reach the frozen target. The stronger positive-control failure demonstrates that all 83 exemptions cannot be accepted under the frozen universal exempt-head/section and earliest-cutoff restrictions. Smallest safe correction: keep these events unaccounted and report a freeze divergence; a later claim must distinguish permitted/only-prefix/mechanical exemption classes and pre-/post-cutoff populations rather than weakening the check or fabricating head provenance. This is a target-consistency defect, not a successful skip-work attack.

### C3 command + full output + exit

```text
# rev=b06cc612711560c53eef3ec21484c6963601262f
# cmd: python3 /fast/scratch/hyaku/kama-r76/CR01Falsify/c3.py
NAIVE rows=83 copied_lines=126 status_ungraded_lines=126 summary_ungraded_lines=341 exit=0
CONTROL empty
APPEND_EXEMPT events=232 register=53 exempt=0 restored=91 disclosed=5 unaccounted=83 cutoff=10f37171fb696c542586cbee96ea4a509ab74afc introductions=1 rotation_safe=1
APPEND_EXEMPT_FINDING unaccounted 83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 84a81304d7b0c77c84fe495f3bb728e8729faaff SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e246c40ec1b4ba08c36359934f69b8064b7dc54a SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 1e41928aba2b81dd65ea75084918a7fadf453720 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 1e41928aba2b81dd65ea75084918a7fadf453720 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 3285cdf7a50481694a36c4425cf32c915ab5e5f0 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e545ed99aaa519196a2a7779b0a293b2ce4c765c corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 70af36c2b15b46d3b4b3c15ef20459cff640dfaf corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b8e485cc6b201c8e4604a20808e58babbfe08e34 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 726f737a942f1606d66e032f1efbcbb6f689ccf1 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 101f3991d3570bc9350fbf9c5561f4be1185699d corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 5b108c1a7e943c571140df3a1d7e2e29bfdfb501 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted c7311039bcbd76c38b0648d33197864331f34364 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 6433390a5c8f4412c2410c114309ffced5c0572f corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 0df800e896f6bce285a81e794ad4ae1d1e6c3a71 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted f1e755e0bebccec65bbfef5cc8dc0ffce8279f9d corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 92063cfc60e217fa7e2098c568578119b16a1b95 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted fa3b62ae6475d111eb466d79af616aeebb08bbb9 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 382d11b2107d335705875da1a4d889b074bd6fa6 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 4fe239a479bd86478912f3d79d42ec036ac9ae04 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 2793eb5173e35d24538a2832d04883a126634947 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted c8c92db4bdf1c64357b995e0fe8d2a4f481fe995 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 8bc8e37582481a14a59a8c6e1b762f047a40c260 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted dabc6eee2de0e3ecc668b77728186f4a3f592945 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted f1a4ad2a33b4c3dc8d5d583bb36ebd265050fd15 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9307b15e0731f91efbd17ea10ef0d579fc1c9065 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ef76777e5fbdc39a80ec7a93e41dc177366168db corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 0718b6abbda6afa6b0ce586f46739fbb92c7cf9c corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 4991ecc28efa1378f394d267dd67ab0a11c1b976 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 3442d707fdf926ec5ea3f34363cf2f0899cc79b5 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 1541a0dd1628225b838235fe2b7b3d69ad8f50de SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 8370e39cc9a0589b831a724b00e6fa4a6293e52f SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9a3104c771509df2dad6b6fe13c023bd3c472c35 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 1406a91ee01ba4294aa8dd3069476600e7778676 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9c60eae6f7ed84f7da93d219a406aadc30958c6c corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted c2c05e30b80efaf83024f9741380f1839a17edc4 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ec030b36a24fd1aadd7de70cc3b1009c8988aec0 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 750e76b9363bfc679fdf134340675c3c925772b6 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b9d5a091d25676e6c5078d330ebd6abd21a4fc7d SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 7b74e2f2515a6f598918488fa5144658ff29925f SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted bfaea9532e6865dd220579f254d428919b5677f6 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e4891d8a4c9c70e97124980c2ec9aee5762a7f0a SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9e9e3c79800f67794b200ef803e9e312193ff451 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 4e20dfc062a3bad44d99a2122190a7c7c9d45f0e SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 494c165759a644a56ec81bb51a7837b028817d89 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 0e2e4ea18facfacad5b64394820d1611aa25c0ae corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9552e547b6ed099bf8ed607ac250317863662be7 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e7f16ee05ad09906f2ff2283bd32b9a3c8fafbcb SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted dfe42d00923ba6ff63761d3f2e5dd7bf54ec531a SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 286281109b9aced74fa452a8a0ee644bdaf914c0 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ad7f1d6239c7fecf83a9a7a69b0367ad26a894fa SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted dc48ee2e9f454b9caf986d14cf81bbc5be28cae1 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 1106d5295dec99951abaa81da31db8ab3fc49fea SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted bf0db9e3f5059ddf0b557102fa25ea1f32916c46 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e45a4f1b1720482dba7c27077cce4d7a65acc285 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 121e708ad891c5f20d1627ce163c0a32cc509393 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 910e674793e87929a9584791786b61dd0ee75db3 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted af6eb6c29d782f9376036844d38ee0e1e6f20bad SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e2b860c8907a4ba122dbbf5f2b2188695fb7c5f5 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 7c8350f3ca5495e1203ba5ceb6fcbbc43367d193 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 7c8350f3ca5495e1203ba5ceb6fcbbc43367d193 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 7d588685d27d62c14f4a336c3a1a018cf61594c0 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted d843bbf8ee58bc1cef154b92fa6592aafd6ae10c SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted da97596dc213693a88b7792f6e53d9da9836a287 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b421d33274226746009574b864e89019b4afdf08 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 8798cbb9a794047d612e8da555f3697b93bbd2e8 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e9c415545a6a6ebef310d0f90b965487165aa3f7 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e9c415545a6a6ebef310d0f90b965487165aa3f7 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted bc1918fb7a418a436c91d70a7860d2e1493e330d SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b11fb5c3962c466fe6b5501741950c1798495f6e SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted f97ef674b58adb734f5169311bec70941197457a SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted f5d3764081c3240d3b9b2514b010a7c81a6fe785 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted f54b47090929ac350370599c62f0f9dc68f1ec18 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ba9f724800b7385fc3b732924ffebd143344367d SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 900e31b762d51b155fe79f2ef689ca52143e391e SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 11c08bdc0064b9566dc220821db8b9116c6cf788 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b919f0cb35f40e444899b8de70ea79b813ece678 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ac1c8538e391bb76cf1118da10d375b95cc4c1e9 SCORECARD.md missing valid exempt row
finding_counts={'unaccounted': 83}
exit=1
CONTROL count-copy
APPEND_EXEMPT events=232 register=53 exempt=0 restored=91 disclosed=5 unaccounted=83 cutoff=10f37171fb696c542586cbee96ea4a509ab74afc introductions=1 rotation_safe=0
APPEND_EXEMPT_FINDING wrong-class 83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 corpus/knowledge/consumer-registry.md
APPEND_EXEMPT_FINDING wrong-class ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 corpus/knowledge/consumer-registry.md
APPEND_EXEMPT_FINDING wrong-class 84a81304d7b0c77c84fe495f3bb728e8729faaff SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class e246c40ec1b4ba08c36359934f69b8064b7dc54a SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 1e41928aba2b81dd65ea75084918a7fadf453720 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 1e41928aba2b81dd65ea75084918a7fadf453720 corpus/knowledge/consumer-registry.md
APPEND_EXEMPT_FINDING wrong-class 3285cdf7a50481694a36c4425cf32c915ab5e5f0 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class e545ed99aaa519196a2a7779b0a293b2ce4c765c corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 70af36c2b15b46d3b4b3c15ef20459cff640dfaf corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class b8e485cc6b201c8e4604a20808e58babbfe08e34 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 726f737a942f1606d66e032f1efbcbb6f689ccf1 corpus/knowledge/consumer-registry.md
APPEND_EXEMPT_FINDING wrong-class c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 101f3991d3570bc9350fbf9c5561f4be1185699d corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 5b108c1a7e943c571140df3a1d7e2e29bfdfb501 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class c7311039bcbd76c38b0648d33197864331f34364 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 6433390a5c8f4412c2410c114309ffced5c0572f corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 0df800e896f6bce285a81e794ad4ae1d1e6c3a71 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class f1e755e0bebccec65bbfef5cc8dc0ffce8279f9d corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 92063cfc60e217fa7e2098c568578119b16a1b95 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class fa3b62ae6475d111eb466d79af616aeebb08bbb9 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 382d11b2107d335705875da1a4d889b074bd6fa6 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 4fe239a479bd86478912f3d79d42ec036ac9ae04 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 2793eb5173e35d24538a2832d04883a126634947 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class c8c92db4bdf1c64357b995e0fe8d2a4f481fe995 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 8bc8e37582481a14a59a8c6e1b762f047a40c260 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class dabc6eee2de0e3ecc668b77728186f4a3f592945 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class f1a4ad2a33b4c3dc8d5d583bb36ebd265050fd15 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 9307b15e0731f91efbd17ea10ef0d579fc1c9065 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class ef76777e5fbdc39a80ec7a93e41dc177366168db corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 0718b6abbda6afa6b0ce586f46739fbb92c7cf9c corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 4991ecc28efa1378f394d267dd67ab0a11c1b976 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 3442d707fdf926ec5ea3f34363cf2f0899cc79b5 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 1541a0dd1628225b838235fe2b7b3d69ad8f50de SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 8370e39cc9a0589b831a724b00e6fa4a6293e52f SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 9a3104c771509df2dad6b6fe13c023bd3c472c35 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 1406a91ee01ba4294aa8dd3069476600e7778676 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 9c60eae6f7ed84f7da93d219a406aadc30958c6c corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class c2c05e30b80efaf83024f9741380f1839a17edc4 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class ec030b36a24fd1aadd7de70cc3b1009c8988aec0 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 750e76b9363bfc679fdf134340675c3c925772b6 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class b9d5a091d25676e6c5078d330ebd6abd21a4fc7d SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 7b74e2f2515a6f598918488fa5144658ff29925f SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class bfaea9532e6865dd220579f254d428919b5677f6 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class e4891d8a4c9c70e97124980c2ec9aee5762a7f0a SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 9e9e3c79800f67794b200ef803e9e312193ff451 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 4e20dfc062a3bad44d99a2122190a7c7c9d45f0e SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 494c165759a644a56ec81bb51a7837b028817d89 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 0e2e4ea18facfacad5b64394820d1611aa25c0ae corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 9552e547b6ed099bf8ed607ac250317863662be7 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class e7f16ee05ad09906f2ff2283bd32b9a3c8fafbcb SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class dfe42d00923ba6ff63761d3f2e5dd7bf54ec531a SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 286281109b9aced74fa452a8a0ee644bdaf914c0 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class ad7f1d6239c7fecf83a9a7a69b0367ad26a894fa SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class dc48ee2e9f454b9caf986d14cf81bbc5be28cae1 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 1106d5295dec99951abaa81da31db8ab3fc49fea SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class bf0db9e3f5059ddf0b557102fa25ea1f32916c46 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class e45a4f1b1720482dba7c27077cce4d7a65acc285 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 121e708ad891c5f20d1627ce163c0a32cc509393 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 910e674793e87929a9584791786b61dd0ee75db3 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class af6eb6c29d782f9376036844d38ee0e1e6f20bad SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class e2b860c8907a4ba122dbbf5f2b2188695fb7c5f5 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 7c8350f3ca5495e1203ba5ceb6fcbbc43367d193 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 7c8350f3ca5495e1203ba5ceb6fcbbc43367d193 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 7d588685d27d62c14f4a336c3a1a018cf61594c0 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class d843bbf8ee58bc1cef154b92fa6592aafd6ae10c SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class da97596dc213693a88b7792f6e53d9da9836a287 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class b421d33274226746009574b864e89019b4afdf08 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 8798cbb9a794047d612e8da555f3697b93bbd2e8 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class e9c415545a6a6ebef310d0f90b965487165aa3f7 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class e9c415545a6a6ebef310d0f90b965487165aa3f7 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class bc1918fb7a418a436c91d70a7860d2e1493e330d SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class b11fb5c3962c466fe6b5501741950c1798495f6e SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class f97ef674b58adb734f5169311bec70941197457a SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class f5d3764081c3240d3b9b2514b010a7c81a6fe785 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class f54b47090929ac350370599c62f0f9dc68f1ec18 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class ba9f724800b7385fc3b732924ffebd143344367d SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 900e31b762d51b155fe79f2ef689ca52143e391e SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class 11c08bdc0064b9566dc220821db8b9116c6cf788 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class b919f0cb35f40e444899b8de70ea79b813ece678 SCORECARD.md
APPEND_EXEMPT_FINDING wrong-class ac1c8538e391bb76cf1118da10d375b95cc4c1e9 SCORECARD.md
APPEND_EXEMPT_FINDING post-introduction ba9f724800b7385fc3b732924ffebd143344367d SCORECARD.md younger than cutoff 10f37171fb696c542586cbee96ea4a509ab74afc
APPEND_EXEMPT_FINDING post-introduction 900e31b762d51b155fe79f2ef689ca52143e391e SCORECARD.md younger than cutoff 10f37171fb696c542586cbee96ea4a509ab74afc
APPEND_EXEMPT_FINDING post-introduction 11c08bdc0064b9566dc220821db8b9116c6cf788 SCORECARD.md younger than cutoff 10f37171fb696c542586cbee96ea4a509ab74afc
APPEND_EXEMPT_FINDING post-introduction b919f0cb35f40e444899b8de70ea79b813ece678 SCORECARD.md younger than cutoff 10f37171fb696c542586cbee96ea4a509ab74afc
APPEND_EXEMPT_FINDING post-introduction ac1c8538e391bb76cf1118da10d375b95cc4c1e9 SCORECARD.md younger than cutoff 10f37171fb696c542586cbee96ea4a509ab74afc
APPEND_EXEMPT_FINDING unaccounted 83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 84a81304d7b0c77c84fe495f3bb728e8729faaff SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e246c40ec1b4ba08c36359934f69b8064b7dc54a SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 1e41928aba2b81dd65ea75084918a7fadf453720 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 1e41928aba2b81dd65ea75084918a7fadf453720 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 3285cdf7a50481694a36c4425cf32c915ab5e5f0 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e545ed99aaa519196a2a7779b0a293b2ce4c765c corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 70af36c2b15b46d3b4b3c15ef20459cff640dfaf corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b8e485cc6b201c8e4604a20808e58babbfe08e34 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 726f737a942f1606d66e032f1efbcbb6f689ccf1 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 101f3991d3570bc9350fbf9c5561f4be1185699d corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 5b108c1a7e943c571140df3a1d7e2e29bfdfb501 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted c7311039bcbd76c38b0648d33197864331f34364 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 6433390a5c8f4412c2410c114309ffced5c0572f corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 0df800e896f6bce285a81e794ad4ae1d1e6c3a71 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted f1e755e0bebccec65bbfef5cc8dc0ffce8279f9d corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 92063cfc60e217fa7e2098c568578119b16a1b95 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted fa3b62ae6475d111eb466d79af616aeebb08bbb9 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 382d11b2107d335705875da1a4d889b074bd6fa6 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 4fe239a479bd86478912f3d79d42ec036ac9ae04 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 2793eb5173e35d24538a2832d04883a126634947 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted c8c92db4bdf1c64357b995e0fe8d2a4f481fe995 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 8bc8e37582481a14a59a8c6e1b762f047a40c260 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted dabc6eee2de0e3ecc668b77728186f4a3f592945 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted f1a4ad2a33b4c3dc8d5d583bb36ebd265050fd15 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9307b15e0731f91efbd17ea10ef0d579fc1c9065 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ef76777e5fbdc39a80ec7a93e41dc177366168db corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 0718b6abbda6afa6b0ce586f46739fbb92c7cf9c corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 4991ecc28efa1378f394d267dd67ab0a11c1b976 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 3442d707fdf926ec5ea3f34363cf2f0899cc79b5 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 1541a0dd1628225b838235fe2b7b3d69ad8f50de SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 8370e39cc9a0589b831a724b00e6fa4a6293e52f SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9a3104c771509df2dad6b6fe13c023bd3c472c35 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 1406a91ee01ba4294aa8dd3069476600e7778676 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9c60eae6f7ed84f7da93d219a406aadc30958c6c corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted c2c05e30b80efaf83024f9741380f1839a17edc4 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ec030b36a24fd1aadd7de70cc3b1009c8988aec0 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 750e76b9363bfc679fdf134340675c3c925772b6 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b9d5a091d25676e6c5078d330ebd6abd21a4fc7d SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 7b74e2f2515a6f598918488fa5144658ff29925f SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted bfaea9532e6865dd220579f254d428919b5677f6 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e4891d8a4c9c70e97124980c2ec9aee5762a7f0a SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9e9e3c79800f67794b200ef803e9e312193ff451 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 4e20dfc062a3bad44d99a2122190a7c7c9d45f0e SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 494c165759a644a56ec81bb51a7837b028817d89 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 0e2e4ea18facfacad5b64394820d1611aa25c0ae corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9552e547b6ed099bf8ed607ac250317863662be7 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e7f16ee05ad09906f2ff2283bd32b9a3c8fafbcb SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted dfe42d00923ba6ff63761d3f2e5dd7bf54ec531a SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 286281109b9aced74fa452a8a0ee644bdaf914c0 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ad7f1d6239c7fecf83a9a7a69b0367ad26a894fa SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted dc48ee2e9f454b9caf986d14cf81bbc5be28cae1 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 1106d5295dec99951abaa81da31db8ab3fc49fea SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted bf0db9e3f5059ddf0b557102fa25ea1f32916c46 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e45a4f1b1720482dba7c27077cce4d7a65acc285 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 121e708ad891c5f20d1627ce163c0a32cc509393 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 910e674793e87929a9584791786b61dd0ee75db3 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted af6eb6c29d782f9376036844d38ee0e1e6f20bad SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e2b860c8907a4ba122dbbf5f2b2188695fb7c5f5 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 7c8350f3ca5495e1203ba5ceb6fcbbc43367d193 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 7c8350f3ca5495e1203ba5ceb6fcbbc43367d193 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 7d588685d27d62c14f4a336c3a1a018cf61594c0 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted d843bbf8ee58bc1cef154b92fa6592aafd6ae10c SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted da97596dc213693a88b7792f6e53d9da9836a287 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b421d33274226746009574b864e89019b4afdf08 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 8798cbb9a794047d612e8da555f3697b93bbd2e8 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e9c415545a6a6ebef310d0f90b965487165aa3f7 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e9c415545a6a6ebef310d0f90b965487165aa3f7 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted bc1918fb7a418a436c91d70a7860d2e1493e330d SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b11fb5c3962c466fe6b5501741950c1798495f6e SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted f97ef674b58adb734f5169311bec70941197457a SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted f5d3764081c3240d3b9b2514b010a7c81a6fe785 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted f54b47090929ac350370599c62f0f9dc68f1ec18 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ba9f724800b7385fc3b732924ffebd143344367d SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 900e31b762d51b155fe79f2ef689ca52143e391e SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 11c08bdc0064b9566dc220821db8b9116c6cf788 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b919f0cb35f40e444899b8de70ea79b813ece678 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ac1c8538e391bb76cf1118da10d375b95cc4c1e9 SCORECARD.md missing valid exempt row
finding_counts={'wrong-class': 83, 'post-introduction': 5, 'unaccounted': 83}
exit=1
CONTROL derived-class-sections
APPEND_EXEMPT events=232 register=53 exempt=47 restored=91 disclosed=5 unaccounted=36 cutoff=10f37171fb696c542586cbee96ea4a509ab74afc introductions=1 rotation_safe=0
APPEND_EXEMPT_FINDING wrong-class 83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 corpus/knowledge/consumer-registry.md
APPEND_EXEMPT_FINDING wrong-class ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 corpus/knowledge/consumer-registry.md
APPEND_EXEMPT_FINDING wrong-class 1e41928aba2b81dd65ea75084918a7fadf453720 corpus/knowledge/consumer-registry.md
APPEND_EXEMPT_FINDING wrong-class 3285cdf7a50481694a36c4425cf32c915ab5e5f0 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class e545ed99aaa519196a2a7779b0a293b2ce4c765c corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 70af36c2b15b46d3b4b3c15ef20459cff640dfaf corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class b8e485cc6b201c8e4604a20808e58babbfe08e34 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 726f737a942f1606d66e032f1efbcbb6f689ccf1 corpus/knowledge/consumer-registry.md
APPEND_EXEMPT_FINDING wrong-class c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 101f3991d3570bc9350fbf9c5561f4be1185699d corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 5b108c1a7e943c571140df3a1d7e2e29bfdfb501 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class c7311039bcbd76c38b0648d33197864331f34364 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 6433390a5c8f4412c2410c114309ffced5c0572f corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 0df800e896f6bce285a81e794ad4ae1d1e6c3a71 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class f1e755e0bebccec65bbfef5cc8dc0ffce8279f9d corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 92063cfc60e217fa7e2098c568578119b16a1b95 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class fa3b62ae6475d111eb466d79af616aeebb08bbb9 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 382d11b2107d335705875da1a4d889b074bd6fa6 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class ef76777e5fbdc39a80ec7a93e41dc177366168db corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 0718b6abbda6afa6b0ce586f46739fbb92c7cf9c corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 9c60eae6f7ed84f7da93d219a406aadc30958c6c corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 750e76b9363bfc679fdf134340675c3c925772b6 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 9e9e3c79800f67794b200ef803e9e312193ff451 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 0e2e4ea18facfacad5b64394820d1611aa25c0ae corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class dc48ee2e9f454b9caf986d14cf81bbc5be28cae1 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class e45a4f1b1720482dba7c27077cce4d7a65acc285 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 121e708ad891c5f20d1627ce163c0a32cc509393 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 910e674793e87929a9584791786b61dd0ee75db3 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class e2b860c8907a4ba122dbbf5f2b2188695fb7c5f5 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class 7c8350f3ca5495e1203ba5ceb6fcbbc43367d193 corpus/SOURCES.md
APPEND_EXEMPT_FINDING wrong-class e9c415545a6a6ebef310d0f90b965487165aa3f7 corpus/SOURCES.md
APPEND_EXEMPT_FINDING post-introduction ba9f724800b7385fc3b732924ffebd143344367d SCORECARD.md
APPEND_EXEMPT_FINDING post-introduction 900e31b762d51b155fe79f2ef689ca52143e391e SCORECARD.md
APPEND_EXEMPT_FINDING post-introduction 11c08bdc0064b9566dc220821db8b9116c6cf788 SCORECARD.md
APPEND_EXEMPT_FINDING post-introduction b919f0cb35f40e444899b8de70ea79b813ece678 SCORECARD.md
APPEND_EXEMPT_FINDING post-introduction ac1c8538e391bb76cf1118da10d375b95cc4c1e9 SCORECARD.md
APPEND_EXEMPT_FINDING post-introduction ba9f724800b7385fc3b732924ffebd143344367d SCORECARD.md younger than cutoff 10f37171fb696c542586cbee96ea4a509ab74afc
APPEND_EXEMPT_FINDING post-introduction 900e31b762d51b155fe79f2ef689ca52143e391e SCORECARD.md younger than cutoff 10f37171fb696c542586cbee96ea4a509ab74afc
APPEND_EXEMPT_FINDING post-introduction 11c08bdc0064b9566dc220821db8b9116c6cf788 SCORECARD.md younger than cutoff 10f37171fb696c542586cbee96ea4a509ab74afc
APPEND_EXEMPT_FINDING post-introduction b919f0cb35f40e444899b8de70ea79b813ece678 SCORECARD.md younger than cutoff 10f37171fb696c542586cbee96ea4a509ab74afc
APPEND_EXEMPT_FINDING post-introduction ac1c8538e391bb76cf1118da10d375b95cc4c1e9 SCORECARD.md younger than cutoff 10f37171fb696c542586cbee96ea4a509ab74afc
APPEND_EXEMPT_FINDING unaccounted 83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 1e41928aba2b81dd65ea75084918a7fadf453720 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 3285cdf7a50481694a36c4425cf32c915ab5e5f0 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e545ed99aaa519196a2a7779b0a293b2ce4c765c corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 70af36c2b15b46d3b4b3c15ef20459cff640dfaf corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b8e485cc6b201c8e4604a20808e58babbfe08e34 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 726f737a942f1606d66e032f1efbcbb6f689ccf1 corpus/knowledge/consumer-registry.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 101f3991d3570bc9350fbf9c5561f4be1185699d corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 5b108c1a7e943c571140df3a1d7e2e29bfdfb501 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted c7311039bcbd76c38b0648d33197864331f34364 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 6433390a5c8f4412c2410c114309ffced5c0572f corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 0df800e896f6bce285a81e794ad4ae1d1e6c3a71 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted f1e755e0bebccec65bbfef5cc8dc0ffce8279f9d corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 92063cfc60e217fa7e2098c568578119b16a1b95 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted fa3b62ae6475d111eb466d79af616aeebb08bbb9 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 382d11b2107d335705875da1a4d889b074bd6fa6 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ef76777e5fbdc39a80ec7a93e41dc177366168db corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 0718b6abbda6afa6b0ce586f46739fbb92c7cf9c corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9c60eae6f7ed84f7da93d219a406aadc30958c6c corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 750e76b9363bfc679fdf134340675c3c925772b6 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 9e9e3c79800f67794b200ef803e9e312193ff451 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 0e2e4ea18facfacad5b64394820d1611aa25c0ae corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted dc48ee2e9f454b9caf986d14cf81bbc5be28cae1 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e45a4f1b1720482dba7c27077cce4d7a65acc285 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 121e708ad891c5f20d1627ce163c0a32cc509393 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 910e674793e87929a9584791786b61dd0ee75db3 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e2b860c8907a4ba122dbbf5f2b2188695fb7c5f5 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 7c8350f3ca5495e1203ba5ceb6fcbbc43367d193 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted e9c415545a6a6ebef310d0f90b965487165aa3f7 corpus/SOURCES.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ba9f724800b7385fc3b732924ffebd143344367d SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 900e31b762d51b155fe79f2ef689ca52143e391e SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted 11c08bdc0064b9566dc220821db8b9116c6cf788 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted b919f0cb35f40e444899b8de70ea79b813ece678 SCORECARD.md missing valid exempt row
APPEND_EXEMPT_FINDING unaccounted ac1c8538e391bb76cf1118da10d375b95cc4c1e9 SCORECARD.md missing valid exempt row
finding_counts={'wrong-class': 31, 'post-introduction': 10, 'unaccounted': 36}
exit=1

process_exit=0
```

## Reproduction drivers

For C3, save the audit command's stdout as audit.json in the same scratch directory first. The drivers create their own fixtures under that scratch path. No clone, git commit, index, or lane mutation is required.

### c1.py

```python
import importlib.util, pathlib, subprocess
R='/home/vgpnk/Projects/shokunin/kama-shokunin'
B='b06cc612711560c53eef3ec21484c6963601262f'
s=importlib.util.spec_from_file_location('base',R+'/tools/round72-receipt-tip-binding.py'); m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
raw=m._blob
# Overlay only self-record bytes at the immutable base; no git writes or new commits.
def strip(data, all_text=False):
    out=[]; active=False
    for line in data.decode().splitlines():
        if line.startswith('```'): active=not active;out.append(line);continue
        if not active and not all_text: out.append(line)
    return ('\n'.join(out)+'\n').encode()
scope_file=pathlib.Path('/fast/scratch/hyaku/kama-r76/CR01Falsify/province-scope.txt')
scope_file.write_text('\n'.join(m.default_record_paths(75)+['PROVINCE.md'])+'\n')
for mode,scope in [('original','base'),('fences','base'),('original','province'),('fences','province'),('fences','declared'),('all','base')]:
    print('CONTROL mode='+mode+' scope='+scope)
    def blob(repo,rev,path):
        data=raw(repo,rev,path)
        if mode!='original' and path in ('SCORECARD.md','corpus/lessons/round-75.md') and rev==B:
            return strip(data,mode=='all')
        return data
    m._blob=blob
    try:
        specs=m.default_record_paths(75) if scope=='base' else scope_file.read_text().splitlines()
        if scope=='declared':specs+=['SKILL.md','corpus/**']
        result=m.audit(R,B,75,specs)
        print(m.render(result));print('exit='+str(result['exit']))
    except m.CouldNotEvaluate as e:
        print('RECEIPT_TIP_BINDING_UNREADABLE '+str(e));print('exit=2')
```

### c2.py

```python
import importlib.util,pathlib
R=pathlib.Path('/home/vgpnk/Projects/shokunin/kama-shokunin');S=pathlib.Path('/fast/scratch/hyaku/kama-r76/CR01Falsify');B='b06cc612711560c53eef3ec21484c6963601262f'
s=importlib.util.spec_from_file_location('facts',R/'tools/round76-selfrecord-facts.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
original=m.text
score=original(R,B,'SCORECARD.md');log=original(R,B,'LOG.md')
record_commit=m.git(R,'log','-1','--format=%H','-G','work tip `b8ed2568',B,'--','LOG.md').decode().strip()
for name,sc,lg in [('base',score,log),('prose-only',score+'\n### Correction (2026-11-04) — province-digest\nSupersedes: 0e8dc562f99367c3668c5ac2375c49828efa3152aa61fc235f28e896b271b5c4\nThe values changed.\n',log),('relabel-own-record-commit',score,log.replace('work tip `b8ed256829589a13a0ba2249a8ae9e2b8800fb5a`','work tip `'+record_commit+'`'))]:
 (S/(name+'-SCORECARD.md')).write_text(sc);(S/(name+'-LOG.md')).write_text(lg)
 def overlay(repo,rev,path):
  if rev==B and path in ('SCORECARD.md','LOG.md'):return sc if path=='SCORECARD.md' else lg
  return original(repo,rev,path)
 m.text=overlay
 print('CONTROL '+name+' record_commit='+record_commit)
 print('exit='+str(m.audit(R,B)))
```

### c3.py

```python
import importlib.util,json,pathlib,collections
R=pathlib.Path('/home/vgpnk/Projects/shokunin/kama-shokunin'); S=pathlib.Path('/fast/scratch/hyaku/kama-r76/CR01Falsify')
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('exempt',R/'tools/round76-append-exempt.py'); a=load('accepted',R/'tools/round75-append-accepted.py');t=load('audit',R/'tools/append-only-audit.py')
d=json.loads((S/'audit.json').read_text());secs=m.exemption_sections(R,d,t);intro=m.introduction_history(R,d['to']);accepted=m.git(R,'show',d['to']+':'+m.ACCEPTED)
rows=[m.HEADER]+['\t'.join([e['commit'],e['file'],'copied-count',str(e['ungraded']),'','counts copied without class/section work']) for e in d['events'] if e['status']=='ungraded']
text='\n'.join(rows)+'\n';(S/'count-copy.tsv').write_text(text)
naive=sum(int(row.split('\t')[3]) for row in rows[1:]);population=[e for e in d['events'] if e['status']=='ungraded'];print('NAIVE rows='+str(len(rows)-1)+' copied_lines='+str(naive)+' status_ungraded_lines='+str(sum(e['ungraded'] for e in population))+' summary_ungraded_lines='+str(d['summary']['ungraded_lines'])+' exit='+str(int(len(rows)-1!=len(population) or any(int(row.split('\t')[3])!=e['ungraded'] for row,e in zip(rows[1:],population)))))
for name,content in [('empty',m.HEADER+'\n'),('count-copy',text),('derived-class-sections',m.class_register(d,secs))]:
 result=m.grade(d,accepted,content,secs,intro,lambda c:m.ancestor(R,c,intro[0]),a)
 print('CONTROL '+name);print(m.render(result));print('finding_counts='+str(dict(collections.Counter(f['class'] for f in result['findings']))));print('exit='+str(m.verdict(result)))
```

## Review self-check

Accuracy 4/5: actual outputs retained; C1 is a committed substitute, not the not-yet-landed scope CLI. Completeness 4/5: all assigned skip-work controls exercised; complete green C2 target not exercised or claimed. Clarity 4/5: long C3 receipt is deliberately unabridged. Actionability 5/5: exact rejection clauses and minimal freeze-safe corrections named. Conciseness 4/5: reproducible source and full receipts add length. Overall 4.2/5. Improvements retained in the report: distinguish necessary work from a proven reachable target; distinguish process exits from grading exits; distinguish working-tree instruments from immutable evidence. Would the user agree: the concrete blockers are exposed rather than turned into a false pass.
