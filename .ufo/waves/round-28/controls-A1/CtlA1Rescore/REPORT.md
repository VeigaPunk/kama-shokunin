VERDICT: does-not-meet
counted 9 registered 38 exit 0
counter sha256: a38faefeeb48be9fd3590b5077030ed6b7cef08dcaf1ca0540b464bd222749a5

The verdict line is the strongest control, CtlSourceBlind: 9 counted against target 18, exit 0.
The counter is amendment A1 at lane commit 75b78bb4900aae1edcdb6b229bb8c572c20fcbce, verified by
sha256 in every scratch tree before scoring and never edited. Each evidential pre-freeze control was
rebuilt on 75b78bb4 from its committed fixture and re-scored once. No control meets the target under
A1, and the strongest falls from 14 to 9.

# Round-28 C1: A1 re-score of the five evidential pre-freeze controls

## Result table

| control | A0 counted | A1 counted | registered | exit | changed rows |
|---|---|---|---|---|---|
| CtlSourceBlind | 14 | 9 | 38 | 0 | 5 lost: F28-09, F28-10, F28-11, F28-13, F28-27 (all `e:generic-conversion`) |
| CtlLabelKeyed | 12 | 7 | 41 | 0 | 5 lost: F28-02, F28-19, F28-20, F28-22, F28-23 (`e:generic-conversion`); F28-27 gains `e:generic-conversion` beside `e:default`, still refused |
| CtlJunk | 0 | 0 | 30 | 0 | none |
| CtlDuplicateField | 0 | 0 | 26 | 0 | none |
| CtlDoNothing | 0 | 0 | 0 | 0 | none |

A0 numbers are `controls/<name>/receipt.json` (counter sha256 `e6a706bb…0540c`). A1 numbers are
`receipt-<name>.json` in this directory (counter sha256 `a38faefe…749a5`); `receipt.json` is
CtlSourceBlind's A1 receipt byte-for-byte. Registration counts are unchanged (38, 41, 30, 26, 0), so
A1 refused rows that A0 had counted; it did not shrink what the fixtures register. Total across the
five falls 26 → 16. A1 widens the strongest control's margin from 4 rows to 9.

## Changed rows and why

