# X2Fixture evidence (generated from results.json / lane.json)

tool = `python3 kama-shokunin/tools/append-only-audit.py --repo D --to <tip> --json`
counter = `round46-append-audit-check.py :: recompute(D, <tip>)` (importlib, frozen)
oracle = byte-exact: `git diff -U0` parsed positionally per file section, tip lines from `git cat-file blob` bytes without the phantom trailing empty element

| case | tool rc | tool ev | counter ev | tool vs counter | tool vs oracle | counter vs oracle | both wrong |
|---|---|---|---|---|---|---|---|
| crlf | 0 | 1 | 1 | AGREE | DIFFER | DIFFER | True |
| crlf2 | 0 | 1 | 1 | AGREE | match | match | False |
| cr | 0 | 1 | 1 | AGREE | DIFFER | DIFFER | True |
| nonl | 0 | 1 | 1 | AGREE | match | match | False |
| ws | 1 | 1 | 1 | AGREE | match | match | False |
| dups | 0 | 1 | 1 | AGREE | match | match | False |
| bin | 0 | 0 | 0 | AGREE | match | match | False |
| utf8 | 1 | 0 | 0 | AGREE | DIFFER | DIFFER | True |
| mode | 0 | 0 | 0 | AGREE | match | match | False |
| ren | 0 | 1 | 1 | AGREE | match | match | False |
| merge | 1 | 2 | 2 | AGREE | match | match | False |
| octo | 1 | 1 | 1 | AGREE | match | match | False |
| octo2 | 1 | 2 | 2 | AGREE | match | match | False |
| twice | 1 | 2 | 2 | AGREE | match | match | False |
| large | 1 | 1 | 1 | AGREE | match | match | False |
| blank | 0 | 1 | 1 | AGREE | DIFFER | DIFFER | True |
| trunc | 0 | 1 | 1 | AGREE | DIFFER | DIFFER | True |
| laneblank | 0 | 1 | 1 | AGREE | DIFFER | DIFFER | True |
| dash | 0 | 0 | 0 | AGREE | DIFFER | DIFFER | True |
| dir | 1 | 1 | 1 | DISAGREE | match | DIFFER | False |

