# K0Harm — round-48 no-harm attack (run at 380bcdff9c8af06997c482f6eb03db926a794a2b)

**Verdict: mixed — 4 commanded gates pass, 3 fail (2 fail on the known integration items, 1 is a NEW exit-2 wall in `sources-append-only.py`), and 2 NEW gaps found: both legacy receipt readers (`tests/llamacpp-live/check-receipt.py`, `tools/gguf-identity.py`) reject the round-48 v5 receipts. The SOURCES change itself is append-only in substance (+S492 +S493 only, no deletions); no new digest/hexrun pollution was introduced.**

Evidence: `out/K0Harm/evidence/commands.out`, `out/K0Harm/evidence/receipt-readers.out`; receipts copied to `out/K0Harm/` (`receipt-{1,2,3}.json`, `install.txt`, `evidence/v4-receipt-1.json`). All commands ran in a scratch clone at `380bcdff…` (`git clone --shared`), TMPDIR in scratch.

## Command results (tip 380bcdff…)

| Command | exit | Verdict |
|---|---|---|
| `python3 tools/gate-registry-check.py` | 1 | FAIL — known: 2 unregistered (`tools/round48-append-audit-v3-check.py`, `tools/round48-live-replay-v5-audit.py`); registered 40 unregistered 2 defective 0 |
| `python3 tools/capability-repertoire-audit.py` | 0 | PASS — listed 11 observed 11 missing 0 unsubstantiated 0 met True |
| `python3 tools/round41-scorecard-reconcile.py` | 1 | FAIL — known: spot count 33 vs 34 (calibration row), mismatches=1 met=False |
| `python3 tools/round42-selfdesc-reconcile.py` | 1 | FAIL — known: r41=1 (same spot mismatch), mismatches=1 met=False |
| `python3 tools/round43-registry-audit.py` | 1 | FAIL — known + mechanism note: unreg=2, spot 33 vs 34, and gate selftest documented pass=6 fail=0 vs run pass=5 fail=1 (see calibration) |
| `python3 tools/planned-pointer-check.py SCORECARD.md` | 0 | PASS — pointer ok, 8 measured results ok, met=True |
| `python3 tools/digest-ledger.py scan --repo . --rev 380bcdff…` | 0 | PASS — tokens=123; external_absent=1, wrong_flagged=1 identical to base 33e005 (pre-existing, not round-48) |
| `python3 tools/hexrun-census.py scan --repo . --rev 380bcdff…` | 1 | FAIL — known: unknown=1 = d0012618 (round-47 fleet report commit), same as base; no new unknown |
| `python3 tools/sources-append-only.py --from 33e005… --to 380bcdff…` | 2 | **FAIL — NEW** — parse guard refuses: row-like line `| S010 | …` at `corpus/SOURCES.md:520`@33e005 (:522@380bcdff) inside the round-45 re-verification table; see F1 |
| `tests/llamacpp-live/check-receipt.py --selftest` | 0 | PASS (14 VALID + 1 NOT-EVALUATED accepted, 103 mutations rejected) — but v5 receipts are **rejected** (F2) |
| `tools/gguf-identity.py --selftest` | 0 | PASS (30/30) — but `--receipt` on a v5 receipt exits 2 `receipt_schema_unsupported` (F3) |

`python3 tools/round48-append-audit-v3-check.py` (C1) was re-run by this seat on the real build commit: `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`, exit 0 — the C1 claim reproduces at the actual 380bcdff commit.

## Axis-by-axis

### Operability — FAIL (new)
- `sources-append-only.py` cannot grade the round-48 SOURCES append at all (exit 2). The append itself is clean (`git diff 33e005..380bcdff -- corpus/SOURCES.md` = exactly +2 lines, S492 + S493, no deletions), so the round-48 change is *in substance* append-only; the tool is simply unusable on any revision containing the round-45 re-verification table (F1).
- The two legacy receipt readers reject the v5 receipts the build ships (F2, F3). Neither is wired into current gates, so this is a latent operability break, not a live gate failure.

### Freshness — PASS
- `digest-ledger` at 380bcdff: tokens=123, external_absent=1 (bcc55c92…), wrong_flagged=1 (5585f602…) — byte-identical flag set to base 33e005: nothing new went stale or absent this round.
- `hexrun-census` at 380bcdff: tokens 1800→1803 (all three new runs classified lane/upstream), unknown stays exactly d0012618 (the known round-47 fleet report commit). No new unknown.
- Improvement: the v5 receipts pin the model URL to HF commit `499bc882…` (S492 row), replacing the moving `main` resolve URL (S490) — the freshness risk the round-47 D6 flagged is closed.

