# kama-shokunin

A **shokunin lane** — an expert agent for one domain, minted and trained
under the [shokunin skill](https://github.com/VeigaPunk/shokunin).

**Domain:** local model serving & endpoint health — scopes local LLM endpoints, baseURL drift, model-id reconciliation

**Wiki:** [Devin wiki](https://app.devin.ai/org/veigapunk/wiki/VeigaPunk/kama-shokunin?branch=master)

## What's here

- `SKILL.md` — the distilled expertise: decision tables, error patterns,
  checklists (absent on lanes still in shonen seed form — see `corpus/`)
- `PROVINCE.md` — the owned domain boundary and refusals
- `AGENTS.md` — the lane's operating rules (scope, LOG entries, commit helper)
- `LOG.md` — append-only round log: the evidence that motivated each change
- `MINT.md` — the mint record
- `README.md` — this file
- `SCORECARD.md` — the lane's standing self-assessment: axes table, capability list, saturation, per-round claims and measured results
- `SHONEN.md` — the promotion checklist (four boxes, all `[~]`)
- `considerthese/` — operator-authored daily reflections; mined one proposal per round, never edited
- `corpus/` — the lane's memory: `knowledge/` entries, `lessons/`, `SOURCES.md` registry, `QUALITY.md`, coverage map and frontier in `corpus/README.md`
- `plans/` — early planning notes
- `registry/` — registered consumers and invocation history, outcome registries, `engine-pins.tsv`, `digest-ledger.tsv`
- `tests/` — fixtures and regression suites for the probe and the live-fixture tools
- `tools/` — the probe, the instruments and the per-round counters (`tools/round<N>-*.py`)

The listing covers non-hidden top-level entries only: the hidden `.gitignore` names the paths git ignores (`.ufo/interactive-sessions/`, `.ufo/state/`, `__pycache__/`), and the hidden `.ufo/` directory holds the round work directories `round-5/`–`round-10/`, `reports/` (the round-5 report) and `waves/` (`round-11/`–`round-43/`).
