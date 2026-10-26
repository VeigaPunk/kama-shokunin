## Round 47 — append-only-audit v2 against numstat and a declared contract (calibration) and replayable live receipts at b11909 (operability) (2026-10-26)

Authority: `shokunin.conf` assigns operability + calibration; the lowest-scoring assigned axis is calibration (7), and C1 works it, while C2 works the other assigned axis, operability (8). Calibration 7 is below the saturation line 8, so the stagnation nudge is inactive. Base `172b8ad040d51ce8c011238c1408d4e0b6aa9595` (round-46 spot-check); freeze commit `bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba` (`.ufo/waves/round-47/preregistration.json`; counters `tools/round47-append-audit-v2-check.py` sha256 `a180ab84cc642731a6bd5fca92e5218dfaa6c074279e2f001110b348d73755ed` and `tools/round47-live-replay-audit.py` sha256 `15408dce5b2f8f5dbe4dd7bacf17ddb0737fcbe480686907f40483273b128b0f`, both byte-identical at the freeze and at the build; controls `.ufo/waves/round-47/controls/`; KQ64 receipt `.ufo/waves/round-47/freeze/prereg-time-check.out` → `RESULT pass: no timestamp later than the committer time`, exit 0). Both corrections landed after the freeze at `3a09a1d93dcc16799cf6c4b48786e6440af134c4` (9 files, +2517/−114), before the wave: `tools/append-only-audit.py` v2 with `registry/append-only-contract.tsv` (C1), and `tools/kama-llamacpp-live.py` v4 with `tools/kama-live-replay.py` and three b11909 receipts (C2). C1 is routed from the round-46 outside closure D1 (`--`-prefixed deleted lines dropped: `0718b6ab` SCORECARD 2417 against numstat 2421) and D2 (`restored_at_tip` fell 2416 → 2409 when the tip moved); C2 from r46-D5 and r45-D3 (receipts that could not be re-run once a cache path vanished, and a dead `log_path`).

| Claim | Axis, score | Before → after | Counting command | Evidence |
|---|---|---|---|---|
| C1 — `append-only-audit` v2: the lane's append-only self-description audited over the files a machine-readable contract declares, every deleted count equal to `git diff --numstat`, restoration a byte-exact multiset maximum over the event's own window (routed r46-D1, r46-D2) | calibration 7 → 7 (instrument correction; no score move) | base `selftest=1 contract=0 lane=0 fixture=0 stable=0 files=0 lane_events=0 lane_mismatch=-1 fixture_mismatch=-1 met=False` (exit 1) → measured value in the round-47 measured-results block, which lands with the measured commit | `python3 tools/round47-append-audit-v2-check.py --repo <fresh clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-47/controls/base.c1.out`; `tools/append-only-audit.py`; `registry/append-only-contract.tsv` |
| C2 — three live receipts at llama.cpp b11909 carry where the server binary and the model came from, and `tools/kama-live-replay.py` re-acquires both into an empty home, verifies each digest, re-runs the lifecycle and refuses a receipt with a wrong digest (routed r46-D5, r45-D3) | operability 8 → 8 (sourced on the b11909 release row opened this round) | base `receipts=0 replay=0 tamper=0 newrow=0 rerun_checks=0 met=False` (exit 1) → measured value in the round-47 measured-results block, which lands with the measured commit | `python3 tools/round47-live-replay-audit.py --repo <fresh clone> --tip <full commit> --scratch <dir> --out <receipt>` | `.ufo/waves/round-47/controls/base.c2.out`; `.ufo/waves/round-47/c2/live/receipt-{1,2,3}.json`; `.ufo/waves/round-47/c2/live/install.txt` |

Controls (all `met=False`, `.ufo/waves/round-47/controls/`): base — C1 `selftest=1 contract=0 lane=0 fixture=0 stable=0 met=False` (the contract file is absent at the base, so v2 cannot expand a file set: `detail: contract: absent at tip`), C2 `receipts=0 replay=0 tamper=0 newrow=0 met=False`; C1 `junk-c1-v1-contract` — the v1 tool unchanged plus a contract file `selftest=1 contract=0 lane=0 fixture=0 stable=0 files=84 met=False` (`detail: lane: tool exit=2, stdout is not one JSON object`; `detail: contract: tool files (0) != expansion (84)`); C1 `junk-c1-v1-numstat` — v1 with the `---` filter fixed and v2 key names `selftest=0 contract=1 lane=0 fixture=0 stable=1 files=84 lane_events=5 lane_mismatch=4 fixture_mismatch=6 met=False` (the two SCORECARD events come back `restored_max` 2413 and `None` instead of 2420 and `dd9f5dc6`, and three fixture events lose their window maximum); C2 `junk-c2-r46-relabel` — the b11906 receipts relabelled v4 `receipts=0 replay=0 tamper=0 newrow=0 rerun_checks=11 met=False` (`detail: receipts: … build_info 'b11906-4d71b42fd'`; `detail: replay: rerun inputs not re-acquired under scratch`, both under `~/.local/opt` and `~/.cache`; `detail: tamper-model: exit 0, rerun outcome pass: not refused`).

