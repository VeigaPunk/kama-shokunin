# RV04RegistryLedger — round 63 review (registry/capability-claims-r63.tsv, host-busy row, ollama nonce, hexrun 795b7be5)

Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (lane HEAD, verified `git cat-file -t` = commit).
Scope: read-only review; no lane, fleet, or sibling file edited; no commit; no process killed. Tip-blob line numbers
are used throughout (`git show <tip>:<path>`); the lane working tree differs only in uncommitted PROVINCE.md,
corpus/SOURCES.md, corpus/knowledge/completion-request-plane.md (not in scope; registry, SCORECARD, tools clean).

## Summary

- Registry ↔ manifest ↔ canonical list: consistent. 12/12 rows bind their manifest run, pattern and binding; the
  canonical round-63 table is row-identical to round 62 (diff of table rows empty).
- Counter at tip (my own live run, `tools/round63-c2-counter.py --repo <lane> --tip 03a6…`):
  `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False`, exit 1.
  The only failing conjunct is `selfdesc_mismatches=8`, which the freeze declares on purpose (L1 re-derives SCORECARD head after measurement).
- Defects found: D1 (counter rejects the declared idle outcome of the context-capacity row: the row is busy-only in
  effect, calibration), D2 (context-capacity note misattributes the busy host; one busy process is a lane-owned orphan),
  D3 (ollama lifecycle leaks its llama-server runner grandchild; the orphan is the reason the host is busy),
  D4–D7 low (duplicated constant stanza, fixed nonce, weak selftest patterns, stray nested tree).
- hexrun ledger row 795b7be5 and `fleet-commit-evidence.json`: the claim is TRUE on independent check; the classifier
  would accept the row on a string-containment test of a lane-authored file alone; the JSON's commit subject is misquoted.

## Checks performed and results

1. Registry vs manifest (`tools/round63-c2-counter.py:52-130` MANIFEST; registry lines 2–13):
   - `quote` is a substring of the manifest prefix in all 12 rows (counter `score()` gate, no `quote:` error).
   - `run`, `pattern`, `binding` equal the manifest template in all 12 rows (no `run:`/`pattern:`/`binding:` errors).
   - Verdict column: 11 rows `true`; `context-capacity-receipt` (registry:6) `host-busy`, the only declared alternative.
   - `diff` of r62 vs r63 registry: only three rows changed — context-capacity (timeout 900→20, verdict true→host-busy,
     observed → `host-not-idle-before-K1`), live-ollama-lifecycle (nonce `ctrun`→`ctrun0001`), and the note text.
     Nothing else in the 12-row population moved.
2. Canonical list (`SCORECARD.md:3303`, round-63 table): row-identical to the round-62 table (empty diff of `^| ` rows);
   `canon_problems` returns no problem at tip; `canonical=63`.
3. Live execution of every bound row at tip (done by my counter run; each row's live output matched its pattern,
   `sensitive=12/12`). The counter's own sensitivity self-test returned `sens_selftest=4/4`.
   Standalone spot checks: `instrument-agreement.py --selftest` → `IA_SELFTEST pass=4 fail=0` rc 0;
   `append-only-audit.py --selftest` → `AOA_SELFTEST pass=51 fail=0` rc 0; `pin-watch.py selftest` rc 0.
4. Self-description reconciler at tip (`tools/round42-selfdesc-reconcile.py`): `mismatches=8`, rc 1 (matches the freeze).
   Details: banner (head lacks "Latest measured round: 63"), planned (no "### Planned (round 64)"), retired, saturation,
   caps (head mirror of 11 names, `live-ollama-lifecycle` absent), province (`PROVINCE.md lacks
   registry/ollama-live-claims-r61.tsv`), r41 coverage count. All are the SCORECARD/PROVINCE re-derivation the freeze defers to L1.

## Item A — ollama nonce (harness rule `NONCE_RE`)

- Rule: `tools/kama-ollama-live.py:69` (and identical duplicate at :109) `NONCE_RE = ^[a-z0-9]{8,32}$`; enforced at :316
  (`nonce-invalid` → SETUP_ERROR). Nonce use: model name `kama-{nonce}` (:409), witness `ready.json` (:497).
- Row: `registry/capability-claims-r63.tsv:13` run `--nonce ctrun0001`. `re.match` of `ctrun0001` → True (9 chars).
  The r62 value `ctrun` (5 chars) → False, consistent with the note's "nonce-invalid". Note text is accurate.
- Live: the counter's live row returned `"verdict": "MODEL_OK"` (covered, sensitive) at tip.
- D5 (low, calibration): the nonce is a constant in the manifest (`counter MANIFEST live-ollama-lifecycle`), so the
  "nonce" carries no per-run freshness. Isolation today comes from the per-work ollama home, not from the nonce.
  The row should say the nonce is a format-valid label, not a freshness token, or the manifest should draw a fresh nonce.