CtlSourceBlind (tree commit 94e8234, fixture applied byte-for-byte from
`controls/CtlSourceBlind/fixture/`; rebuilt mutated hashes equal the A0 REPORT's record exactly:

| file | rebuilt sha256 | A0 REPORT record |
|---|---|---|
| SKILL.md | ab8a2ef0f9a1de3fe741523dc6c10737a3951e248e8ac7784a5ff6cd600fa25c | ab8a2ef0…fa25c |
| corpus/SOURCES.md | c53328c9e5916bbf21701ac768ec88b10f69f2bfbceccf874f450dcb14b626df | c53328c9…626df |
| registry/request-field-outcomes-r28.json | 6a9b29979d9c38bca17049556ce3a4940c9b35639a5ef97482e8d1ab04189d02 | 6a9b2997…9d02 |

| id | field | sent | stored (live, unchanged from A0) | A0 | A1 | why |
|---|---|---|---|---|---|---|
| F28-09 | top_p | 1.5 | 1.0 | counted | refused | `e:generic-conversion`: int(1.5) = 1, `same()` tolerance makes 1.0 equal 1 |
| F28-10 | min_p | -0.5 | 0.0 | counted | refused | `e:generic-conversion`: int(-0.5) = 0 |
| F28-11 | xtc_probability | 1.5 | 1.0 | counted | refused | `e:generic-conversion`: int(1.5) = 1 |
| F28-13 | temperature | -0.5 | 0.0 | counted | refused | `e:generic-conversion`: int(-0.5) = 0 |
| F28-27 | adaptive_target | 1.5 | 1.0 | counted | refused | `e:generic-conversion`: int(1.5) = 1 |

CtlLabelKeyed (tree commit 7ffb9b0, fixture applied byte-for-byte; all five lost rows are the P91
template "1.5 stored as 1.0"):

| id | field | sent | stored (live) | A0 | A1 | why |
|---|---|---|---|---|---|---|
| F28-02 | xtc_threshold | 1.5 | 1.0 | counted | refused | `e:generic-conversion` |
| F28-19 | top_p | 1.5 | 1.0 | counted | refused | `e:generic-conversion` |
| F28-20 | min_p | 1.5 | 1.0 | counted | refused | `e:generic-conversion` |
| F28-22 | xtc_probability | 1.5 | 1.0 | counted | refused | `e:generic-conversion` |
| F28-23 | adaptive_target | 1.5 | 1.0 | counted | refused | `e:generic-conversion` |
| F28-27 | seed | -1 | 4294967295 | refused (`e:default`) | refused (`e:default`, `e:generic-conversion`) | uint32 wrap now also named; count unchanged |

CtlJunk, CtlDuplicateField and CtlDoNothing have no row with a changed `why` list; their A0 and A1
receipts carry identical per-row refusal tags (Junk 30 rows both tags, DuplicateField tag tally
identical, 0 counted; DoNothing has no rows). Verified by comparing `why` sets row-by-row.

### The mechanism, run through the A1 counter's own functions

`conversions(sent)` returns `[bool(sent)]` plus, for a finite number, float32 rounding,
`int(sent)` truncation and the 32-bit and 64-bit wraps; `same()` treats 1.0 as equal to 1 and 0.0 as
equal to 0 within 1e-6 relative tolerance. Checked by importing `count-c1.py` (no side effects):

```text
top_p         sent=1.5  stored=1.0  conversions=[True, 1.5, 1, 1, 1, 1, 1]          -> matches: True
min_p         sent=-0.5 stored=0.0  conversions=[True, -0.5, 0, 0, 0, 0, 0]          -> matches: True
temperature   sent=-0.5 stored=0.0  conversions=[True, -0.5, 0, 0, 0, 0, 0]          -> matches: True
xtc_threshold sent=1.5  stored=1.0  conversions=[True, 1.5, 1, 1, 1, 1, 1]          -> matches: True
top_k         sent=-5   stored=0    conversions=[True, -5.0, -5, 4294967291, -5, …] -> matches: False
mirostat      sent=5    stored=2    conversions=[True, 5.0, 5, 5, 5, 5, 5]          -> matches: False
seed          sent=-1   stored=4294967295 conversions=[True, -1.0, -1, 4294967295, …] -> matches: True
xtc_threshold sent=2.5  stored=1.0  conversions=[True, 2.5, 2, 2, 2, 2, 2]          -> matches: False
```

So A1 removes exactly the rows whose stored value equals a generic conversion of the value sent: the
body of the source-blind and label-keyed shortcuts that happened to be true. It is the same rule as
`pilot_A1`: `xtc_threshold` sent 2.5 counts (stored 1.0 is a probability clamp, not a truncation),
sent 1.5 does not.

## Which clause refused which rows (A1 receipts)

| control | clause tallies over refused rows | rows refused | counted |
|---|---|---|---|
| CtlSourceBlind | `d:not-shown` 24, `e:generic-conversion` 5 | 29 | 9 |
| CtlLabelKeyed | `d:not-shown` 27, `e:generic-conversion` 6, `e:default` 2 (F28-27 carries two) | 34 | 7 |
| CtlJunk | `b:line-does-not-declare-field` 30 and `d:not-shown` 30 (every row has both) | 30 | 0 |
| CtlDuplicateField | `b:duplicate-line-or-field` 16, `d:not-shown` 18, `b:line-does-not-declare-field` 8, `b:set-not-one-key-equal-to-field` 4, `a:no-skill-row` 4; F28-13, F28-16, F28-18, F28-21 never reached the live phase | 26 | 0 |
| CtlDoNothing | none; the counter took the empty-registry early return and launched no server | 0 | 0 |

Clauses (a), (b) and (c) refused no row of CtlSourceBlind or CtlLabelKeyed; the only new refusal is
clause (e). That matches A0: A1 changed no static check.

## Residual shortcut under A1 (what still counts)

CtlSourceBlind still counts 9 rows with no field knowledge and no live look: 7 reject rows
(`sse_ping_interval`, `n_predict`, `n_indent`, `n_keep`, `n_discard`, `min_keep`,
`reasoning_budget_tokens`, each sent -5 and guessed `reject 400` with `-1 to 2147483647` or
`0 to 2147483647`) and 2 effective rows (`top_k` -5 → 0, `mirostat` 5 → 2). CtlLabelKeyed's 7
remaining rows are all the same P90 reject template on integer fields. The shortcut ceiling is
therefore 9 of 18 (A0: 14 of 18); A1 cuts the source-blind yield from 14 to 9 but does not close it.

## Fidelity of the rebuild

- The fixtures were applied from the committed fixture files byte-for-byte (copy / append), not
  regenerated by `guess.py` or `gen.py`, so the scored content is exactly what A0 scored.
- Rebuilt CtlSourceBlind mutated hashes equal the values the A0 REPORT recorded (table above). The
  other three fixtures record no mutated hashes upstream; their fidelity is shown by the live
  payload comparison below and the unchanged registration counts.
- Every live payload equals the A0 receipt row-by-row (`status`, `message`, `effective`,
  `base_effective`): 38/38 CtlSourceBlind, 41/41 CtlLabelKeyed, 30/30 CtlJunk, 21/21
  CtlDuplicateField. DuplicateField's other 5 rows were refused before the live phase in A0 too.
  `base_request_sha256` differs per control because the llama-server body carries timing fields.
- A1 receipt schema is `kama-r28-c1-receipt/v1-A1`, `target` 18, `met` false, `schema_file_at_base`
  `[]`; `counter_sha256` is `a38faefe…749a5` in all five receipts.
- Receipt sha256: CtlSourceBlind `01f9c43d51ab7076836e592c91e6272336c51079d7ea033c52e46278088a1c82`,
  CtlLabelKeyed `fb0e2cf72bd5153e47951416a420377f5cc64af29937ca3b5604207c63d0a849`, CtlJunk
  `3e1de3d6da6cbc88f73b2fbda47f6a4987d9f198caaf5458666d44fab63afaa8`, CtlDuplicateField
  `ed83cfda368e9dfaf9f7a2ab8c353db114f34247dfed666d65fb82f5472b9432`, CtlDoNothing
  `26c773f7499c4950241e992b71bc242846110321f56c955863ffc76215554e88`.

## Exact commands

Setup (scratch only; GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE unset; one sequential loop):

```sh
S=/fast/scratch/hyaku/kama-r28/ctlA1/CtlA1Rescore
L=/home/vgpnk/Projects/shokunin/kama-shokunin
C=$L/.ufo/waves/round-28/controls
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
mkdir -p $S
for n in CtlSourceBlind CtlLabelKeyed CtlJunk CtlDuplicateField CtlDoNothing; do
  mkdir -p $S/$n
  timeout 300 git clone -q $L $S/$n/tree
  timeout 120 git -C $S/$n/tree checkout -q 75b78bb4900aae1edcdb6b229bb8c572c20fcbce
done
cp $C/CtlSourceBlind/fixture/registry/request-field-outcomes-r28.json $S/CtlSourceBlind/tree/registry/
cat $C/CtlSourceBlind/fixture/SKILL.add.md >> $S/CtlSourceBlind/tree/SKILL.md
cat $C/CtlSourceBlind/fixture/SOURCES.add.md >> $S/CtlSourceBlind/tree/corpus/SOURCES.md
cp $C/CtlLabelKeyed/fixture/request-field-outcomes-r28.json $S/CtlLabelKeyed/tree/registry/
cat $C/CtlLabelKeyed/fixture/SKILL-section.md >> $S/CtlLabelKeyed/tree/SKILL.md
cat $C/CtlLabelKeyed/fixture/SOURCES-rows.md >> $S/CtlLabelKeyed/tree/corpus/SOURCES.md
cp $C/CtlJunk/fixture/request-field-outcomes-r28.json $S/CtlJunk/tree/registry/
cat $C/CtlJunk/fixture/SKILL-section.md >> $S/CtlJunk/tree/SKILL.md
cat $C/CtlJunk/fixture/SOURCES-additions.md >> $S/CtlJunk/tree/corpus/SOURCES.md
cp $C/CtlDuplicateField/fixture/registry/request-field-outcomes-r28.json $S/CtlDuplicateField/tree/registry/
cat $C/CtlDuplicateField/fixture/SKILL-section.md >> $S/CtlDuplicateField/tree/SKILL.md
cat $C/CtlDuplicateField/fixture/SOURCES-rows.md >> $S/CtlDuplicateField/tree/corpus/SOURCES.md
cp $C/CtlDoNothing/fixture/registry/request-field-outcomes-r28.json $S/CtlDoNothing/tree/registry/
printf '\n## Round-28 request-field outcomes\n\n| id | field | value | outcome | meaning | source |\n' >> $S/CtlDoNothing/tree/SKILL.md
for n in CtlSourceBlind CtlLabelKeyed CtlJunk CtlDuplicateField CtlDoNothing; do
  git -C $S/$n/tree add -A
  git -C $S/$n/tree -c user.name=CtlA1Rescore -c user.email=ctla1@scratch commit -qm "A1 rescore rebuild of $n fixture (scratch only)"
done
```

Scoring (one control at a time; the counter picks its own port in 47600-47619 and launches the
pinned llama-server itself; no server was started by hand):

```sh
for n in CtlDoNothing CtlSourceBlind CtlLabelKeyed CtlJunk CtlDuplicateField; do
  timeout 900 /usr/bin/python3 $S/$n/tree/.ufo/waves/round-28/count-c1.py --lane $S/$n/tree --repo $S/$n/tree --out $S/$n/receipt.json; echo exit=$?
done
```

stdout, exit and UTC time, with the long `not-counted` id lists elided here (full lists are in each
receipt):

```text
== CtlDoNothing start 08:43:32    registered 0 counted 0 target 18 met False not-counted []                                   exit=0 end 08:43:32
== CtlSourceBlind start 08:43:32  registered 38 counted 9 target 18 met False not-counted ['F28-05', …, 'F28-36']            exit=0 end 08:43:32
== CtlLabelKeyed start 08:43:32   registered 41 counted 7 target 18 met False not-counted ['F28-02', …, 'F28-41']            exit=0 end 08:43:33
== CtlJunk start 08:43:33         registered 30 counted 0 target 18 met False not-counted ['F28-01', …, 'F28-30']            exit=0 end 08:43:33
== CtlDuplicateField start 08:43:33 registered 26 counted 0 target 18 met False not-counted ['F28-01', …, 'F28-25', 'F28-25'] exit=0 end 08:43:34
```

The A1 `not-counted` lists are each A0's list for the same control with this report's lost rows added
(SourceBlind 24 → 29, LabelKeyed 29 → 34); Junk and DuplicateField lists are unchanged in content.

Provenance of the applied fixture files and resulting document hashes is in
`fixture/manifest.json`; per-row A0-vs-A1 deltas (sent value, claimed outcome, live payload, both
`why` lists) are in `fixture/rows-delta.json`. The output directory holds 9 files, under 75 KB in
total, well under 1 MiB.

## Risks and notes

- A1 costs true rows, not only shortcut rows. A clamp to the probability bound 1.0 is refused
  whenever the value sent truncates to 1 (1.5 → 1.0 here): the true `top_p`/`min_p`/
  `xtc_probability`/`adaptive_target`/`xtc_threshold` outcomes in these fixtures are genuine, live
  and now uncounted. This is the preregistered A1 trade and not a defect, but data rows for float
  fields must avoid values whose truncation equals the stored value (2.5 works where 1.5 does not).
- A1 does not touch reject-bound guessing: 9 rows still count from a single `-5 rejected` template
  with `0..INT32_MAX` / `-1..INT32_MAX`. If a control's absolute yield matters, the reject half is
  the untested lever; it was 7 of the 9.
- The receipt is still an oracle: A1 receipts record `live.message` and `live.effective` for refused
  rows, so a two-pass writer can fish and copy. `not_counted_boundary` calls that the claimed work
  (live outcomes); no new hole.
- `excluded_fields` (`n_cache_reuse`, `xtc_threshold`) is still not enforced by A1. CtlLabelKeyed's
  F28-01 is the pilot's `n_cache_reuse` row with only its id renamed and it still counts; its F28-02
  `xtc_threshold` row is now refused by `e:generic-conversion` (sent 1.5), but 2.5 would count. The
  closure still has to check the registry against `excluded_fields`.
- All five runs completed within two seconds (the pinned model is 1.18 MB). The evidence that they
  were real live runs is the exact row-by-row equality of all 130 live payloads with the A0
  receipts, plus the counter's pinned-binary, `/props`, clean-environment and process-identity
  checks; nothing was cached or replayed by this seat.
- After the runs `ss -ltnp` showed no listener on 47600-47619 and `pgrep` showed no process from
  these trees. A sibling seat's llama-server on port 48212 was visible during setup; it is not
  mine and was not touched.
- Every command was under `timeout`. No git or jj write was made in the lane or fleet repository,
  no tracked lane file was edited, and nothing outside this output directory was written. The only
  commits are in the scratch clones. `.ufo/waves/round-28/w1/` was never read. The lane worktree
  carried other seats' uncommitted changes during this run (`M .ufo/waves/round-25/count-c2.py`,
  `M corpus/QUALITY.md`, `M corpus/knowledge/echo-discriminating-counters.md`, untracked `w1/`,
  `integrate.py`, `tools/*`); they are not mine and were left untouched.
- Tool installs or updates: none, so there is nothing to record.

Report: .ufo/waves/round-28/controls-A1/CtlA1Rescore/REPORT.md
