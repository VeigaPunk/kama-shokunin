# R39Attack07 — scope gate versus lane province

**Axis:** calibration and coverage. **Method:** read-only inspection of the lane working tree at `/fast/scratch/hyaku/kama-r39` (HEAD `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`); no source edit, endpoint contact, or mutation. The R39-07 prompt was obtained from `w1/spec.json` / `dispatch.json`.

## Observations

- `PROVINCE.md` defines kama's domain as local model serving/endpoint health, with ownership including model-list identity reconciliation (lines 3–15); it refuses model quality/evaluation, credentials/auth, route mechanism, and remote web properties (40–43). It separately sets a hard operator-owned write boundary for host configuration and services (45–49), and says out-of-province findings are reported, not absorbed (51–53).
- The current crosswalk already treats OpenAI model-list data as catalog/account availability, not proof of a local server, loaded weights, or execution (`corpus/knowledge/served-identity-crosswalk.md:9,26,39,48-58`). Its province handoff keeps local endpoint identity/liveness in kama while explicitly disclaiming a new probe or behavior change (`:55-59`). At frozen base, the file also already lists `created` among OpenAI card fields, but the cited S016 description does not distinguish its meaning from artifact identity (`:26`). Thus the new field-level distinction is a narrow extension within an existing crosswalk topic, not a new grant of authority over hosted service state.
- The round-39 Gate in `corpus/lessons/round-39.md:17,19,21,23` records one admission (only the `created` distinction, expressly no local-health or loaded-weights assertion), a topical reject (multi-round runtime-health matrix), and a province reject (remote hosted health-route configuration, assigned to kake), each with a flip condition. The broader lesson context is consistent with the declared province: the source is a public API reference and it makes no endpoint claim.
- The amendment (`corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md:1-3,25-27`) says its S472 wording grounds the card-field distinction and expressly does not infer a current endpoint or served artifact. `corpus/SOURCES.md:216` gives S472 a scope of catalog creation metadata, expressly “not local endpoint identity or readiness,” and its sole used-by path is that amendment. `corpus/README.md:551` points to the same amendment and describes the distinction as catalog metadata rather than local served-artifact identity.
- Base-vs-working evidence: frozen base `PROVINCE.md` / crosswalk have the above domain and handoff; `git show <base>:corpus/README.md` has no amendment coverage pointer; base `SOURCES.md` has no S472. Working tree has the Gate, amendment, README pointer, and S472. Lane HEAD remains the frozen base with round-39 work in the working tree; therefore these are not committed round results. The separate source repo has no round-39 artifacts.

## Assessment

**No scope/province falsification found.** The recorded admission narrows itself to an already-covered local model-list interpretation; it neither absorbs endpoint operation nor contradicts a province refusal. The two rejects align with the declared topic boundary and remote-web refusal. This supports the semantic scope of C1's Gate; C2's README/source/file presence is a working-tree condition, not committed coverage. This observation does not establish that the admitted knowledge is novel: base crosswalk already says OpenAI list availability is catalog-only, so novelty is specifically the new `created`-field meaning, not the broader catalog-vs-runtime distinction.

**Unresolved:** this pass did not independently inspect the campaign package's full candidate set or test the Gate's completeness beyond the stated admission/rejections; it establishes that the named choices are consistent with the lane province, not that no other plausible in-scope/out-of-scope candidate was omitted. No L0 province amendment or current runtime state was examined.

## Evidence paths

- `PROVINCE.md:3-15,40-53`
- `corpus/knowledge/served-identity-crosswalk.md:9,26,39,48-59` (base and tip)
- `corpus/lessons/round-39.md:17,19,21,23`
- `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md:1-3,25-27`
- `corpus/SOURCES.md:216`; `corpus/README.md:551`
- `.ufo/waves/round-39/assimilation/preregistration-frozen.json`; `w1/spec.json`
