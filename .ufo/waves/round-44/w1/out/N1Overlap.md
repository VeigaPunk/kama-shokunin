# N1Overlap — sibling-overlap scan for round 44 (kama: local model serving + endpoint health)

**Verdict (one line):** No sibling lane pins llama.cpp at b11755/704366d76 or cites `server-schema.cpp`/`server-context.cpp` as its own source; all sibling references to kama's llama.cpp ground are cross-lane bookkeeping (census, overlap warnings, captured copies) or shared **runtime endpoint** use — so C1's re-verification at b11889 is uncontested ground, but the *delta* should be handed to four lanes whose artifacts embed kama's old pin/line numbers (kumitate, kotoba, kaidoku, kagi), and kama's C2 verdict-ledger is the only machine-readable cross-round trend ledger in the fleet.

---

## 1. Scope and method

Seat task: read-only scan of sibling lanes under `/home/vgpnk/Projects/shokunin/*-shokunin` (20 lanes: audio, chousa, game-dev-2d, game-dev-3d, kagi, kaidoku, kake, kasegi, kengaku, kotoba, kotodama, kumitate, lore, mado, mori, revenger, souji, tabi, tameshi, tsukuroi) for:
- llama.cpp pin at b11755 / 704366d76 in their `corpus/SOURCES.md` and knowledge;
- citations of the same llama.cpp server files (`server-schema.cpp`, `server-context.cpp`);
- any release re-verification at a newer llama.cpp tag;
- any trend-verdict ledger against outside closures.

Only read-only git/`grep`/`find` were used. No tool installs (no pacman, no uv, no binaries — nothing recorded). No scratch files were copied (no external receipts produced; all evidence is from the local repos and is reproduced in-line below).

## 2. Evidence

### 2.1 No sibling SOURCES.md row is a llama.cpp source pin

`grep -in "llama" /home/vgpnk/Projects/shokunin/<lane>/corpus/SOURCES.md` across all 20 lanes:
- Only **kotodama** S020 (`corpus/SOURCES.md:49`) mentions Llama — a *paper* row ("fine-tuned Llama3 reaches 0.85 F1", arXiv 2603.19283), unrelated to llama.cpp server source.
- No row in any sibling's SOURCES.md contains `ggml-org`, `704366d76`, `b11755`, `server-schema.cpp`, or `server-context.cpp` (verified by `grep -rn` over each lane's full tree, excluding `.jj`).

### 2.2 No sibling holds a newer-tag release re-verification

