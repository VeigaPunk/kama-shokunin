VERDICT: partial — every §4/§6 report item maps to lane evidence at 54a2926 except four gaps: the report file itself, the end-of-round census output, a real commit hash in LOG.md (SCORECARD's pointer dangles), and wave-2 completion/dead-seat evidence (falsify dir still untracked).

# ReportReadiness — kama round-17 falsify wave

Seat: KamaR17.ReportReadiness. Attacked object: the round-17 report contract
(`/home/vgpnk/Projects/shokunin/.ufo/prompts/kama-round-17.md` §4 and §6) against lane
evidence at `54a29268e2083caa2b1e0d54ee1e7d90961302f3` (lane branch master; working tree
equals that commit outside `.ufo/waves/round-17/falsify/`, verified with
`git diff --stat 54a2926 -- . ':!.ufo/waves/round-17/falsify'` → empty, exit 0).
I did not verify claim truth; other seats own that. This maps required items to evidence.

## Required items → evidence (round commit)

Status vocabulary: PRESENT (pointer exists and resolves), PRESENT-WEAK (pointer exists
but is prose, or resolves only after reconstruction), MISSING (no lane evidence), PENDING
(wave still in flight / not yet written).

### §4 required sections

| # | Required item | Evidence at 54a2926 | Status |
|---|---|---|---|
| 1a | **Work performed** opens naming claims (1–3) and target axes/capability | `SCORECARD.md:645-670` (§Round 17, C1 calibration, C2 operability); `corpus/lessons/round-17.md:13-53` (§Declared claims) | PRESENT |
| 1b | One bullet per work item, each with an evidence pointer | `LOG.md:992-1025` (round-17 entry bullets); `.ufo/waves/round-17/build/advice/` 82 seat reports; `.ufo/waves/round-17/build/completion-summary.json` (`advice_reports: 82`, `missing_reports: []`); `.ufo/waves/round-17/build/drafts/` 15 paste-ready drafts | PRESENT |
| 2 | **Landed changes** — every change tied to a LOG.md entry **and the commit hash that carries it** | Files are in the commit (`git show --name-only 54a2926`); `LOG.md:1013-1025` lists the landed paths **without any hash**; `SCORECARD.md:674-676` says "hash in `LOG.md` §round 17" — that hash is absent (grep for `54a2926`/`54a29268` in LOG.md, SCORECARD.md, lesson → exit 1) | PRESENT-WEAK — dangling hash pointer |
| 3 | **Before → after measurements**, one per claim, counting command, commit measured against | C1 raw: `.ufo/waves/round-17/runs/fault-controls-frozen.json` (`accepted 3`, `detected 5`, `check_sha256 b853576e…`, exit file `1`) and `fault-controls-current.json` (`accepted 0`, `detected 8`, `check_sha256 ddc3f3cc…`, exit `0`); grid `runs/mutants-grid.json` totals cells killed/applicable = 1/8, 7/8, 1/10, 10/10. C2 raw: `runs/controls-frozen.json` (`accepted_bad 6`, 1 inconclusive), `runs/controls-current.json` (`accepted_bad 0`), `live/receipt-{1,2,3}.json` (`kama-llamacpp-live/v2`, 11 checks each), `live/gate.txt` (VALID ×3, probe `36b64978…`, tool `0efd1723…`). Commands: `SCORECARD.md:678-681`, `corpus/lessons/round-17.md:152-172` | PRESENT for outputs; the "commit measured against" is MISSING as an artifact — no run file names a lane revision; it is recoverable only by digest (see Findings F2) |
| 4a | **Sources & frontier** — SOURCES rows before→after with counting command | Start output retained: `.ufo/waves/round-17/sources-before-validate.txt` (exit 0, W04 S031 only). **End-run output absent**: no `sources-after*`/census end file exists under `.ufo/waves/round-17/` (grep over the wave dir finds none). Counts 41→46 are reproducible: `sources-census.sh census --file …` gives rows 41 / tier.A 38 / status.mined 31 at cff9e62 and 46 / 43 / 36 at 54a2926; `validate` mode prints **no row counts**, so the cited "Sources validate exit 0; rows 41 → 46" (`SCORECARD.md:689-690`) mixes two different commands | PARTIAL — before PRESENT, after MISSING |
| 4b | Rows added by tier | `corpus/SOURCES.md:54-58` — S042–S046, all tier `A`; tier census 38 A / 3 C → 43 A / 3 C (B = 0) | PRESENT |
| 4c | Rows touched old→new | None: `corpus/lessons/round-17.md:74-79`; guard `tools/sources-append-only.py`; selftest `runs/selftest-tools_sources-append-only.py_--selftest.txt` (14/14, exit 0); build run `build/advice/SourcesAppendOnly.md` (`ccc4bb3→master`, exit 0). My clone rerun at the round range `cff9e62→54a2926`: only S042–S046 added, `violations: []`, exit 0 | PRESENT (cite a round-range run, not only ccc4bb3→master) |
| 4d | Frontier rows advanced | `corpus/README.md:234-243` (Round-17 coverage row + "Frontier disposition: … now held … Still open: router mode and sleep, other engines, K05…"); `corpus/QUALITY.md:121-123` (KQ20–KQ22); `corpus/lessons/round-17.md:54-79` (§Gate) | PRESENT |
| 5 | **Trend verdicts** — expansion, quality, discernment, with evidence | `SCORECARD.md:698-702` (author: expansion unchanged, quality improved, discernment unchanged); discernment basis `corpus/lessons/round-17.md:182` ("no non-author admit/reject sample exists for this round yet"); no round-17 verifier spot-check exists (`corpus/lessons/` has none past round-16) | PRESENT as author verdicts; report must restate; no outside evidence |
| 6 | **SHONEN** — one line per box | `SHONEN.md:5-12` — four boxes, each `[~]` with a resolvable pointer (lines 5, 7, 9, 11; box 2 cites `live/receipt-{1,2,3}.json`) | PRESENT (4 lines; none `[x]`) |

### §6 campaign addendum extras

| # | Required item | Evidence | Status |
|---|---|---|---|
| 7 | **Stale-lane** line (respawn-per-round; no other mission open) | Report-only statement; the round-17 LOG entry (`LOG.md:992-1026`) has no `Stale-lane` line (grep exits 1); round-16 precedent `LOG.md:990` | MISSING in lane — L1 must write it |
| 8 | **Tool installs** | `build/advice/ScribeInstallDisclosure.md`: "No tool installed or updated (none needed)"; `build/drafts/install-disclosure.md` names retained `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` (sha256 `753bfa73…e226`) and the L0 follow-up line; round-16 install `LOG.md:988-989` | PRESENT — say "none new this round; retained install unchanged; no pacman" |
| 9 | Wave seat counts, role mix, **dead seats**, round total | Build: `build/validation.json` (`spawn 82`, role_mix scout 19 / executor 15 / reviewer 14 / scribe 10 / connector 8 / critic 6 / revenger 4 / sentinel 2 / simplifier 2 / mutation-tester 2), `build/completion-summary.json` (82 completed, 0 failed; verdicts 34 confirm / 32 partial / 1 refute / 15 n/a / 0 nonconformant), `build/refused-result-1.json` (one refused task call). Falsify: `falsify/spec.json` (80 items; reviewer 34, scout 8, critic 7, connector 6, executor 6, scribe 6, revenger 5, mutation-tester 4, sentinel 2, simplifier 2), `falsify/dispatch.json` (`spawn 80`), `falsify/provenance-ledger.json` (policy v2 block, 80 spawned), `falsify/assignments.json` (80), `falsify/attempts.json` (27 records: 25 capacity checks at 15–160 running jobs, 1 task_call). Round total 82+80 = 162 ≤ 200. **No falsify `completion-summary.json`** → dead-seat count has no evidence yet | PARTIAL/PENDING — build PRESENT, wave-2 death tally MISSING |
| 10 | Planner seat mapping (validator rejects `planner`) | `LOG.md:1009-1012`: "L1 holds the planner seat; the planning data-walk rode `RevengerPlannerWalk`"; `build/advice/RevengerPlannerWalk.md`; `validation.json` role_mix contains no `planner` | PRESENT |
| 11 | Inherited-state resolution (and files not authored, named) | `corpus/lessons/round-17.md:3-7` (start cff9e62, clean tree, nothing inherited); my check `grep 'lane-dead-no-report kama round=17' /home/vgpnk/Projects/shokunin/.ufo/watchdog.log` → exit 1 (no line) | PRESENT |
| 12 | Misroot sweep before the report | `corpus/lessons/round-17.md:90` (M6) asserts "no remaining fleet-root file", but **no command output is retained**. Current sweep: `git -C /home/vgpnk/Projects/shokunin status --porcelain` shows `M .ufo/watchdog.log`, `?? .ufo/reports/round-19/mado.md`, `?? .ufo/state/*.report-baseline` — no kama seat note | PRESENT-WEAK — paste the command output in the report |
| 13 | Round-16 spot-check dispositions turned into criteria/fixes or refused with reasons | `corpus/lessons/round-17.md:93-127` (six routed defects dispositioned); `corpus/QUALITY.md:121-123` | PRESENT |
| 14 | Wave evidence committed (spec + registry) and final pushed hash cited | `54a2926` contains build wave evidence only; `git status --porcelain` in lane shows `?? .ufo/waves/round-17/falsify/` — wave-2 evidence is **uncommitted**. No `falsify/validation.json` either (policy block lives in `dispatch.json` + `provenance-ledger.json`) | PENDING |
| 15 | Report file + report commit on fleet repo | `/home/vgpnk/Projects/shokunin/.ufo/reports/round-17/kama.md` — **absent** (`ls` of that directory lists kagi/kaidoku/kake/kasegi/kotoba/kotodama/kumitate/mado/tabi/tsukuroi only) | MISSING |

## Findings

- **F1 (missing deliverable).** The report itself does not exist: the fleet report
  directory has no `kama.md`. Nothing else can be "readiness-complete" until it is written;
  the marker rule (`kama-round-17.md` §4) fails outright on absence.
- **F2 (broken pointer, observed).** `SCORECARD.md:674-676` says measurements are
  "against the working tree that the round-17 build commit lands (hash in `LOG.md`
  §round 17)" — `LOG.md` §round 17 contains no commit hash (grep exit 1). The hash is
  recoverable from the branch tip (`git rev-parse master` → `54a2926…`) and from digest
  binding: `fault-controls-current.json.check_sha256` = sha256 of
  `git show 54a2926:tests/probe-verdicts/check.py` = `ddc3f3cc…`; `live/gate.txt` tool pin
  = sha256 of `git show 54a2926:tools/kama-llamacpp-live.py` = `0efd1723…`; probe pin
  `36b64978…` = `mutants-grid.json` current probe. [INFERENCE] the runs were produced
  against content identical to `54a2926`; no run artifact names a revision itself.
  Fix: state `54a2926` (and the final falsify commit) explicitly in the report, and stop
  citing LOG.md for the hash.
