VERDICT: confirm — round 17 rewrote no lane history text; the only doc deletion is the sanctioned SHONEN.md pointer extension, plus one declared, frozen-copy-mitigated in-place edit to `.ufo/waves/round-13/measure.py` (code, not history text), fully evidenced below.

# Falsify advice — AppendOnlyDocs (round 17, seat KamaR17.AppendOnlyDocs)

Attacked: the append-only/history-preservation discipline of the round-17 landing — every deleted line between round start `cff9e62` and lane commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3` in corpus/, SKILL.md, SCORECARD.md, LOG.md, PROVINCE.md, SHONEN.md, README files, and every other path outside tools/tests code; plus the "frozen pre-round copies" provenance claim.

## 1. Commit topology — no history rewrite at the git layer

- `git merge-base --is-ancestor cff9e62 54a2926…` → exit 0 (IS_ANCESTOR).
- `git rev-parse 54a29268…^` = `cff9e62f05aa7cfb9059444f62eb787100719713` = `git rev-parse cff9e62` — the round is ONE linear commit whose parent is exactly the round-start commit. `git log --oneline cff9e62..54a2926` shows exactly that commit ("round-17: graded check.py fields with fault controls and mutant grid; … jj lane hygiene").
- `git diff --name-status cff9e62 54a2926` → 187 entries, **all `A` or `M`**; no `D`, no `R` — no file deleted or renamed anywhere in the round.

## 2. Deletion inventory (numstat, all 187 files)

`git diff --numstat cff9e62 54a2926` — files with deletions > 0:

| path | +/− | class |
|---|---|---|
| `.ufo/waves/round-13/measure.py` | 158/8 | wave tool code — **outside tools/tests, reported in §5** |
| `PROVINCE.md` | 12/1 | numstat artifact — byte-proven pure insertion (§4) |
| `SKILL.md` | 31/1 | numstat artifact — byte-proven pure insertion (§4) |
| `SHONEN.md` | 1/1 | pointer extension only (§3) — sanctioned |
| `tests/llamacpp-live/check-receipt.py` | 274/16 | tests code (v1→v2), expected churn |
| `tests/probe-verdicts/check.py` | 182/16 | tests code, expected churn |
| `tools/kama-llamacpp-live.py` | 477/132 | tools code (v1→v2), expected churn |

Everything else — `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`, `corpus/knowledge/*.md`, `corpus/lessons/round-17.md` (new), `SCORECARD.md`, `LOG.md`, `AGENTS.md`, `.gitignore`, all `.ufo/waves/round-17/**` — has **0 deletions**. Verified by `git diff cff9e62 54a2926 -- corpus/ SCORECARD.md LOG.md AGENTS.md .gitignore | grep -c '^-[^-]'` → `0` (grep exit 1 = no match). Root `README.md` is absent from the 187-file diff entirely (untouched); tracked READMEs at 54a2926 are `README.md`, `corpus/README.md`, sources copies and wave artifacts — only `corpus/README.md` changed, +17/−0.

## 3. SHONEN.md — the sanctioned pointer extension

Old line 8 (656 chars) is a **strict prefix** of new line 8 (1046 chars); `n.startswith(o)` = True. Appended 390 chars: `"... Round 17 adds graded v2 receipts .ufo/waves/round-17/live/receipt-{1,2,3}.json (11/11 checks each …) and tests/llamacpp-live/controls.py (8 bad fake-server shapes rejected, frozen pair accepted 6); still a lane-owned control, no non-author mark."` — pure append of a round-17 evidence pointer; no prior word altered. Matches "Deletions in docs must be justified (SHONEN pointer extension only)".

## 4. PROVINCE.md / SKILL.md — numstat's "1 deletion" is hunk alignment, not rewriting

difflib over both blobs classifies each as a **single insert block, zero replace/delete blocks**, and reconstructing the old file from the equal blocks reproduces it byte-for-byte (`old == equal-blocks reconstruction: True` for both).

- PROVINCE.md: 12 lines inserted before EOF; the boundary line `"the cache persist on the host; removal is the operator's call."` is **byte-identical** old vs new (git's Myers pairing displayed it as −/+ in the summarized diff; the underlying bytes are equal).
- SKILL.md: 31 lines inserted after old line 553; anchor `"router catalogs, sleeping servers and Ollama."` present at line 553 in both blobs, byte-identical.

**No history text was modified, moved, or deleted in either file.**

## 5. `.ufo/waves/round-13/measure.py` — the one real deletion outside tools/tests (flag for integrator)

Round 17 edited a **prior round's wave artifact in place** (8 deleted lines, old-file numbering):

- L39 docstring `failure is probe_error, never clean.` → extended with the new `worktree_not_at_measured_revision` semantics
- L51 `KQ16 row, and altered pinned snapshot.  A green selftest is gate` → replaced by live-sandbox selftest description
- L55–57 `2 snapshot_tampered; 3 probe_error (unmeasured).  Evaluation modes …` ×3 → replaced
- L455 `and worktree_matches_head` and L457 `return finish(result, 'clean' if clean else 'documentation_mismatch', observations)` → replaced by exit-4 could-not-evaluate branch
- L841 `'selftest_scope': 'frozen construction and gate self-consistency only; …'` → reworded

Assessment: this is gate **code**, not lane history text; the change is declared in the round claims ("round-13 gate exit 4") and in the new SKILL.md row "Round-13 live gate exit 4 | gate: `python3 .ufo/waves/round-13/measure.py --quality corpus/QUALITY.md` | adds 4 could-…". Mitigation verified: pre-edit bytes are preserved at `.ufo/waves/round-17/frozen/round-13_measure.py`, sha256 `2399d64dcde4…` identical computed-from-`cff9e62` blob vs frozen file vs `.ufo/waves/round-17/frozen/manifest.json` (`"source_commit": "cff9e62f05aa…"`). Advice: acceptable, but note the lane's append-only norm technically applies to wave artifacts; the declared frozen copy is what keeps this honest — future rounds should keep doing exactly this.

## 6. Frozen-copy provenance — all five verified byte-identical

Computed sha256 of `git show cff9e62:<src>` vs `git show 54a2926:<frozen>` — all True: `round-13_measure.py` `2399d64dcde4`, `tests_probe-verdicts_check.py` `b853576edd54`, `tests_llamacpp-live_check-receipt.py` `6b9576a13dde`, `tools_kama-llamacpp-live.py` `b8c5e8d40259`, `tools_kama-probe.sh` `36b64978ee3a` (last one's source unchanged in the round; copy still exact). Manifest hashes match.

## 7. tests/tools deletions (in-scope-expected, code only)

The 164 deleted lines in `tests/**` and `tools/kama-llamacpp-live.py` are v1→v2 code churn: v1 schema validator bodies (`REQUIRED_CHECKS`, `if receipt.get("schema") != RECEIPT_SCHEMA`), old teardown/killpg/log-tail logic, and superseded docstrings ("Receipt schema: `kama-llamacpp-live/v1`. Only argv is recorded…"). No lane-history or corpus text hides among them.

## Commands run (all read-only git in the lane; exit codes)

1. `git -C <lane> merge-base --is-ancestor cff9e62 54a2926… && echo IS_ANCESTOR` — IS_ANCESTOR, exit 0
2. `git -C <lane> log --oneline --no-decorate cff9e62..54a2926…` — 1 commit, exit 0
3. `git -C <lane> diff --numstat cff9e62 54a2926…` — 187 files, exit 0
4. `git -C <lane> diff --name-status cff9e62 54a2926…` — all A/M, exit 0
5. `git -C <lane> rev-parse HEAD` / `rev-parse 54a2926…^` / `rev-parse cff9e62` — equal to `cff9e62f05aa…`, exit 0
6. `git -C <lane> diff cff9e62 54a2926… -- .ufo/waves/round-13/measure.py` and `-- PROVINCE.md SHONEN.md SKILL.md` and `-- .gitignore AGENTS.md` — exit 0
7. `git -C <lane> diff cff9e62 54a2926… -- corpus/ SCORECARD.md LOG.md AGENTS.md .gitignore | grep -c '^-[^-]'` — `0`, grep exit 1 (no matches)
8. `git -C <lane> ls-tree -r --name-only 54a2926… | grep -i readme` — 9 tracked READMEs, exit 0
9. `git -C <lane> diff -U0 … -- tests/probe-verdicts/check.py tests/llamacpp-live/check-receipt.py | grep '^-[^-]'` and `-- tools/kama-llamacpp-live.py | grep '^-[^-]'` — exit 0
10. Python (eval kernel, subprocess `git show`) byte-exact blob diffs, prefix test, equal-block reconstruction, frozen-hash equality — all as reported, exit 0

No lane tools/gates were executed → no clone was needed; no lane file written except this Report; no `jj` invocation.

## Limitations

- Git-layer only: per contract I did not run `jj`, so a jj-side operation (e.g. abandon/restore outside git refs) is not directly ruled out; however the working-copy parent chain and the single-commit linear landing leave no room for rewritten text between `cff9e62` and `54a2926` at the git backend jj uses.
- numstat counts 1 deletion each for PROVINCE.md/SKILL.md where byte analysis proves pure insertion (Myers hunk pairing); the byte-level result is authoritative.
- Root `README.md` checked via the tracked-tree diff only (absent = untouched); untracked worktree files are out of scope for a commit-range audit.

## Installs

None.
