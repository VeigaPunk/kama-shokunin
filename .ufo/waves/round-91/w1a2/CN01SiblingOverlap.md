# CN01SiblingOverlap — sibling overlap scan (kama round 91, wave w1a2)

## Scope
Read-only scan of all 20 sibling lanes under `/home/vgpnk/Projects/shokunin/*-shokunin` (kama excluded)
for knowledge/SKILL content on serving-engine timeouts, limits and ports (llama.cpp `--timeout`,
`--port` 8080/9931; Ollama `OLLAMA_KEEP_ALIVE`/`OLLAMA_LOAD_TIMEOUT`/11434/parallel/queue; vLLM
`VLLM_ENGINE_READY_TIMEOUT_S`/keep-alive) and for probes iterating served ids, against kama
`SKILL.md:1882-1895`, `corpus/SOURCES.md:347-350`, `PROVINCE.md`, `serving-thresholds.md`. No lane file
edited, no network, no endpoint contacted, no time measured (`uptime` → 11.80 3.79 1.94).

## Commands and outputs (exit codes)
1. grep tool, `OLLAMA_[A-Z_]+|VLLM_[A-Z_]+|ollama serve|ollama run`, 20 sibling dirs, exclusions
   `!**/.ufo/** !**/corpus/live/** !**/scratch/** !**/sandboxes/** !**/*.t{s,v} !**/*.json{,l} !**/*.out`
   → exit 0; only substantive hit kengaku `eval-prior-art-calibration.md:23` (`VLLM_BATCH_INVARIANT`).
2. Same paths, `9931|OLLAMA_KEEP_ALIVE|OLLAMA_LOAD_TIMEOUT|VLLM_ENGINE_READY_TIMEOUT_S|VLLM_HTTP_TIMEOUT_KEEP_ALIVE|sse-ping-interval|cache-ram|sleep-idle-seconds|models-max|keep_alive`
   → exit 0; every hit a digit substring of a hash/id (`v17_fullpos_9931`) except `--models-max 2` in
   kengaku `endpoints.txt:14`. **No sibling holds any T-row value as knowledge.**
3. Same paths, `(?i)\bollama\b` → exit 0; all hits are kake's refusal of an Ollama row as kama's
   province (F4), none a default value. `-np 1|--parallel|n_parallel|parallel sequence` → exit 0,
   kengaku only (F3).
4. Same paths, `default.{0,40}8080|8080.{0,40}default|default port` → exit 0; hits are Unreal MCP `8000`,
   Render `10000`, an RFC-9110 quote, vendored `bottle.py:3816` — **no llama.cpp 8080 default** (F1).
   `keep-alive|keepalive|keep_alive|engine ready|engine_ready|load timeout|loadTimeout|idle timeout`
   → exit 0; all hits GStreamer `pipewiresrc` keepalive (audio r91), HTTP `Keep-Alive` (kake),
   kotoba's "integrity load timeout" — no serving-engine keep-alive/timeout knowledge.
5. Same paths, `normalize_id|model_matches|router_refine|paste -sd` → exit 0; no `normalize_id` outside
   kama; `paste -sd` only as a CSV-join idiom (F7).
6. bash: `grep -n 'flag authority is kama' …/kengaku-shokunin/PROVINCE.md` → exit 0, :15;
   `grep -n 'flag-change authority' …` → exit 0, :47,:74,:158; `grep -n 'SURFACE [34]' …/round76/c1-after.txt`
   → exit 0, :5-6; `grep -n build_info …/round51/surfaces/endpoints.txt` → exit 0, :15 `b1-39febd2`;
   `grep -n 'Jitsi\|34113' …/kagi-shokunin/SKILL.md` → exit 0, :43; `grep -n 34113 …/kagi-shokunin/PROVINCE.md` → exit 0, :63.
7. bash: `grep -n '^| T0[1-9] \|^| T1[0-4] ' SKILL.md` → exit 0, rows 1882-1895; `sed -n 45,49p PROVINCE.md`
   → exit 0, hard write boundary at :46-47.

## Findings

**F1 — NOTE (negative; answers the assigned contradiction question). No sibling states a default port
8080 for any llama.cpp build, and none holds a b12177-era pin.** kagi's 8080 is Jitsi
(`kagi-shokunin/SKILL.md:43`, `PROVINCE.md:63`); kengaku's units pass `--port` explicitly
(`kengaku/…/round51/surfaces/endpoints.txt:13-14`); kama records `--port 8080` on an archived unit
(`SKILL.md:86-88`). T01 (`SKILL.md:1882`) is uncontested. The 8080 strings a reader meets are consumer
fallbacks: `kama SKILL.md:103`, `kagi/corpus/knowledge/credential-isolation.md:34-35`, `janitor-env-contract.md:55`.

