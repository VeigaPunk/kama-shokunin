**Verdict: two registry-row drafts delivered and machine-validated — `S486` (llama.cpp release b11906 identity, docs/A) and `S487` (kama live lifecycle receipts at b11906, own-work/A) pass the frozen census on a scratch copy of `corpus/SOURCES.md` (validate exit 0, `file ok`, findings identical to the lane baseline; census rows 226 -> 228), and `S486` satisfies the frozen C1 counter's newrow leg (`newrow=1`).**

# S1Row — registry rows this round may add

Seat: leaf, lane kama, round 46. Ids are proposals (`S4NN` is the L1's to assign); the validated copy uses `S486`/`S487`
because census rule E02 requires digits.

## Behavior

- Drafted **row (a)**: llama.cpp release b11906 — tag, commit, asset digest, extracted binaries, `--version`; kind `docs`,
  tier `A`, scope *release identity only*; modelled on S482/S484. It carries the full commit
  `4d71b42fd87db24b8b7c808c151b713aa4459cfd` and the literal `b11906` on one line, which is exactly what the frozen C1
  counter's newrow leg requires (`tools/round46-release-recheck-audit.py:78-80`, `:355-357`).
- Drafted **row (b)**: kama live lifecycle receipts at b11906 — own-work, tier `A`, sampled instants, one model; modelled
  on S485. Anchored on `.ufo/waves/round-46/c1/live/receipt-1..3.json`; the seat item asked for placeholders for the
  server sha256, and a `{{SERVER_SHA256}}` placeholder variant is included, **but** the live run had already landed when
  this seat read the receipts, so the primary row is filled with the observed value `c949950ee76bf84e0dc8f537a98a2c702169f09b5a061c27c87edff753fac3ff`
  and the receipts are pinned by sha256.
- Located quotes: (a) `"target_commitish":"4d71b42fd87db24b8b7c808c151b713aa4459cfd"` at top level of
  `.ufo/waves/round-46/c1/release-b11906.json` (2 words); (b) `{"status":"ok"}` at `captures.health.body` of
  `receipt-1.json` (1 word), plus `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` at
  `captures.loading_503.body` (7 tokens). All under the 25-word bound.
- Listed the census rules each row must pass with the enforcing line in the frozen script (E01-E12, W01/W03/W04), and ran
  them.

## Gates (all run by this seat; nothing rerun for decoration)

| command | exit | result |
|---|---|---|
| `gh api repos/ggml-org/llama.cpp/releases/tags/b11906` (one call) | 0 | 69164 bytes, sha256 `b9041d4af30892fea64767acdcc3de5b9452a2d01f0b0e6fedef6c18976da6d7`, byte-identical to the lane copy `.ufo/waves/round-46/c1/release-b11906.json`; `tag_name b11906`, `target_commitish 4d71b42f…`, `published_at 2026-10-26T19:45:36Z`, `prerelease true`, asset `llama-b11906-bin-ubuntu-x64.tar.gz` 22478121 bytes `sha256:064ade62…eef3` (matches the seat item) |
| `git ls-remote --tags https://github.com/ggml-org/llama.cpp.git refs/tags/b11906 refs/tags/b11889` | 0 | `4d71b42fd87db24b8b7c808c151b713aa4459cfd refs/tags/b11906`, `d854d98bae598388ecea1ed84396587e5edc326d refs/tags/b11889` |
| `git -C /fast/scratch/hyaku/kama-r46/L1/llama.git rev-list --count d854d98b..4d71b42f` | 0 | `17` (confirms "17 commits after b11889") |
| `bash scripts/sources-census.sh validate --file $S/chk/corpus/SOURCES.md --today 2026-10-26` | 0 | `file ok`; 93 `W04` + 1 `W01`, byte-identical to the lane baseline (diff of the two normalised outputs: `IDENTICAL-FINDINGS`) |
| `bash scripts/sources-census.sh census --file $S/chk/corpus/SOURCES.md` | 0 | `rows 228` vs `rows 226` on the lane file; every other counter unchanged |
| control: same rows appended after line 524 instead of inside `## Registry` | 1 | `E12 S486 row outside Registry section`, `E12 S487 row outside Registry section` |
| frozen counter newrow leg, evaluated with the counter's own `ROW`/`RELEASE`/`RELEASE_COMMIT` over base `0163fea2` and the scratch tip | n/a | `newrow 1 ids ['S486']` |

Cell-level invariants asserted at build time: 11 cells (12 pipes) per row, no `|` inside any cell, ids absent at tip.

Live-receipt facts behind row (b), re-derived by `derive-row-facts.py` (not retyped by hand): all three receipts
`outcome=pass`, `11 of 11` checks passed, windows `19:57:39.317Z-19:57:39.905Z`, ports 33179/46073/44923,
`build_info b11906-4d71b42fd`, alias `kama-r46-live`, `/health` body `{"status":"ok"}`, `/metrics` 501, one loading 503
body per run with `envelope_exact` true, teardown `returncode 0`, `sigkill_sent false`, `term_wait_ms 3`.

## Touched surfaces

- Wrote only inside `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/` (deliverables) and my
  scratch `/fast/scratch/hyaku/kama-r46/S1Row/` (now removed). The report at
  `.ufo/waves/round-46/w1/out/S1Row.md`.
- Read-only elsewhere: lane `corpus/SOURCES.md`, `corpus/knowledge/llamacpp-loading-lifecycle.md`,
  `.ufo/waves/round-46/{preregistration.json,c1/*,w1/spec.json,controls/}`, `tools/round46-release-recheck-audit.py`,
  fleet `scripts/sources-census.sh`, the L1 upstream clone (show/rev-list/cat-file only). No lane file edited, no git or
  jj mutation anywhere; `git -C lane status --porcelain` shows only the expected untracked `.ufo/waves/round-46/` wave
  paths (count 4), nothing written by this seat outside the out directory.

## Out of scope (deliberately not done)

- The `## Round-46 release re-verification` section heading (C1 integration text) and the ledger
  `registry/release-recheck-b11906.tsv`: `section=0` on the scratch copy, as expected — that leg belongs to the L1.
- `corpus/lessons/round-46.md` in either used-by cell: the file does not exist yet, so including it would fail E11 today.
- Any verdict on population rows, any change to the counters/preregistration/controls, any live run (I read X1Live's
  receipts, I did not rerun them).

## Findings

1. **F1 (script defect, `scripts/sources-census.sh:497-503` + `:567`).** `validate --file` sets the lane dir to
   `realpath(dirname(file)/..)`, so the seat item's literal instruction ("on a scratch copy of `SOURCES.md`") yields ~200
   false `E11 missing used-by …` lines and exit 1 for rows nobody touched. Reproduce: copy the file to any directory whose
   parent is not a lane root and run `validate --file`. Fix: add `--dir` (or default `dir` to the owning lane) so a copy can
   be validated without a mirrored tree; otherwise document the requirement. Worked around here with a symlink farm
   (`build-rows.py` reproduces it).
2. **F2 (usage hazard, `scripts/sources-census.sh:621`).** Rows appended at the end of `SOURCES.md` are rejected with
   `E12` (control above, exit 1). The registry insertion point must be after line 238 (`| S485 …`) and before `## Paths`;
   this is documented for the L1 in `rows.md` §1.
3. **F3 (evidence moved mid-wave, not a script defect).** `.ufo/waves/round-46/c1/live/install.txt` was rewritten at
   16:58:51 — after the 16:57:39 receipts — gaining `install_tree_sha256 89fbc389…`, `install_links_sha256 5cb9f486…` and
   a harness line, moving its sha256 from `15131698da32294918655b1f992b2365aff23ceac82bfe04a9c0647588534cec` to
   `dc65047e8fafdb367ad2f71edf3a07e62f7775ed4a28938b83a2826fda5d51d4`. A row pinning that file's hash would have gone
   stale within minutes; `S486` therefore cites its content (`--version` line, binary digests) and the release JSON's hash.
   Process fix: anchor rows on the content they depend on, and treat engine-side evidence files as mutable until
   integration.
4. **Note (not a defect).** The round-46 receipts show **one** loading-503 repeat per run, against S485's 24/8/16; row (b)
   states the observed count instead of carrying S485's numbers forward. If X1Live or a replica rewrites any receipt,
   `derive-row-facts.py` re-derives every cited value and the row must be rebuilt from its output.

## Artifact paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/rows.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/rows-validated.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/SOURCES-validated.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/build-rows.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/derive-row-facts.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/derive-facts.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/validate-scratch.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/validate-lane.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/census-scratch.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/control-tail-append.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/release-b11906.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row/ls-remote-b11906.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S1Row.md`

Tooling: none installed or upgraded (no pacman, no uv/npx). `gh` used for one API request only.
