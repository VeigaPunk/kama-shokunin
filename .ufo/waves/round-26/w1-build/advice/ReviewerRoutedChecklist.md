Verdict: at a23c0e04, round-25 routed defects 1-6 are still open. D1 is not clean: one untracked file is left. D7 is correctly held for now, and D8 is met at preregistration. Round-24 items 1, 2 and 4 hold; items 3 (append lineage) and 5 (H2) need the operator or a closure.

# ReviewerRoutedChecklist — routed-defect acceptance (round 26, wave 1)

Checked revision `a23c0e042114016a909eb15173aa6df74b5b7eb0`, base
`1560e4d83f42b04f40336357de6f9637eafa0f4b`. All commands and outputs are in
`.ufo/waves/round-26/w1-build/out/ReviewerRoutedChecklist/checks-a23c0e04.out`.
That file was produced by `checks.sh a23c0e042114016a909eb15173aa6df74b5b7eb0`,
which exited 0. The per-defect pass conditions are in `checklist.md`.

## Findings by severity

**High: D1 is not resolved by a4a159c3.**
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain -- .ufo/waves/round-25`
printed `?? .ufo/waves/round-25/a2-falsify/out/ReplicateReceipt/replication-run3/raw/L3.server.log`
(exit 0). `git ls-files …/replication-run3/raw | wc -l` printed `69`; the
directory holds 70 files. The untracked file (1446775 bytes, sha256
`c6723b145db5673dc3579309b6e42303f855f71281e6062783378c7b3ef1d06b`) is the
L3 `server_log` that the committed `replication-run3/receipt.json` binds.
It is not ignored (`git check-ignore -v` exit 1). It is not too large to
commit: the 1446303-byte `final/raw/L3.server.log` is tracked. Fix: commit
it. Deleting it would orphan the receipt hash.

**High: D5 reproduces at the tip.** In a `git archive a23c0e04` extract,
`python3 .ufo/waves/round-25/count-c2.py` printed
`registered 14 observed 14 bound True missing []` (exit 0). I then built a
mutant: appended `TAMPERED\n` to `final/raw/K1.server.log` and deleted
`final/raw/L3.server.log`. On the mutant the counter printed the same line,
exit 0. An independent sha256 join gave 70 of 70 matched on the tip and
68 matched with 2 unmatched on the mutant. `count-c2.py` has no `hashlib`
and does not register the limit (the grep exited 1).

**Medium: D2, D3, D4 and D6 are untouched since base.** `git diff --numstat 1560e4d8 a23c0e04`
is empty for `corpus/QUALITY.md`, `corpus/lessons/round-25.md`, `SKILL.md` and
`SCORECARD.md`. No `| supersedes S106/S109/S113 —` row exists in
`corpus/SOURCES.md`. `corpus/knowledge/context-capacity.md:55` still says
"the only trace", while `final/raw/K5.server.log:1083` holds the second
trace (`the slot context (4096) exceeds the training context of the model (2048) - capping`).
Line 137 still uses `n_tokens = 1025`; the same framing recurs at lines
143-144, 156 and 161, which are not routed but are worth checking.
`corpus/lessons/round-25.md:49` still claims "the instrument docstring and
SKILL registry row now say M17 survives and why". `SKILL.md` has no line
with M17 followed by "surviv" (exit 1). `SCORECARD.md:1306-1310` still reads
"quality unchanged-to-improved … discernment improved".

**Low: D7 has no audit trail.** The reservation is held now:
`23:1792726390 36 kama kama-r26-w1-build`, 36 seats in the spec, 7 `.md`
advice reports present. But `~/.local/state/shokunin-hyaku/events.log` has
no slot-release events for kama. Once the row is removed, nothing shows
whether every seat had returned. The L1 should record the release time and
the returned-seat count in the wave record.

## Operator or closure action

- R24-5: the H2 Git ≥ 2.45 floor approval is operator-owned and open. The
  host runs `git version 2.56.0`; the open question is the floor policy, not
  the host.
- R24-3: the prepared-versus-landed append lineage is unresolved
  (`corpus/lessons/round-25.md:74`) and needs a ruling. The locators were
  corrected at lines 66-74.
- R24-2: changing PM08 or the mutation semantics needs separate
  authorization. The wording holds at `SKILL.md:888` and `:994`.
- SHONEN promotion stays operator-owned. D8's axis fit (C1 on depth; depth 7 per
  `SCORECARD.md:1304`) is a closure judgment.

## Holds

- R24-1: `git diff --stat 5cb46efc a23c0e04 -- .ufo/waves/round-24 corpus/lessons/round-24.md`
  printed nothing (exit 0).
- D3 precondition: `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
  exited 0 with `kama ok` and W04-only warnings for S108, S109, S110 and S112.

## Residual risk and verification gaps

- The D2, D4 and D6 checks are grep checks on added lines. A hit is necessary but
  not sufficient; the L1 or a falsifier must read the matched line.
- R24-4 can be checked only once the round-26 report exists.
- I did not verify the S107 and S112 corrections (outside D3's routed scope;
  the closure also left them unverified).
- No LSP server applies; these are markdown, JSON and shell surfaces. Every check is
  a literal git or grep observation.
- I started no server, ran no C1 counter and took no lock.

## Files written

- `.ufo/waves/round-26/w1-build/out/ReviewerRoutedChecklist/checklist.md`
- `.ufo/waves/round-26/w1-build/out/ReviewerRoutedChecklist/checks.sh`
- `.ufo/waves/round-26/w1-build/out/ReviewerRoutedChecklist/checks-a23c0e04.out`
- `.ufo/waves/round-26/w1-build/advice/ReviewerRoutedChecklist.md` (this file)
- scratch: `/fast/scratch/hyaku/kama-r26/ReviewerRoutedChecklist/` (`tip/`,
  `mut/`, `checks/`, `census.out`)

Installs: none. No llama-server processes started.
