# CN01 — sibling-overlap scan, kama r81 w1 (connector)

Base `e7d2fd72` · lane `master` = `2c1faed0354dbb3cb9f869cb1af4a9302dfcfd4e` · read-only; receipts (per-lane rc + hits) at `…/round-81/w1/CN01SiblingScan/receipts.txt`.

## 1. Does any sibling lane cite the filed S557 URL? — no, zero hits

- `grep -rn --binary-files=without-match "openai-compatibility" <lane>/corpus/SOURCES.md <lane>/corpus/knowledge/` → rc=1, 0 hits, all 20 siblings; `grep -rn --binary-files=without-match -E 'v0\.40\.11/(docs/)?api-openai-compatibility|api-openai-compatibility\.mdx' <lane> --exclude-dir=.git --exclude-dir=.jj --exclude-dir=.ufo` → rc=1, 0 hits, all 20 siblings.
- `grep -rln --binary-files=without-match "ollama" */corpus/SOURCES.md` → `kama-shokunin/corpus/SOURCES.md` only: no sibling lane cites Ollama documentation at all.
- Fleet-wide (excl. `.git`/`.jj`/`.ufo`) the string occurs exactly twice, both kama: `kama-shokunin/corpus/SOURCES.md:312` (the S557 row) and `kama-shokunin/corpus/lessons/round-80-verifier-spotcheck.md:40`.
- Dead? Yes per kama's own recorded finding, not refetched by me: `round-80-verifier-spotcheck.md:40` — HTTP 404, 14 bytes at that path, 200/25472 B at `docs/api/openai-compatibility.mdx`, sha256 `44071a12…cd5`. No sibling cites it, so **no sibling holds a dead citation and the S557→S558 erratum cannot damage a foreign corpus.**

## 2. Append-only acceptance/register family in sibling lanes — none held; in-province

- `grep -rn --binary-files=without-match -E 'append-accepted|append-registers|append-exempt|append-only-audit' <lane> --exclude-dir=.git --exclude-dir=.jj --exclude-dir=.ufo` → rc=1 for 19 siblings; `souji-shokunin` rc=0, 6 hits, every one a **census receipt about kama, not a sibling instrument**: `census/round-55/wave/w1/S55connector01/receipts/sibling-classification.tsv:72` (kama class C, `tools/append-only-audit.py`, `OVERLAP`); `census/round-56/wave/w1/S56connector01.md:22`; `…/S56connector01-report.md:113,252,313`; `census/round-56/wave/w1-results.json:16`.
- `ls -1 */registry/*append*` → the five registers `append-only-{accepted.tsv,contract.tsv,declarations.md,disclosures.tsv,exempt.tsv}` exist only under `kama-shokunin/registry/`.
- **Ruling: in-province, not absorption.** No lane owns a late-acceptance or accepted-history rule: `grep -rn --binary-files=without-match -iE "late[- ]accept|accept(ed)?[- ]history"` outside kama returns only unrelated prose (`tabi-shokunin/corpus/knowledge/aria-loopback-round-13.md:33`, `tsukuroi-shokunin/corpus/README.md:602`). kama owns it via `PROVINCE.md:17` (lane-instruments row) and `:328`; a census classification owns duplication findings, never acceptance.

## 3. Adjacency lines (one per surface)

- kama `PROVINCE.md:12` — `served-model-id reconciliation | GET /v1/models vs --alias vs the configured model id` (probe form `:254`, `127.0.0.1:8080/v1/models`): S557 grounds exactly this surface, so its correction is kama row work.
- Contested scope: kama `PROVINCE.md:169` ("The generic pinning *method* … is chousa's ground; the specific re-pin of the two held docs rows is kama's") against `chousa-shokunin/PROVINCE.md:5-6` ("citation chaining and hop resolution; claim-vs-source verification … this lane's own corpus"). Dead URL on a kama-held row = kama; pinning method = chousa; no sibling document names S557, so nothing is absorbed.
- Live foreign binding: souji's census binds `kama-shokunin/tools/append-only-audit.py` by **content sha256** `2b9285bfdeeeeda4…f38ff4ee` plus `def numstat` `:465–473`, `clean_at_HEAD` at kama commit `6035e952c252…` (`souji-shokunin/census/round-56/wave/w1/S56connector01.md:22`; paired with `kaidoku-shokunin/tools/round-61/numstat-edge-audit.py:151 parse_numstat` / `:120 NUMSTAT_BINARY`). Re-derived: that digest holds at lane `2c1faed0` and at `6035e952`, `grep -n "def numstat"` = `465` — the foreign cell is exact today and any byte edit in `:465–473` retires it.

## Connector return

**Evidence** — §1–§3, each with its grep and rc; `receipts.txt` is the machine copy. **Affected axes** — adjacency (protected: negative evidence added, no score claimed), operability (C2 counter's implementation shape), calibration (untouched; C1 reads no sibling).
**Proposed move (one, bounded)** — make `tools/round81-append-debt.py` a pure consumer of the frozen `tools/append-only-audit.py --json` (no second `git diff --numstat`/`git diff-tree` parser), keep `append-only-audit.py:465–473` byte-frozen so souji's census digest stays exact, and put the zero-sibling-citation result as one sentence in S558's notes cell rather than as a claim.
**Risks** — S558's notes cell opens once, so the sentence must be final at filing; a future souji census at a new tip may re-classify the new module (expected reclassification, not harm); the 404 is kama's recorded finding, not my fetch.
**Verification** — re-run §1/§2 greps at the filing tip; `sha256sum kama-shokunin/tools/append-only-audit.py` must still print `2b9285bfdeeeeda4…f38ff4ee` and `grep -n "def numstat"` must still print `465`.