- **F3 (missing end evidence, observed).** No end-of-round census output exists. The
  prescribed command `sources-census.sh validate … kama` yields no row counts, yet
  `SCORECARD.md:689-690` asserts "Sources validate exit 0; rows 41 → 46". My clone run at
  54a2926: `validate` exit 0 with `W04 S031` **and a new `W04 S043` duplicate-URL warning**
  (S043 vs S037 share the `server.cpp@704366d76` URL across scopes); `census` mode exit 0
  with rows 46 / tier.A 43 / tier.C 3 / mined 36 / queued 5 / rejected 5. The round-start
  file shows only S031, so the S043 warning is new and is disclosed nowhere. Fix: paste the
  **end-run census output** (both W04s, exit 0) and the count command actually used.
- **F4 (LOG extras, observed).** The round-17 LOG entry lacks the `Stale-lane` line and a
  tool-install statement that §6 #6 requires the report to carry; the round-16 entry
  (`LOG.md:988-990`) has both. Report must supply them even though LOG omits them.
- **F5 (wave-2 accounting pending, observed).** Falsify evidence is uncommitted and has no
  completion summary, so the required dead-seat count and the "wave evidence committed"
  claim have no evidence yet; the round total (162) is arithmetic over `validation.json`
  (82) and `spec.json`/`dispatch.json` (80). Falsify also has no `validation.json`; the
  policy-v2 identity for wave 2 is only in `dispatch.json`'s policy block and
  `provenance-ledger.json`.
