# CN01CrossClaim - round 64 wave b, cross-claim scan (kama)

Seat: CN01CrossClaim (connector, leaf, no subagents, no dispatch). Judged on operability and calibration.
Milestone: cross-claim scan. Tip read: freeze `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a` via read-only `git show`
(line refs below are into those blobs). No counter run, no live server, no installs, no lane edit, no commit.
Evidence: `.ufo/waves/round-64/b/out/CN01CrossClaim/refs.txt` (every grep behind the line refs).
Scratch `/fast/scratch/hyaku/kama-r64/b/CN01CrossClaim` (extracted blobs only; removed before yield).

Wave-b reports read (existed at start, or landed before I finished): X03Regress2, X08StabilityC1, X09ScansTip,
X10EnvIdleProbe. Not read (no report file yet when scanned, only out/ dirs): X04Regress3, X06Reconciler, MT02,
MT04, MT10, MT11, SB02. Round-63 read: CN02CrossClaim (template), KR03DoNothing, MT15C1FakeConsistent,
MT20C2DupAndObserved, MT21C2SelfdescSkip, RV03C2CounterCode, RV04RegistryLedger (skimmed to the findings).

## 0. Findings in brief

1. **The C1 socket weakness has a C2 twin in the host census.** C1 round 63 certified "the answerer" by the
   socket it was shown (MT15). C2's context-capacity row certifies "idle" or "busy" by a host-global process-name
   census (`pgrep -x llama-server`), fails open on an unknown census, and accepts a busy outcome whose two
   brackets are disjoint pid sets (RV03 F2). A PATH-shadowed `pgrep` gives an idle receipt with exit 0 (X10).
