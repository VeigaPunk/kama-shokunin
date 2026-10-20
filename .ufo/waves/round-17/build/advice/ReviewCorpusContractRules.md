VERDICT: partial — the SOURCES contract text is coherent, but the two round-17 row drafts disagree on S042/S043 and KQ22's round-end command cannot see the S041 amendment it names.

# Scope, method, and what was not run

Read-only review for L1. I read `/home/vgpnk/Projects/shokunin/CORPUS.md` §SOURCES.md, the lane registry `corpus/SOURCES.md`, the census implementation `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`, the new guard `tools/sources-append-only.py`, the round-16 lesson and verifier spot-check, and every round-17 draft/advice file named below. I fetched `docs.python.org` 3.14 and 3.15 (read-only) to check the `Popen.returncode` text and page versions. I ran only: `grep -c '^| S0' corpus/SOURCES.md` (41), `python3 tools/sources-append-only.py --help`, and read-only `git log/show/ls`. I did **not** run the lane census, the guard's `--from/--to` checks, any harness, `measure.py`, `mutants.py`, or a live server. Counts from prior rounds are cited as recorded, not re-measured.

Current registry state: 41 rows — `grep -c '^| S0' corpus/SOURCES.md` at lane tip `cff9e62` (2026-10-20). The pre-round validator output is the committed `.ufo/waves/round-17/sources-before-validate.txt`: `W04 S031 duplicate url docs.ollama.com/api/tags across scopes`, `kama ok …/corpus/SOURCES.md`, `exit=0`. Round-16's committed census records rows 41, tier A 38, B 0, C 3, mined 31, queued 5, rejected 5 (`corpus/lessons/round-16-verifier-spotcheck.md`, §Census).

# Checklist L1 must satisfy

## 0. Preconditions

- [ ] Use the lane tip `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master`; never bare `HEAD`.
- [ ] Do not edit the frozen contract text: `CORPUS.md:67-68` — "A change is a new contract version, never an edit to this section." A new rule is a new version, not an in-place edit.
- [ ] Do not edit frozen copies, old receipts/lessons, `MANIFEST.json`, or `.ufo/state/`.
- [ ] The nine matrix files `tests/probe-verdicts/*.json` stay byte-identical and no new `*.json` lands in that directory (round hard constraint). SOURCES evidence goes under `.ufo/waves/round-17/sources/`.
- [ ] Write `corpus/lessons/round-17.md` before validating `used-by`; the census checks path existence on disk (`sources-census.sh:548-568`), and `corpus/lessons/round-17.md` does not exist yet.

## 1. Decide the row set and the ID mapping before writing cells

The two append-ready drafts assign S042/S043 differently. Freeze one mapping first; `sources-rows.md` is the one consistent with the opened files:

| id | source | kind | tier | primary anchor |
|---|---|---|---|---|
| S042 | llama.cpp `tools/server/server-context.cpp` @ 704366d76 | code | A | `get_health` 5288-5299, `res->ok({{"status", "ok"}})` at 5297 |
| S043 | llama.cpp `tools/server/server.cpp` @ 704366d76 | code | A | `signal_handler` 29-37 (`exit(1)` 34); single-model `shutdown_handler` 519-523 (`terminate()` 522); `sigaction` 533-534; `start_loop()` 575-576; `return 0` 590 |
| S044 | Python `subprocess.Popen.returncode` docs | docs | A | `/3.14/library/subprocess.html#subprocess.Popen.returncode`, title "Python 3.14.8 documentation" |
| S045 | Jia & Harman 2011, "An Analysis and Survey…" (TR-09-06 open copy) | **paper** | **B** | TR-09-06 §II.B p.5; DOI record in anchor |
| S046 (conditional) | round-17 `kama-llamacpp-live/v2` receipt | own-work | A | `teaches` opens `supersedes S041 —` if the v2 receipt is registry evidence |

