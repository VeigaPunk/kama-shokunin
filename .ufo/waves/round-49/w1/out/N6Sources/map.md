# Cross-source map — round-49 C1 live-evidence witness (seat N6Sources)

Round: 49, wave 1, lane kama. Read-only analysis of `corpus/SOURCES.md` rows and
`tools/round49-replay-witness-audit.py` (C1, frozen). No lane file edited; proposal
only (the counters and the SOURCES registry are frozen this round).

---

## 1. Source rows → what each grounds (receipt field / counter leg)

| Row | Grounds | Receipt field | Counter leg |
|---|---|---|---|
| S038 (llama.cpp release b11755, asset record) | release-identity *pattern*: official Linux x64 CPU binary, asset digest → member binary hash | ancestor of S486/S488; grounds the round-16-era receipts' `provenance.server` | — (pattern ancestor) |
| S486 (release b11906, asset record) | same pattern for the round-46 receipts | round-46 v3 receipts' `provenance.server` | — |
| S488 (release b11909, asset record) | the operative release row for the C1 receipts: tag caa8191d, asset digest bf94332a…, member `llama-b11909/llama-server` sha256 35ac50fb… | the three committed round-48 v5 receipts (`RECEIPTS`) `provenance.server.{asset_url,asset_sha256,member}` and `server` binary digest; also the counter's frozen `SERVER_SHA` constant (round49…audit.py:16,97) | the `-m`/exe digest targets are *defined* here; the digest comparisons run in the exe and model legs |
| S039 (stories260K GGUF, LFS identity) | model artifact identity baseline: LFS sha256 270cba1…, size 1185376 | underlies S490/S492; receipts' `model` sha256 / `model_sha256_post` | counter's frozen `MODEL_SHA` constant (round49…audit.py:18,101) |
| S492 (stories260K pinned to revision 499bc882) | model identity at a pinned revision: `x-repo-commit`, fixed bytes; the replay locator that replaces S490's moving `main` | `provenance.model.url` (full 40-hex resolve URL) + sha256 in v5 receipts | model leg's `-m`-target digest; counter's own `MODEL_URL` download (round49…audit.py:99-100) |
| S493 (huggingface_hub download guide) | the full-length-commit-hash pin rule | why `provenance.model.url` must be the 40-hex form; live tool's pin validation | counter's `MODEL_COMMIT` = full 40-hex (round49…audit.py:98) |
| S494 (llama.cpp server README @ caa8191d) | `/tokenize` `with_pieces` and `/detokenize` request/response shape at the exact b11909 commit | — (the HTTP surface is exercised live, not recorded) | nonce leg: POST `/tokenize` + `/detokenize` call shape and response parse (`tokens[].id/piece`, `content`) (round49…audit.py:276-286); also the `newrow` leg's required registry-row text (round49…audit.py:394-405) |
| S495 (proc_pid_exe(5)) | `/proc/<pid>/exe` dereference opens the running executable | — | exe leg: `sha_file("/proc/<pid>/exe")` == `SERVER_SHA` (round49…audit.py:260-262) |

Receipt fields *not* grounded by any external source (own-work protocol, acceptable):

- `ready.json {schema: kama-live-witness/v1, port, pid}` (live tool `hold_for_witness`, kama-llamacpp-live.py:280-300) — the witness contract between tool and counter.
- rerun receipt `witness {released, waited_ms, port, pid, dir}` — written by `hold_for_witness`, asserted by the counter (`rr["witness"]["released"] is True`, round49…audit.py:323-326). The *waited_ms* semantics are the tool's own record, never the observer's view (docstring, live tool:284-286).
- Replay `match=true` / exit 0 (round49…audit.py:320-322) — replay tool's own completion contract.

## 2. Which counter checks have NO source row

| Leg | Reads | Coverage today | Gap |
|---|---|---|---|
| **listen** | `/proc/net/tcp{,6}` rows: state `0A`, local addr `0100007F`/`00000000000000000000000001000000`, inode `f[9]`; crossed with `/proc/<pid>/fd` `socket:[<inode>]` links (round49…audit.py:193-226) | S048 (tcp6 address *printing* only), S049 (proc_net_tcp.rst deprecation; scope explicitly **"not state codes"**), S050 (RFC 4291 loopback forms) | **the table's field semantics, the `0A`=LISTEN constant, and the fd-link naming have no row.** This is the only witness sub-check with zero direct grounding. |
| model (argv read) | `/proc/<pid>/cmdline` (and `/proc/<pid>/cwd` for relative `-m` resolution) (round49…audit.py:266-271) | digest half grounded by S492/S493 | the `/proc` argv read itself has no row (`proc_pid_cmdline(5)`/`proc_pid_cwd(5)`); minor, not opened |
| cap | archive-member bounds and sparse refusal (PAX `GNU.sparse.*` headers, `sparse_archive()` control, round49…audit.py:343-391) | — | GNU-tar/PAX sparse-header semantics have no row; minor, not opened |
| nonce (vocabulary half) | counter's own GGUF decode of `tokenizer.ggml.tokens` (round49…audit.py:144-189) | **covered**: S058 (GGUF v3 header/metadata serialization) + S059 (gguf_reader.py reference) | none — not a gap |

