# S1Gate — round-48 Gate decisions, lane kama

Verdict: C1 (calibration 7→7) and C2 (operability 8→8) are **met at the build tip `380bcdff9c8af06997c482f6eb03db926a794a2b` on my own independent run** (both counters `met=True`, `exit=0`), with fifteen gate decisions drafted — eight grounded rejects — and the round held open only for the final-tip re-measurement; no lane file touched, no defect found in either claim.

## What I ran (mine, not the L1 dry run)

Own `git clone --shared` of the lane ($S/lane, HEAD `b85783e8`, toplevel = clone), own scratch `/fast/scratch/hyaku/kama-r48/S1Gate`, removed at seat end.

| # | Command | Exit | Output (first line) |
|---|---|---|---|
| 1 | `python3 tools/round48-append-audit-v3-check.py --repo $S/lane --tip 380bcdff… --scratch $S/c1run --out $S/c1.json` | 0 | `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True` |
| 2 | `python3 tools/round48-live-replay-v5-audit.py --repo $S/lane --tip 380bcdff… --scratch $S/c2run --out $S/c2.json` | 0 | `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True` |
| 3 | `python3 $S/lane/tools/append-only-audit.py --repo $S/lane --to 380bcdff… --json` | 0 | `schema append-only-audit/v3`, `events 5, restored 5, partial 0, unrestored 0, ungraded_lines 89, regressed 0, vanished 0, bad_declarations 0` |
| 4 | `python3 $S/lane/tools/kama-live-replay.py --compare R48/receipt-1.json R48/receipt-2.json` | 0 | `compare match=True mismatches=0` |
| 5 | `… --compare R48/receipt-1.json R47/receipt-1.json` | 1 | `compare match=False mismatches=3` (schema + props alias + models ids) |
| 6 | `… --compare R47/receipt-1.json R47/receipt-2.json` | 0 | `compare match=True mismatches=0` |

Probes against the pinned HF revision (all first-hand, 2026-10-26 ~22:34–22:36 UTC): HEAD of the pinned URL (`x-repo-commit: 499bc882…`, `x-linked-etag: "270cba1b…"`, `x-xet-hash: 7cfbf69e…`, 302 with `cache-control: no-store`), same for `main`, `499bc88` (7-hex) and commits `e2d5caf5` / `96f460f9` / `22027b1a`; download of the pinned URL (1,185,376 bytes → sha256 `270cba1b…`); CDN 200 HEAD (`etag: "7cfbf69e…"`); two signed locations one second apart (`Signature` differs, `Expires` = fetch + 3600 s); `api/models/…/commits/main`, `…/tree/<rev>/tinyllamas` for four revisions. No service was started by me; the only `llama-server` was the C2 counter's own replay, which tore it down.

## Gate decisions (drafted; full text in `w1/out/S1Gate/gate.md`)

| # | Decision | Subject |
|---|---|---|
| D1 | ACCEPT | the calibration verdict is the v3 tool's exit at the tip, scored by the frozen counter |
| D2 | **REJECT** | the pre-build base state as calibration evidence (all-zero floor, v3 contract absent) |
| D3 | **REJECT** | a relabelled v2 tool or the v3 contract without the SCORECARD row (controls `junk-c1-*`) |
| D4 | ACCEPT (provisional) | C1 met at `380bcdff`; calibration stays 7 |
| D5 | ACCEPT (provisional) | C2 met at `380bcdff`; operability stays 8 |
| D6 | **REJECT** | `x-linked-etag` as proof of the revision — it is the LFS object digest |
| D7 | **REJECT** | the CDN redirect Location as a locator — signed, 1 h expiry, `Signature` per fetch |
| D8 | **REJECT** | the CDN 200 `etag` / `x-xet-hash` as the artifact digest |
| D9 | **REJECT** | S490's `main` resolve URL as the replay locator — the ref moved four times in 2 h 36 min |
| D10 | **REJECT** | a 7-hex prefix or any ref as the pin — HF resolves it, the contract does not allow it |
| D11 | **REJECT** | the receipts leg alone / a fabricated `verified` block (control `junk-c2-r47-relabel`: `receipts=1`, everything else 0) |
| D12 | ACCEPT | sha256 of re-acquired bytes + record-time `verified` re-checked against declared digests |
| D13 | ACCEPT | the 89 ungraded lines are the bound, conditional carve-out (17 + 72, both SCORECARD head) |
| D14 | OPEN | final-tip re-measurement (prereg routed r47-D9); lane HEAD `b85783e8` ≠ build tip |
| D15 | ACCEPT as known limits | the three integration items (unregistered counters, 33 vs 34, `d0012618`) |

