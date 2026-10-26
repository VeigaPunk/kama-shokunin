# kama round 40 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_opus)
date: 2026-10-25
report: `.ufo/reports/round-40/kama.md` (fleet repo commit `58fde7e12a956cd414ecc90207ff74e6849b780d`, author `kama-shokunin`)
judged lane state: origin master `04f3ce93184eda038ae6a453b3aa650b7291b1c3`, measured in fresh clones of `https://github.com/VeigaPunk/kama-shokunin.git` (`/tmp/kama-r40-close` for reads; this file committed from `/fast/scratch/hyaku/kama-r40-closure`). The parked worktree was not touched: no jj command there except through the helper's read-only `state`.
round base: `efe25f962a0b3a2b9b111c03bb5b5386c9548195` (round-39 verifier spot-check, the origin tip when the round launched)
dispatch digest (`.ufo/watchdog.log`, mutable): `2026-10-25T15:56:18-03:00 launch kama round=40 pgid=3183165 driver=hyaku-inline attempt=1`; `2026-10-25T16:39:24-03:00 complete kama round=40; hyaku-inline attempt=1`

This file is a closure artifact, not lane work. No lane-authored file was edited, nothing was promoted or minted, and no `[x]` was written into SHONEN.md.

## Step-1 conformance

| check | result |
|---|---|
| report committed by lane identity | OK. `git log --format='%an %H' -- .ufo/reports/round-40/kama.md` → `kama-shokunin 58fde7e12a956cd414ecc90207ff74e6849b780d` (16:33:22 -03), an ancestor of fleet `origin/master`. Filed after the last lane commit (16:32:45) and before the watchdog `complete` line (16:39:24). |
| `SHONEN` heading, one line per box | OK. `## SHONEN` with 4 `[~]` lines. `SHONEN.md` at tip has 4 boxes, all `[~]`. |
| cited lane commits exist and are ancestors of `master` | OK in a fresh clone. `efe25f96`, `f327904b`, `697f897f`, `2429f48e`, `03ea3f59`, `c162640b` and `04f3ce93` all pass `git merge-base --is-ancestor <hash> origin/master`. All six round commits are authored and committed by `kama-shokunin <kama@shokunin.local>`. `git ls-remote origin refs/heads/master` returns `04f3ce93184eda038ae6a453b3aa650b7291b1c3`. |
| pushed / no uncommitted round work | OK. The lane worked in scratch clone `/fast/scratch/hyaku/kama-r40` (porcelain 0, `master` = `04f3ce93`). In the parked worktree, `jj-lane.sh state` reports `branch=master local=df61204c… remote=df61204c… ahead=0 behind=0 head=detached tracked=11 untracked=94`. That checkout is detached on the mutation-sandbox lineage (`873c5d77 mut4 …`), and its remote-tracking ref is stale (it was never fetched after `df61204c`). The 105 porcelain lines are the inherited carry. They are not round-40 work. |
| prompt carries the template contract | OK. `.ufo/prompts/kama-round-40.md` has §§1 MISSION/AXES, 2 Claims, 2b Frontier step, 3 L2 floor, 4 Report contract, 5 Commit/push/L0, and the 6 hyaku addendum. |
| marker vs report | Real report. It has six landed lane commits, receipts, and a 64-seat wave (`results.json`: 64 results, 0 null outputs; `spec.json` 64 items). Status `ok`. |

Conformance notes (do not affect status):
- **N1 — closure prompt inputs are stale.** The prompt lists lane HEAD before and after as `df61204c…`. That is the parked worktree's unfetched local `master`, not the round's base (`efe25f96`) or tip (`04f3ce93`). This verifier graded the fetched remote.
- **N2 — report quote typo.** The report body (§Sources & frontier) prints the located tag-object hash as `35ce313293052f8362e0829e7512bc9bc3d336c`, which is 39 hex characters and drops the trailing `9`. The lesson and S474 carry the correct `…336c9`.
- **N3 — dead SCORECARD pointer.** The SCORECARD round-40 C2 row cites `.ufo/waves/round-40/c2/{base,after}.out`. `c2/base.out` does not exist; the base receipt is `.ufo/waves/round-40/controls/c2-base.out`.
- **N4 — fleet-root validate checks the wrong copy.** The fleet-root `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` reads the parked worktree's `corpus/SOURCES.md`, which has 203 rows (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`). It does not read the 215-row tip. The lane's `census-end-fleetroot.out` is therefore not tip evidence. Its mirror validation is.

## Per-claim re-check

Every number below was re-derived over committed bytes with plain commands (git/grep/awk/jq/sha256sum). No lane counter was executed. The lane receipts were compared byte-for-byte with the values reported.

### C1 — calibration 7 → 7 (declared unverified by the lane)

Frozen predicate (`.ufo/waves/round-40/preregistration.json` C1). Its notes state: "The frozen counter code is the predicate".

