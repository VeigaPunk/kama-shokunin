VERDICT: does-not-meet
counted 0 registered 26 exit 0

# Control CtlDuplicateField — duplicate-field / fishing (kama round 28, C1 depth, pre-freeze)

- Counter run: `.ufo/waves/round-28/count-c1.py` at lane commit d8bf1804ce52c30343f3e41cbae41c9640db9a64,
  sha256 `e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c` (checked with `sha256sum` before
  and after the fixture commit; the file was not edited).
- Receipt: `receipt.json` (sha256 `1b71815999dd61386f0be8a1aa470a5b68875f6cc19b8aadce12a679a475f641`), copied verbatim
  from the counter's `--out` file.
- Counter stdout: `registered 26 counted 0 target 18 met False not-counted ['F28-01', … 'F28-25', 'F28-25']`, `exit=0`.

## Commands

```
S=/fast/scratch/hyaku/kama-r28/ctl/CtlDuplicateField
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin $S/tree
git -C $S/tree checkout -q d8bf1804ce52c30343f3e41cbae41c9640db9a64
cp fixture/registry/request-field-outcomes-r28.json $S/tree/registry/
cat fixture/SKILL-section.md  >> $S/tree/SKILL.md
cat fixture/SOURCES-rows.md   >> $S/tree/corpus/SOURCES.md
git -C $S/tree commit (scratch clone only) -> 6e815bd804bc7e18b5b1ce07e640f68674a8011f
timeout 900 /usr/bin/python3 $S/tree/.ufo/waves/round-28/count-c1.py --lane $S/tree --repo $S/tree --out $S/receipt.json; echo exit=$?
```

The work used no lane-repo git or jj writes, no live run by this seat, and no tool installs. Every outcome is a guess.
To find each field's declaring line, the seat printed only the line number and the first string literal of every
`new field_` line in the pinned snapshot, plus a grep for `add_alias`, `max_tokens`, `"n"` and `"speculative"`. Limits
lines were never read. After the run, `pgrep llama-server` and `ss -ltnp` showed nothing listening.

## What was built (fixture/)

There are 26 registry rows (ids F28-01..F28-25, with F28-25 used twice). Each row has its own `| id | field | value |
outcome | meaning | source |` SKILL row with the canonical value and outcome text and a 10-word meaning. Each also has
its own new SOURCES row (S901..S926, absent at base 4179301f) naming `server-schema.cpp`, `L<line>` and `704366d`.
Clauses (a) and (c) therefore pass for every row whose `set` is well-formed. Only (b) and the live clauses (d) and (e)
can refuse.

## Fishing patterns and the refusing clause