- [ ] Rewrite `knowledge-teardown.md` citations to this mapping before any `used-by` cell is written. Its body and bottom provenance block currently use the reverse mapping.
- [ ] Every `S0NN` citation must point to a row whose `source` + `anchor` actually contain that file/line. Do not cite S043 for `server-queue.cpp` or S042 for `main.cpp`; neither file is in a drafted row. `server.cpp:122-124` already contains the `llama_server` entry point returning `result`, so the `main.cpp` citation is unnecessary.
- [ ] If the graceful-exit predicate depends on `server-queue.cpp` `terminate()`/break, either add a row for that file (URL at 704366d76, sha256, line anchor) or reduce the claim to what `server.cpp` shows and mark the queue implementation unregistered `[INFERENCE]`. The C2 sourced-claim constraint wants a row for each predicate it grounds.

## 2. Registry cells — every row must pass these

The table is 11 columns, so the census requires `NF==13` (`sources-census.sh:635-636`).

| Cell | Rule | Failure |
|---|---|---|
| `id` | `S` + 3 or more digits, next unused, never reused (`CORPUS.md:89`) | E02, E03 |
| `source` | title — canonical URL or DOI; code rows commit-pinned; the openable copy named; never a bare homepage; **no `\|` anywhere** | E01; anchor rule |
| `kind` | one of `spec docs paper code tool dataset talk book community own-work` (`CORPUS.md:91-92`) | E05 |
| `tier` | `A`/`B`/`C`, scoped to `scope`; A primary/authoritative, B strong secondary **including survey**, C lead only; community never A (`CORPUS.md:93-97`) | E06, E10; W01 |
| `scope` | one claim/topic; must differ from an existing row on the same URL or E04 fires | E04 |
| `anchor` | exact section/heading/page/line **plus revision** (commit, version, publication date); never bare homepage (`CORPUS.md:99-100`) | row is a claim (rule 1) |
| `teaches` | one grounded learner benefit; rejected rows read `REJECTED: <reason>; flip: <what would change the verdict>`; numbers carry commands; negatives carry sweeps; inference marked | W02; `CORPUS.md:26,34-42` |
| `status` | exactly `queued`/`mined`/`rejected`; `mined` requires a `used-by` path | E07, W03 |
| `opened` | ISO date, not future relative to `date -u +%F` | E08 |
| `recheck` | ISO date, `NNd` (e.g. `90d`), or symbolic (`on-release`, `every round`); symbolic never judged overdue | E09 |
| `used-by` | repo-relative knowledge/lesson paths, comma-separated, or `—`; list **every** citing path; each path must exist when the row is `mined` (E11 checks mined rows only) | E11; W01/W03 |

Mechanics that break rows silently:

- [ ] Keep every cell free of `|` — including inside backticks and `\|`. The contract says "No `|` inside any cell." (`CORPUS.md:89`). The guard tolerates backticked pipes (`tools/sources-append-only.py:27-31`), but `sources-census.sh` splits on every `|` (`awk -F'|'`), so a backticked pipe passes the guard and fails E01. The census is authoritative.
- [ ] Append the four/five data rows **inside `## Registry`**, after S041 (`corpus/SOURCES.md:53`) and before the blank line/`## Paths`. Any row-shaped line (`| S0.. |`) outside the Registry section is E12 (`sources-census.sh:620-621`), including in the Search log or appended correction prose.
- [ ] Do not duplicate the table header/separator when appending; copy only the data rows.
- [ ] S043's URL is S037's URL. A `#L26-L37` fragment does **not** remove the warning: `url_of` strips `#…` and trailing `/` before comparing (`sources-census.sh:600-603`). Expect `W04 S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76…/tools/server/server.cpp across scopes`; W04 is a warning, exit stays 0. Do not switch to `raw.githubusercontent.com` just to dodge it.
- [ ] S042's `/health`-needs-no-key fact is at `server.cpp:278`, not at S042's `server-context.cpp` URL. Move that registration line to S043's anchor (its file) or drop it from S042; keep S042's scope to the handler body. The row's URL should resolve the anchor a reader is asked to verify.
- [ ] S043's scope says "single-model and router" but its anchor cites only the single-model `shutdown_handler` (519-523). Either add the router branch `server.cpp:481-491` (`ctx_http.stop(); ctx_server.terminate(); mcp_mgr.shutdown(); llama_backend_free();`) or scope the row to single-model and record router as a lead.
- [ ] S045: `kind` is `paper`, not `docs`; tier is `B`, not `A`, because the cited work is a survey and B is the contract's survey tier (`CORPUS.md:95-96`). The draft's note says the criteria are not in `SOURCES.md` and picks A by precedent — but they are in `CORPUS.md` §SOURCES.md, which the lane header points to (`corpus/SOURCES.md:3`). If you want tier A, cite the original paper that defines the terms, not a survey. Keep the honest note that the IEEE body is paywalled and the quoted wording is TR-09-06; put the open TR URL in `source` as the quotable copy, or name it explicitly in `anchor`.
- [ ] S044: anchor `/3.14/`, not `/3/`. `docs.python.org/3/` currently serves **3.15.0** (`<title>… Python 3.15.0 documentation</title>`), while the host runs `/usr/bin/python3` 3.14.8 and `/3.14/` serves "Python 3.14.8 documentation". The quoted sentence is identical on 3.12–3.15, so the claim is robust; the anchor should name the runtime's version. Do not cross-check only 3.13.
- [ ] If S045 stays, its `teaches` must not smuggle an adequacy claim: `scope` says "definitions only", and the row must not become evidence that the test set is adequate or that a kama measurement ran.

