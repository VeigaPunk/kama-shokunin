# K03MetaLoopCritic: do round-60 C1/C2 repeat the "instrument grades instrument" pattern?

Seat: critic, advisory. Lane tree read-only; no lane edits. Base ec3b0d58, tip 11f2d667 (freeze e0b5b1ea, controls 8b9f3060).

## Verdict in one paragraph
Round 60 leaves the pattern in SURFACE (C1 starts a real server; C2 compares lane prose to live bytes) but repeats it in
VERIFIER SHAPE: each counter accepts a decoy that never touches the claimed surface. I ran both decoys (below). Rounds
56/57/59 were rejected by a non-author closure running exactly this kind of no-op/decoy fixture against the counter
(MANIFEST kama rows 56/57/59; lessons/round-59-verifier-spotcheck.md: "R04 decoy", "K05/M12 semantic bypass").
The same closure move defeats C1 and C2 as frozen.

## Counts (commands run in /home/vgpnk/Projects/shokunin/kama-shokunin)
- `ls tools/round[0-9][0-9]-* | wc -l` = 56 of 85 files in tools/ (30 are not round-prefixed; `ls tools | grep -vc '^round[0-9][0-9]-'`).
- `grep -l 'tools/round' tools/round*.py | wc -l` = 18 (loose: includes self-name in usage docstrings; r60 counters hit only themselves).
- Exact-name references to ANOTHER existing roundNN tool file (python scan, regex on real filenames): 14 of 56 (25%):
  r38-operability-audit, r42-digest-audit, r42-selfdesc-reconcile, r43-registry-audit (18 refs), r45-claim-outcome-audit-v2,
  r46-release-recheck-audit, r50-append-audit-v5-check, r56-env-leg-battery, r56-prereg-check, r58-battery-exec-check,
  r58-c1-counter, r58-c2-counter, r59-battery-outcome-check, r59-c1-counter, r59-c2-counter. (Prefix-only variant, any other `roundNN-` token: 12.)
  Rounds 56-59: 10 files (r56 4, r57 0, r58 3, r59 3); 7 of those 10 grade another round tool; the 3 that do not are r56-env-leg-test, r56-replay-code-audit, r59... (the two r56 leaf tools and r56-replay-code-audit).
- Round 60: tools/round60-c1-counter.py and round60-c2-counter.py reference only themselves (`grep -o 'round[0-9][0-9]-[a-z0-9-]*\.py' tools/round60-*.py`). So by this count r60 breaks the chain. The frozen frontier tool tools/round60-supersession-check.py does not exist yet at tip.
  Caveat: C1's tool tools/kama-ollama-live.py is not round-prefixed; the prefix count understates tool lineage.

