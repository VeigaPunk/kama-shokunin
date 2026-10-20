VERDICT: confirm — delivered v3 exact-argv is full-list launch-identity equality with no secret-scan or auth predicate, and no credential value appears in C1 production or the live receipts; the kagi handoff boundary is not yet recorded as a handoff line.

Report: .ufo/waves/round-18/falsify/advice/ConnectKagi.md
Seat: `KamaR18.ConnectKagi-3` (connector, leaf). Advisory only. L1 owns integration and admission; this is not an outside non-author judgment, an admission, or a score change.

## Axes

Round axes: C1 operability 8 and C2 calibration 7 (lowest), per `SCORECARD.md:737-760`. This seat's scan axes are calibration (does the lane's statement about its own argv detector match what the detector can see?) and adjacency/scope (is the kama→kagi boundary recorded?). Operability is unchanged: no production file, counter input, measurement or runtime was touched.

## Setup and read scope

- Clone: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-ConnectKagi-3`; `git switch -q -c seat/ConnectKagi-3 1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; `git rev-parse HEAD` → `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; `git status --porcelain` → only `?? scratch/`.
- Kagi read scope, per assignment: only `/home/vgpnk/Projects/shokunin/kagi-shokunin/SKILL.md` and `kagi-shokunin/corpus/README.md`. No kagi knowledge body, `SOURCES.md`, checklist row, vault material or secret value was opened.
- No `c1/measure.py`, `c2/survivors.py`, `controls.py --selftest`, official runner, server, port or network operation was executed. The only executions are five `check-receipt.py` gate invocations on the committed receipt and on synthetic copies in the clone (below).

File identities at the clone (all `sha256sum`, exit 0):

| Path | SHA-256 |
|---|---|
| `tools/kama-llamacpp-live.py` | `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b` |
| `tests/llamacpp-live/check-receipt.py` | `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335` |
| `tests/llamacpp-live/controls.py` | `106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8` |
| `.ufo/waves/round-18/live/receipt-1.json` | `e616f67e2e2bec196402f56ed3a45fb68f78c9f4e927f0ea7d8acd170caf6d75` |
| `corpus/knowledge/llamacpp-loading-lifecycle.md` | `54ae1d65f2629ed1df63136701c3c1ea5ebcdce9598cb2f3a6fb83bdfc160c1c` |
| kagi `SKILL.md` | `00d6202f8b6d5eabf5438ce0cf287c2ef1236fbb7870c17a66353473f916e3b1` |
| kagi `corpus/README.md` | `7322a41cfa87735ccc85552f5d6ff12b8cfb60afd1497266df99bd01a286562d` |

`dc036d7…` equals the official `--expect-tool-sha256` in `.ufo/waves/round-18/runs/commands.json` `live-gate-1`, so the gate verdicts below are tied to the delivered producer revision, not just to the file on disk.

## Findings

### F1 — exact argv is full-list launch-identity equality, not a secret predicate

`tests/llamacpp-live/check-receipt.py:462-516` re-derives one list from receipt fields (`server.realpath`, `-m model.arg`, `--alias`, `--host 127.0.0.1`, `--port`, `-c`, `-t`, `--no-webui`, `--offline`) and rejects any difference at `:513-516`: `argv does not exactly match the producer's server.realpath/model.arg/alias/host/port/ctx/threads command`. There is no content pattern, no flag denylist and no inspection of argument values beyond field equality.

Retained controls target that predicate in the controls file:

- `tests/llamacpp-live/controls.py:701-707` (k20) inserts `['--api-key', 'X']` before the fixed tail and requires a problem line matching `^(?!.*\bprobe).*\bargv`; the value is the literal placeholder `X`, never a credential.
- `tests/llamacpp-live/controls.py:741-747` (k22) inserts a duplicate `['--host', '0.0.0.0']` before the tail; a first-occurrence flag lookup still reads `127.0.0.1`, so only list equality refuses it.
- `tests/llamacpp-live/controls.py:1735-1736` asserts the k20 forgery kept the fixed tail and the inserted pair.