2. **Two wave-b seats contradict each other on the same frozen rule.** X03 uses the frozen busy rule ("printed
   foreign pid set equals pgrep set at the same moment") as a discriminator; X10 shows honest busy runs violate it.
   The rule as frozen cannot be met by an honest run (K1).
3. **The C1 control set flakes and the C2 control set has a dead clause, and they are the same defect.** A control
   is credited by its name while its witness may not exercise the named check (X08: 1 in 18 runs; MT20c: the quote
   length floor is never exercised). One check closes both (section 3).
4. **C1 already has the fix C2 lacks.** C1 brackets holder identity with two snapshots and compares them
   (`c1.py:717-721`, `:898-901`), and fails closed on unreadable own-uid fd tables (`c1.py:382-385`, `:415`).
   C2's busy and idle outcomes use neither (`cc.py:250-258`, `c2r63.py:363-368`).
5. **Scope split on "another llama-server".** C1 counts holders of its own run port (`c1.py:238`, `:371`). C2 counts
   every llama-server on the host by name (`cc.py:220`). The ollama runner orphan that RV04 D3 found is invisible to
   C1 and makes the C2 host busy. The two counters disagree on what the host contains.

## 1. Cross-claim risk table

Status: OPEN = present at the freeze tip; FROZEN-OK = the freeze's own rule already covers it; WATCH = not a defect
today, a trap for the round-64 build.

| id | C1 side: what it certifies by | C2 mirror: what it certifies by | path:line evidence | status |
|---|---|---|---|---|
| R1 | socket / listener: a canned answerer behind the real child's fd passed (MT15; C1 round 63) | host-global name census: idle or busy from `pgrep -x llama-server`; a PATH-shadowed `pgrep` yields exit 0 idle with `cells: 1` (X10) | `cc.py:220` (`pgrep` by name, PATH lookup), `cc.py:222-223` (OSError/timeout returns None), `cc.py:250-251` (`None` means idle), `c2r63.py:352-368` (busy = pgrep non-empty before and after) | OPEN. Freeze's idle control (idle_ok=1) is forgeable by the same shadow |
| R2 | port-scoped holder census: only holders of the run port count (`listeners(port)`, exe re-hashed) | host-scoped census: every llama-server by name, including sibling claims (CN02 P3; RV04 D3 ollama runner orphan) | `c1.py:238`, `c1.py:371`, `c1.py:258-286` vs `cc.py:220`; RV04 D3 (`.ufo/waves/round-63/w1/RV04RegistryLedger.md` section D3) | OPEN, scope decision. One orphan is invisible to C1 and fatal to C2 |
| R3 | two-bracket identity: `raw_a`/`raw_b` taken around the run, `holders_signature` must match (`c1.py:717-721`, `:898-901`, `:482`) | window union: `seen` accumulates every pid seen over the 20 s poll, not a moment (`cc.py:254-256`); 2 of 3 honest busy runs carry pids absent from both pgrep snapshots (X10 run 1: 2022437; run 3: eight pids) | `cc.py:241-258`; X10 table | OPEN. Contradicts the frozen busy predicate (K1) |
| R4 | fail-closed census: unreadable own-uid fd table is a failure (`c1.py:382-385` `unreadable_own`, `:415`) | fail-open census: an unknown census (pgrep OSError or timeout) is recorded as idle (`cc.py:222-223`, `:250-251`) | `c1.py:258-286` docstring "Fails closed"; `cc.py:218-225`; `cc.py:250-251` | OPEN. Same class: unknown is scored as pass |
| R5 | control whose witness may not exercise its named check: `swap_answer` swaps probe 0's text into probe 1 and is credited only if texts differ; draw collides 7/400 (X08: met=False 1/18, `runfield 3/4`) | control whose witness is dead for its clause: quote-length floor `len(quote) < 8` is never exercised by any control (MT20c survived; the quote control only trips the prefix clause) | C1: `c1.py:1349-1355` (swap), `c1.py:666-668` (`live_ref_text` only when texts differ), `c1.py:751-764` (`draw_probes`), `c1.py:1481-1482` (per-run random). C2: `c2r63.py:293-294` (clause), `c2r63.py:417` (quote control) | OPEN both sides. Shared check in section 3 |
| R6 | pinned constants and the 76-count table live inside the counter: `EXPECT_FAMILIES` (`c1.py:58-66`), `LIBS` (`c1.py:81-139`), `MODEL_SHA`/`SERVER_SHA` (`c1.py:48-49`) | self-pin: reconciler `mism = sum(c.values())` (`rec.py:269`, KR03 S1 made it 0 with met=True); selfdesc conjunct has no control (MT21; `c2r63.py:525-528`); planned 13-file pin table would live in the counter | `.py` is outside every scanner: `digest-ledger`/`hexrun-census` read `.md`/`.tsv` only (CN02 P7; X09 scope gap: 27 LIBS digests unscanned). `round63-c2` rows run the tip's commands (`c2r63.py:352-356`) | OPEN for C2 pin table (not built). WATCH for C1 |
| R7 | counter-run tip: round 64 loads nothing from the tip (freeze C1 predicate) | counter-run tip: round-63 runs the tip's bound tools (`c2r63.py:352-356`); tip tools and their pins can be edited together (R6) | `c2r63.py:352-356`; freeze C1 "loading nothing from the tip" | WATCH. Round-64 C2 must not repeat the pattern |
| R8 | work-dir reuse: C1 overwrites `tip/tools` each run, but copies the registry only `if reg:` (`c1.py:1435-1436`); no reuse refusal (`c1.py:1461`) | work-dir reuse: `checkout_tip` returns any existing `work/tip` without a revision check (`c2r63.py:481-482`; RV03 F1; CN02 P9). The freeze gives the `work-reused` refusal to C2 only | `c1.py:1435-1436`, `c1.py:1461`, `c2r63.py:479-482` | OPEN for C1 (low: tool overwritten every run; stale registry only when the tip lacks one). The freeze's C2-only refusal leaves C1 with the same class |
| R9 | `all_ports_closed` printed as `true` on any SetupError because `all([])` is True (`cc.py:813-815`, `:833-835`; X03, X10 agree) | round-63 row pattern `"all_ports_closed": true` (registry row 6) plus verdict gate `rc == 0` (`c2r63.py:217`) and host-busy alt text (`c2r63.py:363`) | `cc.py:813-815`, `cc.py:833-835` | WATCH, not a survivor today: round 63 also needs rc and alt text. A round-64 rule keyed on the token alone would repeat the MT15 class |

## 2. Contradictions between findings

**K1 (X03 vs X10, and RV03 F2 sides with X10).** X03 says the frozen busy rule ("the refusal's printed foreign-server
pid set equals the counter's pgrep set at the same moment") rejects its supplementary mutant
(`other_pids_seen: []` while `pgrep` shows 4 pids). X10 measured the printed set on honest busy runs: run 1 contains
2022437, run 3 eight transient pids, and neither appears in the before or after pgrep snapshot (X10 table, runs 1 and 3).
So the frozen rule rejects honest busy runs, and X03's mutant result shows only that an empty set is rejected, not
that the rule is sound. RV03 F2 gives the satisfiable form: require the two brackets to share a pid
(`set(before) & set(after)`). X10 supports that direction too: every pid present in both snapshots was always in `seen`
(3 of 3 runs). **Action for L1:** amend the frozen busy rule before wave f, or the honest host-busy run cannot score.

**K2 (X08 vs the freeze's kill rule).** X08 reports met=False at an unchanged tip and tool in 1 of 18 runs (runfield
3/4; `live_ref_text` escaped, `live_ref_usage` caught it). X08 attributes the flake to the counter's control
construction, not to load. The freeze's kill rule reads "any control not rejected by its named check" as a kill of
the instrument, and its amendment rule says any counter change is numbered and committed before the next wave. Under
the literal rule the frozen C1 counter is killed by its own random draw. **Action for L1:** decide whether the
redraw fix (section 3) is an AMENDMENT or a re-measure; do not re-score C1 at this tip before deciding.

**K3 (X10 vs the freeze's idle proof).** The freeze says the idle outcome is "proved by a control (idle_ok=1)". X10
proved idle with a fake `pgrep` first on PATH and got exit 0, `cells: 1`, `host_idle.ok: true`. That is the C2
analogue of MT15's canned answerer: a control whose witness is forged at the census, not the host. The idle proof is
only as strong as its census (R1).

**Agreements worth keeping (two seats, same fact).** X03 and X10 both show `"all_ports_closed": true` is printed on
refusal and idle alike (R9). X10 and RV03 F2 both show the window union is not a moment snapshot (R3). X03 and X10
both show the context-capacity refusal path runs before the idle gate, so only exit code plus `cc.json` error can
classify the outcome.

## 3. One proposed shared check

**Bracketed, identity-bound census for the C2 outcome rows, built from C1's existing machinery.**

Mechanics (counter-side, not tool-side; the tool is unchanged):
- The C2 counter enumerates `/proc/<pid>` itself before and after each `context-capacity` run. A process counts as a
  llama-server only if `/proc/<pid>/exe` re-hashes to the pinned digest (the C1 `holder_record` path, `c1.py:340-346`).
  The scope (exe digest vs name) is stated once in the frozen text; exe digest matches C1 and removes R2's sibling-claim
  pollution.
- Zombies are skipped via `/proc/<pid>/stat`. Any unreadable own-uid entry or enumeration error is `census-unknown`,
  which is neither idle nor busy and makes the row not-met (fail closed, `c1.py:382-385`, `:415`).
- Host-busy is credited iff `S = before ∩ after` is non-empty AND the tool exits 2 with the declared refusal text.
  Idle is credited iff `before = after = ∅` AND the tool exits 0 with `cells == 1`, `observed == 1`, `port_closed`.
- The tool's printed `other_pids_seen` is used only as a one-sided check `S ⊆ printed` (3 of 3 X10 runs satisfied it).
  It is never the credit source, so a tool that prints a canned set cannot earn busy.
- Busy uses the intersection above, not equality: the two brackets can legitimately differ by transient pids. Idle needs both brackets empty. C1's stricter `holders_signature` equality (`c1.py:721`) stays on the run's own holder, where it is correct.

What it closes at once:
- **R1 (C2 census forgeable and fail-open):** the PATH-shadowed `pgrep` idle proof (X10) and the `None`-is-idle path
  (`cc.py:222-223`, `:250-251`) both stop being credit sources. This closes the C2 side of the socket mirror.
- **K1 (C2 busy rule unsatisfiable by honest runs):** the printed-set equality is replaced by the satisfiable
  bracket intersection form (RV03 F2; X10 data). X03's mutant is still rejected: it exits 2 with `model-sha256-mismatch`, which is neither declared outcome (exit 0 idle, or exit 2 with the busy text), so it is rejected on either host state.

What it does NOT close (the next checks, not claimed here):
- R5 (control witness must exercise its named clause): needs a clause-flip assertion per control. The freeze's
  C1 fix is a redraw until the two reference texts differ (`c1.py:751-764`), a numbered C1 AMENDMENT.
- R6 (pins live inside the counter): pins read from the freeze commit (`git -C repo show f6a4ea9:<path>`), not the tip.
- R8 (work-dir reuse in C1): a reuse refusal of the same shape as the C2 `work-reused` one.

Cost: not measured (no run in this seat); the change is about 40 lines reusing C1 helpers.
Semantic risk: "busy" changes meaning from any llama-server to any exe-digest-pinned llama-server. The L1 must state
which meaning the frozen C2 predicate uses; the current text says "any other llama-server child" (`cc.py:218-225`).

## 4. Gaps and what I did not verify

- No live run and no counter run (scan only). Every number above is read from the frozen blobs or copied from a
  wave-b or round-63 report, and labeled as such.
- X04Regress3, X06Reconciler, MT02/04/10/11, SB02 had out/ dirs but no report file when scanned; not read.
- K2 is a reading of the freeze's kill rule, not a seat disagreement. The L1 decides.
- R2's claim that the ollama orphan is invisible to C1 rests on C1 counting only the run port (`c1.py:371`); I did not
  start an ollama runner to confirm the port scope in practice.
- R9 is a conditional: it is WATCH because the round-63 gates also need rc and alt text; I did not test a round-64 rule.

## 5. Bounds, tools, counter line

- Tools installed or upgraded: none. No pacman, no `~/.local/bin` writes.
- No lane file edited; no commit, push or mutating git anywhere. Read-only `git show` of the freeze blobs.
- Scratch under `/fast/scratch/hyaku/kama-r64/b/CN01CrossClaim` (extracted blobs), removed before yield.
- Counter line: n/a (scan only; no counter was run by this seat).
