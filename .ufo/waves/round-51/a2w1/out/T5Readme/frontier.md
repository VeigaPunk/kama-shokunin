## Frontier disposition — round 51 (appended)

Round-51 claims were frozen at `804bde75164444bdf0fe6783d7aa45774bf562bd` (the
preregistration's `frozen_at` is six seconds later; see
`.ufo/waves/round-51/freeze/frozen-at-erratum.md`). The build landed at
`138af25b963450b6520794995605fa7dbbcd87e0`; the frozen-counter build receipts were
measured at `73bf2a7a17104a62a3e442912c8776cbd8dedbd5`. A C2 rerun below measures the
integration-working-tree tip `4eca4892acca6ca4072a0a6fad577d0dd78a5dda`. These are
capability-depth claims, not score increases: operability 8 → 8 (C1) and calibration 7
→ 7 (C2). C1's build receipt is not a new run at the later tip; its two subject tools
are unchanged between the measured tip and that tip (the only `tools/`/`registry/` diff
is the digest-ledger scope fix).

**What moved.** The live tool now opens `/proc/<pid>/exe`, fstats and hashes that running
image, and records its path, dev, inode and digest as `server_exe`
(`tools/kama-llamacpp-live.py:730-761,2041-2044`). The replay compares that receipt to
the dev/inode of its `<work>/server/<member>` and the frozen server digest, and records
`own_server` (`tools/kama-live-replay.py:356-372`). Thus the round-50 decoy that exec'd
the host's separate b11909 install no longer matches. The C1 build receipt reports
`bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True`, exit 0; each of the
three witnessed images was the extracted-member inode, recorded in the rerun receipt
(`.ufo/waves/round-51/a2w1/out/T5Readme/c1-build.out:1-13`). Its base control retained
`bind=1` and teardown but had `own=0 newrow=0 met=False`
(`.ufo/waves/round-51/a2w1/out/T5Readme/base.c1.out:1-15`). The replay selftest rejects
an absent record, a different member, and a different digest
(`tools/kama-live-replay.py:500-511`); S499 adds the `proc_pid_exe(5)` source
(`corpus/SOURCES.md:252`).

C2 changes the audit's default threshold from 20 to 1, so every deletion event in a
contracted file reaches the rule; A-row edits are separated as `permitted` only when the
same id remains and all immutable cells match, and disclosures name missing graded line
keys, counts and mechanical classes (`tools/append-only-audit.py:2-26,175,508-539,544,
629,647,669-722,1417`). At the build the frozen C2 counter passed all nine constructed
scenarios and the lane: `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166
met=True`, exit 0 (`.ufo/waves/round-51/a2w1/out/T5Readme/c2-build.out:1-17`). I reran
that counter at `4eca4892acca6ca4072a0a6fad577d0dd78a5dda`; it again returned
`fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`, exit 0
(`.ufo/waves/round-51/a2w1/out/T5Readme/c2-head.out:1-15`). The v6 tool's JSON summary
there was 106 events, 51 disclosed, 19 restored, zero partial/unrestored/regressed or
bad disclosures, 166 disclosed lines, and 58 permitted lines. The real `ed135b3c` LOG
loss is now a seven-line graded event: two lines are held at the tip and five are
explicitly disclosed as `revert`
(`registry/append-only-disclosures.tsv:11-15`; event detail in the C2 receipts).

The A-row exception is not a blanket exemption: 58 changed lines in 17 `corpus/SOURCES.md`
events are permitted; 9 other deleted source-row lines are graded. The default threshold
is not the same as “every line is graded”: 205 lines in 30 events remain ungraded under
the declared regions (186 `SCORECARD.md` exempt-section lines and 19 lines outside
`## Errata` in `corpus/knowledge/consumer-registry.md`). Sixteen additional source-row
events contain only permitted cells. The tool's v5 section/origin and region rules remain
in force (`registry/append-only-contract.tsv:3,10-11`; measured v6 summary in
`.ufo/waves/round-51/a2w1/out/T5Readme/c2-head.out:1-15`).

**What stays frontier.**

- A copy decoy can put byte-identical frozen bytes at `<work>/server/<member>` and exec
  that copy: the witness compares `/proc/<pid>/exe` to `stat()` of that pathname and the
  frozen digest, not the file's history. Whether the replay actually downloaded the
  archive is not observed. Both are explicit C1 limits
  (`.ufo/waves/round-51/preregistration.json:40-42`; counter comparison at
  `tools/round51-replay-exe-audit.py:351-380`).
- The replay's `probe` execution through `PATH` is not independently pinned, and the
  model check still hashes the mapped file through its pathname rather than resident
  pages. An in-place model rewrite after mapping can therefore evade a check that sees
  the original bytes again; pagemap/smaps or a resident-page digest is not measured
  (`tools/round51-replay-exe-audit.py:88`; `tools/kama-llamacpp-live.py:678-727`; round-50
  limits at `corpus/README.md:1336-1357`). C1 also does not exercise kills during
  download or readiness (`preregistration.json:42`).
- The b11909 asset is refetched from GitHub on each replay: deleting or re-uploading the
  prerelease asset can make the replay fail closed, not prove a wrong binary
  (`corpus/README.md:1408-1410`).
- The b11906 ledger population at b11909+ remains carried, not re-measured here (at least
  S107, S130, S132, S113 and S135); likewise S013's re-pin, S022 and unpinned vLLM stable
  pages S002–S004, K05 (declared versus served context), and the registered consumers'
  last admitted sample (`corpus/README.md:1411-1414`).
- For C2's region-restricted contracts, the counter does not independently recompute
  which deleted keys remain lost at the tip. It checks only that each disclosure key
  occurs among that event's deleted keys no more often than deleted; 24 ledger lines for
  `SCORECARD.md` are in this category. The exact lost-key multiset comparison covers
  whole-file (`region=*`) files only (142 lines); the `only=## ...` knowledge entries
  also rely on the tool's section logic (`tools/round51-append-audit-v6-check.py:42-53,
  338-374`; `preregistration.json:44`). The disclosure class and note are mechanical,
  not explanations or judgments (`tools/append-only-audit.py:16-22`).
- Other round-50 limits remain: content-aware eligibility and delete/restore-into-head
  laundering; lexical binding edge cases; position-aware restoration; a pid start-time
  bound for the `child_pid` join; injection channels beyond the two canaries; and signed
  exec/build provenance (`corpus/README.md:1358-1386,1398-1405`). The evidence remains
  three sampled b11909 receipts, one tiny model and an online replay (`:1387-1389`).

Integration (round 51, L1): drafted by wave-1 scribe T5Readme
(`.ufo/waves/round-51/a2w1/out/T5Readme/frontier.md`). The S499 `used-by` names
`corpus/lessons/round-51.md`; that lesson lands at integration.
