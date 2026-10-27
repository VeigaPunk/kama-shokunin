v2 wave-1 scribe seat T6Quality, round 50 (kama). Verdict: five criteria KQ80-KQ84 are drafted against the C1/C2 build at `97c864be` and anchored to the frozen counters and the two lane receipts; drafting surfaced three defects in the round-50 measurement and source set (two receipt-provenance, one at the measured tip: `corpus/SOURCES.md:251` fails the lane's own A-row guard at `97c864be` and was repaired by an in-place row rewrite at `3d42897b`), one unstated counter limit, and one citation-ordering hazard; none of them is in the criteria, the counters or the controls.

# Seat

- Round 50, lane kama, wave `w1`, seat **T6Quality** (scribe). Assignment: draft `corpus/QUALITY.md` criteria KQ80 onward for the build, one each for witnessed execution, process-bound evidence, teardown, order-independent audits and complete accounting, each citing `corpus/lessons/round-50.md`; deliverable `quality.md` in the seat out directory and this report.
- Judged on calibration and operability. Milestone: r50 attack and frontier.
- Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` was read-only for me except this report and my out directory. I ran no lane-mutating git or jj command, created no fixture, wrote no fleet-root file, started no server and installed no tool. My scratch `/fast/scratch/hyaku/kama-r50/T6Quality` held one `git clone --shared` used only for the `sources-append-only.py` runs (D4); it was removed with `rm -rf` before this report (`ls` -> `No such file or directory`) and no process of mine is left running.

# Behaviour (what I produced)

`quality.md` holds the exact block to append to `corpus/QUALITY.md` after line 428 (the round-49 block ends with the "Integration note (round 49, L1)" paragraph): a `## Criteria added — round 50` heading, a preamble naming the build, the receipts and the frozen counter digests, a five-row table KQ80-KQ84, and the "Drafted by wave-1 scribe T6Quality …" line that the previous three rounds carry. No line above the insertion point is rewritten — `corpus/QUALITY.md` is append-only by contract row `registry/append-only-contract.tsv:4` ("criteria appended as new rows; supersession names the old criterion").

Row content, in the order the assignment names it:

| id | subject | primary anchors at `git show 97c864be:<path>` |
|---|---|---|
| KQ80 (narrows KQ76) | witnessed execution: outside observer, exe digest, LISTEN inode owned by the pid, `descends_from` by `/proc` ppid chain, fresh nonce decoded against the observer's own vocabulary | `tools/round50-replay-bind-audit.py:297-306`, `:343-373`, `:149` |
| KQ81 | process-bound evidence: `rerun.child_pid == observed pid`; `model_mapping` from `/proc/<pid>/maps` re-opened `O_NOFOLLOW`, `fstat` dev+inode checked, hashed over the mapped size; replay refuses a mismatched mapping | `tools/kama-llamacpp-live.py:678-727`, `:1999-2005`; `tools/kama-live-replay.py:343-348`; counter `:469-476` |
| KQ82 | teardown: starter killed, whole tree gone within 30 s, port refuses; pdeathsig on the replay itself, not only live->server | `tools/kama-live-replay.py:100-109`, `:587`, `:314-318`, `:332`; counter `:497-520` |
| KQ83 | order-independent audit: birth-DAG origin, fence-aware sections (CommonMark §4.5), one trailing CR dropped from a key; swapped merge-parent fixtures identical | `tools/append-only-audit.py:480-509`, `:275-280`, `:282-324`; counter `:269-279` |
| KQ84 | complete accounting: `graded + ungraded == deleted` per event, `deleted` equal to numstat, self-reported `ungraded` bounded by the counter's own count | `tools/append-only-audit.py:522-524`; counter `:214-217`, `:68-70` |

Every Check is the command `measure.sh:19-20` itself runs, so a later round re-runs the same invocation:

- `python3 tools/round50-replay-bind-audit.py --repo <clone> --tip <tip> --scratch <dir>` -> `bind=1 teardown=1 newrow=1 bound=3/3 met=True`, `teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`.
- `python3 tools/round50-append-audit-v5-check.py --repo <clone> --tip <tip> --scratch <dir>` -> `fixture=1 lane=1 scenarios=12/12 met=True`, `lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89`.

Both `met=True` lines and the full `detail:` sets are read from the committed receipts, not from a run of mine: `.ufo/waves/round-50/measured/c1-build.out`, `c2-build.out`, and the do-nothing controls `.ufo/waves/round-50/controls/base.c1.out` (`bind=0 teardown=0 newrow=0 bound=0/3 met=False`), `base.c2.out` (`fixture=0 lane=1 scenarios=9/12 met=False`, `order-b`, `fence`, `crlf-launder` FAIL).

# Gates (run / not run)

| gate | state |
|---|---|
| KQ numbering | `grep -o 'KQ[0-9]*' corpus/QUALITY.md | sort -V | tail -1` -> `KQ79` (exit 0); the last ten rows read for format (KQ70-KQ79 and the round-47/48/49 notes, `corpus/QUALITY.md:392-428`). New ids are `KQ80`-`KQ84`, no id reused, no supersession claimed. |
| Frozen counters | `sha256sum tools/round50-replay-bind-audit.py tools/round50-append-audit-v5-check.py` -> `ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89`, `925f07a48a02ad54a9c89230aac7e54c8dafee4ba2e8a823dcb851b9cf48ca46`, equal to `preregistration.json` `claims[].counter_sha256` (exit 0). |
| Receipts committed | `git ls-tree -r --name-only HEAD .ufo/waves/round-50/measured .ufo/waves/round-50/controls` lists both counter receipts, `measure.sh` and both controls at HEAD `3b79eaddf38246c637cc7ba1a94ab363422876b6` (exit 0). |
| Counter execution | **not exercised by me.** Neither round-50 claim counter was run (no network, no llama-server); every number above is a read of a committed receipt. I state no exit code of my own for them (see D1). |
| SOURCES A-row guard (run by me) | on my own `git clone --shared` at `$S/lane` (`/fast/scratch/hyaku/kama-r50/T6Quality/lane`, removed after): `python3 tools/sources-append-only.py --from 26ecba64ad6fb571d09074b07202d1618a46ecd1 --to 97c864bead3ee4a2f629574e77263d33834ec98a` -> `error: 97c864bead3ee4a2f629574e77263d33834ec98a:corpus/SOURCES.md:251: unterminated table row (no closing pipe)`, **exit 2**; `--from 26ecba64… --to 3b79eadd…` -> `added S496 (allowed) / added S497 (allowed) / added S498 (allowed) / no append-only violations`, exit 0; `--from 97c864be… --to 3b79eadd…` -> the same `unterminated table row` error on the *from* tree, exit 2. See D4. |
| Lane state | `git status --porcelain` in the lane shows only untracked wave-1 seat outputs and the `w1.ready*` markers; no tracked file modified (exit 0). |
| Host | five `llama-server`/`kama-llamacpp-live.py` processes were alive at evidence time, all under sibling seats' scratch trees (`/fast/scratch/hyaku/kama-r50/J2NoPdeathsig/...`, `/fast/scratch/hyaku/kama-r50/Sen3Teardown/...`); none is mine, and I left them running rather than touch another seat's in-flight work. |

Full command/output/exit-code log: `.ufo/waves/round-50/w1/out/T6Quality/evidence.out` (160 lines: the read-only survey, exit 0 throughout except the deliberate `ls` probe of the absent lesson, D5, and the `sources-append-only.py` runs, which exit 2 at the measured tip — that is the defect D4).

# Touched surfaces

- Written: `.ufo/waves/round-50/w1/out/T6Quality/quality.md` (the proposed append, 13.4 KB), `.ufo/waves/round-50/w1/out/T6Quality/evidence.out`, and this report `.ufo/waves/round-50/w1/out/T6Quality.md`.
- Read only: `corpus/QUALITY.md`, `corpus/lessons/round-49.md`, `registry/append-only-contract.tsv`, `.ufo/waves/round-50/preregistration.json`, `.ufo/waves/round-50/measured/*`, `.ufo/waves/round-50/controls/*`, `.ufo/waves/round-50/{c1,c2,freeze}/`, and at the build commit `tools/{kama-live-replay.py,kama-llamacpp-live.py,append-only-audit.py,round50-replay-bind-audit.py,round50-append-audit-v5-check.py}` via `git show 97c864be:<path>`.
- Clone: `/fast/scratch/hyaku/kama-r50/T6Quality/lane` (`git clone -q --shared <lane>`, read-only use), removed with `rm -rf /fast/scratch/hyaku/kama-r50/T6Quality` before this report.
- Not touched: no lane file edited, no index/jj state changed, no commit, no push, no `agent://` message, no subagent, no pacman, no install.

# Findings

## D1 — the two counter receipts carry no command line and no exit code

- Where: `.ufo/waves/round-50/measured/c1-build.out:1` and `.ufo/waves/round-50/measured/c2-build.out:1`.
- Show: `bash -c 'for f in .ufo/waves/round-50/measured/*.out; do printf "%-24s first=%s last=%s\n" "$(basename $f)" "$(head -1 $f | cut -c1-40)" "$(tail -1 $f | cut -c1-30)"; done'` (evidence.out:61-79). Every one of the other fifteen receipts starts `$ python3 …` and ends `exit=<n>`; `c1-build.out` starts `tip=97c864be…` and ends `detail: newrow: …`, `c2-build.out` starts `tip=…` and ends `detail: lane: …`. The wrapper that writes those two lines is `measure.sh:19-22` (`{ echo "\$ $*"; "$@"; echo "exit=$?"; } > "$HERE/$name$SUF.out"`), so either these two files were produced by a call outside `run()` or were post-processed.
- Consequence: the predicates are still evidenced (`met=True` is the counter's own token, and the receipts' digests are `75b8b0d7…` and `5a97b51a…`), but a KQ63-style "exits nonzero on the defective input and the receipt carries the exit code" reading has no exit code for C1 or C2, and no command line pinning `--repo/--tip/--scratch` to the receipt.
- Fix (proposed, not applied): re-run both legs through `measure.sh`'s `run` wrapper at `97c864be` and re-file; or append one `exit=<n>` line plus the exact `$ …` line to each receipt as a correction under the append-only rule, naming the superseding text in the round's lesson. Until then the criteria cite `met=True` and not `exit 0` from these files; `quality.md`'s preamble says so.

## D2 — `measure.sh` declares twenty runs and files seventeen receipts

- Where: `.ufo/waves/round-50/measured/measure.sh:39-41` (`r48c2`, `r49c1`, `r49c2`).
- Show: `grep -c '^run ' .ufo/waves/round-50/measured/measure.sh` -> `20`; `ls .ufo/waves/round-50/measured/*.out | wc -l` -> `17`; the three names are absent from `git ls-tree` (evidence.out:47-57). Those three are the round-48 and round-49 counter legs — the regression legs a round-50 build most needs to keep green.
- Consequence: the battery's stated scope (`# Round-50 measurement: claim counters and tip regressions`) is not what the directory holds; nothing in `measured/` shows the round-48/49 counters still pass at the build.
- Fix (proposed, not applied): run the three legs at `97c864be` and commit their receipts, or have the round state in its Gate that the three regression legs were not filed, so a reader does not read seventeen receipts as the whole battery.

## D3 — the C1 witness's model-size window is not in the named limits

- Where: `tools/round50-replay-bind-audit.py:335` (`if st.st_size < 1024 or st.st_size > 64 << 20: continue`).
- Show: counters' limit list — `.ufo/waves/round-50/preregistration.json` `limits[0]`, `limits[1]` — names the in-place-rewrite case, the btrfs `dev` mismatch, the two planted canaries and the single-kill scope; none names the 1 KiB-64 MiB band, yet a model below or above it can never be witnessed (`mapped_model` returns None and `bind` fails).
- Consequence: for the round's own model (`stories260K.gguf`, ~1.7 MB) the band is harmless; for a future larger model the criterion would read red for a reason no limit states. KQ81's limit cell records the band so the criterion does not inherit an unstated one.
- Fix (proposed, not applied): add the band to the round's limit list, or state it in the counter docstring's Legs block beside the other bounds.

## D4 — the measured tip fails the lane's own SOURCES A-row guard; the fix is an in-place row rewrite one commit later

- Where: `corpus/SOURCES.md:251` (the S498 row) at `97c864be`; fixed at `3d42897b65294ad963cd3686ced4666822e0ec73`, which is **not** the measured tip.
- Show: `.ufo/waves/round-50/measured/sao-build.out` is the lane's own receipt for this leg at the measured tip — `error: 97c864be…:corpus/SOURCES.md:251: unterminated table row (no closing pipe)`, `exit=2`. I re-derived it on my own clone: `python3 tools/sources-append-only.py --from 26ecba64… --to 97c864be…` -> same error, exit 2 (evidence.out, appended section). The cause is visible in `git show 3d42897b -- corpus/SOURCES.md`: the S498 `teaches` cell carried a backtick-quoted tick (`(`)`) and a trailing citation, and the fix rewrites that cell in place — `(`) or tildes (~)` -> `or tildes`, and the tail `; full page sha256 \`c85f56cc…\`` is dropped from the row.
- Consequence: (a) any Gate that reads "regressions green at the measured tip" cannot be green on this leg — the receipt for it is red and filed in the same directory; (b) the repair is an in-place change to a registry row's `teaches` cell, which `registry/append-only-contract.tsv:6` (`corpus/SOURCES.md A-row … registry rows appended; only status, recheck and used-by change in place`) does not allow outside those three cells, and the guard cannot see it because against the base the row is an addition (`--from 26ecba64 --to 3b79eadd` -> `added S498 (allowed)`, exit 0); (c) the dropped `c85f56cc…` page digest is no longer cited, so a digest/hexrun census population changes between the two tips.
- Affects the criteria only through the source row: KQ83's fence rule cites S498, whose text still names CommonMark 0.31.2 §4.5 and its URL, so the criterion's anchor survives; nothing in KQ80-KQ84 reads the digest.
- Fix (proposed, not applied): in the lane, keep the row as it was at the build and append a correction row (or a `registry/` correction) rather than rewriting the cell, or state in the round's lesson that the row text was repaired in place with the reason; and cite the round's Gate at the tip that is green, naming which legs were measured at `97c864be` and which were re-measured after `3d42897b`.

## D5 — the lesson all five rows cite does not exist at HEAD

- Where: `corpus/lessons/round-50.md` (absent), cited by every row's "Motivating lesson" cell.
- Show: `ls corpus/lessons/round-50.md` -> `No such file or directory` at `3b79eadd` (evidence.out:110-114); the lesson directory stops at `round-49.md`.
- Consequence: expected per the assignment (the lesson lands at integration), but it fixes an ordering requirement: if the QUALITY append lands before the lesson, any future check that resolves a criterion's lesson citation reads five dangling paths. The rows cite `§Claims C1`/`C2` (the preregistration's own stable ids) plus the round-49 spot-check's §6 seats, so the citation stays resolvable in content even before the file lands; `quality.md`'s closing note states this.
- Fix (proposed, not applied): land `corpus/lessons/round-50.md` in the same integration commit as, or before, the QUALITY append.

