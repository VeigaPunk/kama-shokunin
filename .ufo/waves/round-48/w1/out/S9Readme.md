# S9Readme — round-48 frontier disposition (kama, lane L1 KamaR48)

**Verdict: both frozen counters meet the predicate at the build commit — C1 `met=True`
(exit 0) and C2 `met=True` (exit 0, `replayed=3/3`) — and the round-48 frontier draft is
written; three instrument boundaries (binding false-bind, content-blind head eligibility,
no replay-time execution witness) are new findings, not contract misses.**

## Deliverable

`.ufo/waves/round-48/w1/out/S9Readme/frontier.md` — README-ready block
(`## Frontier disposition — round 48`): what v3 now audits (bound regions: SCORECARD's five
re-derived head titles with window-count eligibility, `only=## Errata` for
`corpus/knowledge/consumer-registry.md`, the binding rule, `regressed` in the exit), what it
still does not audit (the line-6 preamble banner has no region vocabulary, content-blind
eligibility, the 20-line threshold, the lexical binding tripwire, `A-row` unexpressible,
multiset-not-position restoration, contract coverage), what v5 receipts and the replay prove
(record-time digest verification of archive/member/model before the server starts; replay
from committed bytes with counter-side hashes and an equal stable projection; `--compare`
separating instance from stable fields; tamper and URL swap refused; S492 closes round-47's
`newrow` leg), what they do not (a replay that never ran a server but copies captures;
prerelease cliff and asset retention), and what stays frontier.

Not edited: `corpus/README.md` itself (append-only; the block is proposed for the integrator
to append). No lane file was written.

## Evidence (all measured this round)

Clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` (clone HEAD
`b85783e8`, the wave-dispatch commit). Counters are invoked from the lane working tree and
passed `--tip 380bcdff…`, so the tip argument, not the clone HEAD, governs every read. The
counter digests equal the preregistration's `counter_sha256`, and the clone HEAD
`b85783e8` carries the same bytes as `380bcdff` for all four files I ran or read
(`append-only-audit.py`, both counters, `append-only-contract.tsv`, `corpus/SOURCES.md`):

```
tools/round48-append-audit-v3-check.py  92b0f9f1027b8214c7a702d928f89e5a6d9fb814fc565c234f6deee3f2d82ac7
tools/round48-live-replay-v5-audit.py   6bc16e2532469f160cee59c78103688b8d16a9713fdb4d3c255f894975fb0c09
```

1. C1 counter, build tip (exit 0, ~4 s):

```
python3 tools/round48-append-audit-v3-check.py --repo $S/lane \
  --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S/c1 --out $S/c1.out
selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 \
lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True
```

(`out/S9Readme/c1-counter.out`)

2. v3 tool, build tip (exit 0), schema `append-only-audit/v3`:

```
python3 tools/append-only-audit.py --repo $S/lane \
  --to 380bcdff9c8af06997c482f6eb03db926a794a2b --json
commits=311 files=89 events=5 restored=5 partial=0 unrestored=0 ungraded_lines=89 \
regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0
dd9f5dc6c0e6 SCORECARD.md deleted=31  graded=14   ungraded=17 restored
0718b6abbda6 LOG.md      deleted=2292 graded=2292 ungraded=0  restored
0718b6abbda6 SCORECARD.md deleted=2421 graded=2349 ungraded=72 restored
0718b6abbda6 corpus/QUALITY.md deleted=375 graded=375 ungraded=0 restored
0718b6abbda6 corpus/README.md  deleted=663 graded=663 ungraded=0 restored
```

(`out/S9Readme/v3-lane-build.json`)

3. v3 tool, round-48 base `33e00582` with the round-48 contract (exit **1** — the build's
   finding, reproduced): `regressed=1`, the `0718b6ab` SCORECARD event `restored_max=2349
   held_at_to=2348`. The one missing graded line is the round-45 authority banner
   (`git show 82b5e9d3:SCORECARD.md | sed -n 6p`, 754 bytes): `grep -cF` of that text is 0
   at `33e00582:SCORECARD.md` and 1 at `380bcdff:SCORECARD.md`, where it is appended under
   `### Superseded head banners (kept verbatim; round 48)` (`SCORECARD.md:2736`).
   `SCORECARD.md` line 8 is the first `## ` heading. (`out/S9Readme/v3-lane-base.json`)

