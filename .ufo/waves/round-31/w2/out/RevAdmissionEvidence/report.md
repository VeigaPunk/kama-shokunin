# RevAdmissionEvidence — independent verification of the two decisive artifacts

Item: verify (1) `w1/out/CriticClaimSize/c1-noop.json` reads 12+ counted and re-derive *what makes
its rows counted*; (2) `controls/RefRepair/receipt.txt` reads `valid 10 false 3 unresolved 3` and
whether the `(row, class)` collapse explanation matches the frozen counter's code. No prose was
trusted; the frozen counters (sha256 matched) were re-run against the fixture bytes and an
independently rebuilt correction arm.

```
RESULTS
$ sha256sum .ufo/waves/round-31/count-c1.py .ufo/waves/round-31/count-c2.py && git rev-parse HEAD
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  .ufo/waves/round-31/count-c1.py
2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe  .ufo/waves/round-31/count-c2.py
bda324bbc5c1d7db93553adb13c5f380492c3c93        # exit 0; both digests == preregistration; HEAD moved past dispatch tip 382d11b2 (jj snapshot), does not affect committed objects

$ cat .ufo/waves/round-31/w1/out/CriticClaimSize/c1-noop.json
"summary": "registered 12 counted 12 target 12 met True not-counted []",
"tip": "e722ead7889363ffd1cdb352850516d6d70e6936", "base": "07794a4d30a54a60ebdff50ac76d12c6df40a0f1",
12 row objects: id NOOP-01..NOOP-12, counted true, reasons [], live {"status": 200, "slot_task": 3,6,9,...,36}

$ cat .ufo/waves/round-31/controls/RefRepair/receipt.txt
Counter final summary:
rows 28 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 3 unresolved 3 append_only True met False tip 0dafe9e601e3
ARM-FAILED-THE-TARGET — rows 28 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 3 unresolved 3 append_only True met False tip 0dafe9e601e3
Counter sha256: 2d06f38d5a686b4d7a316c8db67256ff862fa6e922c1603c156341ff9a33c6fe  .ufo/waves/round-31/count-c2.py
All 8 listed commands exit 0; arm ran at base 0e6f8ed6 + appended corrections commit 0dafe9e6.

$ git clone scratch-fixtures.bundle fx   # exit 128
error: Repository lacks these prerequisite commits: 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e
# bundle is a delta on the lane base; fix: clone lane, fetch bundle into it
$ git clone -q --no-hardlinks kama-shokunin c1-fx && git fetch -q <bundle> HEAD:refs/remotes/fx/HEAD && git log --oneline fx/HEAD | head -8
7f4e798 Critic fixture: twelve distinct parameters and sources assert unchanged token budget
c0b9b26 Critic fixture: source-type guess and deduplicated C2 paste
e722ead Critic fixture: duplicate no-op alias and literal C2 list paste
0e6f8ed round-31: freeze ...                       # exit 0; e722ead = lane base 0e6f8ed + fixture commit

$ git show e722ead7:registry/chat-param-outcomes-r31.json  (and SKILL.md:1232+, corpus/SOURCES.md)
rows 12; all 12 identical except `id`: {"id":"NOOP-0x","param":"max_tokens","sent":1,
 "outcome":{"kind":"slot","set":{"n_predict":1}},"source":{"row":"S990","file":"server-common.cpp",
 "line":1530,"contains":"llama_params[item.key()] = item.value();"}}
base_body {"messages":[{"role":"user","content":"Hello"}],"max_tokens":1,"temperature":0,"seed":1}
SKILL.md table rows (12, identical modulo id):
 | NOOP-0x | max_tokens | 1 | 200, n_predict = 1 | This repeats the unchanged base request without adding knowledge. | S990 |
corpus/SOURCES.md:432 | S990 | pinned server-common.cpp | ... | server-common.cpp @704366d L1530 | `llama_params[item.key()] = item.value();` ...
S990 grep at base 07794a4d: 0 matches (grep exit 1) — row is new at tip, as rule (c) requires.
python3 distinctness check: distinct-rows(incl id) = 12, distinct-minus-id = 1

$ /usr/bin/python3 .ufo/waves/round-31/count-c1.py --explain NOOP-01 --tip e722ead7...
200, n_predict = 1                                  # exit 0; canonical render == SKILL outcome cell

$ /usr/bin/python3 count-c1.py --lane <lane> --repo /tmp/kama-r31w2/RevAdmissionEvidence/c1-fx --tip e722ead7889363ffd1cdb352850516d6d70e6936 --out c1-noop-rerun.json
registered 12 counted 12 target 12 met True not-counted []        # exit 0 — verbatim reproduction
rerun JSON: all counted=true, all reasons=[], live slot_task ids 3..36 step 3

$ git clone -q --no-hardlinks kama-shokunin c2-arm && cd c2-arm && git checkout -q 0e6f8ed6 && /usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo . --tip 0e6f8ed6 --list --out c2-base-list.json
rows 28 base_mismatched 13 exempt 1 valid_corrections 0 false_corrections 0 unresolved 13 append_only True met False tip 0e6f8ed6891c
  C1 — re-anchor stale source anchors by appended dated corrections (plan claim 1): p1 line 196 p1:no-revision
  C3 — `sources-registry` capability + 3 entries on uncovered ground: p1 line 197 p1:no-revision
  C1: p1 line 266 p1:no-revision            # Round-11 table (## heading at line 222)
  C2: p1 line 267 p1:no-revision
  C1: p1 line 320 p1:no-revision            # Round-12 table (## heading at line 283)
  C1: p1 line 379 p1:no-revision            # Round-13 table (## heading at line 340)
  C1 offline Ollama evidence replay: p1 line 445 p1:no-revision
  C1 declared-name duplicate-corpus admission: p1 line 522 p1:no-revision
  C2 `live-llamacpp-lifecycle`: p1 line 611 p1:no-revision
  C1 graded fields backed by a failing detector: p1 line 680 p1:no-revision
  C2 fail-capable live checks: p1 line 681 p1:no-revision
  C1 — outcome classification and receipt boundary: p1 line 781 p1:no-revision
  C2 — statement→mutant→detector ledger: p1 line 782 p1:no-revision          # exit 0

$ git show 0e6f8ed6:SCORECARD.md | sed -n '255-268p;316-322p;375-381p'   # lines 266,320,379 verbatim
| C1 | calibration 7 → 7; delta 0 | nine legacy files: missing fields 27 → 0; ...      (Round-11 table)
| C1 | calibration 7 → 7, delta 0 | One source path: old snapshot mismatch 1 / ...     (Round-12 table)
| C1 | calibration 7 → 7, delta 0 | two missing precise assertions → zero; ...          (Round-13 table)

$ /usr/bin/python3 gen_corr.py     # appends | CR31:NN | <verbatim rid> | p1 | p1:no-revision | x13, commits, re-runs counter
tip 7f43454427bab857c5e1e3eb6789237a9fc24cb5
rows 28 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 3 unresolved 3 append_only True met False tip 7f43454427ba
  corr CR31:03 row=C1 class=p1 ok=False
  corr CR31:05 row=C1 class=p1 ok=False
  corr CR31:06 row=C1 class=p1 ok=False      # all three corrections on key ("C1","p1") are false;
  # the other 10 corrections ok=True; unresolved = the three distinct C1 problems (lines 266/320/379)
counter exit 0

$ for TIP in b4f3edc0 382d11b2...; do count-c2.py --repo c2-arm --tip $TIP --out c2-tip-$TIP.json; done
rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip b4f3edc0bfc1   # exit 0
rows 30 base_mismatched 13 exempt 1 valid_corrections 10 false_corrections 0 unresolved 3 append_only True met False tip 382d11b2107d   # exit 0

$ /usr/bin/python3 count-c1.py --lane <lane> --repo c1-fx --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out c1-tip-382d11b2.json
registered 18 counted 17 target 12 met True not-counted ['K31-10']      # exit 0

$ pgrep -fl llama-server            # exit 1 — counter started and stopped only its own server
```

