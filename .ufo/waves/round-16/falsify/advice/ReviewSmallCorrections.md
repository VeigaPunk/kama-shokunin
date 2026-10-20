VERDICT: partial — the four knowledge-file appends are substantively accurate and textually append-only, but the set-wide "append-only / no prior line rewritten" claim is false for registry/endpoint-consumers.tsv:32 (1 deletion, 1 insertion), and consumer-registry.md:408's “gains” wording claims a change to lines 84-85 that the diff does not contain.

## What I ran (exact commands, exits)

- `git rev-parse HEAD` → b8e485cc6b201c8e4604a20808e58babbfe08e34 (exit 0).
- `git status --porcelain -- <the five paths>` → empty (exit 0): the reads below are the committed b8e485c bytes.
- `git diff --numstat 20e392e b8e485c -- <the five paths>` (exit 0):
  `8 0 corpus/knowledge/consumer-registry.md`, `10 0 corpus/knowledge/listener-census.md`,
  `9 0 corpus/knowledge/ollama-evidence-replay.md`, `10 0 corpus/knowledge/snapshot-history.md`,
  `1 1 registry/endpoint-consumers.tsv`.
- `git diff -U0 20e392e b8e485c -- <the four .md paths>` (exit 0) → one pure EOF insertion per file:
  `@@ -404,0 +405,8 @@`, `@@ -387,0 +388,10 @@`, `@@ -374,0 +375,9 @@`, `@@ -104,0 +105,10 @@`.
  The TSV hunk is `@@ -32 +32 @@` with one `-` and one `+` line.
- `git diff --check` (exit 0); `git diff --summary` (exit 0, empty: no mode/rename changes).
- `bash tools/test-snapshot.sh` (exit 0): 30 `PASS` lines, `RESULT pass=30 fail=0`.
- `KAMA_PROBE=$PWD/.ufo/waves/round-16/frozen/kama-probe-before.sh bash tools/test-snapshot.sh` (exit 1):
  27 `PASS`, `RESULT pass=27 fail=3`; the three FAILs are exactly `MODEL_LOADING baseline row accepted and diffed`,
  `MODEL_LOADING baseline row dropped as malformed`, `MODEL_LOADING baseline row warned as malformed`.
- `awk 'NR==32' registry/endpoint-consumers.tsv` → `#   MODEL_OK | ... | NOT_HTTP | MODEL_LOADING` (exit 0).
- `grep -n '503' corpus/knowledge/listener-census.md` → only lines 393 and 396 (the appended block); no census row (exit 0).
- `grep -n 'VOCAB=' tools/kama-probe.sh` → line 62 `VOCAB="MODEL_OK MODEL_MISMATCH FOREIGN_SERVICE UNAUTHORIZED_SERVICE DEAD NOT_HTTP MODEL_LOADING"` (exit 0).
- Receipt probe argv (`.ufo/waves/round-16/live/receipt.json`, `receipt-frozen-probe.json`):
  `check --port 32845 ...` and `check --port 39375 ...`; registry declared ports are only `:34113` and `:8080`
  (`cut -f4 registry/endpoint-consumers.tsv | grep -oE ':[0-9]+' | sort -u`).
- `pgrep -x llama-server` after both harness runs → empty (exit 1 from pgrep, i.e. no process; no llama-server was started by me).

## Findings (severity order)

### 1. Medium — "no prior line rewritten" is false for the TSV, though the rewrite is the named correction
`git diff --numstat` reports `1 1` for `registry/endpoint-consumers.tsv`, and `git diff -U0` shows
`@@ -32 +32 @@`: the prior line
`#   MODEL_OK | MODEL_MISMATCH | FOREIGN_SERVICE | UNAUTHORIZED_SERVICE | DEAD | NOT_HTTP`
was replaced in place. The replacement is correct — it matches `tools/kama-probe.sh:62` (VOCAB) and
`:117`, and the emitted verdict token — and an in-place edit is inherent to the explicitly named
`:32` correction. But the acceptance predicate as written covers "those paths" and is therefore
refuted for the TSV. If the predicate is scoped only to the four `.md` appends, it is confirmed.
No data row changed (line 32 is a header comment).

### 2. Low — consumer-registry.md:408 claims the unchanged list gained the verdict
Line 408 reads: “The ‘binding vocabulary’ list at lines 84-85 gains `MODEL_LOADING`.” Lines 84-85
still list exactly six verdicts and contain no `MODEL_LOADING` (an `awk` read of NR 84-85 shows the
list ending `DEAD` | `NOT_HTTP`). The appended section supplies the seventh definition, so the
document as a whole documents seven, but the sentence states that the list itself changed. The
corpus already has the precise convention for this case: `endpoint-identity.md:189` says line 3's
list "are superseded".
Recommend "The binding vocabulary is extended by this correction; lines 84-85 remain textually at
six" (or similar explicit supersession).

