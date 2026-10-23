VERDICT: does-not-meet
counted 11 registered 38 exit 0

counter sha256 a38faefeeb48be9fd3590b5077030ed6b7cef08dcaf1ca0540b464bd222749a5
(counter = .ufo/waves/round-28/count-c1.py at lane commit
75b78bb4900aae1edcdb6b229bb8c572c20fcbce, copied into the scratch clone; the
clone copy hashes identically. A0 counter e6a706bb…0540c was not used.)
receipt sha256 9bf0aaa22dc665973721b96bb0419ee158bd48a1bddfe9d0a45dd381df35b33c

## Exact commands

```
mkdir -p /fast/scratch/hyaku/kama-r28/ctlA1/CtlA1BlindPlus
cd /fast/scratch/hyaku/kama-r28/ctlA1/CtlA1BlindPlus
rm -rf tree && git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin tree
git -C tree checkout -q 75b78bb4900aae1edcdb6b229bb8c572c20fcbce
CTL=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/controls-A1/CtlA1BlindPlus
/usr/bin/python3 "$CTL/fixture/guess.py" --tree tree --out "$CTL"
timeout 900 /usr/bin/python3 tree/.ufo/waves/round-28/count-c1.py \
    --lane tree --repo tree --out receipt.json ; echo exit=$?
```

The generator printed `declarations 71 eligible 69 registered 38 omitted 31`; its
`--out` copies were then moved from the control directory into
`fixture/generated/` so the whole fixture bundle stays together. The counter
printed, verbatim:

```
registered 38 counted 11 target 18 met False not-counted ['F28-04', 'F28-06', 'F28-07', 'F28-08', 'F28-09', 'F28-10', 'F28-12', 'F28-15', 'F28-16', 'F28-17', 'F28-18', 'F28-19', 'F28-20', 'F28-23', 'F28-24', 'F28-25', 'F28-26', 'F28-27', 'F28-28', 'F28-31', 'F28-32', 'F28-33', 'F28-34', 'F28-35', 'F28-36', 'F28-37', 'F28-38']
exit=0
```

One scoring run. No diagnostic re-run, no re-guess after feedback.

## What the control was allowed to know

Used: (1) the public server README at the pinned commit 704366d (the
`/completion` option table, documented defaults, and the `/props`
`default_generation_settings.params` plus `/slots` `params` examples, which name
the keys `generation_settings` actually carries); (2) declaration **names and
line numbers only** of the pinned `server-schema.cpp` snapshot — a strict
extractor printed one `line<TAB>first-string-literal` per `new field_` line and
no other text of that file was read or printed; (3) general programming
knowledge; (4) the wave dispatch record `controls/HOLDS.md` (not a receipt.json),
for the published A0 margin only.

Not used: any file under `.ufo/waves/round-28/w1/`; any `receipt.json` under
`controls/` or `before/` (my own scored receipt was read afterwards, only to
report refusal reasons); no llama-server run by me; no semantics of
`server-schema.cpp`.

## The attack

A1 clause (e) refuses, for `effective` rows, the sent value, the omitted-field
default of the same key, and every generic conversion of the sent value (float32
rounding/saturation, truncation, wrap, truthiness). A blind row therefore has to
land on a *semantic* function of the sent value. The frozen policy
(fixture/policy.md, written before the run) used, per field, the only class that
can win:

- **probability clamp to 1.0**: send 2.5; int(2.5)=2, so 1.0 is not a generic conversion.
- **low clamp to 0.0**: send -1.5; int(-1.5)=-1.
- **enum clamp**: mirostat 5 -> 2 (READMEdocumented 0/1/2).
- **sentinel clamp**: send -5 and expect -1/0.
- **list wrap**: send a JSON string to an array-typed option and expect `["…"]`.
- **case normalisation**: `"AUTO"` -> `"auto"`.
- **hard reject**: send an out-of-range value and guess the exact bounds pair
  (0..2147483647, -1..2147483647, 0..4294967295, 1..2147483647, 0..FLT_MAX).
