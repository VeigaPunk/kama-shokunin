# S9Lesson report — round-49 lesson draft

Verdict: drafted `.ufo/waves/round-49/w1/out/S9Lesson/round-49.md` in the round-48 shape with measured-value placeholders; the three required Mistakes rows each carry a command I ran whose output shows the fix failing on the round-48 state; Gate admits S494/S495 and rejects six shortcuts with S1Gate's probe receipts plus one stub run of my own; two coordination findings (one operator-side, one lane-tree) for the L1. No counter was run; no measurement is claimed.

## Deliverable

- `.ufo/waves/round-49/w1/out/S9Lesson/round-49.md` — header metadata, `## Claims` (C1/C2 with measured-value placeholders filled at integration, plus clearly-labelled build-time values), `## Gate` (S494/S495 admits, six rejects, the recurring prompt-route note), `## Mistakes` (R2/R3/R4), `### Wave` (composition + placeholders), `### Draft provenance`.
- Receipts copied beside it: `share-recount.out`, `stub-health-props.out`, `r2-placeholder-recheck.out`, `r3-precheck.out`.

## Evidence

All commands were run from `/home/vgpnk/Projects/shokunin` or the lane root; the lane was read-only throughout (no `git add/commit/checkout/stash/reset`, no jj mutation).

1. **Frozen inputs.**
   - `.ufo/waves/round-49/freeze/prereg-time-check.out` → `rev=36d5ed2681111b68c180f8ab1646d8dc9beaedee … RESULT pass … exit=0`.
   - `sha256sum tools/round49-replay-witness-audit.py tools/round49-append-audit-v4-check.py` → `86b4a40d…f0d6c1` and `26c465a9…066945`, equal to `preregistration.json` `claims[*].counter_sha256`.
   - Controls read (not re-run): `base.c1.out` `met=False`, `base.c2.out` `met=False`, `junk-c1-fake-witness` `witness=0`, `junk-c2-no-exempt` `scenarios=4/8`, `junk-c2-word-token` `scenarios=7/8`.
