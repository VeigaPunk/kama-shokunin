VERDICT: n/a — recon question answered and decided: neither mechanism is covered ground; a new entry is expansion (repertoire), not a deepening.

# ScoutCoverageOwnership — is loopback-listener ownership already covered ground?

Read-only corpus/coverage seat. Question: does the lane already hold *listener ownership
via `/proc/net/tcp{,6}` inode → pid fd mapping*, or *IPv6 / IPv4-mapped loopback
listeners*, as covered ground?

## Answer

No. Neither is covered ground, in any corpus entry, lesson, SOURCES row or coverage-map
row. The lane holds (a) a dated **host census** produced with privileged `ss -ltnp`, and
(b) one **IPv6 row** that is an HTTP-probe fact (`[::1]:631` answers on `::1`), not a bind
class, an address encoding, or an ownership proof. The planning note's proposed
`corpus/knowledge/loopback-listener-ownership.md` is therefore **expansion**, and should
be recorded as such — a new coverage-map entry, appended, with the mechanism class named.

## Evidence

### 1. What the coverage map claims for the listener entry

`corpus/README.md:29` — `| knowledge/listener-census.md | every loopback TCP listener on this host + its identity verdict | 1 |`.
That is an inventory-and-verdict row for one host sample. It does not name, and cannot be
read as covering, a proof mechanism, a kernel address format, or an address family.

### 2. What the census actually holds

- Method is privileged `ss`, `corpus/knowledge/listener-census.md:4`:
  "`sudo -n ss -ltnp` (passwordless — succeeded, so owner attribution is *measured*, not
  inferred from docker/systemd heuristics)". No `/proc/net/tcp` read, no socket inode, no
  `/proc/<pid>/fd` join. Ownership is human-attributed per pid, not child-relative.
- The one IPv6 row is a response fact, `listener-census.md:58`:
  "`[::1]:631` … `200` `text/html; charset=utf-8` (same CUPS page via `::1`)". The census
  never binds, encodes or classifies IPv6 addresses; it curls one.
- The census's own `recheck:` boundary keeps that method from being generalised,
  `listener-census.md:387`: "ownerless socket attribution needs explicit operator
  authorization for that inspection". The harness's unprivileged own-child join is a
  different proposition with a different authority boundary.

### 3. Full-set negative reads over the whole corpus

- `grep -rn -E 'proc/net/tcp|socket:\[|socket inode' corpus/` → **0** lines (the only
  `/proc` reads recorded anywhere are `/proc/<pid>/{cmdline,cgroup,environ}` identity
  reads, e.g. ledger C7 at `listener-census.md:214-215`).
- `grep -rni -E 'v4-mapped|ipv4-mapped|::ffff' corpus/` → **2** lines, both debt
  statements, not knowledge: `corpus/lessons/round-17.md:270` and
  `corpus/lessons/round-17-verifier-spotcheck.md:243`.
- `corpus/knowledge/` contains 15 entries; none is an ownership, procfs or IPv6-encoding
  entry (`ls corpus/knowledge/`).
- `corpus/SOURCES.md` has 47 rows (S001–S047); none names `net/ipv6/tcp_ipv6.c`,
  `proc_net_tcp.rst`, RFC 4291 or `/proc/net/tcp{,6}` (`grep -n -E
  'proc_net|proc/net|4291|IPv4-mapped|ipv6/tcp|s6_addr' corpus/SOURCES.md` → no row).

### 4. The lane's own record calls this debt, not knowledge

`corpus/lessons/round-17.md:270-271`: "Live tool: `::1`/IPv4-mapped loopback listeners are
not recognised as child-owned (`LoopbackOwnership`)". The outside closure says the same at
`corpus/lessons/round-17-verifier-spotcheck.md:243`. A lesson's debt list asserts the gap;
it does not hold the missing fact.

### 5. The only statement of the address format is a wrong code claim and an inference

- The tool's docstring states a format it does not have a source for,
  `tools/kama-llamacpp-live.py:315-318`: "::1 ends 00000001; an IPv4-mapped 127/8 is the
  v4-mapped prefix 0000000000000000FFFF00 plus the v4 tail", plus the harness policy
  "A child bound to 0.0.0.0 or :: still answers loopback connects but is not counted".
- The round-17 finding that contradicts it marks the explanation as an assumption,
  `.ufo/waves/round-17/falsify/advice/LoopbackOwnership.md:9`: "The `::1` mismatch is a
  proc-format byte-order assumption"; same file, `:10`: "the mapped-prefix literal is 22
  characters". Observed strings it reports: `::1` → `00000000000000000000000001000000`,
  `::ffff:127.0.0.1` → `0000000000000000FFFF00000100007F`.
  [INFERENCE] Splitting those into four 8-hex words gives `00000000 00000000 00000000
  01000000` and `00000000 00000000 FFFF0000 0100007F`; a correct mapped predicate is a
  24-char prefix `0000000000000000FFFF0000` plus the IPv4 `…7F` tail. This is not proof —
  the kernel row (S048, `get_tcp6_sock` `%08X%08X%08X%08X`) and RFC 4291 §2.5.5.2 decide
  it, and `ScoutKernelTcp6` is opening both this round.
- `corpus/knowledge/llamacpp-loading-lifecycle.md:112-113` uses the fact as a harness
  property ("listener proven owned by the child at the first HTTP answer") without ever
  holding the mechanism that proves it.

## Decision: expansion, not deepening

