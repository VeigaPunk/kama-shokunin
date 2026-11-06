# Round-89 SCORECARD draft (seat SB01ScorecardDraft) — DO NOT LAND THIS FILE

This file is the draft plus its provenance. The landing form that the lane's own counters accept is
`scorecard-draft.patch` (SCORECARD.md + PROVINCE.md only), verified at scratch draft commit
`e2e9399c7d8353b0747a0f40de694d3ab558aad2` (see `counters-draft.out`).

Placement map:

| # | Deliverable | Lands where |
|---|---|---|
| 1 | new `## Round 89` section | appended at the end of `SCORECARD.md`, after `## Round 88` |
| 2 | canonical capability list `**Capabilities — canonical list as of round 89**` | last block of that new section, before `### Round-89 disclosed limits` |
| 3 | head `## Capabilities` mirror | its intro sentence re-points to §Round 89 and its table becomes the same rows |
| 4 | `### Planned (round 90)` | in `## Planned`, above `### Planned (round 89)` |
| 5 | head / Axes / Retired / Saturation / PROVINCE edits | forced by the lane's own counters; see §5 |
| 6 | number provenance | §6 (drop before landing) |

---

## 1. New section

## Round 89 — unloadable router model files and a wire-bound router error table (2026-11-06)

Fresh-start round after six rejected closures (rounds 83-88). Base `56174a1fa6a27faa91d3664ef4730b48dd3149c0`;
frozen plan `plans/round-89-claims.md`, counters `tools/round89-unloadable-cells.py` and
`tools/round89-signature-rows.py`, frozen at `4eb75c62f6deb1a586a291d611b71775049b34a6`. Two claims on two
axes, causally separable (C1's counter never reads `SKILL.md`; C2's counter never runs the probe or a
server). **No canned expectation**: every C1 cell's expected verdict is the router's answer to a real
completion at run time, and every C2 row binds to a captured wire answer.

| Claim | Axis | Counting command | Before (base, committed receipt) | Target |
|---|---|---|---|---|
| C1 unloadable router model files (capability `router-unloadable-file-verdict`, sourced S583/S584/S585) | operability | `python3 tools/round89-unloadable-cells.py --repo . --rev <M> --work <scratch>` | `ROUTER_UNLOADABLE cells=11 mismatches=5 positive_mismatches=0 probe=rev`, exit 1, probe `99dd1ab8…` (`.ufo/waves/round-89/controls/c1-base.out`); forgeries F1 `mismatches=3 positive_mismatches=3` (`controls/c1-f1.out`), F2 `mismatches=7 positive_mismatches=2` (`controls/c1-f2.out`) | `cells=11 mismatches=0 positive_mismatches=0 probe=rev`, exit 0, probe `a4f496bb…`; counter bytes equal to freeze; the five harm receipts (`controls/harm-base-probe-verdicts.out`, `controls/harm-base-test-snapshot.out`, `controls/harm-base-r88-oracle.out`, `controls/harm-base-r88-cells.out`, `controls/harm-base-operator-1234.out`) unchanged |
| C2 router error signature table (capability `router-error-signature-table`) | depth | `python3 tools/round89-signature-rows.py --repo . --rev <M2>` | `SIGNATURE_ROWS rows=0 bound=0 unbound=0 duplicates=0`, exit 1 (`.ufo/waves/round-89/controls/c2-base.out`); forgery battery `rows=7 bound=1 unbound=5 duplicates=1`, exit 1 (`controls/c2-forgeries.out`) | `rows=8 bound=8 unbound=0 duplicates=0`, exit 0; counter bytes equal to freeze |

Receipt summary lines, verbatim (`.ufo/waves/round-89/`):

