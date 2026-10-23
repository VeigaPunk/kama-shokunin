VERDICT: partial — the frozen A3 clause (f) refuses 0/12 of the committed round-26 shortcut rows, all 12 of which the round-26 raw-bytes test let through (it flagged 0/12 echoes while the receipt recorded `counted=12`); the full A3 counter still refuses all 12, but only through the body-type schema check (e:bad-request), and clause (f) refuses all 12 once the stored string body is JSON-decoded.

# ExecOfflineEchoReplay — offline replay of the 12 round-26 shortcut rows

Seat: KamaR27A3.ExecOfflineEchoReplay (leaf). Scope: X1 exploratory calibration
evidence only. No server, no port, no subprocess, no `main()`, no network. All
measurements are function-level against the frozen bytes.

## Inputs (sha256, bytes)

| input | path | sha256 |
|---|---|---|
| frozen A3 counter | `.ufo/waves/round-27/count-c1.py` (copy: `/fast/scratch/hyaku/kama-r27c/ExecOfflineEchoReplay/count-c1.py`) | `49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765` |
| round-26 counter | `git -C <lane> show eb09e742:.ufo/waves/round-26/count-c1.py` → `/fast/scratch/hyaku/kama-r27c/ExecOfflineEchoReplay/r26-count-c1.py` | `6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588` |
| shortcut registry | `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json` | `1b78c8aa0423151b9d84f6ad3cef35de7e5260e5ec869fea764ba5dbcc691b91` |
| shortcut receipt | `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json` | `6020a2c39cf698860f64216754925ed623c7225c47871a1644e0c8e6d3d7ac19` |

The harness refuses to run (exit 3) if either counter's sha256 differs from the
two values above. Both matched.

## Command and result

```
cd /fast/scratch/hyaku/kama-r27c/ExecOfflineEchoReplay
ulimit -f 1048576
timeout 120 /usr/bin/python3 replay_echo_tests.py \
  --counter count-c1.py \
  --registry <lane>/.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json \
  --receipt  <lane>/.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json \
  --r26-counter r26-count-c1.py \
  --out <lane>/.ufo/waves/round-27/w1a3/out/ExecOfflineEchoReplay/replay.receipt.json
```

Exit code: **0** (`harness.exit.txt` = `EXIT=0`). Scratch copy and the report
copy of the harness are byte-identical (`c37e5b59…f537a2`).

Trimmed stdout (full file: `.ufo/waves/round-27/w1a3/out/ExecOfflineEchoReplay/harness.stdout.txt`):

```
X26-01 r26_flags_echo=false a3_f=false a3_f_if_decoded=true  body=str   e_body_ok=false msg_has_sig=true  frame=aed0b0990b47 sig='_NSGetExecutablePath failed after buff'
…
X26-12 r26_flags_echo=false a3_f=false a3_f_if_decoded=true  body=str   e_body_ok=false msg_has_sig=true  frame=aed0b0990b47 sig='sampling tensor must be contiguous for'
TOTALS r26_flags_echo 0/12 a3_flags_echo 0/12 a3_if_decoded 12/12 a3_schema_e_rejects 12/12 msg_has_sig 12/12 msg_sha_ok 12/12
FRAMES distinct_signature_stripped=1/12 survivors_a3_h=['X26-01']
SELFCHECK r26_recompute_vs_receipt=agree
OUT …/replay.receipt.json
```

## Per-row measurements (all 12)

`r26` = round-26 test says the signature IS in `req_bytes` (an echo seen);
`a3f` = frozen clause (f) as implemented; `dec` = clause (f) after
`json.loads(body)`; `e` = A3 body-type check accepts; `msg` = receipt message
contains the signature. Body type is `str` for every row.

