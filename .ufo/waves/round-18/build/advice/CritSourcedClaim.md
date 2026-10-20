VERDICT: partial — three planned sources determine code behaviour (kernel tcp6 word order, RFC 4291 mapped form, Python 3.14 BaseException); test-runner exit-code conventions are decorative and MUST NOT be cited as the sourced basis for exit 2.

# Scope
Which new SOURCES rows (S048+) may be cited as the *sourced basis* of C1, per
KQ6 (`corpus/QUALITY.md:28`: a vendor/spec statement "cites an opened `SOURCES.md`
row whose tier fits that scope"). Ruling distinguishes rows that *decide* the
code's correctness from rows that merely decorate it.

# Counterexample tested (strongest available from local evidence)
Live `/proc/net/tcp6` on this host, 2026-10-20:

```
0: 00000000000000000000000001000000:0277 ... 0A   <- a real ::1 listener
```

`::1` prints as four little-endian 32-bit words and ends `01000000`. The
predicate at `tools/kama-llamacpp-live.py:332-335` tests
`addr_hex.endswith('00000001')` — false on every real `::1` row — and
`addr_hex[:24] == '0000000000000000FFFF00'`, a 24-char slice compared to a
22-char literal, never equal regardless of bytes. For a real mapped listener
`::ffff:127.0.0.1` prints `0000000000000000FFFF00000100007F`: `endswith('7F')`
is true but the prefix conjunct already fails, so the child is never recognized
as loopback owner on tcp6. IPv4 path is correct: observed rows `0100007F`
(loopback) and `3600007F` (127.0.0.54) both satisfy `endswith('7F')`
(`tools/kama-llamacpp-live.py:337`).

Consequence: the doc-comment at `tools/kama-llamacpp-live.py:311-318` asserts
this format *unsourced*. Only a kernel-side row upgrades it from assertion to
citation.

# Ruling — rows admissible as C1's sourced basis

1. **Kernel `/proc/net/tcp6` format — LOAD-BEARING, required.** The ownership
   predicate is correct iff it matches how the kernel renders `s6_addr32` words.
   Admissible anchors: `net/ipv6/tcp_ipv6.c` `tcp6_seq_show` `%08X` word prints
   at a pinned tag (tier-A code), or kernel `Documentation/networking/proc_net_tcp.rst`
   *only if* its opened quote pins the word order for the IPv6 table. A generic
   "hex IPv6 address" doc, or a `/proc/net/tcp` doc covering only the 8-char
   IPv4 column, cannot carry this weight — the current `endswith('00000001')`
   bug is exactly what a network-order misreading produces, so an under-anchored
   row would certify the wrong predicate.

2. **RFC 4291 §2.5.5.2 (`::ffff:a.b.c.d`) — LOAD-BEARING, required.** It is the
   authority for the contract requirement that an AF_INET6 `::ffff:127.0.0.1`
   listener is loopback and MUST be ACCEPTED. It decides *which* tcp6 rows the
   predicate should admit, not how they are printed — complementary to row 1,
   not a substitute. Tier-A spec.

3. **Python 3.14 exceptions docs — LOAD-BEARING, required.** The v3 contract
   demands exit 2 + receipt on "BaseException such as KeyboardInterrupt/SystemExit".
   The tool catches `Exception`/`Terminated` only (`tools/kama-llamacpp-live.py:1241-1249`,
   `:1260`, `:1268`, `:1281`, `:1300`, `:1367`, `:1379`, `:1410`); a
   `KeyboardInterrupt`/`SystemExit` raised where `Terminated` handlers are not
   installed escapes as a traceback — exactly the BaseException/Exception
   hierarchy fact. Cite `docs.python.org/3.14/library/exceptions.html`, never
   `/3/` (S044 already records "`/3/` now serves 3.15").

# Ruling — decorative, not a sourced basis

4. **Test-runner exit-code conventions (pytest/automake) — DECORATIVE.**
   "Zero observation → could-not-evaluate" is fixed by the lane's own v3
   contract ("2 could-not-evaluate"), routed R4 in
   `corpus/lessons/round-17-verifier-spotcheck.md` ("zero observation should be
   could-not-evaluate (exit 2), not failed (exit 1)"). No external runner
   convention decides 2 — pytest's nothing-collected is 5, automake's is 99 —
   so citing one as the *basis* is false provenance and, worse, underdetermined:
   two conventions imply two different numbers. If opened at all, it MAY be a
   rationale/vocabulary row only; the behaviour rests on the contract (own-work)
   plus the failing-today observation at `tools/kama-llamacpp-live.py:1240` and
   `:1376-1378` (`all(... passed is True)` → exit 1 on any null/false check).

# Not new-source obligations (do not open rows for these)
- Exact argv re-derivation / duplicate-flag rejection: contract-defined; own-work.
  `--api-key` ordering is already covered by S036 (503 gate "before the API key check").
- `passed: null` / `outcome: not-evaluated` semantics: schema-internal; own-work.
- The `::ffff:127.0.0.1` control's expected ACCEPT: requirements come from
  RFC 4291 (row 2) + kernel format (row 1); the receipt outcome itself is own-work
  evidence (S041/S046 precedent).

# Smallest safe correction
Open exactly three new rows — kernel tcp6 format (code or strictly-anchored doc),
RFC 4291 §2.5.5.2, Python 3.14 exceptions — and cite only those as C1's sourced
basis; cite the tool contract / round-17 receipt rows as own-work for exit-code
and schema claims. Drop or demote the test-runner-convention row to search-log
context.

# Limitations
- The correct fix predicate (e.g., exact slice/literal lengths for the mapped
  prefix) is ProbeTcp6Format's seat; I verified the defect, not the patch.
- Kernel-doc wording for proc_net_tcp.rst is unverified by me [INFERENCE that
  it pins word order]; SourcePins must land the quote before the row is cited.
- No installs; read-only seat, live `/proc/net/tcp6` read only.
