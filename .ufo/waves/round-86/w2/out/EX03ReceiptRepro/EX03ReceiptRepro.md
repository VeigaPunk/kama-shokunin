# EX03ReceiptRepro — round-86 w2: independent after-receipt reproduction (attack seat)

Seat EX03ReceiptRepro (leaf executor; no dispatches made, no installs performed). Date 2026-11-04.
Revision measured: `67eddac89f44e768b670301ea0feff06e766f32d` — verified `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD` printed exactly this at measurement time and `cat-file -t` = `commit`.
Ancestry: base `3ff23da3…` and freeze `c07e1f90…` are both ancestors of the tip (`git merge-base --is-ancestor` rc=0 for each).
Instruments and frozen counter unchanged between freeze and tip: `git -C <repo> diff --stat c07e1f90… 67eddac8… -- tools/round86-rendered-cells.py tools/round86-mutant-owners.py tools/round86-pin-origin.py .ufo/waves/round-86/count.py` → empty output, rc=0.

## Contamination attack (before measuring)

The working tree is dirty: `M LOG.md`, `M SCORECARD.md`, plus untracked `.ufo/waves/round-86/…` wave artifacts (14 porcelain entries). Two ways this could fake a reproduction, both closed:

1. **Instruments grading dirty bytes instead of committed bytes.** Source-verified all three read committed bytes at `--rev` via `git -C <repo> show <rev>:<path>` (`GitTree.blob` in rendered-cells, `grade()` in mutant-owners, `read_text()` in pin-origin); the only worktree branch requires the literal `--rev worktree`, which the frozen counter never passes. The dirty `LOG.md`/`SCORECARD.md` cannot enter any verdict.
2. **Counter executing working-tree instrument bytes that differ from the committed tip.** `git diff --stat HEAD -- <the three instruments> tools/round81-append-debt.py registry/pin-recheck-rows.tsv` → empty (working tree == committed bytes). sha256 of the executed bytes: count.py `75b91e7048b4378877f228053b5bc4f72782ac4e2cb5a367ef02878e9eb2a2ad`, rendered-cells `e038b2c0ab52533ce86ba1551b0c8b66937bc664a395fae33ad82a7186bddcf9`, mutant-owners `b7ee59ae1dbb955b27a467de8ed1163dec56c9b87b2370b41979cb4c23a2b5fd`, pin-origin `6c90e3885e6e67f005a85f955ab353e2c25ed56a9801ad560f331552dbb96b4a`.

## Leg runs — exact command, true exit codes, two-run agreement

