# Mutation inventory (round 24, promisor C1)

Base 0df800e896f6bce285a81e794ad4ae1d1e6c3a71; runner `6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`;
candidate auditor `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`;
grid `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` (manifest d86b7bea…, 47 cells).

Exit map: 0 = the inventory was fully evaluated (killed and surviving mutants are
reported, a kill is not an exit code); 2 = could-not-evaluate, kills nothing.
PM08 is static-only and is never executed against the grid.

| id | execution | attributed grid cells | semantic |
|---|---|---|---|
| PM01-blanket-metadata-refusal | grid | PG01, PG02, PG03, PG04, PG05, PG06, PG07, PG08, PG09, PG11, PG12, PG13, PG17, PG21, PG22, PG23, PG24, PG26, PG28, PG30, PG31, PG33, PG35, PG39, PG41, PG43, PG44, PG47, PG48 | promisor metadata alone (extensions.partialClone, remote.*.promisor, partialclonefilter, paired .promisor+.pack) is not a refusal: a complete promisor-marked repository keeps the verdict of its full-clone twin |
| PM02-blanket-unknown-refusal | grid | PG22, PG23, PG24, PG25, PG29, PG30, PG33, PG34, PG37, PG41, PG42, PG47 | the unknown rule covers a locally unresolved citation that names unavailable referenced content; it must not cover every absent citation, or the historical errata-marked clone (absent hash corrected by errata) would stop being an ordinary failed finding. The mutant refuses every absent (or unknown) citation, before the errata ledger is consulted. |
| PM03-skip-required-object-availability | grid | PG13, PG14, PG15, PG16, PG17, PG18, PG19, PG20, PG21, PG33, PG34, PG47 | objects the audit actually reads must be available: a missing required commit/tree/blob/report object is could-not-evaluate (exit 2), never a clean or failed verdict. This mutant removes the store's missing-object computation (the completeness element); PM04 removes the decision that uses it. Both attack the same verdict surface, so the grid kills them alike: one of them surviving is not evidence about the other. |
| PM04-accept-unavailable-referenced-object | grid | PG33, PG34, PG46, PG47 | a locally unresolved citation that names unavailable referenced local content is could-not-evaluate rather than proved absent; the mutant accepts it as absent and reports an ordinary failed finding |
| PM05-ignore-second-repo | grid | PG26, PG27 | a citation missing in one audited repository but present in the other audited repository is resolvable; the mutant consults the first repository only |
| PM06-swallow-actual-read-error | grid | PG13, PG14, PG16, PG17, PG18, PG20, PG21, PG43 | a failing read of the object the audit needs is could-not-evaluate; the mutant swallows the failure and guesses a value, turning an unavailable object into a verdict |
| PM07-full-all-missing-gate | grid | PG31, PG32, PG35, PG36, PG44, PG45, PG48 | the missing-object traversal is rooted at the pinned lane/fleet roots the audit reads; the mutant roots it at --all. Redundant on a candidate whose traversal already starts from every present object: there it is observationally identical, survives, and is credited with no kill. |
| PM08-remove-no-lazy-fetch-gate | static-only | - | every git call carries --no-lazy-fetch, so a missing promisor object can never be fetched through the promisor remote (transport, repository programs, signatures); removing the flag reopens that channel |
| PM09-peel-bare-full-hash-lookup | grid | PG38, PG39 | the bare full-hash lookup stays unpeeled: a citation of a locally present blob resolves as found; peeling it to ^{commit} turns a present blob into a missing object |
| PM10-ignore-opaque-nonleaf-missing | grid | PG33, PG34, PG46, PG47 | when a citation is unresolved, a missing tree or commit may conceal the dependency names, so the citation is unevaluable (exit 2); the mutant ignores that hole and reports an ordinary failed finding. A known-present blob that merely fails commit peeling keeps its wrong-type finding either way. |
| PM11-any-hole-refusal | grid | PG22, PG25, PG33, PG34, PG35, PG36, PG37, PG41, PG42, PG44, PG45, PG47, PG48 | no missing-object state may be an unconditional audit precondition: an unrelated blob hole next to a fabricated citation keeps the ordinary failed finding, and an unused tree hole next to fully resolved citations keeps the clean verdict; the mutant refuses on any hole |
