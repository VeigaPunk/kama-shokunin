<!-- Draft for corpus/lessons/round-53.md, to be appended after `## Gate`.
     Author: round-53 seat W5Routed (scribe). Facts checked against committed bytes at the
     build c22602bd8d83ab26349d1087e916ca537ee4f9d1 (lesson unchanged at HEAD bc8e6e7f);
     no frozen counter was re-run for this section. Paths are lane-root relative unless
     they name the fleet repo. -->

## Errata

Answers `corpus/lessons/round-52-verifier-spotcheck.md` §6 lines 134–153 (R1–R4, the operator item, the carried L0 rows, promotion). Each row was read out of committed bytes at the build `c22602bd8d83ab26349d1087e916ca537ee4f9d1`; none of the frozen counters was re-run for it.

| Round-52 closure item | State after round 53 | Evidence |
|---|---|---|
| R1 S505 anchor | closed by `S509`; S505 and the round-52 lesson text stand as filed (append-only) | `corpus/SOURCES.md:262`, `:258`; `corpus/lessons/round-52.md:34` |
| R2 C1 carried limits | the libraries narrowed (byte-compared in memory); the model, the host-install memfd, the unobserved download, `vm.memfd_noexec=2` and round-50's three stay open; two new limits are named | `tools/round53-replay-code-audit.py:36-50`; `tools/kama-live-replay.py:74-86`; `.ufo/waves/round-53/measured/c1-build.out:3,6` |
| R3 C2 limits | all four carry; the build answers none of the four, and the new C2 instrument inherits none of them | `SCORECARD.md:3016`, `:3021`; `tools/round53-cited-path-check.py:40-68` |
| R4 seat-report immutability | carried: no tool at HEAD; the wave dispatched a seat to draft one in its own out dir | `tools/` (no `*immutab*`), `SCORECARD.md:3021` |
| Operator: `ed135b3c` | filed as an L0 row (the gap the closure named) and a correction row; unanswered | fleet `.ufo/l0-questions.md:184-185` |
| Operator, carried L0s | unchanged and unanswered | fleet `.ufo/l0-questions.md:145,162,166,169,176` |
| Operator, promotion | unchanged: all four boxes `[~]`, `SHONEN.md` untouched | `SHONEN.md:5,7,9,11`; `git log 4229ea1b..HEAD -- SHONEN.md` empty |

### R1 — S505's anchor: closed by S509, S505 left as filed

The round-52 closure (R1, `corpus/lessons/round-52-verifier-spotcheck.md:134`) named three wrong numbers: S505's anchor "lines 422–439", the round-52 lesson's "line 431", and seat S5Ggml's "21 words".

- S505 still says "`ggml_backend_load_best`, lines 422–439 at tag b11909" — `corpus/SOURCES.md:258`, unchanged (the row is append-only; the decision is not rewritten).
- The round-52 lesson still says "(…, line 431)" — `corpus/lessons/round-52.md:34`, also history.
- S509 carries the correction: "`get_executable_path()` from line 401, `ggml_backend_load_best` from line 480, `GGML_BACKEND_DIR` lines 488–489, the quoted comment line 491, at tag b11909" — `corpus/SOURCES.md:262`.
- Re-checked in this round's committed text copy, `.ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909`: line 401 `static fs::path get_executable_path() {`, line 480 `static ggml_backend_reg_t ggml_backend_load_best(...)`, lines 488–489 `#ifdef GGML_BACKEND_DIR` / `search_paths.push_back(fs::u8path(GGML_BACKEND_DIR));`, line 491 `// default search paths: executable directory, current directory`, line 492 `search_paths.push_back(get_executable_path());`.
- The quote is seven words ("default search paths: executable directory, current directory"), as S509 states; the seat's 21 was wrong.
- The decision is unchanged: reject. S509's own cell says "the decision (reject) is unchanged" (`corpus/SOURCES.md:262`), and the source still shows a compiled `GGML_BACKEND_DIR` ahead of the executable directory and the cwd, so "needs cwd" stays too strong.