Frozen-counter code facts (count-c1.py / count-c2.py, hash-verified):

- count-c1.py counts a registry row iff `reasons` is empty across: unique `id` (dup ids uncounted,
  L383-387); `param` nonempty string; `outcome.kind` in the frozen 4-set; SKILL row whose 6 cells
  equal (id, param, canonical-JSON sent, rendered outcome, meaning ≥8 words, source row id); source
  row present at tip, absent at base, file/line/`704366d` bound, `contains` substring verbatim at
  that snapshot line; live check per kind; KQ38 discrimination. For `slot`: newest slot's `params`
  must contain every `outcome.set` key=value — and the row request is `dict(base_body); req[param]
  = sent`. The fixture's `base_body` already carries `max_tokens:1`, so each NOOP request is
  byte-identical to the base request and the slot trivially holds `n_predict=1`. The `slot`
  discrimination (L467) requires only that some `set` key ≠ `param` ("n_predict"≠"max_tokens"), so
  aliasing the base's own key passes vacuously. Nothing requires param/sent/outcome/source
  uniqueness across rows — `distinct-minus-id = 1` is not checked.
- count-c2.py: `problem_by_key = {(p["row"], p["class"]): p}` (L257) where `p["row"]` is the Claim
  cell's raw text (`rid`, L179); a correction is valid iff the key is a known problem AND
  `len(by_key[key]) == 1` AND observed equals the recomputed string AND id starts `CR31:` (L259-265).
  Three distinct population rows (lines 266/320/379) all carry the bare Claim cell `C1` and all
  fail `p1` → identical key `("C1","p1")` → `problem_by_key` collapses to one entry and all three
  corrections fail the `len==1` test (`ok=False`), leaving 3 unresolved. `unresolved` counts
  problem-list entries (not keys), so the three distinct rows each count.

