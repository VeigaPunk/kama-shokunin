VERDICT: confirm — both suspected tcp6 format defects are real (kernel source + live /proc proof); tcp4 branch already correct; corrected fail-closed predicate below.

Axes walked: correctness (kernel-format ground truth), evidence (source + live /proc), harm-avoidance (no wildcard false accepts), maintainability (exact per-family predicates). Reviewer seat, read-only: no files written except this report; no installs (record: none); no scratch kept.

## Ground truth (kernel v7.2, host kernel 7.2.11-arch1-1, byteorder=little)

- `get_tcp6_sock` prints the local address as four host-register 32-bit words, not network-order hex:
  https://github.com/torvalds/linux/blob/v7.2/net/ipv6/tcp_ipv6.c#L2167-L2174 — `"%4d: %08X%08X%08X%08X:%04X ..."` fed `src->s6_addr32[0], src->s6_addr32[1], src->s6_addr32[2], src->s6_addr32[3]` (L2171-2172). Each word is a `__be32` printed with `%08X`, so on a little-endian host every 32-bit word appears byte-reversed; the swap is per word, NOT a whole-string reversal.
- tcp4 counterpart: https://github.com/torvalds/linux/blob/v7.2/net/ipv4/tcp_ipv4.c#L2811-L2813 — same `%08X` on the be32 `src` (L2813), so `127.0.0.1` prints `0100007F` on LE.

## Live proof (this host; binds loopback only, closed in-process, `ss -ltn` after exit shows none of 47231-47233)

| Bound address | /proc row local column | state |
|---|---|---|
| `::1:47231` | `/proc/net/tcp6` `00000000000000000000000001000000:B87F` | 0A |
| `::ffff:127.0.0.1:47232` | `/proc/net/tcp6` `0000000000000000FFFF00000100007F:B880` | 0A |
| `127.0.0.1:47233` | `/proc/net/tcp` `0100007F:B881` | 0A |

Real wildcard listeners already on this host: `/proc/net/tcp` `00000000:14EB` (0.0.0.0:5355) and `/proc/net/tcp6` `00000000000000000000000000000000:14EB` (`::`:5355).

## Finding 1 — CONFIRMED (defect): `::1` test can never match on LE

- frozen/tools_kama-llamacpp-live.py:332 `addr_hex.endswith('00000001')` assumes network-order print (`...0001`). Actual LE print of `::1` is `...01000000` (live row above) → the test never fires; a `::1` listener is invisible.
- Same wrong claim baked into the docstring, frozen:316 "::1 ends 00000001; an IPv4-mapped 127/8 is the v4-mapped prefix" — docstring must be fixed with the code.

## Finding 2 — CONFIRMED (defect): 24-char slice vs 22-char literal

- frozen:333-334 `addr_hex[:24] == '0000000000000000FFFF00'` — measured `len('0000000000000000FFFF00') == 22`; a 24-char slice never equals a 22-char literal, so the v4-mapped arm is dead code.
- Independent second bug: even at equal length the bytes are wrong. LE word order makes word2 of `::ffff:127.0.0.1` print `FFFF0000` (live row: positions 16-23 `FFFF0000`), so the correct 24-char prefix is `0000000000000000FFFF0000`, not any `...FFFF00` network-order prefix.

## Finding 3 — tcp4 branch already correct (no change)

- frozen:337 `elif not addr_hex.endswith('7F')` — LE print puts the high v4 byte last, so this is exactly 127.0.0.0/8; live rows `0100007F` (127.0.0.1) and host `127.0.0.53%lo:53` / `127.0.0.54:53` all classify as loopback. `0.0.0.0` = `00000000` ends `00` → rejected.

## Does the fix risk counting `0.0.0.0` or `::` as loopback-owned?

No — with the exact per-family predicate below. Rejections: tcp4 `0.0.0.0` = `00000000` (no `7F` tail); tcp6 `::` = 32 zeros (neither exact `::1` constant nor `FFFF0000` prefix), both rows live on this host; mapped wildcard `::ffff:0.0.0.0` = `0000000000000000FFFF000000000000` passes the prefix conjunct but fails the `7F` tail. The two conjuncts are what make it safe: prefix alone would admit `::ffff:0.0.0.0`-style wildcards' address bits into consideration; tail alone would admit non-mapped addresses ending `...7F` (e.g. `2001:db8::7f`). Weaker variants that DO introduce risk: `endswith('01000000')` for `::1` also matches `::1.0.0.0` (not loopback); swapping the whole 32-char string instead of per-word keeps the miss silently.

## Corrected predicate (drop-in, frozen:331-338)

```python
if proc_net.endswith('tcp6'):
    if not (addr_hex == '00000000000000000000000001000000'   # ::1, LE words
            or (addr_hex[:24] == '0000000000000000FFFF0000'  # ::ffff:0/96, LE
                and addr_hex.endswith('7F'))):               # 127/8 tail (v4 high byte)
        continue
elif not addr_hex.endswith('7F'):                            # 127.0.0.0/8, LE
    continue
```

Exact equality for `::1` (not endswith) removes any possibility of a non-loopback tail-word collision. Update docstring lines 312-317 to the per-word LE description.

## Behavioral impact [INFERENCE from callers, same file]

`_listen_inodes` is consumed only via `port_owned_by` (frozen:350), whose callers (frozen:548-551 first-HTTP gate, frozen:634-637 final ownership check) map an empty set to `None` → `port-listener-ownership-unproven`. So today a serve bound to `::1` or `::ffff:127.0.0.1` is fail-closed but misclassified as ownership-unproven instead of recognized; the common 127.0.0.1 (tcp4) bind is unaffected.

## Limitations / residual risk

- Predicates are host-endian-specific (LE). On a BE kernel the prints would be network-order; host verified `little`, and the pre-existing tcp4 branch makes the same assumption, so this adds no new portability debt. [INFERENCE: BE behavior not tested here.]
- v4-compatible `::7f00:1` is deliberately rejected (fail-closed; outside claimed scope `::1`, `::ffff:127.0.0.0/104`, `127/8`).
- Not exercised against a real `llama-server` v6 bind; the /proc rows above are synthetic AF_INET6 listeners, which use the identical `get_tcp6_sock` print path.
