VERDICT: does-not-meet
counted 12 registered 41 exit 0

# Round-28 C1 pre-freeze control: label-keyed shortcut (CtlLabelKeyed)

The counter I ran: `.ufo/waves/round-28/count-c1.py` at lane commit
d8bf1804ce52c30343f3e41cbae41c9640db9a64, sha256
`e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c`. I checked that hash in the
scratch tree right before the run, and the receipt's `counter_sha256` matches it.
Receipt: `receipt.json` (sha256 1e23477be18d413bb83cff6b2e2b02eff56e5caf081f8b7c540cdb175ad02a47,
`met` false, `schema_file_at_base` [], base_request_sha256 b2693a7f…2864).

The control is below the target: 12 rows counted against a target of 18. The margin is only 6 rows,
and 10 of the 12 counted rows are fields the pilot never sent. See "Findings".

## Commands

```
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
S=/fast/scratch/hyaku/kama-r28/ctl/CtlLabelKeyed
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin $S/tree
git -C $S/tree checkout -q d8bf1804ce52c30343f3e41cbae41c9640db9a64
timeout 60 python3 $S/gen.py                      # fixture/gen.py; writes the 3 fixture files into $S/tree
git -C $S/tree add -A && git -C $S/tree -c user.name=ctl -c user.email=ctl@scratch commit -qm "CtlLabelKeyed fixture (scratch only)"
                                                  # scratch commit 87ea100214acf5a4d79a50b7bef32d8285f7dd69
sha256sum $S/tree/.ufo/waves/round-28/count-c1.py # e6a706bb…0c
timeout 900 /usr/bin/python3 $S/tree/.ufo/waves/round-28/count-c1.py --lane $S/tree --repo $S/tree --out $S/receipt.json; echo exit=$?
# -> registered 41 counted 12 target 18 met False not-counted [29 ids]   exit=0
```

I made one scored run. I did not re-score with outcomes taken from that receipt. Doing so would use
the counter's live server as the oracle, which is the claimed work (live outcomes), not a
label-keyed shortcut. I ran no live server of my own, installed no tools, and read no
`server-schema.cpp` semantics: I found declaring line numbers with a grep for `new field_` and the
quoted field name (`gen.py: decl_line`). After the run, `ss -ltnp` and `pgrep llama-server` showed
nothing I started still running or listening.

## What I built (fixture/)

- `request-field-outcomes-r28.json` holds 41 rows, F28-01 to F28-41, one per field. Each row has a
  unique declaring line and a one-key `set`. Every row carries an `origin` key naming what it copied.
- `SKILL-section.md` was appended to the scratch SKILL.md as
  `## Round-28 request-field outcomes (label-keyed control, scratch only)` with the exact six-column
  header. Each meaning cell is the copied origin (at least six words).
- `SOURCES-rows.md` holds S140 to S180, inserted after S139 in the scratch corpus/SOURCES.md. Each
  names `server-schema.cpp`, `L<line>` and `704366d`, and none exists at base.
- `gen.py` is the generator. It writes three bounded files and has no loops that append.

Copy origins used:

- **P90**: pilot F28-90 (`n_cache_reuse` -1, reject 0 to 2147483647), renamed to F28-01. Its value
  and bounds are also reused for 18 other integer fields.
- **P91**: pilot F28-91 (`xtc_threshold` 1.5, stored as 1.0), renamed to F28-02. Its value and
  stored value are also reused for 6 other float fields.
- **README**: `--adaptive-decay` "valid range 0.0 to 0.99" gives 0.99 as the stored value; `--seed`
  "-1, use random seed".
- **Round-25 K cells**: X1 KV pool 8192 as the value sent; K1 per-slot n_ctx 2048 as the stored
  value.
- **E26-17**: `--ctx-size -5` gives the value -5.
- **Round-26 base `generation_settings`**: stored values for 11 sampling fields, copied from
  `.ufo/waves/round-26/w1-build/out/ExecPromptTooLong/healthy1-body.txt`.

## Rows, copied origin, live answer, refusing clause

