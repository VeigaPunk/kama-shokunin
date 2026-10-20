# Round 13 — EvidenceScribe: routed D1 and quality-attribution evidence table

Scope: static reads only, committed HEAD `941bb32` (`git status --short` showed only the untracked `.ufo/waves/round-13/`, so the files cited below equal HEAD). No builds, tests, linters, `fidelity.py`, `reproduce.py`, selftest or census were executed. Tools installed or updated: none. Fleet repo, `.ufo/reports/round-12/kama.md` and sibling repos were not read.

Citation keys: **actual** = the file's bytes at the cited line; **static** = code/text read by eye; **receipt** = committed `.ufo/waves/round-12/acceptance.json` observation, not a fresh execution; **closure-reported** = stated by the round-12 closure lesson, not re-observed here.

## Evidence table

| # | Claim under review | Exact location (file:line) | Named owner | Category | Observation |
|---|---|---|---|---|---|
| E1 | Routed D1 item: append KQ15 wording erratum | `corpus/lessons/round-12-verifier-spotcheck.md:147` (item 1) | kama (next round) | static | Routes two precision defects in KQ15; says status-neutral; says do not rewrite old bytes. |
| E2 | KQ15 says mismatch, tamper and unavailable "each have distinct nonzero exits" | `corpus/QUALITY.md:49` (KQ15 row, "Admit only when" column) | kama | actual | Wording present verbatim. Inaccurate as an exit claim, see E3. |
| E3 | Exit classes actually produced | `.ufo/waves/round-12/fidelity.py:319` `exit_code = 0 if finding == 'clean' else (1 if finding == 'source_mismatch' else 2)` | kama | static | Mismatch = 1; snapshot_tampered, source_unavailable, manifest_invalid, unpinned, snapshot_unavailable, internal_error all = 2. Tamper and unavailable **share exit 2**. |
| E4 | Stable distinct finding IDs | `.ufo/waves/round-12/fidelity.py:64-68` (`PRIORITY` tuple, starts `snapshot_unavailable`, `manifest_invalid`, `snapshot_tampered`, …); IDs `source_mismatch` at `:305`, `source_unavailable` at `:276` | kama | static | Finding IDs are distinct and precedence-ordered; exit codes are not. Correct phrasing: distinct stable finding IDs, shared exit 2 for could-not-evaluate classes. |
| E5 | SKILL registry already states the correct classes | `SKILL.md:396` (verdict-map cell) and `SKILL.md:398-409` notes | kama | static | Registry row: `0 clean; 1 failed (source_mismatch); 2 could-not-evaluate (snapshot_tampered, …, source_unavailable, unpinned, internal_error)`. Supports the erratum; KQ15 is the inconsistent surface. |
| E6 | KQ15 says the comparison blob is fetched "as `git show <pinned-commit>:<source-path>`" | `corpus/QUALITY.md:49` (same row, "Admit only when" column) | kama | actual | `git show` appears as the **comparator** source here. |
| E7 | Comparator actually uses `git cat-file blob` | `.ufo/waves/round-12/fidelity.py:271-273` (gate check path) and `:442-444` (selftest's pinned-source read inside `--selftest`) | kama | static | Both call `git_run(..., 'cat-file', 'blob', f'{SOURCE_REVISION}:{SOURCE_PATH}')`. No `git show` call in the comparator. |
| E8 | Capture is `git show`, comparison is `git cat-file blob` | `corpus/lessons/round-12.md:14-15` ("Capture uses `git show` (S032); the same measurement command independently reads the pinned historical blob with `git cat-file blob`"); `.ufo/waves/round-12/advice/Fidelity.md:37-40` | kama | static | Lesson and advice already separate capture from comparison; KQ15 at `QUALITY.md:49` does not. |
| E9 | Old-snapshot mismatch receipt (before = 1) | `.ufo/waves/round-12/acceptance.json` grep hits at lines 148-149 (`"exit": 1`, `"finding": "source_mismatch"`), 461-462 | kama | receipt | Committed observation; not re-executed. |
| E10 | Corrective snapshot receipt (after = 0 / clean) | `corpus/lessons/round-12.md:210` (record table row "New corrective snapshot, committed pin \| 0 / `clean` \| 0"); `.ufo/waves/round-12/acceptance.json` (after record) | kama | receipt | Committed observation. |
| E11 | Tamper / could-not-evaluate receipts exit 2 | `.ufo/waves/round-12/acceptance.json:379-380` (`"exit": 2`, manifest_invalid, plus source_mismatch detail); `corpus/lessons/round-12.md:212-214` (`snapshot_tampered` 2; `source_unavailable` 2) | kama | receipt | Confirms E3: could-not-evaluate classes exit 2. Receipt wording cannot itself show "distinct exit" for tamper vs unavailable. |
| E12 | Coherent snapshot+manifest mutation stays exit 1 | `.ufo/waves/round-12/acceptance.json:281-282` (`"exit": 1`, `source_mismatch`); `corpus/lessons/round-12.md:211` | kama | receipt | Consistent with the KQ15 clause "mismatch … distinct nonzero exit"; does not contradict E3. |
| E13 | Quality attribution routed item 3 | `corpus/lessons/round-12-verifier-spotcheck.md:149` (item 3); `:122` (quality = improved, grounded in D4) | kama | static | Routes: cite the D4 knowledge-entry interpretation for quality, not D1 snapshot/gate machinery. |
| E14 | Current round-12 quality attribution credits gate machinery | `corpus/lessons/round-12.md:268-270` ("quality **improved** (fail-capable exact-source repair and explicit D1–D5 limits)") | kama | static | This is the wording the closure asked kama to stop using as the sole basis. Existing lesson bytes stay immutable; the correction belongs in the next round's attribution. |
| E15 | D4 knowledge-entry interpretation (credit target) | `corpus/knowledge/served-identity-crosswalk.md:87` (heading "Correction — round 12 D4"); `:96` ("The locality conclusion is [INFERENCE]"); `:103`; `:127-132` | kama | static | Heading and `[INFERENCE]` labels observed. The S011/S031 supersession wording itself was not re-checked against upstream here. |
| E16 | Upstream D4 field support | `corpus/lessons/round-12-verifier-spotcheck.md:108` (reopened Ollama `remote_model` / `remote_host` quotes) | kama | closure-reported | Quotes are the closure's; not re-opened by this seat (no web access used). |
| E17 | S032 method row (`git show` capture semantics) | `corpus/SOURCES.md:44` (row S032, tier A, "opened 2026-10-20") | kama | static | Supports blob-plain-contents capture only; closure says it does not support the `cat-file` comparator (`corpus/lessons/round-12-verifier-spotcheck.md:106`, closure-reported). |
| E18 | Next-criterion append target | `corpus/QUALITY.md:49` is the last line (49 lines total); no KQ16 present at HEAD (`wc -l`) | kama (Criterion writer) | actual | Append-only target is after line 49. |

## Citation drift found in advice (not corpus)

- Advice `AttackSourceCuration.md` cites `fidelity.py:264-265` and `:431` for the `cat-file` reads; current committed lines are `:271-273` and `:442-444` (E7). Advice line numbers are stale; the substance (comparator = `cat-file`) holds.
- Advice `AttackSourceCuration.md` cites `round-12.md:12-13` for the `git show` sentence; current committed lines are `round-12.md:14-15` (E8).

## Limits

- Everything above is static reading or committed receipts; no check was re-run (E9-E12 are receipt observations, labelled as such).
- E16 and the S032 quote (E17) are closure-reported; I did not reopen web sources.
- `fleet .ufo/reports/round-12/kama.md` (the closure's named report) was not read: out of scope.
- Whether `fidelity.py` ever emitted `git show` in a prior revision was not checked; HEAD only.
- No `[INFERENCE]` conclusions are made beyond the tables above.

Report: .ufo/waves/round-13/advice/EvidenceScribe.md
