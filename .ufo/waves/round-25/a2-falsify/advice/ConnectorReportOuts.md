Verdict: holds, with one wording defect. Every sibling line the wave-1 connector quoted still says what it quoted. Its kagi claim is stated too strongly, and one kagi locator is only a partial match.

# ConnectorReportOuts: round 25 attempt 2, wave 2 (falsify), adjacency

Target: `.ufo/waves/round-25/a2-build/advice/ConnectorSiblingOverlap.md`, covering the kengaku concurrency half and the kagi health rule.
This seat was read only across the sibling lanes. It started no llama-server and no other server, contacted no endpoint, wrote nothing to any sibling, and installed or upgraded no tool.

## Axes

- Adjacency, which is report-out accuracy to sibling lanes.
- Correctness of the cited sibling evidence.
- No numeric axis moves. C1 and C2 counts are untouched.

## What I checked (all commands exit 0)

Sibling HEADs: kengaku `1f3b0f1ec41ec297130e8944ff97968d32324632`, kagi `899c50b42634a3a4ad0b28ab7509786315e2fc2b`. `git status --porcelain` on the cited paths printed nothing, so the working copy equals the committed bytes. The kengaku `SKILL.md` lines 494, 495 and 663 have md5 `1881789ac0551b816de2859efa187027` in both HEAD and the working copy. The full per-quote record is in `out/ConnectorReportOuts/quote-check.tsv`.

- **kengaku `r10-scout-endpoint.md:33` matches.** `git show HEAD:... | sed -n 33p | grep -o` printed all four tokens: `--ctx-size 16384`, `--fit off`, `--kv-unified` and `--parallel 2`.
- **kengaku `r10-scout-endpoint.md:67` matches.** The line reads "unified KV ⇒ each slot reports the **full** 16384, not 16384/2".
- **kengaku `r10-scout-endpoint.md:74` matches.** The line reads "unified KV (shared across the 2 slots; see /slots above), so a 2-slot server does **not** halve per-slots context".
- **kengaku `SKILL.md:494-495` matches.** The lines read "`--kv-unified` with `--parallel 2` (each of 2 slots reports / the full 16384 ctx; slot draws do not share a halved context)".
- **kengaku `SKILL.md:663` matches.** The line reads "historical identity — endpoint refuses connections since 2026-10-15".
- **kengaku `r11-prior-art-prereg.md:193-194` matches.** The quoted sentence actually starts at line 192.
- **kagi `op-cli-surface.md:91` matches, byte-identical in HEAD.** The line reads "(llama.cpp `/health` → `{"status":"ok"}`; a foreign listener 404s or closes.)". The probe it describes is at lines 87-88: `curl -fsS --max-time 2 ".../health"`.
- **kagi `SKILL.md:43` is a partial match.** The line has the same `curl -fsS <endpoint-minus-/v1>/health` → `{"status":"ok"}` probe, but not the foreign-listener sentence. "Uses the same rule" holds for the probe only.
- **The kama-side fix has landed.** The connector proposed adding the `--kv-unified` premise to `SKILL.md:188-189`. At tip fa3b62ae, `SKILL.md:188-190` reads "only because that launch also set `--kv-unified`: both slots share one 16384-cell pool". `corpus/knowledge/context-capacity.md:176-185` cites kengaku as "historical, other-build evidence, not a kama observation", so it is cited rather than absorbed.
- **The kama L1 evidence is present.** `.ufo/waves/round-25/final/raw/L1.server.log:1849` reads "send_error: task id = 2, error: Context size has been exceeded.", and `:1866` reads "stop processing: n_tokens = 1025".
- **Kengaku has no record of the concurrency half.** I ran `grep -rn 'Context size has been exceeded|shared pool|one pool|pool total'` over kengaku, excluding `.git`, `.jj` and `.ufo`. The only hits were two unrelated "pooled BSS" lines.
- **Kagi has no record of the loading state.** I ran `grep -rln '503|Loading model|MODEL_LOADING|unavailable_error'` over kagi's md, sh and py files. All five hits are inside hashes or line ranges. None of them is about a loading server.

## What failed: one wording defect

The connector wrote: "Kagi's rule classifies a still-loading llama-server, which answers 503, the same as a foreign listener." That is stronger than kagi's text supports. Kagi names two outcomes (ok, and "404s or closes") and is silent on 503.

The conflation happens at the exit code. `man curl` (curl 8.23.0) says `-f` makes curl "Fail with error code 22 and with no response body output at all" for HTTP codes of 400 or greater. So a 503 and a 404 give the same exit code and neither prints a body. Reading the probe as pass or fail therefore treats a loading server like a squatted port. That misreading is a possible case, [INFERENCE]; no kagi incident was observed.

**Smallest correction:** "Kagi's `/health` rule has no row for 503. Under `curl -f`, a loading server's 503 exits 22 with no body, the same as a foreign 404."

The kagi draft note uses that wording.

## Deliverable: two draft report-out notes for the round report

- `out/ConnectorReportOuts/report-out-kengaku.md` covers the shared-pool concurrency half. It states what kama found (L1: both concurrent requests HTTP 500 at 1025 tokens each on a 2048 pool; L2 and L3 HTTP 200). It gives the evidence path (`context-capacity.md:99-125`, `L1.server.log:1849,1866`, S109, `SKILL.md:688`). It lists three checks for kengaku: combined token load on concurrent 34113 draws, any 500 `Context size has been exceeded.` graded as a model failure, and a wording addition at `r10:74` and `SKILL.md:494-495`. It also states the limits: other build, q4_0 KV, transfer is [INFERENCE], and 34113 is historical with no probing.
- `out/ConnectorReportOuts/report-out-kagi.md` covers the health rule. It states what kama found (a loading server answers 503 `Loading model` before the API-key check). It gives the evidence path (`llamacpp-loading-lifecycle.md:9,27-36`, S036, S037, round-16 receipt). It lists three checks for kagi: past diagnoses that took a failed `/health` as proof of a foreign listener, a 503 row read from the status code, and keeping `op-cli-surface.md:91` and `SKILL.md:43` in step. It also states the limits: build 11755 single-model only, router mode differs, and the misreading is [INFERENCE].

## Risks

- If the report uses the connector's original kagi sentence, it says more than kagi wrote. Use the corrected wording above.
- The kengaku note must keep the "historical, other build" label. Without it, the note reads as a claim about kengaku's results.
- Sibling lines can drift after today. The quotes are pinned to the HEADs listed above.

## Verification (for the L1; this seat already ran these read-only checks)

- `git -C kengaku-shokunin show HEAD:corpus/evidence/round10-fleet/r10-scout-endpoint.md | sed -n '33p;67p;74p'`
- `git -C kagi-shokunin show HEAD:corpus/knowledge/op-cli-surface.md | sed -n 91p` and `sed -n 43p kagi-shokunin/SKILL.md`
- `man curl | col -b | grep -A3 -- '-f, --fail$'`

## Files written

- `.ufo/waves/round-25/a2-falsify/advice/ConnectorReportOuts.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/ConnectorReportOuts/report-out-kengaku.md`
- `.ufo/waves/round-25/a2-falsify/out/ConnectorReportOuts/report-out-kagi.md`
- `.ufo/waves/round-25/a2-falsify/out/ConnectorReportOuts/quote-check.tsv`

Report: .ufo/waves/round-25/a2-falsify/advice/ConnectorReportOuts.md