**F2 — DEFECT (sibling-owned; do not adopt). Kengaku assigns kama a write authority kama disclaims.**
`kengaku/PROVINCE.md:15` "flag authority is kama's (serving plane)" against the same file at `:47-48`
("flag-change authority … stays unowned"), `:74` ("remains unowned"), `:158` ("unowned/integrator").
Kama's side is fixed: T04 `SKILL.md:1885` ("kama reports it and never tunes it (operator-owned)"), T07
`:1888` ("scheduling is out of province"), T11 `:1892` ("do not tune it"),
`serving-thresholds.md` §Limits, `PROVINCE.md:46-47` ("kama never writes to `~/.config`, `~/.omp`, or
systemd units"). Adopting the sentence into `cross-lane-scope.md` would absorb an authority, not gain
adjacency. Handoff H1.

**F3 — NOTE (corroboration, pin caveat). Kengaku sets `--parallel 2` and names `-np 1` as its
determinism control — it tunes the knob T07 only reads.** `PROVINCE.md:14`,
`corpus/knowledge/eval-prior-art-calibration.md:23`, `r11-prior-art-prereg.md:344` (`-np 1`, fixed
`-b`/`-ub`). No contradiction with T07's default `1`; agreement is on the rule (value read from argv).
Its pinned build there is `0.3.0-dev (build 1, commit d7bd3bf)`
(`corpus/evidence/round10-fleet/r10-scout-endpoint.md:36`), **not** b12177 — not citable against S593.

**F4 — NOTE (adjacency credit). Kake refuses the Ollama docs as kama's province, naming S009-S011**
(`kake/PROVINCE.md:354-356`, `LOG.md:1966`, `corpus/lessons/round-57-verifier-spotcheck.md:88`). Its
round-50 verifier read the live `openapi.yaml` and found `servers: url http://localhost:11434`
(`round-50-verifier-spotcheck.md:192`) — agrees with T08's value, but the ref was `main` (moving), so
kama cannot cite it (B4/B6); S594 stays the only binder.

**F5 — NOTE (T06 boundary, live counterexample). The host router halves T06's default:** 5 ids listed
on `:1234` while argv carries `--models-max 2`
(`kengaku/corpus/evidence/round51/surfaces/endpoints.txt:12,14`). T06 ("at most 4 … by default",
`SKILL.md:1887`) holds as a b12177 default and §Limits already discloses argv overrides — no row
change; but applying "more than 4" to `:1234` is wrong by 2×. Handoff H2.

**F6 — NOTE (T02 corroboration by override).** A sibling's older unit ran `--timeout 900` beside
`--port 34113` and `--cors-origins http://127.0.0.1:8080`
(`kengaku/corpus/evidence/round10-fleet/r10-scout-endpoint.md:33`) — the shape T02 warns about (3600 s
is a default, argv decides) and the CORS-origin confusion `cross-lane-scope.md` already records.

**F7 — NOTE (C1 has no sibling prior art, no sibling to regress).** No sibling instrument normalizes a
served id; `paste -sd` is only a label-join (`chousa/tools/research-gate.sh:7054`,
`kagi/corpus/scope-gate.sh:609`, `souji/tools/impl-40.sh:132`). M's one-pass awk
(`tools/kama-probe.sh:445-470`; `paste -sd,` at `:933-935`) is fleet-first — repertoire, not standard.

**F8 — DEFECT (minor, sibling prose vs its own bytes).** `kengaku/PROVINCE.md:15` transcribes the
router build `b1-39ebd2`; its capture says `build_info=b1-39febd2` (`endpoints.txt:15`). Cite the
capture (H6).

**F9 — NOTE (stale sibling health row; drift corroboration for T01's decision cell).** kagi still
presents `34113` as "live llama-server" (`PROVINCE.md:63`, `SKILL.md:43`, observation 2026-09-28);
`kengaku/corpus/evidence/round76/c1-after.txt:5-6` records `:34113 (http=000)` and `:45669 (http=000)`,
and `kengaku/PROVINCE.md:15` dates that resolver pass 2026-11-04 with only `:1234` answering — a `DEAD`
grade follows the unit's port, not the model.

**F10 — NOTE (held-out shape for C1, wave-only).** `endpoints.txt:12` lists
`LiquidAI/LFM3-1.7B-GGUF:Q8_0` among four plain ids: a real served id with a `/` and a non-filename
tail. `normalize_id` yields `LFM3-1.7B-GGUF:Q8_0`; the exact-match forgery keeps the whole string.
The frozen 12 cover `a/` pairs (T5) and `/models/sub/good.gguf` (P2), not this shape — held-out only.

## Contested scope (who owns tuning)
Operator owns the unit and its flags; kama reads defaults at a pin and reports argv overrides
(`PROVINCE.md:46-47`; T04/T07/T11/T12 decision cells). Kengaku owns interpretation and says in three
places that flag-change authority is unowned/integrator, but in one place hands it to kama (F2); kagi
owns credentials/request hygiene and keeps 8080 as a consumer-declaration fact. No lane claims a right
to tune a value kama reports.

## Deliverables (in `out/CN01SiblingOverlap/`)
- `cross-lane-scope-handoff.md` — seven copy-pasteable handoffs (H1 flag authority, H2 pin-vs-override
  incl. `--models-max 2`, H3 port defaults are not consumer fallbacks, H4 stale sibling rows, H5 no
  per-id normalization in the fleet, H6 build-string citation, H7 held-out id shape) with path:line evidence.

## Proposed move (one, bounded)
Add four one-line rules to `corpus/knowledge/cross-lane-scope.md`: flag authority stays with the
operator (refusing kengaku's sentence by name); a pin's default is never a host setting (both live
overrides named); 8080 is not llama.cpp's b12177 default (consumer fallbacks named); no sibling
instrument normalizes served ids. Axis: adjacency 7 improves by naming three sibling boundaries with
dated evidence; the other five axes are untouched — no counter, frozen predicate, SKILL row or source
row changes, so C1/C2 verify with this unlanded. Risk: two named sentences are sibling-owned text (F2,
F8) kama cannot edit; recording them as observations is the write-boundary limit. Verification:
re-`grep -n` each cited path:line before integration; the rules make no counted claim.

VERDICT: holds — no sibling contradicts T01-T14 or S592-S595; kengaku's flag-authority sentence is recorded as a split, not adopted, and adjacency gains four evidence-backed boundary lines.
