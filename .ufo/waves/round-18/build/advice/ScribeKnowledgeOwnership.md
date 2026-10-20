VERDICT: confirm — the `::1` and `::ffff:127.0.0.1` tcp6 hex strings are observed on this host, and the lane predicate's IPv6 loopback test fails on those exact strings; draft written, not integrated.

# ScribeKnowledgeOwnership — round-18 build wave, knowledge entry draft

## Behavior
- Wrote only the owned draft: `.ufo/waves/round-18/build/drafts/knowledge-ownership.md` (sha256 `848b4f5d9f7c549b30dd55ee80d64a33329932bfbbf9ccd7c2be8f8a1a5e08f0`). Entry title: "Loopback listener ownership on Linux". Opens with `source:`, `verified-at:`, `recheck:` lines.
- Provisional rows S048 (kernel v6.12 row printers + tcp_states.h), S049 (man-pages 6.19 proc_pid_net(5), proc_pid_fd(5)), S050 (RFC 4291 §2.5.3, §2.5.5.2). Not appended to `corpus/SOURCES.md`; L1 integrates.
- Lane tree checked read-only: `master` = `e75cf680b534…` (round start); `tools/kama-llamacpp-live.py` lines 326-339 identical to `.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py` lines 326-339.

## Gates
- Acceptance: every quoted source opened this session; URL or path plus line; access date 2026-10-20; quotes ≤25 words (checked by hand). Sources with no located quote: none.
- No placeholders: unknowns are listed under the draft's "Unknown" and "Limits" sections.

## Findings (with locations)
1. **Kernel tcp6 printer.** `net/ipv6/tcp_ipv6.c:2213-2217` prints `"%4d: %08X%08X%08X%08X:%04X …"` from `src->s6_addr32[0..3]`. Source: https://raw.githubusercontent.com/torvalds/linux/v6.12/net/ipv6/tcp_ipv6.c , sha256 `197f0783c9d805f421b4cbeedb07dd219b2a5f10eb48942eb4b2e9ce53cc76f2`.
2. **Kernel IPv4 printer.** `net/ipv4/tcp_ipv4.c:2932-2934` `"%4d: %08X:%04X %08X:%04X %02X …"`. sha256 `116196ff5c093ed5c239fae1e5ca314b65fc8d3e3073f12f0706822725b52b27`.
3. **LISTEN = 0x0A.** `include/net/tcp_states.h:13-22`: enum starts `TCP_ESTABLISHED = 1`, `TCP_LISTEN` is the tenth entry. sha256 `8a41dab66aa79bd0b185da5bbb9b4c72ad7f3efb11bf75d894a80f4273f9766c`.
4. **Observed host hex (2026-10-20, kernel 7.2.11-arch1-1, x86-64, Python 3.14.8):**
   - `::1` → `00000000000000000000000001000000`
   - `::ffff:127.0.0.1` → `0000000000000000FFFF00000100007F`
   - `::` → `00000000000000000000000000000000`
   - IPv4 `127.0.0.1` → `0100007F`; `0.0.0.0` → `00000000`
   Source: own-work scratch probe `/tmp/r18-kco/listener_probe.py` (five listeners on ephemeral loopback/wildcard ports; each fd `socket:[N]` matched the LISTEN row's inode; connects to 127.0.0.1 and ::1 succeeded on the wildcard and mapped listeners). Not a lane artifact; L1 may re-create it as a committed own-work row.
5. **Lane predicate defect (reproduced by string test).** `tools/kama-llamacpp-live.py:332-335`: `if not (addr_hex.endswith('00000001')` / `or (addr_hex[:24]` / `== '0000000000000000FFFF00'` / `and addr_hex.endswith('7F'))):`. Python on the observed `::1` string: `endswith('00000001')` is False. The 24-character slice never equals the 22-character literal. Docstring lines 314-315 repeat the wrong `::1 ends 00000001`. Impact on the harness: a child bound to `::1` is not counted as loopback-owned; a child bound to `::ffff:127.0.0.1` is not counted either. Whether the live gate currently fails on this depends on whether the harness ever sees a tcp6 listener — not tested here [INFERENCE: consistent with C1's suspicion; the C1 seat owns the fix].
6. **Wildcard listeners.** Probe: `0.0.0.0` listener accepts connect via 127.0.0.1; `::` listener accepts connect via ::1. Their rows are all-zero addresses. The lane's fail-closed policy (`tools/kama-llamacpp-live.py:337-338`) treats them as not loopback-owned; that is a policy choice, documented as such in the draft.

## Limits
- Linux only; host printers verified by observation on 7.2.11, source read only at v6.12 (7.2 printers [INFERENCE] unchanged).
- Byte-reversal documented for little-endian only; big-endian untested.
- Namespaces (`proc_pid_net(5)`) and cross-user `/proc/<pid>/fd` access (`proc_pid_fd(5)` ptrace rule) are cited, not tested.
- No test of coexistence of a specific-address and a wildcard LISTEN on one port.
- Race between `/proc/net` and `/proc/<pid>/fd` reads: stated as [INFERENCE].

## Installs / updates
- None. Used existing `curl`, Python 3.14.8, `ss`. No pacman, no tool installs.

## Out of scope / not done
- Did not edit lane docs, SOURCES, QUALITY, the tool, or the gate; did not run the lane measurement or gate; no lane ports bound. Probe used ephemeral ports only and exited with no residual listeners (confirmed by `ss -ltnp`).
- Removed the fetched kernel/RFC/proc copies from `/tmp/r18-kco`; `listener_probe.py` kept there for reproduction.

## Artifact paths
- Draft: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/drafts/knowledge-ownership.md`
- Report: this file.
