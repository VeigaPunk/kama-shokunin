# W2Quality — round 53 (kama), QUALITY rows

**Verdict:** the round-53 QUALITY section already exists in the lane's **uncommitted** working tree
(`KQ94`-`KQ96`, `corpus/QUALITY.md` sha256 `ed46d4b4…7eb94`), so this seat reviewed it against the
build instead of landing a duplicate set: two rows state more than the mechanism does or cite a
lesson section that does not exist (KQ94's memfd quantifier; KQ95/KQ96's `corpus/lessons/round-53.md`
"Mistakes"), and the minimal fix is a verified 3-line diff in this directory. Both frozen counters
reproduce the L1's build receipts leg for leg on my own clone and fail the base controls.

## Behavior

Read-only on the lane and the fleet; scratch `/fast/scratch/hyaku/kama-r53/W2Quality`, one
`git clone --shared` at `$S/lane`. No pacman (host-wide pause), no tool install, no tracer, no
service started or stopped, no subagent, no `agent://all`. Every git call was
`show`/`status`/`log`/`diff`/`cat-file`/`clone --shared`; no lane, fleet or fixture commit.

Work done: read the contract (`corpus/QUALITY.md:456-476`, `preregistration.json`,
`corpus/lessons/round-53.md`, `corpus/lessons/round-52-verifier-spotcheck.md` R1/R2, both counter
docstrings, the mechanisms they name in the build's tools); re-ran both frozen counters at the build
on my own clone; wrote and ran `sources-anchor-check.py` for the R1 criterion; drafted the three
rows independently; then found the L1's in-tree section, reviewed it clause by clause against the
build, and produced the corrected text.

## Evidence

| # | Command | Observed | Exit |
|---|---|---|---|
| 1 | `python3 tools/round53-replay-code-audit.py --repo $S/lane --tip c22602bd… --scratch $S/c1` | `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True`; each of b1-b3 `8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem to the counter's own archive, 13 root-owned host files`; `newrow: 4 rows new since base; 1 name proc_pid_mem(5)`; 18.26 s (`c1-build.out`) | 0 |
| 2 | `python3 tools/round53-cited-path-check.py --repo $S/lane --tip c22602bd… --scratch $S/c2` | `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True` (`c2-build.out`) | 0 |
| 3 | `sources-anchor-check.py --sources <SOURCES@c22602bd> --row S506 --row S507 --row S508 --row S509 --copy S509=.ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909` | `rows=4 anchors=4 ok=4 fail=0 na=3 covered_copy=1 copy_mismatch=0 met=True`; S509 at 401 / 480 / 488-489 / **491**; fetched sha256 `1436b46b…7fe` = committed copy (`anchor-round53.out`) | 0 |
| 4 | `sources-anchor-check.py … --row S505 --row S101 --row S140 --row S106` | S505 `lines 422–439` → **fail** (`got=[480, 578, 579]`); S101 (`read_graft_line`, `lines 249-260`) → ok; S140/S106 → `n/a reason=form-not-in-grammar` (`anchor-controls.out`) | 1 (by design) |
| 5 | `git show c22602bd:tools/kama-llamacpp-live.py \| sed -n '793p'`; `…round53-replay-code-audit.py \| sed -n '413p'` | both filters: `f[5].startswith('/memfd:')` → `continue` — **every** memfd mapping is skipped, not only foreign ones | 0 |
| 6 | `git show c22602bd:tools/round53-replay-code-audit.py \| sed -n '464,486p'`; `…kama-live-replay.py \| sed -n '505,517p'` | the only memfd examined is the running image through `/proc/<pid>/exe` (seals, dev+inode) | 0 |
| 7 | `grep -n '^## ' corpus/lessons/round-53.md` | `9:## Claims`, `14:## Gate`; no `Mistakes` section (the only "Mistakes" string is "W3Mistakes" at :12) | 0 |
| 8 | `git diff corpus/QUALITY.md` | 10 added lines at `@@ -464,3 +464,13 @@`: the round-53 section with KQ94-KQ96, uncommitted | 0 |
| 9 | `git show d01b2b6d:tools/… \| sha256sum` and at `c22602bd` | counters `1a7a1442…75d8f`, `1afb8b9d…3e3080` at both commits, equal to `preregistration.json` `counter_sha256` — the frozen counters I ran | 0 |
| 10 | `git show c22602bd:tools/*.py │ grep -n` over every pointer I cite | all resolve to the attributed text (`kama-live-replay.py:290,305,323,327,329,333,337,521-522`; `kama-llamacpp-live.py:774,793,801,814,2309`; `round53-replay-code-audit.py:103,393,405,413,424-433,447,456-459,464-486,619-630`; `round53-cited-path-check.py:28-37,41-58,59-73,107`) | 0 |
| 11 | patched copy of `corpus/QUALITY.md` (`quality.proposed.diff` applied to `$S/Q.md`) | `diff -u` clean against a copy of the working file; each of lines 474-476 still 4 cells; 6 spans changed, no other byte | 0 |
| 12 | `pgrep -af llama-server` after my runs | nothing of mine; the host's only server then was peer K2Design's (gone by the end) | 0 |

Base controls read (the L1's committed observations at `4229ea1b`, not re-run):
`base.c1.out` `code=0 coderuns=0/3 met=False` — per run `replay own_code 'None' is not verified with
members` plus eight `rerun code_mappings has no entry …` lines; `base.c2.out` `lane=0 cited=679
unresolved=16 disclosed=0 undisclosed=16 met=False`, all 16 named (SKILL 6, SCORECARD 10).

My C1 receipt matches the L1's `measured-c1-build.out` digit for digit; my C2 receipt matches
`measured-c2-build.out` in every leg and `detail:` line, differing only in the echoed command, the
`fleet=` rev (`ee9f7341` vs my `d2a6c59a`) and the trailer `exit=`.

## Gates (observed, not judged)

C1 and C2 both `met=True` on my own runs at `c22602bd` and `met=False` on the base controls; the C1
`code` leg fails exactly the eight library members the claim adds; the C2 base leaves 16 citations
undisclosed. Admission of the claims belongs to the L1 / canonical judge; this seat only states what
it reproduced. I did not run `tools/append-only-audit.py` — this seat wrote no line of
`corpus/QUALITY.md`.

## Touched surfaces

- Written: `.ufo/waves/round-53/w1/out/W2Quality/` and this report only.
- Read-only: lane (git objects; counters ran against my `git clone --shared`), fleet repo (C2's
  fleet leg). Network: the two counters' own downloads (C1's b11909 archive, model and vocabulary;
  C2's pinned raw URLs — 5 `upstream` ledger rows, 4 distinct URLs) and 4 fetches by this seat
  (`ggml-backend-reg.cpp` @ b11909, `commit.c` @ git v2.56.0, `server-schema.cpp` and `fit.cpp` @
  704366d76).
- The lane's working tree is **not** mine to change: `corpus/QUALITY.md`, `SKILL.md`,
  `tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py`, `registry/hexrun-ledger.tsv` and the
  two `measured/*-build.out` were already modified, and 29 paths untracked, when I arrived.

## Findings

**Q1 (row defect, medium — KQ94 `corpus/QUALITY.md:474`).** The admit cell says "every executable
file mapping of its running server" and "admits no executable memfd but its own sealed server".
Neither holds: both enumerations skip every `/memfd:` mapping (`tools/kama-llamacpp-live.py:793`,
`tools/round53-replay-code-audit.py:413`) and the only memfd read is `/proc/<pid>/exe`
(`:464-486`). The build's own receipt shows it — `code_mappings` carries no `/memfd:` entry while
`server_exe` is `/memfd:llama-server (deleted)`. Command: `git show c22602bd:tools/round53-replay-code-audit.py
| sed -n '413p'`. The reject cell's "a path-less or second-memfd mapping admitted (wave seats
V1Review, V3Review)" is the accurate half, and seat V3Review reported the code gap at
`.ufo/waves/round-53/w1/out/V3Review.md:10` — so this is not a new code finding, it is the row
asserting an enforcement that its own reject cell and V3Review say is absent. Fix: `quality.proposed.diff`
hunk 1 (exact quantifier + "an executable memfd besides the image is not enumerated").

**Q2 (row defect — KQ95 `:475` and KQ96 `:476`).** Both fourth cells cite
`corpus/lessons/round-53.md` **Mistakes**, which does not exist: the lesson has `## Claims` (:9) and
`## Gate` (:14) only. This is the defect class round-52 closure D7 recorded. The citation that was
meant is `corpus/lessons/round-52.md` Mistakes #4 (KQ95) and `corpus/lessons/round-53.md` Gate S509
(KQ96). Command: `grep -n '^## ' corpus/lessons/round-53.md`. Fix: hunks 2 and 3 of the diff.

**Q3 (row defect, calibration — KQ96 `:476`).** The admission locates the quote "in a copy of the
source fetched for that row (the copy committed beside the round)" — making the *committed copy* the
reference, so a copy that is not the fetch passes. R1 says "in the fetched copy". The fix keeps the
copy but admits it only on sha256 equality with the fetch; that holds for S509
(`1436b46b…7fe`, my `anchor-round53.out` and the build's committed bytes). Fix: hunk 3.

**Q4 (integration hazard — the lane working tree is a third state).** `git -C <lane> status
--porcelain` shows 7 modified and 29 untracked paths; `tools/kama-live-replay.py` differs from the
build *and* from the file's own blob at the tip — working tree `:305` reads
`def verify_code(cm, archive, tree, own=None):` while `git show c22602bd:tools/kama-live-replay.py`
at `:305` reads `def verify_code(cm, archive, tree):` (build and tip blobs are both
`6c0bfbdf…98102`). This review is of the working-tree section at sha256 `ed46d4b4…7eb94`; if the L1
edits or lands it differently, the review must be re-derived, not assumed. My own pointers are
build-pinned (`git show c22602bd:`).

**Q5 (coverage limit, for the record).** `corpus/SOURCES.md` at the build has **97** rows whose
anchor names line numbers; `sources-anchor-check.py` reads three forms and reports the rest `n/a`
(e.g. S140's `path line N (declaration X)`, S106's mixed anchor). KQ96/KQ99 as drafted therefore
admit only rows in that grammar; sweeping the rest is round-54 work.

**Q6 (limits the in-tree rows leave implicit, carried by my draft).** `code_observe` compares each
mapped range with member bytes zero-padded to the range length
(`tools/round53-replay-code-audit.py:424-425`) and reads memory once while the server is held
(`:405`); in my draft rows both appear in KQ94's limit cell.

**Q7 (not a defect).** My C2 run resolved against fleet HEAD `d2a6c59a` while the receipts used
`ee9f7341`; every counter and the verdict are identical, so the fleet rev does not carry C2.

## Out of scope (known integration items, untouched)

SCORECARD §Round 53 and measured results, LOG entry, the QUALITY integration itself, README
frontier, SKILL §Round-53 instrument registry, lesson Mistakes/Errata, Planned (round 54). I did not
re-derive the claims beyond re-running the frozen counters.

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality/quality.md` — review of the in-tree rows, clause by clause, with Route A (diff) and Route B (appended KQ97-KQ99)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality/quality-draft-rows.md` — this seat's independently drafted KQ94-KQ96 (not to be landed beside the in-tree rows)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality/quality.proposed.diff` — unified diff against the working-tree `corpus/QUALITY.md` (sha256 `ed46d4b4…7eb94`), 12 lines, one hunk
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality/sources-anchor-check.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality/c1-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality/c2-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality/measured-c1-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality/measured-c2-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality/anchor-round53.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality/anchor-controls.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality/SOURCES.build.md` (`git show c22602bd:corpus/SOURCES.md`, sha256 `7eea0ffb…1ae00`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W2Quality.md` (this report)
