# ReRunC2 — rerun of the frozen round-31 C2 counter at tip 382d11b2

Claim served: C2 (calibration), the frozen claim-row counter's tip reading.
Seat: leaf member, no subagents. Clone recipe from the sibling w2 seats
(`git clone --no-hardlinks --no-checkout`, then `checkout --detach <tip>`); no ReRunC1
output directory existed at read time, so the recipe was taken from
`w2/out/RevRowA/commands.json` and `w2/out/RevRowB/`, which is identical.

```RESULTS
$ /usr/bin/git -c core.hooksPath=/dev/null clone --no-hardlinks --no-checkout \
    /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/ReRunC2/lane
exit 0
tail: Cloning into '/tmp/kama-r31w2/ReRunC2/lane'...
done.

$ /usr/bin/git -c core.hooksPath=/dev/null -C /tmp/kama-r31w2/ReRunC2/lane \
    checkout -q --detach 382d11b2107d335705875da1a4d889b074bd6fa6 && \
    /usr/bin/git -C /tmp/kama-r31w2/ReRunC2/lane rev-parse HEAD
exit 0
tail: 382d11b2107d335705875da1a4d889b074bd6fa6

$ sha256sum /tmp/kama-r31w2/ReRunC2/lane/.ufo/waves/round-31/count-c2.py
exit 0
tail: 2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe  /tmp/kama-r31w2/ReRunC2/lane/.ufo/waves/round-31/count-c2.py
(matches preregistration.json C2.counter_sha256 exactly)

$ cd /tmp/kama-r31w2/ReRunC2/lane && /usr/bin/python3 .ufo/waves/round-31/count-c2.py \
    --repo /tmp/kama-r31w2/ReRunC2/lane \
    --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out /tmp/kama-r31w2/ReRunC2/c2.json
exit 0
verbatim summary line:
rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip 382d11b2107d
(stderr empty; receipt written to /tmp/kama-r31w2/ReRunC2/c2.json, copied to
w2/out/ReRunC2/c2.json)

$ same counter with --list (second read-only run for the problem/correction listing;
  receipt saved as w2/out/ReRunC2/c2-list.stdout.txt and c2-list.json)
exit 0
tail (verbatim):
rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip 382d11b2107d
  C1 — re-anchor stale source anchors by appended dated corrections (plan claim 1): p1 line 196 p1:no-revision
  C3 — `sources-registry` capability + 3 entries on uncovered ground: p1 line 197 p1:no-revision
  C1: p1 line 266 p1:no-revision
  C2: p1 line 267 p1:no-revision
  C1: p1 line 320 p1:no-revision
  C1: p1 line 379 p1:no-revision
  C1 offline Ollama evidence replay: p1 line 445 p1:no-revision
  C1 declared-name duplicate-corpus admission: p1 line 522 p1:no-revision
  C2 `live-llamacpp-lifecycle`: p1 line 611 p1:no-revision
  C1 graded fields backed by a failing detector: p1 line 680 p1:no-revision
  C2 fail-capable live checks: p1 line 681 p1:no-revision
  C1 — outcome classification and receipt boundary: p1 line 781 p1:no-revision
  C2 — statement→mutant→detector ledger: p1 line 782 p1:no-revision
  corr CR31:10:C1 re-anchor stale source anchors:p1 row=C1 — re-anchor stale source anchors ... class=p1 ok=True
  corr CR31:10:C3 sources-registry:p1 row=C3 — `sources-registry` capability + 3 entries on uncovered ground class=p1 ok=True
  corr CR31:11:C2:p1 row=C2 class=p1 ok=True
  corr CR31:14:C1 Ollama replay:p1 row=C1 offline Ollama evidence replay class=p1 ok=True
  corr CR31:15:C1 duplicate-corpus:p1 row=C1 declared-name duplicate-corpus admission class=p1 ok=True
  corr CR31:16:C2 lifecycle:p1 row=C2 `live-llamacpp-lifecycle` class=p1 ok=True
  corr CR31:17:C1 graded fields:p1 row=C1 graded fields backed by a failing detector class=p1 ok=True
  corr CR31:17:C2 fail-capable checks:p1 row=C2 fail-capable live checks class=p1 ok=True
  corr CR31:18:C1 outcome classification:p1 row=C1 — outcome classification and receipt boundary class=p1 ok=True
  corr CR31:18:C2 ledger:p1 row=C2 — statement→mutant→detector ledger class=p1 ok=True

$ /usr/bin/python3 /tmp/kama-r31w2/ReRunC2/indep.py   # independent re-derivation, full
    output saved verbatim as w2/out/ReRunC2/indep.out
exit 0
tail: tip_bytes 124857 base_bytes 117789 startswith True
      tip_sha256 511b1fd8e979f037b490a5a2e354571c5ae6edbc35b15105574d0a5fcbddc849
      base_sha256 73a3270dc89b529300f73f380a658c42938d58e5dbb44e46ef885162eb000083
      prefix_identical True
      appended_head b'\n## Round 31 \xe2\x80\x94 the chat-completions adapter (depth) and claim-row evidence (calibration)\n\nAuthority: assigned axes ope'
```

## (a) Row census — agrees with `rows 30`

My own table walk (no code shared with the counter; saved as `indep.py`/`indep.out`)
applied the documented population rule — every data row of every tip-tree SCORECARD.md
table whose header's first cell is `claim`, rows under the appended
`## Round 31 — claim-row evidence corrections` section excluded — and counted **30**
rows, agreeing with the counter's `rows 30`. The 30 rows, one per line as
`SCORECARD.md:<line>` (round = nearest preceding `## Round <N>` heading):

