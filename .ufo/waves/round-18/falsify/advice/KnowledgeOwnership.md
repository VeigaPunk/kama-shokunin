VERDICT: partial — the entry is genuinely new *corpus* knowledge and its kernel/encoding claims check byte-exactly, but its Limits understate the first-response/ownership race and the round's namespace set, its wildcard claim rests on an undisclosed host wildcard bind that the probe's own harm line denies, and KQ6/KQ12 anchors are incomplete. No false big-endian proof.

# KnowledgeOwnership — `corpus/knowledge/loopback-listener-ownership.md`

Seat `KamaR18.KnowledgeOwnership`, read-only. Lane tip `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; round start `e75cf680b53484a61709ee1b2787d8dbc6419f74`. No lane edit, no port, no server, no `unshare`, no install; no official counting run. Scratch `/tmp/kama-r18-falsify-KnowledgeOwnership` removed. `lsp` was not mounted (`read xd://lsp` -> "No such tool"; mounted list has no `lsp`), so `grep`/`read` are literal fallback, not semantic reference proof.

Target hash: `f1e77af09b90971b712ef72c8db3b3fcd39e5c1e645673bc51176b6804e05382`.
Evidence hashes: `ProbeTcp6Format.md` `dabf9e38…127f77`; `ProbeArgvEffects.md` `4caff953…71e089`; `ScoutCoverageOwnership.md` `9f644192…e38af`; `README.md` `01a6818b…cedf`; `round-18.md` `ccd23c6c…b1d4`; tool `dc036d7d…a04b`; gate `c5715641…8335`.

## 1. Genuinely new mechanism? — new to the corpus, not new in the lane's code

Yes for the corpus; no as a first implementation.

- Corpus negative: `grep -rn -E 'proc/net/tcp|socket:\[|procfs' corpus/ --include='*.md'` excluding the new entry and `lessons/round-18.md` returns **0 lines**. `listener-census.md:4` attributes with `sudo -n ss -ltnp`; no procfs inode->fd join. `llamacpp-loading-lifecycle.md:112-113,197` already asserts "listener proven owned by the child" and `teardown_port_closed` "unless child ownership was proven", but holds no mechanism.
- Code positive: the frozen pre-round tool at `e75cf680` (`sha256 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`, equal to `.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py` and to `git show e75cf680:tools/kama-llamacpp-live.py`) already implements the join; v3 `1c325b2` fixes the tcp6 arm. So the ownership join is **new corpus documentation**, not a new lane capability, and the IPv6 correction is the new code fact.
- `corpus/README.md:261` says "newly held mechanism"; `:265-266` names only the census as prior ground. The entry body is honest about the old predicate (`loopback-listener-ownership.md:61-64`), so the overbreadth is in the coverage row, not the body. Recommend "newly documented mechanism; corrected IPv6 arm" plus the prior overlap in §3e.

## 2. Claims that survive (byte-exact checks)

