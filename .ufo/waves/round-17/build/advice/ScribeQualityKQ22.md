VERDICT: partial — KQ22 is drafted and the S041 mutation is reproduced read-only, but `--from <round-start>` cannot detect it and `tools/sources-append-only.py` is not in the lane tree.

Draft: `.ufo/waves/round-17/build/drafts/quality-kq22.md` (only owned file written; plus this report). No lane doc, tool, frozen copy or sibling file was edited. Tools installed or updated: none. Access date for every source below: 2026-10-20.

## Behaviour (what KQ22 admits and rejects)

- Admit: immutable cells (`id`, `source`, `kind`, `tier`, `scope`, `anchor`, `teaches`, `opened`) byte-identical from a row's first commit; only `status`, `recheck`, `used-by` change in place, logged old→new; a regenerated artefact or corrected anchor takes a new row whose `teaches` opens `supersedes S0NN —`.
- Reject: in-place immutable edits; a supersession that edits or deletes its target; renumbering or reuse; a flagged change excluded without a named exception.
- Round-end gate, as drafted: `python3 tools/sources-append-only.py --from 1e41928 --to <tip>` exits 0, with each unrepairable historical flag named as an exception.

## Findings

1. **Confirmed: the S041 mutation exists and is the only one in registry history.** Read-only comparison (`git show <rev>:corpus/SOURCES.md`, all 9 commits touching the file, `1e41928`→`ccc4bb3`) found exactly two immutable-cell changes: `S041.anchor` and `S041.teaches`, both at `726f737`→`ccc4bb3`. Only allowed change: `S017.used-by` at `20e392e`→`b8e485c`. The row was first committed at `b8e485c` (`git log -S'| S041 |'`). Quotes:
   - `corpus/SOURCES.md:53` (new S041 anchor): "receipt `kama-llamacpp-live/v1` 2026-10-20T14:06:27.859Z–14:06:27.974Z, port 37527" (old: `13:49:38.040Z–13:49:38.170Z, port 32845`).
   - Teaches new text adds "`/v1/models` 503 with the exact loading envelope while loading" (old: "answers `/health` 200, `/v1/models` id = alias").

2. **Contract rule 2 is the authority.** `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:49-50`: "Only `status`, `recheck` and `used-by` change in place, and each change is logged old→new in the round lesson." Line 50–51: "A correction is a new row whose `teaches` opens `supersedes S0NN —`." The contract lives outside the lane at the fleet root; the lane cites it at `corpus/SOURCES.md:3`.

3. **The lesson disclosed the amendment but did not log old→new.** `corpus/lessons/round-16.md:147-149`: "S041's anchor and teaches cells were amended before closure because the receipt file was regenerated; the row was first committed this round (`b8e485c`)." No before/after text appears there. Routed defect 3 (`corpus/lessons/round-16-verifier-spotcheck.md:184`): "a later receipt regeneration must take a superseding row."

4. **Round-start base cannot see the S041 change.** `cff9e62` (current tip, which I take as the round-17 start [INFERENCE]) already contains the amended S041. A check with `--from cff9e62` passes vacuously. My read-only reproduction lists the flag only when the range includes `ccc4bb3`. The draft therefore sets the base to `1e41928`, the first commit touching `corpus/SOURCES.md`.

5. **Consequence for the gate: the checker flags, the caller excepts.** With base `1e41928`, the S041 pair stays in range permanently, because history cannot be rewritten; a superseding row does not remove the historical flag (`corpus/lessons/round-16-verifier-spotcheck.md:184`). `KamaR17.SourcesAppendOnly-2` confirmed its guard is a pure detector with no built-in exception list (IRC, 2026-10-20). The named, dated S041 exception is therefore caller policy: the round lesson lists it with commit, row and cell, and the round records the checker result after that list is applied. The draft now says this (`drafts/quality-kq22.md` KQ22 row). Earlier wording that the checker itself must carry an exception list is withdrawn.

6. **Tool not present.** `tools/` at lane tip holds only `kama-llamacpp-live.py`, `kama-ollama-evidence.py`, `kama-probe.sh`, `test-snapshot.sh`; `git ls-files` shows no `sources-append-only.py`. I did not run any tool. The KQ22 gate sentence is unverified until the sibling tool lands.

7. **Precedents for supersession exist.** `corpus/SOURCES.md:43` (S031): "supersedes S011 — available inventory may include"; `corpus/SOURCES.md:52` (S040): "supersedes S021 — S021's recorded URL now returns 404". Both preserve the superseded row's cells and status (S021 stays `queued`).

8. **Future trigger [INFERENCE from assignment text].** Round-17 C2 plans receipt `kama-llamacpp-live/v2`. If it regenerates the receipt that S041's anchor names (v1 at `.ufo/waves/round-16/live/receipt.json`), the anchor cannot be edited in place; KQ22's supersession route applies.

9. **Admission scope.** `corpus/QUALITY.md:3`: "Criteria apply to new admissions and explicit corrections." KQ22 fits the explicit-corrections clause; it adds no registry content. KQ7's append-only rule (`corpus/QUALITY.md:29`) and KQ14 remain in force.

## Limitations

- Did not run `tools/sources-append-only.py` (absent) or any lane gate (`sources-census.sh`, `measure.py`, `controls.py`); the S041 result is my own read-only git comparison, not the tool's verdict.
- Round-17 start `cff9e62` is an inference from the tip, not a recorded round boundary.
- KQ20/KQ21 content unknown to me; I did not read sibling drafts. Heading may need merging by L1.
- The exception mechanism (finding 5) is unresolved in this draft by design; L1 or the sibling tool owner must choose it.

## Coordination

Sent one short message to `KamaR17.SourcesAppendOnly-2` about the base (`1e41928`, not round start) and the exception requirement. Sent none to other peers.

## Commands run (read-only)

- `git log --format=… -S'| S041 |' -- corpus/SOURCES.md` → `b8e485c`.
- `git log --reverse --format=%h -- corpus/SOURCES.md` → 9 commits, first `1e41928`, last `ccc4bb3`.
- A throwaway Python parser over `git show <rev>:corpus/SOURCES.md` comparing consecutive revisions (script deleted afterwards). Output as in Findings 1.
- `git ls-files tools`, `git rev-parse master` (`cff9e62f05aa7cfb9059444f62eb787100719713`).