| id | signature | r26 | a3f | dec | e | msg | frame sha256[:12] |
|---|---|---|---|---|---|---|---|
| X26-01 | `_NSGetExecutablePath failed after buffer resize` | false | false | true | false | true | aed0b0990b47 |
| X26-02 | `GetModuleFileNameW failed or path too long` | false | false | true | false | true | aed0b0990b47 |
| X26-03 | `RPC not supported in this build` | false | false | true | false | true | aed0b0990b47 |
| X26-04 | `T must be trivially copyable` | false | false | true | false | true | aed0b0990b47 |
| X26-05 | `yield_to_queue() cannot be nested` | false | false | true | false | true | aed0b0990b47 |
| X26-06 | `update() must be called before to_json()` | false | false | true | false | true | aed0b0990b47 |
| X26-07 | `Invalid task_response_type` | false | false | true | false | true | aed0b0990b47 |
| X26-08 | `unsupported batch.has_embd + spec case` | false | false | true | false | true | aed0b0990b47 |
| X26-09 | `Error: gzip is not supported by this browser` | false | false | true | false | true | aed0b0990b47 |
| X26-10 | `CLIP cannot be used as main model, use it with --mmproj instead` | false | false | true | false | true | aed0b0990b47 |
| X26-11 | `Cannot restore media tokens without an mmproj` | false | false | true | false | true | aed0b0990b47 |
| X26-12 | `sampling tensor must be contiguous for async copy` | false | false | true | false | true | aed0b0990b47 |