```
SCORECARD.md:196,197  round 10  (2 rows)
SCORECARD.md:266,267  round 11  (2)
SCORECARD.md:320      round 12  (1)
SCORECARD.md:379      round 13  (1)
SCORECARD.md:445      round 14  (1)
SCORECARD.md:522      round 15  (1)
SCORECARD.md:610,611  round 16  (2)
SCORECARD.md:680,681  round 17  (2)
SCORECARD.md:781,782  round 18  (2)
SCORECARD.md:900,901  round 20  (2)
SCORECARD.md:1012,1013 round 21 (2)
SCORECARD.md:1079     round 22  (1)
SCORECARD.md:1260,1261 round 25 (2)
SCORECARD.md:1322     round 26  (1)
SCORECARD.md:1369,1370 round 27 (2, incl. exempt `X1 (exploratory)`)
SCORECARD.md:1415     round 28  (1)
SCORECARD.md:1475     round 29  (1)
SCORECARD.md:1537,1538 round 30 (2)
SCORECARD.md:1581,1582 round 31 (2)
```

(The preregistration's surface text says "28 rows over 18 tables, rounds 10-30";
30 here = 28 base rows + the 2 round-31 claim rows appended this round.)

## (b) The three `unresolved` strings

The receipt's `unresolved` field is literally `["C1", "C1", "C1"]` — the Claim-cell
text of three problems with no valid correction. The `--list` run attributes them:

```
SCORECARD.md:266  ## Round 11  | C1 | calibration 7 → 7; delta 0 | nine legacy files: missing fields 27 → 0; ...
SCORECARD.md:320  ## Round 12  | C1 | calibration 7 → 7, delta 0 | One source path: old snapshot mismatch 1 / exit 1 `source_mismatch`; ...
SCORECARD.md:379  ## Round 13  | C1 | calibration 7 → 7, delta 0 | two missing precise assertions → zero; selected before exit 1 `documentation_mismatc...
```

All three are class `p1`, observed `p1:no-revision` (the row text names no
7–40-hex token resolving to a tip ancestor). A **fourth** population row has the
exact Claim cell `C1` — SCORECARD.md:1322 (round 26) — but it resolves through its
`measured commit` cell (`a23c0e04`, `7e5ff9b5`, `1560e4d8` all resolve), so it is
not a problem row and not among the three.

Mechanism, verified against count-c2.py:257–268: `by_key`, `problem_by_key` and
`valid_map` are all keyed by `(row, class)` = (Claim-cell text, failing class).
The three rows collapse onto one key `("C1", "p1")`. The correction table carries
no `C1`-row correction at all (10 rows, `ok=True` each, covering the other 10
problems), so the key is absent from `valid_map` and all three problems count as
unresolved. SCORECARD.md:1634–1638 records the same finding in prose ("Not
expressible under the frozen key ... the counter's `(row, class)` key collapses
them"), and the wave-1 reference arm `.ufo/waves/round-31/controls/RefRepair/receipt.txt`
recorded `valid 10 false 3 unresolved 3` when all thirteen corrections were
appended — the two `("C1","p1")` corrections both went false under the
`len(by_key) == 1` rule.

## (c) `append_only` — established by a byte-prefix comparison, verified

The deciding line is count-c2.py:155:

```python
append_only = base_raw is not None and raw.startswith(base_raw)
```

where `raw`/`base_raw` are `git cat-file blob <tip>:SCORECARD.md` and
`<BASE=07794a4d>:SCORECARD.md`. Independent check on the same blobs:
`tip_bytes 124857`, `base_bytes 117789`, `tip.startswith(base) == True`; the first
7068 appended bytes begin `\n## Round 31 — the chat-completions adapter ...`.
`append_only True` is genuine: every base byte is preserved verbatim at the head
of the tip file. (Also honest about scope: this proves append-at-tail only — a
base byte would only be flagged if the tip file were shorter or differed inside
the first 117789 bytes.)

FINDING: On a fresh clone at 382d11b2 the frozen counter (sha256-verified) reads
`rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0
unresolved 3 append_only True met False`, exit 0. My independent re-derivation
AGREES with `unresolved 3`: 30 population rows confirmed with file:line each, the
three unresolved strings are exactly the Claim cells `C1`@266 (round 11),
`C1`@320 (round 12), `C1`@379 (round 13) — all class p1, observed
`p1:no-revision` — and `append_only` is a true byte-prefix of the tip blob over
the base blob. This reading is advisory evidence, not a verdict.

LIMITS:
- `unresolved == 0` is UNREACHABLE for this tree: three problems share key
  `("C1","p1")` and exactly one valid correction per key is required, so any
  single C1-correction silently discharges all three rows (met could then read
  True) and any second C1-correction makes both false. `unresolved 3` here is
  the honest artifact of a counter defect, not evidence that three corrections
  are missing — 13 distinct dispositions exist, only 10 are expressible. My seat
  did not test the single-correction overlay (KamaR31.CriticKeyCollapse is
  covering it); the claim follows by reading lines 257–268 only.
- One run of one checkout; the counter reads committed objects only
  (`git --no-replace-objects`), never the working tree — my clone's worktree
  state is irrelevant to the number.
- `append_only` proves prefix-extension only; it does not prove no base row was
  re-derived elsewhere in the file.
- Rows counted are population rows per the counter's own heading/first-cell
  rule; a table with header `| claim |` anywhere else in the file would count
  too, but my census found none besides the 18 claim tables.
- No lane git write was performed; all counter runs were on the /tmp clone.
- No tools installed or upgraded this run (system python3 + git sufficed).

Receipts kept beside this report: `c2.json`, `c2-list.json`, `c2-list.stdout.txt`,
`c2-list.stderr.txt`, `indep.py`, `indep.out`.
