# KamaR27CtlContentFree — content-free SKILL rows control (round 27, pre-freeze)

Seat: `KamaR27CtlContentFree` (critic, content-free control class).
Lane commit scored: `530eaa998735d226ec90cea9b0cf4242a6b9cb01`
(base `a720399e627b23026143646cb8de470b266346b5`).
Sandbox: `/fast/scratch/hyaku/kama-r27/KamaR27CtlContentFree`
(clean `git clone` of the lane, checked out at 530eaa9; all edits are sandbox-only).
Counter: `.ufo/waves/round-27/count-c1.py`, run **unmodified**,
`sha256 = 382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6`
(the hash is in every receipt and in `cited-source-lines.txt`).

## Control shape

One registry (`control-registry.json`, copied byte-for-byte from
`.ufo/waves/round-27/pilot/pilot-registry.json`): the **two genuine pilot faults**

| id | signature | request | source |
|---|---|---|---|
| E27-90 | `'messages' is required` | `POST /v1/chat/completions {"model":"x"}` | server-common.cpp:1386 (704366d) |
| E27-91 | `"prompt" must not be empty` | `POST /completion {"prompt":[]}` | server-common.cpp:1129 (704366d) |

plus the two `corpus/SOURCES.md` rows `S990`/`S991` naming file, line and
`704366d` (neither exists at base). Only **SKILL.md prose** changes between
variants; the registry, the requests, the controls and the sources are identical
in every variant. Every recorded row was live: the counter's own run returned
`status 400` for the request and `control_status 200` for the control, with the
signature in the JSON error message (see `receipt-V*.json` → `rows[].live`).

Because the substrate has exactly **two** distinct genuine faults and clause (h)
is one-fault-one-row, **2 is the arithmetic ceiling** of every prose variant; the
prose layer contributes nothing to the count in either direction. The variants
below therefore measure *what the counter demands of the prose*, not the
registry.

## What was tried (21 counter runs, 20 prose variants + 1 padding arm)

Each variant is a separate SKILL.md state, scored by a separate run of the frozen
counter under `flock /fast/scratch/hyaku/kama-r27/counter.lock timeout 900`.
Column order in the tables below is the semantic order
`id | signature | trigger | meaning | next action | source`; the counter reads
cells positionally and only inspects `cells[-2]` (see W2).

| variant | prose shape | registered | counted | verdict per row (`why`) |
|---|---|---|---|---|
| V1-pilot-prose-5col | pilot prose verbatim, **5 columns, no meaning column** | 2 | **2** | both `[]` |
| V2-boilerplate-6col | trigger = bare path, meaning = "the request was rejected", next action = one stock template with ONE word varied | 2 | **2** | both `[]` |
| V3-lorem-ipsum | trigger/meaning/next action all lorem ipsum; path in its own column | 2 | **2** | both `[]` |
| V4-copied-meaning-cell | E27-91 meaning cell copied VERBATIM from E27-90 | 2 | **2** | both `[]` |
| V5-copied-next-action | next action copied VERBATIM from the other row | 2 | 1 | E27-91 `h:same-next-action` |
| V6-next-action-case-folded | next action equal up to case + whitespace | 2 | 1 | E27-91 `h:same-next-action` |
| V7-next-action-one-word | next action differs by exactly one word | 2 | **2** | both `[]` |
| V8-junk-trigger-path-column | trigger = `x`, meaning = `y`, path in its own column | 2 | **2** | both `[]` |
| V9-signature-in-wrong-column | signature column = "see below"; signature text parked in the trigger cell | 2 | **2** | both `[]` |
| V10-next-action-six-words | next action exactly 6 words, trigger/meaning single chars | 2 | **2** | both `[]` |
| V11-next-action-five-words | next action 5 words | 2 | 0 | both `a:no-skill-row` |
| V12-noisy-next-action | next action `aaaa bbbb cccc dddd eeee ffff`, all prose noise | 2 | **2** | both `[]` |
| V13-next-action-punctuation-only | next action differs by ONE trailing period | 2 | **2** | both `[]` |
| V14-path-only-in-meaning-cell | trigger holds no path; path only inside the meaning cell | 2 | **2** | both `[]` |
| V15-extra-junk-columns | 9 columns, most junk | 2 | **2** | both `[]` |
| V16-signature-cell-junk | signature cell = signature plus trailing note | 2 | **2** | both `[]` |
| V17-positional-next-action | real next action = 3 words; a junk 6-word cell sits second-to-last | 2 | **2** | both `[]` |
| V18-copied-trigger-wrong-endpoint | E27-91 trigger copied verbatim from E27-90 (names the WRONG endpoint) | 2 | **2** | both `[]` |
| V19-four-cells | only 4 non-empty cells | 2 | 0 | both `a:no-skill-row` |
| V20-stopword-next-action | next action `the the the the the the` | 2 | **2** | both `[]` |
| **V21-padded-15-rows** | **15 boilerplate rows over the same 2 faults** (padding arm) | **15** | **2** | E27-12…E27-24 all `h:same-source-line` |

Raw data: `variant-results.json`, `variant-results-summary.txt`,
`counter-<variant>.txt` (stdout + exit code), `receipt-<variant>.json`,
`patch-SKILL-<variant>.patch`, `skill-section-<variant>.md`,
`patch-SOURCES.patch`, `control-registry.json`,
`registry-V21-padded-15-rows.json`.

## Best score

- Best registered/counted with the assigned substrate (the two pilot faults):
  **2 / 2** — reached by 16 of the 20 prose variants: the pilot-prose control
  V1 plus 15 content-free shapes (V2, V3, V4, V7, V8, V9, V10, V12, V13, V14,
  V15, V16, V17, V18, V20). Only four variants score below 2, and each is a
  structural floor (`V5`/`V6` identical next action, `V11` five words, `V19`
  four cells).