## Item B — context-capacity-receipt host-busy row (registry:6)

Process facts at measurement (`pgrep -x llama-server`, `ps -o pid,ppid,pgid,etime`):

| pid | ppid | pgid | etime | what | owner |
|---|---|---|---|---|---|
| 1706355 | 1494 (systemd --user) | — | 07:52 | `llama-server --port 1234` | operator (the freeze names 1234) |
| 242776 | 1706355 | — | 07:26 | `llama-server --port 45669` | operator (the freeze names 45669) |
| 3262613 | 1494 (systemd --user) | 3262524 (leader gone) | 12:03 | ollama-runner `llama-server --model /fast/scratch/hyaku/kama-r61-closure/c1/c1-9z8mmjqy/run-pd/...` `--port 37323` | **lane-owned orphan**: its scratch dir no longer exists |
| 2406236/2556904/2829015 | — | — | transient | `llama-server --alias kama-completion-probe` (lane tool child, concurrent seats) | lane tools |

Counter code path (checked, not inferred): `tools/kama-context-capacity.py:218-238` `live_llama_server_pids` counts
**every** `llama-server` pid (not only foreign ones); `:241-258` `wait_for_host_idle` waits up to `--host-idle-timeout`
then raises `host-not-idle-before-K1`; `:821-823` maps SetupError to exit 2. The row's mechanism sentence is accurate.

- D2 (medium, honesty of row note): registry:6 says the refusal happens "while any foreign llama-server runs; this host
  keeps operator llama-servers up". Accurate about the mechanism; incomplete about the cause. At measurement, one of the
  four busy processes is a lane-owned orphan 12 h old (3262613) and the rest of the set is lane-tool children from
  concurrent seats. The row's `host-busy` verdict therefore depends on leaked and concurrent lane processes, not on the
  operator alone. The note should name the orphan and say the state is not stable across runs.

- D1 (medium-high, calibration — the row is busy-only in the counter, contrary to its declared two outcomes):
  `tools/round63-c2-counter.py:320-325` accepts either outcome in the verdict check (`ok = outcome in declared and
  (outcome == rec or 'alt' in tpl)`) but then compares the recorded `observed` against the outcome's own text:
  `want_obs = tpl['pattern'] if outcome == 'true' else tpl.get('alt')` (:324) and mismatches += 1 when observed is not in
  it (:325). Registry:6 observed is `host-not-idle-before-K1`, so a run with `outcome == 'true'` (idle host,
  `"all_ports_closed": true`) scores a mismatch and met=False. Synthetic check (`out/RV04RegistryLedger/synth.py`,
  scoring the real MANIFEST and real tip registry text with a stubbed scorer):
  `idle mismatches= 1 covered= 12 errors= 0 host_busy= 0 met_is= False`;
  `busy mismatches= 0 covered= 12 errors= 0 host_busy= 1 met_is= True`.
  So the freeze's predicate ("equals the recorded verdict or is one of the row's two declared outcomes") is not what the
  counter does: the idle outcome is declared in the row note (registry:6 "idle host emits all_ports_closed true") and in
  the manifest (`'alt': HOSTBUSY_TEXT`, counter:79) yet fails. Consequence: the row passes only while a busy host, and
  therefore partly while the orphan of D3 lives. Fix options (for L1, not applied here): compare `observed` against the
  pattern of whichever outcome actually occurred for alt rows, or leave observed as the declared alternative and state
  that only the busy outcome is accepted.

## Item C — hexrun-ledger row 795b7be5 and fleet-commit-evidence.json

- Row: `registry/hexrun-ledger.tsv:125` `795b7be5… upstream VeigaPunk/shokunin .ufo/waves/round-63/census/fleet-commit-evidence.json 2026-10-28`.
- Independent checks (read-only):
  - `git -C /home/vgpnk/Projects/shokunin cat-file -t 795b7be5…` → `commit`.
  - `git -C …/shokunin merge-base --is-ancestor 795b7be5… origin/master` → rc 0 (reachable from fleet origin/master).
  - `git show -s` of that commit: author kama-shokunin, `round-62: file honest-stop report for dispatched unsettled wave`;
    `git show --stat`: `.ufo/reports/round-62/kama.md | 50 +++` (the report exists at that commit).
  - `git -C …/kama-shokunin cat-file -t 795b7be5…` → `fatal: could not get object info` rc 128. Expected: the lane is its own
    repo (origin `VeigaPunk/kama-shokunin.git`); the commit lives in the fleet repo (origin `VeigaPunk/shokunin.git`).
  - The evidence blob is tracked at tip: `git ls-tree 03a6…:.ufo/waves/round-63/census/` lists `fleet-commit-evidence.json`.
  - `corpus/lessons/round-62-verifier-spotcheck.md:7` cites `fleet commit 795b7be5…` (matches the row note).
