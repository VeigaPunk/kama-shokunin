# RV02SourcesGate — round-89 w1 sources gate (kama)

## Scope
Re-opened SOURCES rows S583–S586 at the exact pinned URLs (HTTP status + sha256 vs `corpus/lessons/round-89.md`
`## Gate`); located each quoted string at its stated line and word-counted it; judged whether `teaches` follows;
checked both S586 reject reasons against spec text and gguf.cpp, with live b12177 corroboration; audited every
factual sentence of `corpus/knowledge/router-unloadable-model.md` against cited source lines or committed
receipts; re-ran the KQ143 sweep at base `56174a1fa6a27faa91d3664ef4730b48dd3149c0` in a `git clone --shared`
scratch clone; ran `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`.
Read-only in the lane; no tracked file touched; no pacman, no installs (curl/python3/git only); no requests to
127.0.0.1:1234; all server children were lane-owned (b12177 sha256 `ba272ee3…b362b0`, b11755
`b6a31a8e…cd804`), started on free loopback ports, killed by process group; scratch removed before yield.

## Commands and outputs (exit codes)
1. `curl -sS -o <f> -w %{http_code}` ×4 — all `http=200`; sha256: S583 `cab14969b9e5adf08a057c622d1abfc30fd8a17484de5b35942632d739a71108`,
   S584 `51bd966ab0494aa20d4087975f17d8b9b8ed9c4b63d7cbffe9315ed45de5dd78`, S585
   `53e6dfa95083d5e81d1da316beb9ea1d4f943cec9dd450db54d849023c01df6c`, S586 `1dead27b6a522709f0127d194e58c21dbbbf00ba1c64fe37c54d1a9048b05020`
   — all four match the lesson Gate exactly. exit 0.
2. Quotes at stated lines (`sed -n`): S583:1641 `throw std::runtime_error("model name=" + name + " failed to load");`;
   S584:512 `GGUFv1 is no longer supported…`; S585:7035 `GGML_QUANT_SIZES: dict[GGMLQuantizationType, tuple[int, int]] = {`;
   S586:285 `// Must be \`3\` for version described in this spec, which introduces big-endian support.`
   — word counts 10 / 13 / 6 / 14, all ≤25. exit 0.
3. `grep GGUF_VERSION ggml.h@6c01da62` → `42:#define GGUF_VERSION 3`; `grep "define GGML_MAX_DIMS" ggml.h` → `4`
   (ggml.h:222). exit 0.
4. KQ143 at base clone (verified `git rev-parse HEAD` = `56174a1f…`, toplevel = the clone): recorded grep
   `grep -ril -E "failed to load\|gguf.*header\|truncat" corpus/knowledge SKILL.md` → **exit 1, zero files**;
   unescaped `grep -ril -E "failed to load|gguf.*header|truncat" …` → exit 0, exactly **7 knowledge files + SKILL.md**
   (completion-request-plane, consumer-registry, context-capacity, endpoint-identity, error-is-not-a-verdict,
   gguf-declared-identity, listener-census). `grep -n failed corpus/knowledge/router-mode-readiness.md` → lines
   19,20,47,49 (the `failed: true` rows). exit 0/1 as above.
5. Census: `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → **exit 0**; non-W04 lines are
   one `W01` (S481 used-by list) and the `ok` line for SOURCES.md. 116×W04 (whitespace), nothing actionable.
6. Live checks (script `live_checks.py`, exit 0; children killpg'd):
   A b12177 router child, plain-text `badhdr.gguf` listed `unloaded` (no `failed`), completion →
   `HTTP 500 {"error":{"code":500,"message":"model name=badhdr failed to load","type":"server_error"}}`, then
   `GET /v1/models` → `"exit_code": 1, "failed": true`, value stays `unloaded`; `status.args` carries the full
   child argv incl. `--model <abs path>`.
   B b11755 router child, valid copy, GET-only: `status.args` = `[<b11755 path>, …, "--alias", "stories260K", "--model", "<abs path>…"]`.
   C b12177 `-m` on stories260K with version field patched 3→2: `/health` → 200 `{"status":"ok"}`, log `model loaded` — v2 loads.
   D b12177 `-m` on copy with tensor offset gap (`blk.4.ffn_norm.weight` 1170944→1171008): server **exit 1**, log twice
   `gguf_init_from_reader: tensor 'blk.4.ffn_norm.weight' has offset 1171008, expected 1170944` (= S584:797-801 text).
   b11755 bad-file listing (GET-only): `value=unloaded`, `failed=None`, `exit_code=None` — identical to b12177 listing.
7. `sha256sum` binaries/model: b12177 `ba272ee3…b362b0` ✓, b11755 `b6a31a8e…cd804`, stories260K `270cba1b…256d` ✓ (pins hold).
8. S582 re-check: README @ `6c01da62` sha256 `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` =
   byte-identical to @ `954de24` — lesson's "identical bytes, stays rejected" holds (and no admitted entry cites it).

## Findings
1. **DEFECT (lesson reproducibility)** — `corpus/lessons/round-89.md` `## Gate` row KQ143 records the sweep as
   `grep -ril -E "failed to load\|gguf.*header\|truncat" corpus/knowledge SKILL.md`; run verbatim at base on this
   host (GNU grep) it matches **nothing** (exit 1: `-E` treats `\|` as a literal pipe). The stated result
   "7 knowledge files + SKILL" reproduces only with unescaped `|` (exit 0). The sweep's substance is true; the
   recorded command cannot reproduce it. Evidence: command outputs in item 4 above, clone at base `56174a1f…`.