- **F6 (weak evidence, observed).** The misroot sweep is a prose assertion in M6; no
  command output is retained at the commit. It reproduces cleanly today (F12 above), so
  the report should paste it.
- **F7 (no harm to the section set).** Sections 1a/1b, 4b/4c/4d, 5, 6, 8, 10, 11, 13 all
  have resolvable pointers at the commit; the four gaps (report, end census, real hash,
  wave-2 completion) are additive artifacts, not rewrites.

## Commands run (exit codes)

- `git -C <lane> log --oneline -3 54a2926` → 0.
- `git ls-tree -r --name-only 54a2926 -- <paths>` (lane, wave tree, corpus, tests/tools) → 0.
- `test -f /home/vgpnk/Projects/shokunin/.ufo/reports/round-17/kama.md` → **1 (absent)**;
  `ls` of the report dir → 0.
- `grep -n '54a2926\|54a29268' LOG.md SCORECARD.md corpus/lessons/round-17.md` → **1**.
- `jq` reads of `build/validation.json`, `build/completion-summary.json`,
  `build/verdict-counts.json`, `falsify/{spec,dispatch,assignments,attempts,provenance-ledger}.json`,
  `runs/*.json`, `live/receipt-1.json`, `live/gate.txt` → 0.
- `git diff --stat 54a2926 -- . ':!.ufo/waves/round-17/falsify'` → 0 (empty).
- `git status --porcelain` (lane) → 0: only `?? .ufo/waves/round-17/falsify/`.
- `git -C /home/vgpnk/Projects/shokunin status --porcelain` → 0 (see F12).
- `grep 'lane-dead-no-report kama round=17' .ufo/watchdog.log` → 1 (no line).
- Clone at pin: `git clone -q <lane> /tmp/readiness-kama-clone && git checkout -q 54a2926` → 0.
- Census end (`PYTHONDONTWRITEBYTECODE=1`):
  `sources-census.sh validate --root /tmp/readiness-kama-clone --file /tmp/readiness-kama-clone/corpus/SOURCES.md`
  → 0 (W04 S031, W04 S043, ok); `census` same inputs → 0 (rows 46 / A 43 / C 3 / mined 36).
