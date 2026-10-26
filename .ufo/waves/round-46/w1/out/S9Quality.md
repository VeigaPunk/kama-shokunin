# S9Quality — QUALITY.md criteria KQ66–KQ68 (round 46, calibration)

**Verdict:** Draft delivered append-only-ready — KQ66 (evidence durability), KQ67 (append-only self-description audited, partial events explained), KQ68 (machine-witnessed re-verification verdicts), 12-line block, `git diff`-shaped patch adds 13 lines and removes 0 (and applies: `git apply --check` exit 0); every factual claim in the three rows re-derived at base `0163fea2dab3f282ebd70c71da9ab5de4cedf733`. Three findings outside my file: KQ50 (digest census) and KQ55 (hexrun census) both fail their own stated exit-0 condition at the round-46 base, and one `corpus/QUALITY.md` heading's parenthetical is false for four rows. The citations to `corpus/lessons/round-46.md` resolve: the lesson seat (S9Lesson) added `## Mistakes` row 4 (`stale-premise, undisclosed partial`) for the two append-only partial events KQ67 requires explained; I did not edit that file.

## Deliverables

| File | What |
|---|---|
| `.ufo/waves/round-46/w1/out/S9Quality/criteria.md` | The append-ready block: heading `## Criteria added — round 46 (each cites corpus/lessons/round-46.md)` + KQ66/KQ67/KQ68 rows + provenance note. 8630 bytes. |
| `.ufo/waves/round-46/w1/out/S9Quality/criteria.diff` | Unified diff vs `corpus/QUALITY.md` at base; one hunk `@@ -378,3 +378,16 @@`; added 13, removed 0; the 13 added lines are byte-identical to the block (`block matches: True`). |
| `.ufo/waves/round-46/w1/out/S9Quality/checks.out` | Every command run for this seat with its observed output and exit code. |
| `.ufo/waves/round-46/w1/out/S9Quality/digest-base-details.out` | `digest-ledger.py --details` at base: the two `unknown` digests named. |
| `.ufo/waves/round-46/w1/out/S9Quality/hexrun-base-details.out` | `hexrun-census.py --details` at base: one summary line plus 267 per-token detail lines (`distinct=267`), the 21 `class=unknown` among them. |

## Evidence

All lane reads were read-only. Writes went to `/fast/scratch/hyaku/kama-r46/S9Quality/` (one `git clone --shared`, toplevel asserted equal to the clone dir before its one fixture commit; fixture identity `S9Quality-fixture <s9quality@invalid>`; that clone is deleted, receipt copied into the out dir).

### 1. Format, numbering, and the block's shape

- `grep -n '^## ' corpus/QUALITY.md` → last heading at line 369, `## Criteria added — round 44 (each cites corpus/lessons/round-44.md)`; `grep -oE '^\| KQ[0-9]+' corpus/QUALITY.md` → 65 rows, last `KQ65` at line 380. So KQ66–KQ68 continue the sequence with no collision; `grep -rn 'KQ6[6-9]\|KQ7[0-9]' .ufo/waves/round-46/` outside my own dir → no match.
- Structure check on the drafted block (python, run in the receipt): every table row splits into exactly 4 cells, ids `['KQ66','KQ67','KQ68']`, `bad: []`. Table header line 30 of `criteria.md` matches the file's column set `| ID | Admit only when | Reject or limit when | Motivating lesson |`.
- Append-only: the patch is a pure append after line 380; `removed lines 0` from the diff itself, and `git apply --check --verbose .ufo/waves/round-46/w1/out/S9Quality/criteria.diff` in the lane root → `Checking patch corpus/QUALITY.md...`, exit 0. `git status --porcelain corpus/QUALITY.md registry/ tools/` → empty, so the lane's addressed paths are untouched by this seat.
- The preamble of `criteria.md` records what each row does **not** supersede: KQ66 complements KQ43 (which covers receipt *outputs*: argv, revisions, gate digests), KQ67 supplements KQ22 (per-row `corpus/SOURCES.md` append-only via `tools/sources-append-only.py`) and KQ7 (append at end), KQ68 tightens the round-44 `holds-reworded`/`drifted` verdicts without touching KQ58's `behind`-status rule.

### 2. KQ66 — evidence durability (grounded in round-45 N-E and the round-46 sidecar)

