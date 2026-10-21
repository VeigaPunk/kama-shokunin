VERDICT: partial - round 16 reproduces exactly (exit 0, 3/3 required, 0 defects); author-vs-committer time and batch-check change no measured classification, but batch-check mislabels ambiguous prefixes (landed-ambiguous unreachable) and latent FP/FN classes exist.
Attacked: C1 round-16 result, time base (author `%at` vs committer `%ct`), batch-check lookup (`cat-file --batch-check` with `^{commit}`) in tools/report-landing-audit.py @ a6617149. Scratch clone; lane untouched. Artifacts: falsify/out/Recheck16/.

## Answers
- Author time: no classification changed. Committer variant output is byte-identical to the official raw file (rounds 10-20); round 16 identical; 0 flips in all 11 rounds.
- Batch-check: no classification changed on the corpus. It changes the defect KIND for ambiguous prefixes (synthetic): ambiguous becomes landed-unresolved.
- Round 16 false positives: none. Round 16 false negatives: none. Latent classes below are outside the corpus.

## Executed (exit)
- `git checkout a6617149`: master = HEAD = a6617149; tool blob unchanged vs b76727f3 (`git diff --stat` empty) [0].
- `tools/report-landing-audit.py --lane-repo <clone> --fleet-repo /home/vgpnk/Projects/shokunin --rounds 16 --no-errata --json` [0]: cutoff 1792505790, round_commits 3, required 3, post 0, defects 0.
- `--rounds 10-20 --no-errata --json` [1]; `diff` vs c1-audit-raw.stdout [0, empty].
- `--selftest` [0] 32/32. Default errata `--rounds 16` [0] clean.
- derive.py (own git calls; per-token commit-only resolution) [0]: ALL-AGREE with the tool on all 11 rounds (defects, required, round_commits, post, cutoff).
- Fleet round-16 report: working sha256 = HEAD blob 9ec9c524 (1019676f...) [0]; `git status --porcelain` on the reports dir empty [0].

## Round 16
- Cutoff: fleet 9ec9c524, author = committer = 1792505790 (single add).
- Round commits (author kama-shokunin): b8e485cc6b20 (a 1792504242 / c 1792504249), 726f737a942f (1792505432), ccc4bb31267f (1792505700). All pre under both bases; all cited in Landed (lines 78-80).
- Correctly not counted: cff9e62 (protocol-shokunin, a 1792505817, wrong author). `git log --all --author=kama-shokunin` shows no other round-16 subject.
- Landed tokens b8e485c, 726f737, ccc4bb3, 836b018 resolve (836b018 is an ancestor of b8e485c, not kama-authored, not required). Full hashes 20e392ea..., ccc4bb31..., 726f737a... resolve.

## Time base
- Cutoff author = committer in all 11 rounds. 14 round commits (rounds 16-20) have author != committer; none crosses its cutoff under either base.
- Margin: 1b85a24ec is 2030 s from cutoff on author time but 37 s on committer time (still pre).
- Committer-time variant (out/Recheck16/committer-variant.patch) fails 4/32 selftests [1]: subject-without-space-required, author-time-cutoff-survives-rebase, post-report-excluded, draft-uses-fleet-cutoff. A commit rebased after its report would silently leave `required`. Author time is the right base.

## Batch-check
- Corpus: 0 divergences; no ambiguous or colliding prefixes in rounds 10-20.
- git 2.56.0 (git-batchcheck-ambiguity.txt): `f103 ambiguous` without peel; `f103^{commit} missing` with peel.
- synth-batch-vs-pertoken.json: 8/9 rows equal; the divergent row is an ambiguous prefix (tool missing, per-token ambiguous).
- synth7-ambiguous.txt [0]: 7-hex `0ebd619` (2 commits) through the tool's own audit_round gives `landed-unresolved`, never `landed-ambiguous`.

## Findings (severity order)
1. MEDIUM (label; detection preserved). landed-ambiguous is unreachable: lookup peels `^{commit}` and batch-check prints missing for ambiguity. An ambiguous citation reads as "commit does not exist". An errata row with kind landed-ambiguous can never match (code reading). Advice, not applied: probe ambiguity without the peel (bare-token batch-check prints `ambiguous`), or count `rev-parse --disambiguate` commit candidates.
2. LOW (latent FP; not in corpus). Non-canonical citations inside Landed: uppercase `B8E485C` (draft A, exit 1: landed-omitted for a cited commit); 6-char `b8e485` (B, exit 1: same); sha256 prefix `270cba1b...d256d` (C, exit 1: landed-unresolved). Control D exit 0. Scan of rounds 10-20 Landed bodies: none of these forms.
3. LOW (FN by design, verified). checkable_abbrev skips all-digit and all-a-f 7-hex citations. Unresolvable `1234567` and `deadbee` in Landed give exit 0, no defects (draft E, out/Recheck16/drafts/). Random-typo escape rate about 3.8% [INFERENCE: (10/16)^7 + (6/16)^7].
4. LOW (latent FN, synthetic). lookup returns found when the fleet has a unique match, even if the lane prefix is ambiguous (synth row 2). Negligible at 7 hex [INFERENCE].
5. INFO (scope). Only Landed abbreviations are checked. Round-16 non-Landed unresolvable tokens are sha256 prefixes (72e81bc6, 993ac867, 93ee4302, 36b64978, bf9068d8, 270cba1b, 753bfa73) and external llama.cpp commit 704366d76 (line 131). Correctly unchecked; checking them would add FPs.
6. CONFIRMED. The 9 official defects are not artifacts of the latent classes: no defect token appears in non-canonical form inside a Landed section. r10 40660352 at lines 114/120 (Landed body lines 29-39); r18 101f3991/1c325b2e/c6dc46fa outside body lines 74-87 (1c325b2e at 27, c6dc46fa at 26, 101f3991 at 19); r20 0957ce61 outside body lines 14-20; r20 846e366d/92b14625/33a67778 absent from the report.

## Gaps
- Other git versions untested. No 7-hex cross-repo collision constructed.
- Fleet HEAD advanced (9881be6 -> 38a7cd5) during the session; cutoffs are history-based and unchanged.

## Tooling
- Installs or updates: none (system python3 3.14.8, git 2.56.0). No background processes. Scratch /tmp/kama-r21-Recheck16 deleted after artifacts were copied.

## Files (out/Recheck16/)
derive.py, derive-r16.json, derive-r10-20.json, tool-r16.json, tool-r10-20.json, committer-variant.patch, committer-selftest.txt, committer-r10-20.json, committer-vs-official.diff, synth_semantics.py, synth-batch-vs-pertoken.json, git-batchcheck-ambiguity.txt, synth7_ambiguous.py, synth7-ambiguous.txt, drafts/ (A-E .md and outputs, r16-default-errata.json).