- Kernel `net/ipv6/tcp_ipv6.c` v7.2 fetched from `raw.githubusercontent.com/torvalds/linux/v7.2/...`, `sha256 dd3f400b6d29c940d298e0b0a600a82b32368219aee5bc8f17981b00bd7b0558` (matches S048). `seq_printf` at 2172-2179; `src->s6_addr32[0..3]` at 2176-2177; no `ntohl`/`htonl`/`swab` in `get_tcp6_sock`. Entry `:9-13` exact.
- `include/uapi/linux/in6.h` `sha256 4b70a42300079eee8dc3bc9d6c327a04cbd8eb75b2fa9d995d9f0a3306d6b27d`; line 38 `__be32 u6_addr32[4];`. Entry `:10-11` exact.
- Table `:16-21` matches `ProbeTcp6Format.md:12-16` and raw rows `:186-200`, `:690-704`: `127.0.0.1` -> `0100007F`; `::1` -> `…01000000`; `::ffff:127.0.0.1` -> `0000000000000000FFFF00000100007F`; `::` zeros. `127.1.2.3` / mapped exercised as cases E/F.
- RFC/`/104` `:25-27` matches S050: mapped /96 prefix plus 127/8 = `::ffff:127.0.0.0/104`, not the whole /96.
- Suffix warning `:29-32`: the probe's one-token edit accepts `::ffff:0.0.0.1`, `2001:db8::1`, `fe80::1` (`ProbeTcp6Format.md:55`, `:796`), so the warning is grounded.
- Join `:36-38`: tool `:337-343` (`parts[3] == '0A'`, port match, `parts[9]` inode) and `:370-389` (read `/proc/<pid>/fd`, match `socket:[inode]`). `True/False/None` and gate requirement: `:561-580`, `:654-667`, `check-receipt.py:582-587` (a valid receipt requires `child`; `unproven` fails).
- Frozen vs v3 `:40-44`: `ProbeTcp6Format.md:12-16` gives frozen IPv4 True, `::1`/mapped None, mapped HTTP 200. v3 `_tcp6_is_loopback` `tools/kama-llamacpp-live.py:311-325` accepts exact `::1` and the 96-bit mapped prefix with `address[12] == 127`. Selftest `:1055-1082` binds `::1` and `::ffff:127.0.0.1` and checks `_listen_inodes`/`_tcp6_is_loopback`. Precision: it does **not** call `port_owned_by` on a live child; the full join's live exercise is IPv4. The entry's "its selftest checks real loopback sockets" is true at the parser layer, not the child-fd layer.
- Pre-round predicate `:61-64`: `git show e75cf680:tools/...` lines 332-337 is exactly `endswith('00000001')` plus `[:24] == '0000000000000000FFFF00'` (22 chars). Frozen hash matches. Correct.
- Wolf/wildcard policy `:46-50` matches tool `:337-342`; the gate requires child; missing evidence is `None`, not `False`.
- **Big-endian:** the entry does not falsely claim BE proof. `:32` says "not observed"; S048's scope is "not big-endian hosts"; no BE experiment. The retained parser is LE-only (`:311-321` unconditionally reverses each word); `:30` "decode according to host endianness" is the inferred general rule, not what the parser does. On BE the parser would corrupt. `:54` scopes to one little-endian host. Minor fix: label the rule [INFERENCE] and say "the retained parser reverses each word unconditionally."

## 3. Limits that are missing or under-scoped

### 3a. Race: response observed before ownership check (primary; code-path [INFERENCE])

`readiness_loop`'s docstring claims "a stranger's loading body can never reach loading_503" (`tools/kama-llamacpp-live.py:542-545`). The code evaluates `conn.get('/v1/models')` **before** `_observe` (`:612`) and calls `port_owned_by` only after the response (`:572-579`), setting `proven = True` if the child's listener exists at that moment. Sequence: stranger answers 503 -> closes; child binds the same free port; `port_owned_by` sees the child's inode -> `proven=True`; `:580+` records the stranger's body in `loading_503`. The check proves *a listener at check time*, not the responder. The entry's race sentence (`:54-55`) covers only the procfs reads, and `:48-50` covers only `None`; neither states this ordering. Fix: add "the first HTTP response is observed before the ownership read; a stranger's response can be attributed if the child binds between the response and the fd read; the tool's 'never' claim is not established by this ordering." Narrow window (requires a stranger to bind the picked port, answer, close, and the child to bind before the check), and not reproduced — code-path inference from the pinned lines, not a timed kill.

### 3b. Namespace: "one network namespace" is under-scoped for the round

`:54` says one network namespace. True for the cited `ProbeTcp6Format` evidence (host netns). But the round also ran the **frozen** `_listen_inodes`/`port_owned_by` inside `unshare -rn`: `ProbeArgvEffects.md:81` ("Isolated netns: run under `unshare -rn`"), with `:384-385` showing `{"39729":{"_listen_inodes":[],"port_owned_by":null}}` on `tcp 00000000:9B31`. No `::1`/mapped row was tested there. The v3 parser itself was not run in a second netns. Fix: say "v3 address/join observations: initial netns; the frozen wildcard case was also run in an isolated netns with the same []/None; no `::1`/mapped netns test." This preserves the KQ10 boundary instead of implying a single-netns round.

### 3c. Wildcard evidence: host wildcard bind undisclosed; the probe's own harm line is false