## crlf
- expectation: byte-exact: the 25 deleted lines ended CRLF, the tip holds them LF -> unrestored
- fixture note: CRLF deleted at d8a8651dd2e1, re-added LF at 7e79406b0827
- tool rc=0 events=[{"commit": "d8a8651dd2e18f5eac69148f77b79f954b15a763", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": "7e79406b0827520d92c25add9176ce950f916ce5"}]
- counter events=[{"commit": "d8a8651dd2e18f5eac69148f77b79f954b15a763", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": "7e79406b0827520d92c25add9176ce950f916ce5"}]
- oracle events=[{"commit": "d8a8651dd2e18f5eac69148f77b79f954b15a763", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]

## crlf2
- expectation: restored at 39f5e2b097a9
- fixture note: control for the CRLF case
- tool rc=0 events=[{"commit": "d8a8651dd2e18f5eac69148f77b79f954b15a763", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": "39f5e2b097a9532ff163ef5bad283565f46f6a19"}]
- counter events=[{"commit": "d8a8651dd2e18f5eac69148f77b79f954b15a763", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": "39f5e2b097a9532ff163ef5bad283565f46f6a19"}]
- oracle events=[{"commit": "d8a8651dd2e18f5eac69148f77b79f954b15a763", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": "39f5e2b097a9532ff163ef5bad283565f46f6a19"}] binary=[]

## cr
- expectation: byte-exact: 'item NNN\rTAIL' is not 'item NNN' -> unrestored
- fixture note: deleted at 1f3657545277, head-only text restored at cb15cc77483d
- tool rc=0 events=[{"commit": "1f3657545277701b0df6b51893ea6a4d3da807b3", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": "cb15cc77483dd38b974e9f6b42eb48fdb90c97ce"}]
- counter events=[{"commit": "1f3657545277701b0df6b51893ea6a4d3da807b3", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": "cb15cc77483dd38b974e9f6b42eb48fdb90c97ce"}]
- oracle events=[{"commit": "1f3657545277701b0df6b51893ea6a4d3da807b3", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]

## nonl
- expectation: restored at 42e0862090da (text equal; only the final newline differs)
- fixture note: deletion at f297c147001a; the last deleted line carries the no-newline marker
- tool rc=0 events=[{"commit": "f297c147001a17fca5a9001d48e1359606983ab5", "file": "LOG.md", "deleted": 26, "restored_at_tip": 26, "status": "restored", "restored_by": "42e0862090dae2531ac22aa7561a0508898ddc28"}]
- counter events=[{"commit": "f297c147001a17fca5a9001d48e1359606983ab5", "file": "LOG.md", "deleted": 26, "restored_at_tip": 26, "status": "restored", "restored_by": "42e0862090dae2531ac22aa7561a0508898ddc28"}]
- oracle events=[{"commit": "f297c147001a17fca5a9001d48e1359606983ab5", "file": "LOG.md", "deleted": 26, "restored_at_tip": 26, "status": "restored", "restored_by": "42e0862090dae2531ac22aa7561a0508898ddc28"}] binary=[]

## ws
- expectation: unrestored: 'exact text' means the trailing space is a different line
- fixture note: event at 0aa148672da1 has 25 deletions and 25 additions
- tool rc=1 events=[{"commit": "0aa148672da1885ca7ca5c8ea889c171c90e7fc6", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- counter events=[{"commit": "0aa148672da1885ca7ca5c8ea889c171c90e7fc6", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- oracle events=[{"commit": "0aa148672da1885ca7ca5c8ea889c171c90e7fc6", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]

## dups
- expectation: restored per docstring: 'duplicates may share one line'
- fixture note: 25 identical lines deleted at 98be11fc01d1, tip still holds the same text
- tool rc=0 events=[{"commit": "98be11fc01d178c992ea6b2bbbc5ac20e7d04c28", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": null}]
- counter events=[{"commit": "98be11fc01d178c992ea6b2bbbc5ac20e7d04c28", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": null}]
- oracle events=[{"commit": "98be11fc01d178c992ea6b2bbbc5ac20e7d04c28", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": null}] binary=[]

## bin
- expectation: docstring's own definition (deleted = `-` lines of the diff) yields 0 for a binary diff
- fixture note: no textual deletion is observable in git diff for c89f96735dde
- tool rc=0 events=[]
- counter events=[]
- oracle events=[] binary=[['c89f96735ddea99e3040c8582508d8d7a479e815', 'SCORECARD.md']]

## utf8
- expectation: tool contract: exit 2 'could not evaluate' if it cannot decode the blob
- fixture note: event at 958854940a9a, tip blob is invalid UTF-8
- tool rc=1 events=NONE (no JSON)
- counter events=NONE error=UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
- oracle events=[{"commit": "958854940a9a98070f729fb9ffffaf608d6ab46c", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[['3823428ac1b0c4a0c4037860a23f2971d337cd36', 'LOG.md']]
- tool stderr (tail): `line 1221, in communicate`

## mode
- expectation: no event: a mode change deletes no lines
- fixture note: mode-only change at 82dac3a67bea
- tool rc=0 events=[]
- counter events=[]
- oracle events=[] binary=[]

## ren
- expectation: restored at the rename-back commit; the intermediate rename is a 30-line deletion event
- fixture note: rename away at 6ed6b9cc44e2, back at 9d789c10e027
- tool rc=0 events=[{"commit": "6ed6b9cc44e24d8503f25d540b3a47ac0aa43dcc", "file": "LOG.md", "deleted": 30, "restored_at_tip": 30, "status": "restored", "restored_by": "9d789c10e027bd18b4f38bea228330ce1d303f88"}]
- counter events=[{"commit": "6ed6b9cc44e24d8503f25d540b3a47ac0aa43dcc", "file": "LOG.md", "deleted": 30, "restored_at_tip": 30, "status": "restored", "restored_by": "9d789c10e027bd18b4f38bea228330ce1d303f88"}]
- oracle events=[{"commit": "6ed6b9cc44e24d8503f25d540b3a47ac0aa43dcc", "file": "LOG.md", "deleted": 30, "restored_at_tip": 30, "status": "restored", "restored_by": "9d789c10e027bd18b4f38bea228330ce1d303f88"}] binary=[]

## merge
- expectation: the merge is an event against its first parent (25 deleted), status unrestored
- fixture note: merge commit 093bfc670336 deletes 25 lines relative to first parent
- tool rc=1 events=[{"commit": "bfb871d8440eb547724b630386de7032721e9fbf", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": "a34be7db782a7f5570887762f3cf44202115297f"}, {"commit": "093bfc670336b985d77d1c253ba3371c361d0be5", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- counter events=[{"commit": "bfb871d8440eb547724b630386de7032721e9fbf", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": "a34be7db782a7f5570887762f3cf44202115297f"}, {"commit": "093bfc670336b985d77d1c253ba3371c361d0be5", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- oracle events=[{"commit": "bfb871d8440eb547724b630386de7032721e9fbf", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": "a34be7db782a7f5570887762f3cf44202115297f"}, {"commit": "093bfc670336b985d77d1c253ba3371c361d0be5", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]

## octo
- expectation: first-parent diff decides: 30 deleted; the octopus's other parents delete nothing
- fixture note: merge 507d68fbcfc1 parents=['0c3d24d845d3', '27eb69700bd4', 'ecfc7077ace9']
- tool rc=1 events=[{"commit": "507d68fbcfc12194070e7971d9ffc416b66ad674", "file": "LOG.md", "deleted": 30, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- counter events=[{"commit": "507d68fbcfc12194070e7971d9ffc416b66ad674", "file": "LOG.md", "deleted": 30, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- oracle events=[{"commit": "507d68fbcfc12194070e7971d9ffc416b66ad674", "file": "LOG.md", "deleted": 30, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]

## octo2
- expectation: the side deletion is an event at 3c178a7a44af, and the octopus repeats it against its first parent
- fixture note: octopus 194ada65c9a2; the same 25 lines are deleted in two commits
- tool rc=1 events=[{"commit": "3c178a7a44af73cec91ba3d7700f3f7c1af0ba2e", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": "af4960c0eb27af1dae00f6ceb499e761c43c6e10"}, {"commit": "194ada65c9a25af9d8719343831ccd74059d0fa8", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- counter events=[{"commit": "3c178a7a44af73cec91ba3d7700f3f7c1af0ba2e", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": "af4960c0eb27af1dae00f6ceb499e761c43c6e10"}, {"commit": "194ada65c9a25af9d8719343831ccd74059d0fa8", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- oracle events=[{"commit": "3c178a7a44af73cec91ba3d7700f3f7c1af0ba2e", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": "af4960c0eb27af1dae00f6ceb499e761c43c6e10"}, {"commit": "194ada65c9a25af9d8719343831ccd74059d0fa8", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]

## twice
- expectation: two events: f9fefa5e6642 restored by ff1fbb1fb4de; 96b702bff03e unrestored
- fixture note: same-line double deletion
- tool rc=1 events=[{"commit": "f9fefa5e6642b0ba4a4f7297cd73e9ba63a2f3f7", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": "ff1fbb1fb4de3ffb0eecba2679669c460cd593c4"}, {"commit": "96b702bff03e431139ff7edee0743ad4b0cc1009", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- counter events=[{"commit": "f9fefa5e6642b0ba4a4f7297cd73e9ba63a2f3f7", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": "ff1fbb1fb4de3ffb0eecba2679669c460cd593c4"}, {"commit": "96b702bff03e431139ff7edee0743ad4b0cc1009", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- oracle events=[{"commit": "f9fefa5e6642b0ba4a4f7297cd73e9ba63a2f3f7", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": "ff1fbb1fb4de3ffb0eecba2679669c460cd593c4"}, {"commit": "96b702bff03e431139ff7edee0743ad4b0cc1009", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]

## large
- expectation: one unrestored event, deleted=25
- fixture note: 50k-line file, 25 deleted at 1880d8a1aa29
- tool rc=1 events=[{"commit": "1880d8a1aa299a5e15d02eaaa549761566402013", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- counter events=[{"commit": "1880d8a1aa299a5e15d02eaaa549761566402013", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- oracle events=[{"commit": "1880d8a1aa299a5e15d02eaaa549761566402013", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]

## blank
- expectation: unrestored: the tip holds no blank line (split('\n')'s trailing '' is not a line)
- fixture note: 25 empty lines deleted at 456800058fc9; tip has none
- tool rc=0 events=[{"commit": "456800058fc9ffa606698272a8c7ca1c6f96b0b9", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": null}]
- counter events=[{"commit": "456800058fc9ffa606698272a8c7ca1c6f96b0b9", "file": "LOG.md", "deleted": 25, "restored_at_tip": 25, "status": "restored", "restored_by": null}]
- oracle events=[{"commit": "456800058fc9ffa606698272a8c7ca1c6f96b0b9", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]

## trunc
- expectation: unrestored: a 0-byte file holds no lines at all
- fixture note: 30 blank lines deleted at fe9d6fe5a638, tip file is empty
- tool rc=0 events=[{"commit": "fe9d6fe5a638ca7e02f3e610a07bba4d51aacb66", "file": "LOG.md", "deleted": 30, "restored_at_tip": 30, "status": "restored", "restored_by": null}]
- counter events=[{"commit": "fe9d6fe5a638ca7e02f3e610a07bba4d51aacb66", "file": "LOG.md", "deleted": 30, "restored_at_tip": 30, "status": "restored", "restored_by": null}]
- oracle events=[{"commit": "fe9d6fe5a638ca7e02f3e610a07bba4d51aacb66", "file": "LOG.md", "deleted": 30, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]
- tip_bytes: `0`

## laneblank
- expectation: unrestored: every blank line is gone from the audited file
- fixture note: 507 blank lines deleted from a copy of the lane file at 0885e1fdd244
- tool rc=0 events=[{"commit": "0885e1fdd244e8c1e2d37d1a4ffb0a66afa65377", "file": "SCORECARD.md", "deleted": 507, "restored_at_tip": 507, "status": "restored", "restored_by": null}]
- counter events=[{"commit": "0885e1fdd244e8c1e2d37d1a4ffb0a66afa65377", "file": "SCORECARD.md", "deleted": 507, "restored_at_tip": 507, "status": "restored", "restored_by": null}]
- oracle events=[{"commit": "0885e1fdd244e8c1e2d37d1a4ffb0a66afa65377", "file": "SCORECARD.md", "deleted": 507, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]

## dash
- expectation: event with deleted=25: content lines '--x' render as '---x', not as the '---' header
- fixture note: 25 deletions whose diff text starts with '---' at a4e305289a49
- tool rc=0 events=[]
- counter events=[]
- oracle events=[{"commit": "a4e305289a490acdf2f1eb1efebc674a60f29b14", "file": "LOG.md", "deleted": 25, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]
- numstat: `"0\t25\tLOG.md"`
- numstat_patch: `"diff --git a/LOG.md b/LOG.md\nindex 2d7d8eb..76d218d 100644\n--- a/LOG.md\n+++ b/LOG.md\n@@ -6,25 +5,0 @@\n--- dash comment 005\n--- dash comment 006\n--- dash comment 007\n--- dash comment 008\n--- dash comment 009\n--- dash comment 010\n--- dash comment 011\n--- dash comment 012\n--- dash comment 013\n--- dash comment 014\n--- dash comment 015\n--- dash comment 016\n--- dash comment 017\n--- dash comment 018\n--- dash comment 019\n--- dash comment 020\n--- dash comment 021\n--- dash comment 022\n--- dash comment 023\n--- dash comment 024\n--- dash comment 025\n--- dash comment 026\n--- dash comment 027\n--- dash comment 028\n--- dash comment 029\n"`

## dir
- expectation: the tip holds no LOG.md *lines*: unrestored (the path is a tree at tip)
- fixture note: deleted lines include 'child.txt', which is also the child entry name at 491b27e4c18b
- tool rc=1 events=[{"commit": "491b27e4c18bcfdbf22976a8ac4d9157d22fd42f", "file": "LOG.md", "deleted": 30, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}]
- counter events=[{"commit": "491b27e4c18bcfdbf22976a8ac4d9157d22fd42f", "file": "LOG.md", "deleted": 30, "restored_at_tip": 1, "status": "partial", "restored_by": null}]
- oracle events=[{"commit": "491b27e4c18bcfdbf22976a8ac4d9157d22fd42f", "file": "LOG.md", "deleted": 30, "restored_at_tip": 0, "status": "unrestored", "restored_by": null}] binary=[]
- show_tree: `"tree HEAD:LOG.md\n\nchild.txt\n"`

# lane leg (read-only, lane HEAD)
- to=96d329186e777080c03ac89fdd2366714d504dc3 tool_rc=1 counter_error=None tool_vs_counter=AGREE tool_events=5 counter_events=5
- numstat_sweep_events=5 in_counter_not_in_sweep=[] in_sweep_not_in_counter=[] sweep_binary=[]
- tool_secs=0.769 counter_secs=1.762

| event (tool/counter) | byte-exact deleted | byte-exact restored | byte-exact status |
|---|---|---|---|
| dd9f5dc6c0e6 SCORECARD.md deleted=31 restored_at_tip=24 status=partial restored_by=- | 31 | 24 | partial |
| 0718b6abbda6 SCORECARD.md deleted=2417 restored_at_tip=2416 status=partial restored_by=- | 2421 | 2420 | partial |
| 0718b6abbda6 LOG.md deleted=2290 restored_at_tip=2290 status=restored restored_by=82b5e9d33a19 | 2292 | 2292 | restored |
| 0718b6abbda6 corpus/QUALITY.md deleted=375 restored_at_tip=375 status=restored restored_by=82b5e9d33a19 | 375 | 375 | restored |
| 0718b6abbda6 corpus/README.md deleted=663 restored_at_tip=663 status=restored restored_by=82b5e9d33a19 | 663 | 663 | restored |

numstat per (commit,file) on the lane (no diff text involved):
- 0718b6abbda6:LOG.md deleted=2292
- 0718b6abbda6:SCORECARD.md deleted=2421
- 0718b6abbda6:corpus/QUALITY.md deleted=375
- 0718b6abbda6:corpus/README.md deleted=663
- dd9f5dc6c0e6:SCORECARD.md deleted=31
