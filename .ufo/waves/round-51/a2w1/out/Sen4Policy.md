Verdict: **Round-51 wave size and attack share conform; all live model routes resolve, but dispatch provenance and two prompt/policy inventories have actionable drift.**

## Evidence

- Ran `cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Sen4Policy && ./route_check.py` → exit **0**, `RESULT pass` (`route_check.out`). The script independently counted roles in `a2w1/spec.json`, `dispatch.json` and `out/swarm-registry.json`; each source agrees: 66 seats, 66 unique names, same wave label. `validate.out` records `exit=0`; `validate.stderr` is empty.
- Policy v2 bounds: 64–128 wave seats, maxLanes 256 (`/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json:83-90`). This wave has 66 seats. Attack roles reviewer 11 + critic 9 + mutation-tester 5 = **25/66 = 37.88%**, above the 17-seat floor; addendum's labrat-inclusive count is also 25 because labrat has zero seats. Four connector seats. See `route_check.out` sections 1, 3–4.
- All ten roles resolve through `task.agentModelOverrides` → `modelRoles` to enabled models, each with a fallback chain (`/home/vgpnk/.omp/agent/config.yml:324-367`, lines by role in `route_check.out`). Per-model counts: MiniMax 18, GLM 16, Kimi 14, DeepSeek 14, Gemini 4. Dispatch tasks have no model/modelAlias override.
- For round-50 closure R7, `/home/vgpnk/.omp/agent/config.yml` mtime is **2026-10-27T02:39:08.510680Z** (local `2026-10-26 23:39:08.510680072 -0300`), SHA-256 `0d5874660274d3a4545d9d1f9e1da320f0629a9efb384255b788b897bba6addc`; dispatch registry `createdAt` is `2026-10-27T03:46:01.304Z`, 4,012 seconds later. The complete resolved map and file fingerprints are preserved in `out/Sen4Policy/route_check.out` and summarized in `out/Sen4Policy/policy.md`.

## Findings

1. **Run-9 route labels in `/home/vgpnk/Projects/shokunin/scripts/hyaku/hyaku.env:8-11` disagree with the binding live map** (`lane-addendum.md:10-17`, config lines 353-367). Four roles/36 seats differ: executor 18 (`@m_flash` label vs live `@m_mim`), critic 9 (`@m_flash` vs `@m_kfc`), scout 5 (`@m_sonnet` vs `@m_kfc`), connector 4 (`@m_kfc` vs `@m_antigravity`). A reader relying on the helper labels would assign 36/66 seats to wrong model routes. Proposed correction is in `out/Sen4Policy/proposed-fixes.diff`.
2. **Executor labrat instruction conflict**: `a2w1/build_spec.py:44` says “do not spawn subagents (leaf)” without exception, while rendered executor bounds grant one labrat to all 18 executor tasks; the binding addendum permits that read-only probe (`lane-addendum.md:222-223`). Fix the shared prohibition to expressly allow the one executor labrat; proposed hunk is in `proposed-fixes.diff`. This repeats round-50 closure F4.
3. **Policy role inventory mismatch**: v2 `proposalRoles` includes sentinel (`ufo-wave-policy-v2.json:104-115`), but `lanes[]` lines 256-306 lists labrat and omits sentinel. The wave dispatched four sentinel and zero labrat seats. The validator passed and routing is through config, so no dispatch failure observed; replace the labrat `lanes[]` row with sentinel. Proposed hunk is in `proposed-fixes.diff`.
4. **Policy surface digest differs from live `ufo.json`**: `route_check.out` records policy value `sha256:1064c19a…` and live `/home/vgpnk/Projects/ufo-fsd-alpha/config/ufo.json` value `sha256:610575e8…`. This seat verified only the recorded values differ, not the canonical digest computation; treat as an unadjudicated discrepancy, not a proven stale digest.
5. Two seats bind canonical `adjacency` although wave axes list only calibration/operability: N1Overlap and Sc5Province. Since adjacency is canonical (`AXES.md:16`) and validator passes, recorded as axis-scope telemetry rather than a defect.

No campaign counters, services, lane/fleet files, or Git/JJ state were mutated. No tool was installed.

## Artifacts

- `out/Sen4Policy/policy.md` — full tables, evidence and provenance.
- `out/Sen4Policy/route_check.py` and `route_check.out` — reproducible read-only check and captured output.
- `out/Sen4Policy/proposed-fixes.diff` — proposed corrections only; not applied.