- Census start: blob `git show cff9e62:corpus/SOURCES.md` → `census` → 0 (rows 41 / A 38 /
  mined 31); blob placed in `corpus/` → `validate` → 0 (W04 S031 only), matching retained
  `.ufo/waves/round-17/sources-before-validate.txt`.
- Append-only guard in clone: `python3 tools/sources-append-only.py --from cff9e62 --to 54a2926`
  → 0, `--json` → 0 (`added S042–S046`, `violations: []`).
- Digest binding: `git show 54a2926:tests/probe-verdicts/check.py | sha256sum` → `ddc3f3cc…`
  (= `fault-controls-current.json`); `git show 54a2926:tools/kama-llamacpp-live.py | sha256sum`
  → `0efd1723…` (= gate tool pin); frozen copy `b853576e…` (= frozen JSON).

## Limitations

- Read-only; I ran no gate, control or counting command as a verdict on claims — other
  seats re-run those. Clone census labels the lane `file` instead of `kama` (cosmetic; the
  real command uses `--root /home/vgpnk/Projects/shokunin kama`).
- A before-blob validate placed outside `corpus/` (at repo root) emitted a wall of E11
  "missing used-by" lines; placing the same blob under `corpus/` returns exit 0. That is an
  invocation artifact of `--file` resolution, **not** a lane defect, and I record it so it
  is not mistaken for one.
- Wave-2 seat death status cannot be observed from lane files while the wave is in flight;
  only `assignments.json` (80) and `dispatch.json`/ledger counts (80) exist.
- I did not read `.ufo/interactive-sessions/` or any session store; all recursive searches
  carried the exclusion flags.

## Installs

None. No tool installed, upgraded, or linked; no pacman transaction attempted (pause
respected). Scratch `/tmp/readiness-kama-clone` and `/tmp/sources-before.md` removed.
