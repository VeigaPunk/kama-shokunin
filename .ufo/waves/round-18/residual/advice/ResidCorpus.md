VERDICT: partial — append-only, every pinned-byte/receipt/census claim I re-opened reproduces, but the ownership 3d bullet falsely says the `source:` line gained the S049/S050 anchors (it is byte-identical and carries none), and two pointers are imprecise.

# Evidence (all executed in /tmp/kama-r18-res-ResidCorpus = `cp -a` of the lane; lsp not mounted, `read xd://lsp` -> "No such tool", so grep/read are literal fallback)

## Append-only
`git diff 101f3991 --numstat -- <3 files>` -> `21 0`, `43 0`, `59 0`. Raw diff 147 lines, `grep '^-'` excluding `---` headers -> NONE. Hunk headers are tail-only: `@@ -286,3 +286,24 @@`, `@@ -87,3 +87,46 @@`, `@@ -246,3 +246,62 @@`. Line counts pre->post: 89->132, 288->312, 248->307. No rewritten byte.

## Byte claims re-opened (all grounded unless marked)
- S048: `sha256sum .ufo/waves/round-18/sources/raw/linux/v7.2/net/ipv6/tcp_ipv6.c` = `dd3f400b…0558`; seq_printf at 2172-2179 with `src->s6_addr32[0..3]` at 2176-2177; `awk 2126..2198 | grep 'ntohl|htonl|swab|cpu_to'` -> NONE.
- `linux-in6.h` sha `4b70a423…b27d`; line 38 `__be32 u6_addr32[4];`.
- S049 `proc_net_tcp.rst`: line 8 "deprecated in favor of tcp_diag", line 12 "tcp6_seq_show() in net/ipv6/tcp_ipv6.c".
- S050 rfc4291 (sha `4d58dff6…48b2`): 474 loopback sentence; 548 §2.5.5.2 header; 550-552 mapped text; 570 `|0000…|FFFF|` layout.
- Case D: `ProbeTcp6Format.md:186` binds `::` `IPV6_V6ONLY=0`; `:200` `*:56483`; run 2 `:690`/`:704` `*:40909`; `:5` "only loopback listeners" present; `:766` confirms run 2.
- `ProbeArgvEffects.md:81` `unshare -rn`; `:384-385` LISTEN row + `{"_listen_inodes":[],"port_owned_by":null}`.
- Prior overlap: `llamacpp-loading-lifecycle.md:112-113,197` (ownership before probes; teardown_port_closed requires it).
- Tool race: `:612` `conn.get('/v1/models')` evaluated as `_observe` arg; `port_owned_by` at `:574` inside `:572-579`; docstring `:542-545`; parser unconditional reversal `:311-321`.
- 3f: selftest `:1053-1082` binds real `::1`/`::ffff:127.0.0.1` and checks `_listen_inodes`/`_tcp6_is_loopback`; receipts port 46769, `port_listener_ownership=child` (IPv4 dial).
- Receipts 1-3 (worktree and checkpoint receipt-1): `teardown.returncode=0`, `sigkill_sent=false`, `sigterm_sent=true`; tool `:807-821` issues one `killpg(SIGTERM)` then optional SIGKILL.
- Five-pin: `runs/run.py:48` passes model/server/server-impl/probe/tool `--expect-*`; `runs/commands.json` indices 13/15/17 carry `--expect-server-impl-sha256 e404b91a…`; that equals receipt-1 `server.server_impl_sha256` and `sha256sum /home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so`. Gate arg `check-receipt.py:2133`, enforcement `:387-395`; flagless `allow_none=True` still records tree/impl hashes.
- Window: `server.cpp:515` `is_ready.store(true)`, `:534` `sigaction(SIGTERM)`; `server-queue.cpp:279` `running = true` (lifecycle `:216-217`).

