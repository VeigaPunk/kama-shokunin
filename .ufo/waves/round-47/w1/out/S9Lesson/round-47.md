# kama round 47 lesson

author: kama L1 (agent `KamaR47`); skeleton drafted by wave seat `S9Lesson`, integrated and completed by the L1
date: 2026-10-26
base: `172b8ad040d51ce8c011238c1408d4e0b6aa9595`
freeze: `bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba` (preregistration `.ufo/waves/round-47/preregistration.json`, `frozen_at_utc` 2026-10-26T21:12:52Z; KQ64 receipt `.ufo/waves/round-47/freeze/prereg-time-check.out`)
build: `3a09a1d93dcc16799cf6c4b48786e6440af134c4`
measured: `<fill at integration: measured commit and its receipts>`

This file is a **skeleton**: every `<…>` token is a placeholder the L1 fills after
integration. Everything stated as observed below was read or run by seat `S9Lesson`
at the named commit; its receipts are under
`.ufo/waves/round-47/w1/out/S9Lesson/` and the per-item paths are given inline.
The lane tip at draft time was `46a924e0` (wave spec and dispatch; no integration
commit yet), so no b11909 registry row exists at the build tip and the Gate row
ids below are placeholders taken from the `corpus/SOURCES.md` tail (last row
`S487`; next free `S488`).

## Claims

- **C1 calibration 7→7 `<final wording from preregistration>`.** append-only-audit v2
  (`tools/append-only-audit.py`, schema `append-only-audit/v2`) audits the files
  `registry/append-only-contract.tsv` declares, reads deleted lines by hunk-header
  counts byte-exact and equal to `git diff --numstat`, and measures restoration as a
  multiset maximum over the event's own window. Build-tip observation by this seat,
  **not the measurement**: the frozen counter
  `tools/round47-append-audit-v2-check.py` at `3a09a1d9` prints
  `selftest=1 contract=1 lane=1 fixture=1 stable=1 files=85 lane_events=5
  lane_mismatch=0 fixture_mismatch=0 met=True`, exit 0
  (`out/S9Lesson/c1-counter.out`). The tool itself reports 5 events, exit 1:
  `dd9f5dc6` SCORECARD 31/24 partial; `0718b6ab` LOG 2292 restored, SCORECARD
  2421/2420 partial, QUALITY 375 restored, README 663 restored. Deleted counts equal
  `git diff --numstat --no-renames` for all five (`out/S9Lesson/evidence-stability.txt`).
  `<measured values: SCORECARD §Round-47 measured results>`
- **C2 operability 8→8 `<final wording from preregistration>`.** three live receipts
  at llama.cpp b11909 in schema `kama-llamacpp-live/v4` carry a provenance block
  (asset URL, digest, archive member; model URL, digest) and a null `teardown.log_path`;
  `tools/kama-live-replay.py` re-acquires both into `--work`, verifies both digests,
  re-runs the lifecycle and compares checks. Build-tip observation by this seat,
  **not the measurement**: the frozen counter `tools/round47-live-replay-audit.py`
  at `3a09a1d9` prints `receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11
  met=False`, exit 1, with the single detail `newrow: no registry row names b11909
  and caa8191df159f764fb0160e3d2fc6be008948aee` (`out/S9Lesson/c2-counter.out`);
  the b11909 SOURCES row is `<the row that lands at integration>`. Receipts verified
  locally: all three v4, outcome pass, 11/11 checks passed, `build_info
  b11909-caa8191df`, `teardown.log_path` null (`out/S9Lesson/c2/`).
  `<measured values: SCORECARD §Round-47 measured results>`
- Routed items: r46-D1 and r46-D2 are carried by C1 (deleted counts equal numstat;
  window-maximum restoration); r46-D5 and r45-D3 are carried by C2 (no dead log
  pointer; provenance and replay); r46-D3 is carried by Mistakes row 1 (sufficiency
  family with a fail-capable check); r46-D4 (hexrun-census `unknown=21`) is
  `<closed or ledgered by: …>`; r46-D6 is operator/aggregator, not acted on.
  `<deferred items and their stated reasons: …>`

