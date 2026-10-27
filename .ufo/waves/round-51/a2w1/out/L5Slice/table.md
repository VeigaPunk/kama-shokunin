# Round-25–28 disclosure ledger slice

Audited all 46 registry rows for `corpus/lessons/round-25.md` through `round-28.md`: each deleting commit's `git show --format= --unified=0 <commit> -- <file>` contained exactly one removed line whose CR-stripped SHA-256 matched the registry hash. At commit `138af25b963450b6520794995605fa7dbbcd87e0`, none of these exact lines remains in the same file (checked by SHA-256 over the committed file contents). The classifications below distinguish semantic replacements from loss; `in-place-edit` is therefore generally correct even where the wording or fact was removed. None merits literal restoration: reappending stale/outdated text would be misleading; corrections and qualifications were appended or integrated in the relevant round lesson. A-corr application: preserve historical facts only when still materially true; where a statement was erroneous, superseded, or corrected, append a correction rather than revive it. No content-loss row identified.

| Commit12 | File | SHA12 | Class ok? | Kind | Restore? |
|---|---|---|---|---|---|
| c0a9b029c035 | round-25.md | 09aa69a2a9bd | yes | wording/qualification replacement (C1 before-command stop) | no |
| c0a9b029c035 | round-25.md | 2f0ea822cc71 | yes | wording/qualification replacement (axis attribution) | no |
| c0a9b029c035 | round-25.md | 488ff6ae778a | yes | wording/qualification replacement | no |
| c0a9b029c035 | round-25.md | 51218755068b | yes | wording/qualification replacement | no |
| c0a9b029c035 | round-25.md | 56bea03fa43e | yes | wording/qualification replacement | no |
| c0a9b029c035 | round-25.md | 69ca7179a5c4 | yes | erratum wording update | no |
| c0a9b029c035 | round-25.md | 9ec28861e2b9 | yes | wording/qualification replacement | no |
| c0a9b029c035 | round-25.md | aac2e318873d | yes | wording/qualification replacement | no |
| a46a61815f79 | round-25.md | 3f6e2f6a1aa2 | yes | erratum correction | no |
| a46a61815f79 | round-25.md | e850feb88355 | yes | source anchor correction | no |
| fd48f9a3b7ca | round-26.md | 1056ba279a92 | yes | source-row correction | no |
| fd48f9a3b7ca | round-26.md | 157e58cae654 | yes | count correction | no |
| fd48f9a3b7ca | round-26.md | 1ee2b7f84a8a | yes | source-row correction | no |
| fd48f9a3b7ca | round-26.md | 1eebc04b79a5 | yes | source-row correction | no |
| fd48f9a3b7ca | round-26.md | 26edd0a54128 | yes | omission/scope correction | no |
| fd48f9a3b7ca | round-26.md | 2ac3cd9a6873 | yes | timestamp erratum | no |
| fd48f9a3b7ca | round-26.md | 383cc683a47e | yes | redundancy pruning | no |
| fd48f9a3b7ca | round-26.md | 3cc9c47140da | yes | structural/procedure wording edit | no |
| fd48f9a3b7ca | round-26.md | 3d61348d0e36 | yes | wording edit | no |
| fd48f9a3b7ca | round-26.md | 3de77d0b28f9 | yes | source-row correction | no |
| fd48f9a3b7ca | round-26.md | 5c027c78f946 | yes | erratum wording correction | no |
| fd48f9a3b7ca | round-26.md | 9ad0c7c0e015 | yes | source-row correction | no |
| fd48f9a3b7ca | round-26.md | a8e4fcc65aca | yes | source-row correction | no |
| fd48f9a3b7ca | round-26.md | b015de5bbf84 | yes | source-row correction | no |
| fd48f9a3b7ca | round-26.md | c31256f9c01e | yes | supersession attribution update | no |
| fd48f9a3b7ca | round-26.md | e732b6125de6 | yes | receipt/duplicate clarification | no |
| fd48f9a3b7ca | round-26.md | edf48397119c | yes | source provenance wording edit | no |
| d183ec572a5e | round-27.md | 42445a5885dd | yes | verdict corrected per frozen kill rule | no |
| d183ec572a5e | round-27.md | 55cfcefa6432 | **no** | removal of blanket assertion; contradicted by newly admitted corrections | no (do not restore false assertion) |
| d183ec572a5e | round-27.md | 5c88056e8087 | yes | source/novelty qualification | no |
| d183ec572a5e | round-27.md | c0f899e0cd19 | yes | count correction | no |
| d183ec572a5e | round-27.md | e03edacccc20 | yes | mistake-row precision correction | no |
| d183ec572a5e | round-27.md | ec9b6e4affb6 | yes | count/path clarification | no |
| d183ec572a5e | round-27.md | f0f7b55913ca | yes | verdict corrected per frozen kill rule | no |
| d183ec572a5e | round-27.md | fc179550ed30 | yes | verdict corrected per frozen kill rule | no |
| 4d2e74f421bc | round-27.md | 1dea72ec2842 | yes | seat attribution wording edit | no |
| 4d2e74f421bc | round-27.md | 3f4e7491029a | yes | count correction | no |
| 4d2e74f421bc | round-27.md | 78208abada5f | yes | source-row supersession | no |
| 4d2e74f421bc | round-27.md | 8f2c6ddf5d48 | yes | mistake-row precision correction | no |
| 4d2e74f421bc | round-27.md | f533cbde1bfa | yes | path/attribution clarification | no |
| 9ce5bd377562 | round-28.md | 07558d232ae1 | yes | registry/counter correction | no |
| 9ce5bd377562 | round-28.md | 0fc477177294 | yes | report precision correction | no |
| 9ce5bd377562 | round-28.md | 3b9e2130606b | yes | amendment chronology clarification | no |
| c23ebaa4883a | round-28.md | 2c151c250e81 | yes | meaning-cell/intro correction | no |
| c23ebaa4883a | round-28.md | 2c3a9f31b5cd | yes | control-wave evidence wording edit | no |
| c23ebaa4883a | round-28.md | 2fcca81865fe | yes | wave evidence wording edit | no |

**Classification defect:** row `d183ec572a5e…`, SHA `55cfcefa6432…`, says the deleted text was a `removal`. The diff removes “No existing row's `status`, `recheck` or `used-by` changed.” but this round specifically changes the same-file S136 source row to supersede its escape-length wording and STD 90 attribution; immediately following text describes the supersession. This is an in-place edit of an overbroad statement, not a whole-line removal of an otherwise valid record. Recommended smallest correction: revise that ledger class from `removal` to `in-place-edit`; do not restore the assertion. A-corr is satisfied by the subsequent explicit account of the S136/S139 change.
