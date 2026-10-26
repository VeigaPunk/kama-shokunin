# U0Consumers - readers and documents the round-49 build changes (lane commit 74558c71, base 438127bc)

Verdict: no reader is broken by the new signature or the `witness` block; the live-tool and replay chain is green end to end. Two instruments the build leaves red or stale: the round-48 C1 counter (`round48-append-audit-v3-check.py`) now exits met=False at the tip, and `witness` is read by nothing (a validator, the compare, and the replay all accept any value). Eight documents state things the build made false or out of date. The lane working tree was moving during the seat (L1 integrating: SKILL.md, README, QUALITY, lifecycle knowledge, contract, three tools show `M`); line numbers below are at commit 74558c71 unless marked `[wt]`.

Method: `git grep` over tools/ tests/ SKILL.md corpus/ registry/ (excluding .ufo history) for the eight terms, then ran each consumer in my own `git clone --shared` (`/fast/scratch/hyaku/kama-r49/U0Consumers/lane`, removed at end). No lane file edited.

## 1. Callers of `verify_archive_member` (signature gained `server_size=None`)

| site | what it passes | affected? |
|---|---|---|
| tools/kama-llamacpp-live.py:1664 (main, v5 record-time) | 5th arg `os.path.getsize(server_real)` | no - the only production caller; size is always passed |
| tools/kama-llamacpp-live.py:1374 (`_provenance_selftest`) | 5th arg `os.path.getsize(srv)` | no |
| tools/kama-llamacpp-live.py:1395 (`verify_archive_member(*args)`, token grid) | 4-tuple rows (digest-mismatch, member-absent, not-a-file, member-digest-mismatch, sparse, not-regular) + one 5-tuple (size-mismatch) | works only because each 4-tuple dies before the size check |
| tools/round49-replay-witness-audit.py:11 | prose only (R1 description); the counter's `cap` legs drive the CLI (`--server` file, so size is passed) | no |
| tools/kama-live-replay.py | does not import it; its own `extract()` (`tarfile.extractall(filter="data")`, :151-153) and `acquire()` are digest-gated but have no size/member bounds and `fetch()` (:91-98) no byte cap | no break; the R1 bounds do not cover the replay's own archive path |
| corpus/QUALITY.md:410 (KQ74), corpus/lessons/round-48-verifier-spotcheck.md:110 | name the function | docs only |

Finding A1 (design, not a defect today): `server_size=None` is a silent opt-out. A future caller that forgets the argument skips `provenance-member-size-mismatch` and reaches the hash loop with only the sparse check. Proposed fix: make `server_size` a required positional (`def verify_archive_member(archive, asset_sha256, member, server_sha256, server_size)`) and update the six 4-tuples at :1395 (they would then need a size; pass `1` or `os.path.getsize(srv)`). Do this only if the lane wants the check structural; it is not needed for the C1 counter, which goes through the CLI.

Finding A2 (wt, observed): the working tree rewrites the function to `os.open(O_NONBLOCK)` + `fstat` on one descriptor (seat V1Live F1) and adds a `many.tar` selftest row for `provenance-archive-too-many-members`. Same signature; the 4-tuple grid at :1395 is unchanged in shape. No new consumer break.

## 2. `witness` block / `--witness-dir` / `ready.json`

Producer: `hold_for_witness()` tools/kama-llamacpp-live.py:280; receipt write :1862 (`receipt['witness']`, then `verify_live(... 'post-witness')` re-grades listener ownership); flags :1264 (`--witness-dir`, `--witness-timeout`), parse check :1582. Passthrough: tools/kama-live-replay.py:275-281 (also adds `res["witness_dir"]`, extends subprocess timeout by `witness_timeout`). Observer: tools/round49-replay-witness-audit.py:298.

Readers of a live receipt and what each does with an unknown top-level key `witness`:

| reader | result (executed) |
|---|---|
| tests/llamacpp-live/check-receipt.py (top-level checks by key, no exact-key-set check) | VALID for a real witnessed receipt (`receipts/wit-receipt.json`), for `witness: "garbage"` (`receipts/w-junk.json`) and for `witness: {"released": false, "waited_ms": 120000}` (`receipts/w-unreleased.json`) |
| tools/kama-live-replay.py `--compare` (`projection()` :168, `compare()` :198) | `compare match=True mismatches=0` against all three; witness is deliberately not compared (module docstring :45) |
| tools/kama-live-replay.py `replay()` | reads the rerun receipt, never reads `witness`; match is independent of it |
| tools/round47-live-replay-audit.py, round48-live-replay-v5-audit.py | consume replay JSON by key (`schema == kama-live-replay/v1`, `rerun_receipt`); the extra `witness_dir` key is ignored. Both still met=True at the tip (below) |
| tests/llamacpp-live/{install-*-grid,unpinnable-e2e,controls}.py | drive the tool or `check-receipt`; none enumerates receipt keys |
| `argv` check (check-receipt.py:651-702) | `argv` is the llama-server argv, which `--witness-dir` does not change; no impact |