| id | field | value | claimed outcome | origin | live (counter's run) | clause |
|---|---|---|---|---|---|---|
| F28-01 | n_cache_reuse | -1 | reject 0..2147483647 | P90 renamed | 400, 0..2147483647 | **counted** |
| F28-02 | xtc_threshold | 1.5 | effective 1.0 | P91 renamed | 200, 1.0 (base 0.1) | **counted** |
| F28-03 | n_keep | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |
| F28-04 | n_discard | -1 | reject 0..2147483647 | P90 reused | 400, 0..2147483647 | **counted** |
| F28-05 | n_probs | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |
| F28-06 | min_keep | -1 | reject 0..2147483647 | P90 reused | 400, 0..2147483647 | **counted** |
| F28-07 | dry_allowed_length | -1 | reject 0..2147483647 | P90 reused | 400, 0..2147483647 | **counted** |
| F28-08 | dry_penalty_last_n | -1 | reject 0..2147483647 | P90 reused | 400, 0..2147483647 | **counted** |
| F28-09 | repeat_last_n | -1 | reject 0..2147483647 | P90 reused | 400, 0..2147483647 | **counted** |
| F28-10 | top_k | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |
| F28-11 | mirostat | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |
| F28-12 | n_indent | -1 | reject 0..2147483647 | P90 reused | 400, 0..2147483647 | **counted** |
| F28-13 | n_cmpl | -1 | reject 0..2147483647 | P90 reused | 400, bounds 1..4 | d:not-shown (bounds differ) |
| F28-14 | t_max_predict_ms | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |
| F28-15 | sse_ping_interval | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |
| F28-16 | reasoning_budget_tokens | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |
| F28-17 | speculative.n_max | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |
| F28-18 | speculative.n_min | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |
| F28-19 | top_p | 1.5 | effective 1.0 | P91 reused | 200, 1.0 (base 0.95) | **counted** |
| F28-20 | min_p | 1.5 | effective 1.0 | P91 reused | 200, 1.0 (base 0.05) | **counted** |
| F28-21 | typical_p | 1.5 | effective 1.0 | P91 reused | 200, 1.5 | d:not-shown |
| F28-22 | xtc_probability | 1.5 | effective 1.0 | P91 reused | 200, 1.0 (base 0.0) | **counted** |
| F28-23 | adaptive_target | 1.5 | effective 1.0 | P91 reused | 200, 1.0 (base -1.0) | **counted** |
| F28-24 | speculative.p_min | 1.5 | effective 1.0 | P91 reused | 200, key absent | d:not-shown |
| F28-25 | adaptive_decay | 1.5 | effective 0.99 | P91 value, README range | 400 | d:not-shown |
| F28-26 | n_predict | 8192 | effective 2048 | K cells X1/K1 | 200, 8192 | d:not-shown |
| F28-27 | seed | -1 | effective 4294967295 | README seed, base gs | 200, 4294967295 = base | e:default |
| F28-28 | temperature | -5 | effective 0.800000011920929 | E26-17, base gs | 200, 0.0 | d:not-shown |
| F28-29 | top_n_sigma | -5 | effective -1.0 | E26-17, base gs | 200, -5.0 | d:not-shown |
| F28-30 | dry_base | -5 | effective 1.75 | E26-17, base gs | 200, 1.75 = base | e:default |
| F28-31 | repeat_penalty | -5 | effective 1.0 | E26-17, base gs | 400 | d:not-shown |
| F28-32 | frequency_penalty | -5 | effective 0.0 | E26-17, base gs | 200, -5.0 | d:not-shown |
| F28-33 | presence_penalty | -5 | effective 0.0 | E26-17, base gs | 200, -5.0 | d:not-shown |
| F28-34 | mirostat_tau | -5 | effective 5.0 | E26-17, base gs | 200, -5.0 | d:not-shown |
| F28-35 | mirostat_eta | -5 | effective 0.10000000149011612 | E26-17, base gs | 200, -5.0 | d:not-shown |
| F28-36 | dynatemp_range | -5 | effective 0.0 | E26-17, base gs | 200, -5.0 | d:not-shown |
| F28-37 | dynatemp_exponent | -5 | effective 1.0 | E26-17, base gs | 200, -5.0 | d:not-shown |
| F28-38 | dry_multiplier | -5 | effective 0.0 | E26-17, base gs | 200, -5.0 | d:not-shown |
| F28-39 | speculative.ngram_size_n | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |
| F28-40 | speculative.ngram_size_m | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |
| F28-41 | speculative.ngram_min_hits | -1 | reject 0..2147483647 | P90 reused | 200 | d:not-shown |

The "live" column is copied from the receipt's `live` objects. Clauses (a), (b) and (c) refused no
row: the table, the declaring lines and the new S### rows are all cheap to build.

Refusals by clause:

- **(d) live outcome not shown: 27 rows.** 26 sent an integer value with reused reject bounds or an
  effective value copied from another cell, and the server answered something else. F28-13 was
  rejected, but with bounds 1..4.
- **(e) stored value equals the default: 2 rows** (`seed`, `dry_base`).

## Findings

1. **The pilot's outcomes generalize.** The reject pattern copied from F28-90 (-1 refused with
   bounds 0..2147483647) counted on 6 other integer fields. The clamp pattern copied from F28-91
   (1.5 stored as 1.0) counted on 4 other float fields. With no live run and no schema reading, two
   template outcomes produced 12 counted rows, or 2/3 of the target. The counter cannot tell a copied
   template from an observed outcome when the template happens to be true. Every counted row's
   outcome is genuinely live-true, so this is a margin problem rather than a false count. Under this
   control class the remaining integer and float fields gave no further hits. [INFERENCE] A guessed
   template set that is somewhat wider (other bounds such as 1..4, or other clamp targets) could push
   a no-work writer closer to 18. That is the source-blind control's ground, not tested here.
2. **The excluded fields are not enforced.** The preregistration lists `excluded_fields:
   ["n_cache_reuse", "xtc_threshold"]`, but `count-c1.py` never reads that list. F28-01 and F28-02
   are the pilot rows with only their ids renamed, and both counted. Pilot data can enter the count
   once its ids are renamed.
3. **The receipt is an outcome oracle.** For rows that were not counted, `live` records the real
   status, bounds message or stored value (for example n_cmpl 1..4, temperature -5 stored as 0.0).
   One receipt-guided rewrite would turn most of these misses into counted rows. Per the
   preregistration's `not_counted_boundary`, that is running the server and recording true outcomes,
   which is the claimed work, so I did not try it. The guard against it is per-row review of sources
   and meaning prose, not this counter.

## Boundaries kept

- I made no git or jj writes in the lane repo or the fleet repo. The only commit is in the scratch
  clone.
- I edited no tracked lane files. The only lane writes are this directory: REPORT.md, receipt.json
  and fixture/, 60K in total.
- No tool installs, so there are none to record and no RULES.md-governed actions.