2. **Build receipts** (the L1's runs; read, not re-executed).
   - `measured/c1-build.out`: `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, `exit=0`; `cap sparse-1e15: exit 2 setup_error 'provenance-member-sparse' executed=False`.
   - `measured/c2-build.out`: `fixture=1 lane=1 scenarios=8/8 met=True`, `exit=0`; lane `ungraded_lines 82`, event `0718b6ab` `ungraded 65 <= natively exempt 65`.
   - `measured/aoa-build.out`: event `0718b6ab SCORECARD.md … ungraded=65 … status=restored`, summary `restored=5 … regressed=0`, `exit=0`.
   - `measured/aoa-selftest-build.out`: `AOA_SELFTEST pass=30 fail=0`.
   - `measured/r48c1-build.out`: `lane=0`, `graded tool=2356 counter=2349`, `ungraded tool=65 counter=72`, `exit=1`.
3. **Gate quotes** (`grep -n` on the committed copies).
   - S494: `.ufo/waves/round-49/c1/server-README-caa8191d.md:700` holds the quoted sentence (20 words); copy mtime `2026-10-26 20:11:45 -03` (= 23:11:45Z), committed in the freeze `36d5ed26`.
   - S495: `.ufo/waves/round-49/c1/proc_pid_exe.5.txt:75-76` holds the quoted sentence (15 words); same mtime.
4. **Mistakes row 1 (R2).**
   - `git -C /home/vgpnk/Projects/shokunin show 15710a2a:.ufo/reports/round-48/kama.md | grep -cE '__[A-Z]+__'` → `5` (lines 7, 14, 15, 16, 49).
   - `git … log --format=%H -- .ufo/reports/round-48/kama.md | wc -l` → `2`; `git show --numstat dcc079e7` → `6 6`.
   - `git show -s --format='%ai %ci' 15710a2a` → author `19:58:24`, committer `19:59:10`; lane tip `4d8334af` committed `19:58:49 -0300`.
   - Precheck on the `15710a2a` bytes (run by me): five placeholder findings + the census finding, `RESULT fail findings=6 exit=1` (`S9Lesson/r2-placeholder-recheck.out`).
5. **Mistakes row 2 (R3).**
   - `grep -oP '\t[WE][0-9]+\t' .ufo/waves/round-48/census/end.out | sort | uniq -c` → `1 W01`, `93 W04`.
   - `/home/vgpnk/Projects/shokunin/.ufo/reports/round-48/kama.md:65` says `(93 W04, 0 E; …)`.
   - Precheck on the filed report (run by me): `finding: census: omits W01=1 (line(s) 65 …)`, `RESULT fail findings=1 exit=1` (`S9Lesson/r3-precheck.out`).
6. **Mistakes row 3 (R4).**
   - `~/.omp/agent/config.yml` `/task/agentModelOverrides`: `critic: "@m_kfc"`, `connector: "@m_kfc"`, `executor/scribe/simplifier/revenger/sentinel/labrat/sonic: "@m_flash"`.
   - Recount from the live map (`S9Lesson/share-recount.out`): round 48 `m_flash_live=26/69 (37.7%)`; round 49 `39/71 (54.9%)`.
   - `.ufo/reports/round-48/kama.md:13` states `42/69 (61%)` for the same role list.
   - `.ufo/prompts/kama-round-49.md:176` still quotes `critic … @m_flash`; `.ufo/waves/round-49/w1/build_spec.py:217-218` computes the share live with critic excluded.
7. **Rejects (S1Gate probes, read).** `.ufo/waves/round-49/w1/out/S1Gate/gate_rejects.out`: probe A (`/health` 200, `/props` model_path with the frozen model sha, exe python `375532f8…`, counter's only problem = exe); probe B (`-m` argv hash matches, no socket); probe C (invented vocabulary round-trips, 10/10 pieces disagree with the GGUF vocabulary). Control `junk-c1-fake-witness.c1.out` shows a copied receipt with `witness.released: true` still scoring `witness=0`.
8. **Stub run (mine).** A single loopback python stub answered `GET /health` 200, `GET /props` 200 with a model_path, and `POST /tokenize` 200; it was stopped in-process (`S9Lesson/stub-health-props.out`). `pgrep -af llama-server` → none afterwards; `pgrep -af 'http.server|kama-r49/S9Lesson'` → none.

## Findings for the L1

- **F1 (operator-side, recurring).** `.ufo/prompts/kama-round-49.md:176` still quotes the run-8 map with `critic @m_flash`, while `~/.omp/agent/config.yml` routes critic and connector `@m_kfc`. The lane's spec computes the live share, so this wave's numbers are right, but the stale quote is in the round-49 prompt again. Proposed fix (operator-owned): regenerate the prompt's route block from `agentModelOverrides` at launch, or make the spec the sole source of the share.
- **F2 (lane tree).** An untracked `corpus/lessons/round-49.md` exists in the lane working tree (`mtime 2026-10-26 20:28:48 -03`, before this draft finished; not authored by this seat). It is close to this draft, but it carries no measured placeholders, gives R2's first report time as `19:58:24` without the committer time `19:59:10`, and its row-3 fix text cites "23/69-style shares", which is not a round-48 figure. The L1 should land one reconciled version (this draft is the evidence-checked one) rather than two.
- **F3 (coordination).** S1Gate's `gate.md` was absent at draft time; only `gate_rejects.py`/`gate_rejects.out` existed. The lesson cites the probe receipt and says so. If `gate.md` lands later, the Gate prose should cite it too.

No defect was found in the frozen counters, the preregistration or the controls; nothing frozen was edited.

## Limits

- I did not run `round49-replay-witness-audit.py` or `round49-append-audit-v4-check.py`; the `met` values in the Claims are placeholders for the measured commit, and the only values quoted are the build receipts (`74558c71`), labelled as not the measurement.
- I did not start llama-server; the one local HTTP process was the /health,/props stub, torn down in-process and verified gone. A later `pgrep` shows a peer's (M1Ctr) counter run under `/fast/scratch/hyaku/kama-r49/M1Ctr/…`; that process is not this seat's and was not touched.
- No installs, no pacman, no `gh` requests, no subagents, no lane mutations. Scratch `/fast/scratch/hyaku/kama-r49/S9Lesson` removed after copying the receipts.

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Lesson/round-49.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Lesson/share-recount.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Lesson/stub-health-props.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Lesson/r2-placeholder-recheck.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Lesson/r3-precheck.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/S9Lesson.md`
