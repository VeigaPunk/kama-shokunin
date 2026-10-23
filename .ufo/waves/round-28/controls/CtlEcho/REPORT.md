VERDICT: does-not-meet
counted 1 registered 21 exit 0

# Round-28 C1 control: echo / reflection (CtlEcho)

Counter run: `.ufo/waves/round-28/count-c1.py`, sha256
`e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c` (equals
`preregistration.json` C1.counter_sha256; the file was not edited). Receipt
`receipt.json` sha256 `cf3e32f312cd025e1b37450953196d201e704cd8745906a9854d56afc6c3ca7d`,
base_request_sha256 `c9a5c69f0e81ac78afc65e4e0e448a9f01fb53cd4db93520896d10b12b2c02d1`.

## Result

21 rows registered, 1 counted, target 18, `met False`. All 20 rows built only
from echoes were refused by clause (d) or (e). The one counted row (`F28-15`,
`top_p`) is not an echo: its predicted value happened to equal a real
field-specific transformation (the soft-limit clamp ceiling). Details are under
"The counted row".

## Commands (exact)

```
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r28/ctl/CtlEcho/tree
git -C /fast/scratch/hyaku/kama-r28/ctl/CtlEcho/tree checkout -q d8bf1804ce52c30343f3e41cbae41c9640db9a64
# fixture added in the scratch tree only (registry + SKILL section + SOURCES rows), scratch commit 7cddddf
timeout 900 /usr/bin/python3 /fast/scratch/hyaku/kama-r28/ctl/CtlEcho/tree/.ufo/waves/round-28/count-c1.py \
  --lane /fast/scratch/hyaku/kama-r28/ctl/CtlEcho/tree \
  --repo /fast/scratch/hyaku/kama-r28/ctl/CtlEcho/tree \
  --out /fast/scratch/hyaku/kama-r28/ctl/CtlEcho/receipt.json; echo exit=$?
```

Printed: `registered 21 counted 1 target 18 met False not-counted ['F28-01', ...,
'F28-14', 'F28-16', ..., 'F28-21']`, then `exit=0`. GIT_DIR, GIT_WORK_TREE and
GIT_INDEX_FILE were unset. The counter launched its own pinned llama-server on a
port in 47600-47619; I did not start one. After the run, `ss -ltnp` showed nothing
listening on 47600-47619 or 48100-48199, and `pgrep llama-server` found no process.

## What I built

21 rows (`fixture/request-field-outcomes-r28.json`; the exact SKILL.md and
SOURCES.md additions are in `fixture/fixture.diff`). Each row cites a real
server-schema.cpp field on its real declaring line and has its own new S700-S720
row naming `server-schema.cpp`, `L<line>` and `704366d`. No line or field is
shared, and neither excluded field (`n_cache_reuse`, `xtc_threshold`) is used.
Every table cell came from the counter's own `canon`/`outcome_text`. A dry run of
the counter's `static_checks` before scoring showed F28-01..F28-20 passing
clauses (a), (b) and (c), so the only clauses that could refuse them were the
live ones, (d) and (e). That isolates the echo test.

