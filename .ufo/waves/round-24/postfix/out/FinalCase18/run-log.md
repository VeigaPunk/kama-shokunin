# FinalCase18 run log (PG18-missing-fleet-report-plain)

Host tools: git 2.56.0, python 3.14.8. No installs performed.

## 1. clone

    git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin clone
    git checkout --detach 92063cfc60e217fa7e2098c568578119b16a1b95
    # HEAD = 92063cfc60e217fa7e2098c568578119b16a1b95, worktree clean (git status --porcelain empty)

Clone root: /fast/scratch/hyaku/kama-r24/postfix/FinalCase18/clone

## 2. digest check (registered producer identities)

    b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f  tools/report-landing-audit.py
    30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270  tests/report-audit/promisor-grid.py
    971c3ecbc1af05d4e6806ed06e8d3c7499ff55caf09e7bbc2c5ae2992204f200  tests/report-audit/promisor-mutants.py
    eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00  tests/report-audit/isolation-mutants.py
    d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1  tests/report-audit/promisor-grid-expectations.json
    8478d1bca0f11e616ded96bb800f9be78fcd942400f52b1a416447d0dbed79f4  .ufo/waves/round-24/fixes/StoreLocalPresence/opaque-garbage-proof-v2.py
    5a570882189f7255b45c44d2a4c5ca844a0a8152656498de300c464e83d65a62  .ufo/waves/round-24/fixes/StoreLocalPresence/proof-driver-replay-v3.py

All match the registered identities. The expectation manifest digest equals the
registered primary manifest d86b7bea... (47 graded cells, PG40 ungraded).

## 3. grid run (CURRENT arm only; 2 cells)

    cd /fast/scratch/hyaku/kama-r24/postfix/FinalCase18/clone
    TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase18/tmp-current \
      python3 tests/report-audit/promisor-grid.py --arm current \
        --case PG18-missing-fleet-report-plain \
        --case PG17-missing-fleet-report-promisor --json
    # exit 0; stdout -> grid-pg18-pg17-current.json; stderr empty (0 bytes)

Grid self-reported digests: grid_sha256 30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270,
expectations_sha256 d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1,
population_sha256 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88, population_size 47,
auditor_sha256 current b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f,
timeout_seconds 30.

Frozen arm was NOT run (contract: frozen/both are CNE2 before a pristine run).

## 4. independent re-derivation of the PG18 cell (full stderr)

    TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase18/tmp-probe python3 probe_pg18.py
    # exit 0 (probe); auditor exit 2; stdout 0 bytes; stderr 392 bytes
    # argv: python3 tools/report-landing-audit.py --lane-repo <lane> --fleet-repo <fleet> --rounds 1 --json --no-errata

## 5. discrimination control (DIFFERENT input state: report object present)

    TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase18/tmp-control python3 control_probe_pg18.py
    # exit 0 (probe); auditor exit 0; stdout 776 bytes, JSON verdict document, defects []