- `controls/c1-base.out` line 13 — `ROUTER_UNLOADABLE cells=11 mismatches=5 positive_mismatches=0 probe=rev probe_sha256=99dd1ab8d41bb682bb24d4747b85d1f86fb84c145c6531cd2f0201d738d54be5 server_sha256=ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0 rev=56174a1fa6a27faa91d3664ef4730b48dd3149c0` (exit 1, line 14)
- `controls/c1-f1.out` line 13 — `ROUTER_UNLOADABLE cells=11 mismatches=3 positive_mismatches=3 probe=rev probe_sha256=bd7a6a2228d04b69abcc5d19f2907a9caf737347ef96ff92722edbc3180e7bdf server_sha256=ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0 rev=138a75437bcd11b72446087e970f5dfc5abf9ccd`
- `controls/c1-f2.out` line 13 — `ROUTER_UNLOADABLE cells=11 mismatches=7 positive_mismatches=2 probe=rev probe_sha256=0943fb461d0226e29d1b8a3b6af67740d4fe6863505ee6ed771719a30fdc3d19 server_sha256=ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0 rev=9b4c7af16fdd4bba9e4815f4615f4b003f340747`
- `controls/c2-base.out` line 2 — `SIGNATURE_ROWS rows=0 bound=0 unbound=0 duplicates=0 rev=56174a1fa6a27faa91d3664ef4730b48dd3149c0` (exit 1, line 3)
- `controls/c2-forgeries.out` line 22 — `SIGNATURE_ROWS rows=7 bound=1 unbound=5 duplicates=1 rev=0c09884dad924640b92135209b9fc7e361f991ee` (exit 1, line 23)
- `measured/c1.out` line 14 — `ROUTER_UNLOADABLE cells=11 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=a4f496bb0ed931792641171a1269a91a8307dce5d534d5f4ee03daba01a7ddaf server_sha256=ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0 rev=4f9eacf720aa59ed806b31b758571e364658179b` (exit 0, line 15)
- `measured/c2.out` line 11 — `SIGNATURE_ROWS rows=8 bound=8 unbound=0 duplicates=0 rev=21b9e36d6192e0a691550b32e0e6c38412227f4c` (exit 0, line 12)
- `measured/harm-M.out` line 2 — `tests=72 passes=72 failures=0` (exit 0, line 3); line 4 — `RESULT pass=30 fail=0` (exit 0, line 5)
- `measured/harm-M.out` line 10 — `ORACLE_CELLS rev=4f9eacf720aa59ed806b31b758571e364658179b cells=3 mismatches=0` (exit 0, line 11)
- `measured/harm-M.out` line 16 — `ROUTER_CELLS cells=17 mismatches=2 canned=14 live=3 probe=rev probe_sha256=a4f496bb0ed931792641171a1269a91a8307dce5d534d5f4ee03daba01a7ddaf` (exit 1, line 17; the two are C05 and C12, lines 13 and 15 — the frozen counter's expected residual, not a green)
- `measured/host-gguf-sweep.out` line 38 — `HOST_GGUF_SWEEP files=36 ok=36` (no loadable local file graded invalid)

### Round-89 measured results

| Claim | Measured commit | Counting command → output | Verdict (author) |
|---|---|---|---|
| C1 operability | `4f9eacf720aa59ed806b31b758571e364658179b` | `python3 tools/round89-unloadable-cells.py --repo . --rev 4f9eacf7… --work <scratch>` → `ROUTER_UNLOADABLE cells=11 mismatches=0 positive_mismatches=0 probe=rev`, exit 0; counter sha256 `1d86194c…` at M equal to freeze (line 1 of `measured/c1.out`); harm (`measured/harm-M.out`): `tests=72 passes=72 failures=0`, `RESULT pass=30 fail=0`, `ORACLE_CELLS … cells=3 mismatches=0`, `ROUTER_CELLS … mismatches=2` (C05, C12), operator router GET `MODEL_OK router-unloaded-autoload` on all four entries | Frozen predicate met at M: K1 `positive_mismatches=0`; K2 every harm receipt agrees with its base counterpart (the round-88 counter keeps its own residual, C05 and C12); K3 the counter's bytes are unchanged from the freeze. |
| C2 depth | `21b9e36d6192e0a691550b32e0e6c38412227f4c` | `python3 tools/round89-signature-rows.py --repo . --rev 21b9e36d…` → `SIGNATURE_ROWS rows=8 bound=8 unbound=0 duplicates=0`, exit 0; counter sha256 `30f3af7f…` at M2 equal to freeze (line 1 of `measured/c2.out`) | Frozen predicate met at M2; K2 holds — no row carries a message the receipt does not hold (the forgery battery's fabricated row was unbound at base). |

Score deltas: none claimed — no axis score moves this round. Two capabilities enter the repertoire with
first-working round 89, and the `router-mode-readiness` row's evidence pointer is re-pointed so it names
a green of the landed rule (round-88 closure D1/R2).

### Round-89 disclosed limits

- The probe reads the GGUF **header only** and never opens a non-regular file or any tensor data, so a file
  whose header parses but whose tensor payload is corrupt still grades `MODEL_OK`; only a real load tells.
- The file check runs only when `status.args[0]` is a local file as this host sees it. A containerised or
  remote router, a relative path, an unknown tensor type and a parse-budget overrun keep the previous
  verdict on purpose: a false red is worse than the known false green.
- Operator-router evidence differs in form between base and M (base: one registry row,
  `model_ok=1 drift=0 exit=0`; M: per-model lines, `MODEL_OK router-unloaded-autoload` on four entries);
  both receipts agree on the verdict and neither loads a model.

---

## 2. Canonical capability list (inside the new section)

The two rows `router-unloadable-file-verdict` and `router-error-signature-table` are new; the
`router-mode-readiness` row is the corrected one. Changed rows in the head mirror are the same three.

Corrected `router-mode-readiness` evidence pointer (replaces the superseded `ROUTER_CELLS cells=17
mismatches=0` green at `138a7543`, round-88 spotcheck D1 / ruling R2):

    tools/kama-probe.sh, tools/round88-router-cells.py,
    .ufo/waves/round-88/repair/oracle-cells.py (ORACLE_CELLS
    rev=8b5bb69df0f7cd7302db2964354f5d7a0ba8f4b7 cells=3 mismatches=0,
    .ufo/waves/round-88/repair/oracle-cells-repair.out),
    .ufo/waves/round-89/measured/harm-M.out (ORACLE_CELLS
    rev=4f9eacf720aa59ed806b31b758571e364658179b cells=3 mismatches=0);
    the round-88 frozen counter's own residual is mismatches=2 (C05, C12) at both base and M,
    never cited as a green

**Capabilities — canonical list as of round 89**

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
| late-delta | Re-derive a late register's round delta against the frozen generator: carried rows bound byte-wise to the base revision, new rows by cell and by accepting/deletion round order | `tools/round82-late-delta.py` | 82 |
| selfrecord-round81 | Re-derive six declared facts of the round-81 self-record at the sealed revision and grade dated value-bound corrections whose fix path carries the new token at the tip | `tools/round82-selfrecord-round81.py` | 82 |
| sources-registry | Curate where kama learns: tier-scoped, revision-anchored rows; contract-v1 census clean | `corpus/SOURCES.md` | 10 |
| append-debt | Grade the append-only acceptance population under a late-acceptance rule: a later round's row binds by strict ancestry and round order and accepts what the frozen cutoff cannot | `tools/round81-append-debt.py`, `registry/append-only-late.tsv` | 81 |
| ollama-offline-evidence-replay | Reconcile caller-supplied `/api/tags` + `/api/ps` captures fail-closed | `tools/kama-ollama-evidence.py` | 14 |
| live-llamacpp-lifecycle | Start the pinned llama.cpp server on an unregistered loopback port, capture loading/ready surfaces, grade, tear down | `.ufo/waves/round-16/live/receipt.json` | 16 |
| gguf-declared-identity-replay | Decode bounded local GGUF metadata offline and compare declared metadata with a captured receipt | `tools/gguf-identity.py` | 20 |
| context-capacity-receipt | Run the registered context-capacity cells on the lane-owned llama.cpp fixture and write a sha256-bound receipt | `tools/kama-context-capacity.py` | 25 |
| instrument-agreement | Run a lane instrument N times over one tree and emit a receipt with per-run digests and an agreement counter | `tools/instrument-agreement.py` | 30 |
| pin-watch | List upstream release tags for each pinned serving engine and report the newest tag and how many releases sort above it | `tools/pin-watch.py` | 41 |
| digest-ledger | Classify every full SHA-256 the lane's documents cite: committed blob, ledger-declared external artifact, unverifiable with reason, or flagged known-wrong | `tools/digest-ledger.py` | 42 |
| hexrun-census | Classify every lower-case hex run of 32–127 chars the lane's documents cite | `tools/hexrun-census.py` | 43 |
| append-only-audit | Grade the lane's contract-declared append-only self-description against its git history, every deleted line accounted | `tools/append-only-audit.py` | 46 |
| live-receipt-replay | Re-acquire a pinned receipt's server archive and model from recorded https URLs, verify sha256 before execution, re-run the lifecycle from an empty home | `tools/kama-live-replay.py` | 47 |
| live-ollama-lifecycle | Start the pinned Ollama binary on an unregistered loopback port, create a qualified model, capture surfaces, grade, tear down | `tools/kama-ollama-live.py` | 61 |
| worktree-landing-check | Prove at report time that each declared self-record path's worktree bytes are byte-identical to its HEAD blob | `tools/round67-worktree-landing-check.py` | 67 |
| receipt-pointer-audit | Audit every section-relative `measured/…` receipt citation against an append-only ledger whose own target must exist | `tools/round68-receipt-pointer-audit.py` | 68 |
| newest-closure-counter | Resolve the lane's newest non-author closure mechanically and fail when the calibration row names an older one | `tools/round69-newest-closure-counter.py` | 69 |
| pre-report-gate | Run the round's reconciled instruments as ONE gate; exit 0 only when every arm is green and the tree is clean | `tools/pre-report-gate.py` | 71 |
| province-host-claims | Re-derive every `province-host:` marker against the live host and require a later dated correction | `tools/round71-province-host-claims.py` | 71 |
| round-scope | Grade a round's own scope as a verdict: frozen plan at the tip, no uncommitted record path, no ignored wave path | `tools/round72-round-scope.py` | 72 |
| receipt-tip-binding | Bind every cited receipt to the revision it measured: header names an ancestor and the `rev..tip` delta touches only record paths | `tools/round72-receipt-tip-binding.py` | 72 |
| round-scope-cases | Grade linked-worktree dirt, newer-round ignored work and nested submodule dirt in addition to the inherited scope cases | `tools/round73-round-scope-cases.py` | 73 |
| receipt-claim-binding | Reject a three-token tip claim whose cited receipt header names another revision; real records use explicit revisions | `tools/round73-receipt-claim-binding.py` | 73 |
| province-host-drift | Compare the newest recorded kernel/architecture/distribution triple with the live triple | `tools/round73-province-host-drift.py` | 73 |
| selfdesc-canon | Resolve the capability repertoire from the newest capability table by round number regardless of heading markup | `tools/round74-selfdesc-canon.py` | 74 |
| receipt-claim-v2 | Bind a self-record's receipt citations by explicit revision with paragraph-scoped claim grading | `tools/round74-receipt-claim-binding.py` | 74 |
| province-host-drift-v2 | Require every `recorded at <rev>` host block to be byte-identical at its recorded revision and the tip | `tools/round74-province-host-drift.py` | 74 |
| interpretation-pins | Bind the lane's two routed interpretation debts to boundary fixtures whose declared reading the committed module produces and whose reversed reading a mutated copy is caught producing | `tools/round75-interpretation-pins.py` | 75 |
| survivor-probe | Certify the shipped receipt-claim arms by source mutation: five named mutants must each turn their owning selftest arm red | `tools/round75-survivor-probe.py` | 75 |
| append-accepted | Grade every audit-undisclosed deletion event as accepted history through a committed, hash- and class-bound register with the temporal cutoff | `tools/round75-append-accepted.py` | 75 |
| receipt-scope | Classify a self-record's citation population: fenced quotation excluded, self-description deltas non-shifting, every live citation named | `tools/round76-receipt-scope.py` | 76 |
| selfrecord-facts | Re-derive eight declared self-record facts at the revisions they name and count value-bound corrections | `tools/round76-selfrecord-facts.py` | 76 |
| append-exempt-class | Account every audit event once and preserve a multi-register introduction cutoff — **partial**: the round-76 counter is red on its own target (`unaccounted=41` at its audit revision) and stays as the historical probe; `append-registers` (round 77) and `append-registers-tip` (round 78) supersede the accounting | `tools/round76-append-exempt.py` | 76 |
| citation-baseline | Bind a pre-round measurement receipt by header ancestry and byte reproducibility at its introducing commit while the at-the-tip delta rule still shifts ordinary receipts | `tools/round77-citation-baseline.py` | 77 |
| append-registers | Account every audit event once across two registers with independent introduction cutoffs, the audit's `permitted` carriage class and the contract's `out_of_region` class, with rotation detection | `tools/round77-append-registers.py` | 77 |
| selfrecord-round76 | Re-derive six sealed round-76 facts and accept only value-bound corrections whose stated value re-derives | `tools/round77-selfrecord-round76.py` | 77 |
| selfrecord-round77 | Re-derive six declared facts of the round-77 self-record at the sealed revision and grade dated value-bound corrections | `tools/round78-selfrecord-round77.py` | 78 |
| append-registers-tip | Account every append-only audit event at the audited revision with ancestry-filtered, commit-bound register rows and both register digests | `tools/round78-append-registers.py` | 78 |
| live-reconcile | Exercise the probe's MODEL_OK / MODEL_MISMATCH / DEAD verdicts end-to-end against the pinned llama.cpp child on an unregistered loopback port | `tools/round78-live-reconcile.py` | 78 |
| selfrecord-round78 | Re-derive six declared facts of the round-78 self-record at the sealed revision and grade dated value-bound corrections whose new values re-derive at the tip | `tools/round79-selfrecord-round78.py` | 79 |
| gate-arm-composition | Compose a round's own instrument selftests as one pre-report-gate arm, fail-closed on a red, malformed or absent instrument | `tools/pre-report-gate.py` (arm 10 `round78-instruments`) | 79 |
| unregistered-census | Classify a serving listener by whether a registry row declares its port, graded by two fixture registries over the lane-owned pinned child | `tools/round79-unregistered-census.py`, `tools/kama-probe.sh listeners` | 79 |
| selfrecord-round79 | Re-derive six declared facts of the round-79 self-record at its sealed revision and grade one dated value-bound correction per stale fact against the tip | `tools/round80-selfrecord-round79.py` | 80 |
| engine-pin-relations | Relate every pinned serving-engine ref the lane holds to its upstream newest release and tag identity from a committed tag list, with each cell re-derivable offline | `tools/round80-engine-pin-relations.py`, `registry/engine-pin-relations.tsv` | 80 |
| class-engine-register | Prove the `registered` census class on a second engine fixture (Ollama v0.40.11) and audit an engine register whose every row names its receipt | `tools/round80-ollama-census.py`, `registry/unregistered-class-engines.tsv` | 80 |
| late-path-binding | Bind a caller-supplied late-register path to its committed identity — repo-relative path, commit-tracked presence, committed-byte equality — and resolve the file's and each row's introduction at the audited revision, or refuse with exit 2 | `tools/round81-append-debt.py` (`load_late`; arms `late-path-outside-repo`, `late-path-untracked`, `late-path-dirty`, `late-path-bound`) | 83 |
| pending-falls | Show a previous round's declared `pending` count falling at the next round's base: recompute the window from the frozen audit, require every window event accepted, and fail when the declared number disagrees with the window | `tools/round83-pending-falls.py` | 83 |
| pin-recheck | Grade one recheck row per engine relation row by byte comparison of two committed anchor extracts, with a four-value verdict and an explicit `ungraded` class that never counts as graded | `tools/round83-pin-rechecks.py`, `registry/pin-recheck-rows.tsv`, `corpus/anchors/` | 83 |
| rendered-cell-identity | Select a self-assessment cell only from rendered Markdown — HTML comments, backtick/tilde fences, `round-N correction` blocks and non-column-0 lines are not cells — and grade three coupled facts: the head banner names the newest terminal gate receipt with its revision, command and receipt bytes, the calibration row names the newest committed verifier spotcheck by highest round number, and that row names its disposition | `tools/round86-rendered-cells.py` | 86 |
| mutant-owning-arms | Map every declared mutant of the debt selftest to a declared owning arm and reconcile each completed summary with its arm population and its failure-line cardinality, so a dropped arm or a forged summary is a red run | `tools/round86-mutant-owners.py` | 86 |
| pin-origin-corroboration | Corroborate every pin-recheck row against the live source bytes at its declared URL and line range, separating remote origin from the local extract pair's hash integrity | `tools/round86-pin-origin.py` | 86 |
| gate-round86-instruments | Compose the round-86 instrument trio's own selftests as pre-report-gate arm 14 `round86-instruments`, fail-closed on a red, malformed or foreign summary, and prove the arm red on seeded faults by a fault harness | `tools/pre-report-gate.py` (arm 14), `tools/round87-gate-arm-faults.py` (`ARM14_FAULTS faults=3 killed=3 escaped=0`) | 87 |
| router-mode-readiness | Grade a llama.cpp router endpoint by the `status` of the expected model's `/v1/models` entry: an unloaded model on a `--no-models-autoload` router, a failed, incomplete or unknown one is `MODEL_UNLOADED` and a loading or downloading one `MODEL_LOADING`, while sleeping and autoload-unloaded models are `MODEL_OK` cold starts, each branch checked against a real completion on a live pinned b11755 router child; **evidence re-pointed round 89 (round-88 D1/R2)** — the green this row names is the post-repair oracle receipt, because `ROUTER_CELLS cells=17 mismatches=0` at `138a7543` certified the superseded rule that graded sleeping and autoload-unloaded entries `MODEL_UNLOADED` | `tools/kama-probe.sh`, `tools/round88-router-cells.py`, `.ufo/waves/round-88/repair/oracle-cells.py` (`ORACLE_CELLS rev=8b5bb69df0f7cd7302db2964354f5d7a0ba8f4b7 cells=3 mismatches=0`, `.ufo/waves/round-88/repair/oracle-cells-repair.out`), `.ufo/waves/round-89/measured/harm-M.out` (`ORACLE_CELLS rev=4f9eacf720aa59ed806b31b758571e364658179b cells=3 mismatches=0`); the round-88 frozen counter's own residual is `mismatches=2` (C05, C12) at both base and M, never cited as a green | 88 |
| pinned-fixture-restore | Re-create the lane's pinned llama.cpp fixture model from its upstream file, verified by sha256 before an atomic rename, and refuse a present file with another digest | `tools/fetch-pinned-model.py` | 88 |
| router-unloadable-file-verdict | Grade a llama.cpp router entry that is `unloaded` (not failed) on an autoload router as `MODEL_UNLOADED` / `router-model-missing` or `router-model-invalid` when an absolute `--model`/`-m`, `--mmproj`/`-mm` or `--model-draft`/`-md` path in `status.args` is absent or its GGUF header fails a loader check, only when `status.args[0]` names an existing local file; a relative path, an unreadable file, an unknown tensor type or a non-local router keeps the round-88 `router-unloaded-autoload` verdict | `tools/kama-probe.sh`, `tools/round89-unloadable-cells.py` (`ROUTER_UNLOADABLE cells=11 mismatches=0 positive_mismatches=0`, `.ufo/waves/round-89/measured/c1.out`) | 89 |
| router-error-signature-table | Bind the table's eight rows of `SKILL.md` §Router error signatures (llama.cpp router mode) to captured b12177 wire answers — endpoint, HTTP code and exact `error.message` — and fail a duplicate, a fabricated message, source text instead of wire text, a wrong build, a missing receipt and a row outside the section | `tools/round89-signature-rows.py` (`SIGNATURE_ROWS rows=8 bound=8 unbound=0 duplicates=0`, `.ufo/waves/round-89/measured/c2.out`) | 89 |

---

## 3. Planned (round 90)

### Planned (round 90)

1. Operability (carried r88 R5): repair `tests/probe-verdicts/check.py` so it can grade `MODEL_UNLOADED`
   rows — at this round's tip the file names no `MODEL_UNLOADED`, so the verdict class the round-88 rule
   emits is outside its own gate, and the round-89 wave's held-out cells cannot be added to it.
2. Operability (carried r87 R4): investigate the `round75-instruments` arm's `APPEND_DEBT` red and record
   the cause before any round claims an all-green gate.
3. Calibration: extend C1's file classes to the held-out cells the wave reports (near-end truncation, a
   directory or FIFO at the path, unreadable permissions, a missing mmproj, a split shard) only from
   committed receipts that also record the base verdict for the same cell.
4. Freshness: re-run `tools/round89-router-signatures.py` at the next pinned llama.cpp release and re-grade
   all eight rows, so the table cannot silently outlive the build that was asked.
5. Calibration: grade each capability row's evidence pointer against the rule that row describes — round
   88's D1 (a row describing the repaired rule while its first pointer certified the superseded one)
   survived to this round's freeze, so the class is not yet closed by a counter.

---

## 5. Required head, Axes, Retired, Saturation and PROVINCE edits

Each of these is named by a lane counter, not by taste. Before: `mismatches=5` (and `RENDERED_CELLS
mismatches=3`) at lane master `c8db858691e883955f10cf9d7e1dec8f8d732bc8`; after: `mismatches=0 met=True`
and `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1`. Receipts: `counters-draft.out`.

**(a) head authority line** — `banner` fact (needs `Latest measured round: 89`) and `gate` fact (needs the
newest terminal gate receipt, because the counter reads ONE line and takes its FIRST `PRE_REPORT` token):

    **Current authority (round 89):** assigned axes are operability + calibration (`shokunin.conf`);
    Latest measured round: 89. Round-89 claims, counting commands and measured commit: §Round 89 below.
    The round-88 terminal gate receipt is `.ufo/waves/round-88/measured/gate-final.out` (committed at
    `64eaf5969e11e8955636dfb52c13eb089f731d9a`, measured at
    `12eedc6b7a5ca11c53fe520c7d40e4568fb19fa0`): `PRE_REPORT round=88 arms=14 failed=1 uncommitted=0`,
    exit1, the failing arm being the carried `round75-instruments` red; the gate's invocation form is
    `python3 tools/pre-report-gate.py --repo . --round 88` (the receipt records its rev and clean state,
    not argv). The round-86 terminal record that follows is history: ...

**(b) `## Capabilities` intro** — `Mirror of the round-88 canonical capability list that §Round 88
carries` → `Mirror of the round-89 canonical capability list that §Round 89 carries`.

**(c) `## Retired`** — `6 axes and 55 capabilities` → `6 axes and 57 capabilities` (`retired` fact).

**(d) `## Saturation`** — `83, 86, 87, 88 (highest canonical list, §Round88)` → `83, 86, 87, 88, 89
(highest canonical list, §Round89)`, and `Latest repertoire entries are round88 router-mode-readiness and
pinned-fixture-restore, after round87 gate-round86-instruments.` → `Latest repertoire entries are round89
router-unloadable-file-verdict and router-error-signature-table, after round88 router-mode-readiness and
pinned-fixture-restore.`

**(e) `depth` Axes row** — cited `SKILL.md` sha256 `1c6c2973…` (1787 lines) and `grep -c '^## ' SKILL.md`
→ `51`; observed at the tip `e332a3b077c1bddbca1e65f7550b6e7bcc7d998076ffee44cb153fed292c86b8` (1828
lines), run prints `53`. The row's prose also names the round-89 additions.

**(f) `coverage` Axes row** — cited `PROVINCE.md` sha256 `fce8a60e…` (426 lines) and knowledge-file count
`58`; the landed PROVINCE paragraph makes it `806c3db2977cbc149f05fb93e303eca5b305c74614831ee7de01445a3da800e7`
(434 lines) and the count `59`. The row also names the round-89 knowledge entry.

**(g) `calibration` Axes row** — `closure_ptr` fact and the `closure`/`disposition` rendered-cell facts:
re-point the row from the round-87 closure to `corpus/lessons/round-88-verifier-spotcheck.md` and state
`round88 rejected-honest-stop`. The replacement row is in `scorecard-draft.patch`; its two load-bearing
sentences are the `latest outside closure` token and the disposition phrase.

**(h) PROVINCE.md** — the `province` fact requires every `tools/` token in a canon row's evidence cell to
appear in PROVINCE.md, and the two new rows cite `tools/round89-unloadable-cells.py` and
`tools/round89-signature-rows.py`. The drafted paragraph (in `province-round89-note.md`):

Round 89: `tools/kama-probe.sh` decides whether an autoload router entry that only looks
`unloaded` can actually load — an absolute `--model`/`-m`, `--mmproj`/`-mm` or `--model-draft`/`-md` path
missing from the local filesystem is `router-model-missing`, and a GGUF header the loader rejects is
`router-model-invalid` (`tools/round89-unloadable-cells.py`, oracle = the router's own answer to a real
completion). `tools/round89-signature-rows.py` binds the router error-signature rows to captured b12177
wire answers. Header checks only: no non-regular file is opened and no tensor data is read, so a corrupt
payload behind an intact header still grades `MODEL_OK`; the operator's router stays read-only.

---

## 6. Number provenance

Every measured number in this draft, with the committed receipt line it is copied from. Paths are relative
to the lane root; the `.ufo/waves/round-89/` prefix is elided in the first column.

| Number (as written) | Receipt path:line |
|---|---|
| `cells=11`, `mismatches=5`, `positive_mismatches=0`, base `rev=56174a1f…`, probe `99dd1ab8…` | `controls/c1-base.out:13` |
| `mismatches=3`, `positive_mismatches=3`, probe `bd7a6a22…`, `rev=138a7543…` | `controls/c1-f1.out:13` |
| `mismatches=7`, `positive_mismatches=2`, probe `0943fb46…`, `rev=9b4c7af1…` | `controls/c1-f2.out:13` |
| `cells=11`, `mismatches=0`, `positive_mismatches=0`, probe `a4f496bb…`, `rev=4f9eacf7…`, `server_sha256=ba272ee3…` | `measured/c1.out:14` (exit 0, `:15`) |
| counter sha256 `1d86194c…` at M and at freeze | `measured/c1.out:1`; `controls/c1-base.out:1` |
| `rows=0 bound=0 unbound=0 duplicates=0`, base `rev=56174a1f…` | `controls/c2-base.out:2` (exit 1, `:3`) |
| `rows=7 bound=1 unbound=5 duplicates=1`, fixture `rev=0c09884d…` | `controls/c2-forgeries.out:22` (exit 1, `:23`) |
| `rows=8 bound=8 unbound=0 duplicates=0`, `rev=21b9e36d…` | `measured/c2.out:11` (exit 0, `:12`) |
| counter sha256 `30f3af7f…` at M2 and at freeze | `measured/c2.out:1`; `controls/c2-base.out:1` |
| `tests=72 passes=72 failures=0` | `measured/harm-M.out:2` (exit 0, `:3`); base `controls/harm-base-probe-verdicts.out` tail (`tests=72 passes=72 failures=0`) |
| `RESULT pass=30 fail=0` | `measured/harm-M.out:4` (exit 0, `:5`); base `controls/harm-base-test-snapshot.out:31` |
| `ORACLE_CELLS rev=4f9eacf7… cells=3 mismatches=0` | `measured/harm-M.out:10` (exit 0, `:11`); base `controls/harm-base-r88-oracle.out:5` |
| `ROUTER_CELLS cells=17 mismatches=2 canned=14 live=3`, C05/C12 | `measured/harm-M.out:16` (`:13`, `:15`); base `controls/harm-base-r88-cells.out:19` |
| `ORACLE_CELLS rev=8b5bb69d… cells=3 mismatches=0` (landed-rule green) | `.ufo/waves/round-88/repair/oracle-cells-repair.out:5` |
| `HOST_GGUF_SWEEP files=36 ok=36`; `>100k` sweep scope | `measured/host-gguf-sweep.out:38` (`:1`) |
| operator router `MODEL_OK router-unloaded-autoload`, four entries; base `model_ok=1 drift=0 exit=0` | `measured/harm-M.out:19`-`:22`; `controls/harm-base-operator-1234.out:14`-`:16` (`served_model` lists four ids, `:28`) |
| `PRE_REPORT round=88 arms=14 failed=1 uncommitted=0`, `12eedc6b…`, `clean=0` | `.ufo/waves/round-88/measured/gate-final.out:1`, `:16` |
| `8` (table rows) | `measured/c2.out:11` |
| `89`, `88`, `87`, `86`, `85`, `84`, `83` (round labels, first-working round) | section identity and `corpus/lessons/round-88-verifier-spotcheck.md:8`; `plans/round-89-claims.md:6` |
| base `56174a1f…`, M `4f9eacf7…`, M2 `21b9e36d…` | `controls/c1-base.out:13`; `measured/c1.out:14`; `measured/c2.out:11` |
| freeze `4eb75c62…` | **not a receipt value**: derived by `git log --diff-filter=A --format=%H -- plans/round-89-claims.md` → `4eb75c62f6deb1a586a291d611b71775049b34a6`; the same commit adds `tools/round89-unloadable-cells.py` and `tools/round89-signature-rows.py` (same query, both `4eb75c62…`). No file under `controls/` or `measured/` names the freeze commit |
| `1828` lines, `53`, SKILL sha256 `e332a3b0…` | record anchors derived by `counters-draft.out` (`r41 depth` detail lines) |
| `434` lines, `806c3db2…`, `59`, PROVINCE sha256 | record anchors derived by `counters-draft.out` (`r41 coverage` detail lines and the run line) |
| `57`, `89`, `mismatches=0 met=True`, `RENDERED_CELLS … gate=1 closure=1 disposition=1` | `counters-draft.out` (draft tip block) |

---

## 7. Integration order and hazards

1. **Land the head gate sentence only after the round-89 terminal gate receipt exists.** The `gate` fact
   resolves the highest-round receipt matching `^\.ufo/waves/round-[0-9]+/measured/.*\.out$` that carries a
   `PRE_REPORT` line. Today that is round 88; committing `.ufo/waves/round-89/measured/gate-final.out` moves
   it to 89 and turns the drafted sentence red until it is re-pointed at the new receipt's own `rev`, token
   and path. Do not invent those values: copy them from the receipt.
2. **PROVINCE.md must land with SCORECARD.md.** Without the round-89 paragraph the `province` fact names
   `tools/round89-unloadable-cells.py` and `tools/round89-signature-rows.py` as absent.
3. **Cite receipts without `:line` suffixes.** `tools/round68-receipt-pointer-audit.py` and
   `tools/round72-receipt-tip-binding.py` treat a backticked `x.out:14` as a path and report it unresolved;
   put line numbers in prose (`line 14`), as this draft does.
4. **`round72-receipt-tip-binding.py --round 89` is unreadable for a reason outside this draft**: the
   round-89 lesson cites a `.jsonl` receipt (`corpus/lessons/round-89.md:24`) and the instrument's receipt
   extensions are `.out .txt .log .json`. Round 88 had the same class (`.py`). Either wrap the wire rows in
   a `.out`/`.json` receipt or record the instrument's limit.
5. **Not in this draft (L1's):** wave-1 dispositions and any change to the claim verdicts, `LOG.md`,
   `plans/`, the round-89 lesson, and the terminal gate receipt itself. The draft states only what the
   committed `controls/` and `measured/` receipts hold.

