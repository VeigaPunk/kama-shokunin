source: S178 — kumitate-shokunin/scripts/counter-rerun.mjs @ ce9aee5, decision note kumitate-shokunin/.ufo/waves/round-48/r48/ReviewQualityDraft.md:123-125 @ 4e4f471; S179 — mori-shokunin/tools/mori-source-drift.py @ e57c58b, mori-shokunin/corpus/knowledge/source-drift-r36.md:21 @ 6827d6e
verified-at: 2026-10-23 (round 30; receipts `.ufo/waves/round-30/c2/selftest.out`, `receipt-a.json`, `receipt-b.json`)
recheck: `python3 tools/instrument-agreement.py --selftest` ; `python3 tools/instrument-agreement.py --runs 3 -- <instrument command>`

# Instrument run-agreement — what a rerun counter shows about a lane instrument

A lane counter's number means nothing if the same tree produces a different number on the next
run. Round 26 found the class on kama's own instruments (a port-reuse and timestamp problem in
live error-signature captures); round 30 turns the discipline into a lane capability:
`tools/instrument-agreement.py` runs one instrument `N` times over the same committed tree in
fresh temp dirs, normalizes only the volatile fields the caller *declares*, and reports
`IA runs=N agree=A disagree=D digest=<sha256 prefix>` with a receipt carrying every run's exit,
normalized stdout/stderr heads and digest.

## What it shows

- A digest of `(exit code, normalized stdout, normalized stderr)` per run, and whether all runs
  share it. `receipt-a.json`: `python3 tools/error-verdict-census.py --json` →
  `IA runs=3 agree=3 disagree=0 digest=24ce96bc3905 exit=0`.
- `receipt-b.json`: `python3 tools/sources-append-only.py --from 2aa46e24 --to 52ac3af --json` →
  `IA runs=3 agree=3 disagree=0 digest=db4c39bbbdfd exit=0`.
- The selftest exercises four arms (`selftest.out`, `IA_SELFTEST pass=4 fail=0`, exit 0): a
  deterministic instrument (`agree=3`), a nondeterministic one whose deviation falls on its second
  run (`agree=2 disagree=1`, tool exit 1), an instrument whose only varying field is *declared*
  (`agree=3`), and an exit-code-only deviation (`agree=2 disagree=1`). The second and fourth arms
  are the fail-capability: a tool that always printed agreement would pass neither.

## What it does not show

- That the instrument is right. A deterministic counter can be deterministically wrong; this tool
  says nothing about a claim's predicate, population or target. `fresh`/`agree` is reproducibility,
  not correctness — the same boundary S179 draws for source copies ("`fresh` proves only byte
  identity with the committed copy, never that the row's `teaches` is right", source-drift-r36.md:21).
- That the declared normalization is harmless. Every declared rule (`--normalize REGEX=REPL`) is a
  claim that the matched text is not part of the measurement. Declaring a digest or a verdict
  string would launder a real disagreement; declaring a temp path or a run id does not.
- Anything about run-to-run *state*: each run gets a fresh `TMPDIR`, so an instrument that depends
  on state left by a previous run is either caught (as the selftest's marker fixture is) or, if the
  state lives outside `TMPDIR`, invisible to this tool.

## A refusal worth keeping: the corpus guard is not an agreement subject

`tests/ollama-corpus-guard/check.py` produced `IA runs=3 agree=1 disagree=2` on three runs of the
same tree (`receipt-b-corpusguard-refused.json`). The difference is its own staging path
(`/tmp/kama-corpus-guard-<rand>/...`) *and* a `tool_sha256` computed over a staged wrapper whose
bytes contain that path. The path is the tool's artifact (declarable); the digest over patched
content is a measurement, so normalizing it away would erase the disagreement the instrument
exists to report. The guard is therefore used as a *fixture* for the discipline, not as an
agreement subject — a counter whose output embeds its own staging identity cannot certify
reproducibility of a claim.

## Cross-lane boundary

- S178 (kumitate r48) mechanizes the *counter* rerun inside its own counter craft; kama adopts the
  discipline for its own instruments and does not take kumitate's implementation, because dispatch
  and counter mechanics belong to kumitate's province.
- S179 (mori r36) compares *committed source copies* against re-fetched bodies over the network;
  kama adopts the byte-comparison rule for its own SOURCES rows and leaves the network re-fetch and
  its state table to mori.
- Neither sibling owns "run agreement for endpoint-health instruments". This entry states the
  transfer and the boundary; contested scope is reported in the round report, not absorbed.

## Limits recorded this round

The tool hashes all blobs of a tree per run only when the caller's instrument forces it; the
default 300 s per-run timeout is the only bound. `--runs 3` is the demonstrated arm; a larger `N`
is untested here. The tool refuses to overwrite an existing receipt path (exit 2), so a rerun needs
a fresh path — that is deliberate, to keep a receipt bound to the tree it measured.