2. **NOTE (KQ143 sense classification incomplete)** — lesson says the non-cited hits "match 'truncat' in unrelated
   senses": actually `corpus/knowledge/endpoint-identity.md` matched **only** `gguf.*header` (line 80, one-line span
   "`.gguf` normalization … `Server` header", no truncat), and `corpus/knowledge/context-capacity.md` matched both
   (`gguf.*header` at line 7 "A GGUF header declares a training context", `truncat` at 128-129). Neither is
   loadability prior art the entry must cite (context-capacity:7's "header declares" framing is already represented
   by cited `gguf-declared-identity.md:7`), so no missing citation — but the Gate row's characterization is imprecise.
3. **NOTE (mechanism attribution, frozen claims C1 rule + SKILL §Round-89 row 2 + S584 teaches)** — "tensor data past
   end of file — S584 gguf.cpp": at b12177 that S584 check (data-blob read, gguf.cpp ~876-880) is **unreachable on
   the server load path**: `src/llama-model-loader.cpp` (same commit) calls `gguf_init_from_file` with
   `no_alloc = true` (lines 571, 683; also 632, 943, 1152) and `server-models.cpp` has no gguf usage, so the loader
   parses headers only; the real enforcement is at data-load time (`llama_file::read_raw` throws "unexpectedly
   reached end of file", `src/llama-mmap.cpp:278-280`). The probe's header-time past-end check stays
   oracle-conservative — any file it flags cannot load (U4 oracle: http=500 failed to load), so C1's observable
   predicate is unaffected — but S584 does not "name the failing check in the router child's log" for the past-end
   case, and the S584 teaches overstates the mirror for that one sub-check. All other S584 sub-checks (magic,
   version 0/1/byte-swapped/>3, alignment u32+power-of-two, >4 dims, ne[0] % block, exact contiguity) verified
   line-by-line and match the probe's `gguf_state` (tools/kama-probe.sh:492-612) exactly.
4. **NOTE (uncited pointer)** — knowledge §3 "The operator's router lists absolute paths" and the claims' Goal
   sentence about operator entries' files existing with GGUF magic have no committed receipt showing raw
   `status.args` paths: `controls/harm-base-operator-1234.out` records the probe verdict/summary only. I did not
   query 1234 (not named by this item). Low risk: relative-listing behavior is receipt-backed (P4) and my A/B
   captures show both builds list absolute paths when given absolute dirs.
5. **S586 reject: AGREE, both stated reasons verified (static + live)** — (a) version: spec line 285 says must be 3,
   loader rejects only 0, byte-swapped (`&0xFFFF==0`), 1, `>GGUF_VERSION(3)` (S584:492-520; gguf.h:42) — patched-v2
   stories260K loads on b12177 (item 6C). (b) contiguity: spec normatively requires only offsets that are ALIGNMENT
   multiples with advisory "should be padded" wording (S586:329-331, 347-352); loader requires exact running-sum
   equality (S584:797-803) — gap rejected with exit 1 and the exact expected-offset error (item 6D). Flip condition
   (loader enforces exactly the spec) not met. Quote located at line 285, 14 words, sha256 matches.
6. **Corroborations (previously pointer-less sentences, now receipt-backed by my w1 outputs)** — SKILL §signatures
   row 2 tail and knowledge §2 "afterwards … `unloaded` + `failed: true` + `exit_code: 1`" (item 6A, live b12177);
   knowledge §3 b11755 `status.args` (item 6B); knowledge §1 "same on b11755" listing-identically (b11755 GET-only
   capture). All eight C2 SKILL rows carry exactly the messages in `measured/router-signatures.jsonl` (9 calls,
   8 error answers, all `server_sha256=ba272ee3…`); both stated "traps" match receipts (`load` unknown id → 404
   "File Not Found" though S583:2121 says "model is not found"; `unload` unknown id → 400 per S583:2269-2273).

Knowledge sentence audit: every checked sentence is **supported** — header source lines (1641/1956/1962/2121-2125/
2269-2273, gguf.cpp ranges 471-517/622-633/677-751/781-818, constants 6802-6838/7035-7072) all verified in the
re-fetched bytes; `verified-at` pins (binary sha, 36-file sweep `files=36 ok=36`, GET-only operator receipt) hold;
§1-§4 and the Limits bullets verified as detailed above and in findings 3-6. One clause rides on uncommitted recon
(b11755 failed-completion behavior) — now partially corroborated (listing half) by my receipts; the completion half
remains recon-only, not a contradiction.

## Deliverables
- `.ufo/waves/round-89/w1/out/RV02SourcesGate/live_checks.py` — live check driver (A-D).
- `.ufo/waves/round-89/w1/out/RV02SourcesGate/live-checks.out` — A/C/D outputs incl. v2 load and contiguity rejection.
- `.ufo/waves/round-89/w1/out/RV02SourcesGate/b11755_args.py`, `b11755-args.out` — b11755 `status.args` capture.
- This report: `.ufo/waves/round-89/w1/RV02SourcesGate.md`. Scratch `/fast/scratch/hyaku/kama-r89/RV02SourcesGate/` removed.

VERDICT: holds — all four rows re-open clean (hashes/quotes/teaches verified; S586 reject confirmed live); one DEFECT in the lesson's recorded KQ143 grep (escaped `\|` matches nothing) and mechanism-precision NOTEs reported.
