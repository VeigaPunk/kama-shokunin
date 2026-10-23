# RerunCounter — round 29, wave 2 (kama lane), attempt 2

Seat: `kama-r29-w2-RerunCounter` (executor). Claim served: **C1 (calibration) — counter and receipts**.
Scratch clones: `/tmp/kama-w2-rerun-RerunCounter*` (unique per seat; nothing outside them touched).

## Verdict

**PASS — the inherited C1 receipt reproduces byte-for-byte at the claimed tip, and the claimed summary
line is confirmed verbatim.** Three defects/risks are reported below for the L1; none of them changes
the C1 verdict at the frozen tip, but two are forward-looking (they will bite the *next* round).

## 1. The assigned check (fresh clone, run the frozen counter)

Exactly the item's command, on a fresh clone of the lane repo:

```
$ git clone --no-local /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-w2-rerun-RerunCounter
$ cd /tmp/kama-w2-rerun-RerunCounter
$ /usr/bin/python3 .ufo/waves/round-29/count-c1.py \
      --repo /tmp/kama-w2-rerun-RerunCounter --tip refs/heads/master --out receipt.json
```

**Summary line, verbatim (stdout):**

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a
```

- Expected string `statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True` — **confirmed** as an exact prefix; the line continues ` tip 513eba3ba51a`, i.e. **tip prefix `513eba3b` — confirmed**.
- **Counter sha256 in the clone = `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`** — confirmed. Identical to the lane worktree copy, to `git show 827d136:.ufo/waves/round-29/count-c1.py`, and to `git show 513eba3:.ufo/waves/round-29/count-c1.py` (all three sha256 equal; the counter is unchanged across freeze → data).
- **Clone tip = `513eba3ba51a142c9936553e3a85918345eb5c4c`** — confirmed (`git rev-parse HEAD refs/heads/master` in the clone both give it; `HEAD` → `refs/heads/master`).
- Exit code **0**.
- **Receipt is byte-identical to the lane's own committed-attempt artifact**
  `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/final/c1-513eba3b.json`
  — both sha256 `f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504`, `diff` empty.
  Same for `final/c1-513eba3b-cleanenv.json`.
- Saved copies of my receipts:
  `.ufo/waves/round-29/w2/out/kama-r29-w2-RerunCounter/receipt-fresh-clone-513eba3b.json` (sha256 `f3c7a439…dd504`),
  `…/receipt-fresh-clone-origin-tip-49f849f2.json`,
  `…/receipt-base-2aa46e24.json`.

## 2. Adversarial probes (all read-only; lane untouched)

| Probe | Result | Evidence |
|---|---|---|
| Determinism: 3 runs, different `--out` | **byte-identical**, sha256 `f3c7a439…dd504` each | `/tmp/kama-w2-rerun-RerunCounter/r1.json r2.json r3.json` |
| Clean environment `env -i PATH=/usr/bin:/bin HOME=$HOME`, fresh clone | **byte-identical** | `/tmp/kama-w2-rerun-RerunCounter-clean/receipt.json` |
| Worktree corruption: appended a junk `\| SA29:fake:0 \|` row to the **clone's** `SCORECARD.md` | receipt **unchanged** (counter reads committed objects only) | `r_wt.json` sha256 = `f3c7a439…dd504` |
| `git replace --graft` on the tip | receipt **unchanged** (counter uses `--no-replace-objects`) | `r_replace.json` identical |
| Base tip `--tip 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` | `… valid_corrections 0 false_corrections 0 unresolved 11 met False` — **before-state confirmed** | `r_base.json` |
| Freeze tip `827d136546b85059a984b34970f5b493d9a71290` | `… unresolved 11 met False` | `r_827d136….json` |
| Controls tip `35b90184` | `… unresolved 11 met False` | `r_35b90184….json` |
| Base receipt vs lane `before/c1-base.json` | **identical** including the full 69-entry `all_statements` (needs `--list`) | `base_list.json` |
| Correction rows ↔ counter mismatches | **exact 1:1**: 11 rows, 11 mismatch sids, every last cell equals the counter's observed string, no duplicate sids | script cross-check |
| Injected a false correction row (a holding statement) | detected: `false_corrections 1 unresolved 1 met False` | `/tmp/kama-w2-rerun-RerunCounter-why/r_falsecorr.json` |
| Amending only the "why" prose cells (observed values untouched) | `met True` preserved — prose edits are safe | `/tmp/kama-w2-rerun-RerunCounter-why/` |
| 14 control receipts re-read | 13 `Ctl*` all `met False`; `RefPaste` (the reference policy) `met True` — matches `controls/SUMMARY.md` | `controls/*/receipt.json` |

No tool was installed (none needed); no pacman transaction was run.

## 3. Defects and risks for the L1 (I did not fix any of these — lane files are read-only for me)

### D1 (MATERIAL, forward-looking) — the correction table re-creates the very defect class it corrects

The four **P-class** correction rows quote the failing pointer *token* verbatim in their "statement
token" cell:

```
| SA29:SCORECARD.md:P:980355388a:0 | SCORECARD.md:192 | P | `MISSION.md:29` | 1e41928a | … | p:absent |
| SA29:SCORECARD.md:P:312b3e69b1:0 | SCORECARD.md:740 | P | `round-17-verifier-spotcheck.md:217–221` | c6dc46fa | … | p:absent |
| SA29:SCORECARD.md:P:1c6c1f3e4c:0 | SCORECARD.md:1349 | P | `.ufo/reports/round-25/kama.md:120-129` | 7f84cd0e | … | p:absent |
| SA29:SCORECARD.md:P:17a7db7c81:0 | SCORECARD.md:1375 | P | `count-c1.py:384` | d183ec57 | … | p:absent |
```

Those backticked tokens are themselves extracted by the frozen extractor (`RE_P` matches
`` `path:N` `` anywhere on a line) at the **next** base. I ran the frozen extractor with
`BASE = 513eba3b` (the round-29 data commit) against a clone: **93 statements, 15 false at writing —
the original 11 plus 4 new ones at SCORECARD.md lines 1456, 1458, 1463, 1464**, all `p:absent`,
all written by W = `513eba3b` itself. The next round's counter would therefore see 15 mismatches, and
round 29's 11 rows do not cover the 4 new ones.

**Mitigation I measured (not applied):** rewriting only the token cell so the path is not followed by
`:N` — `` `MISSION.md` line 29 ``, `` `count-c1.py` line 384 ``, `` `.ufo/reports/round-25/kama.md` lines 120–129 ``,
`` `round-17-verifier-spotcheck.md` lines 217–221 `` — drops the next-base false count from 16 to 12
(the 4 P rows disappear; the observed-value cells and the `SA29:` sids are untouched, so the
round-29 receipt itself is unaffected: `met True` was preserved in an equivalent probe). Note the
predicate is frozen and must not be amended; this is a **prose-format** change to the correction
table, not a counter change.

### D2 (MATERIAL, forward-looking) — the attempt-1 `SHONEN.md` edit introduces a NEW false-at-writing statement

`SHONEN.md` (attempt-1 worktree edit, line 8) replaces the old wording with a quoted span of 195
chars that the extractor classifies as **class Q**:

```
 (8 adverse controls rejected: 7 bad server shapes + 1 injected teardown fault; frozen accepted-bad = 6 (5 accepted bad receipts + 1 receiptless escape), with K3 inconclusive; corrected round 29,
```

It contains a digit and `=`, is not a command prefix, so `RE_Q` picks it up; and it occurs **only in
`SHONEN.md` itself**, which class Q excludes — so it is `q:no-artifact` at its writing revision.
Measured at the simulated next base: `SHONEN.md:Q:030767d70a:0`, line 8, `q:no-artifact`, with **no
`SA29:` row** to cover it. The base `SHONEN.md` line 8 has **no** Q candidate at all (the old wording
is not backticked), so this false statement is **introduced by the attempt-1 edit**, and it lands on
the axis this round is about. The same edit is what fixes the "8 bad fake-server shapes" wording gap,
so it should not simply be reverted; the fix is to phrase it without a backticked `=N` span, or to
record a correction row for it.

### D3 (MINOR, citation hygiene in the attempt-1 leftovers) — three relative path citations do not resolve from the lane root

| Citation | Resolves? |
|---|---|
| `before/c1-base.out` (SCORECARD.md:1475, LOG.md round-29 block) | **DANGLING** — real path is `.ufo/waves/round-29/before/c1-base.out` |
| `final/c1-513eba3b.out` (SCORECARD.md:1475, LOG.md:1841) | **DANGLING** — real path is `.ufo/waves/round-29/final/c1-513eba3b.out` |
| `w1/out/ExecTimingTranscript/` (LOG.md:1848) | **DANGLING** — real path is `.ufo/waves/round-29/w1/out/ExecTimingTranscript/` |

The same three targets (`corpus/knowledge/self-assessment-at-writing.md`, `corpus/lessons/round-29.md`,
`.ufo/waves/round-29/final/c1-513eba3b.out`) are **untracked** in the lane right now. If the L1 lands
the SCORECARD/LOG/SOURCES narrative without landing those files, the landed SCORECARD cites paths that
do not exist in the committed tree — a new P-class false pointer written by the correction round
itself (I simulated that: the narrative-only commit still yields `met True` **for this round**, but
the pointers are dangling). Landing the narrative and its cited files in the same commit closes this.

### D4 (INFORMATIONAL, no action needed) — the pushed tip moved past the data commit; the receipt is unaffected

`origin/master` is now `49f849f292c338f5e4e2cc8a60eb1372a8f40412` ("considerthese: 2026-10-23 daily
reflection", committer date `2026-10-23T09:21:19-03:00`), a **descendant** of `513eba3b` that adds
only `considerthese/2026-10-23.md` and touches neither `SCORECARD.md` nor `SHONEN.md`. A fresh clone of
the real remote gives the identical counts with a different tip token:
`statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 49f849f292c3`.
So the claim as stated ("the fresh-clone receipt at the pushed tip reads … tip prefix 513eba3b") is
true of the **data commit** and of the lane's local `master` at freeze time; against the live remote
today the tip token is `49f849f2`. All metric fields are identical, so nothing in the claim's substance
changes. The L1 should decide which tip the landed narrative names.

**Disclosure — my footprint on lane state:** to answer (D4) I ran `git fetch origin` inside the lane
repo (15:24:39 -0300). That fast-forwarded `refs/remotes/origin/master` to `49f849f`, and jj's
colocated auto-import (`jj op log` top op: `import git refs`) advanced the jj `master` bookmark and
`refs/heads/master` from `513eba3b` to `49f849f`. **No file, index, `HEAD` or working-copy content
changed**: `git status --short` shows the same 6 modified + 9 untracked attempt-1 paths as before,
`git diff --cached` is empty, `HEAD` is still detached at `513eba3b`, and the counter sha256 is still
`fe11d599…7383`. No `git add/commit/checkout/reset` was run in the lane; the jj working copy `@`
(`914d797e`, parent `513eba3b`) is untouched. The L1 must know `master` now sits one commit ahead of
the attempt-1 working copy's base, so jj will rebase `@` onto `49f849f` on its next operation.

**Lane-write discipline:** I wrote only inside
`.ufo/waves/round-29/w2/out/kama-r29-w2-RerunCounter/` and this report file
`.ufo/waves/round-29/w2/RerunCounter.md`. No lane source file, `.ufo/state/`, `MANIFEST.json`,
fleet script or template was edited. All scratch clones live under `/tmp/kama-w2-rerun-RerunCounter*`.

## 4. What the L1 should do

1. Land the attempt-1 narrative **together with** the files it cites (`corpus/knowledge/self-assessment-at-writing.md`,
   `corpus/lessons/round-29.md`, `.ufo/waves/round-29/final/c1-513eba3b.out`) and with the three
   relative paths rewritten to lane-root-relative form (D3).
2. Re-word the four P-row token cells to drop the `:N` suffix (D1) — measured to remove the 4
   next-base false pointers with no effect on the round-29 receipt.
3. Re-word the new `SHONEN.md` line-8 span so it is not a class-Q candidate, or add its correction row (D2).
4. Re-run the frozen counter after landing, at the landed tip, and record the receipt in
   `.ufo/waves/round-29/final/` alongside the narrative that cites it. Do not amend the frozen counter
   or the predicate (kill rule).

## 5. Exact commands a verifier can re-run

```
git clone --no-local /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-verify-rerun
cd /tmp/kama-verify-rerun
sha256sum .ufo/waves/round-29/count-c1.py        # fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383
git rev-parse HEAD refs/heads/master             # 513eba3ba51a142c9936553e3a85918345eb5c4c
/usr/bin/python3 .ufo/waves/round-29/count-c1.py --repo /tmp/kama-verify-rerun \
    --tip refs/heads/master --out receipt.json
sha256sum receipt.json                           # f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504
```

Note for a verifier cloning the **live remote** (`https://github.com/VeigaPunk/kama-shokunin.git`):
`refs/heads/master` resolves to `49f849f2…` and the counts are unchanged. Note also that a clone of
the **lane working directory** (whose git `HEAD` is detached, as jj leaves it) has **no**
`refs/heads/master`; use `--tip refs/remotes/origin/master` there, or the counter exits 2 with
`could-not-evaluate: tip refs/heads/master unresolved` (verified, exit code 2).