Findings:
- B1 (check-receipt does not know `witness`). check-receipt.py's docstring (:2-8) says it is "bound to the exact receipt keys emitted by tools/kama-llamacpp-live.py"; after this build the producer emits a key the validator neither requires nor type-checks, so `witness` can be forged or malformed in a committed receipt and still read `VALID`. Fix: when `witness` is present require `schema == "kama-live-witness/v1"`, `port`/`pid` ints equal to `receipt.port` and `receipt.child_pid`, `released` bool, `waited_ms` int >= 0; reject a non-object. Add the mutation rows to the selftest (`selftest: 16 VALID and 1 NOT-EVALUATED receipts accepted; 107 mutations...` count then changes).
- B2 (`released` is not evidence an observer ran). `receipts/wit-stale.json`: re-running the tool on a `--witness-dir` that still holds `release` from an earlier run gives `released: true, waited_ms: 0` and a fresh `ready.json` the observer never read (command in section 6). Anyone consuming `witness.released` as "an outside party looked" is wrong; only the C1 counter's out-of-band observation proves that. Fix: `hold_for_witness` refuses (or unlinks) a pre-existing `release`/`ready.json` at entry; the replay docstring (:41-45) and SKILL row should say `witness` is self-reported timing, not an attestation.
- B3 (receipt embeds a host path). `witness.dir` is the absolute witness directory (`/fast/scratch/...` in my run). A committed witnessed receipt therefore carries a scratch path (cf. corpus/QUALITY.md:386 KQ66, which treats host paths in receipts as needing a re-fetch locator). Minor; fix: record `dir` as basename or omit.
- B4 (timeout doc). tools/kama-live-replay.py:41 and SKILL.md:1475 say `--timeout` "bounds the live child only"; with `--witness-dir` the bound is `timeout + witness_timeout` (:281-283). The docstring now says so at :42-43; SKILL.md:1475 does not (it has no `--witness-dir` flag at all).

Executed regressions at tip 74558c71 (all in my clone, exits observed):
- round48-live-replay-v5-audit.py: `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True`, rc 0.
- round47-live-replay-audit.py: `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True`.
- round49-replay-witness-audit.py (C1): three witnesses ok (`exe+listen+model ok`, nonce round-tripped), `cap sparse-1e15 ... provenance-member-sparse`, `newrow: ... S494`.
- kama-live-replay --selftest `KLR_SELFTEST pass=22` at the commit (pass=23 in the working tree: a new witness-passthrough case); kama-llamacpp-live --selftest ok; check-receipt --selftest ok.

## 3. `append-only-audit/v3` string and the `definition: v4` key

Tool: tools/append-only-audit.py `SCHEMA` :135 (unchanged), `"definition": "v4"` in the result dict :504.

| consumer | at tip 74558c71 |
|---|---|
| tools/round48-append-audit-v3-check.py:411,600 (requires schema `append-only-audit/v3`) | accepts the schema and ignores the extra `definition` key, but the counter **now reports met=False**: `lane=0 ... detail: lane: 0718b6abbda6 SCORECARD.md ungraded tool=65 counter=72` (also graded 2356 vs 2349, restored_max, held_at_to, summary ungraded_lines tool=82 counter=89). Same counter at the base 438127bc: `lane=1 ... met=True`. Cause: the counter's own `binds()`/origin model is the v3 rule (tools/round48-append-audit-v3-check.py:226-233) and now disagrees with the tool by exactly the 7 lines v4 grades. |
| tools/round47-append-audit-v2-check.py (schema `append-only-audit/v2`, :381,538) | met=False at the base and at the tip, identically (contract header mismatch + tool exit 2) - superseded before this round |
| tools/round46-append-audit-check.py | met=False at base and tip, identically - superseded |
| tools/round49-append-audit-v4-check.py (C2) | the contract; frozen |
| SKILL.md:1473 row `Round-48 append-only audit v3` | stale: states `AOA_SELFTEST pass=28`, `ungraded_lines 89`, no `definition` key, no v4 rules. Measured now: `AOA_SELFTEST pass=30 fail=0` (commit and working tree), lane summary `ungraded_lines=82`, `ungraded=0`, exit 0 |
| SCORECARD.md:2790 canonical-list row `append-only-audit` (round-48 wording; capability-repertoire-audit.py only checks that an evidence path resolves, it will not flag the wording) | v3 wording; v4 changes the binding and the exempt-region rules it describes |
| corpus/README.md:916 "schema `append-only-audit/v3`" prose, :979-991 pointers into `append-only-audit.py:396,119,171-174` and `binds()` of the v3 counter | historical for round 48; any round-49 prose should say "schema string unchanged, definition v4" |
| corpus/QUALITY.md:408,422,423 pointers `append-only-audit.py:190-199`, `:409-411`, `:423-441`, `:202-207` | the KQ footer at :404 only discloses commit-anchoring for kama-live-replay.py and kama-llamacpp-live.py; the append-only-audit pointers are not disclosed, and at the tip they land on other code (`:202` is `row_token`, was `line_at`; `:190` is a contract-parse line, was `binds`). Fix: add append-only-audit.py to the :404 sentence or re-cite as `git show 380bcdff:tools/append-only-audit.py` |

