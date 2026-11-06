# Proposed one-line handoffs for `corpus/knowledge/cross-lane-scope.md` (round 91, prose only)

Seat `CN01SiblingOverlap`, read-only scan at lane `KamaR91a2`. Nothing below is landed; the L1
integrates. Each line is copy-pasteable and names its evidence.

## New section «Serving thresholds — who may set what (round 91)»

- **Flag authority is the operator's, not kama's.** `SKILL.md:1885` (T04), `:1888` (T07), `:1892`
  (T11), `corpus/knowledge/serving-thresholds.md` §Limits ("a unit's argv or environment overrides
  them, and kama does not read service units (operator-owned)"), `PROVINCE.md:45-49`. Kengaku's
  `PROVINCE.md:15` ("flag authority is kama's (serving plane)") must not be adopted as written: that
  lane's own `PROVINCE.md:47-48,74,158` says flag-change authority is "unowned/integrator". Rule: no
  lane sets a serving flag on kama's behalf, and kama never sets one.

- **A pin's default is not the host's setting.** kama reads the default at one tag and reports the
  override from argv; a sibling's capture is evidence of the override only. Live counterexamples:
  `kengaku-shokunin/corpus/evidence/round51/surfaces/endpoints.txt:12-14` — 5 ids listed on the
  `:1234` router whose argv carries `--models-max 2` (T06's b12177 default is 4), and
  `kengaku-shokunin/corpus/evidence/round10-fleet/r10-scout-endpoint.md:33` — an older `:34113` unit
  with `--timeout 900` (T02's default is 3600 s). Neither contradicts a row; both would be misread as
  one.

- **No sibling may cite kama's T-rows as a live unit setting.** The rows are `source`-bound to a tag
  (`S593` b12177, `S594` v0.40.11, `S595` v0.32.0); a lane that needs the host's value reads the unit
  argv, as kengaku already does (`PROVINCE.md:14`). A sibling capture at a different build is not a
  counterexample: kengaku's `r10-scout-endpoint.md:36` build is `0.3.0-dev (build 1, commit d7bd3bf)`,
  its round-51 successor reports `build_info=b1-39febd2` (`endpoints.txt:15`) — the latter is the only
  string to cite, because `PROVINCE.md:15` transcribes it as `b1-39ebd2`.

## New row «port defaults are not consumer fallbacks»

- **`8080` is never llama.cpp's listen default at b12177** (T01, `SKILL.md:1882`, `9931`). The `8080`
  strings a reader will meet outside kama are (a) consumer fallbacks — `kama SKILL.md:103`
  (`~/.local/bin/omp` builtin `llama-cpp` default `http://127.0.0.1:8080`), `kagi-shokunin/
  corpus/knowledge/credential-isolation.md:34-35`, `janitor-env-contract.md:55`; (b) historical unit
  argv — `kama SKILL.md:86-88` (`--port 8080` on the predecessor unit, Jitsi taking 8080 on
  2026-09-15); (c) an *allowed origin*, not a listen port — `kengaku-shokunin/corpus/evidence/
  round10-fleet/r10-scout-endpoint.md:33` (`--cors-origins http://127.0.0.1:8080` beside
  `--port 34113`, already warned of at `cross-lane-scope.md` §Consumer ownership).
  Scan result: no sibling states a default port `8080` for any llama.cpp build.

## New row «stale sibling endpoint rows are not current state»

- **`34113` is dead; only the `:1234` router answered on 2026-11-04.** `kagi-shokunin/PROVINCE.md:63`
  and `SKILL.md:43` still present `34113` as "live llama-server" from a 2026-09-28 observation;
  `kengaku-shokunin/corpus/evidence/round76/c1-after.txt:5-6` records `SURFACE 3 absent
  http://127.0.0.1:34113 (http=000)` and `SURFACE 4 absent http://127.0.0.1:45669 (http=000)`, and
  kengaku's `PROVINCE.md:15` dates that resolver pass 2026-11-04. Cite kagi's row as the 2026-09-28 drift record
  (which it is), never as present health.

## New row «no sibling instrument normalizes served ids per-id»

- **C1's one-pass awk has no sibling prior art and no sibling to regress.** A fleet scan for
  `normalize_id|model_matches|router_refine` returns no match outside kama; `paste -sd` appears only as
  a CSV-join idiom for unrelated comparisons (`chousa-shokunin/tools/research-gate.sh:7054`,
  `kagi-shokunin/corpus/scope-gate.sh:609`, `souji-shokunin/tools/impl-40.sh:132`,
  `revenger-shokunin/reports/round-79/selftest_probe.sh:35`). Adjacency claim available to round 91:
  first fleet probe to grade a served list in one linear pass — a *claim*, not a shared instrument.

## Held-out fixture handed to the C1 held-out seats (not a predicate change)

- **A real served id with a slash and a non-`.gguf` suffix.** `kengaku-shokunin/corpus/evidence/
  round51/surfaces/endpoints.txt:12` lists `LiquidAI/LFM3-1.7B-GGUF:Q8_0` beside four plain ids on the
  same router. Under `normalize_id` this becomes `LFM3-1.7B-GGUF:Q8_0` (last `/` dropped, nothing
  stripped); an exact-match implementation would keep the full string. Kama's C1 cells exercise `a/`
  pairs (T5) and `/models/sub/good.gguf` (P2) but never a `/` id whose tail is not a filename, so this
  shape is a wave-only held-out cell, never a change to the frozen 12.