Command per leg (run twice, `$?` captured directly after each `python3` invocation, no pipes):

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/count.py <c1|c2|c3> --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 67eddac89f44e768b670301ea0feff06e766f32d --work /fast/scratch/hyaku/kama-r86/EX03ReceiptRepro/w
```

| leg | rc run1 | rc run2 | stdout `cmp -s` (full file) | runs agree |
|-----|---------|---------|------------------------------|------------|
| c1  | 0       | 0       | 0 (byte-identical)           | yes        |
| c2  | 0       | 0       | 0 (byte-identical)           | yes        |
| c3  | 0       | 0       | 0 (byte-identical)           | yes        |

No timing exclusion was needed: none of the six stdout streams contains a timing field, so `cmp -s` over whole files is the byte comparison. All six leg stderr streams are 0 bytes (no traceback, no `could-not-evaluate`).

### c1 verdict line (verbatim)

```
RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85
```

### c2 verdict block (verbatim)

```
DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5
DEBT_MUTANT_OWNER M2 owner=note-deletion-equals-subject verdict=killed owning failure line present (1 FAIL lines)
DEBT_MUTANT_OWNER M3 owner=note-deletion-above-subject verdict=killed owning failure line present (1 FAIL lines)
DEBT_MUTANT_OWNER M4 owner=note-subject-exact-summary verdict=killed owning failure line present (2 FAIL lines)
DEBT_MUTANT_OWNER M5 owner=arm-count verdict=killed arms=33 != expected=34
DEBT_MUTANT_OWNER M6 owner=summary-cardinality verdict=killed summary pass+fail=0 != arms=34
DEBT_MUTANT_OWNER_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34
```

### c3 verdict block (verbatim)

```
PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0
PIN_ORIGIN_ROW llama.cpp/b11755 verdict=verified anchors=2/2 corpus/anchors/llamacpp-b11755-health.txt: upstream 478-490 byte-identical; corpus/anchors/llamacpp-b12111-health.txt: upstream 479-491 byte-identical
PIN_ORIGIN_ROW llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a verdict=verified anchors=2/2 corpus/anchors/llamacpp-39febd2a-router.txt: upstream 2197-2204 byte-identical; corpus/anchors/llamacpp-b12111-router.txt: upstream 2199-2206 byte-identical
PIN_ORIGIN_ROW llama.cpp/b7200 verdict=verified anchors=2/2 corpus/anchors/llamacpp-b7200-health.txt: upstream 403-415 byte-identical; corpus/anchors/llamacpp-b12111-health.txt: upstream 479-491 byte-identical
PIN_ORIGIN_ROW sglang/v0.5.22 verdict=verified anchors=2/2 corpus/anchors/sglang-v0.5.22-health.txt: upstream 108-111 byte-identical; corpus/anchors/sglang-v0.5.23-health.txt: upstream 108-113 byte-identical
PIN_ORIGIN_ROW vllm/v0.32.0 verdict=verified anchors=2/2 corpus/anchors/vllm-v0.32.0-prefix-caching.txt: upstream 1-6 byte-identical; corpus/anchors/vllm-v0.33.0-prefix-caching.txt: upstream 1-6 byte-identical
```

## `--selftest` (count.py has no pass-through, so the committed instrument is invoked directly — same invocation shape as the frozen before receipts)

```
TMPDIR=/fast/scratch/hyaku/kama-r86/EX03ReceiptRepro/w python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round86-rendered-cells.py --selftest   # rc=0
TMPDIR=/fast/scratch/hyaku/kama-r86/EX03ReceiptRepro/w python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round86-mutant-owners.py --selftest    # rc=0
TMPDIR=/fast/scratch/hyaku/kama-r86/EX03ReceiptRepro/w python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round86-pin-origin.py --selftest       # rc=0
```

- c1: `RENDERED_CELLS_SELFTEST pass=11 fail=0` — 11 PASS arms: green, fenced-shadow, comment-shadow, tilde-fence-shadow, indent-shadow, unclosed-fence-fails-closed, contradictory-receipt, missing-receipt, command-round-disagrees, closure-only-stale, no-closure-population. The round-85 false-green arm (`fenced-shadow` with stale live cells → mismatches=3, gate=0) is red here.
- c2: `DEBT_MUTANT_OWNERS_SELFTEST pass=10 fail=0` — 10 PASS arms: pristine-green, owned-failure, forged-summary, dropped-arm, fail-lines-disagree, two-summaries, foreign-owner, traceback, exit-two, green-with-fail.
- c3: `PIN_ORIGIN_SELFTEST pass=7 fail=0` — 7 PASS arms: verified, fabricated-hash-consistent (→mismatch, not verified), digest-lie, malformed-header, missing-anchor, unreachable, range-outside-upstream.

Format note: the frozen before receipts end with an `exit=0` trailer appended by their generator; my `*-selftest.after` files are the verbatim instrument stdout without that trailer — the true rc is recorded above instead.

## Cross-check against the L1's published after receipts

`cmp -s` of my run-1 stdout vs `.ufo/waves/round-86/measured/after/c1.out`, `c2.out`, `c3.out` → 0, 0, 0 (byte-identical for all three legs, including the selftest-consistent arms=34 and all five PIN_ORIGIN_ROW details).

## Verdict

**Reproduced — no falsification found.** All three after receipts reproduce independently at `67eddac8`: exit 0 on all six runs, stdout byte-identical within each leg across two runs, byte-identical to the L1's published receipts, and selftests green (11/11, 10/10, 7/7) with the round-85 survivors' arms (M5 arm-count, M6 summary-cardinality) killing on their declared owners. Time-sensitivity caveat (not a defect): c3 corroborates against live upstream bytes; both of my runs and the L1's receipt agree as of 2026-11-04 — later upstream movement would legitimately flip rows to mismatch/unreachable, which is the claim working as designed.

Scope kept: no production file touched, no commit, no mutating git command, no `.ufo/state`/watchdog/MANIFEST access, no claim admission expressed or implied. Tooling: nothing installed or upgraded (python3 3.14.8 and git already present). Scratch `/fast/scratch/hyaku/kama-r86/EX03ReceiptRepro/` removed after receipts were copied out.

Receipts (this wave, my out dir): `c1.after`, `c2.after`, `c3.after` (verbatim leg stdout, run 1 == run 2), `c1-selftest.after`, `c2-selftest.after`, `c3-selftest.after`.

Report: .ufo/waves/round-86/w2/EX03ReceiptRepro.md (byte-identical copy: .ufo/waves/round-86/w2/out/EX03ReceiptRepro/EX03ReceiptRepro.md)
