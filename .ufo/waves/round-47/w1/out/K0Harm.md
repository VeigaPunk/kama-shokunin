# K0Harm — No-harm attack, round 47 (measured at 3a09a1d93dcc16799cf6c4b48786e6440af134c4)

Verdict: **round-47 changes are mostly separable and low-harm, but the planned integration carries three concrete harms — (1) a stale calibration fact already red at freeze (SCORECARD verifier-lesson count says 32, tree holds 33 — makes `round41-scorecard-reconcile.py` and `round42-selfdesc-reconcile.py` red), (2) `tools/sources-append-only.py` cannot grade any SOURCES transition any more (exit 2, row-like rows in the Round-45 re-verification tables), so C2's planned `newrow` lands with no append-only-guard proof, and (3) the live receipt schema bump to `kama-llamacpp-live/v4` breaks every old v3 consumer (`tests/llamacpp-live/check-receipt.py` returns INVALID on a v4 receipt; `tools/gguf-identity.py` is v3-strict) while SKILL.md/README/knowledge still document v3 — plus two transient/acceptable reds that must be watched: gate selftest `pass=5 fail=1` vs documented `pass=6 fail=0` until the two new counters get SKILL rows, and hexrun census `unknown=22` (+1 fleet-commit token from the round-46 lesson).**

Method: fresh `git clone --shared` of the lane at `/fast/scratch/hyaku/kama-r47/K0Harm/lane`, checked out at `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (the build commit). Every command re-ran with full output/exit in `cmd-outputs.log` (same dir). Counters C1/C2 were **not** rerun by this seat (not in item scope; L1 pre-wave dry run at the same commit reported `C1 … met=True`, `C2 receipts=1 replay=1 tamper=1 newrow=0 met=False`).

## 1. Command pass/fail (required list)

| # | Command (at 3a09a1d) | Exit | Verdict |
|---|---|---|---|
| 1 | `python3 tools/gate-registry-check.py` | 1 | expected-red (pre-integration): `registered 38 unregistered 2 defective 0`; the two unregistered are the new `tools/round47-append-audit-v2-check.py` and `tools/round47-live-replay-audit.py` |
| 2 | `python3 tools/capability-repertoire-audit.py` | 0 | pass: `listed 10 observed 10 missing 0 unsubstantiated 0 met True` |
| 3 | `python3 tools/round41-scorecard-reconcile.py` | 1 | **fail**: `run_bad=1 mismatches=1 met=False`; detail `calibration run python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))" no stdout line == '32' (exit 0)` |
| 4 | `python3 tools/round42-selfdesc-reconcile.py` | 1 | **fail**: same detail (`r41=1 … mismatches=1 met=False`) |
| 5 | `python3 tools/round43-registry-audit.py` | 1 | expected-red + calibration spot: `unreg=2 defect=0 flags=0 pins=0 selftest=1 dc=0 spot=1 hidden=0 pop=40 registered=38 mismatches=4`; details: gate unregistered ×2; selftest documented `GATE_SELFTEST pass=6 fail=0` vs run `pass=5 fail=1` exit 1; spot: calibration row states 32, tree holds 33 |
| 6 | `python3 tools/planned-pointer-check.py SCORECARD.md` | 0 | pass: `pointer: ok … measured: ok (×7) met=True` |
| 7 | `python3 tools/digest-ledger.py scan --repo . --rev 3a09a1d…` | 0 | pass with pre-existing flags: `tokens=111 blob=97 external_ok=7 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0`; flagged `5585f602…` (wrong) and `bcc55c92…` (external_absent) are identical at round-46 tip `42ea1204` → not introduced by round 47 |
| 8 | `python3 tools/hexrun-census.py scan --repo . --rev 3a09a1d…` | 1 | pre-existing red, count +1: `unknown=22` vs `unknown=21` at `42ea1204`; delta token `8bca0cf333e7ceab5e734b354c87075c6efec86c` (occurrences=1) cited at `corpus/lessons/round-46-verifier-spotcheck.md:23` — a **fleet** commit (`git -C /home/vgpnk/Projects/shokunin cat-file -t 8bca0cf3…` → commit; lane `cat-file` → 128). Same unknown=22 at freeze `bbcc6dc2`, so it enters at the round-46 verifier commit `172b8ad0`, not at the build |
| 9 | `python3 tools/sources-append-only.py --from 172b8ad0… --to 3a09a1d…` | 2 | **fail (cannot evaluate)**: `error: 172b8ad0…:corpus/SOURCES.md:516: row-like line outside the parsed registry table; refusing to drop it`. Also fails on `4340cf2f→42ea1204`, `42ea1204→bbcc6dc2`, `bbcc6dc2→3a09a1d` — the guard has been unable to grade any transition since its FROM contains the Round-45 re-verification tables (`| S0NN |` row-like lines outside the `## Registry` section) |
| 10 | `python3 tools/gate-registry-check.py --selftest` | 1 | `GATE_SELFTEST pass=5 fail=1`; failing arm is `lane-tip 46a924e0`: exit=1 `registered 38 unregistered 2 defective 0` (the lane arm evaluates the live tip; 2 unregistered counters break the documented `pass=6 fail=0`) |
| 11 | old-consumer probe: `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-47/c2/live/receipt-1.json` | 1 | **INVALID** on v4: `schema is 'kama-llamacpp-live/v4', want …v1/v2/v3`; old required check ids absent/extra (see §3) |