No counter grades anchors, so this closure is documentation-only; the round-52 C1 claim was never resting on it (the route was to the reject's location, not its verdict).

### R2 — C1's carried limits: the libraries narrowed, everything else open, two new

Round-52 closure `:135-140` carried four limits from round 52 plus three from round 50.

Narrowed by this round's build:

- **Libraries load by path (K2Design).** The live tool now records every executable file mapping of its server (`/proc/<pid>/maps` rows with `x` in `perms` and a `/`-rooted pathname other than `/memfd:`) with path, dev, inode, owner and the sha256 of the file *at that path only while the path is the mapped inode*; a `(deleted)` mapping is never opened (`tools/kama-llamacpp-live.py:774-834`). The replay hashes the archive members those mappings name from the archive stream and fails on `code-mapping:digest` / `not-a-member` / `foreign` / `unopened` / `no-archive-library`, reporting the verified set as `own_code` (`tools/kama-live-replay.py:305-338`). The counter adds the leg that matters: it reads each executable range of the server from `/proc/<pid>/mem` and compares the bytes with its own download of the archive at the mapping's file offset (`tools/round53-replay-code-audit.py:36-50`, memory opened at `:405`, host-file rule at `:444-452`). At the build, three of three runs read 8 archive libraries over 8 executable ranges byte-equal, `libllama-server-impl.so`, `libggml*.so*` and the chosen CPU backend `libggml-cpu-zen4.so` among them, plus 13 root-owned host files (`c1-build.out:3,6`). A library swapped at its path after the member check is now a miss, which is what the closure asked for.

Still open, each with the byte that says so:

- **A memfd filled from a host install.** `tools/kama-live-replay.py:74-75`: "The extracted tree still supplies the libraries (by path); a memfd filled from a byte-identical host install still matches." Nothing in the code leg covers the `/memfd:` image itself — the live tool skips `/memfd:` rows by construction (`tools/kama-llamacpp-live.py:792-793`), and the counter's memory comparison excludes them (`tools/round53-replay-code-audit.py:37-38`).
- **The model still loads by path.** `code_mappings()` records only mappings with `x` in their permissions (`tools/kama-llamacpp-live.py:792`) and the counter's required-name list has no model (`tools/round53-replay-code-audit.py:22-24`). `SCORECARD.md:3020` (Planned round 53, item 1) asked for "per-mapping identity … and for the model, read from `/proc/<pid>/maps` and `map_files`"; the build added the libraries and not the model, and `map_files` was rejected as the means (S508, `corpus/SOURCES.md:261`).
- **The download is not observed — open, half narrowed.** The libraries are now compared against the *counter's* own download, so the replay's unpacked file is no longer trusted for them (`tools/round53-replay-code-audit.py:38-41`). The memfd image's bytes still rest on the replay's own archive stream (round-52 sealed leg), and nothing witnesses that the replay read its archive rather than the host install.
- **`vm.memfd_noexec=2` hosts.** Unchanged; the replay's refusal path is the round-52 one, and this round's new row S507 records the sibling condition on the reading side: a host at Yama `ptrace_scope` 2 or 3 cannot run the counter's `code` leg at all (`corpus/SOURCES.md:260`).

Round-50 carried limits, all unchanged: probe PATH execution, model bytes rewritten after mapping, and kills during download or readiness (`corpus/lessons/round-52-verifier-spotcheck.md:140`). The build touched neither `tools/kama-probe.sh` nor the teardown leg (`git log 4229ea1b..c22602bd -- tools/kama-probe.sh` is empty; the counter states the leg is the round-50 one unchanged (`tools/round53-replay-code-audit.py:51`) and `c1-build.out:15` is its detail line).

Two limits this round *adds*, recorded here so they are not discovered by a later closure:

- **Root-owned host files are accepted on identity, not bytes.** 13 host mappings per run pass on uid 0 + the maps inode + not writable by the counter, with no reference digest (`tools/round53-replay-code-audit.py:444-452`; `c1-build.out:6`). That is deliberate — this host's btrfs/overlay root reports a `st_dev` different from the maps line — but a root-owned library replaced on disk is not caught by the `code` leg.
- **The `code` leg needs a descendant relationship.** It can only read a server it started (S507, `corpus/SOURCES.md:260`), so a third party verifying another process's server needs a different mechanism.

### R3 — C2's four round-52 limits: carried, and what this round did not do

Round-52 closure `:141-145` named four limits of the *round-52* C2 counter. `SCORECARD.md:3021` (Planned round 53, item 2) asked for three fixes. State at the build:

- **HTML-comment visibility (K4Cheat; `SCORECARD.md:3016`).** Carried. No visibility check was added: `git log 4229ea1b..c22602bd -- tools/round52-append-restore-check.py tools/round51-append-audit-v6-check.py` is empty, so the round-52 instrument is byte-identical. The *new* C2 counter does not inherit the hole because it does not audit restoration at all; conversely its parser counts a citation written inside an HTML comment (only ``` fences toggle, `tools/round53-cited-path-check.py:147-157`), which is stricter than the round-52 rule but answers a different question.
- **`exempt=` simpler than the tool's (L2Slice; `SCORECARD.md:3016`).** Carried, untouched — same empty `git log` range for the round-52 counter. Planned item 2's "make the C2 counter's `exempt=` rule the tool's (origin and not-gutted)" is not in the build.
- **Fixtures kill only 2 of 8 tool mutants (M5Fixtures; `SCORECARD.md:3016`, `:3021`).** Not shown. The new counter has its own eight constructed scenarios, each with a fixed verdict, and all eight pass at both base and build (`tools/round53-cited-path-check.py:62-68`; `c2-build.out:3-11`; `controls/base.c2.out:3`). But no mutant-kill study of the new counter is committed at the build or at HEAD; the wave dispatches seats M5Ctr (≥15 mutants of `tools/round53-cited-path-check.py`) and M6Ledger (one mutant per ledger row) in `bc8e6e7f:.ufo/waves/round-53/w1/spec.json`, and their results are not in the tree. Until one lands, "eight scenarios" is a count of fixtures, not of killed mutants.
- **`corr_lost` counts contract-graded lines only (K7Calib; `SCORECARD.md:3007`).** Carried; the round-52 counter is untouched, and the round-53 counter has no such leg.

### R4 — seat-report immutability: carried, no instrument

Round-52 closure `:146` recorded nine further in-place rewrites of committed seat reports and that `seat-report-immutability.py` was planned, not landed.

- At HEAD there is still no such tool: `tools/` holds no `*immutab*` file, and the round-53 build's stat lists only `tools/kama-live-replay.py` and `tools/kama-llamacpp-live.py` under `tools/` (`git show --stat c22602bd`).
- `SCORECARD.md:3021` still carries it as a plan ("land seat W3Mistakes' seat-report-immutability and cited-path-exists checks as lane instruments"); the cited-path half landed, the immutability half did not.
- What round 53 did do: dispatch seat X9Immut to turn `.ufo/waves/round-52/w1/out/W3Mistakes/seat-report-immutability.py` into a lane-ready tool **in that seat's out dir** (`bc8e6e7f:.ufo/waves/round-53/w1/spec.json`, item X9Immut: "Routed R4 (planned, not built)"). Nothing is integrated at the build, so this round's own reports are protected only by the prompt rule, not by a check.

### Operator item — `ed135b3c`: now filed, still unanswered

The round-52 closure's operator item (`:147`) said the lane had routed the ruling only in its report and "filed no L0 line". Round 53 filed it, twice, from the lane identity:

- fleet `.ufo/l0-questions.md:184` — the question (may withdrawn canon be kept as restored history; keep or remove, and if removed the A-corr counter needs a named revert exception), filed by fleet commit `ee9f7341bd98de0fcd85f6c01f689301589b27e9` ("round-53: kama L0 question (ed135b3c restored history)", 2026-10-27 03:12:25 −0300).
- fleet `.ufo/l0-questions.md:185` — a correction row replacing the first row's direction: "`ed135b3c` is itself the `Revert …` commit that deleted the five LOG.md lines; it did not add them", filed by `d2a6c59aaabcbde2d4a946c31d0276bb2c3d7887` (03:12:42 −0300). Row 184's wording ("that commit `ed135b3c` added and a `Revert` commit withdrew") was wrong in that sentence; the correction states the fact and leaves the question unchanged.
- The fact, re-checked here: `git show --stat 33b167ec` → `LOG.md | 8 +++++++-` (the entry added, 2026-10-13); `git show --stat ed135b3c` → `LOG.md | 8 +-------`, the revert; the round-52 restoration block names it as the deleting commit and holds five content lines — `LOG.md:2358` (heading), `:2362` ("Deleted by `ed135b3cb869`"), `:2365-2369` (the entry).
- Unanswered: neither row carries an `L0 ANSWER`, and the file's only ANSWER rows are lines 52–53 (kama round-11). Round 53 does not depend on either answer, as row 184 states.

### Operator, carried L0s — unchanged

All three remain open, with no `L0 ANSWER` on any row (the file's ANSWER rows are 52–53 only):

- planner seat under the policy-v2 validator — fleet `.ufo/l0-questions.md:162` (`kama | round-39`);
- the MISSION axes pair (MISSION.md says operability + freshness; the round prompt says operability + calibration — this round again claimed C1 on operability and C2 on calibration) — `:145` (`kama | round-35`);
- the parked lane worktree — `:166`, `:169`, `:176` (`kama | round-41..43`).

### Operator, promotion — unchanged

`SHONEN.md` has four `[~]` boxes and no `[x]` (`SHONEN.md:5,7,9,11`), and the file is unchanged this round (`git log 4229ea1b..HEAD -- SHONEN.md` empty). Final round-53 evidence for boxes 1, 2 and 4 exists or will exist in the measured receipts; promotion stays operator-owned and nothing here marks a box.
