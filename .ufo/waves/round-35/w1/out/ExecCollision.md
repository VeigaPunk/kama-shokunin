# Item-10 ID collision check — round 35, W1, ExecCollision

Scratch only. Lane registry `corpus/SOURCES.md` was not appended to and was not edited. Staged package `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` was read only.

## Procedure

Extractor is the census 0–3-space pattern (literal text match, not a semantic registry parse):

```sh
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' <file> | grep -oE 'S[0-9]+' | LC_ALL=C sort
```

Collisions:

```sh
LC_ALL=C comm -12 reg-ids staged-ids
```

`LC_ALL=C` only fixes sort/comm byte order. Both lists already pass `LC_ALL=C sort -c`. An independent set intersection equals `comm -12`.

## Results

| Measurement | Observed |
| --- | --- |
| Lane extracted-ID count | 200 unique (S001–S194, then S196, S205, S206, S209, S223, S324) |
| Staged extracted-ID count | 134 unique (S325–S458, no gaps in that span) |
| Collision count | **0** |
| `collisions` file | 0 bytes, 0 lines |

Any-indent pipe-row S-id counts equal the 0–3 counts (lane 200/200, staged 134/134). No current row is hidden by indent greater than 3.

### reg-ids

```text
S001
S002
S003
S004
S005
S006
S007
S008
S009
S010
S011
S012
S013
S014
S015
S016
S017
S018
S019
S020
S021
S022
S023
S024
S025
S026
S027
S028
S029
S030
S031
S032
S033
S034
S035
S036
S037
S038
S039
S040
S041
S042
S043
S044
S045
S046
S047
S048
S049
S050
S051
S052
S053
S054
S055
S056
S057
S058
S059
S060
S061
S062
S063
S064
S065
S066
S067
S068
S069
S070
S071
S072
S073
S074
S075
S076
S077
S078
S079
S080
S081
S082
S083
S084
S085
S086
S087
S088
S089
S090
S091
S092
S093
S094
S095
S096
S097
S098
S099
S100
S101
S102
S103
S104
S105
S106
S107
S108
S109
S110
S111
S112
S113
S114
S115
S116
S117
S118
S119
S120
S121
S122
S123
S124
S125
S126
S127
S128
S129
S130
S131
S132
S133
S134
S135
S136
S137
S138
S139
S140
S141
S142
S143
S144
S145
S146
S147
S148
S149
S150
S151
S152
S153
S154
S155
S156
S157
S158
S159
S160
S161
S162
S163
S164
S165
S166
S167
S168
S169
S170
S171
S172
S173
S174
S175
S176
S177
S178
S179
S180
S181
S182
S183
S184
S185
S186
S187
S188
S189
S190
S191
S192
S193
S194
S196
S205
S206
S209
S223
S324
```

### staged-ids

```text
S325
S326
S327
S328
S329
S330
S331
S332
S333
S334
S335
S336
S337
S338
S339
S340
S341
S342
S343
S344
S345
S346
S347
S348
S349
S350
S351
S352
S353
S354
S355
S356
S357
S358
S359
S360
S361
S362
S363
S364
S365
S366
S367
S368
S369
S370
S371
S372
S373
S374
S375
S376
S377
S378
S379
S380
S381
S382
S383
S384
S385
S386
S387
S388
S389
S390
S391
S392
S393
S394
S395
S396
S397
S398
S399
S400
S401
S402
S403
S404
S405
S406
S407
S408
S409
S410
S411
S412
S413
S414
S415
S416
S417
S418
S419
S420
S421
S422
S423
S424
S425
S426
S427
S428
S429
S430
S431
S432
S433
S434
S435
S436
S437
S438
S439
S440
S441
S442
S443
S444
S445
S446
S447
S448
S449
S450
S451
S452
S453
S454
S455
S456
S457
S458
```

### collisions

Empty. Collision count: **0**. No renumber map. Nothing appended.

## Indent guard

Scratch fixture `scratch-registry` is exactly the assigned line (od: `20 20 7c 20 53 30 30 32 20 7c 0a`):

```text
  | S002 |
```

0–3-space pattern:

```sh
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' scratch-registry | grep -oE 'S[0-9]+' | LC_ALL=C sort
```

Output:

```text
S002
```

Column-zero-only pattern:

```sh
grep -oE '^\|[[:space:]]*S[0-9]{3,}' scratch-registry | grep -oE 'S[0-9]+' | LC_ALL=C sort
```

Output:

```text
```

The column-zero-only stdout is empty (0 bytes). The 0–3 pattern extracts `S002`; the column-zero-only pattern misses it.

Corollary, still scratch: an indented staged id (`  | S325 |`) yields nonempty `guard-collisions-0-3` (`S325`) and empty `guard-collisions-column-zero`. A column-zero-only check would false-green that indented collision.

## Artifacts

Relative to the lane root:

- `.ufo/waves/round-35/w1/out/ExecCollision/reg-ids`
- `.ufo/waves/round-35/w1/out/ExecCollision/staged-ids`
- `.ufo/waves/round-35/w1/out/ExecCollision/collisions`
- `.ufo/waves/round-35/w1/out/ExecCollision/scratch-registry`
- `.ufo/waves/round-35/w1/out/ExecCollision/guard-0-3-output`
- `.ufo/waves/round-35/w1/out/ExecCollision/guard-column-zero-output`

## Scope

Lexical ID-collision check and indent-guard proof only. No row was admitted, normalized, or appended. No axis-authority file was edited.