Totals: `r26_flags_echo 0/12`, `a3_flags_echo 0/12`,
`a3_f_flags_echo_if_body_json_decoded 12/12`, `a3_schema_e_rejects_body 12/12`,
`receipt_message_contains_signature 12/12`, `receipt_message_sha256_matches 12/12`
(the excerpts are < 400 bytes, so each excerpt is the full channel text and its
sha256 equals the receipt's `observed.channel_sha256`).

The 12 server messages are one frame with the signature substituted
(representative, X26-01):

```
{"error":{"code":400,"message":"response_format type must be one of \"text\" or \"json_object\", but got: _NSGetExecutablePath failed after buffer resize","type":"invalid_request_error"}}
```

## Mechanism (path:line pointers)

1. **Stored body is a JSON *string*, not an object.** Each row's
   `request.body` is a `str` containing the serialized request, with the
   signature's first character written as a JSON `\u00XX` escape — e.g.
   `shortcut.registry.json` X26-01 body:
   `{"messages":[…],"response_format":{"type":"\u005fNSGetExecutablePath failed after buffer resize"}}`.
   `gen_shortcut.py` states the intent: "its first character written as a JSON
   \u00XX escape so the frozen counter's raw-text echo check … does not see it".
2. **Round-26 test** (`r26-count-c1.py:366-374`, `:384`): `body_text` is the
   stored string verbatim (escape intact), `e_not_echoed = sig not in req_bytes`
   → true for all 12, so all 12 were credited (`shortcut.receipt.json`:
   `counted=12`, every row's `checks.e_not_echoed=true`). The harness
   recomputes `e_not_echoed` for all 12 and every value agrees with the receipt
   (`r26_recompute_vs_receipt=agree`).
3. **Round-26 wire path** (`r26-count-c1.py:159`): `data = body.encode()` for a
   string body — the server received the escape and decoded it to `_NSGet…`,
   which is exactly why the echo appears in the 400 message. The counter's echo
   test looked at different bytes than the server saw. This is the shortcut.
4. **Frozen A3 clause (f)** (`count-c1.py:585-587`; helpers `occurs` :347-348,
   `json_strings` :351-362, `request_surfaces` :365-372): for a `str` body,
   `json_strings` yields the raw serialized text as one surface and the two
   `json.dumps` surfaces are string-serializations of that text — no JSON
   parsing of the body occurs. `occurs` never matches `\u005fNSGet…` against
   `_NSGet…`, so clause (f) flags 0/12 (measured; sample X26-01: 4 surfaces,
   0 hits).
5. **A3 body-type check** (`count-c1.py:578-581`): `body` must be `None`,
   `dict` or `list`; a `str` body raises `e:bad-request`, so `main()` excludes
   the row from live runs (`count-c1.py:665`) and the row is not counted. This
   — not clause (f) — is what refuses all 12 today.
6. **Wire mismatch on the A3 side**: A3's `http()` (`count-c1.py:389`) does
   `json.dumps(body).encode()` unconditionally, which for a `str` body would
   send a quoted JSON string literal rather than the raw object; the schema
   check in (5) prevents that path from being reached. [INFERENCE] A row
   storing its body as a `dict` reproduces the original wire bytes under A3 and
   is then caught by (f) 12/12.
7. **Clause (h) one-frame rule** (`count-c1.py:721-725`, exact
   `msg.replace(sig,"\0").lower().strip("\0 ")` comparison): all 12 messages
   reduce to one distinct signature-stripped frame (`aed0b0990b47…`), so the
   frame leg alone would credit at most **1** of the 12 (X26-01, registry
   order; this measurement applies only the frame leg, not the source-line,
   sub/superstring, request or next-action legs).

## Calibration reading for X1

- The round-26 raw-bytes test is defeated by a single JSON escape
  (`\u005f`) in a stored string body: 0/12 echoes seen while the server echoed
  the decoded signature in every one of the 12 messages. The shortcut does not
  depend on any error knowledge beyond `response_format.type` reflection.
- The frozen A3 clause text (`count-c1.py:44-47`: "in any JSON-decoded string
  key or value of the request body") is **not** what the code implements for a
  string body: no decode step exists, so an escaped echo passes (f) 0/12.
  [INFERENCE] A one-line repair inside `request_surfaces` — `if isinstance(body,
  str): body = json.loads(body)` guarded by `try/except json.JSONDecodeError` —
  makes (f) flag all 12 without touching any other clause; the counterfactual
  column measures exactly that post-decode behaviour (12/12).
- The class is nevertheless refused by the counter as a whole today, but by a
  schema gate (`e:bad-request`), not by the echo rule the round claims. A
  shortcut author who stores the body as a dict gets past (e) and is then
  refused by (f); the same author who stores it as a string is refused by (e).
  Both routes refuse, so no credited row leaks [INFERENCE from the two measured
  branches; the live counter was not run].
- One fault, one row: the 12 rows are one message frame; even a repaired (f)
  that let one through would have to answer to (h), which leaves 1 distinct
  frame.

## Not run / unverified

- The live A3 counter was not run (no port block for this seat; `main()` never
  called). Its live `e:not-shown`, (g) control and (h) message legs are
  unverified here; all statements above are static/function-level.
- The (h) measurement covers only the same-message-frame leg.
- `count-c2.py` and any earlier-round witnesses were not touched.

## Constraints observed

- No server started; no socket, no subprocess in the harness; `pgrep -af
  llama-server` showed three pre-existing processes (ports 47636/47637/47644)
  that this seat did not start and did not interact with.
- No git/jj writes. `git show eb09e742:…` (read-only) materialized the
  round-26 counter to scratch.
- Writes only under `/fast/scratch/hyaku/kama-r27c/ExecOfflineEchoReplay/` and
  `.ufo/waves/round-27/w1a3/out/ExecOfflineEchoReplay/` plus this advice file.
  All fixture/log-writing commands ran under `ulimit -f 1048576` and
  `timeout 120`
- No tool installs or updates this seat.
- `/fast`: 219 GB free before writing (largest artifact 16 KB).

## Artifacts

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-27/w1a3/out/ExecOfflineEchoReplay/`

| file | sha256 |
|---|---|
| `harness.py` | `c37e5b59cd23ba8c8d45d7c2afe1215e0735cf346a8faeeee5bcabee1af537a2` |
| `replay.receipt.json` | `e73ec7b69ab4a2f354dea65542d678c43df658da2b6ea4501dc16499d06339bf` |
| `harness.stdout.txt` | `6bf76ac70205620c453933f2486c2f1ea42b7c1fc97a0524cb7a99dd7ddb620e` |
| `harness.exit.txt` | `418a5c17f33c70e99b0cc0a07fce69191489cfedc94164bfa903785777c5bd4b` |

`replay.receipt.json` carries the inputs' sha256/size, the per-row fields
(raw body, req_bytes sha256, both flags, decoded counterfactual, schema flag,
server message and its sha256 equality, frame sha256), totals, frame analysis
and the r26 recompute self-check.

## Risks / blockers

None for this seat. Residual risk for the reviewer: the receipt's per-row
messages are the committed 400-character (untruncated here) excerpts; a full
channel capture beyond 400 bytes would be needed only if a future message
exceeds that bound (all 12 are shorter).
