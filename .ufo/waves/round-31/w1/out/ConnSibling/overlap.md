# ConnSibling — sibling-overlap scan, kama round-31 wave 1

Seat: ConnSibling (connector). Scope: the 9 sibling lanes named in the item
(kake, kumitate, mori, chousa, kaidoku, tameshi, kotoba, tsukuroi, kotodama),
read-only. Round-31 surfaces in question: kama C1 = the `/v1/chat/completions`
parameter layer of pinned llama-server b11755 (SKILL.md section
`## Round-31 chat-completions parameter outcomes`, `registry/chat-param-outcomes-r31.json`,
new S### rows over server-common.cpp@704366d); kama C2 = SCORECARD.md claim-table
rows + appended correction section.

## Method (all commands read-only)

- `git -C /home/vgpnk/Projects/shokunin/<lane>-shokunin log --oneline -20` for the 9 lanes — all exit 0.
- `grep chat/completions|response_format|logprobs` over each lane's `corpus/` — 2 hits (below).
- Same pattern over each lane's `.ufo/waves/round-4*/` — **0 hits**.
- Supplementary scans: `llama-server|server-common|stories260K|b11755` and
  `claim-row|chat-param-outcomes|chat/completions parameter` over all 9 lanes — every match is a
  *citation of kama's surfaces* from a sibling adjacency/connector doc, not a sibling holding (below).
- `grep registry_count_check` over kake — owner evidence (below).

## Hits on the scanned surface terms

| # | lane | commit | artifact | what it holds | contested scope? |
|---|------|--------|----------|---------------|------------------|
| 1 | kumitate | 3d5760a (r36) | `corpus/knowledge/ops-watchers.md:401-405` | knowledge entry for a watcher ("THE TICK") whose client code POSTs to `http://127.0.0.1:34113/v1/chat/completions` | **No.** Client-side consumer config of the endpoint family, not the server adapter parameter layer. kama must not absorb it; it is adjacent domain knowledge (endpoint health), already kumitate's. If kama r31 prose wants a consumer cross-reference, cite — do not import. |
| 2 | mori | 837b280 (r32) | `corpus/evidence/recheck-r32/S043.src:451` | fetched HTML snapshot of a third-party (z.ai) API reference page; its nav JSON mentions `POST /paas/v4/chat/completions` | **No.** Web-snapshot evidence for mori's recheck surface; unrelated to llama-server b11755. Not contested; nothing to absorb. |

Zero hits for `response_format` and `logprobs` anywhere in the 9 lanes' corpus or round-4x waves.

## Sibling citations of kama's llama surfaces (adjacency, not holdings)

These name kama's fixture/province to bound their own scope — kama keeps ownership; no contest, no absorption:

- mori `8d22d18` (r14) `.ufo/waves/round-14/build/SiblingBoundary.md:66-73,162-163` — routes local model-server unit failures to kama (ADJ-01 handoff), names `llama-server` on 8080/34113.
- kaidoku `b3669e60` (mint) `EXAMPLE.kama.md:16-34,62-66` — describes kama's province incl. llama-server, ports 8080/34113.
- kaidoku `39fbad9d` (r30) `.ufo/waves/round-30/w2/ConnFleetOverlap2.md:121-125` — cites kama `README.md:2292,2387` + `server-common.cpp:96` re OpenAI `invalid_request_error` type (a kama-originated row kama r31 may build on; the source line is kama's, not kaidoku's).
- tsukuroi `68a8ae0` (r18) `.ufo/waves/round-18/build/ConnSibling.md:13` — cites kama `PROVINCE.md:55-69` llama-server lines.
- kotoba `147ac42` (r61) `.ufo/waves/round-61/wave/RevC3Bleed.md:16-17` — quotes kama PROVINCE domain line and names kama's `corpus/knowledge/self-assessment-at-writing.md` as borrowed source material (kake r43 S130 imports the same kama entry — kama is cited, holds nothing from siblings).
- tameshi `e69b488` (r16) `.ufo/waves/round-16/w1/Overlap2.md:179-181` — notes kama launches an ephemeral llama-server on a non-registered loopback port.

## Repair ownership: `registry_count_check` is kake's — kama does not absorb it

Owner evidence (all in kake-shokunin):

- Instrument: `.ufo/waves/round-43/registry_count_check.py` (sha256
  `35ca6d40f91215ab59b79ee9ccbf6e920bfc4067c3caf87173a86a6a87c535db` per `.ufo/waves/round-43/w1/CriticFreezeOrder.md:50`),
  able-to-fail checker re-deriving `corpus/SOURCES.md` census counts (rows/mined/queued/rejected)
  from a claims JSON at two revisions; red on r42 claims (exit 1), green on r43 correction (exit 0),
  receipts `verification/freeze/registry-count-r4{2,3}-check.txt`.
- Landed records: `corpus/knowledge/claim-count-derivation.md` (r43 discipline, cites S130),
  `corpus/lessons/round-43.md:33-36`, `SCORECARD.md:3268-3271` (append-only correction entry) and
  `SCORECARD.md:3357-3360`.
- Defects are also kake's to carry: seat `.ufo/waves/round-43/w1/ReviewQualityV.md:1` (DEFECT —
  census() diverges from the CORPUS.md contract; 4/5 probe classes bypass) and kake's own SCORECARD
  r43 line 5: the checker is "overclaimed as a gate … a smoke aid, not a gate".
- kake's own connector (`.ufo/waves/round-43/w1/ConnectorOverlap.md:35-43`) scanned siblings and
  found `registry_count_check` kake-only.

Why no kama absorption: the checker's object is `corpus/SOURCES.md` census arithmetic, which is
*kake's* surface. kama round-31 touches none of it — C2's object is SCORECARD.md claim-table rows
(revision/evidence-path/counter citation), a different object, and preregistration.json
`not_absorbed` already routes this repair to kake. No sibling is repairing anything else kama's
round-31 plan touches (SKILL.md chat-param section, `registry/chat-param-outcomes-r31.json`,
SCORECARD claim-row corrections).

## Verdict

- Contested-scope holdings requiring a kama report: **0**.
- Benign surface-term hits: 2 (kumitate r36 consumer config; mori r32 web snapshot) — cite-only, never absorb.
- Adjacency citations of kama's llama surfaces: 6 docs across mori/kaidoku/tsukuroi/kotoba/tameshi — kama retains ownership.
- `registry_count_check` repair: owned and repaired by kake (r43), with recorded bypass defects; kama must neither import it as a gate nor re-derive it.
- No live servers were started; nothing to clean up. No files outside
  `.ufo/waves/round-31/w1/out/ConnSibling/` were written; no lane git state touched.