## 3. Proposed rows (at most two — exactly two)

### S496 — `proc_pid_net(5)` (Linux)

- URL: `https://man7.org/linux/man-pages/man5/proc_pid_net.5.html` (the
  `…/man5/proc_net.5.html` alias serves the same page).
- kind `docs`, tier `A`. Scope: the `/proc/net/tcp{,6}` socket-table semantics used by
  C1's listen leg — Linux only; not state-code enumeration, not the hex address byte
  encoding (S048), not deprecation history (S049).
- Anchor: §DESCRIPTION → `/proc/net/tcp`. Quote: "The `sl` value is the kernel hash
  slot for the socket, the `local_address` is the local address and port number pair."
  (page also documents `St` as "the internal status of the socket", and the namespace
  virtualization note: `/proc/net` is a symlink into `/proc/self/net`, so the table the
  counter reads is the server's network namespace's).
- Evidence: man-pages 6.19, page dated 2026-02-08 (colophon); page fetched 2026-10-26.
- Why: the listen leg is the half of the witness claim "the frozen binary is the
  listener of the announced port" that rests on a raw kernel-table parse with no source
  row; without it, the counter's parser (`listen_inodes`) is an ungrounded
  self-implementation. A row also pins the field-position invariant the counter relies
  on (`sl local_address rem_address st tx_queue:rx_queue tr:tm->when retrnsmt uid
  timeout inode …`; observed live on this host, see §4).

### S497 — Linux `include/net/tcp_states.h` @ v7.2

- URL: `https://github.com/torvalds/linux/blob/v7.2/include/net/tcp_states.h`
  (same kernel tag base as S048/S049 — keeps the kernel-version story consistent with
  the host's 7.2.11-arch1-1).
- kind `code`, tier `A`. Scope: the TCP `sk_state` enumeration, i.e. the meaning of the
  `St` column values in `/proc/net/tcp{,6}`; not other kernel versions, not the table
  layout.
- Anchor: enum lines 13–24 (`TCP_ESTABLISHED = 1` … `TCP_LISTEN`), `TCP_STATE_MASK
  0xF` line 30. `TCP_LISTEN` is the 10th enumerator → 0x0A = `0A` in the `%02X`-printed
  `St` column. Raw file sha256 `8a41dab66aa79bd0b185da5bbb9b4c72ad7f3efb11bf75d894a80f4273f9766c`.
- Why: S049's scope explicitly defers state codes ("not state codes"), so the exact
  `0A` filter constant of the listen leg is currently unpinned by any row; this is the
  one-character bug surface that would silently narrow the witness (e.g. filtering on a
  wrong state). One small kernel row closes it.

## 4. Supporting observation (host, kernel 7.2.11)

Live `/proc/net/tcp` LISTEN rows on this host print 17 whitespace-separated tokens;
`f[9]` is numeric and is the socket inode (classic `tcp_seq_show` printf order:
`sl local rem st tx:rx tr:tm retrnsmt uid timeout inode …`), with extra tail columns
after the inode. The counter reads only indices ≤ 9, so the tail drift across kernels
does not affect it — but this is exactly the kind of invariant a `proc_pid_net(5)`
row would pin. Sample row (port 0x35):

```
0: 010011AC:0035 00000000:0000 0A 00000000:00000000 00:00000000 00000000   974        0 1403 …
   f1=local f3=st=0A f7=uid f8=timeout f9=inode(1403)
```

## 5. Risks / notes

- Both proposed rows are Linux-only, consistent with S495's scope; the C1 counter is
  Linux-only by declaration (limits, preregistration).
- `proc_pid_net(5)` alone does not enumerate state codes — that is why S497 is proposed
  as the second row rather than, e.g., a second docs page; the two rows together close
  the listen leg.
- Not opened (explicitly out of the two-row budget): `proc_pid_cmdline(5)` /
  `proc_pid_cwd(5)` (model-leg argv read), `proc_pid_fd(5)` (fd → `socket:[inode]`
  naming), and a GNU-tar/PAX sparse-format row (cap leg). If a future round wants to
  source the cap leg too, the sparse PAX header semantics are the only remaining
  ungrounded claim there.
