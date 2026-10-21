# Proposed SOURCES row (candidate only — registry NOT edited)

Next free id: S102 (current maximum S101; 101 rows).

| S102 | git v2.56.0 `promisor-remote.c` config callback — https://raw.githubusercontent.com/git/git/v2.56.0/promisor-remote.c | code | A | which configuration makes git register a promisor remote, at tag v2.56.0 (the host git); not repository completeness and not `.promisor` pack-marker semantics | `promisor_remote_config`, lines 148–163 at tag v2.56.0 (annotated tag → commit a018953688f1b10bddf91bff8747068f5f4746a4), raw sha256 175e67e1b2cc62db1ead26007ba1e5502f9b585fd33dbc45b59f9876b34f9bca, opened 2026-10-21 | `remote.<name>.partialclonefilter` creates the promisor-remote entry even when no `remote.<name>.promisor` boolean is set: "r = promisor_remote_lookup(config, remote_name, NULL); if (!r) r = promisor_remote_new(config, remote_name);". Metadata only; it says nothing about which objects exist. | mined | 2026-10-21 | on-release | .ufo/waves/round-24/build/advice/SrcPromisorCode.md, tools/report-landing-audit.py |

Notes for L1:
- This is a NEW scope row, not a reopened used source: no existing SOURCES row names `promisor-remote.c` (grep of corpus/SOURCES.md: 0 hits). S092/S099 are git-scm.com partial-clone prose; S089 is git(1) global options; S101 is the only prior git source-code row, `commit.c`. No supersession is claimed.
- If L1 declines to admit the row, the finding still stands as inspection evidence; do not mark it as sourced.