Plain re-measurement. The `teaches` column is `$8` under `awk -F'|'` per the `SOURCES.md` header `| id | source | kind | tier | scope | anchor | teaches | status | …`.

| leg | base `efe25f96` | tip `04f3ce93` (= `2429f48e` for these blobs) |
|---|---|---|
| S474 `teaches` starts `supersedes S472` and holds `5585f6027df2…e50f2` | 0 (no S474) | 1 |
| amendment `## Correction — round 40` names wrong + correct digest | 0 | 1 |
| `corpus/lessons/round-40.md` names R36-D2C and the full `3ad0df68…ce234ff` | 0 (no file) | 1 (one line carries both) |
| other rows whose `teaches` starts `supersedes S472` | 0 | 0 |
| wrong digest `5585f602f71c…` lines in amendment | 1 (uncorrected) | 2 (provenance line + correction section) |

Frozen counter evidence was verified as committed, not re-executed. `tools/round40-calibration-audit.py` builds rows as `[c.strip() for c in line.split("|")[1:]]`, so `row[6]` is `teaches` and `row[7]` is `status`. The S474 test reads `row[7]`, which at the tip is `mined`, so the S474 leg can never be met by a schema-valid row. Receipts: `controls/c1-base.out` = `s474_row=0 amend_corrected=0 r36d2c_fixed=0 false_corrections=1 met=False`, and `c1/after.out` = `s474_row=0 amend_corrected=1 r36d2c_fixed=1 false_corrections=0 met=False`. Both match the report. At base the counter finds `false_corrections=1` (the uncorrected wrong digest in the amendment), which contradicts the preregistration kill-rule prose ("false_corrections == 0" at base). The lane disclosed this in `## Mistakes`.

Ruling: **unprovable.** The substance is real: under a schema-correct reading every prose leg flips 0→1, and each correction re-hashes (§Spot-check). The preregistration makes the frozen code the predicate, though, and that code reads `met=False` at the tip. The lane also declares no C1 improvement. Substituting a corrected counter after data would be post-hoc re-specification, so closure does not do it. No harm was found: every change is additive (`git diff --numstat efe25f96 04f3ce93` shows 0 deleted lines in `LOG.md`, `SCORECARD.md` and `corpus/`), and the census is clean. This is an honest stop.

### C2 — operability 8 → 8 (verified)

| measure | base `efe25f96` | tip `04f3ce93` |
|---|---|---|
| `.ufo/waves/round-38/w1/spec.json` sha256 | absent | `397f598009ad9dab0699cc73d165cff583d8f069b445f0dbaa0b79f6a4122cb7` (pinned value) |
| `.ufo/waves/round-38/w1/run.json` sha256 | absent | `d0666a36f483685bcadfdce997389ea4af7c6a80efe8b75c70e2e4c6d2039642` (pinned value) |
| `jq '.counts.total' run.json` / `jq '.items\|length' spec.json` | — | 36 / 36 |

Authenticity was checked against an independent copy. `/fast/scratch/hyaku/kama-r38/.ufo/waves/round-38/w1/{spec,run}.json` (mtime 2026-10-25 06:10 -03, inside the round-38 window 06:06–06:30) hash to the same two digests, so the staged bytes are the round-38 session files and were not regenerated. Receipts `controls/c2-base.out` (`… met=False`) and `c2/after.out` (`spec_exists=1 run_exists=1 spec_sha_ok=1 run_sha_ok=1 counts_ok=1 met=True`) match the report. Ruling: **improved** (predicate met, score held at 8). This closes defect 3 routed by round 38.

### Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | unprovable | C1: frozen counter cannot evaluate its own predicate; substance real, not credited |
| operability | improved | C2 re-measured 0→1 on all legs; bytes authenticated against round-38 originals |
| coverage | unchanged | no knowledge entry or coverage-map row added |
| freshness | unchanged | S474 re-verifies a held own-work fact; no `verified-at` sweep claimed |
| depth | unchanged | SKILL.md untouched (`git diff --stat efe25f96 04f3ce93 -- SKILL.md` empty) |
| adjacency | unchanged | no cross-domain evidence handled |

The axis table in `SCORECARD.md` is unchanged. Round 40 only appends a section, with no deleted lines.

