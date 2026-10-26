# X2Fixtures — round 49, lane kama: edge fixtures for append-only-audit v4

**Verdict: 11/11 hand predictions matched the tool at 74558c71 (2/2 controls too), and the fixture set finds four v4 behaviours that diverge from v4's stated purpose (two of them causally isolated by controls), plus one rename blindness in the event machinery — all four escapes are latent on the lane at the measured commit (the v5 prototype that closes them is byte-identical on the lane: 5 events, 82 ungraded lines, exit 0).**

## 1. What was measured

| item | value |
|---|---|
| tool artifact | `tools/append-only-audit.py` extracted from lane commit `74558c71c38ceaeace15fd4cf8aa9d84977584b1`, sha256 `3bae58a391bc7a859446c68e632d79b593cf6b286f3599c359899699427eb0ed` (copy: `out/X2Fixtures/tool-at-74558c71.py`, 997 lines) |
| threshold | default 20 (all fixtures use 25-line drops) |
| contract | passed with `--contract` from `$S/contracts/*.tsv`; rows in the fixture's own form of the lane's SCORECARD row (`exempt=## Axes@NOTES.md:2`) |
| fixtures | 11 scenarios + 2 controls, each a fresh `git init` under `/fast/scratch/hyaku/kama-r49/X2Fixtures` with `git rev-parse --show-toplevel` asserted equal to the fixture dir before the first commit; every git call names `-C <fixture>`; throwaway identity via `-c user.name/-c user.email/-c commit.gpgsign=false` only on `git commit` |
| command | `S=/fast/scratch/hyaku/kama-r49/X2Fixtures; export S TMPDIR=$S OUT=…/out/X2Fixtures; python3 "$OUT/run-fixtures.py"` → exit 0, `agree=11/11`, `controls agree=2/2` |
| tool self-check | `python3 tool.py --selftest --scratch $S/st` → `AOA_SELFTEST pass=30 fail=0` (exit 0) |
| hand expectations | `expectations.json` mtime `1793057403.3053133` < first run `1793057530.8172398` (`expectations_before_runs=true`); addendum and controls similarly before their own runs (`compare.json`) |

