# Round 49 — N1Overlap sibling-overlap scan (kama lane)

**Verdict:** No sibling lane under `/home/vgpnk/Projects/shokunin/*-shokunin` reproduces any of the five round-49 kama mechanisms — a live-server execution-witness handshake (server writes `ready.json`, holds until release), `/proc/<pid>/exe` hashing, a nonce challenge to a running server, tar-member sparse/size provenance bounds, or an origin-aware append-only deletion audit — but five lanes hold partial, adjacent mechanisms worth citing when the round-49 knowledge lands: **chousa** (execution-witness tools for gates), **kumitate / mori / tabi** (nonce anti-replay), **kaidoku** (bounded tar-member extraction + sparse-file size-bound fixtures), and **mori / souji** (append-only monitors over SOURCES.md / SCORECARD.md).

## Method (commands, all read-only)

Scanned the 20 sibling lanes (`glob /home/vgpnk/Projects/shokunin/*-shokunin` → 20 lanes, kama excluded as self) at their four named scopes: `<lane>/corpus/SOURCES.md`, `<lane>/SKILL.md`, `<lane>/tools`, `<lane>/registry`. Commands (each run once per pattern across all 20 lanes; `gitignore=false`; missing paths reported and skipped by the tool):

- `grep pattern='proc/.*exe'` — exe/proc references
- `grep pattern='tokenize' case=false` — tokenization
- `grep pattern='nonce' case=false` — nonce
- `grep pattern='sparse' case=false` — sparse (paged 2×)
- `grep pattern='append-only-contract'` — exact contract token; **0 matches**
- `grep pattern='\borigin\b' case=false` — origin (tools-only second pass)
- Follow-up feature passes: `grep pattern='witness|ready\.json|hold_for' case=false`; `grep pattern='readlink|/exe\b' case=false` (paged 2×); `grep pattern='llama|gguf|detokenize|/tokenize' case=false`; `grep pattern='tarfile|tar\.open|pax|archive.?member|is_sparse|member.*size|size.*member' case=false` (tools-only); `grep pattern='append-only|appendonly|launder|ungraded|exempt' case=false` (paged 2×).

Scope notes: **no sibling lane has a `registry/` directory** (all 20 were reported by the grep tool as skipped-missing paths; only kama itself has `registry/`). The four lanes that keep code outside `tools/` were additionally swept for the same markers: `kake/scripts`, `kumitate/scripts`, `tabi/scripts`, `kotoba/verifiers` (`grep pattern='witness|ready\.json|nonce|/exe\b|readlink|append-only|sparse|llama|tarfile' case=false`, paged 2×). `kasegi/c2-controls/` contains only `junk-f20.md` (no code).

---

## 1. Execution witness (server ready-marker + hold/release)

**No match** for `ready.json` or `hold_for` anywhere; no release-file handshake, no server-side witness file. Closest partial mechanisms:

- **chousa** — dedicated execution-witness *tools*, but they witness a shell gate's matcher-route execution, not a live server:
  - `tools/argv-witness.py` (SKILL.md:99; tool docstring lines 2–36): runs the candidate gate with a distinct-path GNU-reporting recorder as `RESEARCH_GATE_GREP`, counting per-record matcher invocations; "It never inspects the gate's stderr" (line 28). Proves routing/attribution, not computation.
  - `tools/mechanism-witness.py` (SKILL.md:100; tool lines 2–37): `bash -x` + private PS4 trace stamps matcher entry lines; `WITNESS=pass|fail OUTPUT=n/9 STAMPS …`.
  - R35/R36 counters `WITNESS_SEPARATED=2/2 LANDED_WITNESS=pass`, `WITNESS_PER_RECORD=5/5` (SKILL.md:94–95).
- **kaidoku** — "witness" is evidence terminology: "Bound local witness; not cryptographic authentication" (SKILL.md:874), "The active C1 witness is the original CLI envelope" (SKILL.md:918–921), archived "residual witness registry" (SKILL.md:1303–1308).
- **kumitate** — "text-mode witness" = a selftest verdict axis independent of suite expressions (`scripts/cite-check.mjs:2676–2704`); not a server handshake.
- **tabi** — "Promise is deliberately held | Intermediate active state and release-before-response sequence" (SKILL.md:2420) describes WebMCP submission semantics, not a server handshake.
- **mado / kagi** — "witness" only as prose ("the printed names witness the config at creation", `tools/mado-devices.py:15–16`; "one read-only witness of the compositor's advertised protocol set", `tools/mado-globals.py:5–6`; kagi `SKILL.md:43` health-check line).

No overlap with C1's `witness` `{released, waited_ms}` receipt block or `kama-live-replay.py --witness-dir/--witness-timeout` interface.

