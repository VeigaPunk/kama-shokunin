VERDICT: partial — `corpus/knowledge/endpoint-identity.md` §Correction — round 16 (lines 182-215): every behavioural claim matches the landed probe, but the section's own probe insertion leaves the rule table's line-19 anchor stale (`:516` now points at the HTML sniff; `schema-unrecognized` moved to 559-560) with no appended anchor note, and two absolute-word claims are wider than the pinned code. The append-only requirement holds.

# ReviewEndpointIdentityCorrection — round-16 correction vs rule table and landed probe

Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`, HEAD `b8e485cc6b201c8e4604a20808e58babbfe08e34` (`b8e485c`), base `20e392e`. Read-only against the lane; only this report and `/tmp/kama-r16-ReviewEndpointIdentityCorrection/` (removed) were written. No subagents. No `measure.py` (forbidden). No llama-server started; no 8080/34113 bind or probe.

## Axes named

- **A1 behavioural fidelity** — does every sentence of the round-16 correction describe `tools/kama-probe.sh` as landed (matcher exactness, precedence, exits, python3 fallback)?
- **A2 table coherence** — do the correction's line citations (3, 17, 161, 163) and the rule table's own anchors (lines 9-20) remain true of the current file after this commit's probe diff?
- **A3 append-only** — is the doc change pure addition, and does it preserve prior corrections' line numbering?
- **A4 provenance** — do the pinned sources and receipts named by the correction exist and match their claimed digests?

## What I ran (cwd = lane root)

| # | Command | Exit | Result excerpt |
|---|---|---|---|
| 1 | `python3 tests/probe-verdicts/check.py` (exact lane-gate invocation named by the correction) | 0 | `tests=72 passes=72 failures=0` |
| 2 | `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json` | 0 | `"tests": 72, "passes": 72, "failures": 0`, `probe_sha256 6edd3c4c…fa50` (= `sha256sum tools/kama-probe.sh`) |
| 3 | `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` | **1** | `tests=72 passes=55 failures=17`; all 17 failures are the 17 rows whose `expected.verdict` is `MODEL_LOADING` |
| 4 | `sha256sum .ufo/waves/round-16/frozen/kama-probe-before.sh`; `git hash-object` on it; `git show b8e485c^:tools/kama-probe.sh \| sha256sum` | 0 | all three `93ee4302…cd64`; blob `447e29b3…` = manifest `source_blob` |
| 5 | Python census of `tests/probe-verdicts/*.json` | 0 | 9 files, 72 rows, 17 `MODEL_LOADING`, 8 `MODEL_OK`, 37 `FOREIGN_SERVICE`, 5 `UNAUTHORIZED_SERVICE`, 3 `MODEL_MISMATCH`, 1 `DEAD`, 1 `NOT_HTTP` |
| 6 | Local stub on kernel-chosen free port 42337 serving the exact envelope plus an extra top-level key; `bash tools/kama-probe.sh check --port 42337 --expect '*' --timeout 2 --connect-timeout 1` | **2** | `MODEL_LOADING / llamacpp-loading`, `drift=1 exit=2` (extra top-level key allowed) |
| 7 | same stub; same command with `PATH=<tmp bin without python3>` and `/usr/bin/bash` | **2** | `FOREIGN_SERVICE / non-2xx-non-model-http`; stderr `python3 not found — using grep fallbacks…` |
| 8 | `git diff --numstat b8e485c^ b8e485c -- corpus/knowledge/endpoint-identity.md`; `git status --porcelain -- corpus/knowledge/endpoint-identity.md tools/kama-probe.sh` | 0 | `35 0` (all additions); status empty |
| 9 | `nl -ba corpus/knowledge/endpoint-identity.md \| sed -n '3p;17p;19p;126p;161p;163p;182,215p'` | 0 | quotes in §Findings |
| 10 | `git show b8e485c^:tools/kama-probe.sh \| nl -ba \| sed -n '516p'` vs `nl -ba tools/kama-probe.sh \| sed -n '516p;559,560p'` | 0 | pre 516 `schema-unrecognized`; current 516 `'<html'*\|'<!doctype'*'html'*) ishtml=1 ;;`; current 559-560 `schema-unrecognized` / `non-model-2xx` |
| 11 | `nl -ba tools/kama-probe.sh \| sed -n '68,69p;114,115p;286,309p;377,392p;454p;503,508p;549,554p;839,853p'` | 0 | current anchors used below |
| 12 | `nl -ba` pinned `server-http.cpp:307-328,347-359,493,541`, `server.cpp:440-462,493-515`, `README.md:479-490,1258` | 0 | quotes in §Findings |
| 13 | `sha256sum` pinned `README.md server-http.cpp server.cpp server-common.cpp server-common.h` | 0 | `714c067b…`, `24ede172…`, `21439622…`, `b4f4aae7…`, `ee401cf8…` — README/server-http/server.cpp match S035/S036/S037 |
| 14 | `pgrep -x llama-server \| wc -l`; `pgrep -f stub503.py \| wc -l` | 1 / 1 | `0` and `0` — nothing of mine left running |

## Confirmations (A1 and A4)

| Correction claim (doc line) | Check | Status |
|---|---|---|
| Line 3 "The verdict vocabulary is fixed" and line 163 "verdict vocabulary are unchanged" are superseded; seven verdicts now (188-190) | `VOCAB` `tools/kama-probe.sh:62` has all seven; both doc quotes are exact at 3/163; run 1 | **confirm** |
| Rule 5 at line 17 is "narrowed, not deleted" (190-192) | line 17 text exact; exact envelope is the only non-2xx carve-out (runs 2, 3) | **confirm** |
| 503 + exact `error` triple → `MODEL_LOADING` / `llamacpp-loading` (192-196) | `tools/kama-probe.sh:503-508`; run 6; rows `canonical-alias`, `wildcard-expect`, `dash-expect`, `no-server-header`, `plain-json-content-type`, `key-order-permuted`, `pretty-printed-body`, `Padding64KiB`, `ExtraFieldsAllowed` | **confirm** |
| exact match: `message`/`type` exact, integer `code` 503 (193-195) | `body_is_llamacpp_loading` `:428-447`; rows `code-float-503.0`, `code-boolean-true`, `CodeAsString`, `code-string`, `MissingCode`, `loading-message-wrong-type` all fall through | **confirm** |
| extra top-level keys allowed (implied by "whose `error` object has…") | run 6; row `ExtraFieldsAllowed` → `MODEL_LOADING` | **confirm** |
| "runs after rule 3 (401/403) and before rule 4 (HTML)" (196) | `:494-501` then `:503-508` then `:510-518`/`:549-554`; rows `401/403-carrying-loading-envelope` → `UNAUTHORIZED_SERVICE`, `exact-envelope-labelled-html` → `MODEL_LOADING` | **confirm** |
| "(drift, exit 2)" (195) | `:848-849` (`MODEL_OK` else drift), `:881`, `:887`; runs 6, 7 both exit 2 | **confirm** |
| "Without python3 the body keeps its old `FOREIGN_SERVICE` verdict" (207) | `:429` fail-closed; run 7 | **confirm** |
| no-slot and router-stream `unavailable_error` bodies stay on rule 5 (205-207) | rows `no-slot-available`, `router-stream-owner-loading` → `FOREIGN_SERVICE / non-2xx-non-model-http`; `:556-566` | **confirm** |
| "starts its listener before `load_model` … `is_ready` only afterwards (S037)" (199-200) | pinned `server.cpp:493-515`: start, `load_model`, then `is_ready.store(true)` at 515 | **confirm** |
| "pre-routing middleware … before the API-key check (S036)" (200-202) | pinned `server-http.cpp:354-359`: state gate at 354, API-key check at 357 | **confirm** |
| line 161/README:1258 `meta: null` "while the model is still loading" (209-213) | doc line 161 and `README.md:1258` exact | **confirm** |
| matrix receipts exist and say 55/17 → 72/0 (185) | `.ufo/waves/round-16/measure-stdout.txt`; my runs 1-3 independently reproduce both arms | **confirm** |

The frozen control is honest: the frozen file is byte-identical to the pre-image (`93ee4302…`, blob `447e29b3…`), and its 17 failures are exactly the 17 `MODEL_LOADING` expectations (`measure-stdout.txt`: `directional: loading_expectations=17 before_failed=17 changed=17 equal=True`).

## Findings

### F1 — MEDIUM — the commit's probe insertion makes the rule table's line-19 anchor wrong, and the correction appends no anchor note

`corpus/knowledge/endpoint-identity.md:19` (rule 7) cites `tools/kama-probe.sh:516` for the `schema-unrecognized` reason. That was correct before this commit:

- pre-image `516`: `*json*) C_REASON=schema-unrecognized ;;`
- current `516`: `'<html'*|'<!doctype'*'html'*) ishtml=1 ;;`
- current `559`: `*json*) C_REASON=schema-unrecognized ;;`

The round-16 probe diff inserted 29 lines at `:420-448` and 7 lines at `:503-508` (net +44), so every anchor in this doc that pointed at the pre-image now points at shifted text (+7 before the helper insertion, +36/+43/+44 after it), including the "current anchors" that round 10 appended to repair the older drift:

| doc anchor | round-10 "current" | at HEAD |
|---|---|---|
| line 19 `:516` (rule 7) | correct then | **now HTML sniff; reason at 559-560** |
| A01/A05 `61-62,107-108` | correct then | `68-69,114-115` (+7) |
| A04/A07 `34-39,370-385` | correct then | `41-46,377-392` (+7) |
| A02 `418` | correct then | `454` (+36) |
| A05 `279-302` | correct then | `286-309` (+7) |
| A02 `795-803` | correct then | `839-853` (+44) |

Round 10 established the convention of appending an anchor-correction paragraph after a probe change (A01-A05). This commit changes the probe more substantially and appends none; the correction names only doc lines 3/17/161/163 and no `tools/kama-probe.sh` line. A reader chasing rule 7's `:516` now lands on the HTML branch — a real wrong turn, not a pointer to equivalent code.

**Smallest safe fix (append-only):** append one anchor block under §Correction listing `:41-46,68-69,114-115,286-309,377-392,454,559-560,839-853` as the current anchors, explicitly superseding A01/A02/A04/A05/A07's "current anchor" clauses, and state the rule-7 reason is now at 559-560.

### F2 — LOW — "Every other non-2xx non-model response keeps rule 5" is false for HTML, which keeps rule 4

Doc line 197. A 503 with `Content-Type: text/html` and no exact envelope is a non-2xx, non-model response, and it takes rule 4, not rule 5: `tools/kama-probe.sh:549-554` (`C_REASON=html-non-model`), confirmed by matrix row `Overbroad503.nginx-html-503` → `FOREIGN_SERVICE / html-non-model`. The verdict is `FOREIGN_SERVICE` either way, so only the row attribution is wrong. The correction's preceding sentence ("before rule 4") already implies the precedence; the "keeps rule 5" wording contradicts it.

### F3 — LOW — "every non-frontend path" omits the OPTIONS short-circuit

Doc lines 200-202 repeat S036's wording. The pinned handler returns before `middleware_server_state` for CORS preflight:

- `server-http.cpp:347-353`: `if (req.method == "OPTIONS") { … res.set_content("", "text/html"); return … Handled; }`

So `OPTIONS /v1/models` during loading answers 200 `text/html`, not the 503 envelope. Non-material to the probe (it sends GET only) and to the `MODEL_LOADING` decision; it is a literal overstatement in a sentence that otherwise explains the gate correctly.

### F4 — INFO — "Router mode never emits the envelope" has a narrow startup window [INFERENCE]

Doc line 205. Router mode calls `ctx_http.start()` and only then `ctx_http.is_ready.store(true)` (`server.cpp:455-460`), while `start()` spawns listener threads and calls `srv->wait_until_ready()` before returning (`server-http.cpp:531-536`). A request accepted in the gap between "listening" and the atomic store can still hit the 503 branch. Steady-state claim is correct; "never" is not guaranteed by the code. Same wording issue as `ReviewProbeDiff.md` F2 for the probe header — this is the doc inheriting it. I did not reproduce the race.

### F5 — INFO — `server.cpp` has a pinned copy and matching digest but no `pins.json` entry

`.ufo/waves/round-16/sources/pins.json` lists only README/server-common.cpp/server-common.h/server-http.cpp. The correction cites S037 (`server.cpp:493-515`); the on-disk file sha256 is `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4`, exactly S037's claimed digest. No false claim, but the pin manifest cannot prove the copy's provenance on its own.

### Related gap owned by another seat (not counted here)

`corpus/knowledge/endpoint-identity.md:126` still says "A live non-`2xx` non-HTML response is a foreign service", which is the rule-5 overreach restated and is not named by the correction (which names 3/17/161/163). `CriticTrendVerdicts.md` Q3 already reports this; listing it here only to confirm the correction's supersession is incomplete within its own file.

## Append-only audit — CONFIRM

- `git diff --numstat b8e485c^ b8e485c -- corpus/knowledge/endpoint-identity.md` → `35 0`; the single hunk is `@@ -178,3 +178,38 @@` and contains only `+` lines.
- At commit-check time (before the concurrent edits noted below) `git status --porcelain` for the doc and probe was empty; HEAD is the lane commit.
- The added block starts at line 181 (section heading at 182), so the correction's own citations (3, 17, 161, 163) and all prior correction text keep their line numbers.

## Concurrent working-tree note (not my edits)

This review targets the landed commit `b8e485c`. While I was finishing, the working tree gained **uncommitted** edits by another seat (I did not make or touch them; `git status` now shows `M tools/kama-probe.sh` and `M corpus/knowledge/endpoint-identity.md`):

- probe header: "(Drift (exit 2)" is rescoped to `check`/`snapshot`, and "Router mode never emits it" becomes "The router's own /v1/models never answers with it" — this addresses the probe-header half of my F4 and sibling `ReviewProbeDiff.md` F1/F2;
- doc line 126: the anti-pattern restatement is now named in the superseded set — this closes the "related gap" I flagged as owned by `CriticTrendVerdicts.md` Q3.

Neither edit fixes F1 (`tools/kama-probe.sh:516` rule-7 anchor is still stale), F2 (doc "Every other non-2xx non-model response keeps rule 5" is unchanged), or F3 (OPTIONS wording is unchanged). The doc edit adds one line inside the round-16 section, so the doc line numbers I cite for the body (197, 200-202, 205) are 198, 201-203, 206 in that dirty tree; everything at or below line 189 is unchanged.

## Limitations

- No LSP device/server is mounted in this seat, so caller/definition/diagnostic checks were impossible; anchors were verified with `nl -ba` plus `git show <base>:<path>` only. No semantic index was available.
- I did not re-run `tools/kama-llamacpp-live.py` or the live receipt; the `MODEL_LOADING` window's reachability is taken from the pinned code plus the L1 live receipt, not re-observed here.
- The F4 router race is inferred from code order; it was not reproduced (needs a timed request against a launching router).
- `listeners`/`consumers` exit-0-on-`MODEL_LOADING` was not exercised (a full `listeners` scan would probe 8080/34113); the code paths are `:744`/`:817` and are unchanged by this doc.
- I did not inspect the full new knowledge entry or other appended docs; this report is scoped to `endpoint-identity.md` §Correction.

## Installs / teardown

- No tools installed or upgraded (no pacman/uv/npx/curl-to-shell).
- Stub server was a `/usr/bin/python3 http.server` on a kernel-chosen free port (42337); terminated (`returncode -15`), `pgrep -f stub503.py` → 0.
- `pgrep -x llama-server` → 0. Scratch `/tmp/kama-r16-ReviewEndpointIdentityCorrection/` removed.
