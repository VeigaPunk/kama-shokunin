# OL04 mapping notes — `corpus/knowledge/ollama-evidence-replay.md:60` (base `ec3b0d5`)

Base line (exact): `  the tags-to-ps digest join is an inference; alias names can multiply; and`

It closes the bullet at lines 56-62 that *credits prior coverage*: it says
`served-identity-crosswalk.md` §Claim / crosswalk row / §Grounded failure cases 3, 5, 6 / §Aliases and
path normalization limits already record these cautions. The line cites no S0xx row itself; the file it
cites carries S010/S011/S012 for the Ollama alias and digest statements. So the line is a restatement
of lane policy about its own classifier, with two propositions: the tags→ps digest join is labelled an
inference, and alias names can multiply.

Evidence used: committed `.ufo/waves/round-60/live/receipt.json` (schema `kama-ollama-live/v1`, nonce
`b61c98ad5747`, `bin/ollama` sha256 `b0a4becf…1b4c`, `receipt_caps(ok)=True`). Second look: my own run
of `tools/kama-ollama-live.py --work <scratch>/run --out <scratch>/r.json` (nonce `7738c503aa04`, port
34219, verdict `MODEL_OK`, exit 0, every capture sha matches its body); receipt retained here as
`second-look-receipt.json`. Both receipts evaluate the OL04B predicate identically (`True`) and carry
the same shapes, so the observation is not a nonce artefact.

## OL04A — `not-observable`

Statement in my words: the join between a `/api/tags` entry and a `/api/ps` entry is kama's own
inference — Ollama's pages do not document digest-based joining of these two surfaces — so a
"same model" conclusion drawn from that join is a lane construct, not an engine guarantee.

Why no capture can test it: the statement is about *documentation provenance and the lane's own
labelling*. The registry's predicate language sees only parsed JSON capture bodies, and no captured
body (version, tags, tags-empty, v1-models, v1-models-empty, v1-model-single, show, ps-before,
generate, ps-after) carries whether a join is documented. A true/false predicate here would be a
predicate over the lane's prose, not over Ollama.

Observed context (not a verdict, recorded for the amendment-free record): `tags` and `ps-after` do
agree on `digest` `8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792`, while their
`size` fields differ (tags `1185492`, ps-after `6312427`, identical in both runs). The join therefore
cannot be a whole-record equality; it must pick a key. That is consistent with the clause but cannot
establish "inference vs documented".

## OL04B — `confirmed`

Statement in my words: one model may answer to more than one name, so a name-keyed identity match is
unsafe.

Observed: in the same run, one imported model (single digest, one `ollama create`) is reported as
`kama-b61c98ad5747:latest` by `/api/tags` (`name` and `model`) and by `/v1/models` (`data[0].id`), and
as `kama-b61c98ad5747` by `/v1/models/kama-b61c98ad5747` (`id`). The receipt's own observation records
`v1_single_id_equals_list_id: false`; the second run reproduces the same split (`kama-7738c503aa04:latest`
vs `kama-7738c503aa04`).

Scope limit (stated, not hidden): the capture performs exactly one `ollama create` and creates no
second native tag alias, so the same-surface alias multiplication of failure case 5 (`ollama cp`,
context-size variant) is *not* exercised. What the capture confirms is cross-surface name multiplicity
for one model in one run — enough to keep name-keyed identity out of the classifier, not enough to
claim alias counts grow per copy.

## Amendment

No row is `contradicted`, so no amendment paragraph is proposed. The live capture did not falsify
either proposition.

## Advisory frontier drafts — proposals only, NOT applied (lane source is read-only for this seat)

- **SOURCES S519 proposal** (round format, 11 columns):
  `| S519 | Ollama v0.40.11 release asset ollama-linux-amd64.tar.zst — https://github.com/ollama/ollama/releases/tag/v0.40.11 | release | A | digest-pinned acquisition of the official Ollama binary that supplies the live surface | release tag v0.40.11, asset ollama-linux-amd64.tar.zst (1508659610 bytes), archive sha256 7bedab90…4b6d, bin/ollama sha256 b0a4becf…1b4c, as recorded in registry/ollama-live-pin.tsv, opened 2026-10-27 | the binary the live claim runs is an official release asset and can be re-derived from its published digest | mined | 2026-10-27 | on-release | tools/kama-ollama-live.py, registry/ollama-live-pin.tsv, .ufo/waves/round-60/live/receipt.json |`
  The companion server/import *docs* rows must be drafted by whoever actually opened those pages; I
  did not open them, so I do not draft sourced doc text (no fabrication).
- **Mined mistake (mine, this wave):** I first wrote the true capture fact
  `c['tags']['models'][0]['size'] != c['ps-after']['models'][0]['size']` as a candidate predicate. It
  evaluates `True` yet `falsifiable()` returns `False`: mutating a scalar leaf to `None`, a sentinel
  string or `""` leaves an inequality between a scalar and an int true, so the predicate cannot be
  flipped. Lesson: a true observation is not yet a registerable predicate; it needs an equality,
  membership or containment anchor that a capture mutation can invert.
- **Knowledge entry proposal** (one, grounded in two runs of v0.40.11 on the fixture GGUF, one model,
  CPU): "On Ollama v0.40.11 the same model is named `X:latest` by `/api/tags` and `/v1/models` but `X`
  by `/v1/models/<name>`; `/api/tags` `size` (1185492) and `/api/ps` `size` (6312427) also disagree
  for one shared digest, so name-keyed and size-keyed joins both break while digest stays stable —
  name multiplicity is cross-surface, not only an alias-copy effect. Two runs (nonces b61c98ad5747,
  7738c503aa04); scope: one version, one fixture model, one host, no alias copy performed."
