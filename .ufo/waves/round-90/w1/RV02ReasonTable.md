# RV02ReasonTable — C2 `## Probe reason codes` review (kama round 90, wave 1)

## Scope
All 24 rows of `SKILL.md` `## Probe reason codes` at M2 2ee0b55f4d3fd0cb3157d26b03280c1d21e27b2d: each row's
trigger prose checked against the probe source at M2 (`fetch` :334-370, `router_autoload` :756-775,
`router_refine` :777-820, `classify` :822-948, `model_matches`/`normalize_id` :469-483, `gguf_state` :544+,
`file_state`/`PATH_FLAGS` :532/:693-704) and against the stub its capture cell builds
(`tools/round90-reason-capture.py` `cells()`). Predicate re-run, receipt re-capture + cmp, counter at M2 and
base, freeze-byte check. Kill rules C2-K1/K2/K3 addressed. Lane untouched except my out dir and this report.

## Commands and outputs (exit codes)
- `python3 tools/round90-reason-capture.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 2ee0b55f… --work <scratch> --out <scratch>/r.jsonl` → exit 0, `REASON_CAPTURE cells=24 probe_sha256=c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97 rev=2ee0b55f…`. `cmp <scratch>/r.jsonl .ufo/waves/round-90/measured/reason-cells.jsonl` → identical (exit 0). Receipt reproduces byte-for-byte.
- `python3 tools/round90-reason-rows.py --repo . --rev 2ee0b55f…` → exit 0: `REASON_ROWS population=23 documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1 receipt=current probe_sha256=c197912f…` (predicate met at M2).
- Same at base 99cdb4d6… → exit 1: `documented=0 rows=0 bound=0 missing=23 receipt=absent probe_sha256=c15ffca8…` — byte-identical to frozen control `controls/c2-base.out`.
- `git diff 6f6d7873… -- tools/round90-reason-rows.py | wc -l` → 0 (counter bytes unchanged since freeze F). `… -- tools/round90-reason-capture.py | wc -l` → 272 (receipt producer evolved post-freeze; claims doc designates it post-freeze work, not the counter — no kill).
- `git rev-parse HEAD` → 2ee0b55f…; dirty files are corpus/README.md, corpus/SOURCES.md and untracked w1 artifacts only; `tools/` and `SKILL.md` clean, so worktree reads = M2 bytes.

Kill rules: K1 holds (counter bytes = freeze bytes). K2 holds (no row contradicts its receipt cell: 24/24 reason+verdict match the re-captured receipt; see overclaims — prose-vs-code gaps, none contradicted by the stub each row binds). K3 holds (receipt probe_sha256 = sha256 of `git show M2:tools/kama-probe.sh`; counter prints `receipt=current`).

## Findings — DEFECT (prose should be fixed; row tokens and receipt unaffected)
- D1 DEFECT `SKILL.md:1840` (section intro): "four `MODEL_UNLOADED`/`MODEL_LOADING` reasons come from the router `status` object" — five such rows exist: router-loading, router-downloading (MODEL_LOADING), router-model-missing, router-model-invalid, router-unloaded (MODEL_UNLOADED). Undercounts by one.
- D2 DEFECT row `router-unloaded` (`SKILL.md:1866`): "entry `unloaded` and the router does not autoload (`models_autoload` not true, or `/props` unusable)". `router_autoload` (probe :756-775) returns not-autoload for: fetch rc≠0, body > MAX_BODY (the post-C1 cap, :763), non-JSON, `role`≠"router", `models_autoload` not exactly `true`, python3 missing. `/props` unusable and "router does not autoload" are indistinguishable to the probe; the row asserts a fact it has not established, and the advice "load it with `POST /models/load`" can be wrong for a router that does autoload but whose `/props` was unusable. Honest wording: "the probe could not confirm autoload".
- D3 DEFECT rows `schema-unrecognized` (`:1856`) / `non-model-2xx` (`:1857`): the code's discriminator is the Content-Type header only (`classify` :938-941 `case "$F_CT" in *json*`), not the body format. A 2xx JSON body under a non-JSON Content-Type lands on non-model-2xx; a non-JSON body under a JSON Content-Type lands on schema-unrecognized. Prose says "2xx JSON without a `data` or `models` array" / "2xx with a non-JSON, non-HTML body" — both misdescribe the split (only the HTML sniff reads the body, :929-934).
- D4 DEFECT rows `router-model-missing`/`router-model-invalid` (`:1863-1864`): "an absolute `--model`/`-m` path in `status.args`" — `PATH_FLAGS` (:532) is `-m --model -mm --mmproj -md --model-draft` (:700-704), so a missing/invalid mmproj or draft path also yields these reasons while the row's stated trigger is not true for it. "absolute" is correct (`os.path.isabs` filter, :697). The "500 `failed to load`" sentence is sourced (S583, `corpus/lessons/round-89-verifier-spotcheck.md:108`, `corpus/knowledge/router-unloadable-model.md:22`) — stands.

