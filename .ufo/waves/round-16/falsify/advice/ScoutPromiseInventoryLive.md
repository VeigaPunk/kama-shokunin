VERDICT: partial — promise/control inventory of tools/kama-llamacpp-live.py and tests/llamacpp-live/check-receipt.py. Every refusal I exercised behaves exactly as promised, but the wave's pairing claim does not hold: 13 producer statements and 20 gate statement groups have no control in controls.txt or the gate selftest. I supplied working negative controls for 6 of the 13 producer items and for 20 of the 20 gate groups; 7 producer claims remain unpaired, one of them (the `loading -> ready` lifecycle) is also unevidenced by the two receipts.

## Axes

1. Pairing completeness: does each refusal/never statement have a control?
2. Truth of the refusal: when reached, does it refuse with the promised token/exit?
3. Evidential independence: is the control able to distinguish the promised mechanism from a nearby coincidence (e.g. registry parser vs hardcoded constant)?

## Method and counts

- Read both files in full (989 and 1014 lines).
- Producer surfaces: 11 `SetupError(...)` sites, 8 docstring invariants, 2 write/atomicity claims.
- Gate surfaces: 122 `bad(` call sites in `validate()` (measured), 16 selftest mutations (`grep -c '    mut('` → 16), 10 re-derived check ids.
- Re-ran shipped controls: `python3 tests/llamacpp-live/check-receipt.py --selftest` → exit 0; both live receipts → exit 0 `VALID`.
- Ran 9 producer controls against /tmp stubs and 32 gate receipt-mutation invocations. No real `llama-server` process was started (my item does not authorize it); no `measure.py` run.

## Producer inventory (statement → control → status)

| # | Statement (site) | Control in wave | Status |
|---|---|---|---|
| P1 | "free loopback port that is never a registered consumer port" (`tools/kama-llamacpp-live.py:6-7`) | `controls.txt` 8080/34113 exit 2; gate receipt check `port_refusal_set` | PAIRED for the two pins; registry-parser arm UNPAIRED (see P10a) |
| P2 | "captures the documented HTTP lifecycle surfaces (loading -> ready)" (`:7`) | none | UNPAIRED **and unevidenced**: both receipts `loading_observed=False`, transitions `[('/health',None,0),('/v1/models',None,0),('/health',200,0)]` |
| P3 | "no ~/.config, ~/.omp, systemd or service writes" (`:11-12`) | none | UNPAIRED in wave; my strace control: 0 forbidden write targets |
| P4 | "only filesystem artifacts are a temp … log (deleted …) and the optional --out receipt" (`:12-14`) | none | PARTIAL: post-hoc absence of both recorded logs and no `.kama-live-*` sibling; no fresh-run instrumentation |
| P5 | exit 1 "at least one check failed (server ran; receipt written)" (`:18`) | none | UNPAIRED in wave; my srv-bad run → exit 1, receipt written |
| P6 | exit 3 "model digest mismatch (refuses to launch)" (`:21`) | `digest_mismatch_exit=3` | PAIRED |
| P7 | "Only argv is recorded from the launch environment — never env" (`:23-24`) | gate selftest `env-key-off-allowlist` + allowlist check | PAIRED (names); no env-value field exists |
| P8 | "Ports that must never be served even if the OS offers them" (`:55-56`) | `registered_port_8080_exit=2`, `registered_port_34113_exit=2` | PAIRED for pins; default-pick retry (`:254`) UNPAIRED |
| P9 | "names are recorded, values never are" (`:72`) | gate selftest | PAIRED; "server sees only these names" is self-attested only (UNPAIRED, see U6) |
| P10 | `registry-unreadable` (`:200`) | none | UNPAIRED; my lane copy → exit 2 |
| P10a | "plus anything the registry TSV names (parsed at runtime)" (`:55-56`, `:196-226`) | none | UNPAIRED: `refused_ports()` returns exactly `[8080, 34113]` on the real registry, so controls cannot attribute anything to the parser; my scratch-registry control proves it works |
| P11 | `explicit-port-out-of-range` (`:236`) | none | UNPAIRED; my `--port 0` / `--port 70000` → exit 2 |
| P12 | `port-refused-registered` (`:238`) | controls 8080/34113 | PAIRED |
| P13 | `port-in-use` (`:246`) | `listening_port_631_exit=2` | PAIRED |
| P14 | `no-free-unregistered-port` (`:254`) | none | UNPAIRED (64 attempts must all land in the refused set; not simulated) |
| P15 | `port-listener-not-our-child` (`:439`, `:459`) | none | UNPAIRED; my foreign-listener stub → exit 2, `setup_error=port-listener-not-our-child` |
| P16 | `port-listener-ownership-unproven` (`:440`, `:460`) | none | UNPAIRED (needs unreadable `/proc`); producer does emit `'unproven'` in my setup-error receipt |
| P17 | "SIGTERM … SIGKILL after TERM_GRACE, then prove the port refuses" (`:573`, `:599`) | receipts + `post_pgrep_llama_server=0`/`post_ss_8080_34113=0` (TERM arm) | PARTIAL in wave; SIGKILL arm UNPAIRED — my TERM-trapping stub gave `sigkill_sent=True`, `term_wait_ms=10001` |
| P18 | "die with SIGKILL if the harness parent dies" pdeathsig (`:297`) | none | UNPAIRED (`prctl_ok=True` is recorded, not controlled) |
| P19 | "block SIGINT/SIGTERM/SIGHUP during teardown" R2 (`:942`) | none | UNPAIRED; my SIGTERM run proves handler+teardown completes, not the ignore window |
| P20 | "At most HTTP_BODY_CAP+1 bytes are read" (`:332`), log caps (`:65-70`), `PROBE_TIMEOUT` (`:58`) | none | UNPAIRED (no oversized fixtures) |
| P21 | "atomic publish: sibling temp file + os.replace" (`:670`) | none | UNPAIRED; observed no temp sibling in 5 `--out` runs (weak) |
| P22 | proxy-disabled opener, "no proxy vars can redirect it" (`:326-327`) | gate env allowlist (indirect) | UNPAIRED directly |