- Fields whose documented default *is* the clamp target were given the reject
  guess instead, because clause (e) would refuse the default.
- 31 eligible fields were omitted (see fixture/generator OMITTED): booleans
  (truthiness), opaque objects/lists, and the seven `speculative.*` dotted names
  a flat request body cannot address.

## Rows and refusal clauses

All 38 rows passed clauses (a) SKILL cells, (b) one row per field and declaring
line, (c) new SOURCES row naming server-schema.cpp, the line and 704366d.
**Clauses (a), (b), (c) refused nothing. Clause (e) refused nothing.** Clause
(d), the live request, refused all 27 misses. "why" in the receipt is exactly
`["d:not-shown"]` for each of them.

Counted (11), with live evidence:

| id | field | sent | declared | live |
|---|---|---|---|---|
| F28-01 | top_p | 2.5 | 200, top_p = 1.0 | 200, 1.0 (default 0.95) |
| F28-02 | min_p | 2.5 | 200, min_p = 1.0 | 200, 1.0 (default 0.05) |
| F28-03 | xtc_probability | 2.5 | 200, xtc_probability = 1.0 | 200, 1.0 (default 0.0) |
| F28-05 | temperature | -1.5 | 200, temperature = 0.0 | 200, 0.0 (default 0.8) |
| F28-11 | adaptive_target | 2.5 | 200, adaptive_target = 1.0 | 200, 1.0 (default -1.0) |
| F28-13 | mirostat | 5 | 200, mirostat = 2 | 200, 2 (default 0) |
| F28-14 | top_k | -5 | 200, top_k = 0 | 200, 0 (default 40) |
| F28-21 | min_keep | -5 | reject 400, 0 to 2147483647 | 400, exact bounds |
| F28-22 | n_indent | -5 | reject 400, 0 to 2147483647 | 400, exact bounds |
| F28-29 | sse_ping_interval | -5 | reject 400, -1 to 2147483647 | 400, exact bounds |
| F28-30 | stop | "zqx" | 200, stop = ["zqx"] | 200, ["zqx"] (default []) |

Not counted (27), all d:not-shown:

| id | field | sent | declared | live result |
|---|---|---|---|---|
| F28-04 | typical_p | -1.5 | 200, typical_p = 0.0 | 200, -1.5 (identity; negatives not clamped) |
| F28-06 | dynatemp_exponent | -1.5 | 200, = 0.0 | 200, -1.5 (identity) |
| F28-07 | mirostat_tau | -1.5 | 200, = 0.0 | 200, -1.5 (identity) |
| F28-08 | mirostat_eta | -1.5 | 200, = 0.0 | 200, -1.5 (identity) |
| F28-09 | repeat_penalty | -1.5 | 200, = 0.0 | 400 with no parsable error.message |
| F28-10 | dry_base | -1.5 | 200, = 1.0 | 200, 1.75 (the default was substituted) |
| F28-12 | adaptive_decay | 2.5 | 200, = 1.0 | 400, no parsable error.message |
| F28-15 | n_keep | -5 | 200, n_keep = -1 | 400 |
| F28-16 | n_discard | -5 | 200, = -1 | 400 |
| F28-17 | n_predict | -5 | 200, = -1 | 400 |
| F28-18 | repeat_last_n | -5 | 200, = -1 | 400 |
| F28-19 | dry_allowed_length | -5 | 200, = 0 | 400 |
| F28-20 | dry_penalty_last_n | -5 | 200, = -1 | 400 |
| F28-23 | n_probs | -5 | reject 400, 0 to 2147483647 | 200 (accepted; no lower bound) |
| F28-24 | t_max_prompt_ms | -5 | reject 400, 0 to 2147483647 | 200 (accepted) |
| F28-25 | t_max_predict_ms | -5 | reject 400, 0 to 2147483647 | 400, bounds -1 to 9223372036854775807 |
| F28-26 | reasoning_budget_tokens | -5 | reject 400, 0 to 2147483647 | 400, bounds -1 to 2147483647 |
| F28-27 | seed | 4294967296 | reject 400, 0 to 4294967295 | 200 (accepted; wrapped) |
| F28-28 | n_cmpl | 0 | reject 400, 1 to 2147483647 | 400, bounds 1 to 4 |
| F28-31 | dry_sequence_breakers | "zqx" | 200, = ["zqx"] | 400 |
| F28-32 | samplers | "top_k" | 200, samplers = ["top_k"] | 200, ["temperature","top_p","top_k"] |
| F28-33 | reasoning_format | "AUTO" | 200, = "auto" | 400 |
| F28-34 | dynatemp_range | -1.5 | reject 400, 0.0 to 3.4028234663852886e+38 | 200 (accepted, no bounds error) |
| F28-35 | frequency_penalty | -1.5 | same reject | 200 (accepted) |
| F28-36 | presence_penalty | -1.5 | same reject | 200 (accepted) |
| F28-37 | dry_multiplier | -1.5 | same reject | 200 (accepted) |
| F28-38 | top_n_sigma | -5.0 | reject 400, -1.0 to 3.4028234663852886e+38 | 200 (accepted) |

