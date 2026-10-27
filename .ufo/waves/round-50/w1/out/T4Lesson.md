# T4Lesson — round-50 lesson draft (kama, wave 1)

**Verdict:** drafted — `round-50.md` follows the round-49 lesson shape with Claims placeholders, three admits and three grounded rejects in the Gate, and four Mistakes rows (three required classes, none invented); five defects found, two of them new this round and none patched (lane and counters are frozen).

Deliverable: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/round-50.md`.
Every receipt this report cites is under `.ufo/waves/round-50/w1/out/T4Lesson/evidence/`; scratch `/fast/scratch/hyaku/kama-r50/T4Lesson` was removed at the end. Nothing on the lane, in the counters, the preregistration or the controls was edited.

## What was done

| # | Step | Command | Exit | Outcome |
|---|---|---|---|---|
| 1 | Read the contract | `sed -n '1,60p' tools/round50-replay-bind-audit.py`, `sed -n '1,110p' tools/round50-append-audit-v5-check.py`, `.ufo/waves/round-50/preregistration.json` | — | claims, predicates, limits, frozen names read |
| 2 | Verify the frozen counters | `git show <rev>:<counter> \| sha256sum` at `601c8889` and `97c864be` | 0 | `ff6ac2ac…c5e89` / `925f07a4…ca46`, both equal to the prereg `counter_sha256` (evidence in the table above; also S2Gate2 F2) |
| 3 | Gate quotes | `python3 evidence/gate-quotes.py` | 0 | `S496 words=12 verbatim=True`, `S497 words=20 verbatim=True`, `S498 words=17 verbatim=True`, `RESULT gate_quotes_bad=0` (`evidence/gate-quotes.out`) |
| 4 | R2/R3 checker on filed bytes | `python3 .ufo/waves/round-49/w1/out/S9Mistakes/report-precheck.py --report evidence/r48-report-at-15710a2a.md --census .ufo/waves/round-48/census/end.out` | 1 | `findings=6 exit=1` (5 placeholders + `omits W01=1`) — the round-49 closure defect reproduces (`evidence/precheck-r48-15710a2a.out`) |
| 5 | Same checker on the corrected round-49 report | `… --report /home/vgpnk/Projects/shokunin/.ufo/reports/round-49/kama.md --census .ufo/waves/round-49/census/end.out [--census …/start.out]` | 1 | `findings=2` (or `4` with both receipts): `count W04: report says 1 … carries 93` + `omits W01=1` — the checker cannot read the report's `W01=1 W04=93` (`evidence/precheck-r49-report.out`, `evidence/precheck-r49-report-bothcensus.out`) |
| 6 | Fix shown able to fail | patched copy at `$S/precheck-patched.py`, same two reports | 1 / 0 | round-48 bytes still `findings=6 exit=1`; round-49 report `RESULT pass findings=0 exit=0` (`evidence/precheck-patched-both-reports.out`, `evidence/proposed-report-precheck-fix.diff`) |
| 7 | Reject: environ alone | `python3 evidence/reject-probes/environ-snapshot.py` | 0 | child's own `os.environ` carries `KAMA_R50_CANARY`; `/proc/<pid>/environ` does not (267 keys) (`evidence/reject-environ.out`) |
| 8 | Reject: maps dev/inode alone | `python3 evidence/reject-probes/maps-inode.py` | 0 | in-place rewrite: maps line and `stat()` keep `103:05` / inode `1220126573`, sha256 `53137a63…` → `f8332a00…`, `hash changed, dev/inode identical: True` (`evidence/reject-maps-inode.out`) |
| 9 | Reject: pdeathsig alone | read `S2Gate2/exp3-pdeathsig.out` (S2Gate2's run, not mine) | 0 | `ignore_survives=True`, `fork_grandchild_survives=True`, `default_child_dies=True` |
| 10 | Stale "live map" count | `python3 evidence/reject-probes/live-map-count.py` | 0 | tuple flash 37 (56.1%), attack 20 (30.3%), neither **9**; live map agrees today (37); on a config copy with `executor: "@m_kfc"` the live count drops to 15 while the tuple stays 37 (`evidence/live-map-count.out`) |
| 11 | Build-tip sweep | `python3 evidence/sweep-build-tip.py --repo $S/lane [--selftest]` and `--repo <lane>` | 0 | selftest `PASS` (planted receipt at base citing the build → `PREDATES`); lane: `rows=148 predates=0` over 8 committed and 140 uncommitted receipts (`evidence/sweep-build-tip.out`, `evidence/sweep-build-tip-tree.out`) |
| 12 | S498 row vs the lane's parser | `python3 tools/sources-append-only.py --from 26ecba64… --to 97c864be…` and `--to 3d42897b…` | 2 / 0 | `error: 97c864be…:corpus/SOURCES.md:251: unterminated table row (no closing pipe)` at the build; `added S496/S497/S498 (allowed) … no append-only violations` after the build-fix (`evidence/sao-build-and-fix.out`) |

## Defects (file, line, command, proposed fix)

**D1 — `corpus/SOURCES.md:251` (S498) located quote is not verbatim.** The cell reads `"A code fence is a sequence of at least three consecutive backtick characters or tildes."`; the copy holds `backtick characters (`) or tildes (~)`, so the row drops the two parentheticals mid-sentence. Command: `python3 .ufo/waves/round-50/w1/out/T4Lesson/evidence/gate-quotes.py` → `S498 row quote … verbatim=False verbatim_in_parts=False` while `S498 gate quote: words=17 <=25=True verbatim=True`. Proposed replacement for the quote cell (verbatim, no backticks, so the row parser stays happy): `"A fenced code block begins with a code fence, preceded by up to three spaces of indentation."` (17 words, verified present). The lesson's Gate row uses the full verbatim sentence and flags the row.

**D2 — `.ufo/waves/round-50/build_spec.py:203-205` counts against a frozen tuple under the label "live map".** `flash = sum(c[r] for r in ("executor", "labrat", "scribe", "sonic", "simplifier", "revenger", "sentinel"))` and the `print(… "flash(live map, critic=@m_kfc excluded)" …)` never open `~/.omp/agent/config.yml`; the wave also holds 9 seats (connector 5, scout 4) in neither bucket, so `flash 37 + attack 20` leaves 9 of 66 unexplained. Command: `python3 .ufo/waves/round-50/w1/out/T4Lesson/evidence/reject-probes/live-map-count.py` → today's live map agrees (37, 56.1%; connector `@m_kfc`, scout `@m_sonnet`), but with `executor: "@m_kfc"` in a config copy the live count is 15 and the tuple is still 37. Proposed fix: compute `flash` as `sum(n for role,n in roles.items() if overrides[role] == "@m_flash")` read from the live config the same way the X16Policy seat's item specifies, and print the three buckets (flash / attack / neither) so the totals partition.

**D3 — `.ufo/waves/round-49/w1/out/S9Mistakes/report-precheck.py:51` cannot read a `CODE=count` census line, so the fix for R3 has no passing case on the report it protects.** `CLAIM_RE` only matches `count CODE`; on `.ufo/reports/round-49/kama.md:58` (`W01=1 W04=93`) it reads `1 W04` and reports `count W04: report says 1, receipt end.out carries 93` plus `omits W01=1` (exit 1). Command in row 5 above. Proposed fix (full diff at `evidence/proposed-report-precheck-fix.diff`): accept `CODE=count` as a second alternative and add `=` to the count's negative lookbehind; with it the round-49 report passes (0 findings) and the round-48 filed bytes still fail (6 findings).

**D4 — `tools/round50-replay-bind-audit.py:529-539` (`newrow_leg`) counts a SOURCES row the lane's own parser rejects.** At the build tip the S498 row is malformed (`line 251`, no closing pipe), yet `measured/c1-build.out` reports `newrow: 3 rows new since base` because the leg keeps any line whose first four non-leading-space characters are `| S<digit>`. Command: row 12 above (`exit=2` at `97c864be`, `exit=0` at `3d42897b`). This is within the counter's literal predicate ("has a registry row"), so it is a limit, not a contract breach; proposed fix if the L1 wants the stronger leg next round: require the line to end with `|` or parse it with the sources tool's row grammar, and let the S498-style row fail closed.

**D5 — cross-reference, verified by reading the code, owned by seat S2Gate2: both frozen counters write `--out` after printing the summary and without creating the parent.** `tools/round50-append-audit-v5-check.py:537` and `tools/round50-replay-bind-audit.py:597`: `if a.out: with open(a.out, "w") …`. A missing parent directory prints `met=True` and then exits 1 — the contract's "not met" code — with the receipt lost (`S2Gate2/gate.md` F1 shows the traceback). Proposed fix (theirs, not applied): `os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)` before the open, or catch `OSError` and return 2 with `could-not-write-receipt: …`.

## Limits of this draft

- Measured values are placeholders: this seat did not run the C1 counter (46 s, three servers, network) or the C2 counter; the build-battery receipts (`measured/*-build.out`) and S2Gate2's independent runs are cited as dry runs and independent readings, not as the round measurement.
- The lesson's Claims describe the mechanics as read from the build code; no claim about a measured `met` is made here.
- `report-precheck.py` is a precheck, not a counter: it cannot see R2's in-place rewrite of filed bytes (it reads one file), and that limit is unchanged by D3.
- The sweep's `rows=120` is a snapshot of the wave as of this seat's run; later seat receipts are not covered.

## Environment / tooling

No installs or upgrades (`python3` stdlib, `git` read-only, `diff`, `sha256sum`). No llama-server was started by this seat: `pgrep -f llama-server` is not claimed clean for peers' processes, and nothing under `/fast/scratch/hyaku/kama-r50/T4Lesson` survives (`rm -rf` at the end).

## Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/round-50.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/gate-quotes.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/gate-quotes.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/reject-probes/environ-snapshot.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/reject-probes/maps-inode.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/reject-probes/live-map-count.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/reject-environ.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/reject-maps-inode.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/live-map-count.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/precheck-r48-15710a2a.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/precheck-r49-report.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/precheck-r49-report-bothcensus.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/precheck-patched-both-reports.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/proposed-report-precheck-fix.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/r48-report-at-15710a2a.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/sweep-build-tip.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/sweep-build-tip.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/sweep-build-tip-tree.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T4Lesson/evidence/sao-build-and-fix.out`
