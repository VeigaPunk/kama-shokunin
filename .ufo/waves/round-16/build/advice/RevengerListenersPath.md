# RevengerListenersPath — MODEL_LOADING through `cmd_listeners` / `cmd_consumers`

Read-only seat. Nothing written except this report. No gate, harness, stub or test was run.

## Axes
A1 calibration honesty (a loading llama.cpp must not read as a foreign service);
A2 output-schema compatibility (existing keys/meanings, consumers);
A3 counter partition integrity (`probed` = Σ per-verdict counters);
A4 diff minimality / reviewability.

## Pins (the target moved while I read)
- Pre-change baseline: `.ufo/waves/round-16/frozen/kama-probe-before.sh`, sha256 `93ee4302…cd64`, 1092 lines. It was byte-identical to `tools/kama-probe.sh` before the C1 edit (`sha256sum` equal to the working file at first read), so *frozen* numbers below are today's pre-change behaviour.
- Working probe pinned for this report: `tools/kama-probe.sh`, sha256 `d0d48d8d…db8fe`, 1134 lines, mtime `2026-10-20 10:27:17 -0300`. The C1 executor landed `MODEL_LOADING` between my reads; every current line number was re-verified at that sha. Anchor on the quoted text, not the numbers, if the file moves again.

## 1. How a loading server flows through `cmd_listeners` today (frozen numbering)
1. Port set: `--port` → one port, scope `"override"`; otherwise `loopback_ports` from `ss -ltn` — frozen:670-675, `ports=("$OPT_PORT"); scopes=("override")`, `done < <(loopback_ports)`.
2. Each port is classified with the bare expectation: frozen:683 `classify "$port" "${OPT_EXPECT:-}"`.
3. `classify` (frozen:415) reaches the loading 503 with a JSON error envelope: `F_CODE=503` ⇒ `is2=0` (frozen:468 `case "$F_CODE" in 2*) is2=1 ;; esac`), body has no `data`/`models` (frozen:477) ⇒ `has_models=0`, and the HTML branch at frozen:507-510 is skipped.
4. Control falls to the non-2xx fallback: frozen:513 `C_VERDICT=FOREIGN_SERVICE` with frozen:521 `C_REASON=non-2xx-non-model-http`, and evidence text ending `(non-2xx HTTP from a non-model service)` (frozen:522).
5. The row is emitted unchanged in shape — seven keys, frozen:693-695 `{"port":…,"bind":…,"owner":…,"verdict":…,"reason":…,"served_model":…,"evidence":…}` — with `served_model` still `-` (initialised frozen:417 `C_VERDICT='' C_SERVED='-' C_EVIDENCE='' C_REASON=''`).
6. The counter `case` has **no** loading arm, so `n_foreign` takes it: frozen:685 `MODEL_OK|MODEL_MISMATCH) n_model=$((n_model+1)) ;;`, frozen:687 `FOREIGN_SERVICE) n_foreign=$((n_foreign+1)) ;;`.
7. Summary therefore reports `foreign_service=1, model_endpoints=0`: frozen:699 `"summary": {"probed": %s, "model_endpoints": %s, "foreign_service": %s, "unauthorized_service": %s, "dead": %s, "not_http": %s}` and frozen:704 `probed=%s model_endpoints=%s foreign_service=%s unauthorized_service=%s dead=%s not_http=%s`. `listeners` always returns 0 — a census (frozen:701 `return 0`).
8. `--expect` is irrelevant on this path: the expectation is consulted only inside the 2xx+model-array branch (frozen:479 `if [ "$is2" -eq 1 ] && [ "$has_models" -eq 1 ]; then`). A loading server with the *correct* expected id was FOREIGN_SERVICE, never MODEL_MISMATCH.

`cmd_consumers` pre-change (frozen:733-777) classifies the same way (frozen:741, :757 `classify "$OPT_PORT"…`, `classify "$pnum" "$expected"`), prints the verdict string in the row (frozen:744-747, :761-765), has **no** per-verdict counters (frozen:770 `"summary": {"consumer_rows_registered": %s, "consumer_rows_evaluated": %s, "exit": %s}`), and derives exit only from file reconciliation: frozen:754-755 `[ "$R_FMATCH" = no ] && exit_code=2` / `missing`. So a loading consumer showed `FOREIGN_SERVICE`/`non-2xx-non-model-http` and still exited 0.

## 2. What MODEL_LOADING changes in their output keys

| Surface | Keys changed | Value changes | Exit change |
|---|---|---|---|
| `listeners` rows | **none** (same 7) | `verdict`→`MODEL_LOADING`, `reason`→`llamacpp-loading`, `evidence` rewritten; `served_model` stays `-` | none (0) |
| `listeners` summary | **+1**: `model_loading` | `model_loading` counts loading; `model_endpoints` keeps its MODEL_OK\|MODEL_MISMATCH meaning | none |
| `listeners` `verdict_vocabulary` | string extended (from `VOCAB`) | — | — |
| `consumers` rows | **none** (both modes) | `verdict`/`reason`/`evidence`; `expected_model_id` echoed but not consulted | **none** — exit is file_match-only |
| `consumers` summary | **none** | — | none |
| `check` rows/summary | **none** | `drift` count and exit become drift for a loading row | 2 |
| `snapshot` | **none** (summary/row keys) | `verdict` cell in `latest.tsv`/dated JSON; DELTA may log a `verdict … -> MODEL_LOADING` transition | 2 |

The `listeners` counter partition must hold after the change: `probed = model_endpoints + model_loading + foreign_service + unauthorized_service + dead + not_http`. Without a loading arm the new verdict matched no `case` arm at all (frozen:684-690), so it would silently vanish from every counter while still incrementing `probed`.

