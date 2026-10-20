# Round 12 — MistakeScribe draft: D1–D5 Mistakes / Gate candidates

Author advisor (leaf, no delegation). Draft only; the lesson was not edited. No scripts, builds, tests or endpoints were run. Evidence is static `read`/`grep` of the lane tree plus the round-11 closure text. "Closure-reported" means the value comes from `corpus/lessons/round-11-verifier-spotcheck.md` and was not replayed here. Tools installed or updated: none.

Scope note: C1 (calibration 7→7, delta 0; `.ufo/waves/round-12/claims.json`) rests only on D1. D2–D5 are conformance/clarity repairs. They move no axis and must not be cited as calibration evidence.

## Mistakes candidate rows

| Class | Evidence pointer | Captured-by | Fix and demonstrated failure criterion |
|---|---|---|---|
| survivor | `corpus/lessons/round-11-verifier-spotcheck.md:101-118` (D1). Closure-reported: frozen `.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` SHA-256 `52665cf2…42fa1`; `git show 2f7303c…:corpus/SOURCES.md` SHA-256 `9dc40d25…2093`; frozen search-log line 55 truncated. Digest-only check passed against `expected.json`. | KQ14 (existing: "content correspondence"; "zero uncorrected count… does not prove"). Round-11 Mistakes `survivor` row (KQ11/KQ14). | Produce `.ufo/waves/round-12/frozen/corpus/SOURCES.md` directly from `git show 2f7303c…:corpus/SOURCES.md`; pin its SHA-256 and the source commit/path in `frozen/expected.json`; `fidelity.py` compares the immutable blob. **Red-before:** `fidelity.py --snapshot <round-11 frozen before SOURCES>` with no manifest must exit 1 `source_mismatch`. **Attack red:** a coherent edit of snapshot and manifest must still exit 1 `source_mismatch` against git bytes. Append an erratum to round 11; do not rewrite its frozen receipt. |
| stale-premise | `corpus/SOURCES.md:6-7` says "Every row was opened in round 10 (2026-10-19)". Row S031 (`:43`) has `opened` = 2026-10-20. Closure-reported D2. | none existing for registry prose/date scope. Candidate new KQ15 (see below). | Append a scope/navigation correction naming each row whose `opened` differs from 2026-10-19 (S031) without editing any source-row cell. **Red-before (static, observed):** header claims all rows are 2026-10-19; S031 contradicts it; no correction exists. Check: count of rows with `opened` ≠ header date and no appended correction naming them = 1 pre-fix, 0 post-fix. |
| stale-premise | `corpus/SOURCES.md:48` "Served identity (next entry, K02)". `corpus/knowledge/served-identity-crosswalk.md` exists (landed). Closure-reported D2. | none existing; same KQ15 candidate. | Append a correction stating the crosswalk is landed at that path. Red-before: `:48` says "next entry" while the file exists. Post-fix: appended correction names the landed path; `:48` unchanged. |
| reference-drift | `SKILL.md:357` "Admission remains `corpus/QUALITY.md` KQ11–KQ13" (observed by grep). `corpus/QUALITY.md:41` defines KQ14. | none existing for pointer completeness; candidate KQ15. | Append a pointer to the complete applicable QUALITY bar (the current highest id, KQ14, named explicitly), not a reduced range. Red-before: `grep -n 'KQ11–KQ13' SKILL.md` → line 357. Post-fix: pointer's highest id equals the highest `KQ` heading in `QUALITY.md`. Historical `lessons/round-11.md:89,96` stay unedited. |
| inference-label | `corpus/knowledge/served-identity-crosswalk.md:38` "Available inventory is not proof of local weights (S031/S010)": stated without `[INFERENCE]`. Same file `:45` labels the digest join correctly. S031 `teaches` cell (`SOURCES.md:43`) is immutable. Closure-reported D4. | KQ13 (existing: "A digest join beyond the documentation is labeled inference"), applied to the locality consequence. | Label the locality consequence `[INFERENCE]` and keep the documented fields (`remote_model`, `remote_host`) as documented. Append a note that "supersedes S011" is registry supersession, not an upstream change. **Red-before (static, observed):** `:38` has 0 `[INFERENCE]` tags on the locality sentence. Check: locality-residency sentences without `[INFERENCE]` or a source-section citation = 1 pre-fix, 0 post-fix. |
| landing | `.ufo/round-10/SEAT-PROTOCOL.md:1` "binding on all 64 seats"; lines 1–11 read with no archival, historical or non-execution marker. Round-11 lesson `:87` calls it an undelivered historical plan. Closure-reported D5. | Round-11 Mistakes `landing` row (PROTOCOL inherited-state rule, existing). | Put a non-execution disclaimer in the artifact itself (see the D5 placement decision below). **Red-before (static, observed):** lines 1–5 contain no marker. Check: `grep -n -i` for `historical|not executed|archiv` within lines 1–5 = 0 pre-fix, ≥1 post-fix. |