## 3. Gate quote rules (round-17 lesson)

- [ ] For **every** new row, `## Gate` records the full URL, the access date (2026-10-20), and a ≤25-word verbatim quote with its exact location (`CORPUS.md:112-115`). The Gate table in `sources-rows.md` cites S-ids and file:line; add a "Gate locations" paragraph like round-16 (`corpus/lessons/round-16.md:186-196`) with the full URLs.
- [ ] Quote only contiguous text; do not stitch two sentences with an ellipsis to stay under 25 words. Split into two located quotes instead.
- [ ] Quote every line you cite. Round-16's nit is the model: S036's Gate cited "body literal at 318-320" but quoted only 318; type and code are at 319-320 (`corpus/lessons/round-16-verifier-spotcheck.md:185`).
- [ ] Quote from the row's URL or an open copy named in the row. S045: say "TR-09-06 §II.B p.5", not "the TSE article". S044: quote the 3.14 page. S042/S043: quote the pinned commit file, with the raw sha256 already in the anchor.
- [ ] Rejections need a reason and a flip condition if they become rows. The non-row leads (PIT page) stay in `## Leads (unopened)` or the search log, never as a row.
- [ ] Do not admit `-9 = SIGKILL` without a source. The Gate already rejects it: "The number 9 for SIGKILL is not sourced by any row opened this round" (`sources-rows.md:45`). Either add a row for `signal.SIGKILL`/`Popen.kill` docs, or write "returncode -9; signal name not separately sourced" and grade the harness's own `sigkill_sent` flag plus the numeric code.
- [ ] If the lesson mines mistakes (the S041 amendment, the draft swap), it carries `## Mistakes` with class · evidence · captured-by · fix (`CORPUS.md:171-177`). Captured-by should name KQ22 and the guard; fix should be the superseding row + guard + logged old→new.
- [ ] The lesson/search log records one bounded search: question, where, date, identified/screened/included/excluded counts, exclusion reasons, stop rationale (`CORPUS.md:126-128`). `sources-rows.md:50-62` is close; add the date and name the 3.14 page as the primary docs read.

## 4. `used-by` and knowledge provenance

