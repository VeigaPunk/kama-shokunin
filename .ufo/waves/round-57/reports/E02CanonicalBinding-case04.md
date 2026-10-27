# E02CanonicalBinding — distinct case 4: independent retest of the assigned case

Separate evidence file for distinct case 4 (the seat report is
`.ufo/waves/round-57/w1/out/E02CanonicalBinding.md`). Everything below was run separately
from the seat report's battery, with its own commands and its own receipts, and each step
names the route it uses. Nothing in the lane was edited.

Assigned case: *an operability-side check whose input is the actual canonical capability
rows, and a no-op omission control.* The case is tested on three points:

1. the rows the check reads are the **table's** rows (an independent route derives the same set);
2. a **no-op** that reads nothing is **rejected**, while the genuine row set is **accepted**;
3. each binding leg fails **on its own** mutant, so no leg is carried by another's failure.

Tip used: `b89bdab2cc114735ec5d331c6c610134258f7864` (the frozen round-57 base). Repo:
`/home/vgpnk/Projects/shokunin/kama-shokunin`. Scratch:
`/fast/scratch/hyaku/kama-r57/E02CanonicalBinding/`.

## Point 1 — independent derivation of the canonical row set (route B, no prototype import)

`independent-derive.py` (sha256 `7e7a7c2e2d7fe9494cd823aebed03488612a3620db16c52e46615355e4d54159`)
reads `SCORECARD.md` at the tip through `git cat-file` and derives the table by a route the
prototype does not use (fixed heading anchor + contiguous pipe block, then the §Saturation
prose sentence as a second, independent count):

```
$ python3 independent-derive.py <lane> b89bdab2
round49_headings=1 at_line=[2843]
heading=**Capabilities — canonical list as of round 49**
routeA_pipe_lines=13 routeA_rows=11
routeA_names=sources-registry,ollama-offline-evidence-replay,live-llamacpp-lifecycle,gguf-declared-identity-replay,context-capacity-receipt,instrument-agreement,pin-watch,digest-ledger,hexrun-census,append-only-audit,live-receipt-replay
routeA_firsts=10,14,16,20,25,30,41,42,43,46,47
routeB_prose_firsts=10,14,16,20,25,30,41,42,43,46,47
agree_names_n=11 agree_firsts=True
retired_line_axes=6 axes
retired_line_caps=11 capabilities
exit=0
```

Receipt: `receipts/independent-derive.out`. The prototype's own audit reports exactly that
row set at the same tip (`canon_round=49 canon_rows=11`, 11 `row=` lines, names identical),
so the input is the committed table and not a literal in the tool.

Corroboration that this is not tip-fragile: the same table hashes
`canon_sha256=e27664aa8213cbe977cc83b6971e841686c4aff5ed23caae415d32f79c1a1b19` with
`canon_rows=11` at `b89bdab2`, `3d2d5d4d` and `8a7f1976`
(`receipts/genuine-base.out`, `receipts/genuine-3d2d5d4d.out`, `receipts/genuine-8a7f1976.out`).

## Point 2 — the no-op is rejected, the genuine set is accepted

Baseline reproduced from the committed frozen control (read at `7c873d7b`, not from the
worktree, which no longer carries it):

```
$ python3 frozen/c1-noop.py
mismatches=0 maxN=46 met=True
exit=0
```

Rejection by the prototype's verifier:

```
$ python3 canon-binding.py verify --repo <lane> --tip b89bdab2 --scratch <dir> \
      --instrument-out frozen/noop-c2.out
tip=b89bdab2cc114735ec5d331c6c610134258f7864
instrument=frozen/noop-c2.out
claims_met=True tree_met=True claimed_rows=0 derived_rows=11 mismatches=6 rejected=1 accepted=0
detail: canon_sha256 claim None != derived e27664aa8213cbe977cc83b6971e841686c4aff5ed23caae415d32f79c1a1b19
detail: canon_rows claim None != derived 11
detail: row lines: missing=['append-only-audit', 'context-capacity-receipt', 'digest-ledger', 'gguf-declared-identity-replay', 'hexrun-census', 'instrument-agreement', 'live-llamacpp-lifecycle', 'live-receipt-replay', 'ollama-offline-evidence-replay', 'pin-watch', 'sources-registry'] extra=[] differ=[]
detail: rows_bound claim None != derived 11
detail: evidence claim None != derived (20, 20)
detail: exec claim None != derived (10, 10)
exit=1                                          <- rejected
```