- Classifier: `tools/hexrun-census.py:248-253` `upstream_ok` only checks that the evidence blob **contains the token and
  the repo string** (`VeigaPunk/shokunin`). It never resolves the object. The census therefore certifies a row whose
  existence proof is a lane-authored JSON, not the upstream object. The row is true here, but the classifier would also
  accept it if the commit did not exist. This is a design limit of the `upstream` class (the same holds for the round-43
  rows), not a defect in this row's content; state it in the census contract if it is kept.
- D6 (low, evidence text): `fleet-commit-evidence.json` "commits" value reads `2026-10-28 round-62: file honest-stop report
  for dispatched unsettled wave (kama report)`. The commit subject is `round-62: file honest-stop report for dispatched
  unsettled wave` (no date prefix, no `(kama report)` suffix). Quote the subject exactly or drop the prefix/suffix.

## Additional defects found while verifying

- D3 (medium, operability — ollama teardown leak; cause of the host-busy orphan): `tools/kama-ollama-live.py` arms
  PR_SET_PDEATHSIG only on the `ollama serve` child (`:352-355`, preexec `_child_pdeathsig` at :77-96) and tears down by
  `os.killpg` of that child (`:524`, `:532`). The llama-server runner that `ollama serve` spawns is in the same session
  but is neither armed nor tracked; no runner pid appears in the receipt. Evidence: pid 3262613 (runner, `--port 37323`)
  is alive 12 h later, ppid 1494 (reparented to systemd --user), its group leader 3262524 has exited, and its scratch dir
  `kama-r61-closure/c1/c1-9z8mmjqy/run-pd` is deleted. The `run-pd` name suggests a parent-death test. [INFERENCE]: the
  Python parent died before `finally` ran, `serve` took the pdeathsig SIGKILL, and the runner survived. Not verified by a
  receipt (none survives). Route to L1/C1 (ollama lifecycle owner). I did not kill it (not spawned by me).
- D4 (low, maintainability): `tools/kama-ollama-live.py:66-73` and `:106-113` are a duplicated module-constant stanza
  (REPO, PIN_FILE, REGISTERED_PORTS, NONCE_RE, READY_TIMEOUT, CREATE_TIMEOUT, GENERATE_TIMEOUT, TEARDOWN_TIMEOUT). Harmless
  today; delete one copy.
- D7 (low, weak pattern): `registry/capability-claims-r63.tsv:7` (`instrument-agreement`, pattern `IA_SELFTEST pass=`) and
  `:11` (`append-only-audit`, pattern `AOA_SELFTEST pass=`) bind only the prefix; the count and `fail=0` are not in the pattern.
  Binding relies on exit 0 (`instrument-agreement.py:117`, `append-only-audit.py:1481` return 1 when fails > 0), so the row is
  true in practice. Use the full `pass=N fail=0` literal as `live-receipt-replay` (`:12`, `KLR_SELFTEST pass=48 fail=0`) does.
- D8 (low, hygiene; not in the registry): untracked nested tree `kama-shokunin/kama-shokunin/.ufo/waves/round-62/w1/A04C1SchemaFuzz.md`
  inside the lane (lane `git status`: `?? kama-shokunin/`). It differs from the tracked
  `.ufo/waves/round-62/w1/A04C1SchemaFuzz.md` (cmp: differs at byte 168). A misrouted write; remove by its owner, not by this seat.

## Verification gaps

- The C2 counter's own C1-side tests (round63-c1-counter) were not run here (out of this item).
- The `live-llamacpp-lifecycle` and `live-ollama-lifecycle` rows were exercised only through the counter's live run
  (one run each). Repeat runs were not made; the host-busy conclusion in D1/D2 holds only for the process set observed here.
- The 3262613 orphan's origin is inferred from process facts; no receipt for the deleted closure run survives.
- Mutation testing of the counter was not part of this item (assigned to mutation-testers).

## Tool and install record

No tool installed or updated. Used `git`, `pgrep`, `ps`, `python3` (stdlib) only. No pacman transaction.

## Receipts

`.ufo/waves/round-63/w1/out/RV04RegistryLedger/`: `c2run.out` (counter one-line, exit), `c2run.err`, `selfdesc.out`
(reconciler, tip), `synth.py` (D1 synthetic scoring), `ia.out`, `aoa.out` (weak-pattern selftests).

## Tally (counter output at tip, measured by this seat)

population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False (exit 1; the failing conjunct is selfdesc_mismatches=8, declared by the freeze)
