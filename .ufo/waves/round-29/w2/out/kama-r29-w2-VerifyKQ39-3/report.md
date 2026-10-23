# VerifyKQ39 — seat report (w2, round 29 attempt 2)

Seat: `kama-r29-w2-VerifyKQ39-3` (reviewer, leaf). Claim served: round-28 spot-check
routed repairs (not claims) — verification of the attempt-1 narrative.
Item: confirm KQ39's writing-revision rule, drift-assignment, and correction-row shape
match what `count-c1.py` actually does, and that CtlBaseTree's receipt (4 drift
statements refused as false corrections) exercises the drift clause.

## Verdict

All four sub-checks PASS. Evidence below; every claim is reproduced, not asserted.

- KQ39 writing-revision rule == counter behavior.
- KQ39 drift assignment == counter behavior.
- KQ39 correction-row shape == counter behavior.
- CtlBaseTree receipt exercises the drift clause (4 statements true at W, false later
  at base, refused as `not-a-mismatch` false corrections); receipt reproduced exactly.

## 1. KQ39 writing-revision rule matches count-c1.py

KQ39 (`corpus/QUALITY.md:289`): "Each checkable self-assessment statement is evaluated
against repository state and history at its writing revision W, identified for its line
by `git blame --line-porcelain`: false at W is a calibration mismatch".

Counter docstring (`count-c1.py:8-14`): "Its writing revision W is the commit
`git blame --line-porcelain <base> -- <file>` names for that line. A statement HOLDS iff
its check passes against the lane tree and history at W". Source:

- `extract()` calls `blame(repo, fname)` (`count-c1.py:173`) which runs
  `git blame --line-porcelain BASE -- path` (`:128-137`), per line `W = revs[i]`
  (`:228`).
- `check()` evaluates each class at W (`:232-265`): P/H/N via `repo.blob(W, path)`,
  C via `repo.commit(token)` + `repo.strict_ancestor(c, W)`, T via `repo.ctime(W)`,
  Q via `git grep -F -q -e <span> W`.
- Receipt fields `W` per statement, `mismatched_at_base` = count of false-at-W.

MATCH.

## 2. Drift assignment matches

KQ39: "true at W but false later is drift, assigned to freshness rather than calibration".

Counter: `mism` contains only statements whose W-evaluation fails
(`check()` returns `(False, obs)`; `mism[s["sid"]] = obs`, `:304-308`). A statement that
holds at W never enters `mism`, regardless of whether it fails at base/tip. Drift is
therefore excluded from calibration by construction; and a correction row naming such a
statement is refused (`:314-321`):
`if sid in seen or sid not in mism or obs != mism[sid]` → `why = not-a-mismatch`.

MATCH. Note (framing, not a defect): the counter has no explicit freshness ledger; KQ39's
"assigned to freshness" is a disposition — operationally the counter simply does not count
drift as calibration, which is the observable behavior the criterion requires.

## 3. Correction-row shape matches

KQ39: "A correction preserves the original statement and is a newly appended row carrying
the counter's observed value; any missing, duplicate, wrong-value or otherwise false
correction counts as a mismatch."

Counter docstring (`:20-30`): a correction row is a table row under heading
`## Round 29 — self-assessment corrections` whose first cell is `SA29:<sid>` and whose
last cell is the observed value this counter prints (exact string); the tip
SCORECARD.md must begin with the base SCORECARD.md bytes (append-only); a row naming a
holding statement / no base statement / wrong observed value / duplicate sid is a FALSE
correction, each counted as unresolved.

Source: `corrections()` (`:268-279`) parses rows under `HEADING`, first cell
`strip("`").startswith("SA29:")`, `sid = first[5:]`, `observed = cols[-1].strip("`")`;
main loop `:309-327` implements append-only (`tip_sc.startswith(base_sc)`), duplicate /
not-a-mismatch / wrong-observed classification, and
`unresolved = len(unresolved_ids) + len(false_rows)` (`:327`).

MATCH.

## 4. CtlBaseTree receipt exercises the drift clause

Control receipt (`.ufo/waves/round-29/controls/CtlBaseTree/receipt.json`):
`false_corrections` = exactly 4 rows, each `why: not-a-mismatch`:

| sid | observed (base) |
|---|---|
| SCORECARD.md:H:cda32b698f:0 | md5=e8bfdcac8e0b66d76c1f0173383d0c80 |
| SCORECARD.md:N:cda32b698f:0 | newlines=1138 unterminated=true |
| SCORECARD.md:H:f4c42debcc:0 | md5=3116d4594d5d5fe259d8815485ea85dc |
| SCORECARD.md:N:54da210e98:0 | newlines=1230 unterminated=false |

Independent verification (not trusting the report or receipt):