Shipped producer controls fully cover 5 of 22 statements (P6, P7, P9, P12, P13) and one arm of 3 more (P1 pins, P8 pins, P17 TERM); the other 14 are unpaired.

## Gate inventory (statement → control → status)

| # | Statement (site) | Control in wave | Status |
|---|---|---|---|
| G1 | "Every claim is re-derived … a bare `passed:true` is never trusted" (`check-receipt.py:16-17`) | 16 selftest mutations + my 23 evidence mutations | PAIRED |
| G2 | each check exactly once, all passed, exactly 10 ids (`:520`, `:528`) | selftest missing/duplicated | PARTIAL: extra id and `passed:false` UNPAIRED; my controls exit 1 |
| G3 | `setup_error` must be null (`:167`) | none | UNPAIRED; my control exit 1 |
| G4 | timestamps parse, ended ≥ started (`:172-180`) | selftest ended-before-started | PARTIAL: unparseable started UNPAIRED; mine exit 1 |
| G5 | alias non-empty, ctx/threads positive (`:186`, `:190`) | none | UNPAIRED; my ctx-0 and alias-"" controls exit 1 |
| G6 | port range, hard pins, not inside own refusal set, sorted, unique (`:198`, `:208`, `:214`, `:217`, `:219`) | selftest port-34113, port-inside-refusal-set | PARTIAL: out-of-range, missing pin, unsorted, duplicate UNPAIRED; my 4 controls exit 1 |
| G7 | server block digests and install_tree basename (`:229-256`, `:249`) | none | UNPAIRED (no negative control at all) |
| G8 | model/probe digests, `--expect-*` flags (`:264-300`, `:278`) | selftest wrong-digest-vs-expect | PARTIAL: malformed `--expect` UNPAIRED; mine exit 1 |
| G9 | child_env allowlist, sorted unique (`:303-315`, `:313`) | selftest env-key-off-allowlist | PARTIAL: sorted/unique UNPAIRED; mine exit 1 |
| G10 | argv alias/port/host/c/t/tail (`:320-333`, `:323`, `:331`) | selftest argv-missing-offline | PARTIAL: alias, port, `--host` UNPAIRED; my 3 controls exit 1 |
| G11 | loading_observed/loading_503 consistency (`:345`, `:347`) | none | UNPAIRED; my 2 controls exit 1. **Cross-check transitions↔loading is absent** (see F2) |
| G12 | port_listener_ownership vocabulary, "foreign" rejected (`:363-368`) | none | UNPAIRED; my foreign→exit 1, unknown→exit 0, unproven→exit 1. Vocabulary skew, see F3 |
| G13 | transitions array present, captures keys present (`:371`, `:380`) | none | UNPAIRED; my 2 controls exit 1 |
| G14 | probe row verdict/exit/drift/expect/declared/summary (`:445`, `:479`) | selftest model-ok-claimed-exit-2, passed-flipped, mismatch-probe-expects-alias | PARTIAL: declared endpoint and summary skew UNPAIRED; mine exit 1 |
| G15 | teardown block shape/returncode/port_refuses (`:487-500`) | selftest missing-teardown | PARTIAL: `port_refuses:false` UNPAIRED; mine exit 1 |
| G16 | re-derive health/models alias/owned_by/props aliases (re-derive blocks after `obs()`) | selftest metrics-200 only | PARTIAL: health, alias, owned_by, props UNPAIRED; my 4 controls exit 1 |
| G17 | re-derive teardown_exited/teardown_port_closed | selftest missing-teardown | PARTIAL: port-open fact UNPAIRED; mine exit 1 |
| G18 | model_unchanged incl. rehash-error (`:687-688`) | selftest model-changed-post-digest | PARTIAL: rehash-error UNPAIRED; mine exit 1 |
| G19 | unreadable receipt → exit 2 (`:994-999`) | selftest unreadable case | PAIRED; not-JSON also mine exit 2 |

