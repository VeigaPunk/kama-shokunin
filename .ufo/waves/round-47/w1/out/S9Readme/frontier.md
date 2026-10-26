## Frontier disposition — round 47

Two claims were built at `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (freeze
`bbcc6dc2`, base `172b8ad0`): append-only-audit v2 with a declared contract (C1,
calibration) and live receipts that a fresh session can replay (C2, operability). The
figures below are measured at that build commit; the capability rows, the scorecard
sections and the b11909 registry row are integration work, not part of this commit, and
are not pre-empted here.

**What is now audited.** `tools/append-only-audit.py` (schema `append-only-audit/v2`)
reads its file set from `registry/append-only-contract.tsv`, whose seven rows each name
the lane line that declares the rule: `LOG.md` (`README.md:16`), `SCORECARD.md`
(`corpus/README.md:521`), `corpus/QUALITY.md` (`corpus/QUALITY.md:24`), `corpus/README.md`
(`corpus/README.md:86`), `corpus/SOURCES.md` (`SKILL.md:578`), `corpus/lessons/*.md`
(`corpus/lessons/round-23.md:100`) and `registry/history/DELTA.md`
(`registry/history/DELTA.md:3`). At `3a09a1d9` that contract expands to 85 files — the
five self-description files, 79 lesson files and `DELTA.md` — over 303 commits.
`python3 tools/append-only-audit.py --repo <clone> --to 3a09a1d9` reports
`commits=303 files=85 events=5 restored=3 partial=2 unrestored=0`, exit 1; its selftest
is `AOA_SELFTEST pass=15 fail=0`. Three things changed from v1. Deleted counts are the
numbers `git diff --numstat --no-renames 0718b6ab^1 0718b6ab` prints — 2292 `LOG.md`,
2421 `SCORECARD.md`, 375 `corpus/QUALITY.md`, 663 `corpus/README.md` — where v1 read
2290 and 2417 because it dropped every deleted line starting with `--` (round-46 closure
D1). Lines compare byte-exact, CRLF and a missing final newline included, and restoration
is a multiset measure maximised over the event's own window (D2): `82b5e9d3` restored
`LOG.md`, `corpus/QUALITY.md` and `corpus/README.md` exactly, and the two `SCORECARD.md`
events read 2420/2421 and 24/31 at `172b8ad0` *and* at `3a09a1d9`, so the tip moving no
longer lowers a restoration (the round-46 spot-check measured v1 falling 2416→2409 on a
head re-anchor). `corpus/lessons/` (79 files, previously unguarded) is inside the audited
set. The round-47 counter recomputes every field on its own code path and reads
`selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5 lane_mismatch=0
fixture_mismatch=0 met=True`.

**What is still not audited.** The audit is file-scoped: the tool expands each contract
row's path pattern and never reads its `rule`, `declared_at` or `note` cell
(`tools/append-only-audit.py:184`), so the contract's prose is documentation, and the
declaring-line check lives only in the round-47 counter. Three consequences. (1) The
`SCORECARD.md` carve-out is declared but not applied: the contract row says the head
sections named at `SCORECARD.md:6` are re-derived in place and a head re-anchor is an
expected partial, yet the two partial events above are indistinguishable from a real
loss of 7 and 1 lines — the exit 1 is a signal to read the contract row, not a verdict.
(2) Only one knowledge file's heading calls its errata region append-only —
`corpus/knowledge/consumer-registry.md:30` (`## Errata — 2026-10-14 re-census
(append-only; rows below keep their round-1 text)`); `corpus/knowledge/context-capacity.md:245`
(`## Errata — round 26`) carries the same semantics without the word ("the round-25
wording above stays") — and no contract row covers `corpus/knowledge/*.md`; whole-file
inclusion would be wrong because the body of those entries is a dated census that may be
edited, so the region needs its own scoping before it can be audited. (3) The 20-line
threshold is a policy, not the rule: at `--threshold 1` the same tip reports 91 events —
12 restored, 8 partial, 71 unrestored —
26 in `SCORECARD.md`, 20 in `corpus/SOURCES.md`, 13 in `LOG.md`, 8 in `corpus/README.md`
and 26 across 15 lesson files, so deletions below 20 lines in files the lane calls
append-only are unwatched. `corpus/SOURCES.md` is declared `A-row`, whose mutable cells
(`status`, `recheck`, `used-by`) are enforced by `tools/sources-append-only.py`
(`SKILL.md:578`, `--selftest` 42/42), not by this audit.

**Live receipts that replay.** The three b11909 receipts
(`.ufo/waves/round-47/c2/live/receipt-{1,2,3}.json`) are `kama-llamacpp-live/v4`: each
records an `outcome` of pass with 11/11 evaluated checks on unregistered loopback ports
37903, 44883 and 39739 (alias `kama-r47-live`, `--ctx 256`, `-t 1`), `build_info
b11909-caa8191df`, ready body `{"status":"ok"}`, `/metrics` 501, one graceful SIGTERM
with `returncode 0`, and a `provenance` block that names where each input came from —
the release asset `llama-b11909-bin-ubuntu-x64.tar.gz` at its URL with sha256
`bf94332a…8695b` and archive member `llama-b11909/llama-server`, and the model
`stories260K.gguf` at `https://huggingface.co/…` with sha256 `270cba1b…bd256d` — so a
replay no longer depends on the host cache paths the same receipts still record
(`server.realpath`, `model.path`), and `teardown.log_path` is null because the temp log is
deleted, its kept lines inlined in `teardown.log_lines`. `tools/kama-live-replay.py`
re-acquires both recorded URLs into `--work`, verifies each sha256 *before* anything is
extracted or executed, re-runs the lifecycle with the receipt's alias, ctx and threads and
compares check by
check, and refuses a receipt whose recorded digest is wrong (`KLR_SELFTEST pass=10
fail=0`). The round-47 C2 counter at `3a09a1d9` reads `receipts=1 replay=1 tamper=1
newrow=0 rerun_checks=11 met=False` (exit 1): the replay runs from `git archive` under a
fresh `HOME`, reproduces all 11 checks, both tampered copies are refused, and the only
unmet leg is the `corpus/SOURCES.md` row naming `b11909` and `caa8191d…`, which the C2
predicate needs and this build does not yet carry. The boundary is unchanged: three
sampled instants on one tiny model, unregistered ports, per-check pass/fail agreement
rather than byte equality, and a replay needs network to github.com and the model host.
b11909 is a third build of the same instrument, so it backs the lifecycle propositions of
S041, S046 and S055 at a new build; it does not re-verify their b11889/b11906 bytes, and
no registered endpoint was sampled.

Still frontier:
- The b11906 ledger population re-verified at b11909+. `registry/release-recheck-b11906.tsv`
  is still the b11906 readout: 91 rows on 16 pinned files. b11909 =
  `caa8191df159f764fb0160e3d2fc6be008948aee` is 3 commits after b11906
  (`gh api repos/ggml-org/llama.cpp/compare/b11906...b11909` → `total_commits 3`, 38
  files changed) and two pinned files moved — `src/llama-context.cpp` (S107, S130, S132)
  and `src/llama-kv-cache.cpp` (S113, S135) — so at least those five rows need a re-read
  at b11909+ before the population can be restated at the new release. This build
  re-reads no row, and the b11909 live receipts do not stand in for it. S477's
  tag-inventory figure stays stale as round 46 measured it (highest `bN` tag b11887 there,
  b11907 at the round-46 sample), and its 30d recheck is not due until 2026-11-24; the
  release identity the population assumes is still a counter constant rather than a
  re-derived fact.
- S013 (Ollama importing a model): still `mined`/`on-release`, used by
  `corpus/knowledge/gguf-runtime-compatibility-boundary.md`, and round 46's measurement
  still stands — `docs/import.md` is 404 at the cited `6d02a43a` (the page became
  `docs/import.mdx` there) — so the row needs the re-pin proposed in round 46
  (`98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18`), not a re-read.
- S022 and the unpinned vLLM stable pages S002–S004: S022 is still `queued` with no
  used-by and a floating `stable` alias, and the build takes no new page read for any of
  the four. They remain frontier because no revision pin and no release trigger dates
  them.
- The rows that cite llama.cpp but fall outside the 91-row population. Round 46 named ten
  (S026, S028, S038, S041, S046, S055, S477, S482, S484, S485); S486 (b11906 binary) and
  S487 (b11906 receipts) sit in the same family and are not in that list, so the family is
  at least twelve and its count needs re-deriving under its own stated rule before it is
  quoted as a number. S026 (PR #18001) and S028 (issue #4746) stay rejected and untouched;
  S038, S482, S484 and S486 are release-asset identity rows that a new release says
  nothing about; S041, S046, S055 and S485 are historical receipts, backed by the b11909
  sample at a new build, not re-verified by it.
- The `hexrun-census` unknowns. `python3 tools/hexrun-census.py scan --repo <clone> --rev
  3a09a1d9` reads `tokens=1772 distinct=280 lane_oid=178 md5_blob=1 upstream_ok=68
  unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=22`, exit 1, against 21 at the
  round-46 measured tips (`42ea1204`, `e8fa87ef`); the additional token
  `8bca0cf333e7ceab5e734b354c87075c6efec86c` is cited in
  `corpus/lessons/round-46-verifier-spotcheck.md:23`, so round-46 D4 (ledger or close the
  unknowns) is still open and this round's red gate is pre-existing, not raised by the
  build.
- The instrument's edges: region scoping for the two knowledge `## Errata` blocks, the
  `SCORECARD.md` head carve-out that the tool cannot apply, the 20-line threshold (91
  events at 1), and contract coverage that is only as good as the rows it carries — a lane
  file declared append-only but missing from the contract is not detected.
- K05 (declared versus served context capacity): unchanged. No authorised
  registered-endpoint sample exists, and this round's fixture run at `--ctx 256` is
  excluded by the context-capacity rows' scope.
- Registered consumers: still no sample this round. The last admitted sample
  (2026-10-15: 3 rows, all `DEAD`) is not re-opened by an ephemeral replay server, and the
  replay instance was torn down with the port refused.