Method: predictions were derived by hand from the v4 definitions (`sections()` at `tools/append-only-audit.py:265`, `origins()` :423, `file_regions()` :384, the prefix filter :472, the carve-out gate :475, `vanished()` :291, the `not files` skip :445, `exit_code()` :528) **before** any fixture was built or run. Two fields are recorded per scenario: `predicted` (what the definitions compute) and `intended` (what v4's purpose in the docstring :1-40 implies). `agree` = tool vs predicted; `intended_met` = tool vs purpose.

One transparency note: the first run reported `deleted=20` on `star-plus-exempt-row`. That was my fixture's label collision (`o20..o24` appeared in both label sets, so git matched 5 common lines); the prediction of 25 for distinct text was right and the tool was right. Labels were corrected and everything re-run from empty fixture dirs. The only post-first-run addition, `only-plus-exempt-rows`, has its prediction in `expectations-addendum.json` written before its own run.

## 2. Results

| # | fixture (axis) | actual (tag, deleted, graded, ungraded, status) | exit | agree | intended_met |
|---|---|---|---|---|---|
| 1 | `fence-heading-move` — heading inside a fenced block whose lines move | c3 25/0/25 ungraded | 0 | **yes** | **no** |
| 2 | `crlf-dated-to-head` — CRLF dated text moved byte-exact into the head | c3 25/25/0 unrestored | 1 | yes | yes |
| 3 | `crlf-normalized-move` — same move with CRLF→LF in the move commit | c2 25/25/0 unrestored, c3 25/0/25 ungraded | 1 | **yes** | **no** |
| 4 | `crlf-normalized-subthreshold` — same, split 13+12 below threshold | c4 25/0/25 ungraded | **0** | **yes** | **no** |
| 5 | `preamble-to-head-dropped` — preamble line moved into the head and dropped | c3 25/25/0 unrestored | 1 | yes | yes |
| 6 | `two-rows-two-titles` — two rows, two different exempt titles | c3 25/0/25 ungraded | 0 | yes | yes |
| 7 | `star-plus-exempt-row` — one `*` row and one `exempt` row for one file | c2 25/0/25 ungraded | 0 | **yes** | **no** |
| 8 | `rename-declared-away` — declared file renamed (no-renames diff) | none; vanished `SCORE.md` | 1 | yes | yes |
| 9 | `rename-within-wildcard` — renamed inside `corpus/lessons/*.md` | none; vanished `corpus/lessons/r1.md` | 1 | yes | yes |
| 10 | `rename-into-declared` — undeclared file renamed onto a declared path | none | 0 | yes | yes |
| 11 | `only-plus-exempt-rows` — one `only=` and one `exempt=` row, one file | c2 25/0/25 ungraded | 0 | yes | yes |
| C1 | `fence-control-no-fence` — same fixture, no fence, no quoted heading | c3 25/25/0 unrestored | 1 | yes | yes |
| C2 | `star-control-star-only` — same file/commit, only the `*` row | c2 25/25/0 unrestored | 1 | yes | yes |

## 3. Findings

### F1 (defect, calibration) — `sections()` is fence-blind, so a quoted `## ` heading makes a home in the exemption

`tools/append-only-audit.py:265-272` treats *any* line starting with `b"## "` as a title, fences included. `origins()` (:423) reuses it, so text born under a quoted `## Axes` inside a fenced block has `origin = {'## Axes'}` and the gate at :475 keeps it ungraded when it is later dropped from the real head.

- Fixture: `fence-heading-move`, contract row `SCORE.md … exempt=## Axes@NOTES.md:2`; c1 has `## Round 1` … ```` ``` ````, `## Axes`, 25 f-lines, ```` ``` ````; c2 moves the 25 lines into the real head (diff 9 deletions, no event); c3 deletes them there and adds 30 regrow lines.
- Command/output: `python3 tool.py --repo <fx> --to HEAD --contract fixtures.csv --json` → `deleted=25 graded=0 ungraded=25 status=ungraded`, **exit 0** — 25 dated-section lines gone, audit green.
- Causally isolated: `fence-control-no-fence` is the same fixture with the 25 lines born plainly under `## Round 1` → `deleted=25 graded=25 unrestored`, exit 1.
- Not covered anywhere: the C2 counter's eight fixtures (launder, native-head, dated-loss, substring, word-token, negated, wildcard-self, wildcard-named) and the tool's 30 selftest cases (the two CRLF cases, `crlf-and-eof` / `crlf-restore-exact`, run with `--files`, i.e. with no contract and no titles) contain no fenced-heading case. The C2 counter has the same blind `sections()` at `tools/round49-append-audit-v4-check.py:233` and the same origin gate at :354, so it cannot catch it either.
- Latent today: scanning every contract-matched file at 74558c71 for a `## ` line inside a fence gives 0 hits (`SCORECARD.md`, `corpus/QUALITY.md`, `corpus/README.md`, `LOG.md`, `corpus/SOURCES.md`, both `corpus/knowledge/*.md`, `registry/report-landing-errata.tsv`); only `SCORECARD.md` carries exempt titles at all.
- Proposed fix (proposal only, definitions are frozen): `out/X2Fixtures/proposed-v5-definitions.diff` hunk 1 makes `sections()` fence-aware (opening ```` ``` ````/`~~~` at ≤3 spaces indent, matching close, quoted heading ignored). Verified: under the prototype (`tool-v5.py`) this fixture becomes `c3 25/25/0 unrestored`, exit 1, and the control is unchanged.

### F2 (defect, calibration) — a `*` row cannot tighten a file another row exempts; the union silently prefers the looser row

`file_regions()` (`tools/append-only-audit.py:384-392`) collects only `exempt` titles and `only` prefixes; a `*` row contributes nothing, so a file matched by both `*` and `exempt` is graded by the exempt row alone.

- Fixture: `star-plus-exempt-row`, rows `SCORE.md … *` and `SCORE.md … exempt=## Axes@NOTES.md:2`; c2 rewrites the 25 `## Axes` lines in place.
- Command/output: `deleted=25 graded=0 ungraded=25 ungraded`, **exit 0**.
- Causally isolated: `star-control-star-only`, identical file and commit with only the `*` row → `deleted=25 graded=25 unrestored`, exit 1. So the second row is the only cause.
- Contract exposure: `parse_contract()` (:179-200) accepts duplicate patterns for one file with conflicting regions, and neither the tool nor the C2 counter reports it (`bad_declarations=0` in both fixtures). The lane's own contract has no duplicate path today, so this is latent.
- Proposed fix: hunk 2 of the diff — a matching `*` row returns `(set(), [])` for that file (whole-file grading dominates); alternatively (and cheaper to freeze) reject a file matched by both a `*` row and an `exempt`/`only` row at parse time. Verified under the prototype: `c2 25/25/0 unrestored`, exit 1; `only-plus-exempt-rows` (no `*`) and `two-rows-two-titles` (two exempt titles) are unchanged, so the fix does not disturb the intended union semantics.

### F3 (defect, calibration) — line-ending normalisation re-births text in the exempt head; split below threshold it escapes entirely

`origin(l)` keys on the exact byte string, so the LF copy of a CRLF dated line is first held in the head and gets `origin = {'## Axes'}`.

- Fixture `crlf-normalized-move`: c2 moves the 25 CRLF dated lines into the head and writes them LF (`deleted=25 graded=25 unrestored` at c2 — the normalisation itself is read as a 25-line loss, and that is the only reason the run exits 1); c3 deletes the LF lines from the head → `deleted=25 graded=0 ungraded=25 ungraded`, **exit 0 for that event**.
- Fixture `crlf-normalized-subthreshold` removes the accidental alarm: the normalising move is split into 13 and 12 deletions (`git diff --numstat --no-renames` per commit: `13 13`, `12 12`, `30 25` — the first two are below `--threshold 20` and raise no event), then c4 deletes the 25 LF lines → single event `deleted=25 graded=0 ungraded=25 ungraded`, **exit 0**, summary `events=1 ungraded_lines=25 unrestored=0 partial=0`. 25 dated lines are gone and the audit is green.
- The byte-exact move (`crlf-dated-to-head`) is graded correctly (`c3 25/25/0 unrestored`, exit 1), which isolates normalisation as the cause.
- Proposed fix: hunk 3+4 of the diff — key origin lookups on the text with one trailing `\r` stripped (`origin_key()`), leaving restoration byte-exact. Verified under the prototype: `crlf-normalized-move` → c2 and c3 both `25/25/0 unrestored`; `crlf-normalized-subthreshold` → c4 `25/25/0 unrestored`, exit 1.
- Residual limit of the proposal (state it, do not hide it): any *other* normalisation (trailing whitespace, rewrapped line, unicode NFC/NFD) still re-births text; the origin key would need to be a content hash of the normalised line, which is a larger definition change.

### F4 (observation, not a defect — but the loss size is unreported) — a rename is invisible to the event machinery; only `vanished` fires, with a bare path

With `--no-renames` everywhere (:293, :308, :375) a rename of a declared file is a full-file deletion, but `files` is expanded at `<to>` only (:409) and `audit()` skips every commit when that set is empty (:445), so the deleted hunk never reaches `deleted_lines()`.

- Fixture `rename-declared-away`: `git diff --numstat --no-renames HEAD~1 HEAD` → `0 53 SCORE.md`, `53 0 OTHER.md`; tool JSON → `files=[] events=[] vanished=['SCORE.md'] unmatched_patterns=['SCORE.md']`, exit 1.
- Fixture `rename-within-wildcard`: `files=['corpus/lessons/r2.md'] events=[] vanished=['corpus/lessons/r1.md']`, exit 1 — the 30 deleted lines of `r1.md` are in no event.
- Fixture `rename-into-declared`: `events=[] vanished=[]`, exit 0 — correct (arriving at a declared path is an addition).
- So a rename does exit 1, but the receipt carries no deleted/graded count for it, and a rename *within* the declared set is likewise only a path name. Proposed fix (hunk 5): expand `files` over every path any commit up to `<to>` held under a contract pattern, so the rename's deletion is graded like any other. Verified under the prototype: `rename-declared-away` → `c2 53/53/0 unrestored` plus vanished; `rename-within-wildcard` → `c2 30/30/0 unrestored` plus vanished; `rename-into-declared` still exit 0.
- This hunk changes the audited file set, so it deliberately fails one v4 selftest case (`vanished-and-paths` asserts the tip-only `files` list; prototype: `AOA_SELFTEST pass=29 fail=1`). Any v5 must update that case to expect the historical path in `files` plus its graded deletion event.

## 4. Confirmed-correct semantics (no change proposed)

- Preamble text has `origin = {None}` and `None` is never an exempt title, so preamble text moved into the head and dropped is **graded** (`preamble-to-head-dropped`: c3 `25/25/0 unrestored`, exit 1). This is the case the round-48 selftest added (`preamble-graded`) extended to a move-then-drop.
- Two exempt titles on one file are a union, and text born under either is exempt text: `two-rows-two-titles` c3 `25/0/25 ungraded`, exit 0 — the v4 origin rule read literally, and defensible because the contract declares both titles re-derived in place.
- `only=` + `exempt=` on one file: the prefix filter (:472) runs before the origin gate, so a line outside the `only` prefix is never graded, regardless of titles (`only-plus-exempt-rows`: c2 `25/0/25 ungraded`, exit 0). Consistent with both rows; worth recording because the `only` rule is an exemption by silence.
- Byte-exact CRLF text is graded through the exemption (`crlf-dated-to-head`).
- Renaming *onto* a declared path is silent and correct (`rename-into-declared`).

## 5. Prototype verification and lane no-op

Proposal applied to a copy of the tip artifact (`$S/tool-v5.py`; diff validated with `patch -p1 --dry-run` in a scratch tree, "checking file tools/append-only-audit.py"). Fixture cohort under the prototype (13/13):

```
fence-heading-move            exit 1  c3 25/25/0 unrestored
crlf-dated-to-head            exit 1  c3 25/25/0 unrestored
crlf-normalized-move          exit 1  c2 25/25/0 unrestored, c3 25/25/0 unrestored
crlf-normalized-subthreshold  exit 1  c4 25/25/0 unrestored
preamble-to-head-dropped      exit 1  c3 25/25/0 unrestored
two-rows-two-titles           exit 0  c3 25/0/25 ungraded
star-plus-exempt-row          exit 1  c2 25/25/0 unrestored
rename-declared-away          exit 1  c2 53/53/0 unrestored    vanished ['SCORE.md']
rename-within-wildcard        exit 1  c2 30/30/0 unrestored    vanished ['corpus/lessons/r1.md']
rename-into-declared          exit 0  -
only-plus-exempt-rows         exit 0  c2 25/0/25 ungraded
fence-control-no-fence        exit 1  c3 25/25/0 unrestored
star-control-star-only        exit 1  c2 25/25/0 unrestored
```

Lane leg at the measured commit, tip artifact vs prototype on a `git clone --shared` of the lane (read-only):

```
tip exit=0  files 92 events 5 ungraded_lines 82 vanished [] bad_decl 0 partial 0 unrestored 0 regressed 0
v5  exit=0  files 92 events 5 ungraded_lines 82 vanished [] bad_decl 0 partial 0 unrestored 0 regressed 0
event lists identical True (n=5)
```

So all four escapes are latent on the lane's current state, and the proposal would not change today's C2 lane receipt.

Artifact-identity control: during this seat's run the lane worktree carried an uncommitted integration edit to the same file (`sha256 5d6c33c0…`, +19/−6, `tools/append-only-audit.py`, negation widening from seat K2Negation). Running all 13 fixtures against that worktree copy reproduces the tip artifact's JSON and exit codes exactly (`identical_to_tip_artifact True fixtures 13`), so nothing here depends on the tip-vs-worktree difference.

## 6. Risks and limits

- The four fixes change the frozen v4 definitions; they belong to a declared v5 with its own counter and preregistration (round 50), not to an in-place edit. The diff is a proposal in this seat's out directory, not applied anywhere.
- F3's fix closes CRLF only; other text normalisations still re-birth lines (stated above).
- F4's fix widens the audited set and breaks one existing selftest case by design; it must be paired with a counter fixture asserting the rename's graded deletion.
- F1's severity depends on someone adding a fenced `## ` line to `SCORECARD.md`; 0 such lines at 74558c71 (measured), so the hatch is latent, not live.
- Fixture commit ids in `results/*.json` belong to ephemeral repos that were removed; the retained evidence is the per-commit `git diff --no-renames -U0` text, git logs, tip snapshots and contract text inside `results/*.txt`, plus the tool JSON in `results/*.json`.
- No tool was installed or upgraded; no service was started or stopped; `pgrep -f llama-server` shows no process started by this seat (the only llama-server entries are other seats' `kama-llamacpp-live.py` workers, untouched). Scratch `/fast/scratch/hyaku/kama-r49/X2Fixtures` removed after the results were copied.

## 7. Files written

Out dir `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X2Fixtures/`:

- `expectations.json` — hand predictions, written before any run (mtime 1793057403.3053133)
- `expectations-addendum.json` — `only-plus-exempt-rows` prediction, before its own run
- `controls.json` — the two causal controls, before their own run
- `run-fixtures.py` — driver: builds every fixture, runs the tool with `--json`, writes results, compares to the expectations
- `compare.json`, `compare.txt` — per-scenario verdicts, want/got, mtimes, run times
- `results/<fixture>.json` — tool JSON + exit + stderr + fixture commit tags
- `results/<fixture>.txt` — git log, per-commit `diff --no-renames -U0` text, tip file snapshots, contract text
- `results/lane-tip.json`, `results/lane-v5.json` — lane leg at 74558c71, tip artifact vs prototype
- `results/v5-prototype.json` — prototype outcomes for all 13 fixtures
- `tool-at-74558c71.py` — the measured artifact (sha256 `3bae58a3…`)
- `results/v5-prototype.py` — the prototype that produced the v5 outcomes (sha256 `199c89db…`), reproducible by applying the diff to `tool-at-74558c71.py`
- `proposed-v5-definitions.diff` — five hunks against `a/tools/append-only-audit.py` (fence-aware `sections()`, `*`-row dominance, CRLF origin key, history-wide contract set)

Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X2Fixtures.md`
