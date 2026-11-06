# RV02SourcesGate — kama r88 w1: S581/S582 re-open, Gate check, knowledge audit, census

## Scope
Non-author check of the round-88 frontier sources step: re-open S581/S582, verify sha256/quote/line/column
facts in `corpus/SOURCES.md` S581/S582 and the `## Gate` table of `corpus/lessons/round-88.md`; sentence
audit of `corpus/knowledge/router-mode-readiness.md` against S581 + cited receipts; census validate.
Read-only in the lane; artifacts in `.ufo/waves/round-88/w1/out/RV02SourcesGate/`.

## Commands and outputs (true exit codes)
- `curl -fsSL .../704366d.../tools/server/README.md -o S581.md` → exit 0; sha256
  `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37` (2402 lines)
- `curl -fsSL .../954de24.../tools/server/README.md -o S582.md` → exit 0; sha256
  `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` (2620 lines)
- GitHub compare API `704366d...954de24` → `status=ahead ahead_by=423 behind_by=0` (954de24 strictly newer)
- Quote location: `grep -c 'can be launched in a \*\*router mode\*\*' S581.md` → 1, at line 1849;
  `grep -c 'The \`status\` object can be' S582.md` → 1, at line 2265
- Anchors in S581: `## Using multiple models` L1847; autoload sentence L1993; status list intro L2059,
  incomplete block closes L2120; `### POST /models/load` L2137 (payload `model`); `### POST /models/unload`
  L2159 (payload `model`); failed block `value:"unloaded"`+`failed:true`+`exit_code` inside 2059-2121;
  `## Sleeping on Idle` L2333-2345 (L2337 wake-on-task; L2342 /health reload-exempt)
- Columns: `awk -F'|' 'NR==336||NR==337{print NF-2}' corpus/SOURCES.md` → 11, 11 (header L11 = 11 columns)
- Hash corroboration: `git show B:tools/kama-probe.sh | sha256sum` = `0943fb46…3d19` (= controls/c1-base.out
  probe_sha256); `git show M:tools/kama-probe.sh | sha256sum` = `bd7a6a22…7bdf` (= measured/c1.out);
  counter sha F=M=worktree = `576a1b37…5e21` (freeze-identical independently confirmed); knowledge blob at
  T `f77d2ae9` == worktree copy
- Census: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0; 118
  lines: 116×W04 (duplicate-url warnings, all pre-existing patterns), non-W04 = `W01 S481 tierC mined
  used-by=…` (also present at round start in controls/census-start.out:94 — pre-existing, not new) and
  final `kama ok …/corpus/SOURCES.md`
- Receipt parity: controls/harm-base-probe-verdicts.out tail `tests=72 passes=72 failures=0` and
  harm-base-test-snapshot.out `RESULT pass=30 fail=0` == measured/harm.out at M (plus censuses 4/4, 4/4)

## Gate table verdicts (agree/disagree record)
- S581 **admit — AGREE.** sha256 match; quote 18 words (≤25), occurs once, at L1849 in the cited section
  (L1847); row 11 columns; teaches (status vocabulary ⇒ listed ≠ loaded) grounded by L1997, L2042-2044,
  L2059-2121; status `mined`, recheck on-release consistent with the pinned-binary rationale.
- S582 **reject — AGREE.** sha256 match; quote 5 words at L2265, once; "newer than the pinned b11755
  binary" verified (ahead_by=423, behind_by=0); "same status list as S581" verified (values at L2269-2323);
  flip (pinned build moves past b11755) is the exact condition under which this reject lapses — sound.
  Remark: the quoted sentence also occurs in S581:2059; the row's location is still correct for S582.
