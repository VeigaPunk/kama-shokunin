# Round 25 attempt 1 build wave: disposition (written by the attempt-2 author)

Attempt 1 dispatched this 34-seat build wave at 08:23:56Z on 2026-10-22. The
orchestrator stood attempt 1 down at 08:30Z for capacity (background job
limit), not for a fault. Four seats had written their advice reports; the
other 30 were cancelled mid-run. Attempt 2 does not resume any attempt-1
identity.

Everything in this folder is committed as the attempt-1 record, byte for
byte as found at 09:20Z. None of it is attempt-2 claim evidence.

| Item | State found | Attempt-2 use |
|---|---|---|
| `spec.json`, `dispatch.json`, `dispatch-attempts.json`, `assignments.json`, `spawn-result.json`, `advice/swarm-registry.json` | validated 34-seat spec and its dispatch record | record only |
| `advice/CriticC2Sizing.md` | complete report | design input: strict counting rule (amendment 1), fixture scope limits |
| `advice/CriticLearningBar.md` | complete report | design input: cells X1-X3 and L1-L3, supersession target (amendment 2) |
| `advice/SrcServerSlotsAuto.md` | complete report | design input only; its source rows are re-opened by an attempt-2 seat before any row is written |
| `advice/ExecPromisorAnchorCount.md` | complete report | design input only (promisor instrument is outside C1's counted set) |
| `out/*` (19 folders, 5 empty) | partial outputs of cancelled seats; a seat may have stopped mid-write | unverified; not claim evidence. `out/ExecCapacityTool/kama-context-capacity.py` is offered to the attempt-2 tool executor as a starting point that must be re-verified; `out/RevengerM11/` showed an M11 re-anchor killed by grid row F20, re-checked by the attempt-2 full mutant run |

Not blind: the attempt-2 author read the attempt-1 K1-K8 receipt rows in
`out/ExecCapacityTool/context-capacity-receipt.json` and the first 400
characters of each `out/ExecEdgeCells/raw/summary.json` row before writing
`../preregistration-amendment-2.json`; that amendment says so.
