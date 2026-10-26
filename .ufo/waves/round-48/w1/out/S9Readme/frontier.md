## Frontier disposition — round 48

Two claims were built at `380bcdff9c8af06997c482f6eb03db926a794a2b` (base
`33e005827742b29772b153cda036ec9f27f653be`, the round-47 closure; counters frozen at
`12284ba3`): append-only-audit v3 under a bound contract (C1, calibration) and live
receipts a fresh session can replay with record-time provenance (C2, operability). The
figures below are measured at that build commit with the frozen counters; the capability
rows, scorecard sections and registry rows are integration work and are not pre-empted
here.

**What v3 now audits.** `tools/append-only-audit.py` (schema `append-only-audit/v3`) takes
a `region` cell for every contract row: `*` grades every line, `exempt=<T1>|…@path:line`
leaves the named `## ` sections ungraded while a section is not gutted, `only=<prefix>@path:line`
grades only the sections whose title starts with the prefix. At `380bcdff` the nine rows of
`registry/append-only-contract.tsv` expand to **89 files** — the five self-description files,
81 lesson files, `corpus/knowledge/consumer-registry.md`, `registry/history/DELTA.md` and
`registry/report-landing-errata.tsv` — over 311 commits.

The two carve-outs the lane declared but could not previously apply are applied:

- **SCORECARD's head.** The five titles `SCORECARD.md:6` names as re-derived —
  `## Axes`, `## Planned`, `## Retired`, `## Saturation`, `## Capabilities` — are ungraded
  *while the section is not gutted*: an exempt title T is eligible for an event when the
  maximum of its line count over the event window is at least its line count at the parent.
  An in-place head rewrite is therefore an event with its deletions ungraded, and a head
  collapsed and never regrown is graded and unrestored.
- **The consumer-registry Errata region.** `corpus/knowledge/consumer-registry.md:30`
  declares its `## Errata` region append-only while the dated census body above may be
  edited; the row is `only=## Errata`, so only deletions inside an `## Errata` section are
  graded. At `--threshold 1` the file's four events are all `ungraded` (0 graded lines of
  1, 15, 1 and 2 deleted) — body edits are outside the rule, as declared.

Every declaration must bind, and the exit code now carries the regression signal:

- binding: the `declared_at` line must say `append-only` (or `append only`) for that path,
  contain none of four listed negations, and name the row's path token or sit in a file the
  row's pattern covers; an `exempt` pointer must call every title re-derived, an `only`
  pointer must declare its prefix. An unbound or malformed row exits 1.
- `regressed` exits 1: an event whose file holds fewer graded lines at the audited revision
  than at its best window commit. This is the round-47 X1Stable finding and it is what the
  build hit first. At the base `33e00582`, v3 with the round-48 contract reports
  `regressed=1`, exit 1: the `0718b6ab` SCORECARD event holds **2348** of its 2349 graded
  lines, and the one missing line is the round-45 authority banner at line 6 — text rounds
  46 and 47 rewrote in place. Line 6 sits before the first `## ` heading, so no exempt title
  can cover it. The build appended the round-45 and round-46 banners byte-exact under
  `### Superseded head banners (kept verbatim; round 48)` (`SCORECARD.md:2736`); the same
  event then holds 2349 and is `restored`.

At `380bcdff` the tool reports `commits=311 files=89 events=5 restored=5 partial=0
unrestored=0 ungraded_lines=89 regressed=0 vanished=0 bad_declarations=0`, exit 0: `LOG.md`
2292/2292 graded lines restored, `SCORECARD.md` 2349/2349 with 72 ungraded, `corpus/QUALITY.md`
375/375, `corpus/README.md` 663/663, and the `dd9f5dc6` SCORECARD event 14/14 with 17
ungraded. The frozen C1 counter reads
`selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5
lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True`, exit 0.

**What v3 still does not audit.**

