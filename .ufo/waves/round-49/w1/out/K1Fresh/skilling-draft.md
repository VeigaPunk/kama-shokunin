# Proposed SKILL.md addition (seat K1Fresh, round 49) - how-to lines that remove the fresh-session guesses

Insert a subsection after the round-48 "Re-running live evidence (v5, round 48)" block
(current SKILL.md ends at line 1484 with the round-48 bullet list). Style mirrors the
existing "Re-running live evidence" bullet lists. Every guess recorded in the K1Fresh
report is covered by one line.

## Proposed text

### Re-running live evidence with a witness (round 49)

The replay tool can hold its rerun server up for an outside observer:

- Witnessed replay: `python3 tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-1.json --work <empty-dir> --out <json> --witness-dir <existing-dir>` runs the normal v5 replay, and once the server is ready and its checks ran, writes `<witness-dir>/ready.json` `{"schema":"kama-live-witness/v1","port":<int>,"pid":<int>}` — `pid` is the llama-server child, not the harness — then holds the server up to `--witness-timeout` seconds (default 120) until a file named `release` appears in the same directory, then tears down as usual. The rerun receipt gains `witness: {"released": true, "waited_ms": N, ...}`; if you release late it reads `released: false`.
- Expected values come from the receipt's own `provenance.verified` (server `member_sha256`, model `model_sha256`); the frozen b11909 pins are server `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` and model `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
- Observe while held (all against `ready.json`'s pid/port):
  - `sha256sum /proc/<pid>/exe` must equal the frozen server digest.
  - `/proc/<pid>/cmdline` must contain `-m <model>`; `sha256sum <model>` must equal the frozen model digest.
  - Listener ownership: `ss -ltnp | grep :<port>` shows the pid. Cross-check the socket inode: `grep "0100007F:<hex-port> " /proc/net/tcp` — note `/proc/net/tcp` stores the local IPv4 byte-swapped (`0100007F` for 127.0.0.1; grep for the swapped form, e.g. port 35223 → `8997`), and the row's inode column must appear in `/proc/<pid>/fd` as `socket:[<inode>]`.
  - Nonce round-trip: `curl -s 127.0.0.1:<port>/tokenize -d '{"content":"<nonce>","with_pieces":true}'` returns `tokens[].piece`; then POST `{"tokens":[<plain-int-ids>]}` (the integer ids, not the `{id,piece}` objects — the objects get HTTP 400) to `/detokenize`; the returned content equals the nonce with at most one leading space, and `''.join(pieces)` equals it exactly (the tokenizer prepends a space token before the first word).
  - Finish with `touch <witness-dir>/release`; afterwards the pid is gone and the port refuses connections.
- Run manual witness sessions with an isolated home (`HOME=$S/home`, `TMPDIR=$S`) so `~/.cache` cannot smuggle the model; the graded counter does the same.
- Graded form: `python3 tools/round49-replay-witness-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>]` replays all three round-48 receipts this way (witness=1 cap=1 newrow=1 met=True).

## Optional registry row (for the L1's instrument-registry draft; flag only)

| Round-49 C1 witnessed-replay audit | measurement: `python3 tools/round49-replay-witness-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>]` | 0 met, prints `witness=0|1 cap=0|1 newrow=0|1 witnessed=N/3 met=True`, then `detail:` lines; 1 not met; 2 could not evaluate | witness legs for all three round-48 receipts (exe digest, LISTEN socket inode owned by the pid, `-m` model digest, nonce round-trip with the model's own vocab), cap refuses a sparse/declared-size-mismatch archive member before hashing (`provenance-member-*`), newrow S494/S495 with the README `caa8191d` `/tokenize` row | read-only on `--repo`; everything else under `--scratch`, removed on exit |