### Round-47 append-only audit at the build commit

v2 reads the file set from a contract, not from a list in the tool.
`registry/append-only-contract.tsv` carries a header and seven rows (LOG.md,
SCORECARD.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md,
`corpus/lessons/*.md`, registry/history/DELTA.md), each with a `declared_at`
line in the lane that states the rule; expanded over `git ls-tree -r`, they are
85 files, 79 of them `corpus/lessons/*.md` blobs. `python3 tools/append-only-audit.py --repo
<fresh clone> --to 3a09a1d93dcc16799cf6c4b48786e6440af134c4` exits **1**:

```
event dd9f5dc6c0e6 SCORECARD.md deleted=31 restored_max=24 status=partial restored_best=dd9f5dc6c0e6 restored_by=-
event 0718b6abbda6 LOG.md deleted=2292 restored_max=2292 status=restored restored_best=82b5e9d33a19 restored_by=82b5e9d33a19
event 0718b6abbda6 SCORECARD.md deleted=2421 restored_max=2420 status=partial restored_best=82b5e9d33a19 restored_by=-
event 0718b6abbda6 corpus/QUALITY.md deleted=375 restored_max=375 status=restored restored_best=82b5e9d33a19 restored_by=82b5e9d33a19
event 0718b6abbda6 corpus/README.md deleted=663 restored_max=663 status=restored restored_best=82b5e9d33a19 restored_by=82b5e9d33a19
summary commits=303 files=85 events=5 restored=3 partial=2 unrestored=0
```

The two routed defects are the two numbers that moved. `0718b6ab`
SCORECARD.md now reads `deleted=2421` and LOG.md `2292`, equal to
`git diff --numstat --no-renames 0718b6ab^1 0718b6ab -- <file>` (2421 and
2292); v1 read 2417 and 2290 because four `--out …` lines and two
(`--tip`, `--rev`) begin with `--`. And the SCORECARD restoration is
`restored_max=2420` measured over the window rather than `restored_at_tip`
against the audited revision: v1 read 2416 at `4a2a4d55` and 2409 at the
round-46 tip, and the same event now reads 2420 at a third, later tip. What
v2 still cannot hold is one line per SCORECARD event, and in both cases it
is head text the file declares re-derived (`SCORECARD.md:6`): the seven
never-held lines of `dd9f5dc6` are the six round-41 `## Axes` rows and the
round-41 reconcile sentence, and the one never-held line of `0718b6ab` is
the round-44 `depth` row ("| depth | **7** | SKILL.md sha256 91440eb8… (1420
lines) … | score round 1; evidence re-anchored round 44 |"), each replaced in
place by a re-anchored row. The SCORECARD contract row says so
in its note ("a head re-anchor is an expected partial"), and v2's
`status` names the same two events partial as v1 did: no verdict class
changes.

The frozen C1 counter is already green at the build commit, so what the
measured commit adds is a re-run rather than new instrument work:
`python3 tools/round47-append-audit-v2-check.py --repo <clone> --tip
3a09a1d9… --scratch <dir>` → `selftest=1 contract=1 lane=1 fixture=1
stable=1 files=85 lane_events=5 lane_mismatch=0 fixture_mismatch=0
met=True`, exit 0 (receipt `c1-counter-at-build.out` in this round's seat
output). C2 is red at the build for one leg only: the L1's pre-wave dry run
reads `receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False`,
because the b11909 `corpus/SOURCES.md` row lands at integration.

**Provenance on the C2 side.** The three receipts are
`kama-llamacpp-live/v4`, `outcome pass`, 11 evaluated checks each,
`captures.props.fields.build_info` `b11909-caa8191df`, and
`provenance.server.member` `llama-b11909/llama-server`; `teardown.log_path`
is null in each, which the counter accepts. The asset
(`llama-b11909-bin-ubuntu-x64.tar.gz`, 22,475,032 bytes, sha256
`bf94332a…695b`) and the model (`stories260K.gguf`, sha256
`270cba1b…256d`) are named by URL and digest, and `install.txt` records the
release digest they were checked against
(`.ufo/waves/round-47/c2/release-b11909.json`).

