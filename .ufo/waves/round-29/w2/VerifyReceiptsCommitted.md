# VerifyReceiptsCommitted — C1 final receipt authenticity

Seat: `kama-r29-w2-VerifyReceiptsCommitted-3` · Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` · 2026-10-23
Full report: `.ufo/waves/round-29/w2/out/kama-r29-w2-VerifyReceiptsCommitted-3/report.md`

## Verdict

**AUTHENTIC — no divergence.** A fresh-clone rerun of the frozen counter at tip `513eba3ba51a142c9936553e3a85918345eb5c4c` produces JSON byte-identical to both `final/c1-513eba3b.json` and `final/c1-513eba3b-cleanenv.json`, and a summary line byte-identical to `final/c1-513eba3b.out` (and to line 1 of `c1-513eba3b-cleanenv.out`, whose second line is a provenance annotation). The claimed receipt
`statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True` is exactly what a clean run produces.

## Method and evidence

1. **Frozen counter integrity.** Working-tree `.ufo/waves/round-29/count-c1.py` sha256 = `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (matches contract). Tracked, unmodified in `git status --porcelain`; committed at freeze `827d1365`.

2. **Tip identity.** Lane `git rev-parse HEAD` = `513eba3ba51a142c9936553e3a85918345eb5c4c` (data commit). Fresh clone to `/tmp/kama-r29-w2-verifyreceipts-3/clone` checks out `513eba3b` detached (source HEAD is detached, jj-managed); clone `status --porcelain` empty; `HEAD:.ufo/waves/round-29/count-c1.py` blob sha256 = `fe11d599…383`.

3. **Reruns** (driver `/tmp/kama-r29-w2-verifyreceipts-3/driver.py`; writes only under `/tmp`):
   - `--tip 513eba3b…` normal env → rc=0, `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a`
   - `env -i PATH=/usr/bin:/bin HOME=/home/vgpnk` → rc=0, identical stdout (replicates `c1-513eba3b-cleanenv.out` provenance)
   - receipt: `counter_sha256=fe11d599…383 tip=513eba3b…4c4c correction_rows=11 false_corrections=[] unresolved_ids=[] met=true`; `by_class` C=27 H=2 N=2 P=10 Q=25 T=3

4. **Byte comparisons (sha256):**
   - `f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504` — final/c1-513eba3b.json = final/c1-513eba3b-cleanenv.json = my run-normal.json = my run-clean.json (all four identical)
   - `c0def613b91d7e323b7d2a22b6695934d237ada1f07518da8322d5055343408d` — final/c1-513eba3b.out = my run-normal.out = my run-clean.out
   - `3e9f7141e84098dab19b31d7c59d93c467702cc1bcbc670a1ca856fa2ceacc8e` — c1-513eba3b-cleanenv.out = same summary line + appended provenance line `env -i PATH=/usr/bin:/bin HOME=$HOME; clone of origin at 513eba3b…; counter sha256 fe11d599…`
   - No `out`/path field exists in the receipt JSON; byte-identity holds on raw bytes, not modulo normalization.

## Residual observation (not a defect in the receipt)

- Default `--tip refs/heads/master` does not resolve to the receipt's tip. Lane `refs/heads/master` was `49f849f292c338f5e4e2cc8a60eb1372a8f40412` — NOT pre-freeze: it is the operator's daily-reflection commit (committer 2026-10-23T09:21:19-03:00; adds only `considerthese/2026-10-23.md`; descendant of 513eba3b per `git merge-base --is-ancestor`). Lane HEAD is detached at `513eba3b` (jj-colocated). The default `--tip refs/heads/master` therefore evaluates 49f849f: same counts and `met True`, but `tip` token differs (`tip 49f849f292c3`) — so a default-tip run does not reproduce `c1-513eba3b.json` byte-for-byte. In a clone of a detached-HEAD source (no `refs/heads/master` created) the default exits 2 `could-not-evaluate: tip refs/heads/master unresolved` (mechanism confirmed by `kama-r29-w2-RerunCounter`; clone of the real remote exits 0). The receipt artifact is faithful at explicit tip `513eba3b`; L1 should note "at tip" = HEAD here and that lane master now sits one commit ahead of the attempt-1 base (jj will rebase the working copy on its next operation).
- Peer corroboration (`kama-r29-w2-RerunCounter`, disclosed): receipt at 513eba3b byte-identical across 3 runs, under clean env, after corrupting the clone worktree SCORECARD.md (counter reads committed objects only), and under a git replace graft (counter uses `--no-replace-objects`). Their in-lane `git fetch origin` moved lane master to 49f849f via jj auto-import; no file/index/HEAD/working-copy change.

## Environment

No installs; pacman untouched. `git 2.56.0`, `python 3.14.8`, `sha256sum`, `cmp`. Scratch left at `/tmp/kama-r29-w2-verifyreceipts-3/`. Lane repo, index, and jj state untouched.