4. Threshold-1 population, same tip (exit 1): `events=98 restored=14 partial=4 unrestored=62
   ungraded=18 ungraded_lines=186`. All four `corpus/knowledge/consumer-registry.md` events
   are `ungraded` (0 graded of 1, 15, 1, 2 deleted) — the `only=## Errata` region excludes
   the census body as declared. (`out/S9Readme/v3-lane-thr1.json`)

5. Binding false-bind probe (scratch fixture `D=$(mktemp -d -p $S)`, `git init -q`,
   `rev-parse --show-toplevel` asserted equal to `$D`). Contract rows `LOG.md A NOTES.md:2`
   and `LOG.md A NOTES.md:3`; declaring lines `The changelog is not really append-only.` and
   `LOG.md isn't append-only.`:

```
python3 tools/append-only-audit.py --repo "$D" --to HEAD --contract contract.tsv
… bad_declarations=0 (exit 0)
binds() in tools/append-only-audit.py and in tools/round48-append-audit-v3-check.py
  both return True for: "The changelog is not really append-only.", "LOG.md isn't
  append-only.", "LOG.md is not strictly append-only."
  and False only for the contiguous form "LOG.md is not append-only."
```

6. C2 counter, build tip (exit 0, ~13 s, downloads ~74 MB):

```
python3 tools/round48-live-replay-v5-audit.py --repo $S/lane \
  --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S/c2 --out $S/c2.out
receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
```

(`out/S9Readme/c2-counter.out`)

7. Receipts (read, not re-run): `kama-llamacpp-live/v5`, `outcome pass`, 11/11 evaluated
   checks, ports 33779/41891/45023, alias `kama-r48-live`, `--ctx 256`, `-t 1`,
   `captures.props.fields.build_info = b11909-caa8191df`, `loading_observed true`;
   `provenance.model.commit 499bc882…`, `provenance.server.asset_sha256 bf94332a…`,
   `provenance.verified {at: record, archive_sha256 bf94332a…, member_sha256 35ac50fb…,
   model_sha256 270cba1b…}`. `corpus/SOURCES.md:245` is S492 with the pinned `/resolve/`
   URL (the `newrow` leg).

8. Release facts (2 `gh api` calls, 2026-10-26): `releases/tags/b11909` → `prerelease: true`,
   `target caa8191df1…`, `published 2026-10-26T21:00:58Z` (receipts recorded 22:27:28Z per
   `.ufo/waves/round-48/c2/live/install.txt`); `releases/latest` → `v0.7.0`,
   `prerelease: false`, target `620d2225`.

## Findings

**F1 (defect, new) — the binding rule accepts a denial, and the frozen counter shares the
implementation so no leg catches it.** `tools/append-only-audit.py:119` (`NEGATIONS` is four
contiguous phrases) and `:196-199` (`binds()`), mirrored at
`tools/round48-append-audit-v3-check.py:147` and `:226-233`. A declaring line negating the
rule in any other phrasing binds, and `row_token()` (`:180-184`) is a bare substring match,
so `changelog` supplies the token for `LOG.md`. Repro: evidence item 5 —
`bad_declarations=0`, exit 0. This is narrower than round-47 V1Ctr F1 (which v3 fixed for the
one contiguous form) but still a false bind on the C1 predicate's own sentence ("every
declaration must bind to a line that says append-only for that path and is not a negation").
Proposed fix (not applied — counter frozen): in `binds()`, test a negation over the window
around the mention, e.g. `re.search(r"(isn[’']?t|is\s+not|not\s+(really|strictly|actually)?|never|no\s+longer)\s+(an?\s+)?append[- ]only", low)`,
and match the token as a whole word or by the declaring path only
(`re.search(r"(?<![a-z0-9])" + re.escape(tok) + r"(?![a-z0-9])", low)` plus
`re.escape(path)`); add a counter fixture (in her own code path) with an unlisted negation
and with a token collision (`changelog`).

**F2 (boundary, new) — the exempt head sections are eligibility-by-line-count only.** An
exempt title is ungraded whenever the maximum of its line count over the window reaches the
parent's (`tools/append-only-audit.py:407-411`), whatever the text. The tool's own fixture
`exempt-rewritten` (`:757-765`) replaces 24 head lines with 24 unrelated ones and grades 0
lines, exit 0; `exempt-gutted-then-regrown` (`:774`) is eligible again once the section
returns later in the window. Consequence: `## Axes` could be replaced wholesale by
same-length junk with no graded line, and a lane round could "re-derive" a head by discarding
its prior content. Proposed, if the lane wants it: require overlap — grade the deleted lines
unless at least some fraction of the parent section's lines survive in the window maximum, or
track the section's line multiset rather than its count.