- Padding arm: registered **15**, counted **2**; the 13 duplicate rows fail
  `h:same-source-line`.
- **Meets target (counted >= 15): NO.** With only two genuine faults the ceiling
  is 2 by clause (h); the counter does not refuse a single row for its prose.

## What the counter does NOT check (the boundary, stated plainly)

Clause (a), read from the frozen code, demands exactly seven things of a SKILL
row, and all of them are structural:

1. the line starts with `| <id> |` (`^E27-\d{2}$`);
2. the registry signature string occurs **somewhere** in the line;
3. the registry `S###` token occurs **somewhere** in the line;
4. at least 5 cells, none empty;
5. the registry request path occurs **somewhere**, in **any** cell;
6. `cells[-2]` — whatever column that position happens to be — splits into
   **>= 6 whitespace tokens**;
7. (clause h, cross-row only) the `cells[-2]` string, folded for case and
   whitespace, differs from every **earlier counted** row's `cells[-2]`.

Nothing else about the prose is inspected. In particular the counter does **not**
check that:

- the **trigger** cell describes how to reproduce the error — a bare path (V2),
  `x` (V8, V10, V20), lorem ipsum (V3), noise (V12) or another row's trigger
  naming the wrong endpoint (V18) all count;
- the **meaning** cell explains the signature — it may be absent entirely (V1's
  5-column layout), generic (V2), lorem ipsum (V3), copied verbatim from another
  row (V4), or junk `y` (V8/V10/V20);
- the **next action** cell is actionable for *this* error — the same stock
  sentence with one word changed (V2), six stopwords (V20), six characters of
  noise (V12) and a 3-word "retry once fixed" (V17) all count;
- the prose refers to the cited **file, line, commit or signature** at all;
- the table even **has** a meaning column (the pilot's own 5-column row counts);
- the **column semantics** hold — the signature may live in the trigger column
  while the signature column says "see below" (V9), and the request path may live
  in the meaning cell (V14) or in a dedicated column (V3/V8);
- next actions are distinct **in meaning** — case+whitespace folding only, so one
  extra word (V7) or one trailing period (V13) defeats the uniqueness test.

The counter's only quantitative prose floor is: 5 non-empty cells and 6
whitespace tokens in `cells[-2]` (V11 with 5 words and V19 with 4 cells are the
two refusals).

## Counterexample (strongest)

A SKILL.md table whose every prose cell is boilerplate:

```
| id | signature | trigger | meaning | next action | source |
|---|---|---|---|---|---|
| E27-90 | `'messages' is required` | /v1/chat/completions | the request was rejected | Fix the request and then retry the call | S990 |
| E27-91 | `"prompt" must not be empty` | /completion | the request was rejected | Fix the request body and then retry the call | S991 |
```

counts **2/2** (`receipt-V2-boilerplate-6col.json`). Identical result when the
prose is `aaaa bbbb cccc` noise (V12), six stopwords (V20), lorem ipsum (V3), or
when the trigger names the *wrong* endpoint because it was copied from the other
row (V18). The counter distinguishes only the five/six-word floors and exact
(case/whitespace-folded) next-action equality.

## Impacted axes

- **C1 depth** (a lowest axis, currently 7). The counted property the counter
  enforces is "one live, sourced, non-echoed fault with a structurally present
  path cell and a 6-word second-to-last cell". The per-row *explanation* — the
  "trigger, meaning, next action" prose the claim names as its surface — is not
  measured. A data seat that finds 15 genuine faults can therefore fill the prose
  with a stock sentence per row and score 15/15 without ever writing a
  reproduction, a meaning, or a per-fault next action. That is a *fixable defect*
  in what the claim asserts, not a tradeoff the Rust judge must accept, because
  nothing in the predicate depends on the prose's content.

## Smallest safe correction (not applied — critic seat does not repair)

Either (i) narrow the C1 surface: state that the columns are for the human
reader and the counted property is "one live, sourced, non-echoed signature per
row, request path present in the row, >= 6-word next action"; or (ii) if prose
quality is meant to be measured, bind clause (a) to named columns instead of
`cells[-2]` — require the header row to name them and check `cells[2]` contains
the request method **and** path (V18/V8/V14 close), require the meaning column to
exist (V1 closes), and fold punctuation as well as case/whitespace in (h)
(V7/V13 close). The five/six-word and five-cell floors are already the only
quantitative demands and should be stated as such.

## Counterpart the counter gets right (for calibration)

- (h) one-fault-one-row blocks padding: 15 boilerplate rows over 2 faults score
  2 (`receipt-V21-padded-15-rows.json`).
- (h) refuses verbatim and case/whitespace-equal next-action copies (V5, V6).
- Genuineness is not attackable through the prose at all: clauses (b), (d), (e),
  (f), (g) still require a snapshot-pinned literal, a live >= 400 message
  containing the signature, a 2xx control, and non-echoed text.

## Reproduction

```
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r27/KamaR27CtlContentFree
cd /fast/scratch/hyaku/kama-r27/KamaR27CtlContentFree && git checkout -q 530eaa998735d226ec90cea9b0cf4242a6b9cb01
sha256sum .ufo/waves/round-27/count-c1.py     # 382c511f…4c6
python3 ctlgen.py                             # 20 prose variants (V1..V20)
python3 run21.py                              # padded-15-rows arm
```

Ports: the frozen counter starts its own `llama-server` on 47600–47619 and stops
it (the counter raises `could-not-evaluate` if a port does not close). No server
was started by this seat directly; no process was left behind by these runs.
No tools were installed or updated for this seat.
