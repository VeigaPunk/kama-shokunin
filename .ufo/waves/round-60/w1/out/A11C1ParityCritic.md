# A11C1ParityCritic — C1-r60 freeze vs counter vs tool (round 60, kama, w1)

Advisory findings only. No lane source edited. Sources read in full: `controls/freeze.txt` (F), `tools/round60-c1-counter.py` (C), `tools/kama-ollama-live.py` (T), `registry/ollama-live-pin.tsv`, committed `live/receipt.json`, `live/serve-lines.txt`, `controls/c1-*.out`.
One live probe run (below, §3); its scratch dir was removed afterwards. Line numbers are file lines.

## 1. Clauses of the freeze sentence the counter does not enforce (F:14-19)

| # | Freeze quote | What C does | Verdict |
|---|---|---|---|
| 1 | F:14-15 "archive sha256 7bedab90...4b6d" and "official Ollama release" | C has no archive constant (C:27-31 hold only VERSION, BIN_SHA, MODEL_SHA). T copies `archive_sha256` into `receipt['pin']` (T:246) and never hashes or compares any archive. `receipt['pin']` is not read anywhere in C. | NOT enforced. "Official" provenance rests on the pin-file comment (pin:2-3) alone. |
| 2 | F:18 "re-derives the binary digest from frozen constants" | C:73 compares the receipt's self-reported `binary_sha256` to `FROZEN_BIN_SHA`. C never hashes a binary. The only use of `REAL_BIN` is to copy it for the patched control (C:184). `running-exe-digest` is accepted from the tool's own `passed` flag (C:81). | Overstated. It compares, it does not re-derive. The constant is frozen and independent of the tip's pin, which is real, but the digest itself is tool-reported. |
| 3 | F:15-16 "captures the HTTP surfaces" | C requires only `tags`, `ps-after`, `version`, `ps-before` (C:89-102). Captures `root`, `tags-empty`, `v1-models-empty`, `v1-models`, `v1-model-single`, `show`, `generate` need not exist, and no capture's `status` field is read. `v1-models` and `generate` content is accepted only through the tool's `passed` flags. | Partly unenforced. |
| 4 | F:16-17 "replays them through tools/kama-ollama-evidence.py before (available_not_loaded) and after one generation (loaded_same_digest)" | C never runs kama-ollama-evidence.py and never reads `finding_id`. It requires `evidence-before-load` and `evidence-after-load` `passed is True` (C:32-34, 81), which is tool self-report. C does re-derive the substance from bodies: `ps-before` is `[]` plus the tags entry (C:102), and `ps-after` digest equals tags digest (C:93-95). The replay itself is not checked. The tool's after-replay reuses the pre-generation `tags_raw` (T:399 vs T:352); tags are never re-fetched after generation. | Replay is unenforced; its substance is partly re-derived. |
| 5 | F:17 "tears the child down" | C accepts the tool-reported `teardown` dict (C:105-107). The child PID is never recorded, so C cannot check it. The only independent signal is incidental: `port in listening_ports()` (C:76) runs after the run, so a still-listening server would fail. Runner and llama-server grandchildren are not checked (see §3). | Self-report plus an accidental check. |
| 6 | F:14 "on a free unregistered loopback port" | "Unregistered" is the hardcoded set `{8080, 34113}` (C:31, T:56), not `registry/endpoint-consumers.tsv` (which also carries those two ports, lines 35-37). C:76 tests "not listening" after teardown, not "free before start". It is a flaky false-reject path if another process takes the ephemeral port after the run, and it proves nothing about pre-start freedom. "Loopback" is enforced only through the log regex `Listening on 127\.0\.0\.1:{port}` (C:113). | Partly enforced (loopback and registered-set yes; "free" no). |
| 7 | F:16 "after one generation" | C:116 requires `POST     "/api/generate"` to appear at least once in the log. It does not require exactly one, and does not check status 200 on the log line. | Weaker than "one". |
| 8 | F:18-19 "model manifest / imported blob from the run's own work dir" | Enforced (manifest glob C:117-125, blob re-hash C:126-129). But C:12 "artifacts only a real Ollama server leaves" is not established. The manifest check is a bare substring `sha256:{FROZEN_MODEL_SHA}`, and a tool that wrote the manifest, blob copy and serve.log itself would pass. No control uses a fabricated-artifact tool. | Enforced as stated for the work dir; C's docstring claim is overstated. |
| 9 | F:14 "digest-pinned ... v0.40.11" | Enforced twice: capture `version` (C:97) and the log `(version 0.40.11)` (C:113). | OK. |
| 10 | F:13-14 "caller nonce", "nonce-named model from the capture bodies" | Enforced: nonce echo (C:69), `kama-{nonce}:latest` in tags and ps-after (C:90-95), manifest dir (C:117). | OK. |

