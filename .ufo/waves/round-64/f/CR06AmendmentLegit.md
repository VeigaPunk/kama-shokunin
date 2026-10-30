# CR06AmendmentLegit — round 64 kama, wave f: is the C1 amendment legitimate?

Seat: CR06AmendmentLegit (leaf critic, process review; no subagent dispatch). Scope: `freeze.txt`
AMENDMENT 1/1a/1b and the wave-b reports that motivated them (CR03DoNothing, RV02CounterCode,
MT13ProbeTokens, MT06MapsLib via `b-results.json`, MT05EnvInject, MT11Selftest). Advisory findings
only; no verdict on C1/C2, no commit, no edit to lane source.

Evidence: `.ufo/waves/round-64/f/out/CR06AmendmentLegit/` (`evidence.md` + the two counter snapshots,
the exact diff, and CR03's candidate tools). No tools installed or upgraded (python3 3.14 stdlib, git,
sha256sum only); host pacman untouched. Clone and all runs in
`/fast/scratch/hyaku/kama-r64/f/CR06AmendmentLegit/`, removed before yield.

## 1. Summary judgement

The amendment is **substantively legitimate and honestly disclosed**, with **two defects in the frozen
record itself** that a non-author closure must not pass over. It is not a rule change that hides a
failure; it is an instrument hardening, correctly disclosed, that narrows one kill-rule clause to what
the counter can actually discriminate — and that narrowing is factually accurate.

| question | answer |
|---|---|
| (a) every amendment traceable to a finding, limited to the instrument? | **Yes.** 19 of 19 amended elements located in the tip counter, each matched to its named wave-b finding (evidence E3). The tool is byte-identical across the window (E1); the C1 amendment is confined to `tools/round64-c1-counter.py` (E2). |
| (b) does the kill-rule rewording change what is claimed, or is it honest disclosure? | **Honest disclosure.** The original clause ("a v2-schema or schema-relabelled tool accepted") is undiscoverable by the counter — the tool's own bookkeeping is ungraded, so K1c/K2/K3 are accepted (reproduced, E8). The replacement clause ("a tool whose receipt omits the holder bookkeeping accepted") *is* discriminated (`bind_claim`/`listener_holders_pinned`/`inconsistent:missing-checks` all fail). Both readings are recorded in the freeze and the lesson. |
| (c) what would a non-author closure say about a rule changed after seats scored? | **It rules on the narrowing, and it must do so against the frozen record as written.** Two record defects below make the record harder to rule on than it needs to be. |
| (d) which sentence of the report must say what? | See §5 — one sentence, on the instrument's byte-identity at the tip, and one on what `met=True` does not show. |

## 2. (a) Traceability and instrument-only scope — PASS, with two record defects

