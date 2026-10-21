VERDICT: confirm - file-set separability holds both ways (other set reverted: stdout and exit identical, working-tree and committed); landing is commit-atomic, so C1's round-21 gate cannot separate a29bb84's C2 part
# C1 vs C2 causal separability (KamaR21.C1C2Separability-6)

Subject: kama a29bb84 (HEAD = master). Fleet passed as `--fleet-repo /home/vgpnk/Projects/shokunin`. Lane not edited. Scratch clones deleted after archiving to `build/out/C1C2Separability-6/` (126 files, 280K; `scripts/`, `run1-4/index.txt` hold every rc).

Axes: A C1 counts with C2 reverted; B C2 counts with C1 reverted; C fault propagation; D landing granularity; E unclaimed inputs and consumers.

## Partition (executed: `git show --stat a29bb84`)
- C1: tools/report-landing-audit.py +404; registry/report-landing-errata.tsv +11.
- C2: tools/kama-llamacpp-live.py +28/-0; tests/llamacpp-live/check-receipt.py +123/-2; tests/llamacpp-live/install-links-grid.py +332.
- Unclaimed by either claim: .ufo/waves/round-21/sources/census-before.txt (+17), validate-before.txt (+8). Grep of tools/, tests/, registry/ for `round-21/sources|waves/round-21`: no match.
- Inputs: C1 = stdlib + fleet `.ufo/reports/round-10..20` + git objects + its TSV. C2 = lane working tree + git 7a6bc911 (frozen arm) + `~/.local/opt/llama-b11755` (grid default).

## Reverts (scratch clones at a29bb84, clean status)
- revC2: C2 files restored to 7a6bc911 (`git checkout 7a6bc911 -- ...`), grid deleted. Checks: `git diff --quiet 7a6bc911 -- <C2 files>` rc 0; `git cat-file -e 7a6bc911:...install-links-grid.py` rc 128 (absent).
- revC1: C1 files deleted. Check: `git diff --quiet a29bb84 -- <C2 files>` rc 0.
- Committed: revC2h = commit 0520d48, revC1h = commit fbf9595 (author kama-shokunin, subject `round-21: scratch ...`).

## A. C1 counts, C2 reverted (exit base / revC2; stdout identical)
- `python3 tools/report-landing-audit.py --no-errata --fleet-repo F` -> 1 / 1. `summary ... corrected=0 uncorrected=9 ... status=failed`
- `python3 tools/report-landing-audit.py --fleet-repo F` -> 0 / 0. `... corrected=9 uncorrected=0 ... status=clean`
- `python3 tools/report-landing-audit.py --selftest` -> 0 / 0. `selftest cases=15 failed=0`
- Committed revC2h: the same three -> 1 / 0 / 0, identical to base.
- Negative control: revC2 `install-links-grid.py --arm current` -> 2 (file absent); grid restored into revC2b (producer at 7a6bc911) -> 2, `could-not-evaluate: current producer has no install_links()`.
- Causal check: faultC1 (errata row for 33a67778 deleted) -> 1, `corrected=8 uncorrected=1`, `UNCORRECTED landed-omitted 33a6777866d0f63d894ef21bc863486bcb35b56c`.

## B. C2 counts, C1 reverted (exit base / revC1; stdout identical)
- `python3 tests/llamacpp-live/check-receipt.py --selftest` -> 0 / 0. `9 VALID and 1 NOT-EVALUATED receipts accepted; 90 mutations + unreadable case rejected`
- `python3 tests/llamacpp-live/install-links-grid.py --arm current` -> 0 / 0. `link=9/9 regular=2/2 type=1/1 null=0/1 wrong=0 status=pass`
- `... install-links-grid.py --arm frozen` -> 1 / 1. `link=0/9 ... status=fail` (by design)
- `... install-links-grid.py` (both) -> 1 / 1. `back_compat install_tree_sha256 equal=True`
- `... install-links-grid.py --selftest` -> 0 / 0. `selftest cases=12 failed=0`
- `tests/llamacpp-live/install-tree-grid.py --selftest` (round-19 grid; runs the C2 gate fixture) -> 0 / 0 (and 0 under revC2).
- Committed revC1h: gate 0, grid current 0, grid both 1, grid selftest 0, identical to base.
- Negative control: revC1 audit -> 2 (`can't open file`).
- Causal check: faultC2 (producer `install_links` never records a link; line 220 `if False:`) -> grid current 1, `link=0/9 ... status=fail`; gate selftest still 0 (it never runs the producer).