Acceptance of the genuine instrument output (same tip):

```
$ python3 canon-binding.py verify --repo <lane> --tip b89bdab2 --scratch <dir> \
      --instrument-out receipts/genuine-base.out
tip=b89bdab2cc114735ec5d331c6c610134258f7864
instrument=receipts/genuine-base.out
claims_met=True tree_met=True claimed_rows=11 derived_rows=11 mismatches=0 rejected=0 accepted=1
exit=0                                          <- accepted
```

A no-op that keeps a full-shaped summary but drops every per-row line is also rejected
(`receipts/verify-forged-omit.out`: `row lines: missing=[11 names]`), and a summary whose only
defect is one digest nibble is rejected (`receipts/verify-forged-sha.out`).

## Point 3 — each leg fails on its own mutant

| Leg | Mutant (scratch tree, hardlinked from `git archive b89bdab2`) | Failing counter | Result |
|---|---|---|---|
| `canon` | `no-heading` — every canonical table stripped from SCORECARD | `canon=1` (and `evidence=1 exec=1` from the vacuity guard: 0 rows may not pass) | `mismatches=3 met=False` exit 1 |
| `evidence` | `mut-delete` — `corpus/knowledge/engine-pin-watch.md` removed | `evidence=1` only | `rows_bound=10/11 evidence=19/20 … met=False` exit 1 |
| `content` | `mut-empty` — same file emptied, path still resolves | `content=1` only | `content=19/20 … exec=10/10 met=False` exit 1 |
| `exec` | `mut-exec` — `tools/pin-watch.py` replaced by an exit-1 stub | `exec=1` only | `exec=9/10 … met=False` exit 1 |
| `exec` | `mut-silent` — `tools/digest-ledger.py` exits 0 printing nothing | `exec=1` only | `exec=9/10 … met=False` exit 1 |
| input is the table | `mut-extra-row` — one row appended (its evidence resolves) | none | `canon_rows=12 rows_bound=12/12 exec=11/11 met=True` exit 0 |
| input is the table | `mut-rename` — one row renamed | none | `row=hexrun-census-renamed … met=True` exit 0 |

The two omission fixtures shipped with the freeze are also red on their own terms:
`controls/canonical-noop` → `rows_bound=1/11 evidence=1/20 exec=0/0 mismatches=2 met=False`
exit 1 (`receipts/noop-rows-only.out`); `controls/no-canonical` → `rows_bound=0/11 … met=False`
exit 1 (`receipts/no-canonical.out`). Note that `no-canonical` selects the **round-48** table
(`canon_round=48, canon_rows=11`): it omits content, not the canonical heading — a distinction
the L1 should know when designing a "no canonical table" control.

## What this case test does not establish

* No-op rejection here is rejection of an *omitting* instrument; a **replay** of a receipt
  recorded at the same tip is accepted (`receipts/verify-cmd-copycat-sametip.out`), because the
  facts it states are true at that tip. Replay onto a different tree is rejected
  (`receipts/verify-cmd-copycat-othertree.out`).
* The verifier re-derives with the same helpers as the auditor, so it cannot catch a shared
  parsing error; an independently written second implementation is still missing.
* `exec` binds `--help` executability, not the capability's described behaviour.
* Staleness of a table whose evidence all resolves is out of scope here (`mut-stale` is
  `met=True`); it is graded by the calibration item, not this one.

## Receipts used by this file

`receipts/independent-derive.out`, `receipts/genuine-base.out`, `receipts/genuine-3d2d5d4d.out`,
`receipts/genuine-8a7f1976.out`, `receipts/frozen-noop.out`, `receipts/verify-frozen-noop.out`,
`receipts/verify-frozen-noop-c2-receipt.out`, `receipts/verify-genuine.out`,
`receipts/verify-forged-omit.out`, `receipts/verify-forged-sha.out`, `receipts/no-heading.out`,
`receipts/mut-delete.out`, `receipts/mut-empty.out`, `receipts/mut-exec.out`,
`receipts/mut-silent.out`, `receipts/mut-extra-row.out`, `receipts/mut-rename.out`,
`receipts/noop-rows-only.out`, `receipts/no-canonical.out`,
`receipts/verify-cmd-copycat-sametip.out`, `receipts/verify-cmd-copycat-othertree.out` —
all under `.ufo/waves/round-57/w1/out/E02CanonicalBinding/`.
