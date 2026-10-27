# L1Slice disclosure-row audit

Scope: all 22 ledger rows for `corpus/README.md` and `corpus/QUALITY.md`. `class ok?` compares the ledger class to append-only-audit v6's mechanical rule (tool docstring lines 20-23). `A-corr` means the file contract says corrections are appended (`registry/append-only-contract.tsv`: README and QUALITY rows). Thus the historical in-place edit should have been recorded as an appended correction; `restore?` is whether substantive lost information should now be restored by append.

| commit12 | file | sha12 | class ok? | kind | A-corr / restore? |
|---|---|---|---|---|---|
| c6199a254244 | corpus/README.md | 5a0b8299e413 | yes | scope/gap list replaced by expanded operational limitations | Append correction; no restore indicated (replacement expands limitations). |
| c6199a254244 | corpus/README.md | 90b2d1fa04cf | yes | inventory claim replaced by operator-owned consumer caveats | Append correction; no restore indicated (scope recast). |
| c6199a254244 | corpus/README.md | 97c8eb730ee1 | yes | empty placeholder replaced by coverage-map rows (structural addition) | Append correction; no restore (placeholder was not substantive content). |
| c6199a254244 | corpus/README.md | bb2e4385bf92 | yes | introductory wording split/rephrased | Append correction; no restore (meaning retained in revised introduction). |
| c6199a254244 | corpus/README.md | f0bd12da3b7d | yes | duplicate/earlier introduction wording replaced by consolidated wording | Append correction; no restore (meaning retained). |
| 83bee7faf5a7 | corpus/README.md | a58011fdcc7d | yes | runtime limitation reworded and qualified with fixture-vs-runtime evidence | Append correction; no restore indicated. |
| 83bee7faf5a7 | corpus/README.md | a8b647365928 | yes | cadence gap clarified (manual snapshot vs operator-owned timer) | Append correction; no restore indicated. |
| 83bee7faf5a7 | corpus/README.md | bb5b130fdcf8 | yes | runtime limitation replaced with more precise qualification | Append correction; no restore indicated. |
| 83bee7faf5a7 | corpus/README.md | dadc3bf9c569 | yes | scheduled-check proposal replaced by actual invocation/timer boundary | Append correction; no restore indicated. |
| ea72c3eae4ec | corpus/README.md | 094cad3f26a9 | yes | current-state pointer re-anchored as historical | Append correction; no restore (current explanation and errata pointer added). |
| ea72c3eae4ec | corpus/README.md | 44e7a89a373c | yes | same historical re-anchor of consumer paths | Append correction; no restore. |
| ea72c3eae4ec | corpus/README.md | 7a33a5a064ce | yes | status wording re-anchored to historical state | Append correction; no restore. |
| e246c40ec1b4 | corpus/README.md | cdad27d51188 | yes | context-size limitation qualified as historical; frontier section structurally added | Append correction; no restore indicated. |
| 726f737a942f | corpus/README.md | 0c85a17cc7a2 | yes | coverage pointer list expanded to include correction targets and evidence artifacts | Append correction; no restore indicated. |
| 726f737a942f | corpus/README.md | 44c080a09211 | yes | frontier limitation rewritten with measured sample qualification | Append correction; no restore indicated. |
| 726f737a942f | corpus/README.md | 9d51bbde2230 | yes | correction-target list expanded (structural pointer update) | Append correction; no restore indicated. |
| 726f737a942f | corpus/README.md | 9eab389e9905 | yes | frontier wording updated to reflect new sample | Append correction; no restore indicated. |
| 726f737a942f | corpus/README.md | a81f35884411 | yes | frontier claim reworded and expanded | Append correction; no restore indicated. |
| 726f737a942f | corpus/README.md | efba3e7941dc | yes | frontier disposition rewritten with added caveats | Append correction; no restore indicated. |
| e97ce4964b17 | corpus/QUALITY.md | 037b9ccc0c75 | yes | criterion heading reworded/narrowed | Append correction and explicitly supersede old criterion; no clearly unique lost claim requiring restoration beyond the replacement criterion. |
| e97ce4964b17 | corpus/QUALITY.md | 8d0fb4121c3e | yes | KQ46 criterion materially rewritten/narrowed, not a typo | Append correction naming superseded KQ46; review old and new criterion together for any intentionally dropped checks. No exact old line remains at tip. |
| 2793eb5173e3 | corpus/README.md | 67730a8d26eb | yes | documentation pointer re-anchored with repo-relative path | Append correction; no restore (description and cited source identifiers retained). |

## Mechanical checks

For each row, the ledger key matched exactly one deleted line in the indicated commit's diff; the recomputed class matched the disclosed class. The exact CR-stripped line key occurred zero times in the file at tip `138af25b963450b6520794995605fa7dbbcd87e0` (parent count was one for each). Therefore no row is an exact-text moved line missed at that tip. The zero exact-key result does not prove that every semantic detail survived a rewritten line; the Quality KQ46 rewrite is the main substantive-review caveat.
