# CriticAxisFit — C1 axis fit (attack before data)

## Verdict

**C1 fits the depth axis.** The round changes a skill surface (a new
`SKILL.md` section, `## Round-26 live error signatures`) with named, verbatim,
source-cited, live-reproduced error signatures. It is not coverage (the
llama-server surface is already governed at base), not freshness (no existing
claim is re-verified), not calibration (no self-assessment counting), not
operability (the rows are reference detail, not a runnable checklist). One
caveat with evidence below: clause (b) only proves absent-from-`SKILL.md`+`corpus`,
so a row can reuse a signature the lane already holds in `.ufo/` advice and
still count as "new". That is a false-provenance seam, not a disqualifier.

## Axis evidence

- AXES.md:11 defines **depth** as "Verifiable technical detail — decision
  tables with real thresholds, named error signatures, cited sources".
  C1's surface is exactly a table of named error signatures, each tied to a
  verbatim string in a pinned llama.cpp source file and to a new SOURCES row.
- The prompt's claim-sizing rule (kama-round-26.md:361-363): "Name the axis by
  the surface the round changes, not by the number it produces … Re-scoring a
  rule the lane already holds on new inputs, or counting rows a sourceless
  fixture also counts, is quality work, never coverage or depth." C1's surface
  is the SKILL.md decision table itself, not a number; the counter's number
  (counted >= 12) is the measurement of depth content, not the axis.
- Not coverage: base `SKILL.md` already governs the llama-server surface
  (line 18 "Local model-serving processes and the ports they own
  (`llama-server` here)", lines 167-182 historical error signatures, lines
  509-577 round-16 live llama.cpp lifecycle). C1 adds no new surface type; it
  adds rows to an existing table.
- Not freshness: no existing claim is re-verified or flagged stale; the rows
  are newly discovered signatures.
- Not calibration: no mismatch between SCORECARD/SHONEN self-assessment and
  observed repo state is counted.
- Round-25 precedent supports fits: `corpus/lessons/round-25-verifier-spotcheck.md`
  rejected the round-25 C1 because it "counts mismatches between instrument
  anchors and the auditor's source, not mismatches between the lane's
  self-assessment" — i.e. the surface was not a skill-content move. C1
  changes skill content, which is the distinguishing feature.

## Do-nothing / shortcut controls

- Do-nothing (base tree): `controls/L1-dead-seat-controls/tip.json` +
  `tip.out` → registered 0 counted 0; cannot meet target 12.
- Junk / fabricated strings: `junk.out`, `generic.out` → all rows fail
  `d_in_source` (strings not verbatim in pinned source); 0/14.
- Help/version text reuse: `controls/A1-rescore/invalid-flag-usage-A1.out`
  → counted 0/14 under A1 (clause f blocks the usage block); the control seat
  `KamaR26CtlAllFalse` met the A0 counter (12/14 via help text) — the counter
  was fixed via A1 before data, and the re-score shows the fix.
- Fabricated source: `fakesource.out` → `d_source_pinned` fails (0/14).
- Fake server binary: `fakeserver.out` → could-not-evaluate (server sha256
  mismatch), so pins hold.
- The only control that was *not* scored is the required "shortcut keyed on
  ids or labels" (`controls/KamaR26CtlShortcut/` is empty; preregistration
  `control_wave.seats.KamaR26CtlShortcut` = "held: provider refusal
  (cyber_policy) on the mutation-tester route"). The L1-run controls cover
  most of its intent (junk, request-echo avoidance via clause e, split/family
  blocking via clause g), but the specific "reuse signatures the lane already
  holds" arm was not executed. This is the gap below.

## The caveat: clause (b) proves less than "new knowledge"

Clause (b) checks absence only over `SKILL.md` and tracked `corpus/`
(`git grep -F -q -e <sig> BASE -- SKILL.md corpus`). It does not check
`.ufo/`, `tests/`, `tools/`, `registry/`. So "absent at base" ≠ "new to the
lane": a row can recycle a signature the lane already holds in advice files.

Counterexample (strongest local one): the 401 authentication-error envelope
`{"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}`.

- Pinned source contains it verbatim: `sources/llama.cpp-704366d/server-http.cpp:294-295`
  (`{"message", "Invalid API Key"}` / `{"type", "authentication_error"}`),
  plus `server-common.cpp:100` maps `authentication_error`.
- Not present in base `SKILL.md`/`corpus/` (clause b): `git grep -F -q -e`
  of the exact envelope over base `SKILL.md`/`corpus` → exit 1 (absent).
  Base `SKILL.md:181` holds the *shorter* historical record `Invalid API Key`
  but not the envelope JSON.
- Already held by the lane: the exact envelope (or its parts) appears at base
  in `.ufo/waves/round-16/build/advice/ConnectKagi.md:36`, 
  `ScoutMiddlewareOrder.md:71,123`, `Falsify/advice/FamilyAuthAndDead.md:65,80`.
- It would count: trigger = http POST `/v1/chat/completions` with no API key
  while the server runs with `--api-key` (allowed arg; not forbidden by
  FORBIDDEN_ARGS), channel body 401 ≥ 400, signature in body, not echoed from
  the request, absent from baseline (baseline runs keyless), ~40 bytes ≥ 20,
  not shared with an earlier counted row. So "new to SKILL.md" passes while
  the underlying knowledge is pre-existing.

## Consequence for the verdict

- This does **not** flip the axis: the surface the round changes is still the
  skill's decision table, and the counter still demands live reproduction on
  the pinned binary plus source pinning — a sourceless or fabricated shortcut
  cannot meet it. Re-adding a held envelope as a named, sourced, live-verified
  row is depth *content* even if the bytes were cited elsewhere.
- It is a judge-visible caveat: `b_new_at_base` is a weaker newness proof than
  the prompt's "Re-scoring a rule the lane already holds … is quality work"
  rule. If the data rows were drawn from round-16 advice files, part of the
  count would be re-scoring held rules, and the "new knowledge" reading of the
  claim would be overstated. The count itself would still be genuine (live
  reproduction, verbatim source).
- The honest check for the judge: for each counted row, `git grep -F -e <sig>`
  over base `.ufo/` and `tests/`; rows that match are recycled knowledge, not
  new. Given the counter is frozen, this stays a measured caveat, not a kill.

## Smallest safe correction (for future rounds, not this frozen one)

Extend clause (b) to grep the whole base tree (or at least `.ufo/waves/`,
`tests/`, `tools/`, `registry/`) for the signature, so "absent at base" means
absent from the lane, not only from `SKILL.md` + `corpus/`. Run the scheduled
shortcut control (reuse of lane-held envelopes) so the gap is covered by a
frozen receipt rather than by this analysis.

## Files written

- `.ufo/waves/round-26/w1-build/advice/CriticAxisFit.md` (this report)
- `.ufo/waves/round-26/w1-build/out/CriticAxisFit/` (empty work dir)
