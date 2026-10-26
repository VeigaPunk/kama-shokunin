## Frontier disposition — round 46

Re-verified this round (`registry/release-recheck-b11906.tsv`): the 91 `on-release` rows of
`corpus/SOURCES.md` pinned to a `ggml-org/llama.cpp` file at a commit (the round-44 population,
unchanged at base `0163fea2`) were re-checked at release b11906 =
`4d71b42fd87db24b8b7c808c151b713aa4459cfd`, 17 commits after b11889
(`git -C /fast/scratch/hyaku/kama-r46/L1/llama.git rev-list --count
d854d98bae598388ecea1ed84396587e5edc326d..4d71b42fd87db24b8b7c808c151b713aa4459cfd` →
`17`): unchanged-file 6, holds 82, holds-reworded 3, drifted 0, removed 0. 73 rows sit on
files byte-identical between the two releases (`git rev-parse <rev>:<path>` at b11889 and
b11906): 6 of them are the pin-equals-release rows S015, S059, S106, S128, S129, S131 and 67
carry their b11889 reading to the same bytes; the three `holds-reworded` rows are S037, S043
and S108 on the byte-identical `server.cpp` and keep their b11889 pin-only/release-only
witnesses. The 18 rows whose file changed are 17 on `tools/server/server-context.cpp` (S042,
S060, S109, S114–S125, S133, S138) and S479 on `tools/server/server-models.cpp`; every hunk
of the one commit that touches these files between the releases (c6fb3b5be, "mtmd: add
mtmd_helper_get_capabilities", net +3 lines, 6 hunks) lies outside every pinned range, so each anchored range is text-equal at
b11906 after the +3 shift and S479's ranges are unshifted — no row drifted, no row was
removed, and no used-by entry needs a flag. One note-level citation is stale wording, not a
claim: S125's b11889 note still quotes `chat_params.allow_audio` as the pre-refactor
expression; the b11906 row cites 1712/1401 and the statement stands. b11906 is registered as a
source opened this round (release identity row, S486 as drafted) and
`corpus/SOURCES.md` §Round-46 release re-verification carries the population, the release and
the machine-witness rule.

The same official binary was re-run on the unchanged stories260K fixture with the unchanged
harness (`tools/kama-llamacpp-live.py` sha256 `8c0dbb2b…`): three `kama-llamacpp-live/v3`
receipts, each 11/11 checks, `build_info b11906-4d71b42fd`, ready `/health` body exactly
`{"status":"ok"}`, every loading 503 the exact envelope, `/metrics` 501, one SIGTERM with
`returncode 0`, `sigkill_sent false` (row S487 as drafted; a second, install-independent
replication reports the same). So the lifecycle propositions S041, S046 and S055 assert hold
unchanged 17 commits later; S485's b11889 receipts stay the b11889 sample, and the b11906
receipts are a new sample of the same instrument at a new build, not a re-verification of
S485's bytes. The boundary is unchanged: these are unregistered loopback ports at sampled
instants, not registered-consumer health; no registered endpoint was sampled this round, and
their last admitted sample (2026-10-15: 3 rows, all `DEAD`) is not re-opened by it.

Still frontier:
- S013 (Ollama importing a model): the live page still teaches the row, but the cited
  revision contradicts it — `docs/import.md` is 404 at `6d02a43a` (the page became
  `docs/import.mdx` in that commit), so the row needs a re-pin, not a re-read; proposed pin
  `98acec40ae2b3ed361fc5117e5b2ae81a4bf5c18` (blob `8a8778ce`, equal to `main` at the sample).
- S022 and the unpinned vLLM stable pages S002–S004: all four teaches hold on today's live
  pages (footer dates still match the rows; S022's stable alias is now dated 2026-09-16 and
  adds Responses API and spec-decode acceptance sections without contradicting the row), but
  they remain frontier because the anchor is a floating `stable` alias and S022 is still
  `queued` with no used-by — no revision pin, no release trigger.
- The floating-series rows: 178 rows carry `on-release`; 91 are the llama.cpp population
  above, 5 are llama.cpp release/receipt rows (S026, S038, S482, S484, S485) and 82 cite
  other sources — 66 documentation pages, mostly anchored to a floating `stable`, `latest`,
  `main` or version-less address or a dated page footer (the Python 3.14, git-scm, man7, jj,
  pytest, llm-d and Ollama/vLLM/SGLang doc series), 3 spec rows (S014, S019, S058), 9
  code-file rows pinned to tags or commits outside llama.cpp, and the lane's own instrument
  rows; 7 of the 82 are rejected and 5 queued. They change on a docs deploy or a tag outside
  the llama.cpp feed, not on a llama.cpp release, so only a live page read dates them — the
  round-46 read holds S002–S004 and S022. The two `ggml-org/ggml` spec rows S014 and S058 were
  re-verified at their pins in round 45.
- Rows that cite llama.cpp but fall outside the population rule (the rule selects exactly 91;
  the llama.cpp-citing rows outside it are exactly 10): S026 (PR #18001, rejected) and S028 (issue #4746, rejected) are untouched
  by 17 commits — `git grep 'v1/metrics' 4d71b42f` still exits 1; S038, S482 and S484 are
  release-asset identity rows and b11906 says nothing about the b11755/b11889 bytes they
  name; S041, S046, S055 and S485 are historical receipts, now backed by the b11906 run
  rather than re-verified by it; S477's tag-inventory figure is stale — it records the highest
  `bN` tag as b11887 and 115 tags above b11755 at 2026-10-25T20:03Z, while the b11906 clone
  re-derives 130 and `git ls-remote --tags` at 2026-10-26T19:57:59Z lists b11907 as the
  highest (7,461 `bN` tags; 1 above b11906), and its 30d recheck is not due until 2026-11-24.
  The release identity the population assumes is a counter constant, not a re-derived fact
  (`RELEASE_COMMIT` is never checked against `git rev-parse b11906^{commit}`), so a
  tag-versus-constant guard is the next counter's work; today they agree.
- Next release trigger: the next `bN` tag above b11906. b11907 =
  `4b851fbee8867136a0c561c8a3521f2fe7d53252` was already tagged at the sample, but
  `releases/tags/b11907` answered 404 — a tag runs ahead of its release by hours, and an
  asset-digest row such as S038/S484 cannot cite it until the release lands. The lane's own
  pin is still b11755 (`registry/engine-pins.tsv`), which `tools/pin-watch.py check` reports as
  `engine=llama.cpp pin=b11755 newest=b11907 newer=131 status=behind` (exit 1), so the
  on-release trigger has been live for many builds. llama.cpp also publishes a semver stream:
  `releases/latest` returns v0.7.0 = commit `620d2225` = the b11669 commit, 86 commits behind
  b11755 and 237 behind b11906, and every `bN` release is a prerelease, so `releases/latest`
  is not a freshness oracle; v0.8.0 (a ~10-day milestone, none tagged at the sample) is a
  coarse second axis, never a replacement for the `bN` row.
- K05 (declared versus served context capacity): still no authorised registered-endpoint
  sample; this round's run is an unregistered fixture at `--ctx 256`, which the
  context-capacity rows' scope already excludes.
- Round-45 D1 (KQ65 hand-read sample for a future claim-outcome reader): the hand-read sample
  control is being produced this round (hand labels on both sides, byte-verified against each
  cited revision) and no reader is frozen, so the deferred item stays open.

Append-only self-description is now audited, not assumed: `tools/append-only-audit.py` (round-46
C2, capability table row `append-only-audit`) sets the five files the lane treats as
append-only (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md)
against its git history and exits 1 on a partial or unrestored mass deletion. At
`4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050` it reports `commits=294 events=5 restored=3
partial=2 unrestored=0` (exit 1): 0718b6ab truncated LOG.md, corpus/QUALITY.md and
corpus/README.md and 82b5e9d3 restored them byte-exactly; the two SCORECARD events are the
head re-derivations the file itself documents (`SCORECARD.md:6`: the head sections are
re-derived from the tree by `tools/round42-selfdesc-reconcile.py`) — 0718b6ab deleted 2417
lines and 2416 are back at the audit revision, dd9f5dc6 deleted 31 and 24 are back — so the
exit-1 is a signal to read, not a loss. What stays
frontier is the instrument's edge: the 20-line threshold hides smaller deletions by design and
the default five-file set is the tool's, not yet the lane's full declared contract.