**F3 (boundary, new) — the SCORECARD preamble banner is not expressible as a region.**
Region titles/prefixes must begin `## ` (`tools/append-only-audit.py:147-151`) and lines
before the first `## ` heading have no section (`:231-239`). `SCORECARD.md` line 6 is such a
line, so it is always graded; the carve-out covers only the five head titles. That is why the
build had to append the r45/r46 banners to keep `regressed=0` (evidence item 3). The
instrument is right to grade it, but the lane's actual practice (rewrite the banner each
round, keep the superseded text) has no declared form: a `preamble=...`/`mutable=` region kind
or an explicit lane rule "the preamble banner is append-kept" is missing. Proposed: a
`preamble@path:line` region kind that leaves exactly that line ungraded while the rest of the
preamble is graded, or (cheaper) keep the append practice and add the rule sentence the
instrument can quote.

**F4 (boundary, new) — `A-row` is validated but unexpressible.** The `rule` cell is parsed and
restricted to `A|A-row|A-corr` (`tools/append-only-audit.py:171-174`) but grading reads only
`region` (`file_regions`, `:350-360`). `corpus/SOURCES.md` is `A-row` with region `*`, so the
cells the row calls mutable (`status`, `recheck`, `used-by`) are graded whole-file like any
line, and an in-place row status flip is a graded deletion. Proposed: a `mutable=<columns>` /
`cells=` region kind, or a per-row region naming the mutable cell syntax.

**F5 (limit, new for the C2 side) — the replay leg witnesses no process.** The replay leg
(`tools/round48-live-replay-v5-audit.py:401-435`) checks the rerun's `started_utc` against the
counter's start, hashes `server.realpath`, `model.path` and `inputs.archive` itself, and
compares checks and projection — but requires no execution witness; the marker file exists
only in `recordcheck` (`:289-333`). A replay tool that downloads the archive and model,
extracts the binary and synthesises a rerun receipt from the receipt's captures with a fresh
`started_utc` would satisfy every replay condition. This is not a predicate miss (the C2
predicate claims re-acquisition and projection equality, not execution), but it is the
boundary the frontier paragraph has to state, and the round-47 K2Cheat class is narrowed, not
closed. Proposed: have the live tool write a per-run nonce file through a path the server
child touches (or require a port-bind/pid-liveness join at rerun time) and make the replay leg
require it.

Pre-existing, not re-reported: `gate-registry-check` lists the two round-48 counters as
unregistered; the round-41/42/43 counters' 33-vs-34 spot-check count; `hexrun-census`'s
`d0012618` unknown. Nothing in this seat changes them.

## Touched surfaces

- Written: `.ufo/waves/round-48/w1/out/S9Readme/frontier.md`,
  `.ufo/waves/round-48/w1/out/S9Readme/{c1-counter.out,c2-counter.out,v3-lane-build.json,v3-lane-base.json,v3-lane-thr1.json}`,
  this report.
- Read-only: the lane at `b85783e8`/`380bcdff`/`33e00582`, the frozen counters and
  preregistration, the three v5 receipts, `c2/live/install.txt`, `c2/hf-revision-499bc882.txt`,
  `controls/*`, `corpus/README.md`, `corpus/SOURCES.md`, `SCORECARD.md`.
- Scratch: `/fast/scratch/hyaku/kama-r48/S9Readme` (one shared clone, one throwaway fixture
  repo, both removed before finishing).

## Out of scope (integration, not this seat)

SCORECARD sections and capability rows, `registry/` rows, the b11909 ledger population, the
round-48 counter registration, and any edit to the counters, preregistration, controls or
`corpus/README.md` (the block is proposed, not applied).

## Tooling

No packages installed or upgraded; no `pacman`; no service started. Only `gh` (already
authenticated) was used, two API reads for the b11909 release identity and `releases/latest`.

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Readme/frontier.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Readme.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Readme/c1-counter.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Readme/c2-counter.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Readme/v3-lane-build.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Readme/v3-lane-base.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Readme/v3-lane-thr1.json`
