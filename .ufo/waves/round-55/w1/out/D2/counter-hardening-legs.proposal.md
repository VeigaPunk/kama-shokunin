source: S506 (proc_pid_mem(5), §DESCRIPTION, man-pages 6.19, page dated 2026-02-08), S507 (ptrace(2), §/proc/sys/kernel/yama/ptrace_scope, value 1, man-pages 6.19, page dated 2026-06-05), S508 (proc_pid_map_files(5), §DESCRIPTION — rejected alternative), S500 (memfd_create(2), §DESCRIPTION/§HISTORY), S501 (F_GET_SEALS(2const), §DESCRIPTION), S502 (kernel mfd_noexec, §Sysctl), S509 (ggml-backend-reg.cpp @ b11909, lines 401/480/488-489/491), S510 (git(1) §Documentation/git.txt codeGITDIRcode), S511 (git-config(1) §GIT_CONFIG_COUNT); lane evidence: `corpus/lessons/round-53.md` §Mistakes 6/8/9, `corpus/lessons/round-55.md` §Mistakes, the round-53 seat reports `.ufo/waves/round-53/w1/out/{K1Cheat,Sen1Mem,J7Late,Sen4Fixture,J12Hide,J11BadFixed}.md`, the round-55 battery `.ufo/waves/round-55/c1/battery/`
verified-at: 2026-10-27 — every S-row was opened in rounds 52/53/55 with a committed copy beside the round (`.ufo/waves/round-52/c1/`, `.ufo/waves/round-53/c1/`, `.ufo/waves/round-55/sources/`); the cited receipts were re-read at the lane tip `8abadfed` this round, not re-run
recheck: re-read the cited receipts (`python3 .ufo/waves/round-55/w1/out/D2/check-citations.py`) and, on a new counter, run its base/do-nothing control and one named mutant per leg before the leg counts; S506/S507/S500/S501/S502 360d, S509 (b11909 tag) until the engine pin moves, S510/S511 on a git release note

# Counter-hardening legs — a leg counts only when a control kills the counter it hardened

Round-55 method entry (axis: calibration — how this lane earns a counter-hardening
leg). It records the six shortcut classes the round-53 wave demonstrated against the
round-53 frozen counters, each shortcut class's round-54/55 leg, and the admission
rule that separates a leg from a comment. It is method knowledge about kama's own
instruments; it asserts nothing about any served endpoint.

What is new here and what is not: KQ94 (round 53) and KQ95 (round 53) already state
the *predicates* for the code-identity and cited-path counters; this entry does not
restate them and does not supersede them. It adds the *leg-admission procedure* and
the mapping from shortcut class to the observable that must fail — ground the round-53
closure called calibration-harm, held until now as wave receipts and two lesson
Mistake rows, not as an entry.

## The failure it answers

Each row is a counter that returned `met=True` while doing the opposite of its
docstring's question. Receipts are committed wave evidence, not re-runs here.

| Seat (round 53) | Frozen counter's false pass | Receipt |
|---|---|---|
| K1Cheat | A root-owned `LD_PRELOAD` library ran arbitrary code inside the observed server; the counter counted it as the 14th benign "root-owned host file" (honest count 13) and printed `met=True` | `K1Cheat/c1-cheat.out:2,5` |
| Sen1Mem | The counter's archive reference sat same-uid beside the replay's `TMPDIR`; the audited replay rewrote it and the `code` leg compared memory against `ATTACKER-SWAPPED-BYTES` | `Sen1Mem/out-archive-ref.txt:1-12` |
| J7Late | The single `/proc/<pid>/mem` pass samples one instant: a flip 5.1 ms after the counter's `release` file, with the server alive 32.3 ms more, still printed `met=True`; the receipt records the pre-flip digest | `J7Late/race-frozen-counter-evidence.json`, `race-v2-counter-stdout.log` |
| Sen4Fixture | The C2 fixture inherited `GIT_DIR`/`GIT_CONFIG_COUNT`; ten fixture commits landed in a foreign repo (358→368) and a `core.hooksPath` hook executed, with `met=True` | `Sen4Fixture/evidence/03-gitdir-escape.txt`, `07-hooks-exec.txt` |
| J12Hide | Hiding four dead `SKILL.md` citations and deleting their ledger rows left `met=True`, `dropped=0`, `cited` 682→678: the drop leg read `SCORECARD.md` only | `J12Hide/c2-frozen-v_a_skill.out:2` (commit `e7b1b2a2`) |
| J11BadFixed | An `upstream` row at tag `b11909` (bytes `5a4acc9b…`) passed against a `91f48e09…` pin, and `master`, a wrong-but-resolving prefix sha and an unrelated resolving `fixed` replacement all passed | `J11BadFixed/c2-upstream-tagcommit.out:2`, `c2-fixed-launder.out:2`, `upstream-ref-probes.txt` |

## The rule

A hardening leg is admitted only when all four hold. A leg missing any one is a
comment on the counter, not part of its claim.

