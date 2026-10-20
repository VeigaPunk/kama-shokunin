# BoundaryOwners — round 15 falsification (boundary attack, read-only)

Root: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Attack: no credential, routing, model-eval or service scope absorbed; PROVINCE unchanged. Scope: final candidate files under the root. No edits except this report. No tests, gates, runners, checks, builds or classifier runs.

## Verdict

**PASS with one disclosed-incident finding (F1) and one low-severity naming overlap (F2).** No boundary absorption found in the committed or new round-15 candidate. PROVINCE.md is byte-identical to HEAD.

| Check | Result | Evidence |
|---|---|---|
| PROVINCE unchanged | PASS | `git diff --quiet HEAD -- PROVINCE.md` clean; `sha256sum` = `a7728760f777573f9a4184df83efadc37fddc29159521c3ec48b11472579c0c6` for both HEAD blob and working file; 53 lines. |
| Sibling-owned province docs untouched | PASS | `git status --short` over `registry/`, `tools/`, `tests/ollama-evidence/`, `corpus/knowledge/{consumer-registry,cross-lane-scope,listener-census,snapshot-history,gguf-runtime-compatibility-boundary,served-identity-crosswalk}.md` is empty. `git diff HEAD -- corpus/knowledge/cross-lane-scope.md` is 0 lines. |
| Modified tracked files | PASS (scope) | 8 files: `.ufo/waves/round-14/measure.py` (+2 lines, the guard only), `LOG.md`, `SCORECARD.md`, `SKILL.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md` (S012 used-by cell extended, S034 row added), `corpus/knowledge/ollama-evidence-replay.md` (appended correction). New: `corpus/lessons/round-15.md`, `tests/ollama-corpus-guard/`, `.ufo/waves/round-15/`. |
| Credential / auth scope | PASS | No `agent.db`, `~/.omp` credential, `auth` or key read in any round-15 product. Only hits are prohibitions (`build/advice/R2Partial.md:42`, `HostSafety.md:22`, `SiblingBoundary.md:122`) and the RULES.md precondition string in spec/dispatch JSON (`falsify/spec.json:2`, `build/spec.json:2`), which records a read gate, not a read. Harness child env is a fixed five-key env (`measure.py:199-208`, `check.py:312-319`; HOME/TMPDIR confined to the fixture dir). Classifier opens only `--tags`/`--ps` (`tools/kama-ollama-evidence.py` header line 9: never reads environment, config or default locations). |
| Routing / dispatch scope | PASS | No `model`/`route`/`provider` keys in `build/dispatch.json`, `build/validation.json`, `falsify/dispatch.json` or `falsify/validation*.json` (grep of `"model"`, `"route*"`, `"provider"` returned nothing). Lesson states "No per-task model, route mutation" (`corpus/lessons/round-15.md`, LOG round-15 block). The 64-seat refusal (`build/provider-failures.json`, `SiblingBoundary.md:37`) is handed to kumitate as evidence, not repaired by kama. |
| Model-eval scope | PASS | Guard verdicts are described as test-contract results only: `SKILL.md` ("0 clean test contract ... neither means serving readiness"); `knowledge/ollama-evidence-replay.md:245` "Not a quality or routing verdict. Whether the model is good is kengaku's". No accuracy, battery, judge or score is added. Original 51-case corpus and its receipt are unchanged (`corpus/lessons/round-15.md` lines 7-9). |
| Service scope | PASS | No `systemctl`, `systemd`, restart, `pacman`, `sudo` or unit edit in any round-15 product. `corpus/lessons/round-15.md` states "No authorized serving runtime was sampled or restored" and keeps service restoration as a frontier gap. `PROVINCE.md:27-29` (restoration is operator-owned) is not contradicted. |
| Write boundary (`~/.config`, `~/.omp`, systemd) | PASS | No write path under those roots in `measure.py`, `check.py`, classifier, or the frozen snapshot. `check.py` writes only `tempfile.TemporaryDirectory` fixtures (`check.py:630`) and the launcher/wrapper inside them. `measure.py` writes only its own `tempfile` root. |
| Frozen baseline integrity | PASS | `.ufo/waves/round-15/frozen/measure-before.py` sha256 `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d` matches `frozen/manifest.json` and `git show 6e348e2:.ufo/waves/round-14/measure.py`. Working `measure.py` differs from the baseline only by the 2-line duplicate guard (`git diff -U0`). |

