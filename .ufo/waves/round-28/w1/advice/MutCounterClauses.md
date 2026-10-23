# Round-28 C1 counter — clause mutation test (MutCounterClauses)

VERDICT — two counter versions were scored because the lane moved mid-wave:

- **A0** (ticket-pinned `e6a706bb…`, commit `d8bf1804`): **3 of 7 mutants survive** —
  `a_cells`, `b_line`, `c_novelty`. `b_dup`, `d_bounds`, `e_identity`, `e_default` are killed.
- **A1** (the current lane `a38faefe…`, commit `75b78bb`, landed while this seat was
  setting up): **4 of 7 survive** — `a_cells`, `b_line`, `c_novelty`, **`e_identity`**.
  A1's new `e:generic-conversion` branch refuses every row the identity check refused, so
  deleting identity no longer raises any control. `b_dup`, `d_bounds`, `e_default` stay killed.

Under both versions every committed control still scores below target; A1 only lowers
baseline counts, never raises one. The survivors are a **control-coverage** finding:
`a_cells` and `b_line` are exercised (they own refusal tags on real rows) but never change a
count; `c_novelty` is never touched; `e_identity` is subsumed under A1.

## Inputs and timeline

| item | value |
|---|---|
| A0 counter (ticket) | `.ufo/waves/round-28/count-c1.py` @ `d8bf1804ce52c30343f3e41cbae41c9640db9a64`, sha256 `e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c` |
| A1 counter (current lane) | same path @ `75b78bb` ("C1 amendment A1 (generic-conversion refusal in clause e)"), sha256 `a38faefeeb48be9fd3590b5077030ed6b7cef08dcaf1ca0540b464bd222749a5` |
| lane base | `4179301f7516ad667509d54b5ebfe0a70a002d5b` |
| scratch | `/fast/scratch/hyaku/kama-r28/w1/MutCounterClauses/` (256M) |
| artifacts | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/MutCounterClauses-2/` (A0 + A1 matrices, diffs, manifests, receipts) |

The A0 copy was cloned and hashed before any mutation; commit `75b78bb` then landed
(counter + preregistration + A1 pilot receipts). Neither lane counter was edited by this
seat. A1's counter diff is only: docstring, `import struct`, a new `conversions()` helper,
receipt schema `v1-A1`, and the clause-(e) block (`sent = …`, identity, new `elif`
`e:generic-conversion`, default unchanged). Five of the seven mutations are byte-identical
strings in both versions; the two clause-(e) mutants were re-derived for A1.

Host pins were verified before the first run (all equal to the counter's constants):
`/usr/bin/python3.14` `375532f8…458b`, `/usr/bin/git` `2912a2a3…384c`,
`llama-server` `b6a31a8e…c804`, `libllama-server-impl.so` `e404b91a…59ed`,
`stories260K.gguf` `270cba1b…256d`; no `/etc/ld.so.preload`.

## Method

The counter reads exactly four paths from `--lane`: `SKILL.md`, `corpus/SOURCES.md`,
`registry/request-field-outcomes-r28.json` and
`.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp`. Each control tree is
that measured surface, materialized with `git show d8bf1804:…` and the committed fixture
applied; `--repo` is one scratch clone of the lane containing the base commit. No fixture
needed a git write, and no lane/fleet git or jj write was made.

| tree | rebuild from the committed fixture |
|---|---|
| freeze | `d8bf1804` unchanged (no registry) |
| empty | header-only section + `{"rows": []}` (`CtlDoNothing/fixture/SKILL.md.diff`) |
| junk | cat `SKILL-section.md`, `SOURCES-additions.md`; cp registry (30 rows) |
| labelkeyed | cat `SKILL-section.md`, `SOURCES-rows.md`; cp registry (41 rows) |
| sourceblind | cat `SKILL.add.md`, `SOURCES.add.md`; cp registry (38 rows) |
| duplicate | cat `SKILL-section.md`, `SOURCES-rows.md`; cp registry (26 rows) |
| echo | `git apply CtlEcho/fixture/fixture.diff` (21 rows) |
| sourcemisuse | cat `SKILL-section.md`, `SOURCES-rows.md`; cp registry (12 rows) |
| pilot | reconstructed from `before/pilot-receipt.json`: F28-90 `n_cache_reuse` -1, reject 0..2147483647, L67/S990; F28-91 `xtc_threshold` 1.5, effective 1.0, L108/S991 |

Every run: sequential, one server at a time,
`env -i PATH=/usr/bin:/bin HOME=/home/vgpnk LANG=C.UTF-8 timeout 900 /usr/bin/python3
<counter> --lane <tree> --repo <scratch clone> --out <receipt>`. The counter launched and
killed its own pinned server on 47600–47619; `ss -ltnp` was empty on that range after every
run. Receipts self-report their counter sha: **63/63 A0 mutant receipts**, **72/72 A1
receipts** (9 baselines + 63 mutants) carry the intended file's hash; the 9 A0 baselines
carry the frozen hash.

**Baseline cross-checks.**

| tree | A0 committed counted | A0 re-run | ids+why equal | A1 baseline | A1 vs committed |
|---|---|---|---|---|---|
| freeze | 0 | 0 | yes | 0 | same |
| empty | 0 | 0 | yes | 0 | same |
| junk | 0 | 0 | yes | 0 | same |
| labelkeyed | 12 | 12 | yes | 7 | −5 |
| sourceblind | 14 | 14 | yes | 9 | −5 |
| duplicate | 0 | 0 | yes | 0 | same |
| echo | 1 | 1 | yes | 1 | same |
| sourcemisuse | 2 | 2 | yes | 1 | −1 |
| pilot | 2 | 2 | yes | 1 | −1 |

The A1 pilot reproduces the L1's own committed `before/pilot-A1-xtc1.5-receipt.json`
**exactly**: counted 1, F28-91 `e:generic-conversion` (and F28-90 counted). The A0 pilot
reproduces `before/pilot-receipt.json`: counted 2, F28-90 error body sha `9584dbff…d3161`,
F28-91 `effective 1.0`, `base_effective 0.10000000149011612`. A1 baseline drops are the
generic-conversion refusals: labelkeyed F28-02/19/20/22/23, sourceblind
F28-09/10/11/13/27, sourcemisuse F28-02, pilot F28-91.

## Mutants (one clause each)

| mutant | exact edit | A0 sha (short) | A1 sha (short) |
|---|---|---|---|
| `a_cells` | SKILL cell-content predicates become `if True:`; 6-cell shape + id kept | `3347cb9a…8071` | `a7b2ae7e…976b` |
| `b_line` | `if False:` around `new field_` + literal; line-range/file kept | `2a37b067…b431` | `4690b63f…7ef9` |
| `b_dup` | duplicate line/field loop replaced by `pass` | `ca468a4a…dc5e` | `c6457497…c98b` |
| `c_novelty` | `row in src_base` removed from clause (c) | `ce4a765a…859e` | `b9b6398a…a7a4` |
| `d_bounds` | reject branch becomes `ok = qs == 400` (message/field/bounds ignored) | `eccd2ebb…7faf` | `64446c01…d279` |
| `e_identity` | identity append removed; A1: `if` merged into the generic-conversion `if` | `d1064ff2…33d0` | `4ff2728e…933d` |
| `e_default` | default comparison append removed | `d6b260b1…c48a` | `d91f97f1…9faa` |

Diffs are in the artifacts directory: `diff_*.diff` (A0) and `diffA1_*.diff` (A1).

## Matrix A0 (ticket-pinned counter)

F=freeze, E=empty, J=junk, L=labelkeyed, B=sourceblind, D=duplicate, C=echo, M=sourcemisuse, P=pilot.

| mutant | F | E | J | L | B | D | C | M | P | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| `a_cells` | 0 | 0 | 0 | 12 | 14 | 0 | 1 | 2 | 2 | **SURVIVED** |
| `b_line` | 0 | 0 | 0 | 12 | 14 | 0 | 1 | 2 | 2 | **SURVIVED** |
| `b_dup` | 0 | 0 | 0 | 12 | 14 | 0→4 | 1 | 2→3 | 2 | KILLED |
| `c_novelty` | 0 | 0 | 0 | 12 | 14 | 0 | 1 | 2 | 2 | **SURVIVED** |
| `d_bounds` | 0 | 0 | 0 | 12→13 | 14→16 | 0→1 | 1→5 | 2 | 2 | KILLED |
| `e_identity` | 0 | 0 | 0 | 12 | 14 | 0 | 1→12 | 2 | 2 | KILLED |
| `e_default` | 0 | 0 | 0 | 12→14 | 14 | 0 | 1→2 | 2 | 2 | KILLED |

## Matrix A1 (current lane counter)

| mutant | F | E | J | L | B | D | C | M | P | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| `a_cells` | 0 | 0 | 0 | 7 | 9 | 0 | 1 | 1 | 1 | **SURVIVED** |
| `b_line` | 0 | 0 | 0 | 7 | 9 | 0 | 1 | 1 | 1 | **SURVIVED** |
| `b_dup` | 0 | 0 | 0 | 7 | 9 | 0→4 | 1 | 1→2 | 1 | KILLED |
| `c_novelty` | 0 | 0 | 0 | 7 | 9 | 0 | 1 | 1 | 1 | **SURVIVED** |
| `d_bounds` | 0 | 0 | 0 | 7→8 | 9→11 | 0→1 | 1→5 | 1 | 1 | KILLED |
| `e_identity` | 0 | 0 | 0 | 7 | 9 | 0 | 1 | 1 | 1 | **SURVIVED** |
| `e_default` | 0 | 0 | 0 | 7→8 | 9 | 0 | 1→2 | 1 | 1 | KILLED |

## Killed — controls, rises, and the flipped rows

| mutant | version | killer control(s) | rise | new counted rows (live evidence) |
|---|---|---|---|---|
| `b_dup` | A0, A1 | **duplicate** (evidential) | 0→4 both | F28-01 `n_predict` 400 `-1..2147483647`; F28-05 `top_k` 200→0 (base 40); F28-19/20 `temperature` 200→0.0 (base 0.8) |
| `b_dup` | A0, A1 | sourcemisuse (HOLD) | 2→3 / 1→2 | F28-18 `repeat_last_n` 400 `0..2147483647` |
| `d_bounds` | A0, A1 | **labelkeyed** (evidential) | 12→13 / 7→8 | F28-13 `n_cmpl`: claimed `0..INT32_MAX`, live `1..4` |
| `d_bounds` | A0, A1 | **sourceblind** (evidential) | 14→16 / 9→11 | F28-05 `n_cmpl` live `1..4`; F28-07 `t_max_predict_ms` live `-1..9223372036854775807` |
| `d_bounds` | A0, A1 | **duplicate** (evidential) | 0→1 both | F28-25 `repeat_penalty`: 400 `Failed to initialize samplers: penalty_repeat must be finite and greater than 0` — a 400 with **no** `Field '…'` message, admitted by status-only |
| `d_bounds` | A0, A1 | echo (HOLD) | 1→5 both | F28-17..20, bounds copied from the request value |
| `e_identity` | **A0 only** | echo (HOLD) only | 1→12 | F28-03..13, stored value equals the request within float32 tolerance |
| `e_identity` | **A1** | none | no rise | all 11 Echo rows are re-refused as `e:generic-conversion` (e.g. F28-03 `0.699999988079071`, F28-07 `0.5`, F28-08 `5`) |
| `e_default` | A0, A1 | **labelkeyed** (evidential) | 12→14 / 7→8 | F28-30 `dry_base` 200→1.75 (= base); A1 also catches F28-27 `seed` wrap as generic-conversion, so only F28-30 flips |
| `e_default` | A0, A1 | echo (HOLD) | 1→2 both | F28-16 `xtc_probability` 200→0.0 (= base) |

`e_identity` under A0 has **no evidential killer**: only CtlEcho (HOLD per
`controls/HOLDS.md`) rises. Under A1 it has no killer at all.

## Survivors — clauses no committed control exercises

Counts identical on all nine trees for each. Per-row `why` comparison shows how much of
each clause is nevertheless reached.

### `a_cells` — exercised, never count-determining (both versions)

- Only tag delta: DuplicateField F28-13, F28-16, F28-18, F28-21 lose `a:no-skill-row`;
  all four keep `b:set-not-one-key-equal-to-field` (F28-16 also duplicates), so the count
  stays 0.
- No committed control has a registry row whose SKILL cells disagree while the rest of the
  row is valid; every fixture generator writes matching cells. The one malformed table
  (SourceMisuse F28-17, cells wrapped in junk) passes the unmutated clause (a) because
  field/value/outcome/source are substring matches.
- The clause's *table-discovery* half is load-bearing in SourceMisuse's second committed
  run (`receipt-skill-ordering.json`: F28-01/F28-02 live-pass, refused only
  `a:no-skill-row` after a decoy table poisons `header_ok`). That receipt is not under
  `controls/*/fixture/`, and the mutant keeps the id+shape lookup, so it does not change
  that run. [INFERENCE] A mutant that drops clause (a) entirely would be killed there
  (0→2); not run (decoy tree not committed).

### `b_line` — exercised, never load-bearing alone (both versions)

- 43 rows lose `b:line-does-not-declare-field` with no count change (A0 tag delta;
  A1 counts are identical): 30 junk, 8 duplicate
  (F28-06/08/09/10/12/15/23/24), 4 sourcemisuse (F28-10..13), 1 echo (F28-21).
- Every one retains another refusal — overwhelmingly `d:not-shown`; the wrong-line rows
  are also rows whose live outcome is false (fabricated/ignored fields, aliases shadowed
  by `n_predict`, off-by-one lines on true fields). The declaring-line check never
  independently decides a row in the committed set.
- A row citing a non-declaring line (`set_desc`, `add_alias`, off-by-one, another
  field's line) with a true live outcome would count. SourceMisuse F28-10..13 attempted
  exactly this shape, but live (d) refused them first.

### `c_novelty` — never exercised (both versions)

- Zero tag changes on all nine trees. Every fixture cites S### absent at base:
  S140+, S700–S720, S8000+, S901–S926, S940–S950, S990/S991; base max is S139.
- SourceMisuse F28-14 (needed `L44` appears only inside `L440`) and F28-15 (wrong
  commit) exercise other parts of clause (c), not base novelty. A row citing a
  pre-existing base S### that names `server-schema.cpp`, the line and `704366d` would
  pass the surviving counter; no control attempts that citation.

### `e_identity` — A0 exercised only by a held control; subsumed under A1

- A0: 11 Echo rows flip when identity is dropped (F28-03..13); CtlEcho is HOLD, so no
  evidential control exercises it. All other trees are unchanged.
- A1: deleting identity changes nothing (1 counted on Echo before and after). The new
  `elif any(same(val, c) for c in conversions(sent))` refuses every one of those rows as
  `e:generic-conversion`; A1's `conversions()` includes the float32 rounding, the integer
  truncation and the 32/64-bit signed/unsigned wraps that produced the identity hits. The
  identity check is now redundant with the generic-conversion check for this control set.

## Drift note (A1 landed mid-wave)

- Commit `75b78bb` replaced the ticket's frozen counter while this seat was building
  trees. The ticket names `e6a706bb`/`d8bf1804`; that version is scored in the A0 table and
  is what the committed control receipts were produced with.
- A1 is **monotonically stricter**: it adds one refusal (`e:generic-conversion`) and
  changes identity only to read `sent` (same value as before). Therefore A1 baselines can
  only fall, and none of the committed controls can newly meet the target. Measured A1
  baselines are 0/0/0/7/9/0/1/1/1 — maximum 9, still 9 below the target of 18.
- The committed control receipts do **not** reproduce under A1 (labelkeyed 12→7,
  sourceblind 14→9, sourcemisuse 2→1, pilot 2→1). Those numbers above are out-of-band
  baselines on the reconstructed fixture trees, not the formal A1 control call.
- Mutation verdicts change only for `e_identity`: killed under A0 (held control only),
  survived under A1. `b_dup`, `d_bounds`, `e_default` stay killed; `a_cells`, `b_line`,
  `c_novelty` stay survivors.

## Caveats

- CtlEcho and CtlSourceMisuse are HOLD controls (`controls/HOLDS.md`); their receipts
  are frozen-counter outputs, not evidential control verdicts. `e_identity` A0 is the
  only kill naming a held control alone.
- `a_cells` keeps the six-cell shape and id binding, matching "drop clause a's cell
  checks"; it is not a "drop clause (a) entirely" mutant.
- The pilot tree is a reconstruction from the committed receipt shape (values, bounds,
  declaring lines); it reproduces both the A0 and A1 committed pilot receipts.
- This experiment scores counter behaviour only; it says nothing about whether a row's
  prose is true (the counter does not judge prose beyond six words).

## Exact commands

```sh
W=/fast/scratch/hyaku/kama-r28/w1/MutCounterClauses
C=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/controls
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE

# scratch base repo and the two counter versions
timeout 300 git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin "$W/repo"
R=d8bf1804ce52c30343f3e41cbae41c9640db9a64
timeout 60 git -C "$W/repo" show "$R:.ufo/waves/round-28/count-c1.py" > "$W/counters/noop.py"
timeout 60 git -C "$W/repo" show 75b78bb:.ufo/waves/round-28/count-c1.py > "$W/counters/current-A1.py"
sha256sum "$W/counters/noop.py" "$W/counters/current-A1.py"   # e6a706bb… ; a38faefe…

# per tree: the four paths the counter reads
for t in freeze empty junk labelkeyed sourceblind duplicate echo sourcemisuse pilot; do
  d="$W/trees/$t"; mkdir -p "$d/corpus" "$d/registry" "$d/.ufo/waves/round-28/sources/llama.cpp-704366d"
  timeout 60 git -C "$W/repo" show "$R:SKILL.md" > "$d/SKILL.md"
  timeout 60 git -C "$W/repo" show "$R:corpus/SOURCES.md" > "$d/corpus/SOURCES.md"
  timeout 60 git -C "$W/repo" show "$R:.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp" > "$d/.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp"
done

# fixtures
printf '\n## Round-28 request-field outcomes\n\n| id | field | value | outcome | meaning | source |\n|---|---|---|---|---|---|\n' >> "$W/trees/empty/SKILL.md"
printf '{"rows": []}\n' > "$W/trees/empty/registry/request-field-outcomes-r28.json"
cat "$C/CtlJunk/fixture/SKILL-section.md"        >> "$W/trees/junk/SKILL.md"
cat "$C/CtlJunk/fixture/SOURCES-additions.md"    >> "$W/trees/junk/corpus/SOURCES.md"
cp "$C/CtlJunk/fixture/request-field-outcomes-r28.json" "$W/trees/junk/registry/"
cat "$C/CtlLabelKeyed/fixture/SKILL-section.md"  >> "$W/trees/labelkeyed/SKILL.md"
cat "$C/CtlLabelKeyed/fixture/SOURCES-rows.md"   >> "$W/trees/labelkeyed/corpus/SOURCES.md"
cp "$C/CtlLabelKeyed/fixture/request-field-outcomes-r28.json" "$W/trees/labelkeyed/registry/"
cat "$C/CtlSourceBlind/fixture/SKILL.add.md"     >> "$W/trees/sourceblind/SKILL.md"
cat "$C/CtlSourceBlind/fixture/SOURCES.add.md"   >> "$W/trees/sourceblind/corpus/SOURCES.md"
cp "$C/CtlSourceBlind/fixture/registry/request-field-outcomes-r28.json" "$W/trees/sourceblind/registry/"
cat "$C/CtlDuplicateField/fixture/SKILL-section.md" >> "$W/trees/duplicate/SKILL.md"
cat "$C/CtlDuplicateField/fixture/SOURCES-rows.md"  >> "$W/trees/duplicate/corpus/SOURCES.md"
cp "$C/CtlDuplicateField/fixture/registry/request-field-outcomes-r28.json" "$W/trees/duplicate/registry/"
cat "$C/CtlSourceMisuse/fixture/SKILL-section.md" >> "$W/trees/sourcemisuse/SKILL.md"
cat "$C/CtlSourceMisuse/fixture/SOURCES-rows.md"  >> "$W/trees/sourcemisuse/corpus/SOURCES.md"
cp "$C/CtlSourceMisuse/fixture/request-field-outcomes-r28.json" "$W/trees/sourcemisuse/registry/"
cd "$W/trees/echo" && timeout 60 git apply "$C/CtlEcho/fixture/fixture.diff"
# pilot: registry + SKILL section + S990/S991 rows written from before/pilot-receipt.json
# (F28-90 n_cache_reuse -1 reject 0..2147483647 L67; F28-91 xtc_threshold 1.5 -> 1.0 L108)

# A0: baselines, then mutants — sequential, one server at a time
for t in freeze empty junk labelkeyed sourceblind duplicate echo sourcemisuse pilot; do
  env -i PATH=/usr/bin:/bin HOME=/home/vgpnk LANG=C.UTF-8 timeout 900 \
    /usr/bin/python3 "$W/counters/noop.py" --lane "$W/trees/$t" --repo "$W/repo" \
    --out "$W/receipts/noop-$t.json"
done
timeout 120 /usr/bin/python3 "$W/make_mutants.py"   # asserts frozen sha, one occurrence each
for m in a_cells b_line b_dup c_novelty d_bounds e_identity e_default; do
  for t in freeze empty junk labelkeyed sourceblind duplicate echo sourcemisuse pilot; do
    env -i PATH=/usr/bin:/bin HOME=/home/vgpnk LANG=C.UTF-8 timeout 900 \
      /usr/bin/python3 "$W/mutants/m_${m}.py" --lane "$W/trees/$t" --repo "$W/repo" \
      --out "$W/receipts/mut-${m}-${t}.json"
  done
done

# A1 addendum: same trees, A1-derived mutants (the two clause-e mutants adapted for if/elif)
timeout 120 /usr/bin/python3 "$W/make_mutants_a1.py"   # asserts A1 sha
for t in freeze empty junk labelkeyed sourceblind duplicate echo sourcemisuse pilot; do
  env -i PATH=/usr/bin:/bin HOME=/home/vgpnk LANG=C.UTF-8 timeout 900 \
    /usr/bin/python3 "$W/counters/current-A1.py" --lane "$W/trees/$t" --repo "$W/repo" \
    --out "$W/receipts/a1-noop-$t.json"
done
for m in a_cells b_line b_dup c_novelty d_bounds e_identity e_default; do
  for t in freeze empty junk labelkeyed sourceblind duplicate echo sourcemisuse pilot; do
    env -i PATH=/usr/bin:/bin HOME=/home/vgpnk LANG=C.UTF-8 timeout 900 \
      /usr/bin/python3 "$W/mutants-a1/m_${m}.py" --lane "$W/trees/$t" --repo "$W/repo" \
      --out "$W/receipts/a1-mut-${m}-${t}.json"
  done
done
ss -ltnp | grep -E ':476[0-1][0-9]' || echo ports-clear
```

## Cleanup and tooling

- No lane-repo or fleet-repo git/jj write; no edit of either counter, `SKILL.md`,
  `SOURCES.md`, `QUALITY.md`, `tools/`, `registry/`, `MANIFEST.json`, `.ufo/state` or the
  watchdog log. Outputs are this report plus `out/MutCounterClauses-2/`.
- No listener on 47600–47619 and no `llama-server --port 476xx` process after the runs;
  the pre-existing sibling servers on 48212/48216 were left alone.
- Tool installs: none. No pacman transactions.