Finding C1: the round-49 regression sweep must list `round48-append-audit-v3-check.py` at the tip as an expected superseded red (v3 counter vs v4 tool, 7 lines on one event), not as a regression of the tool; otherwise the SCORECARD regressions line will read red against a green lane. Evidence: commands in section 6.

## 4. `definition` (generic term) - non-consumers

All other `definition` hits are unrelated prose/tests (SOURCES.md rows, lessons, tests/gguf-identity "Identity key definitions"). Only append-only-audit.py:2,6,43,65,98,504 and its counters use it as the v-tag.

## 5. `binds(`, `row_token`, `NEGATIONS`

- `binds(` callers in the tool: tools/append-only-audit.py:257 (`declaration()` first pointer), :268 (the `only=` pointer). Both pass `decl_path`; the v4 wildcard rule depends on it. No other file imports the tool's `binds`.
- `row_token` called only from `binds` (:237).
- `NEGATIONS` (:146) and the new `NEG_WINDOW` (:212) only inside `binds`.
- Counters have their own copies: round48 `binds` :226, `row_binds` :236,253,378,692; round49 `binds` :120,304 (frozen).
- Contract rows and v4 binding, evaluated at the tip with the tool's own `binds()` (`registry/append-only-contract.tsv`): LOG.md via token `LOG` in README.md:16; SCORECARD.md and corpus/QUALITY.md via tokens in corpus/README.md:761; corpus/README.md, registry/history/DELTA.md, registry/report-landing-errata.tsv, corpus/knowledge/{consumer-registry,error-is-not-a-verdict}.md by self-declaration (exact rows); corpus/SOURCES.md via token `SOURCES` in SKILL.md:578; `corpus/lessons/*.md` is a wildcard row: at the tip it binds through the token `lessons` in the KQ26 criterion corpus/QUALITY.md:143 (a criterion row, not a lesson-file declaration; the working-tree contract already re-anchors it to corpus/README.md:1239 - round-49 seat K2Binding). `bad_declarations=0` at the tip; all 10 rows also bind in the working tree.
- Fragility, not a defect: three rows are anchored by line number into files that are edited in place, not append-only: README.md:16 and SKILL.md:578. An insertion above either line unbinds the row (`declaration ... does not say append-only`, exit 1). The round-49 SKILL.md rows must be appended after line 578 (they are: registry tables end past 1470) and README.md must not gain lines above 16.
- Known v4 limits (not re-reported, tool header lines 16-24 already list them): trailing negation, comma-broken window, `no edits append-only`.

## 6. Documents the build made stale or false (file:line at 74558c71, what changes)

