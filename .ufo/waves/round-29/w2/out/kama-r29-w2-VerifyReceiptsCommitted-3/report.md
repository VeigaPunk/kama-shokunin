# VerifyReceiptsCommitted — C1 final receipt authenticity

Seat: `kama-r29-w2-VerifyReceiptsCommitted-3` · Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` · 2026-10-23

## Verdict

**AUTHENTIC — no divergence.** A fresh-clone rerun of the frozen counter at tip `513eba3ba51a142c9936553e3a85918345eb5c4c` produces JSON byte-identical to both `final/c1-513eba3b.json` and `final/c1-513eba3b-cleanenv.json`, and a summary line byte-identical to `final/c1-513eba3b.out` (and to line 1 of `c1-513eba3b-cleanenv.out`, whose second line is a provenance annotation). The claimed receipt
`statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True` is exactly what a clean run produces.

## Method and evidence

1. **Frozen counter integrity.** Working-tree `.ufo/waves/round-29/count-c1.py` sha256 = `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (matches contract). The file is tracked and unmodified (not in `git status --porcelain` output; committed at freeze `827d1365`).

2. **Tip identity.** `git rev-parse HEAD` in the lane = `513eba3ba51a142c9936553e3a85918345eb5c4c` (data commit; ancestors `827d1365` → `35b90184` → `513eba3b`). A fresh clone (`git clone -q <lane> /tmp/kama-r29-w2-verifyreceipts-3/clone`) checks out `513eba3b` (detached HEAD — the source's HEAD is detached, jj-colocated); `git status --porcelain` in clone = empty; blob `HEAD:.ufo/waves/round-29/count-c1.py` sha256 = `fe11d599…383` (the frozen counter is what the clone carries).

3. **Reruns** (driver `/tmp/kama-r29-w2-verifyreceipts-3/driver.py`; runs write only under `/tmp`):
   - `--tip 513eba3b…` normal env → rc=0, stdout `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a`
   - `env -i PATH=/usr/bin:/bin HOME=/home/vgpnk /usr/bin/python3 …` (replicating `c1-513eba3b-cleanenv.out` provenance line) → rc=0, identical stdout
   - receipt fields: `counter_sha256=fe11d599…383 tip=513eba3b…4c4c statements=69 mismatched_at_base=11 append_only=true correction_rows=11 valid_corrections=11 false_corrections=[] unresolved=0 met=true`

4. **Byte comparisons** (`sha256sum` / `cmp`):
   | file | sha256 |
   |---|---|
   | final/c1-513eba3b.json | `f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504` |
   | final/c1-513eba3b-cleanenv.json | `f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504` |
   | my run-normal.json / run-clean.json | `f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504` (both) |
   | final/c1-513eba3b.out | `c0def613b91d7e323b7d2a22b6695934d237ada1f07518da8322d5055343408d` |
   | my run-normal.out / run-clean.out | `c0def613b91d7e323b7d2a22b6695934d237ada1f07518da8322d5055343408d` (both) |
   | final/c1-513eba3b-cleanenv.out | `3e9f7141e84098dab19b31d7c59d93c467702cc1bcbc670a1ca856fa2ceacc8e` — differs only by its second (provenance) line: `env -i PATH=/usr/bin:/bin HOME=$HOME; clone of origin at 513eba3b…; counter sha256 fe11d599…` |

   - No `out`/path field exists in the receipt JSON (checked); the "ignore out path" allowance was vacuous — raw bytes are identical, not merely equal modulo a field.
   - `by_class` totals: C=27 H=2 N=2 P=10 Q=25 T=3 (sums to 69); `unresolved_ids=[]`; `false_corrections=[]`; `mismatches` lists the same 11 sids the correction rows resolve (first: `SCORECARD.md:Q:f4c42debcc:0` @ line 20, `observed=q:no-artifact`).

## Residual observations (not defects)

- **Default `--tip refs/heads/master` does not resolve to the receipt's tip.** At the time of this review the lane's `refs/heads/master` was `49f849f292c338f5e4e2cc8a60eb1372a8f40412` — this is NOT pre-freeze: it is the operator's daily-reflection commit (committer 2026-10-23T09:21:19-03:00, adds only `considerthese/2026-10-23.md`, and is a descendant of 513eba3b per `git merge-base --is-ancestor`). Lane HEAD is detached at `513eba3b` (jj-colocated). The counter's default `--tip refs/heads/master` therefore evaluates 49f849f, not 513eba3b: same counts and `met True`, but the `tip` token differs (`tip 49f849f292c3`), so a default-tip run does not reproduce `c1-513eba3b.json` byte-for-byte. In a clone of a detached-HEAD source (no `refs/heads/master` is created), the default exits 2 `could-not-evaluate: tip refs/heads/master unresolved` — mechanism confirmed by `kama-r29-w2-RerunCounter` (clone of the real remote resolves master and exits 0). The receipt artifact itself is faithful at explicit tip `513eba3b`; the L1 should note that "at tip" = HEAD here, and that the lane's master now sits one commit ahead of the attempt-1 base (jj will rebase the working copy onto master on its next operation).
- `c1-513eba3b-cleanenv.out`'s second line is provenance text, not counter output — expected, documents `env -i` scrub; replicated and consistent.
- Peer corroboration (`kama-r29-w2-RerunCounter`, disclosed): receipt at 513eba3b is byte-identical across 3 runs, under clean env, after corrupting the clone's worktree SCORECARD.md (the counter reads committed objects only), and under a git replace graft (the counter uses `--no-replace-objects`). Their in-lane `git fetch origin` (15:24:39 -0300) is what moved lane master to 49f849f via jj auto-import; no file/index/HEAD/working-copy change.

## Tools / environment

- No installs; pacman untouched. Used: `git 2.56.0`, `python 3.14.8` (`/usr/bin/python3`), `sha256sum`, `cmp`.
- Scratch: `/tmp/kama-r29-w2-verifyreceipts-3/` (clone + driver + run-*.json/out); lane repo untouched, index/jj state untouched.
