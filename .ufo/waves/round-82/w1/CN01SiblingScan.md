# CN01 — sibling-overlap scan (round 82, kama) — connector, read-only

Lane tip via `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master`; no lane write, no sibling write. Commands + exits: `.ufo/waves/round-82/w1/CN01SiblingScan/receipts.txt`.

## 1. Append-only acceptance/register family binding a row's introducing commit — no sibling holds it
Sweep: `grep -rn 'blame\|introduction\|append-only-late' <lane>/tools <lane>/registry <lane>/corpus/knowledge` over all 20 siblings; `ls -d *-shokunin/registry` → `kama-shokunin/registry` only (exit 0). corpus/knowledge returns only prose "introduction" words; no instrument code. Mechanism hits, each read:
- `kaidoku-shokunin/tools/round-38/registry-immutable.sh:3-5` (`SKILL.md:1713`) — append-only register family; rule is row cell-immutability from BASE to REV, no commit resolution.
- `kaidoku-shokunin/tools/round-55/corrections-pin.py:2-17` (`SKILL.md:1844`) — append-only TSV ledger family; BASE/REV byte-prefix and row order, no commit resolution.
- `kotodama-shokunin/tools/check-supersession-settlement.py:4-8` — append-only supersession chain; binds chain state, no commit.
- `chousa-shokunin/tools/claims-audit.py:33-36` = `claims-audit-v2.py:46-49` (`SKILL.md:155-156`) — `git-first-commit`: a PATH's first-add commit (`git log --diff-filter=A`) earlier than the claims file's first-add; path-scoped ancestry, not a row, no blame.
- `kaidoku-shokunin/.ufo/waves/round-20/tools/evidence-timestamps.py:2,8` (`SKILL.md:1004`) — `git blame --porcelain` bound to a LINE's introducing committer time (nearest same technique, different subject).
- `grep -rn 'append-only-late\|APPEND_DEBT'` outside kama → 14 hits, all `./MANIFEST.json` and `./.ufo/reports/round-81/kama.md` (kama's own report): no sibling register.
Verdict: no absorption. Kama's repair is in-province as scoped (`registry/append-only-late.tsv` + `tools/round81-append-debt.py:33-40` disclosure); it would be sibling-scope absorption only if recorded as the blame-introduction technique itself, which is kaidoku's line-level ground (§3).

## 2. llama.cpp README @ `b12103` / pin-watch relation register — `b12103` unique, register class is not
- `grep -rIn 'b12103' *-shokunin` (non-kama) → 1 hit: `kengaku-shokunin/.ufo/waves/round-48/w1/R48C2MutPins.md:54`, `b12103` inside sha256 `7d6aaa2b…b121034c…` — not a citation. No sibling cites `tools/server/README.md` at `b12103`.
- `grep -rIn 'engine-pin' *-shokunin` (non-kama) → 1 prose hit: `game-dev-2d-shokunin/reports/round-101/r101-D1.md:264` "engine-pinned". The name and the register are kama-only.
- Same document, older tag: `kengaku-shokunin/corpus/SOURCES.md:193` (S178) cites `tools/server/README.md` at tag `b7200`. Kama's `b12103` recency ground is unique; the document is not.
- Same register class: `kagi-shokunin/corpus/release-clocks.tsv:1` (30 rows; 3 fired / 17 not-fired / 10 quote-located) + `kagi-shokunin/corpus/release-clock.py` (`SKILL.md:48`, `:787`) — `anchored_version` vs `observed_version`, the same newer-release-trigger family; `tsukuroi-shokunin/corpus/knowledge/linux-v73-pinwatch-r68.md:1-63` (RW1–RW6, `recheck: on-release`) is a third, unregistered instance.
Verdict: `registry/engine-pin-relations.tsv:1` (`relation/newer/newest`; llama.cpp `b11755` behind 278 `b12103`) is the fleet's only engine relation register, but the pin-watch register capability is already kagi's. The round may claim the engine ground, not the capability.

## 3. `git blame`-based introduction resolution (technique) — kaidoku holds it; no PROVINCE claims it
- `grep -nI 'blame' */PROVINCE.md` → exit 1: no sibling PROVINCE.md mentions blame.
- Registered: `kaidoku-shokunin/SKILL.md:1004` (`evidence-timestamps`) and `kaidoku-shokunin/SKILL.md:1508` (`Hash-bound legacy deadline allowances`; `tools/round-33/timestamps/allowances-hashed.json:14,25,36,47,58` carries per-line `introduced_by`, consumed by `run-gate-hashed.py:34`).
- Records only: `tsukuroi-shokunin/SCORECARD.md:1215`; `tsukuroi-shokunin/corpus/knowledge/adjacency-anchors-r19.json:158,1810` (blame resolves a row's position at a past rev — movement, not introduction); `kake-shokunin/.ufo/waves/round-24/w1/PathsDriftT03KimiSurfaceMjs.md:13` (line added in `9639ec7`); `chousa-shokunin/.ufo/waves/round-25/falsify/FxLedgerR19.md:7`; `game-dev-3d-shokunin/reports/round-106/stale-scan.md:95,108`.
- PROVINCE adjacency: no sibling PROVINCE.md names blame introduction-resolution → kama's province statement is uncontested at PROVINCE level.
- Contested scope: the blame→introducing-commit technique is kaidoku's registered ground; kama holds it only as an internal repair of `round81-append-debt.py`, never as a capability row or general introduction-resolution instrument.