- [ ] Append the round-17 knowledge supplement to `corpus/knowledge/llamacpp-loading-lifecycle.md` (its `source:`/`verified-at:`/`recheck:` trio is lines 1-3) **or** create a new knowledge entry. Either way, the new claims need their own provenance trio: `source:` cites each `S###` row with URL and anchor, `verified-at:` names the open/run date, `recheck:` names a cadence (`CORPUS.md:163-168`). Do not rewrite lines 1-3; append a `## Round-17 supplement — provenance` block.
- [ ] `used-by` lists every citing path. S042 is cited by the knowledge entry; S043/S044 are cited by both the knowledge entry and the lesson. The draft lists only one path per row. The contract defines `used-by` as "repo-relative paths of the knowledge entries or lessons citing the row" (`CORPUS.md:107-108`).
- [ ] Order of operations: write the lesson/knowledge citation first, then the row's `used-by`, then run the census. A green E11 proves existence, not that the cited file actually cites the row.
- [ ] If a new knowledge entry is created, add its row to `corpus/README.md`'s coverage map (an index row is a claim: write it when the file exists, `CORPUS.md:46-48`). If the supplement is appended to the existing entry, append a round-17 coverage note; do not rewrite old lines.
- [ ] Do not count S045 as expansion/coverage. It is method support for the mutation count, not uncovered coverage-map ground (`CORPUS.md:123-125`).
- [ ] Do not create a `knowledge/` entry that duplicates a claim already in `llamacpp-loading-lifecycle.md`; append the delta only.

## 5. Old→new logging (contract rule 2)

- [ ] Allowed in-place cells are exactly `status`, `recheck`, `used-by` (`CORPUS.md:116-117`). Every other cell — `id`, `source`, `kind`, `tier`, `scope`, `anchor`, `teaches`, `opened` — is immutable after the row's first commit.
- [ ] Every in-place change is logged old→new in `corpus/lessons/round-17.md` (the lesson is mandatory; a `SOURCES.md` prose supplement is precedent, not a substitute). Use this shape:

```text
Row changes: new S042, S043, S044, S045 (and S046 if the v2 receipt row lands).
In-place changes (contract rule 2):
- S041 used-by: `corpus/knowledge/llamacpp-loading-lifecycle.md`
  → `corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-17.md`
  (2026-10-20: the round-17 lesson cites the v1 receipt as prior capability).
No status or recheck cell of an existing row changed.
```

