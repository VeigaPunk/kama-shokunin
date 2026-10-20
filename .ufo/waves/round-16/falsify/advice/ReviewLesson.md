# ReviewLesson — `corpus/lessons/round-16.md` against receipts and round-15 routed defects

VERDICT: partial — every asserted measurement number reproduces from the committed
receipts (and from an independent rerun), and the six routed-defect dispositions match
`round-15-verifier-spotcheck.md:163-172`; but the lesson's named "final numbers" artifact
does not exist, one "Before" round referent is wrong, and one pre-fix scope sentence is
overbroad. Details below with command, exit and excerpt.

## What I ran (all read-only; no server started; no install)

| Command | Exit | Result |
|---|---|---|
| `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` (stdout to /tmp) | 1 | `tests=72 passes=55 failures=17`; 17 `[FAIL]` on stderr |
| same with `--probe tools/kama-probe.sh` | 0 | `tests=72 passes=72 failures=0` |
| `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --only ReadyControls.expect-exact-id --json` | 0 | 1/1 pass, measured 0.584 s |
| `sha256sum` frozen probe + `git cat-file blob 20e392e:tools/kama-probe.sh \| sha256sum` | 0 | both `93ee4302…cd64` |
| `bash tools/test-snapshot.sh` | 0 | `RESULT pass=30 fail=0` |
| `python3 tests/llamacpp-live/check-receipt.py <receipt>` (both receipts) | 0 | `VALID` each |
| `curl` S021 URL / S040 v0.10 / release page / HF model card | 404 / 200 / 200 / 200 | see below |
| `curl` raw `server-context.cpp`, `server-models.cpp` @ `704366d` | 200 | quoted lines verify |
| `git cat-file -e b8e485c:.ufo/waves/round-16/acceptance.json` | 128 | `does not exist` |
| `pgrep -x llama-server` | 1 | none running |

`measure.py` was **not** run (lane contract); its committed `measure-stdout.txt` and the
underlying `check.py` rerun above carry the numbers.

## Findings

### F1 — medium — the lesson's "final numbers" pointer is dangling

`corpus/lessons/round-16.md:93-94` says: "Final numbers at the measured commit are in
`.ufo/waves/round-16/acceptance.json`." That file does not exist in the working tree
(`find .ufo/waves/round-16 -name 'acceptance*'` → no output) and was never committed
(`git cat-file -e b8e485c:.ufo/waves/round-16/acceptance.json` → `fatal: path ... does not
exist in 'b8e485c'`, rc 128).

Precedent is against this: rounds 14 and 15 committed `acceptance.json` inside their own lane
commits — `git log --oneline -- .ufo/waves/round-15/acceptance.json .ufo/waves/round-14/acceptance.json`
→ `b8bdc56 round-15: record measured guard repair...` and `06cc6db round-14: record measured
replay capability...`. Every other receipt the lesson names *is* committed at `b8e485c`
(`run-before.json`, `run-after.json`, `measure-stdout.txt`, `live/receipt*.json`,
`live/controls.txt`, `run-check-selftest.txt`, `run-test-snapshot.txt`), which makes this the
one evidentiary pointer with nothing behind it.

Scope: no number in the lesson is falsified by this. The 72/55/17, 72/72, 30/0, 10/10 and
16-mutation figures all reproduce (below). Fix: commit the `acceptance.json`, or re-point the
sentence at the committed receipts.

### F2 — low — "last real llama.cpp observation was round 3 (2026-10-14)" is the wrong round

`corpus/lessons/round-16.md:28-30`: "the last real llama.cpp observation was round 3
(2026-10-14), and the registered consumers are `DEAD`."

The lane record says the opposite about round 3. `LOG.md:211` (round 3, 2026-10-14 survey):
`model_ok=0 drift=11` "every row DEAD"; `LOG.md:246`: "ports 34113 and 8080 both refuse
connections". The last recorded **live** engine response is round 2 (2026-09-29):
`LOG.md:160` "34113 still serves the expected llama.cpp", with `LOG.md:131-132`
`snapshot=20260929T043044Z ... model_ok=3 drift=8`. No later round in `LOG.md` shows
`model_ok>0`; the 2026-10-15 relaunch also read all three rows DEAD (`LOG.md:367-371`).

[INFERENCE] If the intended meaning is "the last time the lane probed the runtime", round 3 is
right but the sentence should say it found it dead; as written it reads as a live 2026-10-14
observation and overstates recency by 15 days.

### F3 — low — pre-fix probe scope sentence is overbroad

