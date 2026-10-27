# X5Digest2 — round-50 digests and object ids: none of the six becomes unknown; one draft `upstream` row closes the census's pre-existing red

**Verdict:** Round 50's six new identifiers need **no new `digest-ledger` row** — the three page/excerpt digests classify `blob` (each is the sha256 of a committed text copy), the server digest is already `external` (`registry/digest-ledger.tsv:16`), and the freeze/build commits classify `lane_oid`; measured `unknown=0` for `digest-ledger` and `unknown=1 → 0` for `hexrun-census` once one `upstream` row (for a *round-49* fleet-commit citation, the only unexplained run at the build) lands with its gh-api evidence file.

## 1. What was asked and what the counters say

Item: append a draft SCORECARD/LOG paragraph naming the round's values (fixture identity), run both counters on the scratch clone, say which values become `unknown`, and draft ledger rows with evidence files.

Answer, measured (all receipts under `w1/out/X5Digest2/`):

| Value | Token shape | Class with the draft paragraph | Why |
|---|---|---|---|
| freeze `601c8889f33d1797c712feb753974c20cf891264` | 40-hex | `lane_oid` | `git cat-file -t` → `commit`; ancestor of the build (`git merge-base --is-ancestor`, exit 0) |
| build `97c864bead3ee4a2f629574e77263d33834ec98a` | 40-hex | `lane_oid` | `git cat-file -t` → `commit` |
| maps page sha256 `e7cdf0ff1c8d8d87e5c92e529a09270945ca3b7cafb8e823a7ca3d294f3c16a2` | 64-hex | `blob` | `git cat-file -p 97c864be…:.ufo/waves/round-50/c1/proc_pid_maps.5.txt \| sha256sum` → `e7cdf0ff…` |
| prctl page sha256 `906bbe5cc7e38c02a82bb60ff3b7e0d1cfb21089a1a24f00f045fb1b86edb1e4` | 64-hex | `blob` | same on `.ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt` → `906bbe5c…` |
| CommonMark 0.31.2 §4.5 excerpt sha256 `2dbd3f25b72d95ad2653bfcd9af704d7400a027ff0ed3e81e0391c3284c66d73` | 64-hex | `blob` | same on `.ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt` → `2dbd3f25…` |
| server digest `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` | 64-hex | `external` (row exists) | `registry/digest-ledger.tsv:16`; `sha256sum /home/vgpnk/.local/opt/llama-b11909/llama-server` → `35ac50fb…` |

**Which become unknown: none of the six.** The only `unknown` either counter reports at the build is `f8cdb853aaff29393faeb0b6d4c2a2296778b698` (hexrun, exit 1), a round-49 citation of a fleet-repo commit (`corpus/lessons/round-49-verifier-spotcheck.md:21`), not a round-50 value. Draft row + evidence turn it `upstream_ok`, exit 0.

## 2. Setup and fixture commits (fixture identity, scratch clone only)

```
S=/fast/scratch/hyaku/kama-r50/X5Digest2; export TMPDIR="$S"
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"   # exit 0
git -C "$S/lane" rev-parse --show-toplevel   # /fast/scratch/hyaku/kama-r50/X5Digest2/lane
```
Commits in that clone (throwaway identity supplied per command as `git -c user.name=… -c user.email=… -c commit.gpgsign=false commit`, never written to config; the lane tree was never mutated):

| rev | content |
|---|---|
| `97c864bead3ee4a2f629574e77263d33834ec98a` | the build (baseline, unmodified) |
| `0de4a871b27b05a6a992b4bb67f63d3549aaf8ce` | build + draft SCORECARD/LOG paragraphs (`SCORECARD-round50-digests.draft.md`, `LOG-round50-digests.draft.md`) |
| `760902e5886d31b05b43ebd76147a052fe9e982a` | + fabricated-citation control paragraph |
| `fe959a4dbfd0e480cf32b5c2efb9cbf7b09f97f0` | paragraph fixture + draft `registry/hexrun-ledger.tsv` row + evidence files |
| `efb53b7295f891f48d3e81728ef7f6bed991ac04` | + abbreviated-only control paragraph (`e7cdf0ff…` style) |
| `44c325cc3e60ff773d704715ed4ed8e9005a18fe` | paragraph fixture minus the three text copies (deleted in the descendant commit) |
| `22e0154b709764d579ff17042064b3f6494909e9` | integration shape: post-build HEAD (`3b79eadd`) + paragraphs + row + evidence |

