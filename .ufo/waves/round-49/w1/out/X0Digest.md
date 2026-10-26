# X0Digest — round-49 digest and object-id census (kama r49, seat X0Digest)

**Verdict:** the round's four headline values all classify today, but only when integration writes them full-length and the measured clone keeps lane history: in house style (8-char ids) all three object ids are invisible to both censuses (measured: fixture byte-for-byte identical to the baseline counts), and in a history-rewritten or shallow clone exactly the three lane ids turn `unknown` (+3, measured); three drafted upstream rows rescue exactly those three and nothing else — the pre-existing `hexrun-census` exit 1 at the build tip is not round-49's and must not be the integration gate.

Lane read-only at the build commit `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (base
`438127bc01ff3b99f98468549d58046f932490ef`, freeze `36d5ed2681111b68c180f8ab1646d8dc9beaedee`),
through one `git clone --shared`; four fixture repos in my own scratch, all reported
`TOPLEVEL_OK` from `git -C <dir> rev-parse --show-toplevel` before their first commit.
Commands: `receipts/commands.md`; every scan line and exit code: `receipts/scan-matrix.tsv`.

## 1. Baseline at the build tip

| tool | line | exit |
|---|---|---|
| `tools/digest-ledger.py scan --repo <clone> --rev 74558c71…` | `tokens=127 blob=111 external_ok=9 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` | 0 |
| `tools/hexrun-census.py scan --repo <clone> --rev 74558c71…` | `tokens=1833 distinct=296 lane_oid=190 md5_blob=1 upstream_ok=92 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=2` | **1** |

`receipts/base-digest.out`, `receipts/base-hexrun.out`, `receipts/base-hexrun.unknown.txt`.

The two pre-existing unknowns are `15710a2a8286bf12d55d943f17028178fe8d421a` and
`dcc079e7e56d3312ec70e0bd5b3c7f885b1242e8`, cited at
`corpus/lessons/round-48-verifier-spotcheck.md:21` as the fleet commits that filed the
round-48 report; both are fleet-repository objects, so the lane clone cannot name them
and no ledger row covers them. **The census that round 49 inherits already exits 1.**
Any integration check written as "hexrun-census exits 0" is therefore vacuous in both
directions: it fails before round 49 lands, and a draft paragraph that adds nothing
(the house-style form, §4) cannot change it.

## 2. The four values as they stand, and their class

`receipts/token-citations-at-build-tip.txt` (documents = `.md`/`.tsv` outside `.ufo/`,
which is what both censuses read):

| value | cited at the build tip in | class at the build tip |
|---|---|---|
| freeze `36d5ed2681111b68c180f8ab1646d8dc9beaedee` | no document (only `.ufo/waves/round-49/preregistration.json` and wave artifacts, which neither census reads) | not a token yet; would be `lane_oid` |
| build `74558c71c38ceaeace15fd4cf8aa9d84977584b1` | no document (only `.ufo` artifacts) | not a token yet; would be `lane_oid` |
| README commit `caa8191df159f764fb0160e3d2fc6be008948aee` | `corpus/SOURCES.md:247` (row S494, once in the URL and once as "at b11909") and `:241` (S488), `corpus/README.md:860`, `corpus/lessons/round-47.md:20`, `corpus/lessons/round-47-verifier-spotcheck.md:77`, `registry/hexrun-ledger.tsv:105`; 6 occurrences | `upstream_ok` — row `registry/hexrun-ledger.tsv:105` (repo `ggml-org/llama.cpp`) whose evidence `.ufo/waves/round-47/hexrun-evidence/caa8191df….txt` is a blob at the revision and contains both the token and the repo text |
| server digest `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` | `LOG.md:2323`, `corpus/SOURCES.md:241` (row S488), `registry/digest-ledger.tsv:16` | `external` → `external_ok`: the row's path `/home/vgpnk/.local/opt/llama-b11909/llama-server` re-hashes to the digest (`x0-digest-rehash-r49.txt`), and the counter's own constant is the same value (`tools/round49-replay-witness-audit.py:97`) |
| base `438127bc01ff3b99f98468549d58046f932490ef` | four `.ufo` artifacts only | not a token yet; would be `lane_oid` |

So the integration paragraph is the first document that puts the freeze, build and base
into either census, and `caa8191d`/`35ac50fb` are already covered by existing rows.

## 3. The draft paragraph, three measured shapes

Fixtures: `fx-full` (`4798904300fe911363015ae323d630a293d966c6`), `fx-abbrev`
(`567fbe1ae441f0858c1a562bcaaaafc344b954b5`), `fx-root-base`
(`1dfcde156b286449a1002db14d353183128c8c75`), `fx-root`
(`68cbf00e7f7614ab6c228b32d75b42faf8589d1f`), `fx-rows`
(`788c2b35a371d1920a6fdf5384d18abea86207cf`), `fx-root` + rows
(`9bbeb3764b198893743f02fdb7bf523795eef65a`).

| shape | digest-ledger | hexrun-census |
|---|---|---|
| baseline (no paragraph) | 127 tokens, `unknown=0`, exit 0 | 1833/296, `lane_oid=190`, `unknown=2`, exit 1 |
| **A** full-length paragraph, history kept (`fx-full`) | unchanged, exit 0 | `tokens=1841 distinct=299 lane_oid=193 upstream_ok=92 unknown=2`, exit 1 |
| **B** house-style paragraph, 8-char ids (`fx-abbrev`) | unchanged, exit 0 | `tokens=1833 distinct=296 lane_oid=190 unknown=2` — **identical to baseline**, exit 1 |
| **C** full-length paragraph, lane history absent (`fx-root`) | `blob=103` (from 111), `unknown=8`, exit 1 | `lane_oid=26`, `unknown=168`, exit 1 |
| **C′** same without the paragraph (`fx-root-base`) | — | `lane_oid=26`, `unknown=165`, exit 1 |
| **D** paragraph + the three draft rows (`fx-rows`) | unchanged, `ledger_bad=0`, exit 0 | `lane_oid=193`, `upstream_ok=92`, `unknown=2`, `ledger_bad=0`, exit 1 |
| **D′** same rows in the history-absent shape (`fx-root` 2nd commit) | `unknown=8`, exit 1 | `upstream_ok=96`, `unknown=165`, `ledger_bad=0`, exit 1 |

Detail lines for A (`receipts/fx-full.ids.txt`):

```
detail: 36d5ed2681111b68c180f8ab1646d8dc9beaedee len=40 occurrences=2 class=lane_oid
detail: 438127bc01ff3b99f98468549d58046f932490ef len=40 occurrences=2 class=lane_oid
detail: 74558c71c38ceaeace15fd4cf8aa9d84977584b1 len=40 occurrences=2 class=lane_oid
detail: caa8191df159f764fb0160e3d2fc6be008948aee len=40 occurrences=8 class=upstream_ok
```

and for D′ (`receipts/fx-root-rows.ids.txt`):

```
detail: 36d5ed2681111b68c180f8ab1646d8dc9beaedee len=40 occurrences=2 class=upstream_ok
detail: 438127bc01ff3b99f98468549d58046f932490ef len=40 occurrences=2 class=upstream_ok
detail: 74558c71c38ceaeace15fd4cf8aa9d84977584b1 len=40 occurrences=2 class=upstream_ok
```

Marginal arithmetic, exactly: A − baseline = `distinct 296→299`, `lane_oid 190→193`,
`tokens +8` (the three new ids twice each, plus `caa8191d` twice; `caa8191d` was already
distinct, and `35ac50fb` is not a hexrun token because `hexrun` excludes length 64 —
`tools/hexrun-census.py:71`). B − baseline = 0 in every cell. C − C′ = `unknown 165→168`,
the three lane ids and nothing else.

## 4. Which of these can become unknown

1. **Normal integration (a commit on top of the build, cloned with full history): none.**
   All three lane ids are ancestors of the build, which is an ancestor of the lane's
   `master` (`git merge-base --is-ancestor` exit 0 for each; the earlier freeze ids the
   LOG cites — `12284ba3`, `bbcc6dc2` — are still ancestors too, so the lane's jj backend
   is not dropping freeze commits). `hexrun`'s `lane_oid` leg is object-existence based
   (`git cat-file --batch-check`, `tools/hexrun-census.py:186-193`, consulted first at
   `:258`), not reachability, so any clone that carries the objects classifies them.
2. **History loss (squash/rewrite at integration, `--depth`/shallow clone, a fresh
   `git init` + tree copy): the freeze, build and base become `unknown`.** Measured as
   exactly +3 (`fx-root` vs `fx-root-base`). That is the only way the round's new ids
   become unknown, and it is not a round-49-specific failure: the same fixture also turns
   165 other lane ids unknown (`lane_oid 190→26`) and 8 digest-ledger tokens unknown
   (`blob 111→103`: cited digests that are SHA-256 of blobs reachable only in lane
   history — `digest-ledger` hashes `rev-list --objects <rev>`, `tools/digest-ledger.py:239`,
   so it classifies against the whole history, not the tip tree; e.g. `LOG.md:122`'s
   `493afecbd6dd85df0f08f4541ecd340b03dc5df797a73bf8744cfd94edebab5a`).
3. **House style: none becomes unknown, because none becomes a token.** `fx-abbrev` is
   indistinguishable from the baseline on both tools. An 8-character run is below
   `hexrun`'s 32-character floor (`tools/hexrun-census.py:71`) and is not 64 characters,
   so `digest-ledger` never sees it either (`tools/digest-ledger.py:67`; its docstring
   lists the limit at `:38-40`). The lane already documents the round-49 witness pin in
   exactly this invisible form three times — `corpus/README.md:1009` (`35ac50fb…d7ff0`),
   `corpus/knowledge/llamacpp-loading-lifecycle.md:440` (`35ac50fb…7ff0`),
   `corpus/lessons/round-47.md:20` (`35ac50fb…7ff0`) — and one full-length citation
   (`LOG.md:2323`) carries the classification. Minimal demonstration
   (`receipts/mini-abbrev.digest.out`, `receipts/mini-full.digest.out`): an 8-character
   citation of the pin gives `tokens=0 … unknown=0` exit 0; the full digest in the same
   tree gives `tokens=1 external_ok=1` exit 0. The first is silent, not correct.

Quantified blindness in the documents that will carry the round-49 entry: backticked
`[0-9a-f]{7,31}` runs that resolve to a lane commit number **302**
(`SCORECARD.md` 137, `LOG.md` 111, `SKILL.md` 28, `corpus/QUALITY.md` 21,
`corpus/SOURCES.md` 5; resolved with `git rev-parse --verify --quiet <id>^{commit}`).
House style for a commit id is therefore, for both censuses, the same as not writing it.

## 5. Draft ledger rows and their measured effect

- `hexrun-ledger-rows.draft.tsv` — three `upstream` rows for the freeze, build and base
  against `VeigaPunk/kama-shokunin`, each with an evidence file under
  `hexrun-evidence/` that carries the token, the repo text, `git log -1`, `git cat-file -t`
  and `gh api repos/VeigaPunk/kama-shokunin/commits/<sha>` (200, same sha; 3 API reads,
  `rate_limit.remaining=4982`). Verified two ways in fixtures: **inert** in the
  history-kept shape (D keeps `upstream_ok=92` and `lane_oid=193`, `ledger_bad=0`) and
  **effective** in the history-absent shape (D′: `unknown 168→165`, `upstream_ok 93→96`,
  `ledger_bad=0`). They do not touch the other 165 unknowns and are not a substitute for
  keeping history.
  Caveat worth keeping: `resolve()` returns `lane_oid` before consulting the ledger
  (`tools/hexrun-census.py:257-259`), so in a normal measurement a typo in one of these
  rows' evidence path would never surface — the fx-root fixture is what exercises them.
- `digest-ledger-row-replacement.diff` — one-line replacement of the existing
  `35ac50fb…` row so its subject names it as the round-49 C1 witness pin and its note
  points at this round's re-hash. No new digest row is needed: the digest has one row,
  its path resolves, and its hash matches (`ledger_bad=0` in `fx-rows`/`fx-rows` digest
  receipt, `external_ok=9` unchanged).
- Nothing is drafted for `caa8191d`: the round-47 row and its committed evidence file
  already classify it `upstream_ok` at the build tip (case in point: 6 occurrences, no
  detail line, so it is not unknown).

Integration paragraphs (drop-in text, fixture identity, one full-length per value):
`draft-scorecard-full.md` (appends at `SCORECARD.md:2809` of the fixture, i.e. after the
build's 2807 lines) and `draft-log-full.md` (appends at `LOG.md:2331`). The house-style
twins `draft-scorecard-abbrev.md` / `draft-log-abbrev.md` are the measured-negative
control, not a recommendation.

## 6. Risks for integration

1. Do not gate on `hexrun-census` exit 0 — it is 1 at the build tip for two round-48
   fleet-commit ids. Gate on the counter matrix: whatever else the scribes' text adds,
   the full-length paragraph must move `distinct` by +3 and `lane_oid` by +3 over the
   baseline and must leave `unknown` at its baseline count (2 at the build tip); measured
   at the fixture: `tokens=1841 distinct=299 lane_oid=193 upstream_ok=92 unknown=2
   ledger_bad=0`. If the paragraph is house style, both tools print exactly the baseline
   numbers (measured: `tokens=1833 distinct=296 lane_oid=190 unknown=2`), i.e. nothing
   was checked — that is the signature to look for.
2. Do not add a second row for any token: two rows for one token are `ledger_bad`
   (`tools/hexrun-census.py:265-266`), and `35ac50fb` already has a row — replace, do not append.
3. If those two round-48 unknowns are going to be ledgered, do it in a commit separate
   from the round-49 paragraph so the token counts move by a known amount.
4. `digest-ledger`'s `external_absent` is not an error (`tools/digest-ledger.py:384`), so
   the `35ac50fb` row stays green even if `/home/vgpnk/.local/opt/llama-b11909/` is deleted
   — the pin would then be evidenced only by the counter's own constant and receipts.
   Not a defect for round 49 (the witness hashes `/proc/<pid>/exe` itself), but the row is
   not a liveness check on the binary.
5. My draft paragraph names values only; the measured-results lines for §Round-49 must
   still come from the L1's counter receipts.

## 7. What this seat did not do

No lane file edited (proposals are files and a diff in this directory), no commit outside
my own fixture repos, no `git add/commit/checkout/stash/reset` in the lane, no tool
install or upgrade, no pacman, no llama-server started (the two live ones belong to peers
X1Offline and U0Consumers), nothing written at the fleet root or in a sibling lane. The
two round-49 counters were not run: C1/C2 measurement is the L1's, and this seat's claim
is the census side only.

## 8. Files

| file | what |
|---|---|
| `draft-scorecard-full.md`, `draft-log-full.md` | drop-in round-49 paragraphs, full-length ids (measured shape A) |
| `draft-scorecard-abbrev.md`, `draft-log-abbrev.md` | house-style twins (measured shape B, negative control) |
| `hexrun-ledger-rows.draft.tsv` | three `upstream` rows to append (header line included for reading; append lines 2-4) |
| `hexrun-evidence/{36d5ed26…,74558c71…,438127bc…}.txt` | committed-evidence drafts, command + output |
| `digest-ledger-row-replacement.diff` | one-row replacement for the `35ac50fb…` digest row |
| `x0-digest-rehash-r49.txt` | pin re-hash: `sha256sum`, `SERVER_SHA` line, size/mode |
| `receipts/scan-matrix.tsv` | 13 scans: fixture, rev, tool, exit, summary |
| `receipts/*.out`, `receipts/*.txt` | raw scan output, detail slices, citation counts, `commands.md` |
