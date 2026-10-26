# S9Qual — the eight held sentences, process-qualified (kama round 44, wave 1)

**Verdict: all eight sentences need the qualification and none can stand as written; all eight are qualified in one append-only patch (4 files, +170 lines, 0 lines rewritten, `git apply --check` exit 0, verifier exit 0), and none is marked "needs no change". Three consequences are left for the L1: the matrix's KQ6 clause no longer describes what the entry cites, its `recheck:` line no longer names the rows the entry rests on, and the two cited rows' `used-by` cells name none of the four entries that now cite them (F2–F4).**

## 1. Population and base

The list is the one the round-43 lesson files at `corpus/lessons/round-43.md:113` and that the outside closure carries forward (`corpus/lessons/round-43-verifier-spotcheck.md:96`, `:110` — "eight sentences needing the process qualification should be marked or corrected"); seat W1K02's crosswalk (`.ufo/waves/round-43/w1/out/W1K02.md` §2) gives the same eight with the qualification each one needs:

1. `corpus/knowledge/runtime-health-surface-matrix.md:8` (Claim)
2. `corpus/knowledge/runtime-health-surface-matrix.md:12` (table header)
3. `corpus/knowledge/runtime-health-surface-matrix.md:15` (vLLM row)
4. `corpus/knowledge/endpoint-health-probe-conventions.md:9-14` (the sentence at 12-14)
5. `corpus/knowledge/endpoint-health-probe-conventions.md:16-17` (the sentence at 16)
6. `corpus/knowledge/served-model-id-resolution.md:39-46`
7. `corpus/knowledge/engine-pin-watch.md:7-9`
8. `corpus/knowledge/engine-pin-watch.md:60-66` (the clause at 60-61)

