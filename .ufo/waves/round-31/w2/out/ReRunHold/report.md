# ReRunHold — round-30 hold re-run at the round-31 landing tip

```RESULTS
$ git clone /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/ReRunHold/clone
exit 0
Cloning into '/tmp/kama-r31w2/ReRunHold/clone'...
done.

$ git -C /tmp/kama-r31w2/ReRunHold/clone checkout 382d11b2107d335705875da1a4d889b074bd6fa6 && git -C /tmp/kama-r31w2/ReRunHold/clone rev-parse HEAD
exit 0
HEAD is now at 382d11b round-31: SOURCES repair — S180-S191 relocated into ## Registry (census E12 exit 1 -> exit 0), lesson Mistakes row 4, census start/end receipts, two late seat artifacts
382d11b2107d335705875da1a4d889b074bd6fa6

$ sha256sum .ufo/waves/round-30/count-c1.py   (cwd: /tmp/kama-r31w2/ReRunHold/clone)
exit 0
c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d  .ufo/waves/round-30/count-c1.py
(matches preregistration.json hold_check pin c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d)

$ /usr/bin/python3 .ufo/waves/round-30/count-c1.py --repo /tmp/kama-r31w2/ReRunHold/clone --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out /tmp/kama-r31w2/ReRunHold/hold.json   (cwd: /tmp/kama-r31w2/ReRunHold/clone)
exit 0
stdout (verbatim, complete — the counter's single summary line):
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 13 false_corrections 0 unresolved 0 met True tip 382d11b2107d
stderr: empty

$ /usr/bin/python3 -c '<dump receipt fields>'   (inspection of hold.json)
exit 0
append_only = True
base = 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d
by_class = {'C': 62, 'H': 13, 'N': 2, 'P': 12, 'Q': 44, 'T': 8}
correction_rows = 13
counter = kama round-30 count-c1 v1
counter_sha256 = c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d
extracted = 69
false_corrections = []
met = True
mismatched_at_base = 13
mismatches = <13 items>
oracle_bound = 72
oracle_items = 72
oracle_paths = ['.ufo/waves/round-29/w1/out/RecallA/missed.json', '.ufo/waves/round-29/w1/out/RecallB/missed.json']
oracle_unbound = 0
oracle_unbound_items = []
statements = 141
target = mismatched_at_base == 13 and unresolved == 0 and oracle_items == 72 and oracle_unbound == 0 and append_only
tip = 382d11b2107d335705875da1a4d889b074bd6fa6
unresolved = 0
unresolved_ids = []
valid_corrections = 13
```

FINDING: The round-30 frozen counter (sha256 verified `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`) still reads `met True` with `unresolved 0` at the round-31 landing tip `382d11b2107d` — exit 0, `statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 13 false_corrections 0`. Against the committed receipt `.ufo/waves/round-31/c1/hold-r30.out` (run at the round-31 base `0e6f8ed6891c`), the summaries are **not byte-identical**; exactly ONE field differs: `tip 0e6f8ed6891c` → `tip 382d11b2107d`. Every count field — statements, extracted, oracle, bound, unbound, mismatched_at_base, append_only, valid_corrections, false_corrections, unresolved, met — is identical. The committed receipt's `Command:` line also shows the earlier attempt ran the same counter under the name `count-c1-r30.py` with `--repo . --tip 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e`; my run used the tracked path and the landing tip per this item's assignment. The hold claim — round-31 additions did not break the round-30 self-assessment census — is corroborated at the landing tip: the appended Round-31 corrections section did not disturb append_only, no new false correction rows entered the round-29/30 headings, and all 13 base mismatches remain validly corrected.

LIMITS:
- The run re-derives the frozen counter's bounded check only; it does not establish that the round-30 extractor's 141-statement population is complete, nor validate the truth of the underlying statements.
- `append_only` is a byte-prefix test on SCORECARD.md; it does not detect in-place edits to other files (SHONEN.md is extracted at base only, corrections at tip only for the two named headings).
- The hold exercises the counter against committed git objects only; it says nothing about files untracked at the tip or about counters of other rounds.
- Receipt comparison is field-by-field against the `.out` wrapper's `Summary:` line; the committed JSON receipt from the base-tip run was not available for a full JSON diff (only its summary line was committed).
- No installs or tool changes were needed; /usr/bin/python3 and /usr/bin/git on the host sufficed.
```

Raw receipts saved beside this report: `hold.json` (full counter receipt), `run.stdout`, `run.stderr`.
