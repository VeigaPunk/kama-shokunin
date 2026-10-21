VERDICT: confirm - the live v3 receipt (install_links) is accepted by every committed v3 receipt consumer at HEAD a6617149; no added server key breaks a strict-key consumer; links are enforced only when a consumer asks (gate flag or pin), and gguf-identity does not evaluate links.
Attacked: `.ufo/waves/round-21/runs/b76727f3/live-receipt.json` (28206 B, sha256 e1fc04ab95b3…, schema kama-llamacpp-live/v3, outcome pass) against committed readers: tests/llamacpp-live/check-receipt.py (blob 6b876437…), tools/gguf-identity.py (blob 195f71e7…, same at 7a6bc911), install-tree-grid.py, controls.py, round-20 FreshnessS039/freshness_check.py and c2/measure.py, round-21 RevengeInstallTreeIntent/receipt_scan.py. tools/ and tests/ are unchanged between measured b76727f3 and HEAD a6617149 (git diff --stat empty).
Pre-round-21 gate = `git show 7a6bc911:tests/llamacpp-live/check-receipt.py` (blob a0dc1d07…).
Pins (receipt = HEAD = disk, all verified): tool e4cc6d88 (HEAD producer), probe 36b64978, server b6a31a8e, impl e404b91a, tree 6c216313 (51 members), links 5cb9f486 (10 links recomputed and equal on disk), no duplicate JSON keys.

## Exits (executed; argv/stdout/stderr/exit in out/runs/, table out/commands.tsv)
ID | command (LIVE = live-receipt.json) | exit | observed
T1/T2 | gguf-identity.py STORIES --receipt LIVE --json (target; lane and HEAD clone) | 0 | engine-agreement, 3/3 comparisons agree
T3 | gguf-identity on 6 R18 v3 receipts | 0 x6 | engine-agreement
T4 | gguf-identity on round-16 v1 and round-17 v2 receipts | 2 x2 | receipt_schema_unsupported (pre-existing)
G1 | check-receipt LIVE, official pins (--require-schema v3 --require-install-links, model/tree/links) | 0 | VALID
G2 | G1 plus server, impl, probe, tool pins | 0 | VALID
G3 | check-receipt LIVE, no pins | 0 | VALID
G4 | LIVE with --expect-install-links-sha256 0x64 | 1 | INVALID: links sha mismatch
G5 | check-receipt on 6 R18 v3, no flags | 0 x6 | VALID
G6 | same with --require-install-links | 1 x6 | INVALID: block absent
F1/F2 | pre-round-21 gate, LIVE with full pins (no links flags) / no pins | 0 / 0 | VALID
F3 | pre-round-21 gate, R18 receipt-1 | 0 | VALID
N1 | install-tree-grid LIVE --tree-sha 6c216313 | 0 | baseline VALID, rejected 3/3
N2 | install-tree-grid LIVE, no tree pin | 1 | rejected 0/3 (as recipe C08)
C2/C3 | freshness_check.py --receipt LIVE / default R18 | 0 / 0 | 7 receipt + 2 archive checks match each
C1 | controls.py --selftest (synthetic only) | 0 | 70 cases, 0 failures
C4/C5 | round-20 c2/measure.py default / --receipt LIVE | 0 / 1 | C5 mismatch: pinned reference is R18 (alias kama-r18-live vs kama-r21-live), by design
C6 | round-21 receipt_scan.py | 0 | 12 live receipts, 51 members, pin 6c216313; only LIVE has install_links
G7/F4/N3 | selftests: gate HEAD (11 VALID+1 NE, 91 mut) / pre-r21 gate (6+1, 77 mut) / tree grid | 0 / 0 / 0 | pass
W1-W3 | uncommitted lane gate copy (blob b26dd0bf…): official pins / plain / selftest | 0 / 0 / 0 | VALID; selftest 12 VALID (committed 11)

