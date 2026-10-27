# W1Errata — round-51 errata draft for the round-52 lesson (D2, D3, D4, D6)

**Verdict: all four routed defects re-verified against committed bytes and drafted append-ready; one of them (D3) is only half closed — the pointer receipt this round produced at `1ab1de39` exists on disk but is not committed at `34d82600`.**

Append-ready text: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W1Errata/errata.md` (a `## Errata (round-51 closure routed defects)` section for `corpus/lessons/round-52.md`, which is 20 lines and ends at the `## Gate` S500 row).

## Method

Read-only. No counter, tool, replay or lane write was run: no `round52-*-audit.py`, no `round52-append-restore-check.py`, no `llama-server`, no `git add/commit`. No tool was installed. Scratch `/fast/scratch/hyaku/kama-r52/W1Errata` held only one `git show` dump of `SCORECARD.md` and the tool copy for the D3 re-derivation; both removed. Lane reads via `git -C /home/vgpnk/Projects/shokunin/kama-shokunin` (no clone was needed, so `$S/lane` was never created). The round-51 report is a fleet-repo file (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-51/kama.md`) and was read only.

## D2 — seat count at filing: 51/66, 15 running (report says 50/66, 16 running)

Claim under test (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-51/kama.md:16`): "the round was landed with **50 of 66 seat reports** in hand … Still running at filing: Sen1Exe, M1Ctr, M2Live, V1Review, K2Design, V3Review, Rev2Arow, Sen3Ledger, L6Slice, T1Lesson, T4Quality, T6Skill, X3R41, X5Census, Sim1, X8Restore."

| Command | Output | Exit |
|---|---|---|
| `git ls-tree --name-only 1ab1de39 -- .ufo/waves/round-51/a2w1/out/ \| grep -cE '\.md$'` | `51` | 0 |
| `git show 1ab1de39:.ufo/waves/round-51/a2w1/dispatch.json \| python3 -c '…["counts"]'` | `{'spawn': 66, 'resume': 0, 'total': 66}` | 0 |
| `git show 1ab1de39:.ufo/waves/round-51/a2w1/out/swarm-registry.json \| python3 … len(members)` | `66` | 0 |
| `git cat-file -s 1ab1de39:.ufo/waves/round-51/a2w1/out/V1Review.md` | `11579` | 0 |
| `git log -1 --format='%H %ci' --diff-filter=A -- …/V1Review.md` | `1ab1de39… 2026-10-27 01:09:47 -0300` | 0 |
| `git log -1 --format='%s' 1ab1de39` | `round-51: measured results (be8169a6), measurement receipts, wave a2w1 seat outputs (50/66 reports at filing)` | 0 |

- 66 − 51 = **15** seats had not filed. The report's 16-name running list is exactly those 15 plus **V1Review**, which was already committed by `1ab1de39` itself (01:09:47), 78 s before the report commit `39877b17` (01:11:05).
- Correction: 51/66 at filing, 15 running, V1Review removed from the running list. The set of 15 (by top-level `<Seat>.md`): Sen1Exe, M1Ctr, M2Live, K2Design, V3Review, Rev2Arow, Sen3Ledger, L6Slice, T1Lesson, T4Quality, T6Skill, X3R41, X5Census, Sim1, X8Restore.
- Limit stated in the draft: five of those 15 had no bytes at all at `1ab1de39` (L6Slice, T1Lesson, V3Review, X3R41, X8Restore); ten had committed evidence in their own subdirectory but no top-level report. At the salvage `9ff76b1f` the count is 54/66; at `34d82600` it is 54/66 plus the non-seat `X7Regen.late-rewrite.md` (55 top-level `.md`), with L6Slice, T1Lesson, X3R41, X8Restore still byte-less.

## D3 — planned-pointer claim had no receipt; this round's receipt is uncommitted