## 2. verify() checks that are decorative (cannot fail given the tool, or fail only through a path the tool cannot produce)

| Check (C line) | Why it cannot fail on a tool-produced receipt |
|---|---|
| `schema` (C:67) | T writes the `SCHEMA` constant (T:53, 217). |
| `nonce` (C:69) | T echoes `args.nonce` (T:253-254). It matters only for the stale control. |
| `evaluated is True` half of the REQUIRED loop (C:81) | T's `check()` defaults `evaluated=True` (T:226) and no call site passes `evaluated=False`, so `evaluated` is always True. |
| REQUIRED `binary-digest`, `model-digest`, `port-unregistered`, `ready`, `version`, `running-exe-digest`, `listener-owned`, `tags-empty-before-create`, `create`, `tags-lists-model`, `v1-models-lists-model`, `evidence-before-load`, `teardown` (C:32-34, 80-82) | T returns `MODEL_OK` only if no evaluated check failed (T:430-432). Each of these is appended unconditionally before any `MODEL_OK`, or the tool returns early with another verdict. Given `verdict == MODEL_OK` (C:71) they are already implied. Only `generate`, `ps-lists-loaded` and `evidence-after-load` add information, because `--no-generate` yields `MODEL_OK` without them (T:384). |
| `port-unregistered` self-check (T:277) | `free_port()` just returned a port that passed the same two tests (T:103-111), so it can fail only by a race. |
| `capture-sha` (C:84-87) | T computes sha256 of the raw bytes and stores the decoded body (T:161-163). It mismatches only for non-UTF-8 bodies, and it is self-consistency, so a producer who recomputes the sha passes. It is non-decorative only against the t1 tamper. |
| `tags-entry`, `ps-digest`, `version`, `ps-before-not-empty` (C:89-102) | Duplicate the tool's own checks on the same bodies. They are real for tampered receipts but cannot fail on an honest one. `len(ent) != 1` fires only for len>1: len 0 raises IndexError on `ent[0]` first and is reported as `capture-parse`. |
| `errors == 0` in `met` (C:216) | `errors` is incremented only at C:177 when `rec is None`, which implies `live_ok == 0`, so `met` is already False. The conjunct can never change the outcome. Tool timeouts (`subprocess.run(timeout=600)`, C:140) or `check=True` failures propagate as a traceback with no summary line, not as `errors=N`. F:22 "any errors>0" is therefore not an implementable branch; it collapses to "no summary line, exit 1". |
| Fake-binary control `verify(r, rd, r.get("nonce"))` (C:192) | The `BINARY_DIGEST_MISMATCH` receipt has `verdict != MODEL_OK`, so verify always returns non-empty. The conjunct is decorative. The control actually tests only T's pre-exec digest gate (T:264-266), not the verifier. Neither "fake server binary" is ever started: the python script (C:179-181) and the patched copy (C:182-187) both exit before any server. A fake binary that serves HTTP is not exercised. |
| Stale control (C:196-198) | A different nonce is rejected by the first nonce test, and also by `tags-entry`, `ps-digest`, `manifest` and others, so it does not isolate the stale-nonce clause. It is real but trivial. |
| Tamper t1 (C:200-201) | Rejected by `capture-sha` alone. A tamper with a recomputed sha, which would exercise the `tags-entry` content check, is not run. |

## 3. Limits stated in the freeze that the counter or tool contradicts (F:25-26)

1. **"one lane-owned child on one loopback port for the length of a run" (F:25)** is contradicted by Ollama itself.
   - Probe: I ran `tools/kama-ollama-live.py --work <my scratch> --nonce pcrit0001a` with a 10 ms poller diffing `/proc/net/tcp{,6}` LISTEN sockets against a pre-run baseline. Result: exit 0 MODEL_OK, receipt port 51791, teardown rc 0.
   - The poller saw 4 new loopback listeners: 51791 (the server), 39687, 41041 and 42099. Peers run other servers concurrently, so I only attribute 39687.
   - That port is the server's own child, from my run's serve.log: `msg="starting llama-server" cmd=".../lib/ollama/llama-server --model <work>/models/blobs/sha256-270cba1b... --port 39687 --host 127.0.0.1 ...` (source=llama_server.go:457).
   - So a second 127.0.0.1 listener, owned by a grandchild process, exists during generation. The tool also runs a client process `binary create` (T:339). The tool docstring T:33-34 ("one loopback port") and F:25 are both overstated. The receipt records neither the extra port nor the grandchild PID, and the counter's `listener-owned` is only the server's port. The committed `live/serve-lines.txt` (17 lines) is filtered and contains no `--port` line, so the shipped evidence cannot show it.
