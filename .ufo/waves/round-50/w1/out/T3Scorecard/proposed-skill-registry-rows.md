# Proposed SKILL.md instrument-registry rows for the two round-50 counters (seat T3Scorecard)

Insertion point: `SKILL.md` at the round-50 tip `3b79eadd`, immediately after the last row of the
`| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |` table at
`SKILL.md:1490` (the `| Round-49 witnessed live receipt replay | ... |` row, `SKILL.md:1496`),
before the blank line and `### Re-running live evidence (witnessed replay, round 49)`.

These two rows remove every defect `tools/round43-registry-audit.py` reports at the draft
(`unreg=2`, `selftest=1`). Measured in a scratch clone with the draft SCORECARD and these rows
committed (`d3e1a374`): `GATE_SELFTEST pass=6 fail=0`, exit 0 (`sim-gate-selftest.out`) and
`unreg=0 defect=0 flags=0 pins=0 selftest=0 dc=0 spot=0 hidden=0 pop=46 registered=46 mismatches=0 met=True`
(`sim-r43.out`).

## Rows (verbatim)

| Round-50 C1 replay-bind audit | measurement: `python3 tools/round50-replay-bind-audit.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `bind=0\|1 teardown=0\|1 newrow=0\|1 bound=N/3 met=True` and one `detail:` line per leg; 1 not met; 2 could not evaluate | `sha256 ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89` for the frozen counter blob; no `--selftest`; needs Linux `/proc`, a pids-capable host, https to github.com and huggingface.co (~75 MB per replay) and about 46 s | `--scratch` and `--out` only; read-only on `--repo` |
| Round-50 C2 append-audit v5 check | measurement: `python3 tools/round50-append-audit-v5-check.py --repo <clone> --tip <full-commit> [--scratch <dir>] [--out <receipt>]` | 0 met, prints `tip=<full>` then `fixture=0\|1 lane=0\|1 scenarios=N/12 met=True` and one `detail:` line per scenario and lane leg; 1 not met; 2 could not evaluate | `sha256 925f07a48a02ad54a9c89230aac7e54c8dafee4ba2e8a823dcb851b9cf48ca46` for the frozen counter blob; no `--selftest`; twelve constructed fixture repos under `--scratch`, about 5 s | `--scratch` and `--out` only; read-only on `--repo` |

## Re-anchor the depth row after the insertion

The insertion changes `SKILL.md`, so the `## Axes` depth row in SCORECARD.md must be re-anchored in
the same commit:

- `` `SKILL.md` sha256 `0ad48efc8610a5ccf9f25cb843de6b9c006c2463971f6a06db053e51a079f0c6` `` →
  `` `SKILL.md` sha256 `d1f9db94cf4c4c43edce3fbe1b8af9296bd3b3338ce756d1ef1c108d30480b73` ``
- `(1504 lines)` → `(1506 lines)`
- `grep -c '^## ' SKILL.md` stays `37`

`d1f9db94...` is the SHA-256 of `SKILL.md` at the simulation commit `d3e1a374` (draft SCORECARD
plus exactly these two rows, nothing else). Any other wording or placement invalidates it; re-run
`python3 tools/round41-scorecard-reconcile.py --repo <clone> --tip <commit>` after the integration
edit and paste the digest it observes. Without the re-anchor, r41 reports
`hash_bad=1 lines_bad=1 mismatches=2 met=False` (`sim-r41.out`).

## Alternative shape in the wave

Seat T2Skill drafts five round-50 rows in a new `## Round-50 instrument registry` section, and
seat X3Gate2 recommends one five-column row per counter in a new section; either shape registers
the population (`registered 46 unregistered 0`). Integration should pick one set, then re-anchor the
depth row to the digest observed *after* that edit — the digest above is exact only for this
two-row insertion after `SKILL.md:1496`.

