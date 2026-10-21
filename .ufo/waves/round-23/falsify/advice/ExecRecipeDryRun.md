# ExecRecipeDryRun — round-23 draft recipe dry run

Verdict: **holds**. The draft round-23 recipe (13 arms, exits exactly as assigned) ran end-to-end at
245a37f69628c2c6bb29bbf17897d8fb5946c857; every arm's observed exit matched its pre-registered
expected exit and the runner exited 0 (13/13 `as_expected`, 0 timeouts, 0 stderr bytes total).
The recipe is machine-executable as written; no arm needed hand-holding.

## Axes
- Calibration (primary): does the declared C1 grid + no-harm + provenance arm set reproduce its
  declared exit vector from a clean committed clone, driven only by a recipe file?
- Operability: recipe placeholders (`{lane}`, `{python}`, `{revision}`, `{out}`) resolve correctly
  outside the canonical lane checkout.

## Provenance
- Work clone: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r23w2/ExecRecipeDryRun`; `git rev-parse HEAD` → `245a37f69628c2c6bb29bbf17897d8fb5946c857` (verified); `git status --porcelain` empty; `refs/heads/master` = same commit.
- Command: `cd /tmp/kama-r23w2/ExecRecipeDryRun && python3 .ufo/waves/round-22/run.py --recipe <recipe.json> --out /tmp/kama-r23w2/ExecRecipeDryRun-out` → runner **exit 0**, wall 188.46 s.
- `commands.json`: `measured_commit 245a37f69628c2c6bb29bbf17897d8fb5946c857`;
  `recipe_sha256 7ab143192798baec0a57e789ec9faa69eb7816af173a841ce05ba2eb39129481` (== sha256 of the delivered recipe.json, re-hashed after the run).

## Observed exits (all `timed_out=false`, all `*.stderr` 0 bytes)

| arm | command (post-substitution, abbreviated to `{lane}`=clone) | observed | expected |
|---|---|---|---|
| r23-audit-selftest | `{python} {lane}/tools/report-landing-audit.py --selftest` | 0 | 0 |
| r23-grid-frozen | `{python} {lane}/tests/report-audit/repo-state-grid.py --arm frozen --json` | 1 | 1 |
| r23-grid-current | `… repo-state-grid.py --arm current --json` | 0 | 0 |
| r23-grid-both | `… repo-state-grid.py --arm both --json` | 1 | 1 |
| r23-mutants | `{python} {lane}/tests/report-audit/isolation-mutants.py --json` | 0 | 0 |
| r23-ledger-10-22 | `{python} {lane}/tools/report-landing-audit.py --rounds 10-22 --fleet-repo /home/vgpnk/Projects/shokunin --json` | 0 | 0 |
| r23-ledger-raw-10-22 | same + `--no-errata` | 1 | 1 |
| r22-witness | `{python} {lane}/.ufo/waves/round-22/report-source-fix/ReportSourceFix/out/red-green-witness.py` | 0 | 0 |
| citation-noharm | `{python} {lane}/tools/citation-provenance.py --json` | 0 | 0 |
| io-current-noharm | `{python} {lane}/tests/llamacpp-live/install-io-grid.py --arm current --json` | 0 | 0 |
| sources-validate | `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | 0 | 0 |
| sources-census | `… sources-census.sh census --root /home/vgpnk/Projects/shokunin kama` | 0 | 0 |
| r23-sources-append-only | `{python} {lane}/tools/sources-append-only.py --from 4fe9339f8fc3a4a4a479d9c938a850da12f1124d --to {revision} --repo {lane}` | 0 | 0 |

## Substantive stdout observations (parsed from the receipts, not re-run)
- `r23-grid-both` JSON: **current** arm `fault met=26/26`, `control met=8/8` (plus `open` 2 not-met, `tradeoff` not-met — reported, ungraded); **frozen** arm `fault met=0/26`, `control met=8/8`, `tradeoff met=1`. Matches the L1-declared grid vector. `frozen_revision` in the JSON = `4fe9339f…` (the grid resolved the frozen auditor from the clone's own object store).
- `r23-mutants` JSON: `pristine: passed`, **killed=23**, `surviving=["M02-lazy-fetch"]`. Nuance vs the L1 declaration ("22 killed, survivors M02 and M20 defensive-only"): in this run `M20-log-sha-shape` is counted **killed**, but via `grid_exit=2` with `error: "could-not-evaluate: fixture premise: git add -- .ufo/reports/round-1/kama.md: fatal: unable to write new index file"` — the script's rule counts a cannot-evaluate grid as a kill (`isolation-mutants.py` docstring: "killed when the grid's current arm reports a violation **or cannot evaluate**"). So M20's kill is a grid-error kill, not a fault-row violation kill; the "defensive-only" framing is not contradicted, but critics should note the totals 23/1 vs declared 22/2 are a labeling difference, and the M20 premise failure ("unable to write new index file") is worth one look for fixture flakiness.
- `r23-ledger-raw-10-22` JSON `summary`: `status failed`, `defects 9` (8 `landed-omitted` + 1 `unresolved-full-hash`), `corrected 0`, rounds 10–22 (13 reports) — exit 1 as declared; with errata (`r23-ledger-10-22`) exit 0.
- `r23-sources-append-only` stdout: `added S095 (allowed)` / `no append-only violations` for `--from 4fe9339f8fc3a4a4a479d9c938a850da12f1124d` (a commit in this history; `git cat-file -t` → commit) `--to` 245a37f (via `{revision}`).
- `r22-witness` exit 0; stdout tail includes `source_registry_sha256 44ff346bf16d5c382b94775ee918b9e65f77e6ad4315542641e8697188d058a9`. The witness resolved `--candidate` to the clone's own `tools/report-landing-audit.py` (its `LANE` is derived from its file location), so it graded the round-23 auditor, not the canonical lane's bytes.

## Isolation notes
- No writes to the lane checkout's tracked files, `.jj`, or indexes: the run executed in `/tmp/kama-r23w2/ExecRecipeDryRun`; only `.exit/.stdout/.stderr/commands.json` receipts under `/tmp/kama-r23w2/ExecRecipeDryRun-out` and the two seat artifacts under the lane's `.ufo/waves/round-23/falsify/` were written. The `--fleet-repo`/`sources-census.sh` arms read the fleet root read-only (round-22 precedent, same argv shape).
- No git env vars exported; the grid/mutant scripts set their own per-subprocess `GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1` and fixture identity.
- Installs/updates: **none**.

## Not verified
- Full semantic content of every arm's JSON (only the summaries quoted above were parsed); per-fault row identities inside the grid receipts were not enumerated here.
- Whether the M20 fixture-premise failure reproduces (observed once, this run only) and whether it is environmental (index write) rather than mutant-caused; the mutant-retest seats own that question.
- Alternate-arm coverage the assignment excluded: grid/`install-io-grid`/`isolation-mutants` selftests, frozen/current alternates (O01), gitfile redirect (O02), io-frozen, io-both, citation selftest — none requested, none run.
- Byte-identity of the rounds 10–22 ledger against any frozen copy (the assignment asked for exits only; exit 0 observed, no byte comparison performed).

## Files written
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/out/ExecRecipeDryRun/recipe.json` (delivered draft recipe, sha256 `7ab143192798baec0a57e789ec9faa69eb7816af173a841ce05ba2eb39129481`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/ExecRecipeDryRun.md` (this report)
- Run receipts (outside lane): `/tmp/kama-r23w2/ExecRecipeDryRun-out/` (13× `.exit/.stdout/.stderr`, `commands.json`)
