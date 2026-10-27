# M10MapServedidentity29 — line 29 of corpus/knowledge/served-identity-crosswalk.md

Population coordinate: `corpus/knowledge/served-identity-crosswalk.md:29` at base
`ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b` (base blob read with
`git -C kama-shokunin show ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b:corpus/knowledge/served-identity-crosswalk.md`,
line length 1397). The line is the crosswalk row for Ollama (S010 @c1737589; S011; S012; S031). Evidence: the committed
receipt `.ufo/waves/round-60/live/receipt.json` (schema `kama-ollama-live/v1`, binary pin b0a4becf…1b4c, version
0.40.11, fixture GGUF sha256 270cba1b…256d). No fresh run was needed: every predicate reads only the committed
capture bodies, and capture order in `tools/kama-ollama-live.py` is fixed (tags/v1-models before `/api/ps` and the
single generation).

## Rows

### OL10A — confirmed
Quoted clause: "`/api/tags` (native available list); `/api/ps` (native running list)".
Documented statement in my words: `/api/tags` enumerates models that are installed/available, while `/api/ps`
enumerates only models currently resident in memory; the two lists are distinct surfaces, so a tag being listed
must not be read as a loaded model.
Observed: `tags.models = [kama-b61c98ad5747:latest]` (name == model) captured after `ollama create` and before
any generation; `ps-before.models = []`; after one `/api/generate` call `ps-after.models` has exactly one entry
with the same name. Predicate (all on the committed bodies):
`len(c['tags']['models']) == 1 and c['ps-before']['models'] == [] and len(c['ps-after']['models']) == 1 and c['ps-after']['models'][0]['name'] == c['tags']['models'][0]['name']`
evaluates True; falsifiable True (mutating any of the three `models` lists flips it). No correction needed.

### OL10B — confirmed
Quoted clause: "ps: `name`, `model`, `size`, `digest`, `details`, `expires_at`, `size_vram`, `context_length`".
Documented statement in my words: a `/api/ps` entry for a loaded model carries those eight documented fields, with
`expires_at` as a time string (the documented unload time), `size_vram`, and `context_length` present.
Observed (ps-after[0]): `size=6312427`, `digest=8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792`
(64 hex), `expires_at=2026-10-27T18:34:10.425205706-03:00`, `size_vram=0`, `context_length=2048`; the same entry also
carries an undocumented `runner: llamacpp` key, and `details` nests `parent_model`/`format`/`family`/`families`/
`parameter_size`/`quantization_level`. Predicate evaluates True; falsifiable True (typed fields flip under value
mutation; the documented-key set check is a subset test, so the extra `runner` key is not treated as a contradiction).
No correction needed. Note for the amendment-free record: tags `size=1185492` (on-disk blob bytes) differs from ps
`size=6312427` (loaded footprint), which is consistent with the line's own size wording but means a raw `size`
comparison across tags/ps is not an identity test.

### OL10C — not-observable
Quoted clause: "name-only matching is unsafe".
Documented statement in my words: the crosswalk's matching policy — equality of names must not be treated as
equality of artifacts, because `ollama cp` "copies an existing model name to a temporary name".
Why not observable: the committed receipt imports exactly one nonce-named model (`kama-b61c98ad5747`) and never
runs `ollama cp`; no capture produces a second name, so no captured surface can compare name equality against
digest/artifact equality. (The related [INFERENCE] digest-join clause is likewise a documentation/proof claim no
HTTP body can settle; it likewise has no live predicate here.)

## Contradictions

None: all three rows are confirmed or not-observable, so no amendment paragraph is owed by this seat. My three rows
do not map the row's `/v1/models` metadata-only and `v1-model-single` clauses (row cap 3); the captures that bear on
them are `v1-models` (keys id/object/created/owned_by, `created=1793136550` equal to the epoch of tags
`modified_at`) and `v1-model-single` (`id=kama-b61c98ad5747` without the `:latest` tag while the list entry has it),
plus `v1-models-empty` (`data=null`) — available for another seat or the integrator.

## Evidence

```
$ python3 /fast/scratch/hyaku/kama-r60/M10MapServedidentity29/validate.py   # exit 0
receipt_caps ok= True
pop line29 present: True pop size= 14
OL10A words= 8 substr= True verdict= confirmed
   evaluate= True falsifiable= True
OL10B words= 9 substr= True verdict= confirmed
   evaluate= True falsifiable= True
OL10C words= 4 substr= True verdict= not-observable
   not-observable reason ok
score: {'covered': 1, 'evaluated': 2, 'eval_lines': 1, 'sensitive': 2, 'bound': 2, 'contradicted': 0, 'amended': 0, 'receipt_ok': True, 'good_rows': 3, 'errors': 0, 'met': False}
```

The validator imported `tools/round60-c2-counter.py` via importlib and applied `receipt_caps`, `safe_compile`,
`evaluate`, `falsifiable`, and `score` to these rows exactly as the counter will; `met=False` is expected because the
full C2 predicate needs 5 predicate rows over 4 lines across all w1 seats and the registry is not yet assembled.
No tool install or upgrade was performed; nothing was written outside this out dir and the seat scratch (removed).