### Depth — PASS (with toolchain-breadth caveat)
- C1 v3 region grading (exempt/only) exercises at the real build: contract has 9 rows incl. SCORECARD exempt head (5 titles) and consumer-registry `only=## Errata`; counter met=True with ungraded_lines=89, exit 0.
- Caveat: the *newer* v5 schema is understood by fewer tools than v4 was — check-receipt.py and gguf-identity.py still only know v1–v4 (F2/F3). Depth of the shipped artifact (v5 receipts) exceeds the depth of the lane's reader set.

### Coverage — PASS modulo the known unregistration
- capability-repertoire-audit met=True; planned-pointer-check met=True; digest-ledger exit 0; hexrun covers the new commits with no new unknown.
- Gate registry coverage: 40 registered / 2 unregistered (the two round-48 counters) — known integration item, expected until their SKILL.md rows land.

### Calibration — FAIL (known items confirmed; one mechanism note)
- round41/42/43 reconcile all fail on the known spot-count mismatch (calibration row says 33, tree holds 34).
- round43 additionally flags gate selftest: documented `GATE_SELFTEST pass=6 fail=0`, run prints `pass=5 fail=1`. Root cause is the same known unregistration: the gate's `--selftest` lane-tip arm (gate-registry-check.py:338-349) evaluates the *live* lane tip, so any wave with unregistered counters makes the gate's own selftest fail by construction until SKILL.md rows land (F4). This is a non-hermetic selftest design, not a regression in the fixture matrix (arms 1–5 pass).

### Adjacency — PASS
- No sibling lane consumes kama live/receipt tools: a fleet-wide grep for `check-receipt.py|gguf-identity.py|kama-live-replay.py|kama-llamacpp-live.py` across `/home/vgpnk/Projects/shokunin/*-shokunin` found only historical connector/scout markdown notes, no code references. F2/F3 therefore stay intra-lane.
- No writes were made outside the seat's named paths; lane, fleet and sibling lanes untouched.

## New findings

- **F1** — `tools/sources-append-only.py` exit 2 on every revision since round 45: row-like line outside the parsed registry table. Evidence: `python3 tools/sources-append-only.py --from 33e005… --to 380bcdff…` → `error: 33e005…:corpus/SOURCES.md:520: row-like line outside the parsed registry table; refusing to drop it` (also on `--from 33e005 --to 33e005`). Line 520@33e005 / 522@380bcdff holds `| \`S010\` | ollama …` — a row in the round-45 "re-verification" table (added by commit `052cb1e9`), not a registry row. The scan at `tools/sources-append-only.py:227-232` applies `ROWLIKE_RE` to the whole blob, so a non-registry table whose first cell looks like `S0NN` permanently blocks the guard. Fix: scope the row-like scan to the parsed registry section (from the `Registry` heading to the next same/higher heading) instead of every line in the document, or rename the round-45 table's id column to non-S keys. (Proposed diff in `out/K0Harm/findings.md`.)
- **F2** — `tests/llamacpp-live/check-receipt.py` rejects v5 receipts. Evidence: `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-48/c2/live/receipt-1.json` → `INVALID … 4 problem(s)` (schema `kama-llamacpp-live/v5` not in whitelist; check-set diff is an artifact of falling back to v1 rules). Control: the round-47 v4 receipt validates (`VALID`, exit 0); the v4 and v5 check sets are identical (11 ids: incl. `teardown_graceful`, `loading_envelope_graded`, `model_unchanged`). The only v5 delta is the schema name + provenance.verified. Fix: add `RECEIPT_SCHEMA_V5`, accept it as v4+ (require `provenance.verified` with archive/member/model sha256 matching `server.asset_sha256`/`server.sha256`/`model.sha256`), and extend `--require-schema` choices to include v5 (`tests/llamacpp-live/check-receipt.py:51-55,305-312,2435`).
- **F3** — `tools/gguf-identity.py` `--receipt` does not support v5. Evidence: `python3 tools/gguf-identity.py <model.gguf> --receipt .ufo/waves/round-48/c2/live/receipt-1.json` → `{"receipt": {"exit_code": 2, "reason": "receipt_schema_unsupported", "status": "could-not-evaluate"}}` (model itself parses, sha256 matches 270cba1…). Schema whitelist is v3/v4 only (`tools/gguf-identity.py:44-47,480-481`). Fix: add `kama-llamacpp-live/v5` to `RECEIPT_SCHEMAS`, reconciling the same fields as v4.
- **F4** — gate-registry-check selftest lane-tip coupling (mechanism behind the known round-43 selftest mismatch): `--selftest` arm 6 evaluates the live lane tip (`tools/gate-registry-check.py:338-349`), so `GATE_SELFTEST pass=5 fail=1` while the two round-48 counters are unregistered; the documented `pass=6 fail=0` (round-43 audit) only holds once SKILL.md rows land. Fix (optional): pin the lane-tip arm's expected unregistered count or allow a known-unregistered allowance so the selftest stays hermetic outside registry-complete states.

Known items confirmed (not re-reported as findings): gate-registry-check unregistered ×2; round41/42/43 spot 33 vs 34; hexrun unknown d0012618.