Summary metric: 16 selftest mutations against 122 refusal sites (~13%). Of the 19 gate statement groups, 2 are fully paired (G1, G19), 11 are only partially covered, and 6 have no selftest control at all (G3, G5, G7, G11, G12, G13). Producer: 5 statements fully paired (P6, P7, P9, P12, P13), 3 paired only for one arm (P1, P8, P17), 14 unpaired.

## Flagged: unpaired / unsupported

**F1 — the loading lifecycle promise has no control and no artifact.** `tools/kama-llamacpp-live.py:7` promises "captures the documented HTTP lifecycle surfaces (loading -> ready)", but both L1 receipts record `loading_observed=False`, `loading_503=null`, `loading_envelope_exact=null`, transitions `[('/health',None,0),('/v1/models',None,0),('/health',200,0)]`. The 10/10 receipt therefore demonstrates ready capture, never loading; nothing in `controls.txt` asserts the loading surface. FamilyLoadingRace may own the calibration side, but the operability claim is unpaired here.

**F2 — gate does not cross-check `transitions` against `loading_503`.** I appended a 503 transition row (documented envelope body) to a valid receipt while leaving `loading_observed=false`/`loading_503=null`: gate exit 0. Stored evidence contradicts the stored claim; the validator accepts it. The two consistency rules at `:345`/`:347` only compare the two loading fields to each other.

**F3 — producer/gate ownership vocabulary skew, observed in a real producer artifact.** Gate allows `child|foreign|unknown` (`check-receipt.py:363-365`); the producer emits `child|foreign|unproven` (`:851`, `:461`). My stub-exit run produced a receipt with `port_listener_ownership='unproven'`, which the gate rejects with "not in child|foreign|unknown". Latent only (every such receipt also carries `setup_error`), but `unknown` is vocabulary no producer path can emit.

**F4 — R1 foreign-listener gate was uncontrolled.** It is the only thing preventing a stranger listener (e.g. after the bind(:0)/rebind race) from having its `/health` and model surfaces attributed to the pinned binary/model, and `controls.txt` has no case for it. My control now supplies one (see run 7).

**F5 — registry-parser arm indistinguishable in the real lane.** `refused_ports()` measured as `[8080, 34113]`, identical to `HARD_REFUSED_PORTS`; both controlled refusals (8080, 34113) are explained by the constant alone. My copy-lane control is the only evidence the TSV parser is live.

**F6 — remaining unpaired producer claims:** no-writes (P3, now straced but not a shipped control), pdeathsig (P18), R2 ignore window (P19), body/log/timeout caps (P20), atomic publish (P21), `no-free-unregistered-port` (P14), `ownership-unproven` (P16).

