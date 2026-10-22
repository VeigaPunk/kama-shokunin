# FinalCase29 evidence index — PG29-errata-corrected-missing-sha-plain

Pin: commit 92063cfc60e217fa7e2098c568578119b16a1b95 (detached, clone at
/fast/scratch/hyaku/kama-r24/postfix/FinalCase29/clone, `git status` clean).
Python 3.14.8, git 2.56.0. No installs, no network.

Verified identities (sha256, pinned clone):
- tools/report-landing-audit.py                b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f
- tests/report-audit/promisor-grid.py          30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270
- tests/report-audit/promisor-grid-expectations.json d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1
- tests/report-audit/promisor-mutants.py       971c3ecbc1af05d4e6806ed06e8d3c7499ff55caf09e7bbc2c5ae2992204f200
- tests/report-audit/isolation-mutants.py      eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00
- .ufo/.../opaque-garbage-proof-v2.py          8478d1bca0f11e616ded96bb800f9be78fcd942400f52b1a416447d0dbed79f4
- .ufo/.../proof-driver-replay-v3.py           5a570882189f7255b45c44d2a4c5ca844a0a8152656498de300c464e83d65a62

Grid runs (argv, exit, raw evidence in this directory):
1. `python3 tests/report-audit/promisor-grid.py --arm current --case
   PG29-errata-corrected-missing-sha-plain --json --out .../grid-pg29`
   -> exit 0. Raw: grid-pg29-current.json (= pg29-stdout.json).
2. same + `--case PG30-errata-corrected-missing-sha-promisor` -> exit 0.
   Raw: grid-pg29-pg30-current.json.
3. `--keep` variants kept the fixtures under
   /fast/scratch/hyaku/kama-r24/postfix/FinalCase29/tmp/promisor-grid-*/
   (fixture promisor-grid-8qm678ir/current/000 = PG29 plain;
    promisor-grid-zvzuhfjt/current/001 = PG30 promisor-marked).

Direct auditor probes (pinned auditor, kept PG29 fixture; read-only):
- probes.py / probes.json   A --no-errata; B errata round 2 (unselected);
  C errata correction 0*40 (absent); D committed ledger (registered path);
  E errata row matching no defect.
- probes2.py / probes2.json F wrong kind; G correction = present blob;
  H uppercase token; I different token.
- probes3.py / probes3.json V1 unrelated lane blob dropped (copy);
  V2 lane tree dropped (copy).
- probes4.py / probes4.json V3 working-tree ledger corrupted (copy);
  V4 working-tree fleet report rewritten (copy).

Each probes*.json entry records argv, exit, stderr, summary, defects and
objects_acquired (lane/fleet). Every probe run reported objects_acquired
{"lane": [], "fleet": []}. Changed input states (V1-V4) are on separate local
copies under tmp/variants/ and were never compared to the registered result as
if unchanged.