## 3. Measurements (commands, outputs, exit codes)

Both exact commands from the item, run once per rev; `matrix.txt` holds the full transcript:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/digest-ledger.py scan --repo "$S/lane" --rev <rev> [--details]
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/hexrun-census.py scan --repo "$S/lane" --rev <rev> [--details]
```

| rev | counter | exit | summary |
|---|---|---|---|
| build `97c864be` | digest-ledger | 0 | `tokens=130 blob=114 external_ok=9 external_absent=1 unverifiable=5 wrong_flagged=1 ledger_bad=0 wrong_unflagged=0 unknown=0` |
| build `97c864be` | hexrun-census | **1** | `tokens=1858 distinct=305 lane_oid=198 md5_blob=1 upstream_ok=94 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=1` — `detail: f8cdb853… len=40 occurrences=1 class=unknown` |
| paragraph `0de4a871` | digest-ledger | 0 | `tokens=133 blob=117 … unknown=0` (+3 distinct: the three page/excerpt digests, all `blob`) |
| paragraph `0de4a871` | hexrun-census | 1 | `tokens=1862 distinct=307 lane_oid=200 … unknown=1` (freeze/build now `lane_oid`; the one `unknown` is unchanged) |
| junk control `760902e5` | digest-ledger | **1** | `tokens=135 … wrong_unflagged=1 unknown=1`; `detail: unknown deadbeefd46a…`, `detail: wrong_unflagged e7cdf0ff000…(first 8 characters match a real digest)` |
| junk control `760902e5` | hexrun-census | **1** | `distinct=308 … unknown=2` — `cafebabe840a…` `unknown` plus the pre-existing `f8cdb853…` |
| + row `fe959a4d` | hexrun-census | **0** | `upstream_ok=95 … unknown=0`; `detail: f8cdb853… len=40 occurrences=1 class=upstream_ok` |
| abbrev control `efb53b72` | digest / hexrun | 0 / 1 | `tokens=133`, `distinct=307`, exits identical to the paragraph fixture — abbreviated forms are not tokens |
| prune control `44c325cc` | digest-ledger | 0 | `tokens=133 blob=117 … unknown=0` even with the three text copies deleted |
| integration shape `22e0154b` | digest / hexrun | **0 / 0** | `tokens=133 blob=117 … unknown=0`; `tokens=1862 distinct=307 lane_oid=200 upstream_ok=95 … unknown=0` |

Details streams differ: `digest-ledger --details` writes to **stdout** (`baseline-digest-build.stdout` holds summary + `detail:` lines; the `.details` capture is 0 bytes), `hexrun-census --details` writes to **stderr** (26 KB `.details` files). This matters if integration pipes only stdout.

## 4. Draft paragraphs (deliverable)

- `SCORECARD-round50-digests.draft.md` — a `### Round-50 digests and object ids (draft; seat X5Digest2, fixture identity)` section naming all six values full-length, each with its evidence path, plus the classification sentence.
- `LOG-round50-digests.draft.md` — the same values as one round-50 bullet.
Both were appended and committed **only in the scratch clone**; the text is deliverable, the commit is fixture identity.

## 5. Draft ledger row (deliverable)

- `proposed-hexrun-ledger-row.tsv` — header + one row:
  `f8cdb853aaff29393faeb0b6d4c2a2296778b698  upstream  VeigaPunk/shokunin  .ufo/waves/round-50/w1/out/X5Digest2/evidence/f8cdb853…json  ·  2026-10-26  note`.
- Evidence: `evidence/f8cdb853aaff29393faeb0b6d4c2a2296778b698.json` (verbatim `gh api repos/VeigaPunk/shokunin/commits/f8cdb853…`, exit 0, sha echoed, 15592 bytes, sha256 `4e629cf9ad195c80825d83ae52c50ac33bf2741834d0e1c6bf81b95ea45871c8`; contains both the token and the `repo` cell text) and `.cmd.txt` beside it (command transcript incl. local `git cat-file -t` → `commit`, `branch -a --contains` → `origin/main`, `remote -v` → `github.com/VeigaPunk/shokunin`, sha256 `9ff6a4f43e288fe2058b58b7fe642c94b78a6190da04015e90f5ec4c3320197a`).
- `proposed-ledger-rows.md` — the six-value class table, the reason no digest row is needed, and the controls.