1. **Named in the output.** The leg prints its own token in the receipt line
   (`envnames=3/3 anon=0 rehash=0`; `dropped=0`), so a reader can see it ran and a
   mutant can be attributed to it.
2. **Killed by a control the previous counter passed.** The change ships with a
   mutant of the *measured* tool (not of the counter) that the pre-hardening counter
   passed and the hardened one fails on that leg: a name in the server's environment
   (`LD_PRELOAD`), an anonymous executable page, a rewritten archive reference, a
   citation hidden outside the guarded surface. A mutant that passes is a *vector
   analysis*, is labelled as such, and is excluded from the kill rule — it never
   counts as a kill.
3. **Outside the measured tree's control.** The hostile input must not be writable by
   the code under audit: the archive is read once and hashed from those bytes
   (`tools/round54-replay-code-audit.py:448-453`), the fixture environment is stripped
   of every inherited `GIT_*` (`tools/round54-cited-path-check.py:198`; S510/S511),
   and no `/proc` read is made for a pid the replay merely names (`:697`; S507).
4. **Its blind interval declared.** A sampling leg states what it cannot see: two
   passes plus a post-exit re-hash, so a flip *and restore* between them, or a rewrite
   after the re-hash, is unobserved (`corpus/lessons/round-55.md` §Mistakes).

Two further conditions belong to the *claim*, not the leg: the base horizon must
contain the change the claim credits (a same-tip base makes the do-nothing control
pass — round 55 reverted exactly that, `dropped=1` at the base), and the counter bytes
measured must equal the frozen `counter_sha256`.

## What each leg buys, and what it still cannot see

- **`anon`** — any executable mapping with no pathname fails (`:499-505`). A stock
  llama-server has none; a JIT or hardening exception would need an explicit range.
- **`envnames`** — the server's environment *names* are recorded and `LD_PRELOAD` /
  `DYLD_INSERT_LIBRARIES` fail the leg (`BAD_ENV`, `:146`). An injected library under
  any other name is caught only if it also creates a file mapping outside the frozen
  set.
- **`hostlibs`** — root-owned host libraries must be in the frozen 13-name set
  (`HOST_LIBS`, `:138`), bound by basename, never byte-compared: a byte-identical host
  install remains indistinguishable, and a root actor who replaces a listed library in
  place is not seen. The set exists because libraries load by path from the tree and
  from the loader's search paths (S509: "default search paths: executable directory,
  current directory"), so the code that runs is not all archive bytes by construction.
- **`code` memory comparison** — reads each executable range through
  `/proc/<pid>/mem` (S506) as the replay's ancestor (S507, Yama scope 1), at most
  64 MiB per row and never zero-padded past a member (`ROW_CAP`, `:145`, `:524`). A
  host at `ptrace_scope` 2 fails closed (`coderuns=0/3`, exit 1) and a host at
  `vm.memfd_noexec=2` cannot run a memfd server at all (S502).
- **`dropped`** — a base-cited token absent at tip on any of the three surfaces needs
  a `fixed`/`externalized`/`superseded` row (`:159`, `:645-656`). It is a
  disappearance check, not a truth check.
- **`upstream`** — a full 40-hex commit, the frozen owner/repo and the digest the
  citing surface states; `master` and tags are refused by construction. It compares
  bytes, never semantics.
- **`fixed`/`superseded`** — the replacement must extend the original stem up to its
  ellipsis and be cited at the base line (`:421-423`); `superseded` covers the other
  direction, a *live* citation re-pointed to a resolving file (`:461-478`).

## Falsifiers

- The entry is wrong if any receipt in §The failure it answers does not print the
  verdict quoted: `check-citations.py` (this proposal's out dir) prints `met=True`.
- The rule's test 2 is wrong if a leg exists whose named mutant prints `met=True` at
  the hardened counter — round 55's battery is the live instance: `m-ldpreload`,
  `m-text-flip` and `m-member-flip` fail their legs (exit 1), while
  `m-ldaudit-foreign` prints `met=True` and is recorded as a void vector, not a kill
  (`.ufo/waves/round-55/c1/battery/m-ldaudit-foreign.out:2`).
- Test 3 is wrong if the audited process can rewrite the reference the leg compares
  against; test 4 is wrong if a flip-and-restore inside the declared interval changes
  the verdict (J7Late run1b measured no change — consistent with the declared limit,
  not a refutation).

## KQ compliance

- KQ1/KQ4: no endpoint is contacted; every number here is a receipt over committed
  bytes or a counter's own output, never a present runtime claim.
- KQ6: every mechanism statement names its page/commit and section (S506/S507/S508/
  S500/S501/S502/S509/S510/S511, all opened with committed copies); tier A for the
  kernel/man pages, B for the two git documentation rows, and no C row supports the
  entry.
- KQ9: absences are "not observed by this leg", never "does not exist" — the blind
  intervals are stated per leg.
- KQ10: no census or probe ran for this entry; the cited runs were made by the named
  seats in their own scratch.
- KQ12: overlap with KQ94/KQ95 is named above; this entry adds no new predicate row.
