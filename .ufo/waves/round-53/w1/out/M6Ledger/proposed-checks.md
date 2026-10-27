# Non-binding future-check proposals for M6Ledger survivors

The round-53 C2 counter and preregistration are frozen. These are coverage observations only; no counter, ledger, or lane file was changed.

1. **`upstream` pin/content binding (M10–M12).** After fetching the URL, SHA-256 the response body and compare it with the full digest recorded in that ledger row's `note` field (the four upstream notes already carry hashes). Alternatively, derive and enforce the expected ref from an independently pinned source. The response-hash option would reject M10's `master` bytes (`7f4d7c35…` vs pinned `1f9d7b73…`) and M11's renamed-origin bytes (`c673b061…` vs pinned `b4f4aae7…`); it also makes M12's parent-ref alias explicit even though its current bytes happen to match.

2. **`never` provenance binding (M13).** The frozen `never` test correctly proves only “not in lane/fleet history”; it cannot prove the file is not an upstream project's file. A future contract could separately verify upstream provenance for `tools/server/...` tokens against a pinned upstream tree or a required per-path external source inventory. Do not treat the M13 survivor as a false result for the frozen `never` predicate; it is a semantic-class/provenance gap in the broader disclosure claim.

3. **`fixed` replacement binding (M15).** For in-place corrections, require the replacement citation to occur at the original token's citation line from `--base` (or explicitly store old/new line anchors and verify the replacement at the expected location). The current check only requires some resolving citation with the replacement token anywhere on the surface; M15 uses a different valid citation at SKILL.md:919 instead of the actual replacement at line 895.
