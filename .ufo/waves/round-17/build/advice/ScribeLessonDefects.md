VERDICT: partial — routed defects 1–6 and the jj risks re-grounded at master `cff9e62`; the round-16 lesson's count, S041, wording and install items hold; `registry/history/.lock` claim refuted; `check.py` mutant count not re-measured

# ScribeLessonDefects — round-17 lesson draft, scoped findings

Draft written: `kama-shokunin/.ufo/waves/round-17/build/drafts/lesson-defects.md` (owned; the only file written besides this report). Access date for all sources: 2026-10-20. Lane tip read: `master` = `cff9e62f05aa7cfb9059444f62eb787100719713`. No `jj` command, no git write, no lane gate, no `measure.py`, `mutants.py` or `controls.py` was run. Sessions and `~/.omp` were not read. Tools installed or updated: none.

## Findings (re-verified)

- **Defect 1 (provenance) — confirmed in part.** `kama-shokunin/.ufo/waves/round-16/falsify/` has no `validation.json`; `build/validation.json` has a `"policy": {` block. `kama-shokunin/.ufo/waves/round-16/dispatch-provenance.py:155`: "any dict key literally "refused" or "spawned" carrying an int adds"; the file has zero `pending` occurrences. The build `taskCall` digest producer (`cdf02ba7…`) was not located: [L1 fills].
- **Defect 2 (summary) — confirmed.** `kama-shokunin/.ufo/waves/round-16/falsify/completion-summary.json:22-26` records 36/41/2. Counting the 79 advice files: 36 confirm / 43 partial / 0 refute under "VERDICT on any line"; 74 open with VERDICT on line 1 (34/40/0) and 5 open with a `#` heading (2 confirm, 3 partial).
- **Defect 3 (S041) — confirmed.** Contract `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:49-50`: "Only `status`, `recheck` and `used-by` change in place, and each change". `git show b8e485c:corpus/SOURCES.md` line 53 (port 32845, 13:49:38Z) differs from master line 53 (port 37527, 14:06:27Z). Sanctioned correction route: a row opening `supersedes S041 —` (contract lines 50–51).
- **Defect 4 (wording) — confirmed; scope wider.** Source `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp`: line 312 "no endpoints are allowed to be accessed when the server is not ready"; 318–320 literals; 346 "If this is OPTIONS request, skip validation because browsers don't include Authorization header"; 347–352 OPTIONS branch; 354 state gate call. Phrase also appears in `corpus/knowledge/endpoint-identity.md:202`, which the routed item does not name.
- **Defect 5 (install) — confirmed.** `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` present, 22,240,468 bytes, sha256 prefix `753bfa7327a75b477d4d`; `/usr/bin/llama-server` absent; `readlink -f ~/.local/bin/llama-server` → `/home/vgpnk/.local/opt/llama-b11755/llama-server`.
- **Defect 6 (debt) — not re-measured.** Lesson line 187 "Five `check.py` harness mutants survive." Count is for L1's `mutants.py`.
- **jj R1 — open.** `.ufo/waves/round-13/measure.py:385` (`cat-file blob <HEAD>`), `:397` (`worktree_matches_head`). Mitigation is procedural.
- **jj R2 — open, bootstrap-only.** `.ufo/waves/round-12/fidelity.py:449`, `.ufo/waves/round-13/measure.py:295`.
- **jj R3 — partly mitigated.** `scripts/hyaku/jj-lane.sh:199` (nothing-to-commit exit 0), `:209-214` (file track), `:218-219` (pre-commit diff-summary check, not in the audit). No post-commit non-empty check (audit §6 rec 5 still open).
- **jj §6.6 — open.** `.ufo/waves/round-16/measure.py:116` `["git", "-C", str(LANE), "cat-file", "blob", spec]`; `no-replace-objects` count 0.
- **jj trial rec 2 — partly refuted.** Master `.gitignore` = `.ufo/interactive-sessions/` only; the lane worktree has an uncommitted `.ufo/state/` line (not this seat's; not committed or reverted). `registry/history/.gitignore` already contains `.lock`, so `registry/history/.lock` IS ignored; the audit's claim is wrong.
- **jj trial rec 3 — open.** `git grep -c -i colocat master -- '*.md'` → 0 matches.

## Limitations

- Audit facts pinned at `726f737` were re-checked at `cff9e62` only where marked; the `jj config` values (trial rec 1) and the size threshold (rec 4) were not re-verified because this seat may not run `jj` in the lane.
- `cdf02ba7…` / `72e81bc6…` digest producers not located: [L1 fills].
- Contract rule 2 is read from `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md` (the file the registry header names); the round-16 lesson's log of the S041 changes was not re-read: [L1 fills].
- [INFERENCE] The audit's helper-bookmark-failure risk (`JjAuditKama.md:174`) was not exercised.

## Hand-off for L1

Integrate the draft's sections in this order: defect table, then per-defect dispositions, then the jj table. Decisions L1 must make are marked in the draft: S041 route (superseding row vs disclosure), whether `endpoint-identity.md:202` joins the wording fix, the post-commit R3 check, the colocated doc location, and whether the worktree `.gitignore` edit is committed or dropped. Checks L1 should run once after integration: the lesson's own `sources-census.sh validate` and `mutants.py` for the C1 count.