## Per claim: surface, do-nothing control, instrument-grades-instrument
### C1 (live Ollama lifecycle)
- Real surface: a real ollama v0.40.11 process, loopback port, imported model, /api/* bodies, serve.log. Committed receipt shows a genuine run (log lines `Listening on 127.0.0.1:58921 (version 0.40.11)`, GIN lines).
- Do-nothing control (controls/c1-base.out: tool absent -> met=False) only reaches "tool missing". It cannot reach a tool that runs no server.
- Instrument grading instrument: tools/round60-c1-counter.py `verify()` grades artifacts produced by author tool tools/kama-ollama-live.py. The counter never launches, observes, or fingerprints the server process; it reads receipt JSON + serve.log + manifest + blob from the dir the tool wrote. Everything it "re-derives" is author-writable.
- Executed counterexample (decoy tool, no Ollama executed, fixture repo under /fast/scratch, removed after):
  decoy tools/kama-ollama-live.py replays the committed receipt with the counter's nonce, rewrites sha256, writes serve.log from
  .ufo/waves/round-60/live/serve-lines.txt, a manifest file and a copied blob; emits BINARY_DIGEST_MISMATCH when --ollama-bin is passed.
  `python3 tools/round60-c1-counter.py --repo <fixture> --tip <HEAD> --work <scratch>` ->
  `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=3/3 log_rejected=1/1 errors=0 met=True`, exit 0, 0.13 s wall.
  Direct call of the counter's `verify()` on hand-built artifacts also returned `[]`.
  Impacted: freeze.txt C1 sentence "independent verifier re-derives ... from the run's own work dir"; kill rule has no decoy control (7 controls are fake binary, stale nonce, receipt tamper, log removal: all single-artifact).
- Smallest safe correction (not applied): counter-side process witness. While run_tool runs, the counter polls /proc for a pid whose /proc/PID/exe sha256 == FROZEN_BIN_SHA and which owns a LISTEN socket on the receipt's port (inode from /proc/net/tcp), then requires that pid gone at teardown; add the decoy above as an 8th control (must be rejected). Optionally count genuine liveness by a counter-chosen prompt/seed the tool cannot know in advance.
### C2 (calibration of INFERENCE statements)
- Real surface: 14 base lines of lane documents vs bodies in one committed live receipt. This is the only part that can move calibration: it can find a lane statement the server contradicts. Observed in receipt: tags digest 8cf91c7109e7... equals ps digest (digest join holds for this run) but differs from the imported GGUF sha 270cba1b... (so the crosswalk line 45 phrase "only digest is content-addressed" is a candidate contradiction for GGUF-content identity; [INFERENCE] that 8cf91c... is the manifest digest; not verified, manifest not kept).
- Do-nothing control (controls/c2-base.out: registry absent, covered=0/14) reaches only "registry missing" (c2-freeze-tip.out also rows=0, so C2 is entirely unbuilt at freeze).
- Instrument grading instrument: partly. The counter's 5 control families are run by the counter on the author's own registry; and `receipt_caps()` trusts self-contained hashes (see below). Mostly it grades author data (registry) against author-produced receipt, not another tool.
- Executed counterexample (scratch script, read-only on lane): population from base = 14 lines; registry with 6 rows whose predicate is `len(c['version']['version'])>0` (true, falsifiable by mutation, unrelated to the quoted claims) on 6 lines and `not-observable` (reason >= 20 chars) on the other 8:
  `score()` -> rows=14 covered=14 evaluated=6 eval_lines=6 sensitive=6 bound=6 contradicted=0 amended=0 receipt_ok=True errors=0 met=True;
  `controls()` -> tautology 1/1, verdict_flip 6/6, quote_corrupt 14/14, drop_line 14/14, tamper 1/1 (all rejected).
  So no clause binds predicate meaning to quote, and "falsifiable" is syntactic (any capture mutation flips it).
  Also: editing ps-after.expires_at and recomputing that capture's sha256 keeps `receipt_ok=True` (hash and body live in the same file); C2 does not tie the receipt to the C1 counter's run.
  Also: nothing requires a lane document to change (labels stay INFERENCE); an all-confirmed outcome is met with zero amendment.
- Smallest safe correction (not applied): freeze per-line required capture paths before data (e.g. line 44/46 -> ps-after.models[*].expires_at; line 45/302 -> tags and ps-after digest join) and require the row predicate chains to cover them; add a "vacuous predicate" 6th control (the version-string row above must be rejected); bind receipt_caps to the receipt's git blob hash recorded in a frozen file or in C1's counter output.

## Which part is again an instrument grading an instrument
- C1 verify() over tool-written artifacts: yes (author tool -> author counter, no counter-owned witness). The real server is real, but the counter cannot tell.
- C2 falsifiable/bound machinery: grades its own predicate language, not the claims; moderate.
- The tooling lineage: 14/56 round tools grade other round tools; r60 counters do not, so the chain itself is not extended.
- Not that pattern: the committed live receipt, the pinned binary digest, the SOURCES rows and the census (external surfaces).

## Clause judged most likely rejected by a non-author closure
C1 predicate clause "independent verifier accepts [the run] and each of its 7 controls is rejected" together with the sentence "re-derives ... from the run's own work dir": a 40-line decoy tool meets it in 0.13 s (shown above), and the round-59 closure rejected on precisely this decoy move (R04 runner decoy). Runner-up, close: C2 "every predicate is falsifiable" (syntactic; vacuous-predicate registry reaches met=True with all 5 controls rejecting).
