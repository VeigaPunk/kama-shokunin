# SN01ScopeAndMisroot — scope and containment audit (kama r86 w3)

Subject: terminal record tip `bafae7afb41843564ac2468d28beb8e0bb98e8e6` (lane `kama-shokunin`).
All lane bytes read with `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show bafae7af:<path>`;
no mutating git/jj command was run anywhere. Environment at audit end 2026-11-05T00:02-03:00.

Lane drift during the window (recorded, not caused by this seat): lane HEAD moved
`bafae7af` → `0f8a0980` via three lane-authored commits (`d05f6d01`, `ec541687`, `0f8a0980`,
author/committer `kama-shokunin <kama@shokunin.local>`; files: `measured/terminal/*`, `w3-*`
dispatch, `SCORECARD.md`, `corpus/lessons/round-86.md`). Every verdict below is on `bafae7af`
bytes, re-read at that revision.

## Verdicts

| # | Item | Verdict |
|---|---|---|
| 1 | Fleet-root untracked/modified classification | **PASS** — no kama-r86 seat misroot; one orchestrator state file modified, one unattributed 0-byte stray |
| 2 | Lane tree at `bafae7af`: out-of-scope writes, credentials | **PASS on MANIFEST/.ufo/state/.scratch/siblings/domain/credentials; F1 (low) on the seat-write boundary** |
| 3 | Commit authorship and lane scope over `3ff23da3..bafae7af` | **PASS** — 11/11 author == committer == lane identity; all paths in-lane |
| 4 | Three new instruments: no hardcoded `/tmp`, honour TMPDIR/`--work` | **PASS** — F5 (low) is a dead import and two false docstrings, not a scratch breach |

## Item 1 — fleet root

```
$ git -C /home/vgpnk/Projects/shokunin status --porcelain -uall
 M .scratch/run15-state.json
?? mo.tip
```

- `.scratch/run15-state.json` — **orchestrator's (hyaku run-15), never touched.** `git diff` shows
  only run-state churn (`"block_start": 84 → 90`, `"block_done": 6 → 0`, and the same for a second
  lane); the `kama` key is one of nine lanes, not a kama-r86 seat artefact.
- `mo.tip` — 0 bytes, `-rw-r--r-- 1 vgpnk vgpnk 0 Nov 4 23:58`, content empty;
  `grep -c -i -E 'kama|round.?86' mo.tip` → `0`. Unattributed stray of the prior wave's F2 class
  (a redirect resolved against the fleet root). Names nothing, so not a kama-r86 misroot; no action.