## Mutants (base LIVE; fixtures in out/fixtures/; exit per consumer)
mutant | gate | gate+links pin | pre-r21 gate | gguf-identity
m1 unknown server key; m2 unknown top-level key | 0 | 0 | 0 | 0
m3 install_links_sha256 dropped | 1 | 1 | 0 | 0
m4 dangling soname, digest recomputed | 1 | 1 | 0 | 0
m5 install_links block removed | 0 | 1 | 0 | 0
m6 install_links is a string | 1 | 1 | 0 | 0
m7 libllama.so retargeted to .0.7.0, digest recomputed | 0 | 1 | 0 | 0
m8 install_links_sha256 = "zz" | 1 | 1 | 0 | 0
m9 extra link to a member, digest recomputed | 0 | 1 | not run | not run
m11 link named LICENSE (tree member) | 1 | not run | not run | 0

## Answers
1. Accepted: yes by every consumer above. Nonzero exits are the expected ones: legacy with --require-install-links (G6), tree grid without tree pin (N2), measure pinned to R18 (C5).
2. Strict-key break: none. No committed reader compares the receipt or `server` against a fixed key set (grep for keys(), sorted(, set(, frozenset, additionalProperties, jsonschema; no receipt schema file in lane). Exact-set comparisons touch only checks[] (check-receipt "unexpected check id"; controls.py:1007) and gguf reconcile output (round-20 measure-final same_json_value). Grep-based, not AST [INFERENCE for unseen readers].
3. Scope limits, not breaks:
 a. Links are opt-in. Without --require-install-links or a links pin the gate accepts m5, m7, m9. SKILL.md:684 states this; the official recipe pins; the tree grid does not (its mutants never touch links).
 b. gguf-identity --receipt exits 0 on every links mutant, including m4 and m11 that the gate rejects. It reconciles model identity only; it is not a link acceptance check.
 c. check-receipt.py:4, identical at 7a6bc911:4: "Bound to the exact receipt keys emitted by ``tools/kama-llamacpp-live.py``." False as implemented (m1, m2, m9 pass). Pre-existing. corpus/lessons/round-16.md M2 "gate rebound to the producer's exact keys" means matching spellings, not rejecting extras. Fix the docstring or add an exact-key check; not done (lane read-only).
 d. Tool pins are per producer version: R18 receipts carry tool 83eac5c0 (pre-r21 producer). Pinning the current tool rejects them (exit 1); with their own pin the pre-r21 gate accepts (exit 0).

## Environment (not mine)
- Lane working tree changed during the session. Now: M SCORECARD.md, M tests/llamacpp-live/check-receipt.py (+8), M tools/kama-llamacpp-live.py (+3), M tools/report-landing-audit.py, ?? build/completion-summary.json, build/verdict-count.json, build/wave-accounting.py. Before my runs git status was empty for tools/, tests/ and runs/b76727f3. I wrote none of these. Consumers ran at committed HEAD via scratch clone; W1-W3 cover the uncommitted gate. run.py:26-27 clean-tree guard will refuse until resolved [INFERENCE].
- __pycache__ dirs in lane predate my first run (03:33-08:07 vs 08:23); not mine.
- Installs/updates: none. Tools: /usr/bin/python3 stdlib, read-only git.
- Read-only git in the lane (status, diff --stat, log, rev-parse, cat-file, show): git may refresh the index stat cache; no content or ref change. No jj commands run.
- No server, daemon or producer launch. controls.py only --selftest. Round-18 runner not run (launches llama-server). install-links-grid.py is not a receipt reader; not rerun (official exit 0 at b76727f3).
- Scratch /tmp/kama-r21-C2GgufReceiptCompat removed after saving fixtures.
Out dir: .ufo/waves/round-21/falsify/out/C2GgufReceiptCompat/ (runs/, commands.tsv 82 rows, fixtures/ 10 receipts <= 28.3 KB).
