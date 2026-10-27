VERDICT: Frozen C2 killed 10 of 15 ledger-row mutants; 5 survived (M10–M13, M15), exposing accepted alternate upstream evidence, an upstream→never class swap, and an arbitrary resolving fixed replacement; baseline and restored bytes both met the predicate.

# Round 53 C2 ledger mutation test — M6Ledger

## Scope and harness

The probe targets the frozen C2 counter at `tools/round53-cited-path-check.py`, without modifying it, the preregistration, or lane files. I used the lane's shared clone only:

```text
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r53/M6Ledger/lane
```

Before the first clone commit, `git -C /fast/scratch/hyaku/kama-r53/M6Ledger/lane rev-parse --show-toplevel` printed `/fast/scratch/hyaku/kama-r53/M6Ledger/lane`. Each mutant is one commit from pristine `c22602bd8d83ab26349d1087e916ca537ee4f9d1`, changing one row only; the counter was run separately for each full mutant tip. The fleet revision was pinned to `ee9f7341bd98de0fcd85f6c01f689301589b27e9`, the revision in the build receipt, rather than the later HEAD.

Command pattern (each receipt is copied into `M6Ledger/<name>.out`):

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-cited-path-check.py \
  --repo /fast/scratch/hyaku/kama-r53/M6Ledger/lane \
  --tip <full-mutant-commit> \
  --fleet-rev ee9f7341bd98de0fcd85f6c01f689301589b27e9 \
  --scratch /fast/scratch/hyaku/kama-r53/M6Ledger/run-<name> \
  --out /fast/scratch/hyaku/kama-r53/M6Ledger/out/<name>.out
