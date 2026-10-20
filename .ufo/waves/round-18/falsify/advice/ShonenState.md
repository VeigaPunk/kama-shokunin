VERDICT: confirm — all four SHONEN boxes are `[~]` with zero `[x]`; SHONEN.md is byte-identical to the round-18 start; the round-18 v3 live fixture is lane-owned loopback and every round-18 artifact scopes it away from consumer health; no artifact implies promotion, and the only named non-author closure on disk explicitly declined to verify any box.

Seat: KamaR18.ShonenState (scout). Lane `kama-shokunin`, reviewed at pushed `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. Read-only except this report. No runtime/gate experiment was named, so none was run; no clone was created; no scratch directory was created. No installs (no pacman/uv/npm/official-binary channel used). No server or listener started by this seat.

## 1. Marks as delivered

Source `/home/vgpnk/Projects/shokunin/kama-shokunin/SHONEN.md#1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5`, unchanged between round-18 start and HEAD:

| Box | Line(s) | Mark | Independent non-author verifier named? |
|---|---|---|---|
| B1 SKILL decision tables/errors/checklists/sources | 5–6 | `[~]` | No — box text itself: "no named non-author verifier" |
| B2 end-to-end domain task logged | 7–8 | `[~]` | No — "still a lane-owned control, no non-author mark" |
| B3 instructions executable without oral context | 9–10 | `[~]` | No — "independent execution review remains open" |
| B4 no cross-domain bleed / PROVINCE accurate | 11–12 | `[~]` | No — author assertion only |

Executed facts:

- `git diff --stat e75cf680b53484a61709ee1b2787d8dbc6419f74..HEAD -- SHONEN.md` → empty (exit 0).
- `git status --porcelain -- SHONEN.md` → empty; `git rev-parse HEAD:SHONEN.md` → `2eb81f23fc33d4f4d592c297bb8ad3900f43714c`; `sha256sum SHONEN.md` → `1ff9e2f3…6d3fb5` (file-content digest).
- `grep -c '\[x\]' SHONEN.md` → 0; `grep -c '\[~\]' SHONEN.md` → 4; box starts at lines 5, 7, 9, 11 (`grep -n '^\s*- \['`).

No box can be promoted on this evidence: promotion (`SHONEN.md:3`) requires all four, and each box's own pointer records that no non-author verification exists.

## 2. Per-box evidence state (author assertion, not verification)

- **B1** — pointer sections exist: `SKILL.md:125` "Decision table", `SKILL.md:167` "Historical error signatures", `SKILL.md:191` "Checklist". Round 18 appended a new section after `SKILL.md:599` (v3 rows, S054/KQ23/KQ24 text) without removing those headings. The claim "cited sources" is author-asserted; `SHONEN.md:6` still says no named non-author verifier.
- **B2** — historical claims reproduce from committed receipts: round-16 `kama-llamacpp-live/v1` = 10 checks, 10 passed, `probe_model_ok` `MODEL_OK/matched` exit 0, `probe_mismatch` `MODEL_MISMATCH/served-id-mismatch` exit 2, `teardown_exited` returncode 0/no SIGKILL, `teardown_port_closed` port_refuses; round-17 v2 receipts 1–3 = 11/11 passed each, health body exactly `{"status":"ok"}`, loading 503 counts 42/45/45 all exact with 0 dropped bodies, `teardown_graceful` alive-at-start + SIGTERM + no SIGKILL + returncode 0. `tests/llamacpp-live/controls.py` claim reproduces: `runs/controls-current.json` has k0–k8 (8 bad shapes), `accepted_bad` 0; `runs/controls-frozen.json` `accepted_bad` 6 (k1,k2,k4,k5,k6,k8). Pointer remains an author assertion (`SHONEN.md:8`).
- **B3** — pointers exist: `SKILL.md:191` §Checklist, `corpus/knowledge/snapshot-history.md:7` §Run it. "Independent execution review remains open" (`SHONEN.md:10`) is still true: the round-18 official pass was author/L1-run (`LOG.md:1084`), and `LOG.md:1082` states round-18 author/seat checks "do not themselves satisfy the independent non-author spot-check duty."
- **B4** — `PROVINCE.md` write boundary is unchanged; only an appended round-18 note at `PROVINCE.md:81–90`. `corpus/knowledge/cross-lane-scope.md` last changed in `3285cdf` (round 11) and is untouched this round. Round-18 commits touch no file outside this lane's repo surfaces (`git diff --name-status` over the round lists only `.ufo/waves/round-18/**`, lane docs and the six declared production files); no write to `~/.config`, `~/.omp` or systemd is claimed or evidenced. The lesson's disclosed wildcard `--host 0.0.0.0` experiment (`corpus/lessons/round-18.md` "Execution conformance disclosures") was a transient build-seat launch, killed, with no HTTP and no persistent state; it does not write into another province, so it does not falsify B4 — but B4 must not be read as certifying that every seat experiment stayed loopback-legal.

## 3. The `[x]` gate — no named independent non-author exists

