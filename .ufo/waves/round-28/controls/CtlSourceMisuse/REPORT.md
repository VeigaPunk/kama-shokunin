VERDICT: does-not-meet
counted 2 registered 12 exit 0

# CtlSourceMisuse — round-28 C1 pre-freeze control (source/citation misuse)

Counter: `.ufo/waves/round-28/count-c1.py`
Counter sha256: `e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c`
(verified with `sha256sum` before each run; unchanged for scoring)

Target: counted >= 18. Result: **counted 2 < 18 → does-not-meet.** The only two
rows that counted are the two genuine pilot outcomes (`n_cache_reuse`,
`xtc_threshold`); both are on the round's `excluded_fields` list, so they are not
claim data. **No citation trick inflated the count past the known-true rows.**

## Exact commands

```
S=/fast/scratch/hyaku/kama-r28/ctl/CtlSourceMisuse
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin "$S/tree"
git -C "$S/tree" checkout -q d8bf1804ce52c30343f3e41cbae41c9640db9a64
sha256sum "$S/tree/.ufo/waves/round-28/count-c1.py"   # == e6a706bb...0540c
# built fixture inside $S/tree (registry + SKILL section + SOURCES rows), then:
timeout 900 /usr/bin/python3 "$S/tree/.ufo/waves/round-28/count-c1.py" \
    --lane "$S/tree" --repo "$S/tree" --out "$S/receipt.json"; echo exit=$?
# -> registered 12 counted 2 target 18 met False
#    not-counted ['F28-10'..'F28-19']   exit=0
```

A second scoring run (receipt-skill-ordering.json) used the same command after
inserting a decoy table + prefixed draft heading before the real SKILL section.

## What was built (fixture/)

- `registry/request-field-outcomes-r28.json` — 12 rows: 2 genuine (F28-01/02)
  with correct citations, 10 citation-misuse cheats (F28-10 .. F28-19) built from
  copied shapes of the two known-true pilot outcomes.
- SKILL section `## Round-28 request-field outcomes` with the frozen 6-column
  header and one row per registry id (fixture/SKILL-section.md).
- SOURCES rows S940–S950 appended to corpus/SOURCES.md (fixture/SOURCES-rows.md);
  base/working-tree max was S139, so all are new.

The scratch tree server-schema.cpp snapshot matched the pin
(`1f9d7b73…0050`). Genuine declaring lines: `n_cache_reuse` L67, `xtc_threshold`
L108. I did **not** run llama-server myself; the frozen counter launched the
pinned b11755 on 127.0.0.1:47600-47619 and answered every live row itself. After
both runs `ss -ltnp` showed no 476xx listener; scratch tree 251M, /fast 76% used.

## Each trick and whether it counted (from receipt.json `why`)

| id | trick | counted? | clause(s) that refused it |
|---|---|---|---|
| F28-01 | genuine n_cache_reuse, correct citation | **counted** | — |
| F28-02 | genuine xtc_threshold, correct citation | **counted** | — |
| F28-10 | cite the field's `->set_desc` line instead of declaration (top_k L91) | refused | `b:line-does-not-declare-field` (+ `d:not-shown`) |
| F28-11 | cite the field's `->set_limits` (hard-limits-style) line (min_p L98) | refused | `b:line-does-not-declare-field` (+ `d:not-shown`) |
| F28-12 | cite a line declaring a *different* field (top_p row → L89 declares top_k) | refused | `b:line-does-not-declare-field` (+ `d:not-shown`) |
| F28-13 | off-by-one line (top_n_sigma row → L100, blank line above L101) | refused | `b:line-does-not-declare-field` (+ `d:not-shown`) |
| F28-14 | SOURCES row names `L440`, so the needed `L44` appears only as a substring (n_predict, real decl L44) | refused | `c:no-new-sources-row` (+ `d:not-shown`) |
| F28-15 | SOURCES row names the **wrong commit** `1234abc` (n_keep, real decl L54) | refused | `c:no-new-sources-row` (+ `d:not-shown`) |
| F28-16 | cite a file **other than** server-schema.cpp (server-task.cpp, n_discard) | refused | `b:not-schema-file` + `c:no-new-sources-row` |
| F28-17 | SKILL cells hold the needed text **inside longer junk** (n_indent) | refused | `d:not-shown` **only — clause (a) matched the junk-wrapped cells** |
| F28-18 | one S### (S950) cited by **many rows** + duplicate field/line | refused | `b:duplicate-line-or-field` **only (its live outcome was genuinely true)** |
| F28-19 | second row on the same field/line/S### (repeat_last_n) | refused | `b:duplicate-line-or-field` (+ `d:not-shown`) |

Separate run (receipt-skill-ordering.json): **a second SKILL table before the
real one** and a **heading-prefix** draft (`## Round-28 request-field outcomes
(draft — ignore this one)`) with a 5-column header poisoned the counter's single
global `header_ok`, so the real table's rows were never collected and **counted
dropped to 0** (every row `a:no-skill-row`). That trick only destroys the count;
it cannot inflate it.

## Findings worth flagging to the counter owner

1. **Clause (a) SKILL match is substring/word-boundary, not cell-equality.** The
   `field`, `value`, `outcome` and `source` cells are matched with `in` / `\bS###\b`,
   so wrapping each in arbitrary junk text (F28-17) still passes (a). Only the id
   cell is exact. A row with junk-wrapped cells is stopped here **solely** by the
   live-outcome clause (d) — the citation layer does not catch it.
2. **The citation clauses refuse rows even when the live outcome is TRUE.**
   F28-16 (n_discard) and F28-18 (repeat_last_n) produced genuine 400-reject
   outcomes that clause (d) accepted, yet they were refused purely by
   `b:not-schema-file`/`c` and `b:duplicate-line-or-field`. This is the clean
   demonstration the source-misuse control is meant to produce: misused citation
   alone voids a row regardless of whether its outcome is real.
3. Nothing in this control reaches `counted >= 18`; the predicate holds against
   every listed citation trick. No counter redesign is forced by this seat.

## Receipts

- `receipt.json` — main run (registered 12, counted 2, exit 0).
- `receipt-skill-ordering.json` — decoy-table/heading-prefix run (counted 0, exit 0).

## Tooling

No tools installed or updated; the host already had the pinned python3.14, git,
llama-server b11755 and model. (Operator 2026-10-19 directive read; nothing to record.)
