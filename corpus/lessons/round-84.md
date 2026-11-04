# kama round 84 — terminal receipts correct the record and the missing pin gains documentary ground

Frozen plan `plans/round-84-claims.md`; base `aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0`, freeze `2d49bf705a2f2f8b45da973407cbb0b2ce2f8fd2`, controls `eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85`. Sealed revision C2 grades `ae4323171596126a9265f7f6c8af4164d499ba09`. No axis score increase is claimed.

- **C1 operability:** bind a late note's deletion round to the event subject; disclose ungraded-population stale rows and compose arm 13. This draft does not attest the unrun integrated predicate.
- **C2 calibration:** answer six stale facts of the frozen eight-fact population with value-bound corrections; F6/F7 remain holding direction tests.
- **C3 freshness:** open the missing b7200 document and reopen the three newest-side documents at their specified refs. Integrated register grading is distinct from these source reads.

## Gate

Four sources personally opened by SCR01 with `curl -sS` on 2026-11-04. Status, body byte count and full SHA-256 below describe the received documents, not endpoint probes. Each located quote is verbatim and no longer than 25 words.

| id | URL | status | bytes | line | ≤25-word located quote | verdict | reason / flip |
|---|---|---|---|---|---|---|---|
| S572 | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b7200/tools/server/README.md` | 200 | 72181 | 406 | "This endpoint is public (no API key check). `/v1/health` also works." | admit | b7200 health header at 404; sha256 `fb4ab6f2e4db180bf9c89533ef63556559c60a66f9c39a92f0c23cd88f6c6a53`, 1530 lines; the document missing from relation 3 is retrievable at tools/server |
| S573 | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12111/tools/server/README.md` | 200 | 136429 | 482 | "This endpoint is public (no API key check). `/v1/health` also works." | admit | b12111 header at 480; sha256 `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137`, 2620 lines; matches the round-83 recorded digest |
| S574 | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx` | 200 | 18295 | 111 | "`/ready`: Returns 200 when the server accepts new requests; 503 while starting, paused, unhealthy, or shutting down." | admit | v0.5.23 Health Check at 108; `/ping` at 112; sha256 `3ed171186990d6a67a1d950f1d491fe83986cf539bf24d1e65b95481e7d87a3c`, 471 lines; matches S567's recorded digest |
| S575 | `https://raw.githubusercontent.com/vllm-project/vllm/v0.33.0/docs/design/prefix_caching.md` | 200 | 13916 | 3 | "Prefix caching kv-cache blocks is a popular optimization in LLM inference to avoid redundant prompt computations." | admit | v0.33.0; sha256 `67ee4e2b7bc23d40e9b366e4a9053ae4ecd0925ddef51f412ac5c16b9dc83a61`, 236 lines; matches S569's recorded digest |

The alternative b7200 `examples/server/README.md` path returned HTTP 404 with a 14-byte body (curl exit 0 without `--fail`); it is not an admitted source. All three newest-side fixed-ref reopens retain their recorded round-83 digests. This is not a fresh tag-list census, nor an assertion that a counter over yet-uncommitted extracts passed.

## Corrections

Six corrections for eight facts: F6 and F7 hold and have no correction line. F2 packs its two old and two new tokens into one comma-separated correction line; the exact whole new composite must occur in SCORECARD ordinary bytes outside excluded correction regions.

```
corrected F1 old=r83c1-late=23 new=r83c1-late=22 at=aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0 date=2026-11-04 fix=SCORECARD.md
corrected F2 old=r83c1-window=8,r83c1-falls=yes new=r83c1-window=7,r83c1-falls=no at=aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0 date=2026-11-04 fix=SCORECARD.md
corrected F3 old=r83c1-delta=123/103/20/0 new=r83c1-delta=113/103/10/10 at=aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0 date=2026-11-04 fix=SCORECARD.md
corrected F4 old=r82c2-new=0 new=r82c2-new=15 at=aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0 date=2026-11-04 fix=SCORECARD.md
corrected F5 old=r83c3-selftest=11 new=r83c3-selftest=14 at=aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0 date=2026-11-04 fix=SCORECARD.md
corrected F8 old=r83-closure=round-82-verifier-spotcheck.md new=r83-closure=round-83-verifier-spotcheck.md at=aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0 date=2026-11-04 fix=SCORECARD.md
```

