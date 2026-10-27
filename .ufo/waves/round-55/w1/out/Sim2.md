# Sim2 — Round-55 wave-evidence minimality review (kama, w1)

**Verdict: lean — 22 files / 1,495,293 B, nothing over 1 MiB, and the single content-free file is `w1/validate.out` (187,305 B, byte-identical to `w1/dispatch.json`); the one real defect is commit drift in the dispatch text, which names `measured/` and `c1/battery/` as already landed at 9c60eae6 when they land at 8abadfed.**

## Scope and method

- Reviewed commit: `9c60eae6f7ed84f7da93d219a406aadc30958c6c` (round-55 w0 freeze) and the commit that actually carries the wave payload, `8abadfed` (`round-55 w1: build measurements green at freeze … dispatch + ready`), both against base `3a600d2f729828419aaea34cc402c8b0d20fb720`.
- One `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` in `/fast/scratch/hyaku/kama-r55/w1/Sim2`; `git rev-parse --show-toplevel` printed that clone. No lane file written, no index touched, no counter run, no service started.
- Sizes are git blob sizes (`git ls-tree -r -l <rev> -- .ufo/waves/round-55/`); digests are sha256 over `git cat-file blob` output, so they are independent of any live worktree state (`manifest.tsv`).

## Inventory

At the cited commit `9c60eae6` — **5 files, 858,956 B**:

| bytes | path (under `.ufo/waves/round-55/`) | disposition |
|---|---|---|
| 830,605 | `sources/git-docs-git-config.html` | keep byte-exact |
| 13,314 | `census/start.out` | keep byte-exact |
| 8,206 | `preregistration.json` | keep byte-exact |
| 3,552 | `controls/base.c1.out` | keep byte-exact |
| 3,279 | `controls/base.c2.out` | keep byte-exact |

Added by `8abadfed` (17 more files) — **22 files total, 1,495,293 B**; the full row-by-row table with sha256 and citation is `disposition.tsv`, the hashed listing is `manifest.tsv`. The additions are `build_spec.py` (43,270), `c1/battery/` (8 files, 35,252), `measured/c1-build.out` (3,561), `measured/c2-build.out` (3,163), `w1.ready` (148), `w1/spec.json` (89,773), `w1/dispatch.json` (187,305), `w1/out/swarm-registry.json` (86,472), `w1/validate.out` (187,305), `w1/validate.stderr` (0).

## 1 MiB threshold

```
$ git -C $S/lane ls-tree -r -l 8abadfed -- .ufo/waves/round-55/ | awk '$4>1048576 {print $4"\t"$5}'
(no output)
$ find .../.ufo/waves/round-55 -type f -size +1M -printf '%s\t%p\n'
(no output)
```

Nothing in the round exceeds 1 MiB; the largest object is the 830,605 B HTML (96.7 % of the freeze commit's bytes, 55.5 % of the wave commit's). It stays: `corpus/SOURCES.md:264` cites "HTML copy `.ufo/waves/round-55/sources/git-docs-git-config.html`" as the audit object for the S511 quote, `corpus/lessons/round-55.md:34` cites it again, the copy is the live page (`grep -c GIT_CONFIG_COUNT` → 3, file ends `</body></html>`), and its blob is unique in the tree (`ls-tree -r 9c60eae6 | grep <blob>` → one path), so it is not derivable from another lane file and a re-fetch would not be the bytes the quote was taken from.

## What is genuinely derivable

**(a) `w1/validate.out` — the only content-free file in the wave dir.** `cmp w1/dispatch.json w1/validate.out` exits 0, and at the commit `git cat-file blob 8abadfed:…/validate.out | cmp - <(… dispatch.json)` prints `IDENTICAL_AT_COMMIT`; both are sha256 `6201d193…`. It carries zero information beyond dispatch.json plus the validator's exit status. Cost: 187,305 B = 12.5 % of the wave dir. No round-55 document cites it; the name is a cross-round convention (`corpus/lessons/round-50-verifier-spotcheck.md:28`, `round-51-…:32`, `round-52-…:31` read `validate.out` for `exit=0` and the dispatch schema/counts). Proposed, not applied: replace it with a ≤300 B receipt (`{"cmd":…,"exit":0,"dispatch_sha256":"6201d193…","spawn":64}`) or cite `dispatch.json` plus that hash — the verifier readings in those three lessons survive such a receipt, but changing a convention mid-round is not worth 187 KB inside a frozen snapshot.

**(b) `w1/out/swarm-registry.json` — 86,472 B, of which 71,691 B is prompt prose.** Per member (`kind, agentId, role, item, axes, milestone`), `item` is byte-identical to `dispatch.registry.members[].item` for 64/64 names and to `spec.json` items (`sorted(...)` sets equal). Only `agentId` is new information. A registry of `name → agentId/role` would be ~15 KB.

**(c) inside `w1/dispatch.json`: 156,136 of 187,305 B (83.4 %) is prompt text that already lives in `spec.json`** — 71,691 B in `registry.members[].item`, 84,445 B again in `taskCall.tasks[].task` (each task = item text + ~199 chars of framing). Total prompt-prose footprint across `spec.json`/`dispatch.json`/`swarm-registry.json` is 299,518 chars (~293 KiB) for one 64-seat set. This is the swarm harness's payload shape, not lane evidence: deleting it would change the dispatch contract, so it is a harness-level observation only.

**(d) `w1/validate.stderr` is 0 B** (sha256 `e3b0c442…`, the empty-blob hash) — carries only "nothing on stderr". Free to keep, free to drop.