FINDING: no-op claim supported YES. `c1-noop.json` reads `registered 12 counted 12 target 12 met
True`; my re-run of the unmodified frozen counter on the fixture (commit `e722ead7`, objects
verified via git history over lane base `0e6f8ed6`) reproduces it verbatim. What makes the rows
counted: unique `id` only — the 12 rows are one row with 12 names; each satisfies the SKILL-cell
binding, the S990 source binding, and the live check because `base_body` already sends
`max_tokens:1`, making every row request the base request and the claimed `n_predict=1` the base's
own stored value. `param`/`sent`/`outcome`/`source` uniqueness is never required.

FINDING: collapse claim supported YES. `receipt.txt` reads `valid_corrections 10 false_corrections
3 unresolved 3` verbatim; my independently generated 13-correction arm (one `CR31:` row per listed
problem, verbatim rid/class/observed) reproduces that exact summary on a different tip commit
(`7f434544`), and `--list` shows all three `row=C1 class=p1` corrections `ok=False`. The code-level
explanation matches: the correction key `(Claim-cell text, class)` collapses the three bare-`C1`
p1 failures into one key and `len(by_key[key]) == 1` fails every correction on it. Two wording
sharpenings for the L1: (a) all corrections on a shared key are false, not "the second" as the
counter's own docstring says; (b) the collapse is in `problem_by_key`/the correction key — the
problem list retains the three distinct rows, which is why `unresolved` is 3. Consequence
confirmed at the landed tips: the tree's ten expressible corrections read `valid 10 false 0
unresolved 3 met False` at both `b4f3edc0` and `382d11b2`; since `met` requires unresolved==0, C2
was unreachable at those tips — consistent with the not-admitted verdict.

LIMITS: (1) The receipt's commands exit 0 and its summary is reproducible, but the arm's appended
SCORECARD bytes are not stored — the control tree `0dafe9e6` exists only in the seat's scratch; my
independently generated corrections reproduce the outcome but do not prove the arm's exact cell
bytes. (2) I verified the frozen counters only on the fixture commit and the two landed tips; the
collapse was not re-tested at other historical states. (3) The noop fixture proves the counter is
meetable with zero new observations; it does not establish anything about the 17 counted rows in
the landed registry (out of my item's scope; RevCounterFair's classes are separate). (4) C3 gate
check untouched (other seat's item). (5) Counter runs used the lane repo for `--lane` (snapshot
files read from disk) — verified against the frozen sha256, no fixture-written state touched.
No tools installed; no tracked lane file modified; scratch under /tmp/kama-r31w2/RevAdmissionEvidence.