- Round-45 receipts carry no locator: `.ufo/waves/round-45/c1/live/receipt-1.json` → `model = {"arg": "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf", "path": …, "sha256": "270cba1b…256d"}` — no URL. The emitter writes exactly those fields: `tools/kama-llamacpp-live.py:1359` (initial `{'arg','path','sha256'}`) and `:1411-1414` (`.update({'path': realpath, 'sha256': model_sha})`); `:1415-1416` only compares against `--model-sha256`.
- The registry cannot supply it: `grep '^| S485' corpus/SOURCES.md` (line 238) → `grep -c huggingface` = 0; the row names the model digest and the `on-release` recheck cell, no re-fetch text. Same at base for the b11889 binary URL, which lives in S484's `scope` cell (line 237) — that part is fine; the model is not.
- Round 46 has the missing record but not on a corpus-reachable path: `.ufo/waves/round-46/c1/live/model-fetch.txt` = `url https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf`, `size 1185376`, `sha256 270cba1b…256d (= expected …)`, `curl_exit 0`; `.ufo/waves/round-46/c1/live/install.txt` likewise records `asset llama-b11906-bin-ubuntu-x64.tar.gz 22478121 bytes sha256 064ade62…` and `c949950e… llama-server`. A wave directory is not the corpus: KQ66 therefore admits the URL "in the receipt's own input record, or in a committed sidecar the receipt's `corpus/SOURCES.md` row cites by path".
- Round-46 receipts still carry no URL (`receipt-1.json` `model` = arg/path/sha256 only), which is why KQ66 is drafted as a rule for the *next* receipt, not as a claim that round 46's is durable.
- Re-fetch evidence I verified for the row's own example: the model digest `270cba1b…` already has `registry/digest-ledger.tsv` row 6 (S039), and `/home/vgpnk/.local/opt/llama-b11889/llama-server` still hashes to `248e790d…` (`sha256sum`, matches S484's stated digest) — so a fresh session can re-fetch and re-hash today; the gap is the locator, not the bytes.

### 3. KQ67 — append-only self-description, partial events explained

- Ran the landed tool at base through the fixture clone (`checks.out`):
  `python3 tools/append-only-audit.py --repo ./lane-clone --to 0163fea2… --json` → `{"commits": 292, "events": 5, "restored": 3, "partial": 2, "unrestored": 0}`, exit 1; events `dd9f5dc6c0e6 SCORECARD.md 31/24 partial`, `0718b6abbda6 SCORECARD.md 2417/2416 partial`, `0718b6abbda6 LOG.md 2290/2290 restored 82b5e9d3`, `… corpus/QUALITY.md 375/375 restored`, `… corpus/README.md 663/663 restored` — identical to the frozen C2 receipt `.ufo/waves/round-46/controls/base.c2.out` (`lane_events=5 lane_partial=2`, same five event lines).
- Both partials are supersessions, and the row says so with the text that is missing: I recomputed the missing lines directly.
  - `dd9f5dc6c0e6`: 31 deleted, 7 missing at tip = six head-axis rows (`operability`, `freshness`, `depth`, `coverage`, `calibration`, `adjacency`) plus the prose line `Reconciled in round 41 against the measured commit (.tools/round41-scorecard-reconcile.py., claim C1)…`; that commit is `round-42: … SCORECARD head and README/PROVINCE reconciled (C1)`, and its diff adds 6 re-derived axis rows. Supersession.
  - `0718b6abbda6`: 2417 deleted, 1 missing at tip = the old `| depth | **7** | .SKILL.md sha256 91440eb8…` row; `82b5e9d3` (`depth re-anchor`) adds the current `| depth | **7** | … 3046955b…` row, which is at `SCORECARD.md:16` at base. Supersession.
- Why a base-to-tip diff is not the check: `git diff --numstat 6b8ccfb3 a553bd7c -- SCORECARD.md LOG.md corpus/QUALITY.md corpus/README.md corpus/SOURCES.md` → `7/0`, `50/4`, `4/0`, `4/0`, `23/1`. A delete-and-restore inside one range is invisible there and visible to the audit.
- Tool contract quoted from its docstring, not invented: first-parent `-U0` diff, deleted = `-` lines excluding `---`, restored by exact line text at `--to`, `restored_by` = first later commit holding every deleted line, exit 0/1/2, threshold 20 (`tools/append-only-audit.py:1-40`; CLI at `:295-303`).
- My draft does not ask for exit 0 at the tip (impossible while the two historical partials stand): it asks for the exit code plus an explained partial. The lesson's row 4 states exactly the two supersessions I recomputed here (2417/2416 → `82b5e9d3`'s `3046955b…` depth row; 31/24 → the round-42 head), so the KQ67 citation and my evidence agree.

