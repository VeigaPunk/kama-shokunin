# OL01 — base line mapping notes

Base population coordinate: `corpus/knowledge/ollama-evidence-replay.md:35` at
`ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`.

Base line (verbatim): `therefore kama lane policy, marked **[INFERENCE]**, not upstream behavior.`

The sentence it ends (base lines 32-35): both Ollama pages are undated OpenAPI 3.1.0,
`info.version 0.1.0`, opened 2026-10-20; they document response fields but no matching,
precedence or readiness rule; therefore every classification rule *below* (the `/api/tags`
and `/api/ps` field table at 37-40 and the remote-marker paragraphs at 42-47) is lane policy
marked INFERENCE, not upstream behavior. Cited rows: S031 (`ModelSummary`, `/api/tags`) and
S012 (`Ps`, `/api/ps`), both `A` in `corpus/SOURCES.md:24,43`.

Decomposition used for the mapping: the sentence asserts (a) which fields the live pages
expose, (b) that the lane's use of those fields is undocumented policy, (c) that no upstream
rule was borrowed. (a) is testable from the capture bodies; (c) is a provenance statement
about the vendor page text and the classifier source, which no capture holds.

## Rows

### OL01A — quote `marked **[INFERENCE]**, not upstream behavior.` (confirmed)
My words: the `/api/ps` rule set is lane policy because upstream exposes a fixed set of ps
entry fields and no remote-marker field; accepting a ps entry that carries `remote_model` or
`remote_host` as a remote marker is therefore the lane's inference for real-world exports, not
a documented ps field (base 42-43).
Observed: `ps-after` entry keys = `context_length, details, digest, expires_at, model, name,
runner, size, size_vram`; no `remote_model`, no `remote_host`. One loaded entry, digest
`8cf91c71…c792`.
Predicate: the exact live key set equals the documented field set plus the live-only `runner`.
It fails if any documented key disappears or any extra (e.g. remote-marker) key appears.

### OL01B — quote `therefore kama lane policy` (confirmed)
My words: the tags remote-field rule (a remote tags entry cannot be counted as locally loaded)
is policy, because the live tags body for a locally imported model carries no remote fields.
Observed: `tags` entry keys = `capabilities, details, digest, model, modified_at, name, size`;
no `remote_model`, no `remote_host`; `details.parent_model = stories260K.gguf`.
Predicate: exact live tags key set. Fails if a remote field appears or a documented key is lost.

### OL01C — quote `not upstream behavior.` (not-observable)
My words: the provenance claim — that the vendor pages contain no matching/precedence/readiness
rule and that the rules therefore were not borrowed from upstream.
Why no capture can test it: the committed receipt holds 10 parsed server HTTP bodies (`version`,
`tags`, `tags-empty`, `v1-models`, `v1-models-empty`, `v1-model-single`, `show`, `ps-before`,
`generate`, `ps-after`) plus a non-JSON root body and child-run checks. It contains no copy of
`docs.ollama.com/api/ps` or `/api/tags`, no page fetch, no OpenAPI text, and no
`tools/kama-ollama-evidence.py` source; documentation content and rule provenance are absent
from every captured surface, so a predicate here could only be a tautology or an error.

No row of this line is contradicted: no captured surface falsified the sentence, so no
amendment paragraph is owed. C2 requires `amended == contradicted`; this line contributes
0 to both.

## Incidental observations (not rows — they belong to other lines)

- Live ps entries carry `runner` (`llamacpp`) and live tags entries carry `capabilities`
  (`["completion"]`); neither appears in the base table's field columns. The table lists
  fields the replay may/must-not use, not an exhaustive field inventory, so this does not
  contradict base 39-40, but the amendment pass may want to note the two extra fields.
- `tags.size = 1185492` and `ps-after.size = 6312427` for the same digest
  `8cf91c71…c792`: independent live support for base 40's rule that `size` carries no
  identity or residency work — a size-based join would have failed on this run.
- `tags-empty` and `ps-before` have byte-identical bodies (`{"models":[]}`,
  sha256 `a6fe9ec6…`), which is the premise behind the `available_not_loaded` rule at base
  20-21 (that line is another seat's coordinate).

## Validation (evidence)

`validate.log` in this directory records, against
`tools/round60-c2-counter.py` loaded via importlib and the committed receipt:
`receipt_ok True`, 10 caps, `root` absent; every quote an exact substring of base line 35 and
3-5 words; `evaluate==True` and `falsifiable==True` for OL01A and OL01B; OL01C predicate empty
with a 195-character reason; `score()` over the population with only these rows gives
`rows=3 covered=1/14 evaluated=2 eval_lines=1 sensitive=2 bound=2 errors=0 good_rows=3`;
mutation checks (`ps-lacks-context_length`, `ps-gains-remote_host`, `tags-lacks-digest`) flip
exactly the row that reads them; a flipped-verdict copy of OL01A is rejected
(`good_rows=2 < rows=3`).
