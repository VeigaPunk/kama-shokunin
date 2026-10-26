# U9Cannot report: `CANNOT-ANSWER.md` cited at served-model-id-resolution.md:46

**Verdict: the file never existed in the lane or the fleet repo; it is a shokuknow campaign artifact, `/home/vgpnk/Projects/shokuknow/lanes/kama/round2/CANNOT-ANSWER.md` (item 1, lines 5-14), copied into the lane entry in round 34 together with its pointer. Proposed replacement is in `.ufo/waves/round-44/w1/out/U9Cannot/proposal.md`.**

## Evidence
1. Lane (`git -C kama-shokunin log --all --name-only --format=%h -- '*CANNOT-ANSWER*'`): no output, so no commit ever added or changed a path with that name. `find` of the lane tree for `*CANNOT*`: none. The string appears only inside text: `corpus/knowledge/served-model-id-resolution.md:46`; its round-34 sources `.ufo/waves/round-34/assimilation/served-model-id-resolution.md:46` and the two `.../validate/corpus/knowledge/...` copies; round-35 seat logs (`ScoutProbeEntry.md:134`, `ReviewC2Ground.md:22,71`, which already noted the file is missing); `corpus/lessons/round-43.md:113`; `corpus/lessons/round-43-verifier-spotcheck.md`.
2. Lane history `git log --all -S CANNOT-ANSWER -- corpus/knowledge/served-model-id-resolution.md`: first touches `dfa18324`/`01d0e985` (2026-10-24, round-34 staging) and `29f9d1e1` "round-34: capability-repertoire census, widened instrument registry gate, alias-theme assimilation (2 entries, 5 rows)". No later commit changed the paragraph.
3. Fleet repo: `git -C /home/vgpnk/Projects/shokunin log --all --name-only --format=%h -- '*CANNOT-ANSWER*'` prints nothing (0 lines): no path with that name was ever committed in the fleet repo. `log --all -S CANNOT-ANSWER` returns 159 commits, all text mentions in reports/manifests (0 within `kama-shokunin`). At `b0fd7b7f`, `git grep CANNOT-ANSWER` hits only `.ufo/reports/round-43/kama.md` (line 96, reporting this same defect) and `MANIFEST.json`.
4. shokuknow (read-only): `lanes/kama/CANNOT-ANSWER.md` and `lanes/kama/round2..round16/CANNOT-ANSWER.md` exist (12 tracked: top level and rounds 2-12 modified in the working tree; rounds 13-16 untracked). `grep` for `EngineDeadError` finds only `lanes/kama/round2/CANNOT-ANSWER.md`. Its lines 5-14 (committed version at `d9583b5a` is md5-identical to the working tree for those lines) carry the wording the lane paragraph reuses: handler returns 503 on `EngineDeadError`; "wave-1 engine-arguments row" records the chat route's 503 admission rejection; "The lane holds the handler as S004, whose anchor is the same source block". Its "smallest next step" was to fold the two 503 semantics into `runtime-health-surface-matrix.md` and extend S004's `teaches` cell.
5. The gap was later closed in the lane: `corpus/SOURCES.md:213` row S327 (vLLM engine args v0.32.0, `--max-num-queued-reqs` rejects with HTTP 503) targets `corpus/knowledge/endpoint-health-probe-conventions.md` ("A 503 can be an admission rejection"); S004 stays in `runtime-health-surface-matrix.md:15` ("503 only on `EngineDeadError`").

## Related defects found (not fixed)
- Line 40 "the wave-1 vLLM engine-arguments row" also points at a shokuknow round-1 artifact, not a lane row.
- Line 41 says the *chat route* returns the admission 503 and line 44 says S004's anchor is "the same source block": S327 does not name a route and is a different page from S004. The proposal drops both.
- Heading line 37 "could not close" is stale given the S327 entry.

## Commands
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --all --oneline -S CANNOT-ANSWER`; `... log --all --name-only --format=%h -- '*CANNOT-ANSWER*'`; `git -C /home/vgpnk/Projects/shokunin log --all -S CANNOT-ANSWER`; `git -C .../shokuknow ls-files | grep -i cannot`; `grep -rIl CANNOT-ANSWER` over lane and shokuknow; `find ... -iname '*CANNOT*'`. All read-only; exit 0. No tools installed, no scratch kept beyond an empty dir.

Wrote:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/U9Cannot.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/U9Cannot/proposal.md