- Ignored fleet-root state (`git status --ignored`) is all orchestrator/tooling: `.ufo/state/*`
  (incl. `inline-dispatcher.log`, 1092 `kama` lines — the dispatcher's own log), `.tower/`,
  `.ruff_cache/`, `.jj/`. None is a seat artefact.
- Prior-wave F1 (a kama review had overwritten fleet `.ufo/reports/round-84/kama.md`) is
  **remediated**: `git status --porcelain -- .ufo/reports/round-84/kama.md` → empty, and
  `git show HEAD:.ufo/reports/round-84/kama.md | wc -l` → `69` == `wc -l < .ufo/reports/round-84/kama.md`.
- `MANIFEST.json` (fleet root) is clean: `git status --porcelain -- MANIFEST.json` → empty; its last
  commits are orchestrator-authored (`9dd0a753 … — hyaku, non-author`), none from the kama lane.

## Item 2 — lane tree at `bafae7af`

- `MANIFEST.json`: **does not exist in the lane** (`ls MANIFEST.json` → No such file or directory;
  `git ls-files MANIFEST.json` → empty), and `git log 3ff23da3..bafae7af -- MANIFEST.json` → empty.
- `.ufo/state/`, `.scratch/`: neither path exists in the lane (`ls -d` → No such file or directory);
  `git log 3ff23da3..bafae7af -- .ufo/state .scratch` → empty.
- Sibling repos / domain source trees: no touched path escapes
  `corpus/ LOG.md SCORECARD.md plans/ PROVINCE.md registry/ tools/ .ufo/waves/round-86/`
  (per-commit filter printed nothing for all 11 commits). No sibling repo holds a kama-r86 artefact:
  a filtered `git -C <sibling> status --porcelain -uall | grep -E 'SN01|KamaR86|round-86|round86|kama-r86'`
  over 16 sibling lanes returned only kengaku's and mado's **own** round-86 work
  (`kengaku-shokunin/.ufo/waves/round-86/L1/freeze-battery.txt` — "kengaku-r86/L1/b1";
  `mado-shokunin/.ufo/waves/round-86/receipts/c1-r86.txt`). And `/home/vgpnk/Projects/shokunin/.ufo/waves`
  has no `kama` directory.
- Credentials: over the whole committed round-86 tree
  (`git grep -n -I -E 'BEGIN …PRIVATE KEY|AKIA…|gh[pousr]_…|glpat-…|xox[abpsr]-…|sk-…|BEGIN CERTIFICATE|Cookie: …'`)
  → **no hit**; same for `[?&](api_key|token|access_token|key)=`. The only 40+ char hex runs in the
  added bytes are SHA-256 digests and git object ids. CommonMark 0.31.2 HTML receipt (13 334 lines)
  included in the scan.

### F1 — LOW: two seat reports are committed outside their own `out/<seat>/` (byte-identical)

The plan's Shape section: "Every seat writes only its own `.ufo/waves/round-86/w1/out/<name>/`".
At `bafae7af`:

```
$ git show bafae7af:.ufo/waves/round-86/w1/CR01PredicateCritic.md | sha256sum
c439b4167b1b65e026ac36453528b8b9a32ffae4a68a8be907ac7b92a79d1eab  -
$ git show bafae7af:.ufo/waves/round-86/w1/out/CR01PredicateCritic/CR01PredicateCritic.md | sha256sum
c439b4167b1b65e026ac36453528b8b9a32ffae4a68a8be907ac7b92a79d1eab  -
$ git show bafae7af:.ufo/waves/round-86/w1/SC01SourcesRecon.md | sha256sum
eedaf2bbfff6f9b86a52e8f2d8cae00773985d009883e66d9e1d1f652470df13  -
$ git show bafae7af:.ufo/waves/round-86/w1/out/SC01SourcesRecon/SC01SourcesRecon.md | sha256sum
eedaf2bbfff6f9b86a52e8f2d8cae00773985d009883e66d9e1d1f652470df13  -
```

Both wave-root files are the seats' reports (`head -12` of the CR01 copy: "# CR01PredicateCritic —
claim-sizing falsification (kama r86 w1) … Seat: critic (author-side advisory)"), not specs. Same
hash in two places = two sources of truth that can drift; this is the prior wave's F3 defect class
re-committed in the terminal record. Impact: hygiene, not evidence loss (the out/ copies are the
canonical ones the record cites). Smallest remediation: delete the wave-root copies (or make them
one-line pointers), as the w2 SN01 seat did for its own report.

## Item 3 — authorship and scope of the commit set

```
$ git log --format='%an <%ae>' 3ff23da3..bafae7af | sort | uniq -c
     11 kama-shokunin <kama@shokunin.local>
$ git log --format='%cn <%ce>' 3ff23da3..bafae7af | sort | uniq -c
     11 kama-shokunin <kama@shokunin.local>
$ git log --format='%h|%an <%ae>|%s' 3ff23da3..bafae7af | wc -l
11
```

Author **and** committer are the lane identity on all 11 commits, matching the helper's contract
(`scripts/hyaku/jj-lane.sh:19` — "author AND committer are `<id>-shokunin <<id>@shokunin.local>`"),
and the lane's configured identity is `kama-shokunin` / `kama@shokunin.local`. Per-commit path
filter (drop `corpus/ LOG.md SCORECARD.md plans/ PROVINCE.md registry/ tools/ .ufo/waves/round-86/`)
printed nothing for any of the 11 commits → the commit set is lane-scoped, no fleet or sibling content.

Three extra commits exist in `refs/jj/keep/` (`365c7f9b`, `7baa0824`, `01ba390b`) — same author,
same parents/timestamps as landed commits; these are jj push-recovery shadows, and the master line
is a fast-forward chain (`bafae7af` → `c5a32443` → … → `c07e1f90`). No master-line rewrite.

### F3 — LOW: the terminal commit rewrote two committed seat receipts

```
$ git show --name-status --format='' bafae7af | grep '^M'
M .ufo/waves/round-86/w1/out/SB01LessonDraft/receipts/anchor-upstream-recheck.txt
M .ufo/waves/round-86/w1/out/SB01LessonDraft/receipts/c2.out
$ git show bafae7af -- …/receipts/c2.out
-DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34
+DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0
```

A receipt is evidence; the wrap-up commit edited it in place instead of appending a dated
correction. The before/after of the `c2.out` line survives only inside the same seat's
`receipts/final.txt` (`<` at line 24/67, `>` at line 69), and `anchor-upstream-recheck.txt`'s header
edit is not described anywhere. No claim flips as a result: the record's cited
`.ufo/waves/round-86/measured/after/c2.out:7` still reads `pass=34 fail=0 arms=34`. Impact is
reproducibility of the seat's own evidence, low. Smallest remediation: restore the receipt bytes and
land the correction as a new dated file.

## Item 4 — instrument scratch discipline

```
$ grep -rn '/tmp' tools/round86-rendered-cells.py tools/round86-mutant-owners.py tools/round86-pin-origin.py
tools/round86-mutant-owners.py:268: print("could-not-evaluate: --work is required (no hardcoded /tmp)", …)
```

No literal `/tmp` path in any of the three instruments; the only match is the refusal message.

- `round86-mutant-owners.py`: `--work` is required — `if not args.work: print("could-not-evaluate:
  --work is required (no hardcoded /tmp)") ; return 2`; the work dir is created under the caller's
  path (`work.mkdir(parents=True, exist_ok=True)`, line 169) and handed to the child as
  `env={**os.environ, "TMPDIR": str(work)}` (line 153). Its own selftest writes nothing.
- `round86-pin-origin.py`: fixtures live in `tempfile.TemporaryDirectory(prefix="r86-origin-")`
  (line 202), which resolves through `TMPDIR` by construction; anchors are written only inside it.
- `round86-rendered-cells.py`: no `--work` argument (none is needed — it only reads `git show`
  bytes); its selftest is a pure in-memory tree (`DictTree`/`FixtureTree`). Scratch discipline is
  honoured vacuously.

### F5 — LOW: dead import and two false docstrings

- `tools/round86-rendered-cells.py:51` — `import tempfile`, never referenced (`grep -c tempfile` → 1;
  `grep -n 'tempfile\.'` → no match), and its docstring line 40 claims "``--selftest`` builds fixture
  trees in $TMPDIR (no git)" while the selftest builds no tree at all (in-memory `DictTree`).
- `tools/round86-mutant-owners.py:41` — "``--selftest`` exercises the classifier on synthetic outputs
  in $TMPDIR"; the selftest classifies literal strings and writes nothing.

Operability impact: a reader auditing "does this touch /tmp?" gets a misleading answer; the import
also fails a strict linter. Smallest remediation: drop the import and correct the two docstrings.

## Disclosed deviations (not findings, recorded for the record's adjacency)

- **Frozen-plan control counts vs delivered instrument.** The plan freezes 11 / 10 / 7 selftest arms.
  At `bafae7af`: rendered-cells 17 controls (11 at `c07e1f90`), mutant-owners 13 (10 at freeze),
  pin-origin 7 (unchanged). The record discloses it — `SCORECARD.md` round-86 C1 row:
  "selftest 17/0 at the terminal tree (11/0 at the freeze)"; lesson M3/M6 name the added arms.
  The frozen PREDICATE strings themselves are **byte-identical** freeze → tip:
  md5 `f36302bf9dc6b97843df1e7f8ddd9e6a` / `34eeb45132f777c0dadb250c28bffa5c` /
  `ae305d34fee65a344e682f7941afb8d4` at both revisions. `plans/round-86-claims.md` and
  `.ufo/waves/round-86/count.py` are unchanged over `c07e1f90..bafae7af` (`git diff --stat` → empty).
- **F2 — LOW, unremediated from w2:** committed round-86 reports still publish `/tmp` scratch
  commands — `.ufo/waves/round-86/w1/out/CN01OverlapScan/CN01OverlapScan.md:151-153`,
  `.ufo/waves/round-86/w2/SN01ScopeSentinel.md:183-185`,
  `.ufo/waves/round-86/w2/out/CN01OverlapScan/CN01OverlapScan.md:209-211`
  ("`… count.py c1 --repo . --rev master --work /tmp/c1`"), against the plan's declared scratch root
  `/fast/scratch/hyaku/kama-r86/<seat>/`. Guidance text only: no round-86 receipt records a command
  that actually ran with `--work /tmp` (11 non-historical `/tmp` lines in the tree are these nine
  suggestion lines, one diagnostic `grep` in SN01, and the w2-results embedding).

## Tools

None installed or upgraded (pacman paused host-wide; nothing was needed). No `/tmp` writes; scratch
copy `/fast/scratch/hyaku/kama-r86/SN01ScopeAndMisroot/` removed before yield.
