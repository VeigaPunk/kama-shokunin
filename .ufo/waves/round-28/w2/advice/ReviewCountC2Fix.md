# ReviewCountC2Fix — review of repair 1 (round-28 lesson Repairs row 1)

Seat: KamaR28.ReviewCountC2Fix (falsify, w2). Verdict: **repair holds as
specified**; the one stronger forgery I attempted (cell + raw body + hash,
all coordinated) passes the patched counter exactly as the repair's own
README/docstring disclose. No actionable defect found that the repair or its
documentation hides.

## Scope and method

- Rebuilt the pre-repair counter from `w1/out/ExecCountC2Fix/count-c2.diff`
  (reverse patch) → sha256 `2f952dca58a4ff2efe55cbb9f2afcae1b8ae4efd41a3ee8461522699d77d760b`, matching the README's recorded "lane counter".
- Patched counter sha256 = `5aa64a370196f352435bdf2cee2526019a3eac2737eb194496c5126d5759fa2a` — identical to the current lane file `.ufo/waves/round-25/count-c2.py` (landed in commit e49b4cf; `git log` confirms).
- All runs in scratch: `/fast/scratch/hyaku/kama-r28/w2/ReviewCountC2Fix/` (tree = committed `final/` copy; counters placed at `.ufo/waves/round-25/`).

## What holds (reproduced)

| case | original | patched |
|---|---|---|
| (a) committed receipt | 14 / 14 / bound True / [] | 14 / 14 / bound True / [] |
| (b) forged cells, raw untouched (`forged-cells.receipt.json`) | 14 / 14 / True / [] | 14 / 11 / False / [K2,K4,L1] |
| (c1) forged K3.props.body, hash not rebound | 14 / 14 / False / [] | 14 / 13 / False / [K3] |
| (c2) forged raw + receipt `raw_props` rebound | 14 / 14 / True / [] | 14 / 13 / False / [K3] |
| parity: duplicate K1 id | 14 / 13 / True / [K1] | 14 / 13 / True / [K1] |
| parity: extra unregistered cell, bogus hashes | 14 / 14 / False / [] | 14 / 14 / False / [] |
| fail-closed: no `final/raw` beside patched file | — | 14 / 0 / False / all |

Lesson Repairs row 1 numbers (before 14/True → after 11/False [K2,K4,L1];
before bound True → after bound False) match exactly. SKILL.md instrument
registry row (line 1222) matches the landed bytes and the demonstrated
behavior; KQ36 text in QUALITY.md is unaffected and not falsified.

## Finding 1 (the seat's untried forgery, disclosed not hidden)

**Triple forgery passes.** I edited K3's cell (props_n_ctx 2048→512) AND
its raw body (`forged-K3.props.body`, n_ctx 512) AND re-bound the receipt's
`raw_props` hash to the forged bytes. Patched counter prints
`registered 14 observed 14 bound True missing []` — indistinguishable from
genuine data under the instrument. This is the repair's stated boundary
(README "Boundary"; docstring lines 51-54): it binds receipt↔raw, not
raw↔server; the external anchor is git history. Confirmed empirically in
`/fast/scratch/hyaku/kama-r28/w2/ReviewCountC2Fix/tree-triple/` with
`triple-forged-receipt.json`. Not a hidden defect: readers are told.

## Finding 2 (minor, pre-existing, unchanged by the repair)

`bound True` does not require receipt completeness: deleting an entire
registered cell (id + raw) still prints `bound True` with the cell listed in
`missing` (both counters; e.g. dup-K1 run). Transparent via the missing list;
not introduced by the repair and not covered by the lesson's wording.

## Finding 3 (wording calibration)

"every per-cell value is recomputed" is exact for the value set that
determines observation/binding (props n_ctx, total_slots, per-slot n_ctx,
n_ctx_train, kv-pool candidates/pool, log_lines, load-request outcomes and
mode). Provenance metadata (argv, port, started/stopped_utc,
concurrency_delta_s, observed/error fields) is not recomputed; the README
documents this and `cell_ok` still structurally checks argv/launch flags.
No falsehood.

## Residual risk / verification gaps

- Coordinated forgery (cell+raw+hash) is outside the instrument; only the
  lane's commit history can anchor raw bytes to a server. If a writer
  fabricated all three layers, no counter behavior would flag it. This is
  disclosed, and the lane's git history is the stated guard.
- The demo transcript in `demo-run-all.out` was recorded when the lane still
  held the original counter; re-running `run-demo.sh` today yields
  before==after (both patched) because the repair landed. The recorded
  evidence artifacts remain; reproduction requires the reverse-patched
  original (done here).
- No llama-server started (no ports used); no installs made.

Evidence: this report; scratch under `/fast/scratch/hyaku/kama-r28/w2/ReviewCountC2Fix/` (tree/, tree-raw1/, tree-triple/, fixtures, outputs above).
