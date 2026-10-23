# RevLiveRepeat — C1 counter live-reading reproducibility (advisory evidence, not a verdict)

Item: does the frozen C1 counter (`.ufo/waves/round-31/count-c1.py`, sha256
`d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216`) give a
reproducible live reading run-to-run? Measured via
`tools/instrument-agreement.py` on a fresh `git clone file://` at the dispatch
tip `382d11b2107d335705875da1a4d889b074bd6fa6`.

## What was run (verbatim tails in `w2/out/RevLiveRepeat/report.md`, receipts beside it)

- Clone at tip; counter sha256 re-verified against `preregistration.json`; all
  three live-fixture pins (server b6a31a8e…, library e404b91a…, model 270cba1b…)
  re-hashed and match the registry's `build.*` fields.
- `instrument-agreement.py --runs 3 --cwd <clone> --out ia-receipt.json` driving
  the preregistered counter command (each run: `--lane <clone> --repo <clone>
  --tip 382d11b2… --out $TMPDIR/receipt.json`). **Zero volatile fields declared**
  (no `--normalize` flags; only the tool's built-in `<TMP>`/ISO-date rules).
- Pairwise `diff` of the three counter receipts; port scan of 47900–47998 and
  `pgrep llama-server` afterward (all clean — counter cleaned up its own servers).

## Result

- Tool summary verbatim: `IA runs=3 agree=3 disagree=0 digest=2614e9a65a3e exit=0`;
  tool exit code 0.
- Differing fields across runs: **none** — the three receipts are byte-identical.
- Per-row `counted` vector: identical across all 3 runs,
  `[T×9, F(K31-10), T×8]`; every run's summary reads
  `registered 18 counted 17 target 12 met True not-counted ['K31-10']`.

## Scope

The falsification target survived: the counter's live reading **is** reproducible
run-to-run (3/3 identical digests, fresh server per run, no declared
normalizations laundering the output). This is a statement about determinism
only — it does not rehabilitate the claim's value: the `CriticClaimSize` no-op
registry and `RevCounterFair` meaningless-counted-row defects stand untouched.
Limits: N=3, one host, one minute, no load contention; server-side per-run log
files were not diffed (outside the counter's output contract). No tools
installed; no tracked file modified.