- *The line-6 banner has no region vocabulary.* Region titles and prefixes must begin
  `## ` (`tools/append-only-audit.py:147-151`), and a line before the first `## ` heading has
  no section at all (`tools/append-only-audit.py:231-239`). The banner the lane rewrites
  every round is therefore always graded, and the carve-out covers the five head sections,
  not the preamble block that announces them. Round 48 keeps exit 0 by *appending* the
  superseded banner, not by exemption; a round that rewrites line 6 without appending the
  old text exits 1 — correctly, but as the instrument's law rather than as the lane's
  declared practice.
- *Eligibility is content-blind.* A declared title is ungraded whenever its line count over
  the window reaches the parent's, whatever the text. The tool's own `exempt-rewritten`
  case replaces 24 head lines with 24 unrelated ones and grades 0 lines, exit 0; the
  `exempt-gutted-then-regrown` case does the same when the section returns later in the
  window. `## Axes` could be replaced wholesale by same-length junk and no event would carry
  a graded line.
- *Sub-threshold deletions.* The threshold is 20 deleted lines per (commit, file)
  (`tools/append-only-audit.py:396`), a policy constant the contract does not derive; a
  19-line deletion is not an event. At `--threshold 1` the same revision reports 98 events
  (14 restored, 4 partial, 62 unrestored, 18 ungraded, 186 ungraded lines, exit 1), so the
  instrument grades 5 of the 98 deletion events a one-line threshold surfaces.
- *Binding is a lexical tripwire, and the counter shares it.* The negation list is four
  contiguous phrases (`tools/append-only-audit.py:119`) and the path token is a bare
  substring match (`:180-199`). A fixture whose declaring lines read `LOG.md isn't
  append-only.` and `The changelog is not really append-only.` binds both rows — the `log`
  inside `changelog` supplies the token — with `bad_declarations=0`, exit 0, and the frozen
  counter's `binds()` (`tools/round48-append-audit-v3-check.py:147,226-233`) returns the same
  answer, so no leg of it can catch a false bind.
- *The `A-row` rule is not expressible.* The `rule` cell is parsed and validated
  (`tools/append-only-audit.py:171-174`) but grading reads only the region; `corpus/SOURCES.md`
  is `A-row` with region `*`, so the cells the row calls mutable (`status`, `recheck`,
  `used-by`) are graded whole-file like any other line.
- *Restoration is a multiset over the whole file, not by position.* Identical text anywhere,
  in any section, counts; an appended copy of a deleted banner is a restoration, and so is a
  duplicate line standing in for a different one.
- *Coverage is only as good as the rows.* A lane file declared append-only but missing from
  the contract is invisible, and a `## ` inside a fenced block is a section boundary
  (preregistration limits).

**What the v5 receipts and the replay now prove.** The three receipts
(`.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json`) are `kama-llamacpp-live/v5`, `outcome
pass`, 11/11 evaluated checks each, on unregistered loopback ports 33779, 41891 and 45023
(alias `kama-r48-live`, `--ctx 256`, `-t 1`), `build_info b11909-caa8191df`, with `props`,
`slots`, `health`, `models` and `metrics` captures and the loading 503 observed. Their
provenance is checked when it is recorded, not when it is read: the model is pinned to
Hugging Face revision `499bc8821c6b12b4e53c5bffcb21ec206f212d81` (sha256 `270cba1b…bd256d`),
the server asset is `llama-b11909-bin-ubuntu-x64.tar.gz` (sha256 `bf94332a…e695b`, member
`llama-b11909/llama-server` sha256 `35ac50fb…d7ff0`), and `provenance.verified.at` is
`record`: the live tool hashed the archive, the archive member and the model *before*
starting the server. The counter's `recordcheck` leg therefore passes only if the tool exits
2 with no server executed and no pass receipt for an unpinned `resolve/main` URL, a wrong
archive digest, an `http://` asset URL, a partial flag set and a non-server member — with a
marker file proving non-execution — and executes a stub with every flag right.

