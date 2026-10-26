# Proposed SKILL.md lines (draft, for lane integration)

Add a `## Round-48 live receipt v5 and replay (owner: kama)` section (near the
round-47 rows, around SKILL.md line 1462) with the rows below. Each row maps to
a guess removed: G1 → counter row + receipts path; G2 → live v5 tool row +
recording checklist; G3 → boundary column sentence.

```markdown
## Round-48 live receipt v5 and replay (owner: kama)

| Surface | Command / exit contract | Boundary |
|---|---|---|
| Live v5 tool | `python3 tools/kama-llamacpp-live.py --server <abs-path> --model <path> --model-sha256 HEX --alias NAME --ctx N --threads M --server-asset-url https://… --server-asset-sha256 HEX --server-member <rel/in-archive-path> --model-url https://huggingface.co/<org>/<repo>/resolve/<40hex>/<file> --server-archive <local-archive> --out PATH` | 0 outcome pass, 1 evaluated failure, 2 setup-error/refused (no receipt on argument refusal). The five provenance flags must come together and are validated BEFORE the server starts: https URLs only, member path relative without `..`, model URL pinned to a 40-hex `/resolve/<commit>/`, archive sha256 == `--server-asset-sha256`, member bytes == `--server` sha256, model sha256 == `--model-sha256`; the receipt then carries `provenance.verified` {at: record, archive_sha256, member_sha256, model_sha256} in schema `kama-llamacpp-live/v5`. |
| Receipt replay | `python3 tools/kama-live-replay.py --receipt <v4-or-v5-receipt> --work <dir> --out <json>`; `--compare A B` compares two receipts offline (no network) | Re-downloads the recorded asset and model into `--work`, verifies both sha256 and the extracted member digest before executing; a v5 replay passes the downloaded archive as `--server-archive`; matching is over a stable projection (props fields, slots count + body digest, health status + body digest, models id/owned_by, metrics status, loading envelope, teardown outcome, listener ownership); ports, pids, times, log text and the models `created` field are instance facts. Exit 0 match, 1 differs, 2 refused. |
| C2 round-48 counter | `python3 tools/round48-live-replay-v5-audit.py --repo <clone> --tip <full-commit> --scratch <dir> [--out <receipt>]` | Prints `receipts=0|1 recordcheck=0|1 replay=0|1 compare=0|1 tamper=0|1 urlswap=0|1 newrow=0|1 replayed=N/3 met=True|False`, then `tip=<full> started=<iso>` and `detail:` lines; exit 0 met, 1 not met, 2 could-not-evaluate. Legs: three committed v5 receipts at `--tip` (`.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json`), record-time refusal checks with a stub server, replay of every receipt from `git archive <tip>` under a scratch HOME with the counter hashing the re-acquired files itself, `--compare` instance-vs-stable cases, tamper and URL-swap refusals, and the pinned model URL as a `corpus/SOURCES.md` row. Needs network to github.com and huggingface.co. |
```

Recording checklist (bullets next to the table):

```markdown
- To record a fresh v5 receipt: download the archive and the model from the
  receipt's `provenance` URLs, verify their sha256, extract
  `provenance.server.member`, then run the live v5 tool above (alias, ctx and
  threads from the receipt's `argv`). A fresh re-run of the evidence is
  `kama-live-replay.py --receipt … --work <empty-dir> --out <json>` or the
  C2 counter.
```

Optional small `--help` improvements (lower value, same class as G3):

- `tools/kama-llamacpp-live.py` `--server-archive` help: append
  `requires all four other provenance flags (--server-asset-url,
  --server-asset-sha256, --server-member, --model-url); a partial set is an
  argument error (exit 2, no receipt)`.
- `tools/kama-live-replay.py` `--help` description: append
  `v5 receipts must also carry provenance.model.commit and
  provenance.verified {at: record}`.