## Gate candidate rows

| Candidate | Decision | Captured-by |
|---|---|---|
| Old round-11 frozen SOURCES snapshot as correspondence evidence | reject as correspondence evidence; keep as historical record with D1 erratum | KQ14 |
| New byte-exact snapshot `.ufo/waves/round-12/frozen/corpus/SOURCES.md`, pinned in `expected.json` | admit, calibration-only, scope = exact bytes at 2f7303c; no scalar change | KQ14, KQ11 |
| Digest-only integrity (snapshot SHA matches expected file) | reject as proof of source correspondence | KQ14 |
| Coherent source+manifest mutation passes the manifest check | must fail as `source_mismatch` against git; otherwise the gate is not falsifiable | KQ14 (falsifiability) |
| D2/D3 stale prose and pointers | admit as conformance repair only under KQ15, if L1 adopts it; otherwise record as uncaptured | KQ15 (candidate) |
| D4 locality inference label | admit; extends KQ13 application, no new criterion | KQ13 |
| D5 archival disclaimer | admit; prior-round plan stays non-executed | Round-11 PROTOCOL inherited-state rule |

Candidate KQ15 wording (for L1 decision, not written here): "Registry scope/date prose and navigation pointers reconcile with per-row `opened` dates, the landed-entry set and the highest current KQ id; each contradiction is corrected by appended text, and a stale pointer fails a command-checkable count." Rejected alternative: folding it into KQ14, because KQ14 concerns claim content correspondence, not navigation prose.

## D5 placement decision for L1

The contract allows only appended historical disclaimers to prior-round evidence. D5 asks for the disclaimer "at that artifact before anyone reuses it", which a footer does not satisfy. Options: (a) prepend a one-line banner above line 1, which edits the file's head; or (b) append a block at the end, which is contract-literal but leaves "binding on all 64 seats" as the first line. My recommendation is (a), because the file is an undelivered plan with no execution path, so a head banner changes no behavior. L1 must rule explicitly, since the two readings conflict.

## Red-before obligations and L1 checks (named, not run by this seat)

1. `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/fidelity.py --snapshot /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-11/frozen/before/corpus/SOURCES.md` → expected exit 1 `source_mismatch`. This is the D1 red. Recompute both SHA-256 values; the closure values are not replayed.
2. Same CLI with the new snapshot and default manifest → expected exit 0 `clean`.
3. `fidelity.py --selftest` → expected exit 0 covering clean, mismatch, tamper and unavailable.
4. `reproduce.py` (once the runner writes it) → confirm the coherent-mutation attack exits 1 `source_mismatch`.
5. D2–D5 static checks as listed in the table: `grep -n` for `opened in round 10`, `next entry`, `KQ11–KQ13`, `proof of local weights`, and a head-of-file marker check on `SEAT-PROTOCOL.md` lines 1–5. Each red count stated above should be reproduced before any edit lands.
6. Frozen digest: `git show 2f7303c…:corpus/SOURCES.md | sha256sum` against the stored snapshot digest. Expected to differ from the old frozen file, per closure.

## Limits

- D1 digest values and the truncated line 55 are closure-reported. My grep returned a display line citing `artifact://1157:raw:55-55`, consistent with the closure's account but not proof of file bytes. The byte comparison decides.
- No mistake row here counts as execution evidence. The rows define the red-before, fix and checks for L1 to run once after integration.
