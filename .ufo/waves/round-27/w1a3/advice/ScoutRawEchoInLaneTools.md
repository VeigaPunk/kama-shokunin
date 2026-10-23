VERDICT: partial — KQ37's raw-bytes reject flags only round-26 `count-c1.py:384`; the frozen round-27 echo walk is decoded, and no `tools/*.py`, `count-c2`, or other gate repeats a request-echo test.

Tip `324d5d62e61276af312c8eb42f678004aec245d1` (`git rev-parse HEAD`, exit 0). `git status --porcelain` on the four files below was empty. No installs. No server. `count-c1.py` `main()` was not run.

## Census

Walked 9 `tools/*.py`, 15 `round-2*/count-*.py` (12 `count-c2*`, `count-gate-mutations.py`, both `count-c1.py`, the fake-server mutant), and 20 `round-2*/*gate*.py`, plus the receipt gate `tests/llamacpp-live/check-receipt.py`. Pattern: `echo|req_bytes|request_surfaces|json_strings|sig not in`. Scan: `/fast/scratch/hyaku/kama-r27c/ScoutRawEchoInLaneTools/scan1.txt`.

`tools/*.py`: no test that a string was echoed or occurs in request bytes. `kama-probe.sh:466` is the shell builtin `echo`, not a test. All 12 `count-c2*` files and the round-2* gate scripts: no such test (the "in body" hits in `m2-no-perstore-gate.py` and `report-landing-audit.py:1138` are the phrase "no source URL in body").

## Table

| path:line | test | raw / decoded | KQ37 flag |
|---|---|---|---|
| `.ufo/waves/round-26/count-c1.py:371-374` and `:384` | `e_not_echoed`: `sig not in req_bytes`. `req_bytes` joins `json.dumps` of the trigger (includes `request`), args, path, `json.dumps(headers)`, and `body` if it is a `str` else `json.dumps(body)` (default `ensure_ascii=True`). Exact substring. `squash` (`:257-258`, no casefold) is applied only to the baseline (`:385-386`), not to the request. | **raw.** A string body is not parsed. Not a walk of decoded keys/values. Not case-folded. | **yes.** This is the reject "echo test reads raw request bytes only". |
| `.ufo/waves/round-27/count-c1.py:347-372` used at `:586` | `f:in-request`: `occurs(sig, s)` for `s` in `request_surfaces`. `occurs` (`:347-348`) is casefold or whitespace-squash. Surfaces: path, `json_strings` (str values and dict keys, any dict/list depth), `json.dumps(body)`, `json.dumps(body, ensure_ascii=False)`. | **decoded**, when `body` is a dict or list. A **string body is not parsed**: `json_strings` appends it (`:353-354`) and `json.dumps` only re-escapes it. Non-string scalars are not added as values; both dumps still contain their JSON text. | **no** on the raw-bytes sentence. The credited path is the decoded walk. See the string-body gap below. |
| `.ufo/waves/round-27/controls/KamaR27CtlNoReader/mutant/count-c1.MUTANT-fake-server.py:208-233` used at `:412-413` | Same `occurs` / `json_strings` / `request_surfaces` / `f:in-request` as the frozen counter. | **decoded**, same string-body limit. | **no** for the echo test. The same file drops `h:same-message-frame` (clash chain `:517-526` has no frame remainder). That is KQ37's other reject (one frame, several rows), not an echo test. |
| `tests/llamacpp-live/check-receipt.py:566-569` and `:2313-2316` | Gate refuses a `child_env_keys` element containing `=` without interpolating it (`:569`). Selftest fails if `env_secret` occurs in gate stdout or stderr (`:2313-2316`). | Neither. Diagnostic text, not request bytes. | **no.** KQ37's subject is a counter that credits a live error signature. |

Not request-echo tests, not flagged: round-26 `:365` (`sig` in pinned source bytes), `:383` (`sig` in the response channel), `:392-394` (signature distinctness, not a frame cut); round-27 `:684` (`occurs` on the control **response** body) and `:707-709` (`h:same-message-frame`, which implements KQ37's frame limb).

## Shortcut check (not `main()`)

Command (exit 0): load `shortcut.registry.json` (12 rows) and apply the round-26 join (`:366-374`, `:384`) and the round-27 `occurs`/`request_surfaces` extracted from the frozen file by AST (functions only).

Each body is a `str` of JSON text whose `response_format.type` starts with a `\u00XX` escape. `json.loads(body)["response_format"]["type"] == signature` on 12/12.

| check | result |
|---|---|
| round-26 `sig not in req_bytes` (would pass the echo clause) | 12/12 |
| round-27 `request_surfaces` on that string body | flags 0/12 |
| round-27 `request_surfaces` after `json.loads(body)` | flags 12/12 |

Example `X26-01` body prefix: `{"messages":[...],"response_format":{"type":"\u005fNSGetExecutablePath failed after buffer resize"}}`. The signature is that text with the escape decoded to `_`.

[INFERENCE] A shortcut row shaped like those 12 is not credited by the frozen counter, but not because `f:in-request` fires. `static_checks` rejects a non-dict/list body as `e:bad-request` (`count-c1.py:577-581`) and the echo walk never parses the string. KQ37's named raw-bytes sentence does not describe `:586`. It does describe round-26 `:384`.

## Unresolved

Whether a reviewer treats `e:bad-request` as enough to satisfy KQ37 when the echo walk itself misses an unparsed string body. Not scored here. C1 stays withdrawn; this is not a count.