- Knowledge-entry **admit — PARTIAL DISAGREE with its reason cell** ("every row of its observation table
  is a committed receipt" — false as stated; Findings 1-3).
- R87 selector reject: outside source scope; no disagree recorded.

## Knowledge audit — corpus/knowledge/router-mode-readiness.md sentence by sentence
- source line ranges 1847-1993 / 2059-2121 / 2137 / 2159 — AGREE (all verified in fetched S581).
- verified-at sha256 `714c067b…` — AGREE (my fetch byte-identical); GET-only on 1234 — AGREE-as-recorded
  (controls/pilot-live-1234.out:1 header attests "GET only").
- Claim: router when launched without a model (cache/`--models-dir`/`--models-preset`) — AGREE
  (S581:1851, 1860-1862).
- Claim: GET /v1/models lists models, each entry with `status` — AGREE (S581:1997, 2004-2007; wording in
  source is "Listing all models in cache", the knowledge paraphrase is fair).
- Claim: "GET /health answers 200 {\"status\":\"ok\"} while no model is resident" — **DISAGREE
  (ungrounded)**: S581:486-489 defines 200 as "the model is successfully loaded and the server is ready";
  S581:2342 only exempts /health from reload; neither cited receipt (c1-base.out, measured c1.out) records
  any /health response; the only wave artifact showing /health 200-ok is a **stub** (w1/out/
  EX02HarnessCorroboration/RouterStatus.json, `"port_mode": "stub"`). Plausible router behavior, but no
  live receipt exists. See Finding 3.
- Claim: listed id ≠ readiness — AGREE (S581:2042-2044); probe-before graded listed ids MODEL_OK — AGREE
  (c1-base.out C02-C07, C10, C12, C14, L01, L03 all `observed=MODEL_OK`).
- Source bullets: quote@1849; autoload default + `--no-models-autoload` + `?autoload=` override@1993;
  six status values + failed load `value:"unloaded"`/`failed:true`/`exit_code` in 2059-2121; load/unload
  `{"model": "<id>"}`@2137/2159 — ALL AGREE (verbatim verified).
- Observation rows 1-3 (fresh/load/unload on pinned b11755 child) — AGREE with a citation-precision nuance:
  probe columns grounded by c1-base.out L01/L03 + measured/c1.out L01-L03; the literal `400 model is not
  loaded` is **never printed in any committed receipt** — it is implied by the frozen oracle mapping
  (tools/round88-router-cells.py:13 `400 "model is not loaded" → MODEL_UNLOADED`) plus exit=0 (no
  could-not-evaluate). See Finding 4.
- Observation row 4 (operator 1234): `unloaded` ×4, `not sent`, `MODEL_OK` before — AGREE
  (pilot-live-1234.out). "autoload on, `--sleep-idle-seconds 600`" — **DISAGREE (ungrounded anywhere)**:
  `git grep` at T finds `--sleep-idle-seconds 600` only in this knowledge file; no receipt or tracked file
  shows the operator router's flags. "MODEL_UNLOADED router-unloaded" after-cell — **DISAGREE (no
  receipt)**: no post-fix probe run against 1234 is recorded (would be GET-only-legal but absent). See
  Finding 1.
- "With autoload on … first request pays the full load" — AGREE (S581:1993, 2337).
- Decision-rule table — AGREE: matches the frozen rule in plans/round-88-claims.md and the implementation
  at M (`git show M:tools/kama-probe.sh` L464-512: statusless→unchanged, loaded win, loading/downloading
  → MODEL_LOADING, else MODEL_UNLOADED `-failed`; measured cells C01-C14, L01-L03 all ok=1).
- Limits: sleeping-not-ready by choice — AGREE (list 2059-2121; wake at L2337); probe sends no completion,
  oracle POST only on lane child — AGREE (counter L153 GET vs L173/L205 POST; harm receipts
  `requests=[GET /v1/models, GET /health]`); without python3 old verdict stays — AGREE (probe at M
  L37/50/94/468: router extraction is `python3 … || true`, no-op without python3).

## Findings
1. **DEFECT** — corpus/knowledge/router-mode-readiness.md:30 (observation row 4): the operator-router
   cells "autoload on, `--sleep-idle-seconds 600`" and "Probe after r88 = MODEL_UNLOADED router-unloaded"
   are presented as observed but are backed by no receipt in the repo (pilot-live-1234.out covers only the
   before-side; no tracked file anywhere names the 1234 server's flags). Fix: drop the two unbacked cells
   or append a GET-only receipt (e.g. /props + a post-fix probe run against 1234).
2. **DEFECT (lesson Gate text)** — corpus/lessons/round-88.md Gate row 3 reason "every row of its
   observation table is a committed receipt" is false as stated: row 4's flags/after-cell (Finding 1) and
   the 400 body (Finding 4) are not printed in any committed receipt.
3. **NOTE** — router-mode-readiness.md Claim § ("GET /health answers 200 … while no model is resident"):
   contradicts the letter of S581:486-489 (200 = loaded-and-ready) and has no live receipt; the sole
   supporting artifact is a stub. Either receipt it live on the lane child or hedge the sentence.
4. **NOTE** — citation-precision: the `400 {"…model is not loaded"}` oracle response quoted in
   round-88-claims.md, lessons/round-88.md:13 and the knowledge table is derivable (frozen oracle mapping +
   `ROUTER_CELLS … exit=0`) but never recorded verbatim. Cheap hardening: counter prints the oracle HTTP
   code per live cell.
5. **NOTE** — no census regressions: validate exit 0; the single non-W04 warning (W01 S481) predates this
   round (census-start.out:94); S581/S582 rows introduce no new warnings.

No BLOCKER. C1/C2 receipts, hashes and the S581/S582 Gate rows are sound; the defects are grounding
over-claims in corpus prose, not in the frozen predicate or the instruments.

## Deliverables
- .ufo/waves/round-88/w1/out/RV02SourcesGate/S581.md (fetched, sha256 714c067b…)
- .ufo/waves/round-88/w1/out/RV02SourcesGate/S582.md (fetched, sha256 eafc1b53…)
- .ufo/waves/round-88/w1/out/RV02SourcesGate/compare.json (GitHub compare 704366d…954de24)
- .ufo/waves/round-88/w1/out/RV02SourcesGate/census-rv02.out (full census validate output)

VERDICT: partial — S581/S582 admits/rejects and the knowledge core (status vocabulary, decision rule, receipt-backed probe behavior) hold; two grounding over-claims (operator-router flags and after-cell; /health-ok-while-unloaded) and the never-printed oracle 400 need prose or receipt fixes.
