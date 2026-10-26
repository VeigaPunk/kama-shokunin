# U1Prior - prior art for C1 (append-only audit v2)

Verdict: no surveyed project defines a "restored line"; the prior art enforces per edge, counts lines or checks file status, or avoids the problem by structure. v2's multiset-over-window restoration has no precedent, and two techniques would close measured blind spots: a strict byte-prefix per edge (56 zero-deletion mid/top insertions on the lane that no deleted-line audit sees) and ancestry/consistency checking (history rewrite). Neither changes the C1 result (7->7); full text and located quotes are in `.ufo/waves/round-47/w1/out/U1Prior/prior.md`.

## Sources (quotes in prior.md, each <=25 words)
- git-diff `--numstat` (https://git-scm.com/docs/git-diff, diff-options.adoc:231-235): machine-friendly added/deleted counts, `-` for binary. v2's deleted contract matches it.
- git pickaxe `-S` (https://git-scm.com/docs/gitdiffcore, gitdiffcore.adoc:251-253): occurrence-count basis; "will not detect in-file moves". Same limit as v2's multiset.
- dangoslen/changelog-enforcer README (https://github.com/dangoslen/changelog-enforcer): checks file status `A`/`M`, not deleted lines. towncrier README (https://github.com/twisted/towncrier): file-per-entry, avoiding the single shared file.
- Enforcement: githooks `update` / `receive.denyNonFastForwards`, GitHub branch protection, chattr `a`, RFC 6962 §2.1.2 consistency proofs.

## Measured (lane 3a09a1d, 303 commits, 85 files; scripts and outputs in out/U1Prior/)
- Command: `python3 prefix_scan.py <clone> 3a09a1d93dcc16799cf6c4b48786e6440af134c4`, output `prefix_scan.out`, exit 0. First-parent edges, strict byte-prefix vs numstat: 267 pure append, 5 deleted>=20 (v2's events), 81 deleted 1-19, **56 deleted=0 but not a prefix** (SOURCES.md 32, SCORECARD.md 8, lessons 10, LOG.md 3, README.md 2, QUALITY.md 1; `mid_breakdown.out`).
- 5 of v2's 91 threshold-1 events are byte-pure appends (EOF newline artefact: LOG.md 83bee7fa/33b167ec/84a81304, SCORECARD.md 84a81304, corpus/README.md 1e41928a); v2 grades them `restored`, correctly.
- v2 at 3a09a1d reproduced here: exit 1, 5 events, 3 restored, 2 partial; `--threshold 1`: 91 events (5 + 86).

## Findings
- **F1 (new, definitional): v2 grades a pure reorder `restored`.** `fixture_move.sh` (exit 0): 40-line LOG.md, last 25 lines moved to top; numstat `15 15`; v2 `--threshold 10` -> `deleted=15 restored_max=15 status=restored restored_by=<same commit>`. A move is indistinguishable from a restoration (git's `-S` has the same limit). Confidence high.
- **F2: 56 zero-deletion non-append edits** are invisible to v2 although corpus/QUALITY.md:24 and corpus/README.md:86 declare "no existing line moves". A byte-prefix per edge closes it and also avoids the `---` bug class; it needs region scoping (K1Design) to be a gate.
- **F3 (K1Design/K1Regions regions):** prior art has no region scoping; towncrier's structural answer (separate files for the mutable parts) is the transferable one.
- **F4 (L1Lowthr):** all surveyed mechanisms are zero-tolerance; legitimate exceptions use an allow-list or label, not a size threshold.
- **F5 (untested, medium):** v2 audits only the rev-list of `--to`; a rewritten history shows no events. Proposed: record the audited tip and require `git merge-base --is-ancestor <previous tip> <to>`.

## Caveats
- GitHub "protect" actions: I found no primary-source action for append-only files; the shipped primitive is branch protection (non-fast-forward and delete blocking). Search results were generated summaries and are not cited.
- F5 and the recommendations are proposals; I did not apply or test them. Nothing in the lane was edited.

## Hygiene
No tools installed (python3, git 2.56.0, curl). Scratch `/fast/scratch/hyaku/kama-r47/U1Prior` removed before finishing.

Written: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U1Prior.md, /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/U1Prior/prior.md (+ prefix_scan.py/.out, mid_breakdown.py/.out, fixture_move.sh/.out in the same directory)
