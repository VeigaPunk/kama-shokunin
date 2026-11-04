# EX02LateRows — operability receipt
- Axes: exact population, byte-faithful cells, end-to-end acceptance, write-scope safety.
- Delivered 20 headerless LF TSV rows for 8 events; appended SHA256 `a4dd677235f1aa8c5dd6d9147a8f489c48185e3fbacf1e24bc7f23e203de5e07`.
- Window: after `aaf974dbd3b6adb2ef914dc7293cda92b4e05551`, through `30d8eac394a8714fad3dc792b74a45a25b4366a2`.
- Clone started at the base; plan absent there. Added byte-identical plan blob from `743c106065363be0cebd1036e6c33d7e6ae632dc` in clone commit `b337e626d42f952d936ad00c464728b04a81f331`.
- Plan SHA256: `be70da57cb21719d41e925701fde2f069219ea9c654ff789a4f4c595aac4fd7c`.
- Frozen audit exit 1 (findings expected); selected exactly the specified eight unrestored events, 20 lines.
- Unrestricted generator emitted 123 rows; window rows match its 20-row subset byte-for-byte. No cells hand-written.
- Generator command (exit 0): `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round81-late-rows.py --repo /fast/scratch/hyaku/kama-r83/EX02LateRows/clone --round 83 --base 30d8eac394a8714fad3dc792b74a45a25b4366a2 --audit-json /fast/scratch/hyaku/kama-r83/EX02LateRows/audit-window.json --write --out /fast/scratch/hyaku/kama-r83/EX02LateRows/late82-generated.tsv`.
- Header removed mechanically; all counts 1, all classes `in-place-edit`; 19 SCORECARD rows and one lesson row.
- Register append: 104→124 lines. Clone proof commit: `84c2f7291720f64b52828200b574bdd05501e4f9`.
- Debt command (exit 0): `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round81-append-debt.py --repo /fast/scratch/hyaku/kama-r83/EX02LateRows/clone --round 83`.
```
APPEND_DEBT round=83 base=30d8eac394a8 events=76 accepted=53 late=23 pending=0 unaccepted=0 bad_rows=0 bad_declarations=0 out_of_population=0
```
- Frozen target `late=35` NOT met: source lines 275–290 store `(commit,file)` event keys and count events, not rows; 15+8=23. All eight events accepted; no row changes made to force a number.
- The lane's debt-tool worktree was modified during the wave; the mandated command exercised that worktree path. No claim that its bytes were revision-pinned.
- Receipts (absolute paths, command/exit metadata inside): `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/EX02LateRows/generator.receipt.json` (audit/generator exits 1/0/0), `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/EX02LateRows/debt.receipt.json` (debt exit 0).
- Retained audit input: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/EX02LateRows/audit-window.json`; complete full-generator output: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/EX02LateRows/generator-all.tsv`.
- Production files unchanged by this seat. No installs, builds, linters, or unrelated tests. LSP unavailable in mounted tools; no symbol refactor needed.
- Risk/blocker: frozen target mixes row count with event count; L1 must disposition the target discrepancy without altering frozen text.
- Report trailer conflicted with hard seat-only scope; report retained here, not at sibling-level `w1/EX02LateRows.md`.
- Scratch removed before terminal handoff.
- Self-evaluation: accuracy 4 (worktree tool not pinned), completeness 4 (target discrepancy explicitly retained), clarity 4 (population filtering documented), actionability 5 (ready-to-append bytes), conciseness 4 (provenance needed); overall 4.2. Improvement: L1's post-integration gate should bind the final tool revision. User-agreement check: evidence distinguishes acceptance from frozen-target failure.