## 3. Minimal compatible change (verified landed at the pinned sha)
- (a) Vocabulary: `VOCAB="MODEL_OK MODEL_MISMATCH FOREIGN_SERVICE UNAUTHORIZED_SERVICE DEAD NOT_HTTP MODEL_LOADING"` — current:60 (frozen:55), plus header comment current:30-34 and usage current:115. Required, because all four subcommands emit `"verdict_vocabulary": "%s"` from `VOCAB` (current:741, :812, :887, :1061); otherwise `listeners --json` would print a verdict outside its own declared vocabulary.
- (b) Counter declaration + arm: current:721 `… n_unauth=0 n_loading=0` and current:731 `MODEL_LOADING) n_loading=$((n_loading+1)) ;;`.
- (c) JSON summary, appended **last** so existing key order is untouched: current:741 `"not_http": %s, "model_loading": %s}` with the arg current:742 `"$n_nothttp" "$n_loading"`.
- (d) Text summary, appended last: current:746 `… dead=%s not_http=%s model_loading=%s` with args current:747 `"$n_nothttp" "$n_loading"`.
- (e) Snapshot baseline whitelist: current:937 `*\ DEAD\ *|*\ NOT_HTTP\ *|*\ MODEL_LOADING\ *) : ;;`. This is not optional: `latest.tsv` persists the verdict verbatim (current:1090-1091 `printf '%s\t%s\t%s\t%s\t%s\t%s\n'` / `"${EV_IDS[i]}" "${EV_VERDICT[i]}"`), and a non-whitelisted verdict hits current:938 `dropping malformed baseline row`, then resurfaces as a phantom `row-added` transition on the next run (current:962).
- (f) Classification gate + exact-envelope helper: current:501 `if [ "$F_CODE" = "503" ] && [ -s "$FBODY" ] && body_is_llamacpp_loading "$FBODY"; then` and current:426-443; it sits after 401/403 and before the HTML/FOREIGN_SERVICE fallbacks, as the claim requires.
- **Not required:** any `cmd_consumers` change. It has no verdict counters and its exit never consults the verdict — `check`'s drift rule carries "drift true" instead: current:862 `if [ "$verdict" != "MODEL_OK" ]; then drift=true; fi`, and the `--port` branch likewise (current:846 `if [ "$C_VERDICT" = "MODEL_OK" ]`).

Why one added key rather than folding loading into `model_endpoints` (the implementer brief allowed either): folding would keep zero new keys but silently redefine `model_endpoints`, which today means MODEL_OK|MODEL_MISMATCH (current:726). The additive key leaves every existing key's meaning byte-identical, keeps the partition checkable, and makes loading directly observable — the operability axis. The only shape movement is one optional key under the unchanged `"schema": "kama-probe/v1"`.

State check at sha `d0d48d8d…`: all six sites above are present; `model_loading` appears exactly once in JSON (741) and once in text (746); args line up with key order (742/747); `n_loading` is incremented exactly once (731). No residual un-landed site found.

## 4. Residual risks / limitations
1. **python3-less host:** the helper fails closed — current:427 `[ "$HAVE_PY" -eq 1 ] || return 1` — so `MODEL_LOADING` is unreachable while `VOCAB` still advertises it. [INFERENCE] harmless on the measurement host (python3 present); a limitation worth one line if the matrix ever runs in a stripped environment.
2. **Envelope-only match:** current:501 gates on status+body only, no `Server: llama.cpp` header. Any service returning that exact 503 envelope is classified `MODEL_LOADING`; [INFERENCE] this includes a proxy in front of llama.cpp, which is the intended subject, but it is not proof of the binary.
3. **Pre-existing wording trap, not introduced:** the listeners JSON still says `"2": "drift (listeners does not gate)"` (current:741) while `listeners` returns 0 (current:743). `MODEL_LOADING` is "drift" in `check`/`snapshot` only; a reviewer may expect a gating exit here. Leave for minimal diff.
4. **Doc drift:** `SKILL.md:12-14` still says "Verdict vocabulary is shared with `tools/kama-probe.sh`: `MODEL_OK` | `MODEL_MISMATCH` | `FOREIGN_SERVICE` | …" and omits `MODEL_LOADING`. Not the probe executor's file; needs an owner. `SKILL.md:233` ("`listeners` classifies… exits `0` as a census") remains accurate.
5. **Schema-compat check:** no in-repo consumer of `listeners` summary keys exists — grep for `model_endpoints|foreign_service|not_http|unauthorized_service` over `*.sh/*.py/*.md/*.json/*.tsv` hits only the probe. `tools/test-snapshot.sh` never invokes `listeners` (grep: no match) and asserts snapshot-only shapes — `test-snapshot.sh:107` `assert doc["summary"] == {"registry_rows_evaluated": 1, "model_ok": 1, …}` and `:111` `assert set(row) == {` — both unaffected. [INFERENCE] external consumers of the v1 listeners summary are unknown.
6. **Snapshot coupling:** keep 937 and 1091 in sync; a baseline written with `MODEL_LOADING` is only readable by a probe that still whitelists it (forward/backward skew across a rollback would drop the row).

## 5. Not run here (L1 owns measurements)
No `bash -n`, no stub matrix, no live probe. Suggested L1 assertions once integrated: (i) `bash -n tools/kama-probe.sh`; (ii) run `listeners --port <loading-stub> --json` and require `probed=1`, `model_loading=1`, `foreign_service=0`, and the six-way partition identity; (iii) a two-run `snapshot` with an isolated `--history` while the stub is loading, requiring no `malformed baseline row` warning and `transitions` stable on the re-run.
