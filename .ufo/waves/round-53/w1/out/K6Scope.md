# K6Scope — round-53 C2 scope critique

**Verdict: the three-file surface is axis-faithful and the C2 claim as frozen is sound (tradeoff, not defect — accept it), but the claim measurably leaves the larger mismatch untouched: the same frozen parser counts 135 unique dead citation tokens (141 occurrences) outside SCORECARD.md/SHONEN.md/SKILL.md at the build commit, 28 of them in living documents, and the ledger mechanism structurally cannot disclose any of them.**

Seat: K6Scope (leaf, scope critic for C2). Tip measured: lane build commit
`c22602bd8d83ab26349d1087e916ca537ee4f9d1`. Counter under review:
`tools/round53-cited-path-check.py` (frozen; `SURFACES = ("SCORECARD.md", "SHONEN.md", "SKILL.md")`
at line 99 of the build-committed copy).

## Method

1. Scratch clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`
   (toplevel verified = `$S/lane`), checked out at `c22602bd` (exit 0).
2. Extracted the counter source at the build commit (`git show c22602bd:tools/round53-cited-path-check.py`)
   and imported it; built `Repo(clone, c22602bd)` and `Repo(/home/vgpnk/Projects/shokunin, HEAD)`,
   then ran the frozen `citations()` + `resolve()` over every path the seat spec names:
   `LOG.md`, `corpus/README.md`, `corpus/QUALITY.md`, all `corpus/knowledge/*.md`, all
   `corpus/lessons/*.md` — outside fences (the parser itself skips fenced blocks).
3. Driver validated against the counter's own semantics: running `survey()` from the same
   module import over the three covered surfaces reproduces the L1's build receipt exactly —
   `cited=682 unresolved=14`, same 14 tokens as `.ufo/waves/round-53/measured/c2-build.out`.
   Full per-file data: `.ufo/waves/round-53/w1/out/K6Scope/scan.json`, driver `scan.py`,
   categorized table `dead-citations.tsv`.

No counter was executed end-to-end for this seat (the ~2 s C2 run's numbers are quoted from
the committed build receipt and re-derived via the module import, which is the strongest
local reproduction available without re-running).

## Counts (at c22602bd, frozen parser applied off-surface)

Grand total: 2717 citation occurrences parsed, 141 unresolved occurrences / 135 unique tokens.

| file group | cited | unresolved |
|---|---|---|
| LOG.md | 464 | 3 |
| corpus/README.md | 178 | 5 |
| corpus/QUALITY.md | 204 | 2 |
| corpus/knowledge/*.md (37 files) | 366 | 18 |
| corpus/lessons/*.md (104 files) | 1505 | 113 |

Breakdown of the 141 (full list in `dead-citations.tsv`):

| category | n | nature |
|---|---|---|
| never-adopted shokuknow proposal paths | 53 | benign — round-41.md lines 35-93 decision table listing rejected package files (`corpus/knowledge/*-amendment-2026-10-2X-rN.md`) |
| `.ufo/watchdog.log` | 23 | fleet runtime log, on disk, never committed (the `untracked` class on covered surfaces; SCORECARD has the row) — 2 in living docs (LOG.md:1105, QUALITY.md:334), 21 in round-frozen lessons |
| upstream llama.cpp paths | 21 | `tools/server/*`, `tools/quantize/README.md`, `tests/model_executor/*`, `tools/measure.py` — the `upstream` class on covered surfaces |
| round-frozen historical drift | 31 | deleted/renamed round artifacts cited from frozen lessons and their verifier-spotchecks |
| sibling-checkout (ufo-fsd-alpha) | 4 | `scripts/local-helper.mjs:8` ×3, `tests/local-helper.test.js:263-266` ×1 |
| anchor beyond EOF | 2 | round-10.md:151 `SKILL.md:9999` (deliberate control token); **round-36-verifier-spotcheck.md:88 `README.md:550` — genuine drift in a living re-verification doc (README.md is shorter at the build)** |
| range notation (parts exist) | 2 | QUALITY.md:309 `RevRow{A..E}`; knowledge/self-assessment-at-writing.md:31 `ConfirmM01..11` (dirs exist individually) |
| use-mention of a known-dead path | 1 | corpus/README.md:501 quotes SCORECARD's absent `.ufo/waves/round-31/c2/c2-tip.json` as the object of the sentence |
| living knowledge-doc drift | 4 | consumer-registry.md:325 `tools/janitor_auth.ts`, consumer-registry.md:330 `scripts/vendor/scihub-paper-downloader.py`, context-capacity.md:238 `corpus/evidence/round10-fleet/r10-scout-endpoint.md`, free-tier-provider-limits.md:65 `.ufo/round-6..9/telemetry.json` |

## Evidence highlights (file:line at c22602bd)

- **Same token, fixed on-surface, dead off-surface (×3):**
  - `scripts/local-helper.mjs` — corrected in place at SKILL.md:113 by the build
    (`~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs`); still cited dead at
    corpus/knowledge/consumer-registry.md:42,47 and corpus/knowledge/listener-census.md:118,176.
    Fleet check: `/home/vgpnk/Projects/shokunin/scripts/` holds only
    `fixtures/ hyaku/ shokunin-watchdog.sh sources-census.sh` — no local-helper.mjs in
    either tree.
  - `.ufo/watchdog.log` — disclosed for SCORECARD.md (ledger, `untracked`, verified on
    disk at the fleet root); still cited dead at LOG.md:1105 (`.ufo/watchdog.log:536`)
    and corpus/QUALITY.md:334.
  - `tools/server/server-schema.cpp` — disclosed for SCORECARD.md and SKILL.md (ledger,
    `upstream`, pinned raw URL @704366d76); still cited dead at LOG.md:1795 (the entry
    itself writes "@704366d76" — upstream use) and corpus/README.md:426; same class:
    README.md:232 `server-http.cpp`, README.md:685-686 `server-context.cpp`/`server-models.cpp`,
    knowledge/llamacpp-loading-lifecycle.md:1,153,154 etc.
- **Structural ceiling:** `evaluate()` at line 350 of the frozen counter flags any ledger
  row whose surface is not in SURFACES as `unknown surface` → `bad`. The disclosure
  mechanism cannot cover any other file by adding rows; widening coverage requires a new
  frozen counter (a new round's claim). The ledger's own header states the bound
  ("a repository path that SCORECARD.md, SHONEN.md or SKILL.md cites outside fences").
- **One real calibration rot in a living verification doc:**
  corpus/lessons/round-36-verifier-spotcheck.md:88 cites `README.md:550`, beyond the
  build tree's corpus/README.md EOF.
- New round-53 material is clean: corpus/lessons/round-53.md cites 17, unresolved 0.

## The scope question

**Is the three-file surface the right self-assessment? Yes at the level the axis rubric
defines.** AXES.md (fleet) line 15 grades calibration as "SHONEN.md/SCORECARD entries
match observed repo state"; SKILL.md is the lane's third standing self-description. The
claim type and predicate name exactly these three files; the routed prototype
(`.ufo/waves/round-52/w1/out/W3Mistakes/cited-path-exists.py`) scanned only SKILL.md +
SCORECARD.md, so round 53 widened rather than narrowed the surface, and the lane's own
round-29 doctrine (corpus/knowledge/self-assessment-at-writing.md: "This is a bounded
extractor, not a semantic proofreader … claims outside the two frozen base files … are
beyond its recall") blesses an explicitly bounded check. The claim is honestly bounded,
measured, and met (`c2-build.out`: cited=682 unresolved=14 disclosed=14 met=True;
reproduced here).

**Does the claim leave the larger mismatch untouched? Yes, measurably.** Off-surface
dead citations outnumber on-surface ones ~10:1 raw (141 vs 14) and are 28:0 in living
documents. Most off-surface misses are benign by design (frozen-lesson drift, rejected
proposal tables, upstream paths, use-mention, range notation, control tokens), so a
naive "scan everything" would drown in false positives — but the actionable residue is
real, and three of its entries are tokens the build itself fixed or disclosed on the
covered surfaces while leaving identical citations dead next door. Under the axis's
plain reading ("self-assessment matched to repo state"), the calibration 7→7 score
certifies the three self-description files only; the lane's wider citation ecosystem
(LOG tail, corpus index, quality ledger, knowledge base) is unmeasured and, where
measured here, measurably stale.

## Defect classification and smallest safe correction

- **Not a defect in the claim or counter** (both are frozen, explicit, and axis-faithful;
  rejecting the claim would punish declared, honest bounding — the judge should accept C2
  as met).
- **Fixable gap at the reporting layer:** the round-53 calibration narrative should carry
  the surface qualifier, and the residue should be recorded as known-unresolved scope.
  Proposed text (full wording in `.ufo/waves/round-53/w1/out/K6Scope/proposed-fix.md`):
  one sentence for SCORECARD §Round 53, one Errata row for corpus/lessons/round-53.md,
  plus an optional round-54 claim widening SURFACES to the living docs with two new
  ledger classes (`sibling-checkout`, `mention`) — never `corpus/lessons/` (113 of the
  141 live there and are expected drift).

## Artifacts

- `.ufo/waves/round-53/w1/out/K6Scope/scan.py` — driver (imports the build-committed counter)
- `.ufo/waves/round-53/w1/out/K6Scope/scan.json` — full per-file results
- `.ufo/waves/round-53/w1/out/K6Scope/dead-citations.tsv` — 141 categorized rows + per-file summary
- `.ufo/waves/round-53/w1/out/K6Scope/proposed-fix.md` — proposed correction text