| # | file:line | now wrong / missing | what it should say |
|---|---|---|---|
| D1 | SKILL.md:1473 | `AOA_SELFTEST pass=28`, lane `ungraded_lines 89`, v3 rules | pass=30 (commit; check working tree after integration), ungraded 82, `definition: v4` rules and the new `round49-append-audit-v4-check.py` as the counter |
| D2 | SKILL.md:1474 | setup-error token list stops at `provenance-member-digest-mismatch`; no bounds | add `provenance-archive-not-regular`, `-archive-too-large`, `-archive-too-many-members`, `-member-sparse`, `-member-size-mismatch`, `--witness-dir`/`--witness-timeout` flags, caps 1 GiB / 4096 members; this is the only non-tool doc that lists the tokens (git grep) |
| D3 | SKILL.md:1475 | replay row: usage lacks `--witness-dir`/`--witness-timeout`; output key list lacks `witness_dir` (and already lacked `live_exit`, `notes`); `KLR_SELFTEST pass=22` (23 in the working tree); "`--timeout` bounds the live child only" | add flags, key, count, timeout sentence (B4) |
| D4 | SKILL.md (no row) | neither `tools/round49-replay-witness-audit.py` nor `tools/round49-append-audit-v4-check.py` registered (known; listed for the gate: `gate-registry-check.py` will print two `unregistered` lines) | known item |
| D5 | SCORECARD.md:2790, :2791 | canonical `append-only-audit` and `live-receipt-replay` rows describe v3 binding and a replay without a witness | reword in the round-49 canonical list; leave the round-48 table byte-intact (append-only) |
| D6 | corpus/README.md:1033-1039 and :1065 | "witnesses no process ... A replay tool that ... synthesises a rerun receipt ... would satisfy every replay condition" and frontier item "An execution witness in the replay leg" | claim C1 closes this; README is append-only: add a correction, do not edit; the 1065 frontier item moves to "closed round 49 (S494, S495) for the C1 counter, leg not required of every replay" |
| D7 | corpus/knowledge/llamacpp-loading-lifecycle.md:444-447 ("What the replay still cannot show", "Instance facts are not reproduced"; the listener ownership/pid facts are now observed from outside during a witnessed replay) | append a round-49 paragraph: `--witness-dir`, ready.json {schema, port, pid}, what the counter observes (/proc/<pid>/exe digest, LISTEN inode, `-m` hash, nonce round-trip through /tokenize + /detokenize) and what it still cannot (witness fields are tool-reported; `released` can be pre-set - B2) |
| D8 | corpus/QUALITY.md:410 (KQ74) pointers `kama-llamacpp-live.py:71`, `:1475-1479` | footer :404 covers them by naming 380bcdff; `:71` is now `import shutil` and `:1475` blank at the tip. OK as long as the footer stays | none, unless KQ rows are re-cited |
| D9 | corpus/QUALITY.md:404 footer | omits append-only-audit.py (see section 3) | extend the sentence |
| D10 | corpus/SOURCES.md S494/S495 `used-by` | names corpus/lessons/round-49.md, which exists only in the working tree (`??`) | lands at integration (known) |
| D11 | tools/kama-live-replay.py:41-45 docstring and tests/llamacpp-live/check-receipt.py:2-8 docstring | replay docstring correct; check-receipt docstring ("exact receipt keys") is false for `witness` (B1) | fix with B1 |
| D12 | corpus/lessons/round-48-verifier-spotcheck.md:110,115 (R1, R5 routed items) | historical; correct as filed | none; round-49 lesson should cite the closure |

Not stale (checked): no committed file pins the sha256 of kama-llamacpp-live.py, kama-live-replay.py or append-only-audit.py (searched 12-hex prefixes of the base and tip digests outside .ufo: no hits), so no pin moves. Committed round-47/48 receipts carry the old `tool.sha256`; unchanged by this build and ignored by `--compare` (replay only records a `notes` line).

## 7. Receipts

In `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/U0Consumers/receipts/`:
- `wit-receipt.json` - real witnessed run (b11909 install, stories260K, `--witness-dir`, released after ready.json): `witness {released true, waited_ms 100, pid, port}`, outcome pass, check-receipt VALID.
- `ready.json` - the ready.json of the stale-release rerun (schema kama-live-witness/v1).
- `wit-stale.json` - same tool, `--witness-dir` still holding `release`: `released true, waited_ms 0` (B2).
- `w-junk.json`, `w-unreleased.json` - round-48 receipt-1 with `witness` set to junk / `released false`; check-receipt VALID and `--compare` match=True (B1).

Commands (cwd my scratch, `TMPDIR` my scratch, `HOME=/home/vgpnk`): `python3 .../round48-append-audit-v3-check.py --repo <clone> --tip <74558c71...>` then the same with `--tip 438127bc01ff...`; `round47-live-replay-audit.py`, `round48-live-replay-v5-audit.py`, `round49-replay-witness-audit.py --repo <clone> --tip <full> --scratch <s>`; the stale-release probe is `kama-llamacpp-live.py --server ~/.local/opt/llama-b11909/llama-server --model ~/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1b...256d --out wit-stale.json --witness-dir <dir holding release> --witness-timeout 60`. Leftover check: no llama-server of mine remains. Tools installed: none.
