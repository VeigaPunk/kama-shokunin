# V7Hashes — hash-resolution audit (round 55)

**VERDICT: PASS (clean).** Every lane-repo commit hash cited in the committed round-55
artifacts resolves in the lane repo; fleet-repo and upstream citations resolve where
their format expects; the only lane-unresolvable commit-shaped tokens are the four
battery fixture-clone tips — unresolvable by design (scratch clones, `fx@invalid`
commits, scratch deleted). The counter sha256s match preregistration ↔ frozen blobs ↔
worktree bytes. No defect found.

## Method and scope

- Audit point: lane tip `bf336baa2fc039a8c003196c41a35d2661843003` (HEAD at audit
  completion). The lane moved 4 commits past the freeze `9c60eae6f7ed84f7da93d219a406aadc30958c6c`
  during this audit, so every artifact was read via `git show <rev>:<path>` — immune to
  worktree state (two `w1/out/` seat files were concurrently modified; `git show`
  sidesteps that).
- Provenance check: `preregistration.json`, `controls/base.c1.out`, `controls/base.c2.out`,
  `census/start.out` are byte-identical between `9c60eae6` and `bf336baa`. The lesson was
  modified by integration commit `c2c05e30` (Sc1 lesson fixes) and is audited in its
  current committed form; `measured/`, `c1/battery/`, `build_spec.py`, `census/end.out`,
  `hexrun-evidence/` first landed in `8abadfed`/`c2c05e30` (post-freeze, see §Artifact-set motion).
- Token rule: `[0-9a-f]{7,40}` with non-hex boundaries → `git -C <lane> cat-file -e <tok>`
  (full and abbreviated alike); lane misses retried in the fleet repo; still-missing
  classified against their citing context. Pure-digit tokens (pids, inodes, sizes,
  epochs) are recorded as `DATA:numeric`, never commit citations. 64-hex tokens are
  content digests, not commits (`digests64.tsv`); the two `counter_sha256` values are
  audited under §Counter-sha256 verification.
- Artifacts audited (all committed at `bf336baa`): `preregistration.json`,
  `corpus/lessons/round-55.md`, `controls/base.c1.out`, `controls/base.c2.out`,
  `measured/c1-build.out`, `measured/c2-build.out`, `census/{start,end}.out`,
  `c1/battery/{control,m-ldpreload,m-text-flip,m-member-flip,m-ldaudit-foreign}.out`,
  `c1/battery/run-battery.py`, `hexrun-evidence/e2e2d10f….txt` (content + filename),
  `build_spec.py`, `w1/{spec,dispatch}.json`, `w1/validate.out`,
  `w1/out/swarm-registry.json`, `sources/git-docs-git-config.html`,
  `SCORECARD.md` (the `## Round 55` section — did not exist at `9c60eae6`),
  `LOG.md` (round-55 entry), and the three cited round-48 v5 receipts
  (`.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json`).
  Out of scope per the seat list: per-seat outputs under `w1/out/<Seat>/`.

## Table 1 — lane-repo commit citations: ALL RESOLVE (`git cat-file -t` = commit)

| token | resolves to | cited in |
|---|---|---|
| `9c60eae6f7ed84f7da93d219a406aadc30958c6c` | freeze commit (round-55 w0 freeze) | measured/{c1,c2}-build.out:1; battery/control.out:1; run-battery.py:14; build_spec.py:11; spec/dispatch/validate (≈270 generated sites); swarm-registry.json |
| `9c60eae6` | same (abbrev) | LOG.md round-55 entry |
| `9c60eae` | same (abbrev) | hexrun-evidence/e2e2d10f…txt:5 ("lane rev 9c60eae") |
| `3a600d2f729828419aaea34cc402c8b0d20fb720` | base (round-54 tip) | prereg:7,10,38; lesson:19; controls/base.c{1,2}.out:1; build_spec.py:10; spec/dispatch/validate (≈80 generated sites) |
| `3a600d2f` | same (abbrev) | lesson:29,107; census/start.out:1; SCORECARD §55:60; LOG entry |
| `0b75a84c56e024cac1662e8ff81802f249acb410` | C2 counter_base (round-53 tip) | prereg:10,28; lesson:28 |
| `0b75a84c` | same (abbrev) | lesson:112,119; build_spec.py:26,76; spec/dispatch/validate; swarm-registry.json |
| `9a3104c771509df2dad6b6fe13c023bd3c472c35` | round-54 draft commit | prereg:10 (disclosure) |
| `ed135b3c` | Revert "HOURS.md…" (lane) | hexrun-evidence/e2e2d10f…txt:11; build_spec.py:120; spec/dispatch/validate |
| `e81d90e6` | round-53 integration (KQ97) | lesson:158 |
| `4a2a4d55` | round-46 append-only-audit | lesson:148 |
| `1541a0dd` | round-48 measured | lesson:164 |
| `8abadfed` | w1 dispatch/battery commit | SCORECARD §55:22 — post-freeze citation, `anc-of-freeze=no`; the §55 section itself first appears in `c2c05e30`, after FREEZE (see O4) |

