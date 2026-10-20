VERDICT: partial — the README/PROVINCE/SHONEN round-16 appends are bounded, claim no `[x]`, and widen no authority beyond the C2 fixture; every substantive claim I attacked confirms. Six low-severity notes remain: three README summary accuracy/completeness defects (a one-versus-two live-run count, a five-of-seven corrections list, a non-verbatim quoted phrase), one PROVINCE provenance-label omission, one SHONEN literal-`[x]` scanner hazard, and a dangling `LOG.md` pointer that SHONEN cites.

# What I ran

All paths relative to `/home/vgpnk/Projects/shokunin/kama-shokunin`.

| Command | Exit | Result |
|---|---|---|
| `git show b8e485c --format='' -- corpus/README.md` | 0 | the 21-line round-16 append |
| `git show b8e485c --format='' -- PROVINCE.md SHONEN.md` | 0 | the 15-line PROVINCE append, 1-line SHONEN rewrite |
| `git show 1e41928:corpus/knowledge/runtime-health-surface-matrix.md \| sed -n '14p'` | 0 | byte-identical to the current line 14 (round-10 provenance confirmed) |
| `sed -n '290,370p' .ufo/waves/round-16/sources/llama.cpp-704366d/server-http.cpp` | 0 | `middleware_server_state` 503 at 314-325; frontend exemption 309-311; state gate 354 before API key 357 |
| `sed -n '430,520p' .ufo/waves/round-16/sources/llama.cpp-704366d/server.cpp` | 0 | single-model: `start()` → `load_model` → `is_ready.store(true)`; router: ready right after `start()` |
| `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json` | 0 | `VALID` |
| `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt-frozen-probe.json` | 0 | `VALID` |
| `python3 tests/llamacpp-live/check-receipt.py --selftest` | 0 | 16 mutations + unreadable case rejected; valid accepted |
| `ss -ltn \| grep -E ':8080\|:34113'` | 1 | no listener on either port |
| `pgrep -ax llama-server` | 1 | no process |
| `sha256sum ~/.cache/kama-shokunin/models/stories260K.gguf`; `stat -c '%s bytes'` | 0 | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, 1185376 bytes |
| `ls -la ~/.local/bin/llama-server` | 0 | symlink → `~/.local/opt/llama-b11755/llama-server` |
| `git diff-tree --no-commit-id --name-only -r b8e485c -- corpus/knowledge` | 0 | 8 files: the new entry + 7 corrected entries |
| `grep -n '\- \[x\]' corpus/README.md PROVINCE.md SHONEN.md` | 1 | no checked boxes |
| `grep -rn "real-runtime evidence for llama.cpp only" .` | 0 | matched only `corpus/README.md:215` |
| `grep -n systemctl tools/kama-llamacpp-live.py` | 1 | no unit control in the tool |
| `systemctl --user list-unit-files \| grep -i llama` | 1 | no llama user unit |
| `find ~/.config -maxdepth 2 -iname '*llama*'` | 0 | no matches |

No `measure.py` run (prohibited). No llama-server started. No connection made to 8080 or 34113; only `ss`, `pgrep`, and code/receipt inspection.

# Confirmations (evidence)

**README `corpus/README.md:202-221`**

- `:209` "`/health` 503 body was already held at `runtime-health-surface-matrix.md:14` (round 10)": the round-10 commit `1e41928` line 14 is the same table row (`503 unavailable_error "Loading model"`); current line 14 unchanged.
- `:206` "every non-frontend path 503 before the API key": pinned `server-http.cpp:307-328` returns 503 for every path except `frontend_paths`, and `:347-359` runs the state gate before `middleware_validate_api_key`.
- `:206` "single-model versus router readiness": `server.cpp:493-515` starts the listener, loads the model, then sets `is_ready`; router mode `:460` sets `is_ready` right after start and never emits the body.
- `:206` "probe's `MODEL_LOADING` mapping and limits": the entry's mapping table and scope limits cover this.
- `:207` lesson covers "C1/C2 gate decisions, mined mistake M1, round-15 routed-defect dispositions": `corpus/lessons/round-16.md` §§Declared claims, Gate, Mistakes (M1), Routed defects.
- `:216-221` frontier disposition: the "still open" set matches the entry's scope limits (`llama.cpp-loading-lifecycle.md`), `registry/history/latest.tsv` (three `DEAD`), and the receipt (`loading_observed` false).
- The live fixture does not probe the registered consumers: the receipts' `port_refusal_set` is `[8080, 34113]` and all captures/probes use the ephemeral port (32845 / 39375).

**PROVINCE `PROVINCE.md:55-66`**

