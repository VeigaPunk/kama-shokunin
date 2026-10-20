VERDICT: partial — the four C2 predicate repairs are identifiable, but the +345-line producer change also adds provenance, listener-policy and diagnostic surface; compatibility is narrower than unchanged v1 behaviour.

# Scope, axes and authority

Attacked: growth and behavioural lineage of `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py`, strictly the producer diff from `cff9e62f05aa7cfb9059444f62eb787100719713` to `54a29268e2083caa2b1e0d54ee1e7d90961302f3`. This is advisory reconstruction, not a round-admission judgment. I did not inspect the gate implementation, run controls, import the producer, or start any runtime/server.

Axes: predicate fidelity; provenance/intent fidelity; v1 behavioural continuity; added implementation surface. These are analysis axes, not new shokunin claims or scores.

Semantic navigation limitation: `read xd://lsp` returned **“No such tool: xd://lsp”** and listed no mounted LSP device. No server could be started or queried, so there was no cold-index result to mistake for absence. The two single-file searches recorded below are literal navigation only, not semantic-reference proof. Definitions and their actual in-file call expressions were then read directly; I make no repository-wide caller/implementation claim.

## Source identity

- Requested diff: **477 insertions, 132 deletions, net +345; 1078 → 1423 lines**. The zero-context diff and the ordinary diff agree on the changes; the former is not an additional implementation revision.
- Baseline Git blob: `16c38b51b38975f6efa78d78bdadfdf23aec7208`; baseline SHA-256: `b8c5e8d402595f3b919ea82f29c87f9a2b5d5c2d88bccffa48f1f8880c2f4fe4`.
- Analyzed current-file Git blob: `07c3b61f472100acd95d5b6b2c99f221d4db2126`, matching the requested diff's new blob; SHA-256: `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`.
- Frozen-copy provenance: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/manifest.json:3-4,25-28`, quote: `"source_commit": "cff9e62f05aa7cfb9059444f62eb787100719713"`. Its actual Git blob and SHA-256 match the baseline. Frozen-file line numbers below therefore identify the old producer, not a reconstructed approximation.

# 1. Reconstructed contract: four predicates plus a cross-cutting fault repair

The four predicates are **health_ready**, **teardown_graceful**, **teardown_port_closed**, and **loading_envelope_graded**. Receipt-on-internal-fault is a fifth requirement, but **not** a twelfth check. The successful check set grows 10 → 11 because graceful replaces exited, health/closure retain their IDs, and loading is the sole net-added check.

## Health: status-only becomes parsed-document equality

Old evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py:936-939`, quote: `health_status == 200`.

New evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:62-64,1168-1179`, quote: `health_status == 200 and health_body == HEALTH_READY_BODY`.

The new code JSON-parses the ready capture, compares the entire parsed object with `{'status': 'ok'}`, and records parsed body plus expected body. Thus whitespace does not matter, but a degraded body, a non-object or an extra object key fails. Parse failure leaves `None` and fails. This is the small executable health repair, supported by the new constant and changed DOC citation.

Important unchanged distinction: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:599-606,659-663`, quote: `transitions[-1]['status'] == 200`. The readiness loop still exits on **status**, not exact health-body equality; the new predicate grades a later ready capture. A wrong 200 does not become a setup/readiness timeout: it becomes a failed check if the remaining run completes.

## Graceful teardown: reaping becomes a particular harness action/outcome

Old evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py:1024-1028`, quote: `receipt['teardown']['returncode'] is not None`.

New evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:749-756,776-802,1311-1332`, quote: `and td.get('returncode') == 0`.

`teardown_graceful` requires all five: live child at teardown start, SIGTERM successfully delivered, no successfully delivered SIGKILL, return code 0, and recorded listener ownership `child`. `_child_running()` obtains a fresh `poll()` rather than trusting cached `returncode`; signal flags move after successful `killpg()` calls. SIGKILL escalation rechecks liveness. These additions serve both the predicate and process-safety intent. A cached-self-exit or kill-required child is no longer equivalent to successful teardown.

This is stronger evidence of harness participation, not proof that no other sender affected the process. The pinned return-zero code is embedded at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:901-938`, quote: `'    return 0;\n'`. It is not a general Python promise that SIGTERM exits zero.

## Port closure: refusal alone becomes refusal AND recorded ownership

Old evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py:1029-1032`, quote: `receipt['teardown']['port_refuses'] is True`.

New evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:759-768,1333-1341`, quote: `and receipt.get('port_listener_ownership') == 'child'`.

The connection-refused test is extracted to `_port_refuses()` without changing its success/error classification. The predicate, not that network operation, becomes stricter. The ownership value is **the latest recorded value**, not an immutable “ever owned” fact: assignments after each liveness gate can overwrite it (`:1159-1162,1208-1218`). No independent ownership recheck is added immediately inside teardown. In ordinary completion, the last post-probes result is `child`; a detected child exit sets `unproven`.

## Loading: informational first sample becomes a required retained-body grade

Old evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py:173-189,920-922`, quote: `None when no 503 was seen. Not a check.`

New evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:205-243,554-576,1143-1154,1342-1356`, quote: `and loading_envelopes_all(bodies) is True`.

The old parser is factored into `_envelope_ok()`. The old first-body field and its True/False/None grade keep their semantics. New `_BodyLog`, hash-index map, repeat counters, return-tuple member, receipt array and counter carry distinct 503 bodies from both readiness phases into the new check. Only retained bodies are graded. Every retained body must have message `Loading model`, type `unavailable_error`, and an actual integer code 503; empty observation fails. This parser checks those fields, not exact object-key equality, just as the old informational parser did.

Call-chain reconstruction from displayed expressions: `_observe()` appends/deduplicates → `readiness_loop()` returns the body list → `main()` records it → `loading_envelopes_all()` applies `_envelope_ok()` in final check assembly. The only displayed producer caller of the changed readiness return tuple is updated to six elements. This is direct source reading, not an LSP-derived call graph.

## Fault containment: substantial work, but not another lifecycle predicate

Old failure chain: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py:1019-1026`, quote: `receipt['teardown'] = {'error': f'{type(exc).__name__}: {exc}'}`. An error-only dict was subsequently indexed for missing returncode.

New chain: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1256-1383`, quote: `receipt['internal_fault'] = f'internal:{internal_fault}'`.

The additions independently guard signal masking, teardown, last-chance child SIGKILL/reaping, fallback port probing, check/rehash assembly and exit computation. The fallback teardown dict has usable fields, failed checks can be assembled with `.get()`, internal faults force exit 2, and an existing setup error is preserved while `internal_fault` records the additional failure. Log reduction gains unlink-in-finally (`:807-826`). The emission section gains an `Exception` handler and encloses timestamp/write in the handler-restoration `finally` (`:1389-1418`). These are fault-evidence and cleanup changes, not only changes to boolean formulas.

Bound of the advertised guarantee: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1391-1418`, quote: `if not emitted:`. An emission exception is logged and returns 2 without a retry in the generic-exception arm; timestamp creation and handler restoration have no enclosing `except`. [INFERENCE] The diff repairs the known teardown→KeyError loss, but does not establish the docstring's universal “any exception ... still writes a receipt” statement. I did not fault-inject these paths.

# 2. Where the 345 net lines went

These are **net line deltas of the displayed diff-hunk groups**, not exclusive estimates of design effort. Shared scaffolding is grouped by location; wrapping/movement is included.

| Hunk group | Net lines | Current evidence location |
|---|---:|---|
| Header/schema, upstream constants, body cap and DOC changes | +32 | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:18-151` |
| Envelope helper extraction, all-bodies helper, `_BodyLog` | +22 | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:205-243` |
| Listener-address filter and its explanation | +15 | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:311-343` |
| Readiness body capture/return plumbing and body discard | +24 | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:505-624` |
| Child-exit ownership token normalization | 0 | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:632-633` |
| Teardown helpers, signal records and log-cleanup restructuring | +23 | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:749-827` |
| Source-binding construction/data block, including separator lines | +106 | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:835-940` |
| Receipt fields and launch/readiness-result wiring | +10 | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1069-1081,1137-1154` |
| Executable health-body check | +8 | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1168-1179` |
| Final checks, fault handling/backstop and emission restructuring | +105 | `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1250-1419` |
| **Total** | **+345** | **477 − 132 = 1423 − 1078** |

Thus about 31% of the net growth is the 106-line source-binding block alone. The source-binding and finalization groups account for 211 of 345 net lines. It is inaccurate to describe the growth as merely four longer predicate expressions.

# 3. Additional surface and bounded divergences

## Source binding is new provenance output, not a new server capability

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:843-938,1081`, quote: `Plain data; never executed, never network-read.`