### F2 — executed witnesses: secret-shaped and non-secret twins fail identically

Commands (clone, cwd `/tmp/kama-r18-falsify-ConnectKagi-3`, `ARGS` = `--require-schema v3` plus the four official `--expect-*-sha256` pins from `runs/commands.json` `live-gate-1`):

```
python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-18/live/receipt-1.json $ARGS
  VALID .ufo/waves/round-18/live/receipt-1.json                      exit 0

python3 -c "import json,copy; d=json.load(open('.ufo/waves/round-18/live/receipt-1.json'));
 a=copy.deepcopy(d); a['argv'][-2:-2]=['--api-key','X'];
 json.dump(a,open('scratch/forged-apikey.json','w'),indent=1,sort_keys=True)"
python3 tests/llamacpp-live/check-receipt.py scratch/forged-apikey.json $ARGS
  INVALID …: 1 problem(s)
    - argv does not exactly match the producer's server.realpath/model.arg/alias/host/port/ctx/threads command
                                                                       exit 1

python3 -c "… a['argv'][-2:-2]=['--metrics'] …"
python3 tests/llamacpp-live/check-receipt.py scratch/forged-metrics.json $ARGS
  INVALID …: 1 problem(s)
    - argv does not exactly match the producer's server.realpath/model.arg/alias/host/port/ctx/threads command
                                                                       exit 1

python3 -c "… a['argv'][-2:-2]=['--host','0.0.0.0'] …"
python3 tests/llamacpp-live/check-receipt.py scratch/forged-duphost.json $ARGS
  INVALID …: 1 problem(s)
    - argv does not exactly match the producer's server.realpath/model.arg/alias/host/port/ctx/threads command
                                                                       exit 1

python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-18/live/receipt-1.json $ARGS
  VALID .ufo/waves/round-18/live/receipt-1.json                      exit 0
```

The `--metrics` twin is decisive for the assignment's question: a non-secret extra flag is rejected by the same message as `--api-key X`. The predicate cannot be a secret detector, because it never had to look at what the token means. The gate's message also does not interpolate the unexpected token or its following value, so the forged placeholder is not echoed into gate stdout. The pristine receipt was never written; its hash is unchanged (`e616f67…`) and re-verification is green.

Note on the frozen comparator: the build-wave `ConnectKagi.md` finding 7 predicted `[INFERENCE]` that the v2 gate accepted a before-tail insertion, and `MutBaselineForgeries.md` showed only the end-append variant (rejected by the tail check). The delivered v3 equality closes the before-tail class; the controls k20/k22 and the official `c1-measure` run (`ReportNumbers.md:91`: "K20 and K22, argv | gate 0 on each | gate 1 on each, targeted argv rejection") are the retained evidence. I did not re-run the frozen v2 invariant.

### F2b — retained evidence pins two sub-classes, not the single-extra-flag class (code-derived; no mutant executed)

k20 is the only single-extra-flag control and its token is secret-shaped; k22's non-secret exemplar is a *duplicate* `--host`, not a single unknown flag. The gate-selftest argv mutations are field/tail mutations only (`check-receipt.py:1768-1777`: missing `--offline`, wrong `argv[0]`, wrong host). Code-derived, not executed: a gate that kept those field/tail checks, denied `--api-key`, and rejected duplicate flags would pass k20, k22 and every existing argv selftest mutation while accepting a single `--metrics` before the tail. The delivered gate rejects that receipt (F2, executed), so this is a coverage limit of the retained evidence, not a current code hole. If L1 keeps the handoff sentence's non-secret clause, one `mut("argv-extra-metrics", …)` in the same list (insert `--metrics` before the tail, expect exit 1) is the minimal retained witness; otherwise drop that clause and cite only k20/k22.

### F3 — no secret-scanning or auth-health claim in C1

