# Round-27 C1 pre-freeze control — KamaR27CtlDoNothing

Seat: do-nothing control (attack the counter, never repair it).
Lane commit: `530eaa998735d226ec90cea9b0cf4242a6b9cb01` (freeze), base `a720399e627b23026143646cb8de470b266346b5`.
Counter run unmodified from the sandbox; `sha256sum .ufo/waves/round-27/count-c1.py` =
`382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6` (matches `preregistration.json` C1.counter_sha256).
Sandbox: `/fast/scratch/hyaku/kama-r27/KamaR27CtlDoNothing` (clone, checked out at freeze; lane repo untouched).
Every run: `flock /fast/scratch/hyaku/kama-r27/counter.lock timeout 900 python3 .ufo/waves/round-27/count-c1.py --lane . --repo . --out <receipt>`.
No tool installed or updated during this seat.

## Control shape

"Do nothing": add no genuine, live, sourced, non-echoed request-validation signature. Four prescribed
variants score the counter against a tree that has no new knowledge, then two amplification probes
attack the dedup/provenance gates.

## Scores (frozen counter bytes)

| # | variant | registered | counted | meets target 15 | per-row why |
|---|---|---|---|---|---|
| v1 | freeze tree as is, no `registry/error-signatures-r27.json` | 0 | 0 | no | (no rows) |
| v2 | empty registry `{"signatures":[]}` | 0 | 0 | no | (no rows) |
| v3 | pilot registry rows E27-90/E27-91, no SKILL section, no SOURCES rows | 2 | 0 | no | both `a:no-skill-row`, `c:no-new-sources-row` |
| v4 | pilot rows + SKILL rows, SOURCES rows reused from base (S130/S135) | 2 | 0 | no | both `c:no-new-sources-row` (id exists at base; live check still shows status 400 with the exact message) |
| v5 (extra) | one genuine fault duplicated 15x: 15 SKILL rows, 15 registry rows, one new SOURCES row S136 | 15 | 1 | no | E27-01 counts; E27-02..15 `h:same-source-line` |
| v6 (extra) | two genuine pilot faults sharing ONE new SOURCES row S136 | 2 | 2 | no | none — both counted |

Best do-nothing score: **v1/v2/v3/v4 counted 0**; best amplification of a do-nothing shape is **v5 counted 1**
(and that one row still needs a real fault, a real 704366d literal and a live 400). No variant meets target.

Receipts: `v1-base/`, `v2-empty/`, `v3-pilot-only/`, `v4-pilot-baseids/`, `v5-duplicate-amplification/`,
`v6-shared-source-row/` (each has `stdout.txt`, `exit-code.txt`, `receipt.json`, `registry.json` where a
registry existed, and `skill-sources.diff`; v1/v3 diffs are empty-by-design notes). All six runs exited 0.
The reconstructed registry files are byte-identical to the scored ones (v3 `f1104157…`, v4 `05908d4b…`,
v5 `59b7b408…`, v6 `31958a4d…` sha256 verified by rebuilding from `pilot/pilot-registry.json` with the same
transform after the fact; see REPORT notes in each dir's stdout + receipt pairing).

## What the counter blocked, and how

- v3/v4 show clauses (a) and (c) are the only gates that stop copied pilot rows: the live check still
  launches the server and gets `status 400` with `'messages' is required` / `"prompt" must not be empty`
  (see v3/v4 receipts `live`), so the rows die purely on static provenance. Correct behaviour.
- v5 shows clause (h) caps amplification of one fault at one counted row (`h:same-source-line`); a
  do-nothing seat cannot reach 15 by repeating genuine text, ids, SKILL rows or next-action cells.
- v4 also shows clause (c) reads the base SOURCES from git (`git show BASE:corpus/SOURCES.md`), so
  rewriting the measured tree's SOURCES content cannot launder a reused id.

## Counter weaknesses found

### 1. Clause (b): a base occurrence that is line-wrapped is invisible to the novelty check

Predicate (b) says the signature "does not occur (case-insensitive) in SKILL.md, corpus/knowledge/ or
registry/ at base". The counter implements this with `git grep -F -i -q -e <sig>` — a per-line, byte-exact
fixed-string search with no whitespace folding (unlike clause (f), which explicitly folds whitespace).

Concrete local evidence (`clause-b-linewrap-gap.txt`): the 36-byte fragment
`exceeds the available context size (` is documented at base **SKILL.md:1122-1123**, wrapped across the
two lines:

```
(`This server does not support metrics endpoint...`, `exceeds the available
context size (`, `couldn't bind HTTP server socket`, `error: invalid argument: `);
```

`git grep -F -i -q -e 'exceeds the available context size (' a720399 -- SKILL.md corpus/knowledge registry`
exits 1 → the counter treats the signature as new. The same fragment is a substring of a real literal at
`.ufo/waves/round-27/sources/llama.cpp-704366d/server-context.cpp:3678`
(`"request (%d tokens) exceeds the available context size (%d "`), on a line whose 4-line window holds
`send_error(`/`ERROR_TYPE_EXCEED_CONTEXT_SIZE`, so it passes (d) by construction. The base SKILL text itself
says the lane already held this message in earlier wave evidence, so a live trigger exists in the round-26
evidence (that reachability is [INFERENCE]; the literal, line and error token are observed).
Impact: a signature already documented in SKILL.md can be registered as "new" and, with a copied live
trigger, counted. This is a false-provenance hole in the one gate whose job is novelty against the base corpus.

Smallest safe correction (for the counter owner, not applied here): make `present_at_base` fold whitespace
and newlines the way `squash()` does, e.g. test the squashed signature against squashed base text for
SKILL.md/corpus/knowledge/registry (and keep the case fold). That is one clause, no new axis.

### 2. Clause (c): one new SOURCES row can cover many registry rows

Predicate prose says "each with trigger, meaning, next action and a new S### source row", but clause (c)
only checks, per row, that *its* S### id exists in the measured SOURCES.md, is absent at base, and that the
row text contains the entry's file name, its line marker and `704366d`. Nothing binds one S### row to one
registry row. Demonstrated by v6: rows E27-90 (`server-common.cpp` line 1386) and E27-91 (same file, line
1129) both cite **S136**, a single new row whose text names both lines → counter prints
`registered 2 counted 2` (see `v6-shared-source-row/receipt.json`).
This does not bypass the live/fault work (each row still needs a distinct real fault, line and message), so
it is a provenance granularity gap, not a shortcut to 15. Correction if the lane wants per-fault sourcing:
require each counted row's S### row to be used by exactly one counted row (or to carry exactly one
`file`+`line` pair), which is a clause-(c) tightening, no axis change.

## Verdicts

- v1 base/no registry: meets target **no** (0/15).
- v2 empty registry: meets target **no** (0/15).
- v3 pilot rows only: meets target **no** (0/15).
- v4 pilot rows + base-id SOURCES rows: meets target **no** (0/15).
- Adversarial best (v5): **1/15**, not target; (v6): 2/15 but only because two genuine pilot faults were
  scored with one shared source row — a (c) granularity finding, not a do-nothing path.

No llama-server was left running (ports 47600-47619 free; the counter's own children are killed);
all runs were lock-serialized and `timeout`-capped.
