# Round 61 lesson — kama (2026-10-28)

Claims: C1 operability — fresh-nonce hold-verified live Ollama v2 lifecycle (counter
`tools/round61-c1-counter.py`); C2 calibration — frozen-population claim registry under a
bounded evaluator (`tools/round61-c2-counter.py` + `registry/ollama-live-claims-r61.tsv`).
Freeze: `.ufo/waves/round-61/controls/freeze.txt`; base `a107b75f3650981d191d73fde73987415e292e14`.

## Gate

| Source | Accessed | Located quote (≤25 words) | Verdict |
|---|---|---|---|
| S525 `https://docs.ollama.com/openapi.yaml` | 2026-10-28 | `expires_at: type: string; description: Time when the model will be unloaded` (PsResponse schema) | **admit** — tier A first-party spec; grounds the registry's `expires_at`/`size_vram`/show bindings; no existing row carries field-level schema text (S012 names the route, not the fields) |
| staged `merge/kama/` package entries (spot-check of two) | 2026-10-28 | see S06 seat draft | **reject** this round — assimilation deferred: the lane's register slice was regenerated (`assimilation/quarantine-slice`, 7 rows, all `payload-absent`); quarantine-first does not bind kama, but wave seats falsify claims first; entries keep their staged state with flip `hand-check next round` |
| `considerthese/2026-10-26.md` proposal 3 (counter-shortcut trend) | 2026-10-28 | "keep a running count of counters that a shortcut can satisfy" | **adopt** — C2's 9-family controls + sensitivity mutation are exactly that measurement; ledger in report |

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| `unrelated-predicate-registry` — a syntactically valid registry whose rows assert unrelated receipt literals met the r60 C2 counter | r60 falsification W1 K01 + W2 F17/F19 (SCORECARD §Round 60) | none in r60 | r61: frozen MANIFEST triples + located-quote-in-prefix + flip-test sensitivity + amendment ledger; counter rejects 9/9 control families (fixture-verified before data) |
| `counter-docstring-drift` — C1 docstring/PREDICATE said "14 controls" while the code enforced 16 | self-review this round | none | corrected to 16/16 before freeze; A16 seat audits predicate-text/code agreement |
| `population-derivation-overreach` — the frozen-population rule named a *property* of a live file; editing the file changed the extensional set | self-review this round | none | freeze text reworded to "the 18 enumerated lines" with the derivation descriptive-only; J01/J02 seats re-derive |
| `hold-blocks-forever` — first `--hold-dir` run blocked 300 s with no release writer | own run timed out bg_23454 | none | hold-mode runs now always pair with an external release plan; documented in the v2 section |

## Sources opened this round

- `https://docs.ollama.com/api` (route index), `https://docs.ollama.com/api/show`,
  `https://docs.ollama.com/openapi.yaml` (S525 admit) — 2026-10-28.
- `considerthese/2026-10-25.md`, `considerthese/2026-10-26.md` (operator input; ledger in report).
- `/home/vgpnk/Projects/shokuknow/merge/kama/` (read-only recon; no adoption this round).

## Wave receipts

v2 wave `w1` (68 seats) results: `.ufo/waves/round-61/w1/w1-results.json` (folded after
WAVE-DONE into the report).