**Limits, read off the instruments.** The counter and the tool share v2's
definitions by contract; ground truth independent of both is `git diff
--numstat` for the deleted count and the constructed fixture for every
field. The contract's coverage is only as good as its rows: a lane file
declared append-only but absent from the contract is not an event, and a
deletion below 20 lines is not measured at all (a wave seat's sub-threshold
census is routed to the round-48 plan below). On the C2 side a replay is
three sampled instants on a 1.2 MB model, agreement is check-by-check
pass/fail equality rather than byte equality of bodies, and the counter
replays receipt-1 only.

**Capabilities — canonical list as of round 47**
Same four columns as the round-46 canonical list, which stays byte-intact; one row is added (`live-receipt-replay`) and `append-only-audit` is reworded for v2 - contract-declared file set, deleted counts equal to `git diff --numstat`, restoration as a maximum over the event's own window - with its first-working round unchanged at 46.
| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed; readiness always unknown | `tools/kama-ollama-evidence.py` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp b11755 server on an unregistered loopback port, capture its loading and ready surfaces, grade and tear it down | `.ufo/waves/round-16/live/receipt.json` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20 |
| context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30 |
| pin-watch | List upstream release tags for each pinned serving engine (SGLang, vLLM, llama.cpp) and report, per pin, the newest release tag and how many releases sort above it; exit 1 flags a recheck trigger | `tools/pin-watch.py`; `registry/engine-pins.tsv`; `corpus/knowledge/engine-pin-watch.md` | 41 |
| digest-ledger | Find every full SHA-256 the lane's documents cite and classify it: a committed blob, a ledger-declared external artifact re-hashed on this host, an unverifiable digest with its reason, or a flagged known-wrong digest; exit 1 on any unexplained digest | `tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 42 |
| hexrun-census | Find every lower-case hex run of 32-127 characters other than 64 that the lane's documents cite (git object ids, MD5 sums, over-long or abbreviated runs) and classify it: a lane object, the MD5 of a committed blob, an upstream object whose committed evidence file contains it, an unverifiable run with its reason, or a flagged wrong run linked to a correct one; exit 1 on any unexplained run | `tools/hexrun-census.py`; `registry/hexrun-ledger.tsv` | 43 |
| append-only-audit | Set the lane's contract-declared append-only self-description - the paths and patterns `registry/append-only-contract.tsv` names, each row pointing at the lane line that declares the rule - against its git history: list every commit that deletes >= 20 lines from one of those files with a deleted count equal to `git diff --numstat` (byte-exact, so no `--`-prefixed line is lost), report the largest share of those lines any commit in the event's own window holds again (a multiset maximum, so a later head re-anchor cannot lower it) and which later commit first holds all of them, and exit 1 on a partial or unrestored mass deletion | `tools/append-only-audit.py`; `registry/append-only-contract.tsv`; `tools/round47-append-audit-v2-check.py` | 46 |
| live-receipt-replay | Re-acquire a `kama-llamacpp-live/v4` receipt's server release archive and model from the URLs its provenance block records, verify both sha256 values before anything is extracted or executed, re-run the lifecycle from an empty home and compare every check the original evaluated, and refuse a receipt whose provenance is missing, whose recorded digest does not match what it downloads, or whose server-archive member is unsafe | `tools/kama-live-replay.py`; `.ufo/waves/round-47/c2/live/receipt-1.json` | 47 |

### Planned (round 48)

1. Calibration: give the append-only contract a coverage check. A lane file
   that some other lane text declares append-only but that no contract row
   names is invisible to C1, and so is every deletion below the 20-line
   threshold (a round-47 seat's sub-threshold census reports 22 such events in
   `corpus/lessons/*.md` alone, all below the threshold; routed, not
   re-verified here). The candidate is a reader that takes the declared set
   from the lane's own declarations and reports the difference from the
   contract, plus a per-file deletion census at threshold 1 in which every
   event carries a disposition, scored against a hand-read sample the way round
   45's claim-outcome re-freeze was routed, under a counter frozen before it is
   scored. The round's second option is the counter/tool shared-definition
   limit: v2's definitions live in both and only `git diff --numstat` and the
   constructed fixture are independent of them.
2. Freshness: llama.cpp after b11909 (b11910, prerelease, published
   2026-10-26T21:20:07Z, `gh api repos/ggml-org/llama.cpp/releases`) — the
   91-row b11906 ledger re-verified at b11909 or later, the five rows a
   round-47 seat reports need renumbering (`src/llama-context.cpp`,
   `src/llama-kv-cache.cpp`), the ten off-population llama.cpp rows, and the
   floating-series rows S013 and S022.