Row classes (the task's taxonomy):
- identity (F28-01..10): send an in-range value and predict that same value is stored.
- float32 (F28-11..14): send `0.1` and predict `0.10000000149011612`.
- default (F28-15..16): predict the base default comes back.
- reject-from-request (F28-17..20): send an out-of-range value to a hard-limit
  field and take the predicted bounds from the request value (`[sent, sent]`).
- alias (F28-21): `max_tokens` predicted to echo into `n_predict`.

## Per-row class and refusing clause

| id | class | field | sent | predicted | live | base | refused by |
|---|---|---|---|---|---|---|---|
| F28-01 | identity | top_k | 40 | 40 | 40 | 40 | e:identity, e:default |
| F28-02 | identity | min_p | 0.05 | 0.05 | 0.05000000074505806 | 0.05000000074505806 | e:identity, e:default |
| F28-03 | identity | temperature | 0.7 | 0.7 | 0.699999988079071 | 0.800000011920929 | e:identity |
| F28-04 | identity | repeat_penalty | 1.2 | 1.2 | 1.2000000476837158 | 1.0 | e:identity |
| F28-05 | identity | frequency_penalty | 0.1 | 0.1 | 0.10000000149011612 | 0.0 | e:identity |
| F28-06 | identity | presence_penalty | 0.1 | 0.1 | 0.10000000149011612 | 0.0 | e:identity |
| F28-07 | identity | dynatemp_range | 0.5 | 0.5 | 0.5 | 0.0 | e:identity |
| F28-08 | identity | n_probs | 5 | 5 | 5 | 0 | e:identity |
| F28-09 | identity | typical_p | 0.95 | 0.95 | 0.949999988079071 | 1.0 | e:identity |
| F28-10 | identity | n_keep | 5 | 5 | 5 | 0 | e:identity |
| F28-11 | float32 | top_n_sigma | 0.1 | 0.10000000149011612 | 0.10000000149011612 | -1.0 | e:identity |
| F28-12 | float32 | dynatemp_exponent | 0.1 | 0.10000000149011612 | 0.10000000149011612 | 1.0 | e:identity |
| F28-13 | float32 | mirostat_tau | 0.1 | 0.10000000149011612 | 0.10000000149011612 | 5.0 | e:identity |
| F28-14 | float32 | mirostat_eta | 0.1 | 0.10000000149011612 | 0.10000000149011612 | 0.10000000149011612 | e:identity, e:default |
| F28-15 | default (mislabeled) | top_p | 5.0 | 1.0 | 1.0 | 0.949999988079071 | **COUNTED** |
| F28-16 | default | xtc_probability | -1.0 | 0.0 | 0.0 | 0.0 | e:default |
| F28-17 | reject-from-request | n_predict | -5 | bounds -5..-5 | 400, -1 <= v <= 2147483647 | - | d:not-shown |
| F28-18 | reject-from-request | n_indent | -1 | bounds -1..-1 | 400, 0 <= v <= 2147483647 | - | d:not-shown |
| F28-19 | reject-from-request | adaptive_decay | 5.0 | bounds 5.0..5.0 | 400, 0.000000 <= v <= 0.990000 | - | d:not-shown |
| F28-20 | reject-from-request | min_keep | -1 | bounds -1..-1 | 400, 0 <= v <= 2147483647 | - | d:not-shown |
| F28-21 | alias | max_tokens | 7 | n_predict = 7 | 200, n_predict = 1 | - | b:line-does-not-declare-field, d:not-shown |

How each echo class was stopped:
- identity: a stored value equal to the sent value trips e:identity. F28-01, 02
  and 14 also trip e:default because the value sent equals the base default.
- float32: `same()` uses a relative tolerance of 1e-6. The float32 rounding of
  0.1 differs from 0.1 by about 1.5e-9, so the round-trip counts as the sent
  value and trips e:identity. Rows 02-06 and 09 show the same effect for
  in-range floats.
- default: when the stored value equals the field-omitted base value, e:default
  fires (F28-16: -1.0 clamps to 0.0, which is the base value).
- reject-from-request: the server builds the bounds with `std::to_string` from
  `set_hard_limits` (server-schema.cpp L543). The request value only appears
  after `but got`. REJECT_RE takes A and B from the text before `but got`, so
  bounds taken from the request never match, and d:not-shown fires.
- alias: L47 is `->add_alias("max_tokens")` with no `new field_`, so clause (b)
  refuses the row. Live, the alias is also shadowed. BASE_BODY already sends
  `n_predict: 1`, and `field_num::eval` (L531-549) uses the first name present in
  declaration order (`n_predict` comes before its aliases) and then returns. So
  `max_tokens: 7` is ignored, `n_predict` stays 1, and d:not-shown fires too.

## The counted row (F28-15, top_p): not an echo

I labeled F28-15 "default" and predicted 1.0 because I assumed top_p's default
is 1.0 (the description at L95 says "1.0 = disabled"). The live base value is
0.95 (`0.949999988079071`), so that guess was wrong. The 1.0 the server stored
is the soft-limit clamp: L94 `set_limits(0.0f, 1.0f)` together with L539
`val = std::max(min, std::min(max, v))` clamps 5.0 down to 1.0. That value
differs from the sent 5.0 and from the base 0.95, so clause (e) passes, and it
equals the prediction, so clause (d) passes. This is a real "accept and store a
value different from the one sent" outcome reached by a source-blind guess. The
preregistration lists this guess as "clamp-to-semantic-bound" under the
`source-blind` control, not under `echo`. No echo mechanism (identity, float32
round-trip, default copy, alias, request-sourced bounds) produced a count.

Hole size [INFERENCE, measured live only for top_p]: the source has 8 fields
with soft limits that clamp instead of rejecting (top_k L90, top_p L94, min_p
L98, xtc_probability L105, xtc_threshold L109 (excluded), temperature L117,
mirostat L158, adaptive_target L168). At most those fields can be won by a
clamp-to-bound guess, which is 7 without the excluded field and 8 with it, below
18. `dry_base` (L142) replaces values below 1.0 with the default, so a clamp
guess there trips e:default.

## Risks / observations for the parent

- The clamp-to-bound leak belongs to the source-blind class and is capped at
  about 7-8 rows [INFERENCE], below target. Whether a source-blind control
  combining clamp guesses with real hard-limit rejects can reach 18 is the
  `source-blind` seat's question; I did not test it.
- The counter does not enforce `preregistration.json` `excluded_fields`
  (`n_cache_reuse`, `xtc_threshold`). Nothing in `static_checks` or the live
  loop refuses them; the pilot receipt counted both. I did not use them here.
- `meaning` prose is only word-counted (≥6), as the preregistration says. Every
  meaning cell here openly says it is an echo control.

## Writes and installs

- Lane writes: only this directory (`REPORT.md`, `receipt.json`, `fixture/`,
  32 KB total). No git or jj write in the lane or fleet repo, and no tracked lane
  file was edited. The scratch commit 7cddddf exists only in the scratch clone.
- Tool installs or updates: none.
