# K1Contract — round 48 design critic: is the v3 append-only contract the lane's true machine-readable self-description?

**Verdict:** The contract is a true machine-readable form for 9 of the lane's live append-only declarations, but two live declarations have no row — `corpus/knowledge/error-is-not-a-verdict.md:173` (self-declared, row-able today) and `corpus/knowledge/context-capacity.md:245` (declared only in prose at `corpus/README.md:817-818`, and **unrepresentable under frozen v3** because the declaration is spread over two lines) — and adding the context-capacity row changes the audit's events (adds `c0a9b029c035`, 47 deleted, all ungraded) while leaving the verdict green; adding it whole-file turns the verdict red.

Seat: K1Contract (leaf). All runs used a `git clone --shared` at `$S/lane` (`$S=/fast/scratch/hyaku/kama-r48/K1Contract`; `git -C $S/lane rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r48/K1Contract/lane`), tip `380bcdff9c8af06997c482f6eb03db926a794a2b` (the round-48 build). No installs (no pacman, uv, npm); only `python3` + read-only `git` used.

## Method

1. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -i -E 'append[- ]only' 380bcdff9c8af06997c482f6eb03db926a794a2b` → 5,430 matched lines; live (non-`.ufo/`, non-`tools/` docstring) hits enumerated per file (evidence: `out/K1Contract/evidence-summary.txt`; counts in scratch grep listing).
2. Read the v3 tool/contract semantics (`tools/append-only-audit.py` at tip, `binds()`/`declaration()` lines 190-228; counter `round48-append-audit-v3-check.py` lines 24-65).
3. Ran the frozen C1 counter on the scratch clone (baseline) and the v3 tool with scratch contracts (baseline + each candidate row / hazard variants).
4. Verified the only representable fix for the context-capacity case end-to-end on a scratch fixture commit (branch `k1contract-verify-fix`, commit `a4ab3a71b5d6493e9b74884d8f56a9aabc93be78` = 380bcdff + one appended declaration line).

## Evidence

Baseline (frozen counter C1, own clone):

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round48-append-audit-v3-check.py --repo $S/lane --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S
selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True
tip=380bcdff9c8af06997c482f6eb03db926a794a2b
$ echo $? → 0
(receipt: out/K1Contract/c1-receipt.txt)
```

Tool runs (v3 schema, `--contract <scratch>`; full JSON in `out/K1Contract/vN.json`; summaries in `evidence-summary.txt`):

| variant | contract | exit | files | events | new knowledge events | ungraded_lines | bad_decl |
|---|---|---|---|---|---|---|---|
| v0 | 9-row contract as at tip | 0 | 89 | 5 | — | 89 | 0 |
| v1 | + `context-capacity.md` row (`only=## Errata@corpus/README.md:817`) | 1 | 90 | 6 | `c0a9b029c035` deleted 47, graded 0, ungraded 47, status ungraded | 136 | 1 (pointer unbound) |
| v2 | + `error-is-not-a-verdict.md` row (`only=## Round24@error-is-not-a-verdict.md:173`) | 0 | 90 | 5 | none | 89 | 0 |
| v3 | both v1+v2 rows | 1 | 91 | 6 | `c0a9b029c035` as v1 | 136 | 1 (same unbound pointer) |
| v4 | + `error-is-not-a-verdict.md` row, region `*` (hazard) | 0 | 90 | 5 | none | 89 | 0 |
| v5 | whole-file `*` rows for the three knowledge files with history events | 1 | 92 | 8 | `726f737a942f` 21, `c0a9b029c035` 47, `d183ec572a5e` 29 — all graded, unrestored | 89 | 2 (the two non-declared files cannot bind) |
| v6 | v1 row re-pointed at the proposed appended declaration line (context-capacity.md:246), on fixture commit a4ab3a71 | 0 | 90 | 6 | `c0a9b029c035` deleted 47, graded 0, ungraded 47, status ungraded | 136 | 0 |

## Missing declarations (KQ71 duty: every lane `.md` outside `.ufo/` that calls a file append-only with no row)

| file:line | what it says | contract row? | disposition |
|---|---|---|---|
| `corpus/knowledge/error-is-not-a-verdict.md:173` | `Append-only; the round24 sections above stand and nothing here repeats them.` (inside `### Round24 refusal semantics`, under `## Round24 — isolation is not evidence availability` at :82) | no | **Add row** `A-corr`, declared_at `error-is-not-a-verdict.md:173`, region `only=## Round24@error-is-not-a-verdict.md:173`. Binds today (v2: `bad_declarations=0`, exit 0). Adds no event at 380bcdff. |
| `corpus/knowledge/context-capacity.md:245` (`## Errata — round 26`) | called append-only at `corpus/README.md:817-818` ("carries the same semantics without the word … the round-25 wording above stays") | no | **Add row** `A-corr`, declared_at `context-capacity.md:246` (new, after the proposed appended line), region `only=## Errata@context-capacity.md:246`. Requires first appending one self-declaring line inside the Errata section (proposed diff: `out/K1Contract/proposed-context-capacity-declaration.diff`). Verified bound + green in v6. |
| `corpus/knowledge/served-identity-crosswalk.md:94` | "… here because registry cells are append-only" (about `corpus/SOURCES.md` cells) | SOURCES row covers it | prose only (target covered) |
| `corpus/knowledge/snapshot-history.md:29` | declares `registry/history/DELTA.md` append-only | DELTA row covers it | prose only (target covered) |
| `corpus/knowledge/instrument-run-agreement.md:20` | cites `tools/sources-append-only.py` | tool, not a lane file | prose only |
| `corpus/README.md:759-761` | "sets the five files the lane treats as append-only (…)" | all five named files have rows | prose only; **stale** wording (contract now has 9 rows/89 files), flagged by round-47 S9Quality F1; A-corr fix is an appended correction, not a rewrite |
| `SKILL.md:1434` | heading "Round-46 instrument registry (freshness re-verification, append-only calibration)" | — | prose only (topic label; round-47 S9Quality F3) |
| `registry/hexrun-ledger.tsv:74`, `registry/verdict-ledger.tsv:141,144,162,165`, `registry/claim-outcome-ledger.tsv:70,94`, `registry/release-recheck-b11889.tsv:11,30`, `registry/release-recheck-b11906.tsv:11,30`, `registry/staged-refusals.tsv:56,58,61,68-74` | quoted/o "corrected append-only", "append-only records", or aspirational "adopt … append-only" | no | prose only (describes past edits or future adoption; none is a present declaration for that file) |
| `registry/history/DELTA.md:3`, `registry/report-landing-errata.tsv:1`, `corpus/knowledge/consumer-registry.md:30` | self-declarations | covered (rows 7,8,9) | covered |
| `LOG.md`, `SCORECARD.md`, `corpus/QUALITY.md`, `corpus/SOURCES.md`, `corpus/lessons/*.md`, `README.md:16` | prose/declarations | covered (rows 1-6) | covered |

