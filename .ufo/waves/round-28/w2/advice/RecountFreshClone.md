# RecountFreshClone — C1 falsify (wave 2)

Verdict: **HOLDS**. The landed measurement reproduces exactly on a fresh clone at the measured tip e49b4cf77046024551ba83d490ef83d9dee061ed with the frozen counters.

## Setup
- Fresh clone: `/fast/scratch/hyaku/kama-r28/w2/RecountFreshClone/tree` (HEAD verified `e49b4cf...`; origin of the lane repo).
- Counter copies: clone's `.ufo/waves/round-28/count-c1.py` sha256 `a38faefeeb48be9fd3590b5077030ed6b7cef08dcaf1ca0540b464bd222749a5` (= pinned A1); `git show d8bf1804:.ufo/waves/round-28/count-c1.py` sha256 `e6a706bb2e15aec288924b9aec863ff0b1ffdd7e588e78250c0f642565c0540c` (= pinned A0). Both matches.

## Verbatim outputs
- C1 (frozen A1 counter, from clone tree, `timeout 900 /usr/bin/python3 .ufo/waves/round-28/count-c1.py --out <scratch>/c1-receipt.json`):
  `registered 34 counted 26 target 18 met True not-counted ['F28-11', 'F28-14', 'F28-16', 'F28-17', 'F28-21', 'F28-22', 'F28-25', 'F28-26']`, exit 0.
- A0 counter (same tree, `--lane <clone> --out <scratch>/a0-receipt.json`):
  `registered 34 counted 34 target 18 met True not-counted []`, exit 0.
- Both match `final/` verbatim (`c1-e49b4cf7.out`, `c1-A0-e49b4cf7.out`; exit=0). Receipts: schema `v1-A1` / `v1`, `counter_sha256` pins as above; non-row fields identical to `final/*-receipt.json` (lane path aside). Per-row diffs are only `base_request_sha256` / `body_sha256` (nondeterministic response-content hashes); `status`, `effective`, `base_effective`, `message`, `why` identical for all 34 rows in both counters.

## Checks
1. Excluded fields: no registry row uses `n_cache_reuse` or `xtc_threshold` (34 rows scanned; intersection empty).
2. Ids unique: 34 distinct ids (F28-01..F28-34), no duplicates.
3. Exactly one SKILL table row per counted row: section heading `## Round-28 request-field outcomes` with exact header; 34 data rows; each counted id appears exactly once (no dup ids in table).
4. No substring-matched junk: for all 26 counted rows the SKILL cells hold the verbatim value: field cell == registry field, value cell == canonical JSON, outcome cell == canonical outcome text (`reject 400, bounds …` / `200, <key> = …`), meaning >= 6 words, source cell contains the S### token (word boundary). Zero deviations.

## Notes
- The A1 not-counted set is exactly the eight generic-conversion rows (float32 saturation: top_n_sigma, dynatemp_exponent, repeat_penalty, frequency_penalty, mirostat_tau, mirostat_eta; uint32 wrap: seed; truncation: n_probs) — consistent with A0 counting 34 and A1 refusing them (26). CtlA1Conversion's 0/52-under-A1 behavior is coherent with this.
- Server/model/source pins were verified inside the counters (both exited 0, no `could_not_evaluate`).
- No tool installs performed. Lane ports 47600-47619 confirmed free after the runs (`ss -ltnp`); no leftover server from this item.
