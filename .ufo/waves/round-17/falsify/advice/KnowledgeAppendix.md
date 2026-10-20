VERDICT: partial — The ready-body and S046 measurements match; the signal-path summary and inherited limits need qualification.

## Scope attacked
Round 17 appended section of `corpus/knowledge/llamacpp-loading-lifecycle.md`, checked against S042–S044/S046, pinned llama.cpp files, the three v2 receipts, the receipt gate summary, and recorded controls.

## Findings (severity order)

### MEDIUM — The graceful-shutdown description omits a signal-loss window
`corpus/knowledge/llamacpp-loading-lifecycle.md:174-176` says the first signal “stops the task loop” and the main thread “returns 0.” S043’s code does not make that unconditional: the handler is installed at `sources/llama.cpp-704366d76/tools/server/server.cpp:533-534`, while `start_loop()` is called later at `server.cpp:575-576`. `server-queue.cpp:132-135` sets `running = false` in `terminate()`, but `server-queue.cpp:278-280` sets `running = true` at the start of `start_loop()`. **[INFERENCE]** A SIGTERM in the post-registration/pre-`start_loop()` interval can therefore be overwritten; the loop need not stop and the process need not return 0. The three S046 receipts establish successful later teardown (each records `alive_at_teardown_start=true`, `sigterm_sent=true`, `sigkill_sent=false`, `returncode=0`, and `term_wait_ms=3`), but do not rule out that interval. Qualify the source path as graceful once `start_loop()` is active, and retain the narrow race as a limitation.

### LOW — “v1 limits above are superseded” needs a narrower scope
`corpus/knowledge/llamacpp-loading-lifecycle.md:194-202` says “The v1 limits above are superseded for receipt v2.” The specific health-body, teardown-predicate, and loading-envelope grading fixes listed there are supported. But the earlier scope limit at `:142-143` says the live loading-body probe verdict “comes from the replay”; that limitation remains. In the current tool, readiness and ready captures precede the `run_probe()` calls (`tools/kama-llamacpp-live.py:1143-1164,1208-1214`), while `loading_envelope_graded` only checks saved envelope bodies (`:1342-1356`). S046 `receipt-3.json#/probes` contains only `MODEL_OK` and `MODEL_MISMATCH`, not a live `MODEL_LOADING` result. Narrow “v1 limits” to the named predicate defects and explicitly carry forward the no-live-probe-during-load limitation; the earlier quality/performance/GPU-path scope limits also remain unchanged.

### LOW — “still DEAD” is not current evidence
`corpus/knowledge/llamacpp-loading-lifecycle.md:209-211` says the consumers are “untouched, still `DEAD`.” The latest available `registry/history/latest.tsv:1-4` identifies snapshot `20261014T124232Z` (October 14) and records the two consumers on port 34113 as `DEAD`; S046’s runs are October 20 and explicitly are not registered-consumer health. The receipts support “untouched,” not their current state. Say “last recorded DEAD in the 2026-10-14 snapshot” or omit the present-tense assertion.

## Residual risk / verification gaps
- The v2 loading-body collector caps distinct 503 bodies at 256 (`tools/kama-llamacpp-live.py:75,560-567`); later distinct bodies increment `loading_bodies_dropped`, but that count is not a failure condition in `loading_envelope_graded` (`:1342-1356`). The knowledge text accurately limits its check claim to “stored” bodies, but the final Limits paragraph should disclose the cap. All three S046 receipts report zero dropped bodies, so this does not affect their observed result.
- Confirmed against the sources/receipts: `/health` ready body is 15-byte `{"status":"ok"}` with the stated SHA-256; OPTIONS precedes the state gate; loading-envelope hash, 42/45/45 totals, three 3-ms returncode-0 teardowns, ports, 11 passing checks, and gate VALID results match. The controls summary reports zero accepted-bad controls. No other factual discrepancy found in the appended body/key-order correction.

## Commands and verification
No build, test, gate, measurement, live server, or fake-server command was run. Static source/receipt inspection used `read`/`grep`; no installs or updates.

Commands run (exit codes):

1. `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kamar17-knowledgeappendix-clone && git -C /tmp/kamar17-knowledgeappendix-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && printf '%s' '{"status":"ok"}' | sha256sum && wc -c /tmp/kamar17-knowledgeappendix-clone/tools/kama-llamacpp-live.py /tmp/kamar17-knowledgeappendix-clone/tests/llamacpp-live/controls.py /tmp/kamar17-knowledgeappendix-clone/tests/llamacpp-live/check-receipt.py` — exit 0.
2. Exact read-only receipt summary — exit 0:
```sh
cd /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live && python3 - <<'EOF'
import json, hashlib
for n in (1,2,3):
    r = json.load(open(f'receipt-{n}.json'))
    print(f'--- receipt-{n}')
    print('schema', r['schema'], 'port', r['port'], 'started', r['started_utc'], 'ended', r['ended_utc'])
    print('checks', len(r['checks']), [(c.get('name'), c.get('passed')) for c in r['checks']])
    print('teardown', json.dumps(r['teardown'], sort_keys=True))
    print('loading_503', json.dumps(r['loading_503'], sort_keys=True))
    bodies = r['loading_503_bodies']
    digests = {b if isinstance(b,str) else json.dumps(b,sort_keys=True) for b in bodies}
    print('bodies_n', len(bodies), 'distinct', len(digests))
    for d in list(digests)[:3]:
        print('body_sha256', hashlib.sha256(d.encode()).hexdigest())
    print('server', json.dumps(r['server'], sort_keys=True)[:600])
    print('tool', json.dumps(r['tool'], sort_keys=True)[:400])
    print('model', json.dumps(r['model'], sort_keys=True)[:400])
    print('internal_fault', r['internal_fault'], 'port_listener_ownership', r['port_listener_ownership'])
    caps = r.get('captures') or {}
    print('captures_keys', sorted(caps.keys())[:20])
EOF
```
(Canonical hashes/counts cited above were checked in the JSON receipt views.)
3. `rm -rf /tmp/kamar17-knowledgeappendix-clone && test ! -e /tmp/kamar17-knowledgeappendix-clone && printf 'scratch removed\n'` — exit 0.

Installs: none.