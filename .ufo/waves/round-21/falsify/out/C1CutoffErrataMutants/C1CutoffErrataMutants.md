VERDICT: partial - four cutoff mutants survive the existing detector; added boundary fixtures kill all eight isolated mutants.
Attack: C1 author-time cutoff / first-add selection / pre-post partition and apply_errata selected-round matching, omitted-commit identity, blob rejection in tools/report-landing-audit.py.
Axes: calibration 7 (primary, detector coverage); operability 8 (preserved). This is scoped mutation evidence, not round admission or an implementation change.
Target: a6617149722c73d90e142fbdc8154d6967055f7e; population fleet snapshot: 7fd7c785a918131a8eb11793bca7857201e9867f.
Binding out-only scope overrides the requested advice/C1CutoffErrataMutants.md destination; this report is ready for L1 placement there.

## Executed detectors and controls
Path abbreviations: D=/tmp/kama-r21-C1CutoffErrataMutants/lane/tools/report-landing-audit.py; P=D's lane root; F=/tmp/kama-r21-C1CutoffErrataMutants/fleet-population; H=target hash above; O=this report's directory. Exact expanded argv, exit, stdout and stderr are retained in each phase JSON.
- S: /usr/bin/python3 D --selftest
- R: /usr/bin/python3 D --lane-repo P --fleet-repo F --branch H --rounds 10-20 --no-errata --json
- L: /usr/bin/python3 D --lane-repo P --fleet-repo F --branch H --rounds 10-20 --json
- B: /usr/bin/python3 O/probe.py boundaries (nine checks using real isolated Git fixtures, not mocked time/history).
Executed /usr/bin/python3 O/probe.py prepare: exit 0. Then phase pristine, every named mutant phase below, and m1-restored through m8-restored: all 17 wrapper invocations exited 0; child exits are recorded separately below.
Each phase ran S/R/L/B concurrently, with a 90-second child deadline; mutations themselves were sequential, exactly one changed line at a time.
Pristine and every restored phase: exits S/R/L/B = 0/1/0/0; S printed "selftest cases=32 failed=0"; B printed "boundaries cases=9 failed=0". R's expected defect exit 1 is not a baseline failure.
R: 9 defects (1 unresolved-full-hash, 8 landed-omitted), required=42, post_report=4. L: 9 corrected, 0 uncorrected, unmatched=0, invalid=0. Both population outputs and exits remained byte-identical across ALL eight mutants.

## One-mutant probes
Verdict columns distinguish the existing S+R+L detector from added B. Files are <phase>.json; all have baseline_ok=true.
| ID / phase | Smallest mutation (target line) | S/R/L/B exits | Existing / with B | Killing cases or observed gap |
|---|---|---|---|---|
| M1 / m1-lane-committer | round_commits %at -> %ct (134) | 1/1/0/1 | killed / killed | S author-time-cutoff-survives-rebase, post-report-excluded, subject-without-space-required, draft-uses-fleet-cutoff; B lane-author-time 1100 -> 5000, required 2 -> 1, post gains rebased commit. |
| M2 / m2-fleet-committer | report_cutoff %at -> %ct (152) | 0/1/0/1 | survived / killed | B fleet-author-time 1200 -> 6000; required 2 -> 3; a post-report commit becomes a required omission. S remains 32/32. |
| M3 / m3-latest-add | report_cutoff out[-1] -> out[0] (154) | 0/1/0/1 | survived / killed | B first-add-not-readd 1250 -> 1500; first-add-post-split changes exit/required/post from 0/0/[between] to 1/1/[]. S remains 32/32. |
| M4 / m4-exclusive-pre | pre atime <= cutoff -> < (183) | 0/1/0/1 | survived / killed | B inclusive-required: a missing commit authored exactly at cutoff disappears; exit 1 -> 0, required 2 -> 1, omitted finding removed. S remains 32/32. |
| M5 / m5-inclusive-post | post atime > cutoff -> >= (184) | 0/1/0/1 | survived / killed | B post-split: same-second commit appears in both required and post_report; post list grows from one to two. S remains 32/32. |
| M6 / m6-unselected-unmatched | selected membership in -> not in (249) | 1/1/0/1 | killed / killed | S unmatched-errata-fails and unselected-round-row-ignored; B selected-unmatched-only expects row [2], gets unselected row [3], invalid=[] in both. |
| M7 / m7-omitted-self-comparison | correction != token -> correction != correction (254) | 1/1/0/1 | killed / killed | S omitted-correction-must-be-the-commit; B omitted-correction-equals-token: wrong but resolvable commit accepted, invalid [1] -> []. |
| M8 / m8-blob-correction | correction lookup peel ^{commit} -> empty (251) | 1/1/0/1 | killed / killed | S blob-is-not-a-correction; B blob-rejected: a real Git blob accepted, invalid [1] -> []. |
S failure counts M1/M6/M7/M8: 4/2/1/1. B failure counts M1..M8: 3/3/2/1/1/1/1/1. No baseline failure, timeout or stderr occurred in these detector runs.
Result: existing detector kills 4/8, survives 4/8; population alone kills 0/8; B kills 8/8. Surviving mutants identify coverage gaps, not permission to change the contract. Pristine passes every added check.

## Hashes and restoration
Common pristine/restored SHA-256: bd671a1e1e79a76a5c644d4efccd5baf0ce1121e9f308987ca816a5645520d69.
Each mutated phase records this probe's actual SHA-256 before and after its detector run; each mN-restored.json records the exact common hash and unchanged outputs before the next mutation. Full replacement bytes and hashes also live in mutants.json.
- M1: 11e1c22abbfa6f3cad1e645d99189c939f47a3ff45b348e92b642767715de304
- M2: 8e48f674833f1563d794878db2066e5d1d6c7b28fd6b55011120429afceb2b05
- M3: b85567407ecae725d55c699b2429d3d980756b9e2d2785c5891d55f178880ca6
- M4: 439a783f43a9cbf568a9a8755a4144c7f13515ce69dc405c2cb2d56c370c9467
- M5: 8409392ad6dbb0ca2df963e2ccf67e862edade1fef0b120c7771351c4ac3b52c
- M6: 336125d9f4abb2937c029f15a6b57f3f881c3af0c007b657cb22818b5df1b7b8
- M7: 37c0e01dd35d52502dca272c625e844fa7e4b312d15196bfd12d3a9ebc82ee7c
- M8: 84dc392cefad0a03be8f251e22d67f51178097bce4325272e9d06dbdceebd37e
Executed cleanup `rm -rf -- /tmp/kama-r21-C1CutoffErrataMutants && test ! -e /tmp/kama-r21-C1CutoffErrataMutants`: exit 0, no output, after M8 exact restoration.
Evidence: setup.json records every fixture/setup Git command and exit, pinned report-file digests and versions; pristine.json + eight mutant JSON + eight restored JSON retain complete raw detector outputs; probe.py reproduces the fixture/detector design; mutants.json records exact mutations.
No lane source/index, fleet, sibling, service or installed model tree was modified; only authorized new output artifacts were written. No persistent process/server or tool install/update was started. Existing tools: Python 3.14.8, Git 2.56.0 (setup.json).