`ProbeTcp6Format.md:5` claims "only loopback listeners ... never 8080/34113." Case D binds `::` with `IPV6_V6ONLY=0` (`:186-200` and `:690-704`), `ss` reports `*:56483` and `*:40909`, and the case answers `127.0.0.1` and `::1` (`:14`). That is a host wildcard, not loopback-only, and it was not isolated. The knowledge entry's `:46` "Wildcard sockets can answer loopback connections" rests on this case; `:54` says one netns and `:56` says "No container namespace..." but neither discloses the host wildcard. `corpus/lessons/round-18.md:187-194` discloses only `ProbeArgvEffects`'s 14.2 ms wildcard, not this twice-run `::` bind. KQ10 (`corpus/QUALITY.md:32`) says an out-of-scope probe's output is recorded and excluded; the probe's own harm claim denies the scope violation. Fix: cite the **isolated** `0.0.0.0` run (`ProbeArgvEffects.md:83-84`, HTTP 200 under `unshare -rn`) for wildcard reachability, or record the host `::` exposure in the entry/lesson. The wildcard fact is true; the evidence boundary is not disclosed.

### 3d. KQ6: S049/S050 section anchors absent

`source:` (`:1`) cites "S048 ..., S049 ..., S050"; `:13-14` gives no S049 line; `:25` gives no RFC section. KQ6 (`corpus/QUALITY.md:28`) requires the documented revision and section, and `ScoutCoverageOwnership.md:119` obligation 3 required §2.5.3/§2.5.5.2. S048 is properly anchored (`v7.2:2172-2179`). Fix: add `S050 §2.5.3 (line 474), §2.5.5.2 (548-552, layout 570)` and `S049:8,12` to the `source:` line or body. Truth error: none; traceability only.

### 3e. KQ12: prior overlapping coverage not named

`README.md:265-266` names only the census. `llamacpp-loading-lifecycle.md:112-113,197` already asserted child ownership and made teardown depend on it; the new entry is the mechanism behind that claim. KQ12 (`corpus/QUALITY.md:39`) asks claims to identify prior overlapping coverage. Fix: add a "Prior overlap: census used privileged `ss`; loading-lifecycle asserted the ownership conclusion without the mechanism; this entry documents the mechanism and corrects the IPv6 arm." The entry already says "false negative" and "historical" (`:42-44`, `:61-64`), so the body is not overclaiming; the coverage row is.

### 3f. Coverage-advice honest limit only partially carried

`ScoutCoverageOwnership.md:97-100` says the entry "adds a proof mechanism and address-encoding facts, not endpoint ground. It is not runtime integration, not a live sample, not a capability of the receipt." The entry carries "mechanism evidence, not current service state" (`:3`) and "bounded harness mechanism" (`:58`), but not "no full v3 run bound an IPv6 listener; selftest only; not a receipt capability." `README.md:265` "Frontier advanced" could be read as a capability. Minor: add the explicit limit; it also prevents the selftest's real-socket bind being read as integration.

## 4. Remaining unknowns / review bounds

- No runtime experiment: no `llama-server`, no listener, no port, no `unshare`, no tool/selftest run. Findings are static code, pinned raw sources, probe transcripts and `git show`.
- The §3a race was not reproduced; it is [INFERENCE] from `:612`/`:572-579` and the tool docstring. It needs a stranger bind and a child bind between response and fd read.
- The §3c host wildcard is evidenced by the probe's own case-D `ss` rows and the `::` bind line; I did not re-run it.
- Big-endian was not tested and is not claimed; the parser's BE behavior is [INFERENCE] from `:311-321` and `%08X` semantics.
- Kernel citations are tag v7.2 raw, not the running 7.2.11-arch1-1 stable branch (same limit the probe recorded). No container/cross-user/SO_REUSEPORT/inode-reuse experiment; the entry's list is accurate for the cited probe.
- `lsp` unavailable: no semantic definition/reference proof; negatives are full-set `grep`/`ls`/`git show` reads, not semantic absence proofs.

## 5. Installs

None. No tool installed, upgraded or re-pinned. No listener was started; no seat-owned listener remains (verified after teardown: `pgrep -af kama-r18-falsify-KnowledgeOwnership` empty). Scratch removed.