- The only outside closure on disk is `corpus/lessons/round-17-verifier-spotcheck.md` (author line `:1` "hyaku closure (non-author integrator, @m_opus)"; commit `e75cf68`, committer `protocol-shokunin`). It grades round 17 only, and at `:269–276` it says: all four boxes remain `[~]` and "are not yet checkable by a non-author"; Box 2 is "a lane-owned live control, not consumer reconciliation"; Box 3 "still has no independent execution review"; Boxes 1 and 4 are author assertions; **"No promotion is implied."**
- `LOG.md:1082` repeats that round-18 author/seat checks do not satisfy the independent non-author spot-check duty.
- No round-18 outside check exists yet: `corpus/lessons/*verifier*` ends at round-17; the parent `.ufo/reports/round-18/` contains `kaidoku.md`, `kasegi.md`, `kengaku.md`, `kotodama.md`, `mado.md`, `tabi.md`, `tameshi.md`, `tsukuroi.md` but **no `kama.md`**. The round-18 build reviewers/critics and this falsify wave are explicitly not an outside non-author judgment (`corpus/lessons/round-18.md` R7; this seat's contract).
- Consequence: writing `[x]` for any box in round 18 would be a fabricated promotion. The correct marks are the four delivered `[~]` lines.

## 4. Live fixture is not consumer reconciliation

- Round-18 receipts: `argv` host `127.0.0.1`, ports `33769`, `44109`, `45359` (`.ufo/waves/round-18/live/receipt-{1,2,3}.json`), schema `kama-llamacpp-live/v3`, `outcome` `pass`, 11/11 checks each; `internal_fault` null; `child_env_keys` = `["HOME","LANG","PATH"]` only; teardown `returncode 0`, `sigkill_sent false`, `port_listener_ownership: "child"`.
- Registered ports are only `8080` and `34113` (`registry/endpoint-consumers.tsv:35–37`); no receipt port is registered; `git diff --name-only e75cf68..HEAD -- registry/` is empty, so no consumer row was touched.
- Model is the lane-owned fixture: `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf`, sha256 `270cba1b…256d`, size `1,185,376` bytes (B2's "1.2 MB" decimal), launched from pinned b11755.
- Semantics are scoped everywhere: `PROVINCE.md:84–85` "a green receipt still proves no registered-consumer health"; `SKILL.md:605` "This does not certify consumer health."; `corpus/SOURCES.md:58` (S046) and `:67` (S055) both say "not registered-consumer health".
- Gate: `runs/live-gate-{1,2,3}.stdout` each line 1 `VALID`; `commands.json` `live-gate-1` argv carries exactly four `--expect-*-sha256` pins (model `270cba…`, server `b6a31a…`, probe `36b649…`, tool `dc036d…`), exit 0.

So even though round 18 adds three green v3 runs, they cannot advance B2 to `[x]`: they are lane-owned own-work on a fake-consumer fixture, not reconciliation of any registered consumer, and no non-author graded the box.

## 5. Pointer-detail gaps (no mark change requested)

1. **"four pins" for round 17 is not reproducible from retained round-17 evidence.** `.ufo/waves/round-17/live/gate.txt:1–7` shows three `VALID` lines and only `probe=36b64978… tool=0efd1723…`; the gate prints only `VALID <path>` (`frozen/tests_llamacpp-live_check-receipt.py:1398`), so the pins line was assembled outside it and model/server pin values were not retained. The four-pin claim is author-recorded at `corpus/lessons/round-17.md:172`, `SCORECARD.md:681` and `SOURCES.md:58`; the round-17 non-author itself cites only "probe and tool pins" (`round-17-verifier-spotcheck.md:131`). Round 18's equivalent claim *is* reproducible via `runs/commands.json`. Smallest correction: keep B2 `[~]`; if L1 wants the pointer exact, append the round-18 v3 four-pin receipt pointer (and/or recompute the round-17 gate with four pins in a clone) rather than rewriting line 8's history.
2. **B2 stops at round 17; round-18 v3 receipts are not cited.** Build advice already ruled `SHONEN.md:8` a historical past-run statement not to be rewritten (`build/advice/ScoutStaleStatements.md:133`, `build/advice/ScoutReceiptConsumers.md:69`). No mark change; an append is optional and would not license a promotion.
3. **No round-18 file states "SHONEN unchanged."** The fleet report's §SHONEN must carry the four `[~]` lines and the no-promotion sentence, or the report is silent about the gate; silence must not be read as admission.

## 6. Adjacent observation (not a SHONEN mark)

`SCORECARD.md:767` (EOF; `wc -l` = 767) still ends §Round 18 with "Measured results, measured commit and exact commands are appended after execution," but no measured block follows in SCORECARD. The measured addendum exists in `LOG.md:1084–1095` and in `corpus/lessons/round-18.md` "Official measurement pass." Route to the SCORECARD/report owner; this does not alter any SHONEN mark and implies no promotion.

## 7. Limits

- Read-only review: no production, fleet, sibling-repo, frozen-evidence or old-lesson edits; the only file written is this report. No jj commands; no git writes.
- No runtime/gate experiment was assigned, so none was run and no separate clone was needed. All claims above come from committed files, `git`/`stat`/JSON reads, and `pgrep`/`ss` observation.
- Ownership hygiene: `pgrep -af kama-r18-falsify-ShonenState` → "no seat processes"; `ss -ltnp` shows no listener on `33769`, `44109` or `45359`; this seat started no server, so there is no process group to tear down.
- `[INFERENCE]` only: that the round-17 gate invocation supplied the model and server pins (not retained). Everything else is observed in committed bytes. SHONEN box *content* beyond pointer existence remains author-asserted and is not independently executed by this seat.
- Concurrent worktree note (not this seat's write): at `2026-10-20 20:20:11 -0300`, `corpus/SOURCES.md` in the live worktree differed from HEAD (`git diff --numstat` 10+/2−; S049/S050 recomposed, new S056 row present) and `.ufo/waves/round-18/falsify/make_spec.py` was already modified at review start. All facts in this report were read from committed HEAD/committed evidence files; this seat edited neither.
