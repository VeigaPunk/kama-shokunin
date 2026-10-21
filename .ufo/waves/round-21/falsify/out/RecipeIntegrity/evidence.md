# RecipeIntegrity evidence — round-21 official measurement runs/b76727f3

Attacked: `runs/b76727f3/` (commands.json, *.stdout/*.stderr/*.exit, live-receipt.json), `.ufo/waves/round-21/recipe.json`, `run.py`, the clean-start and ancestry of `b76727f31e522763ce24e43d6ec86d21b507a11f`, and recipe coverage of `corpus/lessons/round-21.md`. Lane not modified. Scratch clone `/tmp/kama-r21-RecipeIntegrity/lane` pinned to `b76727f3` (master), deleted after this file was written. Times are UTC unless noted; `-0300` mtimes converted.

## 1. Structural audit of commands.json (eval cell, exit 0)
- commands.json: measured_commit = b76727f3; recipe_sha256 = 9d68997d207756f72f5471daed1798ad9a1975a2c7193d40397e38c412194d3e = sha256 of working recipe.json (MATCH).
- 28 recipe entries = 28 recorded commands; identical names and order; no duplicates; keys match.
- Per entry: sha256(.stdout), sha256(.stderr) equal recorded hashes; `.exit` file equals `exit=<code>`; as_expected == (exit == expected); timed_out false; argv equals template with {lane}/{revision}/{out} substituted. FAILING ENTRIES: none. started_utc 11:14:00.272967 .. 11:14:13.726240, monotonic.
- Rows (name exit/expected timeout stdout-B stderr-B): c1-absent-at-base 128/128 180 0 114; c1-audit-selftest 0/0 180 890 0; c1-audit-raw 1/1 180 4726 0; c1-audit-ledger 0/0 180 4853 0; c2-grid-selftest 0/0 180 377 0; c2-grid-frozen 1/1 180 3964 0; c2-grid-current 0/0 180 5611 0; c2-grid-both 1/1 180 7361 0; c2-gate-selftest 0/0 180 98 0; c2-producer-selftest 0/0 180 70 0; c2-live-receipt 0/0 300 0 0; c2-live-gate-pinned 0/0 180 102 0; c2-live-gate-wrong-links-pin 1/1 180 292 0; c2-legacy-receipt-1/-2/-3 0/0 99 0 each; c2-legacy-receipt-1-required 1/1 180 195 0; nh-error-pair 0/0 4983 0; nh-error-selftest 0/0 91 0; nh-install-tree-grid-selftest 0/0 154 0; nh-gguf-selftest 0/0 930 0; nh-gguf-measure 0/0 20940 0; nh-citation 0/0 8024 0; nh-citation-selftest 0/0 24 171; nh-sources-append-only 0/0 215 0; nh-snapshot-selftest 0/0 1289 0; fr-sources-validate 0/0 886 0; fr-sources-census 0/0 309 0.

## 2. Clean start and ancestry (commands run, exits as shown)
- `git clone -q <lane> <scratch>/lane` exit 0; `git checkout -q -B master b76727f3` exit 0; `rev-parse master` = b76727f3; `git status --porcelain | wc -l` in scratch = 0.
- `date -u -d @1792581238` = 11:13:58 (b76727f3 exported in lane reflog); `date -u -d @1792581264` = 11:14:24 (a6617149 commit); `date -u -d '2026-10-21T11:14:00Z' +%s` = 1792581240.
- run.py:25–29: `revision = git('rev-parse','refs/heads/master')`; `if git('status','--porcelain'): parser.error(...)`; `args.out.mkdir(parents=True, exist_ok=False)` only after the check. Runner start 11:14:00 > export 11:13:58, so master was b76727f3 at start, consistent with measured_commit.
- `merge-base --is-ancestor` (exit 0 each): b76727f3 in master; b76727f3 in a6617149; 7a6bc91 in b76727f3.
- `git show b76727f3:.ufo/waves/round-21/recipe.json | sha256sum` = 9d68997d… (= recorded, = working file). `git show b76727f3:.ufo/waves/round-21/run.py | sha256sum` = de70b5c9… (= working file).
- `git ls-tree -r --name-only b76727f3 -- .ufo/waves/round-21/runs | wc -l` = 0. `git log -- .ufo/waves/round-21/runs/b76727f3` = a6617149 only (first and only commit adding the runs dir).
- `git diff --stat b76727f3 a6617149` = 86 files, all under `.ufo/waves/round-21/runs/b76727f3/`; `git diff --name-only b76727f3 a6617149 | grep -v '^.ufo/waves/round-21/runs/b76727f3/' | wc -l` = 0. Measured code == attacked code.
- `git show --stat b76727f3`: 5 files (build/advice/RevengeSpliceOrigin.md and 4 files under build/out/KamaR21.RevengeSpliceOrigin-6/), 208 insertions. `git diff --name-only 4e75d9e b76727f3` = those 5 files only: no code changed between the recipe commit 4e75d9e and the measured commit.
- Tracked at b76727f3: tools/report-landing-audit.py, registry/report-landing-errata.tsv, tests/llamacpp-live/{check-receipt.py,install-links-grid.py,install-tree-grid.py,controls.py}, tools/kama-llamacpp-live.py, corpus/SOURCES.md (9 rows S066–S074, first added in 1471344), .ufo/waves/round-21/sources/{census-before.txt,validate-before.txt}, round-18 receipts 1–3. `git check-ignore -v` on key artifacts: no hits.
- Fleet HEAD during the window: `/home/vgpnk/Projects/shokunin/.git/logs/HEAD` line 753 (1792578942, tameshi report) → 7fd7c785a918131a8eb11793bca7857201e9867f; line 754 (1792581575, mori report) → 9881be6cedd48c5222ade2ccf132f7f6273e2b16 (after the run). Fleet HEAD at run start = 7fd7c785… [INFERENCE: no reflog gap].

## 3. Lane working tree now (read-only; `GIT_OPTIONAL_LOCKS=0`)
- `GIT_OPTIONAL_LOCKS=0 git diff --name-status | cat; echo exit=$?` → `M SCORECARD.md`, `M tests/llamacpp-live/check-receipt.py`, `M tools/kama-llamacpp-live.py`, `M tools/report-landing-audit.py`; exit=0. `git diff --cached --name-status` empty; HEAD = master = a6617149.
- Modification times: SCORECARD.md 11:19:11; check-receipt.py 11:21:47; report-landing-audit.py and kama-llamacpp-live.py 11:23:17. All after the run (11:14:00–11:14:13) and after commit a6617149 (11:14:24). Blob hashes of HEAD copies equal b76727f3's.
- Diff content (committed → working tree):
  - tools/report-landing-audit.py (+128 diff lines): `audit_round` now reads `git show HEAD:<fleet report>` when no explicit path is given ("committed fleet bytes, not a possibly edited working-tree copy"). The committed (measured) version read `Path(fleet_repo)/rel` from the working tree. Also new selftest cases (boundary commit, ambiguous-prefix via hash-object, committed-report-bytes-not-worktree) and changed expected values (required 4→5, round_commits 5→6).
  - tests/llamacpp-live/check-receipt.py (+8 lines): selftest case `links-unicode-canonical-valid` only.
  - tools/kama-llamacpp-live.py (+3 lines): selftest assertion that links_digest is key-sorted only.
- `ps -eo pid,etimes,args | grep -E 'llama-server|kama-llamacpp-live' | grep -v grep` → no output, `grep_exit=1` (none alive now).
- `id -u` = 1000 (vgpnk). `git ls-files --others --ignored --exclude-standard | wc -l` = 1004 (mostly .jj/ state and tools/__pycache__); non-ignored untracked: .ufo/waves/round-21/falsify (905), build (2), wave-accounting.py.
- Fleet `git status --porcelain -- .ufo/reports` (GIT_OPTIONAL_LOCKS=0) → only `?? .ufo/reports/round-20/souji.md`; no tracked kama report modified.

## 4. Rerun of recipe commands from committed bytes (scratch clone at b76727f3; porcelain 0)
Excluded (bounds): c2-live-receipt and c2-producer-selftest (launch the live tool), nh-snapshot-selftest (fixture HTTP server; not claim-bearing).
Results (exit | stdout sha | stderr sha vs recorded):
- Exact (exit, stdout, stderr all equal): c1-audit-selftest, c1-audit-raw, c1-audit-ledger, c2-grid-selftest, c2-grid-frozen, c2-grid-current, c2-grid-both, c2-gate-selftest, c2-live-gate-pinned (uses recorded live-receipt.json copied into scratch out dir), c2-live-gate-wrong-links-pin, c2-legacy-receipt-1, -2, -3, c2-legacy-receipt-1-required, nh-error-pair, nh-error-selftest, nh-install-tree-grid-selftest, nh-gguf-selftest, nh-citation, nh-sources-append-only, fr-sources-validate, fr-sources-census. (22)
- Exact after fix: c1-absent-at-base (exit 128, stderr sha 50a4efdf… equal); nh-gguf-measure (stdout sha equal with recorded `/usr/bin/python3`; my first harness used sys.executable `/usr/bin/python` and differed only in that path string).
- Partial: nh-citation-selftest — exit 0 and stdout equal; stderr differs because citation-provenance.py:129 uses `tempfile.TemporaryDirectory(prefix="citation-provenance-")`; two fresh runs print different random names (`7qilr8yh`, `5etoah6w`; recorded `0152l2gx`).
- Harness bug (mine, now fixed): the first harness appended `--fleet-repo` to any argv containing `report-landing-audit.py`, which also matched the `git cat-file` line; git exited 129 (usage). Fixed by name-keyed injection (only c1-audit-raw and c1-audit-ledger); exit 128 and stderr equal.
- Fleet dependence: C1 reruns used `--fleet-repo /home/vgpnk/Projects/shokunin` explicitly (the tool defaults to the lane's parent directory; the clone lives elsewhere). Results equal the recorded results, so kama round-10–20 reports at the fleet working tree now equal those used at 11:14.

Extra checks (not in recipe; scratch clone; exits as shown):
- check-receipt.py receipt-2.json --require-install-links → exit 1, "INVALID … --require-install-links given but receipt has no server.install_links block".
- check-receipt.py receipt-3.json --require-install-links → exit 1, same message.
- report-landing-audit.py --rounds 3 --json --fleet-repo <fleet> → exit 2, stderr "could-not-evaluate: cannot read …/.ufo/reports/round-3/kama.md".
- report-landing-audit.py --rounds 21 --report 21=<clone>/.ufo/waves/round-21/build/out/ReportFormatDraft/r21-draft.md --json → exit 1; summary defects 3, all landed-omitted: b76727f3, 4e75d9e85ba4bb26e17fb6a5e48922c349e2a19b, 1471344b4c8ba4dcd20405f500741eab9b3c1183; required 4 (cutoff = now; clone history stops at b76727f3, so a6617149 is absent; with the lane's full history the same draft would also omit a6617149 [INFERENCE]).

## 5. C1/C2 separability (lesson lines 29–32; not a recipe command) — eval cell, exit 0
- Clone reverted to base for the C2 files (`git checkout 7a6bc911 -- tools/kama-llamacpp-live.py tests/llamacpp-live/check-receipt.py`; install-links-grid.py absent at base → removed): c1-absent-at-base, c1-audit-selftest, c1-audit-raw, c1-audit-ledger all match recorded exit, stdout and stderr.
- Clone with C1 files removed (report-landing-audit.py and report-landing-errata.tsv are absent at base): c2-grid-selftest, c2-grid-frozen, c2-grid-current, c2-grid-both, c2-gate-selftest, c2-live-gate-pinned, c2-live-gate-wrong-links-pin, c2-legacy-receipt-1/2/3, c2-legacy-receipt-1-required all match recorded.
- Clone restored: `git status --porcelain` empty; HEAD = master = b76727f3.

## 6. Lesson claims → recipe coverage
Strength: E = exit code only; J = stdout/JSON read by hand, not asserted; N = no command.
| Claim (lesson line) | Command | Asserted by recipe | Check result |
|---|---|---|---|
| C1 detects "four" kinds (L12) | none | N | tool has 5 (report-landing-audit.py:61–62); lesson wrong |
| 9 defects r10–20: 1 splice, 8 omissions (L14–15) | c1-audit-raw | E (exit 1; count J) | JSON: 9 = landed-omitted 8 (r10×1, r18×3, r20×4) + unresolved-full-hash 1 (r20); required 42; post_report 4 (r19) |
| 11 scouts, 0 FP/0 FN (L15–16) | none | N | hand recounts in build advice only |
| round-21 report passes before fleet commit (L17) | none | N | current draft exit 1, 3 landed-omitted (§4) |
| ledger "9→0 is bookkeeping" (L18–19) | c1-audit-ledger | E (exit 0 ⇒ uncorrected 0; corrected 9 in JSON) | corrected 9/9 |
| selftest 32/32 (Wave-1 section) | c1-audit-selftest | E + stdout | "selftest cases=32 failed=0" |
| tool absent at round start | c1-absent-at-base | E (128) + stderr | "exists on disk, but not in 7a6bc91" |
| exit 2 for git/range/path errors (Wave-1) | selftest cases | via selftest asserts | is_error checks EvalError → CLI returns 2 (report-landing-audit.py:503–511) |
| AuditEarlyRounds exit 2 at round 3 | none | N | my run: exit 2 |
| C1/C2 file sets separable (L29–32) | none | N | §5: holds both directions |
| C2 frozen link 0/13, subdir 0/1, regular 3/3, type 1/1, null 0/1 (L20–26) | c2-grid-frozen | E (exit 1 = fail as designed; J counts) | JSON: link 0/13, subdir 0/1, regular 3/3, type 1/1, null 0/1, status fail |
| C2 current link 13/13, subdir 1/1 … real tree gate-clean (L20–26) | c2-grid-current | E (exit 0 = pass) + J | JSON: link 13/13, subdir 1/1, regular 3/3, type 1/1, null 0/1, real_tree_gate_clean true |
| install_tree_sha256 unchanged (L24–26) | c2-grid-both | J only (exit 1 comes from frozen arm) | JSON back_compat_install_tree_sha256_equal true; both = 6c216313… |
| grid selftest cells (Wave-1) | c2-grid-selftest | E + stdout (13 ok lines) | 13/13 ok |
| gate 11 VALID + 1 NOT-EVALUATED, 91 mutations | c2-gate-selftest | E + stdout | matches |
| producer fails closed (unreadable, lstat/readlink, control-char, non-regular) | c2-producer-selftest | E (exit 0) — not rerun | kama-llamacpp-live.py:1144–1157; unreadable check conditional on `not os.access(lib, R_OK)` (vacuous under root) |
| live v3 receipt: 10 links, digest 5cb9f486…, VALID with pins | c2-live-receipt + c2-live-gate-pinned | E | 10 install_links keys (verified); pinned gate exit 0, VALID |
| INVALID with wrong links pin | c2-live-gate-wrong-links-pin | E + stdout | "server.install_links_sha256 5cb9f486… != expected 0000…" |
| ephemeral llama-server, torn down | none | N | ps: none alive (state now, not at run) |
| three R18 legacy receipts VALID | c2-legacy-receipt-1/2/3 | E | all exit 0 |
| INVALID with --require-install-links (three receipts) | c2-legacy-receipt-1-required only | E on receipt 1 | receipts 2 and 3 also exit 1 (§4) |
| Frontier census before 65 rows (L57) | none (tracked file census-before.txt) | N | file matches; not produced by recipe at 7a6bc91 |
| Frontier census after 74 (A70 B1 C3; mined 60 queued 7 rejected 7) | fr-sources-census | E + stdout | matches |
| validate exit 0 | fr-sources-validate | E | exit 0, but 8 W04 duplicate-URL warnings (was 6; new S067, S071) |
| S066–S074 quotes ≤25 words verbatim with location/URL/date/revision (L34–50) | none; nh-citation checks cite() tokens only (citation-provenance.py:9–14) | N | unmeasured |
| S001–S065 unchanged | nh-sources-append-only | E + stdout ("no append-only violations"; 9 added) | matches |

## 7. Measurement-design observations
- Exit-code-only contract: 28 declared exits are checked; no stdout/JSON assertion exists in recipe.json. Numeric claims (9 defects; 0/13; 13/13; back-compat) are transcribed by hand.
- Clean-start guard: run.py takes revision from refs/heads/master but checks status of the working tree; it does not check HEAD == master and ignores ignored files. No post-run guard. The run left no visible ignored artifacts: tests/llamacpp-live/__pycache__ dir mtime 08:07:36 -0300 (11:07:36) and tools/__pycache__/*.pyc mtimes 10:45 UTC, both before the run.
- Environment not recorded in commands.json: python /usr/bin/python3 (3.14.8), git 2.56.0, fleet HEAD (7fd7c785… per §2).
- Fleet-root dependencies: fr-* run /home/vgpnk/Projects/shokunin/scripts/sources-census.sh (mtime Oct 19 21:22, fleet repo, not in lane) against the lane path, not the commit; currently SOURCES.md byte-equal to committed (sha equal to a6617149 blob: SAME).
- Post-run tool edit (§3) changes detector input from working-tree to committed fleet bytes; the recorded C1 numbers were produced by the working-tree-reading version.

## 8. Commands not run
c2-live-receipt and c2-producer-selftest (tools/kama-llamacpp-live.py launch paths; bound: never launch the live tool), nh-snapshot-selftest (fixture HTTP server). No llama-server launched; no model downloaded; no install performed (git 2.56.0 and /usr/bin/python3 3.14.8 already present).
