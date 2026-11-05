# SN01ScopeAndMisroot — scope and containment audit, kama r86 w3

Subject: terminal record tip `bafae7afb41843564ac2468d28beb8e0bb98e8e6`. Frozen plan read in full
(`plans/round-86-claims.md`). Lane bytes read only via `git show`; no mutating git/jj anywhere.
Full evidence trail: `.ufo/waves/round-86/w3/out/SN01ScopeAndMisroot/findings.md`.

## Verdicts

1. **Fleet-root classification — PASS.** `git -C /home/vgpnk/Projects/shokunin status --porcelain -uall`
   → ` M .scratch/run15-state.json` and `?? mo.tip`. The first is the hyaku run-15 orchestrator state
   (diff is lane-block churn only: `"block_start": 84 → 90`, `"block_done": 6 → 0`) — never touched.
   `mo.tip` is 0 bytes, `grep -c -i -E 'kama|round.?86' mo.tip` → `0`: unattributed redirect stray,
   not a kama-r86 misroot. No kama-r86 seat artefact exists at the fleet root; the w2 F1 destructive
   misroot (fleet `.ufo/reports/round-84/kama.md`) is **remediated** (worktree == HEAD, 69 lines).
2. **Lane tree at `bafae7af` — PASS on containment; one low hygiene finding (F1).**
   `MANIFEST.json` does not exist in the lane and is untracked/unchanged; `.ufo/state/` and `.scratch/`
   do not exist (`ls -d` → No such file); no touched path leaves the lane; no credential-shaped
   material in the committed round-86 bytes (`git grep -I` for private keys, `AKIA`, `ghp_`, `glpat-`,
   `xox*-`, `sk-`, `Cookie:` → no hit). Siblings hold only their own round-86 work
   (kengaku `freeze-battery.txt` names `kengaku-r86`, mado `c1-r86.txt`). **F1 (LOW):** two seat
   reports are committed twice, byte-identically — `.ufo/waves/round-86/w1/CR01PredicateCritic.md` ==
   `w1/out/CR01PredicateCritic/CR01PredicateCritic.md` (sha256 `c439b416…`) and
   `w1/SC01SourcesRecon.md` == `w1/out/SC01SourcesRecon/SC01SourcesRecon.md` (sha256 `eedaf2bb…`) —
   against the plan's "every seat writes only its own `out/<name>/`".
3. **Authorship / lane scope — PASS.** `git log --format='%an <%ae>' 3ff23da3..bafae7af | sort | uniq -c`
   → `11 kama-shokunin <kama@shokunin.local>`; committers identical (matches `jj-lane.sh:19`).
   Per-commit path filter outside `corpus/ LOG.md SCORECARD.md plans/ PROVINCE.md registry/ tools/
   .ufo/waves/round-86/` printed nothing for all 11 commits. Three extra commits under
   `refs/jj/keep/` are jj push-recovery shadows; master is a fast-forward chain.
4. **Instrument scratch discipline — PASS (F5 LOW).** No literal `/tmp` in any of the three
   (`grep -rn '/tmp'` → only the message `could-not-evaluate: --work is required (no hardcoded /tmp)`).
   `round86-mutant-owners.py` requires `--work`, creates it, and passes `TMPDIR=<work>` to the child
   (lines 153/169/268); `round86-pin-origin.py` builds fixtures in
   `tempfile.TemporaryDirectory(prefix="r86-origin-")` (line 202); `round86-rendered-cells.py` writes
   nothing and needs no work dir. **F5:** `round86-rendered-cells.py:51` imports `tempfile` unused and
   its line-40 docstring claims `--selftest` builds trees in `$TMPDIR` (it is in-memory);
   `round86-mutant-owners.py:41` makes the same false claim.

## Other findings

- **F3 (LOW, evidence hygiene):** the terminal commit itself rewrote two committed seat receipts —
  `.ufo/waves/round-86/w1/out/SB01LessonDraft/receipts/c2.out` lost `arms=34` from its
  `DEBT_MUTANT_OWNER_PRISTINE` line, and `…/anchor-upstream-recheck.txt`'s method header changed.
  No claim flips (`measured/after/c2.out:7` still reads `pass=34 fail=0 arms=34`), but a receipt
  should be append-only; the before/after survives only inside that seat's `receipts/final.txt`.
- **F2 (LOW, unremediated from w2):** committed round-86 reports publish `/tmp` scratch commands —
  `w1/out/CN01OverlapScan/CN01OverlapScan.md:151-153`, `w2/SN01ScopeSentinel.md:183-185`,
  `w2/out/CN01OverlapScan/CN01OverlapScan.md:209-211` (`--work /tmp/c1|c2|c3`) — against the plan's
  declared scratch root `/fast/scratch/hyaku/kama-r86/<seat>/`. Guidance only; no receipt records a
  command that actually ran with `--work /tmp`.
- **Disclosed deviation, not a finding:** the plan freezes 11/10/7 selftest arms; at `bafae7af` the
  instruments carry 17/13/7 controls (11/10/7 at `c07e1f90`), disclosed in `SCORECARD.md` round-86
  ("selftest 17/0 at the terminal tree (11/0 at the freeze)") and lesson M3/M6. The three frozen
  `PREDICATE` strings are byte-identical freeze→tip (md5 `f36302bf…`, `34eeb451…`, `ae305d34…`);
  `plans/round-86-claims.md` and `count.py` are unchanged over `c07e1f90..bafae7af`.

## Environment note

Lane HEAD advanced during the audit `bafae7af` → `0f8a0980` (three lane-authored commits adding
`measured/terminal/*`, `w3-*` dispatch, record text). All verdicts above are on `bafae7af` bytes.

Tools installed: **none** (pacman paused; nothing needed). Scratch
`/fast/scratch/hyaku/kama-r86/SN01ScopeAndMisroot/` removed before yield; no `/tmp` writes.
