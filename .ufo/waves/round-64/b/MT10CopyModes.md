# MT10CopyModes — C1 counter falsification (round 64, wave b)

Seat: MT10CopyModes (leaf, no subagents). Attack item: mutate `tools/round64-c1-counter.py` in the
scratch clone the way a lazy author would, and replay forged tools; run with the forge patches
removed. Tip under test: `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a` (frozen). Evidence:
`.ufo/waves/round-64/b/out/MT10CopyModes/` (SUMMARY.txt, SHAS.txt, per-run stdout/stderr, mutant
copies, forgery diffs, drivers). Scratch removed after copy. Tools installed: none.

## Result in one paragraph

The unmutated counter prints `met=True` at the frozen tip (21 of 21 unmutated runs). Identity
binding holds against every mutant that touches the holder, exe, ancestry or start-tick rules:
those KILL. Two forged tools that differ from the tip only by a one- or two-line edit still pass
the unmutated counter with `met=True` and exit 0 (F1 future-dated `hold.json`, F2 an unchecked
extra server flag). Five counter mutants SURVIVE (a2, d1, d2, e1, e2b): a control is not
targeted, or a credit path needs no evidence that the scenario ran. A relaxed guard for
crash-before-hold is credited (e2b) because no control exercises it (e1). Two operability
defects are also confirmed: a reused `--work` directory makes the second run fail, and the
swap-answer control depends on the drawn probes.

## Baseline (frozen tip, unmutated)

    tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]

Exit 0 in all 21 unmutated runs (base, base-r1/r2, 6 flake, 12 rate runs, all fresh `--work`).

## Method

- Mutants: edited `tools/round64-c1-counter.py` in clone `$S/clone` (checked out at the frozen tip),
  installed the mutant at the clone path, ran `python3 tools/round64-c1-counter.py --repo <clone>
  --tip <frozen> --work <fresh>`, saved stdout/stderr, then `git checkout --` the counter. Every run
  used a fresh work dir (a reused dir produced false failures; see F-ops-1).
- Forgeries and no-patch tree: commits in a second clone `$S/clone2` (tool edits only), scored by the
  unmutated counter from the clone path. Diffs in `out/f1/tool.diff`, `out/f2.diff`.
- Each survivor was re-run; F1 and F2 were re-run and gave `met=True` three times each.
- Procfs evidence: `drv_evidence.py` imports the committed counter, runs one live `witness_run`,
  re-scores exactly as `main()` does, and prints the snapshot the binding decided on.

## Counter mutants (attack items a–e)

Verdict: KILLED = `met=False` and the named control escapes; SURVIVED = `met=True`.