## 2. /proc/<pid>/exe hashing

**No lane reads or hashes `/proc/<pid>/exe`.** Every `exe` substring hit is either the word `execve` (e.g., tsukuroi SOURCES.md S181, col 349 → "execve(2)") or `readlink`-based symlink canonicalization (chousa `research-gate.sh` lines 384–387, 1027–1031, 1825–1829, 3306–3311; mado `verify.sh` lines 2033–2035, 3721–3730; souji `cand-*.sh` `canon_path()/real_path()`; tsukuroi `boot-chain-audit.sh:387–391`). Adjacent:

- **tsukuroi** `tools/score-selftest-literals-r40.py:53` **forbids** scripts from referencing `/proc/self/(exe|fd)` (`SELFREF_RE = re.compile(r'\$\{?SELF|BASH_SOURCE|\$0\b|/proc/self/(exe|fd)|/proc/\$\$')`) — the opposite of using it.
- **kengaku** pins a serving stack's *identity* via `/proc/<pid>/cmdline`, not exe (SKILL.md:491–499): "Serving-stack facts are process-pinned as of round 10 (pid 1299; `/proc/<pid>/cmdline` == … ExecStart, 41 tokens, EXACT_MATCH) … a hermetic gate must never read `/proc` — pin committed bytes instead." That is the closest semantic neighbour to C1's identity pin, but it is historical, cmdline-based, and explicitly non-live (SKILL.md:501–505).
- **mori** uses `/proc/<oracle>/environ` and `/proc/<oracle>/fd/1` as leak channels to close (`tools/mori-silence-cases.sh:94–104`), not as hashing targets.
- **souji** sources `proc_pid_fd(5)`/`readlink(2)` for `readlink -- /proc/<pid>/fd/1` string semantics (SOURCES.md S225 lines 172, S082–S086; SKILL.md:159).

## 3. Nonce challenge to a running server

No sibling challenges a running local server with a fresh nonce (no `/tokenize`, no `detokenize`, no GGUF-vocab decode anywhere; `llama` appears only in kengaku/kagi/kotodama as described below). Nonce machinery exists in five lanes, all aimed at *fixture/receipt replay*, not server liveness:

- **mori** — the closest in spirit on the anti-replay axis: per-run fixture nonce `RUN_NONCE` woven into every fixture body/name, required to be echoed by the census output, with stale/missing tokens failing cases; pins `MORI_RUN_NONCE`. See SKILL.md:330–346; `tools/mori-silence-cases.sh:35–45, 84–91, 168–174, 200–219`; `tools/mori-round13-regressions.py:1095–1096, 1539–1541, 3240–3242`. Explicitly a *fixture/target token*, "not a clock shift" (line 168–169).
- **kumitate** — receipts carry a 128-bit nonce; `--stdin` delivers it to the child and records `stdin_sha256`; a ledger scan treats a nonce bound to a different record digest as `REPLAY` (`scripts/receipt-attest.mjs:5–36, 98–110, 169–203, 346–350`; `scripts/receipt-evidence.mjs:20–44, 191–208`; SKILL.md:620, 624).
- **tabi** — browser-automation counters use case nonces in fixtures/evidence to defeat replay ("defeating the demonstrated nonce-aware no-invoke specimen", SKILL.md:2195; "counter-owned nonce/artifact mutants" :2099; "wrong nonce or unrelated event" :2418).
- **chousa** — nonce-prefixed fixture dirs and "nonce packages" in C1 supplements (SKILL.md:130, 132–135).
- **kasegi** — "volatile nonces replaced" during scope-snapshot sanitization (SKILL.md:61–62).
- **kengaku** — operates a llama.cpp serving stack (qwen-coder, `:34113`) but pins it via cmdline (see §2) and tests against mock endpoints first ("Smoke: … against a **mock endpoint first** … then the live endpoint", SKILL.md:734–735). **kagi** health-checks a llama-server endpoint with `curl -fsS <endpoint-minus-/v1>/health` (SKILL.md:42–43). Neither hashes the binary, challenges it, or holds it open.

## 4. Tar sparse/size bounds