## C/D. Propagation and landing
- faultC1 -> C2 gate 0, grid current 0, grid selftest 0 (stdout == base). faultC2 -> C1 audit 1/0/0 (stdout == base).
- revF (frontier files removed) -> every C1 and C2 check == base. wsC2 (lane's uncommitted producer copied in) -> grid current 0, gate 0, == base.
- The one real coupling: `--report 21=<draft>` requires every `round-21:` commit on master to be cited; today that is only a29bb84. Draft citing nothing -> 1 (`round=21 required=1 defects=1`, `UNCORRECTED landed-omitted a29bb84...`). Draft citing `a29bb84` -> 0 (`defects=0`). Drafts are synthetic, archived in `drafts/`.
- With revC2h's commit on master, the same citing draft -> 1 (`required=2`, `UNCORRECTED landed-omitted 0520d48...`); rounds 10-20 unchanged (0, identical).
- So the C1 round-21 pass certifies all of a29bb84 (C1 + C2 + frontier). Per-file-set counts do not yield per-file-set landing.
- The audit reads `--branch master` by default. A commit on detached HEAD is invisible: the first attempt gave `required=1` until master was moved (observed).

## E. Other couplings and hazards
1. Default fleet root = lane parent (`here.parent`). From any copy outside the real layout: `could-not-evaluate: ... not a git repository`, exit 2 (`base_c1_default_fleet`). C1 needs `--fleet-repo`; C2 has no such dependency.
2. The C2 counting command that can pass is `--arm current` (0). Default `both` exits 1 by design.
3. Name collision: tests/llamacpp-live/controls.py:2 calls its counter "C1 counting command". Not run (it launches the producer against fake servers; bounds). [INFERENCE: its graded receipt shape may move with the new install_links keys; tools/error-verdict-census.py pins install-tree-grid.py and the grid-gate fixture, not check-receipt; not run.]
4. Lane working tree is not a29bb84: tools/kama-llamacpp-live.py has one extra blank line after line 1151 (`git status` M; `diff` rc 1; mtime 07:48:01). Not my edit (my only producer edit is scratch faultC2 at 07:50:55; scratch lane sha256 = a29bb84 blob c05cd8bf). Whitespace-only; no count changed. Left for L1/peer; not reverted.
5. Disclosure: my read-only lane git calls (status/diff/reflog) ran without `--no-optional-locks`. `.git/index` mtime is 07:47:52; I cannot attribute it (my first status call, or the jj export visible in the reflog). No ref or content change; HEAD = a29bb84. `tools/__pycache__` and `.jj/repo` also show post-07:40 mtimes, not from this seat (all my Python ran in scratch with PYTHONDONTWRITEBYTECODE=1).

## Exits and scope
- Host: `find ~/.local/opt/llama-b11755 -newermt 2026-10-21 | wc -l` -> 0. No grid temp-dir leftovers.
- Lane final: `git --no-optional-locks -C <lane> status --short` -> ` M tools/kama-llamacpp-live.py`, `?? .ufo/waves/round-21/build/` (peer state; my outputs are new files under build/).
- Not run: any llama-server or producer live launch; controls.py; error-verdict-census.py; any official measurement in the lane.
- Tools installed or upgraded: none (git 2.56.0 and Python 3.14.8 pre-existing).
