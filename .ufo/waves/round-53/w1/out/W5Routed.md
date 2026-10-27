# W5Routed — round-53 Errata draft (answers the round-52 closure §6)

**Verdict: the `## Errata` draft answers all six round-52 closure items from committed bytes — R1 is closed by S509 (anchor re-checked in the round-53 text copy at lines 401 / 480 / 488–489 / 491), R2 narrows the libraries (8 archive libraries byte-equal in `/proc/<pid>/mem` across 3/3 runs) and half-narrows the download observation while the model, the host-install memfd, `vm.memfd_noexec=2` and round-50's three stay open, R3's four C2 limits all carry with the build answering none of them, R4 carries because no tool exists at HEAD, and the `ed135b3c` operator item is now filed as two fleet L0 rows and still unanswered.** I changed no lane byte: my only writes are the two files named in §1, and the modified files `git status --porcelain` shows in the lane tree (`SKILL.md`, `corpus/QUALITY.md`, `tools/kama-*.py`, `measured/*.out`, `registry/hexrun-ledger.tsv`, the new `integration/` and `hexrun-evidence/` trees) are the L1's integration in progress, not this seat's. The section is a draft for the L1 to append after `## Gate`.

## 1. Deliverable

- `.ufo/waves/round-53/w1/out/W5Routed/errata.md` — the `## Errata` section, paste-ready, one row per closure item plus per-item detail, every fact carrying `file:line`.

