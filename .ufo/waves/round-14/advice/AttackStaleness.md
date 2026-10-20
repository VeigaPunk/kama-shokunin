# AttackStaleness — round 14 critic (timing / simultaneity)

Seat `KamaR14.AttackStaleness`, critic, read-only except this file. Reviewed 2026-10-20.
When I checked, these files did not exist yet, so I treat them as **pending**, not defective: `tools/kama-ollama-evidence.py`, `tests/ollama-evidence/cases.json`, `corpus/knowledge/ollama-evidence-replay.md`, and `.ufo/waves/round-14/measure.py`. This review therefore checks the contract (`spec.json` goal line 2: "No timestamps/expiry/current-liveness inferences") against source and corpus evidence. Nothing was run, no network was used, and no tools were installed.

## Axes
- calibration: the C1 target.
- operability: a consumer who reads the verdict must not mistake it for current state.
- provenance: verdict wording must not claim more than the captures show.

## Counterexamples

**CE1: an exit-0 verdict from a stale capture.**
- Setup: a `/api/ps` export taken at t0 lists `m:1` with digest D. A `/api/tags` export of `m:1` with digest D is taken at t0+Δ, after the `expires_at` lease ran out.
- Result: the contract returns `loaded_same_digest` with exit 0. The model is not resident at t0+Δ.
- Why it cannot be fixed by validation: the ps body has no capture-time field. The documented `PsResponse` holds only `models[]`, with `name, model, size, digest, details, expires_at, size_vram, context_length` (`.ufo/waves/round-11/advice/SourceRunning.md:53-71`). `expires_at` is "Time when the model will be unloaded" (S012), measured from a capture time that is unknown.
- So this is a **tradeoff the judge must accept only if the verdict is worded relative to the captures**. Validation does not repair it.

**CE2: `available_not_loaded` read as current state.**
- Setup: the ps capture was taken before the tags capture, or before a later load.
- Result: "absent from ps" becomes "not loaded".
- Existing corpus forbids exactly this: `corpus/knowledge/served-identity-crosswalk.md:35` says "absence at one sample must not be concluded either way". The replay entry would be a second authority that contradicts it unless it narrows the verdict to "absent from the supplied ps capture".
- This is fixable with wording.

**CE3: `identity_conflict` blamed on the runtime.**
- Setup: `ollama pull` refreshes `m:1` to digest D′ between the ps capture (D) and the tags capture (D′).
- Result: exit 1 (`identity_conflict`). Failing closed is correct. The reason text must not say the server is serving the wrong model, because capture skew is an equally valid explanation.

**CE4: tempting time-based "fixes" that each make things worse.**
1. Comparing `expires_at` to the wall clock makes the output nondeterministic: the same fixtures give different exits on different days. It also breaks the selftest literals and is a current-liveness inference that the contract forbids.
2. Using file mtime or the tags `modified_at` field as a capture time is false provenance. `modified_at` is the model's modification time, not the capture time, and copying or exporting a file resets its mtime.
3. A caller-supplied `--captured-at` flag is an unverifiable assertion and drifts toward an acquisition feature.

## Smallest safe correction (by owner)

- **Classifier** (`tools/kama-ollama-evidence.py`):
  - Never read, parse, or type-check `expires_at`, `size_vram`, `context_length`, or `modified_at`.
  - Import no `time` or `datetime`, and call no `os.stat` or `getmtime`.
  - Put one constant reason in `reasons` for every verdict. For example: `"capture timing unknown: tags and ps exports are not asserted simultaneous or current; ps expiry not evaluated"`.
  - Keep the shared key set unchanged. Adding a `timing` key would need L1 to amend the interface.
  - `identity_conflict` reasons should say the digests differ between the supplied captures, without saying which one is current.
- **Fixtures** (`cases.json`), timing-invariance controls with literal expectations:
  - T1 `ps-expires-at-past`: tags and ps both `{"name":"m:1","model":"m:1","digest":"d1"}`; ps adds `"expires_at":"2001-01-01T00:00:00Z"`. Expect exit 0, `loaded_same_digest`.
  - T2 `ps-expires-at-absent`: same as T1 with no `expires_at`. Expect exit 0, `loaded_same_digest`, which shows that `expires_at` is not a required field.
  - T3 (optional) `tags-modified-after-ps-expiry`: tags `modified_at` `"2030-01-01T00:00:00Z"`, ps `expires_at` `"2020-01-01T00:00:00Z"`. Expect exit 0, `loaded_same_digest`, which shows no ordering is inferred across captures.
  - These count as distinct controls on the timing axis only. They are not new verdict classes.
- **ReplayKnowledge** (`ollama-evidence-replay.md`) and the L1 registry map:
  - Gloss `loaded_same_digest` as "listed in the supplied ps capture with a digest equal to the tags capture".
  - Gloss `available_not_loaded` as "absent from the supplied ps capture".
  - State that capture times, same-instant capture, and same-daemon origin are all unknown.
  - Cite `served-identity-crosswalk.md:35-36` as the prior rule, and do not re-claim it as new.
  - Timestamp validation is explicitly out of scope.

## Checks L1 can run (not run by me)
- `grep -nE 'import (time|datetime)|from datetime|getmtime|st_mtime|os\.stat|expires_at|modified_at' tools/kama-ollama-evidence.py`. Expect no functional hits; a mention inside a docstring or comment is acceptable.
- Run the selftest. T1 and T2 must pass with their literal exit codes and IDs.

## Limits
- The classifier, fixtures, and knowledge entry were not available, so I made no claim about their actual behaviour.
- The ps schema facts come from round-11 scout evidence (S012, OpenAPI info.version 0.1.0). I did not re-open the page this round.
- Whether two captures come from the same host or daemon is a separate unknown for AttackReadiness/SafetyInputs; I only flagged it.
- Tooling: none installed or updated.