- The policy checks statements against the BASE tree instead of W
  (`base_tree_check.py` → `check_at_base`, every lookup pinned to `BASE`).
- Each of the 4 statements HOLDS at W (counter `--list` run: `holds_at_W True`; W =
  `ea72c3eae4ec` for the first three, `83bee7faf5a7` for `N:54da210e98:0`).
  Independently reproduced with `git show`:
  * `ea72c3eae4ec:tools/kama-probe.sh` → md5 `1f81e859c2d7f43f87d1f7e01327b2cf`
    (matches written hex), newlines=1092 unterminated (matches written `1092 lines`).
  * `ea72c3eae4ec:tools/test-snapshot.sh` → md5
    `860f26ac05938cdfc1a8816eff1570b4` (matches written hex).
  * `83bee7faf5a7:SKILL.md` → newlines=323 unterminated (matches written `323 lines`).
- Each FAILS at base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`:
  * `tools/kama-probe.sh` md5 `e8bfdcac8e0b66d76c1f0173383d0c80`, newlines=1138.
  * `tools/test-snapshot.sh` md5 `3116d4594d5d5fe259d8815485ea85dc`.
  * `SKILL.md` newlines=1230.
- `ea72c3eae4ec` and `83bee7faf5a7` are strict ancestors of base
  (`git merge-base --is-ancestor` → true), so base is later in history. Each statement is
  therefore exactly "true at W, false later" = KQ39 drift.
- The frozen counter refuses the policy's rows for them: `not-a-mismatch` false
  corrections, each counted toward `unresolved 9` → `met False`. This demonstrates the
  KQ39 reject clauses "A statement is checked only at base … rather than W" and "later
  drift is called a writing-time error" — the counter refuses both (SUMMARY.md:25;
  KQ39 row, QUALITY.md:289).

Receipt reproduction: re-ran the frozen counter (sha256
`fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`, verified) against the
intact policy clone `/fast/scratch/hyaku/kama-r29/ctl/CtlBaseTree/repo` at
`93efe2d45da5`:

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 6 false_corrections 4 unresolved 9 met False tip 93efe2d45da5   (exit 0)
```

Committed receipt matches the reproduction field-for-field (append_only, by_class,
correction_rows 10, counter_sha256, met False, mismatched_at_base 11, statements 69,
target, tip, unresolved 9, valid_corrections 6, false_corrections, unresolved_ids,
mismatches). Append-only also verified at the blob level: tip SCORECARD.md
(106,061 bytes) starts with base SCORECARD.md (104,553 bytes). Correction-row shape in
the policy tip verified: 10 rows under `## Round 29 — self-assessment corrections`, first
cell `SA29:<sid>`, last cell observed string in counter format (`md5=…`, `newlines=…
unterminated=…`, `p:absent`, `q:no-artifact`).

## Observations

1. The round-28 spotcheck file (`corpus/lessons/round-28-verifier-spotcheck.md`) has no
   literal "calibration-at-writing" item heading. The anchors for the served claim are
   (a) the calibration axis verdict (`:163`: "not claimed. ResSelfAssessment's 3/46
   mismatches are a disclosure: 2 were corrected by an appended LOG entry and 1 is open
   in SHONEN box 2") and (b) routed defect 9 (`:246-247`: SHONEN box 2, round-17 wording
   mismatch still open, carried from ResSelfAssessment). The attempt-1 narrative answers
   these with C1/KQ39 (self-assessment statements judged at their writing revision) and
   repair 9 (SHONEN.md line 8 wording, `corpus/lessons/round-29.md:77`). "Calibration-at-
   writing" is the narrative's framing of that item, not a verbatim spotcheck heading —
   noted for the L1, not a defect.
2. Minor framing: KQ39 says a false correction "counts as a mismatch"; the counter counts
   false corrections as `unresolved` (not `mismatched_at_base`). Functionally identical
   for the target (`met` requires `unresolved == 0`) and documented in the docstring.
   Not a defect.
3. The lane repo does not contain the control commits (`93efe2d45da5` is absent from the
   lane object store); control receipts live in scratch clones
   (`/fast/scratch/hyaku/kama-r29/ctl/…`) by design. I reproduced from that clone.

## Tooling

No installs/updates. Used pre-existing `/usr/bin/git`, `/usr/bin/python3` (stdlib only),
`/usr/bin/md5sum`, `/usr/bin/sha256sum`.

## Verification gaps

- Sibling-covered claims not re-verified here (append-only/correction rows at the real
  data tip 513eba3b, RefPaste, row-level statement checks, controls summary other rows).
- The 5 Q statements that the policy misses (false at W, pass at base) are exercised by
  CtlBaseTree's unresolved list but were not individually re-checked by this seat
  (they are not part of the drift clause being verified).