- `grep -c "Authorization\|Bearer"` on `tools/kama-llamacpp-live.py` and `tests/llamacpp-live/check-receipt.py` → `0` and `0`. The same files contain no `401`/`403` token (`grep -cE '\b401\b|\b403\b'` → `0`, `0`). No auth header, no key option and no expected status assertion is present in C1 production.
- The launch list contains no key flag: `tools/kama-llamacpp-live.py:1241-1251` builds `[server_real, '-m', args.model, '--alias', args.alias, '--host', '127.0.0.1', '--port', port, '-c', ctx, '-t', threads, '--no-webui', '--offline']`.
- The three live receipts record exactly that list, e.g. `receipt-1.json`: `argv = ['/home/vgpnk/.local/opt/llama-b11755/llama-server','-m','/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf','--alias','kama-r18-live','--host','127.0.0.1','--port','33769','-c','256','-t','1','--no-webui','--offline']`; `child_env_keys = ['HOME','LANG','PATH']`; `outcome = pass`; `schema = kama-llamacpp-live/v3`. No `Authorization`, `Bearer`, `api-key`, `op://` or `OP_SERVICE_ACCOUNT_TOKEN` occurrence in any of the three (`json.dumps(receipt)` regex counts all zero).
- The delivered knowledge entry already bounds the claim: `corpus/knowledge/llamacpp-loading-lifecycle.md:257-261` — "The gate re-derives internal consistency, not an authenticated execution trace … Exact argv does not prove effective config free from HOME/config.ini inputs." C1's own wording is a *receipt* hole (round-18 lesson, declared claim and R6), which is exactly what the equality checks.

### F4 — the only credential-adjacent predicate is a names-only allowlist

- Producer: `tools/kama-llamacpp-live.py:84` `CHILD_ENV_KEYS = ('PATH','HOME','LANG','LC_ALL','TMPDIR')`; `:1256-1258` copies only those names when present and records `sorted(child_env)`. Values are never serialized.
- Gate: `tests/llamacpp-live/check-receipt.py:53` pins the same allowlist; `:446-459` requires every recorded element to be a bare name, inside the allowlist, and equal to `sorted(set(...))`.
- Executed off-allowlist-name witness:

```
python3 -c "… b['child_env_keys'] = b['child_env_keys'] + ['AWS_SECRET'] …"
python3 tests/llamacpp-live/check-receipt.py scratch/forged-envkey.json $ARGS
  INVALID …: 2 problem(s)
    - child_env_keys element 'AWS_SECRET' is outside the allowlist PATH/HOME/LANG/LC_ALL/TMPDIR
    - child_env_keys is not the producer's sorted unique list              exit 1
```

- The gate's own selftest carries the named adversary `env-key-off-allowlist` appending the name `AWS_SECRET` (`check-receipt.py:1766-1767`), and the official `gate-selftest` run exits 0 (`runs/commands.json` `gate-selftest`, stdout sha `da22d995…`).
- This is a *name-enumeration* check, not a value scan: it can reject a receipt that claims an off-allowlist variable name, but it cannot prove the recorded list is complete for the real process, and it never inspects values. It is the only predicate on this surface whose subject is credential-shaped.

### F5 — no credential value copied; two synthetic sentinels remain in build-wave advice

A recursive scan of `.ufo/waves/round-18` (excluding `interactive-sessions`) for `op://`, `OP_SERVICE_ACCOUNT_TOKEN`, `sk-…`, `Bearer <token>`, `AKIA…`, `ghp_…` found two files only:

- `.ufo/waves/round-18/build/advice/ConnectKagi.md` — the string `OP_SERVICE_ACCOUNT_TOKEN` is a *variable name* inside kagi's "putting the token in artifacts" Never rule, not a value.
- `.ufo/waves/round-18/build/advice/ProbeArgvEffects.md` — `Authorization: Bearer kamatest` / `Bearer kamatest2` are the seat's chosen synthetic test keys, and the experiment section is titled "(b) `--api-key kamatest` appended; no key sent". They are token-shaped but not secrets.