```

## Pristine and restoration controls

- Pristine `c22602bd8d83ab26349d1087e916ca537ee4f9d1`: exit 0; `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True`. This exactly matches `.ufo/waves/round-53/measured/c2-build.out` with the same fleet revision.
- Original ledger SHA-256: `87a1c696f5bc315e029f898d6476f1a48eda7964436034e0ff4a5a20767c2bf5`.
- After all mutants, a restore commit `18fd9c8e8671f511ffd5b94705f491934f17eec8` restored the exact original ledger bytes; SHA-256 matched. `git -C <clone> status --porcelain` had zero lines.
- Restored counter run: exit 0; `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True` (`M6Ledger/RESTORE.out`).

## Mutant results

“Killed” means C2 returned exit 1 and identified the mutated ledger row as bad, with its citation undisclosed. “Survived” means C2 returned exit 0 / `met=True` with the mutant row accepted. Per-mutant tips, ledger hashes, and exact unified ledger diffs are in `M6Ledger/mutant-tips.tsv` and `M6Ledger/M01.diff`…`M15.diff`; complete counter output is in the matching `.out` receipt.

| Mutant | Ledger line; mutation | Counter result | Verdict |
|---|---|---|---|
| M01 | 25; `never`→`deleted`, evidence set to base commit | exit 1; `bad=1 undisclosed=1`; no commit proved deletion | Killed |
| M02 | 27; `never`→`moved`, evidence `SCORECARD.md` | exit 1; `bad=1 undisclosed=1`; token never existed in lane | Killed |
| M03 | 29; `never`→`eof`, evidence set to build tip | exit 1; `bad=1 undisclosed=1`; path is missing, not beyond EOF | Killed |
| M04 | 31; `deleted` evidence changed from deleting commit `9874e455…` to its parent `addeb57c…` | exit 1; `bad=1 undisclosed=1`; parent does not delete token | Killed |
| M05 | 33; `never`→`untracked` | exit 1; `bad=1 undisclosed=1`; file absent on fleet disk | Killed |
| M06 | 35; `never`→`fixed`, replacement `corpus/lessons/round-53.md` | exit 1; `bad=1 undisclosed=1`; fixed token is still cited at tip | Killed |
| M07 | 37; `never`→`untracked` | exit 1; `bad=1 undisclosed=1`; file absent on fleet disk | Killed |
| M08 | 39; brace-group `never`→`untracked` | exit 1; `bad=1 undisclosed=1`; expanded `base.out` absent on fleet disk | Killed |
| M09 | 41; `untracked`→`upstream`, URL points to watchdog.log | exit 1; `bad=1 undisclosed=1`; URL returned HTTP 404 | Killed |
| M10 | 43; upstream schema URL ref `704366d76…`→`master` | exit 0; `bad=0 undisclosed=0 met=True` | **Survived** |
| M11 | 45; upstream common URL owner `ggml-org`→`ggerganov` | exit 0; `bad=0 undisclosed=0 met=True` | **Survived** |
| M12 | 47; upstream schema URL ref changed to parent commit `707616feb5…` | exit 0; `bad=0 undisclosed=0 met=True` | **Survived** |
| M13 | 49; upstream `server-task.cpp` class→`never`, evidence `-` | exit 0; `bad=0 undisclosed=0 met=True` | **Survived** |
| M14 | 51; upstream `server-chat.cpp` class→`fixed` | exit 1; `bad=1 undisclosed=1`; fixed token is still cited at tip | Killed |
| M15 | 53; `fixed` replacement `tests/report-audit/`→`tests/report-audit/promisor-grid.py` | exit 0; `bad=0 undisclosed=0 met=True` | **Survived** |

## Survivor findings

1. **Upstream pin/content is not re-derived (M10–M12).** At `tools/round53-cited-path-check.py:298-313`, the `upstream` branch validates the URL shape/path suffix, fetches it, and accepts HTTP 200 (`:306-308`); it does not validate the pinned ref, repository identity, or returned content hash. All three alternate URLs were HTTP 200. Actual fetched hashes show the risk is material: the pinned schema URL returns `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`, while M10's `master` URL returns `7f4d7c35a10d0deb6eef8a02a222a0ecf3295b7ec6c65b512e3f241b47df6b54`. The pinned common file returns `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442`, while M11's renamed-origin URL returns `c673b0616dc9d977819cb860f74de5c514b32c2693d86ef0ce452730eb0d18a4`. M12's parent ref returned the pinned schema bytes, but still demonstrates that the stated snapshot ref is not enforced. The ledger notes already contain the full source hashes. This is a coverage finding; see `M6Ledger/proposed-checks.md` for a non-binding future check proposal.

2. **Upstream provenance can be weakened to `never` (M13).** At `tools/round53-cited-path-check.py:265-270`, `never` checks only lane/fleet history. The token `tools/server/server-task.cpp` had zero matching commits in each repository's `git log --all --name-only`; therefore a `never` row passes even though its original row explicitly documents an upstream llama.cpp file. The frozen `never` predicate is true by its stated lane/fleet-history definition; the surviving mutation shows that the wider disclosure claim does not bind a row's class to upstream provenance. This is a coverage finding, not a change to the frozen contract.

3. **A `fixed` row accepts an unrelated replacement citation (M15).** At `tools/round53-cited-path-check.py:239-255`, the check confirms the old token is no longer cited, was unresolved at base, and that the evidence token is cited and resolves at tip. It does not establish that the replacement is the actual correction. M15 changed the evidence from the actual in-place replacement `tests/report-audit/` at SKILL.md:895 to the unrelated-but-resolving `tests/report-audit/promisor-grid.py` at SKILL.md:919; C2 still returned `met=True`. Future-check proposal is in `M6Ledger/proposed-checks.md`.

## Row-count note and evidence inventory

Tasking described 14 rows. At the specified build tip, `registry/cited-path-corrections.tsv` has 15 data rows: 14 non-`fixed` unresolved disclosures plus one `fixed` correction row (the counter excludes `fixed` from the disclosed count). I mutated all 15 rows, one row per run. No baseline failure or inconclusive run occurred. No tool was installed; no llama-server was started, and the final process check found no `llama-server` process. `M6Ledger/probes.txt` records URL statuses, content hashes, and preflight history/disk probes. `M6Ledger/ledger.orig`, `M6Ledger/mutants/`, all `.diff` files, and all counter receipts preserve the detailed bytes and outputs.
