# RevLiveRepeat — is the frozen C1 counter's live reading reproducible run-to-run?

Seat: KamaR31.RevLiveRepeat (reviewer, leaf). Lane: kama-shokunin @ dispatch tip
`382d11b2107d335705875da1a4d889b074bd6fa6`. Counter under test:
`.ufo/waves/round-31/count-c1.py`, sha256 `d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216`
(matches `preregistration.json` C1.counter_sha256; clone's copy re-hashed).

```RESULTS
$ /usr/bin/python3 tools/instrument-agreement.py --help            # (cwd: lane repo)
exit 0
  usage: instrument-agreement.py [-h] [--runs RUNS] [--cwd CWD]
                                 [--normalize NORMALIZE] [--out OUT]
                                 [--selftest]
                                 ...
  positional arguments:
    cmd
  options:
    -h, --help            show this help message and exit
    --runs RUNS
    --cwd CWD
    --normalize NORMALIZE
    --out OUT
    --selftest

$ /usr/bin/git clone --quiet file:///home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/RevLiveRepeat/clone \
  && /usr/bin/git -C /tmp/kama-r31w2/RevLiveRepeat/clone checkout --quiet 382d11b2107d335705875da1a4d889b074bd6fa6 \
  && /usr/bin/git -C /tmp/kama-r31w2/RevLiveRepeat/clone rev-parse HEAD \
  && sha256sum /tmp/kama-r31w2/RevLiveRepeat/clone/.ufo/waves/round-31/count-c1.py
exit 0
  382d11b2107d335705875da1a4d889b074bd6fa6
  d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  /tmp/kama-r31w2/RevLiveRepeat/clone/.ufo/waves/round-31/count-c1.py

$ sha256sum ~/.local/opt/llama-b11755/llama-server ~/.local/opt/llama-b11755/libllama-server-impl.so ~/.cache/kama-shokunin/models/stories260K.gguf
exit 0
  b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804  llama-server      (== registry build.server_sha256)
  e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed  libllama-server-impl.so (== build.library_sha256)
  270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d  stories260K.gguf  (== build.model_sha256)

$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/instrument-agreement.py \
    --runs 3 --cwd /tmp/kama-r31w2/RevLiveRepeat/clone \
    --out .ufo/waves/round-31/w2/out/RevLiveRepeat/ia-receipt.json \
    -- /usr/bin/env bash -c '/usr/bin/python3 .ufo/waves/round-31/count-c1.py \
        --lane /tmp/kama-r31w2/RevLiveRepeat/clone --repo /tmp/kama-r31w2/RevLiveRepeat/clone \
        --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out "$TMPDIR/receipt.json"; \
        rc=$?; cp "$TMPDIR/receipt.json" "/tmp/kama-r31w2/RevLiveRepeat/run-receipts/receipt-$(date +%s%N)-$$.json" 2>/dev/null; exit $rc'
exit 0   (wall 0m0.908s; each run = fresh TMPDIR + own llama-server on a random free port in 47900-47998)
  IA runs=3 agree=3 disagree=0 digest=2614e9a65a3e exit=0
  (receipt ia-receipt.json: verdict "agree"; all three results share digest
   2614e9a65a3ef4011cedd914a8e4d76b3c619cb8e5d5429a1781bbd6f3eecc4e, exit 0,
   stderr_head "", stdout_head "registered 18 counted 17 target 12 met True not-counted ['K31-10']")

$ diff receipt-<run1>.json receipt-<run2>.json ; diff receipt-<run2>.json receipt-<run3>.json ; diff receipt-<run1>.json receipt-<run3>.json
exit 0 (all three; empty diffs — the three counter receipts are byte-identical)
  per-run summary in each: registered 18 counted 17 target 12 met True not-counted ['K31-10']
  per-run counted vector: [T,T,T,T,T,T,T,T,T,F,T,T,T,T,T,T,T,T]  (identical in all 3 runs)

$ for p in $(seq 47900 47998); do (echo >/dev/tcp/127.0.0.1/$p) 2>/dev/null && echo "BUSY $p"; done; pgrep -af llama-server
exit 0
  (no output — every counter-owned server exited; no port left bound)
```

Command notes: the tool's `--runs 3` was used (cheap — ~0.3s/run: stories260K loads
in well under a second on this host). No `--normalize` flag was passed: zero volatile
fields were declared. The only normalization in force is the tool's built-in
(`<TMP>` temp-dir substitution, one ISO-date rule; see `ia-receipt.json` `normalize`
array). The `bash -c` wrapper exists only to give each run a distinct `--out`
`"$TMPDIR/receipt.json"` and to copy it out before the tool deletes the temp dir —
the instrument argv, `--cwd` and exit code are exactly the preregistered counter
command. `volatile fields declared: none`.

FINDING: The frozen C1 counter's live reading IS reproducible run-to-run at the
measured tip. Three independent runs — each with a fresh TMPDIR and a freshly
started pinned llama-server on a different port — produced identical (exit,
stdout, stderr) digests (`IA runs=3 agree=3 disagree=0 digest=2614e9a65a3e`,
tool exit 0), and the three `--out` receipts are byte-identical: same summary
`registered 18 counted 17 target 12 met True not-counted ['K31-10']`, and an
identical per-row `counted` vector (17 True, K31-10 False — its `reject-message-not-adapter`
pre-live discrimination reason is deterministic, and the live block of every
other row, including the nondeterminism-sensitive `ignored` normalization and
`slot_task` ids, matched across runs). The claim "the counter's live reading is
reproducible run-to-run" survived falsification in this seat's scope.

LIMITS:
- Reproducibility, not correctness: agreement says nothing about whether the
  counted rows prove anything — `w1/out/CriticClaimSize/c1-noop.json` already
  shows a no-op registry meets `counted >= 12`, and `RevCounterFair` F1/F2
  classes stand. This run does not weaken those defects.
- N=3 on one host, one load pattern, within one minute. It does not bound
  agreement under CPU contention, partial slot reuse, an occupied-port tail, or
  a llama.cpp nondeterministic path none of the 18 rows exercises.
- Agreement is over normalized (exit, stdout, stderr) plus the byte-identical
  `--out` receipts; server-side log contents (`$TMPDIR/srv-*.log`) were not
  compared (deleted per-run; not part of the counter's output contract).
- Does not establish exit-2/retry behavior, port-exhaustion handling, or
  behavior on a tree other than `382d11b2`.
- No tools installed this seat. No tracked lane file was modified; writes were
  confined to this out directory and `/tmp/kama-r31w2/RevLiveRepeat/`.

## Raw receipts
- `ia-receipt.json` — instrument-agreement receipt (command, cwd, normalize rules, per-run digests).
- `receipt-1792796826533234321-432727.json`, `receipt-1792796826823473062-434102.json`, `receipt-1792796827118275786-435869.json` — the three counter `--out` receipts (byte-identical).
- `diff-1-2.txt`, `diff-2-3.txt`, `diff-1-3.txt` — pairwise diffs of the three receipts (all empty, exit 0).