`corpus/lessons/round-16.md:11-14` says the probe "graded every non-2xx, non-HTML response
without a model array `FOREIGN_SERVICE` / `non-2xx-non-model-http`". The frozen code grades
`401`/`403` as `UNAUTHORIZED_SERVICE` before that fallback
(`.ufo/waves/round-16/frozen/kama-probe-before.sh:458-465`), and the 72-row matrix carries 7
`AuthAndDead` rows. The sentence should say "every remaining non-2xx, non-HTML response".
The fallback's own evidence string and reason are quoted correctly; no measurement changes.

### F4 — low / unverifiable — M4's event is not in any committed artifact

`corpus/lessons/round-16.md:67` (M4) says `RevengerPlannerWalk` wrote relative to the fleet
root, moved the report, and removed the directories "(its own disclosure)". The seat's report
contains no such disclosure: `RevengerPlannerWalk.md`'s method section says only "No tools
installed" and lists no write path, and `grep -rn "misroot\|fleet root\|wrong root"
.ufo/waves/round-16/build/advice/` returns nothing. The fleet root `.ufo/waves/round-16/`
exists with mtime `10:57` but holds only Oct-19 entries (`before.md`, `clobber/`,
`dispatch.md`, `gate/`), consistent with a removal but not proof of one.

Not refuted — the event may have been disclosed only in the seat's terminal message. But the
row's Evidence column points at the policy clause, not the event, so the incident is not
retained with a durable pointer the way round-15 defect 3 asked. Add the seat-message pointer,
or drop "(its own disclosure)".

## Confirmed (no finding)

Numbers — all match receipts and my independent run:

- Frozen probe: `run-before.json` `exit: 1`, `tests 72`, `passes 55`, `failures 17`; sha256
  `93ee4302…cd64` equals `git cat-file blob 20e392e:tools/kama-probe.sh`. Failure set is
  exactly the 17 `expected.verdict == MODEL_LOADING` records (set equality computed from the
  rerun JSON), and the measure diff lists 17 changes, all to `MODEL_LOADING`.
- Repaired probe: `run-after.json` `exit: 0`, `72/72`; my rerun same.
- `tools/test-snapshot.sh`: `RESULT pass=30 fail=0`, exit 0. "was 24" is supported: the script
  has only two commits (`83bee7f` round-2, `b8e485c` round-16), and round-2/4/5 records show
  `RESULT pass=24 fail=0`. The six new cases include the two named (MODEL_LOADING baseline
  kept/diffed, unknown verdict warned/audited/dropped).
- `check.py --selftest`: `tests=72 passes=72 failures=0`, `selftest: 4/4 malformed tests
  rejected`, exit 0 (committed log).
- C2: both receipts `10/10` checks; `port 32845`; `port_refusal_set [8080, 34113]`;
  `probe_model_ok` `{"exit": 0, "reason": "matched", "verdict": "MODEL_OK"}`; controls
  `digest_mismatch_exit=3`, `registered_port_34113_exit=2`, `registered_port_8080_exit=2`,
  `listening_port_631_exit=2`, `post_pgrep_llama_server=0`; gate selftest "16 mutations +
  unreadable case all rejected". I reran the gate on both receipts: `VALID`, exit 0.
- Model file on disk: 1,185,376 B, sha256 `270cba1b…256d` (matches receipt and LOG).
- `--only` timing smoke claim (`0.6 s`) reproduces at 0.584 s.

Quotes — checked at the cited lines against pinned/live files:

- `server-http.cpp:312` "no endpoints are allowed to be accessed when the server is not ready";
  body at 318-320; `server.cpp:493` "start the HTTP server before loading the model...";
  `server-context.cpp:5396` "no slot available"; `server-models.cpp:2585` "Stream owner model is
  loading, retry later" (the last two fetched from raw.githubusercontent @ 704366d; both 200,
  text exact at those lines).
- `README.md:487` "Explanation: the model is still being loaded."; `:1258` "The `meta` field
  can be `null` (for example, while the model is still loading)." (context is `/v1/models`).
- S017 probes.md:70 "Readiness probes determine when a container is ready to accept traffic."
- S040 v0.10:200, rendered "Version: v0.10", sentence "The vLLM /health endpoint only
  indicates that the server process is running, not that models are loaded and ready to
  serve."; S021 recorded URL:404.
- S039 model card: "Various models to be used in llama.cpp CI workflow." (fetched README).
- S038: local `llama-b11755-bin-ubuntu-x64.tar.gz` is 22,240,468 B, sha256
  `753bfa73…a6e226`, exactly the lesson's quoted asset digest; release page renders
  "Pre-release" (the GitHub API itself returned 403 rate-limited, see limits).

Rows — `git diff 20e392e b8e485c -- corpus/SOURCES.md` removes exactly one existing line
(S017). Cell-by-cell, only cell 10 (used-by) changed, to add
`llamacpp-loading-lifecycle.md`. S021's line is untouched and still `queued`; S035-S041 are
new, all opened `2026-10-20`; S040 records "supersedes S021 — S021's recorded URL now returns
404". No status or recheck cell of an existing row changed.

Registry — `registry/history/latest.tsv` is still 3 rows `DEAD connection-refused`, matching
the lesson's "nothing was restored".

## Routed defects — crosswalk to `round-15-verifier-spotcheck.md:163-172`

| # (lesson) | Round-15 item | Lesson disposition | Verdict |
|---|---|---|---|
| 1 | 165 Prior R1 → resolved (count comparison) | "resolved in round 15; no change" | accurate |
| 2 | 166 Prior R2 → resolved (partial vs provider failure) | "resolved in round 15; no change" | accurate |
| 3 | 167 Process incidents → next steered round | wave context forbids session/unbounded; M4/M5 retained; no QUALITY criterion | accurate in substance; M4's pointer is weak (F4) |
| 4 | 168 Dispatch provenance → next round | `build/validation.json` argv/cwd/3 env bindings/`taskCall_sha256`; `dispatch-provenance.py` | accurate — verified: 3 bindings, `taskCall` digest; the tool cites defect 4 and writes the falsify `provenance-ledger.json` `wave_run` (3 bindings, exit 0) |
| 5 | 169 Replay prose precision → append | appended to `ollama-evidence-replay.md` | accurate — appended note at `:376-385` says "evaluation order, not a short-circuit" |
| 6 | 170 S012 wording → append, never rewrite | appended SOURCES note, no cell changed | accurate — note at `SOURCES.md:116-121`; S012 row absent from the diff |

The lesson's "all five agreed" about the round-15 outside sample also checks out: the
discernment table at `round-15-verifier-spotcheck.md:119-123` has five rows, each `agree`.

## Limits and residual risk

- I did not run `.ufo/waves/round-16/measure.py` (contract). Its `exit 0` is taken from the
  committed `measure-stdout.txt` and the underlying matrix run I did execute.
- GitHub API `/releases/tags/b11755` returned **403** (rate limit); the S038 digest was
  verified against the downloaded asset bytes (sha256 equal) and the release HTML label, not
  the API JSON. The release `published` timestamp was not re-verified.
- Both live receipts record `"loading_observed": false` — the 503 window was not caught live.
  The lesson does not claim it (it cites only `probe_model_ok`/`probe_mismatch`), so this is
  not a contradiction; it does mean C2 does not reproduce the C1 envelope live.
- M4 cannot be confirmed or refuted without the L1/seat message record, which is outside this
  item's bound.
- The lesson's `server-context.cpp:5396` / `server-models.cpp:2585` quotes are not covered by
  `sources/pins.json` (only README, server-common.*, server-http.cpp, server.cpp are pinned);
  I verified them from the exact commit's raw files. Add the two files to the pin set if the
  negative controls are meant to be re-derivable offline.
- Process disclosure: one early `grep -rn "pass=24" .ufo corpus` traversed
  `.ufo/interactive-sessions/` and printed four transcript lines before I bounded the search.
  I did not use that output; the "was 24" support was re-derived from `git log --
  tools/test-snapshot.sh` and the round-2/4/5 lesson files.
- No tools installed or upgraded (pacman paused; no `uv`/binary install). Scratch was
  `/tmp/kama-r16-ReviewLesson/`, removed after writing this report.

## Concurrent working-tree drift (not mine)

Between my first `git status` (only untracked `build/completion-summary.json` and
`falsify/`) and the end of this review, 15 tracked files gained modifications — falsify
advice being integrated live (`measure.py` +34 with a matrix-digest pin,
`check-receipt.py` +145, `kama-llamacpp-live.py` +187, `SKILL.md`,
`corpus/knowledge/*`, `PROVINCE.md`). `corpus/lessons/round-16.md` is **not** modified
(`git diff --name-only -- corpus/lessons/round-16.md` → empty), so the citations above
still address the delivered lesson.

My probe rerun used the committed bytes: `current.json` reports
`probe_sha256 6edd3c4cfdf3…` equal to `run-after.json`. `tools/kama-probe.sh` was edited
after that run, but the diff is comment-only (`git diff -- tools/kama-probe.sh`), so the
72/72 and 55/17 results are unaffected. `check.py`'s later diff is docstring/help text
("3 embedded" → "4 embedded"), matching the 4/4 already observed.