### 3. Low — ollama-evidence-replay.md:376 mislabels the provenance
`(appended round 16, outside round-15 routed defect 5)` contradicts the note's source: this exact
precision item *is* routed defect 5 (`corpus/lessons/round-15-verifier-spotcheck.md:169` —
"Replay entry:332–334 ... Append precision rather than imply short-circuiting"), and the build advice
calls the proposed sentence "the complete deliverable of routed defect 5"
(`.ufo/waves/round-16/build/advice/ReviewReplayProsePrecision.md:57`). The technical text itself is
accurate (checked below). "outside" should be dropped or inverted; as written it can be read as
saying defect 5 remains unaddressed.

### 4. Info — listener-census.md:391-392 wording ("premise were applied")
"§9's requested clause ... and its line-363 premise were applied by the probe as rule 5" applies a
premise as if it were a rule. `endpoint-identity.md:17` is the status-agnostic rule 5; the probe's
corresponding generic path is `tools/kama-probe.sh:563-566` (`non-2xx-non-model-http`). The
substantive claim (the clause is implemented; the 4xx text/plain rows still grade
`FOREIGN_SERVICE`) is confirmed; only the grammar conflates premise and clause.

## Confirmed content (no defect found)

- **listener-census.md:389-397** — `endpoint-identity.md:17` rule 5 is status-agnostic for non-2xx
  non-401/403; `tools/kama-probe.sh:503-508` carves out only the exact 503 loading envelope before
  that fallback; `grep -n '503'` finds no census row, so "None of this census's rows was a 503" and
  "no verdict recorded here changes" hold. The sibling falsify run
  (`KamaR16.ExecListenersSummary`) used `listeners --port 37883` against a synthetic stub — a
  single-port override probe, not the `ss -ltn` enumeration the claim calls a census [INFERENCE from
  its own report: "the no-flag `ss -ltn` enumeration path was not attacked"].
- **snapshot-history.md:106-114** — reproduced `RESULT pass=30 fail=0` (30 PASS lines) and the
  historical `RESULT pass=24 fail=0` is at line 66. The six added checks are the six new
  PASS-producing statements (24→30). `"schema": "kama-probe/v2"` is present in the current probe
  (`tools/kama-probe.sh:1063`) and the frozen copy (`kama-probe-before.sh:1019`). The rollback claim
  is confirmed dynamically: the frozen probe drops the seeded `MODEL_LOADING` baseline row as
  malformed and warns (27/3 run above), while the near-miss `MODEL_LOADED` is dropped by both.
- **ollama-evidence-replay.md:376-383** — `corpus_problems()` is at
  `.ufo/waves/round-14/measure.py:351-365`; the duplicate problem is appended first (lines 359-360)
  and `unique < MINIMUM_UNIQUE_CASES` is still evaluated (lines 361-364), so both problems can be
  reported. `run()` at `:375-381` builds `unmeasured_record` rows (`passed: False` at `:174`) and
  the exit is `EXIT_FAIL` (=1, `:72`) at `:396-398`; the child branch is `elif tool_present:` at
  `:382`, so no child is spawned. Exact.
- **consumer-registry.md:406-412** — the seven-verdict vocabulary and "MODEL_LOADING ... drift,
  exit 2" match `tools/kama-probe.sh:503-508` and the probe's non-`MODEL_OK` drift handling. The
  live receipts probed only unregistered ports (32845, 39375); the registry declares only
  34113/8080, and the controls refuse 34113/8080 before any connect
  (`tools/kama-llamacpp-live.py:57,237-238`; `.ufo/waves/round-16/live/controls.txt`). "No consumer
  row or live verdict in this file changes" is therefore accurate.
- **registry/endpoint-consumers.tsv:32** — the new seventh token matches the probe VOCAB exactly;
  no consumer data row changed (the hunk is the comment line only).

## Limitations

- Static reads of committed bytes plus two hermetic harness runs; I did not run
  `tests/probe-verdicts/check.py`, `.ufo/waves/round-14/measure.py`, or any llama-server (other
  seats / L1 own those; `measure.py` is forbidden to me).
- Findings 2-4 are wording/provenance precision, not false technical claims; L1 may accept them
  as-is. Finding 1 is a scope/literal-predicate defect, not a content defect — the TSV rewrite is
  correct and necessary.
- The frozen-probe test run was used only to check the documented rollback limit; its exit 1 is the
  expected result of running the new harness against the old probe, not a defect in the current
  probe.

## Installs

None.