## Table 2 — fleet-repo citations: resolve in the FLEET repo, never the lane (by design)

| token | where | resolution |
|---|---|---|
| `6c4aba34c2a22519152d8c6f32e1039eecb1381b` | `fleet=` field, controls/base.c2.out:1, measured/c2-build.out:1 | fleet commit "round-56: mori dispatch evidence" (10:08 UTC) — fleet HEAD at measurement time, predates the 13:24-UTC freeze; consistent |
| `e2e2d10f` | SCORECARD §55:60,62; LOG entry | fleet commit "round-54: kama honest-stop report + ed135b3c L0 forward" (abbrev of below) |
| `e2e2d10fe4801d7a846e22e5f84cc1a8e133c4e0` | hexrun-evidence filename + lines 1,8,10,… | same fleet commit; the evidence file documents the lane's citation of the fleet commit |

These cite fleet-repo history by contract (C2's upstream rows pin fleet commits; the
seat's own item text acknowledges "fleet rev may differ") — not lane citations, so a
lane `cat-file -e` miss is correct.

## Table 3 — upstream external citations: resolve upstream, never in lane/fleet

| token | where | upstream resolution |
|---|---|---|
| `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` | census/{start,end}.out W04 rows (SOURCES url cells); round-48 receipts' server provenance + raw.githubusercontent URLs (181 sites) | llama.cpp pinned commit — `raw.githubusercontent.com/…/704366d7…/tools/server/server.cpp` → HTTP 200 |
| `499bc8821c6b12b4e53c5bffcb21ec206f212d81` | round-48 receipts `commit` fields + HF resolve URL (6 sites) | `huggingface.co/ggml-org/models-moved/resolve/499bc882…` → HTTP 302 → CDN (exists) |
| `caa8191df` | round-48 receipts `"build_info": "b11909-caa8191df"` (6 sites) | GitHub API resolves → `caa8191df159f764fb0160e3d2fc6be008948aee` |

## Table 4 — unresolvable BY DESIGN: battery fixture tips

Four `tip=` values in `c1/battery/m-*.out:1` fail `cat-file -e` in lane AND fleet (rc≠0):

| receipt | tip (1st line) |
|---|---|
| `m-ldpreload.out:1` | `585a6cb04c3b744157a76e772469d687f35f89ea` |
| `m-text-flip.out:1` | `a12e2c0fbab50832d5321ab1f0c77c5e04a036ac` |
| `m-member-flip.out:1` | `ba085a8bcaf9fc55bcd3d19249179df189ff307e` |
| `m-ldaudit-foreign.out:1` | `aa3c47cda04313221b3018520c4463a7d3ff23d4` |

By construction: `run-battery.py:118-135` runs `git reset --hard FREEZE` in a
`--shared` scratch clone, applies one mutant to `tools/kama-llamacpp-live.py`, commits
with `-c user.name=fx -c user.email=fx@invalid`, and records `rev-parse HEAD` as the
tip; the harness deletes the scratch on exit (`:147`). The hash is a receipt label for
an ephemeral fixture commit — the mutant's content is defined by the committed
`MUTANTS` diff, not by any resolvable object.

## Table 5 — non-commit hex data (excluded from commit resolution; full lists in citations.tsv / digests64.tsv)

- 60 `DATA:*` tokens: 7-digit pids, 8–10-digit inodes/sizes/epochs, 16-hex
  `kama witness …` nonces and memfd-inode tokens inside C1 receipts — runtime values,
  never cited as commits.
- 75 distinct 64-hex tokens: receipt content digests (archive members, model blob,
  `e3b0c44…` empty-string hash) plus the two preregistration `counter_sha256` values.
- `sources/git-docs-git-config.html`: `deadbee`/`fa1afe1` (git-config(1)
  `hasconfig`/`onbranch` doc-example commit placeholders — unresolvable, correct) and
  numeric doc constants (`1048576`, `1073741824`, `16777215`).

## Counter-sha256 verification (seat second half)

- `preregistration.json:16` `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`
  == `sha256(git show 9c60eae6:tools/round54-replay-code-audit.py)` ==
  `sha256(tools/round54-replay-code-audit.py)` worktree bytes. ✓
- `preregistration.json:27` `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c`
  == `sha256(git show 9c60eae6:tools/round54-cited-path-check.py)` ==
  `sha256(tools/round54-cited-path-check.py)` worktree bytes. ✓
  The kill-rule byte-binding ("counter bytes at measurement differ from
  `counter_sha256`") is intact at the current tip.
- **The lesson quotes zero sha256s** — `git show HEAD:corpus/lessons/round-55.md |
  grep -cE 'sha256|digest'` → `0`. The seat text's "quoted in the lesson" is vacuous:
  preregistration is the only audited artifact quoting the digests (observation O1);
  verified against blobs anyway.
- Adjacent artifact (outside seat list): `SKILL.md:1611-1612` registry rows quote the
  same digests in truncated `c81fe971…79af` / `d70a1729…6510` form — prefix and suffix
  consistent with preregistration.

## Findings

No claim-falsifying defect and no conformance defect. Observations:

- **O1 (info).** The seat spec's "counter sha256s quoted in the lesson" does not apply:
  `corpus/lessons/round-55.md` contains no sha256/digest mention at all. The
  preregistration ↔ blob ↔ worktree equivalence above is the substantive check and it
  passes.
- **O2 (info).** The battery roster changed post-freeze: `8abadfed` carried six mutant
  receipts; `git diff --name-status 8abadfed HEAD` shows `m-ldaudit-writable.out` and
  `m-extra-in-tree.out` deleted by `c2c05e30` (SCORECARD §55 calls them "two stale
  first-run receipts deleted at integration"). Their fixture tips
  (`23dc15dae…`, `312530a9…`) were likewise unresolvable-by-design; nothing dangling
  remains in the committed set. The prereg↔roster divergence itself is the kill-rule
  question other seats own, not a hash defect.
- **O3 (residual).** Fixture-tip hashes are unverifiable-by-hash by construction —
  replaying a mutant yields a different commit (timestamps/identity), so the committed
  harness's `MUTANTS` table is the only ground truth for what each tip contained.
  Acceptable by design; noted for the closure.
- **O4 (info).** `SCORECARD.md` §55 cites `8abadfed`, the commit that landed the
  receipts/battery — a post-freeze citation (not an ancestor of `9c60eae6`). It
  resolves in the lane repo at the audit tip, satisfying `cat-file -e`; flagged only
  because the seat's wording pins "at 9c60eae6". The §55 section itself did not exist
  at the freeze commit (first appears in `c2c05e30`), consistent with "if present".

## Residual risk / verification gaps

- Upstream checks are existence-only (HTTP 200/302, API `sha`); bytes were not
  fetched/compared — V4Receipts/S1Source511 own content-level verification.
- I did not rerun either counter (X1Rerun/X2C2Rerun/V3Freeze seats own reruns); this
  audit is hash-resolution/identity only.
- `w1/out/<Seat>/` files are per-seat workspaces, excluded per the seat's artifact
  list (`swarm-registry.json` included as wave infrastructure).
- No tools installed (stock git/python3/curl only; pacman untouched per the pause).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/V7Hashes.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/V7Hashes/evidence.txt` (verbatim command transcript: resolutions, ancestry, upstream probes, sha256 outputs, roster diff)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/V7Hashes/citations.tsv` (every commit-shaped token × class × all sites @ `bf336baa`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/V7Hashes/digests64.tsv` (64-hex non-commit tokens × sites)