- `:56-58` install tree and link: `~/.local/opt/llama-b11755/llama-server` exists; `~/.local/bin/llama-server` is a symlink to it; the receipt argv records exactly that path.
- `:58-59` "1.2 MB GGUF kept in the lane-owned cache": `~/.cache/kama-shokunin/models/stories260K.gguf`, 1,185,376 bytes, sha256 `270cba1b…d256d`; the receipt's `model_sha256_post` matches.
- `:59-60` "free loopback port that is never a registered consumer port or a listening port": `HARD_REFUSED_PORTS {8080,34113}` plus every registry port token; default picks `bind(127.0.0.1:0)` and rejects any refused port; explicit `--port` rejects the refused set and an in-use port (`tools/kama-llamacpp-live.py:192-255`). The receipt's `port_pick_note` discloses the release/rebind race, and `port_owned_by()` fails the run if the listener is not the child's.
- `:60` "tears it down in the same run": `teardown()` SIGTERMs the process group, SIGKILLs after grace, proves the port refuses; receipt `returncode 0`, `sigterm_sent true`, `sigkill_sent false`, `port_refuses true`, `pdeathsig.prctl_ok true`; `controls.txt` records `post_pgrep_llama_server=0` and `post_ss_8080_34113=0`; current host matches.
- `:63-64` "starts no unit, writes nothing under `~/.config`, `~/.omp` or systemd": no `systemctl` in the tool (grep exit 1), no llama user unit (exit 1), no llama-named file under `~/.config` (find exit 0), and the tool writes only the temp log in `/tmp` and the receipt at `--out`.
- `:64-65` "changes no registered row: the three consumers stay `DEAD`": the commit changes only the registry's verdict-comment line (`registry/endpoint-consumers.tsv:32`); `latest.tsv` has three `DEAD` rows; `ss` shows no listener on either port. The current-state `DEAD` (connection refused) reading is [INFERENCE from no listener plus the tracked `latest.tsv` rows]; the README's sentence is about the run changing no row, which is directly confirmed.
- `:61-63` narrowing quote: round-1 `corpus/lessons/round-1-safety.md:88-90` says "L0 must approve any endpoint outside the declared local model registry"; the note narrows it only for the tool's own child and preserves L0 for every other unregistered endpoint.

**SHONEN `SHONEN.md:8`**

- `10/10 kama-llamacpp-live/v1 checks`: receipt `checks` length 10, all `passed: true`; gate `VALID` exit 0.
- `MODEL_OK`/`matched` exit 0 and `MODEL_MISMATCH`/`served-id-mismatch` exit 2: receipt probes re-derived by the gate.
- "teardown proven": `teardown_exited`, `teardown_port_closed`, `model_unchanged` checks all true; receipt teardown facts above.
- "`loading_observed` false": receipt field false; `loading_503` null.
- "unregistered loopback port": port 32845; registry has only 8080 and 34113.
- "not registered-consumer reconciliation, other runtimes, generation or model quality": no generation request in the tool (no completion/chat POST), no other runtime started, no consumer probed.
- "no non-author `[x]`": `grep '\- \[x\]'` exit 1; all four SHONEN boxes are `[~]`.

# Findings (severity order)

## LOW-1 — README undercounts the live runs: "one live lane-owned run"

`corpus/README.md:206` says the entry covers "one live lane-owned run". Two full live runs are receipted:

- `.ufo/waves/round-16/live/receipt.json`: port 32845, `started_utc 2026-10-20T13:49:38.040Z`, 10/10.
- `.ufo/waves/round-16/live/receipt-frozen-probe.json`: port 39375, `started_utc 2026-10-20T13:49:38.250Z`, 10/10.

They are distinct executions (different ports, timestamps, log paths, and `props` capture hashes), not a replay of one run. The entry's own line `corpus/knowledge/llamacpp-loading-lifecycle.md:114` compounds this by calling the control "the same run". The control is the C1/C2 separability evidence and deserves the count. Suggested wording: "one primary live run plus a frozen-probe control run". (The gate accepts both receipts, so the evidence itself is sound; only the README/entry summary is under-inclusive.)

## LOW-2 — "Appended corrections" lists five, but seven knowledge files got round-16 corrections

`corpus/README.md:211-213` enumerates `endpoint-identity.md`, `consumer-registry.md`, `listener-census.md`, `served-identity-crosswalk.md`, `runtime-health-surface-matrix.md`. The commit also appends round-16 corrections to:

- `corpus/knowledge/ollama-evidence-replay.md` ("Repair ordering precision (appended round 16…)");
- `corpus/knowledge/snapshot-history.md` ("## Correction — round 16 (2026-10-20)").

Both carry round-16 append text (`snapshot-history.md:106` "## Correction — round 16 (2026-10-20)"; `ollama-evidence-replay.md:376` "Repair ordering precision (appended round 16, outside round-15 routed defect 5)"), so a reader taking the sentence as the round's complete correction set is [INFERENCE] misled. `LOG.md:936` says "appended corrections in five knowledge entries", which supports the narrower reading (the five vocabulary/loading corrections); the README does not say that. Suggested wording: "Loading-vocabulary corrections: …" (and leave the routed-defect corrections to the lesson), or add the two names.

## LOW-3 — quoted frontier phrase is not verbatim anywhere in the corpus