No sibling validates tar members for sparseness or declared-size-vs-actual equality *before hashing* (kama's `verify_archive_member()`). Closest:

- **kaidoku** `tools/round-42/fetch-carrier.py:408–475` — the nearest functional kin: `_tar_member()` requires the member to be a regular file (`not m.isfile()` → `ChainError('member', … not a regular file')`), `_bounds(carve, m.size, 'tar member')` refuses carves past the member's declared size, and `digest_and_slice()` streams with `total != m.size → ChainError('member','tar member short: %d of %d bytes')` plus `member_sha256` binding (lines 466–475). Motivation is REA carrier carving, and there is no sparse-file check. Same lane also parses SquashFS sparse blocks (`tools/round-37/…/sqfs-list.py:70–71, 494–497`; round-39/40/41/42 copies).
- **kaidoku** `tools/round-31/c2-sqlite-refusals.py:109–129` + SKILL.md:1259–1260 — creates *sparse* SQLite db/`-wal` files of exactly `BUDGET+1` = 268,435,457 bytes to exercise a combined-256-MiB snapshot-budget refusal. Same idea space as "sparse defeats a size bound", inverted (they forge sparse files; kama refuses them).
- **tameshi** `tools/mte-interop.py:176–215` — `verified_tarball()` sha512-gates the whole tarball before reading members, then enforces member-path safety (no absolute/`..` paths, only regular files/dirs) when unpacking vendor packages (lines 204–215).
- **tsukuroi / mori / tameshi probes** — `tarfile.extractall(filter='data')` for `git archive` materialization (e.g., tsukuroi `probe-child-env-allowlist-r36.py:422–425`, `mutants-adjacency-overlap.py:66–67`; mori `mori-routed-r24.py:485–488`); no custom member bounds.
- **kake** `scripts/source_recheck_hardening_selftest.py:194–197, 241–243, 315–317` — sparse fixtures (`huge.json`/`body.bin` truncated to 1 GiB) inside `rlimit_as` memory-bound tests; sparse as an adversarial fixture, not a member check.

## 5. Origin-aware append-only audit

`append-only-contract` (the kama C2 schema token) has **zero occurrences** across all sibling scopes. No lane decides whether a deleted line stays ungraded by where its text was born; no `launder`/`ungraded` audit logic. Closest:

- **mori** `tools/mori-sources-appendonly.py` (SKILL.md:887–895, 903, 912) — a SOURCES.md append-only gate that *lists in-place edits (`ids`) and deleted rows (`deleted`)*, derives `round_changed` from first-parent edit detection, and emits supersede-timing lines (`supersede_timing superseded_as_of=[…] stale_supersede=[…]`, r38). Closest deletion-audit function; no section-origin exemption.
- **souji** — append-only enforcement over SCORECARD.md/SHONEN.md: `tools/souji-capability-agreement.py:29–30` ("if SCORECARD.md … at REV does not begin with its --base bytes, every K1 … item is a mismatch (fail closed)"); `tools/souji-record-agreement.py:17–18, 63–66` ("filed bytes are append-only"; deleting a filed occurrence is a mismatch; K2 section-sha256 record requires byte-identical sections, corrections only as later acts); `tools/souji-registry-agreement.py:15–18` (blob-prefix append-only + `R29-CORRECTION` line ledger); `r32-c1-counter` verdict `MISMATCH(append-only-violated)` (SKILL.md:258). **Stricter** than C2 (any prefix change fails), and not origin-aware.
- **chousa** — `APPEND_SERIALIZED=24/24` and `EXEMPT_AUDIT_MATCH=132/132` counters (SKILL.md:90–91, 102) audit whether *status-exempt citation hops* would have verified (`observed=resolvable`, `CHAIN_EXEMPT_RESOLVABLE`, `research-gate.sh:106–131`); an exemption audit, but over citation chains, not deleted text.
- **kake** — `wave-evidence-ledger` C8 reads the mirror *bytes* and requires append-only equality with the measured registry minus adopted rows (SKILL.md:1216).
- **mado / kasegi** — append-only as a *protocol*: errata/re-anchor sections ("Errata append-only; rejections kept", mado SKILL.md:38, 354, 1006–1007, 1983–2048), JSONL ledgers with `O_APPEND` 3500-byte line cap (kasegi SKILL.md:224–235, 999–1002). No automated deletion grading.

---

## Risk note (for the L1 integration, not a defect)

The round-49 C1/C2 machinery is not duplicated anywhere, so no sibling can be drafted as a reviewer/borrower without building context. The converse risk: **souji's** append-only counters and **mori's** `mori-sources-appendonly.py` are the two instruments most likely to be confused with kama's C2 by an integrator (same surface: append-only audit of lane markdown); the distinguishing features are kama's section-origin exemption (v4), whole-word binding, negation-unbind, and wildcard-row rule, none of which exist in either lane. Similarly **kengaku's** `/proc/<pid>/cmdline` pin is the nearest prior art to C1's exe-hash identity pin but is explicitly non-live and deliberately avoids /proc in gates — cite it in lessons as the boundary case.

## Evidence index (file:line cited above)

All citations are to files as they exist on disk at scan time (2026-10-26); `read`/`grep` outputs are the source of every line number. No counter was run; no files were modified; no tools installed.