Method: read-only inspection of committed bytes at the build `c22602bd8d83ab26349d1087e916ca537ee4f9d1` (HEAD `bc8e6e7f`; `git log c22602bd..HEAD -- corpus/lessons/round-53.md` is empty, so the lesson is the build's text). I ran **no** frozen counter, started **no** server, and re-ran nothing the lane had already measured — the ticket forbids replaying work to decorate a report, and the counters are the L1's evidence, not mine.

## 2. Closure items, decisions and the bytes behind them

| Item | Closure line | Verdict in the draft | Primary evidence (lane-relative) |
|---|---|---|---|
| R1 S505 anchor → S509 | `corpus/lessons/round-52-verifier-spotcheck.md:134` | closed; S505 and round-52 lesson text stand as filed (append-only), decision unchanged (reject) | `corpus/SOURCES.md:258` (S505 "lines 422–439"), `:262` (S509), `corpus/lessons/round-52.md:34` ("line 431"), `.ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909` |
| R2 C1 carried limits | `…:135-140` | libraries **narrowed**; unobserved download **half narrowed**; host-install memfd, model-by-path, `vm.memfd_noexec=2` **stay**, and round-50's three stay; **two new limits named** | `tools/round53-replay-code-audit.py:36-50,444-452`; `tools/kama-live-replay.py:74-86,305-338`; `tools/kama-llamacpp-live.py:774-834`; `measured/c1-build.out:3,6`; `controls/base.c1.out:3` |
| R3 C2 limits (4) | `…:141-145` | all four carried; the build answers none | `SCORECARD.md:3016` (K4Cheat, L2Slice, M5Fixtures), `:3007` (K7Calib), `:3021` (the plan); empty `git log 4229ea1b..c22602bd -- tools/round52-append-restore-check.py` |
| R4 seat-report immutability | `…:146` | carried; no tool at HEAD | `ls tools/seat-report-immutability.py` → exit 2; `git show --stat c22602bd` (only two `tools/` files); `SCORECARD.md:3021` |
| Operator `ed135b3c` | `…:147` | **filed** as L0 by the lane, unanswered | fleet `.ufo/l0-questions.md:184` (`ee9f7341`), `:185` (`d2a6c59a`); `git show --stat 33b167ec` / `ed135b3c`; `LOG.md:2358,2362,2365-2369` |
| Operator carried L0s | `…:148` | unchanged, unanswered | fleet `.ufo/l0-questions.md:145,162,166,169,176`; only two `L0 ANSWER` lines in the file (52, 53) |
| Operator promotion | `…:149-153` | unchanged; four `[~]`, no `[x]`, `SHONEN.md` untouched | `SHONEN.md:5,7,9,11`; empty `git log 4229ea1b..HEAD -- SHONEN.md` |

## 3. Evidence log (commands, outputs, exit codes)

All commands ran read-only from the lane root or the fleet root; nothing was written outside my out dir.

| Command | Output | Exit |
|---|---|---|
| `git rev-parse HEAD`; `git log --oneline -12` | HEAD `bc8e6e7f…`; build `c22602bd`, freeze `d01b2b6d`, base `4229ea1b` in expected order | 0 |
| `git show --stat c22602bd` | 12 files, 2980 insertions, 2 deletions; `tools/kama-live-replay.py +93`, `tools/kama-llamacpp-live.py +105`; no round-52 counter, no immutability tool | 0 |
| `git log --oneline 4229ea1b..c22602bd -- tools/round52-append-restore-check.py tools/round52-replay-memfd-audit.py tools/kama-probe.sh tools/round51-append-audit-v6-check.py` | no output (round-52 C2/A-corr instruments and the probe are byte-identical) | 0 |
| `ls tools/seat-report-immutability.py` | "No such file" | 2 |
| `grep -n "get_executable_path\|ggml_backend_load_best\|GGML_BACKEND_DIR\|default search paths" .ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909` | 401, 480, 488, 489, 491 (comment), 492 (`push_back(get_executable_path())`) | 0 |
| `git show ed135b3c -- LOG.md` (and `--stat 33b167ec`) | revert: `LOG.md | 8 +-------`; origin: `LOG.md | 8 +++++++-` — `ed135b3c` deleted the entry, `33b167ec` added it | 0 |
| `git blame -L 184,185 --porcelain .ufo/l0-questions.md` (fleet) | 184 ← `ee9f7341…` (kama-shokunin, 03:12:25), 185 ← `d2a6c59a…` (03:12:42) | 0 |
| `grep -c "L0 ANSWER" .ufo/l0-questions.md` (fleet) | `2` (lines 52–53 only) | 0 |
| `grep -vc '^#' registry/cited-path-corrections.tsv` | `16` = header + **15 data rows** (10 SCORECARD + 5 SKILL; 14 disclosure + 1 `fixed` at `:27`) | 0 |
| `grep -n "code b1\|coderuns" measured/c1-build.out; … base.c1.out` | `c1-build.out:3` `code=1 … coderuns=3/3 met=True`; `:6` "8 archive files (8 executable ranges) byte-equal …, 13 root-owned host files"; `base.c1.out:3` `code=0 … coderuns=0/3 met=False` | 0 |
| `grep -n "fixture=1 lane" measured/c2-build.out base.c2.out` | build `:3` `cited=682 unresolved=14 disclosed=14 … met=True`; base `:3` `cited=679 unresolved=16 disclosed=0 … met=False` | 0 |
| `sed -n '3018,3022p' SCORECARD.md` | `:3018` `### Planned (round 53)`, `:3020` item 1 (per-mapping identity "and for the model"), `:3021` item 2 | 0 |
| `sed -n '140,185p' tools/round53-cited-path-check.py` | `citations()` at 147, fence toggle at 152/154 — fences only, no HTML-comment rule | 0 |
| `pgrep -af llama-server` | two processes, both peer K2Design's replay under `/fast/scratch/hyaku/kama-r53/K2Design/…`; **none mine** (this seat started no server) | 0 |

## 4. What I add beyond the six items (calibration notes for the L1)

1. **The ticket's "14 ledger rows" is `disclosed=14`, not the row count.** `registry/cited-path-corrections.tsv` holds **15 data rows**: 14 disclosure rows plus one `fixed` row (`:27`, `tests/report-audit/…` → `tests/report-audit/`). The second SKILL in-place fix (`SKILL.md:113`, now `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`) deliberately has **no row** — the ledger's own comment says an absolute path is not a lane citation (`:8-11`). Worse to state a wrong row count in the lesson than to state both numbers.
2. **The C1 build adds limits nobody has written down yet.** (a) 13 root-owned host mappings per run are accepted on uid 0 + maps inode + not-writable, with **no reference digest** (`tools/round53-replay-code-audit.py:444-452`; `c1-build.out:6`) — a root-owned library replaced on disk is invisible to the `code` leg; (b) the `code` leg only reads a server it started, so a host at Yama `ptrace_scope` 2–3 cannot run it at all (S507, `corpus/SOURCES.md:260`). Both are in the draft's R2 section; the lesson's Claims/Gate as landed do not mention them.
3. **"Eight scenarios" is not a mutant-kill number.** S2 of the round-52 plan (`SCORECARD.md:3021`) asked for fixtures that kill the six surviving tool mutants. The build ships eight constructed scenarios that all pass at base and build (`c2-build.out:3-11`), but no mutation study of `tools/round53-cited-path-check.py` is committed at the build or HEAD; seats M5Ctr/M6Ledger are dispatched in `bc8e6e7f:.ufo/waves/round-53/w1/spec.json` and their results are not in the tree. R3 therefore stays "carried" rather than "closed", and the Errata says so instead of counting fixtures as kills.
4. **L0 row 184 contains its own error; row 185 fixes it and I verified the direction.** 184 says the five LOG lines are ones "that commit `ed135b3c` added and a `Revert` commit withdrew" — `ed135b3c` *is* the revert (`Revert "HOURS.md: craft-hours ledger opened (§Craft-hours canon)"`, `LOG.md | 8 +-------`), and `33b167ec` added them (`LOG.md | 8 +++++++-`). The draft cites both rows and the git evidence, so a later closure reading only 184 does not inherit the error.
5. **The new C2 parser is fence-only by design, and that is stricter, not weaker, for citations.** A backtick citation written inside an HTML comment is still counted (`tools/round53-cited-path-check.py:147-157`); the round-52 K4Cheat hole (a *restored block* hidden in a comment) is a different instrument and is untouched in the build. The draft keeps those two facts apart so a later round does not read "HTML comment" as closed.

## 5. Known limits of this draft

- Facts are pinned to `c22602bd`/HEAD `bc8e6e7f`; the wave's own results (M5Ctr, M6Ledger, X9Immut, K8Routed) are not in the tree when I read it, so R3's mutant-kill and R4's tool remain "not shown", not "failed".
- The operator rows live in the **fleet** repo; the lane cannot freeze them. If the operator answers `ed135b3c`, the Errata's "unanswered" sentence ages — the L1 should append the answer as a dated row rather than rewrite that sentence.
- I did not run either counter (the lane's receipts stand on their own); every "met=True" I quote is quoted from `measured/*.out`, never re-measured by me. Nothing in this report is a claim about the counters' current behaviour beyond what their committed bytes and receipts show.
- No install or upgrade was needed; no tool was added to `~/.local/bin` or any PATH directory.

## 6. Cleanup

Scratch `/fast/scratch/hyaku/kama-r53/W5Routed` was created and left empty (no clone needed: all reads were of committed bytes in the lane and fleet trees); it is removed. No llama-server was started by this seat.