Five entries bind three check IDs to five source spans: one health span, one loading span, three graceful-exit spans. Each carries commit, upstream path/URL, line interval, claimed file digest, literal source text and a hash computed from that literal. Loading names S036; health and all graceful spans have `row: null`. The tool itself performs no upstream fetch here, no local source-file verification, and no executable-to-upstream-commit authentication; it embeds attribution for the b11755 contract alongside the caller-selected binary's separate digest. No closure predicate is added by this block.

The nulls are not evidence that S042/S043 remained unregistered. `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:74-79`, quote: `the rows did not exist when the tool was written.` This records a writing-time snapshot retained in the final producer, rather than a live source-registry lookup.

Two source-description corrections did **not** flow back into the producer:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:118-124`, quote: `the documented graceful exit status`; `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:64`, quote: `the claim is code-derived`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:60-61` still embeds the moving `/3/` Python-doc URL. `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:66-67` adopts `/3.14/` and rejects `/3/`.

These are provenance/documentation drift, not demonstrated runtime regressions.

## Loopback filter is a separate acceptance-policy change

Old evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py:257-269`, quote: `if int(parts[1].rsplit(':', 1)[1], 16) == port:`.

New evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:311-339`, quote: `elif not addr_hex.endswith('7F'):`.

Previously a child-owned wildcard listener could satisfy the ownership test by port and inode. The new filter discards wildcard/non-loopback candidates before inode ownership is examined. [INFERENCE] A wrapper ignoring `--host 127.0.0.1` and binding only `0.0.0.0` now fails with ownership unproven instead of qualifying as a child owner. This is additional policy beyond conjoining existing ownership with closure. It does not change the harness's actual `--host 127.0.0.1` launch argument.

Intent is explicitly recoverable: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/SentinelLiveSafety.md:72-79`, quote: `the local address field of /proc/net/tcp is ignored`; `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/C2LiveTool.md:178-182`, quote: `loopback-only listener accounting`. It is not an unexplained accidental edit, though it is outside the four predicate formulas.

Static boundary: the IPv6 branch at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:331-335` uses a suffix test, not full `::1` identity, and compares `addr_hex[:24]` against the 22-character literal `0000000000000000FFFF00`. [INFERENCE] The advertised mapped-IPv4 branch cannot match a conventional 32-character address field. I did not exercise IPv6 or validate kernel byte-order representations. Also, filtering acceptable sockets is not a proof that the child owns no additional wildcard socket.

## Body log strengthens coverage but introduces a non-failing coverage ceiling

Evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:75,554-567,1342-1356`, quote: `loading_bodies.dropped += 1`.

New raw-body output is SHA-256-deduplicated, capped at 256 retained bodies, with repeated observations counted and the first path attached. Each retained body is a UTF-8-replacement-decoded prefix of at most 4096 bytes; its digest was calculated on the HTTP read buffer, not that decoded prefix. The old single-body output remains, but additional body retention and counters are genuinely new receipt surface.

`loading_bodies_dropped` is **reported, not included in pass/fail**. `total_503_responses` sums retained entries and repeats, excluding dropped observations. [INFERENCE] A producer-only counterexample is 256 byte-distinct valid envelopes (whitespace variants suffice), then a wrong envelope, then otherwise-correct readiness/probes/teardown: the wrong 257th body is counted as dropped and the loading check still sees an all-valid retained list. This is not an executed witness and I make no claim that the final gate accepts it. The literal final lesson says “every stored 503 body” (`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:40`); that narrower statement is supported. An uncapped “every observed response” account is not.

# 4. Did v1 behaviour change silently?

**The common launch/probe contract remains; the producer is not behaviourally identical.** Do not equate accepting historical v1 receipts with preserving every v1 producer behaviour.

- **Preserved invariant:** required CLI arguments/defaults, digest rejection before launch, refusal-set parsing and port selection, argv/env allowlist, HTTP proxy/redirect policy, probe invocation and its six unrelated server/probe check formulas are unchanged in the requested diff. The model rehash predicate is unchanged; only its DOC is relabelled. Evidence examples: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:246-308,949-969,1017-1023,1088-1104,1181-1237,1357-1365`, quote: `'--host', '127.0.0.1'`.
- **Declared, not silent:** schema changes v1 → v2 (`:50,947`), `teardown_exited` is removed rather than aliased, health and closure tighten, loading becomes required. Historical v1 gate compatibility is a different file's obligation; I did not independently verify it.
- **Policy changed during the build:** the dispatch initially permitted **no loading observation** to pass. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/spec.json:24`, quote: `if none observed, pass`. Final code requires loading observation (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1345-1348`), while its DOC explicitly says no 503 fails (`:140-141`). The author records `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/C2LiveTool.md:42-47`, quote: `This is L1's ruling`. Thus a fast-ready or missed-loading run changes from eligible-for-success to failed check. It is disclosed in final code/report, not unchanged v1 behaviour and not unexplained intent.
- **Existing field meanings tighten:** the old signal booleans were set before attempted delivery (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py:663-676`); the same names now mean successful delivery (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:780-795`), quote: `recorded only on delivery`. Names are retained but their error-path semantics are not identical.
- **Adjacent v1 shape bug is intentionally repaired:** `verify_live()` changes child-exit ownership from `None` to `unproven` (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py:539-540` → `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:632-633`); default ownership is also present before launch (`:1080`). This was requested by the exception-path review, not required by exact health/body grading: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/ScoutLiveToolExceptionPaths.md:114-116`, quote: `an error-return path that silently breaks the receipt schema`.
- **Failure receipt check composition changes:** old teardown checks were conditional on a non-null teardown (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py:1023-1032`). New finalization appends graceful/closure/loading even when teardown is absent (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1310-1356`). [INFERENCE] After a log-mkstemp failure, the ordinary failure receipt now has those three failed checks plus model integrity instead of only model integrity. Setup-error exit 2 remains unchanged.
- **Small silent documentation regression:** the header loses its exit-3 entry (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:16-24`), but runtime digest mismatch still returns 3 (`:1017-1023`) and argument help still promises it (`:953-954`), quote: `mismatch -> exit 3`. This is not an actual exit-code migration.

# 5. Timeline of intent

There is only **one** commit touching this producer between the assigned endpoints. The sequence below separates observed revision history from design-document dependency order; I do not invent timestamps for individual uncommitted edits.

1. **Initial round-16 acquisition:** `b8e485cc6b201c8e4604a20808e58babbfe08e34`, committed `2026-10-20T10:50:49-03:00`, adds a 989-line lifecycle producer. Git subject: “MODEL_LOADING verdict ... and live llama.cpp lifecycle capability”.
2. **Round-16 hardening:** `726f737a942f1606d66e032f1efbcbb6f689ccf1`, committed `2026-10-20T11:10:32-03:00`, +187/−98 leaves 1078 lines. The last-known-good invariant is the owned ephemeral launch/capture/probe/reap workflow, not that all named checks already proved their descriptions.
3. **Known divergence carried into round 17:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md:23-34` reports degraded health passing, wrong loading envelope passing, kill-required exit passing and receipt loss. Short quote: `receipt_written False`. This is inherited empirical evidence, **not my rerun**. Its reviewed 1078-line SHA equals the assigned frozen baseline (`:3-11`).
4. **Initial round-17 task:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/spec.json:24` specifies the four predicates, receipt-on-fault, preserved input-integrity field and source citations; it initially permits no observed loading and calls return-zero “documented”. The parallel gate task (`:29`) explicitly requires an unchanged historical-v1 path. Neither task initially requires a five-span `source_binding` array.
5. **Evidence/safety elaboration before final producer:** source pinning reconstructs the signal→shutdown→zero chain (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/SourcePinsTeardown.md:80-83`, quote: `a second signal forces exit(1)`); the critic asks for fresh `poll()` and delivered-signal flags (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/CriticSourcedClaim.md:53-58`, quote: `A residual race between poll() and killpg remains`); the sentinel requests backstop kill, independent log cleanup, outer handler restoration and socket-address evidence (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/SentinelLiveSafety.md:62-79`, quote: `Put the log os.unlink(log_path) in its own finally`). The final author report explicitly attributes incorporated safety additions (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/C2LiveTool.md:178-183`).
6. **Final build policy/producer:** the author records L1's no-observation-fails decision, all-body retention, metadata spans and null source rows. The producer is 1423 lines and the digest matches the analyzed file (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/C2LiveTool.md:7-9,42-47,77-89`). Some author-report limitations concern an intermediate gate; I do not treat them as evidence about the final gate.
7. **Single landing:** `54a29268e2083caa2b1e0d54ee1e7d90961302f3`, author date `2026-10-20T11:50:45-03:00`, committer date `2026-10-20T13:24:57-03:00`, lands the entire +477/−132 producer change. Final lesson records S042/S043's later registry naming and narrows wording to stored bodies (`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:31-42,74-79`). The tool still retains the earlier “documented” and moving-doc-URL wording noted above.

# Commands, exits and limits

All shell calls below returned success/overall exit **0**, including cleanup. For the initial compound commands, individual subcommand statuses were not separately captured; the status recorded is the overall shell call. No lane tool, gate, counting script, Python interpreter, fake or llama-server was executed. Consequently the clone-and-checkout prerequisite for executing lane code was never triggered.

Exact shell commands, in invocation order:

1. Exit 0:
```sh
cd /home/vgpnk/Projects/shokunin/kama-shokunin && git diff --stat cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tools/kama-llamacpp-live.py; echo "--- old lines:"; git show cff9e62:tools/kama-llamacpp-live.py | wc -l; echo "--- new lines:"; git show 54a29268e2083caa2b1e0d54ee1e7d90961302f3:tools/kama-llamacpp-live.py | wc -l; echo "--- commits touching file:"; git log --reverse --pretty='%h %ad %s' --date=iso cff9e62..54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tools/kama-llamacpp-live.py
```
2. Exit 0:
```sh
grep -n "Declared claims\|Measurements\|C2" /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md | head -40
```
3. Exit 0:
```sh
cd /home/vgpnk/Projects/shokunin/kama-shokunin && git diff cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tools/kama-llamacpp-live.py > /tmp/kamarevengertoolgrowth-diff.txt && wc -l /tmp/kamarevengertoolgrowth-diff.txt && grep -c '^+' /tmp/kamarevengertoolgrowth-diff.txt && grep -c '^-' /tmp/kamarevengertoolgrowth-diff.txt && grep -n '^@@' /tmp/kamarevengertoolgrowth-diff.txt
```
4. Exit 0:
```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -8 --format=fuller 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tools/kama-llamacpp-live.py
```
5. Exit 0:
```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin hash-object /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py
```
6. Exit 0:
```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --unified=0 cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tools/kama-llamacpp-live.py
```
7. Exit 0:
```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show cff9e62:tools/kama-llamacpp-live.py
```
8. Exit 0:
```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --reverse --format='%H%nAuthorDate: %aI%nCommitDate: %cI%n%s' --numstat b8e485cc6b201c8e4604a20808e58babbfe08e34^..54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tools/kama-llamacpp-live.py
```
9. Exit 0:
```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin hash-object /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py
```
10. Exit 0:
```sh
sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py
```
11. Exit 0:
```sh
git --no-pager -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --no-ext-diff --numstat cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tools/kama-llamacpp-live.py
```
12. Exit 0, scratch removed:
```sh
rm -- /tmp/kamarevengertoolgrowth-diff.txt
```

Other evidence operations were `functions.read`, bounded `functions.glob`, and these exact `functions.grep` searches (successful tool results; no process exit code):

- Path `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md`, pattern `Round 17`.
- Path `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py`, pattern `loading_bodies_dropped|loading_envelopes_all|port_listener_ownership|source_binding|readiness_loop\(|verify_live\(|_listen_inodes\(|_child_running\(`.
- Path `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/spec.json`, pattern `C2LiveTool|loading_envelope_graded|source_binding|loopback`.

All grep operations were against named individual files, not recursive directory searches. The first two shell batches used shell grep/head/redirection rather than the required specialized search/read/write devices; disclosed here as a tooling-bound deviation, not semantic evidence. The temporary diff filename also used a shortened seat spelling; that sole scratch file was removed by command 12. No other scratch was created.

No prohibited session/history/credential store was accessed. No Git write or jj command was run. No port was bound or contacted, so there was no owned listener to tear down or check with `ss`. The only lane write is this requested Report.

Verification exercised: static source/diff inspection and read-only identity/count commands only. Gate compatibility, fault controls, mutant counts and real-run validity are inherited author claims, not results independently exercised by this seat. No installs or updates; pacman untouched.

Confidence: **high** for the line accounting, predicate/call-expression reconstruction, explicit v1 deltas and documented intent changes; **medium** for dependency ordering within the single landing; **unexercised [INFERENCE]** for the overflow witness, IPv6 operational consequences and residual exception reachability. Assigned legacy surface complete.
