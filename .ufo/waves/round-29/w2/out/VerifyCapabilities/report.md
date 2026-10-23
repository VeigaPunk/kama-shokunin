# VerifyCapabilities — no capability pre-claim

**Verdict:** confirmed. `git diff 2aa46e24 -- SCORECARD.md` does not touch any capabilities table. The working-tree capabilities tables contain no round-29 entry. No capability row was appended.

**Confidence:** high. Direct diff, prefix byte-compare, and row extraction. No tools installed.

## What was compared

- Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`
- Base: `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`, blob `2aa46e24:SCORECARD.md` = `24882de8068025f3bfc559ed04a5a360a16dba25`, **1441 lines**
- HEAD: `513eba3ba51a142c9936553e3a85918345eb5c4c` (`SCORECARD.md` **1464 lines**)
- Working tree: `SCORECARD.md` **1504 lines**, status ` M SCORECARD.md` (not staged)

## Diff does not touch the tables

`git diff --numstat 2aa46e24 -- SCORECARD.md`:

```
63	0	SCORECARD.md
```

63 insertions, 0 deletions. Sole hunk (`git diff -U0`):

```
@@ -1441,0 +1442,63 @@ same schema) and the json_schema → grammar transform, with the A1 rule kept.
```

Pure insert after the last line of the base file. Lines 1–1441 of the base blob and the working tree are identical (`diff -q` exit 0). Every capabilities table is inside that prefix.

Split of the same 63 lines:

| Comparison | Hunk | What it adds |
|---|---|---|
| `2aa46e24` → HEAD `513eba3` | `@@ -1441,0 +1442,23 @@` | `## Round 29 — self-assessment corrections` and its 11-row correction table |
| HEAD → working tree | `@@ -1464,0 +1465,40 @@` | `## Round 29 — self-assessment evidence at writing…`, the C1 calibration claim table, and `### Planned (round 30)` |

Neither hunk reaches a capabilities table. The last table ends at line 1302.

## Capabilities tables (working tree = base = HEAD)

Headers (`git grep` at `2aa46e24` and at `HEAD`, and a working-tree grep) are the same five lines. Data rows and `First-working round`:

| Span | Header line | Row | First-working |
|---|---|---|---|
| 122–128 `## Capabilities` (superseded; L128: rows enter only through a demonstrating round) | 124 | `sources-registry` | 10 |
| 457–460 round-14 measured results | 457 | `ollama-offline-evidence-replay` | 14 |
| 621–628 canonical list as of round 16 | 624 | `sources-registry` | 10 |
| | | `ollama-offline-evidence-replay` | 14 |
| | | `live-llamacpp-lifecycle` | 16 |
| 909–913 `### capabilities: append — first working round 20` | 911 | `gguf-declared-identity-replay` | 20 |
| 1298–1302 `### capabilities: append — first working round 25` | 1300 | `context-capacity-receipt` | 25 |

Each span was `diff -q`'d against `2aa46e24:SCORECARD.md` and reported identical. No row's last cell is `29`. None of those spans contains `round-29`, `round 29`, or `Round 29`.

## Round-29 text is not a capability row

The only added text (working-tree lines 1442–1504) has two tables, neither with a capabilities header (`| Capability |`, `| Name | What it can do |`, or `First-working`):

- correction table: `| id | line at base | class | statement token | W | cause | observed |`
- axis-claim table: `| Claim | Axis, score | Before → after | Counting command | Measured commit | Evidence |` — one row, `C1 (measured)`, calibration 7 → 7

The appended claim section ends with the non-claim sentence (working tree line 1498):

```
coverage 9, depth 7, adjacency 7. Capabilities: none claimed.
```

That sentence is outside every capabilities table. Same formula already appears at the close of rounds 27 and 28 (lines 1395 and 1435), which are inside the unchanged prefix.

## Not found

No round-29 capability name, no `First-working round` of 29, no edit to an existing capabilities table, in the committed tip or the dirty working tree.
