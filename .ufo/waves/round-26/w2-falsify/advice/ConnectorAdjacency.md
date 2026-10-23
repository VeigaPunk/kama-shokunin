ATTACK adjacency of the landed R26 section (heading SKILL.md:1062, cited-not-absorbed note SKILL.md:1077-1080, table SKILL.md:1082-1100, tail SKILL.md:1102-1111): partial

Verdict reasoning in one line: no counted row registers a sibling-held string and no row is an auth row (the rows hold), but the note that claims to resolve sibling boundaries names three of the four owners its own cited source names (kumitate is missing), and its kengaku clause silently contradicts kengaku's standing refusal of the serving plane.

## Environment / non-actions

- Lane tip `f406697`. The measured tree of the C1 receipt is `7e5ff9b5`; `git diff --stat 7e5ff9b5 HEAD -- SKILL.md registry/error-signatures-r26.json corpus/SOURCES.md` printed nothing (exit 0), and `git status --porcelain -- SKILL.md` printed nothing, so every line number below is valid in both trees.
- No llama-server started by this seat, no port used, no counter run. `pgrep -af llama-server` at 01:0x showed one child not mine: `1879444 /home/vgpnk/.local/bin/llama-server -m /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47570 -t 2` (another w2 seat using the counter's port block). I left it alone.
- No installs.

## Observation 1 — sibling-signature absorption: none found, with a working control

For each of the 15 distinctive strings in the registry (`registry/error-signatures-r26.json`, entries E26-01..E26-17), over every sibling lane root under `/home/vgpnk/Projects/shokunin`:

```
cd /home/vgpnk/Projects/shokunin && grep -rIl --include='*.md' --include='*.json' --include='*.tsv' --include='*.txt' \
  -F -- "<signature>" */SKILL.md */PROVINCE.md */corpus | grep -v '^kama-shokunin/' | wc -l
```

Result: `0` for all 15 (`This server does not support`, `No available space in KV cache`, `Pooling type 'none'`, `failed to open GGUF file`, `invalid magic characters`, `GGML_ASSERT`, `is too large to process`, `Request body must be an array`, `does not support audio input`, `input_audio`, `Infill is not supported`, `lora-adapters`, `does not support embeddings`, `does not support reranking`, `global properties`). Control, same command against `kama-shokunin/SKILL.md kama-shokunin/PROVINCE.md kama-shokunin/registry kama-shokunin/corpus`: `2`-`3` files for every string, so the probe is not vacuous. Sibling corpus dirs exist for kengaku, kagi, kumitate, tsukuroi, mori (verified by `ls -d`).

Secondary probe, code files (`*.py *.sh *.mjs *.js *.rs`) for five of the most distinctive strings, over the 21 `*/corpus`, 9 `*/tools` and 3 `*/scripts` directories:

```
grep -rIl --include='*.py' --include='*.sh' --include='*.mjs' --include='*.js' --include='*.rs' \
  -F -e "No available space in KV cache" -e "Pooling type 'none'" -e "GGML_ASSERT(n_outputs" \
  -e "increase the physical batch" -e "Infill is not supported" */corpus */tools */scripts \
  | grep -v '^kama-shokunin/'
```

No output, exit 1, wall 0.9 s. Control for the `.py` branch: the same string set matches `kama-shokunin/.ufo/waves/round-26/w1-build/out/ReviewerCounterCode/gen.py` (`grep -c -F "No available space in KV cache"` → `2`, lines 81 and 96). A wider `*/` scan with the same set hit `timeout 240` (wall 240.12 s, 240 s limit), so that wider negative is not used as evidence; only the 0.9 s targeted run is.

Auth rows: `grep -n "401\|403\|api-key\|auth" registry/error-signatures-r26.json` printed nothing (exit 1); rows SKILL.md:1084-1100 contain no 401/403; the section lists `authentication_error`/`invalid_request_error` as observed-but-not-registered at SKILL.md:1106. So kagi's auth vocabulary is not absorbed.

All 17 rows' sources are llama.cpp files (server-context.cpp, server-common.cpp, gguf.cpp, llama-context.cpp), per the registry dump.

## Observation 2 — DEFECT: the note drops kumitate, which its own cited source names as one of four owners

- Landed note, SKILL.md:1077-1080, names kagi, kengaku, tsukuroi. The string `kumitate` does not occur anywhere in SKILL.md:1062-1111 (`sed -n '1062,1111p' SKILL.md | grep -c kumitate` → `0`).
- The note's own citation says four: `.ufo/waves/round-26/w1-build/advice/ConnectorSiblingOverlap.md:3-8` — "Four siblings hold adjacent knowledge kama should cite, not absorb: kengaku …, kagi …, kumitate (omp dispatch/route/fallback semantics), tsukuroi …" — and its proposed move at `:43-45` says "add a one-line 'cited, not absorbed' note naming the four sibling owners (… kumitate omp dispatch …)". The note under-implements the artifact it cites.
- The lane's own boundary already says this: SKILL.md:27-29 ("dispatch/route *mechanism* (kumitate)") and SKILL.md:139 ("Route mechanisms belong to kumitate"); arbitration row `corpus/knowledge/cross-lane-scope.md:28`. The omitted clause leaves this section's consumer-facing next actions without the kumitate fence that SKILL.md:27-29 and SKILL.md:139 apply elsewhere in the same file.
- This is not cosmetic because five rows hand out endpoint-selection / failure-classification instructions in the next-action column: E26-05 SKILL.md:1088 ("Point embedding consumers at a server launched with `--embeddings`"), E26-06 SKILL.md:1089 ("use the non-OpenAI `/embedding` route"), E26-09 SKILL.md:1092 ("send the task to `/completion`"), E26-12 SKILL.md:1095 ("Route audio to a model launched with an audio-capable `--mmproj`"), E26-13 SKILL.md:1096 ("remove audio parts or route to an audio-capable model"). E26-10 SKILL.md:1093 ("Do not read the 500 as a crashed server") and E26-13 ("A client-side capability mismatch reported as a server error") are failure-classification statements; kengaku's own refusal row hands that class to kumitate: `kengaku-shokunin/PROVINCE.md:27-28` ("**kumitate:** OMP route resolution, fallback policy, operational failure taxonomy"). A reader who follows these next actions has no pointer saying resolution and taxonomy are kumitate's.
- Smallest correction — add one clause to the existing note, no row change:
  `; how an omp dispatch or alias resolves is kumitate's (corpus/knowledge/consumer-registry.md:101, cross-lane-scope.md:28) — the rows below describe this server's own endpoints and status meanings, not route resolution`
  Both cited in-lane anchors are real: `corpus/knowledge/consumer-registry.md:101` marks the omp builtin `llama-cpp-local` default (`LLAMA_CPP_BASE_URL || http://127.0.0.1:8080`) and `corpus/knowledge/cross-lane-scope.md:28` is the "route-selection mechanism → kumitate" arbitration row.

## Observation 3 — DEFECT: the kengaku clause contradicts kengaku's standing refusal without recording it

- `kengaku-shokunin/PROVINCE.md:24-25`: "**Not owned:** the model-serving plane (llama-server flags, slot/batch config) — no lane owns it; escalate to the integrator instead of remediating."
- The landed heading says the opposite owner: SKILL.md:1062 "## Round-26 live error signatures (b11755 fixture, owner: kama)", and the rows give serving-plane flag remediation: E26-01 SKILL.md:1084 "Re-launch with `--slots` only if a consumer needs `/slots`", E26-06 SKILL.md:1089 "Launch with `--pooling mean`", E26-10 SKILL.md:1093 "Raise `-ub`/`-b`", E26-02 SKILL.md:1085 "Set `--slot-save-path`".
- The note at SKILL.md:1079 records only "served-model quality is kengaku's". It does not record the empty seat that the cited advice file itself calls out (`.ufo/waves/round-26/w1-build/advice/ConnectorSiblingOverlap.md:12-13`: "kengaku — served-model surface, explicit empty seat"; `out/ConnectorSiblingOverlap/overlap.md` §1: "This is the explicit empty seat kama occupies"). The result is a live cross-lane contradiction: kama claims a plane that kengaku still publishes as unowned, and the section's own citation resolves that contradiction only in a wave artifact, not in the sentence.
- Smallest correction — add one clause to the same note, and nothing to the sibling:
  `; kengaku records the serving plane as unowned (kengaku-shokunin/PROVINCE.md:24-25, "no lane owns it"); this section is kama's first claim there, and re-pointing that refusal is kengaku's, not kama's edit`

## Observation 4 — checked and cleared (no fix needed)

- E26-17 (SKILL.md:1100) and the unregistered SIGSEGV sentence (SKILL.md:1108-1111) are the only process-death vocabulary. `mori-shokunin/PROVINCE.md:6-9` owns journal-derived kill/OOM catalog-ID and signal-11 coredump records and explicitly refuses "endpoint and model-serving health (→ kama)"; tsukuroi (SKILL.md:46-50) owns the OS/systemd/journal planes. The observed exit 134 / SIGABRT is kama's own foreground child, not a journal classification → not absorption.
- E26-15/E26-16 (SKILL.md:1098-1099) mention the OS error text ("the system error at the end of the line … names the cause") but register only gguf.cpp literals; the tsukuroi clause in the note covers the class → not absorption.
- E26-07 (SKILL.md:1090) and E26-14 (SKILL.md:1097) say "Client bug". Kagi's declared domain is "secrets & vault ops — the-janitor flows, credential hygiene evidence" (`kagi-shokunin/PROVINCE.md:3`); a missing JSON field is request shape, not credential hygiene → not absorption. Note the inverse hazard: the cited `overlap.md` ruling 2 uses the broader phrase "consumer-side request hygiene" for kagi, which is wider than kagi's own province; the landed note's narrower "API-key and authentication errors" is the safer wording — do not widen it when applying the corrections above.
- E26-09/E26-12/E26-13 make capability statements ("Model capability, not server configuration"). Capability is server/model configuration, not kengaku-style scoring or evaluation claims → not absorption.
- The note's in-lane anchor is correct: `Invalid API Key` is at SKILL.md:181, inside "## Historical error signatures" (heading SKILL.md:167, next heading SKILL.md:193).
- The note's citation target exists and is tracked: `git ls-files` lists both `.ufo/waves/round-26/w1-build/advice/ConnectorSiblingOverlap.md` and `.../out/ConnectorSiblingOverlap/overlap.md` (exit 0). The line numbers in the cited overlap.md are accurate as spot-checked: kengaku PROVINCE.md:24-25, kagi SKILL.md:42-43, kumitate SKILL.md:437-441, tsukuroi SKILL.md:46-50.

## Proposed move (one bounded edit)

Replace the paragraph at SKILL.md:1077-1080 with:

```
Cited, not absorbed: API-key and authentication errors are kagi's (the lane
already holds `Invalid API Key`, SKILL.md "Historical error signatures");
served-model quality is kengaku's; OS and service-manager errors are
tsukuroi's; how an omp dispatch or alias resolves is kumitate's
(`corpus/knowledge/consumer-registry.md:101`, `cross-lane-scope.md:28`) — the
rows below describe this server's own endpoints and status meanings, not route
resolution. Kengaku records the serving plane as unowned
(`kengaku-shokunin/PROVINCE.md:24-25`, "no lane owns it"); this section is
kama's first claim there, and re-pointing that refusal is kengaku's, not
kama's edit. Boundary scan: wave-1 connector
`.ufo/waves/round-26/w1-build/advice/ConnectorSiblingOverlap.md:3-8`.
```

This is one paragraph at the same position; no row, no registry entry, no SOURCES row, and no sibling file changes.

## Affected axes

- depth (the C1 axis): unchanged. The counter parses only `|`-leading lines inside the section — `skill_rows`, `.ufo/waves/round-26/count-c1.py:131-140`, called once at `:325-328`, `HEADING` at `:75`; the only tip-tree read of SKILL.md is that call. The edit adds no `|` line and no signature, so `counted 17` is invariant. This is a code-path claim, not a run: I did not run the counter (no port block for this seat). Counter sha256 `6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588` equals the frozen value in `preregistration.json`.
- adjacency/calibration: improved. The section stops being the one SKILL.md surface that discusses consumer endpoint choice without the kumitate fence (SKILL.md:27-29, :139), and it records kengaku's published refusal instead of silently contradicting it.
- No axis harmed.

## Risks

- Applying the edit while other w2 seats are reading SKILL.md will move their line numbers (the note grows from 4 lines to about 13; the table shifts down). If a seat pinned absolute lines, land the edit after the wave returns.
- The kengaku clause is a report, not a repair: until a kengaku seat re-points `PROVINCE.md:24-25`, the two lanes still disagree. Editing the sibling is out of bounds and would be a worse defect than the contradiction.
- If the L1 prefers to fix this in the rows' next actions instead of the note, it touches counted row text and the counter's clause (a)/(g) inputs; the note-only edit avoids that class of risk entirely.
- The note's citation to a round-26 wave path is round-scoped. That is existing precedent in SKILL.md (e.g., SKILL.md:253 cites `../.ufo/reports/round-3/kagi.md`), so it is not a defect; the two in-lane corpus anchors added above give it a durable fallback.

## Verification (for the L1, after the edit)

1. `sed -n '/^Cited, not absorbed/,/^$/p' SKILL.md | grep -c '^|'` → `0` (the note still ends at a blank line and stays outside the table).
2. `sed -n '1062,1120p' SKILL.md | grep -c kumitate` → `1`.
3. Re-run the frozen counter in a scratch `git archive` extract under the host lock (`flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out <file>`); expect `registered 17 counted 17 target 12 met True`.
4. Re-run the sibling probe above after any further SKILL.md edit; every string must stay at `0` outside kama.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/advice/ConnectorAdjacency.md` (this report). Nothing else; no scratch files, no lane production file, no sibling file.