| id | mutation | verdict | escapes (family) | deciding procfs observation (or absence) |
|---|---|---|---|---|
| a1 | drop the holder-pid-set rule from `bind_holders` (global) | KILLED | bind 18/20, proxy 0/1, forge 0/3 | `/proc/net/tcp` listener inodes -> `/proc/<pid>/fd` holder set vs `hold_pid`; proxy's holder is the forwarder itself (python exe), not the hold pid |
| a2 | proxy scenario credited under `bind_exe` instead of `bind_holders` (scenario-only skip) | SURVIVED | none | the proxy's holder pid != hold pid AND exe is python; both fail, but the credit names `bind_exe`, so the holder rule is never the discriminating check for that control |
| b1 | `hold_fresh` ignores holder `start_ticks` >= tool ticks | KILLED | bind 19/20 (hold_fresh #2) | `/proc/<pid>/stat` field 22 start ticks vs tool's ticks |
| b2 | `hold_fresh` ignores hold.json mtime | KILLED | bind 19/20 (hold_fresh #1); stalehold stays 2/2 | `stat(hold.json).st_mtime_ns` vs `t0_ns` |
| b3 | `hold_fresh` keeps only `mtime > t0` (drops holder-presence and ticks) | KILLED | bind 19/20; stalehold 1/2 (stale_future escapes) | with the holder requirement gone, stale_future's future mtime passes; its current rejection is the closed old port (no holders) |
| c1 | drop the ancestry rule (`tool_pid` in holder ppid chain) | KILLED | bind 19/20 (tool_pid=1 control); detach 0/1 | `/proc/<pid>/stat` field 4 ppid chain; detach server's chain lacks the tool pid. Reruns: detach nfails=0 once ancestry is gone |
| d1 | a missing forge patch is counted as rejected | SURVIVED | none (prints forge=3/3 on the no-patch tip) | git blob absence of the two patch files at the tip; no run occurs |
| d2 | forge variants never run, counted as rejected | SURVIVED | none (2/2 clean runs met=True) | absence of `work/forged-<name>/receipt.json` and any `/proc` snapshot; the counter does not check either |
| e1 | fake guard relaxed to `r is None` (no crash scenario added) | SURVIVED | none | no control reaches the guard; the 76 fakes all write hold.json |
| e2a | crash-before-hold fake (writes genuine receipt copy, exits) with guard intact | KILLED | detach 0/1 | absence of hold.json: `witness` None, no snapshot; message `no receipt/witness ['tool exited before hold.json']` |
| e2b | same fake, guard relaxed to `r is None` | SURVIVED | none (detach 1/1 credited) | absence of any `/proc` snapshot (raw_a None); every bind check fails on None, but the credit names `bind_ancestry` and the receipt copy is genuine, so clean_receipt passes |

Counter one-liners (full, verbatim from the run outputs):

    a1 : tool_present=1 live_ok=1/1 controls_targeted=70/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=18/20 canned=1/1 detach=1/1 digest=1/1 forge=0/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=0/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    a2 : tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    b1 : tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=19/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    b2 : tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=19/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    b3 : tool_present=1 live_ok=1/1 controls_targeted=74/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=19/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=1/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    c1 : tool_present=1 live_ok=1/1 controls_targeted=74/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=19/20 canned=1/1 detach=0/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    d1 : tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]   (run on the no-patch tip)
    d2 : tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]   (re-run twice clean; the first run hit an unrelated runfield flake, see F-ops-2)
    e1 : tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    e2a: tool_present=1 live_ok=1/1 controls_targeted=75/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=20/20 canned=1/1 detach=0/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
    e2b: tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]

## Forged tools that the unmutated counter accepts (SURVIVED forgeries)

### F1 — future-dated hold.json around a genuine live holder (freshness)

Minimal tool edit (2 lines, `tools/kama-completion-live.py`, after `json.dump(hold_doc, ...)`):

    +            _fut = time.time() + 3600.0
    +            os.utime(os.path.join(hold, 'hold.json'), (_fut, _fut))

Tip `b873f96668858f9263f64d82da7b721723858aa1`, unmutated counter:

    tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]

Reproduced 3 of 3. Procfs evidence (drv_evidence.py): hold.json mtime is +3600.4 s from t0
(`now - mtime = -3599.5 s`); holder pid is the pinned server, `/proc/<pid>/exe` re-hashes to the
pinned digest, its ppid chain includes the tool pid, `start_ticks - tool_ticks = 18`; both probe
answers equal the reference answers. The identity binding is intact; the freeze's clause
"the hold.json is fresh" is not. Cause: `hold_fresh` only checks `mt > t0` (no upper bound), and
the `stale_future` control is rejected by its closed port, not by freshness (b3 proves it).

### F2 — pinned server launched with an extra argv flag the counter never inspects

Minimal tool edit (1 line, `tools/kama-completion-live.py` argv list): add `'--metrics',` after
`'-c', str(args.ctx), '-t', str(args.threads),`. Tip `1199731fbfecc389165caca2588ac948f958303e`:

    tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]

Reproduced 3 of 3. Evidence: the holder's `/proc/<pid>/cmdline` is
`llama-server --model … --alias kama-completion-probe --port … --host 127.0.0.1 -c 512 -t 1 --metrics`.
`bind_argv` checks only `--port`, `--host`, `--alias`, `--model`; `-c`, `-t` and any extra flag go
unchecked. Probe answers equal the reference. Freeze clause broken: "argv … are the pinned set".
Severity: identity intact (genuine binary, descendant, correct exe hash), but a flag such as
`--slot-save-path` or `--log-file` would be accepted with the same probe answers.