## Spot-check (LEARNING.md — discernment from outside)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S474 (own-work SGLang tag inventory, supersedes S472 digest) | admit | `git ls-remote --tags https://github.com/sgl-project/sglang.git`, re-run 2026-10-25 by this verifier | agree | exit 0, 190 lines, sha256 `5585f6027df2dbc4dbafd4979b61c218ffd94e8af99936733218e0ae989e50f2`, byte-identical (`diff`) to `.ufo/waves/round-38/assimilation/exec-tag-inventory/ls-remote-tags.txt` and `.ufo/waves/round-40/c1/ls-remote-rerun.txt`. Line 160 `35ce313293052f8362e0829e7512bc9bc3d336c9	refs/tags/v0.5.22`, line 161 peels to `baa9befa…`. No `v0.5.23`/`v0.5.24`. The row's scope stays inside what the output shows. |
| staged shokuknow `corpus-expansion-1` package: no knowledge entry adopted | reject | `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` (sha256 `3ad0df68504e1f49a0ab23e68b2034a9d6258345468fa03013737ced7ce234ff`, 196639 bytes, 142 staged rows) | agree (decision), reason caveat | Not adopting is right: none of the 142 rows serves either frozen claim, and AXES binds the round to its 1–3 frozen claims. The stated ground "duplicates held territory" is true for only a minority: 27 of 142 staged rows have a source URL already in kama `SOURCES.md`, 81 have a URL that is not held (e.g. S337 Docker Compose services, S362 Vertex custom-container requirements), and 34 have no URL. The decisive ground is scope. The reject also names no candidate and no flip condition (contrast the round-39 Gate). |
| considerthese proposal 2 (version-pin watch) deferred, `R40A27.md` | reject (defer) | same `ls-remote` re-run | agree | The highest SGLang release tag is still `v0.5.22`, and `refs/tags/v0.5.23`/`v0.5.24` count 0, so a watch run today detects nothing. The rows already carry `recheck` cadences. |

Re-opened SOURCES row: **S474** (`corpus/SOURCES.md:226`). The Gate's located quote is the 2-token stdout line `35ce313293052f8362e0829e7512bc9bc3d336c9\trefs/tags/v0.5.22` (≤25 words). It is present at line 160 of the fresh output, and the row's anchor values (190 ref lines, tag object, peeled commit, digest) all match. Agree.

Census (this verifier):
- `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0, 93 W04, 0 E, `kama ok`. This run reads the parked worktree (203 rows; see N4).
- The same validate over a mirror root holding the tip clone (`/tmp/kama-r40-root/kama-shokunin` → `/tmp/kama-r40-close`, plus `shokunin.conf`) → exit 0, 93 W04, 0 E.
- `census --file` gives tip 215 rows (A 205, B 7, C 3; mined 196, queued 8, rejected 11) and base 214 (A 204; mined 195). This matches the report's 214→215 with S474 as the only added row.

## Trend verdicts

- **expansion: unchanged.** S474 corrects provenance for an already-held fact. No `knowledge/` entry was admitted on uncovered ground.
- **quality: improved.** A false citation was superseded by a stronger row: S472's wrong evidence digest by S474, whose digest this verifier reproduced byte-for-byte. The abbreviated R36-D2C package digest was completed and matches a fresh hash. The round-38 wave evidence is now staged as authentic bytes. No entry was found false and left unmarked, with one exception that is a sweep gap and not a new falsehood: the historical round-38 lesson line (D3).
- **discernment: improved.** The outside spot-check agrees with the Gate on the admit (S474) and on the reject decision. The reject's wording is non-specific (D2) but is not wrong as a disjunction, so this is a caveat and not a disagreement.

## Routed defects (lane must fix next round)

- **D1 — C1 counter/schema mismatch.** `tools/round40-calibration-audit.py` reads `row[7]` (status) for the `teaches` test, and the preregistration's base-control prose (`false_corrections == 0`) contradicts the frozen receipt (`1`). This was mined in `## Mistakes` but no `QUALITY.md` criterion cites it (`git diff efe25f96 04f3ce93 -- corpus/QUALITY.md` is empty; KQ25 covers positive controls for kills, not header-bound field indices). Fix: add a criterion citing `corpus/lessons/round-40.md`, or state why KQ25 already covers it. Any future counter over `SOURCES.md` must bind field indices to the header and pass a census-clean positive control before freeze.
- **D2 — non-specific Gate reject.** The round-40 Gate rejects the staged package as "duplicates held territory or is unrelated" without naming candidates or a flip condition. Only 27 of 142 staged rows have a source URL already in kama `SOURCES.md`; 81 have a URL that is not held, and 34 have no URL in the source cell. Name each rejected candidate (or the package theme) with its reason and flip.
- **D3 — correction sweep incomplete.** `corpus/lessons/round-38.md:67` still carries the wrong evidence digest `5585f602f71c…` with no in-file pointer. The appended round-40 note at line 113 covers only the package digest. Append a pointer to S474 and the amendment's correction section.
- **D4 — report/SCORECARD hygiene.** N2: the 39-hex quote in the report. N3: the dead `c2/base.out` pointer. Append corrections; do not rewrite.
- **D5 — carry, not new.** The parked worktree is detached on the mutation-sandbox lineage with a stale remote-tracking ref (`df61204c`), so the fleet-root census and `jj-lane.sh state` there do not describe the tip. Re-anchoring it remains an operator item.

## Verdict

C2 verifies by independent re-measurement. C1 does not verify under its own frozen predicate, the lane declares it unverified, and closure does not rescue it post hoc. No axis is harmed. **Not admitted — honest stop** (`rejected-honest-stop`), status `ok`. The SHONEN boxes remain `[~]` and need a named non-author verifier. Nothing here makes them fully checkable this round.
