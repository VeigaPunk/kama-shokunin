VERDICT: refute - a29bb84 selftest is not env-isolated: GIT_DIR rewrites the decoy and fails, hostile global git config crashes it (exit 1); env-scrub patch restores 15/15 with decoy untouched

# AuditGitEnvExec: report-landing-audit selftest under hostile git env (round 21, BUILD)

Scope: executable check at a29bb84 in a scratch clone (lane untouched; clone was read-only). Tools: git 2.56.0, Python 3.14.8, gpg/gpgconf (pre-installed, not changed). No installs or updates (no pacman/uv/npm). No subagent dispatched. Scratch removed: `rm -rf` exit 0, `ls` exit 2, `pgrep` exit 1.
Setup: decoy = fresh `git init -q --bare` per case; `GNUPGHOME` = scratch; hostile config = `[commit] gpgsign = true` + `[core] hooksPath` to `pre-commit`/`commit-msg` scripts doing `exit 1`.

## 1. Unpatched a29bb84 (`python3 tools/report-landing-audit.py --selftest; echo exit=$?`)
| case | env | exit | result |
|---|---|---|---|
| U1 | none | 0 | 15 `ok`, `selftest cases=15 failed=0` |
| U2 | `GIT_DIR=<bare decoy>` | 1 | no verdict; uncaught CalledProcessError at `git add f` (rc 128, "must be run in a work tree") |
| U3 | `GIT_CONFIG_GLOBAL=<gpgsign + hooksPath>` | 1 | no verdict; `git commit` fails (hooksPath: rc 1; gpgsign-only: rc 128, "gpg failed to sign ... No secret key") |
| U4 | `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=commit.gpgsign GIT_CONFIG_VALUE_0=true` | 1 | no verdict; commit fails (gpg) |
| V6 | `GIT_DIR=<non-bare decoy>/.git` (py matrix) | 1 | 4 FAIL: exact-defect-count, foreign-author-and-other-round-ignored, errata-clean, uncommitted-draft-requires-all; 61 decoy/.git entries changed (index, config, COMMIT_EDITMSG, logs/refs, ...) |

- Decoy write under U2, probed directly: `GIT_DIR=<bare> git -C <tmp> init -q -b master` gives rc 0 with stderr `warning: re-init: ignored --initial-branch=master`. `config` bytes are identical, but `config` mtime and decoy root mtime change. A content-hash check reads "unchanged"; the write is metadata-only. "Never writes the decoy" therefore fails.
- Root cause (read in code): `git()` (L62), `_sh()` (L257) and `_commit()` env (L262) spawn git with inherited `os.environ`. There is no `GIT_*` scrub and no config isolation. `selftest()` does not catch CalledProcessError, so a broken env exits 1 with a traceback, the same code as a failing selftest.
- Clean env (U1) still gives 15/0, so the lane's "15 cases" claim holds only when the caller's git env is clean.

## 2. Minimal patch (delivered; lane not modified)
`out/AuditGitEnvExec/report-landing-audit-env-scrub.patch`: 2070 B, 1 file, 15 insertions / 6 deletions.
- `git_env(**extra)`: `os.environ` minus every `GIT_*` name, plus `GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1`, plus extras.
- Used by `git()`, by `_sh()` (when `env` is falsy) and by `_commit()`. The only subprocess call sites in a29bb84 are L62 and L257 (L44 is the import).
- No new selftest case; the count stays 15.

Verification (executed):
- `py_compile` of patched file: ok. Fresh clone at a29bb84: `git apply --check` rc 0, `git apply` rc 0, result byte-identical to the patched file.
- Patched selftest, Python matrix V0-V6: rc 0, `15/0`, 0 decoy entries changed. Shell P1-P4: exit=0, ok=15 each.
- Production parity (read-only, `--lane-repo <scratch> --fleet-repo /home/vgpnk/Projects/shokunin --json`): clean unpatched equals patched, rc 0, sha256 `f8752ce97c83e32c` (4827 B), `reports=11 defects=9 uncorrected=0 status=clean`. Under `GIT_DIR=<bare decoy>`: unpatched rc 2 (`could-not-evaluate: git rev-parse --verify master^{commit} ... rc=128`); patched rc 0 with identical output. 0 decoy changes.

## 3. Limits
- Only git 2.56.0 was tested. `GIT_CONFIG_GLOBAL` needs git >= 2.32 [INFERENCE: older git would ignore it, so the global-config part of the scrub would not hold there].
- Production now also ignores global and system git config. No effect on this host (parity above). Hosts with e.g. `diff.renames=false` or `log.showSignature` could see different output [INFERENCE, untested].
- Global `safe.directory` is dropped; this matters only for repos owned by another user [INFERENCE, untested].
- Threat model: callers that export `GIT_*` into the audit, such as git hooks or CI [INFERENCE].
- Not delivered: an isolation regression case (would change 15 to 16; L1 decision).

## 4. Artifacts (`out/AuditGitEnvExec/`)
- `report-landing-audit-env-scrub.patch`: the patch.
- `selftest-matrix.txt`: Python matrix V0-V6 (unpatched and patched), production parity, gpg-agent cleanup.
- `shell-cases.txt`: shell cases U1-U4 and P1-P4 with exit codes, plus the targeted reinit probe.

## 5. Reproduce and L1 checks
- `git -C <clone at a29bb84> apply --check <patch>`: expect rc 0.
- `GIT_DIR=<bare decoy> python3 tools/report-landing-audit.py --selftest; echo exit=$?`: unpatched 1, patched 0.
- `GIT_CONFIG_GLOBAL=<hostile config> python3 tools/report-landing-audit.py --selftest; echo exit=$?`: unpatched 1, patched 0.
- Lane integration, official measurement and commits are L1's.