Both forgeries are the valuable finding for C1. Under the freeze's own clauses C1 is not met at
these tips even though the counter exits 0.

## Forge patches removed from the tip tree

Commit `942fe8d2c144c12c887ad635f2b0e6315945d469` removes `controls/forge-A-realchild.patch` and
`forge-B-sleeper-delta.patch`. Unmutated counter:

    tool_present=1 live_ok=1/1 controls_targeted=73/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=0/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]

stderr: `forge forgeA: patch did not apply to the tip tool` (x3). KILLED (met=False, forge 0/3). The
message says "did not apply" but the patch files are absent; wording is misleading, the count is right.
With the d1 credit mutant on the same tip, `met=True` (SURVIVED; one-liner in the table).

## Operability findings (not mutants)

- F-ops-1 (reused `--work`): the second run in the same work dir prints `met=False` with
  `families[... canned=0/1 detach=0/1 pathcopy=0/1 preload=0/1 proxy=0/1 stalehold=0/2]` and
  `error: fake detach: no receipt/witness ['tool exited before hold.json']`. A stale `hold/release`
  file makes the fake return before the counter observes hold.json. The C1 counter has no
  reuse refusal (C2 has `work-reused`). Fails closed here, but it is a false negative and the
  one-liner does not say why.
  Second-run one-liner: `tool_present=1 live_ok=1/1 controls_targeted=69/76 of 76 families_exact=0 missing_families=[] eval_selftest=3/3 errors=0 met=False`
- F-ops-2 (swap control is data-dependent): `runfield/live_ref_text` escapes exactly when the two
  drawn probes have identical reference answers (the swapped answer then equals the reference). In
  a direct draw of the counter's own probe code, the two answers matched in 3 of 25 and 3 of 200
  draws (6/225). The escape occurred once, in one of the three d2 runs; it did not occur in any of
  the 21 unmutated runs. Fix: redraw the probe pair until the reference texts differ.
- F-ops-3 (one unexplained observation): the first c1 run reported detach `fails=['bind_holders']`,
  not `bind_ancestry`. Two re-runs of the same mutant gave detach `nfails=0`, and four standalone
  detach runs gave `fails=['bind_ancestry']`. Not reproduced; I did not identify the cause. The
  holder scan fails closed on unreadable own-uid fd tables, and seats share the uid, so host
  process-table state is the likely source. Recorded as unexplained, not as a verdict.

## Recommended minimal fixes (for the L1 to integrate; nothing applied here)

1. `hold_fresh`: add an upper bound (`mt <= counter's read time + slack`); add live control
   `forge_future_hold` = F1 edit, expecting `hold_fresh`.
2. `bind_argv`: compare the full cmdline to the expected list (or forbid unknown flags); add live
   control `forge_extra_flag` = F2 edit, expecting `bind_argv`.
3. Scenario table: pin the control->check table with a sha256 in the freeze so a renamed expectation
   is visible (a2); each credited scenario must prove it ran (per-scenario receipt and hold dir
   present, distinct pid and ticks from the tool), which closes d1/d2.
4. Crash-before-hold: keep the `r is None or w is None or b is None` guard, and add control
   `crash_before_hold` (genuine receipt copy, exit before hold.json) expecting `bind_listener`
   (no listener, no snapshot). That exercises the guard (e1, e2b).
5. Refuse a non-empty `--work` (as C2 does), or create a fresh `mkdtemp` per run.
6. Swap control: redraw the probe pair while the reference texts are equal.

## Counter one-liner for the baseline (frozen tip)

    tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True families[bind=20/20 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 relabel=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]

Tally: mutants 11 (KILLED 6: a1, b1, b2, b3, c1, e2a; SURVIVED 5: a2, d1, d2, e1, e2b);
forgeries 2 SURVIVED (F1, F2); no-patch tip KILLED (met=False, forge 0/3). Unmutated runs 21/21 met=True.
