# LOG.md disclosure audit at 138af25b963450b6520794995605fa7dbbcd87e0

Each row's deleted text was matched by SHA-256 after removing a trailing CR from `git show -U0` output. Exact text presence was checked against tip `LOG.md`; none of these exact lines remain. `restore?` means append a correction now, not reinsert at the historical location.

| commit12 | file | sha12 | class ok? | kind | restore? |
|---|---|---|---|---|---|
| ed135b3cb869 | LOG.md | 2ee99d81fe2e | yes | content loss: removed dated HOURS ledger-opening entry | yes — append historical correction |
| ed135b3cb869 | LOG.md | b0a06400ef3c | yes | content loss: removed evidence pointer | yes — with entry correction |
| ed135b3cb869 | LOG.md | df41705d9aab | yes | content loss: removed operator-seed statement | yes — with entry correction |
| ed135b3cb869 | LOG.md | eb379fbf0bf9 | yes | content loss: removed threshold/gate/starting-state detail | yes — with entry correction |
| ed135b3cb869 | LOG.md | eee7f85d24a8 | yes | content loss: removed accrual method | yes — with entry correction |
| 47f3aedd6fa3 | LOG.md | a43ddc93e9f4 | yes | pointer re-anchor (`.ufo/...` → `../.ufo/...`) | no; correction not required for path repair |
| f4066979096e | LOG.md | 13740f679956 | yes | wording/count correction (58 candidates → split executor/scout accounting) | no; replacement supplies corrected count |
| f4066979096e | LOG.md | cd7a470f35e5 | yes | wording/count correction (candidate count attribution) | no; replacement supplies corrected count |
| f4066979096e | LOG.md | ea2880ea2f76 | yes | structural move/rewrite of Gate pointer clause | no; replacement retains disposition and pointer |
| fd48f9a3b7ca | LOG.md | 0bbbbbc0f664 | yes | content correction: 42 paths phrasing replaced by late-status entries and missing log | no; replacement retains corrected repair details |
| fd48f9a3b7ca | LOG.md | 2608dd4217d2 | yes | wording/content correction of pre-round-26 signature claim | no; replacement names existing signatures and absent E26 strings |
| fd48f9a3b7ca | LOG.md | 376c554e1051 | yes | wording/content correction of C1 baseline | no; replacement is more precise |
| fd48f9a3b7ca | LOG.md | 68fbe8d485cd | yes | wording correction of source characterization (dead ports → registered ports; 34113 status) | no; replacement retains/revises claim |
| fd48f9a3b7ca | LOG.md | c27514e6dd4a | yes | wording/count correction of scout totals | no; replacement retains corrected attribution |
| 9cb3abae9d48 | LOG.md | 052010766b81 | yes | pointer/provenance re-anchor (working-tree tool → landed tool at tip) | no; replacement is the corrected provenance |
| ce41bae692c8 | LOG.md | 25f19868c2ef | yes | placeholder replacement (measured commit) | no; concrete measured commit replaces placeholder |
| ce41bae692c8 | LOG.md | 656e1c1b0cab | yes | placeholder replacement (C1 after result) | no; concrete result replaces placeholder |
| ce41bae692c8 | LOG.md | a1aa54d42766 | yes | placeholder replacement (C2 after result) | no; concrete result replaces placeholder |
| ce41bae692c8 | LOG.md | e66efd0f1c68 | yes | placeholder replacement (C3 after result) | no; concrete result replaces placeholder |
| 2c0181074050 | LOG.md | cd4b6a9addf9 | yes | wording/content correction with added counter limitation | no; replacement retains account and adds qualification |
| 8bee4e56a995 | LOG.md | 933aa6338c7a | yes | count correction (six Mistakes → five specified rows) | no; corrected count and row identities supplied |
| 8bee4e56a995 | LOG.md | 99e4e99e0a68 | yes | wording/count correction (nine controls → base plus seven shortcut controls) | no; corrected control count supplied |