Each receipt replays from committed bytes: the replay re-acquires both recorded URLs into
scratch, the counter hashes the rerun's `server.realpath`, `model.path` and archive itself
against the frozen digests, requires the rerun's `started_utc` not to precede the counter's
start and its model commit to be the frozen one, and compares every evaluated check plus a
stable projection of the captured surfaces (props fields, slots count and body digest,
health status and body digest, models ids and `owned_by`, metrics status, loading envelope,
teardown outcome, listener ownership). `replayed=3/3`. `--compare` separates instance facts
(port, pid, times, log text, `models.created`) from those surfaces: a copy with only instance
fields changed exits 0, each of five copies with one stable surface changed exits 1. Wrong
digests and swapped URLs (the b11906 asset, another HF revision) are refused with a
digest-mismatch and no rerun. The frozen C2 counter reads `receipts=1 recordcheck=1 replay=1
compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True`, exit 0 — and round 47's one
unmet leg is closed: `corpus/SOURCES.md:245` (S492) carries the pinned revision URL.

**What they still do not prove.**

- *That a server ran at replay time.* The replay leg hashes the re-acquired files and
  compares projections, but witnesses no process: no marker, pid, log freshness, port
  binding or loading observation is required of the rerun
  (`tools/round48-live-replay-v5-audit.py:401-435`; the marker lives only in `recordcheck`,
  `:289-333`). A replay tool that downloads the archive and the model, extracts the binary,
  and synthesises a rerun receipt from the receipt's own captures with a fresh `started_utc`
  would satisfy every replay condition. What holds the chain up is the lane's own live tool,
  not the counter; the counter's independent parts are the digests and the projection.
- *That the evidence outlives its hosts.* b11909 is a GitHub **prerelease** (`prerelease:
  true`, target `caa8191d`, published 2026-10-26T21:00:58Z, about 86 minutes before the
  receipts), and `releases/latest` is v0.7.0 (`prerelease: false`, target `620d2225`) — a
  semver release far behind, so the newest-release API is not a freshness oracle. A `bN` tag
  can exist before its release (round 46's b11907 answered 404), and a release asset can be
  deleted or re-uploaded: the replay then fails closed on the digest and the evidence stops
  being replayable rather than becoming wrong. The only retained copy is host-local
  (`~/.local/opt/llama-b11909*/…`), not committed. The model side pins a revision of a repo
  named `models-moved`: stable while the repo and revision exist.
- *Anything beyond the sample.* Three sampled instants, one 1,185,376-byte tiny model,
  `--ctx 256`, `-t 1`, unregistered loopback ports, one platform (ubuntu-x64) and a replay
  that needs network to github.com and huggingface.co. No registered consumer was sampled
  and no K05 declared-versus-served context comparison is in scope.

**Still frontier:**

- A declared region for the SCORECARD preamble banner (region grammar is `## `-only), or an
  explicit lane rule that the banner is append-kept and the instrument says so.
- Content-aware eligibility for the five exempt head sections; today a wholesale
  same-length replacement is invisible.
- The 20-line threshold as a derived rather than a constant policy, and the 93
  sub-threshold deletion events one-line grading surfaces.
- A binding test a denial cannot pass, and a counter leg that does not reuse the tool's own
  `binds()`.
- Expressing an `A-row`'s mutable cells as a region rather than grading the whole file.
- An execution witness in the replay leg (marker or pid/liveness join) so that "replayed"
  means a server ran, and a retention answer for the prerelease asset the receipts name.
- Carried over unchanged from round 47 and not re-measured here: the b11906 ledger population
  at b11909+ (at least S107, S130, S132, S113, S135), S013's re-pin, S022 and the unpinned
  vLLM stable pages S002–S004, the llama.cpp-citing family count outside the 91-row
  population, the `hexrun-census` unknowns, K05, and the registered consumers (last admitted
  sample 2026-10-15, all `DEAD`, not re-opened by an ephemeral replay server).
