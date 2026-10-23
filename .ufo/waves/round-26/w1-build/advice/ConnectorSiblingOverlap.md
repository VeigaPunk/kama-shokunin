# ConnectorSiblingOverlap — advice (round 26 wave 1, §3 sibling-overlap scan)

Verdict: no sibling holds source-pinned llama-server error signatures; C1's space is
uncontested. Four siblings hold adjacent knowledge kama should cite, not absorb: kengaku
(served-model measurement; explicitly non-owner of the serving plane), kagi (credentials,
auth flows, API-key handling, consumer endpoint diagnostics), kumitate (omp
dispatch/route/fallback semantics), tsukuroi (OS/package/systemd/journal/driver error
strings). Full path:line evidence in `.ufo/waves/round-26/w1-build/out/ConnectorSiblingOverlap/overlap.md`.

## Observations (exact)

1. **kengaku — served-model surface, explicit empty seat.**
   - `kengaku-shokunin/PROVINCE.md:24-25`: "**Not owned:** the model-serving plane
     (llama-server flags, slot/batch config) — no lane owns it; escalate to the integrator
     instead of remediating." Kama's C1 sits exactly here.
   - `kengaku-shokunin/PROVINCE.md:14`: served-model surface pin (34113, `/v1/models`,
     `/health`, pid 1299 process pin). `SKILL.md:452-456` (#7052), `:487-499` (scope
     limit). `corpus/evidence/round10-fleet/r10-scout-endpoint.md:21-36`: live capture,
     `version: 0.3.0-dev (build 1, commit d7bd3bf)` — a different build than kama's pinned
     b11755/704366d (separate fixtures).
2. **kagi — consumer auth/endpoint diagnostics.**
   - `kagi-shokunin/SKILL.md:42` (`stream error Cannot connect to API` = dead model
     endpoint; backoff 2→5→9→19→30 s), `:43` (endpoint-verify; 8080 Jitsi vs 34113
     llama-server), `:57-62` (401/Basic/Bearer matrix), `:459-461` (auth gap).
   - `kagi-shokunin/corpus/knowledge/handler-on-disk-state.md:148-149`, `control-plane-hardening.md:20-60`,
     `handler-trust-boundary.md:33-57`, `transcript-hygiene.md:44-59`,
     `corpus/transcript-scan.sh:91-96`, `lessons/round-7.md:57-60`.
3. **kumitate — dispatch/route taxonomy.** `kumitate-shokunin/SKILL.md:437-441`
   (429→rate_limit, 401→authentication, 403→permission_denied, 400→invalid_request).
   Kama's own `corpus/knowledge/consumer-registry.md:101-105` marks the omp builtin
   `llama-cpp-local` default kumitate-owned.
4. **tsukuroi — OS error strings.** `tsukuroi-shokunin/SKILL.md:46-50`;
   `corpus/knowledge/systemd-user-plane.md:19-23`, `journal-boot-plane.md:160-164`,
   `root-dac-decision-r12.md:121-124` (POSIX errno).
5. **No-llama-server lanes:** chousa, souji, kasegi, mado, tabi, tameshi, kaidoku, lore,
   kotoba, kotodama, kake, game-dev-2d/3d, audio, mori, revenger — no server error
   knowledge. Scattered "does not support"/"failed to load"/"address already in use"
   occurrences are prose, dictionary entries, OSS binary-string dumps (kotoba
   `.ufo/round-44/evidence/omp-live-18.12.2-strings.txt:16938`), or unrelated eval
   fixtures (kengaku `round28-calibration`).

## Proposed move (one bounded proposal)
Before the SKILL.md "## Round-26 live error signatures" section lands, add a one-line
"cited, not absorbed" note naming the four sibling owners (kengaku served-model metadata,
kagi auth/credential diagnostics, kumitate omp dispatch, tsukuroi OS error strings) and
keep the registry's signature source strict to the pinned llama.cpp 704366d files. Do not
register kagi's consumer-side `Cannot connect to API` or auth-matrix strings as C1
signatures (they are not llama-server source literals here). For any http-channel 401/403
row, record kagi's courtesy scope for the auth interpretation. One family per row: the
"This server does not support " prefix in server-common.cpp is shared, so under clause (g)
one counted row blocks its members — plan distinct trigger rows per family member or accept
the family cap.

## Axis effect
Depth: the C1 section still lands with ≥12 registered signatures (source-verbatim space is
uncontested). Calibration/adjacency: the section explicitly resolves sibling boundaries,
avoiding the anti-pattern of kama claiming kagi/kengaku/kumitate/tsukuroi vocabulary —
this protects the same calibration axis the rejected r24-r25 streak worked, without
consuming depth tokens. No axis harmed.

## Risks
- If a data seat registers auth-family strings as kama's own knowledge without the kagi
  courtesy note, the section reads as absorbing kagi's credentialed domain (cross-lane
  bleed). Mitigation: the note above.
- Family-prefix rows could inflate the count if the counter's clause (g) does not catch
  same-family variants; A1 already blocks help/version text, and the L1 control run showed
  the family blocks its members — register families once.
- kengaku's build differs (d7bd3bf vs 704366d); citing its served-model captures is
  historical context, never a substitute for kama's live fixture reproduction.

## Verification
- Grep evidence above is reproducible: patterns `llama`, `llama-server`, `does not
  support|failed to load|couldn't bind|could not bind|address already in use`, `api[_
  -]?key|bearer|unauthorized|401`, `llamacpp|llama.cpp|b11755|704366d` over each
  sibling's SKILL.md/PROVINCE.md/corpus.
- Files written (only these): `.ufo/waves/round-26/w1-build/out/ConnectorSiblingOverlap/overlap.md`
  and this advice file. No sibling/lane/fleet files were modified; no server started; no
  port used.