The row only classifies `upstream` if the evidence file is a blob at the scanned revision (`tools/hexrun-census.py:248-272`), so **row and evidence must land in the same commit**; my `fe959a4d`/`22e0154b` fixtures do exactly that and exit 0.

## 6. Findings (defect-shaped, with command and fix)

**F1 — the build's regression receipt records a failing census without naming the failing citation.** `.ufo/waves/round-50/measured/hexrun-build.out` is `tokens=1858 … unknown=1` / `exit=1` with no `detail:` line, because `.ufo/waves/round-50/measured/measure.sh:29` runs `hexrun-census.py scan --repo . --rev "$TIP"` without `--details`. Show it:
```
$ cat kama-shokunin/.ufo/waves/round-50/measured/hexrun-build.out
tokens=1858 distinct=305 … unknown=1
exit=1
$ grep -n hexrun kama-shokunin/.ufo/waves/round-50/measured/measure.sh
29:run hexrun python3 tools/hexrun-census.py scan --repo . --rev "$TIP"
```
Proposed fix (one line at `measure.sh:29`): add `--details`; the harness already routes stderr into the receipt (`> "$HERE/$name$SUF.out" 2>&1`, `measure.sh:17`) and strips `^detail` from the console summary (`measure.sh:18`), so the receipt would name `f8cdb853…` and the console stays one line.

**F2 — the census is red at the round-50 build and the build's own integration list does not carry it.** Evidence as in F1 plus `matrix.txt` (build row, hexrun exit 1). The round-50 "known integration items" (spec) do not mention it; `.ufo/waves/round-50/measured/*-build.out` does. Proposed fix: land `proposed-hexrun-ledger-row.tsv` + `evidence/` in the integration commit (measured exit 0, `22e0154b`) or record the single `unknown` as deliberate in the SCORECARD paragraph.

**F3 — abbreviated citations are invisible to both counters, so the item's own phrasing would produce no coverage.** `e7cdf0ff…`, `906bbe5c…`, `2dbd3f25…` are 8-hex runs; `digest-ledger.py:67` matches exactly 64 hex and `hexrun-census.py:71-72` matches 32-127 excluding 64. Measured on `efb53b72`: `tokens=133`/`distinct=307`, byte-identical to the paragraph fixture. Fix: the integrated SCORECARD/LOG paragraph must give the full 64-character digests (as the drafts do), not the abbreviated forms.

## 7. Risks and limits

- The `blob` class for the three page digests rests on those blobs being *reachable* from the scanned revision, not on the files existing at HEAD: deleting them in a descendant commit left `unknown=0` (`44c325cc`). A history rewrite that drops the blobs would make them `unknown` — **[INFERENCE]**, not measured, and not something an append-only lane does.
- The server-digest row is `external` against `/home/vgpnk/.local/opt/llama-b11909/llama-server`; on a host without that install the class becomes `external_absent` (exit still 0). The pre-existing `external_absent=1` (`bcc55c92…`, a parked round-35 worktree file) is unchanged by this round.
- `digest-ledger`'s `tokens` counts **distinct** digests, not citations (`tools/digest-ledger.py:117-119`): re-citing the server digest, already cited at `LOG.md:2323` and `corpus/SOURCES.md:241`, moved `tokens` by 0. A paragraph that cites only already-cited digests proves nothing about the counter; the three page digests are the load-bearing new tokens.
- Seat out files live under `.ufo/`, which both counters exclude from *documents* (`digest-ledger.py:75-76`; `hexrun-census.py` `NON_DOCUMENTS`), so the wave's other reports cannot turn the census red — but their blobs do enter the blob set.

## 8. Boundary

No writes outside `kama-shokunin/.ufo/waves/round-50/w1/out/X5Digest2*`; lane, fleet repo, shokuknow untouched; no `git`/`jj` mutation in the lane; no `llama-server` started by this seat (`pgrep -af llama-server` shows only other seats' runs, e.g. `kama-r50/Sen3Teardown/…`, `kama-r50/R0Controls2/…`); no tool installs; scratch `/fast/scratch/hyaku/kama-r50/X5Digest2` removed after the receipts were copied out.

**Deliverables:** `X5Digest2.md` (this report), `SCORECARD-round50-digests.draft.md`, `LOG-round50-digests.draft.md`, `proposed-hexrun-ledger-row.tsv`, `proposed-ledger-rows.md`, `matrix.txt`, `baseline-*`, `fixture-*`, `control-*`, `evidence/*` under `kama-shokunin/.ufo/waves/round-50/w1/out/X5Digest2/`.