No live receipt, gate output, controls file or C1 production file contains a credential-shaped value. The k20 forge uses the literal `X`. The claimed "no credential values copied" therefore holds for C1 and its evidence; the sentinel caveat is about a build-wave advice artifact, not the delivered receipt path. This report itself quotes both sentinel strings (as synthetic), so a later scan over the wave will see a third file; that is the same labeled test data, not a new leak.

### F6 — overlap and explicit contradictions

- Kagi's argv fact is a different object: `kagi-shokunin/SKILL.md:478` — `the-janitor request "<text>"` — "args are rejected (exit 2) by design; argv is world-readable via `/proc`." Kama's gate never reads the llama child's `/proc/<pid>/cmdline`; the only `cmdline` read on the kama surface is the fake-kill pid-reuse guard in `tests/llamacpp-live/controls.py:780-801`. Citing kagi `:478` as the reason for kama's argv refusal would claim a detector that is not implemented.
- Kagi's secret scanning is explicitly *frontier, not held*: `kagi-shokunin/corpus/README.md:111` — "Secret scanning: detection versus verification". Kama must not hand kagi a scanning capability, and kagi must not receive kama's equality predicate as if it were one.
- Kagi's own handoff vocabulary already fits: `kagi-shokunin/SKILL.md:441` — `credentials_in_evidence: false`, `target_authority_conferred: false`.
- Kama already refuses the credential/auth surface to kagi: `kama-shokunin/SKILL.md:27` ("credential material, auth flows and secret handling (kagi)") and `:31` ("A 401 endpoint is evidence about identity; the key that would open it is kagi's surface — report, do not absorb").
- `corpus/knowledge/cross-lane-scope.md` §Round-report handoffs has a kagi bullet, but it is about the 8080 consumer drift, not this live harness. The new boundary has no recorded handoff line.

The contradiction that must stay visible: "exact argv" is **receipt-internal equality plus a producer-attested launch list**. The producer records `receipt['argv'] = server_argv` (`tools/kama-llamacpp-live.py:1251`) and later passes the same object to `Popen` (`:1290`) with no intervening mutation (read of `:1241-1290`); the gate cannot observe the real process. It is therefore not process-observed identity, not effective configuration (a `HOME/.config/llama.cpp/config.ini` or environment value can change behaviour without changing argv, as the knowledge entry states at `:259-260`), and not auth health. The lesson's R6 shorthand "exact argv" does not carry those bounds by itself; a cross-lane reader can over-read it.

One further producer-side limit, stated so the handoff does not overclaim: the gate cannot redact. If a future producer change put a credential on the launch list, the receipt would record it *before* the gate could reject the receipt for not matching the canonical list. Today's list has no such flag, so this is a bound, not a current defect.

## Affected axes