## Gate

Rows opened this round (`mined` for the network and documentation rows, `own-work`
for the receipts), opened 2026-10-26; registry lines `corpus/SOURCES.md`
`<S488>`–`<S491>`, assigned at integration. At the build tip no b11909 row exists
(`git -C <clone> grep -c b11909 3a09a1d9 -- corpus/SOURCES.md` → no match, and the
C2 counter's `newrow` leg is 0), so the rows below are the material the integration
commit registers, not rows already in the registry.

- **`<S488>`** — https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz
  and its asset record https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11909,
  accessed 2026-10-26 (copy `.ufo/waves/round-47/c2/release-b11909.json`, committed
  at the freeze `bbcc6dc2`). Located quote (release JSON, `target_commitish` field):
  `caa8191df159f764fb0160e3d2fc6be008948aee`; `published_at`
  `2026-10-26T21:00:58Z`, `prerelease` true; asset `llama-b11909-bin-ubuntu-x64.tar.gz`
  22475032 bytes, `digest` `sha256:bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`.
  Downloaded-tarball record `.ufo/waves/round-47/c2/live/install.txt`: 22475032 bytes,
  the same sha256, extracted `llama-server` sha256
  `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`, `--version`
  `version: 0.7.0-dev (build 11909, commit caa8191df)`. Independent of install.txt,
  this seat's C2 counter run re-downloaded and digest-checked the archive into scratch
  (`replay=1`, `out/S9Lesson/c2-counter.out`).
- **`<S489>`** — own-work, `python3 tools/kama-llamacpp-live.py` against the `<S488>`
  binary, receipts `.ufo/waves/round-47/c2/live/receipt-1.json` … `-3.json` (copied
  to `out/S9Lesson/c2/`), accessed 2026-10-26. Located quote (`receipt-1.json`,
  `captures.health.body`): `{"status":"ok"}`. All three: schema `kama-llamacpp-live/v4`,
  outcome pass, 11/11 checks evaluated and passed, `captures.props.fields.build_info`
  `b11909-caa8191df`, `teardown.log_path` null, provenance server
  `asset_url`/`asset_sha256`/`member` equal to `<S488>`'s asset and
  `llama-b11909/llama-server`, provenance model URL
  `https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf`
  with `sha256` `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
  The receipts were committed at the build `3a09a1d9`, before the measured commit.
- **`<S490>`** — model artifact, own-work and docs: the same model URL, 1185376 bytes,
  sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; fetch
  record `.ufo/waves/round-46/c1/live/model-fetch.txt` (url, path, size, sha256,
  `curl_exit 0`), re-acquired and digest-checked by the round-47 replay leg. This is
  the locator row r45-D3 asked for; the b11909 receipts' `provenance.model` is the
  in-receipt duplicate.
- **`<S491>`** — git-diff(1), `--numstat`, https://git-scm.com/docs/git-diff, accessed
  2026-10-26 (page last updated for Git 2.56.0, 2026-09-28). Located quotes: "The
  `--numstat` option gives the diffstat(1) information but is designed for easier
  machine consumption", and the field list "1. the number of added lines; … 3. the
  number of deleted lines"; and, in the same option block, "For binary files, outputs
  two `-` instead of saying `0` `0`." This is the definition of the outside count C1's
  `deleted` field must equal; it is not evidence that the tool implements it.

Decisions:

- **Admit** `<S488>`, scoped to release→commit identity and the Linux x64 CPU archive:
  release record, downloaded tarball and extracted binary are three checks of one
  artifact, and the digest was re-verified from a fresh download this round.
- **Admit** `<S489>`, scoped to three sampled instants on one model: 11/11 checks on
  each receipt, one build, one alias. Three samples are an observation, not a
  property of b11909.
- **Admit** `<S490>`, scoped to model identity (URL, size, sha256). The round-46
  fetch record and the round-47 replay agree on the digest; neither is a model-quality
  claim.
- **Admit** `<S491>`, scoped to the definition of the count (`--numstat` output
  format, binary files as `-`). It says what git prints, not what the lane's hunk
  reader does with it; that is C1's lane and fixture legs.
- **Reject** treating a receipt's provenance URL as *verified at record time*. The
  block is a locator plus an expected digest: the live tool records what it was told,
  and a receipt can be written with any URL. At the freeze the replay leg had not run
  (`controls/base.c2.out`: `replay=0`), and round-47's own attack shows the gap is
  real — seat K2Cheat met the frozen C2 counter by copying host-cache bytes with no
  fetch and with the network dead (`K2Cheat.md:29`), and by fabricating a rerun with
  0-byte placeholders (`K2Cheat.md:39`). Only the `replay` leg (fresh home, both
  digests verified after download) is verification; the row's wording must say
  "locator" and name the replay receipt as the check.
- **Reject** counting b11909 as registered before the SOURCES row lands. `newrow=0`
  at `3a09a1d9` (`out/S9Lesson/c2-counter.out`, exit 1; `git grep b11909
  3a09a1d9 -- corpus/SOURCES.md` → no match). `<S488>` is admitted from the
  integration commit that adds the row, not from the release record alone.
- **Reject** citing `install.txt`'s host path `/home/vgpnk/.local/opt/llama-b11909/llama-server`
  as the artifact locator in a Gate row. The locator is the asset URL plus the archive
  member; the host path is a one-host observation and will not resolve elsewhere —
  the same class as the dead-pointer Mistakes row below.
- **Reject** re-asserting `teardown.term_wait_ms` as a b11909 property.
  `<the three b11909 receipts' values, and the reason three samples are not a property>`
  (round-46 filed the same reject for b11906: `corpus/lessons/round-46.md` Gate, last bullet).
- status/recheck/used-by changes to existing rows: `<none | list>`.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| sufficiency-blind — a frozen counter's `met=True` says a fact was produced, not that the claim is sufficient (carried in the closures of rounds 41–45; round-46 D3) | "Counters prove facts, not sufficiency" was routed as a carried item in r41 #1, r42 #2 (`corpus/lessons/round-42-verifier-spotcheck.md:108`), r43 #6 (`round-43-verifier-spotcheck.md:110`), r44 #5 (`round-44-verifier-spotcheck.md:112`) and r45 #4 (`round-45-verifier-spotcheck.md:149`), and never became a `## Mistakes` row (`corpus/lessons/round-46.md:87`, sweep finding 1; `grep -c sufficiency .ufo/waves/round-46/preregistration.json` → 0). The lane pays for it every round and did again this round: the frozen C1 counter reads `met=True` for a fixture-recognizing playback tool that derives nothing from the lane's history (`.ufo/waves/round-47/w1/out/K1Cheat.md:37`, verdict `:47`) and for a print-only selftest stub (same file `:57`); the frozen C2 counter reads `met=True` for a replay tool that copies pre-seeded host assets with no fetch and the network dead (`K2Cheat.md:29`), for a hash-only fabrication with 0-byte placeholders (`:39`), and for a forged `started_utc` (`:45`). Both counters are frozen; these are findings, not in-place edits. | none through round 46 — the round-46 sweep is a pointer, not a row; this round the attacks are K1Cheat and K2Cheat, and the trend check is seat X9Tally's | Trend check (considerthese/2026-10-26.md proposal 3): `python3 .ufo/waves/round-47/w1/out/X9Tally/shortcut-tally.py --check <N>` must exit 1 when the latest round's count of shortcuts that met a frozen counter exceeds `<N>` or the round data is unreadable, and 0 otherwise; the tallied instance set is K1Cheat `K1Cheat.md:37,57` and K2Cheat `K2Cheat.md:29,39,45`, so any round containing one of them must make `--check 0` exit 1. Shown able to fail: with the tally tool absent at draft time, the row check shipped beside this draft was run on two lessons — `python3 out/S9Lesson/check-sufficiency-row.py corpus/lessons/round-46.md` → `row=0 file=corpus/lessons/round-46.md command=0`, exit 1, and the same command on this file → `row=1 … command=1`, exit 0. `<integration: record the tally run (`--check 0` exit 1, `--check 99` exit 0) or state that the tally is deferred and why>` |
| measure-drift — a restoration measured against the audited tip falls when the tip's head is re-derived, with no new loss (round-46 closure D2; closed by C1) | v1 `restored_at_tip` for the `0718b6ab` SCORECARD event is 2416 at `0163fea2` and 2409 at `4340cf2f`, from the round-46 head re-anchor alone (`corpus/lessons/round-46-verifier-spotcheck.md:138`; commands and outputs in `out/S9Lesson/evidence-stability.txt`). v2's window maximum is 2420 at both tips and at `3a09a1d9`; `status` stays `partial` for the one superseded depth row. The missing line is the superseded head row, not a lost body line. | the round-46 outside closure (§2 C2 observation, routed D2); the fix is carried by this round's C1 | Define restoration against the event's own window: `restored_max = max held(x)` over the event commit and every later rev-list commit, with `restored_best`/`restored_by` (`tools/append-only-audit.py:29-34,207-219`). The check is the C1 counter's `stable` leg — at base and tip, every base event appears with equal `deleted` and `restored_max(tip) >= restored_max(base)` (`tools/round47-append-audit-v2-check.py:89-91`). Shown able to fail: the v1 measure at the two tips gives 2409 < 2416, so the stable predicate rejects it; the v2 measure gives 2420 == 2420 and passes (`out/S9Lesson/evidence-stability.txt`). |
| dead-pointer — a receipt records a path into deleted seat scratch, so a later reader cannot resolve what it cites (round-46 closure D5, round-45 D3; closed by C2) | the three round-46 v3 receipts record `teardown.log_path` as `/fast/scratch/hyaku/kama-r46/X1Live/kama-llamacpp-live-*.log`; the directory does not exist (`out/S9Lesson/evidence-d5.txt`: `exists= False` for all three). The three round-47 v4 receipts record `null`. The counter's rule is at `tools/round47-live-replay-audit.py:172-178`: null, or a repo-relative path (no `..`) that exists at the tip. | the round-46 outside closure (`round-46-verifier-spotcheck.md:141`, routed D5); r45-D3 routed the same class to C2 | Schema v4: `teardown.log_path` is null or a committed relative path; the three log tail lines stay inline in `teardown.log_lines`. Shown able to fail: calling the counter's own `check_receipt` on receipt-1 at `3a09a1d9` returns `True` unmutated, and `False` with `teardown.log_path '/fast/scratch/hyaku/kama-r46/X1Live/kama-llamacpp-live-j7s5brv0.log' is not a committed repo-relative path` after that one field is set to the round-46 value (`out/S9Lesson/evidence-d5.txt`). |

## Wave

`kama-r47-w1`, one v2 wave (attack and frontier together), `<seat count>` seats
(`.ufo/waves/round-47/w1/dispatch.json` counts `spawn 65`), `<WAVE-DONE status>`;
`python3 tools/seat-yield.py .ufo/waves/round-47/w1 --expect-reports <N>` →
`<seats=… reports=… missing=…>`, exit `<n>`. `<dead-seat list or none>`.

Every claim was attacked: C1 by `<seats: K1Cheat, K1Hist, K1Design, R1Decl, K1Regions,
M1Ctr, M1Tool, V1Tool, V1Ctr, X1Fixture, X1Stable, L1Lowthr, R1Rerun>`; C2 by
`<seats: K2Cheat, K2Design, Sen2Replay, V2Replay, V2Live, M2Ctr, M2Replay, X2Replica,
X2Offline, X2Receipts, L2Concurrent, K2Fresh, R2Rerun, U2Server, U2Pins, Simp2Tool>`.
The attacks found counter weaknesses the frozen counters cannot fix this round; the
instance set for the sufficiency row is K1Cheat `:37,57` and K2Cheat `:29,39,45`, and
`<the remaining findings and their counters>` belong in SCORECARD §Round-47
"What `met=True` does not show". `<severity, and whether any claim is falsified>`.