- [ ] If nothing changes in place, say so explicitly (round-16's `corpus/lessons/round-16.md:58-61` is the model).
- [ ] A regenerated artifact, re-measured receipt, or corrected anchor takes a **new row** whose `teaches` opens `supersedes S0NN —` (`CORPUS.md:117-118`). Do not edit S041's `anchor`/`teaches` for a v2 receipt; that is exactly the round-16 routed defect (`corpus/lessons/round-16-verifier-spotcheck.md:184`).
- [ ] No whitespace-only or formatting edits to existing rows. The guard compares cells after trimming (`tools/sources-append-only.py:30-31`), so a whitespace edit at a cell edge can pass the guard while the criterion says "byte-identical". If you touch an existing row, the diff must show a real cell value change.
- [ ] Append a `SOURCES.md` correction paragraph (prose, **no row-shaped lines**) for the intro's "Every row was opened in round 10" claim (`corpus/SOURCES.md:7`) and for each in-place change, like rounds 11–16 (`corpus/SOURCES.md:77-85`, `:102`). Do not rewrite the intro.
- [ ] If S041's v2 receipt is registry evidence, add S046 with `teaches` opening `supersedes S041 —`, `status: mined`, `used-by` = the lesson/knowledge path, and `scope` = "v2 receipt schema/grading, not a new server run". If it is only a measurement, say so in the lesson and leave S041 as the v1 record.

## 6. Census exit 0 — the counting command

- [ ] Run from the lane root:

```sh
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
  --root /home/vgpnk/Projects/shokunin kama
```

- [ ] Expected after S042–S045: `W04 S031 …` (pre-existing), `W04 S043 …server.cpp…` (shared URL with S037), `kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`, **exit 0**. No `E`-codes.
- [ ] If S045 is corrected to tier B, the census histogram is rows 45, tier A 41, B 1, C 3, status mined 35, queued 5, rejected 5 `[INFERENCE — arithmetic from the draft; re-run and record the actual output]`. If S045 stays A: A 42, B 0. If S046 lands: rows 46, mined 36, and one more A (own-work) `[INFERENCE]`.
- [ ] Any `E`-code means exit 1; fix the row, do not waive. Missing registry returns 2. Warnings (W01–W04) do not change exit status but still need an explanation in the lesson.
- [ ] Do not use the fleet default `census` mode for the lane check: it exits 1 when any other lane's registry is missing. The scoped `validate … kama` is the command.
- [ ] Record the exact output and exit in the lesson/report. The counts are a claim: `<number> — <command> <date>` (`CORPUS.md:34-38`).
- [ ] Run the census **after** `corpus/lessons/round-17.md` exists; otherwise E11 fails for S043–S045 and a rushed fix would point `used-by` at a draft.

## 7. Round-end append-only guard (rule 2 enforcement)

The guard reads committed blobs with `git show REV:PATH`, never the working tree (`tools/sources-append-only.py:1-17`). Commit first.

- [ ] Historical control (proves the detector works; this is the red-before required by `CORPUS.md:179-182`):

```sh
python3 tools/sources-append-only.py --from b8e485c --to ccc4bb3
# expect exit 1 with two VIOLATION lines for S041: `anchor` and `teaches` changed in place
```

- [ ] Round check (must be clean for this round's changes):

```sh
python3 tools/sources-append-only.py --from cff9e62 --to "$(git rev-parse master)"
# expect exit 0; added S042–S045 listed as allowed; no VIOLATION
```

- [ ] Do **not** use `--from 1e41928` as the round-end check. S041 does not exist at 1e41928 (30 rows at the round-10 registry commit), so the guard reports it as "added" and never compares its cells (`tools/sources-append-only.py:174-187`). The command cannot produce the S041 flag that KQ22's exception list names. The correct evidence is the pair above: b8e485c→ccc4bb3 for the historical amendment, cff9e62→tip for this round. A round-start base is the right base for amendments to rows that existed at the start (S031–S041); it is not evidence about pre-round amendments, which is the historical control's job.
- [ ] If S046 lands, the guard shows S041 unchanged (its cells stay) and S046 as added; that is clean.
- [ ] Keep cells pipe-free even though the guard tolerates backticked pipes; the census is the authority (`CORPUS.md:89`, `sources-census.sh:635`).

## 8. Final sweep before yielding

- [ ] `git diff cff9e62 -- corpus/SOURCES.md` contains only: new S042–S045(/S046) rows and the allowed `used-by`/`status`/`recheck` changes on existing rows. No other bytes moved.
- [ ] `git status --porcelain` shows only intended files; no report written at the fleet root; `corpus/lessons/round-17.md` exists.
- [ ] The Gate has a full URL, access date 2026-10-20, and a ≤25-word located quote for every new row; `## Mistakes` exists if the lesson mines mistakes.
- [ ] `corpus/SOURCES.md` has a round-17 prose supplement and no row-shaped line outside `## Registry`.
- [ ] Census exits 0 (scoped `validate … kama`); guard round check exits 0; historical control exits 1 with S041 `anchor`+`teaches`.
- [ ] No new `*.json` in `tests/probe-verdicts/`; frozen copies untouched; no live server or port left behind.

# Findings, by severity

## High

### F1. S042 and S043 are reversed between the two append-ready drafts

`sources-rows.md:11-12` assigns S042 to `server-context.cpp` and S043 to `server.cpp`. `knowledge-teardown.md:16-18` cites the `get_health` handler as **S043**, `:37-42` cites the SIGTERM handler as **S042**, and its bottom provenance block `:97-105` assigns S042 to `server.cpp`/`main.cpp` and S043 to `server-context.cpp`/`server-queue.cpp`. Example: `knowledge-teardown.md:16` — "(S043, `tools/server/server-context.cpp:5288-5299`". If L1 merges both unchanged, every row citation and every `used-by` cell is wrong, and the registry would claim the wrong file for the wrong id. Freeze the `sources-rows.md` mapping and rewrite the knowledge draft before writing cells.

### F2. `server-queue.cpp` and `main.cpp` are cited as S042/S043 but no row covers them

`knowledge-teardown.md:46-48` cites `server-queue.cpp:132-136` as S043, and `:51` cites `main.cpp` as S042. Neither file is in the drafted rows; the round-16 pinned directory has no `server-queue.cpp`/`main.cpp`, and the round-17 `sources/llama.cpp-704366d76` pin does not make them registry rows. Quote: `knowledge-teardown.md:46` — "`terminate()` sets `running = false` (S043,". `server.cpp:122-124` already contains the `llama_server` entry point returning `result`, so drop `main.cpp`. For the queue's `terminate()`/break, add a row for `server-queue.cpp` (URL/sha256/lines) or reduce the claim to `server.cpp:519-523, 575-576, 590` and mark the queue implementation unregistered `[INFERENCE]`. The C2 claim requires new SOURCES rows for its predicates; a citation to S043 for a different file does not satisfy it.

### F3. KQ22's round-end base cannot flag S041; the rationale is inverted

`quality-kq22.md:12` says: "The round-end check is `python3 tools/sources-append-only.py --from 1e41928 --to <tip>`." At `1e41928` (round-10 registry, 30 rows), S041 does not exist; the guard reports it as "added" and skips comparison (`tools/sources-append-only.py:174-187`). The same criterion at line 12 names S041 `anchor`/`teaches` as the live exception, so the command and the exception list cannot both be right. The rationale — "a round-start base cannot see an amendment already committed before it" — is true for S041 but a first-commit base is worse for S041, not better: the row is absent at the base. The only range that sees the amendment is `b8e485c` (S041's first commit) → `ccc4bb3`, which the guard's task (`.ufo/waves/round-17/build/spec.json:44`, sources-append-only item) states: "It must flag S041 for `--from b8e485c --to ccc4bb3`". For this round, use the pair in §7: `b8e485c→ccc4bb3` as the historical control and `cff9e62→tip` as the round check. Correct KQ22 before adopting it; its reject column's blanket "a round-start check is not evidence" is too broad (it is the correct evidence for round-17 changes to rows that existed at the start).

### F4. S045's kind and tier overclaim

`sources-rows.md:14` sets `kind=docs`, `tier=A`. The contract's kind enum includes `paper` (`CORPUS.md:91-92`), and its B tier explicitly includes a "survey" (`CORPUS.md:95-96`); A is the primary/original paper (`CORPUS.md:93-95`). The cited work is "An Analysis and Survey of the Development of Mutation Testing" — a survey — so it is `paper` + `B`, not `docs` + `A`. The draft's note at `sources-rows.md:24-26` says "tier A is chosen by precedent from S035–S041 and is [INFERENCE]" because "the tier criteria are not written in `corpus/SOURCES.md`" — but they are written in `CORPUS.md` §SOURCES.md, which the lane header points to (`corpus/SOURCES.md:3`). W01 does not fire on tier A, so only review catches this. If you want A, cite the original paper that defines mutant/killed/mutation score, not the survey. The definitions remain usable at B; they are not the sole support for the C1 count (the mutant runner is own-work).

### F5. `-9` = SIGKILL is asserted where the Gate says it is unsourced

`knowledge-teardown.md:70` says "`-9` means it was SIGKILLed". The same round's Gate rejects that claim as cited: `sources-rows.md:45` — "The number 9 for SIGKILL is not sourced by any row opened this round". `CORPUS.md:26` requires "A corpus entry is falsifiable or marked opinion; no unverifiable claims." Either add a row for `signal.SIGKILL`/`Popen.kill` docs (the Python page says `Popen.kill` "sends SIGKILL to the child"; `signal` docs name SIGKILL) or write "returncode -9; negative value means signal 9; the signal name is not separately sourced". The receipt already records the harness's own `sigkill_sent`; grade that flag plus the numeric code, not an inferred name.

## Medium

### F6. S044 anchors the wrong Python version for the runtime

`sources-rows.md:13` anchors `/3/` and says "(resolves to 3.15.0)", with a 3.13 cross-check. `docs.python.org/3/` currently serves 3.15.0 (`<title>… Python 3.15.0 documentation</title>`); `/3.14/` serves "Python 3.14.8 documentation"; the host `/usr/bin/python3` is 3.14.8. The quoted sentence is identical on 3.12–3.15, so the claim is robust, but the anchor should name the runtime's version. Use `/3.14/library/subprocess.html#subprocess.Popen.returncode` and quote "A negative value -N indicates that the child was terminated by signal N (POSIX only)." (15 tokens). The 3.13 cross-check is arbitrary; drop it or replace it with 3.14.

### F7. S043 shares S037's URL; a `#L` fragment does not remove W04

`sources-rows.md:17-20` says L1 may choose a fragment "such as `…/server.cpp#L26-L37`". `url_of` strips `#…` and trailing `/` before duplicate detection (`sources-census.sh:600-603`), so the fragment still yields `W04`; it cannot remove the warning. W04 is a warning and validation still exits 0. Accept it, name it in the lesson/search log, and keep the canonical blob URL. Do not switch hosts to dodge the warning; that would make the row's URL differ from the page actually opened.

### F8. S042's "public endpoint" fact points at S037's file

`sources-rows.md:11` includes "`/health` registered as public at `server.cpp:278`" in S042's anchor, but S042's `source` is `server-context.cpp`. A reader opening S042's URL cannot verify `server.cpp:278`; that line belongs to S043's file. Move the registration claim to S043's anchor (or cite it as context in the Gate, not as S042's cell), and keep S042's scope to the handler body. The "a quote names its location" rule (`CORPUS.md:42-45`) is the relevant discipline.

### F9. `used-by` is incomplete and, for S042, not yet true

`sources-rows.md:11-14` lists S042's used-by as `corpus/knowledge/llamacpp-loading-lifecycle.md` and S043–S045's as `corpus/lessons/round-17.md`. The knowledge supplement cites S042/S043/S044, and the lesson will too; the contract defines `used-by` as the repo-relative paths of the knowledge entries **or** lessons citing the row (`CORPUS.md:107-108`), comma-separated. List every citing path. E11 only checks that listed paths exist (`sources-census.sh:548-568`), so a green E11 does not make an incomplete list true. S042's listed entry does not cite S042 yet; write the append first, then the cell. `corpus/lessons/round-17.md` does not exist yet; creating it is a precondition for E11, not a fix to apply after a red run.

### F10. The knowledge supplement has no provenance trio of its own

`knowledge-teardown.md` is an append to `corpus/knowledge/llamacpp-loading-lifecycle.md`, whose trio is lines 1-3 and does not list S042–S044. The kaika rule requires a new entry to open with `source:`/`verified-at:`/`recheck:`, and `source:` must cite its `S###` row with URL and anchor (`CORPUS.md:163-168`). Appending prose citations without a machine-readable trio leaves the new claims invisible to the freshness sweep. Add a `## Round-17 supplement — provenance` block with the trio before the claims; keep lines 1-3 byte-identical. Do not bury the provenance only in the draft's header.

### F11. The guard and the census disagree on pipes in cells

`tools/sources-append-only.py:27-31` says a `|` inside a backtick code span, or a `\|` escape anywhere, "is cell content, not a delimiter". The census splits on every `|` and rejects `NF!=13` (`sources-census.sh:635-636`); the contract says "No `|` inside any cell." (`CORPUS.md:89`). A row with a backticked pipe passes the guard and fails E01. The guard's selftest case "pipe inside backticks" is therefore not evidence that such a row is valid. L1 must keep every cell pipe-free and use the census as the authoritative shape check; do not cite the guard's tolerance as permission. If the guard is meant to enforce rule 2 only, document the divergence in its header; if it is meant to enforce row shape, it should reject the pipe.

### F12. KQ22 says "byte-identical"; the guard compares trimmed cells

`quality-kq22.md:12` requires immutable cells "byte-identical", but the guard compares cells after "leading/trailing whitespace strip" (`tools/sources-append-only.py:30-31`). A whitespace-only edit at the edges of an immutable cell passes the guard while violating the criterion's own word. The census also trims, so no automated check catches it. L1 must not edit whitespace in existing rows; if the claim is "byte-identical", either compare raw cell text or phrase the criterion as "the trimmed cell value". Do not overclaim that the guard proves byte identity.

### F13. The ready-body equality relation differs between the two drafts

`knowledge-teardown.md:25-26` says "A check should compare the parsed JSON object to exactly `{"status": "ok"}`, with no extra keys, not the raw bytes." `probe-health-body.md:35` says "An exact-byte check is implementable; no drift observed", and `:50` says grade `body == b'{"status":"ok"}'` exactly. The v2 check must pick one relation, and the knowledge entry must match it. Byte-exact is observed (10/10 samples) and is the stronger reading of "exactly the documented ready body"; parsed-JSON equality is more tolerant of serialization changes but weaker. If the check parses, say so and record the observed bytes separately; do not let the entry imply byte identity while the check parses.

## Low

### F14. S043's scope says "router" but the anchor cites only single-model shutdown

`sources-rows.md:12` scopes the row to "single-model and router", but the anchor cites only the single-model `shutdown_handler` at 519-523. The router branch is at `server.cpp:481-491` (`ctx_http.stop(); ctx_server.terminate(); mcp_mgr.shutdown(); llama_backend_free();`). Either add those lines to the anchor or scope the row to single-model (the harness mode) and keep router as a lead. The row's `teaches` already says "single-model and router", so the anchor should match the scope.

### F15. S041's v2 receipt has no row/supersession decision

The C2 claim uses receipt `kama-llamacpp-live/v2`; S041 records v1 (`corpus/SOURCES.md:53`). KQ22 says "A regenerated artefact, a re-measured receipt or a corrected anchor is recorded by a new row" (`quality-kq22.md:12`). The sources draft has no such row. Decide explicitly: add S046 (own-work, `teaches` opens `supersedes S041 —`, `scope` = v2 receipt/grading) or state in the lesson why the v2 receipt is a measurement output, not a registry row. Do not edit S041's `anchor`/`teaches`; that is the round-16 routed defect (`corpus/lessons/round-16-verifier-spotcheck.md:184`).

# Residual risk and verification gaps

- **The drafts are moving.** `sources-rows.md`, `knowledge-teardown.md`, and `probe-health-body.md` were written during this build wave; a later revision may fix F1/F2/F15 without this report. Re-check the draft hashes before integrating.
- **Not executed.** I did not run the lane census, the guard's `--from/--to` checks, `check.py`, `mutants.py`, `controls.py`, or any live server. The expected exits in §6–§7 are derived from the parser and the recorded baseline, not reproduced. `[INFERENCE]`
- **Counts.** 41 rows is observed (`grep -c '^| S0'`). Tier/status counts are from the round-16 verifier's committed census; the post-integration arithmetic (45/41/1/3 or 45/42/0/3) is inference until L1 runs `census`.
- **S041's historical amendment is permanent.** No current command can both use a first-commit base and exit 0 while S041's amendment is in range; the exception list in KQ22 is the honest resolution, but it must name the exact `b8e485c→ccc4bb3` run, not a `1e41928→tip` run that cannot produce the flag.
- **Guard/census divergence** (F11) is not caught by either tool alone; only a pipe-free cell keeps both green. A future guard revision should either reject pipes or explicitly scope itself to append-only diffing.
- **Knowledge/corpus scope.** The corpus does not establish registered-consumer health, runtime integration beyond the lane-owned fixture, or that the v2 receipt's checks are adequate; those remain C2/verifier questions.

# Limitations and installs

Read-only seat. No files written except this report. No lane gate, harness, measurement, or live tool executed. No ports bound. No packages installed or upgraded. Network use: read-only fetches of `https://docs.python.org/3.14/library/subprocess.html` and `https://docs.python.org/3/library/subprocess.html` to verify the `Popen.returncode` text and page versions (2026-10-20).