Registry ledgers (23 files under `registry/`) with no `append[- ]only` mention at all — `registry/append-only-contract.tsv` header aside — need no rows: `chat-param-outcomes-r31.json`, `claim-outcome-ledger.tsv`, `digest-ledger.tsv`, `endpoint-consumers.tsv`, `engine-pins.tsv`, `error-injection-cells.json`, `error-injection-fixtures/*`, `error-signatures-r26.json`, `hexrun-ledger.tsv`, `history/latest.tsv`, `recheck-r45.tsv`, `release-recheck-b11889.tsv`, `release-recheck-b11906.tsv`, `request-field-outcomes-r28.json`, `required-citations.json`, `staged-refusals.tsv`, `verdict-ledger.tsv`.

Knowledge files with mass-deletion history but **no declaration** (must NOT get rows): `corpus/knowledge/llamacpp-loading-lifecycle.md` (`726f737a942f`, 21 deleted), `corpus/knowledge/echo-discriminating-counters.md` (`d183ec572a5e`, 29 deleted) — v5 shows whole-file rows for them would bind-fail and add graded unrestored events (exit 1). Round-46/47 seats (Rev2Decl/contract.md:79, K1Design.md:49) noted the same three events; the round-47 S9Quality KQ71 row and `corpus/README.md:895-898` ("a lane file declared append-only but missing from the contract is not detected") document the class.

## Defects

1. **Unrepresentable declaration (blocker for context-capacity row).** `corpus/README.md:817-818` is the only place the lane calls `corpus/knowledge/context-capacity.md:245`'s Errata append-only, and the declaration is spread over two lines: :817 carries `append-only` and the token `context-capacity`; :818 carries the literal title `## Errata — round 26`. The v3 binding rule (`tools/append-only-audit.py:226`) requires one line to contain all three, so any row pointing at :817 fails:
   ```
   $ python3 tools/append-only-audit.py --repo <clone> --to 380bcdff… --contract <base+context-capacity row> --json
   → {… "declarations": [{"path": "corpus/knowledge/context-capacity.md", …, "ok": false,
       "reason": "only pointer corpus/README.md:817 does not declare '## Errata' append-only"}]} exit 1
   ```
   Fix (append-only-safe, both files are `A-corr`): append one self-declaring line at the top of the Errata section — `Append-only; this Errata section's rows keep their round-26 text.` (`out/K1Contract/proposed-context-capacity-declaration.diff`) — then add the row in the proposed contract. Verified: v6 (fixture commit `a4ab3a71`, row pointer `context-capacity.md:246`) → `bad_declarations=0`, exit 0.
2. **Missing row for a live self-declaration.** `corpus/knowledge/error-is-not-a-verdict.md:173` declares its refusal-semantics block append-only and has no row (v0 `files` = 89 does not include it). Fix: add the v2 row (binds today; adds no event at 380bcdff).

## Which additions change the audit's events at 380bcdff

- `error-is-not-a-verdict.md` row (v2): `files` 89→90, events unchanged (5), `ungraded_lines` 89, exit 0. No event change.
- `context-capacity.md` row, properly bound (v6, at the fixture tip — event set identical for 380bcdff once bound): `files` 89→90, events 5→6, **new event `c0a9b029c035` (deleted 47, graded 0, ungraded 47, status ungraded, held_at_to 0)**, `ungraded_lines` 89→136, exit stays 0. The event is ungraded because the 47 deleted lines are body edits outside the Errata region — an honest non-verdict signal.
- Whole-file `*` rows for any knowledge file (v4/v5): they grade those body edits → `c0a9b029c035` becomes graded 47 unrestored, `726f737a942f` 21 unrestored, `d183ec572a5e` 29 unrestored → exit 1. This is why the region (`only=## Errata` / `only=## Round24`) is the only correct shape, and why non-declared files must not be added.

## Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K1Contract.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K1Contract/proposed-contract-additions.tsv` (11-row contract: the 9 frozen rows + the two proposed rows)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K1Contract/proposed-context-capacity-declaration.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K1Contract/c1-receipt.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K1Contract/contract-at-380bcdff.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K1Contract/{v0,v1,v2,v3,v4,v5,v6}.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K1Contract/evidence-summary.txt`