Record the new entry as **uncovered ground — expansion of repertoire**, in the sense the
coverage map already uses for `knowledge/ollama-evidence-replay.md` ("operational workflow
newly held beyond the conceptual crosswalk", `README.md:167`) and against the round-17
counter-form ("deepens the round-16 entry, no new ground", `README.md:238`).

It is not a deepening of `listener-census.md`, for three reasons the lane's own rules
supply:

1. **Different evidence class.** The census is own-work host evidence pinned to
   2026-09-28/10-14 with a `source:`/`verified-at:` supplement that says no host state was
   re-opened (`listener-census.md:385-386`). The new facts are revision-pinned kernel code
   and an RFC — KQ6 tier-A code/spec rows (`QUALITY.md:28`), not another census sample.
2. **Different proposition.** Census §0 reports that every listener in *that* sample "has
   a measured owner"; the new entry reports *how a harness can prove its own child owns a
   socket before the first HTTP byte*, unprivileged and child-relative. The census's own
   authority boundary (`:387`) shows these do not substitute for each other.
3. **KQ12 needs a new sourced distinction, and there is one.** `QUALITY.md:39` rejects it
   when "row or field growth is called new knowledge without a new sourced distinction".
   Three such distinctions exist and none is in the corpus, so this is not field growth:
   procfs inode→fd ownership join (vs `ss` users column); tcp6 four-word host-byte-order
   encoding (vs textual IPv6 notation); IPv4-mapped reachability under RFC 4291 (vs native
   `::1`).

The honest limit of the expansion claim, which the entry must carry: it adds a **proof
mechanism and address-encoding facts**, not endpoint ground. It is not runtime
integration, not a live sample, not a capability of the receipt. KQ4 (`QUALITY.md:12`)
still applies to anything that looks like integration.

## Obligations on the entry so the expansion stays admissible

1. **New file, appended coverage section.** Do not insert a row into the line-29 table.
   Precedent and rule: `README.md:86` "Appended rather than inserted, so no existing line
   moves"; `QUALITY.md:29` (KQ7) "every correction appended at the end of its file".
2. **Provenance trio first.** `QUALITY.md:38` (KQ11): "New knowledge entries still open
   with the provenance trio" — `source:`, `verified-at:`, `recheck:`, as in
   `corpus/knowledge/llamacpp-loading-lifecycle.md:1-3`.
3. **Cite the deciding rows, not provisional ids.** Kernel `get_tcp6_sock` format and
   `proc_net_tcp.rst` for the encoding; RFC 4291 §2.5.5.2 (and §2.5.3 for `::`/`::1`
   addressing) for reachability. Do not cite a test-runner convention as the basis for
   either behaviour (KQ6 tier fit). Final S-id assignment belongs to
   `ScribeSourcesKernel`; the entry cites what lands.
4. **Do not restate round-17's inference as the format claim.** The byte-order sentence
   must be supported by the kernel source row and the entry must label the two observed
   proc lines as corroboration on this host. This is the round-17 M8 pattern ("read the
   whole control path before admitting a code-derived behavioural claim"); the wrong claim
   currently lives in the tool docstring (`tools/kama-llamacpp-live.py:315`), so the entry
   is also the place that supersedes it.
5. **State the acceptance side, not only rejection.** A listener bound to
   `::ffff:127.0.0.1` with `IPV6_V6ONLY=0` answers an IPv4 loopback client and *is* the
   child's loopback listener; failing ownership for it is a false failure of a healthy
   child. A C1 control that expects rejection there would encode the defect as intent.
6. **Separate kernel fact from harness policy.** `0.0.0.0`/`::` fail-closed
   (`tools/kama-llamacpp-live.py:317-318`) is harness policy, not a kernel property. Under
   KQ21 (`QUALITY.md:122`) the ownership check is harness/input-integrity in character and
   should not be sold as subject evidence.
7. **Do not claim the census is refreshed.** No `/proc` census of foreign listeners was
   run and none is authorised by this entry; `tools/kama-probe.sh listeners` was not
   executed for this seat (KQ10, `QUALITY.md:32`).

## Out-of-scope observation (advisory, not this lane's repair)

The same unheld fact has a second consumer: `tools/kama-probe.sh:279` selects loopback
scope with the textual matcher `127.*|"[::1]"|"::1") scope=loopback ;;`, and
`cmd_listeners` iterates only `loopback_ports` (`:720`). A listener bound to
`[::ffff:127.0.0.1]` matches neither the loopback branch nor the wildcard branch
(`:280`), so it is dropped from the probe's own listener enumeration. That file is outside
C1's declared file set and outside this seat's write scope; recorded so the knowledge entry
does not imply the probe already handles the mapped form.

## Limitations

- Corpus read only. No `ss`, no `/proc/net/tcp` read, no socket join and no listener
  started by this seat; the census rows quoted are historical, not current host state.
- The tcp6 byte-order and 22-vs-24-char findings are reproduced from
  `.ufo/waves/round-17/falsify/advice/LoopbackOwnership.md`; I did not re-derive them. They
  are marked [INFERENCE] there and here until the kernel source row and the on-host probe
  land.
- The `lsp` device was not mounted in this session (no server answered for this checkout),
  so definition/references/hover were unavailable; `grep`/`glob` were used to *locate*
  text only. The negative results above are full-set reads (`ls corpus/knowledge/`, a
  whole-`corpus/` grep with counted output), not semantic absence proofs.
- Nothing under `.ufo/interactive-sessions/`, `~/.omp/` (other than `RULES.md`), or
  `~/.config/` was read.

## Installs

None. No tool was installed, upgraded or re-pinned.