## N1 — KQ80 vs KQ76 (not a defect, a drafting decision)

KQ76 (round 49) already requires an outside witness, the recorded binary as listener, the model as `-m` and a nonce answered by the model's own tokenizer. KQ80 therefore repeats none of it: it adds the facts round 49 lacked — the server's place in the **replay's** process tree and the replay's receipt join — and the row is marked `(narrows KQ76)`. If the L1 prefers one id per subject, KQ80 folds into KQ76 as an added clause without changing its Check.

## N2 — fence and line-ending surfaces sit inside KQ83 (drafting decision, flagged)

The assignment names one criterion for order-independence; KQ83 also carries the fence (`scenario fence`) and CRLF (`scenario crlf-launder`) surfaces because all three are the same failure class — a verdict moved by something that is not the rule — and all three come from C2. `quality.md` ends with a draft-only HTML note saying that, should the L1 want one surface per id, KQ83 splits into KQ83 (order) and one further id for fence and line ending, with no Check changed.

# Out of scope (deliberately not done)

- Neither round-50 claim counter was executed; no network fetch; no `llama-server` started or stopped. One `git clone --shared` was made under my own scratch for the `sources-append-only.py` guard (D4) and removed. The counters' operability is the L1's measured claim and the sibling seats' subject, not mine to re-derive.
- Known integration items stated in the assignment (SKILL.md instrument registry, SCORECARD/LOG/lesson/QUALITY/README entries, S496-S498 `used-by`, the gate registry's unregistered counters) are not re-reported here.
- No edit to `corpus/QUALITY.md`, `corpus/lessons/`, the counters, the preregistration or the controls; the append exists only as proposed text.

# Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T6Quality.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T6Quality/quality.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T6Quality/evidence.out`