**Tool byte-identity (the assignment's hard requirement): PASS.** `git diff f6a4ea9a 23b3fdb1a --
tools/kama-completion-live.py` is empty; both tips hash to `a0c26e14…`. The base tool hashes
differently (`e24bc944…`), so the v3 tool really is the freeze's delta and the amendment window did
not touch it (E1).

**Scope: PASS.** `git diff --name-status f6a4ea9a 23b3fdb1a` outside the wave-b evidence directory
shows the C1 amendment touching only `tools/round64-c1-counter.py` (668+/319−). The C2-side files
(`round64-c2-counter.py`, `round42-selfdesc-reconcile.py`, `shortcut-tally.py`, the registries) are
the C2 build the freeze already discloses under its own heading (E2). The amendment did not
back-door a change to the claim's tool or to the C2 predicate.

**Traceability: PASS.** Each of the 19 elements in AMENDMENT 1's "What changed" list is present in
the tip counter at the location the finding implies, and every one maps to a named wave-b report
(E3 table): RV02 D1/D2/D3/D4/D5/D6/D8–D12, MT03(c), MT04, MT05 F1/F3/F6/F8, MT06, MT10 F2, MT11,
MT13, X08, CR03 K1–K3. There is **no unmotivated hardening** — no check in the tip counter that
traces to no finding. AMENDMENT 1a (`bind_ref_files`, MT06) and AMENDMENT 1b (three instrument
defects the L1's own receipts surfaced) are likewise traced.

### DEFECT 1 (Medium, record) — the freeze's quoted amended sentence says 89; the instrument has 91

freeze.txt AMENDMENT 1 quotes the amended C1 sentence with **"all 89 targeted controls"** and
**"(EXPECT_FAMILIES, sum 89)"** (lines 156, 159). AMENDMENT 1a (line 192) then states: *"the control
total is 91, not 89 (**the amended sentence above reads '91 targeted controls'**, EXPECT_FAMILIES sums
to 91)"*. **The parenthetical is false as written** — the amended sentence above still reads 89. It
has read "89" at every commit from `bf0db9e3` (AMENDMENT 1) through HEAD; it was never updated.

Machine diff of the freeze's quoted sentence against the counter's own docstring predicate
(whitespace-normalised): the **only** substantive difference is 89 vs 91 (E6). The counter's docstring
says 91; `EXPECT_FAMILIES` sums to 91; the freeze's quoted sentence says 89.

This matters because the freeze says "the docstring of the counter repeats it". It does not — the
authoritative normative sentence and the instrument it governs differ in the control count, and the
sentence that claims to have corrected this (AMENDMENT 1a) misdescribes its own file. A reader who
takes the quoted sentence as the claim is reading a claim about 89 controls while the instrument
grades 91.

### DEFECT 2 (Low–Medium, record) — "unreadable pid_gone fails closed" is only partly true

freeze.txt AMENDMENT 1 lists "unreadable pid_gone fails closed" among the fixes (line 138). In the tip
counter, `pid_gone` calls `stat_fields`, which returns `(None, None)` for *any* OSError or parse
failure — including a PermissionError on an unreadable `/proc/<pid>/stat` — and is therefore
indistinguishable from a vanished pid. `pid_gone` then returns `True` ("gone") on `pp is None`. Safe
fault injection: `stat_fields -> (None,None)` makes `pid_gone(999999, 123)` return `True` (E5).
An *unreadable* holder is graded as gone, not as "not observed gone"; the docstring's "unknown start
ticks fail closed" holds only for the `ticks is None` branch.

This does not flip `met` — the port-closed observation backstops the teardown conjunct — and the
disclosed survivor list already carries the general unreadable-holder limit. It is a **disclosed-claim
inaccuracy** rather than a forgery: the amendment text claims a hardening the code does not fully
deliver. RV08 reached the same conclusion by a different route (its D12 disposition, "not fully
fixed"), which is independent corroboration.

## 3. (b) The kill-rule rewording: honest disclosure, not a cover

The original C1 kill rule read: *"…a receipt the counter accepts without its own live contact, **a
v2-schema or schema-relabelled tool accepted**, an evaluator self-test below 3/3."*

The amendment reads that clause as *"a tool whose receipt omits the holder bookkeeping accepted"*.

**The original clause was undiscoverable.** It named a property of the *tool's own bookkeeping* — its
schema string, and whether it computed its holder block from procfs rather than hand-writing one.
The counter loads the tool from the tip and verifies the *process*; it never grades how the tool
derived its receipt. So a candidate could satisfy the original clause and still be accepted, and the
clause could not be a gate the counter enforced.

**The replacement clause is enforced.** A receipt without the holder bookkeeping fails
`bind_claim`, `listener_holders_pinned` and `inconsistent:missing-checks` — visible in the committed
base receipt `controls/c1-base-final-counter.txt`:
`error: live: ["bind_claim", "inconsistent:missing-checks", "listener_holders_pinned", "schema"]`.
The new clause names something the counter actually decides.

**The disclosure is factually accurate.** I reproduced CR03DoNothing's K1c, K2 and K3 against the
**tip** counter: all three print `met=True`, 91/91, 8/8, errors=0 (E8). The freeze's paragraph says
precisely this, names the candidates, states that under the ORIGINAL wording K1c would trigger the
kill rule, and states the honest summary: *"the new instrument rejects forgeries the round-63
instrument accepted; it does not make the tool-side bookkeeping a graded artifact."* The lesson
(`corpus/lessons/round-64.md` §Mistakes 2 and 5) carries the same. **This is the shape of a legitimate
disclosure**: the failure is named, the counter's limits are named, and the claim is restated to what
the counter can decide.

**One thing the disclosure does not say, which the report must.** The counter has **no tool-byte pin
of its own** (`TOOL_SHA`/`tool_sha`/`tool_digest` → no matches, E10). The "byte-pinned" wording in the
C1 sentence is a property of the *lane tip* — established by the freeze's tool-identity check and by
E1 — not something the counter grades. That is consistent with the accepted K1c/K2/K3, but it means
the report's "what `met=True` does not show" list must say that met=True says nothing about *which
tool file* answered, only about *which process* answered. The SCORECARD's current (f) item covers the
provenance half ("tool-side holder bookkeeping is graded as provenance (K1c/K2/K3)") but not the
tool-identity half.

## 4. (c) What a non-author closure would say about a rule changed after seats scored

The closure would find the disclosure **complete on the rule change** and **incomplete on the
record**, in this shape:

1. **The rule change is real and disclosed.** Wave-b seats scored the freeze-commit instrument
   `f6a4ea9a`; AMENDMENT 1 rewrote both the instrument and one kill-rule clause afterwards. The
   freeze says so in its own words ("this is a rule change made after seats scored and is disclosed
   as such — the closure rules on it"), keeps the original C1 sentence verbatim as the pre-amendment
   record, and records the surviving candidates by name. A closure can rule on that.
2. **The narrowing is the kind a non-author closure accepts**: it moves the gate from an
   undiscoverable property to a discoverable one, and it does not weaken the *live* claim (the
   process-binding checks are strictly stronger than at the freeze: 19 new/rewritten elements, 91
   controls vs 76, 8 evaluator plants vs 3, and the round-63 forgeries now rejected).
3. **The closure's reservation would be the two record defects (§2)**: a normative sentence that
   misstates the control count and misdescribes its own correction, and a disclosed fix the code only
   partly delivers. Both are correctable *in the record* without touching the instrument, and neither
   changes a verdict. But a closure that reads "89 controls" and then finds 91/91 in the receipt, or
   that reads "unreadable pid_gone fails closed" and finds a fail-open branch, is being asked to rule
   on a record that misstates itself — that is the closure's problem to name, and the L1's to fix.
4. **The closure should also note the disclosure-order detail**: at the tip this wave scores
   (`23b3fdb1a`), the counter carries the AMENDMENT 1b fixes but the frozen record at that commit does
   not yet describe them — they land four minutes later at `7252c7c9`, together with the wave-f spec
   (E7). This is *before* any wave-f seat dispatched and before the measured-tip scoring, so the
   freeze's own ordering condition ("after wave b settled and BEFORE wave f is dispatched and before
   any measured-tip scoring") holds. It is completeness, not a rule change after scoring — but a
   closure scoring the tip commit must read the record at `7252c7c9` or later, not at `23b3fdb1a`.

## 5. (d) The sentences the report must carry

**Sentence A — the amended claim (replace the current SCORECARD C1 verdict cell's C1 sentence and
add to the "What `met=True` does not show" list):**

> The amended C1 instrument verifies a *process* property: that the process answering the run-port
> listener is the pinned llama-server, bound from procfs and the counter's own code alone, and that
> the receipt's own request and answer belong to this run. It does not verify *which tool file*
> produced that receipt — the counter holds no digest of `tools/kama-completion-live.py` — so
> `met=True` at this tip rests on the lane's byte-identity of that file against the freeze
> (`a0c26e14…`, unchanged across AMENDMENT 1/1a/1b), not on anything the counter graded.

**Sentence B — the rule change (into the same C1 verdict cell, next to the existing
"the freeze text was amended after seats scored (disclosed)" clause):**

> The kill-rule clause was narrowed after wave-b seats scored, and both readings are recorded: under
> the original clause a schema-relabelled tool accepted was a kill, and CR03DoNothing's K1c/K2/K3 are
> accepted by the amended counter with `met=True` because the held child really is the pinned server;
> the amended clause instead kills a tool whose receipt omits the holder bookkeeping, which the
> counter does decide. The honest statement of C1 is that the new instrument rejects forgeries the
> round-63 instrument accepted, and does not make the tool-side bookkeeping a graded artifact.

Both are already latent in the freeze and the lesson; the report must carry them in the report's own
voice, and Sentence A additionally carries the tool-identity limit the current (f) item omits.

**Two record corrections for the L1 (freeze text only, instrument untouched):** change the amended
sentence's "89" to "91" in both places (freeze lines 156, 159) so the quoted sentence equals the
counter's docstring and AMENDMENT 1a's parenthetical becomes true; and either soften AMENDMENT 1's
"unreadable pid_gone fails closed" to what the code does (an unreadable *stat* is graded as gone) or
make the code fail closed on an unreadable stat. Both are text-level; neither changes a verdict, and
neither requires touching the C1 instrument's graded semantics.

## 6. Verification gaps

- One unmodified tip-counter run (77 s, exit 0, 91/91, 8/8, errors=0), matching the committed receipt
  exactly; no flake, so no rerun. The three candidate runs (K1c/K2/K3) are one run each, not a
  stability sample.
- The `pid_gone` finding is a **safe fault injection** (function-level, `stat_fields` stubbed; no
  process, port or signal touched), not a live unreadable-holder exploit.
- The 89-vs-91 diff is a whitespace-normalised text diff of the freeze sentence against the docstring;
  I did not attempt to determine whether the L1 intended 89 or 91 when writing the sentence — only
  that the two disagree and that AMENDMENT 1a misdescribes its own file.
- I did not re-derive the C2 side (the idle-rule clause replacement in AMENDMENT 1b, traceable to
  `b/X10EnvIdleProbe.md`, whose "polling-window union" reasoning I read and did not re-measure). C2 is
  outside this seat's item; noted because it is the same rule-change-after-scoring family.
- No mutation of the counter was performed (this is a process review, not a mutant protocol); the
  K1c/K2/K3 runs are unmodified-counter scores of CR03's candidates.

## 7. One-line counter output this item asks for

```
tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[] eval_selftest=8/8 errors=0 met=True families[bind=30/30 canned=1/1 detach=1/1 digest=1/1 forge=3/3 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 pathcopy=1/1 predead=1/1 preload=1/1 proxy=1/1 ptok=2/2 receiptbind=4/4 relabel=1/1 replay=1/1 reqbind=2/2 runfield=4/4 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 stalehold=2/2 tamper=8/8 timing=4/4 trunc=2/2 witness=5/5]
```

Report: `.ufo/waves/round-64/f/CR06AmendmentLegit.md`
