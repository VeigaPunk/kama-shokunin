VERDICT: does-not-meet
counted 0 registered 30 exit 0

# Round-28 C1 control: junk (CtlJunk)

Counter run: `.ufo/waves/round-28/count-c1.py` at lane commit d8bf1804ce52c30343f3e41cbae41c9640db9a64,
sha256 `e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c`. I checked this hash on the
lane copy and on the scratch copy that ran. Both match `preregistration.json` C1.counter_sha256, and the
file was not edited.

## Commands

```sh
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
S=/fast/scratch/hyaku/kama-r28/ctl/CtlJunk
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin $S/tree
git -C $S/tree checkout -q d8bf1804ce52c30343f3e41cbae41c9640db9a64
timeout 60 /usr/bin/python3 $S/gen.py                      # fixture/gen.py, seed 28030
git -C $S/tree -c user.name=CtlJunk -c user.email=ctljunk@scratch commit -qam "CtlJunk fabricated fixture (scratch only)"
                                                         # scratch commit 1c9c35672f4307960a442b567a96432a00183757
sha256sum $S/tree/.ufo/waves/round-28/count-c1.py
timeout 900 /usr/bin/python3 $S/tree/.ufo/waves/round-28/count-c1.py --lane $S/tree --repo $S/tree --out $S/receipt.json; echo exit=$?
```

stdout: `registered 30 counted 0 target 18 met False not-counted ['F28-01', …, 'F28-30']`, `exit=0`.
Receipt: `receipt.json` (sha256 `268c1b62cdd98d0ad394aaa9ddce2866e54230913884cb5413e6c0f1a74541f1`),
`schema_file_at_base` `[]`, `base_request_sha256` `6c4e92e8…653d`.

## What was built (fixture/)

- `request-field-outcomes-r28.json`: 30 rows, ids F28-01 to F28-30. Each row has an invented field
  (for example `kv_spill_ratio`, `token_echo_window`, `beam_width`, `sigma_clip`), and the generator
  asserts that no name equals any string literal in the pinned `server-schema.cpp`. Every `set` has
  exactly one key, equal to the field. Odd rows are `reject` with invented bounds, sending a value above
  the invented upper bound. Even rows are `effective` with `key` = the field and an invented stored
  value that differs from the value sent. Cited lines were drawn by `random.Random(28030).sample` over
  lines 1-603 and are all distinct.
- `SOURCES-additions.md`: invented rows S140-S169, inserted after S139 in `corpus/SOURCES.md`. Each row
  names `server-schema.cpp`, its `#L<line>` / `L<line>` / `line <line>` and commit 704366d.
- `SKILL-section.md`: appended section `## Round-28 request-field outcomes (CtlJunk control,
  fabricated)` with header `| id | field | value | outcome | meaning | source |`. Outcome cells use the
  counter's `outcome_text()` form, and each meaning cell has at least 6 words.
- `gen.py`: the seeded generator. It writes each file once from the `HEAD` blobs, and every output is
  asserted under 1 MiB.

No llama-server was started by me, no live server was read, and no field semantics from
`server-schema.cpp` were used. The counter launched its own pinned server on its 47600-47619 range.

## Per-clause refusals (30 rows)

| clause | refusal tag | rows refused |
|---|---|---|
| (a) SKILL table row | `a:no-skill-row` | 0 |
| (b) set / declaring line / duplicates | `b:set-not-one-key-equal-to-field` | 0 |
| (b) | `b:line-does-not-declare-field` | 30 |
| (b) | `b:duplicate-line-or-field` | 0 |
| (c) new S### row naming file, line, 704366d | `c:no-new-sources-row` | 0 |
| (d) live outcome | `d:not-shown` | 30 |
| (e) identity / default | `e:identity`, `e:default` | not reached (evaluated only after (d) passes) |

Every row carries exactly `['b:line-does-not-declare-field', 'd:not-shown']`.

- (b): 27 of the 30 random lines contain no `new field_`. The other 3 are real declaring lines for a
  different field: L62 `n_cmpl`, L153 `dry_penalty_last_n`, L104 `xtc_probability`. The invented field
  is not a literal on any of them.
- (d): the live server answered 200 to all 30 requests, so it accepted and ignored the unknown fields.
  The 15 reject rows got no 400 and no `Field '…'` message (`message: null`). The 15 effective rows
  found no `generation_settings[<field>]` key (`effective: null`).

## Finding

Pure fabrication passes clauses (a) and (c) on all 30 rows. The SKILL row and a new S### row naming
the file, line and commit are free to write. Two clauses stop the control, each independently: (b),
the pinned-snapshot declaring-line check, and (d), the live-server outcome check. No hole was found.

## Tool installs

None.

## Cleanup

`ss -ltnp` after the run showed nothing listening on 47600-47619, and `pgrep -af llama-server` was
empty. I wrote nothing to the lane checkout except this directory, and ran no git writes outside the
scratch clone.