### 4. KQ68 — machine witnesses on reworded/drifted verdicts

- Rule taken verbatim from the frozen counter's docstring (`tools/round46-release-recheck-audit.py`, WITNESS paragraph): `len(ws(witness_pin)) >= 12`, `ws(witness_pin) in P` and `not in RF`; `len(ws(witness_new)) >= 12`, `ws(witness_new) in R` and `not in PF`; note `>= 40` chars for `holds-reworded`, `drifted`, `removed`; `removed` → `witness_new` `-`. `ws()` collapses whitespace runs and strips.
- The shortcut the rule closes is frozen in the controls: `.ufo/waves/round-46/controls/junk-c1-massreworded.c1.out` → `pop=91 rows=91 valid=6 unverified=85 … met=False`, 85 rows rejected with `witness_pin rule (>= 12 chars, in pin ranges, absent from release file)`; `.ufo/waves/round-46/controls/junk-c1-carryforward.c1.out` → `valid=71 unverified=20`, where `S037`, `S043`, `S108` fail exactly that rule and the other 17 fail `holds needs every pair text-equal`. Both are the two ways a ledger can look complete without reading.
- The row also states the limit the counter cannot cross: a witness pair proves the anchored text moved, not that the reworded statement is still true (the counter's own docstring: "reworded vs drifted is the reader's call; the counter proves only that the anchored text moved") — hence the draft's requirement that a `holds-reworded` note record the reader's release-context read.

### 5. Draft integration check (fixture clone, not lane history)

On the clone at base plus one fixture commit `3000cb1d6be6b0f10265a6e5b9bfad62fd4c1d24` carrying the appended block:

| Command | Base | Draft tip |
|---|---|---|
| `hexrun-census.py scan` | `tokens=1453 distinct=267 lane_oid=169 md5_blob=1 upstream_ok=65 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=21`, exit 1 | `tokens=1454 distinct=268 lane_oid=170 … unknown=21`, exit 1 |
| `digest-ledger.py scan` | `tokens=104 blob=93 external_ok=4 external_absent=1 unverifiable=3 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=2`, exit 1 | identical, exit 1 |
| `append-only-audit.py --to` | `commits=292 events=5 restored=3 partial=2`, exit 1 | `commits=293 events=5 …`, exit 1 |

So the draft adds one lane-object token (the base commit id it cites), no new unknown hex run, no new digest, and no append-only event: it neither improves nor worsens the two inherited census failures in findings 1–2. The fixture clone and its commit id were scratch and are deleted per the operator directive; the id survives only in `checks.out`'s header, and the runs are re-derivable on any clone that applies `criteria.diff`.

## Findings

**F1 — digest census (KQ50) fails at the base; round 45 introduced it.**
Exact state: `python3 tools/digest-ledger.py scan --repo <clone> --rev 0163fea2…` → `unknown=2`, exit 1 (`checks.out`). The two, with `--details`: `2076290f3b80b7642e2dc165c01fbf1be386a56b4612ba45576d20527834d350` and `248e790dcfb3b04b4edef28884759219d1944cd47eebc29c5c9c7504b8baf7a7` — the b11889 release asset digest and the extracted `llama-server` digest stated in `corpus/SOURCES.md:237` (S484). `registry/digest-ledger.tsv` has 10 lines (header + 9 rows) and neither digest (`grep -c '2076290f3b80b7\|248e790dcfb3b0' registry/digest-ledger.tsv` → 0). `SCORECARD.md:2330` records `unknown=0` at round 43, so this is a regression, not inherited history.
Proposed fix (data, not code): append two rows to `registry/digest-ledger.tsv` — `248e790d… external llama.cpp b11889 extracted llama-server (S484) /home/vgpnk/.local/opt/llama-b11889/llama-server <correct> 2026-10-26 <note: re-hashed on this host today, equal to S484's stated digest>` (the file is present and hashes to it) and `2076290f… unverifiable llama.cpp b11889 release asset llama-b11889-bin-ubuntu-x64.tar.gz (S484) - - 2026-10-26 <note: asset not retained on this host; digest from gh api repos/ggml-org/llama.cpp/releases/tags/b11889 and the round-45 download, a re-download re-hashes it>`. My draft adds no digest, so the row set stays at 11.

**F2 — hexrun census (KQ55) fails at the base; rounds 44–45 introduced 21 unexplained runs.**
`python3 tools/hexrun-census.py scan --repo <clone> --rev 0163fea2…` → `unknown=21`, exit 1 (`checks.out`); `SCORECARD.md:2327` records `unknown=0` with 215 distinct tokens at round 43, base now has 267 distinct. The 21 are listed in `hexrun-base-details.out` (`class=unknown`); 11 of them are cited in `registry/release-recheck-b11889.tsv` (computed by intersecting that file's 32 distinct 40-hex runs with the unknown set), e.g. `0a14a9620961ff627348952112b4a9a6a0513c43` appears 36 times and is a llama.cpp object (`git -C /fast/scratch/hyaku/kama-r46/L1/llama.git cat-file -t 0a14a962…` → `blob`), not a lane object — so `lane_oid` cannot absorb it.
Proposed fix: for each of the 21, either a `registry/hexrun-ledger.tsv` `upstream` row whose `evidence` is a committed blob at the tip containing the token (a fetched upstream record; the recheck ledger itself qualifies but is weak evidence), or `unverifiable` with a reason ≥ 10 characters. Classifying them is a data task for the L1, not a criterion change.
Calibration note: my draft adds none of them (base 21 = draft tip 21).

**F3 — `corpus/QUALITY.md:369` heading is false for four of its rows.**
`369:## Criteria added — round 44 (each cites `corpus/lessons/round-44.md`)` governs the table at 371–380, but rows `377-380` (`KQ62`, `KQ63`, `KQ64`, `KQ65`) cite `corpus/lessons/round-45.md` in their last cell. Command: `awk 'NR>=369&&NR<=380' corpus/QUALITY.md`; `sed -n '377,380p' corpus/QUALITY.md`. Round 45 added criteria without a heading of its own, so the round-44 section's parenthetical now misstates four rows.
Proposed fix (append-only, KQ7/KQ14 — do not rewrite line 369): append a qualification paragraph after line 380 naming KQ62–KQ65 as round-45 criteria whose motivating lesson is `corpus/lessons/round-45.md`, then let the round-46 heading (my block) follow it. My draft is written so the new heading carries the correct citation and does not inherit the error.

**F4 — resolved during the wave: the lesson's `## Mistakes` row 4 now carries the append-only partial explanation KQ67 requires.**
`corpus/lessons/round-46.md` did not exist at base; the wave draft at `.ufo/waves/round-46/w1/out/S9Lesson/round-46.md` now has rows `1 evidence-durability`, `2 wave-stall-blind`, `3 dead-pointer`, `4 stale-premise, undisclosed partial` (row 4 added after I sent the seat the two events with counts, missing text and superseding commits). KQ67's last cell cites row 4 and `## Gate`. That seat also reports a classifier receipt I did **not** run (`out/S9Lesson/probe-append-partial.py` → its `append-partial-base.out` `partials=2 missing=8 superseded=7 prose-dropped=1 lost=0` exit 0, and `lost=2` exit 1 under `--inject`) — quoted as its author's claim, available to the L1 as the "shown able to fail" leg if KQ67 needs one.
Correction that shapes KQ67's wording: the two partials do **not** make C2 fail. `tools/round46-append-audit-check.py`'s `lane` leg requires the tool's exit code to *agree* with the recomputed events, not that no partial exists; `.ufo/waves/round-46/controls/base.c2.out` is `met=False` because the tool, its selftest and the table are absent at base (`detail: tools/append-only-audit.py absent at tip`). The defect KQ67 targets is the undisclosed status. That clause is now in the row's reject cell.

## What I did not do (limits)

- I did not run either frozen claim counter (C1, C2); their outputs quoted here are the committed controls and my own read-only tool runs.
- I did not run S9Lesson's draft `probe-receipt-durability.py`; its exit claims are its author's, not observed by me.
- I did not edit `corpus/QUALITY.md`, `corpus/lessons/`, any registry, or any lane file; the patch is in my out directory only. No jj or git mutation in the lane; the one fixture commit is in my scratch clone under a fixture identity.
- No tool was installed or upgraded; no pacman transaction was attempted; no network fetch was made (the model/binary URLs are quoted from committed round-46 evidence and from round-45's closure).
- KQ66 is not machine-enforced by any lane instrument today: the check it names is a two-command recipe (`grep -F` for the URL, `curl -fL` + `sha256sum`). That is stated in the draft rather than papered over with a tool name.
- Scratch `/fast/scratch/hyaku/kama-r46/S9Quality/` deleted after copying receipts; `TMPDIR` was inside it for every run.

## Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Quality.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Quality/criteria.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Quality/criteria.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Quality/checks.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Quality/digest-base-details.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S9Quality/hexrun-base-details.out`