Grounding for the two headline rejects:

- **`x-linked-etag` is not a revision.** Three different commits (`499bc882`, `e2d5caf5`, `96f460f9`) return `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"`, and that value equals `sha256` of the downloaded bytes: it is content identity. The commit is named by `x-repo-commit` on the same response.
- **The CDN URL is not a locator.** `Expires` tracked fetch time exactly (1793057674 → 2026-10-26T23:34:34Z at 22:34:34; 1793057702 at 22:35:02; 1793057735 at 22:35:35), and two fetches one second apart produced different `Signature` values for the same object; the 302 says `cache-control: no-store`.
- **`main` is not a locator.** `main` now equals the pin, which is exactly the coincidence that makes it unsafe: it moved four times on 2025-10-28 (08:07, 08:55, 09:18, 10:43) and content at that path changed under it (`stories15M-q4_0.gguf` lfs oid `696f4aeb…` at `e2d5caf5` vs `66967fbe…` at `499bc882`). The round-47 receipt-1 still names `…/resolve/main/…` with `verified: null`.

## Findings

- **F1 (low, source-row precision).** `corpus/SOURCES.md:51` (S039) says the path "held three different byte strings on 2025-10-28". Three exist *across history* (`047bf464…` through 2025-09-26, `68c694e7…` at 22027b1a, `270cba1b…` from 96f460f9), but only two are 2025-10-28 revisions. Proposed cell text is in `gate.md` §F1 (lane not edited). Not a defect against either claim; the row's conclusion is strengthened by the exact oids.
- **F2 (gate-level, no lane change).** HF resolves a 7-hex prefix and `main` to the same object today, so "the locator fetches" is never gate evidence; the 40-hex rule is a lane-tool contract (`tools/kama-llamacpp-live.py:71,1477`, selftest `:1300-1302`).
- **F3 (accepted limit).** The stable projection includes the served model alias/ids, so `--compare` across rounds fails by design (run 5 above); only same-round receipts are valid compare controls.
- **F4 (note).** Both counters' `--out` receipt is the one-paragraph summary text, not JSON (`--json` belongs to `tools/append-only-audit.py`); parsing it as JSON fails.

## Touched surfaces

- Written (my seat only): `.ufo/waves/round-48/w1/out/S1Gate/` (`gate.md`, `probes.txt`, `c1.json`, `c2.json`, `c1tool.json`, `loc1.txt`, `loc2.txt`) and this report.
- Read-only: lane tree (clone), counters, controls, receipts, `registry/append-only-contract.tsv`, `corpus/SOURCES.md`, `SCORECARD.md`, lane tools; fleet repo (verified clean: `git status --porcelain` empty).
- No lane file edited, no git/jj mutation in the lane, no fixture commits, no pacman, no tool installs or upgrades, no subagents, no `agent://all`.
- Scratch `/fast/scratch/hyaku/kama-r48/S1Gate` removed.

## Out of scope (not done, not claimed)

- Final-tip measurement (D14) — the L1 must re-run both counters at the closed tip and commit those receipts.
- `gate-registry-check`, the round-41/42/43 counters, `hexrun-census` — the three known integration items, accepted as known limits per the seat brief and not re-investigated.
- Byte-exactness of the appended r45/r46 banners against the pre-rewrite heads — the build's claim; the counter summary does not show it and I did not verify it.

## Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Gate/gate.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Gate/probes.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Gate/c1.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Gate/c2.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Gate/c1tool.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Gate/loc1.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Gate/loc2.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Gate.md`
