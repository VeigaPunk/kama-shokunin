# N6Sources — round-49 w1 scoped findings

**Verdict: the C1 witness's four sub-checks map onto seven source rows (S038/S486/S488,
S039/S492/S493, S494, S495); the listen leg is the only witness sub-check with zero
direct source grounding — propose S496 (`proc_pid_net(5)`) and S497 (`tcp_states.h`
@ v7.2) to close it.**

Deliverable: `.ufo/waves/round-49/w1/out/N6Sources/map.md` (full map, mapping tables,
proposed rows, risks).

## Evidence

- Sources read: `corpus/SOURCES.md` rows S038 (line 50), S039 (51), S486 (239), S488
  (241), S492 (245), S493 (246), S494 (247), S495 (248); registry format header lines
  11-12 (`| id | source | kind | tier | scope | anchor | teaches | status | opened |
  recheck | used-by |`).
- Counter contract: `tools/round49-replay-witness-audit.py` — legs at:
  - exe: `sha_file("/proc/<pid>/exe") == SERVER_SHA` (lines 260-262; constant line 97);
  - listen: `listen_inodes()` parse of `/proc/net/tcp{,6}` — state `f[3] == "0A"`,
    loopback addr `f[1]` ∈ {`0100007F`, `00000000000000000000000001000000`}, inode
    `f[9]`, crossed with `pid_socket_inodes()` fd links `socket:[…]` (lines 193-226);
  - model: `-m` arg from `/proc/<pid>/cmdline` hashes to `MODEL_SHA` (lines 266-273;
    constants 98-101);
  - nonce: POST `/tokenize` (with_pieces) + `/detokenize` round-trip vs the counter's
    own `gguf_tokens()` decode (lines 144-189, 276-289);
  - cap: `sparse_archive()` PAX `GNU.sparse.*` control (lines 343-391);
  - newrow: requires a new registry row naming the README at caa8191d and `/tokenize`
    (lines 394-405).
- SOURCES coverage checks (grep `proc_net|proc_pid_cmdline|proc_pid_fd|gguf|sparse|PAX`
  over `corpus/SOURCES.md`): no row for `/proc/net/tcp` table semantics, `/proc/<pid>/cmdline`,
  fd-socket links, or tar/PAX sparse. GGUF vocabulary decode IS covered by S058 (format)
  + S059 (reference reader). S049's scope explicitly excludes state codes.
- Live cross-check (`awk` on `/proc/net/tcp`, kernel 7.2.11-arch1-1): LISTEN rows
  (`st=0A`) have `f[9]` numeric = socket inode; 17 whitespace tokens with extra tail
  columns after the inode; indices ≤ 9 unaffected. Sample:
  `0: 010011AC:0035 00000000:0000 0A 00000000:00000000 00:00000000 00000000 974 0 1403 …`
- URL checks (fetched 2026-10-26):
  - `https://man7.org/linux/man-pages/man5/proc_net.5.html` serves the page titled
    `proc_pid_net(5)` (man-pages 6.19, dated 2026-02-08); §DESCRIPTION `/proc/net/tcp`.
  - `https://raw.githubusercontent.com/torvalds/linux/v7.2/include/net/tcp_states.h`:
    `TCP_ESTABLISHED = 1` (line 13) … `TCP_LISTEN` (line 22; 10th enumerator = 0x0A),
    `TCP_STATE_MASK 0xF` (line 30); sha256 `8a41dab66aa79bd0b185da5bbb9b4c72ad7f3efb11bf75d894a80f4273f9766c`.

## Findings

1. **Mapping (source → receipt field / counter leg):** S038/S486/S488 ground release
   identity (`provenance.server` fields; S488 is the operative row for the C1 round-48
   v5 receipts and the frozen `SERVER_SHA`); S039/S492/S493 ground model identity
   (`provenance.model`, `MODEL_SHA`, 40-hex pin rule); S494 grounds the nonce HTTP
   surface and the `newrow` text; S495 grounds the exe leg. Details in map.md §1.
2. **Gap — listen leg (defect-class finding):** none of the seven rows grounds the
   `/proc/net/tcp{,6}` table parse of `listen_inodes()` (round49-replay-witness-audit.py:193-211).
   S048 covers only tcp6 address *printing*; S049's scope says "not state codes"; the
   `0A`=LISTEN filter constant and the inode column position are unpinned.
   - Shows it: `grep -n "0A" tools/round49-replay-witness-audit.py` → line 203
     (`f[3] != "0A"`), with no SOURCES row pinning 0x0A = TCP_LISTEN or the table
     layout; `awk '$4=="0A"{print $2,$4,$9}' /proc/net/tcp` demonstrates the live
     dependency on that column invariant.
   - Proposed fix: open two rows next round — S496 `proc_pid_net(5)`
     (https://man7.org/linux/man-pages/man5/proc_pid_net.5.html) for the table
     semantics/field positions, and S497 `include/net/tcp_states.h` @ v7.2
     (https://github.com/torvalds/linux/blob/v7.2/include/net/tcp_states.h) for the
     `0A` = TCP_LISTEN constant. Full drafted registry rows in map.md §3.
3. **Tertiary ungrounded surfaces (deliberately not opened, two-row budget):**
   `/proc/<pid>/cmdline`/`cwd` reads in the model leg (proc_pid_cmdline(5)/proc_pid_cwd(5)),
   fd `socket:[inode]` naming (proc_pid_fd(5)), and the cap leg's GNU-tar/PAX sparse
   header semantics. None weakens the witness claim currently: the digest halves are
   grounded (S492/S493; S058/S059) and the cap refusal is a self-imposed tool bound.

## Constraints honored

- Lane and fleet READ-ONLY: no writes outside the two named seat outputs and scratch;
  no git/jj mutation; no service started/stopped (no llama-server runs by this seat);
  no subagent dispatch; no `agent://all` messages.
- No tool installs performed (none needed).