**F7 — gate selftest coverage is narrow relative to the validator.** Items with no selftest mutation at all include: `setup_error` non-null, health≠200, alias/owned_by/props mismatches, `teardown_port_closed=false`, ownership vocabulary, hard-pin membership, refusal-set ordering, argv alias/port/host, declared endpoint, missing captures, garbage timestamps, ctx/alias scalars, non-JSON receipts, malformed `--expect`. All of these do reject correctly when I supply the mutation — the gap is control coverage, not behaviour.

## Controls actually run (command → exit → excerpt)

Producer (stub server, real GGUF sha `270cba1b…`, ports never 8080/34113 except the refusal path):
1. `--port 0` → 2 · `kama-llamacpp-live: explicit-port-out-of-range`
2. `--port 70000` → 2 · same token
3. `--port 8080` → 2 · `port-refused-registered:8080`
4. lane copy with scratch registry row `…:45678` + `--port 45678` → 2 · `port-refused-registered:45678`
5. lane copy without registry + `--port 45679` → 2 · `registry-unreadable:/tmp/…/registry/endpoint-consumers.tsv`
6. stub exits 1 immediately → 2 · receipt `setup_error='server-exited-early-rc1'`, `ownership='unproven'`, `teardown={returncode:1,port_refuses:True}`; gate on it → 1 `INVALID`
7. stub whose grandchild binds the port but whose own pid does not → 2 · `setup_error='port-listener-not-our-child'`, `ownership='foreign'`, transitions `[('/health',None,1),('/v1/models',None,1),('/health',200,0)]`, `teardown.port_refuses=True`, rc −15
8. TERM-trapping stub + SIGTERM to harness → 2 · `setup_error='terminated:signal 15'`, `teardown={returncode:-9,sigkill_sent:True,term_wait_ms:10001,port_refuses:True}`
9. self-binding stub with wrong model id/owner/props/metrics → 1 · all 10 checks present, 5 false; gate → 1 `INVALID`
10. same stub under `strace -f` → 1 · 16 write targets, `forbidden_write_targets=[]` (all under `/tmp`, `/dev/null`, `/dev/tty`)

Gate:
- `--selftest` → 0 · `selftest: 16 mutations + unreadable case all rejected; valid receipt accepted`
- `receipt.json` → 0 `VALID`; `receipt-frozen-probe.json` → 0 `VALID`
- 32 mutation invocations: 29 reject as promised (exit 1, or exit 2 for the non-JSON receipt), 1 by-design accept (`ownership=unknown` → exit 0), 1 defect accept (F2, exit 0); one initial "loading false" case was a no-op (the receipt has no 503) and was replaced by 2 valid loading controls (exit 1 each)
- non-JSON receipt → 2; malformed `--expect-model-sha256 ZZZZ` → 1
- `refused_ports()` import → `[8080, 34113]`
- after every run `pgrep -x llama-server` empty (exit 1); final `ss -ltn | grep :(8080|34113)` empty (exit 1). One transient pgrep hit (pid 39645) was the concurrently running signal-test stub, not a leak; both were reaped and the final check is empty.

## Limitations

- I did not start the real `llama-server` (item not authorized) and did not run `measure.py` (prohibited). Producer controls exercise harness code with stubs; they do not validate llama.cpp's own behaviour.
- `ownership-unproven` requires an unreadable `/proc`, and `no-free-unregistered-port` requires exhausting 64 picks; neither was simulated.
- Caps (body 64 KiB, log tail 64 KiB, 200 kept lines, 60 s probe timeout) have no oversized fixture; only source reading supports them.
- strace covered `openat/open/creat/unlink/unlinkat/rename/renameat/mkdir/mkdirat`; writes through inherited fds (stdout/stderr, `/dev/tty`) are not path-attributed. `/dev/tty` opens were probe children hitting ENXIO.
- Receipts are self-attested for `install_tree`, `teardown`, `child_env_keys` enforcement and `pdeathsig`; the gate cannot see the child's real environment.
- F1 is a claim-vs-artifact mismatch, not a broken refusal; it may overlap FamilyLoadingRace's item and should be de-duplicated by L1.

## Installs

None. `strace` was already present (`/usr/bin/strace`); no package manager transaction was attempted.