Base check (assignment names lane commit `77d1bbf5`; the lane's HEAD is `098df344`):

```
git -C kama-shokunin log --oneline -3
  098df344 round-44: wave-1 spec and dispatch (v2, 65 seats), C1/C2 drafts, seat fragment checker
  77d1bbf5 round-44: freeze — preregistration, two counters, release-recheck draft tool, controls, census start
git merge-base --is-ancestor 77d1bbf5 HEAD            -> ancestor
git diff --stat 77d1bbf5 HEAD -- <the four files>     -> empty
```

The four files are byte-identical at both revisions, so every line number below holds at both (F5). The four files are also unmodified in the working tree: during this seat's run other wave-1 seats wrote `M SCORECARD.md`, `M SKILL.md`, `M corpus/SOURCES.md` (+2 lines, a new row S483 for `preload.py`), `M corpus/knowledge/runtime-health-surface-processes.md` (its `source:` line gains that row) and `M registry/hexrun-ledger.tsv`, while HEAD stayed at `098df344`; `git diff --stat -- <the four files>` is empty, so the patch's context lines are the committed ones. See F3 for what that uncommitted row means for this patch.

The facts the qualification rests on are the two rows the round-43 entry opened, re-read from their committed copies, not from prose: `S480` (release note, tier A) files "a `/health` endpoint (#58552)" under **Fast restart** in the bullet that names "the new `vllm preload` CLI launches the weight-cache daemon" (release `body` line 8, `.ufo/waves/round-43/c3/vllm-v0.31.0-release.json`); `S481` (pull request, tier C) reads "Add an HTTP `/health` endpoint to the weight cache daemon parent process." (`body` line 3) and "distinguish daemon startup from readiness" (line 5); `preload.py` at tag v0.31.0 registers `@app.get("/health", include_in_schema=False)` at `:73` and answers `Response(status_code=200 if state.is_ready else 503)` at `:75`, with `--weight-cache-health-port` defaulting to `None` at `:134-137` (lane copy `.ufo/waves/round-43/c3/vllm-v0.31.0-preload.py`). `S004` (`corpus/SOURCES.md:16`) remains the inference server's route. So: two `/health` routes, one product, two processes, two meanings, one opt-in.

## 2. The eight, sentence by sentence

| # | file:line | current text (verbatim; quoted and checked in the patch) | minimal qualified replacement (added clause(s) verbatim) | judgment |
|---|---|---|---|---|
| 1 | `runtime-health-surface-matrix.md:8` | "One `/health` URL shape does not carry one portable readiness meaning across llama.cpp, vLLM and SGLang — each engine's documented route semantics differ, and Ollama's opened pages document no dedicated health route at all." | "…nor even inside one product: … vLLM's v0.31.0 release files a `/health` item under the `vllm preload` weight-cache feature, in the same bullet that names the daemon the CLI launches (S480 — the release page does not say which process answers it), the pull request behind that item names the process it went into — the weight cache daemon's parent process (S481, community tier C) — …" | qualified: the thesis is engine-keyed while the finding is intra-product; the Claim is what later entries quote |
| 2 | `runtime-health-surface-matrix.md:12` | `\| Engine \| Documented revision \| Liveness route \| Readiness / loaded meaning \| Identity route (separate) \| Caveat \| S-id \|` | "Read that table as keyed on (engine, process, date read), not on the engine alone. Until a `Process` column exists, each data row carries this process value:" + a five-row process table (llama.cpp server / vLLM inference server only / SGLang server / Ollama server / n/a-Kubernetes) | qualified: seven columns, no process — the header cannot distinguish the two vLLM routes; no data row is rewritten |
| 3 | `runtime-health-surface-matrix.md:15` | cells "`GET /health` listed under Instrumentator APIs", "Render-only servers have no engine and return 200 unconditionally — a passing `/health` may not even reach an engine", "S002, S004" | liveness "+ — the inference server's route; v0.31.0 also lists a `/health` under the `vllm preload` weight-cache feature, which is a different process (S480, S481)"; caveat "+ and 'the vLLM `/health`' names two routes in two processes, so this row is read only together with its process value and the date it was read"; S-id "+ (inference server); S480, S481 (the second route's process)" | qualified: this is the row a reader acts on; the 200s mean opposite things |
| 4 | `endpoint-health-probe-conventions.md:12-14` | "Those are admission valves in the API server process, not a statement that the process is down." | "+ and they are not the whole vLLM 503 space: from v0.31.0 the `vllm preload` weight-cache supervisor answers its own `/health` with 503 until every expected target and draft rank reports, which is a third condition — not ready — on a route in a second process (S480, S481; the two-outcome handler at `preload.py:75`, …)" | qualified — nearest call to "no change": the sentence already says *whose* valves these are, but it closes the entry's enumeration ("That grading does not cover a different 503", line 9), so it must say the set is not complete |
| 5 | `endpoint-health-probe-conventions.md:16` | "A probe that maps every 503 to dead will call a saturated vLLM server dead." | "…and will call a weight-cache supervisor whose ranks are still loading dead — the same status code on a different process's `/health`. Which vLLM process answered therefore belongs in the probe's rule, not only which status came back: … (`--weight-cache-health-port`, default `None`, 'disabled by default' …), so a probe pointed at the inference server never sees it and a probe pointed at it reads a 200 as 'every daemon rank is up', not as 'the engine is alive' (S480, S481)." | qualified: the rule as written cannot be applied to a vLLM `/health` 503 without the process |
| 6 | `served-model-id-resolution.md:39-46` | "…The two routes therefore use the same status code for different conditions … The lane already holds that handler as S004 … so no new row was opened for it in this round; the observation is recorded in `CANNOT-ANSWER.md` for the next wave that touches that file." | "Three routes therefore use the same status code for different conditions … and two of the three are `/health` in two different processes: the inference server's, held as S004 … and — from vLLM v0.31.0 — the `vllm preload` weight-cache supervisor's, which answers 503 … and 200 after …, on a route that is opt-in (S480, S481). The observation is recorded in the lane, not deferred to a file outside it: `CANNOT-ANSWER.md`, which the superseded sentence named, exists nowhere in this lane's tree, and the third route is now held by the two rows at `corpus/SOURCES.md:233-234`." | qualified: two routes become three, and the dead pointer is named as dead instead of being silently replaced |
| 7 | `engine-pin-watch.md:7-9` | "Several kama entries are true only of one engine release. SGLang knowledge is pinned to v0.5.22 … vLLM knowledge to the v0.32.0 docs line …, and the llama.cpp lifecycle work to build b11755 (S038)." | "+ one vLLM entry is pinned elsewhere — to the v0.31.0 release and a merged pull request (S480, S481) — because what that entry states is a property of a process, not of a docs line. The ledger's `engine` column is unique … so a second vLLM pin of a different kind has no line in `registry/engine-pins.tsv` to sit on, … a pin that is current says nothing about which process answers a route: inside S481's own two commits the `/health` endpoint was moved to the `vllm preload` CLI before the pull request merged" | qualified: the pin list is per engine; one entry is pinned per process, and ownership moved inside the pull request |
| 8 | `engine-pin-watch.md:60-61` | "It watches only pins that a registry row backs." | "…*and* that `registry/engine-pins.tsv` gives a line. The vLLM line names the v0.32.0 docs pin and its two rows (S327, S363) and nothing else, so the entry pinned to the v0.31.0 release and a process (S480, S481) is backed by two rows and still watched by nothing. The gap there is a missing ledger line, not a missing row." | qualified: "a row backs a pin" is false as stated — the ledger, not the registry, decides what is watched |

No sentence is marked "needs no change". The closest call is **#4** and the second-closest **#1**: #4 already names its process ("in the API server process") and #1 states only a negative portability result, which the finding strengthens rather than falsifies. Both are still qualified because each is the sentence a reader generalises from — #4 ends the entry's enumeration, #1 is the matrix's thesis and is keyed on the engine whose key the finding breaks.

### Why the patch appends rather than rewrites

The lane's own rule for held entries: "every correction appended at the end of its file" and a dated line is never rewritten (`corpus/QUALITY.md:29`, KQ7), corrections are "appended with the superseded text/revision named" (`corpus/QUALITY.md:143`, KQ26), and a falsified cell is "narrowed by an appended correction, never by rewriting the counted bytes" (`corpus/QUALITY.md:309`, KQ42). The matrix itself already carries two such sections (`:42` round 11, `:60` round 16). So each of the four files gains one `## Correction — round 44 (2026-10-26)` section that quotes the superseded text and gives the qualifying reading; no line above moves, which the verifier proves by byte-comparing the applied file's prefix with the lane's.

## 3. Evidence

All commands run from `/home/vgpnk/Projects/shokunin/kama-shokunin` unless stated; receipts in the out directory.

| check | command | result |
|---|---|---|
| patch applies | `git apply --check -p1 qualify.diff` in a fixture repo (`git rev-parse --show-toplevel` = fixture) | exit 0; applies; 4 hunks, one per file |
| nothing rewritten | `grep -c '^-[^-]' qualify.diff` | 0 deleted content lines; file deltas 77→143, 25→69, 46→71, 73→108 |
| every quote verbatim | `python3 verify-quotes.py --diff qualify.diff` | `VERDICT PASS failures=0`, exit 0 — 7 blockquotes matched against lines 8, 12, 12-14, 16, 39-46, 7-9, 60-61, and 10 inline fragments against lines 15×3, 35, 4, 5×2, 60-61, 61, 65 |
| line anchors intact | same tool, `prefix intact` per file | PASS ×4 (77, 25, 46, 73 lines unchanged at the head of each file) |
| S480/S481 quotes | read of the committed copies `vllm-v0.31.0-release.json`, `vllm-pr-58552.json` | release `body` line 8 and PR `body` lines 3 and 5 printed exactly as quoted; `merged: True 2026-09-27T17:48:55Z` |
| handler and opt-in | `grep -n 'app.get("/health"\|is_ready\|weight-cache-health-port\|disabled by default' .ufo/waves/round-43/c3/vllm-v0.31.0-preload.py` | `:64` `is_ready`, `:73` route, `:75` 200/503, `:134`/`:137` the port and its "disabled by default" help |
| pin ledger | `cat registry/engine-pins.tsv` | 3 data lines, one per engine; `vllm … v0.32.0 S327 S363` — no v0.31.0 line |
| ledger uniqueness | `tools/pin-watch.py:6-7, :81-82` | header "one row per pin", `engine` "unique name"; `raise PinsError(... duplicate engine ...)` |
| dead pointer | `git ls-tree -r --name-only HEAD \| grep -ci cannot-answer` → 0; `grep -rn CANNOT-ANSWER --include='*.md' . \| grep -v '^.ufo/'` | the file is absent from the tree; the only non-`.ufo` mentions are the pointer itself and the two round-43 records |
| lane untouched by this seat | `git status --porcelain` | `M SCORECARD.md`, `M SKILL.md`, `M corpus/SOURCES.md`, `M corpus/knowledge/runtime-health-surface-processes.md`, `M registry/hexrun-ledger.tsv` are **sibling wave-1 seats'** working-tree edits (none of them mine, none in the four files this patch touches — `git diff --stat -- <the four files>` empty); the untracked set is `.ufo/waves/round-44/{tools/merge.py,w1.ready,w1.ready.dispatched,w1/out/}`, this seat's artifacts being `w1/out/S9Qual.md` and `w1/out/S9Qual/` |

Not run, and why: the C1/C2 fragment checker (`check-fragment.py c1|c2`) — this seat produced no claim fragment, so there is nothing to score; `tools/sources-append-only.py` — the patch does not touch `corpus/SOURCES.md`, so its input is unchanged; `tools/citation-provenance.py` — no `cite(<rev>, <path>, sha256=…)` token is added and its default documents (`corpus/lessons/round-18.md`, `round-19.md`, `SOURCES.md`, `SCORECARD.md`, `LOG.md`) are untouched. No build, lint or test exists for prose; `verify-quotes.py` is the only executable check and it is committed as a deliverable so the L1 can re-run it.

## 4. Findings (reported, not fixed)

**F1 — the filed line ranges are spans, not sentences, and two of them are off by a line.** `round-43.md:113` gives "probe-conventions 9-14 and 16-17". The sentence in 9-14 is at **12-14** (line 12 ends "…HTTP 503. Those are"); 16-17 is **one** sentence at line 16 plus the start of the next at 17, and that next sentence ("That is a different condition from llama.cpp's loading 503, and it is not a readiness proof.") stands as written. Likewise `engine-pin-watch` 60-66 is a clause at **60-61** plus the four-version list at 61-66. The patch quotes the exact spans and says so; the list itself should be read as a span index, not as eight sentences. Command: `sed -n '9,18p' corpus/knowledge/endpoint-health-probe-conventions.md`.

**F2 — `used-by` does not follow the citations this patch adds.** `corpus/SOURCES.md:233` (S480) and `:234` (S481) name only `corpus/knowledge/runtime-health-surface-processes.md` and `corpus/lessons/round-43.md`. After the patch, four more entries cite both rows. `used-by` is one of the three mutable cells (KQ22, `corpus/QUALITY.md:123`), so the repair is an in-place cell edit — the L1's call, since it is outside this seat's "no lane edits" bound. Proposed cell text, both rows:

```
corpus/knowledge/runtime-health-surface-processes.md, corpus/lessons/round-43.md, corpus/knowledge/runtime-health-surface-matrix.md, corpus/knowledge/endpoint-health-probe-conventions.md, corpus/knowledge/served-model-id-resolution.md, corpus/knowledge/engine-pin-watch.md
```

**F3 — the process attribution rests on a code file, and that file's row is uncommitted and moving.** The wire behaviour (two outcomes, opt-in port) is `preload.py`'s at tag v0.31.0. At the round-44 base `77d1bbf5` and at HEAD `098df344` the registry has no row for it (`git show 77d1bbf5:corpus/SOURCES.md | grep -c S483` → 0; same at HEAD) — the outside closure's D2, still open at HEAD (`round-43-verifier-spotcheck.md:106`). **During this seat's run a sibling seat wrote such a row into the working tree**: `git status --porcelain` shows `M corpus/SOURCES.md`, and `grep -n preload.py corpus/SOURCES.md` prints `236:| S483 | vLLM preload health route @ v0.31.0 — https://raw.githubusercontent.com/vllm-project/vllm/v0.31.0/vllm/entrypoints/cli/preload.py | code | A | …` with `opened 2026-10-26`, `recheck on-release`, `used-by corpus/knowledge/runtime-health-surface-processes.md`, and the same seat's edit adds `S483` to that entry's `source:` line. That row is **uncommitted**, so this patch deliberately does not cite it: asserting either state ("no row" or "row S483") would be false on one side of the L1's landing decision. The corrections cite `preload.py:75` and `:134-137` and the process entry's read of them instead. If S483 lands, three one-clause follow-ups become true and are worth taking: the matrix KQ6 amendment can say the behaviour is S483's, and the probe and id-resolution corrections can cite S483 beside S480/S481.

**F4 — the matrix's `recheck:` line now under-covers the entry.** `runtime-health-surface-matrix.md:4` declares `on-release` over S001, S004, S006, S009/S010 and S020; S480 and S481 carry 90d. The patch states the operative cadence inside the correction rather than editing line 4 (a dated line, KQ7). A superseding `recheck:` sentence naming the two rows is the L1's decision.

**F5 — base discrepancy, recorded verbatim.** The assignment names lane commit `77d1bbf5`; the working tree's HEAD is `098df344` ("round-44: wave-1 spec and dispatch (v2, 65 seats), C1/C2 drafts, seat fragment checker"). `77d1bbf5` is an ancestor and `git diff --stat 77d1bbf5 HEAD -- <the four files>` is empty, so no anchor in this report depends on which of the two is read.

## 5. Touched surfaces

- `corpus/knowledge/runtime-health-surface-matrix.md` — appended `## Correction — round 44` (Claim, header reading, vLLM row cells, KQ6 clause, recheck consequence).
- `corpus/knowledge/endpoint-health-probe-conventions.md` — appended section (two sentences plus the standing sentence at 17-18).
- `corpus/knowledge/served-model-id-resolution.md` — appended section (three routes, two processes, dead pointer).
- `corpus/knowledge/engine-pin-watch.md` — appended section (pin list, ledger gap).
- Nothing else in the lane: no `SOURCES.md`, no registry, no lesson, no tool, no probe, no service.

Out of scope and deliberately untouched: the two refusals the round-43 lesson records (staged r13 four-process rewrite, r14/r15/r16 amendments); and the neighbouring statements whose `/health` reading was checked and needs no change — `served-identity-crosswalk.md:50` (cites the llama.cpp row at `runtime-health-surface-matrix.md:14`; the finding strengthens "`/health` is not identity"), `endpoint-identity.md:88` (the live probe on `127.0.0.1:34113`, llama.cpp on this host), `runtime-health-surface-matrix.md:26` and `:69-72` (kama's llama.cpp probe use and the round-16 engine leads); and `corpus/knowledge/runtime-health-surface-processes.md`, which already carries the distinction.

## 6. Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Qual.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Qual/qualify.diff` (the patch; `git apply -p1` from the lane root)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Qual/verify-quotes.py` (the check that produced the receipt)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-44/w1/out/S9Qual/verify-quotes.out` (receipt, exit 0)

Scratch `/fast/scratch/hyaku/kama-r44/S9Qual` was used for the diff build and the fixture repos and is removed; no receipt cites a `/tmp` path. No tool was installed or upgraded.
