# ReviewProbe — round 13 static review of measure.py (final, with dispositions)

Reviewer: KamaR13.ReviewProbe (leaf reviewer, read-only). Root: /home/vgpnk/Projects/shokunin/kama-shokunin.
Status: **static review complete; no blocking defect. Five low items were routed to KamaR13.Measure; Measure and L1 dispositioned them as documented limits, not new enforcement (see table).**

## Scope and method

- Read-only static inspection only. I executed nothing: no `measure.py`, no `--selftest`, no git commands, no `sha256sum`, no build/test/lint.
- First full static pass: final `measure.py` at 905 lines, `frozen/expected.json`, and the KQ16 row of `corpus/QUALITY.md`, `frozen/after/corpus/QUALITY.md` and `frozen/before/corpus/QUALITY.md` (grep and raw line reads).
- Docs-only follow-up: Measure reports the file is now 39463 bytes (910 lines), sha256 `2399d64d…918fd6`. I re-read the module docstring (lines 1–73) and the `LIMITS` block (lines 116–153) to confirm the documented updates. **I did not re-read the function bodies after the docs-only change**; I rely on Measure's statement that no behavior changed, and L1 owns the single post-integration run.
- Tools installed or updated: none.

## Evidence (static, location-cited, first pass)

| Claim | Location |
|---|---|
| Exit mapping `clean 0 / documentation_mismatch 1 / snapshot_tampered 2 / probe_error 3` | `measure.py` `FINDINGS` |
| Admit-cell-only search; exactly one KQ16 row; masks fences and HTML comments; 4-cell layout required | `kq16_line_indices`, `assess` |
| Forbidden phrase `distinct\s+non-?zero\s+exits?` searched in admit cell only | `MISTAKEN_RE`, `assess` |
| Contradiction checks: exit pair values, `comparison: git show`, `capture: git cat-file`, KQ15 formulation restated | `contradiction_problems` |
| Empty historical blob → GateError (probe_error); git failures → GateError | `historical_quality`, `git_read` |
| Frozen digest mismatch returns `snapshot_tampered` before any content check | `run_frozen` |
| Frozen role gating: before_is_pinned_start and before missing == DENOMINATOR enforced | `run_frozen` |
| Selftest: 10 real child CLI cases (`sys.executable -I -B`), expected exit + finding + missing | `run_selftest` |
| Live clean requires canonical non-symlink path, worktree == HEAD, pinned before, missing 2 | `run_live` |
| Manifest declares `kq15_line_sha256` for before and after | `frozen/expected.json` |
| Live KQ16 row (corpus/QUALITY.md:61) and frozen after row (frozen/after/corpus/QUALITY.md:61) read raw: text identical; admit cell contains `source_mismatch=1; snapshot_tampered=2; source_unavailable=2` and `capture: git show; comparison: git cat-file blob`; no `distinct nonzero exits`; four pipe-delimited cells | raw reads of those lines |

Static inference (not executed): by the code, the admit cell of the live/after KQ16 row yields `missing_assertions 0`, no contradictions, `content_clean true`. The before blob has no KQ16 row, so it yields `missing_assertions 2`. Byte identity and SHA-256 pins were not computed by me.

## Findings and dispositions

No blocking or high-severity findings.

| # | Finding (first pass) | Disposition (Measure / L1) |
|---|---|---|
| Low-1 | `expected.json` `kq15_line_sha256` pins not enforced by any code path. | Retained as informational metadata. Documented in `LIMITS` (line ~129): the whole before digest plus raw byte prefix implies KQ15 preservation. Verified in the docstring/LIMITS text. Not enforced. |
| Low-2 | Frozen mode records snapshot and `--quality` symlink flags without gating them; live mode fails on symlinked `--quality`. | Retained as documented limit (line ~130): containment plus SHA-256/byte pins are the frozen enforcement; live clean rejects non-canonical or symlinked `--quality`. |
| Low-3 | `splitlines()` vs `split('\n')` indexing risk with exotic separators inside masked regions. | Documented as out of scope (line ~131). Not changed. |
| Low-4 | `--help` prints argparse plaintext and exits 0, bypassing the one-JSON-object contract. | Docstring updated (lines 55–57) to exclude `--help`. No SystemExit catch or `add_help` override. Verified in docstring. |
| Low-5 | `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_NOSYSTEM` not forced. | Documented (line ~132): cat-file blob returns raw bytes; round-12 method remains the config-suppressing reference. |

## Verdict

**Static review: no blocking defect; all five low items accepted by L1 as documented limits, not as code changes.** The conditional verdict stands on the same two items as before:

- L1 runs `--selftest` and the frozen reproduction once after integration. Not run by me.
- L1 confirms the frozen SHA-256 pins and byte identity of `frozen/after` to `corpus/QUALITY.md` at commit time. Not computed by me.

## Limits

- No execution by this seat. Every statement is a static read with line citations; nothing here is an executed check.
- Function bodies were not re-read after the docs-only change; the post-change claim of no behavior change rests on Measure's statement and L1's run.
- Semantic truth of the KQ16 wording and the exit map is not verified here; it belongs to ReviewExit (fidelity.py precedence) and human review (KQ14).