## Census
`census --root … kama` exit 0: rows 56, tier.A 53, tier.C 3, mined 45, queued 5, rejected 6 — identical to `census-after.txt` except its appended literal `exit=0` line. `validate` exit 0: W04 S031, W04 S043, W04 S056, `kama ok`. Before (47/A44/C3, mined37/queued5/rejected5): delta +9 rows, +9 A, 0 C, +8 mined, 0 queued, +1 rejected. W04 is expected: S031/S043 are already in the 47-row file (old-file validate returned those two; its E11 lines are `--file` artifacts because used-by resolves against `dirname(file)/..`), S056 is new and shares common/arg.cpp with S054. W-codes never change status.

## Dispositions
`count-verdicts.py … --json` exit 0: 66 files, 28 confirm / 34 partial / 1 refute / 3 nonconformant, missing 10 named seats — matches the lesson. `validation.json`: policy v2, band 64-100, spec sha `ecf2668a…`, spawn 76; roles match the lesson exactly. Only refute = PrivacyScope (matches fixed table). Nonconformant bodies carry their verdict at line 3 (CounterC1 partial, GateBinding confirm, GateClaimFlags confirm) — the lesson's parenthetical is right. M8: checkpoint `c1-measure.exit`/`c2-survivors.exit` both `exit=2`, worktree both `exit=0`, selftest stdout `43/43 cases passed`. M9 matches CounterC1's "child-trusted for 3 of 4 counts". `lane-dead-no-report kama round=18` is real but external: `/home/vgpnk/Projects/shokunin/.ufo/watchdog.log:536` (nothing round-18-local records it).

# Findings
F1 (medium-low) `loopback-listener-ownership.md:117-119`: "`source:` gains `S049:8,12` and S050 §2.5.3 (line 474), §2.5.5.2 (548-552, layout 570)" is false. `git show 101f3991:<file> | sed -n 1p` equals current line 1 and contains no `S049:8,12`/`§2.5.3`; the anchors exist only inside this appended bullet (the checkpoint already carried URL anchors at lines 66-73). KQ6 is body-satisfied, but the sentence misstates the artifact; reword to name the anchor block, not `source:`.
F2 (low) `llamacpp-loading-lifecycle.md:298-299`: "[534, 279]" gives no file for 279; 534 is `server.cpp` (sigaction) and 279 is `server-queue.cpp` (`running = true`), while `server.cpp:279` is the `/v1/health` route. Lines 216-217 recover it, but KQ23 asks the interval to name both cited statements; name both files.
F3 (low) `loopback-listener-ownership.md:111-113`: "on the host" is not recorded in `ProbeTcp6Format.md` (no unshare/netns line; grep only matches Python "module namespace"). Host execution is [INFERENCE] from absent isolation, like 3a is correctly marked.
F4 (low) `lessons/round-18.md:269` cites `dispatch-95.json` for "the 20 never-assigned build members", but that file's embedded registry is 95 members all `agentId: null` and `counts.spawn=95`; the 75-assigned/20-null split is in `build/advice/swarm-registry.json`. Point there.
F5 (info) The append repeats checkpoint work: ownership 3a/3b/3c/3e already appear at `101f3991:…:75-89` (25-line section added after the falsifier read `1c325b2`), and S047 F1 was fixed in `corpus/README.md` (+17 at checkpoint, naming 534/279, in-window outcome, return0, static caveat). The lesson's "Fixed … in this attempt" row attributes those disclosures to the working-tree append; it adds exact line numbers and the endianness fix, not the first correction. No byte claim is wrong.
F6 (info) ReopenS051/S054 (both partial) are in neither the fixed nor deferred list; their corpus text is the checkpoint's lifecycle 271-280 / README 267-286. S051's SOURCES `teaches` cell still names only three exceptions (BaseExceptionGroup appears in the anchor cell and in lifecycle 278-280), so that report's "source record" item is not fully closed. No report verdict is misrepresented.

# Limits
Static review only: no counter, gate, tool, selftest, live run or listener; no network; no lane edit except this report. lsp unavailable, so reference/definition proof is literal grep, not semantic. The 3a race remains [INFERENCE] as the append says. `/tmp/kama-r18-res-ResidCorpus` deleted after this report; no installs.