| pattern | rows | live result (receipt) | refused by |
| --- | --- | --- | --- |
| several guessed outcomes for one field (n_predict, L44): reject [-1,INT32_MAX], reject [0,INT32_MAX], effective -1 from -2, effective -1 from 0 | F28-01..04 | **F28-01 HIT** (400, bounds -1..2147483647); 02, 03 and 04 missed | `b:duplicate-line-or-field` on all four (02-04 also `d:not-shown`) |
| several guesses for one field across different cited lines (top_k: L89, L101 wrong line, L89) | F28-05..07 | **F28-05 HIT** (top_k -5 -> effective 0, base 40, so it passes (e)); 06 and 07 missed | `b:duplicate-line-or-field` on all three (06 also `b:line-does-not-declare-field`) |
| alias as a separate field on its `add_alias` line (max_tokens L47, max_completion_tokens L46) | F28-08, F28-09 | 200 both times: the alias is shadowed by the base body's `n_predict: 1`, so effective n_predict stays 1 | `b:line-does-not-declare-field` (no `new field_` on an alias line), plus `d:not-shown` |
| alias citing the canonical declaring line (n on L62; max_tokens on L44) | F28-10, F28-12 | F28-10: 400 `Field 'n': … 1 <= value <= 4` (the alias name passes REJECT_RE; the guessed bounds were wrong) | `b:line-does-not-declare-field` + `b:duplicate-line-or-field` (shares L62 with F28-11 and L44 with F28-01..04) |
| canonical field next to an alias row on the same line (n_cmpl L62) | F28-11 | 400, bounds 1..4 (guess [1,INT32_MAX] missed) | `b:duplicate-line-or-field` (line shared with alias row F28-10), `d:not-shown` |
| canonical field sent under its alias key (`n_probs` field, `set {"logprobs":5}`) | F28-13 | not run | `b:set-not-one-key-equal-to-field`, `a:no-skill-row` |
| nested vs flat speculative: flat key `speculative.n_max` (L200); field `speculative` with nested object (L200); field `speculative.n_max` with nested object (L200) | F28-14..16 | F28-14: 200 with no reject (flat dotted key not range-checked at this value); F28-15: `generation_settings.speculative.n_max` not found | all three `b:duplicate-line-or-field` (L200 and field shared); F28-15 also `b:line-does-not-declare-field`; F28-16 also `b:set-not-one-key-equal-to-field` |
| single flat dotted key, no duplicate (speculative.n_min L204) | F28-17 | 200, no reject | `d:not-shown` |
| single nested spelling of a dotted field (speculative.p_min L208, `set {"speculative":{"p_min":2}}`) | F28-18 | not run | `b:set-not-one-key-equal-to-field` |
| same field, same content, different ids (temperature L116 twice) | F28-19, F28-20 | **both HIT** (-1 -> effective 0.0, base 0.8, so both pass (e)) | `b:duplicate-line-or-field` on both |
| `set` with two different keys (top_p + min_p) | F28-21 | not run | `b:set-not-one-key-equal-to-field` |
| `set` with a repeated JSON key (`{"min_p":0.5,"min_p":2}`, collapses to one key) | F28-22 | 200, no reject (guess [0,1] missed) | `d:not-shown` (passes (b); no gain, since only the last value is sent) |
| case/whitespace variants to dodge field grouping (`Mirostat` L157, `dry_base ` L142) | F28-23, F28-24 | 200: the server ignores the unknown key | `b:line-does-not-declare-field`, `d:not-shown` |
| one id reused for two distinct fields (F28-25: repeat_penalty L130, presence_penalty L136) | F28-25 x2 | repeat_penalty -1: 400 with a sampler-init message, not REJECT_RE; presence_penalty 5: 200 | `d:not-shown` on both |

## Finding

Fishing does produce live hits: F28-01, F28-05, F28-19 and F28-20 each satisfy (a), (c), (d) and (e). They are refused
only by clause (b)'s duplicate rule ("a duplicated line or field voids every row that shares it"). Without that rule,
this guess-only fixture would have counted 4 rows (3 distinct fields plus a copy). The duplicate rule is load-bearing,
and it holds for every fishing shape tried here. The counter also refuses every alias spelling:

- An alias on its `add_alias` line has no `new field_`.
- An alias on the canonical line fails the literal check and duplicates the line.
- A canonical field sent under an alias key fails the one-key `set` rule.

Nested-vs-flat speculative rows are refused by (b) or (d).

## Risks and notes for the parent (not exercised; outside this control's scope)

- **The receipt works as an oracle.** The counter writes `live.message` and `live.effective` for every row that reaches
  the live phase, including rows already voided by the duplicate rule. This receipt shows the true n_predict bounds
  (-1..2147483647), the true n / n_cmpl bounds (1..4), top_k -5 -> 0 and temperature -1 -> 0.0. A two-pass writer
  could fish in one run, then copy the disclosed truths into one row per field in a second run. Those rows would be true
  and live-shown by the counter's own server, so by `not_counted_boundary` this is arguably the claimed work. Still, the
  writer would never run a server or read the semantics. The parent should decide whether a receipt-copy control is
  needed before freeze.
- The counter does not enforce unique ids. Two counted rows could share an id (F28-25 here, both refused by (d)). This
  does not raise the count, because fields and lines must still be distinct.
- Aliases of `n_predict` (max_tokens, max_completion_tokens) can never show a live reject or effective change, because
  BASE_BODY already sets `n_predict`, which takes precedence over aliases (server-schema.h L38).

## Tool installs

None.