**(e) `w1.ready.partial` — 944 B, untracked in the live tree, absent from every commit** (`git status --porcelain` → `?? .ufo/waves/round-55/w1.ready.partial`). Atomic-write leftover; `w1.ready` (148 B, committed) is the real marker. Delete candidate for the L1.

Everything else is a distinct 3–13 KB receipt. `measured/c1-build.out` and `c1/battery/control.out` both being 3,561 B is a coincidence of format, not duplication: sha256 `4f8f277b…` vs `8f8bbf60…`, and the diff is pid/port/dev:inode/nonce only — two real runs (measurement and positive control), both required by the frozen kill rule. The battery receipts, `census/start.out`, the two `controls/*.out`, `preregistration.json` and `build_spec.py` are each single-copy and cited (`preregistration.json:40,45`; `corpus/lessons/round-55.md:73,100`), so no deletion there.

## Defect: the freeze commit does not carry the evidence its own dispatch text names

`.ufo/waves/round-55/build_spec.py:24` (the `CONTEXT` string, also line 24's `{MEAS}/…`/`{BAT}/` citations on lines 25–26) says the build "already landed at lane commit `{FREEZE}`", and every one of the 64 seat prompts in `w1/dispatch.json` repeats that sentence. Those paths do not resolve there:

```
$ for p in measured/c1-build.out measured/c2-build.out c1/battery/control.out build_spec.py w1/spec.json; do
    git -C $S/lane cat-file -e 9c60eae6:.ufo/waves/round-55/$p && echo PRESENT || echo ABSENT; done
ABSENT  .ufo/waves/round-55/measured/c1-build.out
ABSENT  .ufo/waves/round-55/measured/c2-build.out
ABSENT  .ufo/waves/round-55/c1/battery/control.out
ABSENT  .ufo/waves/round-55/build_spec.py
ABSENT  .ufo/waves/round-55/w1/spec.json
```

A seat instructed to read the C1/C2 measurement or the battery "at the build commit" gets a `git show` failure; they resolve only at `8abadfed`. This is the minimality mirror: a pointer must resolve at the commit it names, and this one is off by one commit. (The frozen `preregistration.json:45` `receipt_dir` is *not* the same defect — a preregistration names where its receipts will be written, by design.)

Proposed fix, `proposed-context-fix.diff` (against `build_spec.py`, not applied):

```diff
--- a/.ufo/waves/round-55/build_spec.py
+++ b/.ufo/waves/round-55/build_spec.py
@@ -10,4 +10,5 @@
 BASE = "3a600d2f729828419aaea34cc402c8b0d20fb720"
 FREEZE = "9c60eae6f7ed84f7da93d219a406aadc30958c6c"
+EVIDENCE_COMMIT = "8abadfed"  # lane commit carrying .ufo/waves/round-55/measured/ and c1/battery/; set before rebuilding
 SCR = "/fast/scratch/hyaku/kama-r55"
 C1CTR = f"{L}/tools/round54-replay-code-audit.py"
@@ -22,5 +23,5 @@
 CONTEXT = f"""# Goal
-Round 55 for lane kama (local model serving and endpoint health). One v2 wave (attack + verification together); the build already landed at lane commit {FREEZE} (preregistration {PR} - claims, predicates, kill rules, counter sha256s). Base {BASE} (round-54 lane tip). Two claims, frozen before data:
+Round 55 for lane kama (local model serving and endpoint health). One v2 wave (attack + verification together); the freeze landed at lane commit {FREEZE} (preregistration {PR} - claims, predicates, kill rules, counter sha256s); the measurement and battery receipts named below landed one commit later, in {EVIDENCE_COMMIT}, and do not resolve at {FREEZE}. Base {BASE} (round-54 lane tip). Two claims, frozen before data:
```

## Corroboration gathered on the way

- Counter digests at the freeze match the frozen preregistration: `tools/round54-replay-code-audit.py` → `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` (= C1 `counter_sha256`), `tools/round54-cited-path-check.py` → `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c` (= C2 `counter_sha256`).
- The C2 measurement is byte-reproducible: a peer seat's independent replays (`w1/out/X2C2Rerun/rep{1,2,3}-tip9c60eae.out`) are sha256-identical to `measured/c2-build.out` (`bc59e5e1…`), and its base replays are identical to `controls/base.c2.out` (`d6a6f550…`). Those copies are that seat's deliverables, so no wave-dir consequence — but they mean the receipts need no redundancy allowance of their own.

## Answer to the question asked

The wave dir is **lean, not derivable-stuffed**: 1.5 MB across 22 files, no blob over 1 MiB, the only large object (830 KB HTML) is a cited, non-derivable audit copy, and every receipt is single-copy, distinct, and cited. The derivable weight that remains is entirely harness payload — `validate.out`'s 187 KB byte-identical copy, the 86 KB registry mostly repeating prompt text, and the 156 KB of prompt prose inside `dispatch.json` — 429,913 B (28.7 %) of the wave dir, none of which changes what a verifier can conclude, and none of which is safely removable from the lane without changing the swarm harness or a three-round receipt convention. The one thing worth fixing now is the stale commit stamp at `build_spec.py:24`, because it makes 64 seat prompts point at paths that do not exist at the commit they name.

**Tradeoff:** `validate.out` earns its 187 KB only as a convention-shaped receipt; shrinking it would be a one-round harness change with a small risk that a future verifier greps it for the dispatch schema instead of reading the new receipt. Keeping it costs 12.5 % of the wave dir; nothing downstream is harmed either way.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim2.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim2/manifest.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim2/disposition.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim2/duplicates.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sim2/proposed-context-fix.diff`

No tool installed or upgraded (no pacman transaction attempted); no counter run; no service started; scratch `/fast/scratch/hyaku/kama-r55/w1/Sim2` removed before reporting.