- **Calibration (7, lowest): improves.** The move binds one statement about a lane detector to that detector and its named adversary, and prevents the one plausible overclaim (reading k20's `--api-key` as secret scanning). It does not add a general-immunity claim; the twin witness is fresh falsify evidence, not a new entry in the fixed C2 universe.
- **Adjacency/scope: improves.** The kama→kagi boundary becomes a recorded, copy-pasteable handoff instead of an inference from two sibling docs.
- **Operability (8): unchanged, no harm.** No code, no counter input, no measured revision and no runtime changed. The round's measured evidence keeps its hashes.
- **Depth/coverage/freshness: unchanged.** No new knowledge ground, engine or sample.

## Proposed move (one bounded move)

Append one kagi bullet to `corpus/knowledge/cross-lane-scope.md` §Round-report handoffs (append-only; no existing line moves, no old receipt or lesson rewritten). Exact proposed text:

> - **kagi (round 18):** Kama reports: the v3 `argv` field is receipt launch-identity equality over the producer's fixed flag list (`tests/llamacpp-live/check-receipt.py:462-516`; controls k20/k22 `tests/llamacpp-live/controls.py:701-748`), not a secret scan and not auth health — no C1 production file asserts 401/403 or sends `Authorization`, and the gate refuses an extra `--api-key X` placeholder and, in the executed witness of `falsify/advice/ConnectKagi.md` F2, a non-secret `--metrics` twin with the same equality message. The only credential-adjacent predicate is the names-only child-env allowlist (`check-receipt.py:53,446-459`; producer `tools/kama-llamacpp-live.py:84,1256-1258`), whose named adversary is the gate-selftest `env-key-off-allowlist` (`AWS_SECRET`, `check-receipt.py:1766`); values are never recorded. Exact argv does not prove effective config or auth (`corpus/knowledge/llamacpp-loading-lifecycle.md:257-261`), so credential scanning, ref paths and auth state stay kagi's. `credentials_in_evidence: false`; no vault ref path is present in the receipts.

If L1 prefers the round-18 lesson as the single location, the same text can be placed there instead; it should appear once, not in both. No kagi file is edited by kama.

## Risks

1. **Do not turn the allowlist into a certificate.** It is membership-only: a valid receipt cannot list an off-allowlist name, but a forged receipt can omit names, and the gate never sees values. Say "names-only, values never recorded", not "the child env is exactly the recorded list".
2. **Do not read the equality message as redaction.** The producer records argv before the gate; a future keyed launch would be written to the receipt before validation. The current fixed list contains no key flag, and that is the whole basis of the "no credential value" statement.
3. **Do not cite kagi `SKILL.md:478` as the gate's mechanism.** It describes the janitor's stdin rule and `/proc` readability, not a llama cmdline observation. The k20 control is gate-only; no keyed or wildcard server is launched.
4. **Do not convert this into a secret-scanning claim or a C2 universe row.** Kagi's `corpus/README.md:111` marks scanning as unheld frontier; the C2 denominator is fixed to the named round-17 survivors, and fresh falsify witnesses must stay separate.
5. **Sentinel labeling.** `--api-key X` and `Bearer kamatest` are synthetic. If a later kagi scanning-frontier run reads the build advice, label them as non-secret test data or exclude the artifact with that reason; a hit there is a false positive, not a leak finding.

## Verification

For L1, in a scratch copy, not as this seat's verdict:

1. Run the five gate invocations in F2 with the official pins from `runs/commands.json` `live-gate-1`; expect exits `0, 1, 1, 1, 0` and the identical equality problem line for the three forgeries.
2. Run the F4 env-name forge; expect exit 1 with the allowlist problem first.
3. Confirm the appended bullet cites the exact lines and that `git diff` contains no production or counter file.
4. Confirm the unchanged measured hashes: `tools/kama-llamacpp-live.py` `dc036d7…`, receipt-1 `e616f6…`; the round-18 `runs/commands.json` was not re-run or overwritten by this seat.
5. If the handoff bullet keeps the non-secret `--metrics` clause, add the F2b one-line gate-selftest mutation and record a new `gate-selftest` artifact (do not overwrite `runs/`). If the clause is dropped, the bullet cites only the retained k20/k22 controls and the executed witness stays in this report.

## Limitations

- Runtime/gate checks were run only in the isolated clone; no server, listener, port, model load or network operation was performed. The official counters and control suite were not run, by scope.
- Kagi read scope was `SKILL.md` and `corpus/README.md` only. An unread kagi knowledge body could contain relevant cmdline material; the index sentence at `corpus/README.md:76` is that entry's published scope, and `:111` is the frontier statement used here.
- The producer-trust bound is stated from code reading and the delivered knowledge entry, not from a signed or process-observed launch. No claim about the real b11755 process's `/proc/<pid>/cmdline` is made or tested.
- No tool install or update: **none**. No pacman, uv, npm, cargo, host-config, service or fleet change.

## Teardown

Scratch and clone are under `/tmp/kama-r18-falsify-ConnectKagi-3` and were removed after this report was written. A `/proc` scan of every listening pid (`ss -ltnp`; the host set fluctuated 19–20 pids across the two scans) found no pid whose cmdline names this seat, and `pgrep -af kama-r18-falsify-ConnectKagi-3` returned nothing. No seat-owned listener or process remains. No report or artifact is copied back except this file; the experiment source is embedded in F2/F4 above.