## 2. Findings per axis

### Operability — FAIL
- **O1. schema bump v3→v4 orphans every old consumer and every v3-written doc.** Verified consumers of `kama-llamacpp-live/v3` that do not understand v4:
  - `tests/llamacpp-live/check-receipt.py` — gate validates v1/v2/v3 only (docstring `:4-9`; `RECEIPT_SCHEMA*` `:31-33`); on the committed v4 receipt-1 it prints INVALID exit 1 (see #11). A verifier or future L1 that re-validates the round-47 receipts with this gate (the documented workflow in SKILL/README) will report them invalid.
  - `tools/gguf-identity.py` — `--receipt` is v3-strict: `:44 RECEIPT_SCHEMA_V3`, `:476-478` raise `ReceiptError("receipt_schema_unsupported")` for non-v3; help text says "reconcile one llama.cpp v3 receipt".
  - `tools/round45-recheck-audit.py` `:230-232` hard-gates `r.get("schema") != "kama-llamacpp-live/v3"` on its fixed dir `.ufo/waves/round-45/c1/live` — unaffected by round 47 (separate dir), but any future round that globs live-receipt dirs across rounds inherits the break.
  - Docs still claim v3 is current: `SKILL.md:606`, `corpus/README.md:698`, `corpus/knowledge/llamacpp-loading-lifecycle.md:239`. No round-47 plan item updates them (planned section `SCORECARD.md:2677+` mentions SKILL only as a C1 flag target for a *future* freeze).
- **O2. SOURCES append-only guard is dead for the planned C2 row.** `tools/sources-append-only.py` exits 2 on the `--from 172b8ad0 --to 3a09a1d` transition (required #9) and on every transition whose base contains the Round-45+ re-verification tables. The L1's planned `corpus/SOURCES.md` row for b11909 (`newrow` leg) therefore cannot be verified by the lane's own append-only guard at integration time.
- **O3. Gate selftest is transiently self-red.** `GATE_SELFTEST pass=5 fail=1` (documented `pass=6 fail=0` in SKILL.md; round43 audits it). Cause: arm 6 (`lane-tip`) evaluates the live tip, where the two new round47 counters are unregistered. Expected to recover when SKILL rows land; until then "gate green" claims are false.

### Freshness — PASS (carryover, not build-introduced)
- Build adds no new ledger/census tokens of its own. digest-ledger flagged set identical to round-46 tip. Hexrun `unknown` grows 21→22 only because the round-46 verifier lesson (landed at base `172b8ad0`) cites a fleet commit (`8bca0cf3…`, `corpus/lessons/round-46-verifier-spotcheck.md:23`) — same pre-existing unknown family as `b0fd7b7f…` (fleet reports, 104 occurrences). Census remains exit 1 before and after; the round's own transcript must not describe `unknown=21` as current.
- Release freshness: b11909 evidence is pinned to a prerelease tag (published 2026-10-26T21:00:58Z, `prerelease: true`). Asset digest `bf94332a…` is recorded, so an upstream mutation of the same URL is caught (replay refusal path exists); the dependency on a prerelease tag should be written into the SOURCES row and re-checked next round (llama.cpp is at b119xx and moving — the round-45 recheck note already counts 121 tags above b11755).

### Depth — PASS
- `append-only-audit.py` v2 adds numstat cross-check, byte-exact line identity, window-maximised restoration (docstring `:1-44`); the C1 counter recomputes on its own code path and cannot load the tool's outputs (`round47-append-audit-v2-check.py:71`). No regression found in the tool's contract (selftest, contract header `registry/append-only-contract.tsv` = `path rule declared_at note`; 7 declared rows; expansion includes `corpus/lessons/*.md`).
- L1Lowthr (sibling) owns the below-threshold class; nothing here contradicts it.

### Coverage — PASS with bounded caveat
- `capability-repertoire-audit.py` green (10/10) — the two new counters are instruments, not repertoire, so they correctly do not appear.
- Gate coverage gap is intentional pre-integration (O3). Required action: after integration, `gate-registry-check.py` must report `registered 40 unregistered 0 defective 0` and round43's `selftest` leg must print `pass=6 fail=0`; if S1Rows/L1 draft malformed rows (thin-row/empty-entry/empty-exit-map), round43 flags a `defect`.
- C1's own coverage is pattern-limited by design (prereg `limits`): only declared paths are audited. `SKILL.md`, `PROVINCE.md`, `registry/verdict-ledger.tsv`, `corpus/SOURCES.md` rows are not part of the contract's expanded set beyond declared patterns; the contract does not self-audit.

### Calibration — FAIL
- **C1. Stale calibration fact already red at freeze.** `SCORECARD.md:18` (calibration row) states the number of `corpus/lessons/*verifier-spotcheck.md` blobs at the measured commit is `32`; the tree holds **33** (`round-46-verifier-spotcheck.md` added at `172b8ad0`). `round41-scorecard-reconcile.py` and `round42-selfdesc-reconcile.py` are `met=True` at round-46 tip (`42ea1204`, `4340cf2f`) and `met=False` from freeze `bbcc6dc2` through the measured build. This sits exactly on the axis C1 claims to work.
- **C2. GATE_SELFTEST documentation/run mismatch** (same as O3): SKILL.md documents `pass=6 fail=0`; actual run prints `pass=5 fail=1` → round43 `selftest=1`.

### Adjacency — FAIL (docs/tools cross-surface)
- The v3/v4 split (O1) is an adjacency harm: sibling repo/lesson readers and verifiers use `check-receipt.py`/`gguf-identity.py` (v3-strict) and quote the v3 schema from SKILL/README/knowledge. Any such consumer pointed at the round-47 receipts breaks.
- `install.txt`/receipt provenance are consistent (`member: llama-b11909/llama-server` matches extract layout; `teardown.log_path: null`; `captures.props.fields.build_info` = `b11909-caa8191df`; 11 evaluated checks all pass; `server.sha256 35ac50fb2…`, model sha256 matches frozen `270cba1b…`), so the *new* evidence is self-consistent — the break is purely in the older consumers.

## 3. Defects (exact file:line → command → smallest safe fix)

1. **`SCORECARD.md:18`** — command `python3 tools/round41-scorecard-reconcile.py --repo . --tip 3a09a1d…` shows run_bad=1. Fix: update the row to `33` and its "latest outside closure" pointer to `corpus/lessons/round-46-verifier-spotcheck.md` (append a correction line in the SCORECARD round-47 section rather than rewriting history; the fact row is re-derived in place for this class since round 42 — see contract row for SCORECARD head re-anchor).
2. **`tools/sources-append-only.py`** (ROWLIKE handling, `:50-60` and parse loop) — command #9 exits 2 on any FROM ≥ round-45. Fix: scope the row-like-outside-registry refusal to the parsed `## Registry` section: only treat `| S0NN |` lines as a hard parse error when they appear inside the section; lines structurally identical but outside (re-verification tables, lessons) should be ignored, not poison the whole run. This preserves the guard's "no hidden row" property inside the registry while letting the file's non-registry tables exist. (Counter/guard are frozen — this fix belongs to a *future* round; none of this round's counters depend on it.)
3. **`tests/llamacpp-live/check-receipt.py`** (`:31-33`, required-check lists) — command: `python3 tests/llamacpp-live/check-receipt.py <round-47 receipt>` → INVALID exit 1. Fix: teach the gate the v4 shape (provenance block presence + `teardown.log_path` null-or-committed-relative, current check-id set) or document that v4 receipts are validated only by `tools/kama-live-replay.py` and `tools/round47-live-replay-audit.py`; update SKILL/README/knowledge v3 statements to v4 in the same commit (append-only supersession lines).
4. **`tools/gguf-identity.py:44,476-478`** — v3-strict; same treatment: accept v4 (read `provenance.model.sha256`/server sha256) or document the v3-only boundary.
5. **hexrun ledger** — `corpus/lessons/round-46-verifier-spotcheck.md:23` cites a fleet commit not in the lane; census `unknown=22`. Fix (future): add a ledger class/row for fleet-report commit IDs (family includes `b0fd7b7f…`) or drop them from the unknown count with an annotating row, so the count stops drifting by one each round.

Proposed patch texts are in `proposed-fixes.md` (same dir); none applied (read-only lane).

## 4. Deliverables
- `cmd-outputs.log` — verbatim transcript of all 11 commands with exit codes.
- `receipt-1.json`, `receipt-2.json`, `receipt-3.json`, `install.txt` — copies of the cited round-47 C2 live evidence.
- `proposed-fixes.md` — diff-style proposals for §3.