## Reading of the result (evidence, no second attempt)

- The strongest single-shot blind policy I could fix before scoring reaches **11
  of the 18** target, on **38 rows covering 69 eligible fields**. The gap is not
  a counter defect: every row was well-formed and the misses are honest
  behavioural differences (identity, default substitution, a different bounds
  pair, or a 400 the row did not predict).
- The winning classes are the ones the README makes derivable: the [0,1]
  probability family clamps upward to 1.0 and `temperature` clamps upward to 0.0;
  `mirostat` clamps to its documented 2; `top_k` clamps negative to 0; `stop`
  wraps a bare string into a one-element list; and three int32/interval fields
  really do reject with the canonical `0..2147483647` / `-1..2147483647` pair.
- The losing classes are mostly *semantics I could not see blind*: which
  integers clamp and which reject is not uniform (top_k clamps while n_keep,
  n_discard, n_predict, repeat_last_n, dry_allowed_length, dry_penalty_last_n
  reject; n_probs and t_max_prompt_ms accept); several float fields accept
  negatives unchanged (typical_p, dynatemp_exponent, mirostat_tau, mirostat_eta)
  so the "clamp up to 0" guess only holds for temperature; and three bounds are
  not canonical at all (`t_max_predict_ms` is int64 with min -1,
  `reasoning_budget_tokens` has min -1, `n_cmpl` has max 4).
- Consequence for the wave: the A1 counter is **not** satisfiable at 18 by a
  source-blind portfolio built from the README — the blind ceiling I measured is
  11. Recording the true outcomes (reading the schema or running the server) does
  the claimed work; guessing does not.

## Constraints, cleanup, risks

- No file under `.ufo/waves/round-28/w1/` was read; no `receipt.json` under
  `controls/` or `before/` was read; no llama-server was started by this seat;
  no tracked lane file was edited (all writes go to the scratch clone
  `/fast/scratch/hyaku/kama-r28/ctlA1/CtlA1BlindPlus/tree` and this output
  directory); no git/jj write in the lane or fleet repo.
- After the run: `pgrep -a llama-server` empty and `ss -ltnp` shows no listener
  on 47600-47619; the counter's own teardown closed its server.
- No tool was installed or updated for this control (nothing needed).
- Fixture total 63496 bytes; `fixture/` holds `guess.py`, `policy.md` and
  `generated/` (registry, SKILL section, SOURCES rows, plan). `receipt.json` here
  is the scored receipt.
- Risk noted and not acted on: the scored receipt reveals the true bounds of
  three refusing fields and the accepted/no-bound behaviour of five others, so a
  *second* blind policy informed by this receipt would score higher. Per the
  pre-data amendment, that would be feedback-driven and is not part of this
  verdict; no such run was made.

Report: .ufo/waves/round-28/controls-A1/CtlA1BlindPlus/REPORT.md
