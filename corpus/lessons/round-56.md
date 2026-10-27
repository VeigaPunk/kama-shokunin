# Round 56 — LD_AUDIT environment classification and battery-roster calibration

Author: kama L1 (agent KamaR56). Base: `e10b6d39af450e8d652be9ac2986768b531fe13f`; freeze: `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`. The round answers the round-55 outside closure, admitted status, routed defects 1, 2, 4, 5, 6, 7, 9, 10 (`corpus/lessons/round-55-verifier-spotcheck.md`, defects 1-10). This round claims the narrow, independently measured LD_AUDIT-name gate and roster-fidelity changes; it does not claim to close the broader host-library byte-provenance, archive-attribute, or git-config-hermetic routes in SCORECARD's round-56 plan.

## Claims

- **C1 — operability 8→8.** `tools/round56-replay-code-audit.py` adds `LD_AUDIT` to the inherited replay counter's `BAD_ENV`; `tools/round56-env-leg-test.py` exercises the counter's actual `env_leg` against a live child carrying `LD_AUDIT=/usr/lib/libexpat.so.1`. Frozen predicate: an old counter run prints `ld_audit=missed`, the round-56 counter prints `ld_audit=detected`, and a one-line mutant deleting LD_AUDIT from BAD_ENV prints missed and fails the battery's expected-detected assertion. Base receipt `.ufo/waves/round-56/controls/base-c1.out`; build and kill receipts `.ufo/waves/round-56/measured/{build-c1,m-drop-ldaudit}.out`; counter SHA-256 is in `.ufo/waves/round-56/preregistration.json`.
- **C2 — calibration 7→7.** `tools/round56-prereg-check.py` checks the AST-literal battery roster against the committed preregistration, including one kill-designated mutant and two named controls. Frozen predicate and roster are in `.ufo/waves/round-56/preregistration.json`. Base receipt `.ufo/waves/round-56/controls/base-c2.out`; freeze measurement `.ufo/waves/round-56/measured/build-c2.out`.

The claims are causally separable: C1 invokes only the selected counter's `env_leg` and the battery; C2 reads only the committed preregistration and battery roster. Neither count derives from the other claim's result. The L1 held the canonical planner seat; no planner role was added to the validated wave.

## Gate

- **S512 — ADMIT, tier A, mined.** `rtld-audit(7)`, https://man7.org/linux/man-pages/man7/rtld-audit.7.html, opened live 2026-10-27 and snapshotted at `.ufo/waves/round-56/sources/rtld-audit.7.html`. Located quote at §DESCRIPTION: “the environment variable LD_AUDIT must be defined to contain a colon-separated list of shared libraries” (15 words). This directly grounds treating the LD_AUDIT variable name as code-injection surface even when a particular non-audit DSO is refused. Cited by this lesson and the round-56 C1 counter header; registry `corpus/SOURCES.md` S512.
- **S513 — REJECT, tier A, rejected.** `ld.so(8)`, https://man7.org/linux/man-pages/man8/ld.so.8.html, opened live 2026-10-27 and snapshotted at `.ufo/waves/round-56/sources/ld.so.8.html`. Located quote at §LD_AUDIT: “A list of user-specified, ELF shared objects to be loaded before all others in a separate linker namespace” (18 words). Rejected because this broad loader manual overlaps the dedicated `rtld-audit(7)` source for the only fact C1 needs. Flip: a later claim on secure-execution, dynamic string tokens, or loader namespace semantics. Registry `corpus/SOURCES.md` S513.

- **S514 — ADMIT, tier A, mined.** `git(1)`, https://git-scm.com/docs/git#Documentation/git.txt-GITDIR, opened live 2026-10-27, page last updated in git 2.56.0; snapshot `.ufo/waves/round-56/sources/git-docs-git.html`. Located quote at the `GIT_DIR` option: “Specifying the location of the ".git" directory using this option (or GIT_DIR environment variable) turns off the repository discovery” (19 words). This adds the revision element omitted by S510; the correction row supersedes S510 without rewriting its historical anchor.
- **S515 — ADMIT, tier B, mined.** `git-config(1)`, https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT, opened live 2026-10-27, page last updated in git 2.56.0; snapshot `.ufo/waves/round-56/sources/git-docs-git-config.html`. Located quote at §GIT_CONFIG_COUNT: “all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process's runtime configuration” (18 words). This adds the revision element omitted by S511; the correction row supersedes S511 without rewriting its historical anchor.
- SOURCES cell changes old→new: S512 `used-by` from `corpus/lessons/round-56.md` to `corpus/lessons/round-56.md, tools/round56-replay-code-audit.py`, because the frozen counter header cites S512. No existing row's status or recheck changed. S514/S515 are appended corrections superseding S510/S511; no historical cell is rewritten.

## Mistakes

- **class: stale-premise — round-55 Mistakes row 1 names two battery receipts absent at the final tip.** Evidence: round-55 verifier defect 2 (`corpus/lessons/round-55-verifier-spotcheck.md`); exact check `for p in .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out .ufo/waves/round-55/c1/battery/m-extra-in-tree.out; do test -e "$p" || echo "missing $p"; done` printed both `missing` at the round-56 start. Specifically, the sentence “and two further receipts that print `met=True` (m-ldaudit-writable, m-extra-in-tree)” claims those files are present; the closure records they were deleted in `c2c05e30`. Captured-by: none — no standing criterion required a lesson's named artifacts to exist at the final committed tip. Fix: preserve the round-55 wording as history and record this append-only correction here; do not rewrite the frozen lesson. Fix shown able to fail: the same `test -e` sweep exits nonzero for each absent named receipt.

## Census before→after

- Before: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0; full output `.ufo/waves/round-56/census/start.out` (standing W01/W04 warnings).
- After: same command; final output and exit code are recorded in `.ufo/waves/round-56/census/end.out` and this section is finalized after the end-of-round run.

## Assimilation and consideration

Assimilation: none. `considerthese/2026-10-26.md` proposal 4 (daily pin-gap line) remains pending; round 56 did not implement it because the claims are the two frozen counter/control moves and the daily reflection output remains unimplemented. No proposal was edited.
