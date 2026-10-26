# Sibling-overlap scan — round 46, seat N1Overlap (report)

Full findings: `.ufo/waves/round-46/w1/out/N1Overlap/overlap.md` (identical content below).

**Verdict:** No sibling lane holds llama.cpp b11906/b11889 ground; four sibling lanes hold *older* llama.cpp `server-context.cpp` ground at commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (verified ancestor of b11889, rc=0); append-only/history audit tools of their own exist in ≥8 sibling lanes (closest analogues to kama's C2: mori, souji, kaidoku, tsukuroi, kake, kotodama, lore, kotoba).

## Method (commands)

- `grep` (gitignore=false, hidden=false) over every sibling lane's `corpus/SOURCES.md`, `SKILL.md`, `tools/`, `registry/` for: `b11906`, `b11889`, `server-context`, `append[- ]?only|truncat` (case-insensitive for the last). Result: `b11906`, `b11889`, `server-context` → **No matches found** in these four areas in all 21 sibling lanes.
- Full-tree `grep` over all sibling lane roots for `b11906|b11889` and `server-context|server_context`, and for `release-recheck|release_recheck|append-only-audit|append_only_audit`.
- Read-only git on the shared llama clone (`/fast/scratch/hyaku/kama-r46/L1/llama.git`): `git log --oneline -1` for `704366d`, b11889 (`d854d98b`), b11906 (`4d71b42f`); `git merge-base --is-ancestor 704366d d854d98b` → rc=0 (704366d predates b11889); `merge-base --is-ancestor d854d98b 4d71b42f` → rc=0 (b11889 predates b11906).
- No tools were installed (no installs to record).

## 1. b11906 / b11889 ground — none in any sibling lane

- `b11906`: zero hits anywhere in 21 sibling lanes (four target areas and full tree).
- `b11889`: zero real hits. The only full-tree matches are coincidental substrings inside sha256 hex digests, not release ground:
  - `mori-shokunin/.scratch/round22/measure2/mutant-finding-unchecked-refine.json:3230` and `.ufo/waves/round-22/evidence/measure2/mutant-finding-unchecked-refine-observed.json:3230` — `…51218a3d7665cb11889` (hex digest ending in `cb11889`).
  - `audio-shokunin/corpus/live/r98-boundary/MANIFEST.sha256:530` — `…adecbb11889d99df149a188eedd` (hex digest substring).
- No sibling lane has a `registry/` directory at all (every such path was "Skipped missing" in the target-area scans); sibling registries live only in `corpus/SOURCES.md`, which contains no b11906/b11889 token.

## 2. llama.cpp `server-context.cpp` ground — present in 4 siblings, all at the older pin `704366d`

All references trace to kama's own round-44 SOURCES rows (fleet census / overlap artifacts), pinned at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` — verified ancestor of b11889 — never at b11889/b11906. No sibling holds an independent llama.cpp release recheck ledger (grep for `release-recheck` across siblings: zero hits).

- `mado-shokunin/.ufo/waves/round-44/w2/RerunCensus/census-fleet.txt:94-141` — fleet source-census duplicate-URL findings on kama rows: `S060 … tools/server/server-context.cpp … across scopes` (:95), `S109` (:118), `S114-S125` (:121-132), `S133` (:138), plus `server.cpp` (S108), `server-common.cpp` (S127/S137), `llama-context.cpp` (S130/S132), `gguf.cpp`, `arg.cpp`, `README.md` — all at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`.
- `kotoba-shokunin/.ufo/waves/round-71/receipts/census-after.txt:91-136` — same fleet census artifact (kama S060, S109, S114-S125, S133 etc. at 704366d).
- `kumitate-shokunin/.ufo/waves/round-57/build/ConnectorSiblingOverlap/commands.txt:51-54` — `L129 S117 llama.cpp server-context.cpp @ 704366d L5453`, `L130 S118 … L6132`, `L131 S119 … L6137`, `L132 S120 … L6151`; `entry-with-paragraph.scratch.md:40` and `proposed-paragraph.md:3` state explicitly: "kama's S117-S120 are llama.cpp server-context.cpp errors at 704366d, not Temporal/Kafka/Kubernetes/RabbitMQ"; `w1/ConnectorSiblingOverlap.md:29` repeats it.
- `kake-shokunin/.ufo/waves/round-43/w1/ConnectorOverlap.md:52-56` — records kama llama.cpp sources (`server-context.cpp:3702+`, imported upstream code) as residual "shared prefix" hits, alongside "lore's append-only byte-prefix registry checks (.ufo/waves/round-96/seats/V53-byte-prefix-2.md:67-78)".
- False positives (HTML framework attribute, not llama.cpp): `tabi-shokunin/.ufo/waves/round-27/scratch/QuarantineD/S174.body:1440`, `kotodama-shokunin/reports/supplement-opencode-1/scratch/round5-13/evans2003b.pdf:11`, `source-recheck-registers-19/errington_item.html:22` — `ng-server-context="ssr"` Angular attributes.

## 3. Append-only / history audit tools of their own (file:line)

Sibling lanes implement their own append-only/history audit instruments; none is identical to kama's `tools/append-only-audit.py` (git-history mass-deletion scan), but several serve the same purpose:

| Lane | Tool / location | What it checks | Evidence |
|---|---|---|---|
| kaidoku | `tools/round-38/registry-immutable.sh` | SOURCES rule-2 append-only: only `status`/`recheck`/`used-by` may change; variant adds row-deletion + reorder detection; selftest on fixture repo; exit 0/1 | :2-6 (docstring), :10-19 (variant/self-test), :90 (`run_case append-only 0 …`), :110-114 (`"row deleted (append-only)"`, `"row reordered (append-only)"`) |
| tsukuroi | `tools/check-appended-notices.py` | "Read-only structural verifier for append-only round-18 correction notices": authenticated registry records vs immutable Git blobs (declared bytes, append boundary, notice section, capture line) | :1-7 |
| tsukuroi | `tools/check-freshness-r17.py` | freshness gate: target file must still start with baseline bytes "(append-only history)"; baseline_quote exact substring; notice-heading rules | :12-16 |
| mori | `tools/mori-sources-appendonly.py` | CORPUS.md rule-2 gate walking git history of `corpus/SOURCES.md`: immutable-cell edits (`ids`), `deleted` rows, superseder timing; `appendonly_violations = len(ids)+len(deleted)`; exit 0/1/2; read-only git (`rev-parse`/`log`/`show`/`merge-base`) | :1-11, :34-51 |
| souji | `tools/souji-registry-agreement.py` | K2 stale statements must be "append-only by bytes (blob at REV starts with the blob at --list-rev)"; K1 row-deleted detection; reads only `git cat-file`/`ls-tree`/`show` | :15-22 |
| souji | `tools/souji-record-agreement.py` | "filed bytes are append-only": deleting a filed historical occurrence is itself a mismatch | :17-18 |
| souji | `tools/souji-capability-agreement.py` | "Append-only: if SCORECARD.md (resp. SHONEN.md) at REV does not begin with its --base bytes, every K1 (resp. K2) item is a mismatch (fail closed)" | :28-30 |
| kake | `.ufo/waves/round-52/c52_wave_ledger.py` (exists) | wave-evidence ledger gate: "C8 reads the mirror BYTES (`show(root, rev, MIRROR)`) and requires append-only equality with the measured registry minus the adopted rows" | `SKILL.md:1215-1216`, `:1218-1219` |
| kotoba | `verifiers/check_r63_routed_repairs.py` | C2 counter includes a "LOG append-only with growth" check | `SKILL.md:475` |
| kotodama | `tools/check-supersession-settlement.py` | append-only correction-chain settlement classifier (defective row keeps cells; new row `supersedes S###` carries fix); five chain states | :3-6; also `corpus/knowledge/verification/provenance-audit-ledger-format.md:140-143` (§8 append-only rules, active-view reconstruction) |
| chousa | `tools/research-gate.sh` | `--json` state line appended to manifest with O_APPEND, never truncated; NUL-last-byte refusal; prior bytes stay byte-identical | :3950-3966 |
| lore | `.ufo/waves/round-96/seats/V53-byte-prefix-2.md` | byte-prefix append-only verification of `sources.json`/`timeline.json` (r95 → r96, exactly one appended row each, shared prefix parsed-equal) via `V53-scratch/verify_v53.py` | :67-81 |
| kasegi | `ledger/{missions,telemetry,candidates,imports}.jsonl` (external) | append-only JSONL state machine (`ops/shared.mjs::appendLedger`, O_APPEND 3500B cap) | `SKILL.md:224-231`, `:998-1002` |

Additional *word-level* `append_only_audit` metrics recorded by sibling waves (evidence of the same discipline, not standalone tools):

- `kengaku-shokunin/.ufo/waves/round-37/falsify-results.json:130` — critic verdict `no-harm-removed-lines-0` with `"append_only_audit": { "files": 71, "insertions": 8323, "deletions": 0, "status": "63 A, 8 M, 0 D, 0 R", "deletion_lines_in_diff": 0 }`.
- `tabi-shokunin/.ufo/waves/round-30/w2-results.json:88` — `"append_only_audit": "115→118 rows; appended exactly S116,S117,S118; 23 modified rows changed only used-by; 0 violations; lesson logs 23 old→new rows"`.

## 4. Non-overlaps

- No sibling has a llama.cpp *release-recheck* ledger (`release-recheck` grep: zero hits) — kama's `tools/round46-release-recheck-audit.py` / `registry/release-recheck-b11889.tsv` family is unique at the fleet root.
- No sibling references b11906/b11889 in any corpus/SKILL/tools/registry surface.
- No sibling has a `registry/` directory.
- The `ng-server-context` HTML-attribute hits (tabi, kotodama) are unrelated to llama.cpp.

## Note for the lane

This is a report-only scan; nothing was absorbed or modified. Sibling append-only audits differ in mechanism (byte-prefix blob comparison vs row-set diff vs git-history walk vs wave-ledger roll-call) but converge on the same rule — only `status`/`recheck`/`used-by` may change in place. mori's `mori-sources-appendonly.py` and souji's `souji-registry-agreement.py` are the closest functional relatives of kama's C1/C2 counters and could be cited as precedence in the round report.
