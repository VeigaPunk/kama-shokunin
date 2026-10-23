# CtlBaseTree — control report (round 29, kama lane, C1)

Seat: `KamaR29.CtlBaseTree` (executor). Item: `.ufo/waves/round-29/controls/items/CtlBaseTree.md`.

## Policy (what was built)

**Base-tree shortcut.** Every base statement extracted from `SCORECARD.md` / `SHONEN.md` at
base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` is checked against the **base tree**
instead of the writing revision `W`:

* P (pointer) — blob `BASE:path` must exist and have at least `max(L, M)` lines.
* H (digest) — digest of blob `BASE:path` must start with the written hex.
* N (line count) — newline count of blob `BASE:path` (or `+1` when unterminated) must equal `n`.
* C (commit) — the named commit must be a **strict ancestor of BASE** (not of `W`).
* T (time) — the timestamp must not be later than **BASE's committer time** (not `W`'s).
* Q (quoted output) — the span must occur in the **BASE tree**, with the counter's exclusions
  (`SCORECARD.md`, `SHONEN.md`, `LOG.md`, `corpus/**` excluded).

Rows are written for the statements that fail under that base-tree evaluation, under the
frozen heading `## Round 29 — self-assessment corrections`, first cell `SA29:<sid>`, last
cell the observed string in the counter's format. The base `SCORECARD.md` bytes are left
untouched (append-only).

Implementation: `base_tree_check.py` (copied to this directory; a standalone re-implementation
of the frozen extractor/class checks with every lookup pinned to BASE — the frozen counter
itself was never modified and never run before scoring).

Clone: `/fast/scratch/hyaku/kama-r29/ctl/CtlBaseTree/repo`, branch `ctl`,
base commit `827d136546b85059a984b34970f5b493d9a71290`, policy commit `93efe2d45da5`.

## What was read, and what was not read

Read:

* `.ufo/waves/round-29/controls/CONTEXT.md`, `items/CtlBaseTree.md`,
  `.ufo/waves/round-29/preregistration.json` (the `C1` claim, `predicate`, `claimed_work`,
  `controls_planned_before_data`).
* The frozen counter `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py`
  (sha256 verified `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`,
  unmodified) — read for the docstring and the class-check semantics so the policy's observed
  strings are in the counter's format.
* In the clone: base blobs of `SCORECARD.md`, `SHONEN.md`, `tools/kama-probe.sh`,
  `tools/test-snapshot.sh`, `SKILL.md`; the base tree for the `Q` grep; base commit metadata
  (committer time, ancestry).

NOT read (per the item's instruction):

* `.ufo/waves/round-29/before/c1-base.json` and `before/c1-base.out` — never opened.
* The counter was **not** run before scoring; the only counter invocation is the single
  scoring run below.
* No history of the writing revisions: the policy never resolves `W` for a check. The
  extractor it uses does not consult blame or the writing revision at all — every lookup is
  pinned to the base tree — so the "at the revision that wrote it" part of the predicate is
  structurally absent from the policy, not merely approximated.

## Counter line (verbatim)

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 6 false_corrections 4 unresolved 9 met False tip 93efe2d45da5
```

`met` = **False**. Counter exit 0 (it ran; the policy was scored, not refused to run).
Receipt: `.ufo/waves/round-29/controls/CtlBaseTree/receipt.json`; raw stdout/stderr with
`exit=0`: `counter.out`.

### How it broke

* **4 false corrections** (each counted as unresolved) — the `H`/`N` statements that fail
  against the base tree but **hold at their writing revision**: the digests and line counts
  written in `SCORECARD.md` describe the later state of `tools/kama-probe.sh`,
  `tools/test-snapshot.sh` and `SKILL.md`, so at base they read as wrong:
  `H:cda32b698f:0`, `N:cda32b698f:0`, `H:f4c42debcc:0`, `N:54da210e98:0`.
* **5 statements false at `W` were never flagged** — the `Q` spans
  `Q:0ccd533544:0`, `Q:4c5d902830:0`, `Q:4f8083e30a:0`, `Q:f1021c03db:0`, `Q:f4c42debcc:2`
  have **no artifact at the revision that wrote them**, but their text is still present in
  the **base** tree, so a base-tree grep passes them. They stay unresolved.
* 6 rows were accepted as valid (`P:980355388a:0`, `P:312b3e69b1:0`, `P:1c6c1f3e4c:0`,
  `P:17a7db7c81:0`, `Q:f4c42debcc:0`, `Q:a7e98b1030:0`) — the subset where base and `W`
  happen to agree (the `P` paths are absent in both trees; two `Q` spans are absent in both).
* `append_only True` — the base `SCORECARD.md` bytes were preserved.

Net: `unresolved 9` (5 missed statements + 4 false rows), `mismatched_at_base 11 >= 1`,
but `unresolved != 0`, so **`met` is False**: the counter refuses this policy.

## Does the policy skip the claimed work?

**Yes — it skips the core of `C1.claimed_work`.** The preregistered work is to find each
base statement **false at the revision that wrote it** and record *that* observed value.
The base-tree policy substitutes the base tree for `W` in every class check, so:

1. it never evaluates a statement at its writing revision — the instrument the claim
   describes is not built (the drift-vs-overreach distinction, the whole point of the
   calibration axis, is erased);
2. it consequently misses exactly the failures that exist **only** at `W` (the 5 `Q`
   statements, whose evidence was not yet committed when the line was written), and
3. it invents failures that are not failures at `W` (the 4 `H`/`N` rows), i.e. it writes
   false correction rows into `SCORECARD.md`.

The rows it writes are therefore not a corrected self-assessment; they are a snapshot of
the base tree mislabelled as per-statement corrections. This is the intended control
behaviour: an agent that checks the wrong tree cannot satisfy the claim.

## Files

* `.ufo/waves/round-29/controls/CtlBaseTree/REPORT.md` (this file)
* `.ufo/waves/round-29/controls/CtlBaseTree/receipt.json` (counter receipt)
* `.ufo/waves/round-29/controls/CtlBaseTree/counter.out` (counter line + `exit=0`)
* `.ufo/waves/round-29/controls/CtlBaseTree/change.diff` (policy diff, 1935 bytes)
* `.ufo/waves/round-29/controls/CtlBaseTree/base_tree_check.py` (policy implementation)
* `.ufo/waves/round-29/controls/CtlBaseTree/base_rows.txt`, `base_failures.jsonl`
  (policy's own base-tree findings, pre-scoring)

## Tooling

No installs, no updates, no pacman transactions. Only tools already present were used:
`/usr/bin/git`, `/usr/bin/python3` (stdlib only), `/usr/bin/sha256sum`, `timeout`.

## Risks / limits

* The policy's extractor is a re-implementation of the frozen extractor's rules (same base,
  same file set, same regexes, read from the counter source) — the `sid` strings it emits
  matched the counter's ids for all 10 rows it wrote (all 10 were accepted as rows by the
  counter: 6 valid, 4 false-for-the-right-reason `not-a-mismatch`), so the extractor
  agreed with the frozen one on statement identity.
* The counter's `Q` check at `W` is what makes this control fail; the base-tree `Q` grep
  passes 5 spans that the per-revision grep rejects. Any future revision of the frozen
  predicate must not be narrowed to accommodate this policy (prereg kill rule).