- `grep -rnw "b11755" <sibling-tree>` → only three hits, all kama-referential, none a sibling's own claim:
  - `kumitate-shokunin/.ufo/waves/round-57/build/ScoutLocalPriorArt/sibling-scoped-lines.txt:19` — quotes kama's `corpus/knowledge/llamacpp-loading-lifecycle.md:1` (S036–S040 @ 704366d76 = b11755);
  - `kumitate-shokunin/.ufo/waves/round-51/w1/ConnSiblingOverlap.md:77` — notes "kama r31 ... C1 chat-completions parameter table on llama-server b11755";
  - `tsukuroi-shokunin/.ufo/waves/round-19/l1-capture/siblings/kama/e75cf680b534/PROVINCE.md:56-57,79` — a **captured copy of kama's own PROVINCE.md** in tsukuroi's l1-capture evidence tree (kama's tooling directive at `~/.local/opt/llama-b11755`), not tsukuroi's claim.
- `grep -rn "ggml-org|b11755|b118"` over sibling trees: matches are only sha256/hex substrings (e.g. audio `MANIFEST.sha256` containing `...cbb11889d99...`; kake `build-3.json` containing `...a704366aedc...`), **not** release tags. No `b11851`/`b11889` tag reference exists anywhere in sibling trees.
- Fleet-wide: `find /home/vgpnk/Projects/shokunin -maxdepth 4 -name "*release-recheck*" -o -name "*verdict-ledger*"` (excluding kama-shokunin) → **no files**. `find .ufo/reports -name "*.tsv"` → none. kama's `registry/release-recheck-b11889.tsv` and `registry/verdict-ledger.tsv` are unique in the fleet.

### 2.3 No sibling has a trend-verdict ledger against closures

- No `<lane>/registry/` directory or `*ledger*.tsv` outside kama (only `lore-shokunin/corpus/fixtures/*ledger*` dirs, which are malformed-ledger *fixtures*, not ledgers).
- Closest analogs (method, not ledger):
  - **chousa** writes per-round `scorecard-verdict-draft.md` files (`.ufo/plans/round-{2..10}/goal-wave/scorecard-verdict-draft.md`, e.g. `round-10/goal-wave/scorecard-verdict-draft.md:11-14`) using the same verdict vocabulary (improved / unchanged / harmed / unprovable-but-better) — but these are single-round drafts, never compiled into a cross-round TSV, and they are the lane's own judgments, not third against outside closures.
  - **audio** and **chousa** carry the fleet `round-N-verifier-spotcheck.md` convention (audio `corpus/lessons/round-101-verifier-spotcheck.md`; chousa `.jj/repo/op_store/operations/` shows commits naming `corpus/lessons/round-{28,30,31,32,33,34,36,39,40,42,43,44,46,48}-verifier-spotcheck.md`) — same filenaming as kama's C2 outside closure, confirming the convention is shared, while only kama turns it into a ledger.

### 2.4 Shared endpoint ground (runtime, not source pin)

Three lanes touch the same local llama.cpp runtime that kama's C1 rows describe, but none pins the llama.cpp source commit:

| Lane | File:line | What it holds |
|---|---|---|
| kagi | `corpus/knowledge/credential-isolation.md:33-35` | `qwen-local/Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` at `http://127.0.0.1:8080/v1` "(existing llama.cpp endpoint)" — model-pin, not llama.cpp commit-pin |
| kagi | `corpus/knowledge/op-cli-surface.md:91` | "llama.cpp `/health` → `{"status":"ok"}`; a foreign listener 404s or closes." — same `/health` semantics kama C1 verifies |
| kengaku | fleet `.ufo/reports/round-9/kengaku.md:102-108`, `round-10/kengaku.md:60,65-66`, `round-11/kengaku.md:60` | ran a **serving stack** (`UD-IQ2_XXS` + llama.cpp) at `:8080`; cites llama.cpp issue #7052 (non-determinism across slots) as prior-art context — runtime use, no source pin |
| aggregator | fleet `.ufo/waves/aggregator-r11/seats/l0-forensics.md:40-42,203-207` | L13/L15 record kama's own r1 endpoint-drift repoint and `omp` builtin `llama-cpp-local` default `http://127.0.0.1:8080` (`LLAMA_CPP_BASE_URL`); L0-level witness of the same endpoint |

### 2.5 Sibling artifacts that embed kama's pin/line numbers (stale-on-update surface)

| Lane | File:line | Embedded kama detail that b11889 re-verification can invalidate |
|---|---|---|
| kumitate | `.ufo/waves/round-57/build/ConnectorSiblingOverlap/commands.txt:51-53` and `entry-with-paragraph.scratch.md:40`; `round-57/w1/ConnectorSiblingOverlap.md:29` | "kama's S117–S120 are llama.cpp `server-context.cpp` errors at 704366d" (lines 5453, 6132, 6137, 6151) — warned against bare-id cross-lane citation |
| kumitate | `.ufo/waves/round-57/build/ScoutLocalPriorArt/sibling-scoped-lines.txt:19` | quotes kama `llamacpp-loading-lifecycle.md:1` (S036–S040 @ 704366d76 = b11755) |
| kotoba | `.ufo/waves/round-71/receipts/census-after.txt:89-91,113-129` | W04 duplicate-URL census rows embed full URLs `github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/{tools/server/server.cpp,common/arg.cpp,tools/server/server-context.cpp,tools/server/server-common.cpp,tools/server/README.md}` |
| kaidoku | `.ufo/waves/round-30/w2/ConnFleetOverlap2.md:121-125` | fleet overlap map cites "kama `README.md:2292,2387` and `server-common.cpp:96` (llama.cpp)" as the OpenAI-compatible error-`type` ground (paired with kengaku `probe-r19-shim-ds-run.log:125`, kotoba omp strings dump) |
| tabi | `.ufo/waves/round-16/w1/ConnSiblings.md:39` | references kama's vendored evidence copy `llama.cpp-704366d/README.md:392` (modelcontextprotocol.io substring collision note) |

## 3. Contested / shared ground

- **Uncontested:** C1's 91 registry rows (llama.cpp server files @ 704366d76) are exclusively kama-owned. No sibling claims them, pins them, or re-verifies a newer tag. The b11889 re-verification cannot collide with any sibling claim.
- **Shared, not contested (runtime):** the local llama.cpp endpoint (`127.0.0.1:8080`, `/health` → `{"status":"ok"}`) is co-documented by kagi (lines cited above), witnessed by kengaku's serving-stack runs and the aggregator's L0 questions. kama's C1 rows and kagi's `op-cli-surface.md:91` assert the *same observable*; neither contradicts the other, but if kama re-verification at b11889 flags any change to `/health` semantics, kagi's line 91 shares the fault domain.
- **Cross-lane bookkeeping referencing kama's pin (not contested, but stale-prone):** kumitate r57 warning, kotoba r71 census, kaidoku r30 overlap map, tabi r16 note, tsukuroi r19 captured copy — all embed `704366d76` or line numbers that the b11889 re-verification may move.

## 4. Recommended handoffs / reuse for kama (report only; not absorbed)

1. **kumitate** — its r57 warning ("do not cite these rows by bare id across lanes") is already accurate; kama's b11889 verdicts (esp. which of S117–S120 drift) should be appended to kama's knowledge so kumitate's next overlap scan can resolve stale line numbers. Reuse: kumitate's `ScoutLocalPriorArt` quoting pattern is a template for kama's own overlap hygiene.
2. **kotoba** — W04 census rows 89-91/113-129 embed the full 704366d76 URLs; if kama adopts a newer pin in a future round, hand kama's new URL set to kotoba so the census can be refreshed (otherwise its duplicate-URL census silently ages).
3. **kaidoku** — the r30 fleet overlap map (lines 121-125) cites kama `README.md:2292,2387` and `server-common.cpp:96`; at b11889 those line numbers may shift. Hand off the new line numbers for `server-common.cpp` and any README anchor changes.
4. **kagi** — shares the `/health` observable (op-cli-surface.md:91); if C1's b11889 re-verification changes the `/health` contract or the server-common status strings, flag it so kagi can re-check its drift-ping command.
5. **Reuse for C2:** chousa's verdict draft vocabulary and audio's outside-spotcheck lesson are established fleet conventions; kama's verdict-ledger.tsv is the only compiled cross-round ledger — nothing to borrow, but kama's ledger shape (side/verdict/rev/path/line) could be offered as a fleet standard if other lanes adopt the same calibration debt.

## 5. Defects

None found in tooling or repos (read-only scan; no counters run — this seat does not execute C1/C2 verification; no report-issue needed).

## 6. Tooling installs

None (no package manager, no binaries, no scripts installed; nothing to record under the operator's 2026-10-19 directive).

## 7. Evidence commands (all exit 0 unless noted)

```
grep -in "llama" /home/vgpnk/Projects/shokunin/{audio,...,tsukuroi}-shokunin/corpus/SOURCES.md   # only kotodama S020 paper row
grep -rn "ggml-org|704366d76|b11755|server-schema.cpp|server-context.cpp" <20 sibling trees>      # no sibling-owned claim
grep -rnw "b11755" <20 sibling trees>                                                             # 3 hits, all kama-referential
grep -rn "ggml-org|b11755|b118" <20 sibling trees>                                                # only sha256 substrings
find /home/vgpnk/Projects/shokunin -maxdepth 4 \( -name "*release-recheck*" -o -name "*verdict-ledger*" \) | grep -v kama-shokunin   # empty
find /home/vgpnk/Projects/shokunin/.ufo/reports -name "*.tsv"                                     # empty
sed -n '25,45p' kagi-shokunin/corpus/knowledge/credential-isolation.md                           # lines 33-35
grep -n "llama.cpp" kagi-shokunin/corpus/knowledge/op-cli-surface.md                             # line 91
sed -n '115,130p' kaidoku-shokunin/.ufo/waves/round-30/w2/ConnFleetOverlap2.md                   # lines 121-125
grep -n -B2 -A4 "llama.cpp" .ufo/reports/round-{9,10,11}/kengaku.md                              # serving-stack/issue #7052
grep -n -B2 -A4 "llama.cpp" .ufo/waves/aggregator-r11/seats/l0-forensics.md                      # lines 40-42, 203-207
```