2. **"CPU only (CUDA/HIP/Vulkan device variables are set to -1 by the tool)" (F:25-26)**: the env-setting half is true (T:185-189). Nothing in C verifies it, and the receipt never records the env (T:19-20). Real evidence exists in serve.log: my run logged `msg="inference compute" id=cpu library=cpu` and `user overrode visible devices` WARN lines for all three variables. The counter checks none of it, and the committed `serve-lines.txt` has 0 `library=cpu` lines. "CPU only" is an unverified statement that sits next to "not GPU placement" in the same limits line. The two are consistent only if read as "variables set", not "CPU placement proven".
3. **F:21 "prints: ... errors=0 met=True"** differs from the actual line. C:218-219 and `controls/c1-*.out` append ` predicate='C1-r60 ...'`. It is cosmetic, but the frozen print format is not what the counter prints.
4. **C:6 "Frozen predicate (same sentence as ... freeze.txt)"** is not the same sentence. C:8-9 reads "2 fake binaries ... 1 missing log" and "this counter's independent verifier", against F:12-13 "2 fake server binaries ... 1 removed server log" and "tools/round60-c1-counter.py's independent verifier". The printed `PREDICATE` (C:36) is a third, shorter wording.
5. **"tool absent at the measured tip" (F:22)** is wider in C: `git archive` of three paths (C:35, 162) fails if any of the tool, evidence tool or pin is missing, and also on a bad `--repo` or `--tip`, and all print `tool_present=0`. It fails closed, so it is harmless, but the label is imprecise.
6. **Host dependence is not a stated limit.** The counter run at a tip needs `~/.local/opt/ollama-v0.40.11/bin/ollama` and `~/.cache/kama-shokunin/models/stories260K.gguf` on the host (pin:10-11). Neither is carried by the tip, and C:30 hardcodes `REAL_BIN`. F:25-26 does not say the claim is host-state-dependent.

## 4. Should each overstated clause be corrected in the report text?

The frozen predicate stays as is; a miss is reported, never narrowed. Correct these in the report text, by quoting the F sentence and stating what was measured:

- **Correct (§1.2):** write "the verifier compares the receipt's binary_sha256 to a frozen constant", not "re-derives". The tool-side `running-exe-digest` is the only hashing of the running binary and is self-reported.
- **Correct (§1.1):** the archive sha is pinned in the registry but not machine-checked by the counter. State "official" as pin-comment provenance, not an enforced property.
- **Correct (§1.4):** say the replay through kama-ollama-evidence.py is tool-reported, and name what the counter re-derives instead (`ps-before` empty, `ps-after` digest equals tags digest). Mention that the after-replay uses pre-generation tags.
- **Correct (§1.3, §1.5):** "captures the HTTP surfaces" means 7 of 13 captures are required and none has its status read. Teardown is tool-reported.
- **Correct (§3.1), required:** F:25 and T:33-34 "one loopback port" is false as stated. Report "one server port plus a llama-server child port during generation (39687 in my run; port varies)". Do not cite the receipt as proving a single listener.
- **Correct (§3.2):** report "CPU only" as "device env variables set; the CPU result is visible in serve.log, not checked by the counter".
- **Report as a miss, not a rewrite (§2):** the `errors=0` conjunct and the fake-binary `verify` conjunct are decorative. Report the 7/7 controls as "7 rejected", with the note that the 2 fake-binary controls exercise the tool's pre-exec gate, not the verifier and not a running fake server.
- **Calibration:** the statement "the independent verifier ... checks artifacts only a real Ollama server leaves" (C:11-12) should be reported as "checks artifacts a real server leaves, with no control that a tool-fabricated work dir fails".

## 5. Smallest safe corrections (fix-shaped, not applied)

- Record in the receipt the extra loopback listeners (`/proc/net/tcp` diff during generate, or the `--port` from serve.log), and have C require `inference compute ... library=cpu` and the `--port` line in serve.log.
- Have C hash `/proc`-independent evidence: re-hash `REAL_BIN`, compare it to `FROZEN_BIN_SHA` and add an archive constant, if "re-derives" is to remain in the sentence.
- Add a control where a tool-fabricated serve.log, manifest and blob copy run under a stub binary that passes the digest gate, which cannot exist offline. Absent that, drop "only a real server leaves".
- Delete the `errors == 0` conjunct, or make timeouts and non-zero returns increment `errors`, so the F:22 kill rule is implementable.

Checks run: one live tool run (exit 0, MODEL_OK) with a port poller (results in §3.1); reads of the files named above; `grep -n` for line numbers. Nothing else was run, and the scratch dir was removed.