## Findings — row-level verdicts (24/24)
| reason | verdict | note |
|---|---|---|
| connection-refused | true | rc 7 on literal 127.0.0.1 with `--noproxy '*'`; rc 7 is generically "couldn't connect" (edge: connect-timeout is rc 28, not 7) |
| timeout | true* | rc 28 also fires when a transfer starts but exceeds `--max-time` mid-body; "no answer arrives" names only the silent case. * not contradicted by cell |
| empty-reply | true | rc 52 arm exact |
| connection-reset | true | rc 56 arm exact |
| no-http-response | true | "any other curl failure lands here too" VERIFIED: arms 1\|2\|92 + `*` catch everything except 6/7/28/63/52/56 (:836-869). Lead clause ("bytes arrive") is narrower than the branch — self-corrected by the row's own sentence |
| http-401 | true | 401 decided on status alone; body unjudged |
| http-403 | true | same |
| llamacpp-loading | true | status 503 AND exact envelope incl. int code 503 (:882-888, `body_is_llamacpp_loading`); NOTE: silently requires python3 (without it → non-2xx-non-model-http, fail-closed comment :495-501) |
| expected-wildcard | overclaims (minor) | (a) wildcard also for `--expect ''` and `--expect -` (:901), prose names only `'*'`; (b) "liveness only" — `router_refine` runs on wildcard probes (wild skips id match, :788) and can override MODEL_OK with router-* reasons |
| matched | true | normalization = basename + one trailing `.gguf` exactly (`normalize_id` :468-469); subject to shared router-refine precedence (intro covers it) |
| unresolvable-id | true | rc 2: expected normalizes empty OR no served id survives normalization; covers ids like `.gguf` |
| served-id-mismatch | true | rc 1 exact |
| html-non-model | true* | "at any status" real (html check precedes the non-2xx fallthrough :931-936); edge: a 2xx HTML-sniffed body that also carries a data/models array is classified by the array first |
| schema-unrecognized | overclaims | see D3 |
| non-model-2xx | overclaims | see D3 |
| non-2xx-non-model-http | overclaims (minor) | needs "and not sniffed as HTML" (html-non-model takes non-2xx HTML first); "(here 404 JSON)" is the captured case |
| router-sleeping | true | sleeping wins only when no matching entry is loaded/- (:798, ok gate :795) |
| router-unloaded-autoload | overclaims (minor) | trigger not sufficient: also requires entry not `failed`, entry matching expected (non-wild), and not ALL matching unloaded candidates' files missing/invalid (else router-model-*). Table order mirrors code precedence (ok > sleeping > unloaded-autoload > loading > unloadable > down), so reading rows together resolves it |
| router-loading | true | first matching loading/downloading entry names the reason (:814) |
| router-downloading | true | same path |
| router-model-missing | overclaims | see D4 |
| router-model-invalid | overclaims | see D4; "GGUF loader header check" accurate (gguf_state parses magic/u32/u64 container, Bad → invalid) |
| router-unloaded | overclaims | see D2 — the seat-named case, confirmed |
| body-too-large | true | rc 63 arm (:844-848); FBODY truncated (:347) so "nothing was parsed" exact; wc re-check fallback produces the same rc (prose need not mention it) |

## Findings — section-level
- N1 NOTE: the down branch is an open set the section does not disclose: any unrecognized `status.value` prints `router-<value>` / `router-<value>-failed` (:805-819, e.g. `router-unloaded-failed` for an entry with `failed:true`). Frozen counter docstring explicitly excludes them ("`router-unloaded` is the population's representative of the `down` branch"), so C2 stays green, but the intro "What `tools/kama-probe.sh` prints in the `reason` column" implies a completeness the column does not have. A reader hitting `router-unloaded-failed` finds no row.
- N2 NOTE: `dns-failure` exclusion sentence is TRUE at M2 — `fetch` targets the literal `http://127.0.0.1:$port` (:343) with `--noproxy '*'`; rc 6 unreachable. Verified, not an overclaim.
- N3 NOTE (positive): table row order equals code precedence; "Only `MODEL_OK` rows exit 0" holds in the receipt (4 MODEL_OK cells exit 0, all others exit 2); all 24 verdicts match receipt lines.
- N4 NOTE: no tool installs/updates were needed; nothing installed (tooling rule: nothing to record).

## Deliverables
- Report: `.ufo/waves/round-90/w1/RV02ReasonTable.md` (this file)
- Receipt re-run: `.ufo/waves/round-90/w1/out/RV02ReasonTable/reason-cells-rerun.jsonl` (24 lines, cmp-identical to measured)
- Scratch removed; lane tracked files untouched.

VERDICT: holds — predicate, binding and reproducibility verified end-to-end at M2 with base control reproduced; 4 prose defects (D1-D4) and minor overclaims reported, all fixable as doc-only edits, none contradicting a receipt cell (C2-K2 clean).