## Findings

### F1 — Session-transcript exposure by search (disclosed; PROHIBITED-access class, no absorption) — severity: medium (process)

- `build/advice/HostSafety.md:99-103`: a repo-wide grep for `resume_continuity` matched a line inside `.ufo/interactive-sessions/20261015T050057Z/*.jsonl` (a session transcript). The sentinel states it did not read the file beyond the grep hit snippet, and recommends excluding `.ufo/interactive-sessions/`.
- `build/advice/SiblingBoundary.md:121`: an early `glob` for `.ufo/**/SiblingBoundary*` ran with gitignore disabled; it listed directory names including `.ufo/interactive-sessions/`, opened no content, matched nothing.
- `corpus/lessons/round-15.md:94-99` discloses the grep hit and states "no additional file open, host database/credential access or write".
- My check: `grep -rln "20261015T050057Z|resume_continuity|interactive-sessions"` over the repo finds the session-id string or `resume_continuity` only in the disclosure lines above and in pre-existing, non-round-15 files (`.gitignore`, `plans/`, `.ufo/round-5/`, `considerthese/`). No transcript content appears in any round-15 product, so no session data is absorbed into evidence.
- Conclusion: the prohibition was breached once by incidental search hit and was disclosed in the candidate itself. It is not absorbed into any deliverable. Remediation is process only: the lane must exclude `.ufo/interactive-sessions/` from broad greps. Nothing for L1 to change in code.

### F2 — "calibration" term overlap with kengaku vocabulary (naming only) — severity: low

- Root `AXES.md:15` defines `calibration` as kama's fleet self-assessment axis ("gaps named honestly, confidence graded, overreach caught").
- `corpus/knowledge/cross-lane-scope.md:27` gives kengaku "task batteries, scoring, calibration, and quality claims".
- Round-15 text uses `calibration` only in the AXES.md sense (`corpus/lessons/round-15.md:6-7`, SCORECARD "C1 calibration (lowest7 vs operability8)"). `build/advice/SiblingBoundary.md:62` already states this. The round-15 additions contain no judge-calibration, accuracy or score claim, so no scope is absorbed. Only the shared word is a risk for future readers.
- No change required for this round. A later round that writes a judge or accuracy calibration in kama would be absorption.

### F3 — Fleet-level config read outside lane root (informational)

- `SCORECARD.md:226,285,342` and `build/advice/TrendMap.md:9` cite `../shokunin.conf` (the kama axis row). That is a fleet file outside the lane root, read for axis assignment. It is not credential material and no write occurs. Listed only so the reading is recorded; nothing to repair.

## Tooling

No tools installed or updated. Pacman not used (operator pause honoured; `pacman` not invoked). No `uv`, `npm`, `cargo` or binary install.

## Commands run (all read-only; no checks executed)

- `git status --short`, `git diff --stat`, `git diff HEAD -- <files>`, `git diff --quiet HEAD -- PROVINCE.md`, `git log --oneline -3 -- PROVINCE.md`, `git show 6e348e2:.ufo/waves/round-14/measure.py`, `git hash-object`.
- `sha256sum` on PROVINCE.md, frozen baseline, manifest and HEAD blobs.
- `grep`/`glob`/`read` over the root for boundary keywords, dispatch model/route keys, and session-id strings.
- No runner, classifier, `check.py`, selftest, test, build, lint, formatter, network call or service command was run.