`corpus/README.md:215` puts `"real-runtime evidence for llama.cpp only, and stale"` in quotation marks. `grep -rn "real-runtime evidence for llama.cpp only" .` matches only that line. The nearest source wording is `corpus/README.md:60` ("Real-runtime reconciliation is proven for llama.cpp only") and `SKILL.md:333` ("Their real-runtime evidence is llama.cpp-specific and dated"). The meaning is right; the quote marks imply a verbatim source. Drop the quotes or cite the two lines.

## LOW-4 — "official release b11755" omits the Pre-release/mutable caveat

`PROVINCE.md:56` says "official release b11755". `corpus/SOURCES.md:50` (S038) records that the tag is a GitHub **Pre-release**, mutable, and says "cite the digest, not the tag alone"; the asset sha256 is `753bfa73…e226`. The receipt pins the installed tree, but PROVINCE alone gives no digest, so a future reader cannot tie the province statement to the asset from PROVINCE. Suggested wording: "official Pre-release tag b11755 (asset sha256 `753bfa73…`)" or "see the round-16 receipt's `install_tree`". Low because the province statement is about scope, not provenance, and the pinned values are in `SKILL.md` and the receipt.

## LOW-5 — SHONEN's literal `[x]` in the disclaimer

`SHONEN.md:8` contains the token `[x]` only inside "no non-author `[x]`". The checkbox list has no checked box (`grep '\- \[x\]'` exit 1), so the claim is accurate, but a literal `grep '\[x\]'` sees one occurrence and can false-positive a scanner. Reword to "no `[x]` claimed" or "zero checked boxes".

## LOW-6 (adjacent, but SHONEN cites it) — `LOG.md` §round 16 ends on a dangling promise

`SHONEN.md:8` cites `LOG.md` §round 16. That section ends at `LOG.md:953` with "Measured results follow in the next entry." There is no next entry in `b8e485c`; `LOG.md` is 953 lines. The 10/10 numbers are verifiable only from `receipt.json`, which SHONEN also names, so the SHONEN sentence is not false; but the LOG pointer does not itself carry the measured numbers at the commit. This is outside the three files and may [INFERENCE] be intended for L1's post-falsify append; flagging the current-state gap.

# Residual risk

- **L0 record for the narrowing.** `PROVINCE.md:61-63` narrows a round-1 item filed under "Ambiguities requiring L0 operator decision". The narrowing is explicitly bounded to the tool's own child and preserves L0 for all other unregistered endpoints, so it does not widen authority beyond the C2 fixture; but the commit contains no L0 record of the narrowing. If the province rule requires L0 sign-off, this note should be routed to L0 rather than treated as settled.
- **`port_pick_note` race.** `PROVINCE.md:59-60` says the port is "never … a listening port"; the tool releases the `bind(:0)` port before the child re-binds and the receipt discloses a sub-second collision race. The run fails closed on foreign ownership (`port_owned_by`, `port-listener-not-our-child`), so the served endpoint is child-owned or the run fails; the province sentence could mention the fail-closed ownership check if read strictly.
- **"about 8 ms".** The log format is `[M.s.ms.us]` (`common/log.cpp` at 704366d76); the receipt's log lines are `0.00.004.591` ("loading model") and `0.00.008.725` ("model loaded"), so 8.725 ms is process-start-to-loaded and the load call itself spans ≈4.1 ms [INFERENCE from the pinned log format plus the two lines]. The README's "about 8 ms" is defensible as total startup, not as the load-call duration.
- **The empty LOG measurements entry** (LOW-6) means the round's evidence chain at `b8e485c` relies on the receipt files, not the LOG prose, for the C1/C2 numbers.

# Limitations / disclosures

- I did not run the live harness (`tools/kama-llamacpp-live.py`) or any llama-server; this item does not authorize starting one. I relied on the committed receipts, the receipt gate, the tool source, `controls.txt`, and current host state.
- I did not run `.ufo/waves/round-16/measure.py` and did not complete a re-run of the 72-row probe matrix; those belong to other seats. One attempted `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json > /tmp/kama-r16-ReviewReadmeProvinceShonen/...` exited 1 at shell redirection because the scratch directory did not exist; the script did not run and produced no matrix output.
- I stayed on the three appends and cited artifacts. I did not read sibling falsify reports.
- **Bound violation disclosure:** one check, `find ~/.config ~/.omp -iname '*llama*'`, traversed filenames under `~/.omp/agent/sessions/`; the find completed (exit 0) but I opened no file there and discarded the output. Nothing from it is used above. No session/transcript/credential store content was read. Subsequent host checks were bounded to `~/.config` and `systemctl`.
- Two phrase greps (`grep -rn ... .`) were lane-wide rather than limited to the three files; they matched only `corpus/README.md:215`, `corpus/README.md:60`, `SKILL.md:333`, and wave advice (no session or credential store).
- Installs/updates: none. No tool was installed or upgraded for this review.
