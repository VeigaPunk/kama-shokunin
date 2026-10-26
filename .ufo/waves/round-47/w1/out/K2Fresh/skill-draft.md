# Draft SKILL.md lines — suggested additions/corrections from the fresh-session test

These are proposed (not applied) changes. Two edits, both in the live-evidence
area of `SKILL.md` (the seat may not edit the lane; this is the draft).

## Edit 1 — add a current live-evidence replay section (insert after the last
round table, e.g. after the Round-46 rows at the end of the file)

```markdown
## Round-47 live evidence replay (v4 receipts, owner: kama)

Current live lifecycle output schema is `kama-llamacpp-live/v4`. The three
round-47 llama.cpp b11909 receipts are committed at
`.ufo/waves/round-47/c2/live/receipt-{1,2,3}.json`; each carries a
`provenance` block (release archive URL + sha256 + archive member, model URL +
sha256) so the evidence can be re-run from committed bytes alone — no host
install, no `~/.local/opt`, no model cache.

Re-run receipt N from a clean home:

```sh
python3 tools/kama-live-replay.py \
  --receipt .ufo/waves/round-47/c2/live/receipt-N.json \
  --work DIR --out OUT.json
```

- All three of `--receipt`, `--work`, `--out` are required.
- Exits: `0` rerun matched the original receipt's checks (pas/fail equality
  per evaluated check), `1` it ran and differed, `2` refused or could not run
  (bad digest, unsafe/absent member, non-v4 schema, network failure).
- The replay re-acquires the release archive and the model into `--work`,
  verifies both sha256 digests before use, reruns the full lifecycle, writes a
  new v4 receipt next to `--work/rerun-receipt.json`, and refuses (exit 2) on
  any digest mismatch.
- Needs network access to github.com and huggingface.co (~23 MB + 1.2 MB per
  replay). Run from a lane checkout: `registry/endpoint-consumers.tsv` and
  `tools/kama-probe.sh` are resolved relative to the `tools/` directory.
- `kama-llamacpp-live.py`'s provenance flags (`--server-asset-url`,
  `--server-asset-sha256`, `--server-member`, `--model-url`) only record where
  inputs came from; they never fetch. To re-run from zero, use
  `kama-live-replay.py`, not `kama-llamacpp-live.py` alone.
```

## Edit 2 — mark the historical live rows as superseded (line 611, and by
extension lines 537/575)

Append to the Round-18 “Live v3 tool” row (line 611) and to the Round-16/17
live rows a pointer:

```markdown
Historical b11755/v3 guidance. Current schema is `kama-llamacpp-live/v4`;
current evidence (round 47) is re-run with `tools/kama-live-replay.py` from the
receipts in `.ufo/waves/round-47/c2/live/` — see the Round-47 live evidence
replay section. The host paths below (`~/.local/opt/llama-b11755/llama-server`,
`~/.cache/kama-shokunin/models/stories260K.gguf`) exist only where historical
installs survive; do not rely on them for a fresh re-run.
```