- **F1:** `.ufo/waves/round-83/measured/final/c1-legA.out`, measured at `1d90dc816e200481c7a136934a35e8c418ec4501`, prints `late=22`, `bad_rows=10`, `EXIT=1`, not the head's interim successful 23.
- **F2:** the same revision's `c1-pending.out` prints `window=7 accepted=7 unaccepted=0 falls=no`, `EXIT=1`, not the interim eight-event success.
- **F3:** `c1-delta.out` prints `population=113 carried=103 new=10 bad=10`, `EXIT=1`. The token includes all four cells, including the adverse `bad` count.
- **F4:** the frozen witness `.ufo/waves/round-82/measured/before/c2-late-delta-base.out` supplies `new=15`, answering the carried round-82 C2 stale cell; this draft does not silently edit that dated section.
- **F5:** `c3-selftest.out` prints `PIN_RECHECK_SELFTEST pass=14 fail=0`, `EXIT=0`, not 11.
- **F6/F7:** the frozen table records the selfrecord and pin-recheck summaries as holding; neither is corrected. Their holds are not a whole-record audit.
- **F8:** the frozen base's newest outside closure is `corpus/lessons/round-83-verifier-spotcheck.md`, resolved by `python3 tools/round69-newest-closure-counter.py --repo . --rev aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0 --since-round 63`; the live calibration cell must cite it. This draft does not claim that command was rerun by SCR01.

The fix leg is the ordinary live SCORECARD token, not merely this correction block or a `LOG-CORRECTION` line. L1 owns integration and terminal counter receipts; this draft records the correction contract without claiming those changes already landed.

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| `number-drift`/`survivor` — round-83 live authority and axis cells kept interim successful receipts after final audit receipts superseded them | `SCORECARD.md` head authority paragraph and operability/freshness/calibration axis rows at `aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0` versus `.ufo/waves/round-83/measured/final/*.out`, especially `c1-legA.out`, `c1-pending.out`, `c1-delta.out`, `c3-selftest.out`, measured at `1d90dc816e200481c7a136934a35e8c418ec4501` | KQ27 — counts were already required to follow their measured revision, but the live cells survived supersession | C2's six value-bound corrections plus re-derived head cells; new KQ136 requires terminal receipt revision and re-derivation command for current-evidence cells and explicitly names the superseded criterion. The exact append draft is delivered separately as `quality-row.md`. |

## Frontier

S572 makes the b7200 health sentence available at its actual tools/server path; S573-S575 reopen the three specified newest-side documents without claiming a new newest-tag census. The SGLang v0.5.23 `/ready` and `/ping` distinction gains documentary ground in the appended matrix section (S574), not a local runtime observation. R83V4 appends the last-modification reading without removing the cosmetic-edit limitation; R83V5 adds actual coverage-table rows for the two round-83 knowledge entries. Other engines' documents, live serving conformance, registered-consumer restoration and K05 declared-versus-served context capacity remain frontier. No score promotion follows from these index or source changes alone.

## Integration dispositions and freeze divergences

- Audit classifies 0d7c7c3e/SCORECARD as **ungraded**, not restored. Ten rows are retained byte-exact in `registry/append-only-late-r83-restored.tsv` (frozen filename retained). Their removal from the live register is disclosed here. `append-only-disclosures.tsv` is an event-loss ledger, not a rotation log: no fabricated disclosure is appended. See EX02Registers report and base-audit.json. This misses the frozen auxiliary disclosure instruction; no audit rule is changed.
- Original gate control arms12/failed5/uncommitted5 includes transient dirt; independent committed-byte replay is arms12/failed3/uncommitted0. Both miss the target; only persistent failures are intrinsic.
- C1/C3 abbreviated output strings name field predicates, not contiguous substrings: the renderer interposes verdict fields in C3 and prints unaccepted before bad_rows in C1. No numerical target changes.
- F4 sealed locator is line4976, not4971; values new=0/new=15 re-derive. F2 comma-joins its coupled tokens; F3 serializes the bad count. Eight facts and six corrections unchanged.
- Critic fabricated hash-consistent excerpts that pass C3's numeric counter. Source acquisition must be corroborated separately by retained fetched bodies and L1 source opens, not hash integrity alone. All five actual quotes hold; no moved/drifted verdict is invented.
- Mutation study tests a spec implementation, not the delivered file: M1 deletion killed; M2/M3/M4 survived; M5 killed by unresolved-subject arm. Survivors are disclosed, never credited as killed.
- Validator rejected labrat before dispatch; CR02Probes uses critic. Actual 12-seat mix is 5 executor, scribe, scout, connector, reviewer, 2 critic, mutation-tester; attack share4/12. Frozen shape prose said4 executors and labrat. L1 planner mapping is not a dispatched planner.
- All four new source rows are mined/A, not rejected. Genuine rejected candidate: b7200 examples/server path returned404; it is refused as documentary support (flip: a retrievable revision-specific document). No invented content quote; not added as a source row. Independent closure can sample this reject alongside S572 admit.

Stale-lane: this steered lane-round is progressing; no second kama mission is owned by this L1. No tool installs; pacman untouched.

Assimilation: none — SCO01Upstream inspected package/proposal fit, but no staged entry or unimplemented proposal is adopted. C3 is independent source curation.

Outside admit/reject spot-check remains the independent closure's duty; dispatched seats are author-side advisors.
