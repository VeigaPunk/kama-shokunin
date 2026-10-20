VERDICT: partial — kumitate owns swarm-wave dispatch; the refused/spawned tally is kama's ledger

Axes this seat used: calibration (lowest, 7) and operability (8). One move: keep the refused-count repair in kama C2, and send kumitate L1 a shape note rather than the script.

## Ownership

Kumitate's province is orchestration tooling. `kumitate-shokunin/SKILL.md:3-6` says it "scopes OMP task/hub dispatch, ufo-fsd scripts, crates/ufo-core-runtime." The swarm producer it documents is `ufo-swarm-wave.mjs`. `SKILL.md:18` caps that shape at "100 lanes/wave counting spawns+resumes". `SKILL.md:46-48` settles every registry member as an operator row or honest `cancelled`/`aborted`. That is membership accounting.

The lane's seven gates are cite-check, surface-probe, round-gate, proxy-check, claims-check, kimi-census, and sources-check. `SKILL.md:594-595`: "Owner: this lane (kumitate L1)." None of those gates counts `refused` or `spawned`.

The word "provenance" in the two files is a different object. `corpus/README.md:35` describes `native_dispatch_topology.rs` as "wave-token and exact-dispatch proof" on the judged-round path. `SKILL.md:526-529` treats "missing provenance" as a reason an invalid handoff stays unjudged. `corpus/README.md:139` still lists `provenance{,_tests}.rs` inside the 2026-09-28 uncited runtime-remainder set.

Neither file names `dispatch-provenance`, a refused/spawned integer extractor, or `Background job limit reached`.

## Where the zero is minted

The tally lives in kama. `.ufo/waves/round-17/dispatch-provenance.py:2` calls itself a "wave-dispatch provenance ledger". `:44-46` shells `node /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs run`. `:72-74` says "`refused` keeps the round-16 legacy tally". `:381-382` starts that tally at `counts = {"refused": 0, "spawned": 0}`. Spawned counting was already taught to read "Spawned N background agents" (`:12-14`, `:80-81`). Refused counting was not.

Frozen copy sha256 `11ebb2c02f4c9160a4f20fba8d107b14be648ce6a3b1722dbbd112961b8d96df` matches `round-18/frozen/SHA256SUMS:3` and the live round-17 file (37928 bytes).

Round-17 falsify already ran that code. `.ufo/waves/round-17/falsify/advice/ProvenanceRerun.md:1`: "refused attempts are still undercounted." `:3`: "refusal records report zero for 82 refused tasks."

Round 18's raw refusal is the same shape, with a new count. `.ufo/waves/round-18/build/refused-result-1.json` is a dict with keys `text` and `details` only. `details.results` is an empty list. A full walk found no `refused`, `spawned`, `status`, or `state` key. The text contains the phrase `Background job limit reached` 95 times. Head (`:2`): "Failed to start background task jobs: KamaR18.C1LiveTool: Background job limit reached (100)."

[INFERENCE] The frozen extractor, given that file, records `refused: 0`, `spawned: 0`, `spawned_method: null`. The code path is the one ProvenanceRerun executed; this seat did not run the tool.

The same wave's attempt log already stored the integer. `.ufo/waves/round-18/build/attempts.json:5-7`: `"result": "refused"`, `"refused": 95`, `"error": "Background job limit reached (100)"`. The later success row `:172-174` stores `"refused": 0` beside a `result_head` that begins "Spawned 75 background agents". This seat did not identify the writer of `attempts.json`.

## Contradiction inside the two kumitate files

`corpus/README.md:54` and `:59` say registry family R11 is covered "47 of 47" at internals level. `corpus/README.md:128-139` still says `provenance.rs` has no basename mention, dated 2026-09-28. This seat did not open `knowledge/runtime-remainder-census.md`, so those two sentences stay unresolved. Either way, that Rust file is handoff provenance, not this tally.

A second path split, also unresolved: `SKILL.md:9` cites origin `/home/vgpnk/Projects/origin-work/ufo-fsd-alpha`. The kama ledger invokes `/home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs` (`dispatch-provenance.py:44-46`).

## Proposed move

Leave the repair in kama C2, on `.ufo/waves/round-18/dispatch-provenance.py` (the file this round assigns to C2; it is not in the tree yet). Teach `refused` from the per-task prose the way `spawned` already reads its header, so this round's refusal file records `refused: 95` and `spawned: 0`, and a "Spawned 75 background agents" result still counts as spawned.

Offer kumitate L1 a shape note only. The note carries three facts: the OMP refusal is prose with an empty `details.results`; kama's ledger zero-fills a missing integer; the round-18 attempt log already held `refused: 95`. If they want the producer to emit an integer, their own routing rule applies. `SKILL.md:258-260`, written about the membrane-seal defect: "Fix belongs in ufo-fsd-alpha … report cross-domain, do not absorb."

That split helps calibration, the low axis: `c2/survivors.py` scores this ledger, so the repair has to land in kama's file. It leaves operability alone: no swarm exit code, no kumitate gate, and no out-of-province script in the orchestration repo.

## Risks

- Lanes that copied the zero-fill keep fabricating a refusal count until they read the note. This wave's attempt log already has 95, so kama's dispatch record is not waiting on upstream.
- A recipient who patches `provenance.rs` edits the handoff object named in `README.md:35` and `:139`.
- The note must quote both origin paths and not pick a tree.
- [INFERENCE] The `100` in "Background job limit reached (100)" is the same number as `SKILL.md:18`'s lane ceiling. `attempts.json` records `running_jobs` of 139 (`:28`) while that cap reads 100, so the live-job counter and the cap are different counters. The note should not identify them.

## Verification

Done here: the two kumitate files, the frozen ledger (hash-matched), a key walk of `refused-result-1.json`, and a phrase count of 95. Not done: `dispatch-provenance.py` was not executed; `ufo-swarm-wave.mjs` and `provenance.rs` were not opened.

For L1, after C2's patch, a scratch attempt against `refused-result-1.json` should append `refused: 95`, `spawned: 0`. `spawn-result.json:4` ("Spawned 75 background agents") should still resolve through `omp_text_spawned_header`. Kumitate's tree stays unchanged, so cite-check is not in this move.

## Limitations

Sibling read was limited to `kumitate-shokunin/SKILL.md` and `kumitate-shokunin/corpus/README.md`. No scratch clone. No subagents.

## Installs

None.