- Claim (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-51/kama.md:79`): "Planned-pointer `met=True` at the final tip `1ab1de39`."
- `git ls-tree -r --name-only 1ab1de39 -- .ufo/waves/round-51/measured/ | grep pointer` → three files; `grep -o 'tip=[0-9a-f]*'` on them → `73bf2a7a…` (`pointer-build.out`, `met=True`, plan line `### Planned (round 51)`), `c5ec93d5…` (`pointer-int.out`, `met=False`, exit 1), `be8169a6…` (`pointer.out`, `met=False`, exit 1). `grep -rl 1ab1de39 .ufo/waves/round-51/measured/` → no match, exit 1.
- The fact is true; I re-derived it without the lane:
  `git show 1ab1de39:SCORECARD.md > $S/SCORECARD-1ab1de39.md && python3 tools/planned-pointer-check.py $S/SCORECARD-1ab1de39.md` → `pointer: ok (… ### Planned (round 52) …)`, 12 × `measured: ok`, the last `### Round-51 measured results`, `met=True`, **exit 0**. Tool bytes identical at `1ab1de39` and HEAD: sha256 `df7cecfcf07bfa799f9e8170101d0af09795b83ef888669ac893c87d937464d9`. Section present at `1ab1de39:SCORECARD.md:2925`.
- This round's receipt: `.ufo/waves/round-52/d3/pointer-1ab1de39.out` → `tip=1ab1de39…; round-51 closure D3: the receipt the round-51 report cited`, `met=True`, `exit=0`.
- **Defect for the L1 to close:** that receipt is untracked. `git ls-tree -r 34d82600 -- .ufo/waves/round-52/d3/` prints nothing (exit 0, empty) and `git status --porcelain` shows `?? .ufo/waves/round-52/d3/`. The committed `34d82600:.ufo/waves/round-52/measured/pointer-build.out` pins `tip=5dacf2c7…`, not `1ab1de39`. Proposed fix (commit only, no content change): `git -C <lane> add .ufo/waves/round-52/d3/pointer-1ab1de39.out` in the integration commit, and add a pointer receipt at this round's measured commit; until then the round-51 evidence-standard defect is answered in the worktree only.

## D4 — regeneration agreement scope: 142 of 165 rows at `138af25b`, not the ledger

- Round-51 phrasing (`/home/vgpnk/Projects/shokunin/.ufo/reports/round-51/kama.md:73`): "X7Regen (an independent ledger regeneration matches exactly)".
- Seat's own scope (`.ufo/waves/round-51/a2w1/out/X7Regen.md:9-10`): 142 rows/142 lines each side, `only_in_regen=0 only_in_ledger=0`; "excludes the 24 `SCORECARD.md` rows/lines by assignment; both `only=` knowledge files are also excluded. This is a scoped comparison". Artifacts: `X7Regen/ledger.diff:7-20` (142/142, no differences, `identical: order and bytes`, `SCORECARD.md rows=24 lines=24`); `X7Regen/regen-run.out:1-4` (`skipped=['SCORECARD.md', 'corpus/knowledge/consumer-registry.md', 'corpus/knowledge/error-is-not-a-verdict.md']`, `undisclosed=142`).
- Denominator checks: `git show 138af25b:registry/append-only-disclosures.tsv | wc -l` → `167` (header + 166 rows); `grep -c 'SCORECARD.md'` → `24` → 142 compared. At `be8169a6` and `1ab1de39`: `166` lines (header + 165 rows), 23 `SCORECARD.md` rows → 142. So the agreement covers 142 of 165 (166 at `138af25b`) disclosure rows, in the whole-file-graded slice, at `138af25b`.
- Correction drafted: cite the scope (file set, tip, 142/165) wherever the agreement is used. The only citation in the round-51 report is line 73; `1ab1de39:SCORECARD.md` and `1ab1de39:corpus/lessons/round-51.md` do not cite it (`git grep -n 'X7Regen\|regeneration' 1ab1de39 -- SCORECARD.md corpus/lessons/round-51.md` → no match).

## D6 — flip conditions for rejects 1–3

Source: `corpus/lessons/round-51.md:24` (digest alone), `:25` (`readlink` text as identity), `:26` (member-path dev/inode when other links) — each currently "Flip: never". Governing inference: `.ufo/waves/round-51/a2w1/out/J4Hardlink.md:44` (nlink alone does not prove extraction; the robust check is a counter-owned extraction).

Drafted replacements (full text in `errata.md`):

1. **Digest alone — flip when the digest's reference becomes verifier-owned** (the counter extracts/hashes the bytes itself). Round 52 does not reach it: the memfd is replay-filled (`tools/kama-live-replay.py:222-256`) and a memfd filled from the host's byte-identical install still meets (`preregistration.json:41`; seat `J5HostMemfd.md:3` — `met=True` from the host install).
2. **`readlink` text — no reachable flip**: the running image prints the constant `/memfd:llama-server (deleted)` (`.ufo/waves/round-52/measured/c1-build.out:6,8,10`); the counter uses the text only beside `st_nlink 0`, seals and digest (`tools/round52-replay-memfd-audit.py:384-387`). The link is a name; the fd is the object.
3. **Member-path dev/inode — the flip's first half now holds, the second does not.** The running image has no directory entry (`/memfd:`, dev `00:01`, nlink 0, seals 15, frozen digest; `c1-build.out:3,6-10`), so the path class is closed for the image: round-52 hardlink `sealed=0 … met=False` (`J4Hardlink.md:3`), rename-over invisible to the image (`J6RenameOver.md:3`, `met=True`), copy-at-path refused (`J3CopyDecoy.md:1`). The replay now requires `nlink == 0` on `server_exe` (`tools/kama-live-replay.py:456`), superseding the round-51 `member-links` member check (docstring `:63` vs the superseding `:66-75`). The second half — counter-owned extraction, i.e. J4Hardlink's `[INFERENCE]` — is not reached: `nlink == 0` on a replay-filled memfd still does not prove the bytes came from the archive (`preregistration.json:41`; seat table `.ufo/waves/round-52/w1/out/S6Limits/limits.md`, R51 rows: "Closes path provenance as a requirement for the running image; leaves source provenance").

## Touched surfaces

- Wrote only: `.ufo/waves/round-52/w1/out/W1Errata.md` (this report) and `.ufo/waves/round-52/w1/out/W1Errata/errata.md` (deliverable). Nothing else in the lane, fleet repo or scratch remains.
- Lane files read only: `corpus/lessons/round-51.md`, `corpus/lessons/round-51-verifier-spotcheck.md`, `corpus/lessons/round-52.md`, `SCORECARD.md` (via `git show`), `registry/append-only-disclosures.tsv` (via `git show`), `tools/round52-replay-memfd-audit.py`, `tools/kama-live-replay.py`, `tools/planned-pointer-check.py`, `.ufo/waves/round-51/**`, `.ufo/waves/round-52/**`.
- Fleet file read only: `.ufo/reports/round-51/kama.md`.

## Out of scope / not verified

- No counter was run, so this seat adds no measurement of C1/C2 at any revision; the build claims are cited from the committed receipts (`measured/c1-build.out`, `measured/c2-build.out`), not re-executed.
- I did not audit the rest of the round-51 report's numbers, nor the round-52 build's correctness. D1, D5, D7 and the integration items (SCORECARD §Round 52, LOG, QUALITY KQ86/KQ87 supersession, README frontier, round-51 errata D2/D3/D4/D6 landing) are the L1's at integration and are untouched here.
- The errata text is a draft for the lesson; I did not write it into `corpus/lessons/round-52.md`.
